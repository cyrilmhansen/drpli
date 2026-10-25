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

(The intermediate `.REL' was overwritten by the next build before the evidence directory existed --
P10a rebuilt an equivalent one by disabling the ADD route in a scratch copy of the tree, see
`spec/lab-evidence/e2e40-p10a/leftfirst-regenerated.rel' and section 9(e);
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

The two disassemblies:

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

and -- as shipped in P10 -- a conjunction, since removed in P10a (section 9) because the first
disjunct was implied by `paren_add_right` itself.  The witnesses that matter here are the two that
actually reach this arm:

| shape | program | DR's order | status after P10 |
|---|---|---|---|
| `a + (b + c)` — parens, inner **ADD**, reaches this arm | **E45S6** | **right first** | 256/256 identical (new) |
| `n + (n*3)` — parens, inner MUL, reaches this arm | MB34 | left first | identical (unchanged) |
| `(n+1) + (n*3)` — parens, inner MUL, reaches this arm | MB35 | left first | identical (unchanged) |
| `a + (b/d)` — parens, `fixed dec(9,2)`, **does NOT reach this arm** | R722 | (not evidence here) | identical (unchanged) |
| `x + (-32768)` — parens, literal, **does NOT reach this arm** | LR19 | (not evidence here) | identical (unchanged) |
| `a + b + h`, `a + b + 5`, `h + a` (no parens) | E45S2/S5/S8 | left first, park per [C271] | identical (unchanged) |

So parentheses alone do not flip the order — an unparenthesized compound right operand (`(a+b) + c`
spelled without parens, E45S4) parks the left and evaluates it first [C271].  What is licensed here is
a **parenthesized group whose inner operator is ADD**, as the right operand of this arm.  Inner MUL is
measured left-first (MB34, MB35); **inner DIV, SUB, EXP and a parenthesized literal are UNSAMPLED at
this arm**, and P10's claim that R722 and LR19 supplied two of them is corrected in section 9 — those
two programs go through a decimal arm and an out-of-range-literal arm respectively.  What the corpus says about the OTHER positions, restated from the panel rather than from P10's
guesswork:

  * **Parenthesized group on the left: sampled once, by MB35** `(n+1) + (n*3)`, which reaches this arm
    (trace: `arm=NEEDS_PUSH`).  DR's bytes are `LHLD n / INX H / PUSH H / LHLD n / LXI D,3 /
    CALL ?IM22N / POP D / DAD D / SHLD m` -- the parenthesized left group is computed FIRST and
    parked, and MB35's expression fixups run `0x1, 0x1, 0x3` = n, n, m, same as MB34's.  What is NOT
    sampled is a parenthesized left group whose RIGHT operand is simple (`(a+b) + c`): MB35's right is
    compound, so the route it took is [C271]'s park and tells us nothing about a left-group rule.
  * **Parenthesized group inside a store's RHS: sampled** -- MB34, MB35, both inner MUL, both
    left-first.  The inner-ADD case at a store RHS is not.
  * **Parenthesized group inside a condition: not sampled anywhere.**  E45S6 is a PUT item, and that
    is the only context where right-group-first has a sample.
  * **Parenthesized groups on both sides: not sampled.**

Those unsampled shapes keep their existing routes and refusals; nothing here generalizes to them.

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
* Any general parenthesis support.  One shape at one arm: `x + (y + z)` inside the generic FIXED
  ADD lowering.  P10 added "where the ADD would park anyway" to that sentence; the extra clause
  named a condition the guard never tested (it was implied), and it is withdrawn -- see section 9.
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
E40S4, N301-N304, P401, E39S2, E39S3, MB36 (`(n*3) + n', XCHG) and the two
parenthesized-right programs that ARE witnesses at this arm, MB34 and MB35 (inner MUL, left-first),
plus R722 and LR19, which stay byte-exact on the routes they actually take -- see section 9c, they are
NOT witnesses about this arm.

## 9. [E2E-40/P10a] The conjunction was tautological, and two cited witnesses never reached this arm

Two defects in P10, one in the code and one in the write-up.  Neither changes any emitted byte.

**(a) `paren_add_right r && (add_left_needs_push r || writes_de st r || rhs_is_imem st r)` reduced to
`paren_add_right r` by definition, not by observation.**

    let paren_add_right e =
      match e.Ast.e with
      | Ast.Econd { Ast.e = Ast.Ebinary (Ast.Add, _, _); _ } -> true
      | _ -> false

    let rec add_left_needs_push e =
      match e.Ast.e with
      | Ast.Econd x -> add_left_needs_push x          (* recurses into the very node *)
      | Ast.Ebinary _ | Ast.Esuffix _ -> true         (* ... and calls any binary compound *)
      | _ -> false

For any `r`, `paren_add_right r = true` means `r = Econd t` with `t = Ebinary (Add, ...)`, so
`add_left_needs_push r` recurses into `t` and returns true.  Therefore
`paren_add_right r => add_left_needs_push r` **for every AST value**, the suffix's first disjunct is
always true whenever the guard is reached, and the suffix selects nothing.  Independently,
`writes_de st r` inside that disjunction could never have been the deciding term: this match sits
inside the `else` of `if writes_de st r` above it, so `writes_de st r` is false throughout the block.
The shipped test is now `paren_add_right r`.  **This is a semantics-preserving simplification, not a
DR finding** -- the proof is three lines of pattern matching, and no oracle was run or needed.
Verified two ways: a comment-stripped diff of HEAD's vs P10a's `codegen.ml` shows exactly ONE
executable line changed (plus one blank line that moved with a relocated comment block); and MB34,
MB35, MB36, R722, LR19, E45S1-S8, E40S2, E40S4, N301-N304, P401,
E42P1, E39S2, E39S7, E40Q1 remain 256/256 identical to their DR goldens.

**(b) `paren_add_right` itself, not the conjunction, is what keeps MB34/MB35 on the left-first route** --
their inner operator is MUL, so the pattern does not match.  P10's sentence "without the conjunction
this route would fire for `n + (n*3)' (MB34) and `a + (b/d)' (R722)" is withdrawn: it credits a dead
disjunct with doing the work of a live pattern.

The arm-level evidence is DR's code, not just its fixups: MB34's bytes are `LHLD n / PUSH H / LHLD n /
LXI D,0003 / CALL ?IM22N / POP D / DAD D / SHLD m' and MB35's are the same with an `INX H' after the
first `LHLD n' -- left loaded, parked, and only then the parenthesized MUL.  MB35 is also the corpus's
only parenthesized group on the LEFT of an ADD, which is why section 3 splits the left-group case into
what is sampled (compound right) and what is not (`(a+b) + c', simple right).

**(c) Two of the four cited left-first witnesses do not reach this arm.**  A temporary branch trace
(since reverted, with `codegen.ml` verified byte-identical to HEAD before any commit) shows R722
`a + (b/d)` and LR19 `x + (-32768)` produce **no trace line from the generic FIXED ADD arm at all**:
R722's four variables are `fixed dec(9,2)` and LR19's literal is outside the in-range path, so both
are lowered elsewhere.  Absence alone would be weak evidence -- P9a's lesson is that a missing trace
line can equally mean the instrument sat in the wrong place -- so both exclusions are also identified
positively, in `spec/lab-evidence/e2e40-p10a/ARM-REACH.txt': R722's golden and this compiler's rebuilt
image both carry the EXTERNAL name `?DDVOP' (DR's decimal operator) and no `?IM22N', which no
FIXED-binary ADD route produces; and LR19's operands are claimed by an earlier arm of the same match
(`Ast.Ebinary (op, l, r) when e25_bin_routes ...' at `codegen.ml' ~3903, the [E2E-25/C178]
out-of-range-literal route, whose `over_lit_operand' classifier at ~1734 recognizes
`Econd(Eprefix(Minus, Enumber))'), which its bytes confirm -- the left operand is loaded and parked and
the literal goes through a decimal conversion, with no `XCHG' anywhere.  They are therefore evidence
about nothing here, and the P10 table overstated
the sampled operator set.  Correct scope: **inner ADD measured right-first (E45S6), inner MUL measured
left-first at this arm (MB34, MB35), inner DIV/SUB/EXP and a parenthesized literal UNSAMPLED at this
arm.**  Full trace table in `spec/lab-evidence/e2e40-p10a/ARM-REACH.txt`.

**(d) P10 also silently reverted a P9a comment.**  The block above `rhs_is_imem` came back carrying
P9's withdrawn text -- "E45S1's inner node `h + a' is covered by `writes_de', not by this function" and
"`put list(h + a)' ... has not been written" -- after P9a had disproved both by branch trace and
replaced them.  P10a restores P9a's version while keeping P10's helper and its own comment, and the
same trace re-confirmed the finding: `rhs_is_imem` selects the park at E45S1 (inner AND outer), at
E45S8, and at E40S2/E40S4's outer add; `writes_de` at none of them.

**(e) Relocation sequence restated from the surviving evidence.**  P10's code comment wrote
`data 0x2, 0x4, 0x0, 0x2, 0x4, 0x0`, repeating the three expression operands as though the expression
relocated six times.  The recorded sequence (`spec/lab-evidence/e2e40-p10/ORDER-EVIDENCE.txt`, NOT
edited) is `0, 2, 4, 6, 8, A | 2, 4, 0 | 51`: six initialization operands, three expression operands
(`b, c, a`), one code-length operand.  The intermediate classifier-only build's `.REL' had been overwritten.  P10a rebuilt an equivalent
one by disabling the ADD route in a throwaway copy of the tree (`if false && paren_add_right r`,
same source, same flags, built later in a scratch directory), and the reconstruction reproduces
P10's measurements exactly --

    classifier fix only, route off   0x0 0x2 0x4 0x6 0x8 0xa | 0x0 0x2 0x4 | 0x51
    shipped (P10/P10a)               0x0 0x2 0x4 0x6 0x8 0xa | 0x2 0x4 0x0 | 0x51
    DR                               0x0 0x2 0x4 0x6 0x8 0xa | 0x2 0x4 0x0 | 0x51

11 bytes separate left-first from DR, and the SAME 11 offsets (file offsets 113, 117-126) separate
left-first from shipped -- all inside RELOC records, no instruction byte moves.  That is [C264]
stated as directly as this program allows.  The artifact is `spec/lab-evidence/e2e40-p10a/
leftfirst-regenerated.rel', recipe in `spec/lab-evidence/e2e40-p10/ORDER-EVIDENCE.txt'.  It is a
reconstruction, not P10's file, so its hash carries no chain of custody back to that run -- which is
exactly why the distinction between a measurement and an artifact matters in the first place

**(f) `EXPR.ADD_PRESERVE_ROUTE`'s boundary column carried two live falsehoods** ("E45S6 is a my-gap
refusal"; "E45S1's inner agreement came from `writes_de`") alongside the corrections that superseded
them, because P9a and P10 both appended rather than edited.  P10a removes the live statements, keeps
one labelled historical clause, and states why `runtime=NONE` on that row is deliberate rather than
stale: XCHG and PUSH/POP are value-identical and both evaluation orders print the same sum, so no
linked-image run bears on *this* row's contract -- the row's evidence is byte-parity.  Probe column
re-resolved with `tools/panel_keys.py --row EXPR.ADD_PRESERVE_ROUTE`: 10 of 10 registered as
byte-exact specimens, so `EXACT:10` stands.


**(g) Gate on the final tree, and one muddled run discarded.**  `spec/lab-evidence/e2e40-p10a/
gate-final.log' + `GATE-SUMMARY.txt': **983 byte-exact / 0 fail**, negatives **128/128**,
divergences **9/9**, runtime **46/46** (E45S6 printing 31), exit 0.  `tools/coverage_check.py':
86 rows, 15 columns, 0 errors, 0 warnings, no ragged rows.  `tools/corpus_census.py --verify':
44 programs, **15 EXACT, 0 DIFFERS, 0 UNEXPECTED** (note that `coverage_check.py' has no
`--verify' flag -- that option belongs to the census, and passing it to coverage_check is an
error, not a silent no-op).  `tools/panel_keys.py --row EXPR.ADD_PRESERVE_ROUTE': **MIXED:10/10**.
Warning sites 116 at HEAD and 116 here, each counted from a clean-tree build (`git archive' for
HEAD, a fresh copy excluding `_build' for this tree), so no new warnings.  `git diff --check`
exit 0.  Nothing was registered by this slice, so every count equals P10's -- a guard
simplification that moved a count would itself be the bug.

Four gate runs happened; only the last is cited.  The first was launched before a comment-only
rebuild finished, so the binary changed underneath it (kept as `gate-run1-overlapped.log',
disclaimed), and comment-only edits landed after runs two and three as well.  `gate-final.log' is the
fourth: final source built, then one execution against that exact binary.  All four returned the same
numbers, which is itself the check that the comment churn was inert.  The witness list in section 8
applies to this slice too -- 25 programs recompiled individually against the final binary, every one
identical to its DR golden, E45S6 256/256.
