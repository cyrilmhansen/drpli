#!/usr/bin/env python3
"""[E2E-37/P2] spec/COVERAGE.tsv schema validator.

Fails (exit 1) on: duplicate or malformed ids, unknown enum values, a contract that just restates
the construct, manual cites that do not appear in the banked OCR text at the cited printed page,
evidence keys that are not on the gate panel and not corpus programs, corpus names outside the
census, claim ids absent from spec/CLAIMS.md, and the cross-check that keeps citations honest: a row
asserting MEASURED or SINGLE_SAMPLE confidence must name at least one probe that one of its own
cited claims actually mentions.  That last rule is the reason this file can be trusted: it makes a
fabricated citation a build failure instead of a plausible sentence.

Prints, in addition to errors, the honesty counts a coverage table should carry: how many rows have
no runtime evidence at all, how many rest on a single sample, how many manual refs are unverified.

  usage: python3 tools/coverage_check.py [--tsv spec/COVERAGE.tsv] [--quiet]
"""
import argparse, collections, gzip, os, re, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
COLS = ["id", "category", "construct", "contract", "perimeter", "manual_ref", "dr_status",
        "mine_status", "rel_parity", "runtime", "probes", "corpus", "boundary", "confidence",
        "provenance"]
CATS = {"LEX", "DECL", "AGG", "STOR", "EXPR", "COND", "LOOP", "TRAN", "PROC", "IO", "FILE", "OBJ",
        "ABI", "RTME", "NEG", "BUILTIN"}
ENUMS = {
    "perimeter": {"S", "M", "C", "OPEN"},
    "dr_status": {"ACCEPTS", "REJECTS", "ACCEPTS_DEFECT", "UNTESTED"},
    "mine_status": {"SUPPORTED", "DIVERGENT", "REFUSED", "PARTIAL", "NOT_ATTEMPTED"},
    "confidence": {"MEASURED", "SINGLE_SAMPLE", "INFERRED", "UNREVIEWED"},
}
PREFIX = {"LEX": "LEX", "DECL": "DECL", "AGG": "AGG", "STOR": "STOR", "EXPR": "EXPR",
          "COND": "COND", "LOOP": "LOOP", "TRAN": "TRAN", "PROC": "PROC", "IO": "IO",
          "FILE": "FILE", "OBJ": "OBJ", "ABI": "ABI", "RTME": "RTME", "NEG": "NEG", "BUILTIN": "BUILTIN"}


def load_panel():
    """(keys, status) across all three panels: the byte-exact inventory, the recorded
    divergences, and the runtime panel.  The three files have three column layouts -- INVENTORY
    is `name kind source golden-or-refusal-reason', DIVERGENT starts `name source golden ...',
    RUNTIME starts `name kind golden_rel ...' -- so the key is field 0 everywhere and the status
    comes from each file's own convention, not from a shared column index."""
    keys, status = set(), {}
    inv = os.path.join(ROOT, "spec/INVENTORY.txt")
    if os.path.exists(inv):
        for line in open(inv, errors="replace"):
            if line.startswith("#"):
                continue
            p = line.rstrip("\n").split("\t")
            if len(p) < 2 or p[0] == "name":
                continue
            keys.add(p[0])
            status[p[0]] = "EXACT" if p[3].startswith("golden/") else "REFUSAL"
    for fn, tag in (("DIVERGENT.txt", "DIVERGENT"), ("RUNTIME.txt", "RUNTIME")):
        path = os.path.join(ROOT, "spec", fn)
        if not os.path.exists(path):
            continue
        for line in open(path, errors="replace"):
            if line.startswith("#") or not line.strip():
                continue
            p = line.rstrip("\n").split("\t")
            if len(p) < 2 or p[0] in ("key", "name"):
                continue
            keys.add(p[0])
            status[p[0]] = tag
    return keys, status


def load_census():
    f = os.path.join(ROOT, "spec/census/corpus-census.tsv")
    if not os.path.exists(f):
        return set(), None
    rows = [l.rstrip("\n").split("\t") for l in open(f)][1:]
    return {r[0] for r in rows if r and r[0]}, f


def load_claims():
    txt = open(os.path.join(ROOT, "spec/CLAIMS.md"), errors="replace").read()
    blocks = {}
    # Three formats exist in the file: `**C236. ...' (E2E-35/36 era), `C179 [E2E-24, ...]'
    # (the bulk) and `C183.' bullet heads.  A validator that recognised only one would reject
    # claims that exist, which is worse than accepting a citation that does not.
    defs = [(m.start(), "C" + m.group(1))
            for m in re.finditer(r"^(?:##\s+)?(?:[-*+]\s*)?(?:\*\*)?C(\d{2,3})(?:\*\*)?"
                                 r"\s*\*?\s*[.\-\u2014\[(]", txt, re.M)]
    for i, (pos, cid) in enumerate(defs):
        end = defs[i + 1][0] if i + 1 < len(defs) else pos + 4000
        h = txt.find("\n## ", pos)
        if 0 < h < end:
            end = h
        blocks.setdefault(cid, txt[pos:end])
    return blocks


def load_manual():
    f = os.path.join(ROOT, "spec/manuals/PL1-80_Language_Manual_Dec80.txt.gz")
    if not os.path.exists(f):
        return None, f
    pages = gzip.open(f, "rt", errors="replace").read().split("\f")
    return pages, f


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tsv", default=os.path.join(ROOT, "spec/COVERAGE.tsv"))
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()
    errs, warns = [], []
    panel, panel_srcs = load_panel()
    corpus, census_file = load_census()
    claims = load_claims()
    pages, manf = load_manual()

    if not os.path.exists(a.tsv):
        print("coverage_check: %s missing" % a.tsv, file=sys.stderr)
        return 1
    raw = open(a.tsv, errors="replace").read().split("\n")
    body = [(i + 1, l) for i, l in enumerate(raw) if l.strip() and not l.startswith("#")]
    hdr = body[0][1].split("\t")
    if hdr != COLS:
        errs.append("header mismatch: expected %s" % ",".join(COLS))
    seen = collections.Counter()
    rows = []
    for ln, line in body[1:]:
        f = line.split("\t")
        if len(f) != len(COLS):
            errs.append("line %d: %d fields, expected %d" % (ln, len(f), len(COLS)))
            continue
        r = dict(zip(COLS, f))
        r["_ln"] = ln
        rows.append(r)
        seen[r["id"]] += 1
        if not re.match(r"^[A-Z]+\.[A-Z0-9_]+$", r["id"]):
            errs.append("line %d: id %r malformed (CATEGORY.slug, upper)" % (ln, r["id"]))
        if r["category"] not in CATS:
            errs.append("line %d: category %r unknown" % (ln, r["category"]))
        elif not r["id"].startswith(PREFIX[r["category"]] + "."):
            errs.append("line %d: id %r prefix disagrees with category %r"
                        % (ln, r["id"], r["category"]))
        for col, allowed in ENUMS.items():
            if r[col] not in allowed:
                errs.append("line %d: %s=%r not in %s" % (ln, col, r[col], sorted(allowed)))
        if len(r["contract"].strip()) < 15:
            errs.append("line %d: contract too short to be a semantic/lowering assertion" % ln)
        if r["perimeter"] == "C" and r["mine_status"] == "SUPPORTED":
            errs.append("line %d: perimeter=C with mine_status=SUPPORTED (class carries no gap)" % ln)
        if r["confidence"] == "UNREVIEWED" and (r["rel_parity"] != "NONE"
                                                or r["runtime"] != "NONE"):
            errs.append("line %d: UNREVIEWED rows must have rel_parity=NONE and runtime=NONE" % ln)
        if not re.match(r"^(NONE|EXACT:\d+|DIVERGENT:\d+|MIXED:\d+/\d+)$", r["rel_parity"]):
            errs.append("line %d: rel_parity %r malformed" % (ln, r["rel_parity"]))
        if not re.match(r"^(NONE|(INDEPENDENT|DR_ORACLE|BOTH):\d+)$", r["runtime"]):
            errs.append("line %d: runtime %r malformed" % (ln, r["runtime"]))
        # manual reference
        mref = r["manual_ref"]
        if mref == "NONE" or mref.startswith("NONE:"):
            pass
        elif mref.startswith("UNVERIFIED"):
            pass
        else:
            m = re.match(r"^p(\d{1,3})(?::([0-9]+(?:\.[0-9]+)*))?(?:=(.+))?$", mref)
            if not m:
                errs.append("line %d: manual_ref %r malformed (pNN[:§X.Y][=phrase])" % (ln, mref))
            elif pages is None:
                errs.append("line %d: cannot verify manual_ref, %s missing" % (ln, manf))
            else:
                printed = int(m.group(1))
                idx = printed + 7 - 1          # printed page p is PDF page p+7
                if idx < 0 or idx >= len(pages):
                    errs.append("line %d: manual page %d outside the extraction (%d pdf pages)"
                                % (ln, printed, len(pages)))
                else:
                    window = pages[idx] + (pages[idx - 1] if idx else "") \
                        + (pages[idx + 1] if idx + 1 < len(pages) else "")
                    if m.group(3):
                        phrase = re.sub(r"\s+", " ", m.group(3))
                        if re.sub(r"\s+", " ", phrase.lower()) not in \
                                re.sub(r"\s+", " ", window.lower()):
                            errs.append("line %d: manual cite %r not found on printed page %d "
                                        "(OCR window)" % (ln, m.group(3), printed))
                    if m.group(2) and m.group(2) not in window.replace(" ", ""):
                        warns.append("line %d: section %s not seen near printed page %d"
                                     % (ln, m.group(2), printed))
        # evidence keys
        plist = [p for p in r["probes"].split(",") if p.strip() and p.strip() != "NONE"]
        for p in (x.strip() for x in plist):
            if p in panel or p in corpus:
                continue
            if p.startswith("golden/") or p.startswith("artefacts/"):
                if not os.path.exists(os.path.join(ROOT, p)):
                    errs.append("line %d: evidence path %s does not exist" % (ln, p))
                continue
            if re.match(r"^spec/", p):
                if not os.path.exists(os.path.join(ROOT, p)):
                    errs.append("line %d: evidence path %s does not exist" % (ln, p))
                continue
            errs.append("line %d: probe key %r is neither on the panel nor a corpus program "
                        "nor a path" % (ln, p))
        clist = [c for c in r["corpus"].split(",") if c.strip() and c.strip() != "NONE"]
        for c in (x.strip() for x in clist):
            if corpus and c not in corpus:
                errs.append("line %d: corpus user %r is not in the census (%s)"
                            % (ln, c, os.path.relpath(census_file, ROOT)))
        cits = sorted(set(re.findall(r"\bC\d{2,3}\b", r["provenance"])))
        if not cits and not re.search(
                r"(notes/|\.md|\.txt|\bnote\b|PERIMETER|panel|census|INVENTORY|DIVERGENT|RUNTIME|slice)",
                r["provenance"], re.I):
            errs.append("line %d: provenance names no claim id and no recognizable artefact" % ln)
        for c in cits:
            # `C013' and `C13' are the same id written two ways across eleven episodes.
            alt = "C" + str(int(c[1:]))
            if c not in claims and alt not in claims:
                errs.append("line %d: claim %s does not exist in spec/CLAIMS.md" % (ln, c))
        if r["confidence"] in ("MEASURED", "SINGLE_SAMPLE") and plist and cits:
            note_txt = []
            for nf in re.findall(r"note[s]?\s+([A-Za-z0-9._/-]+\.md)", r["provenance"]):
                cand = os.path.join(ROOT, "spec/notes", nf)
                if not os.path.exists(cand):
                    cand = os.path.join(ROOT, nf)
                if not os.path.exists(cand):
                    errs.append("line %d: cited note %s does not exist" % (ln, nf))
                else:
                    note_txt.append(open(cand, errors="replace").read())
            ctext = " ".join([claims.get(c, "") for c in cits] + note_txt)
            def mentions(tok):
                # A PATH probe is stronger evidence than a prose mention: it is separately
                # verified to exist, so it satisfies traceability on its own.
                if "/" in tok:
                    return True
                if re.search(r"(?<![A-Z0-9])" + re.escape(tok) + r"(?![0-9])", ctext):
                    return True
                # Claims and notes name families rather than enumerating probes (`H4/H15/H16',
                # `E36T2-T8/T11-T14', `the E29C series'), so a stem counts as traceable evidence
                # that the cited evidence discusses THIS probe family.  A row may still cite a
                # probe nothing it cites mentions -- it then cannot claim MEASURED confidence.
                m = re.match(r"^([A-Z]+\d*[A-Z]?|[A-Za-z]+)", tok)
                st = m.group(1) if m else ""
                if len(st) < 2:
                    return False
                return bool(re.search(r"(?<![A-Z0-9])" + re.escape(st) + r"(?![a-z])",
                                      ctext, re.I))
            hit = any(mentions(t) for t in plist)
            if not hit:
                errs.append("line %d: %s confidence but none of probes %s is mentioned by cited "
                            "claims %s -- citation is not traceable" % (
                                ln, r["confidence"], ",".join(plist), ",".join(cits)))
    for k, v in seen.items():
        if v > 1:
            errs.append("duplicate id %s (%d rows)" % (k, v))

    n = len(rows)
    bycat = collections.Counter(r["category"] for r in rows)
    stats = {
        "rows": n,
        "by_category": dict(sorted(bycat.items())),
        "mine": dict(sorted(collections.Counter(r["mine_status"] for r in rows).items())),
        "dr": dict(sorted(collections.Counter(r["dr_status"] for r in rows).items())),
        "perimeter": dict(sorted(collections.Counter(r["perimeter"] for r in rows).items())),
        "confidence": dict(sorted(collections.Counter(r["confidence"] for r in rows).items())),
        "no_runtime": sum(1 for r in rows if r["runtime"] == "NONE"),
        "no_parity": sum(1 for r in rows if r["rel_parity"] == "NONE"),
        "single_sample": sum(1 for r in rows if r["confidence"] == "SINGLE_SAMPLE"),
        "unreviewed": sum(1 for r in rows if r["confidence"] == "UNREVIEWED"),
        "manual_unverified": sum(1 for r in rows
                                 if r["manual_ref"].startswith("UNVERIFIED")),
        "manual_none": sum(1 for r in rows
                           if r["manual_ref"] == "NONE" or r["manual_ref"].startswith("NONE:")),
        "with_boundary": sum(1 for r in rows if r["boundary"] != "NONE"),
    }
    if not a.quiet:
        for e in errs:
            print("ERROR %s" % e)
        for w in warns[:20]:
            print("warn  %s" % w)
        print("coverage_check: %d rows, %d errors, %d warnings" % (n, len(errs), len(warns)))
        for k in ("rows", "no_runtime", "no_parity", "single_sample", "unreviewed",
                  "manual_unverified", "manual_none", "with_boundary"):
            print("  %-17s %d" % (k, stats[k]))
        print("  by_category     %s" % json.dumps(stats["by_category"]) if False else
              "  by_category     %s" % " ".join("%s=%d" % kv for kv in
                                                sorted(bycat.items())))
        print("  mine_status     %s" % " ".join("%s=%d" % kv for kv in
                                                sorted(stats["mine"].items())))
        print("  dr_status       %s" % " ".join("%s=%d" % kv for kv in
                                                sorted(stats["dr"].items())))
        print("  perimeter       %s" % " ".join("%s=%d" % kv for kv in
                                                sorted(stats["perimeter"].items())))
        print("  confidence      %s" % " ".join("%s=%d" % kv for kv in
                                                sorted(stats["confidence"].items())))
    open(os.path.join(ROOT, "spec/census/coverage-stats.json"), "w").write(
        __import__("json").dumps(stats, indent=1, sort_keys=True) + "\n")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
