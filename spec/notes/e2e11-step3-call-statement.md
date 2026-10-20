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

## Verification beyond `.REL` byte identity -- including a retraction

C123 is the reason this matters, and my first write-up of it was wrong in a way
worth keeping on the record.  I claimed my wrong anchoring rule produced a
byte-identical E25F that nevertheless linked to a wrong address, and that a
two-site program cannot distinguish "against the first" from "against the
previous".  That sentence is self-contradictory: identical raw `.REL` linked under
identical conditions cannot yield different `.COM`.  The `.COM` difference was
proof that the `.REL` differed, so "byte-identical" was the error.

Reproduced in a throwaway worktree by removing only the re-anchoring line: E25F
differs at byte 105 (`LINK-CHAIN-ADDR` target `0014` vs DR's `001A`), E27A at
bytes 109/124/125.  Two sites discriminate perfectly.  The reason I believed
otherwise is that `tools/reldump.py` printed LINK records' address field only for
`int` values, while they are `(SEGMENT, ADDRESS)` tuples -- so the one number that
identifies the chain target was silently omitted and `LINK-CHAIN-ADDR  None` looked
the same in both files.  Fixed in the tool, and the diff now shows it directly.

Generalized lesson: **a decoded dump is a claim about what matters.**  Comparing
through my own decoder rather than against raw bytes let a suppressed field define
the notion of "same".  Byte identity via `cmp` stays the criterion; decoded dumps
are for understanding a difference, never for asserting absence of one.

The rule itself was right and is corroborated the way I originally described:
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

## Post-slice: the corpus map changed shape (audit re-run)

With the CALL baseline tags in the capability set, `tools/blocker_audit.py`
re-ranks and the #1 blocker disappears from the payoff table entirely (baseline 32
-> 33 tags). Corpus stays 10/41 exactly as predicted -- CALL alone closes nothing,
because every one of the 23 CALL programs has a second blocker -- but three
programs moved to "closable by implementing exactly ONE feature":

| program | now needs only |
|---|---|
| DTEST | `ENTRY_DECL` (external assembly `div2`) |
| FDTEST | `ENTRY_DECL` (external `fdiv2`, in expression position) |
| REVERT | `LABEL_AS_DATA` |

and ACK remains the only two-feature candidate (`BLOCK_OPT:stack` +
`PUT_GENERATED_ITEM`). The new #1 payoffs are STRUCTURE_LEVEL (11 programs) and
FILE/open (10).

**Decisive for the next step: the external modules exist.**
`artefacts/pli80-v14-reference/DISK2/DIV2.ASM` and `FDIV2.ASM` are in the reference
corpus (also under pli80-v10), so external-ENTRY work is verifiable end to end
rather than only at the object-file level -- provided an assembler path is found or
built. That changes the cost comparison the instruction asked for: external ENTRY
now has a *full executable acceptance* route for two programs (DTEST, FDTEST),
whereas named sequential FILE I/O needs `?OIOOP`/`?SIOOP`/`?SLCTS` and stream
FCB mechanics with no comparable shortcut.

## Still open in this feature area

- **Bare-identifier call arguments: 10 of 41 corpus programs** do it (DEPREC,
  DIOCALLS, DTEST, LABELS, MAININVT, MPMCALLA, MPMCALLB, NETWORK, REVERT, SAMPLE),
  and E27B shows what DR does when the identifier is *itself a pointer formal* --
  `LHLD Y / SHLD <desc cell>`, i.e. it forwards the address without materialising
  anything. My compiler refuses that case. This is the cheapest remaining CALL-work
  with real corpus leverage, and E27B's `.REL` is already pinned as a golden.
  I started a byte+reloc-annotated dump for it and stopped when `tools/reldump.py`
  turned out not to expose the parser under the name I assumed; the right next move
  is to extend `tools/relreloc.py` (which does have `parse`) rather than re-derive it.
- DEC/FLOAT formal stores (E26J/E26K goldens pinned, DR lowerings recorded in C128).
- E26I's `x = 0 - x` negate-through-pointer.
