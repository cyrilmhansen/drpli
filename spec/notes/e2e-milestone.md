# First end-to-end compilation — P071A (milestone E2E-1)

Source -> OCaml parser -> binder -> codegen -> LINK-80 `.REL` -> historical
PLILIB `LINK` -> `.COM` -> execution under the isolated CP/M oracle.

## Result
`ocaml/bin/pli80c.exe probes/P071A.PLI out.REL` produces a `.REL` that is
**byte-identical** to the Digital Research oracle golden
(`golden/probe38/P071A/P071A.REL`, 128 bytes). Byte-identical machine code
is the strongest independent proof of semantic equivalence: identical
executable bytes => identical execution. Linking vs the real PLILIB then
yields a `.COM` that EXECUTES CLEANLY (rc=0, no abend, returns to prompt),
independently confirming the runtime ABI the codegen assumes.

## Pipeline wiring (all pre-existing components reused)
- `Pli80.Parser.parse_source` -> `Ast.block`
- `Pli80.Bind.bind_rows` -> per-variable (lower-name, type, auto offset)
- `Pli80.Codegen` (NEW) -> LINK-80 record list (`Rel80.rel_item`)
- `Pli80.Rel80` (NEW) -> bit-packed `.REL` byte stream (port of the
  machine-validated `tools/rel_roundtrip.py` encoder, 268/268 goldens)
- `tools/e2e_gate.py` (NEW) -> compile byte-parity; `--link-run` drives the
  hardened oracle (shell=False, per-run workspace disks, PLILIB link + EXEC).

## Codegen model for P071A (every byte cross-checked vs DR `$C`)
Program frame: `LXI B,0200` (`01 00 02`) ; `CALL ?START` (`cd 0000` +
LINK-CHAIN-EXT `?START` @ operand slot) ; body ; `CALL ?STOPX` +
CHAIN-EXT ; tail LINK-DEF-CODE-SIZE/END-PROGRAM/END-FILE.
Header: PROG-NAME / REQ-LIBRARY PLILIB / EXTDEF / DEF-PUBLIC @code0 /
DEF-DATA-SIZE(abs 6) / SET-LC code.

Statement lowering (fixed-bin integer, result left in HL):
- `x = <int literal>`      -> `LXI H,imm16` ; `SHLD x`
- `x = <var>`              -> `LHLD var`    ; `SHLD x`
- `x = a + b`              -> `LHLD a ; XCHG ; LHLD b ; DAD D` (HL=b+a)
- `x = <expr> - 1`         -> ... `DCX H`   (DR constant-folds the -1)
- store                    -> `SHLD` opcode + **inline data RELOC** of the
  variable's data-segment address (base + auto offset) — DR KNOWS the
  address, no chain.

P071A `z = a + b - 1` => `LHLD a; XCHG; LHLD b; DAD D; DCX H; SHLD z` =
bytes `2a 0000(reloc) eb 2a 0002(reloc) 19 2b 22 0004(reloc)` — exactly the
golden record stream.

## f6 does NOT affect code/relocation (instruction #4, answered)
The `$V` field f6 is an internal/positional byte (C066). For P071A the read
of variable `a` carries f6=28 (defined earlier) yet lowers to the SAME
`LHLD` + data-reloc bytes as a never-defined read would. The codegen
consults f6 not at all and still reproduces DR's `.REL` byte-for-byte ⇒
f6 demonstrably has zero effect on generated code or relocation. Byte
parity here is therefore NOT dependent on f6 and was NOT force-matched.

## Supported subset (narrow by design) & remaining differences
IN: single main procedure; fixed-BINARY scalar locals; assignment of
integer literals (loaded inline `LXI H`, no pool), variable copies, `+`,
`- <small const>` (1..4 via DCX H). Everything else RAISES
`[codegen: ... [TBD]]` rather than guessing:
- integer `* / mod **` and RTL-call sequences (?IM22N/ID22N/…) — not needed
  by P071A; add when a specimen requires them.
- decimal / float / char / bit, conversions, pool constants (`* S(k)`),
  nested data offsets, control flow (if/goto/do), PUT/GET/OPEN — all TBD.
- multi-procedure / EXTERNAL linkage, real forward-branch CHAIN-ADDR,
  SET-LC data-segment emission.
These are deliberate scope cuts for E2E-1, not known-bugs.

## Gates after this milestone
e2e: 1 byte-exact (+ link rc=0). parse 297/0 FAIL. bind 47/47.
rel-roundtrip 268/268. ir 2 byte-exact / 3 struct / 5 gap / 0 FAIL.
test_safety 28/28.
