# E2E-40/P4 — the two class-gated member routes, implemented: 8 specimens byte-exact, and a tool cycle that blocked promotion

Slice: implement the two clauses [C260] characterized but did not implement, promote what they close,
and keep [C254]'s ordinary-variable control byte-exact. Scope was fixed at the outset to FIXED
BINARY(15) internal members: POINTER members, CHAR/VARYING/FLOAT/DEC members, STATIC INITIAL and E30
traversal were explicitly out.

## What was measured before writing any code

P3 had disassembled the shapes; P4 started from those dumps plus two controls:

* **E39P1** — the same statements with flat scalars. DR emits `LXI H,<value> / SHLD`, mine is
  byte-exact. Any change to the store route had to be class-gated or it would break the exact panel.
* **E39S3** — `a + h`, member + ordinary. DR emits `LHLD a / XCHG / LHLD h / DAD D`. This is what
  forbids the obvious-looking predicate.

## The store route, and the arithmetic error that delayed it

DR's member store is `LXI H,<DATA+offsetof> / MVI M,<lo> / INX H / MVI M,<hi>` — H carries the
**address**, the value never enters a register pair. My route was `LXI H,<value> / SHLD`.

My first implementation added the address load *after* the existing value load. E39S1 went 48 -> 59
against DR's 54: it emitted both loads. The array-element code had documented this exact defect years
of slices ago — "calling both emits the value twice (which is what an earlier attempt here did: it
added bytes instead of removing them)" — and I walked into it from the opposite direction. The fix is
to **skip the value load**, not to override it.

The reason I had abandoned the correct rule mid-implementation was [C260]'s cost model, which
concluded DR's member write was *more expensive* than mine and therefore that a byte-exact specimen
must be paying an offsetting cost elsewhere. Measured per write it is cheaper:

| 2-byte store | DR | mine (before) | mine (after) |
|---|---|---|---|
| ordinary scalar | 7 | 7 | 7 (unchanged, E39P1) |
| structure member | 8 | 9 | 8 |

The route turned out not to be new code at all: it is **array form 2**, byte-for-byte, including the
low-byte-first order AC1 once corrected. Only the discriminator is new — form 2 fires on a nonzero
element offset, a member has offset 0 in its own right, so the class had to come from bind.

## The class predicate

`var_info.imem : int option` — `Some k` exactly for a FIXED BIN(p<=15) member of an internal
structure at byte offset k, i.e. bind's own `RTimem (owner, k, RTbin p)`. It is stamped by one
function, `Vinfo.attach`, called from both frame builders (the main block and the per-procedure
scope swap), so it cannot be set in one scope and forgotten in the other. It deliberately does NOT
re-derive membership from the name: a dotted key `g.a` proves membership, but the bare spelling `a`
has no dot, and bind is the authority. Two bugs were caught on the way:

* attaching `proc_rows @ saved` — where `saved` is the OUTER scope's `var_info` list, not bind rows.
  A type error, not a semantic one, but the association change silently dropped `@ saved` first,
  which would have deleted the outer scope's variables.
* extending `var_info` with a required field broke 26 record literals; patched with brace matching
  rather than by hand, and the count (26, not the ~10 I had grepped) is itself evidence that a
  line-based survey of that file undercounts.

## The preservation route, and its boundary

`LHLD / PUSH H / LHLD / POP D / DAD D` replaces `LHLD / XCHG / LHLD / DAD D` when **both** operands
are members. Four programs pin the boundary: E39S2 and E40Q1 (member+member -> PUSH/POP), E39S3
(member+ordinary -> XCHG), E39P1 (ordinary+ordinary -> XCHG). Value-identical either way; 2 bytes.
This completes the correction of [C254], whose original explanation keyed the rule on *tail
position* — [C260] withdrew that, and the class-pair predicate is the replacement.

## Where the reuse-kill belongs, and where it does not

`SHLD` leaves HL holding the value, which is what lets AB19/AB21 chain constants. The member route
puts an ADDRESS in HL, so `last_imm` must be cleared — and E39S7 confirms DR agrees, because its
value reload at 0018 is exactly the 3 bytes a chain would save. But `POP D` restores HL to the summed
value, so the chain legitimately survives an ADD. I killed it after the ADD as well, and S7 moved
54 -> 55 -> 52 as the kill moved from the wrong place to the right one and back. ZK6 — DR's own
no-reuse-after-address-parking witness, already quoted verbatim in my source — is the rule.

## Result

`939 -> 946` byte-exact, 0 fail. Negatives 125/125. Divergences 11/11 (re-pinned, not deleted).
Runtime 19/19. Coverage 85 rows / 0 errors. Corpus census unchanged: 44/41/3/**15 EXACT / 0
DIFFERS**/26/**0 UNEXPECTED**.

Byte-exact now: **E39S1, E39S2, E39S3, E40N1, E40Q1, E40Q2, E40R1** (registered in `SPECIMENS`) and
**E27S12** (byte-exact at 66/66, 0 differing bytes, but *deliberately not registered* — see below).

Still divergent, both re-pinned with the reason: **E39S5** — its CODE is now byte-identical to DR's;
the only remainder is the blocked nested-layout DATA overrun (mine 6, DR 4), 5 differing file bytes,
all record-length fields. **E39S7** — 52 vs DR 57, tail byte-identical from 001F. **E40Q4** — 50 vs
DR 62, POINTER members, untouched.

**E40R1 is the strongest witness in the project**: `.REL` byte-exact, `.COM` IDENTICAL vs DR, console
**BYTE-EQUAL** — 13 raw bytes, `g=        16\r`. The `--link-run` arm links both sides and compares
the transcripts; it is only available for names in `SPECIMENS`, so byte-exactness is what unlocked
it. The RUNTIME.txt row stays (it pins the value, which is ground truth independent of how it was
obtained), but its note asserted "My image is not byte-exact — code 59 vs DR 65", which became false
this slice; corrected in place rather than left as a stale description of current state.

## E27S12 declined registration

E27S12 compiles byte-exact now. It is NOT added to the panel: it was never on any panel — it reached
this episode only as a `DIVERGENT.txt` record. Its honest history is a `my-gap` refusal pin retired
by [C256], then code 64 vs DR 66, now 66 = 66. That is recorded in prose and cited in `COVERAGE.tsv`
as a **path** (`artefacts/ST12.PLI`), not as a byte-exact specimen invented in the same slice that
claims to have closed it. The distinction matters because the panel is what the project treats as
verified parity.

## Tool cycle that made promotion impossible (C262)

`coverage_check.load_panel()` resolves probe keys against the *committed* `spec/INVENTORY.txt`, and
`--update-inventory` regenerates that file *after* the coverage loop that `sys.exit(1)`s on any
error. Citing a new specimen in the probes column therefore broke every invocation **including the
registration command itself**. Fixed with a `[E2E-40/P4]` circularity guard: under
`--update-inventory` the coverage panel is reported, not fatal. Protection is not weakened — the
guard still aborts every ordinary gate run, and the next ordinary run re-validates coverage against
the rewritten inventory. Verified end to end.

## Process errors, this slice

* **`git checkout -- tools/e2e_gate.py` to undo one unwanted edit destroyed the uncommitted
  SPECIMENS registrations and the link-run arm.** `git status` listed 8 modified files and
  `tools/e2e_gate.py` was silently absent — that absence was how I found it. The 6 coverage errors
  that followed were evidence, not a new problem. Reverted by re-editing, then rebuilt and
  re-verified.
* **`LR=0` from `gate --link-run | grep ...; echo $?` was grep's exit code — [C249], third
  occurrence, and this time it nearly had me report a successful link-run I had not verified.**
  Re-run with the code captured directly; the run was then interrupted by my own tool timeout with a
  0-byte output file, so it had to be relaunched in the background with an explicit log.
* `dis80.py` reported `span`/`declared` in its own format and my first measurement script invented a
  `LEN=` parser that returned -1 for everything; switched to the gate's own authority,
  `tools/relstats.py` (which takes a **path**, not bytes).
* A validator-hole test was invalid — I passed `--coverage` where the flag is `--tsv`, and then
  tested on a copy with no census file. The hole did not exist: coverage_check does enforce probe
  resolution, and it is what surfaced the cycle above.
* `[C261]`'s first draft stated S7's sequence as "52 -> 55 -> 52"; the measured sequence is 54 -> 55
  -> 52. Corrected in place.

## Left blocked, unchanged by this slice

POINTER member stores (no oracle; and its writes cannot use two `MVI M`s unchanged); member stores
of computed values; level-2+ nested member layout (E39S5's DATA 4-vs-6); `g.a` where `g` has no
member `a` — **DR's behaviour for that shape is still unmeasured, and my refusal is not
evidence**; `outer_rows` threading for enclosing-frame ambiguity; STATIC INITIAL byte placement
(ENTER/REPORT/MPMCALLB/FSCAN/LOAN2); two-sided widening for `>=`/`<=`; BASED character types;
values for E39S5/E39S7/E40Q4 remain unexecuted.
