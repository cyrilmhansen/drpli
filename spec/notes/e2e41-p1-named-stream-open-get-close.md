# E2E-41/P1 — OPEN, GET FILE(...) LIST and CLOSE of a named stream, byte-exact

Phase P1 of E2E-41.  P0 (`e2e41-p0-file-open-reconnaissance.md`) measured DR's file OPEN
off 34 blocks in 24 objects; this phase turns two of those measurements into a lowering
and says precisely where the lowering stops.

Delivered, all byte-exact whole-file against a DR object:

| specimen | source | object | code | what it pins |
|---|---|---|---|---|
| `P081Q` | `probes/P081Q.PLI` | `golden/e41p1/P081Q/P081Q.REL` (== `golden/probe50/...`) | 63 | `open file(f) input` + `get file(f) list(i)` (FIXED BIN) + `close file(f)` |
| `P072H` | `probes/P072H.PLI` | `golden/e41p1/P072H/P072H.REL` (== `golden/probe40/...`) | 65 | same, with `s CHAR(30) VARYING` as the GET item |

Nothing else about FILE statements is implemented.  PUT, READ, WRITE, KEYED, DIRECT,
PRINT, ENVIRONMENT, TITLE, PAGESIZE, LINESIZE, UPDATE and record-oriented I/O all still
refuse, and the refusal now names the option that is missing evidence instead of saying
"statement kind not in supported subset" (section 8).

## 1. The goldens are a fresh oracle run, and the fresh run equals the historical one

`runtime_check` needs a `.PRN` beside the registered golden (external references), and
`golden/probe40/P072H/` and `golden/probe50/P081Q/` contain only `dir.txt` + `.REL`.  So
both probes were recompiled through the current oracle:

```
$ PLI_SRC=probes python3 oracle/batch.py P081Q P072H --tag e41p1 --reuse
   P081Q: {'status': 'ok', 'outputs': {'PRN': True, 'REL': True}}
   P072H: {'status': 'ok', 'outputs': {'PRN': True, 'REL': True}}
```

and each fresh `.REL` is byte-identical to the historical one:

```
$ cmp golden/e41p1/P081Q/P081Q.REL golden/probe50/P081Q/P081Q.REL   # silent
$ cmp golden/e41p1/P072H/P072H.REL golden/probe40/P072H/P072H.REL   # silent
```

No existing golden was written to; the new tag is additional evidence, and E2E-33/P0's
rule ("a probe that does not run under the current oracle is not registrable") is what
made the recompile necessary.

The listings are the cross-check P0 asked for.  They carry no disassembly column, but
they give the address each statement starts at, which pins every block length
independently of my decoder:

```
   1 a 0000 pp081q: procedure options(main);
   2 c 0006   declare f file, i fixed;
   3 c 0006   open file(f) input;            OPEN  = 0x001B - 0x0006 = 21 bytes
   4 c 001B   get file(f) list(i);           GET   = 0x0036 - 0x001B = 27 bytes
   5 c 0036   close file(f);                 CLOSE = 0x003C - 0x0036 =  6 bytes
   6 a 003C end pp081q;
CODE SIZE = 003F
```

```
   3 c 0006   open file(f) input;            OPEN  = 21
   4 c 001B   get file(f) list(s);           GET   = 0x0038 - 0x001B = 29
   5 c 0038   close file(f);                 CLOSE =  6
CODE SIZE = 0041,  DATA AREA = 001F
```

This corrects a P0 artefact: `openblocks.py` reported the OPEN block as 24 bytes,
because its backward walk stops at `CALL ?OIOOP` and the window it prints runs to the end
of the following item, including the 3-byte operand of the `LXI H,<control block>`
relocation.  The block is 21 bytes (P072H and P081Q both; and the other 32 blocks P0
listed are 3 bytes longer than their true instruction span for the same reason).  The
bytes P0 decoded were right — that is what made this lowering land byte-exact on the
first compile — but the lengths in `OPEN-BLOCKS.txt` and `OPEN-MATRIX.tsv` carry the
extra 3.  See section 10.

## 2. The OPEN block

DR's 21 bytes, from `golden/probe50/P081Q/P081Q.REL` at code offset 0x0006 (and
`tools/dis80.py`, with the five single-byte MOV forms that its DR80 table lacks supplied
from P0's own decoding of the same bytes):

```
af           XRA  A            ; A := 0 — this open has no TITLE
47           MOV  B,A          ; B := 0 (the title length; also kept for the zero words)
c5           PUSH B            ; one stack byte above the six words = the title
33           INX  SP           ; ... and the convention that leaves SP one past the data
21 90 06     LXI  H,0690H      ; w1, the option word
e5           PUSH H
60 68        MOV  H,B ; MOV L,B    ; HL := 0000, both halves built out of the 0 in B
e5 e5 e5 e5 e5   PUSH H x5      ; w2 w3 w4 w5 w6
21 <rel>     LXI  H,/F/ + 0    ; the file's control block (COMMON group, offset 0)
cd <ext>     CALL ?OIOOP
```

`XRA A / MOV B,A / PUSH B / INX SP` is DR's own lengthless-string prologue.  It is not
invented here: P0 §11 found the identical four bytes (`1A 47 C5 33` at 83A0) inside
DR's console-input routine `?CIN` in both `PLILIB.COM` and `PLILIB0.COM`, serving exactly
the no-title form of the same parameter, and P019B's titleless `open file(pf) print`
carries `af 47 c5 33` at the head of its block.  Three independent sites, and the
`?CIN` pair of forms is what proves the rule "title present ⇒ string, absent ⇒ one zero
byte" rather than one of those being my guess.

The five `PUSH H` instead of five more `LXI H,PUSH H` is DR's register-reuse peephole
(the same class as [V102/V103]'s `MOV B,A`).  `st.last_imm` is cleared before and after
so no later statement inherits 0690H through HL.

## 3. What 0x0690 is, and why it is composed rather than copied

Four bits, each with its own witness in P0's fitted table (`W1-BITFIT.txt`, 34 samples,
15 distinct values, every bit fitted by at least two objects):

| bit | set by | witnesses here |
|---|---|---|
| 0x0400 | the file is a declared FILE, not the console | all 34 samples |
| 0x0200 | stream organisation | all `stream`/`input` sites; DR's default organisation |
| 0x0010 | stream (as distinct from record) I/O | same sites |
| 0x0080 | input mode | P081Q, P072H, P021, and every titled stream input |

The interesting part is that **`input` and `stream` spell the same word**.  P021:3
`open file(inf) input title('$1.$1')` and E17B:4 `open file(inf) stream
title('$1.$1')` both measure `w1 = 0x0E90` (9 sites, `OPEN-MATRIX.tsv`), so the choice of
keyword does not change the bits — 0x0200 and 0x0080 are set either way, and 0x0800 comes
from the TITLE.  Drop the title from that word and you have 0x0690, which is what P072H
and P081Q actually contain.  Both spellings are therefore accepted, and they lower
identically.

What is *not* accepted is an OPEN that names no mode at all.  `open file(f);` would take
the same 0x0690 under the default-bit reading above, and that is exactly why it is
refused: the reading is an inference, not a measurement, and P0 §12 probe C exists to
settle it.

## 4. Why w2..w6 are zero here, one word at a time

The five zero words are not "the rest of the record", they are five separate absences,
and each is stated because P0 measured what fills it when it is *not* absent:

* **w2 ORGANIZATION** — an ENVIRONMENT datum.  In all 34 samples it is nonzero only where
  bit 0x4000 (ENVIRONMENT) is set, taking 08 (stream) / 10 (direct) / 18 (keyed).
* **w3 BLOCK(n), w4 FILE(n)** — record-oriented sizes.  The nearest witness that they
  *can* be nonzero on a stream open is P042A:3 `open file(output) stream` with
  B(4096)/F(4096) in w3/w4; P072H and P081Q write neither and measure 0/0.  (P0's
  warning stands: F(128) and B(8000) in `environment(f(128),b(8000))` are two different
  quantities, and the 128-byte `OUT.DAT` of E17D comes from an open that spells F(128).)
* **w5 PAGESIZE, w6 LINESIZE** — set only by their own options, and each of those has one
  witness site in P0 §4 (P021 for PAGESIZE=60 in w5, KEYFILE for LINESIZE=60 in w6),
  with no site measuring both.  Neither option appears in these two probes, so both stay
  zero; the words are not swapped on the strength of that, and section 12 keeps the
  probe that would test it.

## 5. The GET: an attached control block, and one shared item chain

`golden/probe50/P081Q/P081Q.REL` at 0x001B:

```
21 <rel>     LXI  H,/F/ + 0     ; the ONLY instruction the console GET does not emit
11 90 06     LXI  D,0690H       ; the attach mode word
01 00 00     LXI  B,0000H       ; continuation, patched by the usual triple
cd <ext>     CALL ?SIOOP
cd <ext>     CALL ?GNVOP        ; item conversion — identical to the console form
f2 <hi lo>   JP  <continuation>
cd <ext>     CALL ?QCIOP        ; fixed-bin item
22 <a b>     SHLD i
cd <ext>     CALL ?QIOOP
c3 <lo hi>   JMP  back          ; the loop back-edge DR emits after the last item
<triple for the continuation>
cd <ext>     CALL ?QIOOP        ; statement terminator
```

P072H's varying item is `?GNVOP / JP / LXI H,s / MVI B,1E / CALL ?SSVFS` — byte-for-byte
the console CHAR-VARYING form already pinned by [X201/X202].  That is the reason
`lower_get_body` exists as one function with an attach routine as a parameter rather than
as a second copy of GET: the item lowering cannot drift between the two paths, and the
console specimens (R903/R904, X201/X202, N29_DECININT, LOAN1, NETWORK) still pass
unmodified.

**0x0690 is not `w1 & ~something`.**  P0 §8 tested the tempting rule
`DE = w1 & ~0x4800` and it fails on 30 of 68 comparable attaches.  The attach word is a
property of the *statement*: `SIOMODES.txt` counts 26 attaches at 0x0690 including ones on
files whose OPEN word was 0x0E90 (E16C, E17C, E18A, E18B — titled opens, different w1).
So the constant is written as a witnessed value for input statements, with its own
comment, and an output or keyed attach (0x0652 for `put list`, 0x0650 for `write from`,
0x0594 for keyed read — all measured, none lowered here) borrows nothing.

## 6. CLOSE

```
21 <rel>     LXI  H,/F/ + 0
cd <ext>     CALL ?CIOOP
```

Six bytes, and it pushes nothing — all 5 measured CLOSE sites (E16D, E17D, RETRIEVE,
P072H, P081Q) are this.  The consequence for registration is that a CLOSE specimen is
only falsifiable by *file length*: adding a `PUSH H` would change the length and not the
meaning of any single byte, so `P081Q`/`P072H` are whole-file comparisons (384 bytes each)
rather than region comparisons.  `CLOSE FILE(a,b)` (more than one file) is unmeasured and
refuses: DR may well push a vector of control blocks, and a guess would be indistinguishable
from the truth in a single-object probe.

## 7. Control block and COMMON layout (unchanged, re-verified)

Each `dcl f file` becomes a NAMED COMMON group `/F/` of `file_cb_bytes`: 33 zero bytes,
then the name length, then the uppercased name.  Both probes declare `f`, so both groups
are 35 bytes, matching `LINK-DEF-COMMON-SIZE abs 0023 F` in the goldens, and
`LINK-SEL-COMMON F` appears once even though three statements reference `/F/` — the
`st.cur_common` rule (select only on change), which `load_file_cb` now shares with
`on_reg_prefix` so the ON-unit and file paths cannot drift apart.

## 8. Refusals that stay, and what they now say

`open file(f) ...` refuses with the offending option named:

```
codegen: OPEN option KEYED is outside the E2E-41/P1 witnessed subset [TBD] (line 37) -- P0
measured 34 OPEN blocks in 24 DR objects (spec/lab-evidence/e2e41-p0/OPEN-MATRIX.tsv);
TITLE needs DR's 8-byte FCB prologue, ENVIRONMENT its ORGANIZATION and RECORD SIZE words,
PAGESIZE/LINESIZE/PRINT/KEYED/DIRECT their own bits and words, and none of those
combinations is byte-exactly pinned by a .REL in this repository yet
```

That is the message the census now records for the two historical programs that use
KEYED/UPDATE opens: `artefacts/ENTER.PLI:37` (`open file(emp) keyed output
environment(f(128),b(8000))`) and `artefacts/UPDATE.PLI:31` (`open file(emp) update
direct environment(f(128))`).  Both stay in the REFUSED bucket; only their message
changed, which is why the census snapshot was rewritten and the counts did not move.

Also refused, by name: any other FILE statement (`READ`, `WRITE`, `REWRITE`, `UPDATE`,
`CREATE`, `DELETE`, `REWIND` — "no DR witness in this repository yet"), `OPEN` with no
mode word, `CLOSE` with a list of files, `GET FILE(f)` with any second option, with an
expression item, or with EDIT/SKIP, and every PUT carrying a file.

## 9. Execution: the two programs run, and the control run says why that means something

Neither probe prints anything (they have no PUT), so "the console is empty" is not an
assertion — an empty expected string matches every transcript.  `runtime_check` therefore
grew negative expectations (`!text`), and both rows assert that DR's file-open failure is
ABSENT: `!UNDEFINED FILE|!Traceback`.  The staging exists already (`oracle/linkrun.py`
`STAGE_IN`); the file is `F.DAT`, because DR names the FCB from the FILE *variable*
(P0 §9, and the E16x rows above it), not from any title.

```
$ python3 oracle/linkrun.py link --tag e41rt --names P081Q P072H --out e41rt --reuse
   P081Q: COM=True ... /F/ 1952   /SYSIN/ 19D9 | /SYSPRI/ 1A00 | CODE SIZE 1852
   P072H: COM=True ... /F/ 18C8   /SYSIN/ 194F | /SYSPRI/ 1976 | CODE SIZE 17C8
```

LINK resolves every reference of my object against DR's own `PLILIB.IRL` — including the
`/F/` common and `?OIOOP`/`?SIOOP`/`?CIOOP`/`?GNVOP`/`?QCIOP`/`?SSVFS`/`?QIOOP` — with no
undefined symbol, which is the [C137] check the gate runs separately.

With `e41dat/F.DAT` staged (5 bytes, `17 CR LF SUB`): both exit rc=0, console empty.
With the file removed (the control, `spec/lab-evidence/e2e41-p1/RUN-*-no-F.DAT.txt`):

```
UNDEFINED FILE (1), File: F=NUL
Traceback: 056D 03AC 011B 0000 # 0000 0000 9000 0006     (P081Q)
Traceback: 056F 03AE 011B 0000 # 0000 0000 9000 0006     (P072H)
```

The control is what makes the silent success worth anything: the runtime consumed the
pushed words, found the control-block address, attempted the open, reported the CP/M name
it wanted, and only with the file present did GET and CLOSE complete.  The two tracebacks
differ in their first word only (056D vs 056F), which is the 2-byte difference in code
size between the two probes (63 vs 65) — consistent, and the reason I do not read the
`9000 0006` pair as the mode word nibble-swapped: P0 §8 warns against nibble assumptions.

Honest limit: both `.REL` images are byte-identical to DR's, so a run of "my" object *is*
a run of DR's object.  The gate prints exactly that framing for these rows
(`byte-exact image: run validates expectation+oracle, not my lowering`).  To make the
comparison literal rather than inferred, DR's historical object and mine were each linked
separately by LINK 1.31 against `PLILIB.IRL` and each run with the same staged `D:F.DAT`:

```
$ python3 oracle/linkrun.py link --tag e41dr --names P081Q P072H --out e41dr --reuse   # DR's .REL
$ python3 oracle/linkrun.py run  --tag e41dr --names P081Q P072H --out e41dr --reuse
$ cmp golden/e41dr/P081Q.COM golden/e32rt_P081Q/P081Q.COM      # silent, 7040 bytes
$ cmp golden/e41dr/P072H.COM golden/e32rt_P072H/P072H.COM      # silent, 6912 bytes
$ cmp golden/e41dr/P081Q.output.txt golden/e32rt_P081Q/P081Q.output.txt   # silent
$ cmp golden/e41dr/P072H.output.txt golden/e32rt_P072H/P072H.output.txt   # silent
```

The linked `.COM` images and the console bytes agree byte for byte, so the executions are
the same execution.  What these runs establish is that the *encoding* P0 measured is the
encoding DR's runtime accepts — not that some other lowering would also have worked.

## 10. Two corrections to the P0 note

1. **§1(c) and §12's "4 bytes / one word longer" comparison of a `probes/P072H.REL` to an
   `E45P` copy is withdrawn: there is no E45P batch in this repository.**  The oracle
   directory holds the harness (`batch.py`, `linkrun.py`, `run.py`, `cpmwork.py`,
   `disks/`, `in/`, `srctools/`), not batch output, and `grep -c E45P` over every P0
   artefact and over the P0 note returns 0 — the string appears only in prose P0 wrote.
   The real P072H and P081Q objects are `golden/probe40/P072H/P072H.REL` and
   `golden/probe50/P081Q/P081Q.REL`, **both 384 bytes**, both re-measured here as code 65
   / code 63 and reproduced byte for byte by a fresh oracle run (section 1).  Nothing
   else in §1(c) (the line-number rule: LF-only sources report roughly half the real
   line) is affected by this, and that part remains diagnostic-only.
2. **OPEN/CLOSE block lengths in `OPEN-BLOCKS.txt` / `OPEN-MATRIX.tsv` are 3 bytes too
   long**, for the window reason in section 1.  The decoded bytes are correct — the
   lowering was built from them and landed byte-exact — but a length taken from those
   files will not match a listing.  `spec/lab-evidence/e2e41-p0/OPEN-BLOCKS.txt`
   regenerates byte-for-byte from the committed tools (verified this phase with
   `python3 spec/lab-evidence/e2e41-p0/openblocks.py | diff - ...`), so the artefacts are
   reproducible; the fix is to read statement addresses from the `.PRN` (section 1) or to
   subtract the relocation operand.

I also re-checked the P0 claim about `?OFCOP` appearing in OPEN routines; that claim is
already absent from the committed note, and the 18 objects that chain `?OFCOP` do so from
procedure-exit/ON-unit cleanup, not from any OPEN path.

## 11. Gate results after P1

Numbers moved, and only in the directions this phase earns: 983 -> **985** byte-exact
(+P081Q, +P072H), 128 -> **131** refusals (+E41X1, +E41X4, +E41X5, each a `my-gap' with a
quoted DR object -- section 8 of `REFUSALS.txt` says why the two unmeasured refusals are
NOT on the panel), 46 -> **48** runtime rows, 86 -> **89** coverage rows, and the
inventory gains 5 rows.

* e2e gate (run with `--runtime`): **985 byte-exact / 0 fail of 985**, negative panel
  **131/131** refused, divergence panel 9/9, runtime panel 48/48, exit 0.
* runtime panel: 48 rows (was 46), both new rows OK, negative assertions live.
* parse gate: 1076 ok / 7 parity-rejects / 6 FAIL of 1091 — the same six pre-existing
  failures as at 6e665e5 (AB20, E36H13, E37A1, E39S4, LR16, PB16, none of them a FILE
  statement), and `P080Q.PLI` moved from "ok" to a parity-reject because DR itself has no
  `.REL` for it (section 12 of the P0 note, resolved here).  Plus 9 pinned
  option witnesses, 2 of them refusals.
* corpus census: counts unchanged (`HISTORICAL 44 / AUTHENTIC 41 / DR_REJECTED 3 / EXACT
  15 / DIFFERS 0 / REFUSED 26 / UNEXPECTED 0`); two `.msg` strings updated to the new
  OPEN refusal, snapshot rewritten.
* coverage panel: 89 rows, 0 errors, 0 warnings (3 rows added: `FILE.OPEN_STREAM`,
  `FILE.CLOSE_STMT`, `IO.GET_LIST_FILE`; each `SINGLE_SAMPLE`, because two specimens is
  below the table's MEASURED threshold of three).
* `spec/INVENTORY.txt`: +5 rows via `--update-inventory` (2 specimens, 3 refusals).

## 12. Evidence files

* `spec/lab-evidence/e2e41-p1/OPTIONS-AST-BEFORE.txt`, `OPTIONS-AST-AFTER.txt` — the same
  witnesses dumped with `bin/pli80tree.exe` before and after the parser change, with the
  codegen verdict for each.
* `spec/lab-evidence/e2e41-p1/P081Q-REGION.txt` (and the P072H companion inside) — DR's
  `.REL` bytes, `dis80` output, the `.PRN` statement addresses, my `.REL`, and the
  whole-file comparison.
* `spec/lab-evidence/e2e41-p1/REFUSALS.txt` — one entry per refused shape, with the
  message my compiler prints and the DR evidence (or the absence of it) behind it.
  The five small sources it cites are committed under
  `spec/lab-evidence/e2e41-p1/refusals/`, so the file re-runs.
* `spec/lab-evidence/e2e41-p1/RUN-{P081Q,P072H}-{with,no}-F.DAT.txt` — the four run
  captures of section 9, plus the mine-vs-DR `.COM` and console comparisons.
* `golden/e41dr/{P081Q,P072H}/` and `golden/e41dr/*.COM` — DR's historical objects linked
  separately, for the execution comparison in section 9.
* `spec/lab-evidence/e2e41-p1/CODE-DIFF.txt` — the executable-line diff of the codegen
  change with every comment stripped (the [E2E-40/P10a] method): **+124 / -10 lines** for
  the whole phase, which is the size of the lowering without 200 lines of prose in the way.
* `e41dat/F.DAT` — the 5-byte staged input file.
* `golden/e41p1/{P081Q,P072H}/` — fresh oracle `.REL` + `.PRN` + `dir.txt`.

## 13. What P2 needs before it can extend this

Ordered by how much of the corpus they unlock, each with the probe that would settle it:

1. **TITLE** — 25 of 34 measured OPENs.  Needs DR's 8-byte FCB prologue (`3E 40 ED 51
   22 F1 33 CD 3A E9`) and the `?SLCTS`/`?SLVTS` string call in place of `XRA A`.
   E16C/E18A are already byte-exact specimens of the *console* side and their `.REL` files
   contain the titled OPEN, so no new probe is required — the specimens exist.
2. **PUT FILE(f)** — attach word 0x0652 (36 sites), `?PNCOP` chain already lowered for
   the console.  E16D/E17D have `close file(outf)` and would become byte-exact, and the
   128-byte `golden/e2e11iu/E17D/OUT.DAT` is the output-file comparison P0 §9 wanted.
3. **w5/w6 together** — `e2e41-p0` §12 probe A (PAGESIZE and LINESIZE both literal, one
   open).  Until then the assignment of the two words rests on two single-witness sites.
4. **`open file(f)` with no mode word**, and **DIRECT without UPDATE** — §12 probes C and
   the ENTER/UPDATE opens.
5. **Keyed** — `KEYED`+`ENVIRONMENT` (0x0152/0x0153/0x0550) and the attach words 0x0594 /
   0x0514, plus `READ FILE(f) INTO(x) KEYTO(k)`, whose option vocabulary the parser now
   keeps intact (P1a) and whose `?KEYTO`/`?RNIOP` chain is already lowered for the console.
