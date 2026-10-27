TITLE-HELPER EVIDENCE FOR [C288].  Linked so the title site's identity could be checked
against the .REL link chains.

  E46F1.COM  VARYING title.  E46F1.REL carries LINK-CHAIN-EXT code 000A ?SLVTS at the title
             site AND LINK-CHAIN-EXT code 0033 ?SLCTS, which belongs to the program's own
             `put list (X)`.  BOTH helpers in one module: that is the dispatch proof, read
             out of DR's records rather than guessed from mnemonics.
  E46F2.COM  FIXED CHAR(8) title.  LINK-CHAIN-EXT code 000C ?SLCTS.
  E46G1.COM  Literal title.  ?SLCTS, the [C278] route.

Reproduce:
  python3 oracle/linkrun.py link --tag e42p1c --out e42p1b-link --names E46F1 E46F2
  python3 oracle/linkrun.py link --tag e42p0b --out e42p1b-link --names E46G1 --reuse

WARNING: the RESOLVED call addresses are NOT comparable between these images -- PLILIB lands
at a different base in each link session.  The SYMBOL NAMES in the chain records are what
carry the claim; do not read the addresses as evidence.
