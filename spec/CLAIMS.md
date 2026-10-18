
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
- bytes(FIXED DEC(p,s)) = ceil((p+1)/2), INDEPENDENT of scale, directly
  observed at SEVEN precisions: p=1 -> 1 [R514], p=3 -> 2 [R513],
  p=4 -> 3 [R515], p=5 -> 3 [R503], p=7 -> 4 [R508], p=9 -> 5
  [R502/R505], p=15 -> 8 [R501/DFACT]. This is exactly Bind.bytes_of
  `RTdec (p,_) = (p+2)/2`, which was carried as a hypothesis; it is now
  confirmed across the entire accepted band, so accepting p<=15 involves
  NO extrapolation. DR itself stops at p=31 (`NOT IMP`, no .REL [R504]).
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
