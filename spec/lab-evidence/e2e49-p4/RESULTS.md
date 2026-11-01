# E2E-49/P4 — RESULTS (composite FIXED/TEST bank: G1..G8, H1..H6, I1..I6, J1..J4)

## 0. Lineage

- Probes + `mkprobes.py` + `HYPOTHESES.md` + `BASELINE-MINE.txt` committed BEFORE any
  oracle call at **`328eb3f`** (the prediction SHA; `git log --format=%h --
  probes/E49G1.PLI | tail -1`). `golden/e49p4` did not exist before the run. Every
  emitted probe line is <= 71 columns; files are CRLF + `^Z` ([C193] (b)).
- ONE oracle campaign exactly as pre-registered:
  `PLI_SRC=probes python3 oracle/batch.py E49G1 E49G2 E49G3 E49G4 E49G5 E49G6 E49G7
  E49G8 E49H1 E49H2 E49H3 E49H4 E49H5 E49H6 E49I1 E49I2 E49I3 E49I4 E49I5 E49I6
  E49J1 E49J2 E49J3 E49J4 --tag e49p4 --switches '$L$D'`
  -> **24 ok / 24** (`golden/e49p4/`, summary; the runner split into internal batches).
  **NO refusals at all**: all 24 `.PRN` print `NO ERROR(S) IN PASS 1` and
  `NO ERROR(S) IN PASS 2` (verified by count over every file). Verdicts judged on
  complete `.REL` bytes with `tools/reldump.py` (PROTOCOL #6), whole files by `cmp`.
- Classification (PROTOCOL #3): **every difference this round is `my-gap`** — DR
  accepted everything; my baseline (BASELINE-MINE.txt) refused all eighteen A/B/D rows
  and the six C rows came out WHOLE-FILE byte-identical to my output.
  **No `dr-refuses` row exists in this bank.**

## 1. Prediction vs verdict (every MISS kept — this round has NONE)

Head notation: `E5`/`D1` = the stacked member-pair parking bytes of [C337]; `EB` = the
staged literal head of [C333]; `11` = the direct literal head of [C330]; immediates are
`06 x / 3E y` positional on the LOWERED operands, `06 x / 78` the [C342] collapse;
skip `d2` JNC strict / `da` JC weak ([C346] BRANCH law) / `ca` JZ-negated ([C072]).

| id | predicted | measured verdict | score |
|---|---|---|---|
| P-G1 (`rec.na < 'ABC'`, 3/3) | coincident H-A: STAGED `06 03/78` d2, CODE 65, DATA 000F, fill->001C | ACCEPTS: `21 *D(0005 na)/EB/21 *D(0000 'ABC')/06 03/78/CD ?SCCCM/D2 -> 001C`; CODE 65, DATA 000F | **HIT** — `< ' written order, staged, COLLAPSED at equal attributes; whole file differs from golden C1 ONLY at the packed name bytes + the skip byte (file offsets 4,18,26,87: C2->D2) |
| P-G2 (`'ABC' < rec.na`, 3/3) | coincident H-A: DIRECT `06 03/78` d2, CODE 64, fill->001B | ACCEPTS: `21 *D(0005)/11 *D(0000)/06 03/78/CD ?SCCCM/D2 -> 001B`; CODE 64, DATA 000F | **HIT** — differs from golden C2 only at name bytes + skip byte 86 |
| P-G3 (`rec.na > 'AB'`, 3/2 written) | H-A-sw: DIRECT (swap lowers literal first) `06 02/3E 03` d2, CODE 65, DATA 000E, fill->001C; H-A-or: STAGED `06 03/3E 02` CODE 66 | ACCEPTS: `21 *D(0004 na)/11 *D(0000 'AB')/06 02/3E 03/CD ?SCCCM/D2 -> 001C`; CODE 65 | **HIT H-A-sw / H-A-or FALSIFIED** — the byte at 0009 is `11` not `EB` and the immediates are the LOWERED pair `06 02/3E 03` |
| P-G4 (`'AB' > rec.na`, 2/3 written) | H-A-sw: STAGED (swap lowers member first) `06 03/3E 02` d2, CODE 66, fill->001D; H-A-or: DIRECT `06 02/3E 03` | ACCEPTS: `21 *D(0004)/EB/21 *D(0000)/06 03/3E 02/CD ?SCCCM/D2 -> 001D`; CODE 66 | **HIT H-A-sw / H-A-or FALSIFIED** |
| P-G5 (`rec.na <= 'ABCD'`, 3/4 written) | H-A-sw: DIRECT `06 04/3E 03` da, CODE 65, DATA 0010 pool WHOLE, fill->001C; H-A-or: STAGED `06 03/3E 04`; falsifier: truncated pool / min-max / refusal | ACCEPTS: `21 *D(0006 na)/11 *D(0000 'ABCD')/06 04/3E 03/CD ?SCCCM/DA -> 001C`; CODE 65, DATA 0010 | **HIT H-A-sw; [C345] TRANSFERS** — the over-extent literal is pooled WHOLE under a swapped weak relation; H-A-or falsified |
| P-G6 (`'ABCD' <= rec.na`, 4/3 written) | H-A-sw: STAGED `06 03/3E 04` da, CODE 66, fill->001D; H-A-or: DIRECT `06 04/3E 03` | ACCEPTS: `21 *D(0006)/EB/21 *D(0000)/06 03/3E 04/CD ?SCCCM/DA -> 001D`; CODE 66, DATA 0010 | **HIT H-A-sw / H-A-or FALSIFIED** |
| P-G7 (`rec.na >= 'ABC'`, 3/3) | coincident H-A: STAGED `06 03/78` da, CODE 65, fill->001C | ACCEPTS exactly that; `>=` does NOT swap (written order) | **HIT** — the fourth relation's own witness; skip byte alone separates G1/G7 (file offset 87: D2 vs DA) |
| P-G8 (`'ABC' >= rec.na`, 3/3) | coincident H-A: DIRECT `06 03/78` da, CODE 64, fill->001B | ACCEPTS exactly that | **HIT** |
| P-H1 (`na < rec.nb`) | H-B-invis: golden F1 but the packed name bytes | `cmp -l` vs `golden/e49p3/E49F1/E49F1.REL`: differs ONLY at bytes 4,5,18,26,27 | **HIT** — bare LEFT admitted in a relation |
| P-H2 (`rec.na > nb`) | H-B-invis twin: swapped loads (`nb` FIRST), collapse `06 03/78`, d2, CODE 66, DATA 000C, fill->001D | ACCEPTS exactly that: `21 *D(0005 nb)/E5/21 *D(0002 na)/D1/06 03/78/CD ?SCCCM/D2 -> 001D`; vs H1 the ONLY other differences are the two `*D` reloc operands + skip-operand fill (file 58,62,63) | **HIT** — bare RIGHT admitted AND the ORDER law holds on the bare spelling |
| P-H3 (`na <= nb`) | golden F3 but names | differs from golden F3 ONLY at bytes 4,5,18,26,27 | **HIT** — bare/bare accepted |
| P-H4 (`nb >= na`) | golden F3 TOO (written-order `>=` lowers nb-first == F3's swapped `<=`) — the strong transfer test | differs from golden F3 only at the packed name bytes (4,5,6,18,19,26,27,28) | **HIT** — TWO DIFFERENT WRITTEN SPELLINGS, ONE OBJECT; the LOWERED pair is canonical across qualification AND orientation |
| P-H5 (`na > rec.s2`) | golden F2 but names | differs from golden F2 ONLY at bytes 4,5,6,18,19,26,27,28 | **HIT** |
| P-H6 (`s2 <= rec.na`) | the I5 prediction (swap, na first, `06 03/3E 02`, da, CODE 67) | differs from the I5 golden ONLY at bytes 5,6,18,19,27,28 | **HIT** |
| P-I1 (`rec.na < rec.s2`) | DR == my arm-c baseline bytes (written na first, `06 03/3E 02`, d2, CODE 67, DATA 000C, fill->001E) | whole-file `cmp`: **ZERO differing bytes** vs my baseline `.REL` | **HIT — no arm** |
| P-I2 (`rec.s2 < rec.na`) | written s2 first, `06 02/3E 03`, d2 | ZERO differing bytes vs baseline | **HIT — no arm** |
| P-I3 (`rec.s2 > rec.na`) | swapped: na first, `06 03/3E 02`, d2 | ZERO differing bytes vs baseline | **HIT — no arm** |
| P-I4 (`rec.na <= rec.s2`) | swapped: s2 first, `06 02/3E 03`, da | ZERO differing bytes vs baseline | **HIT — no arm** |
| P-I5 (`rec.s2 <= rec.na`) | swapped: na first, `06 03/3E 02`, da | ZERO differing bytes vs baseline | **HIT — no arm** |
| P-I6 (`rec.na >= rec.s2`) | written na first, `06 03/3E 02`, da | ZERO differing bytes vs baseline; AND the I6 whole file differs from the I5 whole file only at the packed name bytes | **HIT — no arm** — `<=` swapped and `>=` written LOWER TO THE SAME OBJECT |
| P-J1 (`^(rec.na = rec.nb)`) | verdict OPEN (first syntax test); H-D-inv: golden E49B5 bytes (mm collapse, CA) | ACCEPTS; `cmp -l` vs `golden/e49p2/E49B5/E49B5.REL`: differs ONLY at bytes 4,5,18,19,26,27 (packed names) | **HIT H-D-inv/H-D-simpl (convergent)** — `^( = )' IS the `^=' object byte for byte |
| P-J2 (`^(rec.na < rec.nb)`) | H-D-inv: F1 head with d2 inverted to da; H-D-extra: extra bytes | ACCEPTS: F1's written-order collapsed head with skip **0xda** -> 001D; vs golden F1 differs only at name bytes + the skip byte (file 82) | **HIT H-D-inv/H-D-simpl; H-D-extra FALSIFIED** — no extra branch, helper or inversion byte anywhere; also byte-equal to the un-negated `na >= nb` lowering (same head, same JC) |
| P-J3 (`^('ABC' = rec.na)`) | H-D-inv: golden E49C4 bytes (direct collapse, CA, CODE 64, DATA 000F, fill->001B) | ACCEPTS; differs from golden C4 ONLY at the packed name bytes (4,5,6,18,19,26,27,28) | **HIT H-D-inv/H-D-simpl** — negation transfers to the literal template as the complement object |
| P-J4 (`^(rec.na <= rec.s2)`) | H-D-inv: the I4 head with da inverted to d2 (swap, `06 02/3E 03`, CODE 67) | ACCEPTS: `21 *D(0008 s2)/E5/21 *D(0002 na)/D1/06 02/3E 03/CD ?SCCCM/D2 -> 001E`; whole file differs from golden **F2** (`rec.na > rec.s2`) ONLY at the packed name bytes | **HIT H-D-inv/H-D-simpl** — `^( <= )' IS the `>' object byte for byte |

**Count: 24 HIT, 0 MISS.** No pre-registered prediction was falsified except the
explicit ALTERNATIVES (H-A-or falsified at G3..G6; H-D-extra falsified at every J row;
H-A-refuse and H-D-refuse falsified by the acceptance itself). H-D-inv and H-D-simpl are
BYTE-CONVERGENT on all four D shapes, exactly as pre-registered: NO claim may
distinguish "skip inverted on the un-negated head" from "operator rewritten to the
complement" from these objects, and RESULTS §2 words the law so that both readings stay
admissible.

## 2. Laws read out of the `.REL` records

### 2.1 Panel A — the ORDER law REKEYS the literal template; everything else transfers
- E49G1..G8: ordered relations between a FIXED member and a literal are ACCEPTED on the
  SAME two `?SCCCM` literal templates as `=`/`^=`. The template follows the operand pair
  **AS LOWERED**, exactly as the swap reorders the member-pair loads in [C346]: lowered
  member-first -> STAGED `21 *D(member) / EB / 21 *D(pool)`; lowered literal-first ->
  DIRECT `21 *D(member) / 11 *D(pool)`. `>`/`<=` swap (G3/G4/G5/G6 change template under
  the swap), `<`/`>=` keep written order (G1/G2/G7/G8). H-A-or (written orientation keys
  the template) is FALSIFIED at all four discriminating rows.
- The immediates are positional on the LOWERED operands (`06 = first lowered`,
  `3E = second lowered`): G3 `06 02/3E 03`, G4 `06 03/3E 02`, G5 `06 04/3E 03`,
  G6 `06 03/3E 04`. Equal attributes COLLAPSE to `06 03 / 78` in BOTH literal templates
  under relations (G1/G2/G7/G8) — [C342] keys on the two numbers, not the relation, now
  measured for all four relations.
- BRANCH law transfers: strict `<`/`>` skip JNC `d2` (G1..G4), weak `<=`/`>=` skip JC
  `da` (G5..G8). Skip-operand slot and fill: staged collapse `13/14-15 -> 001C`;
  staged pair `14/15-16 -> 001D`; direct collapse `12/13-14 -> 001B`; direct pair
  `13/14-15 -> 001C`; CODE 65/66 (staged) and 64/65 (direct) per [C347]-style head size.
- [C345] TRANSFERS to relations: the over-extent literal `ABCD` (4 > char(3)) is
  ACCEPTED and pooled WHOLE (DATA 0010) in both orientations under `<=`, with the
  positional pair on the lowered operands. No truncation, no min/max, no refusal.
- [C340] relocation-slot law holds under the rekey: the staged heads carry
  `*D(member)` then `*D(pool)`; the direct heads the same two slots in the same
  record order; only which REGISTER pair (HL via `21`/`EB` vs `11`) differs.

### 2.2 Panel B — qualification stays INVISIBLE to the relation arm
- E49H1..H6: EVERY qualification mix (bare-left, bare-right, bare/bare) is accepted in
  an ordered relation and produces the law-constructed qualified object byte-for-byte
  except the packed module-name fields (no checksum field exists in these 256-byte
  objects — the name offsets are 4..6, 18..19, 26..28). [C344] transfers to the relation
  family; H-B-gate/H-B-mixed FALSIFIED.
- E49H4 (`nb >= na`) is byte-identical (but names) to golden E49F3 (`rec.na <= rec.nb`)
  and E49H3 (`na <= nb`): the canonical thing DR lowers is the PAIR (first lowered,
  second lowered) plus the relation's strictness — written qualification and the written
  choice between `<=`/`>=` leave NO byte trace.

### 2.3 Panel C — the arm-c [C346] law transfers to the full unequal-extent matrix
- E49I1..I6: DR accepts every cell and each object is WHOLE-FILE byte-identical to my
  arm-c baseline `.REL` — the stacked mm head, the positional `06/3E` pair with NO
  collapse at 3/2, the ORDER law (`<`/`>=` written, `>`/`<=` swapped), the BRANCH law,
  DATA 000C, CODE 67, fill `-> 001E`. **NO arm was needed for these six.**
- The 4-relations x 2-orientations matrix at unequal extents is COMPLETE:
  written-order loads (I1 na-first, I2 s2-first, I6 na-first) and swapped loads (I3,
  I4, I5) all follow [C346] with zero exceptions.
- I5 (`rec.s2 <= rec.na`) and I6 (`rec.na >= rec.s2`) are byte-equal but the names: the
  same lowered pair under the same strictness from two relations — the §2.2 canonicality
  reading measured on the QUALIFIED spelling too.

### 2.4 Panel D — `^( ... )' is ACCEPTED on string heads and lowers to the COMPLEMENT object
- E49J1..J4: DR compiles the composition with NO ERROR in both passes. The objects are
  the UN-NEGATED complement's objects byte-for-byte (but names):
  `^(rec.na = rec.nb)` == E49B5 (`^=` mm collapse, CA);
  `^('ABC' = rec.na)` == E49C4 (`^=` direct collapse, CA);
  `^(rec.na < rec.nb)` == F1's head with the skip byte `da` (identical to what an
  un-negated `na >= nb` member pair would carry under §2.1/§2.3 — and NOT F3, which is
  the swapped `<=` load order);
  `^(rec.na <= rec.s2)` == E49F2 (`>`, swapped, `06 02/3E 03`, JNC d2).
- The lowering is therefore: **negation flips the relation to its complement WITHOUT
  changing the lowered pair** — the skip byte is inverted on the head the un-negated
  relation would NOT have produced... H-D-inv and H-D-simpl coincide exactly here, as
  pre-registered (J1: `=` head + CA == `^=` head; J2: `<`-written head + weak skip ==
  `>=` written head; J4: swapped `06 02/3E 03` head + strict skip == `>` head). Both
  readings stay admissible; NO claim may prefer one. H-D-extra FALSIFIED: no CMA, no
  second CALL, no extra branch; the head bytes, CODE size, DATA size and fill all equal
  the complement's.
- The branch law is confirmed consistent: the negated weak skips JC, the negated strict
  skips JNC, `=`/`^=` keep C2/CA — the skip byte ALWAYS follows the (possibly flipped)
  relation, never the negation syntax.

### 2.5 Frame arithmetic reconfirmed
All C/D/mm rows: DATA 000C (member pair pools nothing, [C341]); all literal rows: the
literal pooled FIRST at 0000 shifting the frame ([C314]); `k = 1` is the six-byte
`21 01 00 22 *D(k)`; the skip fill points at the `put list` after the then-statement
([C309] as extended by [C347]).

## 3. What this round did NOT measure

- NO runtime semantics: what `?SCCCM` returns and how JNC/JC/JZ read it is NOT claimed;
  no `spec/RUNTIME.txt` row may come from this family (byte tier only).
- STORE value or STORE target with any of these new shapes (relation-with-literal,
  bare-in-relation, negated compare) — unmeasured, keeps refusing.
- Literal-vs-literal in any relation; BASED members; fixed-member truthiness; `<>`/`><`
  spellings; `&`/`|` composition of conditions; `^( )` over a relation WITH A LITERAL
  operand (the J bank negates `=`/`<`/`<=` on member and one literal-equal row only);
  `^( )` over an over-extent or bare spelling; `^(` `^=` `)` double negation.
- Ordered relations with a literal at UNEQUAL attributes under `>=`/`<` beyond
  G3..G6's `>`/`<=` sample; the collapse in a swapped literal head with unequal lengths
  cannot exist by construction (collapse needs equal numbers — measured only at 3/3).
- Bare spellings in the equal-length literal template under relations (D4 measured bare
  `=` only); qualification x orientation x relation is sampled at H's six points, not
  exhaustively.
- Empty-varying and other non-FIXED families: untouched.

## 4. Classification (PROTOCOL #3)

All twenty-four rows ACCEPTED by DR (`24 ok / 24`, both passes clean in every `.PRN`).
- `my-gap` (18): E49G1..G8 (ordered relations with a LITERAL — my `str_cmp_shape_fix_rel`
  admits no literal side), E49H1..H6 (BARE spellings in relations — the arm admits
  `ImemF/ImemF` only), E49J1..J4 (NEGATED string compares — my `lower_test_skip0` NegL
  arm refuses string operands by name).
- Already byte-exact (6): E49I1..I6 — whole-file `cmp` against my baseline `.REL` shows
  ZERO differing bytes; NO arm needed; [C346] transfer MEASURED.
- `dr-refuses`: NONE this round.
