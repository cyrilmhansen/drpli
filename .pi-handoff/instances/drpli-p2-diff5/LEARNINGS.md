# LEARNINGS — mission drpli-p2-diff5

## Accepted (verified this session)

- **Stage D is CLOSED and the campaign is CLOSED.** D12 (DIF07) and D13 (DIF08) are measured-first
  differential cases at `f596342b`: the pins are `DIF07.mir` 1865 B `072b59ad…c43`, `DIF08.mir`
  1177 B `75051416…49e`, both `x2` fresh deterministic, `stdout == -o`, ZERO stderr, `nfuncs` 2/2
  MEASURED from mir2o stderr (2552/2352 bytes). The runner is **12/12 BOTH-PASS in BOTH modes**
  (default + strict), rc 0, **57 checks, 45/45 comparator controls all REJECTED**, no divergence,
  no infra failure. The expected vectors were the pre-registered §5.4 ones (`[3000,7000,12000]`
  and `[1500,3000,4500,6000]`), hand-derived from the algorithm, never from output.
- The Stage-D frozen panel (all 14 items) is `cmp`-identical to the Stage-C baseline except the
  two expected `mir_numeric` lines (the disclosed 45→47: the two new pins, 38 total pins). The
  close re-ran the whole panel again and it is `cmp`-identical to Stage D. `pli80c.exe` is
  `172595d5…aca281` unchanged; ledger 203/C380; `git diff --exit-code` clean in every tree.
- **D12's pin is structurally identical to the committed DIF05 pin** (modulo the names, the cap
  `20`/the multiplier `1000`, and the three `q = 3/7/12` actuals) and **D13's pin is identical to
  the DIF06 pin** (modulo the names, the cap `12`, the multiplier `1500`) — the refinement is the
  only change; the lowering is unchanged. The pin review was done line-by-line twice against the
  prior campaign's pins.

- **The Stage-C frozen panel (the §5.9 gate) is GREEN and the only movers are the two
  disclosed count lines** (`mirsumtest` 116→172, `mir_return_summary` 14→15). The full
  panel (gate, hir 220, mir_aot 32, cosmo 25, console 43, debug 23, CF 83, call 86,
  suite 29/29, functional-hostile 211, mir_numeric 45) is `cmp`-IDENTICAL to the Stage-B
  baseline; `mir_return_summary` (15) is `cmp`-identical to the stageC/tool.log; the
  `mirsumtest` LIVE is `MIR-SUM OK 172 checks` rc 0; the exe sha is unchanged.
  `functional_runner.py` (the real 26-case dashboard) is NOT a panel item and was not
  re-run.
- The refinement is ANALYSIS-ONLY: the DIF05/DIF06 `.mir` pins re-measured
  BYTE-IDENTICAL after the implementation (cmp rc 0) — the emitted-byte invariant holds.
- The campaign premise is REALIZED: DIF07 (`scaling`/`capped`, q=3/7/12, ×1000) and
  DIF08 (`batched`/`limited`, i=1..4, ×1500) — the hull products leave W(15) (Stage-A
  measured the exact pre-registered `HIR-E19` at line 7 / line 8 with the exact
  intervals), and BOTH now compile NATIVE rc 0 (the post-change .mir files are
  1865/1177 B, stderr empty).
- H2 (the admission hypothesis) is VERIFIED at the pre-change stage; the post-change
  refusals are GONE.

- The FROZEN PANEL after Stage B is GREEN apart from the four disclosed corrupt-table
  movers, and NOTHING else moved (measured this session, logs
  `build/e54p2diff5/stageB-panel/`, record in `PANEL-RECORD.md`): gate 1328/1328-190/190-9/9-
  149 rows 0/0-census 16/0/25/0-prose 5 (`cmp`-IDENTICAL to the P2-DIFF-4 close log); hir 220
  IDENTICAL; mir_aot 32, cosmo 25, console 43, debug 23, CF 83, call 86, suite 29/29, the 211
  hostile functional checks — ALL `cmp`-IDENTICAL; `mirsumtest` 116 (rc 0, the frozen count);
  `mir_numeric` 45 with all 36 committed `.mir` pins byte-equal x2 fresh; the runner **10/10
  BOTH-PASS in BOTH modes**, 47 checks, 37/37 controls REJECTED, no divergence, no infra
  failure; `pli80c.exe` `172595d5…aca281` from the fresh build; `git diff --exit-code -- ocaml/`
  and `-- hir/` rc 0; ledger 203/C380.
- The four `mir_return_summary_test` FAILs are the ONLY panel movement, and every moved line
  is a DIRECT §5.6 consequence (the corrupt modes perturb the inferred value only, so the
  `expected` column is the new value and `got` is that value ± 1): `classifier-narrow-precision`
  (amendment 17, `[1,3]`→`[1,1]`), `spec-min-above-cap`, `spec-min-across-cap`,
  `spec-min-nonpoint`, `spec-distinct-1/2/3`, `spec-full-window-min`, `spec-loop-iv`,
  `spec-boundary-min-13`, `spec-real-dif05-sum1/2/3`, `spec-real-dif06-sum`. Table LINE COUNTS
  are unmoved (29/29, 12/12); `--corrupt-unknown` and `--corrupt-spec-unknown` are
  `cmp`-IDENTICAL; the §5.6 "NOT moving" items (`spec-min-cap-point`,
  `spec-full-window-identity`, `boundary-tight`, `two-arm-hull`, `missing-else-identity`)
  are verbatim in the tables. The §5.6 ctx/subset items (8, 12, 13, 15, 16) are containment
  checks that print no got/expected line — they moved inside the driver and passed there.
- `functional_runner.py` (the real 26-case dashboard) is NOT a frozen-panel item: it runs
  rc 1 with `PASS=18 FAIL=8`, the pre-existing corpus gaps (codegen `[TBD]` subsets, the
  FX-01 emulator discard, the DHRY-00 assert line). The panel's "functional 211" is the
  hostile suite, which is `cmp`-IDENTICAL.

### Accepted (Stage C, this session)

- **The §5.8 table is green at 172 checks** (`b40d0746`). The driver is rc 0, the panel
  tool is rc 0 (15 checks), and every one of the 56 new hand-derived literals was
  confirmed by the module. The §5.8 orientation law is measured: the `Eq`-else-UNREFINED
  pair (`refine-eq-across` `[19,25]→[1,25]`, `refine-eq-else-only` `[21,21]→[21,21]`),
  the `Ne`/`Var op Var` conservative pair (`refine-ne-point` `[20,20]→[1,20]`,
  `refine-varopvar-conservative` `[1,2]`), the missing-ELSE triple (`refine-noelse-*`
  `[2,9]`/`[2,2]`/`[2,9]`), the excluded-arm-then-re-read triple
  (`[8,8]`/`[50,50]`/`[24,45]`), and the full-window no-change pair
  (`refine-fullwindow-lt` `[20,16383]`, `refine-fullwindow-eq` the whole window).
- **The H3 pivot is measured at BOTH levels.** The `p_h3` body (`if x > 20 then c = 16383
  else c = x * 1000`) is `Unknown` over the full window (the refinement never weakens the
  callee's own proof) and `Known` at the small/large points — the §5.8 hostile that the
  refinement could not be a back door. The BACKEND-side H3 (the callee still lowered over
  `W(p)`) is the untouched `mir_backend.ml` + the unchanged 190-negative panel.
- **The DIF07/DIF08 REAL fixtures specialize exactly as the §5.8 literals say** —
  `spec-real-dif07-sum1/2/3` `[3,3]/[7,7]/[12,12]`, `ctx` `[-16383,20]`, entry 12000;
  `spec-real-dif08-sum` `[1,4]` (the hull of the four trips), `ctx` `[-16383,12]`, entry
  5. The driver's own concrete walk (`exec`/`run_callee`) confirms the actuals, the trips,
  the hull and the entry values independently of the module.
- **The `--corrupt-refine-arm` control is NON-VACUOUS**: 32 FAIL lines, rc 1, ZERO stdout,
  ×2. It perturbs the inferred refined-arm value at BOTH endpoints (and forces
  `Unknown→Known (0,0)`) — a one-sided perturbation cannot see an arm EXCLUSION, because
  an excluded arm makes the summary the surviving arm's own interval.

## Proposed
 (unverified)

- The Stage-C §5.8 table (the corrupt tables will be re-pinned to the new values) and the
  H3 pivot fixture.
- The new non-vacuity control (§5.8: a control that perturbs the REFINED arm value and never
  the concrete reference or the condition).
- Stage D: the 12/12 BOTH-PASS outcome (measured, not a mandate).

## Falsified or superseded

### Falsified (Stage C, this session)

- **My own hand derivation of the `p_reread` monotone chain at the FULL window was wrong
  before the run**: I expected `[8,40]` at `[3,30]` (it is `[8,50]` — the join is
  `c ∈ [5,20]` with `x ∈ [3,30]`, not the arm's own refined `x`) and I expected a `Known`
  at the full window (it is `Unknown`: `c + x` reaches `[-16378,16403]`, outside `W(15)`).
  The chain is re-registered as `[3,3] ⊆ [3,30] ⊆ [-100,100]`. LESSON: the monotone chain
  must use the ACTUAL interval, never the arm's refined one, and the full-window
  containment is only meaningful when the body is window-safe at `W(p)`.

- The parent session's `spec-min-across-cap` reasoning ("the else arm is infeasible
  (30<=20 false) -> [20,20]") was WRONG: the actual [3,30] is a NON-POINT interval,
  both arms feasible (the then arm is [21,30], the else is [3,20]), the hull is
  [3,20]. The corrected law is PRE-REGISTERED in §5.6-5 and the MEASURED result
  matches it ([3,20]).
- The §5.6 disclosure list was INCOMPLETE (missed `classifier-narrow-precision`);
  the PRE-EXECUTION amendment (e959106c) records the correction — the same §5.2 law
  applies, no special case, no new code needed.

## Open questions

- RESOLVED: the frozen panel moved ONLY the four `--corrupt-*` tables, all disclosed
  against §5.7-3 (see Accepted). No other panel move ⇒ no STOP. The Stage-C tool update
  re-pins these tables (permitted edit §5.7-3).
