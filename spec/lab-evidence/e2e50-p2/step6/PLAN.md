# E2E-50/P2 step 6 — pre-registration: plan + predicted verdicts

Committed BEFORE any emulator or DR-tool execution (PROTOCOL #1). Authority: `HANDOFF.md` →
Next action, mission E2E-50/P2 step 6. Bounded, isolated, lane-labelled runs only; never the
oracle campaign, never the full runtime tier, never Rune CI.

## Inputs landed before the runs (measured without any external process)

- Lane A fixtures: `spec/functional/tests/FX-00.asm` / `FX-01.asm` (original DRPLi work, LF,
  ASCII, ≤71 cols) and `spec/functional/fixtures/FX-00.COM` / `FX-01.COM`, emitted by
  `tools/mk_functional_fixture.py` from ONE op table; `--check` rc=0 (listing + artifact +
  width agree). Encodings cross-checked read-only against the audited decoder
  (`/home/john/pli/lab/lib/i8080/decode.ml` `lower_opcode`) and the lab's `HELLO.COM.asm`
  listing (`0E 09` = MVI C,9 — my first draft used 0xE8, which is RRC: corrected before any run).
  sha256: FX-00.COM `d2b576cb…` (109 B), FX-01.COM `c555bdad…` (45 B).
- Specs `FX-00.json`, `FX-01.json` (schema `pli80-functional/1`, lane A only,
  `capabilities: []`), expectations from `reference.py:fx00/fx01` — DECLARED, never captured
  (law L3).
- Law amendment (README § 3, labelled): empty `capabilities` is legal ONLY for a Lane-A-only
  substrate fixture (assembly exercises no PL/I construct; § 7 has nothing to validate).
  Lane B / multi-lane specs still fail closed. Measured: hostile suite rc=0 (148 checks) after
  the change — no pinned check was broken; a suite case pinning BOTH sides of the amendment is
  OWED (recorded in PROGRESS).
- BDOS census probe: `functional_runner.py --census PROGRAM.COM` (substrate probe, NOT a
  verdict; parses `BDOS\t…` / `TERM\t…\tbdos:n` events from the Runes structured trace).

## Predictions (written before the runs; falsified text stays here per PROTOCOL #2)

| id | lane | predicted verdict | predicted evidence |
|---|---|---|---|
| FX-00 | A | PASS (SOURCE,DERIVATION pass; COMPILE,LINK not-applicable; RUN exit-0 witness; ASSERT 2 lines) | stdout `FX-00 CORE OK\r\nBDOS2-OK\r\n`; trace census {0,2,9,11,12}, 13 calls (1×9, 10×2, 1×11, 1×12, 1×0), term witness `bdos:0` |
| FX-01 | A | FAIL, attribution `emulator`, stopped at RUN | rc=1, stderr `pli80-run: unsupported BDOS function 1`, stdout DISCARDED (audit 2.18) and saved as `.discarded-stdout.bin`, trace still shows the fn-1 call; ASSERT never runs |
| FX-00 | A `--double-run` | PASS with `double_run.equal=true` | two console captures byte-equal (audit 2.20 determinism proof, first executed one) |
| TABLE-00 | B | COMPILE pass (~896 B .REL, measured at hop 2) | `-d` banner code=358 data=30 |
| TABLE-01 | B | COMPILE pass (~1536 B .REL) | code=627 data=50 |
| TABLE-00/01 | B LINK | PASS with `parse_undefined(FULL)==[]` | single-module objects, PLILIB auto-requested from C: (the [C137] trap applies only to unnamed cross-module companions) |
| TABLE-00/01 | B RUN | done-witness (rc=0) — the repo's E2E-32/E2E-15 precedent shows my `.REL` linked by DR LINK-80+PLILIB runs under cpmsim | console anchor `NAME…\r\r\n … \nD>` |
| TABLE-00/01 | B ASSERT | UNKNOWN→ not predictable: this is the FIRST functional assertion ever executed for these programs. Any mismatch stays FAIL/`undefined` (no narrowing without a discriminating run) | complete normalized stream == `reference.py` |
| TABLE00/01.COM | census probe | UNMEASURED hypothesis (audit § 4): pure-PUT needs fn 2 + terminate only. PROPOSED, never assumed | observed call list from `--trace` |

## Honest limits of this registration

- A fixture PASS proves harness + substrate only, never PL/I (L1).
- Lane B running on cpmsim is a historical-compat lane: the `.COM` embeds PLILIB and is NOT
  distributable, never committed (`build/` is ignored working state).
- No COVERAGE/CLAIMS/RUNTIME promotion comes out of step 6 (README § 11; mission brief).
