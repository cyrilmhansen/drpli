# E2E-11 step 3 — CALL as a statement (internal procedures)

Status: **complete for internal procedures.** Gate **377/377 byte-exact / 0 fail**,
negative panel **68/68 refused**, corpus **10/41** (unchanged — see "Payoff" for
why this slice was still the right one).

## Why this slice

The step-0 blocker audit ranked `CALL_STMT` first by program count (23 of the 31
remaining corpus programs) and it was invisible in the first-blocker ranking,
because those programs are refused earlier for something else. The instruction to
start with internal procedures and minimal DR probes was the right call, and the
corpus turned out to agree with it in an unexpected way: no corpus program is
closable by CALL alone, but three became closable by exactly ONE further feature.

## Probes

`e13src/E24[A-J]`, `E25[A-H]`, `E26[A-K]`, `E27[A-C]`; DR goldens in
`golden/e2e121` … `golden/e2e129`, link/run in `golden/e2e130*`, `e2e131*`.
Sources are CRLF with `;\r\n\x1a` and no trailing `$` line [C118].

The design principle for this set: every question is asked twice, once in
statement position and once in expression position, so the answer comes from the
listings rather than from my expectation — that is the only reason C122 is a
confirmed reuse rather than an assumption.

## What was built

| feature | specimens | claim |
|---|---|---|
| CALL statement = expression-call ABI; disjoint procedure kinds | E24A/B, E24D/E24H/E24I (refused) | C122 |
| forward-CALL chaining, many sites / one chain record | E25F, E27A | C123 |
| zero-argument calls: no descriptor, no storage | E24A, E24F, E24J, E25A | C124 |
| implicit RET after a body with no RETURNS | E25A/B/C/E/G/H, E24A/F/H | C125 |
| label definitions end HL-constant reuse | E25G | C126 |
| store through a pointer formal (3 shapes, 2 byte orders) | E24B/C/E, E25F, E26A–E26E, E26H | C127 |
| compare against a pointer formal | E25B, E25E, E26F, E26G | C128 |
| exhaustive statement walkers | all | C129 |

## Verification beyond `.REL` byte identity

C123 is the reason this matters. My first chained every later forward site against
the FIRST slot; E25F (two sites) was byte-identical and *still linked to a wrong
address* — `reldump` showed matching records, DR's LINK put 011F in both operand
words, mine put 0114 in the second. E27A (three sites) is what exposed the actual
rule: each later site relocates against the *immediately preceding* site.

So for the 16 CALL specimens I ran the full protocol: compile (`.REL` byte-exact
against DR) → link my own `.REL` with DR's LINK-80 → compare the resulting `.COM`
byte-for-byte (**16/16 identical**, sizes 640–7680 B) → execute under cpmsim
(**16/16 rc=0**). Spot-checked the one program with visible output: E25C's
`put skip list('x')` from inside the callee produced `0a 78 0a`.

Because the `.COM` bytes match, output equality against DR is implied rather than
demonstrated separately; I note that explicitly instead of claiming a second
evidence class I did not produce.

## What is refused, and why that is the right answer here

- `CALL` of a value-returning procedure — DR: `NOT PROC` [E24D fixed, E24H float].
  Conformance refusal, [N81, N82].
- No-`RETURNS` procedure in expression position — DR: `TYPES NOT=` [E24I], [N83].
- `x = x + 0` through a pointer formal — C119's zero-elision is pinned for ordinary
  cells only, and dropping the bias would also drop the store, so there is no
  shape to copy.
- Pointer formal as FIRST operand of a two-variable compare, or both operands
  pointers — DR always orders plain-first; the deref-first pairing has no sample.
- DEC/FLOAT formal stores — see below.

## Two corrections to my own prioritization

The user's framing was right on both counts, and my audit had blurred them:

1. **FDTEST does not need CALL-as-statement.** It uses an external `ENTRY` in
   *expression* position (`fdiv2(i,100)` inside a PUT LIST). Its blocker is
   ENTRY_DECL alone.
2. **DTEST's CALL targets an external assembly routine** (`call div2(...)`), so it
   is the same object as ENTRY linkage, not a separate internal-CALL feature.

Both DTEST and FDTEST therefore now sit at "closable by exactly ONE feature:
ENTRY_DECL", which is external ENTRY work — assessed separately, with the
object-file / full-executable distinction kept explicit, because linking and
running additionally need the historical assembly modules.

## Newly discovered, not yet implemented (next slice candidates)

- **DEC and FLOAT pass-by-reference stores exist in DR** (E26J, E26K compile and
  emit `.REL`): DEC = `LXI H,R / MVI A,09 / CALL ?DLDOP` then
  `LHLD Q / MVI A,09 / CALL ?DSTOP`; FLOAT = `LXI H,*S / PUSH H / LHLD Q / POP D /
  CALL ?FX44M`. This makes **N55_FORMAL_STORE the fifth instance** of the
  "negative whose subject DR compiles" pattern (after N56, N63–N66, N77). N55 stays
  in the panel because my compiler really does refuse, but it is now labelled a
  capability gap with the narrower marker, and the old blanket "store to pointer
  formal unproven" text — which implied DR rejected the whole category — is gone.
- **E26I** (`x = 0 - x`, then `x = x - 3`): the negate-through-pointer shape.
- **E27B** (`call s(y)` where `y` is itself a pointer formal, i.e. passing a formal
  on as an actual) — my existing `pointer-formal call argument unproven` refusal.
  Very likely common in the corpus, so worth its own probe set.
- **E24G** external ENTRY as a statement: DR's shape is fully visible
  (`LXI H,*A(desc) / CALL EX` + `LINK-CHAIN-EXT EX`, no EXTDEF) and the object file
  is reachable; deliberately refused [N84] until the linkage is assessed as its own
  milestone.

## Process notes

Four of my edits failed to compile, and the only reason none of them was tested as
a success is that `dune build` output is now gated: `io_val` is `expr option`, the
hoisted `wi` was out of scope, `Printf.sprintf` will not accept a concatenated
format string (three separate messages), and one of my `sprintf` calls had the
concatenation *outside* the format so the `%s` was never bound. A fifth failure —
removing a `| _ -> []` catch-all — surfaced as a runtime `Match_failure` rather
than a type error, which is precisely why the collectors are enumerated now.

One stale-binary near-miss was caught by `ls -la` on the executable showing the old
timestamp after a build that looked like it printed only warnings.
