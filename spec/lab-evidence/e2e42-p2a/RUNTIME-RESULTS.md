# E2E-42 / P2a-D — the seven runtime objects, and four of six predictions being wrong

`oracle/linkrun.py link` + `run` under the vendored `thirdparty/z80pack/cpmsim/cpmsim`, with
`oracle/cpmwork.py`'s `sanitize_cp` guards intact (drive C = the PL/I-80 tools distribution with
its original read-only system tracks; drive D = a freshly formatted scratch disk; the written
file is EXPORTED out of the image, never read off the host filesystem).  Both sides are run from
the SAME harness with the SAME boot seeds: `golden/e42p2adr/` links DR's own `.REL` from
`golden/e42p2a/`, `golden/e42p2a_mine/` links the `.REL` this compiler produces from
`probes/E46L12..E46L18.PLI`.

## The comparison, per object

| probe | class | `.COM` vs DR | console vs DR | written file vs DR | DR's payload |
|---|---|---|---|---|---|
| E46L12 | `v char(20) varying`, `v = 'HELLO'` | IDENTICAL | IDENTICAL (`DONE\r\n`) | IDENTICAL, 128 bytes | `'HELLO'` — 7 |
| E46L13 | `c char(20)` fixed, `c = 'ABC'` | IDENTICAL | IDENTICAL | IDENTICAL | `'ABC                 '` — 22 |
| E46L14 | `k fixed bin(15)`, `k = 42` | IDENTICAL | IDENTICAL | IDENTICAL | `       42` — 9 |
| E46L15 | `z fixed dec(6)` (s=0), `z = 123` | IDENTICAL | IDENTICAL | IDENTICAL | `      123` — 9 |
| E46L16 | three separate file PUTs, one stream | IDENTICAL | IDENTICAL | IDENTICAL | `'AA' 'B' 'CC'` — 13 |
| E46L17 | console PUT, file PUT, console PUT | IDENTICAL | IDENTICAL (`CON AGAIN\r\n`) | IDENTICAL | `'FILE'` — 6 |
| E46L18 | **the same variable on BOTH routes** | IDENTICAL | IDENTICAL (`HELLO\r\n`) | IDENTICAL | `'HELLO'` — 7 |

Every one of the seven is also a byte-exact whole `.REL` against `golden/e42p2a/` (512/512,
384/384, 512/512, 512/512, 640/640, 512/512, 512/512 bytes).  Each written file is 128 bytes:
the payload, then `0x1A` to the end of the record.

## Four of six runtime predictions were WRONG, and the fourth was invented

| pred | said | measured |
|---|---|---|
| **H12** | exactly the 5 bytes `HELLO`, nothing else | **7 bytes: `'HELLO'`** — the apostrophes really are written |
| **H13** | 20 bytes starting `ABC` | **22 bytes: `'ABC'` + 17 blanks + `'`** — the padding question is answered (BLANKS, `0x20`), the quoting was missed |
| **H14** | 7 spaces then `34`, because "FIXED BINARY prints in base 8, [E2E-8]'s measurement" | **7 spaces then `42`** — DECIMAL |
| **H15** | 6 spaces then `123` | **6 spaces then `123`** ✓ the only one that landed |
| **H16** | `AABCC`, no separator | **`'AA' 'B' 'CC'`** — quoted AND blank-separated |
| **H17** | file holds `FILE` | file holds **`'FILE'`**; the console half (`CON` then `AGAIN`) was right |

**H14's "octal" was a fabrication and I need to say so plainly.**  I wrote "[E2E-8]'s measurement
that FIXED BINARY prints in base 8" into the hypothesis file as if it were a citation from this
repository.  It is not: `grep -n "base 8\|octal\|OCTAL" spec/ tools/` returns nothing but my own
sentence.  No object here ever measured the radix of a FIXED BINARY `PUT LIST`, and DR prints
`42`.  That is the failure mode the mission brief names — an invented rationale dressed as
evidence — committed by me, in the file that exists to prevent it.  The number is not the damage;
the damage is that a prediction that quoted a measurement which does not exist was allowed to
stand next to five that were honestly derived.

## The two facts the runtime produced, and the object that separates them

**A CHARACTER item is apostrophe-delimited on the FILE route and NOT on the console route.**
E46L18 is the discriminating object, written AFTER the L12/L17 discrepancy appeared and BEFORE
its oracle run, precisely to separate the two available explanations: if the assignment
`v = 'HELLO'` stored the delimiters into the cell then the console line would carry them too; if
the file's output edit adds them then the console shows bare `HELLO`.  The console shows `HELLO`
and the file shows `'HELLO'`, from the SAME variable in the SAME program, through item chains
that this compiler emits byte-for-byte identically (`LXI H,*D(<v>) / CALL ?SLVTS / CALL ?PNCOP`)
and which differ only in the statement prologue (`?SYSPR` on `0x0252` versus `?SIOOP` on the
attached `0x0652`).  So the delimiters are a property of the STREAM, selected at run time, not of
the emitted item code and not of the stored value.  The mechanism inside PLILIB is unmeasured —
which routine appends the apostrophes, and whether an OPEN option could turn it off, are both
questions with no object here.

**Successive PUT LIST statements on one stream are separated by one blank and never
line-terminated.**  E46L16 writes three items with three statements and the file is
`'AA' 'B' 'CC'`: 4+1+3+1+4 = 13 bytes, no CR, no LF, no restart at offset 0.  E46L17's console
agrees from the other route — `CON AGAIN` on one line, no apostrophes.  This is the measurement
that retires the old F(128) "record size" story's last shadow: nothing in the program asks for a
terminator and none appears.

**Numeric items are right-justified in the 9-wide field DR asks for and are NOT quoted** —
`       42`, `      123` — and `s = 0` produces no decimal point at all (E46L15), which is the half
of the DECIMAL route R502 (scale 3) never reached.

## What this validates, and what it does not

Because every `.COM` here is byte-identical to DR's, these runs CANNOT be evidence about my
lowering — the objects are the same bytes, so agreeing is forced.  That is [C205]'s circularity,
stated rather than hidden.  What the runs do establish: (a) the `.REL` files this compiler writes
LINK through LINK 1.31 + PLILIB with no undefined symbol and no `UNRESOLVED EXTERNAL`, so the
external references and the DEF-DATA layout are executable, not merely equal; (b) the FILE route
runs END TO END and the bytes land in a real CP/M file; (c) they land identically; (d) the
programs TERMINATE (rc=0, `done`, prompt returned) — a PUT FILE that hung or aborted would show
up here and nowhere else; and (e) the runtime behaviour above, which no `.REL` comparison can
reveal.  The compiler evidence is the byte-exact `.REL`; the runtime rows are corroboration plus
the only source of the output-content facts.
