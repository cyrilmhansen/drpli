# spec/functional/tests — functional test specifications (schema `pli80-functional/1`)

**E2E-50/P2 step 3 deliverable** (2026-11-02). One JSON spec per functional test, plus its
source and its independent reference. This directory defines FORMAT and LAW; it carries no
verdicts. Verdicts are produced only by the step-5 harness (`tools/functional_runner.py`, owed)
from executed, lane-labelled evidence.

Positioning (same discipline as `spec/functional/README.md`): this layer is **not a second
scientific ledger**. Compiler-behaviour law lives in `spec/CLAIMS.md`; capability rows in
`spec/COVERAGE.tsv`; byte-panel registration in `tools/e2e_gate.py`/`spec/INVENTORY.txt`. A
functional PASS here never promotes a COVERAGE row and never becomes a DR claim; if this layer
and a canonical file disagree, the canonical file wins.

---

## 1. The three independence laws

These are the reason the layer exists. Every rule below is a corollary of one of them.

**L1 — BYTE ≠ correct.** A whole-file byte-exact `.REL` proves object identity with DR's
compiler output; it says NOTHING about runtime semantics. The ledger itself enforces this: the
E2E-48/P4–E2E-49/P4 claims carry the standing note that no runtime semantics were measured for
`?SCCCM` etc. ("BYTE TIER ONLY — no `spec/RUNTIME.txt` row came or comes from this round",
`HANDOFF.md` § Last verified state, E2E-49/P4). Functional evidence is a different axis and
requires executed programs and independently specified outputs.

**L2 — exit 0 ≠ correct.** `[C137]` (`spec/CLAIMS.md` § C137, measured E2E-11) is the founding
precedent: LINK-1.31 reports `UNDEFINED SYMBOLS:` and **still writes the `.COM`**, which then
runs, prints nothing, and exits rc=0 (`golden/e2e153_l/`, `golden/e2e150dr/E29F.output.txt`).
Therefore:
- "a `.COM` appeared" is NEVER link-stage success;
- "the run exited 0" is NEVER run-stage success;
- link success is the FULL transcript parsed for the undefined-symbols segment
  (`oracle/linkrun.py:245-258` `parse_undefined`, with the pinned regression `selftest`), and
  the segment must be taken from the full segment text, never from a display slice — the
  per-name display line is capped at 120 characters and a `[:120]` slice can end exactly at
  `UNDEFINED SYMBOLS:` and read as clean (`oracle/linkrun.py:238-241`).

**L3 — capture ≠ expectation.** Expected behaviour is DERIVED, never observed from the thing
under test. Each spec's `expected` block names a `derivation` pointing into an independent,
stdlib-only Python reference script committed beside the spec (§ 4). A transcript produced by
DR, by my compiler, or by any lane's run may be stored as EVIDENCE but can never be pasted into
`expected` as its own oracle. (The console `PUT LIST` *format* convention — § 6 — is measured
behaviour recorded in `LEARNINGS.md` 2026-11-02 and cited from goldens; it governs how a PASSING
program must print, not what values it must print.)

## 2. Directory layout

```
spec/functional/tests/README.md            this file — format + law
spec/functional/tests/<ID>.json            one spec, "spec": "pli80-functional/1"
spec/functional/tests/<ID>.PLI             the program source (or <ID>.asm for Lane A fixtures)
spec/functional/tests/reference.py         independent stdlib-only reference (per-family sections)
```

`<ID>` is `^[A-Z][A-Z0-9-]*$` (e.g. `TABLE-00`). Families in force are listed in
`docs/functional-testing.md`; the current corpus family is **TABLE**.

PL/I sources follow the historical probe convention: **CRLF line endings, `^Z`-terminated,
≤ 71 columns** (the same discipline that prevented the `>72-col` oracle failure kept at
`spec/lab-evidence/e2e48-p2d/` as run-1 `67bf83c`).

## 3. JSON schema `pli80-functional/1`

Unknown fields at any level are a **spec error** (the harness must fail closed — a silently
ignored typo must not downgrade or upgrade a verdict). `null` is not a legal value for any
required field.

| Field | Req | Type / form | Meaning |
|---|---|---|---|
| `spec` | Y | `"pli80-functional/1"` | schema tag; the harness rejects any other value |
| `id` | Y | string | stable test id, must equal the basename of the spec and source files |
| `family` | Y | string | corpus family (`TABLE`, `FIXTURE`, …) |
| `title` | Y | string | one-line description of what is functionally checked |
| `provenance` | Y | object | § 5 |
| `source` | Y | object | `{"file": "<rel path>", "sha256": "<hex of file bytes>", "encoding": "<form>"}`; the harness verifies the hash BEFORE any execution; mismatch is a spec/source-stage failure, attribution `source` |
| `capabilities` | Y | array of COVERAGE ids | every row the test exercises; each must exist in `spec/COVERAGE.tsv` and must not be on the forbidden list (§ 7). **[E2E-50/P2 step 6 amendment]** A **Lane-A-only substrate fixture** (hand-encoded assembly, no compiler) exercises no PL/I construct, so § 7 has nothing to validate and the array MAY be empty there and only there; any spec with a lane B still requires a non-empty array (fail closed). Original rule text: "`capabilities` must be a non-empty array", kept as written per PROTOCOL #2. |
| `limits` | Y | object | `{"compile_timeout_s": n, "link_timeout_s": n, "run_timeout_s": n, "run_max_steps": n}` — all positive integers; timeouts are FAIL-with-attribution material, never a retry prompt (§ 8) |
| `lanes` | Y | array (≥1) | § 5.2 lane entries; the verdict of a test is per-lane |
| `console_input` | N | string | console stdin for the run stage; DEFAULT `"^Z"` (one EOF), the `oracle/linkrun.py` convention (`DEFAULT_INPUT`); Lane A specs may omit it (the audited emulator provides no console input at all — `docs/emulator-audit.md` § 2.12) |
| `expected` | Y | object | § 4: `derivation`, `normalization`, `console` (non-empty array), optional `file_expectations` |
| `notes` | N | string | design rationale, cross-references |

## 4. The expected block — reference derivation

```json
"expected": {
  "derivation": "reference.py:table00",
  "normalization": "collapse-spaces-v1",
  "console": ["1 2 2 3 5 8 13 21", "COUNT= 8 SUM= 55"]
}
```

- `derivation` is `<script>:<function>` relative to this directory. The function is pure,
  stdlib-only, takes no inputs (fixed-input corpus), and returns the expected console lines as
  a list of strings. It implements the *specified semantics* independently of the PL/I program
  — e.g. TABLE-01's function sorts the same fixed literal sequence with Python's own sort and
  reports ordering, multiplicity, count and sum; the PL/I program is not consulted.
- The harness performs a **two-way check**: (a) run the derivation and require it to reproduce
  `expected.console` exactly (spec/reference drift is itself a spec FAIL, attribution `source`
  — a stale spec must not be able to pass); then (b) compare the lane's run transcript against
  `expected.console`. Only (b) says anything about the compiler.
- `normalization` is one of `"collapse-spaces-v1"` (default law) or `"exact"` (raw bytes).
  `collapse-spaces-v1` is the gate's own runtime law, adopted verbatim for v1
  (`tools/e2e_gate.py:5632`):
  `norm = re.sub(r" +", " ", raw.replace(b"\r\n", b"\n"))`.
- **An empty expected list is invalid** — "the console is empty" is not an assertion; the gate
  law is adopted: an empty expected string matches every transcript
  (`tools/e2e_gate.py:5628-5636`). Where absence must be asserted, use a NEGATIVE entry
  `"!text"` (same spelling the gate has used since [E2E-41/P1b]), which is a real test.
- Line semantics: **v1 asserts the COMPLETE normalized console stream.** The normalized
  bytes are split on `\n`; the expected list must equal that sequence of lines, in order,
  with no extra and no missing line. One documented deviation from the gate, deliberate and
  stricter: `tools/e2e_gate.py` matches each pipe-item as an ordered SUBSTRING of the stream
  (`e[1:] in norm` / `e not in norm`, `tools/e2e_gate.py:5681-5685`); a functional PASS here
  additionally demands nothing else was printed. One exception, matching the measured E32B1
  behaviour (console ends with a final `\n` even though no statement emitted a SKIP): a single
  trailing empty element after the split is ignored. Under `"exact"`, the raw bytes of the
  captured stream must equal the derivation's declared byte string verbatim (an `expected.raw`
  field replaces `console`); EOL convention is NOT asserted by this law — it is whatever the
  measured golden for that substrate shows (e.g. `golden/e32rt_E32B1/E32B1.output.txt` ends
  with a plain `\n`, od-verified), so exact mode is opt-in per test only where that convention
  has been measured for the item shapes used.

## 5. Provenance and lanes

### 5.1 `provenance` block

```json
"provenance": {
  "origin": "original",
  "author": "DRPLi E2E-50/P2 step 4 corpus",
  "date": "2026-11-02",
  "note": "written for this project; independently specified; no third-party import"
}
```

`origin` is one of `original` | `historical-dr` | `third-party`. The E2E-50/P2 corpus is
`original` only — third-party benchmarks are NOT authorized before rights are verified (mission
brief), and no DR corpus program may be silently imported as "mine". The PL/I/asm source file
carries a matching header comment (PL/I: `/* TABLE-00 — original DRPLi work 2026-11-02; spec:
TABLE-00.json */` as the first comment).

### 5.2 Lane entries

```json
{"lane": "A", "substrate": "runes:pli80-run",
 "toolchain": "hand-crafted original .COM fixture; no compiler, no DR libraries",
 "artifact": "spec/functional/fixtures/<ID>.COM", "artifact_sha256": "<hex>"}

{"lane": "B", "substrate": "cpmsim:z80pack",
 "toolchain": "pli80c -> .REL -> LINK-80 + PLILIB.IRL (user-supplied, never packaged)",
 "link_targets": ["<NAME>"]}
```

- **Lane A (free-core):** original hand-written artifacts executed under the audited emulator
  (`docs/emulator-audit.md`). It validates harness machinery WITHOUT any restricted tool. The
  emulator binary itself is user-supplied (the lab's license status blocks *shipping*, not
  *running* — audit § 6-7).
- **Lane B (historical-compat):** my compiler output linked by the historical DR LINK-80 +
  PLILIB.IRL and run under z80pack cpmsim through the existing `oracle/` workspace machinery
  (`oracle/cpmwork.py` Workspace/Run safety: symlink guards, atomic run-claim, copy-never-move
  seeds, fresh-mkfs scratch disks). DR tools are **user-supplied, never packaged, never
  committed here** (AGENTS.md protection boundary; `artefacts/` stays read-only).
- Every verdict is **lane-labelled**. A run on any other emulator or toolchain is not evidence
  for a spec lane; "never substitute an unlabelled emulator" (mission brief).
- A lane whose `substrate`/`toolchain`/`artifact` is absent on the host is **BLOCKED** (§ 8),
  never silently skipped.

## 6. Console format law for PL/I assertions (design input, evidence-backed)

Adopted for v1 assertions from the accepted measurement (`LEARNINGS.md` § 2026-11-02, hop-1:
od-verified stored goldens; re-verified 2026-11-02 hop-2: DR-side run golden
`golden/e32b_E32B1_dr/E32B1.output.txt` is byte-identical to `golden/e32rt_E32B1/E32B1.output.txt`):

- a FIXED numeric `PUT LIST` item prints in a **10-position right-justified field** (inline
  sign for negatives: `c= -2` shows as `c=` + field containing ` -2`);
- a CHARACTER literal prints unquoted at natural width;
- items inside one statement are separated by **one blank** — a consequence of the numeric
  field width;
- separate `put list(...)` statements **do NOT line-terminate** — statements share one line
  until an explicit `SKIP` (three put statements produced one `\n`-terminated line in E32B1).

With `collapse-spaces-v1` normalization these become plain single-space expected strings;
under `"exact"` the full field layout is asserted.

## 7. Corpus capability perimeter (v1, from `spec/COVERAGE.tsv`)

Constraints measured and accepted in `LEARNINGS.md` § 2026-11-02 (hop-1 capability survey):

- **Allowed:** `AGG.ARRAY_1D_FIXED` (EXACT:30), `AGG.VAR_INDEX_LADDER`, `LOOP.DO_TO_BY`,
  `LOOP.DO_WHILE_UNTIL`, `LOOP.REPEAT_CLAUSE`, `IO.PUT_LIST_FIXED`, `IO.PUT_SKIP`,
  `EXPR.REL_FIXED_EQ_K`, and the ordered-relation-with-literal family ([C348]).
- **FORBIDDEN in v1 specs** (a `capabilities` array naming any of these is a spec error):
  `AGG.MULTIDIM` and `EXPR.K_PLUS_X` — REFUSED rows; `LOOP.TRAVERSAL_RELOAD` — DIVERGENT row
  (`spec/DIVERGENT.txt`): keep loop bounds constant.
- `EXPR.REL_VAR_EQ_EXPR` is UNTESTED — do not build an assertion on it.
- Console INPUT (BDOS 1/10) does not exist on the audited emulator (`docs/emulator-audit.md`
  § 2.12): v1 corpus is pure-PUT, no `GET`.

## 8. Verdict law — PASS / FAIL / BLOCKED / UNKNOWN

Stages of a lane, in order: `SOURCE` (hash/encoding integrity) → `DERIVATION` (reference
reproduces the spec) → `COMPILE` → `LINK` → `RUN` → `ASSERT`. Lane A fixtures skip `COMPILE`
and `LINK` by construction — those stages are recorded `not-applicable` **in advance by the
spec**, not decided after the fact.

- **PASS** — every applicable stage ran, produced typed success evidence, and `ASSERT` matched.
  **A skipped, unrun, or not-attempted stage is NEVER a PASS.** No partial credit.
- **FAIL** — a stage ran and produced typed *failure* evidence, or `ASSERT` mismatched.
- **BLOCKED** — a required dependency is absent or unusable and the stage could not run at all
  (restricted tool not supplied, emulator not built, cpmsim missing, artifact hash file
  missing). BLOCKED is an honest stop, not a retry instruction, and is never reported as PASS.
- **UNKNOWN** — the stage ran but the evidence cannot be classified (unparseable transcript,
  timeout, emulator crash with no typed reason, run ended without the termination witness).
  Missing evidence is UNKNOWN, never a verdict in either direction (PROTOCOL #4 by analogy:
  absence of a witness proves nothing).

Timeouts: hitting `compile_timeout_s`/`link_timeout_s`/`run_timeout_s` or `run_max_steps`
produces FAIL for that stage (attribution per § 9, typically `undefined` until discriminated) —
the `timeout-or-hang` collapse lesson ([C308]: 51 timeouts, 2 emulator deaths, 2 terminations
hidden behind one label) requires the harness to record WHICH termination witness was seen.

## 9. Failure-origin attribution (typed, evidence-only)

Every FAIL/UNKNOWN verdict carries `attribution` ∈ {`source`, `compiler`, `runtime-lib`,
`emulator`, `host`, `undefined`}. Attribution is a CLASSIFICATION OF EVIDENCE, never an
assumption; without a typed signal the value is `undefined`:

| Origin | Admissible only from |
|---|---|
| `source` | the compiler's own diagnostic names the source (stage prefix of a refusal on a source construct); spec-hash or spec/reference mismatch |
| `compiler` | my compiler's refusal/abort message at a named stage (compile stage only, message text recorded verbatim) |
| `runtime-lib` | the program ran to completion under a trusted substrate but output mismatches with the reference double-check clean |
| `emulator` | a typed emulator error on the run path (e.g. `pli80-run: unsupported BDOS function N`, runner error classes; stdout evidence invalid on these paths — see below) |
| `host` | missing tool, unreadable file, subprocess launch failure, spec-dir corruption (pairs with BLOCKED) |
| `undefined` | everything else — including assert-mismatch with no discriminating run |

Two mechanical rules:

1. **`pli80-run` discards buffered program output on every error path** (`bin/main.ml:104-121`,
   accepted measurement, audit § 2.18): program stdout is flushed ONLY on success; any runner
   error exits 1 with the buffer dropped. Harness law: **Lane A stdout is valid evidence only
   at exit 0**; failure-side evidence requires `--trace` (keep the trace file as evidence).
2. Attribution may be *narrowed* only by a discriminating run (e.g. a Lane A fixture proving
   the substrate path, or the [C137] all-objects-named link form), never by reasoning alone;
   until then `undefined` stands.

## 10. Example spec (ILLUSTRATIVE ONLY — not a registered test)

```json
{
  "spec": "pli80-functional/1",
  "id": "TABLE-01",
  "family": "TABLE",
  "title": "sort of a fixed 8-element table; ordering, multiplicity, count, sum",
  "provenance": {"origin": "original", "author": "DRPLi E2E-50/P2 step 4 corpus",
                 "date": "2026-11-02", "note": "independently specified"},
  "source": {"file": "TABLE-01.PLI", "sha256": "<hex>", "encoding": "CRLF ^Z <=71 cols"},
  "capabilities": ["AGG.ARRAY_1D_FIXED", "LOOP.DO_TO_BY", "IO.PUT_LIST_FIXED", "IO.PUT_SKIP"],
  "limits": {"compile_timeout_s": 60, "link_timeout_s": 120, "run_timeout_s": 60,
             "run_max_steps": 4000000},
  "lanes": [
    {"lane": "B", "substrate": "cpmsim:z80pack",
     "toolchain": "pli80c -> .REL -> LINK-80 + PLILIB.IRL (user-supplied)",
     "link_targets": ["TABLE01"]}
  ],
  "expected": {"derivation": "reference.py:table01",
               "normalization": "collapse-spaces-v1",
               "console": ["-3 -1 0 2 2 5 8 13", "COUNT= 8 SUM= 26"]},
  "notes": "duplicates and negatives per mission brief"
}
```

## 11. Results contract (step 6/7, defined here, landed later)

The harness writes verdict records OUTSIDE this directory (report layer, `docs/` /
`spec/functional/results/`, step 7 decides shape). A result record must carry: test id, lane,
verdict, attribution, per-stage evidence paths (transcripts, traces, `.REL`/`.COM` hashes),
host substrate identities (toolchain versions/hashes), and the git HEAD it ran at. **UNKNOWN
and BLOCKED are first-class verdicts and are never rendered as PASS in any report** (mission
brief). No functional result modifies `spec/COVERAGE.tsv`, `spec/RUNTIME.txt` or
`spec/CLAIMS.md`; promotion of anything to those ledgers needs its own pre-registered evidence
round.
