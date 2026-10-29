# HANDOFF.md — DRPLi

Manual prose wins over the managed block below it. Do not hand-edit the managed block.

## Recovery instructions

1. Confirm the repository and revision:
   `cd /home/john/projects/sushiworks/pli80 && git rev-parse --abbrev-ref HEAD && git rev-parse HEAD && git status --porcelain=v1 | wc -l`
   Expect branch `main` and an empty porcelain output; a dirty tree is investigated, never
   cleaned (`AGENTS.md` → Protected).
2. Read `AGENTS.md`, `PROTOCOL.md`, `GOAL.md`, then this file's `## Last verified state`, then
   `PROGRESS.md` and `LEARNINGS.md`.
3. Check checkpoint freshness with `/handoff verify` (extension auto-loaded — the project is
   trusted; see `PROTOCOL.md` → Load). `stale` or `missing` means: re-derive state from commits and lab evidence,
   then refresh with `/handoff`. Do not trust this file's managed block over its prose.
4. Load the authoritative evidence for whatever you are about to do:
   `spec/CLAIMS.md` (claims ledger, C001…C308 at the time of writing),
   `spec/INVENTORY.txt`, `spec/COVERAGE.tsv`, `spec/RUNTIME.txt`, `spec/DIVERGENT.txt`,
   and the newest `spec/lab-evidence/e2e42-p2c/` reports.
5. Do **not** run the compiler, the oracle, LINK-80, cpmsim, Rune CI or `tools/e2e_gate.py`
   unless the session's actual task is compiler development or gate verification.

## Last verified state — E2E-48/P1 (scientific session, measured 2026-10-29)

See `PROGRESS.md` → Current phase for the same content; the short form: round 1 (E48A1..A15)
pre-registered at `284b630`, measured 15 ok/15; round 2 (E48B1..B9) pre-registered at
`3401821`, measured 9 ok/9; goldens in `golden/e48p1/` (uncommitted). DR laws measured this
phase, all read out of the `.REL` records:

- `^b` test on BIT(1): `3A <cell> / B7 / FA + 2-byte operand filler (00 00, filled later by
  SET-LC/RELOC)` = **7 bytes** (the earlier "8 bytes / 5-byte chain" wording was a miscount;
  RESULTS.md §5 supersedes it). CREATE 0052, E48A1 000C, E48A5 0011, E48A12 000C, E48B1,
  E48B7; positive form identical with `F2` (E48A3 0006, E48B2, FLTPOLY2 0075). `DO WHILE`
  exit = address just after the loop-tail `C3 <test>` (tail+3; E48A1 fill 0011→0044);
  IF/ELSE false-chain targets the else (E48A2 000B→0027); no-else IF skip → next statement
  (E48B1 inner 001F→0028).
- `b = (cond)`: materialiser, then `D6 01 / 9F` (`SUI 01/SBB A`: 0→FF, nonzero→00), then
  `32 <cell>`. E48A6 (auto varying = literal) measured **17 bytes** `LXI H,*S(lit) / LXI D,var
  / MVI A,litlen / CALL ?SCVCM / D6 01 / 9F / 32 b`. CREATE's own store at 008F is **18 bytes**
  `LXI H,var / EB(XCHG) / LXI H,*S(lit) / 3E 03 / ?SCVCM / D6 01 / 9F / 32` — same registers,
  different load order; the **discriminator is [TBD]** (only one SCVCM site exists in CREATE;
  all 18 E48 sites use the LXI-D form). The earlier "16 bytes, 2A/LHLD" reading was wrong
  (RESULTS.md §5).
- Materialiser by class (RESULTS.md §3.2): `k = 0` → `LXI H,k / MOV A,M / INX H / ORA M`;
  `k = c` |c| ≥ 4 → `LHLD k / LXI B,two's-comp / DAD B(0x09) / MOV A,H / ORA L` — **no DR
  defect: byte 0x09 is standard DAD B and my `hl_bias` already matches** ([C143] compare-route
  threshold ≤3 confirmed by E48A13 `= 3` = DCX H ×3 vs E48A12 `= 4` = LXI B,FFFC); `k ^= 0`
  AND `^(k = 0)` (value) → same `=0` ladder with `ADI FF / SBB A` (C6 FF/9F) — never CMA;
  `k > 0` → `LXI H,k / XOR A / CMP M / INX H / SBB M` (result already 00/FF, no tail);
  `f = (b = '1'b)` → `LDA / ANI 80 / SUI 80 / D6 01 / 9F / 32`.
- `^(cond)` in a test **inverts the skip byte** (`C2 JNZ → CA JZ`, emitted as `CA 00 00` +
  SET-LC/RELOC fill, E48A13); `if k = 0 & b then` materialises the left into A, then
  `PUSH PSW / LDA b / POP B / ANA B` under one `F2` (E48A14 000C-001D).
- `put list(b)` is **accepted**: `LDA cell / MVI B,01 / CALL ?QB08C / CALL ?PNBOP` (7 objects).
- STATIC bits are DATA-absolute and adjacent (E48B5 0000/0001); `dcl s char(3) static
  initial('AB')` is accepted, cell `41 42 20`, and the PUT reuses that cell — DATA area 3, zero
  pool bytes (E48B6). I refuse both today.
- **My DATA-size double-count — FIXED and committed.** `bind.ml` `section2`'s `span` charged
  STATIC rows; a8d1c3a excludes them (`static_rows` from `bind_rows`' 4-tuple auto flag). E48A3
  (DR 3) and E48A4 (DR 8) are now byte-identical whole-file to the goldens; the gate stayed
  **1074 byte-exact / 0 fail**, census unchanged (15 EXACT). `codegen.ml:12340` needed no change.

## Last verified state (Pi Handoff deployment window — superseded above for work state)

Verified **in the deployment session itself** (i.e. measured now, not quoted from a report):

- Repo `/home/john/projects/sushiworks/pli80`, branch `main`; scientific HEAD
  `0a50fc4c745838e3af1641c8a6f68fd17ed1371a`, with the 2026-10-29 infrastructure chain on top
  (`aa03eeb` renewal activation, `88248b1` renewal e2e test record, plus the closure commits);
  working tree clean (0 porcelain lines) at every checkpoint of this window.
- 12 028 tracked files; 471 102 ignored files present; 37 entries at the repository root.
- Nested third-party repos untouched and clean: `thirdparty/PLI-2000` @
  `c6f0f2ddd9c2100781ce6fb65d79d3039ac94e2a`, `thirdparty/z80pack` @
  `91fd28eb04e675c2127df88ed3f40675e15282e2`.
- `/tmp/wt_base` worktree and `.git/worktrees/` metadata left exactly as found; no branch
  switched; no `clean`/`reset`/destructive checkout run.
- Pi 1.4.0 at `/usr/bin/pi` under the production profile `/home/john/.sushi/pi`;
  `.sushibeta/pi` not used.
- Pi Handoff `v0.1.0-dev.1` (`2ea6219`) is installed and **validated in the real runtime**:
  the extension loads, `/guard status` reports model `sushi/Qwen3.8-Flash-Next-Sushi-STQ-2.75bpw`,
  window 220 000, maxOutput 65 536, reserve 20 000; read-only mode wrote nothing; a controlled
  writable session produced schema-v3 checkpoint blocks in both files, `current` freshness and a
  `READY` attestation, and a level-3 automatic checkpoint preserved substantive notes verbatim.
  Manual prose outside the managed blocks was byte-identical before and after every guard write;
  `GOAL.md`/`LEARNINGS.md` were never written by the guard; all runtime files stayed inside the
  ignored `.pi-guard/`.

Verified **from committed reports, NOT re-run in this session** (treat as recorded results,
not as fresh measurements):

- Latest recorded gate verdict (`spec/lab-evidence/e2e42-p2c/RESULTS.md` §8, and the commits
  `1e5fe03`…`0a50fc4` on top of it): 1074 byte-exact / 0 fail, negative panel 184/184 refused,
  divergence panel 9/9, coverage 102 rows, runtime panel 71/71 as recorded.
- Phase: **E2E-42/P2c** — named-file `PUT FILE … SKIP` bank pre-registered, measured against DR,
  and lowered; claims through **[C308]**.
- Known open scientific item recorded there: `CREATE` still does not compile; remaining blockers
  are `^eofile` inside a `DO WHILE` condition and a store into `BIT(1)` from a condition — neither
  related to PUT. Also recorded, deliberately unfixed: `pli80c`'s `wrote … (data=N)` summary line
  reports a number that is not the DATA segment length.

## Last verified state — E2E-48/P1 COMPLETE for the 24-probe bank (session started 19:36 UTC, 2026-10-29)

**All 24 probes of `golden/e48p1/` are now whole-file byte-identical**, and all 24 are REGISTERED
on the byte panel. Measured in this session, in this order:

- `f839f52` — the census drift the gate aborted on was PROGRESS, not regression: CREATE's
  first-refusal message had moved past `(^ eofile)` (fixed by the `371a12e` NegL arm) and past
  `eofile = (name = 'EOF')` (fixed by `bit_cond_mat`) to `GET LIST of unknown variable name [TBD]`.
  Cause measured: `pli80c.ml` never expands `%include`, so `name` (RECORD.DCL) is unbound. Census
  re-measured through `tools/corpus_census.py --check <prev copy>`; counts IDENTICAL.
  Gate then measured **1074 byte-exact / 0 fail**, negative 184/184, divergence 9/9 — i.e. the
  `371a12e` arms broke nothing.
- `fa09b97` — `bit_store_cond_bytes` added to the prescan: my `371a12e` store arm allocated the
  `?SCVCM` literal's pool cell but `prescan_expr` has no `Econd` arm, so it was never demanded.
  Minimal measured repro: `b = (name = 'EOF');` demanded 1, allocated 4. **E48A12 became exact
  (15/24).**
- `df4b9c8` — step 4, the BIT(1) PUT item: `3A cell / 06 01 / CD ?QB08C / CD ?PNBOP`, nine sites
  (A15 000F sole item, A6 0038, A7 002C+005D, A8, A9, A10, A11, B8 0038). `?PNBOP` REPLACES the
  shared `tail true ()` `?PNCOP` (one tail per item: A6 0035 PNCOP, 0040 PNBOP, 0043 QIOOP). Two
  classifier admissions (Vbit1 in `only_literals_and_chars`; Vbit1 -> false in the blocking
  `List.exists`) plus three named refusals for unmeasured shapes (PUT EDIT, non-final bit item,
  file attach). The `authorize_file_item` reason that claimed "the console route refuses this class
  too" is kept as written and labelled SUPERSEDED (P15 falsified it). **23/24 exact.**
- `613385b` — step 5, STATIC on CHARACTER per R6: `RTchar (n, false)` with a literal INITIAL no
  longer than the extent, cell = full extent blank-padded (`41 42 20`), DATA 3 = 3 static + 0 pool,
  read back by the existing Vfix PUT arm at the DECLARED length. Refused on purpose: no INITIAL, a
  non-literal/longer initialiser, STATIC-on-CHARACTER **VARYING** (catch-all keeps its EXACT words
  for gate rows E46F5 and the FIXED-BINARY(15,0) row), and a store INTO a static char (scratch s1
  proved my automatic route would pool the literal beside the static cell, DATA 3 -> 5 — unmeasured).
  Census re-measured: counts identical, 5 msg deltas (REPORT advanced to `OPEN option KEYED`,
  MPMCALLB to `STATIC on POINTER MEMBER OF CPB@390`; EXPR2/FSCAN/LOAN2 same blocker). **24/24 exact.**
- `992ccad` — panel + claims. 24 SPECIMENS rows (byte tier ONLY: no `spec/RUNTIME.txt` rows, because
  this round captured .REL/.PRN evidence and eight probes read the console with `get list`),
  `--update-inventory` wrote INVENTORY.txt (1098 entries), and claims **C309-C316** record RESULTS §3
  as measured law with the [TBD] list inside C310. Final gate at this commit, measured:
  **1098 byte-exact / 0 fail of 1098**, negative panel 184/184 refused, divergence 9/9, coverage
  102 rows 0 errors, census `--verify` clean (EXACT 15 / DIFFERS 0 / REFUSED 26 / UNEXPECTED 0), rc=0.

Verification method notes for the successor: builds compared cache-neutrally (clean rebuild in a
scratch tree vs `git show <base>:ocaml/lib/codegen.ml`, warning multiset 22/15/28/2/14/2/17/26 —
unchanged); the sweep is
`for n in E48A{1..15} E48B{1..9}; do ./ocaml/_build/default/bin/pli80c.exe probes/$n.PLI /tmp/x/$n.REL && cmp /tmp/x/$n.REL golden/e48p1/$n/$n.REL; done`.

## Unfinished operations — E2E-48/P1 (open at this checkpoint)

- **No half-finished edit.** Working tree clean at this checkpoint except the three handoff files.
- OPEN (recorded, deliberately not started at this boundary): `spec/COVERAGE.tsv` rows for this
  bank's COND/STOR/IO shapes. `coverage_check` passes without them (it validates citations, not
  completeness), so this is a recorded gap, not a failing row.
- `[TBD]` items that must NOT be guessed (all inside C310/C313/C314): the CREATE-vs-E48 SCVCM
  load-order discriminator (18-byte `LXI H,var / XCHG / LXI H,lit` vs 17-byte `LXI H,lit / LXI D,var`
  — no probe varied it); the BIT-store materialiser for `k = c` with |c| in {1,2,3}; `= '0'b` as a
  materialised store; `^(cond)` in a STORE beyond `^(k = 0)`; nested `&` shapes beyond E48A14;
  a bit PUT item that is not final; a store into a STATIC CHARACTER; STATIC-on-CHARACTER VARYING.
- CREATE is NOT byte-exact. Its measured blocker is now front-end: `%include` is never expanded by
  `pli80c.ml` (only `bin/pli80bind.ml` does), so `get list (name)` refuses with an unbound name.

> STATUS 2026-10-30 (E2E-48/P2c): the SCVCM load-order discriminator in the second bullet is
> MEASURED and answered (operand CLASS; RESULTS sections 1-2 of e2e48-p2c); the other [TBD]
> items of that list are UNCHANGED and still must not be guessed. The COVERAGE rows remain
> unwritten (now sub-task 7 of the current Next action).

## Next action - E2E-48/P2c step 6: census re-measure, inventory, FULL GATE

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

## Unfinished operations (Pi Handoff deployment)

- **None in progress.** The Pi Handoff deployment (Phases A–E) is complete, and on
  2026-10-29 the operator authorized and live-tested the renewal activation (project trust,
  compaction disabled project-wide, `renewal.enabled/autoRenew`, cap 8). The remaining
  operator decisions listed in `PROGRESS.md` → Pending (reserve tuning, closing enforcement,
  push) stay **open by design** and are not half-applied.
- No compiler work was started, continued or left half-done in this session. Nothing in
  `ocaml/`, `spec/`, `tools/`, `golden/`, `oracle/` or `probes/` was touched by it, and no gate
  was executed by it.
- No commit was made on behalf of any scientific result; the only authorized commits from this
  session are infrastructure commits over: `.gitignore`, `AGENTS.md`, `GOAL.md`, `PROTOCOL.md`,
  `HANDOFF.md`, `PROGRESS.md`, `LEARNINGS.md`, `handoff.config.json`,
  `.pi/extensions/context-guard/*.ts`, `.agents/skills/pi-handoff/**`.

## Next action (superseded — E2E-48/P1 steps 1-4)

The 2026-10-29 predecessor's six-step list (write RESULTS.md, commit evidence, fix the
bind `span` double-count, gate) was COMPLETED this session: RESULTS.md + chaindump typo
fix at 388673b (all bytes re-derived from the goldens, both MISSes kept), bind fix at
a8d1c3a with the gate still 1074/0 and E48A3/A4 byte-identical. Its step 5 (codegen
arms) and step 6 (panel/claims/census) continue in `## Next action — E2E-48/P1 step 5`
above, which supersedes it in full. (The goldens were in fact already committed at
ece657e, before this step list was written.)

## Next action (historical — deployment window)

**Not established by this session.** A deployment session deliberately did not choose the
compiler's next task, and inventing one here would put an unmeasured intention into the file a
fresh session trusts. The first action of the next session is therefore evidence-reading, not
implementation:

> Read `spec/lab-evidence/e2e42-p2c/RESULTS.md` §7 (CREATE blockers), §8 (the recorded gate
> verdict) and §9 (the unfixed `data=` reporting defect), plus
> `spec/lab-evidence/e2e42-p2c/HYPOTHESES.md`, plus claims `C296`–`C308` in `spec/CLAIMS.md`,
> then `spec/INVENTORY.txt` rows whose refusal text names `^eofile` or a `BIT(1)` condition store.
> Expected output: the candidate next phases written as *pre-registerable hypotheses* (e.g. the
> `^eofile`-in-`DO WHILE` condition form, the `BIT(1)` condition store, the `data=` reporting defect
> in `pli80c`'s summary line). Pick one, write its probe bank and predictions, commit them **before**
> any oracle run — and replace this section with the exact chosen command.

## Discoveries not yet incorporated

- **Renewal e2e test 2026-10-29 — PASSED and closed.** Durable chain, attested-handoff
  recovery, file-only successor bootstrap and auto-checkpoint preservation all verified
  (renewal 1/8, parent `01a188a5-2c00-708a-affc-0a48428f85d5` → successor
  `01a188a6-36ee-708a-affc-0a4c9333a1c9`, checkpoint `g2-470d507dbf6c`). The successor's
  start-pressure reading (~9 000 remaining) was **not** an anomaly: the test deliberately set
  `CONTEXT_GUARD_SYNTHETIC_REMAINING=9000` in the child *process* environment, and that
  synthetic override is re-read at every session_start in the process — by design, not
  measurement. The INFRA TEST WINDOW is closed: the genuine next action above was restored
  verbatim from `a6eec67`. Full record: `PROGRESS.md` → Renewal test window; lessons in
  `LEARNINGS.md`.

- `AGENTS.md`'s reading order, the guard's managed-block rules and `PROTOCOL.md` Part 2 are new to
  this repository; nothing in `spec/` has been reconciled against them, and nothing in `spec/`
  needed reconciling (the guard writes no scientific file).
- `README.md` "Current status (rolling)" is stale relative to the ledger: it still ends at
  **E2E-1 / C067** ("Next: widen codegen to RTL-call arithmetic …"), while HEAD is deep in E2E-42.
  It was deliberately **not** edited here (it is outside the authorized file list for this
  deployment) and is not to be used for status. Correcting it is an open, low-risk documentation
  task for a normal session.
- `generationReserve: 20000` in `handoff.config.json` is an **initial policy value**, not a
  verified fit for the model actually used on DRPLi. It should be checked against the real
  context window and max-output budget reported by `/guard status` before being treated as tuned.
- **Resolved 2026-10-29 (operator decision):** project trust was granted for the exact path
  `/home/john/projects/sushiworks/pli80` (plain `pi` from the project root now auto-discovers
  the extension and the skill; verified in the session started 16:58 UTC — parent cmdline is
  bare `pi`, guard loaded once). Renewal is ENABLED in `handoff.config.json`
  (`enabled/autoRenew true`, `maxRenewals 8`) and Pi auto-compaction is disabled for this
  project via `.pi/settings.json`. Controlled launches strip the inherited
  `CONTEXT_GUARD_AUTO_RENEW=1` with `env -u CONTEXT_GUARD_AUTO_RENEW` so the project config is
  authoritative (see `PROTOCOL.md` → Load).
- Managed checkpoint blocks were hand-edited **once**, deliberately, as the E2 test of the
  level-3 auto-checkpoint preservation path (a `TEST-E2-*` marker, since superseded by the final
  `/handoff` write). Outside such an explicit test, blocks are guard-written only.
<!-- guard:begin checkpoint -->
checkpoint-schema: 3
checkpoint-generation: 18
checkpoint-id: g18-e469320c8d62
checkpoint-kind: auto
content-delta: new
readiness: unattested
status: checkpoint (guard level 4, remaining ~4634, session 01a1899c-bfe2-7470-93c0-80efada31a9a)
checkpointed: 2026-10-29T22:19:29.659Z
source-goal: 730790b648a1e1d14b76243cfe8bc17eea2ba9cd8527f204f9c8d4dbcc527c9d
source-progress: c994ff4745d9c8a042f283cdd40662850e028b1e1d964c6109b8e336847d7fba
source-handoff: f089cb30c0701daf190245715f7bc796b7b3836df5afebcf55d69273207ffa6b
source-learnings: 58874fda930af7a574f431b88ca96dc7c104830a3adc78d3539fbaaae9bf8fc1
source-config: 8e66b82b71db399633cd776d6a5329e70c0eb09173121cfb303569d5f6ba6bf3


### Last verified state
guard level 4; checkpoint requested (auto at level 4)

### Unfinished operations
- (none recorded)

### Next action
- E2E-48/P2c step 6: census re-measure, inventory, FULL GATE

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
> **THE EXACT NEXT ACTION is step 6, then step 7:**
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

### Guard notes
E2E-48/P2c implementation: HANDOFF.md -> "Next action - E2E-48/P2c implementation" STATUS block. HEAD 5f03a2f (clean). Steps 1(a)(b)(c)+3 DONE and measured at 7701f52: dune rc=0, 6/9 golden/e48p2c byte-identical (C1,C2,C5,C6,C7,C9), 24/24 golden/e48p1 byte-identical. EXACT NEXT ACTION = sub-step 4a: widen store_char's qualified-DESTINATION gate for a VARYING internal member with a STRING-LITERAL source (licensed by golden/e48p2c/E48C3, whose golden differs from E48C2 only at the three module-name bytes 6/19/28); then 4b = STATIC-on-CHARACTER-VARYING placement (E48C8) + re-measure E46F5's pinned negative row through the tool write path; then step 2 refusal WHY-strings, step 5 sweep to 9/9, step 6 registration (SPECIMENS rows E48C1..C9 byte tier only, INVENTORY 1098->1107, claims C317..C320 + C310 annotation, census --check, FULL GATE expected 1107/0 — the 1098/0 figure is recorded only at 1595a10 and has NOT been re-run since 6130164). Do NOT implement RESULTS §3 shapes; TEST member-as-RIGHT stays refused via str_cmp_shape_rev's ?imem=false default. Never rewrite a golden; stage explicit paths; no push authorized; renewal 7/8.
<!-- guard:end checkpoint -->
