# E2E-16 — the pool layout rule (C152 closed), and DR's `* 0` turning out to be correct

Baseline HEAD 8e47d4a (510/510, 80/80, 13/41). Final: **531 byte-exact / 0 fail, 80/80 negatives,
corpus 13/41 EXACT 0 DIFFERS.**

## 1. C152 was never about the allocator

E2E-15 ended with "dedup fixed the duplicate record but not the size, so the residual rule is
uncharacterised". That framing was wrong in a way worth naming: I had already fixed one of the two
places that compute pool size, and concluded the rule was unknown. The pool has **two independent
accounting paths** — the prescan demand that sets the pool base (and therefore every automatic
variable's address), and the lowering-time allocator that writes the bytes — and only the second one
deduplicated. Summing `String.length` per occurrence at demand and per content at allocation is
exactly a one-byte-per-repeat discrepancy, which is what MB40 showed.

The measured rule (19 probes, `e19src/PL1-PL13`, `PL16-PL21`):

| probe | literals | DR pool bytes | addresses |
|---|---|---|---|
| PL3 | `'W'`, `'V'` | 57 56 | 0000, 0001 |
| PL4 | `'WW'`, `'WW'` | 57 57 | **0000 only** — one 2-byte cell |
| PL5 | `'W'`, `'WW'` | 57 57 57 | 0000..0002 |
| PL6 | `'WW'`,`'W'`,`'WW'` | 3 | 0000:WW 0001:W — first-use order, repeat free |
| PL13 | `'AB'`, `'A'` | 41 42 41 | exact content; a shared prefix does NOT merge |
| PL7/PL9/PL12 | up to 3 occurrences, incl. inside one PUT list | 1 | |
| PL10/PL11/PL18-PL20 | char stores, and store+PUT sharing | 1 | one table across contexts |
| PL17 | `''`, `''` in two PUTs | 0 | **two `SET-LC(data,0000)` records** |

So: one cell per distinct content, first-use order, contiguous from 0 — **plus a real exception**:
the empty literal registers a zero-length block per occurrence. PL11 (two non-empty stores) gets
one block record; PL17 (two empty stores) gets two. That is only visible if you dump the record
stream, and it is the kind of thing a "match the total size" approach would have papered over in
one direction and broken in the other.

**Deliberately not extrapolated.** PL14 (repeated literal in a PUT EDIT) and PL15 (repeated literal
in a concatenation) came back `diag` from DR — no object, no verdict. Concat therefore keeps
per-occurrence accounting on *both* sides: its lowering uses `pool_alloc`, its demand counts
`String.length` per occurrence. If I had deduped the demand for concat without deduping its
allocation, the base would have been smaller than the pool and automatics would have landed on top
of literal bytes — the FDTEST failure mode, silently.

## 2. The invariant that makes the whole panel a drift test

`st.base` (demanded) and `st.pool_next` (allocated) were never compared. Any future mismatch is
either an oversized data area (C152) or variables aliasing constants (FDTEST), and both produce
plausible-looking output. Codegen now refuses if they disagree. All 531 specimens satisfy it —
which is evidence the two paths agree across the whole corpus, not just across the probes I wrote.

## 3. Runtime, because REL parity bought nothing on its own

Twelve dedup-affected programs were linked and run in both DR and mine; all twelve produced
identical output (`golden/e16miner` vs `golden/e16drr`). PL6 is the interesting one: `'WW'` is put
three times from one shared cell interleaved with a distinct `'W'`, and prints
`WW 7 / W 3 / WW 11`. PL25/PL26 specifically test the hazard content dedup creates — two *different*
variables storing the same literal, and a variable re-stored after its literal was put — and both
print correctly in DR and in mine, so the shared cell is read-only rather than aliased [C157].

## 4. C148's `* 0` claim was wrong, and the fix was to run DR's program

I wrote that DR's `n * 0` → `MOV L,H` "does not produce zero, probable DR defect". DR produces zero
for 7, 0, 256, 257, −5 and `0 * n`. The instruction depends on the value DR already knows is in HL
[C156]: nothing if HL is already 0, `MOV L,H` if the high byte is 0, `DCR H` if H == 1, `MOV H,L`
if H > 1 and L == 0, else `LXI H,0000`. n=512 is what proves propagation rather than a structural
peephole: `DCR H` and `MOV H,L` both zero 0100/0200, but only one of them is correct for each, and
choosing between them requires H's value. It is shallow propagation — `k = f(n)` and `k = n` both
fall back to `LXI H,0000`.

The refusal stays, for the right reason now: matching DR here needs a constant-propagation pass I do
not have, and a generic `LXI H,0000` would match six probes and silently differ on four. Whether to
pursue byte-identity on a shape that DR gets *right* is a project decision, not something to slip in
under a defect story.

The discipline point: I reasoned about DR's semantics from one instruction in a listing. The check
that settled it cost one batch run and five minutes of link/run. Any future "DR is wrong" claim
should be required to arrive with an executed DR program attached.

## 5. Instruments, and what they caught immediately

`spec/INVENTORY.txt` + `--update-inventory` [C158]: one committed row per panel entry, gate aborts
on any REMOVAL / ADDITION / SUBSTITUTION. It fired twice during this milestone, both times on my own
edits — first on PL8/PL9, which I had tagged into the wrong golden directory: same entry count,
different reference, invisible to any total. Second, the related change: a registered specimen whose
golden file is missing used to print `SKIP` and score as neither pass nor fail, so those two mistagged
probes were quietly unverified until the 529-vs-510 arithmetic didn't add up. Both are now fatal, and
the panel total (531) matches its components by hand.

## 6. What is still open

- The `char(1)` `len == cap` store (PL10/PL11) and the empty store into a FIXED char (PL16/PL21)
  still refuse for a pre-existing reason unrelated to the pool: DR compiles all four, my store form
  for those capacities is unmeasured. The dedup rule they would have exercised is instead measured by
  PL18-PL20 and PL17, which build.
- Pool rule for string literals inside FORMAT tables / PUT EDIT: unmeasured (PL14 gave no object).
- C146 record placement: untouched by design [Priority 4] — see below.
- Constant propagation, now identified as a real DR capability with a known shallow extent. That is
  a new and much bigger feature than "small-constant multiplication", and it probably reaches other
  observations I have attributed to peepholes (C143's `+k` thresholds, `x * 1` elision).
