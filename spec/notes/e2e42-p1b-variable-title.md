# E2E-42/P1b — the variable TITLE, and the dispatch that is the real finding

E2E-41/P2b lowered `title(<literal string>)` and refused every other operand by name, with
the comment "a variable title ... routes through `?SLVTS` with the descriptor address in HL,
and no probe of MINE is byte-exact against it".  Four probes of mine are now byte-exact
against it, and they show the sentence was **half right and half wrong**: `?SLVTS` is one of
**two** routes, and which one a site takes is decided by the operand's storage class.
[C288]

Everything below was measured on DR's own `.REL` files under `golden/e42p1c/` and
`golden/e42p1b/`, generated with `PLI_SRC=probes python3 oracle/batch.py` over
`probes/E46F1-5` and resolved through `oracle/passes.json` + `oracle/lib.py:pick()`.

## 1. THE THREE FORMS, AND THE FOUR PROBES

| probe | operand | DR's prologue | OPEN block | w1 |
|---|---|---|---|---|
| `E46F1` | `nm char(14) varying`, `stream output` | `LXI H,<descriptor>` ; `CALL ?SLVTS` | **27 bytes** | `0x0E50` |
| `E46F2` | `nm char(8)` (fixed), `stream output` | `LXI H,<cell>` ; `MVI A,08` ; `CALL ?SLCTS` | **29 bytes** | `0x0E50` |
| `E46F3` | `nm char(14) varying`, `stream input` | `LXI H,<descriptor>` ; `CALL ?SLVTS` | **27 bytes** | `0x0E90` |
| `E46F4` | same, `file abcdefghij` (10 chars) | `?SLVTS`; CB `/ABCDEFGHIJ/` 44 bytes, LINK symbol `/ABCDEF/` | 27 | `0x0E50` |
| `E46F5` | `nm char(14) varying **static**` | `?SLVTS` | — | `0x0E50` |

All four of `E46F1`–`E46F4` are whole-object BYTE-EXACT specimens on the gate panel.
`E46F5` is accepted by DR and refused here, but **not** for a TITLE reason — see §5.

`E46F1` and `E46F2` differ in their source by exactly one declaration:

```
   dcl outf file, nm char(14) varying, k fixed bin(15);      E46F1
   dcl outf file, nm char(8),         k fixed bin(15);       E46F2
   open file(outf) stream output title(nm);                  both
   put file(outf) list('X');                                 both
```

and they differ in the object by the helper name and by two bytes.  That single-variable
difference is what turns "`?SLVTS` is the variable route" into a **dispatch**: a fixed
`CHARACTER(n)` operand keeps `?SLCTS` and passes its **declared** length.  This compiler's PUT
LIST items have chosen between the same two helpers on the same rule since E2E-11 ([C174]);
`TITLE` is that pair's third user, and no new prologue is introduced here.

## 2. WHY THE PROOF IS LINK RECORDS AND NOT DISASSEMBLY

In an unlinked `.REL`, `CALL ?SLCTS` and `CALL ?SLVTS` are both the three bytes `CD 00 00` —
the target lives in a `LINK-CHAIN-EXT` record, not in the operand.  So a mnemonic dump of a
`.REL` cannot actually distinguish the two routines, and any claim about *which* helper DR
calls has to read the chain record's name field.

`spec/lab-evidence/e2e42-p1b/TITLE-DISPATCH.txt` dumps nine objects that way.  The two rows
that decide it:

```
E46F1.REL   code 000A ?SLVTS     (inside the OPEN block, 0006..001F)
            code 0033 ?SLCTS     (the program's own `put file(outf) list('X')')
E46F2.REL   code 000C ?SLCTS     and NO ?SLVTS ANYWHERE IN THE OBJECT
```

`E46F1` therefore carries **both** helpers in one module, selected by the operand at each
site, and `E46F2` — identical except for `varying` — carries only `?SLCTS`.  The linked
`.COM` images in `golden/e42p1b-link/` are the same evidence after resolution, and their
README warns what must not be read off them: `PLILIB` lands at a different base per link
session, so the **addresses are not comparable between images**; only the symbol names carry
a claim.

## 3. DR'S OWN FIVE HISTORICAL SITES AGREE, AND AGREEING REQUIRED RE-READING THE BLOCK TABLE

The census in [C287] counted **30** `TITLE` operands over the 34 measured historical opens,
**25 literal and 5 variable**.  The five variable sites all take `?SLVTS`:

| site | operand | declaration | block | chain |
|---|---|---|---|---|
| `LOAN2:56` | `title(name)` | `name character(14) varying static initial('$con')` | `00CD..00E8` | `?SLVTS` at `00D1` |
| `COPYLPT:38-39` | `title(line)` | `line` is a `character(14)` `varying` STRUCTURE member | `014C..016D` | `?SLVTS` at `0150` |
| `COPYLPT:49-50` | `title(line)` | same | `01E8..020A` | `?SLVTS` at `01EC` |
| `RETRIEVE:31-32` | `title(filename)` | `filename character(14) varying` | `00C1..00E3` | `?SLVTS` at `00C5` |
| `CREATE:22-22` | `title(filename)` | `filename character(14) varying` | `0037..0052` | `?SLVTS` at `003B` |

An earlier draft of this note said "LOAN2 and RETRIEVE take `?SLCTS`", and that was an
artifact of reading only the **first** `?OIOOP` block of each program.  Both programs have two
opens, one with a literal title and one with a variable one, and the literal is the
`?SLCTS` site (`LOAN2` `00B3`, `RETRIEVE` `000C`).  The corrected reading is above; the
mistake is recorded here because it is exactly the error a one-block-per-program census makes,
and the block table in `spec/lab-evidence/e2e41-p0/OPEN-BLOCKS.txt` lists both blocks.

Note `COPYLPT`: its `line` is a **structure member** (`(line character(14), buff
character(254)) varying`) and DR still takes `?SLVTS` with a `LXI H` over the member.
**[P1c correction, recorded in `e2e42-p1c-doc-diagnostics-reconciliation.md`]:** an earlier
draft of this note said the member case "refuses by name".  It does not, and testing it
shows why the sentence was wrong.  `title(line)` is an UNQUALIFIED identifier, so
`open_title` returns `T_var` and `lower_open` consults `st.vars`, where a varying structure
member binds as a FIXED cell -- so this compiler emits `LXI H,<cell>; MVI A,<len>;
CALL ?SLCTS` where DR emits `CALL ?SLVTS`.  The shape COMPILES and its bytes are wrong.  COPYLPT
itself still refuses, but never at that OPEN's title operand (its OPENs carry
PRINT/PAGESIZE/LINESIZE and its ENDFILE handler carries a PUT PAGE).  [C288] does not claim
the member case and no probe of mine pins it; the divergence is documented, not papered over.

## 4. WHAT THE DISPATCH COSTS IN BYTES, AND WHY `w2` CHANGES HANDS

`?SLVTS` has no `MVI A` — the length is a runtime value the helper reads out of the
descriptor — so a varying title prologue is 6 bytes (`LXI H` at `0006`, `CALL ?SLVTS` at `0009`)
and the whole block is **27**; `?SLCTS` adds `MVI A,<len>` for 8 bytes (`LXI H`, `MVI A`, `CALL`
at `000B`) and a block of **29**.  A fixed variable title therefore costs exactly
what a literal one costs, which is why matching only the total block length would not have
caught a wrong route: `E46F2` and a literal-title open are the same size and differ in HL's
target.  Length alone is not enough, and the byte-exact whole-object panel is what pins it.

The second effect is on `w2`, and it comes straight from [C282]'s `INX SP` observation.  In
the **titleless** block, `XRA A ; MOV B,A ; PUSH B ; INX SP` leaves `B = 0`, so DR builds
`w2 = 0x0000` with `MOV H,B / MOV L,B`.  In **any** titled block — literal or variable — `B`
now holds a length, so DR writes `LXI H,0000` instead.  Once a variable title could carry a
**runtime** length the old "reuse `B`" shortcut would have been a live-register bug rather
than a peephole, and the two titled arms in `lower_open` both emit `LXI H,0000` for that
reason.  No `POP` is emitted after `CALL ?OIOOP` in any of the three forms: the callee cleans
the stack, which [C282] measures across all 30 blocks.

## 5. WHAT REMAINS REFUSED, AND WHY THAT IS NOT THE SAME AS UNMEASURED

`open_title` returns a `title_spec` (`T_lit of string | T_var of Ast.name`) rather than a
flattened `string option`, precisely so `lower_open` cannot confuse the two routes and so a
third form cannot be added by accident.  What it refuses, by name:

* **an operand that is not a literal string or a plain declared name** — an expression, a
  qualified reference (`x.y`), an array element.  No object in this corpus puts any of those
  through either helper, so the refusal is an absence of evidence and not a claim that DR
  rejects them.
* **a declared name whose storage class is neither `Vvar` nor `Vfix`** — `BIT(1)`, `DECIMAL`,
  `FLOAT`, `STRUCTURE`, based and external variables.  DR's `COPYLPT` block shows a varying
  *member* taking `?SLVTS`, but this compiler has no byte-exact witness of a member title of
  **its own** -- and, as §3's correction records, a member title is not refused but LOWERED ON
  THE WRONG ROUTE (?SLCTS where DR has ?SLVTS), because the member binds as a fixed cell.
* **`STATIC` operands** — and this is where `E46F5` sits.  DR accepts it (`w1 = 0x0E50`,
  `?SLVTS` at the title site), and this compiler refuses it at the **declaration**: line 3's
  `dcl nm char(14) varying static initial('AB')` hits [C114]'s unsampled
  `STATIC`-on-`VARYING` guard, during layout, before `lower_open` runs.  So `E46F5` measures
  **nothing** about the title route and is on the panel as a `my-gap` row pinned to [C114],
  not as a TITLE gap.  The earlier prose in this repository that called `E46F5` a
  variable-TITLE gap is withdrawn: it conflates two different blockers, and the row now keeps
  them apart so closing [C114] cannot be mistaken for title work and vice versa.

## 6. ACCEPTANCE-LIST MOVEMENT

`FILE.OPEN_STREAM`'s `boundary` no longer says a variable title refuses by name; it points at
this row instead and lists what genuinely remains refused.  The new `FILE.OPEN_TITLE_VAR` row
is `dr_status=ACCEPTS`, `mine_status=SUPPORTED`, `rel_parity=EXACT:4`, `confidence=MEASURED`
— two independent witness sets (four probes of mine plus five historical DR objects) and the
link-record dispatch behind both.  Its `runtime` column is `NONE`: the `.COM` images exist for
chain-record inspection, not as console-oracle rows, and `E46F1`'s `put file(outf)` writes to
a real file whose content this milestone does not characterise.

## 7. BYTE BUDGET

| item | delta | evidence |
|---|---|---|
| `E46F1` / `E46F3` | refused → **byte-exact**, 27-byte block | `golden/e42p1c/E46F1`, `E46F3` |
| `E46F2` | refused → **byte-exact**, 29-byte block | `golden/e42p1c/E46F2` |
| `E46F4` | refused → **byte-exact**, long name + variable title together | `golden/e42p1c/E46F4` |
| gate panel | **+4 EXACT** specimens | `1000 → 1004` |
| `E46F5` | refusal re-labelled, not changed | now a `my-gap` row citing [C114] rather than a mis-described TITLE gap |
| already-accepted programs | **0 bytes changed** | the literal arm is textually the same code; `open_title` gained a constructor, `lower_open` a second arm, and every existing specimen re-matched |

The last row is the one worth stating: `E46D6`, `E17B`, `E16C`, `E18A`, `E16D`, `E17D` and the
rest of the literal-title panels were re-run and are unchanged, which is what makes this an
addition of a route rather than a re-derivation of one.

## 8. RESIDUAL UNKNOWN

* `STATIC` / `EXTERNAL` title operands: `E46F5` proves DR accepts one but this compiler cannot
  reach the code, so no object of mine measures the *lowering*.
* qualified and array-element title operands: unmeasured on both sides.
* `COPYLPT`'s varying **member** title is DR-measured (`?SLVTS`) and LOWERED WRONG here
  (`?SLCTS`), because the member binds as a fixed cell -- see §3.  Unpinned by any probe.
* A `TITLE` on an open that also carries `PAGESIZE`/`LINESIZE` (the `COPYLPT:38` shape) is
  unlowered here because those options are refused, so the block length for that combination
  is DR-side only (33 bytes).

## 9. COMMANDS

```sh
PLI_SRC=probes python3 oracle/batch.py            # probes/E46F*.PLI -> golden/e42p1c/
python3 oracle/linkrun.py link --tag e42p1c --out e42p1b-link --names E46F1 E46F2
python3 tools/reldump.py golden/e42p1c/E46F1/E46F1.REL | grep CHAIN-EXT
python3 spec/lab-evidence/e2e42-p0/census.py      # -> OPEN-CENSUS.txt (title=30, 25 lit / 5 var)
cd ocaml && dune build bin/pli80c.exe && cd ..
python3 tools/e2e_gate.py --update-inventory && python3 tools/e2e_gate.py
python3 tools/coverage_check.py
```
