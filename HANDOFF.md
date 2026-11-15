# HANDOFF.md — DRPLi

Manual prose wins over the managed block below it. Do not hand-edit the managed block.
This file is the recovery entry point: exactly ONE active `## Next action` at level 2.

## Recovery instructions

Lean recovery, in order: (1) this file's `## Next action`; (2) `PROGRESS.md` `## Current
phase`; (3) `spec/CLAIMS.md` — only the claim ids your task cites, never the whole ledger;
(4) the specific evidence for the next action under `spec/lab-evidence/<round>/`. Validate
the checkpoint with `/handoff verify`; a STALE checkpoint is not authoritative — re-read git
log + ledger. `PROTOCOL.md` is binding before any unfamiliar scientific procedure. The
repository outranks any document in it.

Standing operator constraints (unchanged): ZERO oracle unless a brief authorizes it;
`handoff.config.json` NEVER staged; explicit-path commits only; no push; scratch never
committed; `eval "$(opam env)"`; `LC_ALL=C`; capture rc DIRECTLY (no pipeline `$?`); never
batch build with tests; `mirsumtest` from the REPO ROOT; `grep -c $'\x08'` MUST be 0 after
any scripted durable write.

Current authority is the live root files plus `spec/`. Mission work from 2026-11-14 ran in
**sealed named instances**, not here:
`.pi-handoff/instances/drpli-p2-diff5/` (closed, `g13-54112f90ed29`) and
`.pi-handoff/instances/drpli-p1-m4-early-return/` (closed, `g9-b25a63ffa794`). Read those
directories directly — they are small. Named instances remain optional; no sealed instance
is automatically active.

Archive index: everything removed from the root documents by the 2026-11-15 consolidation
is preserved verbatim and hash-pinned in `docs/history/legacy-root-2026-11-15/` (start with
its `README.md`; the procedure and measurements are `CONSOLIDATION-PLAN.md` and
`STAGE-C1-REVIEW.md` in the same directory). Earlier per-round archives:
`docs/history/README.md`. Grep historical files by campaign id, claim id or commit sha.
**Never read a historical document whole.**

## Last verified state

**Campaign E2E-54 is CLOSED; both named instances are sealed and committed. NO CAMPAIGN
OPEN.**
- E2E-54/P2-DIFF-4 closed at `e65c9c31`; guard finalize commit `bf04fafe` (g852, attested).
- E2E-54/P2-DIFF-5 closed at `28c7cfe3`; durables `f19091a4`; instance sealed at `8869644b`.
- E2E-54/P1-m4 closed at `f2bb784c` (recorded in that commit message: dual runner 14/14
  BOTH-PASS, ret-runner 27 checks, close gate rc 0 1328/1328, 190/190, 9/9, census
  16/0/25/0, prose 5 clean, coverage 149/0/0); instance sealed at `49728acc`.
- Ledger: 203 headers via `grep -cE '^## C' spec/CLAIMS.md`, ends C380 — both re-verified
  on 2026-11-15 at consolidation time; UNMOVED by the three closes. The gate figures above
  are the recorded measurements of the named commits; the consolidation did not and cannot
  re-run them (documentary stage only).
- The 2026-11-15 consolidation (Stage B snapshot `bc7fd132`/`2e62e0fb`, Stage C1 review
  `f3041ce8`, Stage C2 application) replaced the oversized root HANDOFF/PROGRESS/LEARNINGS
  with these compact documents; the originals are preserved byte-for-byte in
  `docs/history/legacy-root-2026-11-15/`.
- Working tree: infra dirty files (`.pi/`, `.agents/`, `handoff.config.json`, staged
  `scripts/durable_edit.py`) plus ignored historical evidence remain uncommitted by design.

## Unfinished operations

- No documentary task is pending: Stage C2 completes the 2026-11-15 consolidation per
  `docs/history/legacy-root-2026-11-15/CONSOLIDATION-PLAN.md`.
- Open science obligations are listed in `PROGRESS.md` `## Blockers` (LOAN2 prescan,
  CREATE `%include`, E2E-49/P4 §3 remainders). They are unresolved, NOT closed by this
  consolidation, and NOT automatically authorized work — each needs its own operator brief.

## Next action

**NONE — STOP AND AWAIT THE NEXT OPERATOR BRIEF.** E2E-54 is closed, every named instance
is sealed, and the 2026-11-15 root-document consolidation is complete. §P2-DIFF-4.10 and
§P1-m4.11/§P1-m4.12-5 make STOP binding: any extension (more programs, deeper narrowing,
path feasibility, the `decimal_int ""` defect, the `<=`/`LINE` subset, any new compiler
slice, or any item in `PROGRESS.md` `## Blockers`) requires a NEW operator brief. Do not
open work from this file.

## Discoveries not yet incorporated

- Root `HANDOFF.md` was duplicated wholesale (lines 74–3958 ≡ 3961–7845, offset 3887). Two
  manual `## Next action` headings made the guard's `sectionBody()` ambiguous (it demands
  exactly one match), and `stripManagedSection` strips only the FIRST block — so the g852
  attestation provably covered the duplicated tail including the stale g844 orphan. That is
  the measured mechanism of the permanent staleness, not block corruption. Details:
  consolidation plan §0.1; lessons L-004/L-007 in `LEARNINGS.md`.
<!-- guard:begin checkpoint -->
checkpoint-schema: 3
checkpoint-generation: 853
checkpoint-id: g853-e0525a26995a
checkpoint-kind: manual
content-delta: new
readiness: attested
status: checkpoint (guard level 0, remaining ~49524, session 01a1dee2-4215-71d9-8b5e-4fec0e159dfc)
checkpointed: 2026-11-15T11:37:05.486Z
source-goal: 730790b648a1e1d14b76243cfe8bc17eea2ba9cd8527f204f9c8d4dbcc527c9d
source-progress: e23cc3b174ae2f911ce245b5390a2d7c44dad96e5d1f112b438ac1f2e91d4820
source-handoff: ffbdf0927f517e193c71992946a30921c2207f66e40a568d93d1155e0fee9893
source-learnings: 0b2a256c3697820a413f66896b59b68d01807550623ae42704dd164119daea9e
source-config: 43186947fdaf3f3b9f425f8ce1b144a8227ce1d7bec2b7aeafb32e9f0572dea8


readiness-by: session:01a1dee2-4215-71d9-8b5e-4fec0e159dfc
readiness-at: 2026-11-15T11:37:05.491Z
readiness-checkpoint: g853-e0525a26995a
### Last verified state
guard level 0; checkpoint requested (finalize: Stage C2 consolidation applied and committed (ad6532db); root docs compacted, originals hash-pinned in docs/history/legacy-root-2026-11-15/; no campaign open — STOP and await operator brief; documentary stage only, no compiler/oracle/gate run, no push.)

### Unfinished operations
- (none recorded)

### Next action
**NONE — STOP AND AWAIT THE NEXT OPERATOR BRIEF.** E2E-54 is closed, every named instance
is sealed, and the 2026-11-15 root-document consolidation is complete. §P2-DIFF-4.10 and
§P1-m4.11/§P1-m4.12-5 make STOP binding: any extension (more programs, deeper narrowing,
path feasibility, the `decimal_int ""` defect, the `<=`/`LINE` subset, any new compiler
slice, or any item in `PROGRESS.md` `## Blockers`) requires a NEW operator brief. Do not
open work from this file.

### Guard notes
Stage C2 consolidation applied and committed (ad6532db); root docs compacted, originals hash-pinned in docs/history/legacy-root-2026-11-15/; no campaign open — STOP and await operator brief; documentary stage only, no compiler/oracle/gate run, no push.
<!-- guard:end checkpoint -->
