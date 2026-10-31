# PROGRESS.md — DRPLi

Manual prose wins over the managed block below it. Do not hand-edit the managed block.
This file tracks *working state*; compiler behaviour itself belongs to `spec/CLAIMS.md`.

## Current phase — E2E-48/P2e lowering (verified at baseline `f3a4c60`, 2026-10-30)

- **Arms 1 + 2 DONE and measured**: `d18c6ab` (`bit_cond_mat` merged `abs kk >= 1` arm;
  `bin_lit` folds `Eprefix(Minus,Enumber)`; bare `-0` stays refused, no golden — E48E1/E48E2
  whole-file byte-identical) and `bab0d16` (NegL VALUE arm gains the ladder with `flag_neg`
  `C6 FF/9F` — E48E3/E48E4 byte-identical; E46K14 marker re-measured unchanged; WHY-string
  cites `golden/e48p2e/E48E6/E48E6.PRN` as MEASURED dr-refuses). Laws owed as claims C327/C328
  by step 6 — the ledger ends at C326.
- **Arms 3, 4, 5 NOT STARTED; step 6 OWED.** The single exact, command-level landing spec is
  `HANDOFF.md` → its single level-2 Next-action heading (arm 3 `= '0'b` VALUE 11 bytes; arm 4 FIXED-member TEST via a
  NEW `?SCCCM` encoder + prescan demand twin; arm 5 `authorize_file_item` admits Vbit1; step 6
  claims C327+ / NEG_META E46K14 dr-refuses stamp / SPECIMENS.update 7 probes byte tier only /
  --update-inventory / census --check / coverage_check / registration_audit / FULL GATE reporting
  ACTUAL / COVERAGE rows; [C296] `LXI H,<fcb>` → `LXI H,*C(0000)` correction owed).
- Sweeps at HEAD: E48E 4/7 exact + E48E5/E48E7/E48E8 refused by name + E48E6 refused (correct);
  e48p1 24/24, e48p2c 9/9, e48p2db 10/10, e48p2retire 2/2; clean-rebuild warning multiset
  126 = 28/26/22/17/15/14/2/2 UNCHANGED.
- No half-edited state. Working tree carries ONLY the operator's `handoff.config.json` edit —
  leave it uncommitted and untouched. Standing prohibitions (goldens, §3 shapes, probes ≤71 cols
  CRLF+`^Z`, `eval $(opam env)`, never name a probe variable `c`, no push) are in HANDOFF.md.

## Next action

The ONE active, command-level spec lives in `HANDOFF.md` → its single level-2 Next-action
heading (E2E-48/P2e arms
3, 4, 5 NOT STARTED, then step 6). No competing action exists anywhere else; PROGRESS does not
restate it (PROTOCOL: handoff docs point at claims/specs, never duplicate authority).

## Verified milestones (provenance: `docs/history/README.md`; evidence: `spec/lab-evidence/`)

- E2E-48/P1 — 24/24 probes byte-identical + registered, claims C309–C316, gate 1098/0: `992ccad`.
- E2E-48/P2c CLOSED — arms `14c7321`…`e21281a` era, RETIRE promotions, claims C317–C320,
  FULL GATE 1109/0 negative 182/182: `f67cc6d`; COVERAGE rows + appends: `ef0a198`.
- E2E-48/P2d — run 1 botched (>72-col comments; kept `67bf83c`), wrap `60a2c06`, run 2 10/10
  `d28ff5e`; claims C321–C326 `aa4b5b4`; six arms `6545b5d`/`6491981`/`a72ce43`/`18a06c0`/
  `1e8acb2`/`e21281a`; registration + FULL GATE 1120/0, negative 181/181, census 15/0/26/0,
  INVENTORY 1301: `adbfa2a`; COVERAGE 113 rows 0 errors: `218b474`.
- E2E-48/P2e round 5 — pre-registration `421656a` committed BEFORE the oracle; one run
  7 ok / 8 (E48E6 `BIT REQ` = dr-refuses; P-E6 MISS kept in RESULTS §1); goldens + RESULTS
  `e2b77ba`; lowering arms 1–2 `d18c6ab`/`bab0d16`.

## Completed

*Scientific — recorded, not re-run by this session:*
- `PUT FILE … SKIP` behaviour measured on DR and lowered byte-exactly: `E46N11`–`E46N22`
  bank, 18 specimens added → **1074 byte-exact / 0 fail** recorded in
  `spec/lab-evidence/e2e42-p2c/RESULTS.md` §8; runtime panel 71/71 as recorded.
- Gate tiering + `--link-run` able to fail; slow CP/M arms delegated to the external
  `rune-ci` builders (`GATE-TIERS.md`, `spec/notes/rune-ci-external-gate.md`).
- The `timeout-or-hang` collapse in `oracle/run.py`/`linkrun.py` re-measured by exit code:
  51 timeouts, 2 emulator deaths (`PD7`, `PD9`), 2 that do terminate (`RFACT`, `V5`) —
  `[C308]`, and the `HANG_ARMS` / `NO_RUN_ARMS` / `NO_LINK_ARMS` split in `tools/e2e_gate.py`.

*Infrastructure — performed and verified by this session (see `HANDOFF.md` for the boundary):*
- `.gitignore`: appended only the `# Pi Handoff runtime state` / `.pi-guard/` rule; all
  pre-existing oracle/golden/build/thirdparty rules verified still matching.
- Extension installed at `.pi/extensions/context-guard/{index,core,config,checkpoint,renewal}.ts`,
  taken from the pinned Git revision (bytes verified by SHA-256 and blob id against
  `v0.1.0-dev.1` / `2ea6219`); nothing else from the source repo was copied.
- Skill installed at `.agents/skills/pi-handoff/{SKILL.md,references/bootstrap.md,references/commands.md}`.
- `handoff.config.json` written: `readOnly: true` during validation, `enforceClosing: false`,
  `autoCheckpointAtHandoffLevel: false`, renewal disabled, `generationReserve: 20000`
  (initial policy value, not yet tuned).
- Durable files created: `AGENTS.md`, `GOAL.md`, `PROTOCOL.md`, `HANDOFF.md`, `PROGRESS.md`,
  `LEARNINGS.md`.
- **Phase D (read-only) passed in the real Pi runtime**: extension loaded with no import/TS
  errors; `/guard status` reported read-only mode + the real model/window/reserve; `/handoff
  verify` reported `missing` without writing; `/handoff ready check` evaluated without
  attesting; `/guard simulate 30000` → level 1, `/guard simulate 10000` → level 3 with **no**
  checkpoint written; `/handoff` reported a dry run; no `.pi-guard/` directory was created; every
  tracked file hash, the ignored-file count (471 102) and the profile settings were unchanged.
- **Phase E (writable) passed**: `/handoff` → `g1-01ad31c23339`, generation 1,
  content-delta `initial`, freshness `current`; `/handoff ready check` → READY with four blocking
  PASSes; `/handoff ready` → attested; both blocks shared one transactional identity.
  A level-3 automatic checkpoint (`checkpoint-kind: auto`) then preserved a substantive
  "Last verified state" line and a "Guard notes" block **verbatim**, leaving all manual prose
  outside the managed blocks byte-identical, and left `GOAL.md`/`LEARNINGS.md` untouched.


## Pending
- **LOAN2's new prescan my-gap** (`variable i declared with conflicting kinds; decimal pool prescan
  needs one unambiguous type map [TBD]`): measured cause, fix NOT attempted. `codegen.ml:12460-12490`
  builds ONE global `pd_vars` name -> vkind map for the DEC-pool prescan, and LOAN2 declares `i`
  `fixed decimal(4,2)` at line 32 and `fixed bin` at line 211 — two scopes, both legal, DR accepts
  (its golden exists). Making the prescan scope-aware touches ~15 `List.assoc_opt … cx.pd_vars`
  call sites whose prescan deliberately runs WITHOUT statement context, so it is a design change,
  not an arm. It needs its own measured plan; do not start it on faith.
- CREATE remains NOT byte-exact; its measured blocker is still the front-end `%include` gap
  (`pli80c.ml` never expands INCLUDE). Do NOT implement any unmeasured shape from the
  [TBD] list in RESULTS section 3.
- **Renewal chain:** the E2E-48 phase chain closed at its configured cap; its state file is
  archived under `.pi-guard/archives/` and a new session starts a fresh count per
  `handoff.config.json` — the config and `/guard status` are authoritative for enablement,
  autoRenew and cap; this file quotes no numbers.
- **Deferred documentation work (recorded, operator-aware):** `README.md` "Current status
  (rolling)" is stale (ends at E2E-1/C067); it was deliberately NOT touched by the Mission-1
  documentation consolidation. Never use it for status — the ledger and this file are authority.

## Verified evidence

Measured at the baseline session (2026-10-30, HEAD `f3a4c60`), not quoted from a report:
arms 1–2 produce E48E1..E48E4 whole-file byte-identical (`cmp` at `d18c6ab`/`bab0d16`); E46K14's
pinned refusal re-measured through the binary with gate CRLF+`^Z` semantics — marker unchanged,
NOT re-pinned; regression sweeps e48p1 24/24, e48p2c 9/9, e48p2db 10/10, e48p2retire 2/2;
clean-rebuild warning multiset 126 = 28/26/22/17/15/14/2/2 unchanged. FULL GATE figures
(1120/0, negative 181/181, coverage 113/0, census 15/0/26/0) are recorded from `adbfa2a`/`218b474`
and were NOT re-run by the documentation consolidation — the next gate measurement belongs to
step 6 and must be reported ACTUAL. Round evidence: `golden/e48p2e/`,
`spec/lab-evidence/e2e48-p2e/{RESULTS,HYPOTHESES,BASELINE-MINE}`; closed-round records:
`docs/history/`.

<!-- guard:begin checkpoint -->
checkpoint-schema: 3
checkpoint-generation: 52
checkpoint-id: g52-ae1a170251b3
checkpoint-kind: manual
content-delta: new
readiness: attested
guard-level: 0
checkpointed: 2026-10-31T00:02:57.734Z
source-goal: 730790b648a1e1d14b76243cfe8bc17eea2ba9cd8527f204f9c8d4dbcc527c9d
source-progress: b9c99cc1738bcd4ca66ec98080dd0d40782c0b3cf0a2c54b664dc32f41990a08
source-handoff: a5c9150c17c39e7538352ad244b2f8859ad0517b6d6764f6871046081e0da28c
source-learnings: dff47b3bc4c6177a18669d93bce31273c268afbf2848eaf71e74ec2b83f4a92c
source-config: 0f0cc9c7af73d792e6af3120538e1c6254f8a81ee93993e3088a7e2c76d8ef80
next-action: — E2E-48/P2e: LOWER arms 3, 4, 5 (NOT STARTED), then step 6 (claims + registration + FULL GATE)

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
readiness-by: session:01a18f18-f7db-70fd-bf5a-eff1b343972f
readiness-at: 2026-10-31T00:02:57.738Z
readiness-checkpoint: g52-ae1a170251b3
<!-- guard:end checkpoint -->

## Blockers

- Nothing is half-edited at this boundary; every item below is recorded evidence, not a guess.
- **Missing evidence is the limit, never a licence to guess** (`PROTOCOL.md` #4). The
  E2E-48/P2e RESULTS §3 shapes stay named refusals until a pre-registered round measures them:
  FIXED member in a condition STORE, member-vs-member compare, BASED member in a condition,
  over-extent INITIAL/store, `^=` over a ladder, `^(string compare)`, bare `-0` spelling,
  runtime length rewrite, empty-varying PUT output. No `spec/RUNTIME.txt` row may come from
  this phase family.
- CREATE is NOT byte-exact; measured front-end blocker: `pli80c.ml` never expands `%include`
  (proposal in `LEARNINGS.md` is `proposed, unverified` — needs its own pre-registered round).
- LOAN2's `conflicting kinds` prescan my-gap is a design change, not an arm (see Pending).
- Step 6 debts: claims C327+ unwritten; the [C296] `LXI H,<fcb>` → `LXI H,*C(0000)` traceable
  correction owed; E46K14's NEG_META re-classification owed.
