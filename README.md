# Florida Product Approval skill

An agent skill for reviewing building-envelope products (storefront, curtain wall, windows, doors) against their **Florida Product Approval (FL#)**. You give it the project facts (location/HVHZ, design wind pressures, missile level, glazing mode, opening sizes). It reads the approval's installation tables and tells you which mullions, glass and interlayers, anchorage, heads and sills, and door assemblies meet those requirements. The least capacity of the chosen components governs the system.

It uses the open [Agent Skills](https://agentskills.io) format (a folder with a `SKILL.md`), so the same folder works in **Claude Code** and **OpenAI Codex**, as well as claude.ai and other agents that read that format.

## Supported approvals

| FL# | Rev | Product | Type | Sub-products | Missile levels | HVHZ | Approved | QA expires |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| [FL47012](skills/fl-product-approval/data/approvals/FL47012/NOTES.md) | R9 | Kawneer IR 521 / 521T / 521UT | Storefront | 1 | D, E, A | Yes | 2026-08-11 | 2026-12-31 |
| [FL15404](skills/fl-product-approval/data/approvals/FL15404/NOTES.md) | R7 | Kawneer IR 501T / 501UT | Storefront | 4 | D, E, A | Yes | 2023-10-17 | 2026-12-31 |
| [FL47880](skills/fl-product-approval/data/approvals/FL47880/NOTES.md) | R0 | Kawneer 350 / 500 IR entrance doors | Swinging exterior doors | 7 | D, E, A | Yes, except .4 and .7 | 2025-12-09 | 2026-12-31 |

Missile levels: D and E are large missile, A is small missile. An unqualified "LMI" means Level D.

### Sub-products

| Sub-product | Description | Missile | HVHZ | Drawing |
| --- | --- | --- | --- | --- |
| FL47012.1 | IR 521 storefront, field or pre-glazed, NT/T/UT frames | D, E, A | Yes | IR521-FPA |
| FL15404.1 | IR 501T/UT storefront, wet glazed | D | Yes | 1758 |
| FL15404.2 | IR 501T/UT storefront, dry glazed | D | Yes | 1760 |
| FL15404.3 | IR 501T/UT storefront, small missile | A | Yes | 1759 |
| FL15404.4 | IR 501T/UT storefront, wet glazed, Level E | E | Yes | 1981 |
| FL47880.1 | 350 IR/HW outswing and bi-fold showroom doors | D, A | Yes | KAW046 |
| FL47880.2 | 350/500 IR outswing doors, 8 ft | D | Yes | KAW042 |
| FL47880.3 | 350/500 IR outswing doors, 9 ft | D, A | Yes | KAW041 |
| FL47880.4 | 350/500 IR outswing doors (Wind Zone 3) | D | No | KAW045 |
| FL47880.5 | Flushline outswing doors | D, A | Yes | KAW047 |
| FL47880.6 | IR 350/500 HW outswing doors | D, E | Yes | KAW044 |
| FL47880.7 | IR 350/500 HW outswing doors (Wind Zone 3) | D, A | No | KAW043 |

FL15404.1–.3 share their framing tables. FL47880 covers the doors only; the storefront or curtain wall around them is reviewed under its own approval.

Each FL# links to its `NOTES.md`, which records how the tables were verified and any open items. Always confirm the current revision on [floridabuilding.org](https://www.floridabuilding.org/pr/) before relying on a review.

## Install

```bash
git clone https://github.com/schultzapps/fl-product-approval-skill.git
cd fl-product-approval-skill
pip install -r requirements.txt
```

Requirements: `python3` with `requests` and `pdfplumber` (installed above), and `pdftotext`/`pdftoppm` from poppler-utils. Ingesting scanned approvals also needs `tesseract`.

### Claude Code

Run `claude` in the clone. It finds the skill through `.claude/skills/fl-product-approval`. To use it from any project, link it into your personal skills folder:

```bash
mkdir -p ~/.claude/skills && ln -s "$PWD/skills/fl-product-approval" ~/.claude/skills/fl-product-approval
```

Invoke it with `/fl-product-approval`, or just mention an FL number or product series.

### Codex

Run `codex` in the clone. It finds the skill through `.agents/skills/fl-product-approval`. To use it from any project, link it into your personal skills folder:

```bash
mkdir -p ~/.agents/skills && ln -s "$PWD/skills/fl-product-approval" ~/.agents/skills/fl-product-approval
```

Invoke it with `$fl-product-approval`, or just mention an FL number or product series.

Codex's default sandbox blocks the network and writes outside the current project. To ingest a new approval, run Codex from the clone and allow network access: set `network_access = true` under `[sandbox_workspace_write]` in `~/.codex/config.toml`, or approve the command when Codex asks.

### claude.ai

Zip the `skills/fl-product-approval` folder without `cache/` and upload it as a skill in your settings, with code execution on. It can review projects against the approvals already in it, but can't ingest new ones or save rules.

### Linked, not copied

Both agents read the same `skills/fl-product-approval` folder through links. Approvals you ingest and rules you teach are written there, so they stay in this repository.

## Layout

```
skills/fl-product-approval/      # the skill: copy or link this folder to install it
  SKILL.md                       # when the skill triggers + the two workflows (review, ingest)
  requirements.txt               # Python dependencies for the scripts
  references/                    # project intake, review method, ingest workflow, data schema, general rules
  scripts/
    fpa_fetch.py                 # FL number -> floridabuilding.org record + PDFs + approval.json
    kpa_parse.py                 # Kawneer KPA001 directory -> data/kpa/KPA001.json
    panel_parse.py               # parser for Kawneer-style load tables (coordinate-based)
    extract_tables.py            # extract_spec.json + drawing PDF -> components.json (strict validation)
    verify_manual.py             # hand-entered rows must appear in the PDF text layer
    catalog.py                   # data/index.json: by FL#, category, manufacturer, series; KPA backlog
    check_config.py              # project.json -> pass/fail options per component (Markdown or JSON)
  examples/                      # example project.json files and a worked example
  data/
    index.json                   # catalog (by FL#, by category, by manufacturer, by series, backlog)
    kpa/KPA001.json              # Kawneer published approval directory (Nov 2024), 89 rows
    manufacturers/<slug>/RULES.md
    approvals/FL47012/           # approval.json, extract_spec.json, components.json, NOTES.md, RULES.md
    approvals/FL15404/           # multi-product: common/components.json + products/FL15404.1..4/components.json
    approvals/FL47880/           # multi-product doors: products/FL47880.1..7/components.json
  cache/                         # downloaded PDFs (git-ignored; re-fetch with fpa_fetch.py)
.claude/skills/fl-product-approval -> ../../skills/fl-product-approval   # Claude Code project skill
.agents/skills/fl-product-approval -> ../../skills/fl-product-approval   # Codex project skill
requirements.txt                 # points at skills/fl-product-approval/requirements.txt
```

## Use without an agent

The scripts run on their own:

```bash
cd skills/fl-product-approval
python3 scripts/check_config.py examples/miami-dade-storefront.project.json   # review a project
python3 scripts/fpa_fetch.py 16517                                           # start ingesting another approval
python3 scripts/catalog.py find "IR 521"                                     # look things up
python3 scripts/catalog.py backlog                                           # KPA001 approvals not yet ingested
```

## Limits

This is a screening and assistance tool, not an engineering approval. The capacities are transcribed from the sealed drawings, and the extraction and verification steps are recorded in each approval's `NOTES.md`. Always confirm the current revision on floridabuilding.org. The engineer/architect of record and the AHJ decide acceptability. Water infiltration, flashing and substrate adequacy are outside the scope of a product approval.
