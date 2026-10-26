# Sources — PSVs (Relief Systems)

Where each type of information in this project comes from: the *PSV (API 521)* and *Runaway
Reaction Venting Requirements* decks, the HEM Tailpipe Backpressure calculator and its validation
cases, and the EO Runaway Relief Calculator. Topic-level, not number-by-number: the aim is to show
nothing was invented, and to point a reader to the right book and section if they want to dig.

**Tiers**
- **Library** — reference textbook in `Downloads\ChemE\Textbooks (Level 1)\` (used across projects)
- **Project PDF** — standard, paper or excerpt held in this folder's `Reference Materials\`
- **Web** — public page, URL given
- **Print only** — book cited from a paper copy; no digital copy for page lookup
- **Own work** — derived, fitted or chosen in this project; the basis is stated

Copyrighted PDFs are cited here but never published. Only public literature is used; no data from
any former employer.

## Standards and general relief practice

| Topic | Source | Tier | Location |
|---|---|---|---|
| Overpressure scenarios, protection philosophy, relief-piping two-phase flow (§5.5.10), fires | API STD 521, 7th ed. (2020) | Project PDF | `Reference Materials\API 521-Jun 2020_7th Edition - Marked.pdf` |
| Relief device sizing and selection; backpressure definitions | API 520 Part I | Project PDF | `Reference Materials\api-rp-520-1.pdf` |
| Installation, reaction forces | API 520 Part II | Project PDF | `Reference Materials\API-520-II.pdf` |
| Relief scenarios, device types, PSV sizing practice, correction factors | Crosby *Pressure Relief Valve Engineering Handbook*; CCPS *Guidelines for Engineering Design for Process Safety* (1993 Ch. 14; 2012) | Library + Project PDF | `Textbooks (Level 1)\Process Safety\`; Ch. 14 extract in `Reference Materials\` |
| Low-pressure tank venting (contrast) | API 2000 (cited in deck; not held) | Cited | — |

## Two-phase and runaway-reaction venting

| Topic | Source | Tier | Location |
|---|---|---|---|
| System classification (tempered / gassy / hybrid), applicable balances, Leung omega method, peak loads | CCPS *Guidelines for Pressure Relief and Effluent Handling Systems* (GPREH), §3.4–3.5, Ch. 4 | Project PDF | `Reference Materials\Guidelines for Pressure Relief and Effluent Handling.pdf` |
| Classification criteria by test result, valid sizing method per class (Table VI-2), Leung I/II/III, disengagement | DIERS Project Manual (*Emergency Relief System Design Using DIERS Technology*) | Project PDF | `Reference Materials\Emergency Relief System Design Using DIERS Technology\` |
| Where each classification source sits, page by page | Own source review (2026-09-26) | Own work | `Reference Materials\Tempered-Gassy-Hybrid Classification - Source Notes.md` |
| HEM / omega choked flow | Leung, J.C. (1986), *AIChE J.* 32(10) | Cited | — |
| Pipe friction factor | Churchill, S.W. (1977), *Chem. Eng.* 84(24) | Cited | — |
| Saturation properties for the HEM tool (7 fluids); Peng-Robinson flash in the benchmark solver | `thermo` Python library | Own work (generated) | `hem_pipe_flow.py` |

## Validation benchmarks (HEM)

| Case | Source | Tier | Location |
|---|---|---|---|
| Tube rupture, flashing propane | CCPS GPREH 2nd ed., App. D.1.2 | Project PDF | `Tube Rupture (Appendix D of GPREH)\` |
| Steam-water long pipe | DIERS Project Manual, App. II-E4-2 | Project PDF | `DIERS App II-E Validation (Steam-Water Pipe Flow)\` |
| High-viscosity laminar flashing | DIERS Project Manual, App. IV-A | Project PDF | `DIERS Appendix IV-A Validation (Laminar Flashing Flow)\` |
| Summary of all three | Own report | Own work | `PSV Relief-Calculation Validation Report.pdf` |

## EO Runaway Relief Calculator (`EO Runaway Tool\`)

Tags match the tool's README and `EO Runaway Tool\CLAUDE.md`.

| Topic | Source | Tier | Location |
|---|---|---|---|
| Primary-OH kinetics k11, EO Antoine and density, UNIFAC solubility (S96) | Di Serio et al., *Ind. Eng. Chem. Res.* 1996, 35, 3848 | Project PDF | `Reference Materials\EO Case Study\` |
| Heat of reaction 88–92 kJ/mol, EO liquid c_p, ×1.5 semibatch kinetic correction (Z26) | Zahnd et al., *Org. Process Res. Dev.* 2026, 30, 628 | Project PDF | as above (`op5c00362.pdf`) |
| Heats of reaction and decomposition, adiabatic runaway framing, decomposition near 200 °C (L23) | Loetgering-Lin et al. (BASF), *Chem. Eng. Trans.* 98 (2023) 51–56 | Project PDF | as above |
| Real 22 m³ alkoxylation runaway; accumulation, interlocks, quench tank (G03) | Gakhar & Carr, IChemE Symp. Ser. 149 (Baker Petrolite) | Project PDF | as above |
| EO polymerization / decomposition / isomerization heats, APTAC onset ~205 °C (D08) | Dinh, TAMU M.S. thesis (2008) | Project PDF | as above |
| Gas-phase EO decomposition kinetics, used with caution (C59) | Crocco et al., *J. Chem. Phys.* (1959) | Project PDF | as above |
| Plant basis: 6–10 m³, 3.62 / 4.45 bar, 16–28 kg/min feed, dip-leg sizes, 80 % fill, EO feed T (CH) | Chiu, Swinburne thesis | Project PDF | as above |
| EO and EG density and heat of vaporization (DIPPR-105/106); polyether c_p (Ruzicka-Domalski, Table 2-166); TEG density point | Perry's 9th ed., Sec. 2 | Library | `Textbooks (Level 1)\Handbooks & Quick Reference\Perry's 9th Edition.pdf` |
| UNIFAC activity coefficients γ_EO vs chain length | `thermo.unifac`, generated grid | Own work | `EO Runaway Tool\make_gamma_grid.py` |
| Dip-leg design velocity 0.255 m/s | Back-derived from the Chiu thesis's two plant data points (within 4 %) | Own work | `eo_runaway_model.js` |
| Polyether density rise with chain length | Fit to one real point (TEG) plus the high-MW PEG plateau; checked against DEG | Own work | `eo_runaway_model.js` |
| Stagnant-zone length; valve-to-nozzle line length | No source; flagged as advanced inputs | Own work | tool inputs |
