#!/usr/bin/env python3
"""Parse a manufacturer product-approval listing (Kawneer KPA001) into data/kpa/<name>.json.

    python3 kpa_parse.py                      # downloads KPA001 from kawneer.com
    python3 kpa_parse.py path/to/KPA001.pdf
"""
import json, pathlib, re, sys, datetime, hashlib
import pdfplumber, requests

HERE = pathlib.Path(__file__).resolve().parent
SKILL = HERE.parent
REPO = SKILL.parent.parent
URL = "https://www.kawneer.com/kawneer_files/shared%20files/Performance_Solutions/KPA001.pdf"


# column left edges (pt) = the vertical rules of the KPA001 table; band() uses the rule positions found on each page
NAMES = ["category", "series", "missile_rating", "description", "kawneer_test_reports", "fpa", "tdi", "design_pressure", "glazing", "wet_dry", "notes"]
DEFAULT_EDGES = [36, 132, 231, 291, 426, 513, 594, 657, 720, 820, 878, 972]
BANDS = list(zip(NAMES, DEFAULT_EDGES))
FPA = re.compile(r"^\d{4,5}(\.\d+)?$")


def page_bands(page):
    xs = sorted({round(e["x0"]) for e in page.edges if e["orientation"] == "v" and abs(e["x0"] - e["x1"]) < 1 and e["bottom"] - e["top"] > 20})
    return list(zip(NAMES, xs[:len(NAMES)])) if len(xs) >= len(NAMES) + 1 else BANDS


def band(x, bands):
    name = bands[0][0]
    for n, x0 in bands:
        if x >= x0 - 1:
            name = n
    return name


def parse_page(page, pno):
    ws = [w for w in page.extract_words() if 118 < w["top"] < 555]
    bands = page_bands(page)
    anchors = [w for w in ws if band(w["x0"], bands) == "fpa" and FPA.match(w["text"])]
    if not anchors:
        return []
    rows = [{"y": (a["top"] + a["bottom"]) / 2, "fpa": a["text"], "cells": {n: [] for n, _ in bands}} for a in anchors]
    for w in ws:
        cy = (w["top"] + w["bottom"]) / 2
        r = min(rows, key=lambda r: abs(r["y"] - cy))
        r["cells"][band(w["x0"], bands)].append(w)
    out = []
    for r in rows:
        row = {}
        for n, _ in bands:
            toks = sorted(r["cells"][n], key=lambda w: (round(w["top"] / 4), w["x0"]))
            row[n] = re.sub(r"\s+", " ", " ".join(w["text"] for w in toks)).strip()
        row["page"] = pno
        out.append(row)
    return out


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else None
    if src is None:
        dest = REPO / "cache" / "KPA001.pdf"; dest.parent.mkdir(exist_ok=True)
        dest.write_bytes(requests.get(URL, timeout=120).content); src = str(dest)
    raw = pathlib.Path(src).read_bytes()
    rows, edition = [], None
    with pdfplumber.open(src) as pdf:
        for pno, page in enumerate(pdf.pages, 1):
            m = re.search(r"KPA001\s+([A-Za-z]+ \d{4})", page.extract_text() or "")
            edition = edition or (m.group(1) if m else None)
            rows += parse_page(page, pno)
    out = {"document": "KPA001", "edition": edition, "source_url": URL, "sha256": hashlib.sha256(raw).hexdigest(),
           "parsed": datetime.date.today().isoformat(), "row_count": len(rows),
           "caveat": "Manufacturer listing; can lag the live Florida record (revisions, added missile levels). Always confirm on floridabuilding.org.",
           "rows": rows}
    dest = SKILL / "data" / "kpa" / "KPA001.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    print(f"{len(rows)} rows, edition {edition} -> {dest.relative_to(REPO)}")


if __name__ == "__main__":
    main()
