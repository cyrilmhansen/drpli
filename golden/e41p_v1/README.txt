E2E-40/P7 FIRST BATCH, KEPT BECAUSE IT IS EVIDENCE OF A REJECTION, NOT OF A SPECIMEN.

These are the DR compile outputs for the FIRST spelling of the E41P probes.  E41P2 was written
    declare 1 g, 2 a fixed, 2 b fixed, 1 h fixed;   <-- `h' as a level-1 item INSIDE g's declaration
    h = g.a;
and DR rejected it in PASS 1 with `STRUCTURE ?' at E41P2.PRN line 14, emitting no .REL.  The
probes in golden/e41p/ use the redesigned spelling (h in its own declaration), which DR compiles.

Why this directory exists: spec/notes/e2e40-p7-computed-member-store.md and [C266]'s discussion
cite that rejection, and until now the cited PRN was not in the repository -- it lived in /tmp
and would have vanished.  A claim that cites an oracle output must ship the output.

The MECHANISM IS STILL UNDETERMINED.  Adjacent to [C255] (DUPLIC: a member name shares the flat
namespace) and [C257] (qualify at the USE), but this PRN's marker position does not
discriminate between "a level-1 item may not be declared inside an active structure" and "the
name h collided".  No claim is built on it and neither behaviour is implemented in this
compiler: mine does not reject that spelling.  Needs its own probe in a later slice.
