# E2E-49/P3 — hypotheses and PREREGISTERED predictions (COMPOSITE: equal-length literal pair, member QUALIFICATION, literal-LEFT over-extent, ORDERED RELATIONS — E49C1..C4, E49D1..D4, E49E1..E2, E49F1..F4)

Written and committed **before** the DR oracle is invoked on any P3 probe, under
PROTOCOL.md Part 1 #1 (the committed blob, not a file mtime, proves ordering).
`RESULTS.md` §1 must be a prediction-vs-verdict table over exactly these rows; every
MISS stays in that table (PROTOCOL #2).

    probes written by spec/lab-evidence/e2e49-p3/mkprobes.py (CRLF + ^Z, [C193] (b),
      every emitted line <= 71 columns -- the measured law that killed P2d run 1)
    baseline of MY compiler recorded in BASELINE-MINE.txt at HEAD 685741c (NO oracle
      call): Panel A (C1..C4) and Panel C (E1/E2) ACCEPT on the recorded literal
      templates; EVERY Panel B (D1..D4) and Panel D (F1..F4) probe refuses with rc=2
      through `imem_refuse "comparison"'.
    the commit that adds probes/E49C*/D*/E*/F*.PLI + mkprobes.py + this file +
      BASELINE-MINE.txt is the PREDICTION SHA (fill-in commit below names it; it is
      committed BEFORE any oracle invocation); `golden/e49p3' does not exist at that
      commit and the fill-in commit is still an ancestor of the run.

## What this round is

The operator-authorized campaign **E2E-49/P3 — composite CHARACTER FIXED / TEST bank,
four panels**. Every probe keeps the E49B shared DECL (`1 rec, 2 na char(3), 2 nb
char(3), 2 s2 char(2); dcl k fixed bin(15);`) and the `put list('K=', k);` tail, so
the [C309] skip fill and the [C314] pool-first DATA layout stay comparable with
`golden/e49p1` and `golden/e49p2`. A compare literal, when pooled, lands at 0000 and
shifts the frame; the sizes named below are computed from that law.

- **Panel A (E49C1..C4)** — settle the [C338] [TBD]: does `?SCCCM` collapse the length
  pair to `06 n / 78 (MOV A,B)` when a member meets a literal of EQUAL length? The two
  orientations are decided INDEPENDENTLY (no shared rule presupposed), each in both
  relations `=` and `^=`.
- **Panel B (E49D1..D4)** — QUALIFICATION of the compared members: the three unmeasured
  spellings inside a member-vs-member pair (bare/qualified, qualified/bare, bare/bare)
  and the BARE member on the RIGHT of a literal (the P1 asymmetry, [C335] scope note).
  Judged against `golden/e49p2/E49B1..B5` and `golden/e48p2e/E48E7` to isolate the
  effect of the WRITTEN name alone.
- **Panel C (E49E1..E2)** — a literal LONGER than the extent written LEFT
  (`'ABCD' = rec.na`, `^=`). [C336] measured the OPPOSITE orientation and its RESULTS
  §2.6 explicitly refuses extrapolation; nothing may be assumed.
- **Panel D (E49F1..F4)** — ORDERED RELATIONS `<`, `>`, `<=`, `>=` between qualified
  FIXED members, equal and unequal extents. NEVER probed. Acceptance, helper,
  comparison mechanism and branch bytes are ALL open; NOTHING from `=`/`^=` is
  presupposed (not even `?SCCCM`).

## Prior evidence (literal `.REL` bytes / ledger laws, never a `.PRN`)

- `golden/e49p1/E49A1/E49A1.REL` ([C333]): member-LEFT literal-right stages through
  `EB`: `21 *D(cell) / EB / 21 *D(pool) / 06 <left> / 3E <right> / CD ?SCCCM / C2`;
  all three sampled pairs (3/2, 3/2, 3/4) had UNEQUAL lengths and kept TWO immediates.
- `golden/e48p2e/E48E7/E48E7.REL` ([C330]): literal-LEFT, QUALIFIED member-right, the
  DIRECT head `21 *D(member) / 11 *D(pool) / 06 02 / 3E 03 / CD ?SCCCM / C2`, CODE 65.
- `golden/e49p2/E49B1..B5` ([C337]–[C341]): the QUALIFIED-QUALIFIED member pair parks
  on the STACK (`21 *D(left) / E5 / 21 *D(right) / D1`), equal extents COLLAPSE to
  `06 n / 78`, unequal keeps the positional pair, `^=` skips CA, no literal pooled
  (DATA 000C).
- [C335]: bare vs qualified spelling of the member-LEFT-of-literal compare is
  byte-identical (E49A2 == E49A1 but module-name bytes). SCOPE: left side only.
- [C072]: DR's `^=` skip byte is CA in every sampled family; the `=` skip is C2
  ([C309] fill = next statement).
- `artefacts/PLILIB.IRL` (a preserved historical input, NOT an experiment): its symbol
  table carries a SECOND compare family beside the four measured `?SC*' helpers —
  `?CXCCM ?CXCMS ?CXCVM ?CXSCM ?CXSTS ?CXSVM ?CXVCM ?CXVMS ?CXVVM` — and `?SCCMS`,
  `?SCSCM`, `?SCSTS`, `?SCSVM`, `?SCVMS`. This is a PRIOR for Panel D's helper name,
  never a prediction of bytes: no `.REL` has ever shown what a relational does.

## Competing hypotheses and per-row predictions

### Panel A — the [C338] TBD (4 rows)

- **H-AK-M / H-AC-M** (member-left, E49C1 `rec.na = 'ABC'`, E49C3 `^=`):
  - H-AK-M (KEEP): E49A1's template verbatim with the pair `06 03 / 3E 03` —
    `21 *D(0005 na) / EB / 21 *D(0000 pool) / 06 03 / 3E 03 / CD ?SCCCM / skip`,
    head 17 bytes, **CODE 66**, DATA 000F (`'ABC'@0000..0002, 'K='@0003..0004,
    na@0005..0007, nb@0008..000A, s2@000B..000C, k@000D..000E`); skip C2 (C1) /
    CA (C3), fill = next statement 001D ([C309]).
  - H-AC-M (COLLAPSE): same head with `06 03 / 78` and NO `MVI A` anywhere —
    head 16 bytes, **CODE 65**, fill 001C.
  - Falsifiers for BOTH: refusal (new `dr-refuses` boundary inside the admitted
    fixed-compare class); a different helper (breaks [C333] §2.3); any `E5/D1`
    STACK parking for a member-vs-LITERAL pair (a fourth form — parking was
    measured member-vs-member only, [C337]).
- **H-AK-L / H-AC-L** (literal-left, E49C2 `'ABC' = rec.na`, E49C4 `^=`):
  - H-AK-L (KEEP): E48E7's DIRECT template with `06 03 / 3E 03` —
    `21 *D(0005) / 11 *D(0000) / 06 03 / 3E 03 / CD ?SCCCM / skip`, **CODE 65**,
    DATA 000F; skip C2 (C2-probe) / **CA (C4-probe — first object pairing CA with
    the literal-left template: [C072] synthesis has never been sampled here)**;
    fill 001C.
  - H-AC-L (COLLAPSE): `21 *D(0005) / 11 *D(0000) / 06 03 / 78 / CD ?SCCCM / skip`,
    **CODE 64**.
  - Same falsifier set; PLUS the cross-orientation one: C1 collapsing while C2
    keeps (or vice versa) falsifies any single-rule reading and is recorded as
    its own result, not smoothed over.
- Priors: verdict ACCEPTS (every fixed compare sampled so far is admitted);
  bytes lean KEEP — the collapse has been seen ONLY where both attributes came
  from `MVI B`-able extents (all-member pairs), and the literal template carried
  two immediates in all four unequal samples. But [C338]'s TBD is exactly this
  gap, so BOTH forms are first-class.

### Panel B — qualification (4 rows)

- **H-B-fold** (spellings invisible): DR resolves `na` and `rec.na` to the same cell
  ([C253]/[C258]) and the compare encoding ignores HOW the name was written —
  [C335]'s finding, extended to both slots:
  - E49D1 (`na = rec.nb`), E49D2 (`rec.na = nb`), E49D3 (`na = nb`) each ACCEPT and
    are byte-identical to `golden/e49p2/E49B1` EXCEPT the module-name bytes — same
    stacked head `21 *D(0002) / E5 / 21 *D(0005) / D1 / 06 03 / 78 / CD ?SCCCM / C2
    -> 001D`, CODE 66, DATA 000C, SAME two `*D` relocations (0002, 0005).
  - E49D4 (`'AB' = na`) ACCEPTS byte-identically to the E48E7 template on this DECL:
    `21 *D(0004 na) / 11 *D(0000 'AB') / 06 02 / 3E 03 / CD ?SCCCM / C2 -> 001C`,
    CODE 65, DATA 000E (`'AB'@0000, 'K='@0002, na@0004..0006, nb@0007..0009,
    s2@000A..000B, k@000C..000D`).
- **H-B-gate** (qualification IS a DR boundary): some bare spelling draws a PASS-2
  error with no `.REL` — a `dr-refuses` law of the [C332]/E46K14 kind. My refusal
  gate would then MIRROR DR and stand.
- **H-B-mixed**: orientation-specific acceptance (the P1 asymmetry pattern: bare
  admitted LEFT-of-literal only). Named sub-readings: {D1 yes, D2/D3 no}, {D1..D3
  yes, D4 no}, or any other split — each row's verdict is read independently.
- Priors: rows D1..D3 lean ACCEPT (fold precedent [C335] + no witness that DR ever
  gated on qualification inside an admitted compare); D4 lean ACCEPT but weaker —
  P1 §2.4 deliberately scoped its finding to the LEFT side.
- Falsifiers: an accepted object that differs from E49B1/E48E7 in ANY byte besides
  the module-name fields (relocation order/contents, head form, sizes) — that names
  a qualification effect, not a fold; refusal while the qualified pair is accepted.

### Panel C — literal-LEFT over-extent (2 rows)

- **H-CE** (accept, whole, positional — mirrors [C336] WITHOUT presupposing it):
  E49E1 `21 *D(0006 na) / 11 *D(0000 'ABCD') / 06 04 / 3E 03 / CD ?SCCCM / C2 ->
  001C`, CODE 65, DATA 0010 with `'ABCD'` occupying 0000..0003 UNTRUNCATED
  (`'K='@0004..0005, na@0006..0008, nb@0009..000B, s2@000C..000D, k@000E..000F`);
  E49E2 the same head with skip CA. NOTE this is EXACTLY my current baseline output
  (BASELINE-MINE.txt): if DR accepts with these bytes, these two rows need NO arm.
- **H-CR** (refusal): a literal-longer-than-extent compare is accepted ONLY
  member-left — a NEW asymmetric `dr-refuses` boundary, recorded as law.
- **H-CT** (truncation): pool holds `ABC` (3 bytes), lengths `06 03 / 3E 03`,
  DATA 000F — falsifies "pooled whole" for this orientation.
- **H-CN** (length law NOT positional here): `06 03 / 3E 04` (extent-in-B —
  the [C330] polarity reading reborn under relations?) or any min/max pair —
  falsifies [C334] transfer to over-extent literal-left.
- Prior: ACCEPT (every sampled fixed compare is admitted; [C336] shows DR neither
  refuses nor truncates in the inverse orientation) — but §2.6 of P1 says this row's
  bytes are UNMEASURED in this orientation, so H-CR/H-CT/H-CN stay first-class.

### Panel D — ordered relations (4 rows)

Acceptance itself is open. Competing hypotheses, each falsifiable by the object:

- **H-D-SC** (same helper, new branch): E49F1 takes the measured stacked
  member-vs-member head verbatim (`21 *D(0002) / E5 / 21 *D(0005) / D1 /` then the
  length attribute pair `06 03 / 78` — or KEEP `06 03 / 3E 03`, both readings open
  per the [C338] scope) `CD ?SCCCM`, but the SKIP BYTE is a relation branch — one of
  the flag conditionals JM `FA` / JP `F2` / JC `DA` / JNC `D2` (or a swap of the
  operands + equality branch); a following `ORA/CMP`-style test before the skip is a
  sub-reading. F2/F4 (unequal 3/2) carry positional `06 03 / 3E 02` / `06 02 / 3E 03`
  under this hypothesis (E49B3/B4 law).
- **H-D-CX** (a second helper family): the call target is NOT `?SCCCM` — e.g. any
  `?CX*`/`?SC*` name present in PLILIB.IRL. The head form, length pair and skip byte
  are then ALL read fresh from the object; nothing from `=`/`^=` transfers without
  evidence. The prior for WHICH name is deliberately not written down (symbol-table
  presence is not an experiment).
- **H-DR** (refusal): a PASS-2 error, no `.REL` (the [C332] `BIT REQ` pattern) —
  then the numeric-arm guard's refusal MIRRORS DR and every relation row is
  `dr-refuses`, no arm.
- Priors: verdict UNKNOWN, weakly leaning ACCEPT on language grounds (the manual
  documents character relations) — but a refusal would be consistent with EVERY
  existing witness; do not implement from prior.
- Per-row discriminators: helper name; parking (`E5/D1` vs `EB` vs direct); length
  pair on the UNEQUAL rows — positional vs min/max vs one-operand-only; equal-extent
  rows collapse or not; skip byte per relation (the four rows may differ from each
  other: `<` vs `<=` vs the inverted comparisons). Falsifier of any single-law
  reading: two rows of the same relation-class showing different mechanisms.

## Predictions table (exact per row)

| id | source | predicted verdict | predicted bytes (head, CODE, DATA) | falsifier |
|---|---|---|---|---|
| P-C1 | `if rec.na = 'ABC' then k = 1;` | ACCEPTS | PRIMARY H-AK-M: `21 *D(0005) / EB / 21 *D(0000) / 06 03 / 3E 03 / CD ?SCCCM / C2 -> 001D`, CODE 66, DATA 000F; competing H-AC-M: `... 06 03 / 78 ...` CODE 65 -> 001C | refusal; other helper; E5/D1 parking |
| P-C2 | `if 'ABC' = rec.na then k = 1;` | ACCEPTS | PRIMARY H-AK-L: `21 *D(0005) / 11 *D(0000) / 06 03 / 3E 03 / CD ?SCCCM / C2 -> 001C`, CODE 65, DATA 000F; competing H-AC-L: `... 06 03 / 78 ...` CODE 64 | refusal; other helper; EB appearing in the literal-left head; cross-orientation collapse split vs P-C1 is RECORDED, not smoothed |
| P-C3 | `if rec.na ^= 'ABC' then k = 1;` | ACCEPTS | P-C1's winner head verbatim, skip CA, fill next statement | skip C2; refusal while C1 accepted |
| P-C4 | `if 'ABC' ^= rec.na then k = 1;` | ACCEPTS | P-C2's winner head verbatim, skip **CA** (first CA witness on this template), fill next | skip C2; refusal while C2 accepted |
| P-D1 | `if na = rec.nb then k = 1;` | ACCEPTS (lean) | H-B-fold: == E49B1 but module-name bytes: stacked head, `06 03 / 78`, CODE 66, DATA 000C, relocations `*D(0002)`,`*D(0005)` | refusal (H-B-gate/H-B-mixed); ANY other byte difference vs E49B1 (a qualification effect); different relocations |
| P-D2 | `if rec.na = nb then k = 1;` | ACCEPTS (lean) | same as P-D1 | as P-D1; D1-accept/D2-refuse split = orientation-specific law, recorded as such |
| P-D3 | `if na = nb then k = 1;` | ACCEPTS (lean) | same as P-D1 | as P-D1 |
| P-D4 | `if 'AB' = na then k = 1;` | ACCEPTS (weak lean) | E48E7 template on this DECL: `21 *D(0004) / 11 *D(0000) / 06 02 / 3E 03 / CD ?SCCCM / C2 -> 001C`, CODE 65, DATA 000E | refusal (the P1 asymmetry becomes MEASURED law); lengths inverted `06 03 / 3E 02` (breaks [C334] on the right slot); EB appearing |
| P-E1 | `if 'ABCD' = rec.na then k = 1;` | ACCEPTS (lean) | H-CE: `21 *D(0006) / 11 *D(0000) / 06 04 / 3E 03 / CD ?SCCCM / C2 -> 001C`, CODE 65, DATA 0010, pool WHOLE | H-CR refusal; H-CT truncated pool (DATA 000F); H-CN length readings `06 03/3E 04`, min, max; EB appearing |
| P-E2 | `if 'ABCD' ^= rec.na then k = 1;` | ACCEPTS (lean) | P-E1's winner head verbatim, skip CA | skip C2; refusal while E1 accepted |
| P-F1 | `if rec.na < rec.nb then k = 1;` | VERDICT OPEN, lean ACCEPT | head mechanism open (H-D-SC stacked vs H-D-CX new helper); equal-extent length pair 78-or-3E both open; skip byte a RELATION branch (not C2/CA) under every accepting reading | refusal = H-DR (valid result); any mechanism differing from F3 (same-extent, near relation) falsifies a one-mechanism reading |
| P-F2 | `if rec.na > rec.s2 then k = 1;` | VERDICT OPEN, lean ACCEPT | unequal pair: positional `06 03 / 3E 02` under H-D-SC; ALL readings open under H-D-CX | min/max/one-length-only; refusal |
| P-F3 | `if rec.na <= rec.nb then k = 1;` | VERDICT OPEN, lean ACCEPT | as F1; skip byte may DIFFER from F1's (`<` vs `<=` may not share one branch byte) | refusal; identical-to-F1 bytes IF F1 needed a different branch logic than `<=` semantically requires (record, don't assume) |
| P-F4 | `if rec.s2 >= rec.na then k = 1;` | VERDICT OPEN, lean ACCEPT | as F2 with the operands written SWAPPED: positional `06 02 / 3E 03` under H-D-SC | lengths identical to F2 (class-keyed); refusal |

No row presupposes another panel's answer. Every accepted object is judged
whole-file against the recorded baseline and the goldens by `cmp`, never by segment.

## Command (for the session that runs it — NOT run here)

    PLI_SRC=probes python3 oracle/batch.py E49C1 E49C2 E49C3 E49C4 \
        E49D1 E49D2 E49D3 E49D4 E49E1 E49E2 E49F1 E49F2 E49F3 E49F4 \
        --tag e49p3 --switches '$L$D'

`golden/e49p3` must not exist before this call (verified at pre-registration time: it
does not). Never pass `--reuse` into an existing tag. Then write `RESULTS.md` §1 as a
prediction-vs-verdict table over P-C1..P-F4, re-read every accepted `.REL` with
`tools/reldump.py` / `spec/lab-evidence/e2e42-p2b/chaindump.py` (never a `.PRN` size,
PROTOCOL #6), and commit goldens + report TOGETHER. Lowering may only touch what §2
measures. **No runtime semantics** may be claimed from `.REL` bytes: NO
`spec/RUNTIME.txt` row comes from this round.

## Prediction-SHA fill-in

PREDICTION SHA: **3659f5d** — the commit that added
probes/E49C1..C4,E49D1..D4,E49E1..E2,E49F1..F4.PLI + mkprobes.py + this file +
BASELINE-MINE.txt (`git log --format=%h -- probes/E49C1.PLI | tail -1`); the fill-in
commit naming it is this commit's child and is an ancestor of the oracle run.
