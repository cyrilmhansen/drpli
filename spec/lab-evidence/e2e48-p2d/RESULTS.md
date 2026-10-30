# E2E-48/P2d — RESULTS (round 4, E48D1..E48D10)

## 0. Lineage (both oracle runs are evidence)

- Probes + predictions committed BEFORE any oracle call at `60cf463` (tag planned `e48p2d`).
- **Run 1 (`golden/e48p2d/`, committed `67bf83c`): 0 ok / 10, mechanical failure.** Each probe
  carried its purpose comment as ONE line of 179..317 columns; DR truncates source lines past
  column 72 (`e2e42-p2b` §6 law, re-confirmed), every `*/` was cut, every comment ran to EOF,
  every probe died `UNEXPECTED EOF` with no `.REL`. No prediction was scored from run 1.
- Amendment `60a2c06` (BEFORE run 2): `mkprobes.py` wraps comments ≤71 cols; code lines proven
  byte-identical to `60cf463` by comment-stripped `cmp`; predictions P-D1..P-D10 stand;
  `BASELINE-MINE-WRAPPED.txt` shows my verdicts unchanged (7 refusals / 3 compiles).
- **Run 2 (`golden/e48p2db/`, committed with this file): 10 ok / 10.** All probes ACCEPTED,
  all `.REL` present. Judged on `.REL` bytes only (`$L$D`), never `.PRN` sizes.

## 1. Prediction vs verdict (every MISS kept)

| id | predicted | measured verdict | score |
|---|---|---|---|
| P-D1 | ACCEPTS; `?SLVTS` head, w0E50, cell `02 41 42 20x11` in place, pool `58`, DEF-DATA 0012 | exactly that (E46F5's bytes with the D1 module name) | **HIT** |
| P-D2 | ACCEPTS; `?SLVTS` on INPUT side, w0E90, class-invariant | `21 *D(0000) / CD ?SLVTS / 40 / C5 / 33 / 21 0E90` — yes | **HIT** |
| P-D3 | ACCEPTS; `21 *D(cell) / 3E 08 / ?SLCTS`, cell `41 42 20x6` in place, pool `58`, DATA 000B | exactly that; TITLE MVI A is the DECLARED 8 | **HIT** |
| P-D4 | ACCEPTS; cell `00`+ten `20` = 11 in place, not pooled; PUT read `?SLVTS` | cell 0000..000A in place; read `21 *D(0000) / CD ?SLVTS / CD ?PNCOP`; DATA total 000F = 11+2(`'S='`)+2(`k` auto cell, §2.7) | **HIT** |
| P-D5 | ACCEPTS; empty FIXED cell = five `20` in place | 0000..0004 = `20x5`; read `3E 05 / ?SLCTS` (declared length); DATA 0009 incl. k | **HIT** |
| P-D6 | ACCEPTS; `'CD'` POOLED (DATA grows); "route is the ordinary fixed-char move" | ACCEPTS, `'CD'` IS pooled at 0004 — but the route is NEW: `CALL ?SMCCM` (§2.1), not a move I had seen | **HIT (verdict+pool) / MISS (route wording)** |
| P-D7 | ACCEPTS; "LEADING LENGTH BYTE is rewritten (cell `03 44 45 …`)" and literal pooled | ACCEPTS, `'CDE'` pooled (000C..000E); but the DATA image KEEPS the initial `02 41 42 20x8`; the store is RUNTIME code `?SMCVM` (§2.2) — no compile-time length rewrite exists | **HIT (accept+pool) / MISS (image rewrite — a conceptual error, falsified)** |
| P-D8 | ACCEPTS; `k=2`→DCX×2, `k=3`→DCX×3 with TEST's ≤3 threshold, tail `D6 01 / 9F / 32` | code 0006: `2A *D(k) / 2B 2B / 7C / B5 / D6 01 / 9F / 32 *D(b)`; 0013: same with `2B 2B 2B` | **HIT** |
| P-D9 | ACCEPTS; bit item `3A/06 01/?QB08C/?PNBOP` then literal's own chain + ONE `?QIOOP` | exactly that (000F..0027): non-final bit item ACCEPTED, its own PNBOP tail, then `21/3E 01/?SLCTS/?PNCOP`, one final QIOOP | **HIT** |
| P-D10 | ACCEPTS; literal-LEFT TEST = `21 *D(member) / 11 *S(lit) / 06 len / ?SCCVM` + `C2` skip to NEXT stmt | code 0013: `21 *D(0004) / 11 *D(0000) / 06 02 / CD ?SCCVM / C2 fill→0027` | **HIT** |

## 2. Laws read out of the `.REL` records

1. **STORE into STATIC CHARACTER (FIXED)** (D6 0006): `LXI H,*D(cell) / LXI D,*D(pool) /
   MVI A,declared-extent / MVI B,literal-len / CALL ?SMCCM` — 10 bytes. The literal source IS
   pooled (fresh cell at first free DATA byte); my named refusal is now a `my-gap`.
2. **STORE into STATIC CHARACTER VARYING** (D7 0006): same head, `MVI A,extent(0A) /
   MVI B,src-len(03) / CALL ?SMCVM`. The DATA image keeps the INITIAL cell (`02 41 42 20x8`);
   any length-byte rewrite is runtime behaviour, [TBD] until a link-run measures it.
   D10 0006 shows the AUTOMATIC varying member store uses the same `?SMCVM` shape (A=0E extent).
3. **EMPTY `initial('')`**: VARYING static → `00` + extent blanks IN PLACE (isolates EXPR2's
   000F law); FIXED static → extent blanks, no length byte (new half of the law). PUT reads
   them by `?SLVTS` / `3E,extent ?SLCTS` respectively.
4. **TITLE with a STATIC operand is class-invariant** both output (D1 = E46F5 bytes) and input
   (D2, w0E90). The storage class changes no code byte except the operand address.
5. **Store materialiser, |c| ∈ {2,3}** (D8): `LHLD k / DCX H ×|c| / MOV A,H / ORA L / D6 01 / 9F /
   STA cell` — the ≤3 `DCX H` threshold is ROUTE-INDEPENDENT (same as TEST [C143]). Closes the
   [C310] [TBD]. `k = 1` in a store remains unmeasured.
6. **Non-final BIT(1) PUT item is ACCEPTED** (D9) — my refusal's premise ("no DR witness") is
   falsified. Bit item keeps its OWN `?PNBOP` tail; the following literal chain follows; exactly
   one `?QIOOP` closes the list (one-tail-per-item [C313] holds in the non-final position).
7. **DATA layout slack is the automatics** (D1/D3/D4/D5 "unexplained +2"): DATA = static cells
   (inits in place) → pool literals in code order → automatic variables zero-filled above.
   `LINK-SET-LC data N` with no following DATA record marks the hole. Confirms E48A6's 0027
   arithmetic; not a padding law.
8. **Member-as-RIGHT in TEST** takes the literal-LEFT `?SCCVM` orientation unchanged (D10):
   orientation law is POSITION-independent within the compare — `LXI H` always the internal cell.

## 3. What this round did NOT measure

- Runtime semantics (length rewrite of §2.2; what an empty varying PUT actually prints).
- `k = 1` and negative `c` in the store ladder; `^(cond)` store beyond `^(k = 0)`.
- BIT(1) item behind a file attach (`put file(f) list(b, …)`); BASED member in a condition store.
- STATIC CHARACTER store with src longer than the extent; INITIAL longer than the extent.
- No `spec/RUNTIME.txt` rows may come from this round (byte-tier evidence only).
