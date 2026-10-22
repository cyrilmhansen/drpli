# E2E-28 — nested-procedure placement: the branch-over, and REVERSE's first blocker cleared

Baseline `19d6f6c` (E2E-27 tip): 694 byte-exact / 0 fail, 128/128 negatives, 3 divergences, exit 0.
ARCH-1 unchanged (see the git-diff check in §5).

## 0. P0 — two documentary corrections to the E2E-27 note

**(a) The REVERSE/NETWORK "excerpts" in `e2e27-...md` §0 were mine, not the corpus's.** They are
replaced by verbatim quotations with line numbers. What was actually wrong in them:

| my pseudo-excerpt | the real source |
|---|---|
| `declare head pointer, newnode pointer, sentence pointer;` | REVERSE has no `head` at all; it declares `sentence pointer` in the same `declare` as the structure (lines 6-10) |
| `newnode->next = null();` | REVERSE line 31 is `newnode->next = sentence;` |
| `free head->node;` | REVERSE line 46 is `free p->wordnode;` |
| `declare cityptr pointer, countryptr pointer;` | NETWORK's pointer is `city_head` (line 29); `cityptr`/`countryptr` do not occur |
| `2 city_name char(30) varying, 2 population dec(9), 3 country based(cityptr)` | NETWORK lines 17-22 are `city_name character(citysize) varying, total_distance fixed, investigate bit, city_list pointer, route_head pointer`. `country`, `population`, `dec(9)`, `char(40)` occur **zero** times in the file; `citysize` is a `%replace` macro = 20 (line 11) |
| `cityptr->city_name = 'X';` | NETWORK line 101 is `p->city_name  = city;` |

The habit is the same one as the PROVENANCE audit and C185: writing plausible evidence in the shape
of a quotation. Verbatim plus line numbers is cheaper to check and harder to get wrong.

**(b) LN1's data figures were two different measurements presented as if they disagreed.** All four
numbers are now labelled in that note:

| figure | value | quantity | instrument |
|---|---|---|---|
| `.REL` file | 640 bytes | object padded to 128-byte sectors | `ls` (my stdout prints this as `(%d bytes`) |
| code | 256 = `0100` | CODE segment bytes | DR `CODE SIZE = 0100` = reldump `LINK-DEF-CODE-SIZE` = my `code=256` |
| data area | 32 = `0020` | whole DATA segment = variables **plus** pool | DR `DATA AREA = 0020` = reldump `LINK-DEF-DATA-SIZE abs 0020` |
| automatic storage | 8 | declared variables only (`head`,`p`,`q`,`z` × 2) | DR `BLOCK AT LINE 2, AUTO STORAGE 8 BYTES` = my `data=8` (`rows_of`'s variable-area figure) |

32 = 8 + 24 (the four `put` literals). Same split on ST1 (area 4 / auto 2) and REVERSE (area 59 / sum
of block autos 37). The "384-byte `.REL`" in that note was also wrong — 384 is ST2's file size, not
LN1's 640.

## 1. What the two refusals claimed, and what DR actually does

`codegen.ml` carried, as DR layout facts:

* `main-block statement after an appended procedure [TBD] (unproven DR append layout)` — justified by
  "every golden lowers ALL procedures AFTER every main-block statement";
* `second appended procedure after a tail guard [TBD] unproven, no multi-procedure golden` — one
  guard per program;
* plus `RETURN without value [TBD]`.

ST13's own DR listing (`golden/e2e324d/ST13/ST13.PRN`) contradicts the first:

```
   7 c 0031    free head->node;
       0031       LHLD HEAD A(0002)
       0034       CALL ?FREOP
   8 c 0037  fill: procedure;
       0037       JMP  0000            <-- branch-over, at the declaration
       003A       LXI  H,0004          <-- fill's body
       ...
       0055       RET
       0038       ==== 0056            <-- operand resolves to 0056
  13 c 0056   stop;
       0056       CALL ?STOPX          <-- main's statement AFTER the body
```

The measured model, from N1-N5/N7/N8/N10 and REVERSE:

1. **Every nested-procedure declaration inside a main block emits its own 3-byte `C3 00 00`.** The
   operand is *where main's emission resumes after that body*: N4 `@000C -> 0016` (the `w = 7`), N3
   `@0012 -> 0020` (the next declaration) and `@0020 -> 002E` (the epilogue). The old "chained to the
   epilogue CALL" reading was correct for all 694 earlier specimens **because in all of them the
   resumption point was the epilogue**. That is C185's error shape one layer down: a convention in my
   corpus promoted into a law about the language.
2. **No resumption point → no branch.** REVERSE's main ends in `do while('1'b)` whose tail is
   `JMP 0006`; read_it begins at 001A with its first statement and write_it at 0091 — neither has a
   `JMP`. N3 (which has a reachable epilogue) has two.
3. **A nested procedure gets no prologue.** REVERSE's read_it starts directly with `LXI H,0000 / SHLD
   SENTENCE`, where SENTENCE `A(0016)` is the *enclosing* block's cell: lexical visibility is a plain
   absolute reference, no descriptor. N6 shows a same-named local is a distinct cell (outer `W
   A(000C)`, inner `W A(000E)`), so the binder's scope chain was already right.
4. **Body ends with `RET` when control can fall through, and without it when it cannot** — REVERSE's
   read_it (always-loop tail) emits no RET; write_it does at 010F.
5. **Bare `RETURN;` emits `RET` alone and emission continues**: N7 `RET @003A` then `w = 4 @003B`;
   REVERSE line 29 `RET @0064` inside read_it.
6. **There is no dead-code suppression after a straight-line `STOP`.** N8 emits `w = 2`, a PUT and a
   second `CALL ?STOPX` after its first stop; N10 does the same inside a procedure body; both are
   byte-exact. What my earlier probes actually hit was the *consecutive* `stop;` case — two in a row
   emit one CALL — which was an artifact of my probe template, not a DR rule.

## 2. Results

Byte-exact and registered: **E28N1, E28N2, E28N3, E28N4, E28N5, E28N6, E28N8, E28N10** (keys prefixed
because `N4`-`N8` are already E2E-16 panel entries — checked against `spec/INVENTORY.txt` this time,
not against registration syntax, which is what let `ST1`/`S8` slip through in E2E-27).
**E27S13 (ST13) is promoted from the negative panel to a specimen**: it refuses nothing now and is
byte-exact against `golden/e2e324d/ST13/ST13.REL`, which is the C154 condition for removing a
negative — its behaviour has a golden of its own.

Runtime, from `LINK 1.31` + cpmsim, each program linked twice (my `.REL` and DR's):

```
N1  mine: a=         2      DR: a=         2
N4  mine: z=         7      DR: z=         7
```

N4 is the discriminator that matters. It never calls `sub`, so if the branch-over were absent or
mis-aimed, main would fall into the body, run `w = 2`, and print 2; it prints 7. N1 is the converse
control: the forward CALL reaches the body and 2 is what the body stored. Together they show the
branch is emitted, aimed correctly, *and* that the body is still reachable through the CALL.
Transcripts: `golden/e28my_r`, `golden/e28my_r4`, `golden/e28dr_r`, `golden/e28dr_r4`.

## 3. E28N7 — registered as a divergence, and attributed away from procedures

`mine code=59 data=4 | DR code=57 data=4 | ndiff=35 | first byte 176 | 256/256`. The procedure layout
is fully reproduced (branch-over `@0031`, body, bare `RET @003A`, continued emission, trailing `RET
@003F`, epilogue `@0040`). The difference is one store: after `w = 3`, DR lowers `w = 4` as
`INX H / SHLD W` — reusing the HL that `LXI H,0003` left behind, HL surviving an intervening `RET` —
where mine emits `LXI H,0004 / SHLD W`. That is a literal-store route I have not characterised across
samples; fitting it would touch the shared constant-store path under every accepted specimen, so it is
pinned in `spec/DIVERGENT.txt` instead [C168, C179]. The `INX H` shape also explains why N7's data
area matches exactly: it is purely a code-shape difference.

## 4. REVERSE after this milestone

Blocker (1) — nested-procedure statement placement — is **cleared**: ST13 byte-exact, N1-N6
byte-exact, REVERSE's own read_it/write_it shapes reproduced. REVERSE now stops at

```
codegen: BASED structure member word of type CHAR(30) VARYING at record offset 0 is unsampled [TBD]
```

i.e. blocker (2), CHARACTER VARYING members. Its listing does measure that route now, so the next
milestone starts from evidence rather than guesses: `word = newword` → `LHLD SENTENCE / LXI D,
NEWWORD / MVI A,1E / CALL ?SMVVM`; `put list(word)` → `LHLD SENTENCE / CALL ?SLVTS`; `get
list(newword)` → `LXI D,0290 / LXI B,0000 / CALL ?SYSIN / CALL ?GNVOP / JP ...` with `?SSVFS` on the
input side; and member addressing at a large offset uses `LHLD <qual> / LXI D,<offset> / DAD D`
(`001F` = 31 = `next`'s offset) where my probes only ever exercised `INX H` × 2.

Two further REVERSE/NETWORK blockers this milestone made concrete rather than assumed:

* REVERSE line 13 `if sentence = null then` and line 42 `do while (sentence ^= null)` compare a
  pointer against **bare `null`** (no call parentheses). E28N9 shows that even `if w = 1 then stop;`
  stops at my E2E-3b condition subset, so this is the condition-form gap, not the pointer gap — and
  N9's listing shows DR emitting the compare as `LHLD W / DCX H / MOV A,H / ORA L / JNZ` with the
  `CALL ?STOPX` after it.
* REVERSE's `free p->wordnode` (`LHLD P / CALL ?FREOP`) and `sentence = next` (`LHLD SENTENCE / LXI
  D,001F / DAD D / MOV E,M / INX H / MOV D,M / XCHG / SHLD SENTENCE`) are unqualified member access
  from inside a nested procedure — REVERSE-line 45 shape — which my binder resolves through the
  enclosing block's pointer. Not yet probed at offset > 2 by me.

## 5. Gate, ARCH-1, and what was not done

Gate after this milestone: see `spec/INVENTORY.txt` (703 entries) and the run summary in the commit
message — the number is quoted from the gate's own output, not written down in advance.

ARCH-1 checked the way that actually answers the question: `git diff 19d6f6c -- ocaml/proto` lists no
files. The aggregate-md5-over-`find` instrument that alarmed me in E2E-27 is not used.

Deliberately not done: CHARACTER VARYING / BIT / CHAR / DECIMAL structure members (ST5/ST6/ST7, and
REVERSE's blocker 2); the `INX H` literal-successor route (E28N7, pinned); `LXI D,<offset> / DAD D`
member addressing at offsets beyond the sampled `INX H` cases; `repeat(...) while(...)` and chained
`->` qualification (NETWORK lines 96, 124); `%replace` (NETWORK line 9 — REVERSE's structure decoding
shows the macro value 20 for citysize is *already* handled where it appears in a declaration); GET
stream input; the E2E-3b condition subset; and NETWORK as a whole, which remains a specification with
no DR `.REL` oracle.
