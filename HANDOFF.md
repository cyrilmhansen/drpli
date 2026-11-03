# HANDOFF.md — DRPLi

Manual prose wins over the managed block below it. Do not hand-edit the managed block.
This file is the recovery entry point: exactly ONE active Next-action heading at level 2. Closed-phase
history is archived under `docs/history/` (index: `docs/history/README.md`); science is
authoritative only in `spec/CLAIMS.md` and `spec/lab-evidence/`.

## Recovery instructions

1. Confirm the repository and revision:
   `cd /home/john/projects/sushiworks/pli80 && git rev-parse --abbrev-ref HEAD && git rev-parse HEAD && git status --porcelain=v1`
   A dirty `handoff.config.json` is the OPERATOR's standing edit — investigate, never clean,
   never stage, never commit, never revert it. `AGENTS.md` → Protected.
2. Lean recovery: Pi auto-loads `AGENTS.md`; read this file and `PROGRESS.md` NOW.
   `PROTOCOL.md` governs all scientific procedure and is consulted before any unclear
   scientific/policy action; `GOAL.md` and `LEARNINGS.md` remain authoritative and are read
   selectively by pointer. A deferred read never weakens the protocol.
3. Check checkpoint freshness with `/handoff verify`. `stale` or `missing` means: re-derive
   state from commits and lab evidence, then refresh and attest with `/handoff finalize`.
   Do not trust this file's managed block over its prose.
4. Load evidence SELECTIVELY — the ledgers are far larger than the working window; a
   complete read of any of them is prohibited for recovery:
   - `spec/CLAIMS.md`: read ONLY cited claim ids — `grep -n '^## C352' spec/CLAIMS.md` etc.;
     the E2E-49/P4 block starts at `grep -n '^## C348'`; the E2E-48 family is C309..C332,
     E2E-49/P1 is C333..C336, E2E-49/P2 is C337..C341, E2E-49/P3 is C342..C347, E2E-49/P4 is
     C348..C351. The ledger CURRENTLY ENDS at **C352** (fc01-framing console-framing law,
     commit `1e9fad6`) — no claim ids are owed; [C352] is the RUNTIME law cited by every
     functional expectation containing blank lines. The E2E-49/P4 block starts at
     `grep -n '^## C348'`. [C330] carries
     the labelled E2E-49/P1 CORRECTION append (positional length law); [C335]–[C338] carry
     labelled P3 CORRECTION appends and [C346] a labelled CITATION CORRECTION (the numeric
     ORDER law is [C104], never cite legacy [C027]/[C072] in provenance); [C335]/[C337]/
     [C344]/[C346] additionally carry labelled [E2E-49/P4 CORRECTION(S)] blocks (`9c42f3b`)
     and [C348] a labelled [E2E-49/P4 WORDING CORRECTION] (`5b0ccde`); falsified text is kept
     as written (PROTOCOL #2).
   - `spec/COVERAGE.tsv`: header + `grep` the row KEY being edited (15 columns; schema
     `spec/COVERAGE-SCHEMA.md`; validator rules at `tools/coverage_check.py:203-247`).
   - `spec/INVENTORY.txt`: `grep` the specimen/refusal name only. `spec/RUNTIME.txt` and
     `spec/DIVERGENT.txt`: only rows named by the task.
   - Latest round evidence: `spec/lab-evidence/e2e49-p4/{RESULTS.md,HYPOTHESES.md,
     BASELINE-MINE.txt,PLAN.md,mkprobes.py}` (round CLOSED); prior rounds under
     `spec/lab-evidence/e2e48-*/` and `spec/lab-evidence/e2e49-p{1,2,3}/`.
5. Do **not** run the compiler, the oracle, LINK-80, cpmsim, Rune CI or `tools/e2e_gate.py`
   unless the session's actual task is compiler development or gate verification.
6. **No active round** (FS-01 CLOSED 2026-11-02; prior round E2E-50/P2 CLOSED same day). A
   successor WITHOUT an operator instruction confirms HEAD/tree, runs `/handoff verify`, records
   state and STOPS. The E2E-50/P3 shortlist is `spec/lab-evidence/e2e50-p2/REPORT.md` §5 — a
   shortlist, NEVER an authorisation (FS-01 already executed P3-a and a variant of P3-b's
   isolation aim; P3-b's law declaration, P3-c and P3-d remain proposals). Standing boundary:
   `/home/john/pli/*` (Runes lab `/home/john/pli/lab`, `/home/john/pli/cpm`,
   `/home/john/pli/runes-full-runs`) is READ-ONLY for this project
   unless an operator brief authorizes otherwise.
## Last verified state — FC-01 OPERATOR OVERRIDE (2026-11-02; HEAD `6a35b9c`; ledger ENDS C352; hop 5 CANCELLED before it began; new priority = eight adapted historical programs; no OCaml byte changed)

- **OPERATOR OVERRIDE (FC-01, 2026-11-02).** The planned HOP 5 work is CANCELLED: do NOT
  implement `stage_files`/`expected.file_expectations`, FILE-00/01 or the fc01-fileio oracle
  round; do NOT start ONUNIT-00. New priority: **adapt eight operator-selected historical
  programs into a representative PL/I-80 functional corpus** (Weekday, Hammurabi, Hangman,
  Amazing, Tic-Tac-Toe, Life — BASIC; Dhrystone — Pascal; FFT — Rosetta Code PL/I), preserving
  essential functionality, documenting unsupported features instead of silently removing them,
  and prioritising adaptation + functional measurement + compiler-gap identification.
- **Interruption record (measured, not assumed): there was no hop-5 work to interrupt.** At HEAD
  `6a35b9c` the tree carried only the operator's `handoff.config.json` edit and the g145 managed
  block; `stage_files` appears NOWHERE in `tools/functional_runner.py` and `file_expectations`
  exists only as the pre-existing fail-closed rejection (`tools/functional_runner.py:127,
  398-400`), shipped before this directive. No FILE-00/01 or ONUNIT-00 spec, program, fixture or
  probe was ever created and no fc01-fileio round was pre-registered or run — nothing is
  half-edited and nothing was deleted. The hop-4 file-I/O survey and its PROPOSED schema stay in
  `LEARNINGS.md` § 2026-11-02 hop 4 **as a record**: the plan is cancelled, the measured laws are
  not.
- Sources fetched and verified: `build/functional/fc01-sources/` — 10 files, `sha256sum -c
  SHA256SUMS` all OK measured 2026-11-02 (7 BASIC listings, `dhry-pascal.shar`,
  `fft-rosettagit.md`, extracted `FFT-reference.pli`). Third-party bytes stay OUTSIDE tracked
  files; any derivative work must record origin + licence (README § 5.1 rights rule).
- Hop 4 landed `a5815a8`: FLT-01 REV2 (direct `(a + b) = 6.5`, sha `30da237c…`) + BUILTIN-00
  REV2 (LENGTH first, sha `8b90ff2c…`, expectation re-derived `["", "LEN= 10"]` with
  reference.py in the SAME commit) executed to typed COMPILE FAIL attr=`compiler`, messages
  verbatim in `build/fc01/batchB-rev2/records.json` (HEAD `91dd3a7` at execution, compiler
  `edce9e0e…`); rev1 `build/fc01/batchB/` kept as written (FLT-01 rev1 PASS = probe
  falsification, PROTOCOL #2); docs § 7 + six § 1 rows; prose 5 clean; dashboard rc=0.
- File-I/O measured-law inventory, PROPOSED schema design and the ONUNIT-00 **evidence gap**
  (DR named-file ON ENDFILE firing NEVER measured — pre-registered fc01-fileio round required
  first) are in `LEARNINGS.md` § 2026-11-02 FC-01 hop 4 — READ IT BEFORE IMPLEMENTING.

### Superseded prose below kept as written (PROTOCOL #2; full record in git `91dd3a7`)

- Hop 2 commits: `da029ec` pre-registration (probes FCPS1/2/3 + HYPOTHESES + BASELINE-MINE,
  my objects linked/run under DR LINK-80+PLILIB, goldens `golden/fc01ps-my*`) committed
  BEFORE any DR PLI.COM call; `1e9fad6` oracle round (DR accepted 3 ok/3, FCPS1 console
  `X=         1\r\n\r\n` -> H1 ACCEPTED / H2 FALSIFIED kept as written; my .REL whole-file
  BYTE-EXACT to DR on all three; claim [C352]; `spec/lab-evidence/fc01-framing/RESULTS.md`
  § 1-3; coverage 133 rows 0/0 and prose 5 clean MEASURED on this tree). Batch-A first-run
  FAIL records (8 FAIL, attr=undefined, ASSERT-only; LINK/RUN witnessed `done`) kept as
  written in `build/fc01/batchA/records.json` + evidence dirs (ignored working state,
  never laundered; README § 8/§ 9).
- Superseded FS-01-era state below is KEPT AS WRITTEN (PROTOCOL #2).

### Superseded: FS-01 CLOSED (2026-11-02; first two functional PASSes, lane B; hostile suite 194/194; no scientific byte changed)

- FS-01 (operator-authorized bounded mission, baseline HEAD `876ed9e`) landing chain (explicit
  paths, no push): harness F1 fix + C15 pins `d8a0ec1`; TABLE-01 revision + derived expectation
  `5b29957`; `docs/functional-results.md` § 5 record `a0e2a96`; this prose + LEARNINGS/PROGRESS
  close, then guard finalize. Successor instruction: `## Next action` below. TABLE-00 and
  TABLE-01 executed to **PASS** on Lane B after (a) the harness F1 anchor fix in `tools/functional_runner.py`
  (`_run_lane_b`: capture now ends at `D>`/`I/O ran`/`\Z` WITHOUT eating the program's final CRLF;
  a region not newline-terminated before its terminator is `console-terminator-ambiguous` UNKNOWN,
  fail closed) with hostile-suite case C15 (12 checks; suite self-count **194**, all pass), and
  (b) a TABLE-01 **output-statements-only** revision isolating the test from PLILIB's measured
  79-col wrap (source sha256 `4881f187ef1ad9651c48950b76a6cdd959fdcc980ef989580a0fbfa43c0b0863`,
  1366 B, CRLF/^Z/≤71 cols; algorithm/inputs/invariants unchanged; expectation derived from the
  declared design + README § 6 law via `reference.py:table01`, never captured). Executed ACTUALS:
  TABLE-00 .REL 896 B, COM 7552 B, 93 console bytes, complete-stream 2 lines; TABLE-01 .REL 1536 B
  (code=644 data=50), COM 7808 B, 178 console bytes, 3 lines; LINK both `parse_undefined=[]`;
  RUN `done` witness; `--double-run` captures byte-equal. Evidence roots (ignored working state,
  gitignored `build/`): baseline FAIL reproduction `build/functional/fs01-baseline/`, PASS run
  `build/functional/fs01/`, double-run `build/functional/fs01-double/`, Lane-A unchanged check
  `build/functional/fs01-laneA/` (FX-00 PASS, FX-01 FAIL `emulator` intended). Report:
  `docs/functional-results.md` § 5.
- Preserved/untouched: P2 FAIL evidence `spec/lab-evidence/e2e50-p2/step6/RESULTS.md`; all
  goldens, `artefacts/`, `oracle/disks/`, manuals, `ocaml/`, `spec/CLAIMS.md` (ledger ENDS C351),
  `spec/COVERAGE.tsv`; PLILIB wrap law stays `proposed` (NOT characterized — FS-01 boundary).
  Compiler binary used as-built: `pli80c.exe` sha256 `edce9e0e…` (recorded in every PASS record).
- Prior round: E2E-50/P2 CLOSED `876ed9e` (gate ACTUALS 1174/0, 181/181, 9/9, 133/0/0, census
  15/0/26/0, prose 5 clean recorded `d648bcd`; close archive `docs/history/2026-11-02-e50p2-closed.md`).
## TICT-00 hop 7 — STEP 3 PIN LANDED (2026-11-03, continuation chain hop 7; `spec/functional/tests/TICT-00.PLI` pinned + compile-witnessed; reference/JSON/lane/docs/gate OWED at hop 8)

Read `LEARNINGS.md` § "…TICT-00 implementation hop 7" FIRST. Measured this hop: the hop-6 draft
converted and PINNED — CRLF + bare `^Z`, 499 lines, 9300 B, widest line 64 (<= 71), zero tabs /
high bytes / trailing whitespace, no apostrophes inside literals; sha256
`f9320f5a65d98fc3cc2a4aa4688444aab54cba25814ddbfa17ee5b2bd26c04e7`. Compiling the PINNED source:
rc=0, `tict00.REL` **8704 bytes, code=4030 data=36**, `cmp` BYTE-IDENTICAL to the ignored
scratch draft .REL — the encoding conversion changed nothing semantic (first pin-level compile
witness). Re-ran the port simulator on the EXPLICIT script `2 2 9 7 1 10 1 4`: 120 normalized
lines, 1468 raw bytes, terminal `draw`, script consumed, 8 gets, board `1,3,1,3,1,1,3,1,3`,
**THREE** `THAT SQUARE IS OCCUPIED.` lines (86/91/96 — hop-5's "two" stays falsified), line 1
`TIC-TAC-TOE` with NO leading blank, line 120 the exit-CRLF blank [C352]. NEW: full
line-for-line audit of the port against the upstream `TICTACTOE2.bas` (all 94 statements)
PASSes under the declared 1/2/3 value mapping, and two equivalence adaptations are recorded
(the 113/114/115 three-test becomes `k = 1` + two compares — exactly one can fire because
`j <= m <= j + 2`; `t1 / 3` truncates toward zero and equals BASIC `INT()` because `m >= 1` at
l0112). Lane-B RUN of this machine is still UNWITNESSED; a FAIL stays classified, never
laundered. OWED (hop 8): steps 4-10 in the hop-6/hop-7 LEARNINGS §§ (reference mirror +
DERIVATIONS -> diff vs sim norm() BEFORE the JSON -> JSON generated VIA SCRIPT -> 
`--stages source,derivation` -> lane B `build/fc01/corp7` (+double if PASS) -> docs § 12 + § 1 ->
compile-tier gate -> explicit-path commit). No ocaml/harness byte changed; nothing laundered;
ledger ends C352; third-party bytes never tracked; operator `handoff.config.json` untouched/
unstaged; no push; NEVER re-run the retry-DFS search. Renewal 7/12 used — successor = hop 8.

## Superseded: HANG-00 rev1 **PASS** — continuation chain hop 1 COMPLETE (2026-11-03; the operator's renewal reset ended the capped chain recorded below; HEAD `94ebbdb` at execution; renewals AVAILABLE — use `handoff_renew` at safe boundaries, not terminal finalization)

Hop 1 of the continuation chain finished the OWED HANG-00 triple exactly as contracted and it
executed to **PASS** on the FIRST lane-B run: `spec/functional/tests/HANG-00.PLI`
(sha `3e55a44cb4ab5a21ab20f75a9ca4fd5ad67b4d4f0e71afb4dc199405a2a3c04b`, 7508 B, 295 lines,
≤70 cols, CRLF+^Z, apostrophe-free, all PUTs single-item), `reference.py:hang00` (329-line
stream byte-equal to the independent simulator, diffed BEFORE the JSON, plus game-state
invariants), `HANG-00.json` (12 validated capabilities, link_target HANG00, 23 CR-terminated
values + bare `^Z`, notes (1)–(12)). Lane B `build/fc01/corp5/` (HEAD `94ebbdb`, compiler
`edce9e0e…`): SOURCE/DERIVATION/COMPILE (rc=0, 7936 B, code=3550 data=174)/LINK (`HANG00.COM`
12160 B, `parse_undefined=[]`)/RUN (`done`, **6369 console bytes = exactly the raw count the
simulator predicts**)/ASSERT (329-line complete-stream match) — `verdicts: PASS=1 FAIL=0
BLOCKED=0 UNKNOWN=0`; double-run `build/fc01/corp5-double/` byte-equal (`cmp` rc=0). FIRST
corpus lane-B RUN of numeric `GET LIST` + echo on my own binary — the measured echo/framing
laws held; all five previously lane-B-unwitnessed HANG shapes (GET+echo, nested `show` with its
own varying cell, nested DO ×2, goto-in-IF, stage ladder with calls in DO) are now
run-witnessed PASSing. FULL compile-tier gate rc=0: byte panel **1174/0**, negative **181/181**,
divergence **9/9**, coverage **133 rows 0/0**, census **15/0/26/0**, prose **5 clean**
(`build/gate-hang00.log`). No ocaml/harness byte changed; nothing laundered; ledger ends C352;
operator `handoff.config.json` untouched/unstaged; no push. Full measured record:
`LEARNINGS.md` § "…HANG-00 continuation chain hop 1 COMPLETION" + `docs/functional-results.md`
§ 10. **NEXT = program 4 AMAZ-00** — listing ALREADY READ (sha `3f6fa3f2…` verified); scope
FALSIFICATION: this upstream Amazing has NO walk/direction-INPUT phase — generation + print
only, so AMAZ-00 is PURE-PUT (`console_input` bare `^Z`), H/V declared literals 4x4, flat
arrays (`AGG.MULTIDIM` REFUSED), literal-divisor draws only, TAB banner + dimension INPUT
DROPPED (documented), separator-space adaptation, 4 leading blanks [C352]. Full hop-start
analysis + PROPOSED design: `LEARNINGS.md` § "AMAZ-00 hop start" — READ IT FIRST; exact steps
in `PROGRESS.md` → Next action; then TICT-00, LIFE-00, DHRY-00, FFT-00. Record limitations
honestly, do NOT extend the harness.

## Superseded: HANG-00 implementation hop IN FLIGHT — CLOSED AT CHAIN CAP (2026-11-03, renewal 12/12; docs commit `8ddd6c7`; build verified rc=0, compiler `edce9e0e…`; NO lane run, NO gate run this hop; kept as written per PROTOCOL #2 — the operator reset that followed makes "no successor exists" obsolete)

Read `LEARNINGS.md` § "2026-11-03 — FC-01 CORPUS HANG-00 implementation hop (renewal 12/12 =
CHAIN CAP)" FIRST — it supersedes parts of the design-hop contract below. Measured this hop
(**FALSIFIED**): the design hop's step-1 byte model, which assumed consecutive no-SKIP
`put list(ch);` concatenate with NO separator, is WRONG — one blank precedes every PUT LIST item
that is not the first item printed since the last line start, INCLUDING the first item of a
following statement; witnesses are the three stored Batch-A PASS captures
(`build/fc01/batchA2/{PROC-00,HIST-00,TABLE-02}-*/lane-B/run.console.bin`) and DR's own run
goldens (`golden/e32rt_E32B1/E32B1.output.txt` byte-identical to `golden/e32b_E32B1_dr/`).
**Consequence, DECLARED adaptation:** the dash/letter row, the used-letter row and every grid row
render SPACE-separated (no separator-free route exists: `||`, SUBSTR/LENGTH, counted PUT EDIT and
multi-item internal-member PUT are all measured refusals/FAILs). **ACCEPTED:** a consumed GET
CLOSES the line (HAMM-00 committed expectation), so no separator blank follows an echo.
**COMPILE-witnessed (ignored scratch, rc=0, `shapes01.REL` 1280 B code=500 data=17):** nested
`show: procedure (c)` owning its own `character(1) varying` and doing the PUT; `call show(x)`
inside `do i = 1 to n;` with a VARIABLE bound; `call show(44)` literal actual; member→scalar then
`if x = 3 then call show(x);`; `do while` over calls; `get list(g)`; `if x < 4 then goto top;`
(goto-in-IF). Lane-B RUN of all of these is STILL unwitnessed. **RE-DECIDED:** state stays
INTEGER ASCII codes; words are three literal-indexed arrays `dgum(3)/dfly(3)/dslep(7)` plus
`wlit character(9) varying` ('GUM'/'FLY'/'SLEEPER') instead of the packed `w(21)`+`ws(3)` (drops
`st+i-1` subscript arithmetic and a member-loaded `>` compare); grid stays `p(144)` codes with
the stage-cell indices verified from the listing (M1 30,31,32,41,42,44,45,54,55,56; M2 67,79,91,
103; M3 39,52,65,78; M4 47,58,69,80; M5 114,125; M6 116,129; M7 35; M8 27; M9 142,143; M10 135,
136; pole 1,13,…,133; top 1..7; rope 19; row base `(k-1)*12` — literal multiply, NO division).
Capability list validated citable (all rows dr=ACCEPTS / mine=SUPPORTED): DECL.FIXED_BIN15,
DECL.CHAR_VARYING, AGG.ARRAY_1D_FIXED, AGG.VAR_INDEX_LADDER, AGG.ELEM_AS_ACTUAL, LOOP.DO_TO_BY,
LOOP.DO_WHILE_UNTIL, IO.GET_LIST, IO.PUT_LIST_FIXED, IO.PUT_SKIP, EXPR.REL_FIXED_EQ_K,
EXPR.SELF_ADD_LADDER, EXPR.VARYING_X_VARYING, PROC.CALL_COPYIN, TRAN.GOTO_SAME_BLOCK.
INDEPENDENT scratch game model written: `build/fc01-scratch/hang00_sim.py` (separator law, echo
law, [C352] framing, 23-value script). NOTHING TRACKED IS AUTHORED YET: no `HANG-00.PLI`, no
`HANG-00.json`, no `reference.py:hang00`; no lane run, no gate run; ledger ends C352; nothing
laundered; operator `handoff.config.json` stays unstaged; no push.
**CHAIN CLOSED: renewal gate reports 12/12 = `maxRenewals`; `handoff_renew` REFUSES, so there is
no successor session. Resuming HANG-00 (steps 1-10, design hop § + the corrections above) needs an
OPERATOR decision — raise `renewal.maxRenewals` or reset the ignored `.pi-guard` renewal state —
followed by a fresh controlled `pi` launch.**

## HANG-00 design hop LANDED (2026-11-03, renewal 11/12; execution HEADs `610a8df`/`b6ffc92`; no compiler/emulator/gate run this hop)

Read `LEARNINGS.md` § "2026-11-03 — FC-01 CORPUS HANG-00 design hop" FIRST — it carries the
COMPLETE port contract: 3 declared words as ASCII code tables (GUM, FLY, SLEEPER; sequential
rounds replace `RND`+redraw; N=3), all-letter-integer state (no char arrays; member->scalar
before compare, HIST-00 pattern), the nested `show(c)` 34-branch char-varying ladder
(STRNG-00/WKDAY-00 rev3 measured shapes), numeric FIXED GETs (CHARACTER console GET UNMEASURED —
avoided per IO.GET_LIST), the apostrophe rewrites, the `ON M GOTO` -> if-ladder decision
([C209] exists but lane-B runtime dispatch UNMEASURED), the flattened 144-cell grid with the
recomputed stage-cell indices, the removals list (TAB banner, word-guess interlude, 610 quirk,
dead 620/990), the FIXED 23-value game script (win, win-with-one-miss, hang-lose with a 3-hit
letter and a repeat-guess, exhaustion guard `YOU DID ALL THE WORDS!!` -> stop), the capability
id list to re-validate, and the FIVE unwitnessed shapes (first corpus lane-B RUN of a numeric
GET with echo; consecutive no-SKIP PUTs on one line; goto-in-IF; do-while over calls/nested DO;
single-char varying PUT width). NEXT = that section's steps 1-10 (simulator -> draft -> triple
-> derivation diff -> `--stages source,derivation` -> lane B `build/fc01/corp5` ACTUALS
verbatim -> docs § 10 + § 1 -> compile-tier gate -> explicit-path commit). **This successor
session runs on renewal 12/12 — the CONFIGURED CAP: after landing HANG-00, close the chain with
`/handoff finalize` (handoff_finalize); NO renewal beyond 12/12 without an operator reset.**
Programs 4-8 (AMAZ-00, TICT-00, LIFE-00, DHRY-00, FFT-00) stay queued; HAMM-00 rev2
subtraction-loop stays PROPOSED. No ocaml/harness changes; ledger ends C352; no push;
operator `handoff.config.json` stays unstaged; third-party bytes never tracked.

## HAMM-00 rev1 landed — LANE-B COMPILE FAIL (`my-gap`) recorded; triple + docs § 9 + gate green; committed `610a8df` (2026-11-03, renewal 11/12; execution HEAD `5772b8a`; build rc=0, compiler `edce9e0e…`)

Read `LEARNINGS.md` § "2026-11-03 — FC-01 CORPUS HAMM-00 hop 7" FIRST (now carries the
lane-B MEASURED entry). Lane B executed at `build/fc01/corp4/` (`records.json`, HEAD `5772b8a`,
compiler `edce9e0e…`): SOURCE pass (sha `cc25fe75…`), DERIVATION pass (== spec, 211 lines),
COMPILE **FAIL** attr=`compiler` witness `refusal rc=2`, message verbatim `Fatal error: exception
Failure("codegen: DIV by non-constant [TBD]")`; LINK/RUN/ASSERT unrun; `verdicts: PASS=0
FAIL=1`. Classified `my-gap` (`ocaml/lib/codegen.ml:4997-5010` lowers DIV by CONSTANT only,
`[P071B/P080A]`); expectation NOT laundered; ledger ends C352 (a functional run is not a DR
claim; DR variable-DIV stays UNMEASURED). goto-in-IF, adjacent-literal PUT LIST and the c=2/4
rats dispatch NOT reached — still unmeasured. rev2 PROPOSED (subtraction-loop division, derived
stream identical) — recorded, NOT executed. `docs/functional-results.md` § 9 + § 1 row written;
FULL compile-tier gate rc=0 twice, ACTUALS: byte panel **1174/0 of 1174**, negative **181/181**,
divergence **9/9**, coverage **133 rows 0/0**, census **15/0/26/0**, prose **5 active clean**
(log `build/gate-hamm00.log`). COMMITTED at this boundary: explicit paths
`spec/functional/tests/HAMM-00.PLI` (sha `cc25fe75…`), `HAMM-00.json`,
`spec/functional/tests/reference.py`, `docs/functional-results.md`, `LEARNINGS.md`,
`PROGRESS.md`, `HANDOFF.md` prose — NEVER `handoff.config.json`; no push. Then program 3
HANG-00 (Hangman) per the standing corpus procedure (design hop first). No ocaml/harness
changes; third-party bytes never tracked.

## HAMM-00 hop 6 state — PORT DRAFTED (2026-11-03, renewal 9/12, HEAD `39f1d6b`; build rc=0, compiler `edce9e0e…`)

Read `LEARNINGS.md` § "2026-11-03 — FC-01 CORPUS HAMM-00 implementation hop 6" FIRST. The whole
port now exists as ignored scratch `build/fc01-scratch/HAMM-00.draft.pli` (LF; convert to CRLF +
bare `^Z`, check <=71 cols and zero apostrophes, then pin its sha256 as
`spec/functional/tests/HAMM-00.PLI`). The 1:1 `put list(x); put skip;` line law, the blank-line
counts, the three port choices (z++ after the report, `qq` preserved for BASIC 540, the +100
verdict ladder), the kept dead stores, the verified capability ids and the FIVE lane-B-unwitnessed
shapes (goto-in-IF, variable divisors, adjacent-literal PUT LIST, the `c = 2/4` rats dispatch, the
t3/t4 idempotence guard) are recorded there. NEXT = that section's steps 1-8: reference.py:hamm00
(byte model + chk + nested-floor asserts, DIFF against the hop-5 simulator one-liner before any
JSON) -> HAMM-00.json -> `--stages source,derivation` -> lane B `--evidence build/fc01/corp4`
ACTUALS verbatim -> docs § 9 + § 1 row -> compile-tier gate -> explicit-path commit. No
ocaml/harness changes; no push; ledger ends C352; operator `handoff.config.json` stays unstaged.

## HAMM-00 hop 5 state — AUTHORING PLAN FINAL (2026-11-03, renewal 8/12, HEAD `7957474`; build rc=0, compiler `edce9e0e…`)

Read `LEARNINGS.md` § "2026-11-03 — FC-01 CORPUS HAMM-00 implementation hop 5" FIRST — it
carries the EXACT one-liner that regenerates the 211-line expected stream + the exact
`console_input` string from `build/fc01-scratch/hamm00_sim.py` + `spine_t_300.json` (re-verified
byte-stable this hop: verdict not-too-bad, P1=7, L=10, D1=41, all 8 mask features, 46 fed values
max 1588), the harness contracts read from `tools/functional_runner.py` (Lane-B capture includes
GET echoes; echo lines in `expected.console` carry the trailing `\r`; `check_encoding` enforces
only the declared tokens), the verified `capabilities` id list (no ordered-compare row exists —
cite none, WKDAY precedent), and the ONE new design finding: the two 59/61-char BASIC literals
(862/970) don't fit <=71-col `put list` lines — PROPOSED resolution is the adjacent-literal split
whose seam is normalization-invariant (one space either way); compile of literal-literal adjacency
is UNVERIFIED, a FAIL stays classified. Every compare/division/shift site is planned statement-for-
statement (hop-4 + hop-5 §§). NEXT: author `HAMM-00.PLI` (CRLF/^Z/<=71, `hamm00: procedure
options(main);`, no apostrophes, split literals as above) + `reference.py:hamm00` (diff its output
against the simulator one-liner BEFORE writing the JSON) + `HAMM-00.json` (console_input = 46
values each CR-terminated then bare `^Z`; notes = full removal/substitution list incl. variable
division first use flagged, negative e=-600 declared, bells/TAB/217 dropped, integer P1/L/n,
adjacent-literal split PROPOSED) -> `--stages source,derivation` -> lane B `--evidence
build/fc01/corp4` ACTUALS verbatim -> docs/functional-results.md § 9 + § 1 row ->
`python3 tools/e2e_gate.py` compile tier -> explicit-path commit (never `handoff.config.json`);
no push; ledger ends C352; no ocaml/harness changes; third-party bytes never tracked.

## TICT-00 hop start LANDED (2026-11-02; continuation chain hop 3; docs-only, no compiler/emulator run this hop beyond the ignored scratch pre-compiles)

Both Tic-Tac-Toe listings sha-verified rc=0 and READ. **BASE CHOSEN: TICTACTOE2.bas** (sha
`9945f459…`) — TICTACTOE1 (`e1125402…`) never terminates (win/draw both `GOTO 210`; the only
stop would be GET-at-^Z-EOF, UNMEASURED), so no finite complete stream can be derived from it;
the choice + why are recorded. Measured port shapes (my compiler, ignored scratch shapes03/04/
05; NOT DR claims): `DO BY 3` refused → emulate `(jj-1)*3+1`; `> var` and `= -1` (k<=0) refused
→ positive-literal compares + shift idiom `t2 = t1 + 1; if t2 = 0`; expression-left `=` refused
(matches EXPR.REL_VAR_EQ_EXPR pinned REFUSED); ACCEPTED rc=0: scalar=scalar equality, guarded
multi-statement DO blocks, `s(i) = -1` stores. PROPOSED design (numeric choice GET replaces
string C$ GET; flat goto machine; found-flag loop exits; script must reach ONE legitimate END)
is in `LEARNINGS.md` § "TICT-00 hop start" — READ IT FIRST. EXACT NEXT = that section's
implementation hop steps 1-11 in `PROGRESS.md` → Next action (simulator → draft → pin →
reference mirror diff BEFORE JSON → TICT-00.json → source,derivation → lane B corp7 → docs § 12
+ § 1 → gate → explicit-path commit), then LIFE-00, DHRY-00 (NEVER execute the `.SHAR`), FFT-00.
Nothing tracked authored yet for TICT-00; ledger ends C352; nothing laundered; operator
`handoff.config.json` untouched/unstaged; no push.

## AMAZ-00 rev1 LANDED — lane-B **PASS** on the first run (2026-11-02; continuation chain hop 2; execution HEAD `708ce33`; renewals AVAILABLE — use `handoff_renew` at safe boundaries)

Hop 2 of the continuation chain finished AMAZ-00 (program 4 of 8, Amazing maze) exactly as the
in-flight hop left it: pinned program sha `0c0abfab…` (7327 B, pure-PUT — the upstream listing
has NO walk INPUT phase), `reference.py:amaz00` byte-equal to the independent simulator (18
lines, all maze invariants asserted). This hop authored `AMAZ-00.json` (link_target AMAZ00, sha
pin, `console_input` bare `^Z`, 18 expected lines copied verbatim from the derivation, normal-
ization `collapse-spaces-v1`, limits as HANG-00, 9 capabilities each re-verified SUPPORTED/
dr=ACCEPTS this hop — no IO.GET_LIST: no GET in this program), passed `--stages source,
derivation` (SOURCE pin + derivation == spec 18 lines), and ran lane B `build/fc01/corp6/`
(HEAD `708ce33`, compiler `edce9e0e…`): SOURCE/DERIVATION/COMPILE (rc=0, 5760 B, code=3166
data=58)/LINK (`AMAZ00.COM` 10368 B, `parse_undefined=[]`)/RUN (`done`, **189 console bytes =
exactly the simulator's predicted raw count**)/ASSERT (complete-stream match, 18 lines) —
`verdicts: PASS=1 FAIL=0 BLOCKED=0 UNKNOWN=0`; double-run `build/fc01/corp6-double/`
byte-equal (`cmp` rc=0). FIRST lane-B RUN of the flat goto state-machine generator and of
nested `DO TO` print loops with if/else single-item PUTs — both run-witnessed PASSing; the
separator-space adaptation and 8-leading/1-trailing framing [C352] rendered as derived. FULL
compile-tier gate rc=0: byte panel **1174/0**, negative **181/181**, divergence **9/9**,
coverage **133 rows 0/0**, census **15/0/26/0**, prose **5 clean** (`build/gate-amaz00.log`).
No ocaml/harness byte changed; nothing laundered; ledger ends C352; operator `handoff.config.
json` untouched/unstaged; no push. Full record: `LEARNINGS.md` § "…AMAZ-00 COMPLETION hop" +
`docs/functional-results.md` § 11. **NEXT = program 5 TICT-00** (Tic-Tac-Toe, BASIC — TWO
upstream listings tictactoe1/2: read BOTH, pick and record why; if the chosen version uses
character INPUT for moves, adapt to numeric GET (run-witnessed laws) and document); exact
steps in `PROGRESS.md` → Next action; then LIFE-00, DHRY-00 (NEVER execute the `.SHAR`),
FFT-00. Record limitations honestly; do NOT extend the harness.

## Superseded: AMAZ-00 IMPLEMENTATION IN FLIGHT — committed INCOMPLETE (2026-11-02, operator checkpoint instruction; renewal 2/12; kept as written per PROTOCOL #2 — superseded by the LANDED section above)

Pinned `spec/functional/tests/AMAZ-00.PLI` (sha `0c0abfab…`, 7327 B, CRLF+^Z, <=71,
apostrophe-free; scratch-compile rc=0, 5760 B) + `reference.py:_Amaz00Port`/`amaz00()`
(derivation == independent simulator, BYTE-EQUAL 18 lines; all maze invariants PASS:
C=17, permutation, entrance col 1, z=1, 980 fired, 1011..1014 UNREACHED, bottom gap
[3], connectivity). FALSIFIED since hop start: entrance is column 1 (sim reporting bug);
framing is 8 leading blanks + 1 trailing (not 4/none). NOTHING run on lane B; NO JSON
yet; NO PASS claimed. EXACT NEXT (steps 1-6: JSON -> source,derivation -> lane B corp6
-> docs sec 11 -> gate -> explicit-path commit) in `PROGRESS.md` -> Next action and
`LEARNINGS.md` 2026-11-02 AMAZ-00 implementation hop. Constraints unchanged; ledger
ends C352; operator handoff.config.json untouched/unstaged; no push.

## TICT-00 draft COMPILE-WITNESSED — hop 6 closed at context exhaustion (2026-11-03, continuation chain hop 6; HEAD `824be64`; nothing tracked authored, no lane run, no gate run, no commit this hop)

Read `LEARNINGS.md` § "…TICT-00 implementation hop 6" FIRST — full state + exact steps 3-10.
DONE: LF draft `build/fc01-scratch/TICT-00.draft.pli` mirrors `tict00_sim.py` statement-for-
statement (flat l0002..l2000 machine, f-count AND ladders, M=0 shift idiom, flat loops, printer
with b1 ladder + split loop-next/entry labels l1115n/l1150n/l1152n, detector fall-through,
r-dispatch, terminals, l2000 `f = 0; stop;`, nested show after stop, board init s(i)=2) and
FULL-PROGRAM COMPILES rc=0 (`tict00.REL` 8704 B code=4030 data=36 — first machine-wide witness;
individual shapes were probes). Identical-script cross-check RE-VERIFIED on the CONFIRMED
script (port `2,2,9,7,1,10,1,4` -> DRAW, 8 gets, script consumed; BASIC 119 vs port 120 lines,
diffs only prompts+echo, IT IS vs IT'S, trailing exit-CRLF blank [C352]). FALSIFIED: "2
occupied messages" — the script fires THREE (1 occupied, 10 oOR, 1 occupied). OWED (hop 7,
steps 3-10): pin `spec/functional/tests/TICT-00.PLI` (CRLF/^Z/<=71) -> `reference.py
:_Tict00Port`/`tict00()`+DERIVATIONS diffed vs sim norm() BEFORE JSON -> `TICT-00.json`
GENERATED VIA SCRIPT from derive (link_target TICT00, console_input
`2\r2\r9\r7\r1\r10\r1\r4\r^Z`, grep-verified capabilities, full notes incl. THREE occupied,
unreachable 1180/1200/1112/1137 dead, unreached 104/105,133/138,156/158,163/168,187/189) ->
`--stages source,derivation` -> lane B `build/fc01/corp7` (+double if PASS, ACTUALS verbatim)
-> docs § 12 + § 1 -> compile-tier gate -> explicit-path commit (NEVER handoff.config.json;
no push). NEVER re-run the retry-DFS search. Renewal 6/12 used; successor = hop 7.

## Superseded: TICT-00 CROSS-CHECK BLOCKER RESOLVED — draft step in flight (2026-11-03, continuation chain hop 5; HEAD `60e7038`; build verified at session start; NOTHING tracked authored yet, no lane run, no gate run)

Read `LEARNINGS.md` § "…TICT-00 implementation hop, continuation chain hop 5" FIRST — it
carries the FIX (port model `occ()` was one `skip` short: BASIC 506 = message + TWO blanks,
l500 adds the third — `build/fc01-scratch/tict00_sim.py` corrected), the MEASURED result
(port and BASIC models now MATCH on 8/8 identical scripts under collapse-normalization,
modulo prompt text + echo, apostrophe rewrites, and the port's single trailing exit-CRLF
blank [C352]), the CONFIRMED script (`console_input 2\r2\r9\r7\r1\r10\r1\r4\r^Z` — the
hop-4 string dropped the first move 2), the FAILURE LESSON (a retry-DFS re-search blew up
~11h and was aborted — the hop-4 exhaustive game-tree facts stand; 1180/1200/1112/1137 stay
faithful dead code, NEVER re-search), and the COMPLETE statement-level port plan (flat label
machine, f-count AND ladders, shift idiom, flat loops, manual printer loop, detector
fall-through, r-dispatch, nested show, board init s(i)=2). EXACT NEXT = that section's steps
1-10 (draft -> full scratch pre-compile -> pinned `TICT-00.PLI` -> reference mirror diffed vs
simulator BEFORE the JSON -> `TICT-00.json` -> source,derivation -> lane B corp7 ACTUALS
verbatim -> docs § 12 + § 1 -> compile-tier gate -> explicit-path commit). Then LIFE-00,
DHRY-00 (never execute the .SHAR), FFT-00; HAMM-00 rev2 stays PROPOSED. No ocaml/harness
changes; ledger ends C352; nothing laundered; operator `handoff.config.json` untouched/
staged; no push.

## Superseded: TICT-00 IMPLEMENTATION HOP IN FLIGHT (2026-11-03, continuation chain hop 4; HEAD `c6c699b`; build rc=0, compiler `edce9e0e…`; NOTHING tracked authored yet, no lane run, no gate run)

Read `LEARNINGS.md` § "…TICT-00 implementation hop" (two sections: hop-start contract + the
continuation record) FIRST. DONE this hop: sources re-verified rc=0; independent line-for-line
BASIC model `build/fc01-scratch/tict00_bas.py` (instrumented by BASIC line number, real
GOSUB/RETURN fall-through, `INT((M-1)/3)`, values -1/0/1) + exhaustive game-tree searches
(`tict00_dfs.py`, `tict00_full.py`): MEASURED that the HUMAN win (1200) is UNREACHABLE in any
play, that 1180/1112/1137 never fire, and that the max-coverage terminal script is
`O, 2, 9, 7, 1, 10, 1, 4` (94 BASIC lines fired, 2 occupied messages via 503 and 505, ending
DRAW at 1400). Port model `build/fc01-scratch/tict00_sim.py` written on the HAMM/HANG byte model
with the DECIDED value mapping (1=computer, 2=empty, 3=human; g=1 first pass / g=3 second pass) —
first cross-check run agrees modulo spaces/echo-`\r` and on the terminal, but the port has 85
lines vs 84: UNRESOLVED and the two models were fed DIFFERENT scripts in that run (the port got
the leading `2` choice, the BASIC model got `O` + the remaining moves), so re-run the same script
through both before trusting either. Two model bugs found and fixed (missing `self.m`, bad
token). EXACT NEXT (steps 2-11 in `PROGRESS.md` → Next action): re-run the identical script on
both models and find the line-count difference → pre-compile the risky port shapes in ignored
scratch → LF draft → CRLF + bare ^Z + <=71 cols + apostrophe-free `spec/functional/tests/TICT-00.PLI` + sha pin
→ `reference.py:_Tict00Port`/`tict00()` + DERIVATIONS diffed vs the simulator BEFORE the JSON →
`TICT-00.json` (link_target TICT00, `console_input 2\r9\r7\r1\r10\r1\r4\r^Z` if the DRAW script is
confirmed, notes = value mapping + numeric choice + apostrophe rewrites + unreachable
1200/1180/1112/1137 + unreached-line list) → `--stages source,derivation` → lane B
`build/fc01/corp7` (+corp7-double if PASS, ACTUALS verbatim, a FAIL stays classified) → docs § 12
+ § 1 row → compile-tier gate → explicit-path commit. Then LIFE-00, DHRY-00 (never execute the
`.SHAR`), FFT-00; HAMM-00 rev2 stays PROPOSED. Constraints: no ocaml/harness changes; ledger ends
C352; third-party bytes never tracked; operator `handoff.config.json` never staged; no push.

## Next action — FC-01 CORPUS (OPERATOR OVERRIDE, 2026-11-02): adapt the eight operator-selected historical programs into the existing functional corpus. HOP 5 IS CANCELLED — the file-I/O harness extension (`stage_files`, `expected.file_expectations`), FILE-00/FILE-01, the fc01-framing→fileio oracle round and ONUNIT-00 must NOT be started; the hop-4 close-out `6a35b9c` and Batch-B REV2 `a5815a8` stand. Exact procedure in `PROGRESS.md` → Next action. Sources: `build/functional/fc01-sources/` (ignored working state, fetched by the operator's `fc01-fetch-sources.sh`; `sha256sum -c SHA256SUMS` rc=0 measured 2026-11-02; read `URLS.tsv` + `NOTES.txt` before use). REUSE `tools/functional_runner.py` + `spec/functional/tests/` (schema `pli80-functional/1`) AS IT STANDS — **no renewal cycle is to be spent developing test infrastructure**; where the harness cannot test a program adequately, RECORD the limitation and move to the next program. Expensive runtime/link-run regression belongs to the external rune-ci Buildbot (`spec/notes/rune-ci-external-gate.md`); existing CI results validate new corpus programs ONLY if those tests are explicitly included there. Constraints: NO OCaml compiler changes; no push; no new CI framework; no mass documentation cleanup; explicit-path commits only; the operator's `handoff.config.json` edit stays unstaged; renew at safe boundaries per `handoff.config.json` — renewals AVAILABLE on the continuation chain (operator reset 2026-11-03); use `handoff_renew`, not terminal finalization. **WKDAY-00 DONE — rev3 lane-B PASS
(2026-11-03; docs § 8, evidence build/fc01/corp1..corp3).** Program 2 (Hammurabi → `HAMM-00`):
**rev1 RECORDED 2026-11-03** (hops 2–7, this chain; started as the implementation hop at
renewal 4/12). Triple committed at this boundary (`HAMM-00.PLI` sha `cc25fe75…`,
`HAMM-00.json`, `reference.py:hamm00` — derivation == spec, 211 lines, never captured). Lane B
`build/fc01/corp4/` executed to **COMPILE FAIL attr=`compiler`**, message verbatim `Fatal error:
exception Failure("codegen: DIV by non-constant [TBD]")` — first corpus use of VARIABLE
division, flagged run-unwitnessed in spec note (10); classified `my-gap`
(`ocaml/lib/codegen.ml:4997-5010` lowers DIV by CONSTANT only, `[P071B/P080A]`), kept as
written, never laundered; ledger ends C352. docs § 9 + § 1 row written; FULL compile-tier gate
rc=0 (1174/0, 181/181, 9/9, 133/0/0, census 15/0/26/0, prose 5 clean). rev2 subtraction-loop
PROPOSED, NOT executed. Full record: `LEARNINGS.md` § 2026-11-03 HAMM-00 hops + the rev1 state
section above. Program 3 **HANG-00 rev1 LANDED — lane-B PASS on the first run 2026-11-03**
(continuation chain hop 1; state section above; full record `LEARNINGS.md` § "…hop 1
COMPLETION" + docs § 10): triple committed at this boundary (sha `3e55a44c…`, derivation ==
spec 329 lines never captured, 12 capabilities); evidence `build/fc01/corp5/` + byte-equal
double-run; first corpus GET+echo RUN; gate rc=0. Program 4 **AMAZ-00 rev1 LANDED — lane-B
PASS on the first run 2026-11-02** (continuation chain hop 2; state section above; full record
`LEARNINGS.md` § "…AMAZ-00 COMPLETION hop" + docs § 11): triple committed (pure-PUT, bare `^Z`,
9 capabilities, derivation == spec 18 lines never captured; program + reference landed `948f5e5`/
`708ce33`, JSON this hop), evidence `build/fc01/corp6/` + byte-equal double-run, gate rc=0.
EXACT NEXT: program 5 **TICT-00** (Tic-Tac-Toe, BASIC — two upstream listings, read both and
pick) — steps 1-12 in `PROGRESS.md` → Next action; then LIFE-00, DHRY-00 (never execute the
`.SHAR`), FFT-00.
Corpus laws unchanged and now ALL run-witnessed: literal divisors ≤ 127 (variable DIV MEASURED
refused), ordered-compare constants ≥ 1, strict compares (`COND.GE_LE` refused), no apostrophes,
≤ 71 cols, single-item `put list` with the leading-blank separator law across statements, GET
echo `L\r\r\n` closes the line, exit CRLF [C352]; a FAIL stays classified never laundered.

## HAMM-00 hop 4 state — RICH SPINE FOUND (2026-11-03, renewal 7/12, HEAD `9cbd8dc`; build rc=0, compiler `edce9e0e…`)

Read `LEARNINGS.md` § "2026-11-03 — FC-01 CORPUS HAMM-00 implementation hop 4" FIRST — it carries
the COMPLETE verified 10-year plan, the complaint firability conditions, the port compare/division
law and the exact next steps. Summary: hop 3's "no rich path" was FALSIFIED — two bugs in my own
scratch simulator (buy/sell complaints emitted inside the accepted-amount branch; an unconditional
`break` in `insert_complaints`). The fixed simulator finds a spine with ALL EIGHT features (skip,
starve, buy/sell/feed/plant complaints incl. seed + acres + people variants, plague, rats) and the
verdict **not-too-bad** at g0=2, s0=1500 (P1=7, L=10, D1=41, 211 stream lines, 46 fed values, every
intermediate ≤ 32767). Nothing is promoted to any ledger (ends C352); no ocaml/harness byte touched;
no emulator run this hop; the only tracked changes are these durable documents. NEXT: author the
HAMM-00 triple (`.PLI` + `.json` + `reference.py:hamm00`), `--stages source,derivation`, lane B
`build/fc01/corp4`, docs § 9 + § 1 row, compile-tier gate, explicit-path commit.

## HAMM-00 hop 3 state (2026-11-03, renewal 6/12, HEAD `a5ef608`; checkpoint g161 CURRENT by hash replay; build rc=0, compiler `edce9e0e…`)

Read `LEARNINGS.md` § "2026-11-03 — FC-01 CORPUS HAMM-00 implementation hop 3" and
`PROGRESS.md` → Next action "HOP 3 STATE" FIRST — hop 2's draw-residue table is FALSIFIED
(off-by-one: rats fire ONLY at `g0 ≡ 2,3 (mod 5)`, every year; `g0 ≡ 4` = NO rats; yield
`= (2 g0 mod 5)+1`), the "let P collapse" verdict strategy is FALSIFIED (P1 > 33 → FINK), and
complaints are STATE-FREE (search the accepted-amount spine, then insert complaints). The
simulator is rewritten state-based in ignored scratch `build/fc01-scratch/hamm00_sim.py` +
`hamm00_dfs.py`; hop-2 bugs fixed (starve bit never set; `DIED!!`/`GUTS!!` bang counts).
MEASURED THIS HOP: no rich path found — NO spine at (g0,s0) ∈ {(3,900),(3,1200),(3,1500),
(2,900),(7,900),(8,900)} and one spine at (2,1500) with mask {skip,starve}, verdict
`impeached-year10`, complaint insertion failing. NOTHING is promoted to any ledger; no tracked
file changed except these durable docs; no ocaml/harness byte touched; no emulator run this hop.
EXACT NEXT (wider sweep + legal adaptation relaxations, then the triple) is in `PROGRESS.md`.

## HAMM-00 hop 2 state (2026-11-03, renewal 5/12, HEAD `9c91e9f`; checkpoint g159 verified CURRENT by hash replay; build rc=0, compiler `edce9e0e…`)

Read `LEARNINGS.md` § "2026-11-03 — FC-01 CORPUS HAMM-00 implementation hop 2" FIRST:
PUT-LIST inter-item single-blank separator + `%10d` fields MEASURED from the stored
TABLE-00 raw capture (accepted); console_input convention (each GET line ends CR, trailing
`^Z` bare/never consumed, [C113] quoted) accepted; draw residues locked per role under the
5-draws/year cadence — rats-even-not-year-1 FALSIFIED (proposed: g0 ≡ 3 mod 5, rats c=2
every year, yield 5, births c3=1 → bound 20a+s ≤ 32767, plague years 3,5,7,9, prices
26/21); the design's 1300 buy overclaim FALSIFIED at price 26 (33800 overflow, caught by
chk on the first smoke run); 880/885 ladder goes to 565 WITHOUT the 560 line; integer
P1/L adaptation asserted vs float. `build/fc01-scratch/hamm00.py` written (ignored):
byte-level Stream, run(), rich() predicate; searches NOT yet run. EXACT NEXT and full
procedure are in `PROGRESS.md` → Next action (search g0/S0/DFS → emit expected +
console_input + skeleton → HAMM-00.PLI/.json + reference.py:hamm00 → source,derivation →
lane B corp4 → docs § 9 + § 1 → gate → explicit-path commit). No ocaml/harness changes;
no push; ledger ends C352; operator `handoff.config.json` stays unstaged.

## Superseded next action (FC-01 hop 5) — kept as written per PROTOCOL #2; CANCELLED by the operator override above, never started

FC-01 hop 5 EXACT PROCEDURE: `PROGRESS.md` → Next action. (1) implement the file-I/O harness extension per the PROPOSED design in LEARNINGS hop 4 (stage_files + expected.file_expectations; SOURCE sha pin; DERIVATION two-way; export AFTER RUN, BEFORE run.cleanup(), per-seq subdir; ASSERT byte-compare attr=undefined; Lane-B-only; README § 3/§ 4 amendments; hostile-suite C17, printed self-count). (2) FILE-00/FILE-01 specs+programs+derivations from MEASURED laws only ([C295] quotes/[C300] skip/[C280] widths/[C279] naming; payload <128 B, 0x1A pad; input FCB = FILE-variable name + .DAT), run lane B → build/fc01/fileAB, docs § 8. (3) ONUNIT-00 ONLY after a PRE-REGISTERED fc01-fileio oracle round (hop-2 pattern; probes FCFO* + HYPOTHESES + BASELINE-MINE + linkrun.py STAGE_IN/EXPORT_OUT entries committed BEFORE any DR PLI.COM call; claims C353+) measures DR named-file ENDFILE firing — that behavior is UNMEASURED and must not be extrapolated from SYSIN [C110].

(Hop 4 LANDED: Batch-B REV2 `a5815a8` — FLT-01/BUILTIN-00 named blockers measured verbatim
(build/fc01/batchB-rev2); rev1 batchB kept as written incl. the FLT-01 PASS falsification;
docs § 7 + § 1 rows; file-I/O survey in LEARNINGS hop 4. Hop 3 LANDED: framing schema
`51d64bd` suite 211/211; re-derivation `122981a`; Batch-A **8/8 Lane-B PASS** + docs § 6
`38216e3`; Batch-B rev1 probes `2c67c05`.)

FC-01 hop 2 (historical, kept as written): original representative functional corpus (15-25 programs), autonomous across renewals.
Hop 1: 8 Batch-A programs committed (`cae1a50`). Hop 2 (this chain, `da029ec` oracle
pre-registration + `1e9fad6` oracle round): Lane-B chain EXECUTED — 8/8 FAIL at ASSERT ONLY,
all framing artifacts (leading blank line 8/8: first executed put is `PUT SKIP LIST`; MATH-00
also trailing blank: final bare `PUT SKIP;`). fc01-framing oracle round MEASURED the law:
H1 accepted / H2 falsified, [C352]; my FCPS .REL byte-exact to DR on all three probes — the
FAILs are SPEC expectation defects, NOT compiler/runtime gaps. Batch-A FAIL records and
evidence stay on record (build/fc01/batchA; never laundered).
NEXT: (1) harness schema extension — `""` entries in `expected.console` = exact blank line
(tools/functional_runner.py validation ~line 385; README § 3/§ 4 representation note + § 6
framing-law amendment citing [C352]/FCPS/E29PS1); hostile-suite case C16 (schema + ASSERT
blank-line semantics, complete-stream law NOT weakened; suite prints its measured count).
(2) Re-derive reference.py (7 programs prepend ""; MATH-00 also appends ""), update the 8 spec
JSONs (programs UNCHANGED, source shas stand), rerun Lane B `--evidence build/fc01/batchA2`,
record ACTUAL verdicts, commit + `docs/functional-results.md` § 6. (3) Batch B blocker probes
as specs (BUILTIN-00 LENGTH/SUBSTR; STRCAT-00 `||`; COND-00 `|`; DEC-01 fractional literal;
FLT-01 computed compare; EDIT-00 PUT EDIT) — compile-FAIL is the deliverable; keep messages
verbatim. (4) File-I/O harness extension (stage_files/file_expectations mirroring
oracle/linkrun.py STAGE_IN/EXPORT_OUT: input named from FILE variable, output from TITLE first
token no ext [C279]) + FILE-00/01/ONUNIT-00 (ON ENDFILE(<file>)). (5) Keep corpus overview +
4 metrics updated (docs + this prose). Constraints: no OCaml compiler changes; goldens/
artefacts untouched (new fc01-framing goldens are ADDITIVE evidence); explicit-path commits;
no push; renew at safe boundaries per handoff.config.json cap; `/home/john/pli/*` read-only.
## Unfinished operations

- FC-01 hop 5 (file-I/O harness extension, FILE-00/01, the pre-registered fc01-fileio oracle
  round, ONUNIT-00) is **CANCELLED by operator directive 2026-11-02** and is NOT owed. Nothing was
  half-edited, nothing was deleted: no hop-5 code, spec, fixture or probe ever existed.
- ACTIVE: FC-01 CORPUS — the eight adapted historical programs. WKDAY-00 COMPLETE at rev3
  lane-B PASS (evidence build/fc01/corp1..corp3 + corp3-double, ignored; docs § 8 + § 1 row);
  committed `21c9f69`, gate ACTUALS recorded there. HAMM-00 (Hammurabi, program 2) rev1
  RECORDED at this boundary (triple + docs § 9 + § 1 + gate): derivation-green spec
  (`cc25fe75…`, 211 lines, never captured), lane-B **COMPILE FAIL attr=`compiler`** —
  variable-divisor DIV refused verbatim (`codegen: DIV by non-constant [TBD]`), classified
  `my-gap`, kept as written, expectation never laundered; design/port record and every
  falsification live in `LEARNINGS.md` § 2026-11-03 HAMM-00 hops. **rev2 PROPOSED, NOT
  executed:** subtraction-loop division at the four variable-divisor sites (derived stream
  identical; a port change, not a compiler change). Rights/provenance review per program
  (README § 5.1) and the unsupported-feature record stay explicit deliverables; the BASIC
  upstream licences are UNVERIFIED and are recorded as such, not asserted. Program 3
  **HANG-00 rev1 LANDED lane-B PASS** (continuation chain hop 1, state section above; the
capped-chain record below is kept as written and superseded by the operator reset).
- Standing scientific debts unchanged (`PROGRESS.md` → Pending: LOAN2 prescan, CREATE
  `%include`); plus owed: FCPS1..3 SPECIMENS registration at a gate hop.

## Discoveries not yet incorporated

- Hop 4 file-I/O survey (naming [C279]/E16x, content [C295]/[C300]/[C280], 128-B pad fact with
  unestablished cause [C279](b), cpmwork export/import contracts, proposed `stage_files`/
  `file_expectations` schema, ONUNIT-00 UNMEASURED blocker) lives in `LEARNINGS.md` hop 4 —
  PROPOSED, not adopted; README § 3/§ 4 amendments belong to the implementing commit.
- fc01-framing findings stay fully recorded ([C352], RESULTS § 1–3, LEARNINGS hop 2); the
  GET-echo "two extra newlines" observation stays PROPOSED/uncharacterized; FCPS1..3
  SPECIMENS registration stays owed to a gate hop.

## History and pointers

- Superseded next-action sections, closed phase records and the full renewal-hop status
  log: `docs/history/README.md` (index; baseline extraction at `f3a4c60`; P2e closing-era
  prose `docs/history/2026-10-31-p2e-closed.md`; E2E-49/P1 closing-era prose AND the P2e
  close record `docs/history/2026-11-01-e49p1-closed.md`; E2E-49/P2 closing-era prose AND
  the surviving P1 closing-era sections `docs/history/2026-11-01-e49p2-closed.md`;
  E2E-49/P3 two-generation close archive — in-flight prose at `4df35bb` AND the
  close-owed prose at `c140277` — `docs/history/2026-11-01-e49p3-closed.md`;
  E2E-49/P4 four-generation close archive — the arms-era Next actions at `19ab4e0` and
  `e13311c`, the step-6-era CLOSE instruction at `882f77c`, the close-authorized prose at
  `5c52bba` (identical at HEAD `b5f792c`) — `docs/history/2026-11-01-e49p4-closed.md`; E2E-50/P1
  closing-era prose `docs/history/2026-11-02-e50p1-closed.md`; E2E-50/P2 close archive — 8
  Next-action and 7 Unfinished generations + PROGRESS hop stack, 23/23 byte-verified —
  `docs/history/2026-11-02-e50p2-closed.md`).
- Renewal: effective renewal values are in `handoff.config.json` (authoritative) — never
  this file. The guard writes the managed block below via Handoff commands only.

<!-- guard:begin checkpoint -->
checkpoint-schema: 3
checkpoint-generation: 194
checkpoint-id: g194-0a259c9d4a1a
checkpoint-kind: auto
content-delta: new
readiness: attested
status: checkpoint (guard level 3, remaining ~6915, session 01a1a104-4c0b-7601-8f9d-90d0311d9324)
checkpointed: 2026-11-03T11:06:43.421Z
source-goal: 730790b648a1e1d14b76243cfe8bc17eea2ba9cd8527f204f9c8d4dbcc527c9d
source-progress: 47acbfe3da9d28aa60da62347908e00ef971e76529d59bfcad722cf11166dcde
source-handoff: e91d01a5f1e77cdb435b2e070abbfd7cb039512112758d1aaefadb0396077db0
source-learnings: 62a72829107fbb3ec19b48554fdc54c229e7fdb9b4db1df26748591f537d1fb9
source-config: 43186947fdaf3f3b9f425f8ce1b144a8227ce1d7bec2b7aeafb32e9f0572dea8


readiness-by: session:01a1a104-4c0b-7601-8f9d-90d0311d9324
readiness-at: 2026-11-03T11:07:00.857Z
readiness-checkpoint: g194-0a259c9d4a1a
### Last verified state
guard level 3; checkpoint requested (auto at level 3)

### Unfinished operations
- (none recorded)

### Next action
` below. TABLE-00 and
  TABLE-01 executed to **PASS** on Lane B after (a) the harness F1 anchor fix in `tools/functional_runner.py`
  (`_run_lane_b`: capture now ends at `D>`/`I/O ran`/`\Z` WITHOUT eating the program's final CRLF;
  a region not newline-terminated before its terminator is `console-terminator-ambiguous` UNKNOWN,
  fail closed) with hostile-suite case C15 (12 checks; suite self-count **194**, all pass), and
  (b) a TABLE-01 **output-statements-only** revision isolating the test from PLILIB's measured
  79-col wrap (source sha256 `4881f187ef1ad9651c48950b76a6cdd959fdcc980ef989580a0fbfa43c0b0863`,
  1366 B, CRLF/^Z/≤71 cols; algorithm/inputs/invariants unchanged; expectation derived from the
  declared design + README § 6 law via `reference.py:table01`, never captured). Executed ACTUALS:
  TABLE-00 .REL 896 B, COM 7552 B, 93 console bytes, complete-stream 2 lines; TABLE-01 .REL 1536 B
  (code=644 data=50), COM 7808 B, 178 console bytes, 3 lines; LINK both `parse_undefined=[]`;
  RUN `done` witness; `--double-run` captures byte-equal. Evidence roots (ignored working state,
  gitignored `build/`): baseline FAIL reproduction `build/functional/fs01-baseline/`, PASS run
  `build/functional/fs01/`, double-run `build/functional/fs01-double/`, Lane-A unchanged check
  `build/functional/fs01-laneA/` (FX-00 PASS, FX-01 FAIL `emulator` intended). Report:
  `docs/functional-results.md` § 5.
- Preserved/untouched: P2 FAIL evidence `spec/lab-evidence/e2e50-p2/step6/RESULTS.md`; all
  goldens, `artefacts/`, `oracle/disks/`, manuals, `ocaml/`, `spec/CLAIMS.md` (ledger ENDS C351),
  `spec/COVERAGE.tsv`; PLILIB wrap law stays `proposed` (NOT characterized — FS-01 boundary).
  Compiler binary used as-built: `pli80c.exe` sha256 `edce9e0e…` (recorded in every PASS record).
- Prior round: E2E-50/P2 CLOSED `876ed9e` (gate ACTUALS 1174/0, 181/181, 9/9, 133/0/0, census
  15/0/26/0, prose 5 clean recorded `d648bcd`; close archive `docs/history/2026-11-02-e50p2-closed.md`).

### Guard notes
Post-finalize amendment: PROGRESS.md current-phase header updated at commit 26200ca (hop-6 state: draft compile-witnessed rc=0 8704 B, steps 3-10 owed at hop 7; THREE occupied messages). Successor = TICT-00 hop 7 steps 3-10 per PROGRESS Next action + LEARNINGS hop-6 §; pin PLI -> reference mirror + diff vs sim norm (explicit script 2 2 9 7 1 10 1 4) -> TICT-00.json via script -> source,derivation -> lane B corp7 -> docs sec 12 -> gate -> explicit-path commit. NEVER re-run retry-DFS; no ocaml/harness changes; ledger ends C352; no push.
<!-- guard:end checkpoint -->
