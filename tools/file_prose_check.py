#!/usr/bin/env python3
"""Focused consistency check for the FILE front-end prose.  [E2E-42/P1c]

Why this exists
---------------
P1a and P1b changed what the compiler DOES but not every sentence that describes it, and the
gate cannot see that: a stale comment emits no bytes, and coverage_check validates citation
FORM (does [C288] exist?) but never whether the prose around it still matches the code.  So a
check for the specific obsolete ASSERTIONS is the thing that would actually have caught them.

It is deliberately narrow and deliberately NOT historical.  `spec/notes/e2e41-*',
`spec/lab-evidence/**' and pre-P1c claims are RECORDS of what was believed and measured in an
earlier episode; rewriting them would destroy the evidence that the correction was needed, which
is the whole point of [C279]/[C287]-style corrections.  Those paths are on HISTORICAL below and
are allowed to contain the old sentences.  Only ACTIVE descriptions are policed.

  python3 tools/file_prose_check.py
"""
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Active descriptions: what the compiler does TODAY.
ACTIVE = [
    "ocaml/lib/codegen.ml",
    "ocaml/lib/parser.ml",
    "spec/PERIMETER.md",
    "spec/COVERAGE.tsv",
    "tools/e2e_gate.py",
]

# Sentences that are false since [E2E-42/P1b]/[C287]/[C283], with what replaced them.
FORBIDDEN = [
    (r"variable title[^.\n]{0,60}(?:refus|not lowered|unlowered)",
     "a VARIABLE title is LOWERED since [E2E-42/P1b] on two routes -- [C288]"),
    (r"(?:routes?|route) to \?SLVTS[^.\n]{0,40}refus",
     "the route is a DISPATCH on storage class, not `variable -> ?SLVTS' -- [C288]"),
    (r"VARIABLE title \(\?SLVTS\), a print open",
     "the OPEN/CLOSE header must not list a VARIABLE title among the refusals -- [C288]"),
    (r"nine OUTPUT rows",
     "there are SEVEN rows spelling `output'; the nine counted the FILE VARIABLE named "
     "`output' in LOAN2:54/56 -- [C287]"),
    (r"E2E-41/P3 witnessed subset",
     "the witnessed subset grew at [E2E-42/P0, P1a, P1b]; an era label in a live message is "
     "a claim about what is lowered"),
    (r"long-name refusal here is a my-gap",
     "the long-name refusal is CLOSED since [E2E-42/P1a] -- [C283]"),
    (r"which is not lowered\.?\"",
     "a panel narrative must not blame the TITLE for a refusal whose cause is elsewhere"),
]

# [C280] keeps its superseded counts verbatim (they are the E2E-41/P3b record) but MUST carry the
# correction banner, or a reader takes the nine as current.
C280_BANNER = "[C287] CORRECTS THE COUNTS"

# The refusal text the negative panel matches; these must survive any diagnostic rewrite.
PINNED_MARKERS = [
    "OPEN option %s is outside" % k
    for k in ("KEYED", "RECORD", "SEQUENTIAL", "UPDATE")
] + ["naming BOTH INPUT and OUTPUT", "OPEN repeats option",
        # [E2E-42/P2b] "PUT LIST with options this route" is GONE: P2b lowered every list length the
        # route can name, so that blanket sentence described nothing (no REJECTS row keyed it).  The
        # arm now names the three spellings that still reach it, and two of them have rows.
        "ON options on one PUT", "an EMPTY LIST behind a FILE option"]


def fail(msg, hits):
    print("file prose check: FAIL -- %s" % msg)
    for h in hits[:6]:
        print("   %s" % h)
    return 1


def main():
    errs, rc = [], 0
    for rel in ACTIVE:
        p = os.path.join(ROOT, rel)
        for i, line in enumerate(io.open(p, encoding="utf-8", errors="replace"), 1):
            for pat, why in FORBIDDEN:
                if re.search(pat, line):
                    errs.append("%s:%d  %s\n        [%s]" % (rel, i, line.strip()[:120], why))
    if errs:
        rc = fail("%d stale assertion(s) in active descriptions" % len(errs), errs)

    cg = io.open(os.path.join(ROOT, "ocaml/lib/codegen.ml"), encoding="utf-8").read()
    for m in PINNED_MARKERS:
        if m not in cg and m not in io.open(os.path.join(ROOT, "tools/e2e_gate.py"),
                                            encoding="utf-8").read():
            rc = fail("pinned negative-panel marker %r is gone from the source" % m, []) or rc

    claims = io.open(os.path.join(ROOT, "spec/CLAIMS.md"), encoding="utf-8").read()
    blk = re.search(r"## C280 —.*?(?=\n## C28[1-9]|\Z)", claims, re.S)
    if not blk or C280_BANNER not in blk.group(0):
        rc = fail("[C280] keeps the superseded `nine OUTPUT' counts but lost its %r banner"
                  % C280_BANNER, []) or rc

    # provenance must not cite the same claim TWICE IN THE LEADING CITE CLUSTER.  The rule is
    # deliberately about the cluster, not the whole cell: long multi-episode provenance cells
    # legitimately mention a claim again in prose (DECL.MEMBER_SCOPE says "Corrects [C261]'s
    # E39S5 sentence" after citing [C261]), and a blanket duplicate test would flag that.
    for i, line in enumerate(io.open(os.path.join(ROOT, "spec/COVERAGE.tsv"), encoding="utf-8"), 1):
        if line.startswith("#"):
            continue
        f = line.rstrip("\n").split("\t")
        if len(f) < 15:
            continue
        cluster = re.match(r"^((?:\s*\[C\d+\])+)", f[14])
        if not cluster:
            continue
        seen = re.findall(r"\[C\d+\]", cluster.group(1))
        dup = sorted({c for c in seen if seen.count(c) > 1})
        if dup:
            rc = fail("line %d (%s) cites %s twice in the leading provenance cluster"
                      % (i, f[0], ",".join(dup)), []) or rc

    if not rc:
        print("file prose check: %d active files clean (%d forbidden assertions, %d pinned "
              "markers, [C280] banner, no duplicate provenance cites)"
              % (len(ACTIVE), len(FORBIDDEN), len(PINNED_MARKERS)))
    return rc


if __name__ == "__main__":
    sys.exit(main())
