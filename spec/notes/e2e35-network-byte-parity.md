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
