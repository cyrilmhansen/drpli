# E2E-34 P0–P2 — ON ... GOTO, the recovery pad, the hidden saved-SP cell, REVERT

Gate at this commit: **790 byte-exact / 0 fail, 120/120 negatives refused, 16/16 divergences
as recorded, 12/12 runtime witnesses, exit 0** (baseline entering the milestone was
780 / 121 / 16 / 12).  ARCH-1 (`ocaml/proto/`) untouched.

## P0 — six characterization probes, DR-compiled first

`oracle/batch.py E34A1..E34A7 --tag e34a --switches '$L$D$C$S'` → all `status: ok`
(`/tmp/e34/dr.log`).  Each probe answers exactly one question:

| probe | question | what the DR artifact says |
|---|---|---|
| A1 | statement-handler ON inside a nested procedure | `CALL ?OFCOP / RET` at the proc tail; **no cell, no DAD SP, no pad, no RECOV** |
| A2 | two `ON ... GOTO` to the SAME label | ONCOP×2, **one** pad, **one** cell, **one** SEL-COMMON |
| A3 | `ON/GOTO` + plain `GOTO` to the same label | pad chain (`LINK-SET-LC code 001C`) and plain-goto chain (`@2072 LINK-CHAIN-ADDR code 0042`) are separate records |
| A4 | `ON ... GOTO` to a label defined EARLIER | pad still immediately before the body (`LHLD/SPHL/CALL ?RECOV` at 0x13, body at 0x1a); handler `JMP SKIP` = inline RELOC code 0x13 |
| A5 | plain backward `GOTO` to a PADDED label | shares RELOC code 0x13 with the handler's JMP → **the pad is the label's entry point** |
| A6 | `ON ... GOTO` inside a nested procedure | cell belongs to the procedure's block; main gets none |
| A7 | nested proc with a formal + `ON/GOTO` | SP save is emitted **after** the formal pointer-copy prologue |
| A8 | `ON ... GOTO` inside a nested **DO**-block | no section of its own: cell still 0019, DATA AREA 001B — identical to writing the unit at main level (byte-exact) |
| A9 | `ON ... GOTO` inside a nested unnamed **BEGIN**-block | DR compiles it, cell 0019 = the **outer** block's, pad at 003B; mine still refuses with the pre-existing "procedure without name [TBD]" |

Reversed the REVERSE listing too: procedures with no ON-unit have no OFCOP, so OFCOP is
ON-specific (but *not* GOTO-form-specific — see A1).

## P1 — the implementation, one encoder per piece

`ocaml/lib/bind.ml`
* `on_facts { of_any; of_goto; of_labels }` + `on_stmt`: **one** scan of a block's statements
  (descending DO/IF/BEGIN, stopping at `Sproc`) that answers all three questions at once —
  any ON-unit, any GOTO-form ON-unit, and the label set they target.  Demand and layout
  share it, so they cannot drift [C179].
* `section2` gains `top : bool` and allocates the hidden 2-byte saved-SP cell **only when
  `of_goto`**, after named autos and before anonymous call temps.  A block with only
  statement handlers is laid out exactly as before (E32E1 unchanged, 780 → 789 with zero
  regressions).
* `proc_layout.pl_on`, `proc_layout.pl_sp_cell`, `prog_layout.pl_top_cell`.

`ocaml/lib/codegen.ml`
* `op_dad_sp = 0x39` (single byte; C207) and `op_sphl = 0xf9`.
* `lblstate` gains `on_pads`, `sp_cell`, `on_any`, swapped/restored in `lower_proc` exactly as
  `st.v` and `st.arrays` are — the pad set is a property of a **label**, so it lives with the
  label state.
* `on_reg_prefix` — THE one authority for `LXI H,<COMMON> / MVI A,05` shared by ON and REVERT
  [C202].  It now emits `LINK-SEL-COMMON` **only when the selected group changes** (C210).
* `emit_sp_save` = `LXI H,0000 / DAD SP / SHLD * A(cell)` (8 bytes) at block entry.
* `emit_pad` = `LHLD *A(cell) / SPHL / CALL ?RECOV` (**7** bytes, correcting C208's "9").
* `label_def` — the single site that emits any label's code (statement labels *and* procedure
  entry labels).  It emits the pad first when the label is ON/GOTO-targeted, resolves **all**
  pending forward sites to the pad address, and registers `ls.labs` at the pad address.  That
  one registration is why plain GOTOs, ON stubs, forward and backward jumps all land on the pad
  with no special case anywhere (C209(b)).
* `fwd_ref` keeps the per-label pending-site list; resolution is now N sites → one
  `LINK-CHAIN-ADDR` on the last operand word, the model already proven for forward CALLs
  [C123].  The old "multiple forward GOTO unproven [TBD]" refusal is gone, replaced by N7MFWD
  as a byte-exact specimen.
* `Son` dispatch splits: a direct `GOTO` handler emits registration + continue-JMP + pad-JMP and
  **no inline code and no RET**; a statement handler keeps the inline body + `RET`.
  The GOTO branch counts the absorbed handler in `st.lowered` (else the DISCARD INVARIANT reads
  16 required / 14 lowered).
* `Srevert` arm: `on_reg_prefix` + `CALL ?REVOP`.
* Nested-proc tail `CALL ?OFCOP` when the block has any ON-unit.

## Byte-exact at this point

E32E1 (statement handler, main) · E32E2 (2 GOTO-form ONs, 2 pads, 1 cell, REVERT, GET chain,
640 B) · E34A2 · E34A3 · E34A4 · E34A5 · E34A6 · E34A7 · E34A8 · N7MFWD · N79GOTO · E34B1.

## Panel moves

* **N7_MULTI_FWD** and **N79_ON_HANDLER_GOTO** removed from the negatives — not deleted,
  promoted: each now has a DR golden of its own [E2E-32 rule].  The oracle rejects names longer
  than 8 characters, so the goldens are `golden/e34b/N7MFWD` and `golden/e34b/N79GOTO`, same
  content with the program name shortened.
* 7 E34A probes + those 3 = **+10 specimens**; 121 − 2 + 1 = **120 negatives** (the +1 is
  E34A9_BEGIN_BLOCK_ONGOTO, added below as the tripwire for a real latent hole).
* `spec/INVENTORY.txt` 905 → 912 lines via `--update-inventory`; the diff (2 removed, 9 added)
  was reviewed before the re-run.

## The DATA-segment defect this uncovered

`st.pool <> [] || statics.sy_files <> []` guarded the opening `SET-LC(data,0000)`.  The
second disjunct came from E2E-11 step 2 (commit `0e4bc91`) and FLTPOLY2, which has 44
DATA-segment bytes — so the clause was **redundant in the only specimen that justified it**.
It became reachable the first time a FILE-declaring program had an empty pool (N79GOTO;
isolated control E34B1: a FILE declaration, no literals, no ON → DR emits
COMMON bytes → `DEF-DATA-SIZE` → `SET-LC(code,0000)` with **no** `SET-LC(data,0000)`).
Fixed to `st.pool <> []`.  Census over 1761 goldens, and why the rule is "one SET-LC per pool
BLOCK": 10 goldens have `SET-LC(data,0000)` with zero DATA bytes (PL16/PL17/PL21/V104/V108 —
empty pool block still gets its location record [C152]); 13 have DATA bytes and no
`SET-LC(data,0000)` (KEYFILE/P022/P046/ENTER — first block is not at 0).

## Still open (deliberately)

* **E34A1 / REVERSE / E30E2**: `dcl sysin file;` **inside a nested procedure** is still refused
  ("procedure local of type FILE is unsampled").  NETWORK declares its files at outer level and
  is not blocked by this.
* **Nested unnamed BEGIN-blocks** (A9).  `bind.section2` charges a saved-SP cell for *any* block
  whose `on_facts.of_goto` is true, but exports `pl_sp_cell` only on the `nm = Some pn` branch
  (line ~1597) — the `nm = None` branch at line 1626 is the nested-BEGIN call.  If lowering ever
  reached that layout, DATA would be 2 bytes longer than anything references it, silently.  What
  stands in front of it today is the pre-existing "procedure without name [TBD]" refusal in
  `lower_proc`, and A9 is now registered as a negative precisely so that removing or narrowing
  that refusal without fixing the cell route turns the gate red.  DR's A9 numbers say the fix is
  to reuse the PARENT block's cell (0019, DATA AREA 001B — no per-BEGIN section), not to give
  BEGIN a layout of its own.
* **`CALL ?OFCOP` in a nested procedure** is emitted on `ls.on_any && st.in_proc` and is
  byte-exact in E34A6/E34A7 -- but those two blocks contain a GOTO-form ON anyway, so the
  broader trigger ("ANY ON-unit", from E34A1) is only verified by A1's DR golden, and A1 cannot
  be compiled here because of the FILE-declaration gap above.  The trigger is therefore taken
  from A1's measurement, not from a specimen of my own: if the statement-form-only case turns
  out to differ, A1 is the probe that will say so once `dcl FILE' inside a procedure works.
* **P3** normal-flow runtime witness for E32E2 (must not simulate an EOF event).
* **P4** EOF delivery: console EOF cannot deliver it (`oracle/linkrun.py` says so); needs a
  staged CP/M disk file.  Until then no claim about ENDFILE *firing* is made.
* **P5** NETWORK recompile against DR's 05B0/00EB oracle — now unblocked at line 50.

## P4 - P6 (same session, after the P1-P2 commit `a4bf0a5`)

P1/P2 closed ON/GOTO and REVERT.  P4 onward is the comparison-family work that NETWORK's
remaining refusals turned out to need, plus the NETWORK checkpoint itself.

**P4a - CHARACTER VARYING x VARYING compare, all four shapes (C212).**  `str_cmp_shape_vv'
was rewritten as a classifier pair (`str_vv_side' -> Imm / FCell / Mem, then a 4-arm table)
instead of a list of operand-name combinations.  E34C1-C10, 10 goldens, byte-exact.  The
part worth keeping as a warning: without the guard added to the numeric ident-vs-ident arm,
any varying pair the classifier declined fell through to `CALL ?IS22N' and compiled with rc=0
-- five of the seven probes I first wrote were silently wrong that way.  A `_ -> None' in a
shape table is only as strong as the fallthrough arms beneath it.

**P4b - tail RET for value-returning procedures (C213).**  The E2E-31 note's "value-returning
procedures are not given a trailing RET" was false; the trigger is the shape of the last
top-level statement, and E34D2 (IF/ELSE where both arms RETURN, still one extra RET) is what
falsifies the instruction-level reading.  E34D4 + the E31F5 regression gave the second flag:
a body that cannot fall out (forever loop) gets no RET, so `falls_out' consults both
`proc_tail_exits' and `proc_tail_no_exit'.  E34D1-D4, 4 goldens, byte-exact.

**P5 - based FIXED BINARY member as a comparison operand (C214).**  `bfix_val_load' is now the
single authority for "member value into HL" (it replaced two hand-written copies, [C202]);
`cmp_pair2' decomposes the [C204] parking decision so the member arm and the existing ident/ident
arm share it -- the rewrite of `cmp_pair' onto it is byte-neutral, verified by the 790 specimens
that were already green.  E34E1-E11, 11 goldens, byte-exact: six relations, both orientations,
member-vs-member, offset members.  The `double XCHG' in E34E1/E34E4 turned out to be COMPOSITION
(the ladder's trailing XCHG plus `cmp_pair2''s), not a DR quirk -- I nearly invented a rule for it.

**P5b/P6 - `= k' and `= <arithmetic expression>' (C215).**  NETWORK's line 224
(`if t = infinite', `%replace` -> 32767) had no arm: `^= k' had the ladder, `= 0' had its
memory form, `= k' for k>0 had nothing.  E34F1-5 pin the ladder at k = 1, 5, 255, 300, 32767.
Then line 236 (`if t = d + p->total_distance') needed the expression family: E34F6-14 pin it,
including the fact that DR loads the *variable* first when the expression is one load plus a
literal bias (F7, F14) and the *expression* first when it combines two non-literals (F6, F8,
F11, F12, F13).  `k + x' and expression-vs-expression are refused: no sample.

**NETWORK checkpoint (P6).**  It compiles end to end for the first time: 3200 bytes, DR's exact
total size, DATA area 235/235 exact, 1099 code bytes against DR's 1096.  It is registered as
DIVERGENT row 17 rather than as a specimen, because it is not byte-exact: first differing file
byte 1027 = code 0171 = DR's line 101, `p->city_name = city;'.  There DR does
`LHLD CITY / PUSH H / LHLD P / POP D / MVI A,20 / CALL ?SMVVM' (13 bytes) and mine does
`LHLD CITY / LXI D,CITY / MVI A,20 / CALL ?SMVVM' (11): the C212 load-vs-immediate bit applied
to a varying ASSIGNMENT through a based pointer.  Mine is 2 bytes shorter at that one site and
3 longer overall, and the 1679 differing file bytes are one re-synchronization, not 1679
defects -- which is why the row pins the first divergent address and not the diff size.
October's first divergent byte was 338.

**Two negatives closed.**  E28N9 (`if w = 1 then stop;') and E32C10 (nested `if k = 3' with k a
formal) both documented this exact gap and both have pre-existing DR goldens, so they were
promoted to specimens rather than deleted [E2E-32's rule].  The gate caught the substitution by
name (`2 entries SUBSTITUTED (same name, different reference -- a count cannot see this)'),
which is the check [C158] exists for.  Negatives: 120 -> 118; specimens: 804 -> 831.

**P3 and the EOF question are NOT done.**  The normal-flow runtime witness for E32E2 has not
been produced, and no EOF event has been demonstrated: console EOF cannot deliver one
(`oracle/linkrun.py`), and a staged CP/M disk file is the route.  Nothing in P4-P6 touches the
ENDFILE *firing* claim, which stays unverified; the ON/ENDFILE machinery verified here is the
code DR emits, not the code path that runs when a file ends.

Gate at the end of P6: **831 byte-exact / 0 fail, 118/118 negatives refused, 17/17 divergences
pinned, exit 0.**  ARCH-1 (`ocaml/proto/`) untouched.  Decimal and numeric backlog untouched.
