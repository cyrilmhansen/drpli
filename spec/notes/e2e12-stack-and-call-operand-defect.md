# E2E-12 — OPTIONS(STACK(n)), and two compiler defects found on the way

Milestone per the approved plan: (1) give C137's unresolved-symbol detection a
regression, (2) characterize `OPTIONS(STACK(n))` against DR with MAIN and non-MAIN
controls, (3) implement the smallest evidence-backed STACK route, (4) re-audit ACK and
ACKTST independently, (5) keep byte parity + controlled negatives + runtime
verification, (6) ARCH-1 stays isolated.

Claims: **C138** (STACK), **C139** (silent mis-compile), **C140** (peephole coverage
gap). E2E-11's route/entry work is not revisited here.

---

## 0. First, the correction that reframed the milestone

ACK and ACKTST are **not** procedure-only modules. Both write

```
procedure options(main,stack(2000));
```

and my earlier classification used `'options(main)' in text`, which cannot see a
multi-option list. The corpus's procedure-only population is **2 files (A, MPMCALLB)**,
not 4, and the entry route was never a prerequisite for ACK/ACKTST. Corrected in place
(with this diagnosis attached) in `e2e11-step5-procedure-only-modules.md` §5 and
`e2e11-step5-gap-ranking.md` §8. Two rules came out of it:

* **Classify with the parser, not with `grep`.** The binder already parses block options
  into `(key, args)`; a substring test is strictly weaker and fails silently in the
  direction that misleads a cost estimate.
* **"First refusal" is an artifact of check order.** My block-option check runs before
  statement lowering, so one shallow blocker masked two deeper ones and made both programs
  look nearly free.

## 1. C137 regression (item 1)

`oracle/linkrun.py` now has `parse_undefined(seg_text)` (extracted from `link()`) and a
`selftest` stage dispatched before argparse — no emulator, no tag, no workspace. Three
pinned checks, wired into `tools/e2e_gate.py` next to the reldump selftest, so the gate
aborts if any fails:

1. `golden/e2e153_l3` (companion **not** named): detection returns `['A']`.
2. `golden/e2e153_l4` (companion named, `LINK D:E29F,D:A`): returns `[]`.
3. **Display-independence**: a synthetic segment whose symbol sits at character 263 —
   beyond any display window — must still be detected.

Verified by mutation, not by reading: replacing `parse_undefined` with `return []` makes
the selftest exit 1; restoring it makes it exit 0.

That third check replaced an assertion I had wrong. I had written — in code, in the
commit message and in C137 — that the old `[:120]` status cap *hid the symbol name*. The
surviving broken-link transcript puts `A` at character **110**, inside the old cap, and
the transcript that actually produced my reading was **overwritten when I re-linked with
`--reuse`**. So the mechanism was a story about a lost artifact, not a testable property;
I nearly shipped a test that asserted it. What is verifiable is that detection must not
depend on presentation, and that is now what is pinned. C137's text is corrected to
match.

## 2. STACK characterization and route (items 2, 3)

Twelve DR objects (batches `golden/e2e160`, `e2e161`, `e2e163`), summarized in C138. The
route is one bit-packed 16-bit operand in the MAIN prologue `LXI B,dade` (default `0200`)
plus DR's own validation boundary:

* `stack(65536)` and `stack(2*1000)` → DR pass-1 error, **no .REL** → I refuse too
  (ST5, ST10 registered as dr-refuses, the first negatives in the panel whose evidence is
  a numeric-range diagnostic).
* `stack(0)` → `0200`. **Zero means the default, not zero** — the one probe that the
  obvious reading gets wrong.
* Option order is irrelevant (ST9), and a nested RECURSIVE procedure is unaffected (ST15).
* On a procedure-only **module** the option leaves no trace at all: ST7 is byte-identical
  to ST11, the same module without STACK. Not an error, and nowhere else to hide.

Byte parity: ST1-ST4, ST6-ST9, ST11, ST12, ST15 and V1-V6, W5, W6 — 18 new specimens,
gate **405 → 423**, all byte-exact by raw `cmp`.

### The operand is the runtime stack — measured, not inferred

Same source, only the option differing; recursion depth varied (`f(n) = n * f(n-1)`,
the shape whose lowering is byte-exact):

| probe | stack | depth | mine-built output | DR-built output |
|---|---|---|---|---|
| V3 | default 512 | 400 | `Free Space Overwrite` | same |
| V6 | 600 | 400 | `Free Space Overwrite` | same |
| V4 | **2000** | 400 | `depth 400 ok, r = 0` | same |
| V5 | 2000 | 1200 | `Free Space Overwrite` | same |

`Free Space Overwrite` is DR's own PLILIB runtime diagnostic. So the operand selects a
runtime allocation limit, and getting it wrong changes whether a program runs at all.
`f(400)` printing 0 is correct: 400! mod 2^16 = 0, and 16-bit FIXED wraparound is
already pinned. Depth 400 of this frame shape needs >600 and ≤2000 bytes. Every mine-built
`.COM` in this table is byte-identical to the DR-built one.

## 3. C139 — the silent mis-compile (found by accident, highest priority here)

I built the U probes to demonstrate the stack semantically. DR's `U1` printed
`sum(100) = 5050`; my own object printed `sum(100) = 12488` — **a wrong value, rc=0, no
diagnostic**, from `t = n; return (t + sum(n-1));` in a recursive procedure. My compiler
has been accepting this shape and emitting code that computes nonsense.

The guard now refuses it, and the controls show how narrow the defect is:

| shape | status |
|---|---|
| `n * f(n-1)` — MUL, call right | byte-exact [RFACT, FFACT, V1-V6] |
| `f(n-1) + t` — ADD, call **left** | byte-exact [W5] |
| `dummy = f(n-1); return (t + 1)` | byte-exact [W6] |
| `t = 1; return (t + f(n-1))` | diverges [W3] — so it is not about copying the parameter |
| `n + f(n-1)` | diverges [W1] |
| `t = n; return (t + sum(n-1))` | diverges and **wrong value** [U1, W2] |

The correct lowering is unknown: DR does *not* reload the left operand from the cell mine
uses, and guessing which register/shadow cell holds it across the activation is exactly
what produced 12488. Fixing it is its own milestone; U1/W1/W2/W3 are registered as my-gap
negatives so the gate insists on the refusal.

SUB-with-call-on-right is **not** in the guard. My first evidence for it (S1/S6) was
confounded — see next section.

## 4. C140 — why the missing control mattered more than the finding

Every S and C probe I wrote used a callee whose body was `return (n + 2)`. All six of
them diverged, including call-on-left cases, which for a minute looked like evidence that
ADD-with-call-right was *not* the trigger. The cause was C140: DR lowers `x + 2` to
`INX H / INX H`, my lowering emits `XCHG / LXI D,2 / DAD D`, and my documented
peephole-refusal set does not cover that position — so the divergence was value-correct
and unrelated to the call machinery. The control that separated them was C4 (same shape,
callee body `n * f(n-1)`, byte-exact).

The rule this leaves behind: **attribute a divergence to one cause before citing it as
evidence for another.** A probe that shares an unexamined subexpression with five other
probes measures that subexpression five times.

## 5. Gate-found protocol violations (fixed)

Registering ST8/ST13/ST14 as negatives made the panel fail with "wrong refusal", exposing
four production refusal messages written as `[TBD: ...]` — which does **not** contain the
literal `[TBD]` that `run_negatives()` greps for. Those four messages (append layout,
second appended procedure, DR pass-2 UNDEF diag, no-exit main tail) were invisible to the
protocol; all four now read `[TBD]`. The panel is the reason they were caught: a refusal
that cannot be recognized as a refusal is a silent hole.

## 6. Incidents of my own making, recorded because they are the interesting part

1. **A `dict.update` silently deleted five regression checks.** I registered the STACK
   probes as `T1..T15`, but `T4/T6/T7/T9/T12` were already specimens (the e2e11u..y
   series) — `SPECIMENS.update()` replaced them, so five proven byte-parity checks would
   have vanished while the gate went on printing a clean total. The tell was arithmetic:
   405 + 10 ≠ 410. Renamed to `ST*` (DR-side artifact directories keep their `T*` names,
   so the mapping is deliberate and documented in the gate). Namespaces in a regression
   list are not cosmetic, and a total that *looks* self-consistent is not a check.
2. **Shared scratch race, self-inflicted.** I started a second gate while the first was
   still in its output-check phase. `OUT` was a fixed path (`build/e2e`), so both runs
   wrote the same `<name>.REL` and each could compare a golden against the other's
   output. I killed both runs rather than read their numbers, and made `OUT` per-PID.
   (One `pgrep -f`/`pkill -f` in the same command line also matched my own shell and
   killed it — exit 143 — so process management here is by PID.)
3. **A `[:120]` display cap nearly became a documented mechanism** (§1).
4. **Shell-formatting artifacts masquerading as results.** An unquoted `awk`/`tr` pair
   made six probes look like they emitted operand `00010002`; and one spot-check reported
   "E29I DIFFERS" because I hand-built a golden path that did not exist. Both were
   harness bugs, found by looking rather than concluding — and both were redundant with
   the gate, which had already covered those specimens correctly. Ad-hoc comparison loops
   that duplicate a gate entry add error surface, not evidence.

## 7. ACK and ACKTST re-audit (item 4)

With STACK implemented, neither compiles, and their blockers are not STACK:

| file | first refusal (measured) | construct |
|---|---|---|
| ACK | `PUT form not in E2E-3a subset` (line 12) | `put skip list('    ', (decimal(n,4) do n=0 to maxn));` — the **generate form inside PUT LIST**, plus `decimal(x,4)` applied to a call result |
| ACKTST | `PUT EDIT format item form unsampled` | `put edit(...)(skip,a,2(f(2),a),f(6),f(7),a,f(4),a)` — a **counted format group** `2(f(2),a)` |

Both also call an external entry (`stksiz` in ACKTST), and their Ackermann bodies
`return (n+1)` / bare `return (call(...))` sit in the C140/unproven-add territory, so
each needs its own control pass before a route can be priced. The gap-ranking estimate
"2 programs closable by 2 routes each" is withdrawn.

Nearest next steps, in order of what this session made visible: (a) the C139
add-across-a-call lowering — it is a correctness hole, not a feature; (b) the C140
peephole-coverage audit, since a value-correct-but-byte-wrong sequence can hide in any
position my refusal set does not reach; (c) counted PUT EDIT format groups (ACKTST,
FLTPOLY-class payoff); (d) the append-order route that ST8/ST13/ST14 pin DR evidence for.

## 8. Scope kept honest

No ARCH-1 migration and no production extraction: this session's production changes are
the STACK operand + validation, one narrow ADD guard, four refusal-message fixes, the
per-PID scratch path and the linkrun selftest. `ocaml/proto/` is untouched.
