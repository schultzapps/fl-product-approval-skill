#!/usr/bin/env python3
"""Fetch a Florida Product Approval record by FL number and store it under data/approvals/FL<number>/.

    python3 fpa_fetch.py 47012            # latest revision found by the search
    python3 fpa_fetch.py FL16517 --rev 7  # specific revision (if the search lists it)

Steps: search form (floridabuilding.org) -> list page -> detail page -> download the linked PDFs into
<repo>/cache/FL<number>/ (git-ignored) -> write data/approvals/FL<number>/approval.json -> rebuild data/index.json.
"""
import argparse, datetime, hashlib, html, json, pathlib, re, sys
import requests

BASE = "https://www.floridabuilding.org/pr/"
HERE = pathlib.Path(__file__).resolve().parent
SKILL = HERE.parent
REPO = SKILL.parent.parent
DATA = SKILL / "data"
CACHE = REPO / "cache"
UA = {"User-Agent": "fl-product-approval-skill/0.1 (+research; contact repo owner)"}


def norm_number(s: str) -> str:
    m = re.search(r"(\d{3,6})", s)
    if not m:
        sys.exit(f"cannot read an FPA number from {s!r}")
    return m.group(1)


def hidden_fields(t: str) -> dict:
    return {m.group(1): html.unescape(m.group(2))
            for m in re.finditer(r'<input type="hidden" name="(__[A-Z0-9]+)" id="[^"]*" value="([^"]*)"', t)}


def search(num: str):
    s = requests.Session(); s.headers.update(UA)
    r = s.get(BASE + "pr_app_srch.aspx", timeout=60); r.raise_for_status()
    data = hidden_fields(r.text)
    data.update({"__EVENTTARGET": "lnkSearch", "__EVENTARGUMENT": "", "txtAppNum:txtTextbox": num, "rbGenOutPut": "1"})
    r2 = s.post(BASE + "pr_app_srch.aspx", data=data, timeout=120); r2.raise_for_status()
    t = re.sub(r"<script.*?</script>", "", r2.text, flags=re.S)
    found = []
    for href, label in re.findall(r"href=['\"]([^'\"]*pr_app_dtl\.aspx\?param=[^'\"]+)['\"][^>]*>(.*?)</a>", t, flags=re.S):
        label = re.sub(r"<[^>]+>", "", label).strip()
        m = re.match(r"FL(\d+)(?:-R(\d+))?$", label)  # original applications have no -R suffix
        if m and m.group(1) == num:
            found.append({"fl": label, "rev": int(m.group(2) or 0), "url": requests.compat.urljoin(BASE, href)})
    return s, found


def lines_of(page_html: str):
    t = re.sub(r"<script.*?</script>|<style.*?</style>", "", page_html, flags=re.S)
    t = re.sub(r"<[^>]+>", "\n", t)
    t = html.unescape(t)
    return [l.strip() for l in t.splitlines() if l.strip()]


def after(lines, label, n=1, start=0):
    for i in range(start, len(lines)):
        if lines[i] == label:
            return lines[i + 1:i + 1 + n]
    return []


def parse_detail(page_html: str) -> dict:
    L = lines_of(page_html)
    d = {
        "fl_number": (after(L, "FL #") or [None])[0],
        "application_type": (after(L, "Application Type") or [None])[0],
        "code_version": (after(L, "Code Version") or [None])[0],
        "status": (after(L, "Application Status") or [None])[0],
        "status_comments": (after(L, "Comments") or [None])[0],
        "manufacturer": (after(L, "Product Manufacturer") or [None])[0],
        "category": (after(L, "Category") or [None])[0],
        "subcategory": (after(L, "Subcategory") or [None])[0],
        "compliance_method": (after(L, "Compliance Method") or [None])[0],
        "approval_method": (after(L, "Product Approval Method") or [None])[0],
        "dates": {k: (after(L, lab) or [None])[0] for k, lab in [
            ("submitted", "Date Submitted"), ("validated", "Date Validated"),
            ("pending_fbc", "Date Pending FBC Approval"), ("approved", "Date Approved")]},
        "quality_assurance_entity": (after(L, "Quality Assurance Entity") or [None])[0],
        "quality_assurance_expires": (after(L, "Date", 1) or [None])[0] if "Quality Assurance Contract Expiration" in L else None,
    }
    # engineer / architect of record
    i = next((k for k, l in enumerate(L) if l.startswith("Florida Engineer or Architect Name")), None)
    if i is not None:
        d["evaluator"] = {"name": L[i + 2] if L[i + 1] == "Evaluation Report" else L[i + 1]}
        lic = after(L, "Florida License")
        d["evaluator"]["license"] = lic[0] if lic else None
    # referenced standards
    i = next((k for k, l in enumerate(L) if l == "Year"), None)
    std = []
    if i is not None:
        j = i + 1
        while j + 1 < len(L) and re.match(r"^\d{4}$", L[j + 1]):
            std.append({"standard": L[j], "year": L[j + 1]}); j += 2
    d["referenced_standards"] = std
    # summary of products + limits of use
    products = []
    i = next((k for k, l in enumerate(L) if l == "Summary of Products"), None)
    if i is not None:
        j = i + 1
        if L[j:j + 3] == ["FL #", "Model, Number or Name", "Description"]:
            j += 3
        while j < len(L) and re.match(r"^\d+\.\d+$", L[j]):
            p = {"fl": "FL" + L[j], "model": L[j + 1], "description": L[j + 2]}
            j += 3
            lim = {}
            labs = [("hvhz", "Approved for use in HVHZ:"), ("outside_hvhz", "Approved for use outside HVHZ:"),
                    ("impact_resistant", "Impact Resistant:"), ("design_pressure", "Design Pressure:"), ("other", "Other:")]
            while j < len(L) and L[j] != "Limits of Use":
                j += 1
            j += 1
            while j < len(L):
                hit = next(((k, lab) for k, lab in labs if L[j] == lab), None)
                if not hit:
                    break
                lim[hit[0]] = L[j + 1]; j += 2
            p["limits_of_use"] = lim
            # this product's own documents, listed before the next product number
            p["documents"] = []
            while j < len(L) and not re.match(r"^\d+\.\d+$", L[j]) and L[j] not in ("Back", "Next"):
                if L[j].lower().endswith(".pdf"):
                    p["documents"].append(L[j])
                j += 1
            products.append(p)
    d["products"] = products
    # documents
    docs = []
    for href, text in re.findall(r"href=['\"](\.\./upload/[^'\"]+\.pdf)['\"][^>]*>(.*?)</a>", page_html, flags=re.S | re.I):
        role = ("installation_instructions" if "PR_Instl_Docs" in href else "evaluation_report" if "PR_Tech_Docs" in href
                else "certificate_of_independence" if "PR_Independence" in href else "other")
        fname = html.unescape(href.rsplit("/", 1)[-1])
        owner = [p["fl"] for p in products if fname in p.get("documents", [])]
        docs.append({"role": role, "file": fname, "url": requests.compat.urljoin(BASE, href), "products": owner})
    d["documents"] = docs
    return d


def download(session, url, dest: pathlib.Path):
    dest.parent.mkdir(parents=True, exist_ok=True)
    r = session.get(url, timeout=300); r.raise_for_status()
    dest.write_bytes(r.content)
    return hashlib.sha256(r.content).hexdigest(), len(r.content)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("number"); ap.add_argument("--rev", type=int)
    ap.add_argument("--no-download", action="store_true")
    a = ap.parse_args()
    num = norm_number(a.number)
    s, found = search(num)
    if not found:
        sys.exit(f"no FL{num} record found")
    print("revisions listed:", ", ".join(f["fl"] for f in found))
    pick = next((f for f in found if f["rev"] == a.rev), None) if a.rev is not None else max(found, key=lambda f: f["rev"])
    if not pick:
        sys.exit(f"revision {a.rev} not listed")
    r = s.get(pick["url"], timeout=120); r.raise_for_status()
    rec = parse_detail(r.text)
    rec["source"] = {"detail_page": pick["url"], "retrieved": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
                     "note": "Revision shown is the one the search returned; confirm it is the current approved revision on floridabuilding.org before relying on it."}
    out = DATA / "approvals" / f"FL{num}"
    out.mkdir(parents=True, exist_ok=True)
    if not a.no_download:
        for doc in rec["documents"]:
            dest = CACHE / f"FL{num}" / doc["file"]
            doc["sha256"], doc["bytes"] = download(s, doc["url"], dest)
            doc["cache_path"] = str(dest.relative_to(REPO))
            print("downloaded", doc["role"], doc["file"], doc["bytes"], "bytes")
    # keep hand-curated fields from a previous run
    prev = out / "approval.json"
    if prev.exists():
        old = json.loads(prev.read_text())
        for k in ("series", "kpa001", "ingest_status"):
            if k in old:
                rec[k] = old[k]
    rec.setdefault("ingest_status", "fetched")
    prev.write_text(json.dumps(rec, indent=2, ensure_ascii=False) + "\n")
    print("wrote", prev.relative_to(REPO))
    sys.path.insert(0, str(HERE))
    import catalog
    catalog.rebuild()


if __name__ == "__main__":
    main()
