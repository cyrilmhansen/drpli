# E2E-11 step 3e — external ENTRY: authentic assembler path established

## Result

`oracle/linkrun.py asm --out <tag> --names DIV2 FDIV2` assembles DR's own
assembly modules with **RMAC 1.1 from the distribution disk**, zero unresolved
externals, and `link --tag <dr-compile> --names DTEST FDTEST` then links them via
`EXTRA_REL` into 7808-byte `.COM` files that **run correctly under cpmsim**
(`100 / 2 ** k` halving table, k=0..22).

Artifacts: `golden/e2e140asm/` (RMAC output), `golden/e2e141/` (DR's DTEST/FDTEST
`.REL`), `golden/e2e141l/` (linked `.COM`), `golden/e2e141r/` (transcripts +
output).  Sources copied to `artefacts/DIV2.ASM`, `artefacts/FDIV2.ASM`.

## Why this was the blocking unknown

The step-3 close-out found the modules exist; this step established that they
build and link in my harness.  That converts external ENTRY from
"testable only at object-file level" to "testable end to end", and DTEST/FDTEST
from one-feature-tODO to one-feature-verifiable.  See CLAIMS C132 for the ABI
confirmation extracted from DIV2.ASM itself.

## Immediately next (not done — context ran out mid-implementation)

1. Make external entries visible to codegen: `bind` already classifies them
   (`RTentry { params; external_; ret }`, bind.ml:41/167) but `st.vars` carries
   `vkind` (Vint/Vfix/Vvar/Vdec/Vflt/Vbit1) with no entry case, so codegen cannot
   see `ex` at all and refuses at the CALL target check (codegen.ml:1466).
2. Emit `LXI H,*A(desc)` (existing shared path) + `call_ext st "<SYMBOL>"`
   instead of internal/forward resolution.  DR's records for this are pinned:
   E24G `LINK-CHAIN-EXT EX` at code 0010, no EXTDEF for EX; DTEST
   `LINK-CHAIN-EXT DIV2` at code 0019.
3. Acceptance per C132: `.REL` byte-exact vs `golden/e2e121/E24G`,
   `golden/e2e141/DTEST`, `golden/e2e141/FDTEST`; `.COM` identical after linking
   against the same RMAC module; executed output identical to
   `golden/e2e141r/DTEST.output.txt` (and independently checkable as 100/2**k).
4. FDTEST additionally needs expression-position ENTRY with `returns(float)` --
   the result arrives on the float stack, cf. `?RSBLK`/`?FPRET` in FFACT.

## Cost comparison the instruction asked for (item 4)

With C132, external ENTRY is the cheaper of the two remaining big features:
the descriptor machinery is already built and proven byte-exact for internal
calls; the ABI is confirmed from DR's own assembly source; the toolchain is in
place; and it closes two corpus programs (DTEST, FDTEST) plus contributes to
8 ENTRY programs.  Named sequential FILE I/O still needs `?OIOOP` push-block,
`?SIOOP`, `?SLCTS` and stream FCB mechanics with no shortcut and no additional
program closable on its own (COPY/UPDATE/REPORT each carry further blockers).
Recommendation: finish external ENTRY next, then reassess named FILE.
