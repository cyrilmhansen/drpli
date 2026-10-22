# E2E-27 — level-numbered BASED structures, and the correction of E2E-26's P4

Baseline `a413c58` (E2E-26 tip): 688 byte-exact / 0 fail, 121/121 negatives, 0 divergences, exit 0.
ARCH-1 `ocaml/proto/` untouched (md5 `e67a6868b6743e941b5984a53bbe178d`, 13 files).

## 0. E2E-26's P4 conclusion was wrong, and the correction is the whole milestone

E2E-26 concluded "DR refuses based structures in every spelling tried (PB10/PB16/PB17)". It refused
the three probes I threw at it, and I generalised from that to the language. Two historical corpus
programs refute it directly:

```
REVERSE:   declare head pointer, newnode pointer, sentence pointer;
           declare 1 wordnode based(sentence), 2 word character(30) varying, 2 next pointer;
           allocate wordnode set(newnode);
           newnode->next = null();
           free head->node;

NETWORK:   declare cityptr pointer, countryptr pointer;
           declare 1 city_node based, 2 city_name char(30) varying, 2 population dec(9),
                   3 country based(cityptr);
           allocate city_node set(cityptr);
           cityptr->city_name = 'X';
```

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

LN1 is the milestone's target — two linked records:

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

It is byte-exact (384-byte `.REL`, code 256 / data 8; DR's own listing says CODE SIZE `0100`, DATA
AREA `0020`), and it was **linked twice and run twice**: `LINK 1.31` on my object
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
is unsampled`. ST13 — REVERSE's skeleton minus the varying member — **DR compiles** and mine refuses
earlier, at the main-block/appended-procedure split. That fixes the order by measurement:

1. nested-procedure statement placement (ST13),
2. CHARACTER VARYING **member** store/load (ST5 has the shape with a short field; REVERSE is the
   `word = newword` case),
3. `GET LIST` stream input (REVERSE's `get list(newword)`),
4. the cross-pointer set form — already resolved: `allocate wordnode set(newnode)` on a record
   declared `based(sentence)` is accepted by mine and is exactly what REVERSE does; ST3/LN1 pin it.

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
* NETWORK's `BASED(cityptr) char(40) varying` field-array spelling and its two-level bare-based
  records — the three shapes it needs are exactly the three my note says are blocked.
* `free` of a structure record through a pointer that was never its `set` target, list traversal
  loops (`do while ...; p = p->link`), and reallocating over a freed pointer: none has a DR sample.
