# LINK-80 `.REL` bitstream — PL/I-80 emission model (VALIDATED)

Sources: LINK-80 guide §1.6 + Nestor80 RelocatableFileFormat.md
(authoritative field layouts) + empirical validation: `tools/reldump.py`
decodes, and a re-encoder reproduces P060A / P086H / DEMO `.REL` files
BIT-EXACTLY (content; remainder = zero padding to 128-byte sectors).
Cross-checked against `$C` listings byte-by-byte.

## Stream primitives
| bits | meaning |
|---|---|
| `0` + 8 | absolute data byte, loaded at current LC (chars MSB-first) |
| `1` + `01/10/11` + 16 LE | inline RELOCATABLE value (code/data/common relative) — occupies 2 target bytes at LC |
| `1` + `00` + 4 | link item (types below) |

Link item field presence: types 0–4 = symbol only; 5–7 = value + symbol;
8–14 = value only; 15 = none. Value = 2 seg bits (`00`=abs) + 16 LE.
Symbol = 3-bit count + chars. END-PROGRAM (14) pads to byte boundary.

| type | name | notes |
|---|---|---|
| 0 | EXTDEF | module's own entry name (PL/I emits ONE: the outer proc) |
| 2 | PROG-NAME | program name (PP-prefixed unit name) |
| 3 | REQ-LIBRARY | always `PLILIB` (the guide's 'unused' = library request) |
| 5 | DEF-COMMON-SIZE | (not seen from PL/I) |
| 6 | CHAIN-EXT | value = head slot address, name = `?ROUTINE`; emitted IMMEDIATELY AFTER the CALL operand slot |
| 7 | DEF-PUBLIC | entry symbol @ code 0 |
| 9 | EXT+OFF | not seen |
| 10 | DEF-DATA-SIZE | abs value |
| 11 | SET-LC | switch segment + position (data seg comes FIRST in PL/I output) |
| 12 | CHAIN-ADDR | value = head slot; each slot's 16 bits = next slot addr, 0 ends; linker fills CURRENT LC at the item's emission point. Used for forward `GOTO label` |
| 13 | DEF-CODE-SIZE | abs value (code length) |
| 14 | END-PROGRAM | value abs 0; pads byte boundary |
| 15 | END-FILE | `100 1111` |

## PL/I-80 code-segment emission rules (all validated vs $C)
1. Frame bytes literal (`01 00 02` = LXI B,0200 … `cd` = CALL).
2. Variable/pool operands (`LXI H,*S(k)`, `SHLD Z A(o)` …) = inline
   `data` RELOC values — the compiler KNOWS data addresses (no chain).
3. Backward jumps = inline `code` RELOC (target known).
4. Forward CONDITIONAL branches: opcode + `00 00` data placeholder;
   when the target address becomes known, DR emits the triple
   `SET-LC(code,slot)` + `RELOC code target` + `SET-LC(code,resume)`
   (one triple per branch, NO batching [EX P080H: 4 branches = 4
   triples interleaved exactly at each target]).
5. Forward `GOTO label`: `00 00` placeholder; at the label DR emits
   `CHAIN-ADDR(head=slot)`; multiple refs to one label = chain slots
   pointing at each other?? [single case confirmed P086H; multi pending]
6. RTL calls: operand slot = `00 00` DATA bytes, immediately followed by
   `CHAIN-EXT(?NAME, head=slot)`. Repeat call sites of the same routine
   get SEPARATE chains per statement group [EX DEMO: ?SYSPR heads @13
   and @67 — chains are NOT merged program-wide].
7. $C prints all not-yet-patched slots as `0000` — it is the PRE-LINK
   view (JP 0000 targets above are patched via rules 4–5).

## Decoder/round-trip gate
`tools/reldump.py` (decode) + `tools/rel_roundtrip.py` (decode →
re-encode → bit-exact compare against the original file for every
golden .REL). Run as regression whenever the model changes.

## IRL variant (PLILIB.IRL)
LINK-80 guide §1.7: 128-byte header ([extent,record] of REL start) +
index entries (`?NAME` + \xFE + e/r/b offsets, terminated by count-FF)
+ concatenated REL modules.
