# f6 probe battery design (F0xx) — question / expectation / output cap

## Background census from existing goldens (store node f6)
| src | expr | dest type | last op | store f6 |
|-----|------|-----------|---------|----------|
| P071A L4 | a+b-1 | bin | ISU | 00 |
| P071B L3 | a*b/3 | bin | IDV | 00 |
| P071B L4 | mod(a,b) | bin | IMD | 05 |
| P071D | 2**3 | bin | QDI(after DEX) | 03 |
| P071F L3 | d->z | bin | QDI | 00 |
| P071C L3 | p+q | dec | DAD | 28 |
| P071C L4 | p*q-1.5 | dec | QDD | 21 |
| P072D L1 | d/e | dec | QDD | 00 |
| P072D L2 | d*10.0 | dec | QDD | 05 |
| P071F L4 | x->d | dec | QCD | 00 |
| P071F L6 | z->d | dec | QDD | 00 |
| P071E | x*y+1.5e0 | flt | FAD | 00 |
| P072E L1 | x/y | flt | FDV | 28 |
| P072E L2 | x-y | flt | FSU | 00 |
| P071F L5 | z->x | flt | QIF | 21 |
| P072A | 5 if-stores | bit | BLD | 00/00/01/00/00 |

Neither dest type, nor source type, nor operator alone predicts f6
(FDV=28 vs FSU=00 with identical types; DAD=28 vs DSU-shape=21/05).

## Hypotheses to discriminate
- H1  f6 = semantic (type/conversion driven)            -> stable across shape
- H2  f6 = temp/scratch slot allocator (needs-temp)     -> varies with expr shape
- H3  f6 = node-chain LINK / arena pointer (opaque id)  -> varies with position,
        repeats of the SAME statement give DIFFERENT f6
- H4  f6 = "assigned/previously-read variable" flag     -> the observed 28 pattern

## Probes (one statement each unless stated; $V$L switches)
| probe | program | asks |
|-------|---------|------|
| F001 | f=x/y (float div) | reproduce 28 baseline |
| F002 | f=x*y (float mul) | is * different from / ? |
| F003 | f=x+y (float add, no pool) | add vs sub vs div |
| F004 | f=x-y (float sub) | 00 baseline |
| F005 | z=a/b (int div) | int div vs float div |
| F006 | z=a*b (int mul) | |
| F007 | d=p-q (dec sub) | dec sub vs dec add |
| F008 | d=p+q (dec add) | confirm 28 |
| F009 | d=p*q (dec mul) | |
| F010 | z=a MOD b vs F011 z=a/b  (control for 05) | confirm op-linked 05 |
| **F012 KILLER** | `f=x/y; f=x/y;` two IDENTICAL statements | H3: positional => 2nd differs |
| F013 | `f=x/y; f=x*y; f=x/y;` | H3: same op, different slot |
| F014 | `d=p+q; d=p+q;` identical dec-add twice | H3/H4 |

## Expected discriminating outcomes
- If H3 (opaque/positional): F012's two identical statements show DIFFERENT f6;
  and F013's first and third (same op) differ. => conclude f6 is NOT semantically
  reproducible; keep it as an explicit opaque field, never force it.
- If H1/H2 (op/shape): F012 both statements identical f6; F001..F011 stable per
  operator/type. => derive the rule table.

## Output cap
14 probes x ~8 $V lines = ~112 lines; transcript grep restricted to
store/load lines only (< 60 lines inspected). ONE cpmsim session
(batch-size >= 14) -> bounded, ~4 min.

## RESULTS (f6probe + f6probe/G battery, 18 probes, 1 session)

### Store / conversion / arith f6 is OPAQUE (not source-semantic)
- F012 `f=x/y; f=x/y;` (identical statements): store f6 = **28 then 00**.
  Identical source types/op/dest -> different f6. Kills H1 (type-driven).
- F013 `f=x/y; f=x*y; f=x/y;`: store f6 = **28 / 00 / 31**. Same op (/) at
  two positions gives 28 vs 31. Position-dependent -> supports H3.
- G-series (identical final store `f=x/y`, vary PRECEDING statements):
  G001 (0 prior stmts)=**28**, G002 (1)=**00**, G003 (3)=**97**,
  G004 (0 prior, many decls)=**28**. Same dest addr A(0008) every time,
  so f6 is NOT the dest address; it tracks prior emitted nodes (arena /
  temp-pointer link). Non-monotonic (28,00,97) so not a simple offset.
- F014 dec `d=p+q; d=p+q;` = 28 then 00 (same as F012 float) -> not type.
- F015 `f=x+y; g=x+y;` = 28 then 00 -> first-store-per-VAR is FALSE (g's
  first store is 00), so it is procedure-position, not per-variable.

CONCLUSION: f6 on STORE nodes and on conversion/arith OP nodes is a
compiler-internal link/allocator field that does NOT reduce to
{source type, dest type, operator, conversion, expression context}.
Byte-parity of that field cannot be produced from a source-level IR
without emulating DR's node allocator. We do NOT model it; we leave the
value at the honest default 00 and expose it as an explicit known gap
(gate reports structure-exact separately from byte-exact).
Removed prior speculative guess "DEC store f6=28" (refuted: P072D dec
store=00, P071F dec store=00).

### READ-node f6=0x28 IS semantic (proven, 90/90)
A variable *READ* address node (IID/DID/FID/CID/BID on `NAME A(off)`)
carries f6=0x28 iff that variable has been the target of an earlier
STORE in the same procedure (reaching definition, reset at BEG); else 00.
Verified 90/90 across probe38+probe40+f6probe. This is the ONE solid f6
rule and is what makes P071A / P071E byte-exact.
Pool-constant address nodes: DEC `* S(off)` DID f6=00; FLOAT FID f6=28
(P071C/P071D vs P071E) - modelled as observed, low sample, flagged [obs].

### Conversion op chains (assignment RHS-type -> dest-type)
| src->dst | sequence (after the src load node) | source |
|----------|----------------------------------|--------|
| dec(p,s)->bin | QDD(p,0) ; QDI(15,0)                    | P071F L3 |
| float->dec(p,s)| QFC(14,0) ; QCD(15,s)                   | P071F L4 |
| bin->float     | QIF(15,0)                               | P071F L5 |
| bin->dec(p,s)  | QFD(? ,0) ; QDD(? ,s)  [precision rule TBD] | P071F L6 |
Dec DIVIDE rescale (P072D L3): operand DLD(9,2) then QDD(9,8) [widen scale
to p-1=8] ; DDV result (15,6) ; QDD(15,2) [narrow] ; DAS. Dec MUL literal
(P072D L4): pool '10.0'->DLD(3,1) natural; DMU(13,3); QDD(13,2).
