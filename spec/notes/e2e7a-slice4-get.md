# E2E-7A slice 4 — numeric GET (?QCDOP / ?QCIOP), MOD-in-condition, LOAN1 accepted

STATUS: COMPLETE. LOAN1 is accepted at RAW .REL byte parity, byte-identical
linked .COM, and byte-equal console output under the bounded complete-record
prefix protocol, with its 27-row schedule independently re-computed in Python
`decimal`. This is the 4th historical corpus program accepted after DEMO,
RFACT and DFACT.

Baseline for line counting is `3636eec` (slice 1). Measured over `ocaml/`,
`tools/` and `oracle/` (implementation, not notes/goldens), the working tree at
the end of this slice is **+1,408 / -180 = 1,588 gross lines since 3636eec**,
of which slice 4 itself is **+248 / -48 = 296 gross** (compiler +125/-31,
tools +108/-17, oracle +15/-0). That leaves ~412 lines before the ~2,000-line
consultation checkpoint, so no mid-slice pause was required.

Counter reconciliation (the previous report said "+1,190/-162" for the first
three slices): recomputing the same path set at `cb8bb44` now gives
+1,168/-140. The earlier figure was taken against a slightly different working
tree before the slice-3 commit. The numbers in this file are the recomputed
ones, from one command, so the series is internally consistent.

---

## 1. What slice 4 was asked for, and what it actually needed

The slice was scoped as "numeric GET". LOAN1's sole remaining unseen PLILIB
route was `?QCDOP` (1 of 23). After GET landed, LOAN1 still refused, at:

    if mod(m,12) = 0 then          ->  (?QCDOP done) [TBD] condition form

so this slice also carries FIXED BINARY MOD used as a condition, which needs
**zero new routines** (`?IMDOP` was already banked from P071B). Both pieces
are reported together because neither alone completes LOAN1; nothing else was
touched. PUT EDIT, FILE, FLOAT, general GET formatting, DEC formal parameters
and multi-module work remain out of scope and still refuse.

## 2. Probes

17 probes generated and DR-compiled with `$L$D$C$S` into `golden/e2e10/`
(sources `build/e10/R9xx.PLI`, registered copies `probes/R9xx.PLI`, all CRLF +
CP/M EOF):

| probe | shape | result |
|---|---|---|
| R901 | `get list(p)` into `dec(11,2)` — LOAN1's own declaration | byte-exact |
| R902 | two separate GETs, `dec(9,2)` then `dec(6,4)` — does B track each target scale | byte-exact |
| R903 | `get list(i)` into `fixed binary` — the non-decimal route | byte-exact |
| R904 | `get list(i, a)` — mixed BIN then DEC in ONE list, ordering | byte-exact |
| R905 | `get list(d)` into `dec(9,0)` — scale 0: is `MVI B,00` emitted at all | byte-exact |
| R906 | `get list(x)` into `dec(15,3)` — the ceiling precision | byte-exact |
| R907 | `get list(p)` with EOF on the first item — skip path | byte-exact |
| R908 | `if mod(i,12) = 0 then … else …` — constant divisor, both arms | byte-exact |
| R909 | `if mod(i,d) = 0` — VARIABLE divisor | byte-exact |
| R910 | `if mod(i,12) ^= 0` — the `<>` sense | byte-exact |
| R911 | `if mod(i,12) = 0 then do; … end;` — THEN block, no ELSE | byte-exact |
| R912 | `do while (dec > 0)` wrapping `if mod(m,12) = 0 then do;` — LOAN1's loop skeleton | byte-exact |
| R913 | `dcl a fixed; get list(a)` — promoted from negative N1_GET | byte-exact |
| R914 | `dcl i fixed binary; get list(i)` — promoted from N17_GETINT | byte-exact |
| R915 | `get list(a, i)`: char **varying** then binary | byte-exact |
| R917 | `get list(a, b)`: two char varying items — promoted from N18_GET2 | byte-exact |
| R916 | `get list(a, i)` into **FIXED** char `char(4)` | REFUSED by design; DR golden kept as route evidence [N44] |

16 registered byte-exact positives, 1 designed refusal. Every positive is also
linked: `.COM` byte-identical to DR's linked `.COM`, and console transcripts
byte-equal (see §6).

## 3. The input skeleton (shared by every target kind)

X201/X202 (char varying) had already pinned the skeleton; R901-R917 show it is
*identical* for numeric targets, i.e. GET is one template with a per-item
conversion tail:

    LXI  D,0290          input descriptor (0252 is the PRINT one; never relocated)
    LXI  B,0000          operand triple-patched to the NEXT statement
    CALL ?SYSIN
    --- per item, in source order ---
    CALL ?GNVOP
    JP   <skip>          F2; operand triple-patched, see below
    <conversion + store for this item>
    --- end per item ---
    CALL ?QIOOP          once for the whole statement

Two laws the probes newly establish:

* **One `?GNVOP`/`JP` pair per item**, not per statement. Item k's JP operand
  is patched to *whatever follows that item's store* — the NEXT item's
  `?GNVOP` [R904 `0013 ==== 001B`, R915 `0013 ==== 001D`, R917 `0013 ==== 001D`]
  or, for the last item, the closing `?QIOOP` [R907, X202]. A skip therefore
  abandons the remaining items of the list while still completing the I/O
  call, and the LXI B continuation always points past the `?QIOOP`.
* **A skip (EOF) abandons the remaining items of the list** while still
  completing the I/O call, and the LXI B continuation always points past the
  `?QIOOP`. R907 (`p = 7;` then `get list(p)` with EOF as the whole script)
  pins the structure byte-exactly: `JP` -> `0032` = the `?QIOOP` call, so the
  `?QCDOP`/`?DSTOP` store chain is bypassed.
* **Runtime at EOF is observed but is NOT what I first assumed.** R907's
  transcript is 2 bytes (`^Z`, the echoed EOF) in BOTH arms, and LOAN1's
  transcript likewise ends at `Principal ^Z`: after an EOF on GET nothing
  further is printed, so "the target keeps its previous value" is a
  structural inference from the skipped store chain, not a runtime fact I am
  entitled to claim. My first draft of this note asserted the runtime version;
  corrected here.

## 4. Per-item conversion, by destination kind

| target | DR sequence | evidence |
|---|---|---|
| `FIXED DEC(p,s)` | `MVI B,s` `CALL ?QCDOP` `LXI H,var` `MVI A,p` `CALL ?DSTOP` | R901-R906, R913, LOAN1 |
| `FIXED BINARY` (2-byte cell) | `CALL ?QCIOP` `SHLD var` | R903, R904, R914, R915 |
| `CHAR VARYING(cap)` | `LXI H,var` `MVI B,cap` `CALL ?SSVFS` | X201, X202, R915, R917 |
| `CHAR(n)` fixed | `LXI H,var` `MVI B,cap` `CALL ?SSCFS` | **R916 — observed, NOT implemented [N44]** |

The DEC rule in detail:

* **B is the TARGET SCALE**, taken verbatim from the declaration: 02 for
  `dec(11,2)`/`dec(9,2)`, 04 for `dec(6,4)` [R902], 03 for `dec(15,3)`
  [R906] — and **emitted even at s = 0** (`MVI B,00`, R905), so the `MVI B`
  is unconditional, not a specialization for scale.
* **A is the TARGET DIGIT COUNT** (0B for LOAN1's `dec(11,2)`, 0F for
  `dec(15,3)`) and the store is the ordinary `?DSTOP` used by every DEC store
  [C084].
* **No `?QDDSL`/`?QDDSR` appears anywhere in a GET** — the whole scale law of
  C086 is absent here, which means `?QCDOP` delivers the scanned field
  already at the target scale. GET is therefore the one DEC context where the
  producer fixes the scale instead of the consumer [C086 L5], and it does so
  without a shift because it never had a scale before.
* R901-R906 sample `dec(11,2)`, `dec(9,2)`, `dec(6,4)`, `dec(9,0)`,
  `dec(15,3)`, `dec(9,2)` — six GET shapes. Cell-size/pool consequences
  follow the existing cell law [C084]; nothing new is asserted about
  precisions that no GET probe touched.

## 5. MOD used as a condition (`= 0`, `^= 0`)

DR's shape (LOAN1 00CC, R908-R912):

    <dividend into HL>            e.g. LHLD M
    <divisor into HL, dividend parked in DE>
    CALL ?IMDOP                   remainder returns in HL
    MOV A,H / ORA L               HL-zero test
    JNZ /skip   for `= 0`         (taken iff the condition is FALSE)
    CA    /skip   for `^= 0`

* The **divisor form depends on the operand kind**, and this was invisible
  before: a *variable* divisor is `PUSH H / LHLD d / POP D` [R909 = P071B's
  proven path], while a *literal* divisor is `MVI A,k / PUSH H / MOV L,A /
  ADD A / SBB A / MOV H,A / POP D` [R908, R910, R911, R912, LOAN1] — the
  sign-extend ladder from C079, with the `MVI A` placed *before* the push and
  the push *inside* the ladder's setup. `LXI H,imm` (the store form, D6) is
  NOT used for a divisor.
* The `^= 0` skip byte is **0xCA while `$C` prints `JZ`** [R910, code 001C].
  That extends the C072 parity-defect family (integer var-literal `^=`, DEC
  `^=` [C085]) to a third context: DR's `<>` test always compiles to JPE,
  whatever sits in front of it. The `$C` mnemonic is not the oracle; the byte
  is.
* Only `= 0` and `^= 0` are proven. Other relations against a MOD
  (`> 0`, `<> k`, `mod = mod`) must refuse: a bare HL-zero test cannot
  express `> 0`, and emitting one would silently mis-lower. This is now a
  tested negative [N47].
* LOAN1's own semantics are confirmed at runtime, not just byte-wise: R912
  reproduces `do while (p > 0)` + `if mod(m,12) = 0 then do; y = y + 1; end;`
  and prints `2 1` (year increment fires once, at m = 0) — identical console
  bytes to DR's run.

## 6. Runtime verification (linked .COM + console)

All 16 positives: `.COM` **IDENTICAL** to DR's linked `.COM`, console
transcripts **BYTE-EQUAL** (raw bytes; no normalization, line endings and
echo preserved). Every probe ends in `stop;`, so each transcript is a
COMPLETE program output — no bounded-prefix protocol needed for the probes.

Representative transcripts (`input -> output`, mine and DR identical):

    R901  '500\r'        -> '500\r\r\n\r\n        500.00\r'
    R902  '1.25\r','3.1416\r' -> '1.25\r\r\n3.1416\r\r\n\r\n        1.25    3.1416\r'
    R903  '42\r'         -> '42\r\r\n\r\n       42\r'
    R904  '42,7.50\r'    -> '42\r\r\n\r\n       42         7.50\r'   (BIN then DEC, source order)
    R905  '17\r'         -> '17\r\r\n\r\n          17\r'             (dec(9,0), MVI B,00)
    R906  '1.234\r'      -> '1.234\r\r\n\r\n             1.234\r'    (dec(15,3))
    R907  '\x1a'         -> '^Z'   (2 bytes; store chain skipped, nothing printed after EOF)
    R913  '31\r'         -> '31\r\r\n\r\n       31\r'
    R914  '77\r'         -> '77\r\r\n\r\n       77\r'
    R915  'HELLO,42\r'   -> 'HELLO,42\r\r\n\r\n       42\r\nHELL\r'   (varying truncated to cap 4)
    R917  'ABCD,EFGH\r'  -> 'ABCD,EFGH\r\r\n\r\nABCD\r\nEFGH\r'
    R908  (no input)     -> '\r\n        1\r'   mod(24,12)=0 -> THEN arm taken
    R909  (no input)     -> '\r\n        2\r'   mod(25,12)=1 -> ELSE arm taken
    R910  (no input)     -> '\r\n        3\r'   ^=: THEN arm taken
    R911  (no input)     -> '\r\n        1\r'   THEN-block form
    R912  (no input)     -> '\r\n        2         1\r'  loop + mod test: m=2, y=1

**A process failure worth keeping.** My first pass added per-probe input
scripts to `oracle/linkrun.py` with `str.replace()` calls that silently
no-matched, so R913/R914/R915/R917 ran on the harness default EOF and printed
2 bytes (`^Z`). The gate still reported "console BYTE-EQUAL", because DR's arm
hit the same nothing. Equality of two empty captures is not evidence. The
scripts were re-added with an assertion and the four probes re-run to the
transcripts above; the numbers in this file come from the corrected run.

## 7. LOAN1 acceptance

`artefacts/LOAN1.PLI`, original text, unmodified, 4 agreed criteria:

1. **RAW .REL byte identity**: 1536 bytes, `cmp` clean against the historical
   corpus golden `golden/first8080u/LOAN1/LOAN1.REL` ✓. CODE 487 bytes,
   DATA 60 bytes, 17 pool items; the external-reference set is identical to
   DR's — all **23 of 23** PLILIB routes now emitted, `?QCDOP` last.
2. **Linked .COM identity**: 9984 bytes, byte-identical to the .COM produced
   by linking DR's own LOAN1.REL against the same PLILIB ✓.
3. **Console transcript**: LOAN1's outer `do while('1'b)` never exits, and its
   visible output ends at the scripted EOF (`... Principal ^Z`), with the
   harness reporting no clean exit -- verification therefore uses the bounded
   complete-record prefix protocol (`tools/prefix_check.py --console --records
   27`), NOT timeout truncation: my run captured 38 complete records, the kill
   point was derived from record 27, both arms were re-run with the same
   `--killon` boundary, and the first **27 complete records are byte-equal**
   (28 records captured in each bounded arm). The gate's own `--link-run` arm
   separately reports `.COM IDENTICAL` + `console BYTE-EQUAL (1085 raw bytes)`.
   (An earlier note claimed LOAN1 "terminates on scripted EOF, no bounded
   prefix needed" -- that was wrong; the protocol was needed and is what this
   criterion rests on.)
4. **Independent arithmetic**: `tools/loan1_verify.py` re-computes the
   amortisation from the source's own declarations with Python `decimal`
   (P = 500.00, i = 14.00, PMT = 22.10, `P = P + round(i*P/1200, 2)`,
   `if P < PMT then PMT = P`), and compares against the transcript:
   **27 rows, every (month, year, principal-before, payment) tuple matches**,
   final row 27 = 9.22 principal / 9.33 payment (residual payment, principal
   0 -> loop exits) ✓. The verification deliberately carries three variants
   of the interest term and reports disagreement instead of averaging it:
   full-precision-then-round MATCHES all 27 rows, truncate-at-5-then-round
   MATCHES all 27 rows, truncate-at-2-then-round DIFFERS in 23 rows. So the
   transcript proves `?DROUN` receives more than 2 fractional digits, which is
   consistent with C086 (the division's scale is set by the enclosing context,
   not by the eventual store target) and would have been impossible to see in
   R813's single-month probe. TIE-SENSITIVE rows between the matching and the
   rejected variant: 1 (row 27).

## 8. Defects caught before shipping

* **Over-broad condition pattern.** My first draft matched `Ast.EqR r` with
  `r` unrestricted, so `if mod(i,12) > 0 then` compiled *silently*, reusing the
  `^=` skip byte after a bare HL-zero test — a shape that cannot express `> 0`
  and would have produced wrong code for any future program that used it.
  Caught by probing the shape rather than assuming the refusal; fixed by
  narrowing the pattern to `Eq | Ne` and making `mod > 0` a tested negative
  [N47].
* **Vacuous console arm** (see §6) — fixed by asserting on the harness edit
  and re-running.
* Existing `emit_triple` takes the state argument; my first patch attempt
  mis-called it and the edit failed loudly instead of shipping.

## 9. Independent model

`tools/decmodel.py` extended with GET: `dr_tokens()` now tracks `MVI B`
alongside `MVI A` (QCDOP's scale arrives in B), and a `get list(...)` item
contributes `QCDOP:s` + `DSTOP:p`. Result over the slice-4 corpus:
**11/11 GET specimens SCHED MATCH, 0 DIFFER**. The 5 MOD-condition specimens
report MODEL-REFUSED (`compare operand 'mod(...)' unpinned`): the model tracks
the decimal stack only and deliberately does not model integer MOD, which is
recorded as a model-side limitation, not as coverage. For GET specimens the
value arm is reported `NUM n/a(get)` — a GET-fed variable holds whatever the
input script supplied, which the model does not read; claiming a value match
there would be a fiction. LOAN1's numbers are verified independently by
`tools/loan1_verify.py` (§7.4) instead.

Corpus-wide model state, reported with the exact command that produces it so
every number is reproducible:

    python3 tools/decmodel.py probes/R5*.PLI probes/R6*.PLI probes/R7*.PLI \
            probes/R8*.PLI probes/R9*.PLI
      -> 68 SCHED MATCH / 0 SCHED DIFFER
         30 VALUE-MATCH / 0 VALUE-DIFF
          8 MODEL-REFUSED  (3 pre-existing: decimal(i,15), f(3), g(n);
                            5 new: `compare operand mod(...) unpinned')

The slice-3 note quoted "9 named model-side refusals"; re-running that slice's
own file list (`probes/R5*-R8*`) reproduces 57 SCHED MATCH and 30 VALUE-MATCH
exactly but only 3 refusals, so the 9 figure was taken over a broader list I
cannot reproduce. It is superseded by the command line above rather than being
scaled up to keep an old total -- the same correction pattern as the DEC cell
law and the "0 crashes" claim.

## 10. Fail-loud perimeter after slice 4

Retired because they are now proven positives: **N1_GET** (`dcl a fixed`) ->
R913, **N17_GETINT** (`dcl i fixed binary`) -> R914, **N18_GET2** (two char
varying items) -> R917. Added, each a *tested* negative:

* **N44_GETFIXCHAR** — GET into `char(4)` fixed: DR uses `?SSCFS` [R916],
  unimplemented.
* **N45_GETSUB** — `get list(x(1))`, subscripted item: refuses before lowering.
* **N46_GET1BYTEBIN** — GET into a 1-byte `fixed bin(1)`: only the 2-byte
  `?QCIOP`/`SHLD` form is sampled; the 1-byte cell takes the 0x32/`STA` store
  form [C079] and DR's GET emission for it is unknown.
* **N47_MODGT** — `if mod(i,12) > 0`: MOD-in-condition proven only as `= 0`
  and `^= 0`.

Unchanged: DEC formal parameters [N33], PUT EDIT, one-argument ROUND [N36],
literal ROUND [N37], `?IROUN` [N38], non-literal ROUND digits [N39], ROUND
above operand scale [N40], simple-arg ROUND in `+/-` [N41], ROUND in
multiplicative position [N42], ROUND as divide operand [N43], plus the older
DEC-band and mixed-mode refusals. `get … EDIT/STRING`, `get … from stream`,
data/file GET variants and GET into based/pointer/float/bit targets all still
refuse (the parser rejects `get data(...)` before codegen; that perimeter is
parser-level, not codegen-level).

## 11. Gates

See the `GATES AFTER SLICE 4` block appended to `spec/CLAIMS.md` (C088/C089)
for the full-suite numbers; the e2e gate is 160 byte-exact / 0 fail of 160 and
the negative panel is 39/39. Full link+console regression over every registered
positive: section 14.1 of `spec/notes/corpus-audit-2026-10.md`.

## 12. What LOAN1 does NOT prove

* PUT EDIT (`?EDITF`/`?EDTOV`): LOAN1's puts are all PUT LIST. Still the next
  blocker for IFACT.
* DEC formal parameter passing [N33]: DECPOLY's problem, untouched.
* Fixed-char GET (`?SSCFS`) [N44], 1-byte binary GET [N46], subscripted/stream
  GET [N45], MOD relations other than `= 0`/`^= 0` [N47].
* Anything about EOF *inside* a multi-item list beyond what R907/R904 show:
  "the skip lands on the next item's GNVOP" is byte-pinned [R904, R915, R917];
  EOF behaviour is observed only for a single-item list, where the run's output
  simply ends at the echoed EOF [R907]. "The remaining items are abandoned" is
  a structural reading of the JP chain, not a runtime observation.
