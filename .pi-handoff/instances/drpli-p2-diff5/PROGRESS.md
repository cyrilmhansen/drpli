# PROGRESS — mission drpli-p2-diff5

## Current phase

P2-DIFF-5 IS **CLOSED** (the campaign is complete; STOP, await the operator — the PLAN
§5.11 requires a NEW brief for any new phase). The last action is to commit the
HANDOFF/PROGRESS/LEARNINGS durable edits and then run `/handoff finalize`.

## Completed

- **The campaign is CLOSED at `28c7cfe3`.** The full chain: 710989ef (pre-reg) → 4d970aa6
  (Stage A) → e959106c (§5.6 amendment) → 1544f288 (the refinement) → e69aa556 (the driver)
  → b40d0746 (Stage C) → f596342b (Stage D) → 28c7cfe3 (the close: RESULTS §P2-DIFF-5, the
  PLAN §5.12 dashboard row, arch §7-16). All working trees clean.
- Stage C frozen panel: all 14 items `cmp`-IDENTICAL to the Stage-B baseline (only the two
  disclosed count lines moved: mirsumtest 116→172, mir_return_summary 14→15). `mirsumtest`
  LIVE rc 0 at 172; the panel tool rc 0 at 15; the runner 10/10 in BOTH modes (the pre-Stage-D
  count); exe sha unchanged.
- Stage D (measured-first): the two pins `DIF07.mir` (1865 B `072b59ad…`) and `DIF08.mir`
  (1177 B `75051416…`) were produced by `pli80mir --export` (x2 fresh, deterministic,
  `stdout == -o`, ZERO stderr), `nfuncs` 2/2 MEASURED from mir2o. The runner is now
  **12/12 BOTH-PASS in BOTH modes**, 57 checks, 45/45 controls REJECTED; `mir_numeric` is
  47 (the disclosed 45→47, 38 pins, 36 pre-existing UNMOVED). The close re-ran the full
  14-item panel: `cmp`-IDENTICAL to Stage D.

## Pending

- None. The campaign is CLOSED. The only remaining action is to commit the HANDOFF/PROGRESS/
  LEARNINGS durable edits and then run `/handoff finalize` (or a renewal to a fresh session).

## Next action (exact)

- STOP: the campaign is closed and committed. The ONLY remaining action is the durables
  commit and the `/handoff finalize`. No further experiment is authorized — the PLAN
  §5.11 requires a NEW operator brief for any new phase.

## Verified evidence (this session)

- The close panel (14 items) is `cmp`-identical to the Stage-D baseline; the exe sha
  `172595d5…aca281` is unchanged; the ledger is 203/C380; `git diff --exit-code --
  ocaml/ hir/ tools/ spec/ docs/` is clean before the durables commit.

## Blockers

- None. The campaign is closed and the STOP is in force. No further work is authorized
  without a NEW operator brief (PLAN §5.11).
<!-- guard:begin checkpoint -->
checkpoint-schema: 3
checkpoint-generation: 11
checkpoint-id: g11-57ad309caa64
checkpoint-kind: auto
content-delta: new
readiness: unattested
guard-level: 3
checkpointed: 2026-11-14T22:26:10.277Z
source-goal: 730790b648a1e1d14b76243cfe8bc17eea2ba9cd8527f204f9c8d4dbcc527c9d
source-progress: 92ff1913b64c1a40b2c6014d5225bd5ca5febfb7103782402e28fa9676c7aa74
source-handoff: 8941c3e86cace0931eb3314f92aded97bad787a3257916d0a8b8ef442ce11044
source-learnings: 183af22c37f329c96e9d2a369aee8ccb9db47e8243a68655f3ebc0cf31f154b7
source-config: 43186947fdaf3f3b9f425f8ce1b144a8227ce1d7bec2b7aeafb32e9f0572dea8
next-action: 1. STAGE C (PLAN §5.8) in `ocaml/hir/mirsumtest.ml` IN PLACE (§5.7-2), each expectation a
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
<!-- guard:end checkpoint -->

## STAGE C — COMPLETE (manual prose, supersedes the managed block above)

Committed `b40d0746`. The §5.8 table lives in `ocaml/hir/mirsumtest.ml` in place
(`f_refine` + the `p_reread`/`p_noelse`/`p_varopvar`/`p_nondefinite`/`p_h3` builders and
the `cmp_body`/`cmp_min`/`cmp_eq`/`cmp_ne` helpers): the `Lt`/`Le`/`Ge`/`Gt`/`Eq`/`Ne`
orientation law, the Eq-else-UNREFINED law, `Var op Var` verbatim, the missing-ELSE
refinement, the excluded arm re-read in the join, the full-window no-change law, the five
§5.8 hostiles, the empty-actual seed hostile, the monotone chains, the H3 pivot; plus the
DIF07/DIF08 REAL-fixture specialization (`f_real` ctx + envelope, `spec-real-dif07-*`,
`spec-real-dif08-*`) and the new §5.8 control `--corrupt-refine-arm` (32 FAIL lines, rc 1).
COUNT 116 → 172 (DISCLOSED); the five corrupt tables re-pinned to measured values; the
panel tool is rc 0 (15 checks). FALSIFIED: my own hand derivation of the `p_reread`
monotone chain at the full window (it is `Unknown` there — `c + x` reaches `[-16378,16403]`
outside `W(15)`); corrected before the green run.

## CAMPAIGN CLOSED (manual prose, supersedes the managed block above)

The campaign is CLOSED and committed at `28c7cfe3` (the durables are `b477de03`). The
Stage-C frozen panel and the Stage-D frozen panel are both green. Stage D: the
measured-first pins `DIF07.mir` (1865 B `072b59ad…c43`) and `DIF08.mir` (1177 B `75051416…49e`),
the `nfuncs` 2/2 MEASURED from mir2o stderr, the runner **12/12 BOTH-PASS in BOTH modes**,
57 checks, 45/45 comparator controls REJECTED; `mir_numeric` 47 (the disclosed 45→47, 38 pins,
36 pre-existing UNMOVED); `pli80c.exe` `172595d5…aca281` UNCHANGED; ledger 203/C380; ZERO
oracle; ZERO emitted bytes. STOP — any extension needs a new operator brief (PLAN §5.11).
