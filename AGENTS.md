# AGENTS.md — DR PL/I-80 (project **DRPLi**)

## What this is

Reproduction of the behaviour of the **Digital Research PL/I-80 Compiler v1.4**
(CP/M-80, 1980/1983 distribution) in **OCaml**, judged by **byte-exact complete `.REL`
object output** against the original compiler, which is the oracle.

**Overriding priority: compiler reproduction.** Everything else in this repository —
including the Pi Handoff / context-guard infrastructure installed here — is
*infrastructure*. Infrastructure never outranks, redirects or redefines the scientific
work. If a handoff document and the repository disagree, the repository wins and the
document is the thing that must be corrected.

## Where

- Root: `/home/john/projects/sushiworks/pli80`
- Branch: `main` (DRPLi is the project name, **not** a branch). One worktree only;
  the live `/tmp/wt_base` worktree and `.git/worktrees/` metadata are not ours to touch.
- Long-term deliverable: `ocaml/` (dune project: `lib/lexer.ml`, `parser.ml`, `bind.ml`,
  `ir.ml`, `codegen.ml`, `rel80.ml`, `bin/pli80c.exe`).

## Read in this order at session start

1. `AGENTS.md` (this file)
2. `PROTOCOL.md` — scientific rules and the handoff workflow
3. `GOAL.md` — objective + acceptance criteria (protected; do not edit)
4. `HANDOFF.md` — recovery instructions and exact next action
5. `PROGRESS.md` — current phase, completed/pending, blockers
6. `LEARNINGS.md` — working-method and environment lessons
7. `spec/CLAIMS.md` — **the authoritative evidence ledger** (claims C001…C308 at the
   time of writing). Handoff files are pointers into it, never a substitute for it.

## Evidence rules (summary; full text in `PROTOCOL.md`)

- A statement about compiler behaviour is admissible only from an oracle experiment, and
  is recorded in `spec/CLAIMS.md` with its specimen and golden paths.
- Classify every difference as `dr-refuses`, `my-gap` or `unmeasured`. Missing evidence is
  never promoted into a DR rule; write `[TBD]`.
- Compare **complete `.REL` files byte-for-byte**, not CODE segments alone.

## Protected — never modify, move, clean, regenerate or reset

`artefacts/` (original distribution: `PLI.COM`, `LINK.COM`, `PLILIB.IRL`, …),
`manuals/`, `extracted/`, `references/`,
`oracle/` (`disks/`, `workspace/`, `work/`, `srctools/`, the `.py` harness),
`golden/` (including everything it ignores), `probes/`, `build/`, `ocaml/_build/`,
`thirdparty/` (nested git repos `PLI-2000`, `z80pack`),
`spec/`, `tools/`, existing compiler sources,
`/home/john/pli/` (Runes lab, QX-10 traces), `/home/john/services/rune-ci`.

Never run `git clean`, `git reset --hard`, destructive checkouts, recursive cleanup, or
`git add -A`. Ignored and generated data are evidence, not disposable files.

## Verification

The repository gate is `python3 tools/e2e_gate.py` (compile tier: byte panel, negative
panel, divergence panel, coverage, census, prose checks). `--runtime` and `--link-run`
drive CP/M under cpmsim and are delegated to the external `rune-ci` Buildbot
(`spec/notes/rune-ci-external-gate.md`).

**Do not run the compiler, the oracle, LINK-80, cpmsim, Rune CI or any E2E gate as part
of infrastructure/handoff work.** Run them only when the session's actual task is
compiler development or gate verification.

## Handoff / context-guard infrastructure

Loaded explicitly (project is not yet trusted by the production Pi profile):

```bash
cd /home/john/projects/sushiworks/pli80
PI_CODING_AGENT_DIR=/home/john/.sushi/pi \
pi -e .pi/extensions/context-guard/index.ts
```

- Config: `handoff.config.json`. Runtime state: `.pi-guard/` (git-ignored).
- Commands: `/guard status`, `/guard simulate <n>`, `/handoff`, `/handoff verify`,
  `/handoff ready [check]`. Reference: `.agents/skills/pi-handoff/`.
- The guard writes managed checkpoint blocks **only** inside `HANDOFF.md` and
  `PROGRESS.md`; it never writes `GOAL.md` or `LEARNINGS.md`.
- **Never hand-write or hand-edit a managed checkpoint block.** Never invent checkpoint
  metadata.
- Session renewal is disabled by policy. Do not enable it, and do not change global Pi
  compaction settings, without a new operator decision.

## How to resume work

Read `HANDOFF.md` → `## Next action` and `## Recovery instructions`; verify Git HEAD and
that the working tree is clean; check checkpoint freshness with `/handoff verify` (a
**stale** checkpoint is not authoritative — re-read the ledger and the lab evidence);
then confirm the named specimen/claim files still exist before acting on them.
