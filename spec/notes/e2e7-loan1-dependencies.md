# E2E-7 — LOAN1 dependency assessment (2026-10-18, before any slice-2 code)

ANALYSIS + EVIDENCE. Produced to answer one question: **is "5 unseen
PLILIB routines" the real remaining work for LOAN1?** Answer: **no.** The
routine count is accurate but it measures only part of the cost, and two
of the required items are not decimal work at all.

## 1. Evidence sources used

| source | what it gave |
|---|---|
| `artefacts/LOAN1.PLI` | the actual 42-line source (all constructs enumerated below) |
| `golden/first8080u/LOAN1/LOAN1.PRN` (historical) | statement addresses, CODE SIZE 01E7, DATA AREA 003C — compiled with switches `L D` only: **no `$C`, no symbol dump**, so no instruction-level information |
| `golden/e2e7/LOAN1/LOAN1.REL` (new) | LOAN1 re-compiled with `$L$D$C$S`. Its `.REL` is **byte-identical to the curated historical golden** (`cmp` clean), which is what licenses using the new `$C` listing as the instruction-level description of the accepted program |
| `golden/e2e7/LOAN1/LOAN1.REL` relocations | the jump targets DR backpatches (see §3) — LOAN1 has **zero** CHAIN-ADDR records: every conditional-jump operand is `F2/C2 00 00` patched by the SET-LC/RELOC continuation mechanism already proven for the tail guard |
| `golden/link1/LOAN1.COM`, `golden/run2/LOAN1.output.txt` (phase 1) | a COMPLETE DR interaction: 38 lines, 27 schedule rows, ends `Principal ^Z` |
| `extracted/PL1-80_Applications_Guide_Dec80.txt` ll. 7202-7235 | the published output table for 500 / 14 / 22.10 |
| `oracle/linkrun.py` `INPUTS["LOAN1"]` | the documented scripted stdin: `500\r`, `14\r`, `22.10\r`, `\x1a` — already wired, already exercised |
| 12 micro-cases compiled locally against the current build | exactly which constructs refuse today (table in §4) |

## 2. Layout ground truth (from the new `$C`/`$D` listing)

```
BLOCK AT LINE 9, AUTO STORAGE 17 BYTES
  M   FIXED BINARY(15,0)   0000 (2)      Y  FIXED BINARY(15,0)  0002 (2)
  P   FIXED DECIMAL(11,2)  0004 (6)      PMT FIXED DECIMAL(6,2) 000A (4)
  I   FIXED DECIMAL(4,2)   000E (3)
CODE SIZE = 01E7 (487 B)     DATA AREA = 003C (60 B)
```
* `bytes(FIXED DEC(p,s)) = ceil((p+1)/2)` now holds at **NINE** precisions:
  p = 1, 3, 4, 5, 6, 7, 9, 11, 15 (LOAN1 contributes 6 -> 4 bytes and
  11 -> 6 bytes). Still no extrapolation inside the accepted band.
* Pool inventory visible in the trace: `S(0000)` 'Principal ' (10),
  `S(000A)` 'Interest  ' (10), `S(0014)` 'Payment   ' (10),
  `S(001E)` DEC 0 at 11 digits (6), `S(0024)` 'Year' (4),
  `S(0028)` **DEC 1200 at 4 digits (3 bytes)** — i.e. an *integer* literal
  used in DEC arithmetic becomes a decimal cell with its own digit count.
* LOAN1's whole data layout is already PREDICTED by the current model:
  pool = 10+10+10+6+4+3 = 43 = 0x2B, and DR places M at A(002B), Y at
  002D, P at 002F, PMT at 0035, I at 0039 -- i.e. `var address = pool
  total + auto offset`, exactly `st.base + vi.off` as implemented. DATA
  AREA 003C = 43 pool + 17 auto. So no layout work is outstanding for
  LOAN1; what is outstanding is lowering.
* No tail guard is emitted (outer window is open: `do while('1'b)`), which
  is the already-proven C082/R414-R426-R427 branch of the rule, and the
  code simply ends with the two back edges `JMP 00B6` (inner while test)
  and `JMP 0006` (outer back edge) — CODE SIZE = 01E4+3 confirms it.

## 3. Construct-by-construct map (source -> DR code -> status today)

| # | LOAN1 source | DR code (address) | PLILIB routes | status in my build today |
|---|---|---|---|---|
| 1 | `do while('1'b)` | 0006 window open | — | done [C082] |
| 2 | `put skip list('Principal ')` | 0006-001F | SYSPR SKPOP SLCTS PNCOP QIOOP | done |
| 3 | `get list(P)` x3 (0022, 0058, 008E) | `LXI D,0290; LXI B,0000; ?SYSIN; ?GNVOP; JP ->stmt-end; MVI B,scale; ?QCDOP; LXI H,target; MVI A,digits; ?DSTOP; ?QIOOP` | **?QCDOP** unseen; SYSIN/GNVOP/QIOOP/DSTOP already emitted | **[TBD] refusal** — "GET LIST of non-varying var". Same refusal covers INT targets (`get list(m)`), so this is the *numeric GET family*, not a decimal gap. The JP on GNVOP means an input condition **skips the convert+store** (target = the statement's own trailing `CALL ?QIOOP`, recovered from the REL relocations 0x3e/0x74/0xaa) |
| 4 | `m = 0; y = 0;` | 00AD `LXI H,0000; SHLD M; SHLD Y` | — | **was** a silent byte divergence (duplicate LXI) — FIXED this slice (law D6, [C085]) |
| 5 | `do while (P > 0)` | 00B6-00C9: push 0 (A=0B, 6-byte cell), push P, `?DCMOP`, `JP -> 01E4` | **?DCMOP** | **FIXED this slice** [C085]: 15 specimens byte-exact + DR-runs confirm the flag/push-order law |
| 6 | `if mod(m,12) = 0 then do; ... end;` | 00CC `LHLD M; MVI A,0C; PUSH H; MOV L,A; ADD A; SBB A; MOV H,A; POP D; ?IMDOP; MOV A,H; ORA L; JNZ -> 010D` | ?IMDOP (already emitted) | **[TBD] refusal** — "condition form not in E2E-3b subset". **Not a decimal gap at all**: my compiler already lowers `m = mod(m,12);` byte-exactly (?IMDOP + the `ADD A/SBB A` byte-sign-extension ladder), but no golden has ever put MOD on the *condition* side. Pure lowering work, zero new routines. |
| 7 | `y = y + 1; put skip list('Year',y);` | 00DF-010A | QICOP PNVOP | done |
| 8 | `m = m + 1; put skip list(m,P);` | 010D-013F | QICOP PNVOP DLDOP QDCOP(width 14 = p+3, scale 2) | done (and LOAN1 re-confirms the p+3 width law at p=11) |
| 9 | `P = P + round(i * P / 1200, 2)` | 0142-017F: push i(4), push P(11), `?DMUOP`; push 1200 (own digits, `A=04`), `?DDVOP`; `MVI A,02 ?DROUN`; push P(11); `MVI A,02 ?QDDSL`; `?DADOP`; `MVI A,02 ?QDDSR`; `?DSTOP` into P | **?DDVOP ?DROUN ?QDDSL** unseen | **[TBD] refusal** (divide; and `round` refused as an unsupported DEC builtin shape) |
| 10 | `if P < PMT then PMT = P;` | 0182-0195: push P(11), push PMT(6), `?DCMOP`, `JP -> 0198`; then 0198 push P(11) `?DSTOP` into PMT(6) | ?DCMOP | **FIXED this slice** for the compare; note the *assignment across precisions* (dec(11,2) -> dec(6,2), DSTOP A=06) is a shape no E2E-6 sample exercised — LOAN1 itself pins it (it appears in the accepted listing), and the truncation/overflow law for p_source > p_target remains unreadable from bytes alone |
| 11 | `put list(PMT)` | 01A8-01C3 | DLDOP QDCOP(9=6+3,2) PNVOP QIOOP | done (width law re-confirmed at p=6) |
| 12 | `P = P - PMT` | 01C6-01DE | DLDOP DLDOP DSUOP DSTOP | done |

## 4. Work packages that LOAN1 actually needs

Ordered as the agreed slices. "routes" = new PLILIB entry points;
"packages" is the honest unit of work.

**Slice 2 — DECIMAL DIVIDE + scale-shift law** (?DDVOP, ?QDDSL, ?QDDSR)
* LOAN1 needs: `i * P / 1200` and the QDDSL/QDDSR pair around the add.
* Open question that R512 could not answer: its trace showed
  `MVI A,06 ?QDDSL ... MVI A,06 ?QDDSR, MVI A,02 ?QDDSR` and LOAN1 shows
  `MVI A,02 ?QDDSL` (before DADOP) and `MVI A,02 ?QDDSR` (after). One
  sample each. Need the law for *which* scale goes into each shift:
  candidate "partner scale" vs "target scale" vs "p - s - 1".
* Discriminating probes (3, chosen for maximum separation, not volume):
  (a) `x dec(11,4) = y dec(6,2) / z dec(4,2)` — partner/target scales all
  different; (b) divide into a scale-0 target; (c) divide where the target
  scale exceeds a partner scale. Then verify quotients by RUNNING them
  (branch/print outcomes), because scale propagation is semantic, not
  just byte layout.
* Runtime verification is available: print the quotient and cross-check
  against Python `Decimal` (exact decimal arithmetic) — this is what makes
  the divide slice independently falsifiable.

**Slice 3 — ROUND (+ the tie mode)** (?DROUN)
* LOAN1 needs `round(expr, 2)` (2-arg builtin; `MOD`/`ROUND` both appear
  as `BUILTIN CONSTANT` symbols in LOAN1's symbol table, so the DECIMAL
  precedent [C084] says: parser builtin table + precision-from-context).
* The 1-arg form `round(x)` is unpinned (probe it; refuse if unreadable).
* **Tie mode**: I checked the documented LOAN1 schedule against
  `Decimal` quantizations — half-up and half-even both reproduce all 27
  rows; DOWN and UP do NOT (they miss rows). So the published example
  proves DR's `round` rounds rather than truncates, but LOAN1 has **no
  exact half-cent month**, so it cannot discriminate half-up from
  half-even. One dedicated probe with a literal half-cent
  (e.g. `round(2.125, 2)`, `round(2.135, 2)`) settles it; until then the
  tie mode is [TBD] and only non-tie cases compile.

**Slice 4 — NUMERIC GET family** (?QCDOP + input lowering; NOT decimal)
* Three sites in LOAN1 (all DEC targets) and it is also the blocker for
  `get list(m)` (INT targets) in ACK/ACKTST/DECPOLY, so this is the
  general "GET of a non-varying variable" family: `?SYSIN` setup,
  `?GNVOP` scan, the JP-on-input-condition that skips convert+store, then
  `?QCDOP` (B = scale) + `?DSTOP` (A = digits) for DEC, or presumably a
  plain SHLD / ?QICOP-style convert for INT (unreadable from LOAN1; needs
  one ACK-side probe or the existing ACK golden's $C if I re-list it).
* Harness: **no new infrastructure needed** — `INPUTS["LOAN1"]` already
  exists and phase 1 already drove the whole interaction successfully
  (`golden/run2/LOAN1.output.txt`). What we have never done is compare
  *our* linked GET program against DR's console stream, so the input echo
  path (CP/M echoing typed characters into the console region) is
  untested for our own build. That is a verification risk to retire early
  with a tiny GET probe rather than at LOAN1 acceptance.

**Slice 5 — MOD (or any supported integer expression) on the CONDITION side** (0 routes)
* `if mod(m,12) = 0 then` -> `LHLD; sign-extend ladder; ?IMDOP; MOV A,H;
  ORA L; JNZ -> skip`. My `= 0` condition arm exists but only matches
  `var = 0`; extending it to "expression = 0" needs the expression's HL
  value, which is exactly what `lower_hl` already produces. Small,
  general (unblocks nothing decimal, but LOAN1 is impossible without it).

**Already landed on the way here** (this slice, not LOAN1's decimal work):
* DEC comparison, all six relations [C085].
* D6 HL-constant reuse (delta 0) — LOAN1's `m = 0; y = 0;` could never be
  byte-exact without it.
* D7 DEC pool reuse — required by any program with two identical DEC
  literals, and it CORRECTED a wrong E2E-6 claim.
* Additive-literal scale alignment (`p = p - 1`) — my previous own-digit
  treatment was silently wrong for that shape; nothing caught it until a
  comparison probe happened to contain it.

## 5. What the routine-surface metric got wrong here (record for future rankings)

LOAN1's distance dropped 10 -> 5 when DEC core landed, and 5 *is* the
correct number of new entry points. But the LOAN1 milestone is not "5
routines": two of the five blocking behaviors (?IMDOP's condition use and
the numeric-GET lowering) need **zero** new routines, and the third
(HP-constant elision) is a peephole the metric cannot see at all. The
metric ranks *candidates* well (it correctly predicted DFACT as the
cheapest unlock) and must not be read as an effort estimate.

## 6. LOAN1 acceptance plan (agreed criteria, already validated)

1. `.REL` byte-identical to `golden/first8080u/LOAN1/LOAN1.REL` (512 B
   is DFACT's size; LOAN1's is the 01E7-code/003C-data program above).
2. Linked `.COM` byte-identical vs DR (LINK-80 + PLILIB.IRL).
3. **Complete** console equality over the documented scripted interaction
   (`500`, `14`, `22.10`, `^Z`). LOAN1 TERMINATES on EOF, so no bounded
   prefix is needed: 27 rows + 3 prompts + the `Year` headers, raw bytes
   including all field whitespace, compared against
   `golden/run2/LOAN1.output.txt` re-captured in the same session pair.
   Timeout-truncated output is never used as an oracle.
4. Independent arithmetic: a Python `Decimal` model of
   `P = P + round(i*P/1200, 2); if P < PMT then PMT = P; P = P - PMT`
   reproduces all 27 documented balances and the 9.33 final payment
   (verified today, before any LOAN1 code exists — see §3 row 9/§4 slice
   3), so the schedule can be checked against arithmetic rather than
   only against DR.

## 7. Recommendation

Proceed in the order the user set (compare -> divide -> round ->
GET/other), i.e. **next slice = DECIMAL DIVIDE + QDDSL/QDDSR scale law**,
with 3-4 maximum-separation probes plus runtime quotient checks against
`Decimal`. Slices 4 (numeric GET) and 5 (MOD-in-condition) are the
long pole for LOAN1 acceptance and are *not* decimal work; they should be
scheduled explicitly rather than assumed to fall out of the DEC family.

## 8. POST-SLICE-2 STATUS (same day)

Decimal DIVIDE + the whole QDDSL/QDDSR scale law are landed and banked
(C086), which also retro-fixed two wrong formulas in C084 and one
over-broad peephole from C085. LOAN1's remaining blockers, in order of
appearance now:

| # | blocker | routes needed | note |
|---|---|---|---|
| 1 | `get list(P)` (and `get list(m)` elsewhere) | `?QCDOP` (+ the GNVOP/JP input template) | FIRST blocker today; not decimal-specific |
| 2 | `round(i * P / 1200, 2)` | `?DROUN` | slice 3; tie mode still open (LOAN1 has no half-cent month) |
| 3 | `if P < PMT then PMT = P;` | none | DONE since slice 1 (compare) + E2E-6 (DEC->DEC store across precisions; LOAN1 keeps scales equal) |
| 4 | `p = p + round(...)` add across scales | none | DONE since slice 2 (L1/L5 alignment) |
| 5 | `p = p - pmt`, `put skip list(m,P)`, `put list(PMT)` | none | already byte-exact |

The unseen-route count for LOAN1 is now 2 (?QCDOP, ?DROUN) out of 23.
A side effect worth recording: slice 2 also proved that a DECIMAL FORMAL
PARAMETER is passed by reference into a 2-byte pointer cell, which my build
had been compiling SILENTLY WRONG; it now refuses [N33]. That gap does not
touch LOAN1 (no procedures), but it does gate DECPOLY and any program with a
decimal parameter, so the ranking in section 10 should count it as a
third decimal work package (formal-parameter passing) distinct from
round()/GET.
