# E2E-52/P1 — HYPOTHESES (committed BEFORE the oracle call; PROTOCOL pre-registration)

Cell sizes used in every prediction: DEC cell bytes = ceil((p+1)/2) — dec(4,2)=3,
dec(7,2)=4, dec(9,2)=5, dec(10,2)=6 [R507, LOAN1]; plain `fixed bin` = a 2-byte cell;
a bare-literal store into a DEC target allocates ONE target-precision pool cell keyed
by the packed byte image [C178]; a compare literal is sized by the DEC partner
[R507/R607]; an ADD/SUB literal aligns to its partner [R608]. DR lays pool blocks in
SOURCE order ahead of the variable cells (R507: pool 3.00, pool 0.00, then d).

## Competing models for how DR types a name at prescan/pool time across scopes

- **H1-lexical** (the fix direction): every statement resolves its target through the
  INNERMOST enclosing declaration of that name, exactly as lowering already does
  (`st.vars` inner-first accumulation, [C187] N6 distinct cells); pool demand is the
  union of per-scope-typed literal cells, deduped BY IMAGE program-wide (one shared pool).
- **H2-own-only**: a prescan that sees only each procedures OWN rows — outer variables
  invisible inside procedures. Already contradicted in principle by every historical
  program (LOAN2 reads/writes outer vars inside procs), but it is the failure mode my
  OWN fix must not introduce — E52E tests it (via my post-fix object, not DR).
- **H3-global-outer**: ONE flat type map where the OUTER declaration wins for a shadowed
  name (this is the ORDER my current map has — top rows are prepended last, so assoc
  finds them first — minus the clash refusal). Under H3 an inner DEC store is typed at
  the OUTERS precision (or skipped as binary), changing pool bytes and/or CODE bytes.
- **H4-per-scope-pool**: pool cells dedup only WITHIN a scope — same name (E52A) or same
  image under different names (E52F) typed identically in two scopes yields TWO cells.
  (My current implementation shares `cx.pd_img` across the whole walk — H1/H3 dedup.)

Acceptance prediction: DR ACCEPTS all ten rows.  Grounds: the LOAN2 golden proves the
conflicting-kind shape accepted by the real compiler; [C187] N6 (distinct cells) and
REVERSE/NETWORK historical nested-homonym programs are settled controls.  A DR refusal of
any row would itself be a first-class result (and would falsify the H1 fix direction for
that shape); [C193](a)s DUPLIC experience is recorded as a generator defect, and
[C186](a)s lesson is honored by these two independent positive controls.

## Per-row predictions (pool bytes; DATA total = pool + declared cells; CODE where stated)

| row | shape (one difference) | mine TODAY (BASELINE-MINE) | H1 pool | rival prediction | discriminator |
|------|------------------------|----------------------------|---------|-------------------|----------------|
| E52A | homonym, same type, both `i = 3` | rc=0, 256 B, sha 8217250a | 3 (dedup) | H4: 6 | DATA total 9 (H1/H3) vs 12 (H4); vars 3+3 |
| E52B | outer dec(4,2) / inner dec(9,2), both `i = 3` | rc=2 conflicting kinds | 8 (3+5) | H3: 3 (both stores outer-typed, one image) | DATA 16 (H1/H4) vs 11 (H3); LINK-DEF-DATA-SIZE |
| E52C | DEC outer / `i fixed bin` inner | rc=2 conflicting kinds | 3 (outer only) | H3: pool 3 TOO — but inner store takes LXI H,*S + DLDOP + ?DSTOP | CODE ONLY: H1 inner store is `LXI H,0003 / SHLD` (immediate, [C178] bin-literal path); H3 is the DEC helper route |
| E52D | `i fixed bin` outer / dec(7,2) inner | rc=2 conflicting kinds | 4 (inner cell) | H3: 0 (inner store typed binary) | DATA 10 vs 6; LINK-DEF-DATA-SIZE |
| E52E | inner writes NON-shadowed outer `o dec(9,2)` | rc=0, 256 B, sha 4fe89c7d | 5 | H2: 0 (cell missed, later addresses shift) | DR expected DATA 10; H2 is an invariant test on MY post-fix object, not a DR model |
| E52F | different names `a`/`b`, same type, same image | rc=0, 256 B, sha 8c09f2e7 | 3 (dedup) | H4: 6 | DATA 9 vs 12 |
| E52G | formal shadow (LOAN2 current_year): formal `i dec(9,2)` + literal store; outer `i dec(4,2)` | rc=2 conflicting kinds | 8 (3 outer + 5 formal-target) | H3: 3 | DATA (H1 approx 16; formal-cell WIDTH on DR is itself an open measurement — do NOT fit to it, report it); the S2 design check (BASELINE-MINE appendix) proves the literal-to-formal path exists, so only the NAME clash blocks this row today |
| E52H | 3 scopes: innermost store resolves THROUGH mid `x dec(9,2)` | rc=2 conflicting kinds | 8 | own+main env: ALSO 8 (dedups onto mains 3-byte cell) | CODE/reloc: which *S operand the innermost `LXI H` loads (the 5-B mid image vs the 3-B main image) and the DLDOP width byte |
| E52I | 3 scopes: innermost TEST `x > 0` + store `x = 1` through mid dec(9,2) | rc=2 conflicting kinds | 13 (3 + 5 + 5) | main-env sizing: 9 (3 + 3 + 3) | DATA 21 vs 17 — direct prescan_consumer discriminator |
| E52J | NO shadow; proc-local do-while DEC compare + aligned store | rc=0, 384 B, sha 0a3f6b6a | 15 + 5 = DATA 20 | (control — pins the existing path) | my post-fix object MUST stay byte-identical to today (sha 0a3f6b6a...); DR golden ties the law |

## Falsification conditions (each is a FIRST-CLASS result)

1. Any DR refusal (rc/PRN error) — falsifies this banks acceptance premise for that
   shape; classify `dr-refuses`, keep the .PRN verbatim, and do NOT implement it.
2. DATA total matching a rival column rather than H1 — falsifies H1 for that shape.
3. Whole-file byte comparison of my CURRENT objects (A/E/F/J) against DR goldens failing
   — falsifies some background law this bank reuses (dedup, cell sizes or pool order);
   record it, do not adjust the model to fit.
4. After the lexical-prescan implementation: any E52 object not whole-file byte-exact,
   or E52J/E51-sweep regression, falsifies the fix direction (mirroring lower_procs
   accumulation) — the round then stops at evidence + a corrected PROPOSAL, and LOAN2
   stays refused-by-name rather than guessed past.

## Explicitly NOT claimed before measurement

- That DR dedups literal cells ACROSS scopes (A/F measure it; the S1/S2 scratch objects
  only prove MY current compiler does).
- The WIDTH of DRs formal-parameter DEC cell in this shape (G reports it; S2 is
  my-compiler-only evidence).
- Whether ns (E52H) `LXI H` operand is main- or mid-sized (CODE decides).
- Anything about LOAN2 beyond its blocker message and its golden existing.
