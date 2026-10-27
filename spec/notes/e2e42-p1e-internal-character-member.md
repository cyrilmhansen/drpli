# E2E-42 / P1e — the internal CHARACTER member: resolution, then license

Claims: [C291] (the three licensed routes and the kind split) and [C292] (DR's `DUPLIC' does not reach a
CHARACTER member name).  Panel: `AGG.INTERNAL_CHAR_MEMBER`, `NEG.MEMBER_USE_PERIMETER`.

Splits P1e into the two routes DR actually measured:

* **P1e-A** — an internal CHARACTER member as an OPERAND: `PUT LIST` (E46J6 varying, E46J12 fixed)
  and `OPEN … TITLE` (E46J11 varying, E46J18 fixed).  Four objects.
* **P1e-B** — the QUALIFIED member as a store DESTINATION: `rec.line = 'AB'` through `?SMCVM`
  (E46J21, which prints the same cell afterwards).  One object.

All five are byte-exact whole `.REL` files against `golden/e42p1d/`, chain records and relocation
operands included — the standard this panel has held since [C264], not "the code section agrees".

## What the bank says

```
dcl 1 rec, 2 line char(14) varying, 2 nxt fixed bin(15);   E46J6   put list(line)
  0000  21 <data 0000>      LXI H,*D(0000)   <- the member's OWN cell, DATA-relative reloc
  0003  cd <?SLVTS>
  …      cd <?PNCOP> ; cd <?QIOOP>                          code 56 / data 17

dcl 1 rec, 2 line char(14), 2 nxt fixed bin(15);           E46J12  put list(line)
  0000  21 <data 0000> ; 0003  3e 0e ; 0005  cd <?SLCTS>    code 32 / data 16
```

E46J6 and E46J12 differ in their SOURCE by the single word `varying` and in the object by the helper
and the `MVI A,0E`.  That is [C174]'s storage-class dispatch arriving at a member — the member's
class, not the statement's.

The TITLE pair is the same three instructions with OPEN's tail: E46J11's operand half at code 0006
is E46J6's operand half byte for byte, and the `MOV B,A` that follows takes the length from the
operator exactly as it does for a scalar title [C288].  E46J12/E46J18 together retire the question
P1c's note raised but could not settle — a level-numbered FIXED member takes `?SLCTS`, not `?SLVTS`,
so nothing about a member implies the varying route.

E46J21 is the store:

```
rec.line = 'AB';  put list(rec.line);
  0006  21 <data 0002>   LXI H, rec.line      <- member cell: 2 pool bytes ahead of it
  0009  11 <data 0000>   LXI D, *S            <- 'AB'
  000C  3e 0e            MVI A, 0E            <- declared capacity
  000E  06 02            MVI B, 02            <- literal length
  0010  cd <?SMCVM>                            code 43 / data 19
```

E46J16 is the same five instructions on a flat `dcl (line char(14)) varying`; the two objects differ
only in DATA size (0x13 vs 0x110), because the member's cell is 17 bytes and the flat group's is
270.  So the member store is the measured scalar route at a different address and nothing else —
which is why it went through the existing `store_char` with its `?dst` thunk rather than a new
encoder.  And `rec.line` prints from the same `*D(0002)` it stores to: [C253]'s "two spellings, one
variable" repeats verbatim for this type.

## The design: a kind of its own

bind registers both keys (`line`, `rec.line`) with the member's absolute frame offset, as it already
does for FIXED BINARY(15) and POINTER.  codegen then maps them to `Vimem {owner; name; cap;
varying}` — **not** to `Vvar cap` / `Vfix cap`.

**[C291]**'s one choice is the whole perimeter.  A CHARACTER variable is a legal operand in an assignment, a
comparison, an EDIT item, a concatenation, a subscript, arithmetic and a whole-record move; DR has no
object for any of those on a member.  Had the member been spelled `Vvar`, every one of those routes
would have started accepting it silently, because none of them tests anything but the kind.  As an
unmatched constructor it refuses everywhere except the three arms that name it, and it refuses BY
NAME.

Sizing the cell is separate and does not authorize anything: `rows_of` gives the member its real
`Bind.bytes_of` size, which is why `auto_bytes` now equals DR's AUTO STORAGE (17 for E46J6's
varying `char(14)` + `fixed bin(15)`; 16 for E46J12's 14 + 2).

Two refusals that were NOT member-specific when P1e started, and are now — both were generic
fall-throughs whose wording described an unrelated pre-existing gap, so a reader could not tell that
a boundary was involved:

* `line + 1` said "arithmetic on char variable" — true of flat variables too, so the member stop was
  invisible.  It now names `REC.LINE`.
* `if line = 'AB'` said "condition form not in E2E-3b subset" — but flat string comparison has been
  byte-exact since E2E-29, so that wording was simply wrong about this case.  It now names
  `REC.LINE`.

## [C292]: the census caught a false DR claim

The first version of this step widened bind's `check_member_names` (DR's `DUPLIC`, from E39X2) to
every registered member type.  `corpus_census.py --verify` failed immediately — not on a count, but
on MPMCALLB's recorded refusal *message*, which had moved from an honest `[TBD]` sizing stop to:

> bind: member `line' of structure CLICMD@262 collides with a declaration of the same name …
> [DR: DUPLIC]

MPMCALLB declares `2 line character(128)` inside `1 clicmd` and `declare line character(80)` in the
same block, uses both spellings separately, and DR prints `NO ERROR(S) IN PASS 1` /
`NO ERROR(S) IN PASS 2` with a real `.REL`.  So the widened check was asserting a diagnostic DR does
not print, on a program DR accepts — [C256]'s exact error class, caught by a snapshot rather than by
reading.

Two rules came out of it:

* `DUPLIC` stays on the types it was measured on.  `unshadow_char_members` withdraws a bare
  CHARACTER member key when the same frame holds a cell-owning declaration of that name — in either
  declaration order, which is why it runs on the finished row list and not during the walk.  Without
  it, MPMCALLB's bare `line` would have resolved to `clicmd.line` by `List.assoc` order and handed
  `addr(line)` a 128-byte member instead of the 80-byte buffer: a live wrong address, not a refusal.
* The QUALIFIED key is untouched, and a name shared by two structures still goes to QUALIFY
  (E46K12) — there the stop is required by correctness, since one key would hold two cells.

Honest limit: MPMCALLB cannot be run to completion here (it stops on [C114]'s unsampled
`STATIC on CHAR(27)`), so no object pins *which* cell DR's bare `line` means there.  The ordinary
declaration winning is the reading that makes MPMCALLB's own source work, and it is recorded as this
compiler's rule, not as DR's.

## The perimeter: fifteen rows, no DR claim

`E46K1`–`E46K15` are on the negative panel under a THIRD category, `unmeasured`.  The panel has only
ever had `dr-refuses` and `my-gap`, and both are assertions about DR; registering an unprobed guard
as `my-gap` would have claimed DR compiles fifteen shapes nobody has put through the oracle, and as
`dr-refuses` would have claimed the opposite.  This milestone adds no DR objects, so the honest label
is the one that says "neither verdict is known; this is our stop, and here is what would retire it".

Twelve rows stop on a message P1e wrote, naming the member: bare store (K1), fixed-member store (K2),
comparison (K3, and K14 where the member is the whole condition), PUT EDIT (K4), varying move (K5),
arithmetic (K6), concatenation (K7), SUBSTR (K8), multi-item PUT (K9), ambiguous name (K12), STATIC
head (K13).  Three stop on guards that predate P1e and also fire for ordinary variables — PUT FILE
(K10), `addr()` (K11), GET EDIT (K15) — and are pinned precisely because they prove resolving the
name did not open a route.

K13 is worth its row: `dcl 1 rec static, 2 line char(14) varying` refuses on bind's unaliased-member
path, which is the STATIC gate holding.  The first version of the probe carried a `2 nxt fixed
bin(15)`, and DR's own [C114] static-sizing stop fired first — a row that looked like it tested the
alias rule and tested nothing of the kind.  Dropping the sibling made it the control it was meant to
be.

## Panel

| check | before P1e | after |
|---|---|---|
| byte-exact specimens | 1014 / 1014 | **1019 / 1019** (+E46J6, J11, J12, J18, J21) |
| negative panel | 160 / 160 | **170 / 170** (−5 promoted, +15 perimeter) |
| divergence panel | 9 / 9 | **9 / 9** |
| runtime panel (`--runtime`) | 52 / 52 | **52 / 52** |
| corpus census | 15 EXACT / 0 DIFFERS / 26 REFUSED / 0 UNEXPECTED | unchanged, messages included |
| bind gate | 43 exact / 2 known-gap / 2 FAIL | unchanged (P008, P063A refuse on `FIXED BINARY(31)`/`(16)` precision, unrelated to this step) |
| coverage rows | 93 | **95**, `coverage_check` 0 errors / 0 warnings |
