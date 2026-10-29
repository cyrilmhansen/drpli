# E2E-48/P2c RETIRE round — E46K1/E46K3: pre-registered predictions (oracle NOT yet run)

## Why this round exists (and why it is a corollary, not a new bank)

Commit `14c7321` (step 4a) and `7701f52` (arm 1(a)/3) ADMIT the exact statement
shapes that negative-panel rows E46K1 and E46K3 pinned as refusals. Their own
INVENTORY rows (spec/INVENTORY.txt:514/522) say: `NEITHER verdict is known ...
To retire a row: measure DR on it, then promote it to a byte-exact specimen or
re-classify it as dr-refuses with DR's word attached.` This round performs that
measurement. No new PL/I shape is introduced: both programs' routes are already
law in `spec/lab-evidence/e2e48-p2c/RESULTS.md` §2 --

* E46K1  `line = 'AB';`  -- BARE destination, VARYING member, literal source:
  measured by golden/e48p2c/E48C3 (RESULTS §1 P3, §2.1).
* E46K3  `if line = 'AB' then k = 1;` -- member-LEFT compare in TEST position,
  BARE spelling: §2.4 (E48C9 head, qualified) + §1 P3 (spelling-invariance) +
  [C309] (no-else skip to next statement) + `3A/B7/FA`-free 15-byte head.

## Probes (existing tracked files, unmodified)

```
E46K1: dcl 1 rec, 2 line char(14) varying, 2 nxt fixed bin(15);   line = 'AB';
E46K3: same record;  dcl k fixed bin(15);   if line = 'AB' then k = 1;
```

## PREDICTIONS (derived from committed goldens BEFORE any oracle call)

P-K1  DR verdict: ACCEPT, produces a .REL. Layout per §2.6/C114: no statics,
      pool `'AB'` = *D(0000..0001), rec AUTOMATIC at *D(0002) -- line cell 15
      bytes (1+14) at 0002, nxt 2 bytes at 0011 -- DEF-DATA-SIZE 0013 (2+17).
      CODE: 6-byte prologue `01 00 02 / CD * ?START`; store at 0006 EXACTLY
      `21 *D(0002) / 11 *D(0000) / 3E 0E / 06 02 / CD ?SMCVM` (the [C174]-class
      SMCVM tail with the member's immediate address -- the E48C3/E46J21 law at
      cap 14); then `CD ?STOPX`; DEF-CODE-SIZE 0016.
      WHOLE FILE byte-identical to my object (baseline below).

P-K3  DR verdict: ACCEPT, produces a .REL. Layout: pool `'AB'` 0000..0001, rec
      auto 17 at 0002, k 2 bytes at 0013 -- DEF-DATA-SIZE 0015. CODE:
      15-byte TEST head at 0006 `21 *D(0002) / EB / 21 *D(0000) / 3E 02 /
      CD ?SCVCM / C2 00 00` with the skip word filled (SET-LC/RELOC) to the
      NEXT STATEMENT = the ?STOPX epilogue at 001B [C309]; then-body
      `k = 1` = `21 01 00 / 22 <data 0013>` (LXI H,1 / SHLD -- the existing
      measured store route). WHOLE FILE byte-identical to my object.

P-G1  2 ok / 2 accepts; no DR refusal expected on either.

Falsification consequence: if DR REFUSES either program, the row is
re-classified dr-refuses WITH DR's diagnostic attached and the admitting arm
must be narrowed again -- an acceptance-prediction MISS is recorded, not
edited out (PROTOCOL #2). If DR accepts but the whole file is NOT byte-identical
to mine, the shape stays on the byte panel only up to the differing offset and
the difference is classified my-gap and fed back as a NEW [TBD], not lowered on
faith.

## BASELINE-MINE (measured at HEAD 3ee414a, BEFORE the oracle run)

```
$ ./ocaml/_build/default/bin/pli80c.exe probes/E46K1.PLI ...  -> 128 bytes (pli80c reported
  `code=22 data=17'; the data= SUMMARY is the KNOWN reporting defect [e2e42-p2c §9] -- the
  DEF-DATA-SIZE RECORD reads abs 0013 = 19)
  code 0006: 21 [d0002] 11 [d0000] 3e 0e 06 02 cd [?SMCVM] ; 0013: cd [?STOPX]
$ pli80c probes/E46K3.PLI ... -> 128 bytes (reported `code=30 data=19'; DEF-DATA-SIZE
  RECORD reads abs 0015 = 21)
  code 0006: 21 [d0002] eb 21 [d0000] 3e 02 cd [?SCVCM] c2 [->001B]
  code 0015: 21 01 00 22 [d0013]  ; 001B: cd [?STOPX]
```
(Full reldumps reproduced in RETIRE-BASELINE-MINE.txt at this commit.)
