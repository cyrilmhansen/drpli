# E2E-10 ASSESSMENT (research only) — FLOAT BINARY(24) vs the four "isolated perimeters"

Date: 2026-10-20.  Implementation baseline: `4bc9af8` (+1,578 gross lines through
`07ff3ce`).  **This assessment adds ZERO `ocaml/`, `tools/` or `oracle/` lines**
(verified: `git diff --stat -- ocaml/ tools/ oracle/` empty before commit).  Its
evidence is oracle-only: DR re-runs of 2 corpus programs (FLTPOLY, FFACT) and 5
new minimal probes (R3001-R3005) compiled with `$L$C$D` so every listing carries
DR's instruction-level trace.  Goldens: `golden/e2e13/`, sources `e13src/` (new
provenance directory; nothing duplicated from `e12src/`/`e12b/`).

---

## 0. Correction first: DECPOLY has no DR semantic defect

Committed separately as `3bf2e77`.  I had claimed DECPOLY's caller declares
`FIXED DECIMAL(11,2)`, that P re-declares `(15,4)`, and that `P(x,y,z)` therefore
prints `2` wrongly.  Both halves were false and neither was checked against the
source: lines 11 and 27 both read `(x,y,z) fixed decimal(15,4)` (DR's listing
confirms both), and the `2` is the program's own string literal
`put skip list('       2');` at line 20 — P's value prints `12.2300`, exactly
`1.4*1.4 + 2*2.3 + 5.67`.  Object-level check of the accepted `.REL`: every
`MVI A,<p>` precision site is 15 on both sides; there is no `0x0B` anywhere.
Standing rule adopted: any "DR is wrong here" assertion must quote the source
line in the same breath.

---

## 1. The first-blocker labels were misleading — again

Each of the four "isolated perimeters", and three of the eight "FLOAT" programs,
is really gated by something much larger than the refusal my build reports.
Evidence is the program's own DR object (external-reference set + trace) plus a
read of its source.

| program | my first blocker | what it actually needs (DR object evidence) | verdict |
|---|---|---|---|
| A | `FLOAT BINARY(24,0)` decl | **external procedure** `procedure(x) returns (float)` — multi-module surface (`?FD44M ?FPRET`, 15-byte stub module) | not a float win |
| DTEST | `FLOAT BINARY(24,0)` decl | **`entry(fixed(7),float)`** + `call div2(...)` CALL statement (`?FX44M ?QFCMS ?DIV2`) | not a float win |
| FDTEST | `FLOAT BINARY(24,0)` decl | **`entry(...)`** + `fdiv2` external (`?QFCSS ?FDIV2`) | not a float win |
| ANNUITY | `FLOAT BINARY(24,0)` decl | **18 new routines incl. `LOG`, `?FEX15`, `?FCEIL`, `?FN40S`, `?RECOV`**, FILE/ON-condition | transcendental + condition family |
| LABELS | `codegen: undeclared x` | **label variables** `(x, y, z(3)) label`, `goto`, arrays `z(i) = c(i)`, `call P(lab2)`, ON-unit (`?RECOV`) | deep: labels + goto + arrays |
| OPTIMIST | `PUT ITEM` | **character-varying family** (`?VS2AD ?VS3AD ?SMCVM ?SCCCM ?CXVVM ?SJSVM ?VEROP ?XL3OP`) + **arrays** `negative (1:nwords) character(8) varying static initial(...)` + `verify()` builtin | string + array family |
| SAMPLE | `returns(CHAR(10) VARYING)` | varying + **`upper()` builtin** + **unnamed `begin;` block** + `call output(c)` CALL statement + varying GET | string + block + CALL |
| FSCAN | `procedure gnt without formals` | varying + **`get edit(line) (a)`** (GET EDIT with edit-directed varying: `?EDTIV`) + nested procedure + `?SMVVM ?SCVCM` | string + GET EDIT |

Consequences: (a) the "cheap 4-program perimeter" does not exist — 3 of 4 need
the varying-character family and the 4th needs label variables; (b) the FLOAT
label on A/DTEST/FDTEST is an artefact of the declaration that happens first —
their real gate is ENTRY/EXTERNAL/CALL, i.e. the multi-module surface the user
already deferred; (c) a realistic FLOAT target is **FFACT, FLTPOLY, TEST**.

---

## 2. What FLOAT BINARY(24) actually is (observed, not inferred)

### 2.1 Value model — cheap, and already ~90% decoded from bytes I have

* Cell size **4 bytes**, and plain `float` == `float binary(24)`: R3001 places
  `f` at A(0008) and `g` at A(000C) with `dcl f float; dcl g float binary(24);`.
  FLTPOLY's `x,y,z` sit at A(002F)/A(0033)/A(0037) — stride 4.
* A float **literal becomes a 4-byte pool cell**, and the encoding decodes
  cleanly from three samples in two different objects:

  | literal | bytes | fit |
  |---|---|---|
  | 1.5 | `00 00 40 81` | (0x80\|0x40)·2^(129−136) = 192/128 = 1.5 |
  | 2 | `00 00 00 82` | 128·2^(130−136) = 2 |
  | 2.5 | `00 00 20 82` | 160·2^(130−136) = 2.5 |

  **SUPERSEDED BY STEP 1** (`e2e10-step1-float-model.md`, CLAIMS C100/C101).
  What step 1 established, with 60/60 pool cells reproduced byte-exactly by
  `tools/floatmodel.py`: little-endian 23-bit fraction in bytes 0..2 with an
  IMPLIED leading one, **sign in byte 2 bit 7** (not the exponent byte),
  characteristic in byte 3 with bias 129, `value = (-1)^s (1 + frac/2**23)
  2**(byte3-129)`; zero = all four bytes 0 and exponent byte 0 is a legal NORMAL
  characteristic (so zero is a special case, not exp 0); range |v| in
  [2**-129, 2**127) with anything outside rejected in pass 2 with `CONVERT`
  (1E39, 1.8E38, 1E-45, 1E-60 rejected; 1E38, 1.6E38, 3E-39, 2E-39 accepted);
  no subnormals; no negative zero (`-0.0` shares the zero cell); literal rounding
  = nearest with **ties away from zero**, pinned by exact integer ties
  (16777217->16777218, 16777219->16777220, and both negatives), which EXCLUDES
  round-half-even and round-toward-+inf; literals are taken exactly and DR reads
  >=16 significant digits; literal cells precede variables in the data area, are
  allocated in first-use order and deduplicated by identical bytes; every float
  variable is 4 bytes including `float binary(14)`.
  The byte-order caveat above is resolved: `0.1` -> `cd cc 4c 7d` exercises all
  three fraction bytes at once, and 2**-16 / 2**-23 land in byte 0 as predicted.
  What step 1 did NOT settle is listed in C101's UNRESOLVED block (operand-mode
  suffix rule, binary(14) computed precision, runtime tie direction).

### 2.2 Lowering — the DEC machinery transfers surprisingly well

| route | DR sequence (traced) | relation to accepted DEC law |
|---|---|---|
| store to cell | `LXI H,*S(lit) / PUSH H / LXI H,<dst> / POP D / CALL ?FX44M` | new operand-address convention (both operands are ADDRESSES in DE/HL) |
| read + store | `... CALL ?FA44M / CALL ?FX44S` | ?FX44S = "store top of float accumulator to HL cell" (DEC `?DSTOP` analogue) |
| add / sub / mul / div | `?FA44M ?FS44M ?FM44M ?FD44M` (M form), plus `?FA44S ?FA44L ?FM44S ?FD44S ?FD44R ?FS44R` seen in other objects | **the operand-mode suffix (M/S/L/R) is the real puzzle** — exactly the question that cost the 25-probe divide round (C086) |
| fixed → float | `LHLD i / CALL ?QI15F / CALL ?FX44S` | parallels DEC `?QDI15` direction |
| float → fixed | `CALL ?FL40M / CALL ?QFI15 / SHLD i` | `?QFI15` is the DEC `?QDI15` counterpart |
| compare | `LHLD/LXI H,a / PUSH H / LXI H,*S(b) / POP D / CALL ?FC44M` then relation via push order + skip jump | **identical law to C085** |
| `&` conjunction | `SUI 01 / SBB A`, `PUSH PSW`, `POP B / ANA B`, one `JP` | **identical to C095, verified in FLTPOLY @0064-0083** |
| numeric GET | `?SYSIN / ?GNVOP / JP / ?QCXOP / ?QX8F4 / LXI H,<cell> / CALL ?FX44S` | **C088's skeleton verbatim**, only the conversion tail changes |
| PUT | `MVI A,0E / CALL ?QFCMS` (memory operand) or `CALL ?QFCSS` (stack/call result), then `?PNVOP / ?QIOOP` | C090's editing tail; width byte is a **constant 14** for both forms (not a precision) |
| multi-arg call descriptor | `LXI D,X A(0041) / MVI C,06 / MOV A,M / INX H / STAX D / INX D / DCR C / JNZ` | **byte-identical ABI to DECPOLY (C093)** — float formals are also 2-byte pointer cells, stride 2 |
| float return | `JMP ?FPRET` | parallel to `JMP ?DCRET` (C084) |

So of ~10 lowering routes, **4 are already banked laws** (compare, conjunction,
GET skeleton, call ABI), **2 are near-mechanical substitutions** (PUT tail,
return), and **the genuinely new surface is the value model + the operand-mode
selection rule + the two conversions**.  Routine names are NOT my cost.  **Directly verified:** DR's own
FLTPOLY/FFACT/TEST `.REL` files link to `.COM` against the stock PLILIB with no
user library (`linkrun.py link --tag e2estagedr3` -> `COM=True` for all three),
which proves every one of the 13 new names resolves inside PLILIB.  My `.REL`
only references them through CHAIN-EXT, so FLOAT adds **zero** bytes of runtime
I would have to write — the same situation as DEC.

### 2.3 Union of new routine references

* FFACT 5: `?FL40M ?FM44S ?FPRET ?QFCSS ?QI15F`
* FLTPOLY 9: `?FA44L ?FA44S ?FC44M ?FM44M ?FPRET ?FX44S ?QCXOP ?QFCSS ?QX8F4`
* TEST 8: `?FC44M ?FL40M ?FPRET ?FX44M ?FX44S ?QCXOP ?QFCSS ?QX8F4`
* **union 13.**  Varying-character union (OPTIMIST+SAMPLE+FSCAN) is 16, of which
  4 names (`?FX44S ?QCXOP ?QFCMS ?QX8F4`) also appear in float objects — so the
  two families share some conversion/editing machinery.  Which routine does what
  is NOT established; the overlap is a hint, not a law.

---

## 3. Pricing (calibrated on my own history, not route counts)

Gross `ocaml/`+`tools/` lines per accepted slice, measured from git:

| slice | content | gross |
|---|---|---|
| 7A-1 | DEC compare (C085) | 546 |
| 7A-2 | DEC divide + scale law (C086) | 1,028 |
| 7A-3 | ROUND (C087) | 324 |
| 7A-4 | numeric GET + MOD-in-condition (C088/C089) | 381 |
| 8-5 | PUT EDIT + DO/BY (C090-C092) | 624 |
| 9-6 | multi-arg ABI + DEC formals + `&` + %replace (C093-C099) | 956 |

**FLOAT subset (FFACT → FLTPOLY → TEST).**  Value model (6-8 probes + a Python
model like `tools/decmodel.py`), operand-mode rule (est. 12-20 probes, this is
the risky one), 2 conversions, PUT/GET tails, cell sizing for a new declaration
kind (the PARSER already parses `float binary(24)` — my refusal is raised in
codegen, so this is a `bind`/`codegen` change, not a grammar change).  Estimated
**900-1,400 gross lines, ~25-35 probes**, comparable to slice 7A-2 + 9-6.
Unlocks: **3 programs → 9/41.**  Runtime verification: needed and cheap per
specimen, but note **FFACT never terminates** (`do i = 0 repeat(i+1);` with no
test — same family as IFACT/LOAN1), so it requires the bounded-prefix protocol;
this was confirmed empirically by running DR's own FFACT image (1,415 bytes of
output, no natural exit).  FLTPOLY needs a real GET input script.  Float
printing is highly distinctive — DR emits E-notation with seven fraction digits
(`Factorial(         0 )=  1.0000000E+00`, `...  2.4000000E+01`, observed
value-by-value correct against `math.factorial`), so console equality is a
strong test rather than a formality, AND FFACT carries a free arithmetic oracle
(`math.factorial`) exactly like IFACT's `FACTS` check did.
Risks: (a) operand-mode law may hide a rule the way `s - i` hid C092 and the
peepholes hid C099; (b) precision variants (`float binary(14)`, long float) are
unsampled → must be guarded, so my subset is honestly "float binary(24) only";
(c) 5 of the 8 FLOAT-labelled programs do NOT unlock from this work (entry /
external / FILE / transcendental).

**VARYING-CHARACTER subset (alternative).**  Value model is *two* numbers per
string (current length + max) plus storage layout plus `STATIC INITIAL` tables;
~10 lowering rules all new; OPTIMIST additionally needs **arrays**, SAMPLE needs
**unnamed BEGIN blocks + UPPER + CALL statement**, FSCAN needs **GET EDIT**.
Unlocks realistically **1-2 programs (FSCAN, maybe SAMPLE)**, not 3.  Same
ballpark of lines as FLOAT for a third of the payoff.  Worse trade.

**FILE (context, not proposed).**  14 programs share one declaration kind, but it
is the whole I/O runtime (buffers, FCB, open/close/read/write statements) — a
project of its own, and the largest remaining wall after FLOAT.

---

## 4. Recommendation

**Next implementation milestone: E2E-10 = FIXED FLOAT BINARY(24), landing
FLTPOLY as the acceptance target, with FFACT as the first internal checkpoint.**

Reasoning: FLTPOLY is DECPOLY's structural twin — same `%replace`, same
`do while('1'b)`, same counted `PUT SKIP(2)`, same 3-way `&` decimal… float
compare, same GET skeleton, same 3-argument by-reference descriptor block — so
everything the last slice banked (C093/C094/C095/C097) is reused byte-for-byte,
and the *only* new family is the float value model plus operand-mode selection.
FFACT goes first because it is the cheapest probe-rich slice of that model (5
routine names, no GET, no conjunction) and it exercises conversion in both
directions plus recursive float return; TEST lands last for float compare +
nested IF/ELSE coverage (ELSE is already byte-proven by 7 registered positives,
`DO ... REPEAT` by 21 including RFACT and DFACT — so neither is new work).

Sequencing suggestion inside the milestone: (1) value-model probes + decoder
model, no compiler change; (2) assignment/store/literal subset verified against
R3001/R3002/R3003; (3) FFACT; (4) FLTPOLY; (5) TEST.

**Budget note.**  Implementation since `4bc9af8` is +1,578 gross and the
consultation threshold is ~2,000, so FLOAT *cannot* land inside the current
budget: expect to cross it during step (2)/(3).  Recommend either an explicit
mid-slice checkpoint at ~+1,000 lines, or scoping this budget window to
steps (1)+(2) (model + probes, ~150 lines of `tools/`) and starting the compiler
work in a fresh window.

**Per user instruction, C099 stays as tested fail-loud refusals** (N56-N60) —
no fixed-bin peephole is implemented, and the corpus is unaffected because no
corpus program uses those shapes.
