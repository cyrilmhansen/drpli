# E2E-49/P4 — PLAN (composite CHARACTER FIXED / TEST campaign, OPERATOR-AUTHORIZED 2026-11-01)

Operator authorization covers ALL FOUR panels (A–D), oracle experiments,
evidence-driven compiler changes, integration and documentary closure. The agent
may organize work and manage renewals autonomously. **Never push.** Do not start
P5. Out of scope throughout: STORE, BASED, fixed truthiness, literal-vs-literal,
runtime semantics (byte tier only; NO `spec/RUNTIME.txt` row).

Predecessor boundary: E2E-49/P3 CLOSED at HEAD `b1f72d6` (g87 attested; panel
1150/0, coverage 129/0/0, census 15/0/26/0, ledger ends C347). Evidence:
`spec/lab-evidence/e2e49-p3/RESULTS.md`; laws [C342]–[C347].

## The bank — 24 probes, shared DECL + tail

DECL (`rec.na char(3)`, `rec.nb char(3)`, `rec.s2 char(2)`; `k fixed bin(15)`) and
tail `put list('K=', k);` exactly as in P3, so [C309] fills and [C314] DATA frames
stay comparable with `golden/e49p3`.

- **Panel A — ordered relations with a LITERAL operand (E49G1..G8)**:
  G1 `rec.na < 'ABC'`; G2 `'ABC' < rec.na`; G3 `rec.na > 'AB'`; G4 `'AB' > rec.na`;
  G5 `rec.na <= 'ABCD'`; G6 `'ABCD' <= rec.na`; G7 `rec.na >= 'ABC'`; G8 `'ABC' >= rec.na`.
  Both orientations independently. Open: template choice under the ORDER law,
  positional lengths on LOWERED operands, collapse at 3/3, JNC `d2`/JC `da`,
  possible DR refusal. Competing hypotheses: H-A-sw (measured swap rekeys the
  template: `>`/`<=` swap → member-left becomes direct `21/11`, literal-left
  becomes staged `21/EB/21`; B=first-lowered attr), H-A-or (WRITTEN orientation
  keeps its template; swap would then not transfer), H-A-refuse (dr-refuses).
- **Panel B — BARE spellings in ordered relations (E49H1..H6)**:
  H1 `na < rec.nb`; H2 `rec.na > nb`; H3 `na <= nb`; H4 `nb >= na`; H5 `na > rec.s2`;
  H6 `s2 <= rec.na`. Lean H-B-invis (qual invisible to every measured encoding,
  [C344] transfers): each == its qualified twin byte-for-byte but module-name bytes
  + checksum. Alternatives H-B-gate/H-B-mixed. Compare vs E49F1..F4 goldens.
- **Panel C — unequal-extent relation matrix (E49I1..I6)**, qualified pairs:
  I1 `rec.na < rec.s2`; I2 `rec.s2 < rec.na`; I3 `rec.s2 > rec.na`;
  I4 `rec.na <= rec.s2`; I5 `rec.s2 <= rec.na`; I6 `rec.na >= rec.s2`.
  Completes 4 relations × 2 orientations with F2/F4. Primary: DR accepts and the
  [C346] laws hold → objects EQUAL my arm-c baseline bytes (NO arm). Per-row
  predictions (head 0006, stacked, CODE 67, DATA 000C, fill 001E):
  I1 written 06 03/3E 02 JNC; I2 written 06 02/3E 03 JNC; I3 swapped 06 03/3E 02
  JNC; I4 swapped 06 02/3E 03 JC; I5 swapped 06 03/3E 02 JC; I6 written 06 03/3E 02
  JC. Any deviation falsifies the transfer.
- **Panel D — negated compares (E49J1..J4)**: J1 `^(rec.na = rec.nb)`;
  J2 `^(rec.na < rec.nb)`; J3 `^('ABC' = rec.na)`; J4 `^(rec.na <= rec.s2)`.
  FIRST syntactic acceptance; if accepted, identify the actual lowering —
  H-D-inv (skip byte inverted on the un-negated head: J1≡E49B5 bytes, J3≡E49C4
  bytes, J2 head-written-order skip da, J4 swapped head skip d2), H-D-simpl
  (operator rewritten to the complement — SAME bytes as H-D-inv on these four
  shapes; the convergence is recorded, non-separability stated honestly),
  H-D-extra (extra branch/ORA/CMP bytes — distinguishable), H-D-refuse
  (dr-refuses; then keep refusing, no arm). NO De Morgan assumption.

## Procedure (house method, in order)

1. **Pre-register BEFORE any oracle call**: `spec/lab-evidence/e2e49-p4/mkprobes.py`
   (clone of P3's; names E49G*/H*/I*/J*, comments ≤71 cols, CRLF + `^Z`); generate
   probes into `probes/`; record `BASELINE-MINE.txt` with the ACTUAL binary
   (`eval $(opam env) && cd ocaml && dune build`;
   `./ocaml/_build/default/bin/pli80c.exe probes/E49X.PLI /tmp/out49p4/E49X.REL`;
   accepted rows: bytes via `tools/reldump.py`, never a `.PRN`; refused rows: FIRST
   refusal line, rc of the binary itself); write `HYPOTHESES.md` (per row: primary,
   alternatives, verdict, discriminating byte predictions, falsifiers); **commit all
   of it (probes + mkprobes + HYPOTHESES + BASELINE-MINE) before the oracle** — the
   prediction SHA is proven by `git log --format=%h -- probes/E49G1.PLI | tail -1`.
2. **Oracle**: ONE grouped campaign
   `PLI_SRC=probes python3 oracle/batch.py E49G1 E49G2 E49G3 E49G4 E49G5 E49G6 E49G7 E49G8 E49H1 E49H2 E49H3 E49H4 E49H5 E49H6 E49I1 E49I2 E49I3 E49I4 E49I5 E49I6 E49J1 E49J2 E49J3 E49J4 --tag e49p4 --switches '$L$D'`.
   `golden/e49p4` must NOT exist before the call; never `--reuse`. Classify every
   difference per PROTOCOL #3. Whole-file `cmp` (PROTOCOL #6).
3. **RESULTS.md** §0 lineage / §1 prediction-vs-verdict (every MISS kept verbatim) /
   §2 laws read from `.REL` / §3 what was NOT measured / §4 classification. Commit
   goldens + RESULTS TOGETHER before any compiler change.
4. **Arms** by measured MECHANISM (not panel labels); each arm alone: only measured
   behaviour, whole-file byte verification of new goldens + regression sweep
   (e48/e49 family sweep, E46K14 marker UNMOVED, out-of-scope refusals rc=2, FULL
   gate rc=0), independently committed with evidence cited. Already-byte-exact rows
   need no arm; dr-refuses rows are never implemented.
5. **Consolidation (step 6)**: claims from **C348** derived ONLY from RESULTS §2;
   SPECIMENS round-bank block +24 rows in `tools/e2e_gate.py`; sanctioned
   `python3 tools/e2e_gate.py --update-inventory` (panel expected 1150+accepted but
   the ACTUAL printed number governs — never invent); census re-snapshot per the
   `4b51bc0` recipe (counts UNLESS changed are reprinted by the gate); COVERAGE rows
   (+widenings with labelled SUPERSEDED clauses, quotes byte-checked against the
   pre-edit blob; provenance ids must resolve via `tools/coverage_check.py` — never
   cite legacy [C027]/[C072]; the numeric ORDER law is [C104]); FULL compile-tier
   gate `python3 tools/e2e_gate.py` with **ACTUALS AS PRINTED** recorded.
6. **Close**: archive superseded prose byte-verified vs stated git ranges BEFORE
   replacing (single generation if prose unchanged since pre-registration — verify);
   HANDOFF/PROGRESS/LEARNINGS rewritten, `docs/history/README.md` index row; exactly
   ONE active Next action; `handoff_finalize`; stop. No P5.

## Baseline facts OBSERVED this session by code reading (NOT yet measured runs — successor must produce BASELINE-MINE with the actual binary before the oracle)

- `str_cmp_shape_fix_rel` (`ocaml/lib/codegen.ml:7302`) matches QUALIFIED
  `ImemF/ImemF` ONLY; so Panels A+B are expected to refuse rc=2 at the
  `imem_refuse "comparison"` site (line ~8270+) and Panel C accepts through arm c
  exactly as preregistered above; `lower_test_skip0`'s `Eprefix (NegL, ...)` arm
  (line ~7736) refuses string compares by name → Panel D refuses rc=2.
- Prescan demand twins `is_test_left`/`is_test_right` (`codegen.ml` ~3000–3076)
  currently mirror Eq/Ne literal clauses; if Panel A lowers literal relations, the
  DEMAND twin must widen IN THE SAME COMMIT (one predicate; [C152] invariant).

## Environment facts (verified 2026-11-01)

- HEAD `b1f72d6`; tree clean except the OPERATOR's `handoff.config.json` edit
  (never touch/stage/revert). Checkpoint g87 verified current (prose-hash method of
  `.pi/extensions/context-guard/checkpoint.ts`). Renewal chain: `.pi-guard/
  renewal-state.json` ABSENT → fresh chain, cap/autoRenew per `handoff.config.json`.
- Bootstrap commits: PLAN + HANDOFF Next action + PROGRESS note (this round opens
  IN FLIGHT); pre-registration is the NEXT commit before any oracle call.
- Controlled launch: `env -u CONTEXT_GUARD_AUTO_RENEW PI_CODING_AGENT_DIR=/home/john/.sushi/pi pi`.
- `/handoff verify` freshness = sha256 of the file with managed block(s) stripped and
  trailing whitespace removed (GOAL/LEARNINGS/config hash whole) — reproducible in
  python3; the guard also records it per-session under `.pi-guard/sessions/`.
