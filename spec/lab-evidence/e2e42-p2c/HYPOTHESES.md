# E2E-42/P2c — hypotheses and PREREGISTERED predictions

Written and committed **before** the DR oracle was invoked on any P2c probe,
under the rule the [E2E-42/P2b] episode states at
`../e2e42-p2b/HYPOTHESES.md:1-6` and repeats at `PROCESS.md:12-17`.  A
prediction written after an oracle call is a transcription, and this file is
the load-bearing artefact, so `RESULTS.md`'s first section must be a
prediction-vs-verdict table over exactly these rows.

    git commit  <this commit>   -- probes/E46N*.PLI + this file
    git rev-parse HEAD          -- recorded in RESULTS.md as the prediction SHA

## What P2c is

P2c implements the `FILE` form of the `SKIP` control item, measured.  It is
the last piece of CREATE's tail: lines 41, 44 and 45 of
`artefacts/CREATE.PLI` are `put file(output) skip;`, `put file(output) skip
list('EOF');` and `put file(output) skip;`, and P2b lowered CREATE:39 but not
them, so CREATE still does not compile.  The failure is byte-level and
semantic at once: **P2a shipped a misroute** ([C300]) in which a statement
that names `FILE(f)` reached the console helper and therefore `?SYSPR`
instead of `?SIOOP`.

## The prior evidence, and what it does *not* license

Three objects carry a FILE PUT that DR attached at 0x0652, and their chains
were re-measured with `../e2e42-p2b/chaindump.py` for this episode:

| program | span | bytes | shape |
|---|---|---|---|
| `CREATE` | `01AA`–`01BD` | 20 | attach, `MVI A,01`, `?SKPOP`, `?QIOOP` |
| `CREATE` | `01C1`–`01DF` | 31 | attach, `MVI A,01`, `?SKPOP`, one `?SLCTS`+`?PNCOP` chain, `?QIOOP` |
| `CREATE` | `01E0`–`01F3` | 20 | attach, `MVI A,01`, `?SKPOP`, `?QIOOP` |
| `COPYLPT` | `0295`–`02A8` | 20 | attach, `MVI A,04`, `?SKPOP`, `?QIOOP` — counted |
| `COPYLPT` | `030C`–`0321` | 22 | attach, `LHLD`, `MOV A,L`, `?SKPOP`, `?QIOOP` — expression |
| `COPYLPT` | `0215`–`0226` | 18 | attach, `?PAGOP`, `?QIOOP` — PAGE |

What they license: a FILE `SKIP` **leads** its statement (the skip is between
the attach and the first item chain, so it is a statement option, not an
item); one attach and one close per **statement**; the count is a `MVI A,n`
operand in B and is not pushed; an expression count is loaded into A and
`?SKPOP` still runs; the bare form takes **20** bytes, not the 18 [C300]
recorded, because it is `LXI H`/`LXI D`/`LXI B`/`CALL` = 12 and not 10.

What they do **not** license: COPYLPT's counted skip and its PAGE sit behind
`open file(printfile) print title(...) pagesize(...)` — a **PRINT** open this
compiler refuses at the OPEN itself ([C289], and `KEYFILE`'s and `LOAN2`'s
refusals are OPEN-level too).  So the corpus proves DR *accepts* those
spellings on a named file but never proves it behind a `stream output` open,
which is the only file mode P2c has specimens for.  `CREATE`'s three SKIPs
**are** behind a `stream output` open, but CREATE is a corpus program and
cannot be a specimen, and DR's own `CREATE.REL` is the only object for it.
That is why `E46N9` (counted) and `E46N10` (page) exist: they ask DR the
question the corpus leaves open.

## The cost model, and its cross-checks

`predict_p2c.py` reuses the model [C296] calibrated against 32 DR objects and
adds the three control-item costs measured above.  Running it self-tests the
model against spans it was **not** fitted to — CREATE is not one of the 32
probes and COPYLPT never was — and all five agree:

    CREATE:41 bare FILE SKIP       measured  20  model  20
    CREATE:44 FILE SKIP LIST       measured  31  model  31
    COPYLPT:67 skip(4)             measured  20  model  20
    COPYLPT:81 skip(spaces)        measured  22  model  22
    COPYLPT:53 page                measured  18  model  18

Two rows are also cross-checked against MY compiler as it already stands,
because those two probes contain no FILE SKIP and so already compile:
`E46N16` I predict 96/12 and `pli80c` reports CODE 96, DATA 12; `E46N19` I
predict 81/26 and it reports 81/26.  A prediction produced by the implementation whose
outcome it is predicting is worth nothing, but these two predict DR's
numbers, and DR has not spoken yet.

## Preregistered verdicts

`accept` = DR compiles it with `NO ERROR(S) IN PASS 1` and `... IN PASS 2` and
writes a `.REL`.  `refuse` = it does not.  Sizes are the `.REL` CODE and DATA
segment lengths, the units [C296] and [C300] use.

| probe | DR verdict | CODE | DATA | the thing it decides |
|---|---|---|---|---|
| `E46N1`  | accept | 64 |  9 | the bare form in isolation; `?SYSPR` must not appear |
| `E46N2`  | accept | 75 | 10 | SKIP **before** the item chain, one close |
| `E46N3`  | accept | 73 | 30 | control item + varying operand |
| `E46N4`  | accept | 86 | 11 | control item + TWO items: still ONE attach |
| `E46N5`  | accept | 84 |  9 | two bare SKIPs do not coalesce: 20 + 20 |
| `E46N6`  | accept | 90 | 10 | output then SKIP |
| `E46N7`  | accept | 90 | 10 | SKIP then output; must be `E46N6`'s blocks swapped |
| `E46N8`  | accept | 81 |  9 | **routing**: `?SYSPR` = 1 and `?SIOOP` = 1 in one object |
| `E46N9`  | accept | 64 |  9 | counted skip behind a `stream output` open |
| `E46N10` | accept | 62 |  9 | FILE PAGE behind a `stream output` open (`?PAGOP` = 1) |
| `E46N11` | accept | 116 | 12 | runtime item/skip/item |
| `E46N12` | accept | 90 | 11 | runtime skip before any output |
| `E46N13` | accept | 75 | 13 | runtime `skip list('EOF')`, CREATE:44's own shape |
| `E46N14` | accept | 156 | 12 | runtime three successive skips |
| `E46N15` | accept | 162 | 20 | runtime routing: `?SYSPR` PUT either side of a file skip |
| `E46N16` | accept | 96 | 12 | runtime CONTROL, no skip; payload predicted exactly below |
| `E46N17` | accept | 193 | 124 | CREATE:39–45 spelled with a literal title |
| `E46N18` | accept | 72 | 12 | expression skip count, `LHLD`/`MOV A,L` |
| `E46N19` | accept | 81 | 26 | protocol control, strict CRLF |
| `E46N20` | **see below** | — | — | protocol discriminator |

Every one of `E46N1`–`E46N18`, `E46N19` is predicted **accept**, and that is
itself a real risk: [C293] established that DR rejects a control item
**inside** a `LIST` (`E46M45`, `E46M46`) and I am putting a control item
**ahead of** one.  If DR refuses `E46N2`–`E46N4` then the shape CREATE
carries is not reachable in `LIST` position and the whole sub-phase's premise
collapses — and CREATE:44 is the counter-evidence to that, so the prediction
stands.

## `E46N20`, and why it contradicts [C303] before DR has voted

[C303] (`../../CLAIMS.md`) says **"DR refuses LF outright"** and backs it with
E46M33-vs-E46M36 as "the control that isolates the terminator".  The artifacts
in this repository do not support that reading, and I found it while writing
this bank:

* `probes/E46M33.PLI` **as committed and as ACCEPTED** (`golden/e42p2b5`, the
  call whose verdict [C303] cites) has **8 bare-LF body lines and one CRLF** —
  its last.  And `golden/e42p2b5/E46M33/E46M33.PRN` lists all nine source
  lines with **correct numbers** and puts its `SYNTAX ?` at `7 c`, the
  duplicated-`FILE` statement.  DR read a bare-LF body and counted its lines.
* `probes/E46M36.PLI` — the one that died of `UNEXPECTED EOF` with **no
  listing** — differs from it in having **no CR on the last line** before the
  `^Z`.
* It has a second defect: its line 1 is `E46M35:`, not `E46N`… `E46M36:`.  The
  episode's own "differ ONLY in the terminator" is not true of those two
  files.
* And `probes/E46D4`–`E46D7` carry 3–6 bare-LF body lines each and
  `golden/e42p1b` has a `.REL` for all four, and `E46E1`–`E46E4` carry one
  bare LF each with `E46E4` producing a `.REL`.

So the variable [C303] named is the wrong one, and it matters to *me*: if bare
LF anywhere were fatal, this whole bank would be fine (it is strict CRLF), but
the reason would be wrong, and a future episode would write a probe on the
wrong rule.  `E46N20` is the isolated test: the same program as `E46N19`,
byte-identical except that every line ending is a bare LF, **including the
last**, then `0x1A`.

Prediction: `E46N20` is **refused**.  Which refusal is not predicted — the
two candidates are DR's `UNEXPECTED EOF` (consistent with [C303]'s "LF
anywhere") or a pass-1/pass-2 diagnostic with a listing (which would mean
DR's reader tolerates LF and [C303] is wrong about the *mechanism*, not just
the wording).  If `E46N20` is *accepted*, the last-line CR was what mattered
and [C303] must be corrected.

Independently, and measured **without** DR: my own lexer counts lines on `CR`
and on a bare `LF` only when `col > 1` (`../../../ocaml/lib/lexer.ml:21-24`),
and on a bare-LF source it **disagrees with DR's listing**: `E46M33`'s
duplicated-`FILE` statement is line 7 and DR numbers it 7, while this
compiler reports `(line 4)`.  That is a defect in *my* line counting, not in
DR, and it is why every probe in this bank is strict CRLF: a `[TBD]` line
number I assert in `NEG_META` has to be the one DR's listing gives.

## Runtime predictions, and the one number that is deliberately not predicted

`E46N16`'s exported file is predicted **exactly**, because [C295] and [C299]
between them settle the whole payload: a character item on a file is
apostrophe-**quoted**, items take **one blank** between them across statement
boundaries, and a `PUT` **never** terminates its line.  Two one-item
statements, no skip:

    N16OUT  =  'A' 'B'        =  37 27 41 27 20 27 42 27   =  7 bytes

`E46N11` is `E46N16` with one `put file(outf) skip;` between the two
statements and nothing else changed.  So **the byte-length difference between
the two exported files is the size of what one FILE SKIP writes**, and the
difference in their content **at the point where they diverge** is those
bytes.  Nothing about that inference needs a guess about CR, LF, spaces or
record padding, which is the point: the mission forbids guessing, and the pair
makes guessing unnecessary.

Predicted for the pair, and nothing more:

* `N11OUT` and `N16OUT` share their first 3 bytes (`'A'` quoted).
* They first differ at offset 3.
* `N11OUT`'s `B` item still appears, apostrophe-quoted, somewhere after that.
* `N14OUT` has THREE skips in the same gap as `N11OUT`'s one, so
  `len(N14) - len(N16)` is three times the unit and `len(N11) - len(N16)` is
  one unit: `len(N14) - len(N16) == 3 * (len(N11) - len(N16))` is a real
  prediction even with the unit unknown, and it fails if the runtime coalesces.

`UNKNOWN`, explicitly, and not predicted because nothing measures it: the
identity of the terminator bytes; whether the skip writes **before** the
first item in `E46N12` (a skip at position 0) or moves nothing; whether the
item-separating blank survives on either side of a skip, i.e. whether
`E46N11`'s payload is `'A'`+skip+`'B'` or `'A'`+skip+blank+`'B'`.  `E46N13`
tests the third of those from the other side because its skip and its item
are inside **one** statement, so there is no statement boundary to separate
them.

`E46N15` is the destination test and its prediction is qualitative and sharp:
the console transcript must contain the two strings `CON` and `AGAIN` and
**must not** contain `A`, `B` or `EOF`, while `N15OUT` must contain the quoted
`A` and `B`.  If the misroute survives into the implementation, the console
transcript grows whatever a `?SKPOP` writes on the console — [C298] measured
that as one CRLF — and the file loses it.

`E46N8` is the same question at the byte level and it is the strictest guard
in the bank: one object, `?SYSPR` reached by exactly the console statement and
`?SIOOP` by exactly the file statement, and no `?SYSPR` on the path from the
`LXI D,0652` attach.

## What P2c does NOT claim, and what stays refused

`PAGE`, `LINE`, `AFTER`, `BEFORE` stay refused on the named-file route.
`E46N10`, `E46N21`, `E46N22`, `E46N23` ask DR anyway, because a refusal I have
never shown DR to accept is my perimeter, not a DR gap.  Note the refusals
are at **two different stages**: `PAGE`/`LINE` parse (they are in
`ctl_keys`, `../../../ocaml/lib/parser.ml:134`) and die in `file_items`,
while `AFTER`/`BEFORE` die in the **parser** with `PUT: expected
LIST/EDIT/ITEM/FROM` — measured before this bank was written.  A negative that
fails at a different stage from its neighbours must be recorded at the stage
where it actually fails, and `NEG_META` prose saying "refuses in
`file_items`" for all four would be false for two of them.

Also refused, unchanged: keyed-file PUT (`LOAN2`, `KEYFILE`), `ON` options
(`E46M10`), the `EDIT`/`ITEM`/`FROM` kinds (`E46M8`, `E46M9`, `E46M26`),
`$LINESIZE`/`$PAGESIZE` (`E46M3`).

## The claim this episode must settle before it can extend anything

CREATE is **not** byte-exact today: its OPEN is a 27-byte varying-title call
against my 29-byte literal-title one, because CREATE:22 spells
`title(filename)` with a `char(80) varying` and [C288]'s 32-probe
calibration covers only literal titles.  So a claim of the form
"CREATE:39–45 is now byte-exact" is **false** unless the whole object
compares equal, and `RESULTS.md` must state which of the two it achieved.
`E46N17` is written to be the witness that does not need CREATE's own bytes:
the six-item list plus the three SKIP statements, with a literal title.

---

## Addendum, written AFTER DR voted — the table above is unchanged

**This section is appended, not edited into the predictions.**  The 23 rows above are the record
DR was invoked against and they stand as written, including the four DR-verdict predictions that
were wrong; if a reader wants the hit/miss score it is `RESULTS.md` §1.  What follows is only the
pointer, because a pre-registration that quietly corrects itself is not a pre-registration.

Ordering, re-checkable without trusting this file:

```
$ git diff de6ff2f HEAD -- spec/lab-evidence/e2e42-p2c/HYPOTHESES.md   # only this addendum
$ git show de6ff2f:spec/lab-evidence/e2e42-p2c/HYPOTHESES.md | sha256sum  # the blob DR was run against
```

What DR answered, in one line each:

* `E46N1`–`E46N9`, `E46N11`–`E46N19`: **accept**, and 18 of 19 pre-registered CODE/DATA sizes HIT;
  the single miss is `E46N10`'s DATA (predicted 9, DR 10), caused by a ten-character title typed as
  nine, not by the cost model — `RESULTS.md` §2.
* `E46N10` **accepted** as predicted, so `?PAGOP` is a measured DR shape and a refusal of MINE.
* `E46N21` (`line(2)`), `E46N22` (`after(2)`), `E46N23` (`before(2)`): **DR REFUSES, all three,
  `SYNTAX ?` in pass 2, no `.REL`.**  All three verdict predictions were wrong, in the same
  direction.  `E46N21` additionally refutes the pre-registration's own lumping of PAGE and LINE into
  one question — DR accepts one and refuses the other.
* `E46N20`: **refused, as predicted**, with `UNEXPECTED EOF` — one of the two candidates this file
  named.  But the pre-registration's *decision rule* for it was flawed, and that is the more
  important finding: an all-LF file has bare LF in the body **and** no CR on the last line, so it
  cannot separate the two hypotheses it was written to separate.  [C303]'s correction rests on five
  probes already committed and accepted with bare-LF bodies (`E46D4`–`D7`, `E46E4`), not on this
  probe — `RESULTS.md` §5.1.
