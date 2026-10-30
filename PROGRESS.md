# PROGRESS.md — DRPLi

Manual prose wins over the managed block below it. Do not hand-edit the managed block.
This file tracks *working state*; compiler behaviour itself belongs to `spec/CLAIMS.md`.

## Current phase

> **STATUS 2026-10-30 (session 01a18d44, renewal 3/8, checkpointed after arms (d)(e)).**
> **Arms (d) and (e) DONE, COMMITTED, MEASURED**: `18a06c0` store ladder |c| in {2,3} via the
> ONE `hl_bias` authority ([C324]); `1e8acb2` non-final BIT(1) PUT item accepted, guard removed,
> premise falsified by E48D9 kept verbatim ([C325]). Verified at HEAD: `dune clean && dune build`
> rc=0, warning multiset unchanged (126 = 28/26/22/17/15/14/2/2); **D1-D9 whole-file byte-identical
> to `golden/e48p2db/`** (D8 needed both arms -- the inherited "expect D8 after (d)" was jointly
> false, recorded in LEARNINGS); e48p1 24/24; e48c 9/9; full negative panel **181/181 refused,
> 0 anomalies** (gate CRLF+`^Z` semantics). Guard g30 committed as `547701d`.
> **NEXT = arm (f)** (D10 TEST member-as-RIGHT via `str_cmp_shape_rev ~imem:true` at the TEST
> callers codegen.ml:7557/7561; bytes `21 *D(member) / 11 *D(lit) / 06 len / CD ?SCCVM /
> C2 fill->next stmt`, [C326]; RE-MEASURE E46K14's refusal through the binary afterwards -- if its
> marker moved, FIX the arm, never silently re-pin), **then REGISTRATION + FULL GATE**:
> SPECIMENS.update E48D1..D10 (byte tier ONLY, no RUNTIME rows), `--update-inventory`, census
> `cp spec/census/corpus-census.json /tmp/census-prev.json && python3 tools/corpus_census.py
> --check /tmp/census-prev.json` (EXPR2/FSCAN expected to ADVANCE past the empty-initial refusal --
> re-read EVERY delta), FULL GATE (report ACTUAL; expect ~1119-1120 / 0 fail, negative 181),
> COVERAGE.tsv rows for COND/STOR/IO/DECL shapes + `coverage_check` + gate re-run. No half-edited
> state exists at this checkpoint; tree clean except guard blocks.

> **STATUS 2026-10-30 (session 01a18cf9, renewal 2/8, closing at context critical).**
> **E2E-48/P2d arms (a)(b)(c) DONE, COMMITTED, MEASURED.** `6545b5d` empty `initial('')` on STATIC
> VARYING (D4, [C322]); `6491981` TITLE-on-STATIC class-invariance (D1/D2, [C323]) + **E46F5
> promoted** by the three-place edit and verified whole-file byte-identical to
> `golden/e42p1c/E46F5/E46F5.REL` through this binary (my D1 differs from DR's E46F5 only in the
> 9 module-name bytes); `a72ce43` static FIXED store `?SMCCM` (D6, [C321]) — route identical to the
> automatic V106 head, no new encoder, **no prescan demand twin needed** (measured).
> Verified at HEAD: `dune build` rc=0 with the inherited warning multiset unchanged
> (22/15/28/2/14/2/17/26); **D1–D7 whole-file byte-identical to `golden/e48p2db/`**; e48p1 24/24;
> e48c 9/9; negative panel **181/181 refused, 0 anomalies** (gate CRLF+`^Z` semantics — my first
> hand replication used LF and produced 5 FALSE anomalies from line-number shifts in the marker
> texts); `registration_audit` clean at **1110 specimens / 181 rejects**. Tree clean; no
> half-finished edit.
> **NEXT = arms (d)(e)(f) one-per-commit, then registration + inventory + census + FULL GATE
> (measured) + COVERAGE rows — see HANDOFF.md "## Next action - E2E-48/P2d: LOWER the three
> remaining arms (d)(e)(f)" for the exact byte sequences, code sites and refusals to keep.**
> Claims C321–C326 are committed (`aa4b5b4`); the ledger needs no new claims for (a)-(c).

**E2E-48/P2d round 4: oracle MEASURED 10 ok/10, RESULTS written; arms (a)-(c) lowered; (d)-(f) +
registration + gate OWED.**
> **STATUS 2026-10-30 (session 01a18d08, renewal 1/8, step 5 in progress).** Measured THIS
> session at HEAD (guard g23 committed as `4e510d1`, build rc=0): baseline re-verified -- D3/D5/**D7**
> whole-file byte-identical to `golden/e48p2db/` (D7's `?SMCVM` store needs NO arm), the other 7
> probes carry their named refusals verbatim as in BASELINE-MINE-WRAPPED. All eight RESULTS §2
> laws re-read from the literal `.REL` bytes. **REJECTS audit done (dicts live in
> `tools/e2e_gate.py`): exactly ONE falsified row -- E46F5 (TITLE static-varying, promote after
> the arm); E46K14's `if line then` is a DIFFERENT shape, stays pinned, re-measure after the D10
> arm; no rows pin the other five refusals.** Order followed = P2c precedent: claims -> arms
> one-per-commit (a empty-varying initial(''), b TITLE static + E46F5 promotion, c static-FIXED
> store `?SMCCM` + prescan demand twin, d store ladder |c|2/3 DCX, e non-final bit item, f TEST
> member-as-RIGHT SCCVM) -> THEN SPECIMENS registration, `--update-inventory`, census `--check`,
> FULL GATE (expect 1109+10+1 = 1120 / 0 fail once all arms land; report ACTUAL), COVERAGE rows.
> OWED next: write claims C321-C326 into spec/CLAIMS.md + appends to C310/C313/C317, commit; then
> arm (a). Nothing half-edited; every refusal stays named until its arm lands.

**E2E-48/P2d round 4: oracle MEASURED 10 ok/10, RESULTS written; next = claims C321+, registration
+ full gate, then lowering.**

Measured this session (2026-10-30, chain 0/8, HEAD after these commits):

- Infra: `8b637cd` committed the operator's `handoff.config.json` threshold change (19000/
  11000/7000/5000 -> crossings 75k/83k/87k/89k on the 99k window); `142174c` guard g21 finalize
  (g20 was stale ONLY on source-config hash -- the other four source hashes unchanged).
- `67bf83c` **run 1 botched and kept**: tag `e48p2d`, 0 ok/10. Cause: each probe's purpose comment
  was one 179..317-col line; DR truncates past col 72 so `*/` was lost -> `UNEXPECTED EOF`, no
  `.REL`. No prediction scored.
- `60a2c06` amendment BEFORE run 2: `mkprobes.py` wraps comments <=71 cols; code lines proven
  byte-identical to 60cf463 by comment-stripped `cmp`; HYPOTHESES.md gained a dated amendment
  section (originals untouched); `BASELINE-MINE-WRAPPED.txt` = same 7 refusals / 3 compiles.
- `d28ff5e` **run 2**: tag `e48p2db`, **10 ok/10**, all `.REL` present, judged on bytes only.
- RESULTS.md (with this phase's commit) scores P-D1..P-D10: **HIT** P-D1,2,3,4,5,9,10 and P-D8;
  **P-D6 MISS on wording** (route is a new `?SMCCM` head, though ACCEPT+pool were right);
  **P-D7 MISS** (predicted a DATA-image length-byte rewrite that does not exist -- the image keeps
  the initial `02 41 42 20x8`; rewrite is runtime, [TBD]).

**8 laws now measured (RESULTS.md s2, ledger not yet written):** static FIXED store
`21 *D(cell) / 11 *D(pool) / 3E extent / 06 len / CD ?SMCCM`; static VARYING store `?SMCVM`
(same head, and D10 0006 shows the automatic varying member store uses `?SMCVM` too); empty
`initial('')` = varying `00`+extent blanks / FIXED all blanks, both IN PLACE, never pooled;
TITLE on a STATIC operand is class-invariant (D1 == E46F5 bytes modulo module name; D2 input
word `0E90`); store ladder for |c| in {2,3} = `2A / 2B x|c| / 7C / B5 / D6 01 / 9F / 32`
(same <=3 threshold as TEST, [C310] TBD closed; c=1 and negative c still unmeasured); non-final
BIT(1) PUT item ACCEPTED (`3A/06 01/?QB08C/?PNBOP` then the literal chain, one final `?QIOOP`);
DATA "slack" = automatic cells above the pool marked by `LINK-SET-LC` holes (E48A6's 0027
arithmetic confirmed); member-as-RIGHT TEST keeps the literal-left `?SCCVM` head, `LXI H` always
the internal cell.

**Still NOT measured (s3, [TBD], do not implement):** runtime length rewrite; `k = 1` / negative
c in the store ladder; BIT(1) item behind a file attach; BASED member in a condition store;
store/INITIAL longer than the extent. No `spec/RUNTIME.txt` row may come from this round.

**E2E-48/P2c CLOSED (renewal 8/8 successor, 2026-10-30): steps 6 AND 7 are DONE and MEASURED.**
Measured by THIS session, in order:
- HEAD at session start `2bae05e` + the guard's uncommitted g19 managed-block refresh, committed as
  its own commit `2d26c1b` (PROTOCOL Part 2 step 7). Tree clean.
- Baseline re-verified at HEAD: `dune build` rc=0 (needs `eval $(opam env)` — the renewal
  successor's shell does not carry the opam PATH; `dune: command introuvable` otherwise), E48C
  sweep **9/9** whole-file byte-identical, e48p1 **24/24**, and the two RETIRE goldens E46K1/E46K3
  byte-identical to `golden/e48p2retire/`.
- **A real leftover of the promotion was found and fixed:** the retired rows' `NEG_META` entries
  were still stamped by the loop at `tools/e2e_gate.py:3941`, so `registration_audit`'s
  REJECTS/NEG_META **symmetry** rule aborted the gate (`negmeta-only=['E46K1','E46K3']`) — a count
  cannot see it, only the audit can. Fixed by removing those two keys from the loop and keeping the
  superseded sentence verbatim in a comment above it (`f67cc6d`).
- **Step 6 item 2 DONE:** `python3 tools/e2e_gate.py --update-inventory` -> INVENTORY rewritten,
  **1291 rows = 1109 specimens + 182 refusals**, reviewed line by line: the only content changes are
  E46K1/E46K3 becoming specimen rows (goldens verified present), the nine new E48C rows, the
  E46F5 verdict text the 7/8 successor had rewritten in `e2e_gate.py` at `3ee414a` but never
  re-exported, and the shared E46K* prose.
- **Step 6 item 3 DONE — FULL GATE MEASURED twice, both rc=0:** `1109 byte-exact / 0 fail of 1109`,
  negative panel **182/182 refused**, divergence **9/9**, coverage **102 then 107 rows, 0 errors**,
  census `--verify` clean (EXACT 15 / DIFFERS 0 / REFUSED 26 / UNEXPECTED 0), prose check clean.
  The inherited "1107/184" is confirmed FALSE; 1109/182 is what the artifacts produce.
- **Step 7 DONE (`ef0a198`):** the five drafted `spec/COVERAGE.tsv` rows written —
  `COND.BIT1_NEG_TEST`, `STOR.BIT1_COND_STORE`, `COND.AND_BIT1_OPERAND`, `IO.PUT_BIT1_ITEM`,
  `DECL.STATIC_CHAR` — with the CURRENT ledger (C309-C320), not the round-1 draft text: the STOR row
  cites [C317]'s operand-CLASS law and lists E48C1..C8 + E46K1 (18 exact), `DECL.STATIC_CHAR` is
  `PARTIAL` and cites [C314][C319][C320] with the empty-literal / store-into-static / TITLE
  refusals named. Also corrected, each as a PURE APPEND with the original kept word-for-word:
  FILE.PUT_LIST_VAR's CREATE and LOAN2 blocker sentences (LOAN2 now refuses in the prescan, CREATE
  at `GET LIST of unknown variable name`), STOR.STATIC_MEMBER_INITIAL's and DECL.STATIC_INHERIT's
  census blocker names, and DECL.STATIC_INITIAL's falsified `STATIC on character types has no sample
  at all` clause. `coverage_check` 107 rows / 0 errors, gate re-run at that HEAD still 1109/0.

**OPEN AT THIS BOUNDARY: no half-finished COMPILER edit; every commit above was made after its
measurement.**

**Round 4 (E2E-48/P2d) PRE-REGISTERED, oracle NOT RUN** (this session stopped at the
pre-registration boundary on context pressure). Written and committed:
`spec/lab-evidence/e2e48-p2d/mkprobes.py`, ten CRLF probes `probes/E48D1..D10.PLI`,
`BASELINE-MINE.txt` (measured at `ef0a198`: D1/D2/D4/D6/D8/D9/D10 refuse with their named texts;
**D3 static-FIXED title, D5 empty FIXED initial and D7 store into a static VARYING cell already
COMPILE** -- my bytes for those three are unverified against any DR object), and `HYPOTHESES.md`
P-D1..P-D10 derived only from committed goldens (`golden/e42p1c/E46F1/F2/F3/F5`,
`golden/first8080u/EXPR2`, `golden/e48p2c/E48C8`; P-D6/P-D7 pool arithmetic flagged as the weakest
derivations). Two §3 "unmeasured" claims were **FALSIFIED by artifacts already in the tree** during
this work -- DR's accepted object for `TITLE(<static varying>)` is `golden/e42p1c/E46F5/E46F5.REL`,
and the EMPTY-literal static-varying cell is `golden/first8080u/EXPR2/EXPR2.REL` DATA 000F = `00` +
ten `20` (recorded in `LEARNINGS.md`). The `spec/CLAIMS.md` [C319]/RESULTS §3 annotations and the
COVERAGE boundary sentences stay OWED -- they must be corrected with the round's OWN measurements,
not pre-emptively from a prediction.
**No oracle call was made in this session on any E48D probe; `golden/e48p2d` does not exist.**

(Inherited boundary text, kept for lineage:)
**E2E-48/P2c STEP 6 OWED (renewal 7/8 successor, 2026-10-30); arms 4a/4b/2 + RETIRE round + claims DONE.**
Measured by THIS session, in order:
- Re-verified inherited baseline at `c4d6a80`: dune rc=0; E48C sweep 6/9; e48p1 24/24.
- **Step 4a** at `14c7321`: `store_char` admits the UNQUALIFIED destination of an automatic
  VARYING member with a literal source (licensed by golden/e48p2c/E48C3 -- re-verified myself:
  `cmp -l` shows ONLY bytes 6/19/28, the module-name bytes); FIXED-member refusal verbatim;
  dead `imem_qualified` helper removed. Sweep 8/9, e48p1 24/24, warning multiset unchanged.
- **Steps 4b+2** at `3ee414a`: `Bind.RTchar (n, true)` placement arm -- static varying cell =
  [len][literal padded to extent with 0x20] IN PLACE, NOT pooled; `initial('')`/no-INITIAL/
  over-extent/non-literal stay named refusions (§3). E46F5's declaration now lowers and the
  program advances to `OPEN TITLE(nm)`, which refuses BY NAME (static-varying TITLE unmeasured,
  §3); its REJECTS marker + NEG_META reason were RE-MEASURED through the binary, original record
  kept as superseded. WHY-strings of `imem_refuse` and lower_open's k-arm updated to cite
  golden/e48p2c. Sweep **9/9 E48C whole-file byte-identical** and 24/24 e48p1; full 184-row
  REJECTS replication (gate loop semantics) shows EXACTLY two newly-admitted rows: **E46K1**
  (bare member literal store -- licensed by §1 P3/§2.1) and **E46K3** (TEST member compare,
  bare spelling -- licensed by §2.4 + P3; the 7701f52 arms had already admitted it unnoticed,
  since the negative panel had not been run since `1595a10`).
- **RETIRE round DONE**: pre-registered at `630e9be` (predictions derived from golden bytes,
  committed BEFORE any oracle call), oracle `--tag e48p2retire` measured **2 ok / 2** and both
  whole files **byte-identical** to my objects (P-K1/P-K3/P-G1 all HIT, RETIRE-RESULTS.md).
  E46K1/E46K3 retired from REJECTS (now **182 rows**) and promoted with E48C1..C9 into
  SPECIMENS (now **1109**, all paths verified present); claims **C317-C320** + C310
  load-order annotation written. All committed at `1480d6f`; sweeps at that HEAD: E48C 9/9,
  e48p1 24/24, 181-row negative replication clean + E46F5's new marker measured against the
  binary; dune rc=0, warning multiset unchanged.

**EXACT NEXT ACTION = step 6 (census DONE; inventory + FULL GATE owed), then step 7.**
Census MEASURED at `b78770d` HEAD (snapshot committed `014a736`): counts **IDENTICAL**
(15 EXACT / 0 DIFFERS / 26 REFUSED / 0 UNEXPECTED); three msg deltas ALL verified --
EXPR2/FSCAN moved to the specific EMPTY-`initial('')` refusal (correct named stop),
LOAN2 ADVANCED past line 39 to a NEW my-gap blocker (`variable i declared with
conflicting kinds` in the prescan type map -- for a FUTURE pre-registered round, NOT
lowered on faith); REPORT/MPMCALLB unchanged. REMAINING: (2) `python3 tools/e2e_gate.py
--update-inventory`; (3) FULL GATE expecting **1109 / 0 fail, negative 182/182**
(inherited 1107/184 SUPERSEDED by the K1/K3 promotions; report measured numbers only);
(4) step 7 COVERAGE rows + fix/mark-stale the LOAN2 sentence in row FILE.PUT_LIST_VAR
(it says LOAN2 refuses at line 39 -- census now says otherwise) and add a census line
for the new `conflicting kinds` blocker if prose demands it.

**Unmeasured at THIS boundary (do NOT claim): `--update-inventory` and the FULL gate
have NOT been run since the arms landed.** No half-finished edit exists: HEAD is
committed and the tree clean except guard-owned blocks.

(Previous boundary text, superseded above for work state but kept for lineage:)
Of the licensed lowering steps, **1(a)(b)(c) and 3 are DONE** at `7701f52`:
`str_side`'s new `Imem variant (an internal level-numbered CHARACTER VARYING member, BOTH
spellings), the 18-byte member SCVCM head in `str_cmp_shape` (`LXI H,*D(member) / EB /
LXI H,*S(lit) / MVI A,len / ?SCVCM`), the 17-byte literal-left SCCVM arms in
`str_cmp_shape_rev` gated by a new `?imem` parameter that ONLY `bit_cond_mat` passes true — so
the TEST route still refuses member-as-RIGHT exactly as RESULTS §3 demands — the two
`bit_cond_mat` orientation arms sharing the [C095] `D6 01 / 9F / STA` tail, and BOTH demand
twins (`bit_store_cond_bytes` rewritten as one class predicate over {flat Vvar, varying Vimem};
`prescan_cond`'s `is_var` + qualified-spelling lookup). Measured at `7701f52` by THIS session:
`dune build` rc=0, no new warnings; sweep **6/9 E48C whole-file byte-identical** (C1,C2,C5,C6,
C7,C9 — arm 3 arrives free through the shared encoder) and **24/24 `golden/e48p1/` intact**.
Remaining: **E48C3/E48C4** stop at `store_char`'s qualified-DESTINATION gate (licensed to widen
by golden/e48p2c/E48C3 — RESULTS §1 P3; `cmp -l` of the C2/C3 goldens shows ONLY the three
module-name bytes 6/19/28 differ); **E48C8** stops at the STATIC-on-CHARACTER-VARYING
placement (step 4, with E46F5's negative-row consequence). NOT re-run and therefore NOT
claimed: the full gate (1098/0 is recorded at `1595a10` alone) and the census since `7701f52`;
step 2's refusal WHY-string updates are unwritten. Exact next action: `HANDOFF.md` → the STATUS
block of `## Next action - E2E-48/P2c implementation`, sub-step **4a**.

(Original round-3 findings, superseded above for work state: the SCVCM
load-order discriminator that [C310] left [TBD] is ANSWERED by the oracle: the operand CLASS
decides (internal VARYING member -> 18-byte `LXI H,*D(member)/XCHG/LXI H,*S(lit)` — E48C2/C3/C4/C7
+ CREATE 008F; flat cell, auto or static -> 17-byte `LXI H,*S/LXI D,*D` — E48A6/E48C1/E48C8);
qualification and loop position do NOT matter. Also measured: the SCCVM store route (literal left,
17 bytes, length in B, member needs no XCHG — E48C5/C6), the first STATIC-on-CHARACTER-VARYING
layout law (cell = 1-length byte + declared extent blank-padded IN PLACE below the pool, initial
NOT pooled — E48C8), the internal-member compare in TEST position (15-byte head + C2 skip-to-next
— E48C9), and DR's storage-class law that a flat level-0 STATIC does NOT contaminate a later
`dcl 1 rec` (record is AUTOMATIC — E48C7).

Commits this session: `f9f21f2` pre-registration (bank + HYPOTHESES + BASELINE-MINE, oracle NOT
yet run), `8c57856` goldens `golden/e48p2c/` (9 ok/9) + `spec/lab-evidence/e2e48-p2c/RESULTS.md`
(prediction vs verdict: 7 clean HITs; P5/P6 sequences HIT but my size LABEL said 16, actual 17 —
arithmetic slip, kept as written per PROTOCOL #2), `6130164` my-gap fix of the level-0
storage-class leak in `dcl_static_dcls` + census re-measured (counts IDENTICAL; ONE msg delta =
MPMCALLB ADVANCED from `STATIC on POINTER MEMBER OF CPB@390` — the leak — to its next genuine
`STATIC on FIXED BINARY(15,0) MEMBER OF STRINGQCB@82` blocker).

Verified at `6130164`: dune rc=0; 24/24 e48p1 probes still whole-file byte-identical; E48C1
byte-identical to its new golden; D2/D3 scratch (static-first record) compile. NOT yet re-run:
the full gate (the pre-fix run aborted at census `--verify`, which the snapshot update now
closes — the gate must be re-run and is expected to measure 1098/0).

**Pending (this round):** the codegen arms RESULTS §2 licenses — `bit_cond_mat` member(SCVCM)/
reverse(SCCVM) arms with their `bit_store_cond_bytes` prescan twins, the internal-member
store/compare gate widenings (they must admit ONLY the measured shapes: based-member stores stay
refused), the static-VARYING placement arm (careful: E46F5's pinned refusal text must survive via
a named refusal at its `OPEN ... TITLE(nm)` step or its gate row re-measured explicitly), the
TEST-position internal-member arm, then panel registration (SPECIMENS/INVENTORY 1098 -> 1107),
claims C317+, census re-measure, gate.

(Previous phase, closed: **E2E-48/P1: all 24 probes of `golden/e48p1/` byte-identical and
registered. Gate measured 1098 byte-exact / 0 fail, negative 184/184, divergence 9/9, coverage
102 rows 0 errors, census `--verify` clean.**)

Commits this session (each verified by measurement, in order): `f839f52` census re-measured after
`371a12e` (the drift was CREATE advancing, not regressing) · `fa09b97` prescan demand
`bit_store_cond_bytes` (E48A12 exact; the store arm had allocated a pool cell the prescan never
demanded) · `df4b9c8` step 4, the BIT(1) PUT item `LDA / MVI B,01 / ?QB08C / ?PNBOP` with its own
tail replacing `?PNCOP` (23/24) · `613385b` step 5, STATIC-on-CHARACTER (full-extent blank-padded
cell, 0 pool bytes, read at the declared length) + census re-measured (24/24) · `992ccad` panel
registration (+24 SPECIMENS, INVENTORY 1098 via `--update-inventory`) and claims **C309-C316**.

**Pending (recorded, not started):** (a) `spec/COVERAGE.tsv` rows citing C309-C314 and the E48*
probes — `coverage_check` passes without them, so this is a documentation gap, not a red row;
(b) the `[TBD]` list inside C310/C313/C314, which needs a NEW pre-registered round (E48C) — the
CREATE-vs-E48 SCVCM load-order discriminator (18 vs 17 bytes) is the one that blocks a corpus
program; (c) CREATE is still NOT byte-exact and its measured blocker is now front-end:
`pli80c.ml` never expands `%include`, so `get list (name)` (declared in RECORD.DCL) refuses with an
unbound name. Do not implement any of these before the oracle has measured them.

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

- **DONE this session (kept for lineage):** the RETIRE round oracle (`630e9be` prereg -> 2 ok/2 ->
  promoted at `1480d6f`), step 6 registration (`--update-inventory` + FULL GATE measured at
  `f67cc6d`), and step 7's five COVERAGE rows (`ef0a198`).
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
- **Renewal budget is EXHAUSTED (8/8, `maxRenewals: 8`).** `handoff_renew` will refuse with
  `capped`; the operator must either raise the cap by decision or start the successor session
  manually. Nothing about the science changes; the durable files are the recovery path either way.

<!-- guard:begin checkpoint -->
checkpoint-schema: 3
checkpoint-generation: 32
checkpoint-id: g32-eba3b5c605f1
checkpoint-kind: auto
content-delta: none
readiness: unattested
guard-level: 3
checkpointed: 2026-10-30T14:56:40.721Z
source-goal: 730790b648a1e1d14b76243cfe8bc17eea2ba9cd8527f204f9c8d4dbcc527c9d
source-progress: b2d794929d803bfb73916cb5c7d38b0ce78142037649377049fb20f6aaa99ca6
source-handoff: d5fd211bd8496497ed37a5057394f9764b2b6c6e3a3bd5e569eab0fee82318bd
source-learnings: b188c7fb525792a1b7458fee01eaea584ccc29cb50b9e895313b682128d0d3e6
source-config: a16817433633f508b54b8283f85b9a6e9ccbf6e9e467d894145b0d5fc921889d
next-action: (superseded by the section below: its steps 1-4 are DONE — run 1 botched (e48p2d, kept), wrap amendment 60a2c06, run 2 = 10 ok/10 at golden/e48p2db committed d28ff5e, RESULTS.md written)
<!-- guard:end checkpoint -->

## Verified evidence

Measured by the E2E-48/P2c session (2026-10-30), not quoted from a report:

- Oracle `PLI_SRC=probes python3 oracle/batch.py E48C1..E48C9 --tag e48p2c --switches '$L$D'`
  -> **9 ok / 9**, all `.REL` produced; pre-registration committed at `f9f21f2` BEFORE the run;
  goldens committed at `8c57856` with RESULTS.md (prediction-vs-verdict: 7 clean HITs; P5/P6
  sequence HIT with a 16-vs-17 size-label slip kept as written per PROTOCOL #2).
- Laws read from the `.REL` records via chaindump/reldump: member store 18 bytes (E48C2/C3/C4/C7
  + CREATE 008F); flat 17 (C1, A6, C8); SCCVM store 17 with `06 len`, no XCHG member-side (C5/C6);
  C7 DATA `41 42 20 | 00 | pool 4..C | rec AUTO @000D`, DEF-DATA-SIZE 44; C8 `nm` cell 15 bytes
  `02 41 42 20 x12`, DEF-DATA-SIZE 21; C9 head + `C2` skip to next statement 0027.
- Leak fix `6130164`: D2/D3 scratch compile; 24/24 `golden/e48p1/` still whole-file
  byte-identical; E48C1 whole-file byte-identical; census re-measured via
  `tools/corpus_census.py --check <copy of prev>`: counts IDENTICAL (EXACT 15 / DIFFERS 0 /
  REFUSED 26 / UNEXPECTED 0), ONE msg delta = MPMCALLB ADVANCED past the leak blocker to
  `STATIC on FIXED BINARY(15,0) MEMBER OF STRINGQCB@82`.
- Gate at baseline `1595a10` (before any edit this session): **1098 byte-exact / 0 fail**,
  negative 184/184, divergence 9/9, coverage 102/0, census clean, rc=0. NOT yet re-run at
  `6130164` - the first run aborted on the then-stale census snapshot, which the re-measure
  above closed; a fresh full gate run is part of the pending registration step.

## Blockers

- None scientific is open at this boundary, and nothing is half-edited; every commit above was
  made only after its measurement.
- The full gate must be RE-RUN at the P2c HEAD before this round can be called registered (the
  1098/0 figure above is recorded from `1595a10`).
- What limits further parity is **missing evidence**, never a licence to guess: RESULTS section 3
  lists what P2c did NOT measure (based-member condition STORES, member-as-RIGHT in TEST
  position, `^(cond)` stores, `k = c` with |c| in 1..3, `'0'b` as a value, nested `&`, non-final
  bit PUT items, stores INTO static cells, `TITLE(<static varying>)`) - every one stays a named
  refusal.
- CREATE's measured blocker is front-end: `pli80c.ml` does no `%include` expansion, so
  `get list (name)` (from `artefacts/RECORD.DCL`) refuses on an unbound name. Proposed, unverified.
