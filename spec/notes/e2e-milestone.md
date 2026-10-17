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
IN (all byte-identical to DR, link+run rc=0): single main procedure;
fixed-BINARY scalar locals; assignment of integer literals (LXI H,imm),
var copies, `+` (inline DAD/XCHG or LXI B/DAD B), `- <const 1..4>` (DCX H),
`*`/`mod` (by-reference RTL ?IM22N/?IMDOP), `/ <const>` (RTL ?ID22N
divisor zero-extend idiom), `a ** <const>` (integer RTL ?IEXOP), and
`<int-literal> ** <const>` (decimal pool: DLDOP/DEXOP/QDI15 + DATA segment,
BCD ceil((p+1)/2), vars shifted by pool total). Gate specimens: P071A,
P071B, P071D, G101/G102/G103/G104/G105/G106.
Still RAISES `[codegen: ... [TBD]]` (deliberate scope cuts, not bugs):
- integer `/ <var>` (no golden evidence).
- decimal / float / char / bit operands, explicit conversions (Q* chains),
  standalone decimal/float literals (pool only built for `**` base today).
- control flow (if/goto/do), PUT/GET/OPEN, arrays, based/struct, nested
  procedures/EXTERNAL linkage, forward-branch CHAIN-ADDR.
See claims C067–C070 and f6/C066 (f6 has zero effect on code/reloc).

## Gates after this milestone
e2e: 6 byte-exact (+ link rc=0). parse 303/0 FAIL. bind 47/47.
rel-roundtrip 276/276. ir 2 byte-exact / 3 struct / 5 gap / 0 FAIL.
test_safety 28/28.

# E2E-3a — PUT LIST char-literal output (milestone, 2026-10-17)

G107 `put list('OK');` and G108 `put skip(1) list('OK');` (DR syntax
experimentally confirmed: both compile clean on the oracle, e2eput2)
lower to .REL **BYTE-IDENTICAL** to DR; linked .COM vs real PLILIB
**byte-identical** to the DR-linked .COM; and the RAW console output
regions are **byte-equal including whitespace/line-endings**:
`OK\r` (G107), `\r\nOK\r` (G108) — skip(1)'s leading CRLF is real
evidence, rc=0 alone never is.

DR lowering (verified from $C + reldump, spec/notes/codegen.md §PUT):
LXI D,0252 ; LXI B,0000 ; CALL ?SYSPR ; [MVI A,n ; CALL ?SKPOP] ;
LXI H,*S(pool) ; MVI A,len ; CALL ?SLCTS ; CALL ?PNCOP ; CALL ?QIOOP ;
then a deferred backpatch triple (SET-LC operand-slot / RELOC code /
SET-LC resume) AFTER the last statement, patching the LXI B operand to
the ?STOPX epilogue address (the ?QIOOP continuation).

Slice guards (negative panel N1..N5 in e2e_gate): GET LIST, DO-wrapping,
PAGE, variable skip count, multi-item LIST — all refuse with [TBD];
plus the DISCARD INVARIANT counter (every non-decl/non-null statement at
any nesting depth must be accounted for by a lowering step).

# E2E-3b — comparisons, IF/ELSE, GOTO+labels (milestone, 2026-10-17)

Six probes (G113, G114, G114B, G114C, G115, G116): .REL byte-exact,
.linked .COM byte-identical vs DR, RAW console output byte-equal
('A B\r', 'G N >\r', 'L N l <\r', 'N Z\r', 'X X X END\r',
'BIG !\r'). G115 runs a backward-GOTO loop with 3 iterations -> branch
relocation (inline RELOC back / CHAIN-ADDR fwd / deferred triples)
proven on executing code, not just static bytes.

Deferred per user directive: DO loops (Sdoto/Sdowhile -> [TBD]),
computed GOTO goto lab(i) -> [TBD] (N6), multi forward-goto-per-label
-> [TBD] (N7, chain form unproven), non-probe-proven comparison forms
(N8/N9). Negative panel now 9/9.

# E2E-3c — CHAR VARYING representation & codegen (milestone, 2026-10-17)

8 probes (V101-V108) answer the representation questions with
byte-parity + runtime console equality [C073]. Length byte at offset 0
(V104 decisive). RTL truncation (V105) and fixed-char padding (V106)
observed on DR-executing bytes, never assumed. Pool-block rule
refined: zero-size literals open the DATA segment (V104/V108 vs V107).
Gate now 25/25 byte-exact, 15 console-checked arms; negative panel 12/12.

# E2E-3d — string concatenation in PUT LIST (milestone, 2026-10-17)

2 probes answered everything the DEMO shape needs [C074]. Chain emits
right-to-left over a source-allocated pool; PUSH PSW guards the SLVTS
only when a stack entry is already live. .REL + .COM + console all
byte-equal. Gate: 27/27, 17 console arms, NEG 16/16.
DEMO put2 shape = C3 exactly. Remaining for DEMO: GET LIST (3e).

# E2E-3e — GET LIST & FULL DEMO ACCEPTANCE (milestone, 2026-10-17)

GET LIST lowered from X201/X202 to byte parity first-try [C075].
DEMO.PLI (original corpus source) -> DEMO.REL byte-identical to the
1980 golden; .COM identical vs fresh DR link; console byte-equal vs
both the fresh DR arm and the banked run2 baseline [C076]. THE
HISTORICAL GOAL IS MET for DEMO. Gate: 30/30, 20 console arms,
NEG 18/18. Next: DO loops; then COPY (file ops = new territory);
broader corpus; $L listing-position fidelity remains cosmetic-only.
