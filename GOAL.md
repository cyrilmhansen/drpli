# GOAL.md — DRPLi

Protected file. The context-guard blocks writes/edits to it and warns on drift. It is
short and stable on purpose; changes to the objective are an **operator decision**, and
are proposed in `LEARNINGS.md`, never made silently here.

## Objective

Reproduce the behaviour of the Digital Research **PL/I-80 Compiler v1.4** (CP/M-80) in
OCaml, such that for every accepted input the compiler emits a **`.REL` object file that
is byte-identical to the one produced by the original DR compiler** — the whole file, not
just its CODE segment.

## Acceptance criteria

1. **Target: Intel 8080 only.** The oracle runs the original binaries under the neutral
   8080-only emulator path (`oracle/`, `cpmsim -8`). Z80-specific behaviour is out of scope.
2. **The original DR compiler is the oracle.** No claim about compiler behaviour is
   accepted on the strength of the manual, a memory, or an agent's summary — only on an
   experiment against the original binaries, recorded in `spec/CLAIMS.md` with specimen,
   golden paths and verdict.
3. **Complete `.REL` comparison, byte for byte.** Acceptance means whole-file equality
   (all segments, records, relocation data, end record). CODE-segment-only equality is a
   partial result and must be reported as such.
4. **Historical toolchain as reference.** Original **LINK-80 1.31** (`artefacts/LINK.COM`)
   and **PLILIB** (`artefacts/PLILIB.IRL`) are the historical references for linking, the
   `.REL`/`.IRL` formats and the runtime ABI where a question requires them.
5. **Preserve historical quirks.** DR behaviour that is nonstandard, inconsistent with the
   manual, or a compiler bug is reproduced when it is the observed compiler behaviour —
   subject to the `[S]/[M]/[C]` classification in `spec/PERIMETER.md`. Deliberate
   divergence is recorded in `spec/DIVERGENT.txt`, never smuggled in silently.
6. **Regression-gate integrity.** `tools/e2e_gate.py` and the tiered gates stay green; the
   machine-maintained ledgers (`spec/INVENTORY.txt`, `spec/SPECIMENS.tsv`,
   `spec/COVERAGE.tsv`, `spec/RUNTIME.txt`, `spec/DIVERGENT.txt`) stay consistent with the
   panel they describe.
7. **`PLILIB.IRL` analysis is a later stage**, not a current implementation priority. It is
   research to be done when linking/runtime questions require it — it does not preempt
   front-end, binder, IR or codegen work.
