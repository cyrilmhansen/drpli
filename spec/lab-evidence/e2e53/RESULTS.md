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

## §P3 — entry/label VALUE class (LABELS/DEPREC/MPMCALLA family) — **CLOSED** (2026-11-09, sessions 01a1b8dd hops 1-2 / 01a1b8f6 hop 3 / 01a1b90f hop 4 / 01a1b9b1-01a1ba02 hops 5-9 / 01a1ba17 hop 10 / 01a1ba2f hops 11-12 / this successor hop 13; campaign `e53p3`)

**Scope delivered.** The label/entry VALUE class measured by PLAN §P3: a LABEL variable's cell is a
2-byte word holding **the address of its label's recovery PAD**; storing one is
`LXI H,<code> / SHLD *D(cell)` at a scalar or element-offset-0 target and
`LXI H,*D(elem) / LXI D,<code> / MOV M,E / INX H / MOV M,D` at any other element, the code operand a
PLAIN `RELOC code` backward and a `LINK-CHAIN-ADDR` into the operand slot forward (**NO** JMP opcode);
reading one is `LHLD *D(cell)`, plus one deref `5E 23 56 EB` for a POINTER-formal cell, then `E9 (PCHL)`;
`goto z(i)` on a label array is the existing stride-2 ladder (bias `-lb*2` carried as a DATA reloc even
when the operand reads `0000`) plus the deref plus `E9`. DR demands the saved-SP cell and the pads ONLY
for labels whose VALUE is materialised — a program that merely reads its cells gets neither.
**Goal A payoff is ZERO**: no corpus program advanced to EXACT. Three blockers MOVED and all landed in
new refusals (`[C159/AB5]` for DEPREC/MPMCALLA, exactly as CORRECTION-1 predicted;
`char store from non-literal [TBD]` for LABELS); OPTIMIST's `9-byte [C159]` never moved.

**Campaign.** ONE pre-registered oracle run `E527A..H --tag e53p3 --switches '$L$D'` rc=0 —
**5 ok / 3 dr-refuses**; every accepted `.PRN` `NO ERROR(S)` BOTH passes; goldens committed VERBATIM
`6b3dbef4` BEFORE any `ocaml/lib/` arm byte (`dir.txt` never staged).

**H-verdicts (first-hand `build/e53p3/decode/`, hops 2-4; falsified predictions KEPT, never fitted).**
H-A **FALSIFIED** and H-B **FALSIFIED** — scalar ENTRY stores are DR-REFUSED in BOTH directions
(`E527B`/`E527H`: pass 1 clean, `TYPES NOT=  ?`, 2 ERROR(S) pass 2, no `.REL`); the DEPREC W1 store is an
ARRAY cell, and scalar entry/label cells stay UNMEASURED. H-F **FALSIFIED** — `goto c(i)` on an IMPLICIT
distinct-value label array is `ARG COUNT   ?`; the LABELS witness rides only the shared-`?RECOV`-stub
collapse, nothing is armed on F's authority. H-C **CONFIRMED** (backward `LXI H,<plain RELOC code>/SHLD`;
forward scalar = `CHAIN-ADDR` into the SHLD operand slot). H-D **CONFIRMED** (const-subscript element
store: backward plain reloc, forward self-address pair). H-E **CONFIRMED** (dynamic ladder + deref + `E9`;
the bias word is `21 + RELOC data 0000`). H-G **CONFIRMED** (a label-variable ACTUAL rides the EXISTING
pointer-formal descriptor route — hidden DATA cell `LXI H,*D / RELOC data <cell> / SET-LC code <here>`;
the callee's `goto formal;` is `LHLD` + deref + `PCHL`).

**NEW first-hand law — the STOP-WINDOW (hop 12, [C380]).** A MAIN-level label definition BELOW an
explicit `stop;` emits its recovery pad, which is CODE, so DR still emits the epilogue `CALL ?STOPX'
(E527C `DEF-CODE-SIZE 0030`) and still emits a nested procedure's branch-over `JMP' landing on it
(E527G guard `C3' at 0023, backpatched out-of-band to 0035). Two bounds FALSIFIED the naive law into
existence: **R10** (a procedure declaration's ENTRY NAME is in the same label set but is not such a
definition — no guard, no epilogue) and **E25G/E34A6/E34A7** (labels INSIDE a nested procedure do not
reopen MAIN's window). Implementation is one line: clear `st.stop_seen` at the label-prefix site.

**Arm (committed `b7544b61`; bind.ml + codegen.ml ONLY).** bind: `bytes_of RTlabel -> 2`; sizing shadow
`RTlabel | RTentry _ -> 2` + allow-list arms with the `[C159]`/`[C159/AB5]` strings BYTE-IDENTICAL;
`bind_label_arrays` export; demand class `Rk_val` (label name as assignment RHS to a label/entry-class
LHS), threaded through the ref walker; PADDEBUG `:val`. codegen: `Vlbl` vkind; EVERY `RTlabel` row
registered (hop-11's array-skip proposal **FALSIFIED** — `addr_of_raw` needs the array row, and
DEF-DATA-SIZE rides `max auto_bytes pl_total`); `lbl_arrs` save/set/restore mirroring `st.arrays`;
`lbl_val_operand` 5-case (here/pad, forward self-slot `00 00` + `ls.fwd` cons WITHOUT a JMP, pad-forward
REFUSED as unmeasured); `lower_label_assign` dispatched behind a candidate test (so the B/H deaths are
preserved verbatim); Vlbl-first plain `goto`; the measured dynamic computed-goto arm with the catch
`codegen: computed GOTO deferred [TBD]` kept VERBATIM (N6 marker).

**Parity + falsifiers.** FRESH POSITIONAL whole-file `cmp` **5/5 rc=0** vs `golden/e53p3/` in
`build/e53p3/arm-out/` (A 128 B CODE `001D` DATA `0004`; C 256 B `0030`/`0008`; D 128 B `002D`/`000A`;
E 128 B `001E`/`0008`; G 256 B `0038`/`0008`). Mismatches at hop 11 were RECORDED and adjudicated from
the KEPT goldens, never fitted. B/H (`undeclared e (no declaration in scope)`) and F
(`computed GOTO deferred [TBD]`) byte-identical to the pre-arm baseline
`build/e53p3/pre-arm-hop10/`; the `nelem=1` crash unchanged (`lib/codegen.ml:10189 Pattern matching
failed`, RECORDED, never fixed); sweep `build/e53p3/sweep-h12b.log` **201 byte-exact / 0 FAILS**.

**Registration + claim + coverage.** 5 SPECIMENS in `tools/e2e_gate.py` with measured-byte comments;
REAL `--update-inventory` OWN output **1323 → 1328**, refusals 190 UNCHANGED; census OWN path counts
**16/0/25/0** with three corpus messages MOVED VERBATIM. **C380** written BEFORE any `spec/COVERAGE.tsv`
touch (ledger ends C380, 203 headers). Coverage FIRST-HAND, BY HAND (`coverage_gen.py` NEVER used): row
101 `TRAN.COMPUTED_GOTO` UNTESTED/REFUSED → **ACCEPTS / PARTIAL / EXACT:1** — NOT retired, because the
constant-subscript and non-label-target classes still refuse with the `computed GOTO` phrase — plus
THREE new rows `TRAN.LABEL_VALUE_CELL` (EXACT:3, MEASURED), `TRAN.LABEL_AS_ACTUAL` (EXACT:1,
SINGLE_SAMPLE), `TRAN.STOP_TAIL_WINDOW` (EXACT:2, MEASURED); ids appended explicitly to
`spec/COVERAGE-IDS.txt`. `coverage_check` **149 rows, 0 errors, 0 warnings**; its own canonical output at
close time is **SUPPORTED 99 / PARTIAL 24 / REFUSED 20 / DIVERGENT 3 / NOT_ATTEMPTED 3** (the 96 quoted
mid-campaign was the 146-row state before these adjudications — the count moves BY ADJUDICATION and is
recorded here, not reused).

**Close-out tail (hop 13, all numbers COMPUTED).** Armed fingerprint **`fed67d24297d5e85ffc6b74d654c44e8c066ad23d757762306d31f62f597cb5a`**
re-produced on a FRESH `--build-dir _build-e53p3h13` (ZERO `Error`, binary IDENTICAL to the tree);
markers harness argv-19 **`MARKER_FAILS: 0` rc=0** incl. `N6_COMPUTED_GOTO` still refusing with the
pinned phrase (`build/e53p3/markers-h13.log`); DEC regressions **64/0 FAILS**
(`build/e53p3/dec-h13.log`); divergence panel **9/9** (`build/e53p3/divcheck-h13.log`); FULL gate
**rc=0** `build/gate-e53p3-reg3.log` (1328/1328, 190/190, 9/9, 149 rows, census 16/0/25/0, prose 5).

**NEW my-gap found BY THIS TAIL CHECK, recorded VERBATIM and NOT fixed.** The contract predicted
hist 68/124; measured **codegen 72 / total 128**, delta +4 = exactly TWO new sites, both from this arm:
(1) `lib/codegen.ml:14789` `Warning 27 unused variable idx` (the dynamic computed-goto guard binds `idx`
and uses `sidx`) — cosmetic; and (2) a NEW `Warning 8 partial-match` on **`vk_name`** (`codegen.ml:7076`),
which gained an unmatched `Vlbl` case when the `Vlbl` constructor was added. (2) is a **LIVE CRASH
PATH**, not just a warning: first-hand witness `build/e53p3/h13-sanity/SNSL6.PLI`
(`dcl x label; … f = 1.0 + x;`) dies `Fatal error: exception File "lib/codegen.ml", line 7076,
characters 2-7: Pattern matching failed` instead of a loud `[TBD]` refusal, and `SNSL8.PLI`
(`put list(x);`) crashes the same way at `codegen.ml:13455`. A label variable reaching ANY
`vk_name`-formatting refusal (nine call sites) or any vkind dispatch that predates the arm now crashes.
Classified **my-gap**, recorded here rather than fitted, because hop 13 is a close-out hop with no
compiler edits authorized; the fix is PRE-REGISTERED in `LEARNINGS.md` § "hop 13" (fail-loud for `Vlbl`
at every consumer, plus the histogram repair, ZERO oracle needed for the message sites but the byte-tier
falsifier suite is mandatory since `vk_name` text appears in refusal markers the gate pins).
BYTE TIER ONLY — nothing linked or run.

## §P4 — label-kind hygiene: fail-loud closure of the §P3 `Vlbl` my-gap — **CLOSED** (2026-11-09, sessions 01a1bb05 hop 14 / 01a1bb21 hop 15 / this successor hop 16; **ZERO oracle — the pre-registered tag `e53p4` and ids `E528*` were verified UNUSED and stayed UNUSED, no probe, no golden**) — PRE-REGISTERED in `PLAN.md` §P4 BEFORE any `ocaml/lib/` byte

**What P4 is, and what it deliberately is not.** §P3 introduced the `Vlbl` value kind and §P3's own tail
found the cost: the kind reached lowering through paths that had never been written for it, so a label
variable either crashed with OCaml's `Pattern matching failed` or — worse — compiled SILENTLY into an
object with no DR witness behind the operation. P4 closes exactly that. It is **internal failure-mode
hygiene, not a reproduction result**: it adds no DR law, so there is **no claim** (the ledger stays at
**C380**, 203 headers), **no inventory change** (1328 specimens / 190 refusals, verified UNCHANGED by the
gate rather than regenerated), **no coverage touch** (149 rows, `SUPPORTED 99`), and **no Goal A payoff**
(no corpus program moved). `ocaml/lib/codegen.ml` is the ONLY file edited, in hop 15; hops 14 and 16 wrote
zero compiler bytes.

**Arm (committed `39c7919e`; edits (a)–(j) exactly as pre-registered in `PLAN.md` §P4, every one guarded on
`vk = Vlbl` so no other kind's behaviour can move).** (a) `vk_name` gains `| Vlbl -> "label"`, making that
match EXHAUSTIVE again — the nine refusal-formatting call sites now name the variable class instead of
crashing; (b) the unused `idx` of the dynamic computed-goto guard becomes `_idx`; (c) an OUTER `| Vlbl ->`
arm in the PUT-item dispatch refuses `codegen: PUT of a LABEL value is unsampled [TBD] (no DR golden prints
a label variable through a LIST, EDIT or skip item; E527 measures only store/goto/call-use of a label cell)`;
(d) `store_char` gains `| Vlbl -> failwith "codegen: character store into a LABEL cell is unsampled [TBD]
(E527 measures only label-value stores; a ?SMCVM/?SMCCM string never lands in a label cell)"` (the OTHER
missing kinds of that pre-existing partial were left alone — not label scope); (e)/(f) `val_addr` and
`cmp_load_deref` refuse via `List.assoc_opt … st.vars` on `vk = Vlbl` (`comparing a LABEL variable is
unsampled [TBD]`), deliberately NOT via `vk_of`, so no new failure mode appears for any other name;
(g) the DEC->INT store arm refuses `vi.vk = Vlbl` (`DEC->INT conversion store into a LABEL cell is
unsampled [TBD]`); (h) an internal call actual that is a bare `Eident` with a `Vlbl` row is admitted ONLY
when the callee's formal at that position has rt `Bind.RTlabel` — the single pair E527G measures — else
`passing the LABEL variable x as a call argument is unsampled [TBD]`; (i) an EXTERNAL entry actual of that
shape refuses (no external golden passes a label); (j) a bare-`Eident` array SUBSCRIPT with a `Vlbl` row
refuses (`array subscript is a LABEL variable [TBD]`). Every text is NEW wording containing `[TBD]`; no
pinned marker or census string was touched, which is why the markers harness was re-run FIRST.

**Post-fix matrix (FRESH `build/e53p4/post/run.log` vs the pre-arm witnesses `build/e53p4/sanity/`, binary
`172595d5…`; 34 programs + the 13 hop-13 SNSL witnesses).**

| Pre-arm state | Witness(es) | Post-arm state (rc DIRECT) |
|---|---|---|
| CRASH `Pattern matching failed` at `vk_name` (was 7076) | SANL3, SANL27, SNSL6 | LOUD rc=2, ZERO `.REL`: `mixing label into a FLOAT expression is unsampled [TBD]` |
| CRASH at PUT-item inner match (13455, pre-existing partial newly REACHED) | SANL4, SANL17, SANL25, SNSL8 | LOUD rc=2, ZERO `.REL`: `PUT of a LABEL value is unsampled [TBD]` |
| CRASH at `store_char` (6095, pre-existing partial newly REACHED) | SANL5 | LOUD rc=2, ZERO `.REL`: `character store into a LABEL cell is unsampled [TBD]` |
| SILENT object, no DR sample — DEC->INT store | SANL14 (pre: rc=0, 256 B) | LOUD rc=2, ZERO `.REL` |
| SILENT object — fixed compare ladder | SANL21 (pre: rc=0, 256 B) | LOUD rc=2, ZERO `.REL` |
| SILENT object — label actual to FIXED / POINTER formal | SANL22, SANL32 (pre: rc=0, 256 B) | LOUD rc=2, ZERO `.REL` |
| SILENT object — label as array SUBSCRIPT (read and write) | SANL23, SANL24 (pre: rc=0, 128 B) | LOUD rc=2, ZERO `.REL` |
| ARMED shapes must not move | SANL19 `goto x;`, SNSLC float control | rc=0 and **byte-IDENTICAL** (`SANL19.REL` 128 B code=33 data=18; `SNSLC.REL` 256 B code=43 data=4, `cmp` rc=0) |
| Loud-and-correct controls | the other 29 `SANL*.err` | **byte-identical** to the kept pre-arm files (incl. `addr(x)`, `if x then`, DO bound/index, `x = f`, `char store from non-literal`) |

**Parity.** FRESH POSITIONAL whole-file `cmp` against the KEPT goldens VERBATIM — **16/16 rc=0**
(`build/e53p4/parity/cmp.log`, `PARITY_CMP_FAILS: 0`): e53p1 E525A–D 4/4, e53p2 E526A–G 7/7, e53p3
E527A/C/D/E/G 5/5, with the §P3 refusals preserved exactly — E527B/H `undeclared e (no declaration in
scope)` and E527F `computed GOTO deferred [TBD]` (the N6 phrase).

**Falsifiers.** Markers harness argv-19 **`MARKER_FAILS: 0`** (`build/e53p4/markers.log`) — run first,
because nine refusal sites embed `vk_name` output. Corpus deaths UNMOVED: the seven recorded blockers
(EXPR1, REPORT, COPYLPT, LABELS, DEPREC, MPMCALLA, OPTIMIST) are **byte-identical** to the kept
`build/e53p3/fals/*.log`. Census `--check` **rc=0** with counts **16/0/25/0** unchanged
(`build/e53p4/census-check.log`). **DATED site quotation:** the separately recorded, OUT-OF-SCOPE
`nelem=1`/scalar-subscript crash (`SANL33`, SNSLD — `x(2) = lab1;`) is **UNCHANGED in kind** — still
`Pattern matching failed`, still the same recorded site — but its quoted LINE moved **10189 → 10248**
by the +59-line shift the P4 arms introduced above it; any later prose must quote **10248**. It stays
recorded and unfixed.

**Fingerprint and histogram.** Armed fingerprint **`172595d52be44c9ead2404674f02bcce3ba7fc252915e13ce10040a5d5aca281`**
— fresh `--build-dir _build-e53p4h15`, **ZERO `Error`** (`build/e53p4/build-fresh-h15.log`), IDENTICAL to
the default-build tree binary re-checked at hop 16; it **SUPERSEDES `fed67d24…`**. Warning histogram
**FALSIFIED its own prediction:** §P4 predicted **68/124**, measured **codegen 66 / total 122** — and the
delta is attributed first-hand to **THREE** sites, each −2 (the build runs two passes), by header-set
comparison against `build/e53p3/build-fresh-h13.log`: (1) the predicted `14789` unused-`idx` W27 (edit (b));
(2) the predicted `vk_name` W8 header `lines 7076-7091` (edit (a)) — the match became EXHAUSTIVE because
`Vlbl` was the last missing `vkind` constructor, which is why it costs 2 headers, not the 0 a single-arm
edit would; and (3) **UNPREDICTED** `resolve_suffix` `1067 characters 30-31` W27 (shadowed unused `h`) —
consumed legitimately by edit (j), whose guard uses `h.Ast.orig`. No other header moved. Nothing was forced.
Lesson kept: removing a partial match can silence a `partial-match` header AND expose or consume
unrelated per-variable warnings at the same address range; a histogram prediction is a signal, not a target.

**Close-out tail (hop 16, all rc DIRECT, ZERO oracle, ZERO further `ocaml/lib/` byte).** Sweep
`python3 build/e52p3/sweep.py E46N E46K E51 E52 P086 R10` **rc=0, 206 specimens byte-exact / 0 FAILS /
28 refusals** (`build/e53p4/sweep.log`); DEC `R5 R6 R7 R8 LOAN1` **64 byte-exact / 0 FAILS**
(`build/e53p4/dec.log`); divergence **9/9** (`build/e53p4/divcheck.log`). **The carried sweep expectation of
201 MOVED to 206 and is recorded, not forced** — attribution first-hand: the §P3 close-out quoted the sweep
number measured against the PRE-registration inventory (1323 rows), while §P3 then registered the five
E527 specimens in `b7544b61` (1328). Counting the same six prefixes in the pre-registration inventory gives
exactly **201**, in the current one exactly **206**, the difference being precisely
E527A/C/D/E/G, each re-verified individually byte-exact against `golden/e53p3/` on `172595d5…`. Refusal
count 28 and `FAILS: 0` are unchanged; the compiler's behaviour did not move — the STALE EXPECTATION did.
**FULL compile-tier gate rc=0** DIRECT `build/gate-e53p4-reg.log`: **1328 byte-exact / 0 fail of 1328**,
negative panel **190/190**, divergence **9/9**, `coverage_check` **149 rows, 0 errors, 0 warnings**, census
`{EXACT 16, DIFFERS 0, REFUSED 25, NO_ORACLE 3}`, prose **5 active files clean**.

**Tooling law re-confirmed (SNS4 name collision).** `build/e53p4/fals/run.log` carries a stale
`SNS4 rc= 2` line from a first pass that resolved the colliding name to `build/e53p3/sanity/SNS4.PLI`
(the `dcl e(2) entry;` probe). The legacy array witness is `build/e53p2/sanity/SNS4.PLI`; the held artifact
`build/e53p4/fals/SNS4.REL` is correct, and the hop-16 re-check (`build/e53p4/fals/sns4-recheck-h16.log`)
re-compiled that pinned source rc=0 with `cmp` rc=0 against the pre-P2 reference
`build/e53p2/sanity/SNS4.out.rel` (sha `c6ad9b56…`, all three identical). Pin the SOURCE PATH, never the
directory name.

**Explicitly NOT done in P4 (queued, never silently improved).** The `char(2)` twins of the store and
compare holes are pre-existing kind-agnostic looseness and were recorded, not touched — fixing them would
put 900+ specimens at risk with no label authority; the `nelem=1`/scalar-subscript crash at `10248` stays
recorded; A3/A4 (char builtins, FLOAT-expression-as-actual) and the B1 static-varying residue ride future
oracle campaigns. BYTE TIER ONLY — nothing linked or run.
