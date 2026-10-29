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

## Last verified state — E2E-48/P1 step 5 (codegen arms, session started 19:12 UTC)

**COMMITTED at `371a12e` (ocaml/lib/codegen.ml only).** VERIFIED BY MEASUREMENT IN THIS SESSION:
`dune build` rc=0 with no new warning kinds, and the 24-probe sweep (`pli80c.exe` then whole-file
`cmp` against `golden/e48p1/N/N.REL`) gave **14 BYTE-IDENTICAL** —
E48A1 A2 A3 A4 A5 A13 **A14** B1 B2 B3 B4 B5 B7 **B9** — and **10 differing** —
E48A6 A7 A8 A9 A10 A11 A12 A15 B6 B8. E48A14 exact proves the step-3 `&`-bit arm; E48B9 exact
proves the §3.2 SCVCM store route on a plain cell. **The gate was NOT re-run after the arms**
(1074/0 is inherited from `a8d1c3a` and must be re-measured before any panel registration).

Arms landed: the `Ast.Eprefix (Ast.NegL, x)` TEST arm (^bare bit -> 3A/B7/FA; ^(k=0) ->
21/7E/23/B6/CA; ^(k=c) c>=1 -> cmp_load_deref/hl_bias(-c)/7C/B5/CA); `bit_cond_mat`, the §3.2
store classifier returning None for every unpinned shape; the `lower_bool` BIT(1) right operand
(`F5 / 3A / C1 / A0` under one `F2`); and the Vbit1 store arm rewritten as `begin match ... end`.

That last rewrite fixed a **regression I caused and then verified fixed**: an unparenthesised
`match rhs.Ast.e with` as an arm body absorbed every following `| Ast.Eident ...` arm of the OUTER
`match lhs.Ast.e`, so 15 probes died with `Match_failure` at codegen.ml:8026 — a line I never
edited. Lesson recorded in `LEARNINGS.md`; the fix is now build- and sweep-verified.

NOT done: step 4 (PUT bit item — A15 refuses, and `char_var_ok` blocks the 2-item [literal,bit]
lists A6/A7/A8/A9/A10/B8 put), step 5 (STATIC-on-CHARACTER — B6), panel registration, claims
C309+, INVENTORY/COVERAGE, gate, census.

**Successor's first job: diff each of the 10 differing probes against its golden with
`python3 spec/lab-evidence/e2e42-p2b/chaindump.py` on BOTH files.** E48B9 (exact, two SCVCM
stores) versus E48A6/A7/B8 (differ) is the discriminator already in hand; do not guess past it,
and never edit a golden.

## Unfinished operations — E2E-48/P1 (open at this checkpoint)

- DONE since `ece657e`: `RESULTS.md` (prediction-vs-verdict, all bytes re-derived; MISSes kept:
  P15 accepted, P6/P7/P11 spellings, the 8-byte miscount, the falsified "DAD defect" — §5);
  chaindump.py:38 typo fixed in the same commit (388673b); bind span fix + gate (a8d1c3a).
  Working tree clean at this checkpoint; `ocaml/` compiles (dune via `opam exec`).
- OPEN: the codegen arms of HANDOFF "Next action" (none started yet — no half-edited file);
  no `spec/CLAIMS.md` rows yet (next free id **C309**); no INVENTORY/COVERAGE rows; E48
  specimens not in the panel; census not re-run for this phase.
- `[TBD]` items that must NOT be guessed: the CREATE-vs-E48 SCVCM load-order discriminator;
  the BIT-store materialiser for `k = c` with |c| ∈ {1,2,3} (only c=0 and |c|≥4 are pinned);
  `= '0'b` as a materialised (stored) comparison (only `'1'b` pinned, E48A10); `^(cond)` in
  a STORE beyond `^(k = 0)`; nested `&` shapes beyond E48A14.

## Next action — E2E-48/P1 step 5, resumed (steps 1-3 DONE at `371a12e`; step 4 open)

**Steps 1-3 are committed and probe-verified: 14 of 24 goldens byte-identical. The successor's
first job is the DIFF of the 10 that still differ, not new arms.** Never `git clean`/`reset`.

0. `git status --porcelain=v1` → expect ONLY the three handoff files (or clean).
   `cd ocaml && opam exec --switch=default -- dune build` → rc=0 (measured at `371a12e`).
   `python3 tools/e2e_gate.py` → must still be **1074/0**; the gate has NOT been run since the
   arms landed, and if it is not 1074/0 that regression outranks every other item here.
1. For each differing probe (E48A6 A7 A8 A9 A10 A11 A12 A15 B6 B8) diff mine against the golden:
   `python3 spec/lab-evidence/e2e42-p2b/chaindump.py /tmp/e48fix/N.REL` and the same on
   `golden/e48p1/N/N.REL`. E48B9 is EXACT and carries TWO SCVCM stores while E48A6/A7/B8 differ
   — that pair is the in-hand discriminator. Re-run the sweep afterwards:
   `for n in E48A{1..15} E48B{1..9}; do … pli80c.exe ../probes/$n.PLI /tmp/e48fix/$n.REL; cmp vs
   ../golden/e48p1/$n/$n.REL; done`.
   Expected after the begin/end fix: E48A1/A2/A3/A4/A5/A13/B1/B7 EXACT (8), the store probes
   (A6/A7/A8/A9/A11/A12/B8/B9) EXACT if `bit_cond_mat` matches the goldens, E48A10 EXACT, E48A14
   EXACT (step 3), and E48A15/A10-PUT + E48B6 still refusing (steps 4/5 open). Read the
   `cmp` failures with `python3 spec/lab-evidence/e2e42-p2b/chaindump.py` on both files; the
   golden is the authority, never my output.
2. Gate must stay **1074 byte-exact / 0 fail** before panel registration:
   `python3 tools/e2e_gate.py`. Two negative-panel rows constrain the refusal TEXTS:
   `N74_FIXED…`/`N74_BIT_TO_BIT_COPY` requires the substring
   `"store into BIT(1) from ident is unsampled"` (my new message keeps that prefix — verified by
   reading `tools/e2e_gate.py:1699-1717`, NOT by running the gate), and
   `"condition form not in E2E-3b subset"` stays required at gate lines 1778/3157/4421 (MB13,
   LR9, E32C3) — the catch-all in `lower_test_skip0` is still reachable for unpinned NegL shapes,
   but my new inner refusal for `^(<other>)` has its OWN text; if a row breaks, keep the
   catch-all reachable rather than editing the gate.
3. Remaining arms (unchanged from the list below): step 4 the PUT bit item
   (`3A reloc / 06 01 / ?QB08C / ?PNBOP`, refusal at the old ≈10317 `Vbit1 -> failwith`; note
   `?PNBOP` REPLACES the shared `tail true ()`'s `?PNCOP`, and the `char_var_ok` classifier must
   stop treating Vbit1 as a blocking char var — E48A6/A7/A8/A9/A10/B8 are 2-item `[literal,bit]`
   console lists), and step 5 STATIC-on-CHARACTER (E48B6, largest, defer freely).
4. Then panel registration, claims C309+, INVENTORY/COVERAGE, gate, census (items 6-7 below).

Everything below is the predecessor's arm map, still accurate except where marked DONE above.
All arm locations were read in-session (2026-10-29, commit a8d1c3a) — reuse them, do not re-explore:

1. `ocaml/lib/codegen.ml` `lower_test_skip0`: beside the positive bare-bit arm (≈6993, emits
   `0x3a / reloc / op_ora_a / op_jp / 2-byte slot`), add `Ast.Eprefix (Ast.NegL, x)` with
   `x` unwrapped (parser gives `(^ b)` bare-Eident and `(^ (cond ...))` = Econd-wrapped):
   - `Eident Vbit1` → same ladder, skip `0xfa` (JM) [E48A1/A2/A5/A12/B1/B7, CREATE 0052];
   - `Ebinary(EqR Eq, Eident v, Enumber "0")` → `val_addr / 7E / 23 / B6 / 0xca` [E48A13 000F];
   - `Ebinary(EqR Eq, Eident v, Enumber k)` kk ≥ 1 → `cmp_load_deref / hl_bias(-kk) / 7C / B5 /
     0xca` [E48A13 002F pins kk=3 = DCX×3; hl_bias ≥4 = LXI B + op_dad_b 0x09 = E48A12/B1];
   - anything else under NegL keeps refusing (name the shape).
   DO-WHILE/IF skip targets need no change — the existing slot-fill machinery already emits
   `00 00` + SET-LC/RELOC and matches DR (proved by the E48A3/A4 whole-file identity).
2. The BIT(1) store arm (≈8210): replace the unconditional refusal after the `Ebit` literal
   cases with a materialiser dispatch ending `32 <cell>` (STA, `d st 0x32; reloc st Data`):
   - `str_cmp_shape st l rr` (varying = literal) → run `hl_fn(); de_fn(); MVI A,len;
     call_ext "?SCVCM"` then `op_sui 01 / op_sbb_a` [E48A6/B8/B9 17 bytes — hl_fn is already
     LXI H,lit / de_fn LXI D,var, the arm at ≈7200 proves it];
   - `Ebinary(EqR Eq, Eident, Enumber "0")` → `val_addr / bin_zero_tail` (≈6507) [=0 → FF];
   - `Ne 0` or `Eprefix(NegL, Econd(Eq k 0))` → `val_addr / 7E / 23 / B6 / 0xc6 0xff / 9f`
     [E48A8/A11]; `Gt 0` → `21 k / 0xaf / 0xbe / 0x23 / 0x9e` [E48A9, no tail];
   - `Eq k` kk ≥ 4 → `cmp_load_deref / hl_bias(-kk) / 7C / B5 / D6 01 / 9F` [E48A7 k=5];
   - `Ebinary(EqR Eq, Eident Vbit1, Ebit "1")` → `0x3a reloc / E6 80 / D6 80 / D6 01 / 9F`
     [E48A10]. Refuse everything else (the [TBD] list above).
3. `lower_bool` (≈6545) And-arm: in the right-operand match chain add `Eident v when Vbit1` →
   `d st op_push_psw; d st 0x3a; reloc st Data (addr_of ...)` before the shared
   `pop_b / ana_b` [E48A14].
4. PUT: refusal at ≈10317 → bit item `0x3a reloc / 0x06 0x01 / call_ext "?QB08C" /
   call_ext "?PNBOP"` (after literal items' SLCTS/PNCOP, before QIOOP) [E48A15/A6/A7/B8].
5. STATIC-on-CHARACTER per E48B6 (cell = full extent blank-padded, DATA 0000, pool 0, PUT
   reads the cell with declared length) — locate the refusal first (bind/codegen "STATIC on
   CHAR" text; gate NEG rows E46F5). Largest arm; do LAST or defer to a follow-up commit.
6. Verify each step: `cd ocaml && opam exec --switch=default -- dune build`; compile probes to
   `/tmp/e48fix/` (usage: `pli80c.exe IN.PLI OUT.REL`) and `cmp` against `golden/e48p1/N/N.REL`;
   run `python3 tools/e2e_gate.py` (must stay 1074/0 until panel registration, then grows).
7. Then: register `E48A*/E48B*` in `tools/e2e_gate.py` SPECIMENS; claims C309+ from RESULTS §3;
   INVENTORY/COVERAGE rows; gate; `python3 tools/corpus_census.py --check`. CREATE EXACT likely
   needs the [TBD] SCVCM load-order — if it blocks, measure the discriminator with a NEW
   pre-registered probe round (E48C) before implementing, or report census honestly unchanged.


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
checkpoint-generation: 8
checkpoint-id: g8-ca0d7b0cae81
checkpoint-kind: auto
content-delta: none
readiness: unattested
status: checkpoint (guard level 4, remaining ~4838, session 01a18900-db17-7470-93c0-80deb112c0f8)
checkpointed: 2026-10-29T19:27:30.740Z
source-goal: 730790b648a1e1d14b76243cfe8bc17eea2ba9cd8527f204f9c8d4dbcc527c9d
source-progress: 52a3c0455591a5b4a2771956ae819f53efd5102e9201da2e01713a4b55432cf6
source-handoff: fb47e4976b67c5f749535dbdb05d5bd2c05e25c026cb8240ece21603d734b304
source-learnings: 7c0e8146fde39a8bbe29b79e661af80c7fa413d66c6c60f9013378b4475376db
source-config: 8e66b82b71db399633cd776d6a5329e70c0eb09173121cfb303569d5f6ba6bf3


### Last verified state
guard level 4; checkpoint requested (auto at level 4)

### Unfinished operations
- (none recorded)

### Next action
— E2E-48/P1 step 5, the exact continuation (codegen arms)

All arm locations were read in-session (2026-10-29, commit a8d1c3a) — reuse them, do not re-explore:

1. `ocaml/lib/codegen.ml` `lower_test_skip0`: beside the positive bare-bit arm (≈6993, emits
   `0x3a / reloc / op_ora_a / op_jp / 2-byte slot`), add `Ast.Eprefix (Ast.NegL, x)` with
   `x` unwrapped (parser gives `(^ b)` bare-Eident and `(^ (cond ...))` = Econd-wrapped):
   - `Eident Vbit1` → same ladder, skip `0xfa` (JM) [E48A1/A2/A5/A12/B1/B7, CREATE 0052];
   - `Ebinary(EqR Eq, Eident v, Enumber "0")` → `val_addr / 7E / 23 / B6 / 0xca` [E48A13 000F];
   - `Ebinary(EqR Eq, Eident v, Enumber k)` kk ≥ 1 → `cmp_load_deref / hl_bias(-kk) / 7C / B5 /
     0xca` [E48A13 002F pins kk=3 = DCX×3; hl_bias ≥4 = LXI B + op_dad_b 0x09 = E48A12/B1];
   - anything else under NegL keeps refusing (name the shape).
   DO-WHILE/IF skip targets need no change — the existing slot-fill machinery already emits
   `00 00` + SET-LC/RELOC and matches DR (proved by the E48A3/A4 whole-file identity).
2. The BIT(1) store arm (≈8210): replace the unconditional refusal after the `Ebit` literal
   cases with a materialiser dispatch ending `32 <cell>` (STA, `d st 0x32; reloc st Data`):
   - `str_cmp_shape st l rr` (varying = literal) → run `hl_fn(); de_fn(); MVI A,len;
     call_ext "?SCVCM"` then `op_sui 01 / op_sbb_a` [E48A6/B8/B9 17 bytes — hl_fn is already
     LXI H,lit / de_fn LXI D,var, the arm at ≈7200 proves it];
   - `Ebinary(EqR Eq, Eident, Enumber "0")` → `val_addr / bin_zero_tail` (≈6507) [=0 → FF];
   - `Ne 0` or `Eprefix(NegL, Econd(Eq k 0))` → `val_addr / 7E / 23 / B6 / 0xc6 0xff / 9f`
     [E48A8/A11]; `Gt 0` → `21 k / 0xaf / 0xbe / 0x23 / 0x9e` [E48A9, no tail];
   - `Eq k` kk ≥ 4 → `cmp_load_deref / hl_bias(-kk) / 7C / B5 / D6 01 / 9F` [E48A7 k=5];
   - `Ebinary(EqR Eq, Eident Vbit1, Ebit "1")` → `0x3a reloc / E6 80 / D6 80 / D6 01 / 9F`
     [E48A10]. Refuse everything else (the [TBD] list above).
3. `lower_bool` (≈6545) And-arm: in the right-operand match chain add `Eident v when Vbit1` →
   `d st op_push_psw; d st 0x3a; reloc st Data (addr_of ...)` before the shared
   `pop_b / ana_b` [E48A14].
4. PUT: refusal at ≈10317 → bit item `0x3a reloc / 0x06 0x01 / call_ext "?QB08C" /
   call_ext "?PNBOP"` (after literal items' SLCTS/PNCOP, before QIOOP) [E48A15/A6/A7/B8].
5. STATIC-on-CHARACTER per E48B6 (cell = full extent blank-padded, DATA 0000, pool 0, PUT
   reads the cell with declared length) — locate the refusal first (bind/codegen "STATIC on
   CHAR" text; gate NEG rows E46F5). Largest arm; do LAST or defer to a follow-up commit.
6. Verify each step: `cd ocaml && opam exec --switch=default -- dune build`; compile probes to
   `/tmp/e48fix/` (usage: `pli80c.exe IN.PLI OUT.REL`) and `cmp` against `golden/e48p1/N/N.REL`;
   run `python3 tools/e2e_gate.py` (must stay 1074/0 until panel registration, then grows).
7. Then: register `E48A*/E48B*` in `tools/e2e_gate.py` SPECIMENS; claims C309+ from RESULTS §3;
   INVENTORY/COVERAGE rows; gate; `python3 tools/corpus_census.py --check`. CREATE EXACT likely
   needs the [TBD] SCVCM load-order — if it blocks, measure the discriminator with a NEW
   pre-registered probe round (E48C) before implementing, or report census honestly unchanged.

### Guard notes
E2E-48/P1 step 5 (codegen arms) is the next action — HANDOFF.md "Next action — E2E-48/P1 step 5" contains the exact arm locations, reusable helpers (bin_zero_tail, str_cmp_shape, cmp_load_deref/hl_bias, lower_bool And-arm chain), the byte tables from spec/lab-evidence/e2e48-p1/RESULTS.md §3, and the [TBD] list that must NOT be guessed (CREATE-vs-E48 SCVCM load order; k=c |c|<=3 store form; ='0'b materialised; ^ in store beyond k=0). Durable state committed at 138bc06; gate verified 1074/0 at a8d1c3a; E48A3/A4 already byte-identical. Implement arms -> cmp vs golden/e48p1/N/N.REL -> register panel -> claims C309+ -> gate -> census. Never rewrite goldens; stage explicit paths; do not push.
<!-- guard:end checkpoint -->
