# E2E-40/P7 — computed member stores: the destination's addressing mode selects DR's route

## The question

P4 left `E39S7` (`declare 1 g, 2 a fixed, 2 b fixed; g.a = 7; a = a + g.b;`) at 52 code bytes against
DR's 57, with DATA 4/4 and the divergence pinned. Its record said DR parks the value
(`LXI H,<addr> / POP D / MOV M,E / INX H / MOV M,D -- E39S7`), "but that form is sampled on array
elements only", so the gap stayed. That sentence contains three errors, and the task's brief for this
slice — do not accept the reported sequence as sufficient proof of the selection rule — is exactly
what they cost.

## Re-reading the bytes

Both images, decoded through `tools/reldump.py` (which separates payload bytes from relocated
operands), agree instruction-for-instruction from `0006` to `0016`:

| | DR | mine |
|---|---|---|
| 0006 | `LXI H,*(DATA+0x0) / MVI M,07 / INX H / MVI M,00` | same (P4's literal member route) |
| 000E | `LHLD a / PUSH H / LHLD b / POP D / DAD D` | same (P4's member+member ADD route) |
| 0017 | `PUSH H / LXI H,*(DATA+0x0) / POP D / MOV M,E / INX H / MOV M,D` | **`SHLD *(DATA+0x0)`** |
| next | `LXI D,...` (put list) | `LXI D,...` |

So the entire 5-byte difference is the store of a value that is already in HL. (i) P4's quoted
sequence omitted the leading `PUSH H`. (ii) P4's "the whole 3-byte CODE gap ... DR emits `LXI H,
*(000A)' at 0018" quoted a *relocated* operand as an immediate — DR's fixup says DATA+0x0 — and
counted the gap wrong. Both are the [C264] failure mode: reading addresses out of the code section.

## What selects the route — the existing corpus, re-mined

`LHLD a` in a *store* is not "address the cell of `a`": it is "load the cell's value". Every DR
store in the corpus has one of two tails, and the choice tracks the **destination**:

- destination is a **plain cell** → `SHLD <cell>`; the value never leaves HL.
- destination's address has to be loaded into HL (array element, internal member, pointer-displaced
  cell) → `PUSH H / LXI H,<cell> / POP D / MOV M,E / INX H / MOV M,D`.

That is the array rule [C165] and the pointer-formal rule [C127] read at the level they were always
describing. The corpus says so directly: 12 parked sites in the authentic DR objects — array
elements (AC1 `a(3) = b`, AC2, AC3, RT4 ×2, LR7 `z(2) = 32768`), pointer-based cells (DIORAND inside
`get list(rrec)`, MPMCALLB ×3), a POINTER member (E40Q4) and one internal member (E39S7) — against
3740 `SHLD` occurrences in 1185 objects. AC3's `i = a(0) + a(3)` and RT4's `c = a(2) + a(4)` are
*computed values into ordinary destinations* and park nothing, which is why "computed RHS" cannot be
the trigger by itself. And AC1 parks for `a(3) = b`, a bare variable — so at a fixed-address cell
even `literal vs computed` stops being the discriminator, exactly as [C165] said and [C259]/[C260]
partly forgot.

## Falsification probes — predictions written before DR ran

Four new programs (`golden/e41p`; `PREDICTIONS.txt` records the table below plus three competing
models, authored before the oracle ran). All four compile `.REL` byte-identical to mine on the P7
build.

| probe | statement | destination | DR's body | prediction hit? |
|---|---|---|---|---|
| E41P1 | `a = b + 1` | internal member, DATA+0 | `LHLD b / INX H / PUSH H / LXI H,*(0) / POP D / MOV M,E / INX H / MOV M,D` | **exact** |
| E41P2 | `h = g.a` | ordinary scalar | `LHLD a / SHLD *(h)` | **exact** |
| E41P4 | `a = b` | internal member | parked, 11 bytes | **exact** |
| E41P3 | `g.a=7; g.b=5; a = a + g.b` | internal member | E39S7's 17-byte body; console `12` | **exact** |

Three models were on the table. **M1** ("parking follows the RHS shape, so any store whose load
carries a bias parks") predicted `LHLD;INX H;SHLD` for E41P1 — the triple [C260] quotes — 9 bytes
instead of 12. **M2** ("DR's rule is really the array rule read literally: offset 0 parks nothing")
predicted `SHLD` for E41P4. **M3** ("the bias is folded into the destination address") predicted a
fixup at DATA+0x1. **All three are refuted**: the destination relocates to the cell's own offset,
the bias stays on the value (second witness after AC3's `a(4) = b + 1`, whose cell fixup is +0x6 and
whose element size is 2, so +1 is unrepresentable), and a plain copy into a member parks.

The strongest single number: **`LHLD;INX H;SHLD` (`2a .. 23 22`) occurs ZERO times in the code
sections of all 1963 goldens**, mine included — opcode bytes are payload, so a hidden operand cannot
mask an adjacency. Meanwhile 34 authentic DR statements of the form `var = var` (LABELS `y = x`,
R613 `z = x`, R3094/R3101 `a = b; b = c; c = a`, LOAN2 `m = sm`) are `LHLD / SHLD` with **no**
intervening `INX H`. The cited triple is the self-add *ladder* on an ordinary variable — where load
and store name the same cell, so HL holding the value is harmless — misread as a member store.

## The rule, and its two unmeasured edges

Implemented in the common store tail of the `Ast.Eident` assignment route:

```
destination is an internal FIXED BIN(<=15) member  AND  the RHS went through the general
expression path (one mutable flag, set in exactly the catch-all branch that calls `lower_hl')
    -> PUSH H / LXI H,<cell> / POP D / MOV M,E / INX H / MOV M,D
otherwise keep what P4 established
```

The flag is the honest boundary. Two member shapes deliberately keep `SHLD` because DR has no
sample of them: the **self-add ladder** (`a = a + 5` — DR's ladder is measured only on ordinary
variables, and E40L1, P4's probe of the member case, was built with MY compiler and no DR oracle was
ever produced for it, so it is not evidence), and an **out-of-range literal**, which must still run
DR's decimal-conversion calls (`lit_dec_to_hl`) that are unsampled for members. This mirrors C165's
precedence — form 4 before form 3 — one level up. No specimen name, no byte count, no expected
output appears in the predicate.

**Register state, measured rather than inferred.** The parked store leaves HL at `cell+1`, so
constant reuse dies there: `last_imm` is cleared at the *store*, not at the preceding `DAD D`, where
HL legitimately holds the sum — the ZK6 rule, unchanged. E41P1's following `put list(a)` reloads with
a full `LHLD a` and **no `XRA A`**, which is what a still-live zero would have produced
(E36H11/E36H12/ZS3–ZS6), so the kill is right and the ladder/reuse machinery is not being fooled.

## Runtime: an oracle that isn't circular, and one that isn't either

E39S7's own console value is not an arithmetic oracle: DR never writes `g.b`, so its DATA is 0 and
`a + g.b` = `a + 0` = 7 — an implementation that dropped the ADD entirely would print 7 too. That is
why **E41P3** exists with both operands initialized: 12 = 7 + 5 requires the addition to have run
and the parked store to have written the sum. E41P1 (10 = 9+1) and E41P4 (9) are the biased-copy and
plain-copy companions; E41P2 (7) is the ordinary-scalar control. All four values come from DR's own
linked-and-executed `.COM` (`oracle/linkrun.py link/run --tag e41p`), and E41P1's console value is
what makes P6's "execution cannot discriminate" wording need a word: it holds for *offsets*, because
a self-consistent wrong frame still prints the right number, but the bias and the sum *are* visible
in the output here. The honest limit: all four images are byte-identical to DR's, so the run
validates the interpretation of DR's bytes, not an alternative lowering.

## E40S2 / E40S4 are not this defect

They stayed divergent (67 vs DR 68) on the same build where E41P1/P3/P4 came out byte-exact — which
is the direct evidence that they are separate questions, not leftovers. Their stores are all
literals; their residual is one instruction of **operand preservation** inside `a + b + c` (`XCHG`
where DR uses `PUSH H`). P6's gate comment claimed "the same residual E39S7 already pins" and
"C261's predicate is too narrow"; the second half stands, the first is corrected in place. No
selection logic was touched for them.

## Documentation cleanup shipped with this slice

* `bind.ml`: the stale "E39S5 ... head re-dispatch ... left unresolved and refuses" paragraph under
  UNQUALIFIED MEMBER RESOLUTION is replaced by the measured C264 result, including why the level-1
  gate is *not* about E39S5 and what remains deliberately partial.
* `bind.ml`: `group_counts`/`group_info` split into `group_descendants` + `is_group` (the proven
  predicate "has descendants", the only thing layout reads) and `descendant_count` (a number used
  **only** in the unsampled `$S` line `STRUCTURE LEVEL n, MEMBERS k`, whose DR meaning — direct
  children vs subtree, for level ≥ 2 — was never observed; the value here is subtree descendants at
  all depths). Diagnostic behaviour and layout are byte-for-byte what P6 produced; the E40S3 dump
  still prints `.H STRUCTURE LEVEL 2, MEMBERS 2`.
* `PERIMETER.md`: **the P4 table had lost a whole row** — my P6 splice consumed "member store of a
  COMPUTED value" and left the E39S5 row with 7 fields and the text "stays in ts form destroys HL".
  Both restored, the deleted row from `git show 6df2bd9:spec/PERIMETER.md`.
* `COVERAGE.tsv`: two rows recorded `STATIC on ... MEMBER OF EMPLOYEE@31 is unsampled` as ENTER's
  verified blocker. That refusal was the phantom subgroup cell, never a DR-shaped fact: ENTER and
  UPDATE stand behind keyed `open ... environment(...)` again, REPORT behind `STATIC on CHAR(15)`,
  MPMCALLB unchanged behind `STATIC on CHAR(27)`.
* `codegen.ml`: the three errors in P4's store-gate note quoted above.
* `claims`: [C266] adds the rule and the corrections; C260's citation gets the definitive zero-count
  and an explanation of what the triple really was; C266 point 1 also corrects my own first draft of
  this slice, which accused C260 of leaving the claim standing when it had already withdrawn it.

## Provenance, and one DR behaviour I did not explain

Sources `artefacts/E41P1..P4.PLI`; DR compile transcripts `golden/e41p/transcript-batch0.txt` and
per-program `E41Pn/E41Pn.PRN` (banner `PL/I-80 Compiler Version 1.4, Serial No. 3032-0000-001130,
Digital Research, Inc.`); DR link transcripts `golden/e41p/link-batch0/1.transcript.txt`; DR run
output `golden/e41p/E41Pn.output.txt`, whose contents are `10`, `7`, `12`, `9` -- exactly the values
in the four new RUNTIME.txt rows. `golden/e41p/PREDICTIONS.txt` holds the model table written before
the oracle ran, including the three refuted models.

**One thing happened that I recorded but did not resolve.** E41P2's FIRST spelling was
`declare 1 g, 2 a fixed, 2 b fixed, 1 h fixed; ... h = g.a;` -- `h` declared as a level-1 item inside
structure `g`. DR rejected it with `STRUCTURE ?` in PASS 1 and produced no `.REL` (the v1 PRN, kept
in `/tmp/e40p7/e41p_v1/E41P2/E41P2.PRN`, flags the declaration line, and the session log reads
`E41P2  diag  PRN=True REL=False`). Moving `h` to its own `declare` statement compiled cleanly. I did
NOT determine the mechanism: it could be `g` gaining a member named `h` while `h` is also referenced
unqualified, or the level-1-inside-structure spelling itself, and the PRN's marker position does not
discriminate. So the probe was redesigned around the shape rather than explained by it, and this is
an unmeasured DR behaviour, not a lesson. It is adjacent to [C255]'s DUPLIC rule and [C257]'s
qualify-at-the-use, and worth a probe of its own in a later slice.

## Panels

`949 → 954` byte-exact (E39S7 promoted from the divergence panel by the panel's own failure,
E41P1–P4 registered); divergences `12 → 11` (E40Q4, E40S2, E40S4 + the 8 older rows); runtime panel
26 rows; negatives 125/125; coverage 85 rows / 0 errors; census 44 programs with `msg` now compared
(15 EXACT / 0 DIFFERS / 26 REFUSED / 0 UNEXPECTED). Inventories regenerated with `--update-inventory`
(the C262 cycle), then re-validated by an ordinary gate run.
