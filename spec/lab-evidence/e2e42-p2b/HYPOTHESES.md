# E2E-42 / P2b — Multi-Item PUT FILE LIST: hypotheses registered BEFORE measurement

Episode: **E2E-42/P2b** (multi-item named-file PUT: multi-literal, multi-scalar, internal
members and CREATE integration).
Baseline this phase starts from: `c816af5a1e9330c740e969697678243ac099eb9b` (`main`).
Oracle tag: `e42p2b`, switches `$L$D$S`.

## 0. Ordering discipline, and why this section is at the top

P2a wrote `HYPOTHESES.md` before it invoked DR — and then a `git stash -u` + `git stash pop`
destroyed the files' timestamps, so the ordering could only be re-established from reasoning and
not shown [spec/lab-evidence/e2e42-p2a/PROCESS.md §4].  That phase accepted the criticism and
promised the next one would make the order MACHINE-VISIBLE.  It does:

1. this file and the 32 probes it predicts are committed in ONE commit;
2. the commit SHA is recorded in RESULTS.md;
3. the oracle is invoked only after that commit exists.

A `git log` on this directory shows the hypotheses commit strictly before the measurement
commit.  That is the evidence; the filesystem mtime of anything here is not evidence of anything.

## 1. What is already fixed, and what is therefore NOT being predicted

**FP1 — DR has already answered the structural question, twice, and both objects are in this
repository.** `spec/lab-evidence/e2e42-p2b/DR-EVIDENCE.md` decodes them with the `chaindump.py`
in this directory (needed because `tools/dis80.py` prints `.` for every relocated operand and so
cannot show which cell an item addresses):

* `golden/first/KEYFILE/KEYFILE.REL` code 008C-00AC — `put file(keys) list(name,k)`, TWO items,
  ONE `?SIOOP`, ONE `?QIOOP`, the two chains back to back with nothing between them, and the
  continuation in `LXI B` pointing at the byte AFTER the close.
* `golden/first/CREATE/CREATE.REL` code 015C-01A7 — SIX items, ONE `?SIOOP`, ONE `?QIOOP`, five
  CHARACTER VARYING chains (`LXI H,*D / ?SLVTS / ?PNCOP`) and one FIXED DECIMAL chain
  (`LXI H,*D / MVI A,06 / ?DLDOP / MVI A,09 / MVI B,00 / ?QDCOP / ?PNVOP`).

So the SHAPE of a multi-item file PUT is not a hypothesis — it is measured DR fact.  What these
two objects cannot be is a **specimen**: both are corpus programs compiled by DR, and
`tools/coverage_check.py` forbids a corpus .REL as the witness of a new lowering.  The claims
below are therefore about MY bytes.

**FP2 — the item chain per class is pinned by `golden/e42p2a/` [C290], and it is the same chain
the console route emits [C293]:**

| item | chain | bytes |
|---|---|---|
| CHARACTER literal | `LXI H,*D(cell) / MVI A,<len> / ?SLCTS / ?PNCOP` | 11 |
| DECIMAL literal | `LXI H,*D(cell) / MVI A,<p> / ?DLDOP / MVI A,<p+3> / MVI B,<s> / ?QDCOP / ?PNVOP` | 18 |
| CHARACTER VARYING variable | `LXI H,*D(cell) / ?SLVTS / ?PNCOP` | 9 |
| CHARACTER FIXED variable | `LXI H,*D(cell) / MVI A,<declared n> / ?SLCTS / ?PNCOP` | 11 |
| FIXED BINARY variable | `LHLD *D(cell) / MVI A,<width> / ?QICOP / ?PNVOP` | 11 |
| FIXED DECIMAL variable | as the DECIMAL literal | 18 |

**FP3 — the prologues and the close [C280]:** file = `LXI H,*C(fcb) / LXI D,0652 / LXI B,<cont> /
?SIOOP` (12); console = `LXI D,0252 / LXI B,<cont> / ?SYSPR` (9); close of statement =
`?QIOOP` (3).  Fixed program overhead measured off E46L1: `LXI B,0200 / ?START` = 6, one literal
OPEN = 29, CLOSE = 6, trailing `?STOPX` = 3.

**FP4 — the pool rule [C155]:** one cell per DISTINCT content, allocated at first use in source
order, a repeat costs no bytes AND no block, the EMPTY literal costs no bytes but registers a
zero-length block PER OCCURRENCE.  Measured across statements (PL7/PL12/PL13) and inside one
PUT LIST (PL12) on the CONSOLE route; never on the file route.

**FP5 — where my refusal actually fires today.** `match_put_list_lit`'s `FILE` arm
(ocaml/lib/codegen.ml:2384) pattern-matches `items = [ Ast.Pi_data x ]`, exactly one item, so a
two-item list never reaches `authorize_file_item` at all: it falls to the refusal at line 2440.
The lowering itself (`lower_put_items_gen`, line 9767) already maps over a LIST of items, emits
one prologue and one `?QIOOP`, and has done so for the console route since [E2E-29/P1].  So P2b
is a PARSING and AUTHORIZATION change, not a code-generation change.

## 2. Hypotheses

* **H1 — one attach, one close, whatever N is.** A file PUT of N items emits 12 + Σ(chains) + 3.
  Falsified if any probe shows a second `?SIOOP` inside a statement or a `?QIOOP` before the last
  item.
* **H2 — the second item costs its own chain and NOTHING else.** Sharpest form: E46M1's two-item
  file statement (predicted 37 bytes) versus E46M2's two one-item file statements (predicted 52)
  must differ by exactly 15 = one attach (12) + one close (3).  Any other difference refutes the
  concatenation model — a per-item `LXI D,0652`, a list-length byte, a separator instruction or a
  hoisted width would all show up here.
* **H3 — [C293] holds for N>1: a file item chain is the console item chain of the same operand.**
  This is the claim most at risk.  [C293] is measured at N=1 only.  Every probe below spells the
  same list on both routes in one object so the two are comparable without a second compilation.
  If they differ, [C293] is narrowed to N=1 and the shared generator has to be split.
* **H4 — no folding, no reordering.** A repeated operand appears twice, with the same operand
  (E46M14); the source order of items is the order of chains, checked by spelling every mixed
  list twice in opposite order (E46M5, M9, M10, M11, M13).
* **H5 — the pool behaves inside a list as it does across statements** (E46M4 predicts 11 DATA
  bytes for FOUR literal items; E46M6 predicts two zero-length blocks for two `''` items of ONE
  statement).  File-route pool: never measured.
* **H6 — authorization is per item and a bad item refuses the whole statement, with no bytes
  emitted.** A claim about MY compiler; E46M21-M26 put the unauthorized class in the SECOND
  position, which is where a "check only the first item" bug hides.  E46M26 additionally pins
  that the ITEM question is answered before the OPEN question, the ordering [C290]'s E46K10
  measured for one item.
* **H7 — the internal-member FILE route is licensed by DR's own objects for exactly three
  classes** — CHARACTER VARYING member (`?SLVTS/?PNCOP`: KEYFILE's `name`, four of CREATE's six),
  FIXED BINARY member (`?QICOP/?PNVOP`: E46L7:0047 — and note this compiler already binds a
  `fixed bin(15)` member as an ordinary `Vint`, which is why that one already works today) and
  FIXED DECIMAL member (`?DLDOP/?QDCOP/?PNVOP`: CREATE's `zip`).  A CHARACTER **FIXED** member
  behind an attach appears in NO DR object in this repository, so E46M17 asks the question cold:
  if DR accepts it, that is a new fact and it stays unauthorized for MY output until the object
  is byte-exact; if DR refuses it, the fixed-member class is a DR rejection on this route and is
  registered as such, not as a my-gap.
* **H8 — CREATE stays refused after P2b, for reasons that are not the item count.** Its remaining
  blockers are its `put file(output) skip` (no specimen of mine carries a file attach and a SKIP;
  E46M19 is the probe that measures the shape so the gap is no longer unmeasured) and nothing
  else — its variable `title(filename)` has been byte-exact since [C288].

## 3. Per-probe predictions

All sizes are FP2/FP3 arithmetic.  "verdict" is the prediction of DR's answer, not of mine.
Every `?SIOOP`/`?QIOOP` prediction is per WHOLE OBJECT.

### Sub-phase A — multi-literal

| probe | predicted DR verdict | predicted `?SIOOP` | predicted `?QIOOP` | predicted CODE | predicted DATA | the specific prediction |
|---|---|---|---|---|---|---|
| E46M1 `list('A','B')` file + console | accept | 1 | 2 | 115 | 11 | file stmt = 37 bytes = 12 + 11 + 11 + 3; console stmt = 34 = 9 + 22 + 3; the two `?SLCTS` calls carry `MVI A,01` each, so the widths are per item |
| E46M2 control: two one-item file PUTs | accept | 2 | 2 | 96 | 11 | E46M1 minus E46M2 = 19 bytes of file code, 15 of which is the second attach+close the multi-item form does NOT emit |
| E46M3 `list('A','BB','CCC')` both routes | accept | 1 | 2 | 137 | 15 | three chains, `MVI A` operands 01, 02, 03 in order — NOT 03,03,03 (one width for the list) and NOT 03 (a count) |
| E46M4 `list('A','A','B','A')` | accept | 1 | 1 | 103 | 11 | DATA = 9 title + 1 ('A') + 1 ('B') = 11: THREE items address the SAME cell; four chains all present |
| E46M5 `list('X=',42)` and `list(42,'X=')` | accept | 2 | 2 | 132 | 18 | order preserved: 11+18 then 18+11; tails `?PNCOP` then `?PNVOP`, and `?PNVOP` then `?PNCOP`; `?QIOOP` after BOTH |
| E46M6 `list('','A','')` | accept | 1 | 1 | 92 | 10 | `MVI A,00` for each empty item; DATA = 10 (the two `''` cost NO bytes) and TWO zero-length pool blocks registered, one per occurrence [C155] |

### Sub-phase B — multi scalar variable

| probe | predicted DR verdict | `?SIOOP` | `?QIOOP` | CODE | DATA | the specific prediction |
|---|---|---|---|---|---|---|
| E46M7 two varying, both routes | accept | 1 | 2 | 107 | 51 | file stmt = 12 + 9 + 9 + 3 = 33 — a varying item emits NO width byte, so this is concatenation with nothing in between |
| E46M8 two fixed char, both routes | accept | 1 | 2 | 115 | 33 | `MVI A,0E` then `MVI A,0A`: per-item declared lengths, in order |
| E46M9 varying+fixed, both orders, both routes | accept | 2 | 4 | 178 | 44 | `?SLVTS ?PNCOP ?SLCTS ?PNCOP` and its mirror; both tails are `?PNCOP`, so an order bug cannot hide in the tail |
| E46M10 varying+binary, both orders, both routes | accept | 2 | 4 | 178 | 32 | `LHLD`/`?QICOP`/`?PNVOP` in position 1 and position 2 |
| E46M11 varying+decimal, both orders, FILE only | accept | 2 | 2 | 128 | 34 | CREATE's mixed char/decimal chain with ordinary variables: 9+18 and 18+9 |
| E46M12 same list on the CONSOLE route | **accept predicted, low confidence** | 0 | 2 | 87 | 25 | the [E2E-29/P1] classifier refuses a DECIMAL item beside a CHARACTER one on the console today; DR's own answer here is what will decide whether that boundary is mine or DR's, and NOTHING in P2b changes the console route |
| E46M13 binary+decimal, both orders, both routes | accept | 2 | 4 | 214 | 15 | widths 09 and 06/09/00, per item |
| E46M14 `list(v,v)` and `list(v,k,v)` | accept | 2 | 2 | 121 | 32 | NO folding: three chains in the second statement, and the two `v` chains carry the identical `LXI H,*D(<v>)` operand |
| E46M15 five mixed items | accept | 1 | 1 | 117 | 50 | 9+11+11+18+9 = 58 between one attach and one close |

### Sub-phase C — internal members and CREATE

| probe | predicted DR verdict | `?SIOOP` | `?QIOOP` | CODE | DATA | the specific prediction |
|---|---|---|---|---|---|---|
| E46M16 varying member + binary member, both orders, both routes | accept | 2 | 3 | 146 | 26 | KEYFILE's shape at member+member size; the member cell is the frame offset (E46L7:002F/0047) |
| E46M17 FIXED CHARACTER member alone, then beside a varying member | **unknown — H7's cold question** | 2 | 2 | 105 | 32 | if accepted: `MVI A,08` (the member's declared length) then `MVI A,0E` — the fixed-member FILE chain has no DR witness anywhere |
| E46M18 member+literal+variable, and the QUALIFIED spelling | accept | 2 | 2 | 123 | 50 | `list(rec.line,rec.nxt)` must emit the SAME `LXI H,*D(9)` the bare `line` emits ([C253]: one cell, two spellings) |
| E46M19 CREATE's six-item list, ORDINARY variables | accept | 1 | 1 | 122 | 121 | CREATE's chain with the same capacities (30/30/20/10/dec6/12) and a LITERAL title — the object that licenses CREATE's chain without CREATE's other blockers |
| E46M20 CREATE's six-item list as a level-numbered RECORD | accept | 1 | 1 | 122 | 121 | DR accepts; **MY refusal is expected to be the BIND one** ("a FIXED DECIMAL member registers no alias" [E2E-39/P2]), which is a separate mechanism and is registered as such rather than folded into the PUT story |

### Boundary probes (predicted: DR accepts, mine refuses)

Each puts the unauthorized class in the SECOND position of an otherwise fully authorized list.

| probe | second item | DR verdict | my verdict | why the refusal is mine |
|---|---|---|---|---|
| E46M21 | `q float` | accept (E46L11 already proved FLOAT behind an attach in position 1) | refuse | FLOAT is not an authorized FILE class; a per-item check must not be position-dependent |
| E46M22 | `arr(2)` | accept (E46L10) | refuse | array element, refused at the matcher on syntax |
| E46M23 | `k + 1` | accept (E46L9) | refuse | expression, refused at the matcher |
| E46M24 | `rec` (the whole row) | **unknown — no object in this repository lists a structure by its head name on either route** | refuse, at BIND: `undeclared rec (no declaration in scope)` — the level-1 head is not registered as a variable at all | the refusal names the NAME, not the PUT route; that is a third mechanism and must be registered as one |
| E46M25 | `p pointer` | **unknown** — [C290] records no object on EITHER route prints a pointer | refuse | pointer; the refusal must name the class, not the position |
| E46M26 | `q float` on a file never OPENed | accept | refuse | must refuse on the ITEM first (H6), not on the open — E46K10 measured that order at N=1 |

### Runtime rows (five, within the eight-probe limit)

These predict BYTES OF A FILE, which is the part [C295] has measured only for single-item
statements.  If the multi-item separator differs from the between-statements separator, the two
predictions disagree and that is the finding.

| probe | predicted file content | predicted bytes |
|---|---|---|
| E46M27 `list(v,w); list(v); list(w); list(v,w)` with `v='HELLO'`, `w='XY'` | `'HELLO' 'XY' 'HELLO' 'XY' 'HELLO' 'XY'` — blank between EVERY pair of items, none before the first, because [C295] measured exactly that for separate statements | 33 of content + 5 separators = 38, in a 128-byte file |
| E46M28 `list('AA','B','CCC')` | `'AA' 'B' 'CCC'` with the apostrophes the file edit adds (E46L12/E46L18: the delimiters belong to the stream) | 4+1+3+1+5 = 14 |
| E46M29 `list(v,k,z)` then `list('=',v)` | `'HI'        42      123` then ` '='HI'` — numerics 9 wide right-justified unquoted, character items quoted, one blank between EVERY pair of items including across the statement boundary | 4+1+9+1+9 +1+3+1+4 = 33 |
| E46M30 `list(c,d)` both under-filled fixed chars | `'ABC     ''W   '` — each padded to its OWN declared length (8 and 4), one blank between the items | 10+1+6 = 17 |
| E46M31 six-item CREATE-shaped list with five varying members + one ordinary decimal | `'JOHN' '1 HIGH ST' 'BOSTON' 'MA'    12345 '555-1212'` | 6+1+11+1+8+1+4+1+9+1+10 = 53 |

The alternative, which would refute the separator model for item lists is that a multi-item statement writes its items with
NO separator while separate statements get one blank; that would make the blank a property of the
STATEMENT rather than of the item list, and would contradict nothing measured so far.  E46M27 is
written to tell the two apart inside one file.

## 4. What I will NOT do regardless of what comes back

* No console-route change.  The console multi-item classifier is [E2E-29/P1]'s and its boundaries
  are its own; if E46M11C shows DR accepting what that classifier refuses, the finding is
  recorded and the refusal stays until a console phase measures it.
* No member-registry widening.  A level-numbered FIXED DECIMAL member resolves to no alias in
  this compiler ([E2E-39/P2]); E46M20 measures DR's answer but does not license registering one.
* No SKIP, no ON unit, no EDIT on the file route.
* No promotion of CREATE.  Its six-item chain becoming reachable does not make CREATE itself a
  specimen while its `put file(output) skip` still has no byte-exact witness of mine.
* One `rune-ci submit`, on the final SHA only.
