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

## P3-8 — ON ERROR: the ABSOLUTE-operand registration prefix + the BODY-DEPENDENT handler tail (campaign e52p8) — CLOSED (2026-11-05, hop 3)

Pre-registered `e6d16ff` (PLAN §P3-8 H1–H6 + probes E52UA..UF, committed BEFORE any `ocaml/` byte;
the shape class decoded FIRST from the FIVE pre-existing witnesses LOAN2/ANNUITY/COPYLPT/EXPR1/EXPR2
with ZERO oracle calls in hops 1–2); oracle campaign 6 ok/6; goldens committed VERBATIM `9f36504`;
arm `a7ab5a4` (`ocaml/lib/codegen.ml` ONLY); claim **C366** `17c9963` written from MEASURED BYTES ONLY
and committed BEFORE the COVERAGE rewrite `0cf0688`. All rc captured DIRECTLY (never through a
trailing pipeline); goldens NEVER re-derived; `pli80c` invoked POSITIONALLY; no push.

## 1. Campaign (oracle, ONE grouped batch)

`PLI_SRC=probes timeout 900 python3 oracle/batch.py E52UA E52UB E52UC E52UD E52UE E52UF --tag e52p8
--switches '$L$D'` rc=0 → **6 ok / 6**; every `.PRN` reads `NO ERROR(S) IN PASS 1` AND `NO ERROR(S)
IN PASS 2` — **ZERO dr-refuses**, so NO refusal row joined the NEGATIVES panel from this campaign and
the negative count stayed 186. Goldens `golden/e52p8/` (all six names new to the `NoOverwriteDict`
`SPECIMENS` wrapper — accepted, no SUBSTITUTION); reldumps scratch `build/e52p8/`, registration dumps
`build/e52p8-reg/e52U*-golden-reldump.txt` + `*-mine-reldump.txt`.

## 2. Measured table (whole-file cmp rc=0 on clean binary `9ecea27aa4f2d80f49ad…`)

| probe | ON unit | object | CODE/DATA | registration | handler tail | measured fact |
|---|---|---|---|---|---|---|
| E52UA | `on error x = 1;` | 128 B sha `6baf855210d3…` | `0020`=32 / `0002` | @0006 `21 00 00`(ABS) `AF` `CD ?ONCOP` `C3 slot@000E`→0x17 | `21 01 00 / 22 r(x)` @0010 then **`C9`** @0016 | bare `error` = argument 0 as the LXI operand; a FILE-LESS object carries **NO COMMON group and NO `LINK-DEF-COMMON`/`LINK-SEL-COMMON` record at all**, and the argument operand `0007-0008` has **NO relocation record** — the only patches in the 10 registration bytes are the `?ONCOP` external chain (000B) and the jump-over slot itself (`SET-LC 000E / RELOC code 0x17`) |
| E52UB | `on error goto lbl;` (REMOTE label) | 256 B sha `b68d334de66f…` | `0030`=48 / `0004` | @000D, same 10-byte prefix | entry SP-save `21 00 00 / 39 / 22 r(data 2)` @0006; `C3` @0017 (slot 0018 `CHAIN-ADDR`) → pad @0020 `2A r(data 2) / F9 / CD ?RECOV`, **NO `C9`** | **TWO INDEPENDENT patch triples** — `SET-LC 0015 / RELOC code 0x1A` (jump-over → continuation) and `SET-LC 0018` region `CHAIN-ADDR 0018` (handler → pad) [C208]; the goto form is what demands the cell and the pad [C206] |
| E52UC | `on error begin; put skip list('oops'); goto retry; end;` + ADJACENT `retry:` | 256 B sha `16b09236bf30…` | `0046`=70 / `0008` | @000D, same prefix; SP-save @0006 | inline put-skip-list chain @0017 (`11 52 02`/`01 r(str)`/`?SYSPR`/`3E 01`/`?SKPOP`/`21 r(data 0)`/`3E 04`/`?SLCTS`/`?PNCOP`/`?QIOOP`), `C3` @0033 with `CHAIN-ADDR`, **NO `C9`** | the LOAN2/ANNUITY mirror in isolation: an ADJACENT label MERGES the jump-over and pad targets into ONE address — `SET-LC 001B / RELOC code 0x33`, `SET-LC 0015 / RELOC code 0x36`, pad @0036 [C208] |
| E52UD | `on error begin; x = 1; end;` (plain RETURNING block) | 128 B sha `cfeed90ca4c5…` | `0020`=32 / `0002` | @0006, same prefix | body `21 01 00 / 22 r(x) / C9` @0010–0016 | the shape NO pre-existing golden carries; **H3 as pre-registered**: a returning handler emits `C9`, and — with it — **NO SP-cell, NO pad, NO `DAD SP`** (DATA is `0002` in UA/UD/UE) [H4] |
| E52UE | `on error(2) x = 1;` + `on error(0) x = 2;` | 256 B sha `23b01969fb1a…` | `002B`=43 / `0002` | units @0006 `21 02 00` and @0017 `21 00 00`, each `AF / CD ?ONCOP / C3 slot` | `21 01 00 / 22 r(x) / C9` @0010–0016; `21 02 00 / 22 r(x)` + `C9` @0021–0027 | the ARGUMENT IS the LXI operand VERBATIM, and it never reaches `A`: `error(2)` = `21 02 00`, `error(0)` = `21 00 00` = the bare spelling; DR accepts literals beyond the corpus's 0 and 1 [H2] |
| E52UF | `on endfile(f) stop;` + `on endfile(g) x = 1;` | 384 B sha `4caeceedd52a…` | `002F`=47 / `0002`, COMMON `F`/`G` each `0023` | file units @0006 and @0014 — `21 r(common X 0)` **with `RELOC common`** + `3E 05` + `CD ?ONCOP` + `C3 slot` (11 B, [C109]/[C364]) | first: inline `CD ?STOPX` @0011 and **NO `C9`** (slot @000F → 0x14, straight into the next unit); second: `21 01 00 / 22 r(x)` **with `C9`** @0025 | **THE BODY CONTRAST INSIDE ONE OBJECT** — the two ON units share the condition FAMILY and differ only in the handler's last statement, which pins termination as a property of the BODY, not of the ON unit [H3] |

## 3. Hypothesis verdicts (pre-registered in PLAN §P3-8 §3, kept verbatim)

- **H1** ERROR registers as ABSOLUTE `LXI H,<arg 16-bit LE>` + `XRA A` (`AF`) + `CALL ?ONCOP` + `C3
  <over>` = 10 bytes, with NO `LINK-DEF-COMMON`/`LINK-SEL-COMMON` record in a file-less object and NO
  relocation ON THE ARGUMENT OPERAND — **CONFIRMED** (UA/UB/UC/UD/UE; `AF` is ONE byte where the file
  route spends `MVI A,nn` on two). NO competitor falsifier fired: no object had an 11-byte ERROR
  registration, an `MVI` condition byte or a relocated LXI operand.
- **PRECISION NOTE on [C366]'s wording (mine, this hop, recorded not fitted).** The claim says the
  file-less objects carry "NO relocation of any kind in its registration". Read strictly that is too
  broad: the two things MEASURED and intended are (i) NO COMMON group and NO `SEL-COMMON`/`RELOC
  common` record anywhere in the object, and (ii) NO relocation record attaching to the LXI ARGUMENT
  operand (it is an absolute 16-bit constant). The registration region does legitimately contain two
  other link patches — the `?ONCOP` `CHAIN-EXT` and the `RELOC code` that fills the jump-over slot with
  the continuation address — exactly as the file-scoped prefix does. The claim text is kept as committed
  (`17c9963`); a future metadata-only ledger touch may tighten the phrase. Nothing about the BYTES
  changes: the encoding law H1 states is what the goldens measure.
- **H2** the conditional-name ARGUMENT is that LXI operand verbatim — **CONFIRMED** (UE `error(2)` =
  `21 02 00`, `error(0)` = `21 00 00`; the corpus's `error(1)` = `21 01 00` at COPYLPT/EXPR1/EXPR2).
- **H3 the tail is BODY-DEPENDENT — CONFIRMED, and PROVEN INSIDE ONE OBJECT** by UF: `on endfile(f)
  stop;` = inline `CD ?STOPX` and NO `C9`, while `on endfile(g) x = 1;` in the same program carries
  `C9` @0025; UA/UD (returning bodies) carry `C9`, UC (tail goto) carries `C3` and no `C9`. My
  `codegen.ml` emitted the `C9` UNCONDITIONALLY after every non-goto handler on [C109]'s authority —
  the hop-2 `my-gap` is CORRECTED on UF's measured bytes, not on inference.
- **H4** a handler whose body RETURNS demands NEITHER the block SP-cell NOR the pad — **CONFIRMED**
  (UA/UD/UE DATA `0002`, no `DAD SP`); UB/UC (goto handlers) carry the save + cell + pad.
- **H5** the jump-over operand is the fall-through CONTINUATION and an adjacent label MERGES the two
  patch targets while a remote label keeps them INDEPENDENT — **CONFIRMED** (UB 0015→0x1A vs
  0018→0x20; UC merged at 0x36).
- **H6** DR ACCEPTS all six, including the direct `on error goto lbl;` spelling — **CONFIRMED**
  (6 ok/6, `NO ERROR(S)` in both passes). Every pre-registered prediction hit; this round's own
  falsifiers NEVER triggered.

Pre-campaign falsifications kept VERBATIM as written history (hops 1–2, in `LEARNINGS.md` and PLAN
§P3-8): hop 1's reading that ANNUITY's pad/jump-over geometry was NON-adjacent was FALSIFIED — a
column-shifted hex artifact of the first dump tool (`dis80.py`'s reldump-TEXT mode prints reloc
operands as `.` and produced FALSE gaps; the bitstream decoder `build/e52p8/ondump2.py` is the honest
tool), ANNUITY is the ordinary adjacent case; hop 1's fixed slot-7 walk-back was also FALSIFIED.

## 4. The arm, and my first-draft falsifier

Arm `a7ab5a4` (`ocaml/lib/codegen.ml` ONLY): a SECOND prefix encoder `on_error_reg_prefix` beside
`on_reg_prefix` (the file encoder is NOT mutated) emitting ABSOLUTE `LXI H,<arg LE>` / `XRA A` /
`CALL ?ONCOP` / `C3 <slot>`; the ERROR arm admits bare `error` or ONE integer literal 0..65535 verbatim
and ONLY the four measured handler shapes (statement + `C9`; returning `BEGIN…END` block, lowered
per-statement, + `C9`; DIRECT `goto`; block TAIL-goto, no `C9` per [C364]); every other argument or
handler shape refuses BY NAME with `[TBD]`; the body-dependent tail was also corrected on the ENDFILE
route (bare `stop` handler = registration + `C3` slot + inline `CD ?STOPX`, NO `C9`, emitted DIRECTLY so
`stop_seen`/`after_forever` never leak into the caller's epilogue), with UNDEFINEDFILE+STOP and nested
STOP now refusing BY NAME because NOTHING measures them. Helpers `has_goto`/`block_tail_goto`/
`handler_body` hoisted to the `Son` arm top plus a NEW `has_stop` (one rule, two routes [C202]).

**FALSIFIED IN-HOUSE (my own first draft, kept verbatim):** the first STOP branch armed the measured
no-`C9` tail but OMITTED the shared registration `+C3+triple` sequence, so E52UF `cmp` MISSED at octet
150 — 5/6 before the fix. LESSON (recorded in `LEARNINGS.md`): registration is condition- and
body-blind [C120]/[C202]; only the handler TAIL partitions, so EVERY branch of a restructured match must
carry the shared prefix. After the fix: `dune build` rc=0 DIRECT, binary `9ecea27aa4f2d80f49ad…`
(supersedes draft `f9abf6b6d07f1d3db500…`), per-File codegen warning histogram **68 == BASELINE**
(kinds 27/9/11/8/26/39/57/32 — no drift from the arm; the per-File count of a FULL clean-build log is
the honest method, totals of partial logs are not), cmp UA..UF whole-file **6/6 rc=0**, sweep
`build/e52p8-reg/sweep-arm.log` 124 specimens **FAILS: 0** + 21 expected named refusals, and the
boundary-marker harness `build/e52p8-reg/markers.py` (which replicates the gate's `REJECTS` loop)
E46K4/K15/N21/E52PF/PU/PV/RE + SE/SF/SG all rc=2 with **MARKER_FAILS: 0**.

**PROCEDURE (new, accepted):** that harness first FALSIFIED ITS OWN METHOD — writing LF-only sources
made E46N21 report `line 6` and MISS its registered `(line 12)` marker. A marker harness MUST
materialise the source exactly as `run_negatives` does, `src.replace("\n","\r\n").encode() + b"\x1a"`,
because the refusal's reported LINE NUMBER depends on it.

## 5. LOAN2 rerun UNMODIFIED + registration

`artefacts/LOAN2.PLI` sha `7be23ba390926c20…` (UNCHANGED, last touched Phase 0), invoked POSITIONALLY
at `1dc53f4` on binary `9ecea27aa4f2d80f49ad…`: **rc=2 DIRECT, NO `.REL` produced** (stdout 0 bytes;
stderr `build/e52p8-reg/LOAN2-stderr.log`), first diagnostic VERBATIM

`codegen: condition form not in E2E-3b subset [TBD]: (| (< dl 0) (> dl 2))`

— LOAN2 **ADVANCED past ON ERROR line 58**, the subround's target blocker CLOSED; the new first
blocker is the OR-of-relations condition at LOAN2:91 `if dl < 0 | dl > 2 then` (`dl` is FIXED BINARY),
raised at `codegen.ml:9154`, whose message prints the IR and carries NO line number. It is RECORDED,
**NOT fixed** and NOTHING was hardcoded to LOAN2 (PLAN §6 "record whatever actually happens, never fit"
— no candidate was predicted for this blocker, and none was fitted after the fact). Census advances
recorded VERBATIM with it: EXPR1 → `GET form not in E2E-3e subset [TBD] (line 21)`, EXPR2 → `FLOAT
expression shape builtin is unsampled [TBD] (line 35)`.

Registration: SPECIMENS +6 with the measured-law comment `244f6e1`; sanctioned `--update-inventory`
diff EXACTLY **+6**, 1243 → **1249**, ZERO removals, refusals unchanged 186; census OWN write path
(`corpus_census.py --check`) rc=0 with counts UNCHANGED **15/0/26/0**; FULL gate REAL rc=0 DIRECT
`build/gate-e52p8-reg.log` — **1249/0 byte-exact, 186/186 negatives, 9/9 divergence, coverage 140 rows
0/0, census 15/0/26/0, prose 5**. Claim **C366** `17c9963` from MEASURED BYTES ONLY (the six goldens +
fresh reldumps) committed **BEFORE** the COVERAGE rewrite `0cf0688`: row `COND.ON_ERROR` REFUSED/NONE →
**SUPPORTED / EXACT:6**, id KEPT as the stable key, the pre-campaign contract sentence ("ON ERROR is
accepted by DR and not implemented here; the condition-table operand and the handler-chain entry for a
non-ENDFILE condition are unprobed") preserved VERBATIM as HISTORICAL, perimeter spelled as MY
refusals BY NAME, corpus column naming the ON ERROR users AND the three census-verified advances;
`coverage_check.py` rc=0 **140 rows 0/0** (SUPPORTED 90) with stats regenerated by their OWN write
path; `file_prose_check.py` rc=0. Ledger ENDS **C366**.

## 6. What P3-8 does NOT say (byte tier only)

- **Byte tier only**: NO `golden/e52p8` object was linked or run under cpmsim; nothing here asserts any
  ERROR-RECOVERY behaviour — whether `?ONCOP`/`?RECOV` actually establish or restore a handler at
  runtime is UNMEASURED by this claim, and no `spec/RUNTIME.txt` row exists.
- The arm covers `ON ERROR` with NO argument or ONE integer literal 0..65535, lowered ONLY for the four
  handler shapes in §2. Every unmeasured shape is MY refusal BY NAME with `[TBD]` and is NOT a DR rule:
  expression/variable/string arguments, out-of-range or multiple arguments, `ON ERROR` with a `STOP`,
  `RETURN`, `NULL` or `DCL` handler, a nested `STOP` in a block handler, a `STOP`-bodied handler on the
  UNDEFINEDFILE route (only ENDFILE carries UF's bytes), and `REVERT ERROR` (NO object at all; only
  `REVERT UNDEFINEDFILE` is measured, and E52SE stays an UNARMED `my-gap`).
- Corpus users (LOAN2, ANNUITY, COPYLPT, EXPR1, EXPR2) are users of the CONSTRUCT, not parity claims; the
  five pre-existing witnesses AGREE with the new six but no whole-program byte-exactness is claimed for
  them — LOAN2 still refuses, now at line 91.
- GOLDENS ARE EVIDENCE, NEVER RE-DERIVED; the ENDFILE/UNDEFINEDFILE regressions (E52SA..SD, [C109],
  [C364]) stayed byte-exact through the tail correction; SF/SG stay `dr-refuses`; the operator's
  `handoff.config.json` was NEVER staged; no push.
- This SUPERSEDES the final sentence of §P3-7 above ("it still refuses at ON ERROR line 58"), kept
  VERBATIM as the record of that hop: at HEAD after P3-8 LOAN2's first blocker is the §5 condition form.

## 7. DEFECT REPAIRED BY THE SUCCESSOR (2026-11-05, docs hop) — [C366] COVERAGE commit `0cf0688` CLOBBERED THE LEDGER

**ACCEPTED (measured, this hop).** §5 as written above was TRUE OF THE INTENT but NOT of the tree: commit
`0cf0688` replaced `spec/COVERAGE.tsv` with a **72-line stale snapshot** (141 → 72 lines, 133 deletions /
69 insertions) whose header was the E2E-36-era banner ("gate 933 byte-exact / 124 negatives", git 4247a61)
and whose `COND.ON_ERROR` row was still `REFUSED / NONE` with `probes=N80_ON_HANDLER_BEGIN`,
`corpus=UPDATE,OPTIMIST`. The COVERAGE rewrite therefore NEVER LANDED, although the same commit's
`spec/census/coverage-stats.json` carries the correct POST-rewrite numbers (rows 140, SUPPORTED 90,
REFUSED 21, no_parity 28, MEASURED 114, SINGLE_SAMPLE 18) — proving the intended rewrite was computed
against the good file and the wrong content was written afterwards. The full gate rc=0 1249/0 was run
BEFORE that commit (`244f6e1`), so nothing panel-verified had yet caught it.
**ROOT CAUSE (accepted):** `tools/coverage_gen.py` is an OBSOLETE one-shot generator that carries a
hard-coded ~1970s-era row list and ENDS with `open('spec/COVERAGE.tsv.new','w')` +
`os.replace(... , 'spec/COVERAGE.tsv')`. Running it — which this round's brief called "the stats' OWN
write path" — silently overwrites the hand-authored ledger. The stats' actual own write path is
`tools/coverage_check.py`, which writes only `spec/census/coverage-stats.json`. Nothing else calls
`coverage_gen.py` (grepped).
**FALSIFIED:** the hop-3 note "coverage_gen + prose rc=0" as evidence of a landed coverage rewrite;
and the earlier assumption in this file that the row rewrite was in the tree.
**REPAIR (no oracle call, no `ocaml/` byte, goldens untouched):** restored `spec/COVERAGE.tsv` from
`git show 17c9963:spec/COVERAGE.tsv` (the last good 140-row state, one commit BEFORE the clobber), then
re-applied the COND.ON_ERROR rewrite the commit message describes — id KEPT, the pre-campaign contract
sentence preserved VERBATIM as HISTORICAL, `SUPPORTED / EXACT:6`, probes E52UA..UF, corpus the five
ON-ERROR census users (ANNUITY, COPYLPT, EXPR1, EXPR2, LOAN2 — `UPDATE`/`OPTIMIST` were FALSIFIED:
`grep -il "on error" artefacts/*.PLI` names exactly those five), boundary = my refusals BY NAME plus the
byte-tier-only NOT-say plus the three census-verified advances VERBATIM, confidence MEASURED, provenance
[C366] + [C109] [C364] [C206] [C208] [C120] [C202]. NEW sub-falsification found while re-authoring: the
row's old "the BEGIN-body handler is a second refusal" two-part-gap claim is FALSIFIED by E52UD (a plain
returning `BEGIN…END` handler is lowered), while `N80_ON_HANDLER_BEGIN` still refuses on a
`procedure without name` diagnosis of its BIT(1) STATIC INITIAL body — an unrelated parser my-gap, not
the ON unit; both are recorded in the row's boundary cell. Verification rc DIRECT: `coverage_check.py`
rc=0 → **140 rows, 0 errors, 0 warnings, SUPPORTED 90** — byte-for-byte the numbers of
`build/e52p8-reg/coverage-after-c366.log` and of the committed `coverage-stats.json` (which therefore did
NOT move); `file_prose_check.py` rc=0. Evidence `build/e52p8-reg/coverage-repair.log`,
`build/e52p8-reg/prose-repair.log`.
**PROPOSED (never authorization, never done here):** delete or neuter `tools/coverage_gen.py` (or gate it
behind an explicit `--i-know-this-is-the-1970-snapshot` flag plus a row-count-shrink abort), and add a
gate assertion that `COVERAGE.tsv` row count never decreases without a labelled correction commit.

## P3-9 — OR (`|`) conditions: the value-level truth-byte fold, the NODE-LOCAL class-driven order, the VAR-FIRST DEC fold pair and the standalone `< 0` leaf (campaign e52p9) — CLOSED (2026-11-06, hop 7)

Pre-registered `4495604` (PLAN §P3-9 H1–H10 + probes E52VA..VK, committed BEFORE any `ocaml/`
byte; the class decoded FIRST from the pre-existing ANNUITY:46 and LOAN2:91/113/120 original
goldens with ZERO oracle calls in hops 1–2); oracle campaign **11 ok / 11, ZERO dr-refuses**;
goldens committed VERBATIM `9bb3f99`; arm `d918dde` (`ocaml/lib/codegen.ml` ONLY); claim **C367**
`eaa5ef3` written from MEASURED BYTES ONLY and committed BEFORE any `spec/COVERAGE.tsv` touch;
row `COND.OR` + explicit `spec/COVERAGE-IDS.txt` line `7da60b5` (NEVER `coverage_gen.py`). All rc
captured DIRECTLY (never through a trailing pipeline); goldens NEVER re-derived; `pli80c` invoked
POSITIONALLY into FRESH paths; the operator's `handoff.config.json` NEVER staged; no push.

## 1. Campaign (oracle, ONE grouped batch)

`PLI_SRC=probes timeout 900 python3 oracle/batch.py E52VA E52VB E52VC E52VD E52VE E52VF E52VG
E52VH E52VI E52VJ E52VK --tag e52p9 --switches '$L$D'` rc=0 → **11 ok / 11**; every `.PRN` read;
**ZERO dr-refuses**, so NO refusal row joined the NEGATIVES panel and the negative count stayed
186. Goldens `golden/e52p9/` committed VERBATIM. **Probe-tail DEVIATION, recorded honestly and
kept in PLAN §4:** the brief's `put edit(x)(a);` tail has NO DR-accepted golden anywhere (an `A`
edit on an arithmetic item is UNMEASURED), and a refusal on it would have killed all eleven
goldens; the probes carry NO put — the continuation is `x = 2;` (E52UA-proven). Byte predictions
covered the CONDITION regions, which are the science; whole-file cmp at arm time verified the rest.

## 2. Measured table (whole-file cmp rc=0 on the committed-tree rebuild `11c6283e75b60fe3…`, re-verified FIRST-HAND into fresh `build/e52p9-hop7/out/`, `build/e52p9-arm/parity.txt`)

| probe | condition | object | CODE/DATA | measured fact |
|---|---|---|---|---|
| E52VA | `if dl < 0 then x = 1;` | 128 B | `001C` / `0004` | standalone TEST leaf = `3A <r data dl+1> / B7 ORA A / F2 <slot>` — the relocation lands **EXACTLY ONE PAST the declared cell**; the `B7` normalization appears ONLY in the standalone test, never inside a fold |
| E52VB | `dl < 0 \| dl > 2` | 128 B | `0026` / `0004` | the LOAN2:91 region verbatim: 17-byte fold @0006 `2A r0 / 2B 2B 2B / 7C / 2F / F5 / 3A r1 / C1 / B0 / F2 <slot>` — ladder (RIGHT in source) produced FIRST, the `< 0` LDA computed **LAST after the push**, ONE terminal branch, no second conditional jump anywhere |
| E52VC | `dl > 2 \| dl < 0` (source-swapped) | 128 B | `0026` / `0004` | **BYTE-IDENTICAL to E52VB** — emission order is a property of the operand CLASSES, not of the spelling order |
| E52VD | `a < 0 \| b > 2` (separate vars) | 128 B | `0026` / `0006` | same 17-byte fold with INDEPENDENT relocs: ladder reads `r(data b)`, the `< 0` operand reads `r(data a + 1)` — one past the declared cell again |
| E52VE | `dl = 0 \| dl > 2` | 256 B | `002C` / `0004` | head is the LADDER `2A` (NOT the zero-test `21`): `2A r0 / 2B×3 / 7C 2F / 21 r0 / F5 / 7E 23 B6 D6 01 9F / C1 B0 / F2` — rule-2 same-variable swap; the `21` head hoists ABOVE the `F5`, the zero-test tail materializes after the push |
| E52VF | `dl = 0 \| dl > 2 \| m > 1 \| dl < 0` | 256 B | `003C` / `0006` | FOUR operands = THREE pairwise `C1/B0` folds and **ONE** `F2` (slot→0x33): node1 same-var swap (ladder first), node2 `m > 1` `2A r2 / 2B 2B / F5 / 7C 2F / C1 B0` did NOT move ahead of node1's zero-test — the class rules are **NODE-LOCAL**, not a global priority; node3 `F5 / 3A r1 / C1 B0 / F2` |
| E52VG | `pv = 0 \| pmt = 0` (dec(9,2)/dec(7,2)) | 256 B | `0047` / `0014` | DEC fold pair **VAR-FIRST**: node1 relocs `21 → data 0x9` (pv) THEN `21 → data 0x0` (pooled zero); node2 `21 r(0xE)` (pmt) hoisted above the `F5` THEN `21 r(0x5)` (zero7). DATA `0014` read from the `LINK-DEF-DATA-SIZE` RECORD |
| E52VH | `dl < 0 \| dl > 2` with `ELSE` | 256 B | `002F` / `0004` | fold bytes of VB verbatim through `C1 B0`; `F2` slot patches to the ELSE body (code 0x20) and the `C3` over-else skip at 001D patches to the statement AFTER the else (0x26) — **two INDEPENDENT patch targets**, mirrors [C312] |
| E52VI | `p = 0 \| dl > 1` then `q = 0 \| p = 0` (dec(10,2)/dec(9,2)) | 384 B | `0076` / `001A` | stmt1 keeps SOURCE order (rule 3); both DEC pairs VAR-FIRST (`0xB`(p) before `0x0`(zero10); `0x11`(q) before `0x6`(zero9)); stmt2's SECOND operand reuses the SAME dec(10,2) zero cell (`0xB`/`0x0` again) — [C155] content-deduplicated pooling, ONE cell per (precision,scale), no duplicate |
| E52VJ | `dl > 0 \| dl < 0` | 128 B | `0025` / `0004` | `> 0` = the memory-compare materialiser `21 r0 / AF BE 23 9E` verbatim as in AND ([C128]/[C105]), `21` hoisted above the `F5`, `3A` LAST — head `21` vs RB's `3A` discriminates, and it is `21` |
| E52VK | three boundaries (precedence, group, value position) | 256 B | `0080` / `0009` | stmt1 `dl < 0 \| m = fm & dl > 2` opens with the FULL `m = fm` EqVV materialiser before any push (`2A r2 / E5 / 2A r4 / D1 / CD ?IS22N / 7C B5 / D6 01 / 9F`); stmt2 `(or) & m = fm` emits the OR fold FIRST, then the pre-existing `C1 A0` AND sandwich [C105], then ONE `F2`; stmt3 `b = (dl < 0 \| dl > 2);` (BIT(1) VALUE position) ends in a **BARE `32 r(bitcell)`** with the fold's `C1 B0` immediately before it and NO `D6 01 / 9F` normalization in the store path |

## 3. Hypothesis verdicts (pre-registered in PLAN §P3-9 §3/§4; every MISS kept verbatim)

- **H1 (the fold) CONFIRMED.** Value-level, single-branched: per-operand truth bytes (bit 7 IS
  truth), `F5 PUSH PSW` between operands, `C1 POP B / B0 ORA B`, ONE terminal `F2 JP` per OR node;
  chains keep ONE branch (VF's four operands). No falsifier fired: no branch-per-operand, no
  condition-cell short-circuit, no second `F2`.
- **H2 (fold ORDER) adjudicated — BOTH pre-registered candidates FALSIFIED; the surviving law is
  CLASS-DRIVEN AND NODE-LOCAL (rules 1–3 of [C367]).** **RB (right-first fold) FALSIFIED by
  E52VC**: right-first predicts a `3A`-headed node for `dl > 2 | dl < 0`; the golden heads with
  `2A` and is byte-identical to E52VB. **SN/LB (strict source order, SN's `<0`-last proviso
  included) FALSIFIED by E52VE and by E52VF node1**: both begin with the LADDER head `2A`, never
  with the zero-test head `21`. Rule 1 (`< 0` computed LAST in its node) is confirmed by VB/VC/VD/
  VJ/VF-node3/LOAN2:91; rule 2 (same-variable FIXBIN `= 0` immediately followed by a `> k` ladder
  → ladder pushed first) by VE and VF node1; rule 3 (everything else source order) by VI stmt1,
  VG and LOAN2:113. VF additionally proves the rules are **NODE-LOCAL**: `m > 1` did not jump
  ahead of node1's zero-test.
- **H3 (standalone `< 0`, VA) CONFIRMED — PRIMARY prediction HIT**: `3A <r data dl_hi> / B7 / F2
  <slot>`; the bias-0-ladder competitor, any refusal (dr-refuses), `E4 JM` polarity, a `D6 01/9F`
  materialiser and a `DB nn` mystery all stayed unfired. The reloc lands EXACTLY one past the
  declared cell (obligation O-3, H4's proviso).
- **H4 (separate cells, VD) CONFIRMED**: predicted fold shape verbatim, independent relocs,
  `< 0` operand reads `r(data a + 1)`, DATA `0006` as predicted.
- **H5 (FIXBIN `= 0` as an OR operand, VE) SPLIT**: the [C310] zero-test materialiser bytes and the
  ladder hoist above the `F5` HIT verbatim; the SN *order* clause (head `21`) was FALSIFIED —
  measured head is the ladder `2A` (rule 2).
- **H6 (4-operand chain, VF) CONFIRMED on the fold law** (3×(`F5 … C1 B0`), ONE `F2`) with the §3
  order correction; the per-operand SN emission sequence MISSED.
- **H7 (DEC push order) — PAR FALSIFIED, LITERAL-FIRST FALSIFIED, VAR-FIRST IS THE MEASURED LAW.**
  PAR (width parity) died at hop 3 on VI (odd 9 in stmt2 measured VAR-first) and again on VG. The
  hop-4/hop-5 LITERAL-FIRST reading died at the arm: VG relocs `0x9`(pv)→`0x0`(zero), VI
  `0xB`(p)→`0x0`, `0x11`(q)→`0x6`, and LOAN2:113 measures `21 r(P@02CA)` before `21 r(zero@01E6)`
  — all VAR-FIRST. The reading had ASSUMED the decimal pool sits ABOVE the automatics; this tree's
  layout (pool BELOW, proven across the 1249 registered goldens) makes the two readings produce
  DIFFERENT relocation numbers, and the goldens say var-first. The hop-3/4 "ADD survives" sentence
  rested on the same misread and is SUPERSEDED: `ANNUITY`:46 pushes its zero literal first because
  in THAT object the literal cell does sit above the variables; DR's internal layout choice is not
  observable from zero-content cells, so [C367] states the pair order PER OBJECT AS MEASURED and
  does not re-litigate the [C155]-family allocator question. **[C155] dedup CONFIRMED**: the
  dec(10,2) zero cell appears ONCE in VI and is reused by both statements; the falsifier (two
  identical cells) did not fire.
- **H8 (OR with ELSE, VH) CONFIRMED in law**: two INDEPENDENT patch targets (`F2`→else,
  `C3`→after-else), no merged slot; the predicted absolute addresses (001F/0024) shifted to
  0x20/0x26 with the §4 size miss below — geometry law HIT, byte totals MISSED.
- **H9 (`dl > 0` inside an OR, VJ) CONFIRMED**: `21 r0 / AF BE 23 9E`, `21` hoisted above the `F5`,
  `3A` last; RB's `3A`-first competitor did not fire.
- **H10 (grouping/value position, VK)**: all THREE shapes DR-ACCEPTED (campaign 11/11), recorded
  VERBATIM without byte prediction as pre-registered; ALL THREE were then armed byte-exact —
  precedence sandwich, OR-fold-first inside AND, and the value-position fold ending in a BARE `32`.

## 4. Falsifiers adjudicated VERBATIM (pre-registration vs measurement)

1. **PLAN §4 VG byte order predicted LITERAL-FIRST** (`21 <r zero9>` before `21 <r pv>`) —
   measured **VAR-FIRST** (relocs `0x9` then `0x0`); VI likewise.
2. **RB (right-operand-first fold)** — falsified by the byte-IDENTICAL `E52VB == E52VC` pair.
3. **SN/LB (strict source order)** — falsified by the VE and VF-node1 LADDER heads `2A`.
4. **PAR (width-parity push order)** — falsified by VI at hop 3; the VAR-FIRST measurement keeps it
   dead.
5. **EVERY PLAN §4 whole-CODE-SIZE prediction was SHORT** — the predictions omitted the `x = 2;`
   continuation statement and its slot geometry: VA `0014`→`001C`, VB/VC/VD `001F`→`0026`, VE
   `0024`→`002C`, VF `0034`→`003C`, VG `0038`→`0047`, VH `002C`→`002F`, VJ `001E`→`0025` (VI and
   VK carried no total prediction; their H7/H10 SHAPE predictions HIT). The fold-REGION byte
   predictions with an agreed shape HIT (VB = LOAN2:91 verbatim; VH two independent targets; VJ
   head `21`; VF 3 folds + ONE `F2`).
6. **The hop-4/hop-5 LITERAL-FIRST DEC law** — falsified in the arm session: the first attempt
   armed literal-first and the **VG and VI whole-file cmps FAILED against the goldens**; the
   re-derivation from the golden reldumps established VAR-FIRST (pool BELOW the automatics on this
   tree), the refit restored **11/11 cmp rc=0** and `build/e52p9-arm/parity.txt` records
   "DEC VAR-FIRST refit (literal-first FALSIFIED)" in its header. The residual ADD-vs-literal-first
   "ambiguity" of the arm plan is DISSOLVED — it was a layout MISREAD, not an evidence gap. The
   AND route (`dec_eq_bool_parts`) was ALWAYS var-first; the fold now matches it, and no And byte
   was changed.
7. **hop-4's "VI DATA 001B"** — falsified: the `LINK-DEF-DATA-SIZE` RECORD says `001A`; the
   compiler console's `data=` line is a COSMETIC display that differs from the record and is never
   cited as authority (it is what produced the 001B misreading).

## 5. Arm, verification, registration

Arm `d918dde` (`ocaml/lib/codegen.ml` ONLY, applied through the anchor-asserting idempotent
`build/e52p9-arm/arm-splice.py` after THREE script corrections — `bit_cond_mat` blank-line offset;
E2/E3 descending-position splice order; an extra `end` plus `expr_kind`-vs-`expr` guard binding —
and a `_sc` unused-subpattern fix restoring the histogram): `or_cls`/`or_classify`/`or_head`/
`or_tail`/`collect_or` + `lower_or` in the let-rec group before `lower_bool`; the Or fold arm
BESIDE the And fold; leaf arms before the catch-all; the TEST Or arm beside And; the standalone
`< 0` TEST arm (`3A r(v+1) / B7 / F2`, plain Vint auto only, the pre-existing `[TBD]` refusal
surviving for every other operand); the `bit_cond_mat` Or arm with `~allow_dec:false`; DEC fold
pairs VAR-FIRST through `dec_pool`; **no And byte touched**. Warning histogram from a FULL rebuild
in a fresh `--build-dir`: codegen `68` / total `124` == baseline. The hop-6 recorded hash
`c621ea8c6d05ac…` proved NOT reproducible from the committed tree (build-dir artifact); the honest
authority is the golden CMP — the committed source rebuilds deterministically to
`11c6283e75b60fe3…` and 11/11 whole-file cmps rc=0 were re-verified from the committed tree into
FRESH paths twice (hop-6 `build/e52p9-reg/parity-recheck.txt`, hop-7 `build/e52p9-hop7/`). Sweep
FAILS: 0; every named negative fires its VERBATIM refusal; markers harness (CRLF + bare `^Z`)
10/10 MARKER_FAILS 0 rc=0. **LOAN2 POSITIONAL rc=2, NO .REL**, first blocker VERBATIM
`codegen: statement kind not in supported subset [TBD] (line 92)` = the `signal error` statement —
**PREDICTED = MEASURED**, recorded, NEVER fixed (its DR lowering `21 00 00 / AF / CD ?SIGOP` is an
original-golden byproduct, UNARMED, out of scope; a LATER subround). EXPR1 (`GET form … (line 21)`)
and EXPR2 (`FLOAT expression shape builtin … (line 35)`) UNCHANGED; the census (`b080894`, OWN
prescribed path) records the LOAN2 message MOVED with counts UNCHANGED 15/0/26/0. Registration:
SPECIMENS +11 + `--update-inventory` → 1249→**1260 EXACTLY** (+11 rows, every added line inspected),
refusals 186 unchanged (`bdbc28a`); **C367 `eaa5ef3` from MEASURED BYTES ONLY committed BEFORE ANY
COVERAGE touch**; `COND.OR` row SUPPORTED / EXACT:11 + EXPLICIT `spec/COVERAGE-IDS.txt` line
(`7da60b5`, NEVER `coverage_gen.py`; column count taken from the FIRST NON-COMMENT row (15) per the
hop-7 law, diff verified ≈ one TSV line + one IDS line BY CONTENT); `coverage_check.py` rc=0 **141
rows, 0/0, SUPPORTED 91** with stats refreshed by their OWN write path; FULL gate rc=0 DIRECT
`build/gate-e52p9-reg.log` — **1260/0 byte-exact, 186/186 negatives, 9/9 divergence, coverage 141
rows 0/0, census 15/0/26/0, prose 5**.

## 6. What P3-9 does NOT say (byte tier only)

- **Byte tier only**: no `golden/e52p9` object was linked or run under cpmsim; nothing here asserts
  what DR *decides* at runtime for any condition — only that these bytes are what the compiler
  emits and this compiler now emits them identically. No `spec/RUNTIME.txt` row comes from this
  subround. Byte parity is not a semantics claim.
- **O-1 panel status**: the LOAN2:91/113/120 and ANNUITY:46 fold citations are an
  ORIGINAL-GOLDEN DECODE (`build/e52p9-arm/loan2-decode.txt`, re-derived with the fixed
  `tools/reldump.py`/`dis80.py` bitstream walk), **PANEL-UNVERIFIED for LOAN2** — it does not
  compile past the fold, so no cmp can adjudicate those citations. The BINDING panel authority is
  the eleven `E52VA..VK` whole-file cmp rc=0.
- **The BY-NAME perimeter is MY gap, never a DR rule**: a `< 0` leaf FIRST in a chain of three or
  more operands, a rule-2 swap across DIFFERENT variables, a fold ladder with k ≥ 3, a DEC operand
  in the BIT(1) value position, and every other operand class (based/external/array members, `<>`,
  string or call operands, nested `|:` forms) take the existing `condition form not in E2E-3b
  subset [TBD]` refusal; whether DR accepts each refused shape is UNMEASURED.
- The AND route and its [C105] `C1 A0` sandwich are UNCHANGED; the O-2 pool-parity finding stands
  (no `prescan_cond` edit was needed — the existing general descent already demands the fold's zero
  cells); `signal error`/`?SIGOP` stays UNARMED and out of scope (PROPOSED P3-10, never
  authorization).
- Corpus users (LOAN2, ANNUITY) are users of the CONSTRUCT, not parity claims; GOLDENS ARE
  EVIDENCE, NEVER RE-DERIVED; the operator's `handoff.config.json` was NEVER staged; no push.
