#!/usr/bin/env python3
"""
Moon candidate analysis from SPH fragment outputs.

INCLUDES:
- Bound orbit condition
- Roche-limit filtering (rigid + fluid)
- Hill-radius stability
- Disk vs true-moon separation
- Individual moon lifetime tracking
- Output catalog of moon candidates

This version is FIXED for filenames like:
  impact.0580_fragments.out
  impact.0580_fragments_aggregates.txt
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import glob
import os
import re

# ==========================================================
# CONSTANTS
# ==========================================================
G = 6.67430e-11          # m^3 kg^-1 s^-2
MIN_MASS = 1e19          # kg
TIMESTEP_DURATION = 100  # seconds

# ----------------------------------------------------------
# Planet / star properties
# ----------------------------------------------------------
PLANET_RADIUS = 1.21e7   # m
PLANET_MASS = 1.19e26    # kg
PLANET_A = 1.0e11        # m (planet orbit around star)
STAR_MASS = 1.99e30      # kg

# ----------------------------------------------------------
# Roche limits (meters)
# ----------------------------------------------------------
D_ROCHE_FLUID = 4.61e7
D_ROCHE_RIGID = 2.38e7

# ----------------------------------------------------------
# Distance / stability limits
# ----------------------------------------------------------
MAX_DISTANCE = 6.0e8
HILL_FRACTION_MAX = 0.5

# ----------------------------------------------------------
# Data directory
# ----------------------------------------------------------
data_dir = "/pfs/10/project/bw16g002/Netra/S2_45"

# ==========================================================
# HELPER FUNCTIONS
# ==========================================================

def hill_radius(a_planet, M_planet, M_star):
    return a_planet * (M_planet / (3.0 * M_star))**(1.0/3.0)


def extract_largest_aggregate(agg_file):
    with open(agg_file) as f:
        lines = f.readlines()

    M, P, V = None, None, None

    for header in ("# largest aggregate:", "# 1st-largest aggregate:"):
        try:
            i = next(j for j,l in enumerate(lines) if header in l)
            for l in lines[i+1:]:
                l = l.strip()
                if l and not l.startswith("#"):
                    M = float(l.split()[0])
                    break
            if M is not None:
                break
        except StopIteration:
            continue

    try:
        i = next(j for j,l in enumerate(lines) if "# pos and vel" in l)
        for l in lines[i+1:]:
            l = l.strip()
            if l and not l.startswith("#"):
                vals = list(map(float, l.split()))
                P = np.array(vals[:3])
                V = np.array(vals[3:6])
                break
    except StopIteration:
        pass

    if M is None or P is None or V is None:
        raise ValueError("Missing aggregate data")

    return M, P, V


def orbital_elements(Mp, m, r_vec, v_vec):
    r = np.linalg.norm(r_vec)
    v = np.linalg.norm(v_vec)
    mu = G * (Mp + m)

    E = 0.5*v*v - mu/r
    if E >= 0:
        return E, np.inf, np.nan, np.nan, np.nan

    a = -mu / (2*E)
    h = np.linalg.norm(np.cross(r_vec, v_vec))
    e2 = 1 + 2*E*h*h/mu**2
    e = np.sqrt(e2) if e2 > 0 else np.nan

    r_peri = a * (1 - e)
    r_apo  = a * (1 + e)

    return E, a, e, r_peri, r_apo

# ==========================================================
# MAIN ANALYSIS
# ==========================================================

frag_files = sorted(glob.glob(f"{data_dir}/impact.*_fragments.out"))
print(f"Found {len(frag_files)} fragment files")

if not frag_files:
    raise RuntimeError("No fragment files found — check data_dir")

R_HILL = hill_radius(PLANET_A, PLANET_MASS, STAR_MASS)
HILL_LIMIT = HILL_FRACTION_MAX * R_HILL

moon_counts = []
hours_list = []
moon_lifetimes = {}
catalog_rows = []

print("Running full moon analysis with Roche + Hill stability...")

for frag_file in frag_files:
    filename = os.path.basename(frag_file)
    match = re.search(r"impact\.(\d+)_fragments\.out", filename)
    if not match:
        print(f"Skipping unmatched file {filename}")
        continue

    timestep = int(match.group(1))
    hours = timestep * TIMESTEP_DURATION / 3600.0

    agg_file = os.path.join(
        data_dir,
        f"impact.{timestep:04d}_fragments_aggregates.txt"
    )

    if not os.path.exists(agg_file):
        print(f"Missing aggregate file for timestep {timestep}")
        continue

    try:
        M_p, P_p, V_p = extract_largest_aggregate(agg_file)
    except Exception as e:
        print(f"Error reading aggregate at {timestep}: {e}")
        continue

    cols = ["x","y","z","vx","vy","vz","mass","rel_mass","mat0","mat1"]
    frags = pd.read_csv(
        frag_file,
        sep=r"\s+",
        comment="#",
        names=cols,
        on_bad_lines="skip"
    )

    if frags.empty:
        moon_counts.append(0)
        hours_list.append(hours)
        continue

    moon_count = 0

    for idx, row in frags.iterrows():
        if row.mass < MIN_MASS:
            continue

        r_vec = np.array([row.x, row.y, row.z]) - P_p
        v_vec = np.array([row.vx, row.vy, row.vz]) - V_p
        r_now = np.linalg.norm(r_vec)

        if r_now < D_ROCHE_RIGID or r_now > MAX_DISTANCE:
            continue

        E, a, e, r_peri, r_apo = orbital_elements(M_p, row.mass, r_vec, v_vec)

        if E >= 0 or np.isnan(e):
            continue

        # Roche constraints
        if r_peri < D_ROCHE_RIGID:
            continue
        if D_ROCHE_RIGID <= r_peri < D_ROCHE_FLUID and e > 0.1:
            continue
        if e > 0.99:
            continue

        # Hill stability
        if r_apo > HILL_LIMIT:
            continue

        # Disk vs moon classification
        is_disk = (e < 0.05 and a < 3 * D_ROCHE_FLUID)
        if is_disk:
            continue

        moon_count += 1

        # Lifetime tracking
        if idx not in moon_lifetimes:
            moon_lifetimes[idx] = [timestep, timestep]
        else:
            moon_lifetimes[idx][1] = timestep

        # Catalog
        catalog_rows.append({
            "timestep": timestep,
            "time_hours": hours,
            "fragment_id": idx,
            "mass_kg": row.mass,
            "a_m": a,
            "e": e,
            "r_peri_m": r_peri,
            "r_apo_m": r_apo
        })

    moon_counts.append(moon_count)
    hours_list.append(hours)
    print(f"Timestep {timestep:04d} | {hours:6.2f} h | moons: {moon_count}")

# ==========================================================
# OUTPUT
# ==========================================================

if catalog_rows:
    pd.DataFrame(catalog_rows).to_csv("moon_candidate_catalog.csv", index=False)
    print("Saved moon_candidate_catalog.csv")

if moon_lifetimes:
    lifetime_rows = []
    for fid, (t0, t1) in moon_lifetimes.items():
        lifetime_rows.append({
            "fragment_id": fid,
            "start_timestep": t0,
            "end_timestep": t1,
            "lifetime_hours": (t1 - t0) * TIMESTEP_DURATION / 3600.0
        })
    pd.DataFrame(lifetime_rows).to_csv("moon_lifetimes.csv", index=False)
    print("Saved moon_lifetimes.csv")

if hours_list:
    h, m = zip(*sorted(zip(hours_list, moon_counts)))
    plt.figure(figsize=(12,6))
    plt.plot(h, m, '-o', lw=1)
    plt.xlabel("Time (hours)")
    plt.ylabel("Number of stable moons")
    plt.title("Stable Moon Candidates vs Time")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig("moon_candidates_vs_time_full_physics.png", dpi=300)
    print("Saved moon_candidates_vs_time_full_physics.png")
