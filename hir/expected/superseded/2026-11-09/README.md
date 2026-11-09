# Superseded pins — 2026-11-09 (E2E-54/P1-a1)

These are the ORIGINAL bytes of the H05 negative pin (rc 2, HIR-E03
"array declaration for a is outside the P0 subset"), produced by the P0/P1-b
subset gate. E2E-54/P1-a1 admits 1-D FIXED BINARY(7..15) element arrays
(PLAN §P1-a1.2), and H05 (`dcl a(5) fixed bin(15); a(1) = 2;`) IS the core
positive shape of that slice, so its negative pin cannot survive: behaviour is
a function of input, and the adjudicated disposition (PLAN §P1-a1.6) is to
archive these bytes VERBATIM and re-pin H05 from MEASURED output as a
positive fixture (hir/expected/H05.txt). See spec/lab-evidence/e2e54/
PLAN.md §P1-a1.6 and RESULTS.md §P1-a1 for the measured flip.
