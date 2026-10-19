# E2E-8 bounded assessment — PUT EDIT format-list encoding, DO/BY rules, IFACT scope

Date: 2026-10-19, after the `4bc9af8` checkpoint (LOAN1 accepted; that commit is
the new baseline for the implementation-line counter and the last recorded FULL
`--link-run` runtime baseline).

Everything below is observed from DR specimens compiled with `$L$D$C$S`
(`golden/e2e11/`). No implementation had been written when this note was made.

---

## 1. IFACT's requirement set

```pli
ifact:  procedure options(main);
        declare (i, n, F) fixed;
        do i = 0 by 1;                    -- (A) index DO, BY only, no TO/WHILE
           F = 1;
           do n = i to 1 by -1;           -- (B) variable FROM, TO, negative step
              F = n * F;
           end;
           put edit('factorial(',i,')=',F)
               (skip, a,f(2), a, f(7));   -- (C) PUT EDIT with a 5-spec format list
        end;
end ifact;
```

* External route set (from `golden/first8080u/IFACT/IFACT.REL`, 384 bytes,
  CODE 0x81 = 129, DATA 0x21 = 33) is exactly 8 entrypoints:
  `?EDITF ?EDTOV ?IM22N ?QICOP ?QIOOP ?SLCTS ?START ?SYSPR`. **Only `?EDITF`
  and `?EDTOV` are new to my build**; the other six are already emitted.
  A seventh route, `?SLVTS` (char-varying stack load), appears in the PUT EDIT
  family but NOT in IFACT -- it shows up in R1003/R1008/R1020, and my build
  already emits it from PUT LIST (`ocaml/lib/codegen.ml` references it 7 times),
  so it is not a new route either.
* Fresh DR re-run of `IFACT.PLI` is **byte-identical to the curated corpus
  .REL** (`cmp` clean), so the corpus golden and my re-run harness agree.
* IFACT does not terminate (outer `do i = 0 by 1` has no exit), like RFACT:
  console verification must use `tools/prefix_check.py --console`, not a
  timeout-truncated capture.
* My build's current refusal is `PUT EDIT deferred [TBD]`, reached from the
  pool prescan before the DO refusals fire; the DO forms separately refuse as
  `DO step unproven [TBD]` (B, and `by k` in general) and `DO without TO
  deferred [TBD]` (A). Verified by compiling all three in isolation.

## 2. PUT EDIT lowering (R1001-R1010, R1018-R1020, IFACT)

Statement skeleton -- identical to PUT LIST's preamble, then a format-table
call, then **one value-push + one `?EDTOV` per item**, then `?QIOOP`:

    LXI  D,0252                 print descriptor (as PUT LIST)
    LXI  B,0000                 operand triple-patched to the NEXT statement
    CALL ?SYSPR
    LXI  H,* S(0000)            the compiled FORMAT TABLE, always allocated FIRST
    CALL ?EDITF                 once per statement
    --- per ITEM, source order ---
    <value preparation>         (see table below)
    CALL ?EDTOV                 once per item, consumes the next format record
    --- end per item ---
    CALL ?QIOOP

Value preparation per item kind (same forms PUT LIST already uses):

| item | sequence | evidence |
|---|---|---|
| char literal | `LXI H,* S(off)` `MVI A,len` `CALL ?SLCTS` | R1010, IFACT |
| binary variable | `LHLD var` `MVI A,09` `CALL ?QICOP` | R1001, R1006, IFACT |
| char varying variable | `LXI H,var` `CALL ?SLVTS` | R1003, R1008, R1020 |

Number of `?EDTOV` calls = number of ITEMS (4 in IFACT), while the format list
has 5 records: the leading `skip` is consumed by `?EDITF`/`?EDTOV` pairing, and
the observed alignment is that the *first* `?EDTOV` applies the *first
item-consuming* record (`a`), with `skip` preceding it in the table. That is an
observation about record order, not yet a proven rule about how `?EDITF`
consumes leading specs -- the runtime console comparison in the implementation
step is what will confirm the pairing (a mis-pairing shifts every field).

## 3. Format-table encoding (decoded from 11 tables)

Table = `80 00` header, then one record per format spec in source order, then
`81` terminator. Record layout is opcode + fixed parameter count per opcode:

| spec | bytes | samples |
|---|---|---|
| `f(w)` | `00 w FF` | R1001 `f(3)`, R1002 `f(12)`, R1019 `f(1)`, IFACT `f(2)`, `f(7)` |
| `f(w,d)` | `00 w d` | R1018 `f(6,2)` -> `00 06 02` |
| `a` | `03 FF` | R1003, R1010, IFACT |
| `a(w)` | `03 w` | R1008 `a(5)` -> `03 05`, R1020 `a(3)` -> `03 03` |
| `skip` | `0C FF` | R1004, R1005, R1010, IFACT |
| `page` | `0F FF` | R1007 |

Full-table checks (all `cmp`-derived, not inferred):

    R1001  (f(3))                80 00 | 00 03 FF                     | 81
    R1004  (skip, f(3))          80 00 | 0C FF | 00 03 FF             | 81
    R1005  (f(3), skip)          80 00 | 00 03 FF | 0C FF             | 81
    R1006  (f(3), f(4))          80 00 | 00 03 FF | 00 04 FF          | 81
    R1010  (skip, a)             80 00 | 0C FF | 03 FF                | 81
    R1020  (a(3), f(2,1), skip)  80 00 | 03 03 | 00 02 01 | 0C FF     | 81
    IFACT  (skip, a, f(2), a, f(7))
                                 80 00 | 0C FF | 03 FF | 00 02 FF | 03 FF | 00 07 FF | 81

UNPINNED, and deliberately not modelled: the meaning of the header's second
byte (0x00 in all 11 samples) and of the `FF` slot in `skip`/`page` (only
`skip`/`page` defaults sampled; `skip(n)`-style counted skips are unprobed).
Records for edit operators other than `f`/`a`/`skip`/`page` (`x`, `b`, `e`,
`p`, `Z`, ...) are unsampled and will refuse.

Allocation order: the format table occupies `*S(0000)` and the *string item*
literals follow it in source order [IFACT: table 0000-000E, `'factorial('`
000F, `')='` 0019; R1010: table 0000-0006, `'XY'` 0007; R1020: table
0000-0009, `'AB'` 000A]. The prescan must therefore count the table length
before any item literal, or every `*S` offset after it shifts -- that is the
same failure mode as the slice-3 ROUND pool-prescan defect.

## 4. DO / index / BY rules (R1011-R1017)

    do i = a to b by k,  k >= 1  (RISING, R1011 to 5 by 2, R1015 to 3 by 1)
        <init i = a>                        LXI H,a (or a peephole form) / SHLD i
      head: LHLD i / LXI B,-(b+1) / DAD B   HL = i - (b+1)
            MOV A,H / ORA A / JP skip       skip when i-(b+1) >= 0, i.e. i > b
        <body>
        LHLD i / (INX H) * k / SHLD i       k rungs
        JMP head
      skip: ==== past the loop

    do i = a to b by -k,  k >= 1  (FALLING, R1012 to 1 by -1, R1013 to 3 by -2)
        <init i = a>
      head: LHLD i / (DCX H) * b / MOV A,H / ORA A / JM skip
                                                skip when i-b < 0, i.e. i < b
        <body>
        LHLD i / (DCX H) * k / SHLD i
        JMP head

    do i = a by k;  (NO TO, NO WHILE -- IFACT's outer loop, forever)
        <init> / <body> / LHLD i / (INX H) * k / SHLD i / JMP <body start>   no test

    FROM may be a VARIABLE: `do n = i to 1 by -1` inits with LHLD i / SHLD n
    [R1014 = IFACT's inner loop] instead of a constant load.

Three things this data settles that I would otherwise have guessed:

* **The falling test subtracts the TO BOUND, not the step.** R1013
  (`to 3 by -2`) emits **3** `DCX H` in the test and **2** in the increment.
  IFACT (`to 1 by -1`) has 1 and 1, where the two hypotheses coincide -- so
  IFACT alone could not have distinguished them, exactly like the ROUND tie
  rule in slice 3.
* **The rising test uses `LXI B, -(b+1)` + `DAD B`**, not rungs, in both
  sampled bounds (3 and 5); and `ORA A` (not `ORA L`) with JP/JM as the
  skip-if-false test -- the same flag convention as the `i < kk` arm [Z401].
* **`do i = 0 by 1 while (i < 4)` and `do i = 0 to 3 by 1` compile to
  byte-IDENTICAL code** [R1016 vs R1015], i.e. DR rewrites an index relation
  `i < c` into a bound `c-1`. `do i = 0 while (i < 4)` [R1017] shows the same
  test with NO increment rung, which is why that program never terminates.
  Whether other index relations (`i > c`, `i ^= c`) get the same rewrite is
  unsampled.

Scope discipline: IFACT needs (A) forever+BY, (B) variable-FROM TO+BY(-1), and
`by 1`/`by -1`. R1011/R1013/R1015/R1016/R1017 fall out of the same parameterized
rule at no extra cost, so they will be registered as positives; the `while`
rewrite will be implemented only for the sampled `index < literal` shape
[R1016/R1017], and everything else keeps refusing (`i > c`, `i >= c`, `UNTIL`,
`REPEAT` combinations, BY with a variable step, bounds that do not fit).

## 5. Probe inventory

`golden/e2e11/` now holds 21 DR specimens: IFACT (re-run of the corpus file) +
R1001-R1010 (format table shapes) + R1011-R1017 (DO/BY) + R1018-R1020
(`f(w,d)`, `f(1)`, mixed `a(3)/f(2,1)/skip`). All 21 compiled under DR with a
`.PRN` and a `.REL`; 20 of them are candidates for byte-exact registration
once implemented, and the ones that do not terminate or produce no output will
be `.REL`-only specimens with the prefix protocol for runtime.

## 6. Tiered validation plan for E2E-8 (new policy, first application)

Measured on this tree, so the estimates are not guesses:

* **Tier 1 -- full REL parity, mandatory after every implementation change.**
  `python3 tools/e2e_gate.py` = **0.3 s** for 160 byte-exact `.REL` comparisons
  + the 39-member negative panel; parse 467 / bind 47 / ir 10 / rel round-trip
  438 / safety 28 together **< 10 s**; incremental `dune build` **< 1 s**
  (clean rebuild ~2-3 min, only run when measuring warning parity).
* **Tier 2 -- targeted link/console, for new/modified specimens plus a
  representative sample.** Measured cost: **22 s per specimen** (6 names
  including both arms = 2 m 11 s). Proposed standing subset for E2E-8,
  14 names ≈ **5-6 min**:
    - new family: `IFACT` (prefix protocol, run separately) + 4 PUT EDIT
      specimens (`R1001`, `R1006`, `R1010`, `R1020`) + 3 DO specimens
      (`R1012`, `R1013`, `R1014`)
    - affected existing families: `X201` (GET/PUT I/O ABI), `R813`
      (DEC print + ROUND in a loop), `R901` (numeric GET), `R912`
      (loop + condition), `LOAN1` (milestone: PUT/QIOOP/DEC/print ABI)
  Non-whitelist/older specimens are NOT re-run unless their lowering changed.
* **Tier 3 -- full `--link-run` (160 specimens, ~50 min): reserved** for the
  IFACT-acceptance commit, for any change to the linker/oracle harness
  (`oracle/linkrun.py`, `oracle/cpmwork.py`, `tools/e2e_gate.py` link arm), or
  when targeted evidence suggests a broader regression. Last full run:
  `4bc9af8`, 118/118 `.COM` identical + 118/118 console byte-equal, 0 fail --
  recorded baseline, not to be re-litigated.

Terminology discipline: a Tier-1 pass is reported as **"full REL regression
passed"**, Tier-2 as **"targeted link/runtime regression passed (N of M
specimens)"**. Neither will be described as full runtime validation.

## 7. Estimated implementation scope

* PUT EDIT: statement matcher + format-table emitter (pool item, allocated
  before item literals) + `?EDITF`/`?EDTOV` sandwich + reuse of the existing
  per-kind value preparation. Refusals for unsampled operators, unsampled item
  kinds (DEC items in an edit list: unsampled), counted `skip`, and any
  item/spec count mismatch beyond the sampled shapes. ~90-120 lines.
* DO/BY: forever+BY form, rising/falling TO+BY forms with the rung/`LXI B`
  laws, variable FROM, and the sampled `while (index < literal)` rewrite.
  ~60-80 lines.
* Gate/notes/registration: ~40-60 lines.
* Total estimate: **200-260 gross lines**, i.e. well inside the reset
  ~2,000-line checkpoint. The main risk is the pool-prescan interaction
  (section 3), which is why the table length must be counted in the same pass
  that counts item literals.
