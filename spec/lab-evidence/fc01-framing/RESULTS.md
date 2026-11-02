# fc01-framing — RESULTS (oracle run landed 2026-11-02; FC-01 detour round)

Pre-registration: probes + `HYPOTHESES.md` + `BASELINE-MINE.txt` committed at `da029ec`
**before** the first DR PLI.COM invocation (PROTOCOL #1; ordering provable from commit blobs:
the oracle goldens `golden/fc01ps*` appear only in the later evidence commit).

## §1 Run records

Compile (DR oracle): `PLI_SRC=probes python3 oracle/batch.py FCPS1 FCPS2 FCPS3 --tag fc01ps
--switches '$L$D'` → **3 ok / 3, NO dr-refuses**; PRN+REL+transcripts in `golden/fc01ps/`.

Link: `linkrun.py link --tag fc01ps --out fc01ps-l` → all three `COM=True`, no UNDEFINED
SYMBOLS (full segment reports in `golden/fc01ps-l/link-batch0.transcript.txt`).

Run: `linkrun.py run --tag fc01ps-l --out fc01ps-r` → rc=0 `done` witness for all three
(one session per program; default single `^Z` console-input script, unconsumed — the programs
are pure PUT).

## §2 Measured verdicts

### 2.1 H1 ACCEPTED — the exit chain emits exactly ONE final newline unconditionally

DR console region (FS-01 anchor law applied to the oracle transcripts; raw bytes):

| probe | DR console (repr) | predicted under H1 | predicted under H2 | verdict |
|-------|-------------------|--------------------|--------------------|---------|
| FCPS1 | `b'X=         1\r\n\r\n'` | `X=         1\r\n\r\n` | `X=         1\r\n` | **H1 match; H2 FALSIFIED** |
| FCPS2 | `b'Y=         2\r\n'` | `Y=         2\r\n` | same | control ✓ |
| FCPS3 | `b'\r\nL=         1 M=         2\r\n'` | `\r\nL=         1 M=         2\r\n` | same | control ✓ |

Law: a bare `PUT SKIP;` as the LAST executed output statement prints exactly one CRLF, and the
program-exit chain prints one MORE CRLF regardless of line state (closing an unterminated line —
the measured E32B1 behaviour — and also firing after a fresh SKIP). The `PUT SKIP LIST` spelling
at stream START emits its own CRLF first (leading blank line — FCPS3), confirming on the DR side
what E29PS1 [C192] measured for the bare spelling.

### 2.2 Object-tier finding — my `.REL` is DR's, byte-for-byte, on all three probes

Whole-file `.REL` comparison (PROTOCOL #6): FCPS1 256/256 B BYTE-EXACT, FCPS2 256/256 B
BYTE-EXACT, FCPS3 384/384 B BYTE-EXACT; consequently the LINK-80 images are byte-equal too
(7168/6912/7168 B). The console equality of §2.1 is therefore *by construction* on the FCPS
objects — the direct DR console run remains the primary witness of the framing LAW, the byte
comparison is the witness that MY COMPILER emits DR's object for these shapes.

### 2.3 Classification of the FC-01 Batch-A Lane-B failures (2026-11-02)

With §2.1, the eight Batch-A ASSERT FAILs are ALL expectation defects (`my-gap` in the SPEC
layer — the reference derivations failed to model framing), NOT compiler or runtime gaps:

- 8/8 programs carry a leading blank line: each one's first executed output statement is
  `PUT SKIP LIST` (measured law, FCPS3 + E29PS1).
- MATH-00 additionally carries a trailing blank line: last executed output statement is a bare
  `PUT SKIP;` (measured law, FCPS1).

The correction path (README § 6 law amendment, reference-derivation + spec updates, schema
extension for blank-line entries) is functional-harness work; it must reproduce the expected
streams by DERIVATION from the declared program shape + § 6, never by capture (L3).

## §3 NOT said by this round

- Nothing about GET/input echo framing (Batch-A programs do no GET; REVERSE's extra newlines
  stay recorded but uncharacterized).
- Nothing about file streams (`PUT FILE`), SKIP counts >1 at exit, page boundaries, or
  `PAGE`; only the console line framing above was sampled.
- No FCPS runtime row was added to `spec/RUNTIME.txt` (byte-tier discipline); no SPECIMENS
  registration happened in this hop — the three probes are registration candidates for a
  later gate hop (objects are byte-exact today).
- The claim number for the framing law is C352 (ledger ENDS C352); the E29PS1/C192 citation is
  to the byte shape only, and this round adds the runtime witness explicitly.
