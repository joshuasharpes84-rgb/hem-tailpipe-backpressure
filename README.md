# HEM Tailpipe Backpressure Calculator (API 521 §5.5.10)

Checks whether a pressure-relief valve's discharge pipe (tailpipe) can carry a **flashing two-phase
relief stream** without exceeding the valve's allowable built-up backpressure. It uses the homogeneous
equilibrium model (HEM) with Leung's omega method, per API 521 7th Ed. (June 2020) §5.5.10.

> **Make it yours, free:** download this repo (**Code → Download ZIP**, or `git clone`), open the folder in
> VS Code or any editor, and extend it for your own case with your AI assistant. This README is written for
> both of you. Taking these tools further is a free service of
> [Sharpes Process Engineering](https://jsharpes-portfolio.netlify.app); the site's Ask box can point you to the right starting file.
>
> **License:** [MIT](LICENSE) for the code and original text: use, modify and share freely, keeping the
> copyright notice. Provided as is, without warranty of any kind. It is an engineering study aid, not a
> substitute for a design checked and sealed by a licensed professional engineer.

- **Live tool:** https://jsharpes-portfolio.netlify.app/#hem-calc
- **Run it locally:** download this repo and open `index.html` in a browser. It needs no install and no server.
- **Related deck:** PSV Sizing, API 521 ([viewer](https://jsharpes-portfolio.netlify.app/slides/psv/),
  [outline](https://github.com/joshuasharpes84-rgb/process-engineering-decks/tree/main/decks/psv))
- **Author:** Joshua Sharpes, EIT. For engineering study only, not a substitute for a stamped relief-system design.

> **For AI assistants:** this README is the complete method description. It covers inputs, equations in
> solve order, sources, validation, and limits. The calculation itself is the `hemCalc()` function in
> `index.html`, with supporting functions above it. Saturation property tables are in `hem_component_data.js`.
> `project/hem_pipe_flow.py` is the separate full-flash Python solver used to validate the method.
> If a user asks "why did it say FAIL", look at the three checks in the "Results" section below.

## What it answers

Given a relief load, fluid, and tailpipe geometry: what pressure builds up at the valve outlet (p₁)?
Does the flow choke inside the pipe? Is the built-up backpressure inside the PRV type's limit?

| Input | Notes |
|---|---|
| Relief load W (lb/h) | mass flow through the valve |
| Component | Propane, n-Butane, Isobutane, Propylene, Ammonia, Chlorine, Water/Steam, or **Custom** (manual densities) |
| Vapor mass fraction x | used with the saturation tables to build two-phase densities |
| Reference point p_R, ρ_R | upstream two-phase state (usually relieving conditions) |
| Flash point p, ρ | second state used to fit omega |
| Pipe ID, equivalent length L | equivalent length includes fittings |
| Pipe material | sets roughness for the Churchill friction factor (named components only) |
| Fanning f | manual only for Custom fluid. Otherwise computed. |
| Exit pressure p₂ | pressure at the pipe outlet (atmosphere, flare header) |
| PRV type, set pressure | Conventional 10 %, balanced bellows 30 %, pilot-operated 50 % allowable built-up backpressure |

## Method (solve order)

1. **Two-phase density** at a pressure from the saturation table: `1/ρ = (1−x)/ρ_L + x/ρ_G`.
   Two-phase viscosity uses the McAdams quality-weighted harmonic mean.
2. **Friction factor:** Churchill (1977) Darcy factor from mixture Re and relative roughness, then
   Fanning = Darcy/4.
3. **Omega (two-point fit, Leung 1986):** `ω = (ρ_R/ρ − 1) / (p_R/p − 1)`.
   HEM specific volume: `v(p) = v_R·[1 + ω(p_R/p − 1)]`.
4. **Choking check:** critical pressure in USC units, `p_c = 5.8742×10⁻⁴ · G · √(ω p_R / ρ_R)`
   with G in lb/h·in², p in psia, ρ in lb/ft³. If p₂ < p_c, the exit is choked and p_c replaces p₂.
5. **Pipe integration:** the momentum balance with acceleration,
   `dL = −dp·[1 + (G²/g_c)·dv/dp] / [f G² v / (2 g_c D)]`, is integrated from the outlet pressure up to a
   trial p₁ (10,000 steps). p₁ is bisected until the integrated length equals L.
6. **Results:** ΔP across the pipe, inlet and exit velocity, built-up backpressure as % of set, and three
   PASS/FAIL checks:
   - choked inside the tailpipe (sonic velocity reached: undersized pipe)
   - built-up backpressure vs. the PRV-type allowable
   - upstream p₁ vs. relieving pressure (set × 1.1 + 14.696 psia)

The "Step-by-step detail" table on the page prints every intermediate value.

## Sources

- API STD 521, 7th Ed. (June 2020), §5.5.10, two-phase flow in relief piping (HEM / omega method)
- Leung, J.C. (1986), "A generalized correlation for one-component homogeneous equilibrium flashing
  choked flow," *AIChE J.* 32(10)
- Churchill, S.W. (1977), "Friction-factor equation spans all fluid-flow regimes," *Chem. Eng.* 84(24)
- Saturation properties: generated from the `thermo` Python library (Peng-Robinson-consistent correlations)

## Validation

The omega calculator is the fast screening form. The full-physics benchmark is `project/hem_pipe_flow.py`,
an HEM pipe-flow solver with a Peng-Robinson flash at every step. It stands in for DIERS TPHEM. It was
validated against published worked examples (`project/PSV Relief-Calculation Validation Report.pdf`):

| Case | Reference | Quantity | Reference | This work | Δ |
|---|---|---|---|---|---|
| Tube rupture, flashing propane | CCPS GPREH 2nd ed. App. D.1.2 | total relief load (lb/h) | 50,725 | 51,487 | +1.5 % |
| Steam-water long pipe | DIERS Project Manual App. II-E4-2 | choked mass flux (lb/s·ft²) | 366.7 | 381.2 | +4.0 % |
| Steam-water long pipe | same | sonic choke pressure (psia) | 42.3 | 45.9 | +8.5 %* |
| High-viscosity laminar flashing | DIERS Project Manual App. IV-A | mass flux G_L (kg/m²·s) | 31.5 | 31.46 | −0.14 % |

\*PR-EOS on steam-water is a known approximation. The deviation is in the expected direction.

## Assumptions and limits

- Homogeneous, equilibrium two-phase flow: no slip, no thermodynamic non-equilibrium. HEM is conservative
  (it predicts less flow capacity) for short pipes, where non-equilibrium flashing raises real capacity.
- Omega is fitted from two points. The page warns when the flash pressure p is above p₂, because ω is then
  being extrapolated beyond its calibrated range.
- Single component only. The saturation tables cover 7 fluids. Use Custom with your own flash densities for mixtures.
- Isothermal-equivalent friction factor, evaluated at reference conditions, held constant along the pipe.
- Does not size the valve orifice. Use API 520 Part I for that. This checks the outlet piping.

## Files

```
index.html            the tool (same code as the live site, standalone)
hem_component_data.js saturation density/viscosity tables, 7 fluids
project/
  hem_pipe_flow.py                     full-flash HEM pipe solver (Python, thermo + scipy)
  validation/                          scripts and output for the three benchmark cases
  PSV Relief-Calculation Validation Report.pdf
  HEM_Tailpipe_Calculator (original standalone).html   first version, before site integration
```

Python scripts need `numpy`, `scipy`, and `thermo`. Some scripts hard-code the author's local paths, so edit
those before running.

## Adapting it

- **Another fluid:** add a block to `hem_component_data.js` in the same shape (`p_psia`, `rhoL`, `rhoG`,
  `muL`, `muG`). Generate it from `thermo` or your simulator's saturation curve.
- **Different allowable:** PRV-type limits are the `hemPrvPct` values in `index.html`.
- **Mixtures or long lines:** use `project/hem_pipe_flow.py`, which flashes at every pressure step.
