# E2E-51/P1 — RESULTS (FIXED BINARY variable-divisor DIVISION bank E51A..E51L)

## 0. Lineage

- Probes + `mkprobes.py` + `PLAN.md` + `HYPOTHESES.md` + `BASELINE-MINE.txt` committed
  BEFORE any DR call at **`9bac977`** (the prediction SHA, verified:
  `git log --format=%h -- probes/E51A.PLI | tail -1` -> `9bac977`). Every probe is
  CRLF + bare `^Z`, all lines <= 71 columns ([C193] (b)). `golden/e51p1` did not exist
  before the run (verified absent at HEAD `9bac977` and immediately before the call).
- ONE oracle campaign exactly as pre-registered:
  `PLI_SRC=probes timeout 900 python3 oracle/batch.py E51A E51B E51C E51D E51E E51F
  E51G E51H E51I E51J E51K E51L --tag e51p1 --switches '$L$D'`
  -> **12 ok / 12** (`golden/e51p1/summary.txt`; the runner split internally into three
  batches of 4; rc=0, no timeout). Never `--reuse`.
- **NO refusals at all**: every one of the 12 `.PRN` prints `NO ERROR(S) IN PASS 1` and
  `NO ERROR(S) IN PASS 2` (verified by count = 2 over every file). DR ACCEPTED every
  binary var-divisor form in the bank.
- Verdicts judged on COMPLETE `.REL` files byte-for-byte with `tools/reldump.py`
  (PROTOCOL #6), whole files by `cmp`.
- Classification (PROTOCOL #3): **eleven `my-gap` rows (E51A..E51K)** — DR emitted an
  object, `BASELINE-MINE.txt` shows my compiler refused each one — and **E51L was
  already byte-exact** (control row: my baseline `.REL` whole-file `cmp` with the DR
  golden, ZERO differing bytes; sha `bc2fd12e…`). **No `dr-refuses` row exists in this
  bank.** The control row passing validates the batch harness before any other verdict
  is read (HYPOTHESES E51L falsifier branch: NOT triggered).
- PRN size headers match every prediction: DATA AREA `0008` for A..J and L, `0009` for
  K (the added 1-byte `d`); CODE SIZE 0017 (A,B), 001C (C,D,F,G), 001F (E), 0028 (H),
  0027 (I), 001A (J,L), 001B (K).

Head notation below: `E5/D1` = PUSH H / POP D parking; `EB` = XCHG; `19` = DAD D;
`2A rN` / `22 rN` = LHLD / SHLD of data reloc target `N`; `21 lo hi` = LXI H immediate;
`3A rN` = LDA of a 1-byte cell; `6F 87 9F 67` = the MOV L,A / ADD A / SBB A / MOV H,A
sign-extend ladder. Frame in every row: `01 00 02 / CD ?START` at 0000, `CD ?STOPX` at
the tail (the E51H/E51I fixup records are spelled out in place).

## 1. Prediction vs verdict (every MISS kept verbatim — this round has TWO)

| id | construct | predicted | measured verdict | score |
|---|---|---|---|---|
| E51A | `z = a / b` | H-A-park: F005 shape `2A r0 / E5 / 2A r2 / D1 / CD ?ID22N / 22` modulo the extra bank cell | ACCEPTS exactly that; the full DATA/RELOC/CHAIN-EXT record stream of `golden/f6probe/F005/F005.REL` matches line-for-line, only the z reloc (r4 -> r6) and DATA SIZE (0006 -> 0008) differ — the extra `c` cell; CODE 0017 | **HIT** — H-A-refuse falsified; F005's provenance CONFIRMED by reproduction |
| E51B | `z = 1200 / b` | H-B-de (primary): `2A r2 / 11 B0 04 / CD ?ID22N / 22` | ACCEPTS: `21 B0 04 / E5 / 2A r2 / D1 / CD ?ID22N / 22 r6`; CODE 0017 | **MISS on H-B-de (FALSIFIED); HIT on competitor H-B-stack** — the LITERAL takes the parked-dividend slot via `LXI H,const` then PUSH/POP, exactly the variable form's parking; `LXI D` direct is NOT used; H-B-conv and H-B-refuse falsified |
| E51C | `z = (a + b) / c` | H-C-park: add law then park the SUM, ONE SHLD | ACCEPTS: `2A r0 / EB / 2A r2 / 19 / E5 / 2A r4 / D1 / CD ?ID22N / 22 r6`; exactly ONE `22` store; CODE 001C | **HIT** — H-C-temp (materialised temp) and H-C-refuse falsified |
| E51D | `z = a / (b + c)` | H-D-inline: park the dividend FIRST, build the sum inside the parked region | ACCEPTS: `2A r0 / E5 (at 0009) / 2A r2 / EB / 2A r4 / 19 / D1 / CD ?ID22N / 22 r6`; one store | **HIT** — H-D-temp and H-D-refuse falsified |
| E51E | `z = a / b / c` | H-E-push: two `?ID22N` calls, quotient PUSH-parked between, ONE SHLD | ACCEPTS: `<a/b div> / E5 / 2A r4 / D1 / CD ?ID22N / 22 r6`; CD count = 2, SHLD count = 1 | **HIT** — H-E-store (store/reload) and H-E-refuse falsified; binary chaining needs no DEC-style store (the [NG17] DEC witness does not transfer, but chaining is accepted) |
| E51F | `z = a / b + c` | H-F-xchg: `<div> / EB / 2A r4 / 19 / 22 r6` ([C141] P7 isomorphism) | ACCEPTS exactly that; CODE 001C | **HIT** — H-F-push (P5 form), H-F-store, H-F-refuse falsified |
| E51G | `z = c + a / b` | H-G-identical: byte-identical object to E51F | whole-file `cmp -l` vs E51F: ONLY bytes 5, 17, 25 differ — the three packed name records (PROG-NAME, EXTDEF, DEF-PUBLIC; one bit each, `F` 0x46 vs `G` 0x47); the DATA/RELOC/CHAIN-EXT/SET-LC record streams are IDENTICAL | **HIT** — H-G-leftfirst and H-G-refuse falsified; orientation-free right-first evaluation HOLDS for DIV operands |
| E51H | `put list(a / b)` | H-H-c079: F005 div lowering then the [C079] numeric tail `3E 09 / ?QICOP / ?PNVOP / ?QIOOP` + cont triple | ACCEPTS: preamble `11 52 02 / 01 00 00 / CD ?SYSPR`, then the F005-shape div, then `3E 09 / CD ?QICOP / CD ?PNVOP / CD ?QIOOP`, then the cont triple as `LINK-SET-LC code 000A / RELOC code 0x25 / LINK-SET-LC code 0025 / CD ?STOPX`; CODE 0028 | **HIT** — H-H-refuse falsified; width byte `09` = the bin15 min(9,digits(32767)+4) law holding over a helper RESULT exactly as over a var |
| E51I | `if a / b = c then z = 1` | H-I-eq: div then the [C072] tail `PUSH H / LHLD c / POP D / CALL ?IS22N / MOV A,H / ORA L / CA(forward)/LAD`, then `21 01 00 / 22 r6` | ACCEPTS (DR prints NO ERRORS). Measured tail after `<div>`: `E5 / 2A r4 / D1 / CD ?IS22N / 7C / B5 / C2 <fwd> / 21 01 00 / 22 r6`, then the skip-operand fill `LINK-SET-LC code 001C / RELOC code 0x24 / LINK-SET-LC code 0024 / CD ?STOPX`; CODE 0027 | **acceptance HIT (H-I-refuse FALSIFIED — my `condition form not in E2E-3b subset` refusal is a `my-gap`); MISS on the jump byte: predicted `CA`, measured `C2` (JNZ)** kept verbatim — the equality zero-test uses the [C089] `= 0` polarity (skip the THEN-part when HL != 0), not the `CA` I predicted from [C072]; H-I-alt partially right (compare keyed on the helper RESULT needs the same park the store uses) |
| E51J | `z = -a / b` | H-J-in20: `2A r0 / CD ?IN20N / E5 / 2A r2 / D1 / CD ?ID22N / 22 r6` | ACCEPTS exactly that; `?IN20N` CHAIN-EXT at 000A precedes `?ID22N` at 0012; CODE 001A | **HIT** — H-J-fuse (negate AFTER divide) falsified by offset order; H-J-refuse falsified |
| E51K | `z = a / d`, `d fixed bin(7)` | H-K-ld: `2A r0 / 3A r8 / E5 / 6F / 87 / 9F / 67 / D1 / CD ?ID22N / 22 r6`; DATA 0009 | ACCEPTS exactly that, incl. DATA SIZE `abs 0009` and the d-at-offset-8 inline reloc; CODE 001B | **HIT** — H-K-lhld, H-K-conv, H-K-refuse falsified; the [C079] 1-byte RHS interleave transfers from MUL to DIV unchanged |
| E51L | `z = a / 3` | H-L-known: P080A ladder; mine already byte-exact | whole-file `cmp` of my baseline `.REL` vs the DR golden: **ZERO differing bytes** (both 128 B, sha `bc2fd12e…`) | **HIT** — control row green; harness and constant path both valid |

**Count: 10 clean HITs, 2 MISSes kept as written** — E51B primary H-B-de falsified
(competitor H-B-stack accepted); E51I predicted jump byte `CA` falsified (measured `C2`).
Every competing refusal hypothesis (H-*-refuse) is falsified by the acceptance itself.

## 2. Laws read out of the `.REL` records (byte tier only)

### 2.1 The DIV parking law — dividend parked, divisor arrives in HL
- `z = <dividend> / <divisor>` lowers as: **evaluate <dividend> into HL; `E5` (PUSH H);
  evaluate <divisor> into HL; `D1` (POP D); `CD ?ID22N`; `22 <z reloc>` (SHLD z)** —
  exactly the [C089] variable-divisor MOD parking shape with the quotient helper. The
  ABI `id22n DE,HL -> HL` (spec/notes/plilib-entrypoints.txt) matches: dividend ends in
  DE, divisor in HL.
- The dividend slot accepts every lowering that leaves HL: a var load (A), an `LXI H`
  literal (B — H-B-de falsified; literals are NOT loaded into DE), a compound sum built
  first in HL (C), and a unary-minus result (J: `?IN20N` runs on the dividend BEFORE the
  park — negate-then-park, no fusion with the divide).
- A compound DIVISOR is evaluated inside the parked region (D): the `E5` precedes the
  sum's own `EB/2A/19`, and the sum lands in HL immediately before `D1`.
- Chaining (E): the first quotient (returned in HL) is itself PUSH-parked as the second
  dividend — `E5 / <divisor load> / D1 / CD ?ID22N` again; ONE store for the whole
  expression.
- 1-byte binary divisor (K): the [C079]/[N303] interleave `raw LDA + PUSH H + sign-extend
  ladder + POP D` transfers verbatim from MUL.

### 2.2 Quotient consumption
- `z = a/b + c` and `z = c + a/b` produce ONE identical object (G == F modulo packed
  name bytes): the quotient in HL is XCHG'd to DE, `c` is loaded and `DAD D` — the
  [C141] P7 isomorphism (call-left: `EB / 2A / 19`), right-first evaluation
  orientation-free.
- PUT item (H): the div lowering simply precedes the standard [C079] numeric tail; the
  width law applies to the helper RESULT (bin15 -> `3E 09`).
- Equality TEST (I): the RESULT is parked (`E5`) across the RIGHT operand (`LHLD c`),
  `D1`, `CALL ?IS22N`, then the HL-zero test `7C B5` and **`C2` (JNZ) over the THEN-part**,
  patched by the standard forward-fixup triple (SET-LC/RELOC-code/SET-LC). `= c` therefore
  shares the [C089] zero-test polarity; the [C072] `CA` reading does NOT apply here.

### 2.3 Constant-divisor boundary
- E51L stays on the P080A in-line ladder (`3E k / E5 / 6F 87 9F 67 / D1 / CD ?ID22N`) —
  both forms coexist; nothing in this round changes the constant path.

## 3. Not measured (deferred, byte tier)
- Runtime semantics of `?ID22N` (toward-zero vs floor truncation, zero-divisor behaviour)
  and any `.COM` link/console evidence: NOT part of this round (PLAN § "Not predicted").
- `z = a / -b` (unary-minus DIVISOR), DIV nested inside MOD, and mixed 1-byte DIVIDEND:
  unmeasured; no claim words cover them.
