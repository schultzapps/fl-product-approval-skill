# Ingesting a new approval

Example: "analyze FPA 16517".

## 1. Fetch

```bash
python3 scripts/fpa_fetch.py 16517          # or --rev N for a specific revision listed by the search
python3 scripts/catalog.py show 16517       # record + any KPA001 rows pointing at it
```

`fpa_fetch.py` posts the floridabuilding.org search form with the application number, opens the detail page (whose URL contains an encrypted `param`, so it has to come from the search), parses the record into `approval.json`, downloads every linked PDF to `cache/FL16517/` with a sha256, and rebuilds the index.

Check `approval.json` → `status`, `status_comments`, `code_version` and `quality_assurance_expires`, and the KPA001 row, for mismatches (for example a missile level or design pressure that differs from the live record).

## 2. Read the documents

- **Evaluation report** (1–3 pages): the compliance statement, code edition, HVHZ, missile levels per glazing type, required interlayers and materials, and the test reports.
- **Installation instructions** (the sealed drawing): start with sheet 1 (general notes, table of contents, abbreviations). Then read each capacity table: anchors, glass, mullions, jambs, corners, heads, sills, intermediate horizontals, doors.
- Check the text layer with `pdftotext -layout -f N -l N file.pdf -`. Sheets with no text layer are drawings only, so render them (`pdftoppm -r 110 -f N -l N -png file.pdf /tmp/sheet`) and read the image.

## 3. Write `extract_spec.json`

Follow the schema in `references/data-schema.md`.

- **Grid tables** in the Kawneer panel layout (Tributary Width | Mullion Height | values, with the height label spanning a block of rows) go in `tables`. For each one, give the page, the panel indexes (left to right, as found by the `Tributary` header words) and the value-column count. Then add `columns` (id, thermal, steel), `applies` (missile levels, glazing modes) and `variants` (member IDs from the detail drawings). Read applicability from **each panel's own title**: one sheet can hold two tables with different glazing modes or missile levels.
- **Anything else** (detail tables, glass capacity, glazing schedule, anchors, doors, rules) goes in `manual_tables` / `manual`. Copy values exactly, using `null` for "-".
- For a manufacturer with a different table layout, write a small parser in `scripts/` and keep the output in the same `components.json` schema, so `check_config.py` works unchanged.

## 4. Extract and verify

```bash
python3 scripts/extract_tables.py 16517     # strict: wrong cell counts, unlabeled blocks or non-ascending axes abort
python3 scripts/verify_manual.py 16517      # every hand-entered row must appear in the PDF text layer
```

Then spot-check at least one cell per grid table against the rendered sheet image.

## 5. Record

- Write `data/approvals/FL16517/NOTES.md`: the source revision and date, what was verified and how, discrepancies, open items, and anything not transcribed.
- Set `"ingest_status": "structured"` (or `"partial"`) in `approval.json`, then run `python3 scripts/catalog.py rebuild`.
- If the revision changes later, rerun `fpa_fetch.py`. If the sha256 of the installation PDF changed, re-extract and re-verify.
