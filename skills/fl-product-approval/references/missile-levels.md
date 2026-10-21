# Missile impact levels (ASTM E1996 A–E) and LMI / SMI

Background for setting a product's missile level at ingest and matching a project at review. The approval's own documents decide a product's rating (general rule R-003). The project's engineer or the AHJ sets the required level. Researched 2026-10-21 from vendor and lab summaries (sources below), not the standard's text: check ASTM E1996 and FBC Chapter 16 before quoting numbers in a deliverable.

## ASTM E1996 missile levels (impact per ASTM E1886)

| Level | Missile | Impact speed | Typical use |
|---|---|---|---|
| A | 2 g steel balls (5/16" nominal) | 130 ft/s | small missile: higher elevations (above 30 ft) |
| B | 2 lb 2x4 | 50 ft/s | lower wind zones; not used for walls |
| C | 4–4.5 lb 2x4 (sources differ) | 40 ft/s | wind zones 1–2 |
| D | 9 lb 2x4 | 50 ft/s (~34 mph) | large missile baseline for most hurricane-prone areas, 30 ft and below |
| E | 9 lb 2x4 | 80 ft/s (~55 mph) | enhanced protection: essential / critical facilities (hospitals, emergency operations centers, shelters) |

- **Height:** the large-missile levels (B–E) generally apply at 30 ft and below; Level A applies above 30 ft.
- **Wind zones:** wind zones (1–4, set by basic wind speed) select between B, C and D for basic protection. Summaries disagree on the speed thresholds, and recent editions move wind zone 4 to an appendix, so take the zone → level mapping from the standard edition the code adopts.

## LMI / SMI (Florida HVHZ terms, TAS 201 / 202 / 203)

- **LMI (large missile impact):** a 9 lb 2x4 per TAS 201, then cyclic pressure per TAS 203. TAS 201 shoots it at 50 or 80 ft/s.
  - At 50 ft/s it is the same test as **Level D**.
  - At 80 ft/s it matches Level E's speed.
  - FL approvals usually write "LMI - Level D". Per **general rule R-004**, an unqualified "LMI" is read as Level D; a product is Level E only where its documents say E.
- **SMI (small missile impact):** 2 g steel balls at 130 ft/s, the same as **Level A**.
  - In TAS 201 the small-missile test is run on the same specimen as the large-missile test.
  - "LMI/SMI" or "large and small missile" therefore covers Levels D and A.
- **HVHZ** (Miami-Dade, Broward): products are tested to TAS 201/202/203. Outside HVHZ, ASTM E1886/E1996 apply; FL evaluation reports state the equivalence between editions.

## How this skill records it

- Product `missile` key: a level or list, e.g. `["D", "A"]` for LMI/SMI, `["D", "E"]` where rows state E (FL47880.6). The checker flags a project level the product doesn't list.
- "Impact" with no level or LMI/SMI stated (e.g. FL47880.2/.4): recorded as Level D only, per R-004 and the user's FL47880 instruction (FL47880 rule R-002).

## Sources

- [Engineering Express: Overview of Missile Impact Levels](https://www.engineeringexpress.com/wiki/astm-e1996-missile-levels-definition/)
- [Intertek: ASTM E1996](https://w3inte.intertek-france.com/building/standards/astm-e1996)
- [Intertek: TAS 201 Impact Test Procedures](https://w3inte.intertek.co.th/building/standards/tas-201)
- [Miami-Dade County: product testing](https://www.miamidade.gov/building/testing.asp)
- [Graham Windows: hurricane impact test methods](https://grahamwindows.com/wp-content/uploads/hi_test-methods.pdf)
- [Kalwall: Windborne Debris Resistance](https://www.kalwall.com/wp-content/uploads/2022/01/Kalwall_Windborne-Debris-Resistance.pdf)
