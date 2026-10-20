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
