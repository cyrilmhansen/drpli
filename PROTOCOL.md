# PROTOCOL.md — DRPLi scientific operating protocol

Two things live here: (1) how evidence is made, (2) how a session hands off. Neither
changes what the compiler is supposed to do — that is `GOAL.md` plus the ledger.

## Part 1 — Scientific method

1. **Formulate the hypothesis before the oracle runs.** Write the predictions as a committed
   artifact (probe bank + expected verdict) *before* invoking DR. Committed blobs, not file
   mtimes, are what prove ordering — see the preamble of
   `spec/lab-evidence/e2e42-p2c/RESULTS.md` and the P2a lesson in
   `spec/lab-evidence/e2e42-p2a/PROCESS.md` (a `git stash -u` destroyed the mtimes that an
   earlier ordering claim rested on; commit `c816af5` records the correction).
2. **Keep falsified predictions and negative evidence.** A MISS stays in the report; it is
   not edited out, and superseded text is kept as written and labelled superseded rather than
   deleted.
3. **Classify every difference** as exactly one of
   `dr-refuses` (DR itself rejects the input — evidence in DR's own listing/object),
   `my-gap` (DR accepts, mine does not — this is a defect, not a rule),
   `unmeasured` (no oracle result exists yet). A refusal reason recorded in
   `spec/INVENTORY.txt` must name which of these it is.
4. **Never turn missing evidence into a claimed DR rule.** "No golden exists" is not
   evidence that DR rejects the form. Absence of a witness is `unmeasured`.
5. **Use `[TBD]`** where the exact detail has not been measured, and say what would measure it.
6. **Compare complete `.REL` files byte-for-byte.** Segment sizes are read out of the objects
   themselves (e.g. via `spec/lab-evidence/e2e42-p2b/chaindump.py`), never out of a `.PRN`
   listing — a `.PRN` prints `CODE SIZE = 0056`, which is hex, and treating a rendering as the
   authority is a recurring error class ([C264]).
7. **`spec/CLAIMS.md` is the authoritative evidence ledger.** New measured behaviour is
   written there with its specimen paths. The handoff documents point at claims; they never
   restate them as independent authority.
8. **Preserve the tiered gates and oracle infrastructure.** `tools/e2e_gate.py` (compile tier),
   `--runtime`, `--link-run`, and the external `rune-ci` builders that own the slow CP/M tiers
   (`spec/notes/rune-ci-external-gate.md`, `spec/lab-evidence/e2e42-p2c/GATE-TIERS.md`) are not
   to be weakened, bypassed or reinterpreted. A gate that cannot fail is not a gate.
9. **Never manipulate ignored or generated data as disposable.** `golden/`, `oracle/disks/`,
   `build/`, `thirdparty/`, `artefacts/` are evidence and inputs. Do not delete, regenerate,
   reorder or "tidy" them; do not run `git clean`/`reset --hard`/recursive cleanup.
10. **Audit actual commits and test output, not agent summaries.** Check `git log`, the
    committed blob, and the report file a verdict is claimed to come from. Numbers in prose are
    re-derived from the artifact that produced them; a "measured" reason string is only as good
    as the distinction its producer actually makes (the P2c `timeout-or-hang` lesson).

Additional standing rule: **an old milestone's status text is not current truth.**
`README.md` "Current status (rolling)" and notes in `spec/notes/` lag the ledger; when they
disagree with `spec/CLAIMS.md` or a gate report, the ledger/report wins and the stale text is
either corrected or explicitly marked stale.

## Part 2 — The Handoff workflow

Infrastructure. It exists so a fresh session can recover **from files alone**, with no
transcript replay.

### Files

| File | Who writes it |
|---|---|
| `AGENTS.md`, `PROTOCOL.md`, `GOAL.md`, `LEARNINGS.md` | agents / operator only. The guard never writes them; `GOAL.md` is additionally write-protected (`protectGoal: true`). |
| `HANDOFF.md`, `PROGRESS.md` | agents write the manual prose sections; the guard writes **only** the managed block delimited by `<!-- guard:begin checkpoint -->` … `<!-- guard:end checkpoint -->` |
| `.pi-guard/` | guard runtime state (per-session JSON, ignored by Git). Nothing else in the tree is written by the guard. |

Manual prose **always wins** over the managed block. The managed block carries machine
identity (`checkpoint-schema: 3`, generation, `checkpoint-id`, readiness, content delta,
source hashes) — never hand-write, hand-edit or copy one; regenerate it with `/handoff`.

### Load

The project is trusted by the production profile, so a plain `pi` launched from the project
root auto-discovers `context-guard`, the `.agents/skills/pi-handoff` skill and the project
`.pi/settings.json` (which disables automatic compaction for **this project only**).
Do **not** also load the extension with `-e`.

```bash
cd /home/john/projects/sushiworks/pli80
env -u CONTEXT_GUARD_AUTO_RENEW PI_CODING_AGENT_DIR=/home/john/.sushi/pi pi
```

`CONTEXT_GUARD_AUTO_RENEW=1` is exported in the operator's interactive environment and would
otherwise mask `handoff.config.json`; controlled launches strip it (no other `CONTEXT_GUARD_*`
override is set: `CONTEXT_GUARD_DISABLED`, `_ENFORCE`, `_READONLY`, `_STATE_DIR`,
`_SYNTHETIC_REMAINING` are unset unless a specific test requires them). Read-only audit
sessions additionally set `CONTEXT_GUARD_READONLY=1` (and may redirect
`CONTEXT_GUARD_STATE_DIR` outside the tree). Instructing a model "don't edit" is not
read-only; that env var is.

### Start of session — DRPLi lean recovery

The project is trusted, so Pi loads `AGENTS.md` as project context. With
`recovery.lean: true`, first read `HANDOFF.md` and `PROGRESS.md`, verify the
current Git HEAD and a clean working tree, then run `/handoff verify`. Consult
`PROTOCOL.md` before any unclear scientific/procedural action; consult
`GOAL.md` and `LEARNINGS.md` selectively by evidence pointer. All six
documents remain authoritative; defer reading rather than discarding their
contents. Consult `spec/CLAIMS.md` SELECTIVELY — read only the cited claim ids
(`grep -n '^## C<NNN>' spec/CLAIMS.md`; the ledgers exceed the working window and a
bulk read is prohibited for recovery) — and the exact current `spec/lab-evidence/` report
for the next scientific experiment. A stale/missing checkpoint is not authoritative:
re-derive from commits/evidence, then refresh + attest with `/handoff finalize`.
Do not begin the oracle in the middle of a handoff/maintenance operation.

### During work

Compiler work first. Preserve all original inputs and evidence. Pre-register hypotheses,
record measured results, and update the existing scientific ledgers (`spec/CLAIMS.md`,
`spec/INVENTORY.txt`, `spec/COVERAGE.tsv`, `spec/RUNTIME.txt`, `spec/DIVERGENT.txt`, the
`spec/lab-evidence/<phase>/` report). Update `PROGRESS.md` when meaningful progress occurs;
put durable *working-method or environment* lessons in `LEARNINGS.md` (not compiler behaviour —
that goes in the claims ledger). No transcript dumps, no duplicated descriptions: link to the
canonical file. Handoff must not change compiler implementation strategy.

### Context pressure — config-driven working policy (Handoff dev.3; consolidated 2026-10-31)

Pi/Sushi may declare a PHYSICAL context window larger than the project's OPERATIONAL
ceiling. Handoff uses `workingContextWindow` from `handoff.config.json` as that ceiling
and NEVER changes Pi/Sushi's physical context window. The Pi output margin is computed
against the physical window; the reserves that matter here are
`generationReserve`/`safetyReserve` in the config. **This document deliberately quotes
no numbers:** `handoff.config.json` and `/guard status` are authoritative for the working
window, the physical window, the reserves and the threshold distances; re-read them at
session start. The guard's estimate remains advisory and is NOT an exact token count.

Alert levels are distances from usable remaining
(usable = working window − estimated used − max(generationReserve, safetyReserve));
the crossing points are computed from the config (check `/guard status`):

- Level 1 (advisory/checkpoint): record scientific results, evidence and exact next action.
- Level 2 (wrap-up): complete bounded work, do not start new substantial work.
- Level 3 (handoff): prioritize durable work, commit explicit paths and request
  `handoff_renew` at the next safe boundary when the objective remains unfinished
  and renewal is permitted or safely preparable.
- Level 4 (closing): prioritize the SAME continuation procedure; do not treat a stale
  checkpoint created by a legitimate prose edit as an irreversible refusal.
  `handoff_renew` can refresh and attest before switching. If renewal is genuinely
  unavailable, use `handoff_finalize` and stop cleanly.

Closing enforcement and renewal enablement are config values: `enforceClosing`,
`renewal.enabled`, `renewal.autoRenew`, `renewal.maxRenewals` — read the file; as decided
on 2026-10-29, renewal is enabled with a bounded cap and project compaction remains
disabled via `.pi/settings.json`. The durable renewal counter and scientific checkpoints
are NOT reset by documentation work. Always inspect `/guard status` to verify the actual
physical and working windows. A threshold alert alone does NOT trigger a session switch.

Renewal discipline:

- `autoRenew: true` only makes `handoff_renew` callable by the model; **it never forces a
  switch at a threshold**. The level-3 rule above — write the durable state, then renew — is
  what actually carries a session across.
- **Never renew mid-oracle-experiment, mid-file-edit, or during an incomplete Git operation.**
  Finish or explicitly suspend the operation at a safe boundary first.
- **Never claim a gate passed unless its actual result was verified.**
- The successor starts fresh (durable files only, no transcript replay). Before continuing it
  must check Git HEAD, checkpoint freshness (`/handoff verify`), unfinished operations, the
  relevant `spec/CLAIMS.md` claims and the exact next action, and must preserve this
  scientific methodology and proceed with the same development objective.
- If renewal is **refused or fails**, the guard names the reason; report it and preserve the
  recovery state, use `handoff_finalize` at a safe boundary, and conclude.
  Never silently fall back to compaction.
- The renewal counter is **durable** (the renewal-state file under the configured
  `stateDir`; closed chains are archived under `stateDir/archives/`): it survives session
  replacement and process restarts and is shared by everything using this stateDir; a new
  independent session continues the same chain's count. At the cap, renewal refuses with
  `capped`. Manage the budget explicitly: raise `renewal.maxRenewals` by operator decision,
  or reset the state file only as a deliberate, recorded operator action. `/handoff renew
  stop` durably stops the chain (survives replacement and restart); `/handoff renew resume`
  clears it; `/handoff renew status` shows the chain.

### End of a substantial session

1. Finish or explicitly suspend the current operation (say which, and where it stands).
2. Update `PROGRESS.md` prose (phase, completed, pending, verified evidence, blockers, next action).
3. Update `HANDOFF.md` prose with the **actual verified state** and the **exact next action**
   (command + expected output) — a task you cannot establish reliably is written as unestablished,
   never invented.
4. Update `LEARNINGS.md` only for durable lessons.
5. Record Git HEAD, relevant commits and the gate/evidence reports you actually read or ran.
6. **Commit the prose** (explicit paths only — never `git add -A`). If the objective
   remains unfinished and model renewal is enabled, request `handoff_renew` at a
   safe boundary: it refreshes and attests even a legitimately stale checkpoint,
   checks the real gate and switches to a fresh session. Do not substitute terminal
   `handoff_finalize` for an available continuation.
7. When renewal is disabled, stopped, capped or refused after preparation, run
   `/handoff finalize`, verify with `/handoff verify` and stop cleanly. If the
   checkpoint refresh dirties the tree, commit only its explicit managed-block paths.
8. `git diff` the result: confirm no scientific file changed unexpectedly.

A committed checkpoint must agree with its own manually authored recovery prose. **Never claim a
gate passed unless it actually ran, or the statement is explicitly attributed to an earlier
recorded result.**
