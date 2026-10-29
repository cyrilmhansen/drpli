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

## Next action — E2E-48 round 2 (the [TBD] list), or the COVERAGE rows

Steps 1-5 and panel registration are DONE; E2E-48/P1 is closed at 24/24 byte-identical and
1098/0. Pick ONE, in this order of value:

1. **Pre-register E48C to measure the SCVCM load-order discriminator** (the only [TBD] that blocks
   a corpus program: CREATE's 18-byte store). Write the probe bank and the predictions, COMMIT them
   BEFORE any oracle run (PROTOCOL #1), then measure with `oracle/batch.py --tag e48p2c` (needs
   `--reuse` if the tag exists; it only ADDS programs). Candidates that vary the discriminator:
   the same `eofile = (name = 'EOF')` store in a DO-WHILE body vs a straight-line body vs behind a
   `put`; a VARYING **member** left operand (the `Mem` shape `bit_cond_mat` refuses today).
   Expected output: new goldens + a claim that names the rule, or a recorded `dr-refuses` row.
2. **`spec/COVERAGE.tsv` rows** - started but NOT written (this session reached the format check
   only, then hit level 3). Format facts MEASURED here, so do not re-derive them: **15** tab-separated
   columns (`id category construct contract perimeter manual_ref dr_status mine_status rel_parity
   runtime probes corpus boundary confidence provenance`); `manual_ref` is column 6, which the FIRST
   table of `spec/COVERAGE-SCHEMA.md` omits - trust the second table and an existing row such as
   `COND.GE_LE`. `probes` = comma-separated INVENTORY keys (E48A1..E48B9 are on the panel now, so they
   resolve); `corpus` = names from the 44-program census (CREATE, EXPR2, FSCAN, LOAN2, MPMCALLB,
   REPORT all qualify); `provenance` = space-separated `[Cnnn]` (C309-C316 exist); use
   `manual_ref = NONE:<why>` to stay clear of the OCR page check. `tools/coverage_check.py` line 8 and
   213: a `MEASURED`/`SINGLE_SAMPLE` row must name at least one probe that one of its OWN cited claims
   also names - cite the claim carrying the specimen ([C313] names E48A15/A6/A7/B8). Drafted rows:
   COND.BIT1_NEG_TEST (E48A1,A2,A5,A12,A13,B1,B7 EXACT:7, [C309][C311]); STOR.BIT1_COND_STORE
   (E48A6..A12,B8,B9 EXACT:9, [C310], boundary = the load-order / |c|<=3 / ='0'b [TBD]s);
   COND.AND_BIT1_OPERAND (E48A14 EXACT:1, SINGLE_SAMPLE, [C312]); IO.PUT_BIT1_ITEM (E48A15,A6,A7,B8
   EXACT:4, runtime NONE because no transcript was captured, [C313]); DECL.STATIC_CHAR (E48B5,B6,B7
   EXACT:3, mine_status PARTIAL because STATIC-on-CHARACTER VARYING still refuses, [C314]).
   Validate with `python3 tools/coverage_check.py` (exit 0), then `python3 tools/e2e_gate.py`: the row
   count goes 102 -> 107 and the byte panel must stay 1098 byte-exact / 0 fail.
3. `%include` in the main pipeline (CREATE's real blocker) — bigger, and needs its own
   pre-registered round for DR's search order/case rules.

Commands to start either way:
  `git rev-parse HEAD` -> expect `992ccad` or a descendant; `git status --porcelain=v1` -> expect
  clean (or only handoff files); `python3 tools/e2e_gate.py` -> **1098 byte-exact / 0 fail**.

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
checkpoint-generation: 11
checkpoint-id: g11-b58aa40e9fee
checkpoint-kind: auto
content-delta: new
readiness: unattested
status: checkpoint (guard level 4, remaining ~3620, session 01a18927-3b36-7470-93c0-80e28e177244)
checkpointed: 2026-10-29T20:12:44.744Z
source-goal: 730790b648a1e1d14b76243cfe8bc17eea2ba9cd8527f204f9c8d4dbcc527c9d
source-progress: cee577b1760ea6379ccb2a0e9e06aa65351c103a38cf57d7ad610620b29d3b8a
source-handoff: d8c627c77f70e481592000c272fb50fb1f199abc65cddff8655668fe6dc8ee0e
source-learnings: 123479d0c781a1ca2ebc186ad04a3754ce3ae21837dc4f1b878e5322e64f768d
source-config: 8e66b82b71db399633cd776d6a5329e70c0eb09173121cfb303569d5f6ba6bf3


### Last verified state
guard level 4; checkpoint requested (auto at level 4)

### Unfinished operations
- (none recorded)

### Next action
— E2E-48 round 2 (the [TBD] list), or the COVERAGE rows

Steps 1-5 and panel registration are DONE; E2E-48/P1 is closed at 24/24 byte-identical and
1098/0. Pick ONE, in this order of value:

1. **Pre-register E48C to measure the SCVCM load-order discriminator** (the only [TBD] that blocks
   a corpus program: CREATE's 18-byte store). Write the probe bank and the predictions, COMMIT them
   BEFORE any oracle run (PROTOCOL #1), then measure with `oracle/batch.py --tag e48p2c` (needs
   `--reuse` if the tag exists; it only ADDS programs). Candidates that vary the discriminator:
   the same `eofile = (name = 'EOF')` store in a DO-WHILE body vs a straight-line body vs behind a
   `put`; a VARYING **member** left operand (the `Mem` shape `bit_cond_mat` refuses today).
   Expected output: new goldens + a claim that names the rule, or a recorded `dr-refuses` row.
2. **`spec/COVERAGE.tsv` rows** - started but NOT written (this session reached the format check
   only, then hit level 3). Format facts MEASURED here, so do not re-derive them: **15** tab-separated
   columns (`id category construct contract perimeter manual_ref dr_status mine_status rel_parity
   runtime probes corpus boundary confidence provenance`); `manual_ref` is column 6, which the FIRST
   table of `spec/COVERAGE-SCHEMA.md` omits - trust the second table and an existing row such as
   `COND.GE_LE`. `probes` = comma-separated INVENTORY keys (E48A1..E48B9 are on the panel now, so they
   resolve); `corpus` = names from the 44-program census (CREATE, EXPR2, FSCAN, LOAN2, MPMCALLB,
   REPORT all qualify); `provenance` = space-separated `[Cnnn]` (C309-C316 exist); use
   `manual_ref = NONE:<why>` to stay clear of the OCR page check. `tools/coverage_check.py` line 8 and
   213: a `MEASURED`/`SINGLE_SAMPLE` row must name at least one probe that one of its OWN cited claims
   also names - cite the claim carrying the specimen ([C313] names E48A15/A6/A7/B8). Drafted rows:
   COND.BIT1_NEG_TEST (E48A1,A2,A5,A12,A13,B1,B7 EXACT:7, [C309][C311]); STOR.BIT1_COND_STORE
   (E48A6..A12,B8,B9 EXACT:9, [C310], boundary = the load-order / |c|<=3 / ='0'b [TBD]s);
   COND.AND_BIT1_OPERAND (E48A14 EXACT:1, SINGLE_SAMPLE, [C312]); IO.PUT_BIT1_ITEM (E48A15,A6,A7,B8
   EXACT:4, runtime NONE because no transcript was captured, [C313]); DECL.STATIC_CHAR (E48B5,B6,B7
   EXACT:3, mine_status PARTIAL because STATIC-on-CHARACTER VARYING still refuses, [C314]).
   Validate with `python3 tools/coverage_check.py` (exit 0), then `python3 tools/e2e_gate.py`: the row
   count goes 102 -> 107 and the byte panel must stay 1098 byte-exact / 0 fail.
3. `%include` in the main pipeline (CREATE's real blocker) — bigger, and needs its own
   pre-registered round for DR's search order/case rules.

Commands to start either way:
  `git rev-parse HEAD` -> expect `992ccad` or a descendant; `git status --porcelain=v1` -> expect
  clean (or only handoff files); `python3 tools/e2e_gate.py` -> **1098 byte-exact / 0 fail**.

### Guard notes
E2E-48/P1 step 5: codegen arms steps 1-3 are DONE, committed at 371a12e (ocaml/lib/codegen.ml) and probe-verified — 14 of 24 golden/e48p1 whole .REL files byte-identical (E48A1 A2 A3 A4 A5 A13 A14 B1 B2 B3 B4 B5 B7 B9); 10 still differ (E48A6 A7 A8 A9 A10 A11 A12 A15 B6 B8). dune build rc=0, no new warning kinds. THE GATE HAS NOT BEEN RE-RUN since these arms landed — run `python3 tools/e2e_gate.py` and require 1074/0 before registering anything; if it is not 1074/0 that regression outranks all other work. Next action is in HANDOFF.md "Next action — E2E-48/P1 step 5, resumed": diff each differing probe against its golden with spec/lab-evidence/e2e42-p2b/chaindump.py (both files) — E48B9 (EXACT, two SCVCM stores) vs E48A6/A7/B8 (differ) is the discriminator already in hand; then step 4 (PUT bit item: 3A reloc / 06 01 / ?QB08C / ?PNBOP replacing the shared tail's ?PNCOP, plus the char_var_ok classifier must stop treating Vbit1 as a blocking char var), step 5 (STATIC-on-CHARACTER per E48B6), panel registration, claims C309+, INVENTORY/COVERAGE, gate, census. Do NOT guess the [TBD] list in HANDOFF.md (CREATE-vs-E48 SCVCM load order; k=c |c|<=3 store form; ='0'b materialised; ^ in store beyond k=0; nested & shapes). Gate rows pin refusal TEXTS: "store into BIT(1) from ident is unsampled" (N74) and "condition form not in E2E-3b subset" (MB13/LR9/E32C3). LEARNINGS.md carries the new accepted lesson: an unparenthesised `match` as an OCaml arm body silently steals the enclosing match's later arms (compiles clean, died as Match_failure at a line I never edited) — write one arm, rebuild, re-sweep. Never rewrite goldens; stage explicit paths; do not push.
<!-- guard:end checkpoint -->
