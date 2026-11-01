#!/usr/bin/env python3
"""[E2E-50/P1] Unit + integration tests for tools/functional_dashboard.py.

Covers the four behaviours the HANDOFF brief names -- classification, aggregation, missing data,
unmapped rows -- plus the two invariants that make the report trustworthy: UNKNOWN is never
rendered as success, and the render is deterministic (same inputs, byte-identical output).
Runs in plain python3; touches no compiler, oracle or gate RUN (the gate MODULE import is the
dashboard's sanctioned read path, exercised once in the integration test).

  usage: python3 tools/test_functional_dashboard.py
"""
import os
import sys
from types import SimpleNamespace

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import functional_dashboard as fd  # noqa: E402

FAILED = []


def check(label, cond):
    print(("PASS  " if cond else "FAIL  ") + label)
    if not cond:
        FAILED.append(label)


# ---------------------------------------------------------------- classification
check("stage msg: codegen prefix", fd.stage_from_machine_message(
    'Fatal error: exception Failure("codegen: [TBD] multi-dimensional")') == "codegen")
check("stage msg: parser exception", fd.stage_from_machine_message(
    "Fatal error: exception Pli80.Parser.Parse_error(_, \"expected statement\")") == "parser")
check("stage msg: binder prose", fd.stage_from_machine_message(
    "Mine refuses at the binder's statement walker") == "bind")
check("stage msg: generic refused licenses NOTHING",
      fd.stage_from_machine_message("DR COMPILES IT ... this is a MY GAP") is None)

INV = {"SP1": ("specimen", "probes/SP1.PLI", "golden/first/A/A.REL"),
       "RF1": ("refusal", "a: procedure options(main);",
               'Fatal error: exception Failure("codegen: [TBD] shape")'),
       "RF2": ("refusal", "a: procedure options(main);", "DR COMPILES IT ... MY GAP")}
CEN = {"NET": {"name": "NET", "dr_verdict": "ok", "mine": "EXACT", "msg": ""},
       "CAL": {"name": "CAL", "dr_verdict": "diag", "mine": "NO_ORACLE",
               "msg": "Fatal error: exception Pli80.Parser.Parse_error(x)"},
       "INVERT": {"name": "INVERT", "dr_verdict": "diag", "mine": "NO_ORACLE",
                  "msg": "Fatal error: exception Failure(\"codegen: [TBD] 2-D\")"}}
RT = {"NET": [("independent", "ok", "artefacts/NET.PLI")]}
EX, DIV, REF = {"SP1"}, {"DV1"}, {"RF1", "RF2"}
NEG = {"RF1": ("my-gap", "..."), "RF2": ("dr-refuses", "...")}
facts = lambda n: fd.name_facts(n, INV, CEN, RT, EX, DIV, REF, NEG)

f = facts("SP1")
check("specimen: OBJGEN+BYTE, no LINK/RUN without a runtime row",
      {"SYNTAX", "BIND", "OBJGEN", "BYTE"} <= f["stages"] and not ({"LINK", "RUN"} & f["stages"]))
check("specimen: golden witness puts DR on ACCEPTS", f["dr"] == "dr ACCEPTS (golden)")
f = facts("DV1")
check("divergent: OBJGEN yes, BYTE explicitly NOT granted",
      "OBJGEN" in f["stages"] and "BYTE" not in f["stages"] and f["mine"] == "BYTE-DIVERGENT")
f = facts("RF1")
check("refusal w/ codegen message: SYNTAX+BIND licensed, no OBJGEN",
      f["stages"] == {"SYNTAX", "BIND"} and "OBJGEN" not in f["stages"]
      and f["mine"] == "REFUSED" and f["neg"] == "my-gap")
f = facts("RF2")
check("generic refusal: NO stage licensed (README law)",
      f["stages"] == set() and f["reached"] is None and f["neg"] == "dr-refuses"
      and f["dr"] == "dr REJECTS (classified)")
f = facts("NET")
check("census+runtime: LINK+RUN granted, exit=ok kind shown",
      {"LINK", "RUN"} <= f["stages"] and f["mine"].startswith("RUN("))
f = facts("CAL")
check("NO_ORACLE + parser message: refused, no stage success",
      f["mine"] == "REFUSED (no oracle)" and f["stages"] == set() and f["dr"] == "dr REJECTS (.PRN diagnostic)")
f = facts("INVERT")
check("NO_ORACLE + codegen message: SYNTAX+BIND", f["stages"] == {"SYNTAX", "BIND"})
f = facts("MISSING42")
check("missing data: an unknown name is UNKNOWN on every axis",
      f["stages"] == set() and f["mine"] is None and f["dr"] is None
      and f["panel"] == "unlisted" and f["reached"] is None)

# ---------------------------------------------------------------- aggregation
COV = {"R.S": {"id": "R.S", "mine_status": "SUPPORTED", "dr_status": "ACCEPTS", "runtime": "NONE",
               "probes": "SP1,RF1", "corpus": "NET", "category": "X", "construct": "c"},
       "R.P": {"id": "R.P", "mine_status": "PARTIAL", "dr_status": "REJECTS", "runtime": "NONE",
               "probes": "NONE", "corpus": "NONE", "category": "X", "construct": "c"},
       "R.R": {"id": "R.R", "mine_status": "REFUSED", "dr_status": "UNTESTED", "runtime": "NONE",
               "probes": "RF2", "corpus": "INVERT", "category": "X", "construct": "c"}}
check("aggregate: all-SUPPORTED rows -> SUPPORTED", fd.aggregate_rows(["R.S"], COV)[0] == "SUPPORTED")
check("aggregate: rows disagree -> PARTIAL", fd.aggregate_rows(["R.S", "R.P"], COV)[0] == "PARTIAL")
check("aggregate: all-REFUSED -> REFUSED", fd.aggregate_rows(["R.R"], COV)[0] == "REFUSED")
check("aggregate: no cited rows -> UNKNOWN, never success",
      fd.aggregate_rows([], COV)[:2] == ("UNKNOWN", "UNKNOWN"))
check("aggregate: DR mixed carries per-class counts",
      fd.aggregate_rows(["R.S", "R.P"], COV)[1].startswith("MIXED("))

# ---------------------------------------------------------------- ladder / UNKNOWN law
check("ladder: no evidence -> UNKNOWN", fd.ladder([]).startswith("UNKNOWN"))
check("ladder: generic refusals only -> UNKNOWN (nothing licensed)",
      fd.ladder([facts("RF2")]).startswith("UNKNOWN"))
check("ladder: exact specimen -> full BYTE chain", fd.ladder([facts("SP1")]) == "SYNTAX BIND OBJGEN BYTE")
check("ladder: runtime -> LINK RUN chain", "LINK RUN" in fd.ladder([facts("NET")]))

# ---------------------------------------------------------------- evidence + unmapped handling
cap = {"cap_id": "T.ONE", "corpus_programs": "NET", "coverage_rows": "R.S;R.R",
       "area": "A", "capability": "c", "boundary_note": "b"}
progs = [{"id": "SP9", "source": "probes/SP9.PLI", "origin": "MICROPROBE",
          "capabilities": "T.ONE", "note": "n"}]
names, _un = fd.evidence_names_for_cap(cap, [], progs, COV, INV, set(CEN))
check("evidence union: citation + program map + resolvable probe tokens",
      names == {"NET", "SP9", "SP1", "RF1", "RF2", "INVERT"})
cand = fd.rank_candidates(
    [dict(cap, coverage_rows="R.P;R.R", _names=["RF2", "INVERT"], _misses=[], _dup=False),
     {"cap_id": "T.S", "coverage_rows": "R.S", "corpus_programs": "NET", "area": "A",
      "capability": "c", "boundary_note": "b", "_names": [], "_misses": [], "_dup": False}],
    {n: facts(n) for n in ("RF2", "INVERT", "NET")}, COV)
check("rank: SUPPORTED-only capability is not a candidate", [c["cap"]["cap_id"] for c in cand] == ["T.ONE"])

# ---------------------------------------------------------------- integration: determinism + report law
cap_hdr, cap_rows = fd.read_tsv(os.path.join(fd.ROOT, "spec/functional/capabilities.tsv"))
prog_hdr, prog_rows = fd.read_tsv(os.path.join(fd.ROOT, "spec/functional/programs.tsv"))
_bundle = fd.build()
t1 = fd.render(*_bundle[:14])
t2 = fd.render(*fd.build()[:14])
check("integration: two renders are byte-identical (deterministic)", t1 == t2)
check("integration: all five views present",
      all(("## View " + v) in t1 for v in "ABCDE"))
check("integration: origin classes stated separately, never summed",
      t1.count("### HISTORICAL") == 1 and "NEVER summed" in t1)
bad = [l for l in t1.splitlines() if l.startswith("|") and "UNKNOWN" in l and " BYTE" in l]
check("integration: no rendered line pairs UNKNOWN with a BYTE success", not bad)
check("integration: citation misses are surfaced as none (validated taxonomy)",
      "citation misses: **none**" in t1)
check("integration: unmapped COVERAGE rows are listed, not dropped",
      "cited by NO capability: **26**" in t1)

print("FAILED:", FAILED or "none")
sys.exit(1 if FAILED else 0)
