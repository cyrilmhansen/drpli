# rune-ci: the gate, run off the critical path by a local Buildbot

Tooling note.  The service lives in `/home/john/services/rune-ci` (its own
`README.md` has the full contract); this note records what the **repository**
needs to know, because two of its conventions — the standard gate command and what
a green build means — are now enforced somewhere other than here.

## Why

`python3 -u tools/e2e_gate.py --runtime` takes ~7 minutes, and most of it is the
52-row runtime panel driving CP/M under `cpmsim`.  An agent editing codegen pays
that on every check, so long runs get skipped, and a skipped gate is a gate that
does not exist.  The gate now also runs *outside* this working tree, on a Buildbot
master bound to 127.0.0.1, driven by `bin/rune-ci`, which returns in ~0.15s and
lets the agent poll or go do something else.

## What the audit found (the v1 configuration)

`master/master.cfg.before-runecli-20261027-014210` is kept as evidence.  The v1
master had two builders (`rune-smoke`, `rune-full`), `max_builds=1`, both ports on
`127.0.0.1`, and the password read from `secrets/web-password` — those were already
right.  What was wrong or missing:

1. **Nothing pinned the revision.** Both `ForceScheduler`s were declared with no
   parameters, and both `steps.Git` hard-coded `branch="main"`, so a forced build
   checked out whatever `main` pointed at *when the worker got to it*.  The full
   factory printed `git rev-parse HEAD` in a step called `git-revision` and compared
   it to nothing.  A build could therefore report a verdict for a commit that was
   not the one asked for, and nothing in the record would say so.
2. **The emulator and the boot disks were not pinned.** The gate resolved `cpmsim`
   from `$CPMSIM` or a list of home-directory fallbacks (`oracle/run.py:19`), and the
   runtime panel ran on `oracle/disks/drivea|driveb.dsk` as they happened to sit in the
   checkout.  (The harness itself is safe — `oracle/cpmwork.py` copies the seeds into a
   per-run zone and never mounts the repository's copies, see
   [oracle-safety.md](oracle-safety.md) — that was never the problem.)  The problem is
   identity: which emulator binary and which disk bytes a verdict depended on was decided
   by the developer's environment, recorded nowhere, and so a green on one host said
   nothing about a green on another.
3. **The gate runner was a 60-line string inside `master.cfg`**, untestable, recording
   only `wall_seconds`.  No panel counts, no phase breakdown, no failed-test names, and
   no way to tell "the harness broke" from "a test failed": a preflight problem and a
   genuine runtime failure both looked like `status: "failed"`.
4. **No client.** Forcing a run meant the web form and a hand-typed 40-character SHA;
   there was no way to ask a question of a finished run except by opening the console
   view and reading a raw log.

## What the service guarantees now

* **Two suites** ([E2E-42/P2c]), and the long arm is no longer anybody's laptop problem.
  `rune_ci_common.gate_argv(suite)` is the single source:

  | suite | command | what it is |
  |---|---|---|
  | `full` (default) | `--runtime -j 8` | the strict gate: byte panel, negatives, divergences, coverage, census, prose, and the 71-row runtime panel. ~2 min on a pool (was ~10 min serial). This is what a commit gets. |
  | `audit` | `--runtime --link-run -j 8` | the strict gate PLUS the 817-arm DR-vs-mine link+run arm. ~10-20 min on a pool (was ~90 min serial). A scheduled audit, not a per-commit gate. |
  | `smoke` | none | wiring only; runs no compiler panel and says so. |

  The import-time assertion still holds, but per-suite: `--link-run` may never appear in
  `GATE_ARGV` — it arrives only through `AUDIT_ARGV`, via `--suite audit`.  A mistyped
  suite name resolves to the STRICT command, never to the audit.  `CI_VERSION` went
  3 → 4 with this, which is what invalidates the cached greens recorded under the serial
  command.

  Why the audit needed a suite at all: `--link-run` used to be "an explicit, exceptional
  audit that no CI run starts", which in practice meant it was run by an agent maybe once
  per milestone, at ~90 minutes of wall clock, or — more often — not at all.  An arm that
  nobody runs is not a gate.  It is now CI's job, on a pinned revision and a pinned
  emulator.

* **`--link-run` can fail, which it could not before.**  `link_arm` printed `.COM
  DIFFERS! vs DR`, `CONSOLE DIFFERS` and `MISSING TRANSCRIPT` and returned nothing; the
  gate's exit status came only from the byte panel.  Delegating that arm to CI would have
  delegated a rubber stamp.  It now returns verdicts, plus two the old code could not see
  (a nonzero link step, and no `.COM` at all — the latter used to read as "mine-only arm,
  captured 0 raw output bytes", a pass).  Checked against the last full serial run: 0
  DIFFERS, 0 CONSOLE DIFFERS, 0 MISSING, so no verdict that exists today changes.  What
  changed is that 23 arms that had been silently proving nothing are now classified: 17
  in `HANG_ARMS` (their transcripts end at their own command echo — they wait for input
  the harness never sends) and 2 in `NO_LINK_ARMS` (10- and 12-character specimen names
  that CP/M's 8.3 limit refuses).  Four more, `E29F/E29G/E29I/E29J`, were not a name
  problem at all but a **missing companion module** — `link()` reads `SAME_TAG_OBJS`
  companions at `golden/<tag>/<COMPANION>/<COMPANION>.REL` and nothing staged them, so
  they linked with an unresolved reference; `link_arm` now compiles and stages `A`/`B`,
  and those four execute for the first time (126, 45, 141 and 45 bytes of real output).
* The revision is pinned three times over: the force payload carries `revision` and
  `requested_sha` as **top-level** fields (a nested `"properties"` dict is silently
  ignored by `control.force()`), `ci/verify_revision.py` fails the build if
  `git rev-parse HEAD` does not match, and `ci/gate_runner.py` measures HEAD before
  and after the gate and refuses to emit a verdict unless both agree.
* The emulator and both boot disks are pinned by SHA-256 in `fixtures/SHA256SUMS`,
  staged into the build's own `oracle/disks/` and re-verified there, with
  `CPMSIM` exported to the fixture binary.  The pinned bytes are this repository's own
  (`thirdparty/z80pack/cpmsim/cpmsim`, `oracle/disks/drive[ab].dsk`), so a CI run and a
  local run execute the same CP/M — the pin is a guarantee, not a different system.  A build cannot reach the repository's
  seeds, and cannot test against an arbitrary host emulator.
* A job is identified by `(SHA, suite, CI fingerprint, fixture fingerprint)`, and an
  idempotency hit is honoured only if the *build* recorded the fingerprint being
  asked about.  Re-pinning an emulator invalidates cached greens, because a green
  under an old emulator is not evidence about a new one.
* **Infra is not a verdict.** The preflight and the wrapper exit **125** for harness
  faults; the gate's 1/2 still mean a test failed.  `rune-ci` drops all panel counts on
  an `infra_error`, so a broken harness can never read as "990 byte-exact" plus a
  footnote.
* `rune-smoke` proves checkout, revision pin and step wiring.  It runs **no compiler
  panel**, and its report says so on the line where a misreading would happen.  Only
  `rune-full` says anything about the compiler.

## Timings, and one number that looks wrong

`ci/gate_runner.py` writes `build/ci/timing.json` (attached as a Buildbot log, so it
is readable from any host that can reach the master) with per-step seconds, the gate
phases, the panel counts (a fifth, `link_run`, exists on the audit suite), the census,
and every runtime row with its seconds.  The runtime panel is the cost — ~588s serial
of a ~595s build, now ~77s on a pool — which is the argument for keeping it off the
editing path.

**Per-row seconds are self-reported since [E2E-42/P2c].**  They used to be derived from
the gap between consecutive timed output lines, which is a fair estimate while rows run
one after another and is meaningless on a pool: with `-j 8` a row's "duration" became
"how long until something else happened to finish".  `runtime_row` now times itself and
prints `[12.3s]`, the wrapper parses that and marks the row
`seconds_self_reported: true`, and only falls back to the gap when a line carries no
suffix — so old logs still parse.  The runner also records `gate_jobs`, because a
timing comparison between a `-j 1` and a `-j 8` build is not a comparison.

`slowest` is reported over **timed output lines**, while `counts.runtime` counts
**panel rows**.  E16D and E17D each print two timed lines — `FILE OK` for the emitted
disk file and `OK WROTE` for the write — but are one panel row each, so a clean run
reports `runtime 52/52` and 54 timed lines.  The client prints both, labelled; the
discrepancy is the two-file-each specimens, not a lost row.

The `link+run` panel runs **between** the byte panel and the negative panel, so it has
its own phase bound and the negative panel's span starts where it ended — otherwise the
audit reports ~10 minutes of emulator time as if the negative panel had spent it.

## Using it from here

```sh
# the gate a commit gets, ~2 min
/home/john/services/rune-ci/bin/rune-ci submit "$(git rev-parse HEAD)" --suite full
# the long DR-vs-mine audit, delegated: ~800 arms, ~10-20 min, off your critical path
/home/john/services/rune-ci/bin/rune-ci submit "$(git rev-parse HEAD)" --suite audit
/home/john/services/rune-ci/bin/rune-ci status bs12       # non-blocking, any time
/home/john/services/rune-ci/bin/rune-ci failures bs12     # names, or the infra reason
/home/john/services/rune-ci/bin/rune-ci latest            # newest job + recent list
```

**Local tiers, and what not to run by hand.**  Measured on this host (24 cores):

| command | serial | `-j 8` | belongs to |
|---|---|---|---|
| `tools/e2e_gate.py` | 2.3 s | — | every edit; it is the fast tier and needs no emulator |
| `tools/e2e_gate.py --runtime -j 8` | 588 s | 77 s | CI (`--suite full`); run locally only when you changed the panel itself |
| `tools/e2e_gate.py --link-run --runtime -j 12` | ~90 min | ~10 min | CI (`--suite audit`); never on the editing path |

The serial numbers are the reason this note existed at all: a 10-minute or 90-minute
check gets skipped, and a skipped gate is a gate that does not exist.

`status` exits 0 whether the build passed or failed (the CI did its job); non-zero
means the *question* could not be answered: 2 usage, 3 master unreachable, 4 auth,
5 malformed API response.  `rune-ci-ctl check` verifies the whole installation —
`checkconfig`, the CI unit tests, the fixture manifest, the host preflight, the
builder/scheduler/worker wiring — in a few seconds, and is the thing to run before
believing a green.

Validated on this host against commit `3741cee` (E2E-41/P3c): 990/990 byte-exact,
133/133 refusals, 9/9 divergences, 52/52 runtime rows, 436s, revision verified,
submit returning in 0.18s, and a re-submit of the same tuple reused the running job.

## What a report is allowed to say

Three non-green outcomes, because three different things went wrong:

| status | meaning | test counts |
|---|---|---|
| `failed` | the gate ran and a panel said no | kept, and the failing tests are named |
| `build_failed` | the tree did not compile (`dune-build`/`checkout` died) | none — no test ran |
| `infra_error` | the harness is wrong (preflight, revision pin, fixtures, wrapper) | dropped, deliberately |

Two counting rules that came out of running the thing:

* A panel banner often gives only two of the three numbers (`RUNTIME PANEL 1 fail of
  52`, `NEGATIVE PANEL 1 fail`).  `passed` is completed at the end of the run from the
  rows the gate actually printed, never guessed: a panel that started and died mid-way
  is reported as `incomplete (n rows printed)` rather than `52/52`.
* `tools/e2e_gate.py` returns at its **first** failing panel, so the panels after it
  print no verdict.  That is a test failure with a short transcript, not a broken
  harness: the wrapper records `panels_not_reached` and the client says *"the gate stops
  at its first failing panel: no verdict from divergences, runtime"*.  A silent panel is
  `infra_error` only when nothing failed, or when the gate exited 0 with panels missing —
  and then the gate's own last line is quoted, since it is the actionable part (e.g.
  *"run --update-inventory and commit the diff"*).

Probe builds on throwaway branches (both deleted; `main` never saw them) established all
of this against a real master: a perturbed runtime expectation fails one named row
(`bs16`), an inventory/`REJECTS` disagreement aborts the gate entirely (`bs18`, `bs19`),
and a legalised negative fails the negative panel and stops the run before the divergence
and runtime panels (`bs20`, `bs21`, six seconds).  A specimen-source edit that only adds
output no expectation forbids stays green (`bs17`) — the byte panel compiles the source
registered in `SPECIMENS`, and a runtime row is a subset check, not a transcript
comparison, so a probe has to perturb an *expectation* to fail anything.  Side branches
work without touching the master config: Buildbot uses the sourcestamp branch in
preference to the step's, so `--branch` is what the worker fetches.
