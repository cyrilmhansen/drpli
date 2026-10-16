# Phase-1 runtime findings (oracle: cpmsim -8 -u, CP/M 2.2)

Date: 2026-10-16. Ledger refs: C018-C024.

## Tool chain (all confirmed working, deterministic)
- `PLI D:NAME $L$D` -> NAME.REL (+NAME.PRN)          [C007/C016]
- `LINK D:NAME` (LINK 1.31, `PLILIB.IRL` on C:) -> D:NAME.COM; map on console.
- 41/41 RELs linked (6 emitted `UNDEFINED SYMBOLS` — the samples needing
  DIV2/FDIV2 RELs or MP/M externals; LINK still produced a .COM).
- DEMO.COM byte-identical across independent sessions -> linker is
  deterministic; safe to use .COM/`cmp` as a fidelity gate [C018].

## Execution goldens
- `golden/run1`: 38 programs run with default `^Z` stdin (EOF during GET ->
  `END OF FILE (1), File: SYSIN=CON` + `Traceback: ...` + abort — RTL
  diagnostic format captured).
- `golden/run2`: scripted dialogs from the Applications Guide. Exact matches:
  DECPOLY `12.2300` (Fig 5-2), FLTPOLY `1.2230000E+01` (Fig 5-1),
  LOAN1 27-row schedule `52.45/30.96/9.33` (Fig 12.1),
  ANNUITY `Payment is       $251.74` (Fig 12.2),
  LOAN2 full table incl. last row `11/82 $0.25 ... $3,000.00 $456.97` (Fig 12.3).
- DEMO: `HELLO John,  WELCOME TO PL/I`.
- Programs whose outer loop re-prompts (LOAN1/LOAN2/ANNUITY; LOAN2's ON ERROR
  catches EOF) never terminate -> harness SIGTERMs sim after dialog is done.
  These are `timeout-or-hang` in summaries; outputs are complete for the dialog.
- RFACT is infinite BY DESIGN (`do i = 0 repeat(i+1)`); observed
  `factorial(n)` table = n! mod 2**16 signed, zero from 18! — see
  golden/run2/RFACT.evidence.txt.

## Fixed arithmetic / attributes (new semantics chapter, C021-C024)
- Default `FIXED` = FIXED BINARY(15,0) (manual l.1563 + $S dump + wrap).
- bin<=15 arithmetic wraps SILENTLY into the 16-bit target (300*300 -> 24464).
  No OVERFLOW check on binary ops (P007/P013A/B).
- FIXED DECIMAL arithmetic is exact BCD; exceeding 15 digits ->
  `FIXED OVERFLOW (1)` + traceback + stop (P016 ladder: 90000, 8100000000 ok;
  square again -> overflow). Constant->variable store out of range ->
  `ERROR (1), Conversion` (P007 storing 65536).
- Max implemented precision = 15 for BOTH bin bits and dec digits:
  FIXED BINARY(16/17/31), FIXED DECIMAL(18,0) declare -> `NOT IMP` and
  NO object file, even though pass 2 reports clean and CODE SIZE is printed
  (P14A-E matrix). bin(6) alone is fine (P13E).
- In multi-line DECLAREs the `NOT IMP` marker is printed after the LAST line
  of the statement, not the offending one (P008/P012 vs P13C) — matters for
  reproducing PRN layouts byte-exactly.
- Storage allocation from $S offsets: bin(1..8)=1 byte, bin(9..15)=2,
  bin(16..17)=3 (but NOT IMP), dec digits ~1 byte/2 digits (+1?). The
  `$S` listing itself (`BLOCK AT LINE n, AUTO STORAGE m BYTES`, symbol
  lines `c XXXX NAME ATTRIBUTES`) is a ready-made spec for our symbol table.

## .INT handoff (C003) and $V (C004)
- SIGKILL the sim right after `NO ERROR(S) IN PASS 2` -> work disk retains
  `demo.int` (0-byte dir entry — CP/M flushes on close) alongside opened
  PRN/REL: proves pass1-2 -> .INT -> pass3 pipeline on the neutral oracle.
- `$V` prints the mnemonic IR stream interleaved with source; `MISSING QUOTE`
  etc. diagnostics confirm compiler's own switch legend echo per compile
  (`V: Verify Intermediate File`). $S = "Symbol Table List".

## Harness mechanics (lessons)
- CP/M typeahead: program console input may be sent IMMEDIATELY after the
  `##SEND NAME\r` launch line — no need to wait for the program prompt;
  waiting FOR the prompt before sending input is what poisoned run1.
- CP/M 2.2 prints its prompt as `\nD>` (LF before, no CR) — prompt regexes
  must match that.
- run.py now: `##KILLON <regex>` (mid-compile forensics), `##SEND` with
  \x/\r escapes, `!!LINE-TIMEOUT` -> rc!=0, `##HALT` re-sends `\rA:BYE\r`
  until sim exits (immune to typeahead garbage).
- batch.py classify() now requires BOTH passes clean (C025: it previously
  called NOT-IMP-killed compiles "ok"; first8080u audit: only the 3 known
  rejections affected, 41 clean samples stand).

## Open / next
- File-based samples (COPYLPT, CREATE, KEYFILE, RETRIEVE, UPDATE, REPORT,
  COPY, ENTER?, DIO*) need real data files or FCB.DCL setup — deferred batch.
- `$E` (expression-optimizer trace) vs `$V` diff not yet captured (C005).
- CALL sample rejection root cause (separate from INVERT family).
- Switch legend table for v1.4 (`V E S M N A B C T I L D P K?`) — echo header
  lists what's active per compile; enumerate by probe.
- Condition-code numbers in RTL messages ("(1)", "(2)") — semantics TBD.
