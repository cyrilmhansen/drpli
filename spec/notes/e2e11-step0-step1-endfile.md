# E2E-11 steps 0-1 — blocker-SET audit, and ON ENDFILE learned from DR

Date: 2026-10-19.  Build at start: `203bf1e`, gate 289/289 byte-exact,
negative panel 58/58, corpus 9/41 EXACT / 0 DIFFERS / 32 REFUSED.

Two pieces of work, in the order the user specified: a **complete dependency
audit** (not a first-blocker ranking), then a **targeted DR-oracle investigation
of `ON ENDFILE(SYSIN)`**.  The audit tool and the run driver are new and are
part of the deliverable.  Everything below is measured; the places where I
initially got it wrong are recorded too, because three of my own shortcuts were
wrong in ways that would have silently corrupted later work.

---

## 1. The audit: `pli80deps` + `tools/blocker_audit.py`

`ocaml/bin/pli80deps.exe` walks the parsed AST **and the bound storage rows**
and emits every feature tag a program touches, with a count and first line.
`tools/blocker_audit.py` runs it over all 41 corpus programs that have a DR
`.REL`, then subtracts a capability baseline.

Two deliberate design decisions, both of which I got wrong on the first draft:

* **The baseline is derived, never asserted.**  A tag counts as supported only
  if some specimen that reproduces DR byte-for-byte today contains it — the 9
  accepted corpus programs *plus every gate positive, corpus or probe*, each
  re-verified by compiling and comparing right now, not assumed.  My first
  draft carried a hand-written `NEUTRAL` list of tags I judged harmless; that
  is the same "rank by what I checked first" error this exercise exists to
  remove, so it is gone and the comment says why.
* **Restricting the baseline to corpus programs is also wrong.**  It reported
  `CALL_STMT` as unsupported-in-23-programs while my build already reproduces
  DR's internal-call lowering byte-exactly on P401/P402/IADD.  Those probes are
  expression-form calls, so the tag still stands for the *statement* form — but
  the point is that capability must be read off all evidence, not a sample.

### What the audit actually says

Complete blocker sets (first-blocker ranking is in `corpus-audit-2026-10.md`;
this is the corrected view):

| programs | set |
|---|---|
| `FDTEST` | ENTRY only |
| `ACK` | `OPTIONS(STACK)` + generated PUT item |
| `DTEST` | CALL statement + ENTRY |
| `LABELS` | array + CALL + `goto L(i)` + LABEL-as-data |
| `REVERT` | CALL + FILE + LABEL-as-data + ON ENDFILE |
| **`FLTPOLY2`** | **BIT(1) + FILE + STATIC + INITIAL + ON ENDFILE** |
| `EXPR1` | exp + CALL + FILE + ON ENDFILE + ON ERROR + SIGNAL ERROR |
| big ones | 11-19 tags each (`MPMCALLA` 19, `LOAN2` 18, `COPYLPT` 17) |

Payoff ranking (programs still needing the kind):

```
CALL_STMT        23   <-- unimplemented, and structurally ~done
FILE_DECL        17
STATIC_ATTR      15   } INITIAL_ATTR co-occurs with STATIC in 14
INITIAL_ATTR     14   }  -> one language feature, not two
BIT_DECL         12
STRUCTURE_LEVEL  11
FILE_STMT:open   10   } always with FILE_DECL (10) and IO_OPT:file (10)
GOTO             10      -> OPEN is the expensive part of a FILE program
ENTRY_DECL        8
ON_COND:endfile   8   <-> FILE_DECL in 8: in this corpus they never separate
POINTER_DECL      7
```

Three corrections to the previous scoping note follow directly:

1. **`CALL statement` is the #1 blocker (23 programs) and I never noticed**,
   because it is rarely the *first* refusal — `codegen.ml` refuses it at
   `Ast.Sprocedure_stmt` only after declarations pass.  `DTEST` proves this:
   its first blocker looked like ENTRY, its real set is `CALL + ENTRY`.
2. **`STATIC` + `INITIAL` are one feature** (14/15 co-occurrence) and
   **`FILE` + `ON ENDFILE` are one feature *in this corpus*** (8/8), which is an
   observation about the programs, not a law about PL/I.
3. **No program is closable by FILE alone**, and only `FDTEST` is closable by
   anything alone (ENTRY).  So "implement FILE, harvest the corpus" is false;
   the FILE cluster plus `open` plus static/initial/bit plus the CALL statement
   is what 17 of the 32 need, and every one of them also needs at least one of
   structures/pointers/VARYING.

`FLTPOLY2` remains the right near-term target, and the audit now states its
complete requirement set rather than my guess: two clusters,
`{BIT(1) + STATIC INITIAL}` and `{FILE + ON ENDFILE}` — nothing else.  It does
not need `open`, structures, pointers, VARYING, ENTRY or `CALL`.

`REVERT` is confirmed as a poor target: `CALL` + `LABEL`-as-data + `GOTO`
alongside FILE.  It stays useful as oracle evidence only.

One gap in the method is recorded rather than hidden: program `A` has an
**empty** blocker set yet still refuses, because a float→fixed store carries no
declaration tag.  The tool cross-checks each set against the compiler's own
first refusal and labels such cases `TAG-BLIND`; route-level gaps (conversions,
peephole decisions) are invisible to a declaration/statement walk by
construction.

---

## 2. DR does not support FIXED precision above 15 — and I did

Finding by accident, then chased down: **all six of my ENDFILE specimens failed
DR compilation**, including the two-line control.  Cause: I wrote
`dcl a fixed bin(31)`.

Live probe (`golden/e2e11f`, one program per precision, `fixed bin(p)` with an
assignment and a PUT):

```
bin:  p=15 ok      p=16,17,23,24,30,31,32 -> "NOT IMP", no .REL
dec:  p=9,15 ok    p=16,31                -> "NOT IMP", no .REL
```

So **PL/I-80 V1.4 caps FIXED BINARY and FIXED DECIMAL at p=15**.  `NOT IMP` is
DR's own diagnostic and it is fatal — no `.REL` is produced.

This is **not a new discovery, and I must not record it as one.**  `PERIMETER.md`
already carries a row — "FIXED BINARY(p) with p>15 | **NOT IMP** at dcl (P068
L-series sweep: 15 ok / 16..32 fail)".  What I found is that **that evidence no
longer exists**: `golden/probe27/P068A/`, `golden/probe28/P068C*/` and the rest
of the P068 set contain a single `dir.txt` each, no listing and no `.REL`, and
none of them is referenced by the gate.  The only surviving `NOT IMP` listings in
the tree are today's.  So the limit had been observed once, was written down, and
was then unverifiable — which is precisely how the `bind.ml` comment came to
describe a 16/24/32-bit storage ladder for types DR will not compile.  E14xx /
E15Dxx re-establish the boundary from primary evidence, and that is the claim's
new standing.

Why the enforcement gap mattered: my compiler accepted `bin(31)` and `dec(31)`.
That is a false capability on the *permissive* side, the dangerous direction — I
would emit bytes for a program DR refuses outright, and since DR never produced a
`.REL` there is nothing to compare them against, so the divergence is
undetectable by construction.  Nothing in the 289 goldens uses
`FIXED` above 15 (checked: the only >15 precisions anywhere in the corpus and
my probes are `FLOAT BINARY(24)`, a different type), so no existing evidence is
invalidated — but the hole was real.

Two things found while verifying the fix:

* **`bind.ml` cited "PROVEN [P063A $S ladder]" for the byte rule, including
  rows `16/17->3`, `24->4`, `32->5`.**  `golden/probe18/P063A/` contains a
  directory listing showing `p063a.pli` and **no `p063a.rel`**, and the source
  file no longer exists in the tree.  The claim was unverifiable, and its
  p>15 rows were extrapolation from a program DR will not compile.  I
  re-derived the ladder from a live specimen instead: `E19A` declares
  `fixed bin(1)..bin(15)` and `fixed dec(1)..dec(15)` in order and stores to
  each; DR's listing offsets give, exactly,
  `bin: p<=7 -> 1 byte (STA), 8<=p<=15 -> 2 bytes (SHLD)` and
  `dec: 1->1, 2..3->2, 4..5->3, 6..7->4, 8..9->5, 10..11->6, 12..13->7,
  14..15->8`.  Both agree with the formulas already in use (`(p+8)/8`,
  `(p+2)/2`) for every p DR accepts, so no sizing changes.
* **`N24_BIGIN` and `N27_DECBIGP` already existed** as negatives for `bin(16)`
  and `dec(20)`, refused by a codegen-time guard.  So the limit was known and
  tested — but enforced only where certain use paths reached that match arm,
  which is why a precision-overflowing declaration that binds without being used
  in that shape could still reach output.  I moved the
  refusal to `bind` (`check_fixed_prec`), which is the earliest point the
  precision is known and is unconditional, quoting DR's wording, and updated
  the two markers to the unified message.  `N72`/`N73` cover `bin(31)`/`dec(16)`
  so the whole refused range is pinned.

Gate contract note, since it cost me three cycles: `run_negatives()` requires
the **literal string `[TBD]`** in stderr.  `[TBD: reason]` does not contain it.

Status after the change: **289/289 byte-exact, 60/60 negatives, 9/41 corpus,
0 DIFFERS** — nothing moved except the two added negatives.

---

## 3. ON ENDFILE — the code shape (`?ONCOP`)

Compile-tier specimens, `golden/e2e11g` (SYSIN) and `golden/e2e11i` (named
file).  `E11A`/`E11C`/`E17A`:

```
on endfile(sysin) put list('HANDLED');
   LXI  H,SYSIN          ; the file's control block  (relocated symbol)
   MVI  A,05             ; condition number 5 = ENDFILE
   CALL ?ONCOP           ; register
   JMP  <past the unit>
<unit body, inline>
   RET                   ; the ON-unit is a subroutine
```

The registration is three instructions, the handler is emitted **inline
immediately after the registration and skipped by a `JMP`**, and it ends with a
`RET` — the runtime calls it as a subroutine.  The same shape appears for a
`BEGIN`-block body (`E11C`, `E17A`), so the body form does not matter.

Storage: `dcl sysin file;` occupies **no data storage** (`E11E`: `dcl sysin
file; dcl a fixed bin(15);` puts `a` at 0x0009 with no gap), because SYSIN's
control block is PLILIB's shared object at TPA 0x0290.  A user `dcl inf file;`
**does** get its own control block in the program's data area (`LXI H,INF` is a
relocated local symbol).  `E11C`'s `DATA AREA = 0009` decomposes exactly as
6 bytes for the ON registration + 1 for `efile` + 2 for `x`, so the condition
registration costs six bytes.

GET sequences, side by side (`E11E` vs `E17A`):

```
get list(x);              -- SYSIN
   LXI D,0290             ; SYSIN control block
   LXI B,0000             ; options word
   CALL ?SYSIN
   CALL ?GNVOP            ; DEC reader (same as E2E-7A slice 4)
   JP   <fail>            ; operand patched by the listing's '==== ' fixup
   CALL ?QCIOP            ; complete input
   SHLD X A(0007)
   <fail>: CALL ?QIOOP

get file(inf) list(x);    -- named stream file
   LXI H,INF              ; this file's own control block
   LXI D,0690             ; its attribute block
   LXI B,0000
   CALL ?SIOOP            ; stream io op   (SYSIN uses ?SYSIN)
   CALL ?GNVOP            ; <-- identical from here down
   ...
```

`open file(inf) stream title('$1.$1')` compiles to: `?SLCTS` of the title
literal, then a fixed argument block pushed on the stack (`MOV B,A / PUSH B /
INX SP / LXI H,0E90 / PUSH H` ×6), then `LXI H,INF` + **`CALL ?OIOOP`**.  The
6-word push block is the same 0x0E90 constant seen in the runtime's traceback
recent-op words.

---

## 4. ON ENDFILE — the semantics, observed not inferred

The user's instruction was explicit: do **not** extend C102 (arithmetic
conditions are terminal) to ENDFILE; establish ENDFILE separately.  Two
runtime-tier controls do it, both reading a staged disk file containing three
numbers, with **four** GETs so EOF is actually reached:

`E18A` — no ON unit at all:

```
X1=         7 X2=         8 X3=         9
END OF FILE (1), File: INF=INF.DAT
Traceback: 08BE 0869 01E9 3900 # 0802 04B0 8082 01E9
```

**Unhandled ENDFILE is terminal** — DR raises the condition, prints
`END OF FILE (1), File: <variable>=<resolved name>` and a traceback, and the
activation dies.  So the outcome happens to agree with C102, but that is now
observation, not analogy, and the message text is file-specific (it names the
variable and the resolved filename), which C102's arithmetic traceback does not
do.

`E18B` — `on endfile(inf) put list('HANDLED');`, same input, same four GETs:

```
X1=         7 X2=         8 X3=         9 HANDLED X4=         9 END
```

The handler ran **exactly once**, then the interrupted GET **completed without
assigning** — `X4` still holds the previous value 9 — and control continued with
the *next* statement.  It did not re-enter the GET, and it did not terminate.

`E17A` is the same mechanism seen through the loop the corpus actually uses:

```
X=7  X=8  X=9  X=9  DONE
```

The duplicated `X=9` is the signature: EOF → handler sets the flag → GET
returns leaving `x` at 9 → the PUT in the loop body executes anyway → the loop
test sees the flag → exit → `DONE`.  **This is the behaviour `FLTPOLY2` depends
on, and it means FLTPOLY2's own output repeats its last value.**

`E11A`/`E11C` establish the same semantics for **SYSIN** rather than by
transfer, which is what the user asked for specifically:

```
E11A:  ^Z -> HANDLED  A=  0  AFTER      (handler once; get completes; continue)
E11C:  7 -> X=7, 8 -> X=8, ^Z -> X=8 DONE   (loop exits, flag set, last value
                                             printed twice)
```

Note `A=0` in E11A: an unassigned local cell reads as zero, which is consistent
with DR zero-filling the data area — already assumed by my static/pool layout.

The `do while(f = '0'b)` test itself lowers as `LDA cell / ANI 80 / JNZ <exit>`,
i.e. DR evaluates the condition and jumps out when true-to-exit, matching the
negated-condition pattern I already use.

---

## 5. BIT(1) and STATIC INITIAL are an independent capability

`E11D` contains no FILE, no ON-unit, no stream I/O — only `bit(1)` storage,
`static initial('0'b)`, bit literals and comparisons.  DR compiles it and the
linked program runs to completion:

```
N=         3
```

`N=3` is the whole point: `f` really was initialised to `'0'b` at entry (the
`f = '0'b` branch ran, `n = 1`), `g = '1'b` worked (`+2`), and the
`f = '1'b` test correctly did *not* fire.  So `BIT(1)` storage plus
`STATIC INITIAL` is its own small capability and should not be bundled into the
FILE milestone — the user's suspicion was right.

Its lowering is unusually cheap, straight from `E11C`/`E17A`:

```
efile = '1'b;      LXI H,EOFLAG S(0000) / MVI M,80     ; 1 byte, HIGH-BIT justified
                  (value is 0x80 for '1'b, 0x00 for '0'b)
efile = '0'b       LDA EOFLAG S(0000) / ANI 80 / JNZ ..
```

So bit(1) is one byte, significant in bit 7, compared by `ANI 80` and a
conditional jump — nothing shared with the FILE machinery.  (`bit(16)` and wide
bit strings are a different question and remain unprobed.)

---

## 6. Oracle harness: what real FILE I/O actually needs

Assessment against the existing `oracle/` stack, per the user's item 6.  The
answer is "small extensions, not a new system" — `cpmwork` already had
`import_local` and `export`, and `cpmtools` (`cpmcp`/`cpmls`) is present, so the
gap was that the run stage never used them.

Landed in `oracle/linkrun.py`:

* `STAGE_IN` — per-program input files imported into the run's scratch `D:`
  before the program starts.
* `EXPORT_OUT` — post-run file capture into the golden dir, **plus a directory
  dump when a capture finds nothing**, so a missing file is never mistaken for
  a program that wrote nothing.
* `ARGS` — per-program command tail (see the naming rule below), and the
  transcript anchor now tolerates it.  Without that tolerance every tailed run
  produced an *empty* output file, which looks exactly like a silent program —
  the second-most-dangerous failure mode in this project after a wrong byte.

Three hard-won rules, all measured:

1. **SYSIN EOF needs `^Z` followed by CR.**  A bare `\x1a` in the console script
   is consumed by CP/M's own command-line read; the program then blocks on
   CONIN and the run times out with no output — indistinguishable from a
   program that printed nothing.  With `"\x1a\r"`, `E11A`/`E11C` behaved
   exactly as designed.  This is why the `INPUTS` entries end `^Z\r`.  (The
   harness default for every other program is still a bare `\x1a`, so any
   historical "clean EOF" reading in an old transcript deserves re-examination;
   `R907`, my only prior immediate-EOF GET probe, exists in the compile tier
   only and was never run.)
2. **Stream-file naming.**  `open file(inf) stream title('E16IN DAT')` was
   **ignored**: DR built the FCB from the FILE *variable's own name* and
   reported `File: INF=NUL`.  `title('$1.$1')` takes the name from the command
   tail, but DR splits the tail at the first **space** into name and extension,
   so `E17D OUT DAT` created a CP/M file literally named `out` and
   `E17A INF DAT` never found `INF.DAT`.  A single **dotted** token
   (`E17A INF.DAT`) is what works, and then DR reports `File: INF=INF.DAT`.
3. **Output files are record-padded.**  `E17D`'s captured `OUT.DAT` is 128
   bytes: `'HELLO'    42` then `^Z` fill.  List-directed output quotes
   character constants and right-justifies numbers, and the file length is a
   whole 128-byte record, not the payload length.  Any byte-exact output-file
   comparison must reproduce the padding, or it compares nothing meaningful.

Consequence for acceptance: **byte-exact `.REL` remains the criterion and is
unaffected** — FILE work can proceed on the compile tier, where I already have
`?ONCOP`/`?OIOOP`/`?SIOOP`/`?SYSIN` shapes.  Runtime FILE evidence is now
obtainable too, which it was not before this session, but output-file
comparison is a *separate* class of evidence from console-transcript matching
and must be registered as such (different artifact, different padding rules)
rather than folded into the existing panel.

---

## 7. Revised E2E-11 sequence

Ordered by the audit's dependency sets, keeping independent features separate:

* **Step 1a — BIT(1) + `STATIC INITIAL`** (independent, 12 programs; ~4
  instructions per use: one-byte high-bit cell, `MVI M,80` store, `ANI 80` +
  conditional jump test).  Acceptance: byte-exact `E11D`, `E11C`-minus-FILE,
  and the `INITIAL`/`STATIC` data-zeroing rule they demonstrate.
* **Step 1b — `FIXED` precision ceiling** — done this session (`check_fixed_prec`,
  `N72`/`N73`, re-derived ladder).
* **Step 2 — FILE declaration + `ON ENDFILE`, SYSIN-only.**  Needs: the
  6-byte condition control block, `LXI H,<cb> / MVI A,05 / CALL ?ONCOP / JMP /
  unit / RET`, `LXI D,0290 / LXI B,0000 / CALL ?SYSIN` GET form, and the
  terminal-unhandled path.  **Acceptance target: `FLTPOLY2`** (10th corpus
  program; its complete requirement set is now known to be exactly steps 1a
  and 2).  `E11A`/`E11C`/`E11E` are its byte-exact specimens.
* **Step 3 — named stream files: `open`/`get file`/`put file`/`close`.**
  Needs `?OIOOP`'s argument block, per-FILE control blocks and `?SIOOP`.
  Acceptance: `E17A`/`E17B`/`E17C`/`E18A`/`E18B` byte-exact.  This is the step
  that moves the 10 FILE+`open` programs from "unreachable" to "missing one or
  two other kinds" — it does not by itself accept any of them.
* **Step 4 — `CALL` statement** (23 programs, #1 by payoff, and closest to
  machinery I already have: descriptor block + RSBLK/SVBLK proven byte-exact on
  P401/IADD/DECPOLY).  It accepts `DTEST` only jointly with ENTRY, so its value
  is measured in unblocked programs, not in an immediate acceptance — worth
  probing against `E17D`-style specimens for whether DR lowers a
  *function-call-as-statement* differently (discarding the return).
* Deferred, each independently unattractive: LABEL-as-data + `goto L(i)`
  (`LABELS`, `REVERT`), POINTER/BASED/ALLOCATE (`REVERSE`, `NETWORK`, DIO*),
  structures (11 programs), ENTRY (8), PICTURE/FORMAT edit-directed output
  (15 programs and a completely separate runtime).

## 8. Principal risks

1. **The resumption semantics are now load-bearing.**  My GET lowering must
   *complete* the interrupted statement — return to the next statement with the
   list items unassigned — not re-enter it and not skip its following PUT.  The
   duplicated-value transcripts are the observable; if I get the return path
   wrong the bytes may still match while the runtime behaviour does not.
2. **Six bytes per ENDFILE registration is inferred from one decomposition**
   (`E11C`: 9 = 6 + 1 + 2).  Two conditions, or `ON ERROR` alongside, will not
   necessarily be 6+6.  Probe before trusting it.
3. **`MVI M,80` vs `LDA/ANI 80`** shows bit(1) *store* going through
   `LXI H,cell` while *test* uses `LDA cell`; whether DR picks `LXI H`+`MVI M`
   versus `MVI A,80 / STA` depends on context I have not sampled (assignment to
   a bit variable only so far).  Arrays/structures/subscripted bit refs unknown.
4. **Console-EOF fragility.**  If `^Z\r` proves unreliable in some program
   shape, the failure mode is a silent empty transcript that reads as "no
   output" — the trap I fell into with the ARGS anchor.  Runtime ENDFILE
   evidence should come from staged files where possible.
5. **The `title`/FCB naming rules were derived from four specimens of one
   program family.**  `IO_OPT:title` appears in 6 corpus programs with
   environment options (`b(8192)` buffers) I have not probed at all.
6. **Output-file acceptance has no precedent in the gate.**  Its padding and
   record rules are new evidence classes; adding them must not blur the
   `.REL` byte-parity rule that everything else rests on.

## Artifacts added

`ocaml/bin/pli80deps.ml` (+ dune entry), `tools/blocker_audit.py`,
`build/mk_e11_probes.py`, `e13src/E11[A-F].PLI`, `e13src/E1[6-9]?[A-D].PLI`,
`e13dat/INF.DAT`, `golden/e2e11{a..k}` (compile tier), `golden/e2e11{gh,hu,iu}`
and `e2e11{gr,hs,is,it,jr,gs}` (link/run tiers), `oracle/linkrun.py`
(`STAGE_IN`, `EXPORT_OUT`, `ARGS`, tolerant transcript anchor, ENDFILE input
scripts), `ocaml/lib/bind.ml` (`check_fixed_prec`, corrected ladder comment),
`tools/e2e_gate.py` (`N72`, `N73`, unified markers).

Raw audit output is banked at `spec/notes/e2e11-step0-blocker-audit-data.txt`.
