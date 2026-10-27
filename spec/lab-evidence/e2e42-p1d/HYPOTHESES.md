# E2E-42/P1d-A — probe hypotheses, recorded BEFORE the oracle ran

Every row here is what this session predicted from the code and from the COPYLPT
object, written down before DR was run on the probe.  DR's answer is appended in
`DR-RESULTS.md`; a prediction that DR falsified stays visible.

| probe | source shape | prediction for DR | what it falsifies |
|---|---|---|---|
| `E46J1` | `dcl nm char(14) varying` + `put list(nm)` | ACCEPTS, `?SLVTS` (control; the route [C174] already pins) | nothing new — it is the control that makes J2's difference a one-variable experiment |
| `E46J2` | `dcl (line char(14), buff char(254)) varying, k fixed bin(15)` + `put list(line); put list(buff)` | ACCEPTS; BOTH members take `?SLVTS`; members are ordinary DATA cells, `line` 15 bytes and `buff` 255 | that COPYLPT's group is a STRUCTURE whose members are reached through something other than an absolute DATA address; that `varying` applies only to the first item of a group |
| `E46J3` | J2's declaration (with a FILE) + `open file(outf) stream output title(line)` | ACCEPTS; 27-byte `?OIOOP` block with `LXI H,<line descriptor>` + `?SLVTS` (COPYLPT `014C`) | that the title route for a member differs from the scalar route |
| `E46J4` | same member used in BOTH `title(line)` and `put list(line)` in one program | ACCEPTS; two `?SLVTS` chain records, one per site | that one of the two sites has a private dispatch of its own |
| `E46J5` | `dcl (line char(14), buff char(254));` — the same group WITHOUT the trailing attribute | ACCEPTS as two FIXED characters: `?SLCTS` + `MVI A,0E` / `MVI A,FE`, and `buff` at DATA + 14 rather than + 15 | that the storage difference is invented by my binder: if DR moves `buff` by 1 byte between J2 and J5 the group attribute really changes the cell size |
| `E46J6` | `dcl 1 rec, 2 line char(14) varying, 2 nxt fixed bin(15)` — a level-numbered internal structure with a VARYING member | DR ACCEPTS; whether `line` is reachable UNQUALIFIED in a `put list` is the open question this probe decides | that the COPYLPT shape and a level-numbered structure's varying member are the same binding problem |
| `E46J7` | `dcl nm varying char(14)` — VARYING BEFORE the type | DR ACCEPTS (the manual allows attribute/type interleaving); the object should equal J1's apart from names | that my parser's type-then-attribute order is the only accepted spelling |
| `E46J8` | `dcl (a fixed bin(15), b char(4)) varying` — a group attribute over a NON-character member | unknown: DR may reject VARYING on a FIXED item, or ignore it for that item, or reject the whole declaration | that a group `varying` distributes blindly to every member |

## What I already measured locally (my compiler, before any DR run)

`pli80bind.exe` on the COPYLPT shape prints

    c 0000 LINE CHAR(14) AUTOMATIC
    c 000E BUFF CHAR(254) AUTOMATIC

where the same source spelled as two scalar declarations prints

    c 0000 LINE CHAR(14) VARYING AUTOMATIC
    c 000F BUFF CHAR(254) VARYING AUTOMATIC

so the trailing group attribute is dropped somewhere between the parser and the
binder, and the DATA offsets already differ (`000E` vs `000F`).  The frame size
differs too: 268 vs 270.

The P1c note blamed the *internal-member registration* path in `bind.ml` (the
`(RTbin 15 | RTptr) when top_level_head` gate at bind.ml ~774).  That gate is
NOT on this path: the parser's group handling (`parse_dcl_item`, parser.ml ~495)
flattens `(line character(14), buff character(254)) varying` into two items with
`dlevel = None`, i.e. two ordinary scalar rows, never `RTimem` rows.  The
attribute arrives in `dattrs` as `VARYING` with no arguments and
`resolve_type_raw` reads only `d.dtype`, so `Tchar {varying = false}` wins.

## Hypotheses

H1 (parser): the group's trailing attributes are not attached to the members.
    FALSIFIED by reading parser.ml — they ARE attached, as `dattrs`.
H2 (binder): `resolve_type_raw` never consults `dattrs` for `VARYING`, so the
    attribute is parsed, stored, and silently ignored.  Predicted by the local
    measurement above; J2/J5 test it on DR's side.
H3 (member registration): the RTimem gate is responsible.  Testable via J6,
    which is the actual level-numbered shape.
H4 (codegen dispatch): `lower_open`/PUT choose the helper from `st.vars`, which
    is derived from the `rt` the binder produced.  If H2 is right, no codegen
    change is needed at all.
