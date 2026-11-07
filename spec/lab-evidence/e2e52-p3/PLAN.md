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
| P3-4 | `PUT EDIT format item form unsampled [TBD] (counted, grouped, picture, remote and rep-group formats are not decoded)` | NEW campaign e52p3d: 11 probes E52PP..PZ pre-registered `3ac7f41` BEFORE any ocaml/ byte; oracle 9 ok/11 (**E52PU bare-x dr-refuses `SYNTAX ?`**, **E52PV x(255) dr-refuses `BAD VAL`** — both NO .REL; x(128)/x(0) compile-accepted by the same listing, bytes unmeasured); goldens + reldumps; claim **C362** | arm (codegen.ml ONLY): `fmt_spec` → `let rec`, `Ast.Pi_repgrp` (NOT `Pi_rep` — brief wording falsified) → `80 n…81` recursive with **count-1 SPLICE** (H2a/H2b FALSIFIED, H2c CONFIRMED) and count-0 refused; `X(w)` → `0B w` for literal w ≤ 128 only, bare-x refuses naming PU; `authorize_file_edit_item` admits `PInum` via the new `edit_num_tree/edit_num_cell/edit_num_lit/edit_num_operand` shape authority (+/- over cells, lit×cell, cell/lit). PA crash root cause = UNPARENTHESISED inner match in `edit_num_cell` swallowing the outer wildcard (`-warn-error -a` = warnings NOT fatal; warning delta 74-vs-70 was the fingerprint), fixed `9b2d781` | **10/10 panel-EXACT** — 9 NEW goldens cmp rc=0 FIRST TRY + **PA cmp rc=0 vs the EXISTING `golden/e52p3/E52PA` (sha `d7b4e7f3…`) = HEADLINE, never fitted** (span 0032-0047 == LOAN2 0544-0558 byte-for-byte; H6a FALSIFIED — `?IM22N` leaves the product in HL, NO XCHG when the product is the whole item; H6b CONFIRMED); sweep **89/89** (R10 bank is 33 rows — the \"34\" count was a slip); INVENTORY 1212→**1222** (+10 specimens) and 180→**182** (PU/PV dr-refuses rows); gate rc=0 **1222/0** `build/gate-e52p3d-reg.log`, census counts UNCHANGED 15/0/26/0 with the 3 predicted msg moves; COVERAGE EXACT:35 | **ADVANCED VERBATIM** past the fmt_spec format catch to `codegen: PUT FILE(OUTPUT) EDIT shape [TBD] (line 212) -- an EDIT list the matcher cannot split…` rc=2 (prescan matcher-split); the predicted DEC-FORMAL-at-147 blocker is **FALSIFIED AT STAGE LEVEL** (the prescan never reaches 147), direction held; recorded `my-gap`, NOT fixed; **P3-5 targets = the live refusals** (line-212 matcher shape, DEC formal/deref + numeric-literal + PIvar-bin-var items, counted SKIP/PAGE+EDIT, format-COUNT expressions, group count 0, x-widths 14..128 object gap) |
| P3-5 | `PUT FILE(OUTPUT) EDIT shape [TBD] (line 212) -- matcher cannot split` | pre-reg `67e5414`; campaign e52p5 9 ok/10 at `676fb9d` (E52RE dr-refuses NO .REL; E52RC BY + E52RG char-var DR-ACCEPTED, boundaries KEPT); goldens `golden/e52p5/` | arm `aeda739` (parser REPSPEC child0=index Eident + BY parse refusal; codegen PIrep + data-walker both routes + prescan cells-ONCE + authorizer PIlit/PInum-inner + named emit_item §2 loop); hop-9 defensive arms `a008840` (prescan-fold PIrep arm, histogram 70->68 = -2 W8 at the fixed site) + `3a494c3` (named REVERSE refusal; `expected )` marker prediction FALSIFIED, panel needs [TBD]) | **7/7 cmp rc=0** RA RB RD RF RH RI RJ on clean binary `e55e892c346741b2` (H1/H2/H3/H6 CONFIRMED; RB patch law: non-final JP -> next item, final -> close ?QIOOP); sweep 101/0; gate **1229/0**, 183/183; inventory +7/+1; claim **C363** measured-bytes-only BEFORE COVERAGE EXACT 35->42 (`2be56f0`) | **ADVANCED VERBATIM** past 212 to `codegen: ON UNDEFINEDFILE is not implemented [TBD] (only ENDFILE(<file>) has a DR lowering; line 44)` — prescan now clears ALL statements; the line-177 PIvar prediction FALSIFIED at stage level (lowering dies at 44 first); my-gap, NOT fixed; NEXT candidate P3-6 = ON UNDEFINEDFILE (line 44) — NEW ground, first PLAN §P3-6 + probes BEFORE any ocaml/ byte |
| P3-6 | `ON UNDEFINEDFILE is not implemented [TBD] (line 44)` | pre-reg c946839 (PLAN §P3-6 + probes E52SA..SG BEFORE any ocaml/ byte); campaign e52p6 5 ok/7 (SF/SG dr-refuses NO .REL; SE accepted UNARMED) | arm 8fc0a3b (bind.ml Rk_on for block-handler trailing goto, Sdobegin AND nameless Sproc/Bbegin; codegen on_reg_prefix 05/06, inline no-RET handler) | **4/4 cmp rc=0** SA SB SC SD whole-file on binary 0efc35e6d4ff81bd (H1-H4 CONFIRMED; SC independent-target discriminator; SA octet-142 MISS -> branch-boundary reload law; sweep 110/0; falsified: Sdobegin-shape brief, sweep-101 undercount); gate **1233/0**, 186/186; inventory +4/+3; claim **C364** 73b9c53 BEFORE COVERAGE EXACT 14->18 6e6ed37 | **ADVANCED VERBATIM** past 44 to `codegen: OPEN option PRINT is outside what this compiler lowers [TBD] (line 54)` (prediction HIT, NOT fitted); SE REVERT stays measured my-gap; NEXT candidate P3-7 = OPEN PRINT / PAGESIZE / LINESIZE from line 54 |
| P3-7 | `OPEN option PRINT is outside what this compiler lowers [TBD] (line 54)` | pre-reg `2bca084` (PLAN §P3-7 + probes E52TA..TJ BEFORE any ocaml/ byte; class decoded from EXISTING OPEN-BLOCKS/OPEN-MATRIX/W1-BITFIT); campaign e52p7 **10 ok/10, ZERO dr-refuses**, goldens VERBATIM `272a996`; claim **C365** | arm `ccf0036` (codegen.ml ONLY): `open_subset_keys` +PRINT/PAGESIZE/LINESIZE; PRINT base 0x0652/0x0E52 behind print+INPUT/print+OUTPUT guards; `open_attr_plan` measured matrix, everything outside refuses BY NAME; ONE `open_emit_words` ladder in all three title branches | **10/10 whole-file cmp rc=0** on binary `8b374e623bc9e280…`; H1–H5 CONFIRMED, H6 refused-as-designed; TI falsifier TRIGGERED (`60 68` not `21 00 00`) and TG/TH 30-B totals FALSIFIED (measured 32/33 B, encodings HIT) — all kept VERBATIM; TJ DR-ACCEPTED via `21 2C 01`; sweep **114/0**; inventory 1233→**1243**; gate **1243/0**, 186/186; `a6e814f` C365 BEFORE COVERAGE `d9ebb30` (NEW row FILE.OPEN_PRINT_ATTRS EXACT:10; 140 rows 0/0) | **ADVANCED VERBATIM** past 54/56 to `ON ERROR is not implemented [TBD] ... line 58` (§6 prediction HIT, NOT fixed); RETRIEVE advanced past its line-19 title-print open to `OPEN option ENVIRONMENT ... (line 31)` — a real advance, no claim; NEXT candidate P3-8 = ON ERROR (LOAN2:58), NEW ground |
| P3-8 | `ON ERROR is not implemented [TBD] (only ENDFILE(<file>) and UNDEFINEDFILE(<file>) have a DR lowering; line 58)` | decoded FIRST from FIVE pre-existing witnesses (LOAN2 00E8, ANNUITY 004B, COPYLPT 00A6, EXPR1/EXPR2 001B — `build/e52p8/onregions.txt`, bitstream disassembly, ZERO oracle in hops 1–2); pre-reg `e6d16ff` (PLAN §P3-8 H1–H6 + probes E52UA..UF BEFORE any `ocaml/` byte); campaign e52p8 **6 ok/6, EVERY prediction HIT, ZERO dr-refuses**; goldens VERBATIM `9f36504`; claim **C366** | arm `a7ab5a4` (codegen.ml ONLY): NEW `on_error_reg_prefix` beside `on_reg_prefix` (file encoder untouched) — ABSOLUTE `LXI H,<arg LE>` / `XRA A` / `CALL ?ONCOP` / `C3 slot` = 10 B; a file-less object has NO COMMON group / NO `SEL-COMMON` record and the argument operand carries NO relocation (only the `?ONCOP` chain and the jump-over `RELOC code` patch it); admits bare + ONE integer literal 0..65535 and ONLY the four measured handler shapes; BODY-DEPENDENT tail (`C9` suppressed iff the handler's last statement transfers unconditionally — goto [C364], stop on the ENDFILE route per UF); everything else refuses BY NAME [TBD] | **6/6 whole-file cmp rc=0** on clean binary `9ecea27aa4f2d80f49ad…` (UA 128 B/0020/0002, UB 256/0030/0004, UC 256/0046/0008, UD 128/0020/0002, UE 256/002B/0002, UF 384/002F/0002 + COMMON F,G 0023); H1–H6 all CONFIRMED, no pre-registered falsifier fired; my FIRST DRAFT falsified in-house (stop branch omitted the shared registration → UF MISS at octet 150, 5/6); histogram 68 == baseline; sweep 124 specimens **FAILS: 0** + 21 named refusals; markers E46K4/K15/N21/E52PF/PU/PV/RE + SE/SF/SG rc=2 **MARKER_FAILS: 0**; inventory 1243→**1249** (+6 exactly, refusals 186); gate rc=0 **1249/0** `build/gate-e52p8-reg.log`; `17c9963` C366 BEFORE COVERAGE `0cf0688` (COND.ON_ERROR SUPPORTED/EXACT:6; 140 rows 0/0) | **ADVANCED VERBATIM** past ON ERROR 58 to `codegen: condition form not in E2E-3b subset [TBD]: (\| (< dl 0) (> dl 2))` = LOAN2:91 `if dl < 0 \| dl > 2 then` (rc=2, NO .REL, message carries NO line number); recorded `my-gap`, **NOT fixed**, nothing fitted (no candidate was pre-predicted); EXPR1 → GET form 21, EXPR2 → FLOAT builtin 35; NEXT candidate PROPOSED P3-9 = the compound/OR-condition class |
| P3-9 | `codegen: condition form not in E2E-3b subset [TBD]: (\| (< dl 0) (> dl 2))` = LOAN2:91 `if dl < 0 \| dl > 2 then` (plus the standalone `< 0` leaf `my-gap`) | decoded FIRST from the ANNUITY:46 + LOAN2:91/113/120 ORIGINAL goldens (hops 1–2, ZERO oracle); pre-reg `4495604` (PLAN §P3-9 H1–H10 + probes E52VA..VK BEFORE any `ocaml/` byte; probe-tail DEVIATION recorded — no DR golden exists for `put edit(x)(a)`); campaign e52p9 **11 ok/11, ZERO dr-refuses**; goldens VERBATIM `9bb3f99`; claim **C367** `eaa5ef3` | arm `d918dde` (codegen.ml ONLY): value-level Or fold — per-operand truth bytes (bit7 IS truth), `F5 PUSH PSW`, `C1 POP B / B0 ORA B`, ONE terminal `F2` per node (n operands = n−1 folds, still ONE branch); class-driven **NODE-LOCAL** order rules 1–3 (`< 0` computed LAST as the atomic bare `3A r(cell+1)`; same-var FIXBIN `= 0` then `> k` ladder → ladder pushed FIRST; else source order); standalone `< 0` TEST leaf `3A r(cell+1)/B7/F2` reloc ONE PAST the declared cell; DEC fold pair **VAR-FIRST** (hop-4/5 LITERAL-FIRST FALSIFIED by the VG/VI cmp + reloc re-derivation; PAR dead); `= 0`/`> 0`/ladder/EqVV materializers reused verbatim; BIT(1) value position = fold then BARE `32`; **no And byte touched**; every other operand class refuses BY NAME [TBD] | **11/11 whole-file cmp rc=0** (VA 128 B/`001C` · VB VC VD 128/`0026` · VE 256/`002C` · VF 256/`003C` · VG 256/`0047` · VH 256/`002F` · VI 384/`0076` · VJ 128/`0025` · VK 256/`0080`; DATA from DEF-DATA RECORDS VG `0014`, VI `001A` — hop-4 `001B` FALSIFIED, console `data=` COSMETIC; VK `0009`; VB==VC byte-identical), FIRST-HAND re-verified from the committed tree into fresh paths twice (hop 6, hop 7 `build/e52p9-hop7/out/`) on binary `11c6283e75b60fe3…`; histogram codegen 68/total 124 == baseline; sweep FAILS 0; markers 10/10 MARKER_FAILS 0; falsifiers KEPT VERBATIM (RB by VB==VC; SN/LB by VE/VF-node1 `2A` heads; PAR; PLAN §4 VG literal-first; EVERY §4 CODE-size SHORT miss — they omitted the `x = 2;` continuation); inventory 1249→**1260** (+11 exactly, refusals 186); census OWN path `b080894` (15/0/26/0, LOAN2 message MOVED VERBATIM); C367 `eaa5ef3` measured-bytes-only BEFORE COVERAGE `7da60b5` (COND.OR SUPPORTED/EXACT:11 + EXPLICIT COVERAGE-IDS line, NEVER coverage_gen.py) — coverage_check rc=0 **141 rows 0/0 SUPPORTED 91**; FULL gate rc=0 DIRECT **1260/0, 186/186, 9/9, 141 rows 0/0, census 15/0/26/0, prose 5** `build/gate-e52p9-reg.log` | **ADVANCED VERBATIM** past LOAN2:91 to `codegen: statement kind not in supported subset [TBD] (line 92)` — the `signal error` statement, PREDICTED = MEASURED, UNARMED, NEVER fixed; its DR lowering `21 00 00 / AF / CD ?SIGOP` recorded as an original-golden byproduct OUT OF SCOPE (PROPOSED P3-10, never authorization); EXPR1 stays at GET form 21, EXPR2 at FLOAT builtin 35; BYTE-TIER-ONLY — no runtime claim, O-1 LOAN2 citations panel-unverified |
| P3-10 | `codegen: statement kind not in supported subset [TBD] (line 92)` = LOAN2:92 `signal error;` (THEN-body of the line-91 OR fold) | Phase-A audit with ZERO oracle pinned SIX SIGNAL sites in FOUR original objects (`build/e52p10/` raw records; PLAN §2 table: LOAN2 0359 `21 00 00`, EXPR1 0175+018D / EXPR2 023D+0255 `21 01 00` four identical, COPYLPT 02AA `21`+RELOC common/`3E 08`, ON-route control 0254); pre-reg `c6c4460` (PLAN §P3-10 H-A..H-X + probes E52WA..WL committed BEFORE any oracle call and any `ocaml/` byte); campaign `e52p10` rc=0 **11 ok/12**, **E52WL `dr-refuses`** PASS-2 line-12 `SYNTAX ?` NO .REL kept VERBATIM; goldens VERBATIM `d46b6c2`; claim **C368** `7153716` | frontend repair AFTER evidence `d84665c`: `Ssignal` gains `cargs : expr list` (parser stops discarding `_sargs`; bind 574/1518 + `pli80deps` traverse; `FROM` KEPT, NEVER lowered), `signal_error_prefix` its OWN encoder ([C202] doctrine; FILE form reuses `on_reg_prefix` because the bytes agree); arm admits MEASURED shapes ONLY — ERROR bare/ONE integer literal (full 16-bit, WE proved NO range check) as ABS `21 lo hi / AF / CD ?SIGOP` 7 B, `endpage(f)` `3E 08` / `endfile(f)` `3E 05` 11 B via SEL-COMMON+`RELOC common 0x0`; PURE statement, no `C3` slot/handler/pad/SP cell; `st.lowered+1`, `st.last_imm <- None`; FROM/multi-arg/other conditions/variable+expression args refuse BY NAME [TBD] | **9/9 accepted probes (WA-WE,WH-WK) whole-file cmp rc=0** on binary `a4c0e235ed4bb81fe284…` (POSITIONAL `pli80c` into FRESH paths; re-verified FIRST-HAND at registration AND again before C368); histogram codegen 68/total 124 == baseline; sweep FAILS 0; markers 10/10 MARKER_FAILS 0; regressions 17/17; **WE FALSIFIES the 0..255 range-check competitor** (`error(256)` = `21 00 01` verbatim); **WF** (`1+1`, stack `?DLDOP`×2/`?DADOP`/`?QDI15`, CODE `0029`/DATA `0003`) and **WG** (`error(n)` via `LHLD`, CODE `001C`) DR-ACCEPTED SINGLE witnesses — armed NEITHER per the pre-registered do-not-generalise clause, open `my-gap` [TBD], panel-unverified; **H-A/B0/B2/C255/E1/E2/F/G ALL CONFIRMED**, no PLAN §3 falsifier fired; `ssignal_ast.ml` proto test `91060ea` 12/12 PASS incl. refused shapes; SPECIMENS +9 → **1269 (+9 exactly)**, WL enters REJECTS → **187 (+1)** (`21d4db6`, every added line inspected, config never staged); census OWN path `0198fe5` 15/0/26/0 UNCHANGED; **C368 measured-bytes-only BEFORE ANY COVERAGE touch** (`7153716`); `COND.SIGNAL` SUPPORTED/**EXACT:9** + EXPLICIT `COVERAGE-IDS` line `65b005e` (NEVER `coverage_gen.py`; 15 cols from FIRST NON-COMMENT row; `delimiter='\t'`) → coverage_check rc=0 **142 rows 0/0 SUPPORTED 92**; FULL gate rc=0 DIRECT `build/gate-e52p10-reg.log` **1269/0, 187/187, 9/9, 142 rows, census 15/0/26/0, prose 5** | **ADVANCED VERBATIM** past line 92 to `codegen: PUT FILE(OUTPUT) has no byte-exact DR witness [TBD] (line 99)` — ACTUAL text recorded, NOT predicted (PLAN §6 forbade a prediction), UNARMED, NEVER fixed; EXPR1 GET-21 / EXPR2 FLOAT-35 unchanged; LOAN2 NEVER claimed exact; BYTE-TIER-ONLY — no runtime `?SIGOP`/signal-delivery claim, PLILIB UNEXAMINED; **STOP: P3-11 NOT authorized** |
| P3-11 | `codegen: PUT FILE(OUTPUT) has no byte-exact DR witness [TBD] (line 99)` = LOAN2:99 `put file(output) page;` behind the LOAN2:54/56 PRINT opens | Phase-A + hop-1 raw-record audit (ZERO oracle): the SAME statement measured VERBATIM in `golden/first/LOAN2` 03AA-03BB (18 B, DOUBLE patch 03A8+03B1->03BC) and COPYLPT 0215-0226, P019B LIST 0063-007C, E46N1/E46N2 skip shapes; pre-reg PLAN §P3-11 H-A..H-K + probes E52XA..XK committed BEFORE any oracle call/`ocaml/` byte; campaign e52p11 **11 ok/11, ZERO dr-refuses**; goldens VERBATIM `060289e`; claim **C369** `a00fc13` measured-bytes-only BEFORE any COVERAGE touch | arm `3e0a3c1` = candidate A: ONE condition line in `lower_open` records a PRINT-spelling OPEN beside OUTPUT into the compiler-side eligibility list; open/PAGE/LIST/SKIP emitters UNCHANGED, ZERO statement bytes; PU1 marker substring survives VERBATIM; BY-NAME refusals kept (PAGE+items, counted PAGE, LINE, console PAGE, KEYED, INPUT named PUT, no-open named PUT, variable LIST items) | **9/9 whole-file cmp rc=0** (XA `0036`/`0002`, XB `003E`/`0006` w1 `0E52`, XC `003E` w1 `2E52`, XD `003C`/`0011` `?SLVTS`, XE `003D`/`0004`, XF `0063`/`0017`, XG `003E`/`0003`, XH `0038`/`0002`, XI `0043`/`0003`) on binary `25c57e27696421e929b8…`; **H-E DOUBLE back-patch CONFIRMED (single-patch FALSIFIED)**; **pagesize-required competitor FALSIFIED by XB**; **input-mirroring attach FALSIFIED by XK** (open `0x0690`, attach STILL `0x0652`, [C280] reconfirmed); MY §4 XA-slot `0030` prediction FALSIFIED — measured `002D` = 001B+18, kept VERBATIM; **XJ (no open) and XK (stream input) DR-ACCEPTED, refused BY NAME here = honest my-gap, goldens KEPT UNCLAIMED** (markers re-measured line 8/line 9 under gate CRLF+bare-^Z); histogram 68/124==baseline, sweep FAILS 0, markers 5/5, regressions 38/38; inventory 1269->**1278/189** (+9/+2 exactly) `69dd508`; census OWN path 15/0/26/0 UNCHANGED; coverage `b9645fa` EXTENDS PUT_PAGE EXACT:1->**7**, PUT_SKIP 18->**20**, PUT_LIST 10->**11** (NO new rows, COVERAGE-IDS diff EMPTY, coverage_gen.py NEVER run, LIST's now-false 'No object yet pairs...' clause kept inside a labelled CORRECTION) -> coverage_check rc=0 **142 rows 0/0 SUPPORTED 92**, prose rc=0; FULL gate rc=0 DIRECT `build/gate-e52p11-reg.log` **1278/0, 189/189, 9/9, 142 rows, census 15/0/26/0, prose 5** | **line-99 blocker CLOSED**; ACTUAL next blocker recorded VERBATIM and NEVER fixed: `codegen: DECIMAL assignment between differing scales is unproven [TBD] (only computed results are pinned as needing a QDDSL/QDDSR fix; a direct DEC operand store always had equal scales in the samples)` — NO `(line N)` clause; EXPR1 GET-21/EXPR2 FLOAT-35 unchanged; LOAN2 NEVER claimed exact; BYTE-TIER-ONLY; **STOP: P3-12 NOT authorized** |
| P3-12 | `codegen: DECIMAL assignment between differing scales is unproven [TBD] (…)` — NO line clause, LOAN2:111 `INF = ci;` (MEASURED by temporary instrumentation, reverted) | Phase A ZERO oracle (LOAN2.REL 04B7-04CB DOWN witness + NG20 UP witness + LOAN1 equal-scale control cmp rc=0; NG21 FALSIFIED as evidence); pre-reg `ecba8c5` (PLAN §P3-12 H-1..H-8 + probes E52YA..YI BEFORE any oracle call/`ocaml/` byte); campaign e52p12 rc=0 **9 ok/9, ZERO dr-refuses**, every `.PRN` `NO ERROR(S)` both passes; goldens VERBATIM `0c43932` BEFORE any emitter byte; claim **C370** `172a642` measured-bytes-only BEFORE any COVERAGE touch | arm `1111d5e` + warning fix `60b9c79` (codegen.ml ONLY): `dctx.c_direct` TRUE ONLY at the ordinary `Eident` DEC-store epilogue; `dec_direct_shape` = `Eident` or `DECIMAL(<plain non-DEC ident>)`; shift `MVI A,|Δs| / ?QDDSL`(up)/`?QDDSR`(down) emitted BETWEEN source `?DLDOP` and `LXI H,dst`; `dv_of` DECIMAL reports the TRUE `{sc=0}` pushed descriptor ONLY on the direct-store route (YI); all other routes keep the EXISTING BY-NAME [TBD] refusals, marker-substring-safe, [TBD] literals 68 unchanged | **9/9 whole-file cmp rc=0** on deterministic binary `6a4c6c1154a0acd8403b…` (POSITIONAL, FRESH `build/p3-12/fix-out/`); histogram codegen 68/total 124 == baseline (Warning 27 `ptr` PROVED baseline via `git archive` replay); sweep **159/0**; DEC regressions **64/0**; markers **15/16** — only `N35` fails BY DESIGN → retired HONESTLY to POSITIVE `NG20` (`probes/NG20.PLI` sha `acf8e951…`, golden KEPT NEVER re-derived, cmp rc=0 twice; refusals 189→**188**; NO invented replacement negative — unmeasured routes, loss ACCEPTED); divergences **9/9** via standalone `build/p3-12/divcheck.py` (`--only-divergent` is the WRITE arm, blocked by stale-census preflight — lesson); registration `5bf5c88` inventory 1278→**1288/188** (+10/−1, every line inspected); census OWN path 15/0/26/0 UNCHANGED, LOAN2 msg MOVED VERBATIM, NOTHING fixed; NEW row `STOR.DEC_SCALE_ASSIGN` SUPPORTED **EXACT:10** + SAME-change COVERAGE-IDS line `bf135a9` (NEVER `coverage_gen.py`; 15 cols FIRST NON-COMMENT row; textual tab; `manual_ref` must match `pNN[:§X.Y][=phrase]` or start `NONE:`) + stats companion `d283623` → coverage_check rc=0 **143 rows 0/0 SUPPORTED 93**, prose rc=0; **FULL gate rc=0 DIRECT `build/gate-e52p12-reg.log` — 1288/0, 188/188, 9/9, 143 rows, census 15/0/26/0, prose 5 — every pre-registered number HIT**; **H-1 CONFIRMED 7/7; H-2 FALSIFIED (YC Δp=9, d=0B); H-3 FALSIFIED (YF d=0E accepted); H-4 FALSIFIED both directions; H-5 CONFIRMED (YC mirrors YD); H-6 shift-free context model FALSIFIED — DR emits `?QI15D / MVI A,02 / ?QDDSL`, pre-arm cmp FAIL byte 68 honest my-gap CLOSED by the sc=0 rule; H-7/H-8 held**; §4 misses KEPT VERBATIM (YB/YE predicted `?QDDSR` measured `?QDDSL`; YG predicted up measured DOWN) | **ADVANCED VERBATIM** past 111/112 to the ACTUAL Line-117 blocker `codegen: non-variable argument against a FIXED DECIMAL formal is unproven [TBD] (… [DECPOLY, R2037/R2038/R725]. Line 117)` = `call display(PL * INF, …)` — recorded, NEVER fixed here; EXPR1 GET-21/EXPR2 FLOAT-35 unchanged; LOAN2 NEVER claimed exact; BYTE-TIER-ONLY; **P3-13 = the Line-117 DEC-formal target under the marathon brief** |
| P3-13 | `codegen: non-variable argument against a FIXED DECIMAL formal is unproven [TBD] (… Line 117)` = LOAN2:117-118 five product actuals vs five `dec(10,2)` formals | Phase A ZERO oracle (authentic LOAN2.REL `055D–05FA` 32 B blocks + static vector `031A–0323` + NG18 literal witness; C093 `*A(005A)=5.67` AUDICATED false-as-cited); pre-reg `7503552` (PLAN §P3-13 H-1..H-8 + probes E52ZA..ZF BEFORE any oracle call/`ocaml/` byte, sanity all six rc=2 at the guard); campaign e52p13 rc=0 **6 ok/6**, every `.PRN` NO ERROR(S) both passes; goldens VERBATIM `6267faf` BEFORE any emitter byte; claim **C371** `1d1885b9` measured-bytes-only BEFORE any COVERAGE touch + DATED correction of BOTH C093 errors | arm `13e53be` (bind `cs_dec` single allocation authority — DEC expression temps sized `bytes_of (RTdec(pf,sf))`, array-named/recursive/attr/external excluded; codegen admits ONLY `Enumber` literal → pre-scaled formal-width `dec_pool` cell + static descriptor RELOC, ZERO code, and `Mul` of two plain DEC autos → armed `dec_push` via ONE `dec_actual_mat` slot terminating DSTOP A=pf; `dec_pool` moved before `lower_hl`) + histogram repair `e971f3e` (dead zip3; predecessor's W9/W39 view FALSIFIED as misleading incremental output) + TWO measured my-gap repairs `9b81ed0` (const_cells DEC demand `dec_pool_bytes(pf)`; deref-DEC PUT LHLD route armed on the ZF golden) | **8/8 whole-file cmp rc=0** on deterministic binary `6db44394…` (histogram 68/124==baseline): ZA `006F` down d=03 QDDSR / ZB `006F` UP d=02 QDDSL 4 B temp / ZC `50 01 00 00 00` / ZD `00 01 00 00 00` zero caller code / ZE interleaved vector `05 00 18 00 00 00` / ZF LOAN2 replication `0106` + deref-PUT `00ED–00F2`; **H-1..H-8 ALL CONFIRMED, ZERO §4 misses, ZERO falsifiers fired**; sweep 168→174/0 (count follows INVENTORY rows — FAILS 0 binding); markers 14/15→**14/14** (N33 out); DEC 64/0; divcheck 9/9; **N33→NG18 retired honestly (187) then N52→NG39 retired by GATE-FOUND NEG-FAIL (186) — LESSON: only the FULL gate runs the negative panel**; registration `39bb9a0`+`601e20e1` inventory 1288/188→**1295/187**→**1296/186**; census `59be109`+`42f3f659` 15/0/26/0 UNCHANGED; NEW row `PROC.CALL_DEC_ACTUALS` `afb95163` EXACT:7 + SAME-change IDS line + dated STOR.DEC_SCALE_ASSIGN correction; EXTENDED `c1059d46` +NG39 EXACT:8 (144 rows 0/0 SUPPORTED 94); FULL gate rc=0 DIRECT `build/gate-e52p13-reg.log` **1296/0, 186/186, 9/9, 144 rows, census 15/0/26/0, prose 5** | **Line-117 blocker CLOSED**; ADVANCED VERBATIM to the ACTUAL Line-121 blocker `codegen: CALL target is not a simple procedure name [TBD] (only `CALL id` / `CALL id(args)` / bare `id;` have a DR lowering sampled; line 121)` = `call summary();` — recorded, NEVER fixed (never-predict HELD); EXPR1 GET-21/EXPR2 FLOAT-35 unchanged; LOAN2 NEVER claimed exact; BYTE-TIER-ONLY; **P3-14 = the Line-121 WHY-first target under the marathon brief** |
| P3-14 | `codegen: CALL target is not a simple procedure name [TBD] (only \`CALL id\` / \`CALL id(args)\` / bare \`id;\` have a DR lowering sampled; line 121)` = LOAN2:121 `call summary();` (name shadows the builtin `SUMMARY`) | Hop-1 WHY anatomy ZERO oracle: capture is PURELY `parser.ml` — `builtins` contains `SUMMARY`, `primary` takes any builtin key + `(` into `Ebuilt`, classifier accepts only `Eident`/`Esuffix`; non-shadow arity-0 single/two-site already rc=0 ([C123]/[C124] armed); pre-reg `9d4c3a75` (PLAN §P3-14 H-1..H-5 + probes E520A..E + sanity BEFORE any oracle call/`ocaml/` byte); campaign 1 `e52p14` 1 ok/5 — E520D ACCEPTED (H-4), A/B/C/E died on MY `procedure();` header defect (DATED §4b `a4d10f1a`, goldens KEPT as provenance; NEW PROBE LAW: DR headers are `procedure;`/`procedure(x);`, zero-oracle sanity cannot catch DR-only syntax); corrective `e52p14b` 3 ok/4, goldens VERBATIM `9ece9a69` BEFORE any `ocaml/` byte, **E520E dr-refuses** `SYNTAX ?` line 14 BOTH passes UNCONFOUNDED; claim **C372** `5aae7109` measured-bytes-only BEFORE ANY COVERAGE touch (every byte re-verified first-hand via NEW `build/p3-14c/items.py` item->file-span dumper) | arm `65da9bd1` (`ocaml/lib/parser.ml` ONLY): CALL arm parses its target as PLAIN identifier + `suffix_chain`, NEVER consulting `builtins`; expression `primary`, bare-statement arm, codegen guard UNCHANGED and REACHABLE — widened classifier was pre-registered as WRONG (classifier cannot distinguish `CALL x;` from bare `x;`, would silently arm the measured-dr-refuses H-5 route); armed binary sha256 `b88e7b023027e2eeba1b6f49dc0815cb25e14f20269074a637a7c1f84f3c72e2` deterministic, histogram codegen 68/total 124 == baseline | **4/4 whole-file cmp rc=0** (A/B/C vs `golden/e52p14b/`, D vs `golden/e52p14/E520D`) FRESH POSITIONAL `build/p3-14c/arm-out/`; E520A vs B EXACTLY 3 differing bytes 0-based 6/19/28 all inside packed PROG-NAME/EXTDEF/DEF-PUBLIC, CODE+DATA identical (**H-2 near-miss kept VERBATIM**: predicted one char byte, 6-bit packing carry crosses boundaries); **H-1/H-3/H-4 CONFIRMED, H-5 MEASURED dr-refuses** — BY-NAME refusal AGREES with oracle; sweep 174→**178/0** post-reg (count moves with INVENTORY, prediction HIT); markers 14/14 + E520E marker re-measured; DEC 64/0; divcheck 9/9; registration `9a31509c` inventory 1296/186→**1300/187** EXACT, census OWN path 15/0/26/0 UNCHANGED, LOAN2 msg MOVED VERBATIM, NOTHING fixed; row 85 `PROC.CALL_COPYIN` (EXACT:40) adjudicated FIRST-HAND **UNBUMPED** (its law = actuals copy-in ladder; panel has NO actuals) + justified NEW row `PROC.CALL_TARGET_DESIGNATOR` `f2513593` + SAME-change IDS line; coverage_check rc=0 **145 rows 0/0 SUPPORTED 95**; FULL gate rc=0 DIRECT `build/gate-e52p14-reg.log` **1300/0, 187/187, 9/9, 145 rows, census 15/0/26/0, prose 5** — every number hit | **Lines-121/135 CLOSED**; ADVANCED VERBATIM 121→**147** — ACTUAL blocker `codegen: PUT FILE(OUTPUT) EDIT of the FORMAL A has no byte-exact DR witness [TBD] (line 147 …)` = `put file (output) edit ('\|',a,…) (…,p'$zz,zzz,zz9v.99',a);` — recorded, NEVER fixed; **never-predict HELD** (recon candidate line 160 did NOT fire); EXPR1 GET-21/EXPR2 FLOAT-35 unchanged; LOAN2 NEVER claimed exact; BYTE-TIER-ONLY; **P3-15 = the line-147 FORMAL-A file EDIT under the marathon brief** |
| P3-15 | `codegen: PUT FILE(OUTPUT) EDIT of the FORMAL A has no byte-exact DR witness [TBD] (line 147 …)` = LOAN2:147-150 `put file (output) edit ('\|',a,…) (…,p'$zz,zzz,zz9v.99',a);` — a file EDIT item on the deref'd `dec(10,2)` FORMAL `a` | Hops 1-2 ZERO-oracle pre-audit: authentic `golden/first/LOAN2/LOAN2.REL` display body `0674-0732` ALREADY pins the refused formal chain (`2A 42 03`@`069E` opcode-exact); hop-2 decode `build/p3-15/fmt.py` fully decoded the 50 B T3 format record with ZERO unknown bytes via [C090]/[C361]/[C362] ONLY — never a fit; pre-reg `bbb916b6` (06:36:06) BEFORE campaign `43298b74` (06:40:37) with the 21 B A/B table bytes pinned in §4; campaign e52p15 rc=0 **4 ok/4**, EVERY `.PRN` `NO ERROR(S)` both passes, goldens VERBATIM before any `ocaml/` byte | arm `95f1bbf7` = ONE clause in `authorize_file_edit_item` (`ocaml/lib/codegen.ml` ~12533): in the `PIvar` branch a `st.deref` member is admitted IFF `vk_of st nm = Vdec _`; EVERY other class keeps the VERBATIM `no_witness` refusal (markers survive, guard stays REACHABLE); ZERO new emitter bytes — lowering is the P3-13 deref-DEC chain verbatim; armed binary sha256 `02ea809e8fbc908a722e1e1b979e238b7353fa16eafe7b31df1bce8da0c826fb` deterministic (default == fresh `_build-p315`), histogram codegen 68/total 124 == baseline | **3/3 whole-file cmp rc=0** (A `00B8`/`0026` 640 B, B `00AD`/`0026` 640 B, C `012C`/`005B` 1024 B) re-held at `arm-out/`, `claim-out/` AND `close-out/`; **H-A prep-only law CONFIRMED** — A vs B identical 15-byte tail, ONLY the 3-byte prep differs (`21 2A 00` vs `2A 26 00`, desc cells NO static bytes); **H-B CONFIRMED** one shared `7C` cell (2 chains A/B, 6 chains C); **H-C predicted-before-measured 21 B table HIT** + E521C 50 B table BYTE-IDENTICAL to LOAN2 T3; **H-D CONFIRMED** nested `80 02 80 02` [C362]; **H-E MEASURED: DR ACCEPTS the fixed-bin formal item (E521D 512 B single witness) — deliberately NOT armed, honest my-gap** (do-not-generalise P3-10 WF/WG); ZERO §4 misses; sweep 178→**181/0**; markers 14/14 + E521D re-measured rc=2 line 17; DEC 64/0; divcheck 9/9; registration `12f92978` inventory 1300/187→**1303/188** — CONTRACT SLIP KEPT VERBATIM (predecessor expected 1303/187; refusals MOVE with REJECTS rows — COMPUTE expectations from panel deltas, never quote them); **NEW TOOL LAW (gate-found): a panel refusal PROSE edit REQUIRES `--update-inventory` + commit in the SAME change** — `785c9997` not re-snapshotted → gate ABORTED rc=2 `1 entry SUBSTITUTED` (a count cannot see it), repair `99ea48ce`; C373 `5d316a36` measured-bytes-only BEFORE ANY COVERAGE touch + DATED FALSE-AS-WRITTEN guard-clause correction + DATED anchor correction `069E`/`0693`; coverage EXTEND row 66 `IO.PUT_EDIT` `85c711a2` EXACT:42→**45** + DATED SUPERSEDED clause, NO new row, IDS unchanged; coverage_check rc=0 **145 rows 0/0 SUPPORTED 95**; FULL gate rc=0 DIRECT `build/gate-e52p15-reg.log` **1303/0, 188/188, 9/9, 145 rows, census 15/0/26/0, prose 5** — every number hit | **Lines-147-150 CLOSED**; ADVANCED VERBATIM 147→**160** — ACTUAL blocker `codegen: non-variable argument against a FIXED DECIMAL formal is unproven [TBD] (… Line 160)` — recorded, NEVER fixed; hop-3 recon candidate `call current_year(IP - YIN);` was PROPOSAL only, never predicted; EXPR1 GET-21/EXPR2 FLOAT-35 unchanged; LOAN2 NEVER claimed exact; BYTE-TIER-ONLY; **P3-16 = the Line-160 FIXED DECIMAL non-variable actual under the marathon brief** |
| P3-16 | `codegen: non-variable argument against a FIXED DECIMAL formal is unproven [TBD] (… Line 160)` = LOAN2:160 `call current_year(IP-YIN);` — IP/YIN both `fixed dec(10,2)`, a DEC **Sub expression actual** vs a FIXED DECIMAL formal | hop-2 audit: bind `decact` shape-agnostic, refusal ONLY at the codegen guard; hop-1 authentic LOAN2 `0738-0752` no-window block decoded ZERO-oracle; pre-reg `dfba24a4` (§1–§7 + probes E522A..E + sanity ALL rc=2 at guard lines 11/12/10/11/13) BEFORE campaign `91b10c25` e52p16 **5 ok/5**, every `.PRN` `NO ERROR(S)` both passes, goldens VERBATIM, ZERO §4 sequence misses — H-A 27 B no-shift control == authentic; H-B L1 alignment MEASURED in the ACTUAL context (`3E 01/?QDDSL` between pushes, left first, precisions 0A/04); H-C L5 window Mul→Add/Sub (D UP d=02 scales-only, DSTOP A=07 pf<both); H-D Add `?DADOP` twin — B/C whole files differ EXACTLY 5 bytes (6/19/28 packed names + 112/113 SU→AD), CODE/RELOC/DATA identical, DATED extends [C086] subtract-only pinning TO ADD; H-E NESTED `a-b*c` DR-ACCEPTED 512 B three-push/one-temp — NOT armed, honest my-gap | arm `85bc0463` = guard widening `Ast.Ebinary (Ast.(Mul \| Add \| Sub), l, r)` over the SAME deliberately NON-recursive helper renamed `dec_arith_operand` (recursive test would silently arm E522E); refusal VERBATIM otherwise; ZERO bind/emitter change; armed binary sha256 `215c4503ffaaa1c7c970014cd6c90833656fca1fb13f838126d8e6aa41405175` deterministic (default == fresh `_build-p316`, ZERO Error lines), histogram 68/124 == baseline | **4/4 whole-file cmp rc=0** re-held arm-out/arm-out2/claim-out; E522E rc=2 `Line 13` BY NAME; sweep 181→**185/0** (count-moves-with-inventory HIT); markers 15/15; DEC 64/0; divcheck 9/9; registration `7fd4cdfd` inventory 1303/188→**1307/189 EXACT** (computed +4/+1 HIT); census 15/0/26/0 msg MOVED VERBATIM, NOTHING fixed; **C374** `85500489` measured-bytes-only BEFORE ANY COVERAGE touch (+ DATED corrections: A DEF-DATA-SIZE **001C**, hop-3 `DATA 0014` was the temp-cell value; §4 labels were composed-op, raw spans 27/37/32/48 B); coverage EXTEND `PROC.CALL_DEC_ACTUALS` `0e20023f` EXACT:8→**12** IDS UNCHANGED, `coverage_check` rc=0 145 rows 0/0 SUPPORTED 95; FULL gate rc=0 DIRECT `build/gate-e52p16-reg.log` **1307/0, 189/189, 9/9, 145 rows, census 15/0/26/0, prose 5** — every number HIT | **Line-160 CLOSED**; ADVANCED VERBATIM 160→**177** — ACTUAL blocker `codegen: PUT FILE(OUTPUT) EDIT of a variable bound as fixed-binary has no byte-exact DR witness [TBD] (line 177)` — recorded, NEVER fixed; EXPR1 GET-21/EXPR2 FLOAT-35 unchanged; LOAN2 NEVER claimed exact; BYTE-TIER-ONLY; **P3-17 = the Line-177 fixed-bin EDIT under the marathon brief** (anchor: KEPT `golden/e52p15/E521D` accepted-unarmed witness) |
| P3-17 | `codegen: PUT FILE(OUTPUT) EDIT of a variable bound as fixed-binary has no byte-exact DR witness [TBD] (line 177)` = LOAN2:177-178 `put skip file (output) edit` — 8 items with TWO `\|` literals, LOCAL `yp` + MAIN `y` fixed-bin autos and the deref'd `fixed dec(10,2)` formal `i` in ONE list | hop-1 pre-audit decoded authentic LOAN2.REL `07BA-07C4`/`07D0-07DA` ZERO-oracle (11 B `LHLD/3E 09/?QICOP/?EDTOV`, NO deref quartet; +DATED hop-1 label corrections: chains 11 B not 13, slots were disasm artifacts ~2-3 low); pre-reg `cfa95bcd` (§1–§7 + probes E523A..C + sanity rc=2 at 10/17/8) BEFORE campaign `40d98144` e52p17 **3 ok/3**, every `.PRN` `NO ERROR(S)` both passes, goldens VERBATIM, ZERO §4 misses — H-A E523A 0049-0053 VERBATIM (shared `7C` data@0014, table data@0000-0013 VERBATIM); H-B LOAN2-class twin cmp rc=0 896 B (yp 007A-0084 / y 0090-009A byte-IDENTICAL scope-independent; `i` = 17 B [C373]; picture `02 0A 02 0F`+15 B data@0013-0025; cy ENTRY code@0040 — DATED correction of hop-3 `004A`; static vector data@0050=`4A 00` RELOC→data@004A [C371]); H-C DR ACCEPTS `dcl s fixed binary static` byte-identical chain, NO static bytes in cell — honest my-gap, NOT armed | arm `f41b6e1c` = exactly ONE clause `\| Vint -> ()` in the non-deref `PIvar` branch of `authorize_file_edit_item` (codegen.ml, after `Vdec _`) + dated evidence comment; ZERO bind/emitter change; deref-Vint E521D keeps VERBATIM BY-NAME refusal; armed binary sha256 `b744acfbea2489a4ecfd8121573635737e5a49f919d76f15fa6df176b66b1d1f` deterministic (default == fresh `_build-p317`, ZERO Error lines), histogram 68/124 == baseline | **cmp 2/2 rc=0** (A 512 B sha12 `a8b57a97cc14`, B 896 B `d6e7167e948d`) re-held arm-out/hop4-out; E523C rc=2 ends `line 8` — golden KEPT UNCLAIMED; registration `a4ea5e69` → `--update-inventory` 1307/189→**1309/190 EXACT** `4b67ed48` (computed +2/+1 HIT); re-sweep **187/0 FAILS 0**; markers **16/16** incl E523C; census OWN path **15/0/26/0** msg MOVED VERBATIM, NOTHING fixed `60423b32`; **C375** `70c38b38` measured-bytes-only BEFORE ANY COVERAGE touch; coverage EXTEND `IO.PUT_EDIT` `78974f57` EXACT:45→**47** col11 39 names, DATED col4/col13 clauses, NO IDS line (extension), `coverage_check` rc=0 145 rows 0/0 SUPPORTED 95; FULL gate rc=0 DIRECT `build/gate-e52p17-reg.log` **1309/0, 190/190 (E523C NEG-OK VERBATIM), 9/9, 145 rows, census 15/0/26/0, prose 5** — every number HIT | **Line-177 CLOSED**; blocker ADVANCED VERBATIM PAST all line numbers to the `.REL` **record-order law** — `codegen: [TBD] a FILE COMMON group with EDIT format tables above static-initialiser cells, or with a format-table group that does not start at data 0, is an unmeasured .REL record order [E2E-52/P3-2 measures P086K only: tables at data 0000, NO static cells]` (NO `(line N)`) — recorded, NEVER fix; marathon budget EXHAUSTED 8 of ≤8 — **STOP; NO P3-18 without operator decision**; EXPR1 GET-21/EXPR2 FLOAT-35 unchanged; LOAN2 NEVER claimed exact; BYTE-TIER-ONLY |

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

## Subround P3-4 — rep-groups `80 n…81`, `x(w)` = `0B w`, file-route EXPRESSION item

### 1. Measured blocker (VERBATIM at HEAD, binary c2c6282f5662cb19a3ce…)
`codegen: PUT EDIT format item form unsampled [TBD] (counted, grouped, picture,
remote and rep-group formats are not decoded)` — fires at prescan on LOAN2 149's
rep-group; PA refuses at `authorize_file_edit_item` PInum; x refuses at the fmt_spec
catch-all. Ledger ENDS C361; tag `e52p3d` VERIFIED unused; names collision-grepped.

### 2. The DR bytes (ALL from EXISTING goldens, re-read fresh this hop)
- **Rep-group encoding MEASURED twice**: LOAN2 pool 0017 `80 00 | 03 FF | 80 02 |
  80 02 | 02…$ZZ,ZZZ,ZZ9V.99 | 03 FF | 81 | 02…$ZZZ,ZZ9.V99 | 03 FF | 81 | 81`
  (stmt 149 `2(2(p,a),p,a)` — nested, inner group closes with its OWN 81) and
  DEPREC 0033/007B/009E: counts 02 and 04, SIBLING groups `80 02…81 80 02…81`,
  nested `80 02 | 80 04 … 81 | items | 81`, groups containing skip/x/pic/a.
  LAW: group = `80 n <records…> 81`, recursive, source order, NO flattening.
- **x(w) = `0B w`** measured widths {02,03,05,06,08,09,0A,0B,0E,0F,10,13}
  (LOAN2 0046/007C, DEPREC); bare `x` and w>19 UNMEASURED.
- **PA witness verified** at golden/e52p3/E52PA/E52PA.REL 0032-0047 == LOAN2
  0544-0558: `2A (LHLD) RELOC data 0F / 11 64 00 / CD ?IM22N / EB (XCHG) /
  2A RELOC data 11 / 19 (DAD D) / 3E 09 / CD ?QICOP / CD ?EDTOV / CD ?QIOOP`;
  table `80 00 03 FF 02 04 00 05 39 39 2F 39 39 81` at *S 0000; m/y cells 0F/11.
  Console EDIT already lowers `100*m+y` byte-exact (E52PI cmp rc=0) — the file
  arm needs ONLY `authorize_file_edit_item` admission; `lower_put_items_gen`
  PInum path is route-independent.
- LOAN2 177 ALSO pins plain bin vars (yp/y: LHLD/MVI A,09/?QICOP/?EDTOV at
  07BA-07D9) but via PIvar — OUT of P3-4 perimeter (stays refused; P3-5).
- Parser emits `Ast.Pi_repgrp (count_expr, items)` (parser.ml 939); prescan and
  emission SHARE `fmt_table_bytes`; bind.ml `fmt_sz` already sizes repgrp 3+inner,
  X 2 (STATIC-descriptor path, not the EDIT table).

### 3. Probes E52PP..E52PZ (11; CRLF+^Z ≤71 cols) — predictions
- PP file `2(a)` → table `80 00 80 02 03 FF 81 81`.
- PQ file nested+sibling `a,2(2(a,a),a),2(x(3),a)` → `80 00 03 FF 80 02 80 02
  03 FF 03 FF 81 03 FF 81 80 02 0B 03 03 FF 81 81`.
- PR console `2(skip,a),p'99'` + expr item → `80 00 80 02 0C FF 03 FF 81 02 02
  00 02 39 39 81`.
- PS `1(a)` count-1: H2a `80 01 03 FF 81` / H2b REFUSED / H2c folded.
- PT file `x(1),a,x(5)` → `80 00 0B 01 03 FF 0B 05 81`.
- PU bare `x`: H5a `0B 00` / H5b `0B 01` / H5c REFUSED.
- PV `x(128)`/`x(255)`/`x(0)` (3 tables): H4a all accept `0B w` / H4b refusal
  above 19 — WHICH width first is the measurement.
- PW file `m+y` → existing lower_hl add + `3E 09/?QICOP/?EDTOV` (H6).
- PX file `100*m`: H6a `…?IM22N/EB/MVI A,09…` vs H6b no XCHG — settles result reg.
- PY file `m-y` → existing subtract + QICOP/EDTOV (H6).
- PZ file `m/3` → accept or REFUSE (division unmeasured on EDIT route anywhere).

### 4. Arm (ocaml/lib/codegen.ml ONLY, after measurement)
(a) fmt_spec `Pi_repgrp (c,is) -> [0x80; fmt_w c] @ concat_map fmt_spec is @ [0x81]`;
(b) fmt_spec `Pi_fmt X` one-arg literal width -> `[0x0B; fmt_w w]`; bare-X and
w-boundaries armed ONLY as PV/PT/PU measure; (c) authorize_file_edit_item PInum ->
admit Ebinary/Econd arithmetic over fixed-bin cells (identifiers bound Vint/Vbfix,
integer literals; ops admitted ONLY those PW/PX/PY(/PZ) measure; float/DEC/call/
subscript/member shapes keep refusing BY NAME. PA cmp vs EXISTING golden is the
whole-file test; no PA golden re-derivation.

### 5. Boundaries KEPT (refuse BY NAME)
`1(...)`-fold unless PS proves it; bare `x` unless PU proves it; widths beyond
what PV measures; Pi_group (no count) never sampled; column(n) `0D w` decoded
here but NOT armed (out of P3-4 brief); PIvar bin var on file route (LOAN2 177
pins, P3-5 candidate); DEC formal a..e — LOAN2 147's expected NEXT blocker,
record VERBATIM, never fit.

## Subround P3-5 — DATA-item DO-repetition (`Ast.Pi_rep`) on the EDIT route (LOAN2:212 blocker)

### 1. Measured blocker (VERBATIM, re-measured this hop at HEAD 8f1f7ce, binary sha256 `345644822818326f…`)
`codegen: PUT FILE(OUTPUT) EDIT shape [TBD] (line 212) -- an EDIT list the matcher
cannot split into data items plus a final wrapped format list: empty data, a
trailing item after the format list, or an item class classify_item does not name`
— rc=2, raised in the PRESCAN walk (`edit_stmts` → `match_put_edit` → the file arm
whose `split` returns None on a non-`Pi_data`/`Pi_fmtlist` item). LOAN2 line 212
VERBATIM: `       ('---------------' do i = 1 to 4)) (a);` (statement starts at 211
`   put file(output) skip edit`) — the class is the **`Ast.Pi_rep` DATA item**
(`'literal' DO <ind> = <from> TO <to> [BY <step>]`, parser.ml 1018 → `Pi_rep (e,
REPSPEC)`). The P3-4 `Pi_repgrp` (FORMAT group) is a DIFFERENT node and is closed.
Ledger ENDS C362; tag `e52p5` verified UNUSED (grep spec/ tools/, ls golden/ build/,
probes/); names E52RA..E52RJ collision-grepped EMPTY in probes/ and spec/INVENTORY.txt.

### 2. The DR bytes (ALL from the EXISTING LOAN2 golden, re-read fresh this hop — ZERO oracle call)
`build/e52p3e/LOAN2-golden-reldump.txt`, procedure `line` span 0944-099F (DEF-CODE-SIZE 09A0):
- Attach + bare skip + EDITF (the P3-2 law, unchanged): `21 r(data 028C file-common) /
  11 52 06 LXI D,0652 / 01 <chain 094F continuation> / CD ?SIOOP(0952) / 3E 01 / CD
  ?SKPOP(0957) / 21 r(data 009D *S table) / CD ?EDITF(095D)`.
- Non-rep items are the EXISTING literal chains: `21 r(029B) / 3E 07 / CD ?SLCTS(0965) /
  CD ?EDTOV(0968)` and `21 r(02A2) / 3E 0C / CD ?SLCTS(0970) / CD ?EDTOV(0973)`.
- **The `Pi_rep` item (H1 witness)** — a pre-tested inline loop around ONE literal copy:
  `0975: 21 01 00 LXI H,0001 ; 0978: 22 r(data 0358) SHLD i ;
   097B: 2A r(0358) LHLD i (TOP) ; 097E: 01 FB FF LXI B,FFFB = -(to+1) ;
   0981: 09 DAD B ; 0982: 7C MOV A,H ; 0983: B7 ORA A ; 0984: F2 <chain 0985→099C> JP exit ;
   0987: 21 r(02AE) / 3E 0F / 098C: CD ?SLCTS / 098F: CD ?EDTOV (ONE body copy) ;
   0992: 2A r(0358) LHLD i / 0995: 23 INX H / 0996: 22 r(0358) SHLD i /
   0999: C3 r(code 097B) JMP TOP ; 099C: CD ?QIOOP / 099F: C9 RET (exit label)`
- The format table `*S 009D` = `80 00 | 03 FF | 81` — the `(a)` list wrapped as usual;
  the rep item contributes **0 format bytes**. This CONFIRMS the UNVERIFIED `bind.ml:1155`
  "rep of data item: no format bytes [verify]" annotation against the LOAN2 golden — the
  ONLY `Pi_rep` in ANY re-dumped golden; lowering of OTHER rep shapes (variable item, BY,
  REVERSE, FROM≠1, variable bounds) stays UNMEASURED.
- Literal cells 029B(7)/02A2(12)/02AE(15) are ONE copy each: the rep body is emitted ONCE
  inside the loop (no unrolling).

### 2a. Pre-arm code-reading falsification (the successor brief's "codegen.ml ONLY")
**FALSIFIED by code reading BEFORE any oracle call.** `parse_rep_spec` (parser.ml 984-998)
drops the INDEX VARIABLE (`let ind = name_any p in … ignore ind`) and drops `BY`
(`ignore by_`); it never parses `REVERSE`. But the golden loop SHLDs/LHLDs the INDEX cell —
codegen CANNOT name it from an `REPSPEC` of `[from;to]`. So the arm MUST touch
`ocaml/lib/parser.ml` (carry `ind` as child 0 of `Ebuilt("REPSPEC",…)`; `by_` present →
parse-stage refusal BY NAME) plus `ocaml/lib/codegen.ml` (matcher, pitem, prescan,
authorize, lowering); `bind.ml` ONLY if the REPSPEC walk sites (585/1477/1914) break on the
new shape — the build measures that. The REPSPEC NAME exclusion at bind.ml:1460 protects
the decimal-pool walk regardless.

### 3. Probes E52RA..E52RJ (10; CRLF+^Z ≤71 cols, E52PP skeleton) — predictions
- RA file `edit(('AB' do i = 1 to 3))(a);` — HEADLINE: table `80 00 03 FF 81`; loop
  `21 01 00 / 22 r(i) / 2A r(i) / 01 FC FF / 09 / 7C / B7 / F2 exit / 21 r(lit) / 3E 02 /
  ?SLCTS / ?EDTOV / 2A r(i) / 23 / 22 r(i) / C3 top / exit: ?QIOOP`; ONE literal cell.
- RB `skip edit('X',('AB' do i = 1 to 3),'Y')(a);` — literal, loop, literal, source order.
- RC file `edit(('AB' do i = 1 to 3 by 2))(a);` — BY step; my parser refuses BY at PARSE
  stage after the arm — recorded, not codegen.
- RD `edit(('AB' do i = 2 to 4))(a);` — FROM≠1: predicts `21 02 00`, `01 FD FF` (-(4+1)).
- RE `edit(('AB' do i = 1 to 4 reverse))(a);` — expect dr-refuses (no object anywhere).
- RF `dcl n fixed bin; … edit(('AB' do i = 1 to n))(a);` — variable bound; either a new
  test shape or refusal — the measurement.
- RG `dcl v char(2); … edit((v do i = 1 to 3))(a);` — rep of a VARIABLE item.
- RH console `put edit(('AB' do i = 1 to 3))(a);` — H2 route-independence of the CODE loop
  (E52PR proved the TABLE law route-independent; CODE independence is NEW ground).
- RI `edit(('AB' do i = 1 to 3))(2(a));` — data rep + count-2 FORMAT rep-group together;
  table `80 00 80 02 03 FF 81 81` (P3-4 law) with the §2 loop.
- RJ `dcl m fixed bin; … edit((100*m do i = 1 to 3))(a);` — rep of a numeric EXPRESSION
  (P3-4 `?IM22N` shape) inside the loop body.

Hypotheses: **H1** the §2 loop law generalises to RA/RD (immediates per bounds); **H2**
route-independence (RH); **H3** variable bound (RF) accept-with-new-shape vs refusal,
UNMEASURED; **H4** BY/REVERSE (RC/RE) accept-vs-refuse UNMEASURED, both OUTSIDE the arm;
**H5** rep-of-variable / rep-of-expression (RG/RJ) — measurement; if accepted the arm may
DEFER the class and keep refusing BY NAME (record); **H6** RI is table-law only (P3-4 closed).
LOAN2 prediction: blocker ADVANCES past 212 to the NEXT unsampled class; expected first
refusal in lowering order — the line-177 `PIvar` bin-var file-route item (`yp`,
`authorize_file_edit_item` "a variable bound as …"); DEC formal 147 stays queued behind it.
Record VERBATIM, NEVER fit.

### 4. Arm (parser.ml + codegen.ml; AFTER measurement, §2a governs)
(a) parser: REPSPEC child 0 = index `Eident`; `[from]`/`[from;to]` arity law otherwise
unchanged; `by_` present → PARSE refusal BY NAME. (b) codegen `data` walker admits
`Ast.Pi_rep (x, spec)` → NEW `PIrep of pitem * Ast.expr` (inner classified by classify_item
— only shapes the plain route ALREADY lowers). (c) fmt table encoding UNCHANGED (rep = 0
format bytes, §2 CONFIRMED). (d) prescan: PIrep allocates the inner item's cells EXACTLY
ONCE (the golden's ONE copy). (e) `authorize_file_edit_item`: admit PIrep whose INNER item
the plain route already admits; else refuse BY NAME. (f) lowering emits the §2 loop around
ONE body copy using the program's existing chain/reloc helpers (forward JP via LINK-SET-LC,
JMP relocs the TOP address exactly as the golden at 0999).
Boundaries KEPT: BY, REVERSE, rep of DEC formal/deref, numeric-LITERAL items, PIvar bin-var
file route (LOAN2 177), counted SKIP/PAGE+EDIT, format-COUNT expressions, group count 0,
x-widths 14..128 object gap, nested rep (no golden, no probe).

### 5. Registration (P3-4 pattern)
ONE grouped campaign `PLI_SRC=probes timeout 900 python3 oracle/batch.py E52RA..E52RJ
--tag e52p5 --switches '$L$D'` rc DIRECT; reldumps to build/e52p5/; arm; cmp every accepted
probe whole-file + full sweep (89) + markers rc=2 + LOAN2 rerun UNMODIFIED POSITIONAL,
blocker VERBATIM; SPECIMENS +N; sanctioned `--update-inventory` (expect 1222 → 1222+N);
census OWN write path FIRST (the 212 blocker line is REPLACED); FULL gate rc=0 DIRECT
`build/gate-e52p5-reg.log`; claim **C363** from MEASURED BYTES ONLY **BEFORE** the COVERAGE
`IO.PUT_EDIT` rewrite (EXACT 35 → 35+accepted); coverage_check + prose rc=0; RESULTS §P3-5
+ PLAN §5 row.

## Subround P3-6 — ON UNDEFINEDFILE(<file>) registration + the GOTO-terminated handler (LOAN2:44 blocker)

### 1. Measured blocker (VERBATIM, hop-9 census record; binary `e55e892c346741b2…`)
`codegen: ON UNDEFINEDFILE is not implemented [TBD] (only ENDFILE(<file>) has a DR
lowering; line 44)` rc=2 — raised at LOWERING (the prescan clears all statements since
P3-5). LOAN2 44-49 VERBATIM: `on undefinedfile(output)` / `begin;` / `put skip
list('^i^icannot write to',name);` / `goto open_output;` / `end;`. Ledger ENDS **C363**;
tag `e52p6` verified UNUSED (grep spec/ tools/, ls golden/ build/); E52SA..SG
collision-grepped EMPTY in probes/ and spec/INVENTORY.txt.

### 2. EXISTING DR evidence (re-read fresh this hop, ZERO oracle call)
`golden/first/LOAN2/LOAN2.REL` (`build/e52p3/loan2-golden-reldump.txt`) ALREADY measures
the whole line-44 class — the hop-10 codegen refusal comment's claim that a goto-in-handler
has "no DR sample" is **FALSIFIED by this golden**:
- Registration at 002F: `21 r(common OUTPUT 0)` after `LINK-SEL-COMMON OUTPUT` /
  `3E 06` MVI A,06 / `CD ?ONCOP` / `C3 <slot 0038>` — the [C109] shape with condition
  byte **06** (ENDFILE=05). No claim names 06; candidate **C364**.
- Handler 003A-005E: console `put skip list` chain (existing law), then `C3` at 005F
  (the goto, operand slot 0060, `LINK-CHAIN-ADDR code 0060`) — and **NO C9 RET** after a
  goto-terminated handler; emission resumes at 0062.
- Patch: `SET-LC 0038 / RELOC code 0x62 / SET-LC 0062` — JMP-over operand = 0062 = the
  pad/label entry (the label `open_output:` is the very next statement).
- `open_output` pad at 0062: `2A r(data 0318) LHLD *A / F9 SPHL / CD ?RECOV` — plus main's
  entry SP-save at 0006: `21 00 00 LXI H,0000 / 39 DAD SP / 22 r(0318) SHLD *A`. A SECOND
  pad at `?RECOV code 0116` (label `retry`, ON-ERROR handler target) — pad demand is real.
- **Bind survey trap:** `refs_stmt` (bind.ml 1687) charges `Rk_on` ONLY for a DIRECT
  `Sgoto` handler; an `Sdobegin`-ending-in-goto falls into `refs_stmt handler` → the goto
  is `Rk_plain` SAME-BLOCK → per [E36T11] NO pad/cell demanded — contradicts this golden.
  The arm must touch **bind.ml AND codegen.ml** ("codegen-only" is falsified by code reading).
`golden/probe57/P088I` (preserved transcript, `$C` diag): `on endfile x = 1;` and
`on undefinedfile x = 3;` → PASS 1 CLEAN, then PASS 2 `SYNTAX ?` (2 ERROR(S)) and a
CODE-LESS .REL — argumentless UNDEFINEDFILE is **dr-refuses**; `endpage`/`name` bare
carried NO error marker (separate unmeasured classes, NOT P3-6 targets).
`golden/probe58/P089I`: only `on conversion(f)` was flagged; `on undefinedfile(f) x = 3;`
carried NO error → the file-argument form parses cleanly (its CODE was killed by the
conversion pass-2 error, so NO bytes are decodable from P089I).

### 3. Probes E52SA..SG (7; CRLF+^Z ≤71 cols) — PREDICTIONS (pre-registered, NEVER fit)
- SA `on undefinedfile(f) x = 1;` minimal: SEL-COMMON F + `21 r(common F 0) / 3E 06 / CD
  ?ONCOP / C3 slot` + inline assignment + **C9 RET** + slot patched to continuation; NO
  DAD SP save, NO pad (statement handler [C206]).
- SB LOAN2 shape (begin; put skip list('oops'); goto openf; end; with `openf:` IMMEDIATELY
  after): entry SP-save `21 00 00 39 22 r(*A)`; pad at openf `2A r(*A) / F9 / CD ?RECOV`;
  handler put chain then `C3` goto; **no C9**; JMP-over operand = pad address.
- SC label NOT adjacent (x=2 between `end;` and `lbl:`): pad at lbl ≠ continuation address;
  JMP-over operand = the `x = 2` statement address; goto operand chains to the PAD — the two
  patch targets are INDEPENDENT.
- SD direct form `on undefinedfile(f) goto fin;`: [C201]/E32E2 pair — `C3 cont` stub then
  `C3 <chain fin>`; pad + SP save; NO inline handler, NO RET.
- SE `revert undefinedfile(f);`: **[TBD] UNMEASURED** — DR verdict unknown (my REVERT
  refuses non-endfile BY NAME; a refusal keeps the boundary; acceptance is a my-gap whose
  arm (same prefix + `?REVOP`) stays PROPOSED, not this subround's headline).
- SF bare `on undefinedfile x = 1;`: predicted **dr-refuses** — PASS 1 clean, PASS 2
  `SYNTAX ?` on the statement (P088I transcript law).
- SG `on undefinedfile(f,g) x = 1;`: **[TBD] UNMEASURED** (manual permits an identifier
  list; no golden carries one; acceptance keeps my refusal, UNMEASURED boundary).
Hypotheses: **H1** condition byte 06 (from LOAN2 golden, predicted SA-SD); **H2** the
[C109] registration prefix is condition-blind; **H3** handler-tail GOTO omits the RET and
jumps INLINE via the ordinary label-resolution path; **H4** a handler-tail goto DEMANDS the
owner block's cell + the label's pad (bind survey fix); **H5** argumentless refuses (SF);
**H6** SE/SG undecided. Boundaries KEPT: goto inside IF/DO of a handler (unmeasured),
cross-block handler-goto, REVERT-undefinedfile, arg-list, every other condition name
(ON ERROR line 58 next), counted SKIP and PRINT/PAGESIZE OPENs 50/54/56 stay queued.
LOAN2 prediction (arm hop): blocker MOVES PAST 44; FIRST candidate in lowering order = the
counted-skip console put at line 50 `put skip(2) list(...)` or the OPEN at 54 — expected
verbatim `codegen: OPEN option PRINT is outside what this compiler lowers [TBD] (line 54)
-- P0 measured 34 OPEN blocks…` (refuse_file_opt; iteration order: TITLE passes, PRINT
refuses); record VERBATIM, NEVER fit.

### 4. Arm (hop 11; AFTER measurement; bind.ml + codegen.ml)
(a) codegen: generalize `on_reg_prefix` with the measured condition-code pair
endfile=05 [C109] / undefinedfile=06; Son dispatch admits `("endfile"|"undefinedfile",
[Eident f])`; (b) handler shape: `Sdobegin ss` with LAST stmt a bare `Sgoto` → lower all
stmts inline, goto via the existing resolve/fwd_ref path, **omit the C9**, `emit_triple` the
JMP-over; every other goto-containing handler keeps refusing BY NAME with the refusal text
corrected to name the MEASURED samples; (c) bind `refs_stmt`: Son handler `Sdobegin` whose
last stmt is a bare `Sgoto` → `[(lbl t, Rk_on)]` (cell + pad demand). cmp SA SB SC SD whole-file
rc=0 vs `golden/e52p6/`; SE SF SG per verdicts; sweep 101; markers rc=2; LOAN2 POSITIONAL
VERBATIM (prediction §3); commit; then registration: SPECIMENS +accepted, inventory
1229→1229+N (+refusals), census OWN path FIRST (line-44 line REPLACED), FULL gate rc=0
`build/gate-e52p6-reg.log`, claim **C364** measured-bytes-only BEFORE the COVERAGE row
rewrite (`ON`-unit rows), coverage_check+prose rc=0, RESULTS §P3-6 + PLAN §5 row.

## Subround P3-7 — OPEN PRINT / PAGESIZE / LINESIZE (LOAN2:54 blocker) — PRE-REGISTERED 2026-11-05, ZERO ocaml/ byte, ZERO oracle call

### 1. Measured blocker (VERBATIM, re-measured this session at HEAD `c0ce1a1`, binary sha256 `0efc35e6d4ff81bd…`, rc=2 DIRECT)
`codegen: OPEN option PRINT is outside what this compiler lowers [TBD] (line 54) -- P0 measured 34 OPEN blocks in 24 DR objects (spec/lab-evidence/e2e41-p0/OPEN-MATRIX.tsv)…`
LOAN2 54/56 VERBATIM: `open file(output) title('$con') print pagesize(0);` / `open file(output) title(name) print;`.
Related re-measured rc=2 blockers: P019B line 3 (same PRINT message); P021 line 4 (`OPEN option KEYED`);
RETRIEVE line 19 (PRINT); KEYFILE line 16 (KEYED); COPYLPT (PUT SKIP-with-count, prescan); DEPREC (array-of-0-byte-elements).

### 2. EXISTING DR evidence (re-read fresh this hop from `spec/lab-evidence/e2e41-p0/OPEN-BLOCKS.txt` + `OPEN-MATRIX.tsv`; goldens untouched)
Every OPEN is: title prologue, SIX pushed words w1..w6, `LXI H,<CB@0>`, `CALL ?OIOOP`. Words: w1 option word,
w2 organisation (ENVIRONMENT only), w3 B(n), w4 F(n), w5 PAGESIZE, w6 LINESIZE.
w1 bits (P0 §7 `W1-BITFIT.txt`): 0x0002 PRINT · 0x0010 STREAM/KEYED · 0x0040 OUTPUT **and** PRINT · 0x0080 INPUT ·
0x0200 stream organisation (set by PRINT alone too) · 0x0400 file (all 34) · 0x0800 TITLE present · 0x1000 LINESIZE ·
0x2000 PAGESIZE · 0x4000 ENVIRONMENT.
MEASURED blocks (bytes verbatim from OPEN-BLOCKS.txt):
- **A** P019B:3 `print` titleless — 21 B, w1=`21 52 06`, then `AF / 47(MOV B,A) / C5 / 33 / 21 52 06 / E5 / 60(MOV H,B) / 68(MOV L,B) / E5×5 / 21 r(CB) / CD ?OIOOP`. B=0 ⇒ zeros from B.
- **B** P021:6 `stream print pagesize(60)` titleless — 24 B: A's prologue, w1=2652, `60 68`, `E5×3` (w2,w3,w4), **`2E 3C` MVI L,3C / E5** (w5), **`68` MOV L,B / E5** (w6=0 — legal only because B=0).
- **C** LOAN2:54 `title('$con') print pagesize(0)` — 29 B, w1=`21 52 2E`; literal-title prologue `21 r(data+00FD) / 3E 04 / CD ?SLCTS / 47 / C5 / 33`; then `21 00 00 / E5×5`. **PAGESIZE(0) is a BIT (0x2000) plus a ZERO word — it adds NO byte.** Same word at DEPREC:51 (`stream print pagesize(0) title`).
- **D** LOAN2:56 `title(name) print` — 27 B, w1=`21 52 0E`, `?SLVTS` prologue, `21 00 00 / E5×5`. Same word RETRIEVE:19 (literal title, 29 B) and DEPREC:78 (29 B).
- **E** KEYFILE:19 `stream output linesize(60) title('$1.key')` — 31 B, w1=`21 50 1E`: literal-title prologue, `21 50 1E / E5`, `21 00 00 / E5×4` (w2..w5), **`2E 3C / E5`** (w6).
- **F** COPYLPT:38 `print pagesize(pagesize) linesize(pagewidth) title(line)` — 33 B, w1=`21 52 3E`, `?SLVTS` prologue, `21 00 00 / E5×3` (w2..w4), **`2A r(data+00FE) / E5`** (w5) and **`2A r(data+0100) / E5`** (w6): VARIABLE attributes are `LHLD <cell>` with a DATA relocation.
- Zero-restoration after a nonzero `MVI L,v` when B≠0 is **`6C` MOV L,H** (H is 0), witnessed at KEYFILE:16 `21 80 00 / E5 / 6C / E5×2` and COPYLPT:49 — NOT in a PRINT/PAGESIZE block.

### 3. Probes E52TA..TJ (10; CRLF + bare ^Z, ≤71 cols) — PREDICTIONS (pre-registered, NEVER fit)
All bodies use only already-lowered statements (console `put list`, `put skip list`, `x = n`), so the OPEN block is the only variable.
- **TA** `open file(pf) print;` → A verbatim, w1 0x0652, 21 B, DR ACCEPTS.
- **TB** `open file(outf) title('$con') print pagesize(0);` → C, w1 0x2E52, 29 B, w5 zero, ACCEPTS (LOAN2:54 class in isolation).
- **TC** `open file(outf) title(name) print;` name char(14) varying → D, w1 0x0E52, 27 B `?SLVTS`, ACCEPTS (LOAN2:56 class).
- **TD** `open file(pf) stream print pagesize(60);` → B, w1 0x2652, 24 B, ACCEPTS.
- **TE** `open file(keys) stream output linesize(60) title('$1.key');` → E, w1 0x1E50, 31 B, ACCEPTS.
- **TF** `open file(printfile) print pagesize(ps) linesize(lw) title(line);` all vars → F, w1 0x3E52, 33 B, ACCEPTS (COPYLPT:38 class with a plain varying title operand).
- **TG** **UND ECIDABLE**: `open file(pf) print pagesize(60) title('$con');` — titled + w5 literal nonzero + w6 zero. H-enc: `21 52 2E/E5, 21 00 00, E5×3, 2E 3C/E5, 6C/E5` → 30 B. falsifier: any other zero-restoration (e.g. `21 00 00`) or a different order.
- **TH** **UNDECIDABLE** (P0 §10 probe E46A): `print pagesize(60) linesize(80) title('$con')` → w1 0x3E52; H-enc w5 `2E 3C`, w6 `2E 50`, 30 B; falsifier: `LXI H` forms or a different word order.
- **TI** **UNDECIDABLE**: `open file(pf) print pagesize(x);` VARIABLE pagesize, no linesize → is w6 restored by `21 00 00` after the `LHLD`? predicted `… E5×3, 2A r(x), E5, 21 00 00, E5` (31 B); falsifier: any other materialisation.
- **TJ** **UNDECIDABLE**: `open file(pf) print pagesize(300);` — value > 0xFF. Predicted DR verdict UNKNOWN (BAD VAL refusal or `21 2C 01`); whichever it is is recorded verbatim; NO fitting.
Hypotheses: **H1** PRINT sets 0x0002|0x0040 and leaves 0x0200 set (A: 0x0652 = 0x0650|0x0002); **H2** the PRINT bits compose with a title bit exactly as D/C show; **H3** PAGESIZE(0) = bit only, word zero, no extra byte; **H4** a literal attribute ≤ 0xFF uses `MVI L,v`; **H5** a variable attribute uses `LHLD <cell>` + DATA reloc; **H6** OUTPUT+PRINT never co-occurs in the corpus ⇒ refused.
### 4. Boundaries KEPT (refuse BY NAME, [TBD])
INPUT+PRINT (no witness); PRINT with ENVIRONMENT/KEYED/DIRECT/RECORD/SEQUENTIAL/UPDATE/APPEND; literal attribute > 0xFF unless TI/TJ measures it; variable PAGESIZE without LINESIZE unless TI answers; PAGESIZE/LINESIZE as an EXPRESSION; TITLE operand shapes unchanged from [C288].
### 5. Implementation plan (AFTER measurement; `open_mode_word` + the w2..w6 emitter only)
Separate the ATTRIBUTE-FLAG encoding from PARAMETER emission: keep one record `{ w1; w5; w6 }`; extend `open_subset_keys` with PRINT/PAGESIZE/LINESIZE; keep the existing three title prologues; emit w2..w6 by the measured register-reuse ladder (titleless ⇒ `60 68` start, `68` restore; titled ⇒ `21 00 00` start, `6C` restore); refuse every unmeasured shape by name. Parser already accepts the vocabulary (`ioopt_keys`); binder untouched.
### 6. LOAN2 direction (pre-registered, NEVER fit)
TA–TC land ⇒ both line-54 and line-56 OPENs lower; LOAN2's blocker MOVES PAST 56. Next candidate in lowering order = **`ON ERROR` at LOAN2:58** (unmeasured condition name, refused today) — expected verbatim `codegen: ON ERROR is not implemented [TBD] …(line 58)`. Record VERBATIM; do NOT fix in P3-7.

## Subround P3-8 — ON ERROR: the ABSOLUTE-operand registration prefix + the BODY-DEPENDENT handler tail (LOAN2:58 blocker) — **CLOSED 2026-11-05 (hop 3)**

CLOSED: campaign e52p8 6 ok/6 (`9f36504`), arm `a7ab5a4` 6/6 cmp rc=0, registration `244f6e1`
(inventory 1249), claim **C366** `17c9963` BEFORE COVERAGE `0cf0688` (COND.ON_ERROR SUPPORTED/EXACT:6),
FULL gate rc=0 `build/gate-e52p8-reg.log`; the measured actuals and every verdict are in
`RESULTS.md` §P3-8. LOAN2 advanced VERBATIM past 58 to the §6 unpredicted condition-form blocker at
line 91 — recorded, NOT fixed; `REVERT ERROR`, expression/variable/multi/out-of-range arguments,
ERROR+STOP/RETURN/NULL/DCL, nested STOP and the UNDEFINEDFILE STOP route stay UNMEASURED and refuse BY
NAME. The sections below are the pre-registration AS WRITTEN.

PRE-REGISTERED 2026-11-05 (session 01a1ab34, renewal 2/12). ZERO `ocaml/` byte and ZERO oracle call
in this hop; this section and `probes/E52UA..E52UF.PLI` are committed BEFORE any compiler byte.

### 1. Measured blocker (VERBATIM, re-measured at HEAD `d9995b7`, binary sha256 `8b374e623bc9e280fa14…`, rc=2 DIRECT)
`codegen: ON ERROR is not implemented [TBD] (only ENDFILE(<file>) and UNDEFINEDFILE(<file>) have a DR lowering; line 58)`.
LOAN2 58-62 VERBATIM: `on error` / `begin;` / `put skip list('^i^iBad Input Data, Retry');` / `goto retry;` / `end;`.
Ledger ENDS **C365**. Probe ids `E52U*` collision-grepped EMPTY in `probes/` and `spec/INVENTORY.txt`;
tag `e52p8` UNUSED (only my own scratch `build/e52p8/` exists).

### 2. EXISTING DR evidence (five independent ON ERROR witnesses, re-read fresh; `build/e52p8/onregions.txt`)
The **bitstream** disassembly (`build/e52p8/ondump2.py` — `dis80.py`'s reldump-TEXT mode prints reloc operands as `.` and therefore showed FALSE gaps) settles the shape. All five agree:

| program | reg. addr | prefix | handler | tail | pad (= goto label) | SP cell |
|---|---|---|---|---|---|---|
| LOAN2 | 00E8 | `21 00 00`(ABS) `AF` `CD ?ONCOP` `C3 ->0111` | inline put-skip-list chain 00F2-010D | `C3` @010E, **no C9** | 0111 `2A r(*A)/F9/CD ?RECOV` | data 0318 |
| ANNUITY | 004B | `21 00 00`(ABS) `AF` `CD ?ONCOP` `C3 ->0074` | inline 0055-0070 | `C3` @0071, **no C9** | 0074 | data 0136 |
| COPYLPT | 00A6 | `21 01 00`(ABS) `AF` `CD ?ONCOP` `C3 ->00CA` | inline put-list (no ?SKPOP) | `C3` @00C7, **no C9** | 00CA | data 0214 |
| EXPR1 | 001B | `21 01 00`(ABS) `AF` `CD ?ONCOP` `C3 ->005E` | inline (put + `get skip`) | `C3` @005B, **no C9** | 005E | data 0040 |
| EXPR2 | 001B | same | inline (+ two `MVI M,00` string clears) | `C3` @0054, **no C9** | 0057 | data 00AD |

Contrast with the **file-scoped** prefix of [C109]/[C364] (`E52SA` 0006, `E52SD` 000D, LOAN2 002F, COPYLPT 0024, EXPR1 000D):
`<SEL-COMMON x>` + `21 r(common x 0)` **with a COMMON relocation** + `3E nn` (`MVI A,<code>`, ENDFILE 05 / UNDEFINEDFILE 06)
+ `CD ?ONCOP` + `C3 slot` = **8 payload bytes after LXI is 3+2+3**; the ERROR prefix is **7 bytes** (3+1+3) because
`XRA A` is ONE byte where `MVI A,nn` is two, and it carries **NO SEL-COMMON record and NO relocation** — the operand is
an ABSOLUTE 16-bit constant. EXPR1 0018 additionally measures a **STOP-bodied** handler (`on endfile(sysin) stop;`) =
inline `CD ?STOPX` and **NO C9 RET** — i.e. [C109]'s RET is **body-dependent**, and my `codegen.ml` (~14010-14050, both
non-goto arms) emits the `C9` UNCONDITIONALLY. That is a recorded my-gap, NOT yet fixed; the panel cannot see it because
no registered specimen has a STOP-bodied handler.

### 3. Hypotheses and falsifiers (pre-registered VERBATIM, NEVER fit)
- **H1 — prefix.** `ON ERROR[<arg>]` registers as `21 lo hi` (LXI H, the 16-bit argument, LITTLE-ENDIAN, ABSOLUTE — no
  `RELOC common`, no `LINK-SEL-COMMON` record anywhere in the object unless a FILE is declared) + `AF` (XRA A) +
  `CD <CHAIN-EXT ?ONCOP>` + `C3 <slot>` = **10 bytes total**. *Competing encoding:* `3E nn` (`MVI A,<code>`) as on the
  file route, or a COMMON/absolute relocation on the LXI operand. *Falsifier:* any object whose registration is 11 bytes,
  whose condition byte is written with `MVI`, or whose LXI operand carries a RELOC record. Every one of the five
  existing witnesses already refutes those competitors; UA..UE re-test the point in minimal isolation.
- **H2 — the argument is the LXI operand verbatim.** Bare `on error` = `21 00 00`; `error(1)` = `21 01 00`;
  `error(2)` must be `21 02 00` and `error(0)` must be `21 00 00` (indistinguishable from bare). *Falsifier:* a refusal
  (`SYNTAX ?`/`BAD VAL`), a clamped operand, an operand that is not the literal, or the value reaching `MVI A`.
- **H3 — the handler tail is BODY-DEPENDENT.** A handler whose last statement transfers unconditionally (GOTO [C364],
  STOP [EXPR1/EXPR2]) emits **NO `C9`**; a handler that RETURNS emits `C9`. *Competing encoding:* the unconditional `C9`
  my code emits today after every non-goto handler. *Falsifier:* UA/UD showing no `C9` after a returning body, or UF's
  `stop;` body carrying a `C9` — each falsifies exactly the arm that copies the blind RET.
- **H4 — a returning handler demands NO block SP-cell and NO pad** ([C206]: the `LXI H,0 / DAD SP / SHLD *A` save and
  the 9-byte pad belong to the GOTO form, not to the ON-unit). *Falsifier:* a `39 DAD SP` entry save, an extra DATA cell,
  or an `LHLD/SPHL/?RECOV` pad in an object whose only ON unit has a returning handler (UA, UD, UE, and the second UF unit).
- **H5 — the jump-over slot is the fall-through continuation and an adjacent label merges the two patch targets**
  ([C208]/[C364]: the pad IS the label's entry; UC merges at one address, UB keeps two independent patch triples).
  *Falsifier:* UB's two `SET-LC/RELOC/SET-LC` triples landing on one address, or UC's landing on two.
- **H6 — verdicts.** All six probes are predicted **DR-ACCEPTED** (both passes clean, an object produced). A refusal on
  any one of them is recorded verbatim as `dr-refuses` and its shape stays unlowered here; no shape is fitted to my
  implementation.

### 4. Probes E52UA..UF (6; CRLF, bare `^Z` at EOF, ≤71 columns, `dcl x fixed bin;` skeleton)
Each predicted CODE byte list is written from the existing witnesses + the established PUT/assignment laws; the arm hop
cmp-checks the WHOLE file byte-for-byte against the golden, so every wrong prediction becomes a visible MISS.

- **E52UA** `on error x = 1;` + `x = 2;` — bare ERROR with a SIMPLE-STATEMENT (returning) handler. Predicted code:
  `01 00 02 CD lo hi(?START)` @0000 · **H1 prefix** `21 00 00 / AF / CD lo hi(?ONCOP) / C3 lo hi(slot 000E)` @0006 ·
  handler `21 01 00 / 22 r(data x)` @0010 · **`C9` RET** @0016 [H3] · continuation `21 02 00 / 22 r(data x)` @0017 ·
  epilogue `CD lo hi(?STOPX)` @001D · `DEF-CODE-SIZE 0020`, `DEF-DATA-SIZE 0002` (x only), **NO COMMON group, NO SP-cell,
  NO pad, NO `DAD SP`** [H4]; slot 000E patched to 0x17.
- **E52UB** `on error goto lbl;` with `x = 1;` BETWEEN the ON and `lbl:` — the DIRECT form, REMOTE label. Predicted:
  entry SP-save `21 00 00 / 39 / 22 r(data 2)` @0006 (cell at data 2, x at data 0, `DEF-DATA-SIZE 0004`) · prefix
  `21 00 00 / AF / CD ?ONCOP / C3 slot 0015` @000D · stub `C3 slot 0018` @0017 · `x = 1` @001A · `CHAIN-ADDR 0018` ·
  **pad @0020** `2A r(data 2) / F9 / CD lo hi(?RECOV)` · `x = 2` @0027 · `CD ?STOPX` @002D · `DEF-CODE-SIZE 0030`.
  Patch triples: slot 0015 → 0x1A (continuation) and slot 0018 → 0x20 (pad) — **two independent targets** [H5].
  *Falsifier:* the two targets coinciding, a pad at the fall-through instead of the label, or DR refusing the direct
  ERROR form (`go to` after a file-less condition name is unpinned by the five witnesses, which all use BEGIN…GOTO).
- **E52UC** LOAN2/ANNUITY mirror: `begin; put skip list('oops'); goto retry; end;` with `retry:` IMMEDIATELY adjacent.
  Predicted: entry SP-save @0006 (`DEF-DATA-SIZE 0008`: 'oops'@0, x@4, cell@6) · prefix `21 00 00 / AF / CD ?ONCOP /
  C3 slot 0015` @000D · inline put-skip-list chain @0017 (`11 52 02` LXI D,*S / `01 lo hi`(slot→0x33) LXI B / `CD ?SYSPR` /
  `3E 01` / `CD ?SKPOP` / `21 r(data 0)` / `3E 04` / `CD ?SLCTS` / `CD ?PNCOP` / `CD ?QIOOP`) · `C3 slot` @0033 with
  `CHAIN-ADDR` and **NO `C9`** [H3] · pad @0036 `2A r(data 6) / F9 / CD ?RECOV` = the merged jump-over+goto target [H5] ·
  `x = 1` @003D · `CD ?STOPX` · `DEF-CODE-SIZE 0046`.
- **E52UD** `on error begin; x = 1; end;` + `x = 2;` — plain **RETURNING** block handler; the shape NO golden contains
  (all five BEGIN handlers end in a GOTO). Prediction as H3+H4: `C9` RET after the block body, NO pad, NO cell, NO `DAD SP`;
  code `… AF / CD ?ONCOP / C3 slot / 21 01 00 / 22 r(x) / C9 / 21 02 00 / 22 r(x) / CD ?STOPX`.
  *Falsifier:* DR emitting no `C9` for a block handler (then [C109]'s RET is block-vs-statement-dependent, not
  body-dependent), or DR refusing the writing outright — either way my current unconditional `C9` for this shape is
  recorded and the shape stays UNARMED.
- **E52UE** `on error(2) x = 1;` + `on error(0) x = 2;` — H2's two NEW literals (only 0 and 1 are witnessed in the
  corpus). Predicted prefixes `21 02 00` and `21 00 00` respectively, everything else as UA. *Falsifier:* a refusal, or
  any operand other than the literal.
- **E52UF** the FILE-condition contrasts under one shape: `on endfile(f) stop;` then `on endfile(g) x = 1;` then `x = 2;`
  (`dcl f file; dcl g file;`). Predicted: first unit = file prefix `21 r(common F 0) / 3E 05 / CD ?ONCOP / C3 slot`,
  handler inline `CD lo hi(?STOPX)` and **NO `C9`** (H3 on the ENDFILE route — EXPR1's reading in isolation);
  second unit = the [C109] witness under the identical shape, handler `21 01 00 / 22 r(x)` **with `C9`** — the pair is
  the direct byte-for-byte contrast with UA. `DEF-COMMON-SIZE 0023 F` and `0023 G` (34 + name length, [C120]), NO
  SP-cell/pad [H4]. *Falsifier:* a `C9` after the STOP body, or none after the assignment body — H3 is then wrong in
  that direction and the RET rule must be re-derived.

### 5. Campaign + arm contract (hop 3)
ONE grouped run `PLI_SRC=probes timeout 900 python3 oracle/batch.py E52UA E52UB E52UC E52UD E52UE E52UF --tag e52p8
--switches '$L$D'`, rc read DIRECT (never a pipeline tail); every `.PRN` read; goldens reldumped to `build/e52p8/`;
classify honestly (`dr-refuses` / `my-gap` / `unmeasured`), keep every MISS verbatim, commit goldens VERBATIM.
Arm ONLY measured shapes: (a) a SECOND prefix encoder beside `on_reg_prefix` (never mutate the file one) emitting
`LXI H,<abs>` + `XRA A` + `CALL ?ONCOP` + `C3`; (b) the BODY-DEPENDENT tail — suppress the `C9` when the handler's last
statement transfers unconditionally (GOTO already measured; STOP only if UF measures it), and correct the existing
ENDFILE/UNDEFINEDFILE arms only if the measurement demands it (their regressions stay byte-exact either way);
(c) reuse the [C364] inline-goto + pad/cell machinery wherever the bytes genuinely agree; (d) every unmeasured argument
or handler shape refuses BY NAME with `[TBD]`. Then build rc=0 DIRECT, cmp accepted probes whole-file rc=0,
sweep **114**, markers E46K4/K15/N21/E52PF/PU/PV/RE + SE/SF/SG rc=2, LOAN2 UNMODIFIED POSITIONAL with its new first
blocker recorded VERBATIM (**do NOT chase it**), registration via sanctioned `--update-inventory` + census OWN write
path FIRST, FULL gate rc=0 → `build/gate-e52p8-reg.log`, claim **C366 from MEASURED BYTES ONLY committed BEFORE the
COVERAGE rewrite**, coverage_check + prose rc=0, RESULTS §P3-8 + PLAN §5 row, durables.

### 6. LOAN2 direction (pre-registered, NEVER fit)
If ON ERROR lands, LOAN2's blocker MOVES past line 58 to the first unlowered statement after it. No candidate is
predicted with confidence — LOAN2 63+ mixes GET/PUT/DO/file statements whose first refusal depends on prescan order.
**Record whatever actually happens VERBATIM and do NOT fit, and do NOT fix it in P3-8.**

## Subround P3-9 — OR (`|`) CONDITIONS: the value-level truth-byte fold, the fold-ORDER law, the standalone `< 0` leaf and the DEC zero-literal PUSH-ORDER rule (LOAN2:91 blocker) — PRE-REGISTERED 2026-11-05 (session 01a1ad29, renewal 2/12; hop 3) — **CLOSED 2026-11-06 (hop 7)**

ZERO `ocaml/` byte and ZERO oracle call in this hop; this section and `probes/E52VA..E52VK.PLI`
are committed BY EXPLICIT PATH BEFORE any compiler byte and BEFORE any oracle call.
Ledger ENDS **C366**; gate baseline **1249/186/9/140-0-0 (SUPPORTED 90), census 15/0/26/0**;
binary `9ecea27aa4f2d80f49ad…`. Probe ids `E52V*` and tag `e52p9` collision-grepped EMPTY this
hop in `probes/`, `golden/`, `spec/INVENTORY.txt` and `tools/e2e_gate.py` (all greps rc=1 DIRECT).

### 1. The measured blocker (VERBATIM, re-verified hop 1 at HEAD `4dae78a`, rc=2 DIRECT, NO .REL)
`codegen: condition form not in E2E-3b subset [TBD]: (| (< dl 0) (> dl 2))` — LOAN2:91 `if dl < 0 | dl > 2 then`.
Two confirmed `my-gap`s: the OR composition itself, and the `< 0` leaf (`codegen: < 0 / negative const form
unproven [TBD]`; DR accepts `dl < 0` inside LOAN2's fold — its STANDALONE test form has never been measured).

### 2. EXISTING DR evidence (all re-verified raw at hop 2; scratch `build/e52p9/phaseA-complete.txt`)
- **The fold is VALUE-LEVEL and SINGLE-BRANCHED.** Every OR truth operand ends as a byte whose **bit 7 is
  truth**; operands combine `F5 PUSH PSW` … `C1 POP B / B0 ORA B`; ONE terminal `F2 JP <skip>` reads the fresh
  sign of `ORA B` (jump iff bit 7 CLEAR = condition false). Mirror of [C312]'s ANA shape; flags ride in C unread;
  `DCX H`/`CMA` touch no flags (the hop-1 "inverted polarity" ghost is FALSIFIED — see `LEARNINGS.md` § P3-9 hop 2).
- **LOAN2:91** (`dl < 0 | dl > 2`, FIXBIN): `2A C802 LHLD dl / 2B×3 / 7C MOV A,H / 2F CMA / F5 / 3A C902 LDA dl_hi /
  C1 / B0 / F2→0360` — **17 bytes**; the RIGHT operand (bias ladder, truth bit = ¬bit7(H(dl−3))) is computed and
  PUSHED FIRST; the LEFT operand (`LDA` of the high byte) arrives LAST into A. Body at 0359 (`signal error` —
  recorded OUT OF SCOPE: DR lowers it `21 00 00 / AF / CD ?SIGOP`).
- **LOAN2:113** (`P = 0 | dl > 1 | m = fm`, 3 operands): operand bools arrive in SOURCE order (DEC `P=0` materialiser
  first, ladder second, `?IS22N` third), each later operand's first ADDRESS LOAD hoisted above the `F5` ([C105] law
  verbatim), TWO chained `F5/C1/B0` folds, ONE `F2→0603`.
- **LOAN2:120** (`m = fm & dl > 0`, AND region at 0603 = 113's JP target): `dl > 0` materialises as the 0−value
  MEMORY compare `AF / BE / 23 / 9E` (bit 7 of 0−dl = truth), `LXI H,dl` hoisted above `F5` — identical to [C105]/
  [C128]/[C310] (`k > 0` row). AND needs NOTHING new.
- **ANNUITY:46** (`PV = 0 | PMT = 0`, DEC dec(9,2)/dec(7,2)): op1 `21 1F01 / 3E 09 / CD ?DLDOP / 21 E300 / 3E 09 /
  CD ?DLDOP / CD ?DCMOP / D6 01 / 9F` — **ZERO LITERAL pushed FIRST, variable second**; op2 `21 1B01 / F5 / 3E 07 /
  CD ?DLDOP / 21 E800 / 3E 07 / CD ?DLDOP / CD ?DCMOP / D6 01 / 9F` (LXI hoisted, MVI after the push); `C1 / B0 /
  F2→01B6`. Single-condition controls 01B6/022F = bare compare + `C2 JNZ skip`, NO materialiser ([C085] holds).
- **THE CONTRADICTION (probe-decided, NEVER fit):** LOAN2:113 op1 pushes **VAR FIRST** (`21 CA02` then literal `21 E601`).
  Same relation, same `var = 0` shape, opposite push order. Two candidate laws fit BOTH witnesses exactly:
  **ADD** "push the operand with the HIGHER 16-bit address first" (LOAN2 P@02CA > pool@01E6 ⇒ var first ✓;
  ANNUITY PV@00E3 < pool@011F ⇒ literal first ✓); **PAR** "width-parity: odd decimal digit count pushes the literal
  first, even pushes the variable first" (9,7 ⇒ literal first ✓; 10 ⇒ var first ✓). A third candidate (per-program
  constant) predicts uniform order inside every one object.

### 3. Hypotheses (byte-exact; NEVER fit; every MISS recorded VERBATIM)
- **H1 — the fold.** `a | b` = truth bytes per operand (operand-specific materialisers unchanged), `F5` between,
  `C1 / B0` fold, ONE terminal `F2 JP skip→continuation`. 3+ operands chain `F5/C1/B0` pairs, still ONE branch
  (113's law). *Falsifier:* two branches, or a condition-cell/branch-per-operand short-circuit shape.
- **H2 — fold ORDER.** Candidates: **SN** "source order EXCEPT an `LDA`-style `< 0` operand is computed LAST"
  (fits 91 AND 113); **RB** "binary right-first fold, right-assoc chain" (fits 91 alone); **LB** pure source order
  (falsified by 91 in advance — VB must reproduce 91 by determinism). *Discriminators:* **VC** head byte —
  SN ⇒ `2A` ladder head (VC region == VB region verbatim); RB ⇒ `3A C9..` first. **VE** (`dl = 0 | dl > 2`, no
  `< 0`): SN/LB ⇒ head `21 C8..` (=0 first); RB ⇒ head `2A C8..` (ladder first). **VF** (4 operands): SN ⇒ head
  `21` (=0), three `F5`s, `dl < 0` LAST (chain law survives 3); RB ⇒ reversed operand emission.
- **H3 — standalone `< 0` (VA).** UNMEASURED form; DR must accept (LOAN2 proves parse+type). PRIMARY:
  `3A <r data dl_hi> / B7 ORA A / F2 <slot→continuation>` (LDA sets no flags ⇒ the ORA is required; skip iff
  bit 7 clear = false). COMPETING: bias-0 ladder `2A <r dl> / 7C MOV A,H / B7 / F2 <slot>`. *Falsifiers:* any
  refusal (form becomes `dr-refuses` and the leaf stays un-armed), `E4 JM` polarity, a materialiser (`D6 01/9F`),
  or a `DB nn` mystery (then the hop-2 `2F` pinning itself is in doubt).
- **H4 — separate cells (VD).** Same 17-byte fold with independent relocs: ladder reads `r(data b)`, the `< 0`
  operand reads `r(data a + 1)` (reloc EXACTLY one past the declared cell, as LOAN2's `C9 = dl+1`).
- **H5 — FIXBIN `= 0` as an OR operand (VE).** Materialiser VERBATIM [C310] `k = 0` row `21 <r dl> / 7E / 23 / B6 /
  D6 01 / 9F` (FF/00 — bit 7 = truth), then the ladder operand with its `LHLD`+`DCX×3` hoisted above `F5`,
  `7C / 2F / C1 / B0 / F2`.
- **H6 — 4-operand chain (VF).** 3×(`F5 … C1 B0`), ONE `F2`; per-operand materialisers unchanged (`= 0` [C310],
  `> c` ladder `7C/2F`, `< 0` `3A hi`). Fold region 38 bytes (addressed layout below); a 4-operand short-circuit
  or a branch per operand FALSIFIES the single-branch law past 3.
- **H7 — DEC push order (VG/VI).** VG replicates ANNUITY (widths 9,7) — BOTH rules predict literal-first there,
  so VG is pure witness re-verification. **VI** puts dec(10,2) and dec(9,2) in ONE object: **PAR** predicts
  statement 1 `p = 0` VAR-first (even 10) and statement 2's `q = 0` LITERAL-first (odd 9) — MIXED inside one
  object; **ADD** predicts literal-first for BOTH operands whose literal pool cell outs addresses the variable
  cells; **program-constant** predicts uniform. Also re-measured: the dec(10,2) zero cell must appear ONCE for
  both statements ([C155] content dedup; *falsifier:* two identical cells).
- **H8 — OR with ELSE (VH).** Identical fold bytes; terminal `F2` slot patches to the ELSE body; THEN body ends
  with the `C3 <slot>` over-else chain (two independent patch targets) — mirrors [C312]'s measured AND-with-else.
  *Falsifier:* `F2` → continuation (else via a different dispatch) or one merged slot.
- **H9 — `dl > 0` inside an OR (VJ).** Memory-compare materialiser `21 <r dl> / AF / BE / 23 / 9E` (bit 7 of
  0−dl = truth), `LXI` hoisted above `F5` when the operand is not first ([C128]/[C105] law) — measured today
  ONLY inside AND; OR placement predicted under SN as operand 1 here, so `21 r(dl) / AF / BE / 23 / 9E / F5 /
  3A <r dl_hi> / C1 / B0 / F2`; RB predicts the `3A` emission first.
- **H10 — grouping / value position (VK).** Three UNMEASURED shapes recorded VERBATIM, NO byte prediction
  (precedent E52SE/SG `[TBD]`): `dl < 0 | m = fm & dl > 2` (precedence `&`> `|`), `(dl < 0 | dl > 2) & m = fm`
  (parenthesised group inside AND), and `b = (dl < 0 | dl > 2);` (OR in VALUE position, [C310] family — store
  tail `32 <b>`). Whatever DR does is evidence; my compiler continues to refuse every unmeasured shape BY NAME.

### 4. Probes E52VA..VK (11; `dcl dl fixed binary; dcl x fixed bin;` skeleton of E52UA/E52SA — CRLF, bare `^Z`
last byte, ≤71 columns)
**DEVIATION, recorded honestly (AGENTS.md: repository/evidence wins over a document's quotation):** the hop-2
brief wording specified a trailing `put edit(x)(a);`. That exact tail appears ONLY in MY leaf probes
(`build/e52p9/leaves/`, compiled by MY binary, rc=0) — an `A` edit on an arithmetic item has NO DR-accepted
golden anywhere (`a`-on-string and picture-on-number are the measured console EDIT shapes; `put list` numeric
is measured). A refusal on the tail would kill ALL eleven goldens, so the probes carry NO put: the continuation
is `x = 2;` (E52UA-proven). Byte predictions below cover the CONDITION regions, which are the science; whole-file
cmp at arm time verifies the rest. Entry `01 00 02 / CD <r ?START>` @0000 and epilogue `CD <r ?STOPX>` and the
`x = k` form `21 kk 00 / 22 <r data x>` are the established laws. `dl`@data 0 ⇒ `LHLD/LXI r(data 0)`, `dl_hi`
= reloc `data 1`; `x`@data 2.
- **E52VA** `if dl < 0 then x = 1;` `x = 2;` — PRIMARY fold region 6 B `3A r1 / B7 / F2 <slot→0011>` @0006-000B ·
  body `x = 1` @000C-0010 · `CD ?STOPX` @0011 → **DEF-CODE-SIZE 0014**, DATA 0004. Ladder competitor: 7 B,
  CODE 0015.
- **E52VB** `if dl < 0 | dl > 2 then x = 1;` `x = 2;` — 17-byte fold @0006-0016 `2A r0 / 2B 2B 2B / 7C / 2F / F5 /
  3A r1 / C1 / B0 / F2 <slot→001C>` · body @0017-001B · epilogue @001C → **CODE 001F**, DATA 0004. Prediction =
  LOAN2:91 region verbatim (all surviving hypotheses agree).
- **E52VC** `if dl > 2 | dl < 0 then x = 1;` `x = 2;` — SN ⇒ region BYTE-IDENTICAL to VB; RB ⇒ `3A r1 / F5 /
  2A r0 / 2B×3 / 7C / 2F / C1 / B0 / F2` (same 17 B, head `3A`). **CODE 001F** either way; DATA 0004.
- **E52VD** `dcl a fixed binary; dcl b fixed binary;` `if a < 0 | b > 2 then x = 1;` `x = 2;` — predicted fold
  `2A r(data 2) / 2B×3 / 7C / 2F / F5 / 3A r(data 1) / C1 / B0 / F2`; **CODE 001F**, **DATA 0006** (a@0,b@2,x@4).
- **E52VE** `if dl = 0 | dl > 2 then x = 1;` `x = 2;` — SN: `21 r0 / 7E / 23 / B6 / D6 01 / 9F` (8) then hoisted
  `2A r0 / 2B×3` (6) `F5` `7C / 2F` `C1 / B0` `F2` = **22-byte fold** @0006-001B · body · epilogue → **CODE 0024**;
  RB competitor: ladder head, same length. DATA 0004.
- **E52VF** `dcl m fixed binary;` `if dl = 0 | dl > 2 | m > 1 | dl < 0 then x = 1;` `x = 2;` — SN chain: op1 8 B
  (=0) · op2 11 (ladder `2B×3`) · op3 10 (ladder `2B×2` on m) · op4 6 (`F5 / 3A r(dl+1) / C1 / B0`) · `F2` 3 =
  **38-byte fold** @0006-002B → **CODE 0034**; DATA 0006 (dl@0,m@2,x@4). Three `F5`, three `C1/B0`, ONE `F2`.
- **E52VG** `dcl pv fixed dec(9,2); dcl pmt fixed dec(7,2);` `if pv = 0 | pmt = 0 then x = 1;` `x = 2;` — ANNUITY
  replica: op1 17 B `21 <r zero9> / 3E 09 / CD ?DLDOP / 21 <r pv> / 3E 09 / CD ?DLDOP / CD ?DCMOP / D6 01 / 9F`;
  op2 20 B `21 <r zero7> / F5 / 3E 07 / CD ?DLDOP / 21 <r pmt> / 3E 07 / CD ?DLDOP / CD ?DCMOP / D6 01 / 9F`;
  `C1 / B0 / F2` → **42-byte fold**, **CODE 0038**; DATA = pv 5 + pmt 4 + x 2 + two pooled zero cells (5+4) —
  exact DEF-DATA-SIZE follows the established cell/pool law, NOT guessed here (cmp verifies).
- **E52VH** `if dl < 0 | dl > 2 then x = 1;` `else x = 2;` `x = 3;` — fold 16 B + `F2 <slot1→else>` · then body
  `21 01 00 / 22 r2 / C3 <slot2→cont>` · else body 5 · continuation 5 · epilogue 3 → **CODE 002C**, DATA 0004;
  TWO patch targets independent (slot1 = else start 001F, slot2 = continuation 0024).
- **E52VI** `dcl p fixed dec(10,2); dcl q fixed dec(9,2); dcl dl fixed binary;` stmt1 `if p = 0 | dl > 1 then
  x = 1;` stmt2 `if q = 0 | p = 0 then x = 2;` each followed by `x = k;` — H7's decisive object: **PAR** ⇒ stmt1
  op1 VAR-first (`21 r(p) / 3E 0A / … / 21 r(zero10) / …`), stmt2 op1 `q = 0` LITERAL-first (odd 9), stmt2 op2
  `p = 0` VAR-first; **ADD** ⇒ literal-first wherever the pool cell outs addresses the variable. ONE shared
  dec(10,2) zero cell and ONE dec(9,2) zero cell ([C155]).
- **E52VJ** `if dl > 0 | dl < 0 then x = 1;` `x = 2;` — SN: `21 r0 / AF / BE / 23 / 9E` (6) `F5` `3A r1` `C1 B0`
  `F2` = **16-byte fold** @0006-0015 → **CODE 001E**, DATA 0004; RB competitor emits the `3A` operand first
  (same length). Head byte `21` vs `3A` discriminates.
- **E52VK** three boundary statements (`m`,`fm` fixed bin; `b` bit(1)): `if dl < 0 | m = fm & dl > 2 then x = 1;`,
  `if (dl < 0 | dl > 2) & m = fm then x = 3;`, `b = (dl < 0 | dl > 2);` each followed by `x = k;` — NO byte
  prediction (`[TBD]`); DR verdicts recorded VERBATIM.

### 5. Campaign + arm contract (hops 4+)
ONE grouped run `PLI_SRC=probes timeout 900 python3 oracle/batch.py E52VA E52VB E52VC E52VD E52VE E52VF E52VG
E52VH E52VI E52VJ E52VK --tag e52p9 --switches '$L$D'`, rc read DIRECT (never a pipeline tail); EVERY `.PRN`
read; goldens committed VERBATIM; classify honestly (`dr-refuses` / `my-gap` / `unmeasured`); every MISS kept
verbatim. Arm ONLY measured shapes: an `Ast.Or` arm in `lower_test_skip0` + the Or fold BESIDE the And fold in
`lower_bool` (NEVER alter And), a `< 0` leaf arm ONLY if VA measures one, the DEC push-order rule ONLY if VI/VG
pin it (else DEC operands inside OR refuse BY NAME), `= 0`/`> c`/`> 0` operand materialisers reused from their
registered laws verbatim; anything beyond the measured operand classes refuses BY NAME `[TBD]`. `prescan_cond`
already descends `Ebinary` GENERALLY (line ~3410) — audit pool-demand parity (one predicate per cell; [C155])
at arm time. Then build rc=0 DIRECT + per-File codegen warning histogram vs **68**; cmp accepted probes
WHOLE-FILE vs `golden/e52p9/`; sweep `python3 build/e52p3/sweep.py E46N E46K E51 E52 P086 R10` FAILS 0; markers
(copy of `build/e52p8-reg/markers.py` — MUST materialise CRLF + bare `^Z`) rc=2 MARKER_FAILS 0; LOAN2/EXPR1/EXPR2
POSITIONAL VERBATIM — record whatever new blocker appears, NEVER fix it (`?SIGOP`/`signal error` and anything
past the OR are OUT OF SCOPE). Registration from **1249**: SPECIMENS +N, sanctioned `--update-inventory`,
census OWN write path FIRST, FULL gate rc=0 → `build/gate-e52p9-reg.log`, claim **C367 from MEASURED BYTES ONLY
committed BEFORE the COVERAGE rewrite** (a new `COND.OR` row needs an EXPLICIT `spec/COVERAGE-IDS.txt` edit;
NEVER `coverage_gen.py`), coverage_check + prose rc=0; RESULTS §P3-9 + PLAN §5 row + §P3-9 CLOSED; durables.
**STOP at P3-9 closure — do NOT start P3-10.**

### 6. LOAN2 direction (pre-registered, NEVER fit)
If the OR fold + `< 0` leaf land, LOAN2's blocker moves PAST line 91. LOAN2 113 needs the 3-operand fold and the
DEC-push-order law (H7) to be pinned by VI/VG; 120's AND is already armed; `signal error` (91's body) will hit the
UNARMED `?SIGOP` lowering — the first refusal may well be a new shape entirely. **Record whatever actually happens
VERBATIM; do NOT fix, do NOT fit.**

## Subround P3-10 — SIGNAL condition lowering + the `?SIGOP` ABI + the lost-argument frontend repair (LOAN2:92 blocker) — PRE-REGISTERED 2026-11-07 (operator brief E2E-52/P3-10; baseline HEAD `ec3ff7b`, ledger ENDS C367, inventory 1260/186, coverage 141/91) — **CLOSED 2026-11-07 (hop 3)**

### 1. Measured blocker (VERBATIM, census record at HEAD `ec3ff7b`, gate `build/gate-e52p9-reg.log`)

`codegen: statement kind not in supported subset [TBD] (line 92)` rc=2, NO .REL —
LOAN2 line 92 `signal error;` (the THEN body of the line-91 OR condition). CLASSIFICATION
`my-gap`: DR ACCEPTS the statement; its object carries the lowering (decoded below).

### 2. EXISTING DR evidence (Phase A audit this session, ZERO oracle, goldens untouched;
raw bitstream reldumps + annotated disassembly in ignored `build/e52p10/`)

SIGNAL witnesses exist in EXACTLY FOUR original objects (full-corpus scan of every
`golden/first/*/[A-Z]*.REL` for a decoded `?SIGOP` chain record; `?SIGNA` appears in
`spec/notes/plilib-routines.txt` but in NO object):

| Witness | Condition | Argument form | Operand bytes | Condition-code bytes | Helper | Relocation family | CODE offset |
|---|---|---|---|---|---|---|---|
| LOAN2:92 | error | bare | `21 00 00` ABS (DATA, no RELOC) | `AF` (XRA A, A=00) | `?SIGOP` | CALL slot 035E LINK-CHAIN-EXT; nothing else | 0359-035F (7 B) |
| EXPR1:58 | error | `(1)` | `21 01 00` ABS | `AF` | `?SIGOP` | slot 017A CHAIN-EXT | 0175-017B (7 B) |
| EXPR1:61 | error | `(1)` | `21 01 00` ABS | `AF` | `?SIGOP` | slot 0192 CHAIN-EXT | 018D-0193 (7 B) |
| EXPR2:87 | error | `(1)` | `21 01 00` ABS | `AF` | `?SIGOP` | slot 0242 CHAIN-EXT | 023D-0243 (7 B) |
| EXPR2:90 | error | `(1)` | `21 01 00` ABS | `AF` | `?SIGOP` | slot 025A CHAIN-EXT | 0255-025B (7 B) |
| COPYLPT:70 | endpage | `(printfile)` | `21` + RELOC **common@0000** (group PRINTF, size 002B, selected earlier by SEL-COMMON) | `3E 08` (**MVI A,08**) | `?SIGOP` | slot 02B0 CHAIN-EXT | 02AA-02B4 (11 B) |

Control witness (ON route, same object): `on endpage(printfile)` registration at COPYLPT
0254 = `LXI H,*C(PRINTF) / MVI A,08 / CALL ?ONCOP / C3 02AA` — the ENDPAGE discriminator
**08** is IDENTICAL on both helpers; the file-operand prefix is byte-for-byte the [C109]/
[C202] file prefix. ENDFILE carries 05 [C120], UNDEFINEDFILE 06 [C364] on the ON route.

Structural facts read directly from the records (original DR evidence, PANEL-UNVERIFIED
until this campaign's probes land):
- SIGNAL is a PURE statement: NO jump-over slot, NO inline handler, NO recovery pad, NO
  SP-save cell, NO ON-stack registration at any of the six sites. Bytes = LXI (3) +
  A-byte (1 via `AF`, or 2 via `3E nn`) + CALL (3).
- The ERROR argument is the 16-bit LITTLE-ENDIAN LXI operand VERBATIM (bare/0 = 0000,
  1 = 0001) with NO relocation — the C366 ON-ERROR law mirrored; the four error(1)
  sites are mutually identical.
- The FILE form relocates the LXI operand into the file's named COMMON group exactly as
  `on_reg_prefix`/`load_file_cb` do (the group-selection record is emitted only when the
  selected group CHANGES, [C202]).
- Jump patching is unaffected: LOAN2's enclosing IF `F2` (0356) patches to 0360 = the
  statement AFTER the 7-byte signal; EXPR1's `C3` (0172) skips to 017C likewise.
- The CALL operand slot bytes are `00 00` DATA plus a `LINK-CHAIN-EXT` record naming
  `?SIGOP` (external name resolved by LINK-80, never by the compiler).

Manual (extracted language manual sec 8.6 / B.27) documents only `SIGNAL condition;` and
lists the recognized conditions (ERROR, FIXEDOVERFLOW, OVERFLOW, UNDERFLOW, ZERODIVIDE,
ENDFILE, ENDPAGE, UNDEFINEDFILE, KEY); the distribution's own programs prove argument
forms EXIST and compile. Manual prose is documentation, NEVER a claim.

EXISTING CLAIMS BORROWED AS ANALOGY (NOT evidence about SIGNAL): C366 (ON ERROR
argument = LXI operand, abs, bare=0000), C109/C120/C202/C364 (file ON prefix, SEL-COMMON
change-rule, condition codes 05/06), C367 (the OR fold reused by probe WK), C206/C208/C109
(pad/SP-cell/adjacency geometry for WJ).

HYPOTHESES AWAITING DIRECT TEST (nothing below is inferred from the six witnesses alone):
acceptance of subcodes 0/2/255/256 in SIGNAL; expression and variable arguments; a bare
file condition WITHOUT argument; the ENDFILE discriminator through SIGNAL; interaction
with a registered handler; SIGNAL under IF.

### 3. Hypotheses (byte-exact; NEVER fit; every MISS recorded VERBATIM)

- **H-A** (WA): standalone `signal error;` = EXACTLY `21 00 00 / AF / CD <slot>` (7 B),
  LXI operand ABSOLUTE (no RELOC record), slot chained `?SIGOP`; the `x = 2` statement
  begins at the very next byte; nothing else in the object changes. Falsifiers: `3E 00`
  for `AF`; any extra CALL/JMP; a RELOC on the operand; any pad/registration bytes.
- **H-B0** (WB): `signal error(0);` accepted, byte-identical to H-A (`21 00 00`).
  Falsifier: DR refusal (record VERBATIM, no golden).
- **H-B2** (WC): `signal error(2);` = `21 02 00 / AF / CD ?SIGOP` (argument verbatim).
- **H-C255** (WD): `signal error(255);` accepted with operand `FF 00` (16-bit verbatim).
- **H-C256** (WE): UNKNOWN verdict — accept with operand `21 00 01` vs `dr-refuses`
  (documented subcode range 0-255; the COMPILER's acceptance rule is unmeasured). Either
  outcome is kept; NO invented golden if refused.
- **H-D1** (WF): `signal error(1+1);` — UNKNOWN. If accepted: competing emission
  hypotheses (folded absolute `21 02 00`; or runtime evaluation sequence). Refusal is a
  legitimate `dr-refuses` outcome.
- **H-D2** (WG): `signal error(n);` dynamic — UNKNOWN; if accepted, decode, do NOT
  generalize to arbitrary expressions from one witness.
- **H-E1** (WH): `signal endpage(pf);` accepted, 11 B = `21` + RELOC common@0 (PF group)
  `/ 3E 08 / CD ?SIGOP`; SEL-COMMON record only when the selected group changes [C202];
  COMMON PF group size per the established plain-file mechanism (E52UF measured 0023).
  Falsifiers: `AF` instead of `3E 08`; a DATA/code relocation on the operand; a different
  discriminator byte; a jump-over slot.
- **H-E2** (WI): `signal endfile(f);` — does SIGNAL's A byte track the ON condition codes
  (ENDFILE 05 [C120])? Predict accept + `3E 05`; competitors: a different byte, refusal.
- **H-F** (WJ): with `on error(1) x = 1;` present, the registration stays EXACTLY the
  C366 bytes, the SIGNAL adds its 7 bytes after the jump-over target, DATA stays 0002
  (returning handler: NO SP cell, NO pad — C366/H4), no new prescan demand. Falsifier:
  any byte/size change outside the added 7-B region.
- **H-G** (WK): the line-91 fold region byte-for-byte from the E52VB golden (17 B, C367)
  with the terminal `F2` patched to the continuation address = signal start + 7, and
  `x = 2` immediately after; the OR encoder is NOT modified to fit SIGNAL.
- **H-X** (WL): bare `signal endfile;` — UNKNOWN verdict and UNKNOWN operand (0000? a
  default FCB? refusal). Manual-example form with NO object witness.

Deliberately NOT probed (no discriminating question within budget; kept UNMEASURED and
refused BY NAME in my compiler): `SIGNAL ... FROM(expr)` (parser's FROM field — no
historical witness anywhere); multiple arguments `error(1,2)`; other condition names
(CONVERT/OVERFLOW/ZERODIVIDE/KEY/FIXEDOVERFLOW) through SIGNAL; `signal undefinedfile(f)`
(duplicates WI's question).

### 4. Probes E52WA..WL (12; CRLF, bare `^Z`, <=71 cols, E52UA/E52UF skeletons)

Sources in `probes/E52W{A..L}.PLI` committed with this PLAN BEFORE any oracle call and
BEFORE any `ocaml/` byte (blobs, not mtimes, prove the ordering).

| Probe | Statement(s) under test | Panel | Prediction |
|---|---|---|---|
| E52WA | `signal error;` + `x = 2;` | A | H-A, 7 B abs-LXI/XRA/CHAIN-EXT |
| E52WB | `signal error(0);` | B | H-B0 = H-A bytes |
| E52WC | `signal error(2);` | B | H-B2 `21 02 00` |
| E52WD | `signal error(255);` | C | H-C255 `21 FF 00` |
| E52WE | `signal error(256);` | C | H-C256 UNKNOWN verdict |
| E52WF | `signal error(1+1);` | D | H-D1 UNKNOWN |
| E52WG | `n = 1; signal error(n);` | D | H-D2 UNKNOWN |
| E52WH | `dcl pf file; signal endpage(pf);` | E | H-E1 11 B, A=08 |
| E52WI | `dcl f file; signal endfile(f);` | E | H-E2 A=05? |
| E52WJ | `on error(1) x = 1; signal error(1); x = 2;` | F | H-F |
| E52WK | `if dl < 0 \| dl > 2 then signal error; x = 2;` | G | H-G |
| E52WL | `signal endfile;` (no argument) | extra | H-X UNKNOWN |

error(1) is NOT re-probed: four original witnesses already decide it (merged per the
brief). Every probe carries a following statement so the continuation is measurable.

### 5. Campaign + frontend + arm contract (hops 2+)

ONE grouped run: `PLI_SRC=probes timeout 900 python3 oracle/batch.py E52WA E52WB E52WC
E52WD E52WE E52WF E52WG E52WH E52WI E52WJ E52WK E52WL --tag e52p10 --switches '$L$D'`,
rc DIRECT; read EVERY `.PRN`; classify accepted/refused honestly; goldens committed
VERBATIM before any emitter code.

FRONTEND REPAIR (after the campaign, evidence-first): `Ast.Ssignal` gains
`cargs : expr list` (parser stops discarding `opt_paren_exprs`; `FROM` KEPT as-is);
bind.ml use-walkers (574/1518 sites) traverse `cargs`. This representation change is an
engineering correction, NOT a DR hypothesis; it must not widen what the codegen admits.
Test AST preservation explicitly even for forms the emitter still refuses.

ARM (codegen, measured shapes ONLY): a `Ssignal` statement arm — bare/integer-literal
ERROR within the range DR measured on WD/WE (emit `on_error_reg_prefix`-style ABS
LXI + `AF` + `call_ext "?SIGOP"`; NO jump-over, NO handler machinery — SIGNAL is not an
ON registration); file form ONLY for conditions whose discriminator byte this campaign
measures (endpage 08 from the original + WH; endfile 05 ONLY if WI accepts and shows
05), via `load_file_cb` + `MVI A,<measured>` + `?SIGOP`. `st.lowered` incremented like
any emitted statement; `st.last_imm <- None` at the call (HL is clobbered — audit the
branch-boundary law [C202] against the accepted goldens, do not assume). Every
unmeasured shape (other conditions, expression/variable args unless a probe pins the
bytes, FROM, multiple args, out-of-range literals) refuses BY NAME `[TBD]`. No
redundant-LXI optimization (no DR witness).

Validation: build rc=0 DIRECT; per-File histogram vs baseline codegen 68 / total 124;
cmp accepted probes WHOLE-FILE vs `golden/e52p10/` (fresh output paths, positional
`pli80c`); sweep `python3 build/e52p3/sweep.py E46N E46K E51 E52 P086 R10` FAILS 0;
markers harness (CRLF+bare `^Z`) rc=2 MARKER_FAILS 0; regressions: E52UA..UF/C366,
E52VA..VK/C367, ENDFILE/UNDEFINEDFILE ON, REVERT, IF/ELSE patching, FILE COMMON,
STOP/CALL/RETURN, all pinned negatives; full negative panel 186 + divergences 9/9.
LOAN2/EXPR1/EXPR2 recompiled POSITIONAL VERBATIM — LOAN2 should move past line 92;
record the ACTUAL new first blocker, do NOT predict it, NEVER fix it. EXPR1/EXPR2 stay
census controls (their own blockers are out of scope).

Registration: SPECIMENS +N for DR-accepted AND byte-exact probes only (baseline 1260),
sanctioned `--update-inventory`, ALWAYS `git diff --cached --stat` before commit (the
operator's `handoff.config.json` NEVER staged); census OWN write path; claim **C368**
written from MEASURED BYTES ONLY, committed BEFORE any `spec/COVERAGE.tsv` touch; new
`COND.SIGNAL` row (EXPLICIT `spec/COVERAGE-IDS.txt` line, NEVER `coverage_gen.py`,
column count from the FIRST NON-COMMENT row); `coverage_check` + `file_prose_check`
rc=0 (141 rows survive + the new one); FULL gate rc=0 -> `build/gate-e52p10-reg.log`.
STOP at P3-10 closure: do NOT implement the next LOAN2 blocker, do NOT start P3-11.

### 6. LOAN2 direction (pre-registered, NEVER fit)

If the measured SIGNAL subset lands, LOAN2 moves PAST line 92. The next refusal is NOT
predicted: later SIGNAL-free statements, REVERT ERROR, GET/PUT shapes or the DEC formal
surface may stop it first. Record the ACTUAL verbatim diagnostic + line and STOP. If
LOAN2 unexpectedly emits a complete .REL, compare byte-for-byte against
`golden/first/LOAN2/LOAN2.REL` and report — do NOT chase the next gap.

### 7. Frontend defect record (accepted, PRE-REGISTERED here, fixed only after the campaign)

`parser.ml` SIGNAL branch consumes `(args)` into `_sargs` and DISCARDS them;
`ast.ml Ssignal` carries only `cond`/`target`. Post-parse the compiler cannot
distinguish `signal error;`, `error(0)`, `error(1)`, `error(2)` or
`endpage(printfile)` — a loss of source semantics, not merely an unimplemented emitter.
Remedy: `cargs : expr list` in the AST (analogous to `Son`/`Srevert`), parser passes the
parsed list, bind use-walkers traverse it; codegen continues to refuse every unmeasured
shape BY NAME. No lowering is ever assigned to `FROM` without a witness.

## Subround P3-11 — PRINT-opened-file PUT eligibility: the line-99 guard and the PAGE/LIST/SKIP routes behind a PRINT OPEN (LOAN2:99 blocker) — PRE-REGISTERED 2026-11-07 (operator brief E2E-52/P3-11; chain 01a1b0c9; baseline HEAD `57e7f62`+guard `f58f64f`, ledger ENDS C368, inventory 1269/187, coverage 142/92) — **CLOSED 2026-11-07 (hop 5)**

### 1. Measured blocker (VERBATIM, census record at `0198fe5`, gate `build/gate-e52p10-reg.log`)

`codegen: PUT FILE(OUTPUT) has no byte-exact DR witness [TBD] (line 99)` rc=2, NO .REL —
LOAN2 line 99 `put file(output) page;` (the THEN body of `if name ^= '' then` at 98, the
file group `OUTPUT` opened ONLY with PRINT-bearing options at 54/56). CLASSIFICATION
`my-gap`: DR ACCEPTS the statement; its own original object carries the lowering at
03AA-03BB (decoded below).

### 2. EXISTING DR evidence (Phase A + hop-1 first-hand raw-record re-verification;
ZERO oracle at pre-registration; dumps in ignored `build/e52p11/` and `build/e52p11/xplan/`)

| Witness | Open (w1) | PUT shape | Statement bytes | Continuation patching | Dump |
|---|---|---|---|---|---|
| LOAN2:99 | 53-56 `title('$con') print pagesize(0)` (2E52) / `title(name) print` (0E52) | bare PAGE | 03AA-03BB = 18 B: `21`+RELOC **common 0x0** / `11 52 06` / `01`+slot 03B1 / CD slot 03B4 CHAIN-EXT `?SIOOP` / CD 03B7 `?PAGOP` / CD 03BA `?QIOOP` | **DOUBLE** SET-LC both to 03BC: LXI B slot 03B1 (@30135→30179) AND the `if name ^= ''` CA skip-slot 03A8 (@30204→30248); 03BC = `call header()` | xplan/LOAN2-full.txt |
| COPYLPT:53 | printfile open w1 `3E52` (title+print+pagesize+linesize) | bare PAGE | 0215-0226 same 18 B | LXI B slot 021C → SET-LC/RELOC code 0x227 (`?STOPX` region) | COPYLPT-reldump.txt |
| P019B | titleless PRINT open w1 `0652` | `list('hello')` | 0063-007C = 26 B: attach 12 + `21`+RELOC data 0x5 / `3E 05` / CD `?SLCTS`@0075 + `?PNCOP`@0078 + `?QIOOP`@007B | slot 006A → RELOC code 0x7D (next console put) | P019B-reldump.txt |
| E46N10 (registered, stream-output route) | `title('N10OUT DAT') stream output` | bare PAGE | 0023-0034 = 18 B (`?PAGOP` bare at 002F-0031, NO count operand) | LXI B slot → 0035 = `?CIOOP` close | E46N10-reldump.txt |
| E46N1 (registered) | stream output + literal title | BARE skip | 0023-0036 = 20 B: attach 12 + `3E 01` + CD `?SKPOP` + CD `?QIOOP` (NO `?PNCOP` — no item chain) | slot 002A → RELOC code 0x37 (close) | xplan/E46N1.txt |
| E46N2 (registered) | same | `skip list('A')` | 0023-0041 = 31 B: attach 12 + skip 5 + `21`+RELOC data 0x9 / `3E 01` / `?SLCTS` + `?PNCOP` + `?QIOOP` | slot 002A → close region 0042 | xplan/E46N2.txt |
| E46L8 (golden, my compiler REFUSES = PU1's program) | NO open | `list(x)` variable | 000C-0025: attach `21` + **LINK-SEL-COMMON F at first use** + RELOC common 0x0 / `11 52 06` / `01`+slot / CD `?SIOOP`, then `2A`+RELOC / `3E 09` / `?QICOP` / `?PNVOP` / `?QIOOP` | slot 0013 → 0x26 (`?STOPX`) | reldump this session |

Open-block geometries (registered goldens, `build/e52p11/xplan/E52T{A,B,C}.txt`):
- E52TA titleless PRINT: entry `01 00 02 CD ?START` 0000-05, prologue `AF 47 C5 33`
  0006-09, block 000A-001A = `21 52 06`/`E5`/`60 68`/`E5 E5 E5 E5 E5`/`21`+RELOC common
  0x0/CD `?OIOOP`@0019 = **17 B** (block+prologue = 21 B, the E46E4 titleless law); CODE
  0035, COMMON PF abs `0024` (34+len, [C120]).
- E52TB literal-title `title('$con') print pagesize(0)`: block 0006-0022 = **29 B**, w1
  `21 52 2e`, literal-title prologue `21`+RELOC data/`3E 04`/`?SLCTS` then `47 C5 33`;
  the `21 00 00`+`E5` word and the FOUR trailing `E5` pushes are part of the TITLED
  route itself, NOT of pagesize — E52TC proves it. CODE 003D, OUTF `0026`.
- E52TC variable varying-title `title(name) print`: block 0006-0020 = **27 B**, w1 `21 52
  0e` (0E52 — NO pagesize bit although TC spells no pagesize), `?SLVTS` route; [C288]
  varying = 2 shorter than literal. CODE 003B.
- E52VA (P3-9): `if dl < 0 then` TEST leaf = `3A`+RELOC data 0x1/`B7`/`F2`+slot = **7 B**;
  immediate store `x = 2` = `21 nn nn`+`22`+RELOC-embedded operand = **6 code bytes**
  (CODE 001C = 6+7+6+6+3 arithmetic re-verified FIRST-HAND this session; the hop-1 note
  "7-B imm store" is hereby CORRECTED to 6).
- SIOMODES pairing (e2e41-p0): the PUT attach word is `0x0652` behind EVERY print/title/
  $con/vartitle open — COPYLPT 021E (page), 029E (skip(4)), 0315 (skip(expr)), 02E1
  (edit), LOAN2 03B3/052B/068A/0796/0813/0830/0951, P019B 006C — the attach is the
  statement's DIRECTION, never a mirror of the open word ([C280]/[C282]).

MY-SIDE PRE-ARM BEHAVIOR (zero-oracle sanity compiles this session, current binary
`a4c0e235ed4bb81fe284…`, `build/e52p11/xplan/sanity.txt`): ALL ELEVEN probes rc=2 at the
line-99 guard `PUT FILE(PF) has no byte-exact DR witness [TBD]` on the PUT's own line —
every OPEN portion (including XB's unmeasured literal-title+print-without-pagesize and
XK's titleless stream-input) lowers today; the refusal is purely the eligibility guard.

GUARD ANATOMY (`ocaml/lib/codegen.ml`, read this session): `lower_open` (~11557) records
`st.file_out <- fu :: st.file_out` ONLY when an option spells `OUTPUT` — a PRINT open
records NOTHING (LOAN2's 54/56 spell no OUTPUT keyword; their file operand is NAMED
`output`, the [C287] trap). The `Pfile` arm (~13778) is the ONE eligibility guard for
LIST, SKIP and PAGE alike (`List.mem fu st.file_out` AFTER per-item
`authorize_file_item`); the `Sk_page` emitter (~12800) is route-independent (`file=Some`
→ bare `CALL ?PAGOP`); the EDIT route deliberately bypasses the guard (P086K [C282]).
NEGATIVE-PANEL CONSTRAINTS: PU1 marker substring `PUT FILE(F) has no byte-exact DR
witness` (no-open LIST) and E41X5 (EDIT-then-no-open) MUST keep firing — no registered
negative pairs a PRINT open with a named PUT (hop-1 collision scan: the two grep hits
were comment prose); E46K10 refuses by ITEM class before the guard; N3_PAGE (console
`put page;`) and E46N21 (LINE with a count) refuse earlier still.

### 3. Hypotheses (byte-exact; NEVER fit; every MISS recorded VERBATIM)

- **H-A** (XA): DR ACCEPTS; open = TA's 21 B verbatim (w1 `52 06`); PAGE = 18 B at 001B,
  attach `11 52 06`, CB operand RELOC common 0x0, `?PAGOP` bare with NO count operand;
  LXI B slot → 0030 = start of `x = 2`; predicted CODE `0036`, one SEL-COMMON PF at the
  open, COMMON PF `0024` (34+2). Falsifiers: attach mirroring the open word; `3E nn`
  before `?PAGOP`; any extra CALL/registration byte; refusal.
- **H-B** (XB): the combination LITERAL-title + print WITHOUT pagesize/linesize — OPEN
  verdict UNKNOWN (absent from the TA..TJ panel; my side accepts it and lowers the 29-B
  TB block with w1 `0E52`). If accepted: PAGE = 18 B, predicted CODE `003E`; competitor:
  the pagesize bit is REQUIRED for PAGE acceptance (refusal), or w1 ≠ 0E52.
- **H-C** (XC): LOAN2:54+99 mirror — TB block verbatim (w1 `2E52`) + 18-B PAGE; accepted;
  predicted CODE `003E`.
- **H-D** (XD): LOAN2:56 mirror — TC `?SLVTS` block (w1 `0E52`) + 18-B PAGE; accepted;
  predicted CODE `003C`.
- **H-E** (XE): PAGE as a conditional THEN-body (LOAN2 98-99 geometry): `if n < 0 then`
  emits the 7-B VA leaf; **DOUBLE back-patch predicted** — the F2 skip slot AND the LXI B
  continuation slot BOTH patch to the start of `x = 2` (LOAN2 patched CA-slot 03A8 and
  LXI-B slot 03B1 both to 03BC); competitor SINGLE-patch (only one of the two moves).
  Predicted CODE `003D`.
- **H-F** (XF): conditional opens + later PAGE (LOAN2 53-56+99 composed): TB block in the
  THEN, else-jump `C3`+slot 3 B, TC block in the ELSE, ONE 18-B PAGE after the merge; F2
  slot → start of ELSE body, C3 slot → start of PAGE, LXI B slot → start of `x = 2`.
  Accepted; predicted CODE `0063`. Falsifier: any branch-local eligibility or pad bytes.
- **H-G** (XG): PRINT open + `list('A')` — the P019B LIST route (26 B, ONE close,
  `?SLCTS`+`?PNCOP`) panel-verified in a minimal whole object. Accepted; predicted CODE
  `003E`. This decides whether the SHARED item emitter is route-independent for LIST.
- **H-H** (XH): PRINT open + bare `skip` — the E46N1 20-B shape (`3E 01`/`?SKPOP`, NO
  `?PNCOP`). Accepted; predicted CODE `0038`.
- **H-I** (XI): PRINT open + `skip list('A')` — the E46N2 31-B shape (skip BETWEEN attach
  and chain; `?PNCOP` appears because a chain follows). Accepted; predicted CODE `0043`.
- **H-J** (XJ): file PAGE with NO open — verdict UNKNOWN. Competitors: `dr-refuses`; or
  accept with the E46L8 geometry (SEL-COMMON at first use + same 18 B; predicted CODE
  `0021` if accepted). Either outcome kept; NO invented golden. My compiler refuses this
  either way (candidate A records OPENs only).
- **H-K** (XK): PAGE behind a `stream input` open — is PAGE a mode question? UNKNOWN
  verdict. If accepted, predicted open = E46E4's 21-B titleless block with w1 `90 06` and
  attach STILL `11 52 06` ([C280] direction law) → CODE `0036`; competitors: refusal, or
  an input-direction attach.

Deliberately NOT probed (kept UNMEASURED, refused BY NAME in my compiler): PAGE+items
(COPYLPT 0268 is the original witness, out of scope this subround); counted PAGE; LINE;
counted/variable-operand skip behind PRINT beyond what XH/XI pin; KEYED, UPDATE, RANDOM;
any console PUT change; `REVERT ERROR`; INPUT-direction named PUTs.

### 4. Probes E52XA..XK (11; sources in `probes/E52X*.PLI`, CRLF + bare `^Z`, ≤71 cols,
first line `E52XX: procedure options(main);`, a statement after EVERY PUT so the LXI B
continuation slot is measurable)

| Probe | Shape | Panel | Prediction |
|---|---|---|---|
| E52XA | titleless `print` open + page + `x = 2` | A | H-A, CODE 0036 |
| E52XB | `title('TEST') print` (no attrs) + page + store | B | H-B, CODE 003E, w1 0E52 |
| E52XC | `title('$con') print pagesize(0)` + page + store | C | H-C, CODE 003E |
| E52XD | `title(name char(14) varying) print` + page + store | D | H-D, CODE 003C |
| E52XE | print open; `if n < 0 then put file(pf) page;` + store | E | H-E DOUBLE patch, CODE 003D |
| E52XF | if/else TB+TC opens; page; store | F | H-F, CODE 0063 |
| E52XG | print open + `list('A')` + store | G | H-G 26 B, CODE 003E |
| E52XH | print open + bare `skip` + store | H | H-H 20 B, CODE 0038 |
| E52XI | print open + `skip list('A')` + store | I | H-I 31 B, CODE 0043 |
| E52XJ | NO open + page + store | J | H-J UNKNOWN verdict |
| E52XK | `stream input` open + page + store | K | H-K UNKNOWN verdict |

### 5. Campaign + arm contract (hops 2+)

ONE grouped run: `PLI_SRC=probes timeout 900 python3 oracle/batch.py E52XA E52XB E52XC
E52XD E52XE E52XF E52XG E52XH E52XI E52XJ E52XK --tag e52p11 --switches '$L$D'`, rc
DIRECT (never a pipeline tail); read EVERY `.PRN`; reldump accepted .RELs into
`build/e52p11/`; goldens committed VERBATIM from the campaign BEFORE any emitter change;
XJ/XK classified honestly (`dr-refuses` → REJECTS + VERBATIM verdict, WL precedent;
accepted-and-mine-refuses → golden KEPT + my-gap REJECTS, SE/E46L8 precedent); NEVER
invent goldens.

ARM (Phase D, AFTER goldens are in git) — the SMALLEST measured rule:
- **Candidate A** — `lower_open` records PRINT-bearing opens into `st.file_out` beside the
  OUTPUT spelling (ONE line; the guard, item authorizers, attach emitter and PAGE emitter
  are UNCHANGED): admitted iff XA..XI all land DR-accepted AND byte-exact through the ONE
  route-independent emitter with NO new statement bytes. This is the general, file-name-
 agnostic rule; NO special-casing of a group named `OUTPUT`.
- **Candidate C** — PAGE-only admission (a `Sk_page`-specific allowance) if any of
  XG/XH/XI refuses or misses byte-exactness while the PAGE probes land; the LIST/SKIP
  guards keep their refusal BY NAME with the message-body prose moved VERBATIM.
- The refusal MESSAGE body may move (it currently cites E16D/E17D and `OPEN 0x0E50`);
  the PU1 substring `PUT FILE(F) has no byte-exact DR witness` MUST survive verbatim.
  BY-NAME refusals KEPT: PAGE+items, counted PAGE, LINE, console PAGE (N3_PAGE), INPUT-
  direction named PUT, no-open PUT (PU1/E41X5/E46L8 class), KEYED etc.

Validation: build rc=0 DIRECT; per-File [TBD] histogram vs baseline codegen 68 / total
124; whole-file `cmp` of every ACCEPTED probe against `golden/e52p11/` (POSITIONAL
`pli80c` into FRESH output paths — a stale output FALSE-PASSes); sweep
`python3 build/e52p3/sweep.py E46N E46K E51 E52 P086 R10` FAILS 0; markers harness
(CRLF + bare `^Z` materialization — `build/e52p8-reg/markers.py` precedent) incl. PU1,
E41X5, E46K10, N3_PAGE, E46N21 → MARKER_FAILS 0; regressions: E46N*/E16D/E17D/E52TA..TJ/
UA..UF/VA..VK/WA..WK whole-file, negative panel 187, divergences 9/9.

Registration: SPECIMENS +N for DR-accepted AND byte-exact probes ONLY (baseline 1269),
sanctioned `--update-inventory`, ALWAYS `git diff --cached --stat` (operator
`handoff.config.json` NEVER staged); census OWN write path. Claim **C369** written from
MEASURED BYTES ONLY, committed BEFORE any `spec/COVERAGE.tsv` touch; PREFER EXTENDING
the existing `FILE.PUT_PAGE`/`FILE.PUT_LIST`/`FILE.PUT_SKIP` rows' probe lists (new rows
ship their `spec/COVERAGE-IDS.txt` line in the SAME change; NEVER `coverage_gen.py`; 15
columns from the FIRST NON-COMMENT row; csv `delimiter='\t'`); `coverage_check` +
`file_prose_check` rc=0; FULL gate rc=0 DIRECT → `build/gate-e52p11-reg.log`. Then
RESULTS §P3-11 + PLAN §5 row + §P3-11 CLOSED + durables.

### 6. LOAN2 direction (pre-registered, NEVER fit)

If the measured PRINT-open eligibility rule lands, LOAN2 moves PAST line 99. The next
refusal is NOT predicted: `call header()` (internal PROCEDURE call), the `do while`
surface, GET/PUT EDIT shapes, the DEC formal surface or the read loop may stop it first.
Record the ACTUAL verbatim diagnostic + line and STOP. If LOAN2 unexpectedly emits a
complete .REL, compare byte-for-byte against `golden/first/LOAN2/LOAN2.REL` and report —
do NOT chase the next gap. **STOP at P3-11: no next-blocker fix, no P3-12.**

### 7. Guard semantics (accepted framing; binding on C369 wording)

`st.file_out` is a COMPILER-SIDE monotonic eligibility list built from the SOURCE
STRUCTURE (an OPEN statement lowered earlier in source order, including inside a
conditional — LOAN2 53-56 opens BOTH branches), NOT a proof of runtime file state: DR
emits the PUT regardless of execution order, and byte-parity is not a runtime claim
(byte-tier-only, PROTOCOL). C369 must say "an OPEN this compiler lowered recorded the
group", never "DR requires the file to be open at runtime".

## Subround P3-12 — DIRECT FIXED-DECIMAL assignment across scales: the shift between the source push and the destination load (LOAN2:111 blocker) — PRE-REGISTERED 2026-11-07 (operator marathon brief; new chain; baseline HEAD `83e82b7`, ledger ENDS C369, inventory 1278/189, coverage 142/92) — **CLOSED 2026-11-07 (hop 4)**

### 1. Measured blocker (VERBATIM, re-measured this session at HEAD `83e82b7`, binary sha256 `25c57e27696421e929b8…`, rc=2 DIRECT, NO .REL)

`codegen: DECIMAL assignment between differing scales is unproven [TBD] (only computed
results are pinned as needing a QDDSL/QDDSR fix; a direct DEC operand store always had equal
scales in the samples)` — the diagnostic carries NO `(line N)` clause. The responsible
statement was MEASURED, not assumed: a TEMPORARY `Printf.sprintf … epos.Source.line` added
to the `dpush` simple-operand refusal (then reverted; fingerprint re-held, tree clean)
reported `(line 111)` = `INF = ci;` (`INF` fixed dec(4,3) @33, `ci` fixed dec(15,14) @34).
Scratch reproducers show BOTH directions refuse today (`a(9,2) = b(4,3)` and `b = a`), while
`ci = 1.00` (literal store role) compiles.

### 2. EXISTING DR evidence (Phase A this session, ZERO oracle; goldens untouched)

| Witness | Shape | DR bytes | Reading |
|---|---|---|---|
| authentic `golden/first/LOAN2/LOAN2.REL` 04B7–04CB (21 B) | `INF = ci` dec(15,14) → dec(4,3) | `21 09 03` LXI H,ci(0309) / `3E 0F` MVI A,15 / CD `?DLDOP`@04BC / **`3E 0B` MVI A,11 / CD `?QDDSR`@04C1** / `21 06 03` LXI H,INF(0306) / `3E 04` MVI A,4 / CD `?DSTOP`@04C9 | DOWN shift sits BETWEEN the source push and the destination load; amount = s_src − s_tgt = 11; A at `?DSTOP` = TARGET precision (4). Decoded first-hand via `build/e52p8/ondump2.py` buffers + `tools/dis80.py` opcode table + CHAIN-EXT names (anchor = opcode+1); `tools/dis80.py` alone prints gaps for RELOC-embedded operands (known limitation). |
| registered negative `golden/negpanel1/NG20/NG20.REL` + `.PRN` (`NO ERROR(S)` both passes) | `c = a` dec(9,2) → dec(9,4) | 0016–0028 `LXI H,A / MVI A,09 / ?DLDOP / **MVI A,02 / ?QDDSL** / LXI H,C / MVI A,09 / ?DSTOP` | UP shift, SAME position, amount = s_tgt − s_src = 2, A at DSTOP = target precision 9. DR **accepts** the class ⇒ the gate's `N35_DEC_STORE_SCALE_DRIFT` is a `my-gap` row and retires to POSITIVE by the N26_DECDIV precedent ([C086]). |
| `artefacts/LOAN1.PLI`:35 `PMT = P` dec(11,2) → dec(6,2), equal scale | control | whole-file `cmp` rc=0 re-measured this session vs `golden/e2e7/LOAN1/LOAN1.REL` (1536 B) | equal-scale cross-PRECISION direct store is already proven exact — NO new probe spent on it. |
| authentic LOAN2.REL 04CC–04EB | `ci = ci / fi` dec(15,14)/dec(7,5) | DLDOP(15) / DLDOP(7) / `?DDVOP` / `MVI A,05 / ?QDDSL` / LXI H,ci / `MVI A,0F` / `?DSTOP` | dividend pre-shift omitted because 15 − p = 0 and the +5 is the CONSUMER fix — matches the ALREADY-ARMED [C086] L3/L5 path ⇒ line 112 is OUTSIDE this slice's perimeter. |
| `golden/negpanel1/NG21` (dr-refuses `SYNTAX ?`, NO .REL) | prints `?QDDSR` in its pass-2 trace | — | **FALSIFIED as evidence**: a listing produced by an erroring pass-2 compile is not a witness; NEVER cite it. |

Cell widths re-confirmed against the [C084] law `bytes = (p+2)/2`: ci(15)=9 at 0309, INF(4)=5
at 0306. Frontend fact learned while authoring probes: `dcl a fixed dec(9,2), b …;` multi-name
lists leave names UNDECLARED here — probe skeletons use one declaration per line (R-probe style).

### 3. Hypotheses (byte-exact; NEVER fit; every MISS recorded VERBATIM)

- **H-1 (candidate law)**: a direct DEC operand store with `s_src ≠ s_tgt` emits
  `MVI A,d / CALL ?QDDSL` (up, d = s_tgt − s_src) or `MVI A,d / CALL ?QDDSR` (down, d = s_src −
  s_tgt) AFTER the source `?DLDOP` and BEFORE `LXI H,<dst>`; `MVI A,<p>` before `?DSTOP` stays
  the TARGET precision; the shift amount NEVER involves a precision. Falsified by any probe where
  the helper is absent, misplaced after the destination load, or whose `MVI` operand ≠ |Δscale|.
- **H-2 (competitor, precision in the amount)**: d = |Δscale| + f(Δp) — falsified the moment any
  probe with Δp ≠ 0 (YB 9→6, YC 6→15, YD 15→4) shows d = |Δscale| exactly.
- **H-3 (competitor, a cap)**: DR refuses/emits something else for large d (only d=2 and d=11 are
  witnessed) — tested by YD (11), YF (14), YG (13).
- **H-4 (competitor, DSTOP rescales with no shift)**: falsified for the UP direction by NG20's
  existing object; the DOWN direction with NO shift would falsify it generally — YB/YE.
- **H-5** (YC): mirrored LOAN2 direction (up by 11) rides `?QDDSL`, proving the law is
  direction-symmetric rather than a one-off.
- **H-6** (YI): `decimal(i,p)` from a FIXED BIN source into a SCALED target — verdict UNKNOWN;
  candidates: QI15D-then-shift, shift-free, or refusal. The current model derives the descriptor
  from the TARGET context ([C084] "the precision argument is ignored"), which predicts NO shift;
  whatever DR does, it is recorded, and the shape is armed ONLY if it is byte-exact through the
  same single emission point.
- **H-7** (YH control): the computed-quotient consumer fix path is UNCHANGED by this slice — it
  must stay byte-exact (its own bytes are already pinned by [C086]).
- **H-8**: no decimal-stack imbalance: every accepted store is exactly one push (`?DLDOP`) and one
  pop (`?DSTOP`), the helper neither pushes nor pops.

### 4. Probes E52YA..E52YI (9; `probes/E52Y*.PLI`, CRLF + bare `^Z`, ≤71 cols, one dcl per line,
`put skip list(<dec var>)` tail — the R711 shape that is already byte-exact)

| Probe | Store | Expected DR sequence at the store | My side TODAY |
|---|---|---|---|
| YA | a(9,2) = b(6,2) | `DLDOP(6,A=06) / LXI H,a / MVI A,09 / DSTOP` — NO helper | compiles (rc=0) |
| YB | a(9,2) = b(9,0) | `DLDOP / MVI A,02 / ?QDDSR / LXI H,a / MVI A,09 / DSTOP` | rc=2 at the guard, `Line 13` (sanity); refusal KEPT whatever DR does (H-E) |
| YC | b(15,13) = a(6,2) | `DLDOP / MVI A,0B / ?QDDSL / LXI H,b / MVI A,0F / DSTOP` | rc=2 |
| YD | inf(4,3) = ci(15,14) = LOAN2:111 verbatim shape | `DLDOP(A=0F) / MVI A,0B / ?QDDSR / LXI H,inf / MVI A,04 / DSTOP` | rc=2 |
| YE | a(9,2) = c(9,0) (equal precision, Δp=0) | as YB | rc=2 |
| YF | b(15,0) = a(15,14), d=14 max | `DLDOP / MVI A,0E / ?QDDSR / LXI H,b / MVI A,0F / DSTOP` | rc=2 |
| YG | a(15,1) = b(15,14), d=13 up | `DLDOP / MVI A,0D / ?QDDSL / LXI H,a / MVI A,0F / DSTOP` | rc=2 |
| YH | c = a / b, computed control | existing [C086] bytes, no change | compiles |
| YI | d(9,2) = decimal(i,7), i fixed bin | UNKNOWN verdict (H-6) | compiles (rc=0) |

Sizes are NOT pre-predicted beyond the statement byte counts (the DATA/AUTO layout is pinned by
whole-file `cmp`, not by arithmetic); the primary discriminators are WHICH scale changes, WHERE
the helper occurs, and WHETHER DR emits a shift at all.

### 5. Campaign + arm contract (hops 2+)

ONE grouped run `PLI_SRC=probes timeout 900 python3 oracle/batch.py E52YA E52YB E52YC E52YD
E52YE E52YF E52YG E52YH E52YI --tag e52p12 --switches '$L$D'`, rc DIRECT; read EVERY `.PRN`;
decode accepted `.REL`s into `build/p3-12/`; goldens committed VERBATIM before ANY `ocaml/` byte;
honest verdicts (DR-accepted / dr-refuses / my-gap), NEVER invent a golden. ARM (after evidence):
the narrow proven law inside the `dpush` simple-operand arm of `ocaml/lib/codegen.ml` ONLY —
replace the blanket `ts <> vd.sc` refusal with the measured shift; do NOT weaken the guard
globally; shapes the panel does not pin (suffix DEC stores, DEC formal/pointer stores across
scales, `decimal()` into scaled targets unless YI pins them) keep explicit [TBD] refusals BY NAME.
Validation: build rc=0 DIRECT; [TBD] histogram codegen 68 / total 124 == baseline; whole-file `cmp`
of every accepted probe (POSITIONAL `pli80c` into FRESH paths); sweep
`python3 build/e52p3/sweep.py E46N E46K E51 E52 P086 R10` FAILS 0; markers harness (CRLF + bare
`^Z`) incl. every DEC negative marker and the N35 retirement decision; DEC regressions (R5xx/R6xx/
R7xx/R8xx, LOAN1 whole-file), negative panel, divergences 9/9; then FULL compile-tier gate rc=0
DIRECT → `build/gate-e52p12-reg.log`. Registration: SPECIMENS + accepted-and-byte-exact only
(baseline 1278), `--update-inventory`, `git diff --cached --stat` (config NEVER staged), census OWN
path; claim **C370** written from MEASURED BYTES ONLY, committed BEFORE any `spec/COVERAGE.tsv`
touch; a NEW row is justified here (no existing contract covers decimal assignment geometry) and
MUST ship its `spec/COVERAGE-IDS.txt` line in the SAME change (NEVER `coverage_gen.py`; 15 columns
from the FIRST NON-COMMENT row; textual tab-delimited edit); coverage_check + prose rc=0; gate
AGAIN; RESULTS §P3-12 + §5 row + **CLOSED**; then proceed to the next ACTUAL LOAN2 blocker under
the marathon authorization (slices P3-13..P3-19 remain available; stop early if LOAN2 is exact).


### 6. LOAN2 direction (pre-registered, NEVER fit)

If the measured direct-store rule lands byte-exact, LOAN2 moves past line 111. The next refusal is
NOT predicted — line 112's divide is armed but line 113's `P = 0 | dl > 1 | m = fm` fold, the
line-115/116 `PUT … EDIT`, and the `call display(<dec expr>,…)` DEC-formal route are all candidate
clusters (reconnaissance only, NOT established blockers). Record the ACTUAL verbatim diagnostic; if
LOAN2 unexpectedly emits a complete `.REL`, go STRAIGHT to whole-file parity against
`golden/first/LOAN2/LOAN2.REL` (sha `712cfcb2…`, never re-derived) and report the first genuine
difference; never patch a byte without an independently demonstrated law.

### 7. Framing binding on C370 wording

Precision and scale are SEPARATE properties: the cell width is the storage law [C084]
(`bytes = (p+2)/2`), the runtime stack entry carries (p, s), and the helper adjusts ONLY the scale
of the TOP entry. C370 must state the shift as a property of the SOURCE push / TARGET store pair as
measured, must not claim numerical/rounding behaviour of `?QDDSR` truncation beyond [C086] L9, and is
BYTE-TIER-ONLY: no runtime, no PLILIB, no CP/M execution claim.

## Subround P3-13 — NON-VARIABLE ACTUALS against FIXED DECIMAL formals: product materialisation into formal-width temps, the C370 shift window at the FORMAL scale, and the pre-scaled literal pool cell (LOAN2:117 blocker) — PRE-REGISTERED 2026-11-07 (operator marathon brief; chain 01a1b1b4 renewal 7/12; baseline HEAD `996038b`, ledger ENDS C370, inventory 1288/188, coverage 143/93) — **CLOSED 2026-11-06 (hop 12)**

### 1. Measured blocker (VERBATIM, re-measured this session against the six new probes)

`codegen: non-variable argument against a FIXED DECIMAL formal is unproven [TBD] (DR passes
an automatic decimal BY REFERENCE -- the descriptor holds LXI H,*A(cell); a literal or
expression decimal argument has no sample [DECPOLY, R2037/R2038/R725]. Line N)` — the guard
spells `Line N` INSIDE the parens (its own dialect). The LOAN2 statement is lines 117-118:
`call display(PL * INF, INT * INF,\nPMT * INF, PP * INF, IP * INF);` — five
`fixed dec(10,2) * fixed dec(4,3)` PRODUCT actuals against five `fixed dec(10,2)` formals
(`display: procedure(a,b,c,d,e); declare (a,b,c,d,e) fixed decimal(10,2);` @142-151).
ZERO-oracle sanity compiles of the six probes on the armed binary `6a4c6c1154a0acd8403b…`
(FRESH positional paths, `build/p3-13/sanity/`) confirm all six refuse TODAY rc=2 with this
guard and NO `.REL` (ZA/ZE Line 12, ZB/ZC Line 10, ZD Line 9, ZF Line 18). The cited
witnesses `[DECPOLY, R2037/R2038/R725]` all pass VARIABLES (Phase A step-3 adjudication:
C093's DECPOLY `*A(005A)=5.67` literal bullet is FALSE AS CITED — correction owed at C371,
dated); the panel-verified literal witness is `golden/negpanel1/NG18/NG18.REL`.

### 2. EXISTING DR evidence (Phase A + hop 5/6, ZERO oracle; goldens untouched)

| Witness | Shape | DR bytes (first-hand re-read this chain) | Reading |
|---|---|---|---|
| authentic `golden/first/LOAN2/LOAN2.REL` 055D–05FA | FIVE product actuals `PL*INF` etc., `dec(10,2)*dec(4,3)` into `dec(10,2)` formals | per arg 32 B: `21 r(var) / 3E 0A / CD ?DLDOP / 21 0306 / 3E 04 / CD ?DLDOP / CD ?DMUOP / 3E 03 / CD ?QDDSR / 21 r(temp) / 3E 0A / CD ?DSTOP` at 055D/057D/059D/05BD/05DD | product scale = 2+3 = 5; DOWN shift d = s_prod − s_formal = 03 sits BETWEEN `?DMUOP` and the temp store (same window as [C370]); `?DSTOP A=0A` = FORMAL precision; temps 6 B (ceil((10+2)/2)=6 [C084]) at 0324/032A/0330/0336/033C, stride 6. |
| same, descriptor vector + call 031A–0323, 05FD–0602 | arity-5 call | DATA bytes EXACTLY `24 03 2A 03 30 03 36 03 3C 03` — five 2-byte LE address constants, each an INLINE DATA RELOC (031A→0324, 031C→032A, 031E→0330, 0320→0336, 0322→033C), STATIC, never runtime-written; call = `21 r(031A)` + `CALL` slot 0601 CHAIN-ADDR → code@0674 | the argument vector is a data-resident list of temp addresses; the call loads its address, not per-arg pushes. |
| same, callee entry 0674–067E + formal reads | arity-5 internal proc | `LXI D,*A(0342) / MVI C,0A / (MOV A,M / INX H / STAX D / INX D / DCR C / JNZ)*` 10 B block copy into callee locals 0342..034B; reads `LHLD(0342+2i) / MVI A,0A / ?DLDOP` | arity ≥2 prologue = 2N-byte block copy ([C094] route, UNCHANGED by this slice); each local is a 2-byte descriptor cell. |
| `golden/negpanel1/NG18/NG18.REL` (panel-verified DR-ACCEPTED; NEG_META of still-refused `N33_DEC_FORMAL` says "DR COMPILES IT") | INT literal `1` vs `fixed dec(9,2)` formal, arity 1, `returns` | caller arg code ZERO runtime bytes; DATA 0000–0004 = `00 01 00 00 00` — a **5 B FORMAL-WIDTH pre-scaled cell** (1→100 at scale 2, [C084] R505 packing law); DATA 000A–000B descriptor cell with INLINE DATA RELOC 000A→0000, `addr:[10]`; call `21 000A` + `CALL` CHAIN-ADDR → code@0035; callee peeled prologue `5E 23 56 EB 22 0C00`; body `2A 0C00 / 3E 09 / CD ?DLDOP / C3 ?DCRET`; return store `21 r(0005) / 3E 09 / CD ?DSTOP` | LITERAL actuals need NO runtime code: a static pool cell + descriptor. **CORRECTION (hop 6, first-hand): the cell is 5 bytes, NOT the 2 bytes of C093's wording** — C371 must correct BOTH C093 errors (false DECPOLY citation AND the 2-byte width; C093's 2-byte cells were the R2033 INT-literal BIN-formal `pool_alloc [|lo;hi|]` route). |
| `build/p3-12/E52YD-reldump.txt` (registered [C370] probe) | `put skip list(dec var)` tail | `LXI D,0252 / LXI B,<slot->?STOPX> / ?SYSPR / MVI A,01 / ?SKPOP / LXI H,*A(v) / MVI A,p / ?DLDOP / MVI A,p+3 / MVI B,s / ?QDCOP / ?PNVOP / ?QIOOP` + main's `CALL ?STOPX`; YD CODE `0041`, 256 B file | continuation-tail shape for the probes; `?QDCOP` width = p+3, scale byte = s. |
| `build/p3-12` literal-store witnesses ([C084] law) | `a(10,2) = 1.5`, `dec(4,3) = 2.5`, `dec(9,2) = 2.5` | cells `50 01 00 00 00 00` / `00 25 00` / `50 02 00 00 00` | pre-scaled packed-BCD literal encodings: LE two digits/byte hi<<4\|lo, sign in last-byte top nibble, value scaled to the TARGET/Formal scale, cell width = (p+2)/2. |

Frontend/guard anatomy (read first-hand, `codegen.ml` 4610–5000): `formal_is_dec` admits ONLY
equal-(p,s) `Eident` (own cell, [C093]) or equal-scale WIDENING `ap<pf` via the [C358] copyin
temp (`Some(t,ap,pf)`); the copyin emission `LXI H,*A(target)/MVI A,ap/?DLDOP; LXI H,*A(t)/
MVI A,pf/?DSTOP` is EXACTLY the LOAN2 temp-materialiser shape (different A-values only) — the
arm can ride existing machinery. The static descriptor emission (~4913) already pushes
`Reloc(Data,tgt)` after `SET-LC(data,slot+2i)` — matches the LOAN2 031A vector. `Enumber`
pool route is armed for BIN (2-byte `pool_alloc`) and FLOAT only; DEC literals fall through
to the guard refusal today.

### 3. Hypotheses (byte-exact; NEVER fit; every MISS recorded VERBATIM)

- **H-1 (product-actual law)**: a DEC expression (product) actual materialises via the FULL
  expression sequence (`?DLDOP` operands, `?DMUOP`) with the scale-align shift
  `MVI A,|s_prod−s_formal| / ?QDDSL`(up)/`?QDDSR`(down) INSIDE the [C370] window (between the
  last arithmetic op and the destination store), then `LXI H,*A(temp) / MVI A,pf / ?DSTOP`;
  the descriptor-vector cell for that arg points at the temp (STATIC inline DATA RELOC).
  Falsified if the shift is absent, misplaced after the `LXI H`, or its amount involves a
  precision.
- **H-2 (temp width = FORMAL precision, [C084])**: bytes = ceil((pf+2)/2), stride = width —
  ZA/ZF pf=10 → 6 B; ZB pf=7 → 4 B; ZE pf=9 → 5 B. Falsified by ANY other stride (e.g.
  expression-context width, or a fixed 6).
- **H-3 (DSTOP A = FORMAL precision)**: `?DSTOP A = pf` always at the materialisation store
  (0A/07/09 per probe). Falsified if A carries the expression/product precision instead.
- **H-4 (shift direction from scales ONLY)**: ZA s5→s2 down `?QDDSR d=03`; ZB s0→s2 up
  `?QDDSL d=02`. Falsified by a direction flip on either (Δp differs between them: −3 vs +5).
- **H-5 (literal-actual law, NG18-generalised)**: a DEC or INT literal actual emits NO caller
  runtime code; DR allocates a STATIC pool cell of FORMAL width pre-scaled to the FORMAL
  scale, plus a descriptor cell with an inline DATA RELOC → value cell. ZC `1.5`@dec(9,2) →
  `50 01 00 00 00`; ZD `1`@dec(9,2) → `00 01 00 00 00` (NG18 verbatim shape). Falsified if a
  literal takes a runtime materialisation, the cell is NOT pre-scaled/formal-width, or DR
  refuses (honest `dr-refuses`, NO invented golden).
- **H-6 (variable actuals unchanged)**: a `dec` variable matching the formal passes its OWN
  cell descriptor (existing [C093] route); mixed var/expr/literal actuals share ONE
  INTERLEAVED descriptor vector in arg order (LOAN2's vector is arg-ordered; a pure
  variables-plus-expressions split-vector competitor is falsified by ZE if it lands).
- **H-7 (callee prologue)**: arity 1 = peeled 5 B (`MOV E,M/INX H/MOV D,M/XCHG/SHLD loc`);
  arity N≥2 = block copy `MVI C,2N` (ZE `06`, ZF `0A`) into consecutive 2 B locals; formal
  reads `LHLD(loc+2i) / MVI A,pf / ?DLDOP` ([C094], UNCHANGED).
- **H-8 (ZF = LOAN2 replication)**: five 32 B product blocks + 6 B temps stride 6 + static
  5-cell vector + `LXI H,*A(vec)/CALL`; a runtime-written vector (SET-LC/SHLD) falsifies the
  static-vector law.

### 4. Probes E52ZA..E52ZF (`probes/E52Z{A..F}.PLI`, CRLF + bare `^Z`, ≤71 cols, one dcl per
line, `E52Zx:` first-line label, continuation `put skip list` after the call) — per-probe
pre-registered byte predictions at the actual site (NEVER fit):

| Probe | Actuals | Predicted DR arg-materialisation bytes | My side TODAY |
|---|---|---|---|
| ZA `p = q(a*b)` | a dec(10,2), b dec(4,3); formal dec(10,2) | `LXI H,*A(a) / MVI A,0A / ?DLDOP / LXI H,*A(b) / MVI A,04 / ?DLDOP / ?DMUOP / MVI A,03 / ?QDDSR / LXI H,*A(t) / MVI A,0A / ?DSTOP` (32 B); t = 6 B; vector 1 cell → t (DATA reloc); q reads `LHLD / MVI A,0A / ?DLDOP` | rc=2 at the guard (Line 12) |
| ZB `p = q(a*b)` | a dec(9,0), b dec(8,0); formal dec(7,2) | same shape with `MVI A,09`, `MVI A,08`, `?DMUOP`, **`MVI A,02 / ?QDDSL`** (up), `MVI A,07` at DSTOP; t = **4 B** (stride discriminates H-2) | rc=2 (Line 10) |
| ZC `p = q(1.5)` | literal vs formal dec(9,2) | ZERO caller code for the arg; STATIC 5 B pool cell `50 01 00 00 00`; descriptor cell DATA-reloc → value cell; call `LXI H,*A(desc) / CALL` | rc=2 (Line 10) |
| ZD `r = g(1)` | INT literal, NG18 shape + skip tail | pool cell `00 01 00 00 00` (5 B), descriptor reloc → cell, ZERO arg code; return store `LXI H,*A(r) / MVI A,09 / ?DSTOP`; skip tail as the YD shape (QDCOP A `0C`, B `02`) | rc=2 (Line 9) |
| ZE `p = q(a, a*b, 2.5)` | mixed arity 3, formal dec(9,2) | arg1 descriptor → a's OWN cell; arg2 32 B product block with `MVI A,03 / ?QDDSR` + `MVI A,09 / ?DSTOP` into a **5 B** temp; arg3 literal pool cell `50 02 00 00 00` + descriptor, zero code; ONE interleaved 3-cell vector; callee block copy `MVI C,06` | rc=2 (Line 12) |
| ZF `call display(v1*inf,…,v5*inf)` | five products dec(10,2)*dec(4,3), five formals dec(10,2), VOID | five 32 B blocks EXACTLY the LOAN2 bytes; five 6 B temps stride 6; static 5-cell vector of inline DATA relocs; `LXI H,*A(vec) / CALL` (CHAIN-ADDR to entry); callee `MVI C,0A` block copy + five `LHLD/MVI A,0A/?DLDOP`; tail `put skip list(a)` width A `0D`/B `02` | rc=2 (Line 18) |

Sizes beyond the statement bytes are NOT pre-predicted (DATA/AUTO layout is adjudicated by
whole-file `cmp`, not arithmetic). Primary discriminators: shift direction+amount (H-1/H-4),
temp stride (H-2), DSTOP A (H-3), literal cell bytes/staticness (H-5), vector interleaving
(H-6), prologue shapes (H-7).

### 5. Campaign + arm contract (hops 2+)

ONE grouped run `PLI_SRC=probes timeout 900 python3 oracle/batch.py E52ZA E52ZB E52ZC E52ZD
E52ZE E52ZF --tag e52p13 --switches '$L$D'`, rc DIRECT; read EVERY `.PRN`; decode accepted
`.REL`s into `build/p3-13/`; goldens + batch `summary.txt` + transcripts committed VERBATIM
BEFORE any `ocaml/` byte; honest verdicts (DR-accepted / dr-refuses / my-gap), NEVER invent a
golden. ARM (after evidence): ONLY inside the `formal_is_dec` guard of `ocaml/lib/codegen.ml` —
- expression actuals (product shapes the panel pins) → lower via the existing product/dpush
  machinery, scale-align to the FORMAL scale with the [C370]-window shift, materialise into a
  FORMAL-width temp (`?DSTOP A=pf`), descriptor-vector cell → temp (STATIC inline DATA RELOC);
- DEC/INT literal actuals (panel-pinned encodings) → pre-scaled FORMAL-width pool cell +
  descriptor cell → value cell, ZERO caller runtime code;
- EVERYTHING outside the panel stays BY-NAME [TBD] (suffix/pointer actuals, unaccepted
  expression shapes, `FIXED BIN`-formal routes untouched); the N33 marker substring
  `FIXED DECIMAL formal is unproven` and the PU1 substring SURVIVE verbatim in the kept
  refusals; the [TBD] histogram stays codegen 68 / total 124.
- N33_DEC_FORMAL → NG18 retirement decision fires ONLY iff the ARMED binary reproduces
  `golden/negpanel1/NG18/NG18.REL` (256 B) whole-file `cmp` rc=0 from `probes/NG18.PLI`
  (CRLF+bare-`^Z` materialisation of the inline gate source); golden KEPT, NEVER re-derived;
  refusals 188→187 (NG20 precedent).
Validation: build rc=0 DIRECT; histogram 68/124 == baseline; whole-file `cmp` of every accepted
probe (POSITIONAL `pli80c` into FRESH paths); sweep `python3 build/e52p3/sweep.py E46N E46K E51
E52 P086 R10` FAILS 0 (159); markers harness (CRLF+bare `^Z`) incl. the N33 decision; DEC
regressions (R5xx–R8xx, LOAN1) 64/0; divergences 9/9 via `build/p3-12/divcheck.py` precedent;
FULL compile-tier gate rc=0 DIRECT → `build/gate-e52p13-reg.log`. Registration from **1288/188**
(accepted-and-byte-exact only, `--update-inventory`, `git diff --cached --stat`, config NEVER
staged, census OWN path); claim **C371** written from MEASURED BYTES ONLY and committed BEFORE
any `spec/COVERAGE.tsv` touch, INCLUDING the dated correction of BOTH C093 errors; row EXTENSION
of an existing DEC-formal contract preferred over a new row (if a NEW row ships, its
`spec/COVERAGE-IDS.txt` line lands in the SAME change; NEVER `coverage_gen.py`; 15 columns from
the FIRST NON-COMMENT row; `manual_ref` must match `pNN[:§X.Y][=phrase]` or start `NONE:`);
coverage_check + prose rc=0; gate AGAIN; RESULTS §P3-13 + §5 progress row + **CLOSED**; then the
next ACTUAL LOAN2 blocker under the marathon authorization (budget through P3-19).

### 6. LOAN2 direction (pre-registered, NEVER fit)

If the measured actual-materialisation rules land byte-exact, LOAN2 moves past Line 117/118.
The next refusal is NOT predicted — `display`'s body is a PUT EDIT (line ~146, candidate
cluster, reconnaissance only), and the line-115/116 EDIT already has its own armed route.
Record the ACTUAL verbatim diagnostic; if LOAN2 unexpectedly emits a complete `.REL`, go
STRAIGHT to whole-file parity against `golden/first/LOAN2/LOAN2.REL` (sha `712cfcb2…`, never
re-derived) and report the first genuine difference; never patch a byte without an
independently demonstrated law. LOAN2 stays UNMODIFIED (sha `7be23ba3…`).

### 7. Framing binding on C371 wording

C371 is BYTE-TIER ONLY — every statement derives from MEASURED BYTES (authentic goldens + this
campaign), never from runtime behaviour, PLILIB or numerical semantics claims. The literal
materialisation is described as a STATIC DATA allocation law (cell width = formal width,
pre-scaled packed image per [C084]), not as a conversion performed at run time. The
descriptor-vector is described as a compile-time data structure (inline DATA RELOCs), NOT as
anything written at runtime unless a probe measures that. C371 MUST carry the DATED correction
of BOTH C093 errors — (i) the DECPOLY `*A(005A)=5.67` citation is FALSE AS CITED (no 005A
exists; every DECPOLY actual is a variable; `5.67` is only the R2038 SOURCE DEC-store), and
(ii) the DEC-literal pool cell is FORMAL-WIDTH (5 B for dec(9,2)), pre-scaled `00 01 00 00 00`
per NG18 raw DATA records re-read this chain — NOT 2 bytes (C093's 2-byte cells were the
R2033 INT-literal BIN-formal route). The correction cites the re-verification evidence paths
and is traceable, NEVER silent.

## Subround P3-14 — CALL TARGETS SHADOWED BY A BUILTIN NAME: the CALL statement parses its target as a plain procedure designator, so `call <builtin-name>(...)` reaches the already-armed [C123]/[C124] call lowering (LOAN2:121 blocker) — PRE-REGISTERED 2026-11-07 (operator marathon brief; new chain 01a1b2d5; baseline HEAD `439add33`+guard `d26f0064`, ledger ENDS C371, inventory 1296/186, coverage 144/94) — **CLOSED 2026-11-07 (hop 5)**

### 1. Measured blocker (VERBATIM) + the WHY anatomy (ZERO oracle, hop 1)

`codegen: CALL target is not a simple procedure name [TBD] (only `CALL id` /
`CALL id(args)` / bare `id;` have a DR lowering sampled; line 121)` — re-measured THIS
hop on the armed binary `6db44394db5f09ad82cdb8e05f8fc92b298f77305301870de09e2485764bdfd2`
POSITIONAL FRESH (`build/p3-14-hop2/loan2.rel`): rc=2, NO `.REL`. The LOAN2 statement is
line 121 `call summary();` (the second site is line 135).

ROOT CAUSE (first-hand, accepted at hop 1): `parser.ml` `builtins` (~85-93) contains
`"SUMMARY"`; `primary` (~223) converts ANY builtin key immediately followed by `(` into
`Ebuilt(key, arglist)`; the `CALL` statement arm (~700) parses its target with `expr0`,
so `call summary();` arrives at codegen `Sprocedure_stmt` as `target.e =
Ebuilt("SUMMARY",[])`, and the classifier (~14695) accepts ONLY `Eident`/`Esuffix` heads
— everything else wraps into `Esuffix(Ebuilt …)` whose head match fails and raises the
BY-NAME refusal. The blocker is PURELY the capture: non-shadow `call foo();` arity-0
forward single AND two-site variants ALREADY compile rc=0 on the armed binary (variant
matrix t14e/t14f; [C123]/[C124] armed), and bare `call summary;` (no `(`) also rc=0
(t14b). ZERO-oracle sanity of the five NEW probes on the armed binary (`build/p3-14-hop2/sanity/`,
FRESH positional): E520A rc=0 (256 bytes, code=50 data=2); E520B rc=2 `(line 11)`;
E520C rc=2 `(line 12)`; E520D rc=2 `(line 11)`; E520E rc=2 `(line 12)` — all refusal texts
the VERBATIM guard above, NO `.REL`.

### 2. EXISTING DR evidence (ZERO oracle this subround; goldens untouched)

| Witness | Shape | DR bytes (first-hand) | Reading |
|---|---|---|---|
| authentic `golden/first/LOAN2/LOAN2.REL` summary chain (hop-1 chain walk, `build/e52p8/ondump2.full3` + own slot-walker `build/p3-14/`) | TWO `call summary();` sites (lines 121, 135), arity 0, name SHADOWS the builtin | head slot 066F (line-135, LAST site) with inline RELOC operand → slot 0621 (line-121, operand word = two zero DATA bytes); LINK-CHAIN-ADDRESS at 066F; the linker fills BOTH with code@0733 = summary entry | DR lowers a builtin-shadowed arity-0 CALL through the SAME [C123] site-to-site chain as any internal procedure. The object NEVER mentions the name `summary` (entry is anonymous). Zero-arg calls carry NO descriptor and NO `LXI H` — [C124] reconfirmed on the authentic object. |
| [C123] E27A (registered) | three forward CALL sites WITH args | chain record targets the LAST site's operand; each later operand is an inline `RELOC(CODE, <immediately preceding site's operand address>)` | the multi-site law E520C tests on the shadowed spelling. |
| [C124] E24J/E24A (registered) | zero-argument calls | bare 3-byte `CALL <entry>`; no descriptor, no storage between sites | the E520A/B shape; empty-parens arity-0 multi-site on a SHADOWED name is NEW probe territory (E27A had args; LOAN2 authentic is corpus-tier, not panel-tier). |
| authentic LOAN2.REL `line()` chain (hop 1) | arity-0 NON-shadow, SEVEN sites | head 0945 ← 08E6 ← 0863 ← 0825 ← 0807 ← 078B ← 0662 → code@0948 | the 7-site chain already reproduces byte-exact in my object ([C123] armed at scale); E520C is the 2-site shadow panel twin. |
| [C093]/[C094] family + my control t14h (this binary, `build/p3-14/t14h.REL`) | `call summary2(i);` non-shadow, equal-(p,s) DEC var actual | main `LXI H,*A(desc 0002) / CALL slot@000A head`; desc cell = inline DATA RELOC → i's own cell 0000; callee entry peeled `5E 23 56 EB / SHLD ptr(0004)`, formal store `LHLD 0004 / MVI M,02 / INX H / MVI M,00 / RET`; tail `CALL ?STOPX` | the E520D prediction (with-args shadow rides the EXISTING variable-actual route once the target parses as `Eident`). |
| my controls on the armed binary (`build/p3-14/`) | t14e single site; t14f two sites (non-shadow) | t14e code 28 B: `LXI B,0200 / CD r(?START) / CD head-slot@0007 / … / JMP / body / CD r(?STOPX)`; t14f code 31 B: second `CD` operand = `07 00` inline RELOC → code@0007, LINK-CHAIN-ADDRESS addr:[000A] (LAST site) | exactly the [C123] two-site geometry; E520C predicts DR identical bytes for the shadowed spelling. |

### 3. Hypotheses (byte-exact; NEVER fit; every MISS recorded VERBATIM)

- **H-1 (shadow-name CALL law)**: DR lowers `call <builtin-shadow>();` exactly as the
  non-shadow arity-0 call: bare `CALL <slot>` (3 B), NO descriptor, NO `LXI H` [C124];
  internal-proc entries are anonymous so the shadow has no object-level trace. FALSIFIED
  if DR refuses E520B (honest `dr-refuses`, NO invented golden) or emits any different
  shape at the call.
- **H-2 (byte-identity with the control)**: `E520B.REL` differs from `E520A.REL` in
  EXACTLY the program-name record bytes (the single character `A`→`B` in the PROG-NAME /
  EXTNAME records; internal procedure names NEVER appear in the object). FALSIFIED by ANY
  additional differing byte (e.g. the shadowed name leaking into an external definition).
- **H-3 (multi-site chain on the shadow)**: E520C reproduces the [C123] site-to-site
  geometry — chain record on the LAST site, later operand an inline RELOC against the
  immediately preceding operand word, first operand two literal zero DATA bytes —
  mirroring the authentic LOAN2 head 066F→0621 both→0733. FALSIFIED by per-site chain
  records, by linking to the FIRST site's operand from a THIRD site style error, or by
  any address difference.
- **H-4 (with-args shadow)**: E520D `call summary(i);` lowers as the existing
  equal-(p,s) DEC variable-actual route: static descriptor cell → the actual's OWN cell,
  `LXI H,*A(desc) / CALL <chain head>`; callee arity-1 peeled copy then the formal's
  deref store [C093]/[C094]. NO builtin dispatch. FALSIFIED by refusal, by a runtime-written
  descriptor, or by a different prologue.
- **H-5 (bare-statement boundary, UNMEASURED)**: E520E bare `summary();` (NO `CALL`
  keyword) — DR acceptance is UNMEASURED. If DR refuses → honest `dr-refuses`, the parser
  bare-statement arm KEEPS its `Ebuilt` capture and the BY-NAME [TBD] refusal stays. If DR
  accepts → the bytes adjudicate against the CALL form and only THEN is extending the arm
  to the bare-statement route a measured option. NEVER arm before evidence.

### 4. Probes E520A..E520E (`probes/E520{A..E}.PLI`, CRLF + bare `^Z`, ≤71 cols, ONE dcl
per line, uppercase label first line, continuation `put skip list(i);` after every call) —
pre-registered predictions (NEVER fit):

| Probe | Shape | Predicted DR bytes at the call site | My side TODAY (sanity, this binary) |
|---|---|---|---|
| E520A control | non-shadow `call foo();` arity-0 forward, ONE site | bare `CD <slot>` at the call (no descriptor, no LXI H); the single operand word is two zero DATA bytes carrying the LINK-CHAIN-ADDRESS (single site = degenerate [C123]); callee entry after the JMP, bare body + RET [C125]; tail `CD ?STOPX`. Control twin t14e geometry + the proven `put skip list` tail. | rc=0 — 256 B, code 0x32: `…CD head@0007… / 11 52 02 / 01 25 00 / CD ?SYSPR / 3E 01 / CD ?SKPOP / 2A r(i) / 3E 09 / CD ?QICOP / CD ?PNVOP / CD ?QIOOP / C3 tail / foo@0028: 21 01 00 / 22 r(i) / C9 / CD ?STOPX` |
| E520B shadow | `call summary();` arity-0, ONE site (LOAN2:121 shape) | IDENTICAL statement bytes to E520A (H-1); whole-file difference vs E520A = the one program-name character ONLY (H-2) | rc=2 at the guard `(line 11)`, NO .REL |
| E520C shadow 2 sites | two `call summary();` in main (mirrors LOAN2 121/135) | site 1 `CD` operand = zero word; site 2 `CD` operand = inline RELOC → site 1's operand address; LINK-CHAIN-ADDRESS on the LAST site operand; linker fills both with the entry LC (authentic LOAN2 twin law) | rc=2 `(line 12)` (FIRST refusal aborts), NO .REL |
| E520D shadow w/ actual | `call summary(i);` arity-1, equal-(p,s) DEC var | `LXI H,*A(desc)` (inline RELOC → static descriptor cell) `CD <chain head>`; desc cell = inline DATA RELOC → i's own cell; callee peeled arity-1 prologue + deref formal store + RET (t14h control bytes) | rc=2 `(line 11)`, NO .REL |
| E520E boundary | bare `summary();` NO CALL keyword | UNKNOWN by design (H-5): accept ⇒ bytes vs the CALL form; refuse ⇒ VERBATIM diagnostic, no .REL, KEPT | rc=2 `(line 12)`, NO .REL |

Whole-file sizes are adjudicated by `cmp`, never by arithmetic (P3-13 lesson kept: sizes
beyond the statement bytes are NOT pre-predicted). Primary discriminators: statement-byte
identity A vs B (H-1/H-2), chain-record placement and operand values in C (H-3), descriptor
staticness in D (H-4), the bare-form verdict itself in E (H-5).

### 5. Campaign + arm contract

ONE grouped run `cd /home/john/projects/sushiworks/pli80 && PLI_SRC=probes timeout 900
python3 oracle/batch.py E520A E520B E520C E520D E520E --tag e52p14 --switches '$L$D'`,
rc DIRECT (NEVER pipeline-tail); read EVERY `.PRN`; decode accepted `.REL`s into
`build/p3-14-hop2/`; goldens + batch `summary.txt` + transcripts committed VERBATIM
BEFORE any `ocaml/` byte; honest verdicts (DR-accepted / dr-refuses / my-gap), NEVER
invent a golden.

ARM (after evidence, ONLY if H-1/H-3/H-4 land accepted+byte-exact): the SMALLEST measured
rule is the parser `CALL` arm (parser.ml ~700) — parse the target as a PLAIN identifier
+ `suffix_chain`, NEVER consulting `builtins`, then keep `Sprocedure_stmt { target; args =
[] }` so the already-armed `Esuffix`-head classifier consumes it unchanged; expression
position (`primary`) keeps its builtin capture UNTOUCHED. WHY the parser and NOT a widened
codegen classifier: the classifier cannot distinguish the CALL statement from a bare
statement (both arrive as `Sprocedure_stmt` with `args = []`), so accepting `Ebuilt` heads
there would silently arm the UNMEASURED H-5 route; the parser-side fix keeps the bare
`summary();` refusal honest BY NAME. The guard message stays REACHABLE (bare-statement
route, non-name targets) and its text survives VERBATIM; first-hand check this hop: the
only occurrences of `CALL target is not a simple procedure name` outside `ocaml/` are the
census LOAN2 rows (which MOVE VERBATIM at registration, nothing fixed) — no negative-panel
or marker row depends on it. `NULL`/prefix expression routes are NOT touched.

Validation (hop 3+): build rc=0 DIRECT; warning histogram codegen 68 / total 124 ==
baseline (fresh `--build-dir`); whole-file `cmp` of EVERY accepted probe on FRESH
POSITIONAL paths; sweep `python3 build/e52p3/sweep.py E46N E46K E51 E52 P086 R10` —
COUNT MOVES WITH INVENTORY rows, FAILS 0 binding; markers harness (CRLF + bare `^Z`)
including every CALL/PUT marker substring; DEC regressions 64/0; divcheck 9/9; **FULL
GATE BEFORE CLOSE** — hop-11/12 lesson binding: ONLY the gate runs the negative panel; a
possible retirement fires ONLY iff the armed binary `cmp` rc=0 vs the KEPT golden (NEVER
re-derived). LOAN2 UNMODIFIED POSITIONAL FRESH → record the ACTUAL next blocker VERBATIM
(§6). Registration from **1296/186** (accepted-and-byte-exact only, `--update-inventory`,
`git diff --cached --stat`, config NEVER staged); census OWN path (counts expect 15/0/26/0,
LOAN2 msg MOVES VERBATIM, NOTHING fixed); claim **C372 written from MEASURED BYTES ONLY
BEFORE any `spec/COVERAGE.tsv` touch**; coverage prefers EXTENDING an existing row — the
CALL-statement family row `PROC.CALL_COPYIN` already states the CALL lowering law
(SUPPORTED EXACT:40); if the evidence instead justifies a NEW row its
`spec/COVERAGE-IDS.txt` line lands in the SAME change (NEVER `coverage_gen.py`; 15 columns
from the FIRST NON-COMMENT row; `manual_ref` must match `pNN[:§X.Y][=phrase]` or start
`NONE:`); `coverage_check` + prose rc=0; FULL gate rc=0 DIRECT →
`build/gate-e52p14-reg.log`; RESULTS §P3-14 + PLAN §5 progress row (insert INSIDE the
table after the P3-13 row — anchor by LINE NUMBER after editing, hop-12 lesson) + §P3-14
**CLOSED**.

### 6. LOAN2 direction (pre-registered, NEVER fit)

If the fix lands byte-exact, LOAN2 moves PAST line 121. The next refusal is NOT predicted
— per the hop-1 reconnaissance the remaining CALL sites are line 132 `call line();`
(non-shadow arity-0, 7-site chain family — likely already armed), line 135 `call summary();`
(second shadow site — this slice's own route) and line 160 `call current_year(IP - YIN);`
(a DEC **SUB**-expression actual vs `dec(10,2)` formals — P3-13 armed ONLY `Mul`-of-two-
plain-autos and literals, so the strongest `my-gap` candidate; STRONGEST ≠ PREDICTED).
Record the ACTUAL verbatim diagnostic; if LOAN2 unexpectedly emits a complete `.REL`, go
STRAIGHT to whole-file parity against `golden/first/LOAN2/LOAN2.REL` (sha `712cfcb2…`,
NEVER re-derived) and report the first genuine difference. LOAN2 stays UNMODIFIED (sha
`7be23ba3…`).

### 7. Framing binding on C372 wording

C372 is BYTE-TIER ONLY — every statement derives from MEASURED BYTES (authentic goldens +
this campaign), never from runtime behaviour, PLILIB or evaluation-order claims. The claim
wording must describe what the OBJECT shows (chain topology, absence of descriptor bytes,
anonymity of internal entries), NOT what a linker or runtime "does" beyond filling recorded
addresses (the chain-fill statement is the [C123] recorded law reconfirmed, panel-verified
via E520C only if it lands). The bare-statement boundary (H-5) must be stated as a kept
BY-NAME [TBD] refusal unless E520E measures DR acceptance. If E520B/C/D are DR-REFUSED,
C372 does not exist for this subround — the honest verdict is a `dr-refuses` record with
the VERBATIM diagnostic and NO arm.

### 4b. DATED ADDENDUM (2026-11-07, hop 1): campaign e52p14 MEASURED verdicts + probe defect

Campaign 1 (`golden/e52p14/`, committed VERBATIM `1afc3bd3`, rc=0, 1 ok/5):
**E520D ACCEPTED** both passes NO ERROR(S), `.REL` decoded first-hand — **H-4 CONFIRMED**:
main `21 02 00 / CD head@000A` (LXI H,*A(desc), operand inline CODE?? no — RELOC→DATA 0002;
LINK-CHAIN-ADDRESS addr:[000A]); descriptor cell 0002 = two zero bytes with **inline DATA
RELOC → 0000** (i's OWN cell — STATIC, exactly the armed t14h topology); callee entry 002B
peeled `5E 23 56 EB / SHLD 0004`; body `2A 04 00 / 36 02 / 23 / 36 00 / C9`; tail
`C3 3B / CD ?STOPX`. The SHADOWED builtin name with a variable actual rides the EXISTING
[C093]/[C123] route once the target parses as a name.

**E520A/B/C/E diag, NO .REL — PROBE DEFECT (MINE, not a DR verdict on H-1/H-2/H-3/H-5):**
the SYNTAX pointer fires on the EMPTY-PARENS HEADER `procedure();` (error lines 13/14/17/15
— the headers), while the CALL-SITE lines carry NO error; DR PL/I-80 spells zero-formal
headers `procedure;` (LOAN2 lines 158/188/209 first-hand). E520E's line-12 SYNTAX (bare
`summary();`, BOTH passes) is REAL but CONFOUNDED by the broken header — H5 stays
UNMEASURED pending the corrected twin. NEW PROBE LAW (accepted): DR headers are
`procedure;` / `procedure(x);` — NEVER `procedure();`; zero-oracle sanity CANNOT catch
DR-only syntax (my parser accepts both). Corrected probes (identical statements, header
fixed) re-measure under tag **e52p14b**; `golden/e52p14/` KEPT UNTOUCHED as the campaign-1
record (precedent e52p3d, e42p0b/c).

## Subround P3-15 — FILE-EDIT ITEM ON A DEREFERENCED DEC FORMAL: the guard clause that refuses the one item class the authentic LOAN2 display body proves — PRE-REGISTERED 2026-11-07 (operator marathon brief; chain 01a1b2d5 renewal 6/12; baseline HEAD `96f7a85d`+guard `936eeb61`, ledger ENDS C372, inventory 1300/187, coverage 145/95, armed binary `b88e7b023027e2eeba1b6f49dc0815cb25e14f20269074a637a7c1f84f3c72e2`) — **CLOSED 2026-11-07 (hop 7)**

### 1. Measured blocker (VERBATIM) + pre-audit (hops 1–2, ZERO oracle)

Re-measured THIS hop on the armed binary, POSITIONAL FRESH (`build/p3-15/recheck/`):
rc=2, NO `.REL`:

`codegen: PUT FILE(OUTPUT) EDIT of the FORMAL A has no byte-exact DR witness [TBD] (line 147) -- the file EDIT route is lowered for the item classes its objects pin: the DEC variable of golden/probe55/P086K and the string literal of LOAN2's own golden (115: MVI A,01/?SLCTS/?EDTOV at 053F-0542; 199: six literal chains against one format record).  A list is refused as a WHOLE, item by item, before the attach is emitted.  a procedure formal is read through its pointer cell on the console route, and no object puts a formal between a file EDIT attach and ?EDTOV`

The LOAN2 statement (lines 147–150, source sha `7be23ba3…`, UNMODIFIED):
`put file (output) edit ('|',a,'|',b,'|',c,'|',d,'|',e,'|') (a,2(2(p'$zz,zzz,zz9v.99',a),p'$zzz,zz9.v99',a));` inside `display: procedure(a,b,c,d,e);` with `(a,b,c,d,e) fixed decimal(10,2)`.

HOP-1 PRE-AUDIT (first-hand): the authentic `golden/first/LOAN2/LOAN2.REL` display body
`0674–0732` ALREADY pins the refused shape (see §2). HOP-2 DECODE (first-hand,
`build/p3-15/fmt.py` + `fmt-out.txt` + `tables.py`): the T3 format record at
`data@0015..0046` (50 B) is FULLY decoded with ZERO unknown bytes and fits the existing
laws [C090]/[C361]/[C362] VERBATIM — see §2 row 3. The refusal's reason clause ("no
object puts a formal between a file EDIT attach and ?EDTOV") is FALSE-AS-WRITTEN against
the authentic corpus — it is MY completeness guard, not a DR fact; a DATED correction is
owed at C373 wording (the code text stays VERBATIM this hop; only the ledger prose is
corrected).

### 2. EXISTING DR evidence (ZERO oracle this subround so far; goldens untouched)

| Witness | Shape | DR bytes (first-hand) | Reading |
|---|---|---|---|
| authentic LOAN2.REL display body `0674–0732` | `put file(output) edit` of FIVE `dec(10,2)` FORMALS + six pipe literals, nested rep format | attach `21 +RELOC common0 / 11 52 06 / 01 +RELOC to code@0732 / CD ?SIOOP / 21 15 00 RELOC to data@0015 / CD ?EDITF`; then SIX literal chains `21 EC 01 / 3E 01 / CD ?SLCTS / CD ?EDTOV` alternating with FIVE formal chains `2A 42 03+2i / 3E 0A / CD ?DLDOP / 3E 0D / 06 02 / CD ?QDCOP / CD ?EDTOV` between `?EDITF` and the terminal `CD ?QIOOP@0730` | DR DOES put a DEC formal between a file EDIT attach and ?EDTOV; the formal chain is the armed P3-13 deref `LHLD / MVI A,p / ?DLDOP` prep plus the SAME `p+3 / s / ?QDCOP / ?EDTOV` tail the variable route uses. |
| authentic LOAN2.REL format tables (hop-2 `build/p3-15/fmt-out.txt`) | prescan DATA region `0000..0073` | T1 `80 00 0C FF 03 FF 81` (line-115 family); T2 `80 00 03 FF 02 04 00 05 39 39 2F 39 39 81` = `(a,p'99/99')`; **T3 `data@0015..0046` (50 B) = `80 00 03 FF 80 02 80 02 02 0A 02 0F 24 5A 5A 2C 5A 5A 5A 2C 5A 5A 39 56 2E 39 39 03 FF 81 02 08 02 0C 24 5A 5A 5A 2C 5A 5A 39 2E 56 39 39 03 FF 81 81 81`** = the line-147 format list; literal cell `data@01EC = 7C` SINGLE, shared by all six chains; descriptor cells `data@0342..034B` have NO static bytes (runtime block-copy) | every byte fits [C090]/[C361]/[C362]: `a` record = `03 FF`; picture record `02 b1 b2 len` + text, b1 = count{9,Z,$} − 1 iff leading `$`, b2 = count{9,Z} after the LAST `V` (`9V.99` → 02; `9.V99` → 02, the dot BEFORE the V does NOT count); rep group = `80 n … 81`; table closes `81`. NO unknown byte. |
| `golden/probe55/P086K/P086K.REL` | DEC VARIABLE item on the file EDIT route (armed, registered) | chain heads `?SIOOP@0020 / ?EDITF@0026 / ?DLDOP@002E / ?QDCOP@0035 / ?EDTOV@0038 / ?QIOOP@003B`; table `80 00 00 05 01 81 80 00 00 05 01 81`; data `50 01 00` then runtime cells | the variable prep is `LXI H,*A(cell)`; the guard text cites P086K 0028-0039 as the `MVI A,p / ?DLDOP / MVI A,p+3 / MVI B,s / ?QDCOP / ?EDTOV` law. The ONLY difference vs the formal route is the PREP instruction. |
| `golden/e52p13/E52ZF` 00ED–00F2 + NG39 | deref DEC formal read (console skip-list route, armed at P3-13 [C371]) | `LHLD desc / MVI A,0A / ?DLDOP` then the same width/scale tail | the ITEM LOWERING at `ocaml/lib/codegen.ml` ~13020 ALREADY emits exactly the display-body chain for `Vdec` + `st.deref` members; ONLY `authorize_file_edit_item` (codegen.ml ~12533) refuses. |
| `golden/e52p3d/E52PP` | rep-group + `a` record + pipe literal on the FILE route | data@0000 `80 00 80 02 03 FF 81 81 7C`; heads `?SIOOP@0010 / ?EDITF@0016 / ?SLCTS@001E / ?EDTOV@0021 / ?QIOOP@0024` | `a` is the A edit-mode format element (record `03 FF`, NO declaration needed); the `'|'` literal rides `LXI H,*A(lit) / MVI A,01 / ?SLCTS / ?EDTOV`. |
| E52XA/XG goldens (`golden/e52p11/`) | attach behind `open file(pf) print;` in MAIN | `21 +RELOC common0 / 11 52 06 / 01 +RELOC cont / CD ?SIOOP …` | GOLDEN-PROVEN probe-open geometry; probes MUST `dcl pf file;` (hop-2 accepted: an internal ENTRY name would resolve the common reference differently). |

### 3. Hypotheses (byte-exact; NEVER fit; every MISS recorded VERBATIM)

- **H-A (formal-item law)**: on the file EDIT route a deref'd scalar `fixed dec(p,s)`
  formal emits EXACTLY `LHLD <desc cell> / MVI A,p / CALL ?DLDOP / MVI A,p+3 / MVI B,s /
  CALL ?QDCOP / CALL ?EDTOV` — the prep is the ONLY difference from the armed variable
  route (P086K); the descriptor cells are the callee's runtime block-copy targets (NO
  static bytes). FALSIFIED by any DR refusal of E521B/C or any byte difference in the
  chain.
- **H-B (literal chains ride unchanged)**: `'|'` items keep the armed PIlit chain
  `LXI H,*A(lit cell) / MVI A,01 / ?SLCTS / ?EDTOV`, ONE shared literal cell per distinct
  literal ([C090] reconfirmed on the authentic display body: six chains, one cell).
  FALSIFIED by any chain or cell-count difference.
- **H-C (decoded picture record)**: the probes' format tables equal the DECODED bytes —
  A/B: `80 00 03 FF 02 08 02 0C 24 5A 5A 5A 2C 5A 5A 39 2E 56 39 39 81` (21 B; b1 = 08 =
  $1+Z5+9 3 − 1, b2 = 02 from the `99` after the V, len = 0C); C: the T3 50-byte record
  VERBATIM (§2 row 2); D: `80 00 03 FF 81` (6 B). FALSIFIED by ANY format-table byte
  difference — the decode came from the golden bytes and the pre-existing laws, NEVER
  from a fit.
- **H-D (nested rep groups)**: `2(2(pic,a),pic,a)`-style nesting rides the armed P3-4
  REPSPEC/[C362] law (`80 n … 81` per level, inner before outer `81`). FALSIFIED by any
  record-byte difference in E521C's table vs the T3 clone.
- **H-E (boundary)**: a deref'd FIXED BIN formal as a file EDIT item (E521D) is
  UNMEASURED by this panel's arm; MY side KEEPS the BY-NAME refusal whatever DR does (the
  arm is scoped to `Vdec` ONLY). DR's verdict is recorded honestly either way.

### 4. Probes E521A..E521D (`probes/E521{A..D}.PLI`; CRLF + bare `^Z` + ≤71 cols + ONE dcl per line + first-line label + `procedure(x,y);` headers per the hop-1 probe law + a continuation statement after EVERY put) — predictions from the DECODED laws (NEVER fit):

| Probe | Shape | Predicted DR bytes at the statement (law-derived) | My side TODAY (sanity, `b88e7b02…`) |
|---|---|---|---|
| E521A CONTROL (non-formal DEC item) | main `dcl pf file; open file(pf) print; call show(v,w);` two `dec(10,2)` autos as actuals; callee `show: procedure(x,y);` LOCAL `dcl z fixed dec(10,2);` body `put file(pf) edit('\|',z,'\|')(a,p'$zzz,zz9.v99');` | table 21 B as in H-C; attach `21 r(common0) / 11 52 06 / 01 r(cont) / CD ?SIOOP / 21 r(table) / CD ?EDITF`; chains literal `21 r(lit) / 3E 01 / CD ?SLCTS / CD ?EDTOV`, z `21 r(z-cell) / 3E 0A / CD ?DLDOP / 3E 0D / 06 02 / CD ?QDCOP / CD ?EDTOV`, literal again, `CD ?QIOOP`; call + callee block-copy prologue ride [C371]/[C094] arity-2 variable-actual geometry | expect rc=0 (all classes armed today) |
| E521B FORMAL (the target class) | same main/callee spine; body item is the FORMAL `x`: `put file(pf) edit('\|',x)(a,p'$zzz,zz9.v99');` | IDENTICAL to A EXCEPT the formal prep: `2A r(desc cell) / 3E 0A / CD ?DLDOP` + the same tail (H-A); desc cells have NO static bytes | rc=2 at the guard, `the FORMAL X`, NO `.REL` |
| E521C FULL MIRROR | arity-5 callee `procedure(a,b,c,d,e)`, five `dec(10,2)` formals; body = the LOAN2 147–150 statement VERBATIM on `pf`: 11 items `'\|',a,'\|',b,'\|',c,'\|',d,'\|',e,'\|'`, format `(a,2(2(p'$zz,zzz,zz9v.99',a),p'$zzz,zz9.v99',a))` | T3 clone VERBATIM (H-C/H-D); 6 literal chains + 5 formal chains alternating exactly as the authentic body; single shared `7C` cell; `?QIOOP` terminator | rc=2 at `the FORMAL A`, NO `.REL` |
| E521D BOUNDARY | same spine; callee `procedure(n,m)` `fixed bin` formals; body `put file(pf) edit(n)(a);` | table `80 00 03 FF 81`; fixed-bin FORMAL item class UNMEASURED — verdict recorded honestly | rc=2 at the guard (`the FORMAL N`), refusal KEPT regardless of DR |

Whole-file sizes are adjudicated by `cmp`, never by arithmetic (P3-13/14 lesson kept).
NOTE (design correction, recorded not silent): hop 2 pinned A's literal prediction as
"(20 B)"; the decode law gives the byte sequence above which is 21 bytes — the SEQUENCE
is what is predicted (b1/b2/len law), the count in the hop-2 note was my own arithmetic
slip; `cmp` adjudicates. A's data list keeps the pinned THREE items against TWO format
elements — the authentic display body itself carries 11 items against a 13-element format
list and DR compiled it, so item/format count is NOT a compile-time gate; the count
asymmetry A-vs-B is intentional per the pinned design and the DR verdict is recorded.

### 5. Campaign + arm contract

ONE grouped run `cd /home/john/projects/sushiworks/pli80 && PLI_SRC=probes timeout 900
python3 oracle/batch.py E521A E521B E521C E521D --tag e52p15 --switches '$L$D'`, rc
DIRECT (NEVER pipeline-tail); read EVERY `.PRN`; decode accepted `.REL`s into
`build/p3-15/`; goldens + batch `summary.txt` + transcripts committed VERBATIM BEFORE any
`ocaml/` byte; honest verdicts (DR-accepted / dr-refuses / my-gap), NEVER invent a golden.

ARM (after evidence, ONLY for classes MEASURED accepted+byte-exact): ONE guard clause in
`authorize_file_edit_item` (`ocaml/lib/codegen.ml` ~12533) — in the `PIvar` branch admit a
`st.deref` member iff its `vk_of` is `Vdec _`; EVERYTHING else keeps the VERBATIM
BY-NAME refusal (message text untouched, so the PU1-class marker substrings and the
line-N clause survive). No emitter bytes change (lowering is armed since P3-13). Build
rc=0; histogram codegen 68 / total 124 == baseline (fresh `--build-dir`); whole-file `cmp`
of every accepted probe FRESH POSITIONAL; sweep — COUNT MOVES WITH INVENTORY, FAILS 0
binding; markers (CRLF + bare `^Z`); DEC regressions 64/0; divcheck 9/9; **FULL GATE
BEFORE CLOSE** (only the gate runs the negative panel) → `build/gate-e52p15-reg.log`.
Registration from **1300/187** (accepted-and-byte-exact ONLY, `--update-inventory`, `git
diff --cached --stat`, config NEVER staged); census OWN path (counts 15/0/26/0, LOAN2 msg
MOVES VERBATIM, NOTHING fixed); **C373 written from MEASURED BYTES ONLY BEFORE ANY
`spec/COVERAGE.tsv` touch**, including the DATED correction of the guard-reason clause
(False-as-written vs the authentic corpus — recorded in the ledger, code text kept);
coverage: adjudicate FIRST-HAND against the actual `FILE.PUT_EDIT_*`/`FILE.PUT_*` row
family — EXTEND where the row law fits, else justified NEW row with SAME-change
`spec/COVERAGE-IDS.txt` line (NEVER `coverage_gen.py`; 15 columns from the FIRST
NON-COMMENT row; `manual_ref` `pNN[:§X.Y][=phrase]` or starting `NONE:`); `coverage_check`
+ prose rc=0; FULL gate rc=0 DIRECT; RESULTS §P3-15 + PLAN §5 progress row INSIDE the
table **anchored by LINE NUMBER with the 7-unescaped-pipes check** + §P3-15 **CLOSED**.

### 6. LOAN2 direction (pre-registered, NEVER fit)

If the arm lands byte-exact, LOAN2 moves PAST line 147. The next refusal is NOT predicted
— the hop-2 orientation decode touched T4 (`0047..0073`, the line-199/212-family tables)
for orientation ONLY. Record the ACTUAL verbatim diagnostic; if LOAN2 unexpectedly emits
a complete `.REL`, go STRAIGHT to whole-file parity against `golden/first/LOAN2/LOAN2.REL`
(sha `712cfcb2…`, NEVER re-derived) and report the first genuine difference. LOAN2 stays
UNMODIFIED (sha `7be23ba3…`).

### 7. Framing binding on C373 wording

C373 is BYTE-TIER ONLY — every statement derives from MEASURED BYTES (authentic goldens +
this campaign), never from runtime behaviour or PLILIB. The claim may say the OBJECT
shows the `LHLD`-prep chain between attach and ?EDTOV for a DEC formal; it may NOT claim
what ?EDITF/?EDTOV DO at runtime beyond recorded bytes. The guard-reason clause
correction is DATED and worded as a correction of MY completeness-guard prose (a compiler
internal), not of any DR claim. The FIXED-BIN formal boundary (H-E) stays an open
`my-gap`/unmeasured route unless E521D measures otherwise; floats, based and pointer
formals keep refusing BY NAME.

## Subround P3-16 — DEC SUB/ADD EXPRESSION ACTUALS AGAINST A FIXED DECIMAL FORMAL: is the LOAN2:160 22 B no-window block the L1+L5 composition, or an exception? — PRE-REGISTERED 2026-11-07 (operator marathon brief; chain 01a1b2d5 renewal 10/12; baseline HEAD `a4b5536c` (durables `590e72e8` + guard `a4b5536c`), ledger ENDS C373, inventory 1303/188, coverage 145/95, armed binary `02ea809e8fbc908a722e1e1b979e238b7353fa16eafe7b31df1bce8da0c826fb`) — **CLOSED (hop 6, 2026-11-07)**

### 1. Measured blocker (VERBATIM) + pre-audit (hops 1–2, ZERO oracle)

HOP-2 RE-MEASURED this hop on the armed binary `02ea809e…`, POSITIONAL FRESH
(`build/p3-16/recheck/`), LOAN2 sha `7be23ba3…` UNMODIFIED — rc=2, NO `.REL`:

`codegen: non-variable argument against a FIXED DECIMAL formal is unproven [TBD] (DR passes an automatic decimal BY REFERENCE -- the descriptor holds LXI H,*A(cell); a literal or expression decimal argument has no sample [DECPOLY, R2037/R2038/R725]. Line 160)`

The statement (source read FIRST-HAND hop 1): LOAN2:160 `call current_year(IP-YIN);`
inside `summary: procedure;` (157–162), `IP`/`YIN` both `fixed decimal(10,2)` (lines
29–30), callee `current_year: procedure(I); dcl … I fixed decimal(10,2);` (168–172) — a
DEC **Sub** of two equal-scale plain autos against one SCALAR `RTdec(10,2)` formal. The
guard (codegen.ml ~4839–4860) admits ONLY `Eident` variables, `Enumber` literals and
`Ast.Ebinary (Ast.Mul, plain-dec-auto, plain-dec-auto)` [C371]; Add/Sub fall to the
BY-NAME refusal. `dpush` ALREADY implements the armed Add/Sub chain (`?DADOP`/`?DSUOP`,
codegen.ml ~6582–6599, laws [C086] L1/R705/R707/R715 + L5 consumer fix); the refusal is
the ONLY blocker. BIND AUDIT (contract-mandated, first-hand this hop): `bind.ml` `dec_ok`
(~2297–2321) is EXPRESSION-SHAPE-AGNOSTIC — it keys on callee class + scalar `RTdec`
formal only, and the `temps` sizing (~2340–2362) already allocates the formal-width temp
for ANY non-simple actual when `dec_ok`; **no bind change is needed or permitted.**

### 2. EXISTING DR evidence (ZERO oracle this subround so far; goldens untouched)

All re-verified FIRST-HAND this hop from the KEPT authentic golden (raw hex in
`build/p3-16/loan2-summary-body.txt`), never re-derived:

1. **THE witness — LOAN2.REL summary body `0733–0769`.** `21 BD 02 / 36 80`
   (`end = true`); the **22 B Sub-actual block** `0738–0752` raw
   `21 FA 02 3E 0A CD.. 21 F4 02 3E 0A CD.. CD.. 21 4E 03 3E 0A CD..` =
   `LXI H,*A(02FA) / MVI A,0A / ?DLDOP / LXI H,*A(02F4) / MVI A,0A / ?DLDOP / ?DSUOP /
   LXI H,*A(temp 034E) / MVI A,0A / ?DSTOP` — **NO shift of ANY kind** (operand scales
   equal AND result scale = formal scale); left operand pushed FIRST; `?DSTOP A = 0A` =
   FORMAL precision; then arity-1 actual setup `LXI H,*A(data@034C) / CD (chain slot
   0757 → LC code@076A)`; DATA static `data@034C = 4E 03` with `RELOC data@034C →
   data@034E` — the [C371] static descriptor-vector cell pointing at the 6 B expression
   temp; callee entry `076A` peeled arity-1 prologue `5E 23 56 EB / SHLD 0354`; `YIN = IP`
   (`0759–0766`), `RET` `0769`.
2. **Equal-scale direct/computed Add/Sub witnesses in the SAME golden** — `0412–0422` and
   `043D–044D` (`DLDOP 0A / DADOP / DLDOP 0A / DSTOP 0A`), `047E–048E` and `0491–04B4`
   (two-op `DLDOP/DLDOP/DSUOP` then `DLDOP/DLDOP/DADOP/DSTOP`, precision bytes 0A
   throughout, NO shifts). Equal scales, so NONE of these discriminates the differing-
   scale behaviour.
3. **[C370] (Add/Sub DIRECT STORE between scales)** pins the window ONLY between source
   `?DLDOP` and the destination store for `x = y` assignments — NOT between an `?DSUOP`/
   `?DADOP` and a CALL-actual temp store.
4. **[C371]** pins the WINDOW (MVI A,d / ?QDDSL|?QDDSR) between `?DMUOP` and the temp
   DSTOP ONLY for the **Mul** actual (ZA down d=03, ZB UP d=02) — Mul is exactly the
   operator L1 EXEMPTS (L2: no operand alignment). Whether the window generalises to
   Add/Sub actuals, and whether L1 operand alignment fires in the ACTUAL context, is
   UNMEASURED. The generalisation is MY compiler's standing assumption (armed `dpush`
   path); it is the primary hypothesis to falsify, never to fit.
5. **[C086] expression-context laws L1/L5/L6/L7** (ledger): `+/-` align the SHORTER
   operand UP to max(s) BETWEEN the pushes; equal scales emit nothing; both directions
   proven for SUBTRACT (R705/R707/R715); the CONSUMER fixes the scale; push order right-
   first iff right compound and left simple. Pinned in expression/store contexts — the
   DEC-ACTUAL context is new ground (only Mul has been sampled there).

### 3. Hypotheses (byte-exact; NEVER fit; every MISS recorded VERBATIM)

- **H-A (control, LOAN2 arithmetic replicated):** Sub of two equal-scale plain DEC autos
  against a formal of the SAME scale emits the 22 B block VERBATIM: `push(l,pl) push(r,pr)
  ?DSUOP push-temp(pf)`, NO shift anywhere, `?DSTOP A = pf`, static vector cell → formal-
  width temp. FALSIFIER: ANY shift byte, a different op order, or a window with d = 0.
- **H-A2:** `?DSTOP A` carries the FORMAL precision even when operand precisions differ
  from it (the [C371] H-4 law re-tested on Sub). FALSIFIER: `MVI A` before `?DSTOP` is not
  `pf`.
- **H-B (L1 alignment in the ACTUAL context):** operands with s_l < s_r get the SHORTER
  pushed up `MVI A,d / ?QDDSL` BETWEEN the two pushes (right operand, immediately before
  the arith op); equal scales emit nothing. Direction and d from SCALES only. FALSIFIER:
  no shift between pushes (actual context aligns differently or not at all), a shift on
  the LEFT operand, or wrong d/direction.
- **H-C (L5 window for Add/Sub actuals):** when result scale (max of operand scales per
  L1) differs from the formal scale, the SAME window as Mul [C371] appears BETWEEN
  `?DSUOP`/`?DADOP` and the temp store: `MVI A,|d| / ?QDDSL` (up) or `?QDDSR` (down);
  both a pure-up and an aligned-plus-window shape are probed. FALSIFIER: missing window,
  window BEFORE the arith op, or d/direction not equal to |max(s_l,s_r) − s_f|.
- **H-D (Add twin):** everything above holds verbatim with `?DADOP`; R705/R707/R715 pinned
  the +/- alignment for SUBTRACT only, so Add alignment/window behaviour is UNMEASURED
  even in the expression context — this probe is genuinely open. FALSIFIER: any
  asymmetry vs the Sub twin.
- **H-E (boundary, honest perimeter):** a NESTED compound actual (Sub whose right operand
  is itself a Mul product) has NO admission in the guard here (operands must be plain
  autos); whatever DR does is recorded VERBATIM; the refusal is KEPT unless measurement
  forces otherwise — no silent generalisation.

### 4. Probes E522A..E522E (`probes/E522{A..E}.PLI`; CRLF + bare `^Z` + ≤71 cols + ONE dcl per line + first-line label + `procedure(x);` header per the hop-14 probe law + a continuation statement after every put) — predictions from the DECODED laws (NEVER fit). Shared spine: main calls `p = q(<actual>)`, `q: procedure(x) returns(fixed dec(pf,sf))` with body `return (x)` — the E52ZA/ZB byte-exact geometry [C371]; ONLY the actual block varies:

| Probe | Actual shape | Predicted caller block (law-derived) | My side TODAY (sanity, `02ea809e…`) |
|---|---|---|---|
| E522A CONTROL Sub equal scales | `a - b`, a,b dec(10,2), formal dec(10,2) | **22 B**: `21 r(a) / 3E 0A / CD..DLDOP / 21 r(b) / 3E 0A / CD..DLDOP / CD..DSUOP / 21 r(temp) / 3E 0A / CD..DSTOP` — ZERO shifts (H-A); vector cell → 6 B temp (pf 10); left `a` pushed FIRST | rc=2 at the guard, VERBATIM text, `Line 11` (sanity measured); NO `.REL` |
| E522B Sub differing operands | `a - yi`, a dec(10,2), yi dec(4,3), formal dec(10,2) | **32 B**: A's sequence PLUS `3E 01 / CD..QDDSL` between the TWO pushes — s_l 2 < s_r 3, so the SHORTER-SCALE LEFT `a` is aligned UP after its push, before the `yi` push (L1); result scale = max = 3 vs formal sf 2 → the L5 window `MVI A,01 / ?QDDSR` is ALSO expected between `?DSUOP` and the temp store (H-B + H-C composed); `?DSTOP A=0A`; push `MVI A` bytes carry operand precisions 0A/04 | rc=2 at the guard, `Line 12` (sanity); NO `.REL` |
| E522C ADD differing operands | `a + yi`, same decls as B | identical 32 B geometry with `?DADOP` in place of `?DSUOP` (H-D; open: DR may align Add differently from Sub — R705/R707/R715 pinned BOTH directions for SUBTRACT only, never assumed) | rc=2 at the guard, `Line 10` (sanity); NO `.REL` |
| E522D window-only differing formal | `m - n`, m,n dec(10,0), formal dec(7,2) | **27 B**: `21 r(m) / 3E 0A / CD.. / 21 r(n) / 3E 0A / CD.. / CD..DSUOP / 3E 02 / CD..QDDSL / 21 r(temp) / 3E 07 / CD..DSTOP` — equal operand scales → NO alignment; UP d=2 from scales ONLY while pf 7 < both operand precisions ([C371] ZB law re-tested on Sub, H-C); temp 4 B (floor((7+2)/2)) | rc=2 at the guard, `Line 11` (sanity); NO `.REL` |
| E522E BOUNDARY nested | `a - b * c`, b dec(4,3), c dec(10,2) | expected (H-E): a NESTED product — my guard refuses BY NAME; DR verdict recorded honestly, NEVER fitted; if accepted, decode only, NO arm | rc=2 at the guard |

Whole-file sizes are adjudicated by `cmp`, never by arithmetic (P3-13/14/15 lesson kept).
The `MVI A,d` bytes above are SCALE DIFFERENCES computed from the declared (p,s) rows;
d > 0 in EVERY shift-bearing probe; directions are stated per the L1/L5 wording.

### 5. Campaign + arm contract

ONE grouped run `cd /home/john/projects/sushiworks/pli80 && PLI_SRC=probes timeout 900
python3 oracle/batch.py E522A E522B E522C E522D E522E --tag e52p16 --switches '$L$D'`,
rc DIRECT (NEVER pipeline-tail); read EVERY `.PRN`; decode EVERY accepted `.REL`
FIRST-HAND into `build/p3-16/`; goldens + batch `summary.txt` + transcripts committed
VERBATIM BEFORE any `ocaml/` byte; honest verdicts (DR-accepted / dr-refuses / my-gap),
NEVER invent a golden.

ARM (after evidence, ONLY measured classes): ONE guard-pattern widening in the DEC-formal
actual arm (`ocaml/lib/codegen.ml` ~4846): admit `Ast.Ebinary ((Ast.Add | Ast.Sub), l, r)`
when BOTH operands pass `dec_product_operand` (plain non-deref DEC autos) — the SAME
route as Mul through the ONE armed `!dec_actual_mat` slot; helper RENAMED
`dec_product_operand` → `dec_arith_operand` (comment updated, law unchanged); nested
compounds and everything else keep the VERBATIM BY-NAME refusal (marker substrings and
the Line-N clause survive). NO bind change (audit §1). NO emitter bytes change (`dpush`
Add/Sub + the [C370]/[C371] window are ALREADY armed and ride the measured evidence).
Build rc=0; NEW fingerprint recorded; histogram codegen 68 / total 124 == baseline (fresh
`--build-dir`); whole-file `cmp` of every accepted probe FRESH POSITIONAL; sweep — COUNT
MOVES WITH INVENTORY, FAILS 0 binding; markers (CRLF + bare `^Z`) including the E522
boundary re-measure; DEC regressions 64/0; divcheck 9/9; **FULL GATE BEFORE CLOSE**
(only the gate runs the negative panel) → `build/gate-e52p16-reg.log`.
Registration from **1303/188** — COMPUTE panel-delta expectations, never quote them:
each accepted-and-byte-exact probe adds ONE SPECIMENS row (+k positives); each dr-refuses
probe with retained `.PRN` goes to REJECTS (+r refusals) per the E520E precedent; any
panel-PROSE edit needs the SAME-change `--update-inventory` (P3-15 gate-found law);
`git diff --cached --stat`, config NEVER staged; census OWN path (expect counts 15/0/26/0,
LOAN2 msg MOVES VERBATIM, NOTHING fixed); **C374 written from MEASURED BYTES ONLY BEFORE
ANY `spec/COVERAGE.tsv` touch**; coverage: read `PROC.CALL_DEC_ACTUALS` FIRST-HAND —
EXTEND iff its law fits the Sub/Add evidence (expected EXACT 8→8+k) + SAME-change IDS only
if a NEW row is justified (NEVER `coverage_gen.py`; 15 cols from the FIRST NON-COMMENT
row; `manual_ref` `pNN[:§X.Y][=phrase]` or `NONE:`); `coverage_check` + prose rc=0; FULL
gate rc=0 DIRECT; RESULTS §P3-16 + PLAN §5 progress row INSIDE the table **anchored by
LINE NUMBER with the 7-unescaped-pipes check** (escape raw `|`) + §P3-16 **CLOSED**.

### 6. LOAN2 direction (pre-registered, NEVER fit)

If the arm lands byte-exact, LOAN2 moves PAST line 160. The next refusal is NOT predicted
— lines after 160 were NOT audited as candidates; record the ACTUAL verbatim diagnostic.
If LOAN2 unexpectedly emits a complete `.REL`, go STRAIGHT to whole-file parity against
`golden/first/LOAN2/LOAN2.REL` (sha `712cfcb2…`, NEVER re-derived) and report the first
genuine difference. LOAN2 stays UNMODIFIED (sha `7be23ba3…`).

### 7. Framing binding on C374 wording

C374 is BYTE-TIER ONLY — every statement derives from MEASURED BYTES (authentic goldens +
this campaign), never from runtime behaviour or PLILIB semantics. The claim may say the
OBJECT shows pushes/ops/shifts in a byte order; it may NOT claim what `?DSUOP`/`?DADOP`/
`?QDDSL` DO at run time beyond recorded bytes. If L1 or L5 fail to compose in the ACTUAL
context, the ledger records the DIFFERENCE as a measured DR fact and the arm is narrowed
to the measured shapes ONLY — never a fit. The nested-compound boundary (H-E) stays
`my-gap`/unmeasured unless DR's own object decides otherwise.

## Subround P3-17 — FILE-EDIT ITEM ON A PLAIN FIXED-BINARY AUTOMATIC VARIABLE: the one-clause guard arm the authentic LOAN2 line-177 route pins — PRE-REGISTERED 2026-11-08 (operator marathon brief, LAST slice 8 of <=8; fresh chain; baseline HEAD `b1ee927a`+guard `511da709`, ledger ENDS C374, inventory 1307/189, coverage 145/95, armed binary `215c4503ffaaa1c7c970014cd6c90833656fca1fb13f838126d8e6aa41405175`) — **CLOSED (hop 5 tail, 2026-11-08)**

### 1. Measured blocker (VERBATIM, re-held this hop on `215c4503…`, POSITIONAL FRESH `build/p3-17/sanity/`)

LOAN2 sha `7be23ba3…` UNMODIFIED: rc=2, NO `.REL`:

`codegen: PUT FILE(OUTPUT) EDIT of a variable bound as fixed-binary has no byte-exact DR witness [TBD] (line 177) -- the file EDIT route is lowered for the item classes its objects pin: the DEC variable of golden/probe55/P086K and the string literal of LOAN2's own golden (115: MVI A,01/?SLCTS/?EDTOV at 053F-0542; 199: six literal chains against one format record).  A list is refused as a WHOLE, item by item, before the attach is emitted.  P086K/P086J measure the DEC variable and LOAN2 measures the string literal; every other class is carried by no EDIT object of ours on either route`

The statement (source read FIRST-HAND hop 1): LOAN2 177-178 inside
`current_year: procedure(I)`: `put skip file(output) edit` with items
`('|','Interest Paid During ''',yp,'-''',y,' is ',I,'|')` and formats
`(a,x(15),2(a,p'99'),a,p'$$$,$$$,$$9V.99',x(16),a)` -- 8 items / 7 format entries.
`yp fixed binary` = current_year LOCAL auto (cell data@0356); `y fixed binary` = MAIN
auto (cell data@02C2); `I fixed decimal(10,2)` = deref'd FORMAL, ALREADY armed by
P3-15. The refused class is exactly: **plain FIXED BINARY automatic VARIABLE as a
file EDIT (PIvar, non-deref) item.**

DATED CORRECTION of the hop-1 LEARNINGS byte labels (accepted per PROTOCOL #2; the
hop-1 text stands unchanged, this section is the authority): re-verified FIRST-HAND
this hop from `build/p3-13/p13dump.py rawcode` on the KEPT authentic golden (sha
`712cfcb2…`). The hop-1 slot numbers were disasm-column artifacts, consistently ~2-3
bytes LOW: the two fixed-bin VARIABLE chains are 11 B (not "13 B"); the `?QICOP` CALL
opcodes sit at **07BF**/**07D5** (operand slots 07C0/07D6), the `?EDTOV` CALLS at
**07C2**/**07D8** (slots 07C3/07D9); the LHLD opcodes are at 07BA (`2A 56 03`, operand
reloc **07BB->data@0356** = yp) and 07D0 (`2A C2 02`, reloc **07D1->data@02C2** = y);
the continuation word `01 06 08` reloc is **0794->code@0806** (NOT 0807 -- 0806 is the
next statement `call line();` `CD 8B 07` at 0806-0808, operand slot 0807 CHAIN-ADDR ->
078B, the first call's operand word; `C9` of current_year is at **0809**, body ENDS
076A-0809). The hop-1 "0800 `CD 62 06`" mislocated call line() #2 -- the raw bytes
show `CD 62 06` is the operand image at call #1's slot 078B-078C (chain geometry
[C358]/[C372], not new ground). Every citation below is re-derived from the raw hex +
reloc/EXT records printed this hop.

### 2. Existing DR evidence (ZERO oracle so far this subround; goldens untouched)

1. **THE witness -- authentic LOAN2.REL `07BA-07C4` and `07D0-07DA`**: each fixed-bin
   variable item = `LHLD <own cell> (2A lo hi, operand RELOC -> DATA cell) / MVI A,09
   (3E 09 = fixed binary default width) / CALL ?QICOP (CD 00 00, EXT slot) / CALL
   ?EDTOV (CD 00 00, EXT slot)` -- 11 bytes, NO `5E 23 56 EB` deref quartet, NO
   `MVI B,s`/`?QDCOP` pair. The WHOLE statement context is armed except this item
   class: attach `21 00 00`(078E->common@0) / `11 52 06` / `01 06 08`(0794->code@0806)
   / ?SIOOP(slot 0797); skip `3E 01` / ?SKPOP(slot 079C); table `21 47 00`(079F->
   data@0047) / ?EDITF(slot 07A2); literal chains `21 EC 01 / 3E 01`(SLCTS 07A9-07AB,
   EDTOV 07AC-07AE; second '|' at 07F8-07FA REUSES the SAME shared cell data@01EC,
   reloc 07F9->data@01EC); the deref'd DEC formal I `2A 54 03`(07E7->data@0354) /
   `3E 0A / DLDOP(07EB) / 3E 0D / 06 02 / QDCOP(07F2) / EDTOV(07F5)` [P3-15]; close
   ?QIOOP 0803-0805 (slot 0804). The format record (data@0047.., nested `80 02 … 81`
   rep wrapper, `p'99'` at data 0052-0056) is the armed [C090]/[C361]/[C362] machinery.
2. **KEPT accepted anchor** `golden/e52p15/E521D/E521D.REL` (sha `edca27a01a50…`,
   raw re-read this hop): the DEREF'd fixed-bin FORMAL `2A 0D 00 / 5E 23 56 EB / 3E 09
   / CD.. / CD..` at 005F-006D (operand reloc 0060->data@000D descriptor cell). The
   VARIABLE form differs by the ABSENCE of the deref quartet and by LHLD targeting the
   variable's own cell. E521D stays a SINGLE accepted-unarmed witness (do-not-
   generalise, P3-10 WF/WG law): the deref-Vint branch keeps refusing BY NAME.
3. **Console-route twins, panel-proven**: the SAME item-lowering arm `Vint | Vbased _ |
   Vbfix _` (codegen.ml ~13085) emits `lower_hl(Eident) / MVI A,vi.w / CALL ?QICOP /
   tail`, and `tail` under `is_edit` is `?EDTOV` -- E46L3 `LHLD a / MVI A,09 / ?QICOP`
   and E52PW/PX/PY/PZ/PA `… 3E 09 / ?QICOP / ?EDTOV`. **THE LOWERING ALREADY EXISTS;
   `authorize_file_edit_item` (codegen.ml 12541) is the ONLY blocker** -- its non-deref
   branch (12578-12584) admits `Vdec _` only; `Vint` falls to the `no_witness` arm.
4. P3-15 hop-2 verified the FULL record machinery (EDITF/EDTOV/attach/skip/literal
   sharing/nested rep) precedes and is independent of the guard.

### 3. Hypotheses (byte-exact; NEVER fit; every MISS recorded VERBATIM)

- **H-A (auto fixed-bin item):** a plain MAIN- or block-level `fixed binary` automatic
  variable as a file EDIT item emits EXACTLY the 11 B authentic chain
  `LHLD <own cell> (DATA reloc) / MVI A,09 / CALL ?QICOP / CALL ?EDTOV` -- no deref
  quartet, no QDCOP pair, width from the declared precision. FALSIFIER: any shift,
  width byte, extra op or a `5E 23 56 EB` quartet in the VARIABLE item.
- **H-B (LOAN2:177 twin):** the whole mixed statement -- skip prefix before EDITF,
  literals with the shared-cell law, LOCAL auto + cross-block MAIN auto + deref'd DEC
  formal in ONE list, the nested `2(a,p'99')` format -- is DR-ACCEPTED, and after the
  one-clause arm my whole file is BYTE-EXACT vs the probe golden. FALSIFIER: any
  `.PRN` error on the probe, or any cmp diff after the arm.
- **H-C (STATIC boundary, honest perimeter):** the authentic object does NOT answer
  the storage class (both LOAN2 fixed-bin items are autos). Probe C records the DR
  verdict VERBATIM. MY SIDE ALREADY REFUSES THE DECLARATION ITSELF (`codegen: STATIC
  on FIXED BINARY(15,0) is unsampled [TBD] … line 8`, sanity measured this hop) -- the
  EDIT guard is UNREACHABLE for a static bin in this compiler; whatever DR does, the
  arm decision rides ONLY on A+B, and C stays `my-gap`/unmeasured, never fitted.
- **Perimeter (never generalise silently):** the `Vint -> ()` arm admits the PLAIN
  non-deref variable class ONLY. Deref'd fixed-bin formals (E521D shape), based/
  pointer/char-class items and every other guard arm keep the VERBATIM refusal text.

### 4. Probes E523A..E523C (`probes/E523{A,C}.PLI` main-level, `E523B.PLI` the LOAN2
class twin; CRLF + bare `^Z` + <=71 cols + ONE dcl per line + first-line label +
`procedure(i);` header + a continuation statement after every put) -- predictions are
the DECODED chains VERBATIM; whole-file identity is adjudicated by `cmp`, NEVER by
size arithmetic (P3-13/14/15/16 lesson). Item chains below are opcode patterns; cells/
addresses are bind layout and are NEVER predicted.

| Probe | Statement under test | Predicted item chain (law-derived) | My side TODAY (sanity `215c4503…`, this hop) |
|---|---|---|---|
| E523A auto | `put file(pf) edit('\|','XX',a,'\|')(a,x(15),2(a,p'99'),a);` `a fixed binary` main auto | literals `LXI H,*C / MVI A,len / ?SLCTS / ?EDTOV`; `a`: **`2A lo hi (operand RELOC -> data cell) / 3E 09 / CD ?QICOP / CD ?EDTOV`** = 11 B, the LOAN2 yp/y pattern verbatim | rc=2 BY-NAME `PUT FILE(PF) EDIT of a variable bound as fixed-binary … (line 10)`, NO `.REL` (sanity HIT) |
| E523B LOAN2 twin | LOAN2 177-178 VERBATIM on named `pf`: `put skip file(pf) edit` 8 items incl LOCAL `yp`, MAIN `y`, deref'd DEC formal `i` | B's yp/y chains = the same 11 B pattern (width 3E 09); `i` = armed deref-Vdec `LHLD desc / 3E 0A / ?DLDOP / 3E 0D / 06 02 / ?QDCOP / ?EDTOV`; prologue `?SIOOP / 3E 01 / ?SKPOP / LXI H,*C(table) / ?EDITF`, close `?QIOOP`; the two '\|' items share ONE literal cell | rc=2 BY-NAME `… (line 17)`, NO `.REL` (sanity HIT; skip+EDITF route NOT separately refused -- the list guard fires FIRST exactly as in LOAN2) |
| E523C STATIC | `put file(pf) edit('\|',s)(a,2(a,p'99'));` `s fixed binary static` | H-C: DR verdict OPEN, recorded VERBATIM; if accepted, decode only, NO arm depends on C | rc=2 at the STATIC-DECLARATION guard `STATIC on FIXED BINARY(15,0) is unsampled [TBD] … line 8` (BEFORE the EDIT guard -- recorded honestly), NO `.REL` |

### 5. Campaign + arm + validation + registration contract

ONE grouped run `cd /home/john/projects/sushiworks/pli80 && PLI_SRC=probes timeout 900
python3 oracle/batch.py E523A E523B E523C --tag e52p17 --switches '$L$D'`, rc DIRECT
(NEVER pipeline-tail); read EVERY `.PRN`; decode EVERY accepted `.REL` FIRST-HAND into
`build/p3-17/`; goldens + `summary.txt` + transcripts committed VERBATIM BEFORE any
`ocaml/` byte; honest verdicts, NEVER invent a golden.

ARM (iff E523A and E523B are DR-ACCEPTED AND my compile of the SAME probes is whole-file
`cmp` rc=0 against their goldens): exactly ONE clause in the non-deref `PIvar` branch of
`authorize_file_edit_item` (codegen.ml 12580-12581): add `| Vint -> ()` after `| Vdec _
-> ()`, with a dated evidence comment (LOAN2 07BA-07C4/07D0-07DA + E523A/B). ZERO
bind/emitter change; the deref branch and ALL other arms keep the VERBATIM refusal
(marker substrings survive; E521D-form stays my-gap). Build rc=0 (grep the build log for
`Error` BEFORE recording any fingerprint -- P3-16 lesson); NEW fingerprint determinism
(default == fresh `_build-p317`); histogram codegen 68 / total 124 == baseline (fresh
`--build-dir`); whole-file `cmp` of every accepted probe FRESH POSITIONAL into a NEW
out dir; sweep -- COUNT MOVES WITH INVENTORY, FAILS 0 binding; markers (CRLF + bare
`^Z`) incl. any E523 boundary re-measure; DEC regressions 64/0; divcheck 9/9; LOAN2
UNMODIFIED POSITIONAL FRESH -> ACTUAL next blocker VERBATIM, NEVER fix (§6). **FULL
GATE BEFORE CLOSE** (only the gate runs the negative panel) ->
`build/gate-e52p17-reg.log`.

Registration from **1307/189** -- COMPUTE expectations from panel deltas, never quote
them: each accepted-and-byte-exact probe adds ONE SPECIMENS row (+k positives); each
dr-refuses probe goes to REJECTS (+r) with VERBATIM `.PRN` evidence; any prose edit of
a REJECTS row needs the SAME-change `--update-inventory` (P3-15 gate-found law);
`git diff --cached --stat`; config NEVER staged; census OWN path (expect counts
15/0/26/0; the LOAN2 msg MOVES VERBATIM, NOTHING fixed); **C375 written from MEASURED
BYTES ONLY BEFORE ANY `spec/COVERAGE.tsv` touch** (reproduce every cited byte/span from
raw records FIRST-HAND -- P3-16 lesson, hop-1 labels already corrected once this hop);
coverage: read row 66 `IO.PUT_EDIT` (currently EXACT:45) FIRST-HAND and adjudicate the
EXTEND count (expect 45 + accepted probes sharing its law; a NEW row needs explicit
justification + SAME-change IDS line; NEVER `coverage_gen.py`; 15 cols from the FIRST
NON-COMMENT row); `coverage_check` + prose rc=0; FULL gate rc=0 DIRECT; RESULTS §P3-17
(every §4 miss VERBATIM; the DATED hop-1 label corrections; parity table) + PLAN §5
progress row INSIDE the table **anchored by LINE NUMBER with the 7-unescaped-pipes
assert RUN IN CODE** (escape raw `\|`) + §P3-17 **CLOSED**.

### 6. LOAN2 direction (pre-registered, NEVER fit)

If the arm lands byte-exact, LOAN2 moves PAST line 177. The next refusal is NOT
predicted -- lines after 178 were NOT audited as candidates; record the ACTUAL verbatim
diagnostic. If LOAN2 unexpectedly emits a complete `.REL`, go STRAIGHT to whole-file
parity against `golden/first/LOAN2/LOAN2.REL` (sha `712cfcb2…`, NEVER re-derived) and
report the FIRST genuine difference; a matching CODE stream is NOT completion. LOAN2
stays UNMODIFIED (sha `7be23ba3…`). **After §P3-17 closes: STOP. The marathon slice
budget (8 of <=8) is EXHAUSTED; no P3-18 without a new operator decision.**

### 7. Framing binding on C375 wording

C375 is BYTE-TIER ONLY -- every statement derives from MEASURED BYTES (authentic
goldens + this campaign), never from runtime behaviour or PLILIB semantics. The claim
may say the OBJECT shows LHLD/width/QICOP/EDTOV in a byte order and a reloc pointing at
a DATA cell; it may NOT claim what `?QICOP`/`?EDTOV` DO at run time beyond recorded
bytes. If the probe bytes deviate from the authentic chain, the DIFFERENCE is recorded
as a measured DR fact and the arm NARROWS to the measured shapes -- never a fit; if
either A or B fails to land byte-exact, the arm is NOT taken at all.
