# E2E-35 — NETWORK byte parity and executable control-flow evidence

Episode scope (from the task): (P0) make the size measurements mean what they are called, (P1)
get a normal-flow execution witness for ON ... GOTO without simulating an EOF, (P2) explain and
close NETWORK's first divergence, (P3) iterate NETWORK, (P4) run NETWORK and deliver a real EOF,
(P5) keep the remaining semantic hazards separate, (P6) sketch a machine-readable coverage
inventory.  This file records what has actually been measured, phase by phase.

## P0 — what "code size" means, and what the divergence panel had been printing

`tools/e2e_gate.py::_rel_stats` returned a count of the strings reldump prints as `DATA code'.
DR's .REL is a bit stream (see `tools/reldump.py::decode`): a clear bit introduces one data byte
at the current (segment, logical address); a RELOC item advances that address by two and adds no
item; a CHAIN-EXT fixes up an operand word whose bytes are elsewhere.  The item count is therefore
`section size minus fixup bytes`, not a size:

    E34G1   58 items      CODE SIZE = 0046 = 70 bytes
    NETWORK 1096 items    CODE SIZE = 05B0 = 1456 bytes

The distinction is not pedantic for NETWORK, which is the program this episode is about: the
recorded excess was +5 (1101 vs 1096 items) while the section excess is **+7 (1463 vs 1456)**,
because DR and I differ in how many operand words get relocated as well as in how many bytes we
emit.  For the other 16 rows the mine-minus-DR delta survives the redefinition, which is exactly
why the mistake stayed invisible: a metric that preserves deltas looks like a size.

`tools/relstats.py` (new) reads the sizes out of `LINK-DEF-CODE-SIZE` / `LINK-DEF-DATA-SIZE`
using **reldump's own decoder** — it imports `decode()` rather than parsing the stream again, so
there is one decoder [C202].  That those fields equal DR's listing is measured, not assumed:

    $ python3 tools/relstats.py --selfcheck golden
    relstats selfcheck: 3596 declared sizes; 2600 cross-checked against a DR listing;
    2583 agree; 0 disagree in DR-produced files (INVARIANT); 17 disagree in *_mine files
    (byte-parity gaps, expected); 0 other

The 17 `*_mine` disagreements are my .REL next to DR's listing — real parity gaps, listed in
DIVERGENT.txt.  Four more appeared on the first run in directories *without* that marker; every
one was provenance, not measurement: the runtime panel stores the artifact it executes, and
[E2E-23] requires that to be MY .REL, so `golden/e30g1m`, `golden/e32rt_E32B3`,
`golden/e32run_E32B3` and `golden/e32rt_PB4` hold my output beside DR's listing.  Each was
confirmed by rebuilding the artifact and comparing hashes (E30G1 `f28c07f8…`, E32B3 `9e471af4…`,
PB4 `626d41f0…`), and they are exempted by pinned md5 in `relstats.MY_OUTPUT` rather than by a
path pattern, so the exemption dies if the bytes move.

A falsified hypothesis, recorded because it was mine: relstats first asserted
`items + 2*relocs == declared`.  The corpus refuted it (P046 spells 8 data items + 14 relocs into
a 16-byte data segment, so relocs overlap items).  No formula is asserted now; the only claimed
relationship is the one measured against DR's listing.

Panel changes: `_rel_stats` returns the declared sizes and RAISES if a .REL has no
DEF-CODE-SIZE record (an unknown size is not zero); `divergence_load` now skips `#` lines so the
panel can define its own columns; all 17 rows were re-measured and DIVERGENT.txt carries the
legend and a provenance note for the old numbers.  `nbytes` is unchanged for all 17 rows — it was
always a file-level diff and it still is.

`emit_sp_save`'s 7 bytes were verified against DR's listing, not against my codegen:
E32E2 `0006 LXI H,0000 / 0009 DAD SP / 000A SHLD *A(0019)` and the next source line starts at
`000D`, so the save is 0x000D-0x0006 = 7 bytes; the pad at `0074 LHLD *A(0019) / 0077 SPHL /
0078 CALL ?RECOV` ends at `007B` = 7 bytes as well.

## P1 — normal-flow ON ... GOTO, executed (E35N1, E35N2), and E32E2 registered

Nothing with the ON/GOTO machinery in it had ever been run.  E32E1 and E32E2 have DR goldens and
are byte-exact, but both `get list(w)` from SYSIN: executing them requires an ENDFILE event, and
simulating one and calling it evidence is forbidden (standing instruction, and [C205]).  So two
new probes were built that never read:

    e35n1: procedure options(main);
      declare sysin file, n fixed;
      n = 0;
      on endfile(sysin) goto h;      -- registers ?ONCOP, allocates the hidden SP cell, pads h
      goto a;
    a: n = n + 1;   goto b;
    b: n = n + 2;   goto h;          -- plain GOTO to a label that ON/GOTO padded
    h: n = n + 4;   put list('n=', n);   stop;
    end e35n1;

E35N2 is the same with `revert endfile(sysin);' inserted before the last goto.  Both were
DR-compiled fresh (`oracle/batch.py E35N1 E35N2 --tag e35n`), both are **byte-exact** against
those goldens, both linked through LINK 1.31 + PLILIB and both ran to normal termination:

    DR   image:  n=         7        mine image:  n=         7
    DR .COM md5: f82211438733dc46c6bc59fa7f0462d2 (E35N1)  594336c617e22caa834cf75ac01326d5 (E35N2)
    my .COM md5: identical in both cases

`n = 0+1+2+4 = 7` was written down from PL/I semantics before the run, and it is what both images
print, so the value is an independent expectation and not a transcription of the output.  Because
the images are identical, the run is [C205]-circular as evidence about my *lowering*: it validates
the expectation and DR's oracle.  What is NOT already known, and is now observed, is the pad's
place in ordinary control flow.

**The pad is where a plain GOTO lands.**  In the linked image, DR's own bytes:

    0136  C3 39 01          JMP 0139          <- the compilation of `goto h;'
    0139  2A CA 1A          LHLD 1ACA         <- hidden saved-SP cell (block DATA +0004)
    013C  F9                SPHL
    013D  CD 67 12          CALL 1267         <- ?RECOV
    0140  2A C8 1A          LHLD 1AC8         <- h's body: `n = n + 4;'

The recovery pad is the label.  `goto h' does not jump to 0140; it jumps to 0139, restores SP from
the cell, calls ?RECOV with nothing pending, and falls through into the body.  This confirms
[C209] from the executable rather than from a listing, and it shows DR's design is safe in exactly
the case the model made me worry about -- a pad executed when no condition is pending.  E35N2
additionally gives the first observed execution of the `revert endfile(sysin)' emission (?REVOP)
in straight-line code, with the same value and clean termination.

Registered with this slice: E35N1, E35N2 as specimens *and* runtime-panel rows (14/14 runtime now,
was 12/12), and E32E2 as a specimen -- its golden had been verified by hand in E2E-34 and never
enforced, and it is the only probe pinning two GOTO handlers plus a REVERT in one block with the
saved-SP cell allocated **per block** [C206].  Gate: 843 byte-exact / 0 fail, 119/119 negatives,
17/17 divergences, 14/14 runtime witnesses, exit 0.

Still not done, and not claimed: the ENDFILE condition has still never FIRED in anything I
executed.  P4 needs a real EOF -- a named file that reaches end-of-data, not a scripted Ctrl-Z
(`oracle/linkrun.py` documents why the latter is unreliable for SYSIN).

Tooling lesson kept because it nearly produced a false report: `tr -d '\x1a'` (GNU tr has no \x
escapes) deletes the characters `\`, `x`, `1`, `a`.  Displaying a probe with it made intact files
read as corrupt (`declare` -> `declre`, `n = 1` -> `n = ;`).  Verified with python before
repeating the claim; display commands that touch evidence get checked like everything else.
