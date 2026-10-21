# Florida Product Approval skill

An agent skill for reviewing building-envelope products (storefront, curtain wall, windows, doors) against their **Florida Product Approval (FL#)**. You give it the project facts (location/HVHZ, design wind pressures, missile level, glazing mode, opening sizes). It reads the approval's installation tables and tells you which mullions, glass and interlayers, anchorage, heads and sills, and door assemblies meet those requirements. The least capacity of the chosen components governs the system.

It uses the open [Agent Skills](https://agentskills.io) format (a folder with a `SKILL.md`), so the same folder works in **Claude Code** and **OpenAI Codex**, as well as claude.ai and other agents that read that format.

## Skills

| Skill | What it does |
| --- | --- |
| [`fl-product-approval`](skills/fl-product-approval/SKILL.md) | Reviews a project against an FL approval, and ingests new approvals from floridabuilding.org into its data store. |

Approvals ingested so far:
- **FL47012-R9: Kawneer IR 521/521T/521UT storefront.** Its sealed drawing IR521-FPA has been turned into 25 structured tables.
- **FL15404-R7: Kawneer IR 501T/501UT storefront.** This is a multi-product approval:
  - .1 LMI wet glazed;
  - .2 LMI dry glazed;
  - .3 SMI;
  - .4 Level E.

  Its four scanned drawings were transcribed and verified. The tables shared by .1–.3 are stored once, and each sub-product keeps only what differs.
- **FL47880-R0: Kawneer IR entrance doors.** Seven sub-products with door rating tables (lock, glass, hinge, assembly).

Any other approval goes through the same workflow: say "analyze FPA 16517" and the skill fetches, extracts and verifies it.

## Compatibility

| | Claude Code | Codex | claude.ai |
| --- | --- | --- | --- |
| Review a project | Yes | Yes | Yes (with code execution) |
| Ingest a new approval | Yes | Yes, with network enabled (see below) | No: needs floridabuilding.org access and a writable skill folder |
| Save learned rules | Yes | Yes | No: the uploaded skill is read-only |
| Project skill folder in this repo | `.claude/skills/` (symlink) | `.agents/skills/` (symlink) | n/a |
| Personal skill folder | `~/.claude/skills/` | `~/.agents/skills/` (older versions: `~/.codex/skills/`) | Upload a zip |
| Invoke explicitly | `/fl-product-approval` | `$fl-product-approval` or `/skills` | Mention it by name |

Both agents also pick the skill up on their own when you mention an FL number or a product series with a Florida approval.

Requirements on every platform:
- `python3` with `requests` and `pdfplumber` (`pip install -r requirements.txt`)
- `pdftotext` and `pdftoppm` from poppler-utils
- `tesseract`, only for ingesting scanned (older) approvals

## Install

### Recommended: work from a clone

The skill writes to its own folder when it ingests an approval (`data/`, `cache/`) or saves a rule you teach it (`RULES.md`). Working from a clone keeps that work in git, where you can review, commit and share it.

```bash
git clone https://github.com/schultzapps/fl-product-approval-skill.git
cd fl-product-approval-skill
pip install -r requirements.txt
```

Then start your agent in that folder:
- **Claude Code:** run `claude`. It finds the skill through `.claude/skills/fl-product-approval`.
- **Codex:** run `codex`. It finds the skill through `.agents/skills/fl-product-approval`.

Both links point at the same `skills/fl-product-approval` folder, so there is one copy of the data.

### Use it from any project

Symlink the clone into your personal skills folder, so new approvals and rules still land in the clone:

```bash
# Claude Code
mkdir -p ~/.claude/skills && ln -s "$PWD/skills/fl-product-approval" ~/.claude/skills/fl-product-approval
# Codex
mkdir -p ~/.agents/skills && ln -s "$PWD/skills/fl-product-approval" ~/.agents/skills/fl-product-approval
```

Or install a copy with the [skills CLI](https://github.com/vercel-labs/skills):

```bash
npx skills add schultzapps/fl-product-approval-skill
```

A copy is fine for reviews. Approvals you ingest or rules you teach go into that copy and are lost if you reinstall it.

### claude.ai

Zip the `skills/fl-product-approval` folder, leaving out `cache/`, and upload it as a skill in your claude.ai settings. Code execution must be on. The uploaded skill can review projects against the approvals already in it. To ingest new approvals, use Claude Code or Codex and upload a fresh zip.

### Codex sandbox notes

- **Network:** Codex's default sandbox blocks the network, and ingest has to reach floridabuilding.org. For an ingest session, allow network access: either set `network_access = true` under `[sandbox_workspace_write]` in `~/.codex/config.toml`, or approve the command when Codex asks to run it outside the sandbox.
- **Writes:** Codex can write only inside the workspace. If the skill is symlinked from `~/.agents/skills` to a clone outside your current project, ingest and rule saving are blocked. Run Codex from the clone for that work.

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
