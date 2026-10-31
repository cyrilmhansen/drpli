# docs/history/2026-10-31-p2e-arm3-closed.md — E2E-48/P2e arm 3, closed

Recorded 2026-10-31 when arm 3 landed. **A RECORD, not current instructions**
(index: `docs/history/README.md`). Authority for the law:
`spec/lab-evidence/e2e48-p2e/RESULTS.md` §2.3 (claim C329 owed by step 6).

## Verbatim spec text as it stood in HANDOFF.md's live Next-action (pre-`e49902a`)

3. **Arm 3 — `= '0'b' VALUE** (the fallback inside `bit_cond_mat`'s `Eq` arm, ~7222-7232, which
   admits only `Ast.Ebit "1"`). Emit for `Ast.Ebit "0"`: `3A *D(b) / E6 80 / D6 01 / 9F`
   (E48E5 0006, 11 bytes incl. the `32` STA) — i.e. the `'1'b` head WITHOUT the `D6 80` step.
   `bit_store_cond_bytes` demands nothing here (no pool cell), so no prescan change.

## Closure record — measured ACTUALS (2026-10-31)

- Landed at `e49902a`, single file `ocaml/lib/codegen.ml` (+20/-2): new arm
  `Ast.Eident v, Ast.Ebit "0" when vk_of st v.Ast.orig = Vbit1` in `bit_cond_mat`'s `Eq`
  fallback, body `3A + Data reloc / E6 80 / flag ()`; the caller's `STA` and the `'1'b`
  arm are untouched; `bit_store_cond_bytes` untouched (no pool cell demanded — demand and
  lowering remain ONE predicate, [C152]/[C179] law); its doc-class list updated in prose.
  The `'0'b` REVERSED orientation (`'0'b = b`) and every RESULTS §3 shape stay refused.
- E48E5 complete `.REL` byte-identical to `golden/e48p2e/E48E5/E48E5.REL` (whole-file
  `cmp`). E48E sweep at this commit: **5/7 exact** (E48E1..E48E5); E48E7/E48E8 refuse by
  name (arms 4/5, unstarted); **E48E6 KEEPS refusing** (dr-refuses, no `.REL` produced).
- Regression sweeps: e48p1 24/24, e48p2c 9/9, e48p2db 10/10, e48p2retire 2/2 — all
  whole-file byte-identical. Negative panel with GATE semantics (CRLF+`^Z`, stderr):
  181/181 refused, 0 anomalies; E46K14's pinned marker UNMOVED (not re-pinned).
- Clean scratch-tree rebuild (LEARNINGS cache-neutral rule): warning multiset
  22/15/28/2/14/2/17/26 = **126 UNCHANGED**.
- Compile-tier FULL GATE `python3 tools/e2e_gate.py` rc=0, ACTUALS: **1120 byte-exact /
  0 fail of 1120**, negative 181/181, divergence 9/9, coverage 113 rows 0 errors, census
  EXACT 15 / DIFFERS 0 / REFUSED 26 / UNEXPECTED 0. (The E48E probes are NOT in these
  counts — their registration is step 6.)
