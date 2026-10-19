# `components.json` schema

Top level: `approval`, `revision`, `drawing_no`, `source_document`, `value_semantics`, `tables[]`, `rules{}`, `glazing_schedule{}`, `glazing_type_schedule{}`, `glass_capacity[]`, `installation_anchors[]`, `door_assemblies{}`.

## Grid table (`kind: "grid"`)

```json
{"id": "mullion-shallow-LD-field", "component": "mullion", "family": "Mullions w/ Shallow Pocket Fillers", "sheet": 7,
 "applies": {"missile": ["A","D"], "glazing": ["field"]},
 "x_axis": "tributary_width_in", "y_axis": "mullion_height_in",
 "columns": [{"id": "nosteel_NT", "thermal": "NT", "steel": false, "label": "No Steel M1/M2/M3"}, ...],
 "variants": [{"id": "M1", "thermal": ["NT"], "steel": false, "width_in": 2.5}, ...],
 "blocks": [{"y": 96, "rows": [{"x": 30, "v": [70, 70, 70, 90, 90, 90]}, ...]}, ...]}
```

`component` is one of `mullion`, `corner_mullion`, `jamb` or `head_sill_anchor_cluster`. In anchor-cluster tables, the first column is `midspan_clusters` (how many are required) and the remaining columns are `end_<n>` (capacity with n anchors per end cluster), and `applies.shim_gap_in` holds the maximum shim gap.

## Detail table (`kind: "detail"`)

```json
{"id": "head-LD-field", "component": "head", "sheet": 16, "applies": {...}, "dlo_widths_in": [33.5, 57.5, 69.5],
 "rows": [{"detail": "H1", "thermal": ["NT"], "capacity_psf": [90, 90, 90]}]}
```

`component` is one of `head`, `sill` or `intermediate_horizontal`.

## Glass capacity row

```json
{"location": "field", "max_dlo_width_in": 33.5, "max_dlo_height_in": 97, "sealant": ["WG-D","WG-G"], "direction": ["OG","IG"], "capacity_psf": {"G-C": 90, "G-D": 90}}
```

## Rules

`rules.missile_to_glazing` maps a missile level to its allowed glazing schedules. The `rules` object also holds the governing rule, pressure basis, tributary-width formula, general notes and evaluation-report limits, all as text quoted or paraphrased from the documents with the sheet or note number.

All capacities are ASD PSF applying to both positive and negative pressure, and `null` means not permitted.
