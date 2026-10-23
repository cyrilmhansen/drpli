# E2E-30 — NETWORK integration, evidence-first

Target: `artefacts/NETWORK.PLI` (the 8-inch disk's Dijkstra shortest-path program).  Its own header
says how big it is -- NETWORK.PLI lines 3-5: "It has 8 internal procedures: SETUP, CONNECT, FIND,
PRINT_ALL, PRINT_PATHS, SHORTEST_DISTANCE, PRINT_ROUTE, and FREE_ALL" -- and the file is 266 lines.
**Full NETWORK byte-exactness was NOT the acceptance bar** — the
bar was: identify the real first blocker, prove an ordered subset of its graph structures, and leave
a matrix that lets a later milestone continue without re-reading the program.

> ### [E2E-31/P0] Provenance correction — citations in this note that did not exist
>
> An audit of every quotation and count in this note against the repository found three
> unsupported statements.  They are corrected below and in place.  The **technical conclusions
> stand**; only the evidence cited for them was wrong.
>
> 1. **"175 lines, 6 procedures" -- a misread of a different table.**  Both numbers come from
>    `spec/notes/grammar-vs-corpus.md` line 115: `| INVESTIGATE | 6 | NETWORK.PLI:175,
>    NETWORK.PLI:179, NETWORK.PLI:185 |`.  There **6 is an identifier-occurrence count** and **175
>    is a source line number** -- neither is a program length or a procedure count.  I read them as
>    one sentence about the program.  True values: 266 lines, 8 internal procedures (NETWORK.PLI
>    lines 3-5, and the `end <name>;` boundaries at 60, 83, 107, 127, 154, 208, 245, 263).
> 2. **The REVERSE quotations are inventions, and the invented text has exactly one source in the
>    repository: this note.**  I wrote that REVERSE.PLI "line 29 comments the algorithm as
>    'reverses the words in a linked list by building it in reverse order'", that "line 74" holds a
>    banner `put skip('reverses a sentence : ')`, and that "lines 79, 84" show commented sample
>    output.  `artefacts/REVERSE.PLI` is **53 lines**, so there is no line 74, 79 or 84 at all; line
>    29 is `return;`; the string "reverses a sentence" as a *banner* appears nowhere, and the
>    linked-list phrase appears nowhere in the repo outside this note.  I did not open the file
>    before quoting it.  What is actually in REVERSE.PLI: line 2 `/* This program reads a sentence
>    and reverses it.     */`, line 24 `sentence = null;`, line 29 `return;`, line 41
>    `put skip list('Actually, ');`.
> 3. **The `world hello` conclusion was right but its evidence was the wrong artifact.**  The
>    sound basis is the **executed DR transcript**, which was already in the repo: in
>    `golden/e29dr_runB/REVERSE.output.txt` input `hello world .` prints `Actually,  world hello .`
>    and input `a b c .` prints `Actually,  c b a .` -- word order reversed, words intact.  That is
>    stronger than any comment and needs no inference.  The earlier "misattribution" finding (that
>    `world hello` is correct behaviour, not an anomaly) is therefore **confirmed**, by execution.
>
> Also corrected in place: "718 instruction lines" counted listing rows beginning with an address
> field (718), which includes 39 source-marker rows; the instruction-line count is **679**.  A
> measurement has to name the quantity it measures.  The BIT-store addresses were quoted as
> `0360/036C/03D1`: 0360 and 03D1 are the *LHLD* at the start of statements 179 and 196, and 03D1
> belongs to a **false** store -- the `MVI` instructions themselves are at 0366, 0437 (true) and
> 0335, 03D8 (false).  The traversal was quoted as "six copies ... 0382 ... 056B": there are **8**
> `repeat` traversals in the source and DR emits **9** pointer-null top tests (0382/056B are not
> among them).  `returns(POINTER)` was cited as line 91 (the declaration is line 90; 91 is where my
> parser reports it), and its call-site evidence was cited as "011C", which is a `MOV M,D` inside
> `connect`, not a call site.
>
> **One false lead was also caught before it became a claim.**  I found that my compiler refuses
> `p->flag = true` and assumed DR accepted it, since NETWORK writes bits that way.  Compiling the
> same shape under DR (`golden/e31p1/E30T7`) gives **`NO DCL ?` and 2 ERROR(S) IN PASS 2** -- DR
> rejects it too, because `true`/`false` are not literals in PL/I-80: NETWORK's own `%replace` at
> lines 9-13 substitutes `'1'b`/`'0'b` (and `citysize` = 20, `infinite` = 32767).  My E30B5 probe
> already carries that `%replace` and is byte-exact.  So there is no bit-literal gap, and the
> refusal I "discovered" was my probe's bug, not the compiler's.

## Gate

| | start (8c522c6) | end (d6cdf45) |
|---|---|---|
| byte-exact specimens | 748 / 0 fail | **756 / 0 fail** |
| negatives refused | 120 / 120 | **119 / 119** (E27S6 promoted [C154]) |
| divergence panel | 8 / 8 | **14 / 14** (6 traversal/graph rows added) |
| exit | 0 | **0** |

`dune build` and `dune build bin/pli80c.exe` clean.  `ocaml/proto/` (ARCH-1) untouched — verified
with `git diff 8c522c6 --stat -- ocaml/proto/` (empty).

## P0 — two E2E-29 misattributions corrected (commit 9b946ba)

**REVERSE's `world hello` was a misattribution, not an anomaly** [conclusion confirmed by
E2E-31/P0; the citations originally given here were fabricated -- see the provenance box above].
The authentic evidence is the **executed DR transcript** `golden/e29dr_runB/REVERSE.output.txt`:
input `hello world .` prints `Actually,  world hello .`, and input `a b c .` prints
`Actually,  c b a .`.  Word order is reversed and the words themselves are intact, which is what
`write_it` does -- it walks the list printing the whole `word` member (`put list(word)`) -- so the
output is correct, not an anomaly.  The program's only description of itself is line 2, `/* This
program reads a sentence and reverses it.     */`.  `artefacts/attic/REVERSE_881.rel` is a
different build and does not bear on this.

**The "DR truncated `'Actually, '` to `'Actual'"` claim was fabricated and is withdrawn.**  Two
independent reasons.  (a) REVERSE has no `character(6)` member at all — its record is
`word CHAR(30) VARYING @0` + `next POINTER @31`, size 33 — so a 9-byte literal cannot truncate.
(b) `'Actually, '` (10 chars) is a **PUT-list** item; in `golden/e2e319d/REVERSE/REVERSE.PRN` it
emits `MVI A,0A` at **00A2** followed by `CALL ?SLCTS` at **00A4** and `CALL ?PNCOP` at **00A7**
-- a print, not a `?SMCVM` store.  (This note previously cited 01D1, which is wrong.)  The earlier
note had read `0A` as a capacity, which was the
half-capacity rule from the E2E-28 varying work.  The real lesson (`A` = destination capacity, never
the value's length) is kept, but re-cited from **E30T1** (byte-exact): `'ABCDEFGH'` (8) into a
`CHAR(6)` member emits `MVI A,06` (dest capacity) / `MVI B,08` (source length) / `CALL ?SMCVM`.  DR's
runtime truncation is inferred from the ABI, **not executed and not claimed**.

## P1 — the NETWORK oracle, established before any implementation

Recompiled the unchanged source on the disk image's PL/I-80 v1.4 (`golden/e30net_dr`): the `.REL` is
**byte-identical** to `golden/first8080u/NETWORK/NETWORK.REL` and the `.PRN` identical too.  So,
exactly as [C194] established for REVERSE, the historical listing is v1.4 output, not an earlier
compiler generation — the E2E-27 hedge is retired for NETWORK as well.

Figures confirmed from the listing and re-measured against the binary: `NO ERROR(S) IN NETWORK` (both
passes), **CODE SIZE 05B0** (201 code records, last at offset 05A1 + 15 = 05B0), **DATA AREA 00EB**
(= the `LINK-DEF-DATA-SIZE` field).  The historical PRN was compiled with `$L$D` only, so it carries
**no disassembly**; a second compile with `$L$D$C$S` (`golden/e30net_c`) is the instruction-level
oracle used throughout — DR's own bytes, not a re-decode [E2E-23].  That listing contains **679
instruction lines** across 1086 PRN lines (718 rows begin with an address field, but 39 of those are
source-marker rows).  DR's own DATA map gives both record layouts exactly:
`city_node` = `.CITY_NAME CHAR(20) VARYING @0000`, `.TOTAL_DISTANCE FIXED @0015`, `.INVESTIGATE
BIT(1) @0017`, `.CITY_LIST POINTER @0018`, `.ROUTE_HEAD POINTER @001A`, size **001C** (21+2+1+2+2,
contiguous -- no padding); `route_node` = `.NEXT_CITY POINTER @0000`, `.ROUTE_DISTANCE FIXED @0002`,
`.ROUTE_LIST POINTER @0004`, size **0006** -- which is exactly the `LXI H,0006` DR emits for
`allocate route_node set (r)` at 00E1.

**First blocker on the unchanged program** (before E2E-30): `BIT(1) member at record offset 23
unsampled`.  Verified by hand against the source, not copied from E2E-27: `investigate` is at offset
0017 = the 21-byte `city_name CHAR(20) VARYING` cell (20 data + 1 length) + 2 for `total_distance`,
contiguous with no padding — the [C185] law, no padding exception.

## P2 — the BIT(1) member ABI [C195]

Reached through the SHARED `bmem_addr`/`member_step` encoder, so bit / fixed / varying / pointer
members cannot drift apart [C179][C189].  True is bit 7 (`0x80`), exactly as the scalar cell
[E2E-11 step 1a].

| shape | DR bytes | NETWORK location |
|---|---|---|
| `p->bit = '1'b` | `LHLD <p>` / [step] / `MVI M,80` | 0366 (line 179), 0437 (line 204) |
| `p->bit = '0'b` | `LHLD <p>` / [step] / `MVI M,00` | 0335 (line 175), 03D8 (line 196) |
| `if p->bit` | `LHLD <p>` / `LXI D,0017` / `DAD D` / `MOV A,M` / `ORA A` / `JP <skip>` | 0382-038B (line 185) |

Byte-exact: **E30B1** (bit@0, store + both test arms), **E30B5** (`bit(1)` inside `DO WHILE`),
**E30B7** (bit@2 beside a fixed member), **E30B3** (scalar control, re-pinned), and **E27S6/ST6**
(offset-2 bit beside a 21-byte varying cell — the layout probe E2E-27 refused, now promoted [C154]).
`if p->f = '1'b` / `^=` (E30B4) and a bit inside a multi-item PUT (E30B6) stay refused: DR's
comparison/PUT bytes for a member bit are in no sample.

## P3 — the pre-test pointer traversal [C196]

`do p = <init> repeat(p-><link>) while(p ^= null); BODY; end;` — **8 copies in the source** (lines
96, 119, 122, 173, 184, 198, 256, 258) and my E30L1-L4 probes.  DR emits **9** `LHLD / MOV A,H /
ORA L / JZ` top tests, attributed by its own listing to NETWORK lines 95 (013A), 118 (01B3), 121
(01EE), 172 (031B), 183 (037A), 197 (03E7), 233 (04D9), 255 (0563) and 257 (0579); **8** are these
traversals and the 9th is line 233's plain `do while(q^=null)`, which DR also tests at the top.  A
`do while(true)` (lines 31, 54, 141, 146, 180, 222) emits **no test at all**.  Measured byte
order:

```
init     <p = from>     LHLD <from> / SHLD P            (an ordinary pointer store)
TEST     p ^= null      LHLD P / MOV A,H / ORA L / JZ <exit>
BODY
REPEAT   <p = p->link>  LHLD P / [step] / MOV E,M / INX H / MOV D,M / XCHG / SHLD P
         JMP back to TEST                                (update after body, re-test gates exit)
```

The init and repeat clauses lower through the existing `lower_assign`; the head test through
`lower_test_skip`.  No new encoder, and the guard must be a plain `POINTER` with no `TO` and no `BY`
or the shape is refused.  This is deliberately the pre-test shape, **not** an algorithmically
equivalent post-test `while`: reordering test/update would break raw REL parity, which is the
acceptance criterion [C137].  Concretely, NETWORK's `find` opens `do p = city_head` with
`LHLD CITY_HEAD A(005A) / SHLD P A(00A8)` at **0134-0137** and the test immediately after at 013A
(this note formerly cited "02C6", which does not exist in the trace).

**E30L1** (the minimal traversal) compiles; mine 69 code bytes vs DR 66, data 12/12, first diff 59.
Deleting one `LXI H,0000` from my stream makes the whole image byte-identical — i.e. the traversal
lowering is exact and the entire difference is DR reusing `HL=0` across `head = null;` and `n = 0;`,
the same register-reuse family as PB4/PB20/E28N7/O1/O2/O4/E29X3.  It is **pinned as a divergence,
not fitted** [C141].  E30L2/L3/L4 are the same family (all DATA AREA exact, mine larger).  **E30L5** is *not* the
post-test form this note claimed: it is the same pre-test traversal with `if n > 3 then p = null;`
in the body, and it **refuses** for that assignment -- `codegen: assignment of this expression to the
POINTER p is unsampled [TBD]`.  That is a real NETWORK dependency (line 239 `q = null;`) and belongs
in the matrix, not in the divergence panel.

## P4 — chained qualification, and the graph witness

`q->next_city->city_name` (NETWORK print_all line 124, E30C1, E30G1) is now **byte-exact** [E30C1,
code 79/79, data 15/15].  DR's route is a two-level dereference: read the inner POINTER member into
HL (`LHLD <base>` / step / `MOV E,M` / `INX H` / `MOV D,M` / `XCHG`), then read the final VARYING
member through that HL (step / `CALL ?SLVTS`).  E30C1 0044–004B and NETWORK 0220–0227 are the same
bytes; both halves reuse existing encoders, so no third addressing mechanism appears [C179].  A chain
into a **non-varying** member (E30C2, arithmetic) and a chain inside a **comparison** (E30C3) stay
refused — in no golden.

**E30G1** is the two-type graph witness (city/road records, BIT flags, chained qualification,
allocation, pre-test traversal).  It compiles and, linked through LINK 1.31 + PLILIB, its console
output is **byte-identical to DR's own E30G1** under the same input (`golden/e30g1d` vs
`golden/e30g1m`).  Its `.REL` is **not** byte-exact (mine 426 code bytes vs DR 419, DATA AREA 21/21)
— the excess is HL reloads DR elides by reusing a live register.  This is the milestone's central
honest result: **the graph mechanism is behaviourally correct and the register-reuse peephole is
not**, attributed to one cause [C140], pinned not fitted [C141].  Note the runtime comparison is NOT
circular here (contrast [C193]): G1's two `.REL` files differ, so the two linked `.COM` images differ,
so matching output is independent evidence of behaviour — unlike byte-identical pairs, where
`cmp`-equality already guarantees identical output.

## NETWORK dependency matrix (state at d6cdf45)

| # | construct | NETWORK lines (verified) | status today | evidence / blocker |
|---|---|---|---|---|
| 1 | `BIT(1)` based member store/test | decl 20; stores 175, 179, 196, 204; test 185 | **DONE** | E30B1/B5/B7, E27S6; DR `MVI M,80` 0366/0437, `MVI M,00` 0335/03D8, test 0382-038B |
| 2 | chained qualification into a VARYING member | 123-124 | **DONE** | E30C1 byte-exact; DR 0220-0227 |
| 3 | pre-test pointer traversal `do p=.. repeat(..) while(p^=null)` | 8 sites: 95-96, 118-119, 121-122, 172-173, 183-184, 197-198, 255-256, 257-258 | **LOWERED, diverges** | E30L1-L4; only excess is HL/DE reuse |
| 4 | `CHAR VARYING`/`POINTER`/`FIXED` members in a 2-type graph | 17-27 | **DONE** | E29V*/E29X*/E30B*; G1 runs identically |
| 5 | allocation / `free p->struct` | alloc 78, 100; free 259, 261 | **DONE** | E2E-26/27; DR `?ALLOP` 00E4/0168, `?FREOP` 0584/059B |
| 6 | `GET LIST` multi-item | 55 (3 items), 143/148 (1 item) | **DONE** | E30H1 byte-exact |
| 7 | **`find(..) returns(POINTER)`** | decl 90; returns 98, 106; call sites 76, 77, 177, 221 | **DONE in E2E-31** [C199] | E31F1/E31F3 byte-exact; callee `LHLD P / RET` 0150/0153, 01A9/01AC |
| 8 | **named-SYSIN `ON ENDFILE(sysin) goto label` / `REVERT`** | 50, 140, 145 / revert 151 | next | E30E2/E30E3 refuse; DR `LXI H,SYSIN / MVI A,05 / CALL ?ONCOP` 0027, 025A, 02A4; `?REVOP` 02F8 |
| 9 | bare `null` assigned to a POINTER | 239 (`q = null;`) | **WITHDRAWN — was never a blocker** | already byte-exact (E31F6); E30L5 refused because that probe said `repeat(p->dist)` instead of `repeat(p->link)` |
| 10 | compound/relational condition operands reached through pointers | 102, 158, 236 | next | E30C3/E30B4 refuse the member-comparison forms |
| 11 | pointer-vs-null as a plain `do while` condition | 233 | **shape visible, unsampled by me** | DR tests at TOP (04D9-04DE, body from 04E1) |
| 12 | label transfer for the ON-unit target | labels `eof:` 59, 153; `eol:` 151 | unsampled | DR emits `JMP 0000` after `?ONCOP` -- a deferred backpatch, not an immediate address |
| 13 | `%replace` preprocessor | 9-13 (`true`->`'1'b`, `false`->`'0'b`, `citysize`=20, `infinite`=32767) | **DONE** (resolved before parse) | E30B5 carries its own `%replace` and is byte-exact |

Two things this table replaces from the first version of the note.  Row 3 previously claimed "7x"
over a set of ranges that did not correspond to the source, and rows 1/8 cited line numbers that were
never checked; every number above was read off `artefacts/NETWORK.PLI` in this pass, and every
address off DR's own `$C$S` listing with its line attribution.

`true`/`false` and `citysize` are NOT PL/I-80 literals or constants -- NETWORK's `%replace` (lines
9-13) substitutes `'1'b`, `'0'b`, 20 and 32767.  Dropping that preprocessor produces `NO DCL ?` and
`2 ERROR(S) IN PASS 2` from DR itself (`golden/e31p1/E30T7`), which is why an earlier draft of this
note wrongly reported "`= true` on a bit member is a gap": the gap was in my probe, not the compiler.

Remaining NETWORK blockers are therefore, in order: **returns(POINTER)**, then **named-SYSIN
ENDFILE/REVERT with label transfer**, then **bare `null` as an assignment value**, then the
compound/relational condition shapes.  The traversal and BIT pieces that E2E-27 blamed for NETWORK's
gap are cleared.


## Recommended E31 scope

1. **`returns(POINTER)`** — the callee form is `LHLD <ptr> / RET` (find: 0150/0153 for line 98,
   01A9/01AC for line 106).  The caller form is fully visible at connect line 77:
   `LHLD DESTINATION_CITY A(009A) / SHLD * A(00A4) / LXI H,* A(00A4) / CALL FIND / SHLD D A(00A0)`
   -- the actual argument is copied into an anonymous parameter slot, reloaded into HL, the procedure
   is called, and the **result is taken from HL** by the following `SHLD`.  (An earlier draft of this
   note cited "the call-site form at 011C"; 011C is a `MOV M,D` inside `connect`, not a call site.)
   Establish the discriminating cases before widening: a local pointer, `null()`, a pointer formal,
   repeated calls (register preservation), and `return` from inside IF/DO.
2. **Named-SYSIN `ON ENDFILE/REVERT`** — `LXI H,SYSIN / MVI A,05 / CALL ?ONCOP` at 0027, 025A, 02A4
   and the same with `?REVOP` at 02F8.  `MVI A,05` is identical in all four sites, so it is a
   condition code rather than a label number; the label arrives as the `JMP 0000` backpatch that
   follows.  Determine whether registration, removal and transfer are three separate lowerings.
3. **Bare `null` as an assignment value** (`q = null;`, NETWORK line 239) — small, and E30L5 is
   already a refusal probe for it.
4. **Register reuse** — 14 divergence rows hang on HL/DE liveness.  DR's own trace already states a
   falsifiable rule to attack: reaching the offset-0x17 member at line 179, DR emits
   `LHLD P / INX D / INX D / DAD D / MVI M,80` (0360-0366) **without reloading DE**, even though
   `LHLD P`, `XRA A`, `MOV M,A` and `INX H` intervened since its `LXI D,0015` at 0358 -- none of
   which writes DE.  So: *reuse a loaded DE unless an emitted instruction writes DE*.  That must be
   tested with probes designed to DISCONFIRM it, and HL has to be asked separately [C141][C185].
5. Label transfer, member-vs-member relational conditions, then re-attempt NETWORK as a whole; the
   matrix above is the reading order.

## Reproducing

```
python3 oracle/batch.py NETWORK --tag e30net_dr            # P1 oracle ($L$D)
python3 oracle/batch.py NETWORK --tag e30net_c --switches '$L$D$C$S'   # code-trace oracle
python3 oracle/batch.py E30B1 E30C1 E30G1 ... --tag e30p1 --switches '$L$D$C$S'
./ocaml/_build/default/bin/pli80c.exe artefacts/E30G1.PLI /tmp/E30G1.REL
mkdir -p golden/e30g1m/E30G1 && cp /tmp/E30G1.REL golden/e30g1m/E30G1/   # + the DR .PRN
python3 oracle/linkrun.py link --tag e30g1m --names E30G1 --out e30g1m --reuse
python3 oracle/linkrun.py run  --tag e30g1m --out e30g1m --names E30G1 --reuse --killon ENDRUN \
        --input ALAMEDA 7 BERKELEY BERKELEY 5 CONCORD ENDRUN ENDRUN
python3 tools/e2e_gate.py --update-inventory && python3 tools/e2e_gate.py
```

> **[E2E-31 addendum]** Row 7 is closed and row 9 was never real.  NETWORK's actual first blocker is
> now row 8, `ON ENDFILE(sysin) GOTO eof` (line 50) -- and rows 3/9 of this table need one more
> correction that only execution revealed: the traversal family recorded here as "only excess is
> HL/DE reuse" contains **two distinct wrong-value defects**, and E31F7C reproduces NETWORK's own loop
> body (`s = s + w->v`) printing `7768' instead of `6'.  See
> `spec/notes/e2e31-returns-pointer-and-value-defects.md` and [C200] before trusting any row of this
> matrix as a *byte*-level statement.
