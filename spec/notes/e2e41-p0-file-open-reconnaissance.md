# E2E-41 P0 — what DR's file-OPEN actually is (reconnaissance only)

HEAD at start: `935f18a` (E2E-40 Part A). Gate re-verified at the end of this
episode and unchanged: **983 byte-exact / 0 fail, 128/128 refusals, 9/9
divergences, 46/46 runtime, coverage 86 rows / 0 errors / 0 warnings, census
44 HISTORICAL / 41 AUTHENTIC / 15 EXACT / 26 REFUSED / 0 UNEXPECTED, exit 0.**

**P0 changes no OCaml source, no test registration and no golden.** Everything in
this note comes from DR objects already in the repo, read with the tools in
`spec/lab-evidence/e2e41-p0/`. Nothing here is a registered claim: no CLAIMS.md row
is added, because a claim in this spec gets registered with the gate row that
re-measures it. Sections 6-8 state *candidates* with their witnesses and their
counterexamples, and section 10 says exactly which samples are missing before any of
them can become a claim.

---

## 1. Where this compiler stands today

| layer | state | where |
|---|---|---|
| lexer | OPEN/READ/WRITE/REWRITE/UPDATE/CLOSE/CREATE/REWIND/DELETE are keyword tokens | `ocaml/lib/lexer.ml` |
| parser | all nine become one node: `Sfilestmt { key; file; opts }`; `opts` comes from `parse_io_opts` | `parser.ml:690-698`, `parser.ml:813-826` |
| option vocabulary | `ioopt_keys` = FILE STREAM SOURCE SINK TITLE ENVIRONMENT RECORD PREAMBLE KEYFROM KEYINTO KEY SET SETUPDATE INPUT OUTPUT UPDATE APPEND VARYING ENV | `parser.ml:106-109` |
| binder | `RTfile of { internal }`, built for `Ast.Tfile` and for a `dcl … file` with/without INTERNAL; a FILE is excluded from the value-symbol arms | `bind.ml:48, 86, 142, 209, 262` |
| control block | one named COMMON group per FILE variable: `33 zero bytes, name length, name` (size 34+len), emitted after the header links, before the DATA segment | `codegen.ml:10119-10121`, `codegen.ml:10737-10752` |
| `LXI H,<CB>` | already emitted — `on_reg_prefix` does SEL-COMMON (only when the group *changes*) + a COMMON reloc at offset 0 | `codegen.ml:8864-8871` |
| lowering of the nine statements | none: the catch-all raises | `codegen.ml:10100-10103` |
| names > 6 chars | refused outright | `codegen.ml:10122-10129` |

Three defects found while establishing that, none of them codegen-semantics:

**(a) the option list is silently truncated.** `KEYED`, `DIRECT`, `PRINT`,
`PAGESIZE`, `LINESIZE` and `KEYTO` are not in `ioopt_keys`, so
`parse_io_opts` stops at the first of them and the rest of the statement is left to
be re-read as following statements. Of the 34 sampled DR `open` statements these
words appear: `PRINT` 9 times, `KEYED` 4, `PAGESIZE` 4, `LINESIZE` 2, `DIRECT` 1 —
so on 18 of 34 sites my AST holds *fewer options than DR saw*. A lowering written
against `opts` today would silently receive a truncated list. This is a P1 blocker,
not a P1 detail, and it is why section 10 asks for an accept/reject probe rather than
assuming the option grammar.

**(b) `FILE(f)` is stored as if it were an ON-unit option.** `Sput`/`Sget` keep
`stream : expr option` *and* `on_opts : io_opt list`, and `file(inf)` lands in
`on_opts`, not in `stream` (`ast.ml:100-104`). Consequence: `put file(f) list(x)`
is refused with *"PUT LIST with ON options … needs the ?OIOOP/?SIOOP file-I/O
route"* — a message that describes a condition name where there is none.

**(c) statement line numbers in diagnostics depend on the newline style.** On
CRLF text (every authentic artefact) the reported line is right; on bare-LF text it
comes out at `ceil(real/2)` — measured at 5→3, 7→4, 12→6, 22→11, 35→18. Diagnostic
only, no byte effect, but it means a `[TBD]` message from an LF file must not be
quoted as a line reference.

## 2. First blocker of each historical target

Captured in `MY-FIRST-BLOCKERS.txt` (`pli80c artefacts/<P>.PLI out.rel`, exit 2 in
every case, no `.REL` written):

| program | first refusal | what it really is |
|---|---|---|
| ENTER | `statement kind not in supported subset (line 37)` | OPEN lowering missing |
| UPDATE | `statement kind not in supported subset (line 31)` | OPEN lowering missing |
| COPY | `FILE name INPUT_FILE (10 chars) exceeds 6` | truncation rule — **now measured**, see §5 |
| RETRIEVE | `FILE name SYSPRINT (8 chars) exceeds 6` | same |
| KEYFILE | `PUT LIST with ON options (line 25)` | defect (b): really `put file(keys) list(...)` |
| REPORT | `STATIC on CHAR(15) is unsampled (line 21)` | unrelated earlier blocker |
| FSCAN, LOAN2 | `STATIC on CHAR(80)/CHAR(14) VARYING unsampled` | unrelated |
| DIOCALLS | `BASED(DBUFFV) of type CHAR(127) VARYING` | unrelated (PB6 family) |

Two ordering facts that matter when reading that table: the refusal a program
reports is not always the *first* lowering that would fail — the pool prescan calls
the PUT/GET matchers (`codegen.ml:2114`, `2118`, `2280`) before the statement loop
reaches an earlier OPEN, which is why E16D/P019B/P021 report a PUT refusal while their
OPEN is on an earlier line. And COPY/RETRIEVE never reach the OPEN at all, because
their file names exceed 6 chars — a refusal that §5 shows DR does not make.

## 3. The evidence corpus

`OPEN-INVENTORY.txt`: **2053 `.REL` files scanned** under `golden/` and
`extracted/`, 36 carry a `CHAIN-EXT` for `?OIOOP`, and those 36 files are **24
distinct objects** (SHA-256; `golden/first`, `golden/first8080u` and `golden/bind1`
hold copies of the same oracle output, and a copy is not independent evidence).

* 10 historical programs: COPYLPT, COPY, CREATE, DEPREC, ENTER, KEYFILE, LOAN2,
  REPORT, RETRIEVE, UPDATE — sources in `artefacts/`.
* 14 probe objects: E16A-E16D (`golden/e2e11h`), E17A-E17D (`golden/e2e11i`),
  E18A/E18B (`golden/e2e11j`), P019B (`golden/probes11`), P021 (`golden/probes10`),
  P072H (`golden/probe40`), P081Q (`golden/probe50`).
* **34 OPEN blocks** in the 24 distinct objects (a program has one block per OPEN
  *statement site*, not per execution: RETRIEVE's second open sits inside a
  `do while`).
* **5 CLOSE blocks** (E16D, E17D, RETRIEVE, P072H, P081Q) — `CLOSE-BLOCKS.txt`.
* 70 `?SIOOP` file attaches in 25 distinct objects — `SIOMODES.txt`.
* `?OFCOP` is chained by 18 objects. Its context in `golden/probe44/P077C` is
  `… SHLD / RET / LHLD / SHLD / CALL ?OFCOP / RET`: a procedure-exit path, **not** an
  OPEN path. None of the 34 OPEN blocks touches it. That settles the question the
  memo flagged.

## 4. How the evidence was extracted, and why the first two attempts were wrong

`openblocks.py` finds a block by *anchor*, not by source line:

1. `e41rel.replay()` replays the bit-packed `.REL` stream, keeping the RELOC record
   attached to each code byte, the CHAIN-EXT slots **with the routine name**, and the
   ordered list of named COMMON groups (record type 5 = `DEF-COMMON-SIZE`,
   1 = `SEL-COMMON`, 6 = `CHAIN-EXT`). `tools/reldump.py`'s disassembly *text* is not
   usable as input: on COPYLPT it stops at code 00E6 of 2A02 bytes, and a truncated
   byte map shortens every block decoded from it.
2. Instruction boundaries come from a linear decode over the full byte map using
   `tools/dis80.py`'s DR80 length table. Five single-byte `MOV` forms the table lacks
   (47/60/65/68/6C) decode as `DB nn`, length 1, which keeps boundaries right.
3. A `CHAIN-EXT` is anchored at the CALL's operand slot, so the CALL is at slot−1;
   the walk goes **backward over instruction starts only**.
4. The walk stops when it has six `PUSH H` — that is the block's definition — and then
   absorbs only title-prologue opcodes, ending at the `LXI H` (literal/variable title)
   or the `XRA A` (no TITLE clause). A `CALL` to anything other than `?SLCTS`/`?SLVTS`
   ends the run, which is what keeps a preceding `CALL ?START` or a preceding PUT
   sequence from being swallowed. With that rule the decoder finds **55 blocks across
   all copies (46 OPEN + 9 CLOSE)** and **39 in the 24 distinct objects (34 OPEN + 5
   CLOSE), with zero anomalies**: every OPEN block is exactly six pushed words.
5. Register state is tracked symbolically while walking, because DR does not always
   build a word with `LXI H`: `XRA A / MOV B,A / MOV H,B / MOV L,B` pushes 0x0000, and
   `MOV L,H` collapses HL to a repeated byte. Without that, four of the six words in
   the 21-byte blocks look unset.

Why the symbolic walk exists at all: in the linked `.COM` a pushed word is just a
number, and the number 0x1F40 in ENTER is the *constant* 8000 (B(8000)), not an
address. Only the `.REL` relocation stream distinguishes the two — the trap recorded
as [C264]. `bitfit.py` and `wordfit.py` then test the candidate readings of the words
against every row and print where they fail, rather than being written to agree.

The pairing of block to source statement is **by order**: the *i*-th `?OIOOP` call
site in an object is the *i*-th `OPEN` statement in the text. All 24 objects satisfy
`blocks == statements`, which is what lets the matrix carry option columns at all.

## 5. The OPEN block

Every one of the 34 blocks is this, in this order:

```
<title prologue>            6 or 5 instructions, or 4 when there is no TITLE
LXI H,<w1>  PUSH H          option word
LXI H,<w2>  PUSH H          organisation selector (only with ENVIRONMENT)
LXI H,<w3>  PUSH H          B(n) buffer size
LXI H,<w4>  PUSH H          F(n) record format size
LXI H,<w5>  PUSH H          PAGESIZE(n)
LXI H,<w6>  PUSH H          LINESIZE(n)
LXI H,<CB>                  the file's control block = offset 0 of its COMMON group
CALL ?OIOOP                 CHAIN-EXT to PLILIB
```

…except that DR reuses registers instead of re-loading: 15 of 34 blocks are 29 bytes
because the zero words come from `MOV L,H` (HL collapses to 0x0000 after a
`LXI H,0080`) and from repeated `PUSH H` rather than fresh `LXI H` pairs. Full size
histogram (from `OPEN-MATRIX.tsv`):

| bytes | n | sites |
|---|---|---|
| 21 | 3 | P072H:3, P019B:3, P081Q:3 — no title, all six words constant |
| 24 | 1 | P021:6 |
| 27 | 2 | LOAN2:56, CREATE:22 |
| 29 | 15 | the eight E16/E17/E18 input sites, LOAN2:54, DEPREC:51/78, RETRIEVE:19, P021:3, E16D:3 |
| 31 | 1 | KEYFILE:19 |
| 33 | 2 | COPYLPT:38, UPDATE:31 |
| 34 | 2 | COPYLPT:49, RETRIEVE:31 |
| 36 | 8 | COPY:10/13, KEYFILE:16, P021:4, UPDATE:34, REPORT:27/29, ENTER:37 |

The three title prologues, verbatim from the objects:

```
literal   LXI H,<string in DATA> ; MVI A,<len> ; CALL ?SLCTS ; MOV B,A ; PUSH B ; INX SP
variable  LXI H,<descriptor>                      ; CALL ?SLVTS ; MOV B,A ; PUSH B ; INX SP
absent    XRA A                                   ;               MOV B,A ; PUSH B ; INX SP
```

25 sites use `?SLCTS`, 5 use `?SLVTS` (a VARYING title — LOAN2, CREATE, COPYLPT,
RETRIEVE, KEYFILE), 4 use none. `PUSH B` pushes B then A; `INX SP` drops the low half,
so **the title reaches PLILIB as one byte on the stack**, the length, with the address
having been handed to `?SLCTS`/`?SLVTS` in HL/A. `XRA A` is the zero-length case.

CLOSE is the same block with everything removed:

```
LXI H,<CB@0 of the file's COMMON group> ; CALL ?CIOOP        (6 bytes, 5/5 witnesses)
```

Two things the objects settle that this compiler currently refuses:

* **COMMON symbol truncation.** DR names the group with the **first 6 characters** of
  the uppercased file name and stores the **full** name in the control-block bytes:
  `INPUT_FILE → /INPUT_/` (group size 44 = 34+10), `OUTPUT_FILE → /OUTPUT/` (45 =
  34+11), `SYSPRINT → /SYSPRI/`, `PRINTFILE → /PRINTF/`, `EMPFIL → /EMP/`, `F → /F/`.
  Fifteen distinct group names across the corpus, every CB at group offset **0x0000**.
  `codegen.ml:10122-10129` refuses exactly these two COPY/RETRIEVE names as
  "unmeasured"; they are now measured, and the size in the `DEF-COMMON-SIZE` record is
  computed from the *full* name, not the truncated symbol.
* **SYSIN gets a control block too**: E32E1/E34B1 both `DEF-COMMON-SIZE /SYSIN/ 39`
  (34+5), and those two programs are byte-exact specimens today, so the group layout
  this compiler emits for a FILE is already confirmed against DR for at least
  `SYSIN` and `INF`.

## 6. What the six words carry

`wordfit.py` tests the candidate below against all 34 rows: **33 agree, 0 disagree**,
and the one row that tests nothing is COPYLPT:38, whose pagesize/linesize are
variables (`LHLD <data word>` — DR loads them from storage, so the word is not in the
object).

| word | candidate meaning | witnesses |
|---|---|---|
| w1 | the packed option word (§7) | 34/34 immediate |
| w2 | organisation selector, **only with ENVIRONMENT**: STREAM 0x08, DIRECT 0x10, KEYED 0x18; 0 with no ENVIRONMENT | 0x0000 ×23, 0x0008 ×6, 0x0018 ×4, 0x0010 ×1 |
| w3 | the B(n) buffer size; 0 when no B(n) | 0 ×24, 8192 ×2, 8000 ×2, 4000 ×2, 1024 ×2, 10000 ×1, 2000 ×1 |
| w4 | the F(n) value; **128 when ENVIRONMENT is present without F(n)**; 0 with no ENVIRONMENT | 0 ×23, 0x0080 ×10, 0x0050 ×1 (P021's `f(80)`) |
| w5 | the PAGESIZE(n) literal | 0x003C in exactly one row (P021:6 `pagesize(60)`) |
| w6 | the LINESIZE(n) literal | 0x003C in exactly one row (KEYFILE:19 `linesize(60)`) |

w5/w6 rest on **one site each** — but the two sites put the same value in *different*
words, which is what fixes the assignment; no sampled statement has both options as
literals, so that combination is untested (probe E46A below). The 17 source shapes the
tested population covers are listed in `WORD-FIT.txt`; they do **not** include
`append`, `rewind`, `delete`, `record`, `keyfrom` on an open, or both of
pagesize+linesize as literals.

## 7. w1, bit by bit

15 distinct w1 values over 34 sites. `bitfit.py` asks, for every bit, whether it
separates rows that have an option from rows that do not; with two derived columns
(ORGanisation and MODE, because no single source word gives either) **every bit now
gets a clean verdict except the two constants**:

| bit | verdict (from `W1-BITFIT.txt`) |
|---|---|
| 0x0001 | clear in all 34 |
| 0x0002 | set only for `print` |
| 0x0004 | set only for KEYED and DIRECT — never STREAM |
| 0x0008 | set only for the one DIRECT row |
| 0x0010 | set for KEYED and STREAM, clear for DIRECT (one DIRECT row ⇒ cannot be separated from "not update") |
| 0x0020 | set only for the one `direct update` row |
| 0x0040 | set for OUTPUT and PRINT, never INPUT |
| 0x0080 | set for INPUT only |
| 0x0100 | set for KEYED and DIRECT |
| 0x0200 | set for STREAM |
| 0x0400 | **set in all 34** |
| 0x0800 | set exactly when a TITLE clause is present (29 rows; 4 titleless rows clear it) |
| 0x1000 | set exactly when LINESIZE is present (literal *or* variable — COPYLPT's `linesize(pagewidth)` sets it) |
| 0x2000 | set exactly when PAGESIZE is present |
| 0x4000 | set exactly when ENVIRONMENT is present |
| 0x8000 | clear in all 34 |

Two confounds to keep out of any claim: 0x0004/0x0100 correlate with "F is present"
only because in this corpus every F-bearing file is keyed or direct, and 0x0020 with
"update" only because UPDATE is the single direct file. The low nibble 0x90 / 0x50 /
0x52 / 0x94 / 0x54 / 0x2C is where organisation and mode live together, and no sample
separates bit 2 from bit 4 except the one DIRECT row.

## 8. The neighbouring route: `?SIOOP`, and the mode word

`SIOMODES.txt` lists all 70 file attaches. The preamble is uniform:

```
LXI H,<CB>            ; LXI D,<mode>        ; LXI B,<next statement>   ; CALL ?SIOOP
```

and the chain that follows it is **the same conversion code this compiler already
emits for console I/O**: `?GNVOP ?QCIOP ?QIOOP` (19 attaches, fixed-bin get),
`?SLCTS ?PNCOP ?QIOOP` (4, character put), `?EDITF …` (16, edit put), `?SSVFS` (3,
varying get), `?WNIOP ?QIOOP` (4, `write … from`), `?KEYTO ?RNIOP` (1, keyed read).
Console and file differ in exactly two ways in these objects: the console attaches
(`?SYSPR`, `?SYSIN`) load no HL and call the console routine, and their DE words are
0x0252/0x0290 — the file words 0x0652/0x0690 **minus 0x0400**.

The tempting rule "`DE` = the file's OPEN w1 with the OPEN-only bits cleared" is
**false**: it holds for 38 of 68 attaches that can be matched to an open, and fails on
30, always in the same direction — the attach clears 0x1000/0x2000 (linesize,
pagesize), sometimes clears 0x0004 (KEYFILE's keyed input open → 0x0594 keyed attach,
but REPORT's same-keyed file → 0x0590 for its sequential read), and sets/clears 0x0002
and 0x0040/0x0080 according to **what this operation is** (`put list` → 0x0652, raw
`write … from` → 0x0650, `get` → 0x0690), not what the file was opened as. UPDATE's
two attaches on the same direct file are 0x058C (read) and 0x054C (rewrite). So the
attach word is a per-statement mode word sharing w1's vocabulary: it must be computed
from the statement, and any P1 claim about it needs the statement-side samples.

## 9. Candidate first slices, evaluated

| | A: named **stream** open + close + `get`/`put file(f) list` | B: **KEYED output** (ENTER) | C: **DIRECT update** (UPDATE) |
|---|---|---|---|
| DR objects already in repo | 14 (E16A-E18B, P072H, P081Q, P021) + COPY/CREATE/DEPREC/LOAN2/RETRIEVE/COPYLPT/REPORT | ENTER only | UPDATE only |
| OPEN sites covered | **29 of the 34 sites are stream opens**, carrying 12 of the 15 distinct w1 values — titleless, literal-title, variable-title, print, ENVIRONMENT-with-B-only | 0x4D54, 0x4D94 (3 sites, 2 programs) | 0x4D2C (1 site) |
| new PLILIB names to chain | `?OIOOP`, `?CIOOP`, `?SIOOP` only | + `?WNIOP`, `?QCDOP`, `?EDITF` edit-to-file | + `?WNIOP`, `?RNIOP`/`?KEYTO`, `?QCDOP` |
| already-implemented half | the entire item chain (`?GNVOP/?QCIOP/?SSVFS/?SLCTS/?PNCOP/?QIOOP`, the deferred `LXI B` continuation triple) — only the 3-instruction preamble changes | ENTER's PUT/GET with edit + `STATIC INITIAL` + keyed read, all unmeasured | REWRITE/UPDATE statements, keyed read, `locate`; the direct mode words 0x058C/0x054C have one witness each |
| runtime validation | **already demonstrated in this repo**: `golden/e2e11iu/E17{A,B,C}.output.txt` and `golden/e2e11jr/E18{A,B}.output.txt` are DR runs that read a staged `INF.DAT`, and `golden/e2e11iu/E17D/OUT.DAT` is the file DR's own open/put/close wrote | ENTER is interactive; its staged run in `golden/run1` stops at `UNDEFINED FILE (1), File: EMP=NUL` | needs a file in DR's keyed/direct on-disk format, plus a second run to see the update land |
| other blockers in the way | none for E16C/E16D/E17B/E17D/E18A/P072H/P081Q/P021; E16A/E17A need the ON-`begin…end` handler ("procedure without name"); P019B needs `lineno`/`pageno` | STATIC initial, ON units, keyed read | STATIC initial, keyed/direct read+rewrite |
| risk | low: byte-exact against 14 objects already in the repo; the runtime question is already answered by DR's own transcripts | high: ENTER is the only witness for its w1 and its whole keyed-PUT path is unmeasured | highest: one witness per word value, and the direct/update bits (0x08/0x20) cannot be separated from `update` at all |

**Recommendation: slice A**, and inside it the order (1) `open`+`close` for a
titleless stream file — P081Q (13 instructions, `?OIOOP ?SIOOP ?GNVOP ?QCIOP ?QIOOP
?CIOOP ?START ?STOPX`, no console output at all), then (2) P072H (adds a VARYING get
`?SSVFS`), then (3) E16C/E18A (title + repeated get), then (4) E16D/E17D (a
`put file(f)` output stream), then (5) P021 (three opens, keyed+environment and
pagesize — compile-only byte-exact). Registered as byte-exact specimens against the
`.REL` already in `golden/`, and 2-3 of them as runtime rows using the existing
`STAGE_IN`. Section 10's E46A/E46B/E46C are needed before §6's w5/w6 and §1's option
vocabulary can be stated as claims, but none of them blocks steps 1-5.

## 10. Minimum missing oracle probes

Six one-statement-or-two programs; none is covered by the 34 sampled sites or by the
runs in `golden/`, and each settles something a claim would otherwise guess at.

1. **E46A — `open file(f) stream output pagesize(24) linesize(80) title('$1.$1');`**
   both page/line sizes as literals in one statement. Settles w5/w6 for real (§6 rests
   on one row each) and whether bit12/bit13 both survive in w1 alongside TITLE.
2. **E46B — `open file(f) append title('$1.$1');`** `append` is parsed today and has
   **zero** samples anywhere in the corpus; nothing says which bit it is, or whether
   it reuses the output bits.
3. **E46C — `open file(f);`** (no option at all) and **`open file(f) direct input
   environment(b(2048));`**. The first: does DR still push six words, and what is w1
   with neither organisation nor mode (all 34 samples name at least one). The second:
   DIRECT without UPDATE — the only DIRECT witness is `update`, which is why bits
   0x08/0x20/0x10 cannot be separated today.
4. **E46D — `dcl abcdefgh file; open file(abcdefgh) stream input;`** with a
   7/8-character name, run and inspected with `LINK`. The truncation rule in §5 is
   read off 15 group names, all of which are consistent with `name[0:6]`; this probe
   distinguishes truncation at 6 from "first 6 up to a non-alphanumeric" and shows
   whether a *colliding* truncated pair (`abcdef1`, `abcdef2`) is diagnosed, which is
   what makes the rule safe to implement.
5. **E46F — `dcl f file; open file(f) stream input title('DATAIN TXT');`** run with
   `DATAIN.TXT` staged, plus a twin using `title('$1.$1')` with the same tail.
   `golden/run1/COPY.output.txt` asks PLILIB for `INPUT_FILE` — the variable's full
   10-character name — while `golden/e2e11hr/E16C.output.txt` asks for `INF` despite
   `title('E16IN DAT')`. A literal title demonstrably did *not* name E16C's file, and
   no sample shows one ever doing so. Until this runs, no runtime row may use a literal
   title, and how a CB name becomes an FCB stays unread.
6. **E46E — `open file(f) keyed update environment(f(64),b(512)) keyfrom(...)`** —
   the `keyed`+`update` and `keyfrom`-at-open combinations, and (same object, second
   statement) a `read … keyto`/`rewrite` pair so the keyed write/rewrite mode words
   stop being single-witness.

## 11. Runtime: DR has already opened, read and written a file in this repo

Three things the runs settle, all measured rather than assumed (`oracle/linkrun.py`
carries the staging: `STAGE_IN`, `ARGS`, `EXPORT_OUT`):

* **A `$1` title names the file from the command tail.** `E17A/E17B/E17C` and
  `E18A/E18B` (all `title('$1.$1')`) were run with tail `INF.DAT` against a staged
  `INF.DAT` and produced real output: `X=         7 X=         8 X=         9 X=
  9 DONE`, `X=         7 REACHED SECOND`. A stream input file works end to end in the
  harness today.
* **`$2` names the output file, and F sizes the record.** E17D opens
  `outf … environment(f(128),b(8000)) title('$2.$2')`, does two `put file(outf)` and a
  `close`; with tail `OUT.DAT` it printed `WROTE` and left
  `golden/e2e11iu/E17D/OUT.DAT` — **exactly 128 bytes**, `'HELLO'        42` padded
  with `0x1A`. One 128-byte record: independent corroboration of §6's `w4 = F(n)`, and
  of `CLOSE` flushing.
* **A literal title did not name a file in any run here, and the tail splits at a
  space.** The `E16x` runs (`title('E16IN DAT')`) all fail as `UNDEFINED FILE (1),
  File: INF=NUL` — PLILIB asked for the FILE variable's own name. `ARGS` records that
  `'E17D OUT DAT'` created a file literally named `out` with no extension and that
  `'INF DAT'` found nothing, so a single dotted token is the staging form. All five
  historical file programs in `golden/run1` (COPY, ENTER, KEYFILE, REPORT, UPDATE) end
  the same way, each followed by a `Traceback:` line — the [E2E-33] mechanism, whose
  words still need a PLILIB load map to decode (COPY's traceback carries `# 4E90 …`, a
  mode word; ENTER's carries `EMP` and `$1` fragments).

Consequence for slice selection: steps 3-5 of §9 can be runtime rows, not only
byte-exact rows, with no new oracle capability. What runtime cannot do here is keyed or
direct organisation — nothing in the repo has ever read a DR-keyed file — which is the
other reason §9 rates slices B and C as high-risk.

## 12. What P0 does **not** establish

* Nothing about `read`/`write`/`rewrite`/`update`/`locate`/`keyfrom`/`keyto`
  *statement* lowering — I decoded call windows for `?WNIOP`, `?RNIOP`, `?KEYTO`,
  `?PAGOP` but did not attempt to reduce them to a rule; `IOWINDOWS.txt` is the raw
  material.
* Whether `?OIOOP`'s six words are *arguments* in the order they are pushed or a
  structure PLILIB indexes by offset. The stack depth at the CALL is
  −13 bytes (12 + the title byte) and HL carries the CB, which is consistent with
  either; only a PLILIB disassembly would say, and I have not touched it.
* The meaning of bits 0x0001/0x0400/0x8000 beyond "constant in this population";
  0x0400 is set in every OPEN and cleared in every console attach, which is a
  suggestive *external-file* reading with 34+70 witnesses and no counterexample —
  and still a candidate.
* Whether the organisation selector in w2 is what PLILIB uses for record handling, or
  merely a mirror of w1's organisation bits.
* How a control block's stored name becomes a CP/M FCB: §11 shows the variable's *full*
  name (`INPUT_FILE`, 10 characters) being searched, which cannot fit an 8+3 FCB, and
  whether a literal TITLE is ever used as an external name at all.
* Anything about `INTERNAL` files, `RECORD`/`PREAMBLE` options, `CREATE`/`REWIND`/
  `DELETE` statements, or the `?SIOOP` `LXI B` continuation in the presence of an
  ON-unit whose handler is in another block.
* That slice A is *correct* — it is cheap and byte-exact-checkable, which is a
  different statement.

## 13. Files

```
spec/lab-evidence/e2e41-p0/
  e41rel.py             .REL bitstream replay: code bytes, per-byte RELOC, CHAIN-EXT
                        names, named COMMON group layout; also the PRN line->address
                        and LINK-map readers used by the earlier scripts
  openblocks.py         the block decoder (OPEN; --routines=?CIOOP for CLOSE)
  openmatrix.py         OPEN-INVENTORY.txt (dedup by SHA) + OPEN-MATRIX.tsv (34x28)
  bitfit.py             per-bit discrimination test for w1          -> W1-BITFIT.txt
  wordfit.py            per-row test of the w2..w6 candidate        -> WORD-FIT.txt
  iowindows.py          code around every I/O CALL in the 10 historical programs
  siomodes.py           all 70 ?SIOOP attaches, their DE word and the file's OPEN w1
  OPEN-BLOCKS.txt       the 34 blocks, decoded and disassembled
  CLOSE-BLOCKS.txt      the 5 CLOSE blocks
  OPEN-MATRIX.tsv       one row per OPEN site with source-derived option columns
  OPEN-MATRIX-ROWS.txt  the same, human-readable
  OPEN-INVENTORY.txt    24 distinct objects / 36 copies, with SHA-256 prefixes
  W1-BITFIT.txt  WORD-FIT.txt  IOWINDOWS.txt  SIOMODES.txt
  MY-FIRST-BLOCKERS.txt this compiler's first refusal on each target
```

Regenerate all of it with (from the repo root):

```
python3 spec/lab-evidence/e2e41-p0/openblocks.py    > spec/lab-evidence/e2e41-p0/OPEN-BLOCKS.txt
python3 spec/lab-evidence/e2e41-p0/openblocks.py --routines=?CIOOP > \
       spec/lab-evidence/e2e41-p0/CLOSE-BLOCKS.txt
python3 spec/lab-evidence/e2e41-p0/openmatrix.py    > spec/lab-evidence/e2e41-p0/OPEN-MATRIX-ROWS.txt
python3 spec/lab-evidence/e2e41-p0/bitfit.py        > spec/lab-evidence/e2e41-p0/W1-BITFIT.txt
python3 spec/lab-evidence/e2e41-p0/wordfit.py       > spec/lab-evidence/e2e41-p0/WORD-FIT.txt
python3 spec/lab-evidence/e2e41-p0/iowindows.py     > spec/lab-evidence/e2e41-p0/IOWINDOWS.txt
python3 spec/lab-evidence/e2e41-p0/siomodes.py      > spec/lab-evidence/e2e41-p0/SIOMODES.txt
```
