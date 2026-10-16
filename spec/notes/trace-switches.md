# PL/I-80 v1.4 diagnostic switches — enumerated on cpmsim (C032)

Method: compile P043 (5-line program) with each `$X` in one oracle
session; compiler echoes a self-describing legend per active switch.
Goldens: golden/optswitches.raw.txt, golden/opt-p044.raw.txt,
golden/opt/EXPR1-{VL,EL,VEL}.txt.

| switch | legend echo          | observed output (small program) |
|--------|----------------------|---------------------------------|
| $A     | Analysis Trace       | nothing beyond $L on P043/P044 (needs deeper test material?) |
| $B     | Built-In Subroutine Trace | per-statement list of emitted RTL calls: `000E DLDOP`, `0019 QDI15`, `0030 SYSPR`, `SKPOP`, `QICOP` |
| $C     | Code Trace Only      | **8080 disassembly with addresses + operands per source line** (`LXI B,0200`, `CALL ?START`, `LXI H,* S(0000)`, `MVI A,01`, `CALL ?DLDOP`, `PUSH H`, `LHLD X A(0002)`, `SHLD ...`) |
| $D     | Disk Print           | listing to PRN file [C007] |
| $E     | Expression Optimizer Trace | per-expression node-indexed tree blocks headed `## P O C W PR SF CS SZ` |
| $I     | Interlist Source and Code  | same disassembly as $C interleaved (diff vs $C TBD — C may suppress source echo) |
| $K     | (no legend)          | accepted silently; unknown effect |
| $L     | List Source Program  | numbered listing |
| $M     | Memory Map           | nothing extra visible on P043/P044 (test with bigger program) |
| $N     | Nesting Level Display| nothing on flat program; test nested |
| $P     | (no legend)          | accepted, no output on P043 (PICTURE-only? or dead) |
| $S     | Symbol Table List    | `BLOCK AT LINE n, AUTO STORAGE m BYTES` + attribute/storage dump (see P008/P011 evidence) |
| $T     | Trace Optimizer Actions | per-statement IR node table `nn OPCODE cc` (tree form) |
| $V     | Verify Intermediate File | serialized IR stream with CTL words (C004) |

## Codegen model revealed by $C/$B/$T on P043/P044  [C033]

1. Prologue: `LXI B,0200; CALL ?START` (B = ?stack/base page).
2. Constants live in a **string/data pool**: operands printed
   `* S(0000)`; loaded via `LXI H,*S(k); MVI A,digits; CALL ?DLDOP`.
3. Variables: `LHLD/SHLD X A(0002)` — storage addressed "name A(offset)"
   (matches $S offsets: first auto var at 0002 above the pointer?).
4. Typed opcode families: D*=decimal nodes (DID/DLD/DAD/DMU), I*=16-bit
   int (ILD/IAD/IMU/IAS), conversions QDI/QIC (quotient→int16),
   LIO/SIO/C2/CID/CLD/PNC/SKP/BLK/NID/ENT/BEG/STP/ONC/ENC.
   Numeric literals in expressions are FIXED DECIMAL until a bin target
   forces QDI15.
5. OPTIMIZER (pass 3 codegen) actions observed:
   - identity `x*1`, `x+0` ELIDED (code = bare LHLD/SHLD self-copy;
     the copy itself is NOT removed — byte-identical target keeps it!)
   - `3*x`: constant gets `LXI D,0003` immediate path (no pool)
   - `2+4` NOT folded at compile time (DADOP at runtime)
   - IR trees printed by $T/$E still CONTAIN the eliminated nodes —
     elimination happens at translation to code, not in the .INT file.
6. RTL entry names in `?NAME` form match the PLI2.OVL 8-char string
   table (DLDOP/DMUOP/QDI15/SYSPR/SKPOP/QICOP/START...). Our back-end
   must reproduce the exact call sequence for byte-identity.

## .INT vs code note
The T/E trees dump pre-codegen IR; V dumps the serialized file. The
optimizer's decisions are only observable by diffing IR against $C code.
=> Our reimplementation must model the IR faithfully AND the tree->code
peephole rules exactly for byte-identical output.

## $1/$2 TITLE semantics (Applications Guide §"TITLE(c)")  [C034]
`x`/`y` positions in a TITLE string may be `$1`/`$2` = the program's
FIRST/SECOND default names from the CP/M command line (FCB1/FCB2).
Empirically proven by the keyed-file chain: `ENTER EMPDB` creates
`EMPDB.EMP` (title '$1.EMP'); bare `ENTER` => `UNDEFINED FILE (1),
File: EMP=NUL` + traceback. UPDATE uses `open ... update direct
environment(f(128))`; KEYFILE uses `stream output linesize(60)`.
Full chain ENTER->KEYFILE->UPDATE runs clean under cpmsim -8 with
dialogs scripted; data goldens: golden/iofam2/EMPDB.EMP / .KEY.
Record layout (128-byte fixed): level-1 struct image; char varying =
1-byte length + inline chars (stale tail bytes from INITIAL remain —
buffer never cleared), fixed decimal = packed BCD-ish digits.

## Stream-file format  [C035]
PUT FILE ... LIST writes LIST-DIRECTED TEXT: strings quoted, space
separated, `skip` => CRLF (golden/iofam1/NA.dat, byte-reproducible).
CREATE/RETRIEVE round-trip captured end-to-end (iofam1).
