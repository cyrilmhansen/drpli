# Negative-panel taxonomy — what 65 refusals actually prove

Date: 2026-08-03 (session 14, E2E-11 step 4). Produced by the DR verdict pass
`golden/negpanel1`. Tooling: `tools/mk_neg_panel.py` (exports every `REJECTS`
source verbatim as `negsrc/NGxx.PLI`, CRLF + `^Z`, 8.3-safe names) followed by
`PLI_SRC=negsrc python3 oracle/batch.py --all --tag negpanel1 --switches '$L$C$D'`.

## 1. The question the panel never answered

`run_negatives()` proves one thing: my compiler refuses with `[TBD]`. That is
trivially true of any refusal I wrote. It says nothing about DR, and the panel
therefore conflated two facts with opposite meanings:

- **DR refuses** — a language rule. The refusal is evidence about PL/I-80.
- **DR compiles it** — a gap in my build. The refusal is evidence about *me*.

Nine times now the second category has been recorded as the first: N56, N63, N64,
N65, N66, N77, N54, N55, and this session's N84. Each was discovered by asking
DR, never by reading my own annotation. So the panel got a metadata column,
generated from DR's transcripts rather than transcribed by hand, and the gate now
fails on any negative that lacks one.

## 2. The split

| | count | meaning |
|---|---|---|
| `dr-refuses` | **11** | DR's own compiler rejects the source. The panel's real semantic evidence. |
| `my-gap` | **54** | DR compiles the source and emits a `.REL`; only my build refuses. |

**54 of 65 are conservatism, not perimeter.** The panel is mostly a to-do list
wearing the costume of a boundary. Each of those 54 now has a DR `.REL` sitting in
`golden/negpanel1/NGxx/`, so 54 byte-exact acceptance targets exist that I did not
have to design, price, or generate — this is the cheapest backlog in the project.
The 11 genuine refusals are correspondingly *more* valuable, because each one now
carries DR's verbatim diagnostic.

### The 11 DR refusals, with DR's words

| negative | DR's diagnostic | pass | source line DR objected to |
|---|---|---|---|
| N6_COMPUTED_GOTO | `ARG COUNT` | 2 | `goto l(i);` |
| N24_BIGIN | `NOT IMP` | 1 | large FIXED BINARY precision |
| N27_DECBIGP | `NOT IMP` | 1 | FIXED DEC precision beyond the ceiling |
| N36_ROUND_ONEARG | `SYNTAX` | 2 | `y = round(a);` — one-argument ROUND |
| N45_GETSUB | `ARG COUNT` | 2 | `get list(x(1));` — substring as GET item |
| N72_FIXED_BIN_GT15 | `NOT IMP` | 1 | FIXED BINARY(p) with p > 15 |
| N73_FIXED_DEC_GT15 | `NOT IMP` | 1 | FIXED DEC(p,s) with p > 15 |
| N78_INITIAL_WITHOUT_STATIC | `NOT STATIC` | 2 | `INITIAL` on a non-STATIC bit string |
| N81_CALL_OF_VALUE_RETURNING | `NOT PROC` | 2 | `call acc(s);` on a RETURNS procedure |
| N82_CALL_OF_FLOAT_RETURNING | `NOT PROC`, `SCALE>0` | 2 | CALL of a FLOAT-returning procedure |
| N83_EXPR_OF_NO_RETURNS | `TYPES NOT=` | 2 | `x = p;` where p has no RETURNS |

Three of these confirm claims already in CLAIMS.md verbatim (C114 `NOT STATIC`,
C122 `NOT PROC` / `TYPES NOT=`, C108 the p > 15 ceiling) — the pass therefore also
independently re-validates three claims. Two are new wording: DR reports a computed
GOTO and a GET substring item as `ARG COUNT`, which is a parse-shape complaint, not a
"not implemented" one — worth remembering because `NOT IMP` and `ARG COUNT` point at
different subsystems, and a future probe that expects one and gets the other is
telling me something.

## 3. Annotation audit

I scanned every `REJECTS` comment for claims that DR rejects, and cross-checked each
against that negative's DR verdict. One hit, and it was already a correction ("all
four were compiled by DR itself", N74-N77). So the three mislabels fixed in earlier
sessions (N37 relabeled as a capability gap, N55 reworded, N54/N55/N84 retired) were
the full set of stale text, and nothing in the panel still asserts a DR rule that DR
does not enforce.

## 4. Rules adopted

1. A negative records `category` and DR's verdict. Unclassified = gate failure.
2. Before editing, retiring, or trusting a negative, run it through DR. The base rate
   for "DR compiles it" in this panel is 54/65, so the default expectation should be
   that DR compiles it.
3. `NOT IMP` (pass 1) and a pass-2 diagnostic are different kinds of fact: the first
   is a compiler limit, the second is a language/semantics complaint. Claims should say
   which one they are resting on.
4. When a negative turns out to be `my-gap`, its DR `.REL` becomes an acceptance target
   — do not delete the golden when the negative is retired, promote it.

## 5. What the 54 gaps look like as work

The gaps cluster on shapes already understood but not lowered (perimeter refusals
written during earlier slices): DEC-formal handling (N33, N52, N53), ROUND variants
(N37-N43), DO-loop shapes (N48-N51), string/varying operations (N11-N16, N21-N23),
BIT copy (N74-N77), GET variants (N44-N46), condition forms (N47, N25, N30), and
recursive float formals (N71). They are not one feature each: several share a lowering
family, so the backlog should be priced by family against corpus payoff
(`tools/blocker_audit.py`) rather than taken in panel order.
