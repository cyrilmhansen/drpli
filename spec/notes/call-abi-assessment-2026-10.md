# E2E-5c provisional assessment — CALL/RETURN architecture (2026-10-17)

STATUS: analysis only; NO implementation started. Evidence: probes
P401 (non-recursive call), P402 (bounded recursion) compiled by DR
with $L$D$C (golden/e2e5c, BOTH .REL banked), plus the corpus
RFACT.REL/.COM (DR's own link, observed under oracle), plus a
corpus-wide .REL inventory (SVBLK/RSBLK/CHAIN-ADDR counts).

## EXPERIMENTALLY CONFIRMED (bytes on DR output, cross-checked >=2 sources)

1. Call-by-ADDRESS with link-time pointer cells.
   Constant argument [P401]: value stored as a 2-byte little-endian
   POOL entry; a DATA 'argptr slot' is initialized to the pool cell's
   address via a deferred record pair emitted BEFORE code resumes:
   SET-LC(Data,slot); inline RELOC(Data,pool-addr); SET-LC(Code,pos)
   -- LINK fills the slot with the runtime address at link time.
   Variable argument [RFACT]: same slot mechanism, pointer targets
   the variable's DATA cell (no runtime store at the call site).
   Call site: LXI H,*A(slot); CALL <entry>. Entry operand: forward
   call -> CHAIN-ADDR record; backward/recursive -> INLINE RELOC
   (Code,entry-addr) [P402 @0x57].

2. Callee parameter handling [P401 $C+bytes]:
   prologue: MOV E,M; INX H; MOV D,M; XCHG; SHLD formal-cell
   (formal stores the ADDRESS). Reads: LHLD formal -> HL=ptr;
   MOV E,M;INX H;MOV D,M;XCHG -> HL=value. [P402: recursive prologue
   PREFIXES this with LXI B,<size>; LXI D,<dst>; CALL ?SVBLK and
   ALSO writes a SHADOW value copy (LHLD formal; deref; SHLD shadow
   cell); body arithmetic reads the SHADOW directly via memory-operand
   ladders (XRA A; CMP M; INX H; SBB M; JP/F2 -- skip byte F2 again,
   $C prints 'JP' [C072 family]).]

3. Return [P401/P402]: result in HL (caller: SHLD var directly after
   CALL). Non-recursive: plain RET, no RTL. Recursive: every exit
   path 'CALL ?RSBLK; RET' (P402: 2 returns = 2 RSBLK; matches
   RFACT.REL RSBLK=2/SVBLK=1 inventory across ACK/ACKTST/EXPR*/
   DFACT/FFACT). Conditional-return body uses the standard
   skip-ladder + deferred triple [==== JP -> after-return].

4. 'stop;' = CALL ?STOPX (identical to epilogue call) [P401].

5. Expression argument [P402]: value computed into a caller-side
   DATA temp slot (LHLD;DCX H;SHLD *A(tmp)); call site passes
   LXI H,*A(ptrcell) where ptrcell != tmp on the trace (@A vs @C)
   -- CONFIRMED as bytes to replicate; the SVBLK-saved region is
   believed to reconcile them per activation (HYPOTHESIS).

## HYPOTHESES (state explicitly unproven)
- SVBLK/RSBLK semantics (save/restore of 8-byte block incl. formal
  + shadow + argcells on the HW stack; BC=size, DE=dst). Byte
  replication does NOT require understanding them (RTL comes from
  PLILIB unchanged -- same runtime ABI argument as E2E-1).
- Depth behavior: static slots + per-activation save/restore must
  make recursion safe; unproven beyond 2 levels (P402 recursed 4x
  at compile-evidence level ONLY -- never executed my link).
- RET condition byte (C9 vs quirk) -- reldump it during 5c.

## OBSERVATION (must resolve before 'verified factorial results')
DR's OWN linked RFACT.COM (from the corpus golden .REL, executed on
the oracle) printed only '0' in a 60s window then was killed by
timeout [golden e5clink/e5crun2 transcripts banked note]. RFACT's
loop is genuinely infinite (`stop;` unreachable after `DO ... END;`
with repeat(i+1)); output is line-buffered-ish. Acceptance design
must therefore be: .REL byte-exact + .COM byte-exact vs DR link +
RUNTIME transcript PREFIX comparison (deterministic leading
factorial lines) under a fixed timeout -- full-output equality is
impossible for a forever program. Investigate whether the '0' is
capture truncation-on-kill (likely: pty buffers lost on timeout) or
real runtime behavior; a bounded variant probe (factorial loop with
finite exit) can discriminate cheaply.

## PROPOSED 5c SCOPE (bounded; per slice discipline)
Implement ONLY what RFACT needs, byte-gated by P401/P402/RFACT:
- matcher: call-expression items in PUT lists + call in assignment
  (RFACT's `factorial(i)` inside multi-item put [N301 chain ✓ reused])
- constant-arg pool cell (16-bit LE) + link-time ptr-slot triple
- variable-arg ptr-slot (no temp) [RFACT]
- forward CALL via CHAIN-ADDR, backward/recursive inline RELOC
- nested-proc lowering: prologue (SVBLK prefix iff RECURSIVE),
  formal cells, shadow copy, deref ladders (memory-operand forms
  incl. CMP-M/SBB-M ladder + F2/F4 skip bytes -- reldump first)
- RETURN statement (plain / RSBLK+RET / conditional-position skip
  triple reuse) and `stop;`
- binder: recursive flag + returns-type plumbing (entry descriptors
  EXIST in binder $S but prove NOTHING about this ABI -- runtime
  evidence above is the authority; binder data only supplies
  offsets/sizes)
Explicitly NOT in 5c: multi-arg (ACK 2-arg = next slice), args by
value-expression into pointer cells beyond P402 shape, external/
ENTRY procedures, DO-with-call combinations beyond proven probes.
Acceptance: P401/P402 byte+COM+console; then RFACT.REL byte-exact +
COM identical + bounded-transcript-prefix runtime. RFACT must run
under a timeout (forever program) -- gate needs a bounded-run mode
(small harness addition: expected rc=timeout + prefix compare).
Effort estimate: ~400-600 LoC codegen + one small harness change;
risk MEDIUM (mechanisms all evidenced; unknowns are nested-context
interactions, all fail-loud protected).

## Panel accounting (user question, re-stated)
20->19 was N8_CONDFORM promoted to SUPPORTED coverage (if a<3 now
compiles byte-exact via Z405-equivalent ladder). N20_DOWILE was
RETAINED, re-scoped to i<30 (outside the proven DCX-k<=8 band), so
the fail-loud boundary keeps its negative test; net 19 with zero
dropped invariants. 5b then promoted N5->G117, N10->G118 (fresh DR
goldens, byte+console exact) and added N22-N24: panel now 20/20.
