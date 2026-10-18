# PL/I-80 corpus audit — REV 2 (2026-10-18, post-E2E-5c slice 2) — ANALYSIS ONLY

Scope of this revision: re-rank the 44-program corpus against the
capabilities added since REV 1 (E2E-5a PUT/GET console forms, E2E-5b
numeric I/O + widths, E2E-5c slices 1-2: internal/non-recursive CALL,
recursive SVBLK/RSBLK ABI, DO REPEAT/WHILE/no-exit window + tail guard).
NO compiler code, NO new oracle probes and NO harness changes were made
for this revision: it uses (a) the 41 existing DR .REL + 44 DR .PRN
corpus goldens, (b) local runs of the current build, (c) exact
PLILIB-route counting from the goldens. Full machine-readable tables
banked in `corpus-audit-2026-10-18-data.txt` (same directory).

## 1. Headline status

> **SUPERSEDED IN PART the same day:** DEC core landed and **DFACT is
> byte-exact, so the score below (2/41) is now 3/41**; see section 10 for the
> refreshed distances, the re-ranked next three programs, and the new
> emitted-routine baseline (29 -> 36 entrypoints). The tables in sections
> 1-8 are kept as the REV 2 record.
| metric | REV 1 (post-E2E-4) | REV 2 (now) |
|---|---|---|
| corpus sources | 44 | 44 |
| DR .REL goldens available | 41 | 41 (CALL/INVERT/MAININVT: DR itself errored -> permanently unreachable) |
| byte-exact today | 1 (DEMO) | **2 (DEMO, RFACT)** = 2/41 = 4.9 % of the attainable corpus |
| compiles but diverges | 0 | 1 (FFACT, first diff byte 48) |
| hard fail-loud [TBD] | 40 | 38 |
| compiler CRASHES (uncaught Match_failure) | 0 | **3 (IFACT, OPTIMIST, SAMPLE)** — see D1 |

Corpus wins attributable to 5c: RFACT became byte-exact (recursion +
no-exit window), and the old "DO WHILE/REPEAT/no-TO" first-blocker
cluster (DFACT FFACT IFACT RFACT, 4 programs) has collapsed to
DEC/FLOAT/EDIT needs respectively — the loop machinery is no longer a
barrier anywhere in the corpus. Verified locally: bare `DO;…END;`,
forward/backward plain `GOTO`, 2-item numeric `PUT LIST`, and `SKIP`
inside `PUT LIST` are all supported already (note: a bare
`PUT SKIP;` with no LIST is NOT -- it is defect D1). The only
remaining DO gap is the `BY`-step form (3 programs: DTEST FDTEST
IFACT) plus `UNTIL` (1 program: DIOCALLS).

## 2. New primary metric: DR PLILIB routine-surface distance
Counting the `?NAME` externals a program's DR .REL requests that my
compiler does NOT yet emit anywhere (baseline = union over the 83
byte-exact registered goldens, 29 entrypoints today). This is a
directly evidence-backed proxy for "how much new lowering do we have to
reverse-engineer", independent of first-blocker noise.

smallest distances (of the 41 goldened programs):
| program | new routines | which | remaining need clusters |
|---|---|---|---|
| DEMO, RFACT | 0 | — | none (byte-exact) |
| FDTEST | 1 | ?QFCSS | FLOAT + ENTRY + DO-BY |
| LABELS | 1 | ?RECOV | RECOVER + CALL-stmt + array + label-var |
| IFACT | 2 | ?EDITF ?EDTOV | EDIT + DO-BY |
| A | 2 | ?FD44M ?FPRET | FLOAT (external module, no main) |
| DTEST | 2 | ?FX44M | FLOAT + CALL-stmt + ENTRY + DO-BY |
| ACK | 3 | ?QCIOP ?QDCOP ?QI15D | DEC + multi-arg + GET-num + stack-opt + rep-gen |
| **DFACT** | **4** | ?DCRET ?DMUOP ?QDCOP ?QI15D | **DEC-core only** |
| **COPY** | **4** | ?OIOOP ?SIOOP ?RNIOP ?WNIOP | **FILE-seq only** |
| REVERSE / REVERT | 4 | ?ALLOP ?FREOP … | POINTER / keyed-FILE + recovery |
| FFACT | 5 | ?FL40M ?FM44S ?FPRET ?QFCSS ?QI15F | FLOAT only |
| KEYFILE | 5 | ?KEYTO … | FILE-seq + FILE-KEYED (not sequential-only) |
cluster totals (distinct unseen routines / programs on the path):
DEC-core 11/13 · DEC-edit 2 · EDIT 7/17 · FLOAT 26/11 · FILE-seq 8/13 ·
FILE-keyed 5/6 · GET-num 5/21 · BIT1 13/16 · POINTER 2/8 · RECOV 1/10.
Note `MULTIARG`, `CALLSTMT`, `ARRAY`, `DO-BY`, `REPLACE`, `OPTS` need
**zero** new PLILIB entrypoints — they are pure layout/lowering work on
the ABI already proven.

## 3. Layout evidence already readable from the DR .PRN listings
(hex, from `golden/first8080u/<N>/<N>.PRN`; no probe required)
| program | CODE SIZE | DATA AREA | note |
|---|---|---|---|
| RFACT (exact) | 0099 | 0018 | 1-formal recursive fixed, arg temp, loop var |
| **DFACT** | 00A5 | 0020 | **+12 code / +8 data over RFACT** — one `returns(fixed dec(15,0))`: DEC(15) cell = 8 bytes is consistent with packed BCD (hypothesis, to be probed) |
| FFACT | 00A1 | 001C | +4 data = one float cell |
| IFACT | 0081 | 0021 | no procedure, no stop, main-only |
| COPY | 0081 | 0109 | + 2 named COMMON blocks INPUT_=44 B / OUTPUT=45 B = 33-byte file control block + length-prefixed internal name ('INPUT_FILE'/'OUTPUT_FILE'); titles '$1.$1','$2.$2' live in DATA |
Also confirms the C082 window rule from the opposite side: DFACT,
FFACT, IFACT, COPY request **no ?STOPX** at all (open no-exit window,
epilogue dropped) — IFACT's `DO i=0 BY 1` (no TO) belongs to the same
window family as `DO … REPEAT`, which REV 1 did not know.

## 4. Defects found by this audit (fail-loud discipline violations)
These are the audit's most actionable product; all reproduced locally
against the current build, none require the oracle.
* **D1 CRASH instead of [TBD]** — `codegen.ml:321 match_put_list_lit`
  has no fallthrough for `put_kind` = Edit/Item/Editsk and for a bare
  `put skip;`: OCaml `Match_failure` escape. Reproduced with
  `put edit(i)(f(3));`, `put item(i);`, `put skip;`. Affects IFACT,
  OPTIMIST, SAMPLE today; 17 corpus programs contain such forms.
  Fix = add the [TBD] clause (1 line); must not change the 83.
* **D2 %replace is parsed but never applied** — macro names reach bind
  as undeclared identifiers (`%replace one by 1; x = one;` ->
  "undeclared one"; `%replace true by '1'b;` + `do while(true)` ->
  condition-form [TBD]). Loud, but REV 1 misattributed OPTIMIST to a
  "statement kind" gap. 17 programs (ANNUITY CREATE DECPOLY DEPREC
  DIOCOPY ENTER EXPR2 FLTPOLY FLTPOLY2 FSCAN LOAN2 MAININVT MPMCALLA
  MPMCALLB NETWORK OPTIMIST RETRIEVE) depend on it; 14 of them use
  exactly `do while(true)` -> after expansion that IS the `'1'b`
  no-exit window already proven in C082, so the payoff is reuse of
  existing knowledge rather than new lowering, and it needs zero new
  PLILIB entrypoints. The one semantic to establish is whether DR's
  %replace is a pure token substitution (its listing prints the macro
  lines verbatim, which suggests textual preprocessing before parse).
* **D3 FAIL-SILENT** — non-`main` block options are accepted and
  ignored: `options(main,stack(2000))` and even
  `options(main,stack(2000),segments)` compile with no diagnostic and
  no effect. Affects ACK, ACKTST. `stack` is plausibly
  layout/execution-affecting, so any ACK .REL emitted before this is
  closed would be untrustworthy. Must become [TBD] (or modelled) first.
* **D4 FAIL-SILENT** — the `returns(<type>)` attribute is never
  validated: `returns(float)` and `returns(fixed decimal(15,0))` are
  lowered as if they returned FIXED (both reproduced; FFACT yields a
  plausible 512-byte .REL that is wrong from byte 48). 14 programs
  carry a non-fixed returns type. Until DEC/FLOAT exist, these must
  refuse loudly, not emit fixed-shaped code.
Recommended: D1+D3+D4 as a small hygiene commit **before** any new
feature slice (they are cheap and they protect the byte-parity
semantics of everything that follows); D2 as its own micro-slice
(preprocessor semantics: whether DR's %replace is textual, its
interaction with listings, `'^z'` literals).

## 5. REV 1 first-blocker table — corrections
* `POINTER/BASED 4` -> 9 programs carry pointer/based constructs;
  only 8 of them are goldened-blocked on it as a *need* (ALLTST
  DIOCALLS DIOCOPY DIORAND MPMCALLA MPMCALLB NETWORK REVERSE).
* `FILE decl 12` -> 19 goldened programs need FILE routines
  (13 sequential-only, 6 additionally keyed: ?KEYTO/?KEYOP/?REVOP/
  ?OFCOP/?ONCOP).
* `BIT(1) decl 3` -> 16 programs need the bit/char routine family
  (?CS*AD ?VS*AD ?XL3OP ?VEROP ?SCCCM ?SSCFS …) — the char/varying
  operator family, not just bit(1) declarations.
* `'1'b` was counted as "3+"; corrected: **10** programs use a bit
  literal directly in their body, and **15** more reach the identical
  forever-window condition only through `%replace true by '1'b` (14 of
  those are `do while(true)`) — 24 programs in the window family. The
  earlier `'1'b` grep was wrong (it missed the closing quote of the
  `'1'b` token), which is why REV 1 under-counted it.
* `DO WHILE/REPEAT/no-TO 4` -> RESOLVED (0 programs blocked on it).
* Missing entirely from REV 1: `%replace` (17 programs) and the
  `?RECOV` recovery/ON-unit family (10 programs).

## 6. Three most promising NEXT original corpus programs (ranked)
Ranked by (a) incremental implementation effort, (b) reusable feature
coverage, (c) technical risk — all three have a DR .REL golden already,
so no re-goldening is needed.

### 1st — DFACT  (FIXED DECIMAL core)
* Effort: LOWEST in the corpus. 4 unseen routines
  (?DMUOP ?DCRET ?QDCOP ?QI15D) on a skeleton that is *already
  byte-exact as RFACT*: same no-exit REPEAT window, same suppressed
  stop, same SVBLK/RSBLK recursion, same 4-item PUT LIST. Delta is
  +12 code / +8 data bytes (measured). `DECIMAL(x,15)` is currently
  misread as a multi-arg call -> needs a builtin path, not a new ABI.
  DEC pool conventions are already banked (C079: per-operand
  `MVI A,prec; ?DLDOP`, `?DSUOP`, `?QDI15` chain in N301/N306/G101-106).
* Coverage: DEC-core is on the path of 13/41 programs; DEC-core +
  DEC-edit (?QDDSL/?QDDSR) reaches 12 unseen routines and 2 unlocks
  (DFACT, LOAN1); adding multi-arg+GET-num opens DECPOLY then ACK —
  i.e. DEC is the *entry fee* for the whole numeric-report class
  (LOAN1 LOAN2 ANNUITY DEPREC REPORT UPDATE ENTER CREATE RETRIEVE
  ACKTST DECPOLY).
* Risk: LOW-MEDIUM. Unknowns are contained: DEC cell size vs precision,
  ?DMUOP accumulator discipline, DEC<->INT conversion direction, DEC
  default editing in ?QDCOP. 6-8 micro-probes (R5xx series, same
  $L$D$C$S protocol) plus the .PRN deltas should settle them. Runtime
  proof is available with today's tools (bounded complete-record prefix
  + independent math.factorial oracle) — no infrastructure change.

### 2nd — IFACT  (PUT EDIT + DO BY/step)
* Effort: MEDIUM. Only 2 unseen routines (?EDITF ?EDTOV) but a new
  lowering family: the format list `(skip, a, f(2), a, f(7))` and how
  DR hands it to ?EDITF (descriptor list in DATA? inline?), plus 2 DO
  shapes (`DO i=0 BY 1` no-TO window variant — expected to behave like
  REPEAT since IFACT has no ?STOPX — and a descending
  `DO n=i TO 1 BY -1`). Smallest relevant golden (384 B, CODE=0081,
  DATA=0021), no procedures, no stop: an unusually clean specimen for
  reverse-engineering editing. Precondition: D1 (it crashes today).
* Coverage: the EDIT cluster (EDITF/EDTIV/EDTOB/EDTOV + ?QB08C/?QB16C/
  ?QCB16) is a prerequisite of 17/41 programs — the widest single
  output-side cluster; it is also what converts DEC-core into DEC
  *reporting* (DEPREC/REPORT/ANNUITY/ACKTST/LOAN2) and unlocks the
  PUT-EDIT half of COPYLPT/FSCAN/ALLTST/DIOCALLS/MPMCALL*.
* Risk: MEDIUM-HIGH (format-list encoding is genuinely new; no
  byte-exact editing specimen exists in the 83). Bounded by IFACT's
  size; runtime is console-only => verifiable today.

### 3rd — COPY  (sequential FILE I/O)
* Effort: MEDIUM for .REL parity, HIGH for runtime. 4 unseen routines
  (?OIOOP ?SIOOP ?RNIOP ?WNIOP); the file-block layout is already
  readable from the golden (33-byte control block + length-prefixed
  internal name per FILE variable, as *named COMMON sections*
  INPUT_/OUTPUT_ of 44/45 bytes, titles in DATA). Its main loop is the
  `'1'b` window proven in C082 and its missing epilogue is already
  predicted. No procedure, no stop, 129 bytes of code.
* Coverage: the largest cluster in the corpus — FILE-seq/FILE-keyed are
  on the path of 19/41 programs (COPY COPYLPT CREATE ENTER KEYFILE
  REPORT RETRIEVE UPDATE REVERT NETWORK LOAN2 DEPREC EXPR1 EXPR2
  DIOCOPY ANNUITY); COPY is the *only* program unlocked by the FILE
  investment alone.
* Risk: HIGH. Needs new oracle *infrastructure* (stage an input file on
  the per-run D:, export and compare the output file), CP/M FCB/extent
  and ENDFILE-condition semantics, and runtime `title('$1.$2')`
  argument handling. Byte-parity of the .REL is attainable without any
  of that, so the layout can be banked safely under the existing gate
  while runtime validation stays explicitly deferred (never claimed).

Explicitly de-ranked: **A/FLOAT ladder** (A = 2 routines but it is an
external module with no main and 21 bytes of code — too little
structure to pin the float representation; FFACT is the better FLOAT
entry at 5 routines, and the full FLOAT cluster is 26 unseen routines
plus formatting); **ACK** (the natural multi-arg capstone but 5
clusters deep and blocked by defect D3); **KEYFILE** (looks
sequential but requires keyed ?KEYTO — REV 1's grouping was wrong).

## 7. The three candidate investments, head to head
| | FIXED DECIMAL (core) | multi-argument procedures (+CALL stmts) | sequential FILE I/O |
|---|---|---|---|
| unseen DR routines to learn | **11 core** (+2 DEC-edit) | **0** — pure layout RE on the proven SVBLK/RSBLK/CELL ABI | 8 seq (+5 keyed) |
| programs unlocked ALONE | 1 (DFACT); 2 with DEC-edit (DFACT, LOAN1) | **0** | 1 (COPY) |
| programs it is a prerequisite of | 13 | **23** (widest enabler) | 19 (largest feature cluster) |
| first observable payoff | DFACT immediately | only DECPOLY/ACK *after* DEC+GET+OPTS | COPY (.REL parity), functional proof later |
| new infrastructure needed | none | none | **yes** — per-run file staging + output-file comparison in the oracle harness |
| runtime verification with today's tools | **yes** (console + bounded prefix + arithmetic oracle) | n/a | no (console is empty; the effect is in the output file) |
| main unknowns | DEC cell size/precision law, DMUOP/QDCOP conventions, DECIMAL builtin | N-formal frame ordering, multi-cell call-site layout, `stack(n)` semantics | FCB/DMA 33-byte block contents, ENDFILE/'1'b condition, CP/M extents, `$1` runtime titles |
| technical risk | **LOW-MEDIUM** | MEDIUM (no standalone evidence; needs synthetic probes since the smallest corpus multi-arg specimen is ACK at 1152 B) | **HIGH** (byte-parity plausible, semantics + validation deep) |
| verdict | **best value now** | enabler, not a milestone: schedule it inside the ACK/DECPOLY slice where DEC has already landed | biggest prize, highest cost: do it after DEC+EDIT, with explicit infra approval |

Sequencing arithmetic (unlock counts only, from the need sets):
DEC-core -> DFACT · +DEC-edit -> LOAN1 · +multi-arg/CALL -> still
{DFACT, LOAN1} · +GET-num -> ACK · FILE-seq -> COPY ·
+RECOV/GET-num/EDIT/FILE-key -> COPYLPT, KEYFILE · FLOAT -> A, FFACT ·
+multi-arg/GET-num -> TEST. In other words multi-arg buys its first
program only on top of DEC + GET, whereas DEC and FILE each pay on the
first slice.

## 8. Recommended next milestone (FOR APPROVAL, nothing started)
**E2E-6 — "FIXED DECIMAL core", acceptance specimen DFACT.**
* Step 0 (hygiene, no new capability): close D1 (crash -> [TBD]),
  D3 (unknown block options -> [TBD]), D4 (non-fixed `returns()` ->
  [TBD]) and re-run all gates; the 83 must stay byte-exact.
* Probe series: ~6-10 micro-probes (R501…) in the established R4xx
  style, `$L$D$C$S`, CRLF+^Z sources: DEC declaration vs precision
  (cell size law), DEC constant/pool, ?DMUOP/?DADOP/?DSUOP operand
  discipline, DEC<->INT conversion (?QI15D/?QDI15), `returns(fixed
  dec)` + ?DCRET exit, ?QDCOP default DEC editing/width, DECIMAL(x,p)
  builtin, DEC compare in IF/DO bounds (likely deferred [TBD]).
* Acceptance: DFACT .REL byte-identical (raw cmp) + .COM byte-identical
  vs DR + bounded complete-record console prefix byte-equal (tool
  exists) + first 8 factorial records checked against math.factorial.
  Registered in tools/e2e_gate.py only when exact.
* Fail-loud perimeter kept: DEC *editing* (PUT EDIT pictures,
  ?QDDSL/?QDDSR), GET of DEC, DEC compare/relational forms, FLOAT,
  FILE, POINTER/BASED, multi-formal, `stack(n)` all remain [TBD] until
  probed. No extrapolation from the fixed-bin shapes.
* Estimate: ~350-550 LoC in codegen.ml/bind.ml + probes; checkpoint to
  the user at every ~2000 added lines.
* Then, in order: E2E-7 PUT EDIT (IFACT) — widest output cluster;
  E2E-8 sequential FILE (COPY) — requires the infrastructure decision;
  E2E-9 multi-arg+GET+stack as the ACK capstone; %replace as a cheap
  side-slice that can ride along with any of them (16 programs, 0 new
  routines).

**DECISIONS REQUESTED**
1. Approve E2E-6 (DFACT/DEC core) as the next milestone, including the
   step-0 hygiene fixes?
2. Perimeter: cut POINTER/BASED (8 programs) + label-variable/computed
   GOTO (2) + ENTRY/multi-module (10, incl. A/DTEST/FDTEST) from the
   byte-parity corpus goal, or keep them open? REV 2 recommends: cut
   label-vars and pointer/based; treat ENTRY/multi-module as its own
   later decision because 2 float entry programs (A, FDTEST) are cheap
   on routines but structurally outside the single-object model.
3. Do you authorise oracle *infrastructure* work (per-run file staging
   + output-file comparison) at all, and if yes only for E2E-8?
4. Want %replace expansion pulled forward as a standalone micro-slice
   (it is loud-today, cheap, and converts 13 `do while(true)` loops
   into the already-proven `'1'b` window)?

## 9. Standards used for this revision (unchanged)
* Parity means RAW BYTE EQUALITY (cmp/sha256 of the .REL); reldump's
  masked output was used only for READING, never for a verdict.
* This revision ran NO oracle probe, compiled NO new specimen against
  DR, and changed NO compiler/harness code. Every "unsupported"
  classification is backed by a DR .REL external-reference set, a DR
  .PRN CODE/DATA figure, or a local run of the current build (the
  micro-tests quoted in section 4 are reproducible in one line each).
* Section 4 reports defects as defects. D3 and D4 are FAIL-SILENT
  (wrong output presented as success) -- the worst class under this
  project's rules; they are recommended as step 0 of the next milestone
  precisely so that no future "byte-exact" claim can rest on silently
  ignored options or an unvalidated returns() type.
* Corpus programs with no DR .REL (CALL, INVERT, MAININVT) are DR
  pass-1 SYNTAX rejects (corpus sweep summary.txt = diag), i.e.
  permanently outside byte-parity reach, and are NOT counted as gaps.
* Unlock arithmetic is conservative: a program counts as unlocked only
  when EVERY remaining need cluster is covered, and clusters come from
  DR's own external references plus source-verified constructs, never
  from first-blocker headlines.
* Checkpoint convention honoured: this audit is analysis + 2 document
  files; no code lines were added, and implementation pauses here for
  approval.

## 10. POST-DFACT ADDENDUM (E2E-6 DEC core accepted, same day)
DFACT is byte-exact, so the corpus score is **3/41 (DEMO, RFACT, DFACT)**
with 0 divergent compiles and 0 crashes. Nothing else in this audit's
structure changes; only the numbers move, and the ranking shift is small
but real. Updated without any new dashboard or infrastructure.

* Emitted PLILIB baseline: 29 -> **36** entrypoints (7 new DEC routes:
  ?DADOP ?DSUOP ?DMUOP ?DSTOP ?QDCOP ?QDDSR ?QI15D ?DCRET -- ?DLDOP,
  ?QDI15 and ?DSUOP already came from the N301/N306 constant-fold path).
* DEC-core unlock arithmetic was CORRECT: it bought exactly one program
  (DFACT). No other corpus program became byte-exact from DEC storage /
  arithmetic / return / default-editing alone.
* Distances fell as predicted, and the metric earned its keep:
  | program | REV 2 unseen | now | remaining |
  |---|---|---|---|
  | DFACT | 4 | **0** | accepted, byte-exact |
  | ACK | 3 | **1** | ?QCIOP + multi-arg + GET-num + stack-option + rep-gen |
  | LOAN1 | 10 | **5** | ?DCMOP ?DDVOP ?DROUN ?QCDOP ?QDDSL (compare, divide, round, GET-of-DEC, scale-shift) |
  | DECPOLY | 9 | **3** | ?DCMOP ?QCDOP ?QDDSL + multi-arg + %replace |
  | IFACT | 2 | 2 | unchanged (?EDITF ?EDTOV) -- DEC work touched nothing on its path |
  | COPY | 4 | 4 | unchanged (?OIOOP ?SIOOP ?RNIOP ?WNIOP) |
  | FFACT | 5 | 5 | unchanged (FLOAT) |
* Re-ranked next three original corpus programs:
  1. **IFACT** -- still #1: 2 unseen routes, the EDIT cluster is a
     prerequisite of 17 programs, and it is the cleanest editing
     specimen (no procedure, no stop, 384 B). Now blocked behind a
     *correct* refusal (D1 closed) rather than a crash.
  2. **LOAN1 (DEC completion)** -- newly #2, promoted by this milestone:
     it halved its distance and what is left is entirely INSIDE the
     model just proven (the decimal stack): ?DCMOP compare, ?DDVOP
     divide, ?DROUN round, ?QCDOP DEC-input, ?QDDSL scale-shift. Risk
     per route is low because each already has a readable DR trace from
     R507/R512; the open questions are the non-commutative compare
     operand order and the meaning of the two `MVI A,06`s around DDVOP,
     both resolvable with ~4 targeted probes. It pays for DECPOLY/ACK/
     ACKTST/ANNUITY/REPORT/UPDATE/CREATE/RETRIEVE/LOAN2 as well.
  3. **COPY** -- still #3 (4 routes, largest cluster, needs the
     file-staging infrastructure decision before runtime proof).
  Downgraded: **ACK** is now only 1 route away in the RTL sense, but it
  needs OPTIONS(STACK(n)) *modelled*, not just refused (defect D3), and
  multi-arg + GET-num + the REPSPEC/Pi_rep family; it stays the
  multi-arg capstone, not a standalone milestone.
* Fail-loud perimeter after E2E-6 (each a tested negative): DEC compare,
  DEC divide, DEC precision outside 1..15 (DR's own NOT IMP at 31),
  literal-scale loss, mixed DEC/INT arithmetic, PUT EDIT/ITEM/bare SKIP,
  non-MAIN block options, non-{FIXED, DEC<=15} return types.
* Process note: the audit's defect list was closed BEFORE the feature
  work (commit 64da8f9), which paid for itself immediately -- DFACT's
  first refusal was `returns(FIXED DECIMAL(15,0))`, the exact gate C084
  now opens on evidence, and FFACT's plausible-but-wrong .REL became a
  loud refusal instead of a false pass.

---

# REV 1 — PL/I-80 corpus audit (2026-10-17, post-E2E-4) — ANALYSIS ONLY

 (2026-10-17, post-E2E-4) — ANALYSIS ONLY

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

## 11. SLICE-1 NOTE (E2E-7A decimal comparison landed, same day)
Decimal comparison is implemented and banked as C085 (111 specimens
byte-exact; 15 new comparison/peephole specimens also .COM-identical and
console byte-equal). Two general DR laws came out of it and were needed
for LOAN1 anyway: the HL-constant-reuse elision and DECIMAL pool reuse
(the latter CORRECTS a claim in C084), plus a correction to C084's
literal-precision law (additive `+`/`-` literals align to the DEC
partner; multiplicative ones keep own digits/scale 0).
LOAN1's remaining work is assessed in spec/notes/e2e7-loan1-dependencies.md:
the routine-surface distance of 5 is accurate but incomplete -- numeric
GET and MOD-in-condition need ZERO new routines, and the compare/divide/
round slices are 3 of the 5 packages. The published LOAN1 schedule
(Applications Guide) was reproduced independently with Decimal arithmetic
before any LOAN1 code existed, so the acceptance oracle is already
validated.
