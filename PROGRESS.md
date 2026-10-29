# PROGRESS.md — DRPLi

Manual prose wins over the managed block below it. Do not hand-edit the managed block.
This file tracks *working state*; compiler behaviour itself belongs to `spec/CLAIMS.md`.

## Current phase

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
checkpoint-generation: 19
checkpoint-id: g19-a1cadcc56d16
checkpoint-kind: manual
content-delta: new
readiness: attested
guard-level: 4
checkpointed: 2026-10-29T22:20:03.288Z
source-goal: 730790b648a1e1d14b76243cfe8bc17eea2ba9cd8527f204f9c8d4dbcc527c9d
source-progress: c994ff4745d9c8a042f283cdd40662850e028b1e1d964c6109b8e336847d7fba
source-handoff: a39efb8344f2f7f0e31201dde46a18027883e4984572581e278481d385ccd1ac
source-learnings: ff8f82d25240122069672f7e7b66446ebf3f788d12a4edb5b686afb78e9363e4
source-config: 8e66b82b71db399633cd776d6a5329e70c0eb09173121cfb303569d5f6ba6bf3
next-action: - E2E-48/P2c step 6: census re-measure, inventory, FULL GATE

> STATUS 2026-10-30 (renewal 7/8 successor, HEAD after the RETIRE+claims commit):
> **Steps 1-5 DONE, RETIRE round DONE.** `14c7321` (4a store-destination widening, 8/9),
> `3ee414a` (4b static-varying placement + TITLE-on-static named refusal + step-2 WHY-strings,
> 9/9; E46F5 row RE-MEASURED through the binary), `630e9be` (RETIRE prereg BEFORE the oracle),
> `1480d6f` (oracle measured 2 ok/2, E46K1/E46K3 whole-file byte-identical and PROMOTED;
> SPECIMENS.update adds E48C1..C9 + K1/K3 = **1109 specimens**; REJECTS = **182 rows**;
> claims **C317-C320** + C310 annotation written). Sweeps at HEAD: E48C 9/9, e48p1 24/24,
> 181-row negative replication clean (E46F5's NEW marker verified separately against the
> binary). `dune build` rc=0 with the inherited warning multiset unchanged (126 =
> 22/15/28/2/14/2/17/26).
>
> > NOTE (7/8 successor): step-6 item 1 (census --check) is DONE (counts IDENTICAL
> 15/0/26/0, snapshot `014a736`); LOAN2 advanced to a NEW prescan my-gap
> `variable i declared with conflicting kinds` (future round, recorded not lowered).
> Items 2 (--update-inventory) and 3 (FULL GATE, expect **1109/0, negative 182/182** --
> the 1107/184 in the older text is superseded by the K1/K3 promotions) are OWED.
**THE EXACT NEXT ACTION is step 6, then step 7:**
> 1. Census: `cp spec/census/corpus-census.json /tmp/census-prev.json && python3
>    tools/corpus_census.py --check /tmp/census-prev.json` — counts MUST stay IDENTICAL
>    (EXACT 15 / DIFFERS 0 / REFUSED 26 / UNEXPECTED 0); EXPR2/FSCAN (now the EMPTY
>    `initial('')` refusal), LOAN2 (advances past line 39 to its next genuine blocker),
>    REPORT/MPMCALLB deltas are EXPECTED — read and verify EVERY msg delta in the tsv diff
>    before committing the snapshot (+ spec/COVERAGE.tsv prose defer blocker names to the
>    census; the LOAN2 sentence in row FILE.PUT_LIST_VAR now LAGS — correct or mark stale).
> 2. `python3 tools/e2e_gate.py --update-inventory` (rewrites INVENTORY rows incl. K1/K3
>    becoming byte-exact entries; 1098-entry figure was recorded at `1595a10` only).
> 3. FULL GATE: `python3 tools/e2e_gate.py` — expect **1109 byte-exact / 0 fail**, negative
>    **182/182**, divergence 9/9, coverage 102 rows 0 errors, census --verify clean, rc=0.
>    The checkpoint's "1107/184" figure is SUPERSEDED by this session's K1/K3 discovery.
>    Report measured numbers only.
> 4. Step 7 (lower priority): the five DRAFTED spec/COVERAGE.tsv rows (15 columns; validator
>    rule coverage_check:213; `manual_ref = NONE:<why>`; MEASURED rows must cite probes named
>    by their OWN claims) -> `python3 tools/coverage_check.py`.
>
> Do NOT touch golden/e48p1, golden/e48p2c or golden/e48p2retire. Do NOT implement RESULTS §3
> shapes; member-as-RIGHT in TEST and based-member condition stores stay refused. Do NOT start
> `%include` without its own pre-registered round. Renewal 8/8 would be the LAST under the cap.

(Original step list below, complete for steps 1-5; kept for lineage.)

The round-3 battery is PRE-REGISTERED (`f9f21f2`), MEASURED 9 ok/9 and committed with
`spec/lab-evidence/e2e48-p2c/RESULTS.md` (`8c57856`); the level-0 STATIC-chain my-gap fix is
committed (`6130164`) with the census re-measured (counts IDENTICAL; MPMCALLB advanced one
blocker). E48C1 is already whole-file byte-identical and 24/24 e48p1 probes are intact.
THE PREVIOUS NEXT-ACTION SECTION ("E2E-48 round 2 ... Pick ONE") IS SUPERSEDED by this one;
its item 2 (the five drafted COVERAGE rows) survives as sub-task 7 below.

Implement ONLY what RESULTS section 2 measures; every RESULTS section 3 shape stays a named refusal:

1. `bit_cond_mat` (ocaml/lib/codegen.ml:7005) - add exactly these arms, ONE AT A TIME,
   `dune build` + `cmp` sweep after EACH (LEARNINGS rule):
   (a) (internal varying MEMBER left, literal right) - both spellings, AUTOMATIC records only:
       `LXI H,*D(member) / EB / LXI H,*S(lit) / MVI A,len / CALL ?SCVCM / D6 01 / 9F` (18 bytes
       incl. the `32` STA the Vbit1 arm adds) - sites E48C2 0013, C3 0013, C4 0027, C7 0013;
   (b) (literal left, flat Vvar cell right - auto OR static): `LXI H,*D(var) / LXI D,*S(lit) /
       MVI B,len / CALL ?SCCVM / D6 01 / 9F` (17 bytes) - E48C5 0013, E48C8's SCVCM site stays
       the flat LEFT form;
   (c) (literal left, internal varying member right): same, member cell in HL, NO XCHG - E48C6.
   A BASED member as either side of a condition STORE stays refused (unmeasured).
   Mirror EVERY new pool-cell-allocating shape in `bit_store_cond_bytes` (codegen.ml:2996) -
   prescan demand is ONE rule with lowering (C152/C179; the fa09b97 lesson: an arm without a
   demand twin dies on the pool invariant).
2. Widen the internal-member gate ONLY for the admitted shapes: the store-path `imem_in_e st rhs`
   refusal at codegen.ml:8555 and the TEST-path comparison refusal at 7632 must consult the SAME
   predicates as `bit_cond_mat` (one authority, never a second copy of the byte decision); every
   other member use keeps `imem_refuse` verbatim. Update the refusal WHY-strings to cite
   golden/e48p2c where the bank now measures a shape - corrections stay traceable, never silent.
3. TEST position (E48C9): the 15-byte head `LXI H,*D(member) / EB / LXI H,*S / MVI A,len /
   CALL ?SCVCM / C2 00 00` with the no-else skip to the NEXT STATEMENT (C309 rule); member-as-
   RIGHT in TEST is UNMEASURED - keep refusing it.
4. STATIC-on-CHARACTER-VARYING placement (RESULTS section 2.5, arm at codegen.ml:12861 region,
   `Bind.RTchar (n, true)`): accept ONLY a non-empty string-literal INITIAL not longer than the
   extent; cell = [len-byte][literal padded to n with 0x20] IN PLACE in the static zone, NOT
   pooled; `initial('')` is unmeasured (EXPR2's spelling) - keep refusing it. CAUTION: E46F5's
   declaration then passes and the program advances to `OPEN ... TITLE(nm)` - TITLE on a STATIC
   varying is UNMEASURED, so E46F5 must refuse THERE; its negative-panel row pins the CURRENT
   text and must be re-measured and updated through the tool's write path with an explicit
   reason, never by hand-editing a verdict.
5. Sweep after each arm: `for n in E48C{1..9}; do ./ocaml/_build/default/bin/pli80c.exe
   probes/$n.PLI /tmp/sw/$n.REL && cmp /tmp/sw/$n.REL golden/e48p2c/$n/$n.REL; done` plus the
   24-probe e48p1 loop - expect 9/9 and 24/24 byte-identical at the end.
6. Registration: SPECIMENS.tsv byte-tier rows E48C1..C9 (NO spec/RUNTIME.txt rows - this bank
   captured .REL/.PRN only), `python3 tools/e2e_gate.py --update-inventory` (INVENTORY 1098 ->
   1107), claims C317..C320 in spec/CLAIMS.md (the six laws of RESULTS section 2) plus an
   ANNOTATION on C310 marking its load-order [TBD] answered (keep the old text), census
   re-measure via `tools/corpus_census.py --check <copy of prev>` (counts must stay IDENTICAL;
   EXPR2/FSCAN/LOAN2/REPORT/MPMCALLB msg deltas are expected to ADVANCE - verify each message),
   then `python3 tools/e2e_gate.py` -> expect **1107 byte-exact / 0 fail**, negative 184/184
   (E46F5 row re-measured per step 4), divergence 9/9.
7. Sub-task (carried over, lower priority): the five DRAFTED spec/COVERAGE.tsv rows in the
   previous checkpoint's item 2 (format facts already MEASURED there: 15 columns, validator rule
   at coverage_check:213, `manual_ref = NONE:<why>`); validate with `python3 tools/coverage_check.py`.

Do NOT touch golden/e48p1 or golden/e48p2c. Do NOT start `%include` (CREATE's front-end blocker)
without its own pre-registered round.

**Unmeasured at the `7701f52` boundary (do NOT claim them):** the full gate has not been run
since `1595a10` (1098/0 is that HEAD's recorded figure, not the current one); the census has not
been re-measured since `7701f52`; the refusal WHY-strings of step 2 are NOT yet updated.
**No half-finished edit exists** — `7701f52` is built, swept and committed; the tree is clean.
readiness-by: session:01a1899c-bfe2-7470-93c0-80efada31a9a
readiness-at: 2026-10-29T22:20:03.291Z
readiness-checkpoint: g19-a1cadcc56d16
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
