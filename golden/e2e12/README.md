# golden/e2e12 -- E2E-9 oracle re-runs (multi-argument ABI, DEC formals, `&`, `%replace`)

Every `<NAME>/<NAME>.REL` here is DR PL/I-80 v1.4 pass-2 output, produced by
`oracle/probe.py` against the reference CP/M image from the tracked source in
`probes/<NAME>.PLI` (scratch working copies during development lived in the
untracked `e12src/` and `e12b/` directories).  `<NAME>.PRN` is the DR listing,
`dir.txt` the run directory image listing.

`DECPOLY/DECPOLY.REL` is a re-run of the corpus program and is byte-identical to
the curated copy in `golden/first8080u/DECPOLY/DECPOLY.REL` (verified with
`cmp`); the gate registers the corpus copy as the authority.

`NTEST1`/`NTEST2` are DR-side evidence for the 6-character external-name law
(C096): their objects contain no symbol for the >6-character *internal*
procedure names.  They are NOT registered as gate positives because my build
does not yet accept their trailing-`stop` main layout (a main-block statement
after an appended procedure).

`MANIFEST.sha256` hashes the `.REL` and `.PRN` files in this directory.

All 38 specimen directories carry their `dir.txt` run-directory listing.

Provenance repair, recorded rather than hidden: the working sources for
R2001-R2013 were deleted during an intermediate cleanup, leaving goldens with no
source.  They have been RECONSTRUCTED from the DR source listing embedded in each
`.PRN` (line-numbered, label tokens un-mapped from DR's internal `lNAME` form)
and now live in `probes/`.  The reconstruction is not a gate-positive proof: my
current build REFUSES all twelve (7 on the trailing-`stop` main layout, plus
pointer-formal subtraction, CALL-statement, deref-operand condition, store
through a formal, and multiple-forward-CALL gaps), so none of R2001-R2013 is
registered.  They are kept as the DR evidence behind C093/C094 and as a map of
the next layout gaps.  The registered multi-argument positives are R2030-R2038,
R725, LONGNAME and DECPOLY, whose sources were tracked the whole time.
