NOT AN ORACLE.  This is the first E37 probe batch; all 17 of its compilations
failed for a reason in my harness, not in the compiler.  The generated sources
were LF-terminated with no CP/M ^Z marker, so PL/I-80 printed "UNEXPECTED EOF"
and wrote a .PRN without a .REL.  473 of 490 historical artefacts carry ^Z.
The corrected re-run is golden/e37e (15 ok / 17; the two non-ok are deliberate
probes -- E37A1's `*w' dereference, which DR rejects as a syntax error, and
E37S3, DR's own NOT STATIC control) [C249].

What is versioned here: summary.txt (the 0-ok classification the harness
produced) and E37S6/E37S6.PRN (the representative print file: banner, switch
legend, then UNEXPECTED EOF -- the shape that looks like a compile).  The other
per-program directories and the five session transcripts are local scratch and
gitignored: they are 17 copies of the same four lines, and versioning 60 KB of
noise would make the interesting file harder to find.
