# E2E-48/P2e — RESULTS (round 5, E48E1..E48E8)

## 0. Lineage

- Probes + `mkprobes.py` + `HYPOTHESES.md` + `BASELINE-MINE.txt` committed BEFORE any oracle
  call at **`421656a`** (`git log --format=%h -- probes/E48E1.PLI | tail -1`); the prediction-SHA
  fill-in commit is its child and is also an ancestor of the run. `golden/e48p2e` did not exist
  before the run (verified). All eight comment lines are <= 71 columns (the law that killed P2d
  run 1).
- One oracle call, exactly as pre-registered:
  `PLI_SRC=probes python3 oracle/batch.py E48E1..E48E8 --tag e48p2e --switches '$L$D'`
  -> **7 ok / 8** (`golden/e48p2e/`, `summary.txt`, `transcript-batch0/1.txt`).
- **E48E6 is the one `diag`:** PASS 1 clean, PASS 2 prints
  `14 c  if line then k = 1;` / `BIT REQ  ?` / `1 ERROR(S) IN PASS 2` and produces **NO `.REL`**
  (`golden/e48p2e/E48E6/E48E6.PRN`). It is kept as evidence. Everything below is judged on
  `.REL` bytes read with `spec/lab-evidence/e2e42-p2b/chaindump.py`, never from a `.PRN` size
  (PROTOCOL #6) — the `CODE SIZE = 004A` line printed for E48E6 is a rendering, not an object.

## 1. Prediction vs verdict (every MISS kept)

| id | predicted | measured verdict | score |
|---|---|---|---|
| P-E1 | ACCEPTS; `2A *D(k) / 2B / 7C / B5 / D6 01 / 9F / 32 *D(b)` = 10 bytes | E48E1 0006 exactly that (CODE 55, DATA 5) | **HIT** |
| P-E2 | ACCEPTS; LXI-B form with a POSITIVE immediate `11 02 00` for `k = -2` | E48E2 0006 is `2A *D(k) / 23 23 / 7C / B5 / D6 01 / 9F / 32` — **two `INX H`**, not LXI B | **HIT (verdict) / MISS (encoding)** |
| P-E3 | ACCEPTS; ladder head + negated tail `C6 FF / 9F` | E48E3 0006: `2A / 2B 2B / 7C / B5 / C6 FF / 9F / 32` | **HIT** |
| P-E4 | ACCEPTS; LXI B,FFFB head + `C6 FF / 9F` tail | E48E4 0006: `2A / 11 FB FF / 09 / 7C / B5 / C6 FF / 9F / 32` | **HIT** |
| P-E5 | ACCEPTS; shape `3A` head + mask + 00/FF tail, bytes an open question | E48E5 0006: `3A *D(b) / E6 80 / D6 01 / 9F / 32 *D(f)` — 11 bytes, **no `D6 80` step at all** | **HIT (verdict) / MISS (I predicted a variant of the 13-byte '1'b form; it is 11 bytes)** |
| P-E6 | **ACCEPTS** (verdict-only prediction, no bytes) | **REFUSED**: PASS 2 `BIT REQ`, no `.REL` | **MISS — and the useful kind: the answer is `dr-refuses`** |
| P-E7 | VERDICT UNKNOWN, leaning ACCEPTS; no helper prediction defensible | **ACCEPTS**: `21 *D(member) / 11 *D(pool) / 06 02 / 3E 03 / CD ?SCCCM / C2 fill -> 001C` | **HIT (verdict) / the helper is NEW: `?SCCCM`** |
| P-E8 | ACCEPTS; file frame + bit chain with `?PNBOP` + literal chain + one `?QIOOP` | E48E8 0023..0048 exactly that (CODE 81, DATA 11) | **HIT** |

## 2. Laws read out of the `.REL` records

1. **The biased ladder is sign-INDEPENDENT and its threshold is `|bias| <= 3`, reached from
   `-c`, not from `c`.** `k = -2` (E48E2 0006) emits `LHLD k / INX H / INX H / MOV A,H / ORA L`
   + the [C095] tail — bias `-c = +2`, so a negative constant walks UP with `INX`, and `|c| = 2`
   stays inside the repeat regime; `k = 1` (E48E1) is ONE `DCX H`. The ladder is therefore
   `|c| <= 3 -> INX/DCX repeats, |c| >= 4 -> LXI B,two's-complement(-c) / DAD B` for BOTH signs
   (E48E4 confirms `= 5 -> 11 FB FF`). This closes [C324]'s "`k = 1` remains unmeasured" and
   narrows nothing: it EXTENDS the same cost model, exactly the [C143] shape with the sign of the
   bias flipped by the constant's sign. **My `hl_bias` already implements this rule verbatim**
   (`abs b <= 3 -> repeats`, else `LXI B, b land 0xffff`), so this is a gap of `bit_cond_mat`'s
   admitted CLASSES, not of the bias encoder.
2. **A negated condition as a STORE VALUE keeps the ladder head and retargets only the tail.**
   `^(k = 2)` = the [C324] head + `C6 FF / 9F`; `^(k = 5)` = the [C143] head + `C6 FF / 9F`
   (E48E3/E48E4 0006). `^` in a value is the [C095]-flag polarity flip, never `CMA` (still no
   0x2F in any E48 object across P1/P2c/P2d/P2e). The rule now holds for `= 0` ([C310]) AND the
   ladder, both regimes.
3. **`= '0'b' as a materialised value is `3A *D(b) / E6 80 / D6 01 / 9F / 32 *D(f)` — 11 bytes,
   SIX of them the flag tail** (E48E5 0006..0010). Compare the measured `'1'b` value of [C310],
   E48A10 0006: `3A / E6 80 / D6 80 / D6 01 / 9F` — the `'0'b` form OMITS the `SUI 80` normaliser
   and subtracts the 1 directly. Semantics agree: `b` is high-bit justified, so after `ANI 80`
   the accumulator holds 00 or 80; a bit value is 128, and `= '0'b` is `accumulator - 1`, `= '1'b`
   is `(accumulator - 128) - 1`. My `bit_cond_mat` admits only the `'1'b` arm; `'0'b` is a
   `my-gap`.
4. **A FIXED CHARACTER operand in a compare takes a NEW helper, `?SCCCM`, with BOTH lengths.**
   E48E7 0006: `LXI H,*D(member cell) / LXI D,*D(pooled literal) / MVI B,2 (literal length) /
   MVI A,3 (DECLARED extent) / CALL ?SCCCM / C2 00 00` with the [C309] no-else skip filled to the
   NEXT statement (001C). This is the fixed-vs-literal counterpart of [C191]'s `?SCVCM`/`?SCCVM`
   family — the `CC` pair names the two FIXED operands — and it is the first object anywhere that
   compares a FIXED character. The register law is [C191]'s: HL = right operand, DE = left,
   length of the LITERAL in B, and the declared extent in A (the same "A is the destination/capacity,
   B is the source length" polarity of [C191]/[C197], here in a compare). DATA 000B: pool `'AB'`
   at 0000, `'K='` at 0002, record frame AUTOMATIC (member at 0004, `k` at 0009) — the [C314]/§2.7
   layout law unchanged.
5. **A BIT(1) PUT item behind a file attach is ACCEPTED and its chain is ROUTE-INVARIANT.**
   E48E8 0023..0048: `21 *C(0000) / 11 52 06 / 01 *CODE(0048) / CD ?SIOOP`, then
   `3A *D(b) / 06 01 / CD ?QB08C / CD ?PNBOP`, then the literal chain
   `21 *D(000A) / 3E 01 / CD ?SLCTS / CD ?PNCOP`, then ONE `CD ?QIOOP` and the continuation
   triple. This is byte-for-byte the console bit chain of [C313]/[C325] inside the file frame of
   [C296]; the tail is chosen by ITEM CLASS, not by route (corroborated independently by
   `golden/e42p2a/E46L3`, where the same `?QICOP/?PNVOP` chain appears under both framings).
6. **DR REFUSES the truthiness of a CHARACTER (varying or fixed) operand.** E48E6's PASS-2 error
   marker is `BIT REQ` at the `if line then` statement. Classification: `dr-refuses`. My named
   refusal of E46K14's shape is therefore correct law and its negative-panel row may now be
   labelled measured rather than unmeasured — a refusal reason recorded in `spec/INVENTORY.txt`
   must say which class it is (PROTOCOL #3).

## 3. What this round did NOT measure

- The `BIT REQ` message is DR's own text but I have NOT measured what it accepts elsewhere: no
  claim is made here about a character operand in any OTHER condition position (e.g. a bare
  scalar `char` variable, a `^` over one, or one under `&`).
- `?SCCCM` in a STORE (`s = ...` with a fixed source), `?SCCCM` with the member on the LEFT,
  literal-vs-literal fixed compares, and **member-vs-member** compares of any kind: no object.
- The FIXED member's compare when the member is VARYING-with-qualification, and any **BASED**
  member in a condition (store or test) — still no witness anywhere.
- Over-extent `INITIAL` and over-extent STORE remain UNMEASURED (excluded from this round by
  design; see HYPOTHESES.md "What this round does NOT claim").
- No runtime semantics: judged on `.REL` bytes only, so **no `spec/RUNTIME.txt` row may come from
  this round**. `E48E8`'s `?SCCCM`-free output file was never linked or run.
- E48E6 has no object, so nothing can be lowered from it — it is a classification, not a route.
