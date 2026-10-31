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
   - `spec/CLAIMS.md`: read ONLY cited claim ids — `grep -n '^## C326' spec/CLAIMS.md` etc.;
     the newest E2E-48 block starts at `grep -n '^## C309'` (~line 7170). The ledger CURRENTLY
     ENDS at **C326**: ids C327+ are OWED by the next action's step 6 — their absence is the
     recorded state, not corruption.
   - `spec/COVERAGE.tsv`: header + `grep` the row KEY being edited (15 columns; schema
     `spec/COVERAGE-SCHEMA.md`; validator rules at `tools/coverage_check.py:203-247`).
   - `spec/INVENTORY.txt`: `grep` the specimen/refusal name only. `spec/RUNTIME.txt` and
     `spec/DIVERGENT.txt`: only rows named by the task.
   - Current round evidence: `spec/lab-evidence/e2e48-p2e/{RESULTS.md,HYPOTHESES.md,BASELINE-MINE.txt}`.
5. Do **not** run the compiler, the oracle, LINK-80, cpmsim, Rune CI or `tools/e2e_gate.py`
   unless the session's actual task is compiler development or gate verification.

## Last verified state — E2E-48/P2e lowering (verified at `e49902a`, 2026-10-31)

- Arms 1 + 2 + 3 of the six RESULTS §2 arms are DONE, committed and measured (`d18c6ab`,
  `bab0d16`, `e49902a`): E48E1..E48E5 whole-file byte-identical; E46K14's pinned refusal
  RE-MEASURED through the binary with gate CRLF+`^Z` semantics — marker unchanged, NOT
  re-pinned (re-run at `e49902a`: 181/181, 0 anomalies, marker unmoved); its `imem_refuse`
  WHY-string cites `golden/e48p2e/E48E6/E48E6.PRN` as a MEASURED dr-refuses (append,
  original verbatim); the NEG_META *category* re-classification (unmeasured -> dr-refuses)
  is still step-6 work. Arm 3 (`e49902a`, RESULTS §2.3): `bit_cond_mat`'s `Eq` fallback
  admits `Ast.Ebit "0"` on a `Vbit1` left — `3A *D(b) / E6 80 / D6 01 / 9F` + the caller's
  `STA` = 11 bytes (E48E5 0006..0010, the `'1'b` head WITHOUT the `D6 80` step); no pool
  cell demanded, prescan untouched; E48E6 KEEPS refusing through the new binary (no
  `.REL`). **Arms 4, 5 are NOT STARTED; step 6 (claims/registration/gate/COVERAGE) is
  OWED.** No `ocaml/` edit is half-done.
- Laws and refusals: `spec/lab-evidence/e2e48-p2e/RESULTS.md` §2 (six laws) and §3 (what
  stays unmeasured) are the authority; claims are owed as C327+ (next action step 6).
- E48E6 (`if line then`, CHARACTER VARYING member as bare condition) is **dr-refuses**
  (`BIT REQ`, no `.REL`); it is NOT a specimen and gets no `.REL`-based row.
- Regression baselines in force: e48p1 24/24, e48p2c 9/9, e48p2db 10/10, e48p2retire 2/2;
  FULL GATE baseline 1120 byte-exact / 0 fail (`adbfa2a`), negative 181/181, divergence 9/9,
  coverage 113 rows 0 errors (`218b474`), census 15/0/26/0; clean-rebuild warning multiset 126.
  EVERY one re-measured at `e49902a` (arm 3) with identical ACTUALS (rc=0).

## Next action — E2E-48/P2e: LOWER arms 4, 5 (NOT STARTED), then step 6 (claims + registration + FULL GATE)

> Arm numbering keeps the round's ids: arms 1–2 landed at `d18c6ab`/`bab0d16` (specs archived
> in `docs/history/2026-10-30-next-actions.md`) and arm 3 at `e49902a` (spec + measured closure
> archived in `docs/history/2026-10-31-p2e-arm3-closed.md`); references to a landed arm mean
> completed, measured work. **ONE arm per commit**, `cd ocaml && eval $(opam env) && dune build`
> + the cmp sweep after EACH (LEARNINGS rule: one arm, one build, one sweep).

Sweep loop (expect E48E 7/7 after all arms; at `e49902a` E48E1..E48E5 are exact and
E48E7/E48E8 refuse by name — arms 4/5; E48E6 must KEEP refusing):

    for n in 1 2 3 4 5 7 8; do ./ocaml/_build/default/bin/pli80c.exe probes/E48E$n.PLI /tmp/sw/E48E$n.REL \
      && cmp /tmp/sw/E48E$n.REL golden/e48p2e/E48E$n/E48E$n.REL && echo "E48E$n IDENTICAL"; done

Then the regression sweeps: E48D1..D10 (`golden/e48p2db`) 10/10, E48C1..C9 9/9, e48p1 24/24,
E46K1/K3 2/2 (`golden/e48p2retire`), and the FULL negative panel with GATE semantics (CRLF +
`^Z`, stderr) — 181 rows, and E46K14's marker must NOT move (see arm 2).

(Step 3 — arm 3 `= '0'b' VALUE` — is DONE and measured at `e49902a`; its verbatim spec and
the actuals are archived in `docs/history/2026-10-31-p2e-arm3-closed.md`. Numbering below
keeps the round's ids.)

4. **Arm 4 — FIXED member in TEST via `?SCCCM`** (the biggest arm; §2.4). `str_side` (6870)
   classifies only `Vimem m when m.varying -> Some (`Imem name)`; add a FIXED-member variant that
   carries `m.cap` (the declared extent IS in `mem_char`, codegen.ml:26-27). Add a new
   literal-LEFT/fixed-RIGHT encoder producing exactly
   `21 *D(member) / 11 *D(pool lit) / 06 len / 3E cap / CD ?SCCCM`, used by `lower_test_skip0`
   (the guard at 7597 and the destructuring at 7609) — NOT by `bit_cond_mat`: §2.4 measures TEST
   only and §3 says a fixed member in a STORE is unmeasured, so the STORE route must keep
   refusing it. **THE DEMAND TWIN IS MANDATORY (the fa09b97/e21281a law):** `prescan_cond`'s
   `is_var` (~2981) currently returns `m.varying`; widen it to admit a FIXED internal member
   ONLY because the TEST route now admits it — demand and lowering stay ONE predicate, or the
   C152 pool invariant dies. Verify DATA 000B for E48E7 against the golden.
5. **Arm 5 — bit item behind a file attach** (`authorize_file_item`, refusal text quoted in
   `BASELINE-MINE.txt` E48E8; the console bit chain already exists at ~10775 `Vbit1`). Admit
   `Vbit1` on the file route and reuse the SAME chain bytes
   (`3A *D(b) / 06 01 / CD ?QB08C / CD ?PNBOP`) inside [C296]'s frame; §2.5 + E46L3 prove the
   chain is route-invariant. PUT EDIT of a bit item and every other unadmitted file class stay
   refused. Keep the falsified premise of the removed guard visible as a SUPERSEDED comment.
6. **Claims + registration + gate.** Record C327+ from RESULTS §2 ONLY (each citing its golden),
   classify §2.6 as `dr-refuses` and arms 1-5 as `my-gap`; append the traceable correction to
   **[C296]** ("`LXI H,<fcb>`" is really `LXI H,*C(0000)`, a CODE self-address — HYPOTHESES.md
   §Prior-evidence has the byte dump) and to [C324]/[C310]'s [TBD] clauses (closed by
   reference, originals kept). Register E48E1..E48E5, E48E7, E48E8 in the gate's own
   `SPECIMENS.update({...})` dict in `tools/e2e_gate.py` (NOT `spec/SPECIMENS.tsv`, which is a
   stale E2E-39 artefact; precedents `992ccad`/`f67cc6d`/`adbfa2a`), **BYTE TIER ONLY — no
   `spec/RUNTIME.txt` and no `OUTPUT_CHECK` row may come from this round**. E48E6 is NOT a
   specimen: it has no `.REL`; if a negative row for it is wanted it must go through the gate's
   write path with an explicit reason, never by hand-editing a verdict. Then
   `python3 tools/e2e_gate.py --update-inventory` (review the diff line by line), census
   `cp spec/census/corpus-census.json /tmp/census-prev.json && python3 tools/corpus_census.py
   --check /tmp/census-prev.json` (re-read EVERY msg delta; a corpus advance is not a
   regression), `python3 tools/coverage_check.py`, `registration_audit`, and the FULL GATE
   `python3 tools/e2e_gate.py` — **report ACTUAL numbers, never expected** (baseline was 1120/0,
   negative 181/181, divergence 9/9, coverage 113 rows). Then `spec/COVERAGE.tsv` rows for the
   five new shapes vs the new claims (15 columns, `manual_ref = NONE:<why>`, MEASURED rows cite
   probes named by their OWN claims; `coverage_check` REWRITES
   `spec/census/coverage-stats.json` — commit that path when it changes).

**Standing:** never touch `golden/e48p1`, `e48p2c`, `e48p2d` (botched run), `e48p2db`,
`e48p2retire`, `e42p1c`, `e42p2a`, `e42p2b`, `first8080u`, `e48p2e` (new goldens — evidence);
implement NOTHING from RESULTS §3 (fixed member in a STORE, member-vs-member, BASED member in a
condition, over-extent INITIAL/store, any runtime claim); no `%include`/LOAN2 work without its
own pre-registered round; **do not commit or revert `handoff.config.json` — the
`workingContextWindow` 95000 -> 145000 edit is the OPERATOR's**; no push; probes <= 71 cols and
CRLF + `^Z`; build needs `eval $(opam env)`; **never name a probe variable `c`** (it reads as a
procedure call — see LEARNINGS); renewal 8/8 is the LAST hop under the cap.

## Unfinished operations

- **No half-finished edit.** Arm 3 landed and was measured at `e49902a`; arms 4, 5 are NOT
  started; step 6 is OWED (claims C327+ — the
  ledger ends at C326; NEG_META E46K14 dr-refuses re-classification; SPECIMENS registration of
  the 7 probes byte tier only; `--update-inventory`; census `--check`; `coverage_check`;
  `registration_audit`; FULL GATE reporting ACTUAL; COVERAGE rows; the [C296] `LXI H,*C(0000)`
  correction) — all specified command-level in the single active Next-action section above.
- The working tree at this checkpoint carries ONLY the operator's `handoff.config.json` edit.

## Discoveries not yet incorporated

- None outstanding. Durable method lessons are already classified in `LEARNINGS.md`; compiler
  law lives in `spec/CLAIMS.md` (C327+ owed by step 6, from `e2e48-p2e/RESULTS.md` §2 ONLY).
  The stale `README.md` rolling status is recorded as deferred work in `PROGRESS.md` → Pending.

## History and pointers

- Superseded next-action sections, closed phase records and the full renewal-hop status log:
  `docs/history/README.md` (extracted verbatim at `f3a4c60`).
- Renewal: the E2E-48 phase chain closed at its configured cap; state archived under
  `.pi-guard/archives/`. Effective renewal values are in `handoff.config.json` (authoritative) —
  never this file. The guard writes the managed block below via Handoff commands only.

<!-- guard:begin checkpoint -->
checkpoint-schema: 3
checkpoint-generation: 52
checkpoint-id: g52-ae1a170251b3
checkpoint-kind: manual
content-delta: new
readiness: attested
status: checkpoint (guard level 0, remaining ~40000, session 01a18f18-f7db-70fd-bf5a-eff1b343972f)
checkpointed: 2026-10-31T00:02:57.734Z
source-goal: 730790b648a1e1d14b76243cfe8bc17eea2ba9cd8527f204f9c8d4dbcc527c9d
source-progress: b9c99cc1738bcd4ca66ec98080dd0d40782c0b3cf0a2c54b664dc32f41990a08
source-handoff: a5c9150c17c39e7538352ad244b2f8859ad0517b6d6764f6871046081e0da28c
source-learnings: dff47b3bc4c6177a18669d93bce31273c268afbf2848eaf71e74ec2b83f4a92c
source-config: 0f0cc9c7af73d792e6af3120538e1c6254f8a81ee93993e3088a7e2c76d8ef80


readiness-by: session:01a18f18-f7db-70fd-bf5a-eff1b343972f
readiness-at: 2026-10-31T00:02:57.738Z
readiness-checkpoint: g52-ae1a170251b3
### Last verified state
guard level 0; checkpoint requested (finalize: Mission-2 audit corrections applied (operator-approved, branch mission1-docs-consolidation): FAIL-2 archive addendum 7beb633 restores the one dropped baseline PROGRESS bullet verbatim (19/19 excerpts now byte-verified against f3a4c608); FAIL-1 prose fix 93c5bca removes the four inline heading-substring traps so guard extraction lands on the single real level-2 Next-action heading (upstream pi-handoff issue #8 remains OPEN and unfixed — workaround only). Scientific landing spec re-verified byte-identical (baseline HANDOFF 180-187/207-255); all protected trees zero-diff vs f3a4c608; arms 3/4/5 and step 6 remain NOT STARTED/OWED; operator config edit preserved unstaged; no renewal, no push.)

### Unfinished operations
- (none recorded)

### Next action
— E2E-48/P2e: LOWER arms 3, 4, 5 (NOT STARTED), then step 6 (claims + registration + FULL GATE)

> Arm numbering keeps the round's ids: arms 1–2 landed at `d18c6ab`/`bab0d16` (specs archived
> in `docs/history/2026-10-30-next-actions.md`); references below to "arm 1"/"arm 2" mean that
> completed, measured work. **ONE arm per commit**, `cd ocaml && eval $(opam env) && dune build`
> + the cmp sweep after EACH (LEARNINGS rule: one arm, one build, one sweep).

Sweep loop (expect E48E 7/7 after all arms; E48E6 must KEEP refusing):

    for n in 1 2 3 4 5 7 8; do ./ocaml/_build/default/bin/pli80c.exe probes/E48E$n.PLI /tmp/sw/E48E$n.REL \
      && cmp /tmp/sw/E48E$n.REL golden/e48p2e/E48E$n/E48E$n.REL && echo "E48E$n IDENTICAL"; done

Then the regression sweeps: E48D1..D10 (`golden/e48p2db`) 10/10, E48C1..C9 9/9, e48p1 24/24,
E46K1/K3 2/2 (`golden/e48p2retire`), and the FULL negative panel with GATE semantics (CRLF +
`^Z`, stderr) — 181 rows, and E46K14's marker must NOT move (see arm 2).

3. **Arm 3 — `= '0'b' VALUE** (the fallback inside `bit_cond_mat`'s `Eq` arm, ~7222-7232, which
   admits only `Ast.Ebit "1"`). Emit for `Ast.Ebit "0"`: `3A *D(b) / E6 80 / D6 01 / 9F`
   (E48E5 0006, 11 bytes incl. the `32` STA) — i.e. the `'1'b` head WITHOUT the `D6 80` step.
   `bit_store_cond_bytes` demands nothing here (no pool cell), so no prescan change.
4. **Arm 4 — FIXED member in TEST via `?SCCCM`** (the biggest arm; §2.4). `str_side` (6870)
   classifies only `Vimem m when m.varying -> Some (`Imem name)`; add a FIXED-member variant that
   carries `m.cap` (the declared extent IS in `mem_char`, codegen.ml:26-27). Add a new
   literal-LEFT/fixed-RIGHT encoder producing exactly
   `21 *D(member) / 11 *D(pool lit) / 06 len / 3E cap / CD ?SCCCM`, used by `lower_test_skip0`
   (the guard at 7597 and the destructuring at 7609) — NOT by `bit_cond_mat`: §2.4 measures TEST
   only and §3 says a fixed member in a STORE is unmeasured, so the STORE route must keep
   refusing it. **THE DEMAND TWIN IS MANDATORY (the fa09b97/e21281a law):** `prescan_cond`'s
   `is_var` (~2981) currently returns `m.varying`; widen it to admit a FIXED internal member
   ONLY because the TEST route now admits it — demand and lowering stay ONE predicate, or the
   C152 pool invariant dies. Verify DATA 000B for E48E7 against the golden.
5. **Arm 5 — bit item behind a file attach** (`authorize_file_item`, refusal text quoted in
   `BASELINE-MINE.txt` E48E8; the console bit chain already exists at ~10775 `Vbit1`). Admit
   `Vbit1` on the file route and reuse the SAME chain bytes
   (`3A *D(b) / 06 01 / CD ?QB08C / CD ?PNBOP`) inside [C296]'s frame; §2.5 + E46L3 prove the
   chain is route-invariant. PUT EDIT of a bit item and every other unadmitted file class stay
   refused. Keep the falsified premise of the removed guard visible as a SUPERSEDED comment.
6. **Claims + registration + gate.** Record C327+ from RESULTS §2 ONLY (each citing its golden),
   classify §2.6 as `dr-refuses` and arms 1-5 as `my-gap`; append the traceable correction to
   **[C296]** ("`LXI H,<fcb>`" is really `LXI H,*C(0000)`, a CODE self-address — HYPOTHESES.md
   §Prior-evidence has the byte dump) and to [C324]/[C310]'s [TBD] clauses (closed by
   reference, originals kept). Register E48E1..E48E5, E48E7, E48E8 in the gate's own
   `SPECIMENS.update({...})` dict in `tools/e2e_gate.py` (NOT `spec/SPECIMENS.tsv`, which is a
   stale E2E-39 artefact; precedents `992ccad`/`f67cc6d`/`adbfa2a`), **BYTE TIER ONLY — no
   `spec/RUNTIME.txt` and no `OUTPUT_CHECK` row may come from this round**. E48E6 is NOT a
   specimen: it has no `.REL`; if a negative row for it is wanted it must go through the gate's
   write path with an explicit reason, never by hand-editing a verdict. Then
   `python3 tools/e2e_gate.py --update-inventory` (review the diff line by line), census
   `cp spec/census/corpus-census.json /tmp/census-prev.json && python3 tools/corpus_census.py
   --check /tmp/census-prev.json` (re-read EVERY msg delta; a corpus advance is not a
   regression), `python3 tools/coverage_check.py`, `registration_audit`, and the FULL GATE
   `python3 tools/e2e_gate.py` — **report ACTUAL numbers, never expected** (baseline was 1120/0,
   negative 181/181, divergence 9/9, coverage 113 rows). Then `spec/COVERAGE.tsv` rows for the
   five new shapes vs the new claims (15 columns, `manual_ref = NONE:<why>`, MEASURED rows cite
   probes named by their OWN claims; `coverage_check` REWRITES
   `spec/census/coverage-stats.json` — commit that path when it changes).

**Standing:** never touch `golden/e48p1`, `e48p2c`, `e48p2d` (botched run), `e48p2db`,
`e48p2retire`, `e42p1c`, `e42p2a`, `e42p2b`, `first8080u`, `e48p2e` (new goldens — evidence);
implement NOTHING from RESULTS §3 (fixed member in a STORE, member-vs-member, BASED member in a
condition, over-extent INITIAL/store, any runtime claim); no `%include`/LOAN2 work without its
own pre-registered round; **do not commit or revert `handoff.config.json` — the
`workingContextWindow` 95000 -> 145000 edit is the OPERATOR's**; no push; probes <= 71 cols and
CRLF + `^Z`; build needs `eval $(opam env)`; **never name a probe variable `c`** (it reads as a
procedure call — see LEARNINGS); renewal 8/8 is the LAST hop under the cap.

### Guard notes
Mission-2 audit corrections applied (operator-approved, branch mission1-docs-consolidation): FAIL-2 archive addendum 7beb633 restores the one dropped baseline PROGRESS bullet verbatim (19/19 excerpts now byte-verified against f3a4c608); FAIL-1 prose fix 93c5bca removes the four inline heading-substring traps so guard extraction lands on the single real level-2 Next-action heading (upstream pi-handoff issue #8 remains OPEN and unfixed — workaround only). Scientific landing spec re-verified byte-identical (baseline HANDOFF 180-187/207-255); all protected trees zero-diff vs f3a4c608; arms 3/4/5 and step 6 remain NOT STARTED/OWED; operator config edit preserved unstaged; no renewal, no push.
<!-- guard:end checkpoint -->
