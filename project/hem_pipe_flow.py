"""
Homogeneous Equilibrium Model (HEM) for choked / flashing two-phase flow of a
single-component fluid through a constant-diameter pipe segment.

Built as a stand-in for the DIERS TPHEM program (not available on this
workstation) for pressure-relief flashing-flow sizing problems -- e.g. the
tube-rupture worked example in CCPS GPREH Appendix D.1.2.

Method
------
Local thermodynamic state (density, quality, viscosity) comes from
pressure-enthalpy (PH) flashes via `thermo` (Peng-Robinson EOS). The fluid
is marched in small pressure decrements from a stagnation (near-zero
velocity) inlet state along the pipe at a trial constant mass flux G. At
each step the local specific volume must satisfy both the equilibrium
flash AND the steady adiabatic energy balance:

    h(P, v) = h0 - (G*v)^2 / 2

solved by fixed-point iteration. The HEM momentum balance is applied as a
finite control-volume step (no dv/dP derivative needed):

    -dP = G^2 dv + (f * v_avg * G^2)/(2 D) ds + rho_avg * g * sin(theta) ds

which is rearranged to solve for the pipe length ds consumed by each
pressure decrement dP. Summing ds down to the specified backpressure gives
the total pipe length "needed" for a trial G; this is monotonically
decreasing in G (more flow -> more friction/acceleration per unit dP, or
choking -- ds <= 0 -- cuts the march short). G is bisected so the length
needed exactly equals the leg's physical length (plus an entrance-loss
equivalent length), which is the classic shooting-method solution for
choked/backpressure-limited HEM pipe flow.

Sign convention: sin_theta = +1 for flow travelling vertically upward
(gravity opposes flow, adds resistance), -1 for vertically downward flow
(gravity assists), 0 for horizontal.
"""

import numpy as np
from scipy.optimize import brentq

G_GRAV = 9.80665  # m/s^2


def churchill_f(Re, rel_rough):
    """Churchill (1977) Darcy friction factor, valid across all Re."""
    Re = max(Re, 1.0)
    A = (2.457 * np.log(1.0 / ((7.0 / Re) ** 0.9 + 0.27 * rel_rough))) ** 16
    B = (37530.0 / Re) ** 16
    return 8.0 * ((8.0 / Re) ** 12 + 1.0 / (A + B) ** 1.5) ** (1.0 / 12.0)


def flash_ph_mass(flasher, MW, P, h_mass):
    """PH flash using mass-specific enthalpy [J/kg] (thermo wants molar J/mol)."""
    H_molar = h_mass * MW * 1e-3
    return flasher.flash(P=P, H=H_molar, zs=[1.0])


def homogeneous_viscosity(state):
    """McAdams mass-quality-weighted harmonic mean viscosity."""
    x = state.VF  # mole == mass quality for a pure component
    if x <= 0.0:
        return state.liquid0.mu()
    if x >= 1.0:
        return state.gas.mu()
    mu_l = state.liquid0.mu()
    mu_g = state.gas.mu()
    return 1.0 / (x / mu_g + (1.0 - x) / mu_l)


def _solve_v(flasher, MW, P, h0_mass, G, v_seed, max_iter=50, tol=1e-9):
    """Implicit local specific volume consistent with the energy balance.

    Returns (v, state), or (None, None) if the trial G drives the kinetic
    term (G*v)^2/2 so large that the implied local enthalpy has no
    physical PH-flash solution -- treated by the caller as an immediate
    choke rather than a crash (this happens routinely for the very high
    trial G values swept during the G_scan in solve_choked_hem).
    """
    v = v_seed
    state = None
    for _ in range(max_iter):
        h_local = h0_mass - 0.5 * (G * v) ** 2
        try:
            state = flash_ph_mass(flasher, MW, P, h_local)
        except Exception:
            return None, None
        v_new = 1.0 / state.rho_mass()
        if abs(v_new - v) <= tol * max(v, 1e-8):
            return v_new, state
        v = 0.5 * (v + v_new)  # damped update for stability near choke
    return v, state


def march_leg(flasher, MW, P0, G, D, roughness, sin_theta, P_back,
              K_entrance=0.5, n_steps=2000, VF0=0.0):
    """
    March one leg at fixed trial mass flux G [kg/(m2 s)] from stagnation
    conditions (P0, quality VF0) down to P_back (or until choked).

    Returns dict with:
      s_needed   -- pipe length [m] consumed to reach P_back, or to the
                    choke point if choking occurs first
      L_entrance -- equivalent length [m] of the K_entrance minor loss
      choked     -- True if the march ended by choking (ds <= 0) rather
                    than by reaching P_back
      P_stop     -- pressure [Pa] where the march ended
    """
    res0 = flasher.flash(P=P0, VF=VF0, zs=[1.0])
    h0_mass = res0.H_mass()
    v0 = 1.0 / res0.rho_mass()
    mu0 = homogeneous_viscosity(res0)

    f0 = churchill_f(G * D / mu0, roughness / D)
    L_entrance = K_entrance * D / f0

    P_steps = np.linspace(P0, P_back, n_steps)
    v_prev = v0
    s_accum = 0.0
    choked = False
    P_stop = P_back
    x_stop = VF0
    T_stop = res0.T

    for i in range(1, len(P_steps)):
        P_i = P_steps[i]
        v_i, state_i = _solve_v(flasher, MW, P_i, h0_mass, G, v_prev)
        if state_i is None:
            choked = True
            P_stop = P_steps[i - 1]
            break
        dP = P_steps[i - 1] - P_i
        dv = v_i - v_prev
        v_avg = 0.5 * (v_prev + v_i)
        rho_avg = 1.0 / v_avg
        mu_avg = homogeneous_viscosity(state_i)
        Re = G * D / mu_avg
        f = churchill_f(Re, roughness / D)
        friction_term = f * G ** 2 * v_avg / (2.0 * D)
        grav_term = rho_avg * G_GRAV * sin_theta
        denom = friction_term + grav_term
        numer = dP - G ** 2 * dv

        if denom <= 0.0 or numer <= 0.0:
            choked = True
            P_stop = P_steps[i - 1]
            break

        s_accum += numer / denom
        v_prev = v_i
        P_stop = P_i
        x_stop = state_i.VF
        T_stop = state_i.T

    return dict(s_needed=s_accum, L_entrance=L_entrance, choked=choked,
                P_stop=P_stop, x_stop=x_stop, T_stop=T_stop, G=G)


def solve_choked_hem(flasher, MW, P0, L, D, roughness, sin_theta, P_back,
                      K_entrance=0.5, n_steps=2000, VF0=0.0,
                      G_scan=None):
    """
    Find the mass flux G [kg/(m2 s)] through a pipe leg of physical length
    L such that the HEM momentum balance is exactly satisfied over
    L + entrance-loss-equivalent-length, either by reaching P_back
    (subsonic/unchoked exit) or by choking right at the exit.

    G is located via a log-spaced scan followed by bisection rather than a
    hand-picked bracket: for a gravity-assisted leg (sin_theta < 0) with a
    dense fluid, very low trial G is numerically degenerate (the gravity
    term alone can exceed the friction term, "choking" the march after a
    single step for reasons that have nothing to do with real acoustic
    choking) which breaks simple monotonic bracket assumptions. The
    physically meaningful root is the first transition, scanning upward in
    G, where the residual goes from positive to negative -- this skips
    over that low-G artifact (which shows a negative-to-positive jump
    instead) and lands on the true friction/acceleration-choking crossing.
    """
    def residual(G):
        r = march_leg(flasher, MW, P0, G, D, roughness, sin_theta, P_back,
                      K_entrance, n_steps, VF0)
        return r["s_needed"] - (L + r["L_entrance"])

    if G_scan is None:
        G_scan = np.logspace(1, 5.5, 80)  # ~10 to ~316,000 kg/(m2 s)

    resids = [residual(G) for G in G_scan]
    bracket = None
    for i in range(len(G_scan) - 1):
        if resids[i] >= 0 and resids[i + 1] < 0:
            bracket = (G_scan[i], G_scan[i + 1])
            break
    if bracket is None:
        raise RuntimeError(
            "No positive-to-negative residual crossing found while scanning "
            f"G from {G_scan[0]:.3g} to {G_scan[-1]:.3g}. Residuals: {resids}"
        )

    G_lo, G_hi = bracket
    G_star = brentq(residual, G_lo, G_hi, xtol=1e-2, rtol=1e-10)
    result = march_leg(flasher, MW, P0, G_star, D, roughness, sin_theta,
                        P_back, K_entrance, n_steps, VF0)
    A = 0.25 * np.pi * D ** 2
    result["A"] = A
    result["mass_flow_rate"] = G_star * A  # kg/s
    return result
