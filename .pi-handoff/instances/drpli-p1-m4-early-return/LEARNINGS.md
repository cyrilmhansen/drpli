# LEARNINGS — mission drpli-p1-m4-early-return

## Accepted (measured this mission)

- Census 4-tuple counts only the 41 AUTHENTIC programs (16+0+25+0); DR_REJECTED/NO_ORACLE (3)
  is a separate field and can NEVER appear in it. "16/0/25/3" ⇒ reporting artifact.
- MIR immediates are BARE decimals (`mov t, 9`); the `i64:k` form is a MEMORY operand —
  `mov x, i64:7` compiles to a dereference of address 7 and SEGFAULTS at exec while mir2o
  still accepts the text. (probe1–4 falsified, probe5/6 accepted, build/e54p1m4/probe/.)
- mir2o ACCEPTS labels/instructions after an unconditional `ret` and both paths execute per
  the jump/fall semantics (probe5/probe6 exec ×2 each).
- No committed pin quotes the no_return_in nested-RETURN message: amending it moves zero pins.
- mir_return_summary.ml treats ANY non-final Return (incl. If-arm returns) as Unknown by
  construction (its subset law, ~lines 21/201) — the §P1-m4.8 boundary holds structurally
  (exec-level confirmation still owed).
- The §P1-m4.3 classifier + terminating-arm join exclusion WORKS as measured: ER01/ER02 lower
  rc 0 deterministically (1223/978 B, sha `debdef29…`/`64d2bcbb…`), mir2o accepts the post-`ret`
  `Ljoin1:` shape (2 funcs each), and BOTH hand-derived vectors execute on BOTH native lanes
  (glibc + cosmo tiny): [4,9,4] and [3,12], rc 0, ×2 fresh processes identical
  (`build/e54p1m4/stageB/`).
- Refusal-message wording after the change: only ERN1/ERN4/ERN8 keep the VERBATIM nested E18;
  ERN5/ERN6 refuse with NEW §P1-m4.3 wording (VOID / not-final-arm-statement), and ERN2/ERN3
  refuse EARLIER with the pre-existing body-must-end law. §P1-m4.6's "verbatim pre-change
  message" expectation was therefore too narrow — the negatives refuse BY NAME, not necessarily
  with the same sentence.
- Two EARLIER E19 laws dominate the §P1-m4.6 "window" expectation for out-of-range early
  returns: a literal wider than the result precision refuses as `conversion FIXED BINARY(15,0)
  -> FIXED BINARY(3,0)` (ERN7; the same sentence as CFN2/CFN6/N3 pins), and a binop
  (`RETURN(x+x)` in `FIXED BIN(15)`) refuses as the binop-overflow brief-§4 law — both BEFORE
  the §P1-m0.3-3 return-window check is reached. (probe: `build/e54p1m4/stageB/probe/`)

## Verified additions this hop (accepted — measured 2026-11-15, successor session)

- STEP 4+5 DONE: commit 26994b9a (mir_backend.ml + 18 pins + RESULTS §P1-m4.SB), commit 669835ba
  (RESULTS §P1-m4.SP frozen panel). All 18 pins RE-VERIFIED first-hand and REPRODUCED byte-for-byte
  by a SECOND fresh scratch build (_build-e54p1m4b, build2.log) — committed source == pin source.
- ARMING DECIDED (Open question 1 CLOSED): option (a). `ocaml/_build/default` rebuilt from committed
  HEAD after `git diff --exit-code -- ocaml/ hir/ tools/` rc 0. pli80c.exe sha 172595d5...aca281
  VERIFIED UNCHANGED (pli80c's dune libraries = pli80 only — it never links the hir library);
  pli80mir.exe MOVED 0dab512e...->2d19e871... (the required mover); pli80hir/semtest/mirsumtest/
  mirnumtest exes byte-UNCHANGED (linker closure reaches Mir_backend only from pli80mir). The panel
  judged the exe built from committed 26994b9a. Rationale in RESULTS §P1-m4.SP.
- H3 CONFIRMED: all 14 panel items rc 0; 11 logs cmp-IDENTICAL to the P2-DIFF-5 close baseline
  (gate 1328/1328+census 16/0/25/0, hir 220, aot 32, cosmo 25, console 43, debug 23, CF 83, call 86,
  suite 29/29, mir_numeric 47, mir_return_summary 15 + mirsumtest 172, runner logs); functional 211
  and dual_backend 12/12 BOTH-PASS 57 checks 45/45 controls differ ONLY in stamp/HEAD/tmp lines.
- §P1-m4.8 MEASURED (candidates + discriminating probe): ERNSUM.pli (caller does `a=sel(2);
  b=sel(7); r=a*b;`) REFUSES with operands proved within [4,4] and [-16383,16383] — refinement at
  x=2 comes ONLY from the pre-existing P2-DIFF-5 infeasible-arm law; the feasible-early-return leg
  x=7 stays full-window (no invention from the early ret). Non-vacuity control ERNSUMC.pli (no
  early RETURN, provable join) ADMITS rc 0 (645 B). Evidence build/e54p1m4/stageB/probe/.
- PL/I THEN takes ONE statement: `if ... then y=9; return(y);` parses the return OUTSIDE the arm.
  Two-statement arms need `then do; ... end;` (the committed ERN4 idiom). Cost me one false probe:
  the first ERCTL "mutant discrimination" was actually the old no-RETURN two-arm join path.
- join_env semantics: Some/Some -> iv_hull; a binding present on ONE side only is DROPPED. Hence a
  join-leak mutant is visible only when a BOTH-armed variable's hull breaks a downstream proof: the
  final C-M4a probe ERCTL (`y=127` before, `y=129; return(y)` in a do-arm, `return (y*y)` after) is
  ADMITTED by the committed backend (127*127=16129 <= W(15)) and REFUSED by the env-flow mutant
  (hull [127,129] reaches 16641 > W(15), E19 line 9, no artifact). Measured by hand.
- C-M4b MEASURED: deleting `no_return_in body;` at the While site makes mutant ERN1 refuse with the
  §P1-m4.3-4 classifier message at line 5 — NOT the pinned nested-E18 bytes. Control detection =
  pinned-bytes mismatch inside the suite. DEVIATION from §P1-m4.9's "stop refusing" wording: the
  classifier is a SECOND guard; record honestly, keep the control.
- Disposable mutant backends build via `git archive HEAD ocaml | tar -x -C <dir>` + string-replace
  (assert count 1) + `dune build` in the copy — rc 0 in ~2s here (dune shared cache). The runner
  REFUSES a stale mutant dir: clear build/e54p1m4/ret-runner/c-m4a|c-m4b before each run.

## Verified additions this hop (accepted — measured 2026-11-15, Stage C + D + close session)

- STAGE C DONE: `tools/mir_aot_ret_test.py` ran GREEN — MEASURED **27 checks**, two fresh runs
  with DIRECT rc 0 (run2/run3; run1 logged PASSED but its rc was not captured — honesty note in
  §P1-m4.SC), logs byte-identical; pins regenerated ×2 fresh == committed Stage-B pins (the
  runner never writes a pin); both §P1-m4.4 vectors EXECUTE on glibc + cosmo tiny with
  fresh-process determinism; C-M4a/C-M4b FAILED LOUDLY inside on disposable mutants. Commit
  `6ff755b2` (tool + RESULTS §P1-m4.SC). The stale dry-run mutants were under build/e54p1m4/
  controls/ (NOT ret-runner/ — that dir did not exist at session start); historical evidence kept.
- STAGE D QUALIFIED (open question 2 CLOSED): the 8080-lane EXECUTION of [4,9,4]/[3,12] IS in
  reach without the oracle — probe `build/e54p1m4/stageD/qualify.py` rc 0 imports the dual
  runner machinery read-only (pli80c -> LINK-80+PLILIB -> cpmsim, fresh workspace, x2). Both
  vectors reproduce byte-exactly, normalized AND raw deterministic. D14/D15 added to
  `tools/dual_backend_test.py` (CASES + docstring only): runner **14/14 BOTH-PASS** in BOTH
  modes, MEASURED 57->67 checks, 45->53 controls ALL REJECTED, both runs direct rc 0.
- THREE full frozen panels GREEN: after B (§P1-m4.SP), after C (§P1-m4.CP: 11/12 non-runner
  cmp-IDENTICAL, functional/runner differ ONLY in stamp/HEAD/tmp lines; exes stable), after D
  (§P1-m4.SD: same, runner items + the disclosed 14/14 movers). H3 CONFIRMED at all three.
- §P1-m4.10-2 vs §P1-m4.12-4 tension ADJUDICATED: the specific pre-registered, H3-pre-disclosed
  Stage-D clause authorizes the dual_backend_test.py amendment; recorded in §P1-m4.T deviation 8,
  not fitted. `git diff --exit-code -- ocaml/ hir/ spec/` stayed rc 0 at every boundary.
- CLOSE: RESULTS §P1-m4.T verdict panel (H1/H2/H3 CONFIRMED; 9-item deviations ledger; NO STOP);
  PLAN §P1-m4.13 CLOSED; arch **## 7-17** bakes the three laws (post-`ret` acceptance is REAL
  jump-reachable code; bare-decimal immediates / `i64:k` = MEMORY operand; the §P1-m4.3
  classifier is a SECOND guard over loop-nested RETURN — C-M4b). Close gate rc 0: 1328/1328,
  190/190, 9/9, census 16/0/25/0, prose 5 clean. Commit `f2bb784c`. **CAMPAIGN CLOSED; STOP
  binding — any extension needs a NEW operator brief.**

## Proposed (unverified)

- (Nothing open.) The former entries are now MEASURED: the frozen panel H3 (three panels GREEN,
  see Accepted this hop), the pins committed at 26994b9a and re-verified ×2 fresh by the Stage-C
  runner (27 checks), ERN7 adjudicated as a RECORDED deviation (§P1-m4.SB/§P1-m4.T).

## Falsified or superseded

- Stage-0 "census 16/0/25/3" (superseded, see Accepted).
- First probe suite (probe1–4 segfault) — probe-form, not a mir2o defect (see Accepted).
- §P1-m4.6 AS PRE-REGISTERED ("each negative refuses with the VERBATIM PRE-CHANGE MESSAGE; ERN7
  → E19 §P1-m0.3-3 window law") is FALSIFIED by measurement: only ERN1/ERN4/ERN8 keep the
  verbatim nested-E18 sentence; ERN2/ERN3 refuse EARLIER (pre-existing body-must-end law);
  ERN5/ERN6 refuse with the NEW §P1-m4.3 wording; ERN7 refuses with the E19 **conversion** law,
  never the return-window law. Every negative still refuses BY NAME, rc 2, ZERO stdout, NO
  artifact, deterministic ×2 — the H2 substance holds, the §P1-m4.6 wording column does not.
  Record as a deviation; do NOT refit any fixture.
- The ERN9-probe question stays OPEN: is the §P1-m0.3-3 return-window check reachable AT ALL for
  an early RETURN? No shape constructed yet reaches it; claim neither way.
- §P1-m4.6 "verbatim pre-change message" + the ERN7 window-law expectation (see Falsified).

## Open questions for the successor

1. Is the §P1-m0.3-3 return-window check reachable for an early RETURN at all? (still open;
   ERN9-probe question — no shape constructed yet reaches it; claim neither way.)
2. CLOSED (Stage D hop): ER01/ER02 dual-lane-qualified on the 8080 lane (x2 fresh cpmsim runs,
   ZERO oracle); D14/D15 added; the runner is now 14/14 BOTH-PASS in BOTH modes.
3. CLOSED (Stage C hop): tools/mir_aot_ret_test.py RUN — green ×2 fresh direct rc 0, MEASURED
   27 checks, controls failing loudly inside.
