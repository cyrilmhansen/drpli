# LEARN.PLI — validation of the learnxinyminutes PL/I-80 tutorial against original DRI tools

Date: 2026-10-19.  Performed at user request, outside the E2E milestone plan.
Evidence: `golden/learn/` (source, `.REL`, `.COM`, console output, all three
raw tool transcripts, `MANIFEST.sha256`).  No change to the OCaml compiler.

## 1. Provenance of the source

Retrieved from the single ` ```text ``` ` fenced block of

    https://raw.githubusercontent.com/cyrilmhansen/learnxinyminutes-docs/refs/heads/add-pli-tutorial/pli.md

branch `add-pli-tutorial`, remote HEAD at time of retrieval:

    b2d6f16abee871471d1f1c626ce816c6fe107b58  refs/heads/add-pli-tutorial

Program text: 123 lines, 3948 bytes.  The repo file is LF-only.  It was saved
as `LEARN.PLI` in CP/M text form: every LF converted to CRLF, then a trailing
`^Z` (0x1A) end-of-file byte.  That is the file-system convention CP/M text
files need and the form every source in `artefacts/` is in (verified against
`artefacts/DEMO.PLI`, `artefacts/RFACT.PLI`); **no program character was
changed**.  A byte-level round-trip assertion (`CRLF` -> `LF` == repo block)
was used to prove this, and the assertion is part of how the specimen was
created, not an after-the-fact claim.

## 2. Environment

| component | banner as printed |
|---|---|
| compiler | `PL/I-80 Compiler    Version 1.4` / `Serial No. 3032-0000-001130` / `Copyright (c) 1980-1982  Digital Research, Inc.` |
| linker | `LINK 1.31` |
| monitor | `64K CP/M Vers. 2.2 (Z80 CBIOS V1.2 for Z80SIM ...)` |
| machine | z80pack `cpmsim -8` (pure 8080), CP/M 2.2 boot seed `oracle/disks/drivea.dsk` |

## 3. Exact commands

```
C:
PLI D:LEARN
LINK D:LEARN
D:
LEARN
```

`PLI D:LEARN` / `LINK D:LEARN` are the drive-qualified form of the documented
`PLI LEARN` / `LINK LEARN`: this harness keeps the compiler and linker on `C:`
and the source and objects on a scratch `D:`.  Semantically the same commands.
No compiler switches were passed, so the run used PL/I-80 defaults and produced
no `.PRN` listing.

## 4. Compiler result — clean, no diagnostics

```
COMPILATION OF: LEARN


   NO ERROR(S) IN PASS 1

   NO ERROR(S) IN PASS 2


CODE SIZE = 041A
DATA AREA = 012B
FREE SYMS = 3469
END  COMPILATION
```

`LEARN.REL`, 3072 bytes.  Note for the retro-engineering record: the tutorial
uses `%REPLACE LIMIT BY 4;`, `**`, `STATIC INITIAL`, `FLOAT BINARY(24)`,
`BIT(1)`, character `VARYING` plus `LENGTH`/`SUBSTR` (including `SUBSTR(...) = `
as a target), a 1/2-level structure, a two-dimensional `FLOAT` array,
`POINTER`/`BASED` with `ALLOCATE ... SET()`/`FREE`/`NULL()`, `PUT SKIP EDIT(...)
(F(7,2))`, `ON`/`SIGNAL`/`REVERT`, `SQRT`, a nested `CALL`, and a `RECURSIVE`
function — and original PL/I-80 1.4 accepts all of it in one pass pair.

## 5. Linker result — clean, no diagnostics

```
LINK 1.31

PLILIB   RQST   LEARN    0100   /OUTPUT/ 31B9   /ERRMSG/ 31F0
/SYSIN/  3283   /SYSPRI/ 32AA

ABSOLUTE     0000
CODE SIZE    30B9 (0100-31B8)
DATA SIZE    045B (32FD-3757)
COMMON SIZE  0144 (31B9-32FC)
USE FACTOR     9F
```

`LEARN.COM`, 13952 bytes.

## 6. Program output — complete, verbatim

```

Hello, world!
Total:        10
Half:  5.0000000E-01
  13.75
PL/I on CP/M      12
PL/I
Ready
        1         1
        2         4
        3         9
        4        16
Even:         2
Even:         4
Even:         6
Square root:  3.0000000E+00
Heap:        42
Ada                          2
From procedure:        10
5 factorial:       120
Division by zero signalled
ZERO DIVIDE (0)
Traceback: 0498
```

Every statement before the abnormal stop produced its expected output, including
the `SIGNAL ZERODIVIDE` ON-unit, the `ALLOCATE`/`FREE`/`NULL()` sequence,
`SQRT`, the structure qualified names, the nested `CALL SHOW_NUMBER`, and the
recursive `FACT(5)` = 120.  After `Division by zero signalled` the runtime
printed `ZERO DIVIDE (0)` and `Traceback: 0498` and returned to the `D>`
prompt.  CP/M carries no program exit status, so there is no exit code to
report; the harness session itself ended normally.

## 7. Diagnosis: documented PL/I-80 behavior, not a compiler defect

The abort is the documented consequence of PL/I-80 treating arithmetic
exceptions as *terminal* conditions.  Verified directly in the local copy of
**PL/I-80 Applications Guide, second printing December 1980, section 7.5,
printed page 65** (`manuals/PL1-80_Applications_Guide_Dec80.pdf`, SHA-256
listed in `manuals/SHA256SUMS`, checksum verified).  Quoted, with the scan's
OCR artifacts left as found:

> "The arithmetic exceptions are FIXEDOVERFLOW or FIXEDOVERFLOW{i) ...
> ZERODIVIDE or ZERODIVIDE(i) ... Note, however, that all arithmetic faults are
> considered terminal. That is, if an ON condition is set for an arithmetic
> exception, then the on-body must contain a transfer to a global label.
> Otherwise, the program is terminated upon return from the ON unit."

The tutorial's ON-unit is

    ON ZERODIVIDE PUT SKIP LIST('Division by zero signalled');

which is a plain statement with no `GO TO` to a global label.  Under the rule
above the program is therefore *required* to terminate on return from that
ON-unit, which is exactly the observed `ZERO DIVIDE (0)` + traceback.  So:

- **DR PL/I-80 1.4** — handler prints its message, then the runtime terminates
  the program.  Correct per its own documentation.
- **Iron Spring PL/I 1.4.1** — handler prints its message, execution resumes.
  That is the IBM-style (non-terminal / resumable) reading of the same code.

This is a **language-semantics dialect difference**, and the observed output is
not evidence of a compiler or linker fault.  It is recorded as claim **C102**.
The user has revised both the English and French tutorials to `GO TO` out of
the ON-unit, which satisfies both implementations; the revision was not
retested here, as instructed.

## 8. Status in this repository

- `LEARN.PLI` is retained as a validation specimen (`learn/`, copy in
  `golden/learn/`).  It is **not** one of the 41 DR corpus programs and does
  not count toward the corpus score; it came from a tutorial, not from the
  December 1980 distribution, and there is no `first8080u` golden for it.
- Current build refuses it fail-loud at the first unsupported declaration kind:
  `codegen: declared variable kind not in supported subset [TBD]: BIT(1)`.
  That refusal happens before the `POINTER`/`BASED`, `VARYING`, `FILE`,
  `ON`/`SIGNAL`, array, and `FLOAT` perimeter members, all of which are also
  independently refused or unsampled.
- If `ON`/arithmetic-exception handling is ever implemented here, the terminal
  semantics documented above is the behavior to reproduce, and this specimen is
  the regression test for it: an ON-unit that returns normally must end the
  program, not resume at the statement after the `SIGNAL`.
