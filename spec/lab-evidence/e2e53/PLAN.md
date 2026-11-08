# E2E-53 — Compiler Coverage Expansion — CAMPAIGN PLAN

Operator authorization (2026-11-07 brief): multi-subround campaign; Goal A = move authentic
DR-accepted corpus programs REFUSED -> EXACT with unchanged sources and whole-file byte-exact
`.REL`; Goal B = expand measured language coverage. Report the two dimensions separately.
Intel 8080 only; DR oracle is law; no PLILIB, no MIR, no runtime work; no push.
Durable evidence rules: `PROTOCOL.md` Part 1 (pre-register before oracle; keep falsified
predictions; classify dr-refuses/my-gap/unmeasured; complete-`.REL` byte comparison; ledger
`spec/CLAIMS.md` is authority; never weaken the gate). Renewal/work policy: Part 2.

## 1. Baseline (VERIFIED FIRST-HAND at campaign open, session 01a1b800, 2026-11-07)

HEAD `9ac1775e46460e8b40a1f0614c02906197ddd391` (P3-19 finalize commit; E2E-52/P3 COMPLETE,
LOAN2 whole-file byte-exact CLAIMED at [C377]). Tree clean except the operator
`handoff.config.json` edit (dirty, NEVER staged) and ignored `build/`/`ocaml/_build-*`/
`golden/*/dir.txt` detritus.

| Instrument | Baseline | Verified by |
|---|---:|---|
| Byte-exact specimens | 1,312 | `spec/INVENTORY.txt` recount |
| Classified negatives | 190 | INVENTORY + gate log 190/190 |
| Controlled divergences | 9 | gate log 9/9 DIV-OK |
| Coverage contracts | 145 | gate `coverage_check: 145 rows, 0 errors, 0 warnings` |
| SUPPORTED contracts | 95 | COVERAGE.tsv `Counter`: 93 ACCEPTS/SUPPORTED + 1 ACCEPTS_DEFECT/SUPPORTED = 94 rows col7 SUPPORTED + … (row-status recount agrees with gate-side prose; treat 145/95 as the gate-attested pair) |
| Corpus census | 16 EXACT / 25 REFUSED / 3 NO_ORACLE / 0 DIFFERS | `spec/census/corpus-census.tsv` recount |
| Ledger | ends **C377** (199 `## C` headers; last gate attested 200 incl. banner variant — trust the sequential id: C377) | grep |
| Last full gate | rc=0 `build/gate-e52p19-reg.log` (all numbers hit) | tail read first-hand |
| Compiler | `dune build` rc=0; binary sha256 `baec1f82…` == armed tree fingerprint | direct build |
| Guard chain | fresh chain, renewalsDone 0, cap 12, `workingContextWindow` 145000, checkpoint current | diagnostics + config |

NO_ORACLE programs (no DR object; cannot count toward Goal A): CALL, INVERT, MAININVT.

## 2. Opportunity matrix (fresh audit 2026-11-07; first refusals re-measured DIRECT on `baec1f82`)

| Candidate | DR evidence | Current blocker (verified fresh, rc=2) | Other corpus users | Independent probes needed | Est. complexity |
|---|---|---|---|---|---|
| A1 GET SKIP family | AUTHENTIC `golden/first/EXPR1/EXPR1.REL` code 004A-005A pins bare `get skip;` = `LXI D,0290 / LXI B,<cont> / CALL ?SIOOP / MVI A,01 / CALL ?SKPOP / CALL ?QIOOP` (17 B, bitstream decode this session); variants live in REPORT/DEPREC/COPYLPT goldens | `GET form not in E2E-3e subset [TBD] (line 21)` (EXPR1:21 `get skip;`) | REPORT:33, DEPREC:95 (`get skip(2);`), COPYLPT:23/32/36 (`get skip list(v);`) — all behind OTHER first blockers | 3-4 minimal: bare / counted const / `get skip list(item)` / (variable count if a golden context proves needed) | LOW-MED: one new GET matcher arm + prescan mirror; shared attach/skip/close bytes already implemented on the PUT side (but NEVER reuse PUT bytes by analogy — DR evidence first) |
| A2 ACK/ACKTST PUT families | DECPOLY/RFACT/LOAN2 witnesses cover pieces; the console LIST rep-item and builtin-call item have NO minimal witness | ACK `PUT form not in E2E-3a subset [TBD] (line 12)`; ACKTST `PUT numeric item form unproven [TBD]` | none (only these 2) | several | MED-HIGH — audit found ACK carries >=3 INDEPENDENT blockers: (i) console matcher `all_data` rejects `Pi_rep`; (ii) `decimal(m,4)` as console PUT LIST item refuses (sanity S3); (iii) `returns(fixed) recursive` multi-formal refuses `attributed RECURSIVE multi-formal activation unproven` (sanity T3); more likely behind |
| A3 FSCAN CHARACTER builtins | none for SUBSTR/VERIFY/LENGTH lowering (sweep stage 3-4); SMVVM/SMCCM store laws exist [C317][C326] | `char store from non-literal [TBD]` (`line = substr(...)` store source) | EXPR2, SAMPLE, ANNUITY share builtin/store pieces; console GET EDIT (E46K15 my-gap) also required | many (whole builtin family) | HIGH — suitable only as a sequence of tightly scoped slices |
| A4 EXPR2 FLOAT call-as-expression | FDTEST/FPRINT float-call witnesses exist for ENTRY float; internal `returns(float binary) recursive` zero-formal call as store RHS unsampled | `FLOAT expression shape builtin is unsampled [TBD] (line 35)` (`value = exp();`) | EXPR1 shares it; then console PUT EDIT with FLOAT item + `f(10,4)`; plus %replace, GET EDIT | 2-3 then many behind | MED for first rule, HIGH for program |
| B1 non-2-byte array elements | goldens OPTIMIST/DEPREC/LABELS/MPMCALLA contain real layouts (context-rich); [C159][C164][C172] measured only 2-byte | `[TBD] array of 0-byte elements [C159]` (DEPREC/LABELS/MPMCALLA), `array of 9-byte elements` (OPTIMIST) | 4 programs share the SAME refusal family | ~4-6 (1/3/5/9-byte strides, const vs var subscript, static vs auto, DATA order) | MED-HIGH; highest Goal-A payoff per rule |
| B2 STATIC structure members | [C114][C371][C376] static-cell laws; member case unsampled | MPMCALLB `STATIC on … MEMBER … unsampled`; ENTER behind OPEN KEYED; DIOCALLS behind BASED char-varying | ENTER, MPMCALLB, DIOCALLS | 1-2 | MED |
| B3 CHAR VARYING returns | none | ANNUITY line 21, SAMPLE line 25 deferred; census `DECL.RETURN_VARYING` REFUSED | RETRIEVE too | ABI probe set (return descriptor, temp, lifetime) | MED-HIGH |
| C OPEN ENVIRONMENT / KEYED / UPDATE | P0 measured 34 OPEN blocks in DR sources but NO lowered object for these options | COPY/RETRIEVE `OPEN option ENVIRONMENT`; ENTER/KEYFILE/REPORT `KEYED`; UPDATE `UPDATE` | 6 programs | large record-layout research | HIGH — do NOT start comprehensively; only an independently measurable subset |
| D existing divergences | 9 pinned DIV-OK rows (BASED reevaluation, pointer loops, E40Q4 layout) | pinned, value-correct or shape-pinned | none | per-law discriminating design | HIGH; only with a falsifiable discriminator |

Ranking rubric applied (probability of unlocking programs; reusable forms; existing evidence;
risk; new unknowns): B1 has the highest historical payoff; A1 has the best
evidence-per-risk ratio and its authentic-golden geometry is already decoded.

## 3. P1 decision and reason

**E2E-53/P1 = GET SKIP statement family (A1).** Reasons:
1. Matches the operator default recommendation; the audit found no candidate whose first rule
   is simultaneously (a) pinned by existing authentic DR bytes (EXPR1.REL 004A-005A measured
   this session), (b) contained in ONE statement route, and (c) shared by four corpus programs.
2. Exercises the full campaign workflow (audit -> probe -> golden -> arm -> parity -> census)
   at low regression risk: the shape today refuses loudly; an arm cannot change any accepted
   specimen.
3. ACK/FSCAN/EXPR2 were audited as instructed and are NOT single-obstacle programs
   (sanity T3/S3 above); queueing them behind their true blocker sets instead.
4. B1 (arrays) is the strongest Goal-A candidate and is scheduled as P2 with its own
   pre-registration after P1 closes.

Scope discipline for P1: measure `get skip;`, `get skip(<const>);`, and `get skip list(<item>);`
on the console route; a `<variable>` count only if DR accepts and a golden/pin proves it.
FILE-route GET SKIP is OUT unless evidence crosses it. Never reuse PUT SKIP bytes by analogy.

## 4. Campaign dashboard (cumulative, vs baseline 1,312 specimens / 16 corpus EXACT)

| Slice | Feature family | New exact specimens | Corpus programs advanced | Newly EXACT programs | Claims | Gate |
|---|---|---|---|---|---|---|
| P1 **CLOSED** | GET SKIP family (console) | +4 (E525A-D, whole-file cmp rc=0) | 0 (blockers moved VERBATIM past GET lines in EXPR1/REPORT/DEPREC/COPYLPT, never fixed) | 0 | C378 (measured-bytes-only, BEFORE COVERAGE) | rc=0 build/gate-e53p1-reg.log (1316/0, 190/190, 9/9, 145 rows SUPPORTED 95, census 16/0/25/0, prose 5) |
| P2 **CLOSED** | non-2-byte array elements (stride 1/3 class) | +7 (E526A-G, whole-file cmp rc=0) | 0 (four B1 blockers re-held VERBATIM 0-byte/9-byte [C159], never fixed) | 0 | C379 (measured-bytes-only, BEFORE COVERAGE) | rc=0 build/gate-e53p2-reg.log (1323/0, 190/190, 9/9, 146 rows SUPPORTED 96, census 16/0/25/0, prose 5) |

## 5. Standing constraints (carry into every slice)

- Oracle campaigns: pre-registered PLAN + CRLF/bare-^Z probes committed by explicit paths
  BEFORE any oracle call or `ocaml/lib/` byte; goldens committed VERBATIM before arm.
- Probe/tag ids: E2E-53 uses `E525*`, `E526*`, ... with tags `e53p1`, `e53p2`, ...
  (verified unused at campaign open).
- Verify each accepted probe by whole-file `cmp` on FRESH POSITIONAL output
  (`pli80c.exe IN OUT`, no `-o`); run affected historical programs unchanged; census via
  `python3 tools/corpus_census.py --check` (own write path); REAL `--update-inventory`
  adjudicated by its own output; claims strictly sequential (next id from actual ledger
  state, first ordinary id **C378**) and written BEFORE any `spec/COVERAGE.tsv` touch;
  NEVER `coverage_gen.py`; new row ids registered explicitly in `spec/COVERAGE-IDS.txt`;
  FULL compile-tier gate rc=0 logged to `build/gate-e53pN-reg.log`; negative/divergence
  panels never weakened; unmeasured forms keep refusing with `[TBD]`; no source-name
  special cases.
- Git: explicit staging only, `git diff --cached --stat` before commit, never `git add -A`,
  never clean/reset, `handoff.config.json` never staged, no push.
- Renewal: only at safe boundaries (never mid-oracle/mid-git); never touch renewal-state;
  close the chain at cap via `handoff_finalize`.

## P1 — GET SKIP family — **CLOSED** (2026-11-08 hop 3; results `RESULTS.md` §P1; claim [C378]; gate rc=0 `build/gate-e53p1-reg.log`) — originally PRE-REGISTERED 2026-11-08, session 01a1b818, BEFORE any oracle call or `ocaml/lib/` byte

### P1.1 Blocker VERBATIM (re-measured FRESH POSITIONAL on `baec1f82…`, ignored `build/e53p1/sanity/`)

Four minimal console-SKIP probes all die at the single E2E-3e catch
(`lower_stmt`, `ocaml/lib/codegen.ml` ~14055; the prescan `Ast.Sget` arm at ~3714 demands 0 pool
bytes for non-EDIT GETs, which is correct here — SKIP items take no pool cell):

```
E525A rc=2  codegen: GET form not in E2E-3e subset [TBD] (line 5)
E525B rc=2  codegen: GET form not in E2E-3e subset [TBD] (line 7)
E525C rc=2  codegen: GET form not in E2E-3e subset [TBD] (line 7)
E525D rc=2  codegen: GET form not in E2E-3e subset [TBD] (line 6)
```

Same message EXPR1:21 carries today (`(line 21)`). Corpus users: EXPR1:21 and REPORT:33 bare,
DEPREC:95 counted `get skip(2);`, COPYLPT:23/32/36 `get skip list(<var>);` — all four behind
OTHER first blockers, so Goal A moves only for the census MESSAGE, not for program EXACTness,
this slice.

### P1.2 Existing authentic evidence (decoded FIRST-HAND this session from KEPT goldens)

The `build/e53-audit/` campaign-open reading is re-measured and **corrected** (P1.5). The
`.PRN` listings pin every statement's code address directly:

| Program:line | statement | `.PRN` pin | measured bytes |
|---|---|---|---|
| EXPR1:21 | `get skip;` | (decode 004A-005A) | `LXI D,0290 / LXI B,<cont 005B> / CALL ?SYSIN / MVI A,01 / CALL ?SKPOP / CALL ?QIOOP` — 17 B |
| REPORT:33 | `get skip;` | `33 c 0065` | byte-identical shape (`?SYSIN` slot 006C, `?SKPOP` slot 0071, `?QIOOP` slot 0074) |
| DEPREC:95 | `get skip(2);` | `95 c 0414` | SAME skeleton with `MVI A,02` (slot 041B `?SYSIN`, 0420 `?SKPOP`, 0423 `?QIOOP`) — 17 B |
| COPYLPT:23 | `get skip list(pagewidth);` (fixed bin) | `23 c 0089` | skip prefix (17 B, `MVI A,01`) then ONE item `CALL ?GNVOP / JP <cont+… 00A3> / CALL ?QCIOP / SHLD data@0100` then `CALL ?QIOOP` — 31 B |
| COPYLPT:36 | `get skip list(line);` (char varying 14) | `36 c 012D` | skip prefix then `CALL ?GNVOP / JP 0149 / LXI H,data@0106 / MVI B,0E / CALL ?SSVFS / CALL ?QIOOP` |

Routine-slot law re-confirmed: CHAIN-EXT slot = CALL operand address (opcode+1); the bare
console SKIP attaches **`?SYSIN`** — the same routine the console `get list(...)` already uses —
NOT `?SIOOP` (that is the FILE-route attach, `lower_get_file`). The count byte rides between
attach and `?SKPOP` exactly as on the PUT LIST route ([E2E-22/P4] `emit_skip_count` literal arm,
`MVI A,n / CALL ?SKPOP`), and the item tails are byte-for-byte the existing `lower_get_body`
arms ([R903] fixed-bin `?QCIOP/SHLD`; [X201/X202] varying `LXI H/MVI B,cap/?SSVFS`).
The console PUT SKIP bytes (`LXI D,0252 / ?SYSPR`) are NOT reused anywhere here — GET evidence
stands on its own goldens.

### P1.3 Arms and falsifiers (probes `probes/E525A..D`, tag `e53p1`, ids VERIFIED unused)

- **H-A (bare)** `E525A` = `get skip;` alone. Prediction: exactly the 17-B EXPR1/REPORT shape
  (`MVI A,01`). FALSIFIER: any different byte, size, or routine sequence; DR refusal.
- **H-B (counted const)** `E525B` = `get skip(2);`. Prediction: the same 17 B with `MVI A,02`
  (DEPREC measures this shape in context). FALSIFIER: DR refusal, an operand other than `02`,
  or a different sequence.
- **H-C (list, fixed-bin item)** `E525C` = `dcl n fixed binary; get skip list(n);`. Prediction:
  17-B skip prefix + 11-B item chain per COPYLPT:23 geometry + closing `?QIOOP`. FALSIFIER:
  refusal or any deviation.
- **H-D (list, char-varying item)** `E525D` = `dcl s character(10) varying; get skip list(s);`.
  Prediction: skip prefix + `GNVOP/JP/LXI H,*D(cell)/MVI B,0A/?SSVFS` + `?QIOOP` per COPYLPT:36.
  FALSIFIER: refusal or any deviation.

Explicitly OUT of P1 (stay refusing BY NAME via the preserved E2E-3e catch): a VARIABLE skip
count on GET (`get skip(n);` — no DR object anywhere; the PUT-side expression law [E46N18] is
NOT evidence for GET), MULTI-ITEM skip lists (`get skip list(a,b);` — no corpus user and no
authentic witness), FILE-route GET SKIP (COPYLPT:23/36 are console `sysin`-style reads; named
`get file(f) skip` has no witness), and `get skip edit(...)`. If DR refuses any probe, that is
recorded `dr-refuses` and NOTHING is armed on its authority.

### P1.4 Arm plan (only after goldens are decoded first-hand)

One new matcher (console `Sget` `kind = List_` with a leading `Pi_ctl ("SKIP", None|Some literal)`
and ONLY `Pi_data Eident` items) in front of `match_get_list_var` at the `Ast.Sget` dispatch, and
skip-prefix emission sharing the existing `emit_skip_count` literal arm + the attach bytes only
where the GET goldens pin them; `lower_get_body`/`lower_get` reused unchanged for the item tails.
The `GET form not in E2E-3e subset` catch STAYS for every other shape. Falsifiers: N45_GETSUB
(subscripted item) and E46K15 (console GET EDIT) must keep their markers; arm changes NO accepted
specimen (all four forms refuse today), the sweep is the legacy falsifier; EXPR1/REPORT/DEPREC/
COPYLPT rerun UNMODIFIED — their census messages may move, their first blockers for the OTHER
families stay and are recorded VERBATIM.

### P1.5 DATED correction (zero-oracle, this session)

The campaign-open note (LEARNINGS 2026-11-08) and PROGRESS/HANDOFF "full contract" recorded the
bare `get skip;` attach as `CALL ?SIOOP`. **FALSIFIED by direct decode:** slot `0051` carries
`?SYSIN` in `golden/first/EXPR1/EXPR1.REL` (also DEPREC 041B, COPYLPT 0090/00F4/0134, REPORT
006C). The predecessor's own kept raw dump `build/e53-audit/expr1-rel.txt` line 205 says
`@ 3235 LINK-CHAIN-EXT  code 0051 ?SYSIN`. The 17-byte geometry is otherwise as quoted. All P1
reasoning above uses the corrected routine.

### P1.6 Validation / registration contract (step 5 of PROGRESS Next action)

Fingerprint determinism (default == fresh `--build-dir`, grep `Error`, ZERO allowed); histogram
baseline; sweep (`python3 build/e52p3/sweep.py E46N E46K E51 E52 P086 R10`) FAILS 0; markers
argv-driven incl. any new negatives, DEC 64/0, divcheck 9/9; probe parity FRESH POSITIONAL
whole-file `cmp` vs `golden/e53p1/`; REAL `--update-inventory` adjudicated by its OWN output;
census OWN path; **C378+ measured-bytes-only BEFORE any `spec/COVERAGE.tsv` touch** (reproduce
every cited byte first-hand — P3-16 lesson); coverage adjudicated FIRST-HAND (candidate rows:
`IO.GET_LIST` row 64 EXTEND; NEVER `coverage_gen.py`); FULL gate rc=0 DIRECT
`build/gate-e53p1-reg.log`; RESULTS.md §P1 in this directory + PLAN §4 dashboard row + §P1
CLOSED; then re-rank the matrix and open P2 (B1 non-2-byte arrays).

## P2 — non-2-byte array elements, B1 family — **CLOSED** (2026-11-08 hop 6; results `RESULTS.md` §P2; claim [C379]; gate rc=0 `build/gate-e53p2-reg.log`) — originally PRE-REGISTERED 2026-11-08, session successor of 01a1b83e (chain 4/12), BEFORE any oracle call or `ocaml/lib/` byte

### P2.1 Blocker VERBATIM (re-held FRESH POSITIONAL on `8e51c261…`, ignored `build/e53p2/pre-audit/`)

The four B1 corpus users refuse at bind sizing (`Bind.layout`, `ocaml/lib/bind.ml` ~1046-1051),
with `elem_sz = bytes_of rt` from the ONE sizing law already measured for scalars ([C159] re-
derivation note at `bind.ml:148-166`: `RTbin p -> (p+8)/8`, `RTchar(n,fix) -> n`,
`RTchar(n,vary) -> 1+n`, `RTentry/RTlabel -> 0`):

```
DEPREC    rc=2  codegen: [TBD] array of 0-byte elements [C159] (…)  — schedule (0:3) entry variable
MPMCALLA  rc=2  codegen: [TBD] array of 0-byte elements [C159] (…)  — localstk (0:255) entry (fixed) variable
LABELS    rc=2  codegen: [TBD] array of 0-byte elements [C159] (…)  — (x, y, z(3)) label
OPTIMIST  rc=2  codegen: [TBD] array of 9-byte elements [C159] (…)  — negative (1:nwords) character(8) varying static initial
```

The classes split THREE ways (pre-audit `LEARNINGS.md` § "P2 B1 arrays"): (a) entry/label arrays
are 2-byte cells whose VALUES are CHAIN-ADDR operands / PCHL computed jumps (value class, refused
BY NAME here — row `TRAN.COMPUTED_GOTO` REFUSED, negative N6 must survive); (b) OPTIMIST is a
STATIC char-VARYING array (`?CXVVM` descriptor + A3 string builtins, refused BY NAME); (c) plain
FIXED automatic arrays with stride 1 (`fixed bin(1..7)`) or odd stride (`char(n>1)`) — the class
this slice measures.

### P2.2 UNARMED sanity audit (FRESH this session, `build/e53p2/sanity/`, binary `8e51c261…`)

Scalar machinery the candidate array shapes would ride on:

| probe | shape | rc | outcome VERBATIM |
|---|---|---|---|
| SNS1 | `dcl b fixed bin(7); b = 5; put list(b);` | 0 | 256 B (C079 LDA/STA ladder + QICOP item proven) |
| SNS2 | `dcl s char(3); s = 'AB'; put list(s);` | 0 | 256 B (V106 `?SMCCM` len<cap store + `?SLCTS` proven) |
| SNS3 | `dcl c char(1); c = 'X';` (len==cap) | 2 | `codegen: fixed store len==cap MOV B/A unproven [TBD]` — the char(1) SCALAR store itself is unproven; char(1)-element stores are therefore OUT of any arm this slice |
| SNS4 | legacy `dcl a(3) fixed; a(2)=7; put list(a(i));` | 0 | 256 B — the accepted 2-byte array control (legacy falsifier) |
| SNX1-5 | `fixed bin(7)` / `char(1)` arrays (const + var subscripts, load + store) | 2 | `array of 1-byte elements [C159]` — all five die at bind.ml ~1047, NOT in codegen: bind sizing is the only obstacle for these shapes so far |
| SNX6-7 | `char(3)` arrays const + var store | 2 | `array of 3-byte elements [C159]` — same bind site |
| SNX8-10 | SINGLE-element arrays `dcl a(1) fixed bin(7)/fixed` and `a(1) = 3` | 2 | **crash, not refusal**: `Fatal error: exception File "lib/codegen.ml", line 10047, characters 2-7: Pattern matching failed` — `arrays :=` runs only when `nelem > 1`, so `a(1)` never registers and the Esuffix LHS falls off `lower_assign`'s match. Classified **my-gap** (crash where a `[TBD]` refusal is required, the [C160] discipline). **RECORDED, NOT FIXED this slice** — no E526 probe exercises `nelem = 1`; the fix is a separate pre-registered change. |

The seven final probes `probes/E526A..G` themselves were sanity-run UNARMED
(`build/e53p2/sanity2/`): every one dies at the bind guard (`1-byte`/`3-byte elements
[C159]`) exactly like SNX1-7 — the front end accepts the syntax; only sizing refuses.

### P2.3 Arms and falsifiers (probes `probes/E526A..G`, tag `e53p2`, ids VERIFIED unused)

Predictions ride ONLY on already-measured laws; each is falsifiable by the campaign bytes:

- **H-A (stride-1 const stores)** E526A: `a(1)=3` (offset 0) and `a(3)=5` (offset≠0). Predicted
  from [C159]'s split: offset 0 the scalar-store family adapted to 1 byte (STA per [C079]'s
  1-byte store law) or the `LXI H,*D / MVI M` general form; offset≠0 `MVI M`-style byte store at
  the folded displacement. FALSIFIER: DR refusal, any 2-byte-shaped store (SHLD/hi-lo pair) for a
  1-byte cell, or an address ladder where a folded operand appears.
- **H-B (stride-1 const read)** E526B: `b = a(2)` and `put list(a(1))`. Predicted: direct folded
  `LDA`-class load ([C079] `LDA abs` + the sign-extend ladder) with no runtime address arithmetic,
  mirroring [C159]'s `LHLD A+off`. FALSIFIER: refusal, a computed-address ladder for a constant
  subscript, or a load sequence not decomposing to known C079 bytes.
- **H-C (stride-1 var subscript READ, bias≠0)** E526C: ladder predicted as the OPTIMIST-pre-audit
  general form with `LXI DE,0001 / CALL ?IM22N` replacing `DAD H`, inside
  `LXI H,*D(base-lb) / PUSH H / … / POP D / DAD D`. FALSIFIER: refusal, plain `DAD H` kept, a
  different multiplier byte, or a structurally different ladder.
- **H-D (stride-1 var subscript STORE)** E526D: same ladder + the measured byte-store tail.
  FALSIFIER: refusal or a tail that stores two bytes.
- **H-E (stride-3 char(3) const store + element PUT)** E526E: literal store predicted on the
  [C321]/V106 `?SMCCM` route with the ELEMENT address as destination (pool cell + `3E cap / 06 len`);
  the `put` read on `?SLCTS` with `MVI A,03`. FALSIFIER: refusal, any other copy routine, or
  inline byte stores where SMCCM is predicted (or vice versa).
- **H-F (stride-3 var subscript store)** E526F: OPTIMIST IM22N ladder with `LXI DE,0003` + the
  SMCCM tail. FALSIFIER: any deviation from the byte sequence already decoded from
  `golden/first8080u/OPTIMIST/OPTIMIST.REL` except the DE operand.
- **H-G (stride-1 var subscript, bias-0 form, `lb=0`)** E526G: predicted the VB1 7-byte form with
  the multiply substituted: `LHLD i / LXI DE,0001 / CALL ?IM22N / LXI D,*D(base) / DAD D` shape
  family — the bias-0 ladder has NEVER been measured at stride≠2. FALSIFIER: refusal or the
  bias-form appearing (then the arm keeps refusing bias-0 at stride≠2).

EXPLICITLY OUT of P2 arms (stay refusing BY NAME through the existing guards): the entry/label
VALUE class (CHAIN-ADDR operands, computed goto/PCHL; `TRAN.COMPUTED_GOTO` row REFUSED and
negative N6 survive untouched); OPTIMIST's static-varying descriptor class (`?CXVVM` + A3 string
builtins, plus the separate `STATIC array … [C159/AB5]` refusal); `char(1)` element stores
(scalar class itself unproven, SNS3); DECIMAL/FLOAT/BIT arrays and precisions beyond 15 (DR
`NOT IMP` per [C079]); multi-dimensional arrays; the `nelem = 1` crash (recorded my-gap above,
never probed here); runtime-variable bounds. If DR refuses a probe, that is recorded
`dr-refuses` and NOTHING is armed on its authority.

### P2.4 Arm plan (executed only after goldens decode first-hand)

Three candidate edits, each armed ONLY for the exact strides/forms the campaign pins, all other
shapes keep the existing `[TBD]`:
1. `bind.ml` ~1046: allow `elem_sz` values MEASURED by the campaign for non-STATIC automatic
   FIXED arrays (the refusal text stays for every unmeasured size; the catch for `elem_sz = 0`
   entry/label and static-varying stays).
2. `codegen.ml dyn_addr` (~1093): stride ladder generalization — measured strides take
   `LXI DE,<stride> / CALL ?IM22N` in place of `DAD H`, ONLY in the (bias≠0 | bias=0) forms the
   goldens pin; unmeasured stride/form combinations keep refusing.
3. `codegen.ml` constant-subscript element load/store consumers (read ~4561, store ~10834): arm
   the measured byte shapes for the pinned strides only; the four [C159] 2-byte store forms
   untouched (legacy falsifier: SNS4 + the whole sweep must stay byte-identical).
No source-name special cases; unmeasured shapes must refuse loudly, never silently take a
2-byte path.

### P2.5 Validation / registration contract

Fingerprint determinism (default == fresh `--build-dir`, grep `Error`, ZERO allowed); histogram
baseline codegen 68 / total 124 (re-count from the fresh log, never carry); sweep
`python3 build/e52p3/sweep.py E46N E46K E51 E52 P086 R10` **FAILS 0** (count COMPUTED from the
panel delta vs the 194/0 registered baseline, never hard-carried); markers argv-driven, the 16
from P1 plus any new negatives — `N6` (computed goto), `N45_GETSUB`, `E46K15` MUST survive; DEC
64/0; divcheck 9/9; probe parity FRESH POSITIONAL whole-file `cmp` vs `golden/e53p2/`; corpus
reruns UNMODIFIED — DEPREC/LABELS/MPMCALLA/OPTIMIST/EXPR1/REPORT/COPYLPT — blockers recorded
VERBATIM, NOTHING fixed (the four B1 blockers must NOT move from `0-byte`/`9-byte [C159]` since
their classes stay refused: if any moves, the arm leaked and gets reverted, not celebrated);
REAL `--update-inventory` adjudicated by its OWN output (baseline **1316/190**, +7 expected if
all probes accepted); census OWN path `python3 tools/corpus_census.py --check
spec/census/corpus-census.json` (expect counts UNCHANGED 16/0/25/0 — the arm touches no corpus
class; adjudicate from OWN output, never force); **C379+ measured-bytes-only BEFORE ANY
`spec/COVERAGE.tsv` touch** (reproduce every cited byte first-hand — the P3-16 lesson); coverage
FIRST-HAND (candidate: EXTEND row 7 `AGG.ARRAY_1D_FIXED` with a DATED stride-generalization
clause, or a NEW `AGG.ARRAY_1D_STRIDED` row + explicit `spec/COVERAGE-IDS.txt` entry — decided
by what the goldens pin, NEVER `coverage_gen.py`); FULL compile-tier gate rc=0 DIRECT
`build/gate-e53p2-reg.log`; `spec/lab-evidence/e2e53/RESULTS.md` §P2 + PLAN §4 dashboard row +
§P2 CLOSED. Goldens committed VERBATIM before any arm byte; `handoff.config.json` never staged;
no push.
