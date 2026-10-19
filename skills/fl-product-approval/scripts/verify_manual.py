#!/usr/bin/env python3
"""Cross-check hand-transcribed tables in components.json against the PDF text layer.

    python3 verify_manual.py 47012

Detail tables (head/sill/intermediate horizontal): the row's  <detail id> <values...>  token run must appear on a text line of the sheet.
Glass capacity rows: width, [height], location, sealant, direction and the six G-A..G-F cells must appear as one line.
Prints every row that cannot be found; exit code 1 if any.
"""
import json, pathlib, re, sys
import pdfplumber

HERE = pathlib.Path(__file__).resolve().parent
SKILL = HERE.parent
REPO = SKILL.parent.parent


def fmt(v):
    return "-" if v is None else (f"{v:.1f}" if isinstance(v, float) or True else str(v))


def lines_of(page):
    ws = page.extract_words()
    ws.sort(key=lambda w: (round(w["top"] / 3), w["x0"]))
    out, cur, key = [], [], None
    for w in ws:
        k = round(w["top"] / 3)
        if key is not None and abs(k - key) > 1:
            out.append(cur); cur = []
        cur.append(w["text"]); key = k
    if cur: out.append(cur)
    return out


def has_run(lines, run):
    n = len(run)
    return any(any(L[i:i + n] == run for i in range(len(L) - n + 1)) for L in lines)


def main():
    num = "".join(ch for ch in sys.argv[1] if ch.isdigit())
    adir = SKILL / "data" / "approvals" / f"FL{num}"
    comp = json.loads((adir / "components.json").read_text())
    app = json.loads((adir / "approval.json").read_text())
    doc = next(d for d in app["documents"] if d["role"] == "installation_instructions")
    pdf = pdfplumber.open(str(REPO / doc["cache_path"]))
    bad = checked = 0
    tabs = {t["id"]: t for t in comp["tables"]}
    for t in comp["tables"]:
        if t.get("kind") != "detail":
            continue
        L = lines_of(pdf.pages[t["sheet"] - 1])
        # sill / intermediate-horizontal sheets print field and pre-glazed cells on one line: id f1 f2 f3 p1 p2
        field_t = tabs.get(t["id"].replace("-pre", "-field")) if t["id"].endswith("-pre") else None
        pre_t = tabs.get(t["id"].replace("-field", "-pre")) if t["id"].endswith("-field") else None
        field_t = field_t if field_t and field_t["sheet"] == t["sheet"] else None
        pre_t = pre_t if pre_t and pre_t["sheet"] == t["sheet"] else None
        for r in t["rows"]:
            vals = [fmt(float(v)) if v is not None else "-" for v in r["capacity_psf"]]
            checked += 1
            if field_t is not None:
                f = next((x for x in field_t["rows"] if x["detail"] == r["detail"]), None)
                run = [r["detail"]] + ([fmt(float(v)) if v is not None else "-" for v in f["capacity_psf"]] if f else []) + vals
                ok = f is not None and has_run(L, run)
            elif pre_t is not None:
                p = next((x for x in pre_t["rows"] if x["detail"] == r["detail"]), None)
                run = [r["detail"]] + vals + ([fmt(float(v)) if v is not None else "-" for v in p["capacity_psf"]] if p else [])
                ok = has_run(L, run) or has_run(L, [r["detail"]] + vals)   # Level E rows may omit the pre half
            else:
                run = [r["detail"]] + vals
                ok = has_run(L, run)
            if not ok:
                bad += 1; print("NOT FOUND", t["id"], r["detail"], vals)
    g = comp.get("glass_capacity", [])
    gl = lines_of(pdf.pages[3])
    for r in g:
        cells = [fmt(float(r["capacity_psf"].get("G-" + k))) if ("G-" + k) in r["capacity_psf"] else "-" for k in "ABCDEF"]
        seal = " ".join(f"{s} or" if i < len(r["sealant"]) - 1 else s for i, s in enumerate(r["sealant"])).split()
        dirs = " ".join(f"{s} or" if i < len(r["direction"]) - 1 else s for i, s in enumerate(r["direction"])).split()
        w = f"{r['max_dlo_width_in']:g}"
        loc = "Field" if r["location"] == "field" else "Pre"
        checked += 1
        found = False
        for L in gl:
            s = " ".join(L)
            pat = rf"(^| ){re.escape(w)}( [\d.]+)? {loc} {re.escape(' '.join(seal))} {re.escape(' '.join(dirs))} " + " ".join(re.escape(c if c == '-' else c.rstrip('0').rstrip('.')) for c in cells)
            if re.search(pat, s):
                found = True; break
        if not found:
            bad += 1; print("NOT FOUND glass", r)
    print(f"checked {checked} hand-entered rows, {bad} not found in the PDF text layer")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
