#!/usr/bin/env python3
"""Triage the my-gap negative panel by cost, not by specimen count.  [ARCH-0 §10
in spirit: generate the table from artifacts rather than asserting it.]

For every negative DR COMPILED (golden/negpanel1/<NGxx>/), read DR's own listing
and extract:
  * CODE SIZE        -- a proxy for how much lowering the construct needs
  * the RTL routines DR calls, and which of those MY build has never emitted
  * how many distinct CALL targets / reloc-bearing operands appear
The last one is the expensive signal: a construct whose lowering uses only
routines I already emit is a LOWERING job; one that needs a routine I have never
emitted also needs its ABI discovered (argument convention, side effects, when
it is called), which is a different order of work and the reason several "small"
specimens turned out not to be (named FILE I/O: ?OIOOP/?SIOOP/?SLCTS).

Usage: tools/neg_triage.py [--json]
"""
import collections, json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CG = os.path.join(ROOT, "ocaml", "lib", "codegen.ml")

def my_routines():
    """RTL names this build has EMITTED, taken from its own .REL output.

    NOT a grep of codegen.ml.  My first version grepped `call_ext st "?NAME"'
    and then any ?NAME string literal; both were wrong in opposite directions --
    call_ext missed ?START/?STOPX (pushed as chain items from emit_program) and
    string literals miss names that arrive through tables, while both also count
    names that appear only in a refusal MESSAGE.  The authoritative answer to
    "have I ever emitted this routine?" is to compile every gate specimen and
    read the symbol field of the LINK-CHAIN-EXT records my own output produced.
    That took 390 compiles and ~40s, and it changed the ranking: ?FD44M, the
    routine corpus program A actually needs, turned out to be something this
    build already emits (R3033), i.e. A is a lowering-only gap, not a runtime one.

    Set is cached in golden/.my_routines.json; rebuild with --refresh.
    """
    cache = os.path.join(ROOT, "golden", ".my_routines.json")
    if "--refresh" not in sys.argv and os.path.exists(cache):
        return set(json.load(open(cache)))
    import e2e_gate as G
    import reldump
    cc = os.path.join(ROOT, "ocaml", "_build", "default", "bin", "pli80c.exe")
    found = set()
    n = 0
    for name, (src, _gold) in G.SPECIMENS.items():
        out = os.path.join(ROOT, "build", "triage_%s.REL" % name)
        r = subprocess.run([cc, src, out], capture_output=True, text=True)
        if r.returncode != 0 or not os.path.exists(out):
            continue
        n += 1
        items, _ = reldump.decode(out, verbose=False)
        for it in items:
            if it[1] == LINK_EXT and isinstance(it[4], str):
                found.add(it[4])
        os.remove(out)
    print(f"(emitted-routine set built from {n} compiled specimens)",
          file=sys.stderr)
    os.makedirs(os.path.dirname(cache), exist_ok=True)
    json.dump(sorted(found), open(cache, "w"))
    return found


LINK_EXT = "LINK-CHAIN-EXT"

def parse_prn(path):
    t = open(path, errors="replace").read()
    code = None
    m = re.search(r"CODE SIZE = ([0-9A-F]+)", t)
    if m: code = int(m.group(1), 16)
    rts = set(re.findall(r"CALL\s+(\?[A-Z0-9]+)", t))
    calls = len(re.findall(r"CALL\s+", t))
    # reloc-bearing operands in the generated code: *S(/*A(/*L markers
    relocs = len(re.findall(r"\*\s*[SAL]\(", t))
    labels = len(re.findall(r"^\s*\d+ [acl] [0-9A-F]{4}", t, re.M))
    return code, rts, calls, relocs, labels

def main():
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    import e2e_gate as G
    mine = my_routines()
    mp = dict(l.split() for l in open(os.path.join(ROOT, "negsrc/MAP.txt")))
    rows = []
    for ng, name in sorted(mp.items()):
        cat = G.NEG_META[name][0]
        d = os.path.join(ROOT, "golden", "negpanel1", ng)
        prn = os.path.join(d, ng + ".PRN")
        rel = os.path.exists(os.path.join(d, ng + ".REL"))
        code, rts, calls, relocs, labels = (None, set(), 0, 0, 0)
        if os.path.exists(prn):
            code, rts, calls, relocs, labels = parse_prn(prn)
        new = sorted(rts - mine)
        rows.append(dict(ng=ng, name=name, cat=cat, rel=rel, code=code,
                         routines=sorted(rts), new=new, calls=calls,
                         relocs=relocs))
    gaps = [r for r in rows if r["cat"] == "my-gap"]
    refs = [r for r in rows if r["cat"] == "dr-refuses"]
    if "--json" in sys.argv:
        import json
        json.dump(rows, sys.stdout, indent=1)
        return
    def key(r):
        return (len(r["new"]), r["code"] if r["code"] is not None else 9999,
                r["name"])
    gaps.sort(key=key)
    print(f"panel {len(rows)}: {len(gaps)} my-gap, {len(refs)} dr-refuses")
    print(f"my build emits {len(mine)} distinct RTL routines")
    print()
    print(f"{'negative':34} {'code':>5} {'calls':>5} {'reloc':>5}  new RTL needed")
    for r in gaps:
        cs = f"{r['code']:04X}" if r["code"] is not None else "?"
        print(f"{r['name']:34} {cs:>5} {r['calls']:>5} {r['relocs']:>5}  "
              f"{', '.join(r['new']) if r['new'] else '-- lowering only --'}")
    fam = collections.Counter()
    for r in gaps:
        fam["new-RTL" if r["new"] else "lowering-only"] += 1
    print("\nsummary:", dict(fam))
    multi = collections.Counter()
    for r in gaps:
        for n in r["new"]:
            multi[n] += 1
    print("routines that would newly be needed (count = gap specimens sharing it):")
    for n, c in multi.most_common():
        print(f"   {n:12} used by {c} specimen(s)")

main()
