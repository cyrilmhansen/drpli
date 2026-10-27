# E2E-41/P3 — the stream OUTPUT open, the named-file PUT LIST, and the withdrawal of a false explanation

Phase P3 of E2E-41.  Starting HEAD `42f297e6cdc4cf8bf5b8d8ef8a4846c460ad38f0` (E2E-41/P2b).
Two commits:

* **P3a** `E2E-41/P3a: correct TITLE census and withdraw unsupported OUT.DAT cause` — a
  documentation, census and coverage change only; no lowering moved [C279].
* **P3b** — the lowering: `OPEN FILE(f) STREAM OUTPUT TITLE('<literal>')` and
  `PUT FILE(f) LIST(<literal>)`, byte-exact against **E16D.REL** and **E17D.REL**, plus the
  first runtime row this project has ever written that asserts the bytes of a file the compiled
  program created.

P3 is the end of E2E-41 as scoped: ENTER/UPDATE (record I/O, KEYED, `READ ... KEY`) are left for
the next episode, and nothing here touches them.

## 1. P3a — two documents were wrong and said so confidently

**(a) The TITLE census was 29, and is 30.**  `spec/PERIMETER.md` carried "30 of 34 rows carry it
(25 literal + **4** variable titles)" while the note and the coverage row both said **29**.  The
matrix is the authority, not either prose file: recounting
`spec/lab-evidence/e2e41-p0/OPEN-MATRIX.tsv` row by row gives **25 literal + 5 variable = 30**
sites with a TITLE and **4** without (P072H:3, P081Q:3, P019B:3, P021:6), and 25 + 5 + 4 = 34 ✓.
The recomputation, the per-site list and the row count are in
`spec/lab-evidence/e2e41-p3/TITLE-CENSUS.txt`; [C279] records the correction; the `0x0800`
conclusion it supports is unchanged because that bit is set in every one of the 30.

**(b) E17D's 128-byte OUT.DAT was attributed to a clause E17D does not have.**  P0 §8 of the
reconnaissance note, and the `E41X5` inventory row after it, explained the 128 bytes as "the
record size its `ENVIRONMENT F(128)' asks for".  `e13src/E17D.PLI` has **no ENVIRONMENT clause**,
so there is no `F(128)` in the program [C279].  What is actually established:

* `golden/e2e11iu/E17D/OUT.DAT` is exactly 128 bytes: 13 payload bytes
  `27 48 45 4C 4C 4F 27 20 20 20 20 34 32` — `'HELLO'` (quotes included), four spaces, `42` —
  followed by 115 `0x1A`.
* Every one of E17D's five words after w1 is `0x0000` — including w6, the record-length word.
  Recounting the whole matrix (`OPEN-MATRIX.tsv`, 34 rows): w6 is the immediate `0x0000` in **32**
  rows, and the only two exceptions are KEYFILE:19 `linesize(60)` → `0x003C` and COPYLPT:38, whose
  sixth word is a DATA reference rather than an immediate.  So nothing in E17D's OPEN asks for
  128 of anything.
* What DR writes at OPEN into the 38-byte control block (`LINK-DEF-COMMON-SIZE abs 0026 OUTF`),
  and which of those bytes CP/M's `F_CLOSE`/`F_CREATE` uses to pad the last record, has **never
  been traced**.  So CP/M's own record padding is a *hypothesis*, and it is recorded as one.  The
  measurement — 128 bytes, `0x1A` tail — is in
  `spec/lab-evidence/e2e41-p3/E17D-OUT-DAT.txt`; the withdrawal is [C279].

## 2. What P3b lowers, and the words it is built from

### 2.1 `OPEN FILE(f) STREAM OUTPUT TITLE('<literal>')`  —  w1 = 0x0E50

Nine rows of `OPEN-MATRIX.tsv` are opens of a stream OUTPUT.  Two of them are compiled by this
repository byte-exactly (E16D:3, E17D:3); the other seven are keyed (P021:4, ENTER:37 → 0x4D54),
print (LOAN2:54/56 → 0x2E52/0x0E52), carry an attribute (COPY:13 ENVIRONMENT → 0x4E50, KEYFILE:19
LINESIZE → 0x1E50) or take a VARIABLE title (CREATE:22).  **CREATE's w1 is 0x0E50, exactly
E16D/E17D's**: the mode word does not care how the TITLE is spelled, only that one is present.
Every one of the nine carries a TITLE — seven literal, two variable (`CREATE:22`, `LOAN2:56`).
That is as far as the nine go: four of them spell `output` with NO `stream` keyword (the two keyed
rows and the two print rows), so the corpus does not support "OUTPUT is accepted only as
`stream output` with a literal TITLE"; it supports "this compiler lowers exactly one of the nine
spellings".  The measured word is

```
0x0E50 = 0x0400 declared file | 0x0200 stream organisation | 0x0010 stream | 0x0040 OUTPUT
         | 0x0800 TITLE present
```

which is the input open's `0x0E90` with the input bit `0x0080` **replaced** by the output bit
`0x0040` — not added to it.  The cleanest witness is the cross-program comparison at the end of
`P3b-MEASURE.txt`: E17D's OPEN block and E17B's (`open file(inf) stream title('$1.$1')`, same
title, same 29 bytes, same position `0006-0022` in both objects) differ at **exactly one
address** — `0012: 50 (E17D) vs 90 (E17B)` — and nothing else moves, **w6 = 0000 included**.  A
stream OUTPUT open therefore carries no record length, which is exactly the fact section 1 needed
before anyone could explain a 128-byte file.

`open_mode_word` accepts `OUTPUT` only under the shapes the corpus measures and refuses the rest
by name.  The three refusals are compositions, not inventions, and each says which measured word
it would have had to emit:

* `input output` on one open — **no measured row spells it** (the matrix has 34 opens; none sets
  both mode bits).
* `output` without `stream` — the only non-stream OUTPUT rows are keyed (`P021:4`, `ENTER:37` →
  0x4D54) or print (`LOAN2:54/56` → 0x2E52/0x0E52), so a bare `output title(...)` has no witness.
  DR compiles all four of those rows, so this refusal is about the *bare* spelling and about this
  compiler having no lowering for the KEYED/PRINT attribute words — it is not evidence that DR
  rejects `output` without `stream`, and the refusal message's "outside that set" phrasing
  overstates the rows it goes on to list.
* a **titleless** `stream output` — the word it composes to is `0x0400|0x0200|0x0010|0x0040 =
  0x0650`, and 0x0650 appears in this census **only as a write-from ATTACH word** (COPY 006F,
  REPORT 00DF/01BE, all three `?WNIOP`/`?QIOOP`) and never as an OPEN w1.  The titleless opens
  that ARE measured are P019B's `open file(pf) print` (w1 = 0x0652) and P072H/P081Q's
  `open file(f) input` (0x0690) — neither is an OUTPUT.

`lower_open` records the file group in `st.file_out` **after** `open_mode_word` has accepted the
combination, so a refused OPEN claims nothing.

### 2.2 `PUT FILE(f) LIST(<one literal>)` — attach 0x0652, `CALL ?SIOOP`

`spec/lab-evidence/e2e41-p0/SIOMODES.txt` tabulates **70** `?SIOOP` attach sites, 36 of which carry
DE = **0x0652** (26 carry 0x0690, 3 carry 0x0650, 5 are keyed-file attaches at 0x054C/0x0550/
0x058C/0x0590/0x0594).  An earlier draft of this note, of C280 and of the refusal message said
"36 attach sites", which counts the 0x0652 family and calls it the file.  E16D and E17D each have
two, both at HL = the file's control block and DE = **0x0652**:

```
program   call   HL file   DE       same file OPEN w1   routines after the attach
E16D      002C   OUTF      0x0652   0E50                ?SLCTS ?PNCOP ?QIOOP
E16D      0046   OUTF      0x0652   0E50                ?DLDOP ...
E17D      002C   OUTF      0x0652   0E50                ?SLCTS ?PNCOP ?QIOOP
E17D      0046   OUTF      0x0652   0E50                ?DLDOP ...
P019B     006C   PF        0x0652   0652                ?SLCTS ?PNCOP ?QIOOP
```

and the attach block itself is the four instructions

```
LXI H,<file control block> ; LXI D,0652 ; LXI B,0000 ; CALL ?SIOOP
```

**0x0652 is 0x0252 plus the declared-file bit, and nothing more is claimed about it.**  The
console PUT attaches with `LXI D,0252 / CALL ?SYSPR`; the file PUT attaches with `LXI D,0652 /
CALL ?SIOOP`, and `0x0252 + 0x0400 = 0x0652` exactly as `0x0290 + 0x0400 = 0x0690` for the GET
[C274].  A first draft of this note decomposed 0x0652 as `0x0400|0x0200|0x0010|0x0040` — that
sums to **0x0650**, so the reading was wrong by the `0x0002` bit the attach word actually
carries.  P0 §3 fits `0x0002` to PRINT *in OPEN words* (0x0652, 0x0E52, 0x2E52 are all print
opens), but E16D/E17D attach 0x0652 on a stream-OUTPUT file and none of the 26 measured GET
attaches (0x0290 console / 0x0690 file) has the bit.  The pairing that IS measured, across all 70
?SIOOP sites in `SIOMODES.txt`:

| attach word | sites | statement |
|---|---|---|
| `0x0652` | 36 | `put file(f) list(...)` |
| `0x0690` | 26 | `get file(f) list(...)` |
| `0x0650` | 3  | record `write` (COPY 006F, REPORT 00DF/01BE, all `?WNIOP`) |
| `0x0590` | 1 | REPORT 007F's read of a KEYED file (`?RNIOP`) |
| `0x0594` | 1 | KEYFILE 0052's keyed read (`?KEYTO ?RNIOP`) |
| `0x0550` | 1 | ENTER 00E4's record write (`?WNIOP`) |
| `0x058C`, `0x054C` | 2 | UPDATE 014E/027D, both followed by `?IM22N` (its REWRITE and DELETE) |

`0x0650` is `0x0652` minus exactly the `0x0002` bit, so within attach words that bit separates
`put list` from `write` and from `get`; and the keyed/direct family (0x0590, 0x0594, 0x0550, 0x058C,
0x054C) replaces `0x0200` with `0x0100` and varies the low nibble (`0x10` stream, `0x0C`, `0x04`) —
statements none of this compiler lowers.  Nothing here is *explained*; it is tabulated.  The PRINT
correlation P0 §3 fitted to `0x0002` belongs to OPEN words, and what the bit means inside DR's
attach path is unmeasured [C280(b)].

**The two PUTs in each program take different item chains, and that is the point of using both:**

```
list('HELLO')   LXI H,pool ; MVI A,05 ; CALL ?SLCTS ; CALL ?PNCOP ; CALL ?QIOOP
list(42)        LXI H,pool ; MVI A,02 ; CALL ?DLDOP
                MVI A,05 ; MVI B,00 ; CALL ?QDCOP ; CALL ?PNVOP ; CALL ?QIOOP
```

The first is a string: the length in `A` is the literal's byte count.  The second is packed
decimal: `?DLDOP` at the digit count of the literal's *text*, then `?QDCOP` at digits+3 with
scale 0, then the editor `?PNVOP` — the same pair the DEC variable items use [C178].

`42` therefore lands in a **packed-decimal cell** (`42 00` at pool offset 0x0F in E16D, 0x0A in
E17D), on the same allocator the DEC stores use — not on the fixed-variable route.  The numeric
item is claimed only for a plain non-negative integer literal: a fraction (nonzero scale), a
signed literal (the tens-complement cell is measured for stores, never for a PUT item) and a
float spelling all refuse.

The strongest evidence that these chains are *item* behaviour rather than file behaviour is
E17D's own console `put list('WROTE')` at `0064`:

```
0064  LXI D,0252        ; console attach word
0067  LXI B,0000
006A  CALL ?SYSPR       ; console stream
006D  LXI H,*S(0011)    ; 'WROTE'
0070  MVI A,05
0072  CALL ?SLCTS
0075  CALL ?PNCOP
0078  CALL ?QIOOP
```

The item bytes are the file PUT's item bytes with nothing changed; only the prologue differs
(`0252`/`?SYSPR` against `0652`/`?SIOOP`, and the `LXI H,<control block>` that precedes it).  So
`lower_put_items_gen` stays ONE function and takes `?file : string option`: `None` is the console
prologue that every existing specimen pins, `Some f` is the file prologue.  The item arms are not
duplicated, and the 70-odd existing PUT specimens cannot drift.

### 2.3 Where the pool cells come from

E17D's DATA segment, from `spec/lab-evidence/e2e41-p3/P3b-MEASURE.txt`:

```
24 31 2E 24 31 | 48 45 4C 4C 4F | 42 00 | 57 52 4F 54 45
'$1.$1'          'HELLO'          42      'WROTE'
offset 0x00      0x05             0x0A    0x0C
```

E16D's is the same rule with a longer title (`'E16OUT DAT'` at 0x00, `'HELLO'` at 0x0A, `42` at
0x0F, `'WROTE'` at 0x11).  That is source order, which is the pool law [C152]/[C155]; the numeric
cell is deduped through `st.dec_cells` like every other DEC cell [R614], so a second `list(42)`
shares it rather than extending the pool.  DR's own listing lines agree with the images it
produced — `CODE SIZE = 007E / DATA AREA = 0016` for E16D (10+5+2+5 = 22 bytes) and
`CODE SIZE = 007E / DATA AREA = 0011` for E17D (5+5+2+5 = 17 bytes); `spec/notes/rel-format.md`
documents the `.REL` file itself as content plus zero padding to 128-byte sectors, which is why
both objects are 512 bytes on disk whatever their logical sections say.

## 3. Byte-exact, and what exactly was compared

```
$ cmp golden/e2e11h/E16D/E16D.REL /tmp/e2e41-p3b/E16D.REL   # silent
$ cmp golden/e2e11i/E17D/E17D.REL /tmp/e2e41-p3b/E17D.REL   # silent
```

512 bytes each, loader pad included — not a code-region comparison.  `P3b-MEASURE.txt`
re-regenerates that verdict from the current binary and additionally compares, window by window,
the bytes `tools/reldump.py` reads out of each `.REL` against DR's own name-resolved listing, and
the DATA segment byte images.  Every window reports `code bytes DR==mine: True`, and
`segments: ... (all equal: True)`.

**The runtime side is not console output.**  `spec/RUNTIME.txt` gained two rows with a new
assertion form, `file:<exported name>=<golden path>`, evaluated by `runtime_check` as an
exact whole-file byte comparison — no space collapsing, no CRLF normalisation, because a data
file has no such licence:

* **E17D** asserts `WROTE` on the console and `file:OUT.DAT=golden/e2e11iu/E17D/OUT.DAT`.  This
  is the first time this compiler's own object has been observed to create a file, and the
  observation is DR's archived 128 bytes against mine, all 128 including the `0x1A` fill.
* **E16D** asserts `WROTE` and `file:E16OUT=golden/e2e11iu/E17D/OUT.DAT`.  `golden/e2e11iu` holds
  E17A..E17D only, so this repository contains no DR-run artefacts for E16D at all: the expectation
  is DR's E17D file used as the byte pattern for the two items E16D writes through the same chains,
  and the row is `kind=independent`, not `dr_oracle`, precisely because it is not a DR oracle for
  E16D.  What it does prove is that my E16D object, whose bytes are DR's, creates a 128-byte file
  whose contents equal DR's 128 bytes — a cross-program check between two independently compiled
  objects, since nothing in E16D's own object could have been tuned to E17D's file.

## 4. The refusals P3b adds, and why each is a claim and not a shrug

Five shapes that *look* like they should come free with a file PUT are refused, each naming the
object that would settle it:

* **`put file(f) list(x)` — a VARIABLE item.**  The measured route is `?SLVTS`: CREATE 0165
  attaches 0x0652 and runs `?SLVTS ?PNCOP ?SLVTS`, KEYFILE 0095 runs `?SLVTS ?PNCOP`.  No
  byte-exact object of mine contains a file PUT of a variable, so the registers `?SLVTS` expects
  are unmeasured here.  Settled by: CREATE:39 (six items), KEYFILE:25 (two).  *Panel: PU1.*
* **A MULTI-ITEM file PUT.**  CREATE 0165 is exactly that — one attach, six items — but all six
  are variables, so what remains unpinned for this route is the words *between* two LITERAL
  items; E16D/E17D put one literal per statement and DR closes each attach with a single `?QIOOP`.
  Settled by: CREATE:39, which is unreachable here because its OPEN carries a variable title.
  *Panel: E41X7.*
* **`put file(f) skip list(...)`.**  Also measured — CREATE attaches 0x0652 and then runs
  `?SKPOP ?QIOOP` (01B3), `?SKPOP ?SLCTS` (01CA) and `?SKPOP ?QIOOP ?STOPX` (01E9), and its source
  has `put file(output) skip;` at lines 41 and 45 — but all of it sits behind a VARIABLE-title
  open.  Settled by: CREATE.  *Panel: E41X6.*
* **`put file(f) edit(...)`.**  DR measures it, and measures it on a stream with **no OPEN at
  all**: P086K:4 attaches 0x0652 at 001F and runs `?EDITF ?DLDOP`, and its GET attaches 0x0690 at
  0046 with `?EDITF ?EDTIV ?QCDOP`.  `golden/probe55/P086K/` holds only a `.REL` — no `.COM`, no
  transcript — so nothing here shows that program ever executed, and P086K is not in this panel.
  The shape therefore falls to the standing `PUT EDIT deferred` refusal
  ([C245]→[C250]), which the OPEN lowering neither advances nor changes.  *Panel: E41X8.*
* **A file PUT on a stream this compiler did not open for output.**  The attach itself does *not*
  require an OPEN: P086K proves that, and P019B puts the same 0x0652 behind a titleless PRINT open
  whose own w1 is 0x0652.  What is unpinned is the LIST item chain behind an attach with no
  lowered OPEN — `?SLCTS ?PNCOP ?QIOOP` after such an attach appears in no object in the census.
  So this is a refusal about what a whole object pins, not about what DR forbids.
  Settled by: a DR object of a literal-title output open plus a literal PUT — which is exactly
  what E16D/E17D became, for the opened case.  *Panel: E41X5.*

**Three probes join the negative panel: E41X6, E41X7, E41X8.**  Each opens its file exactly the
way P3b lowers it and then asks for an item route this compiler does not claim — a SKIP (E41X6),
two items (E41X7), an EDIT format list (E41X8) — so what they pin is the ITEM boundary, not the
open boundary, and each cites a real DR object in `SIOMODES.txt` (CREATE's `?SKPOP` and six-item
attach, KEYFILE's two-item attach, P086K's `?EDITF` on a stream it never opens).  The panel policy
inherited from P1 is that an entry must state a MEASURED DR verdict, so the three OPEN combinations
refused in section 2.1 are NOT panel entries: no DR object in this repository contains an
`input output` open, a non-stream non-keyed non-print OUTPUT open, or a titleless OUTPUT open.
They are documented with their exact sources and messages in
`spec/lab-evidence/e2e41-p3/REFUSALS.txt`, which is where P1/P2 put unmeasured refusals.

`PU1` (`put file(f) list(x)`) moved with this: its panel marker used to be the generic `PUT LIST
with ON options` (a wording that came from the parser recording a FILE option as an ON option),
and it now refuses one level deeper, **by item kind**, which is the true remaining gap.  The
The committed inventory is regenerated (`--update-inventory`, 990 specimen rows and 133 refusal
rows) and the census re-snapshotted:
four programs' `msg` fields change — CREATE and KEYFILE get the new PUT text, ENTER and UPDATE the
P3 subset name — and **the classification counts do not**: 15 EXACT / 26 REFUSED / 0 UNEXPECTED,
with `UNEXPECTED = 0` as the structural check that no corpus program's bytes moved.

## 5. Two harness findings, both measurements

**(a) E16D's file is `E16OUT`, with no extension.**  The harness guessed `OUTF.DAT` and
`E16OUT.DAT` and reported "no file", which was an artefact of guessing.  `p3b-e16d-run.py` runs
E16D through the harness' own `run_programs`, disables only the run-directory cleanup, and reads
the whole D: image with `cpmls`: `e16out`, 128 bytes, sha256 `56ad391f…` — the same bytes as DR's
OUT.DAT.  So the name comes from the TITLE (`'E16OUT DAT'`), not from the FILE variable `outf`
(which would have given `OUTF`), and a SPACE-separated second token did not become an extension.
DR's own LINK map inside the same run names the control-block group `/OUTF/` — so the *group*
comes from the FILE variable and the *name written into the FCB* comes from the TITLE, and those
are different strings in the same program.  Two observations, not a rule: the only other title→name
case in the repository is E17D's
`'$1.$1'` with the dotted tail `OUT.DAT`, which *did* take an extension (`oracle/linkrun.py`'s
`ARGS` comment records DR's own space-tail run leaving a file literally named `out`).  What DR
does with the remaining characters of a title is NOT established here.  `EXPORT_OUT["E16D"]` now
lists the measured name first, keeping the two absent guesses so their absence stays visible.

**(b) `oracle/cpmwork.py`'s F83 guard could not express an extensionless name.**  The pattern was

```python
r"^([A-Za-z0-9_]{1,8})(?:\.([A-Za-z0-9_]{1,3})?)$"     # the '?' is INSIDE the group
```

so the dot was mandatory and the extension optional: `re.match(..., "OUT")` → **None**,
`re.match(..., "OUT.DAT")` → a match, on Python 3.14.8.  That is a defect in the guard, not a
regex-engine quirk — the same shape fails on every version — and it made finding (a) impossible
to *export*: the guard raised before `cpmcp` ran, so a program that had demonstrably written a
file was reported as having written nothing.  CP/M's F8.3 grammar makes the whole `.EXT`
optional, so the group now wraps both the dot and the extension (`(?:\.([A-Za-z0-9_]{1,3}))?`);
`check_f83` still refuses anything outside `[A-Za-z0-9_]`, still caps 8 and 3, and still returns
the same normalised form.  Reproduction: `spec/lab-evidence/e2e41-p3/F83-REGEX.txt`.

## 6. What P3b does NOT claim

* **No record-oriented I/O.**  The record WRITE chain (`?WNIOP`) at COPY 0057/006F and REPORT
  00DF/01BE attaches with 0x0690 and 0x0650 -- words nothing here lowers -- and LOAN2's
  print-with-`?PAGOP` PUTs are PRINT opens, not OUTPUT opens.  The file PUT claimed here is
  stream-mode only, and `read file(f) ... keyto(k)` (KEYFILE 0052, attach 0x0594) is untouched.
* **No KEYED, no DIRECT, no READ, no UPDATE/ENTER.**  `RETRIEVE`, `ENTER`, `UPDATE`, `KEYFILE`,
  `LOAN2`, `REPORT`, `COPY`, `COPYLPT`, `DEPREC` remain REFUSED in the census.
* **No variable TITLE.**  The census's five variable-title opens (LOAN2:56, COPYLPT:38, CREATE:22,
  KEYFILE:19, ENTER:37 — [C278]) stay refused, and the variable-item route they lead to (`?SLVTS`,
  2 sites in SIOMODES.txt) is not lowered either.  P3b also adds no attribute word: the coverage
  row's standing boundary is that w5/w6 assignment rests on E18A and P079A alone.
* **No explanation of the 128-byte padding** beyond "observed, and not caused by any clause in
  the source" [C279].
* **Long FILE names and `PUT EDIT` on a file** are unchanged refusals.
* The attach word is taken from a file this program *opened*; nothing about DR's internal
  stream tables is claimed, and the run is evidence that the words work, not that they are
  understood.

## 7. Panel and gate after P3b

| gate | before | after |
|---|---|---|
| byte-exact specimens | 988 / 0 fail | **990 / 0 fail** (E16D, E17D) |
| negative panel | 130 / 130 | **133 / 133** (E41X5 and PU1 re-worded, none retired; E41X6/E41X7/E41X8 added) |
| divergence panel | 9 / 9 | 9 / 9 |
| runtime rows | 50 | **52** (E17D, E16D — both with file assertions) |
| census | 15 EXACT / 26 REFUSED / 0 UNEXPECTED | unchanged counts, 4 `msg` fields re-snapshotted |
| parse gate | 6 pre-existing failures | unchanged 6 (AB20, E36H13, E37A1, E39S4, LR16, PB16) |
| whole-file `cmp` | 988 silent | 990 silent — E16D.REL and E17D.REL, 512 bytes each |
| dune warnings | 70 | 66 (see the note below on why the drop is unattributed) |

The warning drop is reported without a cause: it was recounted by hand on a clean rebuild, the
four that disappeared sit in the PUT matcher's neighbourhood, and P3b did rewrite that matcher —
but no attempt was made to attribute them one by one, so the number is a measurement and not an
explanation.

**Which run produced which verdict.**  The complete gate with `--link-run --runtime` reached a
fully green verdict on this phase's codegen: 990 byte-exact / 0 fail, negatives 133/133,
divergences 9/9, runtime 52/52 with both new rows reporting `FILE OK`, inventory and census
agreeing, exit 0.  After that run finished, the only edits that landed were to prose — code
comments, this note, [C280]/[C281]/[C282], `COVERAGE.tsv`, `PERIMETER.md`, and the wording of
refusal messages whose panel *markers* are unchanged.  The compile-only arm was then re-run green
against the final binary (same 990/0, 133/133, 9/9, coverage 91 rows 0 errors 0 warnings, census
`recomputed counts match`, inventory idempotent, exit 0), and the two file rows were re-checked
through the gate's own `runtime_check` with that binary — both `FILE OK` again.  A second complete
`--link-run --runtime` run was started and stopped before its final verdict, so no claim is made
here that the final wording-only tree was link-run end to end by hand; `rune-full` on Buildbot runs
that arm on the committed revision.

Evidence written by this phase: `TITLE-CENSUS.txt`, `E17D-OUT-DAT.txt`, `P3b-MEASURE.txt`,
`E16D-RUN.txt`, `F83-REGEX.txt`, `REFUSALS.txt` (with the three `.pli` sources it quotes), and the
scripts that regenerate the middle three.
