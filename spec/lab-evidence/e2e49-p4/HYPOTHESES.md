# E2E-49/P4 — hypotheses and PREREGISTERED predictions (COMPOSITE: ordered relations with a LITERAL, BARE spellings in relations, the UNEQUAL-EXTENT relation matrix, NEGATED compares — E49G1..G8, E49H1..H6, E49I1..I6, E49J1..J4)

Written and committed **before** the DR oracle is invoked on any P4 probe, under
PROTOCOL.md Part 1 #1 (the committed blob, not a file mtime, proves ordering).
`RESULTS.md` §1 must be a prediction-vs-verdict table over exactly these rows; every
MISS stays in that table (PROTOCOL #2).

    probes written by spec/lab-evidence/e2e49-p4/mkprobes.py (CRLF + ^Z, [C193] (b),
      every emitted line <= 71 columns -- the measured law that killed P2d run 1)
    baseline of MY compiler recorded in BASELINE-MINE.txt at HEAD 398fa2c (NO oracle
      call): Panel C (I1..I6) ACCEPTS on the arm-c [C346] bytes; EVERY Panel A (G1..G8),
      Panel B (H1..H6) and Panel D (J1..J4) probe refuses with rc=2 (A/B through
      `imem_refuse "comparison"' naming the written-left member; D through the named
      negated-TEST refusal).
    the commit that adds probes/E49G*/H*/I*/J*.PLI + mkprobes.py + this file +
      BASELINE-MINE.txt is the PREDICTION SHA (it is committed BEFORE any oracle
      invocation); `golden/e49p4' does not exist at that commit.

## What this round is

The operator-authorized campaign **E2E-49/P4 — composite CHARACTER FIXED / TEST bank,
four panels, 24 specimens**. Every probe keeps the E49B shared DECL (`1 rec, 2 na
char(3), 2 nb char(3), 2 s2 char(2); dcl k fixed bin(15);`) and the
`put list('K=', k);` tail, so the [C309] skip fill and the [C314] pool-first DATA
layout stay comparable with `golden/e49p1..p3`. Frame arithmetic (from [C314] + the
measured heads): member pair pools nothing -> DATA 000C, na@0002 nb@0005 s2@0008 k@000A;
literal 'ABC'/'AB'/'ABCD' pooled first -> DATA 000F/000E/0010, pool@0000, na@0005/0004/
0006; then-statement `k = 1` is SIX bytes (`21 01 00 22 *D(k)`) and the skip fill points
at the `put list` that follows it.

- **Panel A (E49G1..G8)** — ORDERED RELATIONS with a LITERAL operand: all four
  relations, both written orientations, equal attributes (3/3: G1/G2/G7/G8 with 'ABC'),
  unequal (3/2 and 2/3: G3/G4 with 'AB') and over-extent (4/3: G5/G6 with 'ABCD').
  Never probed: [C346] scoped itself to the QUALIFIED member pair; [C342]/[C343]/[C345]
  are `=`/`^=` laws. MY BASELINE REFUSES all eight (rc=2), so every A row is my-gap iff
  DR accepts.
- **Panel B (E49H1..H6)** — BARE spellings inside ordered relations: the relation arm
  admits `ImemF/ImemF` ONLY. [C344] proved qualification invisible to every measured
  encoding (`=`/`^=`, both templates). MY BASELINE REFUSES all six.
- **Panel C (E49I1..I6)** — the UNEQUAL-EXTENT relation matrix on QUALIFIED pairs,
  completing 4 relations x 2 orientations where F2/F4 sampled only two cells. MY
  BASELINE ALREADY ACCEPTS on arm-c bytes; primary: DR's objects EQUAL them (NO arm).
- **Panel D (E49J1..J4)** — NEGATED compares `^( ... )' on string heads: the FIRST
  syntactic-acceptance probe for the composition in this family. MY BASELINE REFUSES
  all four by name.

## Competing hypotheses (per panel) and discriminating predictions

Head notation (measured P3 goldens): STAGED (member-first lowered) =
`21 *D(member) / EB / 21 *D(pool) / 06 x / [3E y or 78] / CD ?SCCCM / <skip>`;
DIRECT (literal-first lowered) = `21 *D(member) / 11 *D(pool) / 06 x / [3E y or 78] /
CD ?SCCCM / <skip>`; MEMBER PAIR = `21 *D(first lowered) / E5 / 21 *D(second lowered)
/ D1 / 06 x / [3E y or 78] / CD ?SCCCM / <skip>`. Sizes: staged 65 (collapse) / 66
(pair) CODE; direct 64 / 65; member pair 66 / 67; fills 1C / 1D (staged), 1B / 1C
(direct), 1D / 1E (pair) -- each +1 byte under the unequal pair.

### Panel A — H-A-sw vs H-A-or vs H-A-refuse
- **H-A-sw** (the [C346] ORDER law REKEYS the template): `<`/`>=` lower in written
  order, `>`/`<=` swap, and the TEMPLATE follows the FIRST LOWERED operand --
  literal-first lowered becomes DIRECT, member-first lowered becomes STAGED; the
  positional immediates read `06 = first lowered, 3E = second lowered` (with [C342]
  collapse iff the two numbers are equal); BRANCH law: strict JNC `d2`, weak JC `da`.
- **H-A-or** (WRITTEN orientation keeps its template): member-written-left is always
  STAGED, literal-written-left always DIRECT, positionals written-left/written-right;
  the swap would transfer nothing to the literal family.
- **H-A-refuse**: DR refuses some or all rows (a boundary like [C332]) -- then those
  rows are dr-refuses and MY refusal stands, no arm.
- G1/G2/G7/G8 are COINCIDENT rows (no swap under either law): both hypotheses predict
  identical bytes -- G1/G7 STAGED `06 03 / 78` CODE 65 DATA 000F fill->001C (collapse
  per [C342]); G2/G8 DIRECT `06 03 / 78` CODE 64 DATA 000F fill->001B. The skip byte
  alone separates the relations: G1/G3 d2... (G1 d2, G2 d2, G7 da, G8 da).
- G3 `rec.na > 'AB'` -- H-A-sw: DIRECT `21 *D(0004 na) / 11 *D(0000 'AB') / 06 02 /
  3E 03`, d2, CODE 65, DATA 000E, fill->001C. H-A-or: STAGED `21 *D(0004) / EB /
  21 *D(0000) / 06 03 / 3E 02`, d2, CODE 66, fill->001D. The EB-vs-11 byte at 0009 and
  the immediate pair at 000D..0011 decide.
- G4 `'AB' > rec.na` -- H-A-sw: STAGED (swap lowers na first) `06 03 / 3E 02`, d2,
  CODE 66, fill->001D. H-A-or: DIRECT `06 02 / 3E 03`, d2, CODE 65, fill->001C.
- G5 `rec.na <= 'ABCD'` -- H-A-sw: DIRECT (swap lowers literal first) `06 04 / 3E 03`,
  da, CODE 65, DATA 0010, fill->001C. H-A-or: STAGED `06 03 / 3E 04`, da, CODE 66,
  fill->001D. [C345] TRANSFER: the pool holds 'ABCD' whole -- a TRUNCATED pool literal,
  a min/max length reading or a refusal falsifies both template hypotheses for the
  over-extent spelling and becomes a named remainder.
- G6 `'ABCD' <= rec.na` -- H-A-sw: STAGED `06 03 / 3E 04`, da, CODE 66, fill->001D.
  H-A-or: DIRECT `06 04 / 3E 03`, da, CODE 65, fill->001C.
- Falsifiers: any refusal row -> H-A-refuse (that row); any swap row whose template
  follows the WRITTEN side -> H-A-sw falsified for that relation; any swap row whose
  template follows the LOWERED side -> H-A-or falsified; equal attributes NOT collapsing
  in an accepted row -> [C342] has a relation exception (new law); skip byte C2/CA or an
  extra branch -> the BRANCH law does not transfer.

### Panel B — H-B-invis vs H-B-gate / H-B-mixed
- **H-B-invis** ([C344] transfers to the relation arm): every H row's object EQUALS its
  law-constructed qualified twin byte-for-byte EXCEPT the packed module-name fields and
  the checksum. Twins: H1 == golden F1 (`na < rec.nb` written, collapse, d2);
  H2 == the swapped-collapse twin (`> ' swaps: nb@0005 loaded FIRST, na@0002
  second, `06 03 / 78`, d2, CODE 66, fill->001D); H3 == golden F3
  (swap, collapse, da); **H4 `nb >= na` == golden F3 TOO** -- written-order `>=` lowers
  nb-first, the SAME lowered pair as F3's `<=` swap: two different written spellings,
  ONE object (a strong ORDER-law test); H5 == golden F2 (swap, `06 02 / 3E 03`, d2,
  CODE 67); H6 == the I5 prediction (swap, na first, `06 03 / 3E 02`, da, CODE 67).
- **H-B-gate**: DR refuses SOME bare spellings inside relations (the [C346] arm was
  built strictly for a reason) -- each refusal a dr-refuses law; **H-B-mixed**: accepts
  with different bytes (e.g. refusal only when BOTH sides bare).
- Falsifiers for H-B-invis: any refusal, or any byte outside the name/checksum fields
  differing from the twin.

### Panel C — the arm-c transfer (primary: NO arm)
- Primary [PLAN]: DR accepts all six and every object EQUALS my BASELINE-MINE arm-c
  bytes: head at 0006 `21 *D(first lowered) / E5 / 21 *D(second lowered) / D1 /
  06 <first> / 3E <second> / CD ?SCCCM / <skip> fill->001E`, CODE 67, DATA 000C, no
  collapse at 3/2. Per row: I1 written (na@0002 first) `06 03 / 3E 02` d2; I2 written
  (s2@0008 first) `06 02 / 3E 03` d2; I3 swapped (na first) `06 03 / 3E 02` d2; I4
  swapped (s2 first) `06 02 / 3E 03` da; I5 swapped (na first) `06 03 / 3E 02` da;
  I6 written (na first) `06 03 / 3E 02` da.
- Falsifiers: any refusal (relation + unequal is DR's boundary in some cell), any
  collapse attempt, any min/max reading, a slot order not matching the lowered pair, or
  a skip byte off the BRANCH law. A deviation falsifies the transfer and becomes the
  new law; acceptance byte-equal needs NO arm.

### Panel D — H-D-inv / H-D-simpl / H-D-extra / H-D-refuse (NO De Morgan assumption)
- FIRST question is SYNTACTIC ACCEPTANCE: does DR compile `^( <string compare> )' at
  all (my baseline refuses all four by name; the numeric NegL bank [C143] never
  touches strings; P3 RESULTS s3 lists `^( )' as unmeasured in this family).
- **H-D-inv** (skip byte INVERTED on the un-negated head): J1 == golden E49B5 bytes
  (mm collapse, CA); J2 == golden F1 head with d2 inverted to da; J3 == golden E49C4
  (direct collapse, CA, CODE 64, DATA 000F, fill->001B); J4 == the I4 head with da
  inverted to d2 (swap, `06 02 / 3E 03`, CODE 67).
- **H-D-simpl** (operator rewritten to its complement `^=`, `>=`, `^=`, `>`): produces
  the SAME bytes as H-D-inv on ALL FOUR shapes -- the convergence is PRE-REGISTERED
  HERE and the two hypotheses are NON-SEPARABLE in this bank; no claim may distinguish
  them from these objects and RESULTS must say so.
- **H-D-extra**: extra branch/helper bytes (an inversion via CMA, an ORA, a second
  CALL) -- distinguishable: head length, CODE size or fill moves.
- **H-D-refuse**: DR refuses some rows -> dr-refuses laws, my refusal stays, no arm.

## Arm consequence preview (decided ONLY by RESULTS, never before)
- Panel C acceptance-equal-to-baseline: NO arm. Any accepted A/B/D row needs a NEW
  measured arm (my baseline refuses them). If Panel A lowers literal relations, the
  prescan DEMAND twins `is_test_left`/`is_test_right` must widen IN THE SAME COMMIT as
  the lowering (one predicate; [C152] invariant). dr-refuses rows are NEVER implemented.

## Evidence rules
Every difference classified `dr-refuses` / `my-gap` / `unmeasured` (PROTOCOL #3);
comparison is WHOLE-FILE byte-for-byte of the .REL (PROTOCOL #6); a missing object is
`[TBD]`, never a promoted rule (PROTOCOL #4). Byte tier only: NO `spec/RUNTIME.txt` row
comes from this round.
