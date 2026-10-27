LINKED IMAGES FOR [E2E-42/P1a].

All six COMPILABLE long-FILE-name probes, linked with LINK 1.31 + PLILIB.IRL from DR's own
.REL in golden/e42p1 and golden/e42p1b.  Every one links, which is the point: DR's objects
are well formed and LINK resolves the clipped group symbols.

Reproduce:
  python3 oracle/linkrun.py link --tag e42p1  --out e42p1rt --names E46D1 E46D2 E46D3 E46D7
  python3 oracle/linkrun.py link --tag e42p1b --out e42p1rt --names E46D4 E46D5

The COLLISION-specific batch is golden/e42p1a-link, cited by [C289].
