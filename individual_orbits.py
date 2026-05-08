#!/usr/bin/env python3
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, Circle

# ========== CONFIGURATION ==========
BASE_DIR = "/pfs/10/project/bw16g002/Netra/S2_60"
CATALOG_FILE = os.path.join(BASE_DIR, "moon_candidate_catalog.csv")
OUTPUT_DIR = os.path.join(BASE_DIR, "orbit_plots")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Planetary parameters
PRIMARY_RADIUS = 1.21e7  # meters
ROCHE_LIMIT_FLUID = 4.61e7  # meters
ROCHE_LIMIT_RIGID = 2.38e7  # meters

FLUID_ROCHE_RP = ROCHE_LIMIT_FLUID / PRIMARY_RADIUS
RIGID_ROCHE_RP = ROCHE_LIMIT_RIGID / PRIMARY_RADIUS

# Visual Settings
DPI = 300
COLORS = {
    'primary': '#2d3436',      # Planet
    'orbit': '#0984e3',        # Blue
    'roche_fluid': '#d63031',  # Red
    'roche_rigid': '#fdcb6e',  # Yellow/Orange
    'peri': '#00b894',         # Green
    'apo': '#6c5ce7',          # Purple
}

# ========== LOAD DATA ==========
print("Loading and cleaning data...")
catalog = pd.read_csv(CATALOG_FILE)
catalog.columns = catalog.columns.str.strip().str.lower()

last_timestep = catalog["timestep"].max()
last_data = catalog[catalog["timestep"] == last_timestep].copy()

# Convert meters to Primary Radii (Rp)
last_data["sma_rp"] = last_data["a_m"] / PRIMARY_RADIUS
last_data["peri_rp"] = last_data["r_peri_m"] / PRIMARY_RADIUS
last_data["apo_rp"] = last_data["r_apo_m"] / PRIMARY_RADIUS

# Sort by mass so we don't generate 22,000 plots (takes too long)
# We will take the top 50 most significant fragments
top_data = last_data.sort_values("mass_kg", ascending=False).head(50)

print(f"Generating plots for the 50 most massive fragments at T={last_timestep}...")

# ========== CREATE INDIVIDUAL PLOTS ==========
for idx, fragment in top_data.iterrows():
    fragment_id = int(fragment['fragment_id'])
    
    fig, ax = plt.subplots(figsize=(8, 8))
    
    sma = fragment['sma_rp']
    ecc = fragment['e']
    peri = fragment['peri_rp']
    apo = fragment['apo_rp']
    
    # Physics: Calculate semi-minor axis (b)
    semi_minor = sma * np.sqrt(1 - ecc**2)
    
    # Physics: Planet is at the Focus (0,0). 
    # The center of the ellipse is shifted by -c (where c = a * e)
    center_x = -sma * ecc
    
    # Stability determination
    if fragment['r_peri_m'] < ROCHE_LIMIT_RIGID:
        stability = "UNSTABLE (Inside Rigid Roche)"
        title_color = '#d63031'
    elif fragment['r_peri_m'] < ROCHE_LIMIT_FLUID:
        stability = "MARGINAL (Inside Fluid Roche)"
        title_color = '#e17055'
    else:
        stability = "STABLE (Captured)"
        title_color = '#00b894'

    # Plot the orbit ellipse
    ellipse = Ellipse(
        (center_x, 0), 
        width=2 * sma,
        height=2 * semi_minor,
        angle=0,
        edgecolor=COLORS['orbit'],
        facecolor='none',
        alpha=0.2,
        linewidth=2,
        label='Orbit Path'
    )
    ax.add_patch(ellipse)
    
    # Plot the planet at the focus
    ax.add_patch(Circle((0, 0), 1.0, color=COLORS['primary'], zorder=10, label='Planet (1 $R_p$)'))
    
    # Plot Roche limits
    ax.add_patch(Circle((0, 0), FLUID_ROCHE_RP, fill=False, ls='--', color=COLORS['roche_fluid'], label='Fluid Roche'))
    ax.add_patch(Circle((0, 0), RIGID_ROCHE_RP, fill=False, ls=':', color=COLORS['roche_rigid'], label='Rigid Roche'))

    # Mark Periapsis (closest) and Apoapsis (farthest)
    ax.scatter(peri, 0, color=COLORS['peri'], s=60, edgecolors='black', zorder=15, label='Periapsis')
    ax.scatter(-apo, 0, color=COLORS['apo'], s=60, edgecolors='black', zorder=15, label='Apoapsis')

    # Formatting
    ax.set_aspect('equal')
    limit = max(apo, FLUID_ROCHE_RP) * 1.2
    ax.set_xlim(-limit, limit)
    ax.set_ylim(-limit, limit)
    
    ax.set_title(f"Fragment {fragment_id}: {stability}", color=title_color, fontweight='bold', pad=20)
    ax.set_xlabel(r"Distance ($R_p$)")
    ax.set_ylabel(r"Distance ($R_p$)")
    
    # Info Box
    textstr = '\n'.join((
        f'Mass: {fragment["mass_kg"]:.2e} kg',
        f'SMA: {sma:.2f} $R_p$',
        f'Eccentricity: {ecc:.3f}',
        f'Periapsis: {peri:.2f} $R_p$'
    ))
    ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    ax.legend(loc='lower right', fontsize='small')
    plt.tight_layout()
    
    plt.savefig(os.path.join(OUTPUT_DIR, f"frag_{fragment_id}_orbit.png"), dpi=DPI)
    plt.close()

print(f"Done! Check the folder: {OUTPUT_DIR}")
