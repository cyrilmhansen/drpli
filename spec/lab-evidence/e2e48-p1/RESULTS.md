# E2E-48/P1 — RESULTS: prediction vs verdict, measured DR laws

Measurement date 2026-10-29.  Every byte reading below was re-derived from the `.REL`
records themselves (`tools/reldump.py` per-byte streams, `tools/e2e42-p2b/chaindump.py`
for the linearized CODE, `LINK-SET-LC/RELOC` pairs for chain fills, `LINK-DEF-DATA-SIZE`
and `DATA data` records for the DATA area) — never from a `.PRN` rendering, and never
copied from a prior report.  Where this file contradicts `HYPOTHESES.md`'s *prior-evidence*
section or `HANDOFF.md`'s summary, this file wins; the contradictions are itemized in §5.

## §0 Ordering and provenance (PROTOCOL #1)

* Predictions round 1: probes `E48A1..E48A15` + this directory's `HYPOTHESES.md`
  committed at **`284b630`**, before any oracle call on any E48 probe.
* My-compiler baseline (G3) recorded at **`d609e01`** (`BASELINE-MINE.txt`, binary
  md5 72765a97, objects in `/tmp/e48base/`).
* Predictions round 2: probes `E48B1..E48B9` + `mkprobes2.py` + round-2 predictions
  committed at **`3401821`**, before round 2's oracle call.
* Oracle: `PLI_SRC=probes python3 oracle/batch.py E48A1..E48A15 --tag e48p1 --switches '$L$D'`
  → **15 ok / 15**; then `E48B1..E48B9 --tag e48p1 --reuse` → **9 ok / 9**.  All 24
  programs produced both `.PRN` and `.REL`; DR's pass reports show `NO ERROR(S)` in
  both passes for every probe (G1, G4 confirmed except as noted at P15).
* Goldens committed at **`ece657e`**: `golden/e48p1/<N>/<N>.{REL,PRN}` + `dir.txt`,
  plus batch summaries (`summary.txt`, `transcript-batch0..3.txt`).  Nothing in this
  phase rewrites or regenerates any pre-existing golden.

Notation: `<X>` = 2-byte inline DATA relocation (`RELOC data` at that operand, cell `X`);
`<chain fill>` = the two operand bytes DR emits as `00 00` and patches after the pass
with a `LINK-SET-LC code <operand-address>` + `RELOC code <target>` pair — every
conditional-skip forward target in this bank works this way (E48A1 `SET-LC 0011 → RELOC
code 0x44`, etc.).  There is no 5-byte chain: the filler is the instruction's own 2-byte
operand (§5 item 2).  A bare-bit test head is therefore **7 bytes**: `3A lo hi / B7 /
<cond> 00 00`.

## §1 Round 1 — P1..P15 prediction vs verdict

| # | probe | verdict vs prediction | measured bytes (addresses from the golden) |
|---|---|---|---|
| P1 | E48A1 `do while(^b)` | **HIT** on sequence; **MISS** on size ("8 bytes" — actual 7) | test @000C `3A *D(0000) / B7 / FA 00 00`; chain filled 0011→**0044** = loop-tail `C3 *CODE(000C)` (0041) + 3.  BODY 0013..0040, retest tail 0041. |
| P2 | E48A2 `if ^b then…else…` | **HIT** | identical 7-byte head @0006 `3A/B7/FA`; chain 000B→**0027** = ELSE body; then-block ends `C3 *CODE(003E)` @0024 (operand fill 0025→003E) — the whole-`IF` join target. |
| P3 | E48A3 positive `if b then…else…` | **HIT** | head @0006 `3A/B7/F2` (JP after `B7`: sign test, not zero test); chain 000B→0027 (else).  **My compiler already lowers this head byte-identically** — but my `.REL` differs from the golden by one record: `DEF-DATA-SIZE` mine 0004 vs DR **0003** (§4). |
| P4 | E48A4 `b='1'b`, `b='0'b` as tests | **HIT**; the open question resolves **JNZ** | `= '1'b' @0006: `3A *D(0000) / E6 80 / D6 80 / C2 <chain>` (10 bytes, fill 000E→0027); `= '0'b' @0027: `3A / E6 80 / C2 <chain>` (8 bytes, fill 002D→0046).  Bare tests use JP/JM (F2/FA), ladder tests use C2 — two different skip families.  My compiler emits this ladder byte-identically; my `DEF-DATA-SIZE` is 0009 vs DR **0008** (§4). |
| P5 | E48A5 AUTOMATIC bit, `do while(^b)` | **HIT** | same 7-byte `3A/B7/FA` test @0011 on auto cell `*D(0002)`; fill 0016→0031 (tail 002E + 3).  Layout proves [C114]: pool `'N='`@0000-1, auto bit `b`@**0002** (1 byte), auto `n`@0003-4; DATA `abs 0005` = 0 static + 2 pool + 3 auto.  Auto bit literal stores @0006/0029: `21 *D(0002) / 36 00` and `36 80`. |
| P6 | E48A6 `b = (name = 'EOF')`, auto varying | **MISS on the prefix; HIT on the tail** | measured @0013, **17 bytes**: `21 *D(0003)` (literal cell) `/ 11 *D(0008)` (varying area) `/ 3E 03` (literal length) `/ CD ?SCVCM / D6 01 / 9F / 32 *D(0000)`.  My prediction (`2A/EB/2A…`, 16 bytes) came from a *misread prior witness* — CREATE's store is 18 bytes with an `XCHG` prefix (§3.2, §5).  Flag trick + `STA` confirmed exactly.  The `name = 'AB'` store @0006 is `21 *D(0008) / 11 *D(0001) / 3E 1E / 06 02 / CD ?SMCVM` (13 bytes).  DATA `abs 0039` = 1 static + 7 pool + 31 auto. |
| P7 | E48A7 `b = (k = 0)` and `b = (k = 5)` | `=0` **MISS on load form; HIT on tail**; `=5` accepted (was UNMEASURED) | `= 0` @000C, 12 bytes: `21 *D(0005) / 7E / 23 / B6 / D6 01 / 9F / 32 *D(0000)` — **`LXI H,<cell>`, not `LHLD`**; the zero-fold is `MOV A,M / INX H / ORA M` (0x7E/0x23/**0xB6**, matching [C095]'s ladder; my prediction table's "B4" was a typo).  `= 5` @003A, 15 bytes: `2A *D(0005) / 01 FB FF / 09 / 7C / B5 / D6 01 / 9F / 32 *D(0000)` — **`LHLD` + `LXI B,FFFB` + byte 0x09** (standard DAD B — the bias IS applied; §5 item 1) + `MOV A,H / ORA L`, then flag trick. |
| P8 | E48A8 `b = (k ^= 0)` | accepted; open question resolves: **no skip defect travels** (no skip byte exists) | @000C, 12 bytes: `21 *D(0003) / 7E / 23 / B6 / **C6 FF** / **9F** / 32 *D(0000)`.  Negation of a materialised `= 0` is `ADI FF / SBB A` — the carry-polarity flip (`v+FF` carries iff v ≥ 1, where `v−1` borrows iff v = 0), *not* a CMA and *not* an inverted compare. |
| P9 | E48A9 `b = (k > 0)` | accepted (UNMEASURED predicted) | @000C, 10 bytes: `21 *D(0003) / AF / BE / 23 / 9E / 32 *D(0000)` — `XOR A / CMP M(low) / INX H / SBB M(high)`: subtract the 2-byte value from 0; the final borrow is `k > 0` and `SBB M` materialises it as 00/FF directly.  No SUI/SBB tail needed. |
| P10 | E48A10 `f = (b = '1'b)` | accepted (UNMEASURED predicted) | @0006, 13 bytes: `3A *D(0000) / E6 80 / D6 80 / D6 01 / 9F / 32 *D(0003)` — the P4 ladder's result (00=true, nonzero=false) feeds [C095]'s trick, then `STA` the other bit cell.  Mixed static/auto bit pair works. |
| P11 | `b = ^(k = 0)` | accepted; **MISS** on every predicted spelling (CMA / inverted compare / refusal) | @000C, 12 bytes: `21 *D(0003) / 7E / 23 / B6 / C6 FF / 9F / 32 *D(0000)` — byte-identical *lowering* to P8: `^(cond)` in value position = the same `= c` materialiser with the tail negated (`D6 01`→`C6 FF`).  No 0x2F (CMA) anywhere in the bank. |
| P12 | E48A12 store + negated test in one loop | **HIT in substance** (both shapes compose, nothing new), with P1/P6 size corrections | @000C the 7-byte `3A/B7/FA` (fill 0011→004C = tail 0049+3); @0027 the 17-byte SCVCM store (§1 P6); `if n = 4` @0038: `2A / 01 FC FF / 09 / 7C / B5 / C2 <chain 0041→0049>` biased **test** ladder (JNZ, not STA), then-block literal store `21 *D(0000) / 36 80`; tail `C3 *CODE(000C)`.  DATA `abs 0041` = 1 + 7 pool + 31 name + 2 n. |
| P13 | E48A13 `if ^(k = 0)` / `do while(^(n = 3))` | accepted; `^` **is** a condition operator | @000F: `21 *D(0003) / 7E / 23 / B6 / **CA** <chain 0016→002F>` — the `= 0` *test* ladder with the skip byte inverted **C2→CA** (9 bytes).  Loop @002F: `2A *D(0005) / 0B 0B 0B / 7C / B5 / **CA** <0038→0044>` — bias −3 spelled **three `DCX H`** (the ≤3 arm of [C143]'s compare route), exit jump = natural `= 3` test inverted by `^` (target = statement after loop = tail 0041+3).  Back edge `C3 *CODE(002F)` @0041. |
| P14 | E48A14 `if k = 0 & b then` | accepted; bit operand has a real lowering (predicted UNMEASURED) | @000C, 18 bytes: `21 *D(0006) / 7E / 23 / B6 / D6 01 / 9F` (left operand materialised into A) `/ **F5 / 3A *D(0000) / C1 / A0**` (`PUSH PSW / LDA bit / POP B / ANA B`) `/ **F2** <chain 001C→0038>`.  The conjunction keeps ONE skip byte, `F2` (sign test on the AND result: FF∧80 = 80 → take; any 00 → skip), and a bit operand rides through `BC`, never through the 2-byte `= 0` read. |
| P15 | E48A15 `put list(b)` | **MISS — DR ACCEPTS** (predicted `dr-refuses` on absence of witness) | @000F: `3A *D(0000) / 06 01 / CD ?QB08C / CD ?PNBOP / CD ?QIOOP` — a bit item is a real PUT route (SYSPR preamble `11 0252 / 13 *CODE(end) / CD ?SYSPR` first; no `?SLCTS` because there is no literal; DATA `abs 0001` = the static `80` cell alone).  This is the PROTOCOL-#4 error class caught by measuring; kept in the record. |

Global round-1 verdicts:

* **G1** — **MISS at P15** (predicted refusal), HIT otherwise: all 15 accepted with a `.REL`.
* **G2** — **HIT**: static bit cell at DATA 0000 with its initialiser byte; automatic bit
  occupies exactly 1 byte in the auto block above the pool (E48A5).
* **G3** — baseline refusals as recorded in `BASELINE-MINE.txt` (P1/P2/P5/P12 condition
  form; P6-P10 store-unsampled; P11 prefix-store; P13 `^(cond)`; P14 conjunction operand;
  P15 PUT of a bit).  P3/P4 compile but are **not byte-identical** — one record differs in
  each (`DEF-DATA-SIZE`, §4): a measured **my-gap**, not promoted to any rule.

## §2 Round 2 — R1..R8 prediction vs verdict (+ the unpredicted probe)

| # | probe | verdict | measured bytes |
|---|---|---|---|
| R1 | E48B1 `if ^b then do;…end;` no else, inside `do while(^b)` | **HIT** (sequence; size wording as §1) | outer test @000C `3A/B7/FA`, fill 0011→003C (tail 0039+3); inner test @001A `3A/B7/FA`, fill 001F→**0028** = the statement AFTER the then-block — no second jump for a no-else `IF` skip.  `if n = 4` ladder @0028 `2A/01 FC FF/09/7C/B5/C2 <0031→0039>`; then-store `21 *D(0000) / 36 80`; tail `C3 *CODE(000C)`. |
| R2 | E48B2 positive `if b then do;` no else | **HIT** | @0006 `3A/B7/F2`, fill 000B→0024 = next statement (`put list('E')`).  DATA 3 = static `80` + `'Y'`/`'E'`. |
| R3 | E48B3 one static bit + one literal, no automatics, **no `stop`** | **HIT: DR = 2** (predicted 2; mine says 3 — the falsifiable core resolves **against my formula**) | `DEF-DATA-SIZE abs 0002`; DATA records `0000 00` (the `'0'b` cell), `0001 54` ('T').  Also visible: a program with no `stop` still ends `CD ?STOPX` @001D (implicit), CODE 32. |
| R4 | E48B4 static bit + one auto fixed | **HIT** | size **4**, addresses exactly as predicted: b@0000, 'T'@0001, n@0002-3 (`21 0001 / 22 *D(0002)` store of 1; `2A *D(0002)` for the `?QICOP`). |
| R5 | E48B5 two static bits, no autos | **HIT** | size **4**; cells adjacent b@0000=**00**, c@0001=**80**; pool 'B'@0002, 'C'@0003; two bare tests @0006/@0024 `3A *D(0000|0001) / B7 / F2 <chain>`. |
| R6 | E48B6 `dcl s char(3) static initial('AB')` | **accepted (predicted UNMEASURED→accept); open details resolve**: | DATA = **3 bytes total, `41 42 20`** — the cell is `char(3)`'s FULL extent, blank-padded; there are **no pool bytes** (`abs 0003` = 3 static + 0 pool).  The PUT reads THE STATIC CELL ITSELF: `21 *D(0000) / 3E 03 / CD ?SLCTS / ?PNCOP / ?QIOOP` (length 3, not 2).  Feeds the STATIC-on-CHARACTER `my-gap` (EXPR2, FSCAN, LOAN2, MPMCALLB, REPORT). |
| R7 | E48B8 literal used by BOTH `?SMCVM` store and `?SCVCM` compare | **HIT: one cell** | `'AB'` appears ONCE in the pool (@0001-2); compare @0013 `21 *D(0001) / 11 *D(0005) / 3E 02 / CD ?SCVCM / D6 01 / 9F / 32 *D(0000)` — the SCVCM `LXI H` and the SMCVM `LXI D` (0009) name the SAME address.  DATA `abs 0036` = 1 + 4 + 31 (deduped, [C152]). |
| R8 | E48B9 big pool + auto varying + auto bit + store/test loop | **HIT** | DATA `abs 0048`: pool 16 (`ABCDEFGH`@0000-7, `EOF`@0008-A, `.`@000B, `DONE`@000C-F), then autos in DECLARATION order `name`@0010-2E (31), `b`@**002F** — the bit sits ABOVE the varying as predicted; the SCVCM store @0013 writes `32 *D(002F)` and the loop test @0024 reads `3A *D(002F) / B7 / FA <0029→0063>` (tail 0060+3).  Both shapes compose inside one loop with nothing new. |
| — | E48B7 | **NO PRE-REGISTERED ROW** (the R-table skips this probe; measurement only — recorded honestly) | DATA `abs 0005`: statics adjacent 0000=`80` 0001=`00`, literals ABOVE them ('N'@0002,'P'@0003,'Q'@0004) — [C114] order with two statics; `if ^b` @0006 FA fill→0024 (next stmt), `if c then…else…` @0024 F2 fill 0029→0045 (else), then-jmp 0042→005C. |
| G4 | all round-2 | **HIT**: 9/9 accepted, `.REL` written, no errors. |

## §3 Measured DR laws of this bank (candidates for C309+; classification: accepted-with-evidence)

### 3.1 Test heads on BIT(1) cells — 7 bytes

`3A <cell> / B7 / <skip> <00 00>`; skip byte: **F2 (JP)** positive bare test,
**FA (JM)** bare `^`-negated.  The operand is a forward reference emitted as `00 00` and
filled by `SET-LC/RELOC` after the pass.  Targets, all measured here:

| context | skip taken when | filled to |
|---|---|---|
| `do while(cond)` | cond false (exit) | address just after the loop-tail `C3 <test>` (= tail + 3) |
| `if … then … else …` | cond false | the ELSE body |
| `if … then do; … end;` (no else) | cond false | the next statement |
| `if … then …` + then-block, then tail `C3` (with else) | — | then-blocks end with `C3 <after-IF>` (operand also `00 00` + fill) |

### 3.2 Stores into BIT(1) — `STA (0x32)` with inline DATA reloc; value 00/FF

All materialising condition stores end `… / <flag arithmetic> / 32 <cell>`.  The flag
trick is [C095]'s `SUI 01 / SBB A` (`D6 01 / 9F`), which maps operand value 0 → **FF**
and nonzero → **00**; its measured negation form is `ADI FF / SBB A` (`C6 FF / 9F`),
which maps nonzero → **FF** and 0 → **00** (carry polarity, §1 P8).
Materialiser by operand class (all from §1 rows; the `k` cells are 2-byte fixed bin):

| shape | bytes | lowering |
|---|---|---|
| auto varying `=` literal | 17 | `21 lit / 11 var / 3E litlen / CD ?SCVCM / D6 01 / 9F / 32 b` |
| `k = 0` | 12 | `21 k / 7E / 23 / B6 / D6 01 / 9F / 32 b` |
| `k ^= 0` or `^(k = 0)` | 12 | same, tail `C6 FF / 9F` |
| `k = c`, \|c\| ≥ 4 | 15 | `2A k / 01 lo hi / 09 / 7C / B5 / D6 01 / 9F / 32 b` (`LXI B, 65536−c` + **DAD B**, bias applied correctly; [C143] compare-route threshold) |
| `k > 0` | 10 | `21 k / AF / BE / 23 / 9E / 32 b` (borrow of 0−k = "k>0"; `SBB M` materialises it) |
| `b = '1'b` | 13 | `3A b / E6 80 / D6 80 / D6 01 / 9F / 32 f` (the P4 ladder into STA) |

CREATE's single SCVCM store (008F, 18 bytes: `21 var / **EB** / 21 lit / 3E 03 / …`)
spells the same register setup (`HL` = literal, `DE` = varying, `A` = literal length)
via `XCHG`; every E48 site uses `LXI H,lit / LXI D,var` directly.  **The discriminator
between the two spellings is [TBD]** — no probe in this bank varied it; CREATE's census
path needs it (a round-3 candidate: same expression in varied contexts).

### 3.3 `^` on a general condition, in TEST position

Same ladder as the unnegated test, **skip byte inverted C2→CA** (E48A13 @000F).  In
`DO WHILE`, `^(cond)` therefore exits on `CA` (the unnegated `= c` test would keep
`C2`).  In VALUE position (§3.2) negation is instead the `ADI FF` tail — the two routes
are different mechanisms and neither uses CMA.

### 3.4 `&` with a BIT(1) operand

Left operand materialises into `A` (§3.2 form), the bit arrives via
`F5 / 3A bit / C1 / A0` (`PUSH PSW / LDA / POP B / ANA B`), and ONE `F2` skip follows
(E48A14).  The conjunction is a value-level AND of 00/FF-with-80 patterns, tested by sign.

### 3.5 PUT of a BIT(1) (`put list(b)`) — a route that exists

`3A <cell> / 06 01 / CD ?QB08C / CD ?PNBOP` (before the list-closing `?QIOOP`), after
the usual `?SYSPR` preamble; `06 01` = declared length 1 (E48A15; mixed lists in
E48A6/A7/A12/B8 show `?SLCTS` literal items and the bit item side by side).

### 3.6 DATA area (confirms and extends [C114]/[C115])

`[statics][pool][automatics]`; static bit cells adjacent from 0000 in declaration order
(E48B5 00/80, E48B7 80/00); literals deduped by content (E48B8); automatics above the
pool in declaration order, bit = 1 byte (E48A5, E48B9 `b` above `name`); `DEF-DATA-SIZE`
= total extent.  **STATIC on CHARACTER is accepted**: full-extent cell, blank-padded
initial (E48B6 `41 42 20`), and the cell doubles as the PUT source with its declared
length.

## §4 My defect exposed by this bank (measured `my-gap`, root cause found)

`pli80c` at `d609e01` compiles P3/P4 but the whole `.REL` differs from the golden by
exactly one record — the `LINK-DEF-DATA-SIZE` value:

| probe | DR | mine | delta |
|---|---|---|---|
| E48A3 | 0003 | 0004 | +1 |
| E48A4 | 0008 | 0009 | +1 |
| E48B3 | 0002 | 0003 | +1 (R3 falsifiable core) |
| E48B5 | 0004 | 0005 | +1 |
| E48B7 | 0005 | 0006 | +1 |

Root cause (measured with temporary `E48DBG` instrumentation in the parent session,
since reverted): `codegen.ml`'s data-size formula
`sy_total + pool_total + max(auto_bytes, layout.pl_total) + 2*temps` double-counts a
static byte when the statics dominate the `max` — `bind.ml`'s `section2` `span` charges
STATIC-class rows into `pl_total`, which is meant to cover *automatics* only.  The fix
is in `bind.ml` (exclude STATIC rows from `span`); `codegen.ml:12340` then needs no
change.  This passed 1074 specimens only because every pre-existing one had automatics
≥ statics in the `max` (see `LEARNINGS.md` 2026-10-29).  Classification: **my-gap**,
fix + gate before any §3 implementation work.

## §5 Corrections to prior records (the repository outranks the handoff documents)

1. **"DR's own `DAD H` bias defect"** (`HANDOFF.md` Last-verified-state; the
   `LEARNINGS.md` entry "A DR defect is a target"): **FALSIFIED.** The literal golden
   bytes at E48A7:0040, E48A12:003E and E48B1:002E are all **0x09 = DAD B** (the
   project's own learned constants, `op_dad_b = 0x09`, [C144] method): HL += FFFB/FFFC,
   the bias IS applied and the lowering is semantically correct.  The error came from
   trusting `chaindump.py`'s mnemonic: its table (line 38) mislabels 0x09 as `dad d` —
   a typo in MY tool, exactly the [C264] "a rendering is not evidence" class, ironically
   inside the lesson that cites it.  `chaindump.py:38` is corrected in this commit; no
   existing evidence file is rewritten.  My `hl_bias` already emits 0x09 — nothing to
   reproduce.
2. **"`^b` test = `3A/B7/FA` + 5-byte chain, 8 bytes"** (`HYPOTHESES.md` P1/P12,
   `HANDOFF.md`): the chain *is* the jump's 2-byte operand, emitted `00 00` and filled
   by `SET-LC/RELOC`; head = **7 bytes** (verified in CREATE at 0052-0058 and in every
   E48 golden above).  `HYPOTHESES.md` is kept as written (PROTOCOL #2) and superseded
   by this section.
3. **"CREATE's `eofile = (name = 'EOF')` = 16 bytes `2A <D(005A)> / EB / 2A <D(0035)>`"**
   (`HYPOTHESES.md` prior-evidence #3, echoed by `e2e42-p2c §7`): re-read of
   CREATE.REL shows `0x21` at 008F and 0093 — **`LXI H`**, not `LHLD` — so the shape is
   **18 bytes** `21 var / EB / 21 lit / 3E 03 / CD ?SCVCM / D6 01 / 9F / 32 eofile`.
   Likewise FLTPOLY2's `eofile = true` at 0011 is `0x21 <cell> / 36 80` (`LXI H`/`MVI M`),
   not `2A`.  The P6 prediction inherited both misreadings.
4. `HYPOTHESES.md`'s P7 tail notation `B4` — the goldens uniformly show `0xB6` (`ORA M`),
   matching [C095] and [C144]'s corrected ALU table; `B4` was a transcription error.

## §6 Classification ledger for this bank

All 24 probes are **accepted by DR** → every shape my compiler refuses today is a
measured **my-gap** (P1/P2/P5/P12 condition forms; P6-P11 condition stores; P13 negated
condition tests; P14 conjunction; P15 bit PUT; R1/R2 no-else heads; R6 STATIC-on-CHARACTER),
not a `dr-refuses`.  `dr-refuses` rows from this bank: **none**.  No E48 specimen enters
the byte panel until my compiler reproduces it whole-file (§ implementation), which is
tracked in `PROGRESS.md`; `INVENTORY.txt` reasons must be re-stated as `my-gap` when the
probes are registered.  Claims C309+ record §3 with these specimen/golden paths.
