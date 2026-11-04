# E2E-52/P3 — LOAN2 progressive closure: campaign plan + subround P3-1 (bare PAGE)

Committed BEFORE any `ocaml/` byte of this round (PROTOCOL #1). Baseline: HEAD
`6c44d8d` (P2 close, g276 attested), compiler binary `85bf7a26…` (built rc=0 this
session, identical to the P2 registration gate), tree clean except the operator's
`handoff.config.json`. Historical baseline re-verified where cheap; full gate actuals
recorded below before promotion.

## Campaign objective

Compile `artefacts/LOAN2.PLI` (sha `7be23ba3…`, UNMODIFIED throughout) toward a
whole-file byte-identical `.REL` against `golden/first/LOAN2/LOAN2.REL` (sha
`712cfcb2…`, never re-derived). Loop per blocker: smallest reproducible construct →
search existing goldens/claims/probes → bounded oracle experiment only if evidence is
insufficient → smallest defensible fix → probe byte parity → focused regressions →
recompile LOAN2 → record advance. No special-casing of LOAN2; no invented boundaries.

## Subround P3-1 — PUT FILE with a bare PAGE control item

### 1. Measured blocker (reproduced verbatim, rc captured directly)

`pli80c artefacts/LOAN2.PLI` → rc=2,
`codegen: PUT FILE with a bare PAGE control item [TBD] (line 99) -- PAGE has DR's bytes
(E46N10, 0023-0034, CALL ?PAGOP after the attach) but no specimen of MINE, and LINE is
refused by DR itself (E46N21); SKIP is lowered`.

CLASSIFICATION: **my-gap** — DR ACCEPTS the shape (E46N10 golden; `spec/INVENTORY.txt`
E46N10 row, [E2E-42/P2c]). No new oracle call is needed: the DR side is measured.

ROOT CAUSE of why the message names 99 and not 54: the raise comes from the E2E-52/P1
LEXICAL PRESCAN (`prescan_stmt` → `match_put_list_lit` → `bare_ctl_put`), which walks
EVERY Sput before any lowering; LOAN2's `open ... print [pagesize(0)]` at 54/56 are
separate `open_mode_word` refusals (verified live on a scratch CRLF probe: `OPEN option
PRINT is outside what this compiler lowers`), currently masked behind the prescan stop.

### 2. The DR bytes (read out of the object, PROTOCOL #6 — `tools/reldump.py` on `golden/e42p2c/E46N10/E46N10.REL`, 384 bytes, CODE 0x3E=62, DATA 0x0A=10)

Statement at 0023-0034 (18 bytes):

    0023 21 <RELOC common 0x0000>          LXI H,*C(OUTF)
    0026 11 52 06                          LXI D,0652
    0029 01 <word 002A-002B>               LXI B,*CODE  (backpatched: LINK-SET-LC code
                                            002A + RELOC code 0x0035 -- continuation =
                                            the CLOSE statement at 0035)
    002C CD 0000  LINK-CHAIN-EXT code 002D ?SIOOP
    002F CD 0000  LINK-CHAIN-EXT code 0030 ?PAGOP       <- the PAGE, NO count operand, NO MVI
    0032 CD 0000  LINK-CHAIN-EXT code 0033 ?QIOOP

Corpus corroboration: COPYLPT:53 `put file(printfile) page;` = the same 18 bytes behind
a PRINT open (0215-0226; `predict_p2c.py` self-test span `COPYLPT:53 = 18`). E46N1
(bare SKIP, byte-exact panel specimen) is 20 bytes — PAGE differs from SKIP exactly by
`MVI A,01` being ABSENT and `?SKPOP` being replaced by `?PAGOP` (E46N1 CODE 64 vs E46N10
CODE 62). This is why PAGE is a distinct control KIND, not an encoded skip.

### 3. Boundaries KEPT (no witness → refusal by name; none of these is licensed by E46N10)

- `PAGE(n)` / `PAGE(expr)` on a file PUT: unmeasured (manual shows `PAGE[(p)]`, no
  object carries a count) — stays refused as `the control item PAGE with a count` via
  the ordinary `file_items` item message; the **E46N21 marker substring** `control item
  LINE with a count, unmeasured on the named-file route [TBD] (line 12)` stays alive.
- PAGE + items on a file PUT (`put file(f) page list('A')`): unmeasured; refuses BY NAME.
- Non-leading PAGE: unmeasured position (same positional law as [C304]); refuses.
- CONSOLE `put page`: unmeasured (N3_PAGE negative panel row, marker `PUT form`, my-gap
  per golden/negpanel1/NG25); the file fix must NOT route console PAGE anywhere.
- The routing invariant [C300]: a PUT naming a file never falls through to the console
  helper; the `file_out` guard of the `Pfile` arm is unchanged (E46N10 opens with the
  lowered `stream output title(<literal>)`).

### 4. Predictions (before any compiler byte)

P1. `pli80c probes/E46N10.PLI` whole-file `cmp` vs the golden: **rc=0, 384 bytes,
    byte-exact FIRST TRY** (mine sha == golden `e…` sha recorded after the fact).
    CODE 62, DATA 10. Bytes/relocs exactly §2 above; ?PAGOP appears in my LINK stream
    for the first time as a LINK-CHAIN-EXT at 0030, name-only, no push.
P2. Regression zero-drift: E46N1..N9, N11..N19 whole-file cmp each rc=0 unchanged;
    full gate 1196/0 before registration; negative panel 181/181 INCLUDING N3_PAGE and
    E46N21 with the pinned markers; divergence 9/9; coverage 139 rows 0/0; prose 5.
P3. Census: COPYLPT's refusal MOVES off the PAGE message (its PAGE now lowers; expected
    next COPYLPT stop is its OPEN-attribute/ENVIRONMENT surface or a later unlowered
    construct — record the ACTUAL message); LOAN2's refusal moves PAST line 99 —
    predicted DIRECTION: next stop at/after the OPEN PRINT lines 54/56 (a `OPEN option
    PRINT is outside` class refusal) unless the prescan hits another unlowered construct
    earlier; record ACTUAL verbatim, do not fix it this subround. LOAN2 is NEVER claimed
    exact.
P4. Registration: SPECIMENS +1 (E46N10), REJECTS −1, `--update-inventory` 1196→1197
    (diff exactly ONE line flips from refusal to specimen), post-reg gate rc=0 1197/0.

### 5. Progress table (cumulative index; detail lives in claims/RESULTS)

| Subround | Initial blocker | Evidence | Compiler change | Exact specimens | LOAN2 outcome |
|---|---|---|---|---|---|
| P3-1 | `PUT FILE bare PAGE [TBD] (line 99)` | E46N10 golden + COPYLPT:53 (existing [E2E-42/P2c]); claim **C359** | arm `adb749c`: codegen `Sk_page` kind + bare `CALL ?PAGOP` on the file route ONLY (B1–B7; warning profile identical) | **E46N10 panel-EXACT** (cmp rc=0 FIRST TRY, 384 B, sha `75557545…`; sweep 18/18; INVENTORY 1197; gate rc=0 1197/0, negatives 180/180 — retire removed one row, 181/181 FALSIFIED) | MOVED PAST 99 — ACTUAL `codegen: PUT EDIT deferred [TBD] (line 115; only PUT LIST is implemented; format/picture editing needs the ?EDITF/?EDTOV/?QDDSL route family)` rc=2; OPEN-PRINT-at-54/56 FALSIFIED by stage (prescan dies first), direction clause held; **P3-2 target = PUT EDIT 115** |
| P3-2 | `PUT EDIT deferred [TBD] (line 115; …)` | EXISTING goldens `golden/probe55/P086K.REL`+`P086J.REL` + LOAN2.REL spans (PLAN §2 pre-registered); claim **C360** | arms `a51fb93` (file PUT+GET EDIT route, codegen-only (a)-(g); `?EDTIV` new name) + `2686bcc` (pool-PARTITION record-order fix: prealloc tables before the COMMON group, lowering blocks after; only the measured shape reorders, else RAISE BY NAME) | **P086K + P086J panel-EXACT** (J cmp rc=0 FIRST TRY 256 B; K rc=1 at octet 32 then rc=0 512 B after the order fix — the +3-bytes diagnosis FALSIFIED, pure record ORDER; sweep 75/75; negatives 179/179 after the E41X8 retire `ff1c8f2` MEASURED rc=0, bytes never claimed; INVENTORY 1199 EXACTLY TWO lines; gate rc=0 **1199/0** `build/gate-e52p3b-reg.log`) | MOVED PAST 115 — ACTUAL verbatim `codegen: PUT EDIT format item form unsampled [TBD] (counted, grouped, picture, remote and rep-group formats are not decoded)` (fmt_spec catch, NO line number — as predicted); **P3-3 target = picture `02`-record decode** (operands `04 00 05` UNDECODED) |
| P3-3 | `PUT EDIT format item form unsampled [TBD] (counted, grouped, picture, remote and rep-group formats are not decoded)` | NEW campaign e52p3: 15 probes E52PA..PO pre-registered `eef371b` BEFORE any ocaml/ byte; oracle `8edea80` 14 ok/15 (E52PF **dr-refuses** PICTURE ? NO .REL; no-scale-agreement 3x falsified the scale expectation); goldens `aae0f37`; claim **C361** | arm `d088cdb`: ONE `Ast.Pi_pic` branch in fmt_spec emitting `02 b1 b2 len UPPER(text)`; b1=count{9,Z,$}-1-if-$; b2=count{9,Z} after LAST V (HE — HC and HD FALSIFIED by E52PJ 9.9->00); guards refuse BY NAME | **13/13 accepted probes panel-EXACT** (cmp rc=0 whole-file — P5's 4-probe subset an UNDERCLAIM, falsified; PB..PE,PG..PL,PM,PN,PO; PA refuses my-gap, PF dr-refuses row); sweep 75/75; P086J/K rc=0; INVENTORY 1212 (+13 specimens, +1 refusal); gate rc=0 **1212/0** `build/gate-e52p3c-reg.log`; COVERAGE EXACT:25 | UNCHANGED VERBATIM — same fmt_spec catch text (P6 HIT), now firing on grouped/rep-group 147/149 while still listing \"picture\" (message-quality my-gap, never fitted); **P3-4 target = rep-groups + x(w) + file EXPRESSION item** |

## Subround P3-2 — PUT/GET FILE EDIT (LOAN2:115 blocker)

### 1. Measured blocker (verbatim, at HEAD after P3-1)

`codegen: PUT EDIT deferred [TBD] (line 115; only PUT LIST is implemented; format/picture
editing needs the ?EDITF/?EDTOV/?QDDSL route family)` rc=2. Statement 115-116 (data/format
REVERSAL accepted, see LEARNINGS 59f9afa): `put file(output) skip edit('|',100*m+y) (a,p'99/99');`.

### 2. The DR bytes (all from EXISTING goldens; reldumps in ignored build/e52p3/)

**`golden/probe55/P086K/P086K.REL`** (512 B, CODE 0x62=98, DATA 0x12; probe `dcl f file, d
fixed dec(5,2); d=1.5; put file(f) edit(d)(f(5,1)); get file(f) edit(d)(f(5,1));` NO open):
pool *S(0000)=`80 00 00 05 01 81` (put table), *S(0006)=identical (get table), DEC literal
`50 01 00`@000C, d cell 000F. PUT 0016-003C: `LXI H,*C / LXI D,0652 / LXI B,*CODE(003D) /
CALL ?SIOOP@0020 / LXI H,*S(0000) / CALL ?EDITF@0026 / LXI H,d / MVI A,05 / CALL ?DLDOP@002E /
MVI A,08 / MVI B,02 / CALL ?QDCOP@0035 / CALL ?EDTOV@0038 / CALL ?QIOOP@003B`. GET 003D-0061:
attach `LXI D,0690 / ?SIOOP@0047`, `LXI H,*S(0006) / ?EDITF@004D / CALL ?EDTIV@0050` (NEW
routine name), `MVI B,02 / ?QCDOP@0055 / LXI H,d / MVI A,05 / ?DSTOP / ?QIOOP@0060`; NO GNVOP/JP.

**NEW THIS SESSION — `golden/probe55/P086J/P086J.REL`** (256 B, CODE 0x3D=61, DATA 0x10;
console `put edit(d)(f(9,2), a(4))` with `d fixed decimal(7,2)`): PUT 001F-0036 = `LXI H,*S(0000)
/ ?EDITF / LXI H,*S(000C) / MVI A,07 / ?DLDOP / MVI A,0A / MVI B,02 / ?QDCOP / ?EDTOV / ?QIOOP`
— the DEC-item prep is IDENTICAL in law to P086K (p, p+3, s); console EDIT has NO ?SIOOP attach.
Table `80 00 00 09 02 03 04 81` pins record kinds: header `80 00`; **f(w,d)=`00 w d`**;
**a(w)=`03 w`**; **a=`03 FF`**; terminator `81`.

**`golden/first/LOAN2/LOAN2.REL`** (whole-file witness; statement decode completed this session):
all SEVEN EDIT tables agree record-for-record with their source format lists; additional kinds
decoded but NOT armed: **x(w)=`0B w`** (0B 0F/10/13/06/09 vs x(15)/x(16)/x(19)/x(6)/x(9)),
**picture=`02 A B len text`** (len=text length; A/B operands UNDECODED), **rep-group=`80 n … 81`**
nested (147 `80 02 80 02 … 81 … 81 81`). Stmt 199 (`6 strings (a)` = pure measured subset):
08F1 `?SIOOP`, `MVI A,01 / ?SKPOP`@08F7, `LXI H,*S(0098) [80 00 03 FF 81] / ?EDITF@08FD`,
6×(`LXI H,*S(lit) / MVI A,len / ?SLCTS / ?EDTOV`) literals 024C(7) 0253(15) 0262(15) 0271(12)
027D(15) 028C(15), `?QIOOP`@0942. Six items vs ONE format record: the cycle is RUNTIME (?EDITF),
no extra codegen bytes. Stmt 212 DATA rep-group compiles to an INLINE DO LOOP (counter cell
*D 0358, STA/LDA/ADD/JC chain 0975-0999) — distinct class, stays refused.

### 3. Arm (P3-2a, `ocaml/lib/codegen.ml` ONLY; every byte above is measured)

A1 `match_put_edit`: grow to accept `on_opts = [FILE e]` (plus optional leading
`Pi_ctl("SKIP",None)` -> `Sk_lit 1`, the E46N1 law) alongside the console shape; return the
file expr. Prescan (`~3324`), `edit_stmts`/`prealloc_fmt_tables` consume it — file EDIT tables
enter the SAME fmtq FIFO in SOURCE order (P086K pins put-table@0000 BEFORE get-table@0006).
A2 NEW `match_get_edit` + walk: file GET EDIT, DEC-variable items only; prealloc shares the FIFO.
A3 `lower_put_items_gen`: DELETE the `is_edit && file <> None` guard (premise falsified: file
tables ARE measured); the existing prologue emits attach 0652 + skip + EDITF + items + QIOOP
already in the golden order. Item arms admitted on the file EDIT route: PIlit (SLCTS+EDTOV,
LOAN2 115/199), Vdec var (P086J+P086K+P086K-prep). Console Vdec: DELETE the `is_edit` refusal in
the Vdec arm (premise "no DR sample" falsified by P086J) — the existing `MVI A,p/?DLDOP/MVI
A,p+3/MVI B,s/?QDCOP` + `tail` = exactly the golden bytes.
A4 file GET EDIT lowering: `LXI H,<CB> / LXI D,0690 / LXI B,<cont> / ?SIOOP` then `LXI
H,*S(table) / ?EDITF / ?EDTIV` then per-DEC-item `MVI B,s / ?QCDOP / LXI H,var / MVI A,p /
?DSTOP` then ONE `?QIOOP`; `?EDTIV` is a new `call_ext` name only, NO new encoder.
A5 file EDIT attaches WITHOUT an open (P086K [C282]): the `st.file_out` guard does NOT run on
this route; the file must still be a declared FILE name (file_group).

### 4. Boundaries KEPT (refuse BY NAME; no witness or no panel-testable statement)

picture `02` record, `x(w)` `0B`, rep-groups (`80 n`/`81`), counted SKIP, PAGE+EDIT — fmt_spec
catch (existing message names picture/grouped/counted); DATA rep-group items and remote formats;
numeric-LITERAL items under EDIT (existing refusal); FLOAT/bit/member/struct items; DEC FORMAL
items (deref route, LOAN2 147 later); fixed-bin EXPRESSION items on the FILE EDIT route (pinned
inside LOAN2's own golden but never panel-isolable: the whole statement refuses on its picture
first); every existing console non-EDIT refusal and the E46N21/E46N10 law stay untouched.

### 5. Predictions (pre-registered BEFORE any ocaml/ byte)

P1. P086K: `pli80c probes/P086K.PLI` whole-file `cmp` rc=0 vs golden, FIRST TRY; 512 B, CODE
0x62, DATA 0x12; my LINK stream carries `?SIOOP ?EDITF ?DLDOP ?QDCOP ?EDTOV ?EDTIV ?QCDOP
?DSTOP ?QIOOP` (EDTIV first appearance).
P2. P086J: console DEC edit cmp rc=0 FIRST TRY; 256 B, CODE 0x3D, DATA 0x10.
P3. Zero drift: E46N sweep 18/18; R10xx + E46K4/K15 + E52A..J + E51A..L + console EDIT bank
byte-exact; `dune build` rc=0 with the SAME warning profile.
P4. Focused refusals rc=2, messages name the class: picture/x/rep/PAGE+EDIT/numeric-literal/
DEC-formal; **LOAN2 rerun STILL refuses at line 115 via the fmt_spec catch naming the picture
format** (the data/format reversal means the picture is reached before any item question); record
the message VERBATIM.
P5. E41X8 (`open … stream output title('X Y')` + file PUT EDIT DEC item): compiles rc=0 (no
golden exists — never claim its bytes); retire from REJECTS + delete NEG_META as written history
(E46K1/K3 convention) -> negatives 180 -> 179.
P6. Registration: SPECIMENS +P086K +P086J; `--update-inventory` 1197 -> 1199, diff EXACTLY TWO
lines; post-reg FULL gate rc=0 1199/0; census re-snapshot via its own write path (LOAN2/COPYLPT
messages move — record verbatim); COVERAGE `IO.PUT_EDIT` row (line 65) updated AFTER the MEASURED
DISCREPANCY is verified (it cites IFACT/LOAN1 as picture witnesses — LOAN1 has NO edit
statement; check what N12_EMPTYFIX/IFACT actually hold before touching the row); claim C360
derived ONLY from the §2 bytes.

## Subround P3-3 — picture `02` record decode (operands b1/b2; LOAN2 fmt_spec catch)

### 1. Measured blocker (verbatim, at HEAD after P3-2; census/`## Blockers` record)

`codegen: PUT EDIT format item form unsampled [TBD] (counted, grouped, picture,
remote and rep-group formats are not decoded)` — the `fmt_spec` catch-all
(`ocaml/lib/codegen.ml:2861`), NO line number; reached for LOAN2 stmt 115's
`p'99/99'` from BOTH the prescan and lowering (they share `fmt_table_bytes`).
CLASSIFICATION **my-gap**: DR compiles LOAN2 and every picture shape below.

### 2. The DR bytes (ALL from EXISTING goldens; measured at d9b0a2c; `tools/reldump.py`; re-dumps in ignored build/e52p3/{ANNUITY,DEPREC}-golden-reldump.txt; goldens untouched)

Record shape `02 b1 b2 len UPPER(text)` — 13 instances / 12 distinct texts:

| text | len | b1 | b2 |
|---|---|---|---|
| `99/99` (LOAN2 116) | 05 | 04 | 00 |
| `99` (LOAN2 179) | 02 | 02 | 00 |
| `b99v.99` (195) | 07 | 04 | 02 |
| `$zzz,zz9.v99` (150) | 0C | 08 | 02 |
| `$zz,zzz,zz9v.99` (149) | 0F | 0A | 02 |
| `$$$,$$$,$$9V.99` (179) | 0F | 0A | 02 |
| `$$$,$$$,$$$V.99` (ANNUITY 56) | 0F | 0A | 02 |
| `$$,$$$,$$$V.99` (ANNUITY 66) | 0E | 09 | 02 |
| `ZZZ9` (ANNUITY 78) | 04 | 04 | 00 |
| `B$$,$$$,$$9.V99` (DEPREC 232) | 0F | 09 | 02 |
| `B99` (DEPREC 233) | 03 | 02 | 00 |
| `$Z,ZZZ,ZZ9V.99` (DEPREC 253/282, TWO tables) | 0E | 09 | 02 |

- **len** = text character count (12/12); lowercase sources stored UPPERCASED (5x).
- **b1 FALSIFIED as count{9,Z}** by the three multi-`$` rows (e.g. `$$$,$$$,$$$V.99`:
  digits=2, measured 0A). Surviving rules, both fitting 12/12:
  **HA2** = count{9,Z,$} − (1 if any `$`); **HB8** = count{9,Z} + count of `$` NOT at
  index 0. They AGREE on all existing data and DISAGREE only on non-leading `$` —
  E52PF (`p'9$9'`: HA2→02, HB8→03) SETTLES.
- **b2** candidates indistinguishable on existing data: **HC** = digits {9,Z} after the
  LAST designator {.,V}; **HD** = count{V,.}. Discriminators E52PK (`p'9V.9'`: HC→01,
  HD→02) and E52PL (`p'99V.999'`: HC→03, HD→02). E52PJ (`p'9.9'`: HC=HD=01; b2=00 would
  prove the COMMA is also a designator — third falsifier).
- **Item preparation is FORMAT-INDEPENDENT** (LOAN2 195 span 0895-08CE): a DEC var under
  a picture-carrying list carries the SAME `MVI A,p / ?DLDOP / MVI A,p+3 / MVI B,s /
  ?QDCOP / ?EDTOV` law (p=4 for dec(4,2)); literals `MVI A,len/?SLCTS/?EDTOV`; the arm
  adds RECORD BYTES ONLY, no item-code change.

### 3. Probes (E52PA..E52PO; CRLF + bare ^Z, ≤71 cols; generator kept at ignored build/e52p3/mkprobes.py; ONE grouped campaign `PLI_SRC=probes timeout 900 python3 oracle/batch.py E52PA..E52PO --tag e52p3 --switches '$L$D'`; tag VERIFIED unused; names collision-grepped clean in probes/ and spec/INVENTORY.txt)

Per-probe PREDICTED format-table bytes (hex; `a`=`03 FF` per P086J; predictions state the
MEASURED-law options explicitly where a hypothesis is unsettled):

| Probe | Route / data / format | Predicted table |
|---|---|---|
| E52PA | file skip; `'\|',100*m+y`; `a,p'99/99'` (EXACT 115 mirror) | `80 00 03 FF 02 04 00 05 39 39 2F 39 39 81` (14 B) — EVIDENCE ONLY: PInum item NOT armed at P3-3; PA bytes NEVER claimed (P3-4) |
| E52PB | console; same items; `a,p'9'` | `80 00 03 FF 02 01 00 01 39 81` (10 B) |
| E52PC | `a,p'999'` | `80 00 03 FF 02 03 00 03 39 39 39 81` (12 B) |
| E52PD | `a,p'zz9'` | `80 00 03 FF 02 03 00 03 5A 5A 39 81` (12 B; uppercase storage re-check) |
| E52PE | `a,p'$$9'` | `80 00 03 FF 02 02 00 03 24 24 39 81` (12 B; HA2=HB8=02; digits-only rule would give 01) |
| E52PF | `a,p'9$9'` | HA2: `80 00 03 FF 02 02 00 03 39 24 39 81`; HB8 variant: b1=03 — SETTLES b1 |
| E52PG | `a,p'9',p'99'` (two pictures) | `80 00 03 FF 02 01 00 01 39 02 02 00 02 39 39 81` (16 B; consecutive 02 packing) |
| E52PH | `a,p'$$$,$$$,$$9V.99'` (control) | `80 00 03 FF 02 0A 02 0F 24 24 24 2C 24 24 24 2C 24 24 39 56 2E 39 39 81` (24 B; reproduces LOAN2-179 record isolated) |
| E52PI | console; `d` alone; `p'99V.99'` (scale match) | `80 00 02 04 02 06 39 39 56 2E 39 39 81` (12 B) — ARMABLE |
| E52PJ | `p'9.9'` (scale-mismatch risk) | `80 00 02 02 01 03 39 2E 39 81` (10 B); b2=00 falsifier = comma-as-designator; dr-refuse on scale is ACCEPTABLE data |
| E52PK | `p'9V.9'` (HC/HD decider) | `80 00 02 02 [01 HC \| 02 HD] 04 39 56 2E 39 81` (11 B) |
| E52PL | `p'99V.999'` (HC/HD decider) | `80 00 02 05 [03 HC \| 02 HD] 07 39 39 56 2E 39 39 39 81` (14 B) |
| E52PM | console picture-ONLY first record `p'9V.99'` | `80 00 02 03 02 05 39 56 2E 39 39 81` (12 B; 02 flush against header) — ARMABLE |
| E52PN | FILE picture-only `edit(d)(p'9V.99')` | same 12 B table; attach 0652/?SIOOP, NO skip — ARMABLE |
| E52PO | FILE skip mirror of 115 with `d` for the expression: `('\|',d)(a,p'9V.99')` | `80 00 03 FF 02 03 02 05 39 56 2E 39 39 81` (14 B) — ARMABLE |

DEC item law predicted in code for PI..PO items: `LXI H,*S(table) / ?EDITF /
LXI H,d / MVI A,04 / ?DLDOP / MVI A,07 / MVI B,02 / ?QDCOP / ?EDTOV / ?QIOOP`
(p=4, p+3=7, s=2 — [C360] law); file probes attach `LXI D,0652/?SIOOP`, PO additionally
`MVI A,01/?SKPOP` (E46N1 bare-skip law); console probes have NO attach.

### 4. Arm (after measurement; `ocaml/lib/codegen.ml` ONLY)

ONE new `fmt_spec` branch `Ast.Pi_pic s -> 0x02 :: b1 :: b2 :: len :: UPPER(text)`, with:
- b1/b2 computed by the rules MEASURED at PF/PK/PL (pre-registered intent: HA2/HB8 → use
  the settling value; HC/HD → use the settling value);
- GUARD: any picture char outside {9,Z,$,V,.,B,comma,slash} RAISES BY NAME (unsampled
  picture character); non-leading `$` armed ONLY if E52PF measures it accepted;
- the existing catch-alls (counted SKIP/PAGE, other operators, grouped/rep/remote) stay.

### 5. Boundaries KEPT (refuse BY NAME; NOT licensed by any P3-3 measurement)

rep-groups `80 n … 81` and grouped `2(...)`; `x(w)` `0B` (decoded, not armed); remote
formats; counted SKIP/PAGE; DATA rep-groups; DEC FORMAL (deref) items; fixed-bin
EXPRESSION items on the FILE EDIT route (PA stays evidence); FLOAT/bit/member items;
picture characters outside the measured set; every E46N21/E46N10/P086* law untouched.

### 6. Predictions (pre-registered BEFORE any ocaml/ byte)

P1. Oracle campaign: all 15 probes classified; expected ACCEPTED (`.PRN NO ERROR(S)` both
    passes) EXCEPT possibly E52PJ/PK/PL scale-mismatch `dr-refuses` — classified as
    measured DR scale law; a SECOND bounded batch is allowed iff PH/PL die on scale AND
    HC-vs-HD stays undecided (pre-registered exception).
P2. E52PF settles b1 (HA2 → 02; HB8 → 03); E52PK/PL settle b2 (HC vs HD); E52PD re-proves
    uppercase storage; E52PG proves plain record concatenation with no inter-record padding.
P3. Arm: `dune build` rc=0, warning profile IDENTICAL to `build/e52p3/arm-build-warnings.log`
    histogram method; every predicted table byte in §3 realized for the ACCEPTED probes.
P4. Zero-drift sweep: E46N 19/19, E52A..J 10/10, E51A..L 12/12, R10 bank 34/34, P086J/P086K
    cmp rc=0; boundary markers E46K4/E46K15/E46N21 intact rc=2.
P5. Whole-file cmp rc=0 vs NEW goldens for every armable ACCEPTED probe (candidates PI,
    PM, PN, PO; PJ/PK/PL join iff accepted AND items armed); PA/PB..PH NOT cmp-predicted
    (bin-expression item class stays refused → rc=2 BY NAME, message names the class).
P6. LOAN2 rerun VERBATIM: the SAME fmt_spec catch-all text must fire EARLIER-or-the-same;
    predicted next stop = the rep-group at stmts 147/149 (`2(2(...))` in the P086K-era
    decode) reached via the prescan order — i.e. the message stays VERBATIM identical
    (static string, still listing "picture" even though pictures arm now — a message-quality
    my-gap, recorded, never fitted); NEVER claimed exact.
P7. Registration: SPECIMENS += every new probe whose whole-file cmp is rc=0 (measured set);
    `--update-inventory` +N lines EXACTLY; FULL gate rc=0 to build/gate-e52p3c-reg.log;
    census via own write path; claim **C361** from MEASURED bytes ONLY, committed BEFORE
    the COVERAGE rewrite of `IO.PUT_EDIT` (cite-resolution lesson); coverage_check rc=0;
    prose rc=0.
