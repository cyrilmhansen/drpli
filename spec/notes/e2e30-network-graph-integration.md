# E2E-30 — NETWORK integration, evidence-first

Target: `artefacts/NETWORK.PLI` (the 8-inch disk's Dijkstra shortest-path program, 175 lines, 6
procedures, 2 based record types).  **Full NETWORK byte-exactness was NOT the acceptance bar** — the
bar was: identify the real first blocker, prove an ordered subset of its graph structures, and leave
a matrix that lets a later milestone continue without re-reading the program.

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

**REVERSE's `world hello` was a misattribution, not an anomaly.**  `artefacts/REVERSE.PLI` line 29
comments the algorithm as "reverses the words in a linked list by building it in reverse order"; its
own line 74 banner is `put skip('reverses a sentence : ');`.  Input `HELLO WORLD` → output `world
hello` is therefore the correct result — word order reversed, words themselves unchanged — and the
commented sample output `HELLO` / `WORLD` (lines 79, 84) confirms each word is emitted intact.  It
was never an "unexplained reversal".  `artefacts/attic/REVERSE_881.rel` is a different build and does
not bear on this.

**The "DR truncated `'Actually, '` to `'Actual'"` claim was fabricated and is withdrawn.**  Two
independent reasons.  (a) REVERSE has no `character(6)` member at all — its record is
`word CHAR(30) VARYING @0` + `next POINTER @31`, size 33 — so a 9-byte literal cannot truncate.
(b) `'Actually, '` (10 chars) is a **PUT-list** item; its length byte is `MVI A,0A` feeding `?SLCTS`
at `01D1`, not a `?SMCVM` store.  The earlier note had read `0A` as a capacity, which was the
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
**no disassembly**; a second compile with `$L$D$C$S` (`golden/e30net_c`, 718 instruction lines) is the
instruction-level oracle used throughout — DR's own bytes, not a re-decode [E2E-23].

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
| `p->bit = '1'b` | `LHLD <p>` / [step] / `MVI M,80` | 0360, 036C, 03D1 |
| `p->bit = '0'b` | `LHLD <p>` / [step] / `MVI M,00` | 0382→ (false arm) |
| `if p->bit` | `LHLD <p>` / [step] / `MOV A,M` / `ORA A` / `JP <skip>` | 0382–038C |

Byte-exact: **E30B1** (bit@0, store + both test arms), **E30B5** (`bit(1)` inside `DO WHILE`),
**E30B7** (bit@2 beside a fixed member), **E30B3** (scalar control, re-pinned), and **E27S6/ST6**
(offset-2 bit beside a 21-byte varying cell — the layout probe E2E-27 refused, now promoted [C154]).
`if p->f = '1'b` / `^=` (E30B4) and a bit inside a multi-item PUT (E30B6) stay refused: DR's
comparison/PUT bytes for a member bit are in no sample.

## P3 — the pre-test pointer traversal [C196]

`do p = <init> repeat(p-><link>) while(p ^= null); BODY; end;` — NETWORK's loop six times
(find 013A, print_all 01B3 and 01EE, shortest_distance 031B and 0382, free_all 056B).  Measured byte
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
acceptance criterion [C137].

**E30L1** (the minimal traversal) compiles; mine 69 code bytes vs DR 66, data 12/12, first diff 59.
Deleting one `LXI H,0000` from my stream makes the whole image byte-identical — i.e. the traversal
lowering is exact and the entire difference is DR reusing `HL=0` across `head = null;` and `n = 0;`,
the same register-reuse family as PB4/PB20/E28N7/O1/O2/O4/E29X3.  It is **pinned as a divergence,
not fitted** [C141].  E30L2/L3/L4 are the same family (all DATA AREA exact, mine larger).  **E30L5**
(`do ... while(cond) BODY end;` — test AFTER the body) is refused: that ordering is unsampled.

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

| # | construct | NETWORK lines | status today | evidence / blocker |
|---|---|---|---|---|
| 1 | `BIT(1)` based member store/test | 60, 202, 231, 106, 162 | **DONE** | E30B1/B5/B7, E27S6; NETWORK 0360/036C/0382/03D1 |
| 2 | chained qualification into a VARYING member | 124 | **DONE** | E30C1 byte-exact; NETWORK 0220–0227 |
| 3 | pre-test pointer traversal `do p=.. repeat(..) while(p^=null)` | 7× 94–116, 120–127, 146–169, 176–213, 219–239, 257–263 | **LOWERED, diverges** | E30L1–L4; only excess is HL/DE reuse |
| 4 | `CHAR VARYING`/`POINTER`/`FIXED` members in a 2-type graph | 40–43, 51–54 | **DONE** | E29V*/E29X*/E30B*; G1 runs identically |
| 5 | allocation / `free p->struct` | 80, 153, 261 | **DONE** | E2E-26, E2E-27; G1 exercises both |
| 6 | `GET LIST(a, b, c)` multi-item | 59 | **DONE** | E30H1 byte-exact |
| 7 | **`find(..) returns(POINTER)`** | 91 | **FIRST BLOCKER** | E30F1 refuses; DR: `LHLD P / RET` at 0150 |
| 8 | **named-SYSIN `ON ENDFILE(sysin) goto eof` / `REVERT ENDFILE(sysin)`** | 50, 228 | next | E30E2/E30E3 refuse; DR uses `?ONCOP`/`?REVOP` with `LXI H,SYSIN` + `MVI A,05` (0027/02F8) |
| 9 | `IF NOT (found OR (distance >= ..))` — compound condition with parens + relational operands through pointers | 102, 158 | next | E30C3/E30B4 refuse the member-comparison forms |
| 10 | pointer comparison `q->next_city = null` / `^=` in a nested condition | 112, 208 | **partly DONE** | scalar-side X-arms (E2E-29/P3); member-vs-member unsampled |
| 11 | `GO TO eof/eol` label branching | 50, 223, 228 | unsampled | no golden for `GO TO <label>` in this generator |

Remaining NETWORK blockers are therefore, in order: **returns(POINTER)**, then **named-SYSIN
ENDFILE/REVERT**, then the compound/relational condition shapes, then `GO TO`.  The traversal and BIT
pieces that E2E-27 blamed for NETWORK's gap are cleared.

## Recommended E31 scope

1. **`returns(POINTER)`** — one DR sample exists (`find`, `LHLD P / RET` at 0150) plus the call-site
   form at 011C.  Lowest-risk next gate; do not widen beyond the sampled `RET` shape.
2. **Named-SYSIN `ON ENDFILE/REVERT`** — `?ONCOP`/`?REVOP` with `LXI H,SYSIN` + `MVI A,05`; E30E2/E30E3
   are ready probes.  This is the last structural gate before NETWORK's I/O path.
3. **Register reuse** — the 6 traversal/graph rows and the 8 E2E-23/24/28/29 rows all hang on HL/DE
   liveness across SHLD/LHLD/CALL.  This is the largest open byte-exactness gap: it currently blocks
   NETWORK and every pointer-walking loop from being promoted to exact.  Needs an oracle sample that
   establishes what invalidates reuse; fitting it from a probe I chose would be [C185].
4. `GO TO <label>` and member-vs-member relational conditions.
5. Then re-attempt NETWORK as a whole; the matrix above is the reading order.

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
