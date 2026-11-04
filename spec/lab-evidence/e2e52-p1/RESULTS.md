# E2E-52/P1 — RESULTS (scope-aware DEC pool prescan bank E52A..E52J; LOAN2 blocker class)

## 0. Lineage

- Probes + `mkprobes.py` + `PLAN.md` + `HYPOTHESES.md` + `BASELINE-MINE.txt` committed
  BEFORE any DR call at **`d1fbc16`** (the prediction SHA, verified in this session:
  `git log --format=%h -- probes/E52A.PLI | tail -1` -> `d1fbc16`). Every probe is
  CRLF + bare `^Z`, all lines <= 71 columns, apostrophe-free ([C193] (b)); the keys
  E52A..E52J were collision-checked against `spec/INVENTORY.txt` and `probes/` before
  writing ([C193c]). `golden/e52p1` did not exist before the run (verified absent at
  HEAD `d4a8ced` immediately before the call).
- ONE oracle campaign, exactly as pre-registered:
  `PLI_SRC=probes timeout 900 python3 oracle/batch.py E52A E52B E52C E52D E52E E52F
  E52G E52H E52I E52J --tag e52p1 --switches '$L$D'`
  -> **10 ok / 10** (`golden/e52p1/summary.txt`; the runner split internally into three
  batches of 4/4/2; rc=0, wall clock 27 s, NO timeout). Never `--reuse`.
- **NO refusals at all**: every one of the ten `.PRN` prints `NO ERROR(S) IN PASS 1` and
  `NO ERROR(S) IN PASS 2` (`grep -c 'NO ERROR(S)'` = 2 on every file; the same two lines
  are the only occurrences of the string `ERROR`). DR ACCEPTED every cross-scope
  homonym / pool-dedup form in the bank — the acceptance premise of this round HOLDS,
  and the `[C193](a)`-style DUPLIC refusal precedent does not transfer to shadowing.
- Verdicts judged on COMPLETE `.REL` files byte-for-byte with `tools/reldump.py`
  (PROTOCOL #6) plus whole-file `cmp`; DATA offsets read from the `RELOC data` operands
  and `LINK-DEF-DATA-SIZE`, not from my compiler's stderr `DATA=` header (the standing
  relstats warning).
- Classification (PROTOCOL #3): **six `my-gap` rows (E52B, C, D, G, H, I)** — DR emitted
  an object for each and `BASELINE-MINE.txt` shows my compiler refusing each one with
  the SAME named blocker; **four rows (E52A, E, F, J) are already whole-file
  `cmp`-BYTE-EXACT against the DR golden** (they compile on mine today; the four
  shas are `8217250a…`, `4fe89c7d…`, `8c09f2e7…`, `0a3f6b6a…` — identical in mine and
  in `golden/e52p1/`). **No `dr-refuses` row exists in this bank.**
  HYPOTHESES falsification condition 3 is therefore **NOT triggered**: my current
  objects reproduce DR's pool dedup, cell sizes and pool order on the single-scope and
  non-shadowed shapes, so no background law this bank reuses is in question.
- PRN size headers vs the prediction table: DATA AREA `0009` (A, F), `0010` (B, H),
  `0008` (C), `000A` (D, E), `0014` (G, J), `0015` (I); CODE SIZE `0030` (A, B, F),
  `0026` (C, D), `0020` (E), `004A` (G), `0047` (H), `004D` (I), `0054` (J).

Head notation below (same convention as E2E-51): `21 rN` = `LXI H` with a 2-byte DATA
reloc to offset `N`; `21 lo hi` = `LXI H` immediate; `3E pp` = `MVI A,pp` the DEC
precision descriptor; `2A rN` / `22 rN` = `LHLD` / `SHLD` of a DATA reloc target;
`CD ?DLDOP` / `CD ?DSTOP` / `CD ?DCMOP` / `CD ?DSUOP` = the PLILIB decimal helper calls
(`LINK-CHAIN-EXT` record spelled in place). Frame in every row: `01 00 02 / CD ?START`
at code 0000 and `CD ?STOPX` at the tail.

## 1. Prediction vs verdict (every MISS kept verbatim — this round has ONE)

| id | shape (one controlled difference) | predicted (HYPOTHESES) | measured verdict | score |
|---|---|---|---|---|
| E52A | homonym, SAME type (`i dec(4,2)` outer and inner), both `i = 3` | H1 pool 3 (image dedup across scopes) => DATA 9; H4 rival: 6-byte pool => DATA 12 | ACCEPTS. `LINK-DEF-DATA-SIZE abs 0009`; ONE 3-byte pool cell `00 03 00` at `*S 0000`; outer `i` cell at `0003`, inner at `0006`; both stores load `21 r0` (the SAME cell) | **HIT on H1/H3, H4 FALSIFIED** — the literal pool is keyed by the encoder byte image program-wide, not per scope ([C178] extends across scope boundaries) |
| E52B | `i dec(4,2)` outer / `i dec(9,2)` inner, both `i = 3` (LOAN2 class in miniature) | H1: two cells, pool 8, DATA 16; H3 rival: outer-wins, pool 3, DATA 11 | ACCEPTS. `LINK-DEF-DATA-SIZE abs 0010`; pool = 3-byte `00 03 00` at `0000` + 5-byte `00 03 00 00 00` at `0003`; outer store `21 r0 / 3E 04 / DLDOP / 21 r8 / 3E 04 / DSTOP`; inner store `21 r3 / 3E 09 / DLDOP / 21 rb / 3E 09 / DSTOP` | **HIT on H1, H3 FALSIFIED** — the inner store is typed at the INNER declaration (5-byte image, precision byte `09`, target `000B` = the inner 5-byte cell) |
| E52C | DEC outer (`i dec(4,2)`) / `i fixed bin` inner, both `i = 3` | H1: pool 3, inner store = binary immediate `LXI H,0003 / SHLD`, no cell; H3 rival: same DATA but the DEC helper route inside | ACCEPTS. DATA `0008` (pool 3 at `0000`, outer cell `0003`, inner 2-byte cell `0006`); inner CODE `21 03 00 / 22 r6` — `LXI H` immediate then `SHLD`, **no `?DLDOP`/`?DSTOP` in the nested procedure at all**; CODE 0026 | **HIT on H1, H3 FALSIFIED on the CODE discriminator** (DATA alone could not separate them, exactly as pre-registered) |
| E52D | `i fixed bin` outer / `i dec(7,2)` inner, both `i = 3` | H1: inner 4-byte cell, pool 4, DATA 10; H3 rival: inner typed binary, pool 0, DATA 6 | ACCEPTS. DATA `000A`; pool = ONE 4-byte cell `00 03 00 00` at `0000` (= ceil((7+1)/2), [R507]); outer store is the binary immediate `21 03 00 / 22 r4`; inner store `21 r0 / 3E 07 / DLDOP / 21 r6 / 3E 07 / DSTOP`; CODE 0026 | **HIT on H1, H3 FALSIFIED** — DATA-SIZE discriminator `000A`, not `0006` |
| E52E | inner writes the NON-shadowed outer `o dec(9,2)` | H1: pool 5 + `o` cell 5, DATA 10; H2 (own-rows-only) is an invariant test on MY post-fix object, not a DR model | ACCEPTS. DATA `000A`; pool 5-byte `00 03 00 00 00` at `0000`, `o` cell at `0005`; the nested store is `21 r0 / 3E 09 / DLDOP / 21 r5 / 3E 09 / DSTOP`. **My object is whole-file byte-identical to the golden** (sha `4fe89c7d…`) | **HIT** — outer declarations ARE visible to a procedure's pool demands; H2 (own-rows-only) is falsified for DR by this row and is kept as the constraint my fix must not introduce |
| E52F | different names `a`/`b`, SAME type, SAME image | H1: pool 3 (name-blind dedup) => DATA 9; H4 rival: DATA 12 | ACCEPTS. DATA `0009`; ONE 3-byte pool cell at `0000` loaded (`21 r0`) by BOTH the outer `a = 3` and the inner `b = 3`; cells `a` @`0003`, `b` @`0006` | **HIT on H1, H4 FALSIFIED** a second time, independently of shadowing — the pool key is the byte image, name-blind |
| E52G | FORMAL shadow (the LOAN2 `current_year` shape): formal `i dec(9,2)` + literal store `i = 3`; outer `i dec(4,2)` + `i = 3`; `call q(i)` | H1: pool 8 (3 outer + 5 formal-target); "DATA approx 16; formal-cell WIDTH on DR is itself an open measurement — do NOT fit to it, report it"; H3 rival: pool 3 | ACCEPTS. DATA `0014` (20), CODE `004A`. Pool = 3-byte `00 03 00` @`0000` + 5-byte `00 03 00 00 00` @`0003` (**H1 pool CONFIRMED, H3 FALSIFIED**). Measured cell map: outer `i` 3 B @`0008`; **2-byte argument-pointer block @`000B` whose DATA word holds the absolute address `000D`** (`LINK-SET-LC data 000B` + `RELOC data 0x000D`); **5-byte main-side copy-in temp @`000D`**; **2-byte formal pointer cell @`0012`**. Main-side copy-in `21 r8 / 3E 04 / DLDOP` then `21 rd / 3E 09 / DSTOP` (load at ACTUAL precision, store at FORMAL precision); q prologue `5E 23 56 EB / 22 r12` (MOV E,H / INX H / MOV D,(HL) / XCHG / SHLD) dereferences the block into its own pointer cell; the literal store is `21 r3 / 3E 09 / DLDOP` then **`2A r12`** `/ 3E 09 / DSTOP` — `LHLD` of the POINTER cell, not `LXI H` of a value cell | **MISS on my DATA prediction, kept verbatim:** predicted "approx 16", measured **20 (0x14)** — DR allocates NO 5-byte value cell for the DEC formal; the extra 4 bytes are the 2-byte arg block + 2-byte formal pointer cell and the 5-byte copy-in temp sits in MAIN, so the picture is `8 pool + 3 outer + 2 block + 5 temp + 2 pointer = 20`. The pre-registered instruction was NOT to fit this; it is REPORTED. The literal-to-DEC-formal route itself was already proven by the S2 scratch check (`BASELINE-MINE` appendix) |
| E52H | three scopes: main `x dec(4,2)` stores 3; mid `m` declares `x dec(9,2)` and stores 3; innermost `n` declares NO `x` and stores `x = 3` | H1: resolves through MID — 5-byte image deduping onto MIDs cell, pool 8, DATA 16; rival own+main env: ALSO DATA 16 but the 3-byte MAIN image and MAIN target; discriminator declared as CODE/reloc | ACCEPTS. DATA `0010`; pool 3-byte @`0000` (main) + 5-byte @`0003` (mid); main cell @`0008`, mid cell @`000B`. ns store is `21 r3 / 3E 09 / DLDOP` then `21 r b / 3E 09 / DSTOP` — **identical operand pair to MIDs own store** (the 5-byte MID image, not the 3-byte MAIN image; precision byte `09`, not `04`; target `000B`, not `0008`); CODE 0047 | **HIT on H1, own+main rival FALSIFIED on the pre-registered CODE/reloc discriminator** — resolution goes through EVERY intervening scope, not just main |
| E52I | three scopes: main `x dec(4,2)` stores 3; mid declares `x dec(9,2)` and stores nothing; innermost tests `if x > 0 then x = 1` | H1 (lexical typing of the CONSUMER): pool 3 + 5 + 5 = 13, DATA 21; rival main-only sizing: pool 9, DATA 17 | ACCEPTS. DATA `0015` (21) — pool = 3-byte `00 03 00` @`0000` (mains store), 5-byte `00 00 00 00 00` @`0003` (the CONDITION literal `0` sized at `dec(9,2)`), 5-byte `00 01 00 00 00` @`0008` (the THEN-store literal `1`); main cell @`000D`, mid cell @`0010`; `n` runs `21 r3 / 3E 09 / DLDOP`, `21 r10 / 3E 09 / DLDOP`, `CD ?DCMOP`, `F2 <fwd>`, then `21 r8 / 3E 09 / DLDOP`, `21 r10 / 3E 09 / DSTOP`; CODE 004D | **HIT on H1, main-only sizing FALSIFIED** — `DATA-SIZE discriminator 0015`, and this row measures the **prescan_cond consumer** path directly: the condition literal is sized by the lexically resolved variable, not by the outer homonym |
| E52J | NO shadowing: proc-local `d dec(9,2)`, `d = 3`, `do while (d > 0) d = d - 1;` | control row — pins the existing single-scope prescan; my post-fix object must stay byte-identical (sha `0a3f6b6a…`) | ACCEPTS. DATA `0014` = three distinct 5-byte pool cells (`0000` = 3.00, `0005` = 0.00, `000A` = 1.00) + `d` @`000F`; **my baseline object is whole-file byte-identical to the golden** (sha `0a3f6b6a…`) | **HIT** — control row green; harness and the settled pool laws ([C178], [R507], [R608], [C179]) all validate before any other verdict is read |

**Count: 9 clean HITs, 1 MISS kept as written** (E52G DATA 20 vs predicted "approx 16";
the row's pool half was predicted correctly and every competing-refusal hypothesis is
falsified by the acceptance itself).

Model scoreboard after measurement: **H1-lexical CONFIRMED** on every discriminating row
(B DATA, C CODE, D DATA, H CODE/reloc, I DATA, G pool); **H3-global-outer FALSIFIED**
(five independent discriminators); **H4-per-scope-pool FALSIFIED** (A and F); **H2**
is falsified for DR by E and stands as the invariant my fix must preserve.

## 2. Laws read out of the `.REL` records (byte tier only)

Each item below is derived ONLY from the goldens in `golden/e52p1/` compiled from
`probes/E52*.PLI` by DR PL/I-80 v1.4 (`$L$D`); claims to be registered from this
section and nowhere else.

### 2.1 The scope-resolution law for the decimal pool (the fix direction)
- A variable reference is typed at its **INNERMOST enclosing declaration** at pool time
  exactly as it is at lowering time: E52B (inner store sizes its image at `dec(9,2)` and
  targets the inner cell), E52D (the inner DEC cell exists at all), E52C (the inner
  `fixed bin` store takes the binary-immediate route and allocates no pool cell),
  E52H (resolution passes THROUGH an intervening scope to `main`s homonym is NOT what
  happens; mid wins).
- Shadowed names never produce a conflicting-kind error: DR compiles the shape that my
  prescan refuses BY NAME (`declared with conflicting kinds`) on all six `my-gap` rows.
- Resolution reaches beyond the immediate pair of scopes (E52H: three scopes, innermost
  unqualified reference binds to the MID declaration) and applies inside CONDITION
  forms too (E52I: the comparison literal `0` and the THEN-store literal `1` are both
  sized at the mid `dec(9,2)`), i.e. every consumer of the type map in this bank uses
  the same lexical map.
- Non-shadowed outer variables remain visible inside a procedure (E52E): the prescan
  environment is an ACCUMULATION (inner-first with the outer rows still reachable), not
  a replacement.

### 2.2 The pool is ONE program-wide, image-keyed table (across-scope dedup)
- E52A (same name, same type, same image in two scopes) and E52F (different names, same
  type, same image) each allocate **ONE** 3-byte cell, loaded by both stores
  (`21 r0` twice): the [C178] encoder-image dedup is **scope-blind and name-blind**.
  Pool cells are laid in **source/statement order ahead of the variable cells**,
  including across scope boundaries (E52B: main image @`0000`, inner image @`0003`;
  E52H: main @`0000`, mid @`0003`; E52I: main store, then `n`s condition literal, then
  `n`s store literal).
- Cell width stays the target-precision rule ceil((p+1)/2) [R507] applied to the
  LEXICALLY resolved target (B: 3 and 5; D: 4; G: 3 and 5; H: 3 and 5; I: 3, 5, 5), and
  the DEC helper precision descriptor is `MVI A,p` of that same resolved precision
  (`04`, `07`, `09` measured).

### 2.3 DEC formal shadow (= LOAN2 `current_year`) cell map — measured, not fitted
- The formal of a nested procedure that shadows an outer DEC name is a **2-byte pointer
  cell**, not a value cell (E52G @`0012`), and the store into it goes through
  `LHLD` of that pointer cell (`2A r12`) before `?DSTOP` — the [C131] `?DSTOP` route
  with the pointer indirection this compiler already implements for the unshadowed S2
  shape.
- The call materialises, in the CALLER's DATA: a 2-byte argument-pointer block holding
  the absolute address of a **main-side copy-in temp of the FORMALS precision**
  (`dec(9,2)` = 5 bytes), and the copy-in itself is a load-at-ACTUAL-precision +
  store-at-FORMAL-precision pair (`3E 04` then `3E 09`). The callee prologue
  `5E 23 56 EB / 22 r12` copies the block word into its own pointer cell.
- Consequence for demand accounting: the literal cell for `i = 3` inside `q` is keyed by
  the FORMAL's precision (5 B) and is distinct from main's 3-byte cell (pool 8 total),
  while the DATA total for this shape is 20, not 16.

## 3. What this evidence does NOT say (NOT-say; keeps the next step honest)

- NOTHING about runtime or linking: no `.COM`, no PLILIB execution, no `spec/RUNTIME.txt`
  row comes from this round. Byte tier only.
- Nothing about homonyms whose kinds are OUTSIDE this bank: `CHARACTER`/`VARYING` vs DEC,
  arrays vs scalars, `STATIC`/`EXTERNAL` attributes, pointer/deref forms, or a formal
  shadowing a name with a non-DEC outer kind. Those stay `[TBD]` and my compiler must
  keep refusing them BY NAME.
- Nothing about whether DRs own prescan is a separate pass or the same walk — only that
  its observable typing is lexical, accumulation-based and shared by every consumer
  sampled (store, condition, formal copy-in).
- Nothing about the REST of `artefacts/LOAN2.PLI`: its blocker message and the existence
  of `golden/first/LOAN2/LOAN2.REL` are all that is settled; whether the scope-aware fix
  advances LOAN2 (and to which next blocker) is a MEASUREMENT to be taken after the fix,
  recorded verbatim and NOT fixed further in P1.
- The E52G cell map is measured for THIS shape (DEC formal, DEC actual, literal store).
  It is not a general formal-layout law; [C187] remains the settled nested-layout claim.
- No claim is made that my post-fix objects will match; falsification condition 4 of
  HYPOTHESES.md governs (any non-byte-exact E52 object, or an E52J/E51 regression, stops
  the round at evidence + a corrected PROPOSAL).

## 4. Goldens (registered as a round bank; never re-derived)

| id | bytes | sha256 (golden/e52p1/<id>/<id>.REL) | mine today |
|---|---|---|---|
| E52A | 256 | `8217250ad3cd2fcf496d293527294ab53f32320950e19cb5685a6226a6356fbe` | byte-exact |
| E52B | 256 | `bd67501d2cfbce6eb22a5a1e6b6a97fcae2aee99ed45f5688124fcb46e48bd4f` | refuses (my-gap) |
| E52C | 256 | `b05639ae8187646fadcf4f98e4206a07f224132a1b2062a699ab11e149146ad5` | refuses (my-gap) |
| E52D | 256 | `433a37a2ef51c91a6d6971b85a67cfbc70135d68659436b6441841a042b34ae5` | refuses (my-gap) |
| E52E | 256 | `4fe89c7ddb0bb622c98b076d0613a009f71bb2834fc935423e7f6dfb74311bfc` | byte-exact |
| E52F | 256 | `8c09f2e7e66f6b81c31a53fb5f0ed2f73de18c02dbe2007fad6cdd6d7ad26900` | byte-exact |
| E52G | 256 | `39b3d7cfe775c039d25b3791ed2f71b3e333509ca1193f3759ce46a850134c67` | refuses (my-gap) |
| E52H | 256 | `85c41e0462293b4357c998645dadbad1f180e46a4dc84a7f86992ebd28060258` | refuses (my-gap) |
| E52I | 384 | `0b57b024c2012b0ab674f1d04f93b244326f70a01e60796012b13144336bd027` | refuses (my-gap) |
| E52J | 384 | `0a3f6b6a33ce56303448527897bc5e1b38fc3593f7295cc937ad20d17cf635ee` | byte-exact |
