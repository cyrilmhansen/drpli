# spec/functional — programmer-facing capability layer (E2E-50/P1)

**This directory is ANNOTATION, never a second scientific ledger.** Every capability status in the
generated report is *derived* from the canonical sources below; nothing here asserts a fact about
DR or about this compiler that those sources do not already carry. If an annotation and a canonical
file disagree, **the canonical file wins** and the annotation is the thing to correct (PROTOCOL #7,
AGENTS.md "the repository wins").

Canonical sources (read-only for this layer):

| Source | What the dashboard takes from it |
|---|---|
| `tools/e2e_gate.py` `SPECIMENS` / `REJECTS` | the live panels (1174 + 181 at `5247656`) |
| `spec/INVENTORY.txt` | gate-maintained snapshot: `specimen` rows (name, source path, golden path) and `refusal` rows (name, **inline source text**, reason prose) |
| `NEG_META` in `tools/e2e_gate.py` | the `dr-refuses` / `my-gap` / `unmeasured` class of each negative (123/47/11 at `5247656`); read by **importing** the module — measured side-effect-free (empty stdout, clean tree, nothing compiled). `ast`-parsing the literal dicts under-counts (entries arrive via loops/`.update()`, the trap documented in `tools/panel_keys.py`). |
| `spec/COVERAGE.tsv` | the 133 contract rows: `category, construct, contract, perimeter, dr_status, mine_status, rel_parity, runtime, probes, corpus, boundary, confidence, provenance` (schema `spec/COVERAGE-SCHEMA.md`) |
| `spec/census/corpus-census.json` | the 44 historical programs: `dr_verdict, rel_present, sha_ok, mine (EXACT/REFUSED/NO_ORACLE), mine_bytes, msg` — gate-verified by `corpus_census.py --verify`, so the dashboard reuses the snapshot and does NOT recompile |
| `spec/census/coverage-stats.json` | COVERAGE tallies (written by `tools/coverage_check.py`) |
| `spec/RUNTIME.txt` | the 71 execution rows (46 `independent`, 23 `dr_oracle`, 2 `non-circular`) |
| `spec/DIVERGENT.txt` | the 9 pinned divergences |
| `tools/panel_keys.py:load()` | name → `exact` / `divergent` / `refused` / `unlisted` |
| `spec/SPECIMENS.tsv` | **NOT USED** — it is one legacy row (E39P1, `ada03ca`), not a registration (measured 2026-11-02; see `LEARNINGS.md`) |

## Files here

- `capabilities.tsv` — the taxonomy: one row per capability a PL/I-80 **programmer** can accomplish,
  plus the COVERAGE rows and corpus programs that bear on it.
- `programs.tsv` — the representative-program inventory: stable id, source, origin class, capability ids.
- Generated report: `docs/functional-status.md` (written by `tools/functional_dashboard.py --write`,
  verified by `--check`; never hand-edit it).

## Verification stages (tracked independently; UNKNOWN is a legal answer)

| Stage | Evidence that licenses it | Never inferred from |
|---|---|---|
| `SYNTAX` | a refusal message whose stage prefix is NOT parser/binder (i.e. it reached `codegen:`), or any later stage | a generic "refused" |
| `BIND` | a refusal message naming bind/binder/declaration resolution, or a later stage | the same |
| `OBJGEN` | a `.REL` produced by my compiler: census `mine=EXACT`, or a panel `specimen` registration | a parse success |
| `BYTE` | the name is a `specimen` on the panel (whole-file `.REL` identity is what the panel means) | `OBJGEN` alone |
| `LINK` | a `spec/RUNTIME.txt` row (every runtime row implies a linked `.COM`) or a named link transcript | `BYTE` |
| `RUN` | a `spec/RUNTIME.txt` row with `exit=ok` and its kind (`independent` / `dr_oracle` / `non-circular`) | a byte-exact object |

DR's side is carried separately and never merged into mine: `dr ACCEPTS` (an authenticated golden
exists), `dr REJECTS` (a `.PRN` diagnostic, no `.REL`), `dr UNMEASURED` (no witness — PROTOCOL #4:
absence of a witness is never a DR rule).

## Origin classes (`programs.tsv` column `origin`)

1. `HISTORICAL` — a program from the DR distribution corpus (`artefacts/*.PLI`, batch
   `golden/first8080u`, 44 names).
2. `FOCUSED` — a probe that is a meaningful whole program exercising a recognizable capability.
3. `MICROPROBE` — a round-bank probe written only to discriminate a codegen hypothesis. **Counts
   must never be summed across classes** — 24 E49 microprobes are not 24 programs a programmer can
   write.
