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

## Session start — lean recovery (operator policy 2026-10-30)

Pi auto-loads this `AGENTS.md`. With `recovery.lean: true`, first read
`HANDOFF.md` and `PROGRESS.md` for the current operation, validate the checkpoint
with `/handoff verify`, then consult `spec/CLAIMS.md` selectively — only the cited
claim ids; never bulk-read a ledger — and the specific evidence
for the NEXT action. `PROTOCOL.md` remains binding and must be consulted before
any unfamiliar scientific procedure or policy decision; `GOAL.md` and
`LEARNINGS.md` remain authoritative and are read selectively when relevant.
Lean recovery defers reading; it never relaxes the evidence/protection rules.
On a stale checkpoint, reconstruct from current commits and authoritative evidence
before `/handoff finalize`. Never trust obsolete managed-block instructions.

## Evidence rules (summary; full text in `PROTOCOL.md`)

- A statement about compiler behaviour is admissible only from an oracle experiment, and
  is recorded in `spec/CLAIMS.md` with its specimen and golden paths.
- Classify every difference as `dr-refuses`, `my-gap` or `unmeasured`. Missing evidence is
  never promoted into a DR rule; write `[TBD]`.
- Compare **complete `.REL` files byte-for-byte**, not CODE segments alone.

## Preservation boundaries and authorized scientific work

**Historical inputs and externally maintained sources — preserve.** Do not overwrite,
regenerate or "repair" original DR distribution files in `artefacts/` (`PLI.COM`,
`LINK.COM`, `PLILIB.IRL`, …), `manuals/`, `extracted/`, `references/`, or the
original CP/M disk images in `oracle/disks/`. Existing oracle results and golden
baselines are scientific evidence: never silently rewrite, replace or delete them.
The nested repositories under `thirdparty/` (`PLI-2000`, `z80pack`) and the external
`/home/john/pli/` and `/home/john/services/rune-ci` trees are out of scope
unless explicitly authorized for a separate task.

**Scientific development — modification is expected and permitted.** The active compiler
task may edit `ocaml/` compiler sources, `spec/` (including `spec/CLAIMS.md` and
the machine-maintained ledgers), `tools/`, `probes/`, and the `oracle/` harness
code (including its Python scripts). New probes, golden objects and evidence may
be added as part of pre-registered, measured experiments. Corrections to prior
evidence require explicit justification and a traceable record, not silent
replacement. Follow `PROTOCOL.md`, verify results against the original oracle,
and commit deliberately scoped changes. **Never treat scientific source trees
as read-only merely because they also contain valuable evidence.**

**Generated and ignored working state — preserve, not prohibit.** Authorized
compiler experiments may create or update files in `oracle/workspace/`,
`oracle/work/`, `build/`, `ocaml/_build/`, and `golden/` as required by the
normal workflow. These directories also contain valuable ignored evidence:
never blanket-clean, recursively regenerate, relocate or discard them. Inspect
precise paths and effects before any operation.

Never run `git clean`, `git reset --hard`, destructive checkouts, recursive cleanup,
or `git add -A`. Stage explicit paths only. Ignored and generated data are
not automatically disposable.

## Verification

The repository gate is `python3 tools/e2e_gate.py` (compile tier: byte panel, negative
panel, divergence panel, coverage, census, prose checks). `--runtime` and `--link-run`
drive CP/M under cpmsim and are delegated to the external `rune-ci` Buildbot
(`spec/notes/rune-ci-external-gate.md`).

**Do not run the compiler, the oracle, LINK-80, cpmsim, Rune CI or any E2E gate as part
of infrastructure/handoff work.** Run them only when the session's actual task is
compiler development or gate verification.

## Handoff / context-guard infrastructure

The project is **trusted** by the production profile (exact-path entry for
`/home/john/projects/sushiworks/pli80` in `/home/john/.sushi/pi/trust.json`). A plain `pi`
launched from this directory auto-discovers `context-guard`, the `pi-handoff` skill and
`.pi/settings.json` — do **not** also load the extension with `-e` (it must load exactly once).
Controlled launches remove the inherited environment override:

```bash
cd /home/john/projects/sushiworks/pli80
env -u CONTEXT_GUARD_AUTO_RENEW PI_CODING_AGENT_DIR=/home/john/.sushi/pi pi
```

`handoff.config.json` is authoritative; never let ambient `CONTEXT_GUARD_*` variables decide
behaviour.

- Config: `handoff.config.json`. Runtime state: `.pi-guard/` (git-ignored).
- Commands: `/guard status`, `/guard simulate <n>`, `/handoff`, `/handoff verify`,
  `/handoff ready [check]`, `/handoff finalize`, `/guard events [n]`,
  `/handoff renew [go|stop|resume|status]`. Reference: `.agents/skills/pi-handoff/`.
- The guard writes managed checkpoint blocks **only** inside `HANDOFF.md` and
  `PROGRESS.md`; it never writes `GOAL.md` or `LEARNINGS.md`.
- **Never hand-write or hand-edit a managed checkpoint block.** Never invent checkpoint
  metadata.
- **Renewal enabled, compaction disabled (operator decision 2026-10-29):**
  renewal is enabled for this project with a bounded per-chain cap (an operating limit,
  not unlimited autonomy). The authoritative values — `renewal.enabled`,
  `renewal.autoRenew`, `renewal.maxRenewals`, `workingContextWindow`, reserves,
  thresholds — live ONLY in `handoff.config.json`: read that file and `/guard status`,
  never a document's quotation of them. Each new experiment chain starts only after
  the operator archives and resets the previous ignored renewal-state.json. Automatic Pi compaction is disabled for this
  project only via `.pi/settings.json`. The pressure/renewal operating rules are in
  `PROTOCOL.md` Part 2. Do not change the renewal policy or any **global** Pi setting
  without a new operator decision.

## How to resume work

Read `HANDOFF.md` → `## Next action` and `## Recovery instructions`; verify Git HEAD and
that the working tree is clean; check checkpoint freshness with `/handoff verify` (a
**stale** checkpoint is not authoritative — re-read the ledger and the lab evidence);
then confirm the named specimen/claim files still exist before acting on them.
