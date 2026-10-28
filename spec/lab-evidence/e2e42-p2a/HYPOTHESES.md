# E2E-42/P2a — predictions recorded BEFORE the oracle ran

Probe bank `probes/E46L1..E46L11.PLI`, destination tag `golden/e42p2a/`, switches `$L$D$S`
(the spelling every E46 object of this episode was produced with).  Nothing below was written
after seeing a `.PRN`; the file is committed in the same submission as the goldens it predicts,
and `oracle/batch.py` was run once, on the names listed here, with no `--reuse`.

## The two fixed points every prediction is built from

**FP1 — the route prologue, [C280].**  E16D 0023-002C and E17D 0023-002C are byte-identical and
measure a named-file PUT as

    LXI H,<the file's control block>   ; LXI D,0652 ; LXI B,<continuation> ; CALL ?SIOOP

against E17D's own console PUT at 0064-006C, which measures

    LXI D,0252 ; LXI B,<continuation> ; CALL ?SYSPR

i.e. the SAME skeleton with a selected control block in front and a different word and routine,
the 0x0400 bit being the declared-file bit exactly as in `?SIOG` 0x0290 → `?SNFIO` 0x0690.  Both
close with ONE `CALL ?QIOOP`.  The continuation operand is the address of the NEXT statement and
is patched by the usual deferred `LINK-SET-LC/RELOC/SET-LC` triple.

**FP2 — the item chains on the CONSOLE route, byte-exact specimens of this repository.**  Each is
`<operand>; <helper>; <output tail>` with the tail `?PNCOP` for a character item and `?PNVOP` for a
numeric one [C174][C179]:

| operand class | bytes | witness |
|---|---|---|
| CHARACTER(n) VARYING scalar | `LXI H,*D(<cell>)` / `CALL ?SLVTS` / `CALL ?PNCOP` | V101 001C-0024, E46J6 000F-001A |
| CHARACTER(n) FIXED scalar | `LXI H,*D(<cell>)` / `MVI A,<n>` / `CALL ?SLCTS` / `CALL ?PNCOP` | V106 001C-0026 |
| FIXED / FIXED BIN(15) scalar | `LHLD <cell>` / `MVI A,09` / `CALL ?QICOP` / `CALL ?PNVOP` | N301 002E-0038, E46J6 0024-002E |
| FIXED DECIMAL(p,s) variable | `LXI H,*D(<cell>)` / `MVI A,<p>` / `CALL ?DLDOP` / `MVI A,<p+3>` / `MVI B,<s>` / `CALL ?QDCOP` / `CALL ?PNVOP` | R501 0024-0035, R503 0024-0035 |
| FLOAT variable | `LXI H,*D(<cell>)` / `MVI A,0E` / `CALL ?QFCMS` / `CALL ?PNVOP` | R3030 |

So the P2a question is narrow: **does the route change anything between the attach and the
`?QIOOP`?**  Two pieces of evidence already say yes for one class — CREATE's 0165 attaches 0x0652
and then runs `?SLVTS ?PNCOP ?SLVTS`, and KEYFILE's 0095 attaches 0x0652 and runs `?SLVTS ?PNCOP`
(both tabulated in `spec/lab-evidence/e2e41-p0/SIOMODES.txt`) — but neither is a byte-exact object
of this repository, so neither has ever been *claimed*.  Everything below is therefore stated as an
inference from FP1 + FP2 unless marked DIRECT.

## Per-probe predictions

**E46L1 — `put file(outf) list(v)` and `put list(v)`, `dcl v char(20) varying`.**
File statement: FP1's four instructions, then `LXI H,*D(<v>)` / `CALL ?SLVTS` / `CALL ?PNCOP` /
`CALL ?QIOOP`.  Console statement: `LXI D,0252` / `LXI B,<cont>` / `CALL ?SYSPR` / `LXI H,*D(<v>)`
/ `CALL ?SLVTS` / `CALL ?PNCOP` / `CALL ?QIOOP`.  The five bytes from the `LXI H` through
`?PNCOP` are predicted **byte-identical between the two statements inside one object**; only the
attach and the `LXI B` operand differ.  INFERRED from FP1+FP2; the `?SLVTS`-after-a-0x0652-attach
pairing itself is DIRECT (KEYFILE 0095, CREATE 0165).
Falsified if: DR emits `MVI A,<cap>` before `?SLVTS` on the file route (the file route wanting a
declared length the console route does not); or a second control-block load appears between the
attach and the item; or the chain ends with something other than one `?QIOOP`; or the file PUT
emits `?PNCOP` where the console emits it and `?PNVOP` where it does not.

**E46L2 — the same pair with `dcl v char(20)` (FIXED).**
Predicts `LXI H,*D(<v>)` / `MVI A,14` / `?SLCTS` / `?PNCOP` on BOTH routes, the `MVI A` operand
being the DECLARED length 20 = 0x14 — the same number the descriptor of the varying variable in
E46L1 carries in DATA and does not carry in code.  INFERRED (FP1 + FP2 + [C174]).
Falsified if the file route takes the actual length instead of the declared one, or omits `MVI A`.

**E46L3 — the same pair with `dcl k fixed bin(15)`.**
Predicts `LHLD <k>` / `MVI A,09` / `?QICOP` / `?PNVOP` on both routes: `LHLD`, not `LXI H,*D`,
because the item needs the VALUE, and the width byte is the fixed-binary default 9, not 15.
INFERRED (FP1 + FP2).
Falsified if the file route loads the ADDRESS (`LXI H`) instead of the value, or emits `?PNCOP`.

**E46L4 — the same pair with `dcl z fixed dec(6)` (CREATE's `zip`).**
Predicts `LXI H,*D(<z>)` / `MVI A,06` / `?DLDOP` / `MVI A,09` / `MVI B,00` / `?QDCOP` / `?PNVOP`.
The second `MVI A` is precision+3 = 9, NOT the declared precision — that offset is [C130]'s rule,
measured on four console objects.  INFERRED for the file route.
Falsified if a DEC variable on a file takes the literal route (`MVI A,<digits+3>` with no `?DLDOP`)
or if the width comes out 6.

**E46L5 — `dcl v char(20) varying` plus `put file(outf) list('HELLO')` in ONE program.**
This is the DATA-layout probe.  Prediction: the title pool cell comes first (9 bytes, source
order), then `'HELLO'` at 0009, then the varying variable's 21-byte cell (1 length + 20) above the
pool at 000E, so `LINK-DEF-DATA-SIZE` is 0x23 = 9 + 5 + 21 — the same pool-before-autos rule
E17D measures (pool 0000-0010, DEF-DATA-SIZE 0011).  The literal statement must keep E16D/E17D's
bytes exactly (`LXI H,*D(0009)` / `MVI A,05` / `?SLCTS` / `?PNCOP`), which is the E16D/E17D
baseline requirement.  DIRECT for the ordering rule (E17D), INFERRED for its interaction with a
variable item in the same object.
Falsified if adding a variable PUT changes the literal's pool address, or if DR reuses one pool
cell for the title and the literal.

**E46L6 — `open file(outf) stream output title(t)` with `t char(14) varying`, then
`put file(outf) list(v)` with `v char(30) varying`.**
CREATE's OPEN shape and one of its item classes in one object.  Predicts [C288]'s 27-byte
varying-title block (`LXI H,<desc>` / `CALL ?SLVTS` / `MOV B,A` / `PUSH B` / `INX SP` + six words,
w1 = 0x0E50) followed by FP1's attach and FP2's varying chain.  INFERRED by composition of two
rules that have never been measured in the same object.
Falsified if the title's `?SLVTS` changes the state the following attach needs — e.g. if DR
re-emits `SEL-COMMON` per statement (it should, once, because `st.cur_common` changes at the OPEN)
or if the attach's `LXI H` carries a DIFFERENT reloc than the OPEN's.

**E46L7 — `put file(outf) list(line)` and `put file(outf) list(nxt)`, both LEVEL-NUMBERED
members of an internal `rec`, with the OUTPUT open lowered.**
Predicts DR COMPILES it, and that each member's item chain is byte-identical to E46J6's console
chain for the same member (`LXI H,*D(0)` / `?SLVTS` / `?PNCOP` for `line`; `LHLD` / `MVI A,09` /
`?QICOP` / `?PNVOP` for `nxt`), because [C291] measured that the member's operand is the same
three instructions in PUT and in TITLE.  INFERRED; the member operand itself is DIRECT (E46J6,
E46J12), its position after a file attach is not.
**This probe does not license anything.**  P2a authorises the FILE route for an ordinary declared
scalar only, so this object is expected to become a *measured* `my-gap` negative — and E46K10,
which never OPENS its file, stays `unmeasured`: a different whole-program shape, and DR's verdict
on it is still nobody's observation.
Falsified if DR rejects it (then the row is `dr-refuses` and mine refuses for the right reason).

**E46L8 — PU1's exact shape: `dcl f file, x fixed;` with NO open, then `put file(f) list(x)`.**
Predicts DR COMPILES it and attaches 0x0652 anyway, because P086K:4 attaches 0x0652 on a stream
the program never opens (SIOMODES.txt) — the attach is not gated on an OPEN in DR.  INFERRED from
one EDIT-route object, so this probe is what turns it into an observation for the LIST route.
If DR compiles it, PU1 remains a refusal here (no lowered OUTPUT open ⇒ no whole-object witness)
but its reason MOVES from "this item is unmeasured" to "this file was not opened by a route I
lower", and its panel marker has to be re-pinned to the text that actually fires.
Falsified if DR diagnoses it (then PU1's row becomes `dr-refuses`).

**E46L9 — `put file(outf) list(k + 1)`.**
Predicts DR compiles it: the value expression in HL and then `MVI A,09` / `?QICOP` / `?PNVOP` —
the same tail an expression item has on the console.  Refused by P2a: an expression item after a
file attach has no witness, and P2a's perimeter is one VARIABLE.  If DR compiles it the row is
`my-gap`.

**E46L10 — `put file(outf) list(a(1))`, `dcl a(3) fixed`.**
Predicts DR compiles it with the static-subscript ladder (`LHLD` of the element) and the numeric
tail.  Refused by P2a (an array element is not a declared scalar variable).

**E46L11 — `put file(outf) list(q)` and `put list(q)`, `dcl q float`.**
Predicts DR compiles both with `LXI H,*D(<q>)` / `MVI A,0E` / `?QFCMS` / `?PNVOP` — the constant
14, not a precision [C118-era measurement, R3030/R3037/R3045].  Refused by P2a: FLOAT is not in
the authorised set, and the mission's boundary list names it.

## What a pass buys, and what it does not

A pass on L1-L4 licenses exactly four operand classes on one new statement route, and licenses
them as `Pfile(fe,[one item])`.  It does not license: more than one item (E41X7), SKIP on a file
(E41X6), PUT EDIT on a file (E41X8), a member, an array element, an expression, a POINTER or a
FLOAT operand, a READ, or an unopened file (E41X5, PU1, E46K10).  The word `?SLVTS` in
SIOMODES.txt already implied part of this; the reason P1e did not take it is that no object of
this repository pinned the whole statement, and this step's rule is that a claim needs an object,
not a table [the mission's "Do not promote a runtime behaviour to a compiler claim"].

## What would CHANGE my mind

| Observation | What it would falsify |
|---|---|
| L1's varying item chain on the FILE route differs from its console chain in the same object | H1 and the "the Item part is shared" design note I passed down from P1e; the FILE route would need its own item lowering, and sharing `lower_put_items_gen` would be wrong rather than merely convenient. |
| L1's chain is `LHLD`-based (2 words) like `?Vrop` instead of `LXI H,*D` | my P2a-C design note, which assumed the console's `LXI H,*D` shape, and the pool-prescan extension for a varying literal would be unnecessary. |
| L5 ends up with FOUR pool cells and an `MVI A,14` taken from the varying cell | DR really does re-read the length at emit time, and [C278]'s "DR does NOT re-read it" would need restating for this route. |
| L6 attaches/opens from a VARIABLE title and my `st.file_out` guard lets `put file(f)` through | the guard would have to reject VARIABLE-title files as well, or the literal route has to be keyed on the open that actually happened; either way P2a's claim shrinks. |
| L7/L8/L10/L11 are refused BY DR | they become `dr-refuses` negatives and my refusal is agreement; the member row in particular would no longer be a measured gap. |
| L9 is refused by DR, or its `LXI B` span covers something other than `?QICOP + ?PNVOP` | an expression item on this route is not the console's numeric tail, and the generator's expression arm would need its own witness. |

## RUNTIME PROBES E46L12-E46L17 (P2a-D) — written and FIXED BEFORE their oracle run

Their `.REL` bytes are NOT predicted; what is predicted here is the EXECUTED OUTPUT FILE, a
different oracle.  The classes were chosen deliberately: a varying item exercises the
DESCRIPTOR's length byte at runtime (H12), a fixed item the declared width (H13), a numeric the
9-wide EDIT (H14, H15), and only after those does a sequencing probe run (H16).  Written under a
literal title, so by [C279]'s measurement of E16D the CP/M name is the title's FIRST token with
NO extension.

**H12** — `v char(20) varying; v = 'HELLO'; put file(outf) list(v);` → file `L12OUT` holds
exactly the 5 bytes `HELLO`, then CP/M's `0x1A` fill to the 128-byte record.  Nothing else may
appear: no leading blank, no terminator, no 20-byte padding — the length byte, not the
declaration, is what the runtime honours.

**H13** — `c char(20); c = 'ABC';` → file `L13OUT` holds 20 bytes starting `ABC`.  WHAT the
other 17 are (blank, `0x00`, or the cell's prior bytes) is the measurement — no object in this
project has ever produced an under-filled fixed character string in a FILE, so DR's file is the
oracle.  (Written as `c = 42` first, and this compiler refused it for an unrelated reason —
`char store from non-literal [TBD]` — which would have made the probe test two unmeasured routes
at once; rewritten before the oracle ever saw it, so no prediction was fitted to a result.)

**H14** — `k fixed bin(15); k = 42;` → file `L14OUT` holds 7 spaces then `34` (28 octal —
[E2E-8]'s measurement that FIXED BINARY prints in base 8) in the 9-wide field.

**H15** — `z fixed dec(6); z = 123;` → file `L15OUT` holds 6 spaces then `123` in the 9-wide
field.  The point is `s = 0`: R502 pins scale 3, whose edit always carries a point and three
fractions, and nothing here has run a DECIMAL item whose edit has no fraction at all.  (First
written `z = 123.5`, and this compiler refused it for an unrelated reason — `DEC literal 123.5
into scale 0 [TBD]` — so the rounding half of the question is dropped and the edit width is what
remains under test.)

**H16** — three separate single-item PUT statements on ONE open stream → one file with the
items in program order and NO separator between them: `AABCC` (`list('B')` contributes one
byte: the apostrophes are part of a PUT-EDIT picture, not of a string literal's value).  The
alternatives this discriminates: a flush-per-statement terminator (`AA\r\nB\r\nCC`) or a record
that restarts at offset 0 (`CC`).

**H17** — a console PUT, a file PUT, then a console PUT → console shows `CON` then `AGAIN`, and
`L17OUT` holds `FILE`.  If the file route clobbered SYSOUT's FCB the second line would not
appear.
