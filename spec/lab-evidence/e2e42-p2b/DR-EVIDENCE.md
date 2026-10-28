# E2E-42 / P2b — DR's own multi-item FILE PUT, decoded before any new probe ran

`tools/dis80.py` prints `.` for every relocated operand, so it cannot show which cell a PUT
item addresses; `tools/reldump.py` shows the record stream but not the instruction sequence.
`chaindump.py` in this directory is the decoder written for this phase: it linearizes a .REL's
CODE segment, resolves LINK-FIXUP-PTR targets to segment-qualified labels (`*D(<n>)`,
`*C(<n>)`, `*CODE(<n>)`) and names the external routine each `CD 0000` stands for from the
LINK-EXTNAME records.  The dumps below are its output on objects that ALREADY exist in this
repository, produced before the oracle was invoked on any P2b probe.

## KEYFILE.REL — two items, one attach

`golden/first/KEYFILE/KEYFILE.REL`, code 008C-00AC.  `artefacts/KEYFILE.PLI` line 23 is the
source: `put file(keys) list(name,k);`

```
008C  lxi h  *C(0000)          <- KEYS' control block: LINK-DEF-COMMON-SIZE abs 0026 KEYS
008F  lxi d  0652              <- the file attach mode word [C280]
0092  lxi b  *CODE(00AF)       <- continuation: the byte AFTER the close, not after item 2
0095  call  ?SIOOP
0098  lxi h  *D(0000)
009B  call  ?SLVTS             <- CHARACTER VARYING item
009E  call  ?PNCOP
00A1  lhld  *D(002E)
00A4  mvi a  09
00A6  call  ?QICOP             <- FIXED BINARY item
00A9  call  ?PNVOP
00AC  call  ?QIOOP             <- ONE close for TWO items
```

Both item chains are exactly the chains `golden/e42p2a/E46L1` and `E46L3` put on the same two
classes, on either route [C293].  Nothing between them: no separator, no second `LXI D,0652`, no
second `?SIOOP`.

## CREATE.REL — six items, and the two SKIP shapes

`golden/first/CREATE/CREATE.REL`.

Code 015C-01A7 — `put file(output) list(name,addr,city,state,zip,phone);`, the six members of
`%include 'record.dcl'` (see `artefacts/RECORD.DCL`):

```
015C  lxi h *C(0000) / lxi d 0652 / lxi b *CODE(01AA) / call ?SIOOP     ONE attach
0168  lxi h *D(005A)  ?SLVTS ?PNCOP        name   char(30) varying
0171  lxi h *D(0079)  ?SLVTS ?PNCOP        addr   char(30) varying
017A  lxi h *D(0098)  ?SLVTS ?PNCOP        city   char(20) varying
0183  lxi h *D(00AD)  ?SLVTS ?PNCOP        state  char(10) varying
018C  lxi h *D(00B8)  mvi a 06 / ?DLDOP / mvi a 09 / mvi b 00 / ?QDCOP / ?PNVOP
                                            zip    fixed decimal(6)
019E  lxi h *D(00BC)  ?SLVTS ?PNCOP        phone  char(12) varying
01A7  call ?QIOOP                                                        ONE close
```

The member cells say two things at once.  `zip` at 00B8 and `phone` at 00BC bound that cell at
FOUR bytes, which is the same size this compiler's binder already gives `fixed dec(6)`; and the
five varying members are 31, 31, 21, 11 and (after the decimal) 13 bytes, which is `1 + capacity`
each, so a level-numbered CHARACTER member's cell is the scalar cell laid out at the member
offset — which is [C291]'s finding, here seen on the FILE route rather than the console one.

Code 01AA-01DD and 01E0-01F1 -- the two SKIP shapes:

```
01AA  lxi h *C(0000) / lxi d 0652 / lxi b *CODE(01BE) / call ?SIOOP   <- line 41, `put file(output) skip;'
01B6  mvi a 01 / call ?SKPOP
01BB  call ?QIOOP                          <- 18 bytes: attach, skip, close.  NO item chain.
01BE  jmp  *CODE(0052)                     <- the DO loop back edge
01C1  lxi h *C(0000) / lxi d 0652 / lxi b *CODE(01E0) / call ?SIOOP   <- line 44, `skip list(\'EOF\')'
01CD  mvi a 01 / call ?SKPOP
01D2  lxi h *D(0035) / mvi a 03 / call ?SLCTS / call ?PNCOP           <- the literal, 3 bytes
01DD  call ?QIOOP
01E0  lxi h *C(0000) / lxi d 0652 / lxi b *CODE(01F4) / call ?SIOOP   <- line 45, bare skip again
01EC  mvi a 01 / call ?SKPOP / call ?QIOOP
01F4  call ?STOPX
```

A SKIP on a FILE attach goes BETWEEN the attach and the items -- one `MVI A,<count>` before
`?SKPOP`, the same three instructions the bare console SKIP uses (REVERSE:00FE) -- and a bare
`put file(f) skip;` is a complete statement with a continuation and a close and NOTHING between
`?SKPOP` and `?QIOOP`.  These are CREATE's remaining blockers, and they are a DIFFERENT mechanism
from the item count; P2b does not claim them.  They are now pinned as refusals by REJECTS rows
E41X6 (skip + list) and E41X9 (bare skip), the latter because a real defect lived here: see
RESULTS.md section 5.

## What these two objects do NOT settle

- Neither is an object of THIS project: both are DR corpus programs, compiled by DR, and
  `tools/coverage_check.py` forbids citing a corpus program as the witness for a new claim about
  my own lowering.  They are evidence that the shape EXISTS and that DR ACCEPTS it, which is what
  licenses probing it; they are not evidence about my bytes.
- KEYFILE's two items are a MEMBER and a scalar; CREATE's six are all members, one of them
  DECIMAL.  Neither object puts two ORDINARY variables, or a literal beside a variable, behind
  one attach.  So the multi-item claim for the scalar classes is genuinely unproven and needs its
  own probes.
- No DR object in this repository puts a level-numbered FIXED CHARACTER member behind an attach
  (CREATE has none: four varying + one decimal + one varying), so the fixed-member FILE class
  had no witness at all when the probes were written.  E46M17 asked the question cold and DR
  ACCEPTED it -- see RESULTS.md section 3, where that answer is recorded as a new fact rather
  than as a prediction.
