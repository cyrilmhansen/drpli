# E2E-51/P1 — PLAN (FIXED BINARY variable-divisor DIVISION; OPERATOR-AUTHORIZED 2026-11-04)

Objective: determine which FIXED BINARY division forms DR PL/I-80 v1.4 accepts and how it
compiles them, reproduce accepted forms byte-exactly, and keep every refusal evidence-backed.
Motivating gap: HAMM-00 rev1 (`codegen: DIV by non-constant [TBD]`).

Predecessor boundary: FC-01 corpus CLOSED at HEAD `ac68352`; ledger ends **C352**; no prior
round touched binary var-divisor DIV.

Existing witnesses REUSED as controls (never re-derived): [C089] MOD parking (variable divisor
`PUSH H / LHLD d / POP D`); P080A (`golden/probe48`) constant-divisor DIV ladder, mine
byte-exact; [C141] helper-result parking laws P1–P12; [C079] numeric PUT chain + width law +
1-byte bin(p<=7) storage + `?IN20N`; [C072] equality encoding; golden/f6probe/F005.REL = the
UNCLAIMED DR object for `z = a / b` (binary, accepted: LHLD a/PUSH H/LHLD b/POP D/CALL
?ID22N/SHLD z, CODE 0017, DATA 0006). NG16/17/19 are DEC witnesses — NOT transferable.
Survey of `artefacts/`: every var-divisor `/` there is DEC or FLOAT; no historical binary
witness beyond F005. No negative/INVENTORY row pins the DIV-non-constant refusal.

## The bank — 12 probes `probes/E51*.PLI`, shared DECL `dcl a fixed, b fixed, c fixed, z fixed;`
(P080A/F005 family; plain FIXED = 16-bit binary; predicted DATA SIZE 0008, E51K 0009), no PUT
tail except E51H, no explicit `stop;` — exactly the F005/P080A frame. Rows A..L: var/var (F005
reproduction control), literal-num, compound-num, compound-den, chained, div-left-of-add,
div-right-of-add, div-in-PUT, div-in-condition, unary-minus dividend, bin(7) 1-byte divisor,
constant-divisor control (tied to P080A).

## Procedure (strict order, house method)

1. Pre-register: `mkprobes.py` + generated probes + `HYPOTHESES.md` + `BASELINE-MINE.txt`
   COMMITTED BEFORE any DR call. Prediction SHA proven by `git log --format=%h -- probes/E51A.PLI`.
2. Oracle: ONE grouped campaign
   `PLI_SRC=probes timeout 900 python3 oracle/batch.py E51A E51B E51C E51D E51E E51F E51G E51H E51I E51J E51K E51L --tag e51p1 --switches '$L$D'`.
   `golden/e51p1` must NOT exist before the call; never `--reuse`; a timeout is preserved and
   classified, never retried indefinitely.
3. Inspect every `.PRN` (diagnostics) and complete `.REL` (tools/reldump.py; whole-file cmp per
   PROTOCOL #6). Classify each row `dr-refuses` / `my-gap` / `unmeasured`. RESULTS.md keeps
   every MISS verbatim (PROTOCOL #2). Commit goldens + RESULTS together before any compiler change.
4. Arms by measured MECHANISM only; each arm: whole-file byte verification of new goldens +
   regression sweep + FULL gate rc=0; independently committed. dr-refuses rows are never
   implemented.
5. Closure: claims from **C353** derived ONLY from RESULTS §2; SPECIMENS registration in
   `tools/e2e_gate.py`; sanctioned `--update-inventory`; census re-snapshot; COVERAGE rows;
   HAMM-00 rev1 rerun UNEDITED if its forms are byte-covered (functional evidence stays
   separate from byte-parity evidence). **STOP after P1** — no P2/LOAN2/CREATE/broad refactor.

Constraints: no push; operator `handoff.config.json` never staged/cleaned/reverted; goldens and
ignored evidence never laundered; explicit timeouts everywhere.
