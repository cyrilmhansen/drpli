# E2E-48/P2d — hypotheses and PREREGISTERED predictions (round 4, E48D1..E48D10)

Written and committed **before** the DR oracle is invoked on any E48D probe, under
PROTOCOL.md Part 1 #1 (the committed blob, not a file mtime, proves ordering).
`RESULTS.md` §1 must be a prediction-vs-verdict table over exactly these rows; every MISS
stays in that table (PROTOCOL #2).

    probes written by spec/lab-evidence/e2e48-p2d/mkprobes.py (CRLF, [C193] (b))
    baseline of MY compiler recorded in BASELINE-MINE.txt at HEAD ef0a198 (no oracle call)
    the commit that adds probes/E48D*.PLI + mkprobes.py + this file = the prediction SHA,
      recorded here when known: <fill in at oracle time from `git log --format=%h -- probes/E48D1.PLI`>

## What this round is

Round 3 (E48C) and the RETIRE round closed [C317]-[C320]. What is left open in the ledger is
the **section 3 list** of `spec/lab-evidence/e2e48-p2c/RESULTS.md` — shapes my compiler refuses
BY NAME because no DR object was said to measure them. Writing the bank re-read the artifacts
and found that **three of those "no golden exists" claims are false** (see "Prior evidence
re-read" below): the objects are already committed in this tree. So this round does two things:

1. measures the genuinely-unmeasured shapes (D4-D10), and
2. gives D1-D3 a **fresh per-instruction witness** for a route whose DR object already exists,
   so a lowering can be verified against a probe of its own rather than by borrowing a
   whole-program object.

## Prior DR evidence re-read for this file (literal `.REL` bytes, never a `.PRN`)

- `golden/e42p1c/E46F5/E46F5.REL` — 384 bytes, CODE 68, DATA abs 18, DEF-DATA-SIZE **0012**,
  DEF-COMMON-SIZE 0026 `OUTF`. CODE 0006: `21 *D(0000) / CD ?SLVTS / 40 / C5 / 33 / 21 0E50 /
  E5 / 21 0000 / E5 E5 E5 E5 E5 / 21 *C(0000) / CD ?OIOOP`. DATA 0000..000E =
  `02 41 42 20 x11` (the static varying cell IN PLACE) and 000F = `58` (the pooled `'X'`).
  Its `.PRN` prints NO ERROR(S) IN PASS 1 and PASS 2. **So DR ACCEPTS a STATIC CHARACTER
  VARYING as an OPEN TITLE operand, and §3's "no golden puts a static varying in a TITLE" is
  FALSE.**
- `golden/e42p1c/E46F1/E46F1.REL` (AUTOMATIC varying, output title) has the **same 68 CODE bytes
  and the same 18-byte DATA total**; the difference is only WHICH address the two `LXI H,*D`
  operands name (title `*D(0001)` and pool `*D(0000)` for the automatic twin, `*D(0000)` and
  `*D(000F)` for the static). CODE-segment comparison, not file offsets: `cmp -l` on the two
  files reports 208 bytes because the module name is carried in the name records.
- `golden/e42p1c/E46F3/E46F3.REL` (automatic varying, INPUT title): same prologue, option word
  **0E90**; CODE 71, DATA 17.
- `golden/e42p1c/E46F2/E46F2.REL` (automatic FIXED `char(8)` title): `21 *D(0001) / 3E 08 /
  CD ?SLCTS`, option word 0E50, CODE 70, DATA **11** — the DECLARED length, not the literal's
  ([C174]/[C288]).
- `golden/first8080u/EXPR2/EXPR2.REL` — DATA **000F = 00** then **0010..0019 = 20 x10**, i.e.
  `(token character(10), ...) varying static initial('')` is a **zero length byte plus the
  declared extent blank-padded, in place**; 001A = `00` then blanks for `line character(80)`.
  **So the EMPTY-literal static varying cell layout is already measured by a committed DR
  object**; §3's "zero-cell layout unmeasured" is FALSE for the VARYING case.
- `golden/first8080u/CREATE/CREATE.REL` 008F and `golden/e48p2c/E48C8/E48C8.REL` are the
  class laws of [C317]/[C319].

## Predictions

| id | prediction (derived, not guessed) |
|---|---|
| P-D1 | **ACCEPTS.** Title head `21 *D(0000) / CD ?SLVTS / 40 / C5 / 33`, option word **0E50**, DATA `02 41 42 20 x11` at 0000 + pooled `58` at 000F, DEF-DATA-SIZE **0012** — i.e. DR's existing E46F5 object reproduced with the D1 module name; the storage class changes NO code byte except the two operand addresses. |
| P-D2 | **ACCEPTS.** Same `?SLVTS` prologue on the input side with the STATIC cell address `*D(0000)` and option word **0E90** ([C288] orthogonality extended to a static operand). A refusal here would mean the INPUT route is not class-invariant, which would be a DR rule, not a gap. |
| P-D3 | **ACCEPTS.** Fixed route unchanged: `21 *D(cell) / 3E 08 / CD ?SLCTS` (DECLARED length 8 even though the initial is 2 chars), cell `41 42 20 x6` IN PLACE at 0000, pool `'X'` above it, DEF-DATA-SIZE **11** by [C314]'s full-extent law + E46F2's pool arithmetic. My compiler ALREADY compiles this (BASELINE-MINE), so this probe primarily tests whether my existing bytes are right. |
| P-D4 | **ACCEPTS.** Cell = `00` + ten `20` = **11 bytes in place at 0000**, NOT pooled, NOT deduped; the `put list('S=', s)` item reads it by `?SLVTS` (length from the cell = 0, so nothing is printed for `s`). Derived from EXPR2's DATA 000F. A cell of `00` ALONE (1 byte) would falsify the "extent blank-padded regardless of the literal" law for the empty case. |
| P-D5 | **ACCEPTS.** Fixed empty cell = five `20` bytes in place (extent blank-padded, [C314]); the corpus gives NO empty-FIXED witness, so this is the genuinely new half of the law. |
| P-D6 | **ACCEPTS.** A store into a static CHARACTER cell copies IN PLACE; the discriminating question is the POOL: if DR pools `'CD'` the DATA size grows by 3 (2 chars + pad) over the declaration-only size, if it does not, the size stays at the static extent. Prediction: **pools it** (every measured DR literal source lives in the pool: [C310]'s `21 *S(lit)` sites), so DATA grows; the route itself is the ordinary fixed-char move. |
| P-D7 | **ACCEPTS.** The LEADING LENGTH BYTE is rewritten (cell `03 43 44 45 20 x6`) and the source literal is pooled — i.e. [C319]'s cell is a real varying descriptor, not a constant. |
| P-D8 | **ACCEPTS.** Both sites use the [C143] biased ladder with the SAME threshold as the TEST route: `k = 2` -> `LHLD k / DCX H / DCX H / MOV A,H / ORA L`, `k = 3` -> the same with three `DCX H` (E48A13 measured `= 3` as DCX x3 in TEST; E48A12 measured `= 4` as `LXI B,FFFC`), then `D6 01 / 9F / 32 <cell>`. If the STORE route instead uses `LXI B` for 2 and 3, the threshold is route-specific and [C143]'s wording must be narrowed. |
| P-D9 | **ACCEPTS.** `3A *D(b) / 06 01 / CD ?QB08C / CD ?PNBOP` for the bit item FOLLOWED by the literal item's own chain and exactly ONE `?QIOOP` — [C313]'s one-tail-per-item law. A refusal would make the non-final bit item `dr-refuses` and my named refusal correct. |
| P-D10 | **ACCEPTS.** Literal-left orientation in TEST takes the **SCCVM** head of [C317] §2.3 — `21 *D(member) / 11 *S(lit) / 06 len / CD ?SCCVM` + `C2 00 00` with the no-else skip to the NEXT statement ([C309]) — 14 bytes + the 3-word fill. If DR instead emits the member-LEFT SCVCM head, the orientation law is position-dependent and §2.4 must be re-worded. |

## What this round does NOT claim

- Nothing about a **BASED** member in a condition store (still no witness anywhere) — D10 is an
  AUTOMATIC record. It stays a named refusal until a probe measures it.
- Nothing about `put file(f) list(b)` (a bit item behind a file attach) — that needs an OPEN
  context and its own probe; left for round 5.
- No runtime claim: every probe here is judged on `.REL` bytes only, so no `spec/RUNTIME.txt`
  rows may be added from this round.
- P-D6/P-D7's pool arithmetic is the WEAKEST derivation in the bank (inferred from the literal
  route, not from a static-destination object). A MISS there is the expected outcome, not a
  surprise, and stays in the table.

## Command (for the session that runs it — NOT run here)

    PLI_SRC=probes python3 oracle/batch.py E48D1 E48D2 E48D3 E48D4 E48D5 E48D6 E48D7 E48D8 \
        E48D9 E48D10 --tag e48p2d --switches '$L$D'

Expected first output: the batch's own ok/refused tally. Then write `RESULTS.md` §1 as a
prediction-vs-verdict table over P-D1..P-D10, re-read every accepted `.REL` with
`tools/reldump.py` / `spec/lab-evidence/e2e42-p2b/chaindump.py`, and commit goldens + report
TOGETHER. Lowering may only touch what §2 measures.
