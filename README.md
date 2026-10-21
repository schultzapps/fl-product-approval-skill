# Florida Product Approval skill

An agent skill for reviewing building-envelope products (storefront, curtain wall, windows, doors) against their **Florida Product Approval (FL#)**. You give it the project facts (location/HVHZ, design wind pressures, missile level, glazing mode, opening sizes). It reads the approval's installation tables and tells you which mullions, glass and interlayers, anchorage, heads and sills, and door assemblies meet those requirements. The least capacity of the chosen components governs the system.

It uses the open [Agent Skills](https://agentskills.io) format (a folder with a `SKILL.md`), and is published as a plugin for **Claude Code** and **OpenAI Codex**. The same skill folder also works in claude.ai and other agents that read that format.

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

### Requesting an approval

Approvals are added by the publisher, who ingests and checks each one before releasing it as an update. To request one, [open an issue](https://github.com/schultzapps/fl-product-approval-skill/issues) with the FL number. If you ask the skill about an approval that isn't listed here, it will tell you it isn't in the library yet.

## Install (customers)

The skill is published as a plugin for **Claude Code** and **Codex** from this repository. Install it once, and you get new approvals and fixes when you update.

### Claude Code

In a Claude Code session:

```
/plugin marketplace add schultzapps/fl-product-approval-skill
/plugin install fl-product-approval@fl-product-approval
```

To get updates automatically, open `/plugin`, go to **Marketplaces**, select `fl-product-approval` and choose **Enable auto-update**. To update by hand, run `/plugin marketplace update fl-product-approval`.

### Codex

```bash
codex plugin marketplace add schultzapps/fl-product-approval-skill
codex plugin add fl-product-approval@fl-product-approval
```

To update, run `codex plugin marketplace upgrade fl-product-approval`.

### Other agents and claude.ai

- **Other agents that read the [Agent Skills](https://agentskills.io) format:** run `npx skills add schultzapps/fl-product-approval-skill`, and later `npx skills update` to get updates.
- **claude.ai:** download the latest `skills/fl-product-approval` folder, zip it without `cache/`, and upload it as a skill in your settings. Code execution must be on. claude.ai doesn't update uploaded skills, so upload a fresh zip to get new approvals.

### Requirements

- `python3` with `requests` and `pdfplumber`: `pip install -r skills/fl-product-approval/requirements.txt`
- `pdftotext` and `pdftoppm` from poppler-utils

### What an installed copy can do

| | Claude Code | Codex | claude.ai |
| --- | --- | --- | --- |
| Review a project against an ingested approval | Yes | Yes | Yes (with code execution) |
| Invoke by name | `/fl-product-approval:fl-product-approval` | `$fl-product-approval` | Mention it by name |

Both agents also pick the skill up on their own when you mention an FL number or a product series with a Florida approval.

### Your own rules

You can teach the skill your firm's practices, for example "we always use the steel-reinforced mullion above 10 ft". It saves them to `.fl-product-approval/RULES.md` in your project, outside the plugin, so updates never touch them. Commit that file to share the rules with colleagues. Your rules apply on top of the published ones. If one conflicts with a published rule, the skill points out the conflict and you decide.

## Maintain and release (publisher)

Ingesting approvals and teaching rules happen in a clone of this repository, never in an installed copy.

```bash
git clone https://github.com/schultzapps/fl-product-approval-skill.git
cd fl-product-approval-skill
pip install -r requirements.txt
```

Then turn on publisher mode, once per clone:

```bash
touch skills/fl-product-approval/.maintainer
```

The file is git-ignored, so it never reaches customers. Without it, the skill runs in customer mode: it won't ingest approvals, and it saves rules to `.fl-product-approval/RULES.md` instead of the published rule files.

Start Claude Code (`claude`) or Codex (`codex`) in the clone. Both pick the skill up from the clone itself: Claude Code through `.claude/skills/fl-product-approval`, Codex through `.agents/skills/fl-product-approval`. Both links point at `skills/fl-product-approval`, so there is one copy of the data. Then:

- **Ingest a new approval:** "analyze FPA 16517". Ingest needs `tesseract` for scanned approvals and network access to floridabuilding.org. In Codex, allow network for that session: set `network_access = true` under `[sandbox_workspace_write]` in `~/.codex/config.toml`, or approve the command when Codex asks.
- **Teach a rule:** correct the skill or state a practice; it saves the rule to the right `RULES.md`.
- **Update the approvals tables** at the top of this README when you add or revise an approval.
- Review the diff (`NOTES.md`, `components.json`, `RULES.md`) before releasing. Customers will rely on it.

To release:

1. Bump `version` in **both** `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json`, keeping them equal. Installed copies update only when the version changes, so a push without a bump doesn't reach customers.
2. Run `claude plugin validate .` and check that it passes.
3. Commit and push to `main`.

Customers with auto-update get it at their next session start. Others get it when they run the update command.

### Distribution files

| File | Used by |
| --- | --- |
| `.claude-plugin/marketplace.json` | Claude Code marketplace catalog (lists this repo root as the plugin) |
| `.claude-plugin/plugin.json` | Claude Code plugin manifest |
| `.agents/plugins/marketplace.json` | Codex marketplace catalog |
| `.codex-plugin/plugin.json` | Codex plugin manifest |
| `skills/fl-product-approval/SKILL.md` | The skill itself, in the Agent Skills format both agents read |

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
  .maintainer                    # present only in the publisher's clone (git-ignored): turns on publisher mode
.claude/skills/fl-product-approval -> ../../skills/fl-product-approval   # Claude Code, when working in this clone
.agents/skills/fl-product-approval -> ../../skills/fl-product-approval   # Codex, when working in this clone
.claude-plugin/, .codex-plugin/, .agents/plugins/                        # plugin and marketplace manifests
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
