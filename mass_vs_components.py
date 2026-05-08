import matplotlib.pyplot as plt
import numpy as np

# -------------------------
# DATA YOU PROVIDED
# -------------------------

angles = [15, 30, 45, 60]

# Scenario 1 data (masses in kg)
S1_largest = [
    6.3620329794518407e+25,
    7.2682068343138884e+25,
    7.5038802173229742e+25,
    8.2483502289171494e+25
]

S1_second = [
    7.0521104872447623e+19,
    1.3601550084869865e+21,
    3.0657354699244136e+20,
    2.4966607283282004e+22
]

S1_rest = [
    7.2234138542672592e+22,
    1.2889937104023939e+22,
    8.9990485721490209e+22,
    4.8363771386844842e+23
]


# Scenario 2 data (masses in kg)
S2_largest = [
    1.1940814000306101e+26,
    1.2005493160593551e+26,
    1.2115717408933964e+26,
    1.4741969682398589e+26
]

S2_second = [
    3.1557957557770669e+20,
    2.7420909169738420e+21,
    6.8466971272715084e+19,
    1.2738221490919078e+20
]

S2_rest = [
    7.7176560441141961e+22,
    3.1157803858595490e+22,
    1.6154854964320425e+22,
    1.5095562634842917e+23
]


# -------------------------
# PLOTTING
# -------------------------

x = np.arange(len(angles))
width = 0.12

fig, ax = plt.subplots(figsize=(14,7))

# Scenario 1 bars
ax.bar(x - 3*width, S1_largest, width, label="S1 Largest")
ax.bar(x - 1*width, S1_second, width, label="S1 2nd Largest")
ax.bar(x + 1*width, S1_rest, width, label="S1 Rest")

# Scenario 2 bars
ax.bar(x + 3*width, S2_largest, width, label="S2 Largest")
ax.bar(x + 5*width, S2_second, width, label="S2 2nd Largest")
ax.bar(x + 7*width, S2_rest, width, label="S2 Rest")

ax.set_xlabel("Grazing Angle (degrees)", fontsize=14)
ax.set_ylabel("Mass (kg)", fontsize=14)
ax.set_title("Mass Comparison Across 8 Scenarios (S1 & S2)", fontsize=16)
ax.set_xticks(x)
ax.set_xticklabels(angles)
ax.set_yscale("log")   # log scale required due to huge variation
ax.legend(fontsize=10)
ax.grid(True, which="both", ls="--", alpha=0.5)

plt.tight_layout()
plt.show()


