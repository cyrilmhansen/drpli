# E2E-41/P2 — FILE-name evidence correction, and the literal-TITLE stream OPEN byte-exact

Phase P2 of E2E-41.  Starting HEAD `283fb83d75a7fd7df892a6f3026b64af38094e83`
(E2E-41/P1b).  Two commits:

* **P2a** `E2E-41/P2a: correct DR FILE-name truncation evidence` — a documentation,
  coverage and diagnostic-wording change only; no lowering moved.
* **P2b** `E2E-41/P2b: literal TITLE stream OPEN byte-exact` — the lowering, the three
  new specimens, the retirement of E41X1, and the correction of the P1 note's
  invented "8-byte FCB prologue".

## 1. P2a — `DECL.FILE_NAME_LEN` was backwards, and is now corrected

The row asserted `perimeter C`, `dr_status REJECTS`, probe `N22_FPUT`, corpus
`DIOCALLS`.  All four were wrong:

* `N22_FPUT` is `put list(42)` (`tools/e2e_gate.py`), which declares **no FILE at
  all** — a false attribution, removed.
* `DIOCALLS` declares no FILE variable either; its first blocker is the PB6-family
  `BASED(DBUFFV)` refusal.  The programs actually first-blocked by the long-name
  refusal today are **COPY, COPYLPT, RETRIEVE** (census `msg` fields, re-snapshotted
  with the new wording; classifications unchanged, all three stay REFUSED).
* DR does **not** reject long FILE names.  [C277] measures the real rule off five
  independent historical objects (`golden/first/{COPY,RETRIEVE,COPYLPT,REPORT,DEPREC}`,
  distinct SHA-256 per `spec/lab-evidence/e2e41-p0/OPEN-INVENTORY.txt`; the
  `first8080u` copies of the same bytes are not counted twice):

| FILE name | COMMON group symbol | DEF-COMMON-SIZE | CB stores | object(s) |
|---|---|---|---|---|
| INPUT_FILE (10) | /INPUT_/ | 44 = 34+10 | 33 zeros, 0x0A, "INPUT_FILE" | COPY |
| OUTPUT_FILE (11) | /OUTPUT/ | 45 = 34+11 | 33 zeros, 0x0B, "OUTPUT_FILE" | COPY |
| SYSPRINT (8) | /SYSPRI/ | 42 = 34+8 | 33 zeros, 0x08, "SYSPRINT" | RETRIEVE, DEPREC |
| SOURCEFILE (10) | /SOURCE/ | 44 = 34+10 | full name | COPYLPT |
| PRINTFILE (9) | /PRINTF/ | 43 = 34+9 | full name | COPYLPT |
| REPFILE (7) | /REPFIL/ | 41 = 34+7 | full name | REPORT |
| EMPFILE (7) | /EMPFIL/ | 41 = 34+7 | full name | REPORT |

  The group symbol is the first six characters of the uppercased name; the size is
  computed from the **full** name.  `/INPUT_/` keeps the underscore, so the cut is a
  hard cut at six, not "up to the first non-alphanumeric".  Nothing here is inferred
  from DR's procedure-name truncation law.
* The row is now `perimeter S, dr_status ACCEPTS, mine_status REFUSED, rel_parity
  NONE, confidence MEASURED`, with the probes cited as existing DR-object paths —
  which `coverage_check.py` verifies and which satisfy traceability without a
  fabricated specimen key for a program this compiler still refuses.

**Still unmeasured, and stated as the boundary:** what DR does when two FILE names
collide after the six-character cut (`abcdef1`/`abcdef2` both name /ABCDEF/).  No
object here declares a colliding pair (P0 §10 probe E46D is the missing experiment),
so the refusal stands — silently truncating would make two files share one COMMON
group on an inference.  The refusal's message now says this ("DR accepts this name …
this compiler does not yet implement that COMMON-symbol truncation safely") instead
of calling the law unmeasured; the `Bind.RTfile` comment was corrected the same way.
No other behaviour changed in P2a.

## 2. P2b — the literal-TITLE prologue, reconstructed from the objects

The goldens are the original E2E-11 oracle objects; DR's own `$C` listings place the
OPEN at code 0x0006 and the following statement at 0x0023, so the block is **29
bytes** — no decoder involved:

```
0006  LXI  H,* S(0000)   ; the title's DATA-pool bytes (RELOC data 0x0000)
0009  MVI  A,05          ; BYTE length: 05 for '$1.$1', 09 for 'E16IN DAT'
000B  CALL ?SLCTS
000E  MOV  B,A
000F  PUSH B             ; B,A ...
0010  INX  SP            ; ... low half dropped: the title argument is ONE byte
0011  LXI  H,0E90        ; w1 = 0690 | 0800 (TITLE bit)
0014  PUSH H
0015  LXI  H,0000        ; w2 -- NOT built from B any more
0018  PUSH H
0019..001C  PUSH H x4    ; w3..w6
001D  LXI  H,INF         ; SEL-COMMON INF + RELOC common 0 (first code-segment CB ref)
0020  CALL ?OIOOP
```

21 → 29, exactly +8: the one-byte `XRA A` becomes `LXI H`(3)+`MVI A`(2)+`CALL
?SLCTS`(3) = net **+7**, and the titleless zero-word `MOV H,B / MOV L,B`(2) becomes
`LXI H,0000H`(3) = net **+1**, because after `MOV B,A` the register B holds the title
*length*, not the 0 the zero words were made from.  There is no eighth-byte FCB
structure — the six words and their order are unchanged (P0 §5).

### 2.1 The P1 note's "8-byte FCB prologue" is withdrawn

P1 §13 item 1 said the titled form "needs DR's 8-byte FCB prologue
(`3E 40 ED 51 22 F1 33 CD 3A E9`)".  That claim is corrected by [C278](c):

* The byte sequence occurs in **no file of this repository** — searched: every
  `.REL`, `.COM`, `.IRL`, `.PRN` and text under the tree (only `.git` excluded);
  zero hits for `3E 40 ED 51` anywhere.  The trigram `22 F1 33` appears exactly
  once, at offset 0x06F2 of `golden/link1/UPDATE.COM`, inside a run of little-endian
  pointer halves (`… 22 f5 33 2a e5 33 22 f1 33 21 ed 33 …`) — data, not an
  instruction boundary, and unrelated to any OPEN or TITLE route.
* The sequence cannot be compiler CODE at all: `IN 51H` reads a port, `SHLD 33F1H`
  stores an **inherited HL** pair through absolute memory (the "MOV M" family), and
  `CALL E93AH` is an **absolute** target — while PL/I-80 program objects always chain
  externals via CHAIN-EXT with `0000` operands that LINK fills.  The claim looks like
  a garbled description of a runtime-library path; it never described the TITLE
  prologue, and no inherited-register behaviour was carried into this lowering: the
  bytes above (LXI H over the pool address, MVI A over the length, CHAIN-EXT to
  ?SLCTS) decided.

## 3. Byte-exact results (whole-file `cmp` of the complete `.REL`)

| specimen | source | DR object | file bytes | CODE | result |
|---|---|---|---|---|---|
| E17B | `e13src/E17B.PLI` | `golden/e2e11i/E17B/E17B.REL` | 640 | 0x00AC | **identical** |
| E16C | `e13src/E16C.PLI` | `golden/e2e11h/E16C/E16C.REL` | 640 | 0x0095 | **identical** |
| E18A | `e13src/E18A.PLI` | `golden/e2e11j/E18A/E18A.REL` | 1152 | 0x0131 | **identical** |

All three landed on the first compile with the lowering; nothing was tuned after the
fact.  What each one additionally pins:

* **E17B/E16C** — the two literal lengths (5 and 9) and the pool order: the title
  occupies data 0x0000 (SET-LC per block, one per literal), the PUT strings follow
  above it; `DEF-DATA-SIZE` 0x16 / 0x14 = pool + the 2-byte `x` cell.
* **E18A** — four `get file(inf) list(x)` statements under one titled OPEN, all
  attaching **0x0690** while the open pushed **0x0E90**: the strongest single witness
  that the attach word is the statement's, not a mask of w1 (P0 §8, [C274](a)).
* Register state: the block reuses nothing from previous statements and leaves
  `st.last_imm` clear; E17B/E16C/E18A interleave the block with console PUTs whose
  own `LXI H,*S(pool)` relocations follow it in record order.

Controls re-checked on the full gate: P081Q (384 bytes, code 63), P072H (384, code
65), all console GET/PUT specimens, and the P1 option-parser witnesses (parse gate)
— see the gate numbers in section 6.

## 4. Prescan and codegen-state interaction

`prescan_stmt` gained an `Ast.Sfilestmt { key = "OPEN" }` arm that demands one pool
cell per distinct literal TITLE string via `pdec_str_cell` — the same dedup-by-content
rule as PUT literals ([C152]); the lowering then allocates it through the shared
`pool_str`.  If prescan and lowering disagreed, `st.pool_next <> st.base` fails loud
(the existing invariant), so the ordering cannot drift silently.  A variable title is
not demanded and refuses in `open_title`; an open that refuses for any other reason
never reaches either walker's output.

`open_mode_word` takes the title bit as a measured composition: `w1 |= 0x0800` iff a
TITLE clause is present — the bit fits all 34 P0 rows (`W1-BITFIT.txt`: 29 set, the 4
titleless clear — **[E2E-41/P3a] the count here is wrong: the matrix gives 30 set, 4
clear,** with 25 literal + 5 variable titles, and the bit agrees with the presence of a
TITLE clause in all 34 rows; see spec/lab-evidence/e2e41-p3/TITLE-CENSUS.txt [C279]).  The lowering of the zero word switched from the `MOV H,B` pebble to
`LXI H,0000H` in the title branch **because the goldens show it**, and the two branches
share `load_file_cb` and `?OIOOP` unchanged, so the P1 titleless bytes are untouched.

## 5. Runtime

DR's own runs of these objects are archived (`oracle/linkrun.py` staging + tails
already encode them: `ARGS["E17B"]=ARGS["E18A"]="INF.DAT"`, `STAGE_IN` D:INF.DAT from
`e13dat/INF.DAT` = `7\r\n8\r\n9\r\n\x1a`):

* `golden/e2e11iu/E17B.output.txt` — `D>E17B INF.DAT` → `X=         7 REACHED SECOND`.
* `golden/e2e11jr/E18A.output.txt` — `D>E18A INF.DAT` → `X1=         7 X2=         8
  X3=         9`, then `END OF FILE (1), File: INF=INF.DAT` + `Traceback: 08BE 0869
  01E9 3900 # 0802 04B0 8082 01E9`.  The fourth GET **is meant to hit EOF** — the
  fixture has three records — and the row asserts the authentic abort, exit-by-
  termination, not a clean rc.
* `golden/e2e11hr/E16C.output.txt` — `D>E16C` (no tail) → `UNDEFINED FILE (1), File:
  INF=NUL`.  A literal TITLE demonstrably did **not** name E16C's file; filename
  resolution follows the FILE variable / command tail, never the title spelling (P0
  §11).  E16C is a byte-exact specimen only; no runtime row is registered for it,
  because no archived DR transcript of it *succeeding* exists in this repository and
  a passing run would be a new DR execution, not a recovered fixture.

Two RUNTIME.txt rows were added (E17B, E18A, `kind=dr_oracle`: the expectations are
DR's own transcripts, recovered above); the runtime panel is 48 → **50 rows, 50/50
OK**.  The gate's `--link-run --only E17B E18A` arm links BOTH arms from the
byte-identical `.REL`s and compares raw consoles:

```
  link :    E17B: .COM IDENTICAL vs DR
  run  :    E17B: console BYTE-EQUAL (28 raw bytes): 'X=         7 REACHED SECOND\r'
  link :    E18A: .COM IDENTICAL vs DR
  run  :    E18A: console BYTE-EQUAL (132 raw bytes): 'X1=         7 X2=         8 X3=         9\r\nEND OF FILE (1), File: INF=INF.DAT\r\nTraceback: 08BE 0869 01E9 3900 # 0802 04B0 8082 01E9\r'
```

which is DR's archived console reproduced byte for byte.  The final standard gate
(`--runtime`, exit 0) repeats both programs' runtime rows and the whole byte panel;
see section 7.

Getting there exposed one
harness hole, fixed here in the same commit: `link_run`'s transcript anchor was
`{name}\r\r\n` — the command ECHO — but `linkrun.py`'s ARGS puts the command tail on
that line (`D>E17B INF.DAT\r\r\n`), so the anchor matched nothing and the first P2b
run reported MISSING TRANSCRIPT.  No OUTPUT_CHECK name had ever been run with a tail
(ARGS exists since e2e-11 for exactly these three E2E-13 programs), so the pattern
now allows the tail: `{name}(?: [^\r\n]*)?\r\r\n`.

Honest limits:

* The `.REL` byte-identity means the linked image is the same image on both arms; the
  runs validate the *encoding against DR's runtime*, and the console comparison is
  then an equality by construction, not a second compiler-side test.  That is the
  same framing P1 §9 used; the evidence added here is that the title prologue's
  *parameter* (one length byte on the stack, address+length in HL/A) is what PLILIB
  consumes — the programs read the staged file and print the converted numerics.
* E18A's traceback words are absolute-link addresses; they are part of the expected
  transcript only because the two `.COM` images are byte-identical.

## 6. Negative panel: E41X1 retired

E41X1 (`open file(f) title('XY'); close file(f);`) was registered in P1 as a
`my-gap` negative with the reason "the titled form needs DR's 8-byte FCB prologue …
not lowered yet".  P2b lowers the literal TITLE, so that reason is gone — and the
*reason it now refuses* ("OPEN FILE(...) naming no INPUT or STREAM has no DR
witness") is **unmeasured on the DR side**: no object in the repository opens without
naming a mode, and P0 §10 probe E46C is the missing experiment.  The P1 policy (see
the comment at the head of that REJECTS block) is that panel entries state a measured
DR verdict, so E41X1 was **retired from the active panel**, its registration and
original reason preserved in a retirement comment in `tools/e2e_gate.py` and here.
Its source is not claimed byte-identical to DR (no DR object exists for it); the
byte-parity claims live on E17B/E16C/E18A.  Negative panel: 131 → 130 rows.

Remaining FILE-statement negatives on the panel: E41X4 (READ of a named file),
E41X5 (PUT of a named file).  Refusals kept by name, measured evidence cited in
`spec/lab-evidence/e2e41-p2/REFUSALS.txt`: variable TITLE (?SLVTS), titled
output/print open, ENVIRONMENT/KEYED/DIRECT/PRINT/PAGESIZE/LINESIZE/UPDATE options,
OPEN with no mode word, multi-file CLOSE, PUT FILE, and every record-oriented
statement.  The long-FILE-name refusal also stays (section 1).

## 7. Gate numbers after P2

`python3 tools/e2e_gate.py --runtime` (exit 0), plus `--link-run --only E17B E18A`
for the two DR arms (section 5) and the unchanged `tools/parse_gate.py` set:

* byte panel: 985 → **988/988 byte-exact / 0 fail** (+E17B, +E16C, +E18A; P081Q and
  P072H re-verified whole-file identical in the same run).
* negative panel: 131 → **130/130** (E41X1 retired, section 6).
* divergence panel: **9/9** as recorded (PB6/PB13/E40Q4/AB13/E36H5/E38S4/S103/S105/
  S116 — untouched).
* runtime panel: 48 → **50/50**, the new E17B/E18A rows passing expectation and
  termination; P081Q/P072H and every console GET/PUT row unchanged.
* coverage: **89 rows / 0 errors / 0 warnings** (no new contracts: FILE.OPEN_STREAM
  and IO.GET_LIST_FILE extended in place).
* census: `--verify` clean, counts unchanged (44 HISTORICAL / 41 AUTHENTIC / 3
  DR_REJECTED / 15 EXACT / 0 DIFFERS / 26 REFUSED / 0 UNEXPECTED); the snapshot's
  ENTER/UPDATE `msg` fields now carry the P2 wording (their first refused options
  were always KEYED/UPDATE — TITLE removal changed only the message, not the
  bucket), and COPY/COPYLPT/RETRIEVE/DEPREC carry the P2a long-name wording.
* parse gate: `1076 ok / 7 parity-rejects / 6 FAIL of 1091` with the **identical
  baseline failure set** (AB20, E36H13, E37A1, E39S4, LR16, PB16 — all pre-existing,
  none FILE-option) and `file-option witnesses: 9 ok / 0 FAIL of 9`: the P1
  option-parser witnesses are untouched, exactly as the mission required.
* `dune build`: clean (the two pre-existing warnings in pli80bind/pli80deps only).

## 8. What P3 may take, in order, with the witnesses already in this repository

1. **PUT FILE(f) list** — attach word 0x0652 (36 measured sites in `SIOMODES.txt`),
   the `?PNCOP` chain already lowered for the console, and goldens `golden/e2e11h/
   E16D` and `golden/e2e11i/E17D` (titled **output** opens, w1 0x0E50 — so P3 also
   completes the titled-output OPEN route as a side effect); `golden/e2e11iu/E17D/
   OUT.DAT` (128 bytes, padded with 0x1A) is the archived output-file comparison.
2. **CLOSE under the new specimens** — already byte-exact; nothing to do.
3. **w5/w6 together, mode-less OPEN, DIRECT without UPDATE** — need the P0 §10 probes
   (E46A/E46C) compiled by DR; no new oracle run is authorized in P2 and none was run.
4. **Variable TITLE (?SLVTS)** — 5 measured sites (LOAN2:56, CREATE:22, COPYLPT,
   RETRIEVE, KEYFILE) but all five sit behind unrelated historical blockers
   (long-name refusal, STATIC refusals, PUT FILE); needs a fresh probe object.
5. **FILE-name truncation lowering** — measured rule ([C277]), collision case still
   unmeasured (E46D).
