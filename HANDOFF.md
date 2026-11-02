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
## Last verified state — FC-01 hop 2, fc01-framing round CLOSED (2026-11-02; HEAD `1e9fad6`;
ledger ENDS C352; Batch-A Lane-B executed: 8/8 ASSERT FAIL = spec expectation defects, NOT
compiler gaps; no OCaml byte changed)

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
## Next action — FC-01 hop 3 LANDED (commits `51d64bd` schema/C16 211/211; `122981a` re-derivation; `38216e3` Batch-A **8/8 Lane-B PASS** + docs § 6; `2c67c05` Batch-B 6 probes: 5 typed COMPILE FAILs verbatim, FLT-01 rev1 PASS = probe falsification). HOP 4 EXACT PROCEDURE: `PROGRESS.md` → Next action (FLT-01/BUILTIN-00 REV2 + rerun batchB-rev2, docs § 7, then file-I/O harness extension + FILE-00/01/ONUNIT-00).

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

- FC-01 hop 4 owed: FLT-01 REV2 (direct `(a + b) = 6.5`) + BUILTIN-00 REV2 (length first),
  rerun to build/fc01/batchB-rev2, docs/functional-results.md § 7 — exact procedure in
  `PROGRESS.md` Next action. Nothing half-edited in Git at this boundary; rev1 evidence
  (incl. the FLT-01 PASS) stays on record as written. File-I/O extension + FILE-00/01/
  ONUNIT-00 follow. No compiler process running.
- Standing scientific debts unchanged (`PROGRESS.md` → Pending: LOAN2 prescan, CREATE
  `%include`); plus owed: FCPS1..3 SPECIMENS registration at a gate hop.
## Discoveries not yet incorporated

- fc01-framing findings FULLY recorded: [C352] in the ledger,
  `spec/lab-evidence/fc01-framing/RESULTS.md` § 1–3, LEARNINGS 2026-11-02 FC-01 hop 2
  (accepted law; falsified H2 kept as written). OPEN: the proposed `""` blank-line
  representation in `expected.console` and README § 4/§ 6 amendment (in flight — see Next
  action 1; NOT yet implemented); the GET-echo "two extra newlines" observation stays
  PROPOSED/uncharacterized (no claim); FCPS1..3 SPECIMENS registration stays owed to a gate
  hop; no RUNTIME.txt row came from this round.
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
checkpoint-generation: 142
checkpoint-id: g142-25ea1d801462
checkpoint-kind: manual
content-delta: new
readiness: attested
status: checkpoint (guard level 4, remaining ~1189, session 01a19b41-bc89-7388-bbdc-4f2ea8e5a736)
checkpointed: 2026-11-02T08:28:17.364Z
source-goal: 730790b648a1e1d14b76243cfe8bc17eea2ba9cd8527f204f9c8d4dbcc527c9d
source-progress: 02d8805845ee7fceff50ee959fbd9d4a9b61cbff38e72206307a54fde24a9db1
source-handoff: d07f19e637888f37dfdbc7afce17d3281c65c0a3e6642374ff2050d40a68d74b
source-learnings: 62a72f5f0e75ff9154bf7b0985e552664852dac06640719a59f03a11d79a1912
source-config: 43186947fdaf3f3b9f425f8ce1b144a8227ce1d7bec2b7aeafb32e9f0572dea8


readiness-by: session:01a19b41-bc89-7388-bbdc-4f2ea8e5a736
readiness-at: 2026-11-02T08:28:17.367Z
readiness-checkpoint: g142-25ea1d801462
### Last verified state
guard level 4; checkpoint requested (renewal tool refresh)

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
FC-01 hop 3 CLOSED-OUT: framing schema 51d64bd (suite 211/211 measured), re-derivation 122981a, Batch-A 8/8 Lane-B PASS + double-run + docs sec 6 (38216e3), Batch-B probes 2c67c05 (5 COMPILE FAILs verbatim in build/fc01/batchB; FLT-01 rev1 PASS = probe falsification kept as written). HOP 4 per PROGRESS.md Next action: FLT-01 REV2 direct (a+b)=6.5 + BUILTIN-00 REV2 length-first, rerun --lane B --tests FLT-01 BUILTIN-00 --evidence build/fc01/batchB-rev2, docs sec 7 + sec 1 rows, commit; then file-I/O harness extension (STAGE_IN/EXPORT_OUT mirror, input=FILE var name, output=TITLE first token no ext [C279]) + FILE-00/01/ONUNIT-00. No ocaml changes; explicit paths; no push; operator config edit stays unstaged.
<!-- guard:end checkpoint -->
