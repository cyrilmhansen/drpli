# E2E-39 slice 1 (P1) — BASED views in comparisons deref through the pointer

Baseline `1047632`.  Task: repair [C246]'s BASED comparison defect.  Result: the defect was real, was
not where [C246] said, and is now fixed -- PB4's divergence row retires after eleven episodes, and
E37B1/B2/B3 promote to byte-exact specimens.

## Where [C246] was wrong

[C246] read DR's `LHLD <p> / MOV E,M / INX H / MOV D,M / XCHG / LXI B,FFFC / DAD B / MOV A,H / ORA A /
JM` against my `LHLD <p> / LXI B,FFFC / DAD B / MOV A,H / ORA A / JM`, saw the missing ladder, and
concluded `if q > 3` was a wrong-value test whose z=40 masked it.  The ladder really was missing.  The
conclusion was not checked against a value, and values are cheap: I linked and ran **DR's** E37B1/B2/B3
(`golden/e39dr/E37B{1,2,3}.output.txt` = `q= 1`, `q= 3`, `q= 8`) and my pre-fix images printed the same
three answers.  Four z values (1, 3, 4, 40), four agreements.  Whatever makes `>` agree here, it is not
the deref, and I do not claim to understand it -- which is precisely why an instruction-sequence
difference is not evidence about a value [C249] in a new costume.

The relation that does mis-value is `=`, and it took deliberately-built witnesses to find:

| probe | shape | DR | mine (pre-fix) |
|---|---|---|---|
| E39B4 | `allocate q set(p); q = 7; if q = 7 then r = 1` | `r= 1` | **`r= 0`** |
| E39V1 | `p = addr(z); z = 7; if q = 7 then r = 1` | (n/a) | **`r= 0`** |
| E39V2 | same, `if q > 3` | (n/a) | **`r= 0`** |
| E39V3/V4 | `q = 9; if q > 3` after ALLOCATE | (n/a) | **`r= 0`** |

V1..V4 are the important four: every one of them must take a branch, none did, and two of them use
`>`.  So `>` was *also* broken -- E37B1's agreement was a coincidence at those particular addresses,
not a property of the lowering.  Four variants that all print `0` is the shape of evidence that a
disassembly of one instruction cannot produce.

## Root cause, one line at a time

```ocaml
let cmp_load_deref st (nm : string) =
  d st op_lhld; reloc st Data (addr_of st nm);
  if List.mem (String.lowercase_ascii nm) st.deref then      (* <- the gate *)
    (d st 0x5e; d st 0x23; d st 0x56; d st op_xchg)
```

and at the prologue, `st.deref <- List.map fst pl.Bind.pl_ptrs` -- the procedure's **pointer formals**.
Every single-operand comparison arm (Eq/Ne/Lt/Gt and their shared partners, six call sites) loads
through this one function, so a name whose kind is `Vbased p` (bind's `RTbased`: a view, no cell, no
AUTO STORAGE contribution [C178]) never got the ladder and was compared as the pointer cell it is
held through.

The fix is one branch: `Vbased p` -> `LHLD p` + ladder, `Vbfix (p,k)` / `Vbptr (p,k)` -> `LHLD p` +
`member_step k` + ladder -- i.e. exactly `bfix_val_load` [C202], which the store and plain-read paths
already used.  Not a PB4 sequence: the comparison path stops being a fourth opinion about what a based
name means, and it now agrees with the loader the rest of the compiler agrees with.

## Verification

* PB4, E37B1, E37B2, E37B3 byte-exact against their existing goldens; all four promoted out of
  `spec/DIVERGENT.txt` (12 -> 8 rows) into the specimen panel (935 -> 939, 0 fail).
* Untouched: NETWORK, REVERSE, ST2 (both pointer-store goldens), E34E3, E34E5 -- the exact
  qualified-member witnesses stay exact, and `is_plain_num_auto` still keeps a formal out of that arm,
  so the three address models share the loader without sharing address generation.
* Runtime panel 16 -> 18: E37B1 (false outcome) and E37B3 (true outcome) added with expectations read
  off DR's own images *before* my objects were identical; PB4's row re-annotated to say that since it
  is now byte-identical, that row is evidence about link/run, not about the comparison.
* negatives 124/124, coverage 84 rows / 0 errors (new `COND.BASED_VIEW_LITERAL`), census unchanged
  (no corpus program's classification moved), `--runtime` gate exit 0.

## Deliberately not done

`>=` and `<=` against a literal, and the literal-left orientation, stay refused: DR accepts them
([C247], probes E37B4/E37C4/E37C5/E38C7..C9 banked in `e37e`/`e38a`) but no probe pins the instruction
sequence for a BASED view with those relations, and "implement the whole matrix" would have meant
guessing the parking rule for a deref-first operand.  E39B2/E39B3 were sent to DR and are in
`golden/e39a` for whoever does draw that boundary.

Instrument notes: `oracle/batch.py NAME... --tag TAG` is the driver (I invented
`compile.py --commit --work-root` and it failed loudly, which is the good outcome); `linkrun.py` needs
`link`/`run` stages with `--tag/--names/--out`; `pli80c` takes the output path positionally.
`tools/probe_gen.py --crlf-eof IN OUT` now owns the CP/M text encoding so single probes stop being
hand-rolled [C249].
