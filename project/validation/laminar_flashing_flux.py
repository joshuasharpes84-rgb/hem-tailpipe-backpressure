"""
Laminar, flashing, homogeneous-equilibrium, two-phase Newtonian mass flux
(DIERS Project Manual, Appendix IV-A, Equation IV-A1 / Sample Problem 1).

For high-viscosity systems (Newtonian Reynolds number NRe = G*D/mu_f < 2000
at relief conditions), this is the Hagen-Poiseuille friction-pressure-drop
equation adapted to laminar, homogeneous-equilibrium, flashing flow: average
fluid density is taken as the homogeneous two-phase density at the pipe
exit pressure, and the average two-phase viscosity is taken as the liquid-
phase viscosity. Unlike hem_pipe_flow.py (which marches a trial-G choked
HEM solution through property flashes), this is a single closed-form
algebraic result driven directly by measured/estimated bench-scale
blowdown data -- no EOS flasher required.

CAUTION (per the manual): does not consider momentum pressure drop or
choking. Only valid when GL(measured)/GT(turbulent, calculated) < 0.2.

Sample Problem 1 (DIERS bench-scale blowdown data):
  dP/dT = 10,140 Pa/K,  T = 217 C,  Cp = 2399 J/kg K,
  mu_f = 545 cp,  D = 4.57 mm,  L/D = 175
  Reported answer: GL = 31.5 kg/m2 sec (6.4 lbm/ft2 sec)
"""

import numpy as np


def laminar_flashing_flux(dPdT, T, Cp, mu_f, D, L_over_D):
    """
    Eq. (IV-A1): laminar, flashing, homogeneous-equilibrium mass flux.

    Parameters (SI):
      dPdT     -- slope of the vapor pressure curve at T [Pa/K]
      T        -- average temperature during venting [K]
      Cp       -- liquid heat capacity [J/kg-K]
      mu_f     -- liquid viscosity [Pa-s]
      D        -- vent line diameter [m]
      L_over_D -- vent line length-to-diameter ratio [-]

    Returns GL [kg/m2-sec].
    """
    return (dPdT ** 2) * (T / Cp) * (1.0 / (32.0 * mu_f)) * (D / L_over_D)


def reynolds_number(G, D, mu_f):
    """NRe = G*D/mu_f; must be < 2000 for the laminar correlation to apply."""
    return G * D / mu_f


if __name__ == "__main__":
    # --- Sample Problem 1 inputs (SI) ---
    dPdT = 10_140.0      # Pa/K
    T = 217.0 + 273.15   # K
    Cp = 2399.0          # J/kg-K
    mu_f = 0.545         # Pa-s (545 cp)
    D = 4.57e-3          # m
    L_over_D = 175.0

    GL_TARGET = 31.5  # kg/m2 sec, DIERS reported answer

    print("=== Inputs (DIERS Appendix IV-A Sample Problem 1) ===")
    print(f"dP/dT = {dPdT:.0f} Pa/K")
    print(f"T     = {T:.2f} K")
    print(f"Cp    = {Cp:.0f} J/kg-K")
    print(f"mu_f  = {mu_f:.3f} Pa-s ({mu_f*1000:.0f} cp)")
    print(f"D     = {D*1000:.2f} mm")
    print(f"L/D   = {L_over_D:.0f}")

    GL = laminar_flashing_flux(dPdT, T, Cp, mu_f, D, L_over_D)
    NRe = reynolds_number(GL, D, mu_f)

    print("\n=== Result ===")
    print(f"GL = {GL:.2f} kg/(m2 sec)   [DIERS target: {GL_TARGET} kg/(m2 sec)]")
    print(f"Deviation from DIERS: {100*(GL-GL_TARGET)/GL_TARGET:+.2f}%")
    print(f"NRe = G*D/mu_f = {NRe:.1f}  (laminar correlation valid: {NRe < 2000})")
