
| C079 | E2E-5b numeric + mixed console output banked (N301-N308,G117/G118 golden/e2e5b; ALL .REL byte-identical, .COM identical, console byte-equal incl. formats '        0        -7 A=         0 , B=        -7\r', '   -2 V    -2 \r', width ladder '    1     0 ...'). PUT LIST lowering = SYSPR preamble + optional skip (BARE skip == skip(1) [N302 MVI A,01]); per item: literal = LXI H,*S;MVI A,len;SLCTS;PNCOP | numeric(var/expr) = <HL>;MVI A,width;QICOP;PNVOP | single char/varying var = V101/V106 chain; then ONE QIOOP + cont triple. Numeric PRINT WIDTH = field width incl sign: w(p)=min(9, digits(2^p-1)+4) matching ALL probed p=1..15 + default15 + (16,24 -> 9 but NOT-IMP); banded, NOT linear. 1-byte FIXED BIN (p<=7 per binder sizing): LOAD = LDA abs (3A+inline reloc) then sign-extend MOV L,A;ADD A;SBB **H**(0x9f);MOV H,A [ladder pre-existing]; STORE = value in A then opcode **0x32** + inline-reloc address ($C prints 'STA' -- replicated literally, same byte-vs-mnemonic family as CA/F2 [C072]; semantics never modeled); expression store = MOV A,L (7D, not 6A!). MUL with 1-byte RHS interleaves: LHLD l; raw LDA r; PUSH H; sign-extend; POP D; ?IM22N [N303] (vs PUSH-first for 2-byte, unchanged). Const-minus-const = DEC pool chain (DLDOP per operand [digits-bytes], DSUOP, QDI15) [N301/N306]; prescan now counts those pool bytes. -x = <HL>;?IN20N; (a+1) paren items arrive Econd-wrapped -> unwrap in classify; a+1 = INX H rung [N304]. **FIXED BIN > 15: DR pass-1 'NOT IMP', no .REL (N24/N305/N307) -- codegen mirrors the rejection (perimeter boundary, not our gap)**. Constant-only numeric items, char-var-in-multi-item lists, concat-in-multi = [TBD] (N15/N22/N23). G117/G118 = former negatives N5/N10 promoted with fresh DR goldens | **confirmed** (byte+runtime) | e2e_gate 50/50, 40 console arms, NEG 20/20 |

## C080 — Non-recursive internal CALL/RETURN ABI (E2E-5c slice 1)
STATUS: CONFIRMED & IMPLEMENTED (P401 byte-identical .REL + identical
.COM + console-equal runtime '        4\r'; gate 51/51, 41 arms, NEG
20/20). Layout independently corroborated by TWO further DR DATA AREA
values (P402=0x0E, RFACT=0x18) that the DFS cell/shadow model
reproduces exactly before any recursion code exists.
Mechanism (all from DR bytes: golden/e2e5c/{P401,P402,P403,RFACT}
$L$D$C$S; fresh compile of artefacts/RFACT.PLI reproduces the corpus
RFACT.REL bit-for-bit — source identity + determinism):
- Call-by-address with link-time pointer cells. Per call site: one 2B
  DATA PARAM cell placed AFTER the caller block's named autos (DFS
  section order: caller named, caller cells, callee blocks). Constant
  argument: 16-bit little-endian pool cell (counted in pool prescan,
  allocated in flow order [P401 '2'@data 0]). Pointer cell filled by
  the deferred triple SET-LC(Data,slot) ; RELOC(Data,target) ;
  SET-LC(Code,resume-LC) emitted IMMEDIATELY BEFORE the call-site
  code; call-site = LXI H,*A(slot) ; CALL entry. Forward entry (proc
  not yet lowered; main-first layout) → LINK-CHAIN-ADDR record at the
  callee's FIRST byte [P401 @1285, mirrors forward-GOTO G115]; known
  entry (backward/self [P402]) → inline RELOC(Code,entry) in the CALL
  operand. Result returns in HL; caller stores directly (SHLD).
- Callee entry = label at head of the procedure block (blabel).
  Prologue (non-recursive, 1 formal): MOV E,M ; INX H ; MOV D,M ;
  XCHG ; SHLD <formal ptr cell> — formal holds the ADDRESS. Formal
  reads = LHLD(cell) + deref ladder (5E 23 56 EB → HL=value).
  Formal's `dcl` cell DEDUPS onto the ptr cell when NON-recursive
  [P401 dbl DATA=8: pool2+x2+cell2+formal2] and is a separate value
  'shadow' cell right after the ptrs when RECURSIVE [P402: n@6 ptr,
  n@8 shadow; RFACT: i@10 ptr, i@12 shadow — both match the model's
  DATA totals]. Nested-proc RETURNED cells occupy NO storage.
- ADD with a pointer-formal operand switches ladder form:
  left ; PUSH H(E5) ; right ; POP D(D1) ; DAD D(19) [P401 @37/@3F].
  Mechanically forced: the deref ladder's own XCHG clobbers DE, so
  the plain XCHG-preserve [P071A] cannot carry the left value across
  a second deref. Plain operands keep the XCHG form.
- `stop;` = CALL ?STOPX AT ITS SOURCE POSITION and SUPPRESSES the
  epilogue ?STOPX call [P401: one STOPX @26, code ends at dbl's RET,
  CODE SIZE 0x42]. Programs without explicit stop keep the epilogue
  (42 prior goldens re-verified unchanged).
Scope limits (fail-loud [TBD]): recursive procedures, multi-arg/
multi-formal, expression call arguments, CALL statements, pointer-
formal stores/GETs/DO-controls, 1-byte formals, forward-CALL chains
with >=2 refs [P403 mechanism banked but unimplemented], returns
precision other than default FIXED width.

## C081 — Recursive internal procedure ABI (E2E-5c slice 2)
STATUS: CONFIRMED & IMPLEMENTED for the experimentally verified scope
(single FIXED formal, expression args, self/backward/forward calls).
Evidence: RFACT .REL byte-identical vs the historic corpus golden
(sha 130ce85e01, CODE=0099 DATA=0018) AND its linked .COM byte-identical
vs DR's (7552 B); NFACT byte-identical .REL + .COM + RAW console
equality, and the console values are independently correct
f(0)=1,f(1)=1,f(2)=2,f(3)=6,f(4)=24,f(5)=120,f(6)=720,f(7)=5040;
R405/R406/R407/R408/R411/R417/R421/R423/R429 .REL byte-identical.
Mechanism (DR bytes):
- RECURSIVE attribute (or a self-call) => activation save: prologue
  `LXI B,<section size>; LXI D,<block base + reloc(data)>; CALL ?SVBLK`
  [RFACT @56: LXI B,8; LXI D,10], then the formal-pointer deref ladder
  `MOV E,M; INX H; MOV D,M; XCHG; SHLD <ptr cell>` followed by a SECOND
  deref that stores the VALUE into the dedicated SHADOW cell
  (`SHLD shadow`) [RFACT @5F-6D; P402 same shape].
- Recursive bodies read the shadow cell with plain ladders (LHLD), NOT
  the deref ladder [RFACT @80].
- EVERY exit of a recursive body: `CALL ?RSBLK; RET` — base case AND
  recursive case [RFACT @95/@98, @7C region].
- Self/backward CALL operand = inline RELOC(code,entry); forward CALL
  operand = zero DATA slot + LINK-CHAIN-ADDR at the callee's first byte.
- Expression call argument: evaluate to HL, `SHLD <prescan temp cell>`,
  the deferred pointer pair then links slot -> temp [RFACT @80-84].
- Call expression as a PUT LIST item: Esuffix->PInum descriptor pair,
  then LXI H,*A(cell) + CALL [NFACT @47-4A].
- `i * f(i-1)` (call on the RIGHT of MUL) evaluates RIGHT FIRST:
  arg -> SHLD -> CALL -> PUSH H -> LHLD left -> POP D -> ?IM22N
  [RFACT @8D-9C].
- RECURSIVE is an ATTRIBUTE, not a call graph property: R411 declares
  `f: procedure(i) returns(fixed) recursive` with NO call anywhere and
  still gets the full SVBLK/shadow/RSBLK machinery (byte-identical).
  bind.ml ORs the attribute with call-derived recursion.
Limitations: multi-formal, POINTER/BASED formals, no-formal procedures
[R425], CALL statements and >=2 forward refs to one procedure [P403]
remain fail-loud [TBD].

## C082 — Epilogue displacement window and TAIL GUARD (E2E-5c slice 2)
STATUS: CONFIRMED for all 37 specimens of the guard matrix; the rule is
a SINGLE condition with no loop-classification heuristic.
- Suppression window: a main-block no-exit loop (`DO i=c REPEAT(...)`
  with no TO/WHILE, or `DO WHILE('1'B')`) leaves the window OPEN. While
  it is open, a `stop;` at the window address prints NO code and the
  epilogue `CALL ?STOPX` is DROPPED (final LC == last back edge or the
  appended proc code) [RFACT/R407/R408/R410/R411/R414/R415/R418/
  R421/R422/R424/R425/R426/R427/R431]. Any other executable main-block
  statement ANCHORS (emits code) and CLOSES the window [R401/R409/
  R412/R419/R423/R428]. Procedure blocks do not close it [RFACT/R410].
- TAIL GUARD (the correction of the pre-existing hypothesis): when the
  FIRST top-level procedure body is appended AND the epilogue CALL
  will be emitted after it — i.e. NO explicit stop was printed in place
  AND the window is CLOSED at that proc entry — DR emits 3 bytes at the
  APPEND address, before the entry label / forward-call CHAIN-ADDR /
  prologue:  `C3 00 00`  (JMP <epilogue CALL address>). The operand is
  resolved by the ordinary deferred backpatch triple
  `SET-LC(code,slot) ; RELOC(code,epi) ; SET-LC(code,epi)` emitted
  immediately BEFORE the epilogue CALL bytes.
  Evidence (slot -> target, all == the CD of `CALL ?STOPX`):
  R404 0x29->0x44, R405 0x29->0x6E, R406 0x10->0x55, R423 0x34->0x57,
  R429 0x29->0x44, R432 0x0D->0x28, P404 0x10->0x2B.
  The guard is NOT chained (no CHAIN-ADDR) and its target is NOT the
  ?STOPX operand slot. It is the same continuation mechanism as the
  PUT/LXI-B triples [G113/P401].
- CORRECTION: the earlier candidate rule ("guard iff window OPEN and
  the tail loop CAN exit, i.e. has TO/WHILE") is REFUTED — P404/R432/
  R406 have NO loop in the main tail at all, and R414/R426/R427
  (window open) are byte-exact only with NO guard. `pl_tail_exit` has
  been removed from bind.ml as an unnecessary and wrong predicate.
- R423 needs NO special case: its forever loop + suppressed stop +
  label-anchor `t: put list('K')` closes the window, so the general
  rule fires. Recorded here because it was previously classified as an
  exception requiring a separate `tail_stop_dead` OR-condition.
- Verified-unproven boundary: a SECOND appended procedure in a guarded
  shape (no golden has two top-level procedures) fails loud [TBD]; so
  does an unguarded-then-guarded reordering. R430/R433/R417/R416/
  R409/R402/R432-vs-R433 pairs bound the rule from both sides.

## C083 — Runtime verification of the recursive/loop specimens (E2E-5c slice 2)
STATUS: CONFIRMED (byte-identical images + bounded complete-record console
prefixes + an independent arithmetic oracle)
- NFACT: .REL byte-exact, linked .COM IDENTICAL vs DR (7552 B), RAW
  console BYTE-EQUAL (217 B), and the factorial table is independently
  correct: f(0)=1 f(1)=1 f(2)=2 f(3)=6 f(4)=24 f(5)=120 f(6)=720
  f(7)=5040 (= math.factorial).
- RFACT (no-exit main tail): .REL byte-exact, linked .COM IDENTICAL vs
  DR (7552 B). Console compared through the BOUNDED PREFIX PROTOCOL
  (tools/prefix_check.py): both arms re-run under the harness with
  `--killon` at the SAME program-derived record boundary (never a
  timeout cutoff), and the first 12 COMPLETE records are byte-equal; the
  first 8 factorial records match math.factorial independently.
  RFACT's main loop never exits, but the run itself ENDS: at
  factorial(249) the DR runtime reports `Free Space Overwrite` (SVBLK
  stack grows into free space) and returns to `D>`. So DR's own runtime
  terminates this "non-terminating" program; nothing about that verdict
  is claimed beyond the observed bytes.
- R401 / R412 / R419 (no-exit tail, no console output before the tail):
  linked .COM IDENTICAL vs DR (6784 / 640 / 6784 B); runtime verdict =
  byte-identical image (they produce no console region to compare).
- Harness fix (oracle/linkrun.py): the run session now sends a lone CR
  and waits for the FRESH `D>` prompt before typing the program name.
  Without that sync the stale drive-switch prompt could satisfy the
  later `##WAIT \nD>`, aborting long-output programs before they printed
  anything (observed as empty transcripts for RFACT). The extra bytes
  land before the program's own console region, so transcript extraction
  (anchored on `NAME\r\r\n`) and all previous console comparisons are
  unaffected; a new optional `--killon REGEX` gives the bounded prefix.

## C084 — FIXED DECIMAL core: storage, literals, arithmetic, ABI, returns (E2E-6)
STATUS: CONFIRMED (12 specimens .REL byte-identical + .COM identical +
console byte-equal; acceptance specimen DFACT byte-identical to the
curated corpus golden, plus runtime prefix + independent arithmetic)
Evidence: golden/e2e6/R501,R502,R503,R505,R506,R508,R509,R510,R511,
R513,R514,R515 (fresh DR compiles, $L$D$C$S) + golden/e2e6/DFACT (re-run of the corpus
source; its .REL is byte-identical to golden/first8080u/DFACT/DFACT.REL,
verified by cmp BEFORE either was registered -- the $C trace is the new
information) + golden/first8080u/DFACT/DFACT.REL (acceptance).

STORAGE (bind authority, now DR-proven rather than inferred):
- bytes(FIXED DEC(p,s)) = ceil((p+1)/2), INDEPENDENT of scale, DIRECTLY
  OBSERVED at NINE precisions: p=1 -> 1 [R514], p=3 -> 2 [R513],
  p=4 -> 3 [R515], p=5 -> 3 [R503], p=6 -> 4 [LOAN1 $S], p=7 -> 4 [R508],
  p=9 -> 5 [R502/R505/R512], p=11 -> 6 [LOAN1 $S], p=15 -> 8
  [R501/DFACT]. This is exactly Bind.bytes_of `RTdec (p,_) = (p+2)/2`,
  which was carried as a hypothesis; nine sampled points spanning the band
  make it far more than a fit, but it is NOT a per-value verification: the
  six unsampled precisions p = 2, 8, 10, 12, 13, 14 are LAW-PREDICTED, not
  observed, and a p-parity bug confined to one of them would not be caught
  by any current specimen. (Amended by C086, which read p=6/p=11 out of
  LOAN1's $S instead of trusting the formula.) DR itself stops at p=31
  (`NOT IMP`, no .REL [R504]).
- packing = little-endian packed BCD, two digits per byte as
  (hi<<4|lo), sign nibble in the TOP nibble of the last byte (0 = +).
  Byte-for-byte against DR: 3@p15 -> `03 00 00 00 00 00 00 00` [R501];
  123.45@p7s2 -> `45 23 01 00` [R508]; 1@p9s2 -> `00 01 00 00 00`
  [= 100, i.e. the literal pre-scaled to the TARGET scale] [R505];
  1234@p4 -> `34 12 00` [R511]; 1@p15s0 -> `01 00 ...` [DFACT @S(000C)].
- DEC pool cells are NOT deduplicated and are allocated in flow order
  (R505: 1 at S(0000), 2 at S(0005)), same regime as character literals.

EVALUATION MODEL -- DR runs a decimal STACK, not an accumulator register:
- ?DLDOP pushes (HL = cell address, A = digits); ?QI15D pushes the DEC
  image of the INT(15) value already in HL; a DEC function call pushes
  its result (callee exits `JMP ?DCRET`); ?DADOP/?DSUOP/?DMUOP pop two
  and push one; ?DSTOP pops into a cell (HL = addr, A = TARGET digits);
  ?QDCOP pops and edits into the print buffer (A = width, B = scale).
- push ORDER: left operand first [R505 a+b, c-a, a*b; R511]; the one
  observed case whose RIGHT operand is a DEC call evaluates that call
  first, then reloads the left operand [DFACT: CALL, LHLD i, ?QI15D,
  ?DMUOP] -- mirroring the fixed-bin "right-first when RHS is a call".
- ?QDDSR (rescale to A) appears after ?DMUOP iff the STORE TARGET has
  scale > 0 [R505 dec(9,2) emits MVI A,02; R510 and DFACT dec(*,0)
  emit none]. ADD/SUB never carry a rescale [R505].
- DEC default print WIDTH = p + 3 and B = s, on all TEN edited samples
  (15/0 -> 18/0, 9/2 -> 12/2, 9/0 -> 12/0, 5/0 -> 8/0, 7/2 -> 10/2,
  4/2 -> 7/2, 3/0 -> 6/0, 1/0 -> 4/0). Confirmed at RUNTIME by the field
  contents (R501 '                 3', R508 '    123.45',
  R513 '    12', R514 '   1', R515 '   1.25').

LITERAL PRECISION RULE (two-position, both directly observed):
- bare literal in assignment / RETURN position takes the TARGET's
  digits and scale [R501 d=3 -> A=15; R505 a=1 -> A=9; DFACT
  return(1) -> A=15, 8-byte cell];
- literal as an ARITHMETIC OPERAND takes its OWN digit count with
  scale 0 [R509 *2 -> A=1, 1-byte cell; R511 *1234 -> A=4, 3-byte cell].

CONVERSIONS AND BUILTIN:
- DECIMAL is a DR BUILTIN symbol (`a 0000 DECIMAL BUILTIN CONSTANT`
  [R506/R509]), not a procedure: added to the parser's builtin table, so
  `decimal(i,15)` no longer reaches bind as a 2-argument CALL.
- decimal(x,p) IGNORES p: decimal(i,15) and decimal(i,7) compile to the
  identical `LHLD x ; CALL ?QI15D` pair [R506]. DEC precision comes from
  the context (assignment target / return cell), never from the builtin.
- DEC -> INT: DLDOP(source digits) ; ?QDI15 ; SHLD [R506 `i = d`].
- DEC function exits via `CALL ?RSBLK ; JMP ?DCRET` when RECURSIVE and
  plain `JMP ?DCRET` when not [DFACT @0086/@00A2, R509 @0056]; the
  caller side of the call site is byte-identical to the FIXED ABI
  (`LXI H,*A(slot) ; CALL f`) -- ?DCRET hands the value back on the
  decimal stack, so the caller stores with ?DSTOP [R509] or prints with
  ?QDCOP [DFACT]. FUNCTION descriptor cell = bytes_of(returns type)
  (`.* FIXED DECIMAL(15,0) RETURNED` then PARAMETER at +8 [R509]).

FAIL-LOUD PERIMETER (each member is a tested negative, NEG panel 25/25):
- DEC COMPARISON unimplemented. DR lowers `if d > 0` as
  DLDOP(const),DLDOP(d),?DCMOP,JP [R507], but the operand ORDER for the
  non-commutative relations is unpinned -> refusing beats guessing an
  order that could silently invert the test [N25].
- DEC DIVISION unimplemented. Observed shape is DLDOP, `MVI A,06
  ?QDDSL`, DLDOP, ?DDVOP, `MVI A,06 ?QDDSR`, `MVI A,02 ?QDDSR` [R512];
  the meaning of the two 06s (target p - s - 1?) is a single sample ->
  [N26].
- p outside 1..15: DR itself says `NOT IMP` at p=31 with NO .REL [R504],
  and 16..30 is unpinned, so the band boundary is mirrored as a refusal
  [N27] rather than extrapolated into a cell size.
- literal scale > target scale (digit loss) [N28]; fractional literals
  in OPERAND position; negative DEC literals (sign nibble unpinned).
- mixed DEC/INT arithmetic: the DEC->INT conversion is pinned only for a
  DIRECT decimal operand (`i = d`), so mixed trees refuse [N29].
- DEC arrays/structures, DEC in GET, PUT EDIT pictures (?QDDSL/QDDSR
  picture family), DEC ENTRY-external returns: all still [TBD].

PROCESS NOTE (defect hygiene came first): Step 0 (commit 64da8f9) closed
the audit's D1 crash, D3 silently-ignored block options and D4
silently-FIXED return types BEFORE any DEC byte existed. FFACT moving
from a plausible-but-wrong .REL to a deliberate [TBD] refusal is the
intended outcome, and DFACT's first refusal was `returns(FIXED
DECIMAL(15,0))` -- the gate that this claim now opens for p<=15.

GATES AFTER E2E-6 DEC CORE: e2e 96 byte-exact / 0 fail (was 83);
negative panel 25/25 refused; every DEC specimen ALSO has .COM IDENTICAL
and console BYTE-EQUAL (R501 '                 3', R502 '        3.00',
R503 '       3', R505 '        2.00', R506 '                 5         5',
R508 '    123.45', R509 '                 6', R510 '           2',
R511 '        1234', R513 '    12', R514 '   1', R515 '   1.25');
parse 397 ok / 6 parity-rejects / 0 FAIL; bind 47/47 exact;
rel round-trip 369/369; ir gate 0 FAIL; safety 28/28.
CORPUS: DFACT accepted -> 3/41 attainable programs byte-exact (DEMO,
RFACT, DFACT), 0 divergent compiles, 0 crashes, 41 loud [TBD] refusals.
DFACT RUNTIME (non-terminating main tail, bounded protocol): .COM
IDENTICAL vs DR (8192 B); first 12 COMPLETE records byte-equal; 16
complete factorial records independently correct against
math.factorial -- DEC(15,0) carries the table to i=15 where RFACT's
FIXED BIN(15) overflowed at i=8.

## C085 — FIXED DECIMAL comparison + two general DR codegen laws (E2E-7A slice 1)
STATUS: CONFIRMED (15 specimens .REL byte-identical; DR-side runtime
semantics observed for all nine comparison shapes; own-arm link/console
parity verified for the same set)
Evidence: golden/e2e7/R601..R614 (fresh DR compiles, $L$D$C$S) +
golden/e2e6/R507 (now implemented, was refusal evidence) +
golden/e2e7/LOAN1 (LOAN1 re-compiled with $C: .REL BYTE-IDENTICAL to the
curated golden golden/first8080u/LOAN1/LOAN1.REL, so the trace IS the
listing of the accepted program) + DR run transcripts (branch outcomes).

?DCMOP TAKES NO RELATION ARGUMENT. It pops two decimals and leaves a
three-way result in the 8080 flags; DR therefore encodes the relation in
the PUSH ORDER plus the choice of SKIP jump (taken iff the condition is
FALSE). Derived from 9 byte-level samples, then confirmed by running every
one of them under DR and checking which branch executed:

    CY = (top <= bottom)   Z = (top = bottom)   S = (top > bottom)
    (top = the SECOND operand pushed)

    A >  B  push B,A  JP  (F2)     A <  B  push A,B  JP  (F2)
    A >= B  push A,B  JM  (FA)     A <= B  push B,A  JM  (FA)
    A =  B  push A,B  JNZ (C2)     A ^= B  push A,B  JZ  (CA)

Runtime truth [golden/e2e7run, p=5 q=3, both operand orders in one
program, s=1 means the branch was taken]:
    R601 `>`   s=1 t=0    R602 `<`  s=0 t=1    R603 `=`  s=0 t=0
    R604 `>=`  s=1 t=0    R605 `<=` s=0 t=1    R606 `^=` s=1 t=1
    R607 `0 < p` -> s=1   R608 do while (p>0) -> m=3, p=0.00 (three
         subtractions, loop exited through the JP -> 0057 back edge)
    R609 nested-DO then-block executed (printed 1)
  All nine match the table above. Nothing here is inferred from DR's
  disassembly labels alone.
- "JZ" is opcode CA = JPE, i.e. the SAME mnemonic/opcode skew already
  banked for integer `^=` [C072]; one opcode table serves both families.
- The skip-jump operand is backpatched by the ordinary SET-LC/RELOC
  continuation triple -- no new mechanism. Recovered targets: [R507]
  JP -> 004F = the CALL ?STOPX; [R608] JP -> 0057 = first address after
  the loop; [LOAN1] JP -> 01E4 (inner-while exit, = the outer back edge),
  JP -> 01A8 (past `PMT = P`), and the three GET JPs -> the statement's
  own trailing CALL ?QIOOP (003E/0074/00AA) i.e. input failure skips the
  conversion+store. LOAN1's `if mod(m,12) = 0` JNZ -> 010D.
- Compare LITERALS take the DEC partner's precision [R507/R607: `0`
  pushed MVI A,09 against dec(9,2); LOAN1: `0` -> 6-byte cell S(001E)
  with MVI A,0B against dec(11,2) P].

TWO GENERAL (NOT DECIMAL-SPECIFIC) LAWS FOUND WHILE VALIDATING THIS:
- D6 HL-CONSTANT REUSE, delta 0: consecutive assignments of the SAME
  integer literal emit ONE `LXI H,k` and one store per variable --
  `x = 0; y = 0;` -> LXI H,0000; SHLD X; SHLD Y [R610, and LOAN1's
  `m = 0; y = 0;` at 00AD-00B3]; `x = 5; y = 5;` behaves identically, so
  it is value equality, not a zero special case [R611]. Boundary cases:
  an intervening statement that writes HL restores the fresh load [R612:
  `x = 0; put...; y = 0;` re-emits LXI H,0000]; and DR does NOT track
  values that came from MEMORY -- `y = x; z = x;` re-emits `LHLD X` both
  times [R613]. This joins the existing G114/G116 reuse family (DCX/INX
  ladders for |delta|<=2, MOV L,H for k=0, MVI L for same-high-byte).
  Without it LOAN1 could never be byte-exact.
- D7 DECIMAL POOL REUSE: identical DEC literal cells are shared --
  `d = 3; e = 3;` (both dec(9,2)) emits `LXI H,* S(0000)` twice from ONE
  5-byte cell [R614]. This CORRECTS C084's statement that DEC cells are
  never deduplicated: that was inferred from R505, whose two literals
  have DIFFERENT values and so say nothing about reuse. Keyed on the
  packed byte image (precision, scale, magnitude), so a differing
  precision or scale still gets its own cell. Pool DEMAND in the prescan
  had to be made distinct-key too, or every variable address after the
  pool shifts.

CORRECTION TO C084's LITERAL-PRECISION LAW (it was only half right):
- C084 said "a literal as an ARITHMETIC OPERAND takes its own digit
  count with scale 0". That holds for MULTIPLY and DIVIDE [R509 `*2`
  -> A=01; R511 `*1234` -> A=04 3-byte cell; LOAN1 `/1200` -> A=04
  2-byte cell S(0028)], but ADD and SUBTRACT instead ALIGN the literal
  to the DEC partner: R608's `p = p - 1` against dec(9,2) pushes
  `MVI A,09` from a 5-byte cell holding 1.00 (pool bytes 00 01 00 00 00)
  [R608 $C + .REL data dump]. Same rule as the compare literals. My
  compiler previously used own-digits for +/- too, which was SILENTLY
  WRONG for `dec_var +/- int_literal` -- no registered specimen exercised
  that shape, so nothing caught it until R608. Now implemented, with the
  two unresolved cases refused: partner precision unknown, and partner
  (p,s) disagreeing with the store target (no sample says which wins).

FAIL-LOUD PERIMETER AFTER SLICE 1 (each a tested negative, panel 26/26):
- compare literal with a SCALE against a scaled variable (`d > 3` with
  dec(9,2)): the two candidate encodings (3 vs 300) are not distinguished
  by any sample [N25_DECCMP_SCALE].
- `decimal(x,p)` as a relational operand: [R506] pins DECIMAL only as the
  INT->DEC doorway in an assignment [R607's DECIMAL-free form and
  R601-R606 var/var + var/0], never inside a relation [N30_DECCMP_BUILTIN].
- DEC divide / round / scale-carrying literal pools / DEC arrays / DEC in
  GET / PUT EDIT pictures: unchanged from C084, all still [TBD].
- +/- literal where the partner is not a statically-typed DEC variable or
  DEC function call: refused rather than sized by a guess.

GATES AFTER E2E-7A SLICE 1: e2e 111 byte-exact / 0 fail of 111 (was 96);
negative panel 26/26 refused (N25 replaced by two narrower unpinned
shapes); parse 412 ok / 6 parity-rejects / 0 FAIL of 418; bind 47/47
exact; rel round-trip 385/385; ir gate 0 FAIL; safety 28/28.

## C086 — FIXED DECIMAL divide + the unified scale-shift law (E2E-7A slice 2)

STATUS: ACCEPTED. 25 probes generated and DR-compiled (R701-R725); 23
registered byte-exact positive specimens (135/135 gate total), each also
linked-.COM identical to DR and console byte-equal; R709/R725 excluded from
the positive panel because they evidence a REFUSAL (see DEFECT below); and
R512 (`c = a / 2`) promoted from old divide-refusal evidence to POSITIVE,
which is why its negative N26_DECDIV is retired rather than kept as a twin. plus an
independent Python simulator (tools/decmodel.py) that reproduces DR's
emitted decimal-stack token schedule for all 49 DEC probes it can parse
(0 differences) and declines 4 DEC-*call* shapes by design.

NEW ROUTES: ?DDVOP ?QDDSL ?QDDSR (the latter two were already emitted by
slice 1's multiply rule in one shape only). DEC ABI surface is now 12
routes; LOAN1 needs 23, so 4 remain unseen (?QCDOP ?DROUN ?EDITF/?EDTOV
are not LOAN1's -- LOAN1's remaining set is ?QCDOP ?DROUN + GET-path
routes, see spec/notes/e2e7-loan1-dependencies.md).

THE MODEL: a decimal-stack entry carries (p = digits, s = scale), value
m/10**s. ?QDDSL n shifts the CURRENT TOP left (m *= 10**n, s += n, value
preserved); ?QDDSR n shifts it right (m //= 10**n, s -= n, value
preserved, TRUNCATING). Because the shift acts on the top, its POSITION
between/after the two operand pushes identifies which value is adjusted --
that is what makes the traces decodable, and it is why one shift pair looks
like two different laws until you notice the stack.

L1 +/- align the SHORTER operand UP to max(s_l,s_r); equal scales emit
   nothing; both directions proven for SUBTRACT, not inherited from ADD
   [R705 shift-between-pushes, R707 shift-after-both, R715 both directions
   of -, R505/LOAN1 equal-scale, R608 literal pre-aligned so no shift].
L2 * performs NO alignment; result scale = s_l + s_r [R711 `d = a*b` into
   dec(9,4) emits nothing at all; R719/R720 product scale 4 into a dec(9,2)
   target gets exactly one ?QDDSR 2].
L3 / pre-shifts the DIVIDEND by N = 15 - p_dividend and omits the pair
   entirely when N = 0 [p=9 -> 6: R512,R701,R703,R708,R712,R713,R714,R717,
   R718; p=11 -> 4: R710, so N is not a constant; R702 dividend dec(9,2)
   against a dec(13,2) TARGET still gets 6, so N tracks the DIVIDEND;
   LOAN1/R704 dividend = 15-digit product -> N=0 -> no pair].
L4 quotient scale = s_l + N - s_r (N>0) else s_l - s_r. The quotient's
   PRECISION is unpinned -- no trace ever exposes it -- so a quotient used
   where N is needed refuses [N32_DIV_CHAINED].
L5 the CONSUMER fixes the scale: store/return shifts DOWN (?QDDSR) or UP
   (?QDDSL); an enclosing +/- aligns its own operands instead and adds no
   fix [R701 down 4, R713 down 2, R716 UP 2 into dec(13,8), R711 up 2,
   R505 down 2, R721/R722 quotient carries scale 6 into the add untouched].
L6 result precision is observable only through the next division's N:
   +/- -> min(15, min(p_l,p_r)+1) [R714 (9,9)->10, R717 (9,6)->7, R718 sub
   (5,5)->6]; * -> min(15, p_l+p_r+1) [R718 (5,5)->11; LOAN1/R704
   4+11+1 -> 15 cap -> N=0].
L7 push order: RIGHT first iff it is compound and the left is simple
   [DFACT, R704, R719, R722]; left first otherwise, both-compound [R720,
   R724] and both-simple [R505, R705, R707] included. / ALWAYS pushes the
   dividend first, even against a compound divisor [R712], because the N
   pre-shift has to act on the top.
L8 integer literals: store/return role -> target (p,s); additive/compare
   role -> DEC PARTNER (p,s); multiplicative role -> own digit count with
   scale 0 [R509 *2 A=01, R511 *1234 A=04, R512/R703/R710 /2 /8 A=01,
   LOAN1 /1200 A=04 from a 3-byte cell S(0028)].
L9 DIVISION TRUNCATES, it does not round: R706 printed 2/3 into dec(9,2)
   as 0.66 (half-up would be 0.67) and 9/2 into dec(9,0) as 4; R703/R712
   (7/(3*2) = 1.16) agree. This is the shift-right truncation of L1-L5,
   not a separate rounding rule.

CORRECTIONS TO BANKED CLAIMS:
- C084 "ADD/SUB never carry a rescale" is INCOMPLETE: true only for equal
  scales; unequal scales get the L1/L5 pair [R705, R707, R715].
- C084 "the post-multiply rescale amount is target_scale" is the WRONG
  FORMULA (right answer on its one sample by coincidence): the amount is
  result_scale - consumer_scale = (s_l+s_r) - s_t. R711 (product scale 4
  into dec(9,4)) emits nothing, which the old rule got wrong.
- C085's HL-constant-reuse law D6 is a STRAIGHT-LINE peephole: R723 shows
  `if a > e then m = 1; else m = 0;` reloading `LXI H,0000` in the else
  branch instead of reusing HL through the [G116] MOV L,H trick. My
  unqualified rule fired across the branch boundary (2 bytes short) and
  this was caught by byte-comparison, not by inspection. The tracking
  state now dies on every jump emission.
- L9 also means the DECIMAL rounding MODE (half-up vs half-even) remains
  UNTESTED for `round()`, because division never rounds. That question is
  still open for slice 3; LOAN1's published schedule does not settle it
  (no half-cent month).

DEFECT FOUND AND CLOSED (was fail-silent, is now fail-loud). Sampling
honesty: C084's cell law is directly observed at NINE precisions
(p=1,3,4,5,6,7,9,11,15), NOT at all fifteen -- p=2,8,10,12,13,14 remain
law-predicted (C084 bullet amended accordingly by this claim).
R709/R725 (DEC call as a divide operand) exposed a pre-existing wrong-code
path: DR passes a FIXED DECIMAL formal BY REFERENCE -- the formal gets a
2-BYTE cell holding the caller's address (prologue `MOV E,M; INX H;
MOV D,M; XCHG; SHLD J`, reads `LHLD J; MVI A,digits; CALL ?DLDOP`). My
build gave the formal a full BCD cell (mis-sizing AUTO storage) and pushed
`LXI H,J` (address, not pointer) -- and COMPILED WITHOUT COMPLAINT. It now
refuses: "FIXED DECIMAL formal parameter j is unproven [TBD]" [N33].
DFACT/R509/R510 are UNAFFECTED: DR resolves a bare `dcl i fixed` as FIXED
BINARY(15,0), and those formals are the by-value 2-byte copy already proven
byte-exact.

FAIL-LOUD PERIMETER AFTER SLICE 2 (panel 30/30, each a tested negative):
literal dividend in a divide [N31]; quotient consumed where its precision
is needed [N32]; DEC formal parameter [N33]; divide whose quotient scale
would be NEGATIVE (s_r > s_l + N) [N34]; direct DEC operand stored into a
different SCALE (only computed values are pinned as needing a fix, and
LOAN1's PMT = P crosses precisions but not scales) [N35]; unchanged from
C084/C085: scaled compare literal [N25], decimal(x,p) inside a relation
[N30], DEC(>15) [N27], fractional literal into scale 0 [N28], mixed
DEC/INT arithmetic [N29], PUT EDIT, rounding, GET of numerics.

GATES AFTER SLICE 2: e2e 135 byte-exact / 0 fail of 135 (was 111 at 3636eec);
negative panel 30/30 (N26_DECDIV retired -- `c = a / 2` is now PROVEN --
and N31-N35/N33 added); parse 436 ok / 6 parity-rejects / 0 FAIL of 442;
bind 47/47; rel round-trip 411/411; ir 0 FAIL; safety 28/28. Corpus sweep
(44 sources in artefacts/, 41 with DR goldens): 3 byte-exact (DEMO, RFACT,
DFACT), 0 divergent, 39 refusing with an explicit [TBD], and 2 that fail
LOUDLY but WITHOUT the [TBD] word -- CALL (parser: "expected statement", no
DR golden) and LABELS (codegen: "undeclared x", has a golden). Both were
re-tested against a clean build of 3636eec and behave BYTE-FOR-BYTE the same
way, so they are PRE-EXISTING diagnostic-wording debt, not slice-2
regressions; they are recorded here instead of being counted as "0 crashes",
which would have been false on a strict reading. LOAN1 now refuses at GET
(its comparison and `p = p - pmt` forms are byte-exact).

## C087 — FIXED DECIMAL ROUND (?DROUN) + the tie rule (E2E-7A slice 3)

STATUS: ACCEPTED. 13 probes generated and DR-compiled (R801-R813,
`$L$D$C$S`, golden/e2e9/); 8 registered byte-exact positives (gate 143/143),
each also linked-.COM identical to DR and console byte-equal (all terminate
with `stop;` -> COMPLETE transcripts, no bounded-prefix protocol); 5 refused
by design with their DR goldens kept as evidence; 8 new tested negatives
(N36-N43), panel 38/38.

?DROUN CONVENTION (every byte observed, none extrapolated):
`MVI A,k; CALL ?DROUN` with **k = (scale of the stack entry) - n**, i.e. the
number of fractional digits to DROP, not the requested scale n. Samples:
s=3,n=2 -> 01 [R801,R802,R803,R811]; s=6,n=2 -> 04 [R804,R807]; s=4,n=2 -> 02
[LOAN1,R813]; s=3,n=0 -> 03 [R806]; s=3,n=3 -> 00 [R811 inner]. k=0 IS
EMITTED (unlike the divide pre-shift, which vanishes at N=0 [L3]).

THE ENTRY KEEPS ITS SCALE -- proven three independent ways: R801 still needs
`QDDSR 1` to store into a dec(9,2) target (if DROUN set s=2 the shift would be
zero and absent); R804/R807 need the same `QDDSR 4` the shift-only case needs;
and R807/LOAN1/R813 show the enclosing `+` lifting the OTHER operand up to the
rounded entry's ORIGINAL scale (6 in R807, 4 in LOAN1) via `QDDSL`. So ROUND
adds no new shift machinery: L1 (align shorter up) and L5 (consumer fixes the
scale) apply verbatim, computed from the pre-round scale. My compiler emits
push(argument) -> MVI A,s-n -> ?DROUN -> ordinary consumer fix, and inherits
all arithmetic from DR's ?DROUN at run time.

PUSH ORDER: `X + round(<compound>, n)` pushes the ROUND subtree FIRST [LOAN1
0142-0162 before P at 0165; R813 0026-0046 before P at 0049] -- law L7 once a
round node with a compound argument counts as compound. Simple-argument round
inside +/- has no sample -> refuses [N41].

TIE RULE = HALF-UP, AWAY FROM ZERO, established from DR's own printed values
(this is DR's runtime, not my code, so it is evidence about the machine):
round(2.125,2)->2.13, round(2.135,2)->2.14, round(2.145,2)->2.15,
round(2.155,2)->2.16, round(-2.125,2)->-2.13, round(2.5,0)->3. 2.125 and
2.145 falsify HALF-EVEN (2.12 / 2.14); -2.13 falsifies toward-+infinity.
This CLOSES the open question in C084/C086 ("rounding mode untested, because
division truncates and never ties"). LOAN1's schedule still does not settle
it -- no half-cent month -- so the mode came from these dedicated probes.

ROUND SEES THE PRE-STORE STACK VALUE, not a truncated copy: with two=2,
three=3 (dec(9,2) each), `x = two/three` prints 0.66 while
`y = round(two/three,2)` prints 0.67 [R804]; `p = p + round(seven/three,2)`
prints 102.33, not 102.32 [R807].

LOAN1 SHAPES NOW BYTE-EXACT: R813 is LOAN1's line `P = P + round(i*P/1200,2)`
with LOAN1's own declarations; its instruction stream matches LOAN1's
0142-017F exactly and it prints 505.83 = LOAN1's month-1 balance.

CORRECTIONS / UPDATES TO BANKED TEXT:
- C084/C086 listed "rounding" in the fail-loud perimeter as a decimal gap.
  2-arg ROUND of a DEC expression is now PROVEN and implemented; the
  perimeter was replaced by the 8 narrower negatives below, not deleted.
- C086's "the DECIMAL rounding MODE (half-up vs half-even) remains UNTESTED
  for round()" is superseded: half-up, away from zero, from six printed
  values.
- C086's DEC ABI route list grows to 13 (?DROUN added). The count of routes
  LOAN1 needs that my build has never emitted drops to 1 (?QCDOP for numeric
  GET); ?IROUN is newly OBSERVED in a DR listing but is not LOAN1's.

DEFECT CAUGHT BEFORE SHIPPING (not a shipped regression): my first R813 build
compiled but differed from DR in 11 bytes, because the DEC-literal pool
prescan (`pdec_operand_bytes`) had no ROUND case, so the 1200 cell inside
`round(i*P/1200, 2)` went uncounted, the pool came out 3 bytes short and
every AUTO base after it moved. Layout-wrong output with no diagnostic -- the
fail-silent shape -- caught by raw byte comparison against a fresh DR golden
before registration. The digit count n contributes nothing to the pool by
design: it becomes an immediate byte.

FAIL-LOUD PERIMETER AFTER SLICE 3 (panel 38/38, each tested):
one-argument ROUND [N36] (DR itself rejects it: `SYNTAX ?`, no .REL [R808]);
ROUND of a bare literal [N37] (R809 shows a THIRD literal role -- own digit
count AND own scale, A=04 for 2.125 -- one sample); ROUND of an integer
argument [N38] (DR uses a separate route ?IROUN then ?QI15D with no ?DROUN at
all [R810]); ROUND with a non-literal digit count [N39] (R812 computes
k = 3-n at run time as LHLD/MOV A,L/SUI 04/CMA -- template known, not
implemented); ROUND with n ABOVE the operand scale [N40] (R805 emits the
WRAPPED byte 0xFE; value unchanged in that one sample, rule unpinned);
simple-argument ROUND inside +/- [N41]; ROUND in a multiplicative position
[N42]; ROUND result as a divide dividend or divisor [N43] (a rounded entry's
precision is not observable -- same family as L4). Unchanged from C084-C086:
DEC formal parameters [N33], scaled compare literals [N25], decimal(x,p) in a
relation [N30], DEC(>15) [N27], fractional literal into scale 0 [N28], mixed
DEC/INT arithmetic [N29], PUT EDIT, numeric GET.

GATES AFTER SLICE 3: e2e 143 byte-exact / 0 fail of 143 (was 135); negative
panel 38/38 (was 30); parse 445 ok / 6 parity-rejects / 0 FAIL of 451; bind
47/47; rel round-trip 421/421 -- that is EVERY .REL on disk, which
is 409 tracked goldens plus 12 .REL copies sitting in the gitignored link/run
scratch tags (e2e7link/e2e8link/e2e9run); the number therefore moves with
harness state and is reported with that explanation, not as a fixed count; ir 0 FAIL; safety 28/28; clean-build warnings
63 -> 63 with none inside new code (measured against the 3636eec baseline).
Independent model: 57 SCHED MATCH / 0 DIFFER, 30 VALUE-MATCH / 0 VALUE-DIFF
over the whole DEC corpus, with 9 named model-side refusals; its DROUN token
initially missed because dr_tokens()' CALL alternation lacked DROUN/IROUND --
a harness bug fixed before the result was read.
