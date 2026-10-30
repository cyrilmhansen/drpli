# History: LEARNINGS.md operational notes superseded by later measurement (classification and provenance preserved)

Baseline commit: `f3a4c608189aabbee018a3b3c025cc0501de0288` (branch `main`, 2026-10-30). Extracted verbatim from the durable files on 2026-10-31 by the Mission-1 consolidation (operator-approved; branch `mission1-docs-consolidation`). Nothing below this line is edited: the excerpts are byte-identical to the named source line ranges at the baseline. They are RECORDS of superseded operational states, not current instructions.


## Excerpt — LEARNINGS.md §1 — 'Proposed (E2E-48/P2c session)', lines 264–269

Superseded: the plan was executed (arms `14c7321`, `3ee414a`, `6545b5d`, `6491981`, `a72ce43`, `18a06c0`, `1e8acb2`, `e21281a`) and the owed gate measured at `f67cc6d` (1109/0, negative 182/182) and `adbfa2a` (1120/0, negative 181/181).

## Proposed (E2E-48/P2c session)

- **The widening plan for the measured laws is written as the exact command-level next action in
  `HANDOFF.md`** (arms in `bit_cond_mat`, the demand twin, the imem gate, the static-varying
  placement, panel registration to 1107). The gate re-run at the post-census-fix HEAD is still
  owed: the 1098/0 figure is recorded at `1595a10`, not at `6130164`. [proposed, unverified]

## Excerpt — LEARNINGS.md §2 — 'Tune generationReserve' bullet, lines 283–287

Superseded by operator configuration: reserve values are whatever `handoff.config.json` carries — read it and `/guard status`; this file quotes no numbers. (Original text quotes generationReserve: 20000.)

- **Tune `generationReserve` before trusting the levels.** `20000` is an initial policy number;
  the production model measures `contextWindow=220000`, `maxTokens=65536` (observed via
  `/guard status`), so the reserve is 9.1 % of the window and usable remaining starts at
  ~199 900. Read that again on whichever model a session actually uses, then decide. A reserve is
  a policy budget, not an output cap.

## Excerpt — LEARNINGS.md §3 — 'State owed by the successor' bullet, lines 421–423

Superseded by measurement: `--update-inventory` and the FULL gate ran — `f67cc6d` 1109/0, 182/182; expectations corrected and re-measured at `adbfa2a` (1120/0, 181/181).

- **State owed by the successor (unverified, do not claim):** `--update-inventory` and the
  FULL gate have NOT been run since the arms; expected 1109 byte-exact / 0 fail,
  negative 182/182 (the inherited 1107/184 is falsified by the K1/K3 promotions).

## Excerpt — LEARNINGS.md §4 — 'proposed (not yet done): claims C321-C326' bullet, lines 464–467

Superseded by execution: claims C321–C326 committed `aa4b5b4`; all six arms landed `6545b5d`…`e21281a`; registration/gate `adbfa2a`.

- **proposed** (not yet done): claims C321-C326 drafted from RESULTS s2; arms (a) empty-varying
  initial, (b) TITLE static-varying + E46F5 promotion, (c) static-FIXED store ?SMCCM with its
  prescan demand twin (fa09b97 rule), (d) store-ladder DCX 2/3, (e) non-final bit item,
  (f) TEST member-as-RIGHT SCCVM.
