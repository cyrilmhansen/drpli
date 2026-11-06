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

# E2E-52/P3-10 RESULTS — SIGNAL condition lowering + the `?SIGOP` ABI + the lost-argument
frontend repair (campaign e52p10) — CLOSED (2026-11-07, hop 3)

Pre-registered `c6c4460` (PLAN §P3-10 H-A..H-X + probes E52WA..WL, committed BEFORE any oracle
call and any `ocaml/` byte, after a Phase-A audit with ZERO oracle that pinned SIX SIGNAL sites
in EXACTLY FOUR original objects — `build/e52p10/` raw records, PLAN §2 table); oracle campaign
**11 ok / 12**; the one `dr-refuses` (E52WL) kept VERBATIM with NO invented golden; goldens
committed VERBATIM `d46b6c2` BEFORE any emitter byte; frontend repair + arm `d84665c`;
AST-preservation proto test `91060ea`; registration `21d4db6` (inventory 1260→**1269**, refusals
186→**187**); census OWN path `0198fe5`; claim **C368** `7153716` written from MEASURED BYTES
ONLY and committed BEFORE any `spec/COVERAGE.tsv` touch; row `COND.SIGNAL` + explicit
`spec/COVERAGE-IDS.txt` line `65b005e` (NEVER `coverage_gen.py`). All rc captured DIRECTLY (never
through a trailing pipeline); goldens NEVER re-derived; `pli80c` invoked POSITIONALLY into FRESH
paths; the operator's `handoff.config.json` NEVER staged; no push.

## 1. Campaign (oracle, ONE grouped batch)

`PLI_SRC=probes timeout 900 python3 oracle/batch.py E52WA E52WB E52WC E52WD E52WE E52WF E52WG
E52WH E52WI E52WJ E52WK E52WL --tag e52p10 --switches '$L$D'` rc=0 → **11 ok / 12**; every `.PRN`
read: the eleven accepted probes show `NO ERROR(S)` in BOTH passes; **E52WL is a genuine
`dr-refuses`** — PASS 1 clean (`NO ERROR(S) IN PASS 1`), then PASS 2 at line 12: `SYNTAX ?`,
`1 ERROR(S) IN PASS 2`, NO .REL. `E52WL.PRN` preserved VERBATIM at `golden/e52p10/E52WL/`; the
probe joins the NEGATIVES panel (refusals 186→187). Goldens `golden/e52p10/` committed VERBATIM.

## 2. Measured table (whole-file cmp rc=0 on binary sha256 `a4c0e235ed4bb81fe284…`; every region
re-read FIRST-HAND from `build/e52p10/E52W*-reldump.txt` at registration AND again before C368)

| Probe | Shape | Size | CODE | DATA | SIGNAL region (measured bytes) | golden sha12 |
|---|---|---|---|---|---|---|
| E52WA | `signal error;` | 128 B | `0016` | `0002` | 0006 `21 00 00 / AF / CD` slot 000B `?SIGOP`; only RELOC is `data 0x0` (the `x = 2` SHLD at 000D); `?STOPX` slot 0014 | `5e38a2bcfec7` |
| E52WB | `signal error(0);` | 128 B | `0016` | `0002` | BYTE-IDENTICAL to WA — `error(0)` indistinguishable from bare | `56cea6201f78` |
| E52WC | `signal error(2);` | 128 B | `0016` | `0002` | operand `21 02 00` — argument verbatim in the LXI, ABSOLUTE, no RELOC | `e429edbe557a` |
| E52WD | `signal error(255);` | 128 B | `0016` | `0002` | operand `21 FF 00` | `eda07465e7c4` |
| E52WE | `signal error(256);` | 128 B | `0016` | `0002` | **DR-ACCEPTED** with operand `21 00 01` — full 16-bit little-endian | `620816c8830b` |
| E52WF | `signal error(1+1);` | 256 B | `0029` | `0003` | FIXBIN STACK route, NOT folded: pushes via `?DLDOP` (slots 000C, 0014) + `?DADOP` (0017) + `?QDI15` (001A), then `AF / CD` slot 001E `?SIGOP`; literal cell shared at data 0 | `23d7cd1533bb` |
| E52WG | `n = 1; signal error(n);` | 128 B | `001C` | `0004` | `n = 1` at 0006-000B, then HL route `2A r(n@0) / AF / CD` slot 0011 `?SIGOP` — no stack | `cd2070908104` |
| E52WH | `signal endpage(pf);` | 256 B | `0017` | `0002` | 0006 `21` + `LINK-SEL-COMMON PF` + `RELOC common 0x0` / `3E 08` / `CD` slot 000C `?SIGOP`; COMMON PF `0024` = 34+len(`pf`) [C120] | `42eec0e0e51e` |
| E52WI | `signal endfile(f);` | 256 B | `0017` | `0002` | same shape with `3E 05`; COMMON F `0023` = 34+len(`f`) [C120] | `193ee79323aa` |
| E52WJ | `on error(1) x = 1; signal error(1);` | 256 B | `0027` | `0002` | ON registration [C366]-verbatim 0006-000F (`?ONCOP` slot 000B, jump-over `C3` slot 000E); inline handler `21 01 00 / 22 r(x) / C9` 0010-0016; jump-over patches to 0017 which IS the signal region `21 01 00 / AF / CD` slot 001C `?SIGOP`; NO SP cell | `3bf5f3e16f91` |
| E52WK | `if dl < 0 \| dl > 2 then signal error;` | 128 B | `0027` | `0004` | [C367] `E52VB` fold VERBATIM 0006-0016; `F2` slot 0015 (`LINK-SET-LC code 0015`) carries `RELOC code 0x1e` = signal 0017 + 7 — the jump patches PAST the whole 7-byte statement; `x = 2` at 001E | `37bae1d7df4f` |
| E52WL | `signal endfile;` (bare file condition) | — | — | — | NO .REL — `SYNTAX ?` PASS 2 line 12 (see §1) | .PRN only |

## 3. Hypothesis verdicts (pre-registered in PLAN §3; every MISS kept verbatim)

- **H-A CONFIRMED** (WA): exactly `21 00 00 / AF / CD <slot>` = 7 bytes, LXI operand ABSOLUTE
  (no RELOC), slot CHAIN-EXTed `?SIGOP`, next statement at the very next byte. No falsifier
  fired: no `3E 00`, no extra CALL/JMP, no operand RELOC, no pad/registration bytes. SIGNAL is
  a PURE statement.
- **H-B0 CONFIRMED** (WB): `error(0)` accepted, byte-identical to H-A.
- **H-B2 CONFIRMED** (WC): `21 02 00` — the argument IS the LXI operand verbatim ([C366] law
  mirrored onto `?SIGOP`).
- **H-C255 CONFIRMED** (WD): `21 FF 00`, 16-bit verbatim.
- **H-C256 — ACCEPTED; the refusal competitor FALSIFIED** (WE): DR accepts `error(256)` and
  emits `21 00 01`. The documented 0..255 subcode range is NOT a compiler acceptance rule on
  this route; no 0..255 range check exists in the SIGNAL error path. Kept VERBATIM.
- **H-D1 UNKNOWN-RESOLVED, UNARMED** (WF): `error(1+1)` is DR-ACCEPTED through the runtime
  FIXBIN stack route (`?DLDOP` ×2, `?DADOP`, `?QDI15`), NOT folded to `21 02 00`. The "folded
  absolute" competitor is dead; the stack-route competitor is the MEASURED shape — but it is a
  SINGLE witness, so per the pre-registered clause NOTHING was generalised and NOTHING armed:
  open `my-gap` [TBD], bytes panel-unverified by my compiler.
- **H-D2 UNKNOWN-RESOLVED, UNARMED** (WG): `error(n)` is DR-ACCEPTED via `LHLD n / XRA A /
  CALL ?SIGOP` (CODE `001C`) — the HL route, no stack. Single witness; armed NEITHER (see WF).
- **H-E1 CONFIRMED** (WH): 11 bytes `21 + RELOC common 0x0 / 3E 08 / CD ?SIGOP`; the SEL-COMMON
  record fires because the selected group changes; the plain-file COMMON group obeys the [C120]
  34+len(name) law on this route (PF `0024` — PLAN §3's `0023` guess applied to the 1-char name
  `f`; len(`pf`) = 2 gives `0024`, exactly as the [C120] law predicts).
- **H-E2 CONFIRMED** (WI): SIGNAL's A byte TRACKS the ON condition codes — ENDFILE `05`
  ([C120] family; ENDPAGE `08` mirrors COPYLPT 0254's ON-route control byte), UNDEFINEDFILE
  through SIGNAL UNMEASURED.
- **H-F CONFIRMED** (WJ): the ON registration is byte-for-byte [C366]; the signal lands AT the
  jump-over target with ZERO added bytes to the registration; DATA stays `0002` — a returning
  handler still demands NO SP cell and NO pad [C206].
- **H-G CONFIRMED** (WK): the [C367] fold region is emitted UNCHANGED (the OR encoder was never
  modified to fit SIGNAL) and its single terminal `F2` patches past the 7-byte statement.
- **H-X RESOLVED — `dr-refuses`** (WL): the manual's own bare `signal endfile;` form is a
  PASS-2 `SYNTAX ?` refusal with NO .REL. Recorded VERBATIM; registered on the NEG panel; no
  golden invented; refused BY NAME in my compiler with the honest marker (see §5).

Deliberately NOT probed (PLAN §3, kept UNMEASURED and refused BY NAME): `SIGNAL … FROM(expr)`
(no DR object witness anywhere), multiple arguments `error(1,2)`, other condition names through
SIGNAL, `signal undefinedfile(f)`.

## 4. Frontend defect record (PLAN §7) — repaired AFTER evidence

`parser.ml`'s SIGNAL branch consumed `(args)` into `_sargs` and DISCARDED them; `ast.ml`
`Ssignal` carried only `cond`/`target` — post-parse the compiler could not distinguish
`signal error;`, `error(0)`, `error(1)`, `error(256)` or `endpage(printfile)`: a loss of source
semantics, not merely an unimplemented emitter. Repaired at `d84665c` (evidence-first, after the
campaign): `Ssignal` gains `cargs : expr list` (analogous to `Son`/`Srevert`), the parser passes
the parsed list, `bind.ml` (574/1518) and the `pli80deps` walker traverse it; `FROM` is KEPT in
the AST and NEVER lowered. The representation change did NOT widen what codegen admits. AST
preservation is PROVEN — including on still-refused shapes (WG `error(n)`, WF `error(1+1)`,
multi-arg `error(1,2)`, FROM bare+args, WL bare-file) — by `ocaml/proto/ssignal_ast.ml`
(`91060ea`, arch1 precedent): **12/12 PASS**, build+run rc=0 DIRECT.

## 5. Arm, verification, registration

Arm `d84665c` (frontend files + `ocaml/lib/codegen.ml`): `signal_error_prefix` is its OWN
encoder ([C202] one-primitive doctrine — the ON-role [C366] encoder is never reused for the
SIGNAL role); the FILE form reuses `on_reg_prefix` because the measured bytes agree. The arm
admits ONLY measured shapes: ERROR bare or ONE integer literal (full 16-bit operand — WE proved
no range check) as ABS LXI + `AF` + `call_ext "?SIGOP"`; `endpage(f)` `3E 08` / `endfile(f)`
`3E 05` with a single declared file identifier. PURE statement: no `C3` slot, no handler, no pad,
no SP cell; `st.lowered` incremented, `st.last_imm <- None` at the call (HL clobbered). Every
other shape refuses BY NAME [TBD].

Verification (all rc DIRECT): build rc=0, binary sha256 `a4c0e235ed4bb81fe284…` (md5
`cbede3b5…`); per-File warning histogram codegen 68 / total 124 == baseline; **9/9 accepted probes
(WA-WE, WH-WK) whole-file cmp rc=0** against `golden/e52p10/` via POSITIONAL `pli80c` into FRESH
paths; sweep FAILS 0; markers harness (CRLF + bare `^Z`) 10/10 MARKER_FAILS 0; regressions 17/17
(E52UA..UF + E52VA..VK); EXPR1/EXPR2 POSITIONAL VERBATIM unchanged (GET 21 / FLOAT 35).
**LESSON (accepted):** a pipeline-tail `| head` hid the FIRST build rc; a STALE
`_build/default` binary then FALSE-REFUSED WK; re-verify at least one cmp on the binary you
trust — the cmp, not a recorded hash, is the authority.

LOAN2 ADVANCED VERBATIM past line 92 to `codegen: PUT FILE(OUTPUT) has no byte-exact DR witness
[TBD] (line 99)` — ACTUAL text recorded, NOT predicted (PLAN §6 forbade a prediction), UNARMED,
NEVER fixed; the census (`0198fe5`, OWN path, counts UNCHANGED 15/0/26/0) carries the MOVED
message. If the marker question matters: an LF-only compile of WL reports line 6; the gate's
CRLF + bare-`^Z` materialization reports line 12 — the DR-agreeing line — and the registered
marker `SIGNAL endfile with 0 argument(s)` was RE-MEASURED under the gate materialization
(hop-2 lesson re-confirmed).

Registration `21d4db6`: SPECIMENS +9 (WA-WE, WH-WK ONLY — WF/WG are my-gap refusals, not
panel specimens), `E52WL` enters REJECTS as a genuine `dr-refuses` (decision recorded honestly;
precedent SF/SG); `--update-inventory` → **1269 specimens (+9 exactly) / 187 refusals (+1)**,
every added line inspected, `git diff --cached --stat` clean of config; py_compile rc=0.
**C368 `7153716`** written from MEASURED BYTES ONLY (all cited regions re-read FIRST-HAND from
the raw records before appending) and committed BEFORE any `spec/COVERAGE.tsv` touch; row
`COND.SIGNAL` SUPPORTED / **EXACT:9** + EXPLICIT `spec/COVERAGE-IDS.txt` line `65b005e` (NEVER
`coverage_gen.py`; 15 columns from the FIRST NON-COMMENT row; csv `delimiter='\t'`; diff verified
≈ two lines BY CONTENT); `coverage_check.py` rc=0 **142 rows, 0 errors, 0 warnings, SUPPORTED
92** with stats refreshed by their OWN write path; FULL gate rc=0 DIRECT
`build/gate-e52p10-reg.log` — **1269/0 byte-exact, 187/187 negatives, 9/9 divergence, coverage
142 rows 0/0, census 15/0/26/0, prose 5** — every pre-registered number HIT.

## 6. What P3-10 does NOT say (byte tier only)

- **Byte tier only**: no `golden/e52p10` object was linked or run under cpmsim. NOTHING here
  asserts runtime signal DELIVERY, handler activation, or any `?SIGOP`/PLILIB behaviour — the
  library's action is UNEXAMINED and no `spec/RUNTIME.txt` row comes from this subround. Byte
  parity is not a semantics claim.
- **WF/WG are accepted-but-UNARMED**: their emission routes (stack `?DLDOP/?DADOP/?QDI15`,
  `LHLD`) are measured from DR goldens but are SINGLE witnesses; my compiler refuses both BY
  NAME (`my-gap` [TBD]) and its bytes for these shapes are PANEL-UNVERIFIED. Generalising from
  one witness was pre-registered as forbidden and was not done.
- **O-1**: the LOAN2 0359, EXPR1 0175+018D, EXPR2 023D+0255 and COPYLPT 02AA/0254 citations are
  ORIGINAL-GOLDEN DECODES (`build/e52p10/*-reldump.txt`, `e52p10-signals-disasm.txt`), not cmps;
  the BINDING panel authority is the nine `E52WA..WK` whole-file cmp rc=0.
- **The BY-NAME perimeter is MY gap, never a DR rule**: FROM, multi-argument `error(1,2)`,
  other condition names through SIGNAL, and `signal undefinedfile(f)` are UNMEASURED on both
  sides; a bare file condition is `dr-refuses` ONLY for `endfile` (WL) — other bare spellings
  UNMEASURED.
- LOAN2 is NEVER claimed exact; it still refuses (NO .REL) at the line-99 `PUT FILE(OUTPUT)`
  blocker, recorded and NOT fixed; **P3-11 is NOT authorized**. GOLDENS ARE EVIDENCE, NEVER
  RE-DERIVED; the operator's `handoff.config.json` was NEVER staged; no push.

# E2E-52/P3-11 RESULTS — the named-file PAGE/LIST/SKIP blocks ride VERBATIM behind a lowered
PRINT open; the eligibility guard is a SOURCE-STRUCTURE list; the DOUBLE back-patch under IF
(campaign e52p11) — CLOSED (2026-11-07, hop 5)

Pre-registered in PLAN §P3-11 (hops 1–2: Phase-A raw-record audit with ZERO oracle, then PLAN
§P3-11 H-A..H-K + probes `probes/E52XA..XK.PLI` committed by EXPLICIT paths BEFORE the first
oracle call and BEFORE any `ocaml/` byte); campaign e52p11 **11 ok / 11**, every `.PRN`
`NO ERROR(S)` in BOTH passes — ZERO `dr-refuses`; goldens VERBATIM `060289e` committed BEFORE
any emitter byte; arm `3e0a3c1` (candidate A); registration `69dd508` (inventory 1269→**1278**,
refusals 187→**189**); census OWN path in the same commit (counts UNCHANGED 15/0/26/0); claim
**C369** `a00fc13` written from MEASURED BYTES ONLY and committed BEFORE any `spec/COVERAGE.tsv`
touch; coverage row EXTENSIONS `b9645fa` (NO new rows, `spec/COVERAGE-IDS.txt` diff EMPTY,
`coverage_gen.py` NEVER run, 15 columns from the FIRST NON-COMMENT row, tab-delimited text edit
because `csv.writer` would have re-quoted 7 unrelated lines); FULL gate rc=0 DIRECT
`build/gate-e52p11-reg.log` — **1278/0, 189/189, 9/9, 142 rows 0/0, census 15/0/26/0, prose 5** —
every pre-registered number HIT. All rc captured DIRECTLY (never through a trailing pipeline);
goldens NEVER re-derived; `pli80c` POSITIONAL into FRESH paths; `handoff.config.json` NEVER
staged; no push.

## 1. Campaign (oracle, ONE grouped batch)

`PLI_SRC=probes timeout 900 python3 oracle/batch.py E52XA..E52XK --tag e52p11 --switches '$L$D'`
rc=0 → **11 ok / 11**; `build/e52p11/campaign-rc.txt`; every accepted `.REL` preserved VERBATIM
into `golden/e52p11/` and re-dumped to `build/e52p11/E52X*-reldump.txt`.

## 2. Measured table (9/9 cmp rc=0 on armed binary sha256 `25c57e27696421e929b8…`, re-verified
POSITIONAL into FRESH `build/e52p11/out/`; every region re-read FIRST-HAND from the raw records
at registration and again before C369; sizes from the DEF-CODE-SIZE / DEF-DATA-SIZE records)

| Probe | Shape | Verdict | Size | CODE | DATA | Measured region | golden sha12 |
|---|---|---|---|---|---|---|---|
| E52XA | `open file(pf) print;` + `put file(pf) page;` + `x = 2` | EXACT | 256 B | `0036` | `0002` | open `AF 47 C5 33 / 21 52 06` (w1 `0x0652`) `… CD` `?OIOOP@0019`; PAGE at `001B`: `21`+`RELOC common 0x0` / `11 52 06` / `01`+slot `0022` / `CD` `?SIOOP@0025 ?PAGOP@0028 ?QIOOP@002B`; SET-LC `0022` RELOC `code 0x2d` → `x = 2` at `002D` | `595f31bd6180` |
| E52XB | `title('TEST') print` (NO pagesize) + page | EXACT | 256 B | `003E` | `0006` | 29-B TB block, w1 `0E52`, `?SLCTS@000C`; PAGE at `0023`, slot `002A` → `0035` | `073ffb3a20d1` |
| E52XC | `title('$con') print pagesize(0)` + page (LOAN2:54+99 mirror) | EXACT | 256 B | `003E` | `0006` | w1 `2E52`; PAGE at `0023`, slot `002A` → `0035` | `0f47ebfe5444` |
| E52XD | `title(name) print` — VARIABLE varying title (LOAN2:56 mirror) | EXACT | 256 B | `003C` | `0011` | 27-B `?SLVTS@000A` route, w1 `0E52`; PAGE slots `?SIOOP@002B ?PAGOP@002E ?QIOOP@0031`, slot `0028` → `0033` | `e40a283adb7e` |
| E52XE | `if n < 0 then put file(pf) page;` | EXACT | 256 B | `003D` | `0004` | **DOUBLE back-patch**: SET-LC `0029` (PAGE LXI B) AND SET-LC `0020` (F2 skip) BOTH carry RELOC `code 0x34`; `?SIOOP@002C ?PAGOP@002F ?QIOOP@0032` | `646e8ac3fd1c` |
| E52XF | TB open in THEN, TC open in ELSE, then ONE page | EXACT | 384 B | `0063` | `0017` | F2 slot `000B` → `002D`; ELSE `C3` slot `002B` → `0048`; ONE 18-B PAGE after the merge, `?SIOOP@0052`, NO pad | `fe39d3534116` |
| E52XG | print open + `list('A')` | EXACT | 256 B | `003E` | `0003` | P019B 26-B LIST verbatim: `21`+`RELOC data 0x0`+`3E 01`, `?SLCTS@002D ?PNCOP@0030 ?QIOOP@0033`, slot `0022` → `0035` | `b498e2f1ac72` |
| E52XH | print open + bare `skip` | EXACT | 256 B | `0038` | `0002` | E46N1 20-B shape `3E 01 / ?SKPOP@002A / ?QIOOP@002D`, **NO `?PNCOP`**, slot `0022` → `002F` | `7b6db79cf78b` |
| E52XI | print open + `skip list('A')` | EXACT | 384 B | `0043` | `0003` | E46N2 31-B shape: skip BETWEEN attach and chain `?SKPOP@002A` then `?SLCTS@0032`, `?PNCOP@0035` only because a chain follows, `?QIOOP@0038`, slot `0022` → `003A` | `7578173a18ed` |
| E52XJ | `put file(pf) page;` with NO open anywhere | DR-ACCEPTED, **my-gap** (rc=2, NO `.REL` here) | 256 B | `0021` | `0002` | `LINK-SEL-COMMON PF` at FIRST USE (raw record @834), same 18 B `?SIOOP@0010 ?PAGOP@0013 ?QIOOP@0016`, slot `000D` → `0018` — E46L8's no-open LIST geometry asked of `?PAGOP` | `f164f7770e31` (kept UNCLAIMED) |
| E52XK | `open file(pf) stream input;` + page | DR-ACCEPTED, **my-gap** (rc=2, NO `.REL` here) | 256 B | `0036` | `0002` | open word `21 90 06` (`0x0690`), PAGE attach STILL `11 52 06` (`0x0652`) — geometry IDENTICAL to XA | `4acb18b5ce6d` (kept UNCLAIMED) |

## 3. Hypothesis verdicts (pre-registered in PLAN §3; every MISS kept verbatim)

- **H-A CONFIRMED except for MY OWN pre-registration slip.** Everything measured as predicted —
  18-B PAGE at `001B`, attach `11 52 06`, CB operand `RELOC common 0x0`, `?PAGOP` with NO count
  operand, CODE `0036`, COMMON PF `0024` = 34+2, ONE `SEL-COMMON` at the open — but §4 predicted
  the LXI B slot would patch to `0030`; **the measured target is `002D` = `001B + 18`**. Recorded
  VERBATIM, the law bullet in [C369] uses the measured value. No falsifier fired: no attach
  mirroring, no `3E nn`, no extra CALL, no refusal.
- **H-B CONFIRMED; the pagesize-required competitor FALSIFIED.** `title('TEST') print` with NO
  pagesize and NO linesize is DR-ACCEPTED (`NO ERROR(S)` both passes) with w1 `0E52` and the
  ordinary 18-B PAGE. A pagesize bit is NOT required before a file PAGE is accepted.
- **H-C / H-D CONFIRMED** (CODE `003E` w1 `2E52`; CODE `003C` on the 27-B `?SLVTS` route). The
  18 bytes are INVARIANT across titleless / literal-title / literal-title-with-pagesize /
  variable-varying-title open routes.
- **H-E CONFIRMED — DOUBLE back-patch; the SINGLE-patch competitor FALSIFIED.** Both slots patch
  to the same continuation `0034`, the LOAN2 98–99 geometry (03A8 + 03B1 → 03BC) panel-verified
  minimally.
- **H-F CONFIRMED** — ONE PAGE after the merge of two branch-local opens; NO pad and NO
  branch-local eligibility: an open on ANY lowered source path before the PUT suffices.
- **H-G / H-H / H-I CONFIRMED — the ONE route-independent item emitter.** LIST/SKIP/SKIP-LIST
  behind a PRINT open reproduce P019B (26 B), E46N1 (20 B, no `?PNCOP`) and E46N2 (31 B)
  VERBATIM; zero statement bytes were added or changed for these three.
- **H-J RESOLVED — DR ACCEPTS (my-gap).** No-open file PAGE compiles in DR with `SEL-COMMON` at
  FIRST USE. My compiler refuses it BY NAME; the golden is KEPT and claimed by NO rule of mine
  (E46L8/SE precedent). DR's object is the evidence that the guard's open-list is a compiler-side
  eligibility choice, not a DR requirement.
- **H-K RESOLVED — DR ACCEPTS (my-gap); the input-mirroring attach competitor FALSIFIED.** The
  open carries `0x0690` and the PUT attach stays `0x0652` — [C280]'s direction law reconfirmed on
  a new route. Mine refuses the INPUT-direction named PUT BY NAME.

## 4. Arm, coverage, registration

Arm `3e0a3c1` = candidate A: ONE condition line in `lower_open` records a `PRINT`-spelling OPEN
beside `OUTPUT` into the compiler-side eligibility list. The open emitters, the 18-B PAGE
encoder, the LIST/SKIP emitters and the `[TBD]` refusals are UNCHANGED — zero statement bytes
differ; the PU1 negative-panel marker substring `PUT FILE(F) has no byte-exact DR witness`
survives VERBATIM (its message BODY moved, per PLAN §5). Verification: build rc=0, binary
`25c57e27696421e929b8…` (deterministic, fresh `_build-e52p11`), histogram codegen 68 / total 124
== baseline, 9/9 cmp rc=0, XJ/XK rc=2 BY NAME, sweep FAILS 0, markers 5/5 MARKER_FAILS 0
(incl. PU1/E41X5/E46K10/N3_PAGE/E46N21), regressions 38/38. Registration `69dd508`: SPECIMENS +9
(XA..XI ONLY), XJ/XK → REJECTS as honest `my-gap` rows with markers RE-MEASURED under the gate's
CRLF + bare-`^Z` materialization (XJ line 8, XK line 9); `--update-inventory` 1269→**1278 / 189**
(+9/+2 EXACTLY, every added line inspected, config NOT staged). Coverage `b9645fa` EXTENDS
`FILE.PUT_PAGE` (EXACT:1→**7**), `FILE.PUT_SKIP` (EXACT:18→**20**) and `FILE.PUT_LIST`
(EXACT:10→**11**) — LIST counts 12 probes as EXACT:10 because E46M33/M34 are `dr-refuses`, so
EXACT = byte-exact panel members, not len(probes); `coverage_check.py` validates the FORMAT of
`rel_parity` only, never N against the panel, so the bumps were verified by hand against
`spec/INVENTORY.txt` (all nine X-probes are `golden/` specimens) and then adjudicated rc=0; the
LIST row's now-false "No object yet pairs a file PUT with one of the newly lowered PRINT opens"
clause is kept AS WRITTEN inside a labelled `[E2E-52/P3-11 CORRECTION]` (quote-then-correct, the
P3-8/P3-10 precedent). `coverage_check` rc=0 **142 rows, 0 errors, 0 warnings, SUPPORTED 92**
(rows and the canonical stats UNCHANGED — extensions move no counter), `file_prose_check` rc=0.

**TOOL LESSONS (accepted).** (1) A reldump DATA record can print a SINGLE hex digit (`0x6`);
a `0x[0-9a-f]{2}` regex silently MISSES it and produced false `-1` holes in my first quick dump —
always `0x[0-9a-f]{1,2}`. (2) Do NOT hand-parse raw `.REL`: MACREL record types carry the HIGH bit
(81H..8FH) and a 01H..0FH walk dies at byte 0 — use the `build/e52p8/ondump2.py` /
`build/e52p9/reldumps.py` chain (ondump2 IGNORES CLI args, hard-coded TARGETS). (3) `csv.writer`
with `delimiter='\t'` still re-quotes 7 unrelated COVERAGE lines; edit these rows TEXTUALLY and
verify the diff BY CONTENT (3 lines, 15 columns each).

**LOAN2 — the line-99 blocker is CLOSED; the ACTUAL next blocker is recorded, NEVER fixed**
(PLAN §6 STOP): rc=2, NO `.REL`, message VERBATIM `codegen: DECIMAL assignment between differing
scales is unproven [TBD] (only computed results are pinned as needing a QDDSL/QDDSR fix; a direct
DEC operand store always had equal scales in the samples)` — a message that carries **NO `(line N)`
clause**, so the census/registration lines moved accordingly. EXPR1 (GET line 21) and EXPR2 (FLOAT
line 35) UNCHANGED. Nothing further is authorized from this text.

## 5. What P3-11 does NOT say (byte tier only)

- **Byte tier only**: no `e52p11` object was linked or run under cpmsim; NOTHING here asserts page
  placement, line counting, skip semantics or any PLILIB runtime action, and no `spec/RUNTIME.txt`
  row comes from this subround. Byte parity is not a semantics claim.
- **Eligibility is SOURCE STRUCTURE, never runtime typestate**: the guard answers only "did THIS
  compiler lower an OUTPUT- or PRINT-spelling OPEN for this file group earlier in source order
  (either branch of an IF counts)". XJ (no open) and XK (INPUT open) prove DR does NOT require what
  my guard requires; that difference is my `my-gap`, never a DR rule.
- **Perimeter KEPT, all refusals BY NAME**: PAGE with additional control items (COPYLPT 0268
  class), counted `page(n)`, `LINE` (dr-refuses E46N21), console `put page;` (N3_PAGE), KEYED
  files, INPUT-direction named PUTs and no-open named PUTs (PU1/E41X5/E46K10 class), and VARIABLE
  LIST items behind a PRINT open (LOAN2 `list(clear)` sites, original-golden witnesses only). No
  name-based special-casing: any file identifier in a lowered PRINT (or OUTPUT) open records its
  group.
- LOAN2 is NEVER claimed exact; **the DEC-scales blocker is NOT a diagnosis and NOT authorization**
  — it is the ACTUAL recorded refusal text, unfixed; **P3-12 is NOT authorized** and no next-blocker
  work may be opened from this section.

# E2E-52/P3-12 RESULTS — the cross-scale DIRECT fixed-decimal store shifts by |Δscale| only,
between the source push and the destination load; `?DSTOP` carries the TARGET precision
(campaign e52p12) — CLOSED (2026-11-07, hop 4)

Pre-registered in PLAN §P3-12 (hop 1: Phase A with ZERO oracle — authentic LOAN2.REL
`04B7–04CB` DOWN witness + registered-negative NG20 UP witness + LOAN1 equal-scale control
re-measured `cmp` rc=0 + NG21 FALSIFIED as evidence; then PLAN §P3-12 H-1..H-8 + probes
`probes/E52Y{A..I}.PLI` committed by EXPLICIT paths BEFORE the first oracle call and BEFORE any
`ocaml/` byte); campaign e52p12 rc=0 **9 ok / 9**, every `.PRN` `NO ERROR(S)` in BOTH passes —
ZERO `dr-refuses`; goldens VERBATIM `0c43932` committed BEFORE any emitter byte; arm `1111d5e`
plus the warning-profile fix `60b9c79` (armed binary sha256 `6a4c6c1154a0acd8403b…`,
deterministic); registration `5bf5c88` (inventory 1278→**1288**, refusals 189→**188** by the
honest NG20 retirement); census OWN path in the same commit (counts UNCHANGED 15/0/26/0, LOAN2
message MOVED VERBATIM to the Line-117 blocker, NOTHING fixed); claim **C370** `172a642` written
from MEASURED BYTES ONLY and committed BEFORE any `spec/COVERAGE.tsv` touch; NEW row
`STOR.DEC_SCALE_ASSIGN` + SAME-change `spec/COVERAGE-IDS.txt` line `bf135a9` (NEVER
`coverage_gen.py`; 15 cols from the FIRST NON-COMMENT row; textual tab edit; `manual_ref`
corrected to the `NONE:` form after `coverage_check` adjudicated the free-prose variant live) +
machine stats companion `d283623` → `coverage_check` rc=0 **143 rows, 0 errors, 0 warnings,
SUPPORTED 93**; FULL gate rc=0 DIRECT `build/gate-e52p12-reg.log` — **1288/0, 188/188, 9/9,
143 rows 0/0, census 15/0/26/0, prose 5** — every pre-registered number HIT. HONEST TOOL NOTE:
the gate was first launched in the BACKGROUND and its exit status was therefore NOT captured
directly; the canonical `build/gate-e52p12-reg.log` is the SYNCHRONOUS re-run whose rc=0 was
read DIRECT (`$?` immediately after the redirected process); both logs are byte-identical in
content. All other rc captured DIRECTLY (never through a trailing pipeline); goldens NEVER
re-derived; `pli80c` POSITIONAL into FRESH paths; `handoff.config.json` NEVER staged; no push.

## 1. Campaign (oracle, ONE grouped batch)

`PLI_SRC=probes timeout 900 python3 oracle/batch.py E52YA E52YB E52YC E52YD E52YE E52YF E52YG
E52YH E52YI --tag e52p12 --switches '$L$D'` rc=0 → **9 ok / 9** (`golden/e52p12/summary.txt`:
every row `PRN=True REL=True`; 8 × 256 B, YH 384 B). Every accepted `.REL` preserved VERBATIM
into `golden/e52p12/` and decoded into `build/p3-12/E52Y*-reldump.txt` + `E52Y*-disasm.txt`
(ondump2 buffers + dis80 opcode table + `LINK-CHAIN-EXT` names at anchor = opcode+1).

## 2. Measured table (9/9 whole-file cmp rc=0 on armed binary sha256 `6a4c6c11…`, re-verified
POSITIONAL into FRESH `build/p3-12/fix-out/` AFTER the warning fix; sizes from the
DEF-CODE-SIZE / DEF-DATA-SIZE records; every region below re-read FIRST-HAND this close)

| Probe | Store | Verdict | Size | CODE | DATA | Measured store region (CALL names from CHAIN-EXT anchors) | golden sha12 |
|---|---|---|---|---|---|---|---|
| E52YA | `a(9,2) = b(6,2)` equal-scale control | EXACT | 256 B | `003C` | `0009` | `LXI H,b(data@0005) / MVI A,06 / ?DLDOP@000B / LXI H,a(data@0000) / MVI A,09 / ?DSTOP@0013` — **NO helper**, §4 prediction HIT | `c26a3af19e8b` |
| E52YB | `a(9,2) = b(9,0)` UP d=2 (Δp=3) | EXACT, §4 LABEL MISS | 256 B | `0041` | `000A` | `LXI H,b(0005) / MVI A,09 / ?DLDOP@000B / MVI A,02 / ?QDDSL@0010 / LXI H,a(0000) / MVI A,09 / ?DSTOP@0018` — §4 said `?QDDSR` | `7af4556b587f` |
| E52YC | `b(15,13) = a(6,2)` UP d=11, Δp=9 | EXACT | 256 B | `0041` | `000C` | same geometry, `MVI A,0B / ?QDDSL@0010`, dst `MVI A,0F` — precision NOT in the amount (H-2 falsifier) | `0c709ca1df74` |
| E52YD | `inf(4,3) = ci(15,14)` = LOAN2:111 verbatim geometry | EXACT | 256 B | `0041` | `000B` | `LXI H,ci(0000) / MVI A,0F / ?DLDOP@000B / MVI A,0B / ?QDDSR@0010 / LXI H,inf(0008) / MVI A,04 / ?DSTOP@0018` — cell widths 8+3 match [C084] | `35e834ac73f1` |
| E52YE | `a(9,2) = c(9,0)` UP d=2, Δp=0 | EXACT, §4 LABEL MISS | 256 B | `0041` | `000A` | `MVI A,02 / ?QDDSL` — §4 said `?QDDSR` ("as YB") | `1066a4e92cdf` |
| E52YF | `b(15,0) = a(15,14)` DOWN d=14 | EXACT | 256 B | `0041` | `0010` | `LXI H,a(0000) / MVI A,0F / ?DLDOP / MVI A,0E / ?QDDSR@0010 / LXI H,b(0008) / MVI A,0F / ?DSTOP` — no d cap (H-3 falsifier) | `2f7ed5a93d1e` |
| E52YG | `a(15,1) = b(15,14)` | EXACT, §4 DIRECTION MISS | 256 B | `0041` | `0010` | `LXI H,b(0008) / MVI A,0F / ?DLDOP / MVI A,0D / ?QDDSR@0010 / LXI H,a(0000) / MVI A,0F / ?DSTOP` — §4 predicted UP/`?QDDSL`, measured DOWN | `265f1c9ce4af` |
| E52YH | `c = a / b` computed control (all dec(9,2)) | EXACT | 384 B | `0051` | `000F` | [C086] divide geometry VERBATIM, UNTOUCHED by this slice: `DLDOP(a) / MVI A,06 ?QDDSL / DLDOP(b) / ?DDVOP / MVI A,04 ?QDDSR / LXI H,c(000A) / MVI A,09 / ?DSTOP` | `88a5688cf031` |
| E52YI | `d(9,2) = decimal(i,7)`, `i` fixed bin | EXACT after arm (pre-arm honest `my-gap`, cmp FAIL byte 68) | 256 B | `003F` | `0007` | `LHLD i(data@0000) / ?QI15D@0009 / MVI A,02 / ?QDDSL@000E / LXI H,d(0002) / MVI A,09 / ?DSTOP@0016` — shift PRESENT; my context model predicted none | `cb7dc30f33f0` |
| NG20 (retired `N35_DEC_STORE_SCALE_DRIFT`) | `c(9,4) = a(9,2)` UP d=2 | EXACT — now a POSITIVE specimen | 256 B | `004C` | `000F` | store at 0016–0028: `LXI H,A / MVI A,09 / ?DLDOP / MVI A,02 / ?QDDSL / LXI H,C / MVI A,09 / ?DSTOP` — golden KEPT, NEVER re-derived; cmp rc=0 re-measured twice on the armed binary | `8317ccb59f82` |

The uniform `+5` code bytes of YB..YG over YA (`3E dd CD 00 00`) are exactly the shift; the
`?DSTOP` `MVI A,<p>` is the TARGET precision in every row; every accepted store is ONE source
push (`?DLDOP`, or `?QI15D` on the conversion route) and ONE `?DSTOP` (H-8).

## 3. Hypothesis verdicts (pre-registered in PLAN §3; every MISS kept verbatim)

- **H-1 CONFIRMED 7/7 cross-scale** — the shift `MVI A,|Δs| / CALL ?QDDSL` (s increases) or
  `?QDDSR` (s decreases) sits BETWEEN the source `?DLDOP` and `LXI H,dst`; the amount NEVER
  involves a precision; equal scale emits NO helper (YA; LOAN1 `PMT = P` control).
- **H-2 FALSIFIED (precision in the amount).** YC Δp = 6→15 (=9) and YD Δp = 15→4 (=11) both
  emit d = |Δscale| = `0B` exactly.
- **H-3 FALSIFIED (a cap).** YF d = 14 and YG d = 13 are DR-ACCEPTED with the same geometry; no
  refusal, no different encoding.
- **H-4 FALSIFIED in BOTH directions.** YB/YE (up) and YD/YF/YG (down) carry the explicit helper;
  `?DSTOP` alone does NOT rescale. NG20's pre-existing object had already falsified it for the up
  direction.
- **H-5 CONFIRMED — direction symmetry.** YC mirrors LOAN2:111's own down-shift by 11 as an UP
  `?QDDSL` with the identical amount. Adjudication recorded: PLAN §3 pins **H-5 = YC** and
  **H-7 = YH**; an inherited hop-2 shorthand mislabelled the YH row "H-5" — the gate Y-block
  comment was corrected (line-preserving) in the C370 commit.
- **H-6 — the shift-free context model FALSIFIED; DR ACCEPTS `decimal()` into a scaled target
  WITH a shift.** My pre-arm compiler emitted NO shift (descriptor `{sc=ts}` from the target
  context, [C084] reading) → whole-file cmp FAILED at byte 68 = honest `my-gap`. The arm closes
  it by reporting the TRUE pushed descriptor `{sc=0}` for a plain non-DEC integer argument on the
  direct-store route ONLY; `decimal(<bin expr>)` remains UNMEASURED and refuses BY NAME.
- **H-7 CONFIRMED (YH control).** The computed-quotient consumer fix stays on the already-armed
  [C086] bytes — this slice changed ZERO bytes on that route.
- **H-8 CONFIRMED — no stack imbalance.** One push, one pop per accepted store; the helper
  neither pushes nor pops.

## 4. Arm, validation, registration, coverage

Arm `1111d5e` (`ocaml/lib/codegen.ml` ONLY): `dctx.c_direct` TRUE ONLY at the ordinary `Eident`
DEC-store epilogue (dec_push `~direct:true`); `dec_direct_shape` = `Eident` or
`DECIMAL(<plain non-DEC ident>)`; the guard replaces the blanket `ts <> vd.sc` refusal with
`op_mvi_a / |Δs| / call_ext (?QDDSL or ?QDDSR)` between the source push and the destination
load; `dv_of` `Ebuilt("DECIMAL")` reports `sc=0` ONLY when `c_direct` + plain integer ident;
every other route (suffix stores, pointer-formal stores, `decimal(<bin expr>)`, DEC-formal
actuals) keeps the EXISTING [TBD] refusal VERBATIM — the message bodies were edited to stay
marker-substring-safe, and the [TBD] literal count in codegen.ml stayed EXACTLY 68.
Validation (hop 3 + hop 4 sessions): baseline replay via `git archive` re-proved the histogram
method (Warning 27 `ptr` IS baseline); the arm's ONE new W27 (unused `args` in `dv_of`) fixed to
the wildcard `60b9c79` → histogram codegen 68 / total 124 == baseline EXACTLY; sweep
`E46N E46K E51 E52 P086 R10` **159 byte-exact / FAILS 0**; DEC regressions
`R5xx R6xx R7xx R8xx LOAN1` **64 / FAILS 0**; markers **15/16** — the ONLY failing row is
`N35_DEC_STORE_SCALE_DRIFT` BY DESIGN (see retirement below); divergences **9/9 DIV-OK** via
standalone `build/p3-12/divcheck.py` — TOOL LESSON: the gate's `--only-divergent` flag is the
WRITE/re-measure arm (`divergence_remeasure` rewrites `spec/DIVERGENT.txt` and aborts on
promotion) and is blocked mid-registration by the stale-census preflight, so a standalone driver
calling `divergence_load()` + `divergence_check()` is the CHECK arm.

**NG20 retirement-to-positive (honest).** The gate's `NEG_META` for `N35` already recorded "DR
COMPILES IT"; NG20's `.PRN` shows `NO ERROR(S)` both passes and its `.REL` is a genuine UP-shift
witness. By the N26_DECDIV precedent ([C086]) the row LEAVES REJECTS + NEG_META (both deleted
with retirement comments) and `probes/NG20.PLI` — the harness-re-materialized CRLF + bare-`^Z`
source of the retired inline specimen, sha `acf8e951…` — registers as a POSITIVE specimen with
the golden path UNCHANGED (`golden/negpanel1/NG20/NG20.REL`, NEVER re-derived). Refusals
189→**188**. NO replacement negative was invented for the still-refused suffix/pointer store
routes: their DR behaviour is UNMEASURED and a NEG_META row would be invented evidence — the
panel coverage loss is ACCEPTED and recorded in C370 and the COVERAGE row.

Registration `5bf5c88`: SPECIMENS +9 `E52YA..YI` (comments from FIRST-HAND reldump re-reading) +
NG20; `--update-inventory` 1278→**1288** specimens / 188 refusals (+10/−1 exactly, every line
inspected, staged set verified clean of config); census OWN path rc=0, counts 15/0/26/0
UNCHANGED. Claim **C370** `172a642` measured-bytes-only BEFORE any COVERAGE touch (ledger ENDS
C370, 193 headers). COVERAGE `bf135a9`: NEW row `STOR.DEC_SCALE_ASSIGN` SUPPORTED, **EXACT:10**
(9 Y probes + NG20 — EXACT counts byte-exact panel members, the P3-11 adjudication), probes
`E52YA..YI,NG20`, corpus LOAN2,LOAN1, law from [C370] ONLY, BY-NAME perimeter + falsifiers kept
VERBATIM, byte-tier NOT-say; `spec/COVERAGE-IDS.txt` line in the SAME change (IDENTITY invariant);
`coverage_check` rc=0 **143 rows 0/0 SUPPORTED 93**; `file_prose_check` rc=0.

## 5. LOAN2 — ADVANCED and recorded, NEVER fixed

With the armed direct-store law, `artefacts/LOAN2.PLI` UNMODIFIED (sha `7be23ba3…` re-verified)
lowers PAST line 111 (`INF = ci;`) and 112 (the [C086] divide) and dies at the ACTUAL next
blocker — rc=2, NO `.REL`, VERBATIM:

`codegen: non-variable argument against a FIXED DECIMAL formal is unproven [TBD] (DR passes an
automatic decimal BY REFERENCE -- the descriptor holds LXI H,*A(cell); a literal or expression
decimal argument has no sample [DECPOLY, R2037/R2038/R725]. Line 117)`

Line 117 = `call display(PL * INF, INT * INF, PMT * INF, PP * INF, IP * INF);` — computed
DECIMAL actuals against FIXED DECIMAL formals (same guard family as the retained
`N33_DEC_FORMAL` negative). This blocker is RECORDED, NOT diagnosed further and NOT fixed in
this subround; it is P3-13's evidence target under the standing marathon brief. EXPR1 (GET 21)
and EXPR2 (FLOAT 35) UNCHANGED. (Operational honesty: the hop-3 first attempt at this
positional run died on `Sys_error artefacts/LOAN2.PLI` after an accidental `rm` — repaired the
same session by single-path `git restore`, sha re-verified twice; `Sys_error` was recorded NOWHERE
as science; the VERBATIM text above comes from the repaired, re-run positional compile.)

## 6. What P3-12 does NOT say (byte tier only)

- **Byte tier only**: nothing linked or run; NO numerical/rounding/truncation claim about what
  `?QDDSL`/`?QDDSR` DO inside PLILIB — only WHERE the calls sit and what A holds at the call is
  claimed; the helper internals were NEVER examined; no `spec/RUNTIME.txt` row comes from this
  subround. Byte parity is not a semantics claim.
- **Perimeter KEPT, all refusals BY NAME**: suffix/qualified DEC stores, pointer-formal DEC
  stores across scales, `decimal(<binary EXPRESSION>)`, and non-variable actuals against FIXED
  DECIMAL formals all keep explicit [TBD] refusals; C370 claims NONE of them.
- **The NG20 retirement is a panel-classification fact, not a new law** — the UP-shift bytes
  predated this round (authentic-object Phase A witness); what changed is that MY compiler now
  reproduces them byte-exactly. The removed negative is documented in the REJECTS/NEG_META
  retirement comments, not silently dropped.
- LOAN2 is NEVER claimed exact; the Line-117 blocker is the ACTUAL recorded refusal text, not a
  diagnosis and not authorization beyond the marathon brief's standing next-slice clause;
  **P3-13 proceeds ONLY on evidence-first pre-registration**. GOLDENS ARE EVIDENCE, NEVER
  RE-DERIVED; the operator's `handoff.config.json` was NEVER staged; no push.

---

# E2E-52/P3-13 RESULTS — DEC-expression actuals materialise through the 32 B product block with
the [C370] shift window at the FORMAL scale; DEC/INT literals are STATIC pre-scaled
formal-width pool cells with ZERO caller code; the descriptors form ONE static interleaved
vector in argument order (campaign e52p13) — CLOSED (2026-11-06, hop 12)

Pre-registered in PLAN §P3-13 (hops 4–6: Phase A with ZERO oracle — authentic LOAN2.REL
`055D–05FA` product blocks + static descriptor vector `031A–0323` + `NG18.REL` literal witness,
the C093 `*A(005A)=5.67` discrepancy AUDICATED false-as-cited, then PLAN §P3-13 H-1..H-8 +
probes `probes/E52Z{A..F}.PLI` committed by EXPLICIT paths at `7503552` BEFORE the first oracle
call and BEFORE any `ocaml/` byte, with ZERO-oracle sanity compiles pinning all six at the
guard); campaign e52p13 rc=0 **6 ok / 6**, every `.PRN` `NO ERROR(S)` in BOTH passes — ZERO
`dr-refuses`; goldens + `summary.txt` + transcripts VERBATIM `6267faf` committed BEFORE any
emitter byte; arm `13e53be` (bind `cs_dec` allocation authority + codegen admits ONLY the two
measured actual shapes) plus the histogram repair `e971f3e` and the two measured my-gap repairs
`9b81ed0` (armed binary sha256 `6db44394db5f09ad82cdb8e05f8fc92b298f77305301870de09e2485764bdfd2`,
deterministic, histogram codegen 68 / total 124 == baseline EXACTLY); registration `39bb9a0`
(inventory 1288→**1295**, refusals 188→**187** by the honest N33→NG18 retirement); census OWN
path `59be109` (counts UNCHANGED 15/0/26/0, LOAN2 message MOVED VERBATIM to the Line-121
blocker, NOTHING fixed); claim **C371** `1d1885b9` written from MEASURED BYTES ONLY and
committed BEFORE any `spec/COVERAGE.tsv` touch, INCLUDING the DATED correction of BOTH [C093]
errors; NEW row `PROC.CALL_DEC_ACTUALS` + SAME-change `spec/COVERAGE-IDS.txt` line `afb95163`
(NEVER `coverage_gen.py`; 15 cols from the FIRST NON-COMMENT row; `manual_ref` `NONE:` form);
then the FIRST full-gate run failed rc=1 on `NEG-FAIL N52_DEC_FORMAL_PUT` — adjudicated,
retired honestly to POSITIVE `NG39` (`601e20e1`) with a DATED ADDENDUM to [C371] (`016e58e0`)
and the row extended to **EXACT:8** (`c1059d46`) → `coverage_check` rc=0 **144 rows, 0 errors,
0 warnings, SUPPORTED 94**; FULL gate rc=0 DIRECT `build/gate-e52p13-reg.log` (OVERWRITING the
first failing run's log, which stays quoted verbatim below and in [C371]) — **1296/0, 186/186,
9/9, 144 rows 0/0, census 15/0/26/0, prose 5** — every number pre-registered or adjudicated.
All rc captured DIRECTLY (never through a trailing pipeline); goldens NEVER re-derived;
`pli80c` POSITIONAL into FRESH paths; `handoff.config.json` NEVER staged; no push.

## 1. Campaign (oracle, ONE grouped batch)

`PLI_SRC=probes timeout 900 python3 oracle/batch.py E52ZA E52ZB E52ZC E52ZD E52ZE E52ZF --tag
e52p13 --switches '$L$D'` rc=0 → **6 ok / 6** (`golden/e52p13/summary.txt`: every row
`PRN=True REL=True`; 5 × 384 B, ZF 896 B). Every accepted `.REL` preserved VERBATIM into
`golden/e52p13/` and decoded into `build/p3-13/{zsizes,E52ZA-disasm,E52ZF-disasm}.txt` + raw
data/code reloc dumps via `build/p3-13/p13dump.py` (ondump2 buffers + dis80 table + CHAIN-EXT /
CHAIN-ADDR annotation through the additive `ondump2.full3()`).

## 2. Measured table (8/8 whole-file cmp rc=0 on armed binary sha256 `6db44394…`, re-verified
POSITIONAL into FRESH `build/p3-13/arm-out2/`; sizes and sha12 re-read FIRST-HAND from the KEPT
goldens at this close; every cited region re-verified at claim time against the retained
`.REL` records — see [C371])

| Probe | Shape | Verdict | Size | CODE | DATA | Measured actual site (bytes in [C371]) | golden sha12 |
|---|---|---|---|---|---|---|---|
| E52ZA | `p = q(a * b)`, `a dec(10,2)` `b dec(4,3)` vs `dec(10,2)` formal | EXACT, §4 HIT | 384 B | `006F` | `0011` | 32 B product block `LXI H,*a/MVI A,0A/?DLDOP; LXI H,*b/MVI A,04/?DLDOP/?DMUOP; MVI A,03/?QDDSR; LXI H,*t/MVI A,0A/?DSTOP` — DOWN d=3 between `?DMUOP` and the temp store; 6 B temp; static vector reloc 000F→0011; CHAIN-ADDR slot 002A→code@005A | `33f66277f95c` |
| E52ZB | `p = q(a * b)`, `dec(9,0)*dec(8,0)` vs `dec(7,2)` formal | EXACT, §4 HIT | 384 B | `006F` | `0010` | UP shift `MVI A,02/?QDDSL` ACCEPTED (Δp = −5 irrelevant — direction from SCALES ONLY); temp **4 B** (formal-width stride discriminates H-2); DSTOP `MVI A,07` = pf | `4e9921d90d0e` |
| E52ZC | `p = q(1.5)` | EXACT, §4 HIT | 384 B | `004F` | `000C` | ZERO caller arg code; STATIC 5 B formal-width pool cell `50 01 00 00 00` at data@0000; descriptor 000A inline DATA RELOC → 0000 | `76829f5bf7ed` |
| E52ZD | `r = g(1)` (NG18 shape + skip tail) | EXACT, §4 HIT | 384 B | `004F` | `000C` | pool cell `00 01 00 00 00` (5 B, pre-scaled), descriptor reloc → cell; skip tail QDCOP A `0C`/B `02` as predicted | `ee4cc8e3f021` |
| E52ZE | `p = q(a, a * b, 2.5)` mixed arity 3 | EXACT, §4 HIT | 384 B | `0075` | `0018` | ONE interleaved static vector 0012–0017 `05 00 18 00 00 00` (relocs 0012→0005 own cell / 0014→0018 temp / 0016→0000 literal); 5 B product temp; literal cell `50 02 00 00 00`; callee arity-3 block copy `MVI C,06` | `7495d0406d92` |
| E52ZF | `call display(v1*inf, …, v5*inf)` VOID arity 5 | EXACT, §4 HIT | 896 B | `0106` | `0031` | LOAN2:117–118 replication VERBATIM — five 32 B blocks into 6 B temps stride 6, static 5-cell vector `31 00 37 00 3D 00 43 00 49 00`, `LXI H,*A(vec)` + CHAIN-ADDR slot 00AA→code@00D2, callee `MVI C,0A` block copy + five `LHLD(004F+2i)/MVI A,0A/?DLDOP`; deref-PUT tail `LHLD 004F/MVI A,0A/?DLDOP` @00ED–00F2 then A `0D`/B `02`/`?QDCOP` | `b03584edddfe` |
| NG18 (retired `N33_DEC_FORMAL`) | `r = g(1)` INT literal vs `dec(9,2)` formal | EXACT — POSITIVE specimen | 256 B | `0047` | `000C` | literal cell `00 01 00 00 00` + descriptor 000A→0000, ZERO caller arg code, peeled arity-1 prologue `SHLD 000C`; cmp rc=0 TWICE (fresh positional + markers harness); golden KEPT NEVER re-derived | `59cda824f4a8` |
| NG39 (retired `N52_DEC_FORMAL_PUT`) | `put skip list(q)` with `q` a `dec(9,2)` FORMAL | EXACT — POSITIVE specimen | 384 B | `005C` | `0016` | found BY THE FULL GATE (hop-11 rc=1 NEG-FAIL); cmp rc=0 re-measured fresh positional on `6db44394…`; caller literal cell `50 01 00 00 00` @0000, descriptor 000A→0000, return descriptor 0014→000A; callee deref-PUT `LHLD 0016/MVI A,09/?DLDOP` + `MVI A,0C/MVI B,02/?QDCOP` — third witness of the armed `9b81ed0` route; `.PRN` `NO ERROR(S)` both passes | `3197de7aa11e` |

## 3. Hypothesis verdicts (pre-registered in PLAN §3; every MISS kept verbatim)

- **H-1..H-8 ALL CONFIRMED — ZERO §4 prediction misses and ZERO falsifiers fired** (the first
  fully-hit panel of the P3 campaign so far): product block + window (ZA down `03/?QDDSR`, ZB
  up `02/?QDDSL`), cell width `dec_pool_bytes(pf) = floor((pf+2)/2)` with stride = width (ZA/ZF
  6 B, ZB 4 B, ZE 5 B), DSTOP `MVI A,pf`, direction from SCALES ONLY (Δp irrelevant), literal =
  static pre-scaled formal-width cell with ZERO caller code, ONE interleaved arg-ordered static
  vector, arity-dependent prologue (peeled-1 vs block-copy 2N) with [C094] formal reads
  UNCHANGED, and ZF = LOAN2 replication byte-for-byte.
- **The two MY-GAP repairs that the panel forced (honest, adjudicated by the goldens only, never
  fitted):** (i) `const_cells` — an `Enumber` DEC actual demanded a 2-byte cell while lowering
  allocated the 5-byte formal-width cell (E52ZC/ZD/ZE died at the C152 loud refusal); repaired by
  the SAME demand law `dec_pool_bytes(pf)` (`9b81ed0`). (ii) the DEREF'd DEC formal in `PUT LIST`
  (`put skip list(q);` inside the callee) — my build refused it BY NAME; the E52ZF golden pins it
  as `LHLD <formal cell>/MVI A,pf/?DLDOP` + the unchanged [R5xx] width/scale edit pair, so that
  arm was admitted on the ZF witness (`9b81ed0`); the old refusal text retired to a comment
  VERBATIM per PROTOCOL #2.
- **The [C093] correction (dated, in [C371], verified FIRST-HAND at claim time):** (i) the
  DECPOLY `*A(005A) = 5.67` literal-pool citation was FALSE AS CITED — all three DECPOLY goldens
  (sha `a51a36c2…`) have DATA max `004E`, their descriptor cells 0048/4A/4C relocate to VARIABLE
  cells 0030/38/40, and `5.67` exists only as the R2038 SOURCE `z = 5.67;` DEC-store; (ii) the
  "2-byte pool cell" width was wrong for DEC formals — the truth is the 5 B formal-width
  pre-scaled cell (NG18/ZC/ZD); C093's 2-byte cells were the R2033 INT-literal BIN-formal
  `pool_alloc` route. The literal-pool LAW itself STANDS with the new witnesses.

## 4. Arm, validation, registration, coverage

Arm `13e53be` (`ocaml/lib/bind.ml` + `ocaml/lib/codegen.ml`): bind's `cs_dec` is the SINGLE
allocation authority — a DEC expression temp is sized `bytes_of (RTdec(pf,sf))` ONLY for an
internal, non-recursive, non-attribute callee with a scalar `RTdec` formal (array-named,
recursive, external and attributed callees excluded); codegen admits ONLY the two measured
shapes — `Ast.Enumber` literal → the pre-scaled FORMAL-width `dec_pool` cell + static descriptor
RELOC, ZERO code; `Ebinary(Mul, plain-DEC-auto, plain-DEC-auto)` → the armed `dec_push` route via
ONE forward slot `dec_actual_mat` installed after `dec_push` (the `lower_hl`/`dpush` chains are
SEPARATE — the law was NEVER duplicated), terminating `LXI H,*A(temp)/MVI A,pf/?DSTOP`; `dec_pool`
MOVED before `lower_hl` (`vk_dec_at` precedent); everything else keeps the BY-NAME Line-N [TBD]
refusal VERBATIM (substring `FIXED DECIMAL formal is unproven` intact, [TBD] histogram codegen 68
/ total 124 == baseline after repairing the hop-8 W9/W39 regression — the predecessor's reported
"W9/W39" partial view was FALSIFIED as misleading incremental output, the true new warning was
the dead `zip3`, fixed in `e971f3e`).

Validation: whole-file cmp E52ZA..ZF **6/6 rc=0** FRESH POSITIONAL `build/p3-13/arm-out2/`; sweep
`E46N E46K E51 E52 P086 R10` **168/0** pre-registration, **174/0** post-registration, FAILS 0
binding — SWEEP-COUNT LESSON ACCEPTED: the inherited "159" contract number was STALE because the
sweep counts INVENTORY rows, which move with every registration; re-derive the expected count from
the inventory, never from a prose contract; DEC regressions `R5 R6 R7 R8 LOAN1` **64/0**;
markers **14/15** at hop 10 — the ONLY failing row was retired `N33` firing its old gate row, the
second NG18 witness (harness `.REL` cmp rc=0) — **14/14** at this close with N33 out; divergences
**9/9** via `build/p3-12/divcheck.py`; LOAN2/EXPR1/EXPR2 positional re-recorded (below).

**THE GATE-FOUND RETIREMENT (the binding lesson of this subround, kept VERBATIM).** The hop-11
FULL gate failed rc=1: `NEG-FAIL N52_DEC_FORMAL_PUT: compiled silently (must [TBD])`. The
sweep, markers and DEC-regression suites NEVER run the complete negative panel — **only the gate
does** — so an arm touching PUT/CALL lowering MUST be followed by a FULL gate BEFORE any close
claim. Adjudication measured THIS session, POSITIONAL FRESH: the retired inline gate source
materialized CRLF + bare `^Z` (sha256 `de1e56e8…`, 253 B — exactly the original `ng39.pli` size
in the campaign dir listing) compiles rc=0 to a 384 B object (`code=92 data=15`) with `cmp` rc=0
against the KEPT `golden/negpanel1/NG39/NG39.REL` (sha256 `3197de7a…`, NEVER re-derived); the
original `.PRN` reads `NO ERROR(S) IN PASS 1` and `NO ERROR(S) IN PASS 2`. N52 is the EXACT
retirement class of N33→NG18 / N35→NG20 / N26_DECDIV: REJECTS + NEG_META rows deleted WITH
retirement comments, registered as POSITIVE specimen `NG39`, refusals 187→**186** honestly, NO
invented replacement negative (N53's DEC-formal-conjunction route stays refused — DR behaviour
UNMEASURED). The discovery, re-measure and retirement are recorded as a DATED ADDENDUM INSIDE
[C371] (`016e58e0`), not silently.

Registration `601e20e1`: `--update-inventory` 1295/187 → **1296/186** (+1/−1 exactly, every diff
line inspected, staged set verified clean of config); census OWN path `42f3f659` re-snapshot at
the new HEAD, counts **15/0/26/0 UNCHANGED**, row data byte-identical — the LOAN2 message does
NOT move (the negative panel is not census; NOTHING was fixed). COVERAGE: `PROC.CALL_DEC_ACTUALS`
row `afb95163` (NEW row, so its `spec/COVERAGE-IDS.txt` line shipped in the SAME change —
IDENTITY invariant; `EXACT:7`) was EXTENDED at `c1059d46` with probe `NG39` to **EXACT:8** (row
count 144 UNCHANGED, IDS set UNCHANGED), boundary sentence recording the third deref-PUT panel
witness while the call-ACTUAL deref route stays refused BY NAME; plus the same-change DATED
labelled correction of the now-false final clause of `STOR.DEC_SCALE_ASSIGN` (original clause
kept VERBATIM inside the correction, PROTOCOL #2). `coverage_check` rc=0 **144 rows 0/0
SUPPORTED 94**; `file_prose_check` rc=0.

## 5. LOAN2 — ADVANCED and recorded, NEVER fixed

With the armed actual-materialisation laws, `artefacts/LOAN2.PLI` UNMODIFIED (sha `7be23ba3…`
re-verified at this close) lowers PAST Line-117/118 (the five product actuals — they are exactly
what ZF replicated) and dies at the ACTUAL next blocker — rc=2, NO `.REL`, VERBATIM (re-measured
POSITIONAL FRESH on `6db44394…` at this close):

`codegen: CALL target is not a simple procedure name [TBD] (only `CALL id` / `CALL id(args)` /
bare `id;` have a DR lowering sampled; line 121)`

Line 121 = `call summary();` — a ZERO-argument call whose target IS a simple name, so the
message's own parenthetical is suspicious on its face: this is P3-14's WHY-first investigation
target, NOT a fix. The Line-117 blocker is CLOSED. EXPR1 (GET 21) and EXPR2 (FLOAT 35)
UNCHANGED. LOAN2 is NOT claimed exact anywhere in this subround.

## 6. What P3-13 does NOT say (byte tier only)

- **Byte tier only**: nothing from e52p13 was linked or run; NO claim about what
  `?DMUOP/?QDDSL/?QDDSR/?DLDOP/?DSTOP/?QDCOP` DO inside PLILIB — only WHERE the calls sit and
  what A/B/C hold at the call; no `spec/RUNTIME.txt` row comes from this contract. Byte parity
  is not a semantics claim.
- **Perimeter KEPT, all refusals BY NAME**: add/sub/div-expression, suffix, pointer and
  deref'd-formal ACTUALS, external/recursive/attribute callees, array-named formals and narrowing
  actuals keep explicit [TBD] refusals; C371 claims NONE of them. The armed guard admits ONLY an
  `Enumber` literal or a single `Mul` of two plain DEC autos.
- **Repeated-literal cross-dedup demand is UNMEASURED** — the C152 loud refusal is the safety
  net; no dedup law is claimed.
- **The N52→NG39 retirement is a panel-classification fact, not a new law** — the deref-PUT bytes
  predated this round (E52ZF golden); what changed is that MY compiler reproduces them
  byte-exactly and the negative panel was re-adjudicated by the gate.
- LOAN2 is NEVER claimed exact; the Line-121 blocker is the ACTUAL recorded refusal text, not a
  diagnosis; **P3-14 proceeds ONLY evidence-first with pre-registration before any oracle call or
  `ocaml/` byte**. GOLDENS ARE EVIDENCE, NEVER RE-DERIVED; the operator's `handoff.config.json`
  was NEVER staged; no push.
