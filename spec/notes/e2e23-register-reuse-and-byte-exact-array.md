# E2E-23 — C168 register reuse and byte-exact ARRAY.PL1

**Result: ARRAY.PL1 is byte-identical to DR v1.4 and runtime-identical to DR's own `.COM`.**
The divergence panel is now empty of pre-existing programs: all four of
AB19/AB21/RT1/ARRAY are byte-exact, and every one of them that prints values was
run and compared against a `.COM` built from DR's own `.REL`.

Gate, from a clean rebuild: **607/607 byte-exact, 101/101 negatives, divergence
3/3 as recorded, exit 0.**  Corpus sweep: 159 exact / 40 refused / **zero bare
crashes**.  `ocaml/proto/` untouched (md5 `e67a686891fb…`).

Commits: `ef76202` (P1+P2+P4, the zero-store rule) and `93d9899` (P3, the HL-reuse
forms).

## What the task expected and what was true

E2E-22 recorded ARRAY's residual divergence as "the C168 peephole family **plus a
1-byte code-size delta in the same family**".  Both halves were wrong in the same
direction: the 1-byte delta *was* the peephole, because DR's zero-store form is
`XRA A / MOV M,A / INX H / MOV M,A` (4 bytes) where mine was
`MVI M,00 / INX H / MVI M,00` (5).  One site, one cause, one rule.  Similarly,
AB19/AB21/RT1 were labelled as needing cross-statement constant reuse — they
needed one fact that this codebase already tracks (`st.last_imm`, "HL holds a
known constant") to be *shared* with the array route, plus two missing instruction
arms.  Nothing here is a register allocator.

## Priority 1 — cause, established before any code changed

Analysis on the `.REL`'s own code stream (not the linked `.COM`, which mixes in
RTL placement).  Aligning mine against DR by address showed one differing hunk:
the whole 438/640 raw-byte figure is relocation cascade, not hundreds of
instructions.  Mine 181 code bytes vs DR 180, DATA 62 = 62.

## Priority 2 — the rule, measured on twelve probes first

A corpus survey framed it before probing: across 1310 DR `.REL` files,
`MVI M,00` appears in 51, the all-zero pair `36 00 23 36 00` in **none**, and
`AF 77 23 77` in exactly three distinct programs (E26A, ARRAY, ALLTST) — always
paired stores from a single `XRA`.  That said "value-triggered and narrow", not
"peephole family", and pointed at an accumulator *fact* rather than a pattern.

| probe | source shape | DR | reading |
|---|---|---|---|
| ZS1 | `a(3) = 0` | `XRA / MOV M,A / INX / MOV M,A` | constant-index route too, not pointer-only |
| ZS2 | zero; zero | one `XRA`, four `MOV M,A` | survives a statement boundary and `LXI H` |
| ZS4 | zero; `b=5`; zero | one `XRA` | survives `LXI H,0005 / SHLD b` |
| ZS9 | zero; `i=2`; `a(i)=0` | one `XRA` | survives the **whole variable-index ladder** |
| ZS10 | zero; `a(4)=7`; zero | one `XRA`, but 7 uses `MVI M,07` | **counterexample**: nonzero stores neither use nor disturb A |
| ZS5 | zero; `call q`; zero | **two** `XRA` | **counterexample**: a call invalidates (C141, byte level) |
| ZS7 | zero; `put …`; zero | two | `MVI A`/`LDA` invalidate |
| ZS8 | zero; `if i>1 then b=2`; zero | two | the compare writes A; branch is a merge — invalidated on both readings, so it cannot be wrong in either |
| ZS3, ZS6 | variable index; DO-loop body | XRA pair | ARRAY's own site; loop-body reuse is re-executed and correct |

Implementation: one boolean in the codegen state, set **only** where I emit my own
`XRA A`, plus an operand-byte counter so operand bytes can never be mistaken for
opcodes (a stray `0xAF` byte must not manufacture "A is zero" — that distinction is
the difference between a missed optimization and a wrong value).  Unknown opcodes
invalidate.  No IR, no allocator, no constant propagation.

## Priority 4 — promotion, with runtime evidence

- ZS1–ZS12 byte-exact (checkpoint A).
- ARRAY byte-identical to `golden/e2e214/ARRAY/ARRAY.REL` (checkpoint B).
- ARRAY linked with LINK 1.31 and run: **75 lines, identical to DR's own `.COM`**;
  DATA area 62 = 62, so no layout or neighbouring-variable regression.
- ZS11 (`zero; b=5; zero; put …`) and ZS12 (`zero; call q; zero; put …`) were also
  linked and run: `0 0 5` and `0 0`, matching DR.  This is what makes the
  counterexamples semantic — a reused accumulator that had *not* been re-cleared
  would print whatever `q` left in A.
- Promotion went through the gate's own requirement: the divergence checker
  **failed** on ARRAY's disappearance ("NOW BYTE-EXACT — promote it"), which is the
  designed signal, not something to suppress.  Row deleted, `add_spec`, inventory
  rewritten.

## Priority 3 — the HL-reuse forms

| probe | transition | DR | | probe | situation | DR |
|---|---|---|---|---|---|---|
| ZK1 | 1→2 | `INX H` | | ZK5 | interrupted by `call q` | fresh `LXI H` |
| ZK4 | 2→1 | `DCX H` | | ZK6 | interrupted by a byte-store element write | fresh `LXI H` |
| ZK3 | 257→513 | `INR H` | | ZK12 | `a(1)=4; x=5` | reuse spans the offset-0 element store |
| ZK7 | 1→257 | `INR H` | | ZK8/10/11 | out-of-range literals | **different route entirely** |
| ZK9 | 257→1 | `DCR H` | | ZK2 | 1→5 | `MVI L,05` |

RT1 is `INR H` (`s1=257`, `a(1)=513`); AB19/AB21 were the element route not
carrying the fact.  `hl_const` moved to module level so both routes use **one**
copy of the measured rule.

## Three mistakes, all caught by the panel or by running things

1. **Double emission.** My first version of the element route called `lower_hl`
   *and* `hl_const`.  It added bytes instead of removing them and left a stray
   reload in HL.  Caught by sizes moving the wrong way.
2. **A wrong value, then blamed on DR.** That intermediate build made AB19 print
   `2 1 4`.  I then ran a *stale* `.REL` (copied into a golden directory before the
   fix), saw `4`, and nearly reported a DR miscompile — DR's own `.COM` prints
   `2 1 3`.  `cmp` against the file I had just produced settled it: current build
   is byte-identical and prints correctly.  **Runtime evidence must come from the
   same artifact the byte check uses.**  AB21 and RT1 happened to be unaffected,
   but I re-ran all three from the current build rather than trust that.
3. **An invented guard.** ZK8/ZK10/ZK11 looked like "DR refuses reuse when bit 15
   flips".  A sign guard was written on that reading, then removed when the raw
   bytes showed DR does not reload there at all: it routes the out-of-range literal
   through `LXI H,0000 / MVI A,k / CALL / CALL` and allocates a 4-byte DATA cell, so
   it never reaches the reuse question.  The misreading came from trusting a
   disassembly listing that was misaligned by `SHLD`'s relocation operands.  The
   guard is gone — it was inert (595/595 held with and without it) and an unproven
   condition in instruction selection invites a later reader to trust it.  The three
   probes are pinned in `DIVERGENT.txt` as their own open item.

Also fixed in the gate itself: `DIV-OK` hardcoded "data agrees" and
"(C168 peephole)", which contradicted the rows it was reporting; it now prints the
measured data status and quotes the row's own cause, and a malformed shape field
aborts with the offending line instead of a `ValueError`.

## Open items this session leaves behind

- **Out-of-range literals** (`fixed` cannot hold 65535 / 32768): DR stores them via a
  data cell + runtime call.  Three probes pinned with measured shapes.  Values agree;
  only bytes differ.  This is a self-contained next step.
- **`DCX/INX` repeats beyond 2** and **`MVI H,k`** — never observed; left unimplemented.
- The pre-existing open list from E2E-22 is unchanged: append layout (AB7/EA1/AB14),
  AB13 multi-dimensional, AB5/AB15 STATIC arrays, AB11's condition form, named FILE I/O,
  C161 mixed DEC/BIN.
- C146 / ARCH-1: on hold.  ARCH-1 production untouched.
