# fc01-framing — oracle round plan (FC-01 hop, 2026-11-02)

Purpose: discriminate H1 (unconditional exit CRLF) vs H2 (conditional flush) for the shape
*pure-PUT program whose last executed output statement is a bare `PUT SKIP;`* — the trailing
framing artifact of the FC-01 Batch-A corpus program MATH-00 (leading framing is already
measured: E29PS1 both sides; FCPS3 re-confirms on the `PUT SKIP LIST` spelling as a control).

Ordering (PROTOCOL #1): `probes/FCPS1.PLI FCPS2.PLI FCPS3.PLI` + `HYPOTHESES.md` +
`BASELINE-MINE.txt` (my objects, DR LINK-80+PLILIB, cpmsim console — my side only) and my
evidence goldens `golden/fc01ps-my*/` are committed in the PRE-REGISTRATION commit BEFORE any
invocation of DR PLI.COM. The oracle stage follows in a later commit.

Oracle stage (measured round procedure, mirrors E29/E48):

```
export CPMSIM=$PWD/thirdparty/z80pack/cpmsim/cpmsim
PLI_SRC=probes python3 oracle/batch.py FCPS1 FCPS2 FCPS3 --tag fc01ps --switches '$L$D'
python3 oracle/linkrun.py link --tag fc01ps --out fc01ps-l --names FCPS1 FCPS2 FCPS3
python3 oracle/linkrun.py run  --tag fc01ps-l --out fc01ps-r --names FCPS1 FCPS2 FCPS3
```

Decision rule:
- DR FCPS1 console `X=         1\n\n` → H1 ACCEPTED, H2 FALSIFIED; MATH-00 trailing blank is DR
  behaviour; `README.md` § 6 gains the exit-framing law (evidence-cited) and the Batch-A
  reference derivations + specs are corrected to model the framing law (never the capture).
- DR FCPS1 console `X=         1\n` → H2 ACCEPTED; my extra CRLF is a measured `my-gap`;
  Batch-A verdicts stay FAIL honestly; the gap is recorded in the ledger, NO OCaml change in
  this session (FC-01 constraint).
- Controls (FCPS2/FCPS3) must byte-equal my side under both hypotheses; a control deviation is
  recorded as its own finding (capture-law defect), not laundered.
- .REL whole-file comparison recorded per probe either way; byte-identical objects cannot
  discriminate and are reported as such.
