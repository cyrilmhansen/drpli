# E2E-49/P1 — RESULTS (operand-inverted FIXED compares, E49A1..E49A4)

## 0. Lineage

- Probes + `mkprobes.py` + `HYPOTHESES.md` + `BASELINE-MINE.txt` committed BEFORE any oracle
  call at **`9b3d860`** (`git log --format=%h -- probes/E49A1.PLI | tail -1`); the
  prediction-SHA fill-in commit is its child, `0e9cc3d`, and is also an ancestor of the run.
  `golden/e49p1` did not exist before the run (verified with `ls` at both commits).
  Every emitted probe line is <= 71 columns; files are CRLF + `^Z` ([C193] (b)).
- One oracle call, exactly as pre-registered:
  `PLI_SRC=probes python3 oracle/batch.py E49A1 E49A2 E49A3 E49A4 --tag e49p1 --switches '$L$D'`
  -> **4 ok / 4** (`golden/e49p1/`, `summary.txt`). NO refusals: the whole inverted family is
  admitted, so nothing here is `dr-refuses`; every gap this round opens is a `my-gap`
  (my baseline refused all four, `BASELINE-MINE.txt`).
- All four `.PRN`s print `NO ERROR(S) IN PASS 1` and `NO ERROR(S) IN PASS 2`. Verdicts and
  laws below are judged on the `.REL` bytes read with
  `spec/lab-evidence/e2e42-p2b/chaindump.py` and `tools/reldump.py`, never from a `.PRN`
  (PROTOCOL #6) — the `CODE SIZE = 0042` lines agree with the objects (66 = 0x42) but the
  objects are the authority.

## 1. Prediction vs verdict (every MISS kept)

| id | predicted | measured verdict | score |
|---|---|---|---|
| P-A1 | ACCEPTS; PRIMARY **Form II** `21 *D(pool) / 11 *D(member) / 06 02 / 3E 03`; candidates Form I (= E48E7 verbatim) and Form III (`21/11/06 03/3E 02`); listed falsifiers: XCHG anywhere, new helper, refusal | ACCEPTS, but as **NONE of the three forms**: `21 *D(member 0004) / EB / 21 *D(pool 0000) / 06 03 / 3E 02 / CD ?SCCCM / C2 fill -> 001D` (CODE 66, DATA 000B) | **HIT (verdict) / MISS (encoding)** — the `EB` falsifier fired (member-left STAGES through XCHG, exactly [C191]'s varying clause) and the length pair landed in the Form-III registers but with the Form-I addresses |
| P-A2 | ACCEPTS, bytes identical to P-A1's winner (bare spelling invariance, [C253]/[C258]/[C318]) | E49A2 is whole-file byte-identical to E49A1 except the THREE module-name field bytes (raw offsets 0x06, 0x13, 0x1c — the final char of `E49A1` vs `E49A2` inside the bit-packed LINK-PROG-NAME / LINK-EXTDEF / LINK-DEF-PUBLIC records) | **HIT** |
| P-A3 | ACCEPTS, head identical to A1, skip byte **CA** ([C072] everywhere; arm 4's synthesis) | E49A3 0006..0016 = A1's head verbatim, `0xca` at 0014, skip filled to `001D` — the next statement ([C309]) | **HIT** |
| P-A4 | VERDICT-UNKNOWN, leaning ACCEPTS; if accepted A1's form with the literal length 4 (under a position law the pair is `06 03 / 3E 04`); falsifier: refusal, or a TRUNCATED pool literal | **ACCEPTS**, `21 *D(name 0006) / EB / 21 *D(pool 0000) / 06 03 / 3E 04 / CD ?SCCCM / C2 -> 001D`; DATA 000D with the FULL `'ABCD'` at 0000..0003 — no truncation; frame shifts: name@0006, nxt@0009, k@000B ([C314] pool-first layout) | **HIT (verdict) / HIT (the position-law byte pair)** |

## 2. Laws read out of the `.REL` records

1. **A FIXED member on the LEFT of a literal in TEST is ACCEPTED, staged through `XCHG`.**
   E49A1 0006: `LXI H,*D(member cell) / XCHG / LXI H,*D(pooled literal) / MVI B,<extent> /
   MVI A,<literal length> / CALL ?SCCCM / skip`. [C191]'s FINAL-register law survives the
   inversion — HL ends on the RIGHT operand (the pool literal), DE on the LEFT (the member)
   — and its clause "a member needs `XCHG` only when it is the left operand" is now measured
   for the **FIXED class with *D operands on both sides**: the staging is an ORIENTATION law,
   not an artifact of the varying family's `21 *S(lit)` symbol-pool loads (E48C9).
   [C326]'s literal wording "LXI H carries the internal cell" survives only as the statement
   about the FIRST load; the loaded cell then MOVES to DE. CODE 66 = E48E7's 65 + the one
   `EB`.
2. **The two length immediates are POSITIONAL: B carries the LEFT operand's attribute, A the
   RIGHT's.** Four objects, one law: E48E7 (literal left: `06 02` = literal len; member
   right: `3E 03` = extent); E49A1/A3 (member left: `06 03` = extent; literal right:
   `3E 02` = len); E49A4 (member left `06 03`, 4-char literal right `3E 04`). This
   **FALSIFIES [C330]'s class-polarity reading** ("A is the destination/capacity, B the
   source length", carried over from [C191]/[C197] stores) as a compare law: what C330
   described was a positional coincidence of its single sample. The varying family obeys the
   same positional law already measured: ?SCVCM literal-right keeps its length in A
   ([C318] E48C9), ?SCCVM literal-left in B ([C191] E48D10) — five compare objects, one rule.
   The correction is APPENDED at [C330] with the falsified text kept as written (PROTOCOL #2).
3. **The helper NAME does NOT flip with orientation in the fixed pair.** `?SCCCM` serves
   member-left and member-right alike. [C191]'s "the helper name says what the LEFT operand
   is" applies to the POSITION of the `V` (which operand is VARYING), not to member-vs-literal
   side: the `CC` pair names two fixed-class operands and carries no orientation.
4. **Spelling invariance for the inverted fixed compare.** E49A2 (`if name = 'AB'`) is
   byte-identical to E49A1 (`if rec.name = 'AB'`) except the module-name bytes — the
   [C253]/[C258] one-key-one-cell fold is invisible to DR's compare encoding, extending
   [C318]'s E46K3 corroboration (VARYING, TEST) to the FIXED class. NOTE the scope: this is
   the MEMBER-LEFT orientation; a BARE fixed member on the RIGHT of a literal still has no
   object (E48E7's qualification gate stays the only witness there).
5. **`^=` in the `?SCCCM` family skips with `CA`.** E49A3 0014 = `0xca`, fill = next
   statement 001D ([C309]). This converts arm 4's recorded [C072] SYNTHESIS (the `^=` of the
   literal-left form had no object) into a MEASURED law — in the inverted form.
6. **An over-extent literal in a fixed compare is ACCEPTED with the literal POOLED WHOLE.**
   E49A4: `'ABCD'` occupies DATA 0000..0003 untouched, `MVI B,03` (extent) / `MVI A,04`
   (literal length) travel side by side, CODE is the same 66 bytes. This answers the [TBD]
   recorded in `str_cmp_shape_fix`'s comment (ungated arms, "DR's verdict was never sampled")
   for the member-left orientation: DR does not refuse and does not truncate. The
   literal-LEFT over-extent compare keeps its ungated template — that verdict is still an
   extrapolation ([TBD], §3).

## 3. What this round did NOT measure

- `?SCCCM` in a **STORE** (either orientation), and any fixed-member **store value** — no
  object; the STORE routes keep refusing.
- **Member-vs-member** compares of any kind; **literal-vs-literal fixed** compares; any
  **BASED** member in a condition — no object.
- **Truthiness of a FIXED member** (`if rec.name then`) — [C332] measured only the VARYING
  member's `BIT REQ`; the fixed spelling stays `unmeasured`.
- A **BARE fixed member on the RIGHT** of a literal in TEST (§2.4 note): measured bare only
  on the LEFT.
- **Over-extent in the literal-LEFT orientation** and over-extent **INITIAL/STORE**: excluded
  by design, still `unmeasured`.
- `^( ... )` composition over any compare — out of scope, unmeasured.
- **No runtime semantics**: judged on `.REL` bytes only, so **no `spec/RUNTIME.txt` row may
  come from this round**. What `?SCCCM` DOES with B/A at runtime (who truncates, who pads)
  is not claimed.
