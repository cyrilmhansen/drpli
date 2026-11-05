# E2E-52/P3-1 RESULTS — LOAN2 campaign, subround bare PAGE: arm, registration, close

Campaign brief (operator, 2026-11-04): LOAN2 progressive closure — compile
`artefacts/LOAN2.PLI` (sha `7be23ba3…`, UNMODIFIED throughout) toward whole-file
byte-exactness by repeated blocker→evidence→fix cycles. This file records subround
**P3-1** (`PUT FILE` with a bare `PAGE` control item, LOAN2 line 99). All predictions
were pre-registered in `PLAN.md` (committed `b4deba0`, BEFORE any `ocaml/` byte); all
rc values below were captured DIRECTLY (never through a trailing pipeline).

## 1. The difference (as pre-registered in PLAN §1)

`pli80c artefacts/LOAN2.PLI` refused with rc=2, verbatim
`codegen: PUT FILE with a bare PAGE control item [TBD] (line 99) -- PAGE has DR's bytes
(E46N10, 0023-0034, CALL ?PAGOP after the attach) but no specimen of MINE, and LINE is
refused by DR itself (E46N21); SKIP is lowered`.
Classification **my-gap**: DR ACCEPTS the shape ([E2E-42/P2c]; golden
`golden/e42p2c/E46N10/E46N10.REL`; corpus `COPYLPT:53`). No new oracle call was needed —
the DR side was already measured; the root cause was read in code: the raise came from
the E2E-52/P1 lexical PRESCAN (`prescan_stmt` → `match_put_list_lit` → `bare_ctl_put`),
which is also why LOAN2's `open ... print` refusals at lines 54/56 never surfaced.

## 2. The mechanism (arm `adb749c`, edit list B1–B7, `ocaml/lib/codegen.ml` ONLY)

`Sk_page` is a new constructor of `put_skip` — a CONTROL KIND, never an encoded skip.
It is produced ONLY by `file_skip_of` for a bare leading `Pi_ctl("PAGE", None)`;
`file_items` refuses PAGE followed by items BY NAME; `bare_ctl_put` shares the SKIP
route's matcher for bare PAGE and refuses counted PAGE BY NAME (with a local `pfname`
let — `fname` is not in scope there — the one deviation from the pre-verified edit
list); `lower_put_items_gen` emits `call_ext st "?PAGOP"` on the FILE route only,
between the attach and the items/close; the console, console-literal (`lower_put_lit`)
and console-concat (`lower_cat`) routes get LOUD `failwith` arms and can never reach
PAGE; the LIST-arm empty-list message now says "SKIP or PAGE" (accuracy only). Zero new
encoders; `parser.ml`/`bind.ml` untouched; layout ownership unchanged (the prescan
`Pfile` arm sums only item literals — page adds 0 pool bytes).
`dune build` rc=0; binary sha256 `34e8321a…`; the warning profile is IDENTICAL to the
pristine-HEAD baseline (normalized `Warning NN [name]` histograms diffed equal).

## 3. Predictions vs measured

| PLAN ref | Prediction | Measured | Verdict |
|---|---|---|---|
| P1 | E46N10 whole-file `cmp` rc=0 FIRST TRY, 384 B, CODE 62 / DATA 10, `?PAGOP` LINK-CHAIN-EXT at 0030, continuation 0035 | `cmp` rc=0; mine == golden sha `75557545b43f2ad03f8f7ef93f0e5541d5958b7220699b64983a5a0ab0e31d61`; reldump `?SIOOP@002D / ?PAGOP@0030 / ?QIOOP@0033`, `SET-LC code 0035` | **HIT — ZERO FITTED** |
| P2 | E46N1..N9,N11..N19 sweep unchanged | 18/18 whole-file `cmp` rc=0 | HIT |
| P2 | prereg gate rc=0 1196/0 with E46N10 still stamped in REJECTS | FULL gate at the arm REAL **rc=1** (`build/gate-e52p3-prereg.log`): `run_negatives` NEG-FAILs the retired-but-still-stamped row and the census `--verify` fails first on moved messages | **FALSIFIED (design error, kept)** — the retire must PRECEDE the first passing gate; honest prereg state recorded |
| P2 | registration gate negatives 181/181 | **180/180** (`build/gate-e52p3-reg.log`) | **FALSIFIED (count)** — retiring E46N10 from REJECTS removes exactly one negative row; 180/180 is the honest actual |
| P3 | LOAN2 blocker moves PAST 99, expected direction `OPEN option PRINT` (54/56) | blocker moved; ACTUAL verbatim §7 below — `PUT EDIT deferred [TBD] (line 115; ...)`, NOT the OPEN class (OPEN refusals fire in LOWERING; the prescan dies at 115 first) | DIRECTION clause (moves past 99) HELD; specific OPEN-PRINT class **FALSIFIED by stage** |
| P4 | `--update-inventory` 1196→1197, diff exactly ONE line; post-reg gate rc=0 1197/0 | rc=0, one-line diff (`E46N10 refusal→specimen`); gate REAL rc=0 **1197 byte-exact / 0 of 1197** | HIT |
| §3 | boundaries kept | counted PAGE, PAGE+items refuse BY NAME (rc=2); console `put page` and N3_PAGE (`PUT form` marker) untouched; E46N21 pinned marker survives (grep count 1); NON-LEADING PAGE refuses at the **PARSER** (`trailing PAGE control item before ';' is not supported [TBD]`) — stage falsified vs what §3 implied, boundary KEPT | HIT (one stage correction kept above) |
| §3 census | COPYLPT refusal moves off PAGE | COPYLPT census msg now `PUT FILE(PRINTFILE) LIST item 2 is the control item SKIP with a count, unmeasured on the named-file route [TBD] (line 6...` (its PAGE at 53 lowered; a counted SKIP item is next); LOAN2 names PUT EDIT 115; census re-snapshotted via its OWN write path `corpus_census.py --check spec/census/corpus-census.json` rc=0, counts UNCHANGED **15/0/26/0** | HIT (next blocker differs, recorded verbatim) |

## 4. Parity + registration

E46N10 retired from REJECTS + NEG_META (kept as written history in
`tools/e2e_gate.py`, E46K1/K3 precedent) and registered in SPECIMENS at `f15c976`;
sanctioned `--update-inventory` rc=0 (1196→**1197**, diff EXACTLY ONE line) committed
`e728175`; post-registration FULL gate REAL **rc=0** (`build/gate-e52p3-reg.log`):
byte panel **1197/0 of 1197** including `BYTE-EXACT E46N10: .REL == DR oracle
(384 bytes)`, negative **180/180** (§3 count falsification), divergence 9/9, coverage
139 rows 0/0, census 15/0/26/0, prose 5. COVERAGE row `FILE.PUT_PAGE` →
`mine_status=SUPPORTED` + `rel_parity=EXACT:1` (validator vocabulary; P1/P2 lesson),
probes `E46N10` (panel key) + corpus `COPYLPT`, provenance `[C304] [C359]` + both
RESULTS paths; `coverage_check.py` rc=0 DIRECT **139 rows 0/0**
(`build/coverage-check-e52p3.log`); stats via its own write path (REFUSED 23→22,
SUPPORTED 86→87, no_parity 30→29). Claim **C359** written from MEASURED bytes only
(E46N10 golden reldump + COPYLPT:53 span + my first-try `cmp`), ledger ENDS **C359**
(182 claims); `file_prose_check.py` rc=0 (`build/prose-check-e52p3-claims.log`).

## 5. Effects on the panels and sweeps

E46N1..N9,N11..N19: 18/18 whole-file `cmp` rc=0 (zero drift). Negative panel: N3_PAGE
and E46N21 markers intact and still refusing; total 180 (E46N10 row retired).
Divergence panel 9/9 unchanged. No other specimen moved.

## 6. Gate actuals (byte tier only)

- Gate at the arm (before retire): REAL **rc=1** DIRECT → `build/gate-e52p3-prereg.log`
  (§3 falsification; kept as the honest measured prereg state).
- `--update-inventory`: rc=0 → 1197 entries, `git diff` exactly one line.
- Post-registration FULL gate (`timeout 3600 python3 tools/e2e_gate.py`): REAL **rc=0**
  DIRECT → `build/gate-e52p3-reg.log`; actuals in §4.
- Census via its own write path rc=0, counts UNCHANGED 15/0/26/0.
- `coverage_check.py` rc=0 139 rows 0/0; `file_prose_check.py` rc=0 5 active files clean.

## 7. LOAN2 rerun UNMODIFIED

`pli80c artefacts/LOAN2.PLI` rc=2; the blocker MOVED PAST line 99 — ACTUAL verbatim:
`codegen: PUT EDIT deferred [TBD] (line 115; only PUT LIST is implemented; format/picture
editing needs the ?EDITF/?EDTOV/?QDDSL route family)`.
The OPEN `print`/`pagesize` refusals at 54/56 stay QUEUED BEHIND it: they fire during
LOWERING while the lexical prescan dies at 115 first (54/56 are `Sfilestmt`,
prescan-invisible). NOTHING at 115 was fixed this subround; LOAN2 is NEVER claimed exact.
**Next campaign blocker = PUT EDIT (LOAN2:115)** → subround P3-2, its own pre-registered
PLAN before any compiler byte.

## 8. NOT-say / remaining unmeasured PAGE forms

C359 says NOTHING about: `PAGE(n)` (no golden carries a PAGE count), PAGE followed by
items, a non-leading PAGE on a lowered route (the PARSER stop is measured, no object),
CONSOLE `put page` (N3_PAGE/my-gap, no object), and `LINE` (dr-refuses, E46N21 pass 2).
BYTE TIER ONLY: the `?PAGOP` chain has never been executed under cpmsim; there is no
`spec/RUNTIME.txt` row and no `OUTPUT_CHECK` entry for this round. COPYLPT's next
refusal (counted SKIP item at line 6) is itself an unmeasured boundary, not fixed here.

---

# E2E-52/P3-2 RESULTS — subround PUT/GET FILE EDIT: arm, record-order fix, registration

Records subround **P3-2** (LOAN2:115 `PUT EDIT`, armed subset = file PUT+GET EDIT with
bare-skip, literal `f`/`a` formats, string and DEC-variable data items). All predictions
pre-registered in `PLAN.md` §P3-2 BEFORE any `ocaml/` byte; all rc captured DIRECTLY.

## 1. Predictions vs measured

| PLAN ref | Prediction | Measured | Verdict |
|---|---|---|---|
| P1 | P086K whole-file `cmp` rc=0 FIRST TRY, 512 B | rc=1 at octet 32 at arm `a51fb93`; after the record-ORDER fix `2686bcc`, `cmp` rc=0 (512 B, CODE `0065`=101, DATA `0012`=18, sha `c79f196b…` == golden) | **FALSIFIED (first try) then HIT**; the "+3 code bytes" diagnosis itself FALSIFIED — `0x62`=98 is the last code record's ADDRESS; every CODE/pool byte already agreed; the divergence was purely DATA/COMMON record ORDER |
| P2 | P086J `cmp` rc=0 FIRST TRY, 256 B | rc=0 (sha `76524d50…` == golden) at arm, FIRST TRY | HIT — zero fitted |
| P3 | zero drift | sweep **75/75 byte-exact** (E46N 19/19, E52 10/10, E51 12/12, R10 bank 34/34); markers E46K4/E46K15/E46N21 intact rc=2; warning histogram IDENTICAL; binary `748c434fafd8c01579…` (CLEAN rebuild — incremental of the same source hashes `a353f6fc…`; LESSON: always say which build) | HIT |
| P4 | focused refusals name the class; LOAN2 STILL refuses via the fmt_spec catch, message VERBATIM, no line number | rc=2 BY NAME for picture/x(5)/counted-SKIP-at-option-position/PAGE-at-option-position/numeric literal/DEC formal/fixed-bin expression; LOAN2 UNMODIFIED rc=2 `codegen: PUT EDIT format item form unsampled [TBD] (counted, grouped, picture, remote and rep-group formats are not decoded)` — exactly the predicted catch shape, recorded never fitted | HIT; probe-design FALSIFICATION kept: my first counted-SKIP/PAGE probes put the controls INSIDE the data list — the parser collects EDIT controls ONLY from the statement-option position (re-probes p32r9/p32r10 named the class with the correct line 4 on CRLF) |
| P5 | E41X8 compiles rc=0 (no golden — bytes never claimed); retire REJECTS+NEG_META, negatives 180→179 | rc=0 384 B code=93 data=3; retired at `ff1c8f2` with written-history notes; `--update-inventory` diff EXACTLY ONE line `432d431`, refusals 180→**179** | HIT |
| P6 | registration: SPECIMENS P086K+P086J; inventory 1197→1199 EXACTLY TWO lines; gate rc=0 1199/0; census own write path (moved msgs verbatim); COVERAGE after the IFACT/LOAN1 verification; C360 from measured bytes only | `60ed349`: gate REAL **rc=0 1199/0** (`build/gate-e52p3b-reg.log`), negatives 179/179, divergence 9/9, coverage 139 0/0, census 15/0/26/0 IDENTICAL, prose 5; LOAN2 blocker MOVED verbatim (P3-1 deferred-EDIT text gone), COPYLPT UNCHANGED; discrepancy verified (LOAN1 has NO edit stmt; IFACT's edit has NO picture — the row's clause FALSIFIED); COVERAGE row `9e897e8` SUPPORTED+EXACT:12+MEASURED, coverage_check rc=0 139 rows 0/0; claim **C360** `19ce1f4` from PLAN §2 + re-verified reldump bytes ONLY; `file_prose_check.py` rc=0 | HIT |

## 2. The mechanism (arms `a51fb93` + `2686bcc`, `ocaml/lib/codegen.ml` ONLY)

Contract (a)-(g): `edit_match` + file arm of `match_put_edit` (leading bare SKIP →
`Sk_lit "1"`; counted/other controls raise BY NAME); `match_get_edit` over the FLAT parser
list; `edit_stmts`/`prealloc_fmt_tables` FIFO in SOURCE order; new `prescan_stmt` `Sget`
arm for the GET table's pool bytes; `authorize_file_edit_item` admits ONLY PIlit +
PIvar-Vdec; the `is_edit && file <> None` guard and the Vdec `is_edit` refusal DELETED
(premises falsified by P086K/P086J); `lower_get_file_edit` with `?EDTIV` as a `call_ext`
name only. The fix `2686bcc` is the POOL-PARTITION reorder: `prealloc_fmt_tables` returns
its block count, the module assembly partitions statics/tables/lowering and reorders ONLY
the measured shape (tables + COMMON group + no static cells + tables at data 0000); every
other combination RAISES BY NAME as unmeasured. Zero new encoders.

## 3. LOAN2 rerun UNMODIFIED

rc=2, blocker advanced PAST `PUT EDIT deferred [TBD] (line 115 …)` to the fmt_spec catch
above — NOTHING at 115 fixed beyond the armed subset; the picture `p'99/99'` at 115 is the
**P3-3 target** (record `02 A B len text`, operands UNDECODED). LOAN2 is NEVER claimed
exact. Campaign continues: picture `02` decode, `x(w)` `0B` records, rep-groups,
DEC-formal (deref) items, fixed-bin EXPRESSION items, then the PRINT/PAGESIZE OPENs 54/56.

## 4. NOT-say / remaining unmeasured forms

Byte tier only: no P086K/P086J object executed under cpmsim; no `spec/RUNTIME.txt` row.
E41X8's composite open+EDIT bytes are claimed by NOTHING — no golden exists. Counted
SKIP+EDIT, PAGE+EDIT, picture, x(w), rep-groups, remote/counted/grouped formats,
numeric-literal and DEC-formal and fixed-bin-expression EDIT items, FLOAT/member/struct
items and expression format counts all stay refused BY NAME ([C360] "does NOT say").

# E2E-52/P3-3 RESULTS — subround picture `02` decode: oracle campaign + verdicts

Evidence hop (oracle + classification only; ZERO `ocaml/` byte at this point). Baseline HEAD
`eef371b` (PLAN §P3-3 + probes committed BEFORE any compiler byte); ONE grouped campaign
`PLI_SRC=probes timeout 900 python3 oracle/batch.py E52PA..E52PO --tag e52p3 --switches '$L$D'`
rc=0, **14 ok / 15**; goldens + PRNs at `golden/e52p3/<NAME>/`; reldumps (scratch, ignored)
`build/e52p3/E52P*-golden-reldump.txt`.

## 1. Classification of every difference

- **E52PF (`p'9$9'`) is `dr-refuses`** — MEASURED: `1 ERROR(S) IN PASS 1`; the verbatim
  diagnostic points at the statement (`PICTURE                                    ?` under
  `put edit('|',100*m+y)(a,p'9$9');`); NO `.REL` was emitted (dir has PRN/dir.txt only).
  PF has NO golden and its bytes are claimed by NOTHING. The remaining 14 probes are `ok`
  (every `.PRN` NO ERROR(S) both passes).
- Scale-mismatch expectation FALSIFIED (kept as written): E52PJ `9.9` (scale 1), E52PK
  `9V.9` and E52PL `99V.999` (scale 3) vs `d fixed decimal(4,2)` were all **ACCEPTED** —
  DR enforces NO picture-vs-item scale agreement at compile time (measured 3x). The
  pre-registered SECOND bounded batch was therefore NOT needed.

## 2. Measured format tables (whole DATA blobs, from the goldens)

| probe | measured table (record-decoded) |
|---|---|
| E52PA | `80 00 / 03 FF / 02 04 00 05 [99/99] / 81` (14 B) — PREDICTED EXACTLY; EVIDENCE ONLY |
| E52PB | `80 00 / 03 FF / 02 01 00 01 [9] / 81` |
| E52PC | `80 00 / 03 FF / 02 03 00 03 [999] / 81` |
| E52PD | `80 00 / 03 FF / 02 03 00 03 [ZZ9] / 81` — lowercase source stored UPPERCASED (6th witness) |
| E52PE | `80 00 / 03 FF / 02 02 00 03 [$$9] / 81` — digits-only b1 rule (01) FALSIFIED (again) |
| E52PF | NO golden (dr-refuses) |
| E52PG | `80 00 / 03 FF / 02 01 00 01 [9] / 02 02 00 02 [99] / 81` — plain concatenation, NO padding |
| E52PH | `80 00 / 03 FF / 02 0A 02 0F [$$$,$$$,$$9V.99] / 81` — reproduces the LOAN2-179 record IN ISOLATION |
| E52PI | `80 00 / 02 04 02 06 [99V.99] / 81` — `02` flush against the header |
| E52PJ | `80 00 / 02 02 **00** 03 [9.9] / 81` — b2=00, THE designator surprise |
| E52PK | `80 00 / 02 02 **01** 04 [9V.9] / 81` |
| E52PL | `80 00 / 02 05 **03** 07 [99V.999] / 81` |
| E52PM | `80 00 / 02 03 02 05 [9V.99] / 81` |
| E52PN | `80 00 / 02 03 02 05 [9V.99] / 81` — file route, identical table |
| E52PO | `80 00 / 03 FF / 02 03 02 05 [9V.99] / 81` (+ DEC literal cell `50 01 00`, `\|` cell) |

## 3. Hypothesis verdicts (25 records total: 12 existing-golden + 13 new accepted)

- **b1**: E52PF's dr-refuse removes the HA2-vs-HB8 discriminator; the two rules AGREE on
  every ACCEPTED record ($-runs always leading). **digits-only FALSIFIED** (PE: 02; and the
  three multi-$ records). Measured positional law: a `$` AFTER the first {9,Z} digit
  specifier is refused by DR (`9$9`); `$` after `B` and multi-$ leading runs are accepted;
  commas anywhere.
- **b2**: **HC FALSIFIED** by E52PJ (`9.9`: HC predicted 01, measured **00**). **HD
  FALSIFIED** by E52PJ/PK/PL (predicted 01/02/02, measured 00/01/**03**). NEW surviving
  rule **HE: b2 = count of {9,Z} digit characters AFTER the LAST `V`** (0 if no V) — fits
  ALL 25 records; a bare `.` is NOT a b2 designator. V-without-`.` adjacency (e.g. `9V9`)
  stays UNMEASURED — arm refuses it BY NAME.
- **len**: text character count, 13/13 accepted new probes.
- PREDICTIONS-vs-MEASURED: PA/PB/PC/PD/PE/PG/PH/PI/PM/PN/PO table bytes EXACTLY as PLAN §3
  predicted (11 unambiguous predictions, 11 HIT); PJ's unambiguous b2=01 prediction was
  FALSIFIED (measured 00 — the surprise kept verbatim, never fitted); PK/PL carried
  pre-registered dual branches and one branch hit each (HC/HD both dead, HE born).

## 4. Arm + measured parity (binary `c2c6282f5662cb19a3ce…`, CLEAN rebuild; codegen.ml warnings 70 = P3-2 baseline count; full-log histogram FALSIFIED as a method — compare per-File, a clean build compiles every file)

ONE new `Ast.Pi_pic` branch in `fmt_spec` (ocaml/lib/codegen.ml): record
`02 b1 b2 len UPPER(text)`; b1 = count{9,Z,$} − (1 if any $); b2 = count{9,Z} after the
LAST V (0 if none) — the rule HE born from E52PJ's falsification of HC and HD; GUARDS refuse
BY NAME: chars outside {9,Z,$,V,.,B,comma,slash}; `$` after the first digit specifier
(dr-refuses-consistent with E52PF); V without an adjacent `.` (unmeasured); len>255.
- Whole-file cmp **rc=0 vs the new goldens: PB,PC,PD,PE,PG,PH,PI,PJ,PK,PL,PM,PN,PO — 13 of 13**.
  P5 predicted an armable subset of 4 — an UNDERCLAIM, falsified: console fixed-bin-expression
  items were already armed, so the scale-0 family matches too.
- PA rc=2 BY NAME (file-route EXPRESSION item — boundary KEPT, P3-4 owns it); PF rc=2 BY NAME
  (its refusal now mirrors DR's own refuse on that form).
- LOAN2 rerun rc=2 VERBATIM: `codegen: PUT EDIT format item form unsampled [TBD] (counted,
  grouped, picture, remote and rep-group formats are not decoded)` — the SAME static catch text
  (P6 text prediction HIT); it now fires on the grouped/rep-group formats at 147/149 while still
  listing "picture" — recorded message-quality my-gap, NEVER fitted.
- Zero-drift sweep **75/75 byte-exact / 0 FAIL** (E46N 19/19 incl E46N10, E52A..J 10/10,
  E51A..L 12/12, R10 34/34); P086J/P086K cmp rc=0; markers E46K4/E46K15/E46N21 rc=2 intact.

## 5. Registration + effects (hop 12/12, 2026-11-05)

- SPECIMENS: the 13 cmp-rc=0 probes E52PB..E52PE,PG..PL,PM,PN,PO registered with per-probe
  measured comments (tools/e2e_gate.py, commit 7294d09). E52PA stays UNREGISTERED (my-gap
  file-route EXPRESSION item; golden exists, bytes NOT claimed — P3-4 owns the class).
  E52PF registered on the REFUSAL panel as **dr-refuses** (REJECTS + NEG_META, marker
  `picture $ after a digit specifier is dr-refuses` RE-MEASURED rc=2 on the arm binary;
  E46K14/E46N21 precedent — both sides refuse, stages differ).
- Sanctioned `--update-inventory`: EXACTLY +13 specimen lines (1199→1212) + 1 refusal line
  (179→180), diff inspected line-for-line. FULL gate REAL rc=0 DIRECT
  `build/gate-e52p3c-reg.log`: byte panel **1212/0 of 1212** (all 13 BYTE-EXACT lines
  printed), negatives **180/180**, divergence 9/9, coverage 139 rows 0/0, census 15/0/26/0,
  prose 5.
- Census re-snapshotted via its OWN write path (`--check`, rc=0
  `build/e52p3/census-resnap-c.log`): counts IDENTICAL, metadata-only diff; LOAN2 blocker
  VERBATIM UNCHANGED (same fmt_spec catch text), COPYLPT UNCHANGED.
- Claim **C361** committed from MEASURED BYTES ONLY BEFORE the COVERAGE rewrite (ledger ENDS
  C361, `64e464b`); COVERAGE `IO.PUT_EDIT` → EXACT:25, probes +13 panel keys, corpus
  +ANNUITY,DEPREC, picture-refusal clause kept verbatim as HISTORICAL (`4f5d509`);
  coverage_check rc=0 DIRECT 139/0/0 (`build/coverage-check-e52p3c-row.log`); stats NOT
  drifted (own write path). prose rc=0 (`build/prose-check-e52p3c-claims.log`).
- LOAN2 UNMODIFIED: blocker unchanged; P3-4 = rep-groups `2(...)`/`80 n … 81`, `x(w)` `0B`,
  and the file-route EXPRESSION item (PA bytes pinned at LOAN2 0544-0558).

# E2E-52/P3-4 RESULTS — rep-groups, `x(w)`, file-route EXPRESSION item: campaign, PA fix, registration

Records subround **P3-4** (format rep-groups `n(items)` → `80 n … 81`; `x(w)` → `0B w`;
file-route `PUT … EDIT` EXPRESSION data items). Plan + probes (`PLAN.md` §P3-4, `probes/E52PP..E52PZ`)
committed at `3ac7f41`, BEFORE any `ocaml/` byte. All rc captured DIRECTLY (never through a
trailing pipeline); all quoted bytes re-extracted with `tools/reldump.py` from the goldens.

## 1. Campaign (oracle, ONE grouped batch)

`PLI_SRC=probes timeout 900 python3 oracle/batch.py E52PP..E52PZ --tag e52p3d --switches '$L$D'`
rc=0 → **9 ok / 11**; goldens + PRNs at `golden/e52p3d/<NAME>/`, reldumps (scratch, ignored)
`build/e52p3d/<NAME>-golden-reldump.txt`; existing goldens never re-derived.

| probe | DR | classification | measured shape |
|---|---|---|---|
| E52PP | ok | accepted | file `edit('|')(2(a))` → table `80 00 / 80 02 / 03 FF / 81 / 81` (256 B sha `5b2d194c…`; code `0029`=41, DATA `0009`=9) |
| E52PQ | ok | accepted | `a,2(2(a,a),a),2(x(3),a)` → 24 B table `80 00 03 FF 80 02 80 02 03 FF 03 FF 81 03 FF 81 80 02 0B 03 03 FF 81 81` (256 B sha `88df84be…`; code `0029`, DATA `0019`=25) — double nesting, siblings, source order, NO flattening |
| E52PR | ok | accepted | CONSOLE `2(skip,a),p'99'` + expression item → `80 00 80 02 0C FF 03 FF 81 02 02 00 02 39 39 81` (256 B sha `c4505cd5…`; code `003C`=60, DATA `0015`=21) — the rep-group law is ROUTE-INDEPENDENT |
| E52PS | ok | accepted | `1(a)` → `80 00 03 FF 81` (256 B sha `6c870471…`; code `0029`, DATA `0006`=6) — **count 1 SPLICES, no `80 01 … 81` wrapper** |
| E52PT | ok | accepted | `x(1),a,x(5)` → `80 00 0B 01 03 FF 0B 05 81` (256 B sha `3bb15a6b…`; code `0029`, DATA `000A`=10) — `x(w)` = `0B w` exactly |
| E52PU | **no `.REL`** | **dr-refuses** | bare `x`: `SYNTAX ?` in pass 1 (+ `UNEXPECTED EOF` cascade); PRN only |
| E52PV | **no `.REL`** | **dr-refuses** (partially informative) | `x(255)`: `BAD VAL ?`, `1 ERROR(S) IN PASS 1`; the SAME listing carries compile `c` rows for **x(128) and x(0)** — acceptance measured, BYTES unmeasured |
| E52PW | ok | accepted | file `edit(m+y)(a)` → `2A r(cell) / EB / 2A r(cell) / 19 / 3E 09 / ?QICOP / ?EDTOV` (256 B sha `3c2590b1…`; code `002E`=46, DATA `0009`) |
| E52PX | ok | accepted | `edit(100*m)(a)` → `2A r / 11 64 00 / ?IM22N / 3E 09 …` **NO XCHG** (256 B sha `27b7eeea…`; code `002F`=47, DATA `0007`=7) |
| E52PY | ok | accepted | `edit(m-y)(a)` → `2A / EB / 2A / ?IS22N / 3E 09 …` (256 B sha `7a1fa309…`; code `0030`=48, DATA `0009`) |
| E52PZ | ok | accepted | `edit(m/3)(a)` → `2A r / 3E 03 / E5 6F 87 9F 67 D1 / ?ID22N / 3E 09 …` — literal DIVISION ACCEPTED on the file route (256 B sha `31c40111…`; code `0034`=52, DATA `0007`) — preamble semantics NOT decoded, byte tier only |

PU and PV have NO golden and their bytes are claimed by NOTHING; both are registered on the
REFUSAL panel as `dr-refuses` (REJECTS + NEG_META, markers taken from MY re-measured stderr, see §5).

## 2. Hypothesis verdicts (pre-registered in PLAN §P3-4 §3, kept verbatim)

- **H2a** — "`1(a)` emits `80 01 03 FF 81`" — **FALSIFIED** (PS measured `80 00 03 FF 81`).
- **H2b** — "`1(a)` is REFUSED" — **FALSIFIED** (PS accepted, `NO ERROR(S)` both passes).
- **H2c** — "count 1 flattens: inner records are spliced with no wrapper" — **CONFIRMED**.
  Group law overall: `80 n <subrecords in source order> 81`, recursive, NO flattening for `n ≥ 2`.
- **H4a** — "`x(128)`, `x(255)`, `x(0)` all accept and emit plain `0B w`" — **FALSIFIED**
  (x(255) `BAD VAL`, no object).
- **H4b** — "a REFUSAL above the then-measured max width 19 — WHICH width first is the measurement"
  — **FALSIFIED IN DETAIL**: DR compiles x(128) and x(0) (listing `c` rows) and refuses only x(255);
  the refusal boundary is **255, not 20**. Kept as the live gap: widths **14..128 are compile-accepted
  with NO object witness**, 129..254 UNMEASURED; my arm therefore arms `0B w` only for literal
  `w ≤ 128` and refuses above BY NAME as unmeasured.
- **H5a** (`0B 00`) and **H5b** (`0B 01`) — **MOOT**, PU carries no object.
- **H5c** — "bare `x` is REFUSED" — **CONFIRMED** (`SYNTAX ?`, no `.REL`).
- **H6a** — "PX keeps LOAN2's `XCHG` after `?IM22N`" — **FALSIFIED** (PX has no XCHG).
- **H6b** — "`?IM22N` returns the product in HL; no XCHG when the product IS the whole item" —
  **CONFIRMED** (LOAN2's `EB` parks a product for the FOLLOWING sum operand — E52PA reproduces it).
- P3-4 brief wording "fmt_spec `Pi_rep`" — **FALSIFIED**: the parser node is `Ast.Pi_repgrp`
  (`parser.ml` 939); the arm matches that.

## 3. The subround HEADLINE — E52PA byte-exact, and the crash that preceded it

Pre-registered requirement: `E52PA` whole-file `cmp` rc=0 vs the **EXISTING**
`golden/e52p3/E52PA/E52PA.REL` (sha `d7b4e7f32b9c…`, 384 B, code `004E`=78, DATA `0013`=19 —
reldump values; my compiler's own `data=4` stat line is NOT the golden's DATA size and is never
cited as such).

At the campaign hop the arm made the other nine probes exact but PA CRASHED: `Fatal error: exception
File "lib/codegen.ml", line 11906 … Pattern matching failed` at the syntactically exhaustive match
inside `edit_num_cell`. Root cause (`9b2d781`, `ocaml/lib/codegen.ml` ONLY): the `Eident` arm ended
in an UNPARENTHESISED inner `match vk_of st nm with … | _ -> false`, so OCaml swallowed the OUTER
`| _ -> false` as a third INNER arm, leaving the outer match non-exhaustive; proven with `-dlambda`
(`raise (Match_failure ["lib/codegen.ml" 11921 2])`) after `Obj` instrumentation showed a valid
`Ebinary` scrutinee. The two earlier suspects — stale line map, PIlit `'|'` interaction — are BOTH
**FALSIFIED**; PA is simply the first probe feeding a NON-`Eident` node to `edit_num_cell` (which is
why PW/PX/PY/PZ passed with the bug in). `lib/dune`'s `-warn-error -a` **disables** warnings-as-
errors, so `dune build` rc=0 shipped it; the +4 codegen warning delta (74 vs the 70 baseline =
Warning 8 + Warning 11, doubled byte+native) was the fingerprint and is back to **70** after the fix.

**MET:** on the clean-rebuild binary sha256 `345644822818326f442a…`, E52PA compiles rc=0 (384 B) and
`cmp` rc=0 against the existing golden — never fitted. Its code span 0032-0047 is BYTE-FOR-BYTE
LOAN2.REL 0544-0558 (the LOAN2:115 mirror: `2A RELOC data 0F / 11 64 00 / ?IM22N / EB / 2A RELOC
data 11 / 19 / 3E 09 / ?QICOP / ?EDTOV`). Re-verified a THIRD time at the close hop on the same
binary (all 10 cmps rc=0, `build/e52p3e/`).

## 4. The arm + zero-drift measurements

Arm (`codegen.ml` ONLY): `fmt_spec` became `let rec`; `Pi_repgrp` → `80 n … 81` recursive with the
count-1 SPLICE and a refusal at count 0 (unmeasured); `Pi_fmt X [w]` with `fcount=None` → `0B w` for
literal `w ≤ 128`; `authorize_file_edit_item` admits `PInum` through the new shape authority
`edit_num_tree/edit_num_cell/edit_num_lit/edit_num_operand` (`+`/`-` over cells and admitted trees,
`*` ONLY literal-left × cell, `/` ONLY cell/literal, parens unwrapped, Vint non-deref cells only);
float/DEC/member/call/subscript shapes keep refusing BY NAME. Zero new encoders elsewhere.

- **10/10** accepted-probe whole-file `cmp` rc=0 (PP,PQ,PR,PS,PT,PW,PX,PY,PZ vs the NEW goldens;
  PA vs the EXISTING golden) — measured at `898b191c…` (campaign hop), re-verified at `3456448228…`
  (fix hop) and again at the close hop (`build/e52p3e/`).
- Zero-drift sweep **89/89 byte-exact / 0 FAIL** on the final binary: E52PB..PO 13, E46N1..N19 19,
  E52A..J 10, E51A..L 12, R10xx **33** (the earlier "34" record was a count slip — falsified by
  re-extraction), P086J/K 2.
- Boundary markers all rc=2 with pinned texts: E46K4 (member), E46K15 (GET form), E46N21
  (LINE-with-count), E52PF (picture `$`-after-digit dr-refuses mirror), plus the two NEW rows §5.

## 5. LOAN2 rerun UNMODIFIED + registration

- LOAN2 (`artefacts/LOAN2.PLI`, sha `7be23ba3…`, UNMODIFIED, positional args) rc=2, blocker
  **ADVANCED past** the fmt_spec format catch (rep-groups and pictures now lower) VERBATIM to:
  `codegen: PUT FILE(OUTPUT) EDIT shape [TBD] (line 212) -- an EDIT list the matcher cannot split
  into data items plus a final wrapped format list: empty data, a trailing item after the format
  list, or an item class classify_item does not name`. It fires in the PRESCAN walk, so line 147's
  DEC formals are never reached: the pre-registered prediction "next blocker = DEC FORMAL at 147 via
  `authorize_file_edit_item`" is **FALSIFIED AT STAGE LEVEL**; the direction (the blocker moves) held.
  Classification `my-gap` (DR compiles LOAN2 whole); recorded, NOT fixed, never claimed exact
  (`build/e52p3d/LOAN2-mine-stderr.txt`, re-measured at close in `build/e52p3e/`).
- SPECIMENS +10 (`e397ed9`) with measured comments; NEW honest `dr-refuses` REJECTS/NEG_META rows for
  **E52PU** (marker `BARE x (no width) is dr-refuses`) and **E52PV** (marker `x(width) above 128 is
  unmeasured`) — markers taken from MY ACTUAL re-measured rc=2 stderr, never assumed.
- Sanctioned `--update-inventory` rc=0: EXACTLY 1212→**1222** specimens and 180→**182** refusals,
  diff line-for-line (12 insertion lines).
- Census re-snapshotted via its OWN write path (`corpus_census.py --check /tmp/census-prev-p34.json`)
  rc=0, counts **IDENTICAL 15/0/26/0**, with EXACTLY the three predicted message moves — ACKTST →
  `PUT numeric item form unproven [TBD]`, FSCAN → `char store from non-literal [TBD]`, LOAN2 → the
  line-212 text ABOVE VERBATIM (metadata `head 2c51941 binary c4c5b44f dirty 3`).
- FULL gate REAL **rc=0 DIRECT** `build/gate-e52p3d-reg.log`: byte panel **1222 byte-exact / 0 of
  1222** (all 10 new BYTE-EXACT lines printed), negatives **182/182** (NEG-OK E52PU, E52PV, E52PF
  all alive), divergence 9/9, coverage 139 rows 0/0, census 15/0/26/0, prose 5.
- Claim **C362** committed `1de3e28` from MEASURED BYTES ONLY, BEFORE the COVERAGE `IO.PUT_EDIT`
  rewrite `8c3b0b4` (cite-resolution lesson; ledger ENDS **C362**, 183 claims). `IO.PUT_EDIT` →
  `rel_parity=EXACT:35` (25 prior + 10 new), probes +E52PA,E52PP..E52PZ; the two falsified P3-3-era
  clauses ("x(w) … not armed", "rep-groups … still refusing") and the stale LOAN2 blocker text are
  kept VERBATIM as HISTORICAL per PROTOCOL #2. coverage_check rc=0 DIRECT **139 rows 0/0**
  (`build/coverage-check-e52p3d-coverage.log`), stats NOT drifted; prose rc=0 standalone
  (`build/prose-check-e52p3d-reg.log`).

## 6. What P3-4 does NOT say / live refusals (P3-5 perimeter)

- **Byte tier only**: no `80 n`/`0B w`/XCHG-parking/?ID22N-preamble RUNTIME meaning is claimed; no
  object was executed under cpmsim; no `spec/RUNTIME.txt` row, no `OUTPUT_CHECK` entry.
- x-widths **14..128** have NO object witness (compile-accepted by PV's listing only); 129..254
  UNMEASURED; bare `x` has no object (PU).
- Group **count 0** UNMEASURED, refused BY NAME; `Pi_group` (no count) never sampled; `column(n)`
  `0D w` decoded but NOT armed.
- File-route **DEC formal/deref** items (LOAN2 147), **numeric-LITERAL** items, **PIvar bin-var**
  items (LOAN2 177 pins them), counted **SKIP**/**PAGE** beside EDIT, format **COUNT expressions**,
  and remote/counted/grouped formats ALL still refuse BY NAME — the line-212 matcher-split blocker
  stands. LOAN2 is NEVER claimed exact.
- Harness lessons adopted: a reldump byte regex must accept DR's UNPADDED `0x0` (a `{1,2}`-free
  2-digit regex silently drops 0x00 bytes and falsified my first extraction); census `--verify`
  drift is **FATAL** in a normal gate (it aborts BEFORE the byte panel) — run the census own-write
  path first; cite reldump `DEF-DATA-SIZE`, never the compiler's own stat shorthand, in evidence.


## §P3-5 — DATA-item DO-repetition on the EDIT route (campaign e52p5) — CLOSED

Pre-registered `67e5414` (PLAN §P3-5 + probes E52RA..E52RJ BEFORE any ocaml/ byte). Oracle
ONE grouped campaign rc=0 **9 ok/10** at `676fb9d`: E52RE dr-refuses (`BALANCE ?`+`SYNTAX ?`+
`UNEXPECTED EOF`, NO .REL); RC BY and RG rep-of-char-var **DR-ACCEPTED whole goldens** —
boundaries KEPT refused BY NAME (my-gap, never fitted). Arm `aeda739` (parser REPSPEC child 0 =
index Eident + BY parse refusal; codegen `PIrep`, both-route `data` walker admission, prescan
inner-cells-ONCE, authorizer admits PIlit/PInum-inner, named `emit_item` §2 loop). RB's
first-try MISS at octet 275 decoded the PATCH law (non-final JP → NEXT item start; final →
close `?QIOOP`). Hop-9 arms: defensive `| PIrep _ -> a` prescan-fold (`a008840`; histogram
70 replay-of-`aeda739` → 68, diff EXACTLY −2 W8 at the fixed site) + named REVERSE parse
refusal mirroring DR's verdict (`3a494c3` — the pre-registered `expected )` marker prediction
FALSIFIED at registration: the panel requires [TBD]). MEASURED: **RA RB RD RF RH RI RJ whole-file
cmp rc=0** (clean binary `e55e892c346741b2`, hop-8 binary produced byte-identical objects); H1
(loop law) H2 (route-independence, RH) H3 (var-bound byte-identical, RF) H6 (RI table
`80 00 80 02 03 FF 81 81`) CONFIRMED; H4: BY dr-accepted (RC object) / REVERSE dr-refuses; H5:
RG DR-accepted, RG/RJ — RJ accepted-and-byte-exact, RG refused-by-name boundary KEPT.
Registration: SPECIMENS +7 + RE row; `--update-inventory` 1222→1229 + 182→183 EXACTLY; census
own write path rc=0 counts UNCHANGED 15/0/26/0, LOAN2 blocker MOVED VERBATIM to
`codegen: ON UNDEFINEDFILE is not implemented [TBD] (only ENDFILE(<file>) has a DR lowering;
line 44)` at LOWERING — the line-177 `PIvar yp` prediction FALSIFIED at stage level, recorded,
NOT fixed; FULL gate REAL rc=0 **1229/0**, 183/183, 9/9, 139 rows 0/0, prose 5
(`build/gate-e52p5-reg.log`); claim **C363** (`c940426`, measured bytes only) BEFORE the
COVERAGE rewrite EXACT 35→42 (`2be56f0`, coverage_check rc=0). Byte tier only — no runtime row.
UNMEASURED (never promote): to<=2, from=0, 1-byte index, variable FROM, deref index/bound,
nested rep, BY bytes, RG char-var bytes, numeric-LITERAL/DEC-inner reps.

## P3-6 — ON UNDEFINEDFILE(<file>) + the GOTO-terminated handler (CLOSED 2026-11-05, hop 12 = CAP)

Campaign e52p6 (measured hop 11, rc=0 5 ok/7): SA SB SC SD SE ACCEPTED by DR (NO ERROR(S)
both passes; goldens golden/e52p6/ committed 5ab8639, sizes 256/384/256/256/256 B); SF and SG
dr-refuses (PASS 1 clean, PASS 2 `SYNTAX ?', NO .REL). Arm `8fc0a3b` (bind.ml + codegen.ml):
registration prefix condition-blind with byte 06 (H1/H2 CONFIRMED); goto-terminated BEGIN...END
handler inline + C3, NO C9 (H3); pad LHLD/SPHL/?RECOV + entry DAD SP/SHLD (H4); SC proves pad
vs continuation targets INDEPENDENT; SD = [C201] pair. SA octet-142 first-try MISS decoded the
ON-unit branch-boundary reload law (golden `21 02 00 22` vs mine `23 22`), fixed for both names,
sweep 110/0 corroborating. FALSIFIED: `BEGIN;..;end;` = nameless Sproc/Bbegin not Sdobegin;
briefed sweep-101 undercount (110); hop-10 "no DR sample"/"codegen-only" re-confirmed.
SE REVERT UNDEFINEDFILE DR-ACCEPTED (06+`?REVOP`) KEPT UNARMED — measured my-gap, negative-panel
row. Registered hop 12: SPECIMENS +4 (1229->1233), negatives +3 (183->186) `91592c0`; census own
path rc=0 counts UNCHANGED 15/0/26/0, LOAN2 blocker VERBATIM ADVANCED past 44 to
`OPEN option PRINT ... (line 54)` (§3 prediction HIT), EXPR1/EXPR2 catch-all text moved `9febae8`;
FULL gate rc=0 DIRECT `build/gate-e52p6-reg.log` (1233/0, 186/186, 9/9, 139 0/0, census 15/0/26/0,
prose 5); claim **C364** measured-bytes-only `73b9c53` BEFORE COVERAGE EXACT:14->18 `6e6ed37`
(coverage_check rc=0); binary 0efc35e6d4ff81bd, codegen warnings 68 == baseline. NEXT blocker
(NOT touched): LOAN2:54 OPEN PRINT — candidate P3-7. No runtime assertions; goldens immutable.

## P3-7 — OPEN PRINT / PAGESIZE / LINESIZE (campaign e52p7) — CLOSED (2026-11-05, hop 5)

Pre-registered `2bca084` (PLAN §P3-7 + probes E52TA..TJ COMMITTED BEFORE any `ocaml/` byte; the
whole class decoded from EXISTING `spec/lab-evidence/e2e41-p0/OPEN-BLOCKS.txt` + `OPEN-MATRIX.tsv`
+ `W1-BITFIT.txt`, shapes A–F); goldens committed VERBATIM `272a996`; arm `ccf0036`. All rc
captured DIRECTLY (never through a trailing pipeline); no oracle call after the hop-2 campaign.

## 1. Campaign (oracle, ONE grouped batch)

`PLI_SRC=probes timeout 900 python3 oracle/batch.py E52TA E52TB E52TC E52TD E52TE E52TF E52TG
E52TH E52TI E52TJ --tag e52p7 --switches '$L$D'` rc=0 → **10 ok / 10**; EVERY `.PRN` NO ERROR(S)
in both passes — **ZERO dr-refuses**, so NO refusal row joined the NEGATIVES panel from this
campaign. Goldens `golden/e52p7/`, reldumps (scratch, ignored) `build/e52p7/`.

## 2. Measured table (whole-file cmp rc=0 on clean binary `8b374e623bc9e280…`)

| probe | OPEN statement | object | CODE/DATA | OPEN block | w1 | measured fact |
|---|---|---|---|---|---|---|
| E52TA | `open file(pf) print;` | 256 B | `0035`=53 / `0002` | 21 B | 0652 | shape A verbatim (P019B:3): bit 0x0002 on the OUTPUT-side base 0x0650, 0x0200 KEPT |
| E52TB | `open file(outf) title('$con') print pagesize(0);` | 384 B | `003D`=61 / `0006` | 29 B | 2E52 | PAGESIZE(0) = a BIT plus a plain zero word, NO extra byte; byte-identical to DEPREC:51 |
| E52TC | `open file(outf) title(name) print;` (char(14) varying) | 384 B | `003B`=59 / `0011` | 27 B | 0E52 | the PRINT bit composes with the TITLE bit; `?SLVTS` route (LOAN2:56 class) |
| E52TD | `open file(pf) stream print pagesize(60);` | 256 B | `0038`=56 / `0002` | 24 B | 2652 | `STREAM` is BYTE-INVISIBLE on this route (prologue + word equal the bare-print forms); w5 `2E 3C` MVI L,3C, w6 `68` MOV L,B — legal only because B=0 |
| E52TE | `open file(keys) stream output linesize(60) title('$1.key');` | 384 B | `003F`=63 / `0008` | 31 B | 1E50 | LINESIZE literal in w6 (KEYFILE:19 class) |
| E52TF | `open file(printfile) print pagesize(ps) linesize(lw) title(line);` both vars | 384 B | `0041`=65 / `0015` | 33 B | 3E52 | VARIABLE attributes are `2A r(cell)` LHLD + DATA relocation (COPYLPT:38 class) |
| E52TG | titled `print pagesize(60)` (w6 zero) | 384 B | `0040`=64 / `0006` | **32 B** | 2E52-class | byte-ENCODING prediction HIT (`2E 3C`/E5 then `6C`/E5); pre-registered 30-B TOTAL FALSIFIED (§4) |
| E52TH | titled BOTH literals | 384 B | `0041`=65 / `0006` | **33 B** | 3E52-class | w5 `2E 3C`, w6 `2E 50`, NO `LXI H`, written order kept; same TOTAL falsification (§4) |
| E52TI | titleless VARIABLE PAGESIZE alone | 256 B | `003A`=58 / `0004` | 26 B | 2652 | w5 LHLD + reloc, then w6 `60 68` — THE PRE-REGISTERED FALSIFIER TRIGGERED (§4) |
| E52TJ | titleless `pagesize(300)` (> 0xFF) | 256 B | `003A`=58 / `0002` | 26 B | 2652 | DR ACCEPTED via w5 `21 2C 01` (LXI H full literal) + w6 `60 68`; accept branch realised verbatim (§4) |

## 3. Hypothesis verdicts (pre-registered in PLAN §P3-7 §3, kept verbatim)

- **H1** "PRINT sets 0x0002|0x0040 and leaves 0x0200 set (A: 0x0652 = 0x0650|0x0002)" — **CONFIRMED** (TA).
- **H2** "the PRINT bits compose with a title bit exactly as D/C show" — **CONFIRMED** (TC 0x0E52; TB 0x2E52).
- **H3** "PAGESIZE(0) = bit only, word zero, no extra byte" — **CONFIRMED** (TB == DEPREC:51 byte for byte).
- **H4** "a literal attribute ≤ 0xFF uses `MVI L,v`" — **CONFIRMED** (TD w5 `2E 3C`; TE w6 `2E 3C`).
- **H5** "a variable attribute uses `LHLD <cell>` + DATA reloc" — **CONFIRMED** (TF both words; TI w5).
- **H6** "OUTPUT+PRINT never co-occurs in the corpus ⇒ refused" — **REFUSED-AS-DESIGNED**: the arm guards
  print+INPUT and print+OUTPUT BY NAME as UNMEASURED and never put either to DR. Separately FALSIFIED
  this campaign: the idea that PRINT is merely a spelling of OUTPUT — the 0x0200 bit is KEPT in the
  PRINT word, so 0x0652 ≠ the titleless-OUTPUT candidate 0x0650.

## 4. The four UNDECIDABLE boundaries (predictions VERBATIM, NEVER fit)

- **TG** predicted "H-enc: `21 52 2E/E5, 21 00 00, E5×3, 2E 3C/E5, 6C/E5` → 30 B. falsifier: any other
  zero-restoration (e.g. `21 00 00`) or a different order." — the ENCodings HIT exactly (the titled
  zero-after-literal restoration IS `6C` MOV L,H); the **30-B TOTAL was FALSIFIED — measured block
  32 B** — an arithmetic slip in the pre-registration sum, kept as written.
- **TH** predicted "H-enc w5 `2E 3C`, w6 `2E 50`, 30 B; falsifier: `LXI H` forms or a different word
  order." — ENCodings HIT (no `LXI H`, order preserved); **TOTAL FALSIFIED — measured 33 B**, kept verbatim.
- **TI** predicted "`… E5×3, 2A r(x), E5, 21 00 00, E5` (31 B); falsifier: any other materialisation."
  — **THE FALSIFIER TRIGGERED**: DR wrote `60 68` (re-materialise HL from B after the `LHLD` clobbered
  both halves), NOT `21 00 00`; measured block 26 B. The prediction is kept as written; the ladder in
  **[C365]** is DR's measured law, not my fit.
- **TJ** predicted "DR verdict UNKNOWN (BAD VAL refusal or `21 2C 01`); whichever it is is recorded
  verbatim; NO fitting." — DR **ACCEPTED** `pagesize(300)`; the `21 2C 01` accept branch realised verbatim.

## 5. Arm + registration chain

Arm `ccf0036` (`ocaml/lib/codegen.ml` ONLY): `open_subset_keys` += PRINT/PAGESIZE/LINESIZE; the
`open_mode_word` PRINT branch (0x0652 titleless / 0x0E52 titled) behind the print+INPUT and
print+OUTPUT guards; `open_attr_plan` enforces the MEASURED combination matrix and refuses
everything outside it BY NAME with [TBD]; ONE `open_emit_words` walks the measured register-reuse
ladder in all three title branches. `dune build` rc=0 DIRECT after two draft fixes (literal
`\u00a7`/`\u2014` escapes → the real characters; a redundant `A_zero` sub-pattern); per-File codegen
warning histogram **68 == baseline**. SPECIMENS +10 with the measured-law comment and sanctioned
`--update-inventory` **1233→1243** (diff EXACTLY +10 specimen lines, ZERO removals, refusals stay
186) `6b8d851`; census OWN write path rc=0, counts UNCHANGED **15/0/26/0** `f6fd2b9` — TWO rows
moved VERBATIM: LOAN2 ADVANCED past 54/56 to `codegen: ON ERROR is not implemented [TBD] (only
ENDFILE(<file>) and UNDEFINEDFILE(<file>) have a DR lowering; line 58)` (the §6 prediction HIT,
**NOT fixed** — a later subround owns ON ERROR) and RETRIEVE ADVANCED past its line-19
`title(name) print` open to `OPEN option ENVIRONMENT is outside what this compiler lowers [TBD]
(line 31)` — a real advance, NO claim. Sweep **114/0** (the bank grew past hop-12's 110 via the
E52SA..SD rows); boundary markers rc=2 intact (E46K4/K15/N21/E52PF/PU/PV/RE + SE/SF/SG). FULL gate
REAL rc=0 DIRECT `build/gate-e52p7-reg.log` (1243/0, 186/186, 9/9, 139 rows 0/0, census 15/0/26/0,
prose 5). Claim **C365** from MEASURED BYTES ONLY `a6e814f` committed **BEFORE** the COVERAGE
rewrite `d9ebb30`: row `FILE.OPEN_STREAM` falsified PRINT clause kept VERBATIM as HISTORICAL (id
KEPT); NEW row `FILE.OPEN_PRINT_ATTRS` SUPPORTED + EXACT:10; labelled [E2E-52/P3-7 CORRECTION]
appends to `FILE.OPEN_STREAM_OUTPUT`, `FILE.PUT_LIST`, `FILE.OPEN_TITLE_STATIC`;
`coverage_check.py` rc=0 **140 rows 0/0** with stats refreshed by its own run (the stats' own
write path). `spec/PERIMETER.md` line 38 carries the campaign-wide correction landed in this hop.

## 6. What P3-7 does NOT say (byte tier only)

- **Byte tier only**: no LINK, no cpmsim run, no `spec/RUNTIME.txt` row, no `OUTPUT_CHECK` entry;
  NO runtime meaning is asserted for any of the six pushed words or the attribute bits.
- KEPT boundaries refuse BY NAME as MY perimeter, never promoted to a DR rule: PRINT with INPUT or
  with the spelled OUTPUT; attributes on INPUT, modeless, ENVIRONMENT, KEYED or DIRECT opens; an
  attribute without an operand; EXPRESSION operands; literals above 0xFF beyond the measured TJ form
  on the titleless route; variables that are not plain automatic FIXED BIN 2-byte cells; the TITLED
  zero-restoration after a clobbering parameter word (UNMEASURED); LINESIZE alone on a titled PRINT
  open; a 16-bit LINESIZE; titleless `pagesize(0)`; mixed literal/variable attribute pairs.
- Corpus users (COPYLPT, DEPREC, KEYFILE, LOAN2, RETRIEVE) are users of the CONSTRUCT, not parity
  claims — the census counts never moved.
- LOAN2 is NEVER claimed exact; it still refuses at ON ERROR line 58 (recorded, NOT fixed).
  E52SE stays a measured `my-gap`, SF/SG stay `dr-refuses`; goldens are evidence, NEVER re-derived.
