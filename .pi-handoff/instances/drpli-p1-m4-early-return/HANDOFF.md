# HANDOFF — mission drpli-p1-m4-early-return

Manual prose wins over the managed block below it. Do not hand-edit the managed block.

## Recovery instructions

Lean recovery: `## Next action` here, then PROGRESS.md live heading. Binding science: PLAN
§P1-m4 (`spec/lab-evidence/e2e54/PLAN.md`); evidence log: RESULTS §P1-m4.SA … §P1-m4.T.
Standing: ZERO oracle; sealed instance drpli-p2-diff5 + historical evidence READ-ONLY;
`handoff.config.json` NEVER staged; explicit paths; no push; `eval "$(opam env)"`;
`LC_ALL=C`; direct rc; fresh `--build-dir` scratch; armed `_build/default` may only be
rebuilt from COMMITTED source per the recorded arming decision.

## Last verified state

**E2E-54/P1-m4 IS CLOSED — this mission's work is COMPLETE.** Commits this session chain:
`d25fa628` (Stage A) → `26994b9a` (Stage B backend + 18 pins + §P1-m4.SB) → `669835ba`
(panel §P1-m4.SP, H3 CONFIRMED) → **`6ff755b2`** (Stage C: `tools/mir_aot_ret_test.py` run
GREEN ×2 fresh with MEASURED direct rc 0 and **27 checks**; RESULTS §P1-m4.SC incl. the
C-M4b second-guard deviation) → **`f2bb784c`** (Stage D + CLOSE: D14/D15 QUALIFIED on the
8080 lane via the disposable `stageD/qualify.py` probe rc 0 (cpmsim, ZERO oracle); runner
**14/14 BOTH-PASS** in BOTH modes, MEASURED 57→67 checks, 45→53 controls ALL REJECTED;
THIRD full frozen panel after D all 14 rc 0; RESULTS §P1-m4.CP/.SD/.T; PLAN §P1-m4.13
CLOSED; arch **§7-17** baked; close gate rc 0 1328/1328, 190/190, 9/9, census 16/0/25/0,
prose 5 clean).

H1/H2/H3 all CONFIRMED; §P1-m4.5 post-`ret` ACCEPTED; §P1-m4.8 summary sound, NO widening;
C-M4a/C-M4b failed loudly inside; 9-item deviations ledger RECORDED, NOT fitted; NO STOP
fired. Dual runner now 14/14 (D14=ER01 [4,9,4], D15=ER02 [3,12]). ret-runner 27 checks.
Ledger 203/C380 UNMOVED; `handoff.config.json` never staged; no push ever.

Working tree at `f2bb784c`: `git diff --exit-code -- ocaml/ hir/ tools/ spec/` rc 0 (verified
after the last commit). Only the usual infra dirty files (.pi/, .agents/, handoff.config.json)
and historical ignored/untracked evidence remain.

## Next action

**NONE — STOP is binding (§P1-m4.11/§P1-m4.12-5): campaign E2E-54/P1-m4 is CLOSED; any
extension requires a NEW operator brief.** This session should finalize the checkpoint
(done via /handoff finalize) and close. If the operator opens new work in this directory,
start from their brief, not from this file.

## Unfinished operations

None. All five §P1-m4.12 items complete (A, B, C, D-conditional, CLOSE).

## Discoveries not yet incorporated

All baked: arch §7-17 (post-`ret` acceptance = real jump-reachable code; bare-decimal
immediates / `i64:k` = MEMORY operand; the §P1-m4.3 classifier is a SECOND guard over
loop-nested RETURN); the PL/I `then do; … end;` idiom and the remaining open question
(is the §P1-m0.3-3 return-window check reachable for an early RETURN at all? — ERN9
question, claim neither way) live in this instance's LEARNINGS.md.

## Blockers

None. Renewal chain 3/12. Mission lifecycle: ready to close with the operator.
<!-- guard:begin checkpoint -->
checkpoint-schema: 3
checkpoint-generation: 9
checkpoint-id: g9-b25a63ffa794
checkpoint-kind: manual
content-delta: new
readiness: attested
status: checkpoint (guard level 0, remaining ~29709, session mission:drpli-p1-m4-early-return:01a1dcc3-c4c2-7282-8059-fdf1a3fd1652)
checkpointed: 2026-11-15T02:37:16.168Z
source-goal: 730790b648a1e1d14b76243cfe8bc17eea2ba9cd8527f204f9c8d4dbcc527c9d
source-progress: 4e2ce1af2cd553cf1dd36665de0028b273b8ec3ec384d5e87a583daafd214910
source-handoff: 1f2647d5819b2a1f37222424686f93941d3b0b04ee796d1e5cdcc90bb6c52717
source-learnings: fc0be0b6b933230e3ae30e7375bedd660fc645f5ed4768d5e07c48e154d519a4
source-config: 43186947fdaf3f3b9f425f8ce1b144a8227ce1d7bec2b7aeafb32e9f0572dea8


readiness-by: session:01a1dcc3-c4c2-7282-8059-fdf1a3fd1652
readiness-at: 2026-11-15T02:37:16.170Z
readiness-checkpoint: g9-b25a63ffa794
### Last verified state
guard level 0; checkpoint requested (finalize: E2E-54/P1-m4 CLOSED: Stage C ret-runner green x2 fresh direct rc 0, 27 MEASURED checks (6ff755b2); Stage D QUALIFIED on the 8080 lane (zero-oracle cpmsim probe rc 0), dual runner 12/12->14/14 BOTH-PASS both modes, 57->67 checks, 45->53 controls ALL REJECTED; THIRD full frozen panel (after D) all 14 rc 0; close gate rc 0 (1328/1328, 190/190, 9/9, census 16/0/25/0, prose 5). RESULTS .CP/.SD/.T + PLAN dashboard CLOSED + arch 7-17 in f2bb784c. STOP binding per P1-m4.11/P1-m4.12-5: any extension needs a NEW operator brief.)

### Unfinished operations
- (none recorded)

### Next action
**NONE — STOP is binding (§P1-m4.11/§P1-m4.12-5): campaign E2E-54/P1-m4 is CLOSED; any
extension requires a NEW operator brief.** This session should finalize the checkpoint
(done via /handoff finalize) and close. If the operator opens new work in this directory,
start from their brief, not from this file.

### Guard notes
E2E-54/P1-m4 CLOSED: Stage C ret-runner green x2 fresh direct rc 0, 27 MEASURED checks (6ff755b2); Stage D QUALIFIED on the 8080 lane (zero-oracle cpmsim probe rc 0), dual runner 12/12->14/14 BOTH-PASS both modes, 57->67 checks, 45->53 controls ALL REJECTED; THIRD full frozen panel (after D) all 14 rc 0; close gate rc 0 (1328/1328, 190/190, 9/9, census 16/0/25/0, prose 5). RESULTS .CP/.SD/.T + PLAN dashboard CLOSED + arch 7-17 in f2bb784c. STOP binding per P1-m4.11/P1-m4.12-5: any extension needs a NEW operator brief.
<!-- guard:end checkpoint -->
