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
