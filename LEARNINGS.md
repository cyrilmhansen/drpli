# LEARNINGS.md — DRPLi

Ledger of **working methods and environment knowledge**, including handoff-infrastructure
lessons. It is **not** the evidence ledger: anything about compiler behaviour belongs in
`spec/CLAIMS.md` with its specimen and golden paths, and is referenced here, never copied.
The guard never writes this file.

## Accepted

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
  regardless of the file (`config.ts`). DRPLi policy is renewal OFF, so every DRPLi Pi launch must
  set `CONTEXT_GUARD_AUTO_RENEW=0` explicitly (it is also honoured as `0` = force-off) and
  `/guard status` must be read back to confirm `renewal: policy enabled=false autoRenew=false`.
  Measured 2026-10-29: the first Phase D run reported `enabled=true autoRenew=true` until the
  kill switch was set.
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
- **Proposed [TBD]:** Why the successor's *fresh* context measured ~211k used at once. Candidates:
  (a) the STQ model's API usage figures over-report prompt tokens for this harness's system+renewal
  prompt, (b) an accounting artifact carrying parent usage across the switch. Measure: log the raw
  per-turn usage fields in `.pi-guard/sessions/<successor>.json` and compare against a tokenizer
  count of the successor's first prompt. Until measured, treat successor-start pressure as
  unexplained — this is `unmeasured`, not a defect claim.
- **Accepted (decision, per protocol):** The successor did **not** renew again — the authorized
  procedure says the successor reports and stops; re-renewing while start-pressure is unexplained
  risked burning the chain cap (8) in a renewal loop. Test-window closure (restore the real next
  action from pre-test commit `a6eec67`, `/handoff` refresh, `/handoff ready`) remains an operator/
  next-session step.
