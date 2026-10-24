# E2E-38 — correcting the measurements: C236, PB4, and the STATIC family

Baseline `f928568` (E2E-37).  The instruction was to audit one claim (C236) that smelled like a
misread little-endian store, discriminate PB4 with existing syntax, fix the STATIC inheritance
C242 identified, repair stale coverage documentation, and run a small differential campaign.  Four
of the five prior conclusions in this tree turned out to be wrong, and in three cases the thing that
was wrong was the instrument, not the subject.

## P0 — C236 was a misattribution, and there is no DR byte-order defect at all

`nx = addr(z)` in ST2 stores a pointer.  [C236] said DR writes "the HIGH half at the LOWER address"
and that I reproduce that defect deliberately.  It does not:

```
$ python3 tools/dis80.py golden/e2e323d/ST2/ST2.REL
002F  LXI  D None/None      ; 11   .   .     <- DE := address of z
0032  MOV  M,E              ; 73             <- LOW byte at the current address
0033  INX  H                ; 23
0034  MOV  M,D              ; 72             <- HIGH byte at the next address  = little-endian
```

`pli80c artefacts/ST2.PLI` is `cmp`-identical to that golden, and `git show cbb1608~1:ocaml/lib/codegen.ml`
(4170-4173) emits `0x72, 0x23, 0x73` — `MOV M,D / INX H / MOV M,E` — which *is* the swap.  The
high-at-low order [C236] attributed to DR was my own pre-E2E-36 code.  `MOV M,E` was read as "high
byte first"; `D` is the high register and `E` the low one, so `MOV M,E` is the opposite.  The "byte
DR adds that I cannot find" in the E2E-36 note was the missing `INX H`, i.e. half of a correct
two-byte store.

A second route agrees: `tools/dis80.py golden/first8080u/NETWORK/NETWORK.REL` shows
`MOV M,E / INX H / MOV M,D` at 0xf8-0xfa on its `.link = addr(t+1)` walk, also byte-exact against me.

And the "surviving" DR defect I cited in the same breath — a structure length word stored as
`73 08 89` — does not exist either.  That pattern came from searching **raw `.REL` bytes**, and
PL/I-80 `.REL` is a bit-packed record stream: the disassembler's offsets are stream offsets, not
file offsets, and a three-byte grep over the packed file finds and loses matches at will.  [C127]
already documents DR's two pointer-store shapes and both are little-endian — forward
(`MOV M,E / INX H / MOV M,D`) and backward from `ptr+1` (`XCHG / MOV M,D / DCX H / MOV M,E`, which
puts the high byte at the *higher* address and looks swapped only if the `DCX H` is missed).  There
is no known DR byte-order defect.  Recorded as [C244] with [C236] corrected in place, [C249] for the
instrument, and the `STOR.POINTER_MEMBER_ORDER` row moved from `ACCEPTS_DEFECT/M` to `ACCEPTS/S`.

The read-back that would settle this with a *value* rather than a disassembly is still open: DR
rejects `y = *w` (E37A1: `expected expression` — PL/I-80 has no `*p` operator, a BASED name
dereferences implicitly), and the accepted form `if nx = addr(z)` (E37A2, CODE SIZE 006B) is one my
condition subset refuses [C247].

## P1 — PB4 is a proven wrong-value defect, discriminated with PB4's own syntax

No new construct was needed: PB4 is `if q > 3` with `q based(p) fixed`, so the constant changed and
the branch direction became observable.  E37B1/B2/B3 are that program with z = 1, 3, 4; DR accepted
all three (256-byte .REL, CODE SIZE 005A each).  At the comparison, DR and I differ by four code
bytes and the disassembly says exactly what they are:

```
DR    0016  INX H / MOV D,M / XCHG / LXI B FFFC / DAD B / MOV A,H / ORA A / JM <tgt>
mine  0012                       LHLD <p> / LXI B FFFC / DAD B / MOV A,H / ORA A / JM <tgt>
```

DR dereferences the base to get the datum, biases it by -(k+1) and tests the sign; I bias HL, which
holds the **pointer**, so my branch follows the address.  With z=40 both readings take the branch,
which is why PB4 has sat on the runtime panel printing `q= 44|end` for eleven episodes while being
wrong: the gate itself flags that row as `NON-CIRCULAR: images differ, this run is evidence about
mine`, and the evidence was a coincidence.  With z=1 DR prints `q= 1` and mine must print `q= 5`.

Three new DIVERGENT rows pin it (E37B1/B2/B3, all +4 code, DATA agreeing 6/6, first differing file
byte 0x48).  The fix is *not* attempted here: the same comparison lowering carries NETWORK and
E32C8, and four other comparison shapes are still refused outright, so the relation × operand-class ×
operand-position matrix has to be probed as one unit first [C246][C247].

## P2 — the STATIC family: C242 was right about the fact and I nearly replaced it with a fiction

`dcl_static` reads only a declaration's own attribute list, so a member never inherits `STATIC`, and
every `1 t static, 2 x ... initial(n)` shape was refused with a message claiming *DR* rejects it.
Manual 6.2 says the member inherits the enclosing level's storage class unless it names one; DR
accepts the shape (DIOCALLS, ENTER, FSCAN, LOAN2, REPORT, MPMCALLB all carry .REL with it, and nine
new goldens were accepted with no diagnostic).

What went wrong on the way: my first bisect harness was

```sh
msg=$($B $f 2>&1 | tail -1); [ $? -eq 0 ] && echo OK || echo "$msg"
```

`$?` after a pipeline is `tail`'s status, so every case reported OK and six "accepted" cases were
failures.  I built a mechanism out of that — newline-sensitivity, inline comments, `DEFAULT` as a
keyword — and wrote it into `CLAIMS.md` as C245.  Re-run with the artefact as the authority (`[ -f
out.rel ]`), the layout story evaporates: the refusal is layout-independent.  C245 is withdrawn in
place rather than deleted; the only genuine layout-adjacent fact is that a declaration inside a
nested procedure's block is not checked at all, because the statics pass runs per-block and that
block's path never reaches it.

The fix that landed (`dcl_static_dcls`, [C250]): walk the flat declaration list in source order, keep
a stack of (level, effective class) for enclosing levels, pop everything at a level ≥ mine (so a
level-1 head and a bare scalar inherit nothing), take the member's own STATIC/AUTOMATIC when present
and the enclosing level's otherwise.  A real DEFAULT clause is deliberately not modelled — ENTER's
`default` is a structure *name* and no accepted specimen uses the clause.

What it changed, measured:

| before | after |
|---|---|
| DIOCALLS: `INITIAL without STATIC is rejected by DR` | `BASED(DBUFFV) of type CHAR(127) VARYING is not implemented` |
| ENTER: `INITIAL without STATIC is rejected by DR` | `statement kind not in supported subset (line 37)` |
| E37S3 (member INITIAL, no static anywhere): refused, message said DR rejects | refused, and **DR really does**: pass 2 `NOT STATIC`, 1 error, no .REL |

So the false statement is gone from the nine corpus episodes that quoted it, the faithful case is
now backed by DR's own diagnostic twice over (E37S3 and the generated E38S3), and DIOCALLS/ENTER are
**not** unlocked — which retires the E2E-37 P6 ranking's "rank 1: 0 round trips to unlock".

## P4 — the differential campaign, and what the templates measured

`tools/probe_gen.py`: 16 templates in two families, emitted CRLF+^Z, **validated against my own
compiler before any oracle time**, then DR, then classified.  The first batch I launched reported
`0 ok / 17` while still leaving .PRN files behind: my sources were LF-terminated without `^Z`, so PL/I-80
said `UNEXPECTED EOF` — 473 of 490 historical artefacts carry the marker.  A print file is not a
compile.

Yield (e37e hand-written, e38a generated — the generated campaign reproduces every class):

| outcome | compare family | static family |
|---|---|---|
| byte-exact | E38C1 (`if n > 3`), E38C3 (formal) | — |
| differs (wrong value, PB4 shape) | E38C4/C5/C6 = z 1/3/4 | — |
| DR accepts, I refuse | literal-left ×2, `>=`, `<=`, pointer-equality | unqualified member scope ×5 |
| both refuse (faithful) | — | member INITIAL with no static anywhere |

First-pass yield 2/16 exact.  The failures are the product: five comparison shapes DR accepts and my
`E2E-3b` subset refuses [C247], and the STATIC family's next wall is that my binder does not put
structure members in scope unqualified [C248] — which the manual's own 6.2 example (`C = B + A`)
shows DR does.

## P3 — documentation repairs

* `COVERAGE.tsv`: 77 → 83 rows, 0 errors.  `STOR.POINTER_MEMBER_ORDER` reclassified; `COND.BASED_LITERAL`
  and `REL.BASED_LITERAL` now say wrong-value with the disassembly; six new rows for the campaign's
  findings; `DECL.BASED_STATIC`/`DECL.STATIC_INHERIT` reworded to the surviving truth.
* `COVERAGE-SCHEMA.md`: the 15 columns tabulated explicitly, the 16 declared categories with their
  real counts (15 populated, `FILE` empty), a rule against hard-coding counts, and the claim-file's
  three-format structure described instead of a number.  The tally I first wrote was stale before I
  finished the paragraph, which is now recorded in the file as the reason for the rule.
* `coverage-builtin-sweep.tsv`: `mine_verdict` conflated stages; added `stage_reached` on a six-step
  ladder (parse → name → binding/signature → lowering → parity → runtime) and `evidence_classes`.
  52 documented built-ins: 30 die at lowering, 22 at binding, **0 have a DR golden or a runtime
  witness**.
* `PERIMETER.md`: the [C225] NETWORK "linkage record" diagnosis corrected to [C237]'s instruction
  difference; the INITIAL/STATIC rows rewritten around [C250]; three new accepted-by-DR /
  refused-by-me rows added (member scope, literal-left and `>=`/`<=`, pointer equality) plus the
  faithful `NOT STATIC` control.
* `spec/notes/e2e37-coverage-measurement.md`: its "15 categories" line said 16 and its "12 categories
  all 0 or 1" claim was never tested against a per-category tally — both corrected in place.

## Panel, at the end

`935 byte-exact / 0 fail` (E37C1, E37C3 new), negatives `124/124`, divergence `12/12 as recorded`
(E37B1/B2/B3 new), runtime `16/16` (re-run with `--runtime`, so E2E-37's "not re-run" caveat is
closed), coverage `83 rows / 0 errors`, corpus census `44 HISTORICAL / 41 AUTHENTIC / 3 DR_REJECTED /
15 EXACT / 26 REFUSED / 0 UNEXPECTED`, verified against the committed snapshot, exit 0.

## Standing defects

1. BASED operand in a comparison loads the pointer, not the value [C246] — fix requires the whole
   relation × class × position matrix probed, because NETWORK/E32C8 share the lowering.
2. Unqualified structure-member references unresolved [C248] — the real blocker behind DIOCALLS,
   ENTER, FSCAN, LOAN2, REPORT, MPMCALLB, and the ranked-corpus unlock estimate that depended on it.
3. Static member INITIAL is now correctly attributed but still unimplemented: DR's DATA layout for an
   initial FIXED/CHAR/BIT(n)/VARYING static cell is unsampled.  The accepted probes carry that
   layout as `DATA AREA` sizes (0008/000A/0009) which need comparing with my bind packing — the same
   +2-flavoured anomaly as E32C6/E33MC [C248].
4. No runtime read-back of the pointer store yet; the cheapest form is to accept `nx = addr(z)` as a
   condition [C247].
5. The E30 traversal family and E32C6/E33MC's DATA anomaly are untouched by this episode, and
   §6.4-based re-evaluation remains a named hypothesis, not a cause.
6. Instrument hygiene [C249]: `$?` after a pipeline; CP/M `^Z`; never grep packed `.REL` bytes — cite
   `tools/dis80.py` or `tools/reldump.py`.
