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
