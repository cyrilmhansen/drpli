# E2E-42/P2c — gate tiers, and what the `--link-run` arm never proved

This file is the evidence behind `HANG_ARMS` and `NO_LINK_ARMS` in `tools/e2e_gate.py`,
and behind the timing numbers quoted in `spec/notes/rune-ci-external-gate.md` and that
file's own docstring.  It is lab evidence, not a panel: nothing here is a specimen, and
no byte claim in it is checked by the gate.

## 1. What each tier costs, measured on this host (24 cores)

| command | serial | parallel | verdicts |
|---|---|---|---|
| `tools/e2e_gate.py` | **2.3 s** | — | 1074 byte-exact, 184 refusals, 9 divergences, 102 coverage rows, census, prose |
| `tools/e2e_gate.py --runtime` | **588 s** | **77 s** at `-j 8` | 71/71 runtime rows |
| `tools/e2e_gate.py --link-run -j 6` on 12 specimens | 101 s | **19 s** | identical verdict lines, serial vs parallel |
| `--link-run` per arm | ~6.6 s (mine-only) / ~8.4 s (DR arm) | — | 1072 arms exist |

The compile tier was already fast; the two CP/M tiers were the problem, and both are now
delegated: `--runtime` is rune-ci's `full` suite, `--link-run` is its `audit` suite.

## 2. The arm could not fail

`link_run()` printed `.COM DIFFERS! vs DR`, `CONSOLE DIFFERS` and `MISSING TRANSCRIPT`
and **returned nothing**; `main()`'s status came from the byte panel alone.  Against the
last full serial run (818 arms printed): 212 `.COM IDENTICAL vs DR`, 0
differing, 0 `MISSING TRANSCRIPT` — so tightening this changes no verdict that exists.
What it changes is that the arm can now REPORT a verdict, which is the precondition for
CI being allowed to own it instead of an agent burning 90 minutes on it.

Two more silent shapes are now failures: a nonzero `link` step, and **no `.COM` at all**
— which the old code reported as "mine-only arm, captured 0 raw output bytes" and passed.

## 3. The 55 arms that never terminate

`--link-run` covers 1072 specimens.  55 of them have never produced a console region to
compare: the emulator is killed on timeout and the old harness called that a pass.  Each
was run **alone** (no pool) and its transcript read, so "does not terminate" is measured
per program:

| specimen | last bytes of its own transcript |
|---|---|
| `E11B` | A>C: C> >>> D: D: D> D>E11B 7 A= 7^Z |
| `E11E` | by Udo Munk) A>C: C> >>> D: D: D> D>E11E ^Z |
| `E29PD1` | by Udo Munk) A>C: C> >>> D: D: D> D>E29PD1 |
| `E29PD2` | by Udo Munk) A>C: C> >>> D: D: D> D>E29PD2 |
| `E30H1` | by Udo Munk) A>C: C> >>> D: D: D> D>E30H1 ^Z |
| `E32E1` | by Udo Munk) A>C: C> >>> D: D: D> D>E32E1 ^Z |
| `E32E2` | by Udo Munk) A>C: C> >>> D: D: D> D>E32E2 ^Z |
| `E34A2` | by Udo Munk) A>C: C> >>> D: D: D> D>E34A2 ^Z |
| `E34A3` | by Udo Munk) A>C: C> >>> D: D: D> D>E34A3 ^Z |
| `E34A4` | by Udo Munk) A>C: C> >>> D: D: D> D>E34A4 ^Z |
| `E34A5` | by Udo Munk) A>C: C> >>> D: D: D> D>E34A5 ^Z |
| `E34A6` | by Udo Munk) A>C: C> >>> D: D: D> D>E34A6 ^Z |
| `E34A7` | by Udo Munk) A>C: C> >>> D: D: D> D>E34A7 ^Z |
| `E34A8` | by Udo Munk) A>C: C> >>> D: D: D> D>E34A8 ^Z |
| `E35X2` | 7 by Udo Munk) A>C: C> >>> D: D: D> D>E35X2 |
| `E35X3` | 7 by Udo Munk) A>C: C> >>> D: D: D> D>E35X3 |
| `E35X5` | 7 by Udo Munk) A>C: C> >>> D: D: D> D>E35X5 |
| `E35Y3` | 7 by Udo Munk) A>C: C> >>> D: D: D> D>E35Y3 |
| `E36T14` | by Udo Munk) A>C: C> >>> D: D: D> D>E36T14 |
| `E36T3` | 7 by Udo Munk) A>C: C> >>> D: D: D> D>E36T3 |
| `E36T4` | 7 by Udo Munk) A>C: C> >>> D: D: D> D>E36T4 |
| `E36T5` | 7 by Udo Munk) A>C: C> >>> D: D: D> D>E36T5 |
| `E36T7` | 7 by Udo Munk) A>C: C> >>> D: D: D> D>E36T7 |
| `N79GOTO` | Udo Munk) A>C: C> >>> D: D: D> D>N79GOTO ^Z |
| `PD7` | 1988-2007 by Udo Munk) A>C: C> >>> D: D: D> D> |
| `PD9` | 1988-2007 by Udo Munk) A>C: C> >>> D: D: D> D> |
| `R1030` | 7 by Udo Munk) A>C: C> >>> D: D: D> D>R1030 |
| `R3004` | by Udo Munk) A>C: C> >>> D: D: D> D>R3004 ^Z |
| `R3065` | by Udo Munk) A>C: C> >>> D: D: D> D>R3065 ^Z |
| `R3066` | by Udo Munk) A>C: C> >>> D: D: D> D>R3066 ^Z |
| `R3100` | by Udo Munk) A>C: C> >>> D: D: D> D>R3100 ^Z |
| `R3105` | X X X X X X X X X X X X X X X X X X X X X X X X X X X X |
| `R401` | 07 by Udo Munk) A>C: C> >>> D: D: D> D>R401 |
| `R407` | -17560 )= -17560 f( -17559 )= -17559 f( |
| `R408` | 07 by Udo Munk) A>C: C> >>> D: D: D> D>R408 |
| `R409` | 07 by Udo Munk) A>C: C> >>> D: D: D> D>R409 |
| `R410` | 07 by Udo Munk) A>C: C> >>> D: D: D> D>R410 |
| `R411` | 07 by Udo Munk) A>C: C> >>> D: D: D> D>R411 |
| `R412` | 07 by Udo Munk) A>C: C> >>> D: D: D> D>R412 |
| `R414` | 07 by Udo Munk) A>C: C> >>> D: D: D> D>R414 |
| `R415` | 07 by Udo Munk) A>C: C> >>> D: D: D> D>R415 |
| `R418` | 07 by Udo Munk) A>C: C> >>> D: D: D> D>R418 |
| `R419` | 07 by Udo Munk) A>C: C> >>> D: D: D> D>R419 |
| `R421` | 77 )= 6 f( 14678 )= 6 f( 1467 |
| `R422` | 4 )= 6 f( 16385 )= 6 f( 16386 |
| `R423` | 07 by Udo Munk) A>C: C> >>> D: D: D> D>R423 |
| `R424` | 6 f( -24333 )= 6 f( -24332 )= 6 |
| `R426` | 07 by Udo Munk) A>C: C> >>> D: D: D> D>R426 |
| `R427` | 07 by Udo Munk) A>C: C> >>> D: D: D> D>R427 |
| `R428` | 07 by Udo Munk) A>C: C> >>> D: D: D> D>R428 |
| `R431` | 07 by Udo Munk) A>C: C> >>> D: D: D> D>R431 |
| `REVERSE` | A>C: C> >>> D: D: D> D>REVERSE Whats up? ^Z |
| `RFACT` | 1988-2007 by Udo Munk) A>C: C> >>> D: D: D> D> |
| `TEST` | : C> >>> D: D: D> D>TEST Type Three Numbers: ^Z |

Most stop at their own command echo; `REVERSE` prints `What's up?` and `TEST` prints
`Type Three Numbers:` — programs that wait for input this harness does not send.  None is a crash, and none is "ran and printed nothing".  `V5` is the 55th and the most
interesting: it was NOT in the sample that seeded the set — the **full audit** found it, by
blowing the 136 s budget an unpinned arm gets.  Run alone it reports `rc=2 timeout-or-hang`
in 4.1 s with a transcript that stops at the bare `D>` prompt, **before** its own command
echo, so nothing of V5 ever ran; the old serial harness reported it as "captured 23 raw output
bytes" and passed.  That is the mechanism working: the sample seeded 54, the panel caught the
one the sample missed.

`25` arms printed `captured 0 raw output bytes` in the old serial run; that number is
the footprint of this hole, and it is NOT equal to 54 because some of the 54 printed a
nonzero prefix before hanging (RFACT prints DR's factoring banner).

## 4. Why a pool must not be allowed to invent a hang

The run step's timeout is a **wall-clock** budget.  `V3` runs in **4.1 s** alone and blew
the stock 40 s timeout at `-j 12`; at `-j 6` it passes.  An arm the pool starved and an
arm that genuinely never end are different facts.

`run_timeout(name, jobs)` therefore gives an **unpinned** arm `40 + 12·jobs` seconds
(capped at 160) and a **pinned** arm only 25 s.  The consequence is deliberate: a new hang
cannot hide behind `HANG_ARMS`, because an unnamed arm has to blow a budget that is three
to four times the stock one, while the known hangs cost the audit nothing extra.

## 5. Two specimens cannot be link-run, and four more were silently un-linked

* `N29_DECININT` (12 chars) and `N4_SKIPVAR` (10 chars) die in the link step with
  `SAFETY: illegal CP/M name` — `oracle/cpmwork.check_name` enforces CP/M's 8-character
  limit.  They are in `NO_LINK_ARMS`, are named on the panel's last line, and are **not**
  counted as arms that passed.  They are also not folded into the denominator as failures,
  because "cannot be built" is a different fact from "ran and disagreed".
* `E29F`, `E29G`, `E29I`, `E29J` are multi-module programs whose companion (`A`/`B`)
  `link()` reads at `golden/<tag>/<COMPANION>/<COMPANION>.REL`.  Nothing staged that file,
  so all four linked with an **unresolved reference** and printed "captured 0".  `link_arm`
  now compiles and stages the companion; the four execute for real and produce 126, 45,
  141 and 45 bytes of console respectively.  This is the [C137] lesson in the harness's own
  shape: LINK writes a `.COM` even with `UNDEFINED SYMBOLS:`, so "a .COM appeared" was
  never the test.

## 6. Concurrency fixes this required

* `link_run` shared the tags `e2estage`/`e2elink`/`e2erun`... and `finally`-`rmtree`'d the
  **whole tag directory**, so two arms in flight deleted each other's objects.  Tags are
  now per-specimen (`e2estage_<name>`), which is what makes `-j` possible at all.
* `oracle/cpmwork.Run` claimed its run dir with `if not exists: break` and then
  `makedirs` — a check-then-create window in which a second claimant died in
  `FileExistsError`.  The claim is now the atomic operation (`makedirs` or lose the race
  and take the next slot); the symlink guard still runs before it.
* `--only` was `action="store", nargs="*"`, so `--only A --only B` kept only `B` and every
  other arm printed `skipped (--only filter)` — an operator asking for a batch got a
  3-second run and could read it as a pass.  It is `action="extend"` now, and an unknown
  name aborts the gate instead of being filtered away.
* A row or arm that **raises** is reported as that row's failure (`_safe_row`,
  `_safe_arm`) rather than aborting the pool and leaving the other ~800 without a verdict.
* `runtime_row` prints its own `[12.3s]`.  The CI wrapper used to derive per-row seconds
  from the gap between consecutive timed lines, which is a fair estimate serially and
  meaningless under a pool.

## 7. Where each tier runs from now on

| tier | where | command |
|---|---|---|
| compile panels (2 s) | every edit, locally | `tools/e2e_gate.py` |
| runtime panel (77 s) | rune-ci `--suite full` | `--runtime -j 8` |
| DR-vs-mine audit (10-20 min) | rune-ci `--suite audit` | `--runtime --link-run -j 8` |

The rule this phase adopts: **an agent does not run the CP/M tiers on the critical path.**
It commits, submits, and polls.  A 90-minute local run is not rigour, it is a reason to
skip the check next time.

## 8. What the builder did on the first try, and why it was not a gate failure

Both suites were submitted at the commit that introduced them.  Both died in **2-3 seconds**
in the `dune-build` step:

    bash -c 'cd ocaml && dune build'
    bash: ligne 1: dune: commande introuvable
    program finished with exit code 127

Nothing to do with the gate.  `dune` was on PATH only because the worker daemon had once
been launched from a shell that ran `eval $(opam env)`; restarting the worker to pick up the
new builder dropped that inherited PATH, and every build since would fail before reaching a
panel.  `/proc/<worker>/environ` confirmed it: no `.opam/default/bin`.

The fix is not "start the daemon from the right shell" — that is the same fragility with a
step counter added.  `rune_ci_common.TOOLCHAIN_ENV` names the switch (`PATH`,
`OPAM_SWITCH_PREFIX`, `CAML_LD_LIBRARY_PATH`) and the `dune-build` step gets it, so a build
does not depend on how its daemon was launched.  Verified before shipping, not after:
`env -i HOME=$HOME PATH=<switch>:/usr/bin:/bin … dune build` with `_build/default/bin`
deleted first rebuilt the compiler from scratch, rc=0, 4.7 MB `pli80c.exe`.  The cpmtools the
fixtures step needs (`mkfs.cpm`, `cpmcp`) resolve under the new PATH from `/usr/bin`.

`ci_fingerprint()` now hashes `TOOLCHAIN_ENV` too, and `CI_VERSION` is `rune-ci/5`.  That is
the gap the failure exposed: the fingerprint covered each suite's *argv*, so "same command,
different environment" was invisible to it — a cached green for the command said nothing
about the toolchain the command would find.

Then, at the same SHA:

| suite | build | wall | phases |
|---|---|---|---|
| `full` | #35 | **81 s** | byte 1.6 s, runtime 74.2 s, negatives/divergences/coverage sub-second |
| `audit` | #2 | **1668 s** | byte 1.6 s, runtime 74.2 s, **link_run 1588.1 s** |

Counts recorded by the audit: `byte_exact 1074/1074`, `refusals 184/184`, `divergences 9/9`,
`coverage 102 rows 0 errors`, `runtime 71/71`, **`link_run 1072/1072, failed 0`**, census
`EXACT 15 / DIFFERS 0 / REFUSED 26`, `gate_exit_code 0`, `failed_steps []`.

`slowest_runtime` rows carry `seconds_self_reported: True`, which is the proof the timing fix
matters under a pool: a gap between consecutive lines would have attributed one row's 8.3 s
to whichever row happened to print next.

## 9. The row count was wrong twice, for two different reasons

**Reason one: the wrapper counted lines, not rows.**  `runtime_row_count` came back **92**
for a **71**-row panel.  A runtime row that checks an exported file prints twice --
`runtime E46N13  FILE OK ...` and then `runtime E46N13  OK ...` -- so 21 rows contributed
two lines each.  My local runs missed this because the gate's own `counts.runtime` (the
verdict line I actually read) says 71 and comes from a different place in the log; two
numbers for one thing, and only one of them was wrong.  `_dedupe_rows` now merges by name,
with **fail sticking** if any of a row's lines failed and the **longest** duration winning.

**Reason two, found only because the first fix changed the symptom:** after dedupe, the
builder reported **71** on one build and **70** on the next, over identical code.  That is
not counting; that is the log itself.  `print(x)` issues TWO writes -- the text, then the
newline -- so with `-j 8` a second thread can land between them and produce one physical
line carrying two records.  `gate_runner` anchors rows with `^  runtime `, so a swallowed
row silently stops existing: a 71-row panel with one torn line reports 70.

A count that depends on thread interleaving is worse than a wrong count, because it looks
like a real result and moves.  `_LineAtomicStream` buffers until a newline and hands the
underlying stream the complete line in ONE `write`, which is atomic for a pipe under
PIPE_BUF (4096 on Linux; a gate line is ~80 bytes).  Installed only when a pool starts, so
serial output is untouched -- one writer cannot interleave with itself.

`_line_atomic_selftest()` runs in the gate's own pre-flight, and it is deterministic rather
than race-dependent:

* the **control** asserts the invariant is violated WITHOUT the wrapper -- `print()`'s split
  writes necessarily produce a write not ending in `\n`, which is the exact instant another
  thread can cut in.  A control that might not tear proves nothing, so the gate aborts if it
  doesn't.
* the wrapper must deliver only newline-terminated writes, in order, with no merged records.
* 2400 records through 8 threads must come back as 2400 lines, none carrying two records --
  the 71-reported-as-70 shape, checked directly.

Verified locally against the CI regex itself: a `-j 8` run yields 92 matching lines, 71
distinct row names, and **zero** lines containing two `runtime` records.

`CI_VERSION` is `rune-ci/6`; the fingerprint already hashes `ci/gate_runner.py`, so the
counting fix invalidates cached greens without being told to.

## 10. What each build proved, and which SHA it proved it on

| build | suite | SHA | wall | result |
|---|---|---|---|---|
| #34, audit #1 | full, audit | `87c11db` | 2-3 s | **failed**: `dune: commande introuvable` (section 8) |
| #35 | full | `87c11db` | 81 s | passed |
| audit #2 | audit | `87c11db` | 1668 s | passed, `link_run 1072/1072`, `runtime_row_count 92` |
| #36 | full | `87c11db`+docs | 81 s | passed, `runtime_row_count 71` (dedupe only, before the torn-line fix) |
| #37 | full | `be3c447` | 80 s | passed, `runtime_row_count 70` -- the tearing bug, caught by the count disagreeing with the gate's own verdict line |
| audit, final | audit | the commit that fixes both | — | the audit re-runs on the final SHA because BOTH panels share the stdout plumbing that section 9 fixes; a green for the runtime panel is not a green for the link panel's log |

The last row is deliberate: the stdout wrapper changes how every pooled panel reports, so
the 27-minute audit is re-run on the fixed SHA rather than inherited from `87c11db`.  That
is the cost of delegating, and it is paid by the builder.
