# E2E-40/P8a — the classifier/producer split, and a range that was never DR's

Baseline `c3366fc` (P8). Three tasks, one measurement campaign, thirteen new byte-exact
specimens, one retired refusal. `golden/e43l` (10 programs), `golden/e43b` (**19**, not 20 -- one
was counted twice), see `golden/e44/PROVENANCE.tsv` for the per-program audit [C270],
`golden/e43ll` + `golden/e43lr` (DR's own link + run of E43M1). Spec: [C268], with [C267]
and [C260] corrected in place; [PERIMETER.md] "## [E2E-40/P8a]".

## The reported contradiction, verified before touching anything

The premise was that `member_store_class` decides on resolved DATA addresses while the
value-producing ladder arm decides on textual `Ast.orig` equality, and that `R3`
(`a = g.a + 5`) / `R4` (`g.a = a + 5`) might show a ladder classification riding on
general value production. **The premise was right and the supporting observation in P8
was wrong.** P8 wrote that R3/R4 "prove classifier and emitter agree". They prove their
*output* agrees. Tracing which arm actually ran settles it:

| program | statement | ladder arm fires? | value producer | tail |
|---|---|---|---|---|
| R1 / E42P1 | `a = a + 5` | yes | ladder | `SHLD` |
| R3 | `a = g.a + 5` | **no** | `lower_hl` ADD route | `SHLD` (because the verdict said ladder) |
| R4 | `g.a = a + 5` | **no** | `lower_hl` ADD route | `SHLD` |
| X2 / X4 | `a = g.a - 2` / `- 5` | **no** | `lower_hl` ADD route | `SHLD` |

(Traced with a temporary `prerr_endline` in the arm's guard, built, run, reverted — the
shipped tree contains no trace and the build is from the un-instrumented source.)

The bytes equalled DR's anyway because `lower_hl` and the ladder both call `hl_bias`, whose
`|k| <= 3` → INX/DCX-repeats, else `LXI B,k ; DAD B` selection coincides with the ladder's.
Two independently written predicates, one output, no stated reason they must agree — the
[C260] failure mode, latent rather than active. A byte match cannot distinguish two routes
that converge, exactly as [C264] says about code bytes and addresses.

## The range

`ladder_bias_fits = -8 <= k && k <= 16` was P8's transfer of E22A02..E22A16 / E22B01..E22B08
to a destination class those probes never tested, on the strength of one member sample (+5,
E42P1). DR was shown **28 ladder programs covering 24 distinct biases** (the list first written here
included -30, -5, -2, +1 and +2, which have no artifact -- -30 was a sign slip for E43B30 = +30,
and +/-1 and +/-2 were never probed at a member):

```
-16 -10  -9  -8  -1   3   4   5  14  15  16  17  18  19  20
 30  60 100 127 200 1000 5000 10000 30000 32767
```

Every one: `LHLD <cell> / <bias> / SHLD <cell>`, ladder operand carrying k exactly
(`+100`→`0064`, `+5000`→`1388`, `+30000`→`7530`, `+32767`→`7FFF`, `-9`→`FFF7`), whole-program
CODE `0x3A` unchanged, `.REL` 256/256 identical to mine. So there is no window; the bound is
whether the constant fits the 16-bit `DAD` addend. `+3` vs `+4` (E43L8/E43L9) brackets the
instruction-selection break-even to one unit, confirming [C165]'s `|k| <= 3` rule transfers.

**E42N3 was a refusal of a program DR compiles.** `a = a + 100` at a member: mine refused,
DR ladders. Retired from the negative panel (129 → 128) and re-registered as byte-exact
specimen E43B1C; E43B5C (+32767) covers the extreme. An ordinary variable at +100
(`artefacts/E22A17`) also ladders in mine, so the widening is not member-specific — but no DR
oracle exists for *that* one, and [C268] does not claim it.

## Cross-spelling, measured rather than inferred

`a = g.a + 5` (E43L6) and `g.a = a + 5` (E43L7) are each 256/256 identical to each other, to
E42P1 (`a = a + 5`), and to DR; the linked objects print `105`. The three store fixups are the
same DATA address in all of them. Qualification contributes nothing to the route, which is
[C253]/[C257]'s result extended to the one shape where my code previously keyed on spelling.

## The 32768..65535 interval, and a traceback that is a digit prefix

E43M1 stores `32768` into the member: byte-identical, and DR's own linked object aborts like
E42P2's does (`ERROR (1), Conversion`) — so the check is magnitude-independent, not a >32767
special case, and the interval is measured at both ends at a member destination instead of
composed from LR7 (array) + E42P2 (65535).

Traceback payload comparison, worth remembering before one reads a traceback as addresses:

```
E42P2 (65535):  0612 10B0 3620 3535 3533   -> "6" "65" "655" "6553" "65535"
E43M1 (32768):  0612 1099 3320 3732 3836   -> "3" "32" "327" "3276" "32768"
```

Drop the first word, decode the surviving pairs as ASCII. Mine aborts with byte-equal text
(runtime panel row E43M1).

## Implementation

`member_store` carries its operands — `Ms_literal of string`, `Ms_ladder of Ast.binop * int`.
The ladder arm in `lower_assign` is opened by the verdict for a member destination; an ordinary
variable keeps the textual test. Consequences are enforced, not incidental:

* no `Ms_ladder` member falls through to general value production (the verdict is the guard);
* no `Ms_general` member emits a ladder (`Some _ -> false` closes the arm);
* no member reaches the speculative `SHLD` default — `(_, Some _, Some (Ms_unsampled _))`
  fails loudly in the store match.

Ordinary (non-member) destinations are untouched: `mstore` is `None` for them.

## Gates

`969 byte-exact / 0 fail` (+13, 0 regressions), `128/128` refusals (−1, E42N3 retired),
`11/11` divergences (unchanged — no row moved toward or away from parity), `34/34` runtime
(+6: 91 / 117 / 105 / 105 / 30100 / abort), coverage `85 rows, 0 errors` (`DECL.MEMBER_SCOPE`
`MIXED:46/49`), census `44 programs / 15 EXACT / 0 DIFFERS / 0 UNEXPECTED` (no verdict and no
blocker text moved, which [C265] makes checkable), INVENTORY `+12 / −0`, exit 0.

## Honest accounting of what this changed in behaviour

One shape class changed: member self-updates with `|k|` in 17..32767 (and -9..-30), which were
refusals and are now DR-matching ladders. Everything else was already emitting the right bytes;
what P8a changed there was *why* — the ladder now comes from the same decision that chooses its
store, instead from from two predicates that happened to converge. No divergent row moved; no
ordinary-variable route changed; no corpus verdict changed.

## Two process slips worth recording

* I first wrote the coverage-panel edit against 0-based indices 5/6 while the counts live in
  field 9 and the note in field 15, which overwrote the perimeter letter and the `dr_status`
  value. `coverage_check.py` caught it as a malformed `manual_ref`; both fields were restored
  from HEAD rather than retyped.
* The probe names `E43B100`/`E43B32767` exceeded CP/M's 8-character limit and the oracle
  refused them outright. Legal names are used and the k each one carries is tabulated in
  `golden/e43b/K_TABLE.txt`.

---

# E2E-40/P8b addendum — the endpoint this note claimed, and the counts it got wrong

Baseline `f359b8e`. Spec: [C270]; pre-run hypotheses and results in
`golden/e44/PREDICTIONS.txt`; per-program audit in `golden/e44/PROVENANCE.tsv`.
Everything above this line is P8a's text, unedited; the four corrections below are the
reason this addendum exists.

**(1) `-32768` was claimed and is not DR's.** "the gate is therefore not a window at all: it is
whether the constant fits the 16-bit `DAD` addend" reads an instruction-set property as a
measurement. The ladder arm is gated by `fits t` on the *positive source literal*, so the only
spelling that would produce k = −32768 (`a = a - 32768`) never reaches `ladder_bias_fits`; the
endpoint was dead code AND unmeasured. DR was shown both sides: −32767 ladders with `LXI B,8001`
(E44A1, 256/256, console −32667); −32768 converts the literal, subtracts generally and **parks**
(E44B1, code 0x4B, 256/256 identical to mine — **no codegen change was licensed or made**), and
DR's own run **aborts** `ERROR (1), Conversion` even though −32668 fits BIN(15). The control
E44C1 (`h = h - 32768`, ordinary destination, h in scope) aborts identically, so the check travels
with the literal's route, not with the member store — which is why [C267]'s store-range story and
[C270]'s conversion-range story must be kept apart.

**(2) The bias list was 5 entries too long.** −30 was a sign slip for E43B30 = **+30**; −5, −2,
+1 and +2 have no artifact at a member anywhere in the repository (verified by scanning every
source that declares the `1 g, 2 a fixed` shape: only E43L3's −1, as `DCX H` x1). Measured set:
**24 values** over 28 P8a ladder programs, +−32767 from P8b = 25. Everything between sampled
points is interpolation and is now written that way.

**(3) Program counts were wrong.** `golden/e43b` holds **19** programs, not 20 — one was counted
twice. New P8a programs: 29 (e43l 10 + e43b 19), of which 28 are ladder/cross-spelling and one
(E43M1) is the converted literal. E42P1/E42P2 are P8's, not P8a's.

**(4) "E43L6/E43L7 are whole-file identical to E42P1" was false.** They differ in exactly 4 file
bytes (0x31, 0x32, 0x3A, 0x3B): the two initialization immediates (`MVI M,05`/`MVI M,64` vs
`MVI M,64`/`MVI M,01`) and the record-length bytes following them — my init is `g.a=100; g.b=1`,
E42P1's is `g.a=5; g.b=100`. What IS identical is the self-update sequence at code 0x16–0x20 and
every DATA fixup, including both member-address fixups. E43L6 and E43L7 are whole-file identical
to each other, so the qualification symmetry still holds — with the stronger, narrower statement.

**Gate after P8b:** 972 byte-exact / 0 fail (+3, 0 regressions), 128/128 refusals (unchanged — no
refusal retired here, because the shape was never one), 11/11 divergences (E40S2/E40S4/E40Q4
untouched), 37/37 runtime (+3), coverage 85 rows / 0 errors, census 44 programs / 15 EXACT / 0
DIFFERS / 0 UNEXPECTED, INVENTORY 972 (+3/−0), exit 0. All three new specimens also have DR's
`.COM` identical to mine and byte-equal consoles.
