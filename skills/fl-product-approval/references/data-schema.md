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

## Multi-product approvals

```
data/approvals/FL15404/
  approval.json                        # record; products[] each list their own documents
  NOTES.md, RULES.md
  common/components.json               # tables shared by several sub-products
  products/FL15404.1/components.json   # {"product": "FL15404.1", "extends": "../../common/components.json", "missile": "D", "glazing_method": "wet", "glass": [...], ...}
  products/FL15404.4/components.json   # standalone (no "extends") when the sub-product is a different system
```

When a product file has `extends`, `check_config.py` merges it over the shared file:
- `tables` are concatenated;
- dicts such as `rules` are merged one level deep;
- other keys are replaced.

Product-level keys:
- `product`, `drawing`, `evaluation_report`;
- `missile` (the product's rating, a level or a list of levels such as `["D", "A"]`; the checker flags a project level not in it);
- `glazing_method`, `glass[]` (approved make-ups), `glazing`, `warnings[]`.

## Door rating tables (FL47880 style)

Door-only products put their tables in `door_ratings.tables[]`, with no `tables` key. Each table is one component (`door_lock`, `door_glass`, `door_hinge` or `door_assembly`), and the least passing capacity across components governs.

```json
{"id": "lock", "component": "door_lock", "sheet": 1, "title": "Design Pressure Rating - Lock",
 "rows": [{"option": "Jackson 2086", "max_leaf_w_in": 48, "max_leaf_h_in": 96, "dp_psf": 90}]}
```

- **Size limits** (any subset): `max_leaf_w_in`, `max_leaf_h_in`, `max_opening_w_in`, `max_opening_h_in`, `max_frame_w_in`, `max_frame_h_in`. Glass tables may use `max_leaf_w_single_in` / `max_opening_w_double_in`.
- **Row filters:** `config` (`X`, `XX`, `XXX`), `frame_types`, `door_series`, `missile`, `lock_options`, `glass_options`, `hinges`, `wind_zone`.
- **Values:** `dp_psf` is +/- ASD psf; `null` means N/A on the drawing.
- **Other product keys:** `hvhz`, `max_wind_zone_unprotected` (WZ3 products), `missile_rating` (text), `door_legend` (frame → door opening → D.L.O. deductions), `lock_options`, `glass[]`, `installation_anchors[]`, `anchor_layouts[]`.

## Frame-height tables and glass size limits (FL15404 style)

- **Axes:** grid tables may set `"y_axis": "frame_height_in"` and `"x_axis": "load_width_in"`. The checker reads `frame_height_in` from the opening. Load width uses `tributary_width_in` for intermediate mullions, `jamb_tributary_width_in` for jambs and `corner_load_width_in` for corners.
- **Anchor columns:** columns can be end-anchor quantities, e.g. `{"id": "anchors_6", "end_anchors": 6}`.
- **`dlo_limits`:** `[{"max_dlo_height_in": 108, "max_dlo_width_in": 46.5}, ...]` is used where an approval has no glass pressure table. The DLO height rounds up to the next row, which gives the maximum DLO width. Glass then passes at the product's `rules.max_pressure_psf`, because pressure is governed by the framing.
- **Product limits:** `rules.max_pressure_psf` and `rules.max_frame_height_in` are the product caps; the checker flags any exceedance.
- **`project_out_windows`:** `{max_frame_height_in, max_opening_height_in, max_dlo_width_in, max_dlo_height_in, glass}` for operable inserts.
- **Missing members:** members a product doesn't tabulate (head, sill or anchor clusters in FL15404) are reported as "not tabulated", not as failures.
