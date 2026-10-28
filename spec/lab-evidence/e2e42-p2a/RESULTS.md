# E2E-42 / P2a-B — the eleven predictions against DR, and three of them being wrong

Oracle: `PLI_SRC=probes python3 oracle/batch.py E46L1..E46L11 --tag e42p2a --switches '$L$D$S'`
under the vendored `thirdparty/z80pack/cpmsim/cpmsim`, `oracle/runner.py` unchanged, `--reuse`
only to extend the tag with the runtime probes afterwards.  Eleven objects produced, none
refused by DR.  Predictions were written and committed in `HYPOTHESES.md` **before** the run.

My side: `ocaml/_build/default/bin/pli80c.exe probes/E46Ln.PLI` compared over the WHOLE `.REL`.

| probe | shape | DR | my compiler | predicted | verdict |
|---|---|---|---|---|---|
| E46L1 | `v char(20) varying` on an open output file | code 0x59, DATA 0x1E | **BYTE-EXACT**, 384/384 bytes | refuse (P2a-B); `LHLD` descriptor form | class **right**, route and operand form both **wrong** |
| E46L2 | `c char(20)` fixed | `E46L2.REL` | **BYTE-EXACT**, 384/384 | accept via `?SLCTS` | **right** |
| E46L3 | `k fixed bin(15)` | `E46L3.REL` | **BYTE-EXACT**, 384/384 | accept via `?QICOP` | **right** |
| E46L4 | `z fixed dec(6)`, `y fixed dec(6,3)` | `E46L4.REL` | **BYTE-EXACT**, 512/512 | accept via `?DLDOP`, width p+3, scale s | **right** |
| E46L5 | a literal file PUT then a varying file PUT, sequential | code 0x5E, **DATA 0x23** | **BYTE-EXACT**, 384/384 | refuse (multi-item); pool 9+5+21=0x23 | **route WRONG, pool EXACT** |
| E46L6 | `open ... title(t)` + `put file(outf) list(v)` | code 0x5D, DATA 0x1E | **BYTE-EXACT**, 384/384 | refuse (variable-title route unlicensed) | **WRONG** |
| E46L7 | internal member, varying + fixed | code 154 | refused, `imem_refuse` | DR accepts / I refuse | **right** |
| E46L8 | `dcl f file` with NO open | code 86 | refused by the open guard | DR attaches 0x0652 with no open | **right** |
| E46L9 | `list(k + 1)` | code 90 | refused by the matcher | DR emits the numeric tail, span 12 | **right** |
| E46L10 | `list(a(1))` on a static array | code 97 | refused by the matcher | DR emits the subscript ladder + numeric tail | **right** |
| E46L11 | `q float` | code 89 | refused | `?QFCMS`, `MVI A,0E` | **right** |

Six of the eleven are now byte-exact whole `.REL` files (E46L1-L6); E46L5 and E46L6 compiled
byte-exact where I had predicted a refusal, and five refused for the reason designed.  The
e2e_gate panel after implementation: **1019/1019 byte-exact, 0 fail**, plus the new rows.

## The three misses, stated plainly

**E46L5 — I predicted a refusal for a shape the probe does not contain.**  `HYPOTHESES.md` H5
closes with "Refused by P2a-B: it is precisely the multi-item shape E41X7 refuses", but the `.PLI`
shipped two commits earlier holds **two separate single-item statements** (`list('HELLO');` then
`list(v);`), which is composition, not a multi-item list.  The miss is narrow and specific: a
refusal predicted at the wrong arm, for a shape that was never in the file.  Everything else in H5
landed exactly — "the title pool cell comes first (9 bytes, source order), then `'HELLO'` at 0009,
then the varying variable's 21-byte cell (1 length + 20) at 000E, so `LINK-DEF-DATA-SIZE` is
`0x23` = 9 + 5 + 21" is DR's layout and mine, byte for byte, and the linked image shows
`L5OUT DAT` and `HELLO` adjacent at `19C9`/`19D2`.  So E46L5 became a better specimen than I
planned: it shows the literal route and the variable route coexisting in one DATA image with no
group re-selection between the two statements.

**E46L6 — I predicted a refusal from a guard that does not exist.**  The open guard I wrote in
P1e asks `List.mem fu st.file_out`, and `lower_open` pushes the file name on EVERY lowered OUTPUT
open, BEFORE it dispatches on the title's form (`if List.exists (fun o -> o.io_key = "OUTPUT")
opts then st.file_out <- fu :: st.file_out`, codegen.ml:9053).  So a variable-title output open
authorizes the file PUT, and because [C282]'s variable-title OPEN lowering is itself byte-exact the
whole object comes out DR's.  My hypothesis said "the VARIABLE-title route is not licensed to
produce bytes for this statement form" — true of the CLAIM, false of the CODE: I had written a
guard on the OPEN, not on the title.  [C294] states what the guard actually is.

**E46L1 — right about the class, wrong about the route, and wrong for a reason I had already
disproved.**  P1e's design note, carried into H1, said the varying item would arrive "in
`?Vrop`'s cell-address form (2 words: `LHLD` of the descriptor) and NOT as `LXI H,*D`".  DR emits
`LXI H,*D(<v cell>)` — the cell ADDRESS, one word pair, no descriptor load.  `?Vrop` is the GET
side.  [C291], which I wrote in the previous milestone out of E46J6, already says the PUT side
takes the cell address with `?SLVTS` and not the `LHLD` load a scalar takes.  I quoted the wrong
half of my own claim.

## The measurement this step exists for, from the linked images

`tools/dis80.py --com` on DR's linked `.COM` (every operand resolved, so this is what actually
executes; my objects produce byte-identical `.COM` files — see `RUNTIME-RESULTS.md`).  In each
object the FILE statement and the CONSOLE statement print **the same variable**, and their item
chains are byte-for-byte the same instruction sequence with the same operands:

| class | the chain, emitted twice in one object | file stmt | console stmt |
|---|---|---|---|
| `char(20) varying` | `LXI H,<v> / CALL ?SLVTS / CALL ?PNCOP / CALL ?QIOOP` | E46L1 `012F-013A` | E46L1 `0144-014F` |
| `char(20)` fixed | `LXI H,<v> / MVI A,14 / CALL ?SLCTS / CALL ?PNCOP / CALL ?QIOOP` | E46L2 `012F-013C` | E46L2 `0146-0153` |
| `fixed bin(15)` | `LHLD <k> / MVI A,09 / CALL ?QICOP / CALL ?PNVOP / CALL ?QIOOP` | E46L3 `012F-013C` | E46L3 `0146-0153` |
| `fixed dec(6)`, s=0 | `LXI H,<z> / MVI A,06 / CALL ?DLDOP / MVI A,09 / MVI B,00 / CALL ?QDCOP / CALL ?PNVOP / CALL ?QIOOP` | E46L4 `012F-0143` | E46L4 `014D-0161` |

For E46L1 even the resolved cell address is the same (`LXI H 19CD` twice), and for E46L3 the same
`LHLD 1A69`.  What differs between the two statements is ONLY the prologue: the file route emits
`LXI H,<fcb> / LXI D,0652 / LXI B,<cont> / CALL ?SIOOP` where the console emits
`LXI D,0252 / LXI B,<cont> / CALL ?SYSPR`, and the continuation in `LXI B` is the statement's own
address on both, backpatched by the deferred triple.

That is the whole design decision of P2a, settled by bytes rather than by reasoning: the FILE
route is the console route with a different stream-selection prologue, so one generator serves
both and an item class authorized for the console needs no new lowering to be authorized for a
file — only a new decision, which is what `authorize_file_item` is.
