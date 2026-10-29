# PROGRESS.md — DRPLi

Manual prose wins over the managed block below it. Do not hand-edit the managed block.
This file tracks *working state*; compiler behaviour itself belongs to `spec/CLAIMS.md`.

## Current phase

**E2E-48/P1 is CLOSED: all 24 probes of `golden/e48p1/` are whole-file byte-identical and all 24
are registered on the byte panel. Gate measured 1098 byte-exact / 0 fail, negative 184/184,
divergence 9/9, coverage 102 rows 0 errors, census `--verify` clean.**

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

- **E2E-48/P1 step 5, resumed** — see `HANDOFF.md` → `## Next action

See `HANDOFF.md` → `## Next action — E2E-48 round 2 (the [TBD] list), or the COVERAGE rows`.
E2E-48/P1 step 5 is closed (24/24 byte-identical, 1098/0 measured at `992ccad`); the successor
picks either the pre-registered E48C discriminator round, or the COVERAGE rows, or `%include`
(CREATE's measured front-end blocker) — in that order of value.

<!-- guard:begin checkpoint -->
checkpoint-schema: 3
checkpoint-generation: 9
checkpoint-id: g9-49521ef3acb6
checkpoint-kind: manual
content-delta: new
readiness: attested
guard-level: 4
checkpointed: 2026-10-29T19:33:11.148Z
source-goal: 730790b648a1e1d14b76243cfe8bc17eea2ba9cd8527f204f9c8d4dbcc527c9d
source-progress: e029e6e3d09400b519da970756395bb67f53d0377025a0b978eba6b94af92c29
source-handoff: 1b28af5c24aaa1a60c49cdf30750886b3a541f61b5e976e29d6972c3503fd003
source-learnings: 9b086586388c7011605fa654d8c94e5173ab68a5719f9d943520e80f92e552bd
source-config: 8e66b82b71db399633cd776d6a5329e70c0eb09173121cfb303569d5f6ba6bf3
next-action: — E2E-48/P1 step 5, resumed (steps 1-3 DONE at `371a12e`; step 4 open)

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
readiness-by: session:01a18900-db17-7470-93c0-80deb112c0f8
readiness-at: 2026-10-29T19:33:11.152Z
readiness-checkpoint: g9-49521ef3acb6
<!-- guard:end checkpoint -->
