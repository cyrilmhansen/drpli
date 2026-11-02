# PROGRESS.md — DRPLi

Manual prose wins over the managed block below it. Do not hand-edit the managed block.
This file tracks *working state*; compiler behaviour itself belongs to `spec/CLAIMS.md`.

## Current phase — FC-01 CORPUS ACTIVE (operator-authorized long-running corpus mission; baseline HEAD `e7d758c`; WKDAY-00 PASS at rev3; gate + commit owed at this boundary; program 2 = HAMM-00)

FC-01 hop 4 done so far: Batch-B REV2 landed `a5815a8` — FLT-01 rev2 (direct `(a + b) = 6.5`
compare) and BUILTIN-00 rev2 (LENGTH first, SUBSTR store dropped) both executed to their
DELIVERABLE typed COMPILE FAIL attr=`compiler` with the named-blocker refusals verbatim
(`build/fc01/batchB-rev2/`, HEAD `91dd3a7` at execution); rev1 `build/fc01/batchB/` kept as
written; docs § 7 + six § 1 rows; prose 5 clean; dashboard rc=0. The full file-I/O survey
(naming laws [C279]/E16x, content laws [C295]/[C300]/[C280], 128-B pad fact, fixtures, cpmwork
export/import contracts, proposed schema design, the ONUNIT-00 evidence gap) is recorded in
LEARNINGS 2026-11-02 hop 4 — read it before implementing.
IN FLIGHT: the harness extension itself — NO code written yet at this boundary. (Hop 2/3
state superseded here; archived records unchanged.)

## Previous phase — FS-01 CLOSED (2026-11-02; first two functional PASSes, Lane B; baseline HEAD `876ed9e`)

FS-01 (operator mission "first two functional PASSes") COMPLETE: TABLE-00 and TABLE-01 **PASS**
on Lane B. F1 fixed in the harness (`tools/functional_runner.py` `_run_lane_b` anchor law —
program's final CRLF retained, prompt never captured, newline-less terminator →
`console-terminator-ambiguous` UNKNOWN fail-closed; hostile suite C15, 12 checks, suite self-count
**194** all pass). F2 isolated by a TABLE-01 **output-statements-only** revision (two ~54-column
labelled lines; algorithm/inputs/invariants unchanged; source sha `4881f187…`; expectation
DERIVED from declared design + README § 6 law, never captured; PLILIB wrap law stays `proposed`).
Executed ACTUALS + evidence roots in `docs/functional-results.md` § 5 and `HANDOFF.md`;
baseline FAIL reproduction, PASS run, `--double-run` (byte-equal) and Lane-A unchanged check
(FX-00 PASS / FX-01 FAIL `emulator`) under `build/functional/fs01*` (ignored).
P2 FAIL evidence preserved; no compiler/golden/ledger/COVERAGE/`ocaml/` byte touched.
**No active round**: a successor without an operator instruction confirms HEAD/tree,
`/handoff verify`, records state and STOPS. Open items = `docs/functional-results.md` § 3/§ 5 +
`spec/lab-evidence/e2e50-p2/REPORT.md` § 5 (P3-b law declaration, P3-c BDOS-25/license, P3-d
TABLE-02 remain PROPOSALS; P3-a DONE by FS-01). Operator `handoff.config.json` edit stays
unstaged; no push.
## Previous phase — E2E-50/P2 CLOSED (2026-11-02; functional-testing foundation + emulator/redistribution audit; FULL compile-tier gate rc=0 measured at `545dcf1`, recorded `d648bcd`; CLOSE completed by a docs-only session)

Round COMPLETE. Mission, the durable step sequence 0–8 and every hop record (incl. the
falsified-prediction text kept per PROTOCOL #2) are archived VERBATIM and byte-verified —
**23/23 blocks BYTE-EXACT**, completeness sweep over all 8 Next-action / 7 Unfinished /
8 Current-phase / 2 Next-action-stub generations: 0 unarchived lines — in
`docs/history/2026-11-02-e50p2-closed.md`. Last verified state, landing chain and executed
verdicts (FX-00 PASS + determinism; FX-01 FAIL/`emulator` intended; TABLE-00/01 first
functional execution of a DRPLi-compiled program, CONTENT ≡ REFERENCE, ASSERT FAILs framing
F1/F2 attr=`undefined`; census BDOS-25 free-core blocker measured) live in `HANDOFF.md` →
Last verified state; round report `spec/lab-evidence/e2e50-p2/REPORT.md`. No scientific byte,
claim, COVERAGE row, INVENTORY/RUNTIME/census entry or golden changed; `ocaml/` untouched.
**No active round**: a successor without an operator instruction confirms HEAD/tree,
`/handoff verify`, records state and STOPS. P3 shortlist `spec/lab-evidence/e2e50-p2/REPORT.md`
§5 — never an authorisation. Operator `handoff.config.json` edit stays unstaged; no push.
## Previous phase — E2E-50/P1 CLOSED (2026-11-02; deliverables `4cad695`; close docs-only)

Functional dashboard round COMPLETE, docs-only and evidence-only: compiler, oracle, LINK-80,
cpmsim, Rune CI and the gate were NEVER RUN this round; no ocaml/golden/ledger/COVERAGE/INVENTORY/
census byte changed. Landed at `4cad695`: taxonomy validation fixes (4 typed misses; 30 capability
rows; every cited id/name now re-validated on EVERY dashboard run), `spec/functional/programs.tsv`
(44 HISTORICAL/16 FOCUSED/8 MICROPROBE), `tools/functional_dashboard.py` + 30-check test suite,
generated `docs/functional-status.md` (views A–E), `README.md` rolling-status replacement,
labelled [E2E-50/P1 CORRECTION(S)] in `LEARNINGS.md`. Checks measured at `4cad695`: tests rc=0,
dashboard `--check` rc=0, `coverage_check.py` rc=0 (133 rows 0/0), `file_prose_check.py` rc=0
(5 active clean). Superseded prose archived byte-verified in `docs/history/2026-11-02-e50p1-closed.md`.
**No active round**: successor confirms HEAD/tree, `/handoff verify`, records state, STOPS. The
E2E-50/P2 candidate pool is the §E shortlist in `docs/functional-status.md` (a shortlist, never an
authorisation). Operator `handoff.config.json` edit stays unstaged; no push.

## Earlier phase — E2E-49/P4 CLOSED (FULL compile-tier gate rc=0 measured by the step-6 session at HEAD `5b0ccde`, recorded `882f77c`; CLOSE completed by the docs-only closing session — ledger C348..C351, byte panel 1174, coverage 133 rows)

- Round (OPERATOR-authorized 2026-11-01; PLAN committed at bootstrap `bc6ee4f`): composite
  FIXED/TEST bank — ordered relations with a LITERAL (panel G, E49G1..G8), BARE spellings in
  ordered relations (panel H, E49H1..H6), the unequal-extent relation matrix (panel I,
  E49I1..I6), negated compares (panel J, E49J1..J4); shared P3 DECL + tail so the [C309] fills
  and [C314] frames stay comparable. Pre-registration `328eb3f` committed BEFORE any oracle call
  (24 probes CRLF+`^Z` ≤71 cols + mkprobes.py + HYPOTHESES + BASELINE-MINE with the ACTUAL
  binary at `398fa2c`: panels A/B/D refused rc=2 BY NAME — the code-reading predictions held —
  and panel C accepted); **NO separate fill-in commit in this round** (P3 had `0a46824`); ONE
  grouped batch run, tag `e49p4`, **24 ok / 24 — NO dr-refuses** (18 `my-gap` G/H/J, 6 already
  byte-exact I); goldens + `spec/lab-evidence/e2e49-p4/RESULTS.md` `13fca5b`; traceable wording
  repair `9799f1d`.
- Arms (each committed ALONE, new goldens whole-file BYTE-EXACT, out-of-scope refusals rc=2,
  FULL gate rc=0 at each — panel 1150 then, e49p4 unregistered): a `c515377` (`str_cmp_shape_fix_rel`
  widened to `ImemFb` on BOTH sides; H1..H6; no prescan twin); b `ec904c1` (NEW
  `str_cmp_shape_fix_lit_rel` — LITERAL vs the QUALIFIED `ImemF`, both written orientations; the
  ORDER law REKEYS the template on the FIRST LOWERED operand, staged `EB` vs the SIX-byte direct
  `11` head measured; positional immediates + the [C342] collapse; JNC `d2`/JC `da`; G1..G8; the
  inherited "prescan DEMAND twins MUST widen in the same commit" note FALSIFIED, [C152]
  verified); c `47c2194` (NegL admits ONLY the four goldened rewrites `^(=)`→`^=`,
  `^(<)`→`>=`, `^(<=)`→`>` by ONE recursion on the synthesized complement — ZERO new bytes; the
  inherited `Gt->Le` instruction FALSIFIED, no golden exists for `^(>)`, `^(>=)`, `^( ^= )`).
  Regression sweep at arm c: 47/47 BYTE-EXACT (A,B,C,D,E,F,G,H,I).
- Step 6: part 1 `aec53e1` (claims **C348..C351** from RESULTS §2 ONLY; ledger ENDS at **C351**);
  part 1b `9c42f3b` (FOUR labelled [E2E-49/P4 CORRECTION(S)] blocks at [C335]/[C337]/[C344]/
  [C346], falsified sentences quoted verbatim); docs `19ab4e0`/`e13311c`; registration `cc43963`
  (SPECIMENS +24 round bank; sanctioned `--update-inventory` panel 1150 → **1174**; census
  re-snapshot counts UNCHANGED 15/0/26/0, metadata only); part 2a `dbaf004` (four COVERAGE rows
  RELATION_LITERAL / RELATION_QUALIFICATION / RELATION_UNEQUAL_MATRIX / CMP_NEGATED_COMPLEMENT;
  **133 rows 0/0**; stats re-snapshotted); part 2b `5aeac87` (`COND.CMP_LENGTHS_POSITIONAL`
  EXTENDED to EXACT:14 + four labelled SUPERSEDED/WIDENED clauses, all five quotes byte-checked
  vs the pre-edit blob `cc43963`, ORDER law cited **[C104]**, never legacy [C027]/[C072]); part
  2c `5b0ccde` (labelled WORDING CORRECTION at [C348] — "ALL FOUR relations" contradicted its own
  `<`/`>=` enumeration; equal-attribute `>` NEVER sampled; RESULTS §2.1 carries the same slip and
  stands as written, [C342] COUNT NOTE precedent). TRACEABLE SLIP (PROTOCOL #2, `9799f1d`
  precedent): part 2b's ORIGINAL message `55053bd` (amended to `5aeac87` before anything
  referenced it) also overstated `<=` as never sampled — E49F3 collapses at 3/3 stacked
  ([C346]); the committed row text and the [C348] correction govern.
- FULL compile-tier gate at `5b0ccde` rc=0, ACTUALS as printed: byte panel **1174 byte-exact /
  0 fail of 1174** (all twenty-four e49p4 specimens whole-file BYTE-EXACT at 256 bytes), negative
  **181/181** (E46K14 `[dr-refuses]`, pinned marker UNMOVED), divergence **9/9**, coverage
  **133 rows, 0 errors, 0 warnings**, census **15/0/26/0**, prose **5 active files clean**.
  `dune build` rc=0. BYTE TIER ONLY — no `spec/RUNTIME.txt` row came or comes from this round.
  MEASURED GATE DESIGN: the gate prints coverage/census/prose, then the INVENTORY integrity check
  ABORTS rc=2 BEFORE the byte panel while SPECIMENS leads INVENTORY.txt — the byte-panel ACTUAL
  always comes from the post-`--update-inventory` run (the P3 `4b51bc0` cycle, now understood).
- CLOSE (docs-only session, operator authorization 2026-11-01): superseded prose archived
  byte-verified — **16/16 blocks BYTE-EXACT** against their stated git ranges (`19ab4e0`,
  `e13311c`, `882f77c`, `5c52bba`) — in `docs/history/2026-11-01-e49p4-closed.md`, FOUR HANDOFF
  generations (the planned "two" measured as four by section hashing) plus the PROGRESS
  close-era STATUS stack, both superseded Current-phase headings, the surviving P2 CLOSED
  previous-phase record, the STALE bootstrap-era next-action stub, the P3-frozen Verified
  evidence and the P3-era Blockers; HANDOFF/PROGRESS rewritten to CLOSED; LEARNINGS close notes;
  `docs/history/README.md` index row added. NEXT: NO active round — a successor session without
  an operator instruction confirms HEAD and tree, runs `/handoff verify`, records state and
  STOPS; candidate pool in `HANDOFF.md` → Next action. No push; no P5; operator
  `handoff.config.json` edit stays unstaged.

## Next action

**FC-01 OPERATOR OVERRIDE (2026-11-02). HOP 5 IS CANCELLED — do NOT implement `stage_files`,
`expected.file_expectations`, FILE-00/FILE-01, the fc01-fileio oracle round or ONUNIT-00.**

HAMM-00 DESIGN COMPLETE (2026-11-03 design hop, this chain, renewal 3/12): the full port
design, the MEASURED console-GET echo environment law (echo `L\r\r\n`, no PLILIB extra
terminator, unconsumed ^Z never captured — from golden/e32rt_NETWORK + e29dr_runB transcripts;
expected echo lines carry a trailing `\r`), the GET/GOTO shape confirmations, the bin15
scaling analysis (A=300/S≈2400/P=95 declared adaptation; births order law
floor(floor(X/P)/100)=floor(X/(P*100)) exact, reverse order FALSIFIED; P≥100 one-step
exactness) and the draw/parity/impeach reconstructions are in LEARNINGS.md § 2026-11-03
FC-01 CORPUS HAMM-00 design hop — READ THAT SECTION FIRST; everything needed to implement
is there. EXACT NEXT: prototype reference.py:hamm00 in build/ (iterate the 10-year script to
a rich path: complaints, plague, rats, starvation bounds, asserts all intermediates <32767),
then write HAMM-00.PLI + HAMM-00.json per that section, --stages source,derivation, lane B
--evidence build/fc01/corp4, docs § 9 + § 1 row, e2e_gate compile tier, explicit-path commit.
No ocaml/harness changes; ledger ends C352; no push; operator handoff.config.json stays
unstaged. HAMM-00 IMPLEMENTATION HOP IN FLIGHT (2026-11-03, renewal 4/12). Read FIRST
`LEARNINGS.md` § "2026-11-03 — FC-01 CORPUS HAMM-00 implementation hop start": echo witnesses
re-measured byte-exact (consumed ^Z echoes as literal `^Z` + `\r\r\n` — FALSIFIES the design
hop's blank-row reading; unconsumed ^Z never captured — ACCEPTED, corp3 witness); the design
hop's year-1 script is FALSIFIED at S≈2400 (births `5*(20*300+s') = 37250 > 32767` at the
declared gg=4 draw c=5 — violates its own 20a+s≤6553 bound) and at the year-1 rats draw
(gg=3 → c=3 ODD); the d=45 survival arithmetic is ACCEPTED but needs a tuned opening store
(s0≈600-900, iterate). `COND.GE_LE` is REFUSED — port uses strict compares + shift/flag
idioms only (constants ≥ 1); rest of the design hop § stands (draw formula gg*37+11, GET
shape R903/NETWORK, goto same-block, bells/TAB dropped). EXACT NEXT: (1) build
`build/fc01-scratch/hamm00.py` — byte-level stream model (skip=`\r\n`, text items: literals
natural + fixed numerics `%10d`, echo=`L\r\r\n`, exit appends one `\r\n` [C352]; normalize
`re.sub(' +',' ',raw.replace('\r\n','\n'))`, split `\n`, drop ONE trailing empty), game per
the BASIC trace, asserts ALL intermediates ≤ 32767; iterate script to a rich path (price/feed
complaints, plague year, EVEN rats year — not year 1, skip-year, d>0 year); emit expected
lines (echo lines carry trailing `\r`) + console_input (lines joined `\r`, trailing `^Z`
NEVER consumed) + PL/I statement skeleton. (2) HAMM-00.PLI (CRLF ^Z ≤71, header naming
HAMMURABI.bas sha 93fea01f…) + HAMM-00.json (third-party, licence UNVERIFIED, capabilities
from SUPPORTED rows incl IO.GET_LIST/TRAN.GOTO_SAME_BLOCK, notes = removal/substitution
list). (3) `python3 tools/functional_runner.py --stages source,derivation --tests HAMM-00`,
then lane B `--evidence build/fc01/corp4`, ACTUALS verbatim. (4) docs/functional-results.md
§ 9 + § 1 row; `python3 tools/e2e_gate.py` compile tier ACTUALS; explicit-path commit;
renew at safe boundary. No ocaml/harness changes; ledger ends C352; no push; operator
handoff.config.json stays unstaged; third-party bytes never tracked. (Prior: HAMM-00 DESIGN
committed cb223ba/6571212; WKDAY-00 rev3 PASS `21c9f69`.)

HAMM-00 IMPLEMENTATION HOP 3 STATE (2026-11-03, renewal 6/12; HEAD `a5ef608`, build rc=0,
compiler `edce9e0e…`, checkpoint g161 verified CURRENT by hash replay). Read FIRST
`LEARNINGS.md` § "2026-11-03 — FC-01 CORPUS HAMM-00 implementation hop 3": hop 2's draw-residue
table is FALSIFIED (off-by-one draw index — rats fire ONLY at `g0 ≡ 2 or 3 (mod 5)`, c=2 or c=4,
and EVERY year; `g0 ≡ 4` gives NO rats; yield = `(2 g0 mod 5)+1`, so g0=3 → yield 2 / g0=2 →
yield 5; plague years 3,5,7,9 at g0=3 and 2,4,6,8,10 at g0=2; births c=1 at g0=3 → births bound
`20a+s ≤ 32767`). Complaint paths are STATE-FREE → search the accepted-amount SPINE first, then
insert complaints (firability conditions listed in that section). Letting P collapse every year
is FALSIFIED as a verdict strategy (every year feeds ~44% into P1 → 880 `P1>33` → FINK); the
survivable rich shape is one/two survived starve years + the rest SKIP years (`feed ≥ 20(p+1)`)
with acreage kept `a ≥ 7 p_final`. Simulator rewritten as state-based `build/fc01-scratch/hamm00_sim.py`
(silent/emit modes, 6-bit mask, `DUMMY` plan for the year-11 report, `MAXFEEDLINE=12767`, hop-2
bugs fixed: `starve_years` never populated; 865 `PEOPLE DIED!!` and 950 `HATE YOUR GUTS!!` both
take TWO bangs, 567 FOUR). MEASURED SEARCH RESULT this hop: NO rich spine found — DFS
(`hamm00_dfs.py`, budget 30000) reports NO spine at (g0,s0) = (3,900/1200/1500), (2,900), (7,900),
(8,900), and exactly ONE spine at g0=2, s0=1500 whose mask is {skip,starve} with
verdict `impeached-year10` (a LEGITIMATE complete path per the design hop) but whose complaint
insertion FAILED → `rich_g2_s1500.json` NOT written, `spine` only. UNRESOLVED QUESTION: is the
failure the menu, the mask goal, or the bin15 bounds? Next hop should (a) run the spine search
over a WIDER sweep (g0 ∈ {2,3} × s0 ∈ {600..2400 step 100}, budget ≥ 300k, and let
`verdict ∈ {nero,not-too-bad,fantastic,impeached-yearN≥5}` all count as acceptable — the
complaint-firability filter must also try LATER years and all three plant-complaint kinds),
(b) if still nothing, RELAX the declared adaptation legally and record it: e.g. a larger opening
store `s0` with the year-1 report printing a negative `e = 900 − s0` (allowed: `%10d` prints the
sign; declared, not hidden), or `H` declared as `2*A*Y` so `e ≥ 0` at any `s0`, or an
accepted-buy year followed by a sell-complaint year so the sell complaint is firable, and
(c) ONLY then emit expected lines + console_input + skeleton → `spec/functional/tests/HAMM-00.PLI`
/`.json` + `reference.py:hamm00`/`DERIVATIONS` → `--stages source,derivation` → lane B
`--evidence build/fc01/corp4` → docs § 9 + § 1 row → `python3 tools/e2e_gate.py` compile tier →
explicit-path commit. A FAIL stays classified, never laundered. Constraints unchanged: no
ocaml/harness changes, no push, ledger ends C352, operator `handoff.config.json` stays unstaged,
third-party bytes never tracked.

HAMM-00 IMPLEMENTATION HOP 4 STATE — RICH SPINE FOUND (2026-11-03, renewal 7/12; HEAD
`9cbd8dc`, build rc=0, compiler `edce9e0e…`). Read FIRST `LEARNINGS.md` § "2026-11-03 — FC-01
CORPUS HAMM-00 implementation hop 4" — it contains the COMPLETE plan. Hop 3's "no rich path"
was FALSIFIED as two simulator bugs (buy/sell complaints emitted inside the accepted-amount
branch — a complaint is legal in EVERY year; and `insert_complaints`'s unconditional `break`
tried one combo/one kind). MEASURED SPINE (simulator, ignored scratch
`build/fc01-scratch/hamm00_sim.py` fixed + `hamm00_build.py` + `spine_t_300.json`): g0=2,
s0=1500, A=300/H=900/Y=3/P=95/I=5/Q=1; per year (buy, sell, feed, plant) — y1 0, SELL-claim 301
+0, 1352, SEED-claim 298 +200; y2 BUY-claim 43 +0, 0, 700, 300; y3 0, 0, FEED-claim 1588 +900
(SKIP), 300; y4 0,0,520,259; y5 0,0,780, ACRES-claim 301 +300; y6 0,0,480,239; y7 0,0,760,300;
y8 0,0,460, PEOPLE-claim 230 +229; y9 0,0,740,300; y10 0,0,300 (survived starve d=8), 229.
ALL EIGHT mask features (skip, starve, buyc, sellc, feedc, plantc, plague, rats), verdict
**not-too-bad** (P1=7, L=10 → 960/965 extra draw), D1=41, 211 stream lines, 46 fed values (max
1588), every intermediate ≤ 32767. Port law: strict compares only (`t = x+1; if a < t`, plague
`t = q+4; if t > 4`, impeach `t = (p*45)/100; if d > t`); literal divisors 2/4/5/10/20/45/100
with the rats site dispatched on c ∈ {2,4}; VARIABLE division unavoidable and flagged at exactly
three sites (births `x/p`, P1 `d*100/p` and `/z`, `l = a/p`) — first corpus use, a FAIL stays
classified. NOTHING promoted to any ledger (ends C352); no ocaml/harness byte; no emulator run
this hop. EXACT NEXT (authoritative steps in that LEARNINGS § NEXT): write HAMM-00.PLI for this
spine, `reference.py:hamm00` + `DERIVATIONS`, HAMM-00.json (console_input = 46 CR-joined values +
bare `^Z`; removal/substitution notes), `--stages source,derivation`, lane B `--evidence
build/fc01/corp4`, docs § 9 + § 1 row, `python3 tools/e2e_gate.py` compile tier, explicit-path
commit. No ocaml/harness changes, no push, operator `handoff.config.json` stays unstaged,
third-party bytes never tracked.

HAMM-00 IMPLEMENTATION HOP 2 IN FLIGHT (2026-11-03, renewal 5/12; HEAD `9c91e9f`, build
rc=0, compiler `edce9e0e…`, checkpoint g159 verified CURRENT by hash replay). Read FIRST
`LEARNINGS.md` § "2026-11-03 — FC-01 CORPUS HAMM-00 implementation hop 2": the PUT-LIST
inter-item SINGLE-BLANK separator law is MEASURED from the stored TABLE-00 raw capture
(byte simulator joins items with one space; fixed numeric `%10d`; no trailing blank at
line end; literal-literal adjacency stays unmeasured — port uses none); console_input
sending convention confirmed (each fed line ends CR; trailing `^Z` bare, never consumed,
[C113] note quoted); the draw formula locks each ROLE to a residue class when 5 draws
fire per year — rats-EVEN-only-in-later-years is FALSIFIED as unachievable (PROPOSED
resolution: seed g0 ≡ 3 mod 5 → rats c=2 every year incl. year 1, yield 5, births c3=1
so the births bound is 20a+s ≤ 32767, plague years 3,5,7,9, prices 26/21 alternating);
the design's 1300 buy overclaim is FALSIFIED at price 26 (26*1300=33800 overflows — the
simulator's chk() caught it on the first smoke run; claims must keep y*claim ≤ 32767 and
the live-fed q ≤ 12767 for the q+20000<20000 negative-guard form). 880/885 ladder goes to
565 WITHOUT the 560 YOU-STARVED line; P1/L integer-route adaptations asserted vs float.
`build/fc01-scratch/hamm00.py` EXISTS (ignored) with the byte-level Stream model, run(),
rich() predicate and Fail-based search hooks — the smoke run raised the overflow above.
EXACT NEXT (successor): (1) in build/fc01-scratch, sweep g0 ∈ {3,4} × S0 (try 400..2000;
remember year-1 report prints e=900−s0) and DFS the per-year menus (buy claim ≤ 32767/y
and > s/y; buy-accept ∈ {0,5,10,20}; sell claim a+1, accept < a; feed claim s+1, accept
≤ s targeting d ∈ {5..45} or skip q ≥ 20p+1; plant claim a+1/seed-claim/people-claim, accept
≤ a, seed ≤ s, d < 10p) until rich() + all chk/asserts pass and verdict ≠ fink-ladder;
(2) emit expected lines (echo lines carry trailing `\r`; [C352] framing; exit rule: a bare
final put skip yields ONE trailing "" after the drop-one-empty split law), the console_input
string, and the PL/I statement skeleton; (3) hand-port to `spec/functional/tests/HAMM-00.PLI`
(CRLF ^Z ≤71 cols; header names HAMMURABI.bas sha 93fea01f…; strict compares with
constants ≥ 1 only — weak tests as x < N+1 forms; shift form t=q+4>4 plague guard;
divisors: literals 2/5/10/20/45/100, variables p,c,z,q/20 — run-unwitnessed first use,
flagged; goto same-block labels; no apostrophes in literals — WASN'T rewritten); put
`hamm00()` into reference.py + DERIVATIONS mirroring the port exactly; (4) HAMM-00.json
(third-party, licence UNVERIFIED; capabilities incl IO.GET_LIST, TRAN.GOTO_SAME_BLOCK,
DECL.FIXED_BIN15, IO.PUT_LIST_FIXED, IO.PUT_SKIP, EXPR.REL_FIXED_EQ_K; notes = full
removal/substitution list: bells/TAB/banner dropped, RNG formula with seed g0 declared,
P1/L integer adaptation, rats-every-year residue, negative-input branches compile-only);
(5) `python3 tools/functional_runner.py --stages source,derivation --tests HAMM-00` then
lane B `--evidence build/fc01/corp4 --json-out build/fc01/corp4/records.json`, ACTUALS
verbatim (variable division is run-unwitnessed — a FAIL stays, classified, expectation NOT
laundered); docs/functional-results.md § 9 + § 1 row; `python3 tools/e2e_gate.py` compile
tier; explicit-path commit (LEARNINGS, PROGRESS, HANDOFF prose, the triple, docs). No
ocaml/harness changes; no push; ledger ends C352; operator handoff.config.json stays
unstaged; third-party bytes never tracked.
Nothing of it had begun (measured at `6a35b9c`: no `stage_files` anywhere in
`tools/functional_runner.py`; `file_expectations` is only the pre-existing fail-closed rejection
at lines 127/398-400). Hop-4 close-out `6a35b9c` and Batch-B REV2 `a5815a8` stand untouched; the
hop-4 file-I/O survey + PROPOSED design stay in `LEARNINGS.md` as a RECORD, cancelled as a plan.

NEW PRIORITY — **adapt the eight operator-selected historical programs into a representative
PL/I-80 functional corpus**, autonomously across renewals:

**HOP STATUS 2026-11-03 (this chain):** WKDAY-00 COMPLETE — rev3 **PASS** on lane B
(build/fc01/corp3; double-run byte-equal; source sha `2263d38f…`; docs § 8 + § 1 row written).
Rev1 measured the `> 0` refusal (corp1), rev2 the SILENT `/365` low-byte miscompile (corp2,
narrowed to `compiler` by the .COM byte run) — both `my-gap`, kept as written; NO expectation
re-derived. REMAINING NOW: (a) run `python3 tools/e2e_gate.py` (compile tier) and record ACTUALS
as printed; (b) explicit-path commit (`spec/functional/tests/WKDAY-00.PLI`, `WKDAY-00.json`,
`docs/functional-results.md`, `LEARNINGS.md`, this file); (c) refresh+attest the checkpoint
(`/handoff finalize` or `handoff_finalize`), renew at the safe boundary; (d) proceed to HAMM-00
(Hammurabi, program 2) per the exact procedure below, applying the corpus rule: literal divisors
≤ 127, ordered-compare constants ≥ 1 (LEARNINGS 2026-11-02 CORPUS hop 2). Details in
LEARNINGS 2026-11-02 CORPUS hop 2.

| # | program | original | corpus id | note |
|---|---|---|---|---|
| 1 | Weekday | BASIC | `WKDAY-00` | START HERE — design fully derived, see § "WKDAY-00 exact" below |
| 2 | Hammurabi | BASIC | `HAMM-00` | |
| 3 | Hangman | BASIC | `HANG-00` | |
| 4 | Amazing | BASIC | `AMAZ-00` | maze: 2-D grid ⇒ AGG.MULTIDIM is REFUSED; flatten or record |
| 5 | Tic-Tac-Toe | BASIC | `TICT-00` | two upstream listings (tictactoe1/2) |
| 6 | Life | BASIC | `LIFE-00` | |
| 7 | Dhrystone | Pascal | `DHRY-00` | upstream is a .SHAR; do NOT execute it |
| 8 | FFT | PL/I (Rosetta) | `FFT-00` | `pli/FFT-reference.pli` |

Sources: `build/functional/fc01-sources/` (ignored working state; operator's
`fc01-fetch-sources.sh`; `sha256sum -c SHA256SUMS` rc=0 measured 2026-11-02). They are RESEARCH
COPIES: read `NOTES.txt` — the BASIC URLs are a moving branch and `dhry-pascal.shar` must never be
run. Upstream bytes are NEVER copied into tracked files: each program is an ADAPTATION with
`provenance.origin: "third-party"`, the upstream URL and licence recorded in `provenance.note`,
and the algorithm re-expressed in PL/I-80.

EXACT PROCEDURE per program (reuse the harness AS IT STANDS — no new infrastructure, no runner
edits):
1. Read the upstream listing; write the behavioural spec FIRST (fixed inputs, complete expected
   console stream) into `spec/functional/tests/reference.py:<id>` — derived, never captured (L3).
2. Write `<ID>.PLI`: CRLF, `^Z`-terminated, ≤ 71 columns, header comment naming the adaptation and
   its upstream; keep every line inside the measured 79-col PLILIB wrap; obey README § 7 and the
   pinned-refusal list already in the Batch-A notes.
3. Write `<ID>.json` (schema `pli80-functional/1`; Lane B; `capabilities` = real COVERAGE ids, no
   forbidden/REFUSED/DIVERGENT/UNTESTED rows). Set `console_input` when the program reads — the
   harness already supports it (`^Z` default; `##SEND`).
4. Run `python3 tools/functional_runner.py --lane B --tests <ID> --evidence build/fc01/corp<N>
   --json-out build/fc01/corp<N>/records.json`; record ACTUALS (verdict, stage, attribution, byte
   sizes) — PASS/FAIL/BLOCKED/UNKNOWN as measured, never laundered. Where the harness CANNOT test
   the program adequately, RECORD the limitation in `docs/functional-results.md` and move on; do
   not extend the harness.
5. Update `docs/functional-results.md` (new section per batch) + § 1 rows; run the fast tier
   `python3 tools/e2e_gate.py` (compile tier only — runtime/link-run stay delegated to rune-ci,
   and existing CI results do NOT cover new corpus programs unless explicitly added there).
6. Commit explicit paths only; renew at the safe boundary per `handoff.config.json`.

**WKDAY-00 exact (first program; everything needed is already derived — LEARNINGS 2026-11-02
override section, PROPOSED entry; read that entry, do not re-derive from scratch):**
1. `spec/functional/tests/WKDAY-00.PLI`: CRLF, `^Z`, ≤ 71 cols; header comment naming
   `build/functional/fc01-sources/basic/WEEKDAY.bas` as the adapted original (upstream URL
   `https://raw.githubusercontent.com/coding-horror/basic-computer-games/main/95_Weekday/weekday.bas`,
   sha256 `ccb9a9e5…`); `wkday00: procedure options(main);`; declare all FIXED scalars +
   `t(12) fixed` (month table 0,3,3,6,1,4,6,2,5,0,3,5 literal-assigned — no `READ`/`DATA`, no
   `INITIAL`); TODAY=3/24/1979, TARGET=7/16/1969, both FIXED **non-negative** operands only; every
   `INT(x/n)` becomes `x / n`; `A - (A/7)*7` for mod-7 exactly as the original does it; the
   `M > 2` / leap-adjust branch (`T1 = Y - (Y/4)*4`) and the `B = 0 → 7` fix-up verbatim; the
   was/is/will-be compare `(Y1*12+M1)*31+D1` vs `(Y*12+M)*31+D` — keep operands small enough for
   FIXED BINARY(15) or the multiply overflows: use it only if measured to fit, else replace with
   the equivalent sign-of-difference test and RECORD the substitution; day name by 7 `if b = n`
   branches printing literals; Friday-the-13th literal branch; the pre-1582 refusal literal; the
   30-month/365-year age arithmetic (`A8 = I5*365 + I6*30 + I7 + I6/2`) and the three `.35/.17/.23`
   blocks as `K1 = A8*F/100` with integer F literals 35/17/23 (NO fractional literals — refused).
   First output statement `put skip list(...)` ⇒ expectation starts `""`; end with a non-SKIP PUT
   so no trailing `""`. Every line ≤ ~60 raw cols.
2. `reference.py:wkday00` — Python port ALREADY verified against `datetime` (3/24/1979 Sat,
   1/1/1970 Thu, 2/29/1980 Fri, 12/31/1999 Fri, 7/4/1776 Thu); derived values for the chosen pair:
   `b = 4` → WEDNESDAY (7/16/1969 real weekday is Wednesday — agrees), WAS (1969 < 1979),
   age 9 y 8 m 8 d, `A8 = 3537`, SLEEP 3/4/22, EAT 1/7/26, PLAY 2/2/23, retire 2034.
3. `WKDAY-00.json`: `provenance.origin: "third-party"`, author "DRPLi FC-01 corpus — adaptation of
   the BASIC Weekday listing (coding-horror/basic-computer-games 95_Weekday, public-domain-era
   source; license UNVERIFIED — record in note)", note naming `build/functional/fc01-sources/
   URLS.tsv` + `SHA256SUMS` (`ccb9a9e5…`); `capabilities` from SUPPORTED rows only (e.g.
   `AGG.ARRAY_1D_FIXED`, `AGG.VAR_INDEX_LADDER`, `LOOP.DO_TO_BY`, `IO.PUT_LIST_FIXED`,
   `IO.PUT_SKIP`, `EXPR.REL_FIXED_EQ_K`, `DECL.FIXED_BIN15`); link_target `WKDAY00`; sha256 of the
   committed .PLI bytes.
4. `python3 tools/functional_runner.py --lane B --tests WKDAY-00 --evidence build/fc01/corp1
   --json-out build/fc01/corp1/records.json` → record ACTUALS as executed; then docs
   `docs/functional-results.md` § 8 + § 1 row; `python3 tools/e2e_gate.py` (compile tier only).
5. Documented unsupported/removal list for WKDAY-00 (must appear in the spec `notes` AND docs
   § 8): console `INPUT` (×2) replaced by fixed declared dates; `DEF FNA/FNB` inlined (built-ins/
   function refs refused); `READ`/`DATA` → literal assignments; `TAB()` positioning and the
   banner `PRINT`s dropped (no column PUT — `FILE.PUT_POSITION`/counted EDIT refused); `GOTO`/
   `GOSUB` structure re-expressed as `IF`/`DO` (goto is supported, but the port is clearer); the
   original's 30-day-month/365-year calendar convention KEPT as declared behaviour, not corrected.

Standing constraints: NO `ocaml/` changes; goldens/`artefacts/`/`oracle/disks/` untouched; no push;
no new CI framework; no mass documentation cleanup; operator `handoff.config.json` stays UNSTAGED;
compiler-gap findings are classified `my-gap`/`dr-refuses`/`unmeasured` (PROTOCOL #3) and recorded
without promoting anything to `spec/CLAIMS.md` (ledger still ends at C352) — a functional run is not
a DR claim.

(Superseded hop-5 instruction, kept as written per PROTOCOL #2: FC-01 hop 4 PARTLY DONE. LANDED: Batch-B REV2 `a5815a8` (FLT-01 direct `(a+b)=6.5` refuses
verbatim 'computed FLOAT operand in a comparison is unsampled'; BUILTIN-00 length-first refuses
'int subset'; both COMPILE FAIL attr=compiler at build/fc01/batchB-rev2; docs § 7 + § 1 rows;
LEARNINGS hop-4 section carries the full file-I/O survey — READ IT FIRST).
EXACT NEXT (hop 5):
(1) Harness extension tools/functional_runner.py — design is in LEARNINGS 2026-11-02 hop 4
(PROPOSED): `stage_files` top-level field + `expected.file_expectations` implementation,
SOURCE sha pin, DERIVATION two-way check (reference.py `derive()` must accept the file funcs
— return a latin-1 string; json round-trips it), export in _run_lane_b AFTER RUN and BEFORE
run.cleanup() into per-seq subdir (cpmwork export refuses clobber), ASSERT byte-compare,
Lane-B-only validation, README § 3/§ 4 amendments, hostile-suite case C17 (FakeRun stub
export returns a PATH — pin calls via run.calls), suite self-count printed.
(2) FILE-00 (output; E16D shape, title 'F00OUT DAT', derived payload per [C295]/[C300]/[C280],
<128 B, 0x1A pad) + FILE-01 (input; dcl inf file → stage INF.DAT fixture `7\r\n8\r\n` + ^Z,
gets print X1/X2) specs/programs/derivations; run lane B → build/fc01/fileAB; docs § 8.
(3) ONUNIT-00 ONLY AFTER a pre-registered fc01-fileio oracle round measures DR named-file
ENDFILE firing (hop-2 pattern: probes FCFO* + HYPOTHESES + BASELINE-MINE + linkrun.py
STAGE_IN/EXPORT_OUT entries committed BEFORE any DR PLI.COM call; claim C353+; results in
spec/lab-evidence/fc01-fileio/). Named-file ON firing is UNMEASURED — do NOT derive an
expectation without it.
Constraints unchanged: NO ocaml compiler changes; goldens/artefacts untouched (new fc01-fileio
goldens would be ADDITIVE); explicit-path commits; no push; operator handoff.config.json stays
unstaged; cap per handoff.config.json.
## Verified milestones (provenance: `docs/history/README.md`; evidence: `spec/lab-evidence/`)

- E2E-48/P1 — 24/24 probes byte-identical + registered, claims C309–C316, gate 1098/0: `992ccad`.
- E2E-48/P2c CLOSED — arms `14c7321`…`e21281a` era, RETIRE promotions, claims C317–C320,
  FULL GATE 1109/0 negative 182/182: `f67cc6d`; COVERAGE rows + appends: `ef0a198`.
- E2E-48/P2d — run 1 botched (>72-col comments; kept `67bf83c`), wrap `60a2c06`, run 2 10/10
  `d28ff5e`; claims C321–C326 `aa4b5b4`; six arms `6545b5d`/`6491981`/`a72ce43`/`18a06c0`/
  `1e8acb2`/`e21281a`; registration + FULL GATE 1120/0, negative 181/181, census 15/0/26/0,
  INVENTORY 1301: `adbfa2a`; COVERAGE 113 rows 0 errors: `218b474`.
- E2E-48/P2e round 5 — pre-registration `421656a` committed BEFORE the oracle; one run
  7 ok / 8 (E48E6 `BIT REQ` = dr-refuses; P-E6 MISS kept in RESULTS §1); goldens + RESULTS
  `e2b77ba`; lowering arms 1–3 `d18c6ab`/`bab0d16`/`e49902a` (arm-3 spec archived in
  `docs/history/2026-10-31-p2e-arm3-closed.md`).
- E2E-48/P2e CLOSED — arm 4 `046046a`, arm 5 `c215ea0`, step 6 `809af8d`+`0e64c8b`, docs
  `0749fa6`; claims C327–C332, inventory 1127, coverage 118 rows 0 errors; FULL compile-tier
  GATE rc=0 ACTUAL 1127/0 (neg 181/181, div 9/9, census 15/0/26/0, prose clean) measured at
  `0749fa6` 2026-10-31; closing prose archived in `docs/history/2026-10-31-p2e-closed.md`.
- E2E-49/P1 CLOSED — operand-inverted FIXED compares (member LEFT of literal): pre-registration
  `9b3d860` before the oracle; run 4 ok/4; arms `fee935e`/`b044b7c`; claims C333–C336 + labelled
  C330 CORRECTION; registration panel 1131, coverage 122 rows; FULL GATE rc=0 1131/0 (neg 181/181,
  div 9/9, cov 122/0/0, census 15/0/26/0, prose clean) measured at `0a8ceff`; archive
  `docs/history/2026-11-01-e49p1-closed.md`.
- E2E-49/P2 CLOSED — member-vs-member FIXED TEST compares: pre-registration `3bd9417` before the
  oracle; run 5 ok/5; arm 1 `b1e9221` (stacked parking + equal-extent collapse); claims C337–C341;
  registration panel 1136, coverage 125 rows 0 errors (`0abf1c1`/`8c1d2ee`/`d5983e8`); FULL GATE
  rc=0 **1136/0** (neg 181/181, div 9/9, cov 125/0/0, census 15/0/26/0, prose clean) measured at
  `d5983e8`; archive `docs/history/2026-11-01-e49p2-closed.md`.
- E2E-49/P3 CLOSED — composite FIXED/TEST bank (equal-attribute collapse in BOTH literal
  templates, qualification invisible, over-extent literal-LEFT, ordered relations):
  pre-registration `3659f5d` before the oracle; run 14 ok/14, NO dr-refuses; arms
  `a540fa7`/`0a1b80c`/`cde3258`; claims C342–C347 + labelled corrections at C335–C338 and
  the citation fix at C346 (`4df35bb`); registration panel 1150, coverage 129 rows 0 errors
  0 warnings (`4b51bc0`/`8d3b024`/`8771e1e`); FULL GATE rc=0 **1150/0** (neg 181/181,
  div 9/9, cov 129/0/0, census 15/0/26/0, prose clean) measured at `4df35bb`, recorded
  `1f611f5`; two-generation archive `docs/history/2026-11-01-e49p3-closed.md`.

- E2E-49/P4 CLOSED — composite FIXED/TEST bank (ordered relations with a LITERAL on BOTH `?SCCCM` literal templates with the ORDER-law rekey, qualification invisibility transferred, the complete unequal-extent relation matrix NO-ARM, `^( )` on the complement object):
  pre-registration `328eb3f` before the oracle (BASELINE-MINE binary `398fa2c`); run 24 ok/24, NO dr-refuses (18 my-gap, 6 exact); arms `c515377`/`ec904c1`/`47c2194`; claims C348–C351 +
  labelled corrections at C335/C337/C344/C346 (`9c42f3b`) and the WORDING correction at C348 (`5b0ccde`); registration panel 1174, coverage 133 rows 0 errors 0 warnings
  (`cc43963`/`dbaf004`/`5aeac87`); FULL GATE rc=0 **1174/0** (neg 181/181, div 9/9, cov 133/0/0, census 15/0/26/0, prose clean) measured at `5b0ccde`, recorded `882f77c`;
  four-generation archive `docs/history/2026-11-01-e49p4-closed.md`.


- E2E-50/P1 CLOSED — functional dashboard (evidence-infrastructure audit; capability taxonomy 30 rows validated; 68-program inventory in 3 origin classes; deterministic read-only dashboard + 30 tests; generated docs/functional-status.md views A–E incl. ranked §E candidate shortlist; stale README rolling status replaced; labelled LEARNINGS corrections incl. RUNTIME 71-names falsification). Deliverables `4cad695`; no compiler/oracle/gate run; no scientific byte.

## Completed

*Scientific — recorded, not re-run by this session:*
- `PUT FILE … SKIP` behaviour measured on DR and lowered byte-exactly: `E46N11`–`E46N22`
  bank, 18 specimens added → **1074 byte-exact / 0 fail** recorded in
  `spec/lab-evidence/e2e42-p2c/RESULTS.md` §8; runtime panel 71/71 as recorded.
- Gate tiering + `--link-run` able to fail; slow CP/M arms delegated to the external
  `rune-ci` builders (`GATE-TIERS.md`, `spec/notes/rune-ci-external-gate.md`).
- The `timeout-or-hang` collapse in `oracle/run.py`/`linkrun.py` re-measured by exit code:
  51 timeouts, 2 emulator deaths (`PD7`, `PD9`), 2 that do terminate (`RFACT`, `V5`) —
  `[C308]`, and the `HANG_ARMS` / `NO_RUN_ARMS` / `NO_LINK_ARMS` split in `tools/e2e_gate.py`.

*Infrastructure — performed and verified by this session (see `HANDOFF.md` for the boundary):*
- `.gitignore`: appended only the `# Pi Handoff runtime state` / `.pi-guard/` rule; all
  pre-existing oracle/golden/build/thirdparty rules verified still matching.
- Extension installed at `.pi/extensions/context-guard/{index,core,config,checkpoint,renewal}.ts`,
  taken from the pinned Git revision (bytes verified by SHA-256 and blob id against
  `v0.1.0-dev.1` / `2ea6219`); nothing else from the source repo was copied.
- Skill installed at `.agents/skills/pi-handoff/{SKILL.md,references/bootstrap.md,references/commands.md}`.
- `handoff.config.json` written: `readOnly: true` during validation, `enforceClosing: false`,
  `autoCheckpointAtHandoffLevel: false`, renewal disabled, `generationReserve: 20000`
  (initial policy value, not yet tuned).
- Durable files created: `AGENTS.md`, `GOAL.md`, `PROTOCOL.md`, `HANDOFF.md`, `PROGRESS.md`,
  `LEARNINGS.md`.
- **Phase D (read-only) passed in the real Pi runtime**: extension loaded with no import/TS
  errors; `/guard status` reported read-only mode + the real model/window/reserve; `/handoff
  verify` reported `missing` without writing; `/handoff ready check` evaluated without
  attesting; `/guard simulate 30000` → level 1, `/guard simulate 10000` → level 3 with **no**
  checkpoint written; `/handoff` reported a dry run; no `.pi-guard/` directory was created; every
  tracked file hash, the ignored-file count (471 102) and the profile settings were unchanged.
- **Phase E (writable) passed**: `/handoff` → `g1-01ad31c23339`, generation 1,
  content-delta `initial`, freshness `current`; `/handoff ready check` → READY with four blocking
  PASSes; `/handoff ready` → attested; both blocks shared one transactional identity.
  A level-3 automatic checkpoint (`checkpoint-kind: auto`) then preserved a substantive
  "Last verified state" line and a "Guard notes" block **verbatim**, leaving all manual prose
  outside the managed blocks byte-identical, and left `GOAL.md`/`LEARNINGS.md` untouched.


## Pending
- **LOAN2's new prescan my-gap** (`variable i declared with conflicting kinds; decimal pool prescan
  needs one unambiguous type map [TBD]`): measured cause, fix NOT attempted. `codegen.ml:12460-12490`
  builds ONE global `pd_vars` name -> vkind map for the DEC-pool prescan, and LOAN2 declares `i`
  `fixed decimal(4,2)` at line 32 and `fixed bin` at line 211 — two scopes, both legal, DR accepts
  (its golden exists). Making the prescan scope-aware touches ~15 `List.assoc_opt … cx.pd_vars`
  call sites whose prescan deliberately runs WITHOUT statement context, so it is a design change,
  not an arm. It needs its own measured plan; do not start it on faith.
- CREATE remains NOT byte-exact; its measured blocker is still the front-end `%include` gap
  (`pli80c.ml` never expands INCLUDE). Do NOT implement any unmeasured shape from the
  [TBD] list in RESULTS section 3.
- **Renewal chain:** the E2E-48 phase chain closed at its configured cap; its state file is
  archived under `.pi-guard/archives/` and a new session starts a fresh count per
  `handoff.config.json` — the config and `/guard status` are authoritative for enablement,
  autoRenew and cap; this file quotes no numbers.

## Verified evidence

The FULL compile-tier gate rc=0 at HEAD `545dcf1` with ACTUALS AS PRINTED (byte panel 1174
byte-exact / 0 fail of 1174; negative 181/181, E46K14 `[dr-refuses]` UNMOVED; divergence 9/9;
coverage 133/0/0; census 15/0/26/0 UNCHANGED; prose 5 active clean) was MEASURED by the
step-8 session and recorded at `d648bcd` — NOT re-run by this docs-only close (the mission
required no compiler/oracle/gate/emulator run to close). Measured by THIS closing session
(2026-11-02): HEAD `e7664ed`, tree clean apart from the operator's `handoff.config.json`
edit; checkpoint g131 **current** via replay of the guard's strip+rstrip SHA-256 prose law;
the 23 close-archive blocks re-extracted from `459f51e`/`a6163ef`/`149c6e2`/`690c3a1`/
`218c9be`/`ec9d396`/`545dcf1`/`d648bcd`/`68831ff`/HEAD and byte-compared — **23/23
BYTE-EXACT**; every line lost by any superseded generation verified present verbatim in the
archive. Round evidence: `spec/lab-evidence/e2e50-p2/{PLAN.md,step6/RESULTS.md,
step7/RESULTS.md,REPORT.md}`, `spec/functional/tests/`, ignored evidence roots under
`build/functional/`; earlier rounds `spec/lab-evidence/e2e48-*/`, `e2e49-p*/`; closed-round
records: `docs/history/`.
<!-- guard:begin checkpoint -->
checkpoint-schema: 3
checkpoint-generation: 164
checkpoint-id: g164-3c3faa102b9f
checkpoint-kind: auto
content-delta: new
readiness: unattested
guard-level: 3
checkpointed: 2026-11-02T12:52:02.014Z
source-goal: 730790b648a1e1d14b76243cfe8bc17eea2ba9cd8527f204f9c8d4dbcc527c9d
source-progress: 335a317e95ea84217e7d0812f2f7e625c48a09ba9ac4786a4c985d42804ac7f8
source-handoff: 9ce12745272283e88e121735ff19df49bd18728b337f95b3f9b8a96a52a7ff8a
source-learnings: fdb559ca4bc36b37156484034357b94207496073ab4cf5743aad33e3dde38cdf
source-config: 43186947fdaf3f3b9f425f8ce1b144a8227ce1d7bec2b7aeafb32e9f0572dea8
next-action: ` below. TABLE-00 and
  TABLE-01 executed to **PASS** on Lane B after (a) the harness F1 anchor fix in `tools/functional_runner.py`
  (`_run_lane_b`: capture now ends at `D>`/`I/O ran`/`\Z` WITHOUT eating the program's final CRLF;
  a region not newline-terminated before its terminator is `console-terminator-ambiguous` UNKNOWN,
  fail closed) with hostile-suite case C15 (12 checks; suite self-count **194**, all pass), and
  (b) a TABLE-01 **output-statements-only** revision isolating the test from PLILIB's measured
  79-col wrap (source sha256 `4881f187ef1ad9651c48950b76a6cdd959fdcc980ef989580a0fbfa43c0b0863`,
  1366 B, CRLF/^Z/≤71 cols; algorithm/inputs/invariants unchanged; expectation derived from the
  declared design + README § 6 law via `reference.py:table01`, never captured). Executed ACTUALS:
  TABLE-00 .REL 896 B, COM 7552 B, 93 console bytes, complete-stream 2 lines; TABLE-01 .REL 1536 B
  (code=644 data=50), COM 7808 B, 178 console bytes, 3 lines; LINK both `parse_undefined=[]`;
  RUN `done` witness; `--double-run` captures byte-equal. Evidence roots (ignored working state,
  gitignored `build/`): baseline FAIL reproduction `build/functional/fs01-baseline/`, PASS run
  `build/functional/fs01/`, double-run `build/functional/fs01-double/`, Lane-A unchanged check
  `build/functional/fs01-laneA/` (FX-00 PASS, FX-01 FAIL `emulator` intended). Report:
  `docs/functional-results.md` § 5.
- Preserved/untouched: P2 FAIL evidence `spec/lab-evidence/e2e50-p2/step6/RESULTS.md`; all
  goldens, `artefacts/`, `oracle/disks/`, manuals, `ocaml/`, `spec/CLAIMS.md` (ledger ENDS C351),
  `spec/COVERAGE.tsv`; PLILIB wrap law stays `proposed` (NOT characterized — FS-01 boundary).
  Compiler binary used as-built: `pli80c.exe` sha256 `edce9e0e…` (recorded in every PASS record).
- Prior round: E2E-50/P2 CLOSED `876ed9e` (gate ACTUALS 1174/0, 181/181, 9/9, 133/0/0, census
  15/0/26/0, prose 5 clean recorded `d648bcd`; close archive `docs/history/2026-11-02-e50p2-closed.md`).
<!-- guard:end checkpoint -->

## Blockers

- Nothing is half-edited at this boundary; every item below is recorded evidence, not a
  guess.
- **Missing evidence is the limit, never a licence to guess** (`PROTOCOL.md` #4). The
  E2E-49/P4 RESULTS §3 remainders (with the surviving P1/P2/P3/P2e §3 entries) stay named
  refusals until a pre-registered round measures them: NO runtime semantics for `?SCCCM`
  (what it returns and how JNC/JC/JZ read it is NOT claimed — byte tier, no `spec/RUNTIME.txt`
  row may come from these families); STORE value or STORE target with any of the new shapes
  (relation-with-literal, bare-in-relation, negated compare); literal-vs-literal in any
  relation; BASED members in a condition; fixed-member truthiness; `<>`/`><` spellings; `&`/`|`
  composition of conditions; `^( )` over a relation WITH A LITERAL operand; `^( )` over an
  over-extent or a BARE spelling; `^(` `^=` `)` double negation; ordered relations with a
  literal at UNEQUAL attributes beyond the G3..G6 `>`/`<=` sample; bare spellings in the
  equal-length literal template under a relation (only bare `=` is measured, E49D4); the
  equal-attribute `>` collapse inside a relation (NEVER sampled in any bank — the [C348]
  WORDING CORRECTION); `^=` over a ladder; over-extent in INITIAL/STORE; bare `-0` spelling;
  runtime length rewrite; empty-varying PUT output; PUT EDIT of a bit item.
  Shapes REMOVED from this list by P4 MEASUREMENT: ordered relations with a LITERAL operand on
  BOTH literal templates ([C348]); BARE spellings inside an ORDERED relation, member-pair mixes
  included ([C349], extending [C344]); the unequal-extent STRICT-vs-WEAK combinations "beyond
  F2/F4's single pair" — the COMPLETE 4x2 matrix is measured, no arm ([C350]); `^( ... )`
  composition over the four goldened compare shapes ([C351], the un-witnessed negations above
  keep refusing) — the P3-era wording is preserved verbatim in
  `docs/history/2026-11-01-e49p4-closed.md`.
- E2E-50/P2 functional axis (measured, recorded; no byte-tier effect): Lane-B ASSERT framing
  F1 (harness anchor law — P3-a proposal) and F2 (DR PLILIB 79-col print-wrap — declare from
  the oracle side before any expectation change, P3-b); the free core cannot host PLILIB
  programs (BDOS 25 first call, measured; full census UNMEASURED); Package-A licensing =
  operator decision. Details `spec/lab-evidence/e2e50-p2/REPORT.md` §2/§4/§5.
- CREATE is NOT byte-exact; measured front-end blocker: `pli80c.ml` never expands
  `%include` (proposal in `LEARNINGS.md` is `proposed, unverified` — needs its own
  pre-registered round).
- LOAN2's `conflicting kinds` prescan my-gap is a design change, not an arm (see Pending).

- E2E-50/P2 CLOSED — functional-testing foundation + emulator/redistribution audit: audits
  `docs/emulator-audit.md`/`docs/functional-testing.md`/`docs/functional-results.md`; schema
  `pli80-functional/1` + TABLE-00/01 + FX-00/01 + `reference.py` under `spec/functional/tests/`;
  harness `tools/functional_runner.py` + hostile suite 182 checks self-counting; executed
  verdicts FX-00 PASS, FX-01 FAIL/`emulator` (intended), TABLE-00/01 first functional execution
  of a DRPLi-compiled program (CONTENT ≡ REFERENCE; ASSERT FAILs framing F1/F2, attr
  `undefined`); census BDOS-25 free-core blocker measured. Deliverables `d648bcd` (+`68831ff`);
  FULL GATE rc=0 1174/0 (neg 181/181, div 9/9, cov 133/0/0, census 15/0/26/0, prose clean)
  measured at `545dcf1`, recorded `d648bcd`; 23-block byte-verified close archive
  `docs/history/2026-11-02-e50p2-closed.md`.
