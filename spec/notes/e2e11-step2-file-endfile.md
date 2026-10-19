# E2E-11 step 2 — FILE + ON ENDFILE(SYSIN), FLTPOLY2 accepted

## Acceptance (the standard the user set, all four parts)

FLTPOLY2 (corpus DISK2, `artefacts/FLTPOLY2.PLI`):

| check | result |
|---|---|
| `.REL` vs DR, raw bytes | **identical** (1024 bytes) |
| linked `.COM` vs DR's | **identical** |
| console output, raw bytes | **identical** (158 bytes) |
| transcript | identical except the simulator's wall-clock/mHz footer |
| CPU t-states executed | **identical: 2 356 748** |
| values independently verified | 1.4²+2·2.3+5.67 = 12.23 → `1.2230000E+01`; 2²+2·3+4 = 14 → `1.4000000E+01` |

The t-state equality is the part I find most convincing: it is not a byte
comparison of output but a count of instructions executed, so an ENDFILE path that
diverged in control flow (re-entering the handler, skipping the PUT, terminating
instead of completing the GET) would almost certainly move it.

Oracle provenance got a second confirmation here: my fresh `$L$C$D` compile of a
CRLF-normalised probe copy produced a `.REL` byte-identical to `golden/first` and
`golden/first8080u`, which came from independent earlier runs.  DR is deterministic
and the corpus goldens are real.

**Corpus: 10/41 EXACT** (was 9), 0 DIFFERS, 31 REFUSED.  Also newly byte-exact:
E11A (handler = PUT LIST), E11B (handler = assignment), E11E (GET-only control),
T4 (bare bit condition).  Gate: 353 byte-exact / 0 fail, negatives 64/64.

## What FILE actually is (C120) — and a retraction

`dcl <name> file;` becomes a **named COMMON group**, not DATA:

```
DEF-COMMON-SIZE (abs, 34 + len NAME) NAME ; SEL-COMMON NAME ; SET-LC(common,0)
33 zero bytes | 1 byte = len NAME | the NAME bytes
```

`SYSIN` → 39 bytes, `INF` → 37.  No new bit-level work was needed — `rel80`'s
generic LINK encoder already handled type 1 (name only) and type 5 (ABS value +
name); only the two type codes were missing.  `SEL-COMMON` is re-emitted before
*every* relocation into the group, which is why DR has a second one deep in the
code segment right before `LXI H,SYSIN`.

**I retract C109's "the registration costs 6 bytes of data area".**  I decomposed
E11C's `DATA AREA = 0009` as 6 (ON block) + 1 (bit flag) + 2 (fixed).  The bytes
are actually `00` (static bit cell) | `58 3d` = "X=" | `44 4f 4e 45` = "DONE" | 2
bytes for `x`: 1 static + **6 literal pool** + 2 automatic.  The six was two string
literals I had not looked up, and the sum matching was coincidence.  `ON ENDFILE`
costs ZERO data bytes.  Had I reserved six on the strength of my own claim, every
FILE program would have come out wrong — this is the first thing the implementation
would have broken, and it is a lesson in not trusting an arithmetic decomposition
that identifies no bytes.

## The four pieces that were new

1. **FILE declaration** — accepted in `rows_of`, contributes nothing to DATA, name
   collected for the COMMON emission.  Names longer than 6 chars refuse (DR's
   six-character truncation law is measured for program and entry names, never for
   a COMMON symbol).
2. **`ON ENDFILE(f) <unit>;`** — `LXI H,<cb>` / `MVI A,05` / `CALL ?ONCOP` / `JMP`
   over / handler inline / `RET`.
3. **Bare `if <bit1> then`** — `LDA c` / `ORA A` / `JP skip`, opcode F2.  It tests
   bit 7 through the SIGN flag, which is why it is neither the comparison form
   (`LDA/ANI 80/JNZ`) nor the fixed-bin ident test.  T4 became a positive and N77
   was retired on contact.
4. **Statement-walk coverage for ON handlers** (below) — the real bug of this slice.

## GET needed no work, and that is evidence for C110

My `lower_get` already emitted DR's SYSIN sequence exactly — `LXI D,0290` /
`LXI B,0` / `CALL ?SYSIN` / per item `CALL ?GNVOP`, `JP` to the next item, then
`?QIOOP` and a continuation triple — byte for byte against FLTPOLY2's listing.
More importantly, its *structure* already implements C110's semantics: each item's
`JP` skips the conversion and lands on the next item, so an EOF mid-list leaves every
remaining target unassigned and falls through to the next statement.  No re-entry, no
skipped PUT, no special case.  That is why the interrupted-GET behaviour came out
right without me writing a single line for it — and it is the reason I insisted on the
t-state count rather than just the `.REL`: a skip-the-next-statement implementation
could have matched bytes here too.

## The bug class this slice found: statement walkers that do not descend into ON handlers

`prescan_pool` had no `Son` case, so it never visited the handler.  E11A's handler is
`put list('HANDLED')`, and with the handler invisible to the prescan the pool base
came out as 7 instead of 14.  The symptom was the worst kind: **the DATA bytes were
byte-identical to DR's** (allocation via `pool_alloc` was correct at lowering time),
and only two *relocations* differed.  Five bytes wrong in a 640-byte file, with all
the content present.

The same omission existed in `edit_stmts` — a PUT EDIT inside an ON handler would
have hit `assert false` in `prealloc_fmt_tables` — and in `count_required`, where the
default gave 1 for the ON and 0 for its handler.  That last one agreed numerically on
FLTPOLY2 for the wrong reason (its handler is one statement, so the handler's
increment was being charged to the ON's count); a two-statement handler would have
tripped the DISCARD INVARIANT.  Fixed all three, and restored the increment in the ON
lowering so both sides count the registration and the handler.

Every one of these was discovered by comparing against DR, not by reasoning about the
code.  When I add a statement form, the checklist is now: `prescan_pool`,
`prescan_stmt`, `edit_stmts`, `count_required`, `check_stmt`, `prealloc_fmt_tables`,
`lower_stmt`, and the `pli80deps` walker.

## Refused on purpose

- **`ON ... goto label;`** [E11F → N79].  DR puts `LHLD * / SPHL / CALL ?RECOV` at
  the *target label* (2 hidden automatic bytes) because the handler runs inside
  PLILIB's call context — G115 proves a plain goto emits none, so this is specific
  to the crossing and is a property of the label, not the statement, i.e. non-local.
  Left to compile, E11F produced 335 divergent bytes.
- **`ON ... begin; ... end;`** [E11C/E17A/E16A → N80].  Refuses inside the parser
  with "procedure without name" — an unnamed `BEGIN...END` block handler.  DR
  compiles all three; the goldens exist (`golden/e2e11g/E11C`, `e2e11i/E17A`).
  Not attempted in this slice.
- **Named-stream runtime** (`open`, `get file`, `put file`, `close`) — untouched,
  as agreed.  The declaration side is now done (C120 covers user files too).
- `ON ERROR`, `SIGNAL`, two conditions on one file, `ON ENDFILE` alongside
  `ON ERROR`: unprobed, refuse.

## Harness finding worth recording

The full `--link-run` arm hung for ~40 minutes on R431 (`do i = 0 repeat(i+1);`, an
intentionally infinite probe).  Its cpmsim child outlived the intended timeout and the
parent then blocked on the dead child's pipe.  Compile-tier goldens for infinite-loop
probes are fine; the link/run tier for them is meaningless and needs `--killon`, not a
wall-clock timeout.  I killed the stuck pair and ran the tier restricted to this
slice's specimens.

## Next

Step 3: the `BEGIN...END` handler (N80, blocks E11C/E17A/E16A) and the named-stream
runtime (`?SIOOP`, `?OIOOP`, per-file control blocks in COMMON — C120 already covers
their layout).  Step 4 remains the biggest payoff: `CALL` as a statement, 23 programs.
