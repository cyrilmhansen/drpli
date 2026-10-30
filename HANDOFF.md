# HANDOFF.md — DRPLi

Manual prose wins over the managed block below it. Do not hand-edit the managed block.
This file is the recovery entry point: exactly ONE active `## Next action`. Closed-phase
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

## Last verified state — E2E-48/P2e lowering (verified at baseline `f3a4c60`, 2026-10-30)

- Arms 1 + 2 of the six RESULTS §2 arms are DONE, committed and measured (`d18c6ab`,
  `bab0d16`): E48E1..E48E4 whole-file byte-identical; E46K14's pinned refusal RE-MEASURED
  through the binary with gate CRLF+`^Z` semantics — marker unchanged, NOT re-pinned; its
  `imem_refuse` WHY-string now cites `golden/e48p2e/E48E6/E48E6.PRN` as a MEASURED dr-refuses
  (append, original verbatim). **Arms 3, 4, 5 are NOT STARTED; step 6 (claims/registration/
  gate/COVERAGE) is OWED.** No `ocaml/` edit is half-done.
- Laws and refusals: `spec/lab-evidence/e2e48-p2e/RESULTS.md` §2 (six laws) and §3 (what
  stays unmeasured) are the authority; claims are owed as C327+ (next action step 6).
- E48E6 (`if line then`, CHARACTER VARYING member as bare condition) is **dr-refuses**
  (`BIT REQ`, no `.REL`); it is NOT a specimen and gets no `.REL`-based row.
- Regression baselines in force: e48p1 24/24, e48p2c 9/9, e48p2db 10/10, e48p2retire 2/2;
  FULL GATE baseline 1120 byte-exact / 0 fail (`adbfa2a`), negative 181/181, divergence 9/9,
  coverage 113 rows 0 errors (`218b474`), census 15/0/26/0; clean-rebuild warning multiset 126.

## Next action — E2E-48/P2e: LOWER arms 3, 4, 5 (NOT STARTED), then step 6 (claims + registration + FULL GATE)

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

## Unfinished operations

- **No half-finished edit.** Arms 3, 4, 5 are NOT started; step 6 is OWED (claims C327+ — the
  ledger ends at C326; NEG_META E46K14 dr-refuses re-classification; SPECIMENS registration of
  the 7 probes byte tier only; `--update-inventory`; census `--check`; `coverage_check`;
  `registration_audit`; FULL GATE reporting ACTUAL; COVERAGE rows; the [C296] `LXI H,*C(0000)`
  correction) — all specified command-level in `## Next action`.
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
checkpoint-generation: 51
checkpoint-id: g51-23d103d23a1d
checkpoint-kind: manual
content-delta: new
readiness: attested
status: checkpoint (guard level 0, remaining ~40000, session 01a18ed4-fe26-70c1-9a9a-b62385db7ea9)
checkpointed: 2026-10-30T23:02:14.979Z
source-goal: 730790b648a1e1d14b76243cfe8bc17eea2ba9cd8527f204f9c8d4dbcc527c9d
source-progress: 3f2642cd1a3146636712fab8af6d949009c1f546c08ea1b1ed079638459c184f
source-handoff: 182831f43f13fdd6058c118e12da9214a344f779f72d812d4815d72ca8a83024
source-learnings: dff47b3bc4c6177a18669d93bce31273c268afbf2848eaf71e74ec2b83f4a92c
source-config: 0f0cc9c7af73d792e6af3120538e1c6254f8a81ee93993e3088a7e2c76d8ef80


readiness-by: session:01a18ed4-fe26-70c1-9a9a-b62385db7ea9
readiness-at: 2026-10-30T23:02:14.982Z
readiness-checkpoint: g51-23d103d23a1d
### Last verified state
guard level 0; checkpoint requested (finalize: Mission-1 docs consolidation complete (519a362 + e2549e5, branch mission1-docs-consolidation): HANDOFF/PROGRESS reduced to current state; exactly ONE active ## Next action (E2E-48/P2e arms 3,4,5 then step 6 — landing spec kept verbatim); verbatim archives + index under docs/history/ (baseline f3a4c608); selective-ledger recovery protocol; AGENTS/PROTOCOL quote no numbers (handoff.config.json sole numeric authority); GOAL + all scientific trees zero-diff; operator config edit preserved unstaged.)

### Unfinished operations
- (none recorded)

### Next action
`. Closed-phase
history is archived under `docs/history/` (index: `docs/history/README.md`); science is
authoritative only in `spec/CLAIMS.md` and `spec/lab-evidence/`.

### Guard notes
Mission-1 docs consolidation complete (519a362 + e2549e5, branch mission1-docs-consolidation): HANDOFF/PROGRESS reduced to current state; exactly ONE active ## Next action (E2E-48/P2e arms 3,4,5 then step 6 — landing spec kept verbatim); verbatim archives + index under docs/history/ (baseline f3a4c608); selective-ledger recovery protocol; AGENTS/PROTOCOL quote no numbers (handoff.config.json sole numeric authority); GOAL + all scientific trees zero-diff; operator config edit preserved unstaged.
<!-- guard:end checkpoint -->
