# E2E-49/P1 — hypotheses and PREREGISTERED predictions (operand-inverted FIXED compares, E49A1..E49A4)

Written and committed **before** the DR oracle is invoked on any E49A probe, under
PROTOCOL.md Part 1 #1 (the committed blob, not a file mtime, proves ordering).
`RESULTS.md` §1 must be a prediction-vs-verdict table over exactly these rows; every MISS
stays in that table (PROTOCOL #2).

    probes written by spec/lab-evidence/e2e49-p1/mkprobes.py (CRLF + ^Z, [C193] (b),
      every emitted line <= 71 columns -- the measured law that killed P2d run 1)
    baseline of MY compiler recorded in BASELINE-MINE.txt at HEAD f1e863c (NO oracle call):
      all four shapes refuse with rc=2 through `imem_refuse "comparison"'.
    the commit that adds probes/E49A1..E49A4.PLI + mkprobes.py + this file +
      BASELINE-MINE.txt is the PREDICTION SHA (fill-in commit below names it; it is
      committed BEFORE any oracle invocation); `golden/e49p1' does not exist at that
      commit and the fill-in commit is still an ancestor of the run.

## What this round is

The operator-authorized campaign **E2E-49/P1 — CHARACTER FIXED compare, OPERAND
INVERSION**. E2E-48/P2e arm 4 measured `if 'AB' = rec.name then' — the LITERAL on the
left, a qualified level-numbered FIXED member on the right — as
`21 *D(member) / 11 *D(pool) / 06 02 / 3E 03 / CD ?SCCCM / C2 fill -> next`
([C330], `golden/e48p2e/E48E7/E48E7.REL` 0006, CODE 65, DATA 000B). [C330]'s own
"what this does NOT license" list, and RESULTS §3, name the shape this round asks:
**`?SCCCM` with the member on the LEFT — no object**.

The single existing sample is ambiguous, and that is exactly why the inversion matters.
In E48E7 the member was BOTH the right operand AND the internal cell, so three recorded
wordings coincide byte-for-byte and CANNOT be separated:

- [C191]'s register law "HL carries the RIGHT operand, DE the LEFT";
- [C326]'s restatement "LXI H carries the INTERNAL CELL regardless of side";
- the length polarity: [C330] read `06 02 / 3E 03` as the [C191]/[C197]
  "A is the destination/capacity (extent), B is the source length (literal)" POLARITY
  (class-based), but in the varying family [C191] measured the literal's length in B for
  a literal-LEFT helper (?SCCVM) and in A for a literal-RIGHT one (?SCVCM) — a POSITION
  reading that E48E7 also cannot separate (its literal is left, and A holds the extent).

This round writes the SAME compares with the operands swapped and lets DR say which
reading is law. Symmetry is NOT assumed (operator ruling): acceptance itself is an open
question — [C332] proved a DR language boundary EXISTS inside this operand class (the
truthiness of a VARYING member is refused with `BIT REQ'), so an unmeasured fixed-member
shape is entitled to be refused; nothing here presupposes the answer.

Scope (operator ruling, binding): **TEST conditions only; CHARACTER FIXED; NON-BASED,
level-numbered internal members.** STOREs, BASED members, member-vs-member compares,
literal-vs-literal fixed compares, truthiness of a fixed member, and `^( ... )`
composition stay OUT and keep refusing.

## Prior evidence this file was derived from (literal `.REL` bytes / ledger laws, never a `.PRN`)

- `golden/e48p2e/E48E7/E48E7.REL` ([C330]), re-read with `tools/reldump.py` at this
  session: 0006 `21` RELOC data 0x4 (member cell 0004) / 0009 `11` RELOC data 0x0 (pool
  'AB') / 000C `06 02` / 000E `3e 03` / 0010 `cd` EXT ?SCCCM / 0013 `c2` RELOC code 0x1c
  ([C309] skip to the NEXT statement, the put prologue at 001C); then-body 0016 `21 01 00 /
  22` RELOC data 0x9 (LXI H,1 / SHLD k); DATA 000B = 'AB'@0000, 'K='@0002, frame
  and the AUTOMATIC frame (name@0004, nxt@0007, k@0009 — [C314]'s pool-first layout).
- [C191] (spec/CLAIMS.md line 3736): the orientation law and the naming law "the helper
  name says what the LEFT is"; the XCHG clause — a member "needs XCHG only when it is the
  left operand" — was measured on the VARYING family, where the pool literal of a
  member-left compare loads through `21 *S(lit)` AFTER the XCHG (E48C9, [C318]:
  `21 *D(rec) / EB / 21 *S(lit) / 3E 03 / CD ?SCVCM / C2`). In E48E7 BOTH addresses are
  *D DATA relocs, so neither load is forced through HL and the XCHG question is open for
  the FIXED class.
- [C317]/[C318]/[C326]: member-vs-literal compares measured byte-exact in BOTH
  orientations and BOTH positions (store and TEST) for VARYING members — DR's language
  admits member operands on either side; nothing says the FIXED class follows.
- [C330] "Lowered" note: my arm-4 encoder `str_cmp_shape_fix` matches ONLY
  (`Lit`, `ImemF`); the `ImemF`-left pair falls through to `imem_refuse "comparison"`.
- [C309]: a no-else TEST fills its skip word with the address of the NEXT statement.
- [C072]: DR's `^=` skip byte is CA in every sampled family (a synthesis in arm 4's
  lowering; E48E7 measured C2 only).
- [C253]/[C258]: `name` and `rec.name` fold to ONE ident key and ONE cell; [C318]'s
  RETIRE corroboration (E46K3, `golden/e48p2retire/`) proved spelling-invariance for a
  VARYING member in TEST. The FIXED bare spelling has no compare object.
- [C191]'s E30T1 truncation witness (len 8 / cap 6, `?SMCVM`) is a STORE; NO object
  compares a fixed member against a literal LONGER than its extent — my `str_cmp_shape_fix`
  comment records DR's verdict there as [TBD].
- `probes/E48E7.PLI` is the template: `1 rec, 2 name char(3), 2 nxt fixed bin(15);
  dcl k fixed bin(15);` plus the `put list('K=', k);` tail whose bytes are measured in
  E48E7 itself — kept in every probe of this bank so the skip fill and the DATA layout
  stay comparable across objects.

## Predictions

| id | prediction (derived, not guessed) |
|---|---|
| P-A1 (member-left `if rec.name = 'AB' then`) | **ACCEPTS** — the operand CLASS is admitted in this very position by [C330] (the identical pair with sides swapped), and the varying family is measured in BOTH orientations ([C317]/[C318]/[C326]). **PRIMARY byte prediction, Form II** ([C191]'s address law with [C330]'s class polarity): `21 *D(pool 0000) / 11 *D(member 0004) / 06 02 / 3E 03 / CD ?SCCCM / C2 fill -> 001C` — HL takes the RIGHT operand (now the literal), DE the member, the literal's length stays in B and the extent stays in A, because ONE helper (the name carries no V, so no orientation twin is measured) keeps ONE register polarity. CODE 65, DATA 000B, layout [C314] unchanged; relocations swap order (data 0x0 then data 0x4 at 0007/000A). **Form I** (pure symmetry): bytes IDENTICAL to E48E7 `21 *D(member) / 11 *D(pool) / 06 02 / 3E 03` — falsifies [C191]'s address law for the FIXED class and makes [C326]'s "HL is the internal cell" wording literal law. **Form III** (position law for the lengths too, by strict ?SCVCM/?SCCVM analogy): `21 *D(pool) / 11 *D(member) / 06 03 / 3E 02` — literal's length moves to A with its side; falsifies [C330]'s capacity-in-A reading. Other falsifiers: a DIFFERENT helper name (then [C191]'s "name says what the LEFT is" extends to the fixed pair and ?SCCCM is a literal-left-only name); `EB` XCHG anywhere (member-left needs staging even with *D operands — new law); a REFUSAL (would make my named refusal `dr-refuses` law, as [C332] did for truthiness). |
| P-A2 (same inverted compare, BARE spelling `if name = 'AB' then`) | **ACCEPTS**, bytes **identical to P-A1's winner** ([C253]/[C258] one cell; [C318]'s E46K3 proved spelling-invariance for a VARYING member in TEST). Falsifier: a refusal (would make the qualification part of DR's compare AUTHORIZATION for the fixed class — a language boundary, `dr-refuses`) or bytes different from E49A1 (would make the spelling select the encoding). |
| P-A3 (`if rec.name ^= 'AB' then`) | **ACCEPTS**, head identical to P-A1's winner, skip byte **CA** — [C072] "DR's ^= skip byte is CA everywhere"; this converts arm 4's recorded [C072] SYNTHESIS into a measurement. Falsifier: `C2` (would mean `^=` is DROPPED — a DR defect to record, not to copy); any other skip byte; a refusal. |
| P-A4 (over-extent `if rec.name = 'ABCD' then`) | **VERDICT-UNKNOWN, leaning ACCEPTS**: a compare READS both operands, the lengths travel as separate immediates (B and A in E48E7), nothing writes the member, and [C191]'s store witness E30T1 accepts len 8 > cap 6. If accepted, the form is P-A1's winner with `06 04` (literal length 4; under Form III the pair would be `06 03 / 3E 04`); DATA = 'ABCD'@0000, 'K='@0004, frame name@0006, k@000B, size 000D ([C314]). Falsifier: a PASS-2 refusal (`dr-refuses`: over-extent literals are illegal in fixed compares — then my ungated `str_cmp_shape_fix` comment's [TBD] is answered by the negative and the STORE over-extent question stays open); an accept with the literal TRUNCATED in the pool (would be a DATA-image law, new). |

P-A2/P-A3/P-A4 conditions are stated RELATIVE to P-A1's winner: whichever orientation
law DR picks, the same law must govern the three dependents or the report says so.

## What this round does NOT claim

- **Nothing about a fixed member in a STORE** (`s = rec.name`, `rec.name = 'AB'` as an
  assignment) — [C330] §3; the store routes keep refusing.
- **Nothing about BASED members** in any position, **member-vs-member** compares,
  **literal-vs-literal fixed** compares, or the **truthiness** of a fixed member.
- **Nothing about `^( ... )` composition** over a compare — out of scope, unmeasured.
- **Over-extent is sampled ONLY in the member-left TEST compare** (P-A4); the over-extent
  INITIAL/STORE stay excluded (the same design exclusion as P2e, RESULTS §3).
- **No runtime semantics**: judged on `.REL` bytes under `$L$D` only, so **no
  `spec/RUNTIME.txt` row may come from this round**.
- P-A2's invariance and P-A3's CA byte are EXTRAPOLATIONS from the varying family and
  [C072]; a MISS there is a result and stays in §1 (PROTOCOL #2).

## Command (for the session that runs it — NOT run here)

    PLI_SRC=probes python3 oracle/batch.py E49A1 E49A2 E49A3 E49A4 \
        --tag e49p1 --switches '$L$D'

`golden/e49p1` must not exist before this call (verified at pre-registration time: it
does not; `golden/probe49` is an unrelated old tag).  Never pass `--reuse` into an
existing tag.  Then write `RESULTS.md` §1 as a prediction-vs-verdict table over
P-A1..P-A4, re-read every accepted `.REL` with `tools/reldump.py` /
`spec/lab-evidence/e2e42-p2b/chaindump.py` (never a `.PRN` size, PROTOCOL #6), and
commit goldens + report TOGETHER.  Lowering may only touch what §2 measures.

## Prediction-SHA fill-in

PREDICTION SHA: `<filled by the child commit, before any oracle call>` — the commit that
added probes/E49A1..E49A4.PLI + mkprobes.py + this file + BASELINE-MINE.txt
(`git log --format=%h -- probes/E49A1.PLI | tail -1`); the fill-in commit naming it is
this commit's child and is an ancestor of the oracle run.
