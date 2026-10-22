# E2E-27 — level-numbered BASED structures, and the correction of E2E-26's P4

Baseline `a413c58` (E2E-26 tip): 688 byte-exact / 0 fail, 121/121 negatives, 0 divergences, exit 0.
ARCH-1 `ocaml/proto/` untouched (md5 `e67a6868b6743e941b5984a53bbe178d`, 13 files).

## 0. E2E-26's P4 conclusion was wrong, and the correction is the whole milestone

E2E-26 concluded "DR refuses based structures in every spelling tried (PB10/PB16/PB17)". It refused
the three probes I threw at it, and I generalised from that to the language. Two historical corpus
programs refute it. Both excerpts below are copied verbatim from the sources, with line numbers; an
earlier draft of this note presented reconstructed "excerpts" that were mine, not the corpus's, and
they were wrong in particulars that mattered (`head` does not exist in REVERSE, which uses `sentence`
and `newnode`; `population dec(9)` and a nested `3 country based(...)` exist in neither program --
NETWORK has zero occurrences of `country`, `population`, `dec(9)` or `char(40)`).

`artefacts/REVERSE.PLI` lines 6-10 (one `declare`, structure head at level 1, members at level 2):

```pli
    declare
        sentence pointer,
        1 wordnode based (sentence),
          2 word character(30) varying,
          2 next pointer;
```

REVERSE lines 30-33 and 44-46 (allocation through a second pointer, link built by assignment, and the
`free` on the structure-name qualifier):

```pli
           allocate wordnode set (newnode);
           newnode->next = sentence;
           sentence      = newnode;
           word          = newword;
...
           p = sentence;
           sentence = next;
           free p->wordnode;
```

`artefacts/NETWORK.PLI` lines 16-29 -- two bare-based records (no pointer named in the `based`), and
`citysize` is a `%replace` macro, value 20 (line 11), so the field is `CHARACTER(20) VARYING`:

```pli
    declare
        1 city_node based,
          2 city_name   character(citysize) varying,
          2 total_distance  fixed,
          2 investigate bit,
          2 city_list   pointer,
          2 route_head  pointer;
    declare
        1 route_node based,
          2 next_city   pointer,
          2 route_distance  fixed,
          2 route_list  pointer;
    declare
        city_head pointer;
```

NETWORK lines 100-105 are the qualified store pattern (`allocate city_node set(p)` then `p->city_name
= city;`, `p->route_head = null;`) -- note `null` used as a bare value, without call parentheses.

DR compiles both, no errors, with a `.REL` (REVERSE regenerated here: `golden/e2e319d`, CODE SIZE
`0110`, DATA AREA `003B`). The `first8080u` copy stored only the `.PRN`, which is why E2E-26 had no
object to inspect and inferred a language limit from three failed spellings. The lesson is the same
one as the E2E-25 forensic audit: **a generalisation from probes I chose is evidence about my
sampling, not about DR.**

What is genuinely not in the dialect is one spelling: `declare nb based(pn) nd` — giving a *name* to
a structure type through a based declaration (PB16, re-run in isolation as ST11). DR gives
`SYNTAX` + `BASED REQ` and no `.REL`. So PB16/PB17 were never evidence about structures.

## 1. The layout, measured

Probe structure heads are level-numbered: `declare <lvl> <name> based(<ptr>), <lvl2> <member>, ...`.

| fact | evidence |
|---|---|
| members are contiguous from offset 0, **no alignment padding** | ST6: `fixed, bit(1), fixed` → offsets 0, 2, 3 and allocation size **5** (`LXI H,0005`). Odd offsets are normal. |
| the structure itself contributes **zero** AUTO STORAGE | ST1: `BLOCK AT LINE 1, AUTO STORAGE 02 BYTES` = the pointer alone. `declare head pointer; declare 1 node based(head), 2 val fixed` allocates 2 bytes, not 4. |
| a CHARACTER member is `len+1` (length byte first, then text) | NETWORK map: `CITY_NAME CHARACTER(30) 0000 (001F)`; REVERSE's record is 33 bytes = 30+1+2. |
| a POINTER member is 2 bytes at its own offset | ST2/ST3/ST8/LN1: `LHLD P / INX H / INX H` (offset 2) then a 16-bit store. |
| allocation size = the record size, summed from the members | ST1 `LXI H,0002` (one fixed), ST3 `0004`, ST5 `0009`, ST6 `0005`, ST7 `0006`, LN1 `LXI H,0004` ×2 |
| a nested head inside a based record does **not** extend the record | ST12: `1 outer based(p), 2 o1 fixed, 1 inner, 2 i2 fixed` — outer allocates 2 bytes and `i2` lands in **automatic** storage at 0002. |

## 2. The routes, measured byte for byte

| form | instruction sequence | source |
|---|---|---|
| `allocate <struct> set(<ptr>)` | `LXI H,<size>` / `CALL ?ALLOP` / `SHLD <ptr>` | ST1, ST3, LN1 |
| `free <ptr>` (scalar based) | `LHLD <ptr>` / `CALL ?FREOP` | E2E-26 PB7/PB19 |
| `free p->s` / `free s` (structure) | `LHLD <p>` / `INX H` × offset / `CALL ?FREOP` | ST8 vs ST1 — **byte-identical**, so one lowering with an address source |
| qualified store, constant | `LHLD <qual>` / `INX H` × offset / `MVI M,lo` [`INX H` / `MVI M,hi`] | ST1, ST8 |
| qualified store, general | `<rhs→HL>` / `PUSH H` / `LHLD <qual>` / `INX H` × offset / `POP D` / `MOV M,E` / `INX H` / `MOV M,D` | ST3, LN1 |
| store `addr(x)` into a pointer member | `<x→HL>` / `LHLD <qual>` / `INX H` × offset / `LXI D,<x>` / `MOV M,E` / `INX H` / `MOV M,D` | ST10 |
| qualified read | `LHLD <qual>` / `INX H` × offset / `MOV E,M` / `INX H` / `MOV D,M` / `XCHG` | ST3, ST10, LN1 |
| unqualified store on a named-pointer record | identical to the qualified form with the declared pointer as the source | ST1, E2E-26 P041 |
| link read `p = q->link` | the qualified-read sequence; DE is the stored address, so `SHLD p` follows the list | ST9, LN1 |

Two things that are *not* in this table and are refused rather than guessed:

* **`link = null()` does not become `MVI M,0` / `MVI M,0`.** DR evaluates the null pointer through
  HL like any other value (`LXI H,0000` / `PUSH H` / … / `POP D` / `MOV M,E` / `INX H` / `MOV M,D`),
  exactly as it does for a scalar `p = null()`. My first draft of the qualified store treated a
  zero-valued HL as a literal and emitted `MVI M` — **my invention, not DR's**, and it would have
  silently changed every null-link initialisation. Fixed: only a literal `Enumber` takes the `MVI`
  path, and ST2's listing is the witness.
* **`<-, <` and `GOTO x->f` fail with `MATCH FAILURE` inside DR**, so the whole arrow-accessor
  family is outside this slice (documented in PERIMETER, not implemented).

## 3. Byte-exact results, and the runtime witness

Six probes byte-exact: **ST1, ST3, ST8, ST9, ST10** and **LN1**.

LN1 is the milestone's target — two linked records. From `artefacts/LN1.PLI` lines 2-18, abridged
only by putting independent statements on shared lines (every statement below appears verbatim):

```pli
declare head pointer, p pointer, q pointer, z fixed;
declare 1 node based(head), 2 val fixed, 2 link pointer;
allocate node set(head);  val = 11;  link = null();
allocate node set(p);     p->val = 22;  p->link = null();
head->link = p;           z = p->val;
put list('first=', head->val, ' linked=', z);
p = head->link;           p->val = 33;
q = head->link;           put list(' after=', q->val, ' z=', z);
free head->node;          free q->node;
```

It is byte-exact, and the four numbers that describe its size are four different quantities, which an
earlier draft of this note juxtaposed as if two of them disagreed ("data 8" vs "DATA AREA 0020"):

| figure | value | what it measures | where it comes from |
|---|---|---|---|
| `.REL` file size | 640 bytes | the object padded to 128-byte sectors | `ls`, and my compiler's own `(%d bytes` field, which prints that padded size |
| code | 256 = `0100` | bytes of CODE segment | DR's `CODE SIZE = 0100` = reldump `LINK-DEF-CODE-SIZE code 0100` = my compiler's `code=256` |
| data area | 32 = `0020` | the whole DATA segment: variables **plus** the literal pool | DR's `DATA AREA = 0020` = reldump `LINK-DEF-DATA-SIZE abs 0020` (same value from both files, because they are byte-identical) |
| automatic storage | 8 | only the declared variables: `head`, `p`, `q`, `z` at 2 bytes each | DR's `BLOCK AT LINE 2, AUTO STORAGE 8 BYTES` = my compiler's `data=8`, which is `rows_of`'s variable-area figure, **not** the data segment |

So 32 = 8 bytes of variables + 24 bytes of pool (the four `put` literals `'first='`, `' linked='`,
`' after='`, `' z='). The same split holds on the other probes: ST1 data area 4 against auto storage 2;
REVERSE data area 59 against the sum of its four blocks' auto storage, 37. My stdout `data=` and DR's
`DATA AREA` are two different measurements, and neither one is the file size.

It was **linked twice and run twice**: `LINK 1.31` on my object
(`golden/e27my/LN1/LN1.REL`) and on DR's (`golden/e27dr/LN1/LN1.REL`), both under cpmsim, both
printing

```
first=        11  linked=        22  after=        33  z=        22
```

Expected values derived before running, from the semantics the probes pinned: A.val=11; B.val set to
22 then 33; `z` read from B **before** the link was followed and never re-read, so it stays 22. That
`z` is 22 while `after` is 33 is the discriminating part — it shows the link read produced B's
address, and that z is an independent copy rather than an alias.

No output leaked between the two runs (LN1 allocates and frees; no diagnostic, no `?FREEO`/`?ALLOP`
trace reached stdout, and both runs terminate with the same single line).

## 4. PB4 / PB20 — the E2E-26 divergences, measured and registered

Both `builds-shape-diverges`, registered in `spec/DIVERGENT.txt` with measurements taken by the
panel's own `_rel_stats`/`_rel_first_diff`/`_rel_diff_count` — the same functions `divergence_check`
uses, so the rows are reproducible rather than transcribed from a different instrument:

| name | mine code/data | DR code/data | ndiff | first byte |
|---|---|---|---|---|
| PB4 | 98 / 9 | 102 / 9 | 255 | 72 |
| PB20 | 93 / 9 | 94 / 9 | 224 | 82 |

Root cause is **not** the pointer read. PB20 is `q = q + q` and PB4 is `q = q * 1`; the DR listings
show `<lhs→DE> / <rhs→HL> / DAD D / POP B / STAX B / PUSH B / POP D / <lhs→DE> / DAD D / POP B /
STAX B` — an accumulator pair-combine into the *address* in DE that E2E-25 never saw because its
route only ever produced `DAD D` with the pair holding a *value*. The pointer cell is reloaded per
operand, so C141 holds. Attributing this to the pointer instead of to the arithmetic operand route
would repeat the E2E-25 attribution error, so it is pinned as a divergence with its shape recorded
and left unfixed: fitting it would touch the shared combine path every arithmetic specimen uses.

**ST2** is a third registered divergence: one extra code byte in DR, data area agreeing exactly
(6/6). Both the `null()` and `addr(z)` stores to the pointer member are reproduced byte for byte, so
the missing byte is near the plain `z = 12` that follows and I have not identified it. One byte from
one probe is not a rule.

## 5. REVERSE: not integrated, and now known as an ordered list of blockers

Mine refuses REVERSE with `BASED structure member word of type CHAR(30) VARYING at record offset 0
is unsampled`. ST13 — a main block that calls one nested procedure, which allocates into a based
record and frees it, plus one statement in main after the procedure definition (`artefacts/ST13.PLI`
lines 4-13) — **DR compiles** and mine refuses earlier, at the main-block/appended-procedure split.
That fixes the order by measurement:

1. nested-procedure statement placement (ST13) -- **CLEARED in E2E-28**: ST13 is byte-exact,
   and so are N1-N6/N8/N10 plus six older append-layout refusals (ST8/ST13/ST14/AB7/AB14/EA1).  The
   rule I had taken for a DR law ("every procedure body is appended AFTER every main-block
   statement") was an induction over goldens that all put their statements first.  See
   spec/notes/e2e28-nested-procedure-placement.md.
2. CHARACTER VARYING **member** store/load (ST5 has the shape with a short field; REVERSE is the
   `word = newword` case at line 33),
3. `GET LIST` stream input (REVERSE's `get list(newword)` at line 27),
4. the cross-pointer set form — already resolved: `allocate wordnode set (newnode)` (line 30) on a
   record declared `based (sentence)` (line 8) is accepted by mine and is what REVERSE does; ST3 and
   LN1 pin that layout byte-exactly.

This list was ordered by *where mine stops*, and item 1 has since been removed by fixing it; item 2
is now REVERSE's live blocker.
REVERSE also uses bare `null` as a value without call parentheses (lines 13, 42), `^=` (line 42),
`return` inside a nested procedure (line 29), `do while('1'b)` (lines 12, 26, 42), `put skip list`
(lines 22, 41), and unqualified member access from a nested procedure whose pointer lives in the
enclosing block (`word = newword`, `sentence = next`). Each of those was probed or not independently;
P1 measures the procedure-placement one, and the rest stay labelled untested until they have their
own probes.

The remaining historical targets are unchanged in character: `texp2/NETW.COM`, `METER2`, `SORT3` are
still not available as DR `.REL` oracles, so NETWORK is a specification, not a second oracle.

## 6. Gate

**694 byte-exact / 0 fail** (was 688), **128/128 negatives** (was 121), **divergence panel 3/3 as
recorded**, exit 0. ARCH-1 md5 verified unchanged after the build.

## 7. Deliberately not done

* BIT / CHARACTER / DECIMAL structure members — refused after the layout binds them correctly, with
  ST6/ST7/ST5 as the extension points.
* Unqualified access in a **bare-based** record (`x = 11` where the record has no named pointer):
  ST4 also shows six DR errors of its own, so there is nothing to reproduce.
* Arrow accessors `<-` / `<` and `GOTO x->f` (DR internal `MATCH FAILURE`).
* NETWORK's remaining shapes, read off the source rather than from memory: `character(citysize)
  varying` members (blocked, as ST5 is), `investigate bit` members (blocked, as ST6 is),
  `repeat(<qualified store>) while(<cond>)` (line 96 — a statement form never probed), chained
  qualification `q->next_city->city_name` (line 124 — no sample), bare `null` as a value (lines 96,
  105), and `%replace` (line 9). NETWORK is a different milestone, not a variant of REVERSE.
* `free` of a structure record through a pointer that was never its `set` target, list traversal
  loops (`do while ...; p = p->link`), and reallocating over a freed pointer: none has a DR sample.
