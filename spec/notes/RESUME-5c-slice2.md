# RESUME PROMPT — E2E-5c slice 2 (recursion + RFACT), session of 2026-10-18

## Mission (unchanged)
Reverse-engineer DR PL/I-80 v1.4 (CP/M-80) and reimplement in OCaml
(`~/projects/sushiworks/pli80/ocaml`, hand-written recursive-descent parser).
Scientific method: black-box oracle probes (`oracle/batch.py` + cpmsim -8),
white-box disassembly, falsifiable claims with evidence tags, byte-identical
`.REL` as the hard gate, fail-loud `[TBD]` for anything unproven. Report to
user at every ~2000 added lines and PAUSE.

## Repo / tooling facts
- Build: `cd ocaml && dune build` → `_build/default/bin/{pli80c,pli80parse,pli80tree,pli80bind}.exe`
- Gates: `python3 tools/e2e_gate.py` (+`--link-run`), `tools/parse_gate.py`,
  `tools/bind_gate.py`, `tools/rel_roundtrip.py`, `tools/ir_gate.py`,
  `oracle/test_safety.py`
- Oracle probe run (works from any dir — PLI_SRC must contain NAME.PLI):
  `cd build/e5c2 && PLI_SRC=$PWD timeout 400 python3 ../../oracle/batch.py NAME --tag e2e5c --reuse --switches '$L$D$C$S'`
  (goldens land in `golden/e2e5c/NAME/`; `--reuse` needed since tag dir exists)
- **Probe files MUST end `...\r\n\x1a` (CRLF before EOF byte) — a missing
  final CRLF gives DR "UNEXPECTED EOF / SYNTAX ?" and an incomplete run.**
- Verify bytes with `cmp`/`sha256sum` on the RAW .REL. `tools/reldump.py`
  masks some address fields; `diff <(reldump A|awk) <(reldump B|awk)` is fine
  for locating deltas but never as the acceptance verdict.
- HEAD right now: `d6365fc` = WIP snapshot of this session (compiles clean;
  some new R4xx probes DIFF inside it — that is expected, the guard rule is
  mid-refinement). Slice-1 clean commit: `1726c25`.
- `st.tail_addr` is set at proc entry (line ~1345 codegen) but the guard is
  emitted INSIDE the proc-prologue lowering path (`Sprocedure` arm calls the
  same lowering that contains the guard block).

## What slice 2 has ACHIEVED (verified this session)
- **Recursive internal procedures fully working**: SVBLK prologue
  (`LXI B,secsize; LXI D,blockbase(+reloc); CALL ?SVBLK`), ptr deref,
  SHADOW value cell, RSBLK before every RET, expression call args
  (slot+temp), call-expression as PUT LIST item, mul-right-first when RHS
  is a call (`PUSH H / LHLD / POP D / ?IM22N`), backward/self inline RELOC
  call operand vs forward DATA+CHAIN-ADDR.
- **NFACT byte-exact** (finite twin: `do i=0 to 7; put skip
  list('f(',i,')=',factorial(i)); ...` factorial via recursion) —
  golden `golden/e2e5c/NFACT/NFACT.REL` (512 B, CODE=00A8, sha 037fc6ede2).
- **RFACT reached byte-exact** vs corpus golden
  `golden/first8080u/RFACT/RFACT.REL` (512 B, CODE=0099, DATA=0018,
  sha 130ce85e01) at the stop-arm stage (before guard work started).
- **P401 still byte-exact** (slice-1 regression holds).
- RECURSIVE attribute confirmed as the trigger for shadow+SVBLK (R411
  $S: `F FUNCTION PARAMETERS(1) RECURSIVE` with NO self-call yet full
  SVBLK/shadow machinery) — bind.ml now ORs attribute with call-derivation.
- 16+ probes byte-exact at their best point: R401 R403 R407 R408 R410 R411
  R412 R414 R415 R416 R417 R418 R419 R421 R422 R424 R426 R427 R428 NFACT
  P401 P402(?) RFACT — all before the guard patch series (see below).
- Full legacy gates were green at the pre-guard point (e2e 51/51, parse
  380/6/0, bind 47/47, rel 349/349, safety 28/28, NEG 20/20).

## The open problem: the TAIL GUARD rule
When a procedure is appended into the epilogue region, DR sometimes emits
at the append address, BEFORE the proc prologue:

    c3 00 00  + forward triple (target = the epilogue ?STOPX operand slot)
    i.e. `JMP <epilogue>` with LINK-CHAIN-ADDR on the operand; the epilogue
    `CALL ?STOPX` is then KEPT.

**Complete specimen table (37 probes, DR goldens):**

| probe | main tail | explicit stop printed before procs? | DR guard? | epilogue? |
|---|---|---|---|---|
| R429 | `do i=1 to 3` (TO) | no | **1** | kept |
| R404 | TO loop | no | **1** | kept |
| R405 | TO loop | no | **1** | kept |
| R432 | straight-line `x=5` | no | **1** | kept |
| R406 | straight-line call `x=f(3)` | no | **1** | kept |
| R423 | forever `repeat` + stop + ANCHOR `t: put list('K')` (window closed by anchor) | stop printed NOTHING (suppressed) | **1** | kept |
| R430/R433/R417 | any | stop emitted in place (window closed) | 0 | stop |
| RFACT/R414/R421/R425/R426/R427 | forever loop last-ish, stop suppressed | yes(suppressed) | 0 | dropped |
| R410/R411/R418/R431/P402/NFACT | forever loop, NO stop in source at all | no | 0 | dropped |
| R408 | `do while('1'B)` (=forever), stop suppressed | yes(suppressed) | 0 | dropped |
| P401 | straight-line, stop emitted | yes | 0 | stop |

**Current working rule (consistent with ALL 37):**
`guard fires iff (window open at first appended proc entry) AND
(no explicit stop printed by main) AND (main tail loop CAN exit: has TO,
or WHILE that is not '1'B) — plus the R423 anchor case: window closed
by anchor AFTER a suppressed stop, epilogue kept ⇒ guard`.
Operationalization in progress:
- `bind.ml` `prog_layout.pl_tail_exit` = last executable main stmt
  (dcls/nulls filtered, List.rev) is `Sdoto` with `to_<Some || (while_<Some
  && not WHILE('1'B))` or non-loop ⇒ true. (Implemented ✓)
- codegen `st.tail_exit` field init'd from layout ✓; guard block gated on
  `st.after_forever && not st.stop_seen && st.tail_exit` ✓;
  stop-arm: `at_tail = st.after_forever || st.guard_open` (R423 style:
  stop at guarded address prints nothing but sets `st.tail_stop_dead`);
  epilogue gate: `tail_displaced = st.after_forever && not st.tail_stop_dead`
  (guarded tails KEEP the epilogue).

**The last observed bug (at session end):** guard fired inside RFACT's
recursive body (@70) — ROOT CAUSE FOUND: an older iteration left a nested
`if st.tail_exit then begin` inside the guard block (lines ~1346–1364 of
codegen.ml) whose inner `begin`/`end` balance was broken by a botched
python replace — the OUTER gate had `&& st.tail_exit` appended but the
INNER duplicate `if st.tail_exit then begin ... end` swallowed the
`st.after_forever` semantics? — actually the double gate is redundant,
harmless logically, BUT the matrix run still showed RFACT DIFF at octet
326 = guard@70 inside proc body ⇒ the guard condition was TRUE while
lowering a proc BODY statement: check whether `Sprocedure` inner/nested
procs or body statements re-enter the prologue path with
`st.in_proc=false` (e.g. save/restore of in_proc around body lowering at
line ~1327 `savedp` is restored only at the END — verify body lowering
actually SETS in_proc before recursing; the prologue-vs-body split).
RFACT: tail is forever (repeat) so tail_exit=false — if RFACT still
guarded, the guard that fired came via a path where tail_exit was true:
the factorial body contains its OWN forever?? No — most likely the inner
`if st.tail_exit` block executes with the OUTER gate already passed for
NFACT-shapes, and RFACT's outer gate evaluated tail_exit=true because
`st.tail_exit` was initialized from a DIFFERENT layout (pool walk) or
`bind` sees RFACT main tail stmt as `Sstop` (filter keeps stop; stop is
last?! RFACT source: `...end; stop; ...` INSIDE?? check: RFACT's last
main stmt before proc = forever loop or stop?? If stop is filtered as
non-loop ⇒ tail_exit=true ⇒ guard). **RFACT main block is: dcl×2,
DO-forever, stop (suppressed) then `end pr?` — the filter keeps `stop`??
NO — filter keeps Sstop! List.rev first = Sstop → `_ -> true` →
tail_exit=TRUE → guard fired.** THAT IS THE BUG: the tail_exit
computation must IGNORE `stop` statements (they are suppressed at open
windows / close windows otherwise), i.e. also filter `Ast.Sstop _` out
of the list (or classify stop as tail_exit=false when at an open
window). Fix candidates: filter Sstop in bind's tail_exit list; then
RFACT/R414/R421/R425/... (forever + stop) fall out as tail_exit=false ✓
matching DR (no guard) ✓; R423 (forever + stop + ANCHOR) — after
filtering, last exec = forever loop ⇒ tail_exit=false ⇒ NO guard ✗✗
but DR GUARDS R423!! ⇒ R423 needs the guard via the ANCHOR semantics:
guard iff window open OR (guard_open path) ... R423's window was CLOSED
by the anchor — after the close the proc prologue sees
after_forever=false ⇒ no guard ⇒ wrong. **Refinement: track window
suppression separately: `st.stop_suppressed_dead` (set when a stop
printed nothing); if a stop was suppressed and later procs append after
an anchor, DR guards + keeps epilogue.** So implement: guard fires iff
`(after_forever && not stop_seen && tail_exit)` [R429/R404/R405/R432/
R406: closed?? those have NO stop, window open, TO/straight tail]
OR `tail_stop_dead` [R423: stop suppressed, anchor closed window] — and
forever-window-no-guard via tail_exit=false [RFACT/R410/R411/R431/
R408/R421/R425/R426/R427]. Recheck every row of the table against this
formula before coding.

## Concrete TODO list (ordered)
1. Fix the botched nested guard block (codegen.ml ~1344–1365): one clean
   condition, no duplicated inner `if st.tail_exit`.
2. Fix `pl_tail_exit` in bind.ml: filter out `Ast.Sstop _` (and maybe
   Sproc/Sprocedure) from the "last executable stmt" scan — RFACT bug
   above. Decide R423 handling (tail_stop_dead ⇒ guard OR term) — verify
   against the 37-row table; the table is the spec.
3. Re-run full probe matrix: R401-R433, NFACT, P401-P404, RFACT, Z4xx,
   G/N3xx legacy → target: everything EXACT that was exact pre-guard +
   R404/R405/R406/R423/R429/R432 (guard cases) newly exact. R430/R433/
   R417/R412/R418/R428/R403/R409/R416/R421/R422/R424/R426/R427/R425/
   R414/R410/R411/R408/R407/RFACT/NFACT/P401 must stay exact.
4. Register in `tools/e2e_gate.py`: already added RFACT + NFACT R4xx +
   P404 (remove/keep per outcome); console arms list already extended
   with RFACT NFACT R401 R412 R419 — NFACT must produce the factorial
   console values; REMOVE RFACT/R401/R412/R419 from console arms if
   forever/nonterminating (RFACT/R401 are forever-programs — console
   verification there must use a bounded transcript-PREFIX protocol,
   NOT timeout truncation as semantic oracle; NFACT is finite and is
   the runtime oracle: expect 'f(0)=1'..'f(7)=5040'; P402/R411 no-put
   programs produce nothing).
5. `python3 tools/e2e_gate.py --link-run` (oracle link + console): NFACT
   byte-identical .COM + console values vs math; P401 re-verify; RFACT
   prefix-record protocol (stop after N complete records) per user rule.
6. Run ALL gates (e2e/parse/bind/rel/ir/safety/NEG). Expect parse gate
   to pick up R429-R433 automatically (add to its corpus if needed).
7. `git commit` a clean slice-2 milestone. Then (same slice, small):
   finite-twin runtime verification per user directive.
8. Update `spec/CLAIMS.md` (C081/C082): recursion ABI confirmed;
   guard rule CONFIRMED only for rows reproduced; R423 anchor-guard =
   separate claim; P403 double-forward CHAIN stays deferred (ACK slice).
9. Keep OUT of slice: CALL statement (`call f;` → [TBD] ✓), multi-arg,
   external ENTRY, POINTER/BASED formals (raise ✓ in place).

## Pitfalls hit this session (do not repeat)
- OCaml: `let x = e` immediately before `if ...` needs `in` (two syntax
  errors from that). Python patchers: assert-and-apply ALL edits in one
  script run; a failing later edit discards earlier ones ONLY if you
  write at the end — write-once-at-end is the safe pattern; NEVER trust
  a 'printed ok' from a script that asserted mid-way (first write wins).
- `sub1` with trailing-newline patterns fails when source lines carry
  trailing content (`and savedr = st.in_rec in` on next line).
- batch.py has NO `--out` flag; goldens are fixed at `golden/<tag>/`;
  missing PLI_SRC ⇒ misleading 'import source not a regular file'.
- Old/mislabelled goldens exist (R411 early run was compiled from a
  source WITHOUT `recursive` — regenerate after every probe edit;
  verify probe text vs PRN source lines before trusting a golden).
- `grep -c` prints 0 AND exits 1 → `$(... || echo ?)` fallbacks can
  corrupt shell loops (`?` string comparisons). The 'guards=1' readings
  for R421/422/424 were an artifact of counting `JMP 0000` from a DIFFERENT
  listing region (forward GOTO chains in other probes) — always recheck
  guard claims against the SPECIFIC PRN bytes at the proc-entry address.
- A `cmp` verdict can be masked by loop ordering / /tmp file reuse: use
  per-probe temp filenames when in doubt.

## Key byte facts (RFACT/NFACT/P402 goldens, decoded)
- RFACT frame: ptr, shadow, arg-temp, loop cell — SVBLK `LXI B,8; LXI D,10`;
  deref prologue `MOV E,M; INX H; MOV D,M; XCHG; SHLD shadow`; body reads
  shadow via `LHLD addr` + ladder; every exit `CALL ?RSBLK; RET`;
  self-call operand = inline RELOC(code,entry); forward call = DATA zeros +
  CHAIN-ADDR; PUT item call = Esuffix→PInum chain pair+LXID+CALL;
  `i*factorial(i-1)` right-first: arg→SHLD→LXI H?→CALL→PUSH H→LHLD→POP D→?IM22N.
- Epilogue ?STOPX operand slot is CHAIN-EXT at the tail; guard JMP targets
  exactly that slot (final code size) via CHAIN-ADDR.
- WHILE('1'B) forever: increment-free window, edge=head+4; DO..REPEAT(k):
  increment LHLD(+INX H×k)+SHLD, edge after it; k=2 proven (R427).

## Checkpoint accounting
~3000 lines added since `4eea432` (user checkpoint 2000 was honored at
`1726c25`; slice-2 GO was given after that report). This WIP snapshot
`d6365fc` is NOT the milestone commit — finish TODO 1–8 then commit; if
the session ends before TODO 8, commit the best-green state with an
honest message and leave the DIFFing probes unregistered (fail-loud only
in the panel, never silently).
