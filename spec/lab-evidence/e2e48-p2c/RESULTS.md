# E2E-48/P2c — RESULTS: prediction vs verdict, measured DR laws (round 3)

## §0 Ordering and provenance (PROTOCOL #1)

* Predictions pre-registered at commit **`f9f21f2`** (`probes/E48C1..E48C9.PLI`
  + `HYPOTHESES.md` + `BASELINE-MINE.txt`), committed BEFORE any oracle call on
  an E48C probe. `git diff f9f21f2 HEAD -- probes/E48C*.PLI spec/lab-evidence/e2e48-p2c/HYPOTHESES.md`
  must be empty at audit time.
* Oracle: `PLI_SRC=probes python3 oracle/batch.py E48C1..E48C9 --tag e48p2c
  --switches '$L$D'` → **9 ok / 9**, every probe produced a `.REL`; goldens in
  `golden/e48p2c/<N>/`. Round-1/2 goldens (`golden/e48p1/`) untouched.
* All byte readings below come from the `.REL` records through
  `spec/lab-evidence/e2e42-p2b/chaindump.py` and `tools/reldump.py`, never from
  a `.PRN` ([C264]).

## §1 Prediction vs verdict (the committed rows of HYPOTHESES.md)

| # | probe | predicted | measured (E48Cn golden) | verdict |
|---|---|---|---|---|
| P1 | E48C1 | accept; flat store 17 bytes `21 *S / 11 *D(name) / 3E 03 / ?SCVCM / D6 01 / 9F / 32 b` | accept; 0013-0023 exactly that | **HIT** |
| P2 | E48C2 | accept; auto-member store 18 bytes `21 *D(rec) / EB / 21 *S / 3E 03 / ?SCVCM / D6 01 / 9F / 32 b` | accept; 0013-0024 exactly that | **HIT** |
| P3 | E48C3 | accept; unqualified spelling byte-identical to P2 | accept; store 0013-0024 identical bytes; whole file differs at exactly 3
     offsets (6, 19, 28) — the module-name bytes (`2' vs `3'); every
     CODE/DATA/RELOC record byte identical | **HIT** |
| P4 | E48C4 | accept; `3A/B7/FA <chain>` head, member store 18 bytes INSIDE the loop, `n = 4` ladder as E48A12 | accept; head 000C-0012; store 0027-0038 18 bytes; ladder 0039-0048 = `LHLD n / LXI B,FFFC / DAD B / MOV A,H / ORA L / C2 004A / LXI H,*D(0000) / MVI M,80`; back edge `C3 000C` at 004A | **HIT** |
| P5 | E48C5 | accept; SCCVM store `21 *D(name) / 11 *S / 06 03 / ?SCCVM / D6 01 / 9F / 32 b`, labelled **16 bytes** | accept; 0013-0023 exactly that SEQUENCE, total **17 bytes** | **HIT on sequence; MISS on the size label** — my arithmetic slip: 3+3+2+3+2+1+3 = 17, not 16 (the tail `D6 01 / 9F / 32 X` is 6 bytes, I summed 5). Kept as written per PROTOCOL #2. |
| P6 | E48C6 | accept; member literal-left, NO XCHG, labelled 16 bytes | accept; 0013-0023 = `21 *D(rec) / 11 *S / 06 03 / ?SCCVM / D6 01 / 9F / 32 b`, **17 bytes**, no XCHG | **HIT on sequence; same size-label MISS** |
| P7 | E48C7 | accept; statics FIRST and adjacent in declaration order (`s`@0 `41 42 20`, `b`@3), pool above, `rec` AUTOMATIC above the pool; store = 18-byte member form | accept; DATA `41 42 20` @0000, `00` @0003, pool `41 42`@0004 `45 4F 46`@0006 `53 3D`@0009 `42 3D`@000B, `rec` auto @000D; DEF-DATA-SIZE 002C = 13 + 31; store 0013-0024 = the 18-byte form, `STA *D(0003)` | **HIT** — my binder's level-0 leak is confirmed `my-gap` (see §4) |
| P8 | E48C8 | accept; cell below the pool ([len][chars] layout [TBD]); store predicted flat 17-byte form | accept; `nm` cell at *D(0001) = **15 bytes `02 41 42 20 ×12`** — a 1-BYTE LENGTH CELL followed by the DECLARED EXTENT blank-padded, IN PLACE, NOT pooled; DEF-DATA-SIZE 0015 = 1+15 static + 3+2 pool; store 0006-0016 = flat 17-byte SCVCM form with `LXI D,*D(0001)`; `put list(nm)` = `LXI H,*D(0001) / ?SLVTS` | **HIT** (the [TBD] layout now measured) |
| P9 | E48C9 | accept; test head `21 *D(rec) / EB / 21 *S / 3E 03 / ?SCVCM / C2 <chain>`; skip to next statement; then-body `21 *D(b) / 36 80` | accept; head 0013-001E (15 bytes incl. the `C2 00 00` + fill); fill = `SET-LC/RELOC code 0020 <- 0027` = the NEXT STATEMENT (0027, the `?SYSPR` prologue) — the no-else-IF rule of [C309]; body 0022-0025 = `LXI H,*D(0000) / MVI M,80` | **HIT** |
| G1 | all | 9 accepts | 9 ok / 9, all produced `.REL` | **HIT** |
| G2 | layout | [statics][pool][automatics]; adjacency; dedup; auto-member in-place ([C114]/[C314]/E46J21) | held in all four layout-bearing goldens (C7, C8 new) | **HIT** |

**The discriminator question is ANSWERED:** it is the **operand class** — a
VARYING that is an internal record MEMBER (whether spelled qualified or
unqualified, whether in a straight-line body or inside a `DO WHILE`) materializes
its address in HL and parks it with `XCHG` (18 bytes); a FLAT cell — automatic
(E48A6) or static (E48C8) — gets `LXI H,<lit> / LXI D,<var>` (17 bytes). CREATE
008F's 18-byte spelling is now a measured rule, not an anomaly. [C310]'s
`[TBD]` on the discriminator is superseded by §2 law 1; the other [TBD] items of
C310 (|c| in 1..3, `'0'b` as a value, `^(cond)` beyond `^(k = 0)`, nested `&`)
were NOT varied by this bank and stay [TBD].

## §2 Measured DR laws of this bank

1. **SCVCM store, member class — 18 bytes.** `21 *D(member) / EB / 21 *S(lit) /
   3E len / CD ?SCVCM / D6 01 / 9F / 32 *D(bit)`. Sites: E48C2 0013, E48C3 0013,
   E48C4 0027, E48C7 0013 — four objects, all identical bytes; plus CREATE 008F.
   The member cell is addressed IMMEDIATELY (`LXI H,*D`, E46J21's rule); the XCHG
   is [C191]'s load-order law, now proven to apply in STORE position too.
2. **SCVCM store, flat class — 17 bytes** — unchanged from [C310], now covering
   STATIC flat cells too (E48C8 0006: DE = the static descriptor cell address).
3. **SCCVM store (literal-left orientation) — 17 bytes.** `21 *D(var) / 11
   *S(lit) / 06 len / CD ?SCCVM / D6 01 / 9F / 32 *D(bit)`. Length in **B**;
   HL = the RIGHT operand (the variable), DE = the LEFT (literal) — [C191]'s
   register law verbatim in a store; the member side needs NO XCHG (E48C6).
   [C095]'s flag trick `D6 01 / 9F` carries over from SCVCM to SCCVM unchanged
   (the extrapolation in P5/P6 held except my size label).
4. **TEST position, internal automatic member — 15-byte head.** `21 *D(rec) / EB
   / 21 *S / 3E len / CD ?SCVCM / C2 00 00 <chain>`; `=` skips with C2 [C191],
   the no-else skip target is the next statement [C309]. E48C9 0013.
5. **STATIC on CHARACTER VARYING is a 1+len cell IN PLACE below the pool.**
   `dcl nm char(14) varying static initial('AB')` → DATA `02 41 42 20×12` at the
   static address: the initialiser's LENGTH byte plus the DECLARED EXTENT
   blank-padded; the literal is NOT pooled and NOT deduped; `DEF-DATA-SIZE`
   counts all 15. Reads go through the ordinary descriptor routes (`?SLVTS` in
   PUT, `LXI D,*D(cell)` in SCVCM). This is E48B6's fixed-char law extended by
   the leading length byte. (E48C8 0001; DEF-DATA-SIZE 0015.)
6. **A flat STATIC does not contaminate a later AUTOMATIC structure.** Statics
   occupy DATA 0.. in declaration order (`s`@0000, `b`@0003), the pool follows
   (0004..000C), and `rec` is AUTOMATIC above the pool at 000D; DEF-DATA-SIZE
   44 = 13 + 31. Manual 6.2 as cited by [C242] is about STRUCTURE levels; a
   level-0 declaration is not a parent. (E48C7 DATA records.)

## §3 What this bank does NOT measure

* A **based** member's condition-STORE (P2/P6 spell the internal record only;
  the `LHLD ptr / step / XCHG` TEST spelling exists in E29C4, but its store
  twin has no golden) — stays [TBD], `bit_cond_mat` must keep refusing it.
* An internal member as the RIGHT operand in TEST position; `^(cond)` in a
  store; `k = c` with |c| in {1,2,3}; `'0'b` as a materialised value; nested `&`
  beyond E48A14; a non-final bit PUT item; a store INTO a static CHARACTER
  (VARYING or fixed) — all unchanged [TBD].
* `OPEN ... TITLE(<static varying>)`: E46F5's exact question. This bank puts
  the static varying cell in PUT and in a compare, never in a TITLE — E46F5
  must keep refusing (see §5).

## §4 My defect exposed by this bank (measured, `my-gap`)

`dcl_static_dcls` (codegen.ml:12070) pushes EVERY declaration onto the
storage-class inheritance chain, including level-0 flat ones, and pops only
entries at `level >= lvl`, so a flat `dcl s char(3) static;` remains the
"enclosing" parent of every later `dcl 1 rec,...` in the same block: the whole
record silently inherits STATIC. Scratch proof at `1595a10` (before any oracle
call): record-first compiles, static-first refuses `STATIC on CHAR(30) VARYING
MEMBER OF REC@0 is unsampled` — and the census rows for CREATE (record via
`%include` first, UNAFFECTED) and MPMCALLB (`upper/lower ... static` at 48-50,
automatic `1 cpb` at 166, blocked at `STATIC on POINTER MEMBER OF CPB@390`)
confirm it bites real sources. E48C7 §2.6 is the oracle arbitration: DR places
such a record in the AUTOMATIC area. Classification **my-gap**; fix: level-0
declarations compute their own effective class but never enter the chain
(a level-0 entry already pops the whole chain).

## §5 Consequences recorded with this round

* CREATE's 18-byte store is a MEASURED rule (§2.1) — CREATE's remaining
  blocker stays the front-end `%include` gap ([proposed] in `LEARNINGS.md`);
  this round does not touch it.
* The gate rows pinning `STATIC on CHAR(14) VARYING is unsampled` (E46F5) and
  the FIXED-BINARY(15,0) row are refusal-text rows: implementing law §2.5
  moves E46F5 forward to its `OPEN ... TITLE(nm)` statement, which stays
  unmeasured, so the refusal must persist there with the pinned text or the
  row is re-measured and updated explicitly — never silently.
* EXPR2/FSCAN/LOAN2/REPORT/MPMCALLB census rows re-measured after the §4 fix
  and the §2.5 placement; progress recorded via `tools/corpus_census.py
  --check`, counts verified identical.
