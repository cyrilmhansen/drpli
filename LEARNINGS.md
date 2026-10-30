# LEARNINGS.md — DRPLi

Ledger of **working methods and environment knowledge**, including handoff-infrastructure
lessons. It is **not** the evidence ledger: anything about compiler behaviour belongs in
`spec/CLAIMS.md` with its specimen and golden paths, and is referenced here, never copied.
The guard never writes this file.

## Accepted

- **A pre-flight ledger drift can hide the fact that nothing regressed.** The gate aborts at
  `corpus census --verify` / coverage / prose checks **before** the byte panel compiles anything, so
  a drift looks like "the gate number is unknown", not like "the compiler broke". This session the
  drift was *progress*: CREATE's first-refusal message had moved from
  `condition form not in E2E-3b subset [TBD]: (^ eofile)` to `GET LIST of unknown variable name`
  because the `371a12e` arms lowered both earlier blockers. Read the recomputed message before
  treating a drift as a regression; then re-measure the snapshot through the tool's own write path
  (`--check PREV.json`, with PREV a copy of the old file so a *count* change still fails) and
  record why. [accepted, measured 2026-10-29]
- **Bisect an invariant failure with one-statement scratch programs, not by reading the failing
  probe.** `E48A12`'s "prescan demanded 5, lowering allocated 8" became obvious at `/tmp/t_a.PLI`
  (`b = (name = 'EOF');` alone: demanded 1, allocated 4). The same four scratch runs also produced
  a fact the probes could not show: `if (name = 'EOF') then` still refuses in TEST position while
  the identical compare lowers fine in STORE position — the two routes have separate demand paths.
  [accepted, measured 2026-10-29]
- **When a new item class has its own tail, check whether the shared tail is universal.** The
  console-PUT item chain ends every arm with `tail true ()` (or `false`). DR's bit item carries
  `?PNBOP` *instead of* `?PNCOP` (C313), so the shared emitter had to become conditional —
  otherwise the bytes get both tails. Two lessons in one: (a) read the code that runs *after* the
  match you are extending, not just the match; (b) a dropped `;` after `(match ...)` is a syntax
  error the build catches immediately — write one arm, build, sweep.
  [accepted, measured 2026-10-29]
- **Refusal TEXTS are panel rows; grep before you loosen one.** Gate rows pin substrings of my own
  messages (`"STATIC on CHAR(14) VARYING is unsampled"` for E46F5, `"STATIC on FIXED BINARY(15,0)
  is unsampled"`, `"char var in multi-item PUT unproven"` for E46M12, `"store into BIT(1) from
  ident is unsampled"` for N74). Loosening a classifier also has to be checked against the
  negative rows' *sources*: `P052A/P053A/B/C` and `E46J10/J19` put `BIT(4)/(8)/(16)/(3)`, which are
  a different class from `Vbit1`, so admitting `Vbit1` left 184/184 intact. Verified by grep, then
  by running the panel. [accepted, measured 2026-10-29]
- **Compare warning multisets between two CLEAN builds, and do it in a scratch tree.**
  `cp -r ocaml /tmp/basebuild && git show <base>:ocaml/lib/codegen.ml > ...` then clean-build both
  and `diff` the sorted `Warning N [name]` counts. This session both sides were
  22/15/28/2/14/2/17/26 (kinds 11/26/27/32/39/57/8/9) — my edits added nothing, including the two
  Warning 11s whose line numbers landed inside code I had just edited (pre-existing).
  [accepted, measured 2026-10-29]

- **In OCaml, an arm body that begins with an unparenthesised `match` silently steals the
  following arms of the enclosing `match`.** I added a `match rhs.Ast.e with …` as the body of the
  `| Ast.Eident n when … = Vbit1 ->` arm of `lower_assign`'s `match lhs.Ast.e`; OCaml parsed every
  later `| Ast.Eident …` as a case of MY inner match, so the outer match lost its DEC / varying /
  based arms and 15 probes died with `Match_failure` at the *outer* `match` (codegen.ml:8026) — a
  line I had not touched. It compiles clean (warning 8 is only emitted when a case is provably
  unreachable, and here the stolen cases looked plausible), so `dune build` proved nothing.
  Tell: a `Match_failure` naming a line you never edited, on specimens that passed minutes ago.
  Fix: `begin match … end` (or parentheses) for any match used as an arm body. Rule: **write one
  arm, rebuild, re-run the affected `cmp` sweep — never batch two arms before the first
  verification.** [accepted, measured 2026-10-29: the failure and its cause were observed; the
  fix itself was left UNVERIFIED when the closing phase arrived]
- **`cmp` the whole `.REL` after each arm, not at the end.** Six probes went byte-identical from
  the `^`-TEST arm alone (E48A1/A2/A5/A13/B1/B7), which is what localised the later regression to
  the store/boolean arms instead of a 24-probe mystery. Evidence-first granularity pays in
  debugging time, not just in honesty.

- **A handoff summary can carry a rendering-error that the goldens disprove, and the
  renewal chain propagates it.** The "DR's own DAD H bias defect" recorded in a level-2
  checkpoint summary was traced to a mnemonic typo in `spec/lab-evidence/e2e42-p2b/chaindump.py`
  (`0x09` labeled `dad d`); the literal golden bytes at E48A7:0040/E48A12:003E/E48B1:002E are
  0x09 = DAD B — bias applied correctly, and `hl_bias` already emits 0x09. Nothing to
  reproduce. The predecessor session even wrote the antidote into LEARNINGS ("a mnemonic
  from a disassembler is not evidence") and then committed the error anyway by trusting the
  mnemonic. Lesson: before an inherited summary becomes work ("reproduce the defect"),
  re-read the literal bytes it cites. Evidence: `spec/lab-evidence/e2e48-p1/RESULTS.md` §5;
  tool fixed at commit 388673b. [accepted, measured 2026-10-29]
- **A `max(a, b)` sizing arm must be probed in BOTH regimes.** (pre-existing 2026-10-29
  entry below) — closed the same day: the fix (bind's `section2` span no longer charges
  STATIC rows) is committed at a8d1c3a and E48A3/E48A4 became byte-identical to the new
  goldens with no other change; gate stayed 1074 byte-exact / 0 fail. [accepted, measured]
- **A formula that has only ever been exercised where two terms are large can hide a
  double-count.** My `DEF-DATA-SIZE` is `sy_total + pool_total + max(auto, pl_total) + 2*temps`
  and it passed 1074 specimens, because in every one of them the `max` term was dominated by
  automatics. A static-only program (E48B3) exposes it: bind's `section2` `span` charges
  STATIC rows too, so the static byte is counted twice. Lesson: when a formula is a `max` of two
  quantities, probe the regime where each one wins — that is where the overlap hides. Evidence:
  `golden/e48p1/E48A3, E48B3, E48B5, E48B7` vs `/tmp/e48base/*.REL` (each +1 byte).
- **`--tag` reuse needs `--reuse` and cannot clobber**: `oracle/batch.py` refuses an existing
  golden dir unless `--reuse` is passed, and `--reuse` only *adds* programs. That is what lets a
  second probe round land in the same evidence directory without touching round 1 (measured
  2026-10-29: `SAFETY: golden dir exists; pass allow_reuse to add into it`).
- **A DR defect is a target, not a curiosity.** DR lowers a biased integer compare as `LHLD k /
  LXI B,FFFB / DAD H` — `DAD H` adds HL to itself, so the bias is never applied — where my ladder
  uses the semantically right `DAD B` (0x09 vs 0x19, both 1-byte opcodes). Byte-exactness means
  reproducing the defect and recording it as `[C072]/[C264]`-family historical-quirk preservation
  (GOAL #5), never silently "fixing" it. Tell it apart from a rendering difference: `chaindump.py`
  printed `dad d` for the same byte, so a mnemonic from a disassembler is not evidence — the
  literal `.REL` byte is.
- **Predicting a refusal from absence of a witness is exactly the error PROTOCOL #4 forbids,
  and it is easy to commit even after writing the rule down.** I predicted `put list(b)` would
  be `dr-refuses` because no DR object in the tree prints a bit string; DR compiles it in seven
  of my probes via `LDA / MVI B,01 / ?QB08C / ?PNBOP`. Keep the MISS in `RESULTS.md`.

- **Prove ordering with committed blobs, not filesystem mtimes.** A `git stash -u` + `pop`
  rewrote mtimes and destroyed an ordering claim (E2E-42/P2a:
  `spec/lab-evidence/e2e42-p2a/PROCESS.md`, correction commit `c816af5`). Pre-register a
  prediction bank as a commit before the oracle runs; `git diff <reg-commit> HEAD -- <file>`
  being empty is the proof.
- **A reason string is only as good as the distinction its producer makes.**
  `oracle/linkrun.py` merged `run.py`'s rc=1 (timeout) and rc=2 (emulator died) into one
  `"timeout-or-hang"` label, and 4 of 55 registered "non-terminators" were not
  non-terminators ([C308], `spec/lab-evidence/e2e42-p2c/GATE-TIERS.md` §11). Classify from
  exit codes, and give every distinct fact its own name.
- **A timing/arithmetic tell beats a plausible narrative.** A "hang" that arrived in 4.1 s on a
  25–40 s budget could not be a timeout; genuine hangs in the same set took 94–100 s on a 90 s
  budget. Re-measure alone before believing a pool-con contention story.
- **Never compare two renderings.** DR sizes come from `.REL` segment records
  (`spec/lab-evidence/e2e42-p2b/chaindump.py`), not from a `.PRN` header (`CODE SIZE = 0056` is
  hex); my own `pli80c` stdout `data=` field is not the DATA length
  (`spec/lab-evidence/e2e42-p2c/RESULTS.md` §9, and the [C264] class).
- **Cache-neutral comparisons.** A cached `dune build` prints nothing, so a "0 warnings before
  and after" claim made between a cached and an uncached tree is meaningless — rebuild both trees
  and compare the sorted multiset of warning kinds/messages.
- **An arm that never ran is not a pass.** Excluding `NO_RUN_ARMS` from a panel denominator is
  different from counting them as failures; and a harness whose slow arm *cannot* report a
  verdict cannot be delegated to CI (E2E-42/P2c, `GATE-TIERS.md` §2).
- **Ignored ≠ disposable.** 471 102 files in this tree are ignored — original disk images,
  generated drive images, goldens, gate scratch. There is no safe `git clean` here; verify
  inventory counts before and after any infrastructure change.
- **Verify infrastructure in the real runtime.** A green mock/unit suite does not prove a Pi
  extension loads; load it with `pi -e` and run `/guard status`. A silent load failure disables
  the whole guard apparatus.
- **Verify release bytes from the pinned revision, not a working copy.** `git show <rev>:<path>`
  plus SHA-256/blob-id comparison is the deploy check; the source repo may be mid-development.
- **Environment facts, measured 2026-10-29.** Pi 1.4.0 at `/usr/bin/pi`; production profile
  `/home/john/.sushi/pi` with compaction **enabled** (`reserveTokens`/`keepRecentTokens` 20000)
  and npm packages `pi-web-access`, `pi-params`; Node v26.12.1 (the extension needs ≥ 23 for
  type-stripping); `/home` has 417 G free; oracle uses z80pack `cpmsim -8` (pure 8080);
  `rune-ci` Buildbot lives at `/home/john/services/rune-ci`, bound to 127.0.0.1.
- **Git hygiene for this tree.** Use `GIT_OPTIONAL_LOCKS=0` for inspection; stage explicit path
  lists only; `.pi-guard/` is ignored and must stay out of Git; never touch `.git/worktrees/` or
  the live `/tmp/wt_base` worktree (four worktrees are registered, three of them `prunable` —
  left exactly as found).
- **The launch environment can silently override `handoff.config.json`.** `CONTEXT_GUARD_AUTO_RENEW=1`
  is exported in this operator's shell and turns renewal **and** the model-initiated path on
  regardless of the file (`config.ts`). As of 2026-10-29 renewal is the project policy, but the
  **file must be authoritative**: controlled DRPLi launches strip the inherited override with
  `env -u CONTEXT_GUARD_AUTO_RENEW` and read `/guard status` back to confirm the effective policy
  (the env var remains a per-process kill/experiment switch: `=0` force-off, `=1` force-on).
  Measured 2026-10-29: the first Phase D run reported `enabled=true autoRenew=true` until the
  kill switch was set; the renewal e2e child ran correctly only after `env -u`.
- **Guard slash-commands run without a model turn.** Driving the extension over
  `pi --mode rpc --no-session` and sending them as `prompt` records returns
  `disposition: "handled"` — the state machine can be exercised with zero inference and zero
  transcripts written into the profile. `/reload` is TUI-only there; `new_session` is the
  equivalent for re-running `session_start` (config + checkpoint reload).
- **`/guard simulate` replaces the real measurement for the rest of the session** — after it,
  `/guard status` prints `model: unknown`, `reserve 0` and flags the session `provenance:
  synthetic`. That is by design (`syntheticBudget()`); it means a synthetic run proves the
  switch mechanics only, never real token accounting.
- **Level-3 auto-checkpoints do not lose notes.** `writeCheckpoint(kind:"auto")` reuses the
  previous block's substantive `### Last verified state` and `### Guard notes` (the Phase 1b
  information-loss bug). Verified live on this project: both survived a `checkpoint-kind: auto`
  refresh verbatim, prose outside the markers stayed byte-identical, and `GOAL.md`/`LEARNINGS.md`
  were never written.
- **`content-delta` compares source fingerprints, not wall time.** A second `/handoff` with no
  change in GOAL/prose/LEARNINGS/config yields `content-delta: none`, and readiness then warns
  "checkpoint recorded nothing new" — write the discoveries first, then refresh.

## Accepted (E2E-48/P2c session, measured 2026-10-30)

- **Design a probe bank so it measures its axis EVEN IF a known my-defect is unfixed.** The
  E48C bank declares the record BEFORE the `bit(1) static` (CREATE's own order) in every member
  probe, because writing the bank exposed the level-0 STATIC-chain leak in `dcl_static_dcls`
  (flat scalars pushed as inheritance parents) — with static-first order ALL member probes would
  have died at the DECL, not at the comparison. The one deliberately static-first probe (E48C7)
  then became the bank's oracle arbitration of the defect itself: DR places the record
  AUTOMATIC (DATA `41 42 20 | 00 | pool | rec@000D`). Classification: my-gap, fixed at `6130164`
  only AFTER that golden existed. [accepted, measured]
- **Derive predicted byte-counts by summing instruction widths out of the golden dump, never
  from prose memory.** Seven of nine PREDICTED SEQUENCES hit exactly (helper, registers, length
  byte, skip byte, layout); both misses were my SIZE LABEL for the SCCVM store (I wrote 16, the
  dump is `3+3+2+3+2+1+3 = 17` — I summed the `D6 01 / 9F / 32 X` tail as 5 instead of 6). The
  sequence law was right, the arithmetic was wrong, and the MISS still belongs in the table
  (PROTOCOL #2). [accepted, measured]
- **`tools/corpus_census.py --check <prev>` is measure AND write: it re-measures every program,
  count-guards against the copy, and rewrites `spec/census/corpus-census.{json,tsv}` in the same
  invocation.** After a compiler advance this is the ONE command that both proves counts held and
  refreshes the snapshot; always `git diff` the tsv afterwards and read every msg delta before
  committing. [accepted, measured at `6130164`]
- **A pre-registered oracle round is the cheapest path from [TBD] to law: 9 probes, one batch,
  7/9 predictions confirmed as derived.** Deriving every prediction from literal golden bytes
  (CREATE 008F, E48A6/A12, E29C4/C9, E46J21) instead of from memory is what made the residual
  misses informative (a size label) rather than fatal. [accepted, measured]

## Accepted (E2E-48/P2c implementation, measured 2026-10-30, renewal 7/8 successor)

- **`tools/mk_neg_panel.py` is an UNGUARDED WRITE tool: `--help` executes it.** It rewrites the
  TRACKED, intentionally-FROZEN 65-row `negsrc/` snapshot from today's 184-entry REJECTS --
  renumbering NGxx rows -- and `negsrc/NG14.PLI` is the SOURCE of byte-panel specimen
  N29_DECININT (golden/negpanel1/NG14). The accidental regeneration would have silently
  destroyed that specimen's source. Recovery was exact and non-destructive: `git restore --
  negsrc/` (tree was clean at HEAD before the accident, so HEAD IS the prior state) + removing
  precisely the 119 files listed by `git ls-files --others negsrc/`. RULE: never pass a flag to
  a script that does not parse flags; read the script before invoking it on evidence dirs.
  [accepted, measured 2026-10-30]
- **A widening kills NEGATIVE rows, not just goldens -- replicate the whole panel before
  believing any inherited count.** The checkpoint expected "negative 184/184 (E46F5 row
  re-measured)"; a 15-line replication of the gate's own REJECTS loop (rc!=0 + marker substring,
  importing `e2e_gate` as `mk_neg_panel` does) found E46K1 (admitted by step 4a) and E46K3
  (already admitted by `7701f52`'s arms -- unnoticed because the full gate had not run since
  `1595a10`). Each row's own INVENTORY prose names its retirement procedure (measure DR, then
  promote or re-classify); the expected final numbers are therefore 1109 byte-exact / 182
  refused, NOT the inherited 1107/184. Tell: markers are MESSAGE PREFIXES, so rewording a
  refusal's WHY-text is panel-safe; widening a classifier is not. [accepted, measured 2026-10-30]


(The two entries below belong to the 6/8 successor session and keep their original heading:)

## Accepted (E2E-48/P2c implementation, measured 2026-10-30, renewal 6/8 successor)

- **Re-measure the inherited baseline before writing code; the handoff's numbers were recorded
  at a DIFFERENT HEAD.** The predecessor verified `24/24` and `E48C1 exact` at `6130164` but
  explicitly owed the full gate. Re-running the two sweeps at HEAD `8b42166` reproduced
  24/24 e48p1 whole-file byte-identical, E48C1 byte-identical, and E48C2..C9 refusing with the
  named texts (`store into BIT(1) from condition is unsampled` x4, `store of the internal
  CHARACTER member` x2 for the unqualified spellings, `STATIC on CHAR(14) VARYING is unsampled`,
  `comparison of the internal CHARACTER member`). Tell worth keeping: **the two probes that spell
  the member store unqualified (E48C3/C4) die at the MEMBER-STORE authorization, not at the
  compare** — so arm 1(a) needs BOTH widenings (the compare classifier AND `store_char`'s
  qualified-destination gate) or the sweep cannot reach the compare at all. [accepted, measured]

- **Gate a NEW authorization by CALL SITE, not by classifier, when two positions differ in
  evidence.** RESULTS §2.3 measures `('EOF' = member)' in a STORE but §3 records the same
  orientation in TEST as unmeasured, so widening `str_cmp_shape_rev`'s classifier would have
  silently authorized an unmeasured shape through the TEST arm. The fix is a parameter with the
  safe default (`?(imem = false)`), passed true only by `bit_cond_mat` — one encoder, two
  positions, and the refusal cannot reappear by accident. The mirror-image case is §2.4/§2.1:
  member-LEFT is measured in BOTH positions, so it went into `str_cmp_shape` ungated and arm 3
  (TEST) arrived free. Lesson: before widening a shared classifier, enumerate its callers —
  `grep -n str_cmp_shape ocaml/lib/codegen.ml` is what told me arm 3 needed no new code. Also:
  adding a variant to `str_side` automatically narrows the numeric `?IS22N` guard (which reads
  `None, None -> true`), so a member compare stops mis-routing instead of guessing. [accepted,
  measured 2026-10-30 at `7701f52`: 6/9 E48C byte-identical, 24/24 e48p1 intact]

## Proposed (E2E-48/P2c session)

- **The widening plan for the measured laws is written as the exact command-level next action in
  `HANDOFF.md`** (arms in `bit_cond_mat`, the demand twin, the imem gate, the static-varying
  placement, panel registration to 1107). The gate re-run at the post-census-fix HEAD is still
  owed: the 1098/0 figure is recorded at `1595a10`, not at `6130164`. [proposed, unverified]

## Proposed

- **CREATE's next blocker is a FRONT-END gap, not codegen.** Measured this session: after the
  condition arms landed, CREATE stops at `codegen: GET LIST of unknown variable name [TBD]` for
  `get list (name)`, and `name`/`addr`/`city`/`state`/`zip`/`phone` all come from
  `%include 'record.dcl'` (RECORD.DCL exists in `artefacts/`). `bin/pli80c.ml` reads the source
  text and never expands INCLUDE — that logic lives only in the separate `bin/pli80bind.ml` tool.
  Proposed next round, NOT started: make the main pipeline resolve `%include` (search order and
  case pinned by an oracle probe bank first), then re-measure CREATE's census row. Until then no
  claim about CREATE parity is admissible. [proposed, unverified — the *cause* (no expansion in
  pli80c) is measured, the fix and DR's search order are not]

- **Tune `generationReserve` before trusting the levels.** `20000` is an initial policy number;
  the production model measures `contextWindow=220000`, `maxTokens=65536` (observed via
  `/guard status`), so the reserve is 9.1 % of the window and usable remaining starts at
  ~199 900. Read that again on whichever model a session actually uses, then decide. A reserve is
  a policy budget, not an output cap.
- **Decide project trust separately from explicit loading.** `pi -e …` works without trust;
  `.pi/extensions/` auto-loading and `.agents/skills/pi-handoff/` discovery need operator trust.
  Review skill files before granting it (skills can instruct the model to run scripts).
- **One checkpoint per session, committed in two steps**: prose commit first, then `/handoff`
  refresh + `/handoff ready`, then a separate commit for the managed block if it dirties the tree.
- **Refresh `README.md`'s rolling status** from the ledger, or mark it explicitly historical, so
  no future agent mistakes E2E-1/C067 for the current state.

- **`spec/COVERAGE.tsv` has 15 columns, not 14.** Its schema's first table omits `manual_ref`
  (column 6); the second table and every existing row have it - read an existing row as the template,
  not the prose table. `coverage_check` additionally requires a `MEASURED`/`SINGLE_SAMPLE` row's
  probes to be named by one of the row's OWN cited claims. [accepted, measured 2026-10-29 by reading
  the validator and `COND.GE_LE`; the rows themselves were NOT written - handed on]
- **A level-3 automatic checkpoint can land inside your commit window and change what a commit
  contains.** The guard's `checkpoint-kind: auto` refresh rewrote the managed blocks of HANDOFF.md
  and PROGRESS.md (generation 10) between my edits, and a `git add HANDOFF.md && git commit` then
  recorded THAT rewrite under a message describing prose I had not actually written - my python step
  had aborted on an assertion. Message corrected by amend (local, unpushed). Tell: `git show --stat`
  reports managed-block-sized deltas in the wrong files. Rule: after any guard-triggered write,
  re-read `git status` and `git show --stat` before composing the message. [accepted, measured 2026-10-29]

## Accepted (E2E-48/P2c close + P2d pre-registration, measured 2026-10-30, renewal 8/8 successor)

- **A refusal reason that says "no golden exists" is a SEARCHABLE claim, and two of them were
  false.** The P2c §3 list (inherited through three renewals) said `TITLE(<static varying>)` and
  the EMPTY `initial('')` static cell were unmeasured. They are not: `golden/e42p1c/E46F5/E46F5.REL`
  is DR's own accepted object for exactly the static-varying TITLE (CODE 68 / DATA 18, `?SLVTS` at
  0006, option word `0E50`, cell `02 41 42 20 x11` in place, `.PRN` prints NO ERRORS), and
  `golden/first8080u/EXPR2/EXPR2.REL` DATA **000F = 00 then ten 20 bytes** is the empty-varying
  cell. Neither was ever looked for. RULE: before writing `unmeasured`, run the search —
  `find golden -name '<program>.REL'` then `tools/reldump.py | grep "DATA  *data"`. A refusal
  copied forward by summaries accumulates authority it never earned (the same failure class as the
  `dad d` mnemonic). Classification: the two §3 claims **falsified**; the objects stand.
  [accepted, measured 2026-10-30]
- **Retiring a negative row is a THREE-place edit, and only the audit sees the third.** A row lives
  in `REJECTS`, in `NEG_META`, and (by path) in `SPECIMENS`. Removing it from `REJECTS` but leaving
  its `NEG_META` stamp makes `registration_audit`'s symmetry rule abort the FULL gate — and
  `--update-inventory` **returns before that audit**, so the promotion commit looks green while the
  gate is doomed. The predecessor's sweeps (per-probe `cmp`) could never find it either. Tell:
  `len(NEG_META) != len(REJECTS)`. Cheap pre-flight that costs no compile:
  `python3 -c` importing `tools/e2e_gate.py` and calling `registration_audit` directly. Fix at
  `f67cc6d` keeping the superseded prose verbatim in a comment. [accepted, measured 2026-10-30]
- **`coverage_check` validates citations, never prose currency, so stale blocker NAMES are the real
  rot in `spec/COVERAGE.tsv`.** Four rows still named refusals the binary no longer emits
  (LOAN2's line-39 `STATIC on CHAR(14) VARYING is unsampled`, CREATE's line-41 SKIP control item,
  `STATIC on CHAR(27)`/`CHAR(15)`, and DECL.STATIC_INITIAL's `STATIC on character types has no
  sample at all`). The gate stayed green through all of it. Method I used: diff each named blocker
  against the **census `msg` column** (the only machine-maintained source for "what does my
  compiler refuse today"), then APPEND a dated correction and keep the original sentence word-for-word
  — `git diff` proves the append (`original-preserved: True` for all four). [accepted, measured
  2026-10-30 at `ef0a198`]
- **`--update-inventory`'s success line counts SPECIMENS, not inventory rows**
  ("inventory rewritten (1109 entries)" while the file holds 1291 rows = 1109 specimens + 182
  refusals): the message reports `rows_of(SPECIMENS)` because `inventory_check(write=True)` returns
  `[]`. Read the file, not the line. [accepted, measured 2026-10-30]
- **The renewal successor's shell is NOT the operator's login shell.** `dune` is absent
  (`command introuvable`) until `eval $(opam env)` (switch `default`, ocaml 5.4.0, dune at
  `/home/john/.opam/default/bin/dune`), and the renewal banner's "verify the build: `node --test
  test/`" is a generic template line — this repository has no `test/`; its build verification is
  `dune build` plus the sweeps/gate. Do not invent a Node test suite to satisfy a template. Also:
  a `dune build` that prints nothing may be CACHED, so an "0 warnings" claim from it proves
  nothing — compare clean-rebuild warning multisets as `LEARNINGS` already requires. [accepted,
  measured 2026-10-30]
- **Proposed (unverified): LOAN2's `conflicting kinds` refusal is a DESIGN gap, not an arm.**
  `codegen.ml:12460-12490` builds ONE global `pd_vars` name -> vkind map for the DEC-pool prescan
  and refuses when a name appears with two kinds; LOAN2 legally declares `i` `fixed decimal(4,2)`
  in `main` (line 32) and `fixed bin` in the internal procedure `line` (line 211), and DR's object
  exists. Every one of the ~15 consumers is `List.assoc_opt name cx.pd_vars` and the prescan runs
  deliberately WITHOUT statement context (`codegen.ml:3009` says so), so scope-keying it is a
  refactor with pool-layout consequences. Classified `my-gap`, cause measured; **not started**,
  must not be attempted on faith. [proposed, unverified]

## Falsified or superseded

- **"File mtimes prove pre-registration"** — superseded by the committed-blob rule above (P2a).
- **"55 specimens are registered hangs"** (the original P2c category) — superseded by
  `GATE-TIERS.md` §11 / [C308]: 51 timeouts, 2 emulator deaths, 2 normal terminations. The table
  is kept as written, labelled superseded, not deleted.
- **"The final wording-only tree was link-run end to end by hand"** — not claimed: that run was
  stopped before its verdict; the `rune-full` builder owns that arm
  (`spec/notes/e2e41-p3-stream-output-put-file.md`).
- **`spec/CLAIMS.md`'s own `[C296]`–`[C303]` texts carried stale DR facts** found by re-reading
  the artifacts — an ongoing reminder that even the ledger needs re-measurement, and that a
  handoff summary never outranks it.
- **"DR rejects `DECLARE x POINTER;` without BASED"** — recorded in `spec/PERIMETER.md` as [M],
  and explicitly **not reproduced** on DR v1.4 (E2E-26/P1: PD2–PD5 all compile clean with a `.REL`,
  `spec/notes/e2e26-p1-pointer-based-address-model.md`, annotated in `spec/PERIMETER.md`): the
  trigger was narrower than the row implied. Kept here as the standing example of *do not turn an
  unreproduced observation into a rule*.

## 2026-10-29 — renewal e2e test: successor-session observations (session 01a188a6, renewal 1/8)

- **Accepted (measured):** Automatic renewal worked end-to-end. Parent session
  `01a188a5-…f85d5` attested checkpoint `g2-470d507dbf6c`, called `handoff_renew` once, and the
  successor started fresh with **no transcript replay**; its recovery prompt carried the correct
  durable identity (parent id, chain id, attested checkpoint id).
- **Accepted (measured):** The renewal counter is durable: `.pi-guard/renewal-state.json` shows
  `renewalsDone: 1`, `renewedFromCheckpointId: g2-470d507dbf6c`,
  `lastSuccessorSessionId: 01a188a6-36ee-708a-affc-0a4c9333a1c9`, `stopped: false`, on chain
  `chain:01a188a5-…`.
- **Accepted (measured):** Successor recovery from files alone worked — it identified and executed
  the INFRA TEST WINDOW next action recovered solely from the durable files (highest claim in
  `spec/CLAIMS.md`: **C308**; no scientific file touched).
- **Accepted (measured):** The successor hit guard level 3 **immediately at session start** (three
  thresholds crossed in one step, reported remaining ~9 000 of a declared 220 000 window); the
  guard wrote an automatic, unattested checkpoint `g3-0c5843a47674` (`kind: auto`,
  `content-delta: none`) into both managed files, preserving the prior substantive notes — the
  auto-checkpoint preservation behaviour works on renewals too.
- **Accepted (measured, closure session):** The successor's ~9 000-remaining start reading was
  **fully explained by the test harness itself**: the child process was launched with
  `CONTEXT_GUARD_SYNTHETIC_REMAINING=9000` (the deliberate controlled threshold), that env
  override is re-applied by `loadConfig` at every session_start inside the process, and
  `.pi-guard/sessions/<successor>.json` records `lastRemaining: 9000` exactly — the synthetic
  figure, not a usage estimate. Not a defect, not an accounting artifact. Lesson: when a renewal
  successor reports suspicious pressure, first check whether the launch environment still carries
  a synthetic override before investigating Pi's accounting.
- **Accepted (decision, per protocol):** The successor did **not** renew again — the authorized
  procedure says the successor reports and stops; re-renewing while start-pressure looked
  unexplained risked burning the chain cap (8) in a renewal loop. (The pressure was later
  explained as the harness's synthetic override — the no-re-renew decision stands on the
  procedure alone.) Test-window closure (restore the real next
  action from pre-test commit `a6eec67`, `/handoff` refresh, `/handoff ready`) remains an operator/
  next-session step.

## Closing (E2E-48/P2c step 6, renewal 7/8 successor, measured 2026-10-30)

- **Accepted:** a census delta after a widening is READ, not just counted: LOAN2 ADVANCED
  past the retired line-39 refusal into a NEW, previously shadowed prescan my-gap
  (`variable i declared with conflicting kinds`). It is recorded for a FUTURE
  pre-registered round, never lowered on faith. EXPR2/FSCAN deltas were the expected
  EMPTY-`initial('')` named refusals. [measured at b78770d, snapshot `014a736`]
- **Accepted:** census `--check` rewrites the snapshot AND count-guards in one call; the
  prev-copy discipline caught nothing here because counts genuinely held (15/0/26/0).
- **State owed by the successor (unverified, do not claim):** `--update-inventory` and the
  FULL gate have NOT been run since the arms; expected 1109 byte-exact / 0 fail,
  negative 182/182 (the inherited 1107/184 is falsified by the K1/K3 promotions).

## E2E-48/P2d round (session 01a18cf9, 2026-10-30, through checkpoint g21+)
- **accepted** DR truncates source lines past col 72; a >72-col comment loses its `*/` -> whole-file
  `UNEXPECTED EOF`, no .REL. Run 1 (tag e48p2d, kept at 67bf83c) died exactly this way, 0/10.
  Procedure law: every probe line <=71 cols; verify with awk BEFORE any oracle call.
- **accepted** e42p2b rewritten-probe rule worked again: wrap fix (code lines cmp-identical) + NEW
  tag e48p2db + HYPOTHESES.md dated amendment; run 2 = 10 ok/10. Old artifacts stay committed.
- **accepted** 8 new laws in spec/lab-evidence/e2e48-p2d/RESULTS.md s2: static-fixed store =
  ?SMCCM(A=extent,B=len, literal pooled); static-varying store = ?SMCVM; empty initial('') cells
  (varying 00+blanks, fixed all-blanks, both IN PLACE); TITLE static-operand class-invariant
  (w0E50/w0E90); store ladder |c|2,3 = DCX H x|c| (threshold route-independent, [C310] TBD closed);
  non-final BIT(1) PUT item ACCEPTED (own ?PNBOP, one final ?QIOOP); DATA slack = automatics above
  pool (LINK-SET-LC holes, not padding); member-as-RIGHT TEST keeps ?SCCVM orientation.
- **falsified** P-D7's "DATA image rewrites the leading length byte" -- the image keeps the INITIAL;
  rewrite would be runtime ([TBD]). And my refusal premise "non-final bit item has no witness" --
  D9 is the witness. Three earlier "no golden exists" claims were already falsified at prereg.
