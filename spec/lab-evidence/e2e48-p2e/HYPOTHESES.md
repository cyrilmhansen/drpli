# E2E-48/P2e — hypotheses and PREREGISTERED predictions (round 5, E48E1..E48E8)

Written and committed **before** the DR oracle is invoked on any E48E probe, under
PROTOCOL.md Part 1 #1 (the committed blob, not a file mtime, proves ordering).
`RESULTS.md` §1 must be a prediction-vs-verdict table over exactly these rows; every MISS
stays in that table (PROTOCOL #2).

    probes written by spec/lab-evidence/e2e48-p2e/mkprobes.py (CRLF, [C193] (b),
      every emitted line <= 71 columns -- the measured law that killed P2d run 1)
    baseline of MY compiler recorded in BASELINE-MINE.txt at HEAD dcc874d (NO oracle call)
    the commit that adds probes/E48E*.PLI + mkprobes.py + this file + BASELINE-MINE.txt is
      the PREDICTION SHA, recorded here when known: (fill in at commit time, see below),
      committed BEFORE any oracle invocation; `golden/e48p2e' does not exist at that commit.

## What this round is

E2E-48/P2d is closed (10/10 probes byte-exact and registered; gate 1120/0). What it left
open is the **section 3 list** of `spec/lab-evidence/e2e48-p2d/RESULTS.md`:

- `k = 1` and negative `c` in the store ladder ([C324]'s own [TBD]);
- `^(cond)` in a STORE beyond `^(k = 0)` ([C310]);
- a BIT(1) item behind a file attach (`put file(f) list(b, ...)`);
- truthiness of a member; member-vs-member; a FIXED member in a compare;
- (from `e2e48-p1` RESULTS §3.2) `= '0'b' as a materialised VALUE.

Two further §3 items — store/INITIAL **longer than the extent**, and a **BASED** member in a
condition STORE — are deliberately EXCLUDED from this round and deferred to a later one, for a
mechanical reason recorded in "What this round does NOT claim" below. This round is operator
choice **(D)** of the P2d closing checkpoint: a byte round for still-unmeasured bit/char edges.

Of the eight predictions, SIX are derived from committed bytes and TWO (P-E6, P-E7) are
**verdict-unknown**: they ask whether DR accepts the shape AT ALL. A refusal there is a
classification result (`dr-refuses`, which would make my named refusal correct law), not a
failed experiment — PROTOCOL Part 1 #3/#4.

## Prior evidence this file was derived from (literal `.REL` bytes / ledger laws, never a `.PRN`)

- `golden/e48p2db/E48D8/E48D8.REL` 0006 and 0013 ([C324]): `2A *D(k) / 2B [x2] / 7C / B5 /
  D6 01 / 9F / 32 *D(b)` and the same with `2B x3` — the ladder, its `|c| <= 3` threshold and
  the [C095] tail.  Sizes: the whole materialiser is 9 + |c| bytes for |c| in {2,3}.
- `golden/e48p1/E48A12/E48A12.REL` 0027 (`= 4`) and the [C143] pair at `E48A7` 003A (`= 5`):
  `2A *D(k) / 11 4C FF / 09 / 7C / B5 / D6 01 / 9F / 32` — the LXI-B form where the immediate is
  the TWO'S COMPLEMENT of the constant (`-5 -> FFFB`, `-4 -> FFFC`).  This is the ONLY witness
  for how the ladder encodes a large/negative offset, and every recorded value is NEGATIVE
  because every measured constant is POSITIVE.
- `golden/e48p1/E48A11` vs `E48A8` ([C310], RESULTS §1 P11): `^(k = 0)` as a value emits
  byte-IDENTICAL bytes to `k ^= 0` — `LXI H,k / MOV A,M / INX H / ORA M / C6 FF / 9F`.  No CMA
  (0x2F) appears in any of the 24 P1 objects; `^` retargets the TAIL, never the head.
- `golden/e48p1/E48A10` 0006 ([C310]): `= '1'b' as a value is `3A *D(b) / E6 80 / D6 80 /
  D6 01 / 9F / 32 *D(f)` — the [C112] ladder's result feeding the flag trick.  The `= '0'b'
  VALUE has no object; the `= '0'b' TEST exists only in corpus sources (`e13src/E11D:5`,
  `E20B:5`, `E20E:11`, `E21A:6,9`), which are DR's own programs and CANNOT be witnesses
  (`tools/coverage_check.py` refuses corpus objects as probe evidence) — so they license nothing
  here except the expectation that the form is legal PL/I.
- `golden/e48p2db/E48D10/E48D10.REL` 0013 ([C326]): literal-left TEST on an INTERNAL VARYING
  member = `21 *D(member) / 11 *D(pool lit) / 06 len / CD ?SCCVM / C2 fill -> next stmt`, the
  [C309] skip.  `golden/e48p2c/E48C9` ([C318]) is member-LEFT with `?SCVCM` + `3E len`.
- [C191]: the compare-helper law — the helper NAME says what the LEFT operand is
  (`?SCVCM` = varying/member left, length in A; `?SCCVM` = literal left, length in B;
  `?SCVVM` = varying-vs-varying, no length byte).  **Every measured right operand is VARYING or
  a literal; no object compares a FIXED character operand through any of the three.**
- [C297]: DR ACCEPTS a level-numbered FIXED CHARACTER member as an operand on the FILE route,
  with `MVI A,<declared length> / CALL ?SLCTS` — the member CLASS is legal, its use is
  per-route.  [C296]: a file PUT is `21 *C(0000) / 11 52 06 / 01 *CODE(cont) / CD ?SIOOP`,
  then N item chains with nothing between, then ONE `CD ?QIOOP` + the continuation triple
  (`golden/e42p2b/E46M1`, byte-exact, file statement 0023..0048 = 37 bytes).  **RE-DERIVED from
  the literal bytes for this round**: the attach's first instruction is `LXI H,*C(0000)` — a CODE
  self-address, NOT "`<fcb>`" as [C296]'s prose words it — and `golden/e42p2a/E46L3` 002F..003A
  versus its own console statement 0046..0051 show the ITEM CHAINS ARE ROUTE-INVARIANT: the same
  `LHLD *D(0009) / MVI A,09 / ?QICOP / ?PNVOP` appears under `?SIOOP` and under the `?SYSPR`
  prologue, and both statements close with `?QIOOP`.  Only the framing differs.
- [C313]/[C325]: a BIT(1) item is `3A *D(cell) / 06 01 / CD ?QB08C / CD ?PNBOP` — its own tail,
  in any position, on the CONSOLE route.  No object combines it with a `0x0652` attach.
- `probes/E46K14.PLI` (`if line then k = 1;` on `2 line char(14) varying`) is a PINNED negative
  row: MY compiler refuses it (`comparison of the internal CHARACTER member REC.LINE`) and the
  RETIRE round did NOT retire it, because DR was never asked.  E48E6 asks, with a fresh key.

## Predictions

| id | prediction (derived, not guessed) |
|---|---|
| P-E1 | **ACCEPTS**, and the site is the ladder with ONE `2B`: `2A *D(k) / 2B / 7C / B5 / D6 01 / 9F / 32 *D(b)` = **10 bytes**.  Derived from [C324]'s measured `9 + |c|` shape at c=2/3 plus [C143]'s `|b| <= 3 -> INX/DCX repeats` threshold. falsifier: a `11 01 FF / 09` (LXI B,DAD B) form at c=1 would mean the threshold is `<= 1`-vs-`>= 2`, not `<= 3`; `LHLD / INX H` (bias +1) would mean DR biases the OTHER way and [C143]'s sign reading is wrong. |
| P-E2 | **ACCEPTS**, and the site is the LXI-B form with a POSITIVE two's-complement immediate: `2A *D(k) / 11 02 00 / 09 / 7C / B5 / D6 01 / 9F / 32 *D(b)` = **13 bytes**, i.e. bias `-(c) = +2`.  Derived by substituting c = -2 into the one encoded rule of [C143]/[C324]. **Flagged as an extrapolation, not a witness**: no measured object has a negative constant. falsifier: any other immediate, or a refusal (would make a negative compare constant a DR language limit). |
| P-E3 | **ACCEPTS**, ladder head UNCHANGED and only the tail retargeted: `2A *D(k) / 2B 2B / 7C / B5 / C6 FF / 9F / 32 *D(b)` — [C310]'s "no CMA anywhere, `^` retargets the tail" law, moved from the `= 0` form onto the ladder. **WEAK**: no object has a ladder under `^`. falsifier: `D6 01 / 9F` unchanged (would mean `^` is dropped — a DR defect worth recording), CMA `2F` (would falsify §1 P11's "never CMA" as route-general), or a refusal. |
| P-E4 | **ACCEPTS**, the LXI-B head with the negated tail: `2A *D(k) / 11 FB FF / 09 / 7C / B5 / C6 FF / 9F / 32 *D(b)`.  Same weakness as P-E3. |
| P-E5 | **ACCEPTS** (the form is legal PL/I — four corpus TESTs use `= '0'b`), but the BYTES ARE AN OPEN QUESTION and I predict only the SHAPE: a `3A *D(b)` head with `E6/SUI` masking and the 00/FF tail, i.e. a variant of E48A10's 13 bytes.  My candidate readings are (i) the same `E6 80 / D6 80` head with the NEGATED tail `C6 FF / 9F`, or (ii) a different mask. If DR instead emits the `= '1'b' bytes verbatim, the materialiser ignores the literal's value — a defect to record, not to copy. |
| P-E6 | **VERDICT UNKNOWN — this is the round's real question.**  I predict **ACCEPTS** on the general [C297] pattern that DR's language admits operand classes my bank has simply never asked about, but I have NO byte prediction: nothing in `golden/` tests a character operand as a bare condition.  If DR REFUSES, E46K14's negative row becomes `dr-refuses` law (correct as written) and the `imem_refuse` WHY-string must say so; if DR ACCEPTS, it is a `my-gap` and the bytes are new law. |
| P-E7 | **VERDICT UNKNOWN, leaning ACCEPTS** for the same reason as P-E6 ([C297] admits the FIXED member class on another route; [C326] admits a member in this exact TEST orientation).  NO helper prediction is defensible: [C191]'s three helpers are all pinned on VARYING or literal operands, and a FIXED member has no leading length byte, so `?SCCVM` would have to read one that does not exist.  The probe's purpose is to find out which helper, if any, DR uses. |
| P-E8 | **ACCEPTS.**  The statement is [C296]'s file frame — `21 *C(0000) / 11 52 06 / 01 *CODE(cont) / CD ?SIOOP` — then the bit chain `3A *D(b) / 06 01 / CD ?QB08C` with its own tail, then the literal chain `21 *D(pool) / 3E 01 / CD ?SLCTS / CD ?PNCOP`, then ONE `CD ?QIOOP` and the continuation triple (`lxi d 0252 / lxi b *CODE / ?SYSPR`).  Derived from E46M1 + E46L3 (chains route-invariant, measured above) + [C325] (the bit item and its own `?PNBOP`).  The discriminating unknown is the BIT ITEM'S TAIL: `?PNBOP` is what BOTH bit sites in the console bank use, while `?PNVOP` closes a NUMERIC chain ([C297]); if the file route instead gives the bit item `?PNVOP`, the tail is chosen by ROUTE and not by item class. falsifier: a refusal would make my `authorize_file_item` refusal correct law (`dr-refuses`). |

## What this round does NOT claim

- **Nothing about over-extent INITIAL or an over-extent STORE** (the two remaining §3 items).
  They are excluded on purpose, not forgotten: the only extent law I hold is [C191]'s
  truncation witness, quoted from the ledger (E30T1: a `character(6)' member and an
  `'ABCDEFGH'' source gives `MVI A,06' cap / `MVI B,08' len / `?SMCVM'), and an
  over-extent STATIC INITIAL would need the DATA-image law of [C319]/[C322] to be extended
  beyond the measured `<= extent` range.  Writing that probe needs its own derivation and
  belongs to a separate round; it is not smuggled in here.
- **Nothing about a BASED member in a condition STORE** — no witness anywhere, still refused.
- **Nothing about member-vs-member** compares (kept as a named refusal; would be round 6).
- **No runtime claim of any kind**: every probe is judged on `.REL` bytes under `$L$D`, so **no
  `spec/RUNTIME.txt` row may come from this round**, and nothing here measures the varying
  length-rewrite of P2d §2.2.
- P-E2/P-E3/P-E4 are EXTRAPOLATIONS of a rule measured only at positive/zero constants; a MISS
  there is the expected outcome and stays in the table (PROTOCOL #2).  P-E6/P-E7 have no byte
  prediction at all, so §1 will score them on VERDICT only.

## Command (for the session that runs it — NOT run here)

    PLI_SRC=probes python3 oracle/batch.py E48E1 E48E2 E48E3 E48E4 E48E5 E48E6 E48E7 E48E8 \
        --tag e48p2e --switches '$L$D'

`golden/e48p2e` must not exist before this call (verified: it does not).  Never pass `--reuse`
into an existing tag.  Then write `RESULTS.md` §1 as a prediction-vs-verdict table over
P-E1..P-E8, re-read every accepted `.REL` with `tools/reldump.py` /
`spec/lab-evidence/e2e42-p2b/chaindump.py` (never a `.PRN` size, PROTOCOL #6), and commit
goldens + report TOGETHER.  Lowering may only touch what §2 measures.
