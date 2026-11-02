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
## Next action — FC-01 CORPUS (OPERATOR OVERRIDE, 2026-11-02): adapt the eight operator-selected historical programs into the existing functional corpus. HOP 5 IS CANCELLED — the file-I/O harness extension (`stage_files`, `expected.file_expectations`), FILE-00/FILE-01, the fc01-framing→fileio oracle round and ONUNIT-00 must NOT be started; the hop-4 close-out `6a35b9c` and Batch-B REV2 `a5815a8` stand. Exact procedure in `PROGRESS.md` → Next action. Sources: `build/functional/fc01-sources/` (ignored working state, fetched by the operator's `fc01-fetch-sources.sh`; `sha256sum -c SHA256SUMS` rc=0 measured 2026-11-02; read `URLS.tsv` + `NOTES.txt` before use). REUSE `tools/functional_runner.py` + `spec/functional/tests/` (schema `pli80-functional/1`) AS IT STANDS — **no renewal cycle is to be spent developing test infrastructure**; where the harness cannot test a program adequately, RECORD the limitation and move to the next program. Expensive runtime/link-run regression belongs to the external rune-ci Buildbot (`spec/notes/rune-ci-external-gate.md`); existing CI results validate new corpus programs ONLY if those tests are explicitly included there. Constraints: NO OCaml compiler changes; no push; no new CI framework; no mass documentation cleanup; explicit-path commits only; the operator's `handoff.config.json` edit stays unstaged; renew at safe boundaries per `handoff.config.json`. **WKDAY-00 DONE — rev3 lane-B PASS
(2026-11-03; docs § 8, evidence build/fc01/corp1..corp3).** Program 2 (Hammurabi → `HAMM-00`):
implementation hop STARTED 2026-11-03 (this chain, renewal 4/12). Read `LEARNINGS.md`
§ "2026-11-03 — FC-01 CORPUS HAMM-00 implementation hop start" FIRST — it RE-MEASURES the echo
witnesses byte-exact (consumed ^Z echoes as the literal chars `^Z` + `\r\r\n`, falsifying the
design hop's blank-row claim; unconsumed ^Z never captured — verified against corp3) and
FALSIFIES parts of the design hop's year-1 script (S≈2400 violates the 20a+s≤6553 bound at the
declared year-1 births draw c=5; year-1 rats draw is ODD; the d=45 survival is right but needs a
tuned opening store s0≈600-900). Everything else in the design hop § stands (draw formula,
shift/compare idioms, `COND.GE_LE` REFUSED → strict-compare forms only, goto same-block, GET
shape, removals list). EXACT NEXT: build `build/fc01-scratch/hamm00.py` simulator with TUNED
starts; iterate to a rich path (complaints, ≥1 plague year, ≥1 EVEN rats year — NOT year 1,
≥1 skip-year, asserts all intermediates ≤ 32767); emit expected lines (echo = `L\r`) +
console_input + PL/I skeleton; write HAMM-00.PLI/.json; `--stages source,derivation`; lane B
`--evidence build/fc01/corp4`; docs § 9 + § 1; gate; explicit-path commit.

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
  committed `21c9f69`, gate ACTUALS recorded there. HAMM-00 (Hammurabi, program 2) DESIGN IS
  COMPLETE AND COMMITTED: measured console-GET echo environment law, GET/GOTO shape
  confirmations, bin15 scaling analysis and the full port design are in `LEARNINGS.md`
  § 2026-11-03 HAMM-00 design hop — the successor reads that section and implements the
  triple (prototype simulator → HAMM-00.PLI/.json → derivation check → lane B corp4 →
  docs § 9 + § 1 → gate → commit). Rights/provenance review per program (README § 5.1)
  and the unsupported-feature record are explicit deliverables; the BASIC upstream licences
  are UNVERIFIED and are recorded as such, not asserted.
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
checkpoint-generation: 161
checkpoint-id: g161-eabfea340059
checkpoint-kind: auto
content-delta: new
readiness: attested
status: checkpoint (guard level 4, remaining ~4941, session 01a19c03-9d8d-7761-bfc4-e26ee7d3f66c)
checkpointed: 2026-11-02T11:55:09.636Z
source-goal: 730790b648a1e1d14b76243cfe8bc17eea2ba9cd8527f204f9c8d4dbcc527c9d
source-progress: bd8f5c070f0492c921bc159e2ae1a3232deef2ff287effe07016ceca661ca996
source-handoff: 5b54547bafba58b7ba98810d943455c2ba9e9308e39da51ca1ba0886eadec089
source-learnings: 899e3a9d0ed49b35c020ee00b44a7241ef59f40790c4054ba82954aee806203c
source-config: 43186947fdaf3f3b9f425f8ce1b144a8227ce1d7bec2b7aeafb32e9f0572dea8


readiness-by: session:01a19c03-9d8d-7761-bfc4-e26ee7d3f66c
readiness-at: 2026-11-02T11:55:20.840Z
readiness-checkpoint: g161-eabfea340059
### Last verified state
guard level 4; checkpoint requested (auto at level 4)

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
FC-01 CORPUS HAMM-00 (program 2, Hammurabi): DESIGN COMPLETE and committed at cb223ba. Implement from LEARNINGS.md section "2026-11-03 — FC-01 CORPUS HAMM-00 design hop" (read it FIRST — echo environment law from golden/e32rt_NETWORK + e29dr_runB transcripts, GET/GOTO confirmed shapes, bin15 scaling analysis A=300/S~2400/P=95, draw formula gg*37+11, parity/impeach reconstructions, script plan) + PROGRESS.md Next action. Steps: prototype reference.py:hamm00 simulator in build/fc01-scratch (iterate 10-year script: complaints, plague, rats-even draw, starvation bounds, assert all intermediates <32767; stream = PUTs + echo lines with trailing CR + C352 framing), then HAMM-00.PLI (CRLF ^Z <=71, header naming HAMMURABI.bas sha 93fea01f...) + HAMM-00.json (provenance third-party licence UNVERIFIED, capabilities incl IO.GET_LIST/TRAN.GOTO_SAME_BLOCK, console_input numeric lines + ^Z), --stages source,derivation, then lane B --evidence build/fc01/corp4, ACTUALS verbatim, docs/functional-results.md new section + section-1 row, e2e_gate compile tier, explicit-path commit. Corpus rule: literal divisors <=127, ordered-compare constants >=1 (shift forms for <0/>0); variable divisors (p,c,z) run-unwitnessed — first corpus use. Constraints: no ocaml changes, no harness changes, no push, operator handoff.config.json stays unstaged, third-party bytes never tracked, ledger ends C352 (functional runs are NOT DR claims), renew at safe boundaries (chain 3/12 used).
<!-- guard:end checkpoint -->
