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

* `GATE_ARGV = ["python3", "-u", "tools/e2e_gate.py", "--runtime"]` — the standard
  command, asserted at import time not to contain `--link-run`.  **The repository's
  gate is unchanged by this work**: same command, same panels, same expectations, and
  the CI runs the strict panel only.  `--link-run` remains an explicit, exceptional
  audit that no CI run starts.
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
is readable from any host that can reach the master) with per-step seconds, the six
gate phases, the four panel counts, the census, and every runtime row with its
seconds.  The runtime panel of a clean run is ~430s of a ~436s build: the panel is the
cost, everything else is noise, which is the argument for keeping the gate off the
editing path.

`slowest` is reported over **timed output lines**, while `counts.runtime` counts
**panel rows**.  E16D and E17D each print two timed lines — `FILE OK` for the emitted
disk file and `OK WROTE` for the write — but are one panel row each, so a clean run
reports `runtime 52/52` and 54 timed lines.  The client prints both, labelled; the
discrepancy is the two-file-each specimens, not a lost row.

## Using it from here

```sh
/home/john/services/rune-ci/bin/rune-ci submit "$(git rev-parse HEAD)" --suite full
/home/john/services/rune-ci/bin/rune-ci status bs12       # non-blocking, any time
/home/john/services/rune-ci/bin/rune-ci failures bs12     # names, or the infra reason
/home/john/services/rune-ci/bin/rune-ci latest            # newest job + recent list
```

`status` exits 0 whether the build passed or failed (the CI did its job); non-zero
means the *question* could not be answered: 2 usage, 3 master unreachable, 4 auth,
5 malformed API response.  `rune-ci-ctl check` verifies the whole installation —
`checkconfig`, the CI unit tests, the fixture manifest, the host preflight, the
builder/scheduler/worker wiring — in a few seconds, and is the thing to run before
believing a green.

Validated on this host against commit `3741cee` (E2E-41/P3c): 990/990 byte-exact,
133/133 refusals, 9/9 divergences, 52/52 runtime rows, 436s, revision verified,
submit returning in 0.18s, and a re-submit of the same tuple reused the running job.
