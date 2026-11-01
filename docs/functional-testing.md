# Functional Testing — law, architecture, and status

**E2E-50/P2 step 3 deliverable** (2026-11-02). This document is the prose statement of the
functional-testing law; the machine-facing format is specified in
`spec/functional/tests/README.md` (schema `pli80-functional/1`). Companion:
`docs/emulator-audit.md` (steps 1–2) — the substrate facts this document relies on are measured
there and linked, not restated.

## 1. Why a functional axis at all

The project's target has been byte-exact reproduction of DR PL/I-80 v1.4 `.REL` output, judged
against the original compiler (the oracle). That is a strong but *single-axis* verdict: it
proves the object file is what DR's compiler would emit — it does not execute anything. Runtime
behaviour is currently attested only by the narrow existing layers: the `spec/RUNTIME.txt` panel
(71 rows) and the pinned-divergence list `spec/DIVERGENT.txt` (9 rows), and large claim families
explicitly carry the note that no runtime semantics were measured for them.

Functional testing asks the other question: **does a compiled program do what an independently
written specification says it should do?** It is the axis a programmer experiences, and it can
catch classes of defect the byte panel structurally cannot (a byte-exact object whose lowering
plan we mis-*interpret* when we link and run it ourselves, or, conversely, a semantically fine
object we keep FAILING on layout).

## 2. The independence laws

1. **BYTE ≠ correct.** Whole-file `.REL` identity says nothing about execution semantics. A
   functional PASS never cites the byte panel, and vice versa.
2. **exit 0 ≠ correct.** The founding measured precedent is `[C137]` (E2E-11): LINK-1.31 prints
   `UNDEFINED SYMBOLS:` and *still writes* a `.COM` that runs silently and exits rc=0. The only
   link-stage signal is the parsed UNDEFINED-SYMBOLS segment of the full link transcript; the
   120-character display cap can truncate the diagnostic so it "reads as clean"
   (`oracle/linkrun.py:238-258`, pinned regression `parse_undefined`/`selftest`). This law is
   why "a `.COM` appeared" is not, and never will be, success in this harness.
3. **capture ≠ expectation.** Expected outputs are derived from an independent, stdlib-only
   reference implementation committed beside the spec (`spec/functional/tests/reference.py`,
   owed with the step-4 corpus). A transcript from DR or from any lane's own run may be stored
   as evidence but never pasted in as its own oracle. The harness *double-checks*: reference
   must reproduce the spec's expected list (catches spec drift), then the run must match the
   spec (catches compiler/runtime bugs). Only the second comparison says anything about us.

## 3. Anatomy of a test

```
spec/functional/tests/TABLE-00.json      the spec: identity, provenance, source hash, limits,
                                         lanes, expected + derivation
spec/functional/tests/TABLE-00.PLI       original source (CRLF, ^Z, <=71 cols convention)
spec/functional/tests/reference.py       independent expected-value derivation (stdlib only)
```

Stages per lane, each with its own evidence record:
`SOURCE → DERIVATION → COMPILE → LINK → RUN → ASSERT`.
Lane A fixture specs declare COMPILE/LINK *not-applicable in the spec itself* — skipping after
the fact is not a thing.

## 4. Verdict law

Per lane and test, exactly one of:

| Verdict | Meaning | Evidence requirement |
|---|---|---|
| **PASS** | all applicable stages ran, typed success each, assertions matched | every stage's evidence path recorded; a skipped/unrun stage can never contribute to PASS |
| **FAIL** | a stage ran with typed failure evidence, or an assertion mismatched | the typed signal recorded verbatim; timeout records WHICH termination witness class was observed ([C308] lesson: never collapse timeout/hang/emulator-death into one label) |
| **BLOCKED** | a required dependency absent/unusable — the stage could not run at all | what is missing, by name (restricted tool not supplied, emulator not built, artifact hash mismatch…) |
| **UNKNOWN** | ran but unclassifiable (unparseable transcript, no termination witness, ambiguous mismatch) | the raw evidence preserved; **absence of evidence is never a verdict either way** |

**A skipped stage is never PASS**, in any rendering, at any level of reporting. UNKNOWN and
BLOCKED survive into the report unchanged — the mission brief states it and the step-5 hostile
tests must prove the harness cannot launder them.

## 5. Attribution law

Every FAIL/UNKNOWN carries a typed `attribution` ∈ {`source`, `compiler`, `runtime-lib`,
`emulator`, `host`, `undefined`}. Attribution is only admissible from a **typed signal** (a
named compiler diagnostic, a typed emulator error, a reference/spec drift check, a host
FileNotFound); reasoning alone never assigns an origin, and the default is `undefined` until a
discriminating run narrows it. The mechanical consequences on our two substrates:

- Lane A (`pli80-run`): the audited emulator **discards buffered program output on every error
  path** (`docs/emulator-audit.md` § 2.18, measured from `bin/main.ml:104-121`), so stdout is
  evidence only at exit 0 and failure-side evidence requires `--trace`.
- Lane B (cpmsim + LINK-80): the console transcript is captured in full (no display truncation
  before parsing), prompt-sync uses an explicit fresh-prompt marker (the `##WAIT` stale-echo
  lesson in `oracle/linkrun.py`), and default console input is one `^Z` (EOF) per the existing
  oracle convention.

## 6. Console expectation conventions

v1 adopts the compile-tier gate's runtime normalization **verbatim**
(`tools/e2e_gate.py:5632`: CRLF→LF, runs of spaces → one space) as `collapse-spaces-v1`;
`"exact"` raw-byte mode is available per spec. The PL/I console format law the corpus is written
against (10-position right-justified numeric fields, one-blank item separator, unquoted
CHARACTER literals at natural width, statements sharing a line until `SKIP`) is the accepted
goldens measurement recorded in `LEARNINGS.md` § 2026-11-02 — with the hop-2 re-verification
that the DR-side run golden `golden/e32b_E32B1_dr/E32B1.output.txt` and my run golden
`golden/e32rt_E32B1/E32B1.output.txt` are byte-identical. An empty expected list is invalid (the
gate's "an empty expected is never an assertion" law); absence is asserted with `!text`
negatives, the gate's own spelling since [E2E-41/P1b].

## 7. Substrate and redistribution constraints

From `docs/emulator-audit.md` (steps 1–2) and the mission boundary:

- **Lane A** is the free-core demonstration: original hand-crafted `.COM` fixtures under the
  audited Runes emulator. Running the user-supplied emulator locally is permitted; **shipping**
  it is blocked pending the operator's license decision (audit § 7.1) — nothing in this round
  packages any lab code.
- **Lane B** runs my compiler's `.REL` through the *historical* LINK-80 + PLILIB.IRL under
  z80pack cpmsim (MIT), reusing the `oracle/cpmwork.py` Workspace safety machinery (isolated
  fresh-mkfs scratch disks; copy-never-move seeds; the read-write mount can never touch
  originals). **DR binaries (`artefacts/`) are user-supplied and never distributable**; the
  harness must run with paths supplied at invocation and record their identities (sha256).
- The runtime BDOS census of a LINK-80'd PL/I image under Runes is **UNMEASURED** (audit § 4);
  the "pure PUT LIST needs only fn 2 + terminate" hypothesis stays PROPOSED until step 6
  measures it. Until measured, every Lane-A TABLE claim is UNKNOWN by law — never assumed.
- The audited emulator has **no console input** (BDOS 1/10 missing, audit § 2.12): the v1
  corpus is pure PUT, no `GET`/`ASK`.

## 8. Corpus design constraints (capability perimeter)

Fixed from `spec/COVERAGE.tsv` (survey accepted in `LEARNINGS.md` 2026-11-02): v1 specs use
1-D fixed arrays (`AGG.ARRAY_1D_FIXED`), variable-index ladder, `DO ... TO` loops with constant
bounds, `PUT LIST`/`SKIP`, fixed relations including the ordered-literal family [C348].
Forbidden: `AGG.MULTIDIM`, `EXPR.K_PLUS_X` (REFUSED) and `LOOP.TRAVERSAL_RELOAD` (DIVERGENT);
`EXPR.REL_VAR_EQ_EXPR` is UNTESTED and carries no v1 assertion. The corpus stays small and
progressive: TABLE-00 (traverse/aggregate), TABLE-01 (sort — ordering, multiplicity, count,
sum against the independently computed reference sequence), TABLE-02 only after 00/01 verify.
Fixed inputs include negatives and duplicates; every file carries an original-work provenance
header.

## 9. Relationship to existing layers

- `spec/CLAIMS.md`, `spec/COVERAGE.tsv`, `spec/RUNTIME.txt`, `spec/DIVERGENT.txt`,
  `spec/INVENTORY.txt`, the byte panel: **canonical and untouched by this layer.** No functional
  PASS promotes anything; functional findings feed those ledgers only through their own
  protocol-compliant rounds.
- `spec/functional/capabilities.tsv` / `programs.tsv` and `docs/functional-status.md`
  (E2E-50/P1): annotation views over canonical evidence; the step-7 results reporting reuses
  that model rather than rewriting it.
- The oracle campaign, the full CP/M runtime tier and Rune CI builders are **out of scope this
  round** (AGENTS.md, mission brief); Lane B runs are bounded, isolated, lane-labelled.

## 10. Status (as written at step 3)

| Piece | State |
|---|---|
| Format + law (`pli80-functional/1`) | **defined** — this document + `spec/functional/tests/README.md` |
| TABLE corpus sources + `reference.py` | owed (step 4) |
| Harness `tools/functional_runner.py` + hostile tests | owed (step 5) |
| Lane A fixture evidence | owed (step 6); substrate audited, license blocker recorded |
| Lane B TABLE evidence | owed (step 6); BDOS census UNMEASURED → honest BLOCKED/UNKNOWN first |
| Results reporting | owed (step 7); verdict law § 4 governs every rendering |

Nothing in this document asserts a DR behaviour that is not already measured and recorded in the
ledgers or `LEARNINGS.md`; what is owed stays marked owed.
