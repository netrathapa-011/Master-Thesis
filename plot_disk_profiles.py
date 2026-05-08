import numpy as np
import matplotlib.pyplot as plt
import os

# -----------------------------
# Base directory (where scenario folders are)
# -----------------------------
base_dir = "/pfs/10/project/bw16g002/Netra"

# -----------------------------
# Simulation snapshot info (use actual filenames)
# -----------------------------
sim_snapshots = {
    "S1_15": {"Early": "impact.0000", "Late": "impact.0554"},
    "S1_30": {"Early": "impact.0000", "Late": "impact.1277"},
    "S1_45": {"Early": "impact.0000", "Late": "impact.1277"},
    "S1_60": {"Early": "impact.0000", "Late": "impact.1500"},
    "S2_15": {"Early": "impact.0000", "Late": "impact.0576"},
    "S2_30": {"Early": "impact.0000", "Late": "impact.0584"},
    "S2_45": {"Early": "impact.0000", "Late": "impact.0583"},
    "S2_60": {"Early": "impact.0000", "Late": "impact.1500"}
}

# -----------------------------
# Functions to load and process snapshots
# -----------------------------
def load_sph_snapshot(filename):
    """Load SPH snapshot (ASCII)"""
    x, y, z, m = [], [], [], []
    with open(filename, 'r') as f:
        for line in f:
            if line.startswith("#") or len(line.strip()) < 10:
                continue
            cols = line.split()
            x.append(float(cols[1]))
            y.append(float(cols[2]))
            z.append(float(cols[3]))
            m.append(float(cols[7]))  # mass column
    return np.array(x), np.array(y), np.array(z), np.array(m)

def compute_center(x, y, z, m):
    """Compute mass-weighted center of mass"""
    return np.array([np.average(x, weights=m),
                     np.average(y, weights=m),
                     np.average(z, weights=m)])

def radial_mass_distribution(x, y, z, m, center, nbins=80):
    """Compute radial mass distribution / surface density"""
    r = np.sqrt((x-center[0])**2 + (y-center[1])**2 + (z-center[2])**2)
    bins = np.linspace(0, np.max(r), nbins+1)
    mass_per_bin = np.histogram(r, bins=bins, weights=m)[0]
    r_mid = 0.5*(bins[1:] + bins[:-1])
    area = 2*np.pi*r_mid*(bins[1:] - bins[:-1])
    sigma = mass_per_bin / (area + 1e-30)
    return r_mid, sigma

# -----------------------------
# Color settings for scenarios
# -----------------------------
colors = {"S1": "blue", "S2": "green"}

# -----------------------------
# 1️⃣ Plot Early snapshots
# -----------------------------
plt.figure(figsize=(14,8))
for sim, stages in sim_snapshots.items():
    snapshot_file = os.path.join(base_dir, sim, stages["Early"])
    if not os.path.exists(snapshot_file):
        print("Missing file:", snapshot_file)
        continue
    x, y, z, m = load_sph_snapshot(snapshot_file)
    center = compute_center(x, y, z, m)
    r, sigma = radial_mass_distribution(x, y, z, m, center)
    scenario = sim.split("_")[0]  # S1 or S2
    plt.loglog(r, sigma, label=f"{sim} ({scenario})", color=colors[scenario])

plt.xlabel("Radius (m)", fontsize=14)
plt.ylabel("Surface density Σ(r) [kg/m²]", fontsize=14)
plt.title("Disk Surface Density – Early Snapshots", fontsize=16)
plt.grid(True, which="both", ls="--", alpha=0.5)
plt.legend(fontsize=10)
plt.tight_layout()
plt.savefig(os.path.join(base_dir, "early_snapshots.png"), dpi=300)
plt.close()

# -----------------------------
# 2️⃣ Plot Late snapshots
# -----------------------------
plt.figure(figsize=(14,8))
for sim, stages in sim_snapshots.items():
    snapshot_file = os.path.join(base_dir, sim, stages["Late"])
    if not os.path.exists(snapshot_file):
        print("Missing file:", snapshot_file)
        continue
    x, y, z, m = load_sph_snapshot(snapshot_file)
    center = compute_center(x, y, z, m)
    r, sigma = radial_mass_distribution(x, y, z, m, center)
    scenario = sim.split("_")[0]  # S1 or S2
    plt.loglog(r, sigma, label=f"{sim} ({scenario})", color=colors[scenario])

plt.xlabel("Radius (m)", fontsize=14)
plt.ylabel("Surface density Σ(r) [kg/m²]", fontsize=14)
plt.title("Disk Surface Density – Late Snapshots", fontsize=16)
plt.grid(True, which="both", ls="--", alpha=0.5)
plt.legend(fontsize=10)
plt.tight_layout()
plt.savefig(os.path.join(base_dir, "late_snapshots.png"), dpi=300)
plt.close()

print("Plots saved: early_snapshots.png and late_snapshots.png in", base_dir)
