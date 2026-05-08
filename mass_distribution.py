#!/usr/bin/env python3

# =========================
# NON-INTERACTIVE BACKEND
# =========================
import matplotlib
matplotlib.use("Agg")   # REQUIRED on clusters / batch systems

import numpy as np
import matplotlib.pyplot as plt

# -------------------------
# ANGLES
# -------------------------
angles = [15, 30, 45, 60]
x = np.arange(len(angles))
width = 0.2

# -------------------------
# SCENARIO 1 (S1) MASSES
# -------------------------
S1_largest = [
    6.3706881220212793e25,
    7.2680728159738455e25,
    7.5038802173229742e25,
    8.2483502289171494e25
]

S1_second = [
    4.1267555524408459e19,
    1.3407638224530639e21,
    3.0657354699244136e20,
    2.4966607283282004e22
]

S1_rest = [
    4.8085424367328723e22,
    1.3544298068488986e22,
    8.9990485721490209e22,
    4.8363771386844842e23
]

# -------------------------
# SCENARIO 2 (S2) MASSES
# -------------------------
S2_largest = [
    1.1950151481053229e26,
    1.2005518996997773e26,
    1.2115907682637581e26,
    1.4741969682398589e26
]

S2_second = [
    4.5730173651948372e19,
    2.7804586293184928e21,
    6.8466971272715084e19,
    1.2738221490919078e20
]

S2_rest = [
    1.1236669923697191e22,
    2.8295981808960439e22,
    1.4757385402766649e22,
    1.5095562634842917e23
]

# -------------------------
# PLOTTING
# -------------------------
fig, axes = plt.subplots(1, 2, figsize=(16, 7), sharey=True)

# ---- Scenario 1 ----
axes[0].bar(x - width, S1_largest, width, label="Largest")
axes[0].bar(x,         S1_second,  width, label="2nd Largest")
axes[0].bar(x + width, S1_rest,    width, label="Rest")

axes[0].set_title("Scenario 1 (S1)", fontsize=14)
axes[0].set_xlabel("Grazing Angle (degrees)")
axes[0].set_ylabel("Mass (kg)")
axes[0].set_xticks(x)
axes[0].set_xticklabels(angles)
axes[0].set_yscale("log")
axes[0].legend()
axes[0].grid(True, which="both", ls="--", alpha=0.5)

# ---- Scenario 2 ----
axes[1].bar(x - width, S2_largest, width, label="Largest")
axes[1].bar(x,         S2_second,  width, label="2nd Largest")
axes[1].bar(x + width, S2_rest,    width, label="Rest")

axes[1].set_title("Scenario 2 (S2)", fontsize=14)
axes[1].set_xlabel("Grazing Angle (degrees)")
axes[1].set_xticks(x)
axes[1].set_xticklabels(angles)
axes[1].set_yscale("log")
axes[1].legend()
axes[1].grid(True, which="both", ls="--", alpha=0.5)

plt.suptitle("Mass Distribution(Final Stable Masses ) vs Grazing Angle", fontsize=16)
plt.tight_layout()

# -------------------------
# SAVE (INSTEAD OF SHOW)
# -------------------------
plt.savefig("mass_distribution_S1_S2.png", dpi=300)
plt.close()
