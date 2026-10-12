"""
Validation case for hem_pipe_flow.py against the DIERS Project Manual,
Appendix II-E, Section II-E4-2 "Pipe Flow" worked example (steam-water,
long-pipe HEM model).

Problem (DIERS manual, pages 113/37-41 of Appendix II-E):
  5 wt% steam in saturated water, stagnation at 100 psia, flowing from a
  large (48-in.) vessel through a vertical 2-in. i.d. duct with a square-cut
  entrance flush with the vessel wall (K=0.5) to atmospheric backpressure.
  Target flow rate: 8 lb/sec (G = 366.7 lb/sec-ft2 through the 2-in. pipe).

  DIERS solves this as an inverse problem: fix G, march down the pipe,
  and find the length at which the flow chokes. Reported answer: flow
  chokes at P = 42.3 psia after L = 36.3 ft of pipe (measured from the
  post-entrance state at P=93.6 psia; the entrance pressure drop of 100 ->
  93.6 psia is computed separately via the incompressible K-factor
  correlation, not as an equivalent length).

  hem_pipe_flow.py instead fixes L and P_back and solves for the choked G
  (folding the entrance loss in as an equivalent length via
  L_entrance = K*D/f rather than a discrete pre-drop). To validate, we feed
  it DIERS's answer -- L = 36.3 ft, P_back = atmospheric -- and check that
  it comes back with G close to 366.7 lb/sec-ft2 and a choke point near
  P = 42.3 psia.

Known sources of mismatch:
  - DIERS uses real steam-table properties; this script uses `thermo`'s
    Peng-Robinson EOS for water, which is a rough approximation for
    steam-water two-phase properties (this is a general limitation of
    hem_pipe_flow.py, noted in its own docstring).
  - DIERS's friction factor (f=0.00457 at Re=498,000, their Fanning
    convention) is not tied to an explicit roughness; a commercial steel
    roughness (0.0018 in, same default used in the Tube Rupture script)
    gives a Darcy f of the same order (~0.018-0.02) and is used here.
  - hem_pipe_flow.py folds the entrance loss into an equivalent pipe
    length, rather than DIERS's discrete pre-drop; the two are standard-
    equivalent methods but won't match to the last psi.
"""

import sys
import os
from thermo import ChemicalConstantsPackage, CEOSGas, CEOSLiquid, PRMIX, FlashPureVLS

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from hem_pipe_flow import solve_choked_hem

# --- Unit conversions ---
PSI_TO_PA = 6894.76
FT_TO_M = 0.3048
IN_TO_M = 0.0254
KG_TO_LB = 2.20462
LB_SEC_FT2_TO_KG_SM2 = 4.88243

# --- DIERS Appendix II-E4-2 problem inputs ---
P0 = 100 * PSI_TO_PA               # stagnation pressure, psia -> Pa
VF0 = 0.05                         # 5 wt% steam quality (mass == mole for pure water)
D = 2 * IN_TO_M                    # 2-in i.d. duct
L = 36.3 * FT_TO_M                 # DIERS's reported choke length (post-entrance)
P_BACK = 14.696 * PSI_TO_PA        # atmospheric
K_ENTRANCE = 0.5                   # square-cut entrance flush with vessel wall
ROUGHNESS = 0.0018 * IN_TO_M       # commercial steel, default assumption (as in Tube Rupture script)

# DIERS reported answer, for comparison
G_TARGET_KG_SM2 = 366.7 * LB_SEC_FT2_TO_KG_SM2
P_STOP_TARGET_PA = 42.3 * PSI_TO_PA

# --- Build the water PR-EOS flasher ---
constants, correlations = ChemicalConstantsPackage.from_IDs(["water"])
MW = constants.MWs[0]
eos_kwargs = dict(Tcs=constants.Tcs, Pcs=constants.Pcs, omegas=constants.omegas)
gas = CEOSGas(PRMIX, HeatCapacityGases=correlations.HeatCapacityGases, eos_kwargs=eos_kwargs)
liq = CEOSLiquid(PRMIX, HeatCapacityGases=correlations.HeatCapacityGases, eos_kwargs=eos_kwargs)
flasher = FlashPureVLS(constants, correlations, gas=gas, liquids=[liq], solids=[])

print("=== Inputs ===")
print(f"Stagnation P0:  {P0/PSI_TO_PA:.1f} psia, quality x0 = {VF0:.3f}")
print(f"Duct: D = {D/IN_TO_M:.2f} in, L = {L/FT_TO_M:.1f} ft, vertical upward")
print(f"Entrance K = {K_ENTRANCE}, roughness = {ROUGHNESS/IN_TO_M:.4f} in (commercial steel assumption)")
print(f"Backpressure: {P_BACK/PSI_TO_PA:.2f} psia")

print("\n=== Solving (HEM march, sin_theta=+1 for vertical upflow) ===")
result = solve_choked_hem(
    flasher, MW, P0=P0, L=L, D=D, roughness=ROUGHNESS,
    sin_theta=+1.0, P_back=P_BACK, K_entrance=K_ENTRANCE,
    VF0=VF0,
)

G_lbsecft2 = result["G"] / LB_SEC_FT2_TO_KG_SM2
mdot_lbsec = result["mass_flow_rate"] * KG_TO_LB
P_stop_psia = result["P_stop"] / PSI_TO_PA

print(f"\nG            = {result['G']:.1f} kg/(m2 s)  = {G_lbsecft2:.1f} lb/(sec-ft2)"
      f"   [DIERS target: 366.7 lb/(sec-ft2)]")
print(f"mass flow    = {result['mass_flow_rate']:.4f} kg/s = {mdot_lbsec:.2f} lb/sec"
      f"   [DIERS target: 8.0 lb/sec]")
print(f"choked       = {result['choked']}")
print(f"exit P       = {P_stop_psia:.1f} psia   [DIERS target: 42.3 psia]")
print(f"exit quality = {result['x_stop']:.4f}")
print(f"exit T       = {result['T_stop']:.1f} K")

print("\n=== Percent deviation from DIERS steam-table answer ===")
print(f"G:      {100*(result['G']-G_TARGET_KG_SM2)/G_TARGET_KG_SM2:+.1f}%")
print(f"P_stop: {100*(result['P_stop']-P_STOP_TARGET_PA)/P_STOP_TARGET_PA:+.1f}%")
