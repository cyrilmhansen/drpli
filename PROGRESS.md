# PROGRESS.md — DRPLi

Manual prose wins over the managed block below it. Do not hand-edit the managed block.
This file tracks *working state*; compiler behaviour itself belongs to `spec/CLAIMS.md`.

## Current phase — **E2E-53 CAMPAIGN OPEN** (2026-11-08; operator brief: autonomous
multi-subround COVERAGE EXPANSION; baseline 1,312 specimens / 16 corpus EXACT; whole-file
byte parity non-negotiable; Goal A (corpus) and Goal B (coverage) reported separately; no
push; renewal chain fresh 0/12). Campaign plan + opportunity matrix: `spec/lab-evidence/e2e53/PLAN.md`.
E2E-52/P3 (LOAN2) is COMPLETE and CLOSED at [C377]; its phase prose is kept below as written.

### Historical phase heading (kept as written) — E2E-52/P3 IN FLIGHT (2026-11-04; operator brief: LOAN2 progressive
closure — compile `artefacts/LOAN2.PLI` toward whole-file byte-exactness by repeated
blocker→evidence→fix cycles; multi-subround campaign; renewals autonomous at safe
boundaries; no push; preserve operator `handoff.config.json` (dirty, never staged)).

**Baseline VERIFIED this session:** HEAD `6c44d8d` (P2 close + guard finalize g276,
attested); tree clean except the operator config edit; `dune build` rc=0, compiler
`85bf7a26…` (same binary as the P2 registration gate); `artefacts/LOAN2.PLI` sha
`7be23ba3…` (unchanged, last touched Phase 0); golden `golden/first/LOAN2/LOAN2.REL`
sha `712cfcb2…` untouched; ledger ends C358; 181 claims.

**Subround P3-1 (PUT FILE bare PAGE) — evidence complete, implementation OWED.** LOAN2
blocker reproduced VERBATIM: `codegen: PUT FILE with a bare PAGE control item [TBD] (line
99)`. **KEY FACT: the raise comes from the E2E-52/P1 lexical PRESCAN (`prescan_stmt`
calls `match_put_list_lit` → `bare_ctl_put` for EVERY Sput BEFORE lowering), not from
`lower_stmt`** — which is why LOAN2's PRINT/PAGESIZE OPENs at lines 54/56 (rejected by
`open_mode_word`, `open_subset_keys` = FILE/INPUT/STREAM/OUTPUT/TITLE) do NOT surface:
the prescan dies at 99 first. After PAGE lands, LOAN2's blocker will move — the next
verified blocker is expected to be the PRINT/PAGESIZE opens at 54/56 unless an earlier
prescan refusal intervenes. Evidence: DR golden `golden/e42p2c/E46N10/E46N10.REL`
(384 B, CODE 0x3E=62, DATA 0x0A=10) pins the statement at 0023-0034 = `LXI H,*C(common
0) / LXI D,0652 / LXI B,*CODE(0035) / CALL ?SIOOP / CALL ?PAGOP / CALL ?QIOOP` with
LINK-CHAIN-EXT ?SIOOP@002D, ?PAGOP@0030, ?QIOOP@0033; continuation word 0x35 = CLOSE.
COPYLPT:53 (`put file(printfile) page;` inside an ON ENDFILE unit) carries the SAME 18
bytes behind a PRINT open (0215-00226 per probe record, predict_p2c self-test
`COPYLPT:53 = 18`). PAGE **with a count** and PAGE+items are UNMEASURED (manual
syntax permits, no object) — they must keep refusing BY NAME; LINE stays dr-refuses
(E46N21, marker `control item LINE with a count, unmeasured on the named-file route
[TBD] (line 12)` must survive any message edit); console `put page;` stays refused
(N3_PAGE negative, my-gap, marker `PUT form`). ?PAGOP appears in NO claim id —
`grep -in pagop spec/CLAIMS.md` is EMPTY; the 18-byte law lives in
e2e42-p2c/RESULTS §4 + COVERAGE row `FILE.PUT_PAGE` (line 60, currently REFUSED/NONE).
Registration plan follows the E46K1/E46K3 RETIRE precedent: move `E46N10` from REJECTS
(`tools/e2e_gate.py:4477`, marker `bare PAGE control item [TBD] (line 11)`) + delete its
NEG_META (4054) into SPECIMENS (e42p2c block ~line 1280), `--update-inventory`
1196→1197, gate AGAIN, census re-snapshot via `corpus_census.py --check` (COPYLPT and
LOAN2 census msgs WILL move), COVERAGE `FILE.PUT_PAGE` → SUPPORTED + EXACT:1, new claim
C359 derived ONLY from the existing measured evidence.

## Next action (E2E-54/P2-DIFF-3 — **PRE-REGISTRATION COMMITTED `92d1887b`; STAGE A IS NEXT: write the two DIF03/DIF04 sources, commit them + SHAs BEFORE any compilation**) — session 01a1d8e9, 2026-11-14

**The §P2-DIFF-3 campaign is OPEN.** Recovery: HEAD `92d1887b` (pre-registration of
`spec/lab-evidence/e2e54/PLAN.md` §P2-DIFF-3 — the binding contract: subset, soundness,
DIF03/DIF04 designs + independent expectations, timing law, architecture boundary, falsifiers,
STOP conditions). Baseline re-verified FIRST-HAND against the committed record (no new runs):
HEAD `4e857e09` = the P2-DIFF-2 close; tree clean except the operator `handoff.config.json` +
pre-existing untracked scratch (S2–S5, golden dirs, `_build-*` — preserved, never staged).

**NEXT VERBATIM (Stage A, per brief §4 + PLAN §P2-DIFF-3):**
(1) Read the exact source-syntax constraints ONE more time from the DIF01/DIF02 fixtures
(CRLF + one `^Z`; `n + 0` value-actual idiom; subsidiary needs its own `dcl`s; PUT inside the
loop; no literal+literal ADD on the historical lane) and `hir/dif-fixtures/DIF01.pli` as the
style template. (2) Author `hir/dif-fixtures/DIF03.pli` (entry `pricing`, classifier
`classify(x)` via nested if/else, `cat = classify(n + 0); cost = cat * 1200; put list(cost)`
for n = 2, 20, 200; expected `[1200,2400,3600]`) and `DIF04.pli` (entry `production`, counted
`do while` i=1; i<6; i=i+1; `stepclass(s)` ≤3/≤4/else; `cl = stepclass(i + 0); w = cl * 350;
put list(w)` inside the loop; expected `[350,350,350,700,1050]`). (3) Verify encoding,
`sha256sum`, and COMMIT THE SOURCES + THE REFERENCE SPECS FIRST (explicit paths, PLAN
§P2-DIFF-3.4). (4) ONLY THEN the baseline refusal on the OLD backend: `pli80c -d` (expect
rc 0) and `pli80mir --export` (expect the HIR-E19 `binop '*'` witness) — the exact diagnostic
and attribution recorded; if the refusal is NOT the full-window one, STOP and attribute.
(5) Stage B: `ocaml/hir/mir_return_summary.ml` (pure, `Hir`+`Mir_numeric` only, returns
`Known`/`Unknown`); `mir_backend.ml` one analysis call after the `folded_of`/`-g` scans and
before the lowering loop; `lower_call_e` uses the summary iff `Known` ∧ `in_window`.
(6) Stage C: `mirsumtest.ml` + `tools/mir_return_summary_test.py` (NEVER hir_test.py — the
frozen 220); the F8 file-count line `13→14` is the ONLY disclosed panel exception. (7) Stage D:
D08/D09 in the runner; the full frozen panel; the close.

**Measured facts (accepted, this session):** the refusal mechanism is exactly `lower_call_e`
returning `(rr, window cq)` (mir_backend.ml:813); the summary must NOT change any emission
instruction (the `.mir` output is unaffected — only the caller's interval); CALLN9
(`f(...) + 5`) refuses by SHAPE inside `lower`, never by window — unaffected by the summary;
the profile `dr-pli80-v1.4` is default/max precision 15; W(15) = ±16383 (NOT 32767);
the backend's `lower`/`join_env`/`env0` (formals seeded with the full window) and the
`declare`/`Find`-per-procedure law are the exact semantics the analysis must mirror; the
`Mir_numeric` algebra (iv_add/iv_sub/iv_mul/iv_neg/iv_hull/decimal_int/window) is the ONLY
interval implementation (no second copy).

**Unresolved / proposed (not yet measured):** the historical `pli80c` acceptance of the two
new programs (predicted, NOT yet run); the exact HIR node shapes the classifier produces
(`Convert` may appear at the `cat = classify(...)` assignment — the mirror must tolerate it);
the concrete reference-evaluator domain (proposed full `[-16383,16383]`).

**Open question for the successor:** whether the two DIF programs need the entry-level
`dcl`s per the P2-DIFF-2 subset law (the subsidiary needs its OWN `dcl`s; the entry cannot
share them).

Standing: ZERO oracle; `handoff.config.json` NEVER staged; no push; explicit paths; rc DIRECT;
`eval "$(opam env)"` for builds; `LC_ALL=C`; never batch build+tests; scratch `build/*` never
committed; disposable copies deleted in-command; NEVER hand-edit a managed block; this session
CANNOT use `handoff_renew` (fresh startup 0/12 — the gate permits it at safe boundaries).

SUPERSEDED-BY-ABOVE: ## Next action (E2E-54/P2-DIFF-2 — **THE CAMPAIGN IS COMPLETE: Stages A, B and C ARE CLOSED AND COMMITTED; THE ONLY ACT LEFT IS THE MANAGED-BLOCK REFRESH + FINALIZE, THEN STOP**) — CHECKPOINT 2026-11-13 late

