# E2E-17 — independent PLI-2000 probes: what DR can compile that I cannot

Baseline HEAD 5507ce4 (531/531, 80/80, 13/41). Final: **532 byte-exact / 0 fail, 110/110 refusals,
corpus unchanged.** Repo added: `thirdparty/PLI-2000` (Steadsoft, shallow clone).

## Step 1 — the four named originals, and how DR judges them

The originals are LF-only (`CONV.PL1` has no CP/M EOF byte at all), so a verbatim DR run would have
mixed a *format* failure in with a *language* verdict. I therefore made two copies of each: the raw
bytes, and a mechanically normalized copy (CRLF + CR before `^Z`) whose language text is
byte-for-byte identical — the normalization script asserts that. Result: DR compiles **all four**
normalized originals with `NO ERROR(S) IN PASS 1/2` and emits a `.REL` for each [golden/e2e214]:

| original | content | DR | mine (before) | mine (after) |
|---|---|---|---|---|
| ARRAY.PL1 | `dcl nums(10) bin(15)`, loop, variable subscripts, call with array element | ok | parse crash | `[TBD] non-simple assignment lhs` (C159) |
| PASSARAY.PL1 | `call inner(argument(I))` — array element as actual | ok | parse crash | same (C159) |
| CONV.PL1 | `b = d + b` with `d fixed dec(3)` | ok | parse crash | `[TBD] mixed decimal/integer arithmetic` (C161) |
| DECY.PL1 | `proc;` with no `options(main)`, `a = a + c` dec(5) | ok | parse crash | same, and it is also a procedure-only module (C136) |

**No dialect incompatibility was found in these four.** `proc`, `dcl`, `bin(15)`, `dec(3)`,
`skip(one)` with a *variable* count, block-comment banners, `call` — all accepted. The only thing
that did not transfer was my own parser's missing `PROC` alias [C160], which turned four DR-clean
programs into four parse crashes and thus into something outside the `[TBD]` refusal discipline.
That is the real Step-1 finding: the divergence was mine, not the dialect's.

They are *not* usable as goldens in the historical-corpus sense without the normalization step, and
I have not counted them in the 13/41 corpus figure.

## Step 2 — arrays: the rule is complete, the feature is not

Seventeen probes; DR compiled every one, including 2-D and both abbreviation spellings. The model is
written up as C159; the short version is that DR's arrays are *address arithmetic with a scalar
bias*: constant subscripts become direct `LHLD/SHLD name+offset` references (with stores splitting
between the scalar form at offset 0 and byte-store form above it), variable subscripts become
`LXI H,name+(lb-1)*size / PUSH H / LHLD i / DAD H / POP D / DAD D`, 2-D is row-major with the last
subscript fastest, no bounds check is emitted even for a provably out-of-range subscript, and an
element passed as an actual puts the element's ADDRESS into the call descriptor.

I did not implement it. Three reasons, all of them this project's standing rules:
* `a(i)` already parses as a *call*, so arrays-vs-calls is a bind-time distinction;
* array sizing has to move automatic-variable offsets in `bind.ml`, which is the layout every one of
  the 532 accepted specimens depends on — the highest-blast-radius file in the tree for a feature
  whose probes all currently refuse;
* and a partially-correct array feature would fail loudly (good) or silently mis-size the data area
  (the C152/C162 class). The rule is established; the safe route needs front-end + layout work as
  its own milestone.

## Step 3 — mixed DEC/BIN: what is genuinely missing

Already supported: pure-DEC arithmetic (E2E-6/E2E-7A) and direct DEC→INT store `i = d` (R506) — the
latter now has its own DR golden and byte-exact specimen (CB6). Genuinely missing: a DEC variable as
an operand inside a *binary* expression (`d + b`), which DR handles by converting the DEC operand in
place (`?DLDOP` then `?QDI15`, with the SOURCE's precision) and then running ordinary binary
lowering, with C150's parking rule intact — DEC left ⇒ XCHG, DEC right ⇒ PUSH H/POP D, because the
conversion's own calls destroy DE. Also missing and unchanged: INT→DEC on store (`?QI15D`, CB10, the
Q8 gap), and mixed MUL, where DR's single sample (CB8) shows a parking rule that differs from
ADD/SUB and one sample is not a rule.

I tried the implementation in an isolated worktree. It routed CB1-CB5/CB7 correctly, and then my own
E2E-16 invariant caught it breaking CB9 [C162]. The reason it cannot be a one-line change is that
`is_dec_expr` classifies a *mixed* expression as a DEC expression (so the pure-DEC path refuses it
first), and `lower_hl` has no idea what type context it is lowering into — adding a DEC case to its
`Eident` arm therefore fires inside pure-DEC expressions too. The clean fix is an explicit
integer-context marker threaded through lowering. That is structural, it is well-specified now, and
it is not something to land at the end of a milestone.

## Step 4 — the recommended sequence, ranked

1. **C162 first.** It is not a missing feature; it is a latent wrong-bytes bug in an *accepted*
   feature area (decimal literals), found by accident from an independent probe. Cost: low (the two
   accounting paths already exist and are now compared). Payoff: correctness of every future DEC
   program. Do this before adding DEC surface area.
2. **Constant-subscript 1-D arrays** (the narrowest array slice): declaration parse, bind sizing,
   direct `LHLD/SHLD name+off` reads, the two store forms. Refuse variable subscripts, 2-D,
   element-as-actual, char/float arrays. This is the one array shape whose probes are pure
   front-end + layout + existing lowering, and it lands ARRAY.PL1's inner statements partially.
3. **Variable-subscript arrays** (the `DAD H` ladder + the pre-biased reloc) — unlocks ARRAY.PL1 and
   PASSARAY.PL1's loops.
4. **Mixed DEC/BIN ADD/SUB** via an explicit integer-context marker, then `?QI15D` (INT→DEC store)
   — unlocks CONV.PL1, DECY.PL1 and CB1-CB5/CB7/CB10.
5. Entry-pointer arrays (`CALL.PL1`: `f(3) entry(float)`, `f(i)(x)`) — biggest gap, last, and only
   after 2-4, because it needs array-of-descriptor layout plus a call through a computed address.

## What the instruments did

Two of the three instruments added in the last two milestones paid for themselves in this one: the
demand/layout invariant caught my own incomplete mixed-mode change (CB9) *and* exposed a
pre-existing under-count, and the committed inventory fired on the panel change. The gate also
proved the parser alias harmless in the way that matters: 531 specimens untouched, byte-for-byte.
