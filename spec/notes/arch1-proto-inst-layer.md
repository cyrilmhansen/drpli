# ARCH-1 — isolated prototype: symbolic 8080 with explicit relocation classes

Date: 2026-08-03 (session 14). Scope per instruction: **prototype only, production
architecture untouched.** Nothing in `ocaml/lib` or `ocaml/bin` was modified and
`pli80c` does not link `ocaml/proto/`, so the byte gate is unaffected by anything
here. The three ARCH-0 extractions remain candidates, not approved work.

Code: `ocaml/proto/inst80.ml` (representation + encoder), `ocaml/proto/specimens.ml`
(two DR programs hand-transcribed from their own listings), `ocaml/proto/arch1.ml`
(driver: encode → raw `cmp` against the golden → report). Build: `cd ocaml && dune
build`; run: `_build/default/proto/arch1.exe [--emit DIR]`.

## 1. Result

```
E29A   BYTE-IDENTICAL (128 bytes)  [chain items derived from operand class: 2 ; placed by hand: 0]
E25F   BYTE-IDENTICAL (256 bytes)  [chain items derived from operand class: 2 ; placed by hand: 1]
```

| specimen | what it exercises |
|---|---|
| E29A | header block, external-symbol CALL chain fixups, DR's `0x32`/STA opcode quirk, absolute vs relocatable operands |
| E25F | **the relocation-sensitive case**: mid-stream `SET-LC` switches, DATA-segment descriptor cells, a forward CALL whose target word *is* a chain link (`RELOC code 0014`), a hand-placed `CHAIN-ADDR` header, HL constant reuse, and a procedure body |

E25F is the specimen class that produced my retracted C123 claim, so reproducing it
byte-for-byte from an instruction-level plan is the strongest thing this prototype
could have shown. Padding to 128-byte sectors lives in the driver (a writer property),
not in the representation.

## 2. The representation

Four operand classes, named after what they *contribute to the bitstream* rather than
after mnemonics — because that is where DR's actual behaviour splits:

```ocaml
type operand =
  | I8 of int                     (* one absolute byte:  MVI A,n, opcode bytes      *)
  | I16 of int                    (* two absolute bytes: LXI B,0200 / LXI H,0001    *)
  | Rel of Rel80.seg * int        (* ONE relocatable word: LXI H,*A(4), SHLD, STA   *)
  | CallSym of string             (* opcode + absolute zero slot + CHAIN-EXT, value *)
  | CallSlot of unit              (* opcode + absolute zero slot, no fixup yet      *)
```

The `*` in DR's listing (`LXI H,* A(0004)`) marks the relocatable form; a bare
operand (`LXI H,0001`) stays plain bytes. `I16` vs `Rel` is therefore not a
type-system nicety — it is the difference between 2 and 3 emitted items, and the
difference between a `.REL` DR emits and one it does not.

Ordering is **plan data**, not side effects:

```ocaml
type event =
  | LinkAt of Rel80.rel_item      (* header records; DEF-DATA-SIZE position VARIES *)
  | SetLc of Rel80.seg * int      (* segment switch, declared where DR puts it      *)
  | Ins of ins
  | DataWord of int * operand     (* DATA-segment word + its own SET-LC             *)
  | ChainItem of Rel80.rel_item   (* explicit placement -- see §4                   *)
  | Trailer of Rel80.rel_item
```

The location counter is **threaded through `encode` as a value** and the encoder is a
`List.fold_left` with no mutable state anywhere in `inst80.ml`.

## 3. Threaded location counter: legitimate, and it worked (priority 5 addressed)

ARCH-0 §11 nominated "if `Inst → rel_item` cannot be written without a threaded
location counter, the abstraction is wrong" as the kill criterion. Per the revised
framing, that criterion is measured rather than assumed, and the measurement says the
threaded form is **fine**: nothing had to be smuggled through mutable state, and the
counter only ever moves by `ins_bytes` (a property of the instruction, derived from
its operand class — 1 byte for `I8`, 2 for `I16`/`Rel`, plus opcode bytes).

That derivation is where an earlier draft was wrong, and it is the most instructive
bug of the four. I advanced the counter by `List.length items` instead of byte count.
For `STA dir` those differ — 3 bytes but 2 items (opcode `Data` + operand `Reloc`) —
so the counter drifted and E29A's second chain fixup pointed at `000B` (the opcode
byte) instead of `000C` (the slot). `cmp` caught it at byte 74. The general lesson for
the production extraction: **an instruction's length is not its item count**, and any
layer that reports "the address of my own operand" must compute it from the class, not
from the record list.

Byte identity was preserved, hidden dependencies were reduced (one mutable record with
33 fields → zero mutable state plus one threaded pair), and inspectability improved
(operand classes are enumerable; `ins_bytes` is one function). So the prototype
succeeds on the stated success criterion, not on the surrogate criterion I originally
wrote.

## 4. The "escape hatch" turned out to be an unfinished rule

E25F initially needed one hand-placed `ChainItem`: DR's `LINK-CHAIN-ADDR code 001A`
does not sit next to the chain link (`RELOC code 0014`) whose list it heads — it appears
*after* the following instruction's `LINK-CHAIN-EXT code 001D ?STOPX`. No local rule over
the instruction stream reproduces that, and my first report said so.

That conclusion was wrong, and correcting it is the prototype's best result. Asking
"where does the header *always* appear?" instead of "can I place it locally?" gave:

- **one header per chain, not per site.** Counted across 20 chain-bearing goldens:
  E25C has 8 CALLs / 7 CHAIN-EXT and ONE header; E26J has 9/8 and one; E25F has 4 and
  one; E25D/E25H/E26A/E26K/E27A/E27B/E27C have two targets and exactly two headers.
- **placement at the resolution point.** E25F's header (bit 826) immediately precedes
  `s`'s body (code 001F); E27C's two headers (825, 1032) immediately precede the bodies
  of `p1` (001F) and `p2` (0033). The header belongs to the *definition*, not the
  reference.
- **the head is the newest site** — first site: two absolute zeros; each later site: one
  relocatable CODE word pointing at the current head. This is C123's forward-chain rule
  restated constructively, and it explains why production `fcalls` is *prepended*
  (ARCH-0 §5.3): the list direction was encoding the head-of-chain rule all along,
  without ever saying so.

So the model became two derived constructs (`CallFwd name`, `Resolves name`) and the
`ChainItem` escape hatch was deleted. Final state:

```
E29A   BYTE-IDENTICAL (128 bytes)  [chain items derived from operand class: 2 ; placed by hand: 0]
E25F   BYTE-IDENTICAL (256 bytes)  [chain items derived from operand class: 2 ; placed by hand: 0]
```

Everything in both files — including the record order of chain fixups — now comes from
operand classes, the threaded location counter, and the chain rule, with **zero**
hand-placed link items. The new claim is C135.

Two method points worth keeping. First, the *temptation* was to write a post-hoc rule
("emit the header after the next external chain item") that fits both specimens and is
pure fiction; the discriminating question was which structural event the position always
coincides with, and the answer was visible in the code addresses, not in the bit offsets.
Second, the rule was found by asking a question about *placement*, which is exactly the
kind of question ARCH-0 §5 says production currently cannot answer — there, chain order
is a side effect of a list mutation, so nobody would have thought to look for a rule
where the bytes came from a `::`.

## 5. The four mistakes I made in 250 lines (evidence for the hazard claim)

Not incidental — each is one of ARCH-0's named hazards reappearing in miniature, which
is the best argument I have that these hazards are properties of the problem rather
than of my production code:

1. **List direction.** First version pushed the chain item then the instruction bytes,
   so every `CHAIN-EXT` landed *before* its CALL slot.
2. **List direction, again.** My "fix" (`rev_append (rev xs) acc`) reversed the bytes
   *within* every instruction: `STA` emitted its `Reloc` before its `0x32` opcode
   byte. The dump showed `RELOC` where DR had `DATA` at bit 400; `cmp` showed a
   one-bit shift at byte 32. Three order mistakes total (the `DataWord` SET-LC push,
   same class) — all three invisible in the code that read most naturally.
   Recommendation for any production version: make the emission buffer a queue with an
   `append`, so "later" and "earlier" are named operations instead of `::` vs `@`.
3. **Item count ≠ byte count** (§3 above).
4. **Misreading a listing.** I encoded `LXI H,0001` as relocatable because I had
   pattern-matched DR's `*A(...)` notation onto the wrong operand (§2). The tool that
   found it was `cmp`; a decoded dump would have shown two plausible-looking records
   either way.

Also worth recording: my own `first_diff` returned "DIFFERS at byte 128
(mine=eof dr=eof)" for a **successful** comparison. A checker that reports success as
failure trains you to distrust it, and it nearly made me "fix" a passing specimen.

## 6. Recommendation

Proceed to a **production extraction of the instruction layer** (ARCH-0 §9 step 2) as
a *reviewed* change, not unilaterally — this prototype supports its feasibility but
does not price it. Specifically:

- The representation is adequate for code bytes, relocatable operands, external chain
  fixups, forward chains, segment switches and descriptor cells: the four classes
  covered everything in both specimens with no fifth needed, and no item ever had to be
  placed by hand.
- The extraction must retain `ins_bytes` as a property of the instruction, not of the
  item list (§3), and must express C135's chain rule as a rule rather than as list
  direction.
- The §4 measurement that ARCH-0 flagged as the de-risking prerequisite is DONE, and it
  came back rule-governed. Remaining prototype work before any migration: E27B/E27C
  two-chain re-encoding (to confirm `Resolves` handles two pending chains by name),
  plus the un-probed serialization properties listed below.
- Un-probed here, and therefore still unknown: `DEF-PUBLIC`/`EXTDEF` name truncation to
  6 characters (ARCH-0 §2 step 10), SET-LC-per-byte statics blocks (N306's shape), and
  COMMON-group selection for FILE control blocks. Those are serialization-layer
  properties the prototype's `LinkAt` can express, but they have not been demonstrated.
