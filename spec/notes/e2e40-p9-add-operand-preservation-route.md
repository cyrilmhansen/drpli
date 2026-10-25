# E2E-40/P9 — Which operand does DR preserve on the stack at an ADD?

**Slice:** E2E-40/P9. **Baseline:** `7edd243` (P8c). **Change:** one predicate in
`ocaml/lib/codegen.ml` (the ADD route selector) plus its comment; no other executable line.
**Evidence:** `golden/e45/` (7 DR programs + DR's own linked `.COM` + DR's own consoles),
`golden/e40n/E40S2`, `golden/e40n/E40S4`, `golden/e45/ADD_REGIONS.txt`,
`golden/e45/CORPUS_SCAN.txt`, `golden/e45/PREDICTIONS.txt` (written before the oracle ran).

## 1. The defect

E40S2 and E40S4 have been pinned divergences since E2E-39, re-pinned by P6, P7, P8, P8a, P8b and
P8c.  Both compute `a + b + c` over `FIXED BINARY` members of an internal structure and both came
out one byte short of DR:

```
                     inner ADD (a+b)                        outer ADD ((a+b)+c)
  DR    0027 LHLD a / PUSH H / LHLD b / POP D / DAD D       0030 PUSH H / LHLD c / POP D / DAD D   (6 B)
  mine  0027 identical to DR                                0030 XCHG     / LHLD c / DAD D         (5 B)
```

DR's CODE was `0x44`, mine `0x43`; DATA agreed at 6.  The whole difference was one instruction at
one address, in both programs.

## 2. What the previous claims said, and why each was reachable

| claim | rule as written | falsified by |
|---|---|---|
| [C150] | push iff the **left operand is syntactically compound** | `MB36 (n*3)+n` = XCHG, in the same probe set that produced the rule; `golden/e2e182/D12` = XCHG behind a compound left; E40S2/E40S4 = PUSH behind a compound left.  Kept as "form-4-before-form-3 precedence". |
| [C254] | push in **tail position** | withdrawn in P3: DR's `PUSH H` in E39S2 sits mid-expression with six bytes after it. |
| [C260] | push iff **BOTH operands are members** | E45S1: `h + a` pushes with an ordinary variable on the left. |
| [C266]/[C267] | about the **store** route (destination addressing mode) | not falsified — same *kind* of rule one level up, and it stayed right. |

`vinfo_both_members` cannot even express the E40S2 case: its arguments are `Eident` names, and a
compound left operand is not a name.  That is the mechanical reason the byte was missing — the
predicate's type made the shape invisible, and the note that recorded the residual described it as
"unmeasured" rather than as unrepresentable.

## 3. The corpus before the probes

`golden/e45/CORPUS_SCAN.txt` (tool: `golden/e45/scan_tails.py`) counts DR's two tails over all
**2050** `.REL` files: **44** park sites (`E5 2A . . D1 19`), **128** swap sites (`EB 2A . . 19`).
Classified by the byte immediately before the park, **all 44 parks follow a `LHLD` of a
relocatable DATA cell** (33 have the filler `0x00` left by the absent operand high byte, 11 follow
`DAD D`).  There is no park behind a `MOV M,H`, `MOV A,L`, `LDAX`, or a call return — so the
question "what makes DR park?" is a question about **the operand it loads next**, and the corpus
says nothing at all about parking behind a computed value.

Of the 44, exactly **11 listings / 6 programs** sit at a *second* add, and the swaps at a second
add are **3 programs** (`D12`, E45S2, E45S3).  That is the entire population this rule governs.
**Listings are not programs, and the duplication is not uniform.**  Older runtime programs have a
second copy under `golden/e32rt_<NAME>/` (E40S2, E40S4, E44A1 appear twice); E45S1 appears exactly
once, so halving the listing count is wrong, and the deduplicated reading is 6 park programs and 3
swap programs.  The scan also reads DR's committed goldens only -- it says nothing about my build,
which is why `golden/e45/CORPUS_SCAN.txt` now says so instead of letting a corpus description read
like a post-fix measurement.

## 4. The probes and what DR said

Seven programs, identical declarations and identical six initializations, only the `put list`
expression differing.  Operands are named from **DR's own linked `.COM`** (`golden/e45l`), where a
cell's identity is recovered from DR's initializer shape — a member is written
`LXI H,<addr> / MVI M,v / INX H / MVI M,v` and an ordinary variable
`LXI H,<value> / SHLD <addr>` — so the prologue itself proves that `a,b,c` are members and `h,k,n`
are not, independent of this compiler.  Full decoded regions in `golden/e45/ADD_REGIONS.txt`.

| probe | expression | inner node | outer node | DR CODE | console |
|---|---|---|---|---|---|
| E45S1 | `h + a + b` | `(ord, member)` → **PUSH** | `(compound, member)` → **PUSH** | 0x54 | 35 |
| E45S4 | `a + h + b` | `(member, ord)` → **XCHG** | `(compound, member)` → **PUSH** | 0x53 | 35 |
| E45S7 | `h + k + a` | `(ord, ord)` → **XCHG** | `(compound, member)` → **PUSH** | 0x53 | 43 |
| E45S3 | `h + k + n` | `(ord, ord)` → **XCHG** | `(compound, ord)` → **XCHG** | 0x52 | 59 |
| E45S2 | `a + b + h` | `(member, member)` → **PUSH** | `(compound, ord)` → **XCHG** | 0x53 | 35 |
| E45S5 | `a + b + 5` | `(member, member)` → **PUSH** | `(compound, literal)` → **no swap at all** | 0x52 | 23 |
| E45S6 | `a + (b + c)` | right group first, `(member, member)` → **PUSH** | `(member, compound)` → **PUSH** | 0x54 | 31 |

Single-variable pairs: **S3 vs S7** differ in one operand's storage class and both nodes flip
together; **S1 vs S4** swap the same two classes between the two positions and both nodes flip;
**S1 vs S7** keep the topology and differ only in the inner pair.  S1, S4 and S7 have **no DR
predecessor at all** for their inner node, and all three land on the rule's prediction.

## 5. The rule

> At a two-operand `FIXED` ADD, DR preserves the left operand on the stack —
> `PUSH H / <load right> / POP D / DAD D` — exactly when the **right** operand is loaded from an
> internal structure member's fixed DATA cell, or is itself compound; otherwise it uses `XCHG`.
> A literal right operand is neither: it is added as a 16-bit immediate pair (`M,I / DAD B`) and
> no swap is emitted.

The discriminator is an **addressing mode**, not a class pair, not a position, not a parse-tree
shape.  It is the same kind of answer as [C266]'s store rule, which is also about where an address
has to be — and both times the rule I first wrote down was a proxy that happened to agree with the
sample in front of me.

Implemented as `rhs_is_imem st r` replacing `vinfo_both_members st l r` at the ADD route selector
(`codegen.ml` ~3960).  Evaluation order stays [C150]'s (left first, then right); the predicate only
asks what DR is about to load into HL.  `vinfo_imem` is `Some k` only for `FIXED BIN(≤15)` members
of an **internal** structure, so POINTER/BASED-view members are excluded by construction and E40Q4
is untouched.

## 6. Order of emission: the second addendum to [C268]

Between writing `rhs_is_imem` and running the panel I *replaced* the arm's whole test with it,
which dropped the requirement that DR's parked form literally contains `PUSH H / LHLD … / POP D`.
`E45S5`'s outer node then predicted a park for `+ 5`, and my emitter would have written
`PUSH H / LXI H,5 / POP D / DAD D` — five bytes of code DR has never emitted in any form.
Caught by running the new predicate over the seven DR programs and comparing the predicted park
sites to their bytes (2 predicted, 3 measured — the third being the literal), **before** the panel
ran.  The fix keeps the classifier narrower than the emitter: `writes_de st r` is a
byte-verified-in-DR condition (`11 lo hi / 2A`, or `ED`/`DD`/`FD` for the conversion prefix), so the
literal case takes `LXI B,k / DAD B` at the site [C150] established for a literal addend rather than
falling through an unproven general route.

This is the [C268] split (a classifier and an emitter that agree by coincidence) arriving from the
opposite direction: P8a's defect was a classifier that was *too narrow* for the emitter; this one
was *too wide*.  The general form of the lesson is that the classifier's predicate has to be the
conjunction of "DR would park here" **and** "this file can emit a park here", and neither half is
derivable from the other.

## 7. Collateral (measured)

**982 byte-exact / 0 fail**, 129/129 refusals, **9/9** pinned divergences (was 11), **45/45** runtime
rows (+7 at DR's own console values 35/35/59/35/23/43/24), coverage 86 rows / 0 errors / 0 warnings,
census 44 programs / 15 EXACT / **0 DIFFERS / 0 UNEXPECTED** and `--verify' clean, INVENTORY 982,
gate exit 0.  Nine programs came out 256/256 whole-file identical to DR: the two divergences this
slice was about and seven of the eight probes (E45S6 is the eighth and is refused).

**Three of my own readings did not survive re-measurement, and they are in this file because
deleting them would lose the only record of how they were reached.**  (i) Diffing instruction
listings instead of whole files, and concluding from DR's `LHLD None/None' that an instruction was
missing -- [C264]'s error, made with the tool that had corrected me.  (ii) Registering E45S1 as a
divergence on a route theory my own output contradicted.  (iii) Writing a post-fix tail count into
`golden/e45/CORPUS_SCAN.txt' without re-running the scan.  See [C271](g).

## 8. Not claimed

* **The rule as shipped is a disjunction, and the two halves have different witnesses.**  This
  compiler parks when the right operand is an internal member cell (`rhs_is_imem`, new in P9) **or**
  when storing/keeping the left operand destroys DE (`writes_de`, [C150]) **or** when the left operand
  is syntactically compound ([C150]).  E45S1's inner node `h + a` -- ordinary value in HL, member on
  the right -- is covered by the SECOND disjunct and not the first: DR parks there because its own
  `SHLD h` store reuses HL as an address, and this compiler parks because that same store destroys
  DE.  The bytes are identical, so the repo contains no sample that says which reason is DR's.  The
  discriminating program is `put list(h + a)`, where nothing is stored: DR would park by the class
  reading and this compiler would not.  **That probe has not been written.**  Until it has, "the
  discriminator is the right operand's addressing mode" is the best-fitting rule over 44 park sites,
  not a rule with a falsification test at its own boundary.
* Array elements as the right operand: DR parks (E45S5's inner node, and LR4-family, RT4, AB6).
  Not generalized here because the corresponding left-operand shapes are unmeasured.
* Whether `writes_de`'s "the conversion prefix destroys DE" reading is *why* DR pushes there: only
  the opcode triples are observed, never a reason.
* POINTER/BASED-view members as right operands: E40Q4, unchanged, still 12 bytes.
* SUB / MUL / DIV routes: untouched by this change.  [C150] found MB41 `h - (a*b)` ambiguous
  between a park and a re-load, and nothing here resolves it.
* `E45S6` — DR compiles it, this compiler refuses in the PUT-item classifier.  A different gap,
  registered as a my-gap negative rather than fixed here.
