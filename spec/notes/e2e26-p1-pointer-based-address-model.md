# E2E-26 P1 -- DR's POINTER / BASED / ALLOCATE / FREE address model

All evidence below is DR v1.4 output produced or re-produced in this milestone (batches
`golden/e2e310d` [11 historical probes re-run], `e2e311d` [11 new PB*/PD1], `e2e312d` [PD2/PD3],
`e2e313d` [PD4/PD5], `e2e314d` [PB11-PB17]), read from the `.PRN` storage maps and from `.REL`
disassembly with relocations resolved.  Nothing here is inferred from PL/I standards or from the
pointer-FORMAL rules of C130/C131, although the two agree where they overlap (that agreement is
stated, not assumed).

## Verdicts: what DR accepts and what it refuses

Accepted, NO ERROR(S) IN PASS 1 and PASS 2, .REL emitted (25 probes):

    P019A  P041  P063B  P067B  P067C  P071K  P086M          (historical, re-run here)
    PB1 PB2 PB3 PB4 PB6 PB7 PB8 PB9  PD1 PD2 PD3 PD4 PD5    (new)
    PB18 PB19 PB20 PB21 PB22                                 (new, e2e315d)

Refused (diagnostic, NO .REL):

    P063A  type/defaulting probe, unrelated to storage
    P067A  `free p;'            BASED REQ in pass 2  [pointer operand]
    P080K  `allocate p;'        no SET clause
    P082K  `fixed based(p) static' + allocate set(p)
    PB5    `fixed bin(31) based(p)' + allocate w set(p)     1 ERROR pass 1
    PB11   `fixed bin(16) ...'  same shape                 1 ERROR pass 1
    PB12   `fixed bin(24) ...'  same shape                 1 ERROR pass 1
    PB10   based STRUCTURE + allocate                       BASED REQ + 4 pass-2 errors
    PB16   `declare nb based(pn) nd, pn pointer;'           structure type-name in a BASED dcl
    PB17   `allocate nd set(pn);'                           allocating a structure by name

The bin(16)/bin(24)/bin(31) rejections are **not about size**: `fixed dec(5)` allocates 3 bytes and
`char(5)` allocates 5, both accepted [PB13, PB6].  They are specific to explicit BINARY precision.
Recorded as measured boundaries, not as a rule about allocation.

## Storage model (from DR's own symbol maps)

    P063B  AUTO STORAGE 4   p 0000 POINTER AUTOMATIC | q 0000 BASED(P) | z 0002 AUTOMATIC
    PB1    AUTO STORAGE 6   a 0000 AUTOMATIC | p 0002 POINTER AUTOMATIC | q 0000 BASED(P) | b 0004
    PB2    AUTO STORAGE 6   p 0000 POINTER | r 0002 POINTER | q 0000 BASED(P) | s 0000 BASED(R) | z
    P086M  AUTO STORAGE 6   p 0000 POINTER | q 0002 POINTER | z 0004
    PB9    main: p 0000 POINTER | x 0000 BASED(P) | z 0002 ;  callee: c 0000 .* POINTER PARAMETER

Three consequences, each of which changes my binder rather than merely decorating it:

1. **A POINTER is a 2-byte automatic cell holding a 16-bit data address.**  That retires the
   `[HYPOTHESIS] PROBE 57` note on `Bind.bytes_of RTptr` -- 2 bytes is now measured, on P063B,
   P086M, PB1, PB2, PB3, PB4, PB9, PD1.
2. **A BASED declaration consumes NO storage.**  Its map line prints at its POINTER's offset and the
   block's AUTO STORAGE excludes it (PB4: 4 = p + z; P067C: 2 = p alone).  A based name is therefore
   a *view*, not a variable with a cell -- if the binder gave it a cell it would silently shift every
   later automatic and the DATA area would disagree with DR.  (PB1 is the probe that makes this
   unmissable: the pointer sits BETWEEN two ordinary automatics, so a spurious cell for `q` would
   move `b`.)
3. **POINTER cells follow declaration order, interleaved with ordinary automatics** -- PB1 puts p at
   0002 between a@0000 and b@0004.  The "pointer cells first" rule in bind.ml belongs to FORMAL
   argument descriptors only [C130/C175]; the two must not be conflated.

PB9 also pins the formal/source distinction the milestone brief warns about: passing a source pointer
as an actual produces `.* POINTER PARAMETER` at offset 0 of the callee -- an anonymous descriptor word
-- while the callee's `declare argp pointer` is what lets `q based(argp) fixed` be used there.  Same
2-byte contents, different storage authority.  PB9 is accepted by DR, so a source pointer CAN be
passed; the callee-side mechanism is P2/P3 work and is not claimed here.

## Instruction forms (from .REL disassembly, relocations resolved)

Effective address lives in HL; DR **reloads the pointer cell for every access** and never parks it:

    p = addr(z)   LXI H,<DATA+off z> / SHLD <DATA+off p>            [P063B 000C, P041 000C, PB3]
    p = null()    LXI H,0000 / SHLD <p>                             [P086M 0006]
    q = p  (copy) LHLD <p> / SHLD <q>                               [P086M 000C]
    read  through LHLD <p> / MOV E,M / INX H / MOV D,M / XCHG        [P071K 0014, P063B 0026]
    write const   LHLD <p> / MVI M,lo / INX H / MVI M,hi             [P071K 000C, P067C 000F, P041 0012]
    read+arith    <that read> then the usual bias ladder            [P071K: z = q + 1 -> INX H / SHLD z]
    p = null test LHLD <p> / MOV A,H / ORA L / JNZ <target>          [P019A 000C]

`p->q` and `q` compile identically when `q based(p)`: P041 does `p->q = 100` and `q = 5` with the same
`LHLD p / MVI M,lo / INX H / MVI M,hi` at 0012 and 0041 -- the `->` qualification is a second spelling
of the same indirect reference, not a different mechanism.  (This is a measured equivalence, and it is
only measured for a based name whose pointer is the one being qualified.)

Little-endian throughout: low byte at the pointed-to address, high byte at +1.  These are the same two
deref/store shapes already recorded for pointer FORMALS (C131 rows in spec/PERIMETER.md); for a
general (non-constant) right-hand side the formal-side measurement gives
`<rhs> / PUSH H / LHLD X / POP D / MOV M,E / INX H / MOV M,D`, parking the value in DE because the
pointer load is an `LHLD`, which does not disturb DE.

**The general based store is now measured too, and it is byte-for-byte that same shape** [PB18
`q = z;`, batch e2e315d]: `LHLD <z> / PUSH H / LHLD <p> / POP D / MOV M,E / INX H / MOV M,D`.  PB19
adds the composition that makes P2 tractable: `q = z + 1` is `LHLD <z> / INX H` then that same store,
and `z = q * 2` is the read form (`LHLD <p> / MOV E,M / INX H / MOV D,M / XCHG`) feeding `DAD H` and
`SHLD <z>` -- i.e. a BASED read delivers a value in HL and otherwise composes with the existing
arithmetic machinery unchanged.  PB20 (`q = q + q`, two reads of one pointer), PB21 (`q = 1; q = q + 41`,
constant then self-update) and PB22 (store after an intervening change to the source) are all accepted;
their bytes are compared in P2 rather than read here.

So the pointer-FORMAL instruction generators and the BASED ones coincide where both are measured --
which is a property of the emitted code, NOT permission to conflate the storage models: a formal
pointer is the anonymous `.* POINTER PARAMETER` descriptor word at callee offset 0 [PB9], while a
source POINTER is an automatic cell in declaration order [PB1].  Those are different layout authorities
that happen to be dereferenced the same way.

## ALLOCATE / FREE ABI (P3's basis)

    allocate x set(p)   LXI H,<size> / CALL ?ALLOP / SHLD <p>       [P067C, PB6, PB7 x2, PB8, PB13-15]
    free x              LHLD <p> / CALL ?FREOP                      [same set]

?ALLOP receives the requested size in HL and returns the allocated address in HL -- that is what the
following `SHLD <p>` stores.  FREE receives the address in HL, loaded from the pointer cell, so
`free x;` (based name) and a hypothetical `free p;` would compile to the same two instructions; DR
still refuses the pointer operand [P067A, BASED REQ], which is a front-end requirement and NOT a
code-generation difference.  Sizes measured:

    fixed (=bin(15))      2  [P067C, PB7 both allocations, PB8]
    fixed dec(5)          3  [PB13]      <- equals the decimal cell DR reserves for dec(5)
    bit(8)                1  [PB14]
    char(3)               3  [PB15]      <- equals the character count, no length word
    char(5)               5  [PB6]

Two allocations in one program produce two independent call sites, each with its own `SHLD` into its
own pointer cell [PB7: ?ALLOP@000A->p, ?ALLOP@0013->r], and an ALLOCATE inside a DO loop is a single
call site executed per iteration [PB8: preceded by `JP` from the loop test].  Heap-state bookkeeping
(?ALLOP internals) is not observable from the .REL and is deliberately not claimed.

## Explicitly NOT established here

* **The true trigger of PERIMETER row 26's POINTER-without-BASED anomaly.**  Four probes built to
  reproduce it -- PD2 (`declare p pointer;`, never used), PD3 (unused pointer beside another variable),
  PD4 (uppercase `DECLARE X POINTER;`, the verbatim manual shape), PD5 (lowercase, name `x`) -- ALL
  compile NO ERROR(S) in both passes and emit .REL [golden/e2e312d, e2e313d].  The row's classification
  is not reproducible as written, so the original observation had some narrower cause I have not found.
  Consequently I implement no refusal for it and claim no unconditional support either; the PERIMETER
  row now carries this result.  (Instruction from the milestone brief: a compiler anomaly must not be
  turned into a general language rule -- that cuts both ways, including against a stale row.)

* **[E2E-27] WITHDRAWN** -- Structure-based storage and `allocate <structure> set(p)`. This line
  said DR refuses all three spellings tried (PB10/PB16/PB17) and that P4 was blocked on DR itself.
  It is wrong, and the correct conclusion is claim C185. DR accepts level-numbered based structures:
  `REVERSE.PLI` and `NETWORK.PLI` -- both in artefacts/ throughout every milestone -- declare
  `1 wordnode based (sentence), 2 word character(30) varying, 2 next pointer' and
  `1 city_node based, ...' and compile with no errors and a .REL (REVERSE's object regenerated:
  golden/e2e319d). PB10/PB16/PB17 failed on declaration SPELLING; ST11 isolates PB16's
  `declare nb based(pn) nd' and DR still rejects THAT, so one spelling is genuinely absent while
  structures are present. E2E-27 implements based structures with FIXED and POINTER members
  byte-exactly, and LN1 -- two linked records, link followed, second record modified through it --
  is byte-exact AND runs identically when linked from my .REL and from DR's.
  The mistake's shape is what is worth keeping: three refusals from three spellings of MY OWN
  invention, generalised into a language limit, while two working programs sat in a corpus I had
  been citing for three milestones. A negative about a language feature needs the feature's own
  documentation or a working program as its control, not only probes I picked.
* Pointer arithmetic (`p = p + 2`, `+=`): unprobed, PERIMETER row 58 still open.
* Freeing twice, dereferencing a null or freed pointer: not probed -- unsafe to run and DR's behaviour
  is not demonstrable in isolation.
* Whether `addr()` of a POINTER-typed variable, of an array element, or of a based name is legal.
* Float-based storage (`fixed`/`dec`/`bit`/`char` measured only) and `bin(16/24/31)`.

## Starting point of my compiler

Mine refuses ALL 20 accepted probes at one guard, `codegen.ml`'s declaration-layout switch:
`codegen: declared variable kind not in supported subset [TBD]: POINTER` -- the binder sizes RTptr at
2 (`bytes_of`) but codegen has no value kind for it, and the `based(...)` attribute is not read by the
binder at all, so a based name would currently be laid out as an ordinary cell.  Implementation is
therefore: teach the binder that BASED contributes zero storage and carries its pointer's identity,
give codegen a pointer cell kind and a based view kind, and emit the six instruction families above.


---

## P2/P3 -- what was implemented, and what was run

Built on the address model above, without touching ARCH-1 (`ocaml/proto/' is untouched [C160]).

**bind.ml**: `RTbased of string * rt`. A BASED declaration resolves to it and `bytes_of` reports
**0**, which is the whole of DR's behaviour: PB1 shows `q` printed at `p`'s offset and adds nothing
to AUTO STORAGE, so a based name is a view, not storage.

**codegen.ml**: `vkind` gained `Vptr` (2-byte automatic cell, declaration order, not hoisted) and
`Vbased of string`. The routes are exactly DR's measured forms:

| source | DR's bytes | samples |
|---|---|---|
| read `q` | `LHLD <p> / MOV E,M / INX H / MOV D,M / XCHG` | P063B, P071K, PB19 |
| store const | `LHLD <p> / MVI M,lo / INX H / MVI M,hi` | P071K, P041, P067C |
| store general | `<rhs> / PUSH H / LHLD <p> / POP D / MOV M,E / INX H / MOV M,D` | PB18, PB19 |
| `p->q = v` | identical to `q = v` | P041 |
| `addr(z)` | `LXI H,<DATA+off z>` | P063B, PB18-PB22 |
| `null()` | `LXI H,0000` | P086M |
| `allocate x set(p)` | `LXI H,<size> / CALL ?ALLOP / SHLD <p>` | PB6, PB7 x2, PB8, PB13-PB15 |
| `free x` | `LHLD <p> / CALL ?FREOP` | PD9, PB7 |

The based store does not re-implement anything: it calls the existing `lower_store_ptr` with a new
optional `pa_of` so the cell to reload is the pointer's, while the name tested by the `x = x +- lit`
shape stays the based name (PB21 does `q = q + 41`). One encoder for two spellings [C179].
The pointer cell is reloaded for every store and never parked -- PB3 (pointer re-pointed between
reads) and PB22 (store after an intervening write to the source) both show DR re-reading the cell,
so C141 is unchanged by this slice.

**Gate: 688/688 byte-exact, 121/121 negatives, 0 divergences, exit 0** (was 667/117). 21 probes
registered as specimens, 4 (PB6/PB13/PB14/PB15: based char/decimal/bit) as my-gap negatives.

**Runtime witnesses** -- linked by LINK 1.31 from my own `.REL` and executed, so the evidence comes
from the same artifact the byte check uses:

    PB7   x=       100  y=       200 done      end
    PB1   a=        11  q=        22  b=        22      end
    PB3   first=        11 second=        22      end

PB1 is the one that tests the model rather than the code: it stores 11 directly into `a`, points `p`
at `a`, prints `q` (reads through the pointer), re-points `p` at `b`, stores 22 through it, and reads
`a` again. Getting 22 twice means the re-read happened after the re-pointing, which is what the
address model predicts and what a parked-pointer implementation would get wrong.
They are not in OUTPUT_CHECK: DR kept no run transcript for these batches [E2E-25 lesson].

**Not claimed, recorded instead.** PB4 (`q = q * 1`) and PB20 (`q = q + q`) build and differ -- in
both, an arithmetic operand is itself read through the pointer, and DR's register parking for that
shape is uncharacterized. They are left out of DIVERGENT.txt rather than given size columns filled
with unverified numbers; the first differing byte is at offset 72 (PB4) and 82 (PB20), sizes equal.

**Four defects found on the way**, each of which would have been silent or fatal:

1. `Ebuilt` keys are stored UPPERCASE. My first `addr`/`null` arms matched `"addr"`/`"null"`, so
   `addr(z)` fell through to the generic path and every pointer-holding probe refused with a message
   about pointer arithmetic -- a refusal naming the wrong cause is worse than no refusal.
2. Two new `(match ...)` blocks were left unclosed and one refusal message carried a stray `")`. The
   compiler reported the resulting syntax error on a line ~40 lines away from either cause.
3. `ALLOCATE`/`FREE` initially tripped my own DISCARD invariant: the statement counter counts every
   non-decl/non-null statement, so a new statement arm that does not increment `lowered` aborts the
   build. An internal check is part of the route, not an obstacle beside it.
4. `p->q = 100` raised a bare `Match_failure`. The gap was pre-existing but unreachable: as long as
   `POINTER` refused at the layout switch, no `Eqptr` lhs could ever reach `lower_assign`. Widening
   a declaration makes the holes below it live, so each widening needs its lhs/rhs shapes enumerated
   in the same pass (ME1/ME2/ME3 isolate this: the based store and the based read worked, only the
   `->` spelling crashed).

**Three measurement errors of my own that produced false readings** -- recorded because the
conclusions looked empirical: `cmp` against a golden path that did not exist reported DIFFERS for
four probes that were in fact byte-exact (PB18/PB19/PB21/PB22); `grep -c ALLOP` counts DR's symbol
table row, so "ALLOP=1" did not mean a call was emitted; and a `CALL +4-hex-digits` regex matched
nothing because DR prints `CALL ?ALLOP` with no address column, which is what made FREE look
unimplemented for a while. A rule worth keeping: check that the instrument can see the thing at all
before believing a negative from it.
