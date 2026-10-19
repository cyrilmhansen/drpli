# E2E-8, slice 5 — PUT EDIT + DO/BY, IFACT accepted (2026-10-19)

Baseline for this slice: `4bc9af8` (E2E-7A slice 4, LOAN1 accepted).
Preceded by the bounded assessment `1003657` (`spec/notes/e2e8-ifact-assessment.md`).

**Result: IFACT is byte-exact against the DR corpus golden — the 5th of 41
historical programs accepted.** `ocaml/_build/default/bin/pli80c.exe
artefacts/IFACT.PLI` produces 384 bytes that are `cmp`-identical to
`golden/first8080u/IFACT/IFACT.REL`; its linked `.COM` (9600 B) is identical to
the one built from DR's own `.REL` against the same PLILIB; and under the
bounded complete-record prefix protocol its first 12 console records are
byte-equal to DR's with 6 of them independently re-derived from
`math.factorial` (see §6).

Gate state after the slice: **194/194 `.REL` byte-exact**, negative panel
**42/42**, bind 47/47, parse 498 ok / 6 parity-rejects / 0 FAIL of 504,
ir 0 FAIL, rel round-trip 480/480, clean-build warnings **63 → 63 with an
identical per-kind histogram**.

---

## 1. PUT EDIT — what DR emits

### 1.1 The format list compiles to a byte table in the pool

A PUT EDIT statement is `put edit(<data list>)(<format list>)`. The format list
becomes a literal byte table placed in the `*S` pool:

```
table := 80 00 | <record>... | 81
```

Record encodings (all observed, `reldump` of R1001-R1010 / R1018-R1022 / R1037
and IFACT):

| format spec | bytes | evidence |
|---|---|---|
| `f(w)` | `00 w FF` | R1001, R1002, R1018 |
| `f(w,d)` | `00 w d` | R1020 |
| `a` | `03 FF` | R1003, R1010 |
| `a(w)` | `03 w` | R1008 |
| `skip` | `0C FF` | R1004, R1005, R1010 |
| `page` | `0F FF` | R1007 |

`FF` is the "no word argument" filler; when the spec carries an argument that
argument's byte takes the slot. Record LENGTH varies by opcode: controls (`skip`,
`page`) and `a`/`a(w)` are 2-byte records, `f(w)`/`f(w,d)` are 3-byte records —
so table length is `2 + sum(records) + 1`, not `3 x specs`. R1020's
`(a(3), f(2,1), skip)` table is `80 00 | 03 03 | 00 02 01 | 0C FF | 81` = 12
bytes. IFACT's own list `(skip, a, f(2), a, f(7))`
therefore compiles to `80 00 | 0C FF | 03 FF | 00 02 FF | 03 FF | 00 07 FF | 81`
= 15 bytes at `*S(0000)`, which is exactly what the corpus golden carries.

### 1.2 The statement skeleton

PUT EDIT is PUT LIST with two insertions; everything else is shared:

```
LXI  D,0252            ; output buffer address      (identical to PUT LIST)
LXI  B,0000            ; continuation pointer        (identical)
CALL ?SYSPR
[MVI A,n; CALL ?SKPOP] ; leading `skip n' — identical to PUT LIST
LXI  H,*S(table)       ; <<< NEW: point at the compiled format list
CALL ?EDITF            ; <<< NEW: install it
per data item:
   <the same per-item code as PUT LIST>              (SLCTS / QICOP / QDCOP / SLVTS)
   CALL ?EDTOV          ; <<< replaces ?PNCOP / ?PNVOP after EVERY item
CALL ?QIOOP            ; end of record
SET-LC tail            ; continuation
```

?EDTOV is unconditional: character items, which use `?PNCOP` in a PUT LIST, and
numeric items, which use `?PNVOP`, both get `?EDTOV` [R1003 vs R1001]. So the
`keep_going` choice that PUT LIST makes per item collapses into one routine in
the EDIT path, and my `tail` helper now selects `?EDTOV` whenever a format table
is present.

### 1.3 Pool law: every format table is allocated before every other pool item

This is the one thing about PUT EDIT that is *not* local to the statement.
R1003 is decisive:

```
6  c = 'AB';                      uses *S(0005)   <- literal, LATER address
7  put edit(c)(a);            LXI H,*S(0000)      <- table, EARLIER address
```

The statement on line 7 owns the lower pool address even though line 6 needs its
literal first. R1021 (two EDIT statements) gives `table1, table2, 'AB', 'CD'`;
R1022 (a table inside a `DO` body, a literal in a statement before it) gives
`table_in_do, table_after_do, 'AB', 'XY', 'ZW'`. So:

**Law: DR lays the pool out in two passes — all format tables first (in
source / depth-first order), then all other pool items (in source order).**

Implementation: `prealloc_fmt_tables` walks the statement tree depth-first
before any statement lowers (`edit_stmts`) and `pool_alloc`s each accepted
statement's table; lowering then pops addresses from `st.fmtq` in the same
order instead of allocating. The pool-size prescan counts the table bytes
before the item literals so the AUTO base is right.

### 1.4 Perimeter (each one a tested refusal)

* a FIXED DECIMAL data item inside an EDIT list — no DR sample passes a DEC
  item through an edit list (`?QDCOP`+`?EDTOV` is unevidenced); refused.
* `put skip edit(...)` — a leading control item before the DATA list is
  unsampled (its table position is unknown); refused.
* counted SKIP/PAGE (`skip 3`, `page 2`) — only the bare form's `FF` filler is
  observed; refused.
* replication / picture / control items mixed into the DATA half — the walker
  refuses rather than guessing which half they belong to.

---

## 2. DO/BY — the lowering laws

### 2.1 FROM may be a variable; the init follows an instruction-cost ladder

`do n = i to 1 by -1` (IFACT's inner loop) initializes with
`LHLD I / SHLD N` [IFACT 000C-000F, R1014 byte-exact].

A *constant* FROM is loaded with the cheapest instruction that produces the
value, given what is already in HL (R1012, R1013, R1015, R1022, R1030, R1032):

| HL state before init | instruction DR emits | bytes |
|---|---|---|
| already equals `from` | nothing (just `SHLD`) | 0 |
| equals `from - 1` | `INX H` | 1 |
| known `< 256` and `from <= 255` | `MVI L,from` | 2 |
| anything else | `LXI H,from` | 3 |

`MVI L` is only legal when H is known zero, which is precisely the
`last_imm < 256` case; the ladder is strictly increasing in cost, so DR's
choice is byte-minimal every time it was observed.

**The reuse is control-flow sensitive.** IFACT proves it: the outer loop's init
executes `LXI H,0000`, and the very next source line — the first statement of
the loop *body*, `F = 1` — gets a full `LXI H,0001`, not `INX H`. A loop body is
a branch target: at the back edge HL holds whatever the increment left there, so
knowledge from the pre-body statement is dead. My `st.last_imm` tracker is now
cleared at every loop-body head and after every `LHLD`. (Before that reset,
IFACT's body emitted `INX H` where DR emits `LXI H,0001` — 2 bytes wrong.)

### 2.2 Exit test: subtract a constant, then test the sign byte

```
rising  (step > 0):  c = bound + 1 ; LHLD i ; <subtract c> ; MOV A,H ; ORA A ; JP skip
falling (step < 0):  c = bound     ; LHLD i ; <subtract c> ; MOV A,H ; ORA A ; JM skip
```

and the subtraction itself is peeled by size:

| c | DR's form | evidence |
|---|---|---|
| 1, 2, 3 | `DCX H` × c | R1012 (c=1), R1023 (c=2), R1013/R1024/R1028 (c=3) |
| 4, 5, 6, 20 | `LXI B,-c ; DAD B` | R1025 (c=4), R1026 (c=5), R1011 (c=6), R1027 (c=20) |

The crossover sits exactly where the rung ladder stops being cheaper than
`LXI B,DAD B` (4 bytes): `c = 3` uses rungs, `c = 4` uses the constant form.
Note the falling test subtracts the **bound**, not the step: R1013
(`do i = 9 to 3 by -2`) emits 3 rungs, not 2 — the step never enters the test.

### 2.3 Increment

`LHLD i / (INX H or DCX H) × |step| / SHLD i` — direction from the sign, one rung
per unit [R1011 by 2 → 2 INX; R1013 by -2 → 2 DCX; R1012/R1033 by -1 → 1 DCX],
then `JMP` to the test (or to the body head in the no-test forms). A step must
be an integer *literal* (DR's increment has no room for an expression) and only
|step| ≤ 2 is sampled; magnitude 3 (R1034) is a tested refusal.

### 2.4 The two "no TO" shapes are different programs

* **`do i = c by k;` — forever WITH a step.** Body, increment, `JMP` back, and
  **no exit test at all** [IFACT outer loop, R1014, R1030]. This is the shape
  that opens the epilogue-suppression window exactly like the REPEAT forms.
* **`do i = c;` — indexed, no TO, no WHILE, no REPEAT, no BY: degenerate.** DR
  stores the FROM value, executes the body **once** and falls through: no
  increment, no test, no back-edge `JMP` [R1032, byte-exact]. It is therefore
  *not* a no-exit loop and must not open the suppression window — R1032's PUT
  after the loop lowers normally. This was a surprise: the presence or absence
  of `by 1` (which looks redundant next to an index) changes whether the
  statement is a loop at all.

### 2.5 Perimeter (tested refusals)

* `do ... while (...)`: DR rewrites `while (index < c)` into the bounded form
  (R1016 is byte-identical to R1015) and `do i = 0 while (i < 4)` into a
  forever-with-test form; my build has no lowering for either rewrite and
  refuses [N48, N49]. The rewrite *law* is documented from the assessment, but
  implementing it would add a condition-to-bound rule with one sample pair.
* bound `< 1`: DR switches to a general signed compare
  (`XRA A / CMP M / INX H / SBB M / JM`) [R1029] instead of the constant
  subtraction; not in the banked subset → refused [N50].
* |step| ≥ 3 → refused [N51].
* DO index that is a pointer formal, a DEC variable, or a non-fixed-bin type
  → refused (unchanged).

---

## 3. Defect found and repaired: fixed-bin `a - b` was not in the int subset

`i = 3; s = 20; s = s - i;` — plain 16-bit variable-minus-variable in an
assignment — **refused** in my build ("operator not in int subset") even though
E2E-2 claims fixed-bin arithmetic. It had survived four slices because no
accepted program needed it: LOAN1's subtractions are FIXED DECIMAL (`?DSUOP`),
RFACT/NFACT use multiplication and `+1`. DO/BY probing exposed it (R1033's
body).

DR's law [R1035 `s = s - i`, R1036 `s = i - i`, both byte-exact]:

```
LHLD left ; XCHG ; LHLD right ; CALL ?IS22N ; <store tail>
```

i.e. the *same pair ladder* as addition (`?DAD D`) with the add replaced by
`?IS22N`, which computes `DE - HL` into HL. This is also exactly the primitive
my condition lowering already used for `var OP var` relational tests, so the
runtime was known; only the arithmetic arm was missing. Pointer-deref operands
in this route have no DR sample and stay refused.

---

## 4. Harness defects found while landing this slice

1. **`prefix_check.py --console --facts` was vacuous.** The `--console` branch
   `return`ed before the `--facts` block, so asking for both silently skipped
   the arithmetic oracle. My first IFACT run reported PREFIX-OK while doing no
   factorial verification at all. The facts oracle is now a function
   (`facts_check`) that both arms call, and IFACT was re-run: `FACTS-OK 6
   complete factorial records match math.factorial independently [1,1,2,6,24,
   120]`. RFACT's standalone `--facts` path was re-run too (4 records OK) so the
   refactor did not break the program the oracle was written for.
2. **My AST change broke the binder.** Adding `Ast.Pi_fmtlist` made three
   binder-side matches non-exhaustive, and `bind_gate` went 47/47 → **13 FAIL**
   because the FORMAT-descriptor size fold (`bind.ml`) now saw one wrapper item
   instead of N format items. Fixed by `flatten_items`, applied at all four
   binder consumers of a statement's item list, restoring exactly the pre-E2E-8
   flat view for `$S` purposes: **47 exact / 0 known-gap / 0 FAIL**, and the
   per-site `$S` output is unchanged.
3. **Two probe sources were malformed** (unterminated `DO`, `return;` with no
   value) and one used an unsampled comparison (`s < 0`); R1030/R1032/R1033 were
   rewritten and re-ORACLED rather than being quietly dropped.
4. **`lower_put_items`' optional-argument refactor.** OCaml desugars
   `?(x : int array option)` into a parameter of type `int array`, so the
   first attempt would not typecheck; the function is now split into
   `lower_put_items_gen` (takes `int option`) plus the byte-frozen
   `lower_put_items` wrapper, which keeps every PUT LIST call site untouched.
5. **Warning hygiene.** My new code initially added 6 warnings (2 unused vars,
   2 partial-matches from `bind.ml`, plus 2 more). After fixing them, a full
   `rm -rf _build && dune build` gives **63 warnings with a per-kind histogram
   identical to a freshly built `4bc9af8` worktree** (created for measurement,
   removed afterwards). The 63 pre-existing warnings remain untouched debt.

---

## 5. Evidence table (all 34 new positives are `cmp`-clean)

| specimen | shape | proves |
|---|---|---|
| R1001-R1002 | `edit(i)(f(3))`, `f(12)` | `f(w)` encoding, one-byte vs two-byte width |
| R1003 | `edit(c)(a)` | `a` encoding + **pool order** (table before an earlier statement's literal) |
| R1004-R1005 | `skip` before / after a spec | control records, position inside the table |
| R1006 | two data items, two `f` specs | multi-item EDIT |
| R1007 | `page` | `0F FF` |
| R1008 | `a(5)` | width-carrying A record |
| R1009 | IFACT's exact PUT EDIT with two binaries | the whole statement in isolation |
| R1010 | literal data + `(skip, a)` | literal + char-only format |
| R1011 | `do i = 1 to 5 by 2` | `LXI B,-(b+1)` rising, 2-rung increment |
| R1012 | `do i = 5 to 1 by -1` | falling test = bound, 1 rung; `MVI L` init |
| R1013 | `do i = 9 to 3 by -2` | test subtracts the bound, not the step |
| R1014 | `do n = i to 1 by -1` | variable FROM (IFACT's inner loop) |
| R1015 | `do i = 0 to 3 by 1` | 0-byte init (HL already right), c=4 → `LXI B` |
| R1018 | `i = 42; edit(i)(f(6,2))` | `f(w,d)` in a single-item list |
| R1019 | `edit(i)(f(1),a,f(3,1),skip)` | mixed format records |
| R1020 | `edit(c, i)(a(3), f(2,1), skip)` | char-varying beside a binary in EDIT |
| R1021-R1022 | two EDIT statements | table-first pool law across statements and into a DO body |
| R1023-R1026 | `to 1/2/3/4` | rung↔`LXI B` crossover at c=3/4 |
| R1027-R1028 | `to 20 by -1`, `to 2 by -1` | falling with `LXI B` and with rungs |
| R1030 | `do i = 3 by 1` (forever) | `MVI L` init in the no-test form |
| R1031 | `i = 3; s = i;` | the init ladder is the *general* constant-store ladder |
| R1032 | `do i = 3;` (no BY) | **degenerate DO**: no increment, no back edge |
| R1033 | `do i = 5 by -1` + `s = s - i` | forever descending + the subtraction repair |
| R1035-R1036 | `s - i`, `i - i` | `?IS22N` arithmetic route (§3) |
| R1037 | `do i = 1 to 4 by 2` + PUT | promoted N19_DOBY, re-ORACLED fresh |
| **IFACT** | corpus program | all of the above together |

New PLILIB entrypoints emitted by this slice: **`?EDITF`, `?EDTOV`** (2).
Two existing opcodes also reached a second syntactic role: `MVI L,imm` (init
ladder) and `?IS22N` (arithmetic, previously condition-only).

---

## 6. Tiered validation actually run (per the workflow agreed at `4bc9af8`)

* **Tier 1 — full `.REL` parity, every iteration**: `python3 tools/e2e_gate.py`,
  194/194, panel 42/42, 0.3 s. Run after every patch step.
* **Tier 2 — targeted link + console** on the new specimens plus a small
  regression sample: 17 names (4 m 43 s) then 20 names (6 m 52 s) —
  **32 new specimens + 5 regression names (LOAN1, DEMO, NFACT, R901, R813),
  37 linked `.COM` byte-identical to DR and 37 raw console transcripts
  byte-equal, 0 divergences.** R1030 is excluded from the console arm by
  design: it never terminates and its PUT is unreachable, so it prints nothing.
* **Tier 3 — full `--link-run`**: not run at this slice; the next full
  checkpoint is the natural place for it (the corpus count changes there).
* **IFACT (non-terminating)**: bounded complete-record prefix protocol —
  `tools/prefix_check.py IFACT artefacts/IFACT.PLI golden/first8080u/IFACT/IFACT.REL
  --console --records 12 --facts 6 --maxvalue 32767` → `.COM` IDENTICAL
  (9600 B), `PREFIX-OK` on the first 12 records, `FACTS-OK` on 6 records
  (factorials 0!..5! re-derived in Python; records above FIXED BIN(15) range
  are skipped, never counted as a pass).

---

## 7. Where this leaves the corpus

Byte-exact: **5/41** — DEMO, RFACT, DFACT, LOAN1, IFACT.

Remaining near-miss blockers, in the order the audit lists them:

| program | first blocker now |
|---|---|
| DECPOLY | DEC formal-parameter passing (by-reference 2-byte pointer cell) [N33] |
| COPY | FILE / stream I/O |
| ANNUITY | FLOAT, FILE, POINTER, ENTRY, multi-module |
| P401/P402/P403-class probes | pointer formal in IF condition, multiple forward CALLs |

Nothing in the E2E-8 scope (PUT EDIT, DO/BY) remains blocked: every shape
IFACT uses is banked with named evidence, and every shape my build refuses is
refused *loudly* and is a tested panel member.
