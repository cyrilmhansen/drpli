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
>
> **SUPERSEDED AGAIN, 2026-10-19 (E2E-7A slice 4): LOAN1 is byte-exact, so the
> corpus score is 4/41 (DEMO, RFACT, DFACT, LOAN1)** -- see section 14, which
> also corrects a false statement that section 13 made about LOAN1 and MOD.
>
> **SUPERSEDED AGAIN, 2026-10-19 (E2E-8 slice 5): IFACT is byte-exact, so the
> corpus score is 5/41 (DEMO, RFACT, DFACT, LOAN1, IFACT)** -- see section 15,
> which adds PUT EDIT (?EDITF/?EDTOV) with its format-table pool law, the DO/BY
> lowering laws, a fixed-bin subtraction defect repair, and a fresh full-corpus
> first-blocker sweep that changes the ranking of the next milestone (DECPOLY is
> now blocked by the BINDER, not by DEC formal passing).
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

## 12. SLICE-2 NOTE (E2E-7A decimal divide + scale law, 2026-10-18)

C086 banks ?DDVOP/?QDDSL/?QDDSR and a single unified model of DR's decimal
stack: entries carry (p digits, s scale), QDDSL/QDDSR shift the CURRENT TOP
(their position in the sequence identifies which operand is being adjusted),
and the value's final scale is decided by its CONSUMER, not its producer.
Division pre-shifts the dividend by N = 15 - p_dividend (omitted at N=0,
which is why LOAN1's `i*P/1200` shows no pair) and TRUNCATES; the quotient's
own precision is never observable, so it stays [TBD].

Corrections to previously banked claims (all recorded in C086, not silently):
C084's "ADD/SUB never carry a rescale" was incomplete (unequal scales do),
C084's post-multiply rescale formula was wrong (amount = result_scale -
consumer_scale, not target_scale), and C085's HL-reuse peephole is
straight-line only (R723 reloads `LXI H,0000` inside an else branch).

One FAIL-SILENT defect found and closed: a FIXED DECIMAL formal parameter is
passed by reference into a 2-BYTE pointer cell (prologue SHLD of the caller's
address, reads via LHLD + ?DLDOP). My build sized it as a full BCD cell and
pushed LXI H instead -- wrong AUTO storage AND wrong address, with no
diagnostic. It now refuses [N33_DEC_FORMAL]. This is a THIRD decimal work
package (formal-parameter passing) for the ranking, distinct from round()
and GET; it gates DECPOLY but not LOAN1, whose remaining unseen routes are
now only ?QCDOP and ?DROUN (2 of 23).

Verification standard held: 135/135 byte-exact (23 new divide specimens, plus R512
promoted from old divide-refusal evidence to positive), 30/30 negative panel,
and for all 23 new specimens linked .COM identity + COMPLETE console-transcript
byte-equality (every one terminates with `stop;`, so no bounded-prefix
protocol was needed). Additionally tools/decmodel.py -- an independent
Python simulator of the stack that emits both the token schedule and the
printed field -- matches DR's schedule on 49/49 decodable DEC probes (0
differences) and DR's console values on 22/22 decimal-printing ones; it
declines 4 DEC-*call* shapes by design (R506/R509/R709/R725), which are
model limits, named rather than averaged away. It surfaced that a decimal
divide is computed at 15 working digits then PADDED (R716 prints
2.33333300, not 2.33333333).

Sweep-wording correction recorded with the slice-2 data: the corpus has 44
sources (41 with DR goldens), and 2 of them -- CALL and LABELS -- fail
loudly with a nonzero exit but WITHOUT the literal [TBD] tag (parser
"expected statement" / codegen "undeclared x"). A clean build of 3636eec
behaves identically on both, so they are pre-existing diagnostic-wording
debt rather than new crashes; earlier "0 crashes / all loud [TBD]" lines are
read as "0 crashes, 39 tagged refusals, 2 untagged-but-loud refusals".

## 13. SLICE-3 NOTE (E2E-7A FIXED DECIMAL ROUND, 2026-10-19)

C087 banks ?DROUN from 13 fresh DR specimens (R801-R813): the single byte
argument is k = entry_scale - n (DIGITS TO DROP, not the requested scale),
k=0 is still emitted, and the rounded entry KEEPS its scale -- which is why
R801's store still needs QDDSR 1 and LOAN1/R813's enclosing + still lifts the
other operand with QDDSL. ROUND therefore needed no new shift machinery: it
reuses the C086 alignment/consumer laws verbatim.

The rounding MODE question that C084/C086 deliberately left open is now
closed by DR's own runtime: HALF-UP, AWAY FROM ZERO, falsified against
HALF-EVEN by 2.125 -> 2.13 and 2.145 -> 2.15, and against toward-+infinity by
-2.125 -> -2.13; round(2.5,0) -> 3. ROUND also acts on the PRE-STORE stack
value (R804 prints 0.67 for round(2/3,2) beside 0.66 for the stored
quotient), which is the difference between "correct" and "looks like the
1970s compiler" in a payment schedule.

LOAN1's own ROUND line is byte-exact in isolation (R813 = `P = P +
round(i*P/1200, 2)` with LOAN1's declarations, printing 505.83), so the
schedule generator is now complete except for numeric GET: unseen routes for
LOAN1 are down to 1 of 23 (?QCDOP). MOD-in-condition, which the ranking
counted as a LOAN1 blocker, is not one -- LOAN1 contains no MOD.

> **THIS PARAGRAPH'S LAST SENTENCE IS FALSE -- corrected in section 14.**
> LOAN1 does contain MOD (`if mod(m,12) = 0 then`, line 26, DR code 00CC), and
> that condition form was the second thing slice 4 had to implement. Kept
> verbatim above because the error and its correction are both part of the
> record.

Process note worth keeping: my first R813 build produced layout-WRONG bytes
silently (the pool prescan had no ROUND case, so the literal 1200 cell inside
the call went uncounted and the AUTO base shifted 3 bytes). Generating the
LOAN1-shaped probe BEFORE writing the implementation is what caught it; the
simpler probes R801-R807, whose round arguments contain no literals, would
have passed regardless. Fail-silent defects hide in the interaction between a
new construct and an old accounting rule, not in the new construct alone.

Gate state: e2e 143/143 byte-exact, negative panel 38/38 (N36-N43 added, each
with a refusal-reason marker), parse 445 ok / 6 parity-rejects / 0 FAIL of
451, bind 47/47, rel round-trip 423/423, ir 0 FAIL, safety 28/28, corpus
unchanged at 3/41 byte-exact / 0 divergent.

## 14. SLICE-4 NOTE (E2E-7A numeric GET + MOD-in-condition, LOAN1 accepted, 2026-10-19)

**Corpus score: 4/41 byte-exact, 0 divergent** -- DEMO, RFACT, DFACT and now
**LOAN1**, the 4th historical corpus program accepted at raw byte parity.
LOAN1's `.REL` (1536 B) is `cmp`-identical to `golden/first8080u/LOAN1/LOAN1.REL`,
its linked `.COM` (9984 B) is identical to the .COM built from DR's own .REL
against the same PLILIB, and its console output is byte-equal over the first 27
complete records under the bounded-prefix protocol (LOAN1's outer
`do while('1'b)` does not terminate on the scripted input, so a
timeout-truncated capture is not used as the oracle). Its financial schedule
was re-computed independently in Python `decimal` and matches all 27 rows.

Emitted-routine surface: LOAN1 needs **23** PLILIB entrypoints and my build now
emits **23 of 23**; the project's emitted set grew by 3 with this slice
(`?QCDOP`, `?QCIOP`, plus `?IMDOP` reaching a second syntactic role -- it was
already emitted as an expression, so the entrypoint count is unchanged for it).
The decimal-adjacent gap that had sat at "1 of 23" after slice 3 was in fact
**two** blockers, and the mismatch is the lesson of this slice:

> **Route counting measures WHICH routines a program needs, not the number of
> lowering rules.** `?IMDOP` was already emitted (as `r = mod(a, b)`), yet
> `if mod(m,12) = 0 then` still refused, because DR lowers a MOD in a CONDITION
> with a bare HL-zero test and a divisor form that differs from the expression
> form. A "seen" route can hide an unseen rule. Conversely the routine-surface
> metric remains a ranking device, not an effort estimate -- this slice was
> advertised as "numeric GET" and needed 16 probes, 2 lowering rules and 1
> non-decimal condition form to close.

Two rules landed (C088, C089). The GET law is worth repeating here because it
inverts the decimal scale law the previous slices banked: in arithmetic, the
CONSUMER fixes the scale (C086's `?QDDSL`/`?QDDSR` shifts), but in GET the
PRODUCER does -- `?QCDOP` takes the target scale in B and delivers a value
already at that scale, so no shift instruction appears in any GET, and `MVI B`
is emitted even for scale 0 [R905]. Six GET precisions/scales sampled; no claim
about unsampled ones.

Two near-misses, both caught before shipping, both of the kind this project has
now seen three times (fail-silent interaction, not fail-silent novelty):

1. **An over-broad pattern.** The new condition arm matched `Ast.EqR r` with r
   unrestricted, so `if mod(i,12) > 0 then` compiled silently into a bare
   HL-zero test carrying DR's `<>` skip byte -- semantically wrong code that no
   byte comparison against an existing golden would have flagged, because no
   golden had that shape. Fixed by narrowing to `Eq | Ne` and turning the shape
   into a tested negative [N47]. Lesson: when adding a matcher, probe the shapes
   you intend to REFUSE, not only the ones you intend to accept.
2. **A vacuous console arm.** Harness edits to `oracle/linkrun.py` used
   `str.replace()` without asserting, so four probes never got their input
   scripts, ran on default EOF, printed 2 bytes, and "passed" byte-equality
   against DR's equally-empty capture. Lesson: assert on every harness edit, and
   read the transcript content, not just the verdict word.

Gate state: e2e **160/160** byte-exact (was 143; +16 GET/MOD positives + LOAN1),
negative panel **39/39** (3 GET negatives promoted to positives -- they were
refusing only because numeric GET did not exist; 4 new tested negatives N44-N47),
parse 461 ok / 6 parity-rejects / 0 FAIL of 467, bind 47/47, rel round-trip
440/440, ir 0 FAIL, safety 28/28, corpus **4/41 byte-exact / 0 divergent**.
Clean-build warnings unchanged against the `3636eec` baseline. Full link+console
regression over every registered positive: reported in section 14.1 below once
the run completes.

Remaining blockers for the next programs are unchanged in kind: PUT EDIT for
IFACT, DEC formal parameter passing [N33] for DECPOLY, FILE/stream sequences for
COPY, and the deferred POINTER/BASED, label-variable, ENTRY/multi-module and
FLOAT families.

### 14.1 Full link + console regression after slice 4 (same day)

`python3 tools/e2e_gate.py --link-run` over every registered positive
(160 specimens), DR corpus goldens linked against the same PLILIB:

* `.REL` byte parity: **160 / 160**, 0 fail.
* Linked **`.COM` byte-identical to DR's**: **118 / 118** on the
  console-whitelist arm (the programs whose transcripts are complete and
  trustworthy). Zero `.COM` divergences.
* **Raw console transcripts byte-equal to DR's**: **118 / 118** (echo, prompts,
  CR/LF and field widths compared as raw bytes, never normalized).
* Remaining 42 specimens ran the mine-only link+execute arm by design (older
  non-terminating or no-output programs whose proof stays at .REL byte parity
  plus the bounded-prefix protocol in `tools/prefix_check.py`); they are not
  counted as console passes and nothing in this slice changed their lowering.
* LOAN1 specifically: `.COM` identical (9984 B) and, via the bounded complete-
  record protocol, 27 records byte-equal -- see section 14 and
  `spec/notes/e2e7a-slice4-get.md` §7.
* Independent model (`tools/decmodel.py`, probes R5-R9): 68 SCHED MATCH /
  0 DIFFER, 30 VALUE-MATCH / 0 VALUE-DIFF, 8 MODEL-REFUSED (5 of them the new
  MOD-condition specimens, which the decimal-stack model deliberately does not
  model). The slice-3 note's "9 model-side refusals" did not reproduce and is
  superseded by this command-line-scoped figure.
* Clean-build warnings: 63 -> **63**, with an identical per-file histogram
  against a freshly built `3636eec` worktree (bind 20, codegen 18, parser 12,
  ir 8, token 4, bin/pli80bind 1) and an identical kind histogram. The baseline
  worktree was created for the measurement and removed afterwards.
* rel round-trip **438 / 438** (421 baseline + 17 new `golden/e2e10/` goldens;
  the count moves with harness scratch state, as documented in section 13).

---

## 15. SLICE-5 NOTE (E2E-8 PUT EDIT + DO/BY, IFACT accepted, 2026-10-19)

**Corpus score: 5/41 byte-exact, 0 divergent** — DEMO, RFACT, DFACT, LOAN1 and
now **IFACT**. Verified on raw bytes, not masked listings: `cmp` clean against
`golden/first8080u/IFACT/IFACT.REL` (384 B); linked `.COM` 9600 B identical to
the image built from DR's own `.REL`; console verified by the bounded
complete-record prefix protocol (IFACT's outer `do i = 0 by 1;` never
terminates, so a truncated capture is never used as the oracle) — first 12
records byte-equal, plus 6 factorial records re-derived independently from
`math.factorial`.

What this slice banked (see `spec/CLAIMS.md` C090-C092 and
`spec/notes/e2e8-slice5-put-edit-do.md`):

| route / law | specimens |
|---|---|
| PUT EDIT: `80 00 \| records \| 81` table encoding, `?EDITF` + `?EDTOV` | R1001-R1010, R1018-R1022 |
| **pool law**: every format table allocated before every other pool item | R1003, R1021, R1022 |
| DO init cost ladder (SHLD / INX H / MVI L / LXI H) + control-flow sensitivity | R1012-R1015, R1030-R1032 |
| DO exit test (rising `b+1`/JP, falling `b`/JM; rungs <= 3 vs `LXI B,-c` >= 4) | R1011-R1013, R1023-R1028 |
| DO increment `LHLD / rungs x \|step\| / SHLD`; literal steps only | R1011, R1013, R1018, R1033 |
| forever WITH BY (no test at all) vs **degenerate** DO without BY (no loop) | R1014, R1030, R1032, IFACT |
| fixed-bin `a - b` via `?IS22N` (defect repair, see C092) | R1035, R1036, R1033 |

Emitted-routine surface: +2 new entrypoints (`?EDITF`, `?EDTOV`).  Two existing
opcodes reached a second syntactic role (`MVI L,imm`; `?IS22N`, previously
condition-only).  IFACT's own requirement was 12 entrypoints and my build emits
12 of 12.

### 15.1 Two things this slice corrected in the record

1. **The E2E-8 assessment (section 3 of `e2e8-ifact-assessment.md`) attributed
   variable-FROM evidence to R1019 and R1020.** Those probe numbers were reused
   for PUT-EDIT shapes in the second round of generation, so the two rows
   described DO probes that do not exist. The variable-FROM law
   (`LHLD src / SHLD index`) is nonetheless solid — it is re-observed on R1014
   and directly in IFACT's own golden — and the assessment file now says so.
2. **The audit's first-blocker table row "DO WHILE/REPEAT/no-TO (DFACT FFACT
   IFACT RFACT)" is stale.** Three of those four are now accepted, and the
   remaining one (FFACT) is blocked by its `FLOAT` return type, not by DO/BY.

### 15.2 Fresh full-corpus sweep (this build, raw `.REL` compare)

41 corpus programs with a DR `.REL`: **5 EXACT / 0 divergent / 36 refused**.
First refusal, grouped:

| first refusal | count | programs |
|---|---|---|
| declared variable kind not in supported subset (FLOAT / FILE / POINTER / BIT(1) / BASED) | **28** | A ALLTST ANNUITY COPY COPYLPT CREATE DEPREC DIOCALLS DIOCOPY DIORAND DTEST ENTER EXPR1 EXPR2 FDTEST FLTPOLY FLTPOLY2 KEYFILE LOAN2 MPMCALLA MPMCALLB NETWORK REPORT RETRIEVE REVERSE REVERT TEST UPDATE |
| `block option STACK(...) deferred` | 2 | ACK, ACKTST |
| binder: `multi-arg call at line 21 deferred` | 1 | **DECPOLY** |
| binder: `procedure gnt without formals` (R425 family) | 1 | FSCAN |
| `returns(FLOAT BINARY(24,0))` | 1 | FFACT |
| `returns(CHAR(10) VARYING)` | 1 | SAMPLE |
| `PUT ITEM` output form | 1 | OPTIMIST |
| undeclared identifier / parse-class | 1 | LABELS |

**Strategic consequence, and it changes the ranking I proposed before:
DECPOLY's first blocker is now the BINDER (`multi-arg call`), not DEC formal
passing.** Implementing DEC-formal-by-reference in codegen alone would still
leave DECPOLY refusing, because `bind` rejects the 3-argument call site before
codegen is reached. Either the binder's multi-arg call-descriptor work comes
first, or the two land together.

The 28-program declaration wall is now unambiguously the largest single lever:
36 blocked programs, 28 of them stopped by a single unsupported *declaration
kind* (FLOAT, FILE, POINTER/BASED, BIT(1)). Small isolated output/loop
perimeters (PUT ITEM for OPTIMIST, CHAR-varying RETURN for SAMPLE) each unlock
at most one program and then hit a bigger wall behind it.
