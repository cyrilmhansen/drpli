# E2E-42 / P2c — RESULTS: the named-file SKIP, measured, predicted, and lowered

Written AFTER the oracle ran.  Every prediction scored here was committed in `de6ff2f`
("E2E-42/P2c: pre-registration — 23 probes, the cost model, and every prediction, committed BEFORE
DR is run"), and the file that holds them has not been edited since:

```
$ git log --format='%h %ad %s' --date=iso -3
de6ff2f 2026-10-28 ...: E2E-42/P2c: pre-registration — 23 probes ... BEFORE DR is run
51ea50d 2026-10-28 ...: E2E-42/P2b-F: ...
16b1ffd 2026-10-28 ...: E2E-42/P2b: ...
$ git diff de6ff2f HEAD -- spec/lab-evidence/e2e42-p2c/HYPOTHESES.md      # empty
```

The ordering is proved the way P2b proved it — a committed blob, not a filesystem mtime, which is
the thing that made P2a's claim unrecoverable (`e2e42-p2a/PROCESS.md`).

## 1. Prediction versus verdict

DR's sizes below are read out of each `.REL`'s own segment records via
`spec/lab-evidence/e2e42-p2b/chaindump.py`.  **They are not parsed from the `.PRN`.**  My first
attempt at this table did parse the `.PRN`, which prints `CODE SIZE = 0056`, and read it as
decimal-56 instead of hex-86; that produced a comparison where every size disagreed and every
verdict read "refused", and it is the same class of error as [C264] — treating a rendering as the
authority when the artifact itself is right there.  The `.PRN` header is quoted nowhere below.

| probe | pre-registered | DR `.REL` | verdict | my object | whole file |
|---|---|---|---|---|---|
| E46N1  | accept  64 /  9 |  64 /  9 | HIT |  64 /  9 | **byte-exact** |
| E46N2  | accept  75 / 10 |  75 / 10 | HIT |  75 / 10 | **byte-exact** |
| E46N3  | accept  73 / 30 |  73 / 30 | HIT |  73 / 30 | **byte-exact** |
| E46N4  | accept  86 / 11 |  86 / 11 | HIT |  86 / 11 | **byte-exact** |
| E46N5  | accept  84 /  9 |  84 /  9 | HIT |  84 /  9 | **byte-exact** |
| E46N6  | accept  90 / 10 |  90 / 10 | HIT |  90 / 10 | **byte-exact** |
| E46N7  | accept  90 / 10 |  90 / 10 | HIT |  90 / 10 | **byte-exact** |
| E46N8  | accept  81 /  9 |  81 /  9 | HIT |  81 /  9 | **byte-exact** |
| E46N9  | accept  64 /  9 |  64 /  9 | HIT |  64 /  9 | **byte-exact** |
| E46N10 | accept  62 /  9 |  62 / 10 | **MISS (data +1)** | refused | — |
| E46N11 | accept 116 / 12 | 116 / 12 | HIT | 116 / 12 | **byte-exact** |
| E46N12 | accept  90 / 11 |  90 / 11 | HIT |  90 / 11 | **byte-exact** |
| E46N13 | accept  75 / 13 |  75 / 13 | HIT |  75 / 13 | **byte-exact** |
| E46N14 | accept 156 / 12 | 156 / 12 | HIT | 156 / 12 | **byte-exact** |
| E46N15 | accept 162 / 20 | 162 / 20 | HIT | 162 / 20 | **byte-exact** |
| E46N16 | accept  96 / 12 |  96 / 12 | HIT |  96 / 12 | **byte-exact** |
| E46N17 | accept 193 /124 | 193 /124 | HIT | 193 /124 | **byte-exact** |
| E46N18 | accept  72 / 12 |  72 / 12 | HIT |  72 / 12 | **byte-exact** |
| E46N19 | accept  81 / 26 |  81 / 26 | HIT |  81 / 26 | **byte-exact** |
| E46N20 | **refused** (which refusal not predicted) | no `.REL` | **HIT — `UNEXPECTED EOF`, as one of the two named candidates** | 81 / 26 | n/a |
| E46N21 | accept (DR accepts) | no `.REL` | **DR REFUSED — `SYNTAX ?`, pass 2** | refused | n/a |
| E46N22 | accept (DR accepts) | no `.REL` | **DR REFUSED — `SYNTAX ?`, pass 2** | refused (parser) | n/a |
| E46N23 | accept (DR accepts) | no `.REL` | **DR REFUSED — `SYNTAX ?`, pass 2** | refused (parser) | n/a |

**18 of 19 size predictions HIT, 1 MISS.  17 of 17 accepted probes are whole-file byte-identical to
DR.**  Three of the four DR-verdict predictions for E46N21–N23 were WRONG, and all three were wrong in
the same direction — I predicted DR would accept, DR refused.  `E46N20`'s verdict prediction HIT.  §4
takes that apart, and §5.1 explains why E46N20 does not do the job it was written to do.

## 2. The one miss was a typed number, not the model

E46N10 pre-registered 62/9 and DR returned 62/10.  `CODE` hit; `DATA` was one short.  The cause is
that its title is `title('N10OUT DAT')` — **ten** characters — and `predict_p2c.py` had `prolog(9)`.
Every sibling one- and two-digit probe has a nine-character title (`'N1OUT DAT'` … `'N9OUT DAT'`)
and the ten-character ones (`N10`–`N18`) were typed correctly, so this is a single transposed
argument and not a defect in [C296]'s cost model.

The model rule is `DATA = title_len + sum(len(literal))`, and that reproduces every executed row
exactly:

| probe | title | literal items | model | DR |
|---|---|---|---|---|
| E46N2  |  9 | `A`        | 10 | 10 |
| E46N12 | 10 | `A`        | 11 | 11 |
| E46N13 | 10 | `EOF`      | 13 | 13 |
| E46N11 | 10 | `A`,`B`    | 12 | 12 |
| E46N14 | 10 | `A`,`B`    | 12 | 12 |
| E46N16 | 10 | `A`,`B`    | 12 | 12 |

The **pre-registered value was not edited.**  `HYPOTHESES.md` still carries 62/9 as the number DR was
invoked against, and that is the whole point of pre-registering in a committed blob: a prediction you
can silently fix afterwards is not a prediction.  What was corrected is `predict_p2c.py`, the
generator going forward, with a comment saying exactly what was pre-registered and what DR returned.
After the correction the model reproduces **19/19** measured sizes, and its self-test — five DR spans
it was never fitted to (CREATE:41 = 20, CREATE:44 = 31, COPYLPT:67 = 20, COPYLPT:81 = 22,
COPYLPT:53 = 18) — still passes 5/5.

## 3. What a named-file SKIP is, and what it writes

### 3.1 It is a statement option, not an item ([C304])

The manual's own syntax line on printed page 93 says so, and it is the cite on the coverage row:
`PUT [FILE(fname)] [SKIP[nl]] [PAGE[(p)]]` — `SKIP` sits **outside** `LIST(...)`.  The bytes confirm
it.  E46N2 (`put file(outf) skip list('A')`, 75 code / 10 data), DR's object:

```
0023  lxi h  *C(0000)     <- attach, 12 bytes
0026  lxi d  0652
0029  lxi b  *CODE(0042)
002C  call  ?SIOOP
002F  mvi a  01           <- the SKIP, BEFORE any item chain
0031  call  ?SKPOP
0034  lxi h  *D(0009)     <- the item starts here, after the skip
0037  mvi a  01
0039  call  ?SLCTS
003C  call  ?PNCOP
003F  call  ?QIOOP        <- ONE close for the whole statement
```

The skip's `3E 01 / CD ?SKPOP` lands between the attach's `CALL ?SIOOP` and the first item's
`LXI H,*D`, and the `LXI B,*CODE` continuation operand skips past BOTH to 0042 — one attach, one
close, whatever the list holds.  Note that this is the same one-attach-one-close shape [C296]
established for multi-item lists, with the option threaded in ahead of the chains.

A non-leading control item still refuses: `put file(f) list('A') skip;` is not lowered.  So the
option-ness is positional, and `file_items` consumes a skip at position 1 and refuses a control item
anywhere else.  Refusal positions are counted against the **original** list including the skip, which
is why E46N21 says `item 1` — its leading node is a `LINE`, nothing was consumed, nothing shifted.

### 3.2 Routing is the finding, and only E46N8 can show it ([C300] closed)

E46N8 holds BOTH `put skip;` and `put file(f) skip;` in one program, and DR's object — which mine is
byte-identical to — carries the discriminator in one place:

```
0023  lxi d  0252   ...  0029  call  ?SYSPR     <- the CONSOLE skip
0034  lxi h  *C    0037  lxi d  0652   003D  call  ?SIOOP   <- the FILE skip
                     0040  mvi a  01    0042  call  ?SKPOP    0045  call  ?QIOOP
```

`?SYSPR = 1`, `?SIOOP = 1`, `?SKPOP = 2`, `?QIOOP = 2`.  E46N1 alone, the bare file skip, has
`?SYSPR = 0`.  **Byte-exactness on E46N1 could NOT have closed [C300]**, because a misrouted skip
still contains `?SKPOP` — the symbol that distinguishes the two routes is the one the misroute would
have *added*.  That is why E46N8 was written as a two-statement probe instead of trusting the single
one, and it is the row to delete if the `on_opts`/`stream` guard is ever dropped again.

Across all 17 accepted objects the routing counts agree with DR exactly, statement by statement:

| probe | `?SYSPR` | `?SIOOP` | `?SKPOP` | `?QIOOP` |
|---|---|---|---|---|
| E46N1 | 0 | 1 | 1 | 1 |
| E46N5 | 0 | 2 | 2 | 2 |
| E46N8 | 1 | 1 | 2 | 2 |
| E46N11 | 0 | 3 | 1 | 3 |
| E46N14 | 0 | 5 | 3 | 5 |
| E46N15 | 2 | 3 | 1 | 5 |
| E46N16 | 0 | 2 | 0 | 2 |

E46N16 has `?SKPOP = 0`: it is the same two items with no skip, and it is the control that makes the
other rows mean something.

### 3.3 The runtime rows: DR's files, then mine

Six rows in `spec/RUNTIME.txt`, DR's side `golden/e42p2cdr/` (DR's own `.REL` linked by
`oracle/linkrun.py` and executed, the output file exported whole at 128 bytes), my side my
byte-identical `.REL` linked and run the same way and compared whole-file, no normalisation.
**All six export byte-for-byte identical to DR's, and E46N15's console transcript matches too.**

| probe | statements | DR's file bytes | what it settles |
|---|---|---|---|
| E46N16 | `list('A')`, `list('B')` | `'A' 'B'` (7) | **THE CONTROL.** No skip, and there is **no CR LF anywhere** — a named-file PUT does not terminate its record. |
| E46N11 | `list('A')`, `skip`, `list('B')` | `'A'\r\n'B'` (8) | A skip is exactly one CR LF pair and nothing else — no blank, no padding. |
| E46N12 | `skip`, `list('A')` | `'\r\n'A'` (7) | A **leading** skip is not suppressed; an empty first line reaches the disk. |
| E46N13 | `skip list('EOF')` | `'\r\n'EOF'` (8) | No separator blank between a skip and its statement's own item — 8 bytes, not the 10 an item-list reading would give. |
| E46N14 | `list('A')`, three `skip`, `list('B')` | `'A'\r\n\r\n\r\n'B'` (12) | Skips do not coalesce: three statements, six bytes of line break. |
| E46N15 | console, open, file A, file skip, file B, console, close | file `'A'\r\n'B'`, console `CON AGAIN` | The 0x0652 attach and its `?SKPOP` leave SYSOUT's 0x0252 block usable. |

[C295] measured the blank between separate statements; E46N16 shows the console's per-statement line
break does **not** come along for the ride, and E46N14's `skip(2)`-versus-`skip` equivalence shows the
count is a runtime argument to `?SKPOP`, not something the compiler unrolls — `E46N9`'s `skip(2)` is
the same 20 bytes as `E46N1`'s `skip`, only `MVI A,02` instead of `MVI A,01`.  This is [C305].

## 4. My four verdict predictions were wrong, and they were wrong together

I predicted DR would accept PAGE, LINE, AFTER and BEFORE.  DR accepted PAGE (E46N10, an object) and
refused the other three.  Two separate mistakes, and it is worth naming them separately:

* **PAGE and LINE were lumped.**  HYPOTHESES treated "a file control item other than SKIP" as one
  question with one answer.  DR splits them: `page` is a bare control item that lowers to 18 bytes,
  `line(2)` is a *counted* control item that DR's own parser rejects in pass 2.  This is the H14 error
  from P2b — one prediction covering two shapes — repeated at smaller scale, and the fix is the same:
  one probe per distinguishable claim.
* **AFTER and BEFORE are not PUT options at all.**  They belong to PL/I's file-position family, and
  the manual's PUT syntax on page 93 lists neither.  Predicting acceptance from "PL/I has a BEFORE/AFTER
  on file statements" without checking that the PUT grammar admits them was a claim about the language
  tested against a shape the compiler never offered.  Neither side has a witness: P2c's census of DR's
  34 file-attached PUTs found no `after` and no `before` among them.

## 5. [C303] was wrong about DR, and my own committed goldens were the refutation

[C303] (from P2b) said DR "refuses LF outright", citing E46M36 (`UNEXPECTED EOF`) and E46M35
(`SYNTAX ?`).  E46N19/E46N20 were written as the isolated discriminator — same declarations, same
statements, same `end E46N<n>;`, differing **only** in that N19 is strict CRLF and N20 is all-LF.
DR's answer: a `.REL` for N19, `UNEXPECTED EOF` and no object for N20.

But the refutation did not need a new probe.  Sweeping every committed probe that has a source on
disk:

| probe | bare LF in body | CR on last line | DR |
|---|---|---|---|
| E46D4 / E46D5 / E46D6 / E46D7 | 4 / 6 / 3 / 5 | yes | **ACCEPTED**, `.REL` present |
| E46E4 | 1 | yes | **ACCEPTED**, `.REL` present |
| E46E1 / E46E2 / E46E3 | 1 | yes | refused, for their own `OPEN file(f) input input;` syntax |
| E46M33 / E46M34 | 8 | yes | refused, `SYNTAX ?` |
| E46M36 | 7 | **no** | `UNEXPECTED EOF` |
| E46N20 | 16 | **no** | `UNEXPECTED EOF` |

Five DR-**accepted** probes carry bare LF in the body.  Every accepted probe has a CR on its last
line, and the only two `UNEXPECTED EOF` refusals are the only two that lack it.  The mechanism is
that DR's reader terminates a line on **CR**, so a body LF is ordinary text inside a line, while an
LF-terminated last line is never delivered and the compiler hits end-of-file before `end <name>;`.

The claim is corrected in `spec/CLAIMS.md` [C303] and the coverage row `LEX.SOURCE_FORM` — which
asserted the same falsehood — is corrected with it.  Worth noting *how* it survived a whole milestone:
it was written to explain two confounded runs, and the artifacts that refute it were already committed
in `golden/` by the same phase that wrote the claim.  Nobody re-read them.

### 5.1 E46N20 is not the discriminator it was pre-registered as, and its own decision rule was flawed

HYPOTHESES named E46N20 "the isolated test" and pre-registered the reading rule: *"refuse => the
latter [last-line CR] is not what differs (LF anywhere holds); compile => the last line's CR is what
mattered."*  **That rule is wrong, and it was wrong before DR ran.**  E46N20 is all-LF, so it has BOTH
properties at once — bare LF in the body AND no CR on the last line — and a probe that carries both
candidates cannot separate them.  It is [C164] again, in a probe I wrote myself while criticizing
[C303] for exactly that confound, and the criticism in HYPOTHESES of E46M35-vs-E46M36 ("its line 1 is
`E46M35:`, not `E46M36:`… the episode's own 'differ ONLY in the terminator' is not true of those two
files") applies verbatim to my own pair.

What E46N20 actually establishes is narrower and still useful: DR refuses an LF-terminated last line,
which the pre-registration listed as one of two named candidates, so the *verdict* prediction HIT — but
the mechanism was settled by the five accepted probes in §5, not by this one.  The discriminator the
pre-registration needed was a probe with **bare-LF body and a CRLF last line**, and `E46D5` already is
that probe: six bare-LF body lines, CRLF last line, accepted with a `.REL` in `golden/e42p1b/`,
committed by P1b.  It needed no new oracle run; it needed reading.

**The asymmetry runs against us here, not against DR.**  My lexer normalises line endings, so E46N20
COMPILES in this compiler to an object byte-identical to E46N19's (81/26) that DR never produced.
That is recorded as `LEX.SOURCE_FORM` and [C306], **not** as a negative-panel row, because
`run_negatives()` asserts `"[TBD]" in msg` and every row there pins a designed stop of mine.

## 6. Two rows left the panel because P2c removed the refusal they pinned

`E41X6` (`put file(f) skip list('A')`) and `E41X9` (`put file(f) skip;`) were negative rows.  Both now
compile and both are byte-exact — E46N2 and E41X9's shape via E46N1.  Following the E41X7/E41X4
convention they vanish from `REJECTS` **and** `NEG_META` (the E2E-16 symmetry audit requires both), and
their prose is kept as a retirement note rather than deleted, because E41X9 in particular recorded a
*MISROUTE* and not a language rule:

> E41X9 existed because the bare-skip arm matched on the item list alone and ignored `on_opts`, so
> `put file(output) skip;` reached the console lowering and wrote 13 bytes to SYSOUT while the named
> file went untouched — rc=0, no `[TBD]`, plausible bytes, wrong stream.

Deleting that sentence along with the row would have thrown away the reason the guard exists.

`E46N22`/`E46N23` were **added** to `REJECTS` during this phase and then **removed** from it, for the
mirror-image reason: my refusal is an ordinary parse error with no `[TBD]`, so pinning them there would
have meant either weakening the `[TBD]` requirement or stamping `[TBD]` on every syntax error in the
language.  They are `FILE.PUT_POSITION`, `mine_status=NOT_ATTEMPTED` — no implementation *and* no
refusal design, which is what they actually are.

## 7. CREATE: the blocker moved off PUT, and that is the honest result

`tools/corpus_census.py` re-recorded with **counts unchanged** (EXACT 15 / DIFFERS 0 / REFUSED 26 /
UNEXPECTED 0); two messages moved:

| program | before P2c | after P2c |
|---|---|---|
| CREATE | `PUT FILE(OUTPUT) LIST item 1 is the control item SKIP … (line 41)` | `condition form not in E2E-3b subset [TBD]: (^ eofile)` |
| COPYLPT | `PUT FILE(PRINTFILE) LIST item 1 is the control item PAGE …` | `PUT FILE with a bare PAGE control item [TBD] (line 53)` |

CREATE's refusal leaving line 41 is the integration result P2c was for.  **CREATE still does not
compile**, and the remaining blockers are `^eofile` in a `DO WHILE` condition and `eofile = (name =
'EOF')`, a store into a `BIT(1)` from a condition — neither has anything to do with PUT.

Two things to say precisely about that, because both are easy to overclaim:

* **The move to an EARLIER line is not a regression.**  `DO WHILE` is a post-test loop, so codegen
  lowers the BODY before the condition.  At baseline the body's PUT at line 10 refused first; now the
  body completes and the condition at line 8 is the first thing that stops.  Verified by compiling the
  same source with both binaries (`/tmp/pli80c_base.exe`, rebuilt from the stash at `de6ff2f`).
* **The PUT block lowers end to end.**  `CREATE-PUT-BLOCK.PLI` here is CREATE's four statements at
  lines 39–45 in their real context — inside the loop, behind the variable title — with only the two
  `BIT(1)` uses removed.  Baseline refuses it at the first skip; this compiler writes a 182-code-byte
  object whose disassembly is **4 `?SIOOP`, 3 `?SKPOP`, 4 `?QIOOP`, 0 `?SYSPR`** (`CREATE-PUT-BLOCK.dump.txt`).
  Four statements, four attaches, four closes, three skips, nothing on the console.
  **It is NOT registered as a panel specimen**: it has no DR golden, because no oracle run was made
  against it, and registering it would claim a byte-parity I have not measured.  It is evidence that
  the block *lowers*, and `E46N17` (193/124, byte-exact against DR) is the evidence that the bytes are
  right.

## 8. What the gate says

```
$ python3 tools/e2e_gate.py                  # rc=0
coverage panel   coverage_check: 102 rows, 0 errors, 0 warnings
corpus census    counts: {EXACT: 15, DIFFERS: 0, REFUSED: 26, UNEXPECTED: 0, ...}
e2e gate: 1074 byte-exact / 0 fail of 1074
e2e gate: negative panel clean (184/184 refused)
e2e gate: divergence panel 9/9 as recorded
$ python3 tools/e2e_gate.py --runtime        # the six P2c rows among 71
  runtime E46N11 FILE OK  N11OUT == golden/e42p2cdr/E46N11/N11OUT  (128 bytes, byte for byte)
  ...  (all six)
  runtime E46N15 OK  CON AGAIN
e2e gate: runtime panel 71/71 as recorded
```

1056 → **1074** byte-exact specimens (18 added), 184 → 184 negatives (2 retired, 2 added), 9/9
divergences unchanged, coverage 98 → **102** rows, runtime 65 → **71** rows.

The warning profile is **identical**: 749 lines of `dune build` output before and after, and the
sorted multiset of warning kinds and of message texts (digits stripped, to ignore position shifts) is
byte-equal.  Measured by rebuilding both trees, because a cached `dune build` prints nothing and a
"0 warnings" comparison between a cached and an uncached tree is meaningless — that trap cost one
earlier comparison in this phase a false "clean" reading.

## 9. One defect found in my own reporting, left unfixed deliberately

`pli80c` prints `wrote X.REL (N bytes, code=C data=D)` and its `data=` field is **not** the DATA
segment length.  E46N1 prints `data=0` where its `.REL` DATA area is 9 bytes; E46N17 prints `data=111`
against a real 124.  This is pre-existing — E46M1, E46M19 and E46L7 disagree the same way and all
three are byte-exact — so it is not a P2c regression and no object depends on it.  It is recorded here
because the whole first draft of §1's table was built on it: a script that took my sizes from stdout
and DR's from the `.PRN` compared two renderings against each other and reported a clean result that
was pure artefact.  Both sides must come from the `.REL`.  Not fixed in P2c because it is a reporting
change outside this phase's perimeter, and fixing a summary line without a claim attached is how the
next wrong table gets written.
