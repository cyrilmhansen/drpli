# E2E-40 P2 -- qualified internal member access, resolved where the spelling is introduced

## What E2E-39 deferred, and why the deferral was the wrong call
E2E-39 refused `g.a = 7` with a loud message and recorded: "landing that resolution without C254
would mean one program compiling to two objects here while DR's two objects are identical." E40Q1
and E40Q2 -- run as P1's controls -- test that sentence directly, and it dissolves. DR's qualified
program and its unqualified twin have .REL files differing at **three bytes: offsets 5, 16, 23**,
which are the characters of their two different procedure names. CODE and DATA agree (0036/0008).
So DR's two objects are one object modulo the name, and the fear that sharing a table entry between
two spellings would produce a mismatch was unfounded. Deferring was still defensible at the time --
it was a refusal with a written reason rather than a silent one -- but it was founded on an
unverified premise, and P1's controls were what verified it.

## The change
Three pieces, in descending order of importance:

1. **parser.ml, the `.` step of the suffix loop.** `head.member` with a plain identifier on the left
   becomes ONE dotted identifier (`G.A`). Everything else -- bind's member rows, every codegen
   matcher, width function and classifier -- then sees an ordinary name it already handles. A dot
   cannot be lexed inside an identifier, so the key cannot collide with a declared name. A
   non-identifier left side (`a(1).b`, `p->q.b`) keeps the structured node, so those shapes still
   reach refusals that describe them instead of an undeclared-name message.
2. **bind.ml, member row entry.** Alongside the bare row, a row keyed `head.member` with the
   identical offset, size and type. They cannot drift because the second is built from the first.
3. **codegen.ml.** `qref_key`/`qref_name` resolve an `Eqstruct` to the alias; `lower_hl` and
   `lower_assign` re-dispatch through the ordinary variable path, `lower_assign` on BOTH sides.

Piece 3 was written first, and what it exposed is the reason for piece 1. With only
`lower_hl`/`lower_assign` patched, `cpb.nameadr = addr(t)` compiled but
`cpb.paramadr = cpb.nameadr` still refused: the predicates that decide whether a pointer assignment
is a measured form (`ok rhs`, and the [C179] call admission) inspect the raw AST node, so an
unresolved `Eqstruct` there is an unknown expression kind. Patching `num_width` then made
`put list(g.a + g.b)` work while `put list(g.a)` still refused in the PUT-form matcher. Every miss
was a refusal rather than a wrong value -- that part of E2E-39's worry was right -- but the miss
list is open-ended, and DR says the node should not exist at all.

## Verification: the invariant, not just the size
The claim to test was byte-level, so the test was byte-level:

| pair | DR | mine |
|---|---|---|
| E39S1 (qualified) vs E39S2 (bare) | identical (md5 b3d60402) | **identical** (md5 d58ccdeb) |
| E40Q1 vs E40Q2 | differ at offsets 5, 16, 23 | **differ at offsets 5, 16, 23** |

Nine member programs now compile, all with DATA equal to DR's, all short 4-12 bytes of code --
[C254]'s operand-preservation shortfall, registered as divergence rows (E39S1, E39S7, E40Q1, E40Q4
are new rows; the pre-existing five kept their exact pinned shapes, so the alias rows and the parser
rewrite moved no layout).

Full gate after the parser change: **939 byte-exact, 125/125 negatives, 18/18 divergences, 18/18
runtime, coverage 85 rows 0 errors.** E39X1 and E40X3 still refuse with QUALIFY (P1 intact); E39X1
with its uses qualified now compiles, so DR's named remedy is available here. MPMCALLB's next
blocker is unchanged -- `STATIC on CHAR(27) is unsampled` -- so qualified member access was never
what was holding it.

## Newly opened, newly listed as risks
`g.a` where `g` has no member `a` refuses here with "not a member of that owner", and **DR's
behaviour for that exact shape has never been sampled**. Bind already ignores the head name when it
collects member declarations, so DR may well resolve the member from all visible owners regardless of
what the source says. That is a wrong-acceptance risk pointing the opposite way from everything else
in this episode, and it needs its own probe before either behaviour is trusted.

## Process: three self-inflicted alarms, all caught before committing
- **The "CHANGED bare paths" scare.** My comparison loop reported E39P1 and others differing,
  because the loop compared against files it had never written. `cmp -l` between the real old and
  new objects: 0 bytes.
- **The "lost coverage rows" scare.** A python fragment split COVERAGE.tsv on `\r\n` while the file
  is `\n`-delimited, so the whole file looked like one row and every lookup failed. `grep "^DECL\."`
  and `git log -S` showed both rows present and committed. The rewrite it did attempt was a no-op,
  confirmed by `git diff --stat` -- and the second attempt aborted on an `assert len(parts)==15`
  that I had added defensively, which prevented a real corruption of the two rows I was editing.
- **The missing PERIMETER heading.** `grep "^## \[E2E-4"` found nothing, which looked like a lost
  P1 edit. `git show --stat a944530` says PERIMETER.md changed by 5 lines: P1 edited rows inside the
  E2E-39 section rather than adding a heading, and my memory of the shape was the thing that was
  wrong. In each case the fix was to ask a second, independent question of the repository instead of
  repeating the first one.

## P5 addendum -- the first execution, and it is non-circular
E40R1 adds a labelled qualified-member probe, DR-compiles it (golden/e40b, 6th of the episode's 12
slots), links and runs DR's object (golden/e40dr/E40R1.output.txt: `g=        16`), and registers a
RUNTIME.txt row that runs MY object against DR's printed value. My image differs from DR's at 143
offsets (code 59 vs DR 65), so the gate marks the row NON-CIRCULAR -- the first member-program
evidence that is about my semantics rather than about my ability to reproduce bytes. [C259]

Two bookkeeping errors were caught by guards rather than by reading:
- I hand-appended a row to spec/INVENTORY.txt, which its own header declares MACHINE-MAINTAINED, and
  the gate aborted on the disagreement. `--update-inventory` then regenerated the file
  byte-identically to HEAD, which also proved E40R1 needed no entry: only byte-exact specimens are
  inventoried, and divergence/runtime rows are not.
- `runtime_check` requires a `golden` path, so the row had to point at DR's real oracle output
  (golden/e40b) rather than at the directory I created for the link/run scratch; the note records
  which directory holds DR's transcript and why it exists.
