# PL/I-80 corpus audit (2026-10-17, post-E2E-4) — ANALYSIS ONLY

Compiler sweep of all 44 corpus sources (artefacts/*.PLI) with the
current OCaml build; first-blocker + downstream feature map. Sweep
output banked: see table below. DEMO = 1/44 fully byte-exact today.

## First-blocker distribution (43 blocked)
| blocker | count | programs |
|---|---|---|
| FLOAT decl | 8 | A DTEST FDTEST FLTPOLY INVERT MAININVT SAMPLE TEST |
| FIXED DEC decl | 6 | DECPOLY LOAN1 ANNUITY ENTER REPORT UPDATE(+DEC) ... |
| FILE decl | 12 | COPY COPYLPT CREATE EXPR1 EXPR2 KEYFILE RETRIEVE REVERT NETWORK MPMCALLA MPMCALLB (+ENTER) |
| POINTER/BASED | 4 | ALLTST DIOCALLS DIOCOPY REVERSE |
| BIT(1) decl | 3 | DIORAND LOAN2 UPDATE |
| DO WHILE/REPEAT/no-TO | 4 | DFACT FFACT IFACT RFACT |
| PUT form only | 2 | ACK (multi-item numeric GET/PUT), SAMPLE (behind FLOAT too) |
| statement kind (Sdowhile + SKIP-kw put) | 2 | OPTIMIST FSCAN |
| parser gap (entry-style decls) | 1 | CALL |
| label-variable / computed GOTO | 1 | LABELS |
NOTE: first blockers understate; most programs stack several needs.

## Feature frequency across the corpus (grep-verified)
- DO WHILE / UNTIL / REPEAT / bare DO;: 31/44  (bounded DO: 16/44 ✓ supported since E2E-4)
- FILE decl + OPEN/READ/WRITE (any 'file'): 20/44
- FLOAT (binary) : 13/44
- ENTRY-style/external decls: 11/44
- fixed-decimal: ~7; BIT(1)/bit-literals '1'b: 3+ (COPY loops use '1'b!)
- numeric PUT/GET (list items int/dec): ~20
- PUT with bare SKIP keyword ('put skip list(...)'): ACK OPTIMIST FSCAN ...
- multi-item GET LIST: ACK + all GET users
- varying: ~25 ; concat ||: ~6 ; structures: 2 ; based-pointer: 4

## Unlock calculus (what becomes EXACT with each candidate milestone)
- Loop-verbs + numeric I/O slice (DO WHILE/REPEAT/bare DO; '1'b cond;
  PUT SKIP-kw; PUT LIST(int); GET LIST(int, multi-item)) directly
  unblocks: OPTIMIST, RFACT, DFACT?, ACK (verify no hidden needs).
  Widest reuse-per-effort; every later program loops and prints numbers.
- Sequential FILE slice (FILE decl, OPEN stream/output, READ INTO /
  WRITE FROM (varying), EOF/condition bits, CLOSE?) unblocks COPY,
  COPYLPT?, RETRIEVE?, CREATE, REVERSE? — biggest count cluster (12+)
  but needs oracle harness work (file transfer per-run disks) and
  heavy $C probe series. COPY also needs the loop-verbs slice first.
- FIXED DEC slice: DECPOLY, LOAN1, ANNUITY class (pool layout already
  banked E2E-2c; arithmetic + editing new).
- FLOAT slice: deepest (RTL op family, formatting, 13 programs).
- ENTRY/multi-module (11): cross-object linkage = LINK-80 integration
  territory; CALL/DTEST/FDTEST etc. — recommend explicit DEFERRAL
  decision (perimeter), not silent drift.
- POINTER/BASED (4), label-variables/computed GOTO (2): deep semantics,
  low count — recommend PERIMETER CUT for byte-parity corpus goal.

## Recommended next milestones (ordered)
1. E2E-5 'loop verbs & numeric console': DO WHILE/REPEAT/UNTIL/bare DO;
   '1'b and other cond forms; bare SKIP in PUT; numeric PUT LIST int;
   multi-item/numeric GET LIST. Target corpus wins: OPTIMIST, RFACT,
   ACK (+DFACT if DEC-lite feasible). ~8-12 micro-probes, est.
   250-450 LoC. Risk MEDIUM (chains exist; shapes unknown).
2. E2E-6 'sequential file I/O': COPY as acceptance centerpiece.
   Requires: per-run disk file staging in oracle harness (cpmtools
   already supports), OPEN/READ/WRITE/EOF $C battery. Risk HIGH,
   payoff: 6-12 programs incl. COPY/CREATE/RETRIEVE family.
3. E2E-7 'FIXED DEC data & editing' (LOAN1/DECPOLY/ANNUITY) —
   decisions on FLOAT vs DEC order after seeing 5/6 unlock rates.
DECISIONS NEEDED from user: (a) POINTER/BASED + label-vars: cut from
byte-parity corpus? (b) ENTRY/multi-module: defer wholesale?
Evidence discipline unchanged: probe -> $C/$S -> byte parity -> COM +
raw console equality -> fail-loud outside proven shapes.
## Raw sweep (pli80c, per program, 2026-10-17)
A          TYPE FLOAT BINARY(24,0)
ACK        BLOCK codegen: PUT form not in E2E-3a subset [TBD] (line 10)")
ACKTST     TYPE FIXED DECIMAL(6,0)
ALLTST     BLOCK codegen: declared variable kind not in supported subset [TBD]: POINTER")
ANNUITY    TYPE FIXED DECIMAL(7,2)
CALL       BLOCK Fatal error: exception Pli80.Parser.Parse_error(_, "expected statement")
COPY       BLOCK codegen: declared variable kind not in supported subset [TBD]: FILE")
COPYLPT    BLOCK codegen: declared variable kind not in supported subset [TBD]: FILE")
CREATE     BLOCK codegen: declared variable kind not in supported subset [TBD]: FILE")
DECPOLY    TYPE FIXED DECIMAL(15,4)
DEMO       COMPILED EXACT
DEPREC     TYPE FIXED DECIMAL(8,2)
DFACT      BLOCK codegen: DO WHILE/UNTIL/REPEAT deferred [TBD]")
DIOCALLS   BLOCK codegen: declared variable kind not in supported subset [TBD]: POINTER")
DIOCOPY    BLOCK codegen: declared variable kind not in supported subset [TBD]: POINTER")
DIORAND    BLOCK codegen: declared variable kind not in supported subset [TBD]: BIT(1)")
DTEST      TYPE FLOAT BINARY(24,0)
ENTER      BLOCK codegen: declared variable kind not in supported subset [TBD]: FILE")
EXPR1      BLOCK codegen: declared variable kind not in supported subset [TBD]: FILE")
EXPR2      BLOCK codegen: declared variable kind not in supported subset [TBD]: FILE")
FDTEST     TYPE FLOAT BINARY(24,0)
FFACT      BLOCK codegen: DO WHILE/UNTIL/REPEAT deferred [TBD]")
FLTPOLY    TYPE FLOAT BINARY(24,0)
FLTPOLY2   TYPE FLOAT BINARY(24,0)
FSCAN      BLOCK codegen: statement kind not in supported subset [TBD] (line 14)")
IFACT      BLOCK codegen: DO without TO deferred [TBD]")
INVERT     TYPE FLOAT BINARY(24,0)
KEYFILE    BLOCK codegen: declared variable kind not in supported subset [TBD]: FILE")
LABELS     BLOCK codegen: undeclared x")
LOAN1      TYPE FIXED DECIMAL(11,2)
LOAN2      BLOCK codegen: declared variable kind not in supported subset [TBD]: BIT(1)")
MAININVT   TYPE FLOAT BINARY(24,0)
MPMCALLA   BLOCK codegen: declared variable kind not in supported subset [TBD]: FILE")
MPMCALLB   BLOCK codegen: declared variable kind not in supported subset [TBD]: FILE")
NETWORK    BLOCK codegen: declared variable kind not in supported subset [TBD]: FILE")
OPTIMIST   BLOCK codegen: statement kind not in supported subset [TBD] (line 25)")
REPORT     TYPE FIXED DECIMAL(7,2)
RETRIEVE   BLOCK codegen: declared variable kind not in supported subset [TBD]: FILE")
REVERSE    BLOCK codegen: declared variable kind not in supported subset [TBD]: POINTER")
REVERT     BLOCK codegen: declared variable kind not in supported subset [TBD]: FILE")
RFACT      BLOCK codegen: DO WHILE/UNTIL/REPEAT deferred [TBD]")
SAMPLE     BLOCK codegen: PUT form not in E2E-3a subset [TBD] (line 8)")
TEST       TYPE FLOAT BINARY(24,0)
UPDATE     BLOCK codegen: declared variable kind not in supported subset [TBD]: BIT(1)")

## Post-5a sweep (2026-10-17, /tmp archived below)
A          FLOAT BINARY(24,0)
ACK        codegen: PUT form not in E2E-3a subset [TBD] (line 10)")
ACKTST     FIXED DECIMAL(6,0)
ALLTST     codegen: declared variable kind not in supported subset [TBD]: POINTER")
ANNUITY    FIXED DECIMAL(7,2)
CALL       Fatal error: exception Pli80.Parser.Parse_error(_, "expected
COPY       codegen: declared variable kind not in supported subset [TBD]: FILE")
COPYLPT    codegen: declared variable kind not in supported subset [TBD]: FILE")
CREATE     codegen: declared variable kind not in supported subset [TBD]: FILE")
DECPOLY    FIXED DECIMAL(15,4)
DEMO       COMPILED EXACT
DEPREC     FIXED DECIMAL(8,2)
DFACT      codegen: PUT form not in E2E-3a subset [TBD] (line 10)")
DIOCALLS   codegen: declared variable kind not in supported subset [TBD]: POINTER")
DIOCOPY    codegen: declared variable kind not in supported subset [TBD]: POINTER")
DIORAND    codegen: declared variable kind not in supported subset [TBD]: BIT(1)")
DTEST      FLOAT BINARY(24,0)
ENTER      codegen: declared variable kind not in supported subset [TBD]: FILE")
EXPR1      codegen: declared variable kind not in supported subset [TBD]: FILE")
EXPR2      codegen: declared variable kind not in supported subset [TBD]: FILE")
FDTEST     FLOAT BINARY(24,0)
FFACT      codegen: PUT form not in E2E-3a subset [TBD] (line 10)")
FLTPOLY    FLOAT BINARY(24,0)
FLTPOLY2   FLOAT BINARY(24,0)
FSCAN      codegen: statement kind not in supported subset [TBD] (line 14)")
IFACT      codegen: DO without TO deferred [TBD]")
INVERT     FLOAT BINARY(24,0)
KEYFILE    codegen: declared variable kind not in supported subset [TBD]: FILE")
LABELS     codegen: undeclared x")
LOAN1      FIXED DECIMAL(11,2)
LOAN2      codegen: declared variable kind not in supported subset [TBD]: BIT(1)")
MAININVT   FLOAT BINARY(24,0)
MPMCALLA   codegen: declared variable kind not in supported subset [TBD]: FILE")
MPMCALLB   codegen: declared variable kind not in supported subset [TBD]: FILE")
NETWORK    codegen: declared variable kind not in supported subset [TBD]: FILE")
OPTIMIST   codegen: condition form not in E2E-3b subset [TBD]: true")
REPORT     FIXED DECIMAL(7,2)
RETRIEVE   codegen: declared variable kind not in supported subset [TBD]: FILE")
REVERSE    codegen: declared variable kind not in supported subset [TBD]: POINTER")
REVERT     codegen: declared variable kind not in supported subset [TBD]: FILE")
RFACT      codegen: PUT form not in E2E-3a subset [TBD] (line 10)")
SAMPLE     codegen: PUT form not in E2E-3a subset [TBD] (line 8)")
TEST       FLOAT BINARY(24,0)
UPDATE     codegen: declared variable kind not in supported subset [TBD]: BIT(1)")
