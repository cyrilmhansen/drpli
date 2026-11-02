# fc01-framing — pre-registered hypotheses (written and committed BEFORE any oracle call)

Mission (FC-01, hop: Batch-A Lane-B ASSERT framing failures). The first Batch-A run of the
eight FC-01 corpus programs (`build/fc01/batchA`, 2026-11-02) failed ASSERT on all eight with
two stream-framing artifacts:

1. **Leading blank line** — every corpus program whose first executed output statement carries
   a SKIP captures `\r\n` at stream start. This shape is ALREADY oracle-measured on both sides:
   `golden/e29rt_dr_r/E29PS1.output.txt` and `golden/e29rt_my_r/E29PS1.output.txt` are both
   `\nafter=\n` (bare `PUT SKIP;` first prints a leading newline). The artifact is DR behaviour;
   the Batch-A `expected.console` lists simply omitted it. No oracle call is needed for (1).
2. **Trailing blank line after a final bare `PUT SKIP;`** — MATH-00 (only program whose LAST
   executed output statement is `put skip;`) captured a stream ending `\r\n\r\n`. The stored
   DR-side goldens that end `\n\n` (`golden/run1/A|FSCAN|NETWORK`, `golden/run2/DECPOLY|FLTPOLY`,
   `golden/e29*_REVERSE`) are all contaminated: GET input lines contribute TWO extra newlines
   (echo CR→CRLF plus a GET terminator newline — visible mid-stream in
   `golden/e29dr_runB/REVERSE.output.txt`) or the file includes the prompt (`run1/A` contains
   `D>`), so none isolates exit framing. **UNMEASURED shape**: pure-PUT program, final executed
   output statement = bare `PUT SKIP;`, then `STOP`.

## Probes (probes/FCPS1.PLI FCPS2.PLI FCPS3.PLI — CRLF, ^Z, <=71 cols, pure console PUT)

| probe | shape | purpose |
|-------|-------|---------|
| FCPS1 | `put list('X=', x); put skip; stop;` | trailing framing under H1 vs H2 |
| FCPS2 | `put list('Y=', y); stop;` (unterminated) | control: must equal `Y= 2` + one final `\n` on both sides (measured E32B1 law); a deviation invalidates the capture law |
| FCPS3 | `put skip list('L=', l); put list('M=', m); stop;` | confirms the leading-blank law for the `PUT SKIP LIST` spelling on the DR side (Batch-A shape) |

## Hypotheses (DR console region, per oracle/linkrun.py capture law: `\r\n?` → `\n`, program
region only, prompt excluded)

- **H1 — unconditional exit CRLF**: PLILIB emits exactly one final newline at program exit
  regardless of line state. Predictions:
  - FCPS1 → `X= 1\n\n`
  - FCPS2 → `Y= 2\n`
  - FCPS3 → `\nL= 1\nM= 2\n`
  If H1 holds, MATH-00's captured trailing blank line is DR behaviour; the defect is in my
  spec expectations (reference derivations must model the framing law).
- **H2 — conditional exit flush (unterminated line only)**: predictions:
  - FCPS1 → `X= 1\n`  (the explicit SKIP already terminated the line)
  - FCPS2 → `Y= 2\n`
  - FCPS3 → `\nL= 1\nM= 2\n`
  If H2 holds and my side prints `X= 1\n\n`, the extra CRLF is a **my-gap** (in my `.REL`'s
  exit/skip lowering — PLILIB itself is shared, so the difference must be in the object).

## Second discriminator (recorded either way)

Whole-file byte comparison DR FCPS1/2/3 `.REL` vs my `.REL` (PROTOCOL #6 — complete objects,
sizes read from the objects). If a probe's objects are byte-identical, the `.COM`s and hence the
console streams are identical BY CONSTRUCTION and that probe cannot discriminate; FCPS1 is
expected to be the discriminating object.

## Classification discipline

Any DR refusal (`DR PLI.COM rejects FCPSn`) is `dr-refuses` evidence for that shape and will be
kept verbatim. No rule may be declared from absence of evidence; until this round lands, the
trailing-skip law stays **unmeasured** and the Batch-A expectations stay WRONG-but-unclassified
(no laundering: the FAILs stay on record).
