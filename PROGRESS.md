# PROGRESS.md — DRPLi

Manual prose wins over the managed block below it. Do not hand-edit the managed block.
This file tracks *working state*; compiler behaviour itself belongs to `spec/CLAIMS.md`.

## Current phase — **E2E-52/P3 IN FLIGHT** (2026-11-04; operator brief: LOAN2 progressive
closure — compile `artefacts/LOAN2.PLI` toward whole-file byte-exactness by repeated
blocker→evidence→fix cycles; multi-subround campaign; renewals autonomous at safe
boundaries; no push; preserve operator `handoff.config.json` (dirty, never staged)).

**Baseline VERIFIED this session:** HEAD `6c44d8d` (P2 close + guard finalize g276,
attested); tree clean except the operator config edit; `dune build` rc=0, compiler
`85bf7a26…` (same binary as the P2 registration gate); `artefacts/LOAN2.PLI` sha
`7be23ba3…` (unchanged, last touched Phase 0); golden `golden/first/LOAN2/LOAN2.REL`
sha `712cfcb2…` untouched; ledger ends C358; 181 claims.

**Subround P3-1 (PUT FILE bare PAGE) — evidence complete, implementation OWED.** LOAN2
blocker reproduced VERBATIM: `codegen: PUT FILE with a bare PAGE control item [TBD] (line
99)`. **KEY FACT: the raise comes from the E2E-52/P1 lexical PRESCAN (`prescan_stmt`
calls `match_put_list_lit` → `bare_ctl_put` for EVERY Sput BEFORE lowering), not from
`lower_stmt`** — which is why LOAN2's PRINT/PAGESIZE OPENs at lines 54/56 (rejected by
`open_mode_word`, `open_subset_keys` = FILE/INPUT/STREAM/OUTPUT/TITLE) do NOT surface:
the prescan dies at 99 first. After PAGE lands, LOAN2's blocker will move — the next
verified blocker is expected to be the PRINT/PAGESIZE opens at 54/56 unless an earlier
prescan refusal intervenes. Evidence: DR golden `golden/e42p2c/E46N10/E46N10.REL`
(384 B, CODE 0x3E=62, DATA 0x0A=10) pins the statement at 0023-0034 = `LXI H,*C(common
0) / LXI D,0652 / LXI B,*CODE(0035) / CALL ?SIOOP / CALL ?PAGOP / CALL ?QIOOP` with
LINK-CHAIN-EXT ?SIOOP@002D, ?PAGOP@0030, ?QIOOP@0033; continuation word 0x35 = CLOSE.
COPYLPT:53 (`put file(printfile) page;` inside an ON ENDFILE unit) carries the SAME 18
bytes behind a PRINT open (0215-00226 per probe record, predict_p2c self-test
`COPYLPT:53 = 18`). PAGE **with a count** and PAGE+items are UNMEASURED (manual
syntax permits, no object) — they must keep refusing BY NAME; LINE stays dr-refuses
(E46N21, marker `control item LINE with a count, unmeasured on the named-file route
[TBD] (line 12)` must survive any message edit); console `put page;` stays refused
(N3_PAGE negative, my-gap, marker `PUT form`). ?PAGOP appears in NO claim id —
`grep -in pagop spec/CLAIMS.md` is EMPTY; the 18-byte law lives in
e2e42-p2c/RESULTS §4 + COVERAGE row `FILE.PUT_PAGE` (line 60, currently REFUSED/NONE).
Registration plan follows the E46K1/E46K3 RETIRE precedent: move `E46N10` from REJECTS
(`tools/e2e_gate.py:4477`, marker `bare PAGE control item [TBD] (line 11)`) + delete its
NEG_META (4054) into SPECIMENS (e42p2c block ~line 1280), `--update-inventory`
1196→1197, gate AGAIN, census re-snapshot via `corpus_census.py --check` (COPYLPT and
LOAN2 census msgs WILL move), COVERAGE `FILE.PUT_PAGE` → SUPPORTED + EXACT:1, new claim
C359 derived ONLY from the existing measured evidence.

## Next action (E2E-52/P3-15 hop 2 — P3-14 CLOSED `a72fd2e3`; PRE-AUDIT LANDED; PRE-REGISTRATION OWED; read `LEARNINGS.md` § "P3-15 hop 1" SUCCESSOR CONTRACT FIRST)

**EXECUTE NOW (successor): P3-15 hop 2 = PRE-REGISTER, then campaign+arm+validate+register+close per `LEARNINGS.md` § "P3-15 hop 1" steps (1)–(5) EXACTLY:** (1) write PLAN §P3-15 (§1 blocker VERBATIM line-147; §2 witnesses = authentic LOAN2.REL display body `0674–0732` FULLY decoded first-hand this session — FORMAL item `2A 42 03+2i / 3E 0A / ?DLDOP / 3E 0D / 06 02 / ?QDCOP / ?EDTOV`, literal `|` chains `21 EC 01 / 3E 01 / ?SLCTS / ?EDTOV`, attach `LXI H,*C(common0)/LXI D,0652 INLINE/LXI B code@0732 (RELOC)/?SIOOP/?EDITF`; P086K `0022–003A` shows the variable prep `LXI H,*A(cell)` differs ONLY by that one instruction; guard = `authorize_file_edit_item` ~codegen.ml 12533 `st.deref` BY-NAME refusal whose reason clause is FALSE-AS-WRITTEN vs the corpus; H-A..H-D + falsifiers, `$`-picture format record at `data@0015..` decode FIRST-HAND BEFORE predictions, never fit) + probes `probes/E521{A..D}.PLI` (CRLF+bare-`^Z`, ≤71 cols, ONE dcl/line, headers `procedure;`/`procedure(x,y);` — hop-1 probe law; arity≥2 `fixed dec(10,2)` block-copy callee, `open file (output) print;`, continuation statement after every put, non-formal control twin) + commit by EXPLICIT paths BEFORE any oracle call or `ocaml/` byte. (2) ONE campaign `PLI_SRC=probes timeout 900 python3 oracle/batch.py E521A E521B E521C E521D --tag e52p15 --switches '$L$D'` rc DIRECT, goldens VERBATIM first. (3) arm ONLY measured shapes (expected: admit deref scalar RTdec formal with LHLD prep in `authorize_file_edit_item`; everything else keeps VERBATIM BY-NAME refusals; histogram 68/124; cmp FRESH POSITIONAL; sweep count-moves-with-inventory FAILS 0; markers; DEC 64/0; **FULL GATE BEFORE CLOSE** → `build/gate-e52p15-reg.log`). (4) LOAN2 UNMODIFIED → ACTUAL blocker VERBATIM NEVER fix. (5) register from **1300/187**; census OWN path 15/0/26/0; **C373 measured-bytes-only BEFORE ANY COVERAGE touch**; coverage EXTEND-or-justified-NEW row + SAME-change IDS (NEVER coverage_gen.py; 15 cols; manual_ref `pNN[:§X.Y][=phrase]`|`NONE:`); gate AGAIN; RESULTS §P3-15 + PLAN §5 row INSIDE table **anchored by LINE NUMBER with the 7-unescaped-pipes check (NEW lesson)** + §P3-15 CLOSED; then P3-16 ACTUAL blocker, marathon through P3-19 (slice 6 of ≤8).

**STATE at this checkpoint:** HEAD = this durables commit after `a72fd2e3`; armed binary sha256 `b88e7b023027e2eeba1b6f49dc0815cb25e14f20269074a637a7c1f84f3c72e2` == tree (build rc=0 re-held); ledger ENDS **C372** (195 headers); inventory **1300/187**; coverage **145 rows 0/0 SUPPORTED 95**; LAST full gate rc=0 **`build/gate-e52p14-reg.log`** (1300/0, 187/187, 9/9, 145 rows, census 15/0/26/0, prose 5 — every number hit); **P3-14 CLOSED `a72fd2e3`**; E521*/`e52p15` names VERIFIED UNUSED; LOAN2 UNMODIFIED sha `7be23ba3…` rc=2 NO `.REL` line-147 blocker VERBATIM (`PUT FILE(OUTPUT) EDIT of the FORMAL A … (line 147)`) NEVER fix; EXPR1 GET-21/EXPR2 FLOAT-35; goldens NEVER re-derived; config NEVER staged; no push; rc DIRECT; POSITIONAL FRESH paths (`pli80c IN OUT` — NO `-o`); `eval "$(opam env)"` every shell; never glue `rm`; never parallelize dependent bash calls; byte-tier; NEW LESSON this hop: escape raw `|` in §5-table prose (`\|`) and pipe-count-check the row (7 unescaped pipes) before committing; chain 01a1b2d5 renewal 4/12 used, cap 12.

SUPERSEDED-BY-ABOVE: ## Next action (E2E-52/P3-14 hop 4 — (6) C372 `5aae7109` + (7) NEW coverage row `f2513593` LANDED; GATE → RESULTS → PLAN §5 → CLOSED OWED; read `LEARNINGS.md` § "P3-14 hop 4" FIRST)

**EXECUTE NOW (successor) — P3-14 CLOSE-OUT ONLY, then P3-15 (slice 5 of ≤8; marathon through P3-19):**
(8a) FULL gate rc=0 **DIRECT, synchronous, redirected, NEVER pipeline-tail** → `python3 tools/e2e_gate.py > build/gate-e52p14-reg.log 2>&1; echo RC=$?` from the repo root, expect **1300/0 byte panel, 187/187 negatives, 9/9 divergences, coverage 145 rows 0/0 SUPPORTED 95, census 15/0/26/0, prose 5**. Nothing in `ocaml/` changed since the hop-3 sweep 178/0, so no re-sweep is owed unless the tree moves. ONLY the gate runs the negative panel (hop-11/12 lesson).
(8b) RESULTS **§P3-14** in `spec/lab-evidence/e2e52-p3/RESULTS.md`: parity table for the 4 accepted probes (sizes 256/256/384/256, code 50/50/81/62, data 0/0/0/2, `cmp` rc=0) + the `E520E` dr-refuses row; **H-2 packed-name-record 3-byte near-miss kept VERBATIM** (predicted one char byte, measured 3 file bytes at 0-based 6/19/28 inside PROG-NAME/EXTDEF/DEF-PUBLIC, CODE+DATA identical); probe-defect + corrective-campaign `e52p14b` provenance (PLAN §4b); LOAN2 **121→147 VERBATIM never-fix**; byte-tier-only NOT-say.
(8c) PLAN §5 progress row **INSIDE the table** immediately after the P3-13 row — anchor by LINE NUMBER (`grep -n` the §5 table, hop-12 lesson) — and change the `## …§P3-14` heading to **CLOSED**; `python3 tools/file_prose_check.py` rc=0; commit explicit paths, ALWAYS `git diff --cached --stat`, `handoff.config.json` NEVER staged.
(9) **P3-15** on the ACTUAL line-147 blocker `codegen: PUT FILE(OUTPUT) EDIT of the FORMAL A has no byte-exact DR witness [TBD] (line 147)` = `put file (output) edit ('|',a,…) (…,p'$zz,zzz,zz9v.99',a);` in `display`: evidence-first, **ZERO-oracle pre-audit** of `golden/first/LOAN2/LOAN2.REL` `053F-0542` (the DEC-variable EDIT route) and the `E52PF` picture/REPSPEC precedents **BEFORE any probe**; verify probe names + tag unused (`grep -n "E521" spec/INVENTORY.txt`, tag `e52p15`); pre-register PLAN §P3-15 + probes + LEARNINGS § by EXPLICIT paths BEFORE any oracle call or `ocaml/` byte; NEVER predict the next blocker.

**STATE at this checkpoint:** HEAD = `f2513593` + this durables commit; armed binary sha256 `b88e7b023027e2eeba1b6f49dc0815cb25e14f20269074a637a7c1f84f3c72e2` == tree (build rc=0 re-held this session); ledger ENDS **C372** (195 headers, prose clean); coverage **145 rows 0/0 SUPPORTED 95** (`PROC.CALL_TARGET_DESIGNATOR` NEW row + IDS line, row 85 `PROC.CALL_COPYIN` left UNBUMPED by adjudication); inventory **1300/187**; census 15/0/26/0 with the LOAN2 line-147 msg VERBATIM, source sha `7be23ba3…` UNMODIFIED; sweep post-reg 178/0, markers 14/14, DEC 64/0, divcheck 9/9; cmp 4/4 rc=0 re-held FRESH POSITIONAL `build/p3-14c/arm-out/`; LAST full gate rc=0 still `build/gate-e52p13-reg.log` (**the P3-14 gate is OWED**); goldens NEVER re-derived; config NEVER staged; no push; rc DIRECT; never glue `rm`; POSITIONAL FRESH paths (`pli80c IN.PLI OUT.REL` — NO `-o`); `eval "$(opam env)"` every shell; never parallelize dependent bash calls; chain `01a1b2d5` renewal 3/12 used, cap 12.

SUPERSEDED-BY-ABOVE: ## Next action (E2E-52/P3-14 hop 3 — ARM + VALIDATION + REGISTRATION LANDED `65da9bd1`/`9a31509c`; C372 → COVERAGE → GATE → CLOSE OWED; read `LEARNINGS.md` § "P3-14 hop 3" SUCCESSOR CONTRACT FIRST)

**EXECUTE NOW (successor): complete P3-14 per `LEARNINGS.md` § "P3-14 hop 3" steps (6)–(9) EXACTLY: C372 measured-bytes-only BEFORE ANY COVERAGE touch (bullets: shadow-name CALL-statement law = plain-designator target reaches [C123]/[C124] unchanged; E520D static own-cell descriptor on the shadow; packed-name-record 3-byte law; bare-stmt dr-refuses boundary; BY-NAME perimeter); coverage EXTEND `PROC.CALL_COPYIN` (row 85) preferred — adjudicate whether E520A..D fit the row's law before bumping EXACT counts, else justified NEW row with SAME-change COVERAGE-IDS line (NEVER coverage_gen.py; 15 cols FIRST NON-COMMENT row; delimiter tab; manual_ref `pNN[:§X.Y][=phrase]`|`NONE:`); coverage_check + prose rc=0 (expect 144 rows unchanged if extension; SUPPORTED 94); FULL gate rc=0 DIRECT → build/gate-e52p14-reg.log (expect 1300/0, 187/187, 9/9, census 15/0/26/0, prose 5) — ONLY the gate runs the negative panel; sweep AGAIN post-registration (expect 178/0 — E520A..D are E52-prefixed inventory rows; FAILS 0 binding); RESULTS §P3-14 (parity table; H-2 packed-name-record 3-byte near-miss VERBATIM; probe-defect + e52p14b corrective-campaign provenance; LOAN2 121→147 VERBATIM never-fix; byte-tier) + PLAN §5 row INSIDE the table anchored by LINE NUMBER (hop-12 lesson) + §P3-14 CLOSED; then P3-15 on the ACTUAL line-147 blocker (`PUT FILE(OUTPUT) EDIT of the FORMAL A` — evidence-first, ZERO oracle pre-audit of LOAN2.REL 053F-0542/E52PF precedents BEFORE any probe; NEVER fix in P3-14); marathon through P3-19 (slice 4 of ≤8).

**STATE at this checkpoint: HEAD = `9a31509c` + this durables commit; ARMED binary sha256 `b88e7b023027e2eeba1b6f49dc0815cb25e14f20269074a637a7c1f84f3c72e2` == tree (default `_build` AND fresh `_build-p314b` agree; deterministic; histogram codegen 68/total 124 == baseline EXACTLY); cmp E520A/B/C/D whole-file rc=0 4/4 FRESH POSITIONAL `build/p3-14b/arm-out/`; E520E rc=2 BY NAME guard VERBATIM; sweep 174/0 PRE-registration (178 owed post-reg), markers 14/14 + E520E marker re-measured rc=2 CRLF+bare-^Z, DEC 64/0, divcheck 9/9; inventory 1300/187 EXACT; census OWN path rc=0 counts 15/0/26/0, LOAN2 msg MOVED VERBATIM to Line-147 blocker (`PUT FILE(OUTPUT) EDIT of the FORMAL A …(line 147)`), NOTHING fixed, source sha 7be23ba3… unchanged; ledger ENDS C371 (C372 owed); coverage 144/94 0/0; last full gate rc=0 build/gate-e52p13-reg.log (P3-14 gate owed); goldens NEVER re-derived; config NEVER staged; no push; rc DIRECT; never glue `rm`; POSITIONAL FRESH paths; `eval "$(opam env)"` every shell; chain 01a1b2d5 renewal 2/12 used, cap 12; NEW TOOL LESSON this hop: never parallelize bash calls when a later command depends on a directory an earlier command creates (a race gave a FALSE compile rc=2 Sys_error on E520D before the arm even ran — sequential re-run proved rc=0 cmp rc=0).**

SUPERSEDED-BY-ABOVE: **EXECUTE NOW (successor): complete P3-14 per `LEARNINGS.md` § "P3-14 hop 2" SUCCESSOR CONTRACT steps (1)–(9) EXACTLY: arm parser.ml CALL arm as PLAIN identifier + suffix_chain (NEVER builtins; bare-stmt arm and codegen guard UNCHANGED — E520E proves DR REFUSES bare `summary();` so the BY-NAME boundary is MEASURED, keep it); build fresh `_build-p314b` rc=0 DIRECT + histogram 68/124; cmp E520A/B/C/D vs `golden/e52p14b/` + `golden/e52p14/E520D` FRESH POSITIONAL (E520A already cmp rc=0 vs my control); sweep (count moves with INVENTORY, FAILS 0), markers, DEC 64/0, divcheck 9/9, FULL GATE BEFORE CLOSE; LOAN2 UNMODIFIED → ACTUAL next blocker VERBATIM NEVER fix; register from 1296/186 (+4 SPECIMENS E520A..D, E520E → REJECTS dr-refuses VERBATIM `SYNTAX ?` line 14 both passes, expect 1300/187); C372 measured-bytes-only BEFORE COVERAGE; EXTEND PROC.CALL_COPYIN preferred (NEVER coverage_gen.py); gate rc=0 → build/gate-e52p14-reg.log; RESULTS §P3-14 (H-2 packed-name-record 3-byte near-miss kept VERBATIM; probe-defect + e52p14b corrective-campaign provenance) + PLAN §5 row by LINE NUMBER + CLOSED; then P3-15 actual blocker, marathon through P3-19 (slice 4 of ≤8).** Evidence this hop: `9d4c3a75` pre-registration BEFORE any oracle byte; `1afc3bd3` campaign e52p14 VERBATIM; `a4d10f1a` dated PLAN §4b probe-defect; `9ece9a69` corrective e52p14b VERBATIM. STATE: HEAD = this durables commit; ledger ENDS C371; inventory 1296/186; coverage 144/94; last full gate rc=0 build/gate-e52p13-reg.log; binary `6db44394db5f09ad82cdb8e05f8fc92b298f77305301870de09e2485764bdfd2` == tree (UNARMED); goldens NEVER re-derived; config NEVER staged; no push; rc DIRECT; byte-tier; `eval "$(opam env)"` every shell; POSITIONAL FRESH paths; chain 01a1b2d5 renewal 2/12 used after this.

SUPERSEDED-BY-ABOVE: **EXECUTE NOW (successor): complete P3-14 per `LEARNINGS.md` § "P3-14 hop 1" SUCCESSOR CONTRACT steps (0)–(7) EXACTLY.** ROOT CAUSE ACCEPTED FIRST-HAND (ZERO oracle): parser.ml `builtins` contains "SUMMARY"; `primary` captures a builtin key followed by `(` into `Ebuilt("SUMMARY",[])` and codegen's `Sprocedure_stmt` classifier (~14695) accepts ONLY `Eident`/`Esuffix` heads → Line-121 BY-NAME refusal. Everything else already works: non-shadow `call foo();` forward arity-0 AND two-site chains compile rc=0 ([C123]/[C124] armed); authentic LOAN2.REL chain walk CONFIRMS DR geometry = plain zero-arg CALLs, summary chain head 066F→0621, linker-fills LC@entry 0733. PROPOSED narrow arm (oracle-CONFIRM FIRST): CALL-arm parses target as plain identifier, never consulting builtins; bare-statement `summary();` stays refused unless E520E measures DR acceptance. Write PLAN §P3-14 + probes E520A..E520E (verified unused) + sanity predictions from `build/p3-14/prevA.REL` dumps; commit EXPLICIT paths BEFORE any oracle call/`ocaml/` byte; ONE campaign e52p14; goldens VERBATIM first; arm measured shapes ONLY; validation incl. **FULL GATE BEFORE CLOSE**; register from 1296/186; C372 measured-bytes-only BEFORE COVERAGE; coverage EXTEND-preferred; gate rc=0 → `build/gate-e52p14-reg.log`; RESULTS + PLAN §5 row (anchor by line number) + CLOSED; LOAN2 next ACTUAL blocker VERBATIM NEVER fix (strongest candidate per reconnaissance: line 160 `call current_year(IP-YIN)` DEC-SUB actual — P3-13 armed Mul+literals ONLY; NEVER predict); marathon through P3-19 (slice 4 of ≤8). STATE verified this session: HEAD durables; binary `6db44394db5f09ad82cdb8e05f8fc92b298f77305301870de09e2485764bdfd2` == tree (`ocaml/_build-p314`); ledger ENDS C371; inventory 1296/186; coverage 144/94; gate rc=0 `build/gate-e52p13-reg.log`; LOAN2 sha `7be23ba3…` rc=2 line-121 VERBATIM; goldens NEVER touched; config NEVER staged; NEW renewal chain live (operator archived exhausted state).

SUPERSEDED-BY-ABOVE: **EXECUTE NOW (successor): P3-14 on the LOAN2 Line-121 blocker `call summary();` — full contract = `LEARNINGS.md` § "P3-13 hop 12" (E), exact order:** (1) WHY first-hand, ZERO oracle — the guard text claims only `CALL id`/`CALL id(args)`/bare `id;` are lowered yet `summary` IS a simple name; grep `CALL target is not a simple procedure name` in ocaml/lib/codegen.ml, read the call-site classification, inspect what Line-121 hits TODAY (likely zero-arg internal-procedure cs/entry bookkeeping or empty-paren `()` vs bare-name), audit EXISTING arity-0 witnesses in KEPT goldens/claims BEFORE proposing; classify accepted/proposed/falsified. (2) Verify probe names + tag unused (E520A.. or next free; grep E520/e52p14). (3) Write PLAN §P3-14 (template §P3-13) + probes (CRLF+bare-^Z, ≤71 cols, ONE dcl/line, first-line label, continuation statement) + LEARNINGS § hop; commit EXPLICIT paths BEFORE any oracle call/`ocaml/` byte; ZERO-oracle sanity on 6db44394… to pin my-side behaviour. (4) ONE campaign `cd /home/john/projects/sushiworks/pli80 && PLI_SRC=probes timeout 900 python3 oracle/batch.py <names> --tag e52p14 --switches '$L$D'` rc DIRECT; read EVERY .PRN; decode into build/p3-14/; goldens VERBATIM before any ocaml/ byte; arm measured shapes ONLY; validation (build rc-0-DIRECT, histogram 68/124, cmp FRESH POSITIONAL, sweep — COUNT MOVES WITH INVENTORY, FAILS 0 binding — markers, DEC regressions 64/0, divcheck 9/9, **FULL GATE BEFORE CLOSE** — hop-11/12 lesson: only the gate runs the negative panel); LOAN2 UNMODIFIED → ACTUAL next blocker VERBATIM NEVER fix; register from 1296/186; C372 measured-bytes-only BEFORE ANY COVERAGE touch; coverage row/extension (SAME-change IDS line if NEW row; NEVER coverage_gen.py; 15 cols FIRST NON-COMMENT row); gate rc=0 DIRECT → build/gate-e52p14-reg.log; RESULTS §P3-14 + PLAN §5 row + CLOSED; marathon through P3-19. STATE at this close (ALL ACCEPTED/VERIFIED THIS SESSION): **P3-13 CLOSED**; HEAD = this durables commit; ledger ENDS **C371** (dated N52→NG39 addendum inside, `016e58e0`); inventory **1296/186**; coverage **144 rows 0/0 SUPPORTED 94** (PROC.CALL_DEC_ACTUALS EXACT:8 incl NG39); LAST FULL GATE rc=0 **build/gate-e52p13-reg.log** (1296/0, 186/186, 9/9, 144 rows, census 15/0/26/0, prose 5); armed binary sha256 **6db44394db5f09ad82cdb8e05f8fc92b298f77305301870de09e2485764bdfd2** == tree (build rc=0 re-held); markers 14/14 FAILS 0; DEC 64/0; divcheck 9/9; goldens NEVER re-derived; probes/NG39.PLI sha de1e56e8… cmp rc=0 vs KEPT golden sha 3197de7a… (retirement re-measured first-hand); LOAN2 UNMODIFIED sha 7be23ba3… rc=2 NO .REL Line-121 blocker VERBATIM (`call summary();`) NEVER fix; EXPR1 GET-21/EXPR2 FLOAT-35; `pli80c` POSITIONAL FRESH paths; ALWAYS `git diff --cached --stat`; config NEVER staged; no push; rc DIRECT; never glue `rm`; byte-tier only; `eval "$(opam env)"` every shell; **CHAIN 01a1b1b4 EXHAUSTED AT CAP 12/12 — renewal NOT available to this session; it closes via handoff_finalize; a NEW chain needs the operator to archive+reset ignored .pi-guard/renewal-state.json.**

SUPERSEDED-BY-ABOVE: 

SUPERSEDED-BY-ABOVE: **EXECUTE NOW (successor): follow `LEARNINGS.md` § "P3-13 hop 9" STILL OWED (1)–(7) EXACTLY.** STATE verified: armed binary sha256 **`6db44394db5f09ad82cdb8e05f8fc92b298f77305301870de09e2485764bdfd2`** (deterministic, histogram codegen 68/total 124 == baseline via FULL fresh `--build-dir`); E52ZA..ZF **6/6 whole-file cmp rc=0** (`build/p3-13/arm-out2/`); sweep **168 byte-exact/FAILS 0** (contract's 159 was STALE — INVENTORY rows moved; re-check post-registration); DEC regressions 64/0; divcheck 9/9; **`probes/NG18.PLI`** (sha `20006b0c…`) cmp rc=0 vs KEPT golden → N33→NG18 retirement PROVEN (delete REJECTS ~2734 + NEG_META ~3812 rows, add SPECIMENS NG18, refusals 188→187). Repairs landed `9b81ed0`: const_cells DEC demand `dec_pool_bytes pf` + deref-DEC PUT LHLD route (both measured, goldens-only adjudication). LOAN2 UNMODIFIED rc=2 NO `.REL`, ACTUAL blocker VERBATIM `codegen: CALL target is not a simple procedure name [TBD] (only `CALL id` / `CALL id(args)` / bare `id;` have a DR lowering sampled; line 121)` — PAST 117, NEVER fix; P3-14 target = line 121 `call summary();` (investigate WHY first-hand before pre-registering). Then register from **1288/188** (+6 ZA..ZF + NG18 → expect 1295/187), census OWN path (LOAN2 msg MOVES VERBATIM, counts 15/0/26/0), **C371 measured-bytes-only BEFORE ANY COVERAGE touch + DATED correction of BOTH C093 errors** (false DECPOLY `*A(005A)=5.67`; 2-byte width → 5 B formal-width `00 01 00 00 00`), coverage row/extension (SAME-change IDS line; NEVER coverage_gen.py; 15 cols FIRST NON-COMMENT row; manual_ref `pNN[:§X.Y][=phrase]`|`NONE:`; coverage_check adjudicates 143→144), FULL gate rc=0 DIRECT → `build/gate-e52p13-reg.log`, RESULTS §P3-13 + PLAN §5 row + §P3-13 **CLOSED**; marathon through P3-19.

SUPERSEDED-BY-ABOVE: **EXECUTE NOW (successor): read `LEARNINGS.md` § "P3-13 hop 8 PART LANDED" FIRST and follow its steps (0)–(7) EXACTLY. STATE: ARM EDITS ALREADY APPLIED (UNCOMMITTED at hop-8 close — commit them first, explicit paths ocaml/lib/bind.ml ocaml/lib/codegen.ml) — bind gained `cs_dec` sizing authority (DEC expression temps sized bytes_of callee RTdec row, array-named/recursive/external excluded); codegen admits ONLY the measured literal (`dec_pool` pre-scaled formal-width cell, ZERO code) and Mul-of-two-plain-DEC-autos product (armed `dec_push` route + `!dec_actual_mat` hook terminating DSTOP A=pf into the formal-width temp); Line-N BY-NAME refusal VERBATIM otherwise; `dec_pool` MOVED before lower_hl. Default build rc=0 binary `26ed7ccf54e6bf77…`, but NEW Warnings 9 (missing-record-field — find other call_site constructions) + 39 (unused-rec) MUST be repaired to histogram codegen 68/total 124 == baseline FIRST (full fresh `--build-dir` build; `eval "$(opam env)"` every shell). Then cmp ZA..ZF FRESH POSITIONAL, sweep 159/0, markers + honest N33→NG18 retirement iff cmp rc=0 golden KEPT, DEC 64/0, divcheck 9/9, LOAN2 never-predict, register from 1288/188, C371 measured-bytes-only + DATED both-errors C093 correction, coverage extension, gate rc=0 → build/gate-e52p13-reg.log, RESULTS §P3-13 + PLAN §5 row + CLOSED; marathon through P3-19.**

SUPERSEDED-BY-ABOVE: **DONE hop 8 (session 01a1b225, renewal 8/12; ZERO oracle; ZERO `ocaml/` byte; goldens NEVER touched; config NEVER staged; no push; rc DIRECT; byte-tier):** g456 blocks VERBATIM `afff5e0`; build rc=0 binary `6a4c6c1154a0acd8403b…`==tree. First-hand code anatomy resolved the two open design questions: (1) `dec_pool`/`dec_push` are NOT in scope inside `lower_hl` (chain ends 5723; dpush↔lower_hl mutual) → MOVE `dec_pool` verbatim after `vk_dec_at` @3860 + ONE `dec_actual_mat` ref slot installed immediately after `dec_push`; (2) bind sizing authority — add `cs_dec : bool list` to call_site (internal non-recursive non-attr callee AND scalar RTdec formal), move `callee`/`callee_arrs` above `temps`, size DEC expression temps `bytes_of (RTdec(pf,sf))`, codegen zip3→zip4 and gates BOTH new guard arms (`Ast.Enumber _`, `Ast.Ebinary (Ast.Mul, plain-dec-auto, plain-dec-auto)`) on `decact`; array-named formal shares the RTdec ROW so the exclusion is MANDATORY. Full edit list (bind i–v, codegen a–g), histogram method, validation suite, N33→NG18 retirement rule, registration/C371/coverage/gate/close steps: `LEARNINGS.md` § "P3-13 hop 8" — EXECUTE (1)–(7) there EXACTLY.

SUPERSEDED-BY-ABOVE: **EXECUTE NOW (successor — FULL contract = `LEARNINGS.md` § "P3-13 hop 7 PART LANDED", read FIRST):**

**DONE hop 6 (this session, renewal 6/12; ZERO oracle; goldens NEVER touched; config NEVER staged; no push; rc DIRECT; byte-tier):** step (0) COMPLETE — g450 blocks already at `f281500`; e52p12 `summary.txt`+`transcript-batch0/1/2.txt` committed VERBATIM additive `ed8f1a8` (staged-set = 4 files only). First-hand re-verification ACCEPTED (raw DATA/code reloc records): **NG18 DEC-literal pool cell is 5 B formal-width `00 01 00 00 00`** (pre-scaled per [C084] R505; predecessor "2-byte" FALSIFIED — C371 correction must fix BOTH C093 errors: DECPOLY `*A(005A)=5.67` false citation AND the 2-byte width); LOAN2 product block = **32 B** at 055D/057D/059D/05BD/05DD; vector 031A-0323 static LE address constants → 6 B temps; existing [C358] copyin emission ALREADY equals the LOAN2 temp-materialiser shape (`LXI H,*A(src)/MVI A,ap/?DLDOP; LXI H,*A(t)/MVI A,pf/?DSTOP`); put-skip tail + QDCOP width=p+3/scale B pinned from YD reldump; `E52Z*` names + tag `e52p13` UNUSED; N33 marker substring `FIXED DECIMAL formal is unproven`; retirement iff armed cmp rc=0 vs KEPT golden.
**DONE this session (renewal 7/12; config NEVER staged; no push; rc DIRECT; byte-tier):** g453 blocks VERBATIM `996038b`; build rc=0 binary `6a4c6c1154a0acd8403b…`==tree; step (5) PRE-REGISTRATION `7503552` (PLAN §P3-13 §1–§7 + `probes/E52Z{A..F}.PLI` CRLF+bare-`^Z` per the hop-5 panel; ZERO-oracle sanity: all six rc=2 at the Line-N guard VERBATIM, NO `.REL`); step (6) campaign e52p13 rc=0 **6 ok/6**, every `.PRN` `NO ERROR(S)` both passes; decodes `build/p3-13/{zsizes,E52ZA-disasm,E52ZF-disasm}.txt` + inline data-reloc dumps: **H-1..H-8 ALL CONFIRMED, ZERO falsifiers fired** (ZA down d=03 QDDSR between DMUOP and temp store, DSTOP A=0A; ZB UP d=02 QDDSL ACCEPTED, 4 B temp — direction from SCALES only, width = formal width; ZC/ZD literal cells `50 01 00 00 00`/`00 01 00 00 00` ZERO caller code, static relocs; ZE interleaved vector var/temp/literal; ZF LOAN2 five-block replication verbatim, `MVI C,0A` prologue, `LHLD 004F` read); goldens+summary+transcripts VERBATIM `6267faf` BEFORE any `ocaml/` byte.
**EXECUTE NOW (successor — FULL contract = `LEARNINGS.md` § "P3-13 hop 7 PART LANDED", read FIRST):** (1) ARM per the pinned contract — ONLY the measured shapes at the DEC-formal guard (~4748–4810) and target-selection (~4822–4861) sites: literal actual → pre-scaled formal-width `dec_pool` cell + descriptor static RELOC, ZERO code; product-of-two-plain-DEC-autos actual → existing expression machinery terminating `LXI H,*A(temp)/MVI A,pf/?DSTOP` into a formal-width bind/pool temp (C370 window kept), descriptor RELOC → temp; ALL else BY-NAME [TBD] VERBATIM (marker substrings survive; histogram 68/124 == baseline). Inspect `pairs`/`copy`/`tmp` provenance before writing bytes; NEVER hand-pick addresses; NEVER special-case LOAN2 names. (2) validation: build rc=0 DIRECT; histogram 68/124; whole-file cmp ZA..ZF FRESH POSITIONAL (`build/p3-13/arm-out/`); sweep 159/0; markers CRLF+bare-`^Z` incl. honest N33→NG18 retirement iff armed cmp rc=0 vs KEPT `golden/negpanel1/NG18/NG18.REL` (create `probes/NG18.PLI` from the inline gate source, refusals 188→187); DEC regressions 64/0; divcheck 9/9. (3) LOAN2 UNMODIFIED POSITIONAL → ACTUAL next blocker VERBATIM, NEVER fix (§6 never-predict); EXPR1 21/EXPR2 35. (4) register from **1288/188** (`--update-inventory`, `git diff --cached --stat`, census OWN path, counts expect 15/0/26/0, LOAN2 msg MOVES VERBATIM, NOTHING fixed). (5) **C371 measured-bytes-only BEFORE ANY COVERAGE touch + DATED correction of BOTH C093 errors** (false DECPOLY `*A(005A)=5.67` citation; 2-byte width → NG18 5 B formal-width `00 01 00 00 00`). (6) coverage EXTENSION preferred; SAME-change IDS line if new row (NEVER coverage_gen.py; 15 cols FIRST NON-COMMENT row; manual_ref `pNN[:§X.Y][=phrase]`|`NONE:`); coverage_check+prose rc=0. (7) FULL gate rc=0 DIRECT → `build/gate-e52p13-reg.log`; RESULTS §P3-13 + PLAN §5 row + §P3-13 **CLOSED**; next ACTUAL blocker (marathon through P3-19).

**DONE hop 4-successor (session 01a1b1d9, chain 01a1b1b4 renewal 4/12; ZERO oracle; goldens NEVER touched; config NEVER staged; no push; all rc DIRECT; byte-tier only):** **(l) LANDED — FULL gate rc=0 DIRECT `build/gate-e52p12-reg.log`: 1288/0, 188/188, 9/9, 143 rows 0/0 SUPPORTED 93, census 15/0/26/0, prose 5 — EVERY pre-registered number HIT.** Honest tool note recorded in RESULTS: the FIRST launch was backgrounded and its rc was NOT captured; the canonical log is the synchronous rc-captured re-run (identical content). RESULTS §P3-12 (parity table YA..YI+NG20 with sizes/sha12 re-read FIRST-HAND from `build/p3-12/*-reldump.txt` at close; every §4 miss VERBATIM — YB/YE predicted `?QDDSR` measured `?QDDSL`, YG predicted up measured DOWN, YI pre-arm byte-68 my-gap closed by the sc=0 rule; H-1 CONFIRMED 7/7, H-2/H-3/H-4 FALSIFIED, H-5 symmetry + H-5/H-7 label adjudication, H-6 shift-free model FALSIFIED, H-7/H-8 held; NG20 retirement provenance + ACCEPTED unmeasured-route coverage loss; LOAN2 111→117 VERBATIM NEVER fix; byte-tier-only) + PLAN §5 P3-12 row + §P3-12 **CLOSED** — commit `c6f587a`, prose rc=0. **P3-12 IS CLOSED.**

**DONE Phase A steps (1)-(4) (successor session 01a1b1ec, chain 01a1b1b4 renewal 5/12; ZERO oracle; goldens NEVER touched; config NEVER staged; no push; rc DIRECT; byte-tier):** recovery verified, build rc=0, binary `6a4c6c11…`==tree. (1) authentic LOAN2.REL display-call FULLY DECODED into `build/p3-13/`: per-product `LXI H,*A(var)/A,0A/?DLDOP; LXI H,*A(INF)/A,04/?DLDOP; ?DMUOP; MVI A,03/?QDDSR; LXI H,*A(temp)/MVI A,0A/?DSTOP` at 055D-05FA; temps 0324/2A/30/36/3C (6B each, stride 6); STATIC descriptor vector 031A-0323 (five inline DATA RELOCs → temps, never runtime-written); call `LXI H,*A(031A)` + `CALL` slot 0601 CHAIN-ADDR → code@0674; display entry = arity-5 10-B BLOCK-COPY prologue into 0342..034B; formal reads `LHLD(0342+2i)/MVI A,0A/?DLDOP` [C094] unchanged. CHAIN-ADDR rule-5 (target = LC at emission) CONFIRMED first-hand via new additive `ondump2.full3()` + `build/p3-13/p13dump.py code2/chains` (`dis` alone leaves EXT slots as `abs 0000`). (2) NG18.REL decoded: literal `1` → dec(9,2) formal is DR-ACCEPTED with a STATIC 2-byte pool cell `00 01` @data0000, descriptor cell 000A = inline data RELOC → 0000, ZERO caller runtime code, arity-1 peeled prologue `MOV E,M/INX H/MOV D,M/XCHG/SHLD 000C`, body `LHLD 000C/A,09/?DLDOP/?DCRET`, return store `LXI H,*A(0005)/A,09/?DSTOP`; N33 retirement route = NG20 precedent (golden KEPT NEVER re-derived). (3) C093 `*A(005A)=5.67` bullet ADJUDICATED FALSE-AS-CITED: DECPOLY.REL (3 goldens identical `a51a36c2…`) DATA max 004E — no 005A; descriptors 0048/4A/4C→0030/38/40 VARIABLE cells; R2038 cells 0039/3B/3D→19/21/29 variables; `5.67` is ONLY the R2038 source `z = 5.67;` DEC-store. True literal witness = NG18. Correction owed at C371, dated, NEVER silent. (4) C094 read fully + guard anatomy re-read first-hand (4610-4840: Eident-only DEC admission, copyin widening, Enumber BIN/float-only, Line-117 refusal VERBATIM).
**EXECUTE NOW (successor, exact order — full contract `LEARNINGS.md` § "P3-13 Phase A PART LANDED"):** (0) commit the dirty g448+ guard managed blocks VERBATIM (HANDOFF.md + PROGRESS.md explicit paths, `git diff --cached --stat`, config NEVER staged) plus the UNTRACKED e52p12 `summary.txt`/`transcript-batch*.txt` as a SEPARATE additive evidence commit (e52p11 convention). (5) write PLAN §P3-13 (template §P3-12; §1 blocker VERBATIM; §2 witness table = LOAN2 site + NG18; §3 hypotheses (temp width (pf+1)/2 vs LOAN2 6B stride, shift window C370, static vector, pool-cell width/encoding for `1.5`/larger literals, DSTOP A = formal precision) + falsifiers; §4 per-probe byte predictions NEVER fit; §5 campaign+arm contract (BY-NAME refusals kept, [TBD] histogram 68, N33→NG18 retirement iff cmp rc=0); §6 LOAN2 never-predict; §7 framing) + probes `E52ZA..` (~6-7: single product actual; prod scale≠formal scale≠precision; DEC literal `1.5`; INT literal NG18 shape; same-var twice + mixed var/expr/literal arity 3; arity 5) — CRLF + bare `^Z` + ≤71 cols + ONE dcl per line + `E52Zx:` first-line label + continuation statement; commit PLAN + probes + durables by EXPLICIT paths BEFORE any oracle call or `ocaml/` byte. (6) ONE campaign `PLI_SRC=probes timeout 900 python3 oracle/batch.py E52Z… --tag e52p13 --switches '$L$D'` rc DIRECT; every .PRN read; accepted .RELs decoded into build/p3-13/; goldens VERBATIM (with summary/transcripts) BEFORE any `ocaml/` byte; arm per adjudication; validation (histogram 68/124, cmp FRESH POSITIONAL, sweep 159/0, markers incl N33, DEC regressions 64/0, divcheck 9/9); register from **1288/188**; **C371 measured-bytes-only BEFORE COVERAGE + dated C093 correction**; row/extension + SAME-change IDS line; FULL gate rc=0 DIRECT; RESULTS §P3-13 + PLAN §5 + CLOSED; then next actual blocker (marathon through P3-19).
**STATE:** HEAD = durables commit after this (P3-12 closed `c6f587a`); ledger ENDS **C370** (C371 owed + dated C093 correction owed at C371); inventory **1288/188**; coverage **143/93** 0/0; LAST FULL GATE rc=0 **`build/gate-e52p12-reg.log`**; ARMED binary **`6a4c6c1154a0acd8403b…`** == tree; goldens NEVER re-derived; LOAN2 UNMODIFIED sha `7be23ba3…` rc=2 NO .REL Line-117 blocker VERBATIM NEVER fix; `pli80c` POSITIONAL into FRESH paths; ALWAYS `git diff --cached --stat`; config NEVER staged; no push; rc DIRECT (never pipeline-tail; NEVER glue commands to `rm` operands); byte-tier only; chain 01a1b1b4 renewal 5/12 cap 12.

SUPERSEDED-BY-ABOVE: ## Next action (E2E-52/P3-12 hop 4 CONTINUED — (g)(i)(j) LANDED by successor session 01a1b1c5; (k)(l)(m) OWED — COVERAGE ROW → GATE → CLOSE → P3-13; read `LEARNINGS.md` § "P3-12 hop 4 CONTINUED" FIRST — it is the current contract)

**DONE hop 4-successor (session 01a1b1c5, chain 01a1b1b4 renewal 3/12; ZERO oracle; goldens NEVER touched; config NEVER staged; no push; all rc DIRECT; byte-tier only):** recovery verified HEAD `c186723`, build rc=0, armed binary sha256 `6a4c6c1154a0acd8403b…` == tree. **(g)** divergences **9/9** via standalone `build/p3-12/divcheck.py` (the `--only-divergent` flag is the WRITE/re-measure arm and is blocked by the stale-census preflight — tool lesson recorded). **(i)** registration `5bf5c88`: SPECIMENS **+9 E52YA..YI** with first-hand reldump comments + **N35 retired HONESTLY to POSITIVE NG20** (REJECTS+NEG_META rows deleted with retirement comments; `probes/NG20.PLI` = CRLF+bare-^Z harness materialization sha `acf8e951…`; FRESH positional `cmp` rc=0 vs the KEPT golden, NEVER re-derived); `--update-inventory` → **1288/188** (+10/−1, every line inspected, staged-set verified clean of config); census OWN path rc=0 counts **15/0/26/0 UNCHANGED**, LOAN2 msg MOVED VERBATIM to the Line-117 blocker, NOTHING fixed. **(j)** claim **C370** `172a642` measured-bytes-only BEFORE ANY COVERAGE touch (ledger ENDS **C370**, 193 headers; H-2/H-3/H-4/H-6 falsifiers VERBATIM; NG20 retirement provenance; BY-NAME perimeter; byte-tier NOT-say) + gate YH comment label corrected H-5→H-7 per PLAN §3. **(k)** NEW row **`STOR.DEC_SCALE_ASSIGN`** `bf135a9` + SAME-change `spec/COVERAGE-IDS.txt` line (NEVER `coverage_gen.py`; 15 cols from FIRST NON-COMMENT row; textual tab edit) — `coverage_check` rc=0 **143 rows 0/0 SUPPORTED 93**, prose rc=0; TOOL LESSON: the manual_ref column must match `pNN[:§X.Y][=phrase]` or start `NONE:` — free prose there is an ERROR, adjudicated live.

**EXECUTE NOW (successor, exact order — full detail `LEARNINGS.md` § "P3-12 hop 4 CONTINUED"):** (l) FULL gate rc=0 DIRECT (redirect, NEVER pipeline-tail the rc) → `build/gate-e52p12-reg.log` expect **1288/0, 188/188, 9/9, 143 rows 0/0, census 15/0/26/0, prose 5**; then RESULTS §P3-12 in `spec/lab-evidence/e2e52-p3/RESULTS.md` (per-probe parity table YA..YI+NG20; EVERY §4 miss VERBATIM — YB/YE predicted `?QDDSR` measured `?QDDSL`, YG predicted up measured down, YI pre-arm byte-68 my-gap closed by the sc=0 rule; H-2/H-3/H-4/H-6 falsifiers; NG20 retirement honest; LOAN2 advance 111→112→117 recorded NEVER fix; byte-tier-only) + PLAN §5 progress-table row + PLAN §P3-12 heading **CLOSED**; prose rc=0; commit explicit paths; durables + guard blocks VERBATIM. (m) **BEGIN P3-13** on the ACTUAL Line-117 blocker (`call display(PL * INF, …)` DEC-expression actuals vs FIXED DECIMAL formals): evidence FIRST with ZERO oracle — audit `DECPOLY`/`R2037`/`R2038`/`R725` witnesses + the N33_DEC_FORMAL family reldumps, write PLAN §P3-13 (template §P3-12: §1 blocker VERBATIM; §2 witness table; §3 hypotheses + falsifiers; §4 per-probe byte predictions NEVER fit; §5 campaign+arm contract; §6 LOAN2 never-predict; §7 framing) + probes `E52ZA..` (CRLF + bare `^Z` + ≤71 cols + ONE dcl per line), commit by EXPLICIT paths BEFORE any oracle call/`ocaml/` byte; marathon authorization live (budget through P3-19).

**STATE:** HEAD = durables commit after this; ledger ENDS **C370**; inventory **1288/188**; coverage **143/93** 0/0; last full gate rc=0 `build/gate-e52p11-reg.log` (gate re-run owed at (l)); ARMED binary **`6a4c6c1154a0acd8403b…`** == tree; goldens NEVER re-derived; LOAN2 UNMODIFIED sha `7be23ba3…` rc=2 NO .REL Line-117 blocker VERBATIM NEVER fix; `pli80c` POSITIONAL into FRESH paths; ALWAYS `git diff --cached --stat`; config NEVER staged; no push; rc DIRECT (incident law: never glue commands to `rm` operands); byte-tier only; chain 01a1b1b4 renewal 3/12 cap 12.

**DONE hop 4 (successor session 01a1b1b4, chain renewal 2/12; ZERO oracle; goldens NEVER touched; config NEVER staged; no push; all rc DIRECT; byte-tier only):** recovery verified HEAD `61a32d6`, armed binary re-built deterministic. **(a)** per-File histogram re-proved vs replayed baseline (`git archive 3b64336` → binary `25c57e27…`): Warning 27 `ptr` IS BASELINE (codegen.ml RTbmem); the arm had introduced ONE new W27 unused `args` in `dv_of` — FIXED to wildcard (commit `60b9c79`, zero behavior change); histogram codegen 68/total 124 == baseline EXACTLY; corrected binary sha256 **`6a4c6c1154a0acd8403b973acc8a66a297785cdd1e6f23cc119af2255dc0d1d0`** (supersedes `f561426…`); 9/9 E52YA..YI whole-file cmp rc=0 re-held on FRESH paths. **(b)** sweep E46N E46K E51 E52 P086 R10 → 159 byte-exact, FAILS 0. **(c)** markers 15/16 — ONLY `N35_DEC_STORE_SCALE_DRIFT` now compiles rc=0 with cmp rc=0 vs `golden/negpanel1/NG20/NG20.REL` (harness + fresh re-materialization); RETIREMENT DECIDED honestly (N26 precedent + NEG_META "DR COMPILES IT"): N35 leaves REJECTS+NEG_META, NG20 source registers as POSITIVE specimen `probes/NG20.PLI` (golden path UNCHANGED, NEVER re-derived); refusals 189→188; NO invented replacement negative for the still-refused suffix/pointer DEC-store routes (their DR behaviour UNMEASURED — loss accepted, recorded). **(d)** DEC regressions R5xx–R8xx + LOAN1 → 64 byte-exact, FAILS 0. **INCIDENT repaired:** accidental `rm` of `artefacts/LOAN2.PLI` (missing `;` in my command); restored via single-path `git restore --source=HEAD`, sha `7be23ba3…` verified twice, zero scientific loss; law recorded in LEARNINGS. **(e)** LOAN2 UNMODIFIED POSITIONAL → rc=2, NO .REL, ACTUAL new blocker VERBATIM `codegen: non-variable argument against a FIXED DECIMAL formal is unproven [TBD] (DR passes an automatic decimal BY REFERENCE -- the descriptor holds LXI H,*A(cell); a literal or expression decimal argument has no sample [DECPOLY, R2037/R2038/R725]. Line 117)` — advanced PAST 111/112; NEVER fix this slice; = P3-13 target (`call display(PL * INF, …)` DEC-expression actuals). EXPR1 21/EXPR2 35 unchanged.

**EXECUTE NOW (successor, exact order):** (g) divergences 9/9 (gate divergence panel; `spec/DIVERGENT.txt`); (i) REGISTER from **1278**: SPECIMENS +9 `E52YA..YI` block (comments from `build/p3-12/*-reldump.txt` measured bytes — YA 003C control no-shift; YB/YE 0041 up d=02 QDDSL; YC 0041 up d=0B; YD 0041 = LOAN2:111 verbatim down d=0B QDDSR; YF 0041 down d=0E; YG 0041 down d=0D; YH 0051 computed control; YI 003F decimal() LHLD/?QI15D/MVI A,02/?QDDSL/dst A=09) **PLUS NG20 retirement-to-positive** (delete REJECTS `N35_DEC_STORE_SCALE_DRIFT` ~line 2691 + its NEG_META ~line 3754, add `"NG20": ("probes/NG20.PLI", "golden/negpanel1/NG20/NG20.REL")` — CREATE `probes/NG20.PLI` CRLF+bare^Z from the inline source, cmp rc=0 ALREADY measured); materialize goldens dir entries EXACTLY as batch.py layout if the gate requires; `--update-inventory` → expect **1288/188**, inspect EVERY line, ALWAYS `git diff --cached --stat`, NEVER stage `handoff.config.json`; census OWN path (`cp spec/census/corpus-census.json /tmp/…; python3 tools/corpus_census.py --check /tmp/…`) — LOAN2 msg MOVES VERBATIM to the Line-117 text, NOTHING fixed, counts expect 15/0/26/0; (j) **C370 measured-bytes-only BEFORE ANY `spec/COVERAGE.tsv` touch** (law: direct cross-scale DEC store emits `MVI A,|Δs| / CALL ?QDDSL`(up)/`?QDDSR`(down) BETWEEN source `?DLDOP` and `LXI H,dst`; DSTOP A = TARGET precision; H-2/H-3/H-4 FALSIFIED VERBATIM; decimal()-direct-store sc=0 per YI; BY-NAME perimeter: pointer-formal/suffix routes keep [TBD]; NG20 retirement provenance; byte-tier-only NOT-say; ledger ENDS C369); (k) NEW row `STOR.DEC_SCALE_ASSIGN` SUPPORTED + `spec/COVERAGE-IDS.txt` line in the SAME change (NEVER `coverage_gen.py`; 15 cols from FIRST NON-COMMENT row; textual tab edit); coverage_check rc=0 (expect 143 rows/93 SUPPORTED — let it adjudicate) + prose rc=0; (l) FULL gate rc=0 DIRECT → `build/gate-e52p12-reg.log` (expect 1288/0, 188/188, 9/9, census 15/0/26/0, prose 5); RESULTS §P3-12 + PLAN §5 row + §P3-12 **CLOSED**; (m) **BEGIN P3-13** on the ACTUAL Line-117 blocker (DEC-expression actuals to DEC formals — evidence FIRST: audit DECPOLY/R2037/R2038/R725 witnesses, pre-register probes BEFORE any oracle call/`ocaml/` byte) under marathon authorization (budget through P3-19).

**STATE:** HEAD = durables commit after this; ledger ENDS **C369** (C370 owed); inventory **1278/189** (1288/188 owed at registration); coverage **142/92** 0/0 (143/93 owed); last full gate rc=0 `build/gate-e52p11-reg.log`; ARMED binary **`6a4c6c1154a0acd8403b…`** == tree; goldens NEVER re-derived; LOAN2 UNMODIFIED sha `7be23ba3…` rc=2 NO .REL Line-117 blocker VERBATIM NEVER fix; `pli80c` POSITIONAL into FRESH paths; ALWAYS `git diff --cached --stat`; config NEVER staged; no push; rc DIRECT (NEVER glue commands to `rm` operands — incident law); byte-tier only; chain 01a1b1b4 renewal 2/12 cap 12.

SUPERSEDED-BY-ABOVE: ## Next action (E2E-52/P3-12 hop 3 — ARM LANDED `1111d5e` 9/9 cmp-EXACT on binary `f56142696f344acc80f6`; VALIDATION SUITE + LOAN2 + REGISTER + CLOSE OWED; read `LEARNINGS.md` § "P3-12 ARM LANDED" + § "hop 2" FIRST)

**OPERATOR AUTHORIZATION (new brief, 2026-11-07, session 01a1b18b, NEW chain — this session is NOT a renewal successor):** the P3-11 terminal STOP is SUPERSEDED for work necessary to complete LOAN2; up to EIGHT scientific slices P3-12..P3-19, ~64 new oracle probes, per-slice cycle preregister → measure → implement → validate → register → close → proceed to the next actual blocker without a new prompt; completion = unmodified `artefacts/LOAN2.PLI` compiles AND whole-file `.REL` byte-identity with `golden/first/LOAN2/LOAN2.REL`; compile-tier only (no CP/M run, no PLILIB, no runtime claims); no push; `handoff.config.json` NEVER staged. The obsolete "STOP / nothing authorized / no P3-12" managed prose of P3-11 is Historical; PROTOCOL.md remains binding.

**DONE hop 2 (this session, chain renewal 1/12; ONE campaign run; goldens committed BEFORE any `ocaml/` byte):** campaign e52p12 rc=0 **9 ok/9**, every `.PRN` `NO ERROR(S)` both passes; store regions decoded first-hand (`build/p3-12/`): **H-1 CONFIRMED 7/7** — shift `MVI A,|Δs| / ?QDDSL`(up) or `?QDDSR`(down) sits BETWEEN source `?DLDOP` and `LXI H,dst`; DSTOP A = target precision; H-2/H-3/H-4 FALSIFIED (YC d=11 with Δp=9; YF d=14 accepted); H-5 CONFIRMED; **H-6: DR accepts `decimal(i,7)` into dec(9,2) WITH `?QI15D / MVI A,02 / ?QDDSL`** — my shift-free context model FALSIFIED, pre-arm cmp YI FAILS byte 68 (honest my-gap); YA/YH cmp OK. §4 misses kept VERBATIM (YB/YE/QDDSL vs my QDDSR label, YG down not up). Goldens VERBATIM `0c43932`. DONE hop 1: HEAD `83e82b7` verified; binary sha256 `25c57e27696421e929b8…` == armed baseline; LOAN2 UNMODIFIED rc=2 / NO .REL / blocker VERBATIM; **first responsible statement MEASURED as LOAN2:111 `INF = ci;`** via temporary line-instrumentation of the `dpush` refusal, then REVERTED (tree clean, fingerprint re-held); both shift directions reproduce rc=2 in scratch probes; **Phase A evidence CLOSED** — the new law already has TWO DR witnesses: authentic LOAN2.REL 04B7-04CB (`DLDOP / MVI A,0B / ?QDDSR / LXI H,dst / MVI A,04 / ?DSTOP`, d = 14-3 = 11, TARGET precision at DSTOP) and registered-negative NG20 (= gate `N35_DEC_STORE_SCALE_DRIFT`, `dec(9,2)`→`dec(9,4)` = `?QDDSL 02` in the SAME position, full `.PRN`+`.REL`, DR `NO ERROR(S)` both passes) → N35 retires to POSITIVE by the N26_DECDIV precedent; equal-scale cross-precision control already whole-file exact (LOAN1 `PMT = P` re-measured `cmp` rc=0 this session); LOAN2:112 divide bytes agree with the ARMED [C086] path → outside P3-12's perimeter; NG21 FALSIFIED as a witness (error listing, no .REL). Nine CP/M-compatible probes materialized `probes/E52Y{A..I}.PLI` (CRLF + bare `^Z` + ≤71 cols + one dcl per line; sanity: YA/YH/YI rc=0, YB..YG rc=2 at the guard). Full findings + the successor contract: `LEARNINGS.md` § "E2E-52/P3-12 Phase A CLOSED".

**EXECUTE NOW (successor, exact order — full detail `LEARNINGS.md` § "P3-12 ARM LANDED"):** (a) warning histogram codegen 68/total 124 == baseline (Warning 27 `ptr` seen — check whether baseline had it; if NEW, it came from my `ocaml/lib/codegen.ml` edit, fix before anything else); (b) sweep `python3 build/e52p3/sweep.py E46N E46K E51 E52 P086 R10` FAILS 0; (c) markers harness (CRLF+bare ^Z, `build/e52p8-reg/markers.py` precedent); (d) DEC regressions R5xx/R6xx/R7xx/R8xx + LOAN1 whole-file cmp; (e) LOAN2 UNMODIFIED POSITIONAL FRESH path — record ACTUAL next blocker VERBATIM (expect advance past 111; NEVER fix); EXPR1/EXPR2 positional; (f) negative panel: N35_DEC_STORE_SCALE_DRIFT (NG20) retires to POSITIVE honestly; negatives count moves 189→188 unless replaced; (g) divergences 9/9; (h) FULL gate rc=0 DIRECT → `build/gate-e52p12-reg.log`; (i) register from 1278: SPECIMENS +9 (E52YA..YI all now byte-exact), `--update-inventory`, `git diff --cached --stat`, census OWN path; (j) **C370 measured-bytes-only BEFORE any COVERAGE touch**; (k) NEW row `STOR.DEC_SCALE_ASSIGN` + SAME-change `spec/COVERAGE-IDS.txt` line (NEVER coverage_gen.py; 15 cols FIRST NON-COMMENT row; textual tab edit); coverage_check+prose rc=0; (l) gate AGAIN; RESULTS §P3-12 + PLAN §5 row + §P3-12 **CLOSED**; (m) BEGIN P3-13 on the ACTUAL next blocker (marathon authorization live).

SUPERSEDED-BY-ABOVE: **EXECUTE (in this exact order — (2) DONE):** (1) write PLAN §P3-12 (template §P3-11 — §1 blocker VERBATIM + the instrumentation method; §2 witness table; §3 H-A..H-I with falsifiers incl. the precision-in-shift and d-cap competitors; §4 per-probe pre-registered byte sequences, NEVER fit; §5 campaign + smallest-arm contract + validation list; §6 LOAN2 direction; §7 DSTOP-A framing) + the §5 progress-table row; commit `spec/lab-evidence/e2e52-p3/PLAN.md` + the nine `probes/E52Y*.PLI` by EXPLICIT paths BEFORE any oracle call or `ocaml/` byte; ALWAYS `git diff --cached --stat`; config NEVER staged. (2) ONE campaign `PLI_SRC=probes timeout 900 python3 oracle/batch.py E52YA E52YB E52YC E52YD E52YE E52YF E52YG E52YH E52YI --tag e52p12 --switches '$L$D'` rc DIRECT; read every `.PRN`; decode every accepted `.REL` (ondump2 buffers + `tools/dis80.py` table + CHAIN-EXT names at anchor = opcode+1); commit goldens VERBATIM before touching `ocaml/`. (3) arm ONLY the measured shapes in the `dpush` simple-operand arm; unproven shapes keep explicit [TBD] refusals; NEVER special-case LOAN2 names/addresses. (4) build rc=0 + histogram codegen 68 / total 124 == baseline + whole-file `cmp` of every accepted probe into FRESH paths + sweep FAILS 0 + markers harness (CRLF+bare `^Z`, incl. every DEC/N35-adjacent marker) + DEC regressions + negatives + divergences 9/9 → FULL compile-tier gate rc=0 DIRECT `build/gate-e52p12-reg.log`. (5) LOAN2 UNMODIFIED POSITIONAL → record the ACTUAL next blocker VERBATIM (or, if it compiles, go STRAIGHT to the §7 whole-file parity phase of the brief). (6) register (SPECIMENS +accepted only, baseline 1278, NG20 retirement decision recorded honestly, census OWN path), claim **C370** measured-bytes-only BEFORE any COVERAGE touch, NEW `STOR.DEC_SCALE_ASSIGN`-class row ONLY if justified + its `spec/COVERAGE-IDS.txt` line in the SAME change (NEVER `coverage_gen.py`), coverage_check/prose rc=0, gate AGAIN, RESULTS §P3-12 + §P3-12 **CLOSED**, commit guard blocks VERBATIM, then BEGIN THE NEXT REAL BLOCKER (P3-13) under the same authorization. Renew autonomously at safe committed boundaries only.

**STATE:** HEAD = `1111d5e`; ledger ENDS **C369**; inventory **1278/189**; coverage **142/92** 0/0; last full gate rc=0 `build/gate-e52p11-reg.log`; ARMED binary now `f56142696f344acc80f6…` (sha256, == tree; suite not yet run); goldens NEVER re-derived; `pli80c` POSITIONAL into FRESH paths; tree clean except guard blocks + operator `handoff.config.json` (NEVER stage); no push; rc DIRECT; byte-tier only.

SUPERSEDED-BY-ABOVE: 

SUPERSEDED-BY-ABOVE: ## Next action (E2E-52/P3-11 hop 3 LANDED — campaign 11 ok/11, goldens VERBATIM `060289e` BEFORE any byte, candidate A ARMED `3e0a3c1` 9/9 byte-exact, LOAN2 past 99; REGISTRATION → C369 → COVERAGE → GATE → CLOSE OWED; read `LEARNINGS.md` § "P3-11 hop 3 LANDED" STILL-OWED FIRST; STOP at P3-11 closure)

**DONE this hop (session 01a1b13c, chain 01a1b0c9 renewal 3/12; goldens committed BEFORE any `ocaml/` byte; config NEVER staged; no push; all rc DIRECT):** recovery verified HEAD `fd8783b`, build rc=0 binary `a4c0e235…`==baseline; ONE campaign rc=0 **11 ok/11**, all .PRN `NO ERROR(S)` both passes; EVERY §4 CODE prediction HIT (XA 0036 XB 003E XC 003E XD 003C XE 003D XF 0063 XG 003E XH 0038 XI 0043 XJ 0021 XK 0036); **H-E DOUBLE patch CONFIRMED (single falsified), H-B pagesize-required competitor FALSIFIED, H-J ACCEPTED no-open SEL-COMMON-at-first-use, H-K ACCEPTED input open w1 9006 attach STILL 0652**; honest §4 miss recorded VERBATIM: H-A slot "→0030" was my arithmetic slip, measured 002D. Goldens VERBATIM `060289e`. Candidate A armed `3e0a3c1`: ONE condition line in `lower_open` records `PRINT` beside `OUTPUT` into `st.file_out`; guard/emitters UNCHANGED, zero statement bytes; PU1 substring survives VERBATIM (message body moved per §5). VERIFIED armed binary `25c57e27696421e929b8…` (deterministic, fresh `_build-e52p11`): histogram 68/124==baseline; cmp XA..XI **9/9**; XJ/XK rc=2 BY NAME; sweep FAILS 0; markers 5/5; regressions **38/38**. **LOAN2 ADVANCED VERBATIM past line 99**: rc=2 NO .REL, ACTUAL new blocker `codegen: DECIMAL assignment between differing scales is unproven [TBD] (only computed results are pinned as needing a QDDSL/QDDSR fix; a direct DEC operand store always had equal scales in the samples)` — **NO `(line N)` clause**; NEVER fix (PLAN §6). EXPR1 GET-21/EXPR2 FLOAT-35 unchanged. Evidence: `build/e52p11/{campaign-rc.txt,*-reldump.txt,out/,sweep-arm.log,markers.log,reg/,pos/}`.

**EXECUTE (successor, EXACT order — full contract `LEARNINGS.md` § hop 3 STILL OWED):** (6a) registration from **1269**: SPECIMENS **+9** XA..XI ONLY; XJ/XK → REJECTS `my-gap` (SE/E46L8 precedent, goldens KEPT, markers RE-MEASURED under gate CRLF+bare-^Z); `--update-inventory` → **1278/189** (+9/+2, inspect every line, `git diff --cached --stat`, config NEVER staged); census OWN path (15/0/26/0, LOAN2 msg MOVED VERBATIM to DEC-scales text, NOTHING fixed); commit. (6b) **C369 measured-bytes-only BEFORE ANY `spec/COVERAGE.tsv` touch** (bullets (a)-(i) Phase-A contract; ledger ENDS C369). (6c) EXTEND `FILE.PUT_PAGE`/`FILE.PUT_LIST`/`FILE.PUT_SKIP` rows (NEVER new rows, NEVER `coverage_gen.py`; 15 cols FIRST NON-COMMENT row; `delimiter='\t'`; IDS set UNCHANGED by extensions); coverage_check rc=0 expect **142 rows 0/0 SUPPORTED 92** + prose rc=0. (6d) FULL gate rc=0 DIRECT → `build/gate-e52p11-reg.log` expect **1278/0, 189/189, 9/9, 142 rows, census 15/0/26/0, prose 5**. (6e) RESULTS §P3-11 + PLAN §5 row + §P3-11 **CLOSED** + durables. **STOP at P3-11 — NEVER the DEC-scales blocker, no P3-12, no runtime claims.**

**STATE:** HEAD = this durables commit; ledger ENDS **C368** (C369 owed); inventory **1269/187** (1278/189 owed); coverage **142/92**; armed binary `25c57e27696421e929b8…`==tree; goldens NEVER re-derived; `pli80c` POSITIONAL FRESH paths; ALWAYS `git diff --cached --stat`; chain 01a1b0c9 renewal 3/12 cap 12; no push; rc DIRECT; byte-tier only.

SUPERSEDED-BY-ABOVE: ## Next action (E2E-52/P3-11 hop 2 LANDED — PLAN §P3-11 + probes E52XA..XK PRE-REGISTERED BEFORE any oracle call or `ocaml/` byte; CAMPAIGN e52p11 OWED; read `LEARNINGS.md` § "P3-11 hop 2" + PLAN §P3-11 FIRST; STOP at P3-11 closure)

**DONE this hop (session 01a1b127, chain 01a1b0c9 renewal 2/12; ZERO oracle; ZERO `ocaml/` byte; goldens NEVER touched; config NEVER staged; no push; all rc DIRECT):** recovery verified HEAD `57e7f62`+guard `f58f64f`; build rc=0 binary `a4c0e235ed4bb81fe284…` (md5 `cbede3b5…`) == baseline re-held; g427 blocks VERBATIM `093ba87`. FIRST-HAND: LOAN2 03AA-03BB 18-B PAGE + DOUBLE patch (LXI-B 03B1, CA 03A8 → 03BC); E46N1 20-B bare skip re-dumped (NO `?PNCOP`); E46N2 31-B; E46L8 no-open attach + SEL-COMMON-at-first-use; **CORRECTION: imm store `x = 2` = 6 code bytes, not 7** (VA CODE 001C arithmetic + E46L8 both close). TB/TC prove the titled-route `21 00 00`+E5 word and 4 trailing E5 pushes are ROUTE furniture, not pagesize furniture → XB predicts 29-B block, w1 `0E52`. Zero-oracle sanity: ALL 11 probes rc=2 at the eligibility guard on their PUT line — every OPEN (XB combo, XK titleless input) lowers TODAY; gap = `st.file_out` recording only (`lower_open` records ONLY spelled `OUTPUT`; LOAN2:54/56 spell print, no OUTPUT). LANDED: PLAN §P3-11 (H-A..H-K + falsifiers incl H-E DOUBLE-vs-SINGLE + §4 CODE predictions XA 0036 XB 003E XC 003E XD 003C XE 003D XF 0063 XG 003E XH 0038 XI 0043 XJ 0021 XK 0036; §5 candidate adjudication; §6 never-predict; §7 source-structure-not-runtime guard semantics) + 11 `probes/E52X*.PLI` (CRLF+bare ^Z, ≤71 cols, statement after every PUT) + LEARNINGS § hop 2 — committed by EXPLICIT paths BEFORE the first oracle call.

**EXECUTE (successor, EXACT order — PLAN §P3-11 §5 is the binding contract):** (2) ONE campaign `PLI_SRC=probes timeout 900 python3 oracle/batch.py E52XA E52XB E52XC E52XD E52XE E52XF E52XG E52XH E52XI E52XJ E52XK --tag e52p11 --switches '$L$D'` rc DIRECT (NEVER pipeline-tail); read EVERY `.PRN`; reldump accepted .RELs into `build/e52p11/`; goldens VERBATIM into git BEFORE any emitter change; XJ/XK honest (dr-refuse → REJECTS precedent WL; accepted-and-mine-refuses → golden KEPT + my-gap REJECTS precedent E46L8/SE); NEVER invent goldens. (3) arm SMALLEST measured rule — candidate A = ONE line in `lower_open` also recording PRINT-bearing opens into `st.file_out`, admitted iff XA..XI (esp. XG/XH/XI) land accepted+byte-exact via the ONE route-independent emitter; else candidate C PAGE-only; NO open-encoder/emitter byte change; PU1 substring `PUT FILE(F) has no byte-exact DR witness` survives; BY-NAME refusals kept (PAGE+items, counted PAGE, LINE, console PAGE, INPUT named PUT, no-open, KEYED). (4) build rc=0 DIRECT + histogram codegen 68/total 124 + whole-file cmp accepted probes (POSITIONAL, FRESH out paths) + sweep `python3 build/e52p3/sweep.py E46N E46K E51 E52 P086 R10` FAILS 0 + markers harness CRLF+bare ^Z (`build/e52p8-reg/markers.py` precedent) incl PU1/E41X5/E46K10/N3_PAGE/E46N21 MARKER_FAILS 0 + regressions E46N*/E16D/E17D/TA..TJ/UA..UF/VA..VK/WA..WK + negatives 187 + divergences 9/9. (5) LOAN2/EXPR1/EXPR2 POSITIONAL VERBATIM — ACTUAL blocker past 99 recorded, NEVER fix; unexpected LOAN2 .REL → cmp vs `golden/first/LOAN2/LOAN2.REL`, report, STOP. (6) registration from **1269** (accepted+byte-exact only; `--update-inventory`; ALWAYS `git diff --cached --stat`; config NEVER staged; census OWN path); **C369 measured-bytes-only BEFORE ANY `spec/COVERAGE.tsv` touch** (bullet contract in LEARNINGS § Phase A + PLAN §2/§7); prefer EXTENDING `FILE.PUT_PAGE`/`FILE.PUT_LIST`/`FILE.PUT_SKIP` rows (new rows ship their `spec/COVERAGE-IDS.txt` line in the SAME change; NEVER `coverage_gen.py`; 15 cols from FIRST NON-COMMENT row; `delimiter='\t'`); coverage_check+prose rc=0; FULL gate rc=0 DIRECT → `build/gate-e52p11-reg.log`; RESULTS §P3-11 + PLAN §5 row + §P3-11 **CLOSED** + durables. **STOP at P3-11 — no next-blocker fix, no P3-12, no runtime claims.**

**STATE:** HEAD = this durables commit; ledger ENDS **C368**; inventory **1269/187**; coverage **142/92** 0/0; binary `a4c0e235ed4bb81fe284…` == tree; goldens NEVER re-derived; LOAN2 blocker VERBATIM `codegen: PUT FILE(OUTPUT) has no byte-exact DR witness [TBD] (line 99)` (rc=2, NO .REL, NEVER fix); census `0198fe5` 15/0/26/0; tree clean except guard blocks + operator `handoff.config.json` (NEVER stage) + ignored `build/e52p1*/`, `ocaml/_build*`, `ocaml/*.log`; `pli80c` POSITIONAL into FRESH paths; ALWAYS `git diff --cached --stat`; chain 01a1b0c9 renewal 2/12 cap 12; no push; rc DIRECT; byte-tier only.

SUPERSEDED-BY-ABOVE: ## Next action (E2E-52/P3-11 hop 1 PARTIAL — first-hand byte re-verification LANDED + checks clean; PLAN §P3-11 + PROBES E52XA..XK STILL OWED, then campaign/arm/register/close; read `LEARNINGS.md` § "E2E-52/P3-11 hop 1 IN FLIGHT" FIRST — it is the complete successor contract; then § "P3-11 Phase A")

**DONE this hop (session 01a1b0c9 renewal 1/12; ZERO oracle; ZERO `ocaml/` byte; goldens NEVER touched; config NEVER staged; no push; all rc DIRECT):** recovery verified HEAD `b0c5dbd`+guard `f58f64f`; build rc=0 binary md5 `cbede3b5…` == baseline. FIRST-HAND raw-record re-verification (dumps `build/e52p11/xplan/`): LOAN2 03AA-03BB 18-B PAGE + DOUBLE patch (LXI B 03B1→03BC AND CA 03A8→03BC); COPYLPT 0215-00226; P019B 0063-007C LIST 26 B; E52TA/TB/TC open blocks + sizes (PF 0024, OUTF 0026, CODE 0035/003D/003B); E52VA leaf + 7-B `x = 2` store; E46N1 attach start. CHECKS CLEAN: `E52X*` names unused, tag `e52p11` unused, NO registered negative pairs PRINT-open + named PUT (the two grep hits are comment prose); PU1/E41X5/E46K10 have no open → candidate A keeps their markers firing. All findings + the full 6-step EXECUTE + probe panel + falsifiers + candidate adjudication recorded in LEARNINGS § hop 1 IN FLIGHT — READ IT FIRST; every cited byte re-checkable against the xplan dumps before acting.

**STATE:** HEAD = this durables commit; ledger C368; inventory 1269/187; coverage 142/92 0/0; binary `a4c0e235ed4bb81fe284…` == tree; goldens NEVER re-derived; LOAN2 blocker VERBATIM `codegen: PUT FILE(OUTPUT) has no byte-exact DR witness [TBD] (line 99)` (rc=2, NEVER fix); census `0198fe5` 15/0/26/0; tree clean except guard blocks + operator `handoff.config.json` (NEVER stage) + ignored `build/e52p1*/`, `ocaml/_build*`, `ocaml/*.log`; `pli80c` POSITIONAL into FRESH paths; ALWAYS `git diff --cached --stat`; chain 01a1b0c9 renewal 1/12 cap 12; no push; rc DIRECT; byte-tier only.

SUPERSEDED-BY-ABOVE: ## Next action (E2E-52/P3-11 — PRINT-OPENED FILE PUT / LOAN2:99 — Phase A AUDITED; PLAN §P3-11 + PROBES E52XA..XK OWED, then ONE `e52p11` campaign, arm, verify, register C369, close; read `LEARNINGS.md` § "P3-11 Phase A" FIRST)

**DONE this hop (session 01a1b0c9, operator brief E2E-52/P3-11; ZERO oracle so far; goldens NEVER touched; `handoff.config.json` NEVER staged; no push; all rc DIRECT):** recovery verified HEAD `06f7993` == brief; g423 recovery blocks committed `1428dad`; build rc=0 DIRECT binary `a4c0e235ed4bb81fe284…` == baseline fingerprint. **Phase A COMPLETE** (raw reldumps `build/e52p11/{COPYLPT,LOAN2,P019B,E46N10}-reldump.txt`; full findings in `LEARNINGS.md` § "E2E-52/P3-11 — Phase A evidence audit"): the exact line-99 statement IS measured VERBATIM inside original `golden/first/LOAN2/LOAN2.REL` at 03AA-03BB (18-byte PAGE, attach `11 52 06`, behind w1 `0E52/2E52` print opens) and COPYLPT:53 at 0215-0226 — same geometry behind print+attrs open w1 `3E52`; P019B LIST-behind-PRINT re-verified at 0063-007C; SIOMODES pairs SKIP/LIST/PAGE/EDIT attaches `0x0652` behind print opens at ~15 sites. The ONLY missing fact is panel-verified whole-object minimal PRINT+PUT specimens + the two negative-space questions (no-prior-OPEN PAGE; INPUT-open PAGE). Guard anatomy pinned: `lower_open` records `st.file_out` ONLY on spelled `OUTPUT` (codegen ~11557); the `Pfile` arm (~13775) is the ONE guard for LIST/SKIP/PAGE; the `Sk_page` emitter is route-independent; PU1/E41X5 negative markers require the no-open LIST refusal + the substring `PUT FILE(F) has no byte-exact DR witness` to survive any guard change.

**EXECUTE (successor, in order):** (1) write PLAN §P3-11 (panels A–J, hypotheses + falsifiers + arm contract; template = §P3-10) and probes **E52XA..E52XK** (11; sources ONLY in `probes/E52X*.PLI`, CRLF + bare `^Z` + ≤71 cols, `dcl f file;` + `dcl x fixed bin;` skeletons; E52VA `if x < 0 then` is the measured IF leaf; continuation statement after every PUT so LXI B slot is measurable) — panel list + predictions are in `LEARNINGS.md` § Phase A; **commit PLAN + probes + durables by EXPLICIT paths BEFORE the first oracle call and before any `ocaml/` byte** (blobs prove ordering, PROTOCOL #1). (2) ONE campaign `PLI_SRC=probes timeout 900 python3 oracle/batch.py E52XA..E52XK --tag e52p11 --switches '$L$D'` rc DIRECT; read EVERY `.PRN`; reldump accepted .RELs into `build/e52p11/`; commit goldens VERBATIM before any emitter change; XJ/XK verdicts may be dr-refuses or my-gaps — classify honestly, never invent goldens. (3) Phase D implementation: choose the SMALLEST measured rule (candidate A = `lower_open` records PRINT opens into `st.file_out` beside OUTPUT; candidate C = PAGE-only admission) per the XG/XH/XI verdicts; preserve every measured OPEN encoder byte, the 18-byte PAGE, attach/PAGOP/QIOOP bytes, IF/ELSE patching, the `[TBD]` refusals for unmeasured combos, and the PU1 marker substring; general file identifiers only — NO name-based special-casing of `OUTPUT`. (4) build rc=0 DIRECT + histogram vs codegen 68/total 124 + whole-file cmp of accepted probes (FRESH out paths, POSITIONAL) + sweep `python3 build/e52p3/sweep.py E46N E46K E51 E52 P086 R10` FAILS 0 + markers harness (CRLF+bare ^Z) + regressions E46N10/E16D/E17D/E46L*/E46M*/E52TA..TJ/UA..UF/VA..VK/WA..WK + negative panel + divergences 9/9. (5) LOAN2/EXPR1/EXPR2 POSITIONAL VERBATIM: record the ACTUAL first blocker past line 99, NEVER fix it, NEVER start P3-12; if LOAN2 unexpectedly emits .REL compare vs `golden/first/LOAN2/LOAN2.REL` and STOP. (6) registration from **1269** (accepted+byte-exact probes only; `--update-inventory`; ALWAYS `git diff --cached --stat`, config NEVER staged; census OWN path), **C369 measured-bytes-only BEFORE ANY COVERAGE touch** (bullet contract in LEARNINGS § Phase A), extend `FILE.PUT_PAGE` (and if G/H land, `FILE.PUT_LIST`/`FILE.PUT_SKIP` — prefer extending existing contracts, NEVER `coverage_gen.py`, 15 cols from FIRST NON-COMMENT row, `delimiter='\t'`, new rows ship their `spec/COVERAGE-IDS.txt` line in the SAME change), `coverage_check` + `file_prose_check` rc=0, FULL gate rc=0 DIRECT → `build/gate-e52p11-reg.log`, RESULTS §P3-11 + PLAN §5 row + §P3-11 **CLOSED** + durables. **STOP at P3-11 closure — do NOT fix the next LOAN2 blocker, no P3-12, no runtime claims.**

**STATE:** ledger ENDS **C368**; inventory **1269/187**; coverage **142/92** 0/0; gate rc=0 at prior HEAD (`build/gate-e52p10-reg.log`); binary `a4c0e235ed4bb81fe284…` == tree; goldens NEVER re-derived; LOAN2 blocker VERBATIM `codegen: PUT FILE(OUTPUT) has no byte-exact DR witness [TBD] (line 99)`; census `0198fe5` 15/0/26/0; tree clean except operator `handoff.config.json` (NEVER stage) + ignored `build/e52p1*/`, `ocaml/_build*`, `ocaml/*.log`; `pli80c` POSITIONAL into FRESH paths; chain 01a1b069 CLOSED at 3/12 — this session 01a1b0c9 is a NEW operator chain; no push; all rc DIRECT.

SUPERSEDED-BY-ABOVE: ## Next action (E2E-52/P3-10 hop 3 REMAINDER + SUBROUND P3-10 CLOSED — STOP REACHED; NOTHING AUTHORIZED; successor verifies then closes the session)

**DONE (this successor session 01a1b0af, chain 01a1b069 renewal 3/12; ZERO oracle; goldens NEVER touched; `handoff.config.json` NEVER staged; no push; all rc DIRECT):** recovery verified; build rc=0 binary `a4c0e235ed4bb81fe284…` == tree; **(3)** all C368-cited bytes re-verified FIRST-HAND vs `build/e52p10/*-reldump.txt` + WL `.PRN` (incl. the WG region position and WE `21 00 01`), **C368 committed `7153716` measured-bytes-only BEFORE any COVERAGE touch** (ledger ENDS C368); **(4)** `COND.SIGNAL` NEW row SUPPORTED/**EXACT:9** + EXPLICIT `spec/COVERAGE-IDS.txt` line `65b005e` (NEVER `coverage_gen.py`; 15 cols from FIRST NON-COMMENT row; `delimiter='\t'`; diff 2 lines BY CONTENT) — `coverage_check` rc=0 **142 rows 0/0 SUPPORTED 92**, prose rc=0; **(5)** FULL gate rc=0 DIRECT `build/gate-e52p10-reg.log` — **1269/0, 187/187, 9/9, 142 rows, census 15/0/26/0, prose 5** — every pre-registered number HIT; **(6)** RESULTS §P3-10 + PLAN §5 P3-10 row + PLAN §P3-10 **CLOSED** `fbca4fe`, prose rc=0; LEARNINGS § hop 3 REMAINDER + this durables rewrite.

**EXECUTE (successor — the ONLY steps):** commit the guard-refreshed managed blocks in HANDOFF.md/PROGRESS.md VERBATIM (explicit paths, NEVER hand-edit, NEVER stage `handoff.config.json`, ALWAYS `git diff --cached --stat` first), then **STOP**. **E2E-52/P3-10 IS CLOSED AND NOTHING FURTHER IS AUTHORIZED** — do NOT touch the line-99 `PUT FILE(OUTPUT)` blocker, no P3-11, no `REVERT ERROR`, no PLILIB/MIR, no oracle, no runtime claims; a NEW operator brief is required for any further subround.

**STATE:** ledger ENDS **C368**; inventory **1269/187**; coverage **142 rows, SUPPORTED 92**, 0/0; gate rc=0 at HEAD (`build/gate-e52p10-reg.log`); binary `a4c0e235ed4bb81fe284…` == tree; goldens NEVER re-derived; census `0198fe5` 15/0/26/0 with LOAN2 blocker VERBATIM `codegen: PUT FILE(OUTPUT) has no byte-exact DR witness [TBD] (line 99)` (rc=2, NO .REL, NEVER fix); `pli80c` POSITIONAL into FRESH paths; ALWAYS `git diff --cached --stat` before commit; tree clean except guard blocks + operator config (NEVER stage) + ignored `build/e52p10*/`, `ocaml/_build-e52p10/`, `ocaml/*.log`; chain 01a1b069 renewal 3/12 cap 12; no push; all rc DIRECT.

SUPERSEDED-BY-ABOVE: ## Next action (E2E-52/P3-10 hop 3 PART DONE — AST TEST `91060ea` + REGISTRATION `21d4db6` (1269/187) + CENSUS `0198fe5` LANDED; C368 -> COVERAGE -> GATE -> CLOSE OWED; read `LEARNINGS.md` § "P3-10 hop 3 PART" FIRST — it contains the FULLY DRAFTED C368 text; STOP at P3-10 closure)

**DONE this hop (session 01a1b09a, chain 01a1b069 renewal 2/12; ZERO oracle; goldens NEVER touched; config NEVER staged; no push; all rc DIRECT):** recovery verified HEAD `75da3be`, build rc=0 binary `a4c0e235ed4bb81fe284…` == tree. (1) AST-preservation proto test `ocaml/proto/ssignal_ast.ml` + dune stanza (arch1 precedent): parse-level asserts cargs/target PRESERVED on WA-bare/WC/WD/WE(256)/WH/WI AND still-refused WG `error(n)`, WF `error(1+1)`, multi `error(1,2)`, FROM bare+args, WL bare-file — **12/12 PASS, build+run rc=0**, commit `91060ea`. (2) registration commit `21d4db6`: SPECIMENS +9 (E52WA-WE,WH-WK; per-probe measured comments from FIRST-HAND raw-record re-verification), `E52WL` enters REJECTS as **genuine dr-refuse** (decision recorded honestly; precedent SF/SG; VERBATIM `SYNTAX ?` PASS 2 line 12; marker `SIGNAL endfile with 0 argument(s)` RE-MEASURED rc=2 under the gate's CRLF+bare-^Z materialization — LF-only shifts 12->6, hop-2 lesson re-confirmed); WF/WG NOT registered (my-gap single witnesses, H-D2 no-generalise); `--update-inventory` -> **1269 specimens (+9 exactly)/187 refusals (+1)**, every added line inspected, config NEVER staged. (2b) census OWN path commit `0198fe5`: rc=0, counts UNCHANGED 15/0/26/0, LOAN2 message MOVED VERBATIM to line-99 `PUT FILE(OUTPUT)` blocker, EXPR1/EXPR2 unchanged, NOTHING fixed.

**EXECUTE (successor hop 3 remainder, in order):** (3) re-spot-check 2-3 cited bytes vs `build/e52p10/E52W*-reldump.txt` + `e52p10-signals-disasm.txt`, then append the DRAFTED C368 (verbatim text + bullet contract in `LEARNINGS.md` § "P3-10 hop 3 PART", STILL-OWED block) to `spec/CLAIMS.md` and commit — **measured-bytes-only, BEFORE ANY `spec/COVERAGE.tsv` touch**. (4) `COND.SIGNAL` row SUPPORTED/**EXACT:9** in `spec/COVERAGE.tsv` + EXPLICIT `spec/COVERAGE-IDS.txt` line (NEVER `coverage_gen.py`; **15 cols from FIRST NON-COMMENT row**; csv `delimiter='\t'`; verify diff ≈ 2 lines BY CONTENT); `python3 tools/coverage_check.py` rc=0 expect **142 rows 0/0 SUPPORTED 92**; `python3 tools/file_prose_check.py` rc=0. (5) FULL gate `python3 tools/e2e_gate.py` rc=0 DIRECT (redirect to file, NEVER pipeline-tail the rc) -> `build/gate-e52p10-reg.log`; expect **1269/0, 187/187, 9/9, 142 rows 0/0, census 15/0/26/0, prose 5**. (6) RESULTS §P3-10 (per-probe table; H-A/B0/B2/C255/E1/E2/F/G HIT; WE 0..255-falsifier VERBATIM; WL dr-refuse verdict; WF/WG single-witness NO-generalise; LOAN2 advance 92->99 VERBATIM NEVER fix; stale-binary lesson; byte-tier-only) + PLAN §5 row + §P3-10 **CLOSED** + durables. **STOP at P3-10 — do NOT implement the line-99 `PUT FILE(OUTPUT)` blocker, no P3-11, no runtime claims.**

**STATE:** HEAD at this durables commit; ledger ENDS **C367** (C368 owed, TEXT DRAFTED in LEARNINGS); inventory **1269/187**; coverage 141/SUPPORTED 91 (COND.SIGNAL owed -> 142/92); binary `a4c0e235ed4bb81fe284…` == tree; goldens NEVER re-derived; `pli80c` POSITIONAL into FRESH paths; tree clean except guard blocks + operator `handoff.config.json` (NEVER stage) + ignored `build/e52p10*/`, `ocaml/_build-e52p10/`, `ocaml/*.log`; chain 01a1b069 renewal 2/12 cap 12; no push; rc DIRECT.

SUPERSEDED-BY-ABOVE: ## Next action (E2E-52/P3-10 hop 2 LANDED — CAMPAIGN MEASURED 11 ok/12 + ARM BYTE-EXACT 9/9; AST TEST + REGISTRATION + C368 + GATE + CLOSE OWED; read `LEARNINGS.md` § "P3-10 hop 2" FIRST; STOP at P3-10 closure)

**DONE this hop (session 01a1b085, fresh chain renewal 1/12; ZERO ocaml byte BEFORE goldens; goldens NEVER touched; config NEVER staged; no push; all rc DIRECT):** campaign `e52p10` rc=0 **11 ok/12**; every .PRN read (11× `NO ERROR(S)` both passes; **WL dr-refuses**: PASS 2 line 12 `SYNTAX`, NO .REL, kept VERBATIM, no invented golden). Raw-record decode of all 11 goldens: H-A/H-B0/H-B2/H-C255 HIT; **WE falsifies the 0..255 compiler-range competitor** (error(256) = `21 00 01`, full 16-bit verbatim); WF accepted UNFOLDED via stack `?DLDOP×2/?DADOP/?QDI15` + `AF`+CALL and WG accepted via `LHLD`+`AF`+CALL — both SINGLE witnesses, armed NEITHER (open my-gap [TBD]); H-E1 HIT (PF 0024), **H-E2 HIT `3E 05` — SIGNAL A byte tracks ON codes [C120]**; H-F/H-G HIT. Goldens VERBATIM `d46b6c2` BEFORE any ocaml byte. Frontend repair + arm `d84665c`: `Ssignal` gains `cargs` (parser stops discarding; bind 574/1518 + pli80deps traverse; FROM kept never lowered); `signal_error_prefix` OWN encoder; arm admits ONLY measured shapes (ERROR bare/literal 0..65535; endpage(f) 08, endfile(f) 05 via `on_reg_prefix` + `?SIGOP`; pure statement, no C3/pad/SP-cell). VERIFIED binary `a4c0e235ed4bb81fe284…`: build rc=0 DIRECT, histogram codegen 68/total 124, 9/9 cmp whole-file (WA-WE,WH-WK), sweep FAILS 0, markers 10/10, regressions 17/17, **LOAN2 ADVANCED VERBATIM to `codegen: PUT FILE(OUTPUT) has no byte-exact DR witness [TBD] (line 99)` NEVER fix**; EXPR1 21/EXPR2 35 unchanged. LESSON: a pipeline-tail `| head` hid the first build rc → STALE `_build/default` binary FALSE-REFUSED WK; re-verify one cmp on the binary you trust.

**EXECUTE (successor hop 3, in order):** (1) AST-preservation test (owed from brief step 2): `ocaml/proto/ssignal_ast.ml` + dune stanza (arch1.ml precedent) asserting `cargs` PRESERVED on `signal error;`, `error(1)`, `endpage(pf)`, `error(1,2)` and FROM forms — including still-REFUSED shapes; build rc=0; commit explicit paths. (2) registration from **1260**: SPECIMENS +9 (WA-WE,WH-WK ONLY — WF/WG are my-gap refusals, NOT dr-refuses; DECIDE honestly + record whether WL enters REJECTS as a genuine dr-refuse citing its VERBATIM `SYNTAX` verdict, precedent SF/SG — refusals 186→187 ONLY if registered), `--update-inventory`, ALWAYS `git diff --cached --stat` (config NEVER staged); census OWN path (expect 15/0/26/0, LOAN2 message MOVED VERBATIM to PUT FILE(OUTPUT) line 99, NOTHING fixed). (3) **C368 measured-bytes-only committed to `spec/CLAIMS.md` BEFORE ANY `spec/COVERAGE.tsv` touch** (LEARNINGS § hop 2 table; BY-NAME perimeter incl the WF/WG single-witness clause; byte-tier-only NOT-say; provenance [C366][C120][C202][C206][C208][C367]). (4) `COND.SIGNAL` row SUPPORTED/EXACT:9 + EXPLICIT `spec/COVERAGE-IDS.txt` line (NEVER `coverage_gen.py`; 15 cols from FIRST NON-COMMENT row; csv `delimiter='\t'`); `coverage_check` rc=0 expect **142 rows 0/0 SUPPORTED 92** + prose rc=0. (5) FULL gate rc=0 DIRECT → `build/gate-e52p10-reg.log`. (6) RESULTS §P3-10 + PLAN §5 row + §P3-10 **CLOSED** + durables. **STOP at P3-10 — do NOT implement the line-99 PUT FILE(OUTPUT) blocker, no P3-11, no runtime claims.**

**STATE:** HEAD `d84665c` (+ this durables commit); ledger ENDS **C367** (C368 owed); inventory **1260/186**; coverage 141/SUPPORTED 91; binary `a4c0e235ed4bb81fe284…` == tree (intentionally != pre-arm `11c6283e…`); goldens NEVER re-derived; `pli80c` POSITIONAL into FRESH paths; tree clean except guard blocks + operator `handoff.config.json` (NEVER stage) + ignored `build/e52p10/`, `ocaml/_build-e52p10/`, `ocaml/*.log`; chain 01a1b069 renewal 1/12 cap 12; no push; rc DIRECT.

SUPERSEDED-BY-ABOVE: ## Next action (E2E-52/P3-10 hop 1 LANDED — PRE-REGISTRATION `c6c4460` committed BEFORE any oracle call and any `ocaml/` byte; ORACLE CAMPAIGN `e52p10` OWED; read `LEARNINGS.md` § "P3-10 hop 1" FIRST; STOP at P3-10 closure)

**DONE this hop (session 01a1b069, operator brief E2E-52/P3-10; ZERO oracle, ZERO `ocaml/` byte; goldens NEVER touched; config NEVER staged; all rc DIRECT; no push):** recovery verified HEAD `ec3ff7b` == brief; P3-9 close re-held. **Phase A audit COMPLETE** (PLAN sec 2 evidence table + `build/e52p10/` raw dumps): SIX SIGNAL sites in EXACTLY FOUR original objects — LOAN2 0359-035F (`signal error;` = `21 00 00` ABS / `AF` / CD slot 035E CHAIN-EXT `?SIGOP`, 7 B), EXPR1 0175+018D and EXPR2 023D+0255 (`error(1)` = `21 01 00` ABS, four BYTE-IDENTICAL 7-B sites), COPYLPT 02AA-02B4 (`endpage(printfile)` = `21`+RELOC common@0 group PRINTF / `3E 08` / CD slot 02B0, 11 B) + ON-route control COPYLPT 0254 same `3E 08` via ?ONCOP. SIGNAL is a PURE statement (no jump-over/handler/pad/SP-cell anywhere); jumps patch past it. TOOL LESSON: `build/e52p8/ondump2.py` IGNORES CLI args (hard-coded TARGETS) — driver is `build/e52p10/sigdump.py`. **Phase B LANDED `c6c4460`:** PLAN §P3-10 (H-A..H-X + falsifiers + arm contract + frontend defect record) + probes E52WA..WL (12; CRLF+bare ^Z, ≤71 cols; error(1) merged — 4 witnesses; FROM/multi-arg/other conditions NOT probed, kept unmeasured BY-NAME).

**EXECUTE (successor hop 2, in order):** (1) ONE campaign `PLI_SRC=probes timeout 900 python3 oracle/batch.py E52WA E52WB E52WC E52WD E52WE E52WF E52WG E52WH E52WI E52WJ E52WK E52WL --tag e52p10 --switches '$L$D'` rc DIRECT; read EVERY .PRN; accepted => preserve .REL VERBATIM into `golden/e52p10/` (batch writes it), reldump+sigdump every accepted region into `build/e52p10/`; refused => keep .PRN diagnostic VERBATIM, NO invented golden; commit goldens + measurements BEFORE any emitter code. (2) frontend repair AFTER evidence: `ast.ml` `Ssignal` gains `cargs : expr list`; `parser.ml` ~679 stop discarding `_sargs`; `bind.ml` 574/1518 traverse cargs; FROM kept, never lowered; test AST preservation even on still-refused forms. (3) arm codegen `Ssignal` arm per PLAN sec 5: measured shapes ONLY (bare/literal-ERROR within the WD/WE-measured range: ABS `21 lo hi` + `AF` + `call_ext "?SIGOP"`; endpage(f) via `load_file_cb` + `3E 08`; endfile(f) 05 ONLY if WI measures it; NO C3 slot/handler bytes; `st.lowered+1`, `st.last_imm <- None`; everything else refuses BY NAME [TBD]). Build rc=0 DIRECT; histogram vs codegen 68/total 124; cmp accepted probes WHOLE-FILE (positional pli80c into FRESH paths); sweep `python3 build/e52p3/sweep.py E46N E46K E51 E52 P086 R10` FAILS 0; markers harness (copy `build/e52p8-reg/markers.py`, CRLF+bare ^Z) rc=2 MARKER_FAILS 0; regressions UA..UF/VB..VK/ON ENDFILE/UNDEFINEDFILE/REVERT/IF-ELSE/FILE COMMON/STOP-CALL-RETURN/negatives 186/divergences 9/9. (4) LOAN2/EXPR1/EXPR2 POSITIONAL VERBATIM — record LOAN2's ACTUAL new first blocker (do NOT predict, NEVER fix); if LOAN2 unexpectedly emits .REL, cmp vs `golden/first/LOAN2/LOAN2.REL` and report, STOP. (5) registration from **1260** (accepted+byte-exact probes only; SPECIMENS block, `--update-inventory`, ALWAYS `git diff --cached --stat` — config NEVER staged; refusals ONLY genuine dr-refuses), census OWN path, **C368 measured-bytes-only BEFORE ANY COVERAGE touch**, `COND.SIGNAL` row + EXPLICIT `spec/COVERAGE-IDS.txt` line (NEVER `coverage_gen.py`; 15 cols from FIRST NON-COMMENT row), coverage_check+prose rc=0, FULL gate rc=0 DIRECT `build/gate-e52p10-reg.log`. (6) RESULTS §P3-10 + PLAN §5 row + §P3-10 **CLOSED** + durables. **STOP at P3-10 — do NOT implement the next LOAN2 blocker, no P3-11, no REVERT ERROR, no runtime claims.**

**STATE:** HEAD `c6c4460`; ledger ENDS **C367**; inventory **1260/186**; coverage 141/SUPPORTED 91 0/0; binary `11c6283e75b60fe3…` == tree; goldens NEVER re-derived; tree clean except operator `handoff.config.json` (NEVER stage) + ignored `build/e52p10/`, `ocaml/*.log`; `pli80c` POSITIONAL into FRESH paths; all rc DIRECT; no push; this session = fresh operator-launched chain (prior chain 01a1af4f closed).

SUPERSEDED-BY-ABOVE: ## Next action (E2E-52/P3-9 hop 7 CLOSE COMPLETE — **SUBROUND P3-9 FULLY CLOSED**; ONLY the guard-block commit remains; then STOP, nothing authorized)

**DONE (this successor session, chain 01a1af4f renewal 4/12; ZERO oracle; goldens NEVER touched; config NEVER staged; all rc DIRECT; no push):** g410 blocks VERBATIM `8ada736`; build rc=0 binary `11c6283e75b60fe3…` == tree; **(3)** `COND.OR` row SUPPORTED/EXACT:11 (probes E52VA..VK, corpus LOAN2,ANNUITY, provenance [C367][C105][C155][C366]) + EXPLICIT IDS line, NEVER `coverage_gen.py`, column count from the FIRST NON-COMMENT row (15) — commit `7da60b5`, `coverage_check` rc=0 **141 rows 0/0 SUPPORTED 91**, prose rc=0 (evidence `build/e52p9-hop7/`); **(4)** FULL gate rc=0 DIRECT `build/gate-e52p9-reg.log` — **1260/0, 186/186, 9/9, 141 rows 0/0, census 15/0/26/0, prose 5**, every pre-registered number HIT; **(5)** RESULTS §P3-9 + PLAN §5 P3-9 row + §P3-9 **CLOSED** heading — commit `66cb943`, prose rc=0 (all falsifiers VERBATIM incl. RB by VB==VC, SN/LB by VE/VF-node1 `2A` heads, PAR, hop-4/5 LITERAL-FIRST with the VG/VI first-attempt cmp FAILs adjudicated by the VAR-FIRST refit, EVERY §4 CODE-size SHORT miss VA 0014→001C / VB VC VD 001F→0026 / VE 0024→002C / VF 0034→003C / VG 0038→0047 / VH 002C→002F / VJ 001E→0025, hop-4 VI 001B falsified, LOAN2 line-92 PREDICTED=MEASURED NEVER fix, byte-tier-only, O-1 panel-unverified); **(6)** this durables append (LEARNINGS § "hop 7 CLOSE").

**EXECUTE (successor — the ONLY remaining step):** commit the guard-refreshed managed blocks in HANDOFF.md/PROGRESS.md VERBATIM (explicit paths, NEVER hand-edit, NEVER stage `handoff.config.json`, ALWAYS `git diff --cached --stat` first), then **STOP**. **E2E-52/P3-9 IS CLOSED; NOTHING FURTHER IS AUTHORIZED** — do NOT start P3-10 / `signal error` / `?SIGOP` (PROPOSED only; a new operator brief is required), no oracle, no PLILIB/MIR, no push.

**STATE:** ledger ENDS **C367**; inventory **1260/186**; coverage **141 rows, SUPPORTED 91**, 0/0; gate rc=0 at HEAD (`build/gate-e52p9-reg.log`); binary `11c6283e75b60fe3…`; goldens NEVER re-derived; census `b080894` 15/0/26/0 with LOAN2 blocker VERBATIM `codegen: statement kind not in supported subset [TBD] (line 92)` (rc=2, NO .REL, NEVER fix); tree clean except operator `handoff.config.json` + ignored scratch; `pli80c` POSITIONAL into FRESH paths; chain 01a1af4f 5/12 cap 12; no push; all rc DIRECT.

SUPERSEDED-BY-ABOVE: ## Next action (E2E-52/P3-9 hop 7 PART DONE — C367 LANDED `eaa5ef3`; COND.OR COVERAGE ROW + GATE + RESULTS/PLAN CLOSE OWED; read `LEARNINGS.md` § "hop 7 (this session 01a1af94)" FIRST; STOP at P3-9 closure)

**DONE THIS HOP (session 01a1af94, chain 01a1af4f renewal 3/12; ZERO oracle; goldens NEVER touched; config NEVER staged; all rc DIRECT; no push):** g406 blocks committed VERBATIM `16d3db7`; build rc=0 binary `11c6283e75b60fe3…` == STATE; **11/11 E52VA..VK cmp rc=0 re-verified FIRST-HAND** into FRESH `build/e52p9-hop7/out/` (`parity.txt`); every C367 byte re-read first-hand from the raw reldump records; **C367 measured-bytes-only committed `eaa5ef3` BEFORE any COVERAGE touch**, prose rc=0. **NOT LANDED:** the `COND.OR` row — my csv script took the column count from comment LINE 1 of `spec/COVERAGE.tsv` (n=1), its assertion fired BEFORE any write, so the ledger and the IDS manifest are UNMODIFIED (`coverage_check` still 140 rows 0/0 SUPPORTED 90). Context went critical at this step; this session RENEWES.

**EXECUTE (successor, in order):** (3) append `COND.OR` to `spec/COVERAGE.tsv` (SUPPORTED, `EXACT:11`, probes `E52VA,E52VB,…,E52VK`, corpus `LOAN2,ANNUITY`, law text from [C367], boundary = my BY-NAME refusals (`<0`-first-in-3+-chain, cross-var rule-2, ladder k>=3, value-position DEC, other operand classes) + And-route untouched + LOAN2 still refuses at line 92 (`?SIGOP` UNARMED) + O-1 panel-unverified disclaimer + BYTE-TIER-ONLY NOT-say + the falsifiers (RB by VB==VC, SN/LB by VE/VF-node1 `2A` heads, PAR, hop-4/5 LITERAL-FIRST) + the census advances VERBATIM; provenance `[C367] [C105] [C155] [C366]`, confidence MEASURED) + EXPLICIT appended line `COND.OR` to `spec/COVERAGE-IDS.txt` — **NEVER `coverage_gen.py`; take the column count from the first NON-COMMENT row (15), not line 1**; verify `git diff --stat` ≈ one TSV line + one IDS line BY CONTENT, then `python3 tools/coverage_check.py` rc=0 (expect **141 rows / 0/0 / SUPPORTED 91**) + `python3 tools/file_prose_check.py` rc=0; commit explicit paths. (4) FULL gate `python3 tools/e2e_gate.py` rc=0 DIRECT -> `build/gate-e52p9-reg.log` (expect 1260/0, 186/186, 9/9, 141 rows 0/0, census 15/0/26/0, prose 5). (5) RESULTS §P3-9 + PLAN §5 row + §P3-9 CLOSED (all falsifiers VERBATIM incl. EVERY §4 CODE-size SHORT miss and the VG/VI first-attempt cmp FAILs adjudicated by the VAR-FIRST refit); prose rc=0; commit. (6) durables (`/handoff` + `/handoff ready`) + renew/finalize. **STOP at P3-9 — do NOT start P3-10/SIGNAL ERROR.**

**STATE:** HEAD after this commit; ledger ENDS **C367**; gate inventory **1260/186**; coverage panel still **140 rows** (COND.OR owed); binary `11c6283e75b60fe3…`; goldens NEVER re-derived; tree clean except operator `handoff.config.json` (NEVER stage; ALWAYS `git diff --cached --stat` before commit); `pli80c` POSITIONAL into FRESH paths; no push; all rc DIRECT; chain **01a1af4f 3/12**, cap 12.

SUPERSEDED-BY-ABOVE:  — CENSUS LANDED `b080894`; C367 → COVERAGE → GATE → RESULTS → DURABLES OWED; read `LEARNINGS.md` § "hop 6 CLOSE PART 1" FIRST (it holds the first-hand raw-byte re-verification + the three pre-registration falsifier classes), then § "hop 6 REMAINDER", § "hop 6"; STOP at P3-9 closure)

**DONE THIS HOP (session 01a1af80, chain 01a1af4f renewal 2/12; ALL rc DIRECT; ZERO oracle; goldens NEVER touched; config NEVER staged; no push):** recovery verified HEAD `a53d7e2`; build rc=0 binary `11c6283e75b60fe3a4984210…` == recorded state; 11/11 E52VA..VK cmp rc=0 re-verified into FRESH `build/e52p9-close/out/`; guard g402 blocks committed VERBATIM `618fbe6`; **step (1) CENSUS LANDED `b080894`** (prescribed OWN path `cp spec/census/corpus-census.json /tmp/census-prev-e52p9.json; python3 tools/corpus_census.py --check /tmp/census-prev-e52p9.json` rc=0; counts UNCHANGED 15/0/26/0; LOAN2 message MOVED VERBATIM to `codegen: statement kind not in supported subset [TBD] (line 92)` — PREDICTED=MEASURED, NEVER fix; EXPR1/EXPR2 unchanged). C367 byte authority re-verified FIRST-HAND from `build/e52p9-arm/goldens-dump.txt`: VAR-FIRST DEC pairs VG(pv@9→zero@0; pmt@E above F5→zero7@5)/VI(p@B→zero10@0; q@11→zero9@6; second p operand hoisted above F5, SHARED zero10 cell ✓[C155]); CODE sizes VA 001C VB/VC/VD 0026 VE 002C VF 003C VG 0047 VH 002F VI 0076 VJ 0025 VK 0080; VB==VC byte-identical 17 B; VE/VF-node1 rule-2 FULL ladder head `2A` (RB falsified by VC; SN falsified by VE); F5-sandwich mechanism PROPOSED (left truth rides in A across the right HL-only head; swapped-first operand needs no split).

**EXECUTE (successor, in order):** (2) **C367 measured-bytes-only appended to `spec/CLAIMS.md` and committed BEFORE ANY `spec/COVERAGE.tsv` touch** — full bullet contract in LEARNINGS § "hop 6 CLOSE PART 1" STILL OWED (i); include the O-1 panel-unverified disclaimer, O-2 pool parity, O-3 reloc-addr+1, literal-first+PAR falsifications, sizes from DEF records, BY-NAME perimeter, byte-tier-only NOT-say. (3) `COND.OR` SUPPORTED row (EXACT:11, probes E52VA..VK) appended to `spec/COVERAGE.tsv` (csv column-edit; NEVER `coverage_gen.py`) + EXPLICIT matching line to `spec/COVERAGE-IDS.txt`; verify `git diff --stat` ≈ two lines BY CONTENT; `python3 tools/coverage_check.py` rc=0 (~141 rows — derive from file) + `python3 tools/file_prose_check.py` rc=0. (4) FULL gate `python3 tools/e2e_gate.py` rc=0 DIRECT → `build/gate-e52p9-reg.log` (expect 1260/0, 186/186, 9/9, coverage rows 0/0, census 15/0/26/0, prose 5). (5) RESULTS §P3-9 (parity table; H-list HIT/MISS; falsifiers VERBATIM: PAR, hop-4/5 literal-first, PLAN §4 VG literal-first order, EVERY §4 CODE-size SHORT-miss list, VG/VI first-attempt cmp FAILs adjudicated by VAR-FIRST refit; LOAN2 line-92/EXPR1 21/EXPR2 35 advances; §6 byte-tier-only) + PLAN §5 P3-9 row + §P3-9 CLOSED; prose rc=0; commit explicit paths. (6) durables: `/handoff` refresh + `/handoff ready` attest, commit blocks VERBATIM, renew/finalize. **STOP at P3-9 — do NOT start P3-10/SIGNAL ERROR.**

**STATE:** HEAD after this commit; ledger ENDS **C366** (C367 owed); gate inventory **1260/186**; binary `11c6283e75b60fe3…`; goldens NEVER re-derived; tree clean except operator `handoff.config.json` (NEVER stage; ALWAYS `git diff --cached --stat` before commit); `pli80c` POSITIONAL into FRESH paths; no push; all rc DIRECT; chain **01a1af4f 2/12**, cap 12.

SUPERSEDED-BY-ABOVE: ## Next action (E2E-52/P3-9 hop 6 REMAINDER — O-1/MARKERS/SWEEP/EXPR/SPECIMENS+INVENTORY ALL LANDED; CENSUS, C367, COVERAGE, GATE, RESULTS/PLAN CLOSE OWED; read `LEARNINGS.md` § "hop 6 REMAINDER" FIRST, then § "hop 6"; STOP at P3-9 closure)

**DONE THIS HOP (session 01a1af69, chain 01a1adf0 8/12; ALL rc DIRECT; ZERO oracle; goldens NEVER touched; config NEVER staged; no push):** recovery verified HEAD `41b1165`; FULL fresh `--build-dir` rebuild deterministic, histogram **codegen 68 / total 124 == baseline**, **11/11 E52VA..VK whole-file cmp rc=0 re-verified from the COMMITTED tree** (evidence `build/e52p9-reg/parity-recheck.txt`; binary `d9e648e8c0394ea5…` pre-comment-fix — hop-6's recorded `c621ea8c…` is NOT reproducible from the tree, the CMP is the authority); **O-1 LANDED**: `build/e52p9-arm/loan2-decode.txt` raw-reldump re-derivation of :91/:113/:120 (EqVV-LATER hoist, Gt0-And-right, DEC pair VAR-FIRST with ADD-coincidence note, single-F2 geometries, NEW: the :120 then-body is ONLY `call summary();` — `m = m + 1;` sits OUTSIDE the if, no do; CHAIN-ADDR slot 0601 = `call display(...)`); EXPR1/EXPR2 POSITIONAL VERBATIM UNCHANGED (`build/e52p9-reg/expr-positional.txt`); LOAN2 rc=2 VERBATIM `(line 92)` NO .REL (`loan2-positional.txt`, NEVER fix); markers harness `build/e52p9-reg/markers.py` **10/10 MARKER_FAILS 0 rc=0**; sweep re-run on the rebuilt binary **FAILS: 0** (`sweep-arm.log`); stale-comment fix committed `1356b8b` (ODecEq0 type line literal-first→VAR-FIRST, line-preserving, zero behavior change, parity re-held; binary now `11c6283e75b60fe3…`); **registration `bdbc28a`**: SPECIMENS +11 comment+dict block in `tools/e2e_gate.py`, `--update-inventory` → **1260 EXACTLY +11 rows** (every added line inspected), refusals 186 unchanged.

**EXECUTE (successor, in order):** (1) census prescribed OWN path — `python3 tools/corpus_census.py --check <prev.json>` (this REWRITES snapshots then compares counts — expected 15/0/26/0; LOAN2 census message MOVES from the condition-form(91) text to `codegen: statement kind not in supported subset [TBD] (line 92)` VERBATIM, EXPR1/EXPR2 unchanged, NOTHING fixed); commit census artifacts explicit paths. (2) **C367 measured-bytes-only committed to `spec/CLAIMS.md` BEFORE ANY `spec/COVERAGE.tsv` touch** — content authority: LEARNINGS § hop 6 + § hop 6 REMAINDER (fold law left-assoc post-order, F5/C1/B0, ONE F2, bit7 truth, rules 1-3 NODE-LOCAL + BY-NAME refusals incl. `<0`-first-in-3+-chain and cross-var rule-2 and k>=3 and value-position DEC; FIXBIN leaf materializers; **DEC VAR-FIRST with VG/VI/LOAN2 reloc witnesses AND the literal-first falsification**; O-2 pool parity no-prescan-edit; O-3 reloc addr+1; VK precedence + BARE 32; sizes incl. VG DATA 0014 / VI 001A from DEF-DATA records; O-1 = original-golden-decode, panel-unverified for LOAN2; byte-parity ≠ runtime). (3) NEW `COND.OR` row in `spec/COVERAGE.tsv` (SUPPORTED, probes E52VA..VK) + EXPLICIT appended line to `spec/COVERAGE-IDS.txt` — **NEVER `coverage_gen.py`**; verify by CONTENT (`git diff --stat` ≈ two lines); `coverage_check.py` rc=0 (row count derive from file, ~141) + `file_prose_check.py` rc=0. (4) FULL gate `python3 tools/e2e_gate.py` rc=0 DIRECT → `build/gate-e52p9-reg.log` (expect 1260/0, 186/186, 9/9, coverage rows 0/0, census 15/0/26/0, prose 5). (5) RESULTS §P3-9 (parity table VA–VK; honest first-attempt VG/VI FAIL history adjudicated by VAR-FIRST refit; H-list HIT/MISS; PAR + literal-first falsifiers VERBATIM) + PLAN §5 row + §P3-9 CLOSED; commit docs explicit paths. (6) durables + managed blocks, renew or finalize. **STOP at P3-9 — do NOT start P3-10/SIGNAL ERROR.**

**STATE:** ledger ENDS **C366** (C367 owed); HEAD `bdbc28a`; tree clean except operator `handoff.config.json` (NEVER stage; `--update-inventory` STAGES files — ALWAYS `git diff --cached --stat` before committing; a stale config entry rode into `57fc210` and was repaired via soft-reset, never pushed); gate inventory now **1260 specimens / 186 refusals** (last full gate ran at 1249 — successor re-runs); binary `11c6283e75b60fe3…`; goldens NEVER re-derived; `pli80c` POSITIONAL `IN.PLI OUT.REL` into FRESH paths (stale outputs FALSE-PASS cmps); histogram needs FULL fresh-build-dir build (bin-only = 122, misleading); chain 01a1adf0 8/12 cap 12; no push; all rc DIRECT.

SUPERSEDED-BY-ABOVE: ## Next action (E2E-52/P3-9 hop 5 — ARM `ocaml/lib/codegen.ml` ONLY, then verify/register/close and STOP; read `LEARNINGS.md` § "hop 5 PART 6" FIRST (the FINAL plan + obligations), then § "hop 5 PART 4" (corrections), § "hop 5 PART 3" (algorithm), § "hop 5 PART 2" (emission lists); execute; STOP at P3-9 closure)

**DONE THIS HOP (session 01a1ae54, chain 01a1adf0 renewal 5/12; all rc DIRECT; ZERO `ocaml/` byte, ZERO oracle):** build rc=0 binary `9ecea27aa4f2d80f49ad…` == baseline; goldens-dump re-read IN FULL — all VA–VK regions re-confirmed against PART 2/3 lists; probe condition lines re-extracted; THREE CORRECTIONS written to LEARNINGS § hop 5 PART 4: (1) `is_plain_bin_auto` does NOT exist — use `is_plain_num_auto` @4040 + own `Eident` name extraction; (2) `hl_bias`/`cmp_load_deref` are AFTER `lower_bool` @7276 — fold machinery MUST be placed BEFORE lower_bool using inline `op_lhld/reloc` + literal byte sequences only; (3) fold GtC ladder gated k∈{1,2} (DCX×(k+1) witnessed; k≥3 in-fold refuses BY NAME [TBD]). Anchors re-pinned: And test-arm @8528-8531 (Or arm goes right after); Lt TEST arm @8628-8641 (`<0` leaf arm goes BEFORE it; textual `Enumber "0"` match, no int_lit_checked); bit_cond_mat @8105 ends `| _ -> None` @~8316, caller BARE `32 STA` @~9962; prescan parity re-confirmed, NO edit; DEC literal-first via `dec_pool` manual `21 r(zero)/3E p/?DLDOP/21 r(var)/3E p/?DLDOP/?DCMOP/D6 01 9F`, NEVER `dec_eq_bool_parts`.

**HOP 5 PART 7 (session 01a1ae80, renewal 7/12, CLOSING at pressure; ZERO `ocaml/` byte remains):** recovery verified HEAD `1318891`, g395 guard blocks committed `284e178`, build rc=0 binary `9ecea27aa4f2d80f49ad…` == baseline. ALL 8 PART 6 anchor sites re-pinned on THIS tree; the COMPLETE ready-to-run arm splice is saved at `build/e52p9-arm/arm-splice.py` (idempotent, asserts every anchor, backs up to `codegen.ml.pre-splice`; contents = PART 6 plan items 1–7 exactly: or_cls/or_classify/or_head/or_tail/collect_or + let-rec-and `lower_or`, lower_bool Or arm beside And + leaf arms after DEC-Eq/`Eq ident 0` before catch-all, And-right saved clause after DEC clause (OAnd/OGroup excluded), TEST Or arm + `<0` TEST arm `3A r(v+1)/B7/F2` before the Lt arm, bit_cond_mat arm `~allow_dec:false`). LESSON (accepted): codegen.ml anchors containing backtick/apostrophe pairs fail edit-tool exact matching — use Python line-equality splices. Renewal NOT available (g395 already seeded this successor) — finalized at this boundary.
**EXACT NEXT (successor):** (a) `python3 build/e52p9-arm/arm-splice.py`; (b) `cd ocaml && eval "$(opam env)" && dune build` rc DIRECT (fix ONLY syntax if any; NEVER alter And bytes); then steps (3)–(5) below unchanged (histogram 68, cmp VA–VK whole-file, sweep, markers, LOAN2/EXPR1/EXPR2 POSITIONAL — predicted `signal error` 92 NEVER fix — O-1 loan2-decode re-derivation, registration 1260, C367 BEFORE COVERAGE, gate, RESULTS/PLAN/CLOSED, STOP at P3-9). Full details LEARNINGS § "hop 5 PART 7".
**EXECUTE (successor, hop-5 steps (2)–(5)):** (2) arm `ocaml/lib/codegen.ml` ONLY per **LEARNINGS § "hop 5 PART 6" — the FINAL ARM PLAN (placement, class list with exact bytes, node1 rules, the seven edit sites, obligations O-1/O-2/O-3)** alongside § PART 4 corrections + § PART 3 algorithm + § PART 2 emission lists. PART 6 NEW accepted facts: LOAN2 `P fixed dec(10,2)` ⇒ LOAN2:113 witnesses **EqVV in a LATER fold slot** and :120 witnesses **Gt0 as And-right**; fold DEC operands emit via the classifier DIRECTLY (lower_bool's DEC arms are VAR-first — never dispatch fold DEC through them); bit_cond_mat Or arm uses `~allow_dec:false`. O-1: LOAN2/ANNUITY fold regions are original-golden-decode, panel-unverified — re-derive LOAN2 113/120 via reldump into `build/e52p9-arm/loan2-decode.txt`, record under C367; probes VA–VK cmps are the binding authority. (3) `cd ocaml && eval "$(opam env)" && dune build` rc=0 DIRECT + per-File warning histogram vs **68** + cmp VA–VK whole-file vs `golden/e52p9/` + `python3 build/e52p3/sweep.py E46N E46K E51 E52 P086 R10` FAILS 0 + markers harness (copy `build/e52p8-reg/markers.py`, CRLF + bare `^Z`) + LOAN2/EXPR1/EXPR2 POSITIONAL VERBATIM (predicted LOAN2 blocker `signal error` 92, NEVER fix). (4) registration from 1249 (SPECIMENS +11, `--update-inventory` → **1260**, refusals 186, census OWN path, **C367 measured-bytes-only BEFORE COVERAGE**, new `COND.OR` row + EXPLICIT `spec/COVERAGE-IDS.txt` line, NEVER `coverage_gen.py`), coverage_check+prose rc=0, gate rc=0 `build/gate-e52p9-reg.log`. (5) RESULTS §P3-9 + PLAN §5 row + §P3-9 CLOSED, durables. **STOP at P3-9 — do NOT start P3-10/SIGNAL ERROR.**

**STATE:** ledger ENDS **C366**; gate 1249/186/9/140-0-0 SUPPORTED 90, census 15/0/26/0; binary `9ecea27aa4f2d80f49ad…`; goldens NEVER re-derived; no push; `handoff.config.json` NEVER staged; all rc DIRECT; `pli80c` POSITIONAL; chain 01a1adf0 **5/12** (cap 12).

SUPERSEDED-BY-ABOVE: ## Next action (E2E-52/P3-9 hop 5 REMAINDER — ARM codegen.ml ONLY; the FULL final arm design is in `LEARNINGS.md` § "hop 5 PART 3" (newest) + emission lists in § "hop 5 PART 2"; read BOTH, then execute; STOP at P3-9 closure)

**DONE this hop (session 01a1ae44, chain 01a1adf0 renewal 4/12; all rc DIRECT; ZERO `ocaml/` byte, ZERO oracle):** build rc=0 binary `9ecea27aa4f2d80f49ad…` == baseline; goldens-dump + all 11 probes re-read; EVERY arm site verified on THIS tree and the fold mechanism fully understood (`is_plain_bin_auto` @3980 = the ready operand gate; And test-arm @8526; `EqR Lt` refusal arm @8629; `lower_bool` @7276 ends fold at 7337; `bit_cond_mat` @8105, caller STA @9962; DEC materialiser via `dec_pool` literal-first, prescan parity CONFIRMED — no prescan edit; PUSH-PSW/POP-B flag-byte mechanism explained; full fold algorithm + operand classifier + registration subset (1249→1260, 186 unchanged) written to LEARNINGS § hop 5 PART 3). The ARM EDIT ITSELF IS STILL OWED — pressure stopped this session before any codegen change.

**EXECUTE (successor, steps (2)–(5) of the hop-5 contract):** (2) arm `ocaml/lib/codegen.ml` ONLY per LEARNINGS § "hop 5 PART 3" (Or test-arm after @8529; VA `<0` TEST arm before @8629; `Ast.Or` fold arm in lower_bool beside And; `or_operand` classifier — Lt0 atomic `3A r(v+1)`, GtC head `cmp_load_deref; hl_bias(-(k+1))`+tail `7C 2F`, Eq0 `val_addr`+`bin_zero_tail`, Gt0 `val_addr`+`AF BE 23 9E`, EqVV head `2A r(l)`/tail `E5/2A r(r)/D1/?IS22N/7C/B5/D6 01 9F`, DEC literal-first NEW materialiser — NEVER edit `dec_eq_bool_parts`; node-local rules 1–3 with node1 swap, `a<0|x|y` n≥3 refuses, cross-var rule-2 refuses BY NAME; `C1 B0 (0xB0)` fold; NEVER alter And bytes). (3) build rc=0 DIRECT + histogram vs 68 + cmp VA–VK whole-file vs `golden/e52p9/` + sweep `python3 build/e52p3/sweep.py E46N E46K E51 E52 P086 R10` FAILS 0 + markers harness (copy `build/e52p8-reg/markers.py`, CRLF + bare `^Z`) + LOAN2/EXPR1/EXPR2 POSITIONAL VERBATIM (predicted blocker `signal error` 92, NEVER fix). (4) registration from 1249 (SPECIMENS +11, `--update-inventory`, census OWN path, **C367 measured-bytes-only BEFORE COVERAGE**, new `COND.OR` row + EXPLICIT `spec/COVERAGE-IDS.txt` line, NEVER `coverage_gen.py`), coverage_check+prose rc=0, gate rc=0 `build/gate-e52p9-reg.log`. (5) RESULTS §P3-9 + PLAN §5 row + §P3-9 CLOSED, durables. **STOP at P3-9 — do NOT start P3-10/SIGNAL ERROR.**

**STATE:** ledger ENDS **C366**; gate 1249/186/9/140-0-0 SUPPORTED 90, census 15/0/26/0; binary `9ecea27aa4f2d80f49ad…`; goldens NEVER re-derived; no push; `handoff.config.json` NEVER staged; all rc DIRECT; `pli80c` POSITIONAL; chain 01a1adf0 **4/12** (cap 12); HEAD = durables commit atop `5f3a281`.

SUPERSEDED-BY-ABOVE: ## Next action (E2E-52/P3-9 hop 5 — ARM `ocaml/lib/codegen.ml` ONLY, then verify/register/close and STOP; read `LEARNINGS.md` § "hop 5 PART 2" FIRST — it holds the arm-time verified facts, the exact per-probe emission lists and the five arm-time decisions — then § "hop 5 REMAINDER" for the corrected DEC-operand finding)

**DONE (verified this hop, session 01a1ae33, chain 01a1adf0 renewal 4/12 after checkpoint g385-422366900219 attested; all rc DIRECT; ZERO `ocaml/` byte, ZERO oracle):** recovery re-verified — HEAD `0c62d1f` (guard g384 blocks atop durables `48a5fc2`), tree clean but operator `handoff.config.json` (NEVER staged) + ignored `ocaml/*.log`; `dune build` rc=0 DIRECT, binary `9ecea27aa4f2d80f49ad…` == baseline; `build/e52p9-arm/goldens-dump.txt` (751 lines) and ALL 11 `probes/E52V*.PLI` re-read in full; `golden/e52p9/` holds all 11. Arm-time facts ACCEPTED by code reading (see the LEARNINGS § "hop 5 PART 2"): parser is LEFT-assoc precedence-climbing with `Or=10 < And=20 < rel=30` (VK parses exactly as measured); `F5` saves the LEFT truth byte in **A**, so only HL-only prefixes (`21`/`2A` + `hl_bias`) are hoistable and `3A` is atomic — the mechanism behind rule 1; DEC `=0` OR operand = `dec_push(literal)` then `dec_push(var)` then `?DCMOP`/`D6 01`/`9F`, and `dec_pool`/`dec_cell_addr` REUSES the cell `prescan_cond` already demands for `Or` (parity holds, no prescan edit); insertion points pinned — Or test-arm beside And @**8526**, Or fold beside And in `lower_bool` @**7276**, new `<0` TEST arm **BEFORE** the `EqR Lt` arm @**~8630** (whose refusal `codegen: < 0 / negative const form unproven [TBD]` must survive for non-auto operands), value-position arm in `bit_cond_mat` @**8105** (`32 STA` stays at the caller @~9963). LOAN2 91/92/113/120 re-read verbatim; E52VB still refuses rc=2 with the catch-all at **9154** (nothing armed).

**EXECUTE (in order):** (2) arm `ocaml/lib/codegen.ml` ONLY — `Ast.Or` arm in `lower_test_skip0` BESIDE And (`lower_bool st c; d st op_jp; slot`), `Ast.Or` fold arm BESIDE And in `lower_bool` with `C1 POP B / B0 ORA B (0xB0)`, VA `<0` TEST leaf (`3A r(cell+1)/B7/F2`, plain `Vint` auto only), rules 1–3 NODE-LOCAL per the LEARNINGS emission lists (rule 2 same-var FIXBIN `=0`-then-`>c` ONLY, other-var refuses BY NAME [TBD]; `a<0|b|c` has no witness → refuse), separate OR DEC materialiser (literal-first — NEVER edit `dec_eq_bool_parts`), VK precedence + value-position BARE `32`, **NEVER alter And bytes**; record the ADD-vs-literal-first and hoist-placement ambiguities for C367. (3) build rc=0 DIRECT + histogram vs **68** + cmp VA–VK whole-file vs `golden/e52p9/` (first-mismatch offsets honest) + `python3 build/e52p3/sweep.py E46N E46K E51 E52 P086 R10` FAILS 0 + markers harness (copy `build/e52p8-reg/markers.py`, CRLF + bare `^Z`) + LOAN2/EXPR1/EXPR2 POSITIONAL VERBATIM (predicted LOAN2 blocker = `signal error` at 92, `?SIGOP` out of scope, NEVER fix). (4) registration from **1249** (`--update-inventory`, census OWN path, **C367 measured-bytes-only BEFORE COVERAGE**, new `COND.OR` row + EXPLICIT `spec/COVERAGE-IDS.txt` line, NEVER `coverage_gen.py`), coverage_check+prose rc=0, gate rc=0 `build/gate-e52p9-reg.log`. (5) RESULTS §P3-9 + PLAN §5 row + §P3-9 CLOSED, durables. **STOP at P3-9 — do NOT start P3-10/SIGNAL ERROR.**

**STATE:** ledger ENDS **C366**; gate 1249/186/9/140-0-0 SUPPORTED 90, census 15/0/26/0; binary `9ecea27aa4f2d80f49ad…`; goldens NEVER re-derived; no push; `handoff.config.json` NEVER staged; all rc DIRECT; `pli80c` POSITIONAL; chain 01a1adf0 **4/12** (cap 12); durables HEAD `8e86ad2` (dis80 fix `8b929d7`, hop-5 prose `48a5fc2`).

SUPERSEDED-BY-ABOVE: ## Next action (E2E-52/P3-9 hop 5 REMAINDER — ARM ONLY, then verify/register/close and STOP; read `LEARNINGS.md` § "hop 5 REMAINDER IN FLIGHT" FIRST — it carries the corrected DEC-operand finding and every measured byte)

**DONE (verified this session, all rc DIRECT; session 01a1ae1e, chain 01a1adf0 renewal 2/12):** recovery verified HEAD `8b929d7`; hop-5 step (1) "commit dis80 fix" is **already LANDED** there (`git status` clean but for the guard blocks + operator `handoff.config.json`, NEVER staged). `dune build` rc=0 DIRECT, binary `9ecea27aa4f2d80f49ad…` == baseline; ZERO `ocaml/` byte, ZERO oracle. Raw dump `build/e52p9-arm/goldens-dump.txt` + all 11 probe sources re-read and confirmed against the hop-5 PART byte list.

**FALSIFIED (accepted finding, blocks a naive arm):** the predecessor's design step "reuse/extend `dec_eq_bool_parts` … literal-first" is WRONG — `codegen.ml:7249` hoists the **VARIABLE** `21 r(var)` (AND route, DECPOLY/R2026), while the OR witnesses VG/VI put the **POOLED LITERAL** cell first (`21 r(zero) / 3E p / ?DLDOP / 21 r(var) / 3E p / ?DLDOP / ?DCMOP / D6 01 9F`). Arming needs a SEPARATE OR DEC materialiser; NEVER edit `dec_eq_bool_parts` (it would alter And). PROPOSED (unverified): implement it address-ordered per the residual **ADD** law and let VG/VI + the DECPOLY AND goldens adjudicate; record the ambiguity in C367.

**EXECUTE (in order):** (2) arm `ocaml/lib/codegen.ml` ONLY: `Ast.Or` arm in `lower_test_skip0` BESIDE And (And arm at line **8527**), `Ast.Or` fold arm BESIDE And in `lower_bool` (7276) with `C1 POP B / B0 ORA B (0xB0)`, `<0` standalone TEST leaf (VA `3A r(cell+1)/B7/F2`; refusal site 8635), rules 1–3 NODE-LOCAL (rule 2 same-var `=0|>c` only; other-var refuses BY NAME [TBD]), encoders `2A…/hl_bias(-(k+1))/7C 2F`, `bin_zero_tail`, `21/AF/BE/23/9E` for `> 0`, atomic `3A` for `<0`, ident-vs-ident `=` via `2A/E5/2A/D1/?IS22N/7C/B5/D6 01/9F`; VK `a|(b&c)` = AND sandwich first, `(a|b)&c` = OR fold then And sandwich, value position = OR fold then BARE `32 r(b)` (audit `bit_cond_mat` 8105; refuse anything outside VK); NEVER alter And. (3) build rc=0 DIRECT + histogram vs **68** + cmp VA–VK whole-file vs `golden/e52p9/` + `python3 build/e52p3/sweep.py E46N E46K E51 E52 P086 R10` FAILS 0 + markers harness (copy `build/e52p8-reg/markers.py`, CRLF + bare `^Z`) + LOAN2/EXPR1/EXPR2 POSITIONAL VERBATIM (predicted next blocker `signal error` at 91, `?SIGOP` out of scope, NEVER fix). (4) registration from **1249** (`--update-inventory`, census OWN path, **C367 measured-bytes-only BEFORE COVERAGE**, explicit `spec/COVERAGE-IDS.txt` line, NEVER `coverage_gen.py`), gate rc=0 `build/gate-e52p9-reg.log`. (5) RESULTS §P3-9 + PLAN §5 row + §P3-9 CLOSED, durables. **STOP at P3-9 — do NOT start P3-10.**

**STATE:** ledger ENDS **C366**; gate 1249/186/9/140-0-0 SUPPORTED 90, census 15/0/26/0; binary `9ecea27aa4f2d80f49ad…`; goldens NEVER re-derived; no push; `handoff.config.json` NEVER staged; all rc DIRECT; `pli80c` POSITIONAL; chain 01a1adf0 2/12 (cap 12).

SUPERSEDED-BY-ABOVE: ## Next action (E2E-52/P3-9 hop 5 PART — dis80 FIXED+VERIFIED (UNCOMMITTED), ALL 11 golden folds RAW-DERIVED, exact arm design in `LEARNINGS.md` § "E2E-52/P3-9 hop 5 PART" — read it FIRST; then commit dis80, ARM, verify, register, close P3-9, STOP)

**DONE THIS HOP (session 01a1ae0d, chain 01a1adf0 renewal 1/12; ZERO `ocaml/` byte, ZERO oracle):** build rc=0 binary `9ecea27aa4f2d80f49ad…` == baseline re-held; `tools/dis80.py` minimally fixed (`0xD6 SUI` len2, `0x2F CMA` len1) and VERIFIED linear on E52VE/VG/VI; every VA–VK fold region re-derived byte-for-byte from raw reldump records into `build/e52p9-arm/goldens-dump.txt`; all 11 probe sources re-read; prescan parity audited (`prescan_cond` descends `Or` generally, DEC zero-cell demand fires); full arm design (operand encoders, rules 1–3 node-local, `ORA B 0xB0` fold, VK precedence/value-position, refuse-BY-NAME perimeter) recorded ACCEPTED/PROPOSED in the LEARNINGS hop-5 section.

**EXECUTE NEXT (hop 5 remainder):** (1) commit `tools/dis80.py`; (2) arm `ocaml/lib/codegen.ml` ONLY per that design (Or test-arm beside And in `lower_test_skip0` @8526 + Or fold beside And in `lower_bool`; NEVER alter And bytes); (3) build rc=0 DIRECT + histogram vs 68 + cmp VA–VK whole-file vs `golden/e52p9/` + sweep `python3 build/e52p3/sweep.py E46N E46K E51 E52 P086 R10` FAILS 0 + markers harness (CRLF+bare ^Z) + LOAN2/EXPR1/EXPR2 POSITIONAL VERBATIM (LOAN2 predicted next blocker `signal error` body at 91 — ?SIGOP out of scope, NEVER fix); (4) registration from 1249 (--update-inventory, census OWN path, **C367 measured-bytes-only BEFORE COVERAGE**, explicit `spec/COVERAGE-IDS.txt` edit, NEVER coverage_gen.py), gate rc=0 `build/gate-e52p9-reg.log`; (5) RESULTS §P3-9 + PLAN §5 row + §P3-9 CLOSED, durables. STOP at P3-9 closure — do NOT start P3-10.

**STATE:** HEAD `8c099a0`; ledger ENDS C366; gate 1249/186/9/140-0-0 census 15/0/26/0; binary `9ecea27aa4f2d80f49ad…`; UNCOMMITTED: `tools/dis80.py` + this hop's LEARNINGS/PROGRESS prose; goldens untouched; no push; `handoff.config.json` NEVER staged; all rc DIRECT.

SUPERSEDED-BY-ABOVE: ## Next action (E2E-52/P3-9 hop 4 PART DONE — order-law CANDIDATE PINNED from raw bytes (left-assoc chain, push-left/compute-right, `<0`-LAST, same-var `=0|>c` ladder-first swap, else source order); DEC literal-first CONFIRMED, PAR dead; dis80 D6/2F fix identified; ARM OWED at hop 5 — read `LEARNINGS.md` section "E2E-52/P3-9 hop 4 PART" FIRST, it holds every measured byte and the exact arm contract)

**DONE THIS HOP (session 01a1adf0; ZERO `ocaml/` byte, ZERO oracle, goldens untouched; all rc DIRECT):** recovery verified (HEAD `42d91094` == brief, g377 attested, hashes replayed — GOAL/LEARNINGS/config match, PROGRESS/HANDOFF differ only by the guard's own block rendering; no renewal-state file — fresh chain, operator-launched session). RAW-hex evidence table built from `build/e52p9/vdumps.txt`+`reldumps.txt` + fresh `tools/reldump.py` record dumps for VB–VK + LOAN2 91/113/120 + ANNUITY 46: **the hop-3 UNRESOLVED fold-ORDER question is now candidate-pinned** — left-assoc post-order fold, LEFT truth byte `F5`-pushed, RIGHT computed after push then `C1 POP B / B0 ORA B`, ONE terminal `F2 JP`; rule 1: `<0` LDA operand computed LAST in its node (VB==VC byte-identical, VD separate-var, VJ, VF node3, LOAN2:91); rule 2: same-variable FIXBIN `=0` immediately followed by `>c` ladder → ladder produced+pushed FIRST, zero-test materialises AFTER the F5 (VE, VF node1; other-var pair = NO witness → must refuse BY NAME [TBD]); rule 3: everything else source order (VI both stmts, VG, 113). DEC zero-operand LITERAL-FIRST CONFIRMED from fresh relocs (VG cells data@9/14 pushed before vars @0/5; VI zero10@11/zero9@17 pushed before p@0/q@6; ANNUITY verbatim) — **PAR FALSIFIED; ADD vs literal-first indistinguishable on pool-above-data layouts — record ambiguity in C367**. `reldumps.txt` DATA-size lines are WRONG (VG=0014, VI=001B from DEF-DATA records; read raw records). `0xD6` SUI is 2 bytes — hop-3 `vdumps` desync confirmed artifact; fix `tools/dis80.py` minimally (`0xD6:'SUI' len2`, `0x2F:'CMA' len1`) and verify on E52VE/VG/VI before arm time. `<0` leaf forms measured: standalone TEST = `3A r(cell+1) / B7 / F2 slot`; in-fold = bare `3A r(cell+1)` (bit7 IS truth, no B7). VH ELSE: two independent patch targets CONFIRMED. VK raw head decoded (precedence AND-fold first; value-position OR = fold then BARE `32 <bitcell>`, NO D6/9F normalization) — re-derive every VK byte from the golden before arming.

**EXECUTE NEXT (hop 5 = ARM + registration, per the `LEARNINGS.md` hop-4 NEXT contract):** (1) dis80 minimal fix + verify; (2) arm ONLY measured shapes in `ocaml/lib/codegen.ml`: Or arm in `lower_test_skip0` + Or fold beside And in `lower_bool` (NEVER alter And bytes; VK `a|(b&c)`/`(a|b)&c` reuse the proven And fold `C1/A0` sandwich; value-position `b=(...)` fold+`32` only if VK decode holds byte-exact — else leave `my-gap` documented); chain flatten + rules 1–3; operand materialisers: ladder `2A…/hl_bias(-(k+1))/7C/2F`, zero-test `21/7E/23/B6/D6 01/9F` (`bin_zero_tail`), memcompare `21/AF/BE/23/9E`, LDA-`<0` atomic, DEC `=0` `dec_eq_bool_parts` literal-first (reuse/extend ONLY for witnessed widths/scales; refuse by name anything else incl. other-var zero-vs-ladder swap); `<0` standalone TEST leaf arm (VA 6 B); `prescan_cond` pool-demand parity audit; [C105] hoist law exactly as the dumps show; (3) build rc=0 DIRECT + histogram vs 68 + cmp VA–VK 11 whole-file vs `golden/e52p9/` (record first mismatch offsets honestly) + sweep `python3 build/e52p3/sweep.py E46N E46K E51 E52 P086 R10` FAILS 0 + markers harness (CRLF+bare ^Z) + LOAN2/EXPR1/EXPR2 POSITIONAL VERBATIM (record new first blocker — NEVER fix; ?SIGOP out of scope; unexpected .REL → whole-file cmp vs historical golden); (4) register exact subset in `tools/e2e_gate.py` SPECIMENS, `--update-inventory` (expect 1249→+N, review diff), census own path, **C367 measured-bytes-only committed BEFORE COVERAGE** (new `COND.OR` row + EXPLICIT `spec/COVERAGE-IDS.txt` line, NEVER coverage_gen.py), coverage_check + prose rc=0, FULL gate rc=0 → `build/gate-e52p9-reg.log`; (5) RESULTS §P3-9 (parity table, order law incl. residual ambiguities, PAR falsifier verbatim, H1–H10 HIT/MISS), PLAN §5 row + §P3-9 CLOSED, durables. STOP at P3-9 closure — do NOT start P3-10 or SIGNAL ERROR.

**STATE:** HEAD `42d91094` + durables commit; ledger ENDS **C366**; gate baseline 1249/186/9/140-0-0 SUPPORTED 90, census 15/0/26/0; binary `9ecea27aa4f2d80f49ad…` == baseline (ZERO ocaml change since); tree clean except operator `handoff.config.json` (NEVER staged) + ignored scratch; renewal chain fresh (this hop 4 consumed the startup checkpoint; successor = renewal 1/12 of chain 01a1adf0 if renewed); no push; all rc DIRECT.

SUPERSEDED-BY-ABOVE: ## Next action (E2E-52/P3-9 hop 3 DONE — PRE-REG `4495604` + CAMPAIGN e52p9 **11 ok/11** + goldens `9bb3f99`; fold law H1 + standalone `<0` leaf + VH/VJ measured; fold-ORDER partly pinned (`<0` LAST confirmed; VE/VF same-var FIXBIN reorder vs VI source-order — UNRESOLVED rule); PAR push rule FALSIFIED, ADD survives; VK all 3 boundaries DR-ACCEPTED; hop 4 = fix decode bug, PIN order law from RAW hex, then ARM — read `LEARNINGS.md` section "E2E-52/P3-9 hop 3" FIRST)

**DONE THIS HOP (all rc DIRECT; ZERO `ocaml/` byte):** guard g375 blocks VERBATIM `0f78452`; PLAN sec P3-9 H1-H10 + probes E52VA..VK committed BY EXPLICIT PATH `4495604` BEFORE any oracle call/ocaml byte (tail DEVIATION documented: unmeasured `put edit(x)(a)` dropped, UA skeleton proven); ONE campaign e52p9 rc=0 **11 ok/11, ZERO dr-refuses**; goldens VERBATIM + raw dumps `9bb3f99`; every measurement and my decoder misparse artifact (`DB D6` 1-byte line desyncs following `01 xx 9F` triples) are in `LEARNINGS.md` section hop 3.

**EXECUTE NEXT (hop 4 = ARM):** (1) read `build/e52p9/reldumps.txt` RAW hex (authoritative; reldump line-wrap of reloc list is sloppy — recompute VI literal-vs-var addresses from raw relocs to confirm ADD), pin the operand-EMISSION-order rule (same-variable FIXBIN `>` before `=`? class priority?) across VB/VC/VE/VF/VG/VI + LOAN2 91/113, record falsifications VERBATIM; (2) arm ONLY measured shapes: `Ast.Or` arm in `lower_test_skip0` (~9154, my parse is LEFT-assoc) + Or fold beside And in `lower_bool` (NEVER alter And); `<0` leaf `3A r(cell+1) / B7 / F2 slot`; `> 0` mem-compare `21/AF/BE/23/9E`; DEC `= 0` push per the PINNED rule; ladder/`7C 2F` reuse; ELSE geometry per VH; every other shape refuses BY NAME [TBD]; prescan_cond pool-demand parity; (3) build rc=0 DIRECT + histogram vs 68 + cmp 11 probes WHOLE-FILE vs golden/e52p9 + sweep (`python3 build/e52p3/sweep.py E46N E46K E51 E52 P086 R10` FAILS 0) + markers (CRLF+bare ^Z copy) + LOAN2/EXPR1/EXPR2 POSITIONAL VERBATIM, NEVER fix next blocker (?SIGOP out of scope); commit; (4) registration from **1249** (--update-inventory, census OWN path, gate rc=0 `build/gate-e52p9-reg.log`), **C367 measured-bytes-only BEFORE COVERAGE** (explicit spec/COVERAGE-IDS.txt edit, new COND.OR row, NEVER coverage_gen.py), coverage_check+prose rc=0, RESULTS sec P3-9 + PLAN sec 5 row + sec P3-9 CLOSED, durables, renew near cap. STOP at P3-9 closure — do NOT start P3-10.

**STATE:** ledger ENDS **C366**; gate baseline 1249/186/9/140-0-0 SUPPORTED 90, census 15/0/26/0; binary `9ecea27aa4f2d80f49ad…` == baseline; tree clean except operator `handoff.config.json` (NEVER staged) + ignored scratch (build/e52p9/*, ocaml/*.log); no push; renewal chain 01a1acf2 2/12 consumed (cap 12).

SUPERSEDED-BY-ABOVE: ## Next action (E2E-52/P3-9 hop 1 PART DONE — Phase A evidence audit: OR witnesses DECODED from ANNUITY/LOAN2 goldens, leaves isolated; PLAN §P3-9 + probes E52VA.. OWED BEFORE any oracle call or `ocaml/` byte; 2026-11-05, session 01a1acf2, fresh chain 0/12; read `LEARNINGS.md` § "E2E-52/P3-9 hop 1 IN FLIGHT" FIRST — it holds every measured byte and the full owed contract)

**DONE THIS HOP (all rc DIRECT; ZERO `ocaml/` byte, ZERO oracle call, goldens untouched):** recovery verified (HEAD `4dae78a`, binary `9ecea27aa4f2d80f49ad…` == baseline, LOAN2 blocker VERBATIM rc=2); `E52V*`/`e52p9` collision-free; **leaves isolated**: `dl < 0` REFUSES (`codegen: < 0 / negative const form unproven [TBD]` — my-gap, DR accepts it in LOAN2), `dl > 2` already compiles; **OR decoded from originals**: ANNUITY:46 (DEC) = two FF/00 materialisations, left travels via PUSH PSW flag byte, right in A, ONE `C1 POP B / B0 ORA B / F2 <skip>` — value-level, single branch; LOAN2:91/113 (FIXED-BIN) use `LHLD / DCX ladder / MOV A,H / CMA / PUSH PSW / … / POP B / ORA B / JP` with ONE branch per OR (3 operands at 113 still one branch); NEW byproduct: DR lowers `signal error` = `21 00 00 / AF / CD ?SIGOP` (recorded, NOT to be armed in P3-9). **UNRESOLVED**: my static flag trace of the FIXED-BIN ORs predicts inverted polarity — probes must measure, never guess. Scratch: `build/e52p9/` (ordump.py, leaves/).

**EXECUTE NEXT (hop 2 = Phase A finish + Phase B PRE-REGISTER, per the brief's §3–§4):** (1) check dis80 opcode table for `2F`; re-read ANNUITY 01B6/022F single controls + locate LOAN2:120 AND region; compare my LEA2 bytes with DR's `dl > 2` ladder. (2) Write **PLAN §P3-9** (H-list + per-probe predictions/falsifiers) and **probes/E52VA..** (8–12, families A–F from the brief; CRLF + bare ^Z + ≤71 cols; skeleton like E52UA), **COMMIT BOTH BY EXPLICIT PATH BEFORE ANY ORACLE CALL AND BEFORE ANY `ocaml/` BYTE**. (3) ONE campaign `PLI_SRC=probes timeout 900 python3 oracle/batch.py <names> --tag e52p9 --switches '$L$D'` rc DIRECT; preserve goldens VERBATIM; classify honestly. Then arm-only-measured (Phase D/E), historical recompile (Phase F: LOAN2/EXPR1/EXPR2 VERBATIM, never fix the next blocker), registration + **C367 BEFORE COVERAGE** (explicit `spec/COVERAGE-IDS.txt` edit if new row; NEVER coverage_gen.py), gate rc=0 `build/gate-e52p9-reg.log`, RESULTS §P3-9 + PLAN §5 row + CLOSED, durables, renew at cap as needed.

**STATE:** ledger ENDS **C366**; gate baseline 1249/186/9/140-0-0 SUPPORTED 90, census 15/0/26/0; tree clean except operator `handoff.config.json` (NEVER staged) + ignored `build/e52p9/` scratch; no push.

SUPERSEDED-BY-ABOVE: ## Next action (COVERAGE LEDGER INTEGRITY HARDENING COMPLETE — protections landed, falsification-tested, FULL gate re-confirmed rc=0 on the final tree; STOP reached, nothing authorized, 2026-11-05; read `LEARNINGS.md` § "P3-8 CLOSE HARDENING" FIRST)

**DONE THIS SESSION (all rc DIRECT; ZERO `ocaml/` byte, ZERO new oracle call, goldens NEVER touched, `spec/COVERAGE.tsv` byte-identical, no push, operator `handoff.config.json` NEVER staged):** baseline verified at `4485315`; five commits: `2728890` initialize `spec/COVERAGE-IDS.txt` ONCE from the repaired ledger (140 IDs, ledger order, never tool-regenerated) → `872fa22` `coverage_check.py` CONTRACT-IDENTITY INVARIANT (exact set comparison vs the manifest — removed/renamed/substituted contracts fail even when every surviving row is valid; missing manifest fails CLOSED) + STATS GATING (canonical `coverage-stats.json` written ONLY on a clean validation; new `--ids`/`--stats-path`, old CLI preserved) + schema doc → `85e0726` `coverage_gen.py` NEUTRALIZED to an inert fail-closed stub (rc=2, AST-clean of any write/rename/delete, points to COVERAGE.tsv + coverage_check.py) → `a5670e5` `tools/test_coverage_integrity.py` (36 checks rc=0) covering every required falsification, incl. the LIVE sandbox proof that the normal compile-tier gate pre-flight aborts on a missing contract before any specimen compiles → `1a2c40b` [C366] narrow wording correction (NO relocation ON THE ARGUMENT OPERAND; `?ONCOP` CHAIN-EXT and jump-over `RELOC code` acknowledged; former phrase kept as a labelled correction — nothing historical removed). FULL gate rc=0 `build/gate-coverage-integrity.log`: **1249/0, 186/186, 9/9, coverage 140 rows 0/0 (SUPPORTED 90), census 15/0/26/0, prose 5**; COVERAGE.tsv sha `ba1ca9b11e2934a4…` and stats sha `39e096d5fcfc9fcf…` byte-identical to the repaired P3-8 state.

**STATE:** ledger ENDS **C366**; binary `9ecea27aa4f2d80f49ad…`; tree clean except the operator config + ignored scratch (three inert `build/e2e-<pid>/` dirs from accidentally-completed real-path gate runs — generated working state, left in place per policy). LOAN2 UNMODIFIED rc=2, NO .REL, first blocker VERBATIM `codegen: condition form not in E2E-3b subset [TBD]: (| (< dl 0) (> dl 2))` = LOAN2:91, NOT fixed.

**EXACT NEXT:** commit the refreshed managed blocks VERBATIM (documented mechanism; never hand-edit), then **STOP**. **P3-9 is NOT started** — the next scientific campaign (compound/OR-condition class at LOAN2:91) remains an operator decision; do NOT implement OR conditions, touch `lower_test_skip0`, add probes, run the oracle, change LOAN2, or start PLILIB/MIR.

SUPERSEDED-BY-ABOVE: ## Next action (P3-8 SUBROUND CLOSED + COVERAGE LEDGER REPAIRED — the brief's STOP is REACHED; only a full-gate re-confirm is PROPOSED, 2026-11-05; read `LEARNINGS.md` § "DOCS CLOSE + A LEDGER-CLOBBER REPAIR" FIRST)

**DONE THIS SESSION (docs-only; ZERO `ocaml/` byte, ZERO oracle call, goldens NEVER touched, no push, operator `handoff.config.json` NEVER staged; all rc DIRECT):** guard g368 blocks committed VERBATIM `9adf3fc`; `RESULTS.md` §P3-8 (measured table, H1–H6 ALL CONFIRMED, first-draft falsifier VERBATIM, marker CRLF+`^Z` procedure, LOAN2→condition-form / EXPR1→GET-21 / EXPR2→FLOAT-35 advances VERBATIM, registration 1249 + **C366** BEFORE COVERAGE, §6 byte-tier-only NOT-say, **§7 the defect record**), `PLAN.md` §5 P3-8 row + §P3-8 **CLOSED** marker — `86db760`; `LEARNINGS.md` repair section `87ebe5f`.

**ACCEPTED DEFECT + REPAIR (the reason this hop was NOT a plain close):** commit `0cf0688` never landed the COVERAGE rewrite — the obsolete `tools/coverage_gen.py` (hard-coded E2E-36 row list, ends `os.replace('spec/COVERAGE.tsv')`) was run as "the stats' own write path" and clobbered the ledger 141→72 lines, leaving `COND.ON_ERROR` REFUSED/NONE. Repaired: restored `git show 17c9963:spec/COVERAGE.tsv`, re-applied the row by csv column-edit (id KEPT, historical sentence VERBATIM, SUPPORTED/**EXACT:6**, probes E52UA..UF, corpus ANNUITY,COPYLPT,EXPR1,EXPR2,LOAN2, boundary = BY-NAME refusals + byte-tier-only + the three census advances). Verified `coverage_check.py` rc=0 **140 rows 0/0 SUPPORTED 90 == the committed `coverage-stats.json` (stats did NOT move = the consistency proof)** and `file_prose_check.py` rc=0; evidence `build/e52p8-reg/coverage-repair.log`, `prose-repair.log`. **LAW: `coverage_check.py` is the stats' ONLY write path; NEVER run `coverage_gen.py` on this tree; verify ledger rewrites by CONTENT (`git diff --stat` ≈ one line + re-read the row), never by a validator exit code.**

**STATE:** ledger ENDS **C366**; build rc=0 binary `9ecea27aa4f2d80f49ad…`; gate last ran rc=0 **1249/0, 186/186, 9/9, 140 rows 0/0, census 15/0/26/0, prose 5** (`build/gate-e52p8-reg.log`, BEFORE the clobber — the restore re-establishes exactly that panel state, coverage-panel-verified standalone); LOAN2 UNMODIFIED rc=2, NO .REL, first diagnostic VERBATIM `codegen: condition form not in E2E-3b subset [TBD]: (| (< dl 0) (> dl 2))` = LOAN2:91, NOT fixed.

**EXACT NEXT (nothing is authorized):** `/handoff` + commit the refreshed managed blocks VERBATIM, then **STOP**. PROPOSED (never authorization, do NOT start without an operator brief): (1) ONE full `python3 tools/e2e_gate.py` re-run to confirm the combined state after the restore; (2) neuter/delete `tools/coverage_gen.py` + add a gate assertion that the COVERAGE row count never shrinks without a labelled correction; (3) metadata-only tightening of [C366]'s "NO relocation of any kind in its registration" phrase (precise meaning: NO COMMON group, NO SEL-COMMON record, NO relocation ON THE ARGUMENT operand; the `?ONCOP` CHAIN-EXT and the jump-over `RELOC code` DO exist); (4) subround P3-9 = the compound/OR-condition class at LOAN2:91 (`my-gap`), decoding EXISTING E37/E38 `COND.*` goldens FIRST, then PLAN §P3-9 + probes BEFORE any `ocaml/` byte.

SUPERSEDED-BY-ABOVE: ## Next action (P3-8 hop 3 REMAINDER CLOSED — VALIDATION + REGISTRATION + C366 + COVERAGE ALL LANDED; RESULTS §P3-8 + PLAN §5 ROW + DURABLE COMMIT OWED, 2026-11-05; read `LEARNINGS.md` § "hop 3 REMAINDER CLOSED" FIRST)

**CLOSED THIS HOP (all rc DIRECT, goldens NEVER touched, no new oracle call, no push, operator `handoff.config.json` NEVER staged):** clean rebuild rc=0 binary `9ecea27aa4f2d80f49ad…`; codegen warning histogram **68 == baseline**; cmp UA..UF **6/6 whole-file rc=0**; sweep **FAILS: 0** (124 specimens + 21 named refusals); marker harness `build/e52p8-reg/markers.py` **MARKER_FAILS: 0** (E46K4/K15/N21/E52PF/PU/PV/RE + SE/SF/SG all rc=2) — LESSON: the harness MUST materialise CRLF + bare `^Z` like `run_negatives`, else the reported line number moves and the marker misses. **LOAN2 VERBATIM** (sha `7be23ba390926c20…`, HEAD `1dc53f4`, POSITIONAL) **rc=2, NO .REL**, first diagnostic VERBATIM `codegen: condition form not in E2E-3b subset [TBD]: (| (< dl 0) (> dl 2))` = LOAN2:91 `if dl < 0 | dl > 2 then` — ON ERROR 58 CLOSED, blocker RECORDED, NOT fixed. SPECIMENS +6 (`244f6e1`), inventory 1243->**1249** (+6 exactly, 186 refusals), census OWN path rc=0 counts **15/0/26/0** with EXPR1->GET 21 / EXPR2->FLOAT builtin 35 / LOAN2->condition form, FULL gate rc=0 `build/gate-e52p8-reg.log` (**1249/0, 186/186, 9/9, 140 0/0, prose 5**), **C366** `17c9963` measured-bytes-only BEFORE COVERAGE `0cf0688` (COND.ON_ERROR SUPPORTED/EXACT:6, falsified clause kept VERBATIM as HISTORICAL), coverage_check + coverage_gen + prose rc=0. Ledger ENDS **C366**.

**EXECUTE NEXT (docs-only, finish the brief):** (1) `spec/lab-evidence/e2e52-p3/RESULTS.md` — append `§P3-8` table: campaign e52p8 **6 ok/6**, H1..H6 EVERY prediction HIT (abs prefix 10 B no COMMON/reloc; argument verbatim incl. error(2)/error(0); BODY-DEPENDENT tail proven inside UF; no cell/pad for returning handlers; UB two independent triples vs UC adjacent merge 0x36; all DR-ACCEPTED), sizes UA 128/0020/0002 UB 256/0030/0004 UC 256/0046/0008 UD 128/0020/0002 UE 256/002B/0002 UF 384/002F/0002+COMMON F,G 0023, the first-draft prologue-omission falsifier (UF MISS octet 150, 5/6) KEPT VERBATIM, implementation arm `a7ab5a4` 6/6 cmp + sweep + markers, LOAN2/EXPR1/EXPR2 advances VERBATIM, registration 1249 + C366 + COVERAGE EXACT:6, §6 BYTE-TIER-ONLY NOT-say. (2) `PLAN.md` §5 table: one P3-8 row (pre-reg `e6d16ff`, goldens `9f36504`, claim C366, arm `a7ab5a4`, verification, next blocker) + mark §P3-8 CLOSED. (3) prose rc=0 standalone; (4) FIRST action of the successor: the guard refreshed the managed blocks in HANDOFF.md/PROGRESS.md for checkpoint **g367-d6cecb5a9d02** (renewal 1/12, attested by session 01a1ab9a) AFTER commit `eae0ff2`, so they are UNCOMMITTED in the tree — commit them VERBATIM (explicit paths, NEVER hand-edit the managed block, NEVER stage `handoff.config.json`) before anything else, then re-verify HEAD and that the tree is clean apart from the operator config + ignored scratch. Then STOP — do NOT start P3-9, no oracle, no PLILIB/MIR.

**PROPOSED (never authorization) next scientific choice:** the compound-condition class — LOAN2:91 `dl < 0 | dl > 2` refuses at `codegen.ml:9154` `condition form not in E2E-3b subset`; `my-gap` for OR-of-relations (existing `COND.*` rows + E37/E38 goldens are the evidence to re-read), `dr-refuses` rows unchanged (E46N21 LINE-with-count, EXPR2's FLOAT builtin is a separate `my-gap`). Smallest investigation: decode existing goldens for the `|` condition shape, then pre-register PLAN §P3-9 + E52VA.. probes BEFORE any `ocaml/` byte. DO NOT execute this hop.

SUPERSEDED-BY-ABOVE:  — ARM COMMITTED `a7ab5a4` 6/6 CMP + SWEEP CLEAN; HISTOGRAM/markers/LOAN2 + REGISTRATION OWED, 2026-11-05; read `LEARNINGS.md` § "hop 3 PART DONE" FIRST — it is the exact remaining contract)

**HOP-3 STATUS (session 01a1ab4c, renewal 3/12):** guard g362 blocks committed VERBATIM `5946467`; baseline re-held (build rc=0, binary `8b374e623bc9e280fa14…`). `ocaml/lib/codegen.ml` arm LANDED AND COMMITTED `a7ab5a4`: `on_error_reg_prefix` (abs LXI H,arg / XRA A; file encoder untouched), helpers hoisted (has_goto/block_tail_goto/handler_body + NEW has_stop), ERROR arm admitting ONLY bare/one-int-arg + the four measured handler shapes (statement-C9, returning block-C9 per-stmt lowering, direct goto, block tail-goto; STOP/RETURN/NULL/DCL handlers and all other args refuse BY NAME [TBD]), body-dependent STOP tail on the ENDFILE route (manual `call_ext ?STOPX`, NO C9, no stop_seen leak — UF 0011-0013/epilogue @002C) with UNDEFINEDFILE+STOP and nested STOP now refusing BY NAME. FIRST DRAFT FALSIFIED in-house: the stop branch omitted the registration+C3+triple sequence — UF CMP_RC=1 at octet 150 (5/6); fixed, build rc=0 DIRECT binary `9ecea27aa4f2d80f49ad…` (supersedes draft `f9abf6b6d07f1d3db500…`), **cmp 6/6 rc=0 (UA UB UC UD UE UF)** whole-file vs golden/e52p8/, sweep rc=0 **FAILS: 0** with 21 expected named refusals (`build/e52p8-reg/sweep-arm.log`). OWED NOW: warning histogram vs 68, markers E46K4/K15/N21/E52PF/PU/PV/RE + SE/SF/SG rc=2, LOAN2 POSITIONAL VERBATIM (58 now armed — record the advance, never fix), commit explicit paths, then the hop-2 registration contract (SPECIMENS +6, --update-inventory from 1243, census OWN path FIRST, gate rc=0 build/gate-e52p8-reg.log, C366 measured-bytes-only BEFORE COVERAGE, coverage_check+prose rc=0, RESULTS §P3-8 + PLAN §5 row, durables).

SUPERSEDED-BY-ABOVE: ## Next action (P3-8 hop 3 = ARM + REGISTRATION OWED, 2026-11-05; read `LEARNINGS.md` § "P3-8 hop 2 CLOSED" FIRST — it holds every measured byte)

**STATE (hop 2 CLOSED, all rc DIRECT):** pre-registration `e6d16ff` (PLAN §P3-8 H1–H6 + probes
E52UA..UF, CRLF/bare-^Z/≤71 cols, collision-grepped, committed BEFORE any `ocaml/` byte) → campaign
`PLI_SRC=probes timeout 900 python3 oracle/batch.py E52UA..E52UF --tag e52p8 --switches '$L$D'` rc=0
DIRECT **6 ok/6**, every .PRN `NO ERROR(S) IN PASS 1` + `PASS 2` → goldens committed VERBATIM `9f36504`.
**ALL SIX PREDICTIONS HIT**: H1 abs prefix `21 <arg LE> / AF / CD ?ONCOP / C3 over` (10 B, no
COMMON/SEL-COMMON/RELOC in a file-less object); H2 `error(2)`=`21 02 00`, `error(0)`=`21 00 00`; **H3
BODY-DEPENDENT tail** — UA/UD returning bodies emit `C9` @0016, **UF: `on endfile(f) stop;` = inline
`CD ?STOPX` NO `C9` while `on endfile(g) x = 1;` carries `C9` @0025**; H4 no cell/pad for returning
bodies (DATA 0002, no `DAD SP`) vs UB cell@2 (0004) / UC cell@6 (0008); H5 UB two independent targets
(0015→0x1A, 0018→pad 0x20), UC adjacent merge (0x36); H6 all accepted incl. `on error goto lbl;`.
Sizes UA 128/0020 UB 256/0030 UC 256/0046 UD 128/0020 UE 256/002B UF 384/002F.

**EXECUTE hop 3 (the ARM, then registration):** (1) `ocaml/lib/codegen.ml` — add a SECOND prefix encoder
beside `on_reg_prefix` (NEVER mutate the file one): `LXI H,<arg>` absolute (no reloc) / `AF` /
`CALL ?ONCOP` / `C3 <slot>`; admit `Ast.Son` `cond = "error"` with `cargs = []` (arg 0) or ONE integer
literal (that value); EVERY other ERROR argument or handler shape refuses BY NAME with `[TBD]`. (2) Make
the tail BODY-DEPENDENT: suppress the trailing `C9` iff the handler's LAST statement transfers
unconditionally — GOTO (existing [C364] arm) and STOP (MEASURED by UF on the ENDFILE route; ERROR+STOP is
UNMEASURED, so keep that combination refused/unchanged until a specimen pins it); returning bodies keep
`C9` (UA/UD). Keep bind.ml `Rk_on` + pad/cell machinery as is (bytes agree).
(3) Verify: `cd ocaml && eval "$(opam env)" && dune build` rc=0 DIRECT; per-File warning histogram vs
baseline **68**; cmp **UA UB UC UD UE UF** whole-file rc=0 vs `golden/e52p8/`; sweep
`python3 build/e52p3/sweep.py E46N E46K E51 E52 P086 R10` = **114/0**; markers E46K4/K15/N21/E52PF/PU/PV/RE
+ SE/SF/SG rc=2; LOAN2 UNMODIFIED POSITIONAL — record its new first blocker VERBATIM, NEVER fix or
hardcode it; commit explicit paths.
(4) Register: SPECIMENS +6, sanctioned `--update-inventory` (real delta from **1243**), census OWN write
path FIRST, FULL gate rc=0 DIRECT → `build/gate-e52p8-reg.log`, claim **C366 from MEASURED BYTES ONLY
committed BEFORE the COVERAGE `ON`-unit rewrite**, `coverage_check.py` + `file_prose_check.py` rc=0,
RESULTS §P3-8 + PLAN §5 row, durables, renew near exhaustion (chain 01a1ab34, cap 12).
Boundaries KEPT: byte-tier only — NO runtime claims; no push; goldens NEVER re-derived; operator
`handoff.config.json` NEVER staged; all rc DIRECT (never a pipeline tail); `pli80c` POSITIONAL;
standing PROPOSALS (never authorization): SE `?REVOP` arm; ENVIRONMENT route (RETRIEVE:31 / REPORT:29).

SUPERSEDED-BY-ABOVE: ## Next action (P3-8 hop 2 IN FLIGHT, 2026-11-05, session 01a1ab1e, renewal 1/12 of cap 12)

** hop 2 progress so far (all rc DIRECT, ZERO `ocaml/` byte, ZERO oracle call):** recovery
VERIFIED (HEAD `2790c96` = g358 attested block committed; tree clean except operator
`handoff.config.json` NEVER staged + ignored scratch logs; `dune build` rc=0 binary
`8b374e623bc9e280fa14…` == registration baseline; LOAN2 blocker re-measured VERBATIM line 58
rc=2). **ANNUITY 0070-0078 CLEANLY DISASSEMBLED — the hop-1 ambiguity is CLOSED and its
"retry not adjacent / 0074 mid-dump" reading is FALSIFIED:** `build/e52p8/ondump2.py` (NEW
scratch tool: the bitstream decoder of `ondump.py` + `dis80.py`'s DR-learned opcode table +
CHAIN-EXT/CHAIN-ADDR symbol walking; dis80's reldump-TEXT mode prints reloc operands as `.` and
showed FALSE gaps) proves ANNUITY is the ordinary adjacent-label case: registration 004B
`21 00 00 / AF / CD ?ONCOP / C3 ->code@0074`, handler inline 0055-0070, `C3` at 0071 (slot 0072
CHAIN-ADDR) NO C9, pad AT 0074 = label `retry:` `2A r(data@0136) / F9 / CD ?RECOV`, body 007B —
identical geometry to LOAN2 (00E8/010E/0111), COPYLPT error(1) (00A6/00C7/00CA), EXPR1
(001B/005B/005E), EXPR2 (001B/0054/0057). Full byte lists in `LEARNINGS.md` § "P3-8 hop 2 IN
FLIGHT"; output preserved `build/e52p8/onregions.txt`.

**NEW DISCOVERY — a latent my-gap in MY EXISTING ON lowering (recorded, NOT fixed):** the
`C9 RET` at codegen.ml (~14010-14050, both non-goto arms) is emitted UNCONDITIONALLY per
[C109], but the EXPR1/EXPR2 goldens measure `on endfile(sysin) stop;` = inline `CD ?STOPX` with
**NO C9 RET**. The RET tail is BODY-DEPENDENT (a handler whose last statement transfers
unconditionally — GOTO or STOP — emits none). No registered specimen has a STOP-bodied handler,
so the byte panel CANNOT catch this. ON ERROR arming must never copy the blind RET.

**EXACT NEXT ACTION (hop 2 remainder → hop 3):** (1) WRITE `spec/lab-evidence/e2e52-p3/PLAN.md`
§Subround P3-8 — hypotheses H1 the ERROR prefix is ABSOLUTE `LXI H,<arg 16-bit LE>` + `XRA A`
(`AF`, ONE byte, NOT `MVI A,nn`) + `CALL ?ONCOP` + `C3 <over>` (7 bytes, one SHORTER than the
file-scoped [C109]/[C364] prefix, no SEL-COMMON, no reloc); H2 the conditional-name ARGUMENT is
that LXI operand verbatim (bare = 0000, `error(1)` = 0001); H3 the handler tail is
BODY-DEPENDENT — goto-terminated inline + `C3` + NO RET [C364], STOP-bodied NO RET (EXPR1/2), a
RETURNING handler emits `C9` (UNMEASURED for ERROR → probe UD); H4 a handler with NO goto demands
NO block SP-cell and NO pad ([C206]); H5 jump-over operand = the fall-through continuation,
adjacent label merges them ([C208]); plus per-probe byte-exact predictions and explicit
FALSIFIERS, VERBATIM, and the LOAN2 next-blocker prediction (line 58 must clear; the NEXT
blocker candidate is the first unlowered statement after it — record whatever actually happens,
NEVER fit). (2) WRITE probes `probes/E52UA..E52UF.PLI` in the E52SA style (CRLF line endings,
bare `^Z` at EOF, ≤71 columns, `dcl f file; dcl x fixed bin;` skeleton): **UA** bare `on error` +
assignment handler `x = 1;` (H1 + H3 returning-tail); **UB** bare `on error` + DIRECT `goto lbl;`
to a NON-adjacent label (H5 independent patch targets on the ERROR route, cf. SC); **UC**
LOAN2-mirror `begin; put skip list('oops'); goto retry; end;` with adjacent `retry:` (H1+H3
no-RET law in isolation); **UD** plain RETURNING `begin; x = 1; end;` (is there a C9? a pad? a
cell? UNMEASURED); **UE** `on error(0);` and `on error(2)` (H2 argument verbatim); **UF** the
FILE-condition contrasts under identical shapes: `on endfile(f) stop;` (does the no-RET law
transfer to ENDFILE? — the EXPR1 reading in isolation) and/or `on endfile(f) x = 1;` (the [C109]
RET witness to compare byte-for-byte against UA). Collision-grepped ALREADY: `E52U*` EMPTY in
`probes/` and `spec/INVENTORY.txt`; tag **e52p8 UNUSED** (verify once more: `grep -rn e52p8
spec/ golden/ build/ oracle/ tools/ --include='*' | grep -v e52p8/ondump`). (3) **COMMIT PLAN +
probes by EXPLICIT PATH BEFORE any `ocaml/` byte** (if a guard block landed uncommitted, commit
it VERBATIM first). (4) ONE grouped campaign `PLI_SRC=probes timeout 900 python3
oracle/batch.py E52UA E52UB E52UC E52UD E52UE E52UF --tag e52p8 --switches '$L$D'` rc DIRECT
(NEVER a pipeline tail), read every .PRN, reldump goldens to `build/e52p8/`, classify honestly
(dr-refuses / my-gap / unmeasured; keep MISSes verbatim), commit goldens VERBATIM.
(5) Arm ONLY measured shapes: a SECOND prefix encoder next to `on_reg_prefix` (never mutate the
file one), body-dependent RET tail (fix the STOP/GOTO case), reuse the [C364] inline-goto +
pad/cell machinery where bytes agree, unmeasured argument/handler shapes refuse BY NAME with
[TBD]; keep ENDFILE/UNDEFINEDFILE regressions byte-exact. Then build rc=0 DIRECT, cmp accepted
probes whole-file rc=0 vs `golden/e52p8/`, sweep 114, markers E46K4/K15/N21/E52PF/PU/PV/RE +
SE/SF/SG rc=2, LOAN2 POSITIONAL VERBATIM new blocker, registration via sanctioned
`--update-inventory` + census OWN write path FIRST, FULL gate rc=0 logged
`build/gate-e52p8-reg.log`, claim **C366 from MEASURED BYTES ONLY committed BEFORE the COVERAGE
rewrite**, coverage_check + prose rc=0, RESULTS §P3-8 + PLAN §5 row, durables, renew near
exhaustion.
Standing boundaries KEPT: byte-tier only — NO runtime claims; no push; goldens NEVER re-derived;
operator `handoff.config.json` NEVER staged; all rc DIRECT (never a pipeline tail); `pli80c`
POSITIONAL (`pli80c IN.PLI OUT.REL`); never hardcode LOAN2; ON ERROR never presumed a file event
— its operand is ABSOLUTE and its condition byte is AF/XRA A, measured. Standing PROPOSALS (never
authorization): SE `?REVOP` arm; ENVIRONMENT route (RETRIEVE:31 / REPORT:29 36-B `4E52`); the
STOP-bodied-handler RET correction.

### P3-8 hop 1 LANDED (2026-11-05, session 01a1ab05): ON ERROR DECODED + CONFIRMED on 5 original goldens; PLAN §P3-8 PRE-REGISTRATION IS THE EXACT NEXT ACTION

**P3-7 CLOSED — every hop-5 deliverable LANDED at this boundary commit (all rc DIRECT, ZERO oracle calls, ZERO `ocaml/` bytes this hop).** `spec/PERIMETER.md` line-38 correction appended INSIDE the FILE-attribute-cluster final cell, labelled [E2E-52/P3-7 CORRECTION]: falsified `Still refusing by name:` sentence kept VERBATIM as HISTORICAL; PRINT/PAGESIZE/LINESIZE implemented for the MEASURED combinations [C365], PAGE already [C359], file PUT/GET EDIT C360-C363 (E41X8 refusal OBSOLETE); KEYED/DIRECT/RECORD/SEQUENTIAL/UPDATE/APPEND/ENVIRONMENT remain unsupported on the OPEN routes; titleless OUTPUT 0x0650 stays OUTSIDE the measured OPEN implementation; unmeasured PRINT/attribute combinations still refuse BY NAME; NO claim that all combinations of individually supported attributes are supported. RESULTS §P3-7 + PLAN §5 row KEPT as the killed session authored them (idempotent recovery — only PERIMETER was missing; every cited hash verified to exist). Verification of the FINAL COMBINED state: `file_prose_check.py` rc=0; `coverage_check.py` rc=0 140 rows 0/0; FULL compilation-tier gate rc=0 DIRECT `build/gate-e52p7-hop5.log` — 1243/1243 byte-exact, 186/186 negatives, 9/9 divergence, coverage 140 rows 0/0, census 15/0/26/0, prose 5. Ledger ENDS **C365**; goldens NEVER re-derived; SE my-gap / SF-SG dr-refuses kept.

**AUTHORIZED NEXT (operator brief 2026-11-05): E2E-52/P3-8 = ON ERROR (LOAN2:58, `codegen: ON ERROR is not implemented [TBD] … line 58`).** Contract, in order: (1) DECODE EXISTING evidence FIRST — `golden/first/LOAN2/LOAN2.REL` ON-unit region, claims C109/C120/C201/C202/C364, E52SA..SD specimens + `golden/e52p6/`, ON ENDFILE/UNDEFINEDFILE witnesses, `artefacts/COPYLPT.PLI` (`on error(1)`), `ocaml/lib/codegen.ml` Son dispatch + `on_reg_prefix`, bind.ml ON references/recovery-pad/saved-SP; do NOT modify LOAN2 source. (2) Preregister PLAN §P3-8 + a small DISCRIMINATING probe bank (bare ON ERROR with assignment handler / direct GOTO / BEGIN…END ending in GOTO / plain returning BEGIN handler; ON ERROR(1) if DR accepts the spelling; ENDFILE/UNDEFINEDFILE contrasts under identical handler shapes; saved-SP/continuation discriminator) with competing condition-code hypotheses, acceptance/refusal predictions, byte predictions and explicit falsifiers — COMMITTED BEFORE any `ocaml/` byte. ON ERROR is NOT presumed a file event; its condition code and registration operand must be MEASURED. (3) ONE grouped `e52p8` campaign (`PLI_SRC=probes timeout 900 python3 oracle/batch.py <probes> --tag e52p8 --switches '$L$D'`) rc DIRECT, ONLY if existing goldens leave the questions open. (4) Arm measured forms reusing existing handler/control-flow machinery ONLY where bytes genuinely agree; preserve ENDFILE/UNDEFINEDFILE regressions; no hardcoded LOAN2, no invented codes; unmeasured shapes refuse BY NAME. (5) cmp whole-file, focused ON bank + sweep 114, markers, LOAN2 POSITIONAL VERBATIM (record the new first blocker, do not chase it), registration via sanctioned `--update-inventory` + census OWN path, FULL gate rc=0 logged, claim C366 from MEASURED BYTES ONLY BEFORE the COVERAGE rewrite, RESULTS §P3-8 + PLAN §5 row, prose rc=0, durables, renew per cap. Standing boundaries KEPT: byte-tier only — no runtime claims; no push; operator `handoff.config.json` NEVER staged; goldens NEVER re-derived; all rc DIRECT (never a pipeline tail); `pli80c` POSITIONAL. Standing PROPOSALS (never authorization): SE `?REVOP` arm; ENVIRONMENT route (RETRIEVE:31 / REPORT:29 36-B `4E52`).

### P3-8 hop 1 LANDED (2026-11-05, session 01a1ab05): ON ERROR DECODED + CONFIRMED on 5 original goldens; PLAN §P3-8 PRE-REGISTRATION IS THE EXACT NEXT ACTION

ACCEPTED (bytes, LEARNINGS § "P3-8 hop 1"): bare `on error` = `LXI H,0000 / XRA A / CALL
?ONCOP / JMP <over>` (ABSOLUTE operand, condition 00 via AF, 7-byte prefix — LOAN2 00E8,
ANNUITY 004B); `on error(1)` = `LXI H,0001 / XRA A / ?ONCOP / JMP <over>` (COPYLPT 00A6,
EXPR1/EXPR2 001B); goto-terminated BEGIN handlers inline, `C3` chain, NO RET (C364 law
holds); pad `LHLD <block SP cell>/SPHL/?RECOV` at the goto label, cell SHARED with
file-scoped pads (LOAN2 d0318, COPYLPT d0214, ANNUITY d0136); `revert error(1)` = LXI H,
0001/XRA A/?REVOP measured UNARMED; `on endfile(sysin) stop;` body = inline CALL ?STOPX
**NO RET** — C109's RET tail is body-DEPENDENT, re-read before arming. ANNUITY pad/jump-over
geometry AMBIGUOUS mid-dump — clean disassembly owed. PROPOSED probes: E52UA simple-
statement error handler; UB remote non-adjacent goto target pad geometry; UC LOAN2-mirror
begin…goto; UD plain returning begin handler (RET? UNMEASURED); UE error literals 0/1/2
plus refusal boundary; UF ENDFILE/UNDEFINEDFILE contrasts. FALSIFIED: slot-7 fixed walk-back.

EXACT NEXT ACTION (hop 2): re-disassemble ANNUITY 0070-0078; then write PLAN §P3-8
(hypotheses/byte predictions/falsifiers VERBATIM) + probes E52UA..UF (CRLF/bare ^Z/
column conventions; collision-grep ids); COMMIT PLAN+probes BEFORE any ocaml/ byte; ONE
grouped campaign `PLI_SRC=probes timeout 900 python3 oracle/batch.py E52UA..UF --tag e52p8
--switches '$L$D'` rc DIRECT; then arm (ERROR const-operand prefix + AF inside existing
on_reg_prefix/Son machinery, only where bytes agree; unmeasured shapes refuse BY NAME;
ENDFILE/UNDEFINEDFILE regressions preserved), cmp/sweep 114/markers/LOAN2 POSITIONAL
VERBATIM, registration, gate, C366 measured-bytes-only BEFORE COVERAGE, RESULTS §P3-8 +
PLAN §5 row, durables. Constraints: no push; operator handoff.config.json NEVER staged;
goldens NEVER re-derived; all rc DIRECT; pli80c POSITIONAL; byte-tier only.

### P3-8 hop 1 IN FLIGHT (2026-11-05, session 01a1ab05): ON ERROR DECODED from LOAN2+COPYLPT+ANNUITY goldens; EXPR direct-dump + PLAN §P3-8 PRE-REGISTRATION OWED

DONE this hop (ZERO ocaml/, ZERO oracle): full decode in `LEARNINGS.md` § "P3-8 hop 1 IN
FLIGHT" — bare ERROR registers `LXI H,0000 / XRA A / CALL ?ONCOP / JMP over` (ABSOLUTE
constant, condition byte 0 via XRA A, 7-byte prefix); `ERROR(1)` = `LXI H,0001`; inline
no-RET goto-terminated handlers reuse the [C364] machinery verbatim; pad `LHLD <SP cell>/
SPHL/?RECOV` AT the goto label, cell shared per BLOCK with file-scoped pads (LOAN2 0318,
COPYLPT 0214); `revert error(1)` measured UNARMED.

OWED (exact next actions, in order): (1) direct-dump EXPR1/EXPR2/ANNUITY ON-unit regions with
the WORKING annotated disassembler (registration start = slot-6 MVI form / slot-5 XRA-A form;
the fixed slot-7 walk-back was FALSIFIED) to confirm/extend the decode before preregistering.
(2) Write PLAN §P3-8 (hypotheses: H1 prefix LXI H,const+XRA A; H2 handler-tail law for
plain-BEGIN vs simple-statement handlers — UNMEASURED by goldens; H3 pad placement when the
goto-target label is NOT adjacent; competing encodings, acceptance predictions, byte
predictions, falsifiers VERBATIM) + probes E52UA..UF: UA bare ON ERROR + assignment handler;
UB bare ON ERROR + direct goto to a REMOTE label; UC begin…goto handler (LOAN2 mirror); UD
plain begin;…;end; returning handler; UE on error(1)+error(2) literals; UF ENDFILE/
UNDEFINEDFILE contrasts under identical shapes. Collision-grep probe ids; COMMIT PLAN+probes
BEFORE any `ocaml/` byte. (3) ONE grouped campaign `PLI_SRC=probes timeout 900 python3
oracle/batch.py <probes> --tag e52p8 --switches '$L$D'` rc DIRECT; goldens VERBATIM.
(4) Arm Son dispatch in codegen.ml (+bind.ml if Rk_on demands it for ERROR label refs):
ERROR → const-operand prefix + XRA A; reuse on_reg_prefix machinery ONLY where bytes agree;
unmeasured argument shapes refuse BY NAME; keep ENDFILE/UNDEFINEDFILE regressions intact.
(5) cmp whole-file; focused ON bank + sweep 114; markers; LOAN2 POSITIONAL new blocker
VERBATIM; registration; FULL gate logged rc; claim C366 measured-bytes-only BEFORE COVERAGE;
RESULTS §P3-8 + PLAN §5 row; durables; renew only near exhaustion (chain 01a1ab05, 0/12 used).
Constraints: no push; operator handoff.config.json NEVER staged; goldens NEVER re-derived;
all rc DIRECT (never a pipeline tail); `pli80c` POSITIONAL; byte-tier only — no runtime claims;
ON ERROR never presumed a file event; no hardcoding LOAN2.

SUPERSEDED-BY-ABOVE (hop-5 contract — DELIVERED by the paragraphs above): ## Next action (hop 4 PART DONE, 2026-11-05; renew into hop 5)

**LANDED hop 4 (commit `d9ebb30`, all rc DIRECT): COVERAGE.tsv — FILE.OPEN_STREAM boundary rewrite (falsified PRINT clause kept VERBATIM HISTORICAL, id KEPT, +[C365]); NEW row FILE.OPEN_PRINT_ATTRS SUPPORTED EXACT:10; labelled CORRECTIONs on FILE.OPEN_STREAM_OUTPUT (KEYFILE:19 lowered as E52TE), FILE.PUT_LIST, FILE.OPEN_TITLE_STATIC; coverage_check rc=0 140 rows 0/0 + coverage-stats.json via own write path — both committed.** Recovery facts (hop 5, verify): HEAD `d9ebb30`, binary `8b374e623bc9e280…` build rc=0, ledger ENDS **C365**, sweep 114/0, gate-e52p7-reg.log 1243/0 (its coverage panel predates the new row: next gate expect **140 rows 0/0**).

**OWED to close P3-7 (hop 5, docs-only, NO oracle):** (1) RESULTS.md §P3-7 — 10-probe table (TA 256B code 0035/DATA 0002 blk 21B w1 0652; TB 384/003D/0006 29B 2E52; TC 384/003B/0011 27B 0E52; TD 256/0038/0002 24B 2652; TE 384/003F/0008 31B 1E50; TF 384/0041/0015 33B 3E52; TG 384/0040/0006 32B; TH 384/0041/0006 33B; TI 256/003A/0004 26B; TJ 256/003A/0002 26B), H1–H5 CONFIRMED, H6 refused-as-designed; TI falsifier VERBATIM (predicted w6 `21 00 00`, DR `60 68`); TG/TH 30-B totals FALSIFIED VERBATIM (32/33, encodings HIT); TJ DR-ACCEPTED `21 2C 01`; LOAN2 → `ON ERROR … line 58` + RETRIEVE → `OPEN option ENVIRONMENT … (line 31)`; campaign 10 ok/10 ZERO dr-refuses; §6 byte-tier-only NOT-say. (2) PLAN.md §5 progress table P3-7 row (same facts). (3) spec/PERIMETER.md line 38: append ONE labelled [E2E-52/P3-7 CORRECTION] paragraph — falsified `Still refusing by name: PRINT…` sentence kept verbatim; also note PAGE (C359) and file PUT EDIT (C360–C363) clauses stale since E2E-42; still refusing: KEYED/DIRECT/RECORD/SEQUENTIAL/UPDATE/APPEND/ENVIRONMENT, titleless OUTPUT 0x0650, every PRINT/attribute combo outside the matrix. (4) `python3 tools/file_prose_check.py` rc=0 DIRECT standalone. (5) Durables close + explicit-path commits; renew (5/12 used of cap 12; NEVER stage handoff.config.json).
Standing PROPOSALS (never authorization): P3-8 ON ERROR (LOAN2:58); SE `?REVOP` arm; ENVIRONMENT route (RETRIEVE:31/REPORT:29 36-B `4E52`). Constraints: no push; goldens NEVER re-derived; ON ERROR NOT fixed; SE my-gap/SF-SG dr-refuses kept; all rc DIRECT (never pipeline tail); `pli80c` POSITIONAL; chain 01a1aa7d.

SUPERSEDED-BY-ABOVE (hop-4 full contract, items 1 done):

**E2E-52/P3-7 hop 4 CONTRACT IN FORCE (unchanged, docs-only; read LEARNINGS.md § "hop 4 IN FLIGHT" FIRST, it adds the validator facts and the three extra stale rows).** Recovery DONE this hop: HEAD `5d4fe25`, build rc=0 binary `8b374e623bc9e280…` (== registration), coverage baseline 139 rows 0/0 rc=0, prose rc=0. Execute: (1) COVERAGE.tsv via python column-edit (rows are huge; NEVER hand-match them): rewrite row `FILE.OPEN_STREAM` boundary — falsified `Still refused by name: PRINT/…` sentence kept VERBATIM as HISTORICAL, cite [C365] + golden/e52p7, pointer to the new row, id KEPT, provenance +[C365]; labelled [E2E-52/P3-7 CORRECTION] appends to rows `FILE.OPEN_STREAM_OUTPUT` (KEYFILE:19 0x1E50 NOW lowered as E52TE), `FILE.PUT_LIST` (PRINT/LINESIZE no longer open-refusal blockers; EXACT:4 unchanged), `FILE.OPEN_TITLE_STATIC` (LOAN2 blocker quote obsolete — now ON ERROR 58); NEW row `FILE.OPEN_PRINT_ATTRS` inserted after FILE.OPEN_STREAM_OUTPUT: perimeter S, manual_ref `p60:9.5=OPEN FILE(fname) [file-attributes];`, dr ACCEPTS, mine SUPPORTED, EXACT:10, runtime NONE, probes E52TA..TJ + `golden/probes11/P019B/P019B.REL` + `golden/probes10/P021/P021.REL`, corpus COPYLPT,DEPREC,KEYFILE,LOAN2,RETRIEVE (P019B/P021 NOT census names), boundary = the full refused-by-name list in the LEARNINGS § + corpus-users-are-not-parity-claims + byte-tier-only; confidence MEASURED; provenance `[C365]` + OPEN-MATRIX/OPEN-BLOCKS/PLAN/RESULTS paths (no duplicate leading cites). `python3 tools/coverage_check.py` rc=0 expect **140 rows 0/0** (its run also refreshes coverage-stats.json — commit that diff if moved). (2) PERIMETER.md line 38: one PROPOSED campaign-wide correction paragraph, falsified sentence kept verbatim (PRINT/PAGESIZE/LINESIZE C365; PAGE C359; PUT EDIT C360–C363). (3) RESULTS.md §P3-7: 10-probe measured table (TA 256B code 0035/0002 blk21B 0652; TB 384/003D/0006 29B 2E52; TC 384/003B/0011 27B 0E52; TD 256/0038/0002 24B 2652; TE 384/003F/0008 31B 1E50; TF 384/0041/0015 33B 3E52; TG 384/0040/0006 32B; TH 384/0041/0006 33B; TI 256/003A/0004 26B; TJ 256/003A/0002 26B — from tools/e2e_gate.py SPECIMENS comment), H1–H5 CONFIRMED + H6 refused-as-designed, TI falsifier VERBATIM (predicted w6 21 00 00, DR wrote 60 68), TG/TH 30-B totals FALSIFIED VERBATIM (32/33; encodings HIT, no falsifier fired), TJ DR-ACCEPTED via 21 2C 01, campaign 10 ok/10 ZERO dr-refuses, LOAN2 ADVANCED VERBATIM to `ON ERROR … line 58` + RETRIEVE to `OPEN option ENVIRONMENT … (line 31)`, registration chain ccf0036/6b8d851/f6fd2b9/gate 1243/0/a6e814f, sweep 114/0, §6 NOT-say byte-tier-only. (4) PLAN.md §5 progress table P3-7 row. (5) `python3 tools/file_prose_check.py` rc=0 standalone. (6) Durables (HANDOFF new item 0a-novies-new12 + PROGRESS close or hop-5 P3-8-PRE-REG contract), explicit-path commits, then renew (4/12 used of cap 12 — check handoff.config.json, NEVER stage it).
Constraints: NO new oracle campaign; no push; goldens NEVER re-derived; ON ERROR 58 NOT fixed; SE my-gap/SF-SG dr-refuses kept; ledger ENDS C365; all rc DIRECT (never a pipeline tail); `pli80c` POSITIONAL.

SUPERSEDED-BY-ABOVE: **E2E-52/P3-7 hop 3: BUILD + CMPs + LOAN2 + SWEEP + MARKERS + ARM COMMIT + REGISTRATION (1/3 SPECIMENS+inventory, 2/3 census) + GATE + CLAIM C365 ALL LANDED; COVERAGE + RESULTS/PLAN ROWS + DURABLES OWED (hop 4).**

ACCEPTED (measured this hop, all rc DIRECT): `dune build` rc=0 after ONE defect fix — the hop-2
draft had written literal `\u00a7`/`\u2014` escapes in four message/comment strings (4 NEW Warning 14
illegal-backslash AND mojibake `u00a7` inside refusal text); replaced with the real characters this
file already uses (89 times). A second draft defect `| A_zero | A_lit16 _ -> assert false` had a
redundant sub-pattern (1 NEW Warning 12) — removed, behaviour unchanged (A_zero is handled by the
preceding case). Final: binary sha256 `8b374e623bc9e280fa148ac1f9382ddecaf160a0315d21bd31223a66fbc924cd`,
codegen warning histogram **68 == baseline** (per-File count of the full clean log; the log double-prints
each warning, so 68 lines = 34 unique). **cmp E52TA..E52TJ whole-file rc=0 = 10/10** vs `golden/e52p7/`
(goldens `272a996`, NEVER re-derived). LOAN2 UNMODIFIED POSITIONAL rc=2, blocker ADVANCED VERBATIM past
54/56 to `codegen: ON ERROR is not implemented [TBD] (only ENDFILE(<file>) and UNDEFINEDFILE(<file>) have
a DR lowering; line 58)` — §P3-7 §3 prediction HIT, **NOT fixed** (later subround). Sweep
`python3 build/e52p3/sweep.py E46N E46K E51 E52 P086 R10` = **114 specimens byte-exact / 0 FAIL**
(`build/e52p7-verify/sweep-e52p7.log`) — NOT 110: the bank grew by the four E52SA..SD rows registered in
`91592c0` AFTER hop 12 counted 110. Markers rc=2 intact: E46K4, E46K15, E46N21, E52PF, E52PU, E52PV,
E52RE + SE/SF/SG. Commits: arm `ccf0036` (ocaml/lib/codegen.ml only); SPECIMENS +10 rows and sanctioned
`--update-inventory` 1233→**1243** diff EXACTLY +10 specimen lines, 0 removals, refusals stay 186
(`6b8d851`); census OWN write path `corpus_census.py --check spec/census/corpus-census.json` rc=0 counts
UNCHANGED 15/0/26/0 (`f6fd2b9`) — TWO rows moved VERBATIM: LOAN2 (line 54→58, see above) and **RETRIEVE
advanced past its line-19 `title(name) print` open to `OPEN option ENVIRONMENT … (line 31)`** — a real
advance, no claim; every other OPEN row unchanged because the census truncates the message where the
pinned `OPEN option <KEY> is outside` PREFIX still stands. FULL gate REAL **rc=0** DIRECT
`build/gate-e52p7-reg.log` (1243/0 of 1243, negatives 186/186, divergence 9/9, coverage 139 rows 0/0,
census 15/0/26/0, prose 5). Claim **C365** from MEASURED BYTES ONLY committed BEFORE COVERAGE `a6e814f`.

FALSIFIED THIS HOP (procedure, mine): a global `\'`→`'` text replace in `tools/e2e_gate.py` to clean
three apostrophes in my NEW COMMENT destroyed 30 legitimate escapes inside single-quoted Python strings
→ SyntaxError at line 3647. Recovered by rewriting the file from `git show HEAD:tools/e2e_gate.py`
(verified clean in `git status` BEFORE my edit, so only my own work was lost) and re-applying the block
without backslashes; `python3 -m py_compile` rc=0 and `git diff` = 72 insertions / 0 deletions before
commit. LESSON: never bulk-replace quote escapes across a Python file; scope replacements to the block
you added, and run py_compile after ANY tools/ edit.

OWED at hop 4 (small, docs-only + one ledger row; NO new oracle campaign):
(1) COVERAGE: row 52 `FILE.OPEN_STREAM` perimeter/boundary text still says `Still refused by name: PRINT/…`
    — FALSIFIED by the arm; rewrite it VERBATIM-preserving history (falsified clauses kept as HISTORICAL,
    id KEPT) citing [C365] + the 10 goldens, and PROPOSED new row `FILE.OPEN_PRINT_ATTRS`
    (mine_status=SUPPORTED, rel_parity EXACT:10, probes E52TA..TJ, corpus COPYLPT/DEPREC/KEYFILE/LOAN2/
    P019B/P021/RETRIEVE, boundary naming every KEPT refusal). Then `python3 tools/coverage_check.py` rc=0
    (expect 140 rows 0/0) and refresh coverage stats via its OWN write path.
(2) `spec/lab-evidence/e2e52-p3/RESULTS.md` §P3-7 (10-probe table with the measured sizes/code/DATA from
    tools/e2e_gate.py's SPECIMENS comment, hypothesis verdicts H1-H5 CONFIRMED, TI falsifier + TG/TH total
    falsifications VERBATIM, TJ accept branch, LOAN2/RETRIEVE advances, §6 NOT-say byte-tier-only) +
    `PLAN.md` §5 P3-7 progress row; `python3 tools/file_prose_check.py` rc=0 standalone.
(3) Durables + explicit-path commits; renewal chain 01a1aa7d — check `handoff.config.json` cap before
    renewing. Ledger ENDS **C365**. Constraints: no push; goldens NEVER re-derived; SE my-gap + SF/SG
    dr-refuses KEPT; operator `handoff.config.json` NEVER staged; all rc DIRECT (never a pipeline tail);
    `pli80c` POSITIONAL. Standing PROPOSALS (never authorization): ON ERROR (LOAN2:58) as P3-8;
    SE `?REVOP` arm; ENVIRONMENT (RETRIEVE:31 / REPORT:29 36-B `4E52` block).

### E2E-52/P3-7 hop 1 DONE — PRE-REGISTRATION LANDED `2bca084` (ZERO ocaml/, ZERO oracle); campaign `e52p7` OWED (2026-11-05, fresh chain)

Verified this hop: HEAD `c0ce1a1` at start, checkpoint **g341-6c8d927fdd83 CURRENT + attested** by five-source
hash replay (`/handoff verify` has no CLI path; the replay is the documented stand-in); ledger ENDS **C364**;
build rc=0 binary `0efc35e6d4ff81bd…`; LOAN2 blocker VERBATIM line 54 `OPEN option PRINT … [TBD]` (rc=2 DIRECT);
P019B:3 / RETRIEVE:19 same, P021:4 + KEYFILE:16 `OPEN option KEYED`, COPYLPT SKIP-count, DEPREC array.
P3-6 NOT reopened. The PRINT/PAGESIZE/LINESIZE class is fully decoded from EXISTING evidence into shapes
A–F (bytes + w1 bits + the register-reuse ladder incl. `PAGESIZE(0)` = bit 0x2000 with a ZERO word, and the
`MVI L,v` / `MOV L,B` / `MOV L,H` restorations) in `spec/lab-evidence/e2e52-p3/PLAN.md` §P3-7 §2.
Probes **E52TA..TJ** committed BEFORE any compiler byte; four UNDECIDABLE boundaries (TG/TH/TI/TJ) carry
byte-exact predictions and falsifiers.

NEXT ACTION (hop 2 CLOSED mid-arm, hop 3 OWED): campaign e52p7 MEASURED 10 ok/10 rc DIRECT, ZERO
dr-refuses, goldens committed VERBATIM `272a996`; decode/ladder/matrix in `LEARNINGS.md` § "hop 2:
campaign e52p7 MEASURED". ARM codegen.ml ONLY, UNCOMMITTED in tree: open_subset_keys +PRINT/
PAGESIZE/LINESIZE; refuse_file_opt OPEN narrative rewritten (pinned KEYED/RECORD/SEQUENTIAL/
UPDATE prefixes kept — census msgs WILL move); open_mode_word n_print guards (print+INPUT/print+
OUTPUT refuse) + print base 0x0652/0x0E52 branch before modeless; open_attr/A_var classifier
open_attr_plan enforcing the measured matrix; open_emit_words ladder replaces all three hardcoded
w2..w6 tails; op_mvi_l/op_mov_l_h added. ONE compile error was FIXED (Unbound value s in the
defensive titled refusal → plain failwith) but the build was NOT re-run since — FIRST ACTION hop 3:
`cd ocaml && eval "$(opam env)" && dune build` rc DIRECT (rc=0 NOT yet verified; the tail-pipe
masked rc=1 AGAIN this hop). Then warnings histogram vs 68; cmp TA..TJ whole-file rc=0 vs
golden/e52p7; LOAN2 UNMODIFIED POSITIONAL blocker VERBATIM (predicted `ON ERROR … line 58`, do NOT
fix); sweep 110; markers E46K4/K15/N21/E52PF/PU/PV/RE rc=2; COMMIT arm explicit paths; then
registration: SPECIMENS +10, --update-inventory delta from 1233 (NO refusal rows — zero dr-refuses),
census OWN write path FIRST, gate rc=0 DIRECT build/gate-e52p7-reg.log, C365 measured-bytes-only
BEFORE COVERAGE, coverage_check+prose rc=0, RESULTS §P3-7 + PLAN §5 row, durables.
Constraints: no push; goldens NEVER re-derived; P3-6 `ON UNDEFINEDFILE` intact; SE my-gap / SF/SG dr-refuses kept;
operator `handoff.config.json` NEVER staged; all rc DIRECT (never a pipeline's); `pli80c` POSITIONAL; renewal
chain FRESH (no `.pi-guard/renewal-state.json`, 0/12 used); ledger ENDS **C364** until C365 is measured.

SUPERSEDED-BY-ABOVE: NEXT ACTION: **NO active round on this chain — it is CAPPED at hop 12/12.** This session:
refresh+attest via `handoff_finalize`, commit the managed blocks VERBATIM, reverify freshness,
**STOP — NEVER `handoff_renew` past the cap.** SUCCESSOR (only after the operator archives/resets
`.pi-guard/renewal-state.json`): PROPOSED **E2E-52/P3-7 = OPEN PRINT / PAGESIZE / LINESIZE** from
LOAN2 line-54 — read HANDOFF item 0a-novies-new8 + LEARNINGS § "hop 12 = CAP"; inspect existing
`spec/lab-evidence/e2e41-p0/OPEN-MATRIX.tsv` + LOAN2/COPYLPT goldens; PROPOSED probes + PLAN
§P3-7 COMMITTED BEFORE any `ocaml/` byte; NO oracle campaign without a new operator brief.
Constraints: no push; goldens NEVER re-derived; SE stays my-gap, SF/SG stay dr-refuses; LOAN2
refuses at line 54 UNFIXED; no runtime assertions; operator `handoff.config.json` NEVER staged;
all rc DIRECT; `pli80c` POSITIONAL; ledger ENDS **C364**.

SUPERSEDED-BY-ABOVE:
### E2E-52/P3-6 hop 11 DONE — campaign e52p6 MEASURED (5 ok/7) + ARM LANDED `8fc0a3b` (4/4 accepted cmp rc=0); REGISTRATION OWED at hop 12 = CAP 12/12 (read `LEARNINGS.md` § "hop 11: campaign e52p6 MEASURED + ARM LANDED" FIRST)

HEAD `8fc0a3b`; binary `0efc35e6d4ff81bd…`; codegen warnings 68 == baseline; sweep **110/0**;
markers E46K4/K15/N21/E52PF/PU/PV/RE rc=2; LOAN2 rc=2 VERBATIM at **line 54 OPEN PRINT**
(§3 prediction HIT, never fitted); SF+SG dr-refuses; SE measured-accepted, KEPT unarmed.
NORTH (hop 12 FIRST): the 5 campaign goldens are UNTRACKED (`golden/e52p6/`) — commit them by explicit path (evidence, never re-derived); ocaml/build-warn-e52p6.log is scratch, never stage.

NEXT (hop 12 = CAP, docs+panel only, ZERO new oracle campaigns): execute the PROPOSED hop-12
contract in that LEARNINGS § — SPECIMENS SA SB SC SD + honest refusal rows SF/SG (dr-refuses,
markers from MY stderr WITH [TBD]) and SE (my-gap); sanctioned `--update-inventory` (measure the
real delta from 1229); census OWN write path FIRST (line-44 line REPLACED by line-54, EXPR1/EXPR2
catch-all moved); FULL gate rc=0 DIRECT `build/gate-e52p6-reg.log`; **C364 measured-bytes-only
BEFORE** the COVERAGE `ON`-unit rewrite; coverage_check + prose rc=0; RESULTS §P3-6 + PLAN §5 row;
durables; then **`handoff_finalize` — NEVER `handoff_renew` past the cap**.
Constraints: no push; goldens NEVER re-derived; operator `handoff.config.json` NEVER staged; all rc
DIRECT (the masked-rc trap fired again this hop); pli80c POSITIONAL; ledger ENDS **C363**.

SUPERSEDED-BY-ABOVE: 
### E2E-52/P3-6 hop 10 DONE — ON-UNDEFINEDFILE EVIDENCE DECODED from EXISTING goldens; PRE-REGISTRATION LANDED (probes + PLAN §P3-6); CAMPAIGN e52p6 OWED (2026-11-05, hop 10/12; read `LEARNINGS.md` § "hop 10: ON-UNDEFINEDFILE EVIDENCE DECODED" FIRST + PLAN §P3-6)

LANDED (all rc DIRECT, ZERO `ocaml/` byte, ZERO oracle call): clean build binary
`e55e892c346741b2…` (== hop-9 final). LOAN2 line-44 class decoded from the EXISTING
`golden/first/LOAN2/LOAN2.REL`: registration `LXI H,*OUTPUT / MVI A,06 / CALL ?ONCOP /
JMP slot` (condition byte **06** — no claim names it; candidate **C364**), handler ending in
a GOTO emits the inline chain then an inline `C3` and **NO C9 RET**; recovery pad
`LHLD *D(0318) / SPHL / CALL ?RECOV` at the target label; main-entry `DAD SP/SHLD` SP-save
present. FALSIFICATIONS kept verbatim: the codegen refusal comment's "no DR sample" claim
(LOAN2 golden IS the sample for a BEGIN…END ending in a bare goto) and "arm = codegen.ml
ONLY" (bind.ml `refs_stmt` classifies the Sdobegin handler's trailing goto `Rk_plain`
same-block → demands NO cell/pad — contradicts the golden; the arm is **bind.ml +
codegen.ml**). P088I/P089I preserved transcripts: bare `on undefinedfile x = 1;` = PASS-2
`SYNTAX ?` dr-refuses; the `(f)` form parses clean; BOTH .RELs have NO CODE (pass-2 error
killed the object) — verdicts only, never bytes. 7 probes `probes/E52SA..E52SG.PLI`
(CRLF+bare ^Z, ≤71 cols verified; collision greps probes/+INVENTORY EMPTY; tag `e52p6`
verified UNUSED) + `PLAN.md` §P3-6 (predictions: SA code-06 + RET no-pad; SB SP-save + pad +
no-RET + JMP-over→pad; SC pad/continuation targets INDEPENDENT; SD [C201] direct pair with
06; SE/SG [TBD]; SF dr-refuses; LOAN2 next blocker predicted past 44 = counted console SKIP
50 or `OPEN option PRINT … (line 54)`; NEVER fit) COMMITTED BEFORE any ocaml/ byte.

NEXT (hop 11): (1) ONE grouped campaign `PLI_SRC=probes timeout 900 python3 oracle/batch.py
E52SA E52SB E52SC E52SD E52SE E52SF E52SG --tag e52p6 --switches '$L$D'` rc DIRECT; read
every .PRN; reldump goldens to `build/e52p6/`; classify honestly (SF dr-refuses row marker =
MY re-measured stderr WITH [TBD]; SE/SG if DR-accepted stay my-gap boundaries, refuse BY
NAME, never fitted); keep MISSes verbatim. (2) Arm PLAN §P3-6 §4: bind `refs_stmt` Rk_on for
`Sdobegin` ending in bare `Sgoto`; codegen `on_reg_prefix` condition-code parameter
(endfile 05 [C109] / undefinedfile 06 measured); handler-tail-goto inline lowering, NO RET;
every other goto-containing handler keeps refusing BY NAME with the text corrected to name
the measured samples. Build rc=0 DIRECT; cmp accepted probes whole-file rc=0 vs
`golden/e52p6/`; sweep 101; markers E46K4/K15/N21/E52PF/PU/PV/RE rc=2; LOAN2 UNMODIFIED
POSITIONAL blocker VERBATIM; commit. (3) Registration at hop 11 if budget allows, else
**hop 12 = CAP 12/12**: SPECIMENS +accepted + honest refusal rows, sanctioned
`--update-inventory` 1229→1229+N (+refusals), census OWN write path FIRST (line-44 census
line REPLACED; drift aborts the gate before the byte panel), FULL gate rc=0 DIRECT
`build/gate-e52p6-reg.log`, claim **C364** measured-bytes-only committed **BEFORE** the
COVERAGE rewrite, coverage_check + prose rc=0, RESULTS §P3-6 + PLAN §5 row, durables — then
`handoff_finalize`; NEVER `handoff_renew` past the cap; the operator archives/resets renewal
state before any further hop.

Constraints: no push; goldens NEVER re-derived; operator `handoff.config.json` NEVER staged
(dirty standing edit); all rc DIRECT (pipeline-masking trap fired 3 hops running); `pli80c`
POSITIONAL; ledger ENDS **C363**; renewals autonomous (10/12 consumed, cap 12); campaign
continues.

SUPERSEDED-BY-ABOVE (kept as written): ### E2E-52/P3-5 hop 9 DONE — DEFENSIVE ARMS + FULL REGISTRATION LANDED; SUBROUND P3-5 CLOSED; LOAN2 AT ON UNDEFINEDFILE (2026-11-05, hop 9/12; read `LEARNINGS.md` § "hop 9: DEFENSIVE ARMS + REGISTRATION LANDED" FIRST)

LANDED (all rc DIRECT, evidence build/e52p5-hop9/ + build/gate-e52p5-reg.log): defensive `| PIrep _ -> a`
prescan-fold arm `a008840` (histogram codegen 70→68, diff EXACTLY −2 W8 at the fixed site — honest
method = replay-build `aeda739` then diff); named REVERSE parse refusal `3a494c3` (panel requires
[TBD]; `expected )` prediction FALSIFIED); SPECIMENS +7 + RE row + `--update-inventory` 1222→1229 +
182→183 EXACTLY `4dbdaa0`; census own write path rc=0 counts 15/0/26/0 UNCHANGED, LOAN2 blocker
VERBATIM `codegen: ON UNDEFINEDFILE is not implemented [TBD] (only ENDFILE(<file>) has a DR lowering;
line 44)` (line-177 PIvar prediction FALSIFIED at stage level, NOT fixed); FULL gate REAL rc=0
1229/0, 183/183, 9/9, 139 0/0, prose 5; claim **C363** measured-bytes-only `c940426` BEFORE COVERAGE
EXACT 35→42 `2be56f0` (coverage_check rc=0); prose rc=0; RESULTS §P3-5 + PLAN §5 row `a1a82d4`.
Binary `e55e892c346741b2…` (clean rebuild; 7 cmps + sweep 101/0 re-verified on it).
NEXT (hop 10): PROPOSED P3-6 = ON UNDEFINEDFILE (LOAN2 44) — NEW ground, write PLAN §P3-6 + probes,
collision-grep, COMMIT BEFORE any ocaml/ byte, ONE grouped campaign rc DIRECT; boundaries KEPT.
Ledger ENDS **C363**; goldens NEVER re-derived; operator `handoff.config.json` NEVER staged; all rc
DIRECT (pipeline trap); pli80c POSITIONAL; renewals autonomous (cap 12); campaign continues.

SUPERSEDED-BY-ABOVE (kept as written): ### E2E-52/P3-5 hop 8 DONE — ARM LANDED, ALL 7 ACCEPTED PROBES BYTE-EXACT (`aeda739`); one defensive fold arm + sweep/markers/LOAN2 + REGISTRATION OWED (2026-11-05, hop 8/12; read `LEARNINGS.md` § "E2E-52/P3-5 hop 8: ARM LANDED" FIRST)

MEASURED this hop (all rc DIRECT): `dune build` rc=0, binary `345644822818326f…` →
`a55ef4eb7c7e51fb…`; **cmp RA RB RD RF RH RI RJ whole-file rc=0 vs `golden/e52p5/`** (headline
class MET, never fitted). RB's first-try MISS at octet 275 decoded the PATCH LAW: a non-final
repetition's forward JP goes to the START OF THE NEXT ITEM (slot 0038 → 0x4F), a final one to
the close `?QIOOP` (RA 0028 → 0x3F) — fixed by flushing `repl_exit` at the top of `emit_item`.
RC (BY, parser), RG (char-var inner, authorizer), RE (`expected )`, parser) rc=2 BY NAME —
boundaries KEPT as pre-registered. UNCOMMITTED-NOTHING (arm is in `aeda739`); tree carries
only the guard blocks + operator config.
NEXT (hop 9): (1) add the defensive `| PIrep _ -> a` arm to the prescan inner fold
(codegen.ml ~3581, Warning 8 / PA trap class; unreachable but must be closed), rebuild rc=0
DIRECT, re-run the 7 cmps (expect byte-identical), per-File warning histogram vs baseline 70;
(2) sweep 89; markers E46K4/K15/N21/E52PF/PU/PV rc=2; LOAN2 UNMODIFIED POSITIONAL — predicted
blocker line-177 `PIvar yp`, record VERBATIM, NEVER fit; commit; (3) registration per PLAN
§P3-5 §5: SPECIMENS +7 + RE REJECTS/NEG_META row (marker = MY re-measured `expected )`),
sanctioned `--update-inventory` 1222→1229 + negatives 182→183, census OWN write path FIRST
(212 line REPLACED; drift aborts the gate before the byte panel), FULL gate rc=0 DIRECT
`build/gate-e52p5-reg.log`, **C363 from MEASURED BYTES ONLY committed BEFORE** the COVERAGE
`IO.PUT_EDIT` rewrite (EXACT 35→42), coverage_check+prose rc=0, RESULTS §P3-5 + PLAN §5 row,
durables, renew 9/12. Constraints: no push; goldens NEVER re-derived; operator
`handoff.config.json` NEVER staged; all rc DIRECT; pli80c POSITIONAL; ledger ENDS C362.

SUPERSEDED-BY-ABOVE (kept as written): ### E2E-52/P3-5 hop 7 DONE### E2E-52/P3-5 hop 7 DONE (arm sites ALL verified by code reading, ZERO ocaml/ byte); ARM OWED — execute `LEARNINGS.md` § "hop 7: ARM SITES ALL VERIFIED" PROPOSED contract (2026-11-05; fresh chain hop 7/12; read that § + PLAN §P3-5 §4 FIRST)

Verified THIS hop: HEAD `391d809` clean (operator config excepted); build rc=0 DIRECT binary
`345644822818326f…` (== headline hash); RA/RB/RF reldumps re-read — the rep loop IS
lower_doto's TO-arm shape with a ONE-item body: init UNCONDITIONAL `LXI H,from / SHLD i`
(no ladder, no 1-byte-cell route), immediate test `LHLD i / LXI B,-(to+1) / DAD B / MOV A,H /
ORA A / JP slot` (cc<=3 refuse UNMEASURED), RF var-bound `LHLD n / SHLD temp / head: LHLD temp /
XCHG / LHLD i / ?IS22N / JM slot` byte-identical to the existing Eident arm (temp via
`st.base + max auto_end st.floor + 2*st.temps`, kill_de at head), step `LHLD/INX H/SHLD/JMP
reloc Code head`, exit patched by `emit_triple st jpslot st.lc` AT THE END OF THE LOOP (RB:
JP goes to the NEXT item's chain; ONE ?QIOOP after the LAST item). Exact edit sites and the
five non-exhaustive pitem matches (the PA trap) are in that §: parser.ml `parse_rep_spec`
(REPSPEC child 0 = Eident; BY -> `err p` parse refusal; RE stays `expected )`), codegen.ml
`type pitem` +PIrep, `match_put_edit` data-walker -> pitem accumulation (BOTH routes), prescan
folds ~3558/~3570 (inner cells ONCE), `authorize_file_edit_item` ~11941 (admit PIrep iff inner
PIlit or PInum-via-edit_num_tree; RG keeps refusing = boundary KEPT), defensive arm at
`authorize_file_item` ~11776 (file_items already refuses Pi_rep on the LIST route), item loop
~12176 refactor to named `emit_item` + PIrep lowering. bind.ml walk sites tolerate the new
child (code-read; build measures). NEXT hop 8: write the arm, `dune build` rc=0 DIRECT
(NEVER `dune build | tail` — trap fired 3 hops), warnings histogram per-File vs 70, binary
!= `345644822818326f…`, cmp **RA RB RD RF RH RI RJ rc=0** vs `golden/e52p5/`, RC/RG/RE rc=2,
sweep 89, markers E46K4/K15/N21/E52PF/PU/PV rc=2, LOAN2 UNMODIFIED POSITIONAL — predicted
line-177 `PIvar yp`, RECORD VERBATIM NEVER fit; commit arm; then registration: SPECIMENS +7,
sanctioned `--update-inventory` 1222->1229 + negatives 182->183 (RE row, marker = MY actual
re-measured `expected )`), census OWN write path FIRST, FULL gate rc=0 DIRECT
`build/gate-e52p5-reg.log`, **C363 MEASURED BYTES ONLY BEFORE** COVERAGE `IO.PUT_EDIT`
rewrite (EXACT 35->42), coverage_check+prose rc=0, RESULTS §P3-5 + PLAN §5 row, durables,
renew (8/12). Constraints: no push; goldens NEVER re-derived; operator handoff.config.json
NEVER staged; all rc DIRECT; pli80c POSITIONAL; ledger ENDS C362; renewals autonomous, cap 12.

SUPERSEDED-BY-ABOVE (kept as written): ### E2E-52/P3-5 campaign e52p5 MEASURED (9 ok/10, goldens `676fb9d`); ARM parser.ml+codegen.ml OWED NOW (2026-11-05; fresh chain hop 6/12; read `LEARNINGS.md` § "E2E-52/P3-5 CAMPAIGN e52p5 MEASURED + ALL BYTES DECODED; ARM OWED" + PLAN §P3-5 FIRST)

ZERO `ocaml/` byte this hop. Executed step (1): ONE grouped campaign rc=0 DIRECT; E52RE
**dr-refuses** (`SYNTAX ?`, no .REL — register REJECTS+NEG_META row, marker from MY actual
`expected )`); 9 accepted NO ERROR(S) both passes; ALL reldumps decoded (every byte list in
the LEARNINGS §): RA/RD == PLAN §2 loop law (H1 CONFIRMED); RF variable-bound == EXISTING
`lower_doto` var-bound shape byte-identical (H3 CONFIRMED accept); RH console loop == file
loop (H2 CONFIRMED); RI table `80 00 80 02 03 FF 81 81` (H6 CONFIRMED); RJ body = P3-4
numeric chain in loop; RC BY **ACCEPTED by DR** (INX H × n, test unchanged) — boundary KEPT,
parse-refuse; RG char-var inner — `authorize_file_edit_item` plain route refuses PIvar-char,
boundary KEPT (§4e). cmp targets = **RA RB RD RF RH RI RJ (7)**. NEXT: (2) arm per
LEARNINGS § PROPOSED (i)-(ii): parser `parse_rep_spec` REPSPEC child 0 = index `Eident` + BY
parse-refusal; codegen `PIrep of pitem * Ast.expr`, shared `data` walker admits Pi_rep, prescan
fold inner-cells-ONCE, authorize admits PIrep(inner-admitted) else BY NAME, lower_put_items_gen
emits §2 immediate loop (cc>=4 only; to<=2/from=0/var-FROM/nested refuse UNMEASURED) or RF
var-bound loop around ONE inner chain via emit_triple/reloc; build rc=0 DIRECT; cmp 7 rc=0;
RC/RG/RE rc=2; sweep 89; markers E46K4/K15/N21/E52PF/PU/PV rc=2; LOAN2 UNMODIFIED POSITIONAL,
blocker VERBATIM (predicted line-177 `PIvar yp`; NEVER fit). (3) registration: SPECIMENS +7,
--update-inventory 1222→1229 +1 refusal 182→183, census OWN write path FIRST, FULL gate rc=0
DIRECT build/gate-e52p5-reg.log, **C363 MEASURED BYTES ONLY BEFORE** COVERAGE IO.PUT_EDIT
rewrite (EXACT 35→42), coverage_check+prose rc=0, RESULTS §P3-5 + PLAN §5 row, durables.
Constraints: no push; goldens NEVER re-derived; operator handoff.config.json NEVER staged; all
rc DIRECT; pli80c POSITIONAL; ledger ENDS C362; renewals autonomous (6/12 consumed, cap 12).

SUPERSEDED-BY-ABOVE (kept as written): ### E2E-52/P3-5 **PRE-REGISTERED** at `67e5414`; ORACLE CAMPAIGN `e52p5` OWED NOW (2026-11-05; fresh chain hop 5/12; read `LEARNINGS.md` § "E2E-52/P3-5 PRE-REGISTRATION LANDED" + PLAN §P3-5 FIRST)

LANDED this hop (all rc DIRECT, ZERO `ocaml/` byte, ZERO oracle call): g320 block committed
VERBATIM `8f1f7ce`; build rc=0 binary `345644822818326f…`; LOAN2 golden `line` span
0944-099F decoded — the **`Pi_rep` DATA-item loop law**: init `LXI H,from/SHLD ind`; test
`LHLD/LXI B,-(to+1)/DAD B/MOV A,H/ORA A/JP P exit`; ONE literal body chain
`?SLCTS/?EDTOV`; step `LHLD/INX H/SHLD/JMP`; exit `?QIOOP`; table `80 00 03 FF 81` —
rep = **0 format bytes** (bind.ml:1155 `[verify]` now golden-corroborated).
**FALSIFIED by code reading: "codegen.ml ONLY"** — `parse_rep_spec` drops index name and
BY; arm = parser.ml (REPSPEC child 0 = index `Eident`; BY parse-refusal; REVERSE
unparseable today) + codegen.ml. Pre-registration `67e5414`: PLAN §P3-5 (per-probe
predictions, H1-H6, LOAN2 next-blocker prediction line-177 `PIvar yp`, NEVER fit) + probes
E52RA..E52RJ (CRLF+^Z ≤71 verified) + BASELINE-MINE-p35 (all 10 rc=2 unarmed: 8
matcher-split, RH console deferred, RE parser-stage). Tag `e52p5` unused; E52R* EMPTY.
**NEXT — execute PLAN §P3-5 §5:** (1) ONE campaign `PLI_SRC=probes timeout 900 python3
oracle/batch.py E52RA E52RB E52RC E52RD E52RE E52RF E52RG E52RH E52RI E52RJ --tag e52p5
--switches '$L$D'` rc DIRECT; read .PRNs; reldump to build/e52p5/; classify
`dr-refuses`/`my-gap`/`unmeasured`; keep MISSes verbatim. (2) arm per §2a/§4; cmp every
ACCEPTED probe whole-file rc=0; sweep 89; markers E46K4/K15/N21/E52PF/PU/PV rc=2; LOAN2
rerun UNMODIFIED POSITIONAL, blocker VERBATIM (predicted `line 177` — record, do NOT fit).
(3) registration: SPECIMENS +N; sanctioned `--update-inventory` 1222→1222+N; census OWN
write path FIRST (212 line REPLACED; drift aborts gate); FULL gate rc=0 DIRECT
`build/gate-e52p5-reg.log`; claim **C363** MEASURED BYTES ONLY BEFORE the COVERAGE
`IO.PUT_EDIT` rewrite; coverage_check+prose rc=0; RESULTS §P3-5 + PLAN §5 row; durables.
Constraints: no push; goldens NEVER re-derived; operator `handoff.config.json` NEVER
staged; all rc DIRECT (pipeline trap fired THREE hops); `pli80c` POSITIONAL; ledger ENDS
**C362**; renewals autonomous (5/12 consumed, cap 12); campaign continues.

SUPERSEDED-BY-ABOVE: ### E2E-52/P3-4 **CLOSED** (RESULTS §P3-4 + PLAN §5 row at `b76cd2f`; headline re-held a 3rd time); SUBROUND **P3-5 PRE-REGISTRATION OWED** (2026-11-05; fresh chain hop 4/12; read `LEARNINGS.md` § "E2E-52/P3-4 CLOSED … LOAN2:212 NEXT-BLOCKER EVIDENCE DECODED; P3-5 PRE-REGISTRATION OWED" FIRST)

LANDED this hop (all rc DIRECT, ZERO `ocaml/` byte, ZERO oracle call): `dune build` rc=0 clean
binary sha256 `345644822818326f442a…` (== the headline hash); **10/10 accepted-probe whole-file
cmps re-measured rc=0 THIS session** (E52PA 384 B vs the EXISTING golden sha `d7b4e7f3…` = the
headline re-held; PP..PZ 256 B vs `golden/e52p3d/`); refusals E52PU/E52PV/E52PF rc=2 with pinned
markers; LOAN2 rc=2 VERBATIM `(line 212)`; `RESULTS.md` §P3-4 (campaign table, every hypothesis
verdict verbatim, root cause, registration, §6 NOT-say) + `PLAN.md` §5 P3-4 progress row committed
`b76cd2f`; prose rc=0 `build/prose-check-e52p3e-results.log`. Evidence in ignored `build/e52p3e/`.

**DECODING DONE (no oracle run needed for the NEXT blocker):** LOAN2 212 is
`put file(output) skip edit ('-------','------------',('---------------' do i = 1 to 4)) (a);` —
the failing class is the **`Ast.Pi_rep` DATA-item DO-repetition in the DATA half** (parser.ml 1018);
`match_put_edit`'s `data` walker admits only `Pi_data`/`Pi_fmtlist` so `classify_item` is never
reached, hence the line-212 catch. `Pi_rep` ≠ the P3-4 `Pi_repgrp` format group. `bind.ml:1155`
annotates `Pi_rep` as 0 format bytes **"[verify]"** — UNVERIFIED, and NO golden contains a
`Pi_rep` in a file EDIT list, so its lowering is **UNMEASURED**.

**NEXT (successor) — subround P3-5, PRE-REGISTER FIRST:**
(1) `PLAN.md` §P3-5 (measured blocker VERBATIM + the 212 source line + the Pi_rep/Pi_repgrp
distinction + hypotheses H1 file-route data-rep encoding, H2 console-route independence, H3
variable-bound, H4 `BY`/`REVERSE` refusal, H5 rep-inside-rep-group; per-probe PREDICTED bytes;
arm sketch; boundaries KEPT: DEC formal/deref, numeric-literal, PIvar bin-var file route, counted
SKIP/PAGE+EDIT, format-COUNT expression, group count 0, x 14..128 gap; predictions incl. the LOAN2
next-blocker prediction — expected to ADVANCE past 212 to the NEXT unsampled class, never fit)
AND the probes `probes/E52RA..E52R*.PLI` (CRLF + bare ^Z, ≤71 cols, skeletons from probes/E52PP
style) — grep `probes/` + `spec/INVENTORY.txt` for name collisions and VERIFY the tag `e52p5`
is UNUSED; **COMMIT PLAN + probes BEFORE any ocaml/ byte** (explicit paths; if a guard-block
refresh landed uncommitted, commit it VERBATIM first).
(2) ONE grouped campaign `PLI_SRC=probes timeout 900 python3 oracle/batch.py <names> --tag e52p5
--switches '$L$D'` rc DIRECT; read every .PRN; reldump new goldens to `build/e52p5/`; classify
all differences (`dr-refuses`/`my-gap`/`unmeasured`); keep MISSes verbatim; also decode the
procedure-`line` CODE span from the EXISTING LOAN2 golden as corroboration.
(3) arm (codegen.ml ONLY, after measurement) + full sweep + markers rc=2 + LOAN2 rerun UNMODIFIED
positional, blocker VERBATIM.
(4) registration: SPECIMENS + sanctioned `--update-inventory` (expect 1222 → 1222+N), census via
its OWN write path FIRST (messages WILL move), FULL gate rc=0 DIRECT `build/gate-e52p5-reg.log`,
claim **C363** from MEASURED BYTES ONLY committed **BEFORE** the COVERAGE `IO.PUT_EDIT` rewrite,
coverage_check + prose rc=0, RESULTS §P3-5 + PLAN §5 row, durables.
Constraints: no push; goldens NEVER re-derived; operator `handoff.config.json` NEVER staged
(dirty standing edit); all rc DIRECT (the pipeline-masking trap has fired THREE hops running);
`pli80c` POSITIONAL (`pli80c [-d] IN.PLI OUT.REL`); renewals autonomous (4/12 consumed, cap 12);
campaign continues past every blocker; ledger ENDS **C362**.

SUPERSEDED-BY-ABOVE: ### E2E-52/P3-4 REGISTRATION LANDED (gate rc=0 1222/0, ledger ENDS C362, COVERAGE EXACT:35); RESULTS/PLAN ROWS + P3-5 OWED (2026-11-05; fresh chain hop 3/12; read `LEARNINGS.md` § "E2E-52/P3-4 REGISTRATION LANDED (steps 1-5 minus RESULTS/PLAN); P3-4 CLOSE OWED" FIRST)

LANDED this hop (all rc DIRECT): guard block `2c51941`; build rc=0 binary
`345644822818326f…`; 10/10 cmps re-verified incl. E52PA vs EXISTING golden sha `d7b4e7f32b9c…`
= headline re-held; PU/PV post-fix stderr re-measured rc=2 BY NAME; SPECIMENS 10 +
dr-refuses REJECTS/NEG_META rows + `--update-inventory` rc=0 EXACTLY 1212→1222 & 180→182
(`e397ed9`); census own write path rc=0 counts IDENTICAL 15/0/26/0, the 3 predicted msg moves
(ACKTST numeric-item-unproven, FSCAN char-store-non-literal, LOAN2 line-212 VERBATIM);
FULL gate **REAL rc=0 DIRECT** `build/gate-e52p3d-reg.log` (1222/0, 182/182, 9/9, 139 0/0,
15/0/26/0, prose 5); **C362** measured-bytes-only committed `1de3e28` BEFORE the COVERAGE
`IO.PUT_EDIT` rewrite `8c3b0b4` (EXACT:25→35, falsified clauses VERBATIM as HISTORICAL);
coverage_check rc=0 139 rows 0/0, prose rc=0 standalone. LESSONS: reldump regexes must accept
unpadded `0x0`; census drift aborts the gate before the byte panel — run census --check first.
**NEXT (successor):** (1) `spec/lab-evidence/e2e52-p3/RESULTS.md` §P3-4 + `PLAN.md` §5 P3-4
row (campaign 9 ok/11, PU/PV verdicts, H2a/H2b+H4b-detail+H5a/H5b+H6a FALSIFIED,
H2c/H5c/H6b CONFIRMED, PA root cause + headline, 147-prediction falsified at stage level),
explicit-path commit. (2) Then subround **P3-5** per PLAN §P3-5 (live refusals: DEC
FORMAL/deref, numeric-LITERAL items, counted SKIP/PAGE+EDIT, format-COUNT-expression, group
count 0, x-widths-14..128 object gap): PLAN + probes COMMITTED BEFORE any ocaml/ byte.
Constraints: no push; goldens NEVER re-derived; operator handoff.config.json NEVER staged;
all rc DIRECT (pipeline-masking trap fired twice running); pli80c POSITIONAL; renewals
autonomous (3/12 consumed, cap 12); campaign continues.

SUPERSEDED-BY-ABOVE: ### E2E-52/P3-4 PA FIXED — HEADLINE MET (PA cmp rc=0 vs existing golden, sha `d7b4e7f3…`); REGISTRATION OWED (2026-11-05; fresh chain hop 2/12; read `LEARNINGS.md` § "E2E-52/P3-4 PA FIX + SWEEP 89/89 + MARKERS + LOAN2 ADVANCED LANDED; REGISTRATION OWED" FIRST — it carries the root cause, every measured ACTUAL and the exact owed steps (1)-(5))

LANDED this hop (all rc DIRECT): root cause = unparenthesised trailing inner match in
`edit_num_cell` swallowed the outer `| _ -> false` (outer match non-exhaustive;
`-warn-error -a` = warnings NOT fatal). Fix committed `9b2d781` (codegen.ml only). Binary
`345644822818326f442a…`: **E52PA compile rc=0 384B, whole-file cmp rc=0 vs EXISTING
golden/e52p3/E52PA = HEADLINE**; 9/9 accepted-probe cmps re-verified; sweep **89/89**
(incl. P086J/K); markers E46K4/K15/N21/E52PF rc=2 intact; warnings 70 == baseline. LOAN2
blocker ADVANCED VERBATIM to `PUT FILE(OUTPUT) EDIT shape [TBD] (line 212)` (prescan
matcher split; DEC-147 prediction FALSIFIED at stage level; recorded, NOT fixed).
**NEXT: execute `LEARNINGS.md` § above, owed steps (1)-(5): SPECIMENS 10 + PU/PV dr-refuses
rows from ACTUAL stderr, --update-inventory 1212→1222 (+refusals), FULL gate rc=0 DIRECT
build/gate-e52p3d-reg.log, census own write path (msgs WILL move), claim C362 MEASURED BYTES
ONLY BEFORE the COVERAGE IO.PUT_EDIT rewrite (EXACT:25→35), coverage_check+prose rc=0,
RESULTS §P3-4 + PLAN §5 rows, durables.** Constraints: no push; goldens NEVER re-derived;
operator handoff.config.json NEVER staged; all rc DIRECT; pli80c POSITIONAL; renewals
autonomous (2/12 consumed).

SUPERSEDED-BY-ABOVE: ### E2E-52/P3-4 campaign e52p3d MEASURED (9 ok/11) + ARM LANDED (9/9 new-probe cmp rc=0); PA MATCH_FAILURE BLOCKER OWED, then sweep/LOAN2/registration (2026-11-05; fresh chain hop 1/12; read `LEARNINGS.md` § "E2E-52/P3-4 campaign e52p3d MEASURED + arm LANDED" FIRST — it carries every measured byte, all verdicts (H2c/H5c/H6b + x(0)/x(128)-compile CONFIRMED; H2a/H2b/H4b-detail/H5a/H5b/H6a FALSIFIED verbatim) and the exact owed steps)

ACTUALS this hop (rc DIRECT): baseline build `c2c6282f…`, PA/PP..PZ refusals
re-measured exactly pre-registered. ORACLE one grouped campaign rc=0 **9 ok/11**:
**PU dr-refuses** (bare `x` `SYNTAX ?`, no .REL), **PV dr-refuses** (`x(255)` `BAD VAL`,
no .REL; listing markers measure `x(0)`/`x(128)` COMPILE — their bytes UNMEASURED).
Goldens `golden/e52p3d/` (9×256 B), reldumps `build/e52p3d/`. ARM (codegen.ml ONLY,
UNCOMMITTED at checkpoint): fmt_spec became `let rec`; `Pi_repgrp` → `80 n…81` recursive,
**count-1 FLATTENS** (E52PS `80 00 03 FF 81` — no wrapper); `X(w)` → `0B w` literal
w ≤ 128 only (bare-x refuses naming PU); `authorize_file_edit_item` PInum admitted via
new `edit_num_tree/edit_num_cell/edit_num_lit/edit_num_operand` shape authority (Vint
cells, lit×cell, cell/lit, +/- nested; all else refuses BY NAME). **9/9 accepted probes
whole-file cmp rc=0 FIRST TRY** on binary `898b191c…` (PZ division and PX no-XCHG
already byte-exact in existing lowering — H6b). **BLOCKER: PA now CRASHES `Fatal error:
exception File "lib/codegen.ml", line 11906, characters 2-7: Pattern matching failed`
— a Match_failure at `edit_num_cell`'s syntactically-EXHAUSTIVE `match (unwrap_e x).Ast.e
with Ast.Eident … | _ -> false`; suspect stale line map or PIlit-`'|'`-item interaction;
DEBUG FIRST, codegen.ml only.** PA cmp vs EXISTING `golden/e52p3/E52PA/E52PA.REL` =
HEADLINE, unmet. codegen warnings 74 vs baseline 70 (+4 mine) — attribute at sweep.
**NEXT (successor):** (1) fix PA, rebuild, PA cmp rc=0, re-verify 9/9 cmps on final
binary. (2) sweep E52PB..PO/P086J/K/E46N 19/E52A..J/E51A..L/R10 (75+13 intact + new);
markers E46K4/K15/N21/E52PF rc=2. (3) LOAN2 rerun UNMODIFIED positional, blocker
VERBATIM (expect DEC FORMAL 147; classify, do NOT fix). (4) registration: SPECIMENS
10 (PP..PZ+PA), sanctioned --update-inventory 1212→1222, honest REJECTS/NEG_META rows
for PU+PV (dr-refuses; markers from ACTUAL stderr) then inventory +1 refusal if rows
land, FULL gate rc=0 DIRECT `build/gate-e52p3d-reg.log`, census own write path (fmt_spec/
X catch texts CHANGED — msgs WILL move), claim **C362** MEASURED BYTES ONLY BEFORE
COVERAGE `IO.PUT_EDIT` rewrite (EXACT = 25+new; cite lesson), coverage_check+prose rc=0,
RESULTS §P3-4 + PLAN §5 row, explicit-path commits, finalize/renew.
Constraints: no push; goldens NEVER re-derived; operator handoff.config.json NEVER
staged; all rc DIRECT (masked-pipeline trap fired AGAIN this hop — `dune build | tail`
reports tail's rc); pli80c POSITIONAL; never hardcode LOAN2; renewals autonomous.

SUPERSEDED-BY-ABOVE: ### E2E-52/P3-4 PRE-REGISTERED at `3ac7f41`; CAMPAIGN e52p3d OWED NOW (2026-11-05; fresh chain — operator reset renewal state; read `LEARNINGS.md` § "E2E-52/P3-4 recovery + evidence decode + PRE-REGISTRATION LANDED" FIRST)

DONE this hop (all rc DIRECT): g310 guard block committed VERBATIM `6d83a36`; prose-hash
verify measured CURRENT (documented checkpointSources algorithm; `/handoff` slash command
UNAVAILABLE in model context — limitation reported); P3-3 closure verified (ledger ENDS
C361, tag e52p3d unused, E52PA..PO collision-grepped). EVIDENCE DECODED from EXISTING
goldens: rep-group `80 n records 81` RECURSIVE (LOAN2 pools 0017/007F, DEPREC
0033/007B/009E; counts 02/04, nested+sibling, NO flattening); `x(w)=0B w` widths
{02..0F,10,13} measured, bare-x and w>19 UNMEASURED; PA relocations verified code
0032-0047 == LOAN2 0544-0558 (`2A RELOC data 0F / 11 64 00 / ?IM22N / EB / 2A RELOC
data 11 / 19 / 3E 09 / ?QICOP / ?EDTOV / ?QIOOP`); console PInum path
(`lower_put_items_gen`) is route-independent — file arm needs ONLY
`authorize_file_edit_item`; LOAN2 177 pins PIvar bin-vars on file route (07BA-07D9)
but that class stays REFUSED (P3-5); parser emits `Ast.Pi_repgrp` (NOT Pi_rep).
PRE-REGISTRATION LANDED `3ac7f41`: PLAN §P3-4 + probes E52PP..E52PZ (11, CRLF+^Z
≤71 cols verified by script).
**NEXT steps (successor):** (1) `cd ocaml && eval "$(opam env)" && dune build` rc=0,
record binary sha (clean rebuild), confirm PA still rc=2 by NAME at
authorize_file_edit_item — baseline re-measure. (2) ONE grouped campaign:
`cd /home/john/projects/sushiworks/pli80 && PLI_SRC=probes timeout 900 python3
oracle/batch.py E52PP E52PQ E52PR E52PS E52PT E52PU E52PV E52PW E52PX E52PY E52PZ
--tag e52p3d --switches '$L$D'` — rc DIRECT; read each .PRN accept/refuse; reldump
new goldens to build/e52p3d/; verdicts H2a/b/c (PS), H4a/b (PV widths), H5a/b/c
(bare x PU), H6a/b (PX result reg), PW/PY/PZ ops; keep every MISS verbatim.
(3) arm PLAN §P3-4 §4 (codegen.ml ONLY): (a) fmt_spec Pi_repgrp -> `80 n…81`
recursive via fmt_w count; (b) Pi_fmt X one literal arg -> `0B w` (arm ONLY widths
measured; bare-x only if PU accepts); (c) authorize_file_edit_item PInum admit ONLY
the ops PW/PX/PY/PZ measure on fixed-bin cells (float/DEC/call/subscript/member keep
refusing BY NAME). (4) build; cmp PP..PZ accepted probes whole-file vs NEW goldens;
**cmp E52PA vs EXISTING golden/e52p3/E52PA/E52PA.REL — E52PA must go byte-exact**;(
5) sweep controls (E52PB..PO, P086J/K, E46N, E52A..J, E51A..L, R10xx — expect 75+13
baseline intact + new; markers E46K4/K15/N21/E52PF rc=2); LOAN2 rerun UNMODIFIED
positional, record blocker VERBATIM (expected NEXT: DEC FORMAL at 147 via
authorize_file_edit_item — classify, do NOT fix). (6) registration: SPECIMENS for
byte-exact new probes + PA, --update-inventory, FULL gate rc=0 to
build/gate-e52p3d-reg.log, census own write path, claim **C362** from MEASURED bytes
ONLY BEFORE the COVERAGE rewrite (IO.PUT_EDIT cites), coverage_check + prose rc=0,
RESULTS §P3-4 + PLAN §5 rows, durables, finalize.
Constraints: no push; existing goldens NEVER re-derived; operator handoff.config.json
NEVER staged; all rc DIRECT (never trailing pipes); pli80c POSITIONAL; never hardcode
LOAN2; renewals autonomous at safe boundaries (fresh chain, cap 12).

SUPERSEDED-BY-ABOVE: ### E2E-52/P3-3 CLOSED (registration chain `7294d09`→`a4eddd6`→`64e464b`→`4f5d509`→`794cfb2`, gate rc=0 1212/0, ledger ENDS C361); RENEWAL CAP 12/12 REACHED — CHAIN CLOSES (2026-11-05; read `LEARNINGS.md` § "E2E-52/P3-3 REGISTRATION LANDED — SUBROUND CLOSED at the 12/12 renewal cap" FIRST)

Registration executed in full THIS hop, every rc DIRECT: 13 SPECIMENS rows + E52PF
dr-refuses REJECTS/NEG_META row (marker `picture $ after a digit specifier is dr-refuses`
re-measured rc=2); `--update-inventory` EXACTLY 1199→1212 (+13 specimens) + 1 refusal
(179→180); FULL gate REAL rc=0 `build/gate-e52p3c-reg.log` (1212/0 of 1212, negatives
180/180, divergence 9/9, coverage 139/0/0, census 15/0/26/0, prose 5); census own write
path rc=0 metadata-only, LOAN2 blocker VERBATIM UNCHANGED; **C361** from MEASURED BYTES
ONLY committed BEFORE the COVERAGE rewrite (`64e464b`; b1=count{9,Z,$}−1-if-$, b2=count{9,Z}
after the LAST V, len=text length, UPPER(text), concatenation, route-independent, PF
dr-refuses positional law, no compile-time scale agreement); IO.PUT_EDIT EXACT:25 +
coverage_check rc=0 (`4f5d509`); RESULTS §5 + PLAN §5 P3-3 row (`794cfb2`); prose rc=0
twice. PA stays UNREGISTERED (P3-4 owns the file EXPRESSION item).

**NEXT (P3-4, campaign continues):** subround **P3-4 = rep-groups `2(...)` → tables `80 n
… 81` + `x(w)` → `0B w` + the file-route fixed-bin EXPRESSION item** (PA bytes already
pinned at LOAN2.REL 0544-0558: `LHLD/LXI D,0064/?IM22N/XCHG/LHLD/DAD/MVI A,09/?QICOP/
?EDTOV`). Execute: (1) `PLAN.md` §P3-4 + probes written from the LOAN2/P086K evidence and
COMMITTED BEFORE any ocaml/ byte; grep probes/+INVENTORY for name collisions; verify the
tag is UNUSED. (2) ONE grouped campaign `PLI_SRC=probes timeout 900 python3 oracle/batch.py
<names> --tag e52p3d --switches '$L$D'`; classify every difference. (3) arm + sweep + LOAN2
rerun VERBATIM (never fit). (4) registration (SPECIMENS, sanctioned --update-inventory, FULL
gate rc=0 to build/gate-e52p3d-reg.log, census own write path) + claim **C362** from MEASURED
bytes ONLY BEFORE the COVERAGE rewrite + coverage_check + prose rc=0 + RESULTS/PLAN rows +
durables. Constraints: no push; existing goldens never re-derived; operator
handoff.config.json never staged; all rc DIRECT; pli80c POSITIONAL; CRLF+bare ^Z probes ≤71
cols. **RENEWALS 12/12 CONSUMED — this chain is CLOSED at the configured cap: a new hop
requires the operator to archive and reset the ignored `.pi-guard` renewal-state.json (or
raise the cap). Close this session via `handoff_finalize`; do NOT call `handoff_renew`.**

SUPERSEDED-BY-ABOVE: ### E2E-52/P3-3 analysis LANDED (this hop, NOTHING committed, ZERO ocaml/ byte, ZERO oracle call); PLAN §P3-3 + probes + ONE grouped campaign OWED (2026-11-05; read `LEARNINGS.md` § "E2E-52/P3-3 picture-record analysis COMPLETE" FIRST — it carries the full 12-record measured table, the surviving hypotheses HA2/HB8 (b1) and HC/HD (b2) with discriminators, the pairing precedents, the fmt_spec arm site, and the E52PA..E52PO probe bank)

Steps (all rc DIRECT, never a trailing pipeline):
(1) Write `spec/lab-evidence/e2e52-p3/PLAN.md` §P3-3 (measured-12-record table, hypotheses +
    falsifiers, per-probe PREDICTED table bytes for E52PA..E52PO, arm = ONE `Ast.Pi_pic` branch
    in `fmt_spec` emitting `02 b1 b2 len UPPER(text)` under the guard "picture chars outside
    {9,Z,$,V,.,B,comma,slash} refuse BY NAME; non-leading `$` armed ONLY if PF measures it",
    boundaries kept, predictions P1..P5 incl. LOAN2's same-catch rep-group move prediction)
    and the probes themselves (CRLF+bare ^Z, ≤71 cols, skeletons copy P086J/P086K style);
    `grep` probes/ + spec/INVENTORY.txt for E52P* collisions FIRST. COMMIT PLAN §P3-3 + probes
    BEFORE ANY ocaml/ byte (explicit paths; commit the pending guard-block refresh VERBATIM
    first if it lands uncommitted).
(2) ONE grouped campaign: `PLI_SRC=probes timeout 900 python3 oracle/batch.py E52PA E52PB
    E52PC E52PD E52PE E52PF E52PG E52PH E52PI E52PJ E52PK E52PL E52PM E52PN E52PO --tag e52p3
    --switches '$L$D'` (tag verified UNUSED); goldens land golden/e52p3/; classify every
    difference dr-refuses/my-gap/unmeasured; a SECOND bounded batch is allowed if PH/PL die on
    scale mismatch and HC-vs-HD stays undecided.
(3) RESULTS.md §P3-3: measured table bytes per probe + hypothesis verdicts (HA2 vs HB8, HC vs HD).
(4) arm + sweep (E46N 19/19, R10xx, E52A..J, E51A..L, P086J/K cmp rc=0) + PM/PN/PO whole-file
    cmp vs NEW goldens + LOAN2 rerun VERBATIM (record what it ACTUALLY prints; never fit;
    PA bytes NEVER claimed — PInum on file route stays refused for P3-4).
(5) registration: SPECIMENS (armable new probes only), sanctioned --update-inventory (expect
    +2 lines if PN,PO... count what cmps rc=0), FULL gate rc=0 to build/gate-e52p3c-reg.log,
    census own write path, claim **C361** from MEASURED bytes only (ledger ends C360) committed
    BEFORE the COVERAGE rewrite of IO.PUT_EDIT (cite-resolution lesson) + coverage_check rc=0,
    prose rc=0, RESULTS §5 row, durables, explicit-path commits.
Constraints: no push; existing goldens never re-derived (NEW probes ADD goldens); operator
handoff.config.json never staged; pli80c POSITIONAL args; state which build a sha came from;
CRLF probes; renewals autonomous (10/12 consumed, cap 12); campaign continues past every blocker.

SUPERSEDED-BY-ABOVE: ### E2E-52/P3-2 FULLY LANDED (C360 `19ce1f4`, COVERAGE `9e897e8` rc=0 139/0/0, RESULTS+PLAN `0d93acc`); SUBROUND P3-3 = PICTURE `02` DECODE OWED (2026-11-05; read `LEARNINGS.md` § "E2E-52/P3-2 COVERAGE + C360 + RESULTS/PLAN LANDED" FIRST — it carries the measured ACTUALS and the exact P3-3 steps (1)-(4))

Registration debt is CLOSED: claim C360 from MEASURED bytes only (ledger ENDS C360); `IO.PUT_EDIT`
row SUPPORTED + EXACT:12 + MEASURED, falsified IFACT/LOAN1 clause kept verbatim as HISTORICAL,
coverage_check rc=0 DIRECT 139 rows 0/0 (`build/coverage-check-e52p3c-coverage.log`), stats
committed via own write path; RESULTS.md §P3-2 + PLAN §5 P3-2 row; prose rc=0 standalone twice.
Chain: `19ce1f4` → `9e897e8` → `0d93acc` → durables. LESSONS: claim commit MUST precede the
COVERAGE commit (validator resolves cites); never report the claims total via `grep -c '^## C'`
(file starts mid-index).
NEXT = P3-3, steps in that LEARNINGS §: (1) PLAN.md §P3-3 pre-registered and COMMITTED BEFORE
any ocaml/ byte — decode operands of `02 04 00 05 | "99/99"` via one-operand-at-a-time oracle
probes (`p'9'`, `p'999'`, `p'ZZ9'`, `p'9V9'`, two pictures, picture beside `a(w)`); (2) ONE
grouped oracle campaign, goldens + RESULTS §P3-3 decode, classify all differences; (3) arm +
sweep + LOAN2 rerun VERBATIM (record what it ACTUALLY prints, never fit); (4) registration +
claim C361 from MEASURED bytes only. Constraints: no push; existing goldens never re-derived
(NEW probes may add goldens); operator `handoff.config.json` never staged; all rc DIRECT; CRLF
probes; EDIT controls only from the statement-option position; state WHICH build a sha came
from; renewals autonomous (9/12 consumed, cap 12); campaign continues past every blocker.

SUPERSEDED-BY-ABOVE: ### E2E-52/P3-2 REGISTERED (gate rc=0 1199/0, negatives 179/179, census recorded); COVERAGE IO.PUT_EDIT + C360 + RESULTS/PLAN OWED (2026-11-05; read `LEARNINGS.md` § "E2E-52/P3-2 registration LANDED" FIRST — it carries the measured ACTUALS, the FALSIFIED IFACT/LOAN1 picture clause and the exact owed steps 1-6)

LANDED this hop: `95b1fa6` g298 block; `ff1c8f2` E41X8 retired (MEASURED rc=0 384B, NO golden,
bytes never claimed; negatives 180→179); `60ed349` SPECIMENS P086K+P086J, `--update-inventory`
EXACTLY TWO lines 1197→1199, census own write-path rc=0 (LOAN2 blocker VERBATIM moved to
`codegen: PUT EDIT format item form unsampled [TBD] (counted, grouped, picture, remote and
rep-group formats are not decoded)`; COPYLPT unchanged), FULL gate REAL rc=0 DIRECT
`build/gate-e52p3b-reg.log` (1199/0, 179/179, 9/9, 139 0/0, 15/0/26/0, prose 5).
VERIFIED prerequisite: LOAN1 has NO edit stmt; IFACT's edit has NO picture — the `IO.PUT_EDIT`
row's IFACT/LOAN1-picture clause is FALSIFIED.
NEXT: (1) rewrite COVERAGE.tsv `IO.PUT_EDIT` (line 65) citing P086K/P086J, boundary naming the
still-refusing picture/x/rep/counted/grouped/remote forms with LOAN2's verbatim message;
`coverage_check.py` rc=0. (2) claim **C360** from MEASURED bytes ONLY (ledger ends C359; never
claim E41X8 bytes). (3) `file_prose_check.py` rc=0. (4) RESULTS.md §P3-2 + PLAN.md §5 row.
(5) durables, explicit-path commits. (6) subround P3-3 = picture `02` A/B decode — PLAN section
committed BEFORE any ocaml/ byte. Constraints: no push; goldens never re-derived; operator
`handoff.config.json` never staged; all rc DIRECT (never a trailing pipeline); never hardcode
LOAN2; renewals autonomous (9/12, cap 12).

SUPERSEDED-BY-ABOVE: ### E2E-52/P3-2 P086K FIXED (DATA/COMMON record ORDER); SWEEP GREEN 75/75; E41X8 RETIREMENT + REGISTRATION OWED (2026-11-04; read `LEARNINGS.md` § "E2E-52/P3-2 P086K FIXED" FIRST — it carries the falsified +3-bytes diagnosis, the measured record-order law, the falsified probe design and the exact owed steps (1)-(5))

Headline ACTUALS this hop (all rc DIRECT): `dune build` rc=0, binary `748c434fafd8c01579…`
(CLEAN rebuild — an incremental build of the same source hashes differently, `a353f6fc…`; always
say which build). P086K whole-file `cmp` **rc=0** (512 B, CODE 0x65=101, DATA 0x12=18); P086J
**rc=0** (256 B). Zero-drift sweep **75 specimens byte-exact / 0 FAIL** (E46N 19/19, E52 10/10,
E51 12/12, R10 bank 34/34); boundary markers intact rc=2 (E46K4 imem-EDIT, E46K15 GET-subset
line 3, E46N21 LINE-with-count). Focused refusals rc=2 BY NAME: picture → the fmt_spec catch with
NO line number; `x(5)` → operator X unsampled; counted SKIP+EDIT and PAGE+EDIT **in the
statement-option position** (my first probes put them inside the data list and were FALSIFIED as
probe designs — the parser collects EDIT controls only from the option position) → name the class
with the CORRECT line 4 on CRLF sources; numeric literal → matcher "cannot split" catch; DEC
formal → names the formal; fixed-bin EXPRESSION → names the class + cites LOAN2 0544-0558. LOAN2
UNMODIFIED rc=2, next blocker VERBATIM: `codegen: PUT EDIT format item form unsampled [TBD]
(counted, grouped, picture, remote and rep-group formats are not decoded)` — P3-1's "PUT EDIT
deferred … (line 115)" is behind us, exactly as the arm-design § predicted.
NEXT: (1) commit the pending guard managed-block refresh in HANDOFF.md/PROGRESS.md VERBATIM
(explicit paths, never handoff.config.json) — HEAD is `2686bcc` (P086K fix + durables, sweep green
at that commit); (2) retire E41X8 (compiles rc=0 now; inline source, NO golden, never claim its
bytes) from
REJECTS `tools/e2e_gate.py:2568` + NEG_META 4021 → negatives 180→179; (3) registration: SPECIMENS P086K+P086J, `--update-inventory`
1197→1199 EXACTLY TWO lines, FULL gate rc=0 1199/0 to `build/gate-e52p3b-reg.log`, census via its
OWN write path recording moved LOAN2/COPYLPT messages verbatim, COVERAGE `IO.PUT_EDIT` row ONLY
after verifying the IFACT/LOAN1 discrepancy (LOAN1 has NO edit stmt) + coverage_check rc=0, claim
**C360** from MEASURED bytes only, prose rc=0, RESULTS.md + PLAN §5 row, durables,
explicit-path commits, no push. Campaign CONTINUES past every blocker: next LOAN2 classes =
picture `02`-record decode, `x(w)` `0B` records, `2(...)` rep-groups, DEC-formal (deref) items,
fixed-bin EXPRESSION items, then the PRINT/PAGESIZE OPENs at 54/56 — each with its own PLAN
section committed BEFORE its byte. Constraints: no push; goldens never re-derived; operator
`handoff.config.json` never staged; all rc DIRECT (never a trailing pipeline — `cmd | tee | head`
reports tee's status); never hardcode LOAN2; renewals autonomous at safe boundaries (7/12
consumed at this hop, cap 12). Scratch evidence this hop wrote (ignored working state, keep):
`build/e52p3/sweep.py`, `build/e52p3/refusals/p32r*.pli` (the two falsified designs are
p32r4/p32r5; the correct option-position ones are p32r9/p32r10),
`build/e52p3/loan2-postfix-stderr.log`, `/tmp/e52p3-sweep/`.

SUPERSEDED-BY-ABOVE: ### E2E-52/P3-2 ARM LANDED (uncommitted); P086J cmp rc=0 FIRST TRY; P086K MISSES AT BYTE 32 — DEBUG, SWEEP, REFUSALS, REGISTRATION OWED (2026-11-04; read `LEARNINGS.md` § "E2E-52/P3-2 ARM IMPLEMENTED" FIRST — it carries the full arm record, the falsified P1, the two mechanics lessons, and owed steps (1)-(7) exactly)

Headline ACTUALS this session (all rc DIRECT): `dune build` rc=0 binary `a353f6fc7a48d185…`,
warning histogram IDENTICAL to `build/e52p3/arm-build-warnings.log`; arm = contract (a)-(g)
executed in `ocaml/lib/codegen.ml` ONLY, UNCOMMITTED in tree; HEAD `1a1ceb6` + operator
config dirty. P2 HIT: P086J whole-file cmp rc=0 first try (256 B). P1 FALSIFIED kept
verbatim: P086K cmp rc=1 at octet 32; mine 512 B code=101 (golden 98, +3 bytes), divergence
starts at the DEF-COMMON/SEL-COMMON/FCB record area — suspect a spurious second SEL-COMMON
on the GET (st.cur_common reset between statements) or a prescan table-count miss. NEXT ACT:
reldump /tmp/p086k.rel with the tool that wrote build/e52p3/p086k-reldump.txt, diff
record-for-record, fix, cmp AGAIN. Then sweep (E46N 18/18, R10xx, E46K4/K15 markers, E52,
E51), focused refusals BY NAME, LOAN2 rerun verbatim (predicted: fmt_spec catch, no line
number), E41X8 retirement (negatives 180->179), registration 1197->1199 (gate rc=0 1199/0,
census own write path, IO.PUT_EDIT row after IFACT/LOAN1 verification, C360 from MEASURED
bytes only), prose rc=0, explicit-path commits. Campaign continues past every blocker.
Constraints: no push; goldens never re-derived; operator handoff.config.json never staged;
all rc DIRECT; never hardcode LOAN2; renewals autonomous at safe boundaries (6/12 consumed,
cap 12).

SUPERSEDED-BY-ABOVE: ### E2E-52/P3-2 ARM CONTRACT VERIFIED against the code (this session, renewal 5/12); IMPLEMENT A1-A5 NOW, then sweep/registrations (2026-11-04; read `LEARNINGS.md` § "E2E-52/P3-2 arm DESIGN VERIFIED against the code" FIRST — it carries the exact golden byte lists, the parser-representation facts and the seven-point implementation contract (a)-(g); then `spec/lab-evidence/e2e52-p3/PLAN.md` §P3-2 §3/§4/§5)

Steps, all rc DIRECT (never a trailing pipeline):
(1) `git rev-parse HEAD && git status --porcelain=v1` (only operator handoff.config.json may be
 dirty); `cd ocaml && eval "$(opam env)" && dune build` rc=0, binary `34e8321a…`.
(2) Implement LEARNINGS (a)-(g) in `ocaml/lib/codegen.ml` ONLY: `edit_match` record +
 `match_put_edit` file arm (leading bare SKIP → `Sk_lit "1"`; counted/other control → raise BY
 NAME); `match_get_edit` on the FLAT parser list; `edit_stmts`/`prealloc_fmt_tables` FIFO in
 SOURCE order (put-table@0000 then get-table@0006); new `prescan_stmt` `Ast.Sget _` arm for the
 GET table's pool bytes; `authorize_file_edit_item` (admit ONLY PIlit + PIvar-Vdec); DELETE the
 `is_edit && file <> None` guard (11557) and the PIvar/Vdec `is_edit` refusal (~11797); NEW
 `lower_get_file_edit` with `?EDTIV` as a name only. Build rc=0, warning profile IDENTICAL
 (`build/e52p3/arm-build-warnings.log` is the P3-1 baseline).
(3) Predictions (PLAN §5, pre-registered): `pli80c.exe probes/P086K.PLI` whole-file `cmp` rc=0
 FIRST TRY vs `golden/probe55/P086K/P086K.REL` (512 B, CODE 0x62, DATA 0x12); SAME for P086J vs
 `golden/probe55/P086J/P086J.REL` (256 B, CODE 0x3D, DATA 0x10). Zero-drift sweep: E46N 18/18,
 R10xx console EDIT bank, E46K4/K15 boundary rows, E52A..J, E51A..L. Focused refusals rc=2
 naming the class: picture / x(w) / rep-group / counted-SKIP+EDIT / PAGE+EDIT / numeric-literal
 / DEC-formal / fixed-bin-expression-on-file-EDIT. **LOAN2 rerun must STILL refuse and its
 ACTUAL message recorded VERBATIM** (LEARNINGS last bullet predicts the fmt_spec catch, which
 carries no line number — record what the compiler actually prints, do not fit it).
 E41X8 compiles rc=0 → retire REJECTS row (`tools/e2e_gate.py:2568`) + delete NEG_META (4021):
 negatives 180→179.
(4) Registration per PLAN §5 P6: SPECIMENS P086K+P086J (keep the golden paths), sanctioned
 `--update-inventory` 1197→1199 EXACTLY TWO lines, FULL gate rc=0 1199/0 to
 `build/gate-e52p3b-reg.log`; census re-snapshot via its OWN write path (record moved
 LOAN2/COPYLPT messages verbatim); COVERAGE `IO.PUT_EDIT` row (line 65) updated ONLY after
 verifying the MEASURED IFACT/LOAN1 discrepancy (LOAN1 has NO edit statement) +
 `coverage_check.py` rc=0; claim **C360** derived ONLY from PLAN §2 / LEARNINGS measured bytes;
 `file_prose_check.py` rc=0; explicit-path commits, no push.
(5) Campaign CONTINUES past every blocker: next LOAN2 classes = picture `02`-record decode,
 `x(w)` `0B` records, rep-groups, DEC-formal (deref) items, fixed-bin EXPRESSION items, then the
 PRINT/PAGESIZE OPENs at 54/56 — each with its own PLAN section committed BEFORE its byte.
Constraints: no push; goldens never re-derived; operator handoff.config.json never staged; all rc
 DIRECT; never hardcode LOAN2; renewals autonomous at safe boundaries (cap 12, 5/12 used).

SUPERSEDED-BY-ABOVE (kept as written): ### E2E-52/P3-2 PLAN §P3-2 LANDED (commit below); ARM A1-A5 OWED (2026-11-04; renewal 5/12; read `LEARNINGS.md` § "E2E-52/P3-2 evidence COMPLETE + PLAN §P3-2 LANDED" + `spec/lab-evidence/e2e52-p3/PLAN.md` §P3-2 FIRST)

Exact next steps, all rc DIRECT:
(1) `git rev-parse HEAD; git status --porcelain=v1` (only operator handoff.config.json may be
 dirty); `cd ocaml && eval "$(opam env)" && dune build` rc=0, binary `34e8321a…`.
(2) Implement PLAN §3 arms **A1-A5 in `ocaml/lib/codegen.ml` ONLY** (match_put_edit file branch
 + prescan/FIFO; match_get_edit + get-file-EDIT lowering with `?EDTIV` via call_ext; delete the
 `is_edit && file <> None` guard ~11558 and BOTH Vdec is_edit refusals (~11797); file EDIT
 attaches without open [C282]; keep every boundary refusal of PLAN §4 BY NAME). dune build rc=0,
 warning profile IDENTICAL.
(3) Predictions (pre-registered): `pli80c.exe probes/P086K.PLI` whole-file cmp rc=0 FIRST TRY vs
 `golden/probe55/P086K/P086K.REL` (512 B); SAME for P086J vs `golden/probe55/P086J/P086J.REL`
 (256 B). Zero-drift sweep E46N 18/18, R10xx, E46K4/K15, E52A..J, E51A..L. Focused refusals
 picture/x/rep/numeric-literal/DEC-formal; **LOAN2 rerun must STILL refuse at 115 naming the
 picture** — verbatim record. E41X8 compiles rc=0 -> retire from REJECTS+NEG_META (negatives
 180→179).
(4) Registration per PLAN §5 P6: SPECIMENS P086K+P086J, `--update-inventory` 1197→1199 EXACTLY
 TWO lines, gate rc=0 1199/0 to build/gate-e52p3b-reg.log; census own write path; COVERAGE
 IO.PUT_EDIT row ONLY after verifying the IFACT/LOAN1 discrepancy (LOAN1 has NO edit stmt);
 claim **C360** from PLAN §2 measured bytes only; prose rc=0; explicit-path commits, no push.
(5) Campaign CONTINUES past every blocker: next LOAN2 classes = picture 02-record decode,
 x-records, rep-groups, DEC-formal (deref) items, then the PRINT/PAGESIZE OPENs 54/56.
Constraints: no push; goldens never re-derived; operator handoff.config.json never staged; all rc
 DIRECT; never hardcode LOAN2; renewals autonomous at safe boundaries (cap 12).

SUPERSEDED-BY-ABOVE: ### E2E-52/P3-2 evidence DECODED + CORRECTED; PLAN §P3-2 owed BEFORE any ocaml/ byte (2026-11-04; renewal 3/12; read `LEARNINGS.md` § "E2E-52/P3-2 evidence decode LANDED" FIRST — it supersedes the predecessor survey bullets below and carries the exact owed steps (1)-(5))

DECED THIS SESSION (all rc/measured from existing goldens; NOTHING compiler-edited):
`clear` = `%replace` macro (LOAN2:12), `a` = FORMAT item (the data/format order REVERSAL —
LOAN2:115 DATA is `'|'` + `100*m+y`); LOAN2 *S(0007) table = console law `80 00 03 FF` +
new picture record `02 04 00 05 "99/99"` + `81`; P086K 512 B FULLY decoded (both PUT and
GET statements; file tables identical to console law; DEC prep = existing `p/p+3/s` law —
the predecessor's `MVI B,06` FALSIFIED, bytes are `MVI A,08 / MVI B,02`; `?EDTIV` is the
one new routine name); all 7 EDITF sites mapped to source lines 115/147/177/191/195/199/212
(02FF is the console stmt at 85); barrier located: `lower_put_items_gen` guard ~11558 with
FALSIFIED premise + `match_put_edit` file-blindness + fmtq FIFO + `st.file_out` open-guard
vs P086K's NO-open attach (C282).
SUCCESSOR: execute LEARNINGS owed steps (1)-(5) EXACTLY — byte-list stmt-199 span + remaining
tables, check e2e8/e2e11 goldens for closer witnesses, write PLAN §P3-2 with pre-registered
predictions and COMMIT BEFORE any ocaml/ byte, then arm (PROPOSED P3-2a: file PUT+GET EDIT,
bare skip, literal f/a formats, string/DEC items; picture/x/rep/V refuse BY NAME; P086K panel
specimen 1197→1198, E41X8 retirement candidate), sweep/refusals/LOAN2-verbatim/registration/
C360 from measured bytes only. Constraints unchanged: no push; goldens never re-derived;
operator handoff.config.json never staged; all rc DIRECT; never hardcode LOAN2; renewals
autonomous at safe boundaries; campaign continues past every blocker.

SUPERSEDED-BY-ABOVE (kept as written; its "data items (a,p'99/99')" PROPOSED bullet was
FALSIFIED this session by the data/format reversal above):

P3-1 DELIVERED IN FULL: INVENTORY 1196->1197 one-line diff `e728175`; post-reg FULL gate REAL rc=0 **1197/0** (`build/gate-e52p3-reg.log`; negatives MEASURED 180/180 — the brief's 181/181 FALSIFIED, retire removes one row); claim **C359** `c410d18` (ledger ENDS C359, 182); COVERAGE FILE.PUT_PAGE SUPPORTED/EXACT:1 + stats own write path rc=0 `d3b8859`; RESULTS.md + PLAN §5 row `3e74d83`; prose rc=0 x2. Tree clean except operator `handoff.config.json`.
P3-2 survey DONE so far (all in that LEARNINGS §): LOAN2:115 verbatim `put file(output) skip edit('|',100*m+y) (a,p'99/99');`; refusal site `match_put_list_lit` codegen.ml:2646; console EDIT EXISTS ([C090], fmt_spec = literal-width f/a only); **DR file-EDIT witnesses already in hand**: `golden/probe55/P086K/P086K.REL` re-dumped (attach 0652 + ?SIOOP/?EDITF table `80 00 00 05 01 81`/?DLDOP/?QDCOP/?EDTOV/?QIOOP, pool law holds, NO open needed) and `golden/first/LOAN2/LOAN2.REL` span 0522-055C (skip = MVI A,01/?SKPOP; `100*m+y` = LHLD/LXI D,0064/?IM22N/XCHG/LHLD/DAD/MVI A,09/?QICOP/?EDTOV); reldump at `build/e52p3/loan2-golden-reldump.txt` (ignored). E41X8 negative row pins the P086K shape — retirement candidate.
SUCCESSOR: execute LEARNINGS owed steps (1)-(7) EXACTLY — finish evidence (declarations of `a`/`clear`; decode ALL LOAN2 tables + spans 068A,0796,0830,086E,08F1,0951), then pick the smallest first arm (PROPOSED P3-2a = file EDIT, bare skip + literal f/a formats = the fully-pinned P086K bytes; string/V/picture = later subrounds), write **PLAN §P3-2 + predictions, COMMIT BEFORE any ocaml/ byte**, then arm/sweep/refusals/LOAN2-verbatim-rerun/registration/claim from measured bytes only. Constraints unchanged: no push; goldens never re-derived; operator handoff.config.json never staged; all rc DIRECT; never hardcode LOAN2; renewals autonomous at safe boundaries; campaign continues past every blocker.

SUPERSEDED-BY-ABOVE: ### E2E-52/P3-1 registration OWED (2026-11-04; arm LANDED `adb749c`, census re-snapshot LANDED; gate/inventory/COVERAGE/C359/RESULTS OWED; then P3-2 = PUT EDIT)

READ FIRST: `LEARNINGS.md` § "E2E-52/P3-1 ARM LANDED + registration IN FLIGHT" — it carries
the full measured record (arm, boundaries, falsifications, LOAN2 advance) AND the exact owed
registration steps (1)-(7) in order. Headlines, all MEASURED this session:
- E46N10 whole-file `cmp` rc=0 FIRST TRY vs `golden/e42p2c/E46N10/E46N10.REL` (384 B, sha
  `75557545…`); E46N sweep 18/18 byte-exact; warning profile IDENTICAL to baseline.
- All boundaries hold (counted PAGE, PAGE+items, console PAGE/N3_PAGE, E46N21 marker intact);
  non-leading PAGE refuses at the PARSER (falsifies the PLAN §3 stage, keeps the boundary).
- LOAN2 blocker MOVED PAST 99 — ACTUAL verbatim `codegen: PUT EDIT deferred [TBD] (line 115;
  only PUT LIST is implemented; ...)` rc=2. OPEN PRINT 54/56 stays queued BEHIND it (prescan
  order). P3-2 target = PUT EDIT at 115, its own PLAN pre-registered BEFORE any compiler byte.
- `tools/e2e_gate.py` UNCOMMITTED EDIT IN TREE: E46N10 retired from REJECTS + NEG_META (kept
  as written history) and ADDED to SPECIMENS — commit explicit paths BEFORE --update-inventory.
- Prereg-gate rc=0 expectation FALSIFIED and measured: gate at arm = REAL rc=1
  (`build/gate-e52p3-prereg.log`, census drift); run_negatives fails a retired-but-still-
  stamped row. Census re-snapshotted via its own write path rc=0, counts UNCHANGED 15/0/26/0
  (COPYLPT msg now names counted-SKIP item 2 line 6; LOAN2 names PUT EDIT 115) — COMMIT
  spec/census/*. 
Constraints unchanged: no push; goldens never re-derived; operator handoff.config.json never
staged; all rc DIRECT (never trailing pipelines); never hardcode LOAN2; renewals autonomous
at safe boundaries; campaign CONTINUES past PAGE.

SUPERSEDED-BY-ABOVE: ### E2E-52/P3 subround P3-1 IN FLIGHT — implementation steps (b)-(f) OWED, PLAN PRE-COMMITTED (2026-11-04; step (a) DONE: `spec/lab-evidence/e2e52-p3/PLAN.md` committed `b4deba0` BEFORE any compiler byte, on top of durables `5c21f87`; baseline was `6c44d8d`; compiler still `85bf7a26…` UNEDITED)

SUCCESSOR: re-verify HEAD/tree, rebuild (`cd ocaml && eval "$(opam env)" && dune build`
rc=0), then execute steps (b)-(f) below EXACTLY — all site numbers, pinned markers and
the edit list B1-B7 are in this section and `LEARNINGS.md` § "E2E-52/P3 hop 1"; read
those FIRST; do NOT bulk-read the ledger. AFTER P3-1 the CAMPAIGN CONTINUES: recompile
LOAN2, capture the next verbatim blocker (expected class: OPEN option PRINT at lines
54/56 — record, then plan subround P3-2 per the campaign loop; predictions commit before
each fix; never stop merely because PAGE landed). No push; operator `handoff.config.json`
never staged; goldens never re-derived; all rc DIRECT.

Execute IN ORDER, all rc captured DIRECTLY (never trailing pipelines):
(a) write `spec/lab-evidence/e2e52-p3/PLAN.md` — pre-registered predictions for E46N10
whole-file cmp against the golden (CODE 62/DATA 10; statement bytes 0023-0034 exactly as
the reldump above; ?PAGOP LINK-CHAIN-EXT record at 0030; continuation 0035), the refusal
boundaries kept (PAGE(count), PAGE+items, console PAGE, LINE), and the predicted LOAN2
next-blocker direction (blocker moves PAST line 99; expected OPEN-PRINT at 54 unless an
earlier prescan stop appears — record the ACTUAL verbatim message, predict only the
DIRECTION) + the P3 progress table header; commit BEFORE any ocaml/ edit.
(b) implement in `ocaml/lib/codegen.ml` ONLY: new `Sk_page` constructor on `put_skip`
(2257); `file_skip_of` admits `Pi_ctl("PAGE", None)` (counted PAGE still None); in
`file_items` refuse `Sk_page` with non-empty rest BY NAME (PAGE+items unmeasured) and
update the None-node narrative (PAGE no longer "does not lower" — counted PAGE is the
unmeasured remainder; keep the E46N21 marker substring intact); `bare_ctl_put` FILE arm
admits ("PAGE", None) through `file_items` and refuses counted PAGE by name, update the
final catch-all message; `lower_put_items_gen` match at ~11636 gains `| Sk_page ->` =
`call_ext st "?PAGOP"` on the file route, LOUD refusal on the console route; add loud
`Sk_page` arms to `lower_put_lit` (3389) and `lower_cat` (10923) for exhaustiveness —
they are console-only and must never see PAGE. NO other file, NO new encoder (reuse
`call_ext`). Preserve: file-named PUTs never reach the console route; layout ownership
(prescan `Pfile` arm already sums only item literals — page adds 0 pool bytes).
    EXACT EDIT LIST (sites verified 2026-11-04): B1 line 2257 add `| Sk_page` to
    `put_skip`; B2 `file_skip_of` add `| Ast.Pi_ctl ("PAGE", None) -> Some Sk_page` +
    comment update; B3 `file_items` success branch (`| [] ->`) guard `skipn = Sk_page &&
    rest <> []` -> named refusal "PAGE followed by items [TBD]", and rewrite ONLY the
    narrative tail (the format string `is %s, unmeasured on the named-file route [TBD]
    (line %d)` stays byte-identical — E46N21 marker lives inside it); B4 `bare_ctl_put`
    FILE arm: `| "SKIP", _ | "PAGE", None ->` share the file_items route, new `| "PAGE",
    Some _ -> failwith` counted refusal, catch-all message updated; B5
    `lower_put_items_gen` (~11636) `| Sk_page ->` file route `call_ext st "?PAGOP"`,
    console LOUD refusal; B6 `lower_put_lit`/`lower_cat` skip matches get loud
    `Sk_page -> failwith` arms (unreachable, exhaustiveness); B7 LIST-arm empty-list
    guard (~2667) message "SKIP" -> "SKIP or PAGE" (accuracy only). NO new encoder;
    parser.ml/bind.ml/panel/goldens untouched.
(c) `cd ocaml && eval "$(opam env)" && dune build` rc=0 (check NO new warnings — the
warning profile is a checked artifact); compile probes/E46N10.PLI → `cmp` whole file vs
`golden/e42p2c/E46N10/E46N10.REL` (expect rc=0 FIRST TRY per the model); recompile
E46N1..N9,N11..N19 vs their goldens (all must stay byte-exact; `cmp` each).
(d) focused refusals: `put page;` console refuses (N3_PAGE wording path), counted PAGE
refuses by name, `put file(f) page list('A')` refuses by name, E46N21 marker intact.
RE-RUN LOAN2 UNMODIFIED: capture the ACTUAL new first refusal VERBATIM + rc; do NOT fix
it this subround — record in the evidence file.
(e) full gate `timeout 3600 python3 tools/e2e_gate.py > build/gate-e52p3-prereg.log`
expect rc=0 **1196/0** (E46N10 NOT yet on the panel); commit compiler arm + PLAN/RESULTS
record; then registration hop: SPECIMENS+REJECTS/NEG_META move, `--update-inventory`
(1196→1197, exactly ONE line), gate AGAIN to `build/gate-e52p3-reg.log` rc=0 1197/0,
census re-snapshot via its OWN write path (record moved COPYLPT/LOAN2 msgs), COVERAGE
`FILE.PUT_PAGE` row → SUPPORTED/EXACT:1 + coverage_check rc=0, claim **C359** written
from measured bytes ONLY (E46N10 golden + COPYLPT:53 span + my new object),
`--update-inventory` unchanged count afterwards, commit explicit paths.
(f) update the P3 progress table (`spec/lab-evidence/e2e52-p3/PROGRESS.md`) + durables;
renew ONLY at a safe boundary if context demands; then proceed to the NEXT blocker per
the campaign loop — do NOT stop after PAGE.
Constraints: no push; goldens never re-derived/overwritten; operator
`handoff.config.json` never staged; no hardcoded LOAN2 names/bytes/positions in the
compiler; predictions commit BEFORE compiler edits; every rc direct.

SUPERSEDED-BY-ABOVE: ### E2E-52/P2 CLOSED — NO ACTIVE ROUND (2026-11-04; hop 2 registration session at HEAD `755bf1c` + this close-prose commit; E52G REGISTERED, panel 1196 byte-exact / 0 of 1196; ledger ENDS **C358**): successor confirms HEAD/tree (only the operator's `handoff.config.json` edit may be dirty), runs `/handoff verify`, records state and **STOPS** — await an operator brief. Standing PROPOSALS and constraints live in `HANDOFF.md` item 0 and the Current-phase record above (shortlist, NEVER authorizations); the P1-era "E52G joins `spec/DIVERGENT.txt`" proposal is OBSOLETE (G is byte-exact and registered). No push; goldens never re-derived; NEVER re-run the retry-DFS; no expansion to other LOAN2 blockers; operator `handoff.config.json` never staged; all rc captured DIRECTLY.

SUPERSEDED-BY-ABOVE (kept as written; its steps (a)-(e) were EXECUTED IN FULL this hop — registration `dca9219`, COVERAGE `90582a5`, LOAN2 blocker recorded UNCHANGED, RESULTS `755bf1c`, close prose + finalize this): ### E2E-52/P2 hop 2 OWED (2026-11-04; renewed 1/12 from checkpoint g274; arm `d67a263` landed+gated, durable commits `a365686`/`d67a263`/`c34c690`/`546c70a`+this; at HEAD only operator `handoff.config.json` may be dirty)

Execute IN ORDER, all rc captured DIRECTLY (never trailing pipelines):
(a) register E52G: add `"E52G": ("probes/E52G.PLI", "golden/e52p1/E52G/E52G.REL")` to
the LAST `SPECIMENS.update({...})` block in `tools/e2e_gate.py` (the e52p1 block ~line
1894); run `python3 tools/e2e_gate.py --update-inventory` (expect INVENTORY 1195->1196,
diff exactly ONE line E52G); rerun `timeout 3600 python3 tools/e2e_gate.py` to
`build/gate-e52p2-reg.log`, expect REAL rc=0 and **1196 byte-exact / 0 of 1196**; commit
explicit paths (gate script + INVENTORY).
(b) update COVERAGE row `PROC.DEC_FORMAL_COPYIN_CELLMAP` (spec/COVERAGE.tsv line 144):
`mine_status` DIVERGENT->EXACT and `rel_parity` DIVERGENT:1->EXACT:1 (validator
vocabulary: EXACT:n|DIVERGENT:n|MIXED:e/d|NONE); E52G is NOW a panel key -- cite the
specimen AND keep the golden path; rewrite the residual sentence to measured reality
(copy-in temp implemented via Bind `cs_copies`; refusals unchanged for unmeasured
forms); cites stay [C358] [C131] [C187]; NO new rows (139 stays). Run
`python3 tools/coverage_check.py`, expect rc=0 139 rows 0/0; commit.
(c) LOAN2: compile `artefacts/LOAN2.PLI` UNMODIFIED with pli80c.exe (positional args,
scratch `build/e52p2/`), record the blocker line VERBATIM (last known: `codegen: PUT
FILE with a bare PAGE control item [TBD] (line 99)`); advance/fix NOTHING; never claim
LOAN2 exact.
(d) write `spec/lab-evidence/e2e52-p2/RESULTS.md` (difference, mechanism,
predictions-vs-measured, parity, E52A-J/E51 effects, gate actuals rc, LOAN2 blocker,
NOT-say/remaining unsupported copy forms); NO new claim (C358 states the law; may add
an implementation-landed NOTE to the C358 entry ONLY if justified -- default: no).
(e) close prose (PROGRESS Current-phase + Next action + HANDOFF item 6 -> E2E-52/P2
CLOSED; standing proposals kept incl. dashboard **26**), commit explicit paths, then
handoff_finalize (or renew at the safe boundary if permitted). STOP after P2; no push;
goldens never re-derived; operator handoff.config.json never staged.

SUPERSEDED-BY-ABOVE (kept as written):
### E2E-52/P1 CLOSED — NO ACTIVE ROUND (2026-11-04; hop 6 closing session at HEAD `22b9c0c` + this close commit; ledger ENDS **C358**): successor confirms HEAD/tree (only the operator's `handoff.config.json` edit may be dirty), runs `/handoff verify`, records state and **STOPS** — await an operator brief

The hop-6 contract below (steps a-d) is DONE in full: (a) the three E52 COVERAGE rows
are MAPPED in `spec/functional/capabilities.tsv` (inspect-first honored: the failing
check is the stale hardcoded `**26**` string at `tools/test_functional_dashboard.py:132`
compared against the live unmapped count — mapping the rows is the legitimate fix; no
spec prose was touched to paper over anything) and the rendered doc refreshed via
`--write` (rc=0, `--check` rc=0); the still-remaining rc=1 is the PRE-EXISTING stale
constant alone, recorded verbatim and NEVER fixed — its refresh is a standing PROPOSAL,
not an authorization for this round; (b) census `--check` rc=0 counts identical,
coverage stats not drifted, FULL gate **REAL rc=0** DIRECT →
`build/gate-e52p1-reg2.log` (1195/0 of 1195, 181/181, 9/9, 139 rows 0/0, census
15/0/26/0, prose 5); (c) close prose: this section + Current phase + HANDOFF item 6 →
**E2E-52/P1 CLOSED** with E52G an OPEN `my-gap` + PROPOSAL (copy-in-temp arm at a
future authorized hop; whether G joins `spec/DIVERGENT.txt` stays PROPOSED, never
adopted); (d) attest + explicit-path commit of durable files (never
`handoff.config.json`). **STOP after P1.**

SUPERSEDED-BY-ABOVE (kept as written; its remaining steps 4-7 and the hop-6 addendum's
steps a-d were EXECUTED by hops 5 and 6 as recorded above): ### E2E-52/P1 hop 5 PARTIAL — steps 1-3 LANDED (`e2a9866` RESULTS §5; `68bba2d` g268 blocks; `edf4a25` 9 SPECIMENS + INVENTORY 1186→1195 + post-update gate **REAL rc=0** 1195/0; `7176ff8` claims **C356..C358**, ledger ENDS **C358**, prose rc=0); COVERAGE rows (4), census/stats (5), ALL harness self-tests (6), CLOSE prose + attest (7) OWED (2026-11-04; renewals 4/12 used)

RE-VERIFIED this session at `ceb302c` (binary `2785a1b6…`, identical rebuild of arm
`6a4c554`, dune rc=0): NINE specimens whole-file BYTE-EXACT vs `golden/e52p1`
(A,B,C,D,E,F,H,I,J; controls A/E/F/J byte-identical to BASELINE shas
`8217250a`/`4fe89c7d`/`8c09f2e7`/`0a3f6b6a`), E52G rc=0 NOT exact (mine `6ea285ba…`,
DATA 000F vs 0014, CODE 003A vs 004A; residual EXACTLY the §2.3 cell map, full record
reldump diff kept verbatim in RESULTS §5; condition-4 stop, NEVER fitted); E51 sweep
12/12. `--update-inventory` diff = exactly 9 lines, NO E52G. Gate ACTUALS
`build/gate-e52p1-reg.log`: 1195/0 of 1195, 181/181, 9/9, 136 rows 0/0, census
15/0/26/0, prose 5.
OWED EXACTLY (hop 5 remainder, in order; full ACTUALS in `LEARNINGS.md` § "E2E-52/P1
hop 5 PARTIAL"): (4) append THREE COVERAGE rows to `spec/COVERAGE.tsv` AFTER the
inventory update (done): DECL row [C356] lexical shadow/accumulation law (probes
E52B,C,D,E,H,I, `EXACT:6`, corpus LOAN2, MEASURED); pool row [C357] image-keyed
program-wide dedup (probes E52A,B,D,F,H,I, `EXACT:6`, MEASURED); PROC row [C358] DEC
formal cell map — **E52G is NOT a panel key, cite the PATH
`golden/e52p1/E52G/E52G.REL`; `mine_status=DIVERGENT`, `rel_parity=DIFFERS:1`,
`confidence=SINGLE_SAMPLE`; NEVER cite G byte-exact**; schema
`spec/COVERAGE-SCHEMA.md`, validator `tools/coverage_check.py` — run it, expect 139
rows 0/0, rc captured DIRECTLY; commit rows + (if their own write paths move) stats.
(5) census/stats via their OWN write paths only if head/binary moved
(`corpus_census.py --check spec/census/corpus-census.json`). (6) ALL harness
self-tests at this registration hop — `tools/test_functional_dashboard.py` rc=1 stale
`**26**` check is PRE-EXISTING: record verbatim, NEVER silently fix; run the FULL gate
AGAIN post-COVERAGE with rc DIRECT. (7) close prose (PROGRESS Current-phase + Next
action + HANDOFF item-6: **E2E-52/P1 CLOSED** with G an OPEN `my-gap` + PROPOSAL
(copy-in-temp arm at a future authorized hop; PROPOSED, never adopted: whether G joins
`spec/DIVERGENT.txt`); standing PROPOSALS list retained: FCPS1..3 registration, README
§ 5.1 rights review, E2E-50/P3 shortlist; dashboard `**26**` refresh; successor without
an operator brief records state and STOPS) + refresh/attest via handoff_finalize +
explicit-path commit of durable files. **STOP after P1**; no push; goldens never
re-derived/overwritten; NEVER re-run the retry-DFS; do not expand to other LOAN2
blockers; operator `handoff.config.json` never staged; all rc captured DIRECTLY.

SUPERSEDED-BY-ABOVE (kept as written): ### E2E-52/P1 hop 4 PARTIAL

### HOP 5 IN-FLIGHT ADDENDUM (2026-11-04; step 4 LANDED, dashboard finding MEASURED)

ACCEPTED: step 4 committed — 3 COVERAGE rows, `coverage_check.py` **rc=0 DIRECT, 139
rows 0/0**; the validator REJECTED `rel_parity DIFFERS:1` as MALFORMED — accepted
vocabulary is `EXACT:n|DIVERGENT:n|MIXED:e/d|NONE`; the G row shipped as
`DIVERGENT:1` (lesson kept). MEASURED (accepted, unresolved): step 6 first run —
`python3 tools/test_functional_dashboard.py` **rc=1**, the ONLY failure verbatim:
`FAIL  integration: unmapped COVERAGE rows are listed, not dropped` (the log tail does
NOT show the known stale `**26**` check this time) — the three NEW E52 rows are
unmapped in the dashboard capability mapping; the known-pre-existing `**26**` drift
finding is superseded IN PART by this measurement, kept as written.
NEXT ACTION (successor, hop 6, exact order): (a) map the three rows
(`DECL.DEC_POOL_LEXICAL_SHADOW`, `DECL.DEC_POOL_IMAGE_DEDUP_PROGRAMWIDE`,
`PROC.DEC_FORMAL_COPYIN_CELLMAP`) where `tools/functional_dashboard.py`/its capability
map expects (inspect the failing check first; do NOT touch spec prose to paper over
it), rerun dashboard to rc=0 (or record a still-pre-existing rc=1 verbatim incl. the
`**26**` check if it reappears); (b) census + coverage stats via their OWN write paths
if drifted (`corpus_census.py --check spec/census/corpus-census.json`; stats per the
E2E-49/P4 part-2a precedent) then FULL gate `timeout 3600 python3 tools/e2e_gate.py`
with rc DIRECT (expect 1195/0, 181/181, 9/9, 139 rows 0/0, census 15/0/26/0, prose 5),
log to `build/gate-e52p1-reg2.log`; (c) step 7 close prose: PROGRESS Current-phase +
this section + HANDOFF item-6 -> **E2E-52/P1 CLOSED** with E52G an OPEN `my-gap` +
PROPOSAL (copy-in-temp arm at a future authorized hop; PROPOSED, never adopted:
whether G joins `spec/DIVERGENT.txt`); ledger ENDS **C358**; standing PROPOSALS kept
(FCPS1..3 registration, README § 5.1 rights review, E2E-50/P3 shortlist, dashboard
refresh); successor without an operator brief records state and STOPS; (d) refresh +
attest (handoff_renew at a safe boundary if permitted, else handoff_finalize),
explicit-path commit of durable files. STOP after P1; no push; goldens never
re-derived; NEVER re-run the retry-DFS; no expansion to other LOAN2 blockers; operator
`handoff.config.json` never staged; all rc captured DIRECTLY, never through pipes.

SUPERSEDED-BY-ABOVE (kept as written): ### E2E-52/P1 hop 4 PARTIAL — ARM LANDED `6a4c554` (B,C,D,H,I byte-exact; A/E/F/J unchanged; E51 12/12; LOAN2 ADVANCED; census re-snapshotted; PRE-REG GATE rc=0); RESULTS §5 + REGISTRATION + CLOSE OWED (2026-11-04; renewals 3/12 used)

MEASURED this hop (accepted): scope-aware prescan arm (`pd_own` field +
`pd_vars`=TOP-only + `Sproc` arm `pd_vars = own @ cx.pd_vars`, ONE file,
codegen.ml) makes E52B,C,D,H,I whole-file BYTE-EXACT vs `golden/e52p1`; controls
A/E/F/J byte-IDENTICAL to BASELINE shas `8217250a`/`4fe89c7d`/`8c09f2e7`/`0a3f6b6a`;
E51A..L sweep 12/12. E52G: blocker GONE, pool bytes byte-identical to DR
(`00 03 00`@0000+`00 03 00 00 00`@0003) but NOT whole-file exact: DATA 000F vs 0014
— residual is EXACTLY the §2.3 formal cell map (DR: block@0x0B→temp@0x0D,
5-byte main-side copy-in temp, pointer cell @0x12; mine: block→actual cell 0x08,
NO temp, pointer @0x0D). H1 is NOT contradicted (typing/pool lexical = confirmed);
condition 4 read literally fires ONLY for row G → stop at evidence for G,
NEVER fit, NEVER implement the copy-in arm this round (out of pre-registered
PLAN §4 scope; "do not expand"). LOAN2 rerun UNMODIFIED ADVANCED: next blocker
verbatim `codegen: PUT FILE with a bare PAGE control item [TBD] (line 99)` —
RECORDED, NOT fixed (census REFUSED 26 unchanged). Census re-snapshotted via its
OWN write path (`corpus_census.py --check`, rc=0, counts UNCHANGED 15/0/26/0,
metadata + LOAN2 msg only) — UNCOMMITTED. FULL pre-registration gate REAL rc=0
(captured DIRECTLY): byte panel 1186/0 of 1186, negative 181/181, divergence 9/9,
coverage 136 rows 0/0, census 15/0/26/0, prose 5 — `build/gate-e52p1-pre-reg.log`.

OWED EXACTLY (hop 5, in order): (1) append RESULTS.md §5 "post-fix verification"
(10-row verdict table + the E52G delta verbatim incl. reldump lines; §1-§4 and
predictions UNTOUCHED); commit `spec/census/*` + RESULTS + LEARNINGS § "hop 4"
together. (2) Register the NINE byte-exact specimens (E52A,B,C,D,E,F,H,I,J —
NOT G) in `tools/e2e_gate.py` SPECIMENS + sanctioned `--update-inventory`
(expect 1186→1195) + gate AGAIN (byte-panel ACTUAL post-update; capture rc
DIRECTLY). (3) claims from **C356** ONLY from RESULTS §2 (§2.1/§2.2/§2.3 —
§2.3 claimable as measured DR law although my object differs). (4) COVERAGE rows
AFTER the inventory update (cite only registered probes/claims; schema
`spec/COVERAGE-SCHEMA.md`, validator `tools/coverage_check.py:203-247`; no row
cites G as byte-exact). (5) census via own write path again if head/binary moved.
(6) ALL harness self-tests (test_functional_dashboard.py rc=1 stale `**26**` check
PRE-EXISTING — record verbatim, NEVER silently fix). (7) close prose
(E2E-52/P1 CLOSED with G an OPEN my-gap + PROPOSAL: copy-in-temp arm at a future
authorized hop; also PROPOSED, not adopted: whether G joins spec/DIVERGENT.txt) +
`/handoff` + attest. STOP after P1; no push; goldens never re-derived/overwritten;
NEVER re-run the retry-DFS; operator handoff.config.json never staged.

SUPERSEDED-BY-ABOVE (kept as written): E2E-52/P1 IN FLIGHT — ORACLE 10/10 ACCEPTED + goldens/RESULTS committed `e14d180`; SCOPE-AWARE PRESCAN IMPLEMENTATION OWED — hop-3 contract (steps 1-2 of which are DONE — arm landed `6a4c554`, LOAN2 rerun done, pre-reg gate rc=0 done; step 3 registration OWED as re-stated above):

### E2E-52/P1 hop 3 contract (as written by hop 3; kept verbatim) (2026-11-04; hop 3 closed at context pressure; renewals 2/12 used)

Hop 3 LANDED (steps 1+2 of the contract below, `e14d180` — goldens + RESULTS committed
TOGETHER BEFORE any compiler change; `ocaml/` UNTOUCHED, `dune build` rc=0 at session
start, binary `f172d8ea…`): ONE grouped campaign `--tag e52p1` -> **10 ok / 10**, every
`.PRN` `NO ERROR(S)` in both passes, **ZERO `dr-refuses`**. Verdicts in
`spec/lab-evidence/e2e52-p1/RESULTS.md` §1/§2: six `my-gap` rows (B,C,D,G,H,I) and four
rows already whole-file cmp-BYTE-EXACT vs mine (A/E/F/J — falsification condition 3 NOT
triggered). **H1-lexical CONFIRMED** on all five pre-registered discriminators (B DATA
0x10, C CODE `21 03 00 / 22 r6` inner binary immediate, D DATA 0x0A, H CODE/reloc binds
THROUGH mid to `r3`/`rb` with `3E 09`, I DATA 0x15 = lexical prescan_cond); **H3
global-outer FALSIFIED** five times; **H4 per-scope pool FALSIFIED** twice (A, F) — the
DEC pool is ONE program-wide IMAGE-keyed table, dedup scope-blind and name-blind, cells
laid in source order ahead of the variables across scope boundaries; **H2 falsified for
DR by E** and kept as the invariant the fix must not introduce. ONE MISS kept verbatim
(PROTOCOL #2): E52G predicted "approx 16", measured **20 (0x14)** — DR gives a DEC formal
NO value cell: caller-side 2-byte arg-pointer block @0x0B -> main-side 5-byte copy-in
temp @0x0D (load `3E 04` actual / store `3E 09` formal), callee 2-byte POINTER cell
@0012, prologue `5E 23 56 EB / 22 r12`, store via `2A r12` + `?DSTOP`; reported, never
fitted. Full ACTUALS + the read-off-source implementation sketch (all ~15 `pd_vars`
consumers are pure `List.assoc_opt` first-match — verified by reading every site):
`LEARNINGS.md` § "E2E-52/P1 hop 3".

NEXT (hop 4, exact) = steps 3-5 of the hop-2 contract below, in that order:
1. Implement PLAN §4 as ONE small structured change in `ocaml/lib/codegen.ml`: new
   `pd_own : (string * (string * vkind) list) list` field in `pdec_ctx` (:1687, single
   construction site :13499); per-proc own rows via the SAME `rt_to_vk`, clash refusal KEPT
   for a duplicate-within-ONE-procedures-own-rows only; `pd_vars` = TOP rows only
   (replace `proc_vk_rows` at :13432-13452); prescan `Sproc` arm (:3300-3320) recurses with
   `{ cx with pd_ret = ret; pd_fl_ret = …; pd_vars = own @ cx.pd_vars }`. Keep pd_img/
   pd_str/pd_fl/pd_procs/pd_fl_procs/const_cells/pool base INTACT; do NOT touch `bind`.
2. `cd ocaml && eval "$(opam env)" && dune build`; compile all ten probes positionally to
   `build/e52p1-mine/` and `cmp` whole-file vs `golden/e52p1/<n>/<n>.REL`: expect B,C,D,G,
   H,I byte-exact and **A/E/F/J byte-identical to their BASELINE-MINE shas** (`8217250a`,
   `4fe89c7d`, `8c09f2e7`, `0a3f6b6a`). If any E52 object is NOT byte-exact, or a control
   moves, STOP at evidence + a corrected PROPOSAL (HYPOTHESES condition 4) — never fit
   blindly. Then sweep `probes/E51*.PLI` (expect 12/12 vs `golden/e51p1/`) and commit the
   arm ALONE.
3. `artefacts/LOAN2.PLI` rerun UNMODIFIED — record the exact next blocker verbatim if it
   advances, do NOT fix it. FULL gate `timeout 3600 python3 tools/e2e_gate.py` BEFORE
   registration (expect 1186/0, 181/181, 9/9, 136 rows 0/0, census 15/0/26/0, prose 5);
   then register: SPECIMENS block + sanctioned `--update-inventory`, gate AGAIN
   post-update, claims from **C356** ONLY from RESULTS §2, COVERAGE rows AFTER the
   inventory update, census via the tool's own write path, run ALL harness self-tests
   (the stale dashboard `**26**` check is PRE-EXISTING — record, never silently fix).
   Close prose + `/handoff` + attest; **STOP after P1**; no push; operator
   `handoff.config.json` never staged; goldens never overwritten/laundered; NEVER re-run
   the retry-DFS.

SUPERSEDED-BY-ABOVE (kept as written): hop-2 contract, whose steps 1-2 are DONE:

Hop 2 LANDED (committed `d1fbc16` BEFORE any DR call; `git log --format=%h --
probes/E52A.PLI` proves order): `spec/lab-evidence/e2e52-p1/{PLAN.md,HYPOTHESES.md,
mkprobes.py,BASELINE-MINE.txt}` + generated `probes/E52A..J.PLI` (CRLF+^Z, <=71 cols,
apostrophe-free, keys collision-checked [C193c]). BASELINE-MINE MEASURED at HEAD
`99845ae`, binary `f172d8ea...`: A rc=0 256B sha8217250a / E rc=0 sha4fe89c7d / F rc=0
sha8c09f2e7 / J rc=0 384B sha0a3f6b6a (same-kind or no homonym — compile today); B/C/D/
G/H/I rc=2 `declared with conflicting kinds ... [TBD]` (LOAN2 class). Scratch design
checks (BASELINE-MINE appendix, NOT panel probes): S2 LITERAL-store-to-DEC-FORMAL rc=0 —
E52G is blocked ONLY by the name clash, the route exists; S6 (bin store + proc-local
dec(7,2) store) rc=0; S7 (two-level `if y > 0 then y = 1`) rc=0. `ocaml/` IDENTICAL
`e15e325`..HEAD; `golden/e52p1` VERIFIED ABSENT; no DR call made yet.

NEXT (hop 3, exact):
1. ONE grouped campaign: `cd /home/john/projects/sushiworks/pli80 && PLI_SRC=probes timeout 900 python3 oracle/batch.py E52A E52B E52C E52D E52E E52F E52G E52H E52I E52J --tag e52p1 --switches '$L$D'` (NEVER --reuse; timeout preserved/classified, never retried).
2. Inspect every .PRN + complete .REL (`tools/reldump.py`, whole-file cmp); classify each row `dr-refuses`/`my-gap`/`unmeasured` against the HYPOTHESES.md per-row table (models H1-lexical / H2-own-only / H3-global-outer / H4-per-scope-pool; DATA and CODE discriminators THERE). Write RESULTS.md (verdicts + every MISS verbatim PROTOCOL #2; laws ONLY from measured §2; §3 NOT-say); commit goldens + RESULTS TOGETHER BEFORE any compiler change.
3. Implementation ONLY after evidence, one small structured change (direction pre-registered in PLAN §4): `pd_vars` (codegen.ml:13438) starts as TOP rows ONLY; per-proc own-rows table via the SAME `rt_to_vk`; the prescan `Sproc` arm (~3300) recurses with `{ cx with pd_vars = own @ cx.pd_vars }` — assoc first-match = lexical shadow, mirroring `lower_proc` (~12210) `st.vars <- attach proc_rows pl_rows @ saved`. Keep pd_img/pd_str/pd_fl dedup refs, pd_procs, pd_fl_procs, const_cells, pool base INTACT; keep a clash check WITHIN one accumulation; do NOT touch bind (outer_rows dead). Invariants: A/E/F/J objects byte-IDENTICAL to BASELINE-MINE shas; [C179] demand==allocation; unsupported constructs still refused BY NAME. If a DR object contradicts H1, STOP at evidence + PROPOSAL — never fit blindly.
4. Verify: `cd ocaml && eval "$(opam env)" && dune build`; new accepted specimens whole-file byte-exact vs `golden/e52p1/<n>/<n>.REL`; regression sweep E51A..L (expect 12/12) + panel intact; LOAN2 rerun UNMODIFIED — record the exact next blocker if it advances, do NOT fix it.
5. FULL gate `timeout 3600 python3 tools/e2e_gate.py` BEFORE registration (expect 1186/0, 181/181, 9/9, 136 rows 0/0, census 15/0/26/0, prose 5); then register: SPECIMENS block + sanctioned `--update-inventory`, gate AGAIN post-update (byte-panel ACTUAL from the post-update run); claims from **C356** derived ONLY from RESULTS §2; COVERAGE rows AFTER inventory; census via the tools own write path; run ALL harness self-tests at this registration hop (stale dashboard `**26**` check is PRE-EXISTING — record, never silently fix). Close prose + `/handoff` + attest; **STOP after P1**; no push; operator `handoff.config.json` never staged; goldens never overwritten/laundered; NEVER re-run the retry-DFS.


### SUPERSEDED (kept as written): E2E-51/P2 CLOSED — NO ACTIVE ROUND (2026-11-04; HAMM-00 rev2 LANDED `a21a586`, record `52f9a54`): successor confirms HEAD/tree, runs `/handoff verify`, records state and **STOPS** — await an operator brief

E2E-51/P2 is DONE in full and measured: reference-model `fed0:` correction + re-derived
212-line expectation committed BEFORE execution (`a21a586`); SOURCE/DERIVATION
pre-verified via stage ceiling (`build/fc01/hamm-rev2-srcder/`); lane B **six-stage PASS**
rc=0 direct (`build/fc01/hamm-rev2/records.json`); `--double-run` PASS byte-equal
(`build/fc01/hamm-rev2-double/`); hostile suite 211/211; FULL compile-tier gate rc=0
(`build/gate-hamm00-rev2.log`, 1186/0 of 1186 — P1 panel intact); docs § 17 + § 1 row
committed (`52f9a54`); § 16 rev1 FAIL kept intact; no DR claim promoted (ledger ENDS
**C355**). **Standing PROPOSALS (NEVER authorizations):** refresh the stale
`test_functional_dashboard.py` hardcoded `**26**` check (MEASURED pre-existing at P1 HEAD
`1fc37d5`, drift from `216ea7a`; run ALL harness self-tests at future registration hops);
FCPS1..3 SPECIMENS registration at a gate hop; README § 5.1 rights review for the eight
corpus sources (due); E2E-50/P3 shortlist (`spec/lab-evidence/e2e50-p2/REPORT.md` § 5);
fc01-fileio/ONUNIT-00 stay CANCELLED.

### SUPERSEDED (kept as written; the "HAMM-00 rev2 derivation fix" proposal below was AUTHORIZED and LANDED as E2E-51/P2 above): E2E-51/P1 CLOSED — NO ACTIVE ROUND (2026-11-04, closing session at HEAD `0c61c8d`): successor confirms HEAD/tree, runs `/handoff verify`, records state and **STOPS** — await an operator brief

The hop-6 closure contract below (kept as written) is DONE in full: (1) prose check run
STANDALONE, exit code captured DIRECTLY (no pipeline): **rc=0**, 5 active files clean,
nothing to fix (`build/prose-check-e51p1-close.log`); (2)+(3) close prose in HANDOFF.md
item-6 + this file (Current phase + Next action → CLOSED); (4) explicit-path commit of the
durable files only (never `handoff.config.json`, no push), then attest via handoff_finalize.
**Standing PROPOSALS (NEVER authorizations):** HAMM-00 rev2 **derivation fix** — add the
`fed0:` loop-entry skip to `reference.py:_Hamm00Port` and re-derive the expectation (the OLD
"rev2 subtraction-loop division" workaround is OBSOLETE: variable-divisor division now
compiles byte-exact; do NOT propose or implement it); FCPS1..3 SPECIMENS registration at a
gate hop; README § 5.1 rights review for the eight corpus sources (due); E2E-50/P3 shortlist
(`spec/lab-evidence/e2e50-p2/REPORT.md` § 5); fc01-fileio/ONUNIT-00 stay CANCELLED. Ledger
ENDS **C355**.

### SUPERSEDED (kept as written; COMPLETED by the closing session above): Hop-6 closure status (2026-11-04; start HEAD `cc164a2`) — coverage cites FIXED rc=0; post-coverage FULL gate rc=0 (1186/0, 181/181, 9/9, 136 rows 0/0, census 15/0/26/0, prose 5; `build/gate-e51p1-reg2.log`); HAMM-00 rev1 UNMODIFIED rerun: DIV blocker GONE — COMPILE rc=0/LINK/RUN PASS, **ASSERT FAIL `missing [] / extra ['']`** (one extra blank line, blocker LOCATED + recorded in docs/functional-results.md NEW § 16 + § 1 row (both written, uncommitted)); attr `undefined`, expectation untouched, nothing laundered (`build/fc01/hamm-rerun/`). Full ACTUALS: `LEARNINGS.md` § "E2E-51/P1 hop 6 (closure)".

OWED EXACTLY (successor, closure remainder): root cause ACCEPTED: pinned source `fed0:` loop re-enters at a leading `put skip;` (line 131) so the feed over-ask prints blank-THEN-prompt; `reference.py:_Hamm00Port` is not statement-faithful for that loop (prompt-first) — the DERIVATION, not the compiler, missed one blank (`my-gap` port model; rev2 re-derivation is a PROPOSAL, not executed). Remaining: (1) `python3 tools/file_prose_check.py`, fix only flags on my new § 16 prose; (2) commit ONE commit explicit paths `spec/COVERAGE.tsv spec/census/coverage-stats.json docs/functional-results.md HANDOFF.md PROGRESS.md LEARNINGS.md` — NEVER handoff.config.json, no push; (3) close prose: HANDOFF item-6 -> `E2E-51/P1 CLOSED`, PROGRESS Current-phase/Next action -> CLOSED no-active-round (successor verifies, records, STOPS; standing PROPOSALS: HAMM-00 rev2 derivation fix adding fed0 loop-entry skip, FCPS1..3 SPECIMENS registration, README § 5.1 rights review, E2E-50/P3 shortlist); (4) re-commit durable files, attest via handoff_finalize, STOP after P1** — no P2/LOAN2/CREATE without an operator brief. Ledger ENDS **C355**. Uncommitted working tree AT THIS CHECKPOINT: the two COVERAGE cite fixes, coverage-stats.json, LEARNINGS § above, HANDOFF/PROGRESS prose; `handoff.config.json` = OPERATOR's, never touch/stage/revert. dune: `/home/john/.opam/default/bin/dune`, run from `ocaml/`.
### SUPERSEDED (kept as written): hop-5 pre-flight status

Verified this session: `dune build` rc=0 (rebuilt binary `f172d8eae2a7…`; `ocaml/` identical
`ee589cc`..HEAD so any sha delta vs the predecessor's `2cd1de5cdf22…` is build noise); sweep
RE-RUN **12/12 whole-file BYTE-EXACT** vs `golden/e51p1/`; census write path is
`corpus_census.py --check`; coverage rows MUST postdate `--update-inventory` (panel-key rule);
my first CLAIMS.md 3-edit append failed atomically on a whitespace/em-dash anchor — NOTHING was
written to `spec/CLAIMS.md` yet (ledger still ends C352). The contract below (hop 4) stands
unchanged; the claim decomposition and row proposals are in that LEARNINGS §.

## E2E-51/P1 ALL THREE ARMS LANDED — 12/12 GOLDENS BYTE-EXACT; REGISTRATION OWED, THEN STOP (2026-11-04; HEAD `ee589cc`; compiler sha `2cd1de5cdf22…` + arm 3)

ARM 3 `ee589cc` (E51I TEST consumer) landed ALONE, keyed ONLY on the measured shape
(`Eq`; left an unwrapped `is_var_divisor_div`; right `is_plain_num_auto`) and emitting the golden
head verbatim: `<div parking> / E5 / 2A r(c) / D1 / CD ?IS22N / 7C / B5 / C2 <fwd>` + the
forward-fixup triple `SET-LC 001C / RELOC code 0x24 / SET-LC 0024` (CODE 0027). Sweep ALL 12
probes E51A..E51L: **12/12 whole-file BYTE-EXACT** (skipped the `cmp` only, each .REL vs
`golden/e51p1/<n>/<n>.REL`). FULL compile-tier gate **rc=0** `build/gate-e51p1-arm3.log`: byte
panel **1174/0 of 1174**, negative **181/181**, divergence **9/9**, coverage **133 rows 0/0**,
census **15/0/26/0**, prose **5 active clean**; `dune build` rc=0. FALSIFIED prediction kept as
written: skip byte `CA` ([C072] reading) — measured `C2`/JNZ, the [C089] zero-test polarity.

EXACT NEXT (registration; nothing else is authorized):
(1) claims from **C353** derived ONLY from `spec/lab-evidence/e2e51-p1/RESULTS.md` §2 (§2.1
parking law incl. literal/compound/chained/negate-then-park dividend slots + the [N303] 1-byte
divisor interleave; §2.2 quotient consumption — ADD orientation-free right-first, PUT [C079]
width over a helper RESULT, TEST `C2` polarity + fixup triple; §2.3 constant-divisor boundary;
§3 stays unmeasured) — cite goldens `golden/e51p1/*` + probes `probes/E51*.PLI`; 11 `my-gap`
rows A..K closed, E51L control byte-exact.
(2) SPECIMENS: register the 12 `e51p1` specimens in `tools/e2e_gate.py`, then sanctioned
`python3 tools/e2e_gate.py --update-inventory` (expect panel **1174 -> 1186**), then run the gate
AGAIN so the byte-panel ACTUAL is post-update (the P4 `cc43963` cycle).
(3) census re-snapshot via the tool's own write path; (4) COVERAGE rows for the new classes
(schema `spec/COVERAGE-SCHEMA.md`, validator `tools/coverage_check.py:203-247`); (5) INVENTORY.
(6) **HAMM-00 rev1 rerun UNEDITED** — its A-class blocker (`z = x / y` store) is now
byte-covered by arm 1; record the lane ACTUAL verdict (functional, NOT a DR claim); if it FAILs
for a DIFFERENT reason, record it, never launder.
(7) close prose + `/handoff` + attest, then **STOP after P1**. NO P2/LOAN2/CREATE without an
operator brief.

SUPERSEDED-BY-ABOVE (kept as written):

## E2E-51/P1 ARMS 1+2 LANDED AND GATED (11/12 goldens byte-exact); ARM 3 (E51I TEST) + REGISTRATION OWED (2026-11-04; HEAD `7d17b63`; compiler rebuilt with both arms)

DONE this session: **arm 1 `4ff1ea5`** (Div parking in `ocaml/lib/codegen.ml`:
`lower_hl l / PUSH H / lower_hl r / POP D / CD ?ID22N`, E51K N303 1-byte interleave,
`last_imm` cleared; unmeasured classes — Esuffix divisor, deref/based/qualified —
refused BY NAME) made E51A,B,C,D,E,F,H,J,K,L **10/12 whole-file BYTE-EXACT ALONE**;
**arm 2 `7d17b63`** (E51G ADD right-first+XCHG consumer, keyed exactly on the measured
shape via `is_var_divisor_div`) made it **11/12**. FULL gate rc=0 at EACH arm alone
(`build/gate-e51p1-arm1.log`, `build/gate-e51p1-arm2.log`: 1174/0, 181/181, 9/9,
133 rows 0/0, census 15/0/26/0, prose 5). E51H needed NO consumer arm (existing PUT
route already byte-exact — empirical resolution, kept as recorded).
OWED NOW, in order:
(1) **arm 3 = E51I TEST consumer**: the refusal is verbatim `condition form not in
E2E-3b subset [TBD]: (= (/ a b) c)`; golden tail after `<div>` is `E5 / 2A r4 / D1 /
CD ?IS22N / 7C / B5 / C2 <fwd> / 21 01 00 / 22 r6` + fixup triple `SET-LC 001C /
RELOC code 0x24 / SET-LC 0024` (CODE 0027) — JNZ `C2` = [C089] polarity, the CA
prediction was FALSIFIED at the oracle. Admit ONLY `Eq` with a measured-class
variable-divisor-DIV left and plain-variable right; reuse the park/IS22N/zero-test/
emit_triple machinery; everything else keeps refusing. Build, sweep all 12 probes
(12/12 byte-exact expected), FULL gate rc=0, commit ALONE.
(2) **registration**: claims from **C353** (RESULTS §2 ONLY); SPECIMENS registration of
the 12 e51p1 probes in `tools/e2e_gate.py` + sanctioned `--update-inventory` (panel
1174 -> 1186; run the gate again AFTER so the byte-panel ACTUAL is post-update); census
re-snapshot via the tool's own write path; COVERAGE rows; INVENTORY.
(3) **HAMM-00 rev1 rerun UNEDITED** — its blocker (`z = x / y` store, A-class) is now
byte-covered; record the lane ACTUAL verdict (functional, NOT a DR claim), never launder.
(4) Close prose + `/handoff` + attest, then **STOP after P1**.
Full detail: `LEARNINGS.md` § "E2E-51/P1 hop 3". Constraints unchanged: no push;
operator `handoff.config.json` dirty — never stage/clean/revert; goldens never
laundered; renew only at safe boundaries.

SUPERSEDED-BY-ABOVE (kept as written):

## E2E-51/P1 IN FLIGHT — ORACLE DONE 12/12 ACCEPTED, goldens+RESULTS COMMITTED `b404b7e`; IMPLEMENTATION ARMS OWED (2026-11-04; HEAD `b404b7e`; compiler `edce9e0e…` built rc=0)

Read `LEARNINGS.md` § "E2E-51/P1 hop 2" FIRST — it carries the batch ACTUALS, the two
MISSes kept verbatim (E51B H-B-de falsified/H-B-stack HIT; E51I `C2` not `CA`), the
RESULTS §2 laws and the full PROPOSED implementation analysis. DONE: pre-registration
`9bac977`; ONE grouped batch (12 ok/12, no DR refusals, all `.PRN` NO ERRORS both passes);
RESULTS.md + goldens committed TOGETHER at `b404b7e` (predictions untouched).
OWED NOW, in order: (7) implement arm 1 in `ocaml/lib/codegen.ml` Div arm (~5010): replace
`DIV by non-constant [TBD]` with the measured parking `lower_hl l / PUSH H / lower_hl r /
POP D / CD ?ID22N` (+ E51K 1-byte interleave like MUL N303; keep unmeasured operand classes
— deref/pointer formals, call divisors — REFUSED); `dune build`; compile every
`probes/E51*.PLI` with `./ocaml/_build/default/bin/pli80c.exe` and `cmp` each .REL
whole-file vs `golden/e51p1/<n>/<n>.REL`; ONLY lines that mismatch get further consumer
arms (expected: E51G right-first+XCHG in the general ADD arm — resolve empirically, not by
reasoning; E51H PUT item and E51I equality-TEST consumers); each arm independently
committed with regression sweep + FULL `python3 tools/e2e_gate.py` rc=0; (9) claims from
**C353** derived ONLY from RESULTS §2; SPECIMENS registration + sanctioned
`--update-inventory`; census re-snapshot; COVERAGE rows; INVENTORY; (10) HAMM-00 rev1
rerun UNEDITED if its forms are byte-covered (blocker = A-class store form). **STOP after
P1.** No push; operator `handoff.config.json` dirty at HEAD — never stage/clean/revert it;
goldens/ignored evidence never laundered.

SUPERSEDED-BY-ABOVE (kept as written):

## E2E-51/P1 IN FLIGHT — FIXED BINARY variable-divisor DIV (operator-authorized 2026-11-04; baseline HEAD `ac68352`; compiler `edce9e0e…` built rc=0)

Read `LEARNINGS.md` § "E2E-51/P1 hop 1" FIRST — it carries the ACCEPTED F005 witness
(`golden/f6probe/F005/F005.REL` proves DR accepts `z = a / b` binary, PUSH H/LHLD/POP D/ID22N),
the falsified historical-witness search, and the full PROPOSED byte-prediction table. DONE so
far: round survey + `spec/lab-evidence/e2e51-p1/mkprobes.py` written (12 probes E51A..E51L,
CRLF+bare ^Z, <=71 cols). OWED NOW, in order: (1) `python3 spec/lab-evidence/e2e51-p1/mkprobes.py`;
(2) BASELINE-MINE.txt (per-probe positional compile, timeout 60, rc/refusal-verbatim or
reldump of the .REL); (3) PLAN.md + HYPOTHESES.md; (4) explicit-path pre-registration commit
BEFORE any DR call; (5) ONE grouped oracle batch `--tag e51p1 --switches '$L$D'` (golden/e51p1
must not pre-exist; never --reuse; explicit timeout); (6) RESULTS.md + classification + commit;
(7) implement arms ONLY per measured evidence; (8) `python3 tools/e2e_gate.py`; (9) claims
C353+, COVERAGE/SPECIMENS/census/INVENTORY; (10) HAMM-00 rev1 rerun unedited if covered, else
record as unmeasured-still. **After P1 STOP.** No push; operator `handoff.config.json` is the
dirty file at HEAD — never stage/clean/revert it.

SUPERSEDED-BY-ABOVE (kept as written):

## FC-01 CORPUS CLOSED — FFT-00 hop 22 LANDED (steps 7-11 DONE; program 8 of 8 **PASS**; corpus 8/8; NO ACTIVE ROUND — successor records state and STOPS) (2026-11-03)

DONE this hop (ACTUALS in `LEARNINGS.md` § "…FFT-00 hop 22"): `FFT-00.json` GENERATED
VIA SCRIPT (`build/fc01-scratch/fft00/mk_fft00_json.py`; gates: pin sha `f58e471b…`,
CRLF/^Z/≤71/apostrophe laws, derive-vs-sim byte-equality RE-RUN and abort-on-mismatch
— 13 lines + raw 507 B sha `87acbf18…`; 9 capability ids double-verified
(DECL.FIXED_BIN15, DECL.CHAR_VARYING, AGG.ARRAY_1D_FIXED, AGG.VAR_INDEX_LADDER,
LOOP.DO_TO_BY, EXPR.REL_FIXED_EQ_K, IO.PUT_LIST_FIXED, IO.PUT_SKIP, PROC.CALL_COPYIN);
`AGG.ELEM_AS_ACTUAL` FALSIFIED-absent by grep and dropped, nonexistent
`EXPR.REL_FIXED_LT_K` dropped; asserts no GET and no `put list(<digit>)`; link FFT00,
`console_input "^Z"`, collapse-spaces-v1, notes (1)-(16) full removal list) →
`--stages source,derivation` UNKNOWN [COMPILE: stage ceiling], no SOURCE/DERIVATION
FAIL → lane B `build/fc01/corp10/` **PASS first run** (COMPILE rc=0 3456 B code=1476
data=48 items=1739; LINK FFT00.COM 9088 B sha `9f86815d…` `parse_undefined=[]`; RUN
done **507 console bytes BYTE-IDENTICAL to the derived port raw** sha `87acbf18…`;
ASSERT 13-line complete-stream match; verdicts PASS=1 FAIL=0 BLOCKED=0 UNKNOWN=0) →
double-run `build/fc01/corp10-double/` PASS, `cmp` rc=0 sha `87acbf18…` → docs
`functional-results.md` § 15 + § 1 row + **CORPUS CLOSE** subsection (seven PASSes +
HAMM-00 rev1 recorded `my-gap` FAIL; two drafting self-corrections kept as written:
the six-vs-seven tally garble and an unmeasured "33 shapes" count) → FULL compile-tier
gate rc=0 `build/gate-fft00.log` (1174/0, 181/181, 9/9, 133/0/0, 15/0/26/0, prose 5).
**NEXT ACTION: none is authorized.** The FC-01 operator override is DELIVERED; a
successor session WITHOUT an operator brief confirms HEAD/tree (`git status`; only the
operator's `handoff.config.json` edit may be dirty), runs `/handoff verify`, records
state and STOPS. Standing PROPOSALS (never authorizations): HAMM-00 rev2 subtraction
loop; FCPS1..3 SPECIMENS registration at a gate hop; README § 5.1 rights review for the
eight corpus sources (explicit deliverable, now DUE); E2E-50/P3 shortlist in
`spec/lab-evidence/e2e50-p2/REPORT.md` § 5; fc01-fileio/ONUNIT-00 stay CANCELLED.
Constraints unchanged: no `ocaml/`/harness byte; ledger ends C352; functional runs NOT
DR claims; FAILs never laundered; NEVER re-run the retry-DFS; third-party bytes
untracked; operator `handoff.config.json` untouched/unstaged; no push.

SUPERSEDED-BY-ABOVE (kept as written):

## FFT-00 hop 21 LANDED — steps 5+6 DONE (pin + order audit + reference byte-equal vs sim); steps 7-11 OWED (2026-11-03)

DONE this hop (ACTUALS in `LEARNINGS.md` § "…FFT-00 hop 21"): pin `spec/functional/tests/
FFT-00.PLI` sha `f58e471b…` (3400 B, 122 lines ≤71, CRLF+bare ^Z) compiles rc=0 3456 B
(code=1476 data=48), .REL byte-identical to the draft; `order_audit.py` GREEN (emission order +
78-pair statement bijection, hop-19 lesson); `reference.py` gained `_Fft00Port`/`fft00()`/
`DERIVATIONS["fft00"]`, `derive('fft00')` BYTE-EQUAL vs `fft00_sim.check()` (13 lines, raw 507 B
sha `87acbf18…`) BEFORE any JSON; gate rc=0 `build/gate-fft00-pin.log`.
OWED (steps 7-11, exact contract in that LEARNINGS §): (7) `FFT-00.json` VIA SCRIPT with the
mk_dhry00_json.py gates (re-run sim-vs-derive byte-equality and abort on mismatch; pin sha;
CRLF/^Z/≤71/apostrophe laws; `link_target FFT00`; `console_input "^Z"`; collapse-spaces-v1;
capabilities grep-verified ACCEPTS/SUPPORTED in `spec/COVERAGE.tsv` AND present comment-stripped
in the .PLI — verify `AGG.ELEM_AS_ACTUAL` really occurs before citing it; notes = every removal
(COMPLEX/CONTROLLED/ALLOCATE/recursion/HBOUND/exp/FIXED/FLOAT(18)/BINARY(31)/REORDER/whole-array
actual) + the Q6 scale + twiddle 45/64 + the sg-flag gap + the FP00 runtime laws + the `0 - 45`
pool-mismatch crash witness + the `rem*1000` bin15 bound) → `python3 tools/functional_runner.py
--stages source,derivation --tests FFT-00`; (8) lane B `python3 tools/functional_runner.py --tests
FFT-00 --evidence build/fc01/corp10 --json-out build/fc01/corp10/records.json` (+ `--double-run`
build/fc01/corp10-double if PASS), ACTUALS verbatim, FAIL stays classified never laundered,
expectation never edited to chase PASS; (9) `docs/functional-results.md` § 15 + § 1 row; (10)
`python3 tools/e2e_gate.py` → `build/gate-fft00.log`; (11) explicit-path commit (NEVER
`handoff.config.json`; no push), THEN THE CORPUS-CLOSE RECORD (8 of 8).
Constraints unchanged: no `ocaml/`/harness byte; ledger ends C352; functional runs NOT DR claims;
NEVER re-run the retry-DFS; third-party bytes untracked; operator `handoff.config.json`
untouched/unstaged; no push; renew only at safe boundaries.

SUPERSEDED-BY-ABOVE (kept as written):

## FFT-00 hop 20 LANDED — construct audit + FP00 lane-B laws MEASURED; sims 3-way GREEN; DRAFT rc=0; steps 5-11 OWED (2026-11-03; NOTHING tracked authored yet; program 8 of 8 IN FLIGHT)

Read `LEARNINGS.md` § "…FFT-00 hop 20" FIRST — it carries every ACTUAL (12 construct
probes: COMPLEX/CONTROLLED/HBOUND/FIXED/EXP/BINARY(31)/REORDER/whole-array-actual all
REFUSED; recursion compiles, unwitnessed on lane B; `(m+31)/64` and negative-literal
actuals ACCEPTED; `0 - 45` expression actual = pool-mismatch crash witness), the FP00
lane-B RUN laws (negative %9d signed right-justified; division TRUNCATES TOWARD ZERO;
signed multiply exact; scalar-vs-scalar `if b < z` runs), the falsified nested
two-variable ordered compare (`if v < z` AND the swap `if z > v` both refuse — pointer
deref both sides; FIX = sg flag computed in MAIN, formal-vs-literal `=` inside prn),
and the exact owed steps 5-11: convert `build/fc01-scratch/fft00/FFT-00.draft.pli`
(122 lines, ≤71 cols, rc=0 3456 B code=1476 data=48) to CRLF+bare^Z → pin
`spec/functional/tests/FFT-00.PLI` + compile pin + `cmp` vs draft .REL → **pin-vs-sim
ORDER audit** (hop-19 lesson) → `reference.py:_Fft00Port`/`fft00()`+DERIVATIONS diffed
BYTE-EQUAL vs `fft00_sim.check()` (port==published Q6 table; ≤0.008 vs naive DFT tol
0.02; 13 lines; raw 507 B) BEFORE JSON → `FFT-00.json` VIA SCRIPT (mk_dhry00_json.py
gates copied; link_target FFT00, console_input bare `^Z`, capabilities grep-verified
BOTH ways, full notes/removals) → `--stages source,derivation` → lane B
`build/fc01/corp10` (+corp10-double if PASS) → docs § 15 + § 1 → gate
`build/gate-fft00.log` → explicit-path commit → corpus-close record (8 of 8).
Constraints unchanged: no `ocaml/`/harness byte; ledger ends C352; functional runs NOT
DR claims; FAILs never laundered; NEVER re-run the retry-DFS; third-party bytes
untracked; operator `handoff.config.json` untouched/unstaged; no push; renew only at
safe boundaries.

SUPERSEDED-BY-ABOVE (kept as written):

## DHRY-00 rev1 LANDED — steps 8-11 DONE: program 7 of 8 **PASS** on lane B (2026-11-03; docs § 14 + gate rc=0; the rev0 ASSERT FAIL is kept as written; FFT-00 = program 8/8 OWED)

Read `LEARNINGS.md` § "…DHRY-00 hop 19" FIRST — it carries every ACTUAL: the rev0 lane-B
FAIL (`build/fc01/corp9/`, order-only ASSERT miss at line 12, values all correct — a
GENERATOR bug in hop 18's table emission, FALSIFYING its "statement-for-statement" claim,
kept as written PROTOCOL #2), the rev1 pure-permutation pin fix (new pin sha `fc6695cd…`,
.REL geometry unchanged, expectation NEVER edited), the rev1 PASS
(`build/fc01/corp9b/`: 57-line complete-stream match; the 1368-B RUN capture BYTE-IDENTICAL
to the derived port raw sha `eebbed54…`; double-run byte-equal), and the JSON-via-script
gate (`mk_dhry00_json.py` re-runs sim-vs-derive byte-equality and aborts on mismatch). Gate
rc=0 in `build/gate-dhry00.log`: 1174/0, 181/181, 9/9, 133/0/0, 15/0/26/0, prose 5 clean.
**NEXT = FFT-00 (program 8 of 8, Rosetta PL/I)** — the EXACT 11-step hop-start contract is
the "EXACT NEXT" bullet of that LEARNINGS § (sha-verify + read whole listing; FIRST audit
every construct against the measured subset — modern-PL/I builtins are NOT assumed to exist
in PL/I-80 v1.4; simulator + INDEPENDENT naive-DFT cross-check; draft -> pin -> pin-vs-sim
ORDER audit (the hop-19 lesson) -> reference diff BEFORE JSON -> JSON via script ->
`--stages source,derivation` -> lane B `build/fc01/corp10` (+double) -> docs § 15 + § 1 ->
gate `build/gate-fft00.log` -> explicit-path commit; then the corpus-close record). Then
constraints unchanged: no `ocaml/`/harness byte; ledger ends C352; functional runs are NOT
DR claims; FAILs stay classified, never laundered; NEVER re-run the retry-DFS; third-party
bytes never tracked; operator `handoff.config.json` untouched/unstaged; no push; renew only
at safe boundaries.

SUPERSEDED-BY-ABOVE (kept as written):

Read `LEARNINGS.md` § "…DHRY-00 hop 18" FIRST — it carries every ACTUAL, the four
falsified-then-fixed drafting slips, the capability list and the exact steps 8-11 contract
(JSON via script -> --stages source,derivation -> lane B build/fc01/corp9 (+double) -> docs
§ 14 + § 1 -> gate build/gate-dhry00.log -> explicit-path commit), then FFT-00. Constraints
unchanged: no ocaml/harness byte; ledger ends C352; functional runs are NOT DR claims; FAILs
stay classified, never laundered; NEVER re-run the retry-DFS; third-party bytes never tracked;
operator handoff.config.json untouched/unstaged; no push; renew only at safe boundaries.

SUPERSEDED-BY-ABOVE (kept as written):
Read `LEARNINGS.md` § "…DHRY-00 hop 17 (partial)" FIRST. DONE this hop: (a) hop-16 docs committed
`fe414f8` (explicit paths only; operator `handoff.config.json` left unstaged; no push); (b) build
verified rc=0, compiler still `edce9e0e…`; (c) `dhry00_sim.check(7)` re-run GREEN (57 normalized
lines byte-equal vs model A, raw 1361 B, published should-be 20/20, ≤78-col frame law, exactly one
GET) and `w1.pli` re-compiled rc=0 4096 B code=1858 data=486 (its stale `w1.err` PUT-refusal text is
the pre-fix capture, NOT current state); (d) MEASURED (accepted, scratch, NOT DR claims): expression
call actuals, array-MEMBER call actuals, member actuals into a function, and a nested procedure
calling a sibling nested FUNCTION all COMPILE rc=0; FALSIFIED: `sx(v1 + k)` as a subscript REFUSES
([C159]) — hoist the index to a scalar first. CORRECTED IN PLACE (PROTOCOL #2): an earlier bullet
of this hop asserted a scratch `DHRY-00.draft.pli` + byte-identical `.REL` existed — MEASURED FALSE,
no draft/generator file exists; the lesson (never write an ACTUAL without running the command) is
recorded in that §. STEP 5 IS STILL OWED: write
`build/fc01-scratch/dhry00/mk_dhry00_pli.py` emitting the LF draft `dhry00/DHRY-00.draft.pli`
statement-for-statement from the `Port` class of `dhry00_sim.py` (read that class whole: init_state
→ header → run_loop → table plus the 14 nested subroutines; declares (intglob,int1g,int2g,int3g)
(boolg,char1g,char2g,enumg)(numruns,runidx,ci,z,tv,sb)(dvq,r2,r3,r6,r7) fixed bin(15) + a1(50)
a2(2500) sx(180) pcp(2) dsc(2) enm(2) inc(2); explicit zero-init loops; the 120 literal string-code
stores at sx bases 0/60/120/150 (4 per line); Pascal init pcp(1)=2 dsc(1)=0 enm(1)=2 inc(1)=40
a2(357)=10; ALL nested definitions AFTER `stop;` (LAYOUT LAW); EVERY formal copied to a local before
ANY subscript (TP00 LAW); every hoisted index scalar before subscripts like `sx(frm+k)`; should-be
constants as CHARACTER literals (`put list(<numeric literal>)` is a measured `my-gap` refusal);
then compile with `./ocaml/_build/default/bin/pli80c.exe IN OUT.REL` (POSITIONAL args) and iterate
until rc=0. THEN steps 6-11 exactly as hop 16 spelled them out below (CRLF+bare ^Z+≤71 cols → pin
`spec/functional/tests/DHRY-00.PLI` + compile the pin + `cmp` vs the draft .REL → `reference.py
:_Dhry00Port`/`dhry00()`+DERIVATIONS diffed BYTE-EQUAL vs `dhry00_sim.check(7)` BEFORE any JSON →
`DHRY-00.json` VIA SCRIPT (`link_target DHRY00`, `console_input "7\r^Z"`, capabilities
grep-verified ACCEPTS/SUPPORTED AND present in the .PLI, notes = every removal incl. timing/reals/
apostrophes/label-line split/numeric-literal PUT gap) → `--stages source,derivation` → lane B
`build/fc01/corp9` (+double if PASS, ACTUALS verbatim, FAIL stays classified never laundered) →
docs § 14 + § 1 → gate `build/gate-dhry00.log` → explicit-path commit), then FFT-00. Constraints
unchanged: no `ocaml/`/harness byte; functional runs are NOT DR claims (ledger ends C352); FAILs
stay classified, never laundered; NEVER re-run the retry-DFS; third-party bytes never tracked;
operator `handoff.config.json` untouched/unstaged; no push; renew only at safe boundaries.

SUPERSEDED-BY-ABOVE (kept as written):
## DHRY-00 hop 16 — SIMULATORS DONE (step 4); LF DRAFT (step 5) OWED (2026-11-03; NOTHING tracked authored; no lane/gate run)

FIRST ACTION **DONE** (hop 17, commit `fe414f8`): the hop-16 docs are committed (explicit paths
HANDOFF.md + PROGRESS.md + LEARNINGS.md only; `handoff.config.json` left unstaged; no push).
Successor starts at **step 5**. Read FIRST `LEARNINGS.md` § "…DHRY-00 hop 16" + § "…hop 17
checkpoint" (re-verification ACTUALS). The draft's statement-for-statement source is the `Port`
class of `build/fc01-scratch/dhry00/dhry00_sim.py` (read it whole; `check(7)` is the gate). Both models agree for N=7 (57 normalized lines,
raw 1361 B) and every invariant is green; `build/fc01-scratch/dhry00/dhry00_sim.py::check(7)` is the
regression gate for the draft, `dhry00_sim.out` is the stream reference `reference.py:dhry00` must be
diffed byte-equal against BEFORE any JSON; `w1.pli` (rc=0 4096 B) pre-witnesses every remaining shape.
NEW MEASURED GAP: `put list(<numeric literal>)` REFUSES (PUT form not in E2E-3a subset) -> the
should-be numeric constants print as CHARACTER literals; codegen error line numbers are unreliable.
EXACT NEXT (steps 5-11): (5) write `build/fc01-scratch/dhry00/mk_dhry00_pli.py` emitting the LF draft
`dhry00/DHRY-00.draft.pli` statement-for-statement from the port model: declares (intglob,int1g,int2g,
int3g)(boolg,char1g,char2g,enumg)(numruns,runidx,ci,z,tv,sb)(dvq,r2,r3,r6,r7) fixed bin(15) + arrays
a1(50) a2(2500) sx(180) pcp(2) dsc(2) enm(2) inc(2); explicit zero-init loops; 120 literal string-code
stores at sx bases 0/60/120/150 (4 per line); Pascal init pcp(1)=2 dsc(1)=0 enm(1)=2 inc(1)=40
a2(357)=10; header = put skip / banner / put skip / put skip / prompt / put skip / `get list(numruns)`
/ put skip / 'Execution starts,'+numruns+'runs through Dhrystone'/put skip; run loop `do runidx = 1 to
numruns;` mirroring Port.run_loop (proc5,proc4,int1g=2,int2g=3,cp30(120,90),enumg=1,tv=f2(60,90),
boolg=0+if tv=0 then boolg=1, do while int1g<int2g {int3g=5*int1g-int2g; call proc7(int1g,int2g);
int3g=r7; int1g=int1g+1}, proc8(int1g,int3g), proc1(1), do ci=65 to char2g {tv=f1(ci,67); if enumg=tv
then do; proc6(0); enumg=r6; cp30(150,90); int2g=runidx; intglob=runidx; end}, int2g=int2g*int1g,
divsub(int2g,int3g), int1g=dvq, tv=int2g-int3g, tv=7*tv, int2g=tv-int1g, proc2(int1g), int1g=r2);
final table = 'Execution ends' skip / 'Final values…' skip skip / rows per Port.table (label+value+skip
+ 'should be:' + literal + skip), Char rows via call putc, string rows = label line, put skip, call
putstr(base), put skip, should-be literal; then `put skip; put skip; stop;` and ALL nested definitions
AFTER the stop (LAYOUT LAW): proc5 proc4 proc7 proc8 proc1 proc3 proc6 proc2 f1 f2 f3 divsub cp30
putc putstr, each with its OWN locals, EVERY formal copied to a local before ANY subscript (TP00 LAW),
proc1 = r=pcp(p); dsc/enm/inc/pcp(r)=…(1); cp30(0,(r-1)*30); inc(p)=5; inc(r)=inc(p); pcp(r)=pcp(p);
call proc3(r); if dsc(r)=0 then do; inc(r)=6; proc6(enm(p)); enm(r)=r6; pcp(r)=pcp(1); proc7(inc(r),10);
inc(r)=r7; end. Compile the draft with `./ocaml/_build/default/bin/pli80c.exe IN OUT.REL` (POSITIONAL
args, no -ob); then (6) convert CRLF+bare ^Z, <=71 cols, <=8-letter link name DHRY00 -> pin
`spec/functional/tests/DHRY-00.PLI` + compile the PIN and `cmp` vs the draft .REL; (7) `reference.py
:_Dhry00Port`/`dhry00()` + DERIVATIONS, `derive('dhry00')` BYTE-EQUAL vs `dhry00_sim.check(7)` lines
BEFORE any JSON; (8) `DHRY-00.json` VIA SCRIPT (link_target DHRY00, console_input `7\r^Z`,
capabilities grep-verified ACCEPTS/SUPPORTED in spec/COVERAGE.tsv AND present in the .PLI — comment-
strip first; notes = every removal incl. timing/reals/apostrophes/label-line split/numeric-literal PUT
gap); `--stages source,derivation`; (9) lane B `python3 tools/functional_runner.py --tests DHRY-00
--evidence build/fc01/corp9 --json-out build/fc01/corp9/records.json` (+ --double-run corp9-double if
PASS), ACTUALS verbatim, FAIL stays classified never laundered; (10) docs/functional-results.md § 14 +
§ 1 row; (11) `python3 tools/e2e_gate.py` -> build/gate-dhry00.log; explicit-path commit (NEVER
handoff.config.json; no push). Then FFT-00 (build/functional/fc01-sources/pli/FFT-reference.pli,
evidence corp10, docs § 15). Constraints unchanged: no ocaml/harness byte; functional runs are NOT DR
claims; NEVER re-run the retry-DFS; third-party bytes never tracked; renew only at safe boundaries.

SUPERSEDED-BY-ABOVE (kept as written):
## DHRY-00 implementation hop LANDED (2026-11-03, continuation chain hop 15; shapes pre-compiled + lane-B RUN probes DHP00/TP00 MEASURED; NOTHING tracked authored; simulator OWED)

Read FIRST `LEARNINGS.md` § "…DHRY-00 implementation hop (continuation chain hop 15)" — it carries
the ACTUALS and the full draft contract. Measured (my compiler edce9e0e, ignored scratch
`build/fc01-scratch/dhry00/`, NOT DR claims, ledger ends C352): (1) ACCEPTED — sibling nested
procedure/function calls WORK ONLY with the LIFE-00 layout (ALL main-body statements first,
ALL nested definitions after `stop;`): procedures-before-main REFUSE with `call-site queue
mismatch` (bind queue = root sites first; v4b/v4c refused, v4d rc=0). (2) FALSIFIED — `do while
intloc <= 2` REFUSED (only `<` forms in DO WHILE); `if d < 0` REFUSED (divsub uses
`if rr < yy`). (3) ACCEPTED lane-B RUN (DHP00 COM 13568 B, RUN done 109 B; TP00 RUN done 53 B
verbatim `\r\n        0         0         7         0         7\r\n`) — nested writes to outer
scalars/arrays, 5256 B DHRY-size AUTO data, flat goto loops, code->char ladder PUT, return(rv)
functions ALL RUN-CORRECT, BUT **FALSIFIED silent store-LOSS: a nested-procedure array store
whose subscript is the FORMAL ITSELF writes nowhere — copy formal->local FIRST (TP00 law);
literal and local-variable subscripts correct. (4) MEASURED the proposed 79-col PLILIB wrap
FIRES at exactly 79 columns — the port keeps every line ≤ 78 so no wrap model is needed.
EXACT NEXT (steps 4-11 of the standing contract, in `build/fc01-scratch/dhry00/`):
(4) write `dhry00_pascal_sim.py` (line-for-line Pascal semantics) and `dhry00_sim.py` (port
byte model: sep blank when line open, `%9d`, echo `%d\r\r\n`, exit appends one `\r\n` [C352],
collapse-spaces-v1) — cross-check the two on the FINAL state for N=7 AND against the published
should-be column (IntGlob 5, Bool TRUE, A, B, a1(8)=7, a2(8,7)=17, slot1 0/2/17/SOME-STRING,
slot2 0/1/18/SOME-STRING, 5/13/7, EnumGlob 1, sg1=1ST, sg2=2ND); (5) LF draft
`build/fc01-scratch/dhry00/DHRY-00.draft.pli` per the LEARNINGS draft contract (N=7 via
`get list`; explicit zero-init EVERYTHING; every formal copied to a local before subscripting;
reusable `c30` copy proc; flat label loops for `<=`-whiles; v12-compiled nested if/goto forms);
scratch-compile with `../../../ocaml/_build/default/bin/pli80c.exe`;
(6) convert CRLF+bare ^Z, <=71 cols, <=8-letter link name, zero tabs/high bytes, no in-literal
apostrophes -> pin `spec/functional/tests/DHRY-00.PLI`, compile the PIN and `cmp` vs draft .REL;
(7) `reference.py:_Dhry00Port`/`dhry00()`+DERIVATIONS, diff `derive('dhry00')` vs sim norm()
BYTE-EQUAL BEFORE any JSON; (8) `DHRY-00.json` VIA SCRIPT (link_target DHRY00,
console_input `7\r^Z`, capabilities grep-verified ACCEPTS/SUPPORTED in `spec/COVERAGE.tsv` AND
present in the .PLI, notes = every removal incl. timing/reals/apostrophes/79-col law);
`--stages source,derivation`; (9) lane B `python3 tools/functional_runner.py --tests DHRY-00
--evidence build/fc01/corp9 --json-out build/fc01/corp9/records.json` (+`--double-run` into
corp9-double if PASS), ACTUALS verbatim, FAIL stays classified never laundered; (10)
`docs/functional-results.md` § 14 + § 1 row; (11) `python3 tools/e2e_gate.py` ->
`build/gate-dhry00.log`; explicit-path commit (NEVER `handoff.config.json`; no push). Then
FFT-00 (evidence corp10, docs § 15). Constraints: no `ocaml/`/harness byte; ledger ends C352;
functional runs are NOT DR claims; NEVER re-run the retry-DFS; third-party bytes never tracked;
renew at the safe boundary AFTER the commit (renewal 2/12 used by this session; gate currently
reports the checkpoint needs refresh+attest — run `/handoff` then `/handoff ready`).

SUPERSEDED-BY-ABOVE (kept as written): LIFE-00 **LANDED — lane-B PASS** (2026-11-03, continuation chain hop 13; this session's operator
ask — "an actual Lane-B verdict, not another design step" — is DELIVERED). Read FIRST
`LEARNINGS.md` § "…LIFE-00 completion hop LANDED". Measured: `spec/functional/tests/LIFE-00.PLI`
PINNED sha `fa4ab8cf7ef4715861b9c8b2c70cfe4ce3c900b7d13289064a5c70ca1d2256f9` (4630 B, 150 lines,
widest 63, CRLF + bare ^Z, apostrophe-free; draft-compile .REL byte-identical); reference
`derive('life00')` BYTE-EQUAL to the independent simulator (91 lines, raw 4722 B) BEFORE the
JSON; `LIFE-00.json` generated VIA SCRIPT (10 double-verified capabilities; pure-PUT bare `^Z`);
lane B `build/fc01/corp8/` **PASS on the FIRST run** — COMPILE rc=0 3200 B (code=1663 data=38
items=1748), LINK `LIFE00.COM` 9856 B `parse_undefined=[]`, RUN **4722 console bytes** = exactly
the predicted raw, ASSERT complete-stream match 91 lines, `verdicts: PASS=1 FAIL=0 BLOCKED=0
UNKNOWN=0`; double-run `build/fc01/corp8-double/` byte-equal (sha `2658a5cd…`); full gate rc=0
(1174/0, 181/181, 9/9, 133/0/0, 15/0/26/0, prose 5) in `build/gate-life00.log`; docs § 13 + § 1
row. First lane-B RUN witnesses: nested `cellprint` call inside the doubly-nested DO, 9-wide
numeric corpus headers, padded flat a(448) with in-pass 2/3 marks, centre-inclusive Conway.

## DHRY-00 hop start LANDED (2026-11-03, continuation chain hop 14; steps 1-3 partial: source extracted READ-ONLY + read in full + 8 port shapes MEASURED; design PROPOSED, NOT adopted; NOTHING tracked authored; no lane run, no gate run)

Read FIRST `LEARNINGS.md` § "…DHRY-00 hop start" — it carries the ACTUALS: shar decoded by a
read-only Python here-doc reader into `build/fc01-scratch/dhry00/` (6 members, shas recorded;
`dhry.p-1` = statistics only, `dhry.p-2` = the program; the `.SHAR` was NEVER executed;
`sha256sum -c SHA256SUMS` rc=0 10/10), the full scope facts of the Pascal source (11 subroutines,
variant records behind pointers, `ord`-based enum printing, 30-char packed strings indexed per
character AND compared whole, 50x50 array, `with`/`case`/`repeat…until`, terminal
`readln(NumberOfRuns)`, `clock` timing + reals, apostrophes in literals, the canonical
should-be result table, and the ONE variable-divisor `div`), and the 8 measured shapes:
STATIC ARRAY REFUSED (`codegen: [TBD] STATIC array is not independently characterized [C159/AB5]`)
⇒ all array state must be outer AUTO; nested procedure reading/writing an outer AUTO ARRAY element
COMPILES (lane-B RUN unwitnessed); `do while a < b` ACCEPTED; `do until` REFUSED in both spellings
(`Parser: expected =`) ⇒ `repeat…until` becomes a label + `if flag = 0 then goto top`; a call
inside a condition REFUSED ⇒ hoist to a scalar; `do i = 1 to n` with variable bound ACCEPTED;
`get list(n)`, multi-item `put skip list('A=', a, 'B=', b)`, parenthesized-expression stores and
computed subscripts ACCEPTED. PROPOSED design (re-validate, never adopt silently): keep the 11
subroutines as sibling nested procedures over outer AUTO state; records = 2 slots in parallel
arrays with 0-based enum codes and a flat 60-cell string-code array; `var` params → callee writes a
result cell, caller assigns back (PROC.CALL_COPYIN: no by-reference convention); `div` →
subtraction loop; `<>` → branch swap with `=`; AND → nested if; `case` → if-ladder; `with` → index
temp; chars/bools/enum → integer codes; strings → 30 positional tokens via a `putchar` ladder;
apostrophes dropped (`1ST`/`2ND`, declared); `readln` → numeric `get list`; timing lines + the
too-small branch DROPPED and documented.
EXACT NEXT = the numbered contract below (steps 1-2 are DONE; start at step 2's simulator, then 3
pre-compile the remaining risky shapes — whole-record copy loop, 17-branch code→char ladder, the
outer-auto-array lane-B shape), evidence `build/fc01/corp9`, docs § 14. Per the operator directive,
if a GENUINE compiler limitation blocks execution RECORD the failure promptly; a FAIL stays
classified, never laundered, the expectation never edited to chase a PASS.

SUPERSEDED-BY-ABOVE (kept as written): EXACT NEXT = program 7 **DHRY-00** (Dhrystone, Pascal) per
the standing corpus procedure (PROGRESS § Current phase table + the LIFE/TICT/AMAZ precedents):
(1) `sha256sum -c
SHA256SUMS` rc=0 in `build/functional/fc01-sources/`; **NEVER execute
`pascal/dhry-pascal.shar`** — it is a self-extracting shell archive and execution is forbidden by
the operator table; extract the Pascal payload by READ-ONLY means only (e.g. `unshar`/`sharxf`
if available, else manually decode the `echo`/`sed` here-doc payload; verify the extracted bytes
against any CRC the shar records if cheap) into ignored scratch
`build/fc01-scratch/dhry00/`; read the WHOLE listing; record a hop-start analysis in
`LEARNINGS.md` (scope facts — e.g. the execution-count `NumberOfRunsWithNoMultiplication`/timer
loop must become a DECLARED bounded count, the Pascal `record`/`procedure` parameter semantics vs
the measured PL/I subset, any input; the corpus laws: literal divisors only, no apostrophes,
≤ 71 cols, single-item `put list`, positive-literal + scalar `= 0` compares, member->scalar, no
`|`/`&`-composed conditions, goto never crosses an ACTIVE DO, [C352] framing); (2) independent
scratch simulator `build/fc01-scratch/dhry00_sim.py` on the measured byte model (skip=\r\n,
separator blank when line open, 9-wide right-justified fixed bin(15) numerics — NEVER
`%10d`+join — exit appends one \r\n, collapse-spaces-v1) with independent cross-checks
(the Dhrystone result values are deterministic: derive them twice, e.g. a direct Python
line-for-line model vs the port model, like LIFE's unbounded Conway check); (3) pre-compile risky
shapes in ignored scratch BEFORE drafting; (4) LF draft mirroring the simulator
statement-for-statement → scratch compile → CRLF + bare ^Z + ≤ 71 cols + apostrophe-free
`spec/functional/tests/DHRY-00.PLI`, pin sha256, compile the PINNED file and `cmp` the .REL;
(5) `reference.py:_Dhry00Port`/`dhry00()` + `DERIVATIONS`, diff `derive('dhry00')` vs sim
`norm()` + raw bytes BEFORE any JSON; (6) `DHRY-00.json` VIA SCRIPT from derive (link target
DHRY00, `console_input "^Z"` unless the program reads, capabilities grep-verified in
`spec/COVERAGE.tsv` (ACCEPTS/SUPPORTED) AND present in the .PLI — strip comments before
absence checks, the LIFE generator bug; full notes incl. every removal/substitution); (7)
`python3 tools/functional_runner.py --stages source,derivation --tests DHRY-00`; (8) lane B
`python3 tools/functional_runner.py --tests DHRY-00 --evidence build/fc01/corp9 --json-out
build/fc01/corp9/records.json` (+ `--double-run` into corp9-double if PASS), ACTUALS verbatim,
a FAIL stays classified `my-gap`/`dr-refuses`/`unmeasured`, NEVER laundered, the expectation
never edited to chase a PASS; per the operator directive, if a GENUINE compiler limitation blocks
execution, RECORD the failure promptly rather than spending another session designing around it;
(9) `docs/functional-results.md` § 14 + § 1 row; (10) `python3 tools/e2e_gate.py` compile tier →
`build/gate-dhry00.log`; (11) explicit-path commit (NEVER `handoff.config.json`; no push). Then
FFT-00 (`pli/FFT-reference.pli`, Rosetta PL/I — the only non-BASIC/Pascal source, closer to
native PL/I; evidence corp10, docs § 15); HAMM-00 rev2 subtraction-loop stays PROPOSED.
Constraints: no `ocaml/`/harness byte changes; ledger ends C352; functional runs are NOT DR
claims; NEVER re-run the retry-DFS search; third-party bytes never tracked; operator
`handoff.config.json` stays untouched/unstaged; no push; renewal cap 12/12 stands — this session
continues ONLY because enforcement is disabled and the operator said "implement now", so
RE-FINALIZE (`handoff_finalize`) at every safe boundary and a fresh successor still needs an
operator reset.

SUPERSEDED-BY-ABOVE (kept as written):

LIFE-00 STEP 2 **DONE**, DRAFT (STEP 3) OWED (2026-11-03, hop 12 resumed in-session after the
finalize — enforcement disabled, renewal still capped 12/12, so RE-FINALIZE at every safe
boundary). Read FIRST `LEARNINGS.md` § "…LIFE-00 hop 12 step 2b LANDED" (it supersedes the §
"…LIFE-00 hop 12" above it) and the corrected § "…LIFE-00 implementation hop (continuation chain
hop 11)". MEASURED, ignored scratch only, nothing tracked authored yet, no lane run, no gate run,
no `ocaml/`/harness byte changed: `build/fc01-scratch/life00_sim.py` is FINAL and every assertion
PASSes — the hop-11 neighbour model was FALSIFIED (upstream 530/540 count the 3x3 INCLUDING the
centre, so the eight-temp sum with the `= 3`/`= 4` ladder killed every cell with exactly two live
neighbours; the fix is `t2 = a(n); if t2 = 1 then s = s + 1;` before that ladder); the four
declared patterns are shifted right 2 columns so the window-margin invariant holds (glider
(2,4),(3,5),(4,3),(4,4),(4,5); beacon (2,12),(2,13),(3,12),(4,15),(5,14),(5,15); block
(10,27),(10,28),(11,27),(11,28); blinker (8,17),(9,17),(10,17)); populations **18,20,18,20,18,20**
(declared initial cs **18**); port grids EQUAL an independent unbounded Conway model on all 6
printed generations; stream ACTUALS raw **4722 B** (4720 pre-exit + one exit CRLF [C352]), **91
normalized lines** = banner 2 + 3 blanks + 6 x (pad + header + 12 rows) + bottom pad + the
exit-CRLF blank; headers `GENERATION <g> POPULATION <cs>`; each body row is 30 `.`/`*` positional
tokens (dead glyph `.` DECIDED, rationale in LEARNINGS). The 18 flat seed indices `n = x*32+y+1`
are **69, 77, 78, 102, 109, 132, 133, 134, 144, 175, 176, 274, 306, 338, 348, 349, 380, 381**.
Machine-readable snapshot: `build/fc01-scratch/life00_sim.{json,out}`.
EXACT NEXT = STEP 3 then 4-10: (3) LF draft mirroring the simulator STATEMENT-FOR-STATEMENT —
`life00: procedure options(main);`, `declare a(448) fixed bin(15);`, the REQUIRED explicit
zero-init `do i = 1 to 448; a(i) = 0; end;` (uninitialized static DATA contents are UNMEASURED on
lane B), the 18 `a(k) = 1;` seeds above, the initial scan loop for cs, banner `put list('LIFE');
put skip;` + `put list('CREATIVE COMPUTING  MORRISTOWN, NEW JERSEY'); put skip;` x3 `put skip;`,
then `do g = 0 to 5;` with one `put skip;` pad, the four single-item header PUTs + `put skip;`,
the print pass (nested `do x = 1 to 12;` / `do y = 1 to 30;`, `n = x * 32 + 1;` then `n = n + 1;`,
member->scalar `t1 = a(n);`, `v = 0; if t1 = 1 then v = 1; if t1 = 3 then v = 1;`, `call
cellprint(v);`, finalize `if t1 = 2 then a(n) = 0; if t1 = 3 then a(n) = 1;`, `put skip;` closing
each row), the evolution pass (eight `nk = n +/- ...` temps + `t2 = a(nk); if t2 = 1 then s = s +
1; if t2 = 2 then s = s + 1;` ladders PLUS the centre `t2 = a(n); if t2 = 1 then s = s + 1;`, then
`s = 3` birth -> `a(n) = 3; cs = cs + 1;` and the alive `= 3`/`= 4` survive / die-to-2 ladder),
`put skip;` bottom pad, `stop;`, and the nested `cellprint: procedure (q)` owning its own
`character(1) varying` (`if q = 1 then ch = '*'; if q = 0 then ch = '.'; put list(ch);`) — compile
it in ignored scratch FIRST (`build/fc01-scratch/life00*.pli`, MY compiler, NOT a DR claim; a
refusal stays classified, never laundered), then convert to CRLF + bare ^Z + <=71 cols +
apostrophe-free and PIN `spec/functional/tests/LIFE-00.PLI` with its sha256; (4) `reference.py
:_Life00Port` + `life00()` + `DERIVATIONS` (sep blank + `%9d` numeric, NEVER `_Hamm00Port`'s
`%10d`+join), diff `derive('life00')` vs sim `norm()` BEFORE any JSON; (5) `LIFE-00.json` VIA
SCRIPT (link_target LIFE00, console_input bare ^Z, capabilities grep-verified in
`spec/COVERAGE.tsv` AND present in the .PLI, full notes incl. the centre-count correction, the
2-column shift, the dynamic-box/clamp/INVALID! removal, dead glyph `.`); (6) `python3
tools/functional_runner.py --stages source,derivation --tests LIFE-00`; (7) lane B `--evidence
build/fc01/corp8 --json-out build/fc01/corp8/records.json` (+corp8-double if PASS), ACTUALS
verbatim, a FAIL stays classified `my-gap`/`dr-refuses`/`unmeasured` and is NEVER laundered; (8)
`docs/functional-results.md` § 13 + § 1 row; (9) `python3 tools/e2e_gate.py` compile tier ->
`build/gate-life00.log`; (10) explicit-path commit (NEVER `handoff.config.json`; no push). Reusable
scratch lane-B runner: `build/fc01-scratch/run_bigarray_probe.py`. Then DHRY-00 (NEVER execute
the `.SHAR`) and FFT-00; HAMM-00 rev2 stays PROPOSED. Constraints: ledger ends C352; NEVER re-run
the retry-DFS search; third-party bytes never tracked; operator `handoff.config.json`
untouched/unstaged; no push; RE-FINALIZE the handoff at each safe boundary (cap 12/12).

SUPERSEDED-BY-ABOVE (kept as written):

LIFE-00 IMPLEMENTATION STEPS 2-10 (2026-11-03, continuation chain hop 11 end; step 1 shapes
pre-compile **PASS** and the step-2 simulator is written; NOTHING tracked authored yet). Read
FIRST `LEARNINGS.md` § "…LIFE-00 implementation hop (continuation chain hop 11)" — it carries the
compile ACTUALS (`build/fc01-scratch/s10a.pli` -> s10a.REL 2944 B code=1504 DATA declared 985,
rc=0, MY compiler edce9e0e, not DR claims), the simulator ACTUALS
(`build/fc01-scratch/life00_sim.py`: raw 4722 B, 91 normalized lines, pops 18,12,8,9,7,6), the
THREE falsifications of the hop-10 design (scalar `= 0` IS lane-B run-witnessed PASSing in
AMAZ-00/HANG-00/WKDAY-00; the hop-10 "beacon" coordinates die out — the real beacon is
(2,10),(2,11),(3,10),(4,13),(5,12),(5,13) with a 6->8->6 flicker; declared cs is 18, not 15), the
re-measured numeric field law (separator blank + 9-column right-justified for fixed bin(15) — never
copy `_Hamm00Port.put`'s `%10d`+join), the REQUIRED explicit zero-init loop (`do i = 1 to 448;
a(i) = 0; end;` — uninitialized static DATA contents are UNMEASURED on lane B) and the OPEN
PROPOSED dead-cell-glyph decision (' ' faithful but collapse-spaces-v1 erases the columns; '.'
gives 30 positional tokens per row). EXACT STEPS: (2) settle beacon + glyph in the simulator,
re-run, assert the window-margin and per-generation header==live invariants, record ACTUALS;
(3) LF draft mirroring the simulator statement-for-statement -> CRLF + bare ^Z + <=71 cols +
apostrophe-free `spec/functional/tests/LIFE-00.PLI`, pin sha256; (4) `reference.py:_Life00Port` +
`life00()` + `DERIVATIONS`, diff `derive('life00')` vs sim `norm()` BEFORE any JSON; (5) generate
`LIFE-00.json` VIA SCRIPT (link_target LIFE00, console_input bare ^Z, capabilities grep-verified in
`spec/COVERAGE.tsv` AND present in the .PLI, notes = full removal/substitution list); (6) `python3
tools/functional_runner.py --stages source,derivation --tests LIFE-00`; (7) lane B `--evidence
build/fc01/corp8 --json-out build/fc01/corp8/records.json` (+corp8-double if PASS), ACTUALS
verbatim, a FAIL stays classified `my-gap`/`dr-refuses`/`unmeasured` and is NEVER laundered;
(8) `docs/functional-results.md` § 13 + § 1 row; (9) `python3 tools/e2e_gate.py` compile tier ->
`build/gate-life00.log`; (10) explicit-path commit (NEVER `handoff.config.json`; no push). Reusable
scratch lane-B runner: `build/fc01-scratch/run_bigarray_probe.py`. Then DHRY-00 (NEVER execute the
`.SHAR`) and FFT-00; HAMM-00 rev2 stays PROPOSED. Constraints: no ocaml/harness byte changed;
ledger ends C352; NEVER re-run the retry-DFS search; third-party bytes never tracked; operator
`handoff.config.json` untouched/unstaged; no push; renewal 11/12 used — ONE renewal remains.

SUPERSEDED-BY-ABOVE (kept as written):

LIFE-00 IMPLEMENTATION STEPS 1-10 (2026-11-03, continuation chain hop 10 end; big-array
lane-B probe **PASSed** and the LIFE-00 design is **ADOPTED**; read FIRST `LEARNINGS.md`
§ "…big-array lane-B PROBE PASS + storage FALSIFICATION" — it carries the probe ACTUALS
verbatim, the FALSIFIED hop-9 runtime-allocation claim (compiler stderr `DATA=` header is
NOT the declared section size; relstats LINK-DEF-DATA-SIZE on s6j/s6l = 4004/3374 = arrays
ARE static DATA; 6724 B survives DR LINK-80+PLILIB, BIGA.COM 15104 B RUN done 227 console
bytes all checksums correct), the measured fixed bin(15) 9-column right-justified PUT LIST
field, and the full adopted design: flat padded grid a(448) interior 12x30 index
n = x*32+y+1, single-array 2-pass (2=dead-mark, 3=birth-mark, print finalizes), bounded
`do g = 1 to 6;`, declared glider+beacon+block+blinker cs = 15, INPUT phase DROPPED
(documented), nested cellprint varying-char printer (HANG show law), neighbour sums via
[ C159 ]-legal temps (k1 = n-1; k2 = n-32; k3 = n+32; k2m = k2-1 etc.) + separate
`= 1`/`= 2` ladders, death/birth positive-literal ladders (equality-to-0 stays PROPOSED-
unwitnessed — avoid or pre-compile), header line put list('GENERATION'); put list(g);
put list('POPULATION'); put list(cs); put skip; fixed ONE blank pad per generation
(225/295 dynamic padding dropped, documented), exit blank [ C352 ]. EXACT STEPS: (1) pre-
compile risky shapes in ignored scratch build/fc01-scratch/s10*.pli (nested DO calling
cellprint, a(k2+1) var+1 subscript, if s = 0 equality); (2) simulator life00_sim.py on the
measured byte model (skip=\r\n, separator blank when line open, numeric field 9-wide right-
justified, exit \r\n, collapse-spaces-v1); (3) LF draft -> CRLF+bare^Z+<=71+apostrophe-free
`spec/functional/tests/LIFE-00.PLI` pin sha; (4) `reference.py:_Life00Port`/`life00()` +
DERIVATIONS diffed vs sim norm() BEFORE the JSON; (5) `LIFE-00.json` VIA SCRIPT (link_target
LIFE00, console_input bare ^Z, capabilities grep-verified in spec/COVERAGE.tsv AND present
in the .PLI, notes = full adaptation/removal list incl. the storage falsification); (6)
`--stages source,derivation`; (7) lane B `--evidence build/fc01/corp8 --json-out
build/fc01/corp8/records.json` (+corp8-double if PASS), ACTUALS verbatim, FAIL stays
classified never laundered; (8) docs/functional-results.md § 13 + § 1 row; (9)
`python3 tools/e2e_gate.py` compile tier -> build/gate-life00.log; (10) explicit-path commit
(NEVER `handoff.config.json`; no push). Probe machinery REUSABLE: `build/fc01-scratch/
run_bigarray_probe.py` copies the lane-B law for ad-hoc scratch runs. Then DHRY-00 (NEVER
execute the `.SHAR`) and FFT-00; HAMM-00 rev2 stays PROPOSED. Constraints: no ocaml/harness
byte changes; ledger ends C352; NEVER re-run the retry-DFS search; third-party bytes never
tracked; renewals 10/12 used — renew only at safe boundaries.

SUPERSEDED-BY-ABOVE (kept as written):

LIFE-00 HOP START MEASURED — BIG-ARRAY LANE-B PROBE FIRST, THEN THE DESIGN RECORD
(2026-11-03, continuation chain hop 9 end; TICT-00 LANDED and committed `dfbf07c`; build rc=0
verified at session start, compiler `edce9e0e…`). Read FIRST `LEARNINGS.md` § "…LIFE-00 hop
start" — it carries the measured port shapes (`do i = x-1 to x+1` REFUSED
`DO FROM form unproven`; array member in a condition REFUSED `condition form not in E2E-3b
subset`; `or`-composed member tests FAIL TO PARSE; literal-divisor DIV and CHARACTER VARYING
literal compares ACCEPT; `declare a(1681)/a(2000) fixed bin(15)` COMPILE but the array does NOT
appear in the .REL DATA segment (data=6/12 bytes = scalars only) ⇒ runtime allocation, a
~3360-byte local array under DR LINK-80 + PLILIB is **UNWITNESSED on lane B**), the scope
falsification (upstream LIFE NEVER TERMINATES — line 640 `GOTO 210`, line 650 `END` dead, and
lines 225/295 pad blank rows every generation) and the PROPOSED adaptation (numeric `GET LIST`
row encoding with a leading-1 width sentinel, one flat grid array with a declared stride,
per-cell single-item `put list` printer, TAB banner dropped, a bounded generation count, the
positive-literal compare/shift idioms).
EXACT NEXT: (1) **big-array lane-B RUN probe** in ignored scratch — a program with
`declare a(1681) fixed bin(15);` that stores and reads several cells and prints a checksum,
compiled with my compiler, linked by DR LINK-80 + PLILIB and run under cpmsim (the lane-B
harness or `oracle/linkrun.py` pattern), because if a 3360-byte local array does not survive
the substrate the port needs a smaller declared grid or a different storage shape; record the
ACTUAL verbatim, a FAIL stays classified `my-gap`/`dr-refuses`/`unmeasured` and is NOT a DR
claim (no ledger entry without a pre-registered oracle round); (2) then the full LIFE-00
design record + simulator + the 11-step corpus procedure in the section below (draft → pin
`spec/functional/tests/LIFE-00.PLI` → `reference.py:_Life00Port`/`life00()` diffed vs the
simulator BEFORE the JSON → `LIFE-00.json` VIA SCRIPT → `--stages source,derivation` → lane B
`build/fc01/corp8` (+double if PASS) → docs § 13 + § 1 row → compile-tier gate
`build/gate-life00.log` → explicit-path commit). Then DHRY-00 (**NEVER execute the `.SHAR`**)
and FFT-00; HAMM-00 rev2 stays PROPOSED. Constraints unchanged: no ocaml/harness changes;
ledger ends C352; NEVER re-run the retry-DFS search; third-party bytes never tracked; explicit-
path commits only, NEVER `handoff.config.json`; no push; renew only at safe boundaries.

SUPERSEDED-BY-ABOVE (kept as written): TICT-00 **PASS** LANDED (steps 7-10) — PROGRAM 5 OF 8 COMPLETE; NEXT = LIFE-00 HOP START
(2026-11-03, continuation chain hop 9 end; HEAD `c837d7f` at execution, build rc=0 verified at
session start, compiler `edce9e0e…`). Read FIRST `LEARNINGS.md` § "…TICT-00 completion hop 9".
Measured: lane B `build/fc01/corp7/` executed **PASS on the FIRST run** — SOURCE/DERIVATION/
COMPILE (rc=0, 8704 B, code=4030 data=36, items=4593)/LINK (`TICT00.COM 12160 B`,
`parse_undefined=[]`)/RUN (`done`, **1468 console bytes = exactly the simulator's predicted raw**)
/ASSERT (complete-stream match, 120 lines); `verdicts: PASS=1 FAIL=0 BLOCKED=0 UNKNOWN=0`;
double-run `build/fc01/corp7-double/` byte-equal (`cmp` rc=0, console sha256 `0f7f5819…`).
FIRST lane-B RUN witnesses: the 121-label flat goto machine, variable-subscript stores, `call`
from inside the machine, and the occupied retry loop-back with the numeric GET echo re-asked
(`WHERE DO YOU MOVE 1\r\r\nTHAT SQUARE IS OCCUPIED.\r\n\r\n\r\n`). docs § 12 + § 1 row written
from the records; full compile-tier gate rc=0 (1174/0, 181/181, 9/9, 133/0/0, census 15/0/26/0,
prose 5 clean) in `build/gate-tict00.log`. Corpus: 5 of 8 landed (WKDAY rev3 PASS, HAMM rev1
`my-gap` FAIL recorded, HANG rev1 PASS, AMAZ rev1 PASS, TICT rev1 PASS).
EXACT NEXT = program 6 **LIFE-00** (Game of Life, BASIC `build/functional/fc01-sources/basic/LIFE.bas`)
per the standing corpus procedure: (1) `sha256sum -c SHA256SUMS` in the sources dir, read the WHOLE
listing, record a hop-start analysis in `LEARNINGS.md` (scope falsifications, upstream behaviour,
unsupported features to DOCUMENT rather than silently remove, the port-shape decisions under the
measured corpus laws: literal divisors only, no apostrophes, ≤71 cols, single-item `put list`,
numeric GET + echo, [C352] framing, flat goto machine where nested constructs are unwitnessed);
(2) independent scratch simulator + a finite deterministic game script (BASIC LIFE uses `RND` and/or
input and a `PRINT`-per-generation grid with carriage-control spacing — decide the adaptation and
record it); (3) pre-compile risky shapes in ignored scratch; (4) LF draft -> CRLF + bare ^Z + <=71 +
apostrophe-free `spec/functional/tests/LIFE-00.PLI`, pin sha; (5) `reference.py:_Life00Port`/
`life00()` + `DERIVATIONS`, diff `derive` vs the simulator norm() BEFORE the JSON; (6) generate
`LIFE-00.json` VIA SCRIPT from derive (link target LIFE00, capabilities grep-verified against
`spec/COVERAGE.tsv` AND the pinned .PLI, full notes); (7) `--stages source,derivation`; (8) lane B
`--evidence build/fc01/corp8 --json-out build/fc01/corp8/records.json` (+corp8-double if PASS),
ACTUALS verbatim, a FAIL stays classified `my-gap`/`dr-refuses`/`unmeasured`, never laundered, the
expectation never edited to chase a PASS; (9) `docs/functional-results.md` § 13 + § 1 row; (10)
`python3 tools/e2e_gate.py` compile tier -> `build/gate-life00.log`; (11) explicit-path commit
(NEVER `handoff.config.json`; no push). Then DHRY-00 (**NEVER execute the `.SHAR`** — extract by
read-only means) and FFT-00; HAMM-00 rev2 stays PROPOSED. Constraints unchanged: no ocaml/harness
changes; ledger ends C352; NEVER re-run the retry-DFS search; third-party bytes never tracked;
renew only at safe boundaries (renewal 9/12 used — successor = LIFE-00 hop).

SUPERSEDED-BY-ABOVE (kept as written): TICT-00 REFERENCE + JSON LANDED (steps 4-6) — LANE B / DOCS / GATE / COMMIT OWED
(2026-11-03, continuation chain hop 8 end; HEAD `77c89c2` at session start, build rc=0
verified, compiler `edce9e0e…`). Read FIRST `LEARNINGS.md` § "…TICT-00 implementation
hop 8". Measured: `reference.py:_Tict00Port`/`tict00()`/`_tict00_finalize`/
`_tict00_trunc_div` + DERIVATIONS registered — the 121-label dispatch was GENERATED
MECHANICALLY from the pinned .PLI (`build/fc01-scratch/mk_tict00_mirror.py`) and
hand-checked, so unreached labels are mirrored too; `derive('tict00')` is BYTE-EQUAL to
the independent simulator norm() on all 120 lines (raw 1468 B) — diffed BEFORE the JSON;
all derivation invariants green (draw, 8 gets, board, THREE occupied 86/91/96, 15
unreached labels, l1112/l1137 entered but never branching);
`spec/functional/tests/TICT-00.json` GENERATED VIA SCRIPT (link_target TICT00, sha
f9320f5a…, console_input `2\r2\r9\r7\r1\r10\r1\r4\r^Z`, collapse-spaces-v1, 12
double-verified capabilities, notes (1)-(15)); `--stages source,derivation` printed the
designed UNKNOWN [COMPILE: stage ceiling] with no SOURCE/DERIVATION FAIL (evidence
build/functional/20261103T112342Z). FALSIFIED: my first echo-line assertion omitted the
trailing `\r` (the committed HAMM convention) — fixed to the measured form.
EXACT NEXT = hop-8 § steps 7-10: (7) lane B `--evidence build/fc01/corp7 --json-out
build/fc01/corp7/records.json` (+corp7-double if PASS), ACTUALS verbatim, a FAIL stays
classified never laundered and the expectation is never edited to chase a PASS; (8)
docs/functional-results.md § 12 + § 1 row; (9) `python3 tools/e2e_gate.py` compile tier
-> build/gate-tict00.log; (10) explicit-path commit (NEVER handoff.config.json; no
push). Then LIFE-00, DHRY-00 (never execute the .SHAR), FFT-00; HAMM-00 rev2 stays
PROPOSED. Constraints: no ocaml/harness changes; ledger ends C352; NEVER re-run the
retry-DFS search; renew only at safe boundaries (renewal 8/12 used — successor = hop 9).

SUPERSEDED-BY-ABOVE (kept as written): TICT-00 PIN LANDED (step 3) — REFERENCE/JSON/LANE/DOCS/GATE OWED (2026-11-03, continuation
chain hop 7 end; HEAD `586ee3c` at session start, build rc=0 verified, compiler `edce9e0e…`).
Read FIRST `LEARNINGS.md` § "…TICT-00 implementation hop 7" — it carries this hop's measured
record: `spec/functional/tests/TICT-00.PLI` is PINNED (sha
`f9320f5a65d98fc3cc2a4aa4688444aab54cba25814ddbfa17ee5b2bd26c04e7`, 9300 B, 499 lines, CRLF +
bare ^Z, widest 64 <= 71, no tabs/high bytes/trailing WS, no in-literal apostrophes) and its
compile is byte-IDENTICAL (`cmp` rc=0) to the hop-6 draft .REL: rc=0, 8704 B, code=4030
data=36. Sim re-run with the EXPLICIT script `2 2 9 7 1 10 1 4` reproduces 120 normalized
lines / raw 1468 B / terminal draw / 8 gets / board `1,3,1,3,1,1,3,1,3` / **THREE** occupied
lines (86/91/96); line 1 has NO leading blank and line 120 is the exit-CRLF blank [C352].
NEW this hop: full line-for-line audit of the port against `TICTACTOE2.bas` PASSED, plus two
equivalence adaptations to record in the JSON notes (the 113/114/115 three-test becomes `k = 1`
default + two compares — exactly one can fire since `j <= m <= j+2`; and `t1 / 3` truncates
toward zero, equal to BASIC `INT()` because `m >= 1` at l0112).
EXACT NEXT = hop-6 § steps 4-10 (see the OWED list at the END of the hop-7 LEARNINGS §):
(4) append `reference.py:_Tict00Port` (flat label machine mirroring the pinned .PLI
statement-for-statement; skip `\r\n`, leading-separator blank when a line is open, echo
`%d\r\r\n`, exit one `\r\n`) + `_tict00_finalize` (clone of `_hamm00_finalize` line 452 /
`_amaz00_finalize` line 1101) + `tict00()` asserting 120 lines / draw / 8 gets / board / 3
occupied / unreached labels 104,105,113? no — 104/105,133/138,156/158,163/168,187/189 and
dead 1112/1137/1180/1200 never TERMINATE the run, register in `DERIVATIONS`; then diff
`derive('tict00')` vs the sim `norm()` BEFORE any JSON; (5) generate `TICT-00.json` VIA SCRIPT
from derive (link_target TICT00, console_input `2\r2\r9\r7\r1\r10\r1\r4\r^Z`, sha pin, collapse-
spaces-v1, limits as HANG-00, capabilities grep-verified against `spec/COVERAGE.tsv` AND against
statements actually present in the .PLI — board-init DO loop is the only `LOOP.DO_TO_BY`; verify
or drop AGG.VAR_INDEX_LADDER; notes (1)..(n) incl. THREE occupied, the two equivalence
adaptations, value mapping, numeric choice GET, IT IS rewrite, dead 1180/1200/1112/1137,
unreached list, 1468-raw-byte/120-line prediction); (6) `python3 tools/functional_runner.py
--stages source,derivation --tests TICT-00`; (7) lane B `--evidence build/fc01/corp7 --json-out
build/fc01/corp7/records.json` (+ `--double-run` into corp7-double if PASS), ACTUALS verbatim,
a FAIL stays classified never laundered; (8) `docs/functional-results.md` § 12 + § 1 row;
(9) `python3 tools/e2e_gate.py` compile tier -> build/gate-tict00.log; (10) explicit-path commit
(NEVER `handoff.config.json`; no push). Then LIFE-00, DHRY-00 (never execute the .SHAR), FFT-00;
HAMM-00 rev2 stays PROPOSED. Constraints: no ocaml/harness changes; ledger ends C352; NEVER
re-run the retry-DFS search; renew only at safe boundaries (renewal 7/12 used — successor is
hop 8).

SUPERSEDED-BY-ABOVE (kept as written): TICT-00 DRAFT COMPILE-WITNESSED — PIN/REFERENCE/JSON/LANE OWED (2026-11-03, continuation
chain hop 6 end; HEAD `824be64`, tree = managed blocks + operator `handoff.config.json`;
compiler `edce9e0e…`, build rc=0 verified at session start). Read FIRST `LEARNINGS.md`
§ "…TICT-00 implementation hop 6" — it carries the full state: draft
`build/fc01-scratch/TICT-00.draft.pli` mirrors `tict00_sim.py` statement-for-statement and
compiles rc=0 (`tict00.REL` 8704 B, code=4030 data=36 — FIRST full-machine witness);
identical-script cross-check RE-VERIFIED (BASIC 119 vs port 120 lines, diffs only
prompts+echo, IT IS vs IT'S, trailing exit-CRLF blank; sim run with explicit script
`2 2 9 7 1 10 1 4` — its __main__ default drops the choice 2); FALSIFIED: "2 occupied
messages" -> THREE (moves 1, 10, 1 at lines 86/91/96). NOTHING tracked authored yet; no
lane run, no gate run, no commit this hop. EXACT NEXT = hop-6 § steps 3-10 (convert draft
-> CRLF+bare^Z+<=71 -> pin `spec/functional/tests/TICT-00.PLI` + sha -> `reference.py
:_Tict00Port`/`tict00()`+DERIVATIONS (match `_hamm00_finalize` echo/\r handling), diff
derive vs sim norm() BEFORE JSON -> generate `TICT-00.json` VIA SCRIPT from derive
(link_target TICT00, console_input `2\r2\r9\r7\r1\r10\r1\r4\r^Z`, grep-verified capabilities,
full notes incl THREE occupied messages + dead 1180/1200/1112/1137 + unreached
104/105,133/138,156/158,163/168,187/189) -> `--stages source,derivation` -> lane B
`build/fc01/corp7` (+corp7-double if PASS) ACTUALS verbatim -> docs sec 12 + sec 1 row ->
`python3 tools/e2e_gate.py` compile tier -> explicit-path commit (NEVER
handoff.config.json; no push). NEVER re-run the retry-DFS search. Then LIFE-00, DHRY-00
(never execute the .SHAR), FFT-00; HAMM-00 rev2 stays PROPOSED. Constraints: no
ocaml/harness changes; ledger ends C352; functional runs are NOT DR claims; third-party
bytes never tracked; renew only at safe boundaries (renewal 6/12 used this hop;
successor is hop 7).

SUPERSEDED-BY-ABOVE (kept as written): TICT-00 CROSS-CHECK BLOCKER RESOLVED — DRAFT STEP IN FLIGHT (2026-11-03, continuation
chain hop 5; HEAD `60e7038`, tree clean except managed blocks + operator
`handoff.config.json`; compiler `edce9e0e…`). Read FIRST `LEARNINGS.md` § "…TICT-00
implementation hop, continuation chain hop 5" — it carries the FIX (port `occ()` needed
message + TWO blanks: BASIC 506 PRINT:PRINT:PRINT, l500 PRINT adds the third — models now
MATCH 8/8 identical scripts under collapse-normalization, port = BASIC + one trailing
exit-CRLF blank [C352]), the CONFIRMED spec script (choice 2 = O, moves 2,9,7,1,10,1,4 ->
DRAW; `console_input 2\r2\r9\r7\r1\r10\r1\r4\r^Z` — the hop-4 note's string dropped the
first move 2), the FAILURE LESSON (retry-DFS re-search blew up ~11h — NEVER re-search; the
hop-4 exhaustive facts stand, l1180/1200/1112/1137 stay faithful dead code), and the
COMPLETE statement-level port plan (flat label machine, f-count AND ladders with both
members re-loaded per label, shift idiom for M=0, flat loop emulation i<8/i<4/i<10, printer
l1002..l1080 manual loop with b1 ladder, detector fall-through, r-dispatch, l1400 closes
with put skip and falls to l2000 = dead store, nested show after l2000, board init
s(i)=2 via do loop). NEXT (hop-5 § NEXT steps 1-10): LF draft
`build/fc01-scratch/TICT-00.draft.pli` -> full-program scratch pre-compile -> CRLF+bare^Z
+<=71+apostrophe-free `spec/functional/tests/TICT-00.PLI` pin sha -> `reference.py
:_Tict00Port`/`tict00()`+DERIVATIONS, diff derive vs `tict00_sim.py` norm() BEFORE the JSON
-> TICT-00.json (link_target TICT00, grep-verified capabilities, full notes) ->
`--stages source,derivation` -> lane B `--evidence build/fc01/corp7 --json-out build/fc01
/corp7/records.json` (+corp7-double if PASS; ACTUALS verbatim, FAIL stays classified) ->
docs/functional-results.md § 12 + § 1 row -> `python3 tools/e2e_gate.py` compile tier ->
explicit-path commit (NEVER handoff.config.json; no push). Then LIFE-00, DHRY-00 (never
execute the .SHAR), FFT-00; HAMM-00 rev2 stays PROPOSED. No ocaml/harness changes; ledger
ends C352; third-party bytes never tracked.

SUPERSEDED-BY-ABOVE (kept as written): TICT-00 IMPLEMENTATION HOP IN FLIGHT (2026-11-03, continuation chain hop 4; HEAD `c6c699b`,
build rc=0, compiler `edce9e0e…`, checkpoint g184 attested CURRENT at session start).
Read FIRST `LEARNINGS.md` § "2026-11-03 — FC-01 CORPUS TICT-00 implementation hop" — it carries
the MEASURED game-tree result (the HUMAN win 1200 is UNREACHABLE in any play; 1180 never fires;
1112/1137 never fire), the CHOSEN script `O,2,9,7,1,10,1,4` → DRAW at 1400 with 2 occupied
messages and 94/94+ reachable BASIC lines fired, the port value mapping (`1`=computer,
`2`=empty, `3`=human; `g`=1 first pass / `g`=3 second pass, `h` the complement) that makes every
compare a positive literal, the two FALSIFIED transcription defects in the cross-check model, and
the detailed flat-machine port structure (printer+detector kept in the MAIN block via an `r`
return-address variable because sibling-nested-procedure calls are unwitnessed).
BLOCKER FIRST (see LEARNINGS continuation §): the port model gave 85 collapse-normalized lines vs the BASIC model's 84 — the two were fed DIFFERENT scripts in that run; re-run the identical script through both and fix the port model before anything else.
DONE this hop: `sha256sum -c SHA256SUMS` rc=0; listing re-read; independent BASIC model
`build/fc01-scratch/tict00_bas.py` (line-for-line, instrumented, fixed) + coverage searches
`tict00_dfs.py`/`tict00_full.py`/`tict00_cand.py`; HANG-00 idiom survey.
NOTHING tracked authored yet: no `TICT-00.PLI`, no `TICT-00.json`, no `reference.py:tict00`.
EXACT NEXT (hop-start steps 2-11 continued): (2) port simulator
`build/fc01-scratch/tict00_sim.py` on the HAMM/HANG byte model (`skip`=`\r\n`, `put` =
leading-separator blank when the line is open, `get` echo `%d\r\r\n`, exit appends one `\r\n`
[C352]) — cross-check its collapse-normalized stream against `tict00_bas.py` (only the two
prompts may differ: `DO YOU WANT 'X' OR 'O'` vs the numeric prompt, plus the GET echo text);
(3) pre-compile the risky shapes in ignored scratch BEFORE pinning (flat top-level goto machine
with ~40 labels, `if a = b then` scalar=scalar in a DO body, `s(i) = 1` variable-index store,
the 2-branch show ladder, the `r`-dispatch return, the occupied-retry loop-back);
(4) LF draft -> CRLF + bare ^Z + <=71 cols + apostrophe-free `spec/functional/tests/TICT-00.PLI`,
pin sha256; (5) `reference.py:_Tict00Port`/`tict00()` + `DERIVATIONS`, diff vs the simulator
BEFORE the JSON; (6) `TICT-00.json` (link_target TICT00, `console_input`
`2\r9\r7\r1\r10\r1\r4\r^Z`, capabilities grep-verified SUPPORTED/dr=ACCEPTS rows only, notes =
full removal/substitution list incl. the value mapping, the numeric choice GET, the apostrophe
rewrites, the unreachable 1200/1180/1112/1137 and the unreached-line list); (7) `python3
tools/functional_runner.py --stages source,derivation --tests TICT-00`; (8) lane B
`--evidence build/fc01/corp7 --json-out build/fc01/corp7/records.json` (+ `--double-run` into
`corp7-double` if PASS), ACTUALS verbatim, a FAIL stays classified never laundered; (9) `docs
/functional-results.md` § 12 + § 1 row; (10) `python3 tools/e2e_gate.py` compile tier ACTUALS;
(11) explicit-path commit (NEVER `handoff.config.json`; no push). Then LIFE-00, DHRY-00 (never
execute the `.SHAR`), FFT-00. No ocaml/harness changes; ledger ends C352; third-party bytes never
tracked.

SUPERSEDED-BY-ABOVE: TICT-00 HOP START COMPLETE (2026-11-02, continuation chain hop 3; this commit). BOTH listings
READ and sha-verified; **BASE CHOSEN: TICTACTOE2.bas** (sha `9945f459…`) — TICTACTOE1
(`e1125402…`) NEVER terminates (win/draw both GOTO 210; the only stop is GET-at-^Z-EOF,
UNMEASURED) so no finite complete stream can be derived — decision + full analysis + the
measured port-shape probe batch (shapes03/04/05: BY-3 refused -> (jj-1)*3+1 emulate; `> var`
and `= -1` refused -> shift idiom; scalar=scalar equality + guarded multi-statement DO blocks +
s(i)=-1 stores ACCEPTED rc=0) in `LEARNINGS.md` § "TICT-00 hop start" — READ IT FIRST.
EXACT NEXT (implementation hop): (1) design the PROPOSED port there (flat goto state machine,
numeric choice GET replacing string C$ GET 1=X/2=O documented, apostrophe rewrites, b2/b3/b6
temps, found-flag loop exits, fixed script reaching ONE legitimate END); (2) independent
simulator `build/fc01-scratch/tict00_sim.py` on the HANG/AMAZ byte model; (3) pre-compile
remaining risky shapes in ignored scratch BEFORE pinning; (4) LF draft -> pre-compile ->
CRLF+bare^Z+<=71+apostrophe-free `spec/functional/tests/TICT-00.PLI` pin sha; (5)
`reference.py` mirror + DERIVATIONS, diff vs simulator BEFORE JSON; (6) `TICT-00.json`
(link_target TICT00, capabilities grep-verified SUPPORTED only); (7) `--stages
source,derivation --tests TICT-00`; (8) lane B `--evidence build/fc01/corp7 --json-out
build/fc01/corp7/records.json` (+ corp7-double if PASS), ACTUALS verbatim, FAIL stays
classified; (9) docs § 12 + § 1 row; (10) `python3 tools/e2e_gate.py` compile tier; (11)
explicit-path commit (NEVER handoff.config.json; no push). Then LIFE-00, DHRY-00 (never
execute the .SHAR), FFT-00. No ocaml/harness changes; ledger ends C352; third-party bytes
never tracked.

SUPERSEDED-BY-ABOVE (kept as written): TICT-00 HOP START — program 5 of 8 (Tic-Tac-Toe, BASIC).
NOTHING read or authored yet for this program beyond the standing table note "two upstream
listings (tictactoe1/2)". EXACT STEPS per
the standing corpus procedure (PROGRESS § Current phase table + HANG/AMAZ precedents):
(1) verify `sha256sum -c SHA256SUMS` rc=0 in `build/functional/fc01-sources/` for the Tic-Tac-Toe
file(s); READ BOTH upstream listings (`basic/` — tictactoe1/2 per the operator table), pick the
richer/more testable one and RECORD the choice + why; rights note per README § 5.1 (licence
UNVERIFIED, recorded as such; no upstream bytes in tracked files); if the chosen version has
character INPUT (moves as 1-9 or coordinates), record: CHARACTER console GET is UNMEASURED —
adapt moves to numeric GET like HANG-00 (the GET+echo laws are run-witnessed) or to a declared
fixed script; player-vs-player vs player-vs-computer decides how much logic to keep.
(2) design INSIDE the measured corpus subset: literal divisors ≤ 127 only (variable DIV MEASURED
refused, HAMM-00 rev1); ordered-compare constants ≥ 1, strict compares only (COND.GE_LE
refused); no apostrophes in literals (rewrite contractions); ≤ 71 cols; every `put list`
single-item under the MEASURED leading-blank separator law (rows render space-separated,
collapse-spaces-v1); NO multi-item or member-in-condition (load member to scalar first);
subscripts simple var or var+1 [C159] (b2 temps otherwise); AGG.MULTIDIM refused — flatten any
3x3 board to 9 cells; ON-GOTO/if-chains → if ladders; goto never crosses an ACTIVE DO
(HANG-00 idiom); framing: leading bare PUT SKIPs → leading "" lines [C352]; final output that
closes a line + exit CRLF → trailing "" (MATH-00 precedent).
(3) independent scratch simulator `build/fc01-scratch/tict00_sim.py` on the AMAZ/HANG byte model;
(4) LF draft + scratch pre-compile (shape check only); (5) CRLF + bare ^Z + <=71 +
apostrophe-free `spec/functional/tests/TICT-00.PLI`, pin sha256; (6) `reference.py` mirror +
DERIVATIONS entry, diff vs simulator BEFORE the JSON; (7) `TICT-00.json` (link_target TICT00,
console_input from the chosen script, capabilities grep-verified SUPPORTED/dr=ACCEPTS rows only,
notes = full removal/substitution list); (8) `python3 tools/functional_runner.py --stages
source,derivation --tests TICT-00`; (9) lane B `--evidence build/fc01/corp7
--json-out build/fc01/corp7/records.json` (+ `--double-run` into corp7-double if it PASSES),
ACTUALS verbatim, a FAIL stays classified never laundered; (10) `docs/functional-results.md`
§ 12 + § 1 row; (11) `python3 tools/e2e_gate.py` compile tier; (12) explicit-path commit
(NEVER `handoff.config.json`; no push). Then LIFE-00, DHRY-00 (never execute the .SHAR), FFT-00.
No ocaml/harness changes; ledger ends C352; third-party bytes never tracked.

SUPERSEDED-BY-ABOVE (kept as written): AMAZ-00 IMPLEMENTATION IN FLIGHT — CLOSED: landed
**PASS** at this boundary (see Current phase and LEARNINGS AMAZ-00 COMPLETION hop). DONE+VERIFIED:
`spec/functional/tests/AMAZ-00.PLI` pinned (sha256 0c0abfab0a728861e808a175982530669e9feb99d342b016f84d6d51c9430c9d,
7327 B, 338 lines, CRLF+bare ^Z, <=71 cols, apostrophe-free, single-item puts; compiles
rc=0 5760 B code=3166 data=58); `reference.py:_Amaz00Port`/`amaz00()` + DERIVATIONS
registered; derivation diffed against instrumented scratch simulator: BYTE-EQUAL, 18
lines (8 x "", ". .-- .-- .-- .", 4x(cell,wall), ""); all invariants pass (C=17,
permutation, entrance col 1 (FALSIFIED: earlier 'col 2' was a sim reporting bug), z=1,
n980=1, 1011..1014 UNREACHED, bottom gap [3], connectivity BFS; 12 draws, gg<=885).
FALSIFIED also: '4 leading blanks/no trailing' -> 8 leading + 1 trailing [C352].
MEASURED my-compiler refusals (port-shape, NOT DR claims): member-in-condition refuses;
subscripts must be simple var or var+1 [C159] (w(b-4)/w(b+4) refuse; b2 temps used).
NEXT (successor): (1) AMAZ-00.json (schema pli80-functional/1, link_target AMAZ00, sha
pin above, console_input "^Z", expected 18 lines, derivation reference.py:amaz00,
collapse-spaces-v1, limits as HANG-00, capabilities grep-verified SUPPORTED/dr=ACCEPTS
candidates DECL.FIXED_BIN15 AGG.ARRAY_1D_FIXED LOOP.DO_TO_BY IO.PUT_LIST_FIXED
IO.PUT_SKIP EXPR.REL_FIXED_EQ_K EXPR.SELF_ADD_LADDER TRAN.GOTO_SAME_BLOCK; notes =
removal/substitution list incl. banner dropped, dimension INPUT dropped H=V=4 declared,
flat arrays (AGG.MULTIDIM refused), gg*37+11 literal-divisor draws 4/3/2 seed 0, ON-GOTO
-> ladders, <>0->scalar-temps, separator adaptation, exit-branch unreached).
(2) functional_runner --stages source,derivation --tests AMAZ-00. (3) lane B
--evidence build/fc01/corp6 (+corp6-double if PASS), ACTUALS verbatim, FAIL stays
classified. (4) docs/functional-results.md sec 11 + sec 1 row. (5) e2e_gate compile
tier. (6) explicit-path commit (never handoff.config.json; no push). Then TICT-00,
LIFE-00, DHRY-00 (never execute the .SHAR), FFT-00. No ocaml/harness changes; ledger
ends C352; third-party bytes never tracked. Full record: LEARNINGS.md 2026-11-02
AMAZ-00 implementation hop.

SUPERSEDED-BY-ABOVE (kept as written): AMAZ-00 hop-start: LISTING READ (143 lines, sha this boundary (143 lines, sha
`3f6fa3f2…` verified; full analysis + PROPOSED design in `LEARNINGS.md` § "AMAZ-00 hop start"
— READ IT FIRST; operator directive: execute pragmatically, prioritize a completed adaptation
over preparatory analysis; never alter program/expectation to obtain a PASS). TWO corrections
to the steps below from that section: (i) FALSIFIED — this upstream listing has NO walk/direction
INPUT phase (generation + print only): AMAZ-00 is a PURE-PUT program, `console_input` = bare
`^Z`; (ii) the design fixes H=4,V=4 (or richer 5x4 if residues allow) as LITERAL constants,
flattens W/V arrays (AGG.MULTIDIM refused), uses only literal-divisor draws (2/3/4), TAB banner
+ dimension INPUT + retry loop DROPPED (documented), separator-space adaptation, 4 leading
blank lines [C352], NO trailing blank after the final `"."` row. Steps:
(1) read `build/functional/fc01-sources/basic/AMAZING.bas` (+ `URLS.tsv`/`NOTES.txt`; verify
`sha256sum -c SHA256SUMS` rc=0 for that file); rights note per README § 5.1 (licence UNVERIFIED,
recorded as such); (2) design INSIDE the measured subset — 2-D grid ⇒ `AGG.MULTIDIM` REFUSED,
flatten like the HANG stage grid (literal row/col strides, NO division — variable DIV is
MEASURED refused; strict compares only, constants ≥ 1; literal divisors ≤ 127 if any; every
`put list` single-item with the MEASURED leading-blank separator law across statements; numeric
GET + echo laws now RUN-witnessed — but the maze needs a fixed-length MOVES/SEED-like script or
deterministic maze parameters: the BASIC RND route must be replaced by a DECLARED integer draw
(HAMM `gg*37+11` idiom) or a fixed script; width ≤ 71 cols, no apostrophes; the maze EXIT/move
direction INPUT (LETTERS) is CHARACTER console GET — UNMEASURED — adapt to numeric direction
codes like HANG, and record it); (3) independent scratch simulator
`build/fc01-scratch/amaz00_sim.py` on the HANG byte model (skip=CRLF, separator blank, echo
`L\r\r\n` closes line, exit CRLF [C352], collapse-spaces-v1/drop-one-empty); (4) LF draft +
scratch pre-compile (syntax/shape check of MY port before pinning only); (5) CRLF + bare ^Z +
≤71 + apostrophe-free `spec/functional/tests/AMAZ-00.PLI`, pin sha256; (6)
`reference.py:_Amaz00Port`/`amaz00()` + DERIVATIONS, diff vs simulator BEFORE the JSON; (7)
`AMAZ-00.json` (link_target AMAZ00, capabilities only from SUPPORTED/dr-ACCEPTS COVERAGE rows,
console_input + notes = removal/substitution list); (8) `python3 tools/functional_runner.py
--stages source,derivation --tests AMAZ-00`; (9) lane B `--evidence build/fc01/corp6
--json-out build/fc01/corp6/records.json` (+ `--double-run` into corp6-double if it PASSES);
(10) `docs/functional-results.md` § 11 + § 1 row; (11) `python3 tools/e2e_gate.py` compile tier;
(12) explicit-path commit (NEVER `handoff.config.json`; no push). If a stage FAILs: keep it,
classify `my-gap`/`dr-refuses`/`unmeasured`, record and move on — do NOT extend the harness.

SUPERSEDED-BY-ABOVE: HANG-00 IMPLEMENTATION — CONTINUATION CHAIN HOP 1 COMPLETE (was: IN
FLIGHT; landed PASS this boundary, see Current phase and LEARNINGS hop-1 COMPLETION §). Read FIRST `LEARNINGS.md` § "2026-11-03 —
FC-01 CORPUS HANG-00 continuation chain, hop 1" — it supersedes framing details of both
prior HANG hops. DONE this hop: simulator REWRITTEN with correct framing (four
falsifications listed there; 329 normalized lines, script fully consumed, exit law
[C352]); design-hop shift `t1=m+1; t1<12` FALSIFIED -> port uses direct `if m < 10 then
goto disp;`; nested-DO and single-statement-do-block shapes COMPILE-witnessed in ignored
scratch `build/fc01-scratch/shapes02.pli` (rc=0, 640 B); capability list TRIMMED to 12
validated ids; complete LF draft authored at `build/fc01-scratch/HANG-00.draft.pli`
(statements mirror the simulator exactly; gotos never cross an active DO). EXACT NEXT
(same hop): (1) convert draft -> CRLF + bare ^Z, verify <=71 cols and ZERO apostrophes
and that the draft's every `put list` is single-item, pin sha256, write
`spec/functional/tests/HANG-00.PLI`; (2) append `reference.py` `_Hang00Port` statement
mirror + `hang00()` + DERIVATIONS entry (same byte laws as the simulator; assert
329 lines, verdict path win/win/hang, script consumed, exit framing); (3) diff
`derive('hang00')` vs simulator lines BEFORE writing `HANG-00.json` (link_target HANG00,
sha pin, console_input `71\r85\r71\r77\r1\r70\r65\r76\r89\r1\r69\r88\r83\r86\r87\r65\r66\r67\r68\r81\r84\r90\r1\r^Z`,
12 caps, notes = removals + separator adaptation + unwitnessed shapes + m<10 correction);
(4) `python3 tools/functional_runner.py --stages source,derivation --tests HANG-00`;
(5) lane B `--evidence build/fc01/corp5 --json-out build/fc01/corp5/records.json`
ACTUALS verbatim (a FAIL stays classified, never laundered; FIRST corpus GET-at-RUN is
the risky stage); (6) `docs/functional-results.md` § 10 + § 1 row; (7)
`python3 tools/e2e_gate.py` compile tier ACTUALS; (8) explicit-path commit (NEVER
`handoff.config.json`; no push). THEN program 4 AMAZ-00 (maze) per the standing corpus
procedure; HAMM-00 rev2 stays PROPOSED. No ocaml/harness changes; ledger ends C352;
third-party bytes never tracked; renew only at safe boundaries per `handoff.config.json`.

SUPERSEDED-BY-ABOVE: HANG-00 IMPLEMENTATION HOP IN FLIGHT (2026-11-03, renewal 12/12 = CONFIGURED CHAIN CAP; HEAD
`a78aed5`, build rc=0, compiler `edce9e0e…`). Read FIRST `LEARNINGS.md` § "2026-11-03 — FC-01
CORPUS HANG-00 implementation hop (renewal 12/12 …)": the design hop's step-1 byte model is
FALSIFIED (one blank precedes every PUT LIST item that is not the first since the last line
start, ACROSS statements — three stored Batch-A PASS captures + DR's own
`golden/e32rt_E32B1`/`e32b_E32B1_dr` witness), so the dash row, the used-letter row and every
grid row render SPACE-separated (declared adaptation); a consumed GET CLOSES the line (HAMM-00
committed expectation); every risky shape (nested `show` procedure with its own local
`character(1) varying` + PUT, variable DO bound, call-in-IF, do-while over calls, goto-in-IF,
`get list`, member→scalar) is COMPILE-witnessed in `build/fc01-scratch/shapes01.pli` (rc=0,
1280 B, code=500 data=17); state stays INTEGER codes with three literal-indexed word arrays
plus a `wlit` varying word string; capability list validated citable.
EXACT NEXT = design hop steps 1-10 WITH the separator law folded into the simulator AND the
mirror: scratch `build/fc01-scratch/hang00_sim.py` (independent game model) →
`build/fc01-scratch/mk_hang00_pli.py` generator → LF draft → CRLF + bare ^Z + <=71 cols +
apostrophe-free `spec/functional/tests/HANG-00.PLI` → `reference.py:hang00` statement-for-
statement mirror + `DERIVATIONS` entry → diff mirror vs simulator BEFORE writing `HANG-00.json`
(link_target HANG00, sha pin, `console_input` = 23 CR-terminated codes
`71,85,71,77,1,70,65,76,89,1,69,88,83,86,87,65,66,67,68,81,84,90,1` + bare `^Z`, notes =
removals/unwitnessed/FALSIFIED separator model) → `python3 tools/functional_runner.py --stages
source,derivation --tests HANG-00` → lane B `--evidence build/fc01/corp5
--json-out build/fc01/corp5/records.json` ACTUALS verbatim (a FAIL stays classified, never
laundered) → `docs/functional-results.md` § 10 + § 1 row → `python3 tools/e2e_gate.py` compile
tier ACTUALS → explicit-path commit (NEVER `handoff.config.json`; no push).
**CHAIN CLOSED AT THIS CAP: call `handoff_finalize`, NOT `handoff_renew` — no successor session
exists without an operator reset of `renewal` state; programs 4-8 (AMAZ-00, TICT-00, LIFE-00,
DHRY-00, FFT-00) stay queued and HAMM-00 rev2 stays PROPOSED.**

HAMM-00 rev1 RECORDED (2026-11-03, renewal 11/12; HEAD `5772b8a` at execution; build rc=0,
compiler `edce9e0e…`). Lane B executed (`build/fc01/corp4/records.json`, git_head `5772b8a`):
SOURCE pass (sha `cc25fe75…` + encoding), DERIVATION pass (derivation == spec, 211 lines),
COMPILE **FAIL** attr=`compiler` witness `refusal rc=2` message verbatim `Fatal error: exception
Failure("codegen: DIV by non-constant [TBD]")`; LINK/RUN/ASSERT unrun; `verdicts: PASS=0
FAIL=1`. Classified `my-gap` (`ocaml/lib/codegen.ml:4997-5010` — DIV lowered by CONSTANT only,
`[P071B/P080A]`); the four variable-divisor sites were flagged run-unwitnessed in spec note
(10); expectation NOT laundered; nothing promoted to any ledger (ends C352 — a functional run
is not a DR claim; DR variable-DIV stays UNMEASURED). goto-in-IF / adjacent-literal PUT LIST /
c=2/4 rats dispatch NOT reached — still unmeasured. `docs/functional-results.md` § 9 + § 1 row
written from these ACTUALS; FULL compile-tier gate rc=0 twice, ACTUALS byte panel **1174/0 of
1174**, negative **181/181**, divergence **9/9**, coverage **133 rows 0/0**, census **15/0/26/0**,
prose **5 active clean** (log `build/gate-hamm00.log`). rev2 subtraction-loop division
PROPOSED (derived stream identical; port change only), NOT executed this hop. COMMITTED at this boundary (`610a8df`): explicit paths `spec/functional/tests/HAMM-00.PLI`, `spec/functional/tests/HAMM-00.json`,
`spec/functional/tests/reference.py`, `docs/functional-results.md`, `LEARNINGS.md`,
`PROGRESS.md`, `HANDOFF.md` — NEVER `handoff.config.json`; no push. NEXT: program 3 **HANG-00**
(Hangman) — read `build/functional/fc01-sources/basic/HANGMAN.bas` + `URLS.tsv`/`NOTES.txt`,
rights review (README § 5.1), DESIGN hop first (corpus laws: literal divisors ≤ 127 — variable
DIV now MEASURED refused; ordered-compare constants ≥ 1; strict compares only; ≤ 71 cols; no
apostrophes; GET echo law measured), then triple → `--stages source,derivation` → lane B
`--evidence build/fc01/corp5` → docs § 10 + § 1 → gate → explicit-path commit. Constraints
unchanged (no ocaml/harness changes; ledger C352; no push; FAIL stays classified; renewal chain
11/12 — renew only at safe boundaries per `handoff.config.json`).

**FC-01 OPERATOR OVERRIDE (2026-11-02). HOP 5 IS CANCELLED — do NOT implement `stage_files`,
`expected.file_expectations`, FILE-00/FILE-01, the fc01-fileio oracle round or ONUNIT-00.**

HAMM-00 DESIGN COMPLETE (2026-11-03 design hop, this chain, renewal 3/12): the full port
design, the MEASURED console-GET echo environment law (echo `L\r\r\n`, no PLILIB extra
terminator, unconsumed ^Z never captured — from golden/e32rt_NETWORK + e29dr_runB transcripts;
expected echo lines carry a trailing `\r`), the GET/GOTO shape confirmations, the bin15
scaling analysis (A=300/S≈2400/P=95 declared adaptation; births order law
floor(floor(X/P)/100)=floor(X/(P*100)) exact, reverse order FALSIFIED; P≥100 one-step
exactness) and the draw/parity/impeach reconstructions are in LEARNINGS.md § 2026-11-03
FC-01 CORPUS HAMM-00 design hop — READ THAT SECTION FIRST; everything needed to implement
is there. EXACT NEXT: prototype reference.py:hamm00 in build/ (iterate the 10-year script to
a rich path: complaints, plague, rats, starvation bounds, asserts all intermediates <32767),
then write HAMM-00.PLI + HAMM-00.json per that section, --stages source,derivation, lane B
--evidence build/fc01/corp4, docs § 9 + § 1 row, e2e_gate compile tier, explicit-path commit.
No ocaml/harness changes; ledger ends C352; no push; operator handoff.config.json stays
unstaged. HAMM-00 IMPLEMENTATION HOP IN FLIGHT (2026-11-03, renewal 4/12). Read FIRST
`LEARNINGS.md` § "2026-11-03 — FC-01 CORPUS HAMM-00 implementation hop start": echo witnesses
re-measured byte-exact (consumed ^Z echoes as literal `^Z` + `\r\r\n` — FALSIFIES the design
hop's blank-row reading; unconsumed ^Z never captured — ACCEPTED, corp3 witness); the design
hop's year-1 script is FALSIFIED at S≈2400 (births `5*(20*300+s') = 37250 > 32767` at the
declared gg=4 draw c=5 — violates its own 20a+s≤6553 bound) and at the year-1 rats draw
(gg=3 → c=3 ODD); the d=45 survival arithmetic is ACCEPTED but needs a tuned opening store
(s0≈600-900, iterate). `COND.GE_LE` is REFUSED — port uses strict compares + shift/flag
idioms only (constants ≥ 1); rest of the design hop § stands (draw formula gg*37+11, GET
shape R903/NETWORK, goto same-block, bells/TAB dropped). EXACT NEXT: (1) build
`build/fc01-scratch/hamm00.py` — byte-level stream model (skip=`\r\n`, text items: literals
natural + fixed numerics `%10d`, echo=`L\r\r\n`, exit appends one `\r\n` [C352]; normalize
`re.sub(' +',' ',raw.replace('\r\n','\n'))`, split `\n`, drop ONE trailing empty), game per
the BASIC trace, asserts ALL intermediates ≤ 32767; iterate script to a rich path (price/feed
complaints, plague year, EVEN rats year — not year 1, skip-year, d>0 year); emit expected
lines (echo lines carry trailing `\r`) + console_input (lines joined `\r`, trailing `^Z`
NEVER consumed) + PL/I statement skeleton. (2) HAMM-00.PLI (CRLF ^Z ≤71, header naming
HAMMURABI.bas sha 93fea01f…) + HAMM-00.json (third-party, licence UNVERIFIED, capabilities
from SUPPORTED rows incl IO.GET_LIST/TRAN.GOTO_SAME_BLOCK, notes = removal/substitution
list). (3) `python3 tools/functional_runner.py --stages source,derivation --tests HAMM-00`,
then lane B `--evidence build/fc01/corp4`, ACTUALS verbatim. (4) docs/functional-results.md
§ 9 + § 1 row; `python3 tools/e2e_gate.py` compile tier ACTUALS; explicit-path commit;
renew at safe boundary. No ocaml/harness changes; ledger ends C352; no push; operator
handoff.config.json stays unstaged; third-party bytes never tracked. (Prior: HAMM-00 DESIGN
committed cb223ba/6571212; WKDAY-00 rev3 PASS `21c9f69`.)

HAMM-00 IMPLEMENTATION HOP 3 STATE (2026-11-03, renewal 6/12; HEAD `a5ef608`, build rc=0,
compiler `edce9e0e…`, checkpoint g161 verified CURRENT by hash replay). Read FIRST
`LEARNINGS.md` § "2026-11-03 — FC-01 CORPUS HAMM-00 implementation hop 3": hop 2's draw-residue
table is FALSIFIED (off-by-one draw index — rats fire ONLY at `g0 ≡ 2 or 3 (mod 5)`, c=2 or c=4,
and EVERY year; `g0 ≡ 4` gives NO rats; yield = `(2 g0 mod 5)+1`, so g0=3 → yield 2 / g0=2 →
yield 5; plague years 3,5,7,9 at g0=3 and 2,4,6,8,10 at g0=2; births c=1 at g0=3 → births bound
`20a+s ≤ 32767`). Complaint paths are STATE-FREE → search the accepted-amount SPINE first, then
insert complaints (firability conditions listed in that section). Letting P collapse every year
is FALSIFIED as a verdict strategy (every year feeds ~44% into P1 → 880 `P1>33` → FINK); the
survivable rich shape is one/two survived starve years + the rest SKIP years (`feed ≥ 20(p+1)`)
with acreage kept `a ≥ 7 p_final`. Simulator rewritten as state-based `build/fc01-scratch/hamm00_sim.py`
(silent/emit modes, 6-bit mask, `DUMMY` plan for the year-11 report, `MAXFEEDLINE=12767`, hop-2
bugs fixed: `starve_years` never populated; 865 `PEOPLE DIED!!` and 950 `HATE YOUR GUTS!!` both
take TWO bangs, 567 FOUR). MEASURED SEARCH RESULT this hop: NO rich spine found — DFS
(`hamm00_dfs.py`, budget 30000) reports NO spine at (g0,s0) = (3,900/1200/1500), (2,900), (7,900),
(8,900), and exactly ONE spine at g0=2, s0=1500 whose mask is {skip,starve} with
verdict `impeached-year10` (a LEGITIMATE complete path per the design hop) but whose complaint
insertion FAILED → `rich_g2_s1500.json` NOT written, `spine` only. UNRESOLVED QUESTION: is the
failure the menu, the mask goal, or the bin15 bounds? Next hop should (a) run the spine search
over a WIDER sweep (g0 ∈ {2,3} × s0 ∈ {600..2400 step 100}, budget ≥ 300k, and let
`verdict ∈ {nero,not-too-bad,fantastic,impeached-yearN≥5}` all count as acceptable — the
complaint-firability filter must also try LATER years and all three plant-complaint kinds),
(b) if still nothing, RELAX the declared adaptation legally and record it: e.g. a larger opening
store `s0` with the year-1 report printing a negative `e = 900 − s0` (allowed: `%10d` prints the
sign; declared, not hidden), or `H` declared as `2*A*Y` so `e ≥ 0` at any `s0`, or an
accepted-buy year followed by a sell-complaint year so the sell complaint is firable, and
(c) ONLY then emit expected lines + console_input + skeleton → `spec/functional/tests/HAMM-00.PLI`
/`.json` + `reference.py:hamm00`/`DERIVATIONS` → `--stages source,derivation` → lane B
`--evidence build/fc01/corp4` → docs § 9 + § 1 row → `python3 tools/e2e_gate.py` compile tier →
explicit-path commit. A FAIL stays classified, never laundered. Constraints unchanged: no
ocaml/harness changes, no push, ledger ends C352, operator `handoff.config.json` stays unstaged,
third-party bytes never tracked.

HAMM-00 IMPLEMENTATION HOP 5 STATE (2026-11-03, renewal 8/12; HEAD `7957474`, build rc=0,
checkpoint g165 attested at start). Spine RE-VERIFIED byte-stable via the scratch one-liner in
`LEARNINGS.md` § "...implementation hop 5" (READ THAT SECTION FIRST — it carries the exact
regeneration command for the 211 expected lines + console_input, the harness contracts, the
verified capabilities list, the adjacent-literal split for the two >71-col literals [PROPOSED,
unverified compile], and the complete statement-for-statement port plan). NOTHING authored yet:
no HAMM-00.PLI/.json/reference.py:hamm00 exist. EXACT NEXT = the hop-5 § NEXT steps 1-8: triple
-> --stages source,derivation (diff derivation vs simulator stream first) -> lane B
--evidence build/fc01/corp4, ACTUALS verbatim -> docs § 9 + § 1 -> compile-tier gate ->
explicit-path commit. Constraints unchanged: no ocaml/harness changes, no push, ledger ends C352,
functional runs are NOT DR claims, a FAIL stays classified never laundered, operator
handoff.config.json stays unstaged, third-party bytes never tracked.

HAMM-00 IMPLEMENTATION HOP 4 STATE — RICH SPINE FOUND (2026-11-03, renewal 7/12; HEAD
`9cbd8dc`, build rc=0, compiler `edce9e0e…`). Read FIRST `LEARNINGS.md` § "2026-11-03 — FC-01
CORPUS HAMM-00 implementation hop 4" — it contains the COMPLETE plan. Hop 3's "no rich path"
was FALSIFIED as two simulator bugs (buy/sell complaints emitted inside the accepted-amount
branch — a complaint is legal in EVERY year; and `insert_complaints`'s unconditional `break`
tried one combo/one kind). MEASURED SPINE (simulator, ignored scratch
`build/fc01-scratch/hamm00_sim.py` fixed + `hamm00_build.py` + `spine_t_300.json`): g0=2,
s0=1500, A=300/H=900/Y=3/P=95/I=5/Q=1; per year (buy, sell, feed, plant) — y1 0, SELL-claim 301
+0, 1352, SEED-claim 298 +200; y2 BUY-claim 43 +0, 0, 700, 300; y3 0, 0, FEED-claim 1588 +900
(SKIP), 300; y4 0,0,520,259; y5 0,0,780, ACRES-claim 301 +300; y6 0,0,480,239; y7 0,0,760,300;
y8 0,0,460, PEOPLE-claim 230 +229; y9 0,0,740,300; y10 0,0,300 (survived starve d=8), 229.
ALL EIGHT mask features (skip, starve, buyc, sellc, feedc, plantc, plague, rats), verdict
**not-too-bad** (P1=7, L=10 → 960/965 extra draw), D1=41, 211 stream lines, 46 fed values (max
1588), every intermediate ≤ 32767. Port law: strict compares only (`t = x+1; if a < t`, plague
`t = q+4; if t > 4`, impeach `t = (p*45)/100; if d > t`); literal divisors 2/4/5/10/20/45/100
with the rats site dispatched on c ∈ {2,4}; VARIABLE division unavoidable and flagged at exactly
three sites (births `x/p`, P1 `d*100/p` and `/z`, `l = a/p`) — first corpus use, a FAIL stays
classified. NOTHING promoted to any ledger (ends C352); no ocaml/harness byte; no emulator run
this hop. EXACT NEXT (authoritative steps in that LEARNINGS § NEXT): write HAMM-00.PLI for this
spine, `reference.py:hamm00` + `DERIVATIONS`, HAMM-00.json (console_input = 46 CR-joined values +
bare `^Z`; removal/substitution notes), `--stages source,derivation`, lane B `--evidence
build/fc01/corp4`, docs § 9 + § 1 row, `python3 tools/e2e_gate.py` compile tier, explicit-path
commit. No ocaml/harness changes, no push, operator `handoff.config.json` stays unstaged,
third-party bytes never tracked.

HAMM-00 IMPLEMENTATION HOP 6 STATE (2026-11-03, renewal 9/12; HEAD `39f1d6b`, build rc=0,
compiler `edce9e0e…`). Read FIRST `LEARNINGS.md` § "…implementation hop 6": the COMPLETE port is
DRAFTED on disk at `build/fc01-scratch/HAMM-00.draft.pli` (LF; must be converted to CRLF + bare
`^Z`, width-checked <=71, apostrophe-free, then sha256-pinned); the 1:1 line/framing law
(`put list(x); put skip;`, prompt = `put list(prompt)` with no skip, blank-line counts), the
three port choices (z++ after the report, `qq` preserved for 540, the +100 ladder offsets), the
kept dead stores, the verified capability ids, and the FIVE unwitnessed shapes (goto-in-IF,
variable divisors, adjacent-literal PUT LIST, the `c = 2/4` rats dispatch, the t3/t4
idempotence guard) are all there. NOTHING tracked has been authored yet — no HAMM-00.PLI/.json,
no `reference.py:hamm00`. EXACT NEXT = hop-6 § NEXT steps 1-8 (convert draft -> reference.py +
diff its stream against the hop-5 simulator one-liner -> HAMM-00.json -> `--stages
source,derivation` -> lane B `--evidence build/fc01/corp4` ACTUALS verbatim -> docs § 9 + § 1 ->
compile-tier gate -> explicit-path commit). Constraints unchanged: no ocaml/harness changes, no
push, ledger ends C352, functional runs are NOT DR claims, a FAIL stays classified never
laundered, operator `handoff.config.json` stays unstaged, third-party bytes never tracked.

HAMM-00 IMPLEMENTATION HOP 2 IN FLIGHT (2026-11-03, renewal 5/12; HEAD `9c91e9f`, build
rc=0, compiler `edce9e0e…`, checkpoint g159 verified CURRENT by hash replay). Read FIRST
`LEARNINGS.md` § "2026-11-03 — FC-01 CORPUS HAMM-00 implementation hop 2": the PUT-LIST
inter-item SINGLE-BLANK separator law is MEASURED from the stored TABLE-00 raw capture
(byte simulator joins items with one space; fixed numeric `%10d`; no trailing blank at
line end; literal-literal adjacency stays unmeasured — port uses none); console_input
sending convention confirmed (each fed line ends CR; trailing `^Z` bare, never consumed,
[C113] note quoted); the draw formula locks each ROLE to a residue class when 5 draws
fire per year — rats-EVEN-only-in-later-years is FALSIFIED as unachievable (PROPOSED
resolution: seed g0 ≡ 3 mod 5 → rats c=2 every year incl. year 1, yield 5, births c3=1
so the births bound is 20a+s ≤ 32767, plague years 3,5,7,9, prices 26/21 alternating);
the design's 1300 buy overclaim is FALSIFIED at price 26 (26*1300=33800 overflows — the
simulator's chk() caught it on the first smoke run; claims must keep y*claim ≤ 32767 and
the live-fed q ≤ 12767 for the q+20000<20000 negative-guard form). 880/885 ladder goes to
565 WITHOUT the 560 YOU-STARVED line; P1/L integer-route adaptations asserted vs float.
`build/fc01-scratch/hamm00.py` EXISTS (ignored) with the byte-level Stream model, run(),
rich() predicate and Fail-based search hooks — the smoke run raised the overflow above.
EXACT NEXT (successor): (1) in build/fc01-scratch, sweep g0 ∈ {3,4} × S0 (try 400..2000;
remember year-1 report prints e=900−s0) and DFS the per-year menus (buy claim ≤ 32767/y
and > s/y; buy-accept ∈ {0,5,10,20}; sell claim a+1, accept < a; feed claim s+1, accept
≤ s targeting d ∈ {5..45} or skip q ≥ 20p+1; plant claim a+1/seed-claim/people-claim, accept
≤ a, seed ≤ s, d < 10p) until rich() + all chk/asserts pass and verdict ≠ fink-ladder;
(2) emit expected lines (echo lines carry trailing `\r`; [C352] framing; exit rule: a bare
final put skip yields ONE trailing "" after the drop-one-empty split law), the console_input
string, and the PL/I statement skeleton; (3) hand-port to `spec/functional/tests/HAMM-00.PLI`
(CRLF ^Z ≤71 cols; header names HAMMURABI.bas sha 93fea01f…; strict compares with
constants ≥ 1 only — weak tests as x < N+1 forms; shift form t=q+4>4 plague guard;
divisors: literals 2/5/10/20/45/100, variables p,c,z,q/20 — run-unwitnessed first use,
flagged; goto same-block labels; no apostrophes in literals — WASN'T rewritten); put
`hamm00()` into reference.py + DERIVATIONS mirroring the port exactly; (4) HAMM-00.json
(third-party, licence UNVERIFIED; capabilities incl IO.GET_LIST, TRAN.GOTO_SAME_BLOCK,
DECL.FIXED_BIN15, IO.PUT_LIST_FIXED, IO.PUT_SKIP, EXPR.REL_FIXED_EQ_K; notes = full
removal/substitution list: bells/TAB/banner dropped, RNG formula with seed g0 declared,
P1/L integer adaptation, rats-every-year residue, negative-input branches compile-only);
(5) `python3 tools/functional_runner.py --stages source,derivation --tests HAMM-00` then
lane B `--evidence build/fc01/corp4 --json-out build/fc01/corp4/records.json`, ACTUALS
verbatim (variable division is run-unwitnessed — a FAIL stays, classified, expectation NOT
laundered); docs/functional-results.md § 9 + § 1 row; `python3 tools/e2e_gate.py` compile
tier; explicit-path commit (LEARNINGS, PROGRESS, HANDOFF prose, the triple, docs). No
ocaml/harness changes; no push; ledger ends C352; operator handoff.config.json stays
unstaged; third-party bytes never tracked.
Nothing of it had begun (measured at `6a35b9c`: no `stage_files` anywhere in
`tools/functional_runner.py`; `file_expectations` is only the pre-existing fail-closed rejection
at lines 127/398-400). Hop-4 close-out `6a35b9c` and Batch-B REV2 `a5815a8` stand untouched; the
hop-4 file-I/O survey + PROPOSED design stay in `LEARNINGS.md` as a RECORD, cancelled as a plan.

NEW PRIORITY — **adapt the eight operator-selected historical programs into a representative
PL/I-80 functional corpus**, autonomously across renewals:

**HOP STATUS 2026-11-03 (this chain):** WKDAY-00 COMPLETE — rev3 **PASS** on lane B
(build/fc01/corp3; double-run byte-equal; source sha `2263d38f…`; docs § 8 + § 1 row written).
Rev1 measured the `> 0` refusal (corp1), rev2 the SILENT `/365` low-byte miscompile (corp2,
narrowed to `compiler` by the .COM byte run) — both `my-gap`, kept as written; NO expectation
re-derived. REMAINING NOW: (a) run `python3 tools/e2e_gate.py` (compile tier) and record ACTUALS
as printed; (b) explicit-path commit (`spec/functional/tests/WKDAY-00.PLI`, `WKDAY-00.json`,
`docs/functional-results.md`, `LEARNINGS.md`, this file); (c) refresh+attest the checkpoint
(`/handoff finalize` or `handoff_finalize`), renew at the safe boundary; (d) proceed to HAMM-00
(Hammurabi, program 2) per the exact procedure below, applying the corpus rule: literal divisors
≤ 127, ordered-compare constants ≥ 1 (LEARNINGS 2026-11-02 CORPUS hop 2). Details in
LEARNINGS 2026-11-02 CORPUS hop 2.

| # | program | original | corpus id | note |
|---|---|---|---|---|
| 1 | Weekday | BASIC | `WKDAY-00` | START HERE — design fully derived, see § "WKDAY-00 exact" below |
| 2 | Hammurabi | BASIC | `HAMM-00` | |
| 3 | Hangman | BASIC | `HANG-00` | |
| 4 | Amazing | BASIC | `AMAZ-00` | maze: 2-D grid ⇒ AGG.MULTIDIM is REFUSED; flatten or record |
| 5 | Tic-Tac-Toe | BASIC | `TICT-00` | two upstream listings (tictactoe1/2) |
| 6 | Life | BASIC | `LIFE-00` | |
| 7 | Dhrystone | Pascal | `DHRY-00` | upstream is a .SHAR; do NOT execute it |
| 8 | FFT | PL/I (Rosetta) | `FFT-00` | `pli/FFT-reference.pli` |

Sources: `build/functional/fc01-sources/` (ignored working state; operator's
`fc01-fetch-sources.sh`; `sha256sum -c SHA256SUMS` rc=0 measured 2026-11-02). They are RESEARCH
COPIES: read `NOTES.txt` — the BASIC URLs are a moving branch and `dhry-pascal.shar` must never be
run. Upstream bytes are NEVER copied into tracked files: each program is an ADAPTATION with
`provenance.origin: "third-party"`, the upstream URL and licence recorded in `provenance.note`,
and the algorithm re-expressed in PL/I-80.

EXACT PROCEDURE per program (reuse the harness AS IT STANDS — no new infrastructure, no runner
edits):
1. Read the upstream listing; write the behavioural spec FIRST (fixed inputs, complete expected
   console stream) into `spec/functional/tests/reference.py:<id>` — derived, never captured (L3).
2. Write `<ID>.PLI`: CRLF, `^Z`-terminated, ≤ 71 columns, header comment naming the adaptation and
   its upstream; keep every line inside the measured 79-col PLILIB wrap; obey README § 7 and the
   pinned-refusal list already in the Batch-A notes.
3. Write `<ID>.json` (schema `pli80-functional/1`; Lane B; `capabilities` = real COVERAGE ids, no
   forbidden/REFUSED/DIVERGENT/UNTESTED rows). Set `console_input` when the program reads — the
   harness already supports it (`^Z` default; `##SEND`).
4. Run `python3 tools/functional_runner.py --lane B --tests <ID> --evidence build/fc01/corp<N>
   --json-out build/fc01/corp<N>/records.json`; record ACTUALS (verdict, stage, attribution, byte
   sizes) — PASS/FAIL/BLOCKED/UNKNOWN as measured, never laundered. Where the harness CANNOT test
   the program adequately, RECORD the limitation in `docs/functional-results.md` and move on; do
   not extend the harness.
5. Update `docs/functional-results.md` (new section per batch) + § 1 rows; run the fast tier
   `python3 tools/e2e_gate.py` (compile tier only — runtime/link-run stay delegated to rune-ci,
   and existing CI results do NOT cover new corpus programs unless explicitly added there).
6. Commit explicit paths only; renew at the safe boundary per `handoff.config.json`.

**WKDAY-00 exact (first program; everything needed is already derived — LEARNINGS 2026-11-02
override section, PROPOSED entry; read that entry, do not re-derive from scratch):**
1. `spec/functional/tests/WKDAY-00.PLI`: CRLF, `^Z`, ≤ 71 cols; header comment naming
   `build/functional/fc01-sources/basic/WEEKDAY.bas` as the adapted original (upstream URL
   `https://raw.githubusercontent.com/coding-horror/basic-computer-games/main/95_Weekday/weekday.bas`,
   sha256 `ccb9a9e5…`); `wkday00: procedure options(main);`; declare all FIXED scalars +
   `t(12) fixed` (month table 0,3,3,6,1,4,6,2,5,0,3,5 literal-assigned — no `READ`/`DATA`, no
   `INITIAL`); TODAY=3/24/1979, TARGET=7/16/1969, both FIXED **non-negative** operands only; every
   `INT(x/n)` becomes `x / n`; `A - (A/7)*7` for mod-7 exactly as the original does it; the
   `M > 2` / leap-adjust branch (`T1 = Y - (Y/4)*4`) and the `B = 0 → 7` fix-up verbatim; the
   was/is/will-be compare `(Y1*12+M1)*31+D1` vs `(Y*12+M)*31+D` — keep operands small enough for
   FIXED BINARY(15) or the multiply overflows: use it only if measured to fit, else replace with
   the equivalent sign-of-difference test and RECORD the substitution; day name by 7 `if b = n`
   branches printing literals; Friday-the-13th literal branch; the pre-1582 refusal literal; the
   30-month/365-year age arithmetic (`A8 = I5*365 + I6*30 + I7 + I6/2`) and the three `.35/.17/.23`
   blocks as `K1 = A8*F/100` with integer F literals 35/17/23 (NO fractional literals — refused).
   First output statement `put skip list(...)` ⇒ expectation starts `""`; end with a non-SKIP PUT
   so no trailing `""`. Every line ≤ ~60 raw cols.
2. `reference.py:wkday00` — Python port ALREADY verified against `datetime` (3/24/1979 Sat,
   1/1/1970 Thu, 2/29/1980 Fri, 12/31/1999 Fri, 7/4/1776 Thu); derived values for the chosen pair:
   `b = 4` → WEDNESDAY (7/16/1969 real weekday is Wednesday — agrees), WAS (1969 < 1979),
   age 9 y 8 m 8 d, `A8 = 3537`, SLEEP 3/4/22, EAT 1/7/26, PLAY 2/2/23, retire 2034.
3. `WKDAY-00.json`: `provenance.origin: "third-party"`, author "DRPLi FC-01 corpus — adaptation of
   the BASIC Weekday listing (coding-horror/basic-computer-games 95_Weekday, public-domain-era
   source; license UNVERIFIED — record in note)", note naming `build/functional/fc01-sources/
   URLS.tsv` + `SHA256SUMS` (`ccb9a9e5…`); `capabilities` from SUPPORTED rows only (e.g.
   `AGG.ARRAY_1D_FIXED`, `AGG.VAR_INDEX_LADDER`, `LOOP.DO_TO_BY`, `IO.PUT_LIST_FIXED`,
   `IO.PUT_SKIP`, `EXPR.REL_FIXED_EQ_K`, `DECL.FIXED_BIN15`); link_target `WKDAY00`; sha256 of the
   committed .PLI bytes.
4. `python3 tools/functional_runner.py --lane B --tests WKDAY-00 --evidence build/fc01/corp1
   --json-out build/fc01/corp1/records.json` → record ACTUALS as executed; then docs
   `docs/functional-results.md` § 8 + § 1 row; `python3 tools/e2e_gate.py` (compile tier only).
5. Documented unsupported/removal list for WKDAY-00 (must appear in the spec `notes` AND docs
   § 8): console `INPUT` (×2) replaced by fixed declared dates; `DEF FNA/FNB` inlined (built-ins/
   function refs refused); `READ`/`DATA` → literal assignments; `TAB()` positioning and the
   banner `PRINT`s dropped (no column PUT — `FILE.PUT_POSITION`/counted EDIT refused); `GOTO`/
   `GOSUB` structure re-expressed as `IF`/`DO` (goto is supported, but the port is clearer); the
   original's 30-day-month/365-year calendar convention KEPT as declared behaviour, not corrected.

Standing constraints: NO `ocaml/` changes; goldens/`artefacts/`/`oracle/disks/` untouched; no push;
no new CI framework; no mass documentation cleanup; operator `handoff.config.json` stays UNSTAGED;
compiler-gap findings are classified `my-gap`/`dr-refuses`/`unmeasured` (PROTOCOL #3) and recorded
without promoting anything to `spec/CLAIMS.md` (ledger still ends at C352) — a functional run is not
a DR claim.

(Superseded hop-5 instruction, kept as written per PROTOCOL #2: FC-01 hop 4 PARTLY DONE. LANDED: Batch-B REV2 `a5815a8` (FLT-01 direct `(a+b)=6.5` refuses
verbatim 'computed FLOAT operand in a comparison is unsampled'; BUILTIN-00 length-first refuses
'int subset'; both COMPILE FAIL attr=compiler at build/fc01/batchB-rev2; docs § 7 + § 1 rows;
LEARNINGS hop-4 section carries the full file-I/O survey — READ IT FIRST).
EXACT NEXT (hop 5):
(1) Harness extension tools/functional_runner.py — design is in LEARNINGS 2026-11-02 hop 4
(PROPOSED): `stage_files` top-level field + `expected.file_expectations` implementation,
SOURCE sha pin, DERIVATION two-way check (reference.py `derive()` must accept the file funcs
— return a latin-1 string; json round-trips it), export in _run_lane_b AFTER RUN and BEFORE
run.cleanup() into per-seq subdir (cpmwork export refuses clobber), ASSERT byte-compare,
Lane-B-only validation, README § 3/§ 4 amendments, hostile-suite case C17 (FakeRun stub
export returns a PATH — pin calls via run.calls), suite self-count printed.
(2) FILE-00 (output; E16D shape, title 'F00OUT DAT', derived payload per [C295]/[C300]/[C280],
<128 B, 0x1A pad) + FILE-01 (input; dcl inf file → stage INF.DAT fixture `7\r\n8\r\n` + ^Z,
gets print X1/X2) specs/programs/derivations; run lane B → build/fc01/fileAB; docs § 8.
(3) ONUNIT-00 ONLY AFTER a pre-registered fc01-fileio oracle round measures DR named-file
ENDFILE firing (hop-2 pattern: probes FCFO* + HYPOTHESES + BASELINE-MINE + linkrun.py
STAGE_IN/EXPORT_OUT entries committed BEFORE any DR PLI.COM call; claim C353+; results in
spec/lab-evidence/fc01-fileio/). Named-file ON firing is UNMEASURED — do NOT derive an
expectation without it.
Constraints unchanged: NO ocaml compiler changes; goldens/artefacts untouched (new fc01-fileio
goldens would be ADDITIVE); explicit-path commits; no push; operator handoff.config.json stays
unstaged; cap per handoff.config.json.
## Verified milestones (provenance: `docs/history/README.md`; evidence: `spec/lab-evidence/`)

- E2E-48/P1 — 24/24 probes byte-identical + registered, claims C309–C316, gate 1098/0: `992ccad`.
- E2E-48/P2c CLOSED — arms `14c7321`…`e21281a` era, RETIRE promotions, claims C317–C320,
  FULL GATE 1109/0 negative 182/182: `f67cc6d`; COVERAGE rows + appends: `ef0a198`.
- E2E-48/P2d — run 1 botched (>72-col comments; kept `67bf83c`), wrap `60a2c06`, run 2 10/10
  `d28ff5e`; claims C321–C326 `aa4b5b4`; six arms `6545b5d`/`6491981`/`a72ce43`/`18a06c0`/
  `1e8acb2`/`e21281a`; registration + FULL GATE 1120/0, negative 181/181, census 15/0/26/0,
  INVENTORY 1301: `adbfa2a`; COVERAGE 113 rows 0 errors: `218b474`.
- E2E-48/P2e round 5 — pre-registration `421656a` committed BEFORE the oracle; one run
  7 ok / 8 (E48E6 `BIT REQ` = dr-refuses; P-E6 MISS kept in RESULTS §1); goldens + RESULTS
  `e2b77ba`; lowering arms 1–3 `d18c6ab`/`bab0d16`/`e49902a` (arm-3 spec archived in
  `docs/history/2026-10-31-p2e-arm3-closed.md`).
- E2E-48/P2e CLOSED — arm 4 `046046a`, arm 5 `c215ea0`, step 6 `809af8d`+`0e64c8b`, docs
  `0749fa6`; claims C327–C332, inventory 1127, coverage 118 rows 0 errors; FULL compile-tier
  GATE rc=0 ACTUAL 1127/0 (neg 181/181, div 9/9, census 15/0/26/0, prose clean) measured at
  `0749fa6` 2026-10-31; closing prose archived in `docs/history/2026-10-31-p2e-closed.md`.
- E2E-49/P1 CLOSED — operand-inverted FIXED compares (member LEFT of literal): pre-registration
  `9b3d860` before the oracle; run 4 ok/4; arms `fee935e`/`b044b7c`; claims C333–C336 + labelled
  C330 CORRECTION; registration panel 1131, coverage 122 rows; FULL GATE rc=0 1131/0 (neg 181/181,
  div 9/9, cov 122/0/0, census 15/0/26/0, prose clean) measured at `0a8ceff`; archive
  `docs/history/2026-11-01-e49p1-closed.md`.
- E2E-49/P2 CLOSED — member-vs-member FIXED TEST compares: pre-registration `3bd9417` before the
  oracle; run 5 ok/5; arm 1 `b1e9221` (stacked parking + equal-extent collapse); claims C337–C341;
  registration panel 1136, coverage 125 rows 0 errors (`0abf1c1`/`8c1d2ee`/`d5983e8`); FULL GATE
  rc=0 **1136/0** (neg 181/181, div 9/9, cov 125/0/0, census 15/0/26/0, prose clean) measured at
  `d5983e8`; archive `docs/history/2026-11-01-e49p2-closed.md`.
- E2E-49/P3 CLOSED — composite FIXED/TEST bank (equal-attribute collapse in BOTH literal
  templates, qualification invisible, over-extent literal-LEFT, ordered relations):
  pre-registration `3659f5d` before the oracle; run 14 ok/14, NO dr-refuses; arms
  `a540fa7`/`0a1b80c`/`cde3258`; claims C342–C347 + labelled corrections at C335–C338 and
  the citation fix at C346 (`4df35bb`); registration panel 1150, coverage 129 rows 0 errors
  0 warnings (`4b51bc0`/`8d3b024`/`8771e1e`); FULL GATE rc=0 **1150/0** (neg 181/181,
  div 9/9, cov 129/0/0, census 15/0/26/0, prose clean) measured at `4df35bb`, recorded
  `1f611f5`; two-generation archive `docs/history/2026-11-01-e49p3-closed.md`.

- E2E-49/P4 CLOSED — composite FIXED/TEST bank (ordered relations with a LITERAL on BOTH `?SCCCM` literal templates with the ORDER-law rekey, qualification invisibility transferred, the complete unequal-extent relation matrix NO-ARM, `^( )` on the complement object):
  pre-registration `328eb3f` before the oracle (BASELINE-MINE binary `398fa2c`); run 24 ok/24, NO dr-refuses (18 my-gap, 6 exact); arms `c515377`/`ec904c1`/`47c2194`; claims C348–C351 +
  labelled corrections at C335/C337/C344/C346 (`9c42f3b`) and the WORDING correction at C348 (`5b0ccde`); registration panel 1174, coverage 133 rows 0 errors 0 warnings
  (`cc43963`/`dbaf004`/`5aeac87`); FULL GATE rc=0 **1174/0** (neg 181/181, div 9/9, cov 133/0/0, census 15/0/26/0, prose clean) measured at `5b0ccde`, recorded `882f77c`;
  four-generation archive `docs/history/2026-11-01-e49p4-closed.md`.


- E2E-50/P1 CLOSED — functional dashboard (evidence-infrastructure audit; capability taxonomy 30 rows validated; 68-program inventory in 3 origin classes; deterministic read-only dashboard + 30 tests; generated docs/functional-status.md views A–E incl. ranked §E candidate shortlist; stale README rolling status replaced; labelled LEARNINGS corrections incl. RUNTIME 71-names falsification). Deliverables `4cad695`; no compiler/oracle/gate run; no scientific byte.

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
- **Renewal chain:** the E2E-48 phase chain closed at its configured cap; its state file is
  archived under `.pi-guard/archives/` and a new session starts a fresh count per
  `handoff.config.json` — the config and `/guard status` are authoritative for enablement,
  autoRenew and cap; this file quotes no numbers.

## Verified evidence

The FULL compile-tier gate rc=0 at HEAD `545dcf1` with ACTUALS AS PRINTED (byte panel 1174
byte-exact / 0 fail of 1174; negative 181/181, E46K14 `[dr-refuses]` UNMOVED; divergence 9/9;
coverage 133/0/0; census 15/0/26/0 UNCHANGED; prose 5 active clean) was MEASURED by the
step-8 session and recorded at `d648bcd` — NOT re-run by this docs-only close (the mission
required no compiler/oracle/gate/emulator run to close). Measured by THIS closing session
(2026-11-02): HEAD `e7664ed`, tree clean apart from the operator's `handoff.config.json`
edit; checkpoint g131 **current** via replay of the guard's strip+rstrip SHA-256 prose law;
the 23 close-archive blocks re-extracted from `459f51e`/`a6163ef`/`149c6e2`/`690c3a1`/
`218c9be`/`ec9d396`/`545dcf1`/`d648bcd`/`68831ff`/HEAD and byte-compared — **23/23
BYTE-EXACT**; every line lost by any superseded generation verified present verbatim in the
archive. Round evidence: `spec/lab-evidence/e2e50-p2/{PLAN.md,step6/RESULTS.md,
step7/RESULTS.md,REPORT.md}`, `spec/functional/tests/`, ignored evidence roots under
`build/functional/`; earlier rounds `spec/lab-evidence/e2e48-*/`, `e2e49-p*/`; closed-round
records: `docs/history/`.
<!-- guard:begin checkpoint -->
checkpoint-schema: 3
checkpoint-generation: 483
checkpoint-id: g483-1e5d028586db
checkpoint-kind: manual
content-delta: new
readiness: attested
guard-level: 4
checkpointed: 2026-11-07T04:49:48.937Z
source-goal: 730790b648a1e1d14b76243cfe8bc17eea2ba9cd8527f204f9c8d4dbcc527c9d
source-progress: 38ca496ba093856e0117dc15040df9bf2dfa6a935f307e2e1da38319388706b3
source-handoff: f2fb46a3aaaf2a0109ec98b6b4a169cf485081aaadf08f62f6e67a0cb4133efb
source-learnings: 4a9ecb8862f0a0d18af7ad4f5d19edbecba8fa80d12a06885046a58f62ecabfb
source-config: 43186947fdaf3f3b9f425f8ce1b144a8227ce1d7bec2b7aeafb32e9f0572dea8
next-action: ` steps (8a)-(8c),(9)):** FULL gate rc=0 DIRECT → `build/gate-e52p14-reg.log` (expect 1300/0, 187/187, 9/9, **145 rows**, census 15/0/26/0, prose 5 — ONLY the gate runs the negative panel); RESULTS §P3-14 (parity table + E520E row; H-2 near-miss VERBATIM; probe-defect + `e52p14b` provenance; LOAN2 **121→147** never-fix; byte-tier); PLAN §5 row INSIDE the table anchored by LINE NUMBER + §P3-14 **CLOSED**; then **P3-15** on the ACTUAL line-147 blocker `PUT FILE(OUTPUT) EDIT of the FORMAL A` (ZERO-oracle pre-audit of LOAN2.REL `053F-0542` + `E52PF` precedents BEFORE any probe; verify `E521*`/`e52p15` unused; pre-register PLAN+probes+LEARNINGS by EXPLICIT paths before any oracle call or `ocaml/` byte; never-predict), marathon through P3-19 (slice 5 of ≤8). Ledger ENDS **C372** (195 headers); inventory **1300/187**; coverage **145/95**; last full gate rc=0 `build/gate-e52p13-reg.log` (P3-14 gate OWED); LOAN2 UNMODIFIED sha `7be23ba3…` rc=2 NO `.REL`; all inherited constraints VERBATIM (goldens NEVER re-derived, POSITIONAL FRESH paths, `eval "$(opam env)"` every shell, config NEVER staged, no push, rc DIRECT, never glue `rm`, byte-tier, never parallelize dependent bash calls); durables `64696068` + this block; chain 01a1b2d5 renewal 4/12 scheduled, cap 12.**

0a-marathon-11. **P3-14 hop 3 LANDED (session 01a1b407, chain 01a1b2d5 renewal 2/12; ZERO new oracle; goldens NEVER touched/re-derived; config NEVER staged; no push; rc DIRECT; byte-tier): guard g473 attestation lines committed VERBATIM `9556c6f8`; ARM `65da9bd1` = parser.ml CALL arm parses target as PLAIN identifier + suffix_chain NEVER consulting builtins; expression `primary` + bare-stmt arm + codegen guard UNCHANGED (E520E MEASURED dr-refuses bare `summary();` — BY-NAME boundary honest); armed binary sha256 `b88e7b023027e2eeba1b6f49dc0815cb25e14f20269074a637a7c1f84f3c72e2` deterministic (default == fresh `_build-p314b`), histogram codegen 68/total 124 == baseline; whole-file cmp E520A/B/C vs `golden/e52p14b/` + E520D vs `golden/e52p14/E520D` 4/4 rc=0 FRESH POSITIONAL `build/p3-14b/arm-out/`; E520E rc=2 BY NAME guard VERBATIM; sweep 174/0 PRE + **178/0 POST**-registration (count-moves-with-inventory prediction HIT); markers 14/14 + E520E marker RE-MEASURED rc=2 CRLF+bare-^Z; DEC 64/0; divcheck 9/9; LOAN2 UNMODIFIED sha `7be23ba3…` rc=2 NO .REL — ACTUAL next blocker VERBATIM **line-147** `PUT FILE(OUTPUT) EDIT of the FORMAL A … [TBD] (line 147)` (never-predict HELD: my candidate line-160 did NOT fire; NEVER fix); REGISTRATION `9a31509c`: SPECIMENS +4 E520A..D measured-byte comments, E520E REJECTS+NEG_META dr-refuses (`SYNTAX ?` line 14 BOTH passes, header-clean UNCONFOUNDED), inventory **1300/187 EXACT**, census OWN path 15/0/26/0 msg MOVED VERBATIM NOTHING fixed. Durables `6369f65f`. SUCCESSOR CONTRACT = `LEARNINGS.md` § "P3-14 hop 3" steps **(6)–(9) ONLY**: C372 measured-bytes-only BEFORE ANY COVERAGE touch (bullets (a)-(g) drafted there); coverage ADJUDICATE EXTEND row 85 `PROC.CALL_COPYIN` (EXACT:40) vs justified NEW row + SAME-change IDS (NEVER coverage_gen.py; 15 cols FIRST NON-COMMENT row); FULL gate rc=0 DIRECT → `build/gate-e52p14-reg.log` (expect 1300/0, 187/187, 9/9, census 15/0/26/0, prose 5 — only the gate runs the negative panel); RESULTS §P3-14 (H-2 packed-name-record 3-byte near-miss VERBATIM; probe-defect + e52p14b provenance; LOAN2 121→147 never-fix; byte-tier) + PLAN §5 row INSIDE table by LINE NUMBER + §P3-14 **CLOSED**; then P3-15 on the ACTUAL line-147 blocker (evidence-first ZERO-oracle pre-audit of LOAN2.REL 053F-0542 + E52PF precedents BEFORE any probe; NEVER fix in P3-14), marathon through P3-19 (slice 5 of ≤8). TOOL LESSON accepted: never PARALLELIZE bash calls when a later command depends on state an earlier creates (raced mkdir → misleading Sys_error rc=2; suspect harness before compiler). Ledger ENDS C371 (C372 owed); armed binary `b88e7b02…` == tree; all inherited constraints VERBATIM (goldens NEVER re-derived, POSITIONAL FRESH paths, `eval "$(opam env)"` every shell, config NEVER staged, no push, rc DIRECT, never glue `rm`, byte-tier); chain 01a1b2d5 renewal 3/12 scheduled, cap 12.**

0a-marathon-10. **P3-13 CLOSED at hop 12 (session 01a1b272, chain 01a1b1b4 renewal 12/12 = CAP; ZERO new oracle; goldens NEVER touched; config NEVER staged; no push; rc DIRECT; byte-tier): guard g467 blocks committed VERBATIM d2264d96; build rc=0 binary 6db44394db5f09ad82cdb8e05f8fc92b298f77305301870de09e2485764bdfd2 == tree. (C') N52_DEC_FORMAL_PUT retired HONESTLY to POSITIVE NG39 — adjudication re-measured FIRST-HAND (source sha de1e56e8… 253B, pli80c rc=0 384B code=92 data=15, cmp rc=0 vs KEPT golden sha 3197de7a…, .PRN NO ERROR(S) both passes; gate rows deleted with retirement comments; probes/NG39.PLI VERBATIM; --update-inventory 1295/187->1296/186 exact; census 42f3f659 15/0/26/0 UNCHANGED LOAN2 msg did NOT move; DATED ADDENDUM bullet to C371 016e58e0; row PROC.CALL_DEC_ACTUALS +NG39 EXACT:8 c1059d46 coverage_check rc=0 144/0/0 SUPPORTED 94; markers 14/14, DEC 64/0, divcheck 9/9; FULL GATE rc=0 DIRECT OVERWROTE build/gate-e52p13-reg.log: 1296/0,186/186,9/9,144 rows,census 15/0/26/0,prose 5 — every number hit). (D) RESULTS §P3-13 + PLAN §5 row + §P3-13 CLOSED 79cd5ef0 (8/8 cmp parity; H-1..H-8 ALL CONFIRMED ZERO §4 misses; gate-found lesson VERBATIM: ONLY the full gate runs the negative panel; LOAN2 117->121 VERBATIM re-measured call summary(); NEVER fix; byte-tier-only; tool lesson: §5 row mis-anchored into §P3-12 trailer first attempt, caught by first-hand line-number inspection pre-commit). SUCCESSOR CONTRACT = LEARNINGS § "P3-13 hop 12" (E) ONLY: P3-14 on Line-121 call summary(); — WHY first-hand ZERO oracle (summary IS a simple name: inspect CALL-target guard + zero-arg internal-proc cs/entry bookkeeping + existing arity-0 witnesses in KEPT goldens BEFORE proposing); verify E520*/e52p14 names unused; pre-register PLAN §P3-14+probes+LEARNINGS committed by EXPLICIT paths BEFORE any oracle call/ocaml byte; then ONE campaign e52p14, goldens VERBATIM first, arm measured shapes only, full validation incl FULL GATE BEFORE CLOSE, register from 1296/186, C372 measured-bytes-only BEFORE COVERAGE, coverage, gate rc=0 build/gate-e52p14-reg.log, RESULTS+PLAN §5+CLOSED; marathon through P3-19. CHAIN 01a1b1b4 EXHAUSTED (12/12 cap): renewal NOT available — this session closes via handoff_finalize; NEW chain needs operator to archive+reset ignored .pi-guard/renewal-state.json. All inherited constraints VERBATIM (goldens NEVER re-derived, POSITIONAL FRESH paths, eval "$(opam env)" every shell, config NEVER staged, no push, rc DIRECT, never glue rm, byte-tier); armed binary 6db44394db5f09ad82cdb8e05f8fc92b298f77305301870de09e2485764bdfd2 == tree.**

0a-marathon-9. **P3-13 hop 11 PART LANDED (session 01a1b25c, chain 01a1b1b4 renewal 11/12→12 LAST; ZERO new oracle; goldens NEVER touched; config NEVER staged; no push; rc DIRECT; byte-tier): guard g465 VERBATIM `d615a96`; build rc=0 binary `6db44394…`==tree. (A) C371 `1d1885b9` measured-bytes-only BEFORE any COVERAGE touch — ledger ENDS **C371 (194 headers)**; every cited byte re-verified FIRST-HAND vs KEPT goldens (ZA/ZB 32 B product blocks CODE 006F, ZC/ZD literal cells `50 01 00 00 00`/`00 01 00 00 00` + desc `000A->0000` reloc, ZE vector `05 00 18 00 00 00`, ZF `31 00 37 00 3D 00 43 00 49 00` + deref-PUT `2A 4F 00…`, CHAIN-ADDR ZA 002A→code@005A / ZF 00AA→code@00D2) + **DATED correction of BOTH C093 errors VERIFIED** (DECPOLY 3 goldens sha `a51a36c2…` DATA max `004E`, descriptors→variables 0030/38/40, `5.67` ONLY R2038 SOURCE store; 5 B formal-width cells; literal-pool law STANDS). (B) coverage `afb95163` NEW row **`PROC.CALL_DEC_ACTUALS`** (EXACT:7 E52ZA..ZF+NG18, MEASURED [C371]) + SAME-change IDS line + DATED correction of STOR.DEC_SCALE_ASSIGN stale clause; coverage_check rc=0 **144 rows 0/0 SUPPORTED 94**; prose rc=0. (C) FULL gate **rc=1**: `NEG-FAIL N52_DEC_FORMAL_PUT compiled silently` — adjudicated MEASURED this session: inline source CRLF+bare-^Z → rc=0 384 B **cmp rc=0 vs KEPT `golden/negpanel1/NG39/NG39.REL`** (sha `3197de7a…`) = exact N33→NG18/N35→NG20 retirement class; LESSON accepted: sweep/markers never run the negative panel — ONLY the gate does. SUCCESSOR contract = `LEARNINGS.md` § "P3-13 hop 10/11" steps **(C')–(E) EXACTLY**: retire N52→NG39 (probes/NG39.PLI VERBATIM sha `de1e56e8…`; gate rows deleted with retirement comments; SPECIMENS +NG39 golden KEPT NEVER re-derived; inventory 1295/187→**1296/186**; census 15/0/26/0 UNCHANGED LOAN2 msg MUST NOT move; DATED ADDENDUM bullet to C371; row +NG39 EXACT:8; markers 14/14, divcheck 9/9, DEC regressions; gate rc=0 DIRECT OVERWRITE `build/gate-e52p13-reg.log` expect 1296/0,186/186,9/9,144 rows); RESULTS §P3-13 + PLAN §5 + **CLOSED**; P3-14 Line-121 `call summary();` WHY-first-hand ZERO oracle, pre-register PLAN §P3-14+probes BEFORE any oracle/`ocaml/` byte; marathon through P3-19. **CHAIN EXHAUSTED: this renewal is 12/12 cap 12 — the successor CANNOT renew; it must close via `handoff_finalize`; a new chain needs the operator to archive+reset ignored `.pi-guard/renewal-state.json`.** All inherited constraints VERBATIM (goldens NEVER re-derived, POSITIONAL FRESH paths, `eval "$(opam env)"` every shell, config NEVER staged, no push, rc DIRECT, never glue `rm`, byte-tier); armed binary `6db444394…` NO — `6db44394db5f09ad82cdb8e05f8fc92b298f77305301870de09e2485764bdfd2` == tree.**

0a-marathon-8. **P3-13 hop 10 PART LANDED (session 01a1b249, chain 01a1b1b4 renewal 10/12; ZERO oracle; goldens NEVER touched; config NEVER staged; no push; rc DIRECT; byte-tier): guard g462 VERBATIM `8c9bf60`; markers 14/15 — ONLY retired N33 fails its old row (harness .REL cmp rc=0 vs KEPT NG18 golden = second witness); REGISTRATION `39bb9a0` — SPECIMENS +6 E52ZA..ZF measured-byte comments + honest N33→NG18 retirement (REJECTS+NEG_META deleted, golden KEPT NEVER re-derived), inventory **1295/187 exact**; CENSUS `59be109` rc=0 counts 15/0/26/0, LOAN2 msg MOVED VERBATIM to Line-121 `codegen: CALL target is not a simple procedure name [TBD] (…line 121)` = `call summary();`, NEVER fix; SWEEP post-reg 174/0 FAILS-0 (168+6 prediction HIT; count moves with INVENTORY rows, FAILS 0 binding). SUCCESSOR contract = `LEARNINGS.md` § "P3-13 hop 10 PART LANDED" steps (A)–(E) EXACTLY: (A) **C371 measured-bytes-only BEFORE ANY `spec/COVERAGE.tsv` touch + DATED both-errors C093 correction** (false DECPOLY `*A(005A)=5.67` — DATA max 004E; 2-byte width → 5 B formal-width `00 01 00 00 00`); (B) coverage row/extension (NEVER coverage_gen.py, 15 cols FIRST NON-COMMENT row, manual_ref `pNN[:§X.Y][=phrase]`|`NONE:`, SAME-change IDS, coverage_check adjudicates); (C) FULL gate rc=0 DIRECT → `build/gate-e52p13-reg.log` (1295/0, 187/187, 9/9, census 15/0/26/0, prose 5); (D) RESULTS §P3-13 + PLAN §5 row + §P3-13 **CLOSED**; (E) P3-14 on Line-121 `call summary();` — WHY first-hand (summary IS a simple name; inspect cs/entry bookkeeping), pre-register PLAN §P3-14 + probes BEFORE any oracle call/`ocaml/` byte; marathon through P3-19. All inherited constraints VERBATIM (goldens NEVER re-derived, POSITIONAL FRESH paths, `eval "$(opam env)"` every shell, config NEVER staged, no push, rc DIRECT, never glue `rm`, byte-tier only); ledger ENDS C370; armed binary `6db44394db5f09ad82cdb8e05f8fc92b298f77305301870de09e2485764bdfd2` == tree; chain 01a1b1b4 10/12 cap 12.**

0a-marathon-7. **P3-13 hop 9 VALIDATION LANDED (session 01a1b23b, chain 01a1b1b4 renewal 9/12; ZERO oracle; goldens NEVER touched; config NEVER staged; no push; rc DIRECT; byte-tier): histogram repair `e971f3e` (ONLY true new warning = dead zip3; predecessor's W9/W39 was misleading incremental output — FALSIFIED) → codegen 68/total 124 == baseline EXACTLY; TWO measured repairs `9b81ed0` (const_cells DEC-formal demand `dec_pool_bytes pf` — C152 demanded-2/allocated-5; deref-DEC PUT `LHLD/MVI A,p/?DLDOP` armed by E52ZF golden 00ED-00F2, old refusal text retired to comment VERBATIM) → E52ZA..ZF 6/6 whole-file cmp rc=0 FRESH POSITIONAL `build/p3-13/arm-out2/` on deterministic binary `6db44394db5f09ad82cdb8e05f8fc92b298f77305301870de09e2485764bdfd2`; sweep 168/0 (contract 159 STALE — inventory rows moved; FAILS 0 binding); DEC regressions 64/0; divcheck 9/9; `probes/NG18.PLI` sha `20006b0c…` cmp rc=0 vs KEPT golden → N33→NG18 retirement PROVEN (refusals 188→187 owed at registration); LOAN2 ADVANCED VERBATIM past 117 to ACTUAL Line-121 blocker `codegen: CALL target is not a simple procedure name [TBD] (only `CALL id` / `CALL id(args)` / bare `id;` have a DR lowering sampled; line 121)` = `call summary();` — NEVER fix, §6 never-predict HELD. SUCCESSOR contract = `LEARNINGS.md` § "P3-13 hop 9" STILL OWED (1)–(7) EXACTLY: markers harness; register from 1288/188 (+6 ZA..ZF + NG18 → expect 1295/187, `--update-inventory`, `git diff --cached --stat`, census OWN path 15/0/26/0 LOAN2 msg MOVES VERBATIM); C371 measured-bytes-only BEFORE COVERAGE + DATED both-errors C093 correction; coverage row/extension (NEVER coverage_gen.py, 15 cols FIRST NON-COMMENT row, manual_ref `pNN[:§X.Y][=phrase]`|`NONE:`, same-change IDS line); FULL gate rc=0 DIRECT → `build/gate-e52p13-reg.log`; RESULTS §P3-13 + PLAN §5 row + CLOSED; BEGIN P3-14 on Line-121 `call summary();` — investigate WHY it refuses first-hand (summary IS a simple name — likely cs/entry bookkeeping) evidence-first, pre-register PLAN §P3-14 + probes BEFORE any oracle call/`ocaml/` byte; marathon through P3-19. All inherited constraints VERBATIM (goldens NEVER re-derived, POSITIONAL FRESH paths, config NEVER staged, no push, rc DIRECT, never glue `rm`, byte-tier only, `eval "$(opam env)"` EVERY shell); chain 01a1b1b4 9/12 cap 12.**

0a-marathon-6. **P3-13 hop 8 PART LANDED (session 01a1b225, chain 01a1b1b4 renewal 8/12→9; ZERO oracle; goldens NEVER touched; config NEVER staged; no push; rc DIRECT; byte-tier): recovery + g456 VERBATIM `afff5e0`; design pinned `5f29ee5`; ARM EDITS COMMITTED `13e53be` — bind `cs_dec` single allocation authority (DEC expression temps sized `bytes_of` callee scalar RTdec row; array-named/recursive/attr/external excluded), codegen admits ONLY the measured shapes: `Enumber` literal → `dec_pool` pre-scaled FORMAL-width cell + static descriptor reloc, ZERO code (E52ZC/ZD/NG18); `Ebinary(Mul, plain-DEC-auto, plain-DEC-auto)` → armed `dec_push` via ONE forward slot `dec_actual_mat` (installed after `dec_push`; lower_hl/dpush are SEPARATE chains — never duplicate the law), terminating `LXI H,*A(temp)/MVI A,pf/?DSTOP`, C370-window shift kept (ZA/ZB/ZF); `dec_pool` MOVED before `lower_hl` (vk_dec_at precedent); Line-N BY-NAME refusal VERBATIM otherwise, substring `FIXED DECIMAL formal is unproven` intact. Default build rc=0 binary `26ed7ccf54e6bf77…` (supersedes pre-arm `6a4c6c11…`). NOT YET DONE: histogram repair (NEW Warnings 9 missing-record-field + 39 unused-rec vs baseline 68/124 — fix FIRST, full fresh `--build-dir`, `eval "$(opam env)"` every shell), cmp ZA..ZF FRESH POSITIONAL, sweep 159/0, markers + N33→NG18 retirement iff cmp rc=0 golden KEPT (refusals 188→187), DEC 64/0, divcheck 9/9, LOAN2 never-predict, register from 1288/188, C371 measured-bytes-only + DATED BOTH-errors C093 correction, coverage extension, gate `build/gate-e52p13-reg.log`, RESULTS+PLAN §5+CLOSED. SUCCESSOR contract = `LEARNINGS.md` § "P3-13 hop 8 PART LANDED" steps (0)–(7) EXACTLY; marathon through P3-19. All inherited constraints VERBATIM (goldens never re-derived, POSITIONAL FRESH paths, `git diff --cached --stat`, config NEVER staged, no push, rc DIRECT, never glue `rm`, byte-tier only); chain cap 12, 9/12 used.**

0a-marathon-5. **P3-13 hop 6 LANDED (session 01a1b201, chain 01a1b1b4 renewal 6/12→7; ZERO oracle; goldens NEVER touched; config NEVER staged; no push; rc DIRECT; byte-tier): step (0) COMPLETE — g450 blocks at `f281500`, e52p12 summary/transcripts additive VERBATIM `ed8f1a8`; first-hand re-verification + durables `c9d1a27`. NEW accepted correction: NG18 DEC-literal pool cell = 5 B FORMAL-width `00 01 00 00 00` pre-scaled ([C084] R505 law; predecessor "2-byte" bullet FALSIFIED — C371 must correct BOTH C093 errors: DECPOLY `*A(005A)=5.67` false-as-cited AND the 2-byte width); LOAN2 product block 32 B ×5 at 055D..05DD; [C358] copyin emission already equals the LOAN2 temp-materialiser shape; put-skip tail pinned; `E52Z*`+`e52p13` UNUSED; N33 marker substring recorded. SUCCESSOR: execute PROGRESS.md `## Next action` steps (5),(6) EXACTLY — contract = `LEARNINGS.md` § "P3-13 hop 5 IN FLIGHT" (pre-registered 6-probe panel E52ZA..ZF with byte predictions + falsifiers): write PLAN §P3-13 + probes, commit by EXPLICIT paths BEFORE any oracle call/`ocaml/` byte; then campaign e52p13, goldens VERBATIM first, arm ONLY inside `formal_is_dec` (BY-NAME refusals kept, histogram 68), validation (68/124, cmp FRESH POSITIONAL, sweep 159/0, markers incl honest N33→NG18 retirement iff cmp rc=0 golden KEPT, DEC regressions 64/0, divcheck 9/9), register from 1288/188, C371 measured-bytes-only BEFORE COVERAGE + dated C093 correction, gate rc=0 DIRECT `build/gate-e52p13-reg.log`, RESULTS §P3-13 + CLOSED; marathon through P3-19. Armed binary `6a4c6c1154a0acd8403b…` == tree; ALL inherited constraints in force (goldens VERBATIM never re-derived, POSITIONAL FRESH paths, `git diff --cached --stat`, config NEVER staged, no push, rc DIRECT, never glue `rm`, byte-tier only); commit guard g452+ blocks VERBATIM on recovery.**

0a-marathon-4. **P3-12 CLOSED (session 01a1b1d9, renewal 4/12→5; chain 01a1b1b4): (l) LANDED — FULL gate rc=0 DIRECT `build/gate-e52p12-reg.log` 1288/0, 188/188, 9/9, 143 rows 0/0 SUPPORTED 93, census 15/0/26/0, prose 5; RESULTS §P3-12 + PLAN §5 row + §P3-12 CLOSED `c6f587a`; honest note kept: first gate launch lost rc in background, canonical log is the synchronous rc-captured re-run. Durables 98ddca9 (`## Next action` rewritten for P3-13) + guard blocks effbb66/15fdc9a. SUCCESSOR: execute PROGRESS.md `## Next action` P3-13 Phase A steps (1)–(6) EXACTLY, ZERO oracle FIRST: decode authentic LOAN2.REL display-call (five `dec(10,2)*dec(4,3)` products vs five `fixed dec(10,2)` formals @142-151) + NG18.REL (N33 retirement route, golden KEPT) into fresh `build/p3-13/`; re-verify the C093 `5.67`-vs-DECPOLY-source discrepancy traceably; PLAN §P3-13 + probes E52ZA.. committed BEFORE any oracle call/`ocaml/` byte; contract in LEARNINGS § "P3-13 Phase A IN FLIGHT"; marathon through P3-19. All inherited constraints in force (goldens VERBATIM never re-derived, POSITIONAL FRESH paths, config NEVER staged, `git diff --cached --stat`, no push, rc DIRECT, never glue `rm`, byte-tier only); armed binary `6a4c6c1154a0acd8403b…` == tree; commit guard g447+ blocks VERBATIM on recovery.**

0a-marathon-3. **P3-12 hop 4 (g)(i)(j)(k) LANDED (session 01a1b1c5, chain 01a1b1b4 renewal 3/12→renew 4/12 scheduled; ZERO oracle; goldens NEVER touched; config NEVER staged; no push; rc DIRECT; byte-tier):** divergences 9/9 via NEW standalone `build/p3-12/divcheck.py` (lesson: gate `--only-divergent` is the WRITE/re-measure arm and aborts on stale census — not the check arm); registration `5bf5c88` (SPECIMENS +9 E52YA..YI measured comments; N35_DEC_STORE_SCALE_DRIFT retired HONESTLY to POSITIVE `NG20` — `probes/NG20.PLI` sha `acf8e951…` CRLF+bare-^Z, golden KEPT cmp rc=0 fresh positional, refusals 189→188, inventory 1288/188 exact, census OWN path 15/0/26/0 UNCHANGED, LOAN2 msg MOVED VERBATIM to Line-117, NOTHING fixed); **C370** `172a642` measured-bytes-only BEFORE COVERAGE (ledger ENDS **C370**, 193 headers); row `STOR.DEC_SCALE_ASSIGN` SUPPORTED EXACT:10 + SAME-change IDS line `bf135a9` (lesson: manual_ref must be `pNN[:§X.Y][=phrase]` or start `NONE:`), coverage_check rc=0 **143/93 0/0**, prose rc=0, stats companion `d283623`; durables `29228dc`. Armed binary `6a4c6c1154a0acd8403b…` == tree. **SUCCESSOR: PROGRESS.md → `## Next action` steps (l),(m) EXACTLY** — FULL gate rc=0 DIRECT → `build/gate-e52p12-reg.log` (expect 1288/0, 188/188, 9/9, 143 rows, census 15/0/26/0, prose 5); RESULTS §P3-12 (every §4 miss VERBATIM: YB/YE QDDSR-predicted/QDDSL-measured, YG down-not-up, YI byte-68 my-gap closed by sc=0; NG20 retirement; LOAN2 111→117 NEVER fix; byte-tier-only) + PLAN §5 row + §P3-12 **CLOSED**; then BEGIN P3-13 on the ACTUAL Line-117 blocker (`call display(PL * INF, …)` DEC-expression actuals vs FIXED DECIMAL formals) evidence-first ZERO-oracle: audit DECPOLY/R2037/R2038/R725 + N33 family, PLAN §P3-13 + probes E52ZA.. pre-registered and committed BEFORE any oracle call/`ocaml/` byte; marathon budget through P3-19. All inherited constraints in force (goldens VERBATIM never re-derived, POSITIONAL FRESH paths, `git diff --cached --stat`, config NEVER staged, no push, rc DIRECT, never glue `rm` operands to follow-ups, byte-tier only).

0a-marathon-2. **P3-12 VALIDATION (a)-(e) LANDED (successor session 01a1b1b4, chain renewal 2/12; ZERO oracle this hop; goldens NEVER touched; config NEVER staged; no push; rc DIRECT; byte-tier):** histogram method re-proved via `git archive` baseline replay (binary `25c57e27…` reproduced); Warning 27 `ptr` = BASELINE; arm's ONE new W27 (`args` in `dv_of`) fixed to wildcard `60b9c79` → codegen 68/total 124 == baseline, 9/9 Y cmp re-held on corrected binary **`6a4c6c1154a0acd8403b…`** (new armed fingerprint, deterministic); sweep 159/0; markers 15/16 — **N35 retired honestly** (NG20 shape now cmp rc=0 vs its golden; decision + fresh `probes/NG20.PLI` register-into-positive owed at (i); refusals 189→188, unmeasured-route coverage loss ACCEPTED not papered); DEC regressions 64/0. **INCIDENT repaired:** accidental `rm` of `artefacts/LOAN2.PLI` by a missing `;` in my command; single-path `git restore --source=HEAD`, sha `7be23ba3…` verified, zero scientific loss; NEW LAW: never place `rm` operands adjacent to follow-up commands; always re-check `git status --porcelain` for ` D `. **LOAN2 ADVANCED VERBATIM past 111/112 to ACTUAL blocker (NEVER fix):** `codegen: non-variable argument against a FIXED DECIMAL formal is unproven [TBD] (DR passes an automatic decimal BY REFERENCE -- the descriptor holds LXI H,*A(cell); a literal or expression decimal argument has no sample [DECPOLY, R2037/R2038/R725]. Line 117)` = `call display(PL * INF, …)`; EXPR1 21/EXPR2 35 unchanged. **SUCCESSOR: PROGRESS.md → `## Next action` hop 4 steps (g),(i),(j),(k),(l),(m) EXACTLY** — divergences 9/9; register +9 Y-specimens + NG20 retirement (new `probes/NG20.PLI` committed; NEVER re-derive `golden/negpanel1/NG20/NG20.REL`), inventory 1278→1288/188, census OWN path (LOAN2 msg moves VERBATIM, NOTHING fixed); **C370 measured-bytes-only BEFORE any COVERAGE touch**; NEW row `STOR.DEC_SCALE_ASSIGN` + SAME-change COVERAGE-IDS line (NEVER coverage_gen.py; 15 cols FIRST NON-COMMENT row); FULL gate rc=0 → `build/gate-e52p12-reg.log`; RESULTS §P3-12 + PLAN §5 row + CLOSED; then BEGIN P3-13 on the Line-117 blocker (evidence-first, pre-register before oracle) under marathon authorization. Ledger ENDS **C369**; armed binary `6a4c6c11…`==tree; all inherited constraints in force (goldens VERBATIM, POSITIONAL FRESH paths, `git diff --cached --stat`, config never staged, no push, rc DIRECT, N35 retirement honest, no pipeline-tail rc).

0a-marathon-1. **E2E-52/P3-12 PRE-REGISTERED at `ecba8c5` — campaign `e52p12` OWED; operator LOAN2 COMPLETION MARATHON is LIVE (2026-11-07, session 01a1b18b, NEW operator chain, renewal 1/12; ZERO oracle so far; goldens NEVER touched; `handoff.config.json` NEVER staged; no push; all rc DIRECT; BYTE-TIER ONLY).** **AUTHORIZATION CHANGE (accepted, verbatim in the operator brief):** the P3-11 terminal STOP is SUPERSEDED for work necessary to complete LOAN2 — up to EIGHT slices P3-12..P3-19, ~64 probes, continuing automatically after each closed slice; completion = unmodified `artefacts/LOAN2.PLI` compiles AND whole-file `.REL` identity with `golden/first/LOAN2/LOAN2.REL`; no PLILIB/MIR/runtime, no push. The old "STOP / no P3-12" prose in earlier headings is HISTORICAL. Verified first-hand: HEAD was `83e82b7`; build rc=0, binary sha256 `25c57e27696421e929b8…` == tree (the fingerprint is SHA256 of `ocaml/_build/default/bin/pli80c.exe`, NOT md5); LOAN2 sha `7be23ba3…` rc=2, NO `.REL`, blocker VERBATIM `codegen: DECIMAL assignment between differing scales is unproven [TBD] (…)` with NO `(line N)`. **First responsible statement MEASURED (not assumed) = LOAN2:111 `INF = ci;`** via a temporary `epos.Source.line` addition to the `dpush` refusal, then reverted (`git diff -- ocaml/` EMPTY, fingerprint re-held). **Phase A evidence CLOSED with ZERO oracle:** authentic LOAN2.REL `04B7-04CB` = `LXI H,ci(0309) / MVI A,0F / ?DLDOP / **MVI A,0B / ?QDDSR** / LXI H,inf(0306) / MVI A,04 / ?DSTOP` — shift BETWEEN source push and destination load, d = s_src−s_tgt = 11, DSTOP A = TARGET precision; registered-negative **NG20** (`golden/negpanel1/NG20`, = gate `N35_DEC_STORE_SCALE_DRIFT`) is the UP witness `MVI A,02 / ?QDDSL`, `.PRN` `NO ERROR(S)` both passes ⇒ **N35 retires to POSITIVE** (N26_DECDIV precedent [C086]); LOAN1 `PMT = P` equal-scale/cross-precision control re-measured `cmp` rc=0; LOAN2:112 divide bytes MATCH the already-armed [C086] L3/L5 path (OUTSIDE perimeter); **NG21 FALSIFIED as evidence** (pass-2 `SYNTAX` listing, no `.REL`). Decoding note: `tools/dis80.py` on a `.REL` prints gaps for RELOC-embedded operands — use `build/e52p8/ondump2.py` buffers + dis80's table + CHAIN-EXT (anchor = opcode+1). LANDED: PLAN §P3-12 (H-1 candidate law; H-2 precision-in-amount, H-3 large-d cap, H-4 no-shift-DSTOP, H-6 decimal()-descriptor competitors + falsifiers; per-probe pre-registered sequences; §5 arm/validate/register contract; §7 precision-vs-scale framing binding C370) + §5 progress row + nine `probes/E52Y{A..I}.PLI` (CRLF + bare `^Z` + ≤71 cols + ONE declaration per line — the comma-list `dcl` leaves names undeclared here; sanity YA/YH/YI rc=0, YB..YG rc=2 at the guard) + LEARNINGS § P3-12 Phase A + PROGRESS Next action. **SUCCESSOR: execute PROGRESS.md → `## Next action` steps (2)–(6) EXACTLY** — (2) ONE campaign `cd /home/john/projects/sushiworks/pli80 && PLI_SRC=probes timeout 900 python3 oracle/batch.py E52YA E52YB E52YC E52YD E52YE E52YF E52YG E52YH E52YI --tag e52p12 --switches '$L$D'` rc DIRECT, read EVERY `.PRN`, decode accepted `.REL`s into `build/p3-12/`, commit goldens VERBATIM BEFORE any `ocaml/` byte; (3) arm ONLY the measured shapes in the `dpush` simple-operand arm, unproven shapes keep BY-NAME [TBD] refusals, never special-case LOAN2 names/addresses; (4) build rc=0 + histogram codegen 68/total 124 == baseline + whole-file `cmp` on FRESH POSITIONAL paths + sweep FAILS 0 + markers (CRLF+bare `^Z`) + DEC regressions + negative panel incl. the honest N35 retirement + divergences 9/9; (5) LOAN2 UNMODIFIED → record the ACTUAL next blocker VERBATIM, or if it compiles go STRAIGHT to whole-file parity (first-mismatch localization per the brief §7; a matching CODE stream is NOT completion); (6) register from **1278** (accepted-and-byte-exact only, `--update-inventory`, `git diff --cached --stat`, census OWN path), claim **C370** measured-bytes-only BEFORE any COVERAGE touch, NEW row + its `spec/COVERAGE-IDS.txt` line in the SAME change (NEVER `coverage_gen.py`; 15 cols from the FIRST NON-COMMENT row; textual tab edit), coverage_check+prose rc=0, FULL gate rc=0 DIRECT → `build/gate-e52p12-reg.log`, RESULTS §P3-12 + §P3-12 **CLOSED**, commit guard blocks VERBATIM, then **BEGIN P3-13 on the next actual blocker without waiting for a prompt**. Ledger ENDS **C369**; inventory **1278/189**; coverage **142/92** 0/0; last full gate rc=0 `build/gate-e52p11-reg.log`; armed binary `25c57e27696421e929b8…`==tree; goldens NEVER re-derived; `pli80c` POSITIONAL into FRESH paths; ALWAYS `git diff --cached --stat`; config NEVER staged; no push; renew autonomously only at committed safe boundaries.

0a-novies-new35. **E2E-52/P3-11 hop 4 — (6a) REGISTRATION `69dd508` + (6b) C369 `a00fc13` LANDED FIRST-HAND; (6c) COVERAGE EXTENSIONS IN FLIGHT; SESSION RENEWING (2026-11-07, session 01a1b14e, chain 01a1b0c9 renewal 4/12, cap 5/12 at g431; ZERO oracle; goldens NEVER touched; `handoff.config.json` NEVER staged; no push; all rc DIRECT; byte-tier only).** Acceptance facts (all from `build/e52p11/E52X*-reldump.txt` records re-read this session): SPECIMENS +9 E52XA..XI with measured comments (XA 0036/0002 slot 0022->002D; XB/XC 003E/0006 w1 0E52/2E52; XD 003C/0011 ?SLVTS; XE 003D/0004 DOUBLE patch 0029+0020->0034; XF 0063/0017 C3 002B->0048; XG 003E/0003; XH 0038/0002 NO ?PNCOP; XI 0043/0003); XJ/XK in REJECTS as honest **my-gap** goldens KEPT UNCLAIMED (XJ SEL-COMMON-at-first-use CODE 0021; XK w1 0690 attach STILL 0652), markers RE-MEASURED rc=2 under gate CRLF+bare-^Z (line 8/line 9, `build/e52p11-reg/xjxk-remeasure.log`); inventory **1278/189** (+9/+2, every line inspected); census OWN path rc=0 counts 15/0/26/0, LOAN2 msg MOVED VERBATIM to the DEC-scales blocker, NOTHING fixed; **ledger ENDS C369 (192 headers), prose rc=0**. TOOL LESSONS: reldump prints single-hex DATA bytes (`0x6`) — regex `0x[0-9a-f]{1,2}`; raw .REL walk needs HIGH-bit MACREL types — use the ondump2/reldumps chain (ondump2 IGNORES CLI args). **SUCCESSOR: execute `LEARNINGS.md` § "P3-11 hop 4 IN FLIGHT" EXACTLY — (6c) EXTEND ONLY rows `FILE.PUT_LIST`(+E52XG)/`FILE.PUT_SKIP`(+E52XH,E52XI)/`FILE.PUT_PAGE`(+E52XA..XF), NEVER new rows, NEVER `coverage_gen.py`, 15 cols from FIRST NON-COMMENT row, `delimiter='\t'`, IDS diff EMPTY, labelled correction for the LIST row's now-false "No object yet pairs…" clause, EXACT bumps PAGE 1->7/SKIP 18->20/LIST 10->11 (let `coverage_check.py` adjudicate), coverage_check rc=0 142 rows 0/0 SUPPORTED 92 + prose rc=0, commit explicit paths; (6d) FULL gate rc=0 DIRECT -> `build/gate-e52p11-reg.log` expect 1278/0, 189/189, 9/9, 142 rows, census 15/0/26/0, prose 5; (6e) RESULTS §P3-11 (parity table; every falsifier + my §4 XA-slot-0030 slip VERBATIM, measured 002D; XJ/XK my-gap; LOAN2 line-99 CLOSED advance VERBATIM NEVER fix; byte-tier-only) + PLAN §5 row + §P3-11 **CLOSED** + durables + commit guard blocks VERBATIM. STOP at P3-11 — NEVER the DEC-scales blocker, no P3-12, no runtime claims.** Ledger ENDS **C369**; inventory **1278/189**; coverage 142/92 extensions owed; armed binary `25c57e27696421e929b8…`==tree; goldens NEVER re-derived; `pli80c` POSITIONAL FRESH paths; ALWAYS `git diff --cached --stat`; config NEVER staged; no push; rc DIRECT.

0a-novies-new34. **E2E-52/P3-11 hop 3 LANDED — campaign e52p11 **11 ok/11**, goldens VERBATIM `060289e` BEFORE any `ocaml/` byte, candidate A ARMED `3e0a3c1` **9/9 byte-exact**; LOAN2 ADVANCED past 99; REGISTRATION→C369→COVERAGE→GATE→CLOSE OWED (2026-11-07, session 01a1b13c, chain 01a1b0c9 renewal 3/12; config NEVER staged; no push; all rc DIRECT).** ACCEPTED first-hand (all `.PRN` `NO ERROR(S)` both passes; reldumps `build/e52p11/E52X*-reldump.txt`): every §4 CODE prediction HIT (XA 0036 XB 003E XC 003E XD 003C XE 003D XF 0063 XG 003E XH 0038 XI 0043 XJ 0021 XK 0036); **H-E DOUBLE back-patch CONFIRMED, single-patch competitor FALSIFIED**; **H-B pagesize-required competitor FALSIFIED** (literal-title+print, no pagesize, accepted, w1 0E52); **H-J ACCEPTED** no-open PAGE = E46L8 SEL-COMMON-at-first-use geometry; **H-K ACCEPTED** stream-input open w1 `9006`, attach STILL `0652` — [C280] direction law reconfirmed; honest §4 miss kept VERBATIM: H-A "slot→0030" was my arithmetic slip, measured 002D. Candidate A = ONE condition line in `lower_open` (records `PRINT` beside `OUTPUT` into `st.file_out`); guard/emitters UNCHANGED, zero statement bytes; PU1 substring survives VERBATIM. VERIFIED armed binary `25c57e27696421e929b8…` (deterministic; fresh `_build-e52p11`): histogram codegen 68/total 124==baseline EXACTLY; XA..XI whole-file cmp 9/9 (POSITIONAL, FRESH `build/e52p11/out/`); XJ/XK still rc=2 BY NAME (my-gap, goldens KEPT); sweep FAILS 0; markers PU1/E41X5/E46K10/N3_PAGE/E46N21 5/5 MARKER_FAILS 0; regressions 38/38 (E16D,E17D,TA..TJ,UA..UF,VA..VK,WA-WE,WH-WK from INVENTORY rows). **LOAN2 new ACTUAL blocker VERBATIM (recorded, NEVER fixed — PLAN §6 STOP): `codegen: DECIMAL assignment between differing scales is unproven [TBD] (only computed results are pinned as needing a QDDSL/QDDSR fix; a direct DEC operand store always had equal scales in the samples)` — NO `(line N)` clause; line-99 blocker CLOSED.** EXPR1 GET-21/EXPR2 FLOAT-35 unchanged. **SUCCESSOR: execute `LEARNINGS.md` § "P3-11 hop 3 LANDED" STILL-OWED (6a)-(6e) EXACTLY:** registration from 1269 — SPECIMENS +9 (XA..XI ONLY), XJ/XK into REJECTS as honest `my-gap` (SE/E46L8 precedent; markers re-measured under gate CRLF+bare-^Z), `--update-inventory` → **1278/189**, inspect every line, `git diff --cached --stat`, config NEVER staged; census OWN path (15/0/26/0, LOAN2 msg MOVED VERBATIM, NOTHING fixed); **C369 measured-bytes-only BEFORE ANY COVERAGE touch** (Phase-A bullets (a)-(i); eligibility worded as source-structure evidence, NEVER runtime-open); EXTEND `FILE.PUT_PAGE`/`FILE.PUT_LIST`/`FILE.PUT_SKIP` rows only (NEVER `coverage_gen.py`; 15 cols from FIRST NON-COMMENT row; `delimiter='\t'`; IDS set unchanged); coverage_check rc=0 142 rows 0/0 SUPPORTED 92 + prose rc=0; FULL gate rc=0 DIRECT → `build/gate-e52p11-reg.log` expect **1278/0, 189/189, 9/9, 142 rows, census 15/0/26/0, prose 5**; RESULTS §P3-11 + PLAN §5 row + §P3-11 **CLOSED** + durables. **STOP at P3-11 — NEVER the DEC-scales blocker, no P3-12, no runtime claims.** Ledger ENDS **C368** (C369 owed); inventory 1269/187; coverage 142/92; armed binary `25c57e27696421e929b8…`==tree; goldens NEVER re-derived; `pli80c` POSITIONAL FRESH paths; chain 01a1b0c9 3/12 cap 12; no push; rc DIRECT; byte-tier only.

0a-novies-new33. **E2E-52/P3-11 hop 2 LANDED — PLAN §P3-11 + probes E52XA..XK PRE-REGISTERED BEFORE any oracle call/`ocaml/` byte; CAMPAIGN e52p11 OWED (2026-11-07, session 01a1b127, chain 01a1b0c9 renewal 2/12; ZERO oracle; ZERO `ocaml/` byte; goldens NEVER touched; `handoff.config.json` NEVER staged; no push; all rc DIRECT).** Recovery verified; build rc=0 binary `a4c0e235ed4bb81fe284…`==baseline; g427 VERBATIM `093ba87`. First-hand: LOAN2 18-B PAGE+DOUBLE-patch re-held; E46N1 20-B (NO PNCOP)/E46N2 31-B/E46L8 SEL-COMMON-at-first-use dumps; **imm store CORRECTED to 6 code bytes**; titled-route zero word + 4 E5 pushes are ROUTE furniture (TB/TC) → XB 29-B w1 0E52 prediction; sanity: all 11 probes rc=2 at the eligibility guard — gap is `st.file_out` recording ONLY. LANDED PLAN §P3-11 + 11 probes + LEARNINGS § hop 2 by EXPLICIT paths. **SUCCESSOR: PLAN §P3-11 §5 verbatim — campaign `PLI_SRC=probes timeout 900 python3 oracle/batch.py E52XA..E52XK --tag e52p11 --switches '$L$D'` rc DIRECT; goldens VERBATIM before emitter; honest XJ/XK (WL/E46L8 precedents); candidate A iff XA..XI byte-exact (ONE-line `lower_open` PRINT recording) else candidate C PAGE-only; PU1 substring survives; verify suite (histogram 68/124, cmp FRESH POSITIONAL, sweep 0, markers incl PU1/E41X5/E46K10/N3_PAGE/E46N21, regressions, 187, 9/9); LOAN2 VERBATIM never fix; registration from 1269, C369 measured-bytes-only BEFORE ANY COVERAGE touch (prefer EXTENDING PUT rows, NEVER coverage_gen.py, 15 cols first NON-COMMENT row, delimiter='\t'); gate rc=0 build/gate-e52p11-reg.log; RESULTS/PLAN §5/CLOSED; durables. STOP at P3-11.** Ledger ENDS **C368**; inventory **1269/187**; coverage **142/92**; binary `a4c0e235ed4bb81fe284…`==tree; goldens NEVER re-derived; LOAN2 `(line 99)` NEVER fix; `pli80c` POSITIONAL FRESH paths; ALWAYS `git diff --cached --stat`; config NEVER staged; no push; rc DIRECT; byte-tier only; chain cap 12 (2/12 used).

0a-novies-new32. **E2E-52/P3-11 hop 1 PARTIAL — FIRST-HAND BYTE VERIFICATION + CHECKS LANDED `57e7f62`; PLAN §P3-11 + PROBES E52XA..XK STILL OWED BEFORE THE FIRST ORACLE CALL; SESSION RENEWING (2026-11-07, session 01a1b110, operator chain 01a1b0c9 renewal 1/12; ZERO oracle; ZERO `ocaml/` byte; goldens NEVER touched; `handoff.config.json` NEVER staged; no push; all rc DIRECT).** Recovery verified HEAD `b0c5dbd`+guard `f58f64f`; build rc=0, binary md5 `cbede3b5…` == baseline `a4c0e235ed4bb81fe284…` re-held. LANDED (raw records, `build/e52p11/xplan/`): LOAN2 03AA-03BB 18-B PAGE (`21`+RELOC common0/`11 52 06`/`01`+slot 03B1/CD `?SIOOP`@03B4/`?PAGOP`@03B7/`?QIOOP`@03BA) with DOUBLE back-patch — LXI B slot 03B1 AND the line-98 CA skip-slot 03A8 both → 03BC; COPYLPT 0215-0226 same shape → 0227; P019B 0063-007C LIST-behind-titleless-print 26 B → 007D; E52TA/TB/TC print-open blocks + sizes (PF `0024` [C120], OUTF `0026`, CODE `0035/003D/003B`; literal `?SLCTS` 29 B, varying `?SLVTS` 27 B, bare 17 B after `AF 47 C5 33`); E52VA leaf `3A r(data1)/B7/F2`→0x13 + 7-B imm store; E46N1 attach. CHECKS CLEAN: `E52X*` names + tag `e52p11` UNUSED; NO pinned negative pairs a PRINT open with a named PUT (2 grep hits were comment prose); PU1/E41X5/E46K10 have NO open → candidate A (`lower_open` records PRINT opens into `st.file_out`, codegen ~11557) collides with NOTHING, substring marker `PUT FILE(F) has no byte-exact DR witness` survives. **SUCCESSOR: execute `LEARNINGS.md` § "E2E-52/P3-11 hop 1 IN FLIGHT" STILL-OWED VERBATIM — step (1) write PLAN §P3-11 (template §P3-10) + probes E52XA..XK (CRLF, bare `^Z`, ≤71 cols, `E52XX:` first-line label, statement after EVERY PUT) + optional zero-oracle local `pli80c` sanity compiles to pin MY-side predictions, commit by EXPLICIT paths BEFORE any oracle call/`ocaml/` byte; (2) ONE campaign `PLI_SRC=probes timeout 900 python3 oracle/batch.py E52XA..E52XK --tag e52p11 --switches '$L$D'` rc DIRECT, goldens VERBATIM before any emitter change, XJ/XK classified honestly (WL/SE precedents), NEVER invent goldens; (3) smallest measured rule — candidate A iff XG/XH/XI accepted+byte-exact via the ONE route-independent emitter, else candidate C PAGE-only; (4) build/histogram 68-124/cmp/sweep FAILS 0/markers/regressions/negatives 187/divergences 9/9; (5) LOAN2/EXPR1/EXPR2 POSITIONAL VERBATIM, ACTUAL blocker past 99 recorded NEVER fixed; (6) registration from 1269, **C369 measured-bytes-only BEFORE ANY COVERAGE touch**, prefer EXTENDING `FILE.PUT_PAGE`/`FILE.PUT_LIST`/`FILE.PUT_SKIP` rows (new rows ship their COVERAGE-IDS line in the SAME change; NEVER `coverage_gen.py`; 15 cols from FIRST NON-COMMENT row; `delimiter='\t'`), gate rc=0 → `build/gate-e52p11-reg.log`, RESULTS §P3-11 + PLAN §5 row + CLOSED, durables. **STOP at P3-11 — no next-blocker fix, no P3-12, no runtime claims.** Ledger ENDS **C368**; inventory **1269/187**; coverage **142/92** 0/0; binary `a4c0e235ed4bb81fe284…` == tree; goldens NEVER re-derived; census `0198fe5` 15/0/26/0; `pli80c` POSITIONAL into FRESH paths; ALWAYS `git diff --cached --stat`; config NEVER staged; no push; chain cap 12 (2/12 will be used by this renewal).

0a-novies-new31. **E2E-52/P3-10 hop 3 REMAINDER + SUBROUND P3-10 FULLY CLOSED — STOP REACHED; ONLY THE GUARD-BLOCK COMMIT REMAINS; NOTHING AUTHORIZED THEREAFTER (2026-11-07, session 01a1b0af, chain 01a1b069 renewal 3/12; ZERO oracle; goldens NEVER touched; `handoff.config.json` NEVER staged; no push; all rc DIRECT).** g420 blocks attested (this session started FROM them). LANDED: all C368-cited bytes re-verified FIRST-HAND vs `build/e52p10/E52W*-reldump.txt` + `e52p10-signals-disasm.txt` + WL `.PRN` (WG signal region is at 000C-0012 AFTER its `n=1` statement; WF slots 000C/0014/0017/001A; WK `F2` `RELOC code 0x1e` = signal 0017+7; WE `21 00 01`) — **C368 `7153716` measured-bytes-only BEFORE ANY `spec/COVERAGE.tsv` touch**, ledger ENDS **C368** (191 `## C` headers); `COND.SIGNAL` NEW row SUPPORTED/**EXACT:9** (probes the 9 accepted ONLY — precedent COND.ON_ERROR; WL lives in boundary + NEG panel; corpus LOAN2,EXPR1,EXPR2,COPYLPT all census names; perimeter S; runtime NONE; MEASURED; provenance [C368][C366][C367][C120][C109][C202][C206][C208]) + EXPLICIT IDS line `65b005e` (NEVER `coverage_gen.py`; 15 cols from FIRST NON-COMMENT row; `delimiter='\t'`; diff 2 lines BY CONTENT) — `coverage_check` rc=0 **142 rows 0/0 SUPPORTED 92**, prose rc=0; **FULL gate rc=0 DIRECT `build/gate-e52p10-reg.log` — 1269/0, 187/187, 9/9, 142 rows 0/0, census 15/0/26/0, prose 5 — EVERY pre-registered number HIT**; **RESULTS §P3-10 + PLAN §5 P3-10 row + PLAN §P3-10 CLOSED** `fbca4fe` (H-A/B0/B2/C255/E1/E2/F/G CONFIRMED, no §3 falsifier fired; **WE FALSIFIES the 0..255 range-check competitor** VERBATIM; WF stack `0029`/DATA`0003` + WG `LHLD` `001C` DR-accepted SINGLE witnesses armed NEITHER, open my-gap [TBD], panel-unverified; WL `dr-refuses` PASS-2 line-12 `SYNTAX ?` NO .REL kept VERBATIM + CRLF-materialization marker lesson re-confirmed; frontend `cargs` repair `d84665c` + proto test `91060ea` 12/12; LOAN2 ADVANCED VERBATIM 92->99 `PUT FILE(OUTPUT)` ACTUAL-not-predicted NEVER fix; byte-tier-only; `?SIGOP`/PLILIB UNEXAMINED; H-E1 `0023` = PLAN name-length slip, [C120] 34+len law gives PF `0024` — application note, law holds). NEW validator insights accepted: coverage_check claim window is `pos+4000` for the LAST claim and probe traceability needs only ONE mentioned probe (`hit = any`); the IDENTITY invariant is exact set equality ledger-vs-manifest — a new row MUST ship its manifest line in the same change. **SUCCESSOR: commit the guard-refreshed managed blocks VERBATIM, then STOP — P3-10 is CLOSED and NOTHING is authorized: do NOT touch the line-99 `PUT FILE(OUTPUT)` blocker, no P3-11, no `REVERT ERROR`, no PLILIB/MIR, no oracle, no runtime claims; a NEW operator brief is required for any further subround.** Ledger ENDS **C368**; inventory **1269/187**; coverage **142 SUPPORTED 92** 0/0; census `0198fe5` 15/0/26/0 with LOAN2 blocker VERBATIM line-99 (rc=2, NO .REL, NEVER fix); goldens NEVER re-derived; binary `a4c0e235ed4bb81fe284…` (md5 `cbede3b5…`) == tree, build rc=0 re-held; `pli80c` POSITIONAL into FRESH paths; ALWAYS `git diff --cached --stat`; config NEVER staged; no push; chain cap 12 (3/12 used).

0a-novies-new30. **E2E-52/P3-10 hop 3 PART LANDED — AST TEST + REGISTRATION + CENSUS DONE; C368 -> COVERAGE -> GATE -> CLOSE OWED; SESSION RENEWING (2026-11-07, session 01a1b09a, chain 01a1b069 renewal 2/12; ZERO oracle; goldens NEVER touched; `handoff.config.json` NEVER staged; no push; all rc DIRECT).** Commits: `91060ea` proto test `ocaml/proto/ssignal_ast.ml` + dune stanza — 12/12 PASS rc=0 (cargs/target preserved incl. refused WF/WG/multi/FROM/WL shapes); `21d4db6` registration — SPECIMENS **+9** (WA-WE,WH-WK ONLY), **WL DR-REFUSES REGISTERED** (decision honest, precedent SF/SG; VERBATIM `SYNTAX ?` PASS 2 line 12, NO .REL; marker RE-MEASURED under the gate CRLF+bare-^Z materialization — LF-only shifts 12->6, hop-2 lesson re-confirmed), WF/WG NOT registered (my-gap single witnesses, H-D2); `--update-inventory` **1269/187** (+9/+1 exactly, every line inspected); `0198fe5` census OWN path rc=0 counts 15/0/26/0 UNCHANGED, LOAN2 msg MOVED VERBATIM 92->99 `PUT FILE(OUTPUT)`, NOTHING fixed; durables `cd8bd98`. FIRST-HAND raw-record re-verification table + LEDGER-FORMAT FACT (pre-E2E-52 claims are bold/paragraph prose; C367 @9022 = header+bullets precedent) + **THE FULLY DRAFTED C368 TEXT AND BULLET CONTRACT** are in `LEARNINGS.md` § "P3-10 hop 3 PART" — read it FIRST. **SUCCESSOR:** execute `PROGRESS.md` → `## Next action` hop 3 REMAINDER EXACTLY: spot-check 2-3 cited bytes vs `build/e52p10/E52W*-reldump.txt` + `e52p10-signals-disasm.txt`, append drafted **C368 measured-bytes-only BEFORE ANY `spec/COVERAGE.tsv` touch**, commit; `COND.SIGNAL` SUPPORTED/**EXACT:9** row + EXPLICIT `spec/COVERAGE-IDS.txt` line (NEVER `coverage_gen.py`; **15 cols from FIRST NON-COMMENT row**; `delimiter='\t'`); `coverage_check` rc=0 expect **142 rows 0/0 SUPPORTED 92** + prose rc=0; FULL gate rc=0 DIRECT redirect `build/gate-e52p10-reg.log` (expect **1269/0, 187/187, 9/9, 142 rows, census 15/0/26/0, prose 5**); RESULTS §P3-10 (WE 0..255-falsifier + WL verdict + WF/WG no-generalise + LOAN2 92->99 advances VERBATIM, byte-tier-only) + PLAN §5 row + §P3-10 **CLOSED** + durables. **STOP at P3-10 — NEVER the line-99 blocker, no P3-11, no runtime claims.** Ledger ENDS **C367** (C368 owed); inventory 1269/187; coverage 141/91 -> 142/92 owed; binary `a4c0e235ed4bb81fe284…` == tree; goldens NEVER re-derived; `pli80c` POSITIONAL into FRESH paths; ALWAYS `git diff --cached --stat`; config NEVER staged; no push; chain cap 12 (2/12 used, renewal scheduled by guard).

0a-novies-new29. **E2E-52/P3-10 hop 2 LANDED — CAMPAIGN e52p10 MEASURED + ARM BYTE-EXACT; REGISTRATION/C368/CLOSE OWED; SESSION RENEWING (2026-11-07, session 01a1b085, chain 01a1b069 renewal 2/12; goldens committed BEFORE any `ocaml/` byte; config NEVER staged; no push; all rc DIRECT).** Campaign rc=0 **11 ok/12**: H-A/B0/B2/C255/E1/E2/F/G **HIT**; **WE falsified the 0..255 compiler-range competitor** (`error(256)` = `21 00 01` full 16-bit verbatim); **WF** accepted UNFOLDED on the FIXBIN stack, **WG** accepted via `LHLD` — SINGLE witnesses, armed NEITHER (open my-gap [TBD]); **WL dr-refuses** (`SYNTAX` PASS 2 line 12, NO .REL, VERBATIM, no invented golden). Goldens VERBATIM `d46b6c2`; frontend `cargs` repair + `Ssignal` arm (measured shapes ONLY; own `signal_error_prefix`; FROM kept never lowered) `d84665c`: build rc=0 binary `a4c0e235ed4bb81fe284…`, histogram 68/124, **9/9 whole-file cmp**, sweep FAILS 0, markers 10/10, regressions 17/17; **LOAN2 ADVANCED VERBATIM** past 92 to `codegen: PUT FILE(OUTPUT) … (line 99)` — PREDICTED advance class, ACTUAL text recorded, NEVER fix; EXPR1 21/EXPR2 35 unchanged. LESSON: pipeline-tail `| head` hid a build rc → STALE `_build/default` FALSE-REFUSED WK; re-verify one cmp on the binary you trust. Durables `88656c9`. **SUCCESSOR:** execute `PROGRESS.md` → `## Next action` hop 3 EXACTLY — AST-preservation proto test FIRST (`ocaml/proto/ssignal_ast.ml`, cargs preserved even on refused forms), registration from **1260** (SPECIMENS **+9** WA-WE,WH-WK ONLY; WF/WG NOT registered; WL REJECTS decision honest, precedent SF/SG), census OWN path (LOAN2 message MOVED VERBATIM, NOTHING fixed), **C368 measured-bytes-only BEFORE ANY COVERAGE touch**, `COND.SIGNAL` SUPPORTED/EXACT:9 + EXPLICIT IDS line (NEVER `coverage_gen.py`; 15 cols from FIRST NON-COMMENT row; `delimiter='\t'`), coverage_check rc=0 expect **142 rows SUPPORTED 92**, prose rc=0, FULL gate rc=0 DIRECT `build/gate-e52p10-reg.log`, RESULTS §P3-10 + PLAN §5 + §P3-10 **CLOSED** + durables. **STOP at P3-10 — never the line-99 blocker, no P3-11, no runtime claims.** Ledger ENDS **C367** (C368 owed); inventory 1260/186; coverage 141/91; goldens NEVER re-derived; `pli80c` POSITIONAL into FRESH paths; ALWAYS `git diff --cached --stat`; config NEVER staged; no push; chain cap 12 (2/12 used).

0a-novies-new28. **E2E-52/P3-10 hop 1 LANDED — SIGNAL EVIDENCE AUDITED + PRE-REGISTERED `c6c4460`; ORACLE CAMPAIGN `e52p10` OWED; SESSION RENEWING (2026-11-07, session 01a1b069, operator-authorized brief P3-10, fresh chain; ZERO oracle, ZERO `ocaml/` byte; goldens NEVER touched; `handoff.config.json` NEVER staged; no push; all rc DIRECT).** Recovery verified HEAD `ec3ff7b` == brief. ACCEPTED (raw bitstream records, `build/e52p10/`, PLAN §2 table): SIX SIGNAL sites in exactly FOUR original objects — LOAN2 0359 `21 00 00`ABS/`AF`/CD`?SIGOP`@035E 7B; EXPR1 0175+018D, EXPR2 023D+0255 `21 01 00`ABS identical; COPYLPT 02AA `21`+RELOC common@0 PRINTF/`3E 08`/CD@02B0 11B; ON-route control COPYLPT 0254 same `3E 08` via ?ONCOP; SIGNAL = PURE statement (no jump-over/handler/pad/SP-cell), jumps patch past it. TOOL LESSON: `build/e52p8/ondump2.py` IGNORES CLI args (hard-coded TARGETS) — use `build/e52p10/sigdump.py`. LANDED `c6c4460`: PLAN §P3-10 (H-A..H-X, falsifiers, arm contract, frontend defect record §7) + probes **E52WA..WL** (CRLF+bare ^Z ≤71 cols; error(1) merged by 4 witnesses; FROM/multi-arg/other conditions NOT probed, kept unmeasured BY-NAME). Durables `077309a`; g412 blocks VERBATIM `215c233`. **SUCCESSOR:** execute `PROGRESS.md` → `## Next action` hop 2 EXACTLY: ONE campaign `PLI_SRC=probes timeout 900 python3 oracle/batch.py E52WA..E52WL --tag e52p10 --switches '$L$D'` rc DIRECT → goldens VERBATIM BEFORE any emitter → frontend `Ssignal.cargs` repair AFTER evidence → arm measured shapes ONLY → cmp/sweep/markers/regressions → LOAN2/EXPR1/EXPR2 POSITIONAL VERBATIM (record ACTUAL new blocker, NEVER fix) → registration from 1260, **C368 measured-bytes-only BEFORE COVERAGE** (`COND.SIGNAL`, NEVER `coverage_gen.py`, 15 cols from FIRST NON-COMMENT row) → FULL gate rc=0 `build/gate-e52p10-reg.log` → RESULTS §P3-10 + PLAN §5 + CLOSED + durables. **STOP at P3-10.** Ledger ENDS **C367**; inventory 1260/186; coverage 141 SUPPORTED 91; binary `11c6283e75b60fe3…` == tree; census 15/0/26/0 (LOAN2 `(line 92)` NEVER fix); goldens NEVER re-derived; `pli80c` POSITIONAL into FRESH paths; ALWAYS `git diff --cached --stat` before commit; byte-tier only — NO runtime claims; no push; chain cap 12 (1/12 used).

0a-novies-new27. **E2E-52/P3-9 hop 7 CLOSE COMPLETE — SUBROUND P3-9 FULLY CLOSED; ONLY THE GUARD-BLOCK COMMIT REMAINS; THEN STOP (2026-11-06, successor session of chain 01a1af4f renewal 4/12; ZERO oracle; goldens NEVER touched; `handoff.config.json` NEVER staged; no push; all rc DIRECT).** g410 blocks VERBATIM `8ada736`; build rc=0 binary `11c6283e75b60fe3…` == tree. LANDED: **`COND.OR` row** `7da60b5` (SUPPORTED, EXACT:11, probes E52VA..VK, corpus LOAN2,ANNUITY, law ONLY from [C367], BY-NAME perimeter + falsifiers RB/SN-LB/PAR/LITERAL-FIRST VERBATIM + O-1 panel-unverified + byte-tier-only + census advances; EXPLICIT IDS line, NEVER `coverage_gen.py`, columns from the FIRST NON-COMMENT row (15) — the hop-7 LAW, plus a new sub-lesson: `csv.writer` defaults to COMMA, always pass `delimiter='\t'`; the first attempt died on its own round-trip assert BEFORE any write, harmless); `coverage_check` rc=0 **141 rows 0/0 SUPPORTED 91** + prose rc=0; **FULL gate rc=0 DIRECT `build/gate-e52p9-reg.log` — 1260/0, 186/186, 9/9, 141 rows 0/0, census 15/0/26/0, prose 5 — every pre-registered number HIT**; **RESULTS §P3-9 + PLAN §5 P3-9 row + §P3-9 CLOSED** `66cb943` (parity table; H1 CONFIRMED; H2 SPLIT RB-falsified-by-VB==VC / SN-LB-falsified-by-VE-VF-node1-`2A`-heads, surviving NODE-LOCAL rules 1–3; H3/H4/H8-law/H9/H10 CONFIRMED; H5-order/H6-sequence falsified; H7 VAR-FIRST law, PAR+literal-first dead, [C155] dedup confirmed, VI 001B falsified console-`data=` COSMETIC; EVERY §4 CODE-size SHORT miss VERBATIM; VG/VI first-attempt cmp FAILs adjudicated by the VAR-FIRST refit; LOAN2 line-92 PREDICTED=MEASURED NEVER fix; byte-tier-only). **SUCCESSOR: the ONLY step left is committing the guard-refreshed managed blocks VERBATIM, then STOP — P3-9 is CLOSED and NOTHING is authorized: do NOT start P3-10/`signal error`/`?SIGOP` (PROPOSED only), no oracle, no PLILIB/MIR, no push.** Ledger ENDS **C367**; inventory 1260/186; coverage 141 SUPPORTED 91 0/0; census `b080894`; goldens NEVER re-derived; `pli80c` POSITIONAL into FRESH paths; ALWAYS `git diff --cached --stat` before commit; chain 01a1af4f 5/12 cap 12.

0a-novies-new26. **E2E-52/P3-9 hop 7 PART DONE — C367 LANDED; COND.OR COVERAGE ROW + GATE + CLOSE OWED; RENEWAL SCHEDULED (2026-11-06, session 01a1af94, chain 01a1af4f renewal 3/12; ZERO oracle; goldens NEVER touched; `handoff.config.json` NEVER staged; no push; all rc DIRECT).** g406 blocks committed VERBATIM `16d3db7`; build rc=0 binary `11c6283e75b60fe3…` == STATE; **11/11 E52VA..VK compile rc=0 + whole-file `cmp` rc=0 re-verified FIRST-HAND into FRESH `build/e52p9-hop7/out/`** (POSITIONAL `pli80c.exe IN OUT`; sizes 128/128/128/128/128/256/256/256/384/128/256 == goldens); every C367 byte re-read first-hand from `build/e52p9-arm/goldens-dump.txt` raw records + `loan2-decode.txt` (VG DATA `abs 0014`, VI `abs 001A`; CODE VA 001C · VB/VC/VD 0026 · VE 002C · VF 003C · VG 0047 · VH 002F · VI 0076 · VJ 0025 · VK 0080; VG relocs 0x9→0x0 and 0xE→0x5; VI 0xB→0x0, 0x11→0x6, 0xB→0x0 shared zero10 ✓[C155]). **C367 committed `eaa5ef3` measured-bytes-only BEFORE any `spec/COVERAGE.tsv` touch** (fold = value-level, ONE terminal `F2`; class-driven NODE-LOCAL order: `<0` LAST bare `3A r(cell+1)`, same-var `=0`-then-`>k` ladder pushed first, else source order; VA TEST leaf `3A/B7/F2` reloc EXACTLY one past the declared cell; **DEC pair VAR-FIRST**; materializers verbatim; VH two independent patch targets; VK precedence + BARE `32`; BY-NAME perimeter; O-1 original-golden-decode PANEL-UNVERIFIED; byte-tier-only). FALSIFIED kept verbatim: RB (by VB==VC identity), SN/LB (by VE/VF-node1 `2A` heads), PAR (hop 3), hop-4/5 LITERAL-FIRST (hop 6, layout misread — pool sits BELOW the autos on this tree). **NOT LANDED (honest):** the `COND.OR` row — my csv script took the column count from comment LINE 1 of `spec/COVERAGE.tsv` (`n=1`), its assertion fired BEFORE either write, so the ledger AND `spec/COVERAGE-IDS.txt` are UNMODIFIED (`coverage_check` rc=0 still **140 rows 0/0, SUPPORTED 90**). **LAW: derive the COVERAGE column count from the first NON-COMMENT row (15); verify any ledger edit by `git diff --stat` ≈ one TSV + one IDS line and by the row count moving 140→141.** **SUCCESSOR:** execute `PROGRESS.md` → `## Next action` steps (3)–(6): `COND.OR` SUPPORTED `EXACT:11` row + EXPLICIT IDS line (**NEVER `coverage_gen.py`**) + coverage_check/prose rc=0 → FULL gate rc=0 DIRECT `build/gate-e52p9-reg.log` (expect 1260/0, 186/186, 9/9, **141 rows 0/0**, census 15/0/26/0, prose 5) → RESULTS §P3-9 (all §4 CODE-size SHORT misses + every falsifier VERBATIM, VG/VI first-attempt cmp FAILs adjudicated by the VAR-FIRST refit) + PLAN §5 row + §P3-9 CLOSED → durables. **STOP at P3-9 — do NOT start P3-10/SIGNAL ERROR.** Ledger ENDS **C367**; inventory 1260/186; census `b080894` done; goldens NEVER re-derived; `pli80c` POSITIONAL into FRESH paths; ALWAYS `git diff --cached --stat` before commit; chain 01a1af4f 4/12 cap 12; no push.

0a-novies-new25. **E2E-52/P3-9 hop 6 CLOSE PART 1 — CENSUS LANDED; C367→COVERAGE→GATE→RESULTS→DURABLES OWED; RENEWAL PENDING (2026-11-06, session 01a1af80, chain 01a1af4f renewal 2/12; ZERO oracle; goldens NEVER touched; `handoff.config.json` NEVER staged; no push; all rc DIRECT).** Recovery verified; build rc=0 binary `11c6283e75b60fe3…` == STATE; 11/11 cmp re-held from committed tree; g402 blocks committed `618fbe6`; **census OWN path `b080894`**: rc=0, counts **15/0/26/0 UNCHANGED**, LOAN2 message MOVED VERBATIM to `codegen: statement kind not in supported subset [TBD] (line 92)` (PREDICTED=MEASURED, NEVER fix), EXPR1/EXPR2 unchanged. Durables `ebbab52`: C367 byte authority re-verified FIRST-HAND (VAR-FIRST VG/VI reloc pairs incl shared zero10 cell [C155]; CODE sizes VA 001C VB/VC/VD 0026 VE 002C VF 003C VG 0047 VH 002F VI 0076 VJ 0025 VK 0080; RB falsified by VC byte-identity, SN by VE head `2A`; F5-sandwich mechanism PROPOSED) + the three pre-registration falsifier classes for RESULTS §P3-9 (PAR; hop-4/5 literal-first incl PLAN §4 VG order; EVERY §4 CODE-size SHORT — they omitted the `x = 2;` continuation). **SUCCESSOR:** execute `PROGRESS.md` → `## Next action` steps (2)–(6): **C367 measured-bytes-only committed to `spec/CLAIMS.md` BEFORE ANY `spec/COVERAGE.tsv` touch** (bullet contract = LEARNINGS § "hop 6 CLOSE PART 1" STILL OWED (i)) → `COND.OR` row + EXPLICIT `spec/COVERAGE-IDS.txt` line (NEVER `coverage_gen.py`; verify diff ≈ 2 lines by content) + coverage_check/prose rc=0 → FULL gate rc=0 DIRECT `build/gate-e52p9-reg.log` (expect 1260/0, 186/186, 9/9, rows 0/0, census 15/0/26/0, prose 5) → RESULTS §P3-9 + PLAN §5 + §P3-9 CLOSED → durables. **STOP at P3-9 — do NOT start P3-10/SIGNAL ERROR.** Ledger ENDS **C366** (C367 owed); inventory 1260/186; goldens NEVER re-derived; `pli80c` POSITIONAL into FRESH paths; ALWAYS `git diff --cached --stat` before commit; chain 01a1af4f cap 12; no push.

0a-novies-new24. **E2E-52/P3-9 hop 6 REMAINDER PART CLOSED — O-1/MARKERS/SWEEP/EXPR/SPECIMENS+INVENTORY LANDED; RENEWAL PENDING (2026-11-06, session 01a1af69, chain 01a1adf0; ZERO `ocaml/` byte except line-preserving comment fix `1356b8b`; ZERO oracle; goldens NEVER touched; `handoff.config.json` NEVER staged; no push; all rc DIRECT).** Commits: `1356b8b` (ODecEq0 stale-comment VAR-FIRST correction, parity re-held), `bdbc28a` (SPECIMENS +11 measured-bytes block + `--update-inventory` 1249→**1260 EXACTLY +11**, refusals 186), `c059c56` (durables), this + guard **g400-7658c0d8563c refreshed+attested — renewal scheduled, successor receives ONLY the durable files**. ACCEPTED this hop: recovery verified; FULL fresh `--build-dir` rebuild deterministic; histogram **68/124 == baseline**; **11/11 E52VA..VK whole-file cmp rc=0 re-verified from the COMMITTED tree** (golden cmp, NOT the recorded hash, is the authority — `c621ea8c…` unreproducible, current `11c6283e75b60fe3…`); O-1 `build/e52p9-arm/loan2-decode.txt` raw-reldump: :91 ladder-first/`<0`-last/one-F2 + `?SIGOP@035E` unarmed; :113 DEC pair **VAR-FIRST verbatim** (LXI &P@02CA then *zero@01E6; ADD==VAR-first here), EqVV-LATER hoist, one F2→0603; :120 Gt0-And-right `21`-hoist + `AF BE 23 9E`, C1 A0, NEW: then-body ONLY `call summary();`, `m=m+1` OUTSIDE the if, slot 0601 = `call display(...)`; VG DATA **0014** / VI **001A** from DEF-DATA records (hop-4 VI 001B FALSIFIED, off-by-one; console `data=` COSMETIC). EXPR1/EXPR2/LOAN2 POSITIONAL VERBATIM (LOAN2 `(line 92)`, NEVER fix); markers 10/10 rc=0; sweep FAILS 0. LESSONS: `--update-inventory` STAGES its file — ALWAYS `git diff --cached --stat` before commit (config rode into `57fc210`, soft-reset repaired, NEVER pushed); `pli80c` POSITIONAL into FRESH paths — stale .REL FALSE-PASSes cmp. **SUCCESSOR:** execute `PROGRESS.md` → `## Next action` (hop 6 REMAINDER) steps (1)–(6): census `--check` OWN path → **C367 measured-bytes-only BEFORE ANY COVERAGE touch** → `COND.OR` row + EXPLICIT `spec/COVERAGE-IDS.txt` line (NEVER `coverage_gen.py`) + coverage_check/prose rc=0 → FULL gate rc=0 `build/gate-e52p9-reg.log` → RESULTS §P3-9 + PLAN §5 + §P3-9 CLOSED → durables. **STOP at P3-9 — do NOT start P3-10/SIGNAL ERROR.** Ledger ENDS **C366** (C367 owed); gate inventory now 1260/186 (last full gate ran at 1249 — successor re-runs); goldens NEVER re-derived; chain 01a1adf0 cap 12.

0a-novies-new23. **E2E-52/P3-9 hop 5 PART 6 — FINAL ARM PLAN LANDED; ARM EXECUTION OWED; session RENEWING (2026-11-06, session 01a1ae6a, chain 01a1adf0 renewal 6/12; ZERO `ocaml/` byte, ZERO oracle; build rc=0 binary `9ecea27aa4f2d80f49ad…` == baseline; all rc DIRECT; `handoff.config.json` NEVER staged; no push).** Commit `8a7cc32`. New accepted facts: every VA–VK emission list re-confirmed byte-for-byte against `build/e52p9-arm/goldens-dump.txt`; `dec_eq_bool_parts` is VAR-first and matches only var-vs-var — fold DEC `=0` operands emit via the NEW literal-first materialiser in `lower_or` DIRECTLY, never through lower_bool's DEC arms; LOAN2 declares `P fixed decimal(10,2)` (lines 16–22) ⇒ LOAN2:113 witnesses **EqVV in a LATER fold slot** and :120 **Gt0 as And-right** — original-golden decode, panel-unverified = obligation O-1 (re-derive via reldump to `build/e52p9-arm/loan2-decode.txt`, record in C367). The complete plan (placement as `let rec lower_bool … and lower_or …` between @7274/@7276, class head/tail byte lists, node1 rules with BY-NAME refusals, the 7 edit sites, obligations O-1/O-2/O-3) is `LEARNINGS.md` § "hop 5 PART 6" — read it FIRST, then § PART 4 + § PART 3 + § PART 2. **SUCCESSOR:** `PROGRESS.md` → `## Next action` steps (2)–(5): arm codegen.ml ONLY; build rc=0 + histogram vs 68 + cmp VA–VK whole-file vs `golden/e52p9/` + sweep FAILS 0 + markers (CRLF+bare ^Z) + LOAN2/EXPR1/EXPR2 POSITIONAL VERBATIM (predicted `signal error` 92, NEVER fix); registration 1249→1260 (census OWN path, C367 measured-bytes-only BEFORE COVERAGE, COND.OR row + explicit spec/COVERAGE-IDS.txt line, NEVER coverage_gen.py), gate rc=0 build/gate-e52p9-reg.log; RESULTS §P3-9 + PLAN §5 + CLOSED, durables. STOP at P3-9 — do NOT start P3-10. Ledger ENDS C366; gate 1249/186/9/140-0-0 SUPPORTED 90, census 15/0/26/0; binary `9ecea27aa4f2d80f49ad…` == baseline; goldens NEVER re-derived; no push; rc DIRECT; pli80c POSITIONAL; chain 01a1adf0 6/12, cap 12.

0a-novies-new22. **E2E-52/P3-9 hop 5 PART 4 — arm-session verifications + THREE CORRECTIONS written; ARM OWED; session RENEWING (2026-11-06, session 01a1ae54, chain 01a1adf0 renewal 5/12; ZERO `ocaml/` byte, ZERO oracle; `handoff.config.json` NEVER staged; no push; all rc DIRECT).** Build rc=0 binary `9ecea27aa4f2d80f49ad…` == baseline; goldens-dump + probes re-read, every VA–VK region re-confirmed against PART 2/3. CORRECTIONS (LEARNINGS § "hop 5 PART 4", read FIRST, then § PART 3 algorithm + § PART 2 emission lists): (1) `is_plain_bin_auto` does NOT exist — gate = `is_plain_num_auto` @4040 + own `Eident` name extraction; (2) `hl_bias`/`cmp_load_deref` are AFTER `lower_bool` @7276 — fold machinery MUST sit BEFORE lower_bool, inline `op_lhld`+reloc+literal bytes only (plain-gated operands); (3) fold GtC ladder gated k∈{1,2} (DCX×(k+1); k≥3 in-fold refuses BY NAME [TBD]). Anchors: Or test-arm after @8531; `<0` TEST arm (textual `Enumber "0"`) BEFORE @8628; lower_bool Or fold + full arms GtC/Gt0/EqVV/Lt0/DEC-Or + saved-match clauses (NEVER alter And bytes; cross-var rule-2, `a<0|x|y` n≥3, other-var swap all refuse BY NAME); bit_cond_mat Or arm before `_ -> None` @~8316, caller BARE `32` @~9962 stays; DEC literal-first NEW materialiser via `dec_pool`, NEVER `dec_eq_bool_parts`; prescan parity CONFIRMED no edit. **SUCCESSOR:** `PROGRESS.md` → `## Next action` steps (2)–(5): arm codegen.ml ONLY; build rc=0 + histogram vs 68 + cmp VA–VK vs `golden/e52p9/` + sweep FAILS 0 + markers (CRLF+bare ^Z) + LOAN2/EXPR1/EXPR2 POSITIONAL VERBATIM (predicted `signal error` 92, NEVER fix); registration 1249→1260 (census OWN path, C367 measured-bytes-only BEFORE COVERAGE, COND.OR row + explicit spec/COVERAGE-IDS.txt line, NEVER coverage_gen.py), gate rc=0 build/gate-e52p9-reg.log; RESULTS §P3-9 + PLAN §5 + CLOSED, durables. STOP at P3-9 — do NOT start P3-10. Ledger ENDS C366; gate 1249/186/9/140-0-0 SUPPORTED 90, census 15/0/26/0; binary 9ecea27aa4f2d80f49ad == baseline; goldens NEVER re-derived; config NEVER staged; no push; rc DIRECT; pli80c POSITIONAL; chain 01a1adf0 5/12, cap 12.

0a-novies-new21. **E2E-52/P3-9 hop 5 PART 3 — every arm site READ AND PINNED on THIS tree; the FINAL fold algorithm + operand classifier + registration subset written; the ARM EDIT STILL OWED, ZERO `ocaml/` byte, ZERO oracle (2026-11-06, session 01a1ae44, chain 01a1adf0 renewal 4/12; operator `handoff.config.json` NEVER staged; no push; all rc DIRECT).** Commits: this + `5f3a281`. ACCEPTED (verified by code reading THIS session): `is_plain_bin_auto` @3980 is the exact OR-operand gate (plain Vint auto only); And test-arm @8526-8529 (`lower_bool; op_jp; slot` — the Or test-arm goes beside it); `EqR Lt` refusal arm @8629 (VA `<0` TEST arm `3A r(cell+1)/B7/F2` inserted BEFORE it; refusal survives for non-auto); `lower_bool` @7276, fold ends `C1 A0` @7337, conj_bin_zero right-operand path (`val_addr; F5; bin_zero_tail`) is VE's hoist mechanism verbatim; `bit_cond_mat` @8105 ends `| _ -> None`, caller emits the BARE `32 STA` @9962-9965; `bit_store_cond_bytes` @3426 counts only string cells so VK stmt3 demands nothing; prescan Or descent @3410 + `EqR _` DEC literal demand — parity CONFIRMED, NO prescan edit; DEC OR materialiser = NEW `pre = 21 r(zero cell via dec_pool)` / `post = MVI A,p/?DLDOP/21 r(var)/MVI A,p/?DLDOP/?DCMOP/D6 01 9F` LITERAL-FIRST — **NEVER touch `dec_eq_bool_parts`** (hoists the VAR, And bytes frozen); F5/POP-B mechanism UNDERSTOOD (flags byte carries S=truth bit7; HL-only heads ride above F5, `3A` is atomic). The full fold algorithm (left-spine flatten, node1 swap rules 1–2 node-local, `C1 B0`, ONE F2), the six-operand classifier, and the per-probe registration subset (11 probes: 6×128 + 4×256 + VI 384; inventory 1249→**1260**, refusals 186) are in `LEARNINGS.md` § "hop 5 PART 3" — read it FIRST, then § "hop 5 PART 2" emission lists. **SUCCESSOR:** execute `PROGRESS.md` → `## Next action` steps (2)–(5): arm codegen.ml ONLY; build rc=0 + histogram vs 68 + cmp VA–VK whole-file vs `golden/e52p9/` + sweep FAILS 0 + markers (CRLF+bare ^Z) + LOAN2/EXPR1/EXPR2 POSITIONAL VERBATIM (predicted blocker `signal error` 92, NEVER fix); registration from 1249 (`--update-inventory`, census OWN path, **C367 measured-bytes-only BEFORE COVERAGE**, explicit `COND.OR` row + `spec/COVERAGE-IDS.txt` line, NEVER `coverage_gen.py`), gate rc=0 `build/gate-e52p9-reg.log`; RESULTS §P3-9 + PLAN §5 + CLOSED, durables. **STOP at P3-9 — do NOT start P3-10.** Ledger ENDS **C366**; gate 1249/186/9/140-0-0 SUPPORTED 90, census 15/0/26/0; binary `9ecea27aa4f2d80f49ad…` == baseline; goldens NEVER re-derived; `pli80c` POSITIONAL; chain 01a1adf0 4/12, cap 12.

0a-novies-new20. **E2E-52/P3-9 hop 5 PART 2 — arm-time facts VERIFIED by code reading; the ARM itself is still OWED (2026-11-06, session 01a1ae33, chain 01a1adf0 renewal 4/12; ZERO `ocaml/` byte, ZERO oracle, goldens untouched, no push, operator `handoff.config.json` NEVER staged).** Commits `8e86ad2`+`96ab96e`+this block. ACCEPTED: parser is LEFT-assoc precedence-climbing `Or=10 < And=20 < rel=30` (VK parses exactly as the goldens show); `F5 PUSH PSW` saves the LEFT truth byte in A, so only HL-only prefixes (`21`/`2A` + `hl_bias`) hoist and `3A` is ATOMIC — that is rule 1's mechanism; the DEC `= 0` OR operand is `dec_push(literal)` then `dec_push(var)` + `?DCMOP` + `D6 01 / 9F`, and `dec_pool`/`dec_cell_addr` REUSES the cell `prescan_cond` already demands through its general `Ebinary` descent (parity holds — NO prescan edit). Insertion points pinned: Or test-arm beside And @8526, Or fold beside And in `lower_bool` @7276 (`C1 POP B / B0 ORA B 0xB0`), `<0` TEST arm BEFORE the `EqR Lt` arm @~8630 (plain `Vint` auto only; its existing `[TBD]` refusal must survive), value-position arm in `bit_cond_mat` @8105 with the `32 STA` left at the caller ~9963. E52VB re-measured rc=2 at the 9154 catch-all — nothing armed. PROPOSED (adjudicate against the goldens, never adopt silently): rule-2 swap only for same-var FIXBIN `=0`-then-`>c` (unhoisted in VE, hoisted in VF — witnessed, unexplained; record in C367); `a<0|b|c` has NO witness → refuse BY NAME; ident-vs-ident `=` splits head `2A r(l)` / tail `E5/…/9F`; DEC-vs-ladder keeps source order; OR DEC literal-first with the residual ADD-vs-literal-first ambiguity recorded VERBATIM. FALSIFIED (inherited, still in force): the hop-5 design's `dec_eq_bool_parts` reuse — it hoists the VARIABLE (AND route) and editing it would alter And bytes. **SUCCESSOR:** execute `PROGRESS.md` -> `## Next action` steps (2)-(5): arm `ocaml/lib/codegen.ml` ONLY per `LEARNINGS.md` § "hop 5 PART 2" emission lists, build rc=0 + histogram vs 68 + cmp VA–VK whole-file vs `golden/e52p9/` + sweep FAILS 0 + markers (CRLF + bare `^Z`) + LOAN2/EXPR1/EXPR2 POSITIONAL VERBATIM (expected next blocker `signal error` 92, NEVER fix); registration from 1249, **C367 measured-bytes-only BEFORE COVERAGE** (explicit `spec/COVERAGE-IDS.txt` line, NEVER `coverage_gen.py`), gate rc=0 `build/gate-e52p9-reg.log`; RESULTS §P3-9 + PLAN §5 + CLOSED; durables. **STOP at P3-9 — do NOT start P3-10.** Ledger ENDS **C366**; gate 1249/186/9/140-0-0 SUPPORTED 90, census 15/0/26/0; binary `9ecea27aa4f2d80f49ad…` == baseline; goldens NEVER re-derived; all rc DIRECT; `pli80c` POSITIONAL.

0a-novies-new18. **E2E-52/P3-9 hop 4 PART DONE — fold ORDER LAW candidate-PINNED from RAW bytes; ARM (hop 5) OWED, then STOP at P3-9 closure (2026-11-06, session 01a1adf0; ZERO `ocaml/` byte, ZERO oracle, goldens `9bb3f99` untouched, no push).** Durables `eacb798`. ACCEPTED (raw hex + reloc records are the authority; hop-3 `vdumps.txt` DB-D6 desync = display artifact, `reldumps.txt` DATA-size lines WRONG — VG 0014, VI 001B from DEF-DATA records): fold = LEFT-assoc post-order, LEFT truth byte `F5`-pushed, RIGHT computed after push, `C1 POP B / B0 ORA B`, ONE terminal `F2 JP`; rule 1 `<0` LDA computed LAST in its node (VB==VC byte-identical, VD separate-var, VJ, VF node3, LOAN2:91); rule 2 SAME-VARIABLE FIXBIN `=0` immediately followed by `>c` ladder -> ladder produced+pushed FIRST, zero-test after the F5 (VE, VF node1) — DIFFERENT-variable zero-vs-ladder UNMEASURED, must refuse BY NAME [TBD]; rule 3 everything else source order (VI stmt1/2, VG, LOAN2:113). DEC zero-operand LITERAL-FIRST CONFIRMED (VG cells@9/14 before vars@0/5; VI zero10@11/zero9@17 before p@0/q@6; ANNUITY:46) — **PAR FALSIFIED**; ADD vs literal-first indistinguishable on pool-above-data layouts (record in C367). In-fold `<0` = BARE `3A r(cell+1)` (bit7 IS truth, NO B7); standalone `<0` TEST (VA) = `3A r(cell+1) / B7 / F2 slot`. VH: two independent patch targets. VK head: precedence AND-fold sandwich first; value-position OR = fold then BARE `32 <bitcell>` (no D6/9F) — re-derive every VK byte from the golden before arming. PROPOSED (arm-time): minimal `tools/dis80.py` fix `0xD6:('SUI',2)` + `0x2F:('CMA',1)`, verify on E52VE/VG/VI. **SUCCESSOR:** execute `PROGRESS.md` -> `## Next action` hop-5 contract EXACTLY: arm ONLY measured shapes (`lower_test_skip0` Or arm + `lower_bool` Or fold; NEVER alter And), build rc=0 + histogram 68, cmp VA–VK whole-file, sweep FAILS 0, markers (CRLF+bare ^Z), LOAN2/EXPR1/EXPR2 POSITIONAL VERBATIM (record new blocker, NEVER fix; ?SIGOP out of scope), register exact subset, **C367 BEFORE COVERAGE** (explicit COVERAGE-IDS.txt edit, NEVER coverage_gen.py), gate `build/gate-e52p9-reg.log`, RESULTS §P3-9 + PLAN §5 + CLOSED, durables. STOP at P3-9; do NOT start P3-10. Ledger ENDS **C366**; gate baseline **1249/186/9/140-0-0**, census 15/0/26/0; binary `9ecea27aa4f2d80f49ad…` == baseline; operator `handoff.config.json` NEVER staged; all rc DIRECT; `pli80c` POSITIONAL.

0a-novies-new19. **COVERAGE LEDGER INTEGRITY HARDENING COMPLETE — the `0cf0688` clobber class is mechanically blocked; FULL gate re-confirmed rc=0 on the final tree; STOP reached (2026-11-05, session 01a1ac5b; tools+spec+docs only, ZERO `ocaml/` byte, ZERO new oracle call, goldens NEVER touched, no push, operator `handoff.config.json` NEVER staged).** Commits: `2728890` tracked manifest `spec/COVERAGE-IDS.txt` initialized ONCE from the repaired 140-row ledger (never tool-regenerated) → `872fa22` `coverage_check.py` contract-identity invariant (EXACT set comparison ledger-vs-manifest: removed/renamed/substituted contracts fail even when every surviving row is internally valid; missing manifest fails CLOSED) + stats gating (canonical `coverage-stats.json` written ONLY after a clean validation; CLI preserved, new `--ids`/`--stats-path`) + `COVERAGE-SCHEMA.md` documentation → `85e0726` `coverage_gen.py` neutralized to an inert fail-closed stub (rc=2, AST-clean of write/rename/delete, points to COVERAGE.tsv + coverage_check.py; destructive implementation NOT preserved on any executable path) → `a5670e5` `tools/test_coverage_integrity.py` (36 checks rc=0: every required falsification rejected, every legitimate evolution accepted; canonical stats proven byte-untouched by all failure cases; LIVE sandbox gate test — the normal compile-tier pre-flight aborts on a missing contract before any specimen compiles; LESSON: invoke the SANDBOXED gate path, a real-path gate resolves ROOT to the valid ledger) → `1a2c40b` [C366] narrow wording correction: NO relocation ON THE ARGUMENT OPERAND (the registration DOES carry the `?ONCOP` CHAIN-EXT and the jump-over `RELOC code`; former overbroad phrase kept inside the claim as a labelled metadata correction; all measured bytes/shas/references VERBATIM). **VERIFIED:** full `python3 tools/e2e_gate.py` rc=0 DIRECT `build/gate-coverage-integrity.log` — **1249/0, 186/186, 9/9, coverage 140 rows 0 errors 0 warnings (SUPPORTED 90), census 15/0/26/0, prose 5**; COVERAGE.tsv sha `ba1ca9b11e2934a4…` and stats sha `39e096d5fcfc9fcf…` byte-identical to the repaired P3-8 state; no contract removed/renamed/reclassified; no goldens or compiler changes. **STATE:** ledger ENDS **C366**; binary `9ecea27aa4f2d80f49ad…`; LOAN2 UNMODIFIED rc=2, first blocker VERBATIM `codegen: condition form not in E2E-3b subset [TBD]: (| (< dl 0) (> dl 2))` = LOAN2:91, NOT fixed. **SUCCESSOR: the task's STOP is reached — P3-9 remains UNSTARTED and is an operator decision; do NOT implement OR conditions, touch `lower_test_skip0`, add probes, run the oracle, change LOAN2, or start PLILIB/MIR.** Residual: three inert `build/e2e-<pid>/` scratch dirs from accidentally-completed real-path gate runs during test development (generated working state, left in place per policy).

0a-novies-new18. **E2E-52/P3-8 SUBROUND FULLY CLOSED — RESULTS §P3-8 + PLAN §5 ROW + §P3-8 CLOSED LANDED, and the SUCCESSOR FOUND + REPAIRED A LEDGER CLOBBER (2026-11-05, session 01a1abba, renewal 1/12; docs-only, ZERO `ocaml/` byte, ZERO oracle call, goldens NEVER touched, no push, operator `handoff.config.json` NEVER staged).** Commits: `9adf3fc` guard g368 blocks VERBATIM → `86db760` RESULTS §P3-8 (campaign e52p8 **6 ok/6**, H1–H6 **ALL CONFIRMED**, per-probe measured table UA 128/0020/0002 · UB 256/0030/0004 · UC 256/0046/0008 · UD 128/0020/0002 · UE 256/002B/0002 · UF 384/002F/0002+COMMON F,G 0023, first-draft prologue-omission falsifier KEPT VERBATIM, CRLF+`^Z` marker-materialisation procedure, LOAN2/EXPR1/EXPR2 advances VERBATIM, registration 1249 + **C366** BEFORE COVERAGE, §6 BYTE-TIER-ONLY NOT-say, **§7 the defect record**) + PLAN §5 P3-8 row + §P3-8 CLOSED. **THE DEFECT (accepted, measured): `0cf0688` did NOT land the COVERAGE rewrite — `tools/coverage_gen.py`, an obsolete generator with a hard-coded E2E-36-era row list ending in `os.replace('spec/COVERAGE.tsv')`, was run "as the stats' own write path" and CLOBBERED the ledger 141→72 lines (133 deletions), leaving `COND.ON_ERROR` at REFUSED/NONE; the commit's own `coverage-stats.json` delta proved the intended numbers were computed against the GOOD file, and the pre-clobber gate `244f6e1` could not see damage done after it. REPAIR: restored from `git show 17c9963:spec/COVERAGE.tsv` + re-applied the row by csv column-edit (id KEPT, historical contract sentence VERBATIM, SUPPORTED/**EXACT:6**, probes E52UA..UF, corpus the five ON-ERROR census users ANNUITY,COPYLPT,EXPR1,EXPR2,LOAN2, boundary = my BY-NAME refusals + byte-tier-only + the three census advances VERBATIM, provenance [C366][C109][C364][C206][C208][C120][C202]). VERIFIED rc DIRECT: `coverage_check.py` rc=0 **140 rows 0/0, SUPPORTED 90 == the committed stats (stats did NOT move — the consistency proof)**, `file_prose_check.py` rc=0; evidence `build/e52p8-reg/coverage-repair.log`, `prose-repair.log`. **LAW (accepted): the stats' OWN write path is `coverage_check.py` ALONE; `coverage_gen.py` must NEVER be run on this tree; verify a ledger rewrite by CONTENT (`git diff --stat` ≈ one line) and by re-reading the row, never by a validator exit code alone.** Two sub-falsifications: the row's "BEGIN-body handler is a second refusal" is FALSIFIED by E52UD (lowered), while `N80_ON_HANDLER_BEGIN` still refuses on `procedure without name` from its BIT(1) STATIC INITIAL body — an unrelated parser my-gap; and `corpus=UPDATE,OPTIMIST` was FALSE (`grep -il "on error" artefacts/*.PLI` = those five names). `spec/CLAIMS.md` was NOT touched; tightening [C366]'s "NO relocation of any kind in its registration" phrase is PROPOSED only. **STATE:** HEAD after `87ebe5f` (LEARNINGS); ledger ENDS **C366**; binary `9ecea27aa4f2d80f49ad…` build rc=0 re-held; LOAN2 still rc=2/NO .REL at the VERBATIM condition-form blocker (LOAN2:91), NOT fixed. **SUCCESSOR: P3-8 is CLOSED — the brief's STOP is reached; do NOT start P3-9, no oracle, no PLILIB/MIR. PROPOSED (never authorization): ONE full `python3 tools/e2e_gate.py` re-run to confirm the combined state after the restore; neuter/delete `tools/coverage_gen.py`; add a gate assertion that the COVERAGE row count never shrinks without a labelled correction.**

0a-novies-new17. **E2E-52/P3-8 hop 3 REMAINDER CLOSED — VALIDATION + LOAN2 MEASUREMENT + REGISTRATION + **C366** + COVERAGE ALL LANDED; ONLY RESULTS §P3-8 + PLAN §5 ROW + THE DURABLE COMMIT ARE OWED (2026-11-05, session 01a1ab9a, fresh chain renewal 0/12 used).** All rc DIRECT; goldens NEVER touched; ZERO new oracle call; NO push; operator `handoff.config.json` NEVER staged. MEASURED: clean rebuild rc=0 binary `9ecea27aa4f2d80f49ad…`, codegen per-File warning histogram **68 == baseline**, cmp UA..UF **6/6 whole-file rc=0**, sweep **FAILS: 0**, marker harness (`build/e52p8-reg/markers.py`) E46K4/K15/N21/E52PF/PU/PV/RE + SE/SF/SG all rc=2 **MARKER_FAILS: 0** — LESSON: it MUST materialise CRLF + bare `^Z` exactly as `run_negatives` does, or the refusal's reported line number moves and the registered marker misses (my first LF-only run falsified its own method). **LOAN2 VERBATIM** (sha `7be23ba390926c20…` @ HEAD `1dc53f4`, POSITIONAL) **rc=2, NO .REL**, first diagnostic VERBATIM `codegen: condition form not in E2E-3b subset [TBD]: (| (< dl 0) (> dl 2))` = LOAN2:91 `if dl < 0 | dl > 2 then` — **the ON ERROR line-58 blocker is CLOSED**; recorded, NOT fixed, never hardcoded. Registered `244f6e1`: SPECIMENS +6 (NoOverwriteDict accepted all six, no SUBSTITUTION), inventory 1243->**1249** (+6 exactly), refusals 186; census OWN path rc=0 counts **15/0/26/0** with EXPR1->`GET form … (line 21)` and EXPR2->`FLOAT expression shape builtin … (line 35)` recorded VERBATIM; FULL gate rc=0 `build/gate-e52p8-reg.log` **1249/0, 186/186, 9/9, 140 rows 0/0, census 15/0/26/0, prose 5**. **C366** `17c9963` from MEASURED BYTES ONLY (six goldens + fresh reldumps in `build/e52p8-reg/`) committed BEFORE the COVERAGE rewrite `0cf0688` (`COND.ON_ERROR` REFUSED/NONE -> SUPPORTED/**EXACT:6**, probes E52UA..UF, the falsified "not implemented here / unprobed" clause kept VERBATIM as HISTORICAL, perimeter = my BY-NAME refusals: expression/variable/string args, out-of-range/multiple args, ERROR+STOP/RETURN/NULL/DCL, nested STOP, UNDEFINEDFILE STOP route, `REVERT ERROR`; byte-tier only, NO runtime-recovery claim); coverage_check rc=0, stats own path rc=0, prose rc=0. Ledger ENDS **C366**. **SUCCESSOR (docs-only, then STOP):** execute `PROGRESS.md` -> `## Next action` — RESULTS §P3-8 table + PLAN §5 row + PLAN §P3-8 CLOSED marker, prose rc=0 standalone, `/handoff` + commit HANDOFF/PROGRESS managed blocks VERBATIM. PROPOSED next subround (NOT authorized, NOT to be started this hop): the compound-condition class at LOAN2:91 (`my-gap`, OR-of-relations) — decode EXISTING E37/E38 `COND.*` goldens first, then pre-register PLAN §P3-9 + probes BEFORE any `ocaml/` byte.

0a-novies-new16. **E2E-52/P3-8 hop 2 CLOSED — PLAN §P3-8 + probes E52UA..UF PRE-REGISTERED at `e6d16ff` BEFORE any `ocaml/` byte; CAMPAIGN `e52p8` MEASURED 6 ok/6 with EVERY prediction HIT; GOLDENS COMMITTED VERBATIM `9f36504`; THE ARM (hop 3) OWED (2026-11-05, session 01a1ab34, renewal 2/12; ZERO `ocaml/`).** ACCEPTED: **H1** ERROR registration = `21 <arg 16-bit LE>` ABSOLUTE `/ AF` (XRA A) `/ CD ?ONCOP` `/ C3 <over>` = 10 bytes, with **NO `LINK-DEF-COMMON`/`SEL-COMMON`/`RELOC common` record at all** in a file-less object; **H2** the argument IS that LXI operand verbatim (`error(2)` = `21 02 00`, `error(0)` = `21 00 00` = bare); **H3 the tail is BODY-DEPENDENT — UF proves it inside ONE object: `on endfile(f) stop;` = inline `CD ?STOPX` and NO `C9`, while `on endfile(g) x = 1;` in the same program carries `C9` @0025; UA (statement body) and UD (plain `begin; x = 1; end;`) both emit `C9`** — so my `codegen.ml` unconditional RET is a CONFIRMED my-gap with measured fix ground; **H4** returning handlers demand NO SP-cell and NO pad (UA/UD/UE DATA 0002, no `DAD SP`), goto handlers do (UB cell@2 0004, UC cell@6 0008); **H5** UB (remote label) = TWO independent patch targets (slot 0015→0x1A continuation, slot 0018→pad 0x20), UC (adjacent) = merged at 0x36 [C208]; **H6** all six DR-ACCEPTED (`NO ERROR(S)` both passes) including the direct form `on error goto lbl;`. Sizes: UA 128 B/CODE 0020, UB 256/0030, UC 256/0046, UD 128/0020, UE 256/002B, UF 384/002F (COMMON F,G each 0023). **SUCCESSOR = hop 3 ARM + REGISTRATION** — full byte-level contract in `LEARNINGS.md` § "P3-8 hop 2 CLOSED" and `PROGRESS.md` → `## Next action`: a SECOND prefix encoder beside `on_reg_prefix` (never mutate the file one), admit `error` bare + ONE integer literal only (every other shape refuses BY NAME [TBD]), body-dependent `C9` suppression ONLY where measured, then build rc=0 DIRECT + per-File warning histogram vs **68**, cmp 6/6 whole-file vs `golden/e52p8/`, sweep **114**, markers E46K4/K15/N21/E52PF/PU/PV/RE + SE/SF/SG rc=2, LOAN2 POSITIONAL VERBATIM (record the new blocker, NEVER fix), SPECIMENS +6 + sanctioned `--update-inventory` from **1243**, census OWN write path FIRST, FULL gate rc=0 `build/gate-e52p8-reg.log`, **C366 from MEASURED BYTES ONLY BEFORE the COVERAGE rewrite**, coverage_check + prose rc=0, RESULTS §P3-8 + PLAN §5 row, durables. Ledger ENDS **C365**; binary `8b374e623bc9e280fa14…` == baseline (untouched); goldens NEVER re-derived; operator `handoff.config.json` NEVER staged; all rc DIRECT (never a pipeline tail); `pli80c` POSITIONAL; no push; byte-tier only — no runtime claims.

0a-novies-new15. **E2E-52/P3-8 hop 2 PART DONE — ANNUITY AMBIGUITY CLOSED + A RET-TAIL DEFECT FOUND IN MY OWN ARM; PLAN §P3-8 + PROBES E52UA..UF OWED (2026-11-05, session 01a1ab1e, renewal 1/12; ZERO `ocaml/`, ZERO oracle).** ACCEPTED (clean linear disassembly, `build/e52p8/ondump2.py` → `build/e52p8/onregions.txt`; dis80's reldump-TEXT mode prints reloc operands as `.` and produced FALSE gaps — the bitstream decoder is the honest tool): **all FIVE ON ERROR witnesses agree** — prefix `LXI H,<arg ABS 16-bit LE> / XRA A / CALL ?ONCOP / C3 <over>` (7 B, one SHORTER than the file-scoped [C109]/[C364] prefix, NO SEL-COMMON/reloc; bare = 0000, `error(1)` = 0001), handler INLINE, trailing `C3` goto chain, **NO C9**, pad `LHLD <block SP cell>/SPHL/CALL ?RECOV` AT the label — LOAN2 00E8/010E/0111 d0318, ANNUITY 004B/0071/0074 d0136, COPYLPT 00A6/00C7/00CA d0214, EXPR1 001B/005B/005E d0040, EXPR2 001B/0054/0057 d00AD. **FALSIFIED:** hop-1's "ANNUITY retry NOT adjacent / 0074 mid-dump ambiguous" (a column-shifted hex artifact of `ondump.py`) — ANNUITY is the ordinary adjacent-label case. **ACCEPTED (new my-gap, recorded NOT fixed):** `codegen.ml` emits `C9 RET` UNCONDITIONALLY after non-goto ON handlers on [C109]'s authority, but EXPR1/EXPR2 measure `on endfile(sysin) stop;` = inline `CALL ?STOPX` with **NO C9** — the tail is **BODY-DEPENDENT**; no registered specimen has a STOP-bodied handler, so the byte panel cannot catch it; ON ERROR arming must never copy the blind RET. Verification: build rc=0 binary `8b374e623bc9e280fa14…` == baseline; prose rc=0; LOAN2 line-58 blocker VERBATIM rc=2; E52U* collisions EMPTY; tag `e52p8` UNUSED. HEAD after this closure: `fd378e1` (durables) + this block; ledger ENDS **C365**; gate 1243/0 186/186 9/9 140-0-0 census 15/0/26/0. **SUCCESSOR = the rest of hop 2, from `PROGRESS.md` → `## Next action`:** write PLAN §P3-8 (H1 abs-LXI+XRA prefix; H2 argument verbatim; H3 body-DEPENDENT RET; H4 returning handlers demand NO SP-cell/pad [C206]; H5 jump-over = continuation, adjacency merges [C208]) + probes **E52UA** bare error+assignment, **UB** bare error + DIRECT goto to a REMOTE label, **UC** LOAN2-mirror begin…goto adjacent, **UD** plain RETURNING begin handler (RET? pad? UNMEASURED), **UE** `error(0)`/`error(2)` literals, **UF** `on endfile(f) stop;` + `on endfile(f) x = 1;` contrasts — CRLF + bare ^Z + ≤71 cols, E52SA skeleton — **COMMITTED BY EXPLICIT PATH BEFORE ANY `ocaml/` BYTE**, then ONE campaign `PLI_SRC=probes timeout 900 python3 oracle/batch.py E52UA E52UB E52UC E52UD E52UE E52UF --tag e52p8 --switches '$L$D'` rc DIRECT, goldens VERBATIM, arm ONLY measured shapes (SECOND prefix encoder beside `on_reg_prefix`, never mutate the file one; body-dependent RET; unmeasured shapes refuse BY NAME; ENDFILE/UNDEFINEDFILE regressions intact), cmp/sweep 114/markers/LOAN2 POSITIONAL VERBATIM, registration, gate rc=0 `build/gate-e52p8-reg.log`, **C366 measured-bytes-only BEFORE COVERAGE**, RESULTS §P3-8 + PLAN §5 row, durables. Constraints KEPT: no push; operator `handoff.config.json` NEVER staged; goldens NEVER re-derived; all rc DIRECT (never a pipeline tail); `pli80c` POSITIONAL; byte-tier only — no runtime claims; never hardcode LOAN2.

0a-novies-new14. **E2E-52/P3-8 hop 1 LANDED — ON ERROR DECODED & CONFIRMED on 5 original goldens; hop 2 = PLAN §P3-8 + probes E52UA..UF PRE-REGISTRATION, then ONE e52p8 campaign (2026-11-05, session 01a1ab05, ZERO ocaml/, ZERO oracle).** ACCEPTED: bare `on error` = `LXI H,0000 / XRA A / CALL ?ONCOP / JMP <over>` (absolute constant operand, condition byte 00 via AF — NOT a file event, NOT MVI A,nn; LOAN2 00E8, ANNUITY 004B); `error(1)` = `LXI H,0001` (COPYLPT 00A6, EXPR1/EXPR2 001B); goto-terminated BEGIN handlers inline + `C3`, NO RET ([C364] holds); pad at goto label, block-shared SP cell (LOAN2 d0318/COPYLPT d0214/ANNUITY d0136); `revert error(1)` measured UNARMED; `on endfile(sysin) stop;` has NO RET tail — C109 RET law is body-dependent, re-read before arming. AMBIGUOUS (clean disassembly owed): ANNUITY pad/jump-over geometry 0070-0078. UNMEASURED → probes: plain returning BEGIN handler, simple-statement handler, non-adjacent goto pad geometry, error literals beyond 0/1. FALSIFIED: slot-7 walk-back in my first-pass tool. SUCCESSOR: read `LEARNINGS.md` § P3-8 + `PROGRESS.md` → P3-8 hop-1 LANDED section; execute hop-2 contract: PLAN §P3-8 + probes COMMITTED BEFORE any ocaml/ byte, campaign `--tag e52p8 --switches '$L$D'` rc DIRECT, arm only measured shapes reusing on_reg_prefix where bytes agree, registration → gate → **C366 measured-bytes-only BEFORE COVERAGE** → RESULTS/PLAN rows → durables. HEAD after this closure: see git log; ledger ENDS **C365**; gate 1243/0 186/186 9/9 140 0/0 census 15/0/26/0; binary `8b374e623bc9e280…`; LOAN2 blocker line 58 re-verified; SE my-gap/SF-SG dr-refuses kept; goldens NEVER re-derived; operator `handoff.config.json` NEVER staged; all rc DIRECT; `pli80c` POSITIONAL; no push; byte-tier only.

0a-novies-new13. **E2E-52/P3-7 hop 5: SUBROUND P3-7 CLOSED — PERIMETER line-38 correction LANDED; FULL COMBINED-STATE GATE rc=0; SUCCESSOR = E2E-52/P3-8 ON ERROR PRE-REGISTRATION (operator-authorized) (2026-11-05).** Docs+ledger-boundary hop: ZERO oracle calls, ZERO `ocaml/` bytes. Idempotent recovery found the killed session's RESULTS §P3-7 + PLAN §5 row UNCOMMITTED and KEPT them verbatim (all cited hashes verified); only the PERIMETER correction was missing and was appended INSIDE the FILE-attribute-cluster row's final cell — falsified `Still refusing by name:` sentence kept VERBATIM HISTORICAL; PRINT/PAGESIZE/LINESIZE now implemented for MEASURED combinations [C365]; PAGE [C359]; file PUT/GET EDIT C360–C363, E41X8 refusal OBSOLETE; KEYED/DIRECT/RECORD/SEQUENTIAL/UPDATE/APPEND/ENVIRONMENT still unsupported on OPEN routes; titleless OUTPUT 0x0650 outside the measured implementation; unmeasured PRINT/attribute combos refuse BY NAME; NO all-combinations claim. Verification FINAL STATE, all rc DIRECT: prose rc=0, coverage rc=0 **140 rows 0/0**, FULL gate rc=0 `build/gate-e52p7-hop5.log` (**1243/1243, 186/186, 9/9, 140 0/0, census 15/0/26/0, prose 5**). Ledger ENDS **C365**; goldens NEVER re-derived; ON ERROR 58 NOT fixed; SE my-gap / SF-SG dr-refuses kept; operator `handoff.config.json` NEVER staged. GUARD STATE: prior chain 01a1aa7d consumed g352 (renewal 4/12); THIS session auto-checkpointed g354 UNATTESTED at level 4 — successor must `/handoff verify` then follow `PROGRESS.md` → `## Next action`: P3-8 DECODES existing LOAN2/E52p6 evidence FIRST, then preregisters PLAN §P3-8 + discriminating probes COMMITTED before any `ocaml/` byte; campaign `e52p8` only if goldens leave the ON ERROR questions open; ON ERROR is NOT presumed a file event — condition code + registration operand MEASURED independently. No push; all rc DIRECT; `pli80c` POSITIONAL.

0a-novies-new12. **E2E-52/P3-7 hop 4 PART DONE: COVERAGE LANDED `d9ebb30` (140 rows 0/0 + stats own path); RESULTS/PLAN/PERIMETER/prose/durables OWED at hop 5 (2026-11-05, renewal 4/12).** ZERO oracle. Landed: row `FILE.OPEN_STREAM` falsified `Still refused by name: PRINT/…` kept VERBATIM HISTORICAL + [C365], id KEPT; NEW `FILE.OPEN_PRINT_ATTRS` SUPPORTED EXACT:10 — corpus column validator FALSIFIED hop-3's list (P019B/P021 NOT census names → sit as golden evidence paths; corpus COPYLPT,DEPREC,KEYFILE,LOAN2,RETRIEVE); labelled CORRECTIONs on rows `FILE.OPEN_STREAM_OUTPUT` (KEYFILE:19 0x1E50 lowered as E52TE), `FILE.PUT_LIST`, `FILE.OPEN_TITLE_STATIC` (LOAN2 quote obsolete → ON ERROR 58). Recovery: build rc=0 binary `8b374e623bc9e280…`, gate 1243/0 (next gate expect coverage **140 rows 0/0**). SUCCESSOR: execute `PROGRESS.md` → `## Next action` hop-5 contract — RESULTS §P3-7 (measured table, H1–H5 CONFIRMED, TI falsifier + TG/TH totals falsifications VERBATIM, TJ accept, LOAN2/RETRIEVE advances, §6 byte-tier-only), PLAN §5 row, PERIMETER.md line-38 campaign-wide correction (kept verbatim; PAGE/PUT-EDIT clauses stale since E2E-42), prose rc=0 standalone, durables, renew 5/12 cap 12. NO new oracle campaign; ledger ENDS **C365**; goldens NEVER re-derived; ON ERROR 58 NOT fixed; SE my-gap/SF-SG dr-refuses kept; operator `handoff.config.json` NEVER staged; all rc DIRECT; `pli80c` POSITIONAL; no push; chain 01a1aa7d.

0a-novies-new11. **E2E-52/P3-7 hop 3: ARM BYTE-EXACT 10/10 + REGISTRATION 1-2/3 + GATE rc=0 1243/0 + CLAIM C365 LANDED; COVERAGE + RESULTS/PLAN + DURABLES OWED (2026-11-05, renewal 3/12).** Commits: arm `ccf0036` (codegen.ml ONLY), SPECIMENS +10 & inventory 1233→**1243** (+10 exactly, refusals 186) `6b8d851`, census OWN path rc=0 counts 15/0/26/0 with LOAN2→ON ERROR **58** and **RETRIEVE→ENVIRONMENT 31** VERBATIM (both predictions/advances, NOTHING fixed) `f6fd2b9`, **C365** measured-bytes-only BEFORE COVERAGE `a6e814f`, FULL gate REAL rc=0 DIRECT `build/gate-e52p7-reg.log`. Build rc=0 binary `8b374e623bc9e280…`, codegen histogram 68 == baseline after two draft fixes (`\u00a7`/`\u2014` text escapes → real chars; redundant `A_zero` subpat). **cmp TA..TJ 10/10 whole-file rc=0**, sweep **114/0** (bank grew past hop-12's 110 via SA..SD rows), markers rc=2 (E46K4/K15/N21/E52PF/PU/PV/RE + SE/SF/SG). SUCCESSOR: execute `PROGRESS.md` → `## Next action` hop-4 contract — COVERAGE row 52 rewrite (its `Still refused by name: PRINT/…` clause FALSIFIED, keep as HISTORICAL) + PROPOSED `FILE.OPEN_PRINT_ATTRS` row + coverage_check rc=0 (expect 140 rows) + stats own path, RESULTS §P3-7 + PLAN §5 row + prose rc=0, durables. FALSIFIED this hop and kept verbatim: TI predicted w6 `21 00 00`, DR wrote `60 68`; TG/TH 30-B totals measured 32/33 (encodings HIT); PRINT-is-spelled-OUTPUT falsified (0x0200 kept); global `\'` replace corrupted tools/e2e_gate.py — restored from `git show HEAD:` (only my own edit lost), py_compile rc=0. Ledger ENDS **C365**; goldens NEVER re-derived; ON ERROR 58 NOT fixed; SE my-gap/SF/SG dr-refuses kept; byte-tier only, no runtime assertions; operator `handoff.config.json` NEVER staged; all rc DIRECT; `pli80c` POSITIONAL; no push; renewal chain 01a1aa7d hop 3/12, cap 12.

0a-novies-new10. **E2E-52/P3-7 hop 2: CAMPAIGN e52p7 MEASURED (10 ok/10, ZERO dr-refuses) + ARM APPLIED; BUILD RE-VERIFY + CMPs + LOAN2 + SWEEP + COMMIT + REGISTRATION OWED (hop 3) (2026-11-05, renewal 2/12).** Goldens `golden/e52p7/` committed VERBATIM `272a996`. TG/TH byte-enc predictions HIT (pre-reg 30B totals FALSIFIED, kept verbatim); TI falsifier TRIGGERED (w6 zero = `60 68`, not `21 00 00`); TJ pagesize(300) DR-ACCEPTED via `21 2C 01`. `ocaml/lib/codegen.ml` arm (open_subset_keys+PRINT/PAGESIZE/LINESIZE, n_print guards + 0x0652 base, `open_attr_plan` measured matrix, `open_emit_words` ladder in all three title branches) UNCOMMITTED; ONE compile fix applied, `dune build` rc=0 UNVERIFIED since. Execute `PROGRESS.md` → `## Next action` hop-3 contract exactly; full decode in `LEARNINGS.md` § hop 2. Ledger ENDS C364; goldens NEVER re-derived; LOAN2 NEW blocker (predicted ON ERROR 58) recorded VERBATIM, NOT fixed; SE my-gap/SF/SG dr-refuses kept; operator `handoff.config.json` NEVER staged; all rc DIRECT (pipe trap fired again); pli80c POSITIONAL; no push; renewal 2/12 cap 12.

0a-novies-new9. **E2E-52/P3-7 hop 1: PRE-REGISTRATION LANDED — OPEN PRINT/PAGESIZE/LINESIZE (`2bca084`); ORACLE CAMPAIGN `e52p7` OWED (2026-11-05, fresh chain hop 1).** Recovery VERIFIED first: HEAD `c0ce1a1`, checkpoint **g341-6c8d927fdd83 current + attested** (all five source hashes replayed by hand — the supported `/handoff verify` has no CLI path, `LEARNINGS.md` § E2E-49/P4 records the replay), ledger ENDS **C364**, binary `0efc35e6d4ff81bd…` build rc=0, LOAN2 blocker re-measured VERBATIM at line 54 (`OPEN option PRINT … [TBD]`), P019B line 3 / P021 line 4 KEYED / RETRIEVE line 19 / KEYFILE line 16 / COPYLPT SKIP-count / DEPREC array all re-read. NO P3-6 work repeated. ZERO `ocaml/` byte, ZERO oracle call this hop: the whole PRINT/PAGESIZE/LINESIZE class was decoded from EXISTING evidence (`spec/lab-evidence/e2e41-p0/OPEN-BLOCKS.txt`, `OPEN-MATRIX.tsv`, `W1-BITFIT.txt`) into SIX measured block shapes A–F (P019B 0x0652/21 B; P021:6 0x2652/24 B with `2E 3C` MVI L + `68` MOV L,B; LOAN2:54 0x2E52/29 B — **PAGESIZE(0) is bit 0x2000 plus a ZERO word, it adds NO byte**; LOAN2:56 0x0E52/27 B `?SLVTS`; KEYFILE:19 0x1E50/31 B w6 `MVI L,3C`; COPYLPT:38 0x3E52/33 B variable attrs as `LHLD` + DATA reloc; zero-restoration when B≠0 is `6C MOV L,H`). Probes **E52TA..TJ** (10, all parse+bind, all refuse ONLY at the named OPEN option, rc=2) + PLAN §P3-7 predictions committed BEFORE any compiler byte; four genuinely UNDECIDABLE boundaries (TG titled w5-literal/w6-zero, TH both literals = P0 §10 E46A, TI variable pagesize alone, TJ `pagesize(300)` > 0xFF) carry byte-exact predictions and falsifiers, never fit. SUCCESSOR executes `PROGRESS.md` → `## Next action`: ONE grouped campaign `PLI_SRC=probes timeout 900 python3 oracle/batch.py E52TA E52TB E52TC E52TD E52TE E52TF E52TG E52TH E52TI E52TJ --tag e52p7 --switches '$L$D'` rc DIRECT, classify honestly (TJ verdict verbatim, NO fitting), then arm `open_mode_word` + the w2..w6 emitter ONLY, cmp accepted probes whole-file rc=0 vs `golden/e52p7/`, LOAN2 POSITIONAL VERBATIM (predicted blocker past 56 = `ON ERROR` line 58 — a LATER subround, do NOT fix), sweep, markers, registration, claim **C365** measured-bytes-only, COVERAGE rows, gate, close. Ledger ENDS **C364**; goldens NEVER re-derived; SE stays my-gap, SF/SG stay dr-refuses; no runtime assertions; operator `handoff.config.json` NEVER staged (dirty standing edit); renewal chain FRESH (operator archived `.pi-guard/renewal-state.json`; no state file present, 0/12 used, cap 12, autoRenew true); all rc DIRECT (the pipe-masked-rc trap fired again this hop); no push.

0a-novies-new8. **E2E-52/P3-6 hop 12 = CAP 12/12: SUBROUND CLOSED — REGISTRATION + C364 + FULL GATE rc=0 + FINAL ATTESTATION LANDED (2026-11-05, hop 12/12; this chain ENDS here).** ALL rc DIRECT, ZERO new oracle campaign, ZERO `ocaml/` byte. Chain: goldens committed VERBATIM `5ab8639` (SA 256 SB 384 SC 256 SD 256 SE 256 B + SF/SG refusal PRNs; NEVER re-derived); clean rebuild binary `0efc35e6d4ff81bd…` == hop 11, **4/4 cmp rc=0**, sweep **110/0**, codegen warnings **68 == baseline** (per-File histogram of the full clean log is the honest method — old partial ocaml/build-warn-e52p6.log NOT comparable), SE/SF/SG refuse rc=2 with [TBD]; SPECIMENS +4 + NEGATIVES SF/SG `dr-refuses` + SE `my-gap` (UNARMED, bytes claimed by NOTHING) via sanctioned `--update-inventory` diff EXACTLY +7: 1229→**1233**, 183→**186** `91592c0`; census OWN write path rc=0 counts UNCHANGED 15/0/26/0, LOAN2 blocker VERBATIM line-44→**line-54 `OPEN option PRINT … [TBD]`** (§3 prediction HIT, NOT fitted), EXPR1/EXPR2 catch-all moved `9febae8`; FULL gate REAL rc=0 `build/gate-e52p6-reg.log` (**1233/0, 186/186, 9/9, 139 rows 0/0, census 15/0/26/0, prose 5**); claim **C364** measured-bytes-only `73b9c53` committed BEFORE the COVERAGE `COND.ON_ENDFILE_ONLY` rewrite `6e6ed37` (EXACT:14→**18**, probes +SA SB SC SD, falsified clauses kept VERBATIM as HISTORICAL, id KEPT — stable key; coverage_check rc=0); RESULTS §P3-6 + PLAN §5 row + LEARNINGS hop-12 § + prose rc=0 standalone. **SUCCESSOR (fresh chain ONLY after the OPERATOR archives/resets ignored `.pi-guard/renewal-state.json` — this chain is CAPPED, NEVER `handoff_renew` past 12/12): PROPOSED, never authorization, E2E-52/P3-7 = OPEN PRINT / PAGESIZE / LINESIZE starting at LOAN2 line-54** — inspect existing `spec/lab-evidence/e2e41-p0/OPEN-MATRIX.tsv` + existing LOAN2/COPYLPT DR goldens (NO new oracle before pre-registration); distinguish `OPEN PRINT` from ordinary `STREAM OUTPUT`; investigate PAGESIZE/LINESIZE independently incl. dynamic values where measured; PROPOSED probes + PLAN §P3-7 COMMITTED BEFORE any `ocaml/` byte; preserve FILE/COMMON layout + attach laws. Standing PROPOSALS: SE `?REVOP` arm (bytes measured, my-gap KEPT); ON ERROR (LOAN2:58). Ledger ENDS **C364**; goldens NEVER re-derived; E52SE stays a measured `my-gap`, SF/SG stay DR refusals, LOAN2 still refuses at line 54, NO runtime assertions; operator `handoff.config.json` NEVER staged (dirty standing edit); all rc DIRECT; no push.

0a-novies-new7. **E2E-52/P3-6 hop 11: CAMPAIGN `e52p6` MEASURED + ARM LANDED (`8fc0a3b`) — 4/4 accepted probes byte-exact; REGISTRATION OWED at hop 12 = CAP 12/12 (2026-11-05, hop 11/12).** ONE grouped batch rc=0 5 ok/7 (`golden/e52p6/`, evidence `build/e52p6/`); **SA SB SC SD cmp rc=0 whole-file** on binary `0efc35e6d4ff81bd…`; condition byte **06** measured (C364 candidate); goto-terminated BEGIN…END handler = inline + `C3`, **NO C9**; pad `LHLD *A/SPHL/?RECOV` + entry SP-save; SC proves pad vs continuation patch targets are INDEPENDENT; SA octet-142 MISS decoded the ON-unit FALL-THROUGH HL branch-boundary law (reload, not bump) — fixed for both condition names, sweep **110/0** corroborates. **FALSIFIED:** a `BEGIN;…;end;` handler is a NAMELESS `Sproc` block with `bkind = Bbegin`, not `Sdobegin`; briefed "sweep 101" undercounted (actual 110). **SF dr-refuses** (prediction HIT) and **SG [TBD]→MEASURED dr-refuses**; **SE `revert undefinedfile(f)` DR-ACCEPTED and decoded (`06` + `?REVOP`) but KEPT UNARMED** per pre-registration §3. LOAN2 POSITIONAL ADVANCED VERBATIM past 44 → `OPEN option PRINT … (line 54)` (predicted, NOT fitted). SUCCESSOR: read `LEARNINGS.md` § "hop 11: campaign e52p6 MEASURED + ARM LANDED" + `PROGRESS.md` → `## Next action`, then hop-12 CAP contract: registration (SPECIMENS + refusals SF/SG/SE, `--update-inventory` measured delta from 1229, census OWN path FIRST, gate rc=0 `build/gate-e52p6-reg.log`, **C364 measured-bytes-only BEFORE** the COVERAGE `ON`-unit rewrite, coverage_check+prose rc=0, RESULTS §P3-6 + PLAN §5 row), durables, then **`handoff_finalize` — NEVER `handoff_renew` past the cap**. Ledger ENDS **C363**; goldens NEVER re-derived; operator `handoff.config.json` NEVER staged; all rc DIRECT; no push.

0a-novies-new6. **E2E-52/P3-6 hop 10: PRE-REGISTRATION of the ON-UNDEFINEDFILE campaign LANDED; CAMPAIGN `e52p6` OWED (2026-11-05, hop 10/12).** ZERO `ocaml/` byte, ZERO oracle call. Evidence decoded from EXISTING goldens: LOAN2.REL pins the whole line-44 class — registration `LXI H,*OUTPUT / MVI A,06 / ?ONCOP / JMP slot`, goto-terminated handler = inline chain + `C3` + **NO C9**, pad `LHLD *D(0318)/SPHL/?RECOV` at target label, main-entry `DAD SP/SHLD` save; condition byte **06 unclaimed → candidate C364**. FALSIFIED verbatim: refusal comment "no DR sample" (LOAN2 IS one); "codegen-only arm" (bind.ml `refs_stmt` charges the Sdobegin trailing goto Rk_plain → no pad/cell — must become Rk_on). P088I/P089I transcripts: bare `on undefinedfile` PASS-2 `SYNTAX ?` = dr-refuses; `(f)` form parses; both .REL have NO CODE (verdicts only). Probes E52SA..SG + PLAN §P3-6 predictions (SA 06+RET-no-pad; SB SP-save+pad+no-RET; SC independent patch targets; SD [C201] pair w/ 06; SE/SG [TBD]; SF dr-refuses; LOAN2 predicted blocker past 44 = SKIP-count 50 or `OPEN option PRINT … (line 54)`, NEVER fit) COMMITTED BEFORE any ocaml/ byte. SUCCESSOR: read `LEARNINGS.md` § "hop 10: ON-UNDEFINEDFILE EVIDENCE DECODED" + `PROGRESS.md` → `## Next action` hop-11 contract: ONE grouped campaign `PLI_SRC=probes timeout 900 python3 oracle/batch.py E52SA E52SB E52SC E52SD E52SE E52SF E52SG --tag e52p6 --switches '$L$D'` rc DIRECT, classify honestly (SF dr-refuses row from MY re-measured stderr marker; SE/SG my-gap boundaries KEPT, never fitted), arm bind.ml+codegen.ml, cmp accepted rc=0 vs `golden/e52p6/`, sweep 101, markers rc=2, LOAN2 POSITIONAL VERBATIM, commit; registration at hop 12 = **CAP 12/12**: inventory/census-own-path/gate rc=0 `build/gate-e52p6-reg.log`/**C364 measured-bytes-only BEFORE** COVERAGE/coverage_check+prose/RESULTS+PLAN rows, then `handoff_finalize` — NEVER `handoff_renew` past the cap. Ledger ENDS **C363**; goldens NEVER re-derived; operator `handoff.config.json` NEVER staged; all rc DIRECT; no push; campaign continues.

0a-novies-new5. **E2E-52/P3-5 hop 9: SUBROUND CLOSED — registration + C363 + COVERAGE 42 all
  LANDED; LOAN2 now at ON UNDEFINEDFILE (line 44) (2026-11-05, hop 9/12).** Defensive PIrep
  prescan-fold arm `a008840` (codegen histogram 70→68, EXACTLY −2 W8 at the fixed site, replay
  method honest); named REVERSE refusal `3a494c3` (`expected )` marker prediction FALSIFIED —
  panel requires [TBD]); SPECIMENS +7 + RE row, inventory 1222→1229 + 182→183 EXACTLY `4dbdaa0`;
  census own path rc=0 counts 15/0/26/0, LOAN2 blocker VERBATIM line-44 (line-177 PIvar
  prediction FALSIFIED at stage level, NEVER fitted); FULL gate REAL rc=0 1229/0, 183/183, 9/9,
  139 0/0, prose 5 `build/gate-e52p5-reg.log`; claim **C363** measured-bytes-only `c940426`
  BEFORE COVERAGE IO.PUT_EDIT EXACT 35→42 `2be56f0` (coverage_check rc=0); RESULTS §P3-5 + PLAN
  §5 row `a1a82d4`; binary `e55e892c346741b2…`, sweep 101/0. SUCCESSOR: read `LEARNINGS.md` §
  "hop 9: DEFENSIVE ARMS + REGISTRATION LANDED" and execute `PROGRESS.md` → `## Next action`:
  PROPOSED P3-6 = ON UNDEFINEDFILE (LOAN2 44) NEW ground — PLAN §P3-6 + probes collision-grepped
  and COMMITTED BEFORE any ocaml/ byte, ONE grouped campaign rc DIRECT, classify honestly.
  Ledger ENDS **C363**; goldens NEVER re-derived; operator `handoff.config.json` NEVER staged;
  all rc DIRECT; no push; campaign continues.

0a-novies-new4. **E2E-52/P3-5 hop 8: ARM LANDED — the `Pi_rep`/`PIrep` DATA-item repetition is
  BYTE-EXACT on all 7 accepted e52p5 probes (commit `aeda739`; 2026-11-05, hop 8/12).** Build rc=0
  DIRECT, binary `a55ef4eb7c7e51fb…`; **cmp RA RB RD RF RH RI RJ whole-file rc=0 vs
  `golden/e52p5/`**; RB decoded the patch law (non-final rep JP → NEXT item start; final → the
  close `?QIOOP`). RC BY / RG char-var / RE REVERSE refuse rc=2 BY NAME (boundaries KEPT).
  SUCCESSOR: read `LEARNINGS.md` § "E2E-52/P3-5 hop 8: ARM LANDED" and execute `PROGRESS.md` →
  `## Next action`: (1) defensive `| PIrep _ -> a` prescan-fold arm (PA-class Warning 8) + rebuild
  + re-verify 7 cmps + warning histogram vs 70; (2) sweep 89, markers rc=2, LOAN2 POSITIONAL
  VERBATIM (predicted line-177 `PIvar yp`, NEVER fit); (3) registration +7 SPECIMENS + RE row,
  `--update-inventory` 1222→1229 / negatives 182→183, census OWN path FIRST, gate rc=0
  `build/gate-e52p5-reg.log`, **C363 measured-bytes-only BEFORE** COVERAGE `IO.PUT_EDIT`
  EXACT 35→42, coverage_check+prose rc=0, RESULTS §P3-5 + PLAN §5 row, durables, renew 9/12.
  Ledger ENDS C362; goldens NEVER re-derived; operator `handoff.config.json` NEVER staged; all rc
  DIRECT; no push; campaign continues.

0a-novies-new3. **E2E-52/P3-5 hop 7: ARM SITES ALL VERIFIED by code reading; ARM OWED
  (2026-11-05, hop 7/12).** ZERO `ocaml/` byte. Baseline re-held: build rc=0 DIRECT binary
  `345644822818326f…`; RA/RB/RF reldumps re-read — the rep loop is `lower_doto`'s TO-arm shape
  with a ONE-item body, unconditional `LXI H,from/SHLD i` init, RB proves JP patched by
  `emit_triple` to the NEXT item (one `?QIOOP` after the LAST item). Every edit site and the
  FIVE non-exhaustive pitem matches (the PA trap: parser `parse_rep_spec`; codegen `pitem`,
  `match_put_edit` data-walker, prescan folds ~3558/~3570, both authorizers, item loop ~12176
  via named `emit_item`) + the hop-8 execution contract are in `LEARNINGS.md` § "E2E-52/P3-5
  hop 7: ARM SITES ALL VERIFIED" and `PROGRESS.md` → `## Next action`. Execute: arm → build rc=0
  DIRECT (never a pipeline) → warnings histogram vs 70 → cmp RA RB RD RF RH RI RJ rc=0 vs
  `golden/e52p5/` → RC/RG/RE rc=2 → sweep 89 → markers rc=2 → LOAN2 POSITIONAL VERBATIM
  (predicted line-177 `PIvar yp`, NEVER fit) → commit → registration (SPECIMENS +7, inventory
  1222→1229, negatives 182→183 with MY re-measured `expected )` marker, census OWN path FIRST,
  gate rc=0 `build/gate-e52p5-reg.log`, **C363 measured-bytes-only BEFORE** COVERAGE
  `IO.PUT_EDIT` EXACT 35→42, coverage_check+prose rc=0, RESULTS §P3-5 + PLAN §5 row, durables,
  renew 8/12). Ledger ENDS C362; goldens NEVER re-derived; operator `handoff.config.json` NEVER
  staged; all rc DIRECT; no push; campaign continues.

0a-novies-new2. **E2E-52/P3-5 campaign e52p5 MEASURED + DECODED; ARM OWED (2026-11-05, hop
  6/12).** ZERO `ocaml/` byte this hop. Campaign rc=0 DIRECT **9 ok/10**; **E52RE dr-refuses**
  (`SYNTAX ?`, no .REL); goldens `676fb9d`; every law decoded in `LEARNINGS.md` § "P3-5 CAMPAIGN
  e52p5 MEASURED": RA/RD == PLAN §2 loop (H1 CONFIRMED); RF var-bound == existing `lower_doto`
  shape byte-identical (H3); RH console == file loop (H2); RI table predicted-exact (H6); RJ
  = P3-4 numeric chain in loop; **BY ACCEPTED by DR (RC: INX H × n, test unchanged)** and
  **RG char-var accepted** — BOTH boundaries KEPT per §4a/§4e (record my-gaps, never fit).
  Execute `PROGRESS.md` → `## Next action`: arm parser.ml(`REPSPEC` child 0 = index `Eident`,
  BY parse-refusal) + codegen.ml (`PIrep`, shared `data` walker, prescan ONE-cell, authorize
  inner-admitted, §2/RF loop lowering; to<=2/from=0/var-FROM/nested refuse UNMEASURED);
  cmp **RA RB RD RF RH RI RJ rc=0**, RC/RG/RE rc=2, sweep 89, markers rc=2, LOAN2 POSITIONAL
  VERBATIM (predicted line-177 `PIvar yp`, NEVER fit); registration SPECIMENS +7, inventory
  1222→1229, refusal row 182→183, census OWN path FIRST, gate rc=0 `build/gate-e52p5-reg.log`,
  **C363 measured-bytes-only BEFORE** COVERAGE `IO.PUT_EDIT` (EXACT 35→42), coverage_check+
  prose rc=0, RESULTS §P3-5 + PLAN §5 row. Ledger ENDS C362; goldens never re-derived; operator
  config never staged; all rc DIRECT; renewals autonomous (6/12, cap 12); no push.

0a-novies-new. **E2E-52/P3-5 PRE-REGISTERED (`67e5414`, durables `b6539af`); CAMPAIGN
  `e52p5` OWED (2026-11-05, hop 5/12 consumed).** Execute `PROGRESS.md` → `## Next action`
  steps (1)-(3): ONE grouped oracle campaign (E52RA..E52RJ, tag `e52p5`, `'$L$D'`, rc
  DIRECT), arm parser.ml+codegen.ml per PLAN §P3-5 §2a/§4 (the "codegen ONLY" brief was
  FALSIFIED by code reading: `parse_rep_spec` drops the index name and BY), sweep/markers/
  LOAN2 VERBATIM (predicted next blocker line-177 `PIvar yp`, NEVER fit), registration
  (census OWN write path FIRST, gate rc=0 `build/gate-e52p5-reg.log`, **C363
  measured-bytes-only BEFORE** the COVERAGE `IO.PUT_EDIT` rewrite, coverage_check+prose
  rc=0, RESULTS §P3-5 + PLAN §5 row). The `Pi_rep` loop law is ALREADY decoded from the
  EXISTING LOAN2 golden (LEARNINGS § "P3-5 PRE-REGISTRATION LANDED"). Ledger ENDS C362;
  goldens never re-derived; operator `handoff.config.json` never staged; all rc DIRECT;
  `pli80c` POSITIONAL; renewals autonomous (6/12 cap 12); no push; campaign continues.

0a-decies. **E2E-52/P3-4 CLOSED (evidence rows LANDED `b76cd2f`); SUBROUND P3-5
  PRE-REGISTRATION OWED (2026-11-05, fresh chain hop 4/12).** Docs-only hop, ZERO `ocaml/`
  byte, ZERO oracle call: `RESULTS.md` §P3-4 (campaign 9 ok/11 table with reldump-derived
  code/DATA sizes; verdicts VERBATIM — H2a/H2b FALSIFIED + H2c CONFIRMED (count-1 SPLICE); H4a
  FALSIFIED + H4b FALSIFIED-IN-DETAIL (boundary **255**, not 19; widths 14..128 accepted,
  bytes UNMEASURED; 129..254 unmeasured); H5a/H5b MOOT + H5c CONFIRMED; H6a FALSIFIED + H6b
  CONFIRMED (no-XCHG); `Pi_rep` ≠ `Pi_repgrp` brief wording falsified; PA root cause +
  HEADLINE; LOAN2 line-212 VERBATIM, the DEC-147 prediction FALSIFIED AT STAGE LEVEL; gate
  1222/0 + 182/182, C362, COVERAGE EXACT:35; §6 NOT-say) + `PLAN.md` §5 P3-4 row.
  Independent re-verification THIS session: clean build `345644822818326f442a…`, **10/10 cmps
  rc=0** (PA headline re-held a 3rd time), PU/PV/PF rc=2 markers, LOAN2 rc=2 VERBATIM,
  prose rc=0 — `build/e52p3e/`. DECODED the NEXT blocker with no oracle run: LOAN2 212 is
  `put file(output) skip edit ('-------','------------',('---------------' do i = 1 to 4)) (a);`
  — the failing class is the **`Ast.Pi_rep` DATA-item DO-repetition in the DATA half** (parser.ml
  1018; the `data` walker admits only `Pi_data`/`Pi_fmtlist`, so `classify_item` is never
  reached). `bind.ml:1155` calls `Pi_rep` 0 format bytes with a **"[verify]"** annotation; NO
  golden holds a `Pi_rep` in a file EDIT list → its lowering is **UNMEASURED**.
  SUCCESSOR: read `LEARNINGS.md` § "E2E-52/P3-4 CLOSED … P3-5 PRE-REGISTRATION OWED" and execute
  `PROGRESS.md` → `## Next action` steps (1)-(4): **PLAN §P3-5 + probes E52RA.. COMMITTED BEFORE
  any ocaml/ byte** (collision-grep probes/+INVENTORY, verify tag `e52p5` unused), ONE grouped
  campaign, arm (codegen only), sweep+markers+LOAN2 VERBATIM, registration (census OWN write path
  FIRST, gate rc=0 `build/gate-e52p5-reg.log`, **C363 measured-bytes-only BEFORE** the COVERAGE
  rewrite, coverage_check+prose rc=0, RESULTS §P3-5 + PLAN §5 row). Ledger ENDS **C362**; other
  live refusals (NOT P3-5 targets unless measured): DEC formal/deref, numeric-literal, PIvar
  bin-var file route (LOAN2 177), counted SKIP/PAGE+EDIT, format-COUNT expression, group count 0,
  x 14..128 gap. Constraints: no push; goldens NEVER re-derived; operator `handoff.config.json`
  NEVER staged (dirty standing edit); all rc DIRECT (pipeline-masking trap fired 3 hops running);
  `pli80c` POSITIONAL; renewals autonomous (4/12 consumed, cap 12); campaign continues.

0a-novies. **E2E-52/P3-4 REGISTRATION LANDED — gate rc=0 1222/0, ledger ENDS C362;
  RESULTS/PLAN rows + P3-5 OWED (2026-11-05, fresh chain hop 3/12).** All owed registration
  steps executed DIRECT: 10 SPECIMENS + PU/PV dr-refuses rows `e397ed9`; inventory
  1212→1222 + 180→182 exactly; census own write path rc=0 counts unchanged, 3 predicted msg
  moves (LOAN2 VERBATIM line-212); FULL gate rc=0 `build/gate-e52p3d-reg.log` (1222/0, 182/182,
  9/9, 139 0/0, 15/0/26/0, prose 5); **C362** from MEASURED BYTES ONLY `1de3e28` BEFORE the
  COVERAGE `IO.PUT_EDIT` rewrite `8c3b0b4` (EXACT:25→35; falsified clauses kept VERBATIM as
  HISTORICAL); coverage_check rc=0 + prose rc=0 standalone; 10/10 cmps incl. PA headline
  re-held on binary `345644822818326f…`. SUCCESSOR: read `LEARNINGS.md` § "E2E-52/P3-4
  REGISTRATION LANDED" and execute `PROGRESS.md` → `## Next action`: RESULTS §P3-4 + PLAN §5
  row, then subround P3-5 (PLAN BEFORE any ocaml/ byte). Ledger ENDS **C362**; goldens never
  re-derived; operator handoff.config.json never staged; all rc DIRECT; no push; campaign
  continues.

0a-octies. **E2E-52/P3-4 PA FIXED — HEADLINE MET; REGISTRATION OWED (2026-11-05, fresh
  chain hop 2/12).** Root cause of the PA crash: unparenthesised trailing inner match in
  `edit_num_cell` swallowed the outer `| _ -> false` (non-exhaustive outer match; `-warn-error
  -a` = warnings never fatal) — proven via `-dlambda`; stale-map and PIlit suspects FALSIFIED.
  Fix `9b2d781` (codegen.ml only); binary `345644822818326f442a…`: **E52PA cmp rc=0 vs EXISTING
  golden/e52p3/E52PA (sha `d7b4e7f3…`) = HEADLINE MET**; 9/9 cmps re-verified; sweep 89/89;
  markers rc=2 intact; warnings 70 == baseline. LOAN2 ADVANCED VERBATIM to line-212 matcher-split
  (DEC-147 prediction falsified; NOT fixed). Owed = registration steps (1)-(5) in `LEARNINGS.md`
  § "PA FIX + SWEEP 89/89 + MARKERS + LOAN2 ADVANCED LANDED": SPECIMENS 10 + PU/PV dr-refuses
  rows, --update-inventory 1212→1222, FULL gate rc=0 `build/gate-e52p3d-reg.log`, census own write
  path, **C362 measured-bytes-only BEFORE** COVERAGE `IO.PUT_EDIT` (EXACT:25→35), coverage_check +
  prose rc=0, RESULTS+PLAN rows. Ledger ENDS C361; goldens never re-derived; operator
  handoff.config.json never staged; all rc DIRECT; no push; campaign continues.

0a-septies. **E2E-52/P3-4 CAMPAIGN MEASURED + ARM LANDED; PA BLOCKER OWED (2026-11-05,
fresh chain hop 1/12).** Campaign e52p3d rc=0 9 ok/11 (PU bare-x and PV x(255) are
dr-refuses, no .REL); arm (codegen.ml, fmt_spec let rec repgrp `80 n…81`/count-1-FLATTENS
+ X(w)→`0B w` ≤128 + file PInum shape-authority admission) gives **9/9 accepted-probe
whole-file cmp rc=0** on binary `898b191c…`; **PA crashes: Match_failure codegen.ml:11906
(edit_num_cell, exhaustive — debug suspect stale line map / PIlit interaction); PA cmp vs
EXISTING golden/e52p3/E52PA is the HEADLINE, unmet.** Full state and owed steps (1)-(4)
( fix PA → sweep+markers → LOAN2 VERBATIM → registration + C362 measured-bytes-only BEFORE
COVERAGE rewrite, gate rc=0 build/gate-e52p3d-reg.log) in `PROGRESS.md` → `## Next action`
and `LEARNINGS.md` § "P3-4 campaign e52p3d MEASURED + arm LANDED". Ledger ENDS C361;
goldens never re-derived; operator handoff.config.json never staged; all rc DIRECT;
no push; campaign continues.

0a-sexties. **E2E-52/P3-4 PRE-REGISTERED, CAMPAIGN OWED (2026-11-05, fresh chain;
  operator reset renewal state; pre-reg `3ac7f41`, g310 block `6d83a36`).** Execute
  `PROGRESS.md` → `## Next action` steps (1)-(6): baseline build+PA re-measure; ONE
  grouped campaign `PLI_SRC=probes timeout 900 python3 oracle/batch.py E52PP..E52PZ
  --tag e52p3d --switches '$L$D'`; classify H2/H4/H5/H6 verdicts, keep MISSes;
  arm PLAN §P3-4 §4 (codegen ONLY: fmt_spec Pi_repgrp `80 n…81` recursive — the
  parser node is Pi_repgrp NOT the brief's Pi_rep — X `0B w`, file-route fixed-bin
  arithmetic BY MEASURED OPS); cmp PP..PZ + **PA vs EXISTING golden = headline
  (byte-exact)**; sweep + LOAN2 VERBATIM (expect DEC-FORMAL blocker at 147); register
  (SPECIMENS/--update-inventory/gate rc=0 build/gate-e52p3d-reg.log/census own path/
  C362 measured-bytes-only BEFORE COVERAGE rewrite/prose+coverage_check rc=0/RESULTS
  +PLAN §5/durables). Ledger ENDS C361. Constraints unchanged: no push; goldens never
  re-derived; operator handoff.config.json never staged; all rc DIRECT; pli80c
  POSITIONAL; renewals autonomous (fresh chain, cap 12); campaign continues.

0a-quinquies. **P3-3 FULLY CLOSED; RENEWAL CAP 12/12 REACHED — THIS IS THE FINAL HOP OF
  CHAIN 01a1a795 (2026-11-05, successor of g307, renewal 12/12 consumed).** Registration
  landed in full: `7294d09` (13 SPECIMENS E52PB..PE,PG..PL,PM,PN,PO + E52PF dr-refuses
  REJECTS/NEG_META row, marker re-measured rc=2; sanctioned --update-inventory 1199->1212
  EXACTLY +13+1; FULL gate REAL rc=0 DIRECT build/gate-e52p3c-reg.log 1212/0, 180/180, 9/9,
  139/0/0, 15/0/26/0, prose 5) -> `a4eddd6` (census own write path rc=0, metadata-only, LOAN2
  blocker VERBATIM UNCHANGED) -> `64e464b` (claim **C361** from MEASURED BYTES ONLY, BEFORE
  the COVERAGE rewrite; ledger ENDS **C361**) -> `4f5d509` (IO.PUT_EDIT EXACT:25, falsified
  clauses verbatim as HISTORICAL, coverage_check rc=0 139/0/0, stats not drifted) ->
  `794cfb2` (RESULTS §5 + PLAN §5 P3-3 row; prose rc=0 twice). SUCCESSOR (only after the
  OPERATOR archives/resets the ignored .pi-guard renewal-state.json or raises the cap): read
  LEARNINGS.md § "E2E-52/P3-3 REGISTRATION LANDED — SUBROUND CLOSED at the 12/12 renewal cap"
  and execute PROGRESS.md -> ## Next action = subround **P3-4** (rep-groups 80 n…81, x(w) 0B,
  file-route EXPRESSION item; PA bytes pinned LOAN2 0544-0558): PLAN+probes COMMITTED BEFORE
  any ocaml/ byte, one grouped campaign tag e52p3d (verify unused), arm+sweep+LOAN2 verbatim,
  registration + claim C362 measured-bytes-only BEFORE the COVERAGE rewrite. Constraints
  unchanged: no push; goldens never re-derived; operator handoff.config.json never staged;
  all rc DIRECT; pli80c POSITIONAL; campaign continues. THIS session closes via
  handoff_finalize — NEVER handoff_renew past the cap.

0a-qua. **P3-3 LANDED THROUGH ARM; REGISTRATION OWED (2026-11-05, successor of g305, renewal
  11/12 consumed, cap 12).** Chain `eef371b` (PLAN §P3-3 + probes E52PA..E52PO committed BEFORE
  any ocaml/ byte) → `8edea80` (ONE grouped campaign tag e52p3 rc=0, **14 ok/15**; E52PF
  `p'9$9'` MEASURED **dr-refuses** `PICTURE ?`, NO .REL; scale-mismatch expectation FALSIFIED —
  PJ/PK/PL accepted) → `aae0f37` (goldens) → `d088cdb` (arm: ONE `Ast.Pi_pic` branch in
  `fmt_spec`, `02 b1 b2 len UPPER(text)`; b1 = count{9,Z,$}−1-if-$; **b2 = count{9,Z} after the
  LAST V** — rule HE, HC and HD both FALSIFIED by E52PJ `9.9`→00; guards refuse BY NAME: outside
  {9,Z,$,V,.,B,comma,slash}, $-after-digit, V-without-dot; binary `c2c6282f5662cb19a3ce…` clean
  rebuild; **13/13 accepted probes whole-file cmp rc=0** — P5's 4-probe subset an UNDERCLAIM,
  falsified; PA/PF refuse by name; LOAN2 VERBATIM same fmt_spec catch (P6 HIT); sweep 75/75;
  P086J/K rc=0; markers intact; codegen warnings 70 = baseline — per-File histogram is the honest
  method, full-log totals FALSIFIED as comparison). Ledger ENDS C360; E52PF bytes claimed by
  NOTHING. SUCCESSOR: read `LEARNINGS.md` § "E2E-52/P3-3 LANDED through ARM" and execute
  `PROGRESS.md` → `## Next action` steps (1)-(6): SPECIMENS 13 (+PROPOSED PF REJECTS row),
  `--update-inventory` 1199→1212 (+1 if PF), FULL gate rc=0 `build/gate-e52p3c-reg.log`, census
  own write path, claim **C361** from MEASURED bytes ONLY committed BEFORE the COVERAGE
  `IO.PUT_EDIT` rewrite, coverage_check + prose rc=0, RESULTS §5/PLAN §5 rows, durables. THIS
  CHAIN HAS ONE RENEWAL LEFT (12/12 = cap): the successor must plan its close early and use
  `handoff_finalize` at the cap. Constraints: no push; goldens never re-derived; operator
  `handoff.config.json` never staged; all rc DIRECT; pli80c POSITIONAL; campaign continues.

0a-ter-4. **P3-2 FULLY LANDED; P3-3 (PICTURE `02` DECODE) OWED (2026-11-05, successor of g301,
  renewal 9/12 consumed).** Registration debt CLOSED at HEAD `0d93acc`: claim **C360** `19ce1f4`
  (MEASURED bytes only — reldump re-verified this session: `?DSTOP@005D`, `?STOPX@0063`,
  DEF-CODE-SIZE `0065`=101, P086J table `80 00 00 09 02 03 04 81`; ledger ENDS C360; E41X8 bytes
  never claimed); COVERAGE `IO.PUT_EDIT` `9e897e8` SUPPORTED + EXACT:12 + MEASURED, falsified
  IFACT/LOAN1 clause kept verbatim as HISTORICAL, coverage_check rc=0 DIRECT 139/0/0
  (`build/coverage-check-e52p3c-coverage.log`), stats own write path; RESULTS §P3-2 + PLAN §5
  P3-2 row `0d93acc`; prose rc=0 standalone twice. P086K/P086J cmp rc=0 RE-MEASURED on binary
  `748c434fafd8c01579b1…` (== predecessor clean-rebuild hash). LESSONS: claim commit must
  PRECEDE the COVERAGE commit (validator resolves cites); never total the ledger via
  `grep -c '^## C'` (file starts mid-index). SUCCESSOR: read `LEARNINGS.md` § "E2E-52/P3-2
  COVERAGE + C360 + RESULTS/PLAN LANDED" and execute `PROGRESS.md` → `## Next action` = subround
  **P3-3 = picture `02` decode**: PLAN §P3-3 COMMITTED BEFORE any ocaml/ byte; one-operand
  oracle probes (`p'9'`, `p'999'`, `p'ZZ9'`, `p'9V9'`, two pictures, picture + `a(w)`); arm +
  sweep + LOAN2 verbatim; C361 from measured bytes only. If a guard-block refresh lands
  uncommitted, commit it VERBATIM first. Constraints: no push; existing goldens never re-derived
  (NEW probes may add goldens); operator `handoff.config.json` never staged; all rc DIRECT;
  renewals autonomous at safe boundaries (9/12 consumed, cap 12); campaign continues.

0a-ter-3. **P3-2 REGISTERED; COVERAGE/C360 OWED (2026-11-05, successor of g298, renewal 9/12
  consumed).** E41X8 retired MEASURED rc=0 (no golden, bytes never claimed; negatives 179);
  SPECIMENS P086K+P086J registered; INVENTORY 1197→1199 EXACTLY TWO lines; census own write path
  rc=0 with LOAN2's moved blocker recorded VERBATIM; FULL gate REAL rc=0 1199/0
  (`build/gate-e52p3b-reg.log`). FALSIFIED: the `IO.PUT_EDIT` row's "picture measured on
  IFACT/LOAN1" clause — LOAN1 has NO edit stmt, IFACT's has no picture. SUCCESSOR: read
  `LEARNINGS.md` § "E2E-52/P3-2 registration LANDED" and execute `PROGRESS.md` → `## Next action`
  steps (1)-(6): COVERAGE rewrite + coverage_check rc=0, C360 from MEASURED bytes only, prose,
  RESULTS+PLAN §5, durables, then P3-3 (picture `02` decode, PLAN BEFORE bytes). HEAD `60ed349`;
  commit pending guard block first.

0a-ter-2. **P086K FIXED — RECORD ORDER, NOT BYTES (2026-11-04, successor of g294, renewal 7/12
  consumed).** The reldump diff proved every CODE and DATA byte of P086K already agreed with the
  golden (the predecessor's "+3 code bytes" reading FALSIFIED: `0x62`=98 is the last code record's
  ADDRESS, DEF-CODE-SIZE is `0065`=101 in both); the difference was that DR emits the prealloc'd
  FORMAT TABLES before the FILE COMMON group and the lowering-allocated pool after it. Arm fixed,
  `dune build` rc=0, P086K cmp **rc=0** (512 B), P086J **rc=0** (256 B), sweep **75/75 byte-exact**,
  boundary markers intact, warning histogram identical, LOAN2 advanced VERBATIM to the fmt_spec
  catch. SUCCESSOR: read `LEARNINGS.md` § "E2E-52/P3-2 P086K FIXED" and execute `PROGRESS.md` →
  `## Next action` step (2) (E41X8 retirement — it compiles rc=0 now, no golden, never claim its
  bytes; negatives 180→179) THEN step (3) registration. HEAD `2686bcc` (fix + durables); commit the
  pending guard block verbatim first.

0a-ter. **P3-2 ARM IMPLEMENTED, P086K DEBUG OWED (2026-11-04, successor of g291, renewal
 6/12 consumed).** Arm (a)-(g) landed in `ocaml/lib/codegen.ml` ONLY, UNCOMMITTED; build
 rc=0 binary `a353f6fc7a48d185…`, warning profile IDENTICAL. P086J cmp **rc=0 FIRST TRY**
 (256 B); P086K cmp **rc=1 at octet 32** (512 B, code=101 vs 98 — divergence in the
 DEF-COMMON/SEL-COMMON records; suspect spurious second SEL-COMMON on the GET). SUCCESSOR:
 read `LEARNINGS.md` § "E2E-52/P3-2 ARM IMPLEMENTED" (full record + owed steps (1)-(7)),
 execute `PROGRESS.md` → `## Next action`; first action = reldump-diff P086K, fix, cmp AGAIN.

0a-bis. **P3-2 ARM CONTRACT READY (2026-11-04, successor of g290, renewal 5/12 consumed at
 this hop).** Zero `ocaml/` byte written; the arm is now specified to the instruction level in
 `LEARNINGS.md` § "E2E-52/P3-2 arm DESIGN VERIFIED against the code" (exact golden byte lists
 re-read from `build/e52p3/p086{j,k}-reldump.txt`, the parser's flat GET-EDIT item list, the
 seven codegen-only edits (a)-(g), the two panel rows E41X8/E46K15 verified, and the predicted
 LOAN2 message shape). SUCCESSOR: execute `PROGRESS.md` → `## Next action` steps (1)-(5); read
 that LEARNINGS § then PLAN §P3-2 §3/§4/§5.

0a. **P3-2 STATUS THIS SESSION (2026-11-04, successor of g287):** evidence steps (1)-(2) DONE,
**PLAN §P3-2 COMMITTED BEFORE any ocaml/ byte**; ZERO compiler edits. New witness P086J.REL
(console DEC edit) FALSIFIES both "no DR sample passes a DEC item through an edit list" refusals;
a(w)=`03 w`/a=`03 FF`/f(w,d)=`00 w d`/x=`0B w`/picture=`02 A B len`/rep=`80 n…81` decoded.
SUCCESSOR: execute `PROGRESS.md` → `## Next action` → "PLAN §P3-2 LANDED; ARM A1-A5 OWED"
steps (1)-(5) exactly; read that LEARNINGS § + PLAN §P3-2 first. Renewal 5/12 after this.

0. **E2E-52/P3 CAMPAIGN IN FLIGHT (2026-11-04; renewals autonomous; do NOT stop after
 one blocker).** **P3-1 CLOSED + REGISTERED** (chain `8dbebff` guard block, `e728175`
 INVENTORY 1196->1197 ONE-line diff + post-reg FULL gate REAL **rc=0 1197/0**
 `build/gate-e52p3-reg.log` — negatives MEASURED **180/180**, the brief's 181/181
 FALSIFIED by the retire; claim **C359** `c410d18` ledger ENDS C359/182; COVERAGE
 FILE.PUT_PAGE SUPPORTED+EXACT:1 rc=0 `d3b8859`; RESULTS+PLAN §5 `3e74d83`; prose rc=0;
 tree clean except operator config). E46N10 is a panel-EXACT specimen (384 B).
 **SUCCESSOR: subround P3-2 = PUT EDIT (LOAN2:115 verbatim `codegen: PUT EDIT deferred
 [TBD] (line 115; ... ?EDITF/?EDTOV/?QDDSL route family)`).** READ FIRST `LEARNINGS.md`
 § "E2E-52/P3-2 evidence decode LANDED" (commit `59f9afa`) — it SUPERSEDES the survey
 bullets below: LAW REVERSAL (`edit(L1)(L2)` = DATA then FORMAT; 115 DATA is `'|'` +
 `100*m+y`, FORMATS are `a` + picture `p'99/99'`; predecessor data-item bullet FALSIFIED);
 `clear` = `%replace` macro; P086K fully decoded (file tables = console law; DEC prep
 `MVI A,05/?DLDOP/MVI A,08/MVI B,02/?QDCOP/?EDTOV` = existing p/p+3/s law — `MVI B,06`
 FALSIFIED; `?EDTIV` one new routine; NO-open attach C282); barrier =
 `lower_put_items_gen` `is_edit && file` guard (premise FALSIFIED) + `match_put_edit`
 file-blindness + fmtq FIFO + `st.file_out` guard. Execute that § owed steps (1)-(5): byte-
 list stmt-199 span 08F1-0950 + tables, check golden/e2e8/e2e11, **PLAN §P3-2 committed
 BEFORE any ocaml/ byte**, then arm (PROPOSED P3-2a: file PUT+GET EDIT bare skip + literal
 f/a + string/DEC items; picture-02/x/rep/V refuse BY NAME; specimen probes/P086K.PLI vs
 golden/probe55/P086K 1197→1198; E41X8 retirement; LOAN2 STILL refuses 115 naming the
 `02` record), sweep/refusals/registration/C360 measured-bytes-only. Prior section, kept
 as written:
 § "E2E-52/P3-1 REGISTRATION LANDED; P3-2 (PUT EDIT) evidence survey IN FLIGHT" — it
 carries the refusal site (codegen.ml:2646 in match_put_list_lit), the console EDIT
 state ([C090]; fmt_spec admits ONLY literal-width f/a + bare skip/page), and the
 ALREADY-MEASURED DR file-EDIT witnesses: `golden/probe55/P086K/P086K.REL` re-dumped
 this session (attach 0652/?SIOOP, table `80 00 00 05 01 81` at *S(0000), ?EDITF,
 ?DLDOP/?QDCOP/?EDTOV/?QIOOP, no OPEN needed, pool law holds) and `golden/first/LOAN2/
 LOAN2.REL` span 0522-055C (skip=MVI A,01/?SKPOP; 100*m+y=LHLD/LXI D,0064/?IM22N/XCHG/
 LHLD/DAD/MVI A,09/?QICOP/?EDTOV; full reldump in ignored `build/e52p3/`). E41X8
 negative pins the P086K shape (retirement candidate). Execute the § owed steps (1)-(7):
 finish evidence (decls of `a`/`clear`; decode ALL LOAN2 tables + spans 068A,0796,0830,
 086E,08F1,0951; string-in-format/V/picture/rep encodings), PROPOSED first arm = file
 EDIT bare-skip + literal f/w formats (P086K bytes fully pinned; later subrounds own
 string/V/picture), **PLAN §P3-2 committed BEFORE any ocaml/ byte**, then arm/sweep/
 refusals/LOAN2-rerun-verbatim/register/C360 from measured bytes only. Constraints:
 no push; goldens never re-derived; operator handoff.config.json never staged; all rc
 DIRECT; never hardcode LOAN2; renew at safe boundaries (3/12 used); [C359] does NOT
 license counted PAGE/PAGE+items/console PAGE/non-leading (all still refuse BY NAME).
 SUPERSEDED-BY-ABOVE (kept as written):
 renewals autonomous at safe boundaries; do NOT stop after PAGE).** P3-1 **ARM LANDED
 `adb749c`** (codegen.ml only; B1-B7 executed; binary `34e8321a…`; warning profile IDENTICAL
to baseline). MEASURED: E46N10 whole-file cmp rc=0 FIRST TRY (384 B, sha `75557545…` ==
golden; ?PAGOP@0030 no count, continuation 0035 — exactly PLAN §2); E46N sweep 18/18;
ALL boundaries still refuse (counted PAGE, PAGE+items BY NAME, console PAGE/N3_PAGE, E46N21
marker intact; non-leading PAGE refuses at the PARSER — stage falsified, boundary kept).
**LOAN2 ADVANCED past 99: ACTUAL verbatim `codegen: PUT EDIT deferred [TBD] (line 115; only
PUT LIST is implemented; format/picture editing needs the ?EDITF/?EDTOV/?QDDSL route family)`
rc=2** — OPEN PRINT 54/56 stays queued BEHIND it (prescan order; the specific OPEN-PRINT
expectation was FALSIFIED by stage, direction prediction held). Census re-snapshotted via its
own write path rc=0, counts UNCHANGED 15/0/26/0. UNCOMMITTED IN TREE: `tools/e2e_gate.py`
(E46N10 retired from REJECTS+NEG_META as written history, added to SPECIMENS) and
`spec/census/*` — commit explicit paths FIRST. **SUCCESSOR: execute `LEARNINGS.md` § "P3-1
ARM LANDED + registration IN FLIGHT" owed steps (1)-(7) EXACTLY** (--update-inventory
1196→1197 diff ONE line; reg gate rc=0 1197/0 to build/gate-e52p3-reg.log; COVERAGE
FILE.PUT_PAGE→SUPPORTED/EXACT:1 + coverage_check rc=0; claim C359 from MEASURED bytes only;
RESULTS.md + PLAN §5 table row; commits) then CONTINUE: subround **P3-2 = PUT EDIT
(LOAN2:115)** — start `spec/lab-evidence/e2e52-p3/PLAN.md` §P3-2 (extract LOAN2:115 verbatim,
read `match_put_edit` + E2E-8 `put_kind_str` refusal, search golden/e2e11 evidence) BEFORE
any compiler byte. Prereg-gate rc=0 expectation itself FALSIFIED/measured (gate at arm =
rc=1, `build/gate-e52p3-prereg.log`). Constraints: no push; goldens never re-derived;
operator handoff.config.json never staged; all rc DIRECT; never hardcode LOAN2; renew at
safe boundaries; item 1 below kept as written but SUPERSEDED by this brief.
1. **(Was item 0; kept as written)** **E2E-52/P2 CLOSED (2026-11-04; operator brief: DEC formal copy-in, E52G
byte-exact closure; hop 2 registration session; chain `a365686` plan / `d67a263` arm /
`c34c690`+`546c70a` hop-1 durables / `01bf2df` renewal / `dca9219` registration /
`90582a5` COVERAGE / `755bf1c` RESULTS + this close prose).** **E52G is REGISTERED and
panel-EXACT**: sanctioned `--update-inventory` 1195→**1196** (diff exactly ONE line),
post-registration FULL gate REAL **rc=0** DIRECT `build/gate-e52p2-reg.log` (**1196
byte-exact / 0 of 1196**, `BYTE-EXACT E52G`, 181/181, 9/9, 139 rows 0/0, census
15/0/26/0, prose 5); COVERAGE row `PROC.DEC_FORMAL_COPYIN_CELLMAP` `mine_status=
SUPPORTED` (the validator's byte-exact value; `EXACT` exists ONLY in `rel_parity` — P1
vocabulary lesson applied to the brief's "->EXACT" wording) + `rel_parity=EXACT:1`,
probes cite panel key E52G AND keep the golden path, cites unchanged [C358] [C131]
[C187], NO new rows, coverage_check rc=0 **139 rows 0/0** + stats via its own write
path; LOAN2 rerun UNMODIFIED — blocker UNCHANGED verbatim (`codegen: PUT FILE with a
bare PAGE control item [TBD] (line 99)`), NOTHING advanced or fixed, never claimed
exact; E52A..J 10/10 + E51A..L 12/12 re-measured byte-exact on binary `85bf7a26…`.
NO new claim (C358 states the law; the optional C358 NOTE was declined — default); the
ledger ENDS **C358**. Evidence `spec/lab-evidence/e2e52-p2/{PLAN.md,RESULTS.md}`.
**SUCCESSOR: NO active round and NO pending instruction.** Confirm HEAD/tree (only the
operator's `handoff.config.json` edit may be dirty), `/handoff verify`, record state
and **STOP** — await an operator brief. Standing PROPOSALS (shortlist, NEVER
authorizations): dashboard `**26**` refresh + mapping P1's three unmapped DIV rows
(`EXPR.DIV_VAR_PARK`, `EXPR.DIV_RESULT_ADD`, `COND.DIV_EQ_TEST`); FCPS1..3 SPECIMENS
registration at a gate hop; README § 5.1 rights review for the eight corpus sources
(due); E2E-50/P3 shortlist (`spec/lab-evidence/e2e50-p2/REPORT.md` § 5);
fc01-fileio/ONUNIT-00 stay CANCELLED; the P1-era "E52G joins `spec/DIVERGENT.txt`"
proposal is OBSOLETE — G is byte-exact and registered. Constraints unchanged: no push;
goldens never re-derived; NEVER re-run the retry-DFS; no expansion to other LOAN2
blockers (PAGE/PUT FILE/ON-unit/EDIT stay untouched); operator `handoff.config.json`
never staged; all rc captured DIRECTLY.
SUPERSEDED-BY-ABOVE (kept as written; the hop-2 contract named below was EXECUTED in
full): 0. **E2E-52/P2 IN FLIGHT (2026-11-04; operator brief: DEC formal copy-in, E52G
byte-exact closure).** Hop 1 LANDED: plan pre-committed `a365686`; arm `d67a263`
(Bind `cs_copies` owns the caller-side formal-precision copy-in temp; codegen emits the
[C358] `?DLDOP/@actual + ?DSTOP/@temp` pair before the descriptor-word record and
retargets the block word to the temp; every other DEC mismatch shape refuses BY NAME);
durable record `c34c690`. MEASURED: E52G whole-file `cmp` rc=0 FIRST TRY (sha
`39b3d7cf…` == golden `golden/e52p1/E52G/E52G.REL`, exactly the PLAN §4 prediction, never
fitted); E52A..J 10/10 EXACT; E51A..L 12/12 EXACT; pre-registration FULL gate REAL rc=0
DIRECT `build/gate-e52p2-prereg.log` (1195/0 of 1195, 181/181, 9/9, 139 rows 0/0, census
15/0/26/0, prose 5). Binary `85bf7a26…`. **The successor executes `PROGRESS.md` -> `##
Next action` -> "E2E-52/P2 hop 2 OWED" steps (a)-(e) exactly: register E52G
(SPECIMENS + --update-inventory 1195->1196 + gate AGAIN, expect 1196), COVERAGE row
`PROC.DEC_FORMAL_COPYIN_CELLMAP` -> EXACT:1 (no new rows), LOAN2 UNMODIFIED blocker
record (fix NOTHING), RESULTS.md + close prose, STOP after P2.** Constraints unchanged:
no push; goldens never re-derived; NEVER re-run the retry-DFS; operator
`handoff.config.json` never staged; all rc DIRECT (a `dune build | tail` pipeline masked
rc=1 TWICE this hop -- the rule is real); no PAGE/PUT FILE/ON-unit/EDIT work; no new
claims (C358 states the law; ledger ENDS **C358**); dashboard `**26**` staleness
recorded, never fixed.

1. Confirm the repository and revision:
   `cd /home/john/projects/sushiworks/pli80 && git rev-parse --abbrev-ref HEAD && git rev-parse HEAD && git status --porcelain=v1`
   A dirty `handoff.config.json` is the OPERATOR's standing edit — investigate, never clean,
   never stage, never commit, never revert it. `AGENTS.md` → Protected.
2. Lean recovery: Pi auto-loads `AGENTS.md`; read this file and `PROGRESS.md` NOW.
   `PROTOCOL.md` governs all scientific procedure and is consulted before any unclear
   scientific/policy action; `GOAL.md` and `LEARNINGS.md` remain authoritative and are read
   selectively by pointer. A deferred read never weakens the protocol.
3. Check checkpoint freshness with `/handoff verify`. `stale` or `missing` means: re-derive
   state from commits and lab evidence, then refresh and attest with `/handoff finalize`.
   Do not trust this file's managed block over its prose.
4. Load evidence SELECTIVELY — the ledgers are far larger than the working window; a
   complete read of any of them is prohibited for recovery:
   - `spec/CLAIMS.md`: read ONLY cited claim ids — `grep -n '^## C352' spec/CLAIMS.md` etc.;
     the E2E-49/P4 block starts at `grep -n '^## C348'`; the E2E-48 family is C309..C332,
     E2E-49/P1 is C333..C336, E2E-49/P2 is C337..C341, E2E-49/P3 is C342..C347, E2E-49/P4 is
     C348..C351; E2E-51/P1 is C353..C355; E2E-52/P1 is C356..C358. The ledger CURRENTLY
     ENDS at **C358** (E2E-52/P1 DEC-pool claims, commit `7176ff8`) — no claim ids are
     owed; [C352] remains the RUNTIME console-framing law cited by every
     functional expectation containing blank lines. The E2E-49/P4 block starts at
     `grep -n '^## C348'`. [C330] carries
     the labelled E2E-49/P1 CORRECTION append (positional length law); [C335]–[C338] carry
     labelled P3 CORRECTION appends and [C346] a labelled CITATION CORRECTION (the numeric
     ORDER law is [C104], never cite legacy [C027]/[C072] in provenance); [C335]/[C337]/
     [C344]/[C346] additionally carry labelled [E2E-49/P4 CORRECTION(S)] blocks (`9c42f3b`)
     and [C348] a labelled [E2E-49/P4 WORDING CORRECTION] (`5b0ccde`); falsified text is kept
     as written (PROTOCOL #2).
   - `spec/COVERAGE.tsv`: header + `grep` the row KEY being edited (15 columns; schema
     `spec/COVERAGE-SCHEMA.md`; validator rules at `tools/coverage_check.py:203-247`).
   - `spec/INVENTORY.txt`: `grep` the specimen/refusal name only. `spec/RUNTIME.txt` and
     `spec/DIVERGENT.txt`: only rows named by the task.
   - Latest round evidence: `spec/lab-evidence/e2e52-p2/{PLAN.md,RESULTS.md}` (round
     CLOSED); prior rounds under `spec/lab-evidence/e2e52-p1/` (RESULTS/HYPOTHESES/
     BASELINE-MINE/PLAN/mkprobes), `spec/lab-evidence/e2e48-*/`,
     `spec/lab-evidence/e2e49-p{1,2,3,4}/` and `spec/lab-evidence/e2e51-p1/`.
5. Do **not** run the compiler, the oracle, LINK-80, cpmsim, Rune CI or `tools/e2e_gate.py`
   unless the session's actual task is compiler development or gate verification.
6. **E2E-52/P2 CLOSED (2026-11-04; operator brief: DEC formal copy-in, E52G
byte-exact closure; hop 2 registration session; ledger ENDS **C358**, NO new claim).**
FULL CHAIN: PLAN pre-committed `a365686` (predictions derived from [C358] + the golden
reldump BEFORE any compiler byte); ARM `d67a263` — Bind `cs_copies` is the single
layout authority for the caller-side copy-in temp (allocated in section2's phase-2
pass, size `bytes_of (RTdec(pf,sf))`, [R507] authority; trigger: internal
non-recursive callee, caller-own-row bare `Eident`, `RTdec` vs `RTdec` with `sa=sf &&
pa<pf`); codegen consumes the offset, emits the [C358] `?DLDOP/@actual +
?DSTOP/@temp` pair BEFORE the descriptor-word record and retargets the block word to
the temp; DECPOLY equal-precision route UNCHANGED; every other DEC mismatch shape
refuses BY NAME. MEASURED: E52G whole-file `cmp` rc=0 FIRST TRY (mine sha `39b3d7cf…`
== golden; code `004A`, DATA `0014`, exactly PLAN §4, never fitted — **ZERO MISS this
round**); E52A..J 10/10 and E51A..L 12/12 (re-measured hop 2 on `85bf7a26…`); pre-reg
gate rc=0 DIRECT 1195/0 `build/gate-e52p2-prereg.log`; hop 2: SPECIMENS registration +
`--update-inventory` 1195→1196 (exactly ONE line) + post-registration gate REAL rc=0
DIRECT `build/gate-e52p2-reg.log` **1196/0 of 1196**, 181/181, 9/9, 139 rows 0/0,
census 15/0/26/0 (REFUSED 26 unchanged), prose 5 — `dca9219`; COVERAGE row →
SUPPORTED + `EXACT:1`, coverage_check rc=0 139 rows 0/0, no new rows — `90582a5`;
LOAN2 UNMODIFIED, blocker verbatim UNCHANGED (line 99 bare PAGE) — recorded, NOTHING
fixed — and RESULTS.md `755bf1c` + this close prose. BYTE TIER ONLY: no
`spec/RUNTIME.txt` row, no `OUTPUT_CHECK` entry; the copy-in pair is UNRUN. Remaining
unsupported copy forms (loud refusals, named in RESULTS §8): narrowing, differing
scale, forwarded pointer-formals (the E27B route — now LOUD where it passed silently
before), outer-scope actuals, deref/array heads, recursive/RECURSIVE callees, EXTERNAL
entries. **SUCCESSOR: NO active round and NO pending instruction** — see item 0 above;
standing PROPOSALS and constraints kept there; P1 record below kept as written.

SUPERSEDED-BY-ABOVE (kept as written): 6. **E2E-52/P1 CLOSED (2026-11-04; operator
brief: scope-aware DEC pool prescan, LOAN2
defect; hop 6 closing session at HEAD `22b9c0c` + this close commit; ledger ENDS
**C358**).** FULL CHAIN LANDED: pre-registration `d1fbc16`; ORACLE 10 ok/10 + goldens +
RESULTS `e14d180` (zero `dr-refuses`; H1-lexical CONFIRMED on B,C,D,H,I; H3 falsified 5x;
H4 falsified by A/F — the DEC pool is ONE program-wide IMAGE-keyed table, scope- and
name-blind; H2 falsified for DR by E52E; the ONE MISS E52G kept verbatim: predicted ~16,
measured DATA 20); prescan ARM `6a4c554` (B,C,D,H,I byte-exact, controls A/E/F/J at
BASELINE shas, E51 12/12, LOAN2 ADVANCED to its next verbatim blocker `PUT FILE bare
PAGE [TBD] (line 99)` — recorded, NOT fixed); RESULTS §5 `e2a9866`; 9 SPECIMENS (NO G) +
INVENTORY 1186->1195 + post-update gate rc=0 `edf4a25`; claims **C356..C358** from
RESULTS §2 ONLY `7176ff8`; 3 COVERAGE rows, coverage_check rc=0 **139 rows 0/0**
`ab14933`; coverage-stats via its own write path `22b9c0c`. HOP 6 (this session): the
three rows MAPPED in `spec/functional/capabilities.tsv` (DECL.SCALAR_TYPES +
ARITH.DECIMAL + PROC.CALL), rendered status doc refreshed via `--write` rc=0 (unmapped
32->29), `--check` rc=0; hostile suite rc=0 211/211; census `--check` rc=0 counts
identical 15/0/26/0; stats NOT drifted; FULL gate REAL **rc=0** captured DIRECTLY to
`build/gate-e52p1-reg2.log` (byte panel **1195/0 of 1195**, 181/181, 9/9, 139 rows 0/0,
census 15/0/26/0, prose 5). MEASURED PRE-EXISTING, recorded NEVER fixed:
`tools/test_functional_dashboard.py` **rc=1**, sole verbatim FAIL `integration: unmapped
COVERAGE rows are listed, not dropped` — the stale HARDCODED `**26**` check vs rendered
**29** (drift from P1's `216ea7a` DIV rows; the E52 mapping did NOT introduce it).
**E52G STAYS AN OPEN `my-gap`**: never registered, never fitted; its golden is
registered evidence only. PROPOSED, NEVER ADOPTED: the copy-in-temp arm at a future
authorized hop; whether G joins `spec/DIVERGENT.txt`.
**SUCCESSOR: NO active round and NO pending instruction.** Confirm HEAD/tree (only the
operator's `handoff.config.json` edit may be dirty), `/handoff verify`, record state and
**STOP** — await an operator brief. Standing PROPOSALS (shortlist, NEVER
authorizations): E52/P2 copy-in-temp arm (E52G); dashboard `**26**` refresh + mapping
P1's three unmapped DIV rows; FCPS1..3 SPECIMENS registration at a gate hop; README
§ 5.1 rights review for the eight corpus sources (due); E2E-50/P3 shortlist
(`spec/lab-evidence/e2e50-p2/REPORT.md` § 5); fc01-fileio/ONUNIT-00 stay CANCELLED.
Constraints unchanged: no push; goldens never re-derived; NEVER re-run the retry-DFS; no
expansion to other LOAN2 blockers; operator `handoff.config.json` never staged; all rc
captured DIRECTLY.

SUPERSEDED-BY-ABOVE (kept as written): 6. **E2E-52/P1 IN FLIGHT (2026-11-04; operator brief: scope-aware DEC pool prescan,
LOAN2 defect).** Hop 2 LANDED the PRE-REGISTRATION at `d1fbc16` (probes/E52A..J + PLAN/
HYPOTHESES/mkprobes + BASELINE-MINE, committed BEFORE any DR call). Hop 3 LANDED ORACLE +
EVIDENCE at **`e14d180`**: ONE grouped `--tag e52p1` campaign **10 ok/10**, every `.PRN`
`NO ERROR(S)` in both passes -> **zero `dr-refuses`**; six `my-gap` rows (B,C,D,G,H,I) and
four rows already whole-file cmp-BYTE-EXACT vs mine (A/E/F/J — falsification condition 3
NOT triggered). **H1-lexical CONFIRMED** on all five pre-registered discriminators (B DATA
0x10, C CODE inner-binary-immediate, D DATA 0x0A, H CODE/reloc binds THROUGH mid, I DATA
0x15 = lexical prescan_cond); **H3-global-outer falsified** five times; **H4-per-scope-pool
falsified** twice (A,F — the DEC pool is ONE program-wide IMAGE-keyed table, dedup scope-
and name-blind, source-order cells ahead of the variables across scope boundaries); **H2
falsified for DR by E** and kept as the invariant my fix must not introduce. ONE MISS kept
verbatim (PROTOCOL #2): E52G predicted "approx 16", measured **DATA 20 (0x14)** — a DEC
formal gets NO value cell (2-byte caller arg-pointer block @0x0B -> main-side 5-byte
copy-in temp @0x0D; callee 2-byte POINTER cell @0012; literal store through `2A r12` +
`?DSTOP`); reported, never fitted. `ocaml/` UNTOUCHED this hop. Evidence:
`spec/lab-evidence/e2e52-p1/RESULTS.md` §1-§4 + `LEARNINGS.md` § "E2E-52/P1 hop 3".
**SUCCESSOR: execute `PROGRESS.md` -> `## Next action` -> "HOP 5 IN-FLIGHT ADDENDUM"
steps a-d exactly. LANDED+verified: RESULTS §5 `e2a9866`; 9 SPECIMENS (E52A..F,H,I,J,
NO G) + INVENTORY 1186→1195 + post-update gate REAL rc=0 1195/0,181/181,9/9,136 0/0,
15/0/26/0,prose 5 `edf4a25`; claims C356..C358 from RESULTS §2 only, ledger ENDS C358
`7176ff8`; 3 COVERAGE rows, coverage_check rc=0 139 0/0 (rel_parity vocabulary:
DIVERGENT:1, DIFFERS is malformed); checkpoints `564442e`/this. MEASURED open: dashboard
rc=1, sole verbatim FAIL `integration: unmapped COVERAGE rows are listed, not dropped` —
map the 3 rows in the dashboard capability map, NEVER paper over in prose; the stale
`**26**` check did not reappear this run. E52G stays evidence-only (copy-in-temp
PROPOSAL, never fitted). STOP after P1; no push; goldens never re-derived; NEVER re-run
the retry-DFS; operator handoff.config.json never staged; all rc DIRECT.**

SUPERSEDED-BY-ABOVE (kept as written): **SUCCESSOR: execute the exact hop-4 contract in
`PROGRESS.md` -> `## Next action` -> "SCOPE-AWARE PRESCAN IMPLEMENTATION OWED"** (ONE small `pd_own`/`pd_vars` prescan change
per PLAN §4 — `pd_vars` = top rows only, per-proc own rows via the SAME `rt_to_vk`, the
`Sproc` arm recurses with `pd_vars = own @ cx.pd_vars`, all dedup refs INTACT; build; E52
sweep byte-exact with A/E/F/J UNCHANGED to their BASELINE shas; E51A..L 12/12; LOAN2 rerun
UNMODIFIED — record the next blocker, do NOT fix; FULL gate BEFORE registration; SPECIMENS
+ sanctioned `--update-inventory` + gate AGAIN; claims from **C356** ONLY from RESULTS §2;
COVERAGE rows AFTER the inventory; census via its own write path; ALL harness self-tests
(stale dashboard `**26**` check is PRE-EXISTING — record, never silently fix); STOP after
P1). Constraints: no push; preserve operator `handoff.config.json` (dirty, never
staged/cleaned/reverted); goldens/ignored evidence never overwritten or laundered; ledger
ends **C355**; do not expand to other LOAN2 blockers; NEVER re-run the retry-DFS; if a DR
object contradicts the fix direction, stop at evidence + a corrected PROPOSAL.

**E2E-51/P2 CLOSED — operator-authorized functional follow-up (HAMM-00 rev2).** The P1
hop-6 PROPOSED **DERIVATION fix** was executed under its own brief: in
`reference.py:_Hamm00Port.run()` the feed-loop entry `self.skip()` moved INSIDE the
`while True` — the pinned source's `fed0:` label starts with `put skip;`
(HAMM-00.PLI line 131) and re-enters it on every `goto fed0` over-ask retry (line 142),
so rev1's prompt-first retry was NOT statement-faithful for that one loop (buy/sell/
plant retries match; `fedok:`'s post-loop skip was already correct). `HAMM-00.json`
`expected.console` RE-DERIVED VIA SCRIPT from `DERIVATIONS['hamm00']()` — derived, never
captured (L3): delta EXACTLY one blank line at index 64 (year-3 over-ask: s=1587, asked
1588, retry 900; 211→212 lines), predicted from source semantics BEFORE any execution,
then corroborated (the preserved § 16 actual normalizes to the SAME 212-line stream).
`HAMM-00.PLI`, `ocaml/`, the runner, console normalization and all rev1 evidence/goldens
UNTOUCHED. Lane B `build/fc01/hamm-rev2/`: **SOURCE, DERIVATION, COMPILE, LINK, RUN,
ASSERT ALL PASS** (COMPILE rc=0 12288 B code=3996, LINK `HAMM00.COM 13440 B
parse_undefined=[]`, RUN 6369 B, ASSERT complete-stream 212 lines; runner rc=0 captured
DIRECTLY); stage pre-verify `build/fc01/hamm-rev2-srcder/` SOURCE+DERIVATION pass;
`--double-run` `build/fc01/hamm-rev2-double/` rc=0 PASS, captures byte-equal (`cmp` rc=0,
sha `fddc5b2c…`); hostile suite rc=0 211/211; FULL compile-tier gate **rc=0**
`build/gate-hamm00-rev2.log` (byte panel **1186/0 of 1186** intact, 181/181, 9/9, 136 0/0,
census 15/0/26/0, prose 5). Record `docs/functional-results.md` § 17 + § 1 row; § 16's
rev1 FAIL kept intact as written. NO DR claim promoted (ledger ENDS **C355**).
**SUCCESSOR: NO active round and NO pending instruction.** Confirm HEAD/tree (only the
operator's `handoff.config.json` edit may be dirty), `/handoff verify`, record state and
**STOP** — await an operator brief. No LOAN2, CREATE, FCPS registration or other work
without one; no push; goldens never laundered. Standing PROPOSALS (shortlist, NEVER
authorizations): refresh the STALE `tools/test_functional_dashboard.py` check
`cited by NO capability: **26**` (renders **29** since P1's `216ea7a` DIV rows — MEASURED
pre-existing at `1fc37d5`, NOT a P2 regression; run ALL harness self-tests at future
registration hops); FCPS1..3 SPECIMENS registration at a gate hop; README § 5.1 rights
review for the eight corpus sources (due); E2E-50/P3 shortlist
(`spec/lab-evidence/e2e50-p2/REPORT.md` § 5); fc01-fileio/ONUNIT-00 stay CANCELLED; the
OBSOLETE "rev2 subtraction-loop division" workaround stays de-listed. Full P2 record:
`LEARNINGS.md` § "E2E-51/P2 (2026-11-04)"; evidence `build/fc01/hamm-rev2*/` (ignored
working state). Round record below (E2E-51/P1) kept as written per PROTOCOL #2.
readiness-by: session:01a1b43b-ce61-71e7-84a1-50e549adf32f
readiness-at: 2026-11-07T04:49:48.961Z
readiness-checkpoint: g483-1e5d028586db
<!-- guard:end checkpoint -->

## Blockers

- Nothing is half-edited at this boundary; every item below is recorded evidence, not a
  guess.
- **Missing evidence is the limit, never a licence to guess** (`PROTOCOL.md` #4). The
  E2E-49/P4 RESULTS §3 remainders (with the surviving P1/P2/P3/P2e §3 entries) stay named
  refusals until a pre-registered round measures them: NO runtime semantics for `?SCCCM`
  (what it returns and how JNC/JC/JZ read it is NOT claimed — byte tier, no `spec/RUNTIME.txt`
  row may come from these families); STORE value or STORE target with any of the new shapes
  (relation-with-literal, bare-in-relation, negated compare); literal-vs-literal in any
  relation; BASED members in a condition; fixed-member truthiness; `<>`/`><` spellings; `&`/`|`
  composition of conditions; `^( )` over a relation WITH A LITERAL operand; `^( )` over an
  over-extent or a BARE spelling; `^(` `^=` `)` double negation; ordered relations with a
  literal at UNEQUAL attributes beyond the G3..G6 `>`/`<=` sample; bare spellings in the
  equal-length literal template under a relation (only bare `=` is measured, E49D4); the
  equal-attribute `>` collapse inside a relation (NEVER sampled in any bank — the [C348]
  WORDING CORRECTION); `^=` over a ladder; over-extent in INITIAL/STORE; bare `-0` spelling;
  runtime length rewrite; empty-varying PUT output; PUT EDIT of a bit item.
  Shapes REMOVED from this list by P4 MEASUREMENT: ordered relations with a LITERAL operand on
  BOTH literal templates ([C348]); BARE spellings inside an ORDERED relation, member-pair mixes
  included ([C349], extending [C344]); the unequal-extent STRICT-vs-WEAK combinations "beyond
  F2/F4's single pair" — the COMPLETE 4x2 matrix is measured, no arm ([C350]); `^( ... )`
  composition over the four goldened compare shapes ([C351], the un-witnessed negations above
  keep refusing) — the P3-era wording is preserved verbatim in
  `docs/history/2026-11-01-e49p4-closed.md`.
- E2E-50/P2 functional axis (measured, recorded; no byte-tier effect): Lane-B ASSERT framing
  F1 (harness anchor law — P3-a proposal) and F2 (DR PLILIB 79-col print-wrap — declare from
  the oracle side before any expectation change, P3-b); the free core cannot host PLILIB
  programs (BDOS 25 first call, measured; full census UNMEASURED); Package-A licensing =
  operator decision. Details `spec/lab-evidence/e2e50-p2/REPORT.md` §2/§4/§5.
- CREATE is NOT byte-exact; measured front-end blocker: `pli80c.ml` never expands
  `%include` (proposal in `LEARNINGS.md` is `proposed, unverified` — needs its own
  pre-registered round).
- LOAN2's `conflicting kinds` prescan my-gap is a design change, not an arm (see Pending).

- E2E-50/P2 CLOSED — functional-testing foundation + emulator/redistribution audit: audits
  `docs/emulator-audit.md`/`docs/functional-testing.md`/`docs/functional-results.md`; schema
  `pli80-functional/1` + TABLE-00/01 + FX-00/01 + `reference.py` under `spec/functional/tests/`;
  harness `tools/functional_runner.py` + hostile suite 182 checks self-counting; executed
  verdicts FX-00 PASS, FX-01 FAIL/`emulator` (intended), TABLE-00/01 first functional execution
  of a DRPLi-compiled program (CONTENT ≡ REFERENCE; ASSERT FAILs framing F1/F2, attr
  `undefined`); census BDOS-25 free-core blocker measured. Deliverables `d648bcd` (+`68831ff`);
  FULL GATE rc=0 1174/0 (neg 181/181, div 9/9, cov 133/0/0, census 15/0/26/0, prose clean)
  measured at `545dcf1`, recorded `d648bcd`; 23-block byte-verified close archive
  `docs/history/2026-11-02-e50p2-closed.md`.
