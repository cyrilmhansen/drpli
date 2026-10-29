# E2E-48/P2c RETIRE round — RESULTS (measured 2026-10-30)

Ordering (PROTOCOL #1): predictions committed at `630e9be` (RETIRE-HYPOTHESES.md +
RETIRE-BASELINE-MINE.txt) BEFORE this oracle call; `git diff 630e9be HEAD --` over those two
files and both probes was empty (0 lines) at run time. Oracle:
`PLI_SRC=probes python3 oracle/batch.py E46K1 E46K3 --tag e48p2retire --switches '$L$D'`
-> **2 ok / 2**, both produced `.REL` (128 bytes each); goldens in `golden/e48p2retire/`
(NEW tag dir; golden/e48p1 and golden/e48p2c untouched).

| # | prediction (from committed goldens) | measured verdict of DR | result |
|---|---|---|---|
| P-K1 | ACCEPT; store `21 *D(0002) / 11 *D(0000) / 3E 0E / 06 02 / ?SMCVM`; DEF-DATA-SIZE 0013 | ok, .REL 128 bytes; WHOLE FILE byte-identical to my object | **HIT** |
| P-K3 | ACCEPT; 15-byte §2.4 head `21 *D(0002) / EB / 21 *D(0000) / 3E 02 / ?SCVCM / C2 <chain>` with the [C309] skip filled to the next statement (the ?STOPX epilogue at 001B); `k = 1` = `LXI H,1 / SHLD`; DEF-DATA-SIZE 0015 | ok, .REL 128 bytes; WHOLE FILE byte-identical | **HIT** |
| P-G1 | 2 ok / 2, no refusals | 2 ok / 2 | **HIT** |

## Consequences (the rows' own retirement procedure)

* E46K1 and E46K3 are RETIRED from the negative panel and PROMOTED to byte-exact specimens:
  DR's verdict on both shapes is now a MEASURED acceptance, and my whole objects match
  (`cmp` zero-diff on 128/128 bytes each). The INVENTORY rows' claim `NEITHER verdict is known`
  is superseded for these two programs by this experiment; `--update-inventory` rewrites them.
* §1 P3 (spelling-invariance) and §2.4 (TEST member-LEFT head) are now corroborated OUTSIDE
  their own banks: a record with a second member (`nxt fixed bin(15)`), cap 14 instead of 30,
  literal `2` instead of `3`, and an IF-then with no ELSE all sit on the same law and hit.
* Negative panel is now 182 rows; byte panel gains 11 specimens (E48C1..C9 + these two).
  The FULL gate at this HEAD must measure 1109 byte-exact / 0 fail and 182/182 refused --
  this session re-measures and reports, replacing the inherited 1107/184 expectation.
