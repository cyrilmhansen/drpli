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

Every one of the seven is also a byte-exact whole `.REL' against `golden/e42p2a/': E46L12 512/512, E46L13 512/512, E46L14 384/384, E46L15 512/512, E46L16 640/640, E46L17 512/512, E46L18 512/512 bytes -- read out of the files with `stat', not written down from memory, which is how the first version of this sentence came to transpose E46L13 and E46L14.  Each written file is 128 bytes:
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

**H14's "octal" was a fabrication, and it was committed in TWO places, not one.**  I wrote
"[E2E-8]'s measurement that FIXED BINARY prints in base 8" into the hypothesis file as if it were a
citation from this repository, and then repeated the same invented authority under a second name —
"the E3B2 measurement" — inside `probes/E46L14.PLI`'s own comment, where it shipped in the P2a
commit.  Neither exists: there is no E3B2 specimen in `probes/`, `spec/INVENTORY.txt`,
`spec/COVERAGE.tsv` or `spec/RUNTIME.txt`, and no `[E2E-8]` claim about a radix in `spec/CLAIMS.md`.
No object here ever measured the radix of a FIXED BINARY `PUT LIST`, and DR prints `42` — DECIMAL
[C295].  The second copy is the worse one, because a probe comment reads like documentation of a
measurement rather than like a prediction, and the corrected text now sits in that file saying so.
`HYPOTHESES.md` H14 still says octal on purpose: a hypothesis edited after the run stops being
evidence.  The number is not the damage; the damage is that a prediction quoting a measurement
which does not exist was allowed to stand next to five honestly derived ones.  Full accounting in
`PROCESS.md`.

## The two facts the runtime produced, and the object that separates them

**A CHARACTER item is apostrophe-delimited on the FILE route and NOT on the console route.**
E46L18 is the discriminating object, written AFTER the L12/L17 discrepancy appeared and BEFORE its
oracle run, precisely to separate the two available explanations: if the assignment `v = 'HELLO'`
stored the delimiters into the cell then the console line would carry them too; if the file's
output edit adds them then the console shows bare `HELLO`.  The console shows `HELLO` and the file
shows `'HELLO'`, from the SAME variable in the SAME program, through item chains this compiler
emits byte-for-byte identically.

**And the operand is proved BARE, so no assignment is being blamed.**  This is a second,
independent argument, read straight out of DR's linked image where the `*D` relocs have become
real addresses one can look at.  E46L16's file item `list('B')` is `LXI H,1A31 / MVI A,01 /
CALL ?SLCTS / CALL ?PNCOP` — and the byte at `1A31` is `42`, the single character `B`, with the
length argument saying ONE.  The file E46L16 writes contains `'B'`: three bytes.  Two bytes appear
that are in no cell, in no length, and in no emitted instruction.  In the same program the console
literal `'DONE'` sits bare at `1A32` (4 bytes, printed as `DONE`), and E46L5's `list('HELLO')`
points at `19D2` holding a bare 5-byte `HELLO` while the same route is what writes `'HELLO'` in
E46L12's file.  So the delimiters are produced AFTER `?SLCTS` receives a bare string — they are
the stream's edit, established for literals as well as for the varying variable.  What remains
unmeasured is the mechanism inside PLILIB: which routine appends them, and whether an OPEN option
could turn it off — no object here varies either.

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
