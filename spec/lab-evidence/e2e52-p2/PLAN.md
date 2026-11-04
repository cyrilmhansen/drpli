# E2E-52/P2 — PLAN: DECIMAL formal copy-in (close the E52G `my-gap`)

Operator brief 2026-11-04, opening E2E-52/P2 on top of P1 CLOSED (`6de72c5`,
checkpoint `g272-6b059e276b81`, ledger ENDS C358). Objective: make
`probes/E52G.PLI` whole-file byte-exact against `golden/e52p1/E52G/E52G.REL`
(256 B, sha256 `39b3d7cfe775c039d25b3791ed2f71b3e333509ca1193f3759ce46a850134c67`).
All DR behaviour statements below are from **[C358]** (P1 RESULTS §2.3) plus the
existing golden — predictions are derived BEFORE any trial-and-error output.

## 1. The measured difference (P1 §5 residual, verbatim state)

Mine today (arm `6a4c554`, sha `6ea285ba…`): pool 8 B @`0000`/`0003` and outer
`i` 3 B @`0008` are already exact. Residual = the formal cell map:

| feature | DR golden | mine |
|---|---|---|
| arg-pointer block @`000B` (2 B) | DATA word RELOC → `0x000D` | RELOC → `0x0008` (actual cell directly) |
| main-side copy-in temp | 5 B @`000D`, UNinitialised (no DATA bytes) | absent |
| formal pointer cell | 2 B @`0012` | 2 B @`000D` |
| `LINK-DEF-DATA-SIZE` | `abs 0014` (20) | `abs 000F` (15) |
| copy-in pair in MAIN | `21 r8 / 3E 04 / CD ?DLDOP` then `21 rd / 3E 09 / CD ?DSTOP` at code `0016–0025` | absent |
| `LINK-DEF-CODE-SIZE` | `code 004A` (74) | `code 003A` (58) — delta exactly the 16-byte pair |

Callee side is ALREADY correct on mine: prologue `5E 23 56 EB / 22 r<ptr>` and the
formal store through `LHLD` (`2A r<ptr>`) — the [C131] route — exist; only the
*offsets* shift once the temp is allocated.

## 2. Ownership decision (brief §3)

**Bind owns the five temp bytes.** The existing `cs_temps` mechanism is NOT the
right vehicle: it allocates a fixed 2-byte cell for an *expression* actual and
codegen fills it by evaluating the expression (`lower_hl` + `SHLD`); the copy-in
temp is sized at the FORMAL's DEC precision and filled by the `?DLDOP/?DSTOP`
pair. So:

- `Bind.call_site` gains `cs_copies : int option list` — `Some t` iff argument i
  needs a DEC copy-in temp at pool-exclusive offset `t` (same convention as
  `cs_slot`/`cs_temps`; codegen adds `st.base`).
- Allocation happens in `section2`'s phase-2 pass (alongside expression-argument
  cells, site order, argument order), advancing `cur`; every later cell (child
  blocks etc.) shifts automatically through the existing arithmetic. NO second
  allocator.
- Codegen NEVER allocates for this rule. It consumes the recorded offset and
  cross-checks the SAME precision pair from its own type maps; a disagreement
  (Bind did not allocate but codegen sees a mismatch) is a loud refusal, never a
  silent by-reference pass. This is the single-layout-authority invariant the
  brief demands.

## 3. Trigger predicate (measured shape ONLY)

Fire iff ALL of:
- callee is an INTERNAL, non-recursive, non-`RECURSIVE`-attributed procedure
  (from bind's `reg`);
- argument is a bare `Eident` naming a variable **declared in the caller's own
  block** (`named_of b` rows), not one of the caller's formals (the E27B
  forwarding route is a different, unmeasured shape), not STATIC, not an array
  head, not a based name;
- actual row `RTdec (pa, sa)`, callee formal row `RTdec (pf, sf)`;
- `sa = sf` and `pa < pf` (widening at equal scale — the measured `dec(4,2) →
  dec(9,2)` family).

Temp size = `bytes_of (RTdec (pf, sf))` = `(pf+2)/2` = ceil((p+1)/2) per [R507]
— the SAME authority bind already uses for declared DEC cells.

Everything else involving a DEC formal stays exactly as today or REFUSES by name:
- equal precision AND equal scale → existing by-reference descriptor to the
  actual's own cell (DECPOLY route, byte-exact today);
- `pa > pf` (narrowing), `sa <> sf`, forwarded-formal actuals, outer-scope
  actuals, array elements, expression actuals, EXTERNAL entries, recursive
  callees → refused BY NAME `[TBD] … unmeasured [C358]` (codegen refuses even
  when it can see the types but Bind could not allocate).

Emission (per argument, in the static descriptor arm, BEFORE the `SET-LC data`
block-initialisation record, matching the golden's file order):

```
LXI H,*A(actual_abs) ; MVI A,pa ; CALL ?DLDOP      (load at ACTUAL precision)
LXI H,*A(temp_abs)   ; MVI A,pf ; CALL ?DSTOP      (store at FORMAL precision)
LINK-SET-LC data slot+2i ; RELOC data temp_abs ; LINK-SET-LC code lc
LXI H,*A(slot_abs) ; CALL q                        (unchanged block-pointer call)
```

The callee's formal pointer cell address shifts automatically (its `base` grew by
the 5 bytes); the block word now points at the temp.

## 4. Pre-registered predictions for E52G (derived from [C358] + golden dump)

DATA segment (pool-exclusive → absolute):
- `0000–0007` pool: 3 B `00 03 00` + 5 B `00 03 00 00 00` — UNCHANGED.
- `0008–000A` outer `i` — UNCHANGED.
- `000B–000C` block: word RELOC operand becomes **`data 0xd`** (was `0x8`).
- `000D–0011` copy-in temp: allocated, **no DATA bytes** (uninitialised, like
  every other variable cell in the golden).
- `0012–0013` formal pointer cell at q's base.
- `LINK-DEF-DATA-SIZE abs 0014` (8+3+2+5+2 = 20 = DR's total).

CODE segment:
- `0000–0015` frame + `i = 3` store — UNCHANGED.
- `0016–0025` the 16-byte copy-in pair exactly as in §3 above, i.e. records:
  `21 / RELOC data 0x8 / 3E 04 / CD 0000 / CHAIN-EXT ?DLDOP@001C` then
  `21 / RELOC data 0xd / 3E 09 / CD 0000 / CHAIN-EXT ?DSTOP@0024`.
- between code `0025` and `0026` the DATA-init record trio
  `LINK-SET-LC data 000B / RELOC data 0xd / LINK-SET-LC code 0026`.
- `0026–002E`: `21 / RELOC data 0xb / CD 0000 (CHAIN-ADDR @002A) / C3 0000`.
- q body shifts to `002F`: `5E 23 56 EB / 22 / RELOC data 0x12`; store
  `21 r3 / 3E 09 / CD ?DLDOP` then `2A r12 / 3E 09 / CD ?DSTOP`; `C9` at `0046`.
- tail: `RELOC code 0x47`; `CD ?STOPX` at `0047`; `LINK-DEF-CODE-SIZE code 004A`.

Verdict prediction: whole-file `cmp` **byte-identical** to the golden (sha
`39b3d7cf…`), including record order and padding (bits consumed 1879/2048).

Controls predicted UNCHANGED: E52A/B/C/D/E/F/H/I/J (no DEC-formal call site),
E51A..L 12/12, and every current panel specimen: none carries a
precision-mismatched DEC call (all 1195 are byte-exact TODAY with the
by-reference route, so a mismatch specimen would have diverged — if one exists
and the gate breaks, that is falsification evidence and the round stops at it).

## 5. Steps

1. Commit this PLAN before any compiler byte changes.
2. `bind.ml`: `cs_copies` field + phase-2 allocation + predicate §3.
3. `codegen.ml`: consume `cs_copies`; extend the `formal_is_dec` guard (mismatch
   handling + refusals); emit the pair + retarget the descriptor word.
4. `dune build`; compile E52G; `cmp` vs golden; `reldump` diff on mismatch.
5. Recompile E52A–E52J (whole-file `cmp` ×10) and E51A–E51L (×12) vs goldens.
6. Full compile-tier gate (`timeout 3600 python3 tools/e2e_gate.py`, rc DIRECT);
   expect 1195/1195 unchanged at this point.
7. Register E52G: `SPECIMENS.update` entry; `--update-inventory` (expect 1195 →
   1196); rerun full gate (expect 1196/1196), rc DIRECT.
8. Update `PROC.DEC_FORMAL_COPYIN_CELLMAP` COVERAGE row to EXACT:1 (cite
   specimen E52G now that it is a panel key; keep [C358]); no new claim
   (C358 states the law); coverage_check rc 0 / 139 rows.
9. LOAN2 UNMODIFIED (safe procedure): record the current blocker verbatim; do
   not fix anything beyond copy-in.
10. RESULTS.md §(difference/mechanism/predictions-vs-measured/parity/effects/
    gate/LOAN2/remaining unsupported forms); durable HANDOFF/PROGRESS/LEARNINGS
    prose; explicit-path commits; finalize/renew per config. STOP after P2.

## 6. Explicit non-goals (brief §4)

No generalization to different scales, narrowing, arrays, mixed numeric classes,
recursion, expression actuals, EXTERNAL entries or pointer formals; no PAGE /
PUT FILE / ON-unit / EDIT work; no dashboard `**26**` fix (record only); no new
COVERAGE rows beyond the update of the existing one; no push; goldens never
re-derived; operator `handoff.config.json` never staged.
