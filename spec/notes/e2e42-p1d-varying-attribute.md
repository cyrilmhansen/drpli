# E2E-42/P1d — the VARYING attribute is a storage class, and one binder read fixed three symptoms

E2E-42/P1c closed its report by recording an OPEN DIVERGENCE: COPYLPT's
`open file(sysout) title(line)` emits `?SLCTS` + `MVI A,<len>` here where DR's COPYLPT object
emits `?SLVTS`, and the row blamed structure-member resolution [C288].  The blame was in the wrong
place twice over.  `(line character(14), buff character(254)) varying` is **not** a
level-numbered structure — the parser flattens a parenthesised group of unlevelled items into
ordinary scalar declarations, and DR's own dump calls them `CHAR(14) VARYING **AUTOMATIC**`, not
`MEMBER` — and the defect was not in the TITLE arm at all.  One line in the binder fixed the
classification, the storage layout and the helper dispatch together, and ten new whole objects
became byte-exact.  [C290]

## 1. WHAT DR DOES, IN THREE OF ITS OWN WORDS

```
   dcl (line char(14), buff char(254)) varying, k fixed bin(15);     E46J2
   dcl (line char(14), buff char(254))         , k fixed bin(15);     E46J5
```

Two sources that differ by one word.  DR's `$L$D$S` dumps:

```
   E46J2  c 0000 LINE CHAR(14) VARYING AUTOMATIC      E46J5  c 0000 LINE CHAR(14) AUTOMATIC
          c 000F BUFF CHAR(254) VARYING AUTOMATIC               c 000E BUFF CHAR(254) AUTOMATIC
          BLOCK AT LINE 3, AUTO STORAGE 272 BYTES               BLOCK AT LINE 3, AUTO STORAGE 268
```

`000F - 0000 = 15 = 14 + 1`, and `000E - 0000 = 14`: the attribute makes a CHARACTER cell `n+1`
because a varying reference is a (length, address) descriptor, exactly as `CHARACTER(n) VARYING`
declared inline has always done here [C174].  The object says the same thing E46J2's dump does —
its chain carries `?SLVTS` twice where E46J5's carries `?SLCTS` twice.  And the pre-type spelling
`dcl nm varying char(14)` (E46J7) produces an object identical to the inline spelling's apart from
names.

## 2. WHERE THE FLAG WAS LOST, AND WHY THE SYMPTOM WAS A HELPER

The parser is innocent: for a group declaration it attaches the trailing `varying` to `dattrs`, the
attribute list, and leaves `dtype` per item.  `bind.ml`'s `resolve_type` then built the runtime type
from `d.dtype` **only**.  So the flag existed in the AST, was never consulted, and the name was
classified `RTchar(14, false)` — a fixed cell.

Everything downstream inherited that one read:

* **layout** added 14 bytes instead of 15, so `buff` and everything after it sat one byte low.
  COPYLPT itself still refuses, at its `PUT ITEM (PAGE)' [C280], so the measurement is E46J13 --
  COPYLPT's declaration block verbatim, one PUT -- which measured 276 against DR's 278;
* **`pli80bind -d`** printed `LINE CHAR(14) AUTOMATIC`, so the dump disagreed with DR's;
* **both string operations** chose their helper from that classification.  `lower_open` and the PUT
  item route are pure dispatch on `Vvar`/`Vfix` [C174][C288] — they were never wrong, they were
  being handed a lie.

That is why the fix is one function and not two: a repair at the TITLE arm would have produced an
object with `?SLVTS` at 014C and a 276-byte frame, half-right and undetectable by a CODE-only
comparison [C264].  `apply_varying_attr` (bind.ml) now wraps the type-building match inside
`resolve_type`, the single function through which flat items, structure members, based views,
procedure locals, formals and RETURNS all pass, so no route can see one class and another route see
a different one.

## 3. THE SECOND HALF OF THE LAW, WHICH IS A LANGUAGE RULE

VARYING attaches to CHARACTER and to nothing else.  DR's verdicts, from `golden/e42p1d`:

| probe | declaration | DR |
|---|---|---|
| E46J9 | `dcl k fixed bin(15) varying` | CONFLICT pass 1, **no `.REL`** |
| E46J10 | `dcl b bit(4) varying` | CONFLICT, no `.REL` |
| E46J15 | `dcl p pointer varying` | CONFLICT pass 1 **and** COMP REQ pass 2, no `.REL` |
| E46J8 | `(line char(14), buff fixed bin(15)) varying` | CONFLICT, no `.REL` — but its listing still dumps `BUFF CHAR(4) VARYING` |
| E46J19 | `(a char(4), b fixed bin(15), c char(6)) varying` | CONFLICT, no `.REL`; dumps `A … VARYING` 0000, `B FIXED BINARY(15,0)` 0005, `C CHAR(6) VARYING` 0007 |

The last two show the attribute distributing **per item**: the CHARACTER items take it, the FIXED
one is the error, and DR carries on listing.  Before this fix E46J8, E46J9 and E46J19 each produced
an object of our own — bytes for programs DR refuses to compile.  They now refuse, and the message
names DR's word.  `apply_varying_attr` fails rather than silently ignoring, because a silently
ignored VARYING is exactly the defect this episode was about, deferred to a later symptom.  The
five are on the negative panel as `dr-refuses` [C256]: parity in OUTCOME (no object), not parity in
diagnosis, which a single-shot front end cannot have.

## 4. WHAT IS STILL REFUSED, AND WHAT THE REFUSAL NOW SAYS

> **[E2E-42/P1e] Five of the six are CLOSED and byte-exact** -- E46J6, J11, J12, J18 and J21
> are specimens now [C291], and this section is kept as the record of what P1d could and could
> not say, not as the current perimeter.  The sixth, E46J14's typeless `dcl x varying;', is
> still open, and the reason is stated in [C291]: type inference is a different piece of work
> from member aliasing, and P1e deliberately did not smuggle the second in through the first.

Six probes are `my-gap`: DR emits a real object, we do not.

```
   dcl 1 rec, 2 line char(14) varying, 2 nxt fixed bin(15);   (E46J6, J11, J12, J18, J21)
   dcl 1 rec, 2 line char(14),         2 nxt fixed bin(15);   (E46J12, E46J18)
   dcl x varying;                                             (E46J14)
```

E46J13 is the control that makes this honest: the SAME member, written as a group item, is now
byte-exact 512/512.  So the storage class is no longer what is missing for the level-numbered form
— bind lays that member out at DR's exact offsets, and our `$S` dump of E46J21 equals DR's line for
line (`.LINE CHAR(14) VARYING MEMBER` at 0000, `.NXT FIXED BINARY(15,0)` at 000F).  What is missing
is the **alias**: bind's unqualified-member registry admits only `FIXED BINARY(15)` and `POINTER`
[E2E-39/P2], so `line` and `rec.line` resolve to nothing and PUT/OPEN refuse.  Widening that
registry to CHARACTER would resolve a bare member name in *every* context — assignment, comparison,
EDIT, subscript — through routes that have no member sample, which is how the TITLE divergence in
§1 was built in the first place.  The refusal is kept, and since this episode it says what it is:

```
   codegen: [TBD] `line' resolves to the bound member `REC.LINE' (CHAR(14) VARYING at DATA 0000) ...
```

All five member probes used to refuse with a message that was **false about why** — measured on
HEAD (876fa0f) in a clean worktree, not remembered:

```
   E46J6, E46J12  codegen: [TBD] undeclared line (no declaration in scope)
   E46J21         codegen: [TBD] undeclared rec.line (no declaration in scope)
   E46J11, E46J18 codegen: OPEN TITLE(line) names no declared variable [TBD] (line 4)
```

while `pli80bind -d` on the same files printed `c 0000 .LINE CHAR(14) VARYING MEMBER` — the binder
knew the member, its type and its offset, and had simply never handed the bare name to codegen.
Nothing was undeclared.  A gate cannot see that: `coverage_check.py` validates citation FORM,
`file_prose_check.py` polices sentences, and a wrong diagnostic emits no bytes.  Since P1d the
message names the owner, the internal member, the type as bound and the DATA offset, and says which
DR objects this refusal is waiting on.

E46J14 is the other kind of stale diagnostic: HEAD **emitted an object** for it — code 38, data 2 —
against DR's code 38, data **1** (`dcl x varying` has no cell in DR's block of AUTO STORAGE 0).  One
byte of data area, allocated by nobody, is the sort of difference a CODE-only comparison never
reports [C264].  It refuses now.

E46J14 (`dcl x varying;`, attribute with no type) is accepted by DR as `X(0) VARYING AUTOMATIC` in
**AUTO STORAGE 0** — no cell at all — with its store through `?DLDOP` and its print through
`?PNVOP`, i.e. the dump says VARYING and the code treats it as a number.  Before the fix this
compiler emitted a 2-byte declaration where DR emits 1 and a 19-byte print block where DR emits 16.
It now refuses, because nothing pins what a READ of such a name does.

## 5. VALIDATION

`golden/e42p1d` holds DR's `.PRN`/`.REL` for E46J1–J21 (`--switches '$L$D$S'`).  Whole-object
comparison, RELOC and CHAIN records included [C264]:

* **byte-exact, 10**: E46J1 (control), J2, J3, J4, J5, J7, J13, J16, J17, J20 — added to SPECIMENS;
* **`dr-refuses`, 5**: E46J8, J9, J10, J15, J19 — added to REJECTS with the DR verdict attached;
* **`my-gap`, 6**: E46J6, J11, J12, J14, J18, J21 — added to REJECTS labelled as ours.

Gate state after the change: `e2e_gate` 1014/1014 byte-exact, 0 fail; negative panel 160/160 refused
clean; divergence panel 9/9; `bind_gate` 43 exact / 2 known-gap / 2 FAIL (unchanged from the
baseline, which is 43/2/2); `parse_gate` 9/0; `ir_gate` 2 byte-exact / 3 struct-exact / 5 gap / 0;
`coverage_check` 92 rows, 0 errors; `file_prose_check` clean; `dune runtest` 0.

**The same gate, re-run by the external builder on `6e81d4de6` (bs28, build #20, 436 s), reports
`byte_exact 1014/1014 | refusals 160/160 | divergences 9/9 | runtime 52/52 | coverage 93 rows/0
err/0 warn`.**  The runtime row matters more here than on a codegen-only change: this fix moves
DATA addresses — `buff` from 000E to 000F and everything after it — so 52 programs that actually
run under CP/M and have their output compared executed against the new layout without one
difference [C265].

Corpus effect: the census re-ran and the only changed message is `EXPR2`'s, whose declaration is
`dcl inp char(10) varying static;` — DR rejects that with CONFLICT (`STATIC` is not a varying
storage class [C114]) and we now reject it at the same place for the same reason.  COPYLPT still
refuses, but at `PUT PAGE` — a P2 feature — and no longer anywhere in its TITLE or its storage.

## 5b. DUMP TEXT, NOT JUST BYTES

A byte-exact `.REL` says the addresses agree; it does not say the compiler and the oracle agree
about what the declaration MEANS.  `pli80bind -d` prints DR's `$S` format, so the two texts can be
diffed line for line — and for both the group shape and COPYLPT's declaration verbatim they are
identical:

```
   E46J2  BLOCK AT LINE 3, AUTO STORAGE 272 BYTES      (DR and ours, same three lines)
          c 0000 LINE CHAR(14) VARYING AUTOMATIC
          c 000F BUFF CHAR(254) VARYING AUTOMATIC
          c 010E K FIXED BINARY(15,0) AUTOMATIC
   E46J13 BLOCK AT LINE 3, AUTO STORAGE 278 BYTES      (COPYLPT's declaration, verbatim)
```

Before P1d the same command printed `c 0000 LINE CHAR(14) AUTOMATIC` and `c 000E BUFF …` in a
270-byte frame, i.e. the model itself was wrong and the object was merely consistent with the wrong
model.  That is the difference this episode was about: a self-consistent wrong binding produces
plausible bytes, and only a comparison against DR's dump or object shows it.

## 6. WHAT P1e HAS TO MATCH

The five level-numbered objects are banked and are the target, not an approximation of it: PUT LIST
of a varying member `LXI H,<member>` + `?SLVTS` (E46J6, code 53 / data 17) and of a fixed member
`LXI H,<member>` + `MVI A,0E` + `?SLCTS` (E46J12, 32/16); OPEN TITLE the same two ways (E46J11 42/17,
E46J18 38/16); and the qualified spelling's store through `?SMCVM` (E46J21, 43/19).  All the numbers
here, DR's dumps and the before/after table are read out of `spec/lab-evidence/e2e42-p1d/`:
`HYPOTHESES.md` holds the predictions made before any oracle ran, `DR-RESULTS.md` holds which of
them DR falsified, and `VARYING-DISPATCH.txt` holds every measurement.

One operational note for whoever runs the oracle next: these `.PLI` files are CRLF-terminated CP/M
records.  A probe written with bare `\n` reads to UNEXPECTED EOF in DR and the batch reports a
`FAIL` with an empty listing — that cost the first E46J17–J20 run its goldens.
