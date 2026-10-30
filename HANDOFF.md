# HANDOFF.md — DRPLi

Manual prose wins over the managed block below it. Do not hand-edit the managed block.

## Recovery instructions

1. Confirm the repository and revision:
   `cd /home/john/projects/sushiworks/pli80 && git rev-parse --abbrev-ref HEAD && git rev-parse HEAD && git status --porcelain=v1 | wc -l`
   Expect branch `main` and an empty porcelain output; a dirty tree is investigated, never
   cleaned (`AGENTS.md` → Protected).
2. Lean recovery: Pi auto-loads `AGENTS.md`; read this file and `PROGRESS.md` NOW,
   then the precise `spec/CLAIMS.md` claims and lab evidence for the next operation.
   `PROTOCOL.md` governs all scientific procedure and is consulted when needed;
   `GOAL.md` and `LEARNINGS.md` remain authoritative and are read selectively.
   A deferred read never weakens the scientific protocol.
3. Check checkpoint freshness with `/handoff verify` (extension auto-loaded — the project is
   trusted; see `PROTOCOL.md` → Load). `stale` or `missing` means: re-derive state from commits and lab evidence,
   then refresh and attest with `/handoff finalize` (dev.2). Do not trust this file's
   managed block over its prose.
4. Load the authoritative evidence for whatever you are about to do:
   `spec/CLAIMS.md` (claims ledger, currently through C320),
   `spec/INVENTORY.txt`, `spec/COVERAGE.tsv`, `spec/RUNTIME.txt`, `spec/DIVERGENT.txt`,
   and the newest `spec/lab-evidence/e2e42-p2c/` reports.
5. Do **not** run the compiler, the oracle, LINK-80, cpmsim, Rune CI or `tools/e2e_gate.py`
   unless the session's actual task is compiler development or gate verification.

## Last verified state — E2E-48/P1 (scientific session, measured 2026-10-29)

See `PROGRESS.md` → Current phase for the same content; the short form: round 1 (E48A1..A15)
pre-registered at `284b630`, measured 15 ok/15; round 2 (E48B1..B9) pre-registered at
`3401821`, measured 9 ok/9; goldens in `golden/e48p1/` (uncommitted). DR laws measured this
phase, all read out of the `.REL` records:

- `^b` test on BIT(1): `3A <cell> / B7 / FA + 2-byte operand filler (00 00, filled later by
  SET-LC/RELOC)` = **7 bytes** (the earlier "8 bytes / 5-byte chain" wording was a miscount;
  RESULTS.md §5 supersedes it). CREATE 0052, E48A1 000C, E48A5 0011, E48A12 000C, E48B1,
  E48B7; positive form identical with `F2` (E48A3 0006, E48B2, FLTPOLY2 0075). `DO WHILE`
  exit = address just after the loop-tail `C3 <test>` (tail+3; E48A1 fill 0011→0044);
  IF/ELSE false-chain targets the else (E48A2 000B→0027); no-else IF skip → next statement
  (E48B1 inner 001F→0028).
- `b = (cond)`: materialiser, then `D6 01 / 9F` (`SUI 01/SBB A`: 0→FF, nonzero→00), then
  `32 <cell>`. E48A6 (auto varying = literal) measured **17 bytes** `LXI H,*S(lit) / LXI D,var
  / MVI A,litlen / CALL ?SCVCM / D6 01 / 9F / 32 b`. CREATE's own store at 008F is **18 bytes**
  `LXI H,var / EB(XCHG) / LXI H,*S(lit) / 3E 03 / ?SCVCM / D6 01 / 9F / 32` — same registers,
  different load order; the **discriminator is [TBD]** (only one SCVCM site exists in CREATE;
  all 18 E48 sites use the LXI-D form). The earlier "16 bytes, 2A/LHLD" reading was wrong
  (RESULTS.md §5).
- Materialiser by class (RESULTS.md §3.2): `k = 0` → `LXI H,k / MOV A,M / INX H / ORA M`;
  `k = c` |c| ≥ 4 → `LHLD k / LXI B,two's-comp / DAD B(0x09) / MOV A,H / ORA L` — **no DR
  defect: byte 0x09 is standard DAD B and my `hl_bias` already matches** ([C143] compare-route
  threshold ≤3 confirmed by E48A13 `= 3` = DCX H ×3 vs E48A12 `= 4` = LXI B,FFFC); `k ^= 0`
  AND `^(k = 0)` (value) → same `=0` ladder with `ADI FF / SBB A` (C6 FF/9F) — never CMA;
  `k > 0` → `LXI H,k / XOR A / CMP M / INX H / SBB M` (result already 00/FF, no tail);
  `f = (b = '1'b)` → `LDA / ANI 80 / SUI 80 / D6 01 / 9F / 32`.
- `^(cond)` in a test **inverts the skip byte** (`C2 JNZ → CA JZ`, emitted as `CA 00 00` +
  SET-LC/RELOC fill, E48A13); `if k = 0 & b then` materialises the left into A, then
  `PUSH PSW / LDA b / POP B / ANA B` under one `F2` (E48A14 000C-001D).
- `put list(b)` is **accepted**: `LDA cell / MVI B,01 / CALL ?QB08C / CALL ?PNBOP` (7 objects).
- STATIC bits are DATA-absolute and adjacent (E48B5 0000/0001); `dcl s char(3) static
  initial('AB')` is accepted, cell `41 42 20`, and the PUT reuses that cell — DATA area 3, zero
  pool bytes (E48B6). I refuse both today.
- **My DATA-size double-count — FIXED and committed.** `bind.ml` `section2`'s `span` charged
  STATIC rows; a8d1c3a excludes them (`static_rows` from `bind_rows`' 4-tuple auto flag). E48A3
  (DR 3) and E48A4 (DR 8) are now byte-identical whole-file to the goldens; the gate stayed
  **1074 byte-exact / 0 fail**, census unchanged (15 EXACT). `codegen.ml:12340` needed no change.

## Last verified state (Pi Handoff deployment window — superseded above for work state)

Verified **in the deployment session itself** (i.e. measured now, not quoted from a report):

- Repo `/home/john/projects/sushiworks/pli80`, branch `main`; scientific HEAD
  `0a50fc4c745838e3af1641c8a6f68fd17ed1371a`, with the 2026-10-29 infrastructure chain on top
  (`aa03eeb` renewal activation, `88248b1` renewal e2e test record, plus the closure commits);
  working tree clean (0 porcelain lines) at every checkpoint of this window.
- 12 028 tracked files; 471 102 ignored files present; 37 entries at the repository root.
- Nested third-party repos untouched and clean: `thirdparty/PLI-2000` @
  `c6f0f2ddd9c2100781ce6fb65d79d3039ac94e2a`, `thirdparty/z80pack` @
  `91fd28eb04e675c2127df88ed3f40675e15282e2`.
- `/tmp/wt_base` worktree and `.git/worktrees/` metadata left exactly as found; no branch
  switched; no `clean`/`reset`/destructive checkout run.
- Pi 1.4.0 at `/usr/bin/pi` under the production profile `/home/john/.sushi/pi`;
  `.sushibeta/pi` not used.
- Pi Handoff `v0.1.0-dev.1` (`2ea6219`) is installed and **validated in the real runtime**:
  the extension loads, `/guard status` reports model `sushi/Qwen3.8-Flash-Next-Sushi-STQ-2.75bpw`,
  window 220 000, maxOutput 65 536, reserve 20 000; read-only mode wrote nothing; a controlled
  writable session produced schema-v3 checkpoint blocks in both files, `current` freshness and a
  `READY` attestation, and a level-3 automatic checkpoint preserved substantive notes verbatim.
  Manual prose outside the managed blocks was byte-identical before and after every guard write;
  `GOAL.md`/`LEARNINGS.md` were never written by the guard; all runtime files stayed inside the
  ignored `.pi-guard/`.

Verified **from committed reports, NOT re-run in this session** (treat as recorded results,
not as fresh measurements):

- Latest recorded gate verdict (`spec/lab-evidence/e2e42-p2c/RESULTS.md` §8, and the commits
  `1e5fe03`…`0a50fc4` on top of it): 1074 byte-exact / 0 fail, negative panel 184/184 refused,
  divergence panel 9/9, coverage 102 rows, runtime panel 71/71 as recorded.
- Phase: **E2E-42/P2c** — named-file `PUT FILE … SKIP` bank pre-registered, measured against DR,
  and lowered; claims through **[C308]**.
- Known open scientific item recorded there: `CREATE` still does not compile; remaining blockers
  are `^eofile` inside a `DO WHILE` condition and a store into `BIT(1)` from a condition — neither
  related to PUT. Also recorded, deliberately unfixed: `pli80c`'s `wrote … (data=N)` summary line
  reports a number that is not the DATA segment length.

## Last verified state — E2E-48/P1 COMPLETE for the 24-probe bank (session started 19:36 UTC, 2026-10-29)

**All 24 probes of `golden/e48p1/` are now whole-file byte-identical**, and all 24 are REGISTERED
on the byte panel. Measured in this session, in this order:

- `f839f52` — the census drift the gate aborted on was PROGRESS, not regression: CREATE's
  first-refusal message had moved past `(^ eofile)` (fixed by the `371a12e` NegL arm) and past
  `eofile = (name = 'EOF')` (fixed by `bit_cond_mat`) to `GET LIST of unknown variable name [TBD]`.
  Cause measured: `pli80c.ml` never expands `%include`, so `name` (RECORD.DCL) is unbound. Census
  re-measured through `tools/corpus_census.py --check <prev copy>`; counts IDENTICAL.
  Gate then measured **1074 byte-exact / 0 fail**, negative 184/184, divergence 9/9 — i.e. the
  `371a12e` arms broke nothing.
- `fa09b97` — `bit_store_cond_bytes` added to the prescan: my `371a12e` store arm allocated the
  `?SCVCM` literal's pool cell but `prescan_expr` has no `Econd` arm, so it was never demanded.
  Minimal measured repro: `b = (name = 'EOF');` demanded 1, allocated 4. **E48A12 became exact
  (15/24).**
- `df4b9c8` — step 4, the BIT(1) PUT item: `3A cell / 06 01 / CD ?QB08C / CD ?PNBOP`, nine sites
  (A15 000F sole item, A6 0038, A7 002C+005D, A8, A9, A10, A11, B8 0038). `?PNBOP` REPLACES the
  shared `tail true ()` `?PNCOP` (one tail per item: A6 0035 PNCOP, 0040 PNBOP, 0043 QIOOP). Two
  classifier admissions (Vbit1 in `only_literals_and_chars`; Vbit1 -> false in the blocking
  `List.exists`) plus three named refusals for unmeasured shapes (PUT EDIT, non-final bit item,
  file attach). The `authorize_file_item` reason that claimed "the console route refuses this class
  too" is kept as written and labelled SUPERSEDED (P15 falsified it). **23/24 exact.**
- `613385b` — step 5, STATIC on CHARACTER per R6: `RTchar (n, false)` with a literal INITIAL no
  longer than the extent, cell = full extent blank-padded (`41 42 20`), DATA 3 = 3 static + 0 pool,
  read back by the existing Vfix PUT arm at the DECLARED length. Refused on purpose: no INITIAL, a
  non-literal/longer initialiser, STATIC-on-CHARACTER **VARYING** (catch-all keeps its EXACT words
  for gate rows E46F5 and the FIXED-BINARY(15,0) row), and a store INTO a static char (scratch s1
  proved my automatic route would pool the literal beside the static cell, DATA 3 -> 5 — unmeasured).
  Census re-measured: counts identical, 5 msg deltas (REPORT advanced to `OPEN option KEYED`,
  MPMCALLB to `STATIC on POINTER MEMBER OF CPB@390`; EXPR2/FSCAN/LOAN2 same blocker). **24/24 exact.**
- `992ccad` — panel + claims. 24 SPECIMENS rows (byte tier ONLY: no `spec/RUNTIME.txt` rows, because
  this round captured .REL/.PRN evidence and eight probes read the console with `get list`),
  `--update-inventory` wrote INVENTORY.txt (1098 entries), and claims **C309-C316** record RESULTS §3
  as measured law with the [TBD] list inside C310. Final gate at this commit, measured:
  **1098 byte-exact / 0 fail of 1098**, negative panel 184/184 refused, divergence 9/9, coverage
  102 rows 0 errors, census `--verify` clean (EXACT 15 / DIFFERS 0 / REFUSED 26 / UNEXPECTED 0), rc=0.

Verification method notes for the successor: builds compared cache-neutrally (clean rebuild in a
scratch tree vs `git show <base>:ocaml/lib/codegen.ml`, warning multiset 22/15/28/2/14/2/17/26 —
unchanged); the sweep is
`for n in E48A{1..15} E48B{1..9}; do ./ocaml/_build/default/bin/pli80c.exe probes/$n.PLI /tmp/x/$n.REL && cmp /tmp/x/$n.REL golden/e48p1/$n/$n.REL; done`.

## Unfinished operations — E2E-48/P1 (open at this checkpoint)

- **No half-finished edit.** Working tree clean at this checkpoint except the three handoff files.
- OPEN (recorded, deliberately not started at this boundary): `spec/COVERAGE.tsv` rows for this
  bank's COND/STOR/IO shapes. `coverage_check` passes without them (it validates citations, not
  completeness), so this is a recorded gap, not a failing row.
- `[TBD]` items that must NOT be guessed (all inside C310/C313/C314): the CREATE-vs-E48 SCVCM
  load-order discriminator (18-byte `LXI H,var / XCHG / LXI H,lit` vs 17-byte `LXI H,lit / LXI D,var`
  — no probe varied it); the BIT-store materialiser for `k = c` with |c| in {1,2,3}; `= '0'b` as a
  materialised store; `^(cond)` in a STORE beyond `^(k = 0)`; nested `&` shapes beyond E48A14;
  a bit PUT item that is not final; a store into a STATIC CHARACTER; STATIC-on-CHARACTER VARYING.
- CREATE is NOT byte-exact. Its measured blocker is now front-end: `%include` is never expanded by
  `pli80c.ml` (only `bin/pli80bind.ml` does), so `get list (name)` refuses with an unbound name.

> STATUS 2026-10-30 (E2E-48/P2c): the SCVCM load-order discriminator in the second bullet is
> MEASURED and answered (operand CLASS; RESULTS sections 1-2 of e2e48-p2c); the other [TBD]
> items of that list are UNCHANGED and still must not be guessed. The COVERAGE rows remain
> unwritten (now sub-task 7 of the current Next action).

## Next action (superseded by the section below: its steps 1-4 are DONE — run 1 botched (e48p2d, kept), wrap amendment 60a2c06, run 2 = 10 ok/10 at golden/e48p2db committed d28ff5e, RESULTS.md written)

## Next action — E2E-48/P2e: LOWER the six RESULTS §2 arms (NOT STARTED), then claims + registration + FULL GATE

> **STATUS 2026-10-30 (renewal 7/8, session 01a18dd2, HEAD `e2b77ba`, tree clean except the
> OPERATOR's `handoff.config.json` edit).** Round 5 is pre-registered (`421656a`), measured
> (**7 ok / 8**) and committed with its goldens (`e2b77ba`). **No `ocaml/` file has been edited
> for this round** — every E48E probe is still a named refusal of mine. Read
> `spec/lab-evidence/e2e48-p2e/RESULTS.md` (§1 table, §2 six laws, §3 what stays unmeasured) and
> `HYPOTHESES.md` before editing; claims are OWED (next free ids **C327+**).

**EXACT NEXT ACTION — six arms, ONE per commit, `cd ocaml && eval $(opam env) && dune build` +
the cmp sweep after EACH (LEARNINGS rule: one arm, one build, one sweep).**
Sweep loop (expect E48E 7/7 after all arms; E48E6 must KEEP refusing):

    for n in 1 2 3 4 5 7 8; do ./ocaml/_build/default/bin/pli80c.exe probes/E48E$n.PLI /tmp/sw/E48E$n.REL \
      && cmp /tmp/sw/E48E$n.REL golden/e48p2e/E48E$n/E48E$n.REL && echo "E48E$n IDENTICAL"; done

Then the regression sweeps: E48D1..D10 (`golden/e48p2db`) 10/10, E48C1..C9 9/9, e48p1 24/24,
E46K1/K3 2/2 (`golden/e48p2retire`), and the FULL negative panel with GATE semantics (CRLF +
`^Z`, stderr) — 181 rows, and E46K14's marker must NOT move (see arm 2).

1. **Arm 1 — ladder classes** (`bit_cond_mat`, ocaml/lib/codegen.ml:7128; the two guard arms at
   ~7196 `Some (v, kk) when kk >= 2 && kk <= 3` and ~7208 `when kk >= 4`). Replace both guards
   with ONE `when abs kk >= 1` body — `cmp_load_deref st v.Ast.orig; hl_bias st (-kk);
   mov_a_h / 0xb5 / flag ()` — which already yields E48E1 (`-1` -> one `DCX`), E48E2 (`+2` -> two
   `INX`) and E48E4's head (`-5` -> `LXI B,FFFB / DAD`). **`hl_bias` (codegen.ml:6749) needs NO
   change** — verified: it keys on `abs b`, so the sign law of §2.1 is already its law. Update the
   docstring at ~7128-7146 (it states `k = 1` and `c < 0` as unmeasured) as a traceable
   SUPERSEDED append, original kept. No pool bytes involved -> NO prescan twin needed.
2. **Arm 2 — negated ladder VALUE** (`bit_cond_mat`'s `Ast.Eprefix (Ast.NegL, x)` arm at ~7252,
   today `Some (v, 0)` only). Add the ladder body for `|kk| >= 1` with `flag_neg ()`
   (`C6 FF / 9F`) — E48E3 0006 (`2A / 2B 2B / 7C / B5 / C6 FF / 9F / 32`) and E48E4 0006
   (`2A / 11 FB FF / 09 / ... / C6 FF / 9F / 32`). Do NOT add `^=` over a ladder or `^(string
   compare)` — §3 records neither. **AFTER this arm, RE-MEASURE E46K14's refusal through the
   binary (gate CRLF+`^Z` semantics): its marker must be byte-identical; if it moved, FIX the arm,
   never re-pin.** E46K14 is `dr-refuses` NOW (proved by E48E6's `BIT REQ`, no `.REL`), so the
   `imem_refuse` WHY-string at codegen.ml:3895-3905 — which currently says the truthiness shape
   "has no DR object anywhere" — must be corrected traceably to cite
   `golden/e48p2e/E48E6/E48E6.PRN` as a MEASURED DR refusal (append, keep the original words).
3. **Arm 3 — `= '0'b' VALUE** (the fallback inside `bit_cond_mat`'s `Eq` arm, ~7222-7232, which
   admits only `Ast.Ebit "1"`). Emit for `Ast.Ebit "0"`: `3A *D(b) / E6 80 / D6 01 / 9F`
   (E48E5 0006, 11 bytes incl. the `32` STA) — i.e. the `'1'b` head WITHOUT the `D6 80` step.
   `bit_store_cond_bytes` demands nothing here (no pool cell), so no prescan change.
4. **Arm 4 — FIXED member in TEST via `?SCCCM`** (the biggest arm; §2.4). `str_side` (6870)
   classifies only `Vimem m when m.varying -> Some (`Imem name)`; add a FIXED-member variant that
   carries `m.cap` (the declared extent IS in `mem_char`, codegen.ml:26-27). Add a new
   literal-LEFT/fixed-RIGHT encoder producing exactly
   `21 *D(member) / 11 *D(pool lit) / 06 len / 3E cap / CD ?SCCCM`, used by `lower_test_skip0`
   (the guard at 7597 and the destructuring at 7609) — NOT by `bit_cond_mat`: §2.4 measures TEST
   only and §3 says a fixed member in a STORE is unmeasured, so the STORE route must keep
   refusing it. **THE DEMAND TWIN IS MANDATORY (the fa09b97/e21281a law):** `prescan_cond`'s
   `is_var` (~2981) currently returns `m.varying`; widen it to admit a FIXED internal member
   ONLY because the TEST route now admits it — demand and lowering stay ONE predicate, or the
   C152 pool invariant dies. Verify DATA 000B for E48E7 against the golden.
5. **Arm 5 — bit item behind a file attach** (`authorize_file_item`, refusal text quoted in
   `BASELINE-MINE.txt` E48E8; the console bit chain already exists at ~10775 `Vbit1`). Admit
   `Vbit1` on the file route and reuse the SAME chain bytes
   (`3A *D(b) / 06 01 / CD ?QB08C / CD ?PNBOP`) inside [C296]'s frame; §2.5 + E46L3 prove the
   chain is route-invariant. PUT EDIT of a bit item and every other unadmitted file class stay
   refused. Keep the falsified premise of the removed guard visible as a SUPERSEDED comment.
6. **Claims + registration + gate.** Record C327+ from RESULTS §2 ONLY (each citing its golden),
   classify §2.6 as `dr-refuses` and arms 1-5 as `my-gap`; append the traceable correction to
   **[C296]** ("`LXI H,<fcb>`" is really `LXI H,*C(0000)`, a CODE self-address — HYPOTHESES.md
   §Prior-evidence has the byte dump) and to [C324]/[C310]'s [TBD] clauses (closed by
   reference, originals kept). Register E48E1..E48E5, E48E7, E48E8 in the gate's own
   `SPECIMENS.update({...})` dict in `tools/e2e_gate.py` (NOT `spec/SPECIMENS.tsv`, which is a
   stale E2E-39 artefact; precedents `992ccad`/`f67cc6d`/`adbfa2a`), **BYTE TIER ONLY — no
   `spec/RUNTIME.txt` and no `OUTPUT_CHECK` row may come from this round**. E48E6 is NOT a
   specimen: it has no `.REL`; if a negative row for it is wanted it must go through the gate's
   write path with an explicit reason, never by hand-editing a verdict. Then
   `python3 tools/e2e_gate.py --update-inventory` (review the diff line by line), census
   `cp spec/census/corpus-census.json /tmp/census-prev.json && python3 tools/corpus_census.py
   --check /tmp/census-prev.json` (re-read EVERY msg delta; a corpus advance is not a
   regression), `python3 tools/coverage_check.py`, `registration_audit`, and the FULL GATE
   `python3 tools/e2e_gate.py` — **report ACTUAL numbers, never expected** (baseline was 1120/0,
   negative 181/181, divergence 9/9, coverage 113 rows). Then `spec/COVERAGE.tsv` rows for the
   five new shapes vs the new claims (15 columns, `manual_ref = NONE:<why>`, MEASURED rows cite
   probes named by their OWN claims; `coverage_check` REWRITES
   `spec/census/coverage-stats.json` — commit that path when it changes).

**Standing:** never touch `golden/e48p1`, `e48p2c`, `e48p2d` (botched run), `e48p2db`,
`e48p2retire`, `e42p1c`, `e42p2a`, `e42p2b`, `first8080u`, `e48p2e` (new goldens — evidence);
implement NOTHING from RESULTS §3 (fixed member in a STORE, member-vs-member, BASED member in a
condition, over-extent INITIAL/store, any runtime claim); no `%include`/LOAN2 work without its
own pre-registered round; **do not commit or revert `handoff.config.json` — the
`workingContextWindow` 95000 -> 145000 edit is the OPERATOR's**; no push; probes <= 71 cols and
CRLF + `^Z`; build needs `eval $(opam env)`; **never name a probe variable `c`** (it reads as a
procedure call — see LEARNINGS); renewal 8/8 is the LAST hop under the cap.

## Next action (superseded: choice (D) was taken and executed as E2E-48/P2e — prereg 421656a, oracle 7 ok/8, goldens+RESULTS at e2b77ba; lowering OWED per the section above)

> **STATUS 2026-10-30 (renewal 6/8, session 01a18dba, HEAD `218b474`, tree clean).** **STEP 7 IS
> DONE AND MEASURED.** Six COVERAGE rows written vs C321-C326 (`STOR.CHAR_STATIC_STORE`,
> `DECL.STATIC_CHAR_EMPTY_INIT`, `FILE.OPEN_TITLE_STATIC`, `STOR.BIT1_COND_LADDER_2_3`,
> `IO.PUT_BIT1_NONFINAL_ITEM`, `COND.MEMBER_RIGHT_TEST`; 15 columns, `manual_ref=NONE:<why>` or the
> verified `p60:9.5` cite, byte tier so `runtime=NONE`), plus **19 traceable appends** correcting the
> falsified boundary/contract clauses on lines formerly 108/109/111/112 and on
> `AGG.INTERNAL_CHAR_MEMBER`, `NEG.MEMBER_USE_PERIMETER`, `FILE.OPEN_TITLE_VAR`, `FILE.PUT_LIST_VAR`
> (originals verified byte-preserved as prefixes; the only non-append cells are the four deliberate
> parity-count fixes 4→5, 5→9, 18→19, 4→6, 5→12). `[C323]`'s `20x11` blank-run was falsified by a
> direct `reldump` of `golden/e48p2db/E48D1` and `golden/e42p1c/E46F5` (twelve `20`, 15 bytes) and
> corrected as an append in `spec/CLAIMS.md`. **MEASURED: `coverage_check` 113 rows / 0 errors /
> 0 warnings; FULL GATE rc=0 = 1120 byte-exact / 0 fail of 1120, negative 181/181, divergence 9/9,
> census EXACT 15 / DIFFERS 0 / REFUSED 26 / UNEXPECTED 0, prose clean** (log `/tmp/gate_p2d7.txt`).
> No `ocaml/` file changed. **Operator note:** `handoff.config.json` is MODIFIED in the working
> tree at this boundary (`workingContextWindow` 95000 → 145000) by the operator, not by any session;
> leave it uncommitted and untouched unless the operator authorises committing it.
> **THE EXACT NEXT ACTION is a DECISION, not an arm.** Pick ONE, write its probe bank +
> `HYPOTHESES.md` and commit them BEFORE any oracle call (PROTOCOL §1), then run it:
> (A) `%include` expansion for CREATE (front-end my-gap; needs its own round);
> (B) LOAN2's `variable i declared with conflicting kinds` prescan scope my-gap (design change,
> ~15 `pd_vars` call sites);
> (C) a RUNTIME round for the RESULTS §3 [TBD] list (length rewrite of `?SMCVM`, empty-varying PUT
> output) — the only path that can lift these shapes from byte tier to `spec/RUNTIME.txt`;
> (D) a small byte round for the still-unmeasured bit/char edges (`k = 1`, negative `c`, bit behind
> a file attach, BASED member cond-store, over-extent INITIAL/store, member truthiness,
> member-vs-member, FIXED member compare, and LOAN2's `by '^z'` control-character PUT item).
> Standing: never touch `golden/e48p1|e48p2c|e48p2d|e48p2db|e48p2retire|e42p1c|first8080u`; no
> guessing at a [TBD]; no push; build needs `eval $(opam env)`; probes ≤71 columns (run 1 died on
> that); renewal 7/8.

## Next action - E2E-48/P2d step 7 ONLY: the six COVERAGE.tsv rows, `coverage_check`, gate re-run

> **STATUS 2026-10-30 (recovery session 01a18db4, chain 5/8, HEAD `47936e5`, L4 before any
> edit).** Session verified the boundary and committed the uncommitted guard g41
> refresh+attestation (session 01a18db1's `/handoff finalize`; both diffs were pure managed
> blocks, `source-config` advanced to the committed dev.3 `handoff.config.json` 5fe3a5d…) as
> `47936e5`; tree clean. **ZERO COVERAGE rows written yet — step 7 OWED in full.** Evidence
> re-read this session and CONFIRMED present: claims **C321–C326** at `spec/CLAIMS.md:7375-7441`
> (each names its E48D probes); `spec/lab-evidence/e2e48-p2d/RESULTS.md` §1–§3 (8 laws, 2 kept
> MISSes); COVERAGE.tsv has **107 data rows**, the correction targets are rows at lines
> **108 `COND.BIT1_NEG_TEST`, 109 `STOR.BIT1_COND_STORE` (boundary text still claims |c|∈{1,2,3}
> refused and stores-into-static refused — FALSIFIED by C321/C322/C324, correct as traceable
> append), 111 `IO.PUT_BIT1_ITEM` (non-final clause falsified by C325), 112 `DECL.STATIC_CHAR`
> (empty-initial and store-into-static clauses falsified by C321/C322)**; `AGG.INTERNAL_CHAR_MEMBER`
> (line 105) also names member stores worth a coherence glance. Validator facts (read from
> `tools/coverage_check.py`): E48D1..D10 are panel keys (INVENTORY) so col-11 entries resolve;
> MEASURED/SINGLE_SAMPLE rows need ≥1 col-11 probe mentioned by a cited claim (stem match counts,
> a path probe is self-sufficient); runtime col regex is
> `^(NONE|(INDEPENDENT|DR_ORACLE|BOTH):\d+)$`; rel_parity `^(NONE|EXACT:\d+|DIVERGENT:\d+|MIXED:\d+/\d+)$`;
> `coverage_check` REWRITES `spec/census/coverage-stats.json` on every run — check whether it
> changes and commit that path when it does. Renewal hop 6/8 carries this step; everything below
> unchanged.
> **STATUS 2026-10-30 (renewal 5/8 successor, session 01a18d83, HEAD `adbfa2a`).** **STEP 4
> (REGISTRATION + FULL GATE) IS DONE AND MEASURED. No lowering remains.** Measured by that
> session: sweeps re-run through its own binary FIRST (E48D 10/10, e48p1 24/24, e48p2c 9/9,
> e48p2retire 2/2 whole-file byte-identical; clean-rebuild scratch warning multiset 126 =
> 28/26/22/17/15/14/2/2); the ten rows added to the gate's **`SPECIMENS` dict in
> `tools/e2e_gate.py`** (NOT `spec/SPECIMENS.tsv` — that file is a stale 1-row artefact of
> E2E-39; `992ccad`/`f67cc6d` are the precedents), byte tier ONLY, no RUNTIME/OUTPUT_CHECK rows;
> `--update-inventory` → **INVENTORY 1301 = 1120 specimens + 181 refusals**, diff reviewed line by
> line (ten new D rows + E46F5's `refusal → specimen`, the un-exported leftover of arm (b));
> census `--check` → **counts IDENTICAL 15/0/26/0** with BOTH deltas verified as genuine
> **ADVANCES** past arm (a) (EXPR2 → `ON ERROR … line 24`, FSCAN → `PUT EDIT operator X`);
> **FULL GATE rc=0 = 1120 byte-exact / 0 fail, negative 181/181, divergence 9/9, coverage 107 rows
> 0 errors, census --verify clean, prose clean**; `registration_audit` 1301 entries 0 errors;
> `inventory_check` `[]`.

**THE EXACT NEXT ACTION** (nothing else is owed by this phase; no code changes):
1. Write the six `spec/COVERAGE.tsv` rows against the CURRENT ledger: TITLE on a STATIC operand
   **[C323]** (probes E48D1,D2,D3 + E46F5), stores into STATIC CHARACTER **[C321]** (E48D6,D7,
   D10's automatic `?SMCVM` site), empty `initial('')` **[C322]** (E48D4,D5), store ladder
   |c| ∈ {2,3} **[C324]** (E48D8 — fold into/annotate the existing `STOR.BIT1_COND_STORE` row,
   whose col-13 boundary text STILL says |c| ∈ {1,2,3} and stores into static cells are refused:
   that clause is now FALSIFIED by C321/C322/C324 and must be corrected as a traceable append,
   original kept), non-final BIT(1) PUT item **[C325]** (E48D9 — same for `IO.PUT_BIT1_ITEM`,
   whose boundary names the non-final position as refused), member-as-RIGHT in TEST **[C326]**
   (E48D10 — same for `COND.BIT1_NEG_TEST`/the compare row if it names the refusal).
   Format: 15 tab-separated columns; `manual_ref = NONE:<why>`; col 11 = probes EXACT on this row;
   col 12 = corpus names (must exist in the census); col 14 confidence; col 15 provenance cites the
   claim ids AND the `spec/lab-evidence/e2e48-p2d/RESULTS.md` path. A MEASURED row needs ≥1 of its
   col-11 probes mentioned by its cited claims (`tools/coverage_check.py:203-247`; stem matches
   count, `E48D` is matched by any `E48D…` in the claim text).
2. `python3 tools/coverage_check.py` (expect 0 errors) then `python3 tools/e2e_gate.py` — report
   ACTUAL numbers (expect 1120/0 unchanged; coverage rows 107 → 113).
3. Commit rows + PROGRESS/HANDOFF status; refresh + attest the checkpoint (`/handoff`,
   `/handoff ready`) and close with `handoff_finalize`.
**Standing:** byte tier only for this bank — no `spec/RUNTIME.txt`/`OUTPUT_CHECK` row may come from
it (runtime length rewrite and empty-varying PUT output are [TBD]); never touch `golden/e48p1`,
`e48p2c`, `e48p2d` (botched run, kept as evidence), `e48p2retire`, `e42p1c`, `first8080u`;
implement no RESULTS §3 shape (`k = 1`, negative `c`, bit behind a file attach, BASED member in a
condition store, over-extent INITIAL/store, member truthiness, member-vs-member, FIXED member
compare); no `%include`/LOAN2 work without its own pre-registered round; no push; build needs
`eval $(opam env)`; probes ≤71 columns.

## Next action (superseded by the section above: step 4 registration is DONE and MEASURED at `adbfa2a`) — E2E-48/P2d: LOWER the three remaining arms (d)(e)(f), then register + FULL GATE

**DONE + MEASURED this session (01a18cf9, renewal 2/8; each commit built with `eval $(opam env) &&
dune build`, warning multiset unchanged 22/15/28/2/14/2/17/26, sweeps e48p1 24/24, e48c 9/9):**
- Baseline re-verified first: D3/D5/D7 byte-identical, all 7 named refusals reproduced verbatim.
- `6545b5d` **(a)** E48D4 empty `initial('')` on STATIC VARYING — dropped only the
  `String.length v > 0` guard in the `RTchar (n,true)` static placement; existing formula yields
  `00 + n×20` in place ([C322]). D4 IDENTICAL.
- `6491981` **(b)** TITLE on STATIC operand class-invariant ([C323]) — removed the 3ee414a refusal
  in `lower_open`'s `Vvar` arm; my D1 == DR's E46F5 object except the 9 module-name bytes
  (`cmp -l` offsets 4,5,6/18,19,20/26,27,28). **E46F5 PROMOTED** three-place (SPECIMENS cites
  `golden/e42p1c/E46F5/E46F5.REL`; REJECTS row + NEG_META stamp removed, superseded text kept as
  comments). Negative panel re-run with GATE semantics (CRLF + `^Z`, stderr): **181/181 refused,
  0 anomalies**; `registration_audit` called directly: clean, **1110 specimens / 181 rejects**.
- `a72ce43` **(c)** static FIXED store ([C321]) — retired the R6 refusal in `store_char`'s `Vfix`
  arm; DR's head is the automatic V106 route verbatim (`21 *D(static cell)/11 *D(fresh pool)/
  3E extent/06 len/CD ?SMCCM`), literal pooled. **No new encoder and NO prescan twin needed**
  (the `Sstring` store demand at codegen.ml:~3127 is already class-independent — measured, not
  assumed). D6 IDENTICAL. len=0/>cap/=cap refusals kept (RESULTS §3).
- State: **D1–D7 whole-file byte-identical to `golden/e48p2db/`; D8/D9/D10 still refused by name**;
  tree clean at HEAD; `ocaml/` builds.

**EXACT NEXT ACTION (successor): three arms, ONE per commit, same build+cmp discipline, order (d)(e)(f):**

> STATUS 2026-10-30 (renewal 3/8, session 01a18d44): **arms (d) and (e) are DONE and committed**
> (`18a06c0` ladder |c|2,3 via the one `hl_bias` authority [C324]; `1e8acb2` non-final bit PUT item
> accepted [C325], guard removed with its falsified premise kept verbatim). **D1-D9 whole-file
> byte-identical to `golden/e48p2db/`**; sweeps 24/24 + 9/9; negative panel 181/181, 0 anomalies;
> clean-rebuild warning multiset unchanged (126). D8's identity required BOTH arms (its
> `put list('B=', b, ...)` carries a non-final bit item) — the per-step "expect D8 after (d)" was
> jointly false, recorded in LEARNINGS. **Only step 3 (arm f) and step 4 (registration+gate)
> remain.**

> STATUS 2026-10-30 (renewal 4/8 successor, session 01a18d51, HEAD `e21281a`): **ARM (f) IS DONE
> AND MEASURED — all six arms (a)-(f) of E2E-48/P2d have landed; D1..D10 are 10/10 whole-file
> byte-identical to `golden/e48p2db/`.** `e21281a` = TEST-route `str_cmp_shape_rev` calls widened
> to `~imem:true` ([C326], encoder reused) **plus the prescan demand twin** — `prescan_cond`'s
> literal-LEFT clause `is_cell b` → `is_var b`. That second half was NOT in the inherited spec and
> is a REAL latent my-gap measured before the arm: a literal-left/member-right TEST compare whose
> literal appears nowhere else died with "prescan demanded 0 pool bytes, lowering allocated 2"
> (E29C9 masked it only because its store demands the same content-addressed cell). Sweeps at
> `e21281a`: e48p1 24/24, e48c 9/9, E46K14 (`if line then`) STILL refuses and its pinned marker was
> RE-MEASURED through this binary — unchanged, not re-pinned. Comparison WHY-string corrected
> traceably (truthiness of a member, member-vs-member, FIXED members stay unmeasured).
>
> **EXACT NEXT ACTION (successor) = step 4 ONLY — REGISTRATION + GATE, no further lowering:**
> 1. `cd ocaml && eval $(opam env) && dune build` (rc=0; warning multiset must stay 126 =
>    28/26/22/17/15/14/2/2 — verify by clean rebuild, cache-neutral).
> 2. `spec/SPECIMENS.tsv`: add E48D1..D10 at `golden/e48p2db/<n>/<n>.REL`, **byte tier ONLY — no
>    `spec/RUNTIME.txt` rows from this round** (RESULTS §3: no runtime evidence was captured).
> 3. `python3 tools/e2e_gate.py --update-inventory` (expect 1110 → 1120 rows; review the diff line
>    by line: the only content changes should be the ten new specimen rows).
> 4. Census: `cp spec/census/corpus-census.json /tmp/census-prev.json && python3
>    tools/corpus_census.py --check /tmp/census-prev.json` — EXPR2/FSCAN are EXPECTED to ADVANCE
>    past the empty-`initial('')` refusal (arm (a)); **re-read EVERY msg delta** and commit the
>    snapshot. A corpus advance is not a regression.
> 5. FULL GATE `python3 tools/e2e_gate.py` — **report ACTUAL numbers, never expected** (~1120/0
>    byte tier, negative panel 181/181, divergence 9/9, coverage, census --verify, rc=0). Run
>    `registration_audit` too: the REJECTS/NEG_META symmetry rule is invisible to counts.
> 6. `spec/COVERAGE.tsv` rows for the six new shapes (COND/STOR/IO/DECL/TITLE) against the CURRENT
>    ledger C321-C326, 15 columns, `manual_ref = NONE:<why>`, MEASURED rows cite probes named by
>    their OWN claims → `python3 tools/coverage_check.py` → gate re-run. Then update PROGRESS /
>    HANDOFF and close.
> **Standing:** never touch golden/e48p1, e48p2c, e48p2d (botched run), e48p2retire, e42p1c,
> first8080u; do NOT implement a RESULTS §3 shape (runtime length rewrite, `k = 1`/negative `c`,
> bit behind a file attach, BASED member in a condition STORE, over-extent INITIAL/store, member
> truthiness, member-vs-member, FIXED member compare); no `%include`/LOAN2 work without its own
> pre-registered round; no push; probes ≤71 cols; build needs `eval $(opam env)`.

> STATUS 2026-10-30 (renewal 3/8 successor close, HEAD 3172642, tree clean except
> guard blocks): session committed arms (d) `18a06c0` and (e) `1e8acb2` (D1-D9 byte-identical;
> sweeps 24/24+9/9; negative 181/181 0 anomalies; clean-build multiset 126 unchanged).
> **ARM (f) NOT STARTED — exact landing spec (read from code, no edit yet):** TEST route
> `lower_test_skip0` arm at ocaml/lib/codegen.ml:7572-7585 matches
> `str_cmp_shape_rev st l rr` with the DEFAULT `imem=false`, so D10's
> `if 'AB' = line then` declines it and falls to `imem_refuse "comparison"` at :7770 (the
> message D10 prints today). Arm (f) = pass `~imem:true` at BOTH the guard (7573) and the
> destructuring match (7575); the `Some (`Lit, `Imem k) when imem` encoder at :6972-6979
> already emits `21 *D(member cell) / 11 *S(pool lit) / 06 len / ?SCCVM`, and the arm adds
> `C2 fill + 2 slots` = exactly [C326]/E48D10 0013..0027 (skip to NEXT statement, [C309]).
> Update the :6941-6946 docstring (it states the TEST refusal as current law — supersede
> traceably). AFTER: re-measure E46K14 (`if line then` truthiness, different gate at 7770
> fallback) through the binary with gate CRLF+^Z semantics; its marker must NOT move; if it
> does, FIX the arm, never re-pin. Then step 4 registration: SPECIMENS E48D1..D10 byte tier
> only, --update-inventory, census --check, FULL GATE (report ACTUAL), COVERAGE rows.
> Build needs `eval $(opam env)`. No push.
1. **(d) D8 store ladder |c| ∈ {2,3}** ([C324]) — DONE `18a06c0` (with arm e for D8's put).
   Original step text kept for lineage: in `bit_cond_mat` (ocaml/lib/codegen.ml:7105):
   the `bin_lit` arms today are `Some (v,0)` and `Some (v,kk) when kk >= 4` (the latter =
   `cmp_load_deref / hl_bias (-kk) / MOV A,H / ORA L / flag`). Add ONLY |kk| ∈ {2,3}: DR is
   `2A *D(k) / 2B ×|c| / 7C / B5 / D6 01 / 9F / 32 *D(b)` (D8 0006 with two `2B`, 0013 with three)
   — i.e. `cmp_load_deref` then `d st 0x2b` |c| times, then `op_mov_a_h / 0xb5 / flag ()`.
   `k = 1` and negative `c` STAY refused (§3, no witness). Expect D8 IDENTICAL.
2. **(e) D9 non-final BIT(1) PUT item** ([C325]) — DONE `1e8acb2`. Original step text kept: — refusal text "a BIT(1) PUT item in a NON-FINAL
   position has no DR witness" at codegen.ml:~10542 (its premise is falsified by D9). Route = the
   FINAL-bit bytes already landed in `df4b9c8` (`3A cell / 06 01 / CD ?QB08C / CD ?PNBOP`) with its
   OWN PNBOP tail, the following literal chain untouched, exactly ONE final `?QIOOP` (D9
   000F..0027). PUT EDIT and bit-behind-file-attach STAY refused.
3. **(f) D10 member-as-RIGHT in TEST** ([C326]) — widen the TEST caller to the `~imem:true`
   `str_cmp_shape_rev` (codegen.ml:6947) that `bit_cond_mat` already uses (callers at 7557/7561
   pass the default); bytes `21 *D(member) / 11 *D(lit) / 06 len / CD ?SCCVM / C2 fill→next stmt`
   (D10 0013→0027, C309 skip rule). AFTER the arm, RE-MEASURE E46K14's refusal through the binary
   with gate CRLF semantics — if its marker moved, FIX the arm, never silently re-pin. A BASED
   member in a condition store stays refused.
4. **REGISTER + verify (report ACTUAL, never expected):** SPECIMENS.update E48D1..D10 at
   `golden/e48p2db/<n>/<n>.REL` (byte tier ONLY — NO `spec/RUNTIME.txt` rows from this round);
   `python3 tools/e2e_gate.py --update-inventory`; census
   `cp spec/census/corpus-census.json /tmp/census-prev.json && python3 tools/corpus_census.py --check /tmp/census-prev.json`
   (EXPR2/FSCAN expected to ADVANCE past the empty-initial refusal — re-read EVERY delta);
   FULL GATE `python3 tools/e2e_gate.py` (expect ~1110+9 = 1119-ish / 0 fail, negative 181 —
   REPORT THE MEASURED NUMBERS); then `spec/COVERAGE.tsv` rows for the new shapes +
   `python3 tools/coverage_check.py` + gate re-run.

**Standing:** never touch `golden/e48p1`, `e48p2c`, `e48p2d` (botched run), `e48p2retire`,
`e42p1c`, `first8080u`; never implement a RESULTS §3 shape (runtime length rewrite, k=1/negative c,
bit behind file attach, BASED cond-store, over-extent INITIAL/store); no `%include`/LOAN2 work; no
push; probes ≤71 cols; build needs `eval $(opam env)`; handoff prose edits make the managed
checkpoint stale — refresh + attest with `/handoff` then `/handoff ready`, close with
`handoff_finalize` (renewal gate refuses a stale checkpoint).

## Next action (superseded by the section above: arms (a)(b)(c) are DONE and committed as 6545b5d / 6491981 / a72ce43; E46F5 promoted; D1–D7 byte-identical)

**Done and measured (session 01a18d08, renewals chain 1/8, HEAD `aa4b5b4`):** step 5a (D3/D5/D7
byte-identical at `golden/e48p2db/`; D7 needs NO arm), REJECTS audit (ONE falsified row: E46F5;
E46K14 `if line then` truthiness is a DIFFERENT unmeasured shape and STAYS pinned), step 2 claims
**C321-C326** + appends to C310/C313/C314/C317 (`aa4b5b4`). Guard g24 attested (`35fe9fe`).
Build `cd ocaml && eval $(opam env) && dune build` rc=0; baseline 7 refusals re-verified verbatim.

**THE EXACT NEXT ACTION** (successor session): lower ONE arm per commit, each `dune build` +
`cmp` sweep against `golden/e48p2db/E48Dn.REL` + the 24-probe e48p1 and 9-probe e48c loops
(must stay 24/24, 9/9), in this order:
1. **(a) empty `initial('')` on STATIC VARYING char** (D4): named refusal
   `STATIC INITIAL value '' ... is unsampled` -> cell `00` + extent blanks IN PLACE, not pooled
   ([C322]; D5's FIXED half already compiles exact). Then D4 cmp-identical.
2. **(b) TITLE on STATIC varying operand, both modes** (D1/D2): [C323] class-invariant -- reuse the
   AUTOMATIC `?SLVTS` route, operand = static cell. Then E46F5 promotes: THREE-place edit
   (REJECTS remove row, NEG_META remove stamp, SPECIMENS add citing
   `golden/e42p1c/E46F5/E46F5.REL`); verify E46F5 byte-identical through the binary.
3. **(c) static FIXED char store via `?SMCCM`** (D6): head `21 *D(cell) / 11 *D(pool) /
   3E extent / 06 len / CD ?SMCCM` ([C321]); literal POOLS -- mirror the demand in the prescan
   twin (the `fa09b97` rule or the pool invariant dies).
4. **(d) store ladder \|c\| in {2,3}** (D8): `bit_cond_mat` LHLD/DCX H x\|c\| arm, <=3 threshold
   ([C324]); k=1 and negative c stay refused.
5. **(e) non-final BIT(1) PUT item** (D9): own `?PNBOP` tail, following items keep their routes,
   ONE `?QIOOP` ([C325]); PUT-EDIT and file-attach bit items stay refused.
6. **(f) member-as-RIGHT in TEST** (D10): widen `str_cmp_shape_rev` `?imem` to the TEST route
   under the single E48D10 witness ([C326]); AFTER the arm RE-MEASURE E46K14's refusal through
   the binary -- if its marker changed, fix the arm, do not silently re-pin.
Then REGISTER: SPECIMENS.update E48D1..D10 (byte tier ONLY, no RUNTIME rows) at `golden/e48p2db/`,
`--update-inventory`, census `cp spec/census/corpus-census.json /tmp/census-prev.json &&
python3 tools/corpus_census.py --check /tmp/census-prev.json` (EXPR2/FSCAN expected to ADVANCE
past the empty-initial refusal -- re-read EVERY delta), FULL GATE `python3 tools/e2e_gate.py`
(report ACTUAL; expect 1109+10+1(E46F5)=1120/0 if all arms land, negative panel 181 after E46F5
promotion), then COVERAGE.tsv rows for the new shapes + `coverage_check` + gate re-run.
**Never implement a §3 shape:** runtime length rewrite, k=1/negative c, bit-behind-file-attach,
BASED cond-store, over-extent INITIAL/store. No push. Probes <=71 cols. HANDOFF/PROGRESS/LEARNINGS
updated + finalize/renew at the end.

(Previous next-action section, superseded -- its steps 2 and 5a are DONE as measured above; its
"five REJECTS rows" figure was falsified by the audit to ONE.)

## Next action (superseded) - E2E-48/P2d step 5: claims, registration, gate, then LOWERING

**State (measured, this session):** oracle round COMPLETE and committed: `golden/e48p2db/` (10 ok/10)
at `d28ff5e`, `spec/lab-evidence/e2e48-p2d/RESULTS.md` (prediction table: HITs on P-D1..5,8,9,10;
P-D6 route-wording and P-D7 image-rewrite MISSes kept). My tree: HEAD contains infra `8b637cd`,
`142174c` (config + g21), then the round commits. ocaml/ UNCHANGED since ef0a198 — the new shapes
are still my named refusals (7 of them; D3/D5 already compile and must be cmp-verified against
their NEW goldens as step 5a).

**Steps (exact):**
1. **5a free check first:** build (`cd ocaml && eval "$(opam env)" && dune build`) and cmp my
   E48D3/D5 outputs to `golden/e48p2db/E48D{3,5}/` — they already compile; if byte-identical they
   need only registration, no lowering.
2. Record claims **C321+** in spec/CLAIMS.md from RESULTS.md §2 ONLY (each cites its golden;
   §3 stays [TBD]; §2.7 slack law may fold into an existing layout claim or a method note).
   Mark [C310]'s |c|2..3 [TBD] closed by reference (append, don't rewrite).
3. Register: add the 10 probes to SPECIMENS (byte tier only, NO RUNTIME rows), REMOVE the five
   now-falsified REJECTS rows whose refusal this round measured (static-varying TITLE D1/D2,
   empty INITIAL D4, bit-item-non-final D9, member-RIGHT TEST D10 — audit which REJECTS cite
   exactly those refusals), update NEG_META accordingly, `--update-inventory`, then census
   `--check <copy of prev>` (counts legitimately change) and the FULL GATE `python3 tools/e2e_gate.py`
   (expect 1109+new exact / 0 fail; report ACTUAL numbers). E46F5's REJECTS retirement, if it is
   one, is the THREE-place edit (REJECTS, NEG_META, SPECIMENS).
4. LOWER one arm per commit, `dune build` + cmp sweep after each, mirroring every pool-allocating
   shape in the prescan demand twin (the fa09b97 rule): (a) empty INITIAL on static char both
   classes; (b) TITLE on static varying (both modes); (c) static-fixed store `?SMCCM` head
   [LXI H,cell / LXI D,pool / MVI A,extent / MVI B,len]; (d) static-varying store `?SMCVM`
   (same for automatic varying members per D10 0006); (e) store-ladder |c|2,3 DCX arm; (f) non-final
   bit PUT item (own PNBOP tail).
5. COVERAGE.tsv rows for the new shapes when registered; re-run coverage_check + gate; update
   PROGRESS/HANDOFF; full gate must be reported MEASURED, never expected.

**Prohibitions unchanged:** no RUNTIME rows from this round; runtime length-rewrite is [TBD];
BASED-in-cond-store and bit-behind-file-attach stay refused; never touch golden/e48p2d (botched
run evidence) or earlier goldens; no %include/LOAN2 work; no push; renewal chain 0/8 this session.

> **STATUS 2026-10-30 (renewal 8/8 successor, session closing; HEAD after this commit):**
> **E2E-48/P2c IS CLOSED.** Step 6 and step 7 are DONE and MEASURED:
> - `2d26c1b` committed the guard's g19 managed-block refresh as its own commit.
> - `f67cc6d` — fixed the promotion leftover (`NEG_META` still stamped the two retired rows, which
>   aborted `registration_audit`'s REJECTS/NEG_META symmetry rule; counts 182 vs 184), ran
>   `--update-inventory` (INVENTORY **1291 rows = 1109 specimens + 182 refusals**, reviewed line by
>   line), and measured the **FULL GATE rc=0: 1109 byte-exact / 0 fail, negative 182/182,
>   divergence 9/9, coverage 102 rows 0 errors, census --verify clean (15/0/26/0)**. The inherited
>   "1107/184" is confirmed false.
> - `ef0a198` — step 7: the five drafted COVERAGE rows written against the CURRENT ledger
>   (`COND.BIT1_NEG_TEST`, `STOR.BIT1_COND_STORE`, `COND.AND_BIT1_OPERAND`, `IO.PUT_BIT1_ITEM`,
>   `DECL.STATIC_CHAR`; 107 rows / 0 errors, gate re-run still 1109/0 rc=0) plus four stale blocker
>   sentences marked SUPERSEDED by pure appends (originals kept word-for-word, verified by
>   `git diff` + `startswith`).
> - **Then two §3 "unmeasured" claims were FALSIFIED by artifacts already in the tree** (see
>   `LEARNINGS.md`): DR's object for `TITLE(<static varying>)` IS `golden/e42p1c/E46F5/E46F5.REL`
>   (CODE 68 / DATA 18, `?SLVTS`, w1 `0E50`, cell `02 41 42 20 x11` in place), and the EMPTY
>   `initial('')` static-varying cell IS `golden/first8080u/EXPR2/EXPR2.REL` DATA 000F = `00` +
>   ten `20`. E48F1/E46F5 differ in CODE only at the two `LXI H,*D` operand words.
> - **Round 4 (E48D1..D10) is PRE-REGISTERED and the oracle has NOT been run.** Committed in the
>   closing commit of this session: `spec/lab-evidence/e2e48-p2d/mkprobes.py`, the ten
>   `probes/E48Dn.PLI` (CRLF, [C193] (b)), `BASELINE-MINE.txt` (my state at `ef0a198`: 7 named
>   refusals, 3 that already compile — D3 static-FIXED title, D5 empty fixed initial, D7 store into
>   static varying) and `HYPOTHESES.md` (P-D1..P-D10, every row derived from a listed committed
>   object; P-D6/P-D7 pool arithmetic flagged as the weakest derivations).
>
> **THE EXACT NEXT ACTION** (a fresh session; **renewal is capped at 8/8, so `handoff_renew` will
> refuse — the operator starts the successor manually or raises `renewal.maxRenewals` by decision**):
>
> 1. Verify the boundary: `git rev-parse HEAD` (expect the P2d pre-registration commit or a
>    descendant), `git status --porcelain=v1` (expect clean or only guard blocks),
>    `ls probes/E48D{1..10}.PLI spec/lab-evidence/e2e48-p2d/`, and confirm the pre-registration is
>    the PREDECESSOR of any oracle call:
>    `git log --oneline --format='%h %s' -- probes/E48D1.PLI | tail -1`.
> 2. `cd /home/john/projects/sushiworks/pli80/ocaml && eval $(opam env) && dune build` (the opam
>    PATH is NOT set in a renewal successor's shell) — rc=0, binary current.
> 3. Run the oracle ONCE, exactly as pre-registered:
>    `PLI_SRC=probes python3 oracle/batch.py E48D1 E48D2 E48D3 E48D4 E48D5 E48D6 E48D7 E48D8 E48D9 E48D10 --tag e48p2d --switches '$L$D'`
>    (new tag — `golden/e48p2d` must not exist; never pass `--reuse` into an existing tag).
> 4. Write `spec/lab-evidence/e2e48-p2d/RESULTS.md`: §1 the prediction-vs-verdict table over
>    P-D1..P-D10 (keep every MISS), §2 the laws read out of the `.REL` records with
>    `tools/reldump.py` / `spec/lab-evidence/e2e42-p2b/chaindump.py` (never a `.PRN` size), §3 what
>    the round did NOT measure. Commit goldens + report together.
> 5. Only then lower what §2 measures — one arm per commit, `dune build` + `cmp` sweep after each,
>    and mirror every new pool-allocating shape in its prescan demand twin (the `fa09b97` rule).
>    E46F5's promotion, if D1/D2 land, is a THREE-place edit: `REJECTS`, `NEG_META`, `SPECIMENS`,
>    then `--update-inventory`, census `--check <copy of prev>` (counts MAY legitimately change
>    here — a corpus advance is not a regression, but re-read every delta) and the FULL GATE.
>
> **Standing prohibitions unchanged:** do NOT touch `golden/e48p1`, `golden/e48p2c`,
> `golden/e48p2retire`, `golden/e42p1c`, `golden/first8080u` or any other committed evidence; do
> NOT implement a §3 shape on faith; a BASED member in a condition store and a bit item behind a
> file attach stay refused (no witness anywhere); no `%include` work without its own
> pre-registered round; the LOAN2 `conflicting kinds` prescan gap stays `proposed` (design change,
> not an arm); no push is authorized.

(Previous next-action section, kept for lineage — its steps 6 and 7 are DONE as measured above.)

## Next action (superseded) - E2E-48/P2c step 6: census re-measure, inventory, FULL GATE

> STATUS 2026-10-30 (renewal 7/8 successor, HEAD after the RETIRE+claims commit):
> **Steps 1-5 DONE, RETIRE round DONE.** `14c7321` (4a store-destination widening, 8/9),
> `3ee414a` (4b static-varying placement + TITLE-on-static named refusal + step-2 WHY-strings,
> 9/9; E46F5 row RE-MEASURED through the binary), `630e9be` (RETIRE prereg BEFORE the oracle),
> `1480d6f` (oracle measured 2 ok/2, E46K1/E46K3 whole-file byte-identical and PROMOTED;
> SPECIMENS.update adds E48C1..C9 + K1/K3 = **1109 specimens**; REJECTS = **182 rows**;
> claims **C317-C320** + C310 annotation written). Sweeps at HEAD: E48C 9/9, e48p1 24/24,
> 181-row negative replication clean (E46F5's NEW marker verified separately against the
> binary). `dune build` rc=0 with the inherited warning multiset unchanged (126 =
> 22/15/28/2/14/2/17/26).
>
> > NOTE (7/8 successor): step-6 item 1 (census --check) is DONE (counts IDENTICAL
> 15/0/26/0, snapshot `014a736`); LOAN2 advanced to a NEW prescan my-gap
> `variable i declared with conflicting kinds` (future round, recorded not lowered).
> Items 2 (--update-inventory) and 3 (FULL GATE, expect **1109/0, negative 182/182** --
> the 1107/184 in the older text is superseded by the K1/K3 promotions) are OWED.
**THE EXACT NEXT ACTION is step 6, then step 7:**
> 1. Census: `cp spec/census/corpus-census.json /tmp/census-prev.json && python3
>    tools/corpus_census.py --check /tmp/census-prev.json` — counts MUST stay IDENTICAL
>    (EXACT 15 / DIFFERS 0 / REFUSED 26 / UNEXPECTED 0); EXPR2/FSCAN (now the EMPTY
>    `initial('')` refusal), LOAN2 (advances past line 39 to its next genuine blocker),
>    REPORT/MPMCALLB deltas are EXPECTED — read and verify EVERY msg delta in the tsv diff
>    before committing the snapshot (+ spec/COVERAGE.tsv prose defer blocker names to the
>    census; the LOAN2 sentence in row FILE.PUT_LIST_VAR now LAGS — correct or mark stale).
> 2. `python3 tools/e2e_gate.py --update-inventory` (rewrites INVENTORY rows incl. K1/K3
>    becoming byte-exact entries; 1098-entry figure was recorded at `1595a10` only).
> 3. FULL GATE: `python3 tools/e2e_gate.py` — expect **1109 byte-exact / 0 fail**, negative
>    **182/182**, divergence 9/9, coverage 102 rows 0 errors, census --verify clean, rc=0.
>    The checkpoint's "1107/184" figure is SUPERSEDED by this session's K1/K3 discovery.
>    Report measured numbers only.
> 4. Step 7 (lower priority): the five DRAFTED spec/COVERAGE.tsv rows (15 columns; validator
>    rule coverage_check:213; `manual_ref = NONE:<why>`; MEASURED rows must cite probes named
>    by their OWN claims) -> `python3 tools/coverage_check.py`.
>
> Do NOT touch golden/e48p1, golden/e48p2c or golden/e48p2retire. Do NOT implement RESULTS §3
> shapes; member-as-RIGHT in TEST and based-member condition stores stay refused. Do NOT start
> `%include` without its own pre-registered round. Renewal 8/8 would be the LAST under the cap.

(Original step list below, complete for steps 1-5; kept for lineage.)

The round-3 battery is PRE-REGISTERED (`f9f21f2`), MEASURED 9 ok/9 and committed with
`spec/lab-evidence/e2e48-p2c/RESULTS.md` (`8c57856`); the level-0 STATIC-chain my-gap fix is
committed (`6130164`) with the census re-measured (counts IDENTICAL; MPMCALLB advanced one
blocker). E48C1 is already whole-file byte-identical and 24/24 e48p1 probes are intact.
THE PREVIOUS NEXT-ACTION SECTION ("E2E-48 round 2 ... Pick ONE") IS SUPERSEDED by this one;
its item 2 (the five drafted COVERAGE rows) survives as sub-task 7 below.

Implement ONLY what RESULTS section 2 measures; every RESULTS section 3 shape stays a named refusal:

1. `bit_cond_mat` (ocaml/lib/codegen.ml:7005) - add exactly these arms, ONE AT A TIME,
   `dune build` + `cmp` sweep after EACH (LEARNINGS rule):
   (a) (internal varying MEMBER left, literal right) - both spellings, AUTOMATIC records only:
       `LXI H,*D(member) / EB / LXI H,*S(lit) / MVI A,len / CALL ?SCVCM / D6 01 / 9F` (18 bytes
       incl. the `32` STA the Vbit1 arm adds) - sites E48C2 0013, C3 0013, C4 0027, C7 0013;
   (b) (literal left, flat Vvar cell right - auto OR static): `LXI H,*D(var) / LXI D,*S(lit) /
       MVI B,len / CALL ?SCCVM / D6 01 / 9F` (17 bytes) - E48C5 0013, E48C8's SCVCM site stays
       the flat LEFT form;
   (c) (literal left, internal varying member right): same, member cell in HL, NO XCHG - E48C6.
   A BASED member as either side of a condition STORE stays refused (unmeasured).
   Mirror EVERY new pool-cell-allocating shape in `bit_store_cond_bytes` (codegen.ml:2996) -
   prescan demand is ONE rule with lowering (C152/C179; the fa09b97 lesson: an arm without a
   demand twin dies on the pool invariant).
2. Widen the internal-member gate ONLY for the admitted shapes: the store-path `imem_in_e st rhs`
   refusal at codegen.ml:8555 and the TEST-path comparison refusal at 7632 must consult the SAME
   predicates as `bit_cond_mat` (one authority, never a second copy of the byte decision); every
   other member use keeps `imem_refuse` verbatim. Update the refusal WHY-strings to cite
   golden/e48p2c where the bank now measures a shape - corrections stay traceable, never silent.
3. TEST position (E48C9): the 15-byte head `LXI H,*D(member) / EB / LXI H,*S / MVI A,len /
   CALL ?SCVCM / C2 00 00` with the no-else skip to the NEXT STATEMENT (C309 rule); member-as-
   RIGHT in TEST is UNMEASURED - keep refusing it.
4. STATIC-on-CHARACTER-VARYING placement (RESULTS section 2.5, arm at codegen.ml:12861 region,
   `Bind.RTchar (n, true)`): accept ONLY a non-empty string-literal INITIAL not longer than the
   extent; cell = [len-byte][literal padded to n with 0x20] IN PLACE in the static zone, NOT
   pooled; `initial('')` is unmeasured (EXPR2's spelling) - keep refusing it. CAUTION: E46F5's
   declaration then passes and the program advances to `OPEN ... TITLE(nm)` - TITLE on a STATIC
   varying is UNMEASURED, so E46F5 must refuse THERE; its negative-panel row pins the CURRENT
   text and must be re-measured and updated through the tool's write path with an explicit
   reason, never by hand-editing a verdict.
5. Sweep after each arm: `for n in E48C{1..9}; do ./ocaml/_build/default/bin/pli80c.exe
   probes/$n.PLI /tmp/sw/$n.REL && cmp /tmp/sw/$n.REL golden/e48p2c/$n/$n.REL; done` plus the
   24-probe e48p1 loop - expect 9/9 and 24/24 byte-identical at the end.
6. Registration: SPECIMENS.tsv byte-tier rows E48C1..C9 (NO spec/RUNTIME.txt rows - this bank
   captured .REL/.PRN only), `python3 tools/e2e_gate.py --update-inventory` (INVENTORY 1098 ->
   1107), claims C317..C320 in spec/CLAIMS.md (the six laws of RESULTS section 2) plus an
   ANNOTATION on C310 marking its load-order [TBD] answered (keep the old text), census
   re-measure via `tools/corpus_census.py --check <copy of prev>` (counts must stay IDENTICAL;
   EXPR2/FSCAN/LOAN2/REPORT/MPMCALLB msg deltas are expected to ADVANCE - verify each message),
   then `python3 tools/e2e_gate.py` -> expect **1107 byte-exact / 0 fail**, negative 184/184
   (E46F5 row re-measured per step 4), divergence 9/9.
7. Sub-task (carried over, lower priority): the five DRAFTED spec/COVERAGE.tsv rows in the
   previous checkpoint's item 2 (format facts already MEASURED there: 15 columns, validator rule
   at coverage_check:213, `manual_ref = NONE:<why>`); validate with `python3 tools/coverage_check.py`.

Do NOT touch golden/e48p1 or golden/e48p2c. Do NOT start `%include` (CREATE's front-end blocker)
without its own pre-registered round.

**Unmeasured at the `7701f52` boundary (do NOT claim them):** the full gate has not been run
since `1595a10` (1098/0 is that HEAD's recorded figure, not the current one); the census has not
been re-measured since `7701f52`; the refusal WHY-strings of step 2 are NOT yet updated.
**No half-finished edit exists** — `7701f52` is built, swept and committed; the tree is clean.

## Unfinished operations (Pi Handoff deployment)

- **None in progress.** The Pi Handoff deployment (Phases A–E) is complete, and on
  2026-10-29 the operator authorized and live-tested the renewal activation (project trust,
  compaction disabled project-wide, `renewal.enabled/autoRenew`, cap 8). The remaining
  operator decisions listed in `PROGRESS.md` → Pending (reserve tuning, closing enforcement,
  push) stay **open by design** and are not half-applied.
- No compiler work was started, continued or left half-done in this session. Nothing in
  `ocaml/`, `spec/`, `tools/`, `golden/`, `oracle/` or `probes/` was touched by it, and no gate
  was executed by it.
- No commit was made on behalf of any scientific result; the only authorized commits from this
  session are infrastructure commits over: `.gitignore`, `AGENTS.md`, `GOAL.md`, `PROTOCOL.md`,
  `HANDOFF.md`, `PROGRESS.md`, `LEARNINGS.md`, `handoff.config.json`,
  `.pi/extensions/context-guard/*.ts`, `.agents/skills/pi-handoff/**`.

## Next action (superseded — E2E-48/P1 steps 1-4)

The 2026-10-29 predecessor's six-step list (write RESULTS.md, commit evidence, fix the
bind `span` double-count, gate) was COMPLETED this session: RESULTS.md + chaindump typo
fix at 388673b (all bytes re-derived from the goldens, both MISSes kept), bind fix at
a8d1c3a with the gate still 1074/0 and E48A3/A4 byte-identical. Its step 5 (codegen
arms) and step 6 (panel/claims/census) continue in `## Next action — E2E-48/P1 step 5`
above, which supersedes it in full. (The goldens were in fact already committed at
ece657e, before this step list was written.)

## Next action (historical — deployment window)

**Not established by this session.** A deployment session deliberately did not choose the
compiler's next task, and inventing one here would put an unmeasured intention into the file a
fresh session trusts. The first action of the next session is therefore evidence-reading, not
implementation:

> Read `spec/lab-evidence/e2e42-p2c/RESULTS.md` §7 (CREATE blockers), §8 (the recorded gate
> verdict) and §9 (the unfixed `data=` reporting defect), plus
> `spec/lab-evidence/e2e42-p2c/HYPOTHESES.md`, plus claims `C296`–`C308` in `spec/CLAIMS.md`,
> then `spec/INVENTORY.txt` rows whose refusal text names `^eofile` or a `BIT(1)` condition store.
> Expected output: the candidate next phases written as *pre-registerable hypotheses* (e.g. the
> `^eofile`-in-`DO WHILE` condition form, the `BIT(1)` condition store, the `data=` reporting defect
> in `pli80c`'s summary line). Pick one, write its probe bank and predictions, commit them **before**
> any oracle run — and replace this section with the exact chosen command.

## Discoveries not yet incorporated

- **Renewal e2e test 2026-10-29 — PASSED and closed.** Durable chain, attested-handoff
  recovery, file-only successor bootstrap and auto-checkpoint preservation all verified
  (renewal 1/8, parent `01a188a5-2c00-708a-affc-0a48428f85d5` → successor
  `01a188a6-36ee-708a-affc-0a4c9333a1c9`, checkpoint `g2-470d507dbf6c`). The successor's
  start-pressure reading (~9 000 remaining) was **not** an anomaly: the test deliberately set
  `CONTEXT_GUARD_SYNTHETIC_REMAINING=9000` in the child *process* environment, and that
  synthetic override is re-read at every session_start in the process — by design, not
  measurement. The INFRA TEST WINDOW is closed: the genuine next action above was restored
  verbatim from `a6eec67`. Full record: `PROGRESS.md` → Renewal test window; lessons in
  `LEARNINGS.md`.

- `AGENTS.md`'s reading order, the guard's managed-block rules and `PROTOCOL.md` Part 2 are new to
  this repository; nothing in `spec/` has been reconciled against them, and nothing in `spec/`
  needed reconciling (the guard writes no scientific file).
- `README.md` "Current status (rolling)" is stale relative to the ledger: it still ends at
  **E2E-1 / C067** ("Next: widen codegen to RTL-call arithmetic …"), while HEAD is deep in E2E-42.
  It was deliberately **not** edited here (it is outside the authorized file list for this
  deployment) and is not to be used for status. Correcting it is an open, low-risk documentation
  task for a normal session.
- `generationReserve: 20000` in `handoff.config.json` is an **initial policy value**, not a
  verified fit for the model actually used on DRPLi. It should be checked against the real
  context window and max-output budget reported by `/guard status` before being treated as tuned.
- **Resolved 2026-10-29 (operator decision):** project trust was granted for the exact path
  `/home/john/projects/sushiworks/pli80` (plain `pi` from the project root now auto-discovers
  the extension and the skill; verified in the session started 16:58 UTC — parent cmdline is
  bare `pi`, guard loaded once). Renewal is ENABLED in `handoff.config.json`
  (`enabled/autoRenew true`, `maxRenewals 8`) and Pi auto-compaction is disabled for this
  project via `.pi/settings.json`. Controlled launches strip the inherited
  `CONTEXT_GUARD_AUTO_RENEW=1` with `env -u CONTEXT_GUARD_AUTO_RENEW` so the project config is
  authoritative (see `PROTOCOL.md` → Load).
- Managed checkpoint blocks were hand-edited **once**, deliberately, as the E2 test of the
  level-3 auto-checkpoint preservation path (a `TEST-E2-*` marker, since superseded by the final
  `/handoff` write). Outside such an explicit test, blocks are guard-written only.
<!-- guard:begin checkpoint -->
checkpoint-schema: 3
checkpoint-generation: 49
checkpoint-id: g49-ff86b8ca176c
checkpoint-kind: manual
content-delta: new
readiness: attested
status: checkpoint (guard level 1, remaining ~10749, session 01a18df8-1341-77c5-9d10-4a6bbf7e8fcd)
checkpointed: 2026-10-30T18:40:57.206Z
source-goal: 730790b648a1e1d14b76243cfe8bc17eea2ba9cd8527f204f9c8d4dbcc527c9d
source-progress: 69e6925e1796ae4dfe62fef9f8c35ab55259751dcf1a2cc08718e063f666d8c1
source-handoff: fa0f6649386472f2cc82b021bc652920ffdab9a399f4b27316a2fccd665dfac7
source-learnings: 47d589d480b842477c9aa0d6d7f938da46ba2d5f144b4dfd1d0e5e15a6832fbb
source-config: 5537d66535163979fcef1338bb101a3dab2ffd8b2eb0d467620ccc7f0c0ec616


readiness-by: session:01a18df8-1341-77c5-9d10-4a6bbf7e8fcd
readiness-at: 2026-10-30T18:40:57.212Z
readiness-checkpoint: g49-ff86b8ca176c
### Last verified state
guard level 1; checkpoint requested (finalize: E2E-48/P2e lowering: arms 1+2 DONE at HEAD bab0d16 (E48E1..E48E4 byte-identical; E46K14 marker re-measured unchanged; WHY-string cites E48E6.PRN dr-refuses). Arms 3 ('0'b value 3A/E6 80/D6 01/9F/32 in bit_cond_mat Eq fallback), 4 (FIXED-member TEST via new ?SCCCM encoder + str_side ImemF variant + prescan literal-RIGHT demand twin, TEST only, Eq only), 5 (authorize_file_item admits Vbit1; supersede note at ~10616) NOT STARTED; then step 6 claims C327+ (C332 scope VARYING member only), NEG_META E46K14 loop-removal + dedicated dr-refuses stamp, SPECIMENS.update 7 probes byte tier only, --update-inventory, census --check, coverage_check, registration_audit, FULL GATE ACTUAL (baseline 1120/0, neg 181/181), COVERAGE rows. Renewal capped 8/8 — operator must reset or start successor manually.)

### Unfinished operations
- (none recorded)

### Next action
(superseded by the section below: its steps 1-4 are DONE — run 1 botched (e48p2d, kept), wrap amendment 60a2c06, run 2 = 10 ok/10 at golden/e48p2db committed d28ff5e, RESULTS.md written)

### Guard notes
E2E-48/P2e lowering: arms 1+2 DONE at HEAD bab0d16 (E48E1..E48E4 byte-identical; E46K14 marker re-measured unchanged; WHY-string cites E48E6.PRN dr-refuses). Arms 3 ('0'b value 3A/E6 80/D6 01/9F/32 in bit_cond_mat Eq fallback), 4 (FIXED-member TEST via new ?SCCCM encoder + str_side ImemF variant + prescan literal-RIGHT demand twin, TEST only, Eq only), 5 (authorize_file_item admits Vbit1; supersede note at ~10616) NOT STARTED; then step 6 claims C327+ (C332 scope VARYING member only), NEG_META E46K14 loop-removal + dedicated dr-refuses stamp, SPECIMENS.update 7 probes byte tier only, --update-inventory, census --check, coverage_check, registration_audit, FULL GATE ACTUAL (baseline 1120/0, neg 181/181), COVERAGE rows. Renewal capped 8/8 — operator must reset or start successor manually.
<!-- guard:end checkpoint -->
