
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

---

## C088 — numeric GET LIST: one input skeleton, per-kind conversion tail (E2E-7A slice 4)

STATUS: ACCEPTED. 17 probes generated and DR-compiled `$L$D$C$S`
(`golden/e2e10/`, sources `probes/R90*.PLI`/`R91*.PLI`); 16 registered
byte-exact positives (R901-R915, R917), 1 designed refusal whose DR golden is
kept as route evidence (R916, fixed-char GET -> `?SSCFS`, unimplemented
[N44]). All 16 positives additionally link to a `.COM` byte-identical to DR's
and produce byte-equal console transcripts (§6 of
`spec/notes/e2e7a-slice4-get.md`).

THE SKELETON IS SHARED BY EVERY TARGET KIND. X201/X202 (char varying) had
already pinned it; R901-R917 show numeric GET is the SAME template with a
different per-item tail: `LXI D,0290` (the INPUT descriptor -- 0252 is print's,
and the input one is never relocated), `LXI B,0000` whose operand is
triple-patched to the next statement, `CALL ?SYSIN`, then per item
`CALL ?GNVOP` / `JP <skip>` / conversion+store, and ONE `CALL ?QIOOP` for the
whole statement.

ONE GNVOP/JP PAIR PER ITEM, IN SOURCE ORDER. Item k's JP operand is patched to
whatever follows that item's store -- the NEXT item's `?GNVOP` [R904
0013 ==== 001B, R915, R917] or, for the last item, the closing `?QIOOP` [R907,
X202]. A skip therefore abandons the REST of the list while still completing
the I/O call. R907 (`p = 7;` then `get list(p)`, script = EOF) pins this
byte-exactly: its JP target is the `?QIOOP` call (0023 ==== 0032), so the
`?QCDOP`/`?DSTOP` chain is bypassed. What is NOT claimable is the variable's
aftermath: R907's transcript is 2 bytes (the echoed `^Z`) in both arms, and
LOAN1's output likewise stops at `Principal ^Z`, so nothing after an EOF is
ever printed -- "the target keeps its previous value" is a structural
inference from the skipped store chain, not an observed runtime fact.

PER-ITEM CONVERSION BY DECLARED KIND:

    FIXED DEC(p,s) : MVI B,s ; CALL ?QCDOP ; LXI H,var ; MVI A,p ; CALL ?DSTOP
    FIXED BINARY   : CALL ?QCIOP ; SHLD var            (2-byte cell; no MVI)
    CHAR VARYING   : LXI H,var ; MVI B,cap ; CALL ?SSVFS
    CHAR(n) fixed  : LXI H,var ; MVI B,cap ; CALL ?SSCFS   [R916, NOT implemented]

B IS THE TARGET SCALE AND IS UNCONDITIONAL. 02 for `dec(11,2)`/`dec(9,2)`
[R901, R902, R904, R907, LOAN1], 04 for `dec(6,4)` [R902], 03 for `dec(15,3)`
[R906] -- and `MVI B,00` is STILL EMITTED for `dec(9,0)` [R905], so the byte is
not a scale-specialization. A is the target digit count (0B for LOAN1's
`dec(11,2)`, 0F for `dec(15,3)`), and the store is the ordinary `?DSTOP` of
C084.

GET IS THE ONE DEC CONTEXT WHERE THE PRODUCER FIXES THE SCALE. No `?QDDSL` or
`?QDDSR` appears anywhere in a GET [R901-R906, R913]: `?QCDOP` delivers the
scanned field already at the target scale, which is why C086's consumer-fixes-
scale law inverts here -- there was no prior scale to align to. Six GET shapes
sampled (`dec(11,2)`, `dec(9,2)`, `dec(6,4)`, `dec(9,0)`, `dec(15,3)`, and
LOAN1's three targets); no claim is made about precision values no GET probe
touched.

DEFECTS AND LIMITS. (a) The 1-byte FIXED BINARY target is unsampled -- the
`?QCIOP`/`SHLD` form is proven only for 2-byte cells, and a 1-byte cell takes
the 0x32/`STA` store form [C079], so that shape refuses [N46]. (b) Subscripted,
stream, `get data/EDIT/STRING` items and based/pointer/float/bit targets refuse
[N45 + the existing perimeter]. (c) `?SSCFS` for fixed char is observed but not
implemented [N44]. (d) The console arm nearly lied: four probes initially ran
with the harness's DEFAULT input because my harness edits silently no-matched,
which made "console BYTE-EQUAL" an equality between two nothing-outputs; the
scripts were re-applied with an assertion and the four re-verified. Successful
execution, or equal-but-empty output, is never accepted as proof.

## C089 — MOD as a condition: `= 0` / `^= 0`, and MOD's two divisor forms (E2E-7A slice 4)

STATUS: ACCEPTED. Five byte-exact positives (R908-R912, gate 160/160) covering
LOAN1's year-boundary test in every shape it appears in (constant divisor,
variable divisor, `^=`, THEN-block without ELSE, and wrapped in
`do while (dec > 0)`), each linked to a `.COM` byte-identical to DR's with
byte-equal console output whose branch outcome is correct (R908 prints 1 =
THEN, R909 prints 2 = ELSE, R910 prints 3, R912 prints `2 1`). ZERO new
routines: `?IMDOP` was banked in P071B.

SHAPE: evaluate the dividend into HL, park it in DE across the divisor's
evaluation, `CALL ?IMDOP` (remainder returns in HL), then the plain HL-zero
test `MOV A,H / ORA L`, then `JNZ` for `= 0` and `0xCA` for `^= 0` -- DR's
universal `<>` skip byte, which `$C` PRINTS as `JZ` at R910 code 001C while the
.REL byte is 0xca. That extends the C072 parity-defect family (integer
var-literal `^=`, DEC `^=` [C085]) to a third context: the byte, not the
mnemonic, is the oracle.

MOD'S DIVISOR HAS TWO FORMS, and P071B could not see it because its divisor was
a variable. Variable divisor: `PUSH H / LHLD d / POP D` [R909 = P071B's proven
path]. Literal divisor: `MVI A,k / PUSH H / MOV L,A / ADD A / SBB A / MOV H,A /
POP D` [R908, R910, R911, R912, LOAN1 00CF-00D6] -- C079's sign-extend ladder,
with the `MVI A` before the push and the push inside the ladder. The `LXI H,imm`
store form [D6] is NOT used for a divisor. A constant divisor outside 0..255
refuses (only the `MVI A,k` form is sampled).

ONLY `= 0` AND `^= 0`. Other relations against a MOD (`> 0`, `<> k`,
`mod = mod`, non-zero right side) refuse [N47]. This was not a theoretical
caution: my first draft matched any relation and `if mod(i,12) > 0 then`
compiled SILENTLY into a bare HL-zero test carrying the `^=` skip byte -- code
that is simply wrong for `> 0`. Probing the shape I thought was refused is what
exposed it; the pattern is now narrowed to `Eq | Ne`.

LOAN1's own comment header states the algorithm as `P = (P + (i*P) - PMT`,
which its code does not implement (it accrues `round(i*P/1200, 2)` monthly).
The comment is wrong, the program is not: 27 rows independently re-computed in
Python `decimal` match DR's transcript exactly (§7.4 of the slice-4 note), and
the same check shows the transcript is inconsistent with truncating the
division at 2 decimals before ROUND (23 of 27 rows differ) but consistent with
full-precision or 5-digit truncation -- independent confirmation that C086's
scale law survives inside ROUND's operand.

GATES AFTER SLICE 4: e2e **160 byte-exact / 0 fail of 160** (was 143; +16 GET/MOD
positives R901-R915/R917 and LOAN1 itself as the 4th corpus specimen); negative
panel **39/39** (3 GET negatives promoted to positives, 4 tested negatives added:
N44 fixed-char GET, N45 subscripted GET item, N46 1-byte FIXED BIN GET target,
N47 MOD with a relation other than `= 0`/`^= 0`); parse 461 ok / 6 parity-rejects
/ 0 FAIL of 467; bind 47/47; rel round-trip 438/438 (goldens only once the
transient harness tags were cleaned -- the number moves with harness state, as
stated in C087); ir 0 FAIL; safety 28/28; clean-build warnings 63 -> 63 with an
IDENTICAL per-file and per-kind histogram, verified against a freshly built
`3636eec` worktree that was removed afterwards.
Full `--link-run` regression over all 160 positives: 118/118 linked `.COM`
byte-identical to DR and 118/118 raw console transcripts byte-equal on the
console arm, 0 divergences anywhere; the other 42 specimens are the mine-only
non-terminating/no-output set by design (see corpus audit section 14.1).
Independent model: 68 SCHED MATCH / 0 DIFFER and 30 VALUE-MATCH / 0 VALUE-DIFF
over `probes/R5*-R9*`, 8 MODEL-REFUSED (5 = the new MOD-condition specimens,
which the decimal-stack model does not cover). LOAN1: .REL 1536 B byte-exact,
.COM 9984 B identical, 27 complete console records byte-equal under the bounded
`--killon` prefix protocol, schedule re-computed independently in Python
`decimal` (all 27 rows; truncate-at-2-before-ROUND rejected in 23 rows).
Implementation lines since the `3636eec` checkpoint, over `ocaml/`, `tools/` and
`oracle/`: +1,408 / -180 = **1,588 gross**, of which this slice is +248 / -48 =
296 gross -- inside the ~2,000-line consultation threshold, so no mid-slice
pause was needed. (The "+1,190/-162" reported at the end of slice 3 recomputes
to +1,168/-140 on the same path set; the discrepancy is a pre-commit measurement
and the recomputed figures are the ones quoted here.)

---

## C090 — PUT EDIT: the format list compiles to a pool byte table; ?EDITF/?EDTOV (E2E-8 slice 5)

STATUS: ACCEPTED. 14 byte-exact positives (R1001-R1010, R1018-R1022 and R1009,
which is IFACT's own PUT EDIT statement lifted out with two binary variables),
gate 194/194, all linked to `.COM` images byte-identical to DR's with byte-equal
console output.  PUT EDIT is IFACT's last unbanked route and IFACT itself is
`cmp`-identical to `golden/first8080u/IFACT/IFACT.REL` (384 B): the 5th of 41
corpus programs.

SHAPE (statement skeleton): identical to PUT LIST except that the format list is
compiled into a byte table in the `*S` pool, loaded with `LXI H,*S(table) /
CALL ?EDITF` immediately after `?SYSPR` (and after a leading `skip n`), and that
EVERY item's output tail is `CALL ?EDTOV` instead of the `?PNCOP`/`?PNVOP`
choice.  Character and numeric items converge on one routine: R1003 (`a` + char
varying) and R1001 (`f(3)` + binary) both end in `?EDTOV`.

TABLE ENCODING (every row directly observed):
`table = 80 00 | records... | 81`, with `f(w) = 00 w FF`, `f(w,d) = 00 w d`,
`a = 03 FF`, `a(w) = 03 w`, `skip = 0C FF`, `page = 0F FF`.  `FF` is the
"no word argument" filler; a spec's argument byte takes that slot.  IFACT's
`(skip, a, f(2), a, f(7))` -> `80 00 | 0C FF | 03 FF | 00 02 FF | 03 FF |
00 07 FF | 81` (15 bytes at `*S(0000)`; controls and A are 2-byte records, F is
3-byte), which is what the corpus golden carries.

POOL LAW (new, and not local to the statement): **all format tables are
allocated before all other pool items**; tables keep source/depth-first order
among themselves, other literals keep source order among themselves.  R1003 is
the decisive sample -- the table of line 7 sits at `*S(0000)` while the `'AB'`
literal needed by the EARLIER statement (`c = 'AB'`, line 6) sits at `*S(0005)`.
R1021 (two tables, then both literals) and R1022 (a table inside a `DO` body
still precedes a top-level literal) confirm it.  Implemented as
`prealloc_fmt_tables`/`edit_stmts` (depth-first walk before any lowering) with
addresses consumed from `st.fmtq` in the same order.

PERIMETER (tested refusals): a FIXED DECIMAL data item in an EDIT list (no DR
sample pushes a DEC item through an edit list); `put skip edit(...)` (leading
control item: table position unknown); counted SKIP/PAGE (only the bare form's
`FF` filler is observed); control/replication/picture items mixed into the DATA
half.

NEW ROUTINES: `?EDITF`, `?EDTOV` (project emitted-entrypoint count +2).

## C091 — DO control statements: FROM init cost ladder, exit-test peephole, forever vs degenerate forms (E2E-8 slice 5)

STATUS: ACCEPTED. 17 byte-exact positives (R1011-R1015, R1023-R1028, R1030-R1033,
R1037) plus IFACT, whose outer loop is a no-test forever form and whose inner
loop is a variable-FROM descending loop.

LAWS:
1. **Init.** FROM may be a fixed-bin VARIABLE (`LHLD src / SHLD index`
   [IFACT 000C-000F, R1014]).  A constant FROM is loaded by the cheapest
   instruction that produces it given HL's known value: HL already equal ->
   `SHLD` alone [R1015, R1022, R1032]; HL = from-1 -> `INX H` [R1011, Y302];
   H known 0 and from <= 255 -> `MVI L,from` [R1012, R1013, R1030]; else
   `LXI H,from` [Y302, IFACT].  Cost 0/1/2/3 -- strictly the byte-minimal
   choice in every observed case.
2. **The reuse is control-flow sensitive.**  IFACT line 11 (`F = 1`, the first
   statement of a loop body) gets a full `LXI H,0001` although the loop init
   just executed `LXI H,0000`: at a branch target HL holds what the back edge
   left there.  My `last_imm` tracker is therefore cleared at every loop-body
   head and after every `LHLD`.
3. **Exit test.** `LHLD i / <subtract c> / MOV A,H / ORA A / JP skip` rising
   with `c = bound + 1`, and `... / JM skip` falling with `c = bound` -- the
   falling test subtracts the BOUND, never the step [R1013 `to 3 by -2` -> 3
   rungs].  The subtraction is peeled by size: `DCX H` x c for c <= 3
   [R1012/R1023/R1024/R1028], `LXI B,-c / DAD B` for c >= 4 [R1025 (c=4),
   R1026, R1011, R1027 (c=20)] -- the crossover is exactly where rungs stop
   being cheaper than the 4-byte constant form.
4. **Increment.** `LHLD i / (INX H | DCX H) x |step| / SHLD i`, direction from
   the sign [R1011, R1013, R1012, R1033].  A step must be an integer LITERAL
   (an expression step cannot lower to rungs at all); |step| <= 2 sampled.
5. **Two different "no TO" shapes.**  `do i = c by k;` is a no-exit forever
   loop: body, increment, `JMP` back, NO test [IFACT, R1014, R1030], and it
   opens the epilogue-suppression window like the REPEAT forms.  `do i = c;`
   with no BY/TO/WHILE/REPEAT is DEGENERATE: DR stores FROM, runs the body once
   and falls through -- no increment, no test, no back edge, no window [R1032].
   Whether `by 1` (semantically redundant) appears decides if the statement is
   a loop at all.

PERIMETER (tested): DO..WHILE (DR rewrites `while (index < c)` into the bounded
form -- R1016 is byte-identical to R1015 -- a rewrite my build does not model)
[N48/N49]; bound < 1, where DR switches to a general signed compare
`XRA A / CMP M / INX H / SBB M / JM` [R1029] [N50]; |step| >= 3 [N51]; pointer
formal / DEC / non-fixed-bin index (unchanged).

## C092 — fixed-bin var - var goes through ?IS22N, not DAD (E2E-8 slice 5, defect repair)

STATUS: ACCEPTED, as a DEFECT FIX.  Until this slice my build refused
`s = s - i` with both operands variables ("operator not in int subset"),
although E2E-2 claims fixed-bin arithmetic; `s - <literal>` worked.  Nothing in
the accepted corpus needed it (LOAN1 subtracts in FIXED DECIMAL via `?DSUOP`,
RFACT/NFACT multiply), so the hole survived four slices and was exposed by
DO/BY probing (R1033).

LAW: `left - right` with neither side a literal is the ADDITION pair ladder
with the add replaced by the subtract call -- `LHLD left / XCHG / LHLD right /
CALL ?IS22N`, result in HL [R1035 `s = s - i`, R1036 `s = i - i`, both
byte-exact and both link to identical `.COM` with byte-equal console].  That is
the same primitive my condition lowering already used for `var OP var`
relational tests, so nothing new enters the runtime; only the arithmetic arm
was missing.  Pointer-deref operands in this route are unsampled and refused.

GATES AFTER SLICE 5: e2e **194 byte-exact / 0 fail of 194** (was 160; +32
format/DO probes, +R1035/R1036 subtraction, +R1037, +IFACT as the 5th corpus
specimen); negative panel **42/42** (N19_DOBY removed -- `DO i = 1 TO 4 BY 2` is
now proven, re-ORACLED as R1037; +4 tested refusals N48 DO..WHILE-with-BY,
N49 DO..WHILE-only, N50 DO bound < 1, N51 DO |step| >= 3); bind **47 exact / 0
known-gap / 0 FAIL** (after repairing the regression this slice's AST change
caused -- see below); parse 498 ok / 6 parity-rejects / 0 FAIL of 504; ir 0
FAIL; rel round-trip 480/480; decmodel unchanged at 68 SCHED MATCH / 0 DIFFER,
30 VALUE-MATCH / 0 VALUE-DIFF, 8 MODEL-REFUSED (this slice adds no DEC route);
clean-build warnings 63 -> 63 with an IDENTICAL per-kind histogram, verified
against freshly built `4bc9af8` and current worktrees (`rm -rf _build` each
time); the measurement worktree was removed afterwards.
Tier-2 targeted link + console: 32 new specimens + 5 regression names (LOAN1,
DEMO, NFACT, R901, R813) -> 37 linked `.COM` byte-identical to DR and 37 raw
console transcripts byte-equal, 0 divergences (17 names in 4m43s, then 20 names
in 6m52s).  R1030 is deliberately outside the console arm: it never terminates
and prints nothing.  IFACT (non-terminating) verified by the bounded
complete-record prefix protocol: `.COM` 9600 B IDENTICAL, first 12 COMPLETE
records byte-equal, `FACTS-OK` on 6 factorial records re-derived from
`math.factorial` (records above FIXED BIN(15) range skipped, never counted as
passes).
Two harness defects were found and fixed here, not papered over:
(1) `tools/prefix_check.py --console --facts` returned from the `--console` arm
before the `--facts` block, so the arithmetic oracle never ran -- my first
IFACT "pass" was vacuous; the oracle is now a function both arms call, and both
IFACT and RFACT were re-run to prove it.  (2) Adding `Ast.Pi_fmtlist` made three
binder matches non-exhaustive and `bind_gate` fell to 13 FAIL because the
FORMAT-descriptor size fold saw one wrapper instead of N items; `flatten_items`
at all four binder item consumers restored `$S` byte parity exactly.
Implementation lines since the `4bc9af8` checkpoint, over `ocaml/`, `tools/` and
`oracle/`: +503 / -102 = **605 gross** (of which `ocaml/` alone is +366 / -51)
-- inside the ~2,000-line consultation threshold, so no mid-slice pause was
needed.

## C093 — multi-argument internal call: a DESCRIPTOR BLOCK of address constants, one shared prologue (E2E-9 slice 6)

DECPOLY was the last blocked program whose first blocker was the BINDER, not a
missing runtime routine.  Its call graph is `main -> P`, 3 fixed-decimal
formals, and the accepted `.REL` (1152 B, code=339 data=24) is now byte-exact.
The ABI law, from R2030-R2038 (arity 1..4, expression args, literal args, two
procedures, DEC formals) plus R725 and DECPOLY:

* The CALLER allocates one 2-byte POINTER CELL per argument, contiguously, at
  the tail of its own section: `*A(slot), *A(slot+2), *A(slot+4), ...`  The
  cell count per call SITE is `2 * number-of-arguments` [R2034 3-formal callee
  -> cells at A(0054)/0056/0058, R2035 4-formal -> A(004A) 8 bytes].
* Each cell's CONTENT is a link-time address constant, never a runtime store:
  `SET-LC(data, slot+2i)` + `RELOC(data, target cell)` + `SET-LC(code, ...)`
  [R2031, R2034, R2035, R2037, R2038, DECPOLY].  Because a constant operand is
  two bytes, the whole descriptor fits in 2-byte cells regardless of operand
  width -- this is what makes `1` and `1.4` both legal arguments.
* Emission is **interleaved per argument** (materialise argument i, then write
  its descriptor constant, then argument i+1), NOT batched.  R2032 proves it:
  the `RELOC(&i)` constant lands BEFORE the `j + 1` temporary is computed, the
  `RELOC(&temp)` constant AFTER `SHLD temp`.  So the per-argument descriptor
  pair must live inside the argument lowering, not in one pass at the end.
* The CALLER'S OWN value for a decimal argument is an `LXI H,*A(pool cell)`
  pair: a decimal LITERAL argument takes a 2-byte pool cell and the descriptor
  points at that cell, and in the 3-arg case the last descriptor is the caller's
  own cell (DECPOLY `*A(005A) = 5.67`, R2038 same shape).
* The CALL SITE itself is unchanged from the 1-formal case: ONE
  `LXI H,*A(descriptor-slot)` + `CALL 0000` for the whole block [R2031, R2034,
  DECPOLY @146].
* The CALLEE entry depends on ARITY:
  - arity 1 keeps the peeled dereference prologue
    `MOV E,M / INX H / MOV D,M / XCHG / SHLD <ptr cell>`;
  - arity >= 2 is one contiguous BLOCK COPY of the entire descriptor:
    `LXI D,<first ptr cell> / MVI C,2N / loop: MOV A,M / INX H / STAX D /
     INX D / DCR C / JNZ loop` [R2031 2N=4, R2034 2N=6, R2035 2N=8,
     R2037/R2038/DECPOLY].
  `DCR C` is opcode `0x0D`; the first byte-diff against DR on R2031 was exactly
  `0x05` (DCR B) vs `0x0D` (DCR C).
* Formals are passed BY REFERENCE, so writing a formal writes the caller's
  variable [R2011 runtime: `mid` received `a` and 3 became 5].  My build refuses
  stores to a formal (`store to pointer formal unproven`) because no accepted
  corpus program performs one; that refusal is a tested negative (N55).

## C094 — a FIXED DECIMAL formal is a 2-byte pointer cell read through ?DLDOP (E2E-9 slice 6)

LAW: `dcl q fixed decimal(p,s)` inside a procedure whose q is a FORMAL gives q a
2-byte cell, not the `(p+8)/9` BCD cell the same declaration gives a local
[DECPOLY: P's A(004E)/A(0050)/A(0052) are 2 B each while main's x/y/z are 6 B
each; R725 @135 the same shape at arity 1].  Reading it is
`LHLD <ptr cell>` + `MVI A,<p>` + `CALL ?DLDOP` -- i.e. the ordinary decimal
load ladder with `LXI H,<cell>` replaced by `LHLD`, which is exactly why the
same ?DLDOP primitive needs no new mode.

Corollary, RESTATED AFTER A RETRACTION (see the RETRACTED block below):
because the callee re-declares its formals (`declare (x,y,z) fixed
decimal(15,4);` inside P), the precision byte it emits is the one derived from
ITS OWN re-declaration -- and in DECPOLY both declarations are 15,4, so the
object carries `MVI A,0F` (15) on both sides: main's sites are at 0039, 004C,
005F, 006A, 0072, 0081, 0089, 009A, 00A2 and P's body at 0110, 0118, 012B,
013E (counted in the accepted .REL).  The only smaller precisions in DECPOLY
are the multiplicative-literal law at work -- `MVI A,1` for the literal `2` of
`2 * y` at 00BE, 00DA, 0123 -- and scale bytes (`4` = the target scale of
decimal(15,4)) at 0133/0143/014B.  There is no 11,2 anywhere in DECPOLY.

MODE CHECK (new refusal site, one tested negative): an argument against a FIXED
DECIMAL formal must be a decimal VARIABLE.  Passing a decimal literal or a
decimal expression (`q = g(1.5)`) has no DR sample -- DR would have to place the
literal in some cell and decide its precision -- so the compiler fails loud:
`non-variable argument against a FIXED DECIMAL formal is unproven [TBD]`
[N33, re-pinned from the old arity-1 "DECIMAL formal parameter" refusal].  All
accepted specimens pass variables (DECPOLY x/y/z, R725 a/b, R2037, R2038).

RETRACTED CLAIM (recorded so the ledger stays auditable).  When this slice was
committed (`07ff3ce`) I asserted two things that are FALSE and that the user
caught: (a) that DECPOLY's caller declares `fixed decimal(11,2)` while P
re-declares 15,4, and (b) that DECPOLY therefore prints `2` for `P(x,y,z)` and
so exhibits "DR's own semantic defect".  Both were misreadings, never checked
against the source:

* `artefacts/DECPOLY.PLI` line 11 and line 27 BOTH read
  `(x,y,z) fixed decimal(15,4)` (DR's listing of the published source confirms
  it verbatim at its lines 11 and 24-27).  The 11,2 came from LOAN1, not here.
* The `2` in the transcript is the STRING LITERAL of line 20,
  `put skip list('       2');` -- seven spaces and a two, a stray header line in
  the historical program.  The console bytes are
  `'\n       2\n      x  + 2y + z =            12.2300\n'`, and 12.2300 is
  exactly `1.4*1.4 + 2*2.3 + 5.67`.  **DR's multi-argument FIXED DECIMAL passing
  in DECPOLY is arithmetically CORRECT, and so is my build's.**

Consequence for this ledger: DECPOLY carries no defect disclaimer.  The
`2 * y` literal sites (00BE/00DA/0123, `MVI A,1`) are the C084 multiplicative
literal law operating on a decimal FORMAL read through `LHLD`, which is positive
evidence that the formal-by-reference model composes correctly with literal
precision rules -- the opposite of what I originally wrote.

## C095 — `&` in a condition materialises booleans and ANDs them; ONE skip jump (E2E-9 slice 6)

LAW: for `if A & B then S`, DR does NOT chain two conditional jumps.  Each
operand is evaluated to a boolean BYTE in A -- 0xFF for true, 0x00 for false --
by the flag trick `SUI 01 / SBB A` (NC-true => 0xFF, C-false => 0x00), the left
byte is parked with `PUSH PSW`, the right byte is combined with
`POP B / ANA B`, and the whole conjunction gets a single `JP <target>` skip jump
[DECPOLY @266 3-way `x = 0 & y = 0 & z = 0`, R2021, R2026, R2027].

Consequence for HL-hoisting: neither PUSH PSW nor POP touches HL, so the leading
address load of the NEXT operand is emitted ABOVE its `PUSH PSW`, and the
operand's value-fetch sequence ends up split across the stack push.  Observed
for both operand forms:
  fixed-bin cell-OR  `LXI H,<Y>` ... `PUSH PSW` ... `MOV A,M / INX H / ORA M`
                      [R2021, R2025];
  decimal compare    `LXI H,<X>` ... `PUSH PSW` ... `MVI A,p / CALL ?DLDOP /
                      push right / CALL ?DCMOP` [DECPOLY, R2026].
A DECIMAL operand in a conjunction also means the compare's `?DCMOP` result byte
is consumed as a flag, not as a value -- no `STA/POP` of the compare cell, and
therefore no per-operand skip jump.

Untested shapes, all refused (N52/N53): a PUT of, or a bare read of, a DECIMAL
FORMAL inside a conjunction -- the `LHLD` hoist above `PUSH PSW` has no sample.

## C096 — DR writes external names truncated to 6 characters (E2E-9 slice 6)

LAW: PROG-NAME, LINK-EXTDEF, DEF-PUBLIC and the `EXT:` symbol all carry the
FIRST SIX characters of the program name: DECPOLY -> `DECPOL`, and LONGNAME
(`dcl longprogram ...`, 9 characters) -> `LONGNA` [both .RELs byte-exact].  The
10-character program name `REPLACEP` -> `REPLAC` [R2024].  Internal procedure
names NEVER become external symbols -- DR's NTEST1/NTEST2 objects contain no
`COMPUTEVAL`/`COMPUTEA`/`COMPUTEB` entry at all, so two internals colliding on
their first six characters is legal [NTEST1/NTEST2 .REL: only the program name,
?START/?SYSPR/?SKPOP/?QICOP/?PNVOP/?QIOOP].  My binder had been emitting the
untruncated name, which is why DECPOLY could not match before this.

## C097 — `%replace` is a pass-1 TEXTUAL macro, expanded outside literals (E2E-9 slice 6)

LAW: `%replace <name> by <value>;` vanishes from the object entirely and every
later whole-identifier use of `<name>` becomes `<value>` textually [R2024:
`%replace true by '1'b;` then `do while(true);` compiles to
`JP L1 / ... / CALL ?PRPOP / JMP L0` -- the SAME fold as a literal `'1'b`
condition (Z404), with the `PUSH PSW / ... / POP B / ANA B` residue the
literal `'1'b` shape leaves [Z408]].  Because the expansion is textual, the
replacement inherits whatever context the identifier appeared in; my lexer
implements it as a source-level substitution outside string and comment
literals, and refuses (a) a `%replace` clause whose replacement is not an
integer, bit-string or short identifier token [DIOCOPY hits this refusal today],
and (b) any macro name appearing inside a literal or comment, where DR's
scanner behaviour has no sample.  Directive lines are blanked rather than
deleted so recorded line numbers stay put; `by` and `end` are not reserved.

## C098 — multiply with a dereferenced formal on the left loads the literal straight into DE (E2E-9 slice 6, defect repair)

LAW: in `a * 3` where `a` is a POINTER formal (fixed-bin), the dereference ladder
ends in `XCHG`, which already leaves the operand in DE, so DR does not perform
the usual `PUSH H / LXI D,const / POP D` rotation and instead emits
`LXI D,<const>` directly: `LHLD a / MOV A,M / INX H / MOV H,M / MOV L,A / XCHG /
LXI D,0003 / CALL ?IM22N / RET` [R2036 g1 body, byte-exact].  My build had been
rotating DE through the stack, which is dead code but not byte-equal.  This is
an optimisation the compiler applies whenever DE is already free after the left
operand -- it does NOT apply when the left operand is an ordinary cell.

GATES AFTER SLICE 6: e2e **211 byte-exact / 0 fail of 211** (was 194; +14
multi-arg/conjunction/%replace probes R2023-R2027 + R2030-R2038, +R725 which was
written in slice 4 but refused by the arity-1 binder, +LONGNAME for the 6-char
name law, +DECPOLY as the 6th corpus specimen); negative panel **51/51 refused**
(42 -> 46: N33 re-pinned from "DECIMAL formal parameter" to the mode-checked
"FIXED DECIMAL formal is unproven", +N52 PUT of a DECIMAL formal, +N53 DECIMAL
formal as a conjunction operand, +N54 fixed-bin formal passed through to another
call, +N55 store through a formal; then +5 more for the fixed-bin peephole
perimeter discovered at the end of the slice -- N56 `x + 0`, N57 `lit + lit`,
N58 `x * 2`, N59 `x * 1`, N60 `3 * x`, see C099).  Corpus sweep (all 41 DR programs through the
current build, `tools/sweep_corpus.py`): **6 EXACT / 0 DIFFERS / 35 REFUSED** --
DEMO, RFACT, DFACT, LOAN1, IFACT, DECPOLY.  Zero divergent programs: every
unaccepted corpus program stops in a named `[TBD]`, never with wrong bytes.
Tier-2 targeted link + console for this slice: 17 specimens (DECPOLY, LONGNAME,
R725, R2023-R2027, R2030-R2038) -> 17/17 linked `.COM` byte-identical to DR and
17/17 raw console transcripts byte-identical, each with a non-trivial value
printed (8, 3, 11, 6, 24, "6 / 11", 3.7000, 12.2300, 2.33, 1, and the empty
transcript of the conjunction-that-stops probes).  DECPOLY additionally:
`.COM` 1152-byte module -> byte-identical image, console byte-identical over its
REAL input script (`1.4, 2.3, 5.67` then `0,0,0`), and the simulator's own
`CPU executed 1773926 t-states` count is IDENTICAL for both images (the two
transcripts differ only in the simulator's wall-clock/clock-frequency lines).
Numeric verification: `x*x + 2*y + z` for (1.4, 2.3, 5.67) = 1.96 + 4.6 + 5.67 =
12.23, printed `12.2300` at scale 4 -- correct arithmetic, not just matching
bytes.  (Corrected after the commit: DECPOLY has NO semantic defect.  The
`2` line is the program's own string literal `put skip list('       2')` at
source line 20, and `P(x,y,z)` returns the arithmetically correct 12.2300; the
earlier "caller 11,2 / DR prints 2 / documented DR defect" wording in this block
and in C094 was a misreading and is retracted there.  See C094's RETRACTED
CLAIM block.)
THREE REAL DEFECTS were found and fixed by this slice's byte-diffing, each with
a probe that pins it: (1) `bind.ml`'s call-site fold restarted its accumulator at
`0`, silently dropping every call site but the last -- multi-arg calls lost their
descriptors; (2) `bind.ml`'s attribute lookup was case-sensitive, so the
lowercase `recursive` written in R2023/R2024 did not match, changing the SVBLK
layout; (3) an `if ... then match ...` guard in `codegen.ml` swallowed the rest
of its enclosing iteration body into the match's last arm, so the descriptor
constants disappeared for exactly the arguments the guard was meant to CHECK --
this one was caught only because the .REL stopped matching, and the fix is a
sealed `let () = if ... then begin match ... end in` binding with a comment
explaining the hazard.  A fourth hygiene repair: an assignment to a name with no
declaration raised bare `Not_found` out of `List.assoc`; it now fails loud.
A fourth specimen family came out of the `%replace` validation probes and is
banked as a DISCOVERY rather than a feature: DR strength-reduces fixed-bin
constant arithmetic (`x + 0`, `x * 1` elided; `x * 2` -> `DAD H`; `3 * x`
commuted; `3 + 2` evaluated in the DECIMAL runtime through 1-byte pool cells),
and my lowering does none of that -- see C099.  Those shapes now fail loud
(N56-N60), which is why the corpus still reports 0 DIFFERS.

Clean-build warnings 63 -> **61** (W27 unused-variable 8 -> 6 as dead bindings
went away; every other kind unchanged) -- a decrease, verified by
`rm -rf _build` rebuilds.  Implementation lines since the `4bc9af8` checkpoint,
over `ocaml/`, `tools/` and `oracle/`: +1350 / -228 = **1578 gross** -- still under the ~2,000-line consultation threshold, but
close, so the next slice starts with a user consultation.

## C099 — DR's FIXED BINARY arithmetic peephole set (E2E-9 slice 6, DISCOVERED, not implemented)

Three probes written to validate the multi-clause `%replace` lexer fix instead
exposed a route family that no accepted specimen had ever exercised: DR
strength-reduces small constant factors and summands, and it evaluates
`literal + literal` in the DECIMAL runtime.  All three specimens are DR goldens
in `golden/e2e12c/` (P044, R2045, R2046, compiled with `$L$C$D` so the listing
carries the code trace).  **None is a gate positive: my build now refuses each
shape (N56-N60) rather than emitting the wrong bytes.**

P044 lines 3-6, verbatim from DR's listing:

    x = 2 + 4;   LXI H,*S(0000) ; MVI A,01 ; CALL ?DLDOP
                 LXI H,*S(0001) ; MVI A,01 ; CALL ?DLDOP
                 CALL ?DADOP ; CALL ?QDI15 ; SHLD X A(0002)
    x = x * 1;   LHLD X A(0002) ; SHLD X A(0002)
    x = x + 0;   LHLD X A(0002) ; SHLD X A(0002)
    x = 3 * x;   LHLD X A(0002) ; LXI D,0003 ; CALL ?IM22N ; SHLD X A(0002)

R2046 line 11, `n = n * step` where `%replace step by 2`:

    LHLD n A(0000) ; DAD H ; SHLD n A(0000)

Laws read off this evidence, stated only as far as they go:

1. `left + right` where BOTH are integer literals is NOT folded: DR allocates
   one 1-digit (1-byte) decimal pool cell per literal, pushes both through
   `?DLDOP` with `MVI A,01`, adds with `?DADOP`, and converts the decimal
   result to binary with `?QDI15` before the store.  The DATA AREA of R2045 is
   6 bytes for `dcl i fixed; dcl r fixed;` + two 1-byte literal cells -- four
   bytes of variables, two of constants [R2045, P044].
2. `x - <literal>` DOES take the immediate path: `j = 0 - 7` [N301] and
   `e = 0 - 2` [N306] are byte-exact against my folding.  So rule 1 is
   ADD-specific on the samples available; whether `7 - 2` folds is UNSAMPLED
   (both samples have 0 as the left operand).
3. `x * 1` and `x + 0` elide to a load/store pair of the same cell.
4. `x * 2` becomes `DAD H`.  Together with the ±1/±2 INX/DCX ladder of C091
   this says DR recognises a small family of constant multiplicative/additive
   identities and never calls the runtime for them.
5. `3 * x` (literal left, value right) commutes: DR loads the VARIABLE into HL
   and the literal into DE with `LXI D,<const>`, no stack rotation.  This is the
   general form of C098 -- C098's pointer-formal case was a special instance.

Implementation consequence: my `lower_hl` Add/Mul arms gained three narrow
guards (`fp_add_guard`, `fp_mul_guard`) that fail loud with the DR trace quoted
in the message.  The guard is deliberately narrow -- it fires only on the shapes
DR is known to rewrite, so `x * 3`, `x / 2`, var-op-var and every accepted
specimen keep their existing byte-exact paths (gate went 211/211 with the
guards in place after one over-broad first attempt that broke N301/N306, which
is itself recorded above as evidence for rule 2).

Next slice, in order: implement rules 1, 3, 4, 5 (each needs 1-2 more probes --
`x - y` with literals, `x * 4`, `1 * x`, `x + 0` inside a condition, pool-cell
ordering for two 1-digit decimal literals), then un-refuse N56-N60 and register
P044/R2043/R2045/R2046 as positives.

## C100 — DR FLOAT BINARY(24) representation: the 4-byte format (E2E-10 step 1, RESEARCH ONLY)

Nothing in this claim or C101 changed the compiler: `git diff --stat -- ocaml/
tools/ oracle/` at the previous commit was empty and step 1 touched only
`tools/floatmodel.py`, `e13src/` probe sources and `golden/e2e13/` oracle
output.  Evidence is 20 DR specimens compiled with `$L$C$D` (code traces plus
`.REL`), including two corpus programs (FLTPOLY, FFACT) and eighteen probes
R3001-R3025.  **`tools/floatmodel.py` reproduces 60/60 float-literal pool cells
byte-exactly with 0 mismatches, plus 43 internal assertions**; three further
pool cells are correctly excluded as STRING literals (FLTPOLY's `'       2'`
shares the literal pool: `20 20 20 20`, `'Type'`: `54 79 70 65`).

FORMAT, all bytes DIRECTLY OBSERVED:

    byte 0  fraction bits  7..0     (little-endian)
    byte 1  fraction bits 15..8
    byte 2  bits 6..0 = fraction bits 22..16 ; bit 7 = SIGN (set = negative)
    byte 3  characteristic: value = 2**(byte3 - 129)

    value = (-1)^sign * (1 + fraction/2**23) * 2**(byte3 - 129)

* Implied leading one, 23 stored fraction bits -- 24 significant bits, which is
  exactly what `float binary(24)` names.  Byte order is little-endian across ALL
  THREE fraction bytes: `1.00001525878906` (1+2**-16) -> `80 00 00 81` puts the
  bit in byte 0, `1.00000011920929` (1+2**-23) -> `01 00 00 81` also byte 0, and
  `0.1` -> `cd cc 4c 7d` exercises bytes 0,1,2 simultaneously.  This resolves the
  "order of the two low fraction bytes is a guess" caveat I recorded in the
  E2E-10 assessment (`e2e10-float-perimeter-assessment.md` 2.1): it is no longer
  a guess.  It is NOT IEEE-754 (`struct.unpack('<f', ...)` yields garbage).
* Sign lives in the fraction's top byte, not the exponent byte: `1.75` ->
  `00 00 60 81`, `-1.75` -> `00 00 e0 81`; `-127.5` -> `00 00 ff 87` shows bit 7
  set while bits 6..0 stay 0x7F.  [R3018]
* ZERO is the all-four-bytes-zero pattern; exponent byte 0 is a legal NORMAL
  characteristic (`2E-39` -> `7e 39 2e 00` = 1.361 * 2**-129 [R3023]), so zero is
  a special case, not "exp 0".  `0`, `0.0` and `-0.0` all collapse to the single
  cell `00 00 00 00` [R3007]: DR has NO negative zero.  Side effect worth
  recording: 1.0 * 2**-129 would also be `00 00 00 00`, so the encoding is
  technically ambiguous at that one magnitude -- unreachable from any decimal
  literal DR accepts, and harmless, but it means "exp byte 0" alone must never be
  used to test zero.
* Magnitude range: exponent byte 0..255, i.e. |v| in [2**-129, 2**127).  DR
  rejects anything outside it in PASS 2 with the diagnostic `CONVERT` and
  produces NO .REL: rejected -- `1E39`, `1.8E38` (> 2**127), `1E-45`, `1E-60`
  (< 2**-129); accepted -- `1E38` -> `99 76 16 ff` (byte 255), `1.6E38`,
  `3E-39` (byte 1), `2E-39` (byte 0), `1E-20` -> `08 e5 3c 3e` (byte 62).
  Boundary behaviour is therefore a COMPILE-TIME property my future float
  support must reproduce (refuse, not silently saturate).
* No subnormals were observed at any magnitude in range.

## C101 — DR's literal-to-float conversion: rounding, range check, pool rules (E2E-10 step 1)

* ROUNDING: nearest, **TIES AWAY FROM ZERO** -- the same tie direction as the
  DECIMAL ROUND law C087, arrived at independently.  Pinned by EXACT integer
  ties (a tie is only a tie when the literal is exact, so I used integers at the
  mantissa-capacity boundary, where my first attempt with 14-digit decimals was
  NOT a tie at all -- 1.00000005960464 is strictly below 1+2**-25 and rounds down
  for a different reason):

  | literal | exact position | DR bytes | DR value |
  |---|---|---|---|
  | `16777217` | half-way between 16777216 and 16777218 | `01 00 00 99` | 16777218 (UP) |
  | `16777219` | half-way between 16777218 and 16777220 | `02 00 00 99` | 16777220 (UP) |
  | `-16777217` | half-way | `01 00 80 99` | -16777218 (away from 0) |
  | `-16777219` | half-way | `02 00 80 99` | -16777220 (away from 0) |
  | `50331649` | quarter ulp | `00 00 40 9a` | 50331648 (nearest) |

  Round-half-to-EVEN is EXCLUDED: it would have given 16777216 and -16777216.
  "Toward +infinity" is EXCLUDED: the negative ties moved away from zero.
* The decimal literal is taken to its EXACT value before rounding -- a single
  `nearest/exact` model reproduces all 60 cells, including `0.1` (`.6` of an
  ulp -> up), `12345.678`, `3E7`, `1E-20`.  No intermediate 9-digit decimal
  rounding was needed to fit any sample, and DR reads at least 16 significant
  digits (`1.0000000596046448` rounded UP, `1.00000005960464` rounded DOWN --
  both correct only if the extra digits are seen) [R3006, R3021].
* Pool rules, observed and consistent with the DEC rules of C084/C090:
  float literal cells occupy the data area BEFORE the variables (R3013: cell at
  A(0000), f at A(0004), g at A(0008); R3001: cells 0/4, vars 8/C), cells are
  allocated in FIRST-USE order, and cells are DEDUPLICATED by identical bytes
  (R3007's four zero literals share one cell; R3010's `16777217` and
  `16777218` share one; R3012's `1.00000005960464` and `1.00000004470348` share
  one; R3013's `float binary(14)` and `float binary(24)` share the `1.5` cell).
* Every float VARIABLE occupies exactly 4 bytes, regardless of declared
  precision: `dcl f float binary(14)` and `dcl g float binary(24)` are 4 bytes
  apart [R3013], and `float` == `float binary(24)` [R3001].  STRIPPED
  ARITHMETIC PRECISION for binary(14) is NOT established -- see unresolved.
* Literal -> cell store form (compile-time layout only): the literal address and
  the variable address are both materialised and handed to the runtime --
  `LXI H,*S(cell) / PUSH H / LXI H,<var> / POP D / CALL ?FX44M` [R3001, R3007,
  R3013].  Float-to-float variable copy uses the same `?FX44M` with two
  variable addresses; PUT of a variable is `LXI H,<var> / MVI A,0E / CALL
  ?QFCMS` (width byte is the CONSTANT 14, not a precision) and PUT of a stack
  value (e.g. a call result) is `?QFCSS`.

UNRESOLVED AFTER STEP 1 (deliberately not guessed):

1. `float binary(14)`/long float: storage is 4 bytes, but is the *computed*
   precision truncated (which would change runtime digits and console bytes)?
   Untested; my planned subset is binary(24)-only with a guard.
2. Whether DR's runtime arithmetic (`?FA44M`, `?FM44M`, ...) uses the same tie
   direction as its literal converter.  Irrelevant for `.REL` byte identity;
   relevant only to console equality, which comes from linking the same PLILIB.
3. The operand-mode suffix rule (`?FA44M` vs `?FA44S` vs `?FA44L`, `?FD44R`,
   `?FS44M`) -- the genuinely new lowering law, and the expected centre of
   step 2/3 work.  Step 1 says nothing about it.
   **RESOLVED in C103** (step 2, probes R3030-R3036, R3042-R3044, R3046,
   R3051-R3054).  The answer was NOT the structural cell-vs-stack rule this
   note assumed; a negation and a conversion are separate operand modes.
4. Subnormals: none observed; whether the runtime ever produces one is unknown.
5. The exp-byte-0/zero encoding ambiguity noted above: unreachable from source,
   but recorded so nobody "fixes" it later.

## C102 — PL/I-80 arithmetic-exception ON-units are TERMINAL; the tutorial dialect difference (LEARN validation, 2026-10-19)

* Evidence: original DR PL/I-80 1.4 + LINK 1.31 on `LEARN.PLI` (the
  learnxinyminutes PL/I-80 tutorial program, retrieved byte-identical from
  `cyrilmhansen/learnxinyminutes-docs@b2d6f16`, saved as CP/M text: CRLF + `^Z`,
  program characters untouched).  Compiler reported `NO ERROR(S) IN PASS 1` /
  `PASS 2`, `CODE SIZE = 041A`, `DATA AREA = 012B`; LINK reported no
  diagnostics (`CODE SIZE 30B9`, `DATA SIZE 045B`, `COMMON SIZE 0144`); the
  `.COM` ran and printed every statement's expected output, then
  `ZERO DIVIDE (0)` / `Traceback: 0498` and returned to `D>`.
  Full transcripts: `golden/learn/`, note `spec/notes/learn-tutorial-dri-validation.md`.
* The abort is **documented compiler behavior, not a defect**.  Applications
  Guide §7.5 (printed page 65, local scan, checksum verified) states verbatim:
  *"Note, however, that all arithmetic faults are considered terminal. That is,
  if an ON condition is set for an arithmetic exception, then the on-body must
  contain a transfer to a global label. Otherwise, the program is terminated
  upon return from the ON unit."*
* The tutorial's `ON ZERODIVIDE PUT SKIP LIST(...);` has no `GO TO`, so
  termination on return from the ON-unit is REQUIRED behavior for PL/I-80.
  Iron Spring PL/I 1.4.1 resumes after the handler instead, on the same source.
  That is a **language-semantics dialect difference** between the two
  implementations, and the divergence was predicted by DR documentation before
  the run rather than reverse-engineered from the crash.
* Consequence for this reimplementation, if `ON`/arithmetic exceptions are ever
  implemented: reproduce the TERMINAL semantics (return from an arithmetic
  exception ON-unit ends the program).  `golden/learn/LEARN.PLI` is the
  standing specimen for that rule; it is NOT part of the 41-program DR corpus
  and does not count toward the corpus score.
* Current build refuses the specimen fail-loud at the first unsupported
  declaration kind: `declared variable kind not in supported subset [TBD]:
  BIT(1)`, ahead of its `POINTER`/`BASED`, `VARYING`, `FILE`, `ON`/`SIGNAL`,
  array and `FLOAT` members.

## C103 — DR FLOAT operand-mode suffix law: L/R/M/S is chosen by accumulator SLOT, and three computed kinds are distinct (E2E-10 step 2)

For a FLOAT binary operator X (`?FX44?`, X in A/S/M/D for + - * /) the suffix is
determined by where each operand physically is, and `L`/`R` say which SIDE the
accumulator is on: **L = accumulator value OP HL**, **R = HL OP accumulator**.

| left operand | right operand | DR suffix | samples |
|---|---|---|---|
| cell | cell | `M` (HL, then `PUSH H`/`POP D`) | R3030-R3033, R3036 `a * 2`, R3037 |
| computed | cell | `L` | R3034 `a*b + c`, R3035 `-a + b`, R3036 `i + a`/`i * a`/`i / a`, R3042 `a/b * c`, R3043 `(a-b)/c`, R3046 `-a * b` |
| cell | computed **binary result** | `L` if op is `+` or `*`; `R` if `-` or `/` | R3034 `a + b*c` -> `A44L`, R3051 `a*(b+c)` -> `M44L`, R3052 -> `A44L`; R3042 `a - b*c` -> `S44R`, R3043 `a/(b*c)` -> `D44R`, R3053 -> `D44R` |
| cell | computed **?QI15F conversion** | `R` | R3036 `a + i` -> `A44R`, `a * i` -> `M44R`, `a / i` -> `D44R` |
| cell | computed **negation** | `R` | R3035 `a + -b` -> `A44R`, R3046 `a * -b` -> `M44R` |
| computed | computed | `S` | R3034 `(a+b)*(a-b)` -> `M44S`, `a*b + c*a` -> `A44S`, R3046 `-(a)*-(b)` -> `M44S`, R3044 `i + j` |

* The step-1 prediction that this was a two-way cell-vs-stack rule is
  **refuted**: three kinds of accumulator value behave differently.  R3046 is
  the decisive specimen -- `-a * b` -> `?FM44L`, `a * -b` -> `?FM44R`,
  `-(a) * -(b)` -> `?FM44S` in one program, which no structural rule over
  {cell, non-cell} can express.
* DR exchanges the operands of a COMMUTATIVE op at no cost, and demonstrably
  does so when the right operand is itself a binary result [R3034, R3051,
  R3052]; it keeps the written order around a negation [R3035, R3046] or a
  conversion [R3036], and must for `-` and `/` [R3042, R3043, R3053].  Where
  order is free, the observed choice is what pins the rule -- the semantic
  result would be identical, so byte identity is the only witness.
* `?FN40M` does NOT write the addressed cell.  R3046 reads `a` in `d1 = -a * b`
  and again in `d2 = a * -b`; an in-place negate would corrupt the variable, so
  the DR evidence itself rules that reading out.  `?FN40M`/`?FN40S` produce into
  the accumulator.
* Negative LITERALS never take `?FN40`: the sign is folded into the pool cell at
  compile time [R3007, R3018, R3020], consistent with C101/C100.
* ~~Still refused, not inferred (no DR sample): mixing a plain-cell operand with
  a pointer-formal operand in one op.~~  **CORRECTED in step 3** — see C103a.
  The cell/formal distinction does not exist for suffix selection at all; the
  real cut is address-mode vs computed, and a pointer formal is address-mode.
* Implemented state (step 2): 29 of 36 float probes byte-identical.  Step 3
  supersedes it: see C103a and the note `e2e10-step3-float-conditions.md`.

## C103a — the suffix law's real cut is ADDRESS-MODE vs COMPUTED; a FLOAT pointer formal is address-mode (E2E-10 step 3)

Step 2 recorded `cell` vs `computed` and refused the mix as unsampled.  Ten new
byte-identical probes refute both the refusal and the terminology: an operand is
**address-mode** when DR can push a pointer to its value cheaply, which covers a
plain variable cell (`LXI H,*S`), a float literal pool cell, **and** a FLOAT
pointer formal (`LHLD ptr`); it is **computed** when the value must be produced
into the accumulator (`?QI15F` conversion, `?FN40` negation, an arithmetic
result).  Address-mode pairs take `M` in WRITTEN order with no commute —
there is nothing to materialise:

| shape | DR code | sample |
|---|---|---|
| literal cell * formal | `LXI H,*S / PUSH H / LHLD Y / POP D / ?FM44M` | R3082 |
| formal * literal cell | `LHLD Y / PUSH H / LXI H,*S / POP D / ?FM44M` | R3083 |
| formal + literal cell | `?FA44M`, written order | R3084 |
| formal * formal | `LHLD X / PUSH H / LHLD Y / POP D / ?FM44M` | R3086 |
| `(x*x + 2*y) + z` (z formal) | `?FA44S`, then `LHLD Z / ?FA44L` | R3087 |
| `z + x*y` (formal left, binary right) | x*y first, `LHLD Z / ?FA44L` (commuted) | R3089 |
| `z / (x+y)` | x+y first, `LHLD Z / ?FD44R` (order kept) | R3090 |

The commute rule inside the computed half is unchanged: DR exchanges a
commutative operator's operands only when the right side is itself a binary
result, and keeps the written order around a negation or a conversion.  R3005,
the probe step 2 read as a mixed pair, was never one.  `Fderef` still earns its
place in the mode type because it selects the LOAD INSTRUCTION; it must never
select the suffix.  Implemented state after step 3: 111 float probes
byte-identical, 0 differing, 17 refused (named perimeter members).

## C104 — DR FLOAT relation lowering in a condition; `<>` is not accepted by DR itself (E2E-10 step 3)

Every sampled float relation is `?FC44M` on the two operand addresses followed by
exactly one conditional jump; the push ORDER is what makes the wanted sign come
out positive or negative:

| condition | first pushed | jump | sample |
|---|---|---|---|
| `a > b` | right (b) | `JP` | R3070 (also R3037's shape, whose jump guards the ELSE branch, so `a > b` on floats is really testing `>=` semantics through JP) |
| `a < b` | left (a) | `JP` | R3071 |
| `a >= b` | left (a) | `JM` | R3072 |
| `a <= b` | right (b) | `JM` | R3073 |
| `a = b` | left (a) | `JNZ` (skip) | R3074 — `?FC44M` leaves `A = 0` when equal |
| `a <> b` | — | — | R3075: **DR rejects it**.  PASS 1 clean, `1 ERROR(S) IN PASS 2`, no `.REL` emitted.  DEC `<>` gets JZ [C085]; the float reader offers no such form, so there is nothing to reproduce and the lowering refuses. |

Two consequences that only the bytes showed:

* A comparison LITERAL (`a = 0`, `a > 2.5`) becomes a 4-byte float POOL cell
  (written-order `M`), never a runtime `?QI15F`/`?QX8F4` conversion [R3076,
  R3077].  So a condition consumes pool space, and the pool prescan has to walk
  conditions — otherwise the cell collides with address 0 and every later data
  address shifts silently (real bug, fixed).
* Mixed cell/formal comparisons behave like address-mode pairs [R3079:
  `LHLD X / PUSH H / LHLD Y / POP D / ?FC44M / JP`], per C103a.

## C105 — FLOAT operand of an `&` conjunction: PSW-accumulated booleans, with `>` contributing its raw compare byte (E2E-10 step 3)

`if x=0 & y=0 & z=0` (FLTPOLY) lowers exactly like the DEC conjunction [R2026]:
first operand's boolean byte into A via `?FC44M / SUI 01 / SBB A`; each later
operand's FIRST ADDRESS LOAD hoisted above `PUSH PSW`, then `PUSH H`, then its
own compare+materialisation; each later operand combined by `POP B / ANA B`;
terminal `JP <skip>` on the ANDed sign.  R3078 pins the asymmetry that a purely
structural rule would miss: when the operand is `>` rather than `=`, DR emits
the compare and then NOTHING — `?FC44M`'s signed-comparison byte already has the
sign bit set exactly when "greater" holds, so the boolean needs no
materialisation, and the conjunction's terminal `JP` reads the AND's sign.
`<`, `>=`, `<=` in a conjunction and any non-`=` relation on the RIGHT side of
one have no DR sample and refuse.

## C106 — a deduplicating callee's declared formal cell occupies NO storage; a RECURSIVE callee's does (E2E-10 step 3 + 3b)

The law is about the *dedup* relation, not the declaration type.  When a
procedure's formal dcl dedups onto its 2-byte pointer cell, the declared cell
consumes zero bytes; a local declared after the formals sits immediately after
the pointer cells.  Six probes bracket it by formal count, both types:

```
FLOAT, non-recursive  1/2/3 formals   DR local Q = A(0014)/A(0018)/A(001C)
                                      a charging model says 0018/0020/0028 (+4/+8/+12)
FIXED, non-recursive  1/2/3 formals   DR local Q = A(000C)/A(0010)/A(0014)
                                      a charging model says 000E/0012/0016 (+2/+4/+6)
```

with the pointer cells themselves at DR's address in every case [R3095, R3096,
R3093, R3094, R3101, R3102].  The float formal's address IS its pointer cell,
which is exactly why the float lowering reads it with `LHLD`.

The exception is the written RECURSIVE attribute, where the declared cell IS the
shadow value cell and really is allocated — `P401`, `NFACT` and `R3104`
(`p: procedure(x) returns(fixed) recursive; dcl (x,q) fixed;` with `q` after `x`)
are byte-exact only when it is charged, and turning the rule off for them shifts
addresses.  So `dedup` (which requires `not attrf`) and "consumes no storage" are
the same condition, and `bind.ml`'s existing note about the shadow cell was
pointing at this all along.

Two further facts fell out of the same shape:

* A RECURSIVE callee with a FLOAT formal additionally COPIES the caller's value
  into that declared cell at body entry — R3103's `$C` listing shows
  `LXI H,X A(0010) / PUSH H / LHLD X A(000E) / XCHG / POP H / LXI B,0004 / CALL
  <copy>`.  Every DATA address matches mine and only this prologue is missing,
  which is the most dangerous kind of near-miss, so the case refuses (N71).
* `fixed bin(31)` is DR `NOT IMP` even for a procedure-local declaration (R3094's
  first draft got `NOT IMP` on five separate lines), re-confirming C079 outside
  the main block.

Process error worth keeping: while deciding between "type-discriminated" and
"recursion-discriminated", an ad-hoc shell loop compared `P401`/`NFACT` against a
golden PATH THAT DID NOT EXIST, reported `differs`, and nearly made me abandon the
correct unified rule (and add a refusal for a shape DR has since shown to be
simple).  The real gate — which resolves paths itself — said 286/286 the whole
time.  Ad-hoc comparison loops must take their paths from the gate, not from a
`find | head -1`.

## C107 — numeric GET into a FLOAT variable goes through the DECIMAL reader (E2E-10 step 3)

`get list(x)` for a float is `?GNVOP` / `JP` (skip) then `?QCXOP` (clean the
decimal) / `?QX8F4` (decimal → 4-byte float into the accumulator) / `LXI H,var`
/ `?FX44S` [R3065 one item, R3066 mixed float+fixed list, R3004 two items,
R3100 minimal].  No `MVI A/B` width or scale operands appear anywhere in the
tail, unlike the DEC branch's `?QCDOP`/`?DSTOP` pair [LOAN1, R906].  Value-model
consequence: a runtime-read float does not pass through C101's literal conversion
and its rounding law must not be assumed identical to a literal's.

## C108 — PL/I-80 V1.4 refuses FIXED precision above 15; my build must too (E2E-11 step 0)

One specimen per precision, `fixed bin(p)` with an assignment and a PUT, plus the
decimal equivalent [golden/e2e11f: E1415..E1432, E15D09..E15D31]:

```
FIXED BINARY :  p <= 15 compiles      p = 16,17,23,24,30,31,32 -> "NOT IMP", NO .REL
FIXED DECIMAL:  p <= 15 compiles      p = 16,31                -> "NOT IMP", NO .REL
```

`NOT IMP` is fatal: DR emits no relocatable output at all.  **This restates a
limit PERIMETER already recorded from a "P068 L-series sweep", but that sweep's
artefacts are gone** — every `golden/probe2*/P068*/` directory holds only a
`dir.txt`, with no listing and no `.REL`, and none is gate-referenced.  So the
claim had decayed to an assertion; E14xx/E15Dxx re-establish it from primary
evidence, and the enforcement gap below is what actually changed.  Nothing in the corpus
or in any of the 289 goldens declares FIXED above 15 (the only >15 precisions in
existence here are `FLOAT BINARY(24)`, a different type), so this was not a
regression — it was a latent false capability, since my compiler accepted
`bin(31)`/`dec(31)` and would have emitted bytes for programs DR refuses
outright, with no golden possible to contradict it.  Enforced at the earliest
point the precision is known (`bind.check_fixed_prec`), unconditionally, so no
use-path can slip past it; the earlier codegen-arm version only fired on some
paths.  Pinned by N24 (`bin(16)`), N27 (`dec(20)`), N72 (`bin(31)`), N73
(`dec(16)`).

**Storage ladder, re-derived live** [E19A, golden/e2e11k — 30 declarations of
`fixed bin(1..15)` and `fixed dec(1..15)`, DR's own store offsets]:
`FIXED BINARY`: p≤7 → 1 byte (stored with `STA`), 8≤p≤15 → 2 bytes (`SHLD`) =
`(p+8)/8`.  `FIXED DECIMAL`: 1→1, 2-3→2, 4-5→3, 6-7→4, 8-9→5, 10-11→6,
12-13→7, 14-15→8 = `(p+2)/2`.  The previous citation for the binary ladder was
`P063A`, whose golden directory holds a `.PLI` entry but **no `.REL`** and whose
source no longer exists; its `16/17→3, 24→4, 32→5` rows described precisions DR
cannot compile and were extrapolation.  Values above 15 bits are therefore
unclaimable, not merely unprobed.

## C109 — `ON condition(file)` lowers to `?ONCOP` + an inline handler terminated by `RET` (E2E-11 step 1)

```
on endfile(sysin) <unit>;
   LXI  H,<file control block>      ; relocated SYSIN / INF symbol
   MVI  A,05                        ; condition number 5 = ENDFILE
   CALL ?ONCOP
   JMP  <past the unit>             ; operand patched via the listing's '==== '
<unit body, emitted inline>
   RET                              ; the ON-unit IS a subroutine
```

Identical for a simple-statement body [E11A] and a `BEGIN`-block body
[E11C, E17A], so the body's form is irrelevant to the registration.

**RETRACTION (step 2).** I wrote here that "the registration costs 6 bytes of
data area", decomposing E11C's `DATA AREA = 0009` as 6 (ON) + 1 (bit flag) + 2
(fixed).  That was a coincidence, not a measurement.  E11C's actual nine bytes are
`00` (the `bit(1) static initial('0'b)` cell) | `58 3d` = "X=" | `44 4f 4e 45` =
"DONE" | 2 bytes for `x` — i.e. 1 static + 6 LITERAL POOL + 2 automatic, and the
"6" is two string literals I had not looked up.  `ON ENDFILE` costs ZERO data
bytes: FLTPOLY2 is byte-exact with no allocation for it, and had I reserved six
bytes on the strength of this claim every FILE program would have come out wrong.
Lesson kept: a decomposition that happens to sum correctly is not evidence — the
bytes have to be identified individually.

Also corrected here: the control block the `LXI H,<file>` operand points at is NOT
PLILIB's object at 0x0290 and not "in the program's own data area" for named files.
It is a per-variable **named COMMON group** [C120], identical in shape for SYSIN and
for a user stream.  What 0x0290 actually is, is the *input descriptor* the GET's
`LXI D,0290` loads — a different object, as the relocations make clear (`LXI D,0290`
carries no relocation at all; `LXI H,SYSIN` carries a COMMON-segment one).

## C110 — ENDFILE semantics: handler runs once, the GET then COMPLETES unassigned, control goes to the NEXT statement (E2E-11 step 1)

Established by observation, deliberately not by extending C102, and separately
for a named file and for SYSIN.  Three GETs' worth of data in the staged file,
FOUR GETs in the program, so endfile is actually reached:

```
E18A  no ON unit            X1=7 X2=8 X3=9 / END OF FILE (1), File: INF=INF.DAT
                            / Traceback ...            -> UNHANDLED ENDFILE IS TERMINAL
E18B  ON unit = put only    X1=7 X2=8 X3=9 HANDLED X4=9 END
                            -> handler once, GET completes WITHOUT assigning,
                               next statement runs, NO re-entry, NO termination
E17A  ON unit sets a flag   X=7 X=8 X=9 X=9 DONE       -> same, seen through a loop
E11A  SYSIN, ON unit        ^Z -> HANDLED A=0 AFTER    -> identical for SYSIN
E11C  SYSIN, flag+loop      7→X=7, 8→X=8, ^Z→X=8 DONE -> identical for SYSIN
```

Consequences that are load-bearing for implementation:

* The terminal outcome agrees with C102's arithmetic conditions, but the
  **diagnostic is file-specific** (`END OF FILE (1), File: <variable>=<resolved
  name>`), so it is not C102's path and must not be implemented as such.
* An interrupted GET **returns normally** — it does not re-execute and does not
  abandon the enclosing statement's successors.  My GET lowering must fall
  through to the next statement with the list items untouched; a re-entry or
  skip-the-PUT shape can easily produce byte-matching code with wrong behaviour.
* **Unassigned locals read as zero** (`A=0` in E11A), consistent with the
  zero-filled data area already assumed by pool/static layout.
* Direct corpus consequence: `FLTPOLY2`'s `do while(efile = '0'b)` loop exits
  correctly **and prints its final value twice** [E11C is that shape].  Any
  FLTPOLY2 acceptance must reproduce the duplicate, not "fix" it.
* `do while(cond)` tests as `LDA cell / ANI 80 / JNZ <exit>` — DR's
  negated-condition, matching the pattern already in use [E11C, E17A].

## C111 — SYSIN GET, named-file GET and `open` sequences (E2E-11 step 1)

```
get list(x);            (SYSIN)      get file(inf) list(x);  (named stream)
   LXI D,0290  SYSIN cb                LXI H,INF       this file's own cb
   LXI B,0000  options                 LXI D,0690      its attribute block
   CALL ?SYSIN                         LXI B,0000      options
   CALL ?GNVOP                         CALL ?SIOOP     stream io op
   JP <fail>                           CALL ?GNVOP     <-- identical below
   CALL ?QCIOP                         JP <fail>
   SHLD x                              CALL ?QCIOP / SHLD x / <fail>: CALL ?QIOOP
```

The DEC reader from `?GNVOP` down is shared with the plain numeric GET of E2E-7A
slice 4 [R901-R917], so a file GET differs only in how the stream is attached
(E11E, E17A).  `open file(inf) stream title('$1.$1')` = `?SLCTS` on the title
literal (`LXI H,* S(n) / MVI A,len / CALL ?SLCTS`), then a fixed push-block
(`MOV B,A / PUSH B / INX SP / LXI H,0E90 / PUSH H` ×6), then `LXI H,INF` +
**`CALL ?OIOOP`** [E17A].  `?OIOOP`/`?SIOOP`/`?SYSIN`/`?ONCOP` are PLILIB
externals, i.e. name-resolution targets, not code I generate.

## C112 — `BIT(1)` is one byte, high-bit justified; `STATIC INITIAL` is independent of FILE (E2E-11 step 1)

`E11D` uses `bit(1)`, `static initial('0'b)`, bit literals and bit comparisons,
and **no FILE, stream or ON construct at all**; DR compiles it, LINK produces a
`.COM`, and the program runs to `N=         3`, which requires that `f` was
`'0'b` at entry (branch taken), `g = '1'b` worked, and `f = '1'b` did not fire.
So these are their own small capability, not part of the FILE work [E11D, and
the same lowering inside E11C/E17A].

```
dcl efile bit(1) static initial('0'b);   ; 1 byte, value 0x00
efile = '1'b;      LXI H,EOFLAG S(0000) / MVI M,80      ; '1'b -> 0x80
efile = '0'b       LDA  EOFLAG S(0000) / ANI 80 / JNZ…  ; test = mask bit 7
```

Assignment goes through `LXI H,cell` + `MVI M,80`; testing goes through
`LDA cell` + `ANI 80`.  Whether DR uses `MVI M` versus `MVI A/STA` in other
contexts (arrays, structures, subscripted or wide `bit(n)`, n>1) is unprobed —
`bit(16)` remains unsupported and unclaimed.

## C113 — harness: real SYSIN EOF, file staging and output-file capture (E2E-11 step 1)

* **Console EOF must be `^Z` + CR.**  A bare `\x1a` in a session script is eaten
  by CP/M's own command-line read; the program then blocks on CONIN and the run
  times out having produced nothing — indistinguishable from a silent program.
  With `\x1a\r`, E11A/E11C behave as designed.  No prior specimen establishes
  that a bare-`\x1a` run ever terminated cleanly (`R907`, my only immediate-EOF
  GET probe, exists in the compile tier only).
* **Staging/capture already existed in `cpmwork` (`import_local`, `export`,
  `cpmtools`); the run stage simply never used them.**  Added: `STAGE_IN`,
  `EXPORT_OUT` (with a directory dump on a failed capture, so absence is never
  mistaken for no output), and `ARGS` for command tails, plus a transcript
  anchor that tolerates a tail — without it every tailed run wrote an empty
  output file.
* **Stream-file naming is DR's, not PL/I's.**  `title('E16IN DAT')` is ignored:
  DR builds the FCB from the FILE **variable's own name** and reports
  `File: INF=NUL`.  `title('$1.$1')` reads the command tail but splits it at the
  first **space** into name/extension, so `E17D OUT DAT` created a file literally
  named `out`, and a single **dotted** token (`E17A INF.DAT`) is required — then
  DR reports `File: INF=INF.DAT`.
* **Output files are record-padded.**  E17D's captured `OUT.DAT` is 128 bytes:
  `'HELLO'    42` + `^Z` fill.  List-directed output quotes character constants
  and right-justifies numerics; the length is a whole record, not the payload.
  Byte-exact output-DATA comparison is therefore a distinct evidence class from
  `.REL` parity and from console-transcript matching, with its own rules.

## C114 — DR's data area is ONE block ordered [statics][literal pool][automatics] (E2E-11 step 1a design)

DR's listing prints two relocation *classes* — `NAME S(off)` for statics and pool
literals, `NAME A(off)` for automatics — which invites the reading that there are
two sections.  There is not.  Three specimens decompose `DATA AREA` exactly:

```
E11D  F  S(0000)  'N=' S(0001..0002)  G A(0003)  N A(0004..0005)   DATA = 0006
E20D  F  S(0000)  'N=' S(0001..0002)  N A(0003..0004)              DATA = 0005
E20E  s1 S(0000) s2 S(0001) 'W=' S(0002..0003) w1 A(0004..0005)
      a1 A(0006) w2 A(0007..0008)                                  DATA = 0009
```

So one contiguous block: **static cells first (declaration order), then the
string/decimal literal pool, then the automatics**, with S and A indexing the
same addresses.  `S`/`A` are naming/relocation classes, not separate storage.

Implementation consequence, and why this is a layout change rather than an
architectural fork: my model already places the pool at data offset 0 and
automatics above it, and already reproduces `* S(off)` pool references
byte-exactly.  Adding STATIC therefore means *only* reserving the static bytes
below the pool and shifting the pool base — the same `span`/`rows` shifting
mechanism proven for float formals in E2E-10 step 3b — plus emitting the
initialiser bytes into the data segment.

Related bit(1) facts from the same specimens [E20A, E20B, E20D, E20E, C112]:
store `'1'b` = `MVI M,80`, store `'0'b` = `MVI M,00`; test `= '0'b` =
`LDA c / ANI 80 / JNZ skip`; test `= '1'b` = `LDA c / ANI 80 / SUI 80 / JNZ skip`
(the `SUI 80` appears only for the `'1'b` comparison, mirroring the fixed-bin
zero-test shape).  `INITIAL` on a bit string **requires** `STATIC`: DR's pass 2
reports `NOT STATIC` and emits no `.REL` for `dcl f bit(1) initial('1'b);`
[E20C], so that form must refuse, not degrade.

## C115 — STATIC cells need only a pool-base shift; bind already keeps a separate static offset (E2E-11 step 1a-ii)

Implementing C114 turned out to require no layout model of my own. `bind.ml`
maintains `soff`, a static offset counter independent of the automatic counter,
and returns `(name, rt, offset, auto)` with `auto = not stc` [bind.ml:329-361],
so static cells already arrive numbered 0,1,2... exactly as DR's `S(...)`
column shows them, and automatics arrive packed among themselves exactly as
DR's `A(...)` column shows them. Codegen's whole job was
`base = static_total + pool_total` plus seeding the initialiser bytes as data
blocks at their absolute addresses — the existing per-block
`SET-LC(data,addr)` emission [G113] then produces DR's shape unchanged.

Verified byte-exact: E20B (1 static + literal + auto), E20D, E20E (two statics
at S(0000)/S(0001) with autos above a 2-byte pool), E11D — the strongest of
them, with twelve static bit cells interleaved with four automatics, both bit
comparison forms, a two-way `if/else` and a `n = n + 2` store, DATA AREA 0015
in both compilers. `statics` here is scoped to explicit `STATIC` on `BIT(1)`;
`STATIC` on any other kind refuses, because C114 pins the ORDERING of static
bytes but nothing pins the ENCODING of a multi-byte initialiser (T3 shows DR
does compile `dcl s fixed static initial(5);`, so this is a capability gap, not
a language limit).

One trap worth recording: bind's `stc` is broader than the `STATIC` attribute —
FILE, FORMAT and ENTRY rows are static-classified and consume `soff` bytes.
A `STATIC BIT(1)` declared alongside a FORMAT would therefore land after that
cell, a combination DR has never shown me; that mixture refuses rather than
reordering by analogy.

## C116 — the parser never fills `bdecls`; declarations arrive as `Sdcl` STATEMENTS (E2E-11 step 1a-ii)

`Ast.block.bdecls` exists and is read by `pli80deps`, but `parser.ml` sets
`bdecls = []` at both block constructors [parser.ml:760, parser.ml:1089] and
routes every declaration into `bstmts` as an `Sdcl` item. Any code that wants
"the declarations of a block" must therefore collect the `Sdcl` statements —
reading `bdecls` silently yields an empty list, which fails nothing and looks
correct.

This is how `E20C` compiled instead of refusing. I wrote the INITIAL-without-
STATIC rule, wired it to `b.bdecls`, saw the program build cleanly, and the
rule never fired because the attribute list it consulted was always empty. The
same mistake in `pli80deps.ml`'s `walk_block` was harmless only because
`walk_stmt` independently handles `Sdcl`, so the blocker audit stayed right.

Consequence for the audit: its declaration findings come from statement
walking, not `bdecls`. Consequence for anyone adding an attribute-driven rule:
grep the parser for where the field is actually assigned before trusting it.

## C117 — DR rejects multi-bit bit-string literals; wider BIT is a storage question, not a literal one (E2E-11 step 1a)

`dcl b bit(5);` alone is fine [golden/e2e11u/T2: DR compiled it and emitted a
`.REL`], and `b = c;` between two bit(5) variables is fine [same]. But
`b = '10101'b;` is a **SYNTAX error in DR's own pass 1** with no `.REL`
emitted [golden/e2e11r/T2 hand-written variant, superseded by T2 above which
avoids the literal]. So `'0'b` / `'1'b` are the only bit literals this compiler
has evidence for, and the `BIT(n) n>1` perimeter is about cell layout and copy
lowering, not about literal syntax. Related refusals that DR proves are only
perimeter gaps, pinned as negatives with their own DR goldens: bit-to-bit copy
[N74 ← golden/e2e11u/T1], `bit(5)` copy [N75 ← .../T2], `STATIC INITIAL` on
FIXED [N76 ← .../T3], bare `if f` on a bit variable [N77 ← .../T4].

## C118 — probe source formatting: CRLF throughout, `;` then `\r\n\x1a`, and NO trailing `$` line (E2E-11 step 1a)

Three ways to make a valid-looking probe fail for reasons that have nothing to
do with the feature under test, all hit in this slice:

* LF-only line endings make DR report `UNEXPECTED EOF` and emit no `.REL`
  [golden/e2e11r/T1-T3 and e2e11s/T1-T3 -- two attempts, same cause].  CRLF
  throughout is what DR's lexer expects; every real corpus source is CRLF.
* A trailing `$` on its own line is a **DR syntax error** [e2e11t/T1-T3, after
  fixing the line endings: `SYNTAX` in pass 1, no `.REL`]. Statement-terminator `$` is not required at the
  end of a source, and adding one breaks compilation. My parser also rejects
  it (`trailing garbage after final END`), so both sides agree here — but the
  convention must be stated or probes keep failing mysteriously.
* EOF must be `...;\r\n\x1a`: the `^Z` needs its own preceding CRLF [E2E-9
  rule, restated].

The working convention, matching `e13src/E20A.PLI` byte-for-byte in shape:
CRLF body, final line `end <NAME>;\r\n`, then `\x1a`, no `$`.

## C119 — DR elides a literal zero added/subtracted against a VARIABLE, not against a literal (E2E-11 step 1a)

Twelve probes over four batches pin this exactly. Against a variable the term
vanishes and DR emits a plain copy:

```
a = a + 0;      LHLD A / SHLD A     [T5]   -- byte-identical .REL to `a = a' [T6]
a = a - 0;      LHLD A / SHLD A     [T7]
a = a + 0 + 0;  LHLD A / SHLD A     [T8]   (nested elision, innermost collapses too)
b = a + 0;      LHLD A / SHLD B     [T9]
b = a + 0 + 0;  LHLD A / SHLD B     [T10]
b = a - 0;      LHLD A / SHLD B     [T12]
b = 0 + a;      LHLD A / SHLD B     [T13]  (zero on the LEFT elides as well)
```

Against a literal it does NOT: `b = 5 + 0;` takes DR's decimal pool path —
`LXI H,*S / MVI A,01 / CALL ?DLDOP / LXI H,*S / MVI A,01 / CALL ?DLDOP / CALL
?DADOP / CALL ?QDI15` [T11] — the same no-constant-folding rule already recorded
for `3 + 2` [R2045, P044 line 3]. And a zero MINUEND is not droppable at all:
`0 - a` is a negation, so the rule is asymmetric on `Sub`.

`fp_add_guard`'s older note in this tree described `x = x + 0` as a bare
`LHLD X ; SHLD X` pair — that was right all along — while the refusal wired to
it (N56) turned a *capability gap* into what read like a language boundary. The
gap is now closed by an AST-level elision (`elide_fixed_zero`, gated on every
identifier in the kept expression being a 2-byte FIXED cell) plus a `k = 0` rung
of the constant-bias ladder, which emits no bias instructions and so reproduces
the copy shape with no new lowering. DEC and FLOAT zero-elision remain unprobed
and keep their existing paths.

## C120 — `dcl <name> file;` becomes a NAMED COMMON group of 34 + len(name) bytes (E2E-11 step 2)

A FILE variable takes no DATA cell.  DR emits, per file:

```
LINK  DEF-COMMON-SIZE  (abs, 34 + len NAME)  NAME
LINK  SEL-COMMON                             NAME
LINK  SET-LC           (common, 0)
      33 zero bytes | 1 byte = len NAME | the NAME bytes          <- 34 + len total
```

measured on two names of different length: `SYSIN` → 39 bytes, byte 33 = 0x05,
bytes 34-38 = "SYSIN" [FLTPOLY2, E11A, E11C, E11E, E11F]; `INF` → 37 bytes, byte
33 = 0x03, "INF" [E17A].  So the length byte is the name's own length and the
leading 33 bytes are zero-filled control fields, not garbage.

Two mechanical consequences that are easy to get wrong:

* The block is emitted AFTER the header links (PROG-NAME / REQ-LIBRARY / EXTDEF /
  DEF-PUBLIC) and BEFORE `SET-LC(data,0)`, so DATA-segment addresses are
  unaffected: FLTPOLY2's `eofile` still sits at data 0x0000 and its pool base is
  0x0038 with the literal pool above the single static byte.
* `SEL-COMMON NAME` is re-emitted before EVERY relocation into that group, not
  just once — DR's item sequence has a second `SEL-COMMON SYSIN` immediately
  before the `LXI H,SYSIN` operand deep in the code segment.  Emitting it only at
  the definition would leave that relocation pointing at whatever group happened
  to be active.

No new bit-layout was needed: `rel80.ml`'s generic LINK encoder already handles
type 1 (no value, name) and type 5 (ABS 16-bit value, name).  Only the type codes
were missing.

## C121 — a GOTO out of an ON handler makes DR put a `?RECOV` prologue at the TARGET label (E2E-11 step 2)

`on endfile(sysin) goto out;` lowers as [golden/e2e11g/E11F, code 0x18]:

```
0018   JMP  <out>            ; the handler body is just the jump
001B   out: LHLD * A(000B)   ; 2 hidden automatic bytes
       001E   SPHL
       001F   CALL ?RECOV    ; discard the handler's runtime frame
```

The label itself grows a stack-unwind prologue, because the handler executes
inside PLILIB's call context and jumping past it must drop that frame.  A plain
GOTO has no such thing — G115's labels contain zero `?RECOV` and are byte-exact —
so this is specific to the handler crossing, and it is a property of the TARGET
label rather than of the goto statement, which makes it non-local.

My label lowering has no RECOV path and no hidden-cell allocation, so emitting it
would change the AUTO area as well as the code: E11F came out with 335 divergent
bytes when I let it through.  It now refuses [N79].  Unprobed: whether `SIGNAL`,
`ON ERROR` + goto, or a label reached by BOTH a plain goto and a handler goto take
the same prologue.

## C122 — statement-position CALL uses the SAME lowering as an expression call; and DR's two procedure kinds are disjoint (E2E-11 step 3)

**Statement.** `CALL p(args);` and `x = p(args)` are the same three-part
sequence -- per-argument descriptor pointer cells, then `LXI H,*A(slot)`, then
`CALL <entry>` -- and they differ ONLY in the post-call store of the result.  The
milestone instruction explicitly forbade assuming this, so E24A/E24B put both
forms in one program and the listings decided:

```
call g(a);      000C  LXI  H,* A(0004)      <- descriptor, then CALL
                  000F  CALL 0000
n = h(a);       0012  LXI  H,* A(0006)      <- same shape, different slot
                  0015  CALL 0000
                  0018  SHLD N A(0002)      <- the only extra work
```

Reuse is therefore correct, and my implementation funnels CALL statements through
the existing `Esuffix` path rather than duplicating it.

Two further halves of the same rule, all DR pass-2 diagnostics with NO `.REL`
emitted, so refusing them is conformance rather than a gap:

| program | construct | DR |
|---|---|---|
| E24D | `call acc(s);` where acc `returns(fixed)` | `NOT PROC` |
| E24H | `call hf(a);` where hf `returns(float)` | `NOT PROC` |
| E24I | `n = gs(a);` where gs has no RETURNS | `TYPES NOT=` |

So the procedure kinds are disjoint: a value-returning procedure has no
subroutine form, and a subroutine has no value.  My compiler marks the direct
callee of a CALL statement (`st.call_stmt`) and checks both directions.  The mark
names the exact callee rather than being a depth flag, because an expression call
nested inside a CALL statement's argument list must still be checked against the
expression rule.

**Wrong path.** My first attempt at the mark was a boolean flag, which would have
let `call f(g());` skip the check on `g()`.

## C123 — one CHAIN-ADDRESS serves many forward CALL sites, chained site-to-site (E2E-11 step 3)

**Statement.** When a procedure is called before it is emitted, DR does NOT put a
chain record at each site.  It emits one chain record targeting the LAST site's
operand word, and each later site's operand is an inline `RELOC(CODE, <the
immediately preceding site's operand address>)`.  E27A (three forward calls to `s`)
is the decisive specimen:

```
site 1  0017 CALL 0000     operand 0018 <- two literal zero DATA bytes
site 2  001D CALL S        operand 001E <- RELOC(CODE, 0018)
site 3  0023 CALL S        operand 0024 <- RELOC(CODE, 001E)   NOT 0018
        LINK-CHAIN-ADDRESS, address-to-load = 0024             the LAST site
```

E25F (two sites) agrees: chain on 001A, second site relocated against 0014.  With
a single site -- every accepted specimen before this -- "last" is "that one", so
the old behaviour is a special case of the new rule, not a contradiction of it.

**Verified beyond the bits, and one statement of mine that was false.** I
originally wrote that my wrong version "was byte-identical at the record level
while linking to a WRONG address", and that "a two-site program cannot distinguish
'against the first' from 'against the previous'".  Both halves were wrong, and the
first is self-contradictory: two identical raw `.REL` files linked under identical
conditions cannot produce different `.COM` images, so a `.COM` difference *proved*
the `.REL` differed and my "byte-identical" was the mistake.

I reproduced it by reverting just the re-anchoring line in a throwaway worktree and
comparing against the pinned goldens with the wrong rule in place:

| specimen | sites | raw bytes vs DR | where |
|---|---|---|---|
| E25F | 2 | **DIFFERS** (byte 105) | `LINK-CHAIN-ADDR` target `0014` instead of `001A` |
| E27A | 3 | **DIFFERS** (bytes 109, 124, 125) | chain target, plus one code `RELOC` constant `0x18` vs `0x1e` |

So E25F alone *did* discriminate.  What made the difference invisible was my own
tool: `tools/reldump.py` formats a record's address field only when it is an `int`,
and every LINK record carries a `(SEGMENT, ADDRESS)` **tuple** -- so
`LINK-CHAIN-ADDRESS` printed as `LINK-CHAIN-ADDR  None` with the one number that
identifies the chain target suppressed.  Two files whose chain targets differed
printed identically, and I trusted the dump over `cmp`.  The formatter now prints
tuple address fields (and re-running the diff shows `code 0014` vs `code 001A`
directly), which is the actual fix: a decoder that hides the discriminating field
turns a passing `cmp` into a false "looks the same".

The rule itself is unchanged and stands as stated above, corroborated by linking my
own `.REL` for E25F/E27A and comparing the resolved `.COM` operands with DR.  What
changes is the provenance: the linker comparison was a *second* witness, not the
first, and the reason the bug survived my first look was tool blindness, not
insufficient test coverage.

## C124 — a zero-argument call has no descriptor and no LXI H at all (E2E-11 step 3)

**Statement.** `call q;` and `n = f();` for zero-parameter procedures are a bare
3-byte `CALL <entry>`.  There is no `LXI H` and NO storage: three such sites in
E24J leave main's `a`, `b`, `c` at A(0000), A(0002), A(0004) with nothing between
them, which is the check that the descriptor slot really is zero-sized rather than
merely unreferenced.  bind registers the site anyway, because DR keeps call sites
in source order (E24A: `call q` then `n = f();`).

**Wrong path.** My `Esuffix` arm had `args <> []` in its guard, so zero-argument
calls fell to a refusal that read "zero-arg / non-identifier call deferred".  That
was a capability gap, not a DR limit; the same shape also blocked procedures with
no formals in bind (`procedure q without formals [TBD]`), which E24A/E25A prove is
ordinary DR -- and which needed no new layout rule, only `nf = 0`, which the
existing offset formulas already carried.

## C125 — a procedure without RETURNS gets an implicit RET after its body (E2E-11 step 3)

**Statement.** The trigger is the absence of `RETURNS`, not the shape of the last
statement.  Seven different endings all get the same one-byte exit:

| specimen | body ends with | DR |
|---|---|---|
| E25A | nothing (empty body) | `RET` is the body's ONLY instruction |
| E24A / E24F / E25H | an assignment / a DO WHILE / another CALL | `RET` |
| E25G | a label, then an assignment | `RET` |
| E25B | inside an `IF` (branch skips it) | `RET` after the branch |
| E25E | a DO WHILE | `RET` after the loop's backward JMP |

Value-returning procedures get none: E25D's `f` exits through RETURN's own `RET`
and nothing is appended, while the sibling subroutine `s1` in the same program does
get one.  So the rule is a property of the declaration.

**Wrong path.** None -- this was found because E24A's `.REL` was 3 bytes short of
DR's at exactly the byte where `q` ends.  Every procedure in my corpus goldens so
far ended in `RETURN`, so the fall-through case simply had no coverage.

## C126 — a LABEL definition ends HL-constant reuse (E2E-11 step 3)

**Statement.** DR's straight-line HL-constant reuse does not survive a label
definition.  E25G: `t = 1; jmp: t = 2;` emits `LXI H,0001 / SHLD T / LXI H,0002 /
SHLD T` -- a full reload, where the same pair without the label reuses HL with one
`INX H`.  This is the boundary rule already established for branches [R723], and
the reason is the same: a label is somewhere a GOTO can land, so HL's contents are
not known there.

**Wrong path.** I implemented the reset unconditionally after the label loop rather
than gated on `slabels <> []`.  That silently disabled HL-constant reuse for EVERY
statement.  E24J -- already byte-exact in this session -- went from identical to
one shifted relocation, with identical DATA bytes: the same "addresses all match,
one thing is missing" signature as C116's `bdecls` and C118's missing statement
arms.

## C127 — storing through a pointer formal: three shapes, two byte orders (E2E-11 step 3b)

**Statement.** In a non-recursive procedure the formal cell holds the ADDRESS of
the caller's variable, so every store goes through it.  Which shape DR uses depends
on whether the pointer survives the right-hand side, and the byte ORDER flips with
it:

| RHS shape | lowering | specimens |
|---|---|---|
| constant | `LHLD X / XRA A / MOV M,A / INX H / MOV M,A` (0), else `LHLD X / MVI M,lo / INX H / MVI M,hi` | E26A (0, 255), E25B (3), E26E (9), E26H (300 -- same two-byte form past 255) |
| `x +- literal` | `LHLD X / deref / bias / XCHG / MOV M,D / DCX H / MOV M,E` -- HIGH byte first | E25F (+1), E26B (+256 via LXI B/DAD B, -1, and +1000), E26I (-3 = three DCX H) |
| anything else | `<eval rhs> / PUSH H / LHLD X / POP D / MOV M,E / INX H / MOV M,D` -- LOW byte first, pointer reloaded | E26C (x=y), E26D (x=x, x=x*y), E26H (x=q, x=x+p), E26I (x=0-x) |

The bias case stores high-first only because `DE` still holds `ptr+1` left over
from the deref read; when the pointer is dead, DR reloads it and stores low-first.
So the route is keyed on the RHS **shape**, not on the value -- and E26H `x = x + p`
shows the same thing in the expression itself: with the LEFT operand a deref'd
formal and the right a plain cell, DR keeps the value in DE across `LHLD p` via a
second `XCHG` instead of pushing.

**Wrong path.** I first wired `lower_store_ptr` in as a side-effecting guard
*before* the big `match` in `lower_assign`, so the pointer store ran and then the
ordinary store ran too.  E26E emitted both a store-through-pointer and an SHLD of
the same value.  A guard that emits code is a trap; it is now a first arm of the
match.  The same bug in the `Add` route -- treating any deref as forcing the PUSH
form -- added a spurious PUSH H/POP D pair for `x + p`.

## C128 — comparison against a pointer formal (E2E-11 step 3b)

**Statement.** DR's two-variable fixed compare normally pairs with `XCHG`
(`LHLD first / XCHG / LHLD second / CALL ?IS22N / <skip>`).  When the SECOND loaded
operand is a pointer formal the deref ladder ends in its own `XCHG`, which would
destroy the value held in DE, so DR is forced onto the stack:

```
if i < x       LHLD I / PUSH H / LHLD X / MOV E,M / INX H / MOV D,M / XCHG
               POP D / CALL ?IS22N / JP skip            [E26F]
if x > i       LHLD I / PUSH H / LHLD X / deref / POP D / CALL ?IS22N / JP skip
if i < x (DO WHILE)                                      [E26G, E25E]  byte-identical
```

i.e. the operand order is chosen by which side derefs (plain first, pointer
second) and NOT by the relation -- `x > i` and `i < x` compile to the same
instructions.  Against a literal, the deref is simply prefixed to the ordinary
bias ladder: `if x > 4` is `LHLD X / deref / LXI B,FFFB / DAD B / MOV A,H /
ORA A / JM` [E26G].  The `> 0` case has no bias to apply and instead uses a memory
form: `LHLD X / XRA A / CMP M / INX H / SBB M / JP` [E25B] -- which is why the
plain-variable `> 0` stays refused; that form exists only because HL already holds
an address.  (Its `CMP M`/`SBB M` are 0xBE/0x9E, not the 0xB6/0x96 I first wrote;
byte-exactness caught it, a mnemonic guess would not have.)

**Unserved, refused rather than guessed.** a pointer formal as the FIRST operand of
a two-variable compare, and both operands pointers: DR always orders plain-first,
and the deref-first pairing has no sample.

**Also found, not yet implemented.** DECIMAL and FLOAT formals passed by reference
DO have DR lowerings -- E26J loads through the pointer with `LXI H,R / MVI A,09 /
CALL ?DLDOP` then stores with `LHLD Q / MVI A,09 / CALL ?DSTOP`, and E26K moves a
float with `LXI H,*S / PUSH H / LHLD Q / POP D / CALL ?FX44M`.  This is the fifth
occurrence of the N56/N63-N66/N77 pattern: N55_FORMAL_STORE is a negative whose
subject DR compiles.  It stays in the panel because my compiler genuinely refuses
it, but it is now correctly labelled a capability gap, and its marker matches the
narrower refusal (non-FIXED-BINARY formals) rather than the old blanket one.

## C129 — every AST walker must enumerate every statement kind (E2E-11 step 3, third occurrence)

**Statement.** `bind`'s call-site collector had no arm for `Sprocedure_stmt` at all,
so CALL statements allocated no descriptor cells, and it also omitted ON handlers,
EDIT, FORMAT, file statements, READ/WRITE VARYING subjects, and PUT/GET stream and
option expressions.  It is now exhaustive by enumeration in BOTH of its passes
(`own` and `kids`) over `Ast.stmt_kind`.

**Why enumeration rather than a catch-all.** A missed call site is not a
diagnostic; it is a silently shifted descriptor queue, which is the same failure
class as C116 (`bdecls` always empty) and step 2's `prescan_pool`/`edit_stmts`
(`Son` missing).  With a `| _ -> []` catch-all, adding a statement kind to the AST
compiles cleanly and drops call sites at runtime; without one it is a compile
error.  Removing a catch-all turned out to bite immediately in the other direction:
`own` and `kids` are separate matches over the same statement, so `Sdobegin`,
`Sstop None` and friends fell through to `Match_failure` -- a runtime crash, not a
type error, and the fix is to list the sub-block-only statements in both matches.

## C130 — forwarding a pointer formal as an actual writes the descriptor at RUNTIME (E2E-11 step 3c)

**Statement.** When the actual argument of a CALL is itself a pointer formal of the
calling procedure, DR cannot emit a static descriptor word: the value the callee
needs is the address the formal already holds, which is dynamic.  So the 2-byte
descriptor operand is *replaced* by three instructions plus a store, and the
descriptor pointer is unchanged:

```
t1: procedure (y) ...  call s(y);
      003A LHLD Y A(000A)     <- the formal's VALUE, not the address of Y
      003D SHLD A(0012)       <- into the descriptor cell, at runtime
      0040 LXI H, A(0012)     <- unchanged: the call still points at the block
      0043 CALL S
```

Two consequences that mattered.  First, the forwarding route carries **no
`SET-LC` records**, where the static route wraps each operand in a `SET-LC` pair --
so the difference is not just "load instead of constant" but a different record
shape.  Second, `slot` in this path is already an absolute DATA address: my first
version added `st.base` to it, which wrote the descriptor cells 4 bytes past the
block my own `LXI H` pointed at, and the file was internally inconsistent in a way
no comparison with DR could excuse.

Statement and expression position behave the same as everywhere else in C122:
E27B (`call s(y);`) and E28A (`return (f2(q, p));`) both forward.

**Semantic witnesses, not just bytes.** E28A's `f2` returns `a + b`, which is
commutative and therefore *cannot* detect a swapped argument order -- so I wrote
E28B, where `f2` returns `a * 10 + b`: the linked program prints **53**, and a swap
would print 35.  E28C checks the other failure mode: `b = 2; call t1(b);` where
`t1` forwards `y` into `s`, which does `x = x + 1`; the program prints **3**, so the
mutation reaches the original caller's cell two levels up, where a silently
*copying* forwarding would leave 2.  Both `.REL` byte-exact against DR, both `.COM`
byte-identical, both run rc=0.

**N54_FORMAL_PASSTHRU retired** (6th instance of the pattern after N56, N63-N66,
N77, N55): it was a capability-gap negative whose subject DR compiles.  I checked
DR's verdict before touching it -- `golden/e2e133/E28A` exists and my output is
byte-identical -- and only then converted the source into a positive specimen.  The
negative panel goes 68 -> 67 with 379 -> 381 positives.

## C131 — DEC and FLOAT stores through a pointer formal differ from the ordinary route by ONE OPCODE (E2E-11 step 3d)

**Statement.** Both non-binary pass-by-reference stores are DR's normal lowering
with the destination's address-taking instruction replaced by a cell load:

```
gd: procedure (q) ...  q = r;          (q POINTER/param FIXED DEC(9,2))
      LXI H,R A(000F) ; MVI A,09 ; CALL ?DLDOP     <- source: unchanged
      LHLD Q A(0016)  ; MVI A,09 ; CALL ?DSTOP     <- destination: LHLD, not LXI H

gf: procedure (q) ...  q = 3.25;       (q FLOAT param)
      LXI H,* S(0008) ; PUSH H ; LHLD Q A(001A) ; POP D ; CALL ?FX44M
gf2: (u,v) ...  u = v;   BOTH pointer formals
      LHLD V A(001E) ; PUSH H ; LHLD U A(001C) ; POP D ; CALL ?FX44M
```

The reason is structural, not a coincidence: `?DSTOP` and `?FX44M` already receive
the destination *in a register* (HL and DE respectively), so handing them a
pointer's value instead of a cell address changes only how that register is
loaded.  This is why the feature was cheap once E26J/E26K were probed, and why my
earlier refusal claimed a missing "decimal/float stack store-through-pointer path"
-- there was never a stack mechanism to build, only an opcode to swap.

`LHLD <formal cell>` also means the relocation still points at the formal's own
DATA cell (the pointer), which is why the record stream is otherwise unchanged.

**Scope, kept narrow by refusal.** A FLOAT destination that is a pointer formal with
a *computed* source (the `?FX44S` pop-into-cell route) has no DR sample and still
refuses; so does any other type through a pointer (BIT(1), CHAR).

**N55_FORMAL_STORE retired** (7th instance of the pattern): DR compiles the source,
E28D reproduces it byte-exactly, and E28E is the semantic witness -- `r = g(x)`
where `g` does `q = y` with `y = 2.5` prints `2.50 2.50`, so the caller's own `x`
was overwritten through the pointer rather than a copy being made.  All four
specimens are byte-exact at `.REL`, byte-identical at linked `.COM`, and E28E's
console output is byte-identical to DR's own run.

## C132 — external ENTRY has a complete executable acceptance route: DR's own assembly modules assemble and link (E2E-11 step 3e)

**Statement.** The historical `DIV2.ASM` and `FDIV2.ASM` are in the reference
corpus (`DISK2`, also `pli80-v10`), and the CP/M distribution disk my oracle
already uses carries **RMAC.COM** -- Microsoft MAC-80 relocatable assembler --
which is the tool those sources are written for.  They assemble cleanly with
period software:

```
RMAC D:DIV2.ASM=D:DIV2.REL/L
CP/M RMAC ASSEM 1.1 | 002A | 000H USE FACTOR | END OF ASSEMBLY
```

`000H USE FACTOR` means zero unresolved externals, and the resulting `DIV2.REL` /
`FDIV2.REL` link with DR's LINK-80 and PLILIB.IRL.  Driven end to end, DR's own
`DTEST` and `FDTEST` now **execute**: `LINK D:DTEST,D:DIV2` produces a 7808-byte
`.COM`, and running it prints `100 / 2 ** 0 = 1.0000000E+02`, `... = 5.0000000E+01`,
`... 2.5000000E+01`, i.e. the correct halving sequence computed by the external
assembly routine through the PL/I call descriptor.

**Dialect matters and is not interchangeable.** The sources use `title 'name'`,
`public div2`, `extrn ?signal` and `;` comments -- MAC-80 syntax, not DR ASSEMBLE
syntax (`NAME`/`ENTRY`/`EXTERNAL`, `&` comments).  Using `ASM.COM`, or hand
translating, would make the object file evidence about my transcription rather
than about DR's module, and would quietly downgrade every downstream comparison.

**Independent witness.** The expected values are arithmetic, not a byte match:
`100/2**k` for k=0..22 with 7 significant digits.  DTEST (external CALL statement,
`div2` a subroutine) and FDTEST (external ENTRY in expression position, `fdiv2`
returning float) print **identical** tables, which is itself a check that the two
call forms reach the same descriptor.

**ABI confirmed from the historical source, not inferred.** `DIV2.ASM` opens
```
div2:            ;HL = .low(.p1)
        mov     e,m       ;low(.p1)
        inx     h         ;HL = .high(.p1)
        mov     d,m       ;DE = .p1
        inx     h         ;HL = .low(p2)
        ldax    d         ;a = p1 (power of two)
```
so the callee receives **HL = the address of the descriptor**, and each descriptor
entry is the address of an argument, which is exactly the `LXI H,*A(desc) / CALL`
shape my compiler already emits for internal calls [C122].  The header comments
also pin the contract: `p1 -> fixed(7)`, `p2 -> floating point number`, and for
`div2` the *exit* says `p2 -> p2 / (2**p1)` (a subroutine writing through its
argument, cf. C127/C131), while `fdiv2` says `p1/p2 -> (unchanged); stack: p2 /
(2 ** p1)` -- a value-returning entry leaves its result on the stack that
`?RSBLK`/`?FPRET` consume.

**Object-file vs executable acceptance, now unambiguous.** Previously the
external-ENTRY feature could only ever be tested at `.REL` level, so byte-identical
object files would have been the strongest available claim.  That limitation is
gone: for any program that calls an external entry I can now compare `.REL`,
compare the `.COM` linked by DR's LINK-80 against the same RMAC-built module, and
compare executed output.  `oracle/linkrun.py asm` is the new stage
(`EXTRA_REL` maps DTEST->DIV2, FDTEST->FDIV2 for the link stage).

**Status.** The route is established; my compiler still refuses external ENTRY
[C122-adjacent, N84].  What remains is to make bind's `RTentry` visible to codegen
(`st.vars` carries `vkind`, which has no entry case) and emit
`call_ext <SYMBOL>` in place of the forward/internal resolution, which the
E24G/DTEST/FDTEST goldens make checkable in one step.

**Status update (step 4).** Superseded for the implementation half: codegen now sees
external entries and DTEST/FDTEST are accepted end to end -- see C133.  The toolchain
finding above stands unchanged.

---

## C133 — an external ENTRY call site is `CALL * L(sym)` plus one LINK-CHAIN-EXT, and nothing else (E2E-11 step 4)

**Statement.** `declare <name> entry(<formals>) external [returns(<t>)];` compiled in a
caller that does not define the entry produces, per call site:

```
LXI H,* A(desc) ; CALL * L(<NAME>)        <- + LINK-CHAIN-EXT code <call+1> <NAME>
```

No `LINK-DEF-EXT` group, no inline `RELOC` on the CALL, no `LINK-CHAIN-ADDR`.
`returns(float)` additionally routes the result through the float-stack convention, so
an expression-position external call prints and assigns like an internal float function.

**Evidence.** `artefacts/DTEST.PLI` and `artefacts/FDTEST.PLI` (corpus) versus
`golden/e2e141*`: `.REL` 384 bytes byte-identical; linked `.COM` byte-identical to DR's
(7808 bytes, against RMAC-assembled DIV2/FDIV2 per C132); executed output
byte-identical to DR's own run; 135/135 printed values verified numerically outside the
emulator, including the signed wrap of a 1-byte index cell
(`100 / 2 ** -128 = 3.4028235E+38`). Both runs end in DR's diagnostic
`UNDERFLOW (128), Underflow in Divide by Two / Traceback: p c`, emitted by the external
module's `extrn ?signal`; the final PUT record is incomplete in both, identically.
`golden/e2e143/E29A`, `e2e144/E29C`, `e2e145/E29E` pin the three negative-space claims:
E29A (caller only, 1 record) vs E29E (caller + defining program, 4 records) shows
DEF-EXT comes from the definition, not the reference; E29B (inline RELOC) linked to a
file that executed to a traceback -- a CALL to address 0; E29D (CHAIN-ADDR on the
symbol) got 0 bits consumed and `NOT IMP`.

**Why the record asymmetry matters.** `LINK-CHAIN-EXT` carries a symbol name and no
address field; `LINK-CHAIN-ADDR` carries an address and no name. My first attempt used
the ADDR form because that is what internal forward calls need (C123), and DR's
assembler rejects it -- the two forms are not interchangeable, which is the point of
having two.

**Corollary (accepted shapes).** A 1-byte FIXED index cell is initialized with
`XRA A ; STA` and incremented with `LXI H,c ; INR M ; JMP` -- in-memory, not
`LHLD/INX H/SHLD`. Zero stores use `XRA A` rather than `MVI A,00` wherever DR has
evidence for it (DO init in DTEST, plain assignment in E29A/E29D); non-zero constants
keep `MVI A,lo` (N306/N308). Had I kept the register ladder, the loop would have
incremented a copy: values printed would have stayed correct for `i = 0`, so only the
byte compare, not the output compare, would have caught it.

---

## C134 — pool cells for call-literal arguments have TWO owners, and the base is computed before either runs (E2E-11 step 4)

**Statement.** `base = statics_total + pool_total` is fixed from the prescan, before
lowering allocates a single cell. Therefore every pool cell must be *demanded* by a
prescan walker, and literal call arguments are demanded by whichever walker happens to
cover that expression position: `pdec_fl_expr` for a float-target assignment (which had
an Esuffix arm, so R3062 was always exact) and `prescan_expr` for everything else (which
had no Esuffix arm, so FDTEST's `fdiv2(i, 100)` inside a PUT item demanded nothing). The
byte size of a literal argument cell is a property of the FORMAL, not of the literal's
spelling -- FDTEST passes `100` against a float formal and DR allocates 4 MBF bytes.

**Evidence.** FDTEST's first symptom was `LINK-DEF-DATA-SIZE` mine 0016 vs DR 0018; the
2-byte shortfall put automatic `i` at 000d, inside the float constant 100.0 occupying
000b-000e, so `STA I` would have overwritten the constant while every address in a
decoded dump remained plausible. Counting the cell in `const_cells` instead made FDTEST
exact and broke R3062 (mine 0018 vs DR 0014) -- a double count. With the prescan arm in
place, `formal_float_at` (used by `const_cells`) still resolved callees only through
`pl_ptrs`, answered "not float" for the external entry, and added its 2-byte FIXED cell
on top: FDTEST 001A vs 0018. One accessor (`callee_formal_rt_l`) for all three consumers
resolved it; final: gate 390/390, FDTEST and R3062 both byte-exact.

**Method.** A double count and a missing count are the same symptom class -- a small
DEF-DATA-SIZE disagreement -- so the size delta does not discriminate. The discriminator
is which *previously exact* specimen breaks when you ADD bytes: R3062 broke on adding,
therefore the bytes already had an owner, therefore "missing" was the wrong story and
"two owners" was the right one.

**Architecture.** Three functions answered "is argument i of this callee FLOAT?", each
correct for the case it was written for and each wrong for the new one. This is C129's
pattern with a callee type instead of a statement kind: adding one variant to a
semantic relation fans out across every independently-written consumer. No hard case
was involved -- external ENTRY is the same descriptor ABI as internal calls (C127-C131).
See spec/notes/e2e11-step4-external-entry.md §4.

---

## C135 — a forward-reference chain gets ONE LINK-CHAIN-ADDR header, emitted at its RESOLUTION point (ARCH-1 prototype)

**Statement.** For a CALL whose target is not yet defined, DR's `.REL` contains:

* the FIRST referencing site writes two **absolute zero** bytes as its target word
  and becomes the chain head;
* every LATER site writes one **relocatable CODE word holding the current head**, and
  becomes the new head (so the newest site is the head, and each link points at the
  immediately preceding site — this is C123's forward-chain rule seen from the other
  end);
* exactly **one `LINK-CHAIN-ADDR` header per chain**, naming that head slot, emitted
  at the **resolution point** — immediately before the first byte of the definition
  that resolves the reference — *not* next to the reference, and *regardless of how
  many sites there were*.

**Evidence.** Counted across the chain-bearing goldens (20 specimens): E25C has 8 CALLs
and 7 CHAIN-EXT but ONE header; E26J has 9/8 and one; E25F has 4 CALLs and one;
E25D/E25H/E26A/E26K/E27A/E27B/E27C have two targets and exactly two headers. Placement:
E25F's header sits at bit 826, immediately preceding `s`'s body at code 001F; E27C's two
headers at bits 825 and 1032 immediately precede the bodies of `p1` (code 001F) and `p2`
(code 0033). Production already satisfies this rule — all of those specimens are
byte-exact gate members — but it implements it through `fcalls` being *prepended*, i.e.
a list-direction side effect rather than a stated rule.

**How it was found.** The ARCH-1 prototype (`ocaml/proto/`) initially needed one
hand-placed `ChainItem` for E25F, because no *local* rule over the instruction stream
reproduces DR's placement — the header belongs to a site emitted two instructions
earlier but appears after the following statement's external chain fixup. Treating that
as a permanent escape hatch would have been the wrong conclusion; asking instead "where
does it *always* appear?" produced the resolution-point rule, after which the prototype
reproduces **E29A and E25F byte-identically with zero hand-placed items**. Recorded in
spec/notes/arch1-proto-inst-layer.md §4.

**Caveat.** One per chain, at the definition — established from labels and internal
procedures. Whether an *external* symbol resolution (`LINK-CHAIN-EXT`) has an analogous
header is a different question: externals get their fixup at the reference site (C133),
and the two mechanisms were never conflated here.

---

## C136 — a file whose outermost block has NO `options(main)` is a plain procedure: no `?START` prologue, but still PUBLIC (E2E-11 step 5)

**Statement.** DR compiles a procedure-only source file -- e.g. corpus program `A`:

```
a: procedure(x) returns (float);   CODE SIZE 0015   DATA AREA 0006
  declare x float;                 no LXI B,0200 and no CALL ?START at all
  return (x/2);                    LINK-DEF-PUBLIC code 0000 A  IS still emitted
```

The body is entered as a callable routine: the incoming formal is copied into its
declared cell by the same 2-byte copy ladder seen in nested procedures (`5E 23 56 EB`
+ `SHLD`), the value-returning exit is `JMP` + `LINK-CHAIN-EXT ?FPRET` (not `CALL`, not
`RET`), and a fixed literal divisor becomes a **4-byte MBF pool cell** at `*A(0000)`
(`00 00 00 82`) with `?FD44M` doing a float/float divide -- DR does NOT insert a
runtime ?QI15F conversion.  So the file is externally visible (PUBLIC + EXTDEF) without
being a program entry point.

**Evidence.** `golden/first/A/A.REL` + `A.PRN` (DR's own listing), and four probes run
through DR in batch `golden/e2e147`: Q1 (`returns (float)`, float literal), Q2
(no RETURNS, formal + assignment), Q3 (`returns (fixed)`), Q4 (main + `y = x/2`) --
**all four compile cleanly**, i.e. nothing here is a language limit.

**My status.** Q4 is BYTE-EXACT against DR, which settles the important part: the
mixed-mode float/fixed literal arithmetic route already exists and is correct.  What is
missing is structural -- `emit_program` unconditionally emits the main prologue and
never sets `st.float_ret`/`st.dec_ret` (only `lower_proc` does), so a procedure-only
file gets the main-block entry shape and a FLOAT-returning one is misrouted into the
integer path.  Q1 previously died with a bare `Failure("int_of_string")`; it now refuses
loudly with `[TBD]` naming the literal and the cause.  Blast radius of the eventual
fix is exactly zero for existing work: **no gate specimen lacks `options(main)` (0 of
390)**, and the corpus population is 25 files with main and 4 without -- `A`, `ACK`,
`ACKTST`, `MPMCALLB` -- none of which is accepted, all four of which need this route.

---

## C136b — what else the procedure-only-module goldens pin (E2E-11 step 5)

Added to C136 after implementing the route, because nine DR objects disagreed with
three of my assumptions and each disagreement is now a byte-exact specimen:

1. **END-PROGRAM's operand SEGMENT is the only header field that tells the two file
   kinds apart.** Every MAIN specimen ends `LINK-END-PROGRAM code 0000`; a
   procedure-only module ends `LINK-END-PROGRAM abs 0000`. The *value* is 0 in both
   cases, so nothing else in the stream would reveal it -- a code-path guess about
   "which address END-PROGRAM names" would have been invisible to every other check.
2. **`stop;` inside a module emits its in-place `CALL ?STOPX` and STILL gets no
   epilogue CALL** [Q6, `golden/e2e148/Q6`]: DEF-CODE-SIZE 0016 lands on the second
   byte of the statement's own CALL operand. So the epilogue suppression is about
   the file kind, not about `stop_seen`.
3. **A module body ending in STOP gets NO trailing implicit RET** [Q6 vs Q2]. Q2
   (no RETURNS, assignment last) does get one. The eight earlier no-RETURNS probes
   (E25A/E24A/E25D/...) contain no STOP, so this is a new condition, and I scoped it
   to the shape DR actually pinned: whether a *nested* procedure ending in STOP also
   loses its RET remains unprobed, and nested lowering keeps the byte it always
   emitted.
4. **RETURNS(FIXED DEC) on a module uses the same exit family as a nested DEC
   procedure** [Q9, `golden/e2e149/Q9`]: `CALL ?QI15D / MVI A,<scale> / CALL ?QDDSL
   / JMP ?DCRET`. My earlier refusal assumed the nested exit might not carry to a
   top-level module. It carries unchanged. Q8 -- the same shape with a *plain FIXED*
   formal -- also compiles under DR but needs FIXED->DEC conversion my lowering does
   not have, so it stays a `[TBD]` refusal registered in the negative panel as
   my-gap.
5. **A deduped formal's declared size is not its cost, for the outermost block too.**
   DR's A has DATA AREA 0006 = a 4-byte MBF pool cell + `x`'s **2-byte pointer cell**,
   not `declare x float`'s 4-byte cell. Q5 (formal + extra local) and Q7 (two formals)
   pin that locals land immediately after the pointer cells. Charging the declared
   cell gives +2 (fixed) / +4 (float) and shifts every later address, which is the
   silent-shift failure class of C129, not a size-report nuisance.

## C137 — LINK 1.31 does not search for cross-module PL/I references; it writes a .COM anyway (toolchain, E2E-11 step 5)

**Statement.** With `A.REL` and `E29F.REL` both present on `D:`, `LINK D:E29F`
(companion NOT named) reports

```
UNDEFINED SYMBOLS:
A
ABSOLUTE 0000 / CODE SIZE 1B13 / ...
```

and **still writes E29F.COM** (7808 bytes). That .COM runs, prints nothing, and
exits rc=0. `LINK D:E29F,D:A` resolves `A 0208` and produces a *different* 8320-byte
.COM that runs correctly. This is why DR's own corpus instructions for the
MPMCALLA/MPMCALLB pair read `link mpmcalla,mpmcallb,mpmdio` -- every object is
named. It is a toolchain rule, not a code-generation rule.

**Evidence.** `golden/e2e153_l/link-batch0.transcript.txt` (unnamed, UNDEFINED
SYMBOLS: A), `golden/e2e153_l4/link-batch0.transcript.txt` (named, `A 0208`), and the
paired run outputs `golden/e2e150dr/E29F.output.txt` (1 byte, silent) vs
`golden/e2e151dr/E29G.output.txt` (correct value after the link form was fixed).

**What the harness got wrong, stated accurately (E2E-12 correction).**  I first wrote
that the `[:120]` status slice "cut the report off immediately after `UNDEFINED
SYMBOLS:', so the link looked clean.  That is not supportable: the surviving broken-link
transcript (`golden/e2e153_l3`) puts the symbol name at character 110 -- INSIDE the old
cap -- and the transcript that produced my original reading was overwritten when I
re-linked with `--reuse`.  What I observed was real (a status line that appeared clean
while LINK was reporting an unresolved reference), but the mechanism I attributed it to
is not pinned by any surviving artifact.  The claim that stands is the operational one:
**the harness's verdict must not depend on how much of LINK's report it chooses to
display.**  `parse_undefined()` therefore reads the FULL segment, the display cap is
400, and `oracle/linkrun.py selftest` pins both -- including a synthetic segment whose
symbol sits at character 263, beyond any display window.  Any link-stage acceptance that
checks only "did a .COM appear" accepts a broken program; that part was, and remains,
the actual defect.
---

## C138 — OPTIONS(STACK(n)) is exactly one 16-bit operand in the MAIN prologue, and it is the runtime stack (E2E-12)

**Statement.** For a block carrying `OPTIONS(STACK(n))`, DR emits the main prologue
`LXI B,dade` with `dade` = n (little-endian), where the no-option default is `0200`
(512).  Nothing else in the record stream changes.  Measured over twelve DR objects:

| probe | option | prologue |
|---|---|---|
| ST1 | `options(main)` | `01 00 02` = 512 |
| ST2 | `main,stack(2000)` | `01 d0 07` = 2000 |
| ST3 | `main,stack(100)` | `01 64 00` = 100 (leading zero byte is real) |
| ST12 | `main,stack(1)` | `01 01 00` = 1 |
| ST4 | `main,stack(65535)` | `01 ff ff` = 65535, **accepted** |
| ST6 | `main,stack(0)` | `01 00 02` = **the default, not 0** |
| ST9 | `options(stack(2000),main)` | same as ST2 (order-independent) |
| ST15 | + nested RECURSIVE procedure | same operand; shadow/SVBLK untouched |
| ST7 | procedure-only **module**, `options(stack(2000))` | **no trace at all** |
| ST5 | `stack(65536)` | DR pass-1 ERROR, **no .REL** |
| ST10 | `stack(2*1000)` | DR pass-1 ERROR, **no .REL** |

ST7 vs ST11 (the same module with no STACK) are **byte-identical**: on a file with no
main prologue DR silently drops the option -- it is not an error, and there is no other
field where the value can hide.

**It is the runtime stack, measured semantically.** Same source, only the option
differs, recursion depth varied (`f(n) = n * f(n-1)`, RFACT's shape):

| probe | stack | depth | result |
|---|---|---|---|
| V3 | default 512 | 400 | `Free Space Overwrite` |
| V6 | 600 | 400 | `Free Space Overwrite` |
| V4 | **2000** | 400 | completes, prints |
| V5 | 2000 | 1200 | `Free Space Overwrite` |
| U6 | default 512 | 300 (U-shape) | `Free Space Overwrite` |
| U1/U5 | 2000 | 100 / 300 | completes |

`Free Space Overwrite` is DR's own runtime diagnostic (PLILIB), i.e. the stack grew into
free space.  So the operand selects a runtime allocation limit, and choosing it wrongly
changes whether a program runs -- which is why byte parity on this operand matters beyond
appearance.  Depth 400 of this frame shape needs >600 and <=2000 bytes.

**My status.** Implemented as one operand selection plus DR's validation boundary
(>65535 and non-literal refuse, mirroring "no .REL"; 0 means default).  ST1-ST4, ST6-ST9,
ST11, ST12, ST15 are byte-exact (13 specimens), and V1-V6 are byte-exact with the
mine-built .COM byte-identical to DR-built and identical runtime output.

## C139 — SILENT MIS-COMPILE: FIXED ADD with a call on the right and a value to preserve on the left (E2E-12)

> **RESOLVED by C141 (E2E-13).**  The rule below ("the correct lowering is unknown", "DR
> evidently does not reload the left value from the declared cell") is superseded: DR loads
> the left operand AFTER the call, from its own activation's shadow cell, and my defect was
> parking the value in DE with `XCHG`.  Implemented; U1 now prints 5050.  Where this entry
> says "unknown", read C141.  The wrong-value artifacts are kept as evidence.

**Statement.** `return (t + sum(n-1))` -- a FIXED addition whose right operand is a
procedure call and whose left operand reads a variable that must survive the call --
is compiled by my lowering into a sequence that **runs and computes the wrong number**.
This is not a representation difference:

```
U1  t = n; return (t + sum(n-1));   sum: procedure(n) returns(fixed) recursive
      DR-built  : sum(100) =  5050     (correct: 100*101/2)
      mine-built: sum(100) = 12488     (WRONG, exit rc=0, no diagnostic)
```

Byte-level the divergence is small and consistent: mine emits an extra
`XCHG / LHLD <cell>` (with a RELOC DATA word) and uses `LXI H,imm` where DR uses `LHLD`,
i.e. my lowering reloads the left operand from a cell that does not hold the per-
activation value DR uses.  DR evidently keeps the left value where the recursive
activation cannot clobber it; I do not know where, and guessing is what produced 12488.

**Controls -- the guard is narrow, not general.** All three of these are byte-exact, so
the defect is specific to ADD-with-call-on-the-right:

* `return (n * f(n-1))` -- MUL, call on the right -- byte-exact [RFACT, FFACT, V1-V6].
* `return (f(n-1) + t)` -- ADD, call on the **left** -- byte-exact [W5].
* `dummy = f(n-1); return (t + 1)` -- the local read only after the call result is
  stored -- byte-exact [W6].
* `t = 1; return (t + f(n-1))` -- diverges [W3], which rules out "copying the parameter
  is what went wrong": a literal-assigned local fails identically.

**Action taken.** The shape now refuses with `[TBD]` and the evidence (guard in
`lower_hl`'s general ADD arm; U1/W1/W2/W3 registered as my-gap negatives), because
emitting a plausible sequence with a wrong value is the worst failure class in this
project and had no diagnostic at all.  Correct lowering is an open milestone.  SUB with
a call on the right is **not** covered: my first evidence for it (S1/S6) turned out to be
confounded by C140, so it needs a clean control before a rule is written.  **Update (E2E-13):** the clean control was P6, which showed DR's route is PUSH H / POP D
  (C141) and that my XCHG route was conditionally wrong, not just byte-different; P6 is
  refused for record-order reasons (C142).

---

## C140 — DR strength-reduces `x + 2` to `INX H / INX H`; my peephole refusal does not cover that position, so the divergence passes silently (E2E-12)

**Statement.** Adding the literal 2 to a FIXED value lowers to two `INX H` (0x23 0x23),
not to an arithmetic ladder.  Independently visible twice this session:

```
E27C  p2 body (n = n + 2):   ... 23 23 eb 72 2b 73 c9      [already pinned]
C1    g body (return n + 2): ... 23 23 c9                   [golden/e2e172/C1]
                              mine:  eb 21 02 00 19 c9      (XCHG / LXI D,2 / DAD D / RET)
```

Both sequences compute the same number, so this is a **representation** divergence --
value-correct, byte-wrong.  My compiler has a documented set of DR peepholes it refuses
rather than approximates ([E2E-9 step 6]: "all four shapes below are ones MY lowering
gets WRONG ... so they fail loud here"), and `+1` is handled (`INX H`, N304).  What is
missing is **coverage**: the `+2` case inside a nested procedure's `RETURN` expression
fell through the refusal and emitted the general ladder.

**Why it matters more than the byte count.** Every S/C probe I wrote used a callee with
body `return (n + 2)`, so all six "differ" -- and for a while that looked like evidence
that ADD-with-call-on-the-right was not the trigger (C139).  It was this peephole, and a
control (C4: same shape, callee body `return (n * fq(n-1))`, byte-exact) is what
separated the two.  Recorded as its own claim so the confound cannot be re-read as a
finding: **a divergence must be attributed to one cause before it is cited as evidence
for another.**

---

## C141 — RESOLVES C139: DR never parks a value in a register across a call (E2E-13)

**Statement.** For FIXED arithmetic whose operand list contains a procedure call, DR has
exactly three ways to get the other operand's value into the add/sub/mul, and none of them
is "keep it in DE".  Established from six `$L$C$D` listings (batch `golden/e2e174`,
tools/linecode.py) and confirmed by 47 byte-exact objects, not inferred from output:

| shape | DR's instruction sequence | probes |
|---|---|---|
| `var + call` | `<arg eval ; LXI H,result ; CALL> ; XCHG ; LHLD var ; DAD D` | P1, P2, P3, P10, P11 |
| `lit + call` | `<call> ; (INX H)*lit` — commutes AND strength-reduces | P4 |
| `(a+b) + call` | `<left> ; PUSH H ; <call> ; POP D ; DAD D` | P5 |
| `call + call` | `<first call> ; PUSH H ; <second call> ; POP D ; DAD D` | P12 |
| `var - call` | `LHLD var ; PUSH H ; <call> ; POP D ; CALL ?IS22N` | P6 |
| `call - var` | `<call> ; XCHG ; LHLD var ; CALL ?IS22N` | P7 |
| `var * call` | `<call> ; PUSH H ; LHLD var ; POP D ; CALL ?IM22N` | P8 |

The load-after-call case is *sound*, not merely different: a recursive procedure's locals
live in that activation's own `?SVBLK` shadow block and `?RSBLK` restores them, so
re-reading `LHLD T` after the nested call yields this activation's `t`.  DR does not push
the value because the read is cheap; it pushes when there is nothing left to re-read (a
compound expression, or a second call), and for SUB it pushes because `?IS22N` computes
`DE - HL`, so the **minuend** must be in DE once the call is done -- there is no later load
to defer the value into.  That is why ADD and SUB differ on the same shape.

**My defect, precisely.** `lower_hl`'s general ADD arm did
`<load left> ; XCHG ; <call> ; DAD D` -- DE carries the left value across the call.  Every
DR-compiled callee destroys DE: its prologue runs `LXI D,<shadow>` and the pointer-formal
copy ladder is `MOV E,M / INX H / MOV D,M / XCHG` (both visible in my own object at
code 013C-0150 of `golden/e2e169ml/U1.COM`).  Hence the silent 12488.

**Correction of my build, as executed.** U1 (`t = n; return (t + sum(n-1));`, recursive):

```
mine-built, before : sum(100) = 12488   (golden/e2e169mr/U1.output.txt, kept as evidence)
mine-built, after  : sum(100) =  5050   (golden/e2e180r/U1.output.txt) == DR-built  5050
independent witness: 100*101/2 = 5050
W1 f(8)=36  W2 f(8)=36  W3 f(8)=8   (36 = 8*9/2; W3 sets t=1 per level so f(8)=8) == expected
```

P-series witnesses (mine == DR == independent arithmetic, all 12):
P1 5050 (=100·101/2) · P2 55 (=10·11/2) · P3 109 (=100+3·3) · P4 10 (=1+9) ·
P7 -91 (=9-100, signed) · P8 900 (=100·9) · P10 21 (=9+12) · P11 17 (=7+10) ·
and P5/P6/P9/P12 -- 21/91/113/21 -- which match too even though those four still refuse
on .REL record order (C142).

**Status.** ADD-with-call-right where the left is a simple variable, a literal, or a
parenthesized one is implemented and byte-exact; U1/W1/W2/W3 (previously loud refusals) are
now SPECIMENS.  P5/P12 (left needs parking) and P6 (SUB) are still refused -- see C142.
SUB-with-call-right is a special case of the hazard worth naming: my *previous* route was
not merely byte-different, it was conditionally wrong, because any callee that touches DE
corrupts the parked minuend.  P6 shows a value-correct instance (91) with a callee that
happens not to disturb the arithmetic, which is exactly the kind of case that must not be
mistaken for a working route.

## C142 — DR plans an expression's anonymous cells BEFORE emitting any of its code (E2E-13)

**Statement.** For a call inside an arithmetic expression, DR's bit-packed stream places
the cell-allocation records (`LINK-SET-LC data` + the operand `RELOC`) ahead of the code
records of the *whole expression*, and numbers cells in plan order.  I allocate at the point
of use.  Consequence: identical instruction bytes, different .REL.

Four probes demonstrate it, each with code bytes IDENTICAL to DR and the correct executed
value (`golden/e2e180r` vs `golden/e2e181r`), refused rather than passed:

* **P5 `(t+u)+g(3)`, P6 `t-g(3)`, P12 `g(3)+g(4)`** -- record order.  DR's stream around
  code 0051: `LINK-SET-LC data 0009 ; RELOC data 0x1 ; LINK-SET-LC code 0051 ; DATA 2a...`
  Mine emits the same records but after `DATA 2a / RELOC data 0x7 / DATA e5` [reldump diff].
* **P9 `t + g(h(2))`** -- cell numbering.  DR: outer call's result 000B, inner call's result
  000D, outer argument 000F; mine has 000D and 000F interchanged.  Read off the listings:
  `LXI H,* A(000D) / CALL H / SHLD * A(000F) / LXI H,* A(000B) / CALL G` -- the outer result
  cell is smallest, so result cells are planned outer-first and argument cells come later.
  So the rule is: **allocate a call's result cell, then descend into its arguments.**

**Evidence class, stated plainly.** This milestone made me separate four properties that
`cmp` had been bundling: (1) semantic correctness of the executed value, (2) DR
instruction-selection identity (the code bytes), (3) .REL serialization identity (record
order + cell numbering), (4) link/runtime validity.  P5/P6/P9/P12 are (1)+(2)+pass, (3)-fail.
The acceptance criterion is (3), so they refuse.  The fix is to plan cells before emitting --
a change in the pool/dedup order, which ARCH-0 identified as the riskiest property in the
program and which I did not attempt here; 477 byte-exact specimens depend on that order.

## C143 — DR's small-constant arithmetic: `INX H`/`DCX H` repeated, with TWO thresholds depending on the route (E2E-13)

**Statement.** Adding constant k to a 16-bit value held in HL lowers to repeated
single-byte increments up to a threshold, then to `LXI B,k ; DAD B`.  The threshold is
route-dependent, which is only visible because both routes were probed at k=4:

| route | repeat while | then | evidence |
|---|---|---|---|
| self-update `v = v + k` (hl_bias path) | k <= 3 | `LXI B,k ; DAD B` | K1-K4, X1, S5-S8, E22A02-A16 |
| any other context (result returned or stored elsewhere) | k <= 4 | `LXI B,k ; DAD B` | R4/R5, T2/T4/T8, X2/X3, N7 |
| subtraction, self-update | k <= 3 | `LXI B,two's-complement ; DAD B` | K6, E22B01-B08 |
| subtraction, other | k <= 4 | same | M1-M4, N4/N5, M6/M16 |

Corollaries, each measured:
* `k = 0` emits nothing at all (M0: load ladder then RET) -- so `n + 0` is not `INX H`.
* Literal on the left commutes: `return (2 + n)` is byte-identical to `return (n + 2)` (K9 vs K5).
* The reduction is applied **per operator, not netted**: `return (n - 2 + 3)` emits
  `DCX H DCX H INX H INX H INX H` (M7), not one `INX H`.
* It is not restricted to nested procedures or RETURN expressions: main-level `r = x + 4`
  gives `LHLD X / (INX H)*4 / SHLD R` (T4) and after a call, `return (g(n) + 4)` gives
  `CALL / (INX H)*4` (N7).  This supersedes C140's framing -- the `+2` sequence was never
  about nested procedures.

**My status.** Implemented (`hl_bias_free` for the non-self route, `hl_bias` unchanged for
self-update, `const_sub` extended past 4 to DR's two's-complement `LXI B` form).  All 32
constant probes are byte-exact, including C1/C4/C7 from the previous batch, which DIFFERED
before this milestone: C140's "value-correct but byte-different fallback" is gone -- there
is no fallback left for these shapes, and the guard that used to catch some of them is gone
too.

## C144 — Retracted: "DR's 16-bit zero test uses XRA" was my disassembler's bug, not DR's (E2E-13)

**Statement.** While reading U1 I found byte `B6` where DR's listing prints `ORA M`, and my
hand-written 8080 table decoded `B6` as XRA -- which would have made DR's `if n = 0` test
wrong for every value whose two bytes are equal (257, 514, ...).  I did not run that
conclusion past evidence, and it was false: DR's own listings, cross-checked against linked
images over 60 programs, print `ORA` for 0xB6 and `XRA` for 0xAF, which agrees with this
project's parity-derived rules (`CMP M = 0xBE`, `SBB M = 0x9E`, `0xAF = XRA A`).  The ALU
family order is ADD 0x80, ADC 0x88, SUB 0x90, SBB 0x98, ANA 0xA0, **XRA 0xA8, ORA 0xB0**,
CMP 0xB8; I had ORA and XRA transposed.

**Method adopted after this, and it is the reason the error died in one step.** The
disassembler's table is now *learned* from DR rather than written from memory: parse each
program's `$C` code lines, take the byte at (file offset == code address) in its linked
.COM, and record opcode -> printed mnemonic and opcode -> address delta.  Candidate image
offsets are accepted only if every `LXI` line's byte is one of 01/11/21/31 and every `CALL`
line's byte is a CALL opcode -- two facts pinned independently by byte-exact goldens.  The
result is 43 opcodes with **zero** printed under two mnemonics, and anything unobserved
prints as `DB nn` instead of being guessed.  DR's zero test is correct; the only defect in
this story was mine.

## E2E-14 (C145-C146): where DR puts anonymous call cells, measured record by record

C145. **DR numbers a procedure section's anonymous call cells in TWO PHASES: every call
site's DESCRIPTOR slots first (2 bytes per argument, in pre-order over the sites), and only
then the EXPRESSION-argument VALUE cells.** Evidence [19 DR programs, `$L$C$D` listings +
raw `.REL` record bits]: D3 `t + g(h(k(2)))` numbers descriptors 0013(g) < 0015(h) <
0017(k), then the value cells 0019, 001B; P9 `t + g(h(2))` numbers g.slot 000B, h.slot
000D, then g's argument value cell 000F. My `bind.ml` allocated `(slot, temps)` per site in
a single pass, so `g`'s argument cell landed at 000D *ahead* of `h`'s descriptor -- a pure
numbering inversion, with identical record positions. Fixing the numbering makes **P9
byte-identical to DR** with nothing else changed, and P1/P3/P11 stay byte-identical; the
whole 477-specimen corpus passes with the change applied in an isolated `git worktree`
before it was adopted [golden/e2e174/P9]. Lesson: a divergence in *addresses* and a
divergence in *record order* look identical in a diff and are fixed in completely different
places -- I nearly shipped a stream-reordering mechanism for what was an eight-line
allocation-order change [E2E-13's own diagnosis of P9 was wrong on this point].

C146. **DR writes a call's descriptor record when its CONTENT becomes knowable, which for a
literal-or-declared actual is at plan time -- before the enclosing expression's code -- while
I write it at point of use; this is NOT yet fixed and the shapes that need it stay refused.**
Measured over the same corpus: P6 `t - g(3)` DR@bit 1846 vs mine@1883 (same cell number,
reference at code 0055 in both); P12's second call 1958 vs 2023; D1 `t - u - g(3)` 2031 vs
2208; D11's 2nd/3rd calls 2186/2255 vs 2250/2384. For the DEFER route the call's code *is*
the expression's first code, so plan-time and at-reference coincide and my at-ref emission
is byte-exact [P1-P4, P7-P11, D3, D9] -- which is why the divergence surfaced only in PUSH
routes and multi-call chains. Discriminating probe pair: P3 vs P6 share the identical
alloc bit 1846 [D3 trace], so DR's placement is anchored to the expression's first code
record, not to the `LXI H`. What remains unresolved and is therefore NOT claimed: whether
expression-argument VALUE cells are numbered in pre-order over sites or at the producing
store (D3's numbers are consistent with both; D4/D5, which would discriminate, hit an
unrelated refusal -- MUL by literal 2 in a RETURN/expression context -- first). Migration
proposal (not attempted): emit the descriptor word (`SET-LC data slot+2i` / RELOC word /
`SET-LC code`) in the PUSH-route arms before lowering the left operand, or equivalently
lower the right operand with code bytes captured and data/link records live, then replay.
Both are confined to arms currently behind `[TBD]` guards, so they carry no regression risk
by construction -- but they need a capture/replay path through `reloc` and `link`, which is
the same mechanism class as ARCH-1, so it is proposed rather than done.

C147. **A gate that passes is not a gate that tests what you changed.** Applying only the
numbering fix kept 477/477 green -- because no accepted shape has two call sites in one
section where the old and new orders differ, i.e. the corpus was silent on exactly the
property I was editing. The property only became observable once P9 was retired from the
negative panel, which is why P9's byte-identity (not the green gate) is the evidence, and
why the green gate is the *non-regression* evidence rather than the *correctness* evidence
for the change. Corollary: my narrowing of the nested-call guard to "all actuals are
literals" silently over-refused U1/W1-W3 (`sum(n-1)` has NO nested call at all), which the
gate caught as COMPILE-FAIL within 90 seconds -- the condition had to be `nested AND
not-literal-chain`, not `not-literal-chain`.

## E2E-15 (C148-C154): small-constant multiplication, and two silent mis-compiles found

C148. **DR's FIXED-BINARY multiply by an integer constant is strength-reduced by VALUE, and
the rule is context-free.** Measured over 32 probes (e18src/MB1-MB46,
golden/e2e186-e2e198b):
    k = 1          -> the operand alone (`x * 1' elides; [MB6, P044])
    k = 2^m, m>=1  -> m copies of `DAD H'   (2 [MB1], 4 [MB4], 8 [MB19], 16 [MB21])
    2 <= k <= 32767, not a power of two
                   -> `LXI D,k ; CALL ?IM22N' (3,5,6,7,1000,32767 [MB3/5/20/22/29/30])
    k >= 32768     -> DECIMAL POOL path (`PUSH H / LXI H,*S / MVI A,p / ?DLDOP / ?QDI15 /
                      POP D / ?IM22N') [MB31 k=32768 vs MB30 k=32767 -- the boundary is the
                      signed-16-bit range, NOT a digit count]
    k = 0          -> `MOV L,H' [MB7 `n * 0', MB8 `0 * n', byte-identical to each other]
The identical form appears in an assignment [MB1], a self-update [MB9], a compound operand
[MB10/MB26], a PUT-LIST item [MB12], an IF condition [MB13], a CALL ARGUMENT [MB14], a
chained multiply [MB17 `n*2*2' -> two DAD H, not folded], a width-converting store [MB18]
and a RETURN over a pointer-deref formal [MB16, where the deref prologue `MOV E,M / INX H /
MOV D,M / XCHG' precedes the same `DAD H']. The constant commutes: `2 * n' and `n * 2' are
byte-identical [MB2 vs MB1], as are `3 * n' and `n * 3' [MB27 vs MB3].
**My previous emitter used `PUSH H / LXI H,k / POP D / CALL ?IM22N' (5 bytes) for a literal
right operand where DR uses `LXI D,k' (3 bytes)** -- the two extra bytes were measured at
code 0014: mine E5 21 03 00 D1, DR 11 03 00 [MB3 record stream]. `?IM22N' multiplies DE x HL,
so the operand-to-register assignment is free, which is why DR skips the rotation. 29 of these
probes are now byte-identical specimens. C148 also records that **DR's own `* 0' lowering is
suspicious**: `MOV L,H' copies H into L and does not produce zero, so I refuse rather than
copy an unverified result.

C149. `op_jz = 0xc4` DELETED from codegen.ml: it was referenced nowhere, and 0xC4 is CNZ
while JZ is 0xCA. The 0xCA bytes at the skip sites stay RAW literals on purpose -- [C072]/
[R910] record that DR's listing LABELS that byte JPE while the .REL byte is CA, so naming the
constant `op_jz` would assert a meaning the evidence explicitly declines to settle. A wrong
but unused name is worse than a raw byte with a comment.

C150. **DR's ADD/SUB operand-parking rule is SYNTACTIC, not register-analytic: whenever the
RIGHT operand is compound, the LEFT is parked with `PUSH H ... POP D`; when the right is
simple, `XCHG` is used.** [MB34 `n + (n*3)`, MB35 `(n+1) + (n*3)`, MB37 `n - (n*3)` -> PUSH
H/POP D; MB36 `(n*3) + n` -> XCHG]. Decisively, MB28 `n*3 + n*2` takes PUSH H even though its
right operand (`DAD H') would NOT have destroyed DE, which rules out a liveness-based reading.
**My unconditional XCHG was a MIS-COMPILE, not a byte preference**: `?IM22N' overwrites DE, so
the parked left value was gone and the expression returned only the RIGHT operand. Measured at
HEAD 8c849f9: mine printed 21 where DR prints 28 for `n + (n*3)', 21 vs 35 for `n*2 + n*3',
-21 vs -14 for `n - (n*3)' [golden/e2e195r vs golden/e2e196r, per-name output files read
verbatim]. This path was reachable BEFORE this milestone via `*3', which the multiply guard
never refused -- the defect is pre-existing, and it is the third instance of the C139 family
(a value left in a register across an operation that destroys it).

C151. **`elide_fixed_zero` rewrote `x op 0 -> x' without testing the operator**, so
`m = n * 0' silently became a copy of n (MB7 emitted `LHLD n / SHLD m' and printed 7 for
n=7) and `m = n / 0' never reached the division-by-zero refusal at all -- it became a copy of
n. Now restricted to ADD and Sub, which is what the evidence supports (`x - 0 = x' [T5/T6],
`x + 0 = x' [N56]). This is a fourth silent defect found by probing an adjacent feature: I
only saw it because MB7 was expected to refuse.

C152. **A string literal repeated in one program is pooled ONCE by DR and my emitter does not
produce a matching data area even after dedup'ing the write; the shape refuses.** MB40 is the
clean discriminator: `put skip list('W', n);' twice with PLAIN VARIABLES only -- no multiply,
no call, no expression -- and mine emits DEF-DATA-SIZE 8 against DR's 7, relocating the first
automatic at 2 instead of 1 (every subsequent variable shifts by one byte). Adding
content-keyed string dedup (mirroring the `fl_pool`/`dec_cells` precedent already in the file)
removed the duplicate WRITE (141 -> 139 records, matching DR's count) but NOT the size
difference, so the residual rule is uncharacterised and I refuse rather than emit. The defect
is PRE-EXISTING (reachable at 424eaa2) and was newly exposed only because the probes reached
it; MB12/MB38/MB39 hit the same cause through different items, which is what proves the cause
is the pool and not the arithmetic. MB41-MB43, which would have localised it further,
produced no DR object at all and therefore carry no verdict.

C153. **The C145 nested-call allowance was too broad and is tightened to the measured class.**
With multiplication working, the D-series could finally be BUILT: D3 `g(h(k(2)))' and D4
`g(h(2),k(3))' compile and produce bytes that DIFFER from DR, while D5 `t + g(2*h(3))' and P9
`t + g(h(2))' are byte-identical. So the accepted shape is exactly ONE nested call, depth <=
2, every actual a literal, every call single-argument; anything deeper or wider refuses with
its reason named. Emitting a program I know differs in bytes is not acceptable even when it
runs to the right number -- and the previous refusal was justified but imprecise, which is why
it hid the fact that my allowance covered shapes I had never measured.

C154. **Registration-list collisions are now prevented mechanically, in the gate's own
pre-flight.** `registration_audit()` statically flags any key written twice inside one
dict-literal/`.update()` block (the E2E-12 shape, where five long-standing specimens were
silently replaced) and at runtime forbids a name being both a byte-exact SPECIMENS entry and
a REJECTS entry (the E2E-14 shape, P9 anchored into the wrong block) and requires
REJECTS/NEG_META symmetry (so a verdict explanation can never be orphaned). It was
negative-tested against all three induced shapes before being wired in, and it correctly stays
silent on the clean file -- an instrument that always passes is not an instrument.

### Retractions and corrections in this milestone

R1. **E2E-14's "P5 has a distinct code-address mismatch" is RETRACTED as a production
finding.** DR compiles `return (t + u + g(3))' as `LHLD T / XCHG / LHLD U / DAD D / PUSH H /
LXI H,*A(000B) / CALL G / POP D / DAD D' [golden/e2e174/P5/P5.PRN] -- the call's LXI at 005F.
My measurement showed 0056 because the measurement bypass replaced `add_left_needs_push' with
`false', which sent the expression down the DEFER route (call first). The mismatch was an
artifact of my own instrumentation, not a second defect. A bypass that changes routing is a
change of subject, and I read it as a finding.

R2. This also SHARPENS C146: with the code routes confirmed identical for P5/P6/P12, the only
remaining divergence is WHEN the descriptor record is written -- DR writes a call's descriptor
before the enclosing expression's first code record even when the descriptor is referenced
later (P5's `SET-LC data 000B' at bit 1892 precedes code 0056). So the migration is a
record-timing change, not an instruction-order change. It still needs a capture/replay path
through `reloc`/`link` (ARCH-1 class) and is still NOT attempted; P5/P6/P12/D1/D11/D12 keep
refusing with reasons named.

## E2E-16 (C155-C158): C152 resolved, and C148's "*0 is a DR defect" claim refuted

C155. **THE LITERAL-POOL RULE, ESTABLISHED AND IMPLEMENTED -- C152 IS CLOSED.** DR keeps ONE
pool cell per DISTINCT string CONTENT, allocated at first use, contiguous from data address 0;
a repeated content reuses the earlier address and consumes no further bytes.  Measured on 19 DR
probes (e19src/PL1-PL13, PL16-PL21, goldens golden/e2e199-e2e202) at BYTE level, not by totals:
  PL3  'W','V'          -> 57 56              (two cells)
  PL4  'WW','WW'        -> 57 57 at 0000      (ONE 2-byte cell, not two 1-byte cells)
  PL5  'W','WW'         -> 57 57 57           (three bytes, contents differ)
  PL6  'WW','W','WW'    -> 0000:WW 0001:W, the repeat of the FIRST cell costs nothing
  PL13 'AB','A'         -> 41 42 41           (key is EXACT CONTENT; a shared PREFIX does not merge)
  PL10, PL11, PL18-PL20 -> char stores share the same table as PUT items (cross-context dedup)
  PL7, PL9, PL12        -> three occurrences / identical statements / repeats inside ONE put list
                           all pool a single byte
THE CAUSE of C152 was not the allocator -- `pool_str' already deduplicated by content. It was the
prescan DEMAND (`prescan_stmt`'s Sput/char-store arms), which summed `String.length v' per
OCCURRENCE. Demand reserved two cells, lowering wrote one, so the data area was oversized by the
duplicate byte and every automatic variable shifted up by one. MB40's 7 decomposes exactly:
'W' (1) + n, m and nested f's j (6). Fixed by adding `pdec_str_cell cx v`, which returns 0 for a
content already demanded -- the same shape `pdec_dec_cell` [R614] and `pdec_fl_expr` already use,
so all three literal classes now dedup identically at demand and layout.
THE EMPTY LITERAL IS A GENUINE EXCEPTION, measured not inferred: PL17 (two PUT lists containing
'') emits a SECOND `SET-LC(data,0000)` record with NO DATA bytes -- DR registers a zero-length
pool BLOCK per occurrence even though the address is shared -- while PL11 (two non-empty stores)
registers ONE block. My data-area writer therefore emits an explicit SET-LC for any block after
the first, including one at address 0 (previously only `addr > 0' got a record).
NOT extrapolated: PL15 (a literal repeated inside a CONCATENATION) and PL14 (a repeated literal
in a PUT EDIT) produced NO DR object (diag/NOT IMP), so concat keeps its per-occurrence behaviour
on BOTH sides -- demand and lowering -- rather than a dedup I cannot verify. Mixing dedup'd demand
with non-dedup'd lowering is precisely the drift that caused C152, and it would have been invisible.
MB12/MB38/MB39/MB40 are retired from the negative panel with their own goldens and are now
byte-identical specimens. A demand/layout INVARIANT now aborts codegen if prescan bytes !=
lowering bytes (see C158).

C156. **C148's "`MOV L,H` does not produce zero, probable DR defect" is REFUTED.** DR's
multiply-by-zero is CONSTANT-PROPAGATED, and the emitted instruction depends on the literal value
it already knows is live in HL. Executed DR-built programs (golden/e16mzr) return ZERO for every
value tested -- 7, 0, 256, 257, -5, and `0 * n' -- against the mathematical expectation, which I
wrote down before reading the outputs. The measured instruction table for `m = n * 0;' with n
assigned a literal:
    HL == 0000            -> NOTHING, just `SHLD M'                    [MZ2 n=0]
    high byte == 0        -> `MOV L,H'  (0x6C)                         [MZ1 n=7, MZ6 0*n, MB7/MB8]
    high byte == 1        -> `DCR H'    (0x25)                         [MZ3 n=256]
    high byte > 1, low == 0 -> `MOV H,L' (0x64)                        [MZ8 n=512]
    both bytes non-zero   -> `LXI H,0000'                              [MZ4 257, MZ9 516, MZ5 -5, MZ10 65535]
n=512 is the discriminator that forces the propagation reading: a structural peephole could not
choose `DCR H' for 0100 and `MOV H,L' for 0200 -- both zero HL, but only one is correct without
knowing H's value. And the propagation is SHALLOW: MZ11 (`k = f(n); m = k * 0;') and MZ12
(`k = n; m = k * 0;') both get `LXI H,0000', so DR does NOT track a value through a variable copy
or a call -- only through the literal load that immediately precedes. The rule commutes [MZ6].
**The refusal is PRESERVED, not because DR is wrong but because reproducing DR here requires a
constant-propagation pass my compiler does not have**: I always `LHLD' the variable, so my bytes
differ for every propagated case and emitting a generic `LXI H,0000' would match only MZ4/MZ5/
MZ9/MZ10/MZ11/MZ12 and silently differ on MZ1/MZ2/MZ3/MZ8. That is a byte-identity decision for
the project owner, not a change to slide in under a "found a bug" story.

C157. **Content-dedup'd pool cells are READ-ONLY: no aliasing corruption, verified at runtime.**
PL25 stores 'W' into two DIFFERENT variables and prints each separately; PL26 stores 'W', puts the
literal 'W' with a variable, then re-stores the SAME variable with 'WW' and prints it. Both are
byte-identical to DR and both produce identical executed output in mine and DR (W/W and `W 7'/WW),
so sharing one cell cannot make a later store corrupt an earlier print. Without this check, C155
would have been a plausible-looking way to break values while keeping REL parity [C137].

C158. **Two instruments, both of which fired during their own milestone.** (a) `spec/INVENTORY.txt`
commits one row per panel entry -- name, kind, source, golden (or refusal source + reason) -- and
the gate aborts with a precise diff unless the live panel matches it; changes require an
intentional `--update-inventory` and a reviewed diff. It catches REMOVAL (my P9 case), ADDITION and
SUBSTITUTION (same name, repointed reference) -- the last being invisible to any count, and not
hypothetical: E2E-12's collision kept the panel's shape while replacing five specimens. It fired
live in this milestone on PL8/PL9 being repointed between golden tags, where the total did not move.
(b) a registered specimen with NO golden file is now FATAL (`GOLDEN-MISSING'), not SKIP: two
probes I mistagged were silently scoring as neither pass nor fail, which is how "verify DR actually
produced each reference object" gets violated without anyone noticing.

### Retractions in this milestone

R3. The "478 -> 509" totals in the E2E-15 note are corrected to the verified **510**: 509 was the
symptom of removing P9 from the panel, not a smaller milestone. `spec/notes/e2e15-multiplication-
and-parking.md` carries the correction inline rather than being quietly rewritten.

R4. C148's characterization of DR's `x * 0` as a probable DR defect is WITHDRAWN (see C156). I
read one instruction out of context -- `MOV L,H` -- and concluded the computation was wrong, when
the sequence is a value-selected zeroing idiom whose output is correct for every input I executed.
This is the C144 failure mode (learn DR's semantics from DR's artifacts) repeated in the opposite
direction, and the check that caught it was running DR's program instead of reasoning about its
assembly.

## E2E-17 (C159-C162): independent PLI-2000 probes -- arrays characterized, mixed DEC/BIN mapped, and a latent pool under-count found

C159. **DR's 1-D/2-D FIXED BINARY array model, fully characterized from 17 minimal probes
(AB1-AB17, golden/e2e216-e2e218) plus the independent PLI-2000 suite programs ARRAY.PL1 and
PASSARAY.PL1 (golden/e2e214).  DR compiles all of them with "NO ERROR(S) IN PASS 1/2"; NONE of
them compile in my compiler, which has no array declaration form at all.**  The rules:
  * `declare a(n) fixed` = n contiguous 2-byte cells in the automatic area.  AB1: `a(5)` occupies
    data 0000-0009 and the next variable `b` lands at 000A, so DEF-DATA-SIZE counts the whole
    array -- the array is NOT a pointer and there is no descriptor.
  * **Constant subscript -> a DIRECT reference with compile-time offset (sub - lb) * 2.**  AB3
    `a(3)` on `a(1:5)` is `LHLD A A(0000)+0004`; AB9 `a(5)` is `+0008`; AB4 `a(0)` on `a(0:3)` is
    offset 0.  Loads carry the offset in the instruction (`LHLD A+off`) -- no address arithmetic.
  * **Stores split by offset**: offset 0 uses the ordinary scalar store `LXI H,val / SHLD A`
    [AB1, AB4, AB11, AB12, AB15]; NON-zero offset uses `LXI H,A+off / MVI M,lo / INX H / MVI M,hi`
    [AB3, AB5, AB9, AB14] -- byte stores, little-endian.  So DR's scalar store path handles only the
    base cell and the general computed-address path takes over above it.
  * **Variable subscript -> computed address**: `LXI H,A+(lb-1)*size / PUSH H / LHLD i / DAD H /
    POP D / DAD D`, i.e. the element size is applied by `DAD H` (doubling) and the pre-bias is
    folded into the relocatable operand.  AB2/AB10/ARRAY.PL1 all agree.  The reloc is emitted as
    the *target address itself* (NUMS-2 -> `RELOC data 0x18` for A(001A)): DR expresses the negative
    offset by relocating against a lower address, there is no offset field in the record.
  * Read through a computed address is `MOV E,M / INX H / MOV D,M`; write is `MVI M,lo / INX H /
    MVI M,hi` (AB2 both directions).
  * Subscript EXPRESSIONS are evaluated in place: AB8 `a(i+1)` gives `LHLD I / INX H` inside the
    same ladder -- the C143 `+1 -> INX H` peephole applied to the subscript, not the value.
  * **2-D is ROW-MAJOR with the LAST subscript fastest**: AB13 `m(2:4,1:3)`, `m(1,2)` -> `+FFFC`
    = ((1-2)*3 + (2-1)) * 2 exactly.
  * **No bounds checking is emitted anywhere.** AB13's `m(1,2)` is out of range (first dimension
    starts at 2) and DR compiles it to a negative offset without a word -- and ARRAY.PL1 writes
    `nums(I)` over 1..10 with no check either.  Subscript validation is therefore NOT part of the
    generated code, which is a fact about the target, not an omission of mine.
  * **An array element passed as an actual is passed BY ADDRESS through the call descriptor**:
    AB7 `call p(a(4))` emits `LXI H,A+0006 / SHLD * A(000E) / LXI H,* A(000E) / CALL p`, and the
    callee's `x = x + 100` writes through -- so the descriptor cell holds the element ADDRESS, not
    the value, which is the same pointer-formal mechanism as C130, reached by a different route.
  * `static` arrays: AB5 places the array in the static area (`LHLD A S(0000)+0002`, an `S` cell,
    not an `A` automatic), confirming C114's `[statics][pool][automatics]` layout applies to whole
    arrays.
  * One element of a `char` array and arrays of FLOAT/DEC were NOT probed -- out of scope.
  NOT IMPLEMENTED.  Landing this needs a parser declaration form, bind-side sizing (an array's
  `size` must move the automatic offsets, which is exactly the layout code every accepted specimen
  depends on), and lowering for three address shapes.  The front-end risk is that `a(i)` ALREADY
  parses as a procedure CALL, so arrays and calls are distinguished only by what the name is
  declared as -- a bind-time decision, not a syntactic one.  That is real work and it is the right
  next feature, not a last-hour change.

C160. **`PROC` and `DCL` are DR-accepted abbreviations with no semantic content, and my parser was
missing `PROC`.** All four PLI-2000 originals write `proc options (main);` and DR compiles every
one [golden/e2e214]; probe AB17 (`proc`/`dcl`) is DR-byte-identical to AB16 (same program spelled
`procedure`/`declare`) [golden/e2e218].  `DCL` was already handled by the keyword alternatives at
the DECLARE site; `PROC` was not, so all four independent-corpus programs died with
`expected PROCEDURE after label` -- a parse crash, not a `[TBD]`.  Fixed as an alias in the keyword
test (`at_key_any`, plus the `expect_key` site) rather than a lexer rewrite, so `PROC` cannot drift
from `PROCEDURE` in some positions and not others.  Effect: those programs now reach codegen and
refuse loudly with the actual missing capability named [C159/C161], instead of failing before the
refusal discipline applies.  A parse error is outside the negative panel's contract, which requires
`[TBD]`; converting crashes into reasoned refusals is itself a coverage improvement.

C161. **DR's mixed FIXED DECIMAL / FIXED BINARY arithmetic converts the DEC operand IN PLACE and
then uses ordinary binary lowering -- mapped over 10 probes (CB1-CB10, golden/e2e219-e2e220), all
compiled by DR, and this is genuinely new: what I already had is DEC->INT for a DIRECT operand
(`i = d`, R506) and pure-DEC arithmetic (E2E-6/E2E-7A), neither of which covers `d + b`.**
    conversion:  LXI H,d ; MVI A,p ; CALL ?DLDOP ; CALL ?QDI15   -> HL = 16-bit value
    p is the SOURCE decimal's precision: 03 for dec(3), 05 for dec(5) [CB1 vs CB7]
    DEC on the LEFT  -> XCHG route   [CB1 d+b, CB3 d-b]           (C150: right operand simple)
    DEC on the RIGHT -> PUSH H/POP D [CB2 b+d, CB4 b-d]           (C150: right operand compound)
    MUL with a DEC operand -> DR parks the LEFT with PUSH H even though the right operand is a
        plain `LHLD b` and XCHG would be mechanically sound [CB8 `b = d * b`], so MUL does NOT
        share ADD/SUB's parking rule.  I have exactly one MUL sample and will not generalize from
        it: mixed MUL stays refused.
    result into a DEC variable -> `CALL ?QI15D` before ?DSTOP [CB10 `e = b + d`] -- the FIXED->DEC
        doorway already recorded as open (Q8), unchanged by this milestone.
    DEC + integer LITERAL -> both operands loaded DEC and combined by ?DADOP [CB9], i.e. DR does
        NOT convert the literal; that is my existing pure-DEC route.
Direct DEC->INT (`b = d`) is implemented and now has its own DR golden: CB6 byte-identical [C161].
Why the route is not implemented yet: `is_dec_expr` classifies a MIXED expression as a DEC
expression, so the assignment takes the pure-DEC path and refuses with "decimal operation on
non-decimal operand"; and `lower_hl` has no notion of the target's type context, so giving its
`Eident` arm a DEC case would also fire inside pure-DEC expressions.  An attempt that did exactly
that was built and tested in an isolated worktree: it made CB1-CB5/CB7 route correctly but made
CB9 (a pure-DEC case) double-convert -- and my own new invariant caught it (C162).  The clean fix
needs an explicit integer-context marker (a node or a context parameter) threaded through lowering,
which is a structural change and is deliberately not attempted at the end of a milestone.
    [E2E-25 UPDATE -- THE ROUTE IS IMPLEMENTED, AND THE FIX WAS A PREDICATE, NOT A NODE ANNOTATION.]
    `lower_assign' now guards its decimal-store arm with `is_dec_expr st rhs && dec_pure st rhs', so a
    MIXED tree falls through to the integer route instead of being claimed and then refused; inside
    `lower_hl', a bare FIXED DEC operand converts in place (`LXI H,<var> / MVI A,p / ?DLDOP /
    ?QDI15', p = the SOURCE precision) and takes DR's measured parking shape unchanged.  Byte-exact
    against their own DR goldens AND executed with byte-equal console output and independently
    computed values: CB1 (3+5=8), CB2 (5+3=8), CB3 (3-5=-2), CB4 (5-3=2), CB5 (z=d+b=8), CB7
    (12345+5=12350 on the dec(5) route), plus CONV.PL1, DECY.PL1 and NG14 (`i = i + d', mixed
    self-add).  CB9 (`b = d + 2'), CB6 (`b = d'), DECPOLY, DFACT and C162W1..W8 are byte-identical
    as before, which is the protection this claim's failed attempt used to break.  CB8 (mixed MUL)
    and CB10 (mixed result into a DEC target) STILL REFUSE: see C181.

C162. **A PRE-EXISTING pool DEMAND under-count for decimal literals, caught by the E2E-16
demand/layout invariant within hours of that invariant existing.** CB9 (`b = d + 2` with
`d fixed dec(3)`) needs two decimal cells -- the `d = 3` store's literal and the operand literal --
and DR references both (`*S(0000)` and `*S(0002)`).  My prescan demands 2 pool bytes while lowering
allocates 4.  Under-counting is the dangerous direction: the pool base is where automatic variables
start, so with a 2-byte shortfall `b` would have been placed ON the decimal cells and a later
assignment would have overwritten a live constant -- the FDTEST failure mode, with every address in
a dump still looking plausible.  This reproduces on the released binary with codegen UNMODIFIED, so
it is not introduced by this milestone; before E2E-16 nothing compared the two numbers and it emitted
wrong bytes silently.  Now it refuses loudly.  The exact reason the demand misses a cell is not yet
traced, and it is the first thing I would chase: it is a correctness bug in an already-accepted
feature area, not a missing language feature.

### New refusals and one new specimen from this milestone

30 probes registered as my-gap refusals (AB1-AB17, CB1-CB10 minus CB6, ARRAY, PASSARAY, CONV,
DECY) with markers pinned to the specific refusal text, and CB6 registered as a byte-exact
specimen.  Every one has a DR golden proving DR compiled it, so none of them is a language rule.

## E2E-18 (C162 RESOLVED, C163): the decimal-pool under-count was a target-keyed demand rule

C162 RESOLVED. **Root cause: `prescan_stmt` keys its DECIMAL pool demand on the type of the
assignment TARGET, never on the DEC content of the expression itself.**  For a Vdec target a bare
literal demands a target-precision cell and a complex DEC-typed rhs goes through
`pdec_operand_bytes`; for a FLOAT target the whole statement goes through `pdec_fl_expr`; but for
any OTHER target (a FIXED BINARY variable, which is CB9's `b = d + 2') the statement fell through to
`prescan_expr`, and `prescan_expr` has NO `Enumber` arm at all -- so the operand literal's decimal
cell was never sized, while lowering allocated it.  Demand 2 bytes, allocation 4.  This is the same
structural mistake as C152 (demand and allocation computed independently) reached from the other
side: C152 was demand over-occurring per use, this is demand missing per TARGET TYPE.

Fix (consistent rule, not a +2 adjustment): for a target that is neither DEC nor FLOAT, if the rhs
is a COMPLEX DEC-typed expression, demand it through `pdec_operand_bytes` -- exactly the call the
Vdec branch already makes.  A bare literal or bare identifier is excluded, because under a BIN
target those allocate nothing at lowering (`LXI H,immediate` / direct `LHLD`), and including them
would double-count against `prescan_expr`'s Exp / const-minus-const literal arms.

Evidence: eight new controls W1-W8 (e22src, golden/e2e221 + e2e222) cover DEC store alone, DEC store
+ mixed ADD, mixed ADD with no prior store, DEC+DEC, DEC*literal, literal+DEC (commuted), two DEC
stores, and direct DEC->INT.  **All eight compile, are RAW-BYTE-IDENTICAL to DR, and all eight
link and run to identical values in mine and in DR, matching hand-computed expectations (5,5,5,7,6,
5,5,3).**  W5 (`b = d * 2') confirms the MUL case where demand and allocation legitimately differ in
SIZE from the ADD case -- DR gives the literal its OWN digit count for `*' and ALIGNED precision for
`+', so a flat +2 would have broken W5 while the real rule gets it right.  CB9 itself is now
byte-identical and promoted from refusal to specimen.  Mixed DEC/BIN ADD/SUB with a DEC variable on
the OTHER side (CB1-CB5, CB7, CB8, CB10) still refuses unchanged, so C161 is untouched by this fix
-- verified, not assumed: 25 of the 30 E2E-17 refusals still refuse.

Two process lessons:
  * **W2's golden was recompiled rather than reused.**  My first probe generation wrote
    `b = 5' twice and dropped `d = 3', so golden/e2e221/W2 no longer described its source.
    Comparing against it would have been a comparison against a different program.  A golden
    must come from the exact bytes it is compared with, so W2 went through DR again as e2e222.
  * **C163: I silently replaced five accepted specimens, and my own committed inventory would
    have ratified it.**  I registered the new controls under the names W1..W8 -- `W1'..`W6' are
    E2E-15's stack family, already byte-exact specimens -- and dict assignment replaced five of
    them.  The panel total went to 536 instead of 541; because I ran `--update-inventory' BEFORE
    reading its diff, the committed record would have absorbed the substitution and reported
    green.  Fixed mechanically: `SPECIMENS`/`REJECTS` are now a `NoOverwriteDict` that raises at
    import time on ANY re-registration (literal, loop or `.update()`), loop-driven registrations
    go through `add_spec()`, and the keys became `C162W*`.  Registration order is irrelevant now,
    which is the point -- `registration_audit()` reads source text and cannot see a loop
    assignment that lands on an existing key.  Discipline attached: review
    `git diff spec/INVENTORY.txt' BEFORE accepting an inventory rewrite; a removal line is
    intentional only if you can name it (here: exactly one, CB9's refusal row).

Arrays (Step 2) were attempted and deliberately NOT landed.  The parser already captures dimensions
(`ddims`, `Dim_bound(lo, Some hi)`), so the work is entirely in binding and lowering; but carrying
array info to codegen requires `layout` to return it -- `layout` currently hands back a 4-tuple
`(auto, syms, statics, rows)` consumed at bind.ml:648, bind.ml:847 and the `proc_layout` builder,
and `pl_rows` is a 3-tuple read at 7 sites in codegen.ml.  That is a signature change across the
highest-blast-radius layout code in the tree, with 541 byte-exact specimens resting on it, and it
is not a change to make at the end of a context.  The full design, including the sizing rule and
the three lowering shapes with their exact instruction sequences, is in
spec/notes/e2e18-c162-and-array-design.md so the next milestone starts from a plan and not from zero.

## E2E-19 (C164, C165, C166): 1-D array STORAGE landed in the binder; element ACCESS characterized but reverted

C164. **DR's 1-D FIXED BINARY(15) array STORAGE rule is implemented and byte-verified.**  A
declaration with one dimension and literal bounds occupies `2 * (ub - lb + 1)` bytes in the
automatic area and shifts every following automatic variable by that amount, exactly as DR does it.
Five controls (e23src/AR1-AR5, golden/e2e223) are RAW-BYTE-IDENTICAL to DR and each pins a distinct
part of the rule:
  * AR1 `dcl a(5) fixed, b fixed' -- `b' lands at A(000A): the array takes 0000-0009.
  * AR2 scalar before AND after the array -- `b' at 0000, `c' at 000A, so the array shifts only what
    comes after it (declaration order, not alphabetical).
  * AR3 `dcl a(1:5)' -- same size as AR1, which pins the LOWER:UPPER orientation.
  * AR4 `dcl a(0:3)' -- FOUR elements, `b' at 0008, which pins the arithmetic (4*2, not 5*2).
  * AR5 `dcl a(5) fixed bin(15)' -- explicit type spelling behaves like typeless FIXED.
Implementation shape: `bind.layout` still owns every offset (it remains the single storage
authority -- nothing in codegen re-derives a size), and the array metadata travels in a NEW explicit
field `proc_layout.pl_arrays : (string * int * int * int) list` rather than by widening `pl_rows`,
whose 3-tuple is read at 7 codegen sites.  `layout` now returns a 5-tuple; both consumers were
updated.  Unsupported array declarations refuse at the binder instead of sizing on a guess:
multi-dimensional and assumed-size dimensions, non-constant bounds, an upper bound below the lower
bound, and any element whose size is not 2 bytes (so DECIMAL/FLOAT/BIT/CHARACTER arrays).  STATIC
arrays also refuse: DR places them below the pool, and the interaction with the pre-existing
STATIC-on-fixed-bin guard (C114) is unsampled.
  HOW THE ORIENTATION BUG WAS FOUND: AR3 and AR4 refused with "upper bound below lower bound" -- the
parser stores `a(1:5)' as Dim_bound(first, Some second) and I had assumed the reverse.  The probes
caught it; nothing was inferred from the PL/I manual.

C165. **Constant-subscript element access is fully characterized but NOT shipped.**  I implemented
the read and all four store forms; they emitted correctly (AB1's `b = a(1)` produced the LHLD with
the right address, confirmed by instrumentation) and then a bare `Fatal error: exception Not_found`
followed from `List.assoc nm st.procs` in the call path of `lower_hl`, on a name that was neither a
procedure nor an entry -- i.e. the array branch and the call branch both ran for the same source
expression, so an `Esuffix` is evidently visited by a second path I did not account for.  Because a
non-`[TBD]` crash is a failure under this project's own contract (the negative panel greps for the
literal `[TBD]`), I reverted the codegen change and shipped only the binder half.

What the four forms are, from DR's own objects (all newly measured this milestone):
    offset 0, ANY value          LHLD/LXI H,val ... ; SHLD A(base)        [AB1 AB12 AB16 AC5]
    offset <> 0, LITERAL value   LXI H,A+off ; MVI M,lo ; INX H ; MVI M,hi [AB3 AB9 AB14 AC3]
    offset <> 0, COMPUTED value  PUSH H ; LXI H,A+off ; POP D ; MOV M,E ;
                                 INX H ; MOV M,D                          [AC1 AC2 AC3]
    SAME element on BOTH sides   LHLD A+off ; <bias ladder> ; SHLD A+off   [AB12 off 0, AC4 off 2]
The fourth row is why "literal vs computed" is not DR's rule: AC1 `a(3) = b' parks on the stack
(C141 discipline -- LXI H must destroy HL) while AC4 `a(2) = a(2) + 5' needs no parking at all,
because the element address is an immediate operand of both the load and the store.  AC3 also pins
that a constant subscript BELOW the lower bound is emitted as a negative 16-bit operand
(`LXI H,A+FFFE' for `a(0)' on `dcl a(4) fixed'), so the offset is `(sub-lb)*2' with no clamp and no
bounds check -- consistent with C159's finding that DR never checks.

Two further decisions taken while implementing, both scope-based rather than textual:
  * **The array binding must win over a same-named callable.**  AB1/AB3/AB9 all write
    `a: procedure options(main)' with `dcl a(5) fixed' inside that block, so the program label `a'
    is bound as callable while `a' is also an array.  My first guard required
    `array AND not procedure', which silently routed element reads into the call path -- that is
    precisely what produced the Not_found.  PL/I scoping says the inner declaration shadows the outer
    program name, and DR compiles all these probes, so the declaration wins.  No accepted specimen
    declares an array, so this priority cannot change any existing call site.
  * **Whole-array uses refuse instead of reading 2 bytes.**  `b = a' and `a = 3' raise [TBD] from
    vk_of and from the assignment path.  Reading the base cell of an array as a scalar would be a
    wrong-value mis-compile in the C139/C150/C151 class, which is the worst thing this compiler can
    do.

AC1-AC5 stay as my-gap refusals with pinned markers.  AB2/AB8/AB10 (runtime-variable subscripts),
AB13 (2-D), AB5/AB15 (STATIC), AB6/AC3 (parked-ADD class) continue to refuse.

C166. **A tooling hazard that destroyed a file: `open(p,'w')` truncates BEFORE `write()` validates
its argument.**  While editing the gate I built the new content with a conditional expression that
evaluated to `None`, called `write(None)`, and the `TypeError` arrived AFTER the file had already
been opened for writing -- leaving tools/e2e_gate.py at 0 bytes (the whole 127 KB regression panel).
Recovery was trivial because it was committed, which is the only reason this was not a disaster.
Every file rewrite in this repo now goes: build the string, `assert isinstance(s, str)` plus a
minimum length, write to `p + '.new'`, then `os.replace`.  Note the same class bit me twice in two
milestones (E2E-17's `write()` of a non-string left a file truncated too) -- the prevention has to
be the write pattern, not care.

C165 addendum -- precise crash diagnosis for the next milestone (reproducible, with a saved patch).
The array READ branch itself is correct: for RD1 (`put skip list(a(3))' with `dcl a(5) fixed')
instrumentation shows the binder metadata arriving intact at the lowering site
(`arrays=1 [a] exts=false procs=false') and DR's expected form is exactly
`LHLD A(0000)+off' -- RD3's listing confirms first element `LHLD A A(0000)' and last element
`LHLD A A(0000)+0008', i.e. my offset arithmetic (sub-lb)*2 matches DR for both ends.
Nevertheless the compiler dies with a BARE `Fatal error: exception Not_found' raised at
`List.assoc nm st.procs` inside lower_hl's CALL path, on a name that instrumentation has just
proved is in neither st.procs nor st.exts.  The trace puts the caller at
`lower_put_items_gen ... (fun) ... line 5155` -- so the PUT-item path reaches lower_hl with the same
Esuffix, and the call site that raises is reached without my array guard having held there.  In
short: at least two distinct resolutions of `a(3)' happen for one source expression, and only one of
them sees st.arrays.  A one-line patch cannot fix that; the real requirement is to resolve an
Esuffix ONCE against the bound declaration and pass the resolved meaning (element vs call) down,
rather than re-deriving it at every consumer -- the same structural fact C161 ran into from the
other direction (lower_hl has no type context).  This is the "genuinely broader architectural
dependency" case, so the code was isolated rather than landed:
spec/patches/e19-array-read-attempt.patch reproduces it (apply on d9001fa, build, run
e23src/RD1.PLI).  Verified safe facts from that patch, worth keeping: the read-only build does NOT
crash on store-shaped refusals (ST1 `a(3) = 5' refuses cleanly as a non-simple assignment lhs), so
landings can be ordered read-first once the double-resolution is fixed.


---

## E2E-20 (C165 corrected, C167, C168, C169): indexed-reference resolution, element reads and the four store forms

C165 CORRECTION [E2E-20]. **The "Esuffix resolved twice" diagnosis was wrong, and there was no
architectural dependency.**  Reproducing `spec/patches/e19-array-read-attempt.patch` in a worktree
and instrumenting it shows exactly ONE resolution per source expression: `DBG READONLY nm=a
arrays=1 [a] exts=false procs=false` prints once, then a second probe placed on the *following*
statement of the same arm prints `DBG REACH-THROUGH into call setup for nm=a`, and only then does
`List.assoc nm st.procs` raise.  The mechanism is elementary OCaml: E2E-19's patch inserted
`if is_array then begin <emit LHLD> end else if not-callable then failwith ...` into the body of
lower_hl's existing `Ast.Eident h, args ->` arm, whose body CONTINUES with `let ext = ...` and the
whole call machinery.  An `if` whose branches are `unit` does not terminate the surrounding
sequence, so the element emitted a correct load and the call route then ran on it anyway.  Nothing
was resolved twice; nothing was resolved in the wrong scope.  Two consequences that matter:
(i) E2E-19's recommendation to build a resolution architecture first was based on a misread
crash, and (ii) the real requirement was a *return*, which a guarded match case supplies for free.
Discipline note: the crash trace named `lower_hl`, and the plausible story about PUT re-lowering
the expression was accepted because it fitted C161's unrelated structural gap.  A line number is
not a causal explanation -- a second probe placed after the suspect branch is. [reproduced twice,
E2E-19 and E2E-20, same patch, same two lines of stderr]

C167. **An array's storage EXTENT was missing from the module span; it was correct only in the
declaration order that hid the bug.**  `bind.ml`'s `section2` computed
`span = max(off - drop + rt_bytes rt)` over the named rows, but `rt_bytes` returns the ELEMENT
size (2) for an array -- the row builder advances offsets by `elem_sz * nelem` separately.  So:
`dcl q(3) fixed, s fixed` gave the right 8 (because `s` at offset 6 pushes the max past the
array) while `dcl s fixed, q(3) fixed` gave 4 and array-only `q(3)` gave 2.  DR pins the rule
directly: AB18 (scalar then array) and AB19 (array in the middle) both report
`DATA AREA = 0008` [golden/e2e227], and AB16's DR .REL says `LINK-DEF-DATA-SIZE abs 0006` where
mine said `0002` -- a one-byte difference in the whole file, which is how it was found.
Fixed by taking the extent from `Bind.bind_arrays` (`(ub-lb+1)*esz`) inside `section2`, so there
is ONE sizing rule and codegen still computes no layout of its own.  AR1-AR5 were and remain
byte-exact: they are all array-FIRST, which is the orientation that accidentally worked.
This is the third arrival at the same structural mistake as C152 (demand over-count) and C162
(demand under-count): a size derived in one place and consumed in another.  The lesson is
sharper than those two -- **a rule verified only in the orientation that conceals its bug is not
verified**; E2E-19 tested five array layouts and every one of them happened to be insensitive to
the defect. [AB16 AB17 AB18 AB22, golden/e2e223, e2e227, e2e228]

C168. **DR applies cross-statement constant-reuse peepholes that I do not implement, and they are
not array features.**  Three probes compile in both compilers and differ only for this reason:
AB19 (`x=1; q(1)=2; y=3`) lowers in DR to `LXI H,0001 / SHLD / INX H / SHLD / INX H / SHLD` -- the
three separate LXI H loads collapse to INX H; AB21 (`x=1; q(1)=5; y=9`) lowers to
`LXI H,0001 / SHLD / MVI L,05 / SHLD / MVI L,09 / SHLD` -- with H already 0, DR rewrites the low
byte only; RT1 (six literal stores) shows DR using `DCX H` and emitting 2 fewer DATA bytes than
mine.  Each of these is a value-preserving register reuse across statement boundaries.  Mine
emits the straightforward `LXI H,v` per store, so the values are always right and the bytes are
not.  Consequence for the panel: AB19/AB21/RT1 are registered as NEITHER specimen NOR refusal,
deliberately -- they do not refuse, so registering them as negatives would claim a [TBD] that does
not happen, and they are not byte-exact, so registering them as specimens would fail the gate.
They are kept out of the panel and documented here instead; if the peephole is ever implemented
they become byte-exact specimens with existing goldens (golden/e2e227, e2e228, e2e229).
Note the relationship to C156 (`* 0` elision) and C143's route-dependent thresholds: this is the
same DR optimizer family, arriving from the store side. [AB19 AB21 RT1]

C169. **One authoritative indexed-reference resolution replaced three independent syntactic
guesses, and each one turned out to be blocking a different program.**  The mechanism is small:
`hd_is_element`/`suf_is_element` (a TOTAL predicate over the binder's per-block array list -- it
never refuses, never lowers, never allocates) plus `resolve_suffix`, which returns
`Suf_element of int` (the relocated element address) or `Suf_call`, and is consumed by exactly
one guarded match case per site.  Guarded cases matter: they make the fall-through that caused
C165's crash structurally impossible rather than impossible by care.  What it fixed, one row per
misclassification:
  - `expr_contains_call` was `| Ast.Esuffix _ -> true`, so `a(5) * 3` "contained a call", which
    vetoes `mul_const_form`; AB9 therefore parked (PUSH H / LXI H,3 / POP D) where DR loads the
    literal straight into DE (`LHLD A+0008 / LXI D,0003 / ?IM22N`).  AB23 (`b = x * 3`, scalar)
    pins DR's form independently and is byte-exact both before and after -- the control that
    proves the fix moved only the element case.
  - lower_hl's ADD arm selected "call on the right" for `a(2) + a(3)`, which routed AB6/AC3 into
    the deferred-load path and its refusal.  With the arm guard consulting the resolution they
    fall to the ordinary ADD arm, whose C150 syntactic rule (`add_left_needs_push`) parks the
    left operand -- and DR's AB6 golden is exactly `LHLD / PUSH H / LHLD / POP D / DAD D`.  So the
    existing rule was RIGHT and only the routing was wrong: DR does park for a subscripted
    operand even though no call exists, which re-confirms C150's syntactic reading from a new
    direction.
  - `num_width` (PUT item width) refused any non-procedure Esuffix; RD1/RD2 now take the array
    row's own declared width and DR's form is the scalar one with the element address
    (`LHLD A(0000)+0004 / MVI A,09 / ?QICOP / ?PNVOP / ?QIOOP`).
  - the callee scope: `lower_proc` saved and restored `st.vars` but NOT `st.arrays`, so a nested
    procedure resolved subscripts against its CALLER's block.  AB22 (array last inside `p`)
    crashed with a match failure before the swap and is byte-exact after; RT3 is the runtime
    witness -- outer `w(3)` and inner `w(2)` share a name with different extents, and the eight
    printed values (`1031 1287 13` then `259 515 771 9`) are only reachable if each block uses its
    own extents.  Note this is NOT an array rule: it is the same per-block scope fact as C142.
  - WHOLE-ARRAY USE refuses, and DR refuses too: `b = a`, `a = 3`, `put skip list(a)` all get
    `TYPES NOT=` in pass 2 with NO .REL emitted [golden/e2e230], while mine previously ACCEPTED
    all three and loaded/stored the array's base cell as a scalar.  The guard sits in `addr_of`
    and `vk_of` -- the two points every un-subscripted data reference flows through -- rather
    than at ten call sites, and `resolve_suffix` uses `addr_of_raw` for its base so a subscripted
    reference is unaffected.  `vk_of` is guarded as well as `addr_of` because prescan asks it for
    DEC/FLOAT demand; answering `Vint` there would size the pool around a reference DR rejects.
    Panel class: `dr-refuses`, the strongest kind -- refusing is required for compatibility.
Priority-2's shadowing requirement is satisfied by scope, not by priority: the array list is the
BLOCK's own (`st.arrays` from `Bind.bind_arrays blk`, swapped per callee), so AB1's
`dcl a(5) fixed` inside `a: procedure options(main)` shadows the outer program name because the
inner block's list is what is consulted there.  There is no global "arrays beat procedures"
rule, and a name bound as a callable in the block that references it is still a call. [AB1 AB22
AB23 RT3 GW1-GW3, golden/e2e228, e2e229, e2e230]

C165 status (was: blocked). **Constant-subscript element access is LANDED** -- reads and the four
measured store forms.  Read: `LHLD` + 2-byte DATA reloc at `base + (sub-lb)*esz`, including the
PUT-item context (RD1/RD2) and expression context (RD3/AB1/AB9/AC3/RT4).  Stores: (1) offset 0 ->
value route + `SHLD base` [AB1 AB16 AC5 AB12]; (2) offset<>0 with literal ->
`LXI H,base+off / MVI M,lo / INX H / MVI M,hi` [AB3 AB9 AB18 AB22]; (3) offset<>0 with computed
value -> `PUSH H / LXI H / POP D / MOV M,E / INX H / MOV M,D` [AC1 AC2 AC3 RT4]; (4) same element
on both sides -> `LHLD / <bias> / SHLD`, tested BEFORE (3) because AC4 proves parking is not
selected by literal-vs-computed.  One implementation bug worth recording: 0x72 is `MOV M,D` and
0x73 is `MOV M,E`; my first draft had the comments reversed and therefore the bytes reversed, and
AC1/AC2 caught it as a byte difference rather than as a plausible-looking dump.
Boundaries kept: variable subscripts [AB2 AB8 AB10 ARRAY PASSARAY], multi-dimensional [AB13],
STATIC [AB5 AB15], element-as-actual [AB7 -- DR stores the element ADDRESS in the descriptor],
condition-context element tests [AB11], whole-array [GW1-GW3], non-2-byte elements and
non-constant bounds [refused in the binder].  C161 mixed DEC/BIN was NOT touched. [C159 C164 C167]

C161 design observation (documentation only, NOT a deliverable). `resolve_suffix` is the shape
that a context-sensitive DEC/BIN lowering would need: it is the one place that turns a source
node into a meaning using the bound declaration, and `Suf_element` shows the pattern for carrying
information *out* of resolution.  A DEC/BIN fix wants the mirror image -- an inbound
expected-context argument (integer vs decimal) threaded from the statement through `lower_hl`,
which `is_dec_expr` currently derives by itself and gets wrong for mixed expressions.  Adding a
second parameter to `lower_hl` is the change; the resolution work here neither requires it nor
implements it, and the CB-family refusals are unchanged.


---

## E2E-21 step 1 (C170, C171): safety/evidence corrections, and DR's variable-subscript ladder measured

C170. **Five corpus programs refused with a BARE exception -- rc != 0 and no `[TBD]` -- and the
sweep counted all of them as REFUSED.** `REFUSED` is defined as rc != 0, so it silently absorbs
crashes; this is the exact hole the negative panel's `[TBD]` grep exists to close, and the corpus
instrument did not have it. The count went from 5 to 0 (re-measured by
`grep -E '^REFUSED' sweep-output | grep -vc TBD`). Three distinct causes, none of them array or
new-feature work:
  - `bind.ml`'s statement walker `w` is deliberately exhaustive-by-construction with NO catch-all,
    and had no `Salloc`/`Sfree` arms -- so any program containing ALLOCATE or FREE died inside
    `bind` BEFORE codegen could refuse it (REVERSE, NETWORK; the compiler already warns about this
    match at build time, `not matched: (Salloc _|Sfree _)`). Fixed by traversing their operand
    expressions, which implements nothing: codegen still refuses with `[TBD]: POINTER`.
  - `codegen.ml`'s `match_put_list_lit` outer match was exhaustive only for a stream-less,
    ON-less `put [skip] list(...)`; a named-file PUT (KEYFILE) or a PUT with ON options (CREATE)
    fell off the end. Fixed with two refusing arms placed BEFORE the plain case, plus a catch-all
    so no other statement kind can reach a Match_failure there. Discovery worth keeping: the
    PARSER records `put file(f) list(x)` as an ON OPTION, not as a `stream` -- PU1 shows which
    arm actually fires.
  - Two `failwith ("codegen: undeclared " ^ name)` sites (addr_of/vk_of) produced a message with
    no `[TBD]` (REVERT: `call p(i,exit)`, a label used as a value). Only the wording was wrong;
    the verdict was already a refusal.
Registered as tested negatives via three space-indented probes (AV1 = ALLOCATE/FREE, PU1 =
named-file PUT, markers pinned to the new reasons). The five CORPUS programs are deliberately NOT
panel entries: their sources contain TAB characters and the committed inventory is tab-separated,
so registering them produced a malformed row. The gate caught that by aborting rather than by
accepting a corrupt file -- which is the instrument working, and the reason I switched to minimal
probes instead of changing the inventory schema mid-milestone. Two of my own probe rewrites
(PU2, EX1) turned out to be invalid PL/I (bare Parse_error) and were DROPPED rather than
registered, since a parse error is outside the `[TBD]` contract [E2E-17 lesson]. [AV1 PU1,
golden/e2e214 sweep, corpus/REVERSE NETWORK CREATE KEYFILE REVERT]

C171. **AB19, AB21 and RT1 now have a third, mechanically checked panel** (`spec/DIVERGENT.txt` +
`divergence_check()` in the gate). They compile but are not byte-exact, so they belong to neither
existing panel: registering them as negatives would assert a `[TBD]` that never happens, and as
specimens they would fail. Each row pins the source, the golden, my code-record count, DR's, both
DATA areas, and the differing-byte count; the check requires that each program still BUILDS, still
DIFFERS, and still diverges in exactly the recorded shape. Becoming byte-exact is a FAILURE
("promote it"), and so is starting to refuse. The measured facts [the numbers in my first draft
were invented and had to be replaced by reldump output -- worth stating, because the same mistake
in a report would have been a false claim]:
  - AB19: mine 65 code records vs DR 61, DATA 8 == 8. DR collapses three constant stores to
    `LXI H,1 / SHLD / INX H / SHLD / INX H / SHLD`.
  - AB21: mine 65 vs DR 63, DATA 8 == 8. DR uses `MVI L,k` when the high byte is already correct.
  - RT1: mine 110 vs DR 108, DATA 12 == 12. Short HL-reuse form at code 000C.
  The DATA area agrees in every case, so the C167 sizing fix is cross-checked by programs that
  were written to expose something else entirely. [C168]

E2E-21 P1 prerequisite -- DR's VARIABLE-subscript ladder, measured from AB2 before implementing
[golden/e2e216/AB2/AB2.REL, $L$C$D]. Address generation is IDENTICAL for a read and for a store,
13 bytes, and the operand of `LXI H` is a 2-byte DATA relocation:
```
LXI H, <reloc: array_base + (lb-1)*(-2)>   ; 21 lo hi   (pre-biased base, ONE reloc)
PUSH H                                     ; E5
LHLD <reloc: index_variable>               ; 2A lo hi
DAD H                                      ; 29
POP D                                      ; D1
DAD D                                      ; 19       -> HL = element address
```
then the store of a literal continues `MVI M,lo / INX H / MVI M,hi` (36 .. 23 36 ..) and the read
continues `MOV E,M / INX H / MOV D,M` (5E 23 56). Two consequences for the implementation: no
extra `LXI H` is emitted after the ladder (HL already holds the address, so E2E-20's forms 2 and 3
must NOT be reused verbatim for a computed address), and the ladder's own `PUSH H` is the only
parking involved -- which is consistent with C141 because nothing lives in a register across the
`LHLD` of the index cell. The negative bias `(lb-1)*(-2)` is carried by the relocation arithmetic,
not by a separate offset field, so the operand value must be verified against AB8/AB10 (which use
different bounds) before wiring it up.


## E2E-22 (C172-C175): runtime array subscripts, element arguments, and a wrong-value miscompile found by running the integration programs

C172. **DR's variable-index address ladder: operand = `base - lower_bound*element_size', and TWO
      forms selected by whether that operand is the plain base.** The [C159] wording
      `A+(lb-1)*size' and the E2E-21 note `(lb-1)*(-2)' are WRONG, and three goldens with three
      different bounds say so by their DATA relocation addends: VB1 (lb=0) 0x0000, AB2 (lb=1)
      0xFFFE, VB2 (lb=2) 0xFFFC. `base - lb*esz' fits all three; `(lb-1)*(-sz)' fits none of the
      non-default ones. The two forms are
        bias = 0   : LHLD idx [; INX H] ; DAD H ; LXI D,<base> ; DAD D            (7 bytes, no stack)
        bias <> 0  : LXI H,<biased> ; PUSH H ; LHLD idx [; INX H] ; DAD H ; POP D ; DAD D  (13 bytes)
      The selection is mechanical, not stylistic: `LHLD idx' destroys HL, so with bias<>0 the base
      has to be parked -- on the runtime stack, exactly the C141 discipline applied to an address
      instead of a value. With bias=0 there is nothing to preserve, so DR computes 2*idx first and
      adds the base from DE afterwards. The doubling is `DAD H' of the INDEX, and the second add
      comes from the parked copy, so the ladder's PUSH/POP pair nests inside a caller's own
      parking pair, which is what AB8/AB10 show for a computed store.
      Index expressions: `a(i+1)' emits `LHLD i / INX H / DAD H' -- the +1 is applied to the INDEX
      VALUE before doubling, so it moves exactly one element; an address-side +1 would move two.
      Only +1 is measured; `i+k', `i-1', products and element-as-index all keep refusing.
      Evidence: AB2 AB8 AB10 VB1 VB2 byte-exact, and all five link+run to DR-identical output
      (9, 4, 1 2 3 4 5, 7, 8) -- the runtime results are what rule out an off-by-one that the
      byte comparison alone could hide only if DR were also wrong, which is why both are required
      [C137].

C173. **A pointer formal read in a DO bound position must be DEREFERENCED; omitting it is a
      wrong-VALUE miscompile, and byte-parity plus rc=0 does not reveal it.** DR's tail in both
      bound slots is the ordinary pointer-formal deref [C130] `MOV E,M / INX H / MOV D,M / XCHG'
      (DO1 `do j = 1 to x', DO2 `do j = x to 5'). Before the fix mine stored the POINTER as the
      bound. DO1/DO2 differ from DR by exactly those 4 bytes; the integration programs made the
      semantic damage visible at runtime: linked with LINK 1.31 and run under cpmsim, PASSARAY
      printed 69900 lines where DR prints 75, and ARRAY 139580 against 75 -- both rc=0, both
      "compiled fine". After the fix DO1 prints 1 2 3, DO2 prints 3 4 5, PASSARAY is byte-exact,
      and ARRAY's runtime output is line-for-line identical to DR's.
      Lesson kept as a rule: a program that compiles and matches bytes is evidence; a program that
      compiles with rc=0 is not. Wrong values can be invisible in the panel that counts refusals
      and in the panel that counts bytes -- they surface only by running [C137, C168, C171].

C174. **PUT SKIP accepts a runtime count, and DR keeps only its LOW BYTE**: `LHLD v / MOV A,L /
      CALL ?SKPOP' versus the literal form `MVI A,n / CALL ?SKPOP' [SK3 SK4]. The count is an
      8-bit quantity even when the expression is FIXED(15); DR neither range-checks nor widens.
      Only a bare variable is measured, so an arithmetic/subscripted/call-bearing count refuses
      (a call would clobber A between the load and ?SKPOP -- C141's hazard again).
      Independent corroboration: N4_SKIPVAR, an E2E-8-era inline negative with its own older
      golden (golden/negpanel1/NG36), became byte-identical under the same rule. Two DR goldens
      built through different batches agreeing on one instruction sequence is stronger than one
      probe, and promoting N4 is the only sanctioned way to retire it [C154].
      This one shape was all that separated the compiler from both PLI-2000 integration programs.

C175. **There is NO array calling convention: an array element passed as an actual goes through the
      ordinary pointer-formal descriptor [C130].** Constant index -> `LXI H,<a+off> ; SHLD <desc
      cell> ; LXI H,<desc> ; CALL p' [AB7]; runtime index -> `<ladder> ; SHLD <desc cell> ; CALL'
      [PASSARAY], because the ladder already leaves the address in HL. Both take the DYNAMIC
      descriptor route (runtime SHLD, bare RELOC, no SET-LC wrapping) that E27B established for a
      forwarded pointer formal -- notably, even though a constant-index element address IS
      statically known, DR still writes it at runtime rather than as a static descriptor reloc.
      In the BINDER, an element actual counts as a simple argument and gets NO temporary value
      cell, unlike a call actual [C145]: AB7/PASSARAY allocate none. Giving one would both add a
      DATA byte and shift every later anonymous-cell number, which is why this belongs in bind and
      not in a codegen patch.
      Checkpoint C evidence: EA2 passes `a(4)' AND `a(i)' to a procedure whose body is
      `x = x + 100'; my .REL is byte-exact and both linked .COMs print "106 100", so the callee
      mutated the ORIGINAL cells through both index forms.

C176 [E2E-23, probes ZS1-ZS12 + a 1310-file corpus survey, all byte-exact, ZS11/ZS12 run]
  DR's zero-store form is chosen by a single tracked accumulator fact, not by a general peephole.
  Storing the 2-byte constant 0 through (HL) emits `XRA A / MOV M,A / INX H / MOV M,A' (4 bytes);
  storing any other 2-byte constant emits `MVI M,lo / INX H / MVI M,hi' (5) EVEN WHEN A is already
  known zero (ZS10's `a(4) = 7').  A lone zero byte still uses `MVI M,00' (V104, ZS10's high byte).
  "A = 0" is set by my own XRA A and survives statement boundaries, LXI H, SHLD, LHLD, DAD,
  PUSH/POP, INX H, MVI M and the entire variable-index ladder (ZS9: ONE XRA for both stores); it is
  invalidated by any CALL (ZS5 -- C141's no-parking rule, re-derived at byte level), by any write
  to A (ZS7: MVI A / LDA from the PUT argument path; ZS8: the compare), and at branches.  The rule
  was surveyed BEFORE implementing: `MVI M,00' occurs in 51 goldens, the all-zero PAIR
  `36 00 23 36 00' in NONE, and `AF 77 23 77' in exactly three distinct programs (E26A, ARRAY,
  ALLTST), always as paired stores from one XRA -- which is what proved the rule narrow rather than
  a peephole family, and made ARRAY's single remaining divergence tractable.  ARRAY is now
  byte-identical and its cpmsim output is identical to DR's own .COM (75 lines), with DATA area
  unchanged (62 = 62).  ZS11/ZS12 were run to make the counterexamples SEMANTIC: `0 0 5' proves a
  reused accumulator stored real zeros without disturbing the neighbour b, and `0 0' proves the
  post-call re-clear happened.  E26A's pointer-formal zero store, previously a one-off copy, now
  shares this single rule and stays byte-exact.
  CONSEQUENCE: the C168 label on ARRAY was wrong in size and in kind.  E2E-22's divergence row also
  claimed "a 1-byte code-size delta in the same family" as a second cause -- it was the same cause,
  since the two forms differ by exactly one byte.

C177 [E2E-23, probes ZK1-ZK12 + AB19/AB21/RT1 all byte-exact and all RUN, mine vs DR's own .COM]
  DR's cross-statement HL reuse is ONE fact already tracked here -- "HL holds a known constant
  value" (st.last_imm) -- used by every constant-store route, and the missing work was sharing it,
  not building an optimizer.  Measured forms, cheapest first: +1 `INX H' (ZK1), -1 `DCX H' (ZK4),
  +256 `INR H' (ZK3/ZK7), -256 `DCR H' (ZK9), same-high-byte `MVI L,lo' (ZK2/AB21/Z401), repeated
  value = no reload at all (R610/LOAN1).  Invalidations that are MEASURED, not assumed: a CALL
  (ZK5), and any route that puts an ADDRESS in HL -- a byte-store element write (ZK6), which is why
  RT1's a(2)/a(3)/a(4) reload while its offset-0 a(1) reuses.  The array element at offset 0 uses
  the scalar SHLD route and therefore sits INSIDE a reuse chain (ZK12/AB19), which is exactly why
  the helper had to move to module level: two copies of a measured rule drift by construction.
  AB19 prints `2 1 3', AB21 `5 1 9', RT1 `257 513 769 1025 1281 1537' -- each identical to a .COM
  built from DR's own .REL.  The divergence panel is now empty of pre-existing programs.
  TWO ERRORS RECORDED, because both nearly became accepted results.  (1) An intermediate revision
  of the element route called lower_hl AND the helper, emitting the value twice; that build made
  AB19 store 4 for 3 -- a wrong value, visible only because the program prints its variables.  I
  then blamed DR for it, having run a stale .REL that had been copied into a golden directory
  rather than the current build's bytes: runtime evidence must come from the same artifact the byte
  check uses.  (2) ZK8/ZK10/ZK11 (65535->0, 0->65535, 32767->32768) were read as "DR refuses reuse
  when bit 15 flips" and a guard was written on that reading; the raw bytes show DR does not reload
  there at all -- it routes the out-of-range LITERAL through `LXI H,0000 / MVI A,k / CALL / CALL'
  and allocates a 4-byte DATA cell, never reaching the reuse question.  The guard was removed
  (unproven conditions in instruction selection get trusted later) and the three probes are pinned
  in DIVERGENT.txt as their own open item.  The proximate cause of the misreading was a
  disassembly listing misaligned by SHLD's relocation operands: check bytes, not listings.

C178 [E2E-24, 26 byte-exact probes + 8 executed witnesses: ML1-ML15, MN1-MN8, LP1-LP16, LQ1-LQA]
  DR's route for a FIXED literal outside bin(15) is a packed-decimal pool cell converted at run
  time, NOT a wider immediate: `LXI H,*cell / MVI A,<digit count> / CALL ?DLDOP / CALL ?QDI15`.
  The trigger is the VALUE (ML9 32767 immediate, ML10 32768 decimal -- the boundary is exact, and
  `fixed bin(31)' is `NOT IMP' in DR's own listing, so no immediate fallback exists). The cell's
  PRECISION is the DIGIT COUNT OF THE TEXT, leading zeros included: `32768' is p=5/3 bytes and
  `0000032768' is p=10/6 bytes for the same value (LP2 vs LP15). Nibbles run least-significant
  digit first and the final nibble is the sign (0 positive, 9 negative, ten's complement in p
  digits) -- LP1's 32768 cell is `68 27 03'. Dedup is on the ENCODER'S BYTE IMAGE, not on
  (precision, value): LP1 (`32768' twice), LQ6 (`032768' p=6 then `0032768' p=7, identical images)
  and LQA (a dec(5) store and an integer store of the same literal) each get ONE shared cell, so
  the dedup table crosses declaration kinds. The route is context-free -- assignment, ADD/SUB
  operand (LP4 XCHG, LP5/LP9 PUSH H...POP D), condition, call argument, element store, multiply --
  and C177's HL-constant reuse does NOT survive it: LP1 stores 32768 twice and DR re-emits the
  whole route rather than reusing HL, so the register fact is dropped, not asserted.
  DECISIVE, and the reason byte parity here is not cosmetic: at run time DR ABORTS on every
  overflow case with `ERROR (1), Conversion' plus a traceback. The previous build silently
  truncated and printed a wrong number (ML1 printed `723'). Reproducing the route is what makes
  the failure mode match; mine now produces byte-identical output to DR's own .COM on ML3, ML4,
  ML15, ZK8, ZK10, ZK11, LP15 and LQA. This claim covers the STORE position and BOTH ADD operand orientations: right-literal
  `LHLD x / PUSH H / route / POP D / DAD D' (ML10/LP5/ML1/ML2/ML5), left-literal
  `route / XCHG / LHLD x / DAD D' (LP4, the conversion must come first because a run-time
  conversion cannot bias a register that is not loaded yet), and self-add, which DR emits
  identically to the right-literal form (LP14) so the measured -8..+16 ladder declines it and falls
  through.  The parking pair appears ONLY because the conversion runs in HL, so C150's no-parking
  rule for in-range literals is untouched, not contradicted.  SUB with a plain non-DEC
  identifier on the LEFT is routed too: `LHLD x / PUSH H / LXI H,*S / MVI A,p / ?DLDOP / ?QDI15 /
  POP D / CALL ?IS22N' (LQ5 `y = y - 32768', LP9 `y = x - 65535', ML8 `y = x - 1234567890').  It is
  a NEW lower_hl arm whose `when' guard admits only out-of-range literals with a plain non-DEC
  identifier on the left -- in-range SUB, DEC-typed lefts and compound lefts fall through to the
  shared add/sub dispatcher UNTOUCHED, because hundreds of byte-exact specimens pin that dispatcher
  and rewriting it for one family on two probes is how unrelated programs break.  DR calls a routine
  where its in-range ladder adds a two's complement because after the conversion DE holds the LEFT
  value and HL the constant, the wrong way round for DAD: mechanical, but known for three probes
  only, so it is not generalised.  PUT items, call arguments, conditions and
  element stores remain unrouted and are pinned as WRONG-VALUE rows in DIVERGENT.txt, never as
  acceptable differences.  Executed proof that this is a semantic fix, not a cosmetic one: ML1
  (`y = x + 1234567890') printed 723 at HEAD and now aborts byte-identically to DR's own .COM. ZK8/ZK10/ZK11 -- E2E-23's three divergences -- were never waiting on a
  register optimiser [C168's assumption was wrong]; they were waiting on this route.

C179 [E2E-24, four self-inflicted regressions, each caught by a different guard]
  A pool DEMAND must be made at exactly the AST position whose LOWERING allocates, and prescan
  walkers that RECURSE INTO OPERANDS are the wrong place. Putting a bare `Enumber` arm in
  prescan_expr over-counted every ADD/SUB constant, because those lower through the C150
  constant-operand path, which allocates no cell: prescan demanded 6 bytes, layout produced 0, and
  programs that had built at HEAD (ML1/ML2/ML5/ML8/LQ5) began failing the pool invariant. A patch
  script applied twice inserted TWO such arms and doubled the demand further -- found by reading
  the diff, not by reasoning about the rule. Consequences pinned as rules: (a) making
  previously-building programs fail an INTERNAL consistency check is never an acceptable trade for
  one more exact probe -- the element-store route was byte-exact at one point and was deliberately
  REVERTED because its demand could not be made (pdec_ctx carries scalar kinds only, so prescan
  cannot know an array's element kind); (b) demand and layout must share one encoder, which is why
  bcd_pack_scaled moved above every user rather than being duplicated [C155/C162]; (c) verify a
  change by recompiling the whole probe set with BOTH binaries and diffing the classification, not
  by trusting that unrelated positions are untouched -- that comparison is the only thing that
  proved the regressions gone; (d) a measurement whose every row reports the same number is a
  broken generator, not a law of nature: a variant script built with text-mode reads and `\r\n`
  patterns silently produced nine copies of one input file, and a shell loop that failed to reset
  its source variable reported twelve nonexistent regressions.

C180. **A NEGATIVE out-of-range FIXED literal is a SIGNED decimal cell, not a magnitude plus a
runtime negate -- and the whole ADD/SUB literal matrix is one rule, not five.**  DR's LP8 cell for
`-32768' is `32 72 96' (10^5 - 32768 = 67232, digits LSD-first, final sign nibble 9) and LQ2's
`-65535' is `65 44 93'; the emitted instructions are the ordinary conversion route and NOTHING else,
no `?IN20N'.  Mine was emitting `LXI H,8000 / CALL ?IN20N', which COMPLETED SILENTLY where DR aborts
with `ERROR (1), Conversion' -- so LP8/LQ2/LQ4 closed together on the first measured rule, and their
previously "cosmetic" traceback difference turned out to be a code-size artefact of my own
truncation, visible only once both sides aborted at the same instruction.
    With the sign folded into the cell, DR's arithmetic shape depends ONLY on which SIDE the literal
    sits on and which OPERATOR: left -> `route / XCHG / <other> / (DAD D | ?IS22N)', right ->
    `<other> / PUSH H / route / POP D / (DAD D | ?IS22N)'.  Parentheses vanish (Econd) and the sign
    vanishes into the cell, so E2E-24's four pattern-matched arms collapse into one.  Both orientations
    and both signs are pinned independently (LR3 `32768 - x', LR11 `-32768 + x', LR17 `-32768 - x',
    LR18 `x - (-32768)', LR19 `x + (-32768)', LR2 `x + 0123456789' -- leading zeros still decide p,
    so 6 bytes even inside an ADD), all byte-exact and all re-run against DR by the gate.
    Why the first drafts were wrong, all three caught by the pool invariant rather than by a specimen:
    (a) prescan demanded through a classifier that unwrapped Econd while lowering matched raw
        patterns, so `x + (-32768)' demanded 3 bytes and allocated 0 -- [C179] seen from the other
        side: the two walkers must ask ONE function, not two equivalent-looking ones;
    (b) deleting the out-of-range branch from the two E2E-24 ADD arms without narrowing their
        PATTERNS left `x + 0123456789' matching and biasing HL by a value that does not fit -- 11
        byte-exact specimens became pool refusals.  A pattern may only admit what its body can lower;
    (c) `op = Ast.Add || <other-operand shape>' is true for ANY operator whose other operand is a
        plain identifier, so `x * 32768' allocated a cell nobody demanded and died on the size check
        instead of on its designed MB31 refusal [E2E-23: an unproven condition in selection].

C181. **Mixed DEC/BIN arithmetic routes for ADD and SUB and ONLY for ADD and SUB; the predicate that
says so must PARTITION, not overlap.**  A DEC operand and an out-of-range literal are two classes of
the same idea -- convert into HL, then use the ordinary binary lowering -- but their shape
requirements differ, and for a reason: a literal was measured with a compound partner (LR2), a DEC
variable never was (CB1-CB7 all pair it with a plain identifier), and SUB needs the partner to be
exactly where ?IS22N expects it.  Expressing both predicates as `either class may route' made the DEC
arm CLAIM literal nodes, match none of its own cases, and fire its internal assertion: 12 byte-exact
specimens turned into refusals.  Two predicates answering for one AST node must partition it -- the
DEC predicate excludes any node with a convertible literal operand.
    Still refused, with the refusal text naming exactly what is unpinned: MIXED MUL (CB8 is DR's one
    sample, where DR parks the LEFT operand although XCHG would be mechanically sound -- one sample is
    not a rule), DIV/EXP with a DEC operand, DEC sub-expressions, and MIXED RESULT INTO A DEC TARGET
    (CB10, IC2-IC4, IC6).  CB8's pinned marker moved with its message: the old text said "mixed-mode
    routes are unpinned", which stopped being true once ADD/SUB worked, and a refusal that no longer
    says something true is worse than no refusal.

C182. **An out-of-range FIXED literal must be ROUTED where DR is measured and REFUSED where it is
not -- never silently wrapped.  The way to find every such place is a position sweep, not the
symptom list.**  The divergence panel named six programs; a sweep of 15 new probes putting the
literal into every position the language allows found ELEVEN, including four nobody had probed (DO
bounds, element self-update, function arguments, a DIV dividend).  Every position now either converts
for real (scalar store; ADD/SUB both sides both signs) or stops at one choke point, `int_lit_checked',
whose refusal names the position it is in -- a condition/DO-bound comparison constant, an array
element store (all four forms), an element self-update, a procedure-call or function argument, a
direct HL load.  Before the guards, LP11's `if x > 32768' evaluated as `x + 32767' signed, so mine
TOOK a branch DR never reached and assigned y=1; LP12 stored a wrapped 0x8000 into z(1); LP16 handed
p a truncated value; all four completed with rc=0.  The divergence panel is now EMPTY (0 rows) and
the 14 positions that cannot be reproduced are NEGATIVES pinned by the DR .REL they decline to emit
plus a marker fragment taken from the compiler's ACTUAL stderr.
    One refusal is not a free win, twice over: when narrowing the routing predicate pushed LR8 out of
    the routed set it did not fall back to a designed refusal -- it went on BUILDING with wrong bytes,
    because the element self-update form biases HL from its own copy of the constant.  A position is
    only closed when the site that emits it refuses.
    [E2E-25/P5] INT -> DEC is characterized but NOT implemented: `e = 7' (IC5) and `decimal(b,5)'
    (IC7) are byte-exact SPECIMENS -- both convert via ?QI15D on the decimal stack -- while a bare
    integer VARIABLE or expression reaching a DEC target (IC1-IC4, IC6) refuses on the decimal store's
    guard, where DR emits `CALL ?QI15D' after the value is in HL (IC1's .REL, chain-ext at code 0020).
    That is Q8's gap with measured edges; closing it wants all six goldens and DECPOLY/DFACT/C162W
    in view at once, because that store route is tightly pinned.
- **C183** *(E2E-26 P2/P3, pointer and based address model implemented)* A `POINTER` is a 2-byte
  automatic cell in declaration order and is not hoisted; a `BASED` name is a view with **no** cell --
  it occupies nothing in AUTO STORAGE and its value lives at its pointer's offset. Reads and writes
  therefore all start from the POINTER's address, and DR never parks that address across a store:
  `read q` = `LHLD <p> / MOV E,M / INX H / MOV D,M / XCHG`, `q = const` = `LHLD <p> / MVI M,lo / INX H
  / MVI M,hi`, `q = <general>` = `<rhs> / PUSH H / LHLD <p> / POP D / MOV M,E / INX H / MOV M,D`.
  `p->q = v` emits bytes identical to `q = v` [P041], so the two spellings must share one encoder.
  `ALLOCATE` is a statement whose measured form is `allocate <based-name> set(<ptr>)` -- lowering to
  `LXI H,<bytes-of-based-type> / CALL ?ALLOP / SHLD <ptr>` with 2/1/3/5 for fixed/bit(8)/dec(5)/
  char(5) [PB7, PB8, PB14, PB13, PB15, PB6] -- and `FREE` takes a BASED name, lowering to
  `LHLD <ptr> / CALL ?FREOP` [PD9, PB7]; `free p` on a pointer is rejected by DR itself (BASED REQ,
  no .REL [AV1]), as is `allocate <type-name> to p` (BASED REQ + SYNTAX [PD6, PD8]). Assignment into
  a pointer cell is accepted only for the three right-hand shapes DR is sampled on -- `addr(local)`,
  `null()`, copy from another pointer -- and refuses everything else by name, because pointer
  arithmetic has no sample at all. Evidence: 21 byte-exact probes plus three programs LINKed from
  my own .REL and executed (PB7 `x=       100  y=       200 done`; PB1 `a=11 q=22 b=22`; PB3
  `first=11 second=22`), gate 688/688 with 121/121 negatives.
- **C184** *(E2E-26 P2/P3, reachability and instrumentation)* Two failure modes that no external
  oracle can show you. **(a)** Widening a declaration makes the holes below it live: `p->q = 100`
  raised a bare `Match_failure` on `lower_assign`'s outer match, a gap that had existed all along but
  was unreachable while `POINTER` refused at the layout switch. Every time an acceptance guard is
  widened, the lhs/rhs/operand shape tests downstream of it must be enumerated in the same pass --
  and the minimal way to find which spelling crashes is to build the neighbours: `q = 100` and
  `z = q` compiled while `p->q = 100` crashed, which isolated the defect to the `->` arm in one run.
  **(b)** A negative measurement from an instrument that cannot see the thing is not evidence:
  `cmp` against a nonexistent golden path reported four byte-exact probes as DIFFERS; `grep -c ALLOP`
  counts DR's symbol-table row so `1` did not mean a call was emitted; and a `CALL <hexaddr>` regex
  found nothing because DR prints `CALL ?ALLOP` with no address column, which is what made FREE look
  unimplemented. Before a conclusion is drawn from an absence, show that the same instrument detects
  the thing where it is known to be present.
