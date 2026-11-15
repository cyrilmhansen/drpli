# LEARNINGS.md — DRPLi

**Index only.** Read-only pointers to where lessons live; **no session must bulk-read
history.** The complete pre-2026-11-15 record is preserved verbatim and hash-pinned in
`docs/history/legacy-root-2026-11-15/LEARNINGS.md` (SHA-256
`786ce1a1679a875981f1502370a24ff3efe2eaf45f56764c6033b8bba6dc558c`; 14,462 lines,
355 `## ` sections). Locate it by identifier — never read it whole:

    cd docs/history/legacy-root-2026-11-15
    grep -n "E2E-54/P2-DIFF-4\|C352\|FALSIFIED" LEARNINGS.md

## How to classify (unchanged, authoritative)

- **ACCEPTED** — measured; admissible only with oracle evidence recorded in `spec/CLAIMS.md`.
- **PROPOSED** — planned, NOT executed, NOT evidence. Never promote silently.
- **FALSIFIED** — a hypothesis/baseline/simulator shown wrong by measurement. Kept as written.
- **SUPERSEDED-BY-ABOVE** — retained for provenance per PROTOCOL #2; means "kept", not "delete".
- Difference classes: `dr-refuses` / `my-gap` / `unmeasured`. Missing evidence is never
  promoted into a DR rule; write `[TBD]`.

## Accepted

Current, high-value lessons (live text; short). Bodies of every historical lesson stay in
the snapshot (see the grep table at the bottom).

| Id | Lesson | Where |
|---|---|---|
| L-001 | Ledger count law (method): `grep -cE '^## C' spec/CLAIMS.md` == 203 counts 202 real headers + the wrapped `## CLASS;` line at CLAIMS:5080 (re-verified 2026-11-15). The variants `^## C[0-9]` (202) and `^## C[0-9]{3} ` (200) are NOT the ledger number. | snapshot §P2-DIFF-4 panel durables |
| L-002 | Repo-root execution rule (method): run repository tools from the repository root; `mirsumtest` from ROOT — relative-path redirects make other cwds silently wrong. | snapshot |
| L-004 | Duplicate root headings make the guard ambiguous: `sectionBody()` requires exactly one `## ` match, else `undefined` → checkpoint reported stale → renewal not authorized. Keep `## Next action` (and every required heading) unique. Complementary strip law and tool behaviour: see L-007. | consolidation plan §0.1(4) |
| L-005 | FC-01 corpus authoring laws, all run-witnessed (HISTORICAL RECORD, CORRECTED — see the supersession note in `## Falsified or superseded`): ordered-compare constants ≥ 1; strict compares refused (`COND.GE_LE`); no apostrophes; ≤ 71 columns; single-item `put list` with leading-blank separator; GET echo `L\r\r\n`; exit CRLF [C352]. A FAIL stays classified, never laundered. **The variable-divisor DIV `my-gap` recorded in the original FC-01 corpus was HISTORICAL, not current: E2E-51/P1 resolved compilation of variable-divisor DIV (claims C353–C355; `docs/functional-results.md` § 16, "DIV blocker GONE"), and E2E-51/P2 landed the HAMM-00 rev2 derivation fix (§ 17, lane-B PASS 2026-11-04).** The original rev1 refusal (`docs/functional-results.md` § 9) stands as preserved historical evidence. Never advertise the old restriction as active. | snapshot FC-01 §§; `docs/functional-results.md` §§ 9, 16–17 |
| L-006 | mir2o/MIR backend laws: see `docs/architecture/backend-boundary.md` §7-17 — the authoritative bake of the three P1-m4 laws. Pointer only; do not restate here. | arch §7-17 |
| L-007 | Tool laws behind L-004: `durable_edit.py` refuses duplicated headings (`AMBIGUOUS … refuse (no guessing)`, exit 3) rather than guessing; and the guard's `stripManagedSection` strips only the FIRST checkpoint block, so a duplicated document contaminates the attestation hash. Cross-reference: L-004. | consolidation plan §5, §6.3 |

## Proposed

Proposals are never authorizations. The open proposals live with their rounds, not here:
the `%include`-expansion proposal behind the CREATE blocker (`spec/lab-evidence/e2e48-p2c/
RESULTS.md`, recorded blocker line 107), and the E2E-49/P4 §3 named-refusal list — see
`PROGRESS.md` `## Blockers`. Objective-level proposals remain operator decisions (bottom
of this file).

Handoff knowledge registry: **no published records** as of 2026-11-15 (verified via
`handoff_knowledge list`). Publishing is an explicit, separate operator act, not implied by
this index.

## Falsified or superseded

- **L-003 — FALSIFIED: "Checkpoint bloat is caused by high generation count."** Measured:
  g852 metadata contributes 27 B; the bloat was one 419,843 B `### Next action` snapshot
  payload inside the block, ~100% redundant with manual prose. Blocks shrink only through
  the guard's own refresh once the prose shrinks — never by editing them.
  Evidence: `docs/history/legacy-root-2026-11-15/CONSOLIDATION-PLAN.md` §0.1.
- **SUPERSEDED: the FC-01 variable-divisor DIV restriction** (the `my-gap` half of L-005)
  and the **HAMM-00 rev2 subtraction-loop workaround** — the workaround is explicitly
  OBSOLETE ("variable-divisor division now compiles byte-exact; do NOT propose or implement
  it", pre-consolidation PROGRESS, archived; resolution measured in E2E-51/P1,
  `docs/functional-results.md` § 16; the rev2 derivation fix LANDED as E2E-51/P2, § 17).
- Superseded lesson bodies are kept as written in the snapshot, tagged
  `SUPERSEDED-BY-ABOVE` / `Superseded:` / `(SUPERSEDED ...)` per PROTOCOL #2 — markers mean
  "kept", never "delete".

## Historical lesson bodies (grep index — do not read whole)

Counts below are `^## ` heading matches in the snapshot (measured 2026-11-15); the snapshot
is authoritative.

| Campaign anchor (grep key) | Sections |
|---|---|
| `E2E-54/P2-DIFF` | 27 |
| `E2E-54/P1-` (a*, m*, mD) | 73 |
| `E2E-53` | 27 |
| `E2E-52` | 88 |
| `E2E-4[89]\|E2E-5[01]` | 55 |
| `FC-01\|HAMM-00\|HANG-00\|TICT-00\|AMAZ-00\|LIFE-00\|DHRY-00\|FFT-00\|WKDAY-00` | 48 |

Snapshot tag census (substring counts, not claim counts, measured 2026-11-15): ACCEPTED
887, FALSIFIED 236, PROPOSED 212, CORRECTION 33, SUPERSEDED 19, `my-gap` 134,
`dr-refuses` 68, `unmeasured` 82.

## Errata and reference corrections

Traceable erratum (operator decision D6: committed scientific evidence is NOT rewritten):
the following three paths were recorded WRONG inside `spec/lab-evidence/e2e54/PLAN.md`
(3 matching lines, verified present 2026-11-15) and **stand unmodified there** — this note
is the correction record; no scientific conclusion changes:

| Wrong path (as recorded) | Actual path |
|---|---|
| `ocaml/lib/hir_build.ml` | `ocaml/hir/hir_build.ml` |
| `ocaml/bin/pli80hir.ml` | `ocaml/hir/pli80hir.ml` |
| `ocaml/lib/backend.ml` | `ocaml/hir/backend.ml` |

Additionally: `research/minimal-baseline/README.md` (one mention in the archived
pre-2026-11-15 LEARNINGS) refers to an external tree, never tracked in this repository.

## Objective-level proposals

Objective changes are operator decisions, proposed here and NEVER made silently in
`GOAL.md`. No objective change was pending as of the 2026-11-15 consolidation; any future
one is an operator decision recorded by the operator.
