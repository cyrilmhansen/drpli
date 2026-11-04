# E2E-52/P1 — PLAN (scope-aware DEC pool prescan; LOAN2 blocker; OPERATOR-AUTHORIZED 2026-11-04)

Objective: determine how DR PL/I-80 v1.4 types and pools DEC literal cells when the
**same name is declared in nested scopes with different kinds** (the LOAN2 blocker class),
then make my prescan type map **scope-aware** — mirroring the lexical accumulation the
lowering already performs — reproduce the accepted forms **byte-exactly**, and unblock
`artefacts/LOAN2.PLI` as far as the evidence supports. Stop after P1.

Motivating gap (measured at hop 1, baseline `e15e325`):
`artefacts/LOAN2.PLI` refuses with rc=2
`codegen: variable i declared with conflicting kinds; decimal pool prescan needs one
unambiguous type map [TBD]`, while DR ACCEPTS the same source:
`golden/first/LOAN2/LOAN2.REL` (7680 B, sha `712cfcb2…`, DATA 0x035A, CODE 0x09A0).
LOAN2 shadowing: main `i fixed decimal(4,2)`; `current_year: procedure(I)` with
`I fixed decimal(10,2)`; `line: procedure` with `i fixed bin`.

Predecessor boundary: E2E-51/P2 CLOSED at HEAD `99845ae` (docs-only close over baseline
`e15e325`; `ocaml/` identical between them); ledger ends **C355**; gate baseline
1186/0, 181/181, 9/9, 136 rows, census 15/0/26/0, prose 5.

Existing witnesses REUSED as controls (never re-derived):
- **[C187]**: nested-procedure layout law; a same-named local is a **distinct cell**
  (N6: outer A(000C), inner A(000E)) — DR accepts cross-scope homonyms; a global
  ambiguity model is already falsified by the LOAN2 golden itself.
- **[C178]/E2E-24**: DEC-literal pool cells dedup on the **encoder byte image**
  (LQ6, LQA goldens); cell bytes = ceil((p+1)/2) [R507, LOAN1].
- **[C131]**: DEC formal writes take the `?DSTOP` route (LOAN1 byte-exact on the panel).
- **[C193]/[C118]** probe hygiene (CRLF+^Z, ≤71 cols, key-collision check BEFORE write —
  keys E52A..J measured collision-free against `spec/INVENTORY.txt` and `probes/`).
- Survey (hop 1, script): **NO existing probe or golden has cross-scope homonyms** —
  this bank opens that ground; the label-shadowing precedent [C228] is NOT a variable law.

Architecture (read off source at hop 1, accepted): the **lowering is already lexical** —
`lower_proc` (codegen.ml:11964) sets `st.vars <- Vinfo.attach proc_rows (mapped pl_rows)
@ saved` (inner-first assoc = shadow). The outlier is the **prescan**: `pd_vars`
(codegen.ml:13438) is ONE global name->vkind map built from ALL procs' `pl_rows` (via
`rt_to_vk`) @ top rows, refusing any kind clash; ~15 consumers do
`List.assoc_opt name cx.pd_vars` (1865, 1905, 2914, 2933, 2965-2974, 3112-3121, 3162,
3179, 3198); the `Sproc` prescan arm (3300) swaps only `pd_ret`/`pd_fl_ret` and recurses
with UNCHANGED `pd_vars`. `bind.ml`'s `outer_rows` param (:614) is DEAD.

## The bank — 10 probes `probes/E52*.PLI` (one controlled difference each)

A same-type homonym control + cross-scope image dedup; B different-precision homonym
(LOAN2 class, DATA discriminator); C DEC outer / bin inner (CODE discriminator);
D bin outer / DEC inner (DATA discriminator); E non-shadowed outer write from inner
(accumulation test); F different names same image across scopes (dedup breadth,
name-independent); G formal shadow = LOAN2 current_year shape; H three scopes, inner
write resolves through MID (CODE/reloc discriminator); I three scopes, inner TEST
through MID (prescan_cond consumer, DATA discriminator); J no-shadow regression
control tied to today's rc=0 object. Full row text and per-row hypotheses in
HYPOTHESES.md; `mkprobes.py` regenerates the files; `BASELINE-MINE.txt` records the
measured behavior of the current compiler (4 accepted, 6 refused by name).

## Procedure (strict order, house method)

1. Pre-register: `mkprobes.py` + generated probes + `HYPOTHESES.md` + `PLAN.md` +
   `BASELINE-MINE.txt` COMMITTED BEFORE any DR call. Prediction SHA proven by
   `git log --format=%h -- probes/E52A.PLI`.
2. Oracle: ONE grouped campaign
   `cd /home/john/projects/sushiworks/pli80 && PLI_SRC=probes timeout 900 python3 oracle/batch.py E52A E52B E52C E52D E52E E52F E52G E52H E52I E52J --tag e52p1 --switches '$L$D'`.
   `golden/e52p1` must NOT exist before the call (verified absent); never `--reuse`;
   a timeout is preserved and classified, never retried indefinitely.
3. Inspect every `.PRN` (diagnostics) and complete `.REL` (`tools/reldump.py`;
   whole-file cmp per PROTOCOL #6). Classify each row `dr-refuses` / `my-gap` /
   `unmeasured`. RESULTS.md keeps every MISS verbatim (PROTOCOL #2). Commit goldens +
   RESULTS together BEFORE any compiler change.
4. Implementation ONLY after evidence, as ONE small structured change: `pd_vars` starts
   as the TOP rows only; carry a per-proc own-rows table (name -> rows via the SAME
   `rt_to_vk`); the `Sproc` arm recurses with `{ cx with pd_vars = own @ cx.pd_vars }` —
   `List.assoc_opt` first-match then gives the SAME lexical shadowing as lowering.
   Keep dedup refs (`pd_img`, `pd_str`, `pd_fl`), `pd_procs`, `pd_fl_procs`,
   `const_cells` and the pool base INTACT. Do NOT resurrect `bind`'s dead `outer_rows`.
   Invariants: the single-scope path stays byte-identical; pool demand == lowering
   allocation ([C179]); DATA offsets/relocs byte-exact; unsupported constructs still
   refused BY NAME.
5. Verify: new accepted E52 specimens whole-file byte-exact vs `golden/e52p1`;
   regression sweep over `probes/E51*.PLI` (12) + the panel; rerun original
   `artefacts/LOAN2.PLI` UNMODIFIED — record the exact next blocker if it advances,
   do NOT fix it; FULL compile-tier gate `timeout 3600 python3 tools/e2e_gate.py`
   rc=0 expected with baseline ACTUALS (1186/0, 181/181, 9/9, 136 rows, census
   15/0/26/0, prose 5) BEFORE registration; then register genuinely verified
   specimens/claims from **C356** per PROTOCOL (claims derived ONLY from RESULTS §2),
   sanctioned `python3 tools/e2e_gate.py --update-inventory`, gate AGAIN post-update,
   census re-snapshot via the tools own write path, COVERAGE rows AFTER the inventory
   update, run ALL harness self-tests at this registration hop (standing proposal).
6. Close prose + `/handoff` + attest; **STOP after E2E-52/P1** — no P2, no expansion to
   other LOAN2 blockers, no push; operator `handoff.config.json` never staged.
