# Review method (what `check_config.py` does and how to explain it)

**Required pressure.** The script uses max(|positive|, |negative|). If the input basis is "strength", it multiplies by 0.6 to get ASD. All approval capacities are ASD and apply to both positive and negative pressure. A per-opening `pressure_psf_asd` overrides the project value.

**Lookups.** Tables give maximum tributary width, maximum mullion height and maximum DLO. Each input is rounded **up** to the next tabulated value, and the script never interpolates. A "-" on the sheet (`null` in the data) means the combination is not approved. Inputs beyond the largest tabulated value are reported as outside the range, with the limit that was hit.

**Applicability.** A table is used only if its `applies.missile` contains the project's missile level and its `applies.glazing` contains the glazing mode. Columns are filtered by thermal type. A table whose glazing mode is not stated on the sheet is used but flagged.

**Glass.** Rows are filtered by location (field/pre), by DLO fitting inside the row's max width and height, and by glazing schedules allowed for the missile level. For each schedule/sealant/direction combination the tightest size class that covers the DLO is used.

**Anchorage.** The head/sill anchor-cluster table gives the capacity for each number of anchors per end cluster. It also gives how many midspan clusters are required. Anchor type, embedment and edge distance come from Table 1 for the substrate.

**System capacity.** Pick one passing option per component. The system capacity is the **least** of them (approval sheet 1 note). The design is acceptable when that least capacity is at least the required ASD pressure.

**What to tell the user.** For each component, give the passing options, best first, with capacity, margin and sheet. Show what governs. When nothing passes, say why and suggest changes, such as reducing the bay width (lowers tributary width), adding steel or switching to a 5" mullion, adding anchors per cluster, reducing the shim gap, or changing the glazing schedule or sealant. Repeat any flags (record status, QA expiry, discrepancies with KPA001). Close with the limits: no water-infiltration scope, substrate by others, and the engineer of record decides.
