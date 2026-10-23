# E2E-32 — wrong-value defects fixed: operand parking and formal dereference

Baseline verified before any change: HEAD `e4c84b2` on `main`, pushed, clean, `dune build` +
`bin/pli80c.exe` exit 0, gate **759 / 0 fail, 119/119 negatives, 14+5 = 19/19 divergences, exit 0**,
`ocaml/proto/` untouched (empty diff across the whole milestone).

| | start (e4c84b2) | end |
|---|---|---|
| byte-exact specimens | 759 / 0 fail | **776 / 0 fail** |
| negatives refused | 119 / 119 | **121 / 121** |
| divergence panel | 19 / 19 | **15 / 15** (6 promoted out, 2 added) |
| runtime panel | (none) | **12 / 12** (`--runtime`) |
| wrong values under execution | 5 probes | **0** |

The ordering of this milestone is the task's: correctness first.  Both P4 and P5 were reached only
after P1 and P2 were green, and P4 is reported as measurement rather than implementation.

## P0 — reproduction, before touching anything

`/tmp/e32/repro.py` compiles a probe, compares against its DR golden, and links + runs **both**
images, printing exit codes and raw console text, and flagging circularity.  Independently derived
expectations were supplied on the command line, not copied from DR.  All five E31 rows reproduced
exactly: E31F8 `r=2`/DR 1, E31F4 `s=7742`/DR 6, E31F7C `sum=7768`/DR 6, PB20 `q=6947`/DR 6,
PB4 `q=44`/DR 44; E31F2 right by luck.  Nothing was accepted on equal object size or clean
termination — for E31F8 the two `.COM` files were the same length and differed in one byte.

The one tooling trap worth recording: `tools/reldump.py` emits `DATA` lines sparsely, so counting
them is *not* a segment size, and my first divergence rows carried reldump-derived numbers that the
gate then rejected.  Rows must carry the **gate's own** measurement; both E32B3 and E32C6 needed
correcting after being written from my parser.

## P1 — Family C: the invariant was duplicated, not missing

DR's full E31F8 listing settles it: the callee's entry is
`MOV E,M / INX H / MOV D,M / XCHG / SHLD K A(0008)` — the caller's **address** lands in the formal's
cell — and the test is `LHLD K / MOV A,M / INX H / ORA M / JNZ`.  Mine emitted `LXI H,&K` with the
*identical operand*, then the same tail: one indirection short, so it tested the stored address
instead of the value, which is why `pick(0)` returned 2.

The important finding was *where* the bug was not.  My compiler already had this rule — `st.deref`
lists every formal of a non-recursive callee, and `lower_hl` and `cmp_load_deref` consult it.  That
is why these were **already** byte-exact before the fix:

| probe | shape | status before |
|---|---|---|
| E32C9 | `y = k;` (value read) | byte-exact |
| E32C7 | `if k ^= 2` | byte-exact |
| E32C8 | `if k > 2`, `if k < 2` | byte-exact |

So E31's "a FIXED formal in a comparison is not dereferenced" was too broad to act on.  The defect
was confined to two hand-rolled copies of the load: the `= 0` skip arm and the hoisted-conjunction
site (`LXI H,&cell` where the formal needs `LHLD cell`), plus the ident-vs-ident `=/^=` arm, which
emitted two bare `LHLD`s with no ladder.  Three written-out copies of one invariant, enforced
differently by each — the pattern C202 records.

Fix, one primitive, no duplicated scalar logic:

* `val_addr nm` — "leave HL pointing at the 2-byte value": `LHLD cell` for a by-reference formal,
  `LXI H,&cell` for a plain local.  Used by both zero-test sites.
* the ident-vs-ident `Eq/Ne` arm now routes **both** operands through the existing
  `cmp_load_deref`.  For two plain locals that emits exactly the `LHLD cell` used before, which is
  why nothing moved: **759/759 stayed byte-exact through the change**.

DR samples per orientation, captured first (`golden/e32c`), because a rule verified in one direction
only is not verified [C167]: `k = m` (deref **first** — the shape my `cmp_pair` refused as
unsampled), `m = k`, `k = j` (both).  All three are `PUSH H … POP D / ?IS22N`, so DR's rule is
"either side needs an indirection ⇒ stack form", each side loaded through whatever its own name
requires.

Control that proves the fix is not too broad: **E32C1** (`z = 0`, `z > 3`, a conjunction, locals
only) is byte-exact before *and* after and prints the independently expected `w=2`.

Executed against independent arithmetic after the fix: E31F8 `r=1`; E32C2 `a=1 b=2` (both branch
outcomes, separately visible — v1 of the probe summed them, which hid which branch was wrong);
E32C4 `1/2`; E32C5 `1/2`; E32C9 `4/5`; E32C7 `2/1`; E32C8 `gt=1 lt=4 eq=8`.

Two orientations still refused, registered as **my-gap** negatives rather than perimeter, because DR
compiles both and claiming otherwise would misrepresent the oracle [C188]: `if 0 = k` (E32C3) and
`if k = 3` (E32C10).  Both die in the condition-subset matcher before any load is chosen, so the
Family-C fix does not reach them; E32C10's DR shape (`LHLD K / ladder / LXI D,0003 / ?IS22N`) shows
the load would now be right.

Promoted out of the divergence panel [C154][C168]: **E31F8, E31F2, E31F5**.

## P2 — Family B: DR parks in DE unless the right operand writes DE

E31's note said "DR brackets every dereference with `PUSH H / POP D / DAD D`".  It does not, and my
compiler's own E2E-15 comment already said the opposite reading was wrong ("treated any deref on
either side as PUSH, which added a spurious PUSH H/POP D pair").  Both readings had been tested in
one direction.  The actual rule:

> park the **left** operand in DE (`XCHG`) when the right operand's lowering leaves DE alone; park it
> on the **stack** (`PUSH H` … `POP D`) when the right operand's lowering *writes* DE — which the
> member-read ladder `MOV E,M / INX H / MOV D,M / XCHG` does, and a plain `LHLD m` or a literal does
> not.

That draws the PB4/PB20 boundary E31 could not: PB4's `q = q + 4` has a literal on the right, so DE
parking is legal and the answer was right; PB20's `q = q + q` has a member read on the right, whose
ladder overwrote the parked value, so `DAD D` added **the address** — `6947 = 3 + &z`, reproducible
to the byte.  My predicate was `is a pointer FORMAL` (membership in `st.deref`), so every `BASED`
name and every qualified `p->v` on the right escaped it — including NETWORK's `s = s + w->v`.

Fix = one predicate `writes_de` (a qualified member read `Eqptr`, a based vkind, a `st.deref` member,
or a compound containing one) used by the ADD right-side test and by SUB.  Deliberately silent about
calls, which have their own arms — widening it would silently re-route them.

`E32B1` carries all three right-operand kinds in **one** probe and is byte-exact: `p->v + m` (12),
`p->v + 3` (10), `p->v + p->v` (14).  That single probe is what separates the hypotheses.

SUB used to refuse *any* deref operand ("no DR sample in this route").  E32B2/E32B4 are those samples,
so the refusal is narrowed to the one shape still unmeasured — a pointer formal as **minuend** — and
the measured routes now lower:

| statement | DR | expected | mine after fix |
|---|---|---|---|
| `m - p->v` | `LHLD M / PUSH H / ladder / POP D / CALL ?IS22N` | 4 | 4 ✓ byte-exact |
| `p->v - m` | `XCHG` park, **no** stack pair | −4 | −4 ✓ byte-exact |
| `q->v - p->v`, `p->v - q->v` | PUSH/POP, both sides deref | 2, −2 | 2, −2 ✓ byte-exact |

Non-commutative operators were tested in both orientations on purpose: a rule fitted only to `+`
would have passed the whole matrix while still computing wrong subtraction.

Byte-exact **and** executed-correct: E32B1, E32B2, E32B4, PB20, E31F4, E31F7C — the last being
NETWORK's own accumulation, which is why P2 was sequenced ahead of P4.

Left unfitted: **E32B3** is value-correct (11 / 22 / 15) but 2 code bytes long, first differing at
`0x21` inside a based-destination store.  Attributed to Family A (redundant reload) *before* being
cited, per [C140], and recorded as a divergence row.

**PB4's row was rewritten.**  Its ADD was never in Family B, and its `q > 3` test is not evidence
that based comparisons work: mine emits `LHLD P / LXI B,FFFC / DAD B / MOV A,H / ORA A / JM`, which
biases the **address** and branches on it, taking the correct path only because any `0x1Bxx` address
exceeds 3.  A low address would flip it.

## P3 — the runtime panel, and what each kind of evidence can carry

`spec/RUNTIME.txt` (12 rows) + `runtime_load`/`runtime_check`, wired as an opt-in `--runtime` arm
that runs after the byte and divergence panels and can fail the gate by itself.  Not a parallel
framework: it reuses `compile_one`, so **the object it executes is the same bytes the byte-parity arm
compares**, and it uses `oracle/linkrun.py` for link and execution.

Per row it requires: build succeeds (a row may not silently degrade into a refusal), `link` rc=0
**and** a `.COM` present (a `.COM` appearing is not the test [C137]), the run **terminates** (a
timeout-or-hang is a failure, not a skip), and every expectation substring is present in the console
bytes — with only CRLF→LF and PL/I's space-padding of numerics normalised, so `a= 12` is a byte-level
expectation.

The four claims the task asked to keep apart, as implemented:

| claim | mechanism | circular? |
|---|---|---|
| byte-exactness vs DR | main panel, `cmp` on `.REL` | — (this is the acceptance criterion) |
| independent arithmetic | `--runtime`, `kind=independent` | for a byte-exact image: yes, and labelled so |
| executing a byte-identical image | (not cited as evidence) | **yes — adds nothing about my lowering** |
| non-circular comparison | rows whose `.REL` differs (E32B3, PB4) | no — the run is evidence about mine |

Each row prints which authority did the work: `[NON-CIRCULAR: images differ, this run is evidence
about mine]` or `[byte-exact image: run validates expectation+oracle, not my lowering]`.  That label
exists because after the fixes *ten of twelve* rows became circular, and an unlabelled green runtime
panel would have read as stronger than it is [C205].

Proven non-vacuous before committing: injecting `c= 99` into E32B1's expectations made the gate exit
1 with `expected ['c= 99'], got 'a= 12 b= 10 c= 14'`; a short row raises a field-count error and
duplicate names are refused outright (a dict overwrite hides silently [C158]).  Restored, 12/12.

## P4 — ON ENDFILE: measured, corrected, NOT implemented

Two findings, one of which corrects my own prior claim.

**A statement-handler ON-unit is already byte-exact.**  E32E1 (`on endfile(sysin) n = 99;`) matches
DR's `.REL` byte for byte.  The refusal text had made ON-handling sound generally absent; only the
**label-transfer** form is open.  Registered as a specimen (776).

**The hidden cell is per BLOCK, not per ON-unit.**  E32E2 (two `on … goto` handlers in one block)
shows `LXI H,0 / DAD SP / SHLD * A(0019)` written **once** at block entry and **two** stubs reading
the same `LHLD * A(0019)`.  E31's note said "a 2-byte hidden cell per ON-unit" — that was inferred
from E30E2, which has exactly one ON-unit, where per-unit and per-block are indistinguishable: the
[C167]/[C185] failure mode again.  Corrected in place in the E31 note, in C201, in C206, and in the
compiler's refusal message.  (`DAD SP` is extended opcode `ED 31`, which DR's listing puts on the
line my first grep skipped — the address jump 0006→000A is what proves it is there.)

The remaining work is now exactly four pieces: (1) block-entry SP save into one hidden `*` cell;
(2) per ON-unit registration `LXI H,<file> / MVI A,05 / CALL ?ONCOP / JMP <continue> / JMP <stub>`
(whose prefix mine already emits — E32E1 proves the `?ONCOP` path is right); (3) the stub body
`LHLD * / SPHL / CALL ?RECOV` + `LXI H,<file> / MVI A,05 / CALL ?REVOP`; (4) transfer to the label
block.  **Not attempted with the budget left**: label back-patching plus a real-EOF witness is more
than a careful slice, and half-installed ON plumbing would be worse than a documented gap.

EOF **firing** is still unobserved: E31's attempt to drive a linked object to a real CP/M EOF timed
out under cpmsim, so compile-side parity and runtime handler execution remain separate claims.

## P5 — NETWORK checkpoint

Unchanged `artefacts/NETWORK.PLI` still refuses at the same place, verified by running it:
`an ON handler containing GOTO needs DR's ?RECOV label prologue … [TBD]` (line 50).  No CODE/DATA is
measurable, because no `.REL` is produced — reported rather than inferred.

Order of blockers after this milestone: **ON/GOTO** (line 50) → the **2+-formal DATA allocation**
defect (C203: `connect` takes three formals; mine over-allocates cells for the second and later
formals, proven by E32C6 whose *code* is byte-identical but DATA is 4 bytes too big) → compound
conditions with member operands → `GO TO`.  Both wrong-value families are now behind it, so NETWORK
is closer to *correct* than it was: its traversal (`E31F7C`), its chained qualification (`E30C1`) and
its accumulation (`E32B1`/`E31F4`) all lower byte-exactly today.

## P6 — register reuse: untouched, and now with one clean specimen

No liveness rewrite.  What the milestone added is separation: Family A is "mine larger, value right"
(E32B3, PB4's condition region), Families B/C were "value wrong" and are now gone, so the remaining
15 rows are candidates for a single optimization question.  Two falsifiable starting rules stand
(E31 note): DE-reuse ("DR reuses a loaded DE unless something writes DE") and HL-constant reuse
(E30L1 becomes byte-identical if one `LXI H,0000` is deleted).  Both are still single-direction
evidence and neither should be implemented before a disconfirming probe.

## E33 recommendation, ordered by risk removed

1. **ON ENDFILE/GOTO** — the four pieces above, in the order mine already supports registration.
   Needs the hidden `*` cell in the block's DATA layout (per-block!) and label transfer.  Until EOF
   firing is observed, keep byte-parity and handler-execution as separate claims.
2. **2+-formal DATA allocation** (C203) — one DR probe with two and three formals, then the
   allocator.  Small, and it gates NETWORK's `connect`.
3. **Real CP/M EOF under cpmsim** — `^Z` line, redirected file, or device input, so ENDFILE
   transfer can be *observed*.  Blocks acceptance of (1)'s runtime side.
4. **Equality with a literal on either side of a formal** (E32C3/E32C10) — the loads are now
   correct; only the condition-subset matcher is in the way.
5. **Register reuse** (Family A) — needs disconfirming probes first; 15 rows and 2 code bytes on
   E32B3.
6. **Then unchanged NETWORK.**

## Reproducing

```
python3 /tmp/e32/repro.py E31F8='r= 1' PB20='q= 6' E31F4='s= 6' E31F7C='sum= 6' PB4='q= 44'
python3 oracle/batch.py E32C1 E32C2 E32C3 E32C4 E32C5 E32C6 E32C7 E32C8 E32C9 E32C10 \
        --tag e32c --switches '$L$D$C$S'
python3 oracle/batch.py E32B1 E32B2 E32B3 E32B4 --tag e32b --switches '$L$D$C$S'
python3 oracle/batch.py E32E1 E32E2 --tag e32e --switches '$L$D$C$S'
python3 tools/e2e_gate.py --runtime          # 776 / 121 / 15 / 12, exit 0
```
