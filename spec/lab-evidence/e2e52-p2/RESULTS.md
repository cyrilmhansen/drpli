# E2E-52/P2 RESULTS — DEC formal copy-in: the E52G closure round

Operator brief 2026-11-04, opened on top of E2E-52/P1 CLOSED (`6de72c5`, checkpoint
`g272`, ledger ENDS **C358**). Objective: make `probes/E52G.PLI` whole-file byte-exact
against `golden/e52p1/E52G/E52G.REL` (256 B, sha256
`39b3d7cfe775c039d25b3791ed2f71b3e333509ca1193f3759ce46a850134c67`) via the P1
PROPOSED copy-in-temp arm, then register. **No new claim is promoted by this round:
[C358] already states the DR law; this round implements my side of it.**

Chain (explicit-path commits, no push):
- `a365686` — PLAN.md (this directory) committed BEFORE any compiler byte.
- `d67a263` — ARM: Bind `cs_copies` + codegen `?DLDOP/?DSTOP` pair + descriptor
  retarget (binary sha256 `85bf7a26…`).
- hop 1 durable record `c34c690`; HANDOFF pointer `546c70a`; renewal boundary `01bf2df`.
- `dca9219` — hop 2 REGISTRATION: E52G in SPECIMENS + sanctioned `--update-inventory`
  1195→1196 + FULL gate post-update rc=0.
- `90582a5` — hop 2 COVERAGE row update + stats via the validator's own write path.
- this commit — LOAN2 rerun record + this RESULTS.md + close prose.

## 1. The difference (P1 §5 residual, as pre-registered in PLAN §1)

At P1 arm `6a4c554` the DEC POOL half of E52G was already byte-identical to DR
(pool 3+5 @`0000`/`0003`, outer `i` 3 B @`0008`); the whole file was not. Residual,
mine (sha `6ea285ba…`) vs DR golden:

| feature | DR golden | mine (P1 arm) |
|---|---|---|
| arg-pointer block @`000B` (2 B) | DATA word RELOC → `0x000D` | RELOC → `0x0008` (actual cell directly) |
| main-side copy-in temp | 5 B @`000D`, UNinitialised (no DATA bytes) | absent |
| formal pointer cell | 2 B @`0012` | 2 B @`000D` |
| `LINK-DEF-DATA-SIZE` | `abs 0014` (20) | `abs 000F` (15) |
| copy-in pair in MAIN | `21 r8 / 3E 04 / CD ?DLDOP` then `21 rd / 3E 09 / CD ?DSTOP` @`0016–0025` | absent |
| `LINK-DEF-CODE-SIZE` | `code 004A` (74) | `code 003A` (58) — delta exactly the 16-byte pair |

The callee side (`5E 23 56 EB / 22 r<ptr>` prologue; store through `2A r<ptr>` +
`?DSTOP`) already existed on mine; only its offsets shift once the temp is allocated.

## 2. The mechanism (arm `d67a263`, per pre-registered PLAN §2–§3)

* **Single layout authority — Bind owns the temp.** `Bind.call_site` gains
  `cs_copies : int option list` (pool-exclusive offsets, same convention as
  `cs_slot`/`cs_temps`); allocated in `section2`'s phase-2 pass by advancing the
  SAME `cur`; size = `bytes_of (RTdec (pf, sf))` — the same sizing authority as
  every declared DEC cell ([R507]). Codegen NEVER allocates for this rule: it
  consumes the recorded offset (adding `st.base`) and cross-checks the precision
  pair from its own type maps.
* **Trigger (measured shape ONLY):** internal, non-recursive, non-`RECURSIVE`
  callee; bare `Eident` actual declared in the CALLER's OWN rows (not a caller
  formal — the E27B forwarding route —, not STATIC, not an array head, not a
  deref); `RTdec (pa, sa)` actual vs `RTdec (pf, sf)` formal with `sa = sf` and
  `pa < pf` (widening at equal scale — the measured `dec(4,2) → dec(9,2)` family).
* **Emission** (per matched argument, inside the static-descriptor arm, BEFORE the
  `LINK-SET-LC data` block-initialisation record, matching the golden's file order):
  `LXI H,*A(actual) ; MVI A,pa ; CALL ?DLDOP` then `LXI H,*A(temp) ; MVI A,pf ;
  CALL ?DSTOP`, and the descriptor word `RELOC data` retargets from the actual to
  the temp. Equal precision AND equal scale keeps the untouched DECPOLY
  by-reference route ([R2037]/[R2038]/[R725]).

## 3. Predictions vs measured

PLAN §4 (derived from [C358] + the golden reldump, BEFORE any trial compile with
the arm) predicted for E52G: DATA `0000–0007` pool unchanged, `0008–000A` outer `i`
unchanged, block @`000B` RELOC → `data 0xd`, 5 B temp `000D–0011` with NO DATA
bytes, pointer cell `0012–0013`, `LINK-DEF-DATA-SIZE abs 0014`; CODE: 16-byte pair
@`0016–0025`, the record trio between `0025` and `0026`, call block `0026–002E`, q
body at `002F`, `RELOC code 0x47` / `?STOPX`, `LINK-DEF-CODE-SIZE code 004A`;
verdict **whole-file cmp byte-identical** (sha `39b3d7cf…`), record order and
padding included.

MEASURED (hop 1, arm `d67a263`, binary `85bf7a26…`): whole-file `cmp` **rc=0 FIRST
TRY** — mine sha `39b3d7cf…` == golden; code 74 = `0x4A`, DATA 20 = `0x14`; exactly
the prediction, NEVER fitted. **ZERO MISS in this round** (contrast P1's kept §1
MISS): every PLAN §4 prediction held byte-for-byte on the first attempt.

Re-measured at the registration hop (hop 2, same binary, positional compile to
ignored scratch): `ocaml/_build/default/bin/pli80c.exe probes/E52G.PLI
build/e52p2/E52G.REL` rc=0 (`wrote build/e52p2/E52G.REL (256 bytes, code=74
data=3)`), `cmp build/e52p2/E52G.REL golden/e52p1/E52G/E52G.REL` **rc=0**, sha256
`39b3d7cfe775c039d25b3791ed2f71b3e333509ca1193f3759ce46a850134c67` both sides.

## 4. Parity + registration (hop 2 ACTUALS)

* `tools/e2e_gate.py` SPECIMENS: `"E52G": ("probes/E52G.PLI",
  "golden/e52p1/E52G/E52G.REL")` added to the e52p1 block (`dca9219`).
* Sanctioned `python3 tools/e2e_gate.py --update-inventory` rc=0: INVENTORY
  **1195 → 1196** entries; `git diff spec/INVENTORY.txt` = **exactly ONE line**
  (`+E52G specimen probes/E52G.PLI golden/e52p1/E52G/E52G.REL`).
* COVERAGE row `PROC.DEC_FORMAL_COPYIN_CELLMAP` (`90582a5`): `rel_parity`
  `DIVERGENT:1 → EXACT:1`; `mine_status` `DIVERGENT → SUPPORTED` — the brief's
  wording "mine_status->EXACT" applied through the validator's vocabulary, where
  `EXACT` exists ONLY in `rel_parity` and `SUPPORTED` is defined as "compiles and
  every specimen is byte-exact" (P1 validator-vocabulary lesson honoured); `probes`
  now cites the registered panel key `E52G` AND keeps the golden path; the boundary
  sentence rewritten to measured reality (copy-in temp implemented via Bind
  `cs_copies`; refusals unchanged for unmeasured forms); cites unchanged
  `[C358] [C131] [C187]`; **NO new rows**.
* `python3 tools/coverage_check.py` **rc=0 DIRECT**: **139 rows, 0 errors, 0
  warnings**; stats re-snapshotted by its own write path (`mine.SUPPORTED` 85→86,
  `mine.DIVERGENT` 4→3).

## 5. Effects on E52A..J and E51A..L (hop 2, re-measured independently of the gate)

Positional recompiles with the registration binary `85bf7a26…` into
`build/e52p2/`, whole-file `cmp` vs goldens (rc captured per file):
* **E52A..E52J: 10/10 byte-exact** vs `golden/e52p1/` — the P1 controls and the
  five P1-fixed shadow rows UNCHANGED by the copy-in arm (its trigger fires only
  at a precision-mismatched DEC call site; none of those probes has one).
* **E51A..E51L: 12/12 byte-exact** vs `golden/e51p1/` — the E2E-51 division bank
  intact.

## 6. Gate actuals (byte tier only; every rc captured DIRECTLY, never via a pipe)

* PRE-registration FULL gate (hop 1, arm landed, E52G unregistered):
  `timeout 3600 python3 tools/e2e_gate.py` REAL **rc=0**, log
  `build/gate-e52p2-prereg.log` — `e2e gate: 1195 byte-exact / 0 fail of 1195`,
  negative 181/181, divergence 9/9, coverage 139 rows 0/0, census 15/0/26/0,
  prose 5.
* POST-registration FULL gate (hop 2, THIS tree):
  `timeout 3600 python3 tools/e2e_gate.py` REAL **rc=0** captured DIRECTLY to
  `build/gate-e52p2-reg.log` — `e2e gate: 1196 byte-exact / 0 fail of 1196`, with
  `BYTE-EXACT E52G: .REL == DR oracle (256 bytes)`; negative panel clean
  **181/181**; divergence **9/9**; coverage **139 rows, 0 errors, 0 warnings**;
  census **15/0/26/0** (REFUSED 26 UNCHANGED); prose **5 active files clean**.
* NO `spec/RUNTIME.txt` row and NO `OUTPUT_CHECK` entry comes from this round; the
  runtime behaviour of the copy-in pair is BYTE-TIER-observed structure only,
  UNRUN ([C358] scope).

## 7. LOAN2 rerun UNMODIFIED (step c)

`ocaml/_build/default/bin/pli80c.exe artefacts/LOAN2.PLI build/e52p2/LOAN2.REL`
(artefact UNMODIFIED; rc captured directly; stderr kept at
`build/e52p2/loan2-stderr.log`): **rc=2**, blocker verbatim:

> Fatal error: exception Failure("codegen: PUT FILE with a bare PAGE control item [TBD] (line 99) -- PAGE has DR's bytes (E46N10, 0023-0034, CALL ?PAGOP after the attach) but no specimen of MINE, and LINE is refused by DR itself (E46N21); SKIP is lowered")

MEASURED: the blocker is UNCHANGED from the P1 hop-4 record — the DEC copy-in was
NOT the next LOAN2 blocker. NOTHING was advanced or fixed; no `PAGE`/`PUT FILE`/
ON-unit/EDIT work was done (PLAN §6 non-goal). LOAN2 is never claimed exact.

## 8. NOT-say / remaining unsupported copy forms

* [C358] stays measured for THIS shape ONLY (DEC formal, DEC actual, literal
  store); it is NOT a general formal-layout law ([C187] remains the settled
  nested-layout claim).
* Everything outside the measured widening family remains a LOUD refusal BY NAME
  at codegen (`codegen: [TBD] FIXED DECIMAL(p,s) actual against FIXED
  DECIMAL(p',s') formal: DR's caller-side copy-in temp is measured ONLY for a
  caller-declared actual WIDENED at equal scale ... narrowing, differing scales,
  forwarded pointer-formals, outer-scope actuals and EXTERNAL entries are
  UNMEASURED`): narrowing (`pa > pf`), differing scale (`sa <> sf`), caller-FORMAL
  actuals (the E27B forwarding route — now refused where it previously passed
  silently by reference), outer-scope (non-own-row) actuals, deref/array-head
  actuals, recursive or `RECURSIVE` callees, EXTERNAL entries. Non-variable
  actuals against a DEC formal keep the pre-existing DECPOLY refusal.
* Equal-precision equal-scale DEC actuals still take the unchanged DECPOLY
  by-reference route (byte-exact on the panel today).
* Formal-vs-actual kinds outside DEC, arrays and pointer formals: UNMEASURED,
  untouched.
* No new claim: the ledger ENDS **C358**; no `spec/CLAIMS.md` byte was written this
  round (the "implementation-landed NOTE to C358" was permitted but not required;
  the default — no — was taken).
* Standing findings recorded, NEVER fixed here: the dashboard `**26**` stale check
  (pre-existing FAIL, standing PROPOSAL); whether the P1-era proposal "E52G joins
  `spec/DIVERGENT.txt`" is now OBSOLETE (G is byte-exact and registered — it does
  not join; the P1 proposal is superseded by registration, stated here as fact of
  this round, not as a new law).
