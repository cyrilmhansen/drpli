# E2E-31 — NETWORK control flow and register-state reconstruction

Baseline verified before any change: HEAD `c5ecae0` on `main`, pushed, tree clean, `dune build` and
`dune build bin/pli80c.exe` exit 0, gate **756/0 fail, 119/119 negatives, 14/14 divergences, exit 0**,
`ocaml/proto/` untouched.

| | start (c5ecae0) | end |
|---|---|---|
| byte-exact specimens | 756 / 0 fail | **759 / 0 fail** |
| negatives refused | 119 / 119 | 119 / 119 |
| divergence panel | 14 / 14 | **19 / 19** |
| NETWORK first blocker | `find(..) returns(POINTER)` (line 90) | **`ON ENDFILE ... GOTO` (line 50)** |

## P0 — provenance audit (commit 1e8416e, documentation only)

E2E-30's note contained citations that had never been checked. All three were traced to their origin
rather than quietly deleted; see `spec/notes/e2e30-network-graph-integration.md` ("[E2E-31/P0]
Provenance correction"). Summary:

- **"175 lines, 6 procedures" was a misread of `spec/notes/grammar-vs-corpus.md:115`,**
  `| INVESTIGATE | 6 | NETWORK.PLI:175, NETWORK.PLI:179, NETWORK.PLI:185 |` — where **6 is an
  identifier-occurrence count and 175 is a line number**. NETWORK.PLI is 266 lines, and its own header
  (lines 3-5) says "It has 8 internal procedures: SETUP, CONNECT, FIND, PRINT_ALL, PRINT_PATHS,
  SHORTEST_DISTANCE, PRINT_ROUTE, and FREE_ALL."
- **The REVERSE quotations were invented.** I cited a line-29 comment ("reverses the words in a linked
  list by building it in reverse order"), a line-74 banner and commented output at lines 79/84 —
  `artefacts/REVERSE.PLI` is **53 lines**, line 29 is `return;`, and the linked-list phrase exists
  nowhere in the repository except in my own note. Real content: line 2 `/* This program reads a
  sentence and reverses it.     */`, line 24 `sentence = null;`, line 29 `return;`, line 41
  `put skip list('Actually, ');`.
- **The conclusion survived; the evidence was replaced with better evidence.** The executed DR
  transcript `golden/e29dr_runB/REVERSE.output.txt` prints `hello world .` → `Actually,  world hello .`
  and `a b c .` → `Actually,  c b a .`: word-order reversal, words intact. Execution beats a comment.
- Wrong figures corrected in place: BIT stores are `MVI M,80` at **0366** (line 179) and **0437**
  (line 204), `MVI M,00` at **0335** (line 175) and **03D8** (line 196), test spanning **0382-038B**
  (line 185) — the previously cited 0360/036C/03D1 are statement-start `LHLD`s and 03D1 belongs to a
  *false* store. The traversal is **8** `repeat` sites, not six; DR emits **9** null top tests
  (013A/95, 01B3/118, 01EE/121, 031B/172, 037A/183, 03E7/197, 04D9/233, 0563/255, 0579/257), and the
  cited 0382/056B are not among them. "718 instruction lines" counted *listing rows starting with an
  address*, including 39 source-marker rows; **instructions are 679**. `returns(POINTER)` is line 90,
  and the "call site at 011C" is a `MOV M,D` inside `connect`.
- **A false lead was killed before it became a claim.** I "found" that DR accepts `p->flag = true`
  while mine refused it. Compiling the same source under DR gives `NO DCL ?` + `2 ERROR(S) IN PASS 2`
  (`golden/e31p1/E30T7`) — DR refuses it too, because `true`/`false` are not literals in PL/I-80 but
  `%replace` macros (NETWORK lines 9-13 substitute `'1'b`, `'0'b`, citysize=20, infinite=32767). My
  E30B5 already carries that `%replace` and is byte-exact. There is no bit-literal gap.

New claim **C198**: a citation is only evidence if the file was opened in the same session that cites
it, and a number only means something with the quantity it measures.

Method adopted: DR's `$C$S` listing interleaves `  <line> <flag> <addr>  <source>` marker rows, so
address→line attribution is *mechanical*. `/tmp/e31/attribute.py` parses it; that tool produced every
address quoted above and should be reused rather than eyeballing the listing.

## P1 — RETURNS(POINTER), implemented and cleared

Seven probes, DR goldens captured **first** (`golden/e31p2`, `e31p3`, `e31p5`). The ABI:

| part | DR bytes | evidence |
|---|---|---|
| callee `return(p)` | `LHLD <p> / RET` | E31F1 006C/006F; E31F3 (returns a pointer **formal**); NETWORK find 0150/0153 and 01A9/01AC (lines 98, 106) |
| callee `return(null())` | `LXI H,0000 / RET` | E31F2 005B/005E and 005F/0062 — the same shape, so null-as-result needs no separate arm |
| caller | `LXI H,*A(slot) / CALL f / SHLD dst` | E31F1 0006-000C; NETWORK connect line 77, 00D2-00DE |
| caller, varying arg | `LHLD <arg> / SHLD *A(slot) /` then the row above | NETWORK connect line 77 (00D2-00DE) |

The result travels **in HL**; there is no slot write for it. The `CALL` half is the ordinary
function-call lowering already pinned by 26 byte-exact FIXED-return specimens, so admitting `RTptr`
adds no second calling convention [C179]. **Byte-exact: E31F1, E31F3, E31F6.**

**NETWORK's first blocker moved from line 90 to line 50** — `returns(POINTER)` is genuinely cleared
(it was a prescan-time check, so it would still fire if it applied).

**E31F6 corrects E2E-30's matrix row 9.** Bare `null` assigned to a POINTER cell was *already*
byte-exact. E30L5 refused because *my probe was wrong* — it said `repeat(p->dist)` instead of
`repeat(p->link)`. So NETWORK line 239 `q = null;` was never a blocker. Row 9 withdrawn.

**E31F7/E31F7B found a separate binder gap:** `add` as a procedure name is refused by mine as a
declaration conflict while DR accepts it. E31F7C renames it. Unfixed, unregistered — noted for E32.

## P1's real yield: two WRONG-VALUE defect families, both previously mislabelled

The probes were built to characterise a return ABI and instead caught correctness bugs, because I
**linked and ran** them instead of only comparing bytes [E2E-22][C137].

### Family B — based/pointer member reads accumulated in arithmetic

DR brackets each dereference with `PUSH H / POP D / DAD D`, keeping a running value in HL
(E31F4 0035-004F, summing `a->v + b->v + c->v`). Mine omits the bracketing — so mine emits **fewer**
bytes and computes garbage. Executed after LINK 1.31 + PLILIB, against independently known values:

| probe | shape | DR | mine | mine vs DR code bytes |
|---|---|---|---|---|
| E31F4 | `a->v + b->v + c->v` after 3 pointer calls | `s=6` ✓ | **`s=7742`** ✗ | 104 / 106 (**smaller**) |
| **E31F7C** | `do w = head repeat(w->nx) while(w ^= null); s = s + w->v; end;` — **NETWORK's own loop body** | `sum=6` ✓ | **`sum=7768`** ✗ | 120 / 121 (**smaller**) |
| PB20 | `q = q + q` on `BASED(P)` | `q=6` ✓ | **`q=6947`** ✗ | 93 / 94 (smaller) |
| PB4 | `if q > 3 then q = q + 4` on `BASED(P)` | `q=44` ✓ | `q=44` ✓ | 98 / 102 (smaller) |

E31F7C is the important one: that is the accumulation NETWORK performs in `shortest_distance`, so
**NETWORK would compute wrong shortest distances even after it compiles.** The family is not
uniformly wrong (PB4 is right), so the boundary inside it is still undrawn — and `MINE-SMALLER`
separates it cleanly from the register-reuse rows, which are all mine-LARGER. E2E-30's grouping of
PB4/PB20 with the reuse family was therefore wrong and is corrected in place in `spec/DIVERGENT.txt`.

### Family C — a FIXED formal read in a comparison is not dereferenced

A formal holds the **caller's address**, so DR loads the cell and reads through it
(`LHLD M / MOV E,M / INX H / MOV D,M / XCHG`, E31F5 0073-007D for `if i = m`). Mine uses the cell
value directly — it compares against an address.

| probe | shape | DR | mine | bytes |
|---|---|---|---|---|
| **E31F8** | `returns(FIXED)`, `if k = 0 then return(1); return(2);`, called `pick(0)` | `r=1` ✓ | **`r=2`** ✗ | 64/64, **one byte differs** |
| E31F2 | `returns(POINTER)`, `if k = 0` | `r=1` ✓ | `r=1` ✓ | 81/81, 2 bytes differ |
| E31F5 | `if i = m` inside nested DO/IF | — | not run separately | 127/131 |

E31F8 is the sharpest argument this project has for execution over byte comparison: **identical code
size, ONE differing operand byte, wrong printed number.** E31F2 shows the same defect with the value
surviving by luck (both branches return `null()`), which is why "the output matched" is not a
correctness test either. E31F8 reproduces under `RETURNS(FIXED)`, so this predates E2E-31 entirely —
no earlier probe ever compared a formal parameter.

**Neither family is fitted.** Fixing Family C means dereferencing formals in the condition lowering,
and I have no evidence about whether the 756 accepted specimens exercise that path; guessing would be
the trade C179 forbids. Fixing Family B needs to explain why PB4 is right while PB20/E31F4/E31F7C are
not — one probe per direction, not one rule from one direction [C167].

### Why these runtime comparisons count (the C193 check)

Every pair above was verified NON-CIRCULAR before being cited: both the input `.REL` and the linked
`.COM` differ between DR and mine, so running "both" is running two different programs.

| probe | `.REL` differs? | DR `.COM` | mine `.COM` | images differ? |
|---|---|---|---|---|
| E31F8 | yes | 6912 | 6912 | yes |
| PB20 | yes | 7296 | 7296 | yes |
| E31F7C | yes | 7040 | 7040 | yes |
| E31F4 | yes | 7040 | 7040 | yes |
| PB4 | yes | 7296 | 7296 | yes |

Equal `.COM` sizes are expected (the divergences are inside the code, and LINK pads to record
boundaries); `cmp` says the bytes differ.  This is the opposite of E2E-29's REVERSE comparison, where
byte-identical `.REL` made identical output a foregone conclusion [C137][C193] -- and it is why the
E30G1 runtime agreement recorded in E2E-30 is worth less than these: there the images differ but the
result happened to agree, whereas here the images differ and the results DISAGREE, which is the case
that actually discriminates.

## P2 — ON ENDFILE / REVERT: the handler layout, resolved from a linked image

Not implemented. What was done instead is more useful: the ambiguity in DR's emitted code was settled
by **linking DR's own E30E2 object and reading the patched addresses**
(`golden/e31e2dr/E30E2.COM`).

In the `$C$S` listing, `on endfile(sysin) goto eof;` looks impossible — two consecutive inline
`JMP 0000` would fall into neither. After linking (E30E2, main-block-relative):

```
0133  21 4A 1B     LXI  H,1B4A      ; HL := &SYSIN
0136  3E 05        MVI  A,05        ; condition code 5 = ENDFILE
0138  CD 17 18     CALL 1817        ; ?ONCOP
013B  C3 41 01     JMP  0141        ; normal path: jump OVER the handler stub
013E  C3 66 01     JMP  0166        ; HANDLER STUB (skipped in normal flow)
0141  11 90 02     LXI  D,0290      ; ...which lands exactly on the next real instruction
```

So `?ONCOP` registers the byte immediately after the continue-JMP as the handler, and the first JMP
steps over it. The stub target 0166 is the recovery prologue:

```
0166  2A 5E 1C     LHLD  1C5E       ; the hidden 2-byte saved-SP cell
0169  F9           SPHL             ; restore the stack
016A  CD D1 13     CALL  13D1       ; ?RECOV
016D  21 4A 1B     LXI   H,1B4A     ; &SYSIN again
0170  3E 05        MVI   A,05
0172  CD 8B 18     CALL  188B       ; ?REVOP  -- the handler reverts ITSELF on transfer
0175  CD 1B 14     CALL  141B       ; the label's block
```

Three conclusions for whoever implements this, each of which my compiler's refusal already names but
now has addresses behind it: (1) registration (`?ONCOP`), the jump-over, the stub, and the label
transfer are **four distinct emissions**, not one; (2) the handler prologue is
`LHLD <hidden cell> / SPHL / CALL ?RECOV` and needs a **2-byte hidden cell per ON-unit**; (3) DR
emits `?REVOP` **inside** the transfer path, so `ON ENDFILE ... GOTO` implicitly reverts — which is
why NETWORK's explicit `eol: revert endfile(sysin)` (line 151) still emits its own
`LXI H,SYSIN / MVI A,05 / CALL ?REVOP` at 02F8 and then `JMP 0268`.

NETWORK's sites: `?ONCOP` at 0027, 025A, 02A4 (lines 50, 140, 145) and `?REVOP` at 02F8 (line 151),
all with `LXI H,SYSIN` + `MVI A,05`. Labels: `eof:` at lines 59 and 153, `eol:` at 151. A run driven
to immediate EOF **timed out rather than transferring** — the simulator's console does not deliver a
CP/M EOF that way, so real EOF behaviour still needs a different input mechanism (see E32 item 4).

## P3 — divergence classification (research; no optimizer change made)

The task's warning was correct: the 14 rows were **not** one cause. Measured directions:

| family | mine vs DR bytes | executed value | members |
|---|---|---|---|
| **A. register reuse (HL/DE elision)** | mine **LARGER** | untested individually | PB4? no — see B. PB20/E27S2/E28N7/O1/O2/O4/E29X3/E30L1-L4/E30B2/E30G1 (the reuse ones) |
| **B. based-read arithmetic accumulation** | mine **SMALLER** | **PB20, E31F4, E31F7C wrong**; PB4 right | PB4, PB20, E31F4, E31F7C |
| **C. formal not dereferenced in comparison** | ~equal (1-2 bytes) | **E31F8 wrong**; E31F2 right by luck | E31F2, E31F5, E31F8 |
| unresolved | E30B2/L2/L3/L4/G1 shapes were recorded as A | **not executed individually** | E30B2, E30L2, E30L3, E30L4, E30G1 |

The falsifiable starting rules, both taken from DR's own bytes rather than assumed:
*DE reuse*: DR reuses a loaded DE unless an emitted instruction writes DE — E31F5/NETWORK line 179
(`LXI D,0015` at 0358 then `INX D / INX D / DAD D` at 0363-0365, with `LHLD P / XRA A / MOV M,A /
INX H` in between, none of which writes DE). *HL constant reuse*: E30L1 becomes byte-identical when
one `LXI H,0000` is deleted, so DR reuses HL=0 across `head = null;` and `n = 0;`.

Both are still single-direction evidence. Each needs a disconfirming probe before implementation, and
the existing 756 specimens are the safety net, not the justification.

## E32 priorities (ordered, each with its evidence already in hand)

1. **Family C (formal dereference)** — a wrong-value bug, one-byte symptom, and the narrowest fix.
   First probe in each direction: a fixed formal compared in a condition where the *correct* answer
   differs between dereferenced and not (E31F8 does this), and the same shape inside one of the
   existing byte-exact specimens to see whether the 756 would move. Do not touch the condition
   lowering until the second is known.
2. **Family B (based-read accumulation)** — wrong values on NETWORK's own loop body. Needs the
   PB4-vs-PB20 boundary drawn: what makes one correct. Then DR's `PUSH H / POP D / DAD D` bracket
   becomes a lowering rule, not a guess.
3. **ON ENDFILE/REVERT with GOTO** — layout above is complete enough to implement: 4 emissions,
   hidden 2-byte cell, auto-`?REVOP`. This is NETWORK's actual first blocker today.
4. **Real EOF execution** — settle how to deliver CP/M EOF to `?SYSIN` under cpmsim (a `^Z` line, a
   redirected file, or `RMAC`-style device input) so that ENDFILE transfer can be *observed*, not
   inferred. Until then, ON-handler goldens are compile-side evidence only.
5. **`add` as a procedure name** — binder conflict refusal where DR accepts (E31F7 vs E31F7C).
6. Then unchanged NETWORK: it refuses at line 50 today; rows 10-12 of the E30 matrix are the
   hypothesis list for what comes after, and each must be re-verified from actual compiler output.

## Reproducing

```
python3 oracle/batch.py E31F1 E31F2 E31F3 E31F4 E31F5 E31F6 --tag e31p2 --switches '$L$D$C$S'
python3 oracle/batch.py E31F8 --tag e31p3 --switches '$L$D$C$S'      # RETURNS(FIXED) control
python3 oracle/batch.py E31F9 --tag e31p3 --switches '$L$D$C$S'
python3 oracle/batch.py E31F7C --tag e31p5 --switches '$L$D$C$S'     # NETWORK loop shape
python3 /tmp/e31/attribute.py                        # address -> NETWORK line, mechanically
mkdir -p golden/e31f4_mine/E31F4 && cp /tmp/e31/E31F4.REL golden/e31f4_mine/E31F4/   # + DR .PRN
python3 oracle/linkrun.py link --tag e31f4_mine --names E31F4 --out e31f4_mine --reuse
python3 oracle/linkrun.py run  --tag e31f4_mine --out e31f4_mine --names E31F4 --reuse
```
