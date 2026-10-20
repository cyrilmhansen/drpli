# Gap ranking and the next corpus milestone — after the DR verdict pass

Date: 2026-08-03 (session 14, post-`4f8c3cc`). Inputs: `tools/neg_triage.py`
(generates the cost table from DR's `golden/negpanel1` listings plus the
authoritative emitted-routine set), `tools/blocker_audit.py` (AST blocker sets),
the corpus sweep at **12/41**, gate **390/390**, panel **65/65**.

Repository verified first: `git push origin main` took `83a89f2..a7f56de` — nine
commits, i.e. this session's three plus the six unpushed predecessors from steps
3a–3e (they are contiguous ancestors, so "the three" cannot go up without them).
Sweep re-run after the taxonomy commit: unchanged, 12/41 EXACT, 0 DIFFERS.

## 1. 54 specimens are not 54 features

Clustering the 54 `my-gap` negatives by the lowering dependency their refusal
marker names gives **21 families**. The biggest single family (ROUND, 7
specimens) is one routine plus a few argument-shape rules, and it appears in
**zero** closable corpus programs. Conversely, the single most valuable route
found today (`A`) came from a program the AST audit scores as needing *nothing*.

Cost table (generated; `code` = DR's own CODE SIZE for the specimen, `calls` =
CALL instructions DR emitted, `reloc` = reloc-bearing operands in the listing):

| family | specimens | DR code sizes | new RTL needed | my read of the feature |
|---|---|---|---|---|
| bit-copy | 2 | 000F–000F | none | 1 rule (byte-width copy form) |
| static-initial | 1 | 0010–0010 | none | 1 rule (STATIC+INITIAL on FIXED BIN) |
| float-precision | 1 | 0014–0014 | none | possibly permanent: BINARY(14) may be DR-fixed-precision-24-only |
| mul-idioms | 3 | 0015–001B | none | 1 rule (strength-reduction / operand commutation) |
| add-literal-pair | 1 | 0022–0022 | none | 1 rule (literal-pair fold vs runtime add) |
| dec-literal | 2 | 0019–0023 | none | 1 rule (literal scale into scale-0 / mixed DEC-int) |
| forward-labels | 1 | 0026–0026 | none | 1 rule (multi forward label) |
| condition-forms | 2 | 0029–002A | none | 1 rule (non-zero-condition forms) |
| str-store | 3 | 0015–002C | none | 2 rules (fixed-char store form, varying store) |
| concat | 3 | 0028–004B | none | 1 route (`?PNCOP`/`?GNVOP` operand kinds) |
| dec-store-scale | 1 | 004C–004C | none | 1 rule (store scale drift) |
| dec-compare | 2 | 004D–0056 | none | 1 rule (compare literal scale encoding) |
| dec-divide | 3 | 005C–0077 | none | 2 rules (dividend form, negative scale) |
| do-shapes | 5 | 002C–007D | none | 3 rules (WHILE/REPEAT combos, bound<1, step>2) |
| dec-formal | 3 | 0047–0084 | none | 1 route (DEC formal cells + their modes) |
| float-to-fixed | 1 | 0020–0020 | **?QFI15** | 1 routine + 1 rule (also closes E29B/E29E) |
| put-options | 4 | 0023–003C | **?PAGOP** | 2–3 rules (PAGE, SKIP n, generated/counted items) |
| on-handler | 2 | 0032–003D | **?RECOV** | 1 route + non-local control (handler begin-block) |
| round | 7 | 0023–0063 | **?IROUN** | 2 rules (arg shape; nested-in-arithmetic) |
| float-coercion | 5 | 0027–0072 | **?NSTOP** | 2 rules (arg/formal coercion, recursive prologue copy) |
| get-targets | 2 | 002F–003A | **?QDI07, ?SSCFS** | 2 routines (fixed-char GET store, 1-byte target) |

**47 of 54 need no runtime routine my build has never emitted.** Seven need
exactly one new routine apiece, and no two of those seven share it. So the whole
panel is ~21 features, of which 16 are pure lowering.

### How the cost signal was derived, and the correction it needed

`neg_triage.py` compares each specimen's DR routine set against the routines
**this build has actually emitted**, taken from the symbol fields of my own
`.REL` output across all 390 gate specimens (75 distinct names). Two earlier
versions were wrong in opposite directions and both are worth recording:

- grepping `call_ext st "?NAME"` missed `?START`/`?STOPX` (pushed as chain items
  from `emit_program`) and reported **all 54** gaps as needing new runtime;
- grepping any `"?NAME"` string literal in `codegen.ml` still counted names that
  appear only inside a **refusal message** — a routine I have never emitted but
  have written about.

The corrected set moved `?PNVOP`, `?FA44M`, `?FM44R`, `?DADOP`, `?DMUOP` from
"new runtime" to "already emitted", collapsing 9 gap-routines to 7 and, more
importantly, revealing that **the routine corpus program `A` needs is already in
my output** (see §3). Same lesson as C134 in a different costume: a capability
question answered by a proxy signal has to be checked against the artifact the
claim is really about.

## 2. Payoff: the panel and the corpus measure different things

Cross-referencing the audit's per-program blocker labels against the 21 families:

- **Zero-payoff families** (no corpus program is closable by them): ROUND (7
  specimens!), bit-copy, static-initial, mul-idioms, add-literal-pair,
  dec-literal, forward-labels, condition-forms, dec-store-scale, dec-compare.
  They close no program because those programs' *other* blockers dominate —
  e.g. LOAN2 mentions ROUND but also needs 13 other routes.
- **Families with real payoff**: `put-options` (PUT generated/counted items +
  `options(stack)` map onto ACK and ACKTST, whose complete blocker sets are
  exactly 2 items each), `float-to-fixed` (via `A`), `do-shapes` and `concat`
  (component features of larger programs, no single closure).
- **Corpus blockers with NO panel coverage**: `STRUCTURE_LEVEL` (11 programs),
  `ARRAY_DIM` (9), `BIT_NOT_PREFIX` (8), `FILE_STMT`/`IO_OPT` (10),
  `BASED_ATTR`/`POINTER_DECL`/`ALLOCATE`/`FREE`, `QUALIFIED_REF`,
  `PREPROC_IN_DCL`, `LABEL_AS_DATA`, and most `BUILTIN:*` (exp, log, ceil,
  translate, index, length, addr, divide, summary, ascii, char, pageno). The
  panel was built from construct *perimeters* during slices, so it is dense
  where my probes were dense and empty where I never probed.

So the panel is a good **cost** instrument and a poor **payoff** instrument. Any
ranking that reads only the panel will buy 7 ROUND specimens and close nothing.

## 3. Route-level gaps the AST audit misses — with proof

The audit's blocker sets are only as complete as the detector that wrote them:
its label vocabulary is a closed list of constructs I chose to look for, so "0
blockers" means "nothing my scanner knows about", not "nothing required".

**Case A — the audit's blind spot and my compiler's, in one program.** `A` is
scored 0 blockers, is not in my accepted list, and DR compiles it as 21 bytes:

```
a: procedure(x) returns (float);   CODE SIZE 0015  DATA AREA 0006
  dcl x float;                     CALL ?FD44M   <- float / FIXED divisor
  return (x/2);                    CALL ?FPRET   <- float return
```

My refusal says *"FLOAT value used where a FIXED value is expected — the
float-to-fixed route ?FL40M/?QFI15 appears only inside FFACT's prologue"*. Two
errors in that one sentence: DR uses **`?FD44M`**, not `?FL40M`/`?QFI15`; and no
`.REL` I have byte-matched (mine or DR's FFACT) contains `?QFI15` at all, so the
"appears inside FFACT's prologue" premise is false as stated. `?FD44M` is
something this build **already emits** (R3033, byte-exact). Conclusion: the
cheapest remaining corpus acceptance, diagnosed wrongly by my own refusal message
and invisibly to the blocker audit — and the only authority that settled it was
DR's listing for the program itself.

**Case REVERT — a predicted second route.** `REVERT` is scored 1 blocker
(`LABEL_AS_DATA`: `call p(i, exit)` passes a label as an actual). But its source
also contains `on endfile(sysin) goto lab;` — a GOTO out of an ON handler, which
C121 established needs DR's `?RECOV` label prologue. The audit's vocabulary has
no label for that, so REVERT is priced at 1 route where it plausibly needs 2.
This is a **prediction, not a measurement**: it can only be settled by lowering
label-as-data first and seeing what my compiler hits next, so REVERT should not
be scheduled on the strength of the audit's "1".

**Other route-level gaps no AST scan will ever show:**
- **External assembly modules.** DTEST/FDTEST are accepted only because RMAC
  output exists in `artefacts/`. Nothing in the AST says "this program needs a
  companion module from another toolchain".
- **Layout/demand interactions.** C134 (base computed before a cell was demanded)
  is invisible to both AST scanning and RTL-usage counting; it is a property of
  my own pass ordering.
- **CP/M constraints** (8.3 names, CRLF + `^Z`, `^Z`+CR console EOF) — toolchain,
  not language; they have cost me runs several times, most recently
  `SAFETY: illegal CP/M name 'N36_ROUND_ONEARG'` when exporting the panel.
- **Refusal-message rot.** Messages assert facts about DR ("DR rejects…", "no
  sample shows…"). Nine retired negatives prove they drift. Cheap fix: have the
  audit record each program's **first refusal reason from my compiler** alongside
  the AST blocker set — `A`'s row would then have named the route immediately,
  and the reason would be re-derived every run instead of remembered.

## 4. Recommendation: the next corpus acceptance is `A`

Ranked on cost, dependency depth, and payoff — with the evidence above:

1. **`A` — mixed-mode FLOAT÷FIXED in a FLOAT-returning procedure with no main
   entry.** 21 bytes of code, 6 bytes of data; DR's full listing in hand; and
   both routines it needs are already inside accepted, byte-exact goldens —
   `?FD44M` appears in 4 of them (R3003, R3033, R3042, R3088) and `?FPRET` in 25
   (FFACT and the R3079+ float series).  `?QFI15`, which my refusal message for
   `A` claimed was the route, appears in none. Expected work: replace one refusal arm with an existing
   route, plus whatever the no-`main` procedure-only shape needs (that part is
   unprobed — the honest uncertainty in this estimate).
   **Acceptance beyond byte-parity**, and this is the part worth doing: `A` is
   declared an *external* procedure, so it can be linked against a caller. Write
   a probe `E29F` that calls `a` via the step-4 external-ENTRY machinery, compile
   **both** modules with my compiler, link, and run. That would be the first
   end-to-end program in this project assembled entirely from my own output — no
   RMAC module, no DR object file in the link — which is a capability milestone
   independent of the corpus count.
2. **`?QFI15` float→fixed (`N61`, `E29B`, `E29E`)** — one new routine, three
   pinned specimens, and it is the *correct* version of the conversion my `A`
   message mistakenly invoked. Second because its corpus payoff is also nonzero
   (mixed-mode arithmetic is ubiquitous), but it needs runtime-ABI discovery that
   `A` does not.
3. **`put-options` (ACK, ACKTST — 2 programs, 2 routes each)** — highest real
   program payoff among the small-blocker targets, but `?PAGOP` plus
   counted/generated item semantics is a route, not a rule, and it is the same
   route family that the 8-program `PUT_ITEM` group depends on. Right
   long-term target, wrong next step.
4. **`round` (7 specimens, 1 routine `?IROUN`)** — the cheapest way to *inflate
   the panel*, and the second-cheapest way to accomplish nothing for the corpus.
   Explicitly de-prioritized.

Rejected as next milestones: `REVERT` (predicted 2 routes, second one is
non-local control flow), anything in the file/IO group (10 programs, all with 6+
blockers), and the DEC families (large specimens, up to 0084 code bytes, and no
program closes on them).

## 5. What I would change in the instruments (not doing it to production code)

- `blocker_audit.py`: add a `first refusal (my compiler)` column, captured by
  actually compiling each corpus program. This converts it from a vocabulary-bound
  scan into an empirical one and would have surfaced `A` in step 3.
- `neg_triage.py`: emit the family column mechanically instead of my hand map,
  once families are declared somewhere queryable (§ ARCH-0 §10 table).
- Every refusal message that makes a claim about DR should cite the artifact that
  established it (a `.PRN` path), so stale claims are detectable by `grep` when
  the artifact is checked. `A`'s message cited FFACT's prologue and was wrong;
  a path would have been checkable in one command.
