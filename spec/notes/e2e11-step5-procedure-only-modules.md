# E2E-11 step 5 — procedure-only modules (no OPTIONS(MAIN))

Milestone: implement DR's top-level entry/return handling for a file whose outermost
block is a procedure that is **not** the program entry point, then prove it end-to-end
with two modules compiled by my own compiler, linked with authentic LINK-80 + PLILIB
and run. Claim references: **C136 / C136b** (DR behaviour), **C137** (toolchain).

Outcome: `A` accepted byte-exact, 15 new gate specimens (405/405), 1 new negative
(66/66), corpus 12/41 -> **13/41 EXACT, 0 DIFFERS**, and E29F becomes the first
program whose caller *and* callee objects are both mine, producing 5/5 numerically
correct FLOAT results across the module boundary.

---

## 1. What DR does, and which of my assumptions were wrong

Nine DR objects (Q1-Q9 in `e14src/`, batches `golden/e2e147..e2e149`) plus
`golden/first/A`:

| probe | shape | DR | mine, before | mine, after |
|---|---|---|---|---|
| Q1 | module, `returns(float)`, `return (2.0)` | compiles | **crash** `int_of_string` | BYTE-EXACT |
| Q2 | module, no RETURNS, formal + assignment | compiles | main prologue emitted | BYTE-EXACT |
| Q3 | module, `returns(fixed)`, `return (x)` | compiles | main prologue emitted | BYTE-EXACT |
| Q4 | **main**, `y = x/2` (fixed literal) | compiles | BYTE-EXACT already | BYTE-EXACT |
| Q5 | module, float formal + extra local | compiles | (not probed before) | BYTE-EXACT |
| Q6 | module, no RETURNS, body ends `stop;` | compiles | refused (crash before that) | BYTE-EXACT |
| Q7 | module, two formals | compiles | (not probed before) | BYTE-EXACT |
| Q8 | module, `returns(fixed dec)`, plain FIXED formal | compiles | refused | **still refuses** (my-gap) |
| Q9 | module, `returns(fixed dec)`, DEC formal | compiles | (not probed before) | BYTE-EXACT |
| A | corpus module, `return (x/2)` | compiles | wrong refusal message | BYTE-EXACT |

Three assumptions of mine died here:

* **"A's gap is the mixed-mode FLOAT divide."** It was not. Q4 (main, same
  expression) was already byte-exact, so the arithmetic route existed. The gap was
  the entry structure — and the fixed literal divisor becomes a 4-byte MBF pool cell
  with `?FD44M` doing float/float, with **no** runtime conversion.
* **"A's code is `LXI B,0200 / CALL ?START / LXI H,*S / MVI A,18 / CALL ?FD44M`."**
  That was my own earlier summary of the DR *listing*, and it was wrong: the golden
  contains no `?START` at all and no `MVI A,18`. Re-reading the golden bytes before
  writing code is what caught it (the standing rule: never cite a program without
  checking what it contains).
* **"The module entry needs its own ABI."** It does not. A's code 0000-0006 is
  E27C's `p1` body prologue at 001F-0023, byte for byte (`5E 23 56 EB` + `SHLD`
  of the incoming pointer). So the right implementation was to *reuse* nested
  procedure lowering, not to write a second entry sequence.

## 2. Implementation (contained, no ARCH-1 migration)

**`ocaml/lib/bind.ml`**

* `top_is_proc (b : Ast.block)` — one exported predicate: `bkind = Bproc` and a name
  and **no** `OPTIONS(MAIN)`. Exported because two layout passes must agree on the
  file kind; two copies of the question is the C134 failure mode.
* `prog_layout.pl_top : proc_layout option` — the outermost block laid out by the
  **same `section2` pass that handles nested callees**, by passing
  `formals = bparams` and `nm = Some name`. That last part is load-bearing:
  `section2`'s `dedup` test is `nm <> None`, so keeping `nm = None` would have
  charged `declare x float` its full 4 bytes where DR charges 2 for the pointer
  cell, and A's DATA area would have come out 0008 against DR's 0006.
* The module's proc_layout is also a member of `pl_procs`, so procedure lowering,
  the prescan contexts (`proc_vk_rows`, `pd_procs`, `pd_fl_procs`) and callee-formal
  lookup all find it through channels that already existed. Zero new consumers.
* Refused at the binder, with reasons: a RECURSIVE procedure-only module (no DR
  sample of a shadow-cell/SVBLK prologue for a top-level module).

**`ocaml/lib/codegen.ml`**

* `emit_program` branches on `pl_top`: module -> `lower_proc st ls {blk; bpos}`;
  main -> the unchanged prologue + statement loop. `lower_proc` supplies the copy-in
  ladder, the pointer-formal deref ABI, the RETURNS-driven exit (`RET` / `JMP
  ?FPRET` / `JMP ?DCRET`), the implicit RET for no-RETURNS, and forward-CALL
  resolution at the entry byte.
* `st.top_proc` gates `lower_proc`'s **tail guard** and **append** bookkeeping,
  which key on `not st.in_proc` because they describe a procedure appended *after*
  a main block. A module is the whole file: DR emits no JMP guard, no append address.
* Main-only framing removed for modules: the `LXI B,0200 / CALL ?START` prologue and
  the epilogue `CALL ?STOPX`.
* `END-PROGRAM` operand: `Abs 0` for a module, `Code 0` for main (C136b #1).
* Prescan now receives the module's own return type through **both** channels that
  consult it — `pd_fl_ret` (float cell, C136b) and `pd_ret` (DEC target-precision
  cell) — so the pool is never sized under one model and lowered under another.
* Implicit RET skipped for a module body ending in STOP, **scoped to
  `st.top_proc`**: Q6 pins the module case only, so nested procedures keep the byte
  they have always emitted.
* `rows_of` takes the auto area from the module's section layout
  (`pl_rows` / `pl_total`) instead of `bind_rows`, and refuses any declaration
  `bind_rows` places that `section2` did not (STATIC / FILE / FORMAT in a module —
  a mixture with no DR sample). One authority per file kind.

**Two refusals I wrote and then removed in the same session**, because DR's own
goldens closed them: `stop;` inside a module (Q6) and `RETURNS(DECIMAL)` on a module
(Q9). Both were conservative guesses about the *entry* shape that turned out to be
unchanged from the nested case. Q8 remains a refusal, and its message now correctly
points at the real cause (FIXED -> DEC conversion, `?QI15D`), not the entry structure.

## 3. The regression suite did not cover the integration risk — measured, not argued

The instruction was explicit that 390 MAIN-positive specimens are a regression suite,
not proof of zero integration risk. That was **right, and it cost 45 minutes to
learn**: every `.REL` was byte-exact throughout, including E29F's and E29G's, and the
first end-to-end run printed **nothing**:

```
E29H (no cross-module call):  literal float = 1.7500000E+00 / half = 8.7500000E-01
E29G (cross-module call):     before call        <-- dies at `y = a(3.5)'
```

Same behaviour for DR-built objects, so it was not my codegen. The cause was C137:
`LINK D:E29G` (companion present on `D:` but not named) reports `UNDEFINED SYMBOLS: A`
and **still writes a .COM** that runs, prints nothing and exits 0. My harness printed
that verdict through a `[:120]` slice which cut off right before the name, so the link
looked clean. Naming the objects (`LINK D:E29G,D:A`) resolves `A 0208` and everything
works — which is exactly what DR's corpus instructions for MPMCALLA/MPMCALLB prescribe.

Harness fixes, both kept: the message cap is 400 and the link segment is now parsed
for the undefined list, printing `LINK-FAIL <n>: COM=True but UNDEFINED SYMBOLS: ...`;
and `LINK_NO_EXTRA=1` reproduces the unnamed form so the failure is reproducible
rather than remembered.

Consequence for acceptance policy: **"A's isolated .REL is byte-exact" was true at a
point when A could not run in any program.** REL parity says nothing about link-time
resolution. Do not accept on REL parity alone; do not treat "a .COM appeared" as a
link-stage pass.

## 4. Evidence, by class

`.REL` parity (raw bytes, `cmp`) — 15 specimens now in the gate: A, Q1-Q7, Q9, B,
E29F, E29G, E29H, E29I, E29J.

Link + run integration, DR-built objects vs my own byte-identical objects:

| program | .COM (mine vs DR) | runtime output | note |
|---|---|---|---|
| E29F + A | IDENTICAL, 8320 B | identical | 5 FLOAT results across the boundary |
| E29G + A | IDENTICAL, 8192 B | identical | `a(3.5) = 1.7500000E+00` |
| E29H | IDENTICAL, 8192 B | identical | control: no cross-module call |
| E29I + B | IDENTICAL, 7296 B | identical | `b(i) = 3i+1` for i = 0..4 |
| E29J + A | IDENTICAL, 8192 B | identical | `external` keyword: no effect |
| A alone | IDENTICAL, 2432 B | — | LINK accepts a main-less object |

Runtime transcripts differ only in emulator statistics (`I/O ran for 4016 ms` vs
`4005 ms`, clock frequency) — no behavioural difference.

Independent numeric verification of E29F, parsed from the CP/M run of the mine-built
executable and checked against arithmetic my compiler never performed:

```
a(3.5)  = 1.7500000E+00   a(1.25) = 6.2500000E-01   a(256) = 1.2800000E+02
a(0.5)  = 2.5000000E-01   a(40)   = 2.0000000E+01
expected (x/2): 1.75 0.625 128.0 0.25 20.0   -> PASS (5/5)
```

E29I's `b(i) = 3i+1` gives 1, 4, 7, 10, 13 — a *loop-carried* cross-module call with a
variable argument, so the result is not an artifact of one literal.

Gates after the change: **405/405 byte-exact, 0 fail** (the 390 pre-existing MAIN
specimens untouched — measured before implementing: 0 of 390 lacked `OPTIONS(MAIN)`),
**negative panel 66/66 refused**, **corpus 13/41 EXACT, 0 DIFFERS, 28 REFUSED**.

## 5. What the four procedure-only corpus files need now

| file | status | first refusal |
|---|---|---|
| A | **accepted** (REL + integration) | — |
| MPMCALLB | refused | `STATIC on CHAR(27)` — C114 places statics below the pool but only BIT(1) initialiser bytes are measured |

**CORRECTION (E2E-12).** The two rows this note gave for `ACK` and `ACKTST` --
"`OPTIONS(STACK(...))` on the outer block", and the earlier claim in
`e2e11-step5-gap-ranking.md` that four corpus files (A, ACK, ACKTST, MPMCALLB) are
procedure-only and all four need the entry route -- were **wrong**, and wrong for a
mechanical reason: I classified files with `'options(main)' in text`.  Both ACK and
ACKTST actually read

```
procedure options(main,stack(2000));
```

which **does** contain OPTIONS(MAIN); the substring test just cannot see a multi-option
list.  So the procedure-only population of the corpus is **2 files, not 4** -- A (accepted)
and MPMCALLB -- and the entry route was never a prerequisite for ACK/ACKTST.  After STACK
was implemented (C138) their first refusals moved to PUT forms: ACK needs the generate
form inside PUT LIST (`put skip list('   ', (decimal(n,4) do n=0 to maxn));`), ACKTST
needs a counted format group (`put edit(...)(skip,a,2(f(2),a),f(6),...)`).  Neither is
close.  Lesson kept: string-matching on source text is not a parser, and "first refusal"
is an artifact of *check ordering* -- my block-option check runs before statement
lowering, which hid two deeper blockers behind a shallow one.
`CALL.PLI` is the corpus program that pairs with `A` (`declare a entry(float)
returns(float)` plus an internal `b`, through a `f(3) entry(...) variable` function
array) — that array form is a separate unprobed lowering, and E29F/E29G were written as
the direct-call equivalent precisely to keep this milestone's evidence about the entry
route rather than about entry arrays.

## 6. Deliberately not done

No ARCH-1 migration, no extraction into a separate instruction layer: the production
change stays inside top-level entry/return handling plus one prescan-context wiring.
E27C's two-chain prototype result and C135 remain architectural evidence with no
production consumer.
