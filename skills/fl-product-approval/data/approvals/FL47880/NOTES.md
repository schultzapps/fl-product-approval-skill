# FL47880: Kawneer IR entrance doors (350 / 500 / HW / Flushline) ingest notes

- **Record:** FL47880 (revision 0; the search lists it as `FL47880` with no `-R` suffix). New application, FBC 2023, status Approved; submitted 10/22/2025, approved 12/09/2025. Category Exterior Doors / Swinging Exterior Door Assemblies. Method 1 Option D, evaluated by Hermes F. Norero, P.E. (FL PE-73778), drawings by Building Drops, Inc. QA entity: Architectural Testing, Inc. (Intertek); **QA contract expires 12/31/2026**.
- **Status comment on the record:** "Identify spacer as tested". m.c.
- **Design pressure on the record is "N/A"** for every product: pressures come only from the installation drawings.
- **KPA001:** no row points at FL47880, so it was never in the backlog. Nothing to reconcile.
- **Doors only.** None of these products includes storefront or curtain wall framing. Doors set in IR 500/501/521 storefront, Trifab 450/451/4511T or 1600 System 1 curtain wall rely on that framing's own approval (e.g. FL47012 for IR 521, FL15404 for IR 501T), and the lesser allowable pressure of the door and the framing governs.

## Products

Every product is standalone (`products/FL47880.<k>/components.json`, no `common/`). Each sub-product is a different door system with its own tables, so nothing is shared.

| Product | What it is | Drawing (sheets) | Eval. report | HVHZ | Rating basis | Max DP (psf) |
|---|---|---|---|---|---|---|
| FL47880.1 | 350 IR/HW outswing & bi-fold showroom doors | KAW046 (7) | PER9646 | yes | overall frame size, XX / XXX in Trifab 450/451 | 70 |
| FL47880.2 | 350/500 IR 8 ft. tall outswing doors | KAW042 (16) | PER9642 | yes | separate lock / glass / hinge tables (least governs) | 90 |
| FL47880.3 | 350/500 IR 9 ft. tall outswing doors | KAW041 (12) | PER9641 | yes | overall frame size by frame type | 65 |
| FL47880.4 | 350/500 IR outswing doors (WZ3) | KAW045 (17) | PER9645 | **no** | separate lock / glass / hinge tables (least governs) | 90 |
| FL47880.5 | Flushline outswing doors | KAW047 (13) | PER9647 | yes | door opening × frame × config × lock option, with wind zone per row | 75 |
| FL47880.6 | IR350/500 HW outswing doors | KAW044 (14) | PER9644 | yes | door opening × lock × glass, by frame family; missile D or E per row | 110 |
| FL47880.7 | IR350/500 HW outswing doors (WZ3) | KAW043 (14) | PER9643 | **no** | overall door opening size | 50 |

- **.2 vs .4** look alike: the same glass and lock tables apart from two differences, which is why they are stored separately.
  - .4 adds a Von Duprin XP-98/99 row (42 × 90, 50 psf) and lists rows in a different order.
  - Glazing detail 1 differs: .2 uses 0.090" Trosifol PVB, .4 uses 0.090" SentryGlas. Details 3/4 seal with 3M comp. tape on .2 and polyurethane foam on .4. The glass-option legend (3A–5D) is identical.
- **.4 and .7 (WZ3):** outside HVHZ only. No impact protective system is needed in Wind Zone 3 or less; one is required in Wind Zone 4 (eval. report limits 3–4). The checker flags this when the project sets `project.wind_zone`.
- **Missile ratings (general rule R-004, FL47880 rule R-002):** LMI = large missile Level D, and .6 is the only Level E product. Background: `references/missile-levels.md`. Each product's `missile` list:

| Product | Drawing wording | `missile` |
|---|---|---|
| .1, .3, .7 | "LMI/SMI" | D, A |
| .5 | "large and small impact rated" | D, A |
| .2, .4 | "(impact)" only | D |
| .6 | D or E per row | D, E (rows filter on the project's level) |

  The checker flags a project missile level that isn't in the product's list. Level A for small missile: SMI is the TAS 201 2 g steel ball at 130 ft/s, the same test as ASTM E1996 Level A (confirmed by web research, see `references/missile-levels.md`).

## How the door tables work (differs from FL47012 / FL15404)

- `components.json` → `door_ratings.tables[]`. Each table becomes one checker component: `door_lock`, `door_glass`, `door_hinge` or `door_assembly`. Pick one passing row per component; the least governs (sheet 1 note on .2/.4: "the lesser pressure in any one table shall control").
- **Size inputs differ by product:**
  - .1/.3: overall **frame** width × height;
  - .5/.6/.7: **door opening** width × height;
  - .2/.4 lock and hinge tables: **door leaf** width / height. Their glass tables use single-door leaf width or double-door opening width.
- **Leaf width fallback:** if a leaf size isn't given, the checker uses door opening ÷ number of leaves. That is conservative, since the real leaf is smaller by the clearances.
- `door_legend` gives the frame-to-door-opening and opening-to-D.L.O. deductions (e.g. 500/501 frame: D.O.(W) = FW − 5.00"). Use it to turn frame sizes into door opening sizes.
- **Not in the checker:** anchor schedules and anchor layouts are stored for the report (`installation_anchors`, `anchor_layouts`), not evaluated.

## Verification performed (ingest of 2026-10-21)

- **Source format:** every drawing and evaluation report has a text layer. Tables were transcribed from 110–330 dpi renders (pypdfium2; poppler/tesseract are not installed on this machine).
- **`verify_manual.py 47880`:** 59 rating rows checked. 53 match a row of the same ruled table in the PDF text layer, with merged cells filled down. The 6 misses are all on the .2 glass table (KAW042 sheet 1), where pdfplumber splits the columns and drops the single-door width. Those 6 rows were confirmed against a 220 dpi crop.
- **Visual-only tables** (outlined text, no text layer in the table): .5 KAW047 sheet 1 and .6 KAW044 sheet 1. Both were transcribed at 240–260 dpi, then re-read at 330 dpi and compared cell by cell against the stored rows (28 rows, all match). The .2 hinge limits come from the sheet 2 legend notes, not a table.
- **Glazing callouts** for .1, .3 and .5 were confirmed against the text layer; the others were read from zoomed crops.
- **Evaluation reports** (PER9641–9647) were read in full. All limits of use, standards and test reports are consistent with the drawings.

## Discrepancies and open items

1. **.6 missile E glass (KAW044 sheet 1):** the note says missile level E allows only lock options 1–3 and glass options **5 or 6**, but the missile E row at 110 / 90 psf lists glass option **4**. Options 4 and 6 are the 0.180" interlayer make-ups, so the note probably means "4 or 6". Stored as tabulated and flagged in `warnings`. Confirm with Kawneer or the PE before relying on that row.
2. **.6 column header** reads "450, 450, OR 1600 FRAMES"; stored as Trifab 450/451 and 1600 (presumed typo).
3. **.6 glass 1 and 6** say "Saflex by Kuraray" (Saflex is an Eastman product). Recorded as printed.
4. **"Von Durpin"** is printed on the .2/.4 lock tables; stored as Von Duprin.
5. **.5 wind zone column:** an HVHZ-listed product whose rows carry a wind zone rating of 3 or 4. The checker fails a row whose rating is below the project's `wind_zone`. How a WZ rating applies inside HVHZ is for the EOR/AHJ.
6. **.1 double door:** sheet 2 says the double swing configuration is heavy wall only ("only 350HW frame may be used"). Read as the 350HW door; the XX rows carry `door_series: ["350HW"]`.
7. **.2 / .4 mid-rail:** the mid-rail section (KAW042 sheet 6, KAW045 sheet 7) shall not be used above ±70 psf. This is not modelled; it is in `rules.notes`.
8. **Status comment** "Identify spacer as tested" suggests the commission asked for the IG spacer to be identified. The drawings call out aluminum spacers.
9. **QA expiry 12/31/2026:** re-fetch after that date.

## Not transcribed

Section details, bill of materials and component sheets (part numbers and profiles), and corner construction text beyond what is quoted in `rules.notes`. Read those from the drawings when needed.
