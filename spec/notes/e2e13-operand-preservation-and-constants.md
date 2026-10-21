# E2E-13 — operand preservation across calls, small-constant arithmetic, and the evidence-class split

Correctness-first milestone. Baseline verified from Git, not memory: HEAD `7277a1f`,
tree clean, 423/423, 75/75, 13/41. Final state: **477/477 byte-exact, 75/75 negatives
refused, corpus 13/41 EXACT / 0 DIFFERS / 28 REFUSED**, both pre-flight selftests green.
Claims: C141 (resolves C139), C142 (new gap, refused), C143 (C140 closed), C144 (retraction).

## 1. Instruments built first, because the previous ones were insufficient

There was no way to read the code *my* compiler generated: DR's `$C` listing exists only
for DR compiles, and raw bytes cannot answer "which instruction does DR use here".  Two
tools, both kept:

* `tools/dis80.py` — disassembles a linked `.COM` (offset == code address, verified: DR's
  `LXI B,07D0` sits at file offset 0x0000) or a `.REL`.  Its opcode/mnemonic/length table is
  **learned from DR**, not written from memory: 60 matched (listing, .COM) pairs, image
  offset accepted only if every `LXI` line's byte is 01/11/21/31 and every `CALL` line's is
  a CALL opcode.  Result: 43 opcodes, zero printed under two mnemonics; unobserved opcodes
  print `DB nn`.  REL mode has a documented limitation (some RELOC-covered operand bytes
  never surface as DATA records — use it to read link fields, never to prove absence).
* `tools/linecode.py` — pulls the code DR generated for a *named source line* out of a `$C`
  listing.  Every rule in C141/C143 came from this, which is what "establish it from DR's
  listings" means in practice: `linecode golden/e2e174/P1/P1.PRN "return ("`.

Why this mattered immediately: my hand-written table decoded 0xB6 as XRA, turning DR's
correct `if n = 0` test into an apparent compiler bug.  The learned table (0xB6 = ORA,
0xAF = XRA — matching this project's parity-derived `CMP M=0xBE`, `SBB M=0x9E`) falsified
that in one step.  Retracted as C144.

## 2. Priority 1 — the actual lowering rule, and it was not what C139 guessed

Comparing the two linked images of the *same* source (DR `golden/e2e169dl/U1.COM` vs the
historical wrong-value build `golden/e2e169ml/U1.COM`), at the recursion site:

```
DR    LHLD n ; DCX H ; SHLD *A(001A) ; LXI H,*A(0018) ; CALL sum ; XCHG ; LHLD t ; DAD D
mine  LHLD t ; XCHG ;                  LHLD n ; DCX H ; SHLD *   ; LXI H,* ; CALL sum ; DAD D
```

Mine loads the left operand **before** the call and parks it in DE.  Every DR-compiled
callee destroys DE — its own prologue is `LXI D,<shadow>` plus the copy ladder
`MOV E,M / INX H / MOV D,M / XCHG`, visible in my object at 013C-0150.  So 12488 was not a
rounding or width problem: the addend was whatever the nested activation left in DE.
DR loads the left **after** the call, which is sound because a recursive activation's locals
live in its own `?SVBLK` shadow block restored by `?RSBLK` — the re-read is the same value.

The rule set (C141) came out of six listings, and it splits three ways: defer the load
(simple variable), fold the constant (literal — and DR commutes, `1 + g(3)` is `CALL ; INX H`),
or park it on the **runtime stack** (`PUSH H`/`POP D`) when there is nothing left to re-read
(compound, or a second call).  SUB always stacks, because `?IS22N` computes `DE - HL` and the
minuend has to be in DE after the call.  C139's guess ("DR does not reload the left value
from the declared cell") was half right and misleading: DR *does* reload from the declared
cell, just later.

**Correction, as executed.** U1: 12488 → **5050** (== DR-built, == 100·101/2).  W1/W2 = 36
(8·9/2), W3 = 8 (its `t = 1` makes it a counter).  All twelve P witnesses match DR *and*
independently computed arithmetic — see C141 for the table.  U1/W1-W3 moved from REJECTS to
SPECIMENS; the wrong-value artifacts stay committed as evidence.

## 3. Priority 2 — SUB audit, clean controls, and one conditional-wrongness

S1/S6 were confounded by `n + 2` callees (C140); P6/P7 are clean controls whose callees are
byte-exact.  Result: my SUB-with-call-right route had the **same** DE-parking defect, and it
is worse than the ADD case — `LHLD t ; XCHG ; <call> ; ?IS22N` computes `DE - HL` with a DE
that the callee is free to overwrite, so it is conditionally wrong rather than wrong only for
recursive callees.  P6 happens to print the right 91 (its callee `n*3` leaves DE's value
usable), which is precisely the trap: a correct witness from an unsafe route.  It is refused
loudly, with DR's route written in the `[TBD]` message so the next session starts from the
answer rather than re-deriving it.

Untested and therefore **not** refused (per instruction): ADD/SUB with a pointer-formal
operand across a call, MUL with a nested call operand, mixed FIXED/FLOAT operands across a
call, `lit - call`.  Each is listed in §6.

## 4. Priority 3 — C140 closed as a rule, not as a refusal (C143)

`+k` is `(INX H)*k` up to a threshold, then `LXI B,k ; DAD B`.  The threshold is **route
dependent** and only visible because both routes were probed at exactly k=4:

```
n = n + 4  (self-update)  -> LXI B,0004 ; DAD B        [K4, X1]
return (n + 4) / t = n+4 / r = x+4 / g(n)+4 -> (INX H)*4   [R4, X2, T4, N7]
```

Subtraction mirrors it (`DCX H` to 3 self-update / 4 otherwise, then two's-complement
`LXI B`).  Plus three measured corollaries that each kill a plausible over-generalization:
`k = 0` emits nothing (M0); the literal-left case commutes byte-identically (K9 vs K5); and
`n - 2 + 3` reduces per operator rather than netting to `+1` (M7).  Implemented via
`hl_bias_free` (new, threshold 4) alongside the existing `hl_bias` (self-update, 3);
`const_sub` extended past 4 to DR's `LXI B` form instead of refusing.  All 32 constant
probes byte-exact, including C1/C4/C7 which DIFFERED at the start of this milestone — the
value-correct-but-byte-wrong fallback is gone for these shapes.

## 5. Priority 4 — the evidence-class split this milestone forced (C142)

`cmp` had been bundling four properties.  Separating them is the durable result:

1. **semantic correctness** — executed value vs independent arithmetic
2. **DR instruction-selection identity** — the code bytes
3. **.REL serialization identity** — record order and anonymous-cell numbering
4. **link/runtime validity** — LINK resolves every object by name, .COM identity, console

P5 `(t+u)+g(3)`, P6 `t-g(3)`, P12 `g(3)+g(4)`, P9 `t+g(h(2))` pass (1) and (2) — identical
instruction bytes, correct values, DR-parity linked output — and fail (3): DR emits the
call's `LINK-SET-LC data` / `RELOC` records *before* any code record of the expression, and
numbers cells in that plan order (P9: outer result 000B < inner result 000D < outer
argument 000F; mine has the last two interchanged).  Since (3) is the acceptance criterion,
they refuse loudly with the cause named, rather than passing on value or shipping a
plausible byte stream.

**The known fix, deliberately not attempted here:** plan a call's result cell before
descending into its arguments, and emit allocation records before the expression's code.
That edits the pool/dedup ordering — the property ARCH-0 flagged as the riskiest in the
program, on which 477 byte-exact specimens now depend.  It needs its own milestone with the
full gate as the safety net, not a opportunistic patch inside a correctness pass.

## 6. Incidents and hygiene

* **Key collision, again.** Registering my constant probes as `T2/T4/T8` silently overwrote
  the long-standing specimens `T4` and `T8` (e2e11u/e2e11w).  Caught by the arithmetic +
  collision-check script I added after the ST*/T* incident in E2E-12 — the totals looked
  plausible either way.  Re-keyed to `Y2/Y4/Y8`, with source/artifact names left canonical
  (`e16src/T4.PLI`, `golden/e2e177/T4/`) and the mismatch commented in the gate.
* One registration attempt aborted mid-script on a bad anchor and wrote nothing, so an
  "applied" message was not evidence of an applied change; verified by re-import instead.
* `hl_bias_free` and `expr_contains_call` were each first placed after their use (OCaml
  ordering) — build caught both.  The first `expr_contains_call` returned false for a bare
  `Esuffix`, so P9 emitted instead of refusing: caught by checking the refusals individually
  rather than trusting the count.
* One refusal I wrote said "SUB is worse than a byte difference" before I had proved it;
  the proof is the DE-destruction visible in my own callee prologue bytes, stated in C141.
* One gate at a time, per-PID scratch (fixed last milestone), no rebuilds during a run.

## 7. Still open, in the order I would take them

1. **C142 record-order / cell-numbering fix** — plan-then-emit; unlocks P5/P6/P9/P12 and the
   general parking route.  Gate-gated; touches the riskiest order property.
2. Pointer-formal operands across calls (ADD defer route, SUB push route) — unprobed, so
   still refused by the older narrower guards.
3. `lit - call`, `call - lit`, MUL with nested call operand — unprobed dimensions.
4. Mixed FIXED/FLOAT across a module boundary (`?QFI15`, `?QI15D`) — untouched here.
5. Naming audit: `op_jz = 0xC4` in codegen.ml is a byte pinned by parity while DR's learned
   table never shows 0xC4; 0xCA is `JZ`.  Possibly a mislabelled constant, possibly a
   conditional-CALL site.  Worth one grep-and-listing pass, because a wrong *name* on a
   correct byte is how the next C144-style false conclusion gets made.
