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

## §P2 — non-2-byte array elements (B1 class) — **CLOSED** (2026-11-08, sessions 01a1b875 hop 2 / 01a1b88b hop 3 / 01a1b89d hop 4 / 01a1b8b4 hop 5 / this successor hop 6; campaign `e53p2`)

**Scope delivered.** The plain automatic stride class measured by PLAN §P2: `fixed bin(7)`
arrays (1-byte cells) and `char(3)` arrays (3-byte cells) — constant subscripts folding to data
displacements, variable subscripts through the bias ladder with the multiply REPLACED BY THE
STRIDE (and OMITTED entirely at stride 1). Entry/label-value arrays, static-varying descriptors
and char(1) elements stayed refused BY NAME exactly as pre-registered; Goal A payoff is ZERO
(the arm clears none of the four B1 blockers — this slice is Goal-B coverage).

**Campaign.** ONE pre-registered oracle run `E526A..G --tag e53p2 --switches '$L$D'` rc=0
7 ok/7; every `.PRN` `NO ERROR(S)` BOTH passes (re-counted 2 lines/file at claim time);
goldens committed VERBATIM `d55ec7b5` BEFORE any `ocaml/lib/` arm byte (`dir.txt` never staged).

**H-verdicts (adjudicated FIRST-HAND from `build/e53p2/decode/`, every byte re-verified at
claim time):** H-A CONFIRMED (offset-0 `MVI A,v/STA`; offset≠0 `LXI H,*D/MVI M,v`); H-B CONFIRMED
(folded `LDA *D(elem)` + sign-extend ladder `6F 87 9F 67` + `SHLD`; PUT item `MVI A,07/?QICOP/?PNVOP`);
**H-C, H-D-ladder and H-G MULTIPLY PREDICTIONS FALSIFIED** — stride 1 emits NO `DAD H`, NO
`LXI DE,0001` and NO `?IM22N` in EITHER bias form (bias≠0: `21 FF FF/E5/2A r(i)/D1/19`; bias=0:
`2A r(i)/11 r(base)/19`, 7 bytes, no PUSH/POP); H-E CONFIRMED (`?SMCCM` len<cap store and
`?SLCTS + MVI A,03/?PNCOP` read on the ELEMENT address; pool literal FIRST in DATA, E526E
`DEF-DATA-SIZE 000B` = 2+9); H-F CONFIRMED (OPTIMIST IM22N ladder generalises verbatim to
stride 3: `LXI DE,0003/CALL ?IM22N`). Falsified predictions kept, never fitted.

**Arm (committed `9ac4181a`, hop-4 `cfc8859b`, bind.ml + codegen.ml only).** bind rt-FORM
allow-list `RTbin 7→1`, `RTchar(3,false)→3` (refusal string byte-identical); `dyn_ref.dyn_esz`
+ `dyn_addr` stride dispatch; `lower_hl` ez=1 read; ez=1 literal store `0≤v≤127`; ez=3 string
stores via `store_char ~dst`; hop-5 root cause was DISPATCH SHAPE, not the guard (statement
match FELL THROUGH into `lower_hl`/`num_width`; TRACE-ITEM falsified "guard never fires");
arms now return `char_item_emitted` gating the numeric tail. `aw <> 2` element-as-ACTUAL refuses.

**Parity + falsifiers.** FRESH POSITIONAL whole-file `cmp` 7/7 rc=0 (sizes 128/256/256/128/256/
128/256; CODE `0013/002E/002B/0014/002D/0022/0029`; DATA `0004/0006/0006/0006/000B/000D/0006`)
`build/e53p2/hop5-parity/`, RE-HELD at claim time `build/e53p2/c379-out/` on binary
`cb906871…`. Legacy falsifiers all held VERBATIM (`build/e53p2/hop5-falsify/`): SNS4
byte-identical; DEPREC/LABELS/MPMCALLA `0-byte [C159]`, OPTIMIST `9-byte [C159]`; EXPR1/REPORT/
COPYLPT unmodified. Tail: fresh `--build-dir` binary IDENTICAL, ZERO `Error`; hist 68/124;
sweep 194/0 FAILS 0; markers 19/19 (erratum: real name `N6_COMPUTED_GOTO`); DEC 64/0; divcheck 9/9.

**Registration + claim + coverage.** SPECIMENS +E526A..G with measured-byte comments (REAL
`--update-inventory` OWN output 1323/190, `b2f0d474`); census `--check` rc=0 counts UNCHANGED
16/0/25/0 (snapshot refresh `36efba7c`). **C379** `8364798e` measured-bytes-only BEFORE any
COVERAGE touch (202 headers). Coverage adjudicated FIRST-HAND **NEW row `AGG.ARRAY_1D_STRIDED`**
(not an EXTEND of row 7: its contract states the 2-byte-specific law verbatim) + explicit
`spec/COVERAGE-IDS.txt` entry, `fafda045`; coverage_check 146 rows 0/0, SUPPORTED 96 — the
contract's 145/95 reflected the EXTEND option, the count moves BY ADJUDICATION and is recorded.
FULL gate **rc=0 DIRECT** `build/gate-e53p2-reg.log`: 1323/0 byte-exact, 190/190 NEG, 9/9 DIV,
146 rows, census 16/0/25/0, prose 5 — every number hit. BYTE TIER ONLY; `nelem=1` crash remains
RECORDED, not fixed; zero corpus programs advanced.
