---
name: fl-product-approval
description: Florida Product Approval (FPA / FL#) review for building-envelope products — storefronts, curtain walls, windows, doors. Use when the user gives an FL number (e.g. "FL47012", "FPA 16517"), names a product series that has a Florida approval (e.g. Kawneer IR 521, Trifab 601T), or asks whether a configuration (mullions, glass/interlayers, anchors, heads/sills, doors) meets project design wind pressures, missile/impact level, or HVHZ requirements. Also use to ingest a new approval from floridabuilding.org into the skill's data store.
---

# Florida Product Approval review

This skill does two things:

1. **Review a project against an approval**: take the project facts (location, HVHZ, design pressures, missile level, glazing mode, frame type, opening sizes) and list which configurations in the approval's installation instructions meet them.
2. **Ingest an approval**: given an FL number, pull the record and its documents from the Florida Building Commission site and turn the sealed drawing's tables into structured data. Every approval follows the same path, so "analyze FPA 16517" means running the ingest workflow on 16517.

Paths below are relative to this skill directory. Scripts need `python3` with `requests` and `pdfplumber` (`pip install -r requirements.txt` at the repo root).

## Data store

- `data/index.json` is the catalog. It holds every ingested approval, keyed by FL number, plus lookups `by_category` (Florida category/subcategory), `by_manufacturer` and `by_series`, and a `backlog` of approvals listed in manufacturer directories (KPA001) that haven't been ingested yet. Run `python3 scripts/catalog.py find "<text>"` to search it.
- `data/approvals/FL<number>/` holds one folder per approval:
  - `approval.json`: the Florida record (revision, status, code edition, limits of use, documents with URLs and sha256).
  - `extract_spec.json`: hand-curated instructions describing how to read the drawing.
  - `components.json`: the structured capacity tables and rules. The review uses this file.
  - `NOTES.md`: verification log, discrepancies and open items. **Read it before quoting this approval.**
  - `RULES.md`: rules the user has taught for **this approval only** (see "Learned rules" below).
  - For a **multi-product approval** (see below), instead of one `components.json`:
    - `common/components.json`: tables shared by several sub-products.
    - `products/FL<n>.<k>/components.json`: one per sub-product. It holds what is specific to that product (glass, glazing method, missile level, any of its own tables), and `"extends": "../../common/components.json"` when it shares the common tables. A sub-product with a different system stands alone (no `extends`).
- `data/manufacturers/<slug>/RULES.md`: rules the user has taught that apply to every product from one manufacturer.
- `data/kpa/KPA001.json` is Kawneer's published approval directory, parsed into rows (series → FL number, missile rating, DP, glazing). It is maintained by hand and can be wrong: use it **only to find approvals**. Ratings, pressures and glazing come from the approval's own documents (general rule R-003).
- Source PDFs are downloaded to `<repo>/cache/` (git-ignored). Re-fetch them with `scripts/fpa_fetch.py`.

## Multi-product approvals (FL<n>.1, .2, ...)

One FL number often covers several **sub-products**, numbered `.1`, `.2`, `.3` and so on. Each is listed separately on the Florida record with its own limits of use, and usually its own installation drawing and evaluation report.

- **How they differ:** sub-products are usually largely the same system in different configurations, such as wet vs. dry glazing, large vs. small missile, a different glass make-up, or a Level E version.
- **Shared vs. separate data:** sometimes the framing tables are identical (FL15404.1–.3 share every mullion, jamb, corner and anchor table and differ only in glass and glazing). Sometimes one product is a different system (FL15404.4, Level E: different framing, heights, pressure cap and glass). Store shared tables once in `common/` and only the differences in `products/FL<n>.<k>/`.
- **During review:** always establish **which sub-product** applies before reviewing. Pick it from the project's missile level, glazing method and glass (`catalog.py show <n>` lists them). If more than one could fit, ask. Set `"approval": "FL15404.2"` in `project.json`. The checker refuses an ambiguous `FL15404` and lists the choices.
- **During ingest:** confirm whether the sub-products' drawings really are identical in a given table by comparing them side by side. Don't assume. Record the comparison in `NOTES.md`.
- **Rules:** learned rules for the approval live in `data/approvals/FL<n>/RULES.md`. A rule that applies to only one sub-product says so in its Scope line.

## Workflow A: review a project

1. Make sure the approval has been ingested (`data/approvals/FL<n>/components.json` or `products/*/components.json` exists). If it hasn't, run Workflow B first. For a multi-product approval, decide which sub-product applies (see above).
2. Collect the project facts using `references/project-intake.md`. **Ask for anything missing; don't assume it.** The most important items are:
   - Design pressures and their basis. The approval tables are **ASD**, while ASCE 7 C&C pressures are strength-level (multiply by 0.6 for ASD). Ask which one the user has.
   - Missile level (Large D, Large E, or Small A).
   - Field- or pre-glazed, and frame type (NT/T/UT).
   - Tributary width, mullion height (or **frame height**, for approvals whose tables use it, such as FL15404) and DLO for each typical and worst-case opening, plus shim gap and substrate. Check each table's `x_axis` / `y_axis` to see which inputs it uses.
3. Write a `project.json` file in the format of `examples/miami-dade-storefront.project.json` and run `python3 scripts/check_config.py project.json`. Add `--json` for structured output.
4. Explain the result to the user (see `references/review-method.md`):
   - For each component, list the options that pass (capacity ≥ required; no extra margin, see general rule R-001).
   - State that the **least capacity of the chosen components governs the system**.
   - Point out any component with no passing option, give the table limit that caused it (the report prints it), and suggest what to change (steel-reinforced or 5" mullion, narrower bay, more anchors per cluster, smaller shim gap, a different glazing schedule).
   - Repeat the flags and open items from `NOTES.md`.
   - Apply the learned rules in scope (see below) and say which rule you applied.
   - Cite drawing sheets (e.g. "IR521-FPA sheet 7").
5. Close with the limits: this is a screening aid. The engineer of record and the AHJ decide acceptability, and the approval doesn't cover water infiltration or substrate adequacy.

Questions the scripts don't cover (door hardware, part numbers, detail geometry, sheets that are drawings only) have to be answered from the drawing itself. Render the page with `pdftoppm -r 110 -f N -l N -png <pdf> /tmp/x` and read the image. Never invent a value that isn't in `components.json` or on a sheet you have looked at.

## Workflow B: ingest an approval (e.g. "analyze FPA 16517")

Follow `references/ingest-workflow.md`. In short:

1. `python3 scripts/fpa_fetch.py 16517` searches floridabuilding.org, saves `approval.json`, downloads the PDFs and updates the index.
2. Read the evaluation report (limits of use, glazing/interlayer limits, missile levels) and the installation instructions sheet by sheet: the general notes and table of contents first, then each capacity table.
3. Write `extract_spec.json`. Grid tables in the Kawneer panel layout are parsed automatically. Transcribe the other tables into `manual_tables` / `manual`, following `references/data-schema.md`.
4. Run `python3 scripts/extract_tables.py 16517` (strict validation) and `python3 scripts/verify_manual.py 16517` (checks hand-entered rows against the PDF text layer). Spot-check a few cells against the rendered sheet images.
   - **Scanned documents** (no text layer; `pdftotext` returns nothing, which is common for older approvals such as FL15404): OCR the evaluation reports with `tesseract`. Transcribe the drawing tables visually from 200 dpi renders. Then verify by OCR'ing each value column on its own and comparing against your transcription, which catches dropped or transposed cells. OCR confuses 5/9 and 3/5, so resolve every mismatch against the image.
   - **Multiple sub-products:** fetch records each sub-product's documents (`products[].documents` in `approval.json`). Ingest each one, sharing identical tables through `common/`.
5. Write `NOTES.md` recording what was verified and how, and any discrepancies (for example KPA001 vs the live record, unlabeled tables, or an imminent QA expiry). Set `ingest_status` in `approval.json`, then run `python3 scripts/catalog.py rebuild`.

## Learned rules (user-taught guidance)

When the user corrects you, states a practice ("for IR 521 we always...", "never use X when..."), or "trains" the skill on a product, save it so it persists. Keep it isolated to the scope it belongs to.

**Scopes, from narrowest to broadest:**
1. **Approval:** `data/approvals/FL<n>/RULES.md`. Use this when the rule mentions things that exist only in that approval: its member IDs (M5, 5M4, PGH7...), its tables or sheets, its glazing types. This is the default.
2. **Manufacturer:** `data/manufacturers/<slug>/RULES.md` (for example `kawneer`). Use this only when the user says the rule applies to all of that manufacturer's products.
3. **General:** `references/general-rules.md`. Use this only when the user says it applies to every product (for example a firm-wide practice on pressure basis or margins).

If the scope isn't clear, ask before saving. For example: "Is this IR 521 only, all Kawneer, or every product?"

**When reviewing approval FL<n>, read only:**
- that approval's `RULES.md`
- its manufacturer's `RULES.md`
- `references/general-rules.md`

Never apply another approval's rules. For example, IR 521 pre-glazed mullion rules must not leak into a Trifab 601T review. If a question about one product reminds you of a rule saved for another, you may mention that it exists, labeled as belonging to that other approval, but don't apply it.

**Precedence:** approval > manufacturer > general. The approval's own sealed documents (`components.json`, the drawing) outrank every learned rule. If a rule contradicts the approval, say so and follow the approval unless the user, as the responsible professional, decides otherwise. Record that decision in the rule entry.

**Entry format.** Append one entry per rule. Never silently rewrite an existing entry. If a rule is replaced, mark the old one superseded.

```
### R-003  Pre-glazed mullions: prefer expansion mullion over M-series
- Scope: FL47012 (IR 521) - pre-glazed only
- Rule: ...
- Why / source: user instruction 2026-10-19 ("..."), or a sheet reference
- Applies when: missile D, pre-glazed, mullion height > 108"
- Status: active | superseded by R-00x
```

After saving, run `python3 scripts/catalog.py rebuild` so the index records which approvals have rules, then tell the user which file the rule went into.

## Approvals ingested so far

Check `data/index.json`. As of this version it contains:
- **FL47012-R9:** Kawneer IR 521/521T/521UT storefront (field- or pre-glazed, Large Missile D/E, Small Missile A, HVHZ). Single product.
- **FL15404-R7:** Kawneer IR 501T/501UT storefront. Four sub-products:
  - .1 large missile D, wet glazed;
  - .2 large missile D, dry glazed;
  - .3 small missile A, dry glazed;
  - .4 large missile E, wet glazed.
  .1–.3 share their framing tables (`common/`). .4 is standalone. Tables use frame height × load width with end-anchor columns. Project-out GLASSvent windows apply to .1–.3.
