import numpy as np

# -----------------------------
# Step 1: Read planet structure
# -----------------------------
planet_file = "target.structure"

# Load columns: r (m), m (kg), rho (kg/m^3)
data = np.loadtxt(planet_file, usecols=(0,1,2))
radii = data[:,0]      # m
masses = data[:,1]     # kg
densities = data[:,2]  # kg/m^3

# Planet radius = max radius
R_p = radii[-1]
# Planet mass = max cumulative mass
M_p = masses[-1]

# Average density of planet
rho_p = M_p / ((4/3) * np.pi * R_p**3)

print(f"Planet radius: {R_p:.2e} m")
print(f"Planet mass: {M_p:.2e} kg")
print(f"Planet average density: {rho_p:.2f} kg/m^3")

# -----------------------------
# Step 2: Read projectile properties from spheres.in
# -----------------------------
spheres_file = "spheres.in"

# Manually extracted from your spheres.in
M_proj = 2.986e25  # kg

# Composition fractions
mantle_frac_proj = 0.7
shell_frac_proj = 0.0
core_frac_proj = 1.0 - mantle_frac_proj - shell_frac_proj  # assume remaining is core

# Material densities (kg/m^3)
rho_core = 7800   # Iron
rho_mantle = 2700 # Granite
rho_shell = 2700  # Granite (if any)

# Compute weighted average density
rho_proj = core_frac_proj*rho_core + mantle_frac_proj*rho_mantle + shell_frac_proj*rho_shell

# Estimate projectile radius from mass and density
R_proj = ((3*M_proj)/(4*np.pi*rho_proj))**(1/3)

print(f"\nProjectile mass: {M_proj:.2e} kg")
print(f"Projectile radius: {R_proj:.2e} m")
print(f"Projectile density: {rho_proj:.2f} kg/m^3")

# -----------------------------
# Step 3: Compute Roche limits
# -----------------------------
# Fluid satellite
d_roche_fluid = 2.44 * R_p * (rho_p / rho_proj)**(1/3)
# Rigid satellite
d_roche_rigid = 1.26 * R_p * (rho_p / rho_proj)**(1/3)

print(f"\nRoche limit (fluid satellite): {d_roche_fluid:.2e} m")
print(f"Roche limit (rigid satellite): {d_roche_rigid:.2e} m")

# -----------------------------
# Step 4: Compare with satellite distance
# -----------------------------
# Example distance from planet center (replace with actual from your simulation)
r_sat = 2.5e6  # meters

if r_sat < d_roche_fluid:
    print("Satellite is inside the Roche limit (fluid) → may be disrupted")
else:
    print("Satellite is outside the Roche limit (fluid) → likely stable")
