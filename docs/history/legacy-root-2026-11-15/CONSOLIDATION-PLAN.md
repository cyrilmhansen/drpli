# CONSOLIDATION-PLAN — legacy root HANDOFF / PROGRESS / LEARNINGS

**STATUS: PLAN ARTIFACT ONLY. This document is not an authorization to apply anything.**
No active root document was modified in Stage B. Execution requires explicit operator
approval (Stage C).

Prepared at HEAD `bc7fd132b087c95604ca400d9403f51435aed990` (snapshot commit), snapshot HEAD
`49728acce6d5964c45dfe6fa4bd1bfbbe9883ccc`, checkpoint `g852-54fe9fceab22`, legacy project
mode, mission instance **drpli-p2-diff5 sealed** and **drpli-p1-m4-early-return sealed**.

---

## 0. Why this plan is different from the brief's assumptions

The Stage B brief carried four assumptions. Three are confirmed; **two numbers are wrong and
one causal presumption is refuted**. Every measurement below is reproducible and was obtained
read-only (`audit --json`, bounded Python). Nothing here presumes a cause.

| Brief said | Measured | Verdict |
|---|---|---|
| HANDOFF 1.91 MB / PROGRESS 1.35 MB / LEARNINGS 1.79 MB | 1,905,931 / 1,353,945 / 1,793,045 B | CONFIRMED |
| combined managed blocks 842,167 B | **1,264,269 B** (three blocks, both marker pairs inclusive; Stage B reported 1,264,089 — 180 B basis difference; re-measure at C2) | UNDERCOUNTED — audit sees only HANDOFF's *first* block |
| checkpoint g852, attested | g852 attested **and** a second, orphaned **g844 (auto, unattested)** block in HANDOFF | CONFIRMED + more severe |
| duplicate `## Next action` at 2449 / 4984 | raw lines **2449 / 6336** (audit numbers are block-stripped) | CONFIRMED (line basis differs) |
| duplicate `## Unfinished operations` at 2560 / 5095 | raw lines **2560 / 6447** | CONFIRMED (same) |
| "do not presume the generation count caused the large blocks" | **Refuted as a cause.** Generation 852 contributes 27 bytes of metadata. The blocks are ~420 KB because of a single `### Next action` payload of **419,843 B** | CORRECT INSTINCT, now proven |

### 0.1 The actual causal chain (proven, not presumed)

1. **`HANDOFF.md` contains two whole document copies.** Lines 74–3958 are reproduced at
   lines 3961–7845 (offset exactly 3887 lines). Of the 3,885 line-pairs, **1,328 differ only
   inside the managed checkpoint blocks** (g852 vs g844 metadata) and **exactly 1 prose line
   differs** (`SUPERSEDED-BY-ABOVE: ` prefix present in copy 1, absent in copy 2). The
   redundant tail is **950,249 B = 49.9% of the file**. Inside it, the manual-prose body
   (copy-1 lines 1653–2608 ↔ copy-2 lines 5540–6495) is **byte-identical**, SHA-256
   `e2fc26f02e1037db…` both sides, 85,431 B.
2. Because copy 2 carries a *stale* checkpoint generation, `HANDOFF.md` now has **two
   `guard:begin checkpoint` blocks**.
3. The guard's `stripManagedSection()` (checkpoint.ts:735) removes only the **first**
   occurrence. So the g852 attestation hash `source-handoff: 5da7fb06…` provably covers the
   duplicated document *including the stale g844 block* — verified: `sha256(strip1(HANDOFF)
   .rstrip()) == 5da7fb0608d11981dd79023a9352d3a66916b868cbfa3a9d4fa246293341c0b5`.
4. The guard's `sectionBody()` (checkpoint.ts:1583-1589) **returns `undefined` unless exactly
   one heading matches** (`if (matches.length !== 1) return undefined`). HANDOFF has **two**
   `## Next action` prose headings → `proseNext` is `undefined` → verify reports
   *"next action exists only inside the managed block"* → renewal is **not authorized**. This
   is the measured mechanism of the current stale state, not a corruption of the block.
5. The block's `### Next action` payload (419,843 B, 1,158 non-blank lines) is **100%
   redundant with live prose**: 1,156 lines appear verbatim in HANDOFF manual prose, only 2
   lines are unique to the block. PROGRESS's `next-action:` field holds the same payload
   (419,965 B). **The block is large because the prose it snapshots is large.**

**Consequence, and the single most important line in this plan:** the managed blocks cannot be
shrunk by editing them. They shrink *automatically* on the next guard-owned refresh **once the
prose they derive from is unique and small**. Fixing duplication is therefore a *precondition*
for checkpoint compaction, not an independent cosmetic cleanup.

---

## 1. Exact source files and proposed destination files

All destinations are inside the already-committed snapshot directory or the existing root.
No new framework, no new tool, no new directory layout.

| # | Source (live) | Destination / disposition | Mechanism |
|---|---|---|---|
| S1 | `HANDOFF.md` (1,905,931 B) | rewritten root `HANDOFF.md` (target ≤ 12 KB total incl. one refreshed block) | atomic whole-file replace (§6), draft §3.1 |
| S2 | `PROGRESS.md` (1,353,945 B) | rewritten root `PROGRESS.md` (target ≤ 14 KB incl. refreshed block) | atomic whole-file replace, draft §3.2 |
| S3 | `LEARNINGS.md` (1,793,045 B) | rewritten root `LEARNINGS.md` as an **index** (target 12–15 KB) | atomic whole-file replace, draft §3.3 |
| S4 | superseded prose removed from S1/S2/S3 | **already archived**: `docs/history/legacy-root-2026-11-15/{HANDOFF,PROGRESS,LEARNINGS}.md`, committed at `bc7fd132` | done in Stage A/B; no further move needed |
| S5 | — | `docs/history/README.md` gains **one table row** pointing at this snapshot (preserve existing rows verbatim) | `durable_edit.py archive-apply`-style exact-section append, or a manual single-line edit |

Explicitly **not** touched by any stage: `GOAL.md`, `AGENTS.md`, `PROTOCOL.md`,
`spec/CLAIMS.md`, `spec/*.tsv|txt`, `golden/**`, `ocaml/**`, `hir/**`, `tools/**`,
`oracle/**`, `artefacts/**`, `manuals/**`, `extracted/**`, `references/**`,
`thirdparty/**`, `.pi-handoff/**` (sealed instances), `handoff.config.json`,
`scripts/durable_edit.py`, `.pi/**`.

Note S4 is what makes this plan cheap: unlike the 2026-10-31/11-02 consolidations
(`docs/history/README.md`), which extracted *per-section* close archives, here the entire
original document is already preserved byte-for-byte. No section-by-section extraction or
per-line re-verification of destinations is required beyond the completeness sweep in §7.

---

## 2. SHA-256 preconditions

Re-run `python3 scripts/durable_edit.py hash <file>` at the moment of application and refuse
on any mismatch. Snapshot hashes are permanent; live hashes are a moving target and are
restated below as of `49728acc`.

**Archive (immutable precondition — must never change):**

| Path | Required SHA-256 |
|---|---|
| `docs/history/legacy-root-2026-11-15/HANDOFF.md` | `7364774e58b41c85355562680ce2da534c4831136eedc4077109b45a8440276f` |
| `docs/history/legacy-root-2026-11-15/PROGRESS.md` | `81bb20cd18a56f2312f2440880720527de6ac34783daa922f53d3525613ecad6` |
| `docs/history/legacy-root-2026-11-15/LEARNINGS.md` | `786ce1a1679a875981f1502370a24ff3efe2eaf45f56764c6033b8bba6dc558c` |

**Live source (precondition at Stage C start):** identical to the three values above, because
the root files were verified byte-equal to the snapshot at Stage B. If any differs, the
snapshot is no longer a faithful capture of what is being replaced → **STOP §8.1**.

**Guard attestation preconditions (from the g852 block):**
- `source-handoff` = `5da7fb0608d11981dd79023a9352d3a66916b868cbfa3a9d4fa246293341c0b5`
- `source-progress` = `e0fd808334a044e5a1ab008a99e20882fa7d291dfe8503de8e70cda24865182a`
- `source-learnings` = `786ce1a1679a875981f1502370a24ff3efe2eaf45f56764c6033b8bba6dc558c`
- reproducing `source-handoff` requires the guard's own law: strip **first** checkpoint block,
  right-strip whitespace, SHA-256 over UTF-8 bytes.

**Structural preconditions (line/byte anchors, HANDOFF.md):**

| Anchor | Required value |
|---|---|
| total lines | 7845 |

(C1 note: 7845 is the Python `split('\n')` element count — the file has 7,844 `wc -l` lines and
no content after the final newline. State the basis in the C2 precondition script.)
| `<!-- guard:begin checkpoint -->` | lines 2609 and 6496 |
| `<!-- guard:end checkpoint -->` | lines 3960 and 7844 |
| copy-1 prose body sha (L1653–2608) | `e2fc26f02e1037db…` |
| copy-1 ↔ copy-2 differing line-pairs | 1329 (1328 in-block + L74) |
| redundant tail to delete | lines 3961–7845 (950,249 B) |

---

## 3. Proposed new document structure and full draft contents

Three properties are mandatory in all drafts:
(a) **exactly one** `## Next action` heading, (b) **exactly one** `## Unfinished operations`
heading, (c) the guard's required section set per `checkpoint.ts:670-675` (`REQUIRED_SECTIONS`,
verified C1). Omitting any of these, or duplicating one, fails `durable-files-valid` (a
**blocking** readiness check, `checkpoint.ts:1338-1341`; `validateFile` demands each required
heading appear **exactly once** in manual prose, and `headingMatchesTitle` (`checkpoint.ts:1568-
1577`) counts suffixed headings like `## Next action (E2E-…)` as matches):

- **handoff**: `## Recovery instructions`, `## Last verified state`, `## Unfinished operations`,
  `## Next action`, `## Discoveries not yet incorporated` — draft §3.1 satisfies this.
- **progress** (C1 correction — this supersedes §4's claim that the guard requires `## Next
  action` only in HANDOFF): `## Current phase`, `## Completed`, `## Pending`,
  `## Verified evidence`, `## Blockers`, `## Next action` — **each exactly once**. The current
  PROGRESS fails (9 `## Next action` occurrences); draft §3.2 as written also **fails**
  (no `## Next action`, no `## Completed`, no `## Blockers`). **MANDATORY C2 FIX:** the applied
  PROGRESS must carry exactly one `## Next action` (STOP semantics per D4 below, mirroring
  HANDOFF), rename/retain a single `## Completed` (milestone table belongs here) and a single
  `## Blockers` (= the Open obligations content), keep `## Pending` + `## Verified evidence` +
  `## Current phase`, each once.
- **learnings**: `## Accepted`, `## Proposed`, `## Falsified or superseded` — each exactly once.
  Current LEARNINGS fails (`## Accepted` ×14, `## Proposed` ×2); draft §3.3 as written also
  **fails** (none of the three). **MANDATORY C2 FIX:** organize the D1 index under exactly one
  heading of each required name (the L-001…L-007 table's rows split by classification into
  `## Accepted`; a short `## Proposed` stub naming open proposals; `## Falsified or superseded`
  carrying L-003 etc.). The pointer-only/index design of D1 is preserved; only the heading
  scaffold changes.
- **goal** (untouched): `## Objective`, `## Acceptance criteria` — verified ×1 each, GOAL.md
  stays valid.

The D4 Next action body must not consist solely of `none`/`TBD`/`N/A`/`(none)`: the guard's
`PLACEHOLDER_RE` (`checkpoint.ts:1277`) rejects that; a full sentence such as
`NONE — STOP AND AWAIT THE NEXT OPERATOR BRIEF. …` passes (verified C1: the regex is
anchored full-string, the draft body is far longer).

Draft text is written to be honest: it restates only what commits/evidence record, with
pointers, and marks every figure that Stage C must re-measure as `[REVERIFY]`. It invents no
scientific conclusion (PROTOCOL #4).

### 3.1 `HANDOFF.md` (target ~3 KB manual prose; guidance 2–4 KB)

```markdown
# HANDOFF.md — DRPLi

Manual prose wins over the managed block below it. Do not hand-edit the managed block.

## Recovery instructions

Lean recovery, in order: (1) this file's `## Next action`; (2) `PROGRESS.md` live heading;
(3) `spec/CLAIMS.md` — only the claim ids your task cites, never the whole ledger; (4) the
specific evidence for the next action under `spec/lab-evidence/<round>/`. Validate the
checkpoint with `/handoff verify`; a STALE checkpoint is not authoritative — re-read git
log + ledger. `PROTOCOL.md` is binding before any unfamiliar scientific procedure.
The repository outranks any document in it.

Standing operator constraints (unchanged): ZERO oracle unless a brief authorizes it;
`handoff.config.json` NEVER staged; explicit-path commits only; no push; scratch never
committed; `eval "$(opam env)"`; `LC_ALL=C`; direct rc; never batch build with tests;
`grep -c $'\x08'` MUST be 0 after any scripted durable write.

Current authority is the live root files plus `spec/`. Mission work from 2026-11-14 onward
runs in **sealed named instances**, not here:
`.pi-handoff/instances/drpli-p2-diff5/` (closed, `g13-54112f90ed29`) and
`.pi-handoff/instances/drpli-p1-m4-early-return/` (closed, `g9-b25a63ffa794`). Read those
directories directly — they are small.

History: everything removed from this file by the 2026-11-15 consolidation is preserved
verbatim and hash-pinned in `docs/history/legacy-root-2026-11-15/` (README + CONSOLIDATION-
PLAN.md). Grep it by campaign id, claim id or commit sha. Do NOT read it whole.

## Last verified state

**Campaign E2E-54 is CLOSED; both named instances are sealed and committed.**
- E2E-54/P2-DIFF-4 closed at `e65c9c31`; guard finalize `bf04fafe` (g852, attested).
- E2E-54/P2-DIFF-5 closed at `28c7cfe3`; durables `f19091a4`; instance sealed at `8869644b`.
- E2E-54/P1-m4 closed at `f2bb784c` (H1/H2/H3 CONFIRMED; dual runner 14/14 BOTH-PASS;
  ret-runner 27 checks; close gate rc 0: 1328/1328, 190/190, 9/9, census 16/0/25/0, prose 5
  clean); instance sealed at `49728acc`.
- Ledger 203 claims / ends C380, UNMOVED by all three closes. Gate figures above are the
  recorded measurements; re-measure before relying on them `[REVERIFY]`.
- Working tree: infra dirty files (`.pi/`, `.agents/`, `handoff.config.json`, staged
  `scripts/durable_edit.py`) plus historical ignored evidence remain uncommitted by design.

## Unfinished operations

- The 2026-11-15 consolidation is **awaiting operator approval for Stage C**; see
  `docs/history/legacy-root-2026-11-15/CONSOLIDATION-PLAN.md` §8 for STOP conditions.
- Open science obligations are listed in `PROGRESS.md` → `## Open obligations`; they are
  unresolved, NOT closed by this consolidation.

## Next action

**NONE — STOP AND AWAIT THE NEXT OPERATOR BRIEF.** E2E-54 is closed and every named
instance is sealed. §P2-DIFF-4.10 and §P1-m4.11/§P1-m4.12-5 make STOP binding: any extension
(more programs, deeper narrowing, path feasibility, the `decimal_int ""` defect, the
`<=`/`LINE` subset, any new compiler slice) requires a NEW operator brief. Do not open work
from this file. If the operator approves the consolidation instead, execute Stage C exactly
as specified in the plan above — documentary maintenance only, no compiler/oracle/gate runs.

## Discoveries not yet incorporated

- Root `HANDOFF.md` was duplicated wholesale (lines 74–3958 ≡ 3961–7845), which is what made
  `sectionBody("## Next action")` ambiguous and the checkpoint permanently stale. Mechanism
  and measurements: consolidation plan §0.1. Worth checking in `PROGRESS.md` history.
```

### 3.2 `PROGRESS.md` (target ~6–8 KB manual prose; guidance 3–8 KB)

```markdown
# PROGRESS.md — DRPLi

Manual prose wins over the managed block below it. Do not hand-edit the managed block.
This file tracks *working state*; compiler behaviour belongs to `spec/CLAIMS.md`.

## Current phase

**NO CAMPAIGN OPEN.** E2E-54 (P1-m4, P2-DIFF-4, P2-DIFF-5) is CLOSED; the named instances
are sealed under `.pi-handoff/instances/`. Awaiting an operator brief. Before this
consolidation the live heading here still read "E2E-53 CAMPAIGN OPEN" (2026-11-08) — a
stale-handoff artefact; the git commits below are the authority, not that heading.

## Verified recent milestones

Newest first. Every row is a recorded measurement, not a summary judgement; re-run the
named gate to rely on a figure `[REVERIFY]`.

| Campaign | Closed at | Result (as recorded) | Evidence |
|---|---|---|---|
| E2E-54/P1-m4 | `f2bb784c` | early-RETURN classifier + terminating-arm join; 18 measured-first pins `hir/mir-ret-expected/*`; dual runner 14/14 BOTH-PASS, 57→67 checks, 45→53 controls rejected; third full frozen panel 14 rc 0 | `spec/lab-evidence/e2e54/{PLAN,RESULTS}.md` §P1-m4.*; arch §7-17 |
| E2E-54/P2-DIFF-5 | `28c7cfe3` | branch-condition refinement of the return-summary If join; DIF07/DIF08 differential; 20 moved literals | §P2-DIFF-5; sealed instance |
| E2E-54/P2-DIFF-4 | `e65c9c31` | call-site specialization differential DIF05/DIF06; twice-green panel; five falsifications recorded | §P2-DIFF-4; arch §7-15 |
| E2E-54/P1-m0…m3c | 2026-11-09…11 | MIR/numerics seam rounds, incl. one STOP-and-attribute resolved by pre-registered amendment | §P1-m*, sealed/historical evidence |
| FC-01 corpus | 2026-11-03 | 8 adapted historical programs; programs 1-6 landed, DHRY-00 PASS, FFT-00 PASS → corpus complete; HAMM-00 rev1 `my-gap` FAIL recorded | `docs/functional-results.md`, `build/fc01/corp1..corp8` (ignored) |
| E2E-53 | 2026-11-08 | coverage expansion campaign, 1,312 specimens baseline | `spec/lab-evidence/e2e53/PLAN.md` |
| E2E-52/P3 (LOAN2) | CLOSED at [C377] | progressive closure | `spec/lab-evidence/e2e52-p3/` |
| E2E-51/P1 | — | three arms, 12/12 goldens byte-exact | `spec/lab-evidence/e2e51-p1/` |
| E2E-49/P1…P4, E2E-50/P1,P2 | 2026-11-01…02 | compare/relation law families; gate 1174/0 era | `docs/history/*-closed.md` archives |

## Open obligations (ACTIVE — not closed by this consolidation)

- **LOAN2 prescan `my-gap`.** `variable i declared with conflicting kinds; decimal pool
  prescan needs one unambiguous type map [TBD]`. Cause measured
  (`codegen.ml:12460-12490` builds ONE global `pd_vars` name→vkind map; LOAN2 declares `i`
  `fixed decimal(4,2)` at 32 and `fixed bin` at 211). DR accepts (golden exists). Fix is a
  design change (~15 `List.assoc_opt … cx.pd_vars` sites, prescan runs without statement
  context) and needs its own measured plan. Do not start it on faith.
- **CREATE is not byte-exact.** Measured blocker remains the front-end `%include` gap
  (`pli80c.ml` never expands INCLUDE). Do NOT implement unmeasured shapes from the `[TBD]`
  list in RESULTS §3.
- **`spec/lab-evidence/e2e49-p4` RESULTS §3 remainders** (plus surviving P1/P2/P3/P2e §3
  entries) stay named refusals until a pre-registered round measures them: `?SCCCM` runtime
  semantics; STORE value/target shapes; literal-vs-literal relations; BASED members in a
  condition; fixed-member truthiness; `<>`/`><`; `&`/`|` composition; `^( )` over a relation
  with a literal; bare spellings under a relation; the equal-attribute `>` collapse; `^=`
  over a ladder; over-extent in INITIAL/STORE; bare `-0`; runtime length rewrite;
  empty-varying PUT output; PUT EDIT of a bit item. **Missing evidence is the limit, never a
  licence to guess** (PROTOCOL #4).
- **HAMM-00 rev2** (subtraction-loop workaround for variable DIV) remains **PROPOSED, never
  executed**.
- **Runtime/link-run regression** is delegated to the external `rune-ci` Buildbot
  (`spec/notes/rune-ci-external-gate.md`); existing CI results validate new corpus programs
  only if those tests are explicitly included there.

## Requires operator adjudication

- Whether the ACTIVE obligations above should stay in root `PROGRESS.md` or be promoted to a
  named mission instance (the direction the project has moved since 2026-11-14).
- Whether the three stale-but-historical root `## Next action` generations should be treated
  as closed, given FC-01 says "corpus complete" while `## Current phase` still read
  E2E-53 OPEN.

## Verified evidence

`tools/e2e_gate.py` (compile tier) is the repository gate. Round evidence:
`spec/lab-evidence/<round>/{PLAN,RESULTS}.md`; goldens `golden/**`; claims `spec/CLAIMS.md`
(203 / C380 as of 2026-11-15). Full pre-consolidation detail:
`docs/history/legacy-root-2026-11-15/`.

## Pending

See `## Open obligations`. Infrastructure note: renewal policy and caps live ONLY in
`handoff.config.json`; this file quotes no numbers.
```

### 3.3 `LEARNINGS.md` (target 12–15 KB; guidance 5–15 KB)

Structure: a **legend + index**, not history. Every lesson line carries its classification so
`accepted` / `proposed` / `falsified` stay distinguishable at a glance.

```markdown
# LEARNINGS.md — DRPLi

Read-only index of where lessons live. **No session must bulk-read history.** The complete
pre-2026-11-15 record is preserved verbatim in
`docs/history/legacy-root-2026-11-15/LEARNINGS.md` (SHA-256
`786ce1a1679a875981f1502370a24ff3efe2eaf45f56764c6033b8bba6dc558c`), 14,463 lines /
355 sections / 42 campaigns. Locate it by identifier:

    cd docs/history/legacy-root-2026-11-15
    grep -n "E2E-54/P2-DIFF-4\|C352\|FALSIFIED" LEARNINGS.md

## How to classify (unchanged, authoritative)

- **ACCEPTED** — measured; admissible only with oracle evidence recorded in `spec/CLAIMS.md`.
- **PROPOSED** — planned, NOT executed, NOT evidence. Never promote silently.
- **FALSIFIED** — a hypothesis/baseline/simulator shown wrong by measurement. Kept as written.
- **SUPERSEDED-BY-ABOVE** — retained for provenance per PROTOCOL #2; means "kept", not "delete".
- Difference classes: `dr-refuses` / `my-gap` / `unmeasured`. Missing evidence is never
  promoted into a DR rule; write `[TBD]`.

## Index — current, high-value lessons (live text; short)

| Id | Classification | Lesson | Where |
|---|---|---|---|
| L-001 | ACCEPTED (method) | Ledger count law: `grep -cE '^## C' spec/CLAIMS.md` == 203 counts 202 real headers + the wrapped `## CLASS;` line at CLAIMS:5080. `^## C[0-9]` (202) and `^## C[0-9]{3} ` (200) are NOT the ledger number. | snapshot §P2-DIFF-4 panel durables |
| L-002 | ACCEPTED (method) | Relative-path redirect hazard: run repo tools from the repo root; `mirsumtest` from ROOT. | snapshot |
| L-003 | FALSIFIED | "Checkpoint bloat is caused by high generation count." Measured: g852 metadata is 27 B; the bloat is one 419,843 B `### Next action` snapshot payload, 100% redundant with prose. | `CONSOLIDATION-PLAN.md` §0.1 |
| L-004 | ACCEPTED (infra) | Duplicate root headings make the guard ambiguous: `sectionBody()` requires exactly one match, else `undefined` → stale checkpoint → renewal not authorized. Keep `## Next action` unique. | plan §0.1(4) |
| L-005 | ACCEPTED | Corpus laws, all run-witnessed (FC-01): literal divisors ≤ 127 (variable DIV MEASURED refused = `my-gap`, `codegen.ml:4997-5010`); ordered-compare constants ≥ 1; strict compares (`COND.GE_LE` refused); no apostrophes; ≤ 71 cols; single-item `put list` with leading-blank separator; GET echo `L\r\r\n`; exit CRLF [C352]. A FAIL stays classified, never laundered. | snapshot FC-01 §§ |
| L-006 | ACCEPTED | mir2o/MIR laws (baked to arch §7-17): mir2o accepts post-ret code (jump-reachable real code); MIR immediates are bare decimals, `i64:k` is a MEMORY operand (SEGFAULT law); the §P1-m4.3 classifier is a SECOND guard over loop-nested RETURNs. | `docs/architecture/backend-boundary.md` §7-17 |
| L-007 | ACCEPTED | `durable_edit.py` refuses duplicated headings (`AMBIGUOUS`, exit 3) rather than guessing; `stripManagedSection` strips only the FIRST block, so a duplicated document contaminates the attestation. | plan §5 |

## Index — historical lesson bodies (grep, do not read whole)

| Campaign | Sections | Snapshot anchor (`grep -n '^## '`) |
|---|---|---|
| E2E-54/P2-DIFF-1…5 | 30+ | "E2E-54/P2-DIFF" |
| E2E-54/P1-a*, m*, mD | 60+ | "E2E-54/P1-" |
| E2E-53/* | 40+ | "E2E-53/" |
| E2E-52/P1…P3 | 50+ | "E2E-52/" |
| E2E-51, 50, 49, 48 | 90+ | "E2E-4[89]\|E2E-5[01]" |
| FC-01 corpus | ~15 | "FC-01\|HAMM-00\|HANG-00\|TICT-00\|AMAZ-00\|LIFE-00\|DHRY-00\|FFT-00" |

Counts are indicative; the snapshot is authoritative. Tag census in the pre-consolidation
snapshot: ACCEPTED 887, FALSIFIED 236, PROPOSED 212, CORRECTION 33, SUPERSEDED 19,
`my-gap` 134, `dr-refuses` 68, `unmeasured` 82 (substring counts, not claim counts).

## Handoff knowledge registry

The append-only knowledge registry currently has **no published records** (verified
2026-11-15). Publishing is an explicit, separate act and is not implied by this index.

## Objective-level proposals

Objective changes are operator decisions, proposed here and NEVER made silently in `GOAL.md`.
No objective change is pending as of this consolidation `[operator to confirm]`.
```

---

## 4. Handling duplicate headings without choosing an arbitrary occurrence

The brief demands no arbitrary pick. There is none: the occurrences are **distinguishable by
evidence**, and the discrimination is mechanical and reproducible.

**Discrimination rule (Stage C, in this order):**
1. **Block authority.** Compare `checkpoint-generation`, `checkpoint-kind` and `readiness`
   inside each `guard:begin checkpoint` block. g852 is `manual` + **attested**; g844 is `auto`
   + **unattested**. The attested, higher-generation block is authoritative; the other is an
   orphan. (Guard identity check itself reports `g852-54fe9fceab22`.)
2. **Prose authority.** Copy 1 (lines 74–2608) is the region the attestation covers. Proof:
   `sha256(stripManagedSection_first(HANDOFF).rstrip()) == source-handoff (5da7fb06…)`. Copy 2
   (3961–7845) is *inside* that hash only because it is the stale duplicate. Copy 1 additionally
   carries the `SUPERSEDED-BY-ABOVE: ` marker on its entry-19 line, which copy 2 lacks — i.e.
   copy 1's prose is the labelled, self-describing copy.
3. **Action.** Do not merge, do not interleave, do not pick "the later one because it's newer".
   **Delete the whole redundant tail (lines 3961–7845) as a single contiguous region.** It is a
   contiguous block, so a single range deletion — not a per-heading decision — removes all
   38 duplicated headings at once. After that, every level-2 heading in HANDOFF is unique and
   `sectionBody()` / `durable_edit.py` become unambiguous by construction.
4. **Nothing is lost.** Completeness sweep (§7.3) proves every line in the deleted tail is
   present in the committed snapshot, except the known 1,328 in-block metadata pairs and the
   1 prose prefix line, each individually enumerated in the plan. The g844 block's own content
   is not prose: it is guard state, which the guard will regenerate; §5 governs it.

PROGRESS.md has a related but distinct problem: **nine** `## Next action …` headings (C1
recount; lines 51, 262, 1442, 1444, 1824, 1841, 1912, 1962, 2154; 29 level-2 headings total),
(`## Next action (E2E-54/P2-DIFF-4 — CLOSED…)`, a second P2-DIFF-4 STAGE-A one, and P3-18 /
P1-m3c / P1-mD / P1-m1 / P1-m0 / P1-h / P1-a2 / P1-a1 stubs). 29 level-2 headings total.
Same rule: the authoritative live heading is the one whose campaign closes latest by **git
commit date**, not file position — that is P2-DIFF-4 CLOSED (`e65c9c31`, 2026-11-14), then
superseded in fact by P2-DIFF-5 (`28c7cfe3`) and P1-m4 (`f2bb784c`). Draft §3.2 replaces the
whole stack with **exactly one** `## Next action` in PROGRESS — a STOP/await-brief heading
matching HANDOFF (required by `REQUIRED_SECTIONS.progress`; see §3 mandatory properties).
The redundant prose is preserved in the snapshot.

---

## 5. Keeping the managed blocks untouched until a guard-owned refresh

- Stage C **never** hand-edits, truncates, reconstructs or deletes managed content by hand.
  The only permitted writer of managed blocks is the guard transaction
  (`/handoff` → `/handoff ready`, or `/handoff finalize` / `handoff_renew`).
- Sequence is mandatory: **(a)** replace manual prose, **(b)** commit prose-only, **(c)** run
  the guard refresh, **(d)** commit the guard's own write as a separate commit (project
  precedent: `bf04fafe` "guard-managed checkpoint block refresh (g852, FINALIZED): the guard's
  own finalize write … committed verbatim by explicit paths. No hand-edit, no metadata
  invented").
- **Consequence of the deletion in §4 on block 2:** deleting lines 3961–7845 removes the stale
  g844 block as a side effect of removing a prose region; that is unavoidable and legitimate,
  but Stage C must record it explicitly in the commit message rather than pretend the block
  was edited. This is a *deletion of an orphan by removing the duplicated document*, not an
  edit of managed content. If the operator prefers, Stage C can instead excise
  lines 6496–7844 and keep the duplicate prose — **operator decision §8-D3**; the plan
  recommends the single contiguous deletion.
- **g852 pair retention (D3, C1 addition):** the intact attested **g852 pair** — HANDOFF block
  at raw lines 2609–3960 (421,527 B) and PROGRESS block at raw lines 5795–7134 (420,640 B) —
  must reach the replacement files **verbatim as byte slices of the originals**, untouched,
  until the guard's own refresh regenerates them. §6.4 governs the HANDOFF slice; the same law
  applies to PROGRESS: new file = `new_prose ++ byte-slice(PROGRESS lines 5795..7134 ++
  trailing content after 7134 if any)`. No checkpoint field is ever hand-written, retyped or
  edited, in either direction.
- **Expected effect of the refresh:** once `## Next action` is unique and ~700 B,
  `sectionBody()` returns it and the rewritten block's `### Next action` payload becomes
  ~700 B instead of 419,843 B. That is how the block shrinks — through the guard, never by
  editing it. Stage C MUST measure this and must not assume it (see §7.4 for the fallback if
  the guard's persisted session bundle keeps replaying the old giant payload; if so the block
  stays ~420 KB and the only remaining lever is a **guard-side** field-retention decision,
  which is an operator/infra decision outside this documentary stage).

---

## 6. Non-destructive application, interruption and concurrency

Reusing existing primitives; **no new generic consolidation framework**.

1. **Pre-verify** (read-only): recompute all §2 hashes; `git status --porcelain` inventory;
   assert HEAD ancestry contains `bc7fd132`; assert the three archive blobs are unchanged in
   git objects (`git cat-file blob HEAD:… | sha256sum`), not just in the worktree.
2. **Draft to scratch, never in place**: write proposed content to
   `build/consolidation-2026-11-15/{HANDOFF,PROGRESS,LEARNINGS}.md.new` (ignored dir).
3. **Dry-run diff** with the tool where possible. For exact-section work use
   `durable_edit.py plan … --expect-sha256 <hash> [--check-refs]`, then `apply` with the same
   hash. **Known limitation, explicitly not bypassed:** `plan`/`apply`/`archive-*` refuse with
   `AMBIGUOUS: N exact matches … refuse (no guessing)` (exit 3) while duplicate headings exist,
   and no heading in the duplicated tail can be targeted. Measured in Stage B:
   `## Unfinished operations` → AMBIGUOUS at 2560, 6447; `## History and pointers` → AMBIGUOUS
   at 2591, 6478; and `## Recovery instructions` (the only unique heading) plans correctly and
   stops before managed content. Therefore **the whole-file replaces in §3 cannot be done with
   `durable_edit.py` and must use its atomicity law directly**: write temp file in the SAME
   directory, `fsync`, `os.replace()`. An interrupted replace leaves the original
   byte-identical. Exit-code discipline from the tool: 0 ok, 2 usage, 3 not-found/ambiguous,
   4 managed-block target, 5 hash conflict, 6 missing evidence reference, 7 io error.
4. **Order matters — de-duplicate first, then section-edit.** The safe HANDOFF sequence is:
   (i) build the new file as `new_prose` ++ `byte slice of original lines 2609..3960` (the
   g852 block, copied verbatim from the original file and **never regenerated or retyped**),
   with the redundant tail (lines 3961..7845) absent; (ii) atomic replace per §6.3; (iii) the
   §5 guard refresh. Stage C writes **new manual prose only** — it must never author managed
   content, and the surviving block reaches the new file purely as a byte slice of the
   original.
5. **Concurrency**: before each write, re-hash the target and compare with the plan's recorded
   hash (`--expect-sha256` law). Any mismatch = another writer → CONFLICT (exit 5) → STOP §8.
   Project is single-worktree; also refuse to run if `.pi-guard/` shows an active renewal in
   flight (`handoff_inspect`), and never run Stage C concurrently with `/handoff renew`.
6. **One file per commit, explicit paths only.** Never `git add -A`; `git add <explicit path>`
   then `git commit --only -m … -- <explicit paths>` (verified in Stage B that `--only` leaves
   other staged content untouched, and note `--only` requires the path to be known to git
   first).

### 6.8 Interruption between replacements — this is NOT a three-file transaction (C1, explicit)

Three `os.replace()` calls are each individually atomic; **there is no cross-file atomicity**.
An interruption (crash, ctrl-C, concurrent writer) can therefore leave 0, 1 or 2 of the three
root docs replaced. Recovery law:

1. **No commit and no guard refresh while the set {HANDOFF, PROGRESS, LEARNINGS} is mixed.**
   All three replaces complete, all §7 pre-validation passes, and only then the §5(c) guard
   refresh runs. A half-replaced state must never be committed or attested.
2. **Resume, or roll forward, deterministically:** before *each* individual replace, re-hash
   the target. A target whose hash equals its §2 pre-hash → replace it. A target whose hash
   equals the *new* file's recorded hash → already done, skip (idempotent replay). Any other
   hash → foreign writer → STOP §8.1, do not touch.
3. **Abort path:** pre-Stage-C copies are taken to `build/consolidation-2026-11-15/backup/`
   (git-ignored) before any replace; abort = `cp` back, per file, re-hash to restore the §2
   preconditions. Alternatively (once the prose commit exists) `git checkout HEAD -- <that one
   root file>` — permitted **only** for the three root docs this stage itself writes.
4. Because everything before the guard refresh is uncommitted, the recovery unit is the whole
   stage: re-running §6.1–§6.4 from the top after any interruption is always safe (each step
   is idempotent under rule 2).
7. **No gate/compiler runs.** Documentary stage only: no `dune build`, no `e2e_gate.py`, no
   cpmsim, no oracle, no LINK-80, no rune-ci. (Per AGENTS.md: infrastructure work must not run
   them.)

---

## 7. Review, refresh/attestation, reference verification, recovery-cost measurement

1. **Git diff review.** Per file: `git diff -- <path>` must show only (a) prose removal whose
   lines all appear in the snapshot, (b) prose additions. Managed bytes: verify the g852 slice
   is byte-identical before and after with `git diff --exit-code` restricted to
   `<!-- guard:begin checkpoint -->`..`<!-- guard:end checkpoint -->` (extract and compare
   before/after bytes for block 1; block 2's removal is accounted for in §5/§8-D3).
2. **Guard refresh + attestation.** `/handoff verify` → `/handoff` (refresh) →
   `/handoff ready` (attest), or `handoff_finalize`. Confirm: exactly one checkpoint block,
   `checkpoint-generation` incremented, `content-delta` reported, `readiness: attested`,
   and `next-action-recorded` = **pass** with `source: handoff-prose`. Then commit the guard's
   write separately, verbatim, explicit paths.
3. **Completeness sweep ("no line lost").** For every non-blank line deleted from the live
   files, assert membership in the snapshot. Report the count of lines not found — target 0,
   with the single known exception class (§4.2: the 1 prose line differing only by the
   `SUPERSEDED-BY-ABOVE: ` prefix, plus in-block metadata). This mirrors the earlier archive
   convention ("completeness sweep 0 unarchived lines", `docs/history/README.md`).
4. **Reference verification.** Re-run `durable_edit.py audit --root . --json` and assert
   `duplicate-active-heading` and `active-next-action-ambiguous` findings are GONE. Then run
   `--check-refs` on every new prose section (exit 6 must not occur). Apply the §B triage
   below so shorthand forms are expanded before judging. Expect the *shorthand* residuals to
   remain (they are a tool limitation, not document defects): `REF_RE` treats any `a/b.ext` as
   a path, so sibling lists (`HANDOFF.md/PROGRESS.md`, `dir.txt/summary.txt`,
   `hir.ml/hir_build.ml`, `CALL07/CALL08/CALLN9.pli`) and ranges (`H01..H05.pli`) never resolve
   literally. Do not "fix" prose to satisfy them; record them as false positives.
5. **Recovery-cost measurement.** `audit --json` → `recovery_cost_estimates` before/after,
   and `handoff_inspect` "recovery cost". Also `/handoff verify` must report
   **no stale/ambiguous findings**. **C1 correction on the renewal gate:** `.pi-guard/` holds
   no usable renewal chain state today (`handoff_inspect`: "renewal: refused
   (state-unavailable) — chain (none) 0/12"), so `handoff_renew` will stay refused; that is the
   **expected** post-condition, not a defect. Attestation must proceed via `/handoff` +
   `/handoff ready` or `handoff_finalize`, which do not need chain state. Confirm
   `next-action-recorded: pass` and `durable-files-valid: pass`. Record both the chars/4
   estimate and the tier decision.
6. **Post-consolidation size estimates (projected, to be measured):**

| File | Before | Prose target | + refreshed block | Projected total |
|---|---|---|---|---|
| `HANDOFF.md` | 1,905,931 B | 2.5–4 KB | 2–4 KB (if §5 refresh re-derives) | **~5–8 KB** |
| `PROGRESS.md` | 1,353,945 B | 6–8 KB | 2–4 KB | **~9–12 KB** |
| `LEARNINGS.md` | 1,793,045 B | 12–15 KB | none (archive tier) | **~12–15 KB** |
| three root docs | 5,052,921 B | — | — | **~26–35 KB (−99.3%)** |
| lean recovery tier | 3,220,720 chars ≈ 805,180 est. tokens | — | — | **≈ 8–10 KB chars ≈ 2–2.5k est. tokens** (budget 12,000 — passes with wide margin) |
| full six-doc tier | 5,018,757 chars ≈ 1,254,690 est. tokens | — | — | **≈ 55–65 KB chars ≈ 14–16k est. tokens** |

Pessimistic variant (if §5.4's guard bundle keeps the 419,843 B payload): HANDOFF/PROGRESS
stay ~430 KB each; reduction limited to ~1.8 MB total (LEARNINGS + duplicated tail). In that
case consolidation *still* halves recovery cost but does **not** fix lean-tier size, and the
remaining cause is guard-side — report to operator, do not hand-edit the block.

---

## 8. STOP conditions and rollback

**STOP immediately, leaving the tree as found, if any of:**
1. Archive blob hash ≠ §2 value, or live file hash ≠ §2 recorded value at apply time (concurrent
   writer) → do not overwrite; report.
2. Any pre-existing dirty/untracked path would be staged, modified, cleaned or deleted by the
   operation. (Stage B found **121 dirty/untracked paths**, including 9 modified infra files,
   **1 pre-staged file `scripts/durable_edit.py` (456 insertions vs HEAD)**, 112 untracked
   including `S2.PLI`, `S2.log`… `S5.log` at repo root and `golden/**/dir.txt`. These are not
   ours to touch.)
3. A managed block would have to be hand-written, or `### Next action` content cannot be
   reproduced byte-exactly from the original file slice.
4. `audit` still reports `duplicate-active-heading` / `active-next-action-ambiguous` after the
   change, or `next-action-recorded` fails with a *new* reason.
5. The completeness sweep finds a deleted line absent from the snapshot (other than the §4.2
   known exception).
6. A `--check-refs` failure that would require *inventing* a path to satisfy it. Never invent;
   report the reference instead.
7. Any temptation to close an `## Open obligations` item, reclassify a `my-gap`, edit
   `spec/CLAIMS.md`, or restamp a golden. Science truth ledgers are out of scope for Stage C.
8. A named mission instance becomes selected (`handoff_inspect` ≠ legacy mode) — the premise of
   this stage.

**Rollback.** Every step is a commit of explicit paths on `main`, never pushed:
```sh
git log --oneline -3                       # note the pre-Stage-C HEAD
git revert --no-commit <consolidation sha>
git diff --cached --name-only              # assert only the intended root docs
git commit -m "revert: consolidation 2026-11-15 (<reason>)"
# then guard refresh + attest again (§5 sequence), because prose changed back
```
`git revert` (never `reset --hard`, never `git clean`, never destructive checkout) keeps the
chain append-only. If the damage is only in the working tree and uncommitted, restore the
single file from HEAD by explicit path: `git checkout HEAD -- HANDOFF.md` — permitted **only**
for a file this stage itself wrote, never for pre-existing dirty paths; if in doubt, keep the
pre-apply copy under `build/consolidation-2026-11-15/backup/` and `cp` it back.

**Operator decisions required before Stage C:**
- **D1** — Approve/reject the §3 drafts verbatim, especially §3.3 L-001…L-007 (which lessons
  are "current" is an editorial judgement the assistant must not make alone).
- **D2** — Confirm the §3.2 `## Open obligations` classification (active vs historical) for
  LOAN2 prescan, CREATE `%include`, the E2E-49/P4 §3 refusal list, and HAMM-00 rev2 PROPOSED.
  **C1 evidence check (see §10 D2): the HAMM-00 rev2 entry is OUTDATED and must not be
  transported as an open obligation.**
- **D3** — Choose §5's treatment of the stale g844 block (single contiguous tail deletion —
  recommended — vs prose-only excision).
- **D4** — Decide whether consolidation happens in the **root/legacy** handoff at all, or
  whether root documents should instead be reduced to a stub pointing exclusively at sealed
  named instances (the direction the project has actually moved in since 2026-11-14).
- **D5** — Note `scripts/durable_edit.py` is staged with +456 lines and **differs from HEAD**;
  the audit numbers in §0 were produced by the *uncommitted* version. Re-run the audit against
  the committed `61ac240e` version before relying on tool behaviour in Stage C.

---

## 9. Reference triage (Stage B result — feeds §7.4)

Of the 32 `missing-archive-reference` findings (HANDOFF 16, PROGRESS 14, LEARNINGS 2):
**12 are genuine path errors, 17 are shorthand false positives, 3 are expected-absent
gitignored scratch.**

**Genuine broken references (real path errors, fix only with operator approval):**
| Reference | Actual path |
|---|---|
| `ocaml/lib/hir_build.ml` (5 findings: HANDOFF 3, PROGRESS 2) | `ocaml/hir/hir_build.ml` |
| `ocaml/bin/pli80hir.ml` (5 findings: HANDOFF 2, PROGRESS 3) | `ocaml/hir/pli80hir.ml` |
| `ocaml/lib/backend.ml` (1 finding: PROGRESS) | `ocaml/hir/backend.ml` |
| `research/minimal-baseline/README.md` (LEARNINGS ×1, 6 mentions of `research/` total) | **absent and never tracked in git** — external tree (cf. AGENTS.md out-of-scope external paths) |

These three `ocaml/{lib,bin}/*` paths also appear in `spec/lab-evidence/e2e54/PLAN.md`, which
is committed scientific evidence: correcting prior evidence needs explicit justification and a
traceable record, **not silent replacement** → operator decision (D6).

**Shorthand false positives (leave prose alone):** `HANDOFF.md/PROGRESS.md`,
`hir.ml/hir_build.ml`, `dir.txt/summary.txt`, `claims/coverage/inventory/goldens/dir.txt`
(category enumeration, not a path), `CALL07/CALL08/CALLN9.pli` (exist in
`hir/mir-call-fixtures/`), `CALL07.mir/CALL08.mir/CALLN1.mir/CALLN9.rc/CALLN9.stderr.txt`
(exist in `hir/mir-call-expected/`), `hir/fixtures/H01..H05.pli` (all five exist),
`hir/expected/H01..04.txt` (all four exist, tracked), and `step6/RESULTS.md` (fragment of a
brace enumeration — `spec/lab-evidence/e2e50-p2/step6/RESULTS.md` **does exist**).

**Expected-absent (ignored working state, not defects):** `build/p1m3-brief-true.md`,
`build/e54p1m3-reg-gate.log`, and `build/e52p3/E52PL/PM/PN/PO-golden-reldump.txt` —
`.gitignore` line 12 ignores `build/`; transient scratch (the last is also a range
enumeration). Classify as historical/ephemeral, never as a broken scientific reference.

---

## 10. Stage C1 binding review decisions (operator policy D1–D6, 2026-11-15)

Every C1 measurement below was reproduced read-only at HEAD `2e62e0fb`; deltas from §0 are
noted explicitly. Full verdicts: `STAGE-C1-REVIEW.md` in this directory.

- **D1 — ACCEPTED.** LEARNINGS becomes a short discovery index only; no corpus or large summary
  is transported. The three-required-heading scaffold fix (§3 mandatory properties) does not
  change this: each of `## Accepted` / `## Proposed` / `## Falsified or superseded` carries
  index rows + pointers, not bodies.
- **D2 — ACCEPTED WITH CORRECTIONS (C1 evidence check):**
  - **LOAN2 prescan: still OPEN (`my-gap`).** Verified: `artefacts/LOAN2.PLI` declares
    `i fixed decimal(4,2),` at line 32 and `i fixed bin;` at line 211; the refusing code is
    `vk_rows`/`conflicting kinds` at `ocaml/lib/codegen.ml:16065-16080` (failwith text at
    16072), `pd_vars` built at 16087, consumed by `prescan_pool` (def. 1885, call 16134);
    18 `cx.pd_vars` sites. **§3.2's citation `codegen.ml:12460-12490` is WRONG (that region is
    DO-index lowering) — the applied draft must cite 16065-16090.** Goldens exist
    (`golden/first/LOAN2`, `golden/first8080u/LOAN2`): DR accepts; open limitation confirmed.
  - **CREATE `%include`: still OPEN.** Verified: no INCLUDE expansion in `ocaml/bin/pli80c.ml`;
    recorded blocker `spec/lab-evidence/e2e48-p2c/RESULTS.md:107` ("the blocker stays the
    front-end `%include` gap"). Open limitation, correctly classified.
  - **E2E-49/P4 §3 remainders: still OPEN as named refusals / unmeasured.** Verified against
    `spec/lab-evidence/e2e49-p4/RESULTS.md` §3/§4 (18 `my-gap`, shapes listed match the draft).
  - **HAMM-00 rev2: OUTDATED PROPOSAL, not an open obligation.** Two distinct "rev2"s exist:
    (i) the **derivation fix** was AUTHORIZED and LANDED as E2E-51/P2 (`a21a586`, record
    `52f9a54`; `docs/functional-results.md` § 17: six-stage lane-B **PASS** 2026-11-04,
    double-run byte-equal); (ii) the **subtraction-loop division workaround** is explicitly
    **OBSOLETE** (pre-consolidation PROGRESS 4385-4389: "variable-divisor division now compiles
    byte-exact; do NOT propose or implement it"). The applied §3.2 must **remove** it from Open
    obligations and record it as obsolete/superseded in a historical note.
  - The scientific ledger (`spec/CLAIMS.md`, 203/C380) is **not altered** by any of this.
- **D3 — RECLASSIFIED as damaged legacy-document layout; recovery procedure = §4+§5+§6.4/§6.8,
  now complete.** Byte-level preservation is proven on two levels: the archive blobs are pinned
  by git (`git cat-file blob HEAD:…` re-hashed in C1 to the §2 values), containing both original
  blocks (g852 manual+attested at HANDOFF 2609-3960; g844 auto+unattested orphan at 6496-7844;
  g852 in PROGRESS 5795-7134; LEARNINGS 0/0). The g852 **pair** is retained verbatim in the
  replaced roots until the guard regenerates it (§5 g852-pair clause). Marker counts before/after
  are tabulated in `STAGE-C1-REVIEW.md`. No checkpoint field is ever edited by hand; the orphan
  disappears only as part of the reviewed contiguous deletion, recorded in the commit message.
- **D4 — ACCEPTED.** Root HANDOFF carries exactly one canonical `## Next action` meaning STOP /
  await operator brief; it does not resume FC-01, P1-m4 or any sealed instance. C1 verified the
  deleted-tail scenario restores uniqueness (39 unique H2s after removing 3961-7845) and that
  the STOP wording survives `PLACEHOLDER_RE`. PROGRESS's required single `## Next action`
  (§3 fix) carries the same STOP meaning — HANDOFF remains the single authoritative copy.
- **D5 — CONFIRMED, tool untouched.** The staged `scripts/durable_edit.py` (+456 vs HEAD
  `61ac240e`) is not modified or re-staged by this plan. C1 verified that the semantics §6.3
  relies on (`hash`, `plan`, `apply`, `--expect-sha256`, AMBIGUOUS→exit 3, same-dir temp +
  `fsync` + `os.replace`, exit codes 0/2/3/4/5/6/7) exist **in the committed version too**
  (HEAD copy lines 12-17, 53, 187-197, 226, 292-293); the discrepancy is that `audit` and
  `archive-plan/archive-apply` exist **only in the staged/on-disk version**, so every §0 and §7.4
  audit number in this plan was produced by the uncommitted tool. Stage C's §6.3 replaces need
  no staged-only feature; §7.4's audit re-check runs the on-disk staged tool read-only.
  Re-verify `git diff --cached --stat scripts/durable_edit.py` before and after Stage C: must
  read exactly 456 insertions / 1 deletion, unchanged.
- **D6 — ACCEPTED: no rewrite of committed scientific artifacts.** The three `ocaml/{lib,bin}`
  path errors inside `spec/lab-evidence/e2e54/PLAN.md` (verified present: 3 matching lines) are
  NOT corrected in C2. The traceable erratum is recorded twice, both new/append-only:
  (a) one new row in `docs/history/README.md` (the S5 row) plus (b) an `## Errata and reference
  corrections` note inside the new root `LEARNINGS.md` index listing the wrong path, the actual
  path, and `spec/lab-evidence/e2e54/PLAN.md` as the artifact where the wrong path stands
  unmodified. `research/minimal-baseline/README.md` is recorded as external/never-tracked.
- **Operator decision D4-of-§8 (root-stub vs consolidation)** remains OPEN for C2 authorization;
  §3 drafts assume consolidation-in-root.
- **§3.2/§3.3 applied content differs from the §3 text** wherever §3 "mandatory properties"
  requires; the §3 code blocks are superseded by §10/D1-D5 for heading scaffold, HAMM-00,
  and the codegen citation.
