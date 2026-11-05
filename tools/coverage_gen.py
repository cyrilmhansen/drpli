#!/usr/bin/env python3
"""OBSOLETE — this script is a fail-closed stub and writes NOTHING.

The former `coverage_gen.py` held a hard-coded E2E-36-era snapshot of the coverage
table and ended by replacing `spec/COVERAGE.tsv` with `os.replace()`.  Running it
"as the stats' own write path" during the E2E-52/P3-8 close (commit 0cf0688) CLOBBERED
the scientific ledger from 140 contracts down to its stale 71 -- the repair is recorded
in `LEARNINGS.md` (section "P3-8 DOCS CLOSE + A LEDGER-CLOBBER REPAIR") and in
`spec/lab-evidence/e2e52-p3/RESULTS.md` section 7.

The destructive implementation is deliberately NOT preserved on any executable path.

What the tree actually uses:
  * spec/COVERAGE.tsv            the maintained contract ledger (hand-edited, reviewed);
  * spec/COVERAGE-IDS.txt        the registered contract-ID manifest enforced by the
                                 validator's exact-set identity invariant;
  * tools/coverage_check.py      the validator, and the ONLY writer of the derived
                                 statistics spec/census/coverage-stats.json;
  * spec/COVERAGE-SCHEMA.md      schema and maintenance rules for all of the above.

If you believe you need to regenerate the ledger: you do not.  Edit
`spec/COVERAGE.tsv` (and, for a genuinely new contract, `spec/COVERAGE-IDS.txt`) as an
explicit reviewed change, then run `python3 tools/coverage_check.py`.
"""
import sys

def main():
    print(__doc__.strip(), file=sys.stderr)
    print("coverage_gen: REFUSING to run -- obsolete generator; it must never write the "
          "scientific ledger.  Exit status 2; no file was created, opened for writing, "
          "renamed, truncated or deleted.", file=sys.stderr)
    return 2

if __name__ == "__main__":
    sys.exit(main())
