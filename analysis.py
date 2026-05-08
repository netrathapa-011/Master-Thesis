#!/usr/bin/env python3
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, Circle
from matplotlib.lines import Line2D

# ========== CONFIGURATION ==========
BASE_DIR = "/pfs/10/project/bw16g002/Netra/S1_45"
CATALOG_FILE = os.path.join(BASE_DIR, "moon_candidate_catalog.csv")
OUTPUT_FILE = os.path.join(BASE_DIR, "S1_45_comprehensive_analysis.pdf")

# Physical parameters
PRIMARY_RADIUS = 1.09e7 
PRIMARY_MASS = 7.17e25 
ROCHE_LIMIT_FLUID = 3.89e7  
ROCHE_LIMIT_RIGID = 2.01e7  

FLUID_ROCHE_RP = ROCHE_LIMIT_FLUID / PRIMARY_RADIUS
RIGID_ROCHE_RP = ROCHE_LIMIT_RIGID / PRIMARY_RADIUS

# Colors for Thesis
COLORS = {
    'primary': '#2d3436',      # Dark Charcoal
    'stable': '#00b894',       # Green
    'marginal': '#fdcb6e',     # Yellow/Orange
    'unstable': '#d63031',     # Red
    'roche_fluid': '#e17055',  
    'roche_rigid': '#0984e3',  
}

# ========== LOAD AND PREPARE DATA ==========
if not os.path.exists(CATALOG_FILE):
    raise FileNotFoundError(f"{CATALOG_FILE} not found.")

catalog = pd.read_csv(CATALOG_FILE)
catalog.columns = catalog.columns.str.strip().str.lower()

# Get last timestep
last_timestep = catalog["timestep"].max()
last_data = catalog[catalog["timestep"] == last_timestep].copy()

# Calculate parameters in Rp
last_data["sma_rp"] = last_data["a_m"] / PRIMARY_RADIUS
last_data["peri_rp"] = last_data["r_peri_m"] / PRIMARY_RADIUS

# Stability Classification
def classify_stability(row):
    if row['r_peri_m'] < ROCHE_LIMIT_RIGID: return 'unstable'
    if row['r_peri_m'] < ROCHE_LIMIT_FLUID: return 'marginal'
    return 'stable'

last_data['stability'] = last_data.apply(classify_stability, axis=1)

# ========== PLOTTING ==========
fig = plt.figure(figsize=(16, 10))
gs = plt.GridSpec(2, 2, height_ratios=[1.5, 1])

# --------------------------------------------------
# 1. ORBITAL ARCHITECTURE (Top Left)
# --------------------------------------------------
ax1 = fig.add_subplot(gs[0, 0])
top_moons = last_data.sort_values('mass_kg', ascending=False).head(20)

for _, moon in top_moons.iterrows():
    a = moon['sma_rp']
    e = moon['e']
    b = a * np.sqrt(max(0, 1 - e**2))
    color = COLORS[moon['stability']]
    
    orbit = Ellipse((-a*e, 0), 2*a, 2*b, color=color, fill=False, alpha=0.5, lw=1)
    ax1.add_patch(orbit)
    ax1.scatter(moon['peri_rp'], 0, color=color, s=10)

ax1.add_patch(Circle((0,0), 1.0, color=COLORS['primary']))
ax1.add_patch(Circle((0,0), FLUID_ROCHE_RP, color=COLORS['roche_fluid'], fill=False, ls='--'))
ax1.add_patch(Circle((0,0), RIGID_ROCHE_RP, color=COLORS['roche_rigid'], fill=False, ls=':'))

ax1.set_aspect('equal')
limit = FLUID_ROCHE_RP * 2.5
ax1.set_xlim(-limit, limit); ax1.set_ylim(-limit, limit)
ax1.set_title("Orbital Architecture (Massive Fragments)")
ax1.set_xlabel("x ($R_p$)"); ax1.set_ylabel("y ($R_p$)")

# --------------------------------------------------
# LEGEND / INDEX
# --------------------------------------------------
legend_elements = [
    Line2D([0], [0], color=COLORS['stable'], lw=2, label='Stable'),
    Line2D([0], [0], color=COLORS['marginal'], lw=2, label='Marginal'),
    Line2D([0], [0], color=COLORS['unstable'], lw=2, label='Unstable'),
    Line2D([0], [0], color=COLORS['roche_fluid'], lw=2, ls='--', label='Fluid Roche Limit'),
    Line2D([0], [0], color=COLORS['roche_rigid'], lw=2, ls=':', label='Rigid Roche Limit'),
]
ax1.legend(handles=legend_elements, loc='upper right', fontsize=9, frameon=True)

# --------------------------------------------------
# 2. PARAMETER SPACE (Top Right)
# --------------------------------------------------
ax2 = fig.add_subplot(gs[0, 1])
scatter = ax2.scatter(last_data['sma_rp'], last_data['e'], c=last_data['mass_kg'], 
                      cmap='viridis', alpha=0.6, s=15, edgecolors='none')
ax2.axvline(FLUID_ROCHE_RP, color=COLORS['roche_fluid'], ls='--')
ax2.set_title("Orbital Parameter Distribution")
ax2.set_xlabel("Semi-major Axis ($R_p$)"); ax2.set_ylabel("Eccentricity ($e$)")
plt.colorbar(scatter, ax=ax2, label='Mass (kg)')

# --------------------------------------------------
# 3. STABILITY BAR CHART (Bottom Left)
# --------------------------------------------------
ax3 = fig.add_subplot(gs[1, 0])
counts = last_data['stability'].value_counts()
counts.plot(kind='bar', color=[COLORS.get(x) for x in counts.index], ax=ax3)
ax3.set_title("Stability Classification Count")
ax3.set_ylabel("Number of Fragments")

# --------------------------------------------------
# 4. MASS DISTRIBUTION (Bottom Right)
# Robust for 1 or multiple objects
# --------------------------------------------------
ax4 = fig.add_subplot(gs[1, 1])
mass_data = last_data[last_data['mass_kg'] > 0]['mass_kg']

if len(mass_data) == 1:
    m = mass_data.iloc[0]
    ax4.scatter(m, 1, s=150, color='purple')
    ax4.set_xscale('log')
    ax4.set_yticks([])
    ax4.set_ylim(0.5, 1.5)
    ax4.set_title("Mass of Final Surviving Object")
    ax4.set_xlabel("Mass (kg)")
    ax4.annotate(f"{m:.2e} kg", xy=(m, 1), xytext=(0, 15), textcoords='offset points', ha='center')
elif len(mass_data) > 1:
    bins = np.logspace(np.log10(mass_data.min()), np.log10(mass_data.max()), 20)
    ax4.hist(mass_data, bins=bins, color='skyblue', edgecolor='black')
    ax4.set_xscale('log')
    ax4.set_ylabel("Count")
    ax4.set_title("Mass Frequency (Log Scale)")
    ax4.set_xlabel("Mass (kg)")
else:
    ax4.text(0.5, 0.5, "No valid mass data", ha='center', va='center', transform=ax4.transAxes)

# --------------------------------------------------
# SAVE FIGURE
# --------------------------------------------------
plt.tight_layout()
plt.savefig(OUTPUT_FILE)
plt.close(fig)
print(f"Final Dashboard saved to {OUTPUT_FILE}")
