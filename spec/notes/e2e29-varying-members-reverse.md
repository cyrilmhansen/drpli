# E2E-29 — CHARACTER VARYING structure members, string and pointer comparison, and REVERSE

Date: 2026-10-22/23. Gate: **748 byte-exact / 0 fail, 120/120 negatives refused, divergence panel
8/8 as recorded, exit 0**. Parent commit `50e7c2f` (E2E-28). Compiler delta: `ocaml/lib/codegen.ml`,
`ocaml/lib/bind.ml`, `ocaml/lib/parser.ml`. ARCH-1 (`ocaml/proto/`) untouched — verified with
`git diff 50e7c2f --stat -- ocaml/proto/` (empty).

## 0. What was asked, and what is delivered

| item | status |
|---|---|
| P1 VARYING member store/load/comparison, offsets, AUTO, capacity truncation, PUT | **done**: 10 varying-member probes + E27S5 promoted + REVERSE, all byte-exact; capacity truncation observed live |
| P2 character comparisons in IF and DO WHILE | **done**: 11 probes (C1-C11) byte-exact, 3 also runtime-identical |
| P3 pointer/null comparisons in IF and DO WHILE | **done**: 8 probes (X1,X2,X4-X9) byte-exact, both orientations, both branch outcomes, 2 runtime-identical |
| P4 GET LIST into a VARYING variable/member | **done — and it turned out to need no implementation**: `lower_get` already emitted DR's exact `?SYSIN / ?GNVOP / ?SSVFS` route for a scalar VARYING target, which is REVERSE's `get list(newword)` at 003C-0053 byte for byte. The work was proving that, not writing it. |
| P5 REVERSE integration | **done**: unchanged `artefacts/REVERSE.PLI` reproduces `golden/e2e319d/REVERSE/REVERSE.REL` byte for byte, linked through LINK 1.31 + PLILIB, and its `.COM` produces byte-identical console output to DR's own linked object on two scripted inputs |

## 1. The two overturnings

**(a) Two refusals were bug reports.** `E27S5` was registered with the note "DR COMPILES IT
(golden/e2e323d/ST5/ST5.REL)" and `N23_CHARVAR_MULTI` refused a VARYING item beside a numeric item in
one PUT list as "unsampled". Both shapes now build byte-exactly (against that same ST5 golden, and as
`E29N23`), so both are removed from the negative panel — [C154]: a negative goes when its behaviour
has a golden of its own. Panel count 122 → 120 with no silent substitution: the two keys are
accounted for individually in the gate's registration audit. This is [C188] repeating one milestone
later, in the same dict.

**(b) My probes, not the language.** Six of my first eight probes declared `p` in a shared prefix and
again in the body; DR answered with one PASS-1 error whose symbol-table row reads `DUPLIC`. I read
that as a language boundary before I read it as a defect in my generator — [C186](a) again. A second
instance closed the milestone: renaming probes into collision-free `E29*` keys wrote them with LF line
endings, and DR answered *every one* with `UNEXPECTED EOF` [C118]; and those new names collided with
`PD1/PD2/PD3`, which are tracked E2E-13 pointer probes — my script overwrote three real sources, which
is why the gate reported `DIFF PD1/PD2/PD3` (mine building the new program against the old golden).
`git checkout` restored them and they remain byte-exact against `golden/e2e311d`/`e2e312d`. Rule now
[C193]: check a key against `spec/INVENTORY.txt` **and** `git status` before writing the source file,
and verify CRLF before handing a file to DR.

## 2. VARYING member ABI (measured, all byte-exact)

* **Cell**: 1 length byte + declared capacity. REVERSE's `.word`@0 has `.next`@**001F** (30+1), record
  **0021** (33). ST5's cap-6 member: `.next`@**0007**, record **9**. A VARYING member contributes
  nothing to AUTO STORAGE, like every other based member [C185].
* **Literal store**: `LHLD <q>` / [C189 `member_step`] / `LXI D,*S` / `MVI A,cap` / `MVI B,len` /
  `CALL ?SMCVM`. `len == cap` folds to `MOV B,A` (V3: `'ABCDEF'` into `character(6)`); `len == 0`
  folds to a bare `MVI M,00` with no call (V8). Both folds are the existing scalar `store_char` tails,
  reached through one shared destination thunk rather than re-implemented.
* **VARYING → member**: `LHLD <q>` / step / `LXI D,<src>` / `MVI A,cap` / `CALL ?SMVVM` (V2, REVERSE).
* **Member → member**: source / `PUSH H` / destination / `POP D` / `MVI A,cap` / `?SMVVM` (V7).
* **PUT read**: `LHLD <q>` / step / `CALL ?SLVTS` / `?PNCOP` (ST5, V2, V6, V7, V8, REVERSE).
* `A` is the **destination capacity** in every store, never the value's length; the source carries its
  own length byte. `w` and `p->w` lower to identical bytes, so one encoder (`vbvar_addr`) serves both
  spellings and every route — [C179]'s requirement restated for instruction selection, as [C189] did
  for the offset step.
* Capacity truncation is done by DR's runtime (`?SMCVM`/`?SMVVM`), not by the compiler. The
  witness is E30T1 (a `character(6)` VARYING member assigned the 8-char literal `'ABCDEFGH'`),
  where DR emits `LHLD P / LXI D,*S / MVI A,06 / MVI B,08 / CALL ?SMCVM` [golden/e30p1 000F] —
  A is the DESTINATION capacity (06), B is the SOURCE length (08); my E30T1 is byte-exact.
  **[E2E-30/P0 correction]** An earlier version of this note claimed REVERSE proved truncation
  live, storing `'Actually, '` into a `character(6)` member and printing `Actual`. That was wrong
  on three counts: REVERSE has no `character(6)` member (its `word` is `character(30)`);
  `'Actually, '` is a PUT-list literal (`put skip list('Actually, ')`, line 41) that never touches
  a member — its `MVI A,0A` at 00A2 feeds `?SLCTS`, a print, not `?SMCVM`; and the transcript
  prints `Actually, ` in full. No executed transcript in E2E-29 shows truncation. The A=cap/B=len
  distinction is real and compile-side (E30T1); the runtime truncation it implies is not yet
  observed and is not claimed here.

## 3. Comparison ABI (measured, all byte-exact)

HL carries the **right** operand, DE the **left**; the helper name says what the left is.

| shape | sequence |
|---|---|
| varying = literal | `LXI H,*S / LXI D,<var> / MVI A,len / ?SCVCM` |
| literal = varying | `LXI H,<var> / LXI D,*S / MVI B,len / ?SCCVM` |
| member = literal | `LHLD <q> / [step] / XCHG / LXI H,*S / MVI A,len / ?SCVCM` |
| literal = member | `LHLD <q> / [step] / LXI D,*S / MVI B,len / ?SCCVM` (no XCHG — HL is already right) |
| varying = varying | `LXI H,right / LXI D,left / ?SCVVM` |
| member = varying | `LHLD <q> / XCHG / LXI H,<cell> / ?SCVVM` (E29C10) |

The reversed row is a **different helper and a different length register** — reading only
`varying = literal` would have predicted the wrong routine *and* the wrong register for the mirror
image, which is [C167] exactly (both orientations were sampled because they differed, not to confirm
they matched). `=` skips the then-body with `C2`, `^=` with `CA`.

**Pointer/null**: `p = null` → `LHLD / MOV A,H / ORA L / C2`; `p ^= null` → same with `CA`; both
operand orientations byte-identical (X4 = X1). The cell's own bits are the test — no null value is
loaded. Bare `null` and `null()` are the same value to DR (X1 vs X5; REVERSE lines 14/24 use the bare
form), so `bind.resolve_name` maps the builtin with zero arguments to `Ebuilt("NULL",[])` and the two
spellings never travel separately — which also removes the old pointer-assignment refusal for bare
`null`. Pointer-to-pointer is a different routine: `LHLD / PUSH H / LHLD / POP D / ?NC22N`, `C2` for
`=` (X7), `CA` for `^=` (X9). X6/X8 supply the allocated-pointer side.

## 4. Procedure locals and the nested-body tail rule

REVERSE's `read_it` declares `newword character(30) varying` and `write_it` declares `p pointer`; DR
gives them ordinary absolute DATA cells (`NEWWORD A(0018)`, `P A(0039)`), so the nested layout admits
`Vvar`/`Vfix`/`Vptr` with main's routes (the old refusal cited "REVERSE's layout unproven" — now proven
by both REVERSE and PD1–PD3). A nested body whose last statement is a no-exit loop gets **no trailing
RET** (PD1: `003B JMP 0034`, then main's stop at `003E` with no `C9`); a statement after such a loop is
still emitted and the RET returns (PD2 at `0044`); an exiting loop keeps its RET (PD3). REVERSE's
`read_it` is PD1's shape, its `write_it` PD3's. Bare `put skip;` (PS1 = REVERSE line 49 at `00FE`) is
the ordinary prologue + `?SKPOP` + `?QIOOP` with an empty item list — `lower_put_items_gen` with
`[]`, not a second encoder.

## 5. Runtime witnesses (DR's object vs mine, same harness, same scripted stdin)

| program | transcript (identical on both sides) |
|---|---|
| E29V2 | `v= HELLO` |
| E29V7 | `a= ONE  b= ONE` (member→member across two allocated records) |
| E29VB | `AB  tail` (VARYING member + literal item, reversed order) |
| E29C1 / E29C11 | `c1=         1` / `c11=         0` (equal-length true / different-length false) |
| E29C9 | `c9=         9` (member = literal, reversed orientation, true branch) |
| E29X8 | `x8-notreached=         0 x8=         9` (allocated pointer ≠ null; then null = null) |
| E29X9 | `x9=         0` (`p ^= r` false when `r = p`) |
| E29PS1 | `\nafter=\n` (bare skip) |

[golden/e29rt_dr_r, golden/e29rt_my_r; linked objects in golden/e29rt_dr, golden/e29rt_my]. Each
side's object was byte-compared before linking (`cmp` reported identical, recorded in the session).

**REVERSE**: `golden/e29dr_l/REVERSE.COM` (DR's object) and `golden/e29my_l/REVERSE.COM` (mine)
produced byte-identical console output on both scenarios —
`"\nWhat's up? .\n\n\n"` (sentinel first) and the three-sentence terminating-sentinel script
(`"\nWhat's up? hello world .\n\n\nActually,  world hello .\n\nWhat's up? a b c .\n\n\nActually,  c b
a .\n\nWhat's up? .\n\n\n"`) [golden/e29dr_run{A,B}, golden/e29my_run{A,B}]. The link was confirmed
genuine: 0 unresolved externals, 2866 bytes of PLILIB runtime absorbed, entry at 0100h.

**[E2E-30/P0 correction]** The paragraph below described REVERSE's output as an unexplained
"oddity" and claimed its comment promises `olleh dlrow`. Both are false. REVERSE prepends each new
word to a linked list (`newnode->next = sentence; sentence = newnode;`) and `write_it` walks that
list printing each WORD member whole — so it reverses **word order**, leaving every word's
characters intact. Input `hello world` correctly prints `world hello`, exactly as the algorithm
requires; the source comment says only "reverses a sentence" (line 2) and contains no `olleh dlrow`
anywhere in `artefacts/REVERSE.PLI` or the golden PRN. The behaviour is neither odd nor pending a
reading — it is the intended result, and my earlier framing mistook a correct linked-list reversal
for a character-level one.

**The runtime comparison is circular and has to be read as such [C137].** Each pair of .REL files is
byte-identical and LINK 1.31 is deterministic, so DR's `.COM` and mine are the same bytes — `cmp
golden/e29dr_l/REVERSE.COM golden/e29my_l/REVERSE.COM` reports identical at 7808 B, and the same holds
for the nine E29 pairs. Running "both" is running one file twice: identical output is guaranteed by the
byte-exactness rather than adding independent evidence to it. What the runs genuinely establish is
(i) that the byte-exact artifact I emit executes under CP/M, terminates cleanly, and is not a
plausible-looking-but-dead image, and (ii) what DR's own linked runtime does — the correct
word-order reversal (`world hello`), and `c1=1`/`c11=0` and `x8`/`x9` covering both outcomes of a
compare and of a null test. That is
evidence about the oracle and about runnability. The evidence that my lowering is right remains
byte-exactness against DR goldens; the runtime shows those bytes describe a working program.

One observed oddity, recorded rather than explained: the transcript of *both* objects reverses the last
input word (`world hello`, `c b a`) while REVERSE's own comment says `olleh dlrow` — this is identical
on both sides and needs a separate reading before I cite it [C150].

**[E2E-30/P0] The paragraph immediately above is superseded and kept only for provenance [C166].** It
is wrong: there is no such comment (`REVERSE.PLI` says only "reverses a sentence") and reversing the
order of whole words is the linked-list algorithm's correct, expected output — not an oddity and not
pending a reading. See the correction earlier in this section; do not cite the struck text.

## 6. One divergence

`E29X3` (`do while (p ^= null)` after `p = null;`): **61** code bytes vs DR's **58**, data identical
(9/9), 157 of 256 file bytes differ, first at offset 65 — because DR reuses `HL=0` straight through the
preceding `SHLD P` and lowers the second `p = null` as `SHLD` alone, while I reload `LXI H,0000`. Same
family as PB4/PB20/E28N7/O1/O2/O4 [C141]. Not fitted: no sample establishes what invalidates the reuse
across `SHLD`/`LHLD`/`CALL`, and 33 accepted witnesses share that encoder. Pinned in
`spec/DIVERGENT.txt` so a future change cannot silently shift it.

## 7. Files

* `artefacts/E29*.PLI` — 34 probes (33 byte-exact, E29X3 divergent); originals kept under their short
  names in `artefacts/attic/e29-shortnames/`, with goldens in `golden/e2e341d`, `e2e342d`, `e2e343d`,
  `e2e350d`–`e2e354d`.
* `golden/e2e360`, `e2e361`, `e2e362` — the clean re-runs (CRLF, no duplicate declarations) used for
  registration; `golden/e2e364`/`e2e365`/`e2e366`/`e2e367`, `e29rt_*`, `e29*run*` — runtime witnesses.
* `tools/e2e_gate.py` — E2E-29 registration block (35 specimens, 2 negatives retired).
* `spec/INVENTORY.txt` (748 rows), `spec/DIVERGENT.txt` (8 rows), `spec/CLAIMS.md` C190–C194.
* `oracle/linkrun.py` — `--stdin` now accepts a literal CRLF string (the harness's `\r\n` unescaping
  made an 8-byte CR-only script out of a 4-line input).
