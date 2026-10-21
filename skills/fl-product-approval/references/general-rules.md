# General rules (apply to every product)

Only add rules here when the user says a rule applies to all products and manufacturers. Product-specific rules belong in `data/approvals/FL<n>/RULES.md`, and manufacturer-wide rules belong in `data/manufacturers/<slug>/RULES.md`. See SKILL.md, "Learned rules".

### R-001  No extra safety factor on approval capacities
- Scope: general (all products, all manufacturers)
- Rule: Approval capacities are allowable (ASD) values with the safety factors already built in. A component passes when its tabulated capacity is greater than or equal to the required ASD pressure; for example, 49 psf required against a 50 psf table value passes. Don't apply additional factors, don't call a passing option "tight" or "low margin", and don't recommend a heavier member, glass or anchorage for margin. When several options pass, rank them on what the user asked for (cost, spacing, availability), not on capacity headroom.
- Why / source: user instruction, 2026-10-19 ("safety factors are not at play ... the safety factors are already built in")
- Applies when: always
- Status: active

### R-002  "Comments: Archived" on Florida records is not an issue
- Scope: general (every approval on floridabuilding.org)
- Rule: The "Comments: Archived" value on a product approval detail page does not indicate a problem with the approval or its revision. Don't flag it, don't list it as an open item, and don't ask the user to confirm the revision because of it. The record's Application Status ("Approved") is what matters.
- Why / source: user instruction, 2026-10-20 ("ignore that comments archived thing - not an issue")
- Applies when: always
- Status: active

### R-003  The approval's own documents are the source of truth; KPA001 is only an index
- Scope: general (all approvals; applies to any manufacturer listing such as KPA001)
- Rule: When sources disagree, follow the product approval's own documents: evaluation report, sealed installation drawings and the floridabuilding.org record. KPA001 and other manufacturer directories are maintained by hand and can be wrong or out of date. Use them only to find approvals (series → FL number). Never take a rating, design pressure, glazing or missile level from them when the approval documents say something else. Record the discrepancy in NOTES.md as "KPA001 differs; approval documents govern".
- Why / source: user instruction, 2026-10-20 ("always treat the product approval evaluation as the truth, KPA001 is manually updated and could be wrong")
- Applies when: always
- Status: active

### R-004  LMI (large missile impact) = Level D
- Scope: general (all products, all manufacturers)
- Rule: Where an approval's drawings or evaluation report rate impact as "LMI" (large missile impact) without naming a level, read it as large missile Level D. A product is Level E only where its own documents say Level E. A Level E project can't use an LMI-only product.
- Why / source: user instruction, 2026-10-21 ("LMI is Level D", then confirmed it applies beyond FL47880). Consistent with TAS 201: the 9 lb 2x4 large missile at 50 ft/s is the Level D test; at 80 ft/s it matches Level E (see `references/missile-levels.md`)
- Applies when: setting a product's missile level at ingest, and matching a project's missile level at review
- Status: active
