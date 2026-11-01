# E2E-49/P3 — RESULTS (composite FIXED/TEST bank: C1..C4, D1..D4, E1..E2, F1..F4)

## 0. Lineage

- Probes + `mkprobes.py` + `HYPOTHESES.md` + `BASELINE-MINE.txt` committed BEFORE any
  oracle call at **`3659f5d`** (fill-in `0a46824`; `git log --format=%h --
  probes/E49C1.PLI | tail -1`). `golden/e49p3` did not exist before the run. Every
  emitted probe line is <= 71 columns; files are CRLF + `^Z` ([C193] (b)).
- ONE oracle campaign exactly as pre-registered:
  `PLI_SRC=probes python3 oracle/batch.py E49C1 E49C2 E49C3 E49C4 E49D1 E49D2 E49D3
  E49D4 E49E1 E49E2 E49F1 E49F2 E49F3 E49F4 --tag e49p3 --switches '$L$D'`
  -> **14 ok / 14** (`golden/e49p3/`, summary; the runner split into internal batches).
  **NO refusals at all**: every `.PRN` prints `NO ERROR(S) IN PASS 1` and
  `NO ERROR(S) IN PASS 2`. Verdicts judged on complete `.REL` bytes with
  `tools/reldump.py` (PROTOCOL #6), whole files by `cmp`.
- Classification (PROTOCOL #3): **every difference this round is `my-gap`** — DR
  accepted everything; my baseline (BASELINE-MINE.txt) refused all eight B/D rows and
  differed on all four A rows; the two C rows came out byte-identical to my output.
  **No `dr-refuses` row exists in this bank.**

## 1. Prediction vs verdict (every MISS kept)

| id | predicted | measured verdict | score |
|---|---|---|---|
| P-C1 (member-left, `=`, 3/3) | ACCEPTS; H-AK-M KEEP `06 03/3E 03` (CODE 66) vs H-AC-M COLLAPSE `06 03/78` (CODE 65) | ACCEPTS, COLLAPSED: `21 *D(0005 na)/EB/21 *D(0000)/06 03/78/CD ?SCCCM/C2 -> 001C`; CODE 65 (0x41), DATA 000F | **HIT verdict / H-AC-M CONFIRMED, H-AK-M FALSIFIED** — the [C338] TBD resolves: the collapse DOES extend to the member-vs-literal staged template |
| P-C2 (literal-left, `=`, 3/3) | ACCEPTS; H-AK-L KEEP (CODE 65) vs H-AC-L COLLAPSE (CODE 64) | ACCEPTS, COLLAPSED: `21 *D(0005)/11 *D(0000)/06 03/78/CD ?SCCCM/C2 -> 001B`; CODE 64 (0x40) | **HIT / H-AC-L CONFIRMED, H-AK-L FALSIFIED** — the DIRECT template collapses too; no split between orientations |
| P-C3 (`^=` member-left) | P-C1's head with skip CA | CA at 0013, fill -> 001C | **HIT** |
| P-C4 (`^=` literal-left) | P-C2's head with skip CA (first CA witness on this template) | CA at 0012, fill -> 001B | **HIT** — [C072]'s synthesis becomes MEASURED on the direct fixed template |
| P-D1 (`na = rec.nb`) | lean ACCEPT == E49B1 but module-name bytes | `cmp -l` vs `golden/e49p2/E49B1/E49B1.REL`: differs ONLY at bytes 5,6,19,27,28 (the packed name fields + checksum) | **HIT** — bare-qualified pair byte-identical to the qualified-qualified object |
| P-D2 (`rec.na = nb`) | same as P-D1 | name bytes only (5,6,7,19,20,27,28,29) | **HIT** — bare RIGHT in a member pair is admitted, invisible |
| P-D3 (`na = nb`) | same as P-D1 | name bytes only, same set as D2 | **HIT** — bare/bare too; E49B1..D3 = byte-quartet |
| P-D4 (`'AB' = na`) | weak-lean ACCEPT on E48E7's template; alternatives H-B-gate/H-B-mixed refusal | ACCEPTS: `21 *D(0004 na)/11 *D(0000 'AB')/06 02/3E 03/CD ?SCCCM/C2 -> 001C`; CODE 65, DATA 000E | **HIT (fold reading)** — the P1 "asymmetry" was MY evidence limit, NOT a DR boundary; the bare spelling is admitted in the RIGHT slot of the direct template (unequal 2/3 → two immediates, no collapse) |
| P-E1 (`'ABCD' = rec.na`) | H-CE (== my baseline bytes); falsifiers H-CR/H-CT/H-CN | ACCEPTS; whole file **byte-identical to my baseline .REL**: `21 *D(0006)/11 *D(0000 ABCD)/06 04/3E 03/CD ?SCCCM/C2 -> 001C`, CODE 65, DATA 0010, pool WHOLE | **HIT — no arm needed**; [C336] transfers to the literal-LEFT orientation BY MEASUREMENT, not extrapolation |
| P-E2 (`^=` same pair) | P-E1's head with CA | identical to my baseline with 0xca at 0013 | **HIT** |
| P-F1 (`rec.na < rec.nb`) | verdict OPEN, lean accept; helper/mechanism/branch all open | ACCEPTS: stacked mm head VERBATIM (`21 *D(0002 na)/E5/21 *D(0005 nb)/D1`) written ORDER, `06 03/78`, `CD ?SCCCM`, skip byte **0xd2 (JNC)** -> 001D; CODE 66, DATA 000C | **HIT (verdict)**; H-D-CX FALSIFIED (helper stays ?SCCCM); H-D-SC confirmed with the JNC branch; equal extents collapse in RELATIONS too |
| P-F2 (`rec.na > rec.s2`) | positional `06 03/3E 02` under H-D-SC | ACCEPTS: operands **SWAPPED** — `21 *D(0008 s2)/E5/21 *D(0002 na)/D1/06 02/3E 03/CD ?SCCCM/JNC -> 001E`; CODE 67 | **verdict HIT; my predicted length pair FALSIFIED** — B/A are positional on the SWAPPED operands: `06 02/3E 03`, not `06 03/3E 02` |
| P-F3 (`rec.na <= rec.nb`) | as F1, skip may differ | ACCEPTS: **SWAPPED** (`21 *D(0005 nb)/E5/21 *D(0002 na)/D1/06 03/78/CD ?SCCCM`), skip **0xda (JC)** -> 001D; CODE 66 | **HIT**; `<=` swaps AND branches JC |
| P-F4 (`rec.s2 >= rec.na`) | positional `06 02/3E 03` under H-D-SC | ACCEPTS: **WRITTEN order** (`21 *D(0008 s2)/E5/21 *D(0002 na)/D1/06 02/3E 03/CD ?SCCCM/JC -> 001E`); CODE 67 | **HIT (pair and order)** — `>=` does NOT swap |

## 2. Laws read out of the `.REL` records

1. **The equal-extent collapse is a `?SCCCM` LENGTH-PAIR law, not a member-pair
   peculiarity.** When the two positional length attributes are EQUAL, DR emits
   `MVI B,n / MOV A,B` (`06 n / 78`) with NO `MVI A` — measured now in BOTH literal
   templates: staged `EB` member-left (E49C1/C3, CODE 65) and direct `11`
   literal-left (E49C2/C4, CODE 64), alongside the stacked member-vs-member objects
   (E49B1/B2/B5). Unequal attributes keep two immediates (E48E7 2/3, E49A* 3/2,3/4,
   E49B3/B4, E49D4 2/3, E49E1/E2 4/3, E49F2/F4). This SETTLES [C338]'s [TBD]: the
   collapse condition is the EQUALITY OF THE TWO ATTRIBUTES, whatever their source
   (extent or literal length) — six collapse objects (B1,B2,B5,C1,C2,C3,C4) vs every
   unequal pair keeping two immediates.
2. **`CA` is the `^=` skip byte on the DIRECT literal-left template too** (E49C4 0012,
   E49E2 0013): [C072]'s family law, converted from synthesis to measurement in this
   orientation. Fill = next statement ([C309]) in all fourteen objects.
3. **Qualification of an internal FIXED member is INVISIBLE to every measured compare
   encoding.** The [C253]/[C258] fold: E49D1/D2/D3 are byte-identical to E49B1 (all
   three spellings of the member pair); E49D4 shows the bare member admitted in the
   RIGHT slot of the direct template, so the P1 scope note ("left side only") was an
   evidence boundary, NOT a DR gate. Bare spellings in the `?SCCCM` family now have
   objects for: bare-left-of-literal (E49A2), bare-right-of-literal (E49D4), and any
   combination in a member-vs-member pair (D1/D2/D3). One cell, one encoding.
4. **An over-extent literal written LEFT is ACCEPTED and pooled WHOLE** (E49E1/E2:
   `'ABCD'` intact at 0000..0003, positional `06 04 / 3E 03`): [C336]'s finding now
   MEASURED in the literal-left orientation; H-CR/H-CT/H-CN all falsified. My
   existing template already reproduces both objects byte-for-byte.
5. **ORDERED RELATIONS on FIXED character members are ACCEPTED through the SAME
   `?SCCCM` helper and the SAME stacked head parking as `=`** ([C337] form), with TWO
   relation-specific laws: (a) **operand ORDER** — `<` and `>=` take the operands in
   WRITTEN order, `>` and `<=` are lowered with the operands **SWAPPED** (mirroring
   the numeric family's `a > b` as `b < a` rule — now measured for characters);
   (b) **branch byte** — strict relations (`<`, `>`) skip with **JNC `0xd2`**, weak
   relations (`<=`, `>=`) with **JC `0xda`**. The length pair stays POSITIONAL ON THE
   OPERANDS AS LOWERS (after any swap): F2 `06 02/3E 03` (s2 lowered left), F4
   `06 02/3E 03` (s2 written left); equal extents collapse (`06 03/78`) in F1/F3.
   No new helper family appears: the PLILIB `?CX*` prior is FALSIFIED for these four
   shapes. (Runtime flag semantics of ?SCCCM/JNC/JC are NOT claimed — byte tier.)
6. **Sizes:** collapsed heads: staged 16 bytes CODE 65 (C1/C3), direct 15 bytes CODE
   64 (C2/C4), stacked 17 bytes CODE 66 (D1..D3, F1, F3); non-collapsed stacked 18
   bytes CODE 67 (F2, F4); direct with two immediates CODE 65 (D4, E1, E2). DATA:
   000F (A panel, 'ABC' pooled), 000C (D1..D3, F1..F4, no compare literal), 000E
   (D4 'AB'), 0010 (E1/E2 'ABCD') — [C314] pool-first layout in all fourteen.

## 3. What this round did NOT measure

- STOREs (either orientation), literal-vs-literal, BASED members, fixed truthiness,
  `^( ... )` composition — untouched, keep refusing.
- BARE spellings in an ORDERED RELATION (D-panel objects are all `=`; every F object
  writes BOTH members qualified) — `unmeasured`; the relation arm must admit
  qualified-only until measured.
- Ordered relations with a LITERAL operand (member/literal `<` etc.) — no object.
- Relations `<>`-style spellings or `><`; unequal-extent STRICT vs WEAK combinations
  beyond F2/F4's single pair; the collapse in a swapped-head with unequal lengths is
  per-operand-position (measured once, F2/F4).
- No runtime semantics: judged on `.REL` bytes only — **no `spec/RUNTIME.txt` row may
  come from this round**.

## 4. Classification (PROTOCOL #3)

All fourteen rows ACCEPTED by DR (`14 ok / 14`, both passes clean in every `.PRN`).
- `my-gap` (12): E49C1..C4 (collapse missing in both literal templates), E49D1..D4
  (bare-spelling admission), E49F1..F4 (ordered relations).
- Already byte-exact (2): E49E1, E49E2 — whole-file `cmp` against my baseline `.REL`
  shows ZERO differing bytes (module names are equal by construction); NO arm needed.
- `dr-refuses`: NONE this round.
