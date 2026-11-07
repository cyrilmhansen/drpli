# E2E-53 — Compiler Coverage Expansion — ROUND RESULTS

Byte-tier only (`.REL` whole-file `cmp` against DR objects; nothing linked or run).
Classification per PROTOCOL Part 1; ledger `spec/CLAIMS.md` is the authority.

## §P1 — GET SKIP family — **CLOSED** (2026-11-08, session 01a1b82b hop 3; campaign `e53p1`)

**Scope.** Arm the console GET SKIP statement family (bare `get skip;`, constant
`get skip(<n>);`, `get skip list(<fixed-bin var>);`, `get skip list(<char varying var>);`)
to whole-file byte-exactness on DR-witnessed bytes ONLY; every other GET form keeps the
preserved `GET form not in E2E-3e subset [TBD]` catch.

**Provenance chain (committed order, PROTOCOL #1 honoured):** pre-registration
`2ba9d0ca` (PLAN §P1.1–§P1.6 + `probes/E525A..D` CRLF + bare `^Z` + LEARNINGS) BEFORE any
oracle call or `ocaml/lib/` byte → ONE campaign `PLI_SRC=probes timeout 900 python3
oracle/batch.py E525A E525B E525C E525D --tag e53p1 --switches '$L$D'` rc=0 **4 ok/4**,
EVERY `.PRN` `NO ERROR(S)` BOTH passes → goldens VERBATIM `be66e654` (sizes/sha12 below)
→ arm `53dd4a9f` (`ocaml/lib/codegen.ml` only: `match_get_skip` matcher, `lower_get_body
~skipn` emitting `MVI A,n / CALL ?SKPOP` after the `?SYSIN` attach, `lower_get_skip`
dispatch before `match_get_list_var`; PUT bytes NEVER consulted) → durables `4fdd6cf8` →
registration `1212bb25` → **C378 `3b904631` BEFORE ANY `spec/COVERAGE.tsv` contact** →
coverage `5c8d89c1` → gate `build/gate-e53p1-reg.log` rc=0.

**Parity table (whole-file `cmp` rc=0, FRESH POSITIONAL `pli80c.exe IN OUT` NO `-o`,
armed binary sha256 `8e51c261…`, re-held at claim time `build/e53p1/claim-out/`):**

| Probe | Statement | Golden | Bytes | CODE | DATA | sha12 | cmp |
|---|---|---|---|---|---|---|---|
| E525A | `get skip;` | `golden/e53p1/E525A/E525A.REL` | 128 | `001A` | `0000` | `f5660e23d5f4` | rc=0 |
| E525B | `get skip(2);` | `golden/e53p1/E525B/E525B.REL` | 128 | `001A` | `0000` | `6589ac82b59` (full `f6589ac82b59`) | rc=0 |
| E525C | `get skip list(n);` `n fixed binary` | `golden/e53p1/E525C/E525C.REL` | 256 | `0026` | `0002` | `6bbae5752840` | rc=0 |
| E525D | `get skip list(s);` `s char(10) varying` | `golden/e53p1/E525D/E525D.REL` | 256 | `0028` | `000B` | `5f1981266c3c` | rc=0 |

**§4 hypotheses — ZERO misses (all four CONFIRMED first-hand, `build/e53p1/decode/`):**
H-A bare form = 17-B prefix with count `01`; H-B constant count rides the `MVI A` operand
verbatim (`3E 02` at `000F`, the ONLY byte differing from A); H-C fixed-bin tail `GNVOP /
JP(→own ?QIOOP opcode) / QCIOP / SHLD(cell)` 11 B; H-D varying tail `GNVOP / JP / LXI
H,*D(desc) / MVI B,0A / SSVFS` 14 B.  The continuation word (`LXI B`) targets the NEXT
statement's first opcode in every witness.

**DATED CORRECTION (falsified carried fact, zero-oracle):** the campaign-open contract
quoted the attach as `?SIOOP`; the KEPT goldens say **`?SYSIN`** (EXPR1 slot `0051`,
DEPREC `041B`, COPYLPT `0090`/`0134`, REPORT `006C`).  The 17-B geometry itself stands.
Correction also written into PLAN §P1.5, the SPECIMENS comment, COVERAGE row 64 col04 and
C378.

**Corpus rerun (UNMODIFIED sources, `build/e53p1/corpus-out/`) — blockers moved VERBATIM
past the GET lines, NOTHING fixed:** EXPR1 → `FLOAT expression shape builtin is unsampled
[TBD] (line 29)`; REPORT → `OPEN option KEYED … (line 27)`; DEPREC → `array of 0-byte
elements [C159]`; COPYLPT → `PUT FILE(PRINTFILE) LIST item 2 is the control item SKIP with
a count … (line 65)` (all rc=2; corpus newly-EXACT count this slice = 0).

**Perimeter (armed, first-hand `build/e53p1/perim/`, all rc=2 NO `.REL`):** variable-count
`get skip(n)` and multi-control forms keep the E2E-3e catch; `get list(..) skip` order is
the pre-existing PARSER refusal; FILE-route `get file(f) skip;` stays UNMEASURED (my OPEN
parse guard fires first — no claim about DR file-skip bytes); fixed-char/subscripted items
keep `GET LIST of this target kind is unproven` (N44/N45 provenance); multi-item skip lists
NOT promoted.  N45_GETSUB and E46K15 markers survive.

**Numbers:** inventory **1316/190** (REAL `--update-inventory` OWN output, exactly +4
specimen rows); census OWN path UNCHANGED **16/0/25/0**; coverage row 64 `IO.GET_LIST`
EXACT:24→**28** (+E525A..D; NEVER `coverage_gen.py`), `coverage_check` 145 rows 0/0
SUPPORTED 95; FULL gate **rc=0 DIRECT** `build/gate-e53p1-reg.log` — 1316 byte-exact/0
fail, 190/190 NEG-OK (incl E523C my-gap VERBATIM), 9/9 DIV, 145 rows, census 16/0/25/0,
prose 5 — EVERY pre-registered number HIT.  Ledger ENDS **C378** (201 headers).

**Tool lessons (recorded in LEARNINGS hop 3):** (1) sweep counts must be COMPUTED from
panel deltas — the contract's quoted 187 was already stale (measured 190 pre-reg, 194
post-reg); (2) `p13dump` needs explicit `lohi` ranges and prints operand-slot addresses
in plain hex — an empty dump is not a zero-byte golden; (3) `corpus_census.py --check`
takes the snapshot path as its argument; (4) a registration-comment draft that mislabels
chain slots is caught only by re-deriving from raw hex before composing (caught, fixed
pre-commit).

**Next:** re-rank matrix, open **P2 = B1 non-2-byte arrays** (4 corpus users, highest
Goal-A payoff per §3) — ids `E526*`/tag `e53p2` must be VERIFIED UNUSED and §P2
PRE-REGISTERED before any oracle call or `ocaml/lib/` byte.
