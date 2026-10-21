#!/usr/bin/env python3
"""Turn an approval's extract_spec.json + its installation-instruction PDF into components.json.

    python3 extract_tables.py 47012            # uses cache/FL47012/<installation PDF> (run fpa_fetch.py first)
    python3 extract_tables.py 47012 --pdf some.pdf

extract_spec.json (hand-curated per approval) lists
  tables:        grid tables parsed from the PDF by panel_parse (page, panel indexes, value-column count, column ids, applicability)
  manual_tables: detail tables transcribed by hand (head/sill/intermediate horizontal ...)
  manual:        everything else (rules, glazing schedule, glass capacity, anchors, doors)
Validation is strict: every height block must get exactly one height label, widths must increase inside a block,
heights must ascend, and any row with the wrong number of value cells aborts the run.
"""
import argparse, json, pathlib, sys
import pdfplumber

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import panel_parse as pp

SKILL = HERE.parent
ROOT = SKILL  # cache/ lives in the skill dir so paths hold wherever the skill is installed


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("number"); ap.add_argument("--pdf")
    a = ap.parse_args()
    num = "".join(ch for ch in a.number if ch.isdigit())
    adir = SKILL / "data" / "approvals" / f"FL{num}"
    spec = json.loads((adir / "extract_spec.json").read_text())
    approval = json.loads((adir / "approval.json").read_text())
    pdf_path = a.pdf
    if not pdf_path:
        doc = next(d for d in approval["documents"] if d["role"] == spec["pdf_role"])
        pdf_path = ROOT / doc["cache_path"]
        if not pdf_path.exists():
            sys.exit(f"{pdf_path} missing - run: python3 scripts/fpa_fetch.py {num}")
    pdf = pdfplumber.open(str(pdf_path))
    cache, tables, problems = {}, [], []
    for t in spec["tables"]:
        page = pdf.pages[t["page"] - 1]
        if t["page"] not in cache:
            ws = page.extract_words(); cache[t["page"]] = (ws, pp.panels(ws))
        ws, pans = cache[t["page"]]
        blocks = []
        for pi in t["panels"]:
            x0, x1 = pans[pi]
            blocks += pp.parse_panel(ws, x0, x1, t["ncols"])
        heights = [b["height"] for b in blocks]
        if heights != sorted(heights) or len(set(heights)) != len(heights):
            problems.append(f"{t['id']}: heights not strictly ascending {heights}")
        for b in blocks:
            w = [r["width"] for r in b["rows"]]
            if w != sorted(w) or len(set(w)) != len(w):
                problems.append(f"{t['id']}: widths not increasing in height block {b['height']}: {w}")
        out = {k: v for k, v in t.items() if k not in ("page", "panels", "ncols")}
        out["kind"] = "grid"
        out["blocks"] = [{"y": b["height"], "rows": [{"x": r["width"], "v": r["vals"]} for r in b["rows"]]} for b in blocks]
        tables.append(out)
        print(f"{t['id']:40s} sheet {t['sheet']:>2}  heights {heights[0]:g}-{heights[-1]:g}  rows {sum(len(b['rows']) for b in blocks)}")
    tables += spec.get("manual_tables", [])
    comp = {"approval": f"FL{num}", "revision": approval["fl_number"], "drawing_no": spec.get("drawing_no"),
            "source_document": pathlib.Path(pdf_path).name, "axes": {"x": "tributary width (in)", "y": "mullion height (in)"},
            "value_semantics": "allowable ASD pressure in PSF, applies to both Ext.(+) and Int.(-); null = combination not permitted (shown as '-' on the sheet)",
            "tables": tables, **spec.get("manual", {})}
    (adir / "components.json").write_text(json.dumps(comp, indent=1) + "\n")
    if problems:
        print("\nVALIDATION PROBLEMS:\n  " + "\n  ".join(problems)); sys.exit(1)
    print(f"\nwrote {(adir / 'components.json').relative_to(ROOT)}  ({len(tables)} tables) - validation OK")


if __name__ == "__main__":
    main()
