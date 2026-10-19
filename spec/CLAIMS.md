
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
4. Subnormals: none observed; whether the runtime ever produces one is unknown.
5. The exp-byte-0/zero encoding ambiguity noted above: unreachable from source,
   but recorded so nobody "fixes" it later.
