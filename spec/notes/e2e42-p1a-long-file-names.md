# E2E-42/P1a — long FILE names: the six-character symbol, and no refusal

Phase P1a of E2E-42.  Before this commit the compiler **refused** any `dcl <name> file`
whose name was longer than six characters.  That refusal was my invention, not a DR
behaviour: [C277] had measured DR's truncation rule off five historical objects and then
recorded, correctly, that the *lowering* was missing — and somewhere between that note
and `codegen.ml` the missing lowering became a refusal that named DR.

## 1. The rule, restated from the objects

Two different things live in a FILE declaration and only one of them is truncated:

* the **LINK-80 COMMON group symbol** is the first six characters of the uppercased name,
  slash-delimited: `INPUT_FILE -> /INPUT_/`, `OUTPUT_FILE -> /OUTPUT/`, `SYSPRINT ->
  /SYSPRI/`, `SOURCEFILE -> /SOURCE/`, `PRINTFILE -> /PRINTF/`, `REPFILE -> /REPFIL/`,
  `EMPFILE -> /EMPFIL/`.  **The underscore survives truncation**, so this is a hard cut at
  six characters and not a cut at the first non-alphanumeric.
* the **control block** stores the FULL uppercase name: 33 zero bytes, a one-byte length,
  then the name.  So `DEF-COMMON-SIZE = 34 + len(full name)` — 44 for `INPUT_FILE`, 45 for
  `OUTPUT_FILE`, 42 for `SYSPRINT`.

The length byte counts the full name.  Only the symbol is clipped.

## 2. The probes, and what each one pins

| probe | what it declares / does | DR | result |
|---|---|---|---|
| E46D1 | `abcdef1` + `abcdef2`, **colliding, equal sizes**, all six statements | ACCEPTS, `0x0690` | **byte-exact** (640 B) |
| E46D2 | `dcl abcdefg file;` and **no OPEN at all** | ACCEPTS | **byte-exact** (256 B) |
| E46D3 | `in_file` + `insize` — underscore at position 3, and a 6-char control | ACCEPTS, `0x0690` | **byte-exact** (640 B) |
| E46D4 | `abcdef1` + `abcdefghij` — **colliding, unequal sizes** 41 vs 44 | ACCEPTS | **byte-exact** (512 B) |
| E46D5 | `abcdef1`/`abcdef2` referenced in an alternating order | ACCEPTS | **byte-exact** (640 B) |
| E46D6 | `averylongname` (13) **with a literal TITLE** — the two features together | ACCEPTS, `0x0E90` | **byte-exact** (384 B) |
| E46D7 | `alpha1` + `beta2`, **non**-colliding 6- and 5-char names | ACCEPTS, `0x0690` | **byte-exact** (384 B) |

E46D2 matters on its own: it proves the truncation is a **declaration** rule, not an OPEN
rule.  A long-named FILE that is never opened still gets an `ABCDEF` group symbol.

E46D7 is the control for the collision rows: two names that do *not* collide after the cut
produce two distinct groups (`ALPHA1` 40 bytes, `BETA2` 39), so truncation and merging are
different things.  E46D3 is the boundary control on both ends — `IN_FIL` proves the
underscore survives the cut, `INSIZE` proves a six-character name is not padded to seven.
E46D6 proves the TITLE bit composes with a long name instead of competing with it.

## 3. SEL-COMMON is keyed on the VARIABLE name, not the symbol. [C284]

This was the one thing the "just clip the string" plan got wrong, and E46D5 caught it.

E46D5 declares `abcdef1` and `abcdef2` — one shared symbol `ABCDEF`, two variables — and
references them in this order:

```
  dcl abcdef1 file, abcdef2 file;      <- 2 DEF-COMMON-SIZE (abs 0029 = 41 = 34+7, BOTH named ABCDEF)
  open file(abcdef1) stream input;     <- switch abcdef2 -> abcdef1
  open file(abcdef1) stream input;     <- same variable, no switch
  get  file(abcdef1) list(i);          <- same variable, no switch
  get  file(abcdef2) list(i);          <- switch abcdef1 -> abcdef2
  get  file(abcdef2) list(i);          <- same variable, no switch
  close file(abcdef1);                 <- switch abcdef2 -> abcdef1
```

DR emits **5** `SEL-COMMON` records, and every one carries the same clipped name `ABCDEF`:
two at the declarations (each `DEF-COMMON-SIZE` is followed by its own `SEL-COMMON`, even
for the second colliding declaration) and three at the three switch points above.

The counterfactual was run, not argued.  With `st.cur_common` keyed on `file_sym fu`
instead of `fu`, this compiler emits **3** SEL-COMMON — at bit offsets 302, 830 and 1606 —
and loses the two at **2748** and **4180**, which are exactly the `abcdef1 -> abcdef2` and
`abcdef2 -> abcdef1` switches.  The declaration records survive because the DEF path emits
its SEL-COMMON unconditionally.  The object is still 640 bytes and no longer compares equal
(`cmp` fails).  Reverting restores byte-exactness, verified above.

`codegen.ml` therefore keeps `st.cur_common` on the **full** name and writes `file_sym nm`
into the **record**.  The two are deliberately different, and a comment says so; a future
"simplification" that keyed on the symbol would emit 3 SEL-COMMON and break E46D5.

The same trace shows up in E46D4 (`abcdef1`, 7 chars, and `abcdefghij`, 10 chars — the same
symbol at two DIFFERENT sizes, `0x29` = 41 and `0x2C` = 44, because each control block
stores its own full name): 2 `DEF-COMMON-SIZE` plus 6 `SEL-COMMON` = 8 LINK records, one
SEL for each of the four variable switches in `open/open/get/close`.  Mine matches, 512
bytes, byte for byte.

## 4. What LINK-80 does with a collision is linker behaviour, measured — not invented

I did not want to write down a claim about collisions without running one, so all four
linked images below came out of the real harness (`oracle/linkrun.py link`, LINK 1.31 +
`artefacts/PLILIB.IRL`).  Evidence: `spec/lab-evidence/e2e42-p1a/LINK-COLLISION.txt`.

| probe | declarations | LINK-80 says | the control block, as linked |
|---|---|---|---|
| E46D4 | `abcdef1` + `abcdefghij` | `/ABCDEF/ FIRST COMMON NOT LARGEST` | len byte `0x0A`, name bytes `ABCDEFG` — **7 of 10 characters** |
| E46D5 | `abcdef1` + `abcdef2` | *(nothing)* | len byte `0x07`, name `ABCDEF2` |
| E46F4 | `abcdefghij` alone | *(nothing)* | len byte `0x0A`, name `ABCDEFGHIJ` — complete |
| E46D6 | `averylongname` alone | *(nothing)* | len byte `0x0D`, name `AVERYLONGNAME` — complete |

Five things this pins:

1. **A colliding pair becomes ONE group at ONE base address.**  E46D4's and E46D5's `.COM`
   each contain a SINGLE control block where DR's `.REL` carries two `DEF-COMMON-SIZE`
   records, so at run time the two variables are the same file.  (E46D1 declares the same
   equal-size pair; only E46D4 and E46D5 were put through LINK-80.)  That is a **program bug**, and it is LINK-80's
   behaviour, not DR compiler behaviour.
2. **The size LINK-80 keeps is the FIRST group's** — which is what the warning says.  In
   E46D4 the first block is 41 bytes (33 zeros + length + 7 name characters) and the second,
   which lands at the same base, needs 44.  41 bytes hold exactly seven name characters, so
   the surviving record is cut after `ABCDEFG` while its own length byte still says 10 — a
   **self-inconsistent control block**, read at 1989..198F of `E46D4.COM`.
3. **With equal sizes nothing is clipped and the second record wins.**  E46D5's two blocks are
   both 41 bytes, no warning fires, and the surviving name is `ABCDEF2` — the *second*
   variable's, because it overwrote the first at the shared base.
4. **Without a collision a long name is stored in full.**  E46F4 and E46D6 are the controls:
   10 and 13 characters, both complete.  So item 2's clipping is a collision artifact and not
   a six-character limit on the stored name — the control block always carries the full name,
   only the LINK symbol is clipped.
5. **None of it is the compiler's business.**  Every object above starts as a byte-exact
   `.REL` from DR and from this compiler; the divergence appears only when LINK-80 resolves
   two groups to one name.  So this compiler reproduces DR's *records* and adds no diagnostic
   DR does not have — a collision warning here would make us disagree with the oracle about a
   program DR accepts, which is the one thing this project cannot afford.

## 5. Effect on the corpus

`COPY`, `COPYLPT` and `RETRIEVE` were first-blocked by the long-name refusal.  Their census
messages now name their **next** real blocker — `ENVIRONMENT`, `PUT ITEM (PAGE)` and
`PRINT` respectively.  All three still sit in REFUSED; no program moved to EXACT.  The
census counts are unchanged (44 HISTORICAL / 41 AUTHENTIC / 15 EXACT / 26 REFUSED / 3
DR_REJECTED / 0 DIFFERS), re-recorded and verified identical.

No census row any longer reports the 6-character refusal, which is the honest way to see
that the blocker moved rather than disappeared.

Gate after P1a: 7 new BYTE-EXACT specimens, 0 regressions, 990 → 997.
