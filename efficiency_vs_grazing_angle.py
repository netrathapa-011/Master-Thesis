import numpy as np
import matplotlib.pyplot as plt
import os
import pandas as pd

# -----------------------------
# 1. Configuration & Physical Parameters
# -----------------------------
base_dir = "/pfs/10/project/bw16g002/Netra"

# Snapshot list for the equilibrium (late) stage
late_snapshots = {
    "S1_15": "impact.1074", "S1_30": "impact.1277",
    "S1_45": "impact.1500", "S1_60": "impact.1500",
    "S2_15": "impact.1096", "S2_30": "impact.1084",
    "S2_45": "impact.1083", "S2_60": "impact.1102"
}

# Scenario-specific physical parameters from your Roche_limit.py output
physics_map = {
    "S1": {"R_planet": 1.09e7, "R_roche": 3.89e7}, 
    "S2": {"R_planet": 1.21e7, "R_roche": 4.61e7}
}

# -----------------------------
# 2. Analysis Functions
# -----------------------------

def get_moon_forming_data(snap_dict):
    data_list = []
    
    for sim, snap_file in snap_dict.items():
        path = os.path.join(base_dir, sim, snap_file)
        if not os.path.exists(path):
            print(f"File not found: {path}")
            continue
            
        # Load SPH Data (Columns: ID, x, y, z, vx, vy, vz, mass)
        # Note: adjust columns index if your file format differs
        data = np.loadtxt(path)
        x, y, z, m = data[:, 1], data[:, 2], data[:, 3], data[:, 7]
        
        # Determine Group and Angle
        group = "S1" if "S1" in sim else "S2"
        angle = int(sim.split('_')[1])
        
        # Get Physics
        Rp = physics_map[group]["R_planet"]
        Rr = physics_map[group]["R_roche"]
        
        # System Centering (COM)
        cx, cy, cz = np.average(x, weights=m), np.average(y, weights=m), np.average(z, weights=m)
        r = np.sqrt((x-cx)**2 + (y-cy)**2 + (z-cz)**2)
        
        # Integrate Masses
        m_disk = np.sum(m[r > Rp])
        m_moon = np.sum(m[r > Rr])
        
        # Calculate Efficiency percentage
        efficiency = (m_moon / m_disk) * 100 if m_disk > 0 else 0
        
        data_list.append({
            "Scenario": group,
            "Angle": angle,
            "Total_Disk_Mass": m_disk,
            "Moon_Mass": m_moon,
            "Efficiency": efficiency
        })
        
    return pd.DataFrame(data_list)

# -----------------------------
# 3. Main Execution and Plotting
# -----------------------------

if __name__ == "__main__":
    # Calculate Data
    df = get_moon_forming_data(late_snapshots)
    
    # Save results for your thesis tables
    df.to_csv(os.path.join(base_dir, "moon_efficiency_results.csv"), index=False)
    print("CSV data saved successfully.")

    # Generate the Efficiency Trend Plot
    plt.figure(figsize=(10, 6))
    plt.rcParams['font.family'] = 'serif'
    
    # Plot S1 Trend
    s1_data = df[df['Scenario'] == "S1"].sort_values('Angle')
    plt.plot(s1_data['Angle'], s1_data['Efficiency'], 'o-', color='#000080', 
             linewidth=2, markersize=8, label="Scenario S1 (Cooler/Low Velocity)")
    
    # Plot S2 Trend
    s2_data = df[df['Scenario'] == "S2"].sort_values('Angle')
    plt.plot(s2_data['Angle'], s2_data['Efficiency'], 's-', color='#8B0000', 
             linewidth=2, markersize=8, label="Scenario S2 (Warmer/High Velocity)")

    # Add labels and formatting
    plt.xlabel("Grazing Angle (Degrees)", fontsize=12)
    plt.ylabel("Moon-Forming Efficiency (%)", fontsize=12)
    plt.title("Satellite Formation Efficiency vs. Grazing Angle (Last stage)", fontsize=14, fontweight='bold')
    plt.xticks([15, 30, 45, 60])
    plt.ylim(0, 100)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend(frameon=True)
    
    # Save the figure
    plt.tight_layout()
    plt.savefig(os.path.join(base_dir, "efficiency_trend_plot.png"), dpi=300)
    print("Efficiency trend plot saved.")
