# E2E-48/P2c — hypotheses and PREREGISTERED predictions (round 3, E48C1..E48C9)

Written and committed **before** the DR oracle is invoked on any E48C probe, under
PROTOCOL.md Part 1 #1 (the committed blob, not a file mtime, proves ordering).
`RESULTS.md` §1 must be a prediction-vs-verdict table over exactly these rows;
every MISS stays in that table (PROTOCOL #2).

    probes written by spec/lab-evidence/e2e48-p2c/mkprobes.py (CRLF, [C193] b)
    git commit  <the commit that adds probes/E48C*.PLI, mkprobes.py and this file>
    git rev-parse HEAD   -- recorded in RESULTS.md as the prediction SHA

## What E2E-48/P2c is

Round 1 (E48A*) and round 2 (E48B*) closed [C309]-[C316]. The one [TBD] there that
blocks a corpus program is inside [C310]: CREATE's SCVCM store at
`golden/first8080u/CREATE/CREATE.REL` 008F is **18 bytes** `21 var / EB / 21 lit /
3E 03 / CD ?SCVCM / D6 01 / 9F / 32 b` while every one of the eighteen E48 sites is
**17 bytes** `21 lit / 11 var / 3E len / CD ?SCVCM / D6 01 / 9F / 32 b`. No probe
varied the discriminator. The remaining candidate — and the only difference between
E48A6's source and CREATE's statement — is that CREATE's `name` is an **internal
level-2 VARYING member** (`%include 'record.dcl'`: `dcl 1 record, 2 name character(30)
varying, ...`) while E48A6's `name` is a flat cell. [C191] already has a load-order
law for TEST position ("the load-able side is emitted first into HL; XCHG moves a
loaded HL into DE for free; XCHG only when the member is the LEFT operand"), and
`golden/e42p1d/E46J21/E46J21.REL` 0006 shows DR addressing an automatic member's
cell *directly* (`LXI H,*D(0002)`, no pointer). This round measures whether that law
carries into the STORE route, and in the same bank measures two layout questions and
one orientation question that the same route depends on.

A defect in MY binder was found while writing this bank (measured at HEAD `1595a10`,
before any oracle call): `dcl_static_dcls` (codegen.ml:12070) treats a level-0 flat
`dcl s char(3) static;` as the enclosing storage-class parent of every LATER
`dcl 1 rec,...` statement, because the inheritance chain pops only entries at
level >= 1. Manual 6.2 ([C242]'s cited text) speaks of *structure levels*; a flat
scalar is not a structure level. Scratch proof: `dcl 1 rec,...; dcl b bit(1) static`
compiles, `dcl b bit(1) static; dcl 1 rec,...` refuses `STATIC on ... MEMBER OF REC@0`.
The census rows for CREATE (advancing) and MPMCALLB confirm the leak from the real
sources. All E48C probes EXCEPT P7 declare the record first (CREATE's own order,
via `%include` before the `declare ... eofile bit(1) static` block), so the bank
measures the discriminator WITHOUT depending on the fix; P7 exists to measure DR's
placement rule for the static-first order directly. Classification of the leak:
**my-gap** (my implementation vs the cited manual text and DR-compiled corpus
programs); P7 is its falsifiable oracle measurement.

## The prior DR evidence (re-read for this file, never from a `.PRN`)

All readings from the `.REL` records via `../e2e42-p2b/chaindump.py` at this HEAD:

* CREATE 008F-009E (member, store): `21 *D(005A) / EB / 21 *D(0035) / 3E 03 / CD
  ?SCVCM / D6 01 / 9F / 32 *D(0000)`. *D(005A) is `name`'s descriptor cell inside
  the automatic `record`; *D(0035) is the pooled `'EOF'`.
* E48A6 0013-0021 (flat, store): `21 *D(0003) / 11 *D(0008) / 3E 03 / CD ?SCVCM /
  D6 01 / 9F / 32 *D(0000)`.
* E48A12 0027-0035 (flat, store, INSIDE `do while(^b)`): the identical 17-byte
  form — statement position did not change the shape for a flat cell.
* E29C4 001C-0028 (BASED member, TEST, `=`): `LHLD *D(0005) / XCHG / LXI H,*D(0000)
  / MVI A,02 / ?SCVCM / C2 <chain>` — XCHG when the member is the LEFT operand.
* E29C9 001C-0027 (BASED member, TEST, literal LEFT): `LHLD *D(0005) / LXI D,*D(0000)
  / MVI B,02 / ?SCCVM / C2 <chain>` — a DIFFERENT helper, length in B, NO XCHG.
* E46J21 0006-0010 (auto internal member, string store IN): `LXI H,*D(0002) /
  LXI D,*D(0000) / MVI A,0E / MVI B,02 / ?SMCVM` — automatic-member cells are
  immediate DATA addresses; pool at DATA 0000, `rec` automatic above it (DATA 0002,
  DEF-DATA-SIZE 0x13 = 19 = 2 pool + 17 auto).
* FLTPOLY2 0011 (`eofile = true` on a STATIC bit): `21 *D(0000) / 36 80` (the [C112]
  high-bit store, corrected reading per [C316]).

## The predictions

Notation as in round 1: `<X>` = a 2-byte inline DATA/COMMON reloc; `<chain>` = the
5-byte skip chain. "size" counts the shape itself.

| # | probe | shape | PREDICTED DR lowering | basis |
|---|---|---|---|---|
| P1 | E48C1 | flat varying store, straight-line (control) | ACCEPT; `21 *S / 11 *D(name) / 3E 03 / CD ?SCVCM / D6 01 / 9F / 32 *D(b)` = **17 bytes**, the E48A6 spelling | E48A6 0013 |
| P2 | E48C2 | `b = (rec.name = 'EOF')`, qualified auto member | ACCEPT; `21 *D(rec) / EB / 21 *S / 3E 03 / CD ?SCVCM / D6 01 / 9F / 32 *D(b)` = **18 bytes**, CREATE's spelling; the member is materialized in HL and parked by XCHG | CREATE 008F + C191 load order + E46J21 member immediacy |
| P3 | E48C3 | the same UNQUALIFIED (CREATE:34 exactly) | ACCEPT; store bytes **identical to P2's** (qualification is a front-end matter; C191's one-thunk rule) | CREATE 008F, C191 |
| P4 | E48C4 | P3's statement inside `do while(^b);` | ACCEPT; loop head `3A *D(b) / B7 / FA <chain>`, member store **18 bytes as P2**, then `n = 4` ladder + `36 80`-family as E48A12 0038-0047; position does NOT change the store form | E48A12 (flat kept 17 in-loop), CREATE 0052/008F |
| P5 | E48C5 | `b = ('EOF' = name)` flat, literal LEFT | ACCEPT; `21 *D(name) / 11 *S / 06 03 / CD ?SCCVM / D6 01 / 9F / 32 *D(b)` = **16 bytes**: C191's helper split (`SCCVM`, length in B) applied to the store; the flag tail is an EXTRAPOLATION (only `?SCVCM` stores carry it in goldens today) — falsifiable | C191, E29C9 head |
| P6 | E48C6 | `b = ('EOF' = rec.name)`, literal left, member right | ACCEPT; `21 *D(rec) / 11 *S / 06 03 / CD ?SCCVM / D6 01 / 9F / 32 *D(b)` = **16 bytes**, NO XCHG (HL is already the right operand) | C191 mirror rule, E46J21 |
| P7 | E48C7 | flat `char(3) static` declared BEFORE an auto record; qualified member store inside | ACCEPT; statics FIRST in DATA in declaration order (`s` at *D(0000) `41 42 20`, `b` at *D(0003)), pool above them, `rec` AUTOMATIC above the pool (the manual 6.2 reading; my chain-leak would put `rec` static — DR is the arbiter); store = P2's 18 bytes | C114/C314 layout laws, manual 6.2 as cited by C242, MPMCALLB compiles |
| P8 | E48C8 | explicit `dcl nm char(14) varying static initial('AB')`, compared flat | ACCEPT (EXPR2/FSCAN/LOAN2 spell exactly this and DR compiled them); cell below the pool per [C114]; **layout of a varying-static cell ([len][chars] vs pointer pair) is [TBD] — the golden decides**; store: predict flat form **17 bytes** `21 *S / 11 *D(nm) / 3E 03 / ?SCVCM / D6 01 / 9F / 32 b` (its address is immediate, like a flat auto's) | corpus AUTHENTIC witnesses, C114 |
| P9 | E48C9 | `if rec.name = 'EOF' then b = '1'b;` auto member in TEST | ACCEPT; head `21 *D(rec) / EB / 21 *S / 3E 03 / CD ?SCVCM / C2 00 00 <chain>` (C191: `=` skips with C2), skip target = statement after the no-else IF (C309's E48B1 rule); then-body `21 *D(b) / 36 80` | E29C4 001C, C191, C309, FLTPOLY2 0011 |

Global predictions:

* **G1** — DR accepts all nine (a `.REL` + `NO ERROR(S)` in both passes). The only
  genuinely un-witnessed axis is the store-route orientation (P5/P6): if DR refuses
  `('EOF' = x)` in a store where it accepts it in a test, that is a `dr-refuses`
  row and C191's law narrows.
* **G2** — DATA layout keeps [C114]/[C115]/[C314]: `[statics][pool][automatics]`,
  static cells absolute and adjacent in declaration order, literals deduplicated by
  content, varying automatic members inside their record's automatic area (E46J21).
  P7 adds: a flat STATIC does not move a later record into the static zone; P8
  fixes the varying-static cell encoding for the first time.
* **G3** — my compiler's state BEFORE the oracle run, measured at HEAD `1595a10`
  with binary md5 `e22f3cf884e9ddca280be5aa59baafca` (see `BASELINE-MINE.txt`):
  P1 compiles; P2/P5/P6 refuse `store into BIT(1) from condition is unsampled`
  (no Mem arm, no SCCVM arm in `bit_cond_mat`); P3/P4 refuse `store of the internal
  CHARACTER member REC.NAME ... is unmeasured`; P9 refuses `comparison of the
  internal CHARACTER member ...`; P7 refuses with the STATIC-LEAK catch-all (the
  my-gap above); P8 refuses `STATIC on CHAR(14) VARYING is unsampled` (the text the
  gate pins for E46F5). After the oracle: each ACCEPTED probe must become
  whole-file byte-identical to its golden, or the row is recorded as a measured
  `my-gap` in `spec/INVENTORY.txt`, never quietly promoted (PROTOCOL #3, #7).

## What a MISS buys

* If P2/P3/P4 carry the **17-byte** form, operand class is NOT the discriminator;
  the surviving candidates are CREATE-specific: the multiple-member record, the
  `%include`d source, or the word `record` as level-1 name — each becomes a named
  E48D axis and CREATE's 18-byte site stays [TBD].
* If P5/P6 show SCVCM (not SCCVM) — i.e. DR re-orders the OPERANDS instead of the
  registers — C191's helper rule is TEST-only and the store route has its own law.
* If P7 places `rec` BELOW the pool, manual 6.2 as I read it is wrong and my
  chain-leak is DR behaviour — MPMCALLB then needs static POINTER-member placement,
  not a binder fix, and this file's classification of the leak flips to the DR law.
* P8's golden is the FIRST oracle witness of a static VARYING cell's bytes; it is
  the evidence E46F5, EXPR2, FSCAN and LOAN2 have been waiting for.
* If P9 refuses, an automatic internal member cannot be compared in TEST position
  even though CREATE's store form compiles — a `dr-refuses` row narrowing the
  condition subset.

## Oracle command (to run AFTER this commit)

    PLI_SRC=probes python3 oracle/batch.py E48C1 E48C2 E48C3 E48C4 E48C5 E48C6 E48C7 E48C8 E48C9 --tag e48p2c --switches '$L$D'

Outputs land in `golden/e48p2c/<N>/`. Round-1/2 goldens in `golden/e48p1/` are not
touched ([PROTOCOL #9]: goldens are evidence; `--tag e48p2c` is a NEW directory).
