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

## Next action — FC-01 CORPUS (OPERATOR OVERRIDE, 2026-11-02): adapt the eight operator-selected historical programs into the existing functional corpus. HOP 5 IS CANCELLED — the file-I/O harness extension (`stage_files`, `expected.file_expectations`), FILE-00/FILE-01, the fc01-framing→fileio oracle round and ONUNIT-00 must NOT be started; the hop-4 close-out `6a35b9c` and Batch-B REV2 `a5815a8` stand. Exact procedure in `PROGRESS.md` → Next action. Sources: `build/functional/fc01-sources/` (ignored working state, fetched by the operator's `fc01-fetch-sources.sh`; `sha256sum -c SHA256SUMS` rc=0 measured 2026-11-02; read `URLS.tsv` + `NOTES.txt` before use). REUSE `tools/functional_runner.py` + `spec/functional/tests/` (schema `pli80-functional/1`) AS IT STANDS — **no renewal cycle is to be spent developing test infrastructure**; where the harness cannot test a program adequately, RECORD the limitation and move to the next program. Expensive runtime/link-run regression belongs to the external rune-ci Buildbot (`spec/notes/rune-ci-external-gate.md`); existing CI results validate new corpus programs ONLY if those tests are explicitly included there. Constraints: NO OCaml compiler changes; no push; no new CI framework; no mass documentation cleanup; explicit-path commits only; the operator's `handoff.config.json` edit stays unstaged; renew at safe boundaries per `handoff.config.json`. **WKDAY-00 DONE — rev3 lane-B PASS
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
section above. Program 3 **HANG-00 (Hangman, BASIC) DESIGN HOP LANDED 2026-11-03** — the
complete port contract, fixed 23-value game script, capability list, removals and the five
unwitnessed shapes are in `LEARNINGS.md` § "2026-11-03 — FC-01 CORPUS HANG-00 design hop"
(read that section FIRST). EXACT NEXT: the HANG-00 IMPLEMENTATION hop — that section's steps
1-10 (scratch simulator on the HAMM byte model -> LF draft -> triple with `reference.py:hang00`
-> derivation-vs-simulator diff BEFORE the JSON -> `--stages source,derivation` -> lane B
`--evidence build/fc01/corp5` ACTUALS verbatim -> docs § 10 + § 1 -> compile-tier gate ->
explicit-path commit). **The implementation session runs at renewal 12/12, the configured cap:
land HANG-00, then close the chain with handoff_finalize — no renewal past 12/12 without an
operator reset.** Corpus laws unchanged: literal divisors ≤ 127 (variable DIV now MEASURED
refused — HANG has NO division by design), ordered-compare constants ≥ 1, strict compares
(`COND.GE_LE` refused), no apostrophes, ≤ 71 cols, a FAIL stays classified never laundered.

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
  upstream licences are UNVERIFIED and are recorded as such, not asserted. Program 3 HANG-00
  DESIGN HOP LANDED (state section above; `LEARNINGS.md` § HANG-00 design hop); implementation
  owed at renewal 12/12 (chain cap — finalize after landing, no renewal past it without an
  operator reset).
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
checkpoint-generation: 173
checkpoint-id: g173-1d75595a1954
checkpoint-kind: manual
content-delta: new
readiness: attested
status: checkpoint (guard level 0, remaining ~64076, session 01a19ce5-2a5d-7761-bfc4-e2869ccffee5)
checkpointed: 2026-11-02T15:44:56.547Z
source-goal: 730790b648a1e1d14b76243cfe8bc17eea2ba9cd8527f204f9c8d4dbcc527c9d
source-progress: 0c86f6e406d19e9eae70c29e147ee5d17152959deba41c17ab8c3912a88e9b9c
source-handoff: 2fd7ec6b632943fe1e21fea5226e67ba1fe3e1dfbf1d360e511953f0c0ae91dd
source-learnings: c97e5bf4a4ef579817dfc4a3245e6331f9c754e63f5ddb5663d1354dcb9397e4
source-config: 43186947fdaf3f3b9f425f8ce1b144a8227ce1d7bec2b7aeafb32e9f0572dea8


readiness-by: session:01a19ce5-2a5d-7761-bfc4-e2869ccffee5
readiness-at: 2026-11-02T15:44:56.551Z
readiness-checkpoint: g173-1d75595a1954
### Last verified state
guard level 0; checkpoint requested (finalize: HAMM-00 rev1 LANDED (610a8df triple+docs+LEARNINGS, b6ffc92 prose hash-record). Lane B FAIL attr=compiler 'codegen: DIV by non-constant [TBD]' = my-gap, kept classified; gate rc=0 1174/0,181/181,9/9,133/0/0,15/0/26/0,prose 5. NEXT: HANG-00 (Hangman) DESIGN hop in-session: read build/functional/fc01-sources/basic/HANGMAN.bas + URLS.tsv + NOTES.txt, rights review README 5.1, feature/capability analysis (corpus laws: literal divisors <=127, variable DIV measured refused, constants >=1 strict compares, <=71 cols, no apostrophes, GET echo law), derive fixed inputs + expected stream, write LEARNINGS design section + docs/PROGRESS/HANDOFF prose, commit design hop; then triple -> --stages source,derivation -> lane B build/fc01/corp5 -> docs sec 10 + sec 1 -> gate -> explicit-path commit. Renewal chain 11/12; ledger ends C352; no ocaml/harness changes; never stage handoff.config.json; no push.)

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
HAMM-00 rev1 LANDED (610a8df triple+docs+LEARNINGS, b6ffc92 prose hash-record). Lane B FAIL attr=compiler 'codegen: DIV by non-constant [TBD]' = my-gap, kept classified; gate rc=0 1174/0,181/181,9/9,133/0/0,15/0/26/0,prose 5. NEXT: HANG-00 (Hangman) DESIGN hop in-session: read build/functional/fc01-sources/basic/HANGMAN.bas + URLS.tsv + NOTES.txt, rights review README 5.1, feature/capability analysis (corpus laws: literal divisors <=127, variable DIV measured refused, constants >=1 strict compares, <=71 cols, no apostrophes, GET echo law), derive fixed inputs + expected stream, write LEARNINGS design section + docs/PROGRESS/HANDOFF prose, commit design hop; then triple -> --stages source,derivation -> lane B build/fc01/corp5 -> docs sec 10 + sec 1 -> gate -> explicit-path commit. Renewal chain 11/12; ledger ends C352; no ocaml/harness changes; never stage handoff.config.json; no push.
<!-- guard:end checkpoint -->
