# FL47012 — Kawneer IR 521 / 521T / 521UT storefront: ingest notes

- **Record:** FL47012-R9. Revision application, FBC 2023 (8th Ed.), status Approved; approved 08/11/2026. Method 1 Option D, evaluation report by Lucas A. Turner, P.E. (FL PE-58201).
- **Product:** FL47012.1, IR521 FG/PG NT/T/UT. HVHZ yes, outside HVHZ yes, impact resistant yes. The record's own design-pressure field is "N/A"; capacities come from the drawing.
- **Drawing:** IR521-FPA, initial release 6/8/2026, sealed 6/16/2026. 43 PDF pages; drawing sheets 1–21 correspond to PDF pages 1–21.
- **Standards:** AAMA 501-15, TAS 201/202/203-94.

## Verification performed (ingest of 2026-10-19)

| Data | Source sheet | How it was captured | Check |
|---|---|---|---|
| Anchor-cluster tables (1/4" and 3/8" shim) | 3 | panel parser | strict validation; cells spot-checked against layout text |
| Mullion tables: shallow-pocket, expansion, 5", Level E | 7–12 | panel parser | strict validation; sheet 7 compared cell-by-cell with the rendered image; others spot-checked |
| Corner and jamb tables | 13–15 | panel parser | strict validation; spot-checked |
| Head, sill, intermediate-horizontal detail tables | 16, 17, 19, 20 | hand transcription | `verify_manual.py`: every row found in the PDF text layer |
| Glass load capacity (field and pre) | 4 | hand transcription from the rendered image | `verify_manual.py`: all 40 rows found in the text layer |
| Glazing schedule G-A..G-F, sealant schedule, glazing materials | 4 | hand transcription from the image | visual |
| Table 1 installation anchors | 2 | text layer | visual |
| Door assembly table D1–D6 | 21 | text layer | visual |
| General notes, abbreviations, governing rule | 1 | image | visual |

## Discrepancies and open items

1. **"Comments: Archived"** appears on the R9 detail page even though the status is Approved. Confirm on floridabuilding.org that R9 is the current revision before relying on it.
2. **QA contract expires 12/31/2026** (Intertek). Recheck the record after that date.
3. **KPA001 (Nov 2024) lags the live record.** It lists FL# "47012" as LMI only (Zone 4, Level D & E, ±70 psf). The live record and evaluation report also cover **Small Missile Level A** (glazing G-F), and several tables go up to 90 psf.
4. **Sheet 10** (Level E shallow-pocket mullions) doesn't state field vs pre-glazed in its title. It is stored without a glazing-mode restriction and flagged in reports.
5. **Pre-glazed head table (sheet 17)** gives thermal types per detail (e.g. PGH10 = NT/T/UT), while the detail drawings on sheet 18 are labeled with one frame type (e.g. PGH10 "IR 521 UT"). The table is used as written; confirm against the detail when selecting a head.
6. **Expansion mullions E1–E5:** resolved by reading sheet 8 (2026-10-19). E1: NT/T, no steel, 2-1/2 to 2-3/4" face. E2: NT/T/UT, no steel, 2-3/4 to 3". E3: NT/T/UT, no steel, 3 to 3-1/4". E4: NT, with steel, 2-1/2 to 2-3/4". E5: NT/T/UT, with steel, 3 to 3-1/4". Stored in components.json variants.
7. **Door assemblies:** only a Level A/D table exists (sheet 21). No Level E door capacity was found. Door, transom and sidelite BOMs and assembly details (sheets 21–25N) and part drawings (27–29) are drawings only and were not transcribed.
8. **Anchor-cluster "Midspan Cluster Qty"** is read as the number of additional clusters required at midspan of the head/sill segment (sheets 2–3). Assumed to use the same anchor count as the end clusters; confirm on sheet 2/3 details.
9. The certificate-of-independence link on the record serves the same file as the evaluation report (identical sha256). The certification text is inside the evaluation report.
