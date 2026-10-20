#!/usr/bin/env python3
"""Review project requirements against an ingested Florida Product Approval and list the configurations that pass.

    python3 check_config.py project.json            # Markdown report
    python3 check_config.py project.json --json     # machine-readable

See references/project-intake.md for the project.json format and references/review-method.md for the rules used.
Everything here is a screening aid: capacities come from components.json (transcribed from the sealed approval drawing),
and the report restates the assumptions. The engineer/architect of record decides what is acceptable.
"""
import argparse, json, pathlib, re, sys

HERE = pathlib.Path(__file__).resolve().parent
DATA = HERE.parent / "data"
ASD_FACTOR = 0.6   # ASCE 7 strength-level C&C pressure -> ASD (0.6W)


def merge(base, prod):
    """Product data over shared data: tables are concatenated, dicts merged one level deep, everything else replaced."""
    out = dict(base)
    for k, v in prod.items():
        if k == "tables":
            out[k] = base.get(k, []) + v
        elif isinstance(v, dict) and isinstance(base.get(k), dict):
            out[k] = {**base[k], **v}
        else:
            out[k] = v
    return out


def load(ref):
    """ref: 'FL47012', '47012', 'FL15404.1' or '15404.1'. Multi-product approvals keep shared data in common/ and each
    product's own data in products/FL<n>.<k>/ (its components.json may 'extends' the shared file)."""
    m = re.match(r"\D*(\d+)(?:\.(\d+))?", str(ref))
    num, sub = m.group(1), m.group(2)
    d = DATA / "approvals" / f"FL{num}"
    if not (d / "approval.json").exists():
        sys.exit(f"FL{num}: not ingested - see references/ingest-workflow.md")
    app = json.loads((d / "approval.json").read_text())
    pdir = d / "products"
    if pdir.exists():
        prods = sorted(x.name for x in pdir.iterdir() if (x / "components.json").exists())
        want = f"FL{num}.{sub}" if sub else (prods[0] if len(prods) == 1 else None)
        if want not in prods:
            listing = "\n".join(f"  {p['fl']}: {p['description']}" for p in app.get("products", []))
            sys.exit(f"FL{num} has several products - set \"approval\" to one of them:\n{listing}")
        f = pdir / want / "components.json"
        comp = json.loads(f.read_text())
        if comp.get("extends"):
            comp = merge(json.loads((f.parent / comp["extends"]).resolve().read_text()), comp)
        comp["product"] = want
        return app, comp
    if not (d / "components.json").exists():
        sys.exit(f"FL{num}: no components.json - ingest it first (see references/ingest-workflow.md)")
    return app, json.loads((d / "components.json").read_text())


def yval(t, o):
    """The table's vertical axis: mullion height (default) or frame height."""
    key = t.get("y_axis", "mullion_height_in")
    if key == "mullion_height_in":
        return o.get("mullion_height_in")
    return o.get(key)


def xval(t, o):
    """The table's horizontal axis for this member."""
    if t["component"] == "jamb":
        # a jamb carries half of its single adjacent bay; default to half the typical tributary width (end bay = typical bay)
        return o.get("jamb_tributary_width_in", o["tributary_width_in"] / 2)
    if t["component"] == "corner_mullion" and "corner_load_width_in" in o:
        return o["corner_load_width_in"]
    return o["tributary_width_in"]


def applies(t, missile, mode):
    a = t.get("applies", {})
    if missile and missile not in a.get("missile", [missile]):
        return False, None
    g = a.get("glazing")
    if g is None:
        return True, "glazing mode not stated on the sheet" if t["component"] == "mullion" and t["id"].endswith("-E") else None
    return (mode in g if mode else True), None


def grid_lookup(t, x, y):
    """Round both axes UP to the next tabulated value (tables list maxima). Returns (block_y, row_x, values) or None."""
    blk = next((b for b in sorted(t["blocks"], key=lambda b: b["y"]) if b["y"] >= y), None)
    if not blk:
        return None
    row = next((r for r in sorted(blk["rows"], key=lambda r: r["x"]) if r["x"] >= x), None)
    return (blk["y"], row["x"], row["v"]) if row else None


def range_note(t, x, y):
    hname = t.get("y_axis", "mullion_height_in").replace("_in", "").replace("_", " ")
    wname = t.get("x_axis", "tributary_width_in").replace("_in", "").replace("_", " ")
    blk = next((b for b in sorted(t["blocks"], key=lambda b: b["y"]) if b["y"] >= y), None)
    if not blk:
        return f"{hname} {y:g} exceeds table max {max(b['y'] for b in t['blocks']):g}"
    return f"at {hname} {blk['y']:g} the table stops at {wname} {max(r['x'] for r in blk['rows']):g} (need {x:g})"


def thermal_ok(col_thermal, want):
    return not want or col_thermal in (None, want)


def opt(component, name, cap, req, **extra):
    return {"component": component, "option": name, "capacity_psf": cap, "required_psf": req, "pass": cap is not None and cap >= req, **extra}


def eval_mullions(comp, o, req, missile, mode, thermal, kinds):
    out, notes = [], []
    for t in comp["tables"]:
        if t.get("kind") != "grid" or t["component"] not in kinds:
            continue
        ok, warn = applies(t, missile, mode)
        if not ok:
            continue
        x, y = xval(t, o), yval(t, o)
        if y is None:
            out.append(opt(t["component"], f"{t['family']} [{t['id']}]", None, req, note=f"input '{t.get('y_axis')}' is required for this table"))
            continue
        hit = grid_lookup(t, x, y)
        if hit is None:
            out.append(opt(t["component"], f"{t['family']} [{t['id']}]", None, req, note=range_note(t, x, y)))
            continue
        by, rx, vals = hit
        for c, v in zip(t["columns"], vals):
            if not thermal_ok(c.get("thermal"), thermal):
                continue
            vid = [x["id"] for x in t.get("variants", []) if x.get("steel") in (None, c.get("steel")) and c.get("thermal") in x.get("thermal", [c.get("thermal")])] if c.get("steel") is not None else []
            tag = f" -> {'/'.join(vid)}" if vid else ""
            out.append(opt(t["component"], f"{t['family']} - {c.get('label') or c['id']} ({c['id']}{tag})", v, req, table=t["id"], sheet=t["sheet"],
                           looked_up=f"width {rx:g} / height {by:g}", **({"warning": warn} if warn else {}), **({"note": t["notes"]} if t.get("notes") else {})))
    return out


def eval_details(comp, o, req, missile, mode, thermal, comp_name):
    out = []
    for t in comp["tables"]:
        if t.get("kind") != "detail" or t["component"] != comp_name:
            continue
        ok, _ = applies(t, missile, mode)
        if not ok:
            continue
        w = o["dlo_width_in"]
        idx = next((i for i, c in enumerate(t["dlo_widths_in"]) if c >= w), None)
        for r in t["rows"]:
            if thermal and thermal not in r["thermal"]:
                continue
            cap = r["capacity_psf"][idx] if idx is not None else None
            out.append(opt(comp_name, f"{r['detail']} ({'/'.join(r['thermal'])})", cap, req, table=t["id"], sheet=t["sheet"],
                           looked_up=f"DLO {t['dlo_widths_in'][idx]:g}" if idx is not None else f"DLO {w:g} exceeds table max {t['dlo_widths_in'][-1]:g}"))
    return out


def eval_glass_dlo(comp, o, req):
    """Approvals without glass pressure tables: glass is limited by a D.L.O. size table (max width for a given max height)."""
    h, w = o["dlo_height_in"], o["dlo_width_in"]
    row = next((r for r in sorted(comp["dlo_limits"], key=lambda r: r["max_dlo_height_in"]) if r["max_dlo_height_in"] >= h), None)
    cap = comp["rules"].get("max_pressure_psf")
    builds = "; ".join(f"{g['id']}: {g['build']}" for g in comp.get("glass", []))
    if row is None:
        return [opt("glass", "DLO size table", None, req, note=f"DLO height {h:g} exceeds table max {max(r['max_dlo_height_in'] for r in comp['dlo_limits']):g}")]
    fits = w <= row["max_dlo_width_in"]
    return [opt("glass", "approved glass per this product", cap if fits else None, req, sheet=1,
                size_class=f"DLO height up to {row['max_dlo_height_in']:g} allows width up to {row['max_dlo_width_in']:g} (have {w:g} x {h:g})",
                note="pressure governed by the framing tables" if fits else "DLO too wide for this height", build=builds)]


def eval_glass(comp, o, req, missile, mode, want):
    if "glass_capacity" not in comp and "dlo_limits" in comp:
        return eval_glass_dlo(comp, o, req)
    allowed = comp["rules"]["missile_to_glazing"].get(missile, [])
    best = {}
    for r in comp["glass_capacity"]:
        if mode and r["location"] != mode:
            continue
        if o["dlo_width_in"] > r["max_dlo_width_in"] or o["dlo_height_in"] > r["max_dlo_height_in"]:
            continue
        for sched, cap in r["capacity_psf"].items():
            if sched not in allowed:
                continue
            for s in r["sealant"]:
                for d in r["direction"]:
                    if want.get("sealant") and want["sealant"] != s or want.get("direction") and want["direction"] != d or want.get("schedule") and want["schedule"] != sched:
                        continue
                    key = (sched, s, d)
                    area = r["max_dlo_width_in"] * r["max_dlo_height_in"]
                    if key not in best or area < best[key][0]:     # tightest size class that still covers the DLO
                        best[key] = (area, cap, r)
    out = []
    for (sched, s, d), (_, cap, r) in sorted(best.items()):
        out.append(opt("glass", f"{sched} {s} {d}", cap, req, sheet=4, size_class=f"up to {r['max_dlo_width_in']:g} x {r['max_dlo_height_in']:g} DLO",
                       build=comp["glazing_schedule"][sched]["build"]))
    if not out:
        out.append(opt("glass", "no tabulated glazing covers this DLO / mode / missile level", None, req))
    return out


def eval_anchor_clusters(comp, o, req, missile, mode):
    out = []
    shim = o.get("shim_gap_in", 0.25)
    for t in comp["tables"]:
        if t["component"] != "head_sill_anchor_cluster" or t["applies"]["shim_gap_in"] < shim:
            continue
        hit = grid_lookup(t, o["tributary_width_in"], o["mullion_height_in"])
        if hit is None:
            out.append(opt("anchor_cluster", f"shim gap up to {t['applies']['shim_gap_in']} in", None, req, note=range_note(t, o["tributary_width_in"], o["mullion_height_in"])))
            continue
        by, rx, vals = hit
        mid = vals[0]
        for c, v in zip(t["columns"][1:], vals[1:]):
            out.append(opt("anchor_cluster", f"{c['end_cluster_anchor_qty']} anchors per end cluster, shim gap up to {t['applies']['shim_gap_in']} in", v, req, sheet=3,
                           looked_up=f"width {rx:g} / height {by:g}", midspan_clusters_required=mid))
    return out


def eval_project_out(comp, o, pw, req):
    spec = comp.get("project_out_windows")
    if not spec:
        return [opt("project_out_window", "project-out windows", None, req, note="not part of this product")]
    probs = []
    if o.get("frame_height_in", 0) > spec["max_frame_height_in"]:
        probs.append(f"frame height {o.get('frame_height_in'):g} > {spec['max_frame_height_in']:g} max with project-out windows")
    if pw.get("dlo_width_in", 0) > spec["max_dlo_width_in"] or pw.get("dlo_height_in", 0) > spec["max_dlo_height_in"]:
        probs.append(f"window DLO exceeds {spec['max_dlo_width_in']:g} x {spec['max_dlo_height_in']:g}")
    if pw.get("opening_height_in", 0) > spec["max_opening_height_in"]:
        probs.append(f"window opening height > {spec['max_opening_height_in']:g}")
    cap = comp["rules"].get("max_pressure_psf") if not probs else None
    return [opt("project_out_window", "project-out window (pressure governed by framing)", cap, req, note="; ".join(probs) or "within limits", build=spec["glass"])]


def eval_doors(comp, o, req, thermal):
    out = []
    for r in comp["door_assemblies"]["rows"]:
        if o.get("door_width_in", 0) > r["max_door_opening_w_in"] or o.get("door_height_in", 0) > r["max_door_opening_h_in"]:
            continue
        for th in ([thermal] if thermal else ["NT", "T", "UT"]):
            out.append(opt("door", f"{r['id']} {th}: {r['config']}", r[th], req, sheet=21))
    return out


def run(project):
    app, comp = load(project["approval"])
    dp = project["design_pressures"]
    basis = dp.get("basis", "ASD").lower()
    raw = max(abs(dp.get("positive_psf", 0)), abs(dp.get("negative_psf", 0)))
    req_asd = raw * (ASD_FACTOR if basis.startswith("strength") else 1.0)
    missile, mode, thermal = project.get("missile_level"), project.get("glazing_mode"), project.get("thermal")
    want = project.get("glazing", {})
    result = {"approval": app["fl_number"] + (f" / product {comp['product']}" if comp.get("product") else ""), "project": project.get("project", {}), "required_asd_psf": round(req_asd, 1), "pressure_basis_input": dp.get("basis", "ASD"), "openings": [], "flags": []}
    prod = next((p for p in app["products"] if p["fl"] == comp.get("product")), app["products"][0])
    lim = prod["limits_of_use"]
    if project.get("project", {}).get("hvhz") and lim.get("hvhz", "").lower() != "yes":
        result["flags"].append("Approval is NOT listed for HVHZ use.")
    if app.get("status") != "Approved":
        result["flags"].append(f"Approval status is {app.get('status')}.")
    if missile and "missile_to_glazing" in comp.get("rules", {}) and missile not in comp["rules"]["missile_to_glazing"]:
        result["flags"].append(f"Missile level {missile} is not covered by this approval.")
    if missile and comp.get("missile") and missile != comp["missile"]:
        result["flags"].append(f"Product {comp.get('product')} is rated missile level {comp['missile']}; the project calls for level {missile}. Check the other products of this approval.")
    cap = comp.get("rules", {}).get("max_pressure_psf")
    if cap and req_asd > cap:
        result["flags"].append(f"Required {req_asd:.1f} psf exceeds this product's maximum tabulated pressure of {cap:g} psf.")
    for w in comp.get("warnings", []):
        result["flags"].append(w)
    for o in project["openings"]:
        members = o.get("members", ["glass", "mullion", "head", "sill", "anchor_cluster"])
        req = round(o.get("pressure_psf_asd", req_asd), 1)
        comps = {}
        if "glass" in members: comps["glass"] = eval_glass(comp, o, req, missile, mode, want)
        if "mullion" in members: comps["mullion"] = eval_mullions(comp, o, req, missile, mode, thermal, {"mullion"})
        if "corner" in members: comps["corner_mullion"] = eval_mullions(comp, o, req, missile, mode, thermal, {"corner_mullion"})
        if "jamb" in members: comps["jamb"] = eval_mullions(comp, o, req, missile, mode, thermal, {"jamb"})
        for k in ("head", "sill", "intermediate_horizontal"):
            if k in members: comps[k] = eval_details(comp, o, req, missile, mode, thermal, k)
        if "anchor_cluster" in members: comps["anchor_cluster"] = eval_anchor_clusters(comp, o, req, missile, mode)
        if "door" in members and "door_assemblies" in comp: comps["door"] = eval_doors(comp, o, req, thermal)
        pw = o.get("project_out_window")
        if pw:
            comps["project_out_window"] = eval_project_out(comp, o, pw, req)
        not_tabulated = [k for k, v in comps.items() if not v]
        comps = {k: v for k, v in comps.items() if v}
        fh_max = comp.get("rules", {}).get("max_frame_height_in")
        notes = []
        if fh_max and o.get("frame_height_in", 0) > fh_max:
            notes.append(f"frame height {o['frame_height_in']:g} exceeds the product maximum {fh_max:g}")
        if not_tabulated:
            notes.append("not tabulated for this product (governed by other members): " + ", ".join(not_tabulated))
        result["openings"].append({"id": o["id"], "inputs": {k: v for k, v in o.items() if k != "id"}, "required_asd_psf": req, "components": comps,
                                   "notes": notes, "unsatisfied": [k for k, v in comps.items() if not any(x["pass"] for x in v)]})
    result["assumptions"] = [
        "Capacities are allowable (ASD) PSF from the sealed approval drawing; a strength-level input is converted with x0.6." if basis.startswith("strength") else "Input pressures treated as ASD, as the approval tables are ASD.",
        "Tabulated widths / heights / DLO are maxima: the tool rounds each up to the next tabulated value and never interpolates.",
        "System capacity = the LEAST capacity of the components you select.",
        comp.get("rules", {}).get("governing", ""),
        "Water infiltration, flashing, substrate adequacy and bucks are by others, outside the approval.",
        "Screening aid only - the engineer/architect of record and the AHJ decide acceptability.",
    ]
    return result


def md(res):
    L = [f"# Product approval review - {res['approval']}", ""]
    p = res["project"]
    if p:
        L.append("**Project:** " + ", ".join(f"{k}: {v}" for k, v in p.items()))
    L.append(f"**Required design pressure used:** {res['required_asd_psf']} psf ASD (input basis: {res['pressure_basis_input']})\n")
    for f in res["flags"]:
        L.append(f"> FLAG: {f}")
    for o in res["openings"]:
        L += ["", f"## Opening {o['id']}  (needs {o['required_asd_psf']} psf)", "", "Inputs: " + ", ".join(f"{k}={v}" for k, v in o["inputs"].items()), ""]
        if o["unsatisfied"]:
            L.append(f"**No passing option for:** {', '.join(o['unsatisfied'])}\n")
        for n in o.get("notes", []):
            L.append(f"_Note: {n}_\n")
        for k, opts in o["components"].items():
            ok = [x for x in opts if x["pass"]]
            L.append(f"### {k.replace('_', ' ')} - {len(ok)} of {len(opts)} pass")
            L += ["", "| Option | Capacity psf | Result | Notes |", "|---|---:|---|---|"]
            for x in sorted(opts, key=lambda x: (not x["pass"], -(x["capacity_psf"] or 0))):
                n = "; ".join(str(x[q]) for q in ("looked_up", "size_class", "note", "warning") if x.get(q))
                if x.get("midspan_clusters_required") is not None:
                    n += f"; midspan clusters required: {int(x['midspan_clusters_required'])}"
                if x.get("build"):
                    n += f"; {x['build']}"
                L.append(f"| {x['option']} | {x['capacity_psf'] if x['capacity_psf'] is not None else '-'} | {'PASS' if x['pass'] else 'fail'} | {n} |")
            L.append("")
    L += ["## Assumptions", ""] + [f"- {a}" for a in res["assumptions"] if a]
    return "\n".join(L)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("project"); ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    res = run(json.loads(pathlib.Path(a.project).read_text()))
    print(json.dumps(res, indent=1) if a.json else md(res))
