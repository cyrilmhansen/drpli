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
