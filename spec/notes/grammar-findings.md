# Grammar findings from corpus validation (item 3, round 1)

Method: `grammar/audit.py` scans all PL/I sources (artefacts + probes +
.DCL context + MATSIZE.LIB) vs. the grammar's known vocabulary; manual
App B/C/§12 lists diffed by hand. Report: grammar-vs-corpus.md.

## Coverage status
- App B statement list: 31 types; grammar has exactly 31 productions (1:1).
- Corpus uses 20/31 statement types. **ABSENT from corpus** (need synthetic
  probes): FORMAT, ALLOCATE/FREE (only ALLTST/ACKTST touch them), most
  READ/WRITE KEY(FROM/TO) record forms, structured IF-ELSE chains?,
  computed GOTO LAB(K) unverified.
- §1 vocabulary audit converged: residual unknown tokens are all user
  identifiers (CITY, TOKEN, PMT, B4 label, TRUE/FALSE %REPLACE macros...).

## Gaps found and resolved into the grammar this round
1. **Condition-name table** [M §8.5]: ERROR FIXEDOVERFLOW OVERFLOW
   UNDERFLOW ZERODIVIDE ENDFILE ENDPAGE UNDEFINEDFILE KEY. ON-unit rules:
   BEGIN-block units, no RETURN exit, non-local GOTO ok, stack max 16,
   REVERT pops newest, auto-revert at block exit. Default actions [M §8.8]
   — incl. the *manual confirming C024*: FIXEDOVERFLOW never raised for
   FIXED BINARY overflow.
2. **Non-standard ON/SIGNAL with numeric designator**: `ON ERROR(1)`,
   `SIGNAL ERROR(1)` [EX EXPR1/2, COPYLPT] — plausibly the same numeric
   codes printed in RTL messages ("END OF FILE (1)"...). PROBE 32 → P018.
3. **OPEN/file option cluster** [EX COPY, COPYLPT, LOAN2, ENTER, KEYFILE,
   CREATE, RETRIEVE, UPDATE]: `STREAM`, `PRINT`, `KEYED`,
   `ENVIRONMENT(F(n)[,B(n)])`, `TITLE('...')` ('$1.EMP' = drive/user naming,
   '$con' = console), `PAGESIZE(n)`. DCL-vs-OPEN placement unknown → P021.
4. **DEFAULT attribute is a PHANTOM**: ENTER's `1 default static` is a
   group *named* default; `address = default` is a group->group struct
   assignment. Grammar now models DR structures correctly:
   level-based DCL with group items, FLAT unqualified field references,
   struct-copy by group assignment. PROBE 38 → P022 (dot-qualification
   rejection, layout order, copy semantics).
5. **Pointer qualification `->`** [M §1.4 l.556; EX NETWORK 45 uses] —
   was missing from expressions entirely.
6. **Built-in table decoded** [M §12 TOC, OCR-corrupted, cross-checked
   against §12.x body headings]: adds BOOL (12.3.1 — the v1.4 RELNOTES
   fix!), DIVIDE (12.4.6), FIXED (12.4.7), HBOUND, LBOUND, LINENO, NULL,
   PAGENO (12.6.x). NULL used BARE (`p = null`, `q ^= null`) [EX].
   STKSIZ/MAXWDS/ALLWDS/TOTWDS are used by samples and compile —
   *undocumented v1.4 builtins* → eventually extract the dispatch table
   from PLI binaries (PROBE 27).
7. Subset-G cut checks queued: FLOAT DECIMAL (P017), STRUCTURE keyword
   (P023-ish), dynamic arrays/HBOUND on static arrays.

## Notes on tooling
- audit.py excludes Z80.LIB (RMAC macro library, not PL/I).
- Operator counts (§6) are heuristic (comment remnants inflate `*`/`**`);
  do not cite without hand-verification.

## Probe queue (next oracle sessions; all <= ~30 lines, compile $L, some run)
| probe | question | PROBE marker |
|---|---|---|
| P017 | `FLOAT DECIMAL` / `FLOAT DECIMAL(5)` accepted? | 37 |
| P018 | `ON ERROR(1)`, `SIGNAL ERROR(2)`, ONCODE values vs RTL "(n)" | 32 |
| P019 | NULL bare vs call; BOOL/DIVIDE/FIXED/LBOUND/HBOUND/LINENO/PAGENO syntax | 19b/27 |
| P020 | FORMAT stmt + PICTURE (App D) syntax legality | 29 |
| P021 | DCL vs OPEN option placement (STREAM/KEYED/ENV/TITLE/PAGESIZE) | 33 |
| P022 | level rules, dot-qualification, struct assign copy semantics | 18/38 |
| P023 | STRUCTURE keyword + PROC(a) STRUCTURE parameter | 35 |
| P024 | ALLOCATE/FREE runtime + STKSIZ interplay | 34 |
| P025 | ANSI DEFAULT attribute with reference name | 39 |

## Round 2 results (compiled AND run on cpmsim, golden/probes9-11)

Resolved by experiment:
- **FLOAT DECIMAL: CUT** — pass 1 `CONFLICT` diagnostic (new class!), no object.
- **Structures**: `grp.a` dot-qualification COMPILES and RUNS (read-only?
  assignment target TBD); `grp = grp2` COPIES field-by-field (P022).
- **Builtins** (P019A/B round2 run): `NULL` bare value ✓; `BOOL(x,y,'1010'b)`
  3-arg truth table ✓ ('1'b,'1'b -> '0'b per Z=1010); `divide(7,2,5)=3`;
  `fixed('123')=123`; `lbound(arr,1)=1`, `hbound(arr,1)=5` on static arrays;
  `lineno(pf)/pageno(pf)` OK with DECLARED file (undeclared sysprint =>
  pass2 `NO DCL` + `TYPES NOT=`).
- **FORMAT**: label REQUIRED (`money: FORMAT(...)`); reference via remote
  item **`R(label)`** — bare label = SYNTAX (P020 round3 runs).
- **OPEN matrix (P021)**: KEYED/ENVIRONMENT/TITLE/STREAM/PRINT/PAGESIZE all
  legal on OPEN, NOT in DCL (DCL with them = SYNTAX). Runtime open of
  unresolved title => `UNDEFINED FILE (1), File: INF=NUL` + traceback.
- **NEW diagnostic classes** (C026): pass1 {SYNTAX, NOT IMP, CONFLICT};
  pass2 {NO DCL, TYPES NOT=, CLOSURE}. Any error => no REL regardless of
  the pass-2/3 output that follows.
- **ON ERROR(1)**: compiles; at runtime SIGNAL ERROR(1) hit the TOPMOST
  ON ERROR unit (general), oncode=1 — designator selection UNRESOLVED.

Anomalies opened as probes:
- **PICTURE scaling (P020)**: p'++,+++.++' of 1234.56 => '+12.35'
  (=value/100), contradicting manual App D example => PROBE 40 matrix.
- `p->.q = 7` SYNTAX although `FREE P->.A` is App-B syntax => PROBE 41
  (dereference grammar). DIVIDE rounding mode => PROBE 42.

Queue updated: P018B (handler-selection matrix), P023 (STRUCTURE keyword),
P025 (DEFAULT attr), PROBE 40-42 as above. Next big-ticket items remain:
$E-vs-$V optimizer diff (C005) and the file-I/O run family (P021-style
sequences CREATE->RETRIEVE in one session).
