# E2E-15 — multiplication family, the parking rule, and what it cost to find them

Baseline HEAD 8c849f9 (478/478, 74/74, 13/41). Final: **478 -> 510 byte-exact specimens, 74 -> 80
negatives, corpus unchanged (13/41 EXACT, 0 DIFFERS)** -- verified by the full gate run.

> CORRECTION [E2E-16/P3]: the body of this note and my first post-milestone summary quoted **509**.
> That number was WRONG, and it was the symptom of the error described in section 6 -- while
> "simplifying" P9's registration I deleted a verified specimen, so the panel had 509 entries and
> P9 was silently untested.  The correct verified total at the end of E2E-15 is **510 byte-exact**
> (477 inherited + P9 + 32 new MB probes), re-established in E2E-16 by restoring
> `SPECIMENS["P9"]` and re-running the full panel.  A total is not a check: 509 and 510 differ by
> one line of output nobody read, which is why `spec/INVENTORY.txt` now names every entry.

## 1. The multiplication result is not the interesting part

C148 is a clean rule and it fell out of one probe matrix: hold the scaffolding identical, vary the
expression, read DR's `$C` listing. `k=1` elides, `k=2^m` emits m copies of `DAD H`, other `k <=
32767` emits `LXI D,k ; CALL ?IM22N`, `k >= 32768` takes the decimal pool, `k=0` emits DR's
suspicious `MOV L,H`. Context-free across all nine contexts I probed.

The interesting part is what that matrix exposed, and none of it was about multiplication:

* **C150 -- a live mis-compile in my ADD/SUB emitter, reachable at baseline.** My general route
  was `HL = left ; XCHG ; HL = right ; DAD D`, which is only correct if evaluating the right
  operand leaves DE alone. `?IM22N` does not. So `n + (n * 3)` printed **21** (the right operand
  alone) where DR prints **28**, `n * 2 + n * 3` printed 21 vs 35, `n - (n * 3)` printed -21 vs
  -14. That is the third occurrence of the C139 pattern -- a value parked in a register across an
  operation that destroys it -- and it was hiding behind a *guard for another feature*: the
  multiply-by-2 refusal made `n + (n*2)` unbuildable, so nobody noticed that `n + (n*3)` was
  buildable and wrong. Closing one route uncovered the other.
* **C151 -- `elide_fixed_zero` did not test the operator.** `x * 0` became a copy of `x`; `x / 0`
  became a copy of `x` and never reached the division-by-zero refusal. Found only because MB7 was
  supposed to refuse and instead built.
* **C152 -- a pre-existing pool-layout defect** found via MB40, whose program contains no
  multiply, no call, and no expression: two PUT statements sharing one string literal. Mine
  writes 139 records like DR but declares DEF-DATA-SIZE 8 against 7, shifting every automatic.

Three silent defects, one milestone, all found by *probing an adjacent feature* rather than by
testing it directly. The lesson is that a `[TBD]` guard is not only a safety device -- it is also
a blindfold, and removing it must be done with the runtime panel, not just the REL comparison.

## 2. Why runtime evidence was decisive here

Every one of MB15/MB28/MB34/MB35/MB37 *compiled* in my build and the REL bytes looked "just a
selection difference at 0x14". Only `cmp` plus a linked run separated "different instruction
choice" from "wrong answer". So the acceptance bar for this milestone was: byte-identity AND a
correct executed value AND -- for the pre-existing wrong path -- an independent arithmetic
expectation (`7 + 7*3 = 28`, written down before reading DR's output, not after).

I also read the run outputs **verbatim** rather than through a regex. My first extraction
`grep -oE "W *[-0-9]+|[-0-9]+"` reported MB15 as "mine=82 dr=82 SAME" -- an artifact of matching
digits in the surrounding transcript. A numeric-similarity claim built on a sloppy extractor is
worse than no claim, because it looks like verification.

## 3. DR's own defect, and why I refuse to copy it

`n * 0` and `0 * n` both lower to `MOV L,H`, which copies H into L and does not produce zero. DR
compiled it, emitted a `.REL`, and my instinct was "match DR or fail". I am not matching it: a
byte-for-byte goal is a goal about my output, not a licence to reproduce a wrong computation
without checking it. The refusal names the reason and points at a runtime experiment on DR's own
`.COM` as the thing that would settle it.

## 4. C146 after this milestone (Priority 3)

Nothing about C146 changed in production -- P5/P6/P12/D1/D11/D12 still refuse -- but the evidence
got better, and one of my E2E-14 claims turned out to be about my own instrument:

**R1: P5's "code-address mismatch" was an artifact.** I measured DR referencing P5's descriptor at
code 005F and mine at 0056, and recorded it as a distinct second problem. What my measurement
actually did was replace `add_left_needs_push` with `false`, which rerouted the expression through
the DEFER path (call first, hence 0056). The bypass changed the subject and I read the result as a
finding. With the guard intact, DR's P5 sequence is `LHLD T / XCHG / LHLD U / DAD D / PUSH H /
LXI H,*A(000B) / CALL G / POP D / DAD D` and my push-route emits exactly that.

**So C146 is narrower than it looked.** Code bytes match for all three refused shapes; the only
remaining difference is *when the descriptor record enters the bit stream* -- DR writes a call's
descriptor before the enclosing expression's first code record even though it is referenced later
(P5: `SET-LC data 000B` at bit 1892, expression code starts at 0056). The migration therefore
needs a way to emit DATA-segment records ahead of CODE-segment records that are not yet emitted:
a capture/replay path through `reloc`/`link`. That is ARCH-1-class machinery, all three shapes are
already behind loud `[TBD]` guards (so the change cannot regress anything by construction), and it
is proposed rather than attempted -- per instruction, and because "the guards make it safe" is not
the same as "the mechanism is understood".

## 5. Instruments added

* `registration_audit()` in the gate: static duplicate-key detection per registration block, plus
  runtime SPECIMENS/REJECTS overlap and REJECTS/NEG_META symmetry checks. Negative-tested against
  all three historical collision shapes before being wired in; silent on the clean file.
* Probe hygiene: batch runners must not be pointed at an existing golden tag (the safety rule fires
  and reports 0 ok, which looks like DR refusing). MB41-43 and the first MB44-46 runs were exactly
  that, and `golden/e2e182/D2` debris from E2E-14 is the same class of error. No golden, no verdict.

## 6. (added by E2E-16) the count that was wrong

Section 4's claim about P9 was right and my registration was not. E2E-16's Priority 3 turned that
into an instrument: `spec/INVENTORY.txt` commits one row per panel entry (name, kind, source,
golden), and the gate aborts unless the live panel matches it exactly. It detects three things a
count cannot: a REMOVAL (my P9 case), an ADDITION, and a SUBSTITUTION -- same name, repointed
golden, identical total. The substitution case is not hypothetical: E2E-12's collision replaced
five specimens while keeping the panel's shape, and in E2E-16 the inventory fired on PL8/PL9
being repointed between golden tags, where the entry count did not move at all.
