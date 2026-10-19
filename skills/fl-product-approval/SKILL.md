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
- `data/kpa/KPA001.json` is Kawneer's published approval directory, parsed into rows (series → FL number, missile rating, DP, glazing).
- Source PDFs are downloaded to `<repo>/cache/` (git-ignored). Re-fetch them with `scripts/fpa_fetch.py`.

## Workflow A: review a project

1. Make sure the approval has been ingested (`data/approvals/FL<n>/components.json` exists). If it hasn't, run Workflow B first.
2. Collect the project facts using `references/project-intake.md`. **Ask for anything missing; don't assume it.** The most important items are:
   - Design pressures and their basis. The approval tables are **ASD**, while ASCE 7 C&C pressures are strength-level (multiply by 0.6 for ASD). Ask which one the user has.
   - Missile level (Large D, Large E, or Small A).
   - Field- or pre-glazed, and frame type (NT/T/UT).
   - Tributary width, mullion height and DLO for each typical and worst-case opening, plus shim gap and substrate.
3. Write a `project.json` file in the format of `examples/miami-dade-storefront.project.json` and run `python3 scripts/check_config.py project.json`. Add `--json` for structured output.
4. Explain the result to the user (see `references/review-method.md`):
   - For each component, list the options that pass and the margin above the requirement.
   - State that the **least capacity of the chosen components governs the system**.
   - Point out any component with no passing option, give the table limit that caused it (the report prints it), and suggest what to change (steel-reinforced or 5" mullion, narrower bay, more anchors per cluster, smaller shim gap, a different glazing schedule).
   - Repeat the flags and open items from `NOTES.md`.
   - Cite drawing sheets (e.g. "IR521-FPA sheet 7").
5. Close with the limits: this is a screening aid. The engineer of record and the AHJ decide acceptability, and the approval doesn't cover water infiltration or substrate adequacy.

Questions the scripts don't cover (door hardware, part numbers, detail geometry, sheets that are drawings only) have to be answered from the drawing itself. Render the page with `pdftoppm -r 110 -f N -l N -png <pdf> /tmp/x` and read the image. Never invent a value that isn't in `components.json` or on a sheet you have looked at.

## Workflow B: ingest an approval (e.g. "analyze FPA 16517")

Follow `references/ingest-workflow.md`. In short:

1. `python3 scripts/fpa_fetch.py 16517` searches floridabuilding.org, saves `approval.json`, downloads the PDFs and updates the index.
2. Read the evaluation report (limits of use, glazing/interlayer limits, missile levels) and the installation instructions sheet by sheet: the general notes and table of contents first, then each capacity table.
3. Write `extract_spec.json`. Grid tables in the Kawneer panel layout are parsed automatically. Transcribe the other tables into `manual_tables` / `manual`, following `references/data-schema.md`.
4. Run `python3 scripts/extract_tables.py 16517` (strict validation) and `python3 scripts/verify_manual.py 16517` (checks hand-entered rows against the PDF text layer). Spot-check a few cells against the rendered sheet images.
5. Write `NOTES.md` recording what was verified and how, and any discrepancies (for example KPA001 vs the live record, unlabeled tables, or an imminent QA expiry). Set `ingest_status` in `approval.json`, then run `python3 scripts/catalog.py rebuild`.

## Approvals ingested so far

Check `data/index.json`. As of this version it contains FL47012-R9, Kawneer IR 521/521T/521UT storefront (field- or pre-glazed, Large Missile D/E, Small Missile A, HVHZ).
