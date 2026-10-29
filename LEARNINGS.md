# LEARNINGS.md — DRPLi

Ledger of **working methods and environment knowledge**, including handoff-infrastructure
lessons. It is **not** the evidence ledger: anything about compiler behaviour belongs in
`spec/CLAIMS.md` with its specimen and golden paths, and is referenced here, never copied.
The guard never writes this file.

## Accepted

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

## Proposed

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
