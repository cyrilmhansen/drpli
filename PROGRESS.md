# PROGRESS.md — DRPLi

Manual prose wins over the managed block below it. Do not hand-edit the managed block.
This file tracks *working state*; compiler behaviour belongs to `spec/CLAIMS.md`.

## Current phase

**NO CAMPAIGN OPEN.** E2E-54 (P1-m4, P2-DIFF-4, P2-DIFF-5) is CLOSED; the named instances
`drpli-p2-diff5` and `drpli-p1-m4-early-return` are sealed under `.pi-handoff/instances/`.
Awaiting an operator brief. Before the 2026-11-15 consolidation the live heading here still
read "E2E-53 CAMPAIGN OPEN" (2026-11-08) — a stale-handoff artefact; the git commits below
are the authority, not that heading.

## Completed

Newest first. Every row restates what the named commit recorded; it is not a fresh
measurement — rely on the named evidence, never on this table alone.

| Campaign | Closed at | Result (as recorded) | Evidence |
|---|---|---|---|
| E2E-54/P1-m4 | `f2bb784c` (2026-11-15) | early-RETURN classifier + terminating-arm join; 18 measured-first pins `hir/mir-ret-expected/*`; dual runner 14/14 BOTH-PASS, 57→67 checks, 45→53 controls rejected; third full frozen panel 14 rc 0; H1/H2/H3 CONFIRMED | `spec/lab-evidence/e2e54/{PLAN,RESULTS}.md` §P1-m4.*; `docs/architecture/backend-boundary.md` §7-17; sealed instance |
| E2E-54/P2-DIFF-5 | `28c7cfe3` (2026-11-14) | branch-condition refinement of the return-summary If join; DIF07/DIF08 differential; 20 moved literals | §P2-DIFF-5; sealed instance `8869644b` |
| E2E-54/P2-DIFF-4 | `e65c9c31` (2026-11-14) | call-site specialization differential DIF05/DIF06; twice-green panel; five falsifications recorded | §P2-DIFF-4; arch §7-15 |
| E2E-54/P1-m0…m3c | 2026-11-09…11 (e.g. m3c `5d8d2a4a`) | MIR/numerics seam rounds, incl. one STOP-and-attribute resolved by pre-registered amendment | §P1-m*, sealed/historical evidence |
| FC-01 corpus | 2026-11-03 | 8 adapted historical programs; programs 1–6 landed; DHRY-00 PASS; FFT-00 PASS → corpus COMPLETE 8/8; HAMM-00 rev1 `my-gap` FAIL recorded (later resolved — see E2E-51) | `docs/functional-results.md` §§ 5–15 |
| E2E-51/P1 | `4468a9c` (2026-11-04) | FIXED BINARY variable-divisor DIV gap RESOLVED — claims C353–C355, 12/12 bank goldens byte-exact at close, gate 1186/0 | `spec/lab-evidence/e2e51-p1/`; `docs/functional-results.md` § 16 |
| E2E-51/P2 | `52f9a54` (2026-11-04) | HAMM-00 rev2 reference-model derivation fix; six-stage lane-B PASS, double-run byte-equal | `a21a586`; `docs/functional-results.md` § 17 |
| E2E-53 | 2026-11-08 | coverage expansion campaign, 1,312-specimen baseline | `spec/lab-evidence/e2e53/PLAN.md` |
| E2E-52/P3 (LOAN2) | CLOSED at [C377] | progressive closure; `artefacts/LOAN2.PLI` whole-file byte-exact | `spec/lab-evidence/e2e52-p3/` |
| E2E-49/P1…P4, E2E-50/P1,P2 | 2026-11-01…02 | compare/relation law families; functional foundation; gate 1174/0 era | `docs/history/*-closed.md` archives |

## Pending

See `## Blockers` — the open scientific backlog. Nothing there is automatically
authorized. Infrastructure note: renewal policy and caps live ONLY in
`handoff.config.json`; this file quotes no numbers.

## Verified evidence

`tools/e2e_gate.py` (compile tier) is the repository gate. Round evidence:
`spec/lab-evidence/<round>/{PLAN,RESULTS}.md`; goldens `golden/**`; claims `spec/CLAIMS.md`
(203 headers / ends C380, re-verified 2026-11-15). Runtime/link-run regression is delegated
to the external `rune-ci` Buildbot (`spec/notes/rune-ci-external-gate.md`); existing CI
results validate new corpus programs only if those tests are explicitly included there.
Full pre-consolidation detail: `docs/history/legacy-root-2026-11-15/` — grep by campaign id,
claim id or commit sha; never read whole.

## Blockers

Nothing is half-edited at this boundary; every item below is recorded evidence, not a
guess. These are OPEN BACKLOG items, **not authorizations**: each needs its own
pre-registered, operator-briefed round. **Missing evidence is the limit, never a licence to
guess** (`PROTOCOL.md` #4).

- **LOAN2 prescan `my-gap` (open backlog).** `variable i declared with conflicting kinds;
  decimal pool prescan needs one unambiguous type map [TBD]`. Cause measured:
  `ocaml/lib/codegen.ml:16065-16090` builds ONE global `pd_vars` name→vkind map while LOAN2
  declares `i` `fixed decimal(4,2)` (L32) and `fixed bin` (L211). DR accepts (goldens
  `golden/first/LOAN2`, `golden/first8080u/LOAN2`). Fix is a design change (≈18
  `cx.pd_vars` sites; prescan runs without statement context) and needs its own measured
  plan. Do not start it on faith.
- **CREATE is not byte-exact.** Measured blocker: the front-end `%include` gap
  (`ocaml/bin/pli80c.ml` never expands INCLUDE; `spec/lab-evidence/e2e48-p2c/RESULTS.md`
  line 107: "the blocker stays the front-end `%include` gap"). Do NOT implement unmeasured
  shapes from the `[TBD]` list in that RESULTS §3.
- **`spec/lab-evidence/e2e49-p4/RESULTS.md` §3 remainders** (plus surviving P1/P2/P3/P2e §3
  entries) stay named refusals until a pre-registered round measures them: `?SCCCM` runtime
  semantics; STORE value/target shapes; literal-vs-literal relations; BASED members in a
  condition; fixed-member truthiness; `<>`/`><`; `&`/`|` composition; `^( )` over a relation
  with a literal; bare spellings under a relation; the equal-attribute `>` collapse; `^=`
  over a ladder; over-extent in INITIAL/STORE; bare `-0`; runtime length rewrite;
  empty-varying PUT output; PUT EDIT of a bit item.
- **E2E-50/P2 functional axis** (measured, recorded; no byte-tier effect): Lane-B ASSERT
  framing F1 (harness anchor law) and F2 (DR PLILIB 79-col print-wrap); the free core cannot
  host PLILIB programs (BDOS 25 first call, measured; census UNMEASURED); Package-A
  licensing = operator decision. Details `spec/lab-evidence/e2e50-p2/REPORT.md` §2/§4/§5.

Historical note (superseded, NOT blockers): the FC-01-era variable-divisor DIV `my-gap` was
RESOLVED by E2E-51/P1 (claims C353–C355; `docs/functional-results.md` § 16 "DIV blocker
GONE"), and the HAMM-00 rev2 *derivation fix* LANDED as E2E-51/P2 (§ 17, PASS 2026-11-04).
The old rev2 *subtraction-loop division workaround* is explicitly OBSOLETE — never propose
or implement it.

## Requires operator adjudication

- Whether the backlog items above stay in root `PROGRESS.md` or move to a named mission
  instance (the direction the project has taken since 2026-11-14).
- Pre-consolidation question, preserved: whether stale-but-historical root `## Next action`
  generations were closed — FC-01 says "corpus complete" while the old `## Current phase`
  still read E2E-53 OPEN. The 2026-11-15 consolidation resolved the document layout; the
  adjudication point itself (instance vs root for future work) remains the operator's.

## Next action

**NONE — STOP AND AWAIT THE NEXT OPERATOR BRIEF.** Same STOP as `HANDOFF.md` `## Next
action`, which is the single authoritative copy; this heading resumes nothing, authorizes
nothing, and opens no campaign.
<!-- guard:begin checkpoint -->
checkpoint-schema: 3
checkpoint-generation: 853
checkpoint-id: g853-e0525a26995a
checkpoint-kind: manual
content-delta: new
readiness: attested
guard-level: 0
checkpointed: 2026-11-15T11:37:05.486Z
source-goal: 730790b648a1e1d14b76243cfe8bc17eea2ba9cd8527f204f9c8d4dbcc527c9d
source-progress: e23cc3b174ae2f911ce245b5390a2d7c44dad96e5d1f112b438ac1f2e91d4820
source-handoff: ffbdf0927f517e193c71992946a30921c2207f66e40a568d93d1155e0fee9893
source-learnings: 0b2a256c3697820a413f66896b59b68d01807550623ae42704dd164119daea9e
source-config: 43186947fdaf3f3b9f425f8ce1b144a8227ce1d7bec2b7aeafb32e9f0572dea8
next-action: **NONE — STOP AND AWAIT THE NEXT OPERATOR BRIEF.** E2E-54 is closed, every named instance
is sealed, and the 2026-11-15 root-document consolidation is complete. §P2-DIFF-4.10 and
§P1-m4.11/§P1-m4.12-5 make STOP binding: any extension (more programs, deeper narrowing,
path feasibility, the `decimal_int ""` defect, the `<=`/`LINE` subset, any new compiler
slice, or any item in `PROGRESS.md` `## Blockers`) requires a NEW operator brief. Do not
open work from this file.
readiness-by: session:01a1dee2-4215-71d9-8b5e-4fec0e159dfc
readiness-at: 2026-11-15T11:37:05.491Z
readiness-checkpoint: g853-e0525a26995a
<!-- guard:end checkpoint -->
