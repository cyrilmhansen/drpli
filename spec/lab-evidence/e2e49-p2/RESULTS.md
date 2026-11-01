# E2E-49/P2 — RESULTS (member-vs-member FIXED compares in TEST, E49B1..E49B5)

## 0. Lineage

- Probes + `mkprobes.py` + `HYPOTHESES.md` + `BASELINE-MINE.txt` committed BEFORE any oracle
  call at **`3bd9417`** (`git log --format=%h -- probes/E49B1.PLI | tail -1`); the
  prediction-SHA fill-in commit is its child, `586c240`, and is also an ancestor of the run.
  `golden/e49p2` did not exist before the run (verified with `ls` at both commits).
  Every emitted probe line is <= 71 columns; files are CRLF + `^Z` ([C193] (b)).
- One oracle campaign, exactly as pre-registered:
  `PLI_SRC=probes python3 oracle/batch.py E49B1 E49B2 E49B3 E49B4 E49B5 --tag e49p2 --switches '$L$D'`
  -> **5 ok / 5** (`golden/e49p2/`, `summary.txt`; the runner split the five probes into two
  simulator batches of 4 + 1 — `transcript-batch0.txt`, `transcript-batch1.txt`). NO
  refusals: the whole member-vs-member fixed family is admitted, so nothing here is
  `dr-refuses`; every gap this round opens is a `my-gap` (my baseline refused all five,
  `BASELINE-MINE.txt`).
- All five `.PRN`s print `NO ERROR(S) IN PASS 1` and `NO ERROR(S) IN PASS 2`. Verdicts and
  laws below are judged on the `.REL` bytes read with
  `spec/lab-evidence/e2e42-p2b/chaindump.py` and `tools/reldump.py`, never from a `.PRN`
  (PROTOCOL #6) — the `CODE SIZE` lines agree with the objects (0x42 = 66, 0x43 = 67) but
  the objects are the authority.

## 1. Prediction vs verdict (every MISS kept)

| id | predicted | measured verdict | score |
|---|---|---|---|
| P-B1 (`if rec.na = rec.nb then`, equal extents 3/3) | ACCEPTS; PRIMARY **Form S** `21 *D(nb 0005) / 11 *D(na 0002) / 06 03 / 3E 03` (direct, CODE 65); competing **Form M** `21 *D(na) / EB / 21 *D(nb) / 06 03 / 3E 03` (staged, CODE 66); H-R refusal first-class | ACCEPTS, but as **NONE of the pre-registered forms**: `21 *D(LEFT cell 0002) / E5 (PUSH H) / 21 *D(RIGHT cell 0005) / D1 (POP D) / 06 03 / 78 (MOV A,B) / CD ?SCCCM / C2 fill -> 001D` (CODE 66, DATA 000C) | **HIT (verdict) / MISS (encoding)** — BOTH listed falsifiers fired: the parking is the [C141] STACK, not `EB` (H-M's literal extrapolation of [C333] is falsified), and the left operand is NOT materialized directly into DE (H-S's [E29C6] transfer is falsified); a SECOND surprise: the equal extents COLLAPSE to `MVI B,03 / MOV A,B` — no `MVI A` immediate anywhere in this head |
| P-B2 (`if rec.nb = rec.na then`) | ACCEPTS, B1's winner with the two member-cell relocations SWAPPED in their slots; falsifier: byte-identical relocations | E49B2 = E49B1's head with the FIRST `21` carrying `*D(0005)` (nb, now LEFT) and the second `*D(0002)` (na, RIGHT); whole-file `cmp -l` differs ONLY in the module-name bytes (raw 0x06/0x13/0x1c) plus the two swapped member-cell relocation records (raw 0x3a/0x3e/0x3f) | **HIT (relative clause)** — the written side selects the slot; (the absolute Form-S/M winner named in the row was wrong, as P-B1's MISS records) |
| P-B3 (`if rec.na = rec.s2 then`, 3 vs 2) | ACCEPTS, positional lengths `06 03 / 3E 02`; falsifiers inverted/min/max/refusal | ACCEPTS: `21 *D(0002) / E5 / 21 *D(0008) / D1 / 06 03 / 3E 02 / CD ?SCCCM / C2 -> 001E`; CODE 67 — the two immediates return because the extents DIFFER (no collapse); head = B1's winner with `3E 02` inserted (18 bytes) | **HIT (verdict + positional pair)** / the form clause rides on B1's actual winner (stack form, not S/M) |
| P-B4 (`if rec.s2 = rec.na then`) | ACCEPTS, B3's pair SWAPPED with the operands: `06 02 / 3E 03`; falsifier: identical to B3 (class-keyed) | ACCEPTS: `21 *D(0008) / E5 / 21 *D(0002) / D1 / 06 02 / 3E 03 / CD ?SCCCM / C2 -> 001E`; CODE 67 | **HIT** — positional law confirmed on an all-member pair; min/max/class falsifiers all FALSIFIED by the data |
| P-B5 (`if rec.na ^= rec.nb then`) | ACCEPTS, B1's winner head verbatim, skip **CA**, fill = next statement (001C under H-S, 001D under H-M) | E49B5 = E49B1 with `0xca` at 0014 and the SAME fill `001D` (the actual 17-byte head lands on the H-M address); module-name bytes + the skip byte + its record checksum are the ONLY diffs (`cmp -l` raw 0x05/0x13/0x1b/0x52 — the digit pair `1`/`5` packs one bit lower in the name fields than `1`/`2`) | **HIT (verdict + CA byte + [C309] fill)** — the skip byte is CA in the STACKED member-vs-member head too |

## 2. Laws read out of the `.REL` records

1. **A member-vs-member FIXED compare in TEST is ACCEPTED through `?SCCCM`, and its two
   cell addresses PARK ON THE STACK.** E49B1 0006: `LXI H,*D(left cell) / PUSH H /
   LXI H,*D(right cell) / POP D / MVI B,<len pair, §2/§3> / CALL ?SCCCM / skip`. The load
   ORDER is the written order (left first — [C334]'s family continues), the FINAL registers
   are [C191]'s (HL ends on the RIGHT operand, DE on the LEFT), but the parking MECHANISM
   is the [C141] stack pattern, not [C333]'s `EB` staging: both listed forms are falsified.
   `XCHG` remains the parking of a member-left compare whose OTHER operand is a POOLED
   LITERAL (E49A1/A2/A3/A4); when BOTH operands are internal cells DR parks through
   `PUSH H`/`POP D` — the same choice the varying family made for both-load pairs
   (E34C5/C6/C7). No mechanism is claimed beyond what the six objects show.
   `golden/e49p2/E49B1/E49B1.REL` (CODE 66, DATA 000C).
2. **EQUAL EXTENTS COLLAPSE: `MVI B,<extent> / MOV A,B` (`06 n / 78`) replaces the two
   immediates.** Measured in THREE objects (E49B1/B2/B5, both extents 3). When the extents
   DIFFER (E49B3/B4) the head carries the two explicit immediates and the head is one byte
   LONGER (18 vs 17). SCOPE WARNING: every equal-length fixed object so far is
   member-vs-member; whether `?SCCCM` collapses a member-vs-LITERAL pair whose literal
   length EQUALS the extent is UNMEASURED ([TBD]) — E48E7/E49A1/A2/A3 (2 vs 3) and E49A4
   (3 vs 4) have never met an equal pair. The literal template keeps its two immediates.
3. **The positional length law [C334] survives on an ALL-MEMBER pair: `MVI B` carries the
   LEFT operand's declared extent, `MVI A` the RIGHT's.** E49B3 `06 03 / 3E 02` (na 3 left,
   s2 2 right); E49B4 `06 02 / 3E 03` — the pair SWAPS with the operands. The falsifier
   readings are eliminated by the data: MIN (`06 02 / 3E 02`), MAX (`06 03 / 3E 03`) and any
   class-keyed polarity. This is the first evidence where BOTH attributes are extents —
   [C334] was measured on member-vs-literal pairs only.
4. **The written side selects the relocation slot.** E49B1 vs E49B2 differ ONLY in the
   module-name bytes and the two swapped member-cell `*D` relocations (first `LXI H` slot
   = LEFT operand's cell, second = RIGHT's) plus record checksums: the encoding is not
   orientation-blind, and a byte-identical inversion would have falsified §3 — it did not.
5. **`^=` skips with `CA` in the stacked head too.** E49B5 0014 = `0xca`, fill = next
   statement `001D` ([C309]); extends [C333] §2.5 (measured there member-vs-literal) to the
   member-vs-member form. `golden/e49p2/E49B5/E49B5.REL`.
6. **Sizes and layout:** equal-extent head 17 bytes -> CODE 66 (0x42, the same total as
   E49A1 by coincidence: `E5 + D1` costs one byte more than `EB`, the collapse saves one);
   unequal-extent head 18 bytes -> CODE 67 (0x43). DATA 000C in all five objects —
   `'K='@0000, na@0002, nb@0005, s2@0008, k@000A` — [C314]'s pool-first layout, no compare
   literal pooled.

## 3. What this round did NOT measure

- **Any BARE spelling in a member-vs-member compare** — every probe writes BOTH members
  qualified; bare-bare, bare-qualified and qualified-bare pairs are `unmeasured` and keep
  refusing (the P1 asymmetry — bare admitted LEFT-of-literal only — is untouched).
- **The equal-extent collapse for member-vs-LITERAL pairs** (§2.2 scope warning): no fixed
  object with literal length == extent has ever run.
- `?SCCCM` in a **STORE** (either orientation) and any fixed-member store value — no
  object; the STORE routes keep refusing.
- **Literal-vs-literal** fixed compares; any **BASED** member in a condition — no object.
- **Truthiness of a FIXED member** — [C332] measured only the VARYING `BIT REQ`; stays
  `unmeasured`.
- **Over-extent** in a member-vs-member pair (both attributes are DECLARED extents here)
  and over-extent INITIAL/STORE — still `unmeasured`.
- **Relations beyond `=` and `^=`** (`<`, `>`, `<=`, `>=` on member pairs): never probed;
  the numeric-arm guard still declines them.
- **`^( ... )` composition** over any compare — out of scope, unmeasured.
- **No runtime semantics**: judged on `.REL` bytes only, so **no `spec/RUNTIME.txt` row
  may come from this round**. What `?SCCCM` DOES with unequal B/A at runtime (who pads or
  truncates) is not claimed.

## 4. Classification (PROTOCOL #3)

All five rows: **`my-gap`** — DR accepted everything (5 ok / 5, both passes clean) and my
baseline at `7fa763b` refused all five (`BASELINE-MINE.txt`). NO `dr-refuses` this round;
H-R stays a falsified hypothesis (kept above as written, PROTOCOL #2).
