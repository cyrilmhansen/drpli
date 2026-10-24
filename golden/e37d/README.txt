NOT AN ORACLE.  This is the first E37 probe batch, and every one of its 17
compilations failed for a reason in my harness rather than in the compiler: the
generated sources were LF-terminated with no CP/M ^Z marker, so PL/I-80 printed
"UNEXPECTED EOF" and wrote a .PRN without a .REL.  473 of 490 historical
artefacts carry ^Z; the corrected re-run is golden/e37e (15 ok / 17, the two
non-ok being deliberate probes: E37A1's `*w' dereference, which DR rejects as a
syntax error, and E37S3, DR's own NOT STATIC control) [C249].

Kept, not deleted, because "a print file exists" looking like "it compiled" is
the failure mode this directory demonstrates.
