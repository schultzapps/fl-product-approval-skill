# FL15404: Kawneer IR 501T / IR 501UT storefront ingest notes

- **Record:** FL15404-R7. Revision application, FBC 2023, status Approved; approved 10/17/2023. Method 1 Option D, evaluated by Warren W. Schaefer, P.E. (FL PE-44135). QA entity: Architectural Testing, Inc. (Intertek); QA contract expires 12/31/2026.
- **Standards:** AAMA 501, TAS 201/202/203, ASTM E1886 / E1996 / E330 / E283 / E331.
- **Multi-product approval.** Each sub-product (FL15404.1–.4) has its own drawing and evaluation report:

| Product | What it is | Drawing | Eval. report | Missile | Glazing | Data |
|---|---|---|---|---|---|---|
| FL15404.1 | IR501T/UT LMI storefront, wet glazed | 1758 (10 sheets) | WWS-208 | Large D | wet | `products/FL15404.1/` + `common/` |
| FL15404.2 | IR501T/UT LMI storefront, dry glazed | 1760 (10 sheets) | WWS-209 | Large D | dry | `products/FL15404.2/` + `common/` |
| FL15404.3 | IR501T/UT SMI storefront | 1759 (10 sheets) | WWS-210 | Small A | dry | `products/FL15404.3/` + `common/` |
| FL15404.4 | IR501T/UT Level E LMI storefront, wet glazed | 1981 (5 sheets) | WWS-379 | Large E | wet | `products/FL15404.4/` (standalone) |

- **What differs between .1, .2 and .3:** only the glass make-up and glazing method (sheet 8). The mullion, jamb and corner pressure tables, the D.L.O. size table, the frame anchor table and the project-out window limits are identical on drawings 1758, 1759 and 1760. They were compared side by side and are stored once in `common/components.json`.
- **.4 is a different system:** 2-3/4" framing only, frame height to 126", 60 psf maximum, different D.L.O. table, 0.180 SentryGlas 1-1/4" IG, and no CMU substrate, corners, expansion mullions or project-out windows.

## How the tables work (differs from FL47012)

- **Axes:** maximum **frame height** (not mullion height) × maximum **load width**.
- **Load width:**
  - intermediate mullion: glass centerline to glass centerline (= tributary width);
  - side jamb: frame edge to the first glass centerline;
  - corner: the greater of sides A and B.
- **Columns are end-anchor quantities:**
  - intermediate mullion: 6 or 4 per end;
  - side jamb: 3 or 2 per end (1758–1760); drawing 1981's jamb table header reads 6 / 4 (see open item 3);
  - corner mullion: 6 end anchors.
- **What governs:** pressure is set by the vertical framing and its end-anchor counts. There are no head, sill, horizontal or glass pressure tables; glass is limited by the D.L.O. size table.

## Verification performed (ingest of 2026-10-20)

- **Source format:** all drawings and evaluation reports are scanned images with no text layer. Evaluation reports were OCR'd with tesseract.
- **Transcription method:** drawing tables were transcribed visually from 200 dpi renders, then checked by OCR of each pressure column separately:
  - Every value matched except OCR's 5↔9 and 3↔5 confusions. Those produce impossible values above the 70/60 psf caps and were resolved against the image.
  - Row counts per table matched exactly: 34 / 33 / 22 rows for 1758–1760, 51 / 51 for 1981.
- **Cross-drawing check:** the mullion, jamb, corner, D.L.O. and anchor tables on 1758, 1759 and 1760 were compared side by side and agree.
- **Parts lists** (sheet 10 for 1758–1760, sheet 5 for 1981) give item descriptions only. Kawneer part numbers are not listed, except the 2-piece mullion 575-523 / filler 575-524.

## Discrepancies and open items

1. **"Comments: Archived"** appears on the R7 record page while the status is Approved, the same as FL47012. Confirm R7 is current.
2. **WWS-210 (FL15404.3) note 5** says small missile rated for "missile level D locations" and must be shuttered in large-missile locations. The Florida record and KPA001 call it Level A (small missile). The data treats .3 as missile A.
3. **Drawing 1981 side jamb table** column headers read "6 anchors / 4 anchors", while sheet 2 shows 3 anchors at each side jamb end (2 may apply). The data is stored as printed; confirm with the drawing before quoting anchor counts.
4. **KPA001 (Nov 2024)** lists .1/.2/.3 at ±70 psf and .4 as "Varies", glazing 1-1/4". That matches the drawings (70 / 60 psf caps).
5. **Pre-1981 sheets 6–7** (sections) and project-out window details were viewed but not transcribed. They are drawings only.
6. **Not modeled:** door/entrance framing. This approval has none.
