# E2E-40/P10 — E45S6: a parenthesized ADD on the right of an ADD. Two gaps, not one.

**Scope.** Close the `my-gap' refusal registered in P9 for `put list(a + (b + c))'.  No new DR oracle
experiment was run and none is claimed: DR compiled E45S6 in P9, and its `.REL', linked `.COM' and
console output have been committed since (`golden/e45/E45S6/', `golden/e45l/E45S6.COM',
`golden/e45r/E45S6.output.txt').  What is predicted below is my own output, not DR's, and every
"before" number was measured on the pre-change build.

**Starting HEAD: `2ca66b8` (E2E-40/P9a, pushed).** Baseline re-verified on that commit rather than
assumed: 982 byte-exact / 0 fail, 129/129 refusals, 9/9 pinned divergences, 45/45 runtime rows,
coverage 86 rows / 0 errors / 0 warnings, census 44 programs / 15 EXACT / 0 DIFFERS / 0 UNEXPECTED
with `--verify' clean, gate exit 0 (`spec/lab-evidence/e2e40-p9a/p9a-gate-full.log').

## 1. The refusal, reproduced

    $ ocaml/_build/default/bin/pli80c.exe artefacts/E45S6.PLI /tmp/e45s6.rel
    Fatal error: exception Failure("codegen: PUT numeric item form unproven [TBD]")

The message string appears twice in `num_width` (codegen.ml:8434 and 8472 in the pre-change file);
the one that fired is the second, the catch-all.  Which one, and why, is settled by trace rather than
by reading, below.

## 2. Two independent problems, and the first fix exposed the second

P9 registered E45S6 as a *PUT-item-classifier* gap.  That was half right and it cost a wrong
inference: had I stopped at "classifier fixed, program compiles", the program would have compiled and
been **wrong by 11 bytes**.

**Problem A — width inference (the actual refusal).**  `classify_item` admits a parenthesized item
(`Ast.Econd inner -> Some (PInum inner)`, [N304], byte-exact since E2E-8), but the recursive width
function `w` inside `num_width` had cases for `Eident`, `Ebinary`, `Eprefix`, `Eqstruct`, `Eqptr`,
`Esuffix`, `Enumber` and **no `Econd`** — so a nested group fell to the catch-all.  Temporary trace
(removed before commit) printed the node that arrives:

    TRACE-ITEM (BIN Add ID:a (COND (BIN Add ID:b ID:c)))

so the item is `Ebinary(Add, Eident a, Econd(Ebinary(Add, Eident b, Eident c)))`; the outer binary is
accepted by `w`'s `Ebinary` case, which recurses into both operands, and the *inner* `Econd` is the
first and only refusal point.  Width is max-of-IDENT-leaf-widths, so traversing parens cannot invent
a number: it reads the same binder rows the unwrapped spelling reads, giving 9 for all of `a`, `b`,
`c` — and DR's own item prologue is `MVI A,09`.  Precedent for treating parens as transparent is in
four predicates of this same file (`unwrap_e`, `add_left_needs_push`:750, `writes_de`:2879,
`rhs_is_imem`:2736) because DR lowers a parenthesized expression exactly like the unwrapped one
[P401, `(i+i)`].

**Problem B — evaluation order (exposed by fixing A).**  With only `| Ast.Econd x -> w x` added
(temporary patch, built, measured):

    code=84 data=12, rc=0        # compiles at last
    cmp vs golden/e45/E45S6/E45S6.REL  ->  11 differing bytes

(The intermediate `.REL' was overwritten by the next build before the evidence directory existed;
`spec/lab-evidence/e2e40-p10/ORDER-EVIDENCE.txt' says so plainly rather than implying it was kept.)

The 11 bytes are the fixup operands and the record lengths, not instructions: DR's expression loads
are the *same five instructions* in a different order.

The instruction count is the same and so is the total length: both sides emit 17 bytes for the
expression.  What differs is the order, and the order is visible in the **relocation records**, which
is the only place a `LHLD <cell>` operand exists in a `.REL` [C264].  From `tools/reldump.py`, over
DR's image and mine after both fixes (full output in
`spec/lab-evidence/e2e40-p10/ORDER-EVIDENCE.txt`):

    DR   : 0x0 0x2 0x4 0x6 0x8 0xa   0x2 0x4 0x0   0x51
    mine : 0x0 0x2 0x4 0x6 0x8 0xa   0x2 0x4 0x0   0x51
           ^^^^^^^^^^^^^^^^^^^^^^^   ^^^^^^^^^^^   ^^^^
           DATA initializers          the ADD       code-length reloc

The first six fixups are the six DATA initializers and agree exactly; the last code-region one is the
length.  The three in the middle are the expression, and they read `b, c, a`.  Mine with only the
classifier fix ran `0x0, 0x2, 0x4` = `a, b, c` -- left-first -- and differed from DR by 11 bytes with
the same instruction count.  Cells are identified from DR's own DATA initializers (7, 11, 13 are
distinct), so this is neither a layout argument nor a naming argument: **DR evaluates the
parenthesized right group first and parks its sum while it loads `a`.**

Cells identified from DR's own DATA initializers (`a`=7, `b`=11, `c`=13 are distinct, and the DATA
layout is identical in both images — the first five expression-and-store fixups agree at
0x0,0x2,0x4,0x6,0x8), so this is not a layout argument and not a spelling argument: **DR evaluates
the parenthesized right group first and parks its sum while it loads `a`.**  The two disassemblies:

    DR (linked image, operands concrete)          mine, classifier fix only
    LHLD b   ; PUSH H ; LHLD c ; POP D ; DAD D     LHLD a   ; PUSH H
    PUSH H ; LHLD a ; POP D ; DAD D                    LHLD b ; PUSH H ; LHLD c ; POP D ; DAD D
                                                     POP D  ; DAD D

The instruction sequence itself was already committed in P9, at `golden/e45/ADD_REGIONS.txt'
lines 53-58: `37: LHLD b | 3A: PUSH H | 3B: LHLD c | 3E: POP D | 3F: DAD D' then
`40: PUSH H | 41: LHLD a | 44: POP D | 45: DAD D', under the heading "Parens change the ORDER, not
the route".  P9 wrote that sentence and still registered the program as a classifier-only gap.

Both are value-correct (31 = 7+(11+13)) and DR's own linked object prints exactly that.  A byte
difference in the fixup stream is invisible to the console, which is why execution could not have
found it [C264].

## 3. The rule, and the four witnesses that bound it

`paren_add_right r && (add_left_needs_push r || writes_de st r || rhs_is_imem st r)` selects
`lower_hl st r; PUSH H; lower_hl st l; POP D; DAD D`, placed **before** the existing route tests in
the generic `FIXED ADD` arm.  The gate is

    | Ast.Econd { Ast.e = Ast.Ebinary (Ast.Add, _, _); _ } -> true

and the conjunction is load-bearing.  Without it the new route would also fire for shapes that are
byte-exact today on the left-first routes, and four registered witnesses say so:

| shape | program | DR's order | status after P10 |
|---|---|---|---|
| `a + (b + c)` — parens, inner **ADD** | **E45S6** | **right first** | 256/256 identical (new) |
| `n + (n*3)` — parens, inner MUL | MB34 | left first | identical (unchanged) |
| `(n+1) + (n*3)` | MB35 | left first | identical (unchanged) |
| `a + (b/d)` — parens, inner DIV | R722 | left first | identical (unchanged) |
| `x + (-32768)` — parens, inner prefix/literal | LR19 | left first | identical (unchanged) |
| `a + b + h`, `a + b + 5`, `h + a` (no parens) | E45S2/S5/S8 | left first, park per [C271] | identical (unchanged) |

So parentheses alone do not flip the order — an unparenthesized compound right operand (`(a+b) + c`
spelled without parens, MB33/E45S4) parks the left and evaluates it first [C271].  What is licensed
here is specifically a **parenthesized ADD group** as the right operand of an ADD that would park
anyway.  Inner `Sub`/`Mul`/`Div`/`Exp` are excluded by construction because the two left-first
samples above are exactly `Mul` and `Div`; inner `Sub` has no sample at all, and neither has a
parenthesized group on the **left**, nor a parenthesized group inside a store's RHS, nor a
parenthesized group in a condition.  Those keep their existing routes and refusals.

**No reassociation.**  The AST is untouched: `a + (b + c)` stays `Add(a, Cond(Add(b, c)))`.  Nothing
normalizes it to `(a + b) + c`, and no operand is reordered in the tree — only which operand DR's
own emitted sequence loads first, plus which value gets parked.  Since these are in-range FIXED
values the sum is identical either way, which is precisely why this defect class is invisible to
execution: the console witness (31) pins the value, not the order.  The order is pinned by
byte-identity and by DR's fixup sequence.

## 4. What was predicted, by whom, when

To keep the chronology honest: this is not a pre-oracle prediction campaign — DR's answer for E45S6
has been in the repo since P9, and P9's own retirement comment on `REJECTS["E45S6"]` already stated
that DR's three expression fixups read `DATA+2, +4, +0` and that DR therefore evaluates the right
group first.  P9 recorded the fact and drew the wrong scope from it ("the refusal is about my PUT
item classification, NOT about operand preservation"), because it never tested what its own compiler
would do once the refusal moved.  Measured in P10, in order: the classifier-only patch and its
11-byte gap, then the route patch and its 0-byte gap.

## 5. Registrations

`E45S6`: retired from the negative panel (129 → 128) and registered as a byte-exact specimen
(982 → 983) and a runtime row (45 → 46) with expectation `31`, kind `independent`, against DR's
`golden/e45r/E45S6.output.txt` (nine spaces then `31`, 10 bytes).  The retirement text stays in
`tools/e2e_gate.py` where the entry was, because a `my-gap` row that silently disappears is
indistinguishable from a gap that never existed [C256].  `DECL.MEMBER_SCOPE` is untouched (E45S6 is
not one of its probes); `EXPR.ADD_PRESERVE_ROUTE` gains E45S6 in its probe list, its parity count,
and one clause about the order — no new coverage row, since the contract is the same ADD route.
`PERIMETER` gets a P10 section; `[C272]` is new and states the order rule; `[C271]` gains a pointer
to it.

## 6. Not claimed

* That DR's reason is anything in particular.  What is observed is an emitted order and a parked
  value; "DR evaluates the parenthesized group first" describes code, not an implementation.
* Any general parenthesis support.  One shape: `x + (y + z)` where the ADD would park anyway.
* That a parenthesized inner SUB behaves like either family.  Unmeasured; excluded by construction.
* That the classifier change is safe for non-numeric `Econd` items.  `w` refuses anything its other
  cases refuse; a parenthesized character or based-varying item still reaches its own refusal.
* POINTER/BASED-view members as right operands: unchanged, `E40Q4` still 12 bytes out; a BASED-view
  member's deref ladder is not an `Econd(Add)` node and this rule does not reach it.
* SUB/MUL/DIV ADD-route generalization: untouched by P9 and by P10.

## 7. Correction to my own P9a commit message

P9a's message asserts "0 FAIL/ABORT/Traceback lines in the log".  Literally false: the log contains
five `Traceback` matches, all inside `OK` rows — E42P2, E43M1, E44B1, E44C1, E44D1 print DR's runtime
abort banner `ERROR (1), Conversion  Traceback: ...` because those five rows exist to pin aborts
[C267].  The intended claim (no gate failure) held: exit status was 0.  P9a is pushed, so the
message is annotated here rather than rewritten.  Lesson: a grep pattern is a claim too, and
matching a substring of an expected diagnostic is not the same as the panel failing.

## 8. Gate, measured on this build

    $ python3 -u tools/e2e_gate.py --runtime      # exit status read without a pipe [C249]
    P10_EXIT=0
    e2e gate: 983 byte-exact / 0 fail of 983
    e2e gate: negative panel clean (128/128 refused)
    e2e gate: divergence panel 9/9 as recorded (compiles, differs, shape pinned)
    e2e gate: runtime panel 46/46 as recorded (expectation + termination)
      runtime E45S6    OK  31

Standalone `tools/coverage_check.py': 86 rows, 0 errors, 0 warnings.  Standalone
`tools/corpus_census.py --verify': recomputed counts match, nothing written (44 programs, 15 EXACT,
0 DIFFERS, 0 UNEXPECTED).  `spec/INVENTORY.txt': 983 specimen rows + 128 refusal rows = 1111.
`EXPR.ADD_PRESERVE_ROUTE` recomputes to `EXACT:10` from its own probe column via
`tools/panel_keys.py --row`; no coverage row was added, because the order rule belongs to the same ADD
route contract as [C271].

Explicitly re-verified byte-for-byte after the change, beyond the panel: E45S1-S5, S7, S8, E40S2,
E40S4, N301-N304, P401, E39S2, E39S3, and the four left-first parenthesized guards MB34, MB35, MB36,
LR19, plus R722 (`a + (b/d)').
