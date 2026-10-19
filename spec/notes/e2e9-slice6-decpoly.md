# E2E-9 slice 6 -- multi-argument internal ABI, FIXED DECIMAL formals, `&`, `%replace`; DECPOLY accepted

Date: 2026-10-20.  Prior checkpoint: `4bc9af8` (LOAN1).  Prior commit:
`fa9d782` (slice 5, IFACT).  Result: **DECPOLY `.REL` byte-identical (1152 B,
code=339 data=24), 6th corpus program accepted; gate 211/211 byte-exact, panel
46/46, corpus 6 EXACT / 0 DIFFERS / 35 REFUSED.**

## 1. What DECPOLY needs, and in the order it had to be built

| step | mechanism | DR evidence |
|---|---|---|
| 1 | multi-arg call descriptors (2-byte pointer cell per argument, per-site block) | R2031, R2034, R2035, DECPOLY |
| 2 | callee entry: arity 1 peeled, arity >= 2 counted block copy (`MVI C,2N ... DCR C`) | R2030/R725 vs R2031-R2038 |
| 3 | per-argument INTERLEAVED emission of expression temp + descriptor constant | R2032 |
| 4 | FIXED DECIMAL formal = 2-byte pointer cell, read `LHLD` + `MVI A,p` + `?DLDOP` | DECPOLY, R2037, R2038, R725 |
| 5 | mode check: decimal argument against a DECIMAL formal must be a variable | N33 (re-pinned) |
| 6 | `&` conjunction: `SUI 01 / SBB A` boolean bytes, `PUSH PSW` / `POP B / ANA B`, one `JP`; next operand's address load hoisted above the push | DECPOLY, R2021, R2025, R2026, R2027 |
| 7 | external name truncated to 6 characters | DECPOLY -> DECPOL, LONGNAME -> LONGNA, REPLACEP -> REPLAC |
| 8 | literal-right multiply with a dereferenced left operand skips the DE rotation | R2036 |
| 9 | `%replace` pass-1 textual macro | R2024, DECPOLY |
| 10 | counted `PUT SKIP(2)` | R2023 |

Steps 1-5 are one indivisible unit: the binder refused the 3-argument call site
before codegen was ever reached, so no amount of codegen work alone could move
DECPOLY.

## 2. Laws landed

C093 (descriptor block + prologue by arity), C094 (DEC formal cell + mode check),
C095 (`&` materialise-and-AND), C096 (6-char external names), C097 (`%replace`),
C098 (DE-free multiply).  No new runtime routine was introduced anywhere in the
slice.

## 3. Defects found by byte-diffing (all four repaired)

1. `bind.ml` call-site fold restarted its accumulator at `0`, so only the LAST
   call site survived -- multi-argument descriptors silently vanished.
2. `bind.ml` `has_attr` compared case-sensitively: the lowercase `recursive`
   written in R2023/R2024 did not register, changing SVBLK presence.
3. `codegen.ml` guard written as `if c then match ... with ... | _ -> failwith (...);`
   swallowed every following expression into the match's LAST arm, so the
   descriptor constants were emitted only for arguments the guard REJECTED.  The
   tell was that DECPOLY still linked and printed correct numbers while its
   `.REL` lost 20 bytes of data records.  Repaired with a sealed
   `let () = if c then begin match ... end in` binding and a comment naming the
   hazard.
4. Assignment to a name with no declaration raised bare `Not_found` from
   `List.assoc`; it now fails loud as an implicit-FLOAT `[TBD]`.

## 4. Verification

* e2e gate 211/211 byte-exact; negative panel 46/46 refused (4 new members).
* Corpus sweep: 6 EXACT / 0 DIFFERS / 35 REFUSED.
* Tier-2 targeted link + console, 17 specimens: 17/17 `.COM` byte-identical and
  17/17 console byte-identical, every value mathematically correct
  (8, 3, 11, 6, 24, 6/11, 3.7000, 12.2300, 2.33, 1).
* DECPOLY specifics: console byte-identical over a REAL two-line input script;
  simulator `CPU executed 1773926 t-states` identical for both images;
  `x*x + 2*y + z` for (1.4, 2.3, 5.67) = 12.23 printed as `12.2300` ✓.
* DECPOLY's `P(x,y,z)` -> `2` is DR's own semantic defect (callee formal
  re-declared at 15,4 vs caller 11,2); reproduced exactly, recorded, not hidden.

## 5. Deliberately out of scope (perimeter negatives in force)

N52 PUT of a DECIMAL formal; N53 DECIMAL formal in a conjunction; N54 formal
passed through to another call; N55 store through a formal; N33 decimal literal /
expression argument against a DECIMAL formal; attributed `RECURSIVE` with more
than one formal; trailing-`stop` main layout (NTEST1/NTEST2 shape).

## 6. Late discovery: DR's fixed-bin arithmetic peephole set (C099)

The multi-clause `%replace` lexer fix was validated against DR with three new
specimens (R2043 macro form, R2045 the same program with inline literals, R2046
a macro used only in supported shapes) plus the old P044 battery.  Two things
came out of it:

* **`%replace` is confirmed textual.**  R2043 and R2045 have byte-identical DR
  code traces.  The `%replace` directive lines also keep their own source line
  numbers in DR's listing (lines 3-6 of R2043), which is why my implementation
  blanks the directive text rather than deleting it.
* **A whole route family my compiler has never been checked against is wrong.**
  DR elides `x + 0` and `x * 1` to a load/store pair, turns `x * 2` into
  `DAD H`, commutes `3 * x` into `LHLD x / LXI D,0003 / ?IM22N`, and evaluates
  `3 + 2` in the decimal runtime with 1-byte pool cells plus `?QDI15`.  My build
  had no sample of any of these (the corpus never uses them), so it emitted
  plausible alternatives.  All four now fail loud, with the DR trace quoted in
  the refusal, and are pinned by N56-N60.  One over-broad first attempt at the
  guard broke N301/N306 (`0 - 7`, `0 - 2`), which is itself evidence that the
  decimal-pool route is ADD-specific; the guard was narrowed accordingly.

This is the second time in two slices that writing a probe to validate a small
fix uncovered a new lowering law (last time: `s - i` -> `?IS22N`, C092).  The
general lesson holds: a route being "seen" says nothing about the rules hiding
inside it.
