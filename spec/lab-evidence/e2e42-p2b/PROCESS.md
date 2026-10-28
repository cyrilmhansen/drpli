# E2E-42 / P2b — process accounting

Everything below is ordered by **commit SHA and `git log` date**, not by filesystem timestamps:
`e2e42-p2a/PROCESS.md` records that this phase's predecessor ordered its narrative by mtime, which is
not evidence (`git` rewrites nothing, a checkout rewrites everything).

## The pre-registration sequence, as commits

| commit | when (git log) | what it contained | oracle calls it authorised |
|---|---|---|---|
| `c816af5` | — | baseline the phase starts from | — |
| `f3902363ddddeeca77b9f374055c4c6338014d03` | 2026-10-28 13:31:27 +0100 | 32 probes `E46M1`–`E46M32`, `HYPOTHESES.md` §1–§4 (per-probe CODE/DATA/`?SIOOP`/`?QIOOP` predictions), `chaindump.py`, `predict_sizes.py` | the three `e42p2b*` batches |
| `5de6b08` | 2026-10-28 13:38:06 +0100 | every probe re-wrapped to ≤71 columns after DR truncated a 233-column comment | (same batches — the fix was for a submission defect, not a prediction) |
| `18785e5` | 2026-10-28 15:12:06 +0100 | `E46M33`, `E46M34`, `HYPOTHESES.md` §5 | `e42p2b5` |
| `ae15bee` | 2026-10-28 15:24:02 +0100 | `E46M35`, `E46M36`, `HYPOTHESES.md` §6 | `e42p2b6` |

No probe was written, and no prediction was amended, after the oracle call it belongs to.  The
`P2b` implementation (matcher, authorisation, pool fix) came **after** `e42p2b*`, which is the point:
the predictions were written when the code could not yet produce them.

## Oracle invocations, and the switch that does not work

    PLI_SRC=probes python3 oracle/batch.py E46M1 … E46M11 --tag e42p2b --switches '$L$D'

* `$L$D` completes; **`$L$D$S` hangs** on this harness (the symbol-table switch never returns and the
  batch times out).  Three tags were needed for 32 probes because of the batch size, not because of
  anything about the programs: `e42p2b`, `e42p2b2`, `e42p2b3`.
* A golden tag directory refuses to be overwritten unless `--reuse` is passed; the follow-up probes
  therefore got new tags (`e42p2b4` = the aborted run, `e42p2b5`, `e42p2b6`) instead of being merged
  into the first.  That is the guard behaving, and the aborted tag is kept for exactly that reason.
* `batch.py` classifies from the **transcript**, not from the PRN: `ok` needs both
  `NO ERROR(S) IN PASS 1` and `NO ERROR(S) IN PASS 2` with no error count.  A run whose PRN shows a
  full listing and `CODE SIZE = …` can still be a pass-2 refusal with no `.REL` — which is what
  `E46M24/M25/M33/M34` are.  Read `dir.txt` for whether an object exists; the PRN header alone will
  not tell you.

## Probe format is part of the evidence

Three rules, each of which cost at least one wasted call ([C303], `RESULTS.md` §11):

1. **≤72 columns.**  Longer lines are truncated by DR before parsing; a long comment can end the file
   early (`UNEXPECTED EOF`).
2. **CRLF + `^Z`.**  An LF-only source produces `UNEXPECTED EOF` with no listing from DR, and makes
   *this* compiler mis-count statement lines in its `[TBD]` messages.
3. **`end <name>;`, not `end <name>.`** — measured on E46M35.  Every accepted source here, and all 588
   `artefacts/*.PLI`, uses the semicolon.

## Two failure modes found by the panel rather than by a test

* **A silent misroute.**  `put file(f) skip;` matched the console bare-skip arm, compiled with rc=0
  and no `[TBD]`, and put the bytes on SYSOUT.  The byte panel could not see it (CREATE is a corpus
  program, and CREATE still refused either way); what exposed it was **the census message's line number
   moving from 39 to 44** — past a statement that should still have refused.  [C300].
* **A panel entry that was dead text.**  `NEG_META["E46K10"]` was written, then silently overwritten by
   a later `for _k in ("E46K1", … "E46K15")` bulk loop.  A specific entry must come **after** any loop
   that assigns to the same key.  The first version of the E46K10 prose the panel ever printed was the
   loop's generality, not the entry.

## `dune build | head -N` kills the build and lies about it

`head` closes the pipe, `dune` dies of `SIGPIPE`, the binary is **not relinked**, and the next test run
quietly exercises the OLD compiler — which is how a stale refusal message appeared in a session where I
had already replaced it.  `dune` also hashes content, so `touch` does not force a rebuild.  The
discipline this phase adopted: `rm -rf _build && dune build > /tmp/warn.txt 2>&1; echo RC=$?`, then
`grep -oP '^Warning \d+' /tmp/warn.txt | sort | uniq -c` and compare to the baseline profile.  The
profile is a test: when I wrote `on_opts` where the guard needed `on_opts = _ :: _`, the arm swallowed
the console route below it and the compiler said so with two new redundant-case warnings before any
panel ran — 22 → 24 W11 and 26 → 28 W9 caught a misroute that the byte panel cannot see.

## Edits made after an oracle call, and why each is legitimate

* `NEG_META["E46K10"]` re-classified `unmeasured` → `my-gap`, and `E46M26`'s prose corrected: those are
  re-readings **of DR's committed objects**, and the objects are the evidence, not my file's mtime.
  One sentence in that batch was itself a fabrication (that P086K's PUT is `list(d)`); it is withdrawn
  in place, with the source line and the object bytes that falsify it quoted ([C302]).
* `probes/E46M33.PLI`, `E46M34.PLI` were rewritten (LF → CRLF, `.` → `;`) — **after** their first
  oracle call.  That is legitimate only because the first call's artefacts are kept (`e42p2b4`) and
  because the rewrite changed the *submission*, not the *prediction*, and the corrected probes got
  their own call (`e42p2b5`) against predictions committed at `18785e5`.
* `E46M26`'s probe comment still asserts the guard order P2b falsified.  It is left alone: DR's listing
  echoes the source, so editing it would break `E46M26.PRN` ↔ `E46M26.PLI` identity, and deleting a
  wrong claim from an artefact makes the artefact look like it predicted the right thing.

## One CI submission

One `rune-ci submit` on the final SHA, not on intermediate SHAs, and the result is not waited for.
