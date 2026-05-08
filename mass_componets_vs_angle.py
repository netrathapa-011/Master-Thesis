import matplotlib.pyplot as plt
import numpy as np

# -----------------------------------------
# Impact angles
# -----------------------------------------
angles = [15, 30, 45, 60]

# -----------------------------------------
# Scenario 1 — masses (kg)
# -----------------------------------------
S1_largest = [
    6.3620329794518407e25,
    7.2682068343138884e25,
    7.5038802173229742e25,
    8.2483502289171494e25
]

S1_second = [
    7.0521104872447623e19,
    1.3601550084869865e21,
    3.0657354699244136e20,
    2.4966607283282004e22
]

S1_rest = [
    7.2234138542672592e22,
    1.2889937104023939e22,
    8.9990485721490209e22,
    4.8363771386844842e23
]

# -----------------------------------------
# Scenario 2 — masses (kg)
# -----------------------------------------
S2_largest = [
    1.1940814000306101e26,
    1.2005493160593551e26,
    1.2115717408933964e26,
    1.4741969682398589e26
]

S2_second = [
    3.1557957557770669e20,
    2.7420909169738420e21,
    6.8466971272715084e19,
    1.2738221490919078e20
]

S2_rest = [
    7.7176560441141961e22,
    3.1157803858595490e22,
    1.6154854964320425e22,
    1.5095562634842917e23
]

# -----------------------------------------
# Convert to Earth masses
# -----------------------------------------
ME = 5.972e24

def to_Earth(m):
    return np.array(m) / ME

S1_largest_em = to_Earth(S1_largest)
S1_second_em  = to_Earth(S1_second)
S1_rest_em    = to_Earth(S1_rest)

S2_largest_em = to_Earth(S2_largest)
S2_second_em  = to_Earth(S2_second)
S2_rest_em    = to_Earth(S2_rest)

# -----------------------------------------
# Plot
# -----------------------------------------
plt.figure(figsize=(12,7))

# Scenario 1
plt.plot(angles, S1_largest_em, "o-", color="blue", label="S1 Largest Aggregate")
plt.plot(angles, S1_second_em, "o--", color="cyan", label="S1 Second Aggregate")
plt.plot(angles, S1_rest_em, "o:", color="skyblue", label="S1 Rest Mass")

# Scenario 2
plt.plot(angles, S2_largest_em, "s-", color="green", label="S2 Largest Aggregate")
plt.plot(angles, S2_second_em, "s--", color="lime", label="S2 Second Aggregate")
plt.plot(angles, S2_rest_em, "s:", color="lightgreen", label="S2 Rest Mass")

plt.xlabel("Grazing Angle (degrees)", fontsize=14)
plt.ylabel("Mass (Earth Masses)", fontsize=14)
plt.title("Final Mass Components vs. Grazing angle", fontsize=16)

# 🔥 FIX: Show all lines clearly
plt.yscale("log")

plt.grid(True, linestyle="--", alpha=0.5)
plt.legend(fontsize=11)

plt.tight_layout()
plt.savefig("mass_components_vs_angle.png", dpi=300)

