# STAGE-C1-REVIEW — binding review of CONSOLIDATION-PLAN.md before any application

Date: 2026-11-15. Session: read-only w.r.t. root HANDOFF/PROGRESS/LEARNINGS; no compiler,
oracle, build or gate execution; no checkpoint refresh; no push.
Reviewed HEAD: `2e62e0fb` (parent `bc7fd132`, snapshot HEAD `49728acc`). All C1 numbers below
were independently reproduced (bounded read-only Python + git plumbing + `durable_edit.py
plan/audit`, which perform no writes).

## 1. Baseline — CONFIRMED

| Item | Result |
|---|---|
| Mission mode | legacy project mode; no instance selected; `handoff_inspect`: "legacy mode; no instance closure seal" |
| Archive/follow-up commits | `bc7fd132` (snapshot), `2e62e0fb` (README correction) are HEAD and its parent; `bc7fd132` is an ancestor of HEAD |
| HANDOFF.md sha256 | `7364774e…40276f` — root == archive worktree == `git cat-file blob HEAD:` ✓ |
| PROGRESS.md sha256 | `81bb20cd…3ecad6` — all three levels ✓ |
| LEARNINGS.md sha256 | `786ce1a1…dc558c` — all three levels ✓ |
| Archive discoverability | `docs/history/legacy-root-2026-11-15/{HANDOFF,PROGRESS,LEARNINGS}.md` committed; both original checkpoint blocks (g852 ×2, g844 ×1) preserved verbatim inside the pinned bytes |
| Pre-staged script | `scripts/durable_edit.py` staged at +456/−1 vs HEAD `61ac240e`; untouched by C1 |
| Other dirty/untracked | infra files, `S2..S5.PLI/.log`, `golden/**/dir.txt`, `ocaml/_build-*` etc. inventoried, untouched — matches plan §8.2 |
| Guard state | checkpoint **stale** (attested Next action disagrees — mechanism proven below); attestation itself valid: strip-first+rstrip replay reproduces `source-handoff 5da7fb06…` and `source-progress e0fd8083…` exactly; renewal chain **absent** (`chain (none) 0/12`, renew refused state-unavailable — expected, see §5) |

## 2. D1–D6 verdicts

| D | Verdict | Basis (C1-verified) |
|---|---|---|
| **D1** | **PASS** | §3.3 is a pointer-only index; no corpus transport. **Condition:** re-scaffold under exactly one `## Accepted` / `## Proposed` / `## Falsified or superseded` each (`REQUIRED_SECTIONS.learnings`, checkpoint.ts:670-675). Recorded in plan §3 + §10-D1. |
| **D2** | **PASS WITH CORRECTIONS** | LOAN2 open `my-gap` (LOAN2.PLI L32/L211 verified; true site codegen.ml:16065-16090 — **draft's 12460-12490 citation is wrong**, corrected in §10-D2). CREATE `%include` open (pli80c.ml has no INCLUDE expansion; e2e48-p2c/RESULTS.md:107). E2E-49/P4 §3 remainders genuinely open named refusals (RESULTS §3/§4: 18 my-gap). **HAMM-00 rev2 is an OUTDATED proposal, not an open obligation:** the rev2 *derivation fix* LANDED as E2E-51/P2 (`a21a586`, docs § 17 PASS 2026-11-04) and the *subtraction-loop workaround* is explicitly OBSOLETE (variable-divisor division compiles byte-exact; "do NOT propose or implement"). Ledger untouched. |
| **D3** | **PASS after plan amendments (applied in this review)** | Damaged layout = wholesale duplication + orphan g844. Preservation proven at blob level (git cat-file hashes above). g852 **pair** (HANDOFF 2609–3960, 421,527 B; PROGRESS 5795–7134, 420,640 B) retained verbatim in the replaced roots via byte slices (plan §5/§6.4 extended to PROGRESS); g844 orphan (6496–7844, 422,102 B, kind=auto, readiness=unattested) removed **only** as part of the single reviewed contiguous deletion 3961–7845, recorded in the commit message. No field hand-edited. Marker counts verified independently (§3 below). |
| **D4** | **PASS** | Draft §3.1 has exactly one `## Next action`, meaning STOP/await brief; resumes nothing. Uniqueness after deletion proven: the kept region has **39 level-2 headings, zero duplicates**. STOP wording survives `PLACEHOLDER_RE` (anchored full-string, checkpoint.ts:1277). **Condition:** PROGRESS must also carry exactly one STOP-consistent `## Next action` (§3.2 draft as written FAILS validation — see §4 finding F1). |
| **D5** | **PASS** | Script unmodified/unrestaged. C1 verified the relied-on semantics (`hash`/`plan`/`apply`, `--expect-sha256`, AMBIGUOUS→exit 3, same-dir temp+fsync+`os.replace`, exit codes 0/2/3/4/5/6/7) exist **in the committed HEAD version too**; `audit` + `archive-plan/apply` are **staged-only** — recorded discrepancy: all §0/§7.4 audit figures came from the staged on-disk tool. Live behaviour spot-checked: `plan HANDOFF.md --section "## Unfinished operations"` → `AMBIGUOUS … lines 2560, 6447; refuse (no guessing)` exactly as §6.3 says. |
| **D6** | **PASS** | The 3 wrong `ocaml/{lib,bin}` paths are verified present in committed `spec/lab-evidence/e2e54/PLAN.md` and will **not** be rewritten. Traceable erratum defined for C2: one row in `docs/history/README.md` + an `## Errata and reference corrections` note inside the new LEARNINGS index (plan §10-D6). `research/minimal-baseline/README.md` recorded as external/never-tracked. |

## 3. Replacement documents and checkpoint marker counts

**Paths of proposed replacements (content = plan §3 drafts as amended by plan §3-mandatory-
properties and §10):** `HANDOFF.md`, `PROGRESS.md`, `LEARNINGS.md` (repo root). The exact draft
bytes will be generated at C2 into `build/consolidation-2026-11-15/{HANDOFF,PROGRESS,
LEARNINGS}.md.new` (git-ignored) and **hashed there before any replace**; each live replace then
requires hash(new draft) == hash(about to be written). The reviewed plan revision carrying these
decisions is committed at this file's sibling `CONSOLIDATION-PLAN.md` (sha256 recorded in the C1
commit message; root docs unchanged, hashes of §1 stand).

Checkpoint marker counts (begin/end pairs, `guard:checkpoint` blocks), verified by grep:

| File | Before (live & archive, identical) | After replace, before refresh | After guard refresh |
|---|---|---|---|
| HANDOFF.md | **2 / 2** (g852 manual attested @2609–3960; g844 auto unattested orphan @6496–7844) | 1 / 1 (g852 slice verbatim) | 1 / 1, generation 853, attested |
| PROGRESS.md | 1 / 1 (g852 @5795–7134; its `next-action:` field carries the same ~420 KB payload) | 1 / 1 (g852 slice verbatim) | 1 / 1, gen 853 |
| LEARNINGS.md | 0 / 0 (archive tier) | 0 / 0 | 0 / 0 |

After deletion all level-2 headings in HANDOFF are unique (39); PROGRESS drops from 9 → 1
`## Next action` headings; current audit findings `duplicate-active-heading` (2) and
`active-next-action-ambiguous` (1) must be **gone** post-C2 (§7.4 gate).

## 4. Findings requiring (now-embedded) plan corrections

- **F1 (blocking as originally drafted):** `REQUIRED_SECTIONS.progress` **includes**
  `## Next action`, `## Completed`, `## Blockers` — plan §4's claim to the contrary is refuted
  by checkpoint.ts:670-675 + validateFile:690-702 + headingMatchesTitle:1568-1577 (suffixed
  headings count). Draft §3.2 as written, and §3.3 for learnings, would **fail
  `durable-files-valid`** — a blocking readiness check — exactly like the damage being repaired
  (current PROGRESS fails with 9 duplicates; current LEARNINGS fails with `## Accepted` ×14,
  `## Proposed` ×2). Fix mandated in plan §3/§4 before any C2 draft is generated.
- **F2:** §3.2 LOAN2 citation `codegen.ml:12460-12490` wrong → 16065-16090 (18 `cx.pd_vars`
  sites; ~15-claim ≈ 11 assoc sites — say "≈18 sites"). Corrected in §10-D2.
- **F3:** §3.2 HAMM-00 rev2 stale → obsolete/landed (§10-D2).
- **F4:** counts/deltas: PROGRESS has **9** `## Next action` (not 5); three-block total
  1,264,269 B inclusive-of-markers (plan: 1,264,089 — basis delta 180 B); block payload
  419,841–843 B (basis); redundancy: **1,158/1,158** non-blank payload lines appear verbatim in
  manual prose (0 unique; plan said 1,156/2 — stronger than claimed). Line-count basis stated
  (split 7845 vs wc 7844). All noted in the amended plan.
- **F5:** §7.5 expectation softened: renewal gate will stay **refused (chain absent)**; C2
  attests via `/handoff`+`/handoff ready` or `handoff_finalize`. Verified config:
  `renewal.enabled=true, autoRenew=true, maxRenewals=12`, `recovery.lean=true`,
  budget 12000 — values live only in `handoff.config.json`.

## 5. Expected reduction (measured before → projected after; C2 must re-measure)

| Quantity | Before (measured C1) | After (projected) |
|---|---|---|
| HANDOFF manual/outside-block bytes | 1,484,404 B | ~3–4 KB prose |
| PROGRESS manual/outside-block bytes | 933,305 B | ~6–8 KB prose |
| LEARNINGS total | 1,793,045 B | ~12–15 KB index |
| Managed payloads | 421,527 + 422,102 + 420,640 B | post-refresh ~2–4 KB each **iff** §5 refresh re-derives (pessimistic variant §7.6: guard session-bundle replay keeps ~420 KB → report, never hand-edit) |
| Three root docs | 5,052,921 B | ~26–35 KB (−99.3%) |
| lean recovery tier | 3,220,720 chars ≈ 805,180 est. tokens (budget 12,000 — currently **fails**) | ≈ 8–10 K chars ≈ 2–2.5 K est. tokens (passes) |
| full six-doc tier | 5,018,757 chars ≈ 1,254,690 est. tokens | ≈ 55–65 K chars ≈ 14–16 K est. tokens |

(chars/4 estimates, not measured tokens.)

## 6. Failure/recovery scenarios (named)

- **S1 concurrent writer:** live hash ≠ §2 at replace time → STOP §8.1, zero writes.
- **S2 interruption between replaces (no cross-file transaction!):** state ∈ {0,1,2,3 replaced},
  each replaced file individually whole (os.replace is atomic per file). Recovery = plan §6.8:
  idempotent resume by per-file re-hash (pre-hash → replace; new-hash → skip; else STOP);
  abort = restore from `build/consolidation-2026-11-15/backup/`. **No commit, and above all no
  guard refresh, while the trio is mixed.**
- **S3 block-slice mismatch:** g852 slice bytes ≠ original range → STOP §8.3, zero writes.
- **S4 refresh keeps giant payload:** §7.6 pessimistic variant → stop, report to operator as a
  guard-side retention question; no manual block edit.
- **S5 post-audit still reports duplicate/ambiguous headings or `durable-files-valid: fail`:**
  STOP §8.4; the offending draft violated plan §3 mandatory properties.
- **S6 completeness sweep finds an unarchived deleted line** (beyond the single
  `SUPERSEDED-BY-ABOVE:` prefix pair): STOP §8.5.
- Rollback after commits: `git revert --no-commit <sha>` + explicit paths + guard re-refresh;
  uncommitted working damage: restore the three root docs from HEAD or backup. Never
  `reset --hard`/`clean`/`add -A`/push.

## 7. Paths Stage C2 would modify (exhaustive)

1. `HANDOFF.md` (atomic replace; g852 slice retained)
2. `PROGRESS.md` (atomic replace; g852 slice retained)
3. `LEARNINGS.md` (atomic replace; index only)
4. `docs/history/README.md` (+1 row, S5 step, verbatim preservation of existing rows)
5. guard-owned refresh of the managed blocks in 1–2 (`/handoff` + `/handoff ready` or
   `handoff_finalize`) — the **only** writer of managed bytes; commits: prose commit(s) then the
   guard write as its own commit, explicit paths, `--only`, pre-staged script left staged.

Nothing else. Not touched: GOAL.md, PROTOCOL.md, AGENTS.md, spec/**, golden/**, ocaml/**,
hir/**, tools/**, oracle/**, artefacts/**, manuals/**, extracted/**, references/**,
thirdparty/**, .pi-handoff/**, .pi-guard/**, handoff.config.json, scripts/durable_edit.py,
.pi/**.

## 8. Remaining operator decisions

- **OD1 (§8-D4 of plan):** consolidation-in-root (drafts as reviewed) vs root reduced to a stub
  pointing only at sealed instances. The reviewed drafts assume consolidation-in-root.
- **OD2:** approve lesson rows L-001…L-007 as the "current" set (editorial judgement reserved to
  the operator).
- **OD3:** confirm that with F1–F5 embedded the C1 verdict is **GO for C2 authorization**;
  without them the §3.2/§3.3 drafts would fail `durable-files-valid` and C2 must not proceed.

## 9. Verdict

**C1 = PASS with amendments (applied to the plan); C2 is authorized only against the amended
plan §3+§10 heading scaffold.** Root HANDOFF.md, PROGRESS.md, LEARNINGS.md remain at their §1
hashes; checkpoint not refreshed; no push. Science unverified by this review (PROTOCOL: this
stage judges document structure only).
