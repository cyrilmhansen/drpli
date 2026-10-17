# Oracle harness filesystem-safety hardening

## Why
Pi runs **without a sandbox**. The oracle harness (batch.py / linkrun.py)
drives `cpmsim` and the cpmtools against real disk images and did so with
`rm -f`, `mkfs.cpm` and `cpmcp` all passed through `subprocess(...,
shell=True)` with f-string-interpolated paths. Because the compiler is
irreplaceable (boot seeds `oracle/disks/drivea|driveb.dsk` are the only
copies of a bootable CP/M-80 + LINK-80 + PLILIB environment) and the
`golden/<tag>` trees are the acceptance baseline the parity gates read,
one bad path or one injected probe name would cause unrecoverable loss.

## Risks found in the audit
1. **Shared scratch dir** — `oracle/disks/` held both the irreplaceable
   boot seeds AND the per-run compiler/work disks. Every run `rm -f`'d and
   re-`mkfs`'d drivec/drived *in that same directory*; `cpmsim` mounts a
   whole dir read-write, so a widened glob could clobber the seeds.
2. **Shell injection** — probe/artefact names were interpolated into shell
   strings (`sh(f"... {n}.PLI")`, `shell=True`). A name like `` x;rm -f ``
   would execute. `local mkfs.cpm` on PATH was also found broken (cannot
   create a fresh image); harness silently depended on which binary PATH
   resolved to.
3. **Silent overwrite** — `open(..., "w")` overwrote transcripts and
   `os.remove(dst)` deleted golden files; re-running with a colliding
   `--tag` would overwrite curated goldens with no warning.
4. **No symlink/traversal checks** — any path component could be a symlink
   pointing outside the tree.

## Safeguards implemented (`oracle/cpmwork.py`)
Two realpath-validated, symlink-free zones; **fail closed** everywhere.

* **Workspace** (`oracle/workspace/`, git-ignored): the *only* place
  generated disk images and scratch are created. Each batch gets a
  **unique** per-run subdir `run-<tag>-<seq>/` (never reuses/clobbers).
* **Boot seeds are read-only.** Each run *copies* `drivea/driveb.dsk` into
  its own subdir; `cpmsim` mounts the copy. Originals are never written.
  Verified: seed sha256 identical before/after a full compile+link+run.
* **Fresh `mkfs` only** — refuses if the target already exists (no clobber);
  rejects symlinked disk targets and bad drive letters.
* **No shell.** Every external call is `subprocess.run([...], shell=False)`
  with an argv list. `/usr/bin/mkfs.cpm` is pinned by absolute path and
  validated present + executable + non-symlink on use (no PATH fallback).
* **CP/M name validation** — `^[A-Za-z0-9_]{1,8}$` (and F8.3 for
  `BASE.EXT`); rejects `/`, `..`, `;`, backticks, spaces, `$(...)`.
* **Symlink rejection** on every path we read/write/create, including each
  existing ancestor component.
* **Output (golden) protection** — creating into a pre-existing `golden/<tag>`
  is refused unless `--reuse`; individual writes refuse to overwrite an
  existing file unless `--reuse`. `--reuse` is also the only way to opt into
  clobbering extracted REL/PRN/COM.
* **Cleanup is workspace-scoped** — `Run.cleanup()` uses Python `rmtree`
  only after asserting the target `realpath` is strictly under the workspace
  root; deleting anything else raises `SafetyError`. No external `rm`.

## Operational changes
* `batch.py` / `linkrun.py` fully rewritten against `cpmwork`; same
  compile/session semantics (still `>>> PLI D:<n> <switches>`, still one
  sim session per batch, still `%INCLUDE` on source drive, still `-u` trap
  for link/run).
* New flags: `--reuse` (opt into touching an existing golden tag),
  `--keep-run` (batch: retain the per-run workspace dir for debugging).
  Default behaviour cleans the workspace and refuses to touch goldens.
* Transcripts are written only as unique `transcript-batchN.txt` (the old
  shared `transcript.txt` that got overwritten per batch is gone); gates
  already read `transcript-batch*.txt`.

## Verification performed
* `test_safety.py` — **28/28** guard tests pass with disposable `/tmp`
  fixtures: name/path injection rejected, symlinked workspace/disk/output
  rejected, mkfs-clobber rejected, golden-tag collision refused,
  overwrite refused without `--reuse`, cleanup outside workspace refused,
  shell metacharacters proven inert (marker file never created).
* **Functional parity (byte-for-byte):**
  - compile: `batch.py P071A P071C` → `.REL` **identical** to goldens.
  - link:    `linkrun.py link LOAN1` → `.COM` **identical** to `golden/link1`.
  - run:     `linkrun.py run LOAN1` → console output **identical** to
    `golden/run2` (LOAN1 ends in a GET-EDIT wait → rc=1/timeout is the
    pre-existing capture mode, not a regression).
  - boot-seed sha256 unchanged across all of the above.
* All gates still green: parse 279/0 FAIL, bind **47 exact**/0 FAIL,
  rel-roundtrip 250/0 fail, ir 2 exact/8 known-gap/0 FAIL.
