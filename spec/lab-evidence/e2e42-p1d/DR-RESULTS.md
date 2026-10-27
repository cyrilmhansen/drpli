# E2E-42/P1d — what DR actually said

Written after the oracle ran (`golden/e42p1d`, `PLI D:<name> $L$D$S`).  The predictions
are in `HYPOTHESES.md` and are NOT edited here; a prediction DR falsified stays falsified.
Full dumps, chains and the before/after table: `VARYING-DISPATCH.txt`.

| probe | prediction | DR's answer | verdict on the prediction |
|---|---|---|---|
| E46J1 | accepts, `?SLVTS` | accepts; `NM CHAR(14) VARYING` at 0000, `K` at 000F; chain `?SLVTS` | **confirmed** |
| E46J2 | accepts, both members `?SLVTS`, cells 15 and 255 | accepts; `LINE … VARYING` 0000, `BUFF … VARYING` 000F, AUTO STORAGE **272**; two `?SLVTS` | **confirmed** |
| E46J3 | accepts, 27-byte `?OIOOP` title block | accepts; chain `?SLVTS ?OIOOP ?SIOOP ?SLCTS ?PNCOP ?QIOOP ?CIOOP` — the title takes `?SLVTS` and the file PUT's literal takes `?SLCTS` | **confirmed**, and it adds the pairing: one object carrying both helpers |
| E46J4 | accepts, two `?SLVTS` records | accepts; `?SLVTS` at the OPEN and `?SLVTS` at the PUT | **confirmed** |
| E46J5 | same group with NO attribute is fixed: `?SLCTS`, `buff` at +14 | accepts; `LINE CHAR(14)` 0000, `BUFF CHAR(254)` **000E**, AUTO STORAGE **268**; two `?SLCTS` | **confirmed** — and this is the row that proves the attribute, not the group syntax, changes the cell |
| E46J6 | open question: is a level-numbered member reachable bare? | **accepts**: dump `.LINE CHAR(14) VARYING MEMBER` at **0000** and `.NXT FIXED BINARY(15,0)` at 000F in AUTO STORAGE 17; `put list(line)` lowers to `LXI H,0000 / CALL ?SLVTS` at code 0010 and `put list(nxt)` to `LHLD 000F / MVI A,09 / ?QICOP / ?PNVOP`; code 53 / data 17 | **answered, not predicted** — DR reaches the bare name, and the varying member's cell is 15 bytes, so the member layout follows the same n+1 rule; this compiler does not reach it |
| E46J7 | accepts (attribute before the type) | accepts, identical object to E46J1 apart from names: code 30 / data 17 | **confirmed** |
| E46J8 | unknown: reject the FIXED item, ignore it, or reject the declaration | **CONFLICT in pass 1, NO .REL**; its listing still prints the block with `B CHAR(4) VARYING` | **the third option, and it is per-item**: the CHARACTER item took the attribute, the FIXED item is the error |
| E46J9 | — | CONFLICT, no .REL | new law |
| E46J10 | — | CONFLICT, no .REL | new law (BIT is not CHARACTER either) |
| E46J11 | — | accepts: title of a varying member is `?SLVTS`, code 42 / data 17 | measured |
| E46J12 | — | accepts: `?SLCTS` with `MVI A,0E` for a FIXED member, code 32 / data 16 | measured — the control that stops "members take ?SLVTS" |
| E46J13 | — | accepts COPYLPT's declaration verbatim: `LINE` 0008, `BUFF` **0017**, AUTO STORAGE **278**, code 57 / data 278 | measured — and 278 is COPYLPT's own frame size |
| E46J14 | — | **accepts** `dcl x varying;`: `X(0) VARYING AUTOMATIC` in AUTO STORAGE **0**, DATA AREA 1, store via `?DLDOP`, print via `?PNVOP` | falsified my expectation of a rejection — and DR's dump says VARYING while its code treats `x` as a number |
| E46J15 | — | CONFLICT in pass 1 **and** COMP REQ in pass 2, no .REL | new law |
| E46J16 | — | accepts; `?SMCVM` then `?SLVTS`, code 43 / data 272 | measured — assignment to a group-declared varying member is the flat route |
| E46J17 | — | accepts; `BUFF` at **000F**, code 30 / data 270 | measured |
| E46J18 | — | accepts; title of a FIXED member is `?SLCTS`, code 38 / data 16 | measured |
| E46J19 | — | CONFLICT, no .REL; dump `A CHAR(4) VARYING` 0000, `B FIXED BINARY(15,0)` 0005, `C CHAR(6) VARYING` 0007 | measured — the per-item law again, with two winners and one error |
| E46J20 | — | accepts a ONE-member group; `?SLVTS` at the title, `?SLVTS`+`?PNVOP` for the two-item print, code 68 / data 17 | measured |
| E46J21 | — | accepts the qualified spelling: `?SMCVM` + `?SLVTS`, code 43 / data 19; dump `.LINE CHAR(14) VARYING MEMBER` at 0000, `.NXT` at 000F | measured |

## The three things DR settled that the code could not

1. **The attribute is per-item and CHARACTER-only.**  E46J8/E46J19 are the proof: DR diagnoses
   CONFLICT on the FIXED item and still applies VARYING to the CHARACTER items in the same
   declaration.  Nothing in this compiler's parser could express "partially accepted", so the
   refusal is whole-declaration and matches DR's OUTCOME (no object).
2. **A typeless `varying` is accepted and is not a string.**  E46J14 falsified my prediction
   that DR would reject it.  DR gives it no cell at all and routes both its store and its print
   through the numeric helpers.
3. **A level-numbered member is reachable by its bare name and takes the same helper pair as a
   flat variable.**  E46J6/E46J11/E46J12/E46J18/E46J21 — five objects DR emits for shapes this
   compiler refuses.  That is a LOWERING gap (the member alias registry), not the classification
   gap P1d closes, and it is registered as `my-gap` so it cannot be mistaken for a DR rejection.
