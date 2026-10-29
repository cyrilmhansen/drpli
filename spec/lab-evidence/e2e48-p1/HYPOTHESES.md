# E2E-48/P1 — hypotheses and PREREGISTERED predictions

Written and committed **before** the DR oracle is invoked on any E48 probe, under
the rule PROTOCOL.md Part 1 #1 states and `../e2e42-p2b/HYPOTHESES.md:1-6`
restates: the committed blob, not a file mtime, is what proves ordering.
`RESULTS.md` section 1 must be a prediction-vs-verdict table over exactly these
rows, and every MISS stays in that table.

    git commit  <the commit that adds probes/E48A*.PLI and this file>
    git rev-parse HEAD   -- recorded in RESULTS.md as the prediction SHA

## What E2E-48/P1 is

The condition-form half of CREATE.  `tools/corpus_census.py` at HEAD `d609e01`
records `CREATE` as REFUSED with

    codegen: condition form not in E2E-3b subset [TBD]: (^ eofile)

and `../e2e42-p2c/RESULTS.md` §7 established that this is now CREATE's *only*
front-of-stream blocker: its whole PUT block lowers (`CREATE-PUT-BLOCK.PLI`, 4
`?SIOOP` / 3 `?SKPOP` / 4 `?QIOOP` / 0 `?SYSPR`), so the two remaining shapes are
`do while(^eofile)` (line 31), `eofile = (name = 'EOF')` (line 34) and
`if ^eofile then` (line 35).  Neither has ever been probed: the ledger has **no**
claim about a `^`-negated condition or about storing a condition into a BIT(1),
and PROTOCOL #4 forbids turning CREATE's witness into a rule without measuring.

Why this candidate and not the others on the shelf (the selection PROTOCOL asks
me to justify):

* **OPEN options** (COPY/ENTER/KEYFILE/UPDATE refuse on OPEN, RETRIEVE on
  `OPEN ... PRINT`) is 5 census programs, but each OPEN option is a whole macro
  expansion of its own and the P0 measurement (`spec/notes/e2e42-p0-*`) counted
  34 OPEN blocks in 24 objects without pinning PRINT/KEYED/UPDATE lowering.  Bigger
  and less bounded than this phase.
* **STATIC on CHARACTER** (EXPR2/FSCAN/LOAN2/MPMCALLB/REPORT) is 5 programs too,
  and its blocker is one layout question (a static varying cell's position in
  [C114]'s data area) — genuinely valuable, but it does not touch the condition
  subset that CREATE, RETRIEVE, DIOCOPY, DIORAND and MPMCALLA all need.
* **the `data=` summary line** (`../e2e42-p2c/RESULTS.md` §9) is a reporting
  defect; no object depends on it.  Lowest value of the four.
* The condition forms are **already half-pinned by DR objects in the tree** (below),
  so the predictions are derived, not guessed, and a MISS will be informative.

## The prior DR evidence (objects already in `golden/`, re-read for this file)

All byte readings below come from the `.REL` records through
`../e2e42-p2b/chaindump.py` and `tools/reldump.py`, never from a `.PRN`
([C264]); `tools/reldump.py` prints a RELOC's two operand bytes as a gap, so the
operand *values* here come from the later RELOC/SET-LC pairs that fill them.

1. **FLTPOLY2** (`golden/first8080u/FLTPOLY2/FLTPOLY2.REL`, a census EXACT) —
   `dcl eofile bit(1) static initial(false)` where `%replace false by '0'b`:
   the positive bare-bit test, `if eofile then stop`, at 0075:
   `3A <D(0000)> / B7 / F2 00 00 <chain>` = LDA dir, ORA A, JP + skip chain.
   `eofile = true` (the ON-unit body) at 0011: `2A <D(0000)> / 36 80` =
   `LXI H,cell / MVI M,80`, i.e. the `'1'b` high-bit store [C112].
2. **E30B5** (`golden/e30p1/E30B5/E30B5.REL`) — the BASED form of the same test:
   `LHLD p / LXI D,0003 / DAD D / 7E / B7 / F2 <chain>` for `do while(p->f)`, and
   `p->f = false` as `LHLD p / LXI D,3 / DAD D / 36 00`.
3. **CREATE** (`golden/first8080u/CREATE/CREATE.REL`, authenticated, NOT yet an
   EXACT) — the two shapes this phase is about:
   * `do while(^eofile)` at 0052: `3A <D(0000)> / B7 / FA` then the 5-byte skip
     chain, **8 bytes** (0052→0059).  The chain's operand is filled at 12460-12523
     by `SET-LC code 0057 / RELOC code 01C1`, and the chain body is written at
     01BE: `C3 <RELOC code 0052>` — `JMP <loop head>`, the back edge, reached
     when the test is FALSE (fall-through).  A second `SET-LC code 00A6 /
     RELOC code 01BE` shows the `if ^eofile` test shares that one tail.
   * `eofile = (name = 'EOF')` at 008F, **16 bytes** (008F→00A1):
     `2A <D(005A)> / EB / 2A <D(0035)> / 3E 03 / CD <chain ?SCVCM> / D6 01 / 9F /
     32 <D(0000)>` = load `name`'s varying descriptor, XCHG, load the literal's
     cell, `MVI A,03`, `CALL ?SCVCM`, then `SUI 01 / SBB A`, then `STA cell`.
     `SUI 01 / SBB A` (op_sui/op_sbb_a, 0xD6/0x9F) is **exactly [C095]'s flag
     trick** — NC-true ⇒ 0xFF, C-false ⇒ 0x00 — and the `STA` is 0x32 with the
     address inline-relocated, which [C079] already pins as DR's 1-byte store
     form whose `$C` rendering says `STA` while the byte is replicated.
     `initial(false)` and `eofile = (name = 'EOF')` therefore leave the cell as
     0x00/0xFF, **not** 0x80/0x00 like a bit-literal store: the two forms are
     different encodings of the same one-byte cell.

What these license and what they do not: they license the *instruction sequence*
predictions below, at 8 and 16 bytes.  They do **not** license any generalisation
to other condition classes (numeric, `<>`, `>`, negated) nor to `^(cond)` nor to
`&`-with-a-bit-operand — CREATE contains only the two instances above, and one
witness per shape is [C301]'s and [C302]'s standing lesson about over-reading a
single object.  Hence this bank.

## The predictions

Notation: `<X>` = a 2-byte inline DATA/COMMON reloc; `<chain>` = DR's 5-byte
skip chain (filler `00 00` at emit time, patched later by `SET-LC/RELOC` — see
E30B5 001F←0032 and CREATE 0056←01BE).  "size" counts bytes of the shape itself,
not the statement around it.

| # | probe | shape | PREDICTED DR lowering | basis |
|---|---|---|---|---|
| P1 | E48A1 | STATIC bit, `do while(^b);` | `3A <b> / B7 / FA <chain>` = **8 bytes** | CREATE 0052 |
| P2 | E48A2 | STATIC bit, `if ^b then ... else ...` | identical **8-byte** test head; the ELSE is reached through the chain, no second jump | CREATE 00A1 (same head; its chain shares the loop's tail) |
| P3 | E48A3 | STATIC bit, POSITIVE `if b then ... else ...` | `3A <b> / B7 / F2 <chain>` = 8 bytes, JP not JNZ (the sign test after `ORA A`) | FLTPOLY2 0075 |
| P4 | E48A4 | STATIC bit, `b = '1'b` and `b = '0'b` **as tests** | `3A / E6 80 [/D6 80] / ?? <chain>` -- the [C112] ANI(,SUI) ladder; **open**: the ledger records JNZ for these while P3's bare test is JP, so the skip byte is the discriminating question | [C112], E11D |
| P5 | E48A5 | **AUTOMATIC** (non-STATIC) bit in `do while(^b)` | same `3A/B7/FA`, 1-byte cell, AUTO STORAGE grows by **1** | RETRIEVE:17/34 and DIOCOPY:40/109 spell it and DR compiled both, but neither object is reproducible by this compiler yet (OPEN/BASED blockers), so the automatic bit cell's test is UNMEASURED here; [C114] for the layout |
| P6 | E48A6 | `b = (<char varying> = '<lit>')`, literal store first, **no GET** | `2A <v> / EB / 2A <lit> / 3E n / CD <chain ?SCVCM> / D6 01 / 9F / 32 <b>` = **16 bytes** | CREATE 008F |
| P7 | E48A7 | `b = (k = 0)` **and** `b = (k = 5)` on `fixed bin(15)` | `= 0`: **predicted** `2A <k>` + [C095]'s `bin_zero_tail` (`7E / 23 / B4 / D6 01 / 9F`) + `32 <b>`. `= 5`: **UNMEASURED**, may refuse. No object pairs either class with an STA | [C095] DECPOLY/R2021/R2025 |
| P8 | E48A8 | `b = (k ^= 0)` | the same materialiser with the `^=` relation; whether the [C072] `CA` defect can travel into a *materialising* operand (it is a skip-byte defect, so arguably not) is **open** | [C072], [C247] family |
| P9 | E48A9 | `b = (k > 0)` | **UNMEASURED**: [C095] pins `>` only as the FIRST operand of a FLOAT conjunction, where DR uses the raw compare byte and materialises nothing; a refusal (`COMP REQ ?`) is as informative as a lowering | [C095] |
| P10 | E48A10 | `f = (b = '1'b)` between two bit cells | **UNMEASURED**: the ANI/SUI ladder has never been materialised into a byte | [C112] |
| P11 | E48A11 | `b = ^(k = 0)` -- `^` applied to a STORED VALUE | **UNMEASURED**: CMA (0x2F) after the flag trick, an inverted compare, or a refusal | none |
| P12 | E48A12 | the COMBINATION: store the condition, then test its negation, in one loop | P1's 8-byte head **and** P6's 16-byte store and nothing new, if the shapes are independent | CREATE 0052+008F+00A1 |
| P13 | E48A13 | `if ^(k = 0) then` and `do while(^(n = 3))` -- `^` on a general condition | **UNMEASURED**: the corpus uses `^` on bit cells and inside strings only. A refusal is a `dr-refuses` row and keeps CREATE's path narrow | none |
| P14 | E48A14 | `if k = 0 & b then` -- a bit cell as a conjunction operand | **UNMEASURED**: [C095] has no bit operand and my `lower_bool` refuses it today. A one-byte cell cannot use the 2-byte `= 0` tail, which is why DR's bytes are needed | [C095] |
| P15 | E48A15 | `put list(b)` | **predicted `dr-refuses`** -- no DR object in the tree prints a bit string. A `.REL` here opens a bit-output route this compiler has never lowered and would have to be measured on its own terms | absence of witness, written as a prediction |

Global predictions:

* **G1** -- DR accepts P1-P14 with `NO ERROR(S) IN PASS 1` and `PASS 2` and writes
  a `.REL` for each; only P15 is predicted to refuse.  Basis: every shape in P1-P6
  appears verbatim in a DR-distributed program DR itself compiled (CREATE,
  FLTPOLY2, RETRIEVE, DIOCOPY, E30B5's source family); the rest are conservative
  extensions a compiler that already materialises booleans should handle.
* **G2** -- no DATA-area surprise: `static initial('0'b)` keeps the static cell at
  DATA 0000 with initialiser byte `00` ([C114], [C115]), and an automatic bit(1)
  grows AUTO STORAGE by exactly 1 byte.
* **G3** -- my compiler must keep refusing the shapes it has never lowered before
  the oracle run.  Measured at HEAD `d609e01` in `BASELINE-MINE.txt` (binary md5
  72765a97), written before any oracle call: P1, P2, P5, P12 refuse with
  `condition form not in E2E-3b subset [TBD]: (^ b)`; P6-P10 with `store into
  BIT(1) from condition is unsampled [TBD]`; P11 with the same site naming a
  `prefix operator`; P13 with `(^ (cond (= k 0)))`; P14 at the conjunction
  operand; P15 at the PUT.  **P3 and P4 already compile** (384 bytes each) -- the
  positive bare-bit test and the ANI/SUI ladder are implemented [E2E-11 step 1a/2],
  so their open question is byte-parity with DR, not refusal.  G3 is therefore
  amended before the oracle ran, from my own binary, and not from DR: it names the
  refusal set, and the two shapes that are not in it.  After the change, each
  accepted probe must be byte-identical whole-file to its golden, or the row goes
  to `spec/INVENTORY.txt` as a measured `my-gap` and not be quietly promoted
  (PROTOCOL #3, #7).

## What a MISS buys

P6–P10, P12 and P14 are the discriminating ones: they ask whether [C095]'s flag
trick is DR's *only* boolean materialiser or whether the bit-cell store uses a
different tail, and whether `^` is a condition operator at all.  A refusal on any
of them is a `dr-refuses` row (and keeps CREATE's path narrow); a lowering that
differs from the prediction is a new claim.  Nothing here is promoted into a rule
without the oracle's own bytes.

## Round 2 (E48B1..E48B9) -- written after round 1's oracle run, before round 2's

Round 1 measured the shapes; three questions stayed open and round 1 also turned
up a defect in **my** code that no previous specimen had ever exposed (see
`RESULTS.md` §4).  These predictions are written and committed before
`oracle/batch.py` is invoked on any E48B probe.

| # | probe | question | PREDICTED DR answer | basis |
|---|---|---|---|---|
| R1 | E48B1 | `if ^b then do; ... end;` with NO else (CREATE:35's spelling) | the same 8-byte `3A/B7/FA <chain>` test head; the chain's target is the statement after the block | CREATE 00A1-00A8 |
| R2 | E48B2 | positive bare `if b then do;` with no else | `3A/B7/F2 <chain>` | FLTPOLY2 0075 |
| R3 | E48B3 | **DEF-DATA-SIZE with one STATIC bit and one literal and no automatics** | **2** -- [C114]'s `[statics][pool][automatics]` with zero automatics; DR's E48A3 already said `3` for two literals, i.e. 1 static + 2 pool | E48A3/E48A6 DR objects, [C114] |
| R4 | E48B4 | static bit + one automatic fixed | size **4** = 1 static + 1 pool + 2 auto, addresses b@0000 'T'@0001 n@0002 | [C114], E48A5 (`b'@0002 above a 2-byte pool) |
| R5 | E48B5 | two static bits, no automatics | size **4** = 2 statics + 2 pool bytes ('B','C'); cells adjacent at 0000/0001, initialisers 00 then 80 | E20B/E20D (one static each), [C114] |
| R6 | E48B6 | `dcl s char(3) static initial('AB')` | **UNMEASURED**. Predicted ACCEPT with s at DATA 0000 carrying the two bytes `41 42` and the third byte of the cell... open whether the pool then starts at 0003 or 0004 (a static char(3) cell is 3 bytes; 'AB' as a PUT literal is a separate 2-byte cell). This row feeds the STATIC-on-CHARACTER gap, not this phase's CREATE path | none -- my compiler refuses the shape outright today |
| R7 | E48B8 | one literal used by BOTH a varying store and a comparison | ONE pool cell (2 bytes, deduped by content [C152]); `?SMCVM`'s `LXI D` and `?SCVCM`'s `LXI H` name the same address | [C152], CREATE's `*D(0035)` reuse |
| R8 | E48B9 | automatic bit + automatic varying + a loop that stores a condition then tests its negation | DATA = pool + (31 varying) + (1 bit) in declaration order, `b` ABOVE `name`; both shapes appear together, nothing new | E48A5, E48A6, CREATE |
| G4 | all | DR writes a `.REL` for R1-R8 | accepted, `NO ERROR(S)` in both passes | as G1 |

The **falsifiable core of R3-R5** is my own arithmetic, not DR's: my compiler
currently prints `DEF-DATA-SIZE = sy_total + pool_total + max(auto, pl_total) +
2*temps`, and `pl_total` (bind's top-block section total) is **1 for a STATIC
bit**, which double-counts the static byte whenever the statics dominate the
`max`.  If DR says 2 where I say 3, the `max` arm is wrong and must be fixed
here, because every accepted E48 specimen depends on it.  If DR says 3, my number
is right and E48A3's mismatch has another cause.  Either way the oracle decides,
not my formula.
