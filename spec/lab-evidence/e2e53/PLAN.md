# E2E-53 — Compiler Coverage Expansion — CAMPAIGN PLAN

Operator authorization (2026-11-07 brief): multi-subround campaign; Goal A = move authentic
DR-accepted corpus programs REFUSED -> EXACT with unchanged sources and whole-file byte-exact
`.REL`; Goal B = expand measured language coverage. Report the two dimensions separately.
Intel 8080 only; DR oracle is law; no PLILIB, no MIR, no runtime work; no push.
Durable evidence rules: `PROTOCOL.md` Part 1 (pre-register before oracle; keep falsified
predictions; classify dr-refuses/my-gap/unmeasured; complete-`.REL` byte comparison; ledger
`spec/CLAIMS.md` is authority; never weaken the gate). Renewal/work policy: Part 2.

## 1. Baseline (VERIFIED FIRST-HAND at campaign open, session 01a1b800, 2026-11-07)

HEAD `9ac1775e46460e8b40a1f0614c02906197ddd391` (P3-19 finalize commit; E2E-52/P3 COMPLETE,
LOAN2 whole-file byte-exact CLAIMED at [C377]). Tree clean except the operator
`handoff.config.json` edit (dirty, NEVER staged) and ignored `build/`/`ocaml/_build-*`/
`golden/*/dir.txt` detritus.

| Instrument | Baseline | Verified by |
|---|---:|---|
| Byte-exact specimens | 1,312 | `spec/INVENTORY.txt` recount |
| Classified negatives | 190 | INVENTORY + gate log 190/190 |
| Controlled divergences | 9 | gate log 9/9 DIV-OK |
| Coverage contracts | 145 | gate `coverage_check: 145 rows, 0 errors, 0 warnings` |
| SUPPORTED contracts | 95 | COVERAGE.tsv `Counter`: 93 ACCEPTS/SUPPORTED + 1 ACCEPTS_DEFECT/SUPPORTED = 94 rows col7 SUPPORTED + … (row-status recount agrees with gate-side prose; treat 145/95 as the gate-attested pair) |
| Corpus census | 16 EXACT / 25 REFUSED / 3 NO_ORACLE / 0 DIFFERS | `spec/census/corpus-census.tsv` recount |
| Ledger | ends **C377** (199 `## C` headers; last gate attested 200 incl. banner variant — trust the sequential id: C377) | grep |
| Last full gate | rc=0 `build/gate-e52p19-reg.log` (all numbers hit) | tail read first-hand |
| Compiler | `dune build` rc=0; binary sha256 `baec1f82…` == armed tree fingerprint | direct build |
| Guard chain | fresh chain, renewalsDone 0, cap 12, `workingContextWindow` 145000, checkpoint current | diagnostics + config |

NO_ORACLE programs (no DR object; cannot count toward Goal A): CALL, INVERT, MAININVT.

## 2. Opportunity matrix (fresh audit 2026-11-07; first refusals re-measured DIRECT on `baec1f82`)

| Candidate | DR evidence | Current blocker (verified fresh, rc=2) | Other corpus users | Independent probes needed | Est. complexity |
|---|---|---|---|---|---|
| A1 GET SKIP family | AUTHENTIC `golden/first/EXPR1/EXPR1.REL` code 004A-005A pins bare `get skip;` = `LXI D,0290 / LXI B,<cont> / CALL ?SIOOP / MVI A,01 / CALL ?SKPOP / CALL ?QIOOP` (17 B, bitstream decode this session); variants live in REPORT/DEPREC/COPYLPT goldens | `GET form not in E2E-3e subset [TBD] (line 21)` (EXPR1:21 `get skip;`) | REPORT:33, DEPREC:95 (`get skip(2);`), COPYLPT:23/32/36 (`get skip list(v);`) — all behind OTHER first blockers | 3-4 minimal: bare / counted const / `get skip list(item)` / (variable count if a golden context proves needed) | LOW-MED: one new GET matcher arm + prescan mirror; shared attach/skip/close bytes already implemented on the PUT side (but NEVER reuse PUT bytes by analogy — DR evidence first) |
| A2 ACK/ACKTST PUT families | DECPOLY/RFACT/LOAN2 witnesses cover pieces; the console LIST rep-item and builtin-call item have NO minimal witness | ACK `PUT form not in E2E-3a subset [TBD] (line 12)`; ACKTST `PUT numeric item form unproven [TBD]` | none (only these 2) | several | MED-HIGH — audit found ACK carries >=3 INDEPENDENT blockers: (i) console matcher `all_data` rejects `Pi_rep`; (ii) `decimal(m,4)` as console PUT LIST item refuses (sanity S3); (iii) `returns(fixed) recursive` multi-formal refuses `attributed RECURSIVE multi-formal activation unproven` (sanity T3); more likely behind |
| A3 FSCAN CHARACTER builtins | none for SUBSTR/VERIFY/LENGTH lowering (sweep stage 3-4); SMVVM/SMCCM store laws exist [C317][C326] | `char store from non-literal [TBD]` (`line = substr(...)` store source) | EXPR2, SAMPLE, ANNUITY share builtin/store pieces; console GET EDIT (E46K15 my-gap) also required | many (whole builtin family) | HIGH — suitable only as a sequence of tightly scoped slices |
| A4 EXPR2 FLOAT call-as-expression | FDTEST/FPRINT float-call witnesses exist for ENTRY float; internal `returns(float binary) recursive` zero-formal call as store RHS unsampled | `FLOAT expression shape builtin is unsampled [TBD] (line 35)` (`value = exp();`) | EXPR1 shares it; then console PUT EDIT with FLOAT item + `f(10,4)`; plus %replace, GET EDIT | 2-3 then many behind | MED for first rule, HIGH for program |
| B1 non-2-byte array elements | goldens OPTIMIST/DEPREC/LABELS/MPMCALLA contain real layouts (context-rich); [C159][C164][C172] measured only 2-byte | `[TBD] array of 0-byte elements [C159]` (DEPREC/LABELS/MPMCALLA), `array of 9-byte elements` (OPTIMIST) | 4 programs share the SAME refusal family | ~4-6 (1/3/5/9-byte strides, const vs var subscript, static vs auto, DATA order) | MED-HIGH; highest Goal-A payoff per rule |
| B2 STATIC structure members | [C114][C371][C376] static-cell laws; member case unsampled | MPMCALLB `STATIC on … MEMBER … unsampled`; ENTER behind OPEN KEYED; DIOCALLS behind BASED char-varying | ENTER, MPMCALLB, DIOCALLS | 1-2 | MED |
| B3 CHAR VARYING returns | none | ANNUITY line 21, SAMPLE line 25 deferred; census `DECL.RETURN_VARYING` REFUSED | RETRIEVE too | ABI probe set (return descriptor, temp, lifetime) | MED-HIGH |
| C OPEN ENVIRONMENT / KEYED / UPDATE | P0 measured 34 OPEN blocks in DR sources but NO lowered object for these options | COPY/RETRIEVE `OPEN option ENVIRONMENT`; ENTER/KEYFILE/REPORT `KEYED`; UPDATE `UPDATE` | 6 programs | large record-layout research | HIGH — do NOT start comprehensively; only an independently measurable subset |
| D existing divergences | 9 pinned DIV-OK rows (BASED reevaluation, pointer loops, E40Q4 layout) | pinned, value-correct or shape-pinned | none | per-law discriminating design | HIGH; only with a falsifiable discriminator |

Ranking rubric applied (probability of unlocking programs; reusable forms; existing evidence;
risk; new unknowns): B1 has the highest historical payoff; A1 has the best
evidence-per-risk ratio and its authentic-golden geometry is already decoded.

## 3. P1 decision and reason

**E2E-53/P1 = GET SKIP statement family (A1).** Reasons:
1. Matches the operator default recommendation; the audit found no candidate whose first rule
   is simultaneously (a) pinned by existing authentic DR bytes (EXPR1.REL 004A-005A measured
   this session), (b) contained in ONE statement route, and (c) shared by four corpus programs.
2. Exercises the full campaign workflow (audit -> probe -> golden -> arm -> parity -> census)
   at low regression risk: the shape today refuses loudly; an arm cannot change any accepted
   specimen.
3. ACK/FSCAN/EXPR2 were audited as instructed and are NOT single-obstacle programs
   (sanity T3/S3 above); queueing them behind their true blocker sets instead.
4. B1 (arrays) is the strongest Goal-A candidate and is scheduled as P2 with its own
   pre-registration after P1 closes.

Scope discipline for P1: measure `get skip;`, `get skip(<const>);`, and `get skip list(<item>);`
on the console route; a `<variable>` count only if DR accepts and a golden/pin proves it.
FILE-route GET SKIP is OUT unless evidence crosses it. Never reuse PUT SKIP bytes by analogy.

## 4. Campaign dashboard (cumulative, vs baseline 1,312 specimens / 16 corpus EXACT)

| Slice | Feature family | New exact specimens | Corpus programs advanced | Newly EXACT programs | Claims | Gate |
|---|---|---|---|---|---|---|
| (P1 in flight) | GET SKIP family | 0 | 0 | 0 | - | - |

## 5. Standing constraints (carry into every slice)

- Oracle campaigns: pre-registered PLAN + CRLF/bare-^Z probes committed by explicit paths
  BEFORE any oracle call or `ocaml/lib/` byte; goldens committed VERBATIM before arm.
- Probe/tag ids: E2E-53 uses `E525*`, `E526*`, ... with tags `e53p1`, `e53p2`, ...
  (verified unused at campaign open).
- Verify each accepted probe by whole-file `cmp` on FRESH POSITIONAL output
  (`pli80c.exe IN OUT`, no `-o`); run affected historical programs unchanged; census via
  `python3 tools/corpus_census.py --check` (own write path); REAL `--update-inventory`
  adjudicated by its own output; claims strictly sequential (next id from actual ledger
  state, first ordinary id **C378**) and written BEFORE any `spec/COVERAGE.tsv` touch;
  NEVER `coverage_gen.py`; new row ids registered explicitly in `spec/COVERAGE-IDS.txt`;
  FULL compile-tier gate rc=0 logged to `build/gate-e53pN-reg.log`; negative/divergence
  panels never weakened; unmeasured forms keep refusing with `[TBD]`; no source-name
  special cases.
- Git: explicit staging only, `git diff --cached --stat` before commit, never `git add -A`,
  never clean/reset, `handoff.config.json` never staged, no push.
- Renewal: only at safe boundaries (never mid-oracle/mid-git); never touch renewal-state;
  close the chain at cap via `handoff_finalize`.
