NOT ORACLE OUTPUT.  These are MY compiler's objects, kept as the discovery record for [C251]: the
four E39V* images are the pre-fix witnesses that all printed `0' when their branches had to be
taken, and the same directory holds the post-fix rebuilds.  golden/e39a/ and golden/e39b/ are the
authentic DR round trips; golden/e39dr/ is DR's objects linked and executed.

PLACEHOLDER .PRN FILES -- read this before trusting a link result here.  linkrun.py wants a .PRN
next to a .REL to resolve external references.  The E39V1..E39V4 programs have no DR .PRN (they
were never sent to the oracle: they exist to be wrong on my side), so their directories carry a
one-line placeholder.  The link and run still succeeded, which tells me the linker resolved
everything from PLILIB rather than from the .PRN -- but a scratch directory that links because I
fabricated an input is exactly the failure mode [C249] is about, so:

  * the placeholder never supplied a symbol (a fabricated .PRN would have had to name one);
  * E39V* values are used only as BEFORE/AFTER evidence about my own lowering, never as a claim
    about DR;
  * every DR-side value in this episode comes from golden/e39a/*.output.txt or
    golden/e39dr/*.output.txt, produced from goldens that have authentic .PRN files
    (golden/e39a/E39B4/E39B4.PRN etc.).

If you re-run one of these links, do not read success as validation of the .PRN.
