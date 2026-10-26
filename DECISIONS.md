# Engineering Decisions — PSVs (Relief Systems)

The calls that shaped the HEM Tailpipe Backpressure calculator, its validation, and the EO Runaway
Relief Calculator: what was decided, what was rejected, and why. Sources are in `SOURCES.md`.

*Built by Joshua Sharpes, EIT, with AI assistance (Claude) for drafting, coding and literature
checks. Scope, method selection, validation criteria and the corrections below are his.*

## HEM Tailpipe Backpressure calculator

**Validate against published solutions before trusting the model.** A from-scratch homogeneous
equilibrium (HEM) pipe-flow solver with a Peng-Robinson flash at every step stands in for DIERS
TPHEM. It was checked against three worked solutions (CCPS GPREH tube rupture, DIERS steam-water
pipe, DIERS laminar flashing), landing within −0.14 % to +8.5 %. The largest deviation is explained
(Peng-Robinson on steam-water is a known approximation) and is in the conservative direction. The
comparison is collected in `PSV Relief-Calculation Validation Report.pdf`.

**Engineering review of the tool (2026-09-12).** Joshua's review produced:
friction factor computed from pipe material roughness instead of entered by hand; reference pressure
capped at relieving pressure; a warning when the flash pressure exceeds exit pressure (the
evaluation then covers only part of the tailpipe); a flag when outlet pressure exceeds relieving
pressure; tighter slider ranges.

**Defined scope.** The tool checks outlet piping only. Orifice sizing is API 520 Part I's job and is
stated as outside the tool. Built-up backpressure follows the API 520 definition (outlet pressure
minus superimposed exit pressure).

## EO Runaway Relief Calculator

**Why EO.** Ethoxylation was chosen because Joshua worked alongside alkoxylation units at a
chemical plant and knows how they run. **Only public literature is used**; no former-employer data.

**What is being sized: the runaway, defined as the normal reaction accelerating.** Joshua set the
basis: the runaway is the normal KOH-catalyzed reaction accelerating on unreacted EO at normal
operating conditions, so the tool varies how much EO accumulates locally. EO decomposition is
coupled to that runaway, not treated as an independent event.

**Loss of mixing is the dominant scenario.** Catalyst deactivation is slow and self-limiting; an
agitator motor failure is instantaneous. Loss of mixing was chosen as the design basis.

**Kinetics challenged, which led to the main finding.** When early results showed a well-mixed batch
giving no relief demand, Joshua questioned it: tens of kilograms of EO reacting together should
exceed set pressure. Checking showed both were right. Dissolved EO in the well-mixed bulk is
pressure-limited to ~1.2 wt % (a 4–12 K rise, no relief). The hazard is a **local EO-rich pocket**
at the dip-leg outlet, which can react adiabatically by hundreds of kelvin once mixing restarts. The
tool sizes that pocket.

**Credible failure modes only.** Three modes are modeled: ESD closes the feed (A), ESD not credited
(B), power outage (C). A fourth (power outage, ESD fails and the feed continues) was removed on
Joshua's reasoning: in an outage the EO feed loses its own motive power regardless of the ESD.

**Geometry from the plant, not a percentage.** The pocket's carrier mass was first a fixed share of
the batch. Joshua's correction: it depends on the mass and density of what accumulates, so it is now
derived from dip-leg geometry, with the dip-leg sized from feed rate at a design velocity
back-derived from the thesis plant data. Joshua also pointed out that EO standing in the line between
the feed valve and the nozzle (set by maintenance clearance) keeps draining after the valve closes;
it is added for the modes where the ESD closes.

**Placeholders replaced with sourced properties.** Polyether heat capacity, densities and EO latent
heat started as estimates and were replaced with Perry's methods, each checked against a literature
value (within 0.3–1 %). A simple density additivity rule was tried and rejected for undershooting
triethylene glycol by 11 %.

**Conflicts reported, not resolved by choice.** Gas-phase decomposition kinetics (Crocco) imply
dormancy below ~350 °C; calorimetry (Dinh, BASF) shows onset near 200 °C. The tool runs the coupled
kinetics but flags the conservative ~200 °C marker. Kinetics are an octanol proxy pushed into a
high-EO regime, so a kinetic multiplier is exposed for sensitivity.

**Validation status, stated plainly.** Mass balance closes to 10⁻¹³; energy balance and property
functions checked; 180–252 input combinations run without error. Comparison with the Baker Petrolite
incident and a DIERS worked example is the next step, not yet done.

## Runaway Reaction Venting deck

**Classification checked across sources.** GPREH frames three system types; DIERS and CCPS (1993)
split them four ways by whether venting holds temperature constant, which is what decides the sizing
method. The source review behind the deck, page by page, is in `Reference Materials\Tempered-Gassy-
Hybrid Classification - Source Notes.md`.
