#!/usr/bin/env python3
"""[E2E-37/P1] HISTORICAL CORPUS CENSUS -- a denominator that can be audited.

Why this exists: `tools/sweep_corpus.py' iterates `golden/first8080u/*' and requires BOTH a
`<N>.REL' and `artefacts/<N>.PLI', so it silently reports "programs" as the number of *matched
pairs* it happened to find.  E2E-36/P6 quoted "44 pairs" from a variant of that loop and read the
difference against the 2026-10-18 audit's 41 as three new corpus sources.  It was not three new
sources: `golden/first8080u' holds 44 program DIRECTORIES (45 `find -type d' results including the
batch root), DR's own `summary.txt' says 41 `ok' + 3 `diag', and the three `diag' programs (CALL,
INVERT, MAININVT) have a PRN and NO REL.  A denominator that changes when a helper's file-existence
test changes is not a measurement, so this tool separates the questions instead of collapsing them:

  1 HISTORICAL        every program in DR's batch summary                       (44)
  2 AUTHENTIC        summary=ok, <N>.REL present, sha256 == MANIFEST.sha256     (41)
  3 DR_REJECTED      summary=diag, no REL, DR's PRN carries the diagnostic       (3)
  4 EXACT            my raw .REL == the authenticated golden byte for byte
  5 DIFFERS          my .REL was produced and is not identical (sizes + bytes)
  6 REFUSED          nonzero exit whose message matches a deliberate refusal site
                     in ocaml/lib/*.ml (the "controlled" case: a perimeter edge)
  7 UNEXPECTED       nonzero exit that is NOT a controlled refusal -- a parser
                     exception, an internal Failure, a timeout, or rc==0 with no
                     output file.  This bucket is the one that must stay empty.

Sources are NEVER invented here: a program without `artefacts/<N>.PLI' is reported as NOSRC, and a
DR-rejected program is never counted as an available oracle.  Output is printed compactly and
written as JSON + TSV snapshots that name the compiler commit, the binary's md5 and the argv, so a
later run can be compared against the exact conditions that produced the numbers.

  usage: python3 tools/corpus_census.py [--json OUT.json] [--tsv OUT.tsv] [--check PREV.json]
"""
import argparse, datetime, hashlib, json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.abspath(__file__)) + "/.."
ROOT = os.path.abspath(ROOT)
BATCH = "golden/first8080u"
BIN = os.path.join(ROOT, "ocaml/_build/default/bin/pli80c.exe")
SRC_DIR = os.path.join(ROOT, "artefacts")


def sh(*a):
    return subprocess.run(a, cwd=ROOT, capture_output=True, text=True).stdout.strip()


def refusal_sites():
    """Every deliberate refusal string in the compiler, normalised for substring matching.

    A message is CONTROLLED iff the exact text my compiler printed also exists as a literal in the
    source that produced it.  This is mechanical: it distinguishes 'the perimeter said no' from
    'something downstream fell over', which is the distinction the E2E-36 sweep could not make.
    """
    lits = []
    for dn in ("ocaml/lib", "ocaml/bin"):
        for f in sorted(os.listdir(os.path.join(ROOT, dn))):
            if not f.endswith(".ml"):
                continue
            txt = open(os.path.join(ROOT, dn, f), encoding="utf-8", errors="replace").read()
            lits += re.findall(r'\b(?:failwith|Failure)\s*\(\s*"((?:[^"\\]|\\.)*)"', txt)
            # `error loc "..."` and friends build messages that get prefixed later; keep the body.
            lits += re.findall(r'\berror\s+[^"]*"((?:[^"\\]|\\.)*)"', txt)
    norm = []
    for l in lits:
        l = re.sub(r'\(line %s\)', '(line N)', l)
        norm.append(l.strip()[:70])
    return [n for n in norm if n]


def classify_refusal(msg, lits):
    core = msg
    m = re.search(r'Failure\("(.*)"\)?\s*$', core)
    if m:
        core = m.group(1)
    core = re.sub(r'\(line \d+\)', '(line N)', core)
    core = re.sub(r'\(\d+ chars\)', '(N chars)', core)
    core = re.sub(r'\d+', 'N', core).strip()
    probe = core[:70]
    for l in lits:
        if probe and (probe in l or l in probe):
            return "REFUSED"
    return "UNEXPECTED"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default=os.path.join(ROOT, "spec/census/corpus-census.json"))
    ap.add_argument("--tsv", default=os.path.join(ROOT, "spec/census/corpus-census.tsv"))
    ap.add_argument("--check", metavar="PREV.json",
                    help="rewrite the snapshots, then compare counts against PREV.json")
    ap.add_argument("--verify", metavar="SNAP.json",
                    help="[E2E-37/P2 gate arm] recompute and compare against SNAP.json WITHOUT "
                         "writing anything -- the read-only arm the gate uses, so a gate run "
                         "cannot dirty the corpus snapshot it is supposed to be checking")
    a = ap.parse_args()

    if not os.path.exists(BIN):
        print("corpus census: %s missing -- build first" % BIN, file=sys.stderr)
        return 2
    summary = os.path.join(ROOT, BATCH, "summary.txt")
    hist = []
    for line in open(summary):
        p = line.rstrip("\n").split("\t")
        # CP/M names are 1-8 significant chars; `A' is a real program in this batch and a
        # {2,9} pattern silently drops it -- which is how a census ends up 43/40/14 instead of
        # 44/41/15.  The fix is the filename grammar, not the arithmetic.
        if len(p) >= 2 and re.match(r"^[A-Z][A-Z0-9]{0,7}$", p[0]):
            hist.append((p[0], p[1]))
    manifest = {}
    for line in open(os.path.join(ROOT, BATCH, "MANIFEST.sha256")):
        p = line.split()
        if len(p) == 2:
            manifest[p[1].lstrip("./")] = p[0]
    dirs = sorted(d for d in os.listdir(os.path.join(ROOT, BATCH))
                  if os.path.isdir(os.path.join(ROOT, BATCH, d)))

    lits = refusal_sites()
    rows = []
    for name, verdict in hist:
        d = os.path.join(ROOT, BATCH, name)
        rel = os.path.join(d, name + ".REL")
        src = os.path.join(SRC_DIR, name + ".PLI")
        row = {"name": name, "dr_verdict": verdict, "dir_present": os.path.isdir(d),
               "rel_present": os.path.exists(rel), "src_present": os.path.exists(src),
               "prn_present": os.path.exists(os.path.join(d, name + ".PRN"))}
        row["sha_ok"] = None
        if row["rel_present"]:
            got = hashlib.sha256(open(rel, "rb").read()).hexdigest()
            want = manifest.get("%s/%s.REL" % (name, name))
            row["sha_ok"] = (got == want) if want else None
            row["rel_bytes"] = os.path.getsize(rel)
        if row["dr_verdict"] == "diag" and row["prn_present"]:
            txt = open(os.path.join(d, name + ".PRN"), errors="replace").read()
            hits = [l.strip() for l in txt.splitlines()
                    if re.search(r"(ERROR|NOT [A-Z ]+LABEL|SEVERITY|FATAL)", l, re.I)][:3]
            row["dr_diag"] = hits[:2]
        if not row["src_present"]:
            row["mine"] = "NOSRC"
        elif row["dr_verdict"] != "ok" or not row["rel_present"] or row["sha_ok"] is not True:
            # no authenticated oracle -> do not claim a parity result either way
            row["mine"] = "NO_ORACLE"
            if row["src_present"]:
                out = "/tmp/census-%s.REL" % name
                r = subprocess.run([BIN, src, out], capture_output=True, text=True, timeout=120)
                row["rc"] = r.returncode
                row["emitted"] = os.path.exists(out)
                if os.path.exists(out):
                    os.remove(out)
                if r.returncode != 0:
                    msg = (r.stderr or "").strip().splitlines()
                    row["msg"] = (msg[-1] if msg else "?")[:120]
                    row["dr_also_rejected"] = r.returncode != 0
        else:
            out = "/tmp/census-%s.REL" % name
            try:
                r = subprocess.run([BIN, src, out], capture_output=True, text=True, timeout=120)
            except subprocess.TimeoutExpired:
                row["mine"] = "UNEXPECTED"
                row["msg"] = "timeout"
                r = None
            if r is not None:
                if r.returncode != 0:
                    msg = (r.stderr or "").strip().splitlines()
                    m = (msg[-1] if msg else "?")
                    row["msg"] = m[:160]
                    row["mine"] = classify_refusal(m, lits)
                    if row["mine"] == "UNEXPECTED":
                        row["exc_type"] = m.split(":")[0][:40]
                elif not os.path.exists(out):
                    row["mine"] = "UNEXPECTED"
                    row["msg"] = "rc=0 and no output file"
                else:
                    a_b = open(out, "rb").read()
                    b_b = open(rel, "rb").read()
                    row["mine_bytes"] = len(a_b)
                    if a_b == b_b:
                        row["mine"] = "EXACT"
                    else:
                        row["mine"] = "DIFFERS"
                        row["dr_bytes"] = len(b_b)
                        n = min(len(a_b), len(b_b))
                        row["differing_bytes"] = sum(1 for i in range(n) if a_b[i] != b_b[i]) \
                            + abs(len(a_b) - len(b_b))
                        row["first_diff"] = next((i for i in range(n) if a_b[i] != b_b[i]), None)
                if os.path.exists(out):
                    os.remove(out)
        rows.append(row)

    def names(st):
        return [r["name"] for r in rows if r.get("mine") == st or
                (st == "AUTHENTIC" and r["dr_verdict"] == "ok" and r["sha_ok"] is True and
                 r["rel_present"]) or
                (st == "DR_REJECTED" and r["dr_verdict"] == "diag" and not r["rel_present"]) or
                (st == "HISTORICAL" or (st == "NOSRC" and r["mine"] == "NOSRC"))]

    snap = {
        "tool": "tools/corpus_census.py",
        "generated": datetime.datetime.now().isoformat(timespec="seconds"),
        "git_head": sh("git", "rev-parse", "HEAD"),
        "git_dirty_paths": [l for l in sh("git", "status", "--porcelain").splitlines() if l],
        "binary_md5": hashlib.md5(open(BIN, "rb").read()).hexdigest(),
        "argv": "<BIN> artefacts/<NAME>.PLI /tmp/census-<NAME>.REL",
        "batch": BATCH,
        "counts": {"HISTORICAL": len(hist),
                   "AUTHENTIC": len([r for r in rows if r["dr_verdict"] == "ok"
                                     and r["sha_ok"] is True and r["rel_present"]]),
                   "DR_REJECTED": len([r for r in rows if r["dr_verdict"] == "diag"
                                       and not r["rel_present"]]),
                   "EXACT": len([r for r in rows if r.get("mine") == "EXACT"]),
                   "DIFFERS": len([r for r in rows if r.get("mine") == "DIFFERS"]),
                   "REFUSED": len([r for r in rows if r.get("mine") == "REFUSED"]),
                   "UNEXPECTED": len([r for r in rows if r.get("mine") == "UNEXPECTED"]),
                   "NOSRC": len([r for r in rows if r.get("mine") == "NOSRC"]),
                   "NO_ORACLE": len([r for r in rows if r.get("mine") == "NO_ORACLE"]),
                   "dirs_present": len(dirs),
                   "sha_unverified": len([r for r in rows if r["rel_present"]
                                          and r["sha_ok"] is not True])},
        "rows": rows,
    }
    for st in ("HISTORICAL", "AUTHENTIC", "DR_REJECTED", "EXACT", "DIFFERS", "REFUSED",
               "UNEXPECTED"):
        print("%-12s %3d  %s" % (st, snap["counts"][st], " ".join(names(st))))
    print()
    for r in rows:
        if r.get("mine") == "DIFFERS" or r.get("mine") == "UNEXPECTED":
            print("  %-10s %s" % (r["name"], json.dumps(
                {k: v for k, v in r.items() if k not in ("name", "dir_present", "prn_present")})))
    print("counts: %s" % json.dumps(snap["counts"]))
    print("head %s  binary %s  dirty %d" % (snap["git_head"][:7], snap["binary_md5"][:8],
                                            len(snap["git_dirty_paths"])))
    if snap["counts"]["UNEXPECTED"]:
        print("corpus census: UNEXPECTED bucket is NOT empty -- investigate before quoting "
              "any coverage number", file=sys.stderr)
    if a.verify:
        prev = json.load(open(a.verify))
        bad = []
        if prev["counts"] != snap["counts"]:
            bad.append("counts: %s" % {k: (prev["counts"].get(k), v)
                                       for k, v in snap["counts"].items()
                                       if prev["counts"].get(k) != v})
        pm = {r["name"]: r for r in prev["rows"]}
        for r in rows:
            q = pm.get(r["name"])
            if q is None:
                bad.append("%s: new program not in the snapshot" % r["name"])
                continue
            for k in ("dr_verdict", "sha_ok", "mine", "mine_bytes", "differing_bytes"):
                if q.get(k) != r.get(k):
                    bad.append("%s.%s: snapshot %r, recomputed %r" % (r["name"], k, q.get(k), r.get(k)))
        for n_ in pm:
            if n_ not in {r["name"] for r in rows}:
                bad.append("%s: in the snapshot, not in the batch" % n_)
        if bad:
            print("corpus census: snapshot DRIFT -- %s" % "; ".join(bad[:8]), file=sys.stderr)
            return 1
        print("corpus census: recomputed counts match %s (nothing written)"
              % os.path.relpath(a.verify, ROOT))
        return 1 if snap["counts"]["UNEXPECTED"] else 0
    os.makedirs(os.path.dirname(a.json), exist_ok=True)
    open(a.json, "w").write(json.dumps(snap, indent=1, sort_keys=True) + "\n")
    cols = ["name", "dr_verdict", "rel_present", "sha_ok", "mine", "mine_bytes", "dr_bytes",
            "differing_bytes", "msg"]
    with open(a.tsv, "w") as f:
        f.write("\t".join(cols) + "\n")
        for r in rows:
            f.write("\t".join(str(r.get(c, "")) for c in cols) + "\n")
    print("snapshot -> %s / %s" % (os.path.relpath(a.json, ROOT), os.path.relpath(a.tsv, ROOT)))
    if a.check:
        prev = json.load(open(a.check))
        if prev["counts"] != snap["counts"]:
            print("corpus census: counts CHANGED vs %s: %s" % (a.check, {
                k: (prev["counts"].get(k), v) for k, v in snap["counts"].items()
                if prev["counts"].get(k) != v}), file=sys.stderr)
            return 1
        print("corpus census: counts identical to %s" % a.check)
    return 0


if __name__ == "__main__":
    sys.exit(main())
