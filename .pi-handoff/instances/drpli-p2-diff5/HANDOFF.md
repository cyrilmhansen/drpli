# HANDOFF — mission drpli-p2-diff5 (P2-DIFF-5)

## Recovery instructions

Lean order: AGENTS.md (auto) → this file → PROGRESS.md (same dir) → the PRE-REGISTRATION
`spec/lab-evidence/e2e54/PLAN.md` §P2-DIFF-5 (the binding law: §5.2 subset, §5.6
disclosure list + the §5.6 amendment, §5.7 boundaries, §5.8–5.11) → the module
`ocaml/hir/mir_return_summary.ml` (the `refine` + `If` arm). Never bulk-read the
legacy root docs. `PROTOCOL.md` is binding before any unfamiliar procedure.

## Last verified state (2026-11-14, successor of 01a1dbbb — the campaign is CLOSED)

- Git HEAD `28c7cfe3`; tree clean in `ocaml/`, `hir/`, `tools/`, `spec/`, `docs/`.
  Commit chain: `710989ef` pre-registration → `4d970aa6` Stage A → `e959106c` the
  §5.6 amendment → `1544f288` the refinement → `e69aa556` the driver → `b40d0746` the
  Stage-C table → `f596342b` the Stage-D pins → `28c7cfe3` the close (RESULTS/PLAN/arch).
- The full frozen panel (all 14 items) is rc 0 and `cmp`-identical to the P2-DIFF-4 baseline.
  The disclosed tool counts: `mirsumtest` 116 → 172; `mir_return_summary` 14 → 15; `mir_numeric`
  45 → 47. The runner is **12/12 BOTH-PASS in BOTH modes**, 57 checks, 45/45 controls REJECTED;
  `pli80c.exe` `172595d5…aca281` UNCHANGED; ledger 203/C380.
- THE ONLY PANEL MOVEMENT is the FOUR `--corrupt-*` stderr tables in
  `tools/mir_return_summary_test.py` (so that tool is rc 1, 4 FAILs) — every moved line is a
  DIRECT §5.6 / §5.6-amendment-17 consequence (§5.7-3 permits the edit); line counts unmoved;
  `--corrupt-unknown` and `--corrupt-spec-unknown` `cmp`-IDENTICAL. NO STOP CONDITION FIRED.
  Evidence: `build/e54p2diff5/stageB-panel/` + `PANEL-RECORD.md` there (git-ignored scratch).
- The parent session's renewal-gate anomaly is CLEARED (this successor started normally).

## Next action (exact)

1. STAGE C (PLAN §5.8) in `ocaml/hir/mirsumtest.ml` IN PLACE (§5.7-2), each expectation a
   HAND-derived literal BEFORE the run: the `Lt`/`Le`/`Ge`/`Eq` orientation law on the `min`
   body; the Eq-else-UNREFINED law; `Ne` and `Var op Var` keep the conservative hull VERBATIM;
   the missing-ELSE refinement (then refined, false path the identity env); an EXCLUDED arm
   with the variable re-read after the join; the full-window no-change law (§5.6-7
   `[-16383,20]`); the hostiles (non-definite `Var`, non-`decimal_int` `Const` e.g. `"007"`,
   `Const` LEFT operand, composite condition) each yielding the SAME result as the
   conservative path; the H3 pivot; and the DIF07/DIF08 REAL-fixture specialization vs the
   concrete reference (DIF07 `[3,3]→[3,3]`, `[7,7]→[7,7]`, `[12,12]→[12,12]`, ctx
   `[-16383,20]`; DIF08 `[1,4]→[1,4]`, ctx `[-16383,12]`). The COUNT moves 116 → NEW
   (DISCLOSED); the tool's `LIVE_OK` literal follows.
2. Re-pin the FOUR corrupt tables in `tools/mir_return_summary_test.py` to the MEASURED new
   values (§5.7-3) and add at least ONE new non-vacuity control perturbing the REFINED arm
   value and never the concrete reference or the condition; the tool's count (14 → NEW) is
   disclosed. Then both the driver and the tool must be rc 0.
3. Re-run the frozen panel (the Stage-C gate), then STAGE D: DIF07/DIF08 as D12/D13
   (measured-first pins, measured `nfuncs`), both lanes ×2, both modes; target 12/12 BOTH-PASS
   (measured).
4. The close: RESULTS §P2-DIFF-5, the dashboard row, arch §7-16, the durables.

## Unfinished operations

- None. The campaign is CLOSED and the operator STOP is in force.

## Discoveries not yet incorporated

See PROGRESS.md and the instance LEARNINGS.md (the §5.6 amendment is already incorporated in
the PLAN). New this session: the panel's only movers are the four corrupt tables (LEARNINGS
"Accepted"); the §5.6 ctx/subset items 8/12/13/15/16 print no corrupt lines — they moved
inside the driver and passed there.

## Key facts (binding)

- NEVER touch `mir_backend.ml` (the analysis is the module only); no new
  `ocaml/hir/*.ml` (the 15-file X3/F8 check); no emitted-byte change; no oracle;
  no pin/golden/negative change; no ledger change; `handoff.config.json` never staged.
- STOP: any refusal other than the predicted §5.5; any summary WIDER than the
  branch-insensitive result; any Known→Unknown at the same seed; any unexplained
  panel move; any soundness doubt.

## Campaign design (the binding law)

The §P2-DIFF-5.2 subset: `Var op Const` (Lt/Le/Gt/Ge; Eq refines only the THEN
side; Ne refines nothing; `Var op Var`/`Const op Var`/non-relational = conservative
join verbatim); clip the arm env's entry to the subset; empty subset → the arm is
PROVABLY INFEASIBLE → EXCLUDED from the join (the one-arm join is that arm);
missing ELSE = the identity env (the old law).
<!-- guard:begin checkpoint -->
checkpoint-schema: 3
checkpoint-generation: 11
checkpoint-id: g11-57ad309caa64
checkpoint-kind: auto
content-delta: new
readiness: unattested
status: checkpoint (guard level 3, remaining ~6884, session mission:drpli-p2-diff5:01a1dbed-74b8-72bd-a54d-4a5bdbef7e64)
checkpointed: 2026-11-14T22:26:10.277Z
source-goal: 730790b648a1e1d14b76243cfe8bc17eea2ba9cd8527f204f9c8d4dbcc527c9d
source-progress: 92ff1913b64c1a40b2c6014d5225bd5ca5febfb7103782402e28fa9676c7aa74
source-handoff: 8941c3e86cace0931eb3314f92aded97bad787a3257916d0a8b8ef442ce11044
source-learnings: 183af22c37f329c96e9d2a369aee8ccb9db47e8243a68655f3ebc0cf31f154b7
source-config: 43186947fdaf3f3b9f425f8ce1b144a8227ce1d7bec2b7aeafb32e9f0572dea8


### Last verified state
guard level 3; checkpoint requested (auto at level 3)

### Unfinished operations
- (none recorded)

### Next action
1. STAGE C (PLAN §5.8) in `ocaml/hir/mirsumtest.ml` IN PLACE (§5.7-2), each expectation a
   HAND-derived literal BEFORE the run: the `Lt`/`Le`/`Ge`/`Eq` orientation law on the `min`
   body; the Eq-else-UNREFINED law; `Ne` and `Var op Var` keep the conservative hull VERBATIM;
   the missing-ELSE refinement (then refined, false path the identity env); an EXCLUDED arm
   with the variable re-read after the join; the full-window no-change law (§5.6-7
   `[-16383,20]`); the hostiles (non-definite `Var`, non-`decimal_int` `Const` e.g. `"007"`,
   `Const` LEFT operand, composite condition) each yielding the SAME result as the
   conservative path; the H3 pivot; and the DIF07/DIF08 REAL-fixture specialization vs the
   concrete reference (DIF07 `[3,3]→[3,3]`, `[7,7]→[7,7]`, `[12,12]→[12,12]`, ctx
   `[-16383,20]`; DIF08 `[1,4]→[1,4]`, ctx `[-16383,12]`). The COUNT moves 116 → NEW
   (DISCLOSED); the tool's `LIVE_OK` literal follows.
2. Re-pin the FOUR corrupt tables in `tools/mir_return_summary_test.py` to the MEASURED new
   values (§5.7-3) and add at least ONE new non-vacuity control perturbing the REFINED arm
   value and never the concrete reference or the condition; the tool's count (14 → NEW) is
   disclosed. Then both the driver and the tool must be rc 0.
3. Re-run the frozen panel (the Stage-C gate), then STAGE D: DIF07/DIF08 as D12/D13
   (measured-first pins, measured `nfuncs`), both lanes ×2, both modes; target 12/12 BOTH-PASS
   (measured).
4. The close: RESULTS §P2-DIFF-5, the dashboard row, arch §7-16, the durables.

### Guard notes
Stage C complete and committed (HEAD b40d0746): mirsumtest rc 0 at 172 checks, panel tool rc 0 (15 checks), five corrupt tables re-pinned to measured values, new --corrupt-refine-arm control. Next: the Stage-C frozen panel re-run (cmp vs build/e54p2diff5/stageB-panel/), then Stage D (DIF07/DIF08 as D12/D13, measured-first pins, both lanes x2, both modes), then the close. Read the SUPERSEDING manual "NEXT ACTION" section at the end of HANDOFF.md.
<!-- guard:end checkpoint -->

## NEXT ACTION — SUPERSEDES the managed block above (manual prose, 2026-11-14, successor of 01a1dbbb)

STAGE C IS COMPLETE AND COMMITTED at `b40d0746` (chain: 710989ef → 4d970aa6 → e959106c →
1544f288 → e69aa556 → b40d0746). Measured: `mirsumtest` LIVE rc 0 at the NEW count
**172 checks** (116 → 172, DISCLOSED); `tools/mir_return_summary_test.py` rc 0, **15 checks**,
the five corrupt tables re-pinned to MEASURED values (widen 12 / narrow 12 / unknown 34 /
spec-widen 36 / spec-narrow 36 / spec-unknown 14 / NEW `--corrupt-refine-arm` 32).
`git diff --exit-code -- hir/ spec/` rc 0. Logs: `build/e54p2diff5/stageC/`.

1. RE-RUN THE FROZEN PANEL (the Stage-C gate, §5.9), `cmp` each log against
   `build/e54p2diff5/stageB-panel/`: `cd ocaml && eval "$(opam env)" && dune build`;
   then each as its own command, DIRECT rc: `tools/e2e_gate.py` (1328/1328-190/190-9/9-149
   rows 0/0-census 16/0/25/0-prose 5), `hir_test.py` (220), `mir_aot_test.py` (32), cosmo
   (25), console (43), debug (23), CF (83), call (86), `test_dual_backend.py` (29/29),
   `test_functional_runner.py` (211), `mir_numeric_test.py` (45, 36 pins ×2), the runner in
   BOTH modes (10/10 BOTH-PASS, 47 checks, 37/37 controls), `sha256sum
   ocaml/_build/default/bin/pli80c.exe` = `172595d5…aca281`, ledger 203/C380. Any move
   outside the two already-measured count lines ⇒ STOP and attribute.
2. STAGE D: DIF07/DIF08 as **D12/D13** in `tools/dual_backend_test.py` (measured-first
   pins into `hir/dif-expected/`, measured `nfuncs`, §5.4 vectors `[3000,7000,12000]` /
   `[1500,3000,4500,6000]`), `mir_numeric_test.py` `EXPORTS` +2 names (45 → 47, disclosed),
   both lanes ×2, both modes; target 12/12 BOTH-PASS (measured).
3. The close: RESULTS §P2-DIFF-5, the dashboard row, `docs/architecture/backend-boundary.md`
   `## 7-16` (additive), the durables.

## P2-DIFF-5 IS CLOSED — STOP, await the operator (manual prose, 2026-11-14, successor of 01a1dbbb)

The full campaign is **CLOSED** and committed at `28c7cfe3` (chain: 710989ef → 4d970aa6 →
e959106c → 1544f288 → e69aa556 → b40d0746 → f596342b → 28c7cfe3). Working tree clean
(`ocaml/`/`hir/`/`tools/`/`spec/`/`docs/` all `git diff --exit-code` rc 0).

**Measured (the close panel, 14 items, rc 0):** gate 1328/1328-190/190-9/9-149 rows 0/0-census
16/0/25/0-prose 5 (cmp-identical); hir 220; mir_aot 32; cosmo 25; console 43; debug 23; CF 83;
call 86; suite 29/29; functional-hostile 211 (only the /tmp dir); mir_numeric **47** (36
pre-existing pins byte-equal, 38 total); mir_return_summary **15**; mirsumtest LIVE
**172 checks**; the runner **12/12 BOTH-PASS** in BOTH modes, 57 checks, 45/45 controls REJECTED;
`pli80c.exe` `172595d5…aca281` UNCHANGED; ledger 203/C380.

**The campaign premise (H2) is realized.** DIF07/DIF08 (the `×1000`/`×1500` hulls leaving
`W(15)`) are now admitted and are the differential cases D12/D13 (the corpus 8 → 12 → 12... 12
programs). H1 (never wider) and H3 (callee obligation) are measured; NO STOP fired at any
stage; ZERO emitted bytes; ZERO oracle; the ledger is untouched.

**STOP.** Any extension of the return-summary analysis needs a NEW operator brief (PLAN
§5.11). No further action is authorized. If the operator returns, the next thing is a
/handoff finalize (and, if desired, a renewal to a fresh session), NOT a new experiment.

