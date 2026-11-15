# Legacy root handoff snapshot — 2026-11-15

**Status: HISTORICAL EVIDENCE. NOT current operational authority.**

An exact, read-only copy of the three oversized legacy root durable documents, taken
before any consolidation. Nothing here is an instruction. Current authority remains the
live root files (`HANDOFF.md`, `PROGRESS.md`, `LEARNINGS.md`, `GOAL.md`), `PROTOCOL.md`,
`AGENTS.md`, and the science ledgers (`spec/CLAIMS.md`, `spec/lab-evidence/**`).

## Provenance

| | |
|---|---|
| Snapshot git HEAD | `49728acce6d5964c45dfe6fa4bd1bfbbe9883ccc` ("Archive sealed E2E-54/P1-m4 mission") |
| Snapshot date | 2026-11-15 |
| Handoff checkpoint at capture | generation **852**, id `g852-54fe9fceab22`, attested, written 2026-11-14T12:51:27.685Z by session `01a1d9f0-b397-700a-9d27-3c0c6fa6a746` |
| Mission instance | **legacy project mode** — no named mission selected; no instance closure seal |
| Campaign state at capture | E2E-54/P2-DIFF-4 CLOSED at `e65c9c31`; last guard checkpoint commit `bf04fafe`; STOP in force, awaiting operator brief |
| Authority for the snapshot | Operator-authorized documentary maintenance, Stage B (archival + plan only) |
| Copy method | Operator-created verbatim copies; independently re-verified by SHA-256 (below) |

## Contents and hashes

SHA-256 verified twice at capture: each archived copy matches its expected digest **and**
the corresponding root file byte-for-byte at HEAD `49728acc`.

| File | Bytes | SHA-256 |
|---|---|---|
| `HANDOFF.md` | 1,905,931 | `7364774e58b41c85355562680ce2da534c4831136eedc4077109b45a8440276f` |
| `PROGRESS.md` | 1,353,945 | `81bb20cd18a56f2312f2440880720527de6ac34783daa922f53d3525613ecad6` |
| `LEARNINGS.md` | 1,793,045 | `786ce1a1679a875981f1502370a24ff3efe2eaf45f56764c6033b8bba6dc558c` |

Re-verify at any time with:

```sh
cd /home/john/projects/sushiworks/pli80
sha256sum docs/history/legacy-root-2026-11-15/{HANDOFF,PROGRESS,LEARNINGS}.md \
          HANDOFF.md PROGRESS.md LEARNINGS.md
```

Root files will begin to differ from this snapshot the moment consolidation lands; that is
expected and is exactly why this directory exists.

## Why the originals are this large (measured, read-only)

These measurements were produced by `python3 scripts/durable_edit.py audit --root . --json`
plus bounded read-only analysis. They matter for anyone interpreting the snapshot:

- **`HANDOFF.md` is duplicated wholesale.** Lines 74–3958 are reproduced at lines
  3961–7845 (offset exactly 3887 lines): 1,328 of the 3,885 line-pairs differ only inside the
  managed blocks, and exactly **one** prose line differs (a `SUPERSEDED-BY-ABOVE: ` prefix).
  Within it, the campaign body (lines 1653–2608 ↔ 5540–6495, 85,431 B) is byte-identical —
  proven by identical SHA-256 `e2fc26f02e1037db…` on both sides. The redundant tail is
  **950,249 B = 49.9% of the file**. 76 of the file's 77 level-2 headings occur exactly twice;
  only `## Recovery instructions` is unique. This is why `## Next action` appears at 2449
  **and** 6336, and `## Unfinished operations` at 2560 **and** 6447.
- **`HANDOFF.md` contains two guard `checkpoint` blocks, not one.** Block 1 (line 2609)
  is generation **852, attested**; block 2 (line 6496) is generation **844, unattested** —
  a stale orphan. Combined managed bytes are **1,264,089**, not the 842,167 that `audit`
  reports (it counts only the first HANDOFF block).
- **Size is caused by checkpoint *field content*, not by the generation count.** Each block
  carries one `### Next action` payload of **419,843 B** (PROGRESS: a `next-action:` field of
  419,965 B) — ~99% of every block — and generation 852 itself contributes 27 bytes of
  metadata. That payload is **100% redundant with live manual prose**: 1,156 of its 1,158
  non-blank lines appear verbatim in `HANDOFF.md` prose. The block is a snapshot of prose that
  grew too large; shrinking the prose (through the guard's own refresh, never by editing the
  block) is what shrinks the block.
- `audit` reports line numbers with managed blocks **stripped**; raw file lines differ.
  Example: audit's duplicate `## Next action` at "line 4984" is raw line 6336.

## How to find historical material

Do **not** read these files top to bottom. They are far too large for a model context.
Locate sections by identifier instead:

```sh
cd docs/history/legacy-root-2026-11-15

# by campaign identifier
grep -n "E2E-54/P2-DIFF-4" *.md | head -40
grep -n "^## .*FC-01" HANDOFF.md

# by claim id, commit, or evidence path
grep -n "C352\|C380" *.md
grep -n "6a35b9c\|a5815a8" *.md
grep -rn "spec/lab-evidence/e2e50-p2" .

# structural map first, then narrow (bounded reads)
grep -n "^## " LEARNINGS.md | tail -30
```

Useful keys: campaign/round ids (`E2E-49/P4`, `E2E-54/P1-m1`, `FC-01`), claim ids
(`C352`, `ledger 203/C380`), golden/evidence paths (`build/fc01/corp*`,
`spec/lab-evidence/**`), commit SHAs, and renewal-chain coordinates
(`session 01a1d9f0`, `renewal 5/12`).

Superseded prose is deliberately preserved as written, tagged `SUPERSEDED-BY-ABOVE`,
`Superseded:` or `(SUPERSEDED ...)` per PROTOCOL rule #2 — those markers mean "kept, not
endorsed", never "delete".

## Relationship to the sealed mission instance

This snapshot is **root/legacy** material only. The successful E2E-54/P1-m4 campaign was run
in a separate, named mission instance and is **sealed** elsewhere:

`.pi-handoff/instances/drpli-p1-m4-early-return/` — mission docs (HANDOFF 5,516 B,
PROGRESS 3,147 B, LEARNINGS 9,811 B) plus `mission.json` and `closure.json`, committed at
`49728acc`. That seal records closure at checkpoint `g9-b25a63ffa794` (attested),
14/14 differential cases, chain `2026-11-14T23:37:17.737Z`, git revision `f2bb784c`.

Sealed instance content is immutable evidence and is **not** part of this consolidation.
Instance docs are small enough to read directly; this snapshot is not.

## WARNING — do not inject these documents into a Pi session

Never `cat`, `read` wholesale, or otherwise load these files into a model context. Each is
1.4–1.9 MB; all three together measure **5,018,757 characters ≈ 1,254,690 estimated tokens**
(chars/4 estimate), against a 220,000-token window and a 145,000-token working context
window. Loading them would exhaust any session before work begins. The lean recovery tier
alone is 3,220,720 characters.

Query with `grep`/`sed -n 'X,Yp'` for a bounded range, or read the live root documents for
current instructions. For knowledge that has been formally published, use the append-only
Handoff knowledge registry rather than these files.

## Related

- Consolidation plan for the live root documents: `CONSOLIDATION-PLAN.md` (plan only, not
  an authorization to apply).
- Earlier per-round archives and the archive convention: `docs/history/README.md`.
