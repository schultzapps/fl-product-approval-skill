# Project intake

Collect these facts before running a review. If any are missing, ask for them, and if you have to proceed on an assumption, state it in the report.

| Item | Why it matters | `project.json` field |
|---|---|---|
| Project name, address, county | HVHZ is Miami-Dade and Broward counties; it also sets the wind speed and debris region | `project.location`, `project.hvhz` |
| Code edition | Approvals are tied to an FBC edition (e.g. 2023 = 8th Ed.). Check `approval.json` → `code_version` | `project.code` |
| Risk category, Vult (mph), exposure, mean roof height | Inputs to the engineer's C&C pressures; record them for traceability | `project.*` (free form) |
| Design pressures, positive and negative, per zone (4 and 5 near corners) | Compared against the tables. Use the worst zone the opening sits in | `design_pressures.positive_psf / negative_psf` |
| Pressure basis | Approval tables are **ASD**. ASCE 7 C&C pressures are strength-level, so ASD = 0.6 × strength. Ask which one the user has | `design_pressures.basis` = `ASD` or `strength` |
| Missile level | Selects the glazing schedules (FL47012: D → G-A to G-D, E → G-E, A → G-F) and the mullion/jamb/sill tables. The project's engineer or AHJ sets the required level by location and height | `missile_level` = `D`, `E` or `A` |
| Field- or pre-glazed | Many tables are limited to one mode | `glazing_mode` = `field` or `pre` |
| Thermal frame | NT (no thermal break), T (one) or UT (two) | `thermal` |
| Preferred glazing | Optional filters: schedule, sealant (WG-D/WG-G/WG-T/DG), direction (OG/IG) | `glazing.schedule`, `glazing.sealant`, `glazing.direction` |
| Each typical and worst-case opening | Tributary width = (left bay width + right bay width) / 2. Mullion height = max mullion length. DLO = daylight opening | `openings[].tributary_width_in`, `mullion_height_in`, `dlo_width_in`, `dlo_height_in` |
| Members to check | Any of `glass`, `mullion`, `jamb`, `corner`, `head`, `sill`, `intermediate_horizontal`, `anchor_cluster`, `door` | `openings[].members` |
| Shim gap at head/sill | Selects the anchor-cluster table (FL47012: 1/4" or 3/8" max) | `openings[].shim_gap_in` |
| Substrate | Picks the anchor type from Table 1 (concrete, wood, steel/aluminum) | report text; see `components.json` → `installation_anchors` |
| Door openings | Width and height for the door-assembly table | `openings[].door_width_in`, `door_height_in` |
| Zone-specific pressure | Optional per-opening override (ASD) | `openings[].pressure_psf_asd` |

**Tributary width:** a bay is the mullion-to-mullion spacing. For an intermediate mullion, tributary width = (bay on its left + bay on its right) / 2.
- With equal bays it **equals the mullion spacing**. Mullions every 60" give a 60" tributary width, not 120". When a table allows tributary width X, it allows equal bays (mullion spacing) of X.
- A jamb or other end member carries only half of its single adjacent bay: tributary width = end bay / 2.

Example file: `examples/miami-dade-storefront.project.json` (illustrative values only).
