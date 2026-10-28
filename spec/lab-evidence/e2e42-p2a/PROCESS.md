# E2E-42 / P2a — process accounting, including the rule I did not meet

## The pre-registration rule, and how this step broke it

The mission's protocol is: write the falsifiable hypotheses, COMMIT them, then run the oracle.
The point of committing first is that the record becomes uneditable-after-the-fact by anyone,
including me.

**That did not happen for P2a.**  `spec/lab-evidence/e2e42-p2a/HYPOTHESES.md` was written before
the oracle ran, but it was never committed before the run: `git log -- <that path>` is empty as of
this writing and `git status` shows the whole directory untracked, while
`golden/e42p2a/E46L1/E46L1.REL` — the oracle's OUTPUT — has an mtime of `08:05:20` and
`HYPOTHESES.md` an mtime of `08:32:29`, i.e. later.  **Those timestamps no longer exist:** a
`git stash -u` + `git stash pop` run later in the same session rewrote the mtime of every untracked
file in the directory to `09:51:09`, so the ordering is now attested by nothing at all.  The two
numbers above are quoted from what I observed at the time and cannot be re-checked by anyone,
including me.  So the honest statement is not "the
hypotheses were pre-registered"; it is "the hypotheses were written before the run, and the only
evidence for that ordering is a filesystem timestamp I could have produced either way".  The
claims [C293]-[C295] do not depend on the pre-registration; they stand on the goldens.  What the
pre-registration was supposed to add — protection against fitting a prediction to a result — is
simply absent here, and the eleven-probe scorecard in `RESULTS.md` should be read with that hole
in it.

The file WAS then committed alongside the goldens at the end of the step, which fixes the ordering
for future steps but cannot retroactively fix this one.

## Edits made after the oracle had run, and why each was legitimate anyway

Two of the seven runtime probes were rewritten AFTER DR had been invoked on them, and both
rewrites are disclosed rather than folded into the prose:

* **E46L13** was `c char(20); c = 42;`.  This compiler refuses that assignment for a reason that
  has nothing to do with PUT — `char store from non-literal [TBD]` — so the object would have
  tested two unmeasured routes at once and the DR run would have told me nothing about the PUT.
* **E46L15** was `z fixed dec(6); z = 123.5;`.  Same problem: `DEC literal 123.5 into scale 0
  [TBD]`.

In both cases the first oracle invocation produced NO `.REL` at all (the batch reported
`UNEXPECTED EOF`, because I had written the files with LF endings and no `0x1A` sentinel — a
harness-side failure, not a DR verdict), so DR never expressed a verdict on the original spelling.
Both probes were then rewritten to a literal assignment that keeps the question I actually asked
(what fills an under-fixed fixed character string; what does a scale-0 DECIMAL edit print), the
matching predictions H13/H15 were rewritten in `HYPOTHESES.md`, and only THEN was the oracle run
again.  The two predictions that were thus edited are flagged in the file itself, and their
outcomes are scored in `RUNTIME-RESULTS.md` against the EDITED text, which is stated there too.

## The fabricated citation, in full

H14 predicted that FIXED BINARY would print in OCTAL and justified it with a citation:
"`[E2E-8]'s measurement that FIXED BINARY prints in base 8`".  E46L14.PLI's own comment repeated
the claim under a second name, "`the E3B2 measurement`".  **Neither exists.**  There is no E3B2
specimen in `probes/`, `spec/INVENTORY.txt`, `spec/COVERAGE.tsv` or `spec/RUNTIME.txt`, and the
only lines in `spec/` or `tools/` containing "octal" are the ones describing this error.  I
invented an authority for a guess and then wrote that guess into a committed source file, where it
became part of the evidence base rather than a note about it.

DR's file holds `       42` — FIXED BINARY PRINTS IN DECIMAL [C295].  The probe's comment has been
corrected in place, in the text above rather than silently, because the false prediction is now the
only record of what was believed before the run; deleting it would have made the miss unfindable.
What remains unfixed, deliberately: `HYPOTHESES.md` H14 still says octal.  A hypothesis file edited
after the oracle stops being a hypothesis.

## What was done right

* The oracle ran on the eleven static probes BEFORE this compiler was changed to accept any of
  them, so DR's verdicts are independent of my lowering, and `HYPOTHESES.md`'s eleven static
  predictions were fixed before that run.
* E46L18 is the one probe written in response to a measurement — the apostrophe discrepancy
  between E46L12's file and E46L17's console — and it is labelled as such, as a marked ADDENDUM at
  the foot of `HYPOTHESES.md` rather than as a ninth entry in the section that was fixed before
  L12-L17 ran.  Its prediction was written before DR was pointed at it.  Writing a probe to
  separate two explanations after noticing they differ is good practice; silently editing the old
  prediction to match would not be, and that is what was NOT done.
* Refusals were designed and described before implementation, and the implementation was then
  checked against DR, not the other way round.
* `tools/e2e_gate.py`'s NEG_META diagnostic was corrected first (P2a-0) because the panel's own
  error message was a lie about which categories exist; the panel was verified at 170/170 before
  anything else changed.

## The number that changed, and why it is not a regression

`PU1` and `E46K10` are both still refusals, with different markers.  `PU1`'s operand `x fixed`
became an authorized class through E46L3, so PU1 now stops at the OPEN guard instead of the item
guard; E46K10's member operand now reaches `authorize_file_item` instead of the matcher.  Neither
retirement is claimed.  Per the mission's own warning, an opened-file variable PUT working does
not retire PU1, because PU1 is a different whole program — one with no OPEN statement at all.  Its
category stayed `my-gap` and its new reason is backed by a measured object (`golden/e42p2a/E46L8`,
DR compiling exactly that program), which is the strongest thing that could honestly be said about
it.
