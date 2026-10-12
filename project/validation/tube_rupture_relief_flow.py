"""
GPREH Appendix D.1.2 -- Tube Rupture, Part 1: flow rate through the break.

Vertical thermosyphon reboiler, propane tube side, tube-side pressure
300 psig, shell-side (steam) max allowable relieving pressure 165 psig
(10% accumulation over 150 psig MAWP). Tubes are 1 in. 16 BWG (0.87 in ID),
12 ft long. Worst case: bottom-tubesheet failure, break 6 in from the tube
end. This splits the tube into two parallel leak paths, both discharging
into the shell at the break:

  Short leg (0.5 ft): saturated/subcooled LIQUID propane, fed from the
    bottom channel. Bottom tubesheet sits 9 ft below the column liquid
    surface (liquid level is 3 ft below the top tubesheet; tube is 12 ft
    long), so the driving pressure is 300 psig plus that 9 ft of liquid
    head. Flow travels upward 0.5 ft to reach the break.

  Long leg (11.5 ft): TWO-PHASE propane (15% vapor, typical circulating
    quality for a thermosyphon reboiler), fed from the top channel at the
    column pressure of 300 psig flat. Flow travels downward 11.5 ft to
    reach the break (gravity assists).

Total relief load = sum of the choked/backpressure-limited HEM mass flow
through each leg. No TPHEM available on this workstation, so both legs are
solved with a from-scratch HEM march (see hem_pipe_flow.py) driven by
`thermo` PR-EOS property lookups instead of the book's TPHEM program.
"""

import sys
import os
import matplotlib.pyplot as plt
from thermo import ChemicalConstantsPackage, CEOSGas, CEOSLiquid, PRMIX, FlashPureVLS

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from hem_pipe_flow import solve_choked_hem, G_GRAV

# --- Unit conversions ---
PSI_TO_PA = 6894.76
FT_TO_M = 0.3048
IN_TO_M = 0.0254
KG_TO_LB = 2.20462
S_TO_HR = 3600.0

# --- Geometry ---
D_TUBE = 0.87 * IN_TO_M            # tube ID
L_TUBE = 12.0 * FT_TO_M            # full tube length
BREAK_FROM_END = 0.5 * FT_TO_M     # break is 6 in from the tube end
L_SHORT = BREAK_FROM_END
L_LONG = L_TUBE - BREAK_FROM_END
ROUGHNESS = 0.0018 * IN_TO_M       # commercial steel tube, default assumption
K_ENTRANCE = 0.5                   # sharp-edged entrance, default assumption

# --- Process conditions ---
P_COLUMN = 300 * PSI_TO_PA + 101325.0    # column / process pressure (absolute)
P_SHELL_BACK = 165 * PSI_TO_PA + 101325.0  # max allowable shell relieving pressure
LIQUID_LEVEL_BELOW_TOP_TS = 3.0 * FT_TO_M
BOTTOM_TS_SUBMERGENCE = L_TUBE - LIQUID_LEVEL_BELOW_TOP_TS  # 9 ft, matches problem statement
LONG_LEG_INLET_VF = 0.15  # 15% vapor quality, typical thermosyphon circulation

# --- Build the propane PR-EOS flasher ---
constants, correlations = ChemicalConstantsPackage.from_IDs(["propane"])
MW = constants.MWs[0]
eos_kwargs = dict(Tcs=constants.Tcs, Pcs=constants.Pcs, omegas=constants.omegas)
gas = CEOSGas(PRMIX, HeatCapacityGases=correlations.HeatCapacityGases, eos_kwargs=eos_kwargs)
liq = CEOSLiquid(PRMIX, HeatCapacityGases=correlations.HeatCapacityGases, eos_kwargs=eos_kwargs)
flasher = FlashPureVLS(constants, correlations, gas=gas, liquids=[liq], solids=[])

# --- Short leg: liquid, +9 ft head, upward 0.5 ft to the break ---
sat_liq_column = flasher.flash(P=P_COLUMN, VF=0.0, zs=[1.0])
rho_liq_column = sat_liq_column.rho_mass()
head_pa = rho_liq_column * G_GRAV * BOTTOM_TS_SUBMERGENCE
P0_SHORT = P_COLUMN + head_pa

print("=== Inputs ===")
print(f"Column pressure:         {P_COLUMN/PSI_TO_PA:8.1f} psia")
print(f"Shell backpressure:      {P_SHELL_BACK/PSI_TO_PA:8.1f} psia")
print(f"Saturated liquid density at column P: {rho_liq_column:.1f} kg/m3")
print(f"Bottom-tubesheet submergence: {BOTTOM_TS_SUBMERGENCE/FT_TO_M:.1f} ft -> head = {head_pa/PSI_TO_PA:.2f} psi")
print(f"Short-leg inlet pressure (liquid): {P0_SHORT/PSI_TO_PA:.1f} psia")
print(f"Short leg length: {L_SHORT/FT_TO_M:.2f} ft, Long leg length: {L_LONG/FT_TO_M:.2f} ft")
print(f"Tube ID: {D_TUBE*1000:.2f} mm ({D_TUBE/IN_TO_M:.3f} in)")

# --- Solve short leg (liquid, VF0=0, upward flow -> sin_theta=+1) ---
print("\n=== Solving short leg (liquid, 0.5 ft, upward) ===")
short = solve_choked_hem(
    flasher, MW, P0=P0_SHORT, L=L_SHORT, D=D_TUBE, roughness=ROUGHNESS,
    sin_theta=+1.0, P_back=P_SHELL_BACK, K_entrance=K_ENTRANCE,
    VF0=0.0,
)
short_mdot_lbhr = short["mass_flow_rate"] * KG_TO_LB * S_TO_HR
print(f"G = {short['G']:.1f} kg/(m2 s), mdot = {short['mass_flow_rate']:.4f} kg/s "
      f"= {short_mdot_lbhr:,.0f} lb/hr")
print(f"choked: {short['choked']}, exit P: {short['P_stop']/PSI_TO_PA:.1f} psia, "
      f"exit quality: {short['x_stop']:.3f}")

# --- Solve long leg (two-phase, VF0=0.15, downward flow -> sin_theta=-1) ---
print("\n=== Solving long leg (two-phase, 15% vapor, 11.5 ft, downward) ===")
long_ = solve_choked_hem(
    flasher, MW, P0=P_COLUMN, L=L_LONG, D=D_TUBE, roughness=ROUGHNESS,
    sin_theta=-1.0, P_back=P_SHELL_BACK, K_entrance=K_ENTRANCE,
    VF0=LONG_LEG_INLET_VF,
)
long_mdot_lbhr = long_["mass_flow_rate"] * KG_TO_LB * S_TO_HR
print(f"G = {long_['G']:.1f} kg/(m2 s), mdot = {long_['mass_flow_rate']:.4f} kg/s "
      f"= {long_mdot_lbhr:,.0f} lb/hr")
print(f"choked: {long_['choked']}, exit P: {long_['P_stop']/PSI_TO_PA:.1f} psia, "
      f"exit quality: {long_['x_stop']:.3f}")

# --- Total relief load ---
total_kgs = short["mass_flow_rate"] + long_["mass_flow_rate"]
total_lbhr = short_mdot_lbhr + long_mdot_lbhr
print("\n=== Total relief load (Part 1 result) ===")
print(f"Total mdot = {total_kgs:.4f} kg/s = {total_lbhr:,.0f} lb/hr")

# --- Diagnostic plot: pressure at each leg's inlet vs. break/exit ---
fig, ax = plt.subplots(figsize=(7, 5))
ax.axhline(P_SHELL_BACK / PSI_TO_PA, color="gray", linestyle="--", label="Shell backpressure (165 psig)")
ax.plot([0, L_SHORT / FT_TO_M], [P0_SHORT / PSI_TO_PA, short["P_stop"] / PSI_TO_PA],
        marker="o", label=f"Short leg (liquid): {short_mdot_lbhr:,.0f} lb/hr")
ax.plot([0, L_LONG / FT_TO_M], [P_COLUMN / PSI_TO_PA, long_["P_stop"] / PSI_TO_PA],
        marker="o", label=f"Long leg (2-phase): {long_mdot_lbhr:,.0f} lb/hr")
ax.set_xlabel("Distance along leg from channel to break (ft)")
ax.set_ylabel("Pressure (psia)")
ax.set_title("Tube Rupture -- HEM Flashing Flow, Bottom Tubesheet Break")
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()
