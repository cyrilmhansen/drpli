# E2E-33 -- encoding correction, the complete ON/GOTO mechanism, and the withdrawal of C203

Gate at this checkpoint: **780 byte-exact / 0 fail, 121/121 negatives refused, 16/16 divergences
as recorded, 12/12 runtime witnesses, exit 0.**  `dune build` and `dune build bin/pli80c.exe`
0 Errors after `dune clean`.  ARCH-1 (`ocaml/proto/') untouched.  No compiler behaviour changed
in this milestone; the four new specimens are E2E-33 measurements that passed on first compile.

## P0 -- `DAD SP' is 39h, not `ED 31'.  My claim was invented, and it hid a missing instruction.

`golden/e32e/E32E2/E32E2.PRN' prints `0009       DAD  SP' in plain text (grep -c = 1), and the
.REL byte at code 0x09 is `39', bracketed by 0x06 = `21 00 00' (LXI H,0000) and 0x0A = `22 xx xx'
(SHLD * A(0019)).  The 8080 has no `ED' prefix at all -- that is Z80.  Nothing about DR's listing
was hiding the instruction: my mnemonic whitelist simply did not contain DAD, and instead of
reading the byte at the apparent gap I asserted an encoding I remembered from a Z80 table, which
happens to be a real Z80 opcode for a different instruction.  Corrected in the E2E-32 note and in
C206 in place; new claim C207 records the procedure (cite the byte; treat a tool's silence as a
claim about the tool).  The saved-SP model is unchanged and stands: HL := SP, stored ONCE PER
BLOCK, read by every handler stub.  Side effect that matters for P1: codegen.ml has no DAD SP
emission path whatsoever (no `d st 0x39' anywhere), so the false encoding was concealing a
genuinely missing instruction.

## P1 -- the ON ENDFILE ... GOTO mechanism, completely characterized (not yet implemented)

From DR's own linked+listed E32E2/E30E2/E32E1 artifacts, plus my own artifacts for comparison:

1. **Registration (already mine, byte-exact)**: `LXI H,<file COMMON> / MVI A,05 / CALL ?ONCOP'.
2. **Two jumps, no RET**: `JMP <continue>` then `JMP <landing pad>`.  A STATEMENT-handler ON ends
   with the inline handler followed by `RET'; a GOTO-handler ON emits no RET at all.
3. **The recovery landing pad** is emitted immediately BEFORE the label's own code and is exactly
   `LHLD * A(cell) / SPHL / CALL ?RECOV' (9 bytes).  The label points AFTER the pad, so a plain
   `goto a' to that label skips recovery while the ON stub enters through it -- which is why G115's
   labels carry zero ?RECOV and are byte-exact.  Pads are therefore per LABEL-TARGETED-BY-ON-GOTO:
   E32E2 has pads at 0x74 and 0x84 (before `a:'s code at 0x7B and `b:'s at 0x8B) and NO pad before
   `c:' (0x91), which only plain gotos reach.
4. **One hidden `*' cell per BLOCK**, and only when the block contains an ON-GOTO: E32E2 stores the
   SP once (`SHLD * A(0019)' at 0x0A) and both pads read the same cell; E32E1, whose handler is a
   statement, has zero `* A(' references and no SP save.  The cell sits at the end of the block's
   automatic area.
5. **`REVERT <conditional>(<file>);' is `LXI H,SYSIN / MVI A,05 / CALL ?REVOP'** (E32E2 code 0x91,
   and it is the label body of E30E2's `fin:', which is why its pad appeared to include a REVOP --
   the REVOP is the revert STATEMENT, not part of the pad).  The E2E-32/P4 note claimed REVERT was
   "already implemented"; that was reading the mnemonic out of my own refusal message's prose.  It
   is not: `grep -i revert' over lib/ast.ml and lib/parser.ml returns nothing, so REVERT has no
   representation in the AST or the parser at all, and NETWORK line 151 needs it.

So the implementation cost is: a REVERT statement (parser + AST + one lowering), the per-block
hidden cell in bind's layout, the SP-save prologue (needs a DAD SP emitter), the two-JMP handler
form, and a landing pad keyed to labels that an ON-GOTO targets.  Mine already has the registration
(E32E1 byte-exact), plain labels and GOTO with forward CHAIN-ADDR resolution (G115 byte-exact), and
the has_goto scan.  Deferred rather than half-installed: a rushed parser/layout change that emitted
the wrong cell count would move the AUTO area of every block and could not be checked against a
runtime, since EOF firing is still unobserved (P3).

## P2 -- C203's cause was wrong, and with it its NETWORK inference

C203 said "with two or more by-reference formals my DATA segment is 4 bytes too large" and inferred
that NETWORK's three-formal `connect' would diverge.  Four new DR-golden probes refute both halves
(golden/e33m): E33M3 (3 FIXED formals, no locals) BYTE-EXACT, E33MM (mixed FIXED+POINTER formals)
BYTE-EXACT, E33ML (2 formals plus locals t,u) BYTE-EXACT, E33MD (3 formals, no locals, WITH
`if a = b') BYTE-EXACT.  What fails is `h(k,j)' with EXACTLY two by-reference formals and NO other
local row: E32C6 (+4 DATA bytes, CODE byte-identical 114/114) and E33MC, reduced to one call site
and one put, +2 bytes (16/14) with CODE byte-identical (81/81).  The excess is therefore neither a
constant nor a function of formal count, and `connect', which takes three formals, measures clean --
**C203 no longer gates NETWORK**.  Mechanism unidentified and deliberately unfitted: five shapes
pass, two fail, and I have no rule that explains the no-other-rows case without inventing one from
the two shapes I chose [C185][C167].

## P3 -- real EOF under simulation: not attempted, and what it would take

Still unobserved.  E31's linked DR E30E2.COM hung to a 20 s watchdog rather than transferring;
`on ... goto` cannot be accepted on a handler whose firing has never been seen, and the CP/M
synthetic-EOF path is the runtime's behaviour, not mine, so a failure to fire is not a compiler
defect.  Next attempt should start from the CP/M BDOS read path under cpmsim with a disk image
whose console/reader returns EOF on the first read, and should treat "handler fires" and "the GET
completes with items unassigned" as two separate measurements [C110].

## P5 -- NETWORK

Unchanged (266 lines, md5-verified).  Still refuses at the ON ENDFILE(sysin) GOTO with no .REL
produced, so no CODE/DATA measurement of mine exists to compare against DR's oracle (CODE SIZE
05B0, DATA AREA 00EB).  After the C203 withdrawal, ON/GOTO + REVERT is the only remaining blocker
with a measured recipe; GO TO, compound conditions and the rest of the graph code sit behind it.

## Hygiene

The --runtime arm re-links and re-runs, and cpmsim writes wall-clock timing into its transcript, so
every gate run dirtied 24 tracked files.  Verified that console bytes and .COM images are unchanged
between runs -- only `I/O ran for N ms' and `Clock frequency' lines move -- then untracked
golden/e32rt_*/*.transcript.txt while keeping .COM, .output.txt, .REL and .PRN tracked.

## E34 recommendation, in order

1. Implement ON/GOTO + REVERT as one unit using items 1-5 above; the two goldens to hit are E32E1
   (must stay exact: it has NO pad, NO hidden cell, NO SP save -- the control that the allocation is
   conditional) and E32E2 (two units, two pads, one cell, plus the REVERT at c:), then E30E2, then
   NETWORK's line 50.
2. Re-attempt unchanged NETWORK.  Do not accept it on compilation success or plausible graph output:
   expect 05B0/00EB, then verify Dijkstra against an independently computed shortest path on a small
   graph where a direct long route and an indirect short route compete -- that is the one class of bug
   that byte-exactness cannot catch, and NETWORK's own `check.txt' oracle already encodes it.
3. Solve EOF firing, and keep "byte-exact ON/GOTO" and "handler fires at runtime" as separate claims
   until both hold [C137][C205].
4. Find the C203 mechanism (2-formals-no-other-row vs 1 and 3), then Family A's liveness rule.
