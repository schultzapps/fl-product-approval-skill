#!/usr/bin/env python3
"""Rebuild data/index.json and answer lookups.

    python3 catalog.py rebuild
    python3 catalog.py show 47012            # one approval (+ KPA001 rows that reference it)
    python3 catalog.py find "IR 521"         # search series / description / manufacturer / category
    python3 catalog.py backlog               # KPA001 approvals not yet ingested
"""
import datetime, json, pathlib, re, sys

HERE = pathlib.Path(__file__).resolve().parent
DATA = HERE.parent / "data"


def base(fpa: str) -> str:
    return re.match(r"\D*(\d+)", fpa).group(1)


def kpa_rows():
    out = []
    for f in sorted((DATA / "kpa").glob("*.json")):
        d = json.loads(f.read_text())
        for r in d["rows"]:
            out.append({**r, "listing": d["document"], "listing_edition": d.get("edition")})
    return out


def rebuild():
    kpa = kpa_rows()
    idx = {"generated": datetime.date.today().isoformat(), "approvals": {}, "by_category": {}, "by_manufacturer": {}, "by_series": {}, "backlog": []}
    for p in sorted((DATA / "approvals").glob("FL*/approval.json")):
        a = json.loads(p.read_text())
        num = p.parent.name
        series = sorted({r["series"] for r in kpa if base(r["fpa"]) == num[2:]} | set(a.get("series", [])))
        has_tables = (p.parent / "components.json").exists()
        idx["approvals"][num] = {
            "fl_number": a.get("fl_number"), "manufacturer": a.get("manufacturer"), "category": a.get("category"),
            "subcategory": a.get("subcategory"), "status": a.get("status"), "code_version": a.get("code_version"),
            "series": series, "ingest_status": a.get("ingest_status"), "has_structured_tables": has_tables,
            "path": f"approvals/{num}"}
        idx["by_category"].setdefault(f"{a.get('category')}/{a.get('subcategory')}", []).append(num)
        idx["by_manufacturer"].setdefault(a.get("manufacturer"), []).append(num)
        for s in series:
            idx["by_series"].setdefault(s, []).append(num)
    have = {n[2:] for n in idx["approvals"]}
    seen = set()
    for r in kpa:
        b = base(r["fpa"])
        if b not in have and (b, r["series"]) not in seen:
            seen.add((b, r["series"]))
            idx["backlog"].append({"fpa": f"FL{b}", "category": r["category"], "series": r["series"], "listing": r["listing"]})
    (DATA / "index.json").write_text(json.dumps(idx, indent=1, ensure_ascii=False) + "\n")
    print(f"index.json: {len(idx['approvals'])} approvals ingested, {len(idx['backlog'])} listed-not-ingested")
    return idx


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "rebuild"
    if cmd == "rebuild":
        rebuild()
    elif cmd == "show":
        n = base(sys.argv[2])
        p = DATA / "approvals" / f"FL{n}" / "approval.json"
        print(p.read_text() if p.exists() else f"FL{n} not ingested - run fpa_fetch.py {n}")
        for r in kpa_rows():
            if base(r["fpa"]) == n:
                print("KPA:", json.dumps(r, ensure_ascii=False))
    elif cmd == "find":
        q = " ".join(sys.argv[2:]).lower()
        idx = json.loads((DATA / "index.json").read_text())
        for n, a in idx["approvals"].items():
            if q in json.dumps(a).lower():
                print("ingested:", n, a["manufacturer"], a["category"], a["subcategory"], a["series"])
        for b in idx["backlog"]:
            if q in json.dumps(b).lower():
                print("backlog: ", b["fpa"], b["category"], b["series"])
    elif cmd == "backlog":
        for b in json.loads((DATA / "index.json").read_text())["backlog"]:
            print(b["fpa"], b["category"], "|", b["series"])


if __name__ == "__main__":
    main()
