# Florida Product Approval skill

A Claude skill for reviewing building-envelope products (storefront, curtain wall, windows, doors) against their **Florida Product Approval (FL#)**. You give it the project facts (location/HVHZ, design wind pressures, missile level, glazing mode, opening sizes). It reads the approval's installation tables and tells you which mullions, glass and interlayers, anchorage, heads and sills, and door assemblies meet those requirements. The least capacity of the chosen components governs the system.

The first approval ingested is **FL47012-R9: Kawneer IR 521/521T/521UT storefront**. Its sealed drawing IR521-FPA has been turned into 25 structured tables. Any other approval goes through the same workflow: say "analyze FPA 16517" and the skill fetches, extracts and verifies it.

## Layout

```
skills/fl-product-approval/
  SKILL.md                     # when the skill triggers + the two workflows (review, ingest)
  references/                  # project intake, review method, ingest workflow, data schema
  scripts/
    fpa_fetch.py               # FL number -> floridabuilding.org record + PDFs + approval.json
    kpa_parse.py               # Kawneer KPA001 directory -> data/kpa/KPA001.json
    panel_parse.py             # parser for Kawneer-style load tables (coordinate-based)
    extract_tables.py          # extract_spec.json + drawing PDF -> components.json (strict validation)
    verify_manual.py           # hand-entered rows must appear in the PDF text layer
    catalog.py                 # data/index.json: by FL#, category, manufacturer, series; KPA backlog
    check_config.py            # project.json -> pass/fail options per component (Markdown or JSON)
  examples/                    # illustrative project.json
  data/
    index.json                 # catalog (by FL#, by category, by manufacturer, by series, backlog)
    kpa/KPA001.json            # Kawneer published approval directory (Nov 2024), 89 rows
    approvals/FL47012/         # approval.json, extract_spec.json, components.json, NOTES.md
.claude/skills/fl-product-approval -> skills/fl-product-approval   (so Claude Code picks it up in this repo)
cache/                         # downloaded PDFs (git-ignored; re-fetch with fpa_fetch.py)
```

## Use

```bash
pip install -r requirements.txt
cd skills/fl-product-approval

python3 scripts/check_config.py examples/miami-dade-storefront.project.json   # review a project
python3 scripts/fpa_fetch.py 16517                                           # start ingesting another approval
python3 scripts/catalog.py find "IR 521"                                     # look things up
python3 scripts/catalog.py backlog                                           # KPA001 approvals not yet ingested
```

To use it in Claude Code from another project, copy or symlink `skills/fl-product-approval` into `~/.claude/skills/`. For claude.ai, zip the `skills/fl-product-approval` folder and upload it as a skill. Ingesting new approvals needs network access to floridabuilding.org.

## Limits

This is a screening and assistance tool, not an engineering approval. The capacities are transcribed from the sealed drawings, and the extraction and verification steps are recorded in each approval's `NOTES.md`. Always confirm the current revision on floridabuilding.org. The engineer/architect of record and the AHJ decide acceptability. Water infiltration, flashing and substrate adequacy are outside the scope of a product approval.
