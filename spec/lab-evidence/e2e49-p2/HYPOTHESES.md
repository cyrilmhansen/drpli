# E2E-49/P2 — hypotheses and PREREGISTERED predictions (MEMBER-vs-MEMBER FIXED compares in TEST, E49B1..E49B5)

Written and committed **before** the DR oracle is invoked on any E49B probe, under
PROTOCOL.md Part 1 #1 (the committed blob, not a file mtime, proves ordering).
`RESULTS.md` §1 must be a prediction-vs-verdict table over exactly these rows; every
MISS stays in that table (PROTOCOL #2).

    probes written by spec/lab-evidence/e2e49-p2/mkprobes.py (CRLF + ^Z, [C193] (b),
      every emitted line <= 71 columns -- the measured law that killed P2d run 1)
    baseline of MY compiler recorded in BASELINE-MINE.txt at HEAD 7fa763b (NO oracle
      call): all five shapes refuse with rc=2 through `imem_refuse "comparison"'.
    the commit that adds probes/E49B1..E49B5.PLI + mkprobes.py + this file +
      BASELINE-MINE.txt is the PREDICTION SHA (fill-in commit below names it; it is
      committed BEFORE any oracle invocation); `golden/e49p2' does not exist at that
      commit and the fill-in commit is still an ancestor of the run.

## What this round is

The operator-authorized campaign **E2E-49/P2 — CHARACTER FIXED compare, MEMBER vs
MEMBER, in TEST**. Both prior rounds of the `?SCCCM` family explicitly named this shape
as having NO object and kept it refusing: [C330] "what this does NOT license" and
`golden/e48p2e/E48E7` RESULTS §3; [C333]/`golden/e49p1` RESULTS §3; my `imem_refuse
"comparison"` ADDENDA. Every fixed compare object measured so far — E48E7 (literal
left), E49A1/A2/A3/A4 (member left) — has exactly ONE internal member and ONE POOLED
LITERAL. This round puts TWO internal, level-numbered, non-BASED, QUALIFIED FIXED
CHARACTER members on the two sides of the relation and lets DR say what the head is.

## Why the recorded laws CANNOT predict this head (the competing readings)

Two laws were each measured only while ONE side was a member, and with two members they
split into two different byte sequences:

- **[C333] staging law** (from E49A1/A2): the member is loaded FIRST into HL
  (`21 *D(member cell)`) and, when it is the LEFT operand, staged through `EB` (XCHG)
  into DE before the pool literal is loaded into HL. Its clause "a member needs XCHG
  only when it is the left operand" was measured for the FIXED class with *D operands.
- **[C191] final-register law** (restated by [C326]): HL ENDS on the RIGHT operand, DE
  on the LEFT — satisfied by every object in the family.
- **[E29C6] varying cell-vs-cell precedent** (`str_cmp_shape_vv`, `Imm/Imm`): when BOTH
  addresses are directly materializable, DR loads the RIGHT operand into HL FIRST and
  materializes the LEFT straight into DE: `21 *D(right) / 11 *D(left)`, NO XCHG.
- **[C330]/[C334] length law**: the two length immediates are POSITIONAL — `MVI B`
  carries the LEFT operand's attribute, `MVI A` the RIGHT's (measured on five
  member-vs-literal objects; NEVER on a pair where both attributes are declared extents).

With operands (member, member) both sides are `*D`-addressable cells, so:

| form | head bytes (E49B1, na@0002 LEFT, nb@0005 RIGHT) | obeys |
|---|---|---|
| **Form S** (direct; right-first) | `21 *D(0005) / 11 *D(0002) / 06 03 / 3E 03 / CD ?SCCCM` | [C191] final law, [E29C6] both-materializable precedent; the member-first reading picks the RIGHT member |
| **Form M** (staged; left-first mirror of E49A1) | `21 *D(0002) / EB / 21 *D(0005) / 06 03 / 3E 03 / CD ?SCCCM` | [C191] final law AND the literal extrapolation of [C333] "a member needs XCHG when it is the LEFT operand" (here the right side is ALSO a member) |

The equal-length inversion pair E49B1/E49B2 separates them with ONE byte (`EB`) and the
relocation slot order. This is NOT assumed symmetry: acceptance itself is open —
[C332] proved DR draws language boundaries inside this operand class (the VARYING
member's truthiness is refused with `BIT REQ'), so **H-R (refusal)** is a first-class
hypothesis, as in P1.

## Prior evidence this file was derived from (literal `.REL` bytes / ledger laws, never a `.PRN`)

- `golden/e49p1/E49A1/E49A1.REL` ([C333]), re-read with `tools/reldump.py` at this
  session: 0006 `21` RELOC data 0x4 / 0009 `eb` / 000A `21` RELOC data 0x0 / 000D `06 03`
  / 000F `3e 02` / 0011 `cd` EXT `?SCCCM` / 0014 `c2` RELOC code 0x1d; then-body 0016
  `21 01 00 / 22` RELOC data 0x9; CODE 66, DATA 000B.
- `golden/e48p2e/E48E7/E48E7.REL` ([C330]): 0006 `21` RELOC data 0x4 (member, RIGHT) /
  0009 `11` RELOC data 0x0 (pool literal, LEFT) / 000C `06 02` / 000E `3e 03` / 0010
  `cd ?SCCCM` / 0013 `c2 -> 001c`; CODE 65 — the DIRECT head, member loaded first into
  HL because the member WAS the right operand.
- [C334]: positional lengths, five objects; [C318]/[C191]: the varying family obeys the
  same positional law.
- [C141]/[E29C6] (`str_cmp_shape_vv` comment): in the varying VV family, both-immediate
  pairs take `21 *D(right) / 11 *D(left)` (E29C6), one-load pairs stage through XCHG or
  the stack — the FIXED family has never shown its choice for a two-member pair.
- [C309]: a no-else TEST fills its skip word with the address of the NEXT statement
  (in this bank: the `put` prologue). [C072]: `^=` skip byte CA in every sampled family;
  [C333] measured CA in the ?SCCCM family ONLY member-vs-literal (E49A3).
- [C314]: pool-first DATA layout, then the AUTOMATIC frame in DECLARATION order
  (E49A1: pool @0000, name@0004, nxt@0007, k@0009; E49A4 with a 4-char literal:
  pool @0000..0003, name@0006, nxt@0009, k@000B).
- `probes/E49A1.PLI` is the template; this bank keeps the SAME tail
  (`put list('K=', k);`) so the skip fill and layout stay comparable, and adds a
  three-member record: `1 rec, 2 na char(3), 2 nb char(3), 2 s2 char(2); dcl k fixed
  bin(15);` — every probe shares this DECL so DATA is the same in all five objects:
  `'K='@0000, na@0002, nb@0005, s2@0008, k@000A, DATA size 000C.

## Competing hypotheses

- **H-R (refusal).** DR refuses member-vs-member fixed compares in TEST (a PASS-2
  error, no `.REL` — the [C332] pattern). Then each difference is `dr-refuses` law and
  NO lowering happens. Considered plausible enough to be first-class because [C332]
  proved the class has boundaries; considered LESS likely for a compare because member-
  vs-literal is accepted on BOTH sides ([C330]/[C333]) and member-vs-literal AND
  cell-vs-cell varying compares ([C317]/[C318]/[E29C6]) exist.
- **H-S (direct head, Form S).** `21 *D(RIGHT member) / 11 *D(LEFT member) / 06 <left
  extent> / 3E <right extent> / CD ?SCCCM / C2|CA fill -> next` — 16-byte head, CODE 65.
  PRIMARY for the head: it is [C191]'s final law plus the ONLY both-immediate witness
  that exists anywhere ([E29C6]) plus the smallest encoding; the XCHG in E49A1 exists
  because LXI D cannot follow an HL load whose value must survive — impossible here,
  since EITHER member address can be materialized directly into DE.
- **H-M (staged head, Form M).** `21 *D(LEFT member) / EB / 21 *D(RIGHT member) / 06
  <left extent> / 3E <right extent> / CD ?SCCCM / skip` — 17-byte head, CODE 66; the
  literal extrapolation of [C333]'s "member-left stages" clause.
- Shared sub-hypotheses (either form): the helper stays `?SCCCM` (the CC pair names two
  FIXED-class operands, carries no orientation — [C333] §2.3); the lengths follow
  [C334]'s positional law; the skip bytes are C2 (`=`) / CA (`^=`) with fill = NEXT
  statement ([C309]); both addresses are `21`/`11` with `*D` DATA relocations to the
  member cells (no LHLD/PUSH form; [C141] parking is for LOAD-able operands, the fixed
  family has never used it).

## Predictions (exact, per row; forms of B2..B5 RELATIVE to B1's winner)

Common frame for EVERY probe (shared DECL, no compare literals pooled):
DATA 000C = `'K='@0000, na@0002..0004, nb@0005..0007, s2@0008..0009, k@000A..000B`;
entry 0000 `01 00 02 cd *CODE ?START`; then-body `21 01 00 / 22 *D(000A)`; tail `put`
prologue 37 bytes ([C314]/[E49A1] verbatim mechanism).

| id | source | prediction | falsifier |
|---|---|---|---|
| P-B1 | `if rec.na = rec.nb then k = 1;` | **ACCEPTS** (primary: H-S) head `21 *D(0005) / 11 *D(0002) / 06 03 / 3E 03 / CD ?SCCCM / C2 fill -> 001C`, CODE 65; competing H-M head `21 *D(0002) / EB / 21 *D(0005) / 06 03 / 3E 03 / CD ?SCCCM / C2 -> 001D`, CODE 66 | H-R (PASS-2 error, no `.REL`) makes it `dr-refuses`; a DIFFERENT helper name breaks [C333] §2.3 for member pairs; any non-`*D` addressing (LHLD/PUSH/POP) is a new law; the equal lengths CANNOT test the length law here (both immediates 03 either way) |
| P-B2 | `if rec.nb = rec.na then k = 1;` | ACCEPTS, P-B1's winner with the two member-cell relocations+immediates SWAPPED in their slots (same CODE size, same length pair `06 03 / 3E 03`) | byte-IDENTICAL relocations to P-B1 (would mean the encoding ignores the written side and [C334] does not transfer); refusal while B1 accepted (orientation-specific boundary — new law) |
| P-B3 | `if rec.na = rec.s2 then k = 1;` | ACCEPTS, P-B1's winner with the RIGHT member = s2 cell `*D(0008)` and lengths POSITIONAL: `06 03 / 3E 02` | `06 02 / 3E 03` (side-inverted); `06 02 / 3E 02` (MIN) or `06 03 / 3E 03` (MAX) — a class/keyed law re-opening [C330]'s falsified polarity; refusal of UNEQUAL-extent member pairs specifically (would be a new `dr-refuses` boundary) |
| P-B4 | `if rec.s2 = rec.na then k = 1;` | ACCEPTS, P-B1's winner with LEFT = s2 `*D(0008)`, RIGHT = na `*D(0002)` and lengths `06 02 / 3E 03` — the B3 pair SWAPPED with the operands | lengths IDENTICAL to P-B3 (`06 03 / 3E 02` or min/max) — that would show the pair is keyed by CLASS/size, not by position, falsifying [C334] for member-member |
| P-B5 | `if rec.na ^= rec.nb then k = 1;` | ACCEPTS, P-B1's winner head verbatim with skip byte **CA** and fill = NEXT statement (the `put` address: 001C under H-S, 001D under H-M) | skip `C2` (`^=` dropped — a DR defect to record, not to copy); any other skip byte; refusal while B1 accepted |

P-B2..P-B5 are stated RELATIVE to P-B1's winner: whichever head law DR picks, the same
law must govern the four dependents or the report says so.

## What this round does NOT claim

- **Nothing about a fixed member in a STORE** (either orientation) — [C333] §3.
- **Nothing about literal-vs-literal** fixed compares, **BASED** members in conditions,
  **truthiness** of a fixed member, or `^( ... )` composition — all stay out (operator
  ruling) and keep refusing.
- **Nothing about BARE spellings**: every probe writes BOTH members qualified; the P1
  asymmetry (bare admitted LEFT only) says nothing about member-vs-member, and this
  round does not sample it. If H-S wins with, e.g., left-in-DE, bare-vs-qualified
  remains unmeasured for BOTH slots.
- **Nothing about over-extent** here: the unequal extents of B3/B4 are DECLARED-member
  vs DECLARED-member, not a literal longer than an extent.
- **No runtime semantics**: judged on `.REL` bytes under `$L$D` only, so **no
  `spec/RUNTIME.txt` row may come from this round**. What `?SCCCM` DOES with unequal
  B/A at runtime is not claimed.

## Command (for the session that runs it — NOT run here)

    PLI_SRC=probes python3 oracle/batch.py E49B1 E49B2 E49B3 E49B4 E49B5 \
        --tag e49p2 --switches '$L$D'

`golden/e49p2` must not exist before this call (verified at pre-registration time: it
does not). Never pass `--reuse` into an existing tag. Then write `RESULTS.md` §1 as a
prediction-vs-verdict table over P-B1..P-B5, re-read every accepted `.REL` with
`tools/reldump.py` / `spec/lab-evidence/e2e42-p2b/chaindump.py` (never a `.PRN` size,
PROTOCOL #6), and commit goldens + report TOGETHER. Lowering may only touch what §2
measures.

## Prediction-SHA fill-in

PREDICTION SHA: **3bd9417** — the commit that
added probes/E49B1..E49B5.PLI + mkprobes.py + this file + BASELINE-MINE.txt
(`git log --format=%h -- probes/E49B1.PLI | tail -1`); the fill-in commit naming it is
this commit's child and is an ancestor of the oracle run.
