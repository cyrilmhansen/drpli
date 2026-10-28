# E2E-42 / P2b — RESULTS: DR's answers, my predictions, and what each of them was worth

Everything here is written AFTER the oracle ran.  The predictions it scores are the ones committed
in `f3902363ddddeeca77b9f374055c4c6338014d03` (2026-10-28 13:31:27 +0100) and are unchanged since:

```
$ git diff HEAD -- spec/lab-evidence/e2e42-p2b/HYPOTHESES.md      # empty
$ git log --format='%h %ad %s' --date=iso -3
5de6b08 2026-10-28 13:38:06 +0100 E2E-42/P2b: ... all 32 probes wrapped to <=71 columns
f390236 2026-10-28 13:31:27 +0100 E2E-42/P2b: 32 probes and every prediction, committed BEFORE DR is run
c816af5 2026-10-28 10:38:01 +0100 E2E-42/P2a: ...
```

## 0. How the ordering is proved this time, and why not by timestamps

P2a documented a violation: ordering was asserted from filesystem mtimes, and after a `git stash`
the mtimes were gone and the claim was unrecoverable (`e2e42-p2a/PROCESS.md`).  P2b's ordering is
proved by three things a reader can re-check without trusting my account:

1. **The 32 predictions in §1–§4 have not been touched since the preregistration commit.**  The
   command is `git diff f390236 HEAD -- spec/lab-evidence/e2e42-p2b/HYPOTHESES.md`, and it reports
   **46 insertions and 0 deletions** — the two additions are §5 (E46M33/M34) and §6 (E46M35/M36),
   each committed BEFORE its own oracle call (`18785e5` 15:12:06, `ae15bee` 15:24:02; the e42p2b5 and
   e42p2b6 golden directories postdate them).  Nothing scored in §1 below was written after DR
   answered, and no prediction that DR answered has been edited.
2. **The probes DR compiled are the probes git holds.**  DR's own printout lists the source it read
   (the `N a|c XXXX <line>` block after `PL/I-80 V1.4 COMPILATION OF:`), and all 32 blocks match
   `probes/E46M*.PLI` line for line — 32 probes, 0 mismatches — allowing only DR's own truncation
   at column 72.  The check is a 20-line script and its result is quoted in section 6.
3. **Probe edits are committed and explained, including one made after an oracle call.**  `5de6b08`
   wrapped the 32 probes after DR truncated a 233-column comment line (§6, "DR's own source format"),
   and `git diff 5de6b08 HEAD -- probes/` shows 4 files and 0 deletions, i.e. no probe DR already
   answered was rewritten.  The exception is inside §11 and is stated there rather than hidden: the
   FIRST submission of E46M33/E46M34 (`git show 18785e5:probes/E46M33.PLI` — LF endings, `end X.`) was
   replaced before its second oracle call, because the artefact it produced (`golden/e42p2b4/`) proves
   the submission was malformed rather than proving anything about the statement.  A rewritten probe
   gets its own tag and its own committed prediction; the old artefact stays.

## 1. DR's verdicts against the predictions

`?SIOOP` / `?QIOOP` are counted out of DR's own .REL by `chaindump.py`'s `instrs()`, not read off
my prose.  `mine` is `cmp` of my compiler's output against DR's golden, whole file.  `predicted`
compares HYPOTHESES.md's numbers with what DR produced: CODE size, DATA size, and the two call
counts.  Probes with no size prediction are the six whose tables predict FILE CONTENTS (M27-M32) or
item classes (M21-M26).

| probe | DR | CODE | DATA | ?SIOOP | ?QIOOP | mine | predicted vs actual |
|---|---|---|---|---|---|---|---|
| E46M1 | accept | 115 | 11 | 1 | 2 | identical | code✓ data✓ SIO✓ QIO✓ |
| E46M2 | accept | 96 | 11 | 2 | 2 | identical | code✓ data✓ SIO✓ QIO✓ |
| E46M3 | accept | 137 | 15 | 1 | 2 | identical | code✓ data✓ SIO✓ QIO✓ |
| E46M4 | accept | 103 | 11 | 1 | 1 | identical | code✓ data✓ SIO✓ QIO✓ |
| E46M5 | accept | 132 | 13 | 2 | 2 | identical | code✓ **data✗ (pred 18)** SIO✓ QIO✓ |
| E46M6 | accept | 92 | 10 | 1 | 1 | identical | code✓ data✓ SIO✓ QIO✓ |
| E46M7 | accept | 107 | 51 | 1 | 2 | identical | code✓ data✓ SIO✓ QIO✓ |
| E46M8 | accept | 115 | 33 | 1 | 2 | identical | code✓ data✓ SIO✓ QIO✓ |
| E46M9 | accept | 178 | 44 | 2 | 4 | identical | code✓ data✓ SIO✓ QIO✓ |
| E46M10 | accept | 178 | 33 | 2 | 4 | identical | code✓ **data✗ (pred 32)** SIO✓ QIO✓ |
| E46M11 | accept | 128 | 35 | 2 | 2 | identical | code✓ **data✗ (pred 34)** SIO✓ QIO✓ |
| E46M12 | accept | 87 | 25 | 0 | 2 | MINE REFUSES | code✓ data✓ SIO✓ QIO✓ |
| E46M13 | accept | 214 | 16 | 2 | 4 | identical | code✓ **data✗ (pred 15)** SIO✓ QIO✓ |
| E46M14 | accept | 121 | 33 | 2 | 2 | identical | code✓ **data✗ (pred 32)** SIO✓ QIO✓ |
| E46M15 | accept | 117 | 51 | 1 | 1 | identical | code✓ **data✗ (pred 50)** SIO✓ QIO✓ |
| E46M16 | accept | 146 | 27 | 2 | 3 | MINE REFUSES | code✓ **data✗ (pred 26)** SIO✓ QIO✓ |
| E46M17 | accept | 105 | 33 | 2 | 2 | identical | code✓ **data✗ (pred 32)** SIO✓ QIO✓ |
| E46M18 | accept | 123 | 51 | 2 | 2 | identical | code✓ **data✗ (pred 50)** SIO✓ QIO✓ |
| E46M19 | accept | 122 | 121 | 1 | 1 | identical | code✓ data✓ SIO✓ QIO✓ |
| E46M20 | accept | 122 | 121 | 1 | 1 | MINE REFUSES | code✓ data✓ SIO✓ QIO✓ |
| E46M21 | accept | 79 | 35 | 1 | 1 | MINE REFUSES | (no size predicted) |
| E46M22 | accept | 79 | 37 | 1 | 1 | MINE REFUSES | (no size predicted) |
| E46M23 | accept | 80 | 33 | 1 | 1 | MINE REFUSES | (no size predicted) |
| E46M24 | **REFUSE** | — | — | — | — | refuses (different reason) | predicted refuse ✓ |
| E46M25 | **REFUSE** | — | — | — | — | refuses (different reason) | predicted unknown; DR refused |
| E46M26 | accept | 44 | 25 | 1 | 1 | MINE REFUSES | predicted DR REFUSE — **wrong** |
| E46M27 | accept | 207 | 63 | 4 | 5 | identical | contents predicted, see §4 |
| E46M28 | accept | 115 | 20 | 1 | 2 | identical | contents predicted, see §4 |
| E46M29 | accept | 190 | 48 | 2 | 3 | identical | contents predicted, see §4 |
| E46M30 | accept | 130 | 30 | 1 | 2 | identical | contents predicted, see §4 |
| E46M31 | accept | 226 | 158 | 1 | 2 | identical | contents predicted, see §4 |
| E46M32 | accept | 149 | 71 | 1 | 3 | identical | contents predicted, see §4 |

**Tally.** 30 of 32 accepted, 2 refused.  24 accepted probes are now byte-exact specimens of mine
(the 23 above plus E46L7, promoted from P2a's negatives); 6 of the accepted ones are my-gaps; 2 are
DR refusals registered with DR's word.  Of the 20 probes whose CODE size I predicted, **20 were
exact**.  Of the 20 ?SIOOP counts and 20 ?QIOOP counts, **40 of 40 were exact**.  Of the 20 DATA
sizes, **11 were exact and 9 were wrong** (§7 owns the nine).

**The two later calls, kept out of that tally because they are a different question.**  E46M33 and
E46M34 (§11) are two more DR refusals — `SYNTAX ?` in pass 2, no object — and both were predicted as
refusals.  E46M35 and E46M36 are protocol probes, also refused, and their job was to isolate why the
first submission of M33/M34 proved nothing.

**The panel's own arithmetic, taken by loading the gate module at `c816af5` and at HEAD** (not from
my prose): SPECIMENS **1032 → 1056** (+24: E46M1-M11, M13-M15, M17-M19, M27-M32 and the promoted
E46L7; nothing removed), REJECTS **174 → 184** (+12 rows — E41X9, E46M12, M16, M20-M26, M33, M34 —
of which 8 are `my-gap` and 4 are `dr-refuses`; −2 rows, E41X7 which now compiles and E46L7 which is
a specimen).  Category counts move by +7 `my-gap` and +4 `dr-refuses`, and E46K10 moves from
`unmeasured` to `my-gap` inside the unchanged 174-minus-2 — which is the [C256] correction §5 records.

## 2. The hypotheses, each with the evidence that decides it

* **H1 — one `?SIOOP` and one `?QIOOP` per STATEMENT, not per item. CONFIRMED.**  E46M1 (2 items,
  one file statement) has ONE attach at 0023 and ONE close ending at 0045; E46M2 (the same two
  items in TWO statements) has TWO attaches, 0023 and 003D, and TWO closes.  E46M19's six-item
  statement is one attach and one close (015C-01A7 in CREATE is the corpus version of the same
  shape).  E46M27 pushes it to four statements in one file: 4 attaches, 5 closes (the fifth is the
  console `put list('DONE')`) [C296].
* **H2 — the second item costs its own chain and NOTHING else. CONFIRMED, in the sharp form.**
  E46M1's file statement spans 0x23 to 0x48 = **37 bytes** = 12 (attach) + 11 (`LXI H,*D(0009) /
  MVI A,01 / ?SLCTS / ?PNCOP`) + 11 (the same for `*D(000A)`) + 3 (close), exactly as predicted;
  E46M2's two one-item statements are 26 + 26.  E46M1 − E46M2 = 19 bytes of CODE, of which 15 is
  the attach+close the multi-item form does not emit ✓.
* **H3 — there is no separator instruction between items. CONFIRMED** in the object, and then in
  the FILE at run time (§4): nothing is emitted between `?PNCOP` of item 1 and `LXI H` of item 2
  (E46M1 0037→003A, E46M16 0035→0038, CREATE 01A4→01A7...).  The blank E46L16 had measured between
  separate statements is an item-boundary effect in the runtime, not code (§4, E46M27).
* **H4 — item order is source order; nothing is folded or reordered. CONFIRMED.**  E46M5, M9, M10,
  M11 and M13 each spell one pair twice in opposite order and the chains come out in opposite
  order; E46M14's `list(v,v)` emits `LXI H,*D(000A)` TWICE (no common-subexpression folding) and
  E46M4's `list('A','A','B','A')` emits four chains that address TWO pool cells.
* **H5 — the pool behaves inside a list as across statements. CONFIRMED with one correction to my
  own model**: dedup by content (`'A'` twice = one cell, E46M4 DATA 11 ✓) but each EMPTY literal
  occurrence gets its own zero-length cell (E46M6: two `''` → two cells at 0009 and 000A ✓).  My
  compiler had been sharing one empty cell; that is fixed in `pool_str` and E46M6 is byte-exact
  against DR [C298].
* **H6 — authorization is per item, and the item question comes before the open question. MY
  PART IS TRUE; THE CLAIM ABOUT DR IS FALSE.**  My matcher refuses a list as a whole and names the
  offending position (E46M21-M26 all refuse, each naming the CLASS, none naming a position — that
  is what the panel pins).  But the ordering half was about DR, and P2a's "measured at N=1" claim
  for it was wrong: see §5.
* **H7 — the FIXED CHARACTER member behind an attach. DR ACCEPTED, and no object in this
  repository had ever shown it.**  E46M17 puts `rec.line` (CHARACTER(14) VARYING) and `rec.c10`
  (CHARACTER(8) FIXED) on a file: the fixed member's chain is `MVI A,08` then `?SLCTS`, i.e. the
  declared length as the width operand, exactly the shape E46L13 pins for a scalar.  Byte-exact
  (105/33) and now a specimen.  This was the one genuinely cold question in the set, and it is
  recorded as a new fact, not as a prediction that happened to be right [C297].

## 3. New facts about DR's file route (each from one object; none of them mine)

1. **A structure-valued item is refused** — `put file(outf) list(v,rec)` gets DR's `COMP REQ ?` at
   the statement, `1 ERROR(S) IN PASS 2`, no .REL (E46M24).  So is a **POINTER** (E46M25), which
   converts [C290]'s "no object prints a pointer" from an absence of evidence into a measured
   rejection on the file route.
2. **A literal subscript is folded into the address.**  `list(v,arr(2))` on `arr(3) fixed` emits
   `LHLD *D(0021)` where the array's base cell is 001F — two bytes along, no index computation at
   run time (E46M22; E46L10 in P2a's golden shows the same for `a(1)`).
3. **`k + 1` as a PUT item is `LHLD k / INX H`** — the cell loaded into HL and incremented in
   place, no call, no temporary (E46M23, and independently E46L9 from P2a).
4. **A LIST attach does not need an OPEN.**  E46M26 has no `open` statement and DR still emits
   `LXI H,*C(0000) / LXI D,0652 / LXI B,<cont> / CALL ?SIOOP` + chains + `?QIOOP`, 44 bytes total.
   [C282] had recorded that an unopened stream's attach is measured only on the EDIT route (P086K);
   E46M26 is the first measured **LIST** attach with no OPEN anywhere in the program.  That is one
   probe, and lowering it is not part of P2b (§10, and E46K10's row).
5. **Members are ordinary operands on this route.**  E46M16/M17/M18: `LXI H,*D(<member offset>)`,
   and the QUALIFIED spelling `rec.line` emits the identical operand to the bare `line` — [C253]'s
   one-cell-two-spellings rule re-verified behind a 0x0652 attach.
6. **A CHARACTER VARYING item emits no width byte** (E46M7: two varying items, 12+9+9+3 = 33 bytes)
   while a FIXED character item carries `MVI A,<declared length>` per item, never one width for the
   list (E46M3: 01, 02, 03 in order; E46M8: 0E then 0A).
7. **The empty literal is not deduped, and a zero-length allocation does not move the pool
   pointer.**  E46M6's `list('','A','')` addresses `*D(0009)` for the empty item, `*D(0009)` AGAIN
   for `'A'`, and `*D(000A)` for the second empty item — so DR gives each `''` its own cell (which
   is why my pool had to stop sharing one empty cell, [C298]) and `'A'` lands where the first `''`
   was allocated without advancing.
8. **A decimal LITERAL is `MVI A,<digits>` / `?DLDOP` / `MVI A,<digits+3>` / `MVI B,<scale>`** and
   its cell is packed BCD — `42` is one byte `0x42` plus one more (E46M5 at *D(000B)), and the two
   statements that name it share that one cell.  My compiler already emitted this (E16D/E17D), so
   it is recorded here as the reason my DATA arithmetic was wrong, not as a new lowering.

## 4. The runtime rows: DR's file bytes, then mine

Six rows in `spec/RUNTIME.txt`.  DR's side is `golden/e42p2bdr/` — DR's own .REL linked by
`oracle/linkrun.py` and executed, its output file exported whole (128-byte CP/M record included);
my side is my own byte-identical .REL, linked and run the same way, asserted by `file:` rows in the
gate's runtime panel (whole-file compare, no normalisation).

| probe | what it asks | DR's file content (bytes of content / 128) | predicted |
|---|---|---|---|
| E46M27 | is the blank a STATEMENT boundary or an ITEM boundary? | `'HELLO' 'XY' 'HELLO' 'XY' 'HELLO' 'XY'` (38) | 38 ✓ |
| E46M28 | three literals in one list | `'AA' 'B' 'CCC'` (14) | 14 ✓ |
| E46M29 | varying + bin + dec, then literal + varying | `'HI'        42       123 '=' 'HI'` (33) | 33 ✓ |
| E46M30 | two under-filled FIXED chars in one list | `'ABC     ' 'W   '` (17) | 17 ✓ |
| E46M31 | CREATE's six-item list, ordinary + members | `'JOHN' '1 HIGH ST' 'BOSTON' 'MA'     12345 '555-1212'` (53) | 53 ✓ |
| E46M32 | console PUT, file PUT, console PUT | `'CON' 'AGAIN'` (13) and console `FIRST SECOND` | 13 ✓ |

**E46M27 is the one that decides something no single-item object could.**  Four statements with 2,
1, 1, 2 items into one file: a blank per *statement* boundary gives 33 + 3 = 36 bytes, a blank per
*item* boundary gives 33 + 5 = 38.  DR wrote 38.  [C295] had measured one blank between separate
one-item statements and could not distinguish the two rules; this does, and the rule is the item
list's [C299].  The apostrophes are on every character item (`'AA'` is 4 bytes quoted) and the
numerics are 9 wide, right-justified, unquoted (p+3, [C292]) — E46M29's `        42` and
`       123` and E46M31's `     12345` are all the same nine-byte field.

My own bytes follow DR's because the objects are identical; the assertion that matters is the file
comparison, and it is in the gate rather than in my prose.

## 5. Two places where my recorded knowledge was wrong, written down rather than quietly fixed

**(a) The E46K10 guard order was mine, not DR's — [C256] again, caught this time.**
P2a registered E46K10 (`put file(outf) list(line);` with no OPEN) with prose saying the item
question is answered BEFORE the open question, "measured" at N=1, and P2b's HYPOTHESES.md carried
that into a prediction that DR would REFUSE the same shape with `COMP REQ ?`.  DR's object
`golden/e42p2b/E46M26/E46M26.REL` compiles it in 44 bytes with no `?OIOOP` anywhere.  So the
sequence of my own claims about that order was: unmeasured → claimed measured → **wrong**.  E46K10's
row is re-classified from `unmeasured` to `my-gap` with both halves cited, and the refusal that now
fires is my completeness guard, not a DR rule.

**And a claim I made in the middle of this milestone and then withdrew, which is the more
instructive half.**  While writing that row I asserted that re-reading P086K showed its PUT to be
`put file(f) list(d)` — a plain LIST PUT on an unopened stream — "not an EDIT as [C282] recorded".
It is not.  `probes/P086K.PLI` reads `put file(f) edit(d)(f(5,1)); get file(f) edit(d)(f(5,1));` and
its object runs `?EDITF / ?DLDOP / MVI A,08 / MVI B,02 / ?QDCOP / ?EDTOV` at 0022-003A: [C282] was
right and I was wrong, and I had written the correction into the panel before checking the source I
claimed to be correcting.  The withdrawn sentence is gone from `NEG_META["E46K10"]` and its
withdrawal is recorded there in its place, because "I re-read the object and it says something else"
is exactly the kind of sentence a reader cannot re-check without the transcript of the mistake.  The
LIST-attach-without-OPEN fact stands on E46M26 alone — one probe, one object — and that is how both
the row and §10 state it.

**(b) `NEG_META["E46K10"]` was dead text.**  The panel sets it at one place and then a loop over
`E46K1 … E46K15` reassigns every K key afterwards, so the specific, evidence-bearing prose P2a
wrote for K10 had never been the text the panel reported.  The entry now sits after the loop and a
comment says why.  A panel row whose prose is silently overwritten by a later generality is worse
than no prose: it reads as evidence and is not.

## 6. The defect this milestone found: `put file(f) skip;` was being written to the console

The corpus census is what caught it.  Before P2b, CREATE refused at line 39 — the six-item list,
E41X7's gap.  After the multi-item matcher landed, CREATE's message moved to line **44**.  Line 41
is `put file(output) skip;`, and if the refusal moved past it, the statement was getting through —
which it was: `match_put_list_lit`'s bare-`put skip;` arm (added by [E2E-29/P4] from REVERSE:00FE)
matched on the item list alone and **ignored `on_opts` and `stream`**, so a file-named bare SKIP was
lowered on the CONSOLE route — `LXI D,0252 / ?SYSPR / MVI A,01 / ?SKPOP / ?QIOOP`, bytes that are
right for the wrong stream, rc=0, no `[TBD]`.  Nothing in a compile of CREATE could see it, because
CREATE still refused, just further down.

Fixed by splitting the arm into three: a file-named control item now goes to `file_items` and
refuses by name; a control item with any other ON option refuses; the bare console `put skip;` is
unchanged (`stream = None`, `on_opts = []`).  The shape is pinned as REJECTS row **E41X9** with kind
`my-gap`, because DR's CREATE carries it: 01AA `?SIOOP`, 01B6 `MVI A,01`, 01B8 `?SKPOP`, 01BB
`?QIOOP` — 18 bytes, attach to close, with no item chain [C300].

Two census messages moved as a result and the snapshot was refreshed (`tools/corpus_census.py
--check spec/census/corpus-census.json`, counts identical):

* **CREATE**: refusal line 39 → **44** → back to **41**.  Line 39's six-item list is lowered now
  (that is E41X7 retired and E46M19 as a specimen); line 41's bare file SKIP is refused again,
  correctly, by E41X9's guard.
* **COPYLPT**: `PUT ITEM (PAGE) deferred` → `PUT FILE(PRINTFILE) LIST item 1 is the control item
  PAGE`.  Same statement, now refused by the route that owns it and naming the file.

Both counts are unchanged (`REFUSED 26`, `EXACT 15`, `DIFFERS 0`), so this is message drift, not
verdict drift, and the reason is in this section rather than in a regenerated file alone.

DR's own source format also bit once, before any prediction was scored: a comment line wider than
72 columns is TRUNCATED, so a probe whose comment ran to 233 columns arrived at DR with an
unterminated `/*` that then ate the rest of the file — `UNEXPECTED EOF`.  Commit `5de6b08` wrapped
all 32 probes to ≤71 columns and the PRN-vs-git comparison in §0 is the check that nothing else
drifted.

## 7. What the predictions were worth, and what the model was wrong about

The CODE model — `predict_sizes.py`, a cost model over prologue + per-item chain + close — hit
every one of the 20 sizes it was asked about, and hit the ?SIOOP/?QIOOP counts in all 40 places.
The DATA misses are different in kind, because **there is no DATA model**: `predict_sizes.py`
computes CODE only (its docstring claims "CODE/DATA", which is an overclaim, corrected in this
commit), and the DATA column of HYPOTHESES.md is my hand arithmetic over declared capacities.
Nine of 20 were wrong, and the misses are not random: **eight are exactly one byte LOW** (M10
32→33, M11 34→35, M13 15→16, M14 32→33, M15 50→51, M16 26→27, M17 32→33, M18 50→51) and one is
five bytes HIGH (M5 18→13).

Four of the nine are diagnosable from DR's own numbers, and they are all the same slip:

| probe | DR DATA | my hand count | DR's layout, read out of the object |
|---|---|---|---|
| E46M17 | 33 | 32 | title `M17OUT DAT` 10 bytes at *D(0000), then auto: `c8` 8 at *D(000A), `line` **15** at *D(0012) — `1 + capacity`, the length byte [C291] |
| E46M16 | 27 | 26 | title 10 + `line` 15 + `nxt` 2 = 27 |
| E46M10 | 33 | 32 | title 10 + `v char(20) varying` **21** + `k` 2 = 33 |
| E46M13 | 16 | 15 | title 10 + `k` 2 + `z fixed dec(6)` 4 = 16 — I charged 3 for the decimal cell |

The rule I kept forgetting is [C291]'s own: **a CHARACTER VARYING cell is capacity + 1**, and the
DATA segment is laid out **pool first, then auto** — which is the opposite of the order my
arithmetic assumed.  E46M18 is the clean demonstration: its pool is the 10-byte TITLE plus `' = '`
(3) = 13, so the scalar `v char(20) varying` sits at *D(000D) = 21 bytes (20 + the length byte),
the structure's `line` at *D(0022) = 13 + 21 = 34, `nxt` at *D(0031) = 34 + 15, and DATA is
13 + 21 + 15 + 2 = 51 — DR's number exactly, where my hand count said 50 because I used 20 for
`v` and 14 for `line`.  E46M5's −5 is a different
slip and it is diagnosable too: `list('X=',42)` and `list(42,'X=')` share ONE two-byte cell for the
literal 42 at *D(000B) (DR's DATA head is `M5OUT DAT` `58 3D` `42 00` = 9 + 2 + 2 = 13), so
**decimal literals are deduped by value across statements exactly as character literals are
[E46M4/[C155]]** and a decimal literal's cell is 2 bytes for two digits — packed BCD, `0x42` for
`42`, which my compiler already emits since its object is byte-identical.  My arithmetic charged
the decimal cell twice, once per statement, and a wider one besides.

What I do NOT claim is a general DATA-layout model: the remaining four (+1 on M11, M14, M15, M18)
fit the same two slips but I have not re-derived each of their cell lists from the object, so they
are reported as misses with a diagnosed family, not as four verified diagnoses.  None of this
affects the objects,
which are byte-identical: the compiler's allocator already produces DR's layout because it was
built against DR's earlier objects, not because my model describes it.  A size model is a
hypothesis too, and the honest reading of §1 is "the model is exact about code and wrong about data
in a regular way, and the data numbers were never modelled at all".

## 8. Implementation: what actually changed in `ocaml/lib/codegen.ml`

1. **`file_items` / `file_item_of` / `file_item_desc` (new, ~line 2351)** — the matcher's validator
   for a file PUT LIST: it names each item's shape, returns `Some items` when every one is a shape
   the route can lower, and raises with the item's POSITION and CLASS otherwise.  A list is refused
   as a whole: no byte, not even the attach, is emitted for a list with one unauthorized item.
2. **`match_put_list_lit`'s FILE arm (was single-item)** — `items = [Pi_data x]` became
   `items } when items <> []`.  That is the whole lowering change: `lower_put_items_gen` has folded
   over an item list since [E2E-29/P1], emitting one prologue, the chains in order, and one
   `?QIOOP`, which is precisely DR's structure.  C293 (one generator, two prologues) did not need
   to be re-derived; it needed to be *allowed*.
3. **`authorize_file_item`: `Vimem` admitted (was refused)** — E46M16-M20 are the evidence.  FIXED
   BINARY, POINTER and CHARACTER members behind an attach all compile byte-exact; the DECIMAL
   member is refused earlier, at bind, because the unqualified-member registry does not cover
   decimal members [E2E-39/P2] (E46M20 is that row, and it is a bind gap, not a PUT gap).
4. **`char_var_ok` bypassed when `file <> None`** — the console multi-item classifier is not the
   file route's authorization.  E46M11/M15 proved the file route does not need it; E46M12 proves
   the console classifier is still refusing a pair DR accepts, and stays a my-gap.
5. **`pool_str`: a fresh zero-length cell per empty-literal occurrence** — E46M6 [C298].
6. **`bare_ctl_put` (new, the E41X9 guard)** — §6.

## 9. Panel state after this milestone

```
e2e gate: 1056 byte-exact / 0 fail of 1056        (24 of those are new: 23 probes + E46L7 promoted)
e2e gate: negative panel clean (182/182 refused)  (10 new rows: E41X9, M12, M16, M20-M26; 2 retired)
e2e gate: divergence panel 9/9 as recorded
coverage panel   coverage_check: 96 rows, 0 errors, 0 warnings
corpus census    counts unchanged: EXACT 15, DIFFERS 0, REFUSED 26, DR_REJECTED 3
file prose       5 active files clean
bind gate: 43 exact / 2 known-gap / 2 FAIL of 47  (the two FAILs are P008 and P063A, pre-existing,
                                                   still reported — this milestone neither fixes
                                                   nor hides them)
warning profile  identical to c816af5: 252 warning lines, same counts by kind (22 W11, 15 W26,
                 28 W27, 2 W32, 14 W39, 2 W57, 17 W8, 26 W9), same file:line signatures
```

## 10. What P2b does NOT claim

* **No SKIP, PAGE, ON, COUNTED-SKIP or line-control on a file PUT** (E41X6, E41X9 refuse; DR's
  bytes exist and are decoded in DR-EVIDENCE.md, but no object of mine carries them).
* **No GET FILE, no record WRITE/READ, no KEYED/DIRECT anything, no PUT EDIT on a file** (E41X8
  unchanged — it refuses on the EDIT route for [C245]/[C250] reasons, not on the file route).
* **No multi-item console PUT of members** (E46M16 is the row), and **no console PUT of a decimal
  beside a character** (E46M12).  Both are DR-accepted; both are console-route work, outside P2b.
* **No lowering of an unopened attach.**  E46M26 measures that DR does it for a LIST item and
  E46K10 is my refusal of the same shape; the guard is deliberate and is now documented as a
  measured gap rather than as an unknown, and lowering it needs its own sub-phase (one probe is not
  a perimeter).
* **CREATE and KEYFILE are still REFUSED in the census.**  P2b removed their multi-item blocker and
  left the rest: CREATE's SKIPs, KEYFILE's `KEYED`/`ENVIRONMENT`/`LINESIZE`/variable-TITLE opens and
  `read ... keyto`.  Neither program is claimed as an achievement of this phase.
* **No claim that DR's DATA layout is understood.**  Nine predicted DATA sizes were wrong (§7); the
  compiler reproduces DR's layout byte-for-byte because it already implemented it, not because the
  model here describes it.

## 11. AFTER THE 32: the option arm's stale text, three oracle calls, and probe format

Re-wording a refusal is a documentation event here, not a string edit ([C282]), so the arm
[E2E-41/P3b] wrote got re-checked against the evidence it cites.  It failed that check.  Its text
said the shapes reaching it include "a multi-item file PUT (CREATE's six)" — which stopped being
true when E46M19 landed — and `grep -n "options this route" tools/e2e_gate.py` came back empty, so
NO REJECTS row keyed the sentence either: it was prose describing nothing.  `tools/file_prose_check.py`
pinned it as a marker the negative panel matches, and the FIRST gate run after I deleted it failed on
that pin, which is the guard working, not a regression.

What can still reach the arm, measured by running it: a **duplicated FILE option**, an **empty LIST**,
and **N options**.  (`put on(x) list('A')` — the ON-handler spelling the old text named — does not
PARSE here at all: `PUT: expected LIST/EDIT/ITEM/FROM`.  Recorded rather than deleted, because the arm
is a defensive default and a reader should know that branch is unreachable.)  The first two went to
the oracle with their predictions committed first (`ae15bee`), and DR refused both:

| probe | statement | DR's answer | my answer | prediction |
|---|---|---|---|---|
| E46M33 | `put file(outf) file(outf) list('A');` | `7 c … / SYNTAX ? / 1 ERROR(S) IN PASS 2`, **no `.REL`** | `[TBD] PUT LIST with 2 ON options on one PUT (line 7)` | refusal — **right** (model sizes 83/98 void) |
| E46M34 | `put file(outf) list();` | `7 c … / SYNTAX ? / 1 ERROR(S) IN PASS 2`, **no `.REL`** | `[TBD] PUT LIST with an EMPTY LIST behind a FILE option (line 7)` | refusal — **right** (model size 72 void) |

Note the diagnostic word: `SYNTAX ?`, not the `COMP REQ ?` of E46M24/E46M25.  DR has at least two
pass-2 failure voices and they say different things — `COMP REQ` is "no generator for this operand",
`SYNTAX` is "this spelling is not a statement" — which is why [C301] keeps them separate instead of
recording "DR errors" as one class.

**The aborted run, and why the format of a probe is part of the evidence.**  The first submission of
those two probes (tag `e42p2b4`) came back `10 b / SYNTAX ? / UNEXPECTED EOF` on a nine-line file,
which is not an answer about `put file(f) file(f)` at all: that source was wrong in **two**
independent ways — UNIX LF line endings, and `end E46M33.` with a period where every accepted probe
uses `end <name>;`.  A confounded oracle result attributes to nothing, so two more probes unconfound
it (tag `e42p2b6`, predicted in HYPOTHESES.md §6):

* **E46M35 (CRLF + trailing period):** `7 b end E46M35. / SYNTAX ? / UNEXPECTED EOF`, no object.  The
  period is a refusal by itself.
* **E46M36 (LF + correct `;`):** `UNEXPECTED EOF` and **no source listing at all** — DR never read it
  as lines.  LF-only input is not a variant of the language; it is a different file.

Those two rows are protocol facts, not panel rows: neither can be a SPECIMENS entry (no object) and
neither can be a REJECTS entry (my compiler *accepts* both shapes).  `golden/e42p2b4/` is committed as
the record of the malformed submission rather than deleted, so the sequence is auditable.

**The line-number defect this exposed, which is MINE and pre-dates P2b.**  With CRLF sources my
refusal messages name the statement's own line (both rows above say `line 7`, which is where DR's
listing puts the statement).  With LF-only sources the same file prints `line 4` for E46M33 and
`line 3` for the same shape in a shorter program, and running those LF files through the binary built
at **baseline `c816af5`** gives `line 3` too — so the mis-count is line-ending handling in the lexer,
not anything P2b wrote.  The offset is not constant (3, 4, 4, 6 measured across four layouts) and the
mechanism is untraced; no byte is affected, and the panel is unaffected because `tools/e2e_gate.py`
writes every negative source as CRLF + `^Z` itself.  It is [C303] so that a future reader of a
`[TBD]` line number knows which convention that number assumes.
