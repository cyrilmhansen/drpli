# E2E-11 step 1a — BIT(1), STATIC and INITIAL implemented (340/340 byte-exact, negatives 64/64)

## What is now in the compiler

**BIT(1)** — new `Vbit1` vkind, one byte, significant in bit 7:

```
dcl f bit(1)                     1-byte cell  [E20A]
f = '1'b;                       LXI H,f / MVI M,80
f = '0'b;                       LXI H,f / MVI M,00
if f = '0'b then ...            LDA f / ANI 80 / JNZ skip        [E21A, E11D]
if f = '1'b then ...            LDA f / ANI 80 / SUI 80 / JNZ skip [E20B, E21A]
```

The bit arm is matched **before** the fixed/decimal ladders on purpose. A bit
cell is 1 byte and the generic 1-byte-zero test reads it with `LHLD` (2 bytes),
so falling through would emit self-consistent but wrong bytes — the R3037 class
of error, avoided by ordering rather than by a runtime check.

**STATIC / INITIAL** — codegen adds the static total to the pool base and seeds
the initialiser bytes as data blocks at their absolute addresses. `bind.ml`
already keeps a separate static offset counter (`soff`) and flags each row
`auto = not stc`, which is DR's single `[statics][literal pool][automatics]`
DATA area (C114) with nothing re-derived. The existing per-block
`SET-LC(data,addr)` emission [G113] then reproduces DR's segment shape
unchanged: a static cell at S(0000) rides the header `SET-LC(data,0)`, and a
literal that follows gets its own `SET-LC(data,1)` — exactly what E20B's `.REL`
contains.

Scope is deliberately narrow: explicit `STATIC` accepted on `BIT(1)` only;
`'0'b`/`'1'b` initialisers only; a static-class row that is not an explicit
static (FILE/FORMAT/ENTRY — bind's `stc` is broader than the attribute)
declared alongside a static bit cell refuses, because that mixture would shift
my cell and DR has never shown it.

## New byte-exact specimens (7 this slice)

| specimen | what it pins |
|---|---|
| E20A | bit(1) store both literals, `if f='0'b` two-way |
| E21A | one cell, both comparison forms, both branches |
| E21B | both `if/else` shapes in one program |
| E20B | static cell at S(0000), literal pushed to S(0001), pool base shift |
| E20D | `'0'b` initialiser byte is `0x00`, auto above pool |
| E20E | two statics at S(0000)/S(0001), three autos at A(0004)+, DATA 0009 |
| **E11D** | **12 static cells + 4 automatics, both test forms, two-way `if/else`, `n = n + 2`, DATA 0015** |

E11D is the one that makes me trust the model rather than a couple of lucky
samples: it is the only bit(1) program in the tree that is entirely independent
of FILE, and its listing interleaves statics with automatics (`s1@S(0000) s2@S
(0001) w1@A(0002) a1@S(0004) s3@S(0005) ... w2@A(000C) w3@A(000E) n@A(000F)`).
Getting that byte-exact means both the ordering law and the relocation shape are
right.

## Corrections to claims I made yesterday

**The constant-bias ladder was far broader than I recorded.** My previous note
claimed INX/DCX for biases 1-3 and LXI B/DAD B from 4, "pinned at 4/5/9/30/200"
— but 200/250/280/290/300 were *operand-derived*, not constant-derived, so they
said nothing about the constant path. Live sweep (spec/e2e11-ladder.txt):

```
|bias| 1,2,3            INX H ×|b| / DCX H ×|b|
|bias| 4..32767         LXI B, b mod 65536 / DAD B     (two's complement!)
bias 0, |bias| > 32767  no byte-level sample -> refuses
```

`+2` was the single value where my old model was wrong, and `v = v + K` is the
most common arithmetic statement in this corpus. N20_DOWILE was retired on
contact: R3105 (`n = n + 2;`) is byte-exact, and holding a negative whose subject
DR proves compilable would be asserting a defect.

**I never should have written the bit-store note as I did.** My first draft of
this slice recorded DR's store as `MVI A,80` / `MVI M,A` / `STA` — invented from
generic 8080 habits, not from the listing. The real form is `LXI H,c` / `MVI M,80`
(one fewer instruction), and the real comparison forms load the cell (`LDA`), they
do not copy it (`MOV M,A`). Corrected before any code was written from it, but the
draft was wrong in the way that matters most: confidently.

**`Ast.block.bdecls` is always empty** (C116) and reading it is how I "implemented"
the INITIAL-without-STATIC rule while it silently never fired: I wired the rule to
`b.bdecls`, E20C compiled, and the attribute list was empty. The parser routes every
declaration into `bstmts` as `Sdcl` [parser.ml:760, 1089]. This is a false-capability
hole with a clean surface — no crash, no warning, just a rule that does nothing.

**DR rejects multi-bit bit-string literals** (C117). `b = '10101'b;` is a pass-1
SYNTAX error with no `.REL`, while `dcl b bit(5);` and `b = c;` compile fine. So the
wide-bit perimeter is cell layout and copy lowering, not literal syntax.

## Where I started wrong, caught by the harness

**My `x = x + 0` refusal rested on a false claim about DR.** I wrote into a refusal
message that DR rejects the statement ("P044 line 5: DR SYNTAX") and kept a negative
panel entry (N56) asserting it. DR compiles `a = a + 0;` without complaint — as
`LHLD A / SHLD A`, byte-identical to its `.REL` for `a = a;` [golden/e2e11v/T5 vs T6].
Four probe groups later (T5-T13) the real law is precise: a literal zero added or
subtracted against a **variable** disappears, from either side, nested forms included;
against a **literal** it does not (`b = 5 + 0` takes the decimal pool path,
?DLDOP/?DADOP/?QDI15 [T11]). Eight new byte-exact specimens; N56 retired. That is the
N63-N66 failure mode for the third time, and worse than the others because the
invented DR rule had been written into the compiler's own diagnostic, where it reads
as evidence to whoever hits it.

**Two of my own edits never ran, and I tested them as though they had.** Each time I
read `dune build` output that led with pre-existing warnings, saw no error in the
first lines, and went straight to byte comparison — against a STALE binary. The real
failures were `Unbound value only_literals` (a helper recursing into its own body
without `let rec`) and `Unbound constructor Ast.Eunop` (the AST spells it `Eprefix`).
The symptom was genuinely confusing: correct-looking code, edit in the right arm,
absolutely no behavioural change. From here on my own testing is gated on
`dune build && echo BUILD OK`.

Also in this slice: I replaced the FLOAT comparison arm instead of adding a sibling
before it, and three goldens (R3045, R3077, R3098) came back `COMPILE-FAIL` with an
`int_of_string "2.5"` crash; a redundant bit arm shadowed that branch; and an
unbound `e` in my own refusal path made four programs raise `Match_failure` instead
of refusing cleanly. None of that reached a commit. The gate caught all of it in one
run, which is the argument for running it after every edit rather than at the end.

## Status

- gate: **348 byte-exact / 0 fail / 0 skip**, negative panel **63/63 refused**
  (N20 and N56 retired — both retired on DR evidence that the construct compiles;
  N74-N78 added, N78 agrees with DR and N74-N77 are perimeter refusals whose DR
  goldens live in `golden/e2e11u/T1..T4`, `e2e11v`, `e2e11w` as acceptance tests for
  later slices).  T5-T10, T12, T13 added as zero-elision positives.
- corpus: unchanged at **9/41 EXACT, 0 DIFFERS** — expected, since nothing in the
  corpus uses `bit(1)`
- FLTPOLY2's first blocker is now exactly what the step-0 audit predicted: `FILE`
  (`FSCAN`/`LOAN2` now fail earlier, on `STATIC on CHAR(80) VARYING`, which is a
  strictly louder refusal than the silent ignore that used to swallow it)

## Next

Step 2 is FILE + `ON ENDFILE` for SYSIN only, acceptance target FLTPOLY2 — the 10th
corpus program. Requirements are all measured (C109-C111): the 6-byte condition
control block, `?ONCOP` registration, the `LXI D,0290 / CALL ?SYSIN` GET form, and
C110's semantic contract (handler runs once, interrupted GET **completes unassigned**,
control to the next statement). That last point is the risk: a re-entry or
skip-the-PUT implementation can match bytes while behaving wrongly, so acceptance
must include linked COM identity and console equality, not just `.REL`.
