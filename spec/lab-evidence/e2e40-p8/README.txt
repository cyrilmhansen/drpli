Working reproductions for [E2E-40/P8], kept because the episode note cites them and /tmp does not
survive.  These are NOT goldens and NOT panels: no DR oracle ever saw most of them, and nothing
here is evidence about DR -- they are the probes used to find out what MY build did before and
after the classifier.  The registered evidence is golden/e42p/ (DR's) and artefacts/E42N*.PLI
(the refusals).

  R1  g.a=5; a = a + 5        (unqualified LHS)      -> ladder + SHLD, now licensed by E42P1
  R2  same, qualified LHS
  R3  a = g.a + 5             CROSS-SPELLING self-update.  P8's note here said it "classifies as
                               the ladder" and cited R3/R4 as proof that classifier and emitter
                               agreed -- TRUE OF THE VERDICT, FALSE OF THE CODE.  The classifier
                               fired (DATA addresses match, [C258]) but the value-producing ladder
                               arm did NOT (its guard was textual `Ast.orig' equality, and "g.a"
                               is not "a"), so the value came from lower_hl's general ADD route
                               while the store came from the ladder tail.  Bytes still equalled DR
                               because both routes call hl_bias, whose |k|<=3 selection coincides
                               with the ladder's.  Traced in P8a and corrected in [C267]/[C268];
                               DR's own witness is golden/e43l/E43L6 (a = g.a + 5) and E43L7
                               (g.a = a + 5), each 256/256 identical to E42P1.
  R4  g.a = a + 5             the mirror of R3, same correction
  RB  g.a = g.a - 3           self-SUB instead of self-ADD
  R5  a = 65535               out-of-range literal -> parked (E42P2).  32768..65535 only.
  R7  a = 32768               same route at the lower bound (LR7's array value)
  R6  a = -65535              negated out-of-range  -> REFUSED (E42N2)
  R8  a = a + 0               elide_fixed_zero collapses it to a self-copy -> parked, unchanged
  R9  ordinary var self-add   control: must stay exactly as it was
  RA  ordinary var, 65535     control: SHLD, unchanged -- the classifier never looks at non-members

Run: ../../ocaml/_build/default/bin/pli80c.exe NAME.PLI out.REL
