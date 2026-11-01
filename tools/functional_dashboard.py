#!/usr/bin/env python3
"""[E2E-50/P1] Functional capability dashboard -- aggregates canonical evidence, compiles NOTHING.

Reads (read-only): spec/functional/capabilities.tsv, spec/functional/programs.tsv (annotations),
spec/COVERAGE.tsv, spec/INVENTORY.txt, spec/RUNTIME.txt, spec/DIVERGENT.txt,
spec/census/corpus-census.json, spec/census/coverage-stats.json (gate-maintained snapshots), and
NEG_META / SPECIMENS / REJECTS by IMPORTING tools/e2e_gate.py (measured side-effect-free at
5247656: empty stdout, tree unchanged, nothing compiled).  It NEVER runs the gate, the compiler,
the oracle, LINK-80 or cpmsim, and never recompiles a number that a committed snapshot already
carries.

Views (deterministic ordering; no timestamps, no git state -- same inputs, same bytes):
  A  capability status (taxonomy order): rows verdict + derived stage ladder + DR side
  B  evidence map: validation misses, COVERAGE rows cited by NO capability
  C  representative programs by origin class (counts NEVER summed across classes)
  D  canonical-ledger snapshot (panel/census/coverage/runtime/divergent counts, as committed)
  E  ranked candidate shortlist for the operator's next compiler round (derived, not authored)

Stage law (spec/functional/README.md): SYNTAX/BIND are licensed ONLY by a machine message whose
stage prefix is identifiable, or by a later stage; a generic "refused" licenses no stage.  OBJGEN
requires a produced .REL (panel specimen, divergent row, or census EXACT/DIFFERS); BYTE requires
panel `exact` (whole-file .REL identity) or census EXACT; LINK/RUN require a spec/RUNTIME.txt row.
UNKNOWN is a legal answer and is NEVER rendered as success.

  usage: python3 tools/functional_dashboard.py [--write | --check]
"""
import argparse
import collections
import importlib.util
import json
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def _load_panel_keys_lib():
    """panel_keys.py ends with an UNGUARDED `main()` call -- importing it runs its CLI with the
    caller's argv (measured 2026-11-02).  Take its definitions by exec-ing the source with that
    trailing call removed; the resolution law (INVENTORY + DIVERGENT) is reused, never re-implemented."""
    path = os.path.join(ROOT, "tools/panel_keys.py")
    src = open(path, encoding="utf-8").read()
    i = src.rindex("main()")
    ns = {"__name__": "panel_keys_lib", "__file__": path}
    exec(compile(src[:i] + "pass\n", path, "exec"), ns)
    return ns


_PANEL = _load_panel_keys_lib()
panel_load = _PANEL["load"]

STAGES = ["SYNTAX", "BIND", "OBJGEN", "BYTE", "LINK", "RUN"]
ORIGIN_ORDER = ["HISTORICAL", "FOCUSED", "MICROPROBE"]
NEG_ORDER = ["my-gap", "dr-refuses", "unmeasured", "UNCLASSIFIED"]


def read_tsv(path):
    """Comment-stripped TSV: returns (header_fields, [dict row]).  '#' lines are comments."""
    with open(path, encoding="utf-8") as f:
        data = [l.rstrip("\n") for l in f if l.strip() and not l.startswith("#")]
    hdr = data[0].split("\t")
    return hdr, [dict(zip(hdr, l.split("\t"))) for l in data[1:]]


def load_inventory():
    """name -> (kind, source_or_text, field4).  kind: specimen|refusal."""
    inv = {}
    with open(os.path.join(ROOT, "spec/INVENTORY.txt"), encoding="utf-8") as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            flds = line.rstrip("\n").split("\t")
            if len(flds) >= 4:
                inv[flds[0]] = (flds[1], flds[2], flds[3])
    return inv


def load_runtime():
    """name -> list of (kind, exit, source)."""
    rows = collections.defaultdict(list)
    p = os.path.join(ROOT, "spec/RUNTIME.txt")
    if not os.path.exists(p):
        return rows
    with open(p, encoding="utf-8") as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            flds = line.rstrip("\n").split("\t")
            if len(flds) >= 6 and flds[0] != "name":
                rows[flds[0]].append((flds[1], flds[5], flds[6] if len(flds) > 6 else ""))
    return rows


def load_census():
    with open(os.path.join(ROOT, "spec/census/corpus-census.json"), encoding="utf-8") as f:
        cen = json.load(f)
    return {r["name"]: r for r in cen["rows"]}, cen.get("counts", {})


def load_gate_meta():
    """Import the gate module (NEVER run it) and take the live panels + NEG_META."""
    spec = importlib.util.spec_from_file_location(
        "e2e_gate_for_dashboard", os.path.join(ROOT, "tools/e2e_gate.py"))
    gate = importlib.util.module_from_spec(spec)
    captured, sys.stdout = sys.stdout, open(os.devnull, "w")
    try:
        spec.loader.exec_module(gate)
    finally:
        sys.stdout.close()
        sys.stdout = captured
    return gate


def stage_from_machine_message(text):
    """Map a MACHINE failure message to the stage it identifies, or None (generic refused).

    Only the prefixes measured in real output are honoured: `codegen:' (Ocaml failure),
    `Pli80.Parser` / `parse_error` (parser), binder wording (bind).  Verdict prose such as
    "DR COMPILES IT ... MY GAP" is NOT a machine message and returns None here -- callers pass
    only census msg / reason bodies that came from a compiler run.
    """
    t = (text or "").lower()
    if "codegen:" in t:
        return "codegen"
    if "pli80.parser" in t or "parse_error" in t:
        return "parser"
    if re.search(r"\bbinder\b|\bbind\b|declaration resolution", t):
        return "bind"
    return None


def name_facts(name, inv, census, runtime, exact, divergent, refused, neg_meta):
    """Derive the stage set + verdict facts for one evidence name.  Pure lookup, no inference
    beyond the README stage law.  Returns a dict; stage set may legitimately be empty (=UNKNOWN)."""
    stages = set()
    reached = None            # furthest identifiable stage reached/passed
    blocked = None            # where a refusal stopped it, when the message names it
    mine = None
    neg_class = None
    dr = None
    if name in neg_meta:
        neg_class = neg_meta[name][0] if isinstance(neg_meta[name], tuple) else "UNCLASSIFIED"
    rt = runtime.get(name)
    if rt:
        kinds = sorted({k for k, _e, _s in rt})
        allok = all(e == "ok" for _k, e, _s in rt)
        stages.update(["OBJGEN", "LINK", "RUN", "BIND", "SYNTAX"])
        mine = "RUN(%s)" % "+".join(kinds) if allok else "RUN-FAIL"
        reached = "RUN" if allok else "LINK"
    if name in exact:
        stages.update(["SYNTAX", "BIND", "OBJGEN", "BYTE"])
        mine = mine or "BYTE-EXACT"
        reached = "BYTE" if "RUN" not in stages else reached
        if name in inv:
            golden = inv[name][2]
            if golden.startswith("golden/") and os.path.exists(os.path.join(ROOT, golden)):
                dr = "dr ACCEPTS (golden)"
            elif not dr:
                dr = "dr UNMEASURED (no golden witness)"
    elif name in divergent:
        stages.update(["SYNTAX", "BIND", "OBJGEN"])
        mine = mine or "BYTE-DIVERGENT"   # BYTE is explicitly NOT granted
        reached = reached or "OBJGEN"
    elif name in refused:
        msg = inv[name][2] if name in inv else ""
        blocked = stage_from_machine_message(msg)
        if blocked == "codegen":
            stages.update(["SYNTAX", "BIND"]); reached = "BIND"
        elif blocked == "bind":
            stages.update(["SYNTAX"]); reached = "SYNTAX"
        # parser-stop or generic refusal: no stage is licensed (README: never infer from "refused")
        mine = mine or "REFUSED"
        if neg_class == "dr-refuses":
            dr = "dr REJECTS (classified)"
        elif neg_class == "my-gap":
            dr = "dr ACCEPTS (classified)"
    cen = census.get(name)
    if cen:
        dr = {"ok": "dr ACCEPTS (oracle ran)", "diag": "dr REJECTS (.PRN diagnostic)"}.get(
            cen["dr_verdict"], dr or "dr UNMEASURED")
        if cen["mine"] == "EXACT":
            stages.update(["SYNTAX", "BIND", "OBJGEN", "BYTE"])
            mine = "BYTE-EXACT" if mine is None else mine
            reached = reached if "RUN" in stages else "BYTE"
        elif cen["mine"] == "DIFFERS":
            stages.update(["SYNTAX", "BIND", "OBJGEN"])
            mine = "BYTE-DIVERGENT" if mine is None else mine
        elif cen["mine"] == "REFUSED":
            blocked = blocked or stage_from_machine_message(cen.get("msg", ""))
            if blocked == "codegen":
                stages.update(["SYNTAX", "BIND"]); reached = reached or "BIND"
            elif blocked == "bind":
                stages.update(["SYNTAX"]); reached = reached or "SYNTAX"
            mine = mine or "REFUSED"
        elif cen["mine"] == "NO_ORACLE":
            # DR emitted a .PRN diagnostic (no oracle .REL) AND mine stopped too; the census msg
            # is MY machine message, so its stage prefix licenses the ladder exactly like a panel
            # refusal does.  Never claim an object was produced.
            blocked = blocked or stage_from_machine_message(cen.get("msg", ""))
            if blocked == "codegen":
                stages.update(["SYNTAX", "BIND"]); reached = reached or "BIND"
            elif blocked == "bind":
                stages.update(["SYNTAX"]); reached = reached or "SYNTAX"
            mine = mine or "REFUSED (no oracle)"
    if not stages:
        reached = reached or ("parser" if blocked == "parser" else None)
    return {"name": name, "stages": stages, "reached": reached, "blocked": blocked,
            "mine": mine, "neg": neg_class or ("my-gap" if cen and cen["mine"] == "REFUSED"
                                               and cen["dr_verdict"] == "ok" else None),
            "dr": dr,
            "panel": ("specimen" if name in exact else "divergent" if name in divergent
                      else "refusal" if name in refused else "unlisted")}


def aggregate_rows(row_ids, coverage):
    """README law: PARTIAL when cited rows disagree, UNKNOWN when they carry no verdict.
    Returns (mine_verdict, dr_verdict, runtime_tokens)."""
    ms, ds, rts = [], [], []
    for rid in row_ids:
        r = coverage.get(rid)
        if not r:
            continue
        ms.append(r["mine_status"])
        ds.append(r["dr_status"])
        rts.append(r.get("runtime", "NONE"))
    if not ms:
        return "UNKNOWN", "UNKNOWN", []
    uniq_m, uniq_d = set(ms), set(ds)
    if uniq_m == {"SUPPORTED"}:
        mv = "SUPPORTED"
    elif uniq_m <= {"REFUSED", "NOT_ATTEMPTED"}:
        mv = "REFUSED" if uniq_m == {"REFUSED"} else "NOT_ATTEMPTED"
    elif len(uniq_m) == 1:
        mv = uniq_m.pop().upper()
    else:
        mv = "PARTIAL"
    ok_d = {"ACCEPTS", "ACCEPTS_DEFECT"}
    if uniq_d <= ok_d:
        dv = "ACCEPTS"
    elif uniq_d == {"REJECTS"}:
        dv = "REJECTS"
    elif uniq_d == {"UNTESTED"}:
        dv = "UNTESTED"
    else:
        dv = "MIXED(" + ",".join("%s:%d" % (k, v) for k, v in sorted(collections.Counter(ds).items())) + ")"
    return mv, dv, rts


def ladder(facts_list):
    """Highest stage CHAIN achieved by any evidence name, rendered strictly.  A stage string is
    emitted only when evidence licenses it; with no evidence at all this returns UNKNOWN, never a
    success word."""
    if not facts_list:
        return "UNKNOWN (no resolvable evidence)"
    best = 0
    marks = []
    for fa in facts_list:
        for i, s in enumerate(STAGES):
            if s in fa["stages"]:
                best = max(best, i + 1)
        if fa["reached"] == "parser":
            marks.append("stopped-at-parser")
        if fa["reached"] == "BIND" and fa["blocked"] == "codegen":
            marks.append("reached-codegen-refused")
    if best == 0:
        extra = ("; " + ";".join(sorted(set(marks)))) if marks else ""
        return "UNKNOWN (nothing licensed%s)" % extra
    chain = " ".join(STAGES[:best])
    if any("BYTE-DIVERGENT" == fa["mine"] for fa in facts_list) and "BYTE" not in STAGES[:best]:
        chain += " +OBJGEN-divergent"
    return chain


def evidence_names_for_cap(cap, caps_hdr, prog_rows, coverage, inv, census_names=frozenset()):
    """Union of: corpus_programs citation, programs.tsv mapping, and probe/corpus tokens of the
    cited COVERAGE rows that resolve to a registered panel name OR a census program (26 census
    programs are REFUSED and therefore absent from INVENTORY).  Returns (names, unresolved)."""
    names = set()
    cp = cap["corpus_programs"].strip()
    if cp != "NONE":
        names.update(p.strip() for p in cp.split(",") if p.strip())
    for pr in prog_rows:
        if cap["cap_id"] in pr["capabilities"].split(";"):
            names.add(pr["id"])
    resolvable = set(inv) | set(census_names)
    for rid in [x for x in cap["coverage_rows"].split(";") if x]:
        r = coverage.get(rid)
        if not r:
            continue
        for tok in re.findall(r"[A-Z][A-Z0-9]*", r["probes"] + "," + r["corpus"]):
            if tok in resolvable:
                names.add(tok)
    return names, set()


def rank_candidates(cap_rows, facts_by_name, coverage):
    """View E scoring, fully derived: (census programs blocked, refused evidence count,
    blocked cited rows, cap_id tiebreak).  Only capabilities whose rows do not all SUPPORT
    qualify."""
    cands = []
    for cap in cap_rows:
        ridz = [x for x in cap["coverage_rows"].split(";") if x]
        mv, dv, _ = aggregate_rows(ridz, coverage)
        if mv == "SUPPORTED":
            continue
        fl = [facts_by_name[n] for n in cap["_names"] if n in facts_by_name]
        blocked_names = [fa for fa in fl if fa["mine"] in ("REFUSED", "BYTE-DIVERGENT", "RUN-FAIL")]
        census_blocked = sum(1 for fa in blocked_names if fa["panel"] == "unlisted" and fa["dr"])
        rows_blocked = sum(1 for r in ridz if r in coverage and
                           coverage[r]["mine_status"] != "SUPPORTED")
        negmix = collections.Counter(fa["neg"] for fa in blocked_names if fa["neg"])
        cands.append({
            "cap": cap, "mv": mv, "dv": dv,
            "census_blocked": census_blocked,
            "names_blocked": len(blocked_names),
            "rows_blocked": rows_blocked,
            "neg": negmix,
        })
    cands.sort(key=lambda c: (-c["census_blocked"], -c["names_blocked"],
                              -c["rows_blocked"], c["cap"]["cap_id"]))
    return cands


def render(cap_hdr, cap_rows, prog_hdr, prog_rows, coverage, facts_by_name, gate, cen_counts,
           cov_stats, runtime, inventory, exact, divergent, refused):
    L = []
    add = L.append
    add("# Functional status -- generated by `tools/functional_dashboard.py --write`")
    add("")
    add("DO NOT HAND-EDIT.  Every verdict here is *derived* from the canonical sources listed in")
    add("`spec/functional/README.md`; this directory is annotation, never a second ledger.  The run")
    add("that produced this file compiled nothing and ran no gate: numbers come from committed")
    add("snapshots (`spec/census/*.json`, `spec/INVENTORY.txt`) and from IMPORTING the gate module.")
    add("`UNKNOWN` is a legal verdict and is never rendered as success.")
    add("")
    add("## View A -- capabilities")
    add("")
    add("`Rows verdict (mine)` aggregates the MINE status of the cited COVERAGE rows (README law:")
    add("PARTIAL when cited rows disagree, UNKNOWN when they carry no verdict).  The `Derived stage")
    add("ladder` names the HIGHEST stage any single evidence name of that capability is licensed to")
    add("reach -- it is a breadth signal, not a per-shape guarantee; individual shapes stop earlier")
    add("and the boundary column says where.  A generic refusal licenses no stage.")
    add("")
    add("| Capability | Area | Rows verdict (mine) | DR side | Derived stage ladder | Evidence |")
    add("|---|---|---|---|---|---|")
    for cap in cap_rows:
        ridz = [x for x in cap["coverage_rows"].split(";") if x]
        mv, dv, _rt = aggregate_rows(ridz, coverage)
        fl = [facts_by_name[n] for n in cap["_names"] if n in facts_by_name]
        add("| %s | %s | %s | %s | %s | %d cited evidence names, %d COVERAGE rows |" % (
            cap["cap_id"], cap["area"], mv, dv, ladder(fl), len(fl), len(ridz)))
    add("")
    add("## View B -- evidence map")
    add("")
    cited_rows = set()
    for cap in cap_rows:
        cited_rows.update(x for x in cap["coverage_rows"].split(";") if x)
    misses = [m for cap in cap_rows for m in cap["_misses"]]
    dup = [cap["cap_id"] for cap in cap_rows if cap["_dup"]]
    add("- capability rows: **%d** (validated: every cited COVERAGE id exists, every cited census"
        " name is one of the 44)" % len(cap_rows))
    add("- citation misses: **%s**" % ("none" if not misses else "; ".join(sorted(set(misses)))))
    add("- duplicate capability ids: **%s**" % ("none" if not dup else ", ".join(sorted(dup))))
    unmapped = sorted(set(coverage) - cited_rows)
    add("- COVERAGE rows cited by NO capability: **%d** -- listed for the operator, never silently"
        " dropped:" % len(unmapped))
    for rid in unmapped:
        add("  - `%s` (%s: %s)" % (rid, coverage[rid]["category"], coverage[rid]["construct"]))
    add("")
    add("## View C -- representative programs by origin class")
    add("")
    add("Counts are NEVER summed across origin classes (`spec/functional/README.md`).")
    for cls in ORIGIN_ORDER:
        rowsc = [r for r in prog_rows if r["origin"] == cls]
        add("")
        add("### %s -- %d programs" % (cls, len(rowsc)))
        add("")
        add("| Program | Source | Capabilities | Panel | Mine | DR | Stages |")
        add("|---|---|---|---|---|---|---|")
        for r in sorted(rowsc, key=lambda x: x["id"]):
            fa = facts_by_name.get(r["id"])
            stages = (" ".join([s for s in STAGES if s in fa["stages"]])
                      if fa and fa["stages"] else "UNKNOWN")
            add("| %s | %s | %s | %s | %s | %s | %s |" % (
                r["id"], r["source"], r["capabilities"],
                fa["panel"] if fa else "-", fa["mine"] or "UNKNOWN" if fa else "UNKNOWN",
                fa["dr"] or "UNMEASURED" if fa else "UNMEASURED", stages))
    add("")
    add("## View D -- canonical-ledger snapshot (committed; not re-measured here)")
    add("")
    negmix = collections.Counter(v[0] for v in gate.NEG_META.values())
    add("- byte panel: **%d** specimens (all whole-file `.REL` identity); negative panel: **%d**;"
        " NEG_META classes: %s." % (
            len(gate.SPECIMENS), len(gate.REJECTS),
            ", ".join("%s %d" % (k, negmix.get(k, 0)) for k in NEG_ORDER if negmix.get(k))))
    add("- INVENTORY.txt rows: **%d** (%d specimen / %d refusal)." % (
        len(inventory), sum(1 for v in inventory.values() if v[0] == "specimen"),
        sum(1 for v in inventory.values() if v[0] == "refusal")))
    census_all = load_census()[0]
    dr_ok = sum(1 for r in census_all.values() if r["dr_verdict"] == "ok")
    dr_diag = sum(1 for r in census_all.values() if r["dr_verdict"] == "diag")
    add("- historical census (44 programs): EXACT %d / DIFFERS %d / REFUSED %d / NO_ORACLE %d;"
        " DR verdicts ok %d / diag %d (counts from `spec/census/corpus-census.json`)." % (
            cen_counts.get("EXACT", 0), cen_counts.get("DIFFERS", 0), cen_counts.get("REFUSED", 0),
            cen_counts.get("NO_ORACLE", 0), dr_ok, dr_diag))
    mm, dm = cov_stats.get("mine", {}), cov_stats.get("dr", {})
    n_rows = cov_stats.get("rows", sum(cov_stats.get("by_category", {}).values()))
    add("- COVERAGE: %d rows -- mine %s; DR %s (from `spec/census/coverage-stats.json`)." % (
        n_rows,
        ", ".join("%s %d" % (k, v) for k, v in sorted(mm.items())),
        ", ".join("%s %d" % (k, v) for k, v in sorted(dm.items()))))
    rk = collections.Counter(k for rows in runtime.values() for k, e, s in rows)
    n_rows_rt = sum(len(v) for v in runtime.values())
    hist_rt = sorted(set(runtime) & {r["name"] for r in load_census()[0].values()})
    add("- RUNTIME.txt: **%d** rows / **%d** distinct names (one row per name), exit=ok on every"
        " row; kinds: %s.  Historical-census programs with a runtime row: %s."
        "  Panel-unregistered runtime names: %s." % (
            n_rows_rt, len(runtime),
            ", ".join("%s %d" % (k, v) for k, v in sorted(rk.items())),
            ", ".join(hist_rt) or "none",
            ", ".join(sorted(n for n in runtime if n not in inventory)) or "none"))
    add("- DIVERGENT.txt (pinned divergences, via panel_keys): %d -- %s." % (
        len(divergent), ", ".join(sorted(divergent))))
    add("")
    add("## View E -- ranked candidate shortlist for the NEXT compiler round")
    add("")
    add("Ranked mechanically from the evidence above (blocked census programs, then refused")
    add("evidence names, then blocked cited rows, then id).  `Blocked evidence` lists up to six")
    add("names whose derived mine verdict is a refusal or a pinned divergence; `Evidence classes")
    add("(NEG_META)` counts over ALL blocked names of the capability.  This is a shortlist for the")
    add("operator to CHOOSE from -- it is not an authorisation, and no candidate may be started")
    add("without a pre-registered round (PROTOCOL).")
    add("")
    add("| Rank | Capability | Verdict | DR side | Blocked evidence | Evidence classes | Boundary (annotation) |")
    add("|---|---|---|---|---|---|---|")
    for i, c in enumerate(rank_candidates(cap_rows, facts_by_name, coverage)[:12], 1):
        names_bl = sorted(n for n in c["cap"]["_names"]
                          if facts_by_name.get(n, {}).get("mine") in
                          ("REFUSED", "BYTE-DIVERGENT", "RUN-FAIL"))
        add("| %d | %s | %s | %s | %s | %s | %s |" % (
            i, c["cap"]["cap_id"], c["mv"], c["dv"],
            ", ".join(names_bl[:6]) or "-",
            ", ".join("%s %d" % (k, c["neg"][k]) for k in NEG_ORDER if c["neg"].get(k)) or "-",
            c["cap"]["boundary_note"]))
    add("")
    return "\n".join(L) + "\n"


def build():
    cap_hdr, cap_rows = read_tsv(os.path.join(ROOT, "spec/functional/capabilities.tsv"))
    prog_hdr, prog_rows = read_tsv(os.path.join(ROOT, "spec/functional/programs.tsv"))
    cov_hdr, cov_rows = read_tsv(os.path.join(ROOT, "spec/COVERAGE.tsv"))
    coverage = {r["id"]: r for r in cov_rows}
    inventory = load_inventory()
    census, cen_counts = load_census()
    runtime = load_runtime()
    gate = load_gate_meta()
    neg_meta = gate.NEG_META
    exact, divergent, refused = panel_load(ROOT)
    refused |= {n for n, (k, _s, _r) in inventory.items() if k == "refusal"}
    cov_stats = {}
    cs = os.path.join(ROOT, "spec/census/coverage-stats.json")
    if os.path.exists(cs):
        cov_stats = json.load(open(cs, encoding="utf-8"))

    # validation (item 1a re-run as a hard check, not a one-off): every cited id/name must exist.
    all_census = set(census)
    for cap in cap_rows:
        miss = []
        for rid in [x for x in cap["coverage_rows"].split(";") if x]:
            if rid not in coverage:
                miss.append("coverage:%s" % rid)
        cp = cap["corpus_programs"].strip()
        if cp != "NONE":
            for p in cp.split(","):
                if p.strip() and p.strip() not in all_census:
                    miss.append("census:%s" % p.strip())
        cap["_misses"] = miss
        names_set, _unres = evidence_names_for_cap(
            cap, cap_hdr, prog_rows, coverage, inventory, set(census))
        cap["_names"] = sorted(names_set)
    ids = [c["cap_id"] for c in cap_rows]
    dup = collections.Counter(ids)
    for cap in cap_rows:
        cap["_dup"] = dup[cap["cap_id"]] > 1
    prog_ids = {p["id"] for p in prog_rows}
    for p in prog_rows:
        if not os.path.exists(os.path.join(ROOT, p["source"])):
            raise SystemExit("programs.tsv: missing source %s" % p["source"])
        for c in [x for x in p["capabilities"].split(";") if x and x != "NONE"]:
            if c not in set(ids):
                raise SystemExit("programs.tsv: %s cites unknown capability %s" % (p["id"], c))
        if p["origin"] not in ORIGIN_ORDER:
            raise SystemExit("programs.tsv: bad origin %r" % p["origin"])

    names = set()
    for cap in cap_rows:
        names.update(cap["_names"])
    names.update(prog_ids)
    facts = {n: name_facts(n, inventory, census, runtime, exact, divergent, refused, neg_meta)
             for n in sorted(names)}
    return (cap_hdr, cap_rows, prog_hdr, prog_rows, coverage, facts, gate, cen_counts,
            cov_stats, runtime, inventory, exact, divergent, refused, dup)


OUT = "docs/functional-status.md"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--write", action="store_true", help="write docs/functional-status.md")
    ap.add_argument("--check", action="store_true", help="verify it is up to date (exit 1 if not)")
    a = ap.parse_args(argv)
    (cap_hdr, cap_rows, prog_hdr, prog_rows, coverage, facts, gate, cen_counts, cov_stats,
     runtime, inventory, exact, divergent, refused, dup) = build()
    text = render(cap_hdr, cap_rows, prog_hdr, prog_rows, coverage, facts, gate, cen_counts,
                  cov_stats, runtime, inventory, exact, divergent, refused)
    if dup and any(v > 1 for v in dup.values()):
        sys.exit("duplicate capability ids: %s" % ", ".join(sorted(k for k, v in dup.items() if v > 1)))
    misses = [m for cap in cap_rows for m in cap["_misses"]]
    if misses:
        sys.exit("citation misses (fix the annotation, not the ledger): %s" % ", ".join(sorted(set(misses))))
    outp = os.path.join(ROOT, OUT)
    if a.write:
        os.makedirs(os.path.dirname(outp), exist_ok=True)
        with open(outp, "w", encoding="utf-8") as f:
            f.write(text)
        print("wrote %s (%d lines)" % (OUT, text.count("\n")))
        return 0
    if a.check:
        if not os.path.exists(outp):
            sys.exit("%s is missing -- run --write" % OUT)
        cur = open(outp, encoding="utf-8").read()
        if cur != text:
            sys.exit("%s is STALE -- rerun --write" % OUT)
        print("%s is up to date" % OUT)
        return 0
    sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
