#!/usr/bin/env python3
"""[E2E-37/P3] Attach verified manual citations to COVERAGE.tsv rows.

The cite strings below were read out of the banked OCR text
(spec/manuals/PL1-80_Language_Manual_Dec80.txt.gz) and each one is checked by
tools/coverage_check.py against the printed-page window it claims, so this script cannot
silently invent a page.  Run it once per batch of cites; it is idempotent.
"""
import os, sys, re

PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "spec/COVERAGE.tsv")

# id -> manual_ref  (format: `s<sec> p.<printed page> "<phrase verbatim from the OCR>"')
CITE = {
    "DECL.STATIC_INITIAL":
        'p31:6.2=only STATIC variables can have the INITIAL attribute',
    "DECL.RECURSIVE":
        'p31:6.3=AUTOMATIC storage is statically allocated',
    "DECL.BASED_TYPE_MATRIX":
        'p31:6.4=The format for the BASED attribute is',
}


def main():
    lines = [l.rstrip("\n") for l in open(PATH) if not l.startswith("#")]
    hdr = lines[0].split("\t")
    for name in ("id", "manual_ref", "contract"):
        if name not in hdr:
            print("coverage_manual_refs: no %r column in %s" % (name, PATH), file=sys.stderr)
            return 1
    i_id, i_ref, i_con = hdr.index("id"), hdr.index("manual_ref"), hdr.index("contract")
    n = 0
    rows = [l.split("\t") for l in lines[1:]]
    for r in rows:
        if r[i_id] in CITE:
            ref = CITE[r[i_id]]
            if r[i_ref] != ref:
                r[i_ref] = ref
                r[i_con] = re.sub(r" -- documented, s\d.*$", "", r[i_con]) + " -- documented, " + ref
                n += 1
    with open(PATH, "w") as f:
        f.write("# spec/COVERAGE.tsv -- language-coverage inventory.  Schema and the meaning of\n"
                "# every column: spec/COVERAGE-SCHEMA.md.  Validated on every gate run by\n"
                "# tools/coverage_check.py.  No claim of complete language coverage is made or implied.\n")
        f.write("\t".join(hdr) + "\n")
        for r in rows:
            f.write("\t".join(r) + "\n")
    print("coverage_manual_refs: %d rows cite the manual" % n)
    return 0


if __name__ == "__main__":
    sys.exit(main())
