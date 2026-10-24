# spec/COVERAGE.tsv schema — E2E-37/P2

Purpose: a machine-readable statement of **what this compiler is known to do, against what
evidence, and where the boundary of that knowledge is**.  It is not a language checklist and it is
not a coverage percentage.  Nothing in this file should be read as "the language is covered": the
population it samples is DR PL/I-80 v1.4 as evidenced by the 41 authenticated historical goldens,
the ~1000 panel entries in `spec/INVENTORY.txt`, and `spec/CLAIMS.md`.  Constructs that neither the
corpus nor any probe exercises appear here with `confidence=UNREVIEWED`, and that is the honest
answer, not a gap to be filled by inference.

Source of truth for manual references: `manuals/PL1-80_Language_Manual_Dec80.pdf`
(sha256 `85e09fc830a3520d…`, 115 pages, OCR).  The OCR text is banked at
`spec/manuals/PL1-80_Language_Manual_Dec80.txt.gz` so that `tools/coverage_check.py` can verify a
page cite without re-running OCR.  Printed page *p* is PDF page *p+7* in that extraction (verified:
printed 1 = PDF 8, printed 7 = PDF 14).

Columns (tab-separated, one header line, no trailing whitespace, no embedded tabs):

| # | column | values / rule |
|---|---|---|
| 1 | `id` | `<CATEGORY>.<slug>` upper case, unique, never renumbered. A retired contract keeps its id and becomes `status=SUPERSEDED`. |
| 2 | `category` | one of `LEX DECL AGG STOR EXPR COND LOOP TRAN PROC IO FILE OBJ ABI RTME NEG` |
| 3 | `construct` | the construct as written in DR/PL/I syntax (short, literal where possible) |
| 4 | `contract` | the **semantic or lowering assertion** verified — what must be true, not which keyword parses. Must not be a restatement of `construct`. |
| 5 | `perimeter` | the existing PERIMETER.md class: `S` = DR supports it (in the shipped language), `M` = manual and DR disagree, `C` = outside what DR ships (correctly absent), `OPEN` = unresolved. `mine_status` carries a gap; `perimeter` never does. |
| 6 | `dr_status` | `ACCEPTS` (a DR `.REL` exists for a probe of it) · `REJECTS` (DR diagnosis recorded, no `.REL`) · `ACCEPTS_DEFECT` (DR accepts and its output is wrong in a way we reproduce deliberately) · `UNTESTED` (no DR probe of this shape has been run) |
| 7 | `mine_status` | `SUPPORTED` (compiles and every specimen is byte-exact) · `DIVERGENT` (compiles; at least one pinned divergence) · `REFUSED` (deliberate refusal at a perimeter edge) · `PARTIAL` (some shapes supported, others refused by name) · `NOT_ATTEMPTED` (no implementation and no refusal design — would fail however it fails) |
| 8 | `rel_parity` | raw `.REL` byte parity, never listing/output parity: `EXACT:<n>` · `DIVERGENT:<n>` · `MIXED:<e>/<d>` · `NONE` |
| 9 | `runtime` | `NONE` · `INDEPENDENT:<n>` (linked+run against a hand-derived expectation) · `DR_ORACLE:<n>` (run against DR's own transcript) · `BOTH:<n>` |
| 10 | `probes` | comma-separated panel keys (`spec/INVENTORY.txt`) and/or golden dirs; every entry must resolve to a file that exists |
| 11 | `corpus` | historical-corpus users by name, from the 44-program census; `NONE` means no authenticated historical program exercises this — that is a fact about the corpus, not about the feature |
| 12 | `boundary` | the unresolved boundary in one sentence, or `NONE` |
| 13 | `confidence` | `MEASURED` (≥3 independent specimens) · `SINGLE_SAMPLE` · `INFERRED` (derived from a nearby measurement, not probed directly) · `UNREVIEWED` (never probed here; text says so) |
| 14 | `provenance` | claim ids `[Cnnn]` and/or note files; at least one, and every `Cnnn` must exist in `spec/CLAIMS.md` |

Deliberate distinctions the validator enforces:

* `UNTESTED` (no DR probe run) is not `REFUSED` (we refuse) is not `NOT_ATTEMPTED` (we have not
  even designed a refusal) is not `UNREVIEWED` (we have not looked).  Collapsing them is how a
  coverage table becomes self-congratulatory.
* `rel_parity` counts raw `.REL` comparisons only.  A formatted-listing match proves nothing about
  bytes and is never cited as parity.
* A `perimeter=C` row may not have `mine_status=SUPPORTED`; if we implement what DR does not ship,
  that is a reimplementation decision and belongs in `boundary`.
* Rows with `confidence=UNREVIEWED` must have `rel_parity=NONE` and `runtime=NONE`.

Maintenance: add a row when a contract is *established or falsified*, not when a specimen is added.
A specimen belongs to an existing row unless it changes what is known.  Run
`python3 tools/coverage_check.py` after any edit; it must exit 0 before commit.

## Categories

`LEX DECL AGG STOR EXPR COND LOOP TRAN PROC IO FILE OBJ ABI RTME NEG BUILTIN`.
The set lives in `tools/coverage_check.py` (CATS/PREFIX); a new category must be added to both, and the
last one added the hard way: `NEG` was missing a comma in the set literal, which made it an unknown
category, and the id/category checks were an `if/elif` chain, so a well-formed id masked it for the
whole episode.  Both are fixed; `BUILTIN` was added for the section-12 audit.

## Columns, explicitly

| # | name | meaning | allowed |
|---|---|---|---|
| 1 | `id` | `<CATEGORY>.<SHAPE>` | category must be the row's own `category` |
| 2 | `category` | one of the 16 declared categories | see *Categories* above |
| 3 | `construct` | the shape, written as source text | free |
| 4 | `contract` | what is actually established about it — DR's behaviour, the instruction sequence, the sizes | free, but must be an *observed* claim |
| 5 | `perimeter` | whose restriction is it | `S` both accept, `M` mine only (a defect in me), `C` faithfully-adopted DR constraint, `OPEN` unmeasured |
| 6 | `manual_ref` | `pNN[:§X.Y][=verbatim phrase]` or `NONE:<why>` | a cite with `=phrase` is checked against the OCR of that printed page |
| 7 | `dr_status` | DR's verdict, measured | `ACCEPTS`, `ACCEPTS_DEFECT` (emits bytes its own docs contradict), `REJECTS`, `UNTESTED` |
| 8 | `mine_status` | my verdict | `SUPPORTED`, `PARTIAL`, `REFUSED`, `DIVERGENT`, `NOT_ATTEMPTED` |
| 9 | `rel_parity` | raw `.REL` comparisons | `EXACT:n`, `EXACT:n/DIFFERS:m`, `DIFFERS:n`, `NONE` |
| 10 | `runtime` | linked-image witnesses | `NONE`, `UNVERIFIED`, `INDEPENDENT:n`, `CORROBORATING:n`, `CONTRADICTS_DR:n`, `n/m` |
| 11 | `probes` | specimen keys and/or paths that carry the evidence | every key must be on the panel, a corpus program, or an existing file |
| 12 | `corpus` | corpus programs this row explains | must be one of the 44 |
| 13 | `boundary` | what this row does *not* settle, and why | free |
| 14 | `confidence` | how much the evidence is worth | `MEASURED` (2+ independent witnesses), `SINGLE_SAMPLE`, `INFERRED` (one accepted shape — forced on `rel_parity`/`runtime`), `UNREVIEWED` (nothing above it holds — forces `rel_parity=NONE`, `runtime=NONE`) |
| 15 | `provenance` | claim refs, sweep files, episode notes | a `MEASURED` row's probes must be nameable in a cited claim or note |

**Do not hard-code row or category counts in prose.** A count in a header goes stale the moment a
row is added, and three documents in this repo did exactly that in E2E-37 ("71 rows", "15
categories", "71 numbered claims").  Run `python3 tools/coverage_check.py` for the current tally,
and `tools/corpus_census.py` for corpus counts; the claims file's structure is described below
rather than by a number.

## Categories in use — 83 rows, 15 of 16 declared categories populated (E2E-38)

`DECL 17 · COND 7 · EXPR 12 · STOR 8 · PROC 8 · AGG 6 · TRAN 6 · IO 5 · LOOP 4 · LEX 3 · OBJ 3 ·
ABI 1 · BUILTIN 1 · NEG 1 · RTME 1 · FILE 0`.

The first version of this table said `DECL 15 · COND 6` and was stale before the sentence ending the
previous section was written: the six rows added in the same session had not been counted.  That is
the argument for the paragraph above, not an argument for being more careful — recompute it from
`tools/coverage_check.py`'s output.

`FILE` is declared and unused: the file-oriented refusals are currently carried by `DECL.FILE_NAME_LEN`
and the `IO`/`RTME` rows.  A declared-but-empty category is not an error, but it should not be read
as coverage.

## Claim-file structure

Claims are cited by number (`[C072]`) and never by prose title.  They are spread over three formats
— `## Cnnn — title` with `- status/evidence/prose/covers/depends` keys in `spec/CLAIMS.md`,
`Cnnn. [E2E-..]` blocks, and `## Cnnn` blocks inside `spec/notes/*.md` — so the count and the
numbering are not contiguous: `spec/CLAIMS.md` itself begins mid-index (its first line is a `| C079
|` table row) and C001–C078 live in the notes.  `tools/coverage_check.py` loads all three formats;
its first version recognised only one, and silently validated citations against a subset of the
corpus.  A withdrawn claim stays in the file with its status changed to `WITHDRAWN` and a pointer to
what replaced it (see [C245] → [C250]): a claim is a record of what was believed when, and deleting
it destroys the audit trail that makes the correction visible.
