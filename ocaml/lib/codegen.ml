(* lib/codegen.ml — MINIMAL 8080 code generator + LINK-80 .REL emitter for
   the PL/I-80 reimplementation. Deliberately scoped to the fixed-BINARY
   integer assignment subset needed by the first end-to-end specimen
   (P071A): assignment of an integer expression (literal, variable copy,
   +, and the -1 / small-const peepholes) to a simple scalar.

   Inputs shared with the IR builder: Parser AST + Bind storage rows.
   Encodings taken VERBATIM from oracle-verified $C disassembly and the
   reldump record stream (spec/notes/codegen.md §1-2, C056/C064). Nothing
   here is invented: every opcode is cross-checked against DR output.

   Anything outside the supported subset raises a clear
   [codegen: unsupported ...] failure rather than guessing. *)

open Rel80

(* [E2E-11 step 1a] Vbit1 is the ONE bit-string kind DR behaviour is pinned for:
   bit(1) is a single byte, significant in bit 7 ('1'b -> 0x80, '0'b -> 0x00)
   [E20A/E20B/E20D/E20E, C112].  Wide bit(n) has no byte-level sample at all, so
   it keeps refusing rather than borrowing this shape. *)
type vkind = Vint | Vfix of int | Vvar of int | Vdec of int * int | Vflt | Vbit1
   (* fixed/varying char capacity. Varying representation PROVEN
      [V101-V104]: length byte at offset 0, data at +1..+n, total
      n+1 bytes (binder authority Bind.bytes_of).
      [E2E-6] Vdec(p,s) = FIXED DECIMAL(p,s); storage bytes =
      ceil((p+1)/2) little-endian packed BCD with the sign nibble in
      the top nibble of the last byte -- confirmed on FOUR independent
      precisions: p=5 -> 3, p=7 -> 4, p=9 -> 5, p=15 -> 8
      [R503/R508/R502/R501 + DFACT], which is exactly Bind.bytes_of
      RTdec; codegen never re-derives sizes. *)
type var_info = { off : int; size : int; vk : vkind; w : int }
(* print width for FIXED BIN: min(9, digits(2^p-1)+4) -- banded rule
   matching ALL 16 probed points p=1..15,16,24 + default15 [N301-N308;
   C079]. NOT a linear formula. *)
let bin_digits10 n =
  let rec go x acc = if x < 10 then acc + 1 else go (x / 10) (acc + 1) in
  go n 0
let binw p = min 9 (bin_digits10 ((1 lsl p) - 1) + 4)
let dec_digits k =
  let k = abs k in
  if k = 0 then 1 else bin_digits10 k

type st =
  { base : int                        (* pool base = total pool bytes *)
  ; mutable items : rel_item list
  ; mutable pool : (int * int list) list  (* (data-addr, bytes) literal blocks *)
  ; mutable pool_next : int           (* next free pool offset *)
  (* [E2E-11 step 1a-ii] STATIC cells.  DR's DATA area is ONE block ordered
     [statics][literal pool][automatics] (C114, verified against E11D/E20D/E20E
     byte totals); `S(...)' and `A(...)' in the listing are naming classes, not
     sections, and the .REL carries plain Data-segment relocations for both.
     A static cell therefore has an ABSOLUTE data address (it sits below the
     pool base), while an automatic is still `declared offset + base', so
     addr_of needs to know which table a name lives in. *)
  ; mutable stat_addrs : (string * int) list
  ; mutable stat_total : int
  ; mutable files : string list   (* [E2E-11 step 2] uppercased FILE names *)
  ; mutable fmtq : int list

      (* [E2E-8] FIFO of pre-allocated PUT EDIT format-table addresses.  DR
         allocates EVERY format table in a block BEFORE any other pool item --
         proven by R1003 (table at *S(0000) while the 'AB' literal used by the
         EARLIER statement `c = 'AB'` sits at *S(0005)), R1021 (two tables,
         then both literals) and R1022 (a table inside a DO body still comes
         before the top-level literal).  Tables keep source/depth-first order
         among themselves, literals among themselves. *)
  ; mutable float_ret : bool
      (* [E2E-10] the current procedure RETURNS FLOAT: `return (e)` has to
         leave the value on DR's float stack and exit through JMP ?FPRET,
         plus ?RSBLK when the activation is recursive [R3038, FFACT] *)
  ; mutable fl_cells : (int * int list) list
  ; mutable str_cells : (int * int list) list
      (* [E2E-10] float literal cells already allocated, for DEDUPLICATION by
         identical bytes [C101: R3007/R3010/R3012/R3013 share cells] *)
  ; mutable dec_cells : (int list * int) list
                                        (* [R614] DEC literal cells are
                                           DEDUPLICATED by byte content:
                                           `d = 3; e = 3;` (both dec(9,2))
                                           emits LXI H,* S(0000) twice from
                                           the SAME 5-byte cell, so DR
                                           reuses rather than re-allocating.
                                           This CORRECTS the E2E-6 note that
                                           DEC cells are never deduplicated,
                                           which was inferred only from R505
                                           (two literals, DIFFERENT values).
                                           Keyed on the packed bytes, so a
                                           differing precision or scale (a
                                           different byte image) still gets
                                           its own cell. *)
  ; mutable lc : int                  (* code location counter *)
  ; mutable last_imm : int option     (* HL still holds this constant?
                                         [G114 b=3 folded from a=5] *)
  ; mutable temps : int               (* dynamic-DO bound temp slots
                                         (2 bytes each, AFTER declared
                                         area [Y302: temp@6 = pool2+4;
                                         Y305: temp@5 = pool1+4]) *)
  ; mutable lowered : int             (* statements actually lowered
                                         (discard-invariant witness) *)
  (* ---- E2E-5c call state [P401/P402/RFACT bytes] ---- *)
  ; mutable stop_seen : bool          (* explicit stop; suppresses the
                                         epilogue CALL ?STOPX [P401: no
                                         second STOPX after dbl code] *)
  ; mutable calls : Bind.call_site list   (* prescan FIFO, DFS order *)
  ; mutable procs : (string * Bind.proc_layout) list
  ; (* [E2E-11 step 5] true while lowering a procedure-only MODULE (no
       OPTIONS(MAIN), C136).  lower_proc's tail-guard and `appended' logic key on
       `not st.in_proc' because they describe a procedure appended AFTER a main
       block; a top-level module IS the whole file, so DR emits no JMP guard and
       no append address at all (golden/first/A starts at its copy-in ladder).
       Without this flag the module path would inherit main-only bookkeeping. *)
     mutable top_proc : bool
  ; mutable exts : (string * (int * bool * Bind.rt option * Bind.rt list)) list
      (* [E2E-11 step 4] EXTERNAL ENTRY targets from Bind.pl_exts: name ->
         (params, external_, RETURNS type, formal types).  Kept SEPARATE from
         `procs' on purpose -- an entry has no block, no body, no formal CELLS
         and no entry address of its own, and mixing it into procs would make
         the forward/internal CALL resolution take the CHAIN-ADDR branch and
         silently emit the wrong relocation. *)
  ; mutable entries : (string * int) list (* lowered proc -> entry lc *)
  ; mutable fcalls : (string * int) list  (* pending forward CALL slots *)
  ; mutable deref : string list           (* ptr-formal names, cur scope *)
  ; mutable floor : int                   (* layout total (cells+procs) *)
  ; mutable vars : (string * var_info) list
  ; mutable arrays : (string * int * int * int) list
    (* [E2E-20] (name, lb, ub, elem bytes) copied straight out of Bind.bind_arrays --
       bind.layout remains the ONLY storage authority; codegen derives nothing. *)
      (* scope chain head (lowername -> info); swapped per procedure
         body [PL/I nesting: inner declarations shadow outer] *)
  ; mutable dec_ret : (int * int) option
      (* [E2E-6] Some(p,s) while lowering the body of a procedure whose
         RETURNS type is FIXED DECIMAL(p,s): selects the ?DLDOP/
         ?DSTOP/JMP ?DCRET path for RETURN [DFACT @007B, R509 @0041] *)
  ; mutable guards : int      (* tail-guard JMPs emitted (max one) *)
  ; mutable appended : bool   (* a TOP-LEVEL procedure body has been
                                 appended at the tail address. Every
                                 golden lowers ALL procedures AFTER
                                 every main-block statement; a live
                                 main statement following an appended
                                 proc is an unobserved DR layout, so
                                 it fails loud instead of guessing. *)
  ; mutable guard_slots : int list
      (* [R404/R405/R406/R423/R429/R432/P404] tail-guard operand slots.
         TAIL GUARD (bytes, 37-specimen matrix): when a top-level
         PROCEDURE body is appended at the address control reaches from
         the MAIN tail (fall-through OR a forward reference such as a
         DO-loop exit jump) AND the epilogue CALL ?STOPX is emitted
         AFTER that appended code, DR emits 3 bytes at the append
         address, BEFORE the entry label / forward-call CHAIN-ADDR /
         prologue:
             C3 00 00            JMP <epilogue CALL address>
         resolved by the usual deferred triple (SET-LC(code,slot),
         RELOC(code,epi), SET-LC(code,epi)) emitted immediately BEFORE
         the epilogue CALL bytes themselves [R404: JMP operand @29 ->
         44 = the CD of the epilogue CALL ?STOPX; R405 @29 -> 6E;
         P404 @10 -> 2B; R423 @34 -> 57; R432 @0D -> 28]. NOTE the
         target is the epilogue CALL INSTRUCTION, not its operand slot
         -- the same continuation mechanism as the PUT/LXI-B triples
         [G113/P401]. CORRECTION to the earlier note in this file: the
         discriminator is NOT "can the main tail loop exit" but
         "is the epilogue displaced past appended proc code", i.e.
         (no explicit stop printed in place) AND (suppression window
         CLOSED at the proc entry). Open-window tails emit an
         unconditional back edge and LOSE the epilogue => no guard
         [RFACT/R407/R408/R410/R411/R414/R421/R422/R424/R425/R426/
         R427/R431]; stop-in-place tails need no jump either [P401/
         R409/R416/R417/R430/R433]. *)
  ; mutable in_proc : bool    (* lowering a procedure body *)
  ; mutable in_rec : bool     (* lowering a RECURSIVE proc body *)
  ; mutable call_stmt : string option
      (* [E2E-11/CALL, C122] set while lowering the DIRECT callee of a CALL
         statement.  DR keeps the two call forms disjoint: `CALL p;` against a
         value-returning p is NOT PROC (E24D fixed, E24H float), and a
         no-RETURNS p used in an expression is TYPES NOT= (E24I).  Naming the
         exact callee rather than using a depth counter means an expression
         call nested inside a CALL statement's argument list is still checked
         against the expression rule. *)
  ; mutable after_forever : bool  (* last MAIN stmt = no-exit loop/stop *)
  ; mutable secs : (string * int * int) list (* proc -> base,size excl pool *)
  ; mutable last_loop_edge : int }
(* label bookkeeping for GOTO resolution [G115/G116]:
   emitted-labels assoc (lowername -> lc); pending forward refs
   (lowername -> operand slot). *)
type lblstate = { mutable labs : (string * int) list
                ; mutable fwd : (string * int) list }

let push st it = st.items <- st.items @ [it]
let d st v = push st (Data (v land 0xff)); st.lc <- st.lc + 1
let reloc st seg v =
  push st (Reloc (seg, v)); st.lc <- st.lc + 2          (* inline: 2 bytes *)
let link st t valu name = push st (Link (t, valu, name))

(* allocate a constant-pool entry (ONE block per literal), returning its
   data-segment address. G113 evidence: DR emits a SET-LC(data,addr) per
   POOL BLOCK (string/dec literal allocation), not one flat byte run —
   single-block programs like G107/G106/P071D cannot distinguish, two
   strings prove it. *)
let pool_alloc st (bytes : int array) =
  let addr = st.pool_next in
  st.pool <- st.pool @ [(addr, Array.to_list bytes)];
  st.pool_next <- addr + Array.length bytes;
  addr

(* [E2E-16/C152] FIXED RULE, measured on 15 DR probes (e19src/PL1-PL13, PL16-PL17).
   The literal pool holds ONE cell per DISTINCT string content, allocated at first use,
   contiguous from data address 0.  A repeated content reuses the earlier address and
   consumes NO further pool bytes.  Verified at byte level, not by totals: PL3 'W','V' ->
   bytes 57 56; PL4 'WW','WW' -> 57 57 (one 2-byte cell); PL5 'W','WW' -> 57 57 57;
   PL6 'WW','W','WW' -> first-use order 0000:WW 0001:W and the repeat costs nothing;
   PL13 'AB','A' -> 41 42 41, so the key is EXACT CONTENT and not a prefix.  Cross-context
   too: PL10 (char store + PUT sharing 'W') and PL11 (two char stores) each pool ONE byte.
   DEF-DATA-SIZE for all of these is exactly unique-pool-bytes + automatics (including a
   nested procedure's own j) + call-descriptor cells -- e.g. PL1 8 = 1 + (n,m,q,c = 8?) ...
   see the table in spec/notes/e2e16-c152-pool-layout.md; MB40's 7 = 'W'(1) + n,m,j (6),
   which is the byte my OLD prescan demand double-counted.

   THE EMPTY LITERAL IS DIFFERENT AND THAT IS MEASURED: PL16 (`c = ''; c = '';') and PL17
   (two PUT lists containing '') each emit a SECOND SET-LC(data,0000) record with no DATA
   bytes, i.e. DR registers a zero-length pool BLOCK per occurrence even though the address
   is shared.  A non-empty repeat registers NO second block [PL11, one SET-LC + one DATA].
   So dedup applies to the ADDRESS, not to the empty-block registration. *)
let pool_str st (bytes : int array) =
  let l = Array.to_list bytes in
  match List.find_opt (fun (_addr, bs) -> bs = l) st.str_cells with
  | Some (addr, _) ->
      if l = [] then st.pool <- st.pool @ [ (addr, []) ];
      addr
  | None ->
      let addr = pool_alloc st bytes in
      st.str_cells <- st.str_cells @ [ (addr, l) ];
      addr

let pool_bytes (s : string) =
  Array.init (String.length s) (fun i -> Char.code (String.get s i))

(* ---- opcodes (8080) : all cross-checked against DR .REL bytes ---- *)
let op_lxi_b = 0x01
let op_lxi_d = 0x11
let op_lxi_h = 0x21
let op_lhld = 0x2a
let op_shld = 0x22
let op_dad_d = 0x19
let op_dad_h = 0x29   (* DAD H -- DR's doubling step [E2E-15/C148] *)
let op_dad_b = 0x09
let op_dcx_h = 0x2b
let op_inx_h = 0x23
let op_xchg = 0xeb
let op_call = 0xcd
let op_push_h = 0xe5
let op_pop_d = 0xd1
let op_mvi_a = 0x3e
let op_mvi_b = 0x06
let op_mov_b_a = 0x47   (* [V102/V103] len==cap store peephole *)
let op_mvi_m = 0x36     (* [V104] MVI M,00: empty-varying store *)
let op_push_psw = 0xf5  (* [W102] PSW guard before nested SLVTS *)
let op_jp = 0xf2      (* [X201/X202] GET skip byte; $C prints "JP";
                          REL byte is F2 = JPE (same family as the ^=
                          CA/"JZ" quirk [C072]); operand patched by a
                          deferred triple to the QIOOP call [X202] *)
let op_mov_l_a = 0x6f
let op_mov_h_a = 0x67
let op_add_a = 0x87
let op_sbb_a = 0x9f

(* [E2E-13/C141] the same strength reduction OUTSIDE a self-update.  The
   threshold is one higher than hl_bias's: DR repeats the single-byte
   increment while k <= 4 and only then switches to `LXI B,k / DAD B' (4 bytes).
   Five probes pin the k=4 boundary, and the discriminator between the two
   thresholds is WHICH ROUTE the assignment takes, not the surrounding code:
       n = n + 4  [K4, self-update, hl_bias]  -> XCHG ; LXI B,0004 ; DAD B
       x = x + 4  [X1, self-update, hl_bias]  -> LXI B,0004 ; DAD B
       t = n + 4  [X2, result into another v]  -> (INX H)*4
       r = x + 4  [T4, result into another v]  -> LHLD X ; (INX H)*4 ; SHLD R
       return (n + 4) [R4]                     -> (INX H)*4
       return (n + 5) [R5] / (x + 8) [T8]      -> LXI B,k ; DAD B
   Subtraction mirrors it: M1..M4 (n-1..n-4) repeat DCX H, N5/M6 (n-5, n-6) use
   `LXI B,two's-complement ; DAD B'.  WHY the tie at |B|=4 breaks two different
   ways is not established; both are reproduced from DR's bytes, and the
   cost reading (INX=1 byte vs LXI B+DAD B=4 bytes) is interpretation, not claim. *)
(* [E2E-13/C141] does the LEFT operand of an ADD have to be parked across a call?
   DR defers the load of a simple variable -- `CALL ; XCHG ; LHLD T ; DAD D' [P1,P2,P3,
   P9,P10,P11] -- because reading it after the call yields the same per-activation value:
   a recursive procedure's locals live in that activation's SVBLK shadow block and ?RSBLK
   restores them.  It cannot do that for a compound expression or a second call, whose
   value no longer exists anywhere to be re-read, so those go on the stack [P5,P12].
   Econd is just a parenthesis, which lower_hl already unwraps transparently [P401 dbl]. *)
(* [E2E-13] does this subexpression contain a procedure call?  Used to tell a call
   operand from one that NESTS another call, whose anonymous-cell numbering DR plans in a
   different order than I do [P9].  Esuffix is a call/index; Econd is a parenthesis. *)
(* [E2E-20/Priority 2] an Esuffix is NOT necessarily a call.  `a(5)' and `f(5)' parse to the
   SAME node shape, so the classification has to consult the bound declaration -- here the
   binder's own array list (st.arrays, copied from Bind.bind_arrays; codegen computes no layout
   of its own).  Before this, the check was purely syntactic (`| Ast.Esuffix _ -> true'), and
   that is the whole of AB9's divergence: `b = a(5) * 3' looked as if it contained a call, which
   vetoes mul_const_form, so I parked the operand (PUSH H / LXI H / POP D) where DR loads the
   literal straight into DE (`LHLD A+0008 / LXI D,0003 / ?IM22N', and AB23 pins the scalar
   analogue `LHLD x / LXI D,0003').  This is the SAME misclassification that had to be fixed for
   the element read and write routes, so there is one authority and one answer.
   NB: an element's SUBSCRIPT is still inspected, so `a(f(1))' counts as containing a call. *)
(* [E2E-20/Priority 2] ONE place answers "does this expression reference an array element?".
   It is a TOTAL function (no refusal, no lowering, no side effects) so every consumer can ask it:
   the classifier below, the read route, the four store forms, the PUT item width, the
   element-as-actual guard.  The answer comes from the binder's per-block array list, never from
   the source text.  Having one predicate is the point: AB6, AB9 and AC3 each failed for a
   different syntactic Esuffix test written independently, and each fix had to be found twice. *)
let hd_is_element arrays hd =
  match hd.Ast.e with
  | Ast.Eident h ->
      List.exists
        (fun (n, _lb, _ub, _ez) ->
          String.equal n (String.lowercase_ascii h.Ast.orig))
        arrays
  | _ -> false

let suf_is_element_arr arrays e =
  match e.Ast.e with Ast.Esuffix (hd, _) -> hd_is_element arrays hd | _ -> false

let rec expr_contains_call arrays e =
  (* TRUE for a call itself, and for anything that has one inside it.  A call
     OPERAND's nesting question is asked by call_operand_is_nested, which looks at the
     callee position and the argument list -- NOT at the operand as a whole, because
     the operand IS a call and asking it trivially answers yes.  (That is exactly the
     bug an earlier version of this function had: it returned false for a bare
     Esuffix, so `g(h(2))' looked unnested and P9 emitted instead of refusing.) *)
  match e.Ast.e with
  | Ast.Esuffix (hd, args) ->
      (not (hd_is_element arrays hd))
      || expr_contains_call arrays hd
      || List.exists (fun a -> expr_contains_call arrays a) args
  | Ast.Econd x -> expr_contains_call arrays x
  | Ast.Ebinary (_, l, r) ->
      expr_contains_call arrays l || expr_contains_call arrays r
  | Ast.Eprefix (_, x) -> expr_contains_call arrays x
  | _ -> false

let call_operand_is_nested arrays r =
  match r.Ast.e with
  | Ast.Esuffix (f, args) ->
      expr_contains_call arrays f
      || List.exists (fun a -> expr_contains_call arrays a) args
  | _ -> false

(* [E2E-14/C145] a nested-call chain in which EVERY actual is a literal, a simple
   variable, or another such chain.  This is exactly the class whose byte parity I
   MEASURED after fixing the anonymous-cell numbering: P9 `return (t + g(h(2)))' is
   byte-identical to DR, because every argument value cell it needs was allocated long
   before (a pool literal), so the only difference was the DESCRIPTOR slot numbering
   order.  A VARIABLE actual in this arm is not measured [C146], so it stays refused.
   A chain with a COMPOUND actual (D3 `g(h(k(2)))', D4 `g(h(2),k(3))', D5
   `g(2*h(3))') additionally needs an argument value cell created by the producing
   store, and DR's ordering rule for those (inner-first, at the store) is not yet
   separated from the per-site alternative -- the probes that would discriminate them
   hit an unrelated refusal first (`n * 2' in an expression context).  So those keep
   refusing with the reason named, rather than being accepted on an unmeasured guess. *)
(* [E2E-15/C153] measured class only.  Now that the constant-multiply route exists (C148),
   the D-series probes could actually be BUILT -- and they told me the C145 allowance was
   too broad: D3 `g(h(k(2)))' (depth 3) and D4 `g(h(2),k(3))' (two nested calls) compile and
   produce bytes that DIFFER from DR, while P9 `g(h(2))' and P1's inner chain are byte-identical.
   So the accepted shape is exactly: ONE nested call, at depth <= 2, every actual a literal,
   every call single-argument.  Anything deeper or wider refuses with the reason named --
   emitting a program I know differs in bytes is not acceptable even when it runs correctly. *)
let rec call_chain_simple depth e =
  match e.Ast.e with
  | Ast.Esuffix (_f, [ a ]) when depth <= 2 ->
      (match a.Ast.e with
       | Ast.Enumber _ -> true
       | Ast.Econd x -> call_chain_simple (depth + 1) x
       | Ast.Esuffix _ -> call_chain_simple (depth + 1) a
       | _ -> false)
  | _ -> false

let rec add_left_needs_push e =
  match e.Ast.e with
  | Ast.Econd x -> add_left_needs_push x
  | Ast.Ebinary _ | Ast.Esuffix _ -> true
  | _ -> false

let hl_bias_free st (b : int) =
  let ab = abs b in
  if ab = 0 then ()
  else if ab <= 4 then
    for _ = 1 to ab do d st (if b > 0 then op_inx_h else op_dcx_h) done
  else
    let w = b land 0xffff in
    d st op_lxi_b; d st (w land 0xff); d st ((w lsr 8) land 0xff); d st op_dad_b


(* variable data-segment address = pool base + declared auto offset.
   [int subset has no pool => base 0; matches DR SHLD/LHLD operands] *)
(* [E2E-20/Priority 2] WHOLE-ARRAY REFUSAL.  An array name appearing WITHOUT a subscript is not
   a value.  DR parses it (pass 1 clean) and rejects it in pass 2 with `TYPES NOT=' [GW1 `b = a',
   GW2 `a = 3', GW3 `put skip list(a)' -- golden/e2e230, all three: NO .REL emitted], and my
   compiler previously ACCEPTED all three and emitted a scalar load/store of the array's BASE
   CELL -- a silent wrong-value miscompile in the C139/C150/C162 class, now refused.
   addr_of is the single point through which every un-subscripted data reference flows, so the
   guard lives here rather than at the ~10 call sites.  resolve_suffix needs the base WITHOUT
   the guard, so it uses addr_of_raw (identical lookup, no refusal). *)
let whole_array_msg st name =
  if List.exists (fun (n, _lb, _ub, _ez) -> String.equal n (String.lowercase_ascii name))
       st.arrays then
    Some ("codegen: [TBD] whole-array reference to `" ^ name
            ^ "' used as a value [C159].  DR parses it and rejects it in pass 2 with "
            ^ "`TYPES NOT=' (GW1 `b = a', GW2 `a = 3', GW3 `put skip list(a)'; "
            ^ "golden/e2e230 -- DR emits NO .REL).  Reading or writing the base cell would "
            ^ "be a wrong-value miscompile, not a byte difference, so it refuses.")
  else None

let addr_of_raw st name =
  let li = String.lowercase_ascii name in
  (* STATIC cells come first: their offset is already an absolute DATA address
     (they live BELOW the pool base), so adding st.base would overshoot by
     exactly static_total + pool_total [C114, E20B/E20D/E20E] *)
  match List.assoc_opt li st.stat_addrs with
  | Some a -> a
  | None ->
      (match List.assoc_opt li st.vars with
       | Some vi -> vi.off + st.base
       | None ->
           (* [E20-21/P0] was a bare message, so the negative panel could not tell a
              reasoned refusal from a crash.  REVERT (`call p(i,exit)') reaches here with
              name="exit": a LABEL used as a value, which DR rejects in pass 2 rather than
              treating as an implicit FLOAT.  No semantics claimed -- only the wording fixed. *)
           failwith
             ("codegen: [TBD] undeclared " ^ name
                ^ " (no declaration in scope; PL/I would make it implicit FLOAT, but no                   DR sample shows such a name used as a call actual -- REVERSE/REVERT-class,                                     a label used as a value is TYPES territory"))

let addr_of st name =
  match whole_array_msg st name with
  | Some msg -> failwith msg
  | None -> addr_of_raw st name

let vk_of st name =
  (* [E2E-20] classification must refuse an un-subscripted array too, not just lowering: prescan
     asks vk_of to decide DEC/FLOAT demand, and answering Vint would size the pool around a
     reference that DR rejects.  See addr_of / GW1-GW3 [C159]. *)
  (match whole_array_msg st name with Some msg -> failwith msg | None -> ());
  let li = String.lowercase_ascii name in
  match List.assoc_opt li st.vars with
  | Some vi -> vi.vk
  | None ->
      (* same fix as above [E20-21/P0]: the message must contain [TBD] so a refusal is
         distinguishable from a crash by the panel, not by reading the trace. *)
      failwith
        ("codegen: [TBD] undeclared " ^ name
           ^ " (no declaration in scope)")

(* [E2E-20/Priority 2] ONE authoritative resolution of a subscripted name.

   `a(3)' parses to the same Esuffix node as `f(3)', so the meaning must come from the BOUND
   DECLARATION in the current scope -- never from text.  This function is the only place that
   decides, and every consumer branches on its result.  The E2E-19 attempt did not have this: it
   put an `if arr then <emit load>' inside lower_hl's existing arm, whose body continues
   UNCONDITIONALLY with `let ext = ...' and the whole call machinery.  An `if' with unit branches
   does not stop the following code, so the element emitted its LHLD and then the call route ALSO
   ran and died in `List.assoc nm st.procs' -- a control-flow error in my patch, not the
   "Esuffix resolved twice" story recorded in C165 [proven by a reach-through probe, E2E-20].
   Returning a discriminated result here makes fall-through impossible by construction. *)
let suf_is_element st e = suf_is_element_arr st.arrays e



(* [E2E-22] payload of Suf_element_dyn: everything needed to build DR's address ladder, and
   nothing else. `dyn_bias' is -lower_bound*element_size, so the relocated operand is
   (dyn_base + dyn_bias) -- AB2 addend 0xFFFE (lb=1), VB2 0xFFFC (lb=2), VB1 0x0000 (lb=0), which
   is what rules out C159's recorded `base + (lb-1)*(-sz)'. *)
type dyn_ref =
  { dyn_base : int
  ; dyn_bias : int
  ; dyn_idx : Ast.expr
  ; dyn_adj : int }

type suffix_ref =
  | Suf_element of int          (* array element; payload = relocated data address *)
  (* [E2E-22/P1] a RUNTIME-computed element address.  This is still an ARRAY reference -- it is
     never routed through the call machinery, which was the whole of C165's misdiagnosis.  `bias'
     is -lower_bound*element_size, so the relocated operand is (base+bias): AB2 (lb=1) carries
     data addend 0xFFFE, VB2 (lb=2) 0xFFFC, and VB1 (lb=0) 0x0000 -- which is what discriminates
     `base - lb*esz' from C159's recorded `base + (lb-1)*(-sz)': the DR goldens say the former.
     `idx' is the index expression and `adj' a literal ADDED TO THE INDEX VALUE (AB8 `a(i+1)'
     emits `LHLD i / INX H / DAD H', i.e. the +1 happens before the doubling, so it moves exactly
     one element -- an address-side +1 would move two [measured, AB8]). *)
  | Suf_element_dyn of dyn_ref
  | Suf_call of string * Ast.expr list

let resolve_suffix st (hd : Ast.expr) (args : Ast.expr list) =
  match hd.Ast.e with
  | Ast.Eident h ->
      let nm = String.lowercase_ascii h.Ast.orig in
      let is_arr =
        List.find_opt (fun (n, _lb, _ub, _ez) -> String.equal n nm) st.arrays
      in
      (match is_arr with
       | Some (name, lb, _ub, ez) ->
           (* the block-local ARRAY declaration wins over a same-named callable: AB1/AB3/RD1 all
              write `a: procedure options(main)' with `dcl a(5) fixed' INSIDE that block, so the
              declaration shadows the enclosing program label -- PL/I scoping, and DR compiles all
              of them.  This is scope-based shadowing, NOT a global array-over-procedure rule: a
              name bound as a procedure in THIS scope and declared as an array elsewhere is still a
              call, because we consult st.arrays, which is per-block. *)
           (match args with
            | [ a ] ->
                let ae = match a.Ast.e with Ast.Econd x -> x.Ast.e | _ -> a.Ast.e in
                (match ae with
                 | Ast.Enumber t ->
                     (match int_of_string_opt
                              (String.concat "" (String.split_on_char '_' t)) with
                      | Some sub ->
                          (* the element's relocated address: base cell of the array
                             + (sub - lb) * element bytes [C159], computed from the
                             RAW base because addr_of refuses un-subscripted array
                             names by design [GW1-GW3]. *)
                          Suf_element
                            ((addr_of_raw st name
                              + (sub - lb) * ez) land 0xffff)
                      | None ->
                          failwith
                            ("codegen: [TBD] array subscript '" ^ t
                             ^ "' is not a decimal literal [C159]"))
                 | Ast.Eident h ->
                     (* simple variable index: `a(i)' [AB2 AB10 VB1 VB2] *)
                     Suf_element_dyn
                       { dyn_base = addr_of_raw st name; dyn_bias = -lb * ez;
                         dyn_idx = a; dyn_adj = 0 }
                 | Ast.Ebinary (Ast.Add, l, ({ Ast.e = Ast.Enumber ks; _ } as rr)) ->
                     (* `a(i+1)' [AB8]: DR adds to the INDEX, then doubles -- see the
                        type comment above.  Only +1 is measured; anything wider keeps
                        refusing rather than extrapolating INX H repetition [E2E-13]. *)
                     (match l.Ast.e with
                      | Ast.Eident _ ->
                          let k = int_of_string
                            (String.concat "" (String.split_on_char '_' ks)) in
                          if k = 1 then
                            Suf_element_dyn
                              { dyn_base = addr_of_raw st name; dyn_bias = -lb * ez;
                                dyn_idx = l; dyn_adj = 1 }
                          else
                            failwith
                              (Printf.sprintf
                                 "codegen: [TBD] array subscript i+%d [C159]: only i+1 is \
                                  DR-measured (AB8). i+k would need k INX H steps between LHLD \
                                  and DAD H -- plausible but UNVERIFIED, so it refuses rather \
                                  than extrapolate [E2E-13]" k)
                      | _ ->
                          failwith
                            "codegen: [TBD] array subscript expression form [C159] (only a bare \
                             index variable and index+1 are DR-measured: AB2 AB8 AB10 VB1 VB2)")
                 | _ ->
                     failwith
                       "codegen: [TBD] runtime-variable array subscript [C159]: the index must be \
                        a simple variable or variable+1 (AB8). DR's ladder for anything else \
                        (multiply, deref, an element as index) is unmeasured, so it refuses.")
            | [] ->
                failwith
                  ("codegen: [TBD] whole-array reference to `" ^ h.Ast.orig
                   ^ "' [C159] (no array-valued expression is implemented)")
            | _ ->
                failwith
                  "codegen: [TBD] multi-dimensional array subscript [C159] (row-major                    with the last subscript fastest is characterized, not implemented)")
       | None -> Suf_call (nm, args))
  | _ -> Suf_call ("", [ hd ])   (* non-identifier target: existing code refuses it *)

(* [E2E-22/P1] DR's variable-index address ladder -- TWO forms, chosen by whether the biased
   operand equals the plain base. Leaves the element ADDRESS in HL:
     dyn_bias = 0  (lb = 0, VB1) : LHLD idx [; INX H*adj] ; DAD H ; LXI D,<reloc base> ; DAD D
     dyn_bias <> 0 (AB2 VB2 AB8 AB10):
                             LXI H,<reloc base+bias> ; PUSH H ; LHLD idx [; INX H*adj] ;
                             DAD H ; POP D ; DAD D
   The difference is mechanical, not stylistic: with bias 0 there is no base value that has to
   survive `LHLD idx' (which destroys HL), so DR computes 2*idx first and adds the base from DE
   afterwards -- 7 bytes, no stack traffic. With bias <> 0 the base MUST survive the LHLD, so DR
   parks it on the runtime stack, which is the C141 discipline applied to an address rather than
   to a value. The doubling is `DAD H' of the index and the second add comes from the parked
   copy, so the ladder's own PUSH/POP pair nests inside a caller's parking pair exactly as AB8
   and AB10 show. Nothing here allocates storage: bind.layout remains the only sizing authority. *)
let dyn_addr st (r : dyn_ref) =
  let opnd = (r.dyn_base + r.dyn_bias) land 0xffff in
  let emit_idx () =
    (match r.dyn_idx.Ast.e with
     | Ast.Eident h ->
         d st op_lhld; reloc st Data (addr_of st h.Ast.orig)
     | _ ->
         failwith
           "codegen: internal: dyn_addr index expression must be a simple variable")
    ;
    (* [AB8] `a(i+1)' increments the INDEX between the LHLD and the doubling, so it shifts the
       result by exactly one element (2 bytes) -- an address-side increment would shift two. *)
    for _ = 1 to r.dyn_adj do
      d st op_inx_h
    done
  in
  if r.dyn_bias = 0 then begin
    emit_idx ();
    d st op_dad_h;
    d st op_lxi_d; reloc st Data opnd;
    d st op_dad_d
  end
  else begin
    d st op_lxi_h; reloc st Data opnd;
    d st op_push_h;
    emit_idx ();
    d st op_dad_h;
    d st op_pop_d;
    d st op_dad_d
  end
let call_ext st name =
  (* CALL <external RTL>: operand slot = cd 00 00, immediately followed by
     LINK-CHAIN-EXT at the operand address [DR emits CHAIN-EXT per call site]
     — matches ?START/?STOPX/?IM22N/?ID22N/?IMDOP record streams *)
  d st op_call;
  let slot = st.lc in
  d st 0; d st 0;
  link st t_chain_ext (Some (Code, slot)) (Some name)

let op_jmp  = 0xc3
let op_jnz  = 0xc2
(* [E2E-15/C149] `op_jz = 0xc4` DELETED: it was never referenced, and 0xC4 is CNZ,
   not JZ (JZ is 0xCA).  The 0xCA bytes the skip/condition sites emit stay RAW literals on
   purpose -- [C072]/[R910] record that DR's listing LABELS that byte JPE while the .REL
   byte is CA, so naming the constant `op_jz` would assert a meaning the evidence explicitly
   declines to settle.  A wrong-but-unused name is worse than a raw byte with a comment. *)
let op_jp   = 0xf2
let op_jm   = 0xfa
let op_mov_a_m = 0x7e
let op_ora_m   = 0xb6
let op_dcr_c = 0x0d      (* DCR C (counted-copy loop) [R2031]; 0x05 = DCR B *)
let op_mov_a_h = 0x7c
let op_ora_a   = 0xb7

(* deferred forward-fixup triple [C062/G107/G113/G114]: placeholder
   already emitted at SLOT; now that target VALUE is known write
   SET-LC(code,slot) / RELOC(code,value) / SET-LC(code,value). *)
let emit_triple st slot value =
  link st t_set_lc (Some (Code, slot)) None;
  push st (Reloc (Code, value));
  link st t_set_lc (Some (Code, value)) None

(* ---- decimal constant POOL (DATA segment) ----
   PL/I-80 stores a literal-base `k ** n` base as a DECIMAL pool entry
   (proven across 6 samples 2/7/12/25/100 + P071D):
     p        = number of decimal digits of k
     bytes    = ceil((p+1)/2)            (PL/I dec storage: +1 sign nibble)
     packing  = little-endian, 2 BCD digits/byte as (hi<<4 | lo), most-
                significant nibble zero-padded [100 -> 00 01 ; 25 -> 25 00 ;
                12 -> 12 00 ; 7 -> 07 ; 2 -> 02]
   Pool sits at data offset 0; auto vars are placed ABOVE it, so every
   variable address = pool_total + declared_soffset (matches DR SHLD
   operands P071D z@1, G106 q@3=pool1+q2). DLDOP precision = p [MVI A,p].
   DATA-seg REL emission order [P071D reldump]:
     SET-LC(data,0) ; pool DATA bytes ; DEF-DATA-SIZE(abs, pool+auto) ;
     SET-LC(code,0) ; code ...   (no pool -> just DEF-DATA-SIZE ; SET-LC(code))
*)
let dec_pool_bytes p = (p + 1 + 1) / 2   (* ceil((p+1)/2) *)

let dec_digits_of k =
  let k = abs k in
  let rec go x acc = if x < 10 then acc + 1 else go (x / 10) (acc + 1) in
  if k = 0 then 1 else go k 0

(* literal text -> (magnitude of ALL digits, own digit count, number of
   fractional digits): "123.45" -> (12345,5,2), "1234" -> (1234,4,0) *)
let dec_lit_value (s : string) : int * int * int =
  let t = String.concat "" (String.split_on_char '_' s) in
  match String.split_on_char '.' t with
  | [ ip ] ->
      if ip = "" then failwith "codegen: malformed numeric literal [TBD]";
      (int_of_string ip, String.length ip, 0)
  | [ ip; fp ] ->
      let all = ip ^ fp in
      let mag = if all = "" then 0 else int_of_string all in
      (mag, dec_digits_of mag, String.length fp)
  | _ -> failwith "codegen: malformed decimal literal [TBD]"

let expr_kind_name (k : Ast.expr_kind) =
  match k with
  | Ast.Eident _ -> "ident"        | Ast.Eqstruct _ -> "qualified name"
  | Ast.Eqptr _ -> "pointer designator" | Ast.Enumber _ -> "numeric literal"
  | Ast.Estring _ -> "character literal" | Ast.Ebit _ -> "bit string"
  | Ast.Eprefix _ -> "prefix operator"  | Ast.Ebinary _ -> "binary operator"
  | Ast.Econd _ -> "condition"          | Ast.Esuffix _ -> "call/index"
  | Ast.Ebuilt _ -> "builtin"           | Ast.Eformat_ref _ -> "format ref"
  | Ast.Epicture _ -> "picture"


let bcd_pack (k : int) (p : int) =
  let nbytes = dec_pool_bytes p in
  let digs =
    let ds = string_of_int k in
    Array.init p (fun i -> Char.code (String.get ds i) - 48)   (* MSB-first *)
  in
  (* digits reversed to least-significant-first nibble order *)
  let lsf = Array.to_list digs |> List.rev in
  let nib = fun i -> try List.nth lsf i with _ -> 0 in
  Array.init nbytes (fun b -> ((nib (2 * b + 1)) lsl 4) lor (nib (2 * b)))


(* sum of decimal-pool bytes required by literal-base ** over all stmts
   (pure pre-scan, no side effects; mirrors pool_alloc ordering). *)

(* [E2E-6] prescan needs the same DEC-literal byte counts the lowering
   run will allocate.  Literal cells are TARGET-precision in bare
   assignment/RETURN position [R501/R505/DFACT] and OWN-digit-count as
   arithmetic operands [R509/R511].  cx carries every block's variable
   kinds and the current procedure's DEC return type; the map is built
   over the whole program, so a name declared with two DIFFERENT types
   is refused instead of silently mis-sizing the pool. *)
exception Fl_range of string

(* --- exact decimal-string helpers: no int64 magnitude limits ---------- *)
let ds_trim (s : string) : string =
  let t = String.trim s in
  let i = ref 0 in
  while !i < String.length t - 1 && t.[!i] = '0' do incr i done;
  if !i > 0 then String.sub t !i (String.length t - !i) else t

let ds_cmp (a : string) (b : string) : int =
  let a = ds_trim a and b = ds_trim b in
  if String.length a <> String.length b then
    compare (String.length a) (String.length b)
  else compare a b

let ds_double (s : string) : string =
  let carry = ref 0 in
  let out = Bytes.make (String.length s + 1) '0' in
  for i = String.length s - 1 downto 0 do
    let v = (Char.code s.[i] - 48) * 2 + !carry in
    Bytes.set out (i + 1) (Char.unsafe_chr (48 + v mod 10));
    carry := v / 10
  done;
  Bytes.set out 0 (Char.unsafe_chr (48 + !carry));
  ds_trim (Bytes.to_string out)

let ds_pow10 (n : int) : string = "1" ^ String.make n '0'

let ds_two_pow24 = "16777216"               (* 2^24: hidden bit plus 23 stored *)
let ds_two_pow23 = "8388608"

(* literal text -> (negative, magnitude digits, decimal scale), where
   value = digits * 10^(-scale).  Handles "1.5", "3E7", "-0.1", "1E-20",
   "1.4691E-39".  More than 18 significant digits is refused: DR garbles
   long tiny literals (R3029/R3041 compile to cells unrelated to their
   value), so that band cannot be reproduced byte-exactly by anything. *)
let fl_lit_split (text : string) : bool * string * int =
  let t0 = String.concat "" (String.split_on_char '_' text) in
  let t = String.map (fun c ->
      if c = 'd' || c = 'D' || c = 'e' then 'E' else c) t0 in
  let (neg, t) =
    if String.length t > 0 && t.[0] = '-' then
      (true, String.sub t 1 (String.length t - 1))
    else if String.length t > 0 && t.[0] = '+' then
      (false, String.sub t 1 (String.length t - 1))
    else (false, t)
  in
  let (mant, expo) =
    match String.index_opt t 'E' with
    | Some i ->
        let ex = String.sub t (i + 1) (String.length t - i - 1) in
        if ex = "" then failwith "codegen: malformed float literal [TBD]";
        (String.sub t 0 i, int_of_string ex)
    | None -> (t, 0)
  in
  let (ip, fp) =
    match String.split_on_char '.' mant with
    | [ a ] -> (a, "")
    | [ a; b ] -> (a, b)
    | _ -> failwith "codegen: malformed float literal [TBD]"
  in
  if String.length ip + String.length fp > 400 then
    failwith "codegen: absurdly long numeric literal [TBD]";
  let raw = ds_trim (ip ^ fp) in
  let rec go d sc =
    let l = String.length d in
    if l > 0 && d.[l - 1] = '0' then
      go (String.sub d 0 (l - 1)) (sc - 1)
    else (d, sc)
  in
  let (digits, scale) = go raw (String.length fp - expo) in
  let digits = if digits = "" then "0" else digits in
  if digits = "0" then (neg, "0", 0)
  else begin
    if String.length digits > 18 then
      failwith
        (Printf.sprintf
           "codegen: float literal %s has %d significant digits, beyond the band DR converts exactly [TBD] (R3029/R3041: long tiny literals compile to unrelated bytes)"
           text (String.length digits));
    (neg, digits, scale)
  end

(* single decimal digit division: divide string `a` by the single digit `dv`,
   returning (quotient, remainder) *)
let ds_div1 (a : string) (dv : int) : string * int =
  let q = Bytes.make (String.length a) '0' in
  let rem = ref 0 in
  for i = 0 to String.length a - 1 do
    let cur = !rem * 10 + (Char.code a.[i] - 48) in
    Bytes.set q i (Char.unsafe_chr (48 + cur / dv));
    rem := cur mod dv
  done;
  (ds_trim (Bytes.to_string q), !rem)

(* subtract non-negative decimal strings, a >= b *)
and ds_sub_small (a : string) (b : string) : string =
  let la = String.length a and lb = String.length b in
  let out = Bytes.make la '0' in
  let borrow = ref 0 in
  for i = la - 1 downto 0 do
    let x = Char.code a.[i] - 48 - !borrow
            - (if i - (la - lb) >= 0 then Char.code b.[i - (la - lb)] - 48 else 0) in
    if x < 0 then begin Bytes.set out i (Char.unsafe_chr (x + 58)); borrow := 1 end
    else begin Bytes.set out i (Char.unsafe_chr (x + 48)); borrow := 0 end
  done;
  if !borrow <> 0 then failwith "codegen: internal: negative remainder in float model";
  ds_trim (Bytes.to_string out)

(* long division of two non-negative decimal strings: (quotient, remainder).
   Schoolbook, one dividend digit at a time, with the running remainder kept
   as a STRING -- DR's float range reaches 2**127, i.e. ~39 decimal digits,
   which no machine integer holds. *)
let ds_divmod (a : string) (dv : string) : string * string =
  let dv = ds_trim dv in
  if dv = "0" then failwith "codegen: internal: zero divisor in float model";
  if ds_cmp a dv < 0 then ("0", ds_trim a)
  else if dv = "1" then (ds_trim a, "0")
  else begin
    (* dv's digit count is implied by the long-division walk *)
    let qbuf = Buffer.create (String.length a) in
    let remb = ref "" in
    for i = 0 to String.length a - 1 do
      remb := ds_trim (!remb ^ String.make 1 a.[i]);
      let c = ref 0 in
      while ds_cmp !remb dv >= 0 do
        remb := ds_sub_small !remb dv;
        incr c
      done;
      Buffer.add_char qbuf (Char.unsafe_chr (48 + !c))
    done;
    (ds_trim (Buffer.contents qbuf), ds_trim !remb)
  end

(* floor(digits * 10^(-scale) * 2^p) as a decimal string, plus the exact
   discarded remainder and its denominator, so the caller can decide a tie
   WITHOUT any floating-point.  p may be negative (values >= 2^24 need a
   right shift), which is why the denominator is a string, not a "how many
   digits were dropped" count. *)
let fl_shift (digits : string) (scale : int) (p : int)
    : string * string * string =
  (* numerator = digits * 10^(max(-scale,0)) * 2^(max(p,0)) *)
  let num = ref (digits ^ String.make (max (-scale) 0) '0') in
  for _ = 1 to max p 0 do num := ds_double !num done;
  (* denominator = 10^(max(scale,0)) * 2^(max(-p,0)) *)
  let den = ref (ds_pow10 (max scale 0)) in
  for _ = 1 to max (-p) 0 do den := ds_double !den done;
  let (q, r) = ds_divmod !num !den in
  (q, r, !den)

(* the binary exponent k with 2^k <= value < 2^(k+1).  A double estimate
   starts the search; every step is DECIDED BY EXACT COMPARISON, so float
   round-off cannot choose the exponent.  t(k) = floor(value * 2^24 / 2^k)
   is >= 2^24 exactly when value >= 2^k. *)
let fl_k (digits : string) (scale : int) : int =
  let dv =
    try float_of_string digits with _ ->
      failwith "codegen: cannot read float literal magnitude [TBD]"
  in
  (* this OCaml has no Float.log2: derive it, and note the estimate is only a
     STARTING POINT -- fl_k's loop decides every step by exact comparison *)
  let ln2 = Float.log 2.0 in
  let flog2 x = Float.log x /. ln2 in
  let est =
    try
      if scale >= 0 then
        int_of_float (Float.floor (flog2 dv -. float_of_int scale *. flog2 10.))
      else
        int_of_float
          (Float.floor (flog2 (dv *. (10. ** float_of_int (-scale)))))
    with _ -> 0
  in
  let est = if est <> est then 0 else est in
  let rec go k tries =
    if tries > 4000 then
      failwith
        "codegen: float literal exponent search did not converge [TBD]";
    (* t(k) = floor(value * 2^(23-k)) is >= 2^24 exactly when value >= 2^(k+1),
       and < 2^23 exactly when value < 2^k, so these two comparisons pin k *)
    let (tq, _, _) = fl_shift digits scale (23 - k) in
    if ds_cmp tq ds_two_pow24 >= 0 then go (k + 1) (tries + 1)
    else if tq = "0" || ds_cmp tq ds_two_pow23 < 0 then go (k - 1) (tries + 1)
    else k
  in
  go est 0

(* literal text -> DR's 4 bytes. *)
let mbf_encode (text : string) : bytes =
  let (neg, digits, scale) = fl_lit_split text in
  if digits = "0" then Bytes.of_string "\000\000\000\000"
  (* DR has NO negative zero: `-0.0` shares the all-zero cell [R3007] *)
  else begin
    let k = fl_k digits scale in
    let (tq, rem, den) = fl_shift digits scale (23 - k) in
    let t = int_of_string tq in   (* tq is in [2^23,2^24), so this is safe *)
    (* t is in [2^23, 2^24): the hidden bit sits at 2^23 and the 23 stored
       fraction bits below it.  Nearest, ties away from zero [R3020], the same
       tie direction the DECIMAL ROUND law C087 reached independently. *)
    (* nearest, ties away from zero: the discarded fraction is rem/den, so it
       rounds up exactly when 2*rem >= den [R3020] *)
    let up =
      if rem = "0" || rem = "" then false
      else ds_cmp (ds_double rem) den >= 0
    in
    let (t, k) =
      if up then
        let t = t + 1 in
        if t >= 1 lsl 24 then (1 lsl 23, k + 1) else (t, k)
      else (t, k)
    in
    let e = k + 129 in
    if e > 255 then
      raise
        (Fl_range
           (Printf.sprintf
              "magnitude 2**%d exceeds DR's float upper bound 2**127 [TBD] (DR pass-2 CONVERT rejects it: R3016/R3025)"
              k));
    if e < 0 then
      raise
        (Fl_range
           (Printf.sprintf
              "magnitude 2**%d is below DR's float lower bound 2**-129 [TBD] (DR rejects the deep cases with pass-2 CONVERT [R3015-R3017, R3026, R3028, R3047] but its SHALLOW-underflow band compiles to unrelated bytes [R3029/R3048]; I reproduce neither)"
              k));
    if e = 0 && t = 1 lsl 23 then
      raise
        (Fl_range
           "magnitude exactly 2**-129 collides with DR's zero encoding (bytes 00 00 00 00) [TBD]; the only exponent-byte-0 value ever observed is 2E-39, which has a NONZERO fraction [R3023]");
    let frac = t - (1 lsl 23) in
    Bytes.of_string
      (String.make 1 (Char.unsafe_chr (frac land 0xff))
      ^ String.make 1 (Char.unsafe_chr ((frac lsr 8) land 0xff))
      ^ String.make 1
          (Char.unsafe_chr (((frac lsr 16) land 0x7f)
                            lor (if neg then 0x80 else 0)))
      ^ String.make 1 (Char.unsafe_chr e))
  end

type pdec_ctx =
  { pd_vars : (string * vkind) list
  ; pd_procs : (string * (int * int) option) list
  ; pd_ret : (int * int) option
  ; pd_dec : (int * int * int) list ref
  ; pd_str : string list ref            (* [E2E-16/C152] string contents already demanded *)
  ; pd_fl : int list list ref
      (* [E2E-10] float literal cell byte-images already counted, so pool
         DEMAND counts each distinct 4-byte cell once (DR deduplicates them
         [C101, R3007/R3010/R3012/R3013]) *)
  ; pd_fl_ret : bool
      (* [E2E-10] the block being prescanned RETURNS FLOAT, so its literal
         operands become float cells rather than DEC/FIXED values *)
  ; pd_fl_procs : string list
  ; pd_callee_rt : string -> int -> Bind.rt option
      (* [E2E-11 step 4] is argument i of call `nm' a FLOAT formal?  The pool
         cell size of a literal argument depends on the FORMAL, so the prescan
         cannot decide from the literal's spelling (FDTEST passes `100' against
         a float formal and DR still allocates 4 MBF bytes).  A function field
         because the two walkers run at different times: prescan has only
         bind's layout, lowering has st. *)
      (* [E2E-10] names (lower-cased) of procedures whose RETURNS type is
         FLOAT BINARY(24).  pd_procs carries DEC precisions only and
         pd_vars holds VARIABLES, so float-returning callees need their own
         list -- without it the pool demand missed FFACT's return literal and
         every data address after the pool shifted down 4 bytes. *)
      (* [R614] distinct DEC literal cells already counted.  DR REUSES a
         decimal pool cell whose byte image is identical -- `d = 3; e = 3;`
         (both dec(9,2)) emits LXI H,* S(0000) twice against ONE 5-byte cell
         -- so pool DEMAND must count each distinct cell once.  Key is the
         packed image (precision, scale, scaled magnitude), i.e. exactly the
         byte content the lowering run compares in dec_pool. This replaces
         the E2E-6 assumption that DEC cells are never deduplicated, which
         was inferred from R505 (two literals, DIFFERENT values). *) }

(* [E2E-16/C152] pool DEMAND for one string-literal occurrence: 0 if that exact content was
   already demanded, else its byte length.  This mirrors pool_str at lowering time, and the
   mismatch between the two WAS C152: the demand summed String.length per OCCURRENCE while the
   allocator deduplicated by CONTENT, so `put skip list('W', n); ... put skip list('W', m);'
   reserved two cells and wrote one -- DEF-DATA-SIZE 8 against DR's 7 and every automatic
   shifted up one byte [MB40, golden/e2e191/MB40].  Keyed by exact content like PL13 proves. *)
let pdec_str_cell cx (v : string) : int =
  if List.mem v !(cx.pd_str) then 0
  else (cx.pd_str := v :: !(cx.pd_str); String.length v)

let pdec_pow10 n =
  let rec go v k = if k = 0 then v else go (v * 10) (k - 1) in go 1 n

(* count the pool bytes for one DEC literal occurrence, 0 if an
   identical cell was already counted [R614] *)
let pdec_dec_cell cx (p : int) (sc : int) (text : string) : int =
  let (mag, _own, ls) = dec_lit_value text in
  if ls > sc then 0          (* the lowering refuses this case *)
  else begin
    let key = (p, sc, mag * pdec_pow10 (sc - ls)) in
    if List.mem key !(cx.pd_dec) then 0
    else (cx.pd_dec := key :: !(cx.pd_dec); dec_pool_bytes p)
  end

(* parenthesised expressions arrive Econd-wrapped [N304]; prescan must
   see through them exactly like lowering does *)
(* [E2E-10] count the pool bytes for one FLOAT literal occurrence: 4 if the
   byte image is new, 0 if that identical cell was already counted.  The
   bytes come from the SAME encoder the lowering uses, so demand and layout
   cannot drift apart.  A literal the encoder refuses (out of range, the
   2**-129 collision, >18 digits) still counts 4 bytes: such a program is
   refused by the lowering and never emits a .REL, so the total is moot. *)
let pdec_fl_cell (cx : pdec_ctx) (text : string) : int =
  let key =
    try
      let b = mbf_encode text in
      List.init (Bytes.length b) (fun i -> Char.code (Bytes.get b i))
    with _ -> [ 0; 0; 0; 4 ]
  in
  if List.mem key !(cx.pd_fl) then 0
  else begin
    cx.pd_fl := key :: !(cx.pd_fl);
    4
  end

(* [E2E-10] float literals inside a float expression, in evaluation order.
   Fixed operands contribute nothing (they are converted at run time by
   ?QI15F) and a float call's arguments are frame temporaries, not pool. *)
let rec pdec_fl_expr (cx : pdec_ctx) (e : Ast.expr) : int =
  (* inlined: pdec_unwrap/unwrap_e are both defined below this point *)
  let e = match e.Ast.e with Ast.Econd x -> x | _ -> e in
  match e.Ast.e with
  | Ast.Enumber t -> pdec_fl_cell cx t
  | Ast.Ebinary (_, l, r) -> pdec_fl_expr cx l + pdec_fl_expr cx r
  | Ast.Eprefix (p, x) ->
      (match (match x.Ast.e with Ast.Econd y -> y | _ -> x).Ast.e with
       | Ast.Enumber k when p = Ast.Minus -> pdec_fl_cell cx ("-" ^ k)
       | _ -> pdec_fl_expr cx x)
  | Ast.Econd inner -> pdec_fl_expr cx inner
  | Ast.Esuffix (_hd, args) ->
      (* A FLOAT call argument that is a LITERAL needs its pool cell demanded
         here: DR passes it by address through the descriptor [R3062:
         `LXI H,*A(0010)`, the slot pointing at the 4-byte literal cell], so
         the cell exists before the variable area is based.  Without this the
         prescan sized the pool 2 bytes short, the variables overlapped the
         literal cell, and every downstream address shifted.  A VARIABLE
         argument needs no demand (its cell is a declared variable); a general
         expression argument has no DR sample and the lowering refuses it. *)
      List.fold_left
        (fun acc a ->
          match (match a.Ast.e with Ast.Econd x -> x | _ -> a).Ast.e with
          | Ast.Enumber t -> acc + pdec_fl_cell cx t
          | _ -> acc)
        0 args
  | _ -> 0

let pdec_unwrap (e : Ast.expr) =
  match e.Ast.e with Ast.Econd x -> x | _ -> e

let pdec_own_digits s =
  (* the literal's OWN digit count -- same rule the lowering run uses
     for operand-position DEC literals [R509 *2 -> 1 digit; R511 *1234
     -> 4 digits -> 3-byte cell] *)
  let (_mag, own, _ls) = dec_lit_value s in
  own

let rec pdec_operand_bytes (cx : pdec_ctx) (e : Ast.expr) =
  match e.Ast.e with
  | Ast.Econd x -> pdec_operand_bytes cx x
  | Ast.Enumber s ->
      pdec_dec_cell cx (pdec_own_digits s) 0 s
  (* [R608] ADD/SUB ALIGN the integer literal to its DEC partner: `p = p - 1`
     against dec(9,2) pushes MVI A,09 from a 5-byte cell holding 1.00, NOT
     the own-digit cell that * and / use [R509/R511/LOAN1]. Sizing the cell
     from the partner here is what keeps the pool aligned; if the partner's
     precision is unknown the lowering refuses, so nothing is under-sized
     silently. *)
  | Ast.Ebinary ((Ast.Add | Ast.Sub) as op, l, r) ->
      let unw x = match x.Ast.e with Ast.Econd y -> y | _ -> x in
      let islit x = match (unw x).Ast.e with Ast.Enumber _ -> true | _ -> false in
      let prec x =
        match (unw x).Ast.e with
        | Ast.Eident n ->
            (match List.assoc_opt (String.lowercase_ascii n.Ast.orig) cx.pd_vars
             with Some (Vdec (p, sc)) -> Some (p, sc) | _ -> None)
        | Ast.Esuffix (b, _) ->
            (match b.Ast.e with
             | Ast.Eident n ->
                 (match List.assoc_opt (String.lowercase_ascii n.Ast.orig)
                          cx.pd_procs with
                  | Some (Some (p, sc)) -> Some (p, sc)
                  | _ -> None)
             | _ -> None)
        | _ -> None
      in
      let side lit other =
        match (islit lit, prec other) with
        | true, Some (po, sc) ->
            let k = match (unw lit).Ast.e with
                    | Ast.Enumber t -> t
                    | _ -> assert false
            in
            pdec_dec_cell cx po sc k
        | _ -> pdec_operand_bytes cx lit
      in
      ignore op; side l r + side r l
  | Ast.Ebinary (_, l, r) -> pdec_operand_bytes cx l + pdec_operand_bytes cx r
  | Ast.Eprefix (_, x) -> pdec_operand_bytes cx x
  (* [E2E-7A slice 3] ROUND(a,n): the ARGUMENT's literals need pool cells like
     any other DEC operand -- LOAN1's `round(i*P/1200, 2)` puts the 1200 cell
     inside the call, and under-counting it moves the AUTO base (R813 caught
     that: my first build sized the pool 3 bytes short).  The digit count n is
     an IMMEDIATE byte (it becomes MVI A, s-n), never a pool cell. *)
  | Ast.Ebuilt ("ROUND", [ a; _ ]) -> pdec_operand_bytes cx a
  | Ast.Ebuilt ("DECIMAL", _) -> 0   (* integer argument: no DEC cell *)
  | _ -> 0

(* is this expression DEC-typed at prescan time? (mirrors codegen's
   is_dec_expr but reads the prescan context instead of st) *)
let rec pdec_is_dec (cx : pdec_ctx) (e : Ast.expr) =
  match e.Ast.e with
  | Ast.Econd x -> pdec_is_dec cx x
  | Ast.Eident n ->
      (match List.assoc_opt (String.lowercase_ascii n.Ast.orig) cx.pd_vars
       with Some (Vdec _) -> true | _ -> false)
  | Ast.Ebuilt ("DECIMAL", _) -> true
  | Ast.Esuffix (b, _) ->
      (match b.Ast.e with
       | Ast.Eident n ->
           (match List.assoc_opt (String.lowercase_ascii n.Ast.orig)
                    cx.pd_procs with
            | Some (Some _) -> true
            | _ -> false)
       | _ -> false)
  | Ast.Ebinary (_, l, r) -> pdec_is_dec cx l || pdec_is_dec cx r
  | Ast.Eprefix (_, x) -> pdec_is_dec cx x
  | _ -> false

let parse_int_const (s : string) =
  (* [E2E-11 step 5] every caller reaches this only after some arm has already
     decided the literal is an INTEGER.  A FLOAT literal arriving here means that
     classification went wrong upstream, and until now the failure was a bare
     OCaml `int_of_string' exception: Q1 (`a: procedure(x) returns (float) ...
     return (2.0)' with NO options(main)) died with `Fatal error: exception
     Failure("int_of_string")', naming neither the construct nor the cause.
     That is also a fail-loud protocol violation in this project's own terms --
     run_negatives() greps stderr for the literal string "[TBD]", so a crash
     would register as "wrong refusal" and hide the reason.  The real defect is
     structural (emit_program never sets st.float_ret, because only lower_proc
     does, so a top-level value-returning FLOAT procedure takes the integer
     return path entirely), and that is deliberately NOT fixed in this commit:
     it changes the entry structure that all 390 specimens depend on.  This only
     turns the crash into a refusal that says what is missing. *)
  let t = String.concat "" (String.split_on_char '_' s) in
  match int_of_string_opt t with
  | Some v -> v
  | None ->
      failwith
        ("codegen: [TBD] non-integer literal '" ^ s
         ^ "' reached the FIXED path -- expression-domain misrouting, not a "
         ^ "syntax error.  For a top-level procedure this is the known missing "
         ^ "no-options(main) path: emit_program selects the main prologue and "
         ^ "the return convention unconditionally, so st.float_ret is never set "
         ^ "for a file whose outermost block is a value-returning procedure "
         ^ "(Q1/Q3 probes, spec/notes/e2e11-step5-gap-ranking.md)")


let rec prescan_expr (cx : pdec_ctx) (e : Ast.expr) =
  match e.Ast.e with
  | Ast.Ebinary (Ast.Exp, l, r) ->
      let extra =
        match (l.Ast.e, r.Ast.e) with
        | Ast.Enumber bs, Ast.Enumber _ ->
            let k = String.concat "" (String.split_on_char '_' bs) in
            dec_pool_bytes (String.length k)
        | _ -> 0
      in
      prescan_expr cx l + prescan_expr cx r + extra
  | Ast.Ebinary (Ast.Sub, { Ast.e = Ast.Enumber a; _ },
                 { Ast.e = Ast.Enumber b; _ }) ->
      (* [N301/N306] const-minus-const DLDOP operands each take a
         dec pool entry *)
      let pint s =
        parse_int_const s
      in
      dec_pool_bytes (dec_digits (pint a))
      + dec_pool_bytes (dec_digits (pint b))
  | Ast.Ebinary (_, l, r) -> prescan_expr cx l + prescan_expr cx r
  | Ast.Eprefix (_, x) -> prescan_expr cx x
  | Ast.Ebuilt (_, es) ->
      List.fold_left (fun a x -> a + prescan_expr cx x) 0 es
  | Ast.Esuffix (hd, args) ->
      (* [E2E-11 step 4, FDTEST] a FLOAT-literal call argument needs its 4-byte
         MBF cell demanded in EVERY expression position.  The
         Sassign-with-float-target path already did this through pdec_fl_expr
         [R3062], which is exactly why R3062 stayed byte-exact while FDTEST did
         not: FDTEST's call sits inside a PUT item, and PUT items are counted
         through prescan_expr, which had no Esuffix arm at all.  The result was
         a pool base 2 bytes short, so the first automatic variable landed on
         top of the constant's low half -- FDTEST referenced the literal 100.0
         at 000b-000e and the index `i' at 000d, and `STA I' would have
         trampled the constant while every address in the dump still looked
         plausible.
         FIXED literal arguments are deliberately NOT counted here: const_cells
         owns them, and counting them in both places is the regression this
         replaces (adding 4 bytes in const_cells moved R3062 from exact to
         0018 vs DR's 0014).  Dedup goes through cx.pd_fl, the same bookkeeping
         pdec_fl_expr uses, so a literal demanded twice contributes once. *)
      let tl =
        match hd.Ast.e with
        | Ast.Eident h -> String.lowercase_ascii h.Ast.orig
        | _ -> ""
      in
      List.fold_left
        (fun acc (i, a) ->
          match (match a.Ast.e with Ast.Econd x -> x | _ -> a).Ast.e with
          | Ast.Enumber t ->
              (match cx.pd_callee_rt tl i with
               | Some (Bind.RTfloat 24) -> acc + pdec_fl_cell cx t
               | Some (Bind.RTfloat p) ->
                   failwith
                     ("codegen: FLOAT BINARY(" ^ string_of_int p
                      ^ ") formal is unsupported [TBD] (only BINARY(24) is "
                      ^ "characterized; C100/C101)")
               | _ -> acc)
          | _ -> acc)
        0 (List.mapi (fun i x -> (i, x)) args)
  | _ -> 0

type chain = C2 of string * string * string   (* lit || var [W101] *)
           | C3 of string * string * string   (* lit || var || lit [W102] *)
type pitem = PIlit of string | PIvar of Ast.name | PInum of Ast.expr
(* [E2E-22/P4] DR's runtime SKIP count, measured on SK3/SK4 (`put skip(one) list(...)'):
     LHLD v ; MOV A,L ; CALL ?SKPOP
   Only the LOW byte of the value is used -- the same 8-bit quantity the `MVI A,n' immediate
   route carries, so a FIXED(15) count is truncated by DR, not range-checked.  Only a bare
   variable is measured: arithmetic, an array element, or a call would need a value in A across
   something that destroys A, and DR's form for those is unmeasured [C141], so they refuse.
   Defined here (before the PUT lowerers) because it uses only the early emitters; it cannot
   call lower_hl, which is bound later in the file. *)
let emit_skip_count st e =
  match e.Ast.e with
  | Ast.Eident h ->
      d st op_lhld; reloc st Data (addr_of st h.Ast.orig);
      d st 0x7d;
      call_ext st "?SKPOP"
  | _ ->
      failwith
        "codegen: [TBD] PUT SKIP count expression is not a bare variable [E2E-22]: DR's measured \
         form is `LHLD v / MOV A,L / CALL ?SKPOP' (SK3 SK4).  An arithmetic or subscripted count \
         would leave the value in A across something that destroys it, and that shape is \
         unmeasured [C141], so it refuses rather than guesses."

(* [E2E-22/P4] a PUT SKIP count is one of three things, and SK1-SK4 pin which is which:
     absent          -> nothing emitted                  [bare `put list(...)`]
     literal n       -> MVI A,n ; CALL ?SKPOP            [SK2 `put skip(2) list(x)']
     expression e    -> lower_hl(e) ; MOV A,L ; CALL ?SKPOP   [SK3 `put skip(one) list(x)']
   DR takes only the LOW byte of the expression value -- `MOV A,L' -- which is the same 8-bit
   quantity the immediate form carries, so the count is a byte even when the expression is a
   16-bit FIXED.  This one shape is all that stood between the compiler and the two PLI-2000
   integration programs (ARRAY, PASSARAY), both of which write `put skip(one) list(...)'. *)
type put_skip = Sk_none | Sk_lit of string | Sk_expr of Ast.expr
type put_shape = Pnone | Plit of put_skip * string
               | Pvar of string option * Ast.expr
               | Pcat of put_skip * chain
               | Pitems of put_skip * pitem list

(* flatten a (left-assoc per our parser) || chain to operands
   left-to-right; only the proven shapes C2 [lit;varying] and
   C3 [lit;varying;lit] survive; anything else -> None -> [TBD]
   at lowering [W101/W102] *)
let flatten_cat (e : Ast.expr) =
  let rec leaves2 x acc =
    match x.Ast.e with
    | Ast.Ebinary (Ast.Cat, l, r) ->
        (* prepend accumulator => recurse RIGHT first to end up with
           SOURCE order left-to-right *)
        (match leaves2 r acc with
         | Some a -> leaves2 l a
         | None -> None)
    | Ast.Estring s -> Some (("STR", s) :: acc)
    | Ast.Eident n -> Some (("VAR", n.Ast.orig) :: acc)
    | _ -> None
  in
  match leaves2 e [] with
  | Some ls ->
      (match ls with
       | [ ("STR", l); ("VAR", v) ] -> Some (C2 (l, v, ""))
       | [ ("STR", l); ("VAR", v); ("STR", r2) ] ->
           Some (C3 (l, v, r2))
       | _ -> None)
  | None -> None

(* item classification (syntax-only; char-vs-numeric resolved at
   lowering where the binder's vk is known). Numeric CONSTANTS alone
   have no DR evidence -> reject. [N301-N306] *)
let classify_item (x : Ast.expr) =
  match x.Ast.e with
  | Ast.Estring v -> Some (PIlit v)
  | Ast.Eident n -> Some (PIvar n)
  | Ast.Ebinary _ | Ast.Eprefix _ -> Some (PInum x)
  | Ast.Econd inner -> Some (PInum inner)  (* parens grouping [N304] *)
  | Ast.Esuffix (hd, args) when args <> [] ->
      (* [RFACT @3B-46] function-call item: pair + LXI H,*A(slot) +
         CALL; the result already sits in HL when the numeric chain
         reads it (MVI A,9; QICOP follows the CALL directly).
         [E2E-9/DECPOLY] the arity restriction is gone -- DR treats a
         3-argument decimal call item exactly like a 1-argument integer
         one (`LXI H,*A(0048) / CALL P / MVI A,12 / MVI B,04 / ?QDCOP`). *)
      (match hd.Ast.e with
       | Ast.Eident _ -> Some (PInum x)
       | _ -> None)
  | _ -> None


let match_skip_ctl (items : Ast.put_item list) =
  match items with
  | Ast.Pi_ctl ("SKIP", Some { Ast.e = Ast.Enumber c; _ }) :: tl ->
      Some (Sk_lit c, tl)
  | Ast.Pi_ctl ("SKIP", None) :: tl ->
      Some (Sk_lit "1", tl)   (* bare SKIP = 1 [N302: MVI A,01] *)
  (* [E2E-22/P4] a non-literal count is no longer a reason to refuse the whole PUT: the
     expression route is DR-measured (SK3/SK4).  Anything that is not SKIP-first still
     falls through to the subset refusal. *)
  | Ast.Pi_ctl ("SKIP", Some e) :: tl ->
      Some (Sk_expr e, tl)
  | _ -> None

(* accepted shapes: literal [G107/G108/G113] or a SINGLE char/varying
   variable [V101/V106]; optional SKIP(const). Pnone -> [TBD]. *)
let all_data (items : Ast.put_item list) =
  let rec go acc = function
    | [] -> Some (List.rev acc)
    | Ast.Pi_data x :: tl -> go (x :: acc) tl
    | _ -> None
  in
  go [] items

(* PUT forms other than PUT LIST are NOT implemented.  Corpus audit REV
   2 defect D1: PUT EDIT / PUT ITEM / bare PUT SKIP used to escape as an
   uncaught Match_failure from this function during the pool prescan
   (IFACT, OPTIMIST, SAMPLE).  They are refused by name now, which is
   the project's fail-loud contract; the implemented subset is PUT LIST
   with optional leading SKIP control item [G107/G108/N301-N306]. *)
let put_kind_str (k : Ast.put_kind) =
  match k with
  | Ast.List_ -> "LIST"
  | Ast.Edit -> "EDIT"
  | Ast.Item -> "ITEM (also the parse form of bare PUT SKIP;/PAGE;)"
  | Ast.Editsk _ -> "SKIP(n) without LIST"

let match_put_list_lit (s : Ast.stmt) =
  match s.Ast.st with
  | Ast.Sput { kind = (Ast.Edit | Ast.Item | Ast.Editsk _) as k; _ } ->
      failwith (Printf.sprintf
                  "codegen: PUT %s deferred [TBD] (line %d; only PUT LIST \
                   is implemented; format/picture editing needs the \
                   ?EDITF/?EDTOV/?QDDSL route family)"
                  (put_kind_str k) s.Ast.spos.Source.line)
  (* [E20-21/P0] BEFORE the plain case, so an unadorned `put [skip] list(...)' still matches
     above.  These two arms replace a BARE Match_failure with a reasoned refusal: a PUT naming a
     FILE stream (corpus KEYFILE `put file(keys) list(name,k)') or carrying ON options (corpus
     CREATE) fell off the end of this match and crashed inside bind/codegen prescan, which is
     outside this project's refusal contract -- rc!=0 is not evidence, `[TBD]` is.  The blocker is
     the ?OIOOP/?SIOOP file-I/O route, the same one that already stops the seven
     named-sequential-FILE corpus programs; it is NOT an array gap, and nothing here implements
     file I/O -- it only names what is missing. *)
  | Ast.Sput { kind = Ast.List_; stream = Some _; _ } ->
      failwith
        (Printf.sprintf
           "codegen: [TBD] PUT LIST naming a FILE stream (line %d): `put file(...) list(...)'             needs the ?OIOOP/?SIOOP file-I/O route -- same blocker as the named-sequential FILE             programs, not an array gap" s.Ast.spos.Source.line)
  | Ast.Sput { kind = Ast.List_; on_opts = _ :: _; _ } ->
      failwith
        (Printf.sprintf
           "codegen: [TBD] PUT LIST with ON options (line %d): ON-expression handling needs the             ?OIOOP/?SIOOP file-I/O route, not an array gap" s.Ast.spos.Source.line)
  | Ast.Sput { stream = None; on_opts = []; kind = Ast.List_; items } ->
      let (sk, rest) =
        match match_skip_ctl items with
        | Some x -> x
        | None -> (Sk_none, items)
      in
      let one x = match classify_item x with
                   | Some i -> [i] | None -> []
      in
      match rest with
      | [ Ast.Pi_data ({ Ast.e = Ast.Estring v; _ } as x) ] ->
          ignore x; Plit (sk, v)          (* byte-frozen 3a path *)
      | [ Ast.Pi_data x ] ->
          (match flatten_cat x with
           | Some ch -> Pcat (sk, ch)     (* proven concat shapes *)
           | None ->
               (match one x with
                | [ it ] -> Pitems (sk, [it])
                | _ -> Pnone))
      | _ when List.length rest >= 2 ->
          (match all_data rest with
           | Some xs ->
               let its = List.map classify_item xs in
               if List.for_all (fun o -> o <> None) its then
                 Pitems (sk, List.map
                   (function Some i -> i | None -> assert false) its)
               else Pnone
           | None -> Pnone)
      | _ -> Pnone
  | _ -> Pnone

(* true iff the literal text is an integer (PL/I float literals like "2.5" and
   "1.5e3" are not).  Used to keep numeric-literal arms out of float text. *)
let is_int_literal (s : string) =
  match int_of_string_opt (String.concat "" (String.split_on_char '_' s)) with
  | Some _ -> true
  | None -> false

(* ---- [E2E-8] PUT EDIT: the compiled format list --------------------
   Decoded byte-wise from 11 DR tables (golden/e2e11/ R1001-R1010,
   R1018-R1020, IFACT).  A format table is a DATA pool item:

       80 00 | record record ... record | 81

   and record length is FIXED PER OPCODE (that is what R1018 vs R1019 vs
   R1020 pin down):
       f(w)    -> 00 w FF   [R1001 f(3), R1002 f(12), R1019 f(1), IFACT f(2)/f(7)]
       f(w,d)  -> 00 w d    [R1018 f(6,2) -> 00 06 02]
       a       -> 03 FF     [R1003, R1010, IFACT]
       a(w)    -> 03 w      [R1008 a(5), R1020 a(3)]
       skip    -> 0C FF     [R1004, R1005, R1010, IFACT]
       page    -> 0F FF     [R1007]
   UNPINNED and therefore not modelled: the header's second byte (0x00 in all
   11 samples), counted skip/page (skip(n) is unsampled), and every other edit
   operator (x/b/e/v/i/n/m/c/p/picture/remote/rep-group).  Those refuse.
*)
let fmt_w (e : Ast.expr) =
  match e.Ast.e with
  | Ast.Enumber t ->
      let v = parse_int_const t in
      if v < 0 || v > 255 then
        failwith "codegen: PUT EDIT width outside 0..255 [TBD]";
      v
  | _ -> failwith "codegen: PUT EDIT non-constant width [TBD] \
                   (only literal widths are sampled)"

let fmt_spec (it : Ast.put_item) : int list =
  match it with
  | Ast.Pi_ctl (k, None) when k = "SKIP" -> [ 0x0c; 0xff ]
  | Ast.Pi_ctl (k, None) when k = "PAGE" -> [ 0x0f; 0xff ]
  | Ast.Pi_ctl (_, Some _) ->
      failwith "codegen: PUT EDIT counted SKIP/PAGE is unsampled [TBD] \
                (only the bare form's second byte 0xFF has been observed)"
  | Ast.Pi_fmt { fkey = "F"; fargs = [ w ]; fcount = None } ->
      [ 0x00; fmt_w w; 0xff ]
  | Ast.Pi_fmt { fkey = "F"; fargs = [ w; d ]; fcount = None } ->
      [ 0x00; fmt_w w; fmt_w d ]
  | Ast.Pi_fmt { fkey = "A"; fargs = []; fcount = None } -> [ 0x03; 0xff ]
  | Ast.Pi_fmt { fkey = "A"; fargs = [ w ]; fcount = None } -> [ 0x03; fmt_w w ]
  | Ast.Pi_fmt { fkey = k; _ } ->
      failwith (Printf.sprintf
                  "codegen: PUT EDIT operator %s is unsampled [TBD] \
                   (only F and A formats are decoded from DR tables)" k)
  | _ ->
      failwith "codegen: PUT EDIT format item form unsampled [TBD] \
                (counted, grouped, picture, remote and rep-group formats \
                 are not decoded)"

let fmt_table_bytes (specs : Ast.put_item list) =
  if specs = [] then failwith "codegen: PUT EDIT with an empty format list [TBD]";
  Array.of_list (([ 0x80; 0x00 ] @ List.concat_map fmt_spec specs) @ [ 0x81 ])

(* `put edit(items)(specs);' -- default stream, no ON options, no leading
   SKIP/PAGE control item (that combination is unsampled: in every EDIT probe
   the skip lives INSIDE the format list).  Items accept exactly what PUT LIST
   prepares -- char literal, fixed-bin variable/expression, char varying --
   because [R1001/R1003/R1010/IFACT] show DR reusing the same value preparation
   with ?EDTOV in place of ?PNCOP/?PNVOP.  FIXED DECIMAL items are refused at
   lowering: no DR sample puts a DEC item through an edit list. *)
let match_put_edit (s : Ast.stmt) =
  match s.Ast.st with
  | Ast.Sput { stream = None; on_opts = []; kind = Ast.Edit; items } ->
      let rec data acc = function
        | [] -> None                     (* no format list: not an EDIT shape *)
        | Ast.Pi_fmtlist specs :: tl ->
            if tl <> [] || acc = [] then None
            else Some (List.rev acc, specs)
        | Ast.Pi_data x :: tl -> data (x :: acc) tl
        (* a control/rep/picture/remote item in the DATA half of an EDIT list
           is unsampled: refuse rather than guess where it belongs *)
        | _ -> None
      in
      (match data [] items with
       | Some (ds, specs) ->
           let its = List.map classify_item ds in
           if List.for_all (fun o -> o <> None) its then
             Some (List.map (function Some i -> i | None -> assert false) its,
                   specs)
           else None
       | None -> None)
  | _ -> None

(* [E2E-8] depth-first source-order walk: every accepted PUT EDIT statement
   in the order lowering will reach it.  Used to pre-allocate the format
   tables at the front of the pool, which is where DR puts them. *)
let rec edit_stmts (ss : Ast.stmt list) : Ast.stmt list =
  List.concat_map
    (fun s ->
      match s.Ast.st with
      | Ast.Sput _ ->
          if match_put_edit s <> None then [ s ] else []
      | Ast.Sdobegin body -> edit_stmts body
      | Ast.Sif { then_; els; _ } ->
          then_ :: (match els with Some e -> [ e ] | None -> [])
          |> edit_stmts
      | Ast.Sdowhile { body; _ } | Ast.Sdoforever body | Ast.Sdoto { body; _ } ->
          edit_stmts [ body ]
      | Ast.Sproc b -> edit_stmts b.Ast.blk.Ast.bstmts
      (* [E2E-11 step 2] same reason as prescan_stmt: an ON handler is inline
         code, and a PUT EDIT in one must be in the FIFO or prealloc_fmt_tables
         hits `assert false' at lowering time. *)
      | Ast.Son { handler; _ } -> edit_stmts [ handler ]
      | _ -> [])
    ss

let prealloc_fmt_tables st (ss : Ast.stmt list) =
  st.fmtq
    <- List.map
         (fun s ->
           match match_put_edit s with
           | Some (_, specs) -> pool_alloc st (fmt_table_bytes specs)
           | None -> assert false)
         (edit_stmts ss)

(* GET LIST (varying);) — single varying data item, default stream,
   no ON opts, no edit. Shapes beyond this raise [TBD] at lowering
   [X201/X202]. *)
let match_get_list_var (s : Ast.stmt) =
  match s.Ast.st with
  (* [E2E-7A slice 4] GET LIST accepts ANY number of simple name items
     [R904 pins the multi-item lowering order].  Every other item shape
     (subscripted, expression, EDIT/STRING form, file options, stream) still
     falls through to the [TBD] refusal at the call site. *)
  | Ast.Sget { stream = None; on_opts = []; kind = Ast.List_; items } ->
      let rec names acc = function
        | [] -> if acc = [] then None else Some (List.rev acc)
        | Ast.Pi_data { Ast.e = Ast.Eident n; _ } :: tl -> names (n :: acc) tl
        | _ -> None
      in
      names [] items
  | _ -> None

(* pool demand: RECURSIVE over container bodies (G114: puts live inside
   IF arms; a flat scan under-counts the pool and shifts DATA) *)
(* [E2E-7A slice 1] a DECIMAL comparison literal takes a pool cell sized
   by the OTHER (decimal) operand's precision -- DR pushes `0` as
   MVI A,09 against a dec(9,2) variable [R507/R607] and as A=0B against
   LOAN1's dec(11,2) P (6-byte cell at S(001E)).  prescan_stmt did not
   visit conditions at all, so without this the pool is under-sized and
   every variable address after it is short by the missing cell. *)
let rec prescan_cond (cx : pdec_ctx) (c : Ast.expr) =
  let unwrap x = match x.Ast.e with Ast.Econd y -> y | _ -> x in
  let prec_of e =
    match (unwrap e).Ast.e with
    | Ast.Eident n ->
        (match List.assoc_opt (String.lowercase_ascii n.Ast.orig) cx.pd_vars
         with Some (Vdec (p, sc)) -> Some (p, sc) | _ -> None)
    | Ast.Esuffix (b, _) ->
        (match b.Ast.e with
         | Ast.Eident n ->
             (match List.assoc_opt (String.lowercase_ascii n.Ast.orig)
                      cx.pd_procs with
              | Some (Some (p, sc)) -> Some (p, sc)
              | _ -> None)
         | _ -> None)
    | _ -> None
  in
  let litof e = match (unwrap e).Ast.e with Ast.Enumber k -> Some k | _ -> None in
  (* a FLOAT operand of a comparison: a float variable (or float formal) or a
     call that returns float.  Used to route a literal partner to the FLOAT
     pool cell instead of a DEC cell [R3076 `a = 0`, R3077 `a > 2.5`]. *)
  let is_fl e =
    match (unwrap e).Ast.e with
    | Ast.Eident n ->
        (match List.assoc_opt (String.lowercase_ascii n.Ast.orig) cx.pd_vars
         with Some Vflt -> true | _ -> false)
    | Ast.Esuffix (b, _) ->
        (match b.Ast.e with
         | Ast.Eident n ->
             List.mem (String.lowercase_ascii n.Ast.orig) cx.pd_fl_procs
         | _ -> false)
    | _ -> false
  in
  match (unwrap c).Ast.e with
  | Ast.Ebinary (Ast.EqR _, a, b) when is_fl a || is_fl b ->
      (* [E2E-10 step 3] the comparison literal becomes a 4-byte float cell, so
         the pool must be sized for it NOW: the condition is lowered before the
         first later variable store, and an unsized cell made the literal and a
         variable share address 0, shifting every subsequent data address. *)
      (match litof a with Some k -> pdec_fl_cell cx k | None -> 0)
      + (match litof b with Some k -> pdec_fl_cell cx k | None -> 0)
  | Ast.Ebinary (Ast.EqR _, a, b) ->
      let one side other =
        match litof side, prec_of other with
        | Some k, Some (p, sc) -> pdec_dec_cell cx p sc k
        | _ -> 0
      in
      one a b + one b a
  | Ast.Ebinary (_, l, r) -> prescan_cond cx l + prescan_cond cx r
  | Ast.Eprefix (_, x) -> prescan_cond cx x
  | _ -> 0

let rec prescan_stmt (cx : pdec_ctx) (s : Ast.stmt) =
  match s.Ast.st with
  | Ast.Sassign { lhs; rhs } ->
      (* [E2E-6] a DEC store of a bare literal allocates one TARGET-
         precision cell; a DEC arithmetic expression allocates one cell
         per literal at the literal's own digit count [R501/R505/R511] *)
      let dec_store_bytes =
        match lhs.Ast.e with
        | Ast.Eident n ->
            (match List.assoc_opt (String.lowercase_ascii n.Ast.orig)
                     cx.pd_vars with
             | Some (Vdec (p, sc)) ->
                 let rhs = pdec_unwrap rhs in
                 (match rhs.Ast.e with
                  | Ast.Enumber t -> pdec_dec_cell cx p sc t
                  | _ -> if pdec_is_dec cx rhs
                         then pdec_operand_bytes cx rhs else 0)
             | _ -> 0)
        | _ -> 0
      in
      (* [E2E-10] a FLOAT target store takes FLOAT cells for its literals
         (R3036 `d7 = a * 2` makes `2` a 4-byte float cell, not a DEC one),
         so the DEC demand path must be skipped entirely for that statement *)
      let fl_target =
        match lhs.Ast.e with
        | Ast.Eident n ->
            (match List.assoc_opt (String.lowercase_ascii n.Ast.orig)
                     cx.pd_vars with
             | Some Vflt -> true
             | _ -> false)
        | _ -> false
      in
      (* [E2E-18/C162] a BIN target with a DEC-TYPED rhs is the mixed case DR
         lowers through the DEC route (DLDOP...QDI15) -- CB9 `b = d + 2'.  The
         DEC demand above is keyed on the TARGET's type, so it returned 0 here
         and prescan_expr, which has no Enumber arm, never sized the operand's
         cell: prescan demanded 2 bytes, lowering allocated 4, putting `b' on
         top of the decimal cell.  Mirroring the Vdec branch's own condition
         (complex DEC-typed expression -> pdec_operand_bytes) is the consistent
         rule; a bare literal or identifier under this target type allocates
         nothing at lowering (LXI H,immediate / direct LHLD), so it is excluded
         to avoid double-counting with prescan_expr's Exp/Sub literal arms. *)
      let dec_rhs_in_int_target =
        match lhs.Ast.e with
        | Ast.Eident n ->
            (match List.assoc_opt (String.lowercase_ascii n.Ast.orig)
                     cx.pd_vars with
             | Some (Vdec _) | Some Vflt -> 0
             | _ ->
                 let r = pdec_unwrap rhs in
                 match r.Ast.e with
                 | Ast.Enumber _ | Ast.Eident _ -> 0
                 | _ -> if pdec_is_dec cx r then pdec_operand_bytes cx r else 0)
        | _ -> 0
      in
      if fl_target then pdec_fl_expr cx rhs
      else
      dec_store_bytes
      + dec_rhs_in_int_target
      + (match rhs.Ast.e with
         | Ast.Estring v -> pdec_str_cell cx v
             (* char-store pool demand [V101-V103/V105]; '' reserves 0
                [V104]; type-mismatched uses RAISE at lowering.  [E2E-16/C152] dedup'd by
                CONTENT, which PL11 (`c = 'W' twice -> one cell) and PL10 (char store and PUT
                sharing one cell) both measure; '' still registers a block at lowering. *)
         | _ -> prescan_expr cx rhs)
  | Ast.Sreturn (Some e0) ->
      (* [E2E-10] a FLOAT function's literal becomes a float cell: FFACT's
         `return (1)` is the 4-byte cell at *S(000C), which sits AFTER the
         main block's two character cells, matching first-use order *)
      if cx.pd_fl_ret then pdec_fl_expr cx e0 else
      (* [E2E-6] a bare literal RETURNed from a DEC function takes a
         TARGET-precision pool cell [DFACT return(1) = 8 bytes at
         S(000C)]; DEC arithmetic literals take their own digit cells *)
      (match cx.pd_ret with
       | Some (p, sc) ->
           let e = pdec_unwrap e0 in
           (match e.Ast.e with
            | Ast.Enumber t -> pdec_dec_cell cx p sc t
            | _ -> if pdec_is_dec cx e then pdec_operand_bytes cx e else 0)
       | None -> 0)
  | Ast.Sput _ ->
      (* [E2E-8] a PUT EDIT statement consumes pool space for the compiled
         FORMAT TABLE plus its item literals, and the table is allocated
         BEFORE the literals [*S(0000) in all 11 samples].  Missing it would
         shift every later data address silently -- the exact failure mode of
         the slice-3 ROUND prescan bug. *)
      (match match_put_edit s with
       | Some (its, specs) ->
           Array.length (fmt_table_bytes specs)
           + List.fold_left
               (fun a it -> match it with
                | PIlit v -> a + pdec_str_cell cx v
                | PInum x -> a + prescan_expr cx x
                | PIvar _ -> a) 0 its
       | None ->
      (match match_put_list_lit s with
       | Plit (_, v) -> pdec_str_cell cx v
       | Pcat (_, C2 (l, _, _)) -> String.length l
       | Pcat (_, C3 (l, _, r)) -> String.length l + String.length r
       | Pitems (_, its) ->
           List.fold_left
             (fun a it -> match it with
              | PIlit v -> a + pdec_str_cell cx v
              | PInum x -> a + prescan_expr cx x
              | PIvar _ -> a) 0 its
       | _ -> 0)             (* var-puts consume no pool [V101] *))
  | Ast.Sif { cond; then_; els; _ } ->
      prescan_cond cx cond
        + prescan_stmt cx then_
        + (match els with Some e -> prescan_stmt cx e | None -> 0)
  | Ast.Sdobegin ss -> List.fold_left (fun a x -> a + prescan_stmt cx x) 0 ss
  | Ast.Sdowhile { cond; body; _ } ->
      prescan_cond cx cond + prescan_stmt cx body
  | Ast.Sdoto { while_; body; _ } ->
      (* the DO ... WHILE guard can hold a DEC comparison literal; sizing
         it here keeps the pool aligned instead of shifting every later
         data address silently (a compare DR's lowering refuses anyway is
         still a refusal, never a short pool) *)
      (match while_ with Some e -> prescan_cond cx e | None -> 0)
        + prescan_stmt cx body
  | Ast.Sdoforever body -> prescan_stmt cx body
  | Ast.Sproc b ->
      (* descending into a procedure: RETURN literals take THAT
         procedure's decimal return precision [DFACT] *)
      let pn =
        match b.Ast.blk.Ast.bname with
        | Some n -> String.lowercase_ascii n.Ast.orig
        | None -> ""
      in
      let ret =
        match List.assoc_opt pn cx.pd_procs with Some r -> r | None -> None
      in
      List.fold_left
        (* pd_procs carries DEC return types only, so floatness comes from
           the kind map (a float-returning procedure appears there as Vflt) *)
        (fun a x ->
          a + prescan_stmt { cx with pd_ret = ret
                                   ; pd_fl_ret =
                                       (List.mem pn cx.pd_fl_procs) } x) 0
        b.Ast.blk.Ast.bstmts
  (* [E2E-11 step 2] an ON handler is inline CODE, so any literal it uses takes a
     pool cell in DR's allocation order.  Missing this made E11A's prescan count
     only 'HANDLED' (7 bytes) and set the pool base there instead of 14, so the
     two relocations of variable `a' (DR: A(000E)) came out as data 0x7 -- right
     code shape, wrong addresses, and byte-identical DATA bytes that hid it. *)
  | Ast.Son { handler; _ } -> prescan_stmt cx handler
  | _ -> 0

let prescan_pool (cx : pdec_ctx) (stmts : Ast.stmt list) =
  List.fold_left (fun acc s -> acc + prescan_stmt cx s) 0 stmts

(* ---- E2E-3a: PUT LIST '<char literal>' [G107/G108 $C-verified] ------
   Supported shape ONLY (match_put_list_lit); anything else fails loud.
   DR sequence (e2eput2 goldens, reldump + $C):
     LXI D,0252 ; LXI B,0000 ; CALL ?SYSPR
     [skip: MVI A,n ; CALL ?SKPOP]        (G108; SKPOP BEFORE data emit)
     LXI H,*S(pool) ; MVI A,len ; CALL ?SLCTS ; CALL ?PNCOP ; CALL ?QIOOP
   then a deferred backpatch triple per statement —
     SET-LC(code,bslot) ; RELOC(code,epi_addr) ; SET-LC(code,epi_addr) —
   emitted after the LAST statement, before the ?STOPX epilogue CALL:
   the LXI B operand receives the epilogue (continuation) address. *)
let lower_put_lit st (skipn : put_skip) (v : string) =
  d st op_lxi_d; d st 0x52; d st 0x02;
  d st op_lxi_b;
  let bslot = st.lc in
  d st 0; d st 0;
  call_ext st "?SYSPR";
  (match skipn with
   | Sk_lit c ->
       let n = parse_int_const c in
       if n <= 0 || n > 255 then
         failwith "codegen: skip count out of MVI range [TBD]";
       d st op_mvi_a; d st n; call_ext st "?SKPOP"
   | Sk_expr e -> emit_skip_count st e   (* [SK3 SK4] LHLD / MOV A,L / CALL ?SKPOP *)
   | Sk_none -> ());
  let bytes =
    Array.init (String.length v) (fun i -> Char.code (String.get v i))
  in
  let addr = pool_str st bytes in
  d st op_lxi_h; reloc st Data addr;
  d st op_mvi_a; d st (String.length v land 0xff);
  call_ext st "?SLCTS"; call_ext st "?PNCOP"; call_ext st "?QIOOP";
  (* G113: the backpatch triple is emitted INLINE after each put; the
     LXI B operand receives the CONTINUATION address (LC right after
     this statement), not an epilogue. [G107/G108: continuation == the
     ?STOPX call, so both models coincided.] *)
  emit_triple st bslot st.lc

(* count statements that MUST be accounted for by lowering (everything
   except declarations and empty statements). The counter + per-stmt
   `lowered` increments make silent discarding — including from future
   container statements — a hard failure. *)
let rec count_required (s : Ast.stmt) =
  match s.Ast.st with
  | Ast.Sdcl _ | Ast.Snull _ -> 0
  | Ast.Sdobegin ss ->
      1 + List.fold_left (fun a x -> a + count_required x) 0 ss
  | Ast.Sif { then_; els; _ } ->
      1 + count_required then_
        + (match els with Some e -> count_required e | None -> 0)
  | Ast.Sdowhile { body; _ } -> 1 + count_required body
  | Ast.Sdoto { body; _ } -> 1 + count_required body
  | Ast.Sdoforever body -> 1 + count_required body
  | Ast.Sproc b ->
      1 + List.fold_left (fun a x -> a + count_required x) 0
          b.Ast.blk.Ast.bstmts
  (* [E2E-11 step 2] the ON registration is an emitted sequence and the handler
     is inline code that lowers too, so both count.  Without this case the
     default gave 1 for the ON and 0 for the handler, which FLTPOLY2 happened to
     satisfy only because its handler is a single statement -- the numbers agreed
     for the wrong reason.  Made explicit so a two-statement handler is correct
     rather than an invariant failure. *)
  | Ast.Son { handler; _ } -> 1 + count_required handler
  | _ -> 1


(* assemble: header ; [SET-LC data + pool bytes] ; DEF-DATA-SIZE ;
   SET-LC code ; prologue ; body ; epilogue ; tail.  Body is lowered
   into a scratch state (collecting code items + pool bytes), then
   re-emitted in segment order. *)

(* is this name an AUTOMATIC-or-formal FIXED DECIMAL variable?  Defined up
   here (not via vk_dec_opt, which lives in the DEC block below) so the CALL
   lowering can mode-check decimal arguments. *)
(* moved above the call lowering: a FLOAT call argument passes the address
   of its pool cell [R3062], so the descriptor path needs fl_pool too *)
(* float literal cells live in the SHARED pool (byte-packed, first-use
   order, deduplicated by identical bytes [C101]) but are tracked apart from
   DEC and character cells, so a coincidental byte match can never alias a
   string literal onto a float operand or the other way round. *)
(* [E2E-11 step 4] the callee's formal type at a position, uniform over internal
   procedures and EXTERNAL ENTRIES, and available to BOTH the prescan and the
   lowering.  It used to be a closure inside the CALL lowering, which is why the
   prescan could not answer "is argument i a float?" -- and not answering it is
   what let a float literal argument cell be allocated after the pool base was
   fixed, putting it on top of the automatic variables (see
   prealloc_call_arg_cells). *)
(* the two inputs are the lists bind produced, so this is usable BEFORE the
   codegen state exists (pool sizing) and after (lowering) -- that is the whole
   reason it is a separate function rather than a closure inside lower_hl. *)
let callee_formal_rt_l (layout : Bind.prog_layout) (nm : string)
    (i : int) : Bind.rt option =
  let li = String.lowercase_ascii nm in
  match List.assoc_opt li layout.Bind.pl_exts with
  | Some (_p, _e, _ret, pt) -> List.nth_opt pt i
  | None ->
      (match
         List.find_opt
           (fun (p : Bind.proc_layout) -> p.Bind.pl_name = li)
           layout.Bind.pl_procs
       with
       | Some pl ->
           (match List.nth_opt pl.Bind.pl_ptrs i with
            | Some (fn, _) ->
                List.find_map
                  (fun (k, rt, _o) -> if k = fn then Some rt else None)
                  pl.Bind.pl_rows
            | None -> None)
       | None -> None)

let callee_formal_rt st (nm : string) (i : int) : Bind.rt option =
  let li = String.lowercase_ascii nm in
  match List.assoc_opt li st.exts with
  | Some (_p, _e, _ret, pt) -> List.nth_opt pt i
  | None ->
      (match List.assoc_opt li st.procs with
       | Some pl ->
           (match List.nth_opt pl.Bind.pl_ptrs i with
            | Some (fn, _) ->
                List.find_map
                  (fun (k, rt, _o) -> if k = fn then Some rt else None)
                  pl.Bind.pl_rows
            | None -> None)
       | None -> None)

let fl_pool st (b : bytes) =
  let l = List.init (Bytes.length b) (fun i -> Char.code (Bytes.get b i)) in
  match List.find_opt (fun (_addr, bs) -> bs = l) st.fl_cells with
  | Some (addr, _) -> addr
  | None ->
      let addr = pool_alloc st (Array.of_list l) in
      st.fl_cells <- st.fl_cells @ [ (addr, l) ];
      addr

let vk_is_dec st (n : Ast.name) =
  match List.assoc_opt (String.lowercase_ascii n.Ast.orig) st.vars with
  | Some vi -> (match vi.vk with Vdec _ -> true | _ -> false)
  | None -> false

(* strip a parenthesised-condition wrapper: DR lowers (c) exactly like c
   [P401 dbl body: (i+i)], and Econd also wraps while-conditions.  Moved up
   from the DEC model block so the CALL lowering can mode-check arguments. *)
let unwrap_e (e : Ast.expr) =
  match e.Ast.e with Ast.Econd x -> x | _ -> e

let is_ident (e : Ast.expr) =
  match e.Ast.e with Ast.Eident _ -> true | _ -> false



(* evaluate an integer expression, leaving the 16-bit value in HL *)
(* does evaluating e touch a pointer formal (deref ladder)? *)
let rec hl_operand_deref st (e : Ast.expr) =
  match e.Ast.e with
  | Ast.Eident n -> List.mem (String.lowercase_ascii n.Ast.orig) st.deref
  | Ast.Ebinary (_, a, b) -> hl_operand_deref st a || hl_operand_deref st b
  | Ast.Econd a | Ast.Eprefix (_, a) -> hl_operand_deref st a
  | _ -> false

(* [E2E-5c slice 2] tail = the continuation address that follows the
   MAIN block (tail_addr in emit_program). DR routes an ADD through
   PUSH H/POP D when the instruction at the evaluation position IS
   the tail position itself (RFACT's main increment at 0x4C:
   LHLD;INX H;SHLD) and uses the plain XCHG form elsewhere (dbl body
   at 0x30: MOV A,M / ORA M) [P401/P402/RFACT byte differentials]. *)
(* [E2E-9 slice 6] DR's FIXED BINARY peephole set, newly sampled by R2045,
   R2046 and P044.  All four shapes below are ones MY lowering gets WRONG --
   it emits a plausible instruction sequence instead of DR's -- so they fail
   loud here until the peepholes are implemented.  Every message carries the
   DR evidence that proves the divergence. *)
let lit_int (e : Ast.expr) =
  match e.Ast.e with
  | Ast.Enumber t -> (try Some (parse_int_const t) with _ -> None)
  | _ -> None

(* [E2E-11 step 1a, T5-T13] DR ELIDES an added/subtracted literal ZERO whenever
   the other side is variable-bearing: `b = a + 0', `b = 0 + a' and `b = a - 0'
   all lower to `LHLD A / SHLD B', and `a = a + 0 + 0' / `b = a + 0 + 0' to the
   same single copy [golden/e2e11v/T5-T7, e2e11w/T8, e2e11x/T9-T11, e2e11y/T12-13].
   It does NOT elide when BOTH sides are literals -- `b = 5 + 0' takes the
   decimal pool path (?DLDOP / ?DADOP / ?QDI15) [T11], the same no-constant-folding
   rule already recorded for `3 + 2' [R2045, P044 line 3].  A zero MINUEND is not
   droppable either (`0 - a' is a negation, not a copy).
   Gated on every variable in the kept expression being a plain 2-byte FIXED
   (Vint): DEC and FLOAT elision are unprobed, so those keep their existing path
   and whatever it refuses. *)
let rec elide_fixed_zero st (e : Ast.expr) =
  let is_zero_lit x =
    match x.Ast.e with
    | Ast.Enumber s -> (try parse_int_const s = 0 with _ -> false)
    | _ -> false
  in
  let rec only_literals x =   (* recursive: must be let rec, or the reference
                                inside its own body is unbound and the build
                                fails -- which it did silently while I read
                                warnings-only output as success *)
    match x.Ast.e with
    | Ast.Enumber _ -> true
    | Ast.Ebinary (_, a, b) -> only_literals a && only_literals b
    | _ -> false
  in
  match e.Ast.e with
  | Ast.Ebinary (op, l, r) ->
      (* [E2E-15/C151] the rewrite `x op 0 -> x' is valid ONLY for + and -.  This
         predicate used to test the zero literal without testing the operator, so
         `m = n * 0' silently became a copy of n (measured: MB7 emitted `LHLD n /
         SHLD m', 81 code bytes, and printed 7 for n=7 -- while DR emits `MOV L,H /
         SHLD m' [golden/e2e186/MB7]).  `m = n / 0' was worse still: it never reached
         the division-by-zero refusal below, it became a copy of n.  Both now fall
         through to the arm that handles (or loudly refuses) the real operator. *)
      if is_zero_lit r && (op = Ast.Add || op = Ast.Sub)
         && not (only_literals l) && elide_ok st l then
        elide_fixed_zero st l
      else if op = Ast.Add && is_zero_lit l && not (only_literals r)
              && elide_ok st r then
        elide_fixed_zero st r
      else
        { e with
          Ast.e = Ast.Ebinary (op, elide_fixed_zero st l, elide_fixed_zero st r) }
  | _ -> e

and elide_ok st (e : Ast.expr) =
  (* every identifier reachable from e must be a plain FIXED BINARY cell *)
  let ok = ref true in
  let rec walk (y : Ast.expr) =
    match y.Ast.e with
    | Ast.Eident n -> if vk_of st n.Ast.orig <> Vint then ok := false
    | Ast.Ebinary (_, a, b) -> walk a; walk b
    | Ast.Eprefix (_, a) -> walk a
    | _ -> ()
  in
  walk e; !ok

let fp_add_guard (l : Ast.expr) (r : Ast.expr) =
  (* [E2E-11 step 1a] a literal-0 operand reaching here means elide_fixed_zero
     declined it -- a non-Vint operand somewhere in the expression, or both
     sides literal.  The two-literal case below still refuses, which is right:
     `b = 5 + 0' takes DR's DECIMAL pool path (?DLDOP / ?DADOP / ?QDI15) [T11],
     it is NOT elided.  The old refusal here fired on `x = x + 0', which DR
     lowers as a 6-byte self-copy [T5, byte-identical to `x = x' [T6]]; that
     gap is closed by elide_fixed_zero + the k = 0 rung of the bias ladder, so
     N56_ADD_ZERO_LIT is retired (a negative whose subject DR compiles documents
     MY gap, not a language rule). *)
  match lit_int r with
  | _ ->
      (match lit_int l, lit_int r with
       | Some _, Some _ ->
           failwith
             ("codegen: fixed-bin ADD between TWO INTEGER LITERALS is not "
              ^ "constant-folded by DR: it emits the DECIMAL pool path "
              ^ "`LXI H,*S / MVI A,01 / CALL ?DLDOP / LXI H,*S / MVI A,01 / "
              ^ "CALL ?DLDOP / CALL ?DADOP / CALL ?QDI15` with one-byte "
              ^ "1-digit cells [R2045 `r = 3 + 2`, P044 line 3 `x = 2 + 4`]; "
              ^ "my immediate folding is not byte-equal [TBD].  Note this is "
              ^ "ADD-specific: `j = 0 - 7` [N301] and `e = 0 - 2` [N306] DO "
              ^ "fold to an immediate in DR, both byte-exact here.")
       | _ -> false)

(* [E2E-15/C148] DR's FIXED-BINARY multiply by an integer CONSTANT.  Measured over 24
   probes (e18src/MB1-MB31, golden/e2e186-e2e189) and CONTEXT-FREE -- the identical form
   appears in an assignment [MB1], a self-update [MB9], a compound operand [MB10/MB26], a
   PUT-LIST item [MB12], an IF condition [MB13], a call argument [MB14], a chained multiply
   [MB17], a width-converting store [MB18] and a RETURN over a pointer-deref formal
   [MB16]:
       k = 1        -> nothing at all: the operand alone  (`x * 1` elides  [P044])
       k = 2^m,m>=1 -> m copies of `DAD H`   (2:[MB1] 4:[MB4] 8:[MB19] 16:[MB21])
       2 <= k <= 32767, not a power of two
                    -> `LXI D,k ; CALL ?IM22N`   (3:[MB3] 5:[MB5] 6:[MB20] 7:[MB22]
                                                  1000:[MB29] 32767:[MB30])
       k = 32768+   -> DECIMAL POOL path (`PUSH H / LXI H,*S / MVI A,p / ?DLDOP /
                       ?QDI15 / POP D / ?IM22N`) [MB31 k=32768, MB23 k=65535] -- refused
       k = 0        -> DR emits `MOV L,H` [MB7 `n * 0`, MB8 `0 * n`], which does NOT
                       produce zero (it copies H into L): REFUSED, see C148's note on
                       DR's own defect.  My build previously emitted ?IM22N by 0 here.
   The operand-to-register assignment is free because ?IM22N multiplies DE x HL, so the
   literal commutes to either side with byte-identical output [MB2 vs MB1, MB27 vs MB3,
   MB11 vs MB10].  This classifier is the SINGLE source of the rule; the emitter below and
   the refusal guard both consult it, so they cannot drift. *)
type mul_form =
  | Mul_elide of Ast.expr            (* emit only the other operand *)
  | Mul_dadh of Ast.expr * int       (* other operand, then m copies of DAD H *)
  | Mul_im22 of Ast.expr * int       (* other operand, then LXI D,k + ?IM22N *)

let mul_const_form arrays (l : Ast.expr) (r : Ast.expr) =
  let both_lit x y =
    match x.Ast.e, y.Ast.e with
    | Ast.Enumber _, Ast.Enumber _ -> true
    | _ -> false
  in
  let pick =
    match lit_int l with
    | Some k when not (both_lit l r) -> Some (k, r)
    | _ ->
        (match lit_int r with
         | Some k when not (both_lit l r) -> Some (k, l)
         | _ -> None)
  in
  (* A CALL anywhere in the other operand stays out of this route: DR's operand-preservation
     rules across a call are C141/C146 territory and are NOT measured for the constant forms,
     so `f(1) * 2' keeps the existing route/refusal rather than borrowing this evidence. *)
  match pick with
  | Some (k, other) when k >= 2 && not (expr_contains_call arrays other) ->
      if (k land (k - 1)) = 0 && k <= 32767 then
        let rec log2 x m = if x = 1 then m else log2 (x lsr 1) (m + 1) in
        Some (Mul_dadh (other, log2 k 0))
      else if k <= 32767 then Some (Mul_im22 (other, k))
      else None
  | Some (1, other) when not (both_lit l r)
        && not (expr_contains_call arrays other) ->
      Some (Mul_elide other)
  | _ -> None

let fp_mul_guard arrays (l : Ast.expr) (r : Ast.expr) =
  (* [E2E-15] mul_const_form is the single source for every CONSTANT-multiply shape DR has a
     measured route for, so the guard must not fire on those.  What is left refused here is
     exactly what the classifier declines: literal 0, literals >= 32768 (DR's decimal-pool
     path), two literals, and literal-left shapes whose other operand contains a call. *)
  if mul_const_form arrays l r <> None then false
  else match lit_int l, lit_int r with
  | (Some 0), _ | _, (Some 0) ->
      failwith
        ("codegen: [TBD] FIXED multiply by literal 0.  DR emits `MOV L,H' for BOTH `n * 0' "
         ^ "and `0 * n' [MB7, MB8, golden/e2e186] -- that instruction copies H into L and "
         ^ "does NOT produce zero, so DR's own lowering looks defective.  I reproduce neither "
         ^ "it (unverified) nor my old ?IM22N-by-0 path (not byte-equal) [C148].")
  | (Some k), _ | _, (Some k) when k > 32767 ->
      failwith
        ("codegen: [TBD] FIXED multiply by literal " ^ string_of_int k
         ^ " >= 32768: DR leaves the 16-bit register route and loads the literal through the "
         ^ "DECIMAL POOL (`PUSH H / LXI H,*S / MVI A,p / ?DLDOP / ?QDI15 / POP D / ?IM22N') "
         ^ "[MB31 k=32768, MB23 k=65535].  My LXI D form would truncate it [C148].")
  | _, (Some 1 | Some 2 as k) ->
      failwith
        ("codegen: fixed-bin MULTIPLY by literal "
         ^ string_of_int (match k with Some x -> x | None -> 0)
         ^ " is strength-reduced by DR, not sent to ?IM22N: `x * 1` ELIDES "
         ^ "to `LHLD X ; SHLD X` [P044 line 4] and `n * 2` becomes `LHLD n ; "
         ^ "DAD H ; SHLD n` [R2046 line 11]; my build emits the ?IM22N "
         ^ "rotation instead [TBD]")
  | Some _, Some _ ->
      failwith
        ("codegen: fixed-bin MULTIPLY between two integer literals is "
         ^ "unsampled -- no accepted DR object contains one [TBD]")
  | _ ->
      (match lit_int l, r.Ast.e with
       | Some _, (Ast.Eident _ | Ast.Ebinary (_, _, _) | Ast.Esuffix _) ->
           failwith
             ("codegen: fixed-bin multiply with the LITERAL on the LEFT is commuted "
         ^ "by DR into `LHLD <right> ; LXI D,<left> ; CALL ?IM22N` with no "
           ^ "stack rotation [P044 line 6 `x = 3 * x`]; my PUSH H / LXI H / "
           ^ "POP D ladder is not byte-equal [TBD]")
       | _ -> false)

let rec lower_hl st (e : Ast.expr) =
  match e.Ast.e with
  | Ast.Enumber s ->
      let v = parse_int_const s in
      d st op_lxi_h; d st (v land 0xff); d st ((v lsr 8) land 0xff)
  | Ast.Esuffix (hd, args) ->
      (* [E2E-5c P401] single-argument internal procedure call.
         Deferred pointer pair + LXI H,*A(cell) + CALL; forward entry
         via CHAIN-ADDR resolved at the procedure's first byte, known
         entry via inline RELOC(code,entry) [P402 backward pattern] *)
      begin match hd.Ast.e, args with
      | Ast.Eident h, args
        when List.exists
               (fun (n, _lb, _ub, _ez) ->
                 String.equal n (String.lowercase_ascii h.Ast.orig))
               st.arrays ->
          (* [E2E-20/Priority 3] ARRAY ELEMENT READ.  This is a GUARDED match case, not an
             `if' inside the existing arm: the arm's body continues unconditionally into the
             call-setup code, which is exactly how E2E-19's implementation emitted a correct
             LHLD and then crashed in `List.assoc nm st.procs' [C165 corrected].  A guarded
             case makes fall-through structurally impossible.
             DR's form is a direct relocated load with the offset folded into the operand:
             RD3 first element `LHLD A A(0000)', last element `LHLD A A(0000)+0008'; AB1
             `b = a(1)' is `LHLD A A(0000)'.  In .REL that is an ordinary 2-byte DATA reloc at
             (base + (sub-lb)*2), the SAME machinery a scalar reference uses -- no new record
             format.  STORES are deliberately not enabled here [C164/Priority 4]. *)
          (match resolve_suffix st hd args with
           | Suf_element addr ->
               d st op_lhld; reloc st Data addr; st.last_imm <- None
           | Suf_element_dyn r ->
               (* [E2E-22/P2] variable-index READ.  DR's tail is `MOV E,M / INX H / MOV D,M' --
                  the value arrives in DE, not HL (AB2 0025-0027, AB8 0039-003B, AB10
                  003D-003F).  What settles the register contract is the CONTINUATION, not the
                  tail: AB2's `b = a(i)' continues `XCHG / SHLD b' and AB8/AB10's PUT item
                  continues `XCHG / MVI A,09 / <numeric PUT tail>'.  DR normalizes to HL with
                  XCHG in every measured case, so the read keeps lower_hl's existing HL contract
                  and every consumer (scalar store, PUT item, arithmetic) works unchanged. *)
               dyn_addr st r;
               d st 0x5e; d st op_inx_h; d st 0x56; d st op_xchg;
               st.last_imm <- None
           | Suf_call _ -> assert false)
      | Ast.Eident h, args ->
          let nm = String.lowercase_ascii h.Ast.orig in
          if
            not (List.mem_assoc nm st.procs || List.mem_assoc nm st.exts)
          then
            failwith
              ("codegen: call to unknown " ^ nm
                 ^ " [TBD] (not a procedure in scope and not an ENTRY "
                 ^ "declaration; line "
                 ^ string_of_int h.Ast.pos.Source.line ^ ")");
          (* [E2E-11 step 4] the external-entry record, threaded through this
             whole arm: it drives the formal-TYPE lookups (there are no formal
             CELLS for an entry), the CALL operand shape (CHAIN-EXT), and the
             NOT PROC / TYPES NOT= checks via RETURNS. *)
          (* [E2E-20/Priority 6] an ARRAY ELEMENT passed as an actual is NOT a value read.
             C159/AB7 show DR puts the element's ADDRESS into the call descriptor
             (`LXI H,A+0006 / SHLD * / LXI H,* / CALL p'), which is a different lowering again
             and is deliberately not landed here.  Without this guard the existing argument
             path would silently lower the element as a VALUE -- right-ish semantics, wrong
             bytes, the exact C139/C150 class -- so it refuses loudly instead. *)
          (* [E2E-22/P3] an array element passed as an ACTUAL is not a value read: DR hands the
             callee the element's ADDRESS through the same call descriptor a pointer formal uses
             [C130], so NO separate array calling convention exists.  Measured forms:
               AB7  `call p(a(4))'  : LXI H,<a+6> ; SHLD <desc cell> ; LXI H,<desc> ; CALL p
               PASSARAY `call inner(argument(I))':
                                      <variable-index ladder> ; SHLD <desc cell> ; CALL inner
             i.e. constant index loads the (statically known) element address with LXI H, and a
             runtime index simply runs the ladder -- which already leaves the address in HL -- and
             stores it.  Both take the DYNAMIC descriptor route (runtime SHLD, bare RELOC records,
             no SET-LC wrapping), which is the route E27B established for a forwarded pointer
             formal: even though an element address IS statically known, DR writes it at runtime,
             so the descriptor word is code, not a static reloc.  Shapes that do not resolve to a
             single element (multi-dimensional, whole-array, unbound name) refuse below through
             resolve_suffix, which is the same single authority used everywhere else [C169]. *)
          let elemrefs =
            List.map
              (fun a ->
                let a = match a.Ast.e with Ast.Econd x -> x | _ -> a in
                match a.Ast.e with
                | Ast.Esuffix (hd2, args2) ->
                    (match
                       (try Some (resolve_suffix st hd2 args2) with _ -> None)
                     with
                     | Some (Suf_element _) | Some (Suf_element_dyn _) as r -> r
                     | _ -> None)
                | _ -> None)
              args
          in
          let ext = List.assoc_opt nm st.exts in
          (* [E2E-11/CALL, C122] the two disjoint procedure kinds, both from DR
             pass 2 with NO .REL emitted: see st.call_stmt's comment.  An
             EXTERNAL ENTRY participates in the same rule: `declare ex
             entry(fixed) external;' has no RETURNS, so `call ex(a);' is legal
             (E24G) and `n = ex(a);' would be DR's TYPES NOT= [C122]. *)
          let returns_some =
            match List.assoc_opt nm st.exts with
            | Some (_p, _e, ret, _pt) -> ret <> None
            | None ->
                (match List.assoc nm st.procs with
                 pl -> pl.Bind.pl_ret <> None)
          in
          let is_stmt = st.call_stmt = Some nm in
          if is_stmt then st.call_stmt <- None;
          if is_stmt && returns_some then
            failwith
              ("codegen: [TBD] CALL of " ^ nm
                 ^ ": DR rejects this -- NOT PROC (a value-returning procedure has "
                 ^ "no subroutine form; use it in an expression instead "
                 ^ "[E24D, E24H]. Line "
                 ^ string_of_int hd.Ast.epos.Source.line ^ ")")
          else if (not is_stmt) && not returns_some then
            failwith
              ("codegen: [TBD] " ^ nm
                 ^ "() in an expression: DR rejects this -- TYPES NOT= (a procedure "
                 ^ "with no RETURNS has no value to yield; invoke it with a CALL "
                 ^ "statement [E24I]. Line "
                 ^ string_of_int hd.Ast.epos.Source.line ^ ")");
          (match st.calls with
           | (cs :: rest) when cs.Bind.cs_proc = nm ->
               st.calls <- rest;
               if List.length cs.Bind.cs_args <> List.length args then
                 failwith "codegen: call-site arity mismatch [TBD]";
               (* [E2E-9] multi-argument internal call.  PER ARGUMENT, in
                  source order, DR does: (1) if the argument is an
                  EXPRESSION, evaluate it and SHLD the value into that
                  argument's value cell; (2) emit the descriptor address
                  constant for that argument's cell.  The two steps are
                  INTERLEAVED, not batched [R2032: RELOC(&i) lands BEFORE
                  the `j + 1` temp store, RELOC(&temp) AFTER it].  Then ONE
                  `LXI H,*A(slot)` + CALL for the whole block -- DR does NOT
                  emit one push per argument [R2001 two, R2034 three, R2035
                  four, DECPOLY three decimals]. *)
               let slot = cs.Bind.cs_slot + st.base in
               let pairs =
                 List.combine cs.Bind.cs_args cs.Bind.cs_temps
               in
               (* set per argument when the actual is a pointer formal of the
                  CALLING scope, i.e. the descriptor word needs DR's dynamic
                  forwarding store [E27B] instead of a static address operand *)
               let fwd = ref (None : string option) in
               (* the callee's formal type at each position, so an argument
                  can be MODE-CHECKED [E2E-9]: DR's only pinned decimal
                  argument route is by-reference from an AUTOMATIC decimal
                  variable [DECPOLY, R2037/R2038, R725]. *)
               (* [E2E-11 step 4] the callee's formal TYPE at a position,
                  uniform over internal procedures and EXTERNAL ENTRIES.
                  For an internal procedure this is the existing lookup: only
                  POINTER formals have a row, and a formal that is not a
                  pointer formal yields None (the value-formal route).  For an
                  external entry there are no formal cells at all -- DR passes
                  every argument BY DESCRIPTOR, which DIV2.ASM demonstrates
                  directly (`div2: ;HL = .low(.p1)` then it loads .p1 out of the
                  descriptor), so bind's recorded ptypes are the whole story.
                  Keeping ONE accessor is deliberate: two parallel code paths
                  here is how a mode rule would drift between internal and
                  external calls without either failing. *)
               let pl_opt =
                 match ext with
                 | Some _ -> None
                 | None -> Some (List.assoc nm st.procs)
               in
               let formal_rt_at i : Bind.rt option =
                 callee_formal_rt st nm i
               in
               (* the callee's formal row at a position, internal shape only *)
               let formal_rt i =
                 match ext with
                 | Some _ -> None
                 | None ->
                     let pl = Option.get pl_opt in
                     (match List.nth_opt pl.Bind.pl_ptrs i with
                      | Some (fn, _) ->
                          List.find_opt (fun (k, _rt, _o) -> k = fn)
                            pl.Bind.pl_rows
                      | None -> None)
               in
               let formal_is_float i =
                 match formal_rt_at i with
                 | Some (Bind.RTfloat 24) -> true
                 | Some (Bind.RTfloat p) ->
                     failwith
                       ("codegen: FLOAT BINARY(" ^ string_of_int p
                        ^ ") formal is unsupported [TBD] (only BINARY(24) is "
                        ^ "characterized; C100/C101)")
                 | _ -> false
               in
               let formal_is_dec i =
                 match formal_rt_at i with
                 | Some (Bind.RTdec _) -> true
                 | Some _ -> false
                 | None ->
                     (* an external entry with no ptype at i is a bind-side bug,
                        not an unsampled shape; an internal non-pointer formal
                        legitimately has no row [value-formal route] *)
                     (match ext with
                      | Some _ ->
                          failwith
                            ("codegen: call argument with no recorded formal type "
                             ^ "against an EXTERNAL ENTRY [TBD] (bind's RTentry "
                             ^ "carries ptypes; arity is checked separately)")
                      | None -> false)
               in
               List.iteri
                 (fun i (arg, tmp) ->
                   (* [E2E-11 step 4, E29C] width-mismatched argument: an actual
                      whose cell is NARROWER than the formal's declared FIXED type
                      cannot be passed by reference -- the callee would read past
                      it.  DR widens: E29C `ff(i, j)' with `dcl (i,j) fixed(7)'
                      against `entry(fixed(7),fixed)' emits
                          LDA J ; <sign-extend to HL> ; SHLD * A(0006)
                          LXI H,* A(0002) ; CALL FF
                      i.e. it copies j's value into an ANONYMOUS 2-byte cell and
                      hands out that cell's address (which is also why DR's data
                      area is 2 bytes bigger than mine was).  My pass-by-reference
                      route would silently let the callee read one byte of j plus
                      whatever follows, so it refuses until implemented. *)
                   let () =
                     (* [E2E-22/P3] an element actual's width is the ARRAY element width; a formal
                        wider or narrower than it is unmeasured (DR would widen through an
                        anonymous cell [E29C], which needs a temp cell -- and AB7/PASSARAY show NO
                        temp for an element), so it refuses rather than pass a short reference. *)
                     (match List.nth elemrefs i with
                      | Some (Suf_element _) | Some (Suf_element_dyn _) ->
                          (* element size comes from the array list -- the same authority
                             bind_arrays feeds to layout and to span [C167] *)
                          let aw =
                            match (unwrap_e arg).Ast.e with
                            | Ast.Esuffix (hd2, _) ->
                                (match
                                   List.find_opt
                                     (fun (n, _l, _u, _e) ->
                                       String.equal n
                                         (match hd2.Ast.e with
                                          | Ast.Eident h2 ->
                                              String.lowercase_ascii h2.Ast.orig
                                          | _ -> "?"))
                                     st.arrays
                                 with
                                 | Some (_n, _l, _u, e2) -> e2
                                 | None -> 2)
                            | _ -> 2
                          in
                          (match callee_formal_rt st nm i with
                           | Some (Bind.RTbin p) ->
                               let fw = Bind.bytes_of (Bind.RTbin p) in
                               if fw <> aw then
                                 failwith
                                   ("codegen: [TBD] fixed(" ^ string_of_int p
                                      ^ ") formal against an array element of "
                                      ^ string_of_int aw
                                      ^ " bytes [E2E-22/P3]: DR's widening route for a narrow "
                                      ^ "actual copies through an anonymous cell [E29C], which is "
                                      ^ "unmeasured for elements; refused (line "
                                      ^ string_of_int arg.Ast.epos.Source.line ^ ")")
                           | _ -> ())
                      | _ -> ())
                   in
                   let () =
                     match (unwrap_e arg).Ast.e with
                     | Ast.Eident v ->
                         let aw =
                           match List.assoc_opt (String.lowercase_ascii v.Ast.orig) st.vars with
                           | Some vi -> vi.size
                           | None -> 2
                         in
                         (match callee_formal_rt st nm i with
                          | Some (Bind.RTbin p) ->
                              let fw = Bind.bytes_of (Bind.RTbin p) in
                              if fw <> aw then
                                failwith
                                  ("codegen: [TBD] fixed(" ^ string_of_int p
                                     ^ ") formal against an actual with a "
                                     ^ string_of_int aw
                                     ^ "-byte cell is unimplemented (DR widens "
                                     ^ "through an anonymous cell [E29C]; line "
                                     ^ string_of_int arg.Ast.epos.Source.line ^ ")")
                          | _ -> ())
                     | _ -> ()
                   in
                   (* [E2E-9] mode check.  Bound as `let () = ... in` on
                      purpose: an `if` whose THEN branch is a MATCH swallows
                      every following expression into the match's last arm
                      (a real DECPOLY byte failure -- the descriptor
                      constants vanished), so the guard must be sealed. *)
                   let () =
                     if formal_is_float i then
                       begin match (unwrap_e arg).Ast.e with
                       | Ast.Eident v when vk_of st v.Ast.orig = Vflt -> ()
                       | Ast.Eident v when List.mem
                             (String.lowercase_ascii v.Ast.orig) st.deref -> ()
                       | Ast.Enumber _ -> ()
                       | _ ->
                         failwith
                           ("codegen: non-float-variable argument against a "
                            ^ "FLOAT formal is unsampled [TBD] (DR's pinned "
                            ^ "float argument routes are a plain float "
                            ^ "variable or a float literal, both passed by "
                            ^ "address through the descriptor [R3061, R3062]; "
                            ^ "a FIXED argument takes a convert-into-temp-cell "
                            ^ "route [R3064: ?QI15F then ?FX44S into an "
                            ^ "anonymous float cell] which is understood but "
                            ^ "not yet implemented, and a general expression "
                            ^ "has no sample at all. Line "
                            ^ string_of_int arg.Ast.epos.Source.line ^ ")")
                       end
                   in
                   let () =
                     if formal_is_dec i then
                       begin match (unwrap_e arg).Ast.e with
                       | Ast.Eident v when vk_is_dec st v -> ()
                       | _ ->
                         failwith
                           ("codegen: non-variable argument against a FIXED "
                            ^ "DECIMAL formal is unproven [TBD] (DR passes an "
                            ^ "automatic decimal BY REFERENCE -- the "
                            ^ "descriptor holds LXI H,*A(cell); a literal or "
                            ^ "expression decimal argument has no sample "
                            ^ "[DECPOLY, R2037/R2038/R725]. Line "
                            ^ string_of_int arg.Ast.epos.Source.line ^ ")")
                     end
                   in
                   (match tmp with
                    | Some t ->
                        lower_hl st arg;
                        d st op_shld; reloc st Data (t + st.base)
                    | None -> ());
                   fwd := None;
                   let target =
                     match tmp with
                     | Some t -> t + st.base
                     | None -> begin
                         match arg.Ast.e with
                         | Ast.Enumber k ->
                             if formal_is_float i then
                               (* a FLOAT literal argument is passed by address
                                  of its POOL cell [R3062: LXI H,*A(0010) with
                                  the descriptor pointing at the 4-byte cell],
                                  so the target is the float cell, not the
                                  2-byte integer cell the fixed route builds. *)
                               (match mbf_encode k with
                                | b -> fl_pool st b
                                | exception Fl_range msg ->
                                    failwith
                                      ("codegen: float literal argument "
                                       ^ k ^ " " ^ msg))
                             else begin
                               let kv = parse_int_const k in
                               pool_alloc st
                                 [| kv land 0xff; (kv lsr 8) land 0xff |]
                             end
                         | Ast.Esuffix _
                           when (match List.nth elemrefs i with
                                 | Some _ -> true
                                 | None -> false) ->
                             0 (* the address route below ignores target *)
                         | Ast.Eident v ->
                             let vn =
                               String.lowercase_ascii v.Ast.orig
                             in
                             if List.mem vn st.deref then begin
                               (* [E2E-11 step 3c, E27B] forwarding a pointer
                                  formal as an actual: DR writes the descriptor
                                  word at RUNTIME, because what the caller must
                                  hand over is the ADDRESS THE FORMAL ALREADY
                                  HOLDS (the original variable), which is not
                                  statically known.  E27B inside t(y):
                                      003A LHLD Y A(000A)   <- the value, not &y
                                      003D SHLD * A(000C)   <- into the desc cell
                                      0040 LXI H,* A(000C)
                                      0043 CALL S
                                  so the static 2-byte operand is REPLACED by
                                  those three code bytes.  Marked through the
                                  ref below; target is unused in that case. *)
                               fwd := Some vn;
                               0
                             end else addr_of st v.Ast.orig
                         | _ ->
                             failwith
                               ("codegen: expression call argument " ^
                                "deferred [TBD]")
                       end
                   in
                   match !fwd with
                   | Some fv ->
                       (* [E27B] and NO SET-LC records on either side: the .REL
                          shows a bare RELOC(DATA,000C) for the SHLD and another
                          for the following LXI H, where the static route wraps
                          its operand in SET-LC pairs.  Line 003D..0040 of
                          E27B.PRN / the record stream is the evidence. *)
                       d st op_lhld; reloc st Data (addr_of st fv);
                       (* `slot' is ALREADY an absolute DATA address here -- the
                          LXI H operand below relocates against it unshifted --
                          so adding st.base double-counted the pool base and my
                          stores wrote cells 4 bytes past the descriptor my own
                          LXI H pointed at.  E28A caught it only because the two
                          SHLD operands and the LXI H operand are three views of
                          one address: mine disagreed with themselves, which no
                          comparison against DR could ever have to forgive. *)
                       d st op_shld; reloc st Data (slot + 2 * i)
                   | None -> (
                     match List.nth elemrefs i with
                     | Some (Suf_element ea) ->
                         (* [AB7] LXI H,<a+off> ; SHLD <desc cell> *)
                         d st op_lxi_h; reloc st Data ea;
                         d st op_shld; reloc st Data (slot + 2 * i)
                     | Some (Suf_element_dyn r) ->
                         (* [PASSARAY] the ladder already leaves the element ADDRESS in HL *)
                         dyn_addr st r;
                         d st op_shld; reloc st Data (slot + 2 * i)
                     | _ ->
                       link st t_set_lc (Some (Data, slot + 2 * i)) None;
                       push st (Reloc (Data, target));
                       link st t_set_lc (Some (Code, st.lc)) None))
                 pairs;
               (* [E2E-11/CALL, E24A/E24J] a zero-argument call has NO
                  descriptor and no `LXI H` at all -- `call q;` and `n = f();`
                  are both a bare `CALL <q>` (three bytes), and the enclosing
                  block's auto area is untouched (main's a/b/c stay at 0/2/4
                  with three zero-arg sites between them).  bind already
                  allocates a 2*0-byte slot, so the queue stays aligned. *)
               if args <> [] then begin
                 d st op_lxi_h; reloc st Data slot;
               end;
               d st op_call;
               (match ext with
                | Some (_p, _e, _ret, _pt) ->
                    (* [E2E-11 step 4, E24G/DTEST] an EXTERNAL ENTRY's CALL operand
                       is a LINK-CHAIN-EXT naming the symbol -- exactly the shape the
                       RTL references use, and NOT a CHAIN-ADDR (the target lives in
                       another module) and NOT an inline RELOC (there is no address
                       in THIS program to point at).  DR emits it per call site
                       (E24G: CHAIN-EXT EX at code 0010; DTEST: CHAIN-EXT DIV2 at
                       code 0019) and does NOT EXTDEF the symbol: E24G's only EXTDEF
                       is the program name [C132].  The name is the declared spelling
                       uppercased, matching how DR names its own symbols. *)
                    let slotx = st.lc in
                    d st 0; d st 0;
                    link st t_chain_ext (Some (Code, slotx))
                      (Some (String.uppercase_ascii h.Ast.orig))
                | None ->
                   (match List.assoc_opt nm st.entries with
                    | Some a ->
                        (* known entry (backward/self): the CALL operand is
                           a single INLINE relocatable reference
                           [RFACT @8A cd+RELOC code 56; NFACT @99] *)
                        reloc st Code a
                    | None ->
                        (* forward: two placeholder DATA bytes; resolved by
                           CHAIN-ADDR at the callee's entry byte
                           [P401 @9-000B + chain @1285] *)
                        let oslot = st.lc in
                        (* [E2E-11/CALL, E25F, C123] the SECOND (and later) forward
                           call to the same not-yet-emitted procedure does NOT get
                           its own chain.  DR relocates its operand RELATIVE TO THE
                           FIRST CALL SITE'S OWN OPERAND WORD: E25F emits
                           `CALL 0000` at 0013 (operand stored at 0014, later
                           CHAIN-ADDR'd to the entry) and then, at the second site
                           0019, the record RELOC(CODE, 0014) -- which the listing
                           prints as `CALL S`.  At link time 001A receives the
                           contents of 0014, i.e. the callee's entry address, so the
                           indirection is semantically a copy of the first patch.
                           That is why one CHAIN-ADDR serves arbitrarily many sites,
                           and why emitting a second chain would be wrong: E25F has
                           exactly ONE chain record for two forward calls. *)
                        (* st.fcalls is PREPENDED, so the head is the most recently
                           emitted site for this procedure.  E27A (three forward
                           calls to one procedure) pins the chain: site 1's operand
                           at 0018 is two zero DATA bytes, site 2's operand at 001E
                           is RELOC(CODE, 0018), site 3's operand at 0024 is
                           RELOC(CODE, 001E) -- each later site is relocated against
                           the IMMEDIATELY PRECEDING site, not against the first.
                           E25F agrees (one later site against 0014).  Then ONE
                           LINK-CHAIN-ADDRESS record targets the LAST site's operand
                           (E27A: 0024; E25F: 001A), and the linker's chain walk
                           propagates the entry address back through the RELOC links:
                           verified by linking my own .REL and comparing the resolved
                           operands against DR's .COM. *)
                        (match List.filter (fun (k, _) -> k = nm) st.fcalls with
                         | (_, prev_slot) :: _ ->
                             reloc st Code prev_slot;
                             (* the site just emitted becomes the anchor for the next
                                one [E27A: 0018 <- 001E <- 0024].  Forgetting this is
                                what made site 3 chain against site 1 -- the .REL
                                differed in exactly one field and E25F (two sites)
                                still matched, so a two-site test cannot catch it. *)
                             st.fcalls <- (nm, oslot) :: st.fcalls
                         | [] ->
                             d st 0; d st 0;
                             st.fcalls <- (nm, oslot) :: st.fcalls)))
               ; st.last_imm <- None
           | _ -> failwith "codegen: call-site queue mismatch [TBD]")
      | _ -> failwith "codegen: non-identifier call target deferred [TBD]"
      end
  | Ast.Eident n ->
      (match vk_of st n.Ast.orig with
       | Vint -> ()
       | Vdec _ ->
           failwith
             "codegen: decimal operand inside an integer expression [TBD] \
              (mixed-mode routes are unpinned)"
       | Vflt ->
           failwith
             "codegen: FLOAT value used where a FIXED value is expected [TBD] (the float-to-fixed route ?FL40M/?QFI15 appears only inside FFACT's prologue, so no standalone conversion or mixed-mode arithmetic is sampled)"
      | _ -> failwith "codegen: arithmetic on char variable [TBD]");
      let vi = List.assoc (String.lowercase_ascii n.Ast.orig) st.vars in
      if vi.size = 1
         && List.mem (String.lowercase_ascii n.Ast.orig) st.deref then
        failwith "codegen: 1-byte pointer formal unproven [TBD]";
      if vi.size = 1 then begin
        (* [N306/N303] 1-byte FIXED BIN: LD A,dir (3A+RELOC) then
           sign-extend into HL: MOV L,A; ADD A; SBB A; MOV H,A *)
        st.last_imm <- None;
        d st 0x3a; reloc st Data (addr_of st n.Ast.orig);
        d st op_mov_l_a; d st op_add_a; d st op_sbb_a; d st op_mov_h_a
      end
      else begin
        d st op_lhld; reloc st Data (addr_of st n.Ast.orig);
        if List.mem (String.lowercase_ascii n.Ast.orig) st.deref then
          (* pointer formal: dereference the passed address [P401 dbl:
             LHLD i; MOV E,M; INX H; MOV D,M; XCHG -> HL = value] *)
          (d st 0x5e; d st 0x23; d st 0x56; d st 0xeb);
        st.last_imm <- None   (* runtime value; not a const *)
      end

  | Ast.Econd x ->
      (* parentheses around an arithmetic expression arrive Econd-wrapped
         (RETURN(expr), item positions). DR lowers them EXACTLY like the
         unwrapped expression [P401 dbl body: (i+i) -> standard Add
         ladder], so unwrap transparently. *)
      lower_hl st x
  | Ast.Ebinary (Ast.Add, l, r) when fp_add_guard l r ->
      failwith "codegen: internal: fp_add_guard raised no message"
  | Ast.Ebinary (Ast.Add, l, { Ast.e = Ast.Enumber "1"; _ }) ->
      (* [(a+1) N304] +1 lowers to INX H on the 2-byte path; other
         additions keep the general ladder *)
      lower_hl st l; d st op_inx_h; st.last_imm <- None
    | Ast.Ebinary (Ast.Add, { Ast.e = Ast.Enumber ks; _ }, r) ->
      (* [E2E-13/C141] LITERAL on the left of an ADD: DR commutes the operand and
         adds the constant to the value instead of loading an immediate and pairing
         it.  Two independent DR samples:
            P4  `return (1 + g(3))'  ->  LXI H,* ; CALL G ; INX H ; RET
            K9  `return (2 + n)'     ->  ... ; XCHG ; INX H ; INX H ; RET
         and K9 is BYTE-IDENTICAL to K5 (`return (n + 2)'), which proves the commute
         rather than merely suggesting it.  This replaces the general ladder, which
         loaded 1/2 into HL, XCHG'd it into DE and did DAD D -- right value, wrong
         bytes, and on the call-right shape it parked DE across the call (C139). *)
      let k = parse_int_const ks in
      lower_hl st r; hl_bias_free st k; st.last_imm <- None
    | Ast.Ebinary (Ast.Add, l, { Ast.e = Ast.Enumber ks; _ }) ->
      (* [E2E-13/C141] non-self constant add: strength-reduce the same way, on the
         left value.  k<=4 -> (INX H)*k, k>=5 -> LXI B,k ; DAD B  [R4,R5,R6,R8,R10,
         R12,T2,T4,T8].  Magnitude 1 lands in the arm above and gives the same byte. *)
      let k = parse_int_const ks in
      lower_hl st l; hl_bias_free st k; st.last_imm <- None
    | Ast.Ebinary (Ast.Add, l, r)
      when (match r.Ast.e with Ast.Esuffix _ -> true | _ -> false)
           && not (suf_is_element st r)
      ->
        (* [E2E-13/C141] THE C139 CORRECTION.  FIXED ADD with a procedure CALL on
           the right.  DR never parks a value in a register across a call: it either
           defers the load until after the call, or pushes onto the runtime stack.
           My old lowering did neither -- it loaded the left operand BEFORE the call
           and XCHG'd it into DE, which the nested activation's own prologue destroys
           (`LXI D,shadow' plus the MOV E,M/INX H/MOV D,M/XCHG copy ladder, visible at
           my code 013C-0150 in golden/e2e169ml/U1.COM).  Hence sum(100)=12488.

           Two DR shapes, from six listings (batch golden/e2e174, $L$C$D):

             left is a simple variable  [P1,P2,P3,P9,P10,P11]
                 <right: arg eval, LXI H,result, CALL> ; XCHG ; <load left> ; DAD D
                 e.g. P1  LXI H,* A(000F) / CALL S / XCHG / LHLD T A(000D) / DAD D
                 The left is re-read AFTER the call, which is sound because a
                 recursive activation's locals live in its own SVBLK shadow block and
                 ?RSBLK restores them -- not because anything is preserved.

             left is a compound expression  [P5 `t+u+g(3)', P12 `g(3)+g(4)']
                 <left> ; PUSH H ; <right> ; POP D ; DAD D
                 e.g. P5  LHLD T / XCHG / LHLD U / DAD D / PUSH H / LXI H,* / CALL G
                        / POP D / DAD D

           The literal-left case lives in the arm above [P4]; MUL and call-on-left
           keep their existing (byte-exact) routes untouched. *)
        (* [E2E-14/C145] the anonymous-cell NUMBERING is now two-phase (all descriptor
           slots, then all expression-argument value cells -- bind.ml), which makes a
           literal-actual nested chain byte-identical to DR: P9 `return (t + g(h(2)))',
           mine == DR byte-for-byte ✓.  Variable actuals in this arm are unmeasured and
           still refuse [C146].
           A nested chain with a COMPOUND actual still has an argument VALUE CELL whose
           number DR assigns inner-first, and that difference is not yet measured, so it
           refuses with the reason named [C142]. *)
        if call_operand_is_nested st.arrays r
         && not (call_chain_simple 1 r)
     then
          failwith
            ("codegen: [TBD] ADD whose call operand is a nested call with a COMPOUND "
             ^ "actual (e.g. `t + g(h(k(2)))', `t + g(2*h(3))'). Under the C145 two-phase "
             ^ "numbering, simple-actual chains are byte-identical to DR [P9, D7]; a "
             ^ "compound actual additionally needs an argument VALUE cell that DR numbers "
             ^ "inner-first (at the producing store) and I number per call site, so the "
             ^ "anonymous-cell records disagree [C142, unmeasured]");
        if add_left_needs_push l then
          failwith
            ("codegen: [TBD] ADD whose left operand must be parked across a call (a compound expression or a second call).  DR uses PUSH H / POP D and I now emit that sequence with code bytes IDENTICAL to DR's -- P5 `(t+u)+g(3)' and P12 `g(3)+g(4)' both run to DR's value (21, 21; golden/e2e180r) -- but DR writes the call's anonymous-cell allocation RECORDS (LINK-SET-LC data / RELOC) before the left operand's code records, while I write them at point of use, so the bit-packed streams differ.  The deferred single-variable case IS implemented and byte-exact [P1-P4, P7-P11]");
        lower_hl st r; d st op_xchg;
        lower_hl st l; d st op_dad_d;
        st.last_imm <- None
    | Ast.Ebinary (Ast.Add, l, r) ->
      (* DR: HL=left ; XCHG ; HL=right ; DAD D  (=> HL = right+left)
         [P071A]. WITH POINTER-DEREF OPERANDS the ladder is
         left ; PUSH H ; right ; POP D ; DAD D [P401 dbl (i+i):
         E5 @37, D1 @3F] — forced by mechanics: the deref ladder's own
         XCHG (EB) clobbers DE, so the XCHG form cannot preserve the
         left value across a second deref. *)
      (* [E2E-11 step 3b, E26H `x = x + p`] the PUSH route is forced only by a
         RIGHT operand that derefs.  When the LEFT is the pointer formal and the
         right is a plain cell, DR takes the ordinary XCHG route: the deref
         ladder leaves HL=value / DE=ptr+1, XCHG flips them so DE carries the
         value across `LHLD p` (the stale ptr+1 in HL is dead the moment the
         right operand loads), then DAD D adds.  Byte-for-byte:
             LHLD X ; MOV E,M ; INX H ; MOV D,M ; XCHG
             XCHG ; LHLD P ; DAD D
         My old test treated any deref on either side as PUSH, which added a
         spurious PUSH H/POP D pair here. *)
      if hl_operand_deref st r then begin
        lower_hl st l; d st 0xe5;                    (* PUSH H *)
        lower_hl st r; d st 0xd1; d st op_dad_d      (* POP D; DAD D *)
      end else begin
        (* [E2E-15/C150] DR's rule is SYNTACTIC, not register-analytic: whenever the RIGHT
           operand is compound (more than one instruction) the LEFT is parked on the runtime
           stack, and when it is simple XCHG is used -- MB34 `n + (n*3)' and MB35
           `(n+1) + (n*3)' take PUSH H/POP D, MB36 `(n*3) + n' takes XCHG, and MB28
           `n*3 + n*2' takes PUSH H even though its right operand (`DAD H') would NOT have
           destroyed DE, which is what rules out a liveness-based reading.  My old unconditional
           XCHG was a MIS-COMPILE, not a byte preference: `?IM22N' overwrites DE, so the left
           value was gone and the expression returned only the RIGHT operand -- measured at
           HEAD, mine printed 21 where DR prints 28 for `n + (n*3)', 21 vs 35 for
           `n*2 + n*3', -21 vs -14 for `n - (n*3)' [golden/e2e195r vs e2e196r].  That path was
           reachable BEFORE this milestone (via `*3', which the mul guard never refused), so the
           defect is pre-existing, not introduced by C148. *)
        if add_left_needs_push r then begin
          lower_hl st l; d st op_push_h; lower_hl st r; d st op_pop_d; d st op_dad_d
        end else
          (lower_hl st l; d st op_xchg; lower_hl st r; d st op_dad_d)
      end
  | Ast.Ebinary (Ast.Mul, l, r) when fp_mul_guard st.arrays l r ->
      failwith "codegen: internal: fp_mul_guard raised no message"
  | Ast.Ebinary (Ast.Mul, l, r) when
      (match mul_const_form st.arrays l r with
       | Some _ -> true
       | None -> false)
      ->
      (* [E2E-15/C148] DR's constant-multiply family: elide / DAD H / LXI D.  See
         mul_const_form for the measurement. *)
      (match mul_const_form st.arrays l r with
       | Some (Mul_elide x) -> lower_hl st x
       | Some (Mul_dadh (x, m)) ->
           lower_hl st x;
           for _ = 1 to m do
             d st op_dad_h
           done
       | Some (Mul_im22 (x, k)) ->
           lower_hl st x; d st op_lxi_d; d st (k land 0xff);
           d st ((k lsr 8) land 0xff);
           call_ext st "?IM22N"
       | None -> assert false)
  | Ast.Ebinary (Ast.Mul, l, r) ->
      (* var/expr OP var: DE=left HL=right, CALL ?IM22N [P071B/P080A].
         [N303] when the RHS is a 1-byte var DR interleaves: raw
         LDA, PUSH H (save left), THEN sign-extend in HL, POP D.
         [RFACT/NFACT @8D/@9C] when the RIGHT operand is a CALL the
         whole right side runs FIRST (arg eval, pair, LXI, CALL,
         PUSH H, LHLD left, POP D) — left-first ordering is only
         evidenced for plain operands [P080A]. *)
      if (match r.Ast.e with Ast.Esuffix _ -> true | _ -> false)
         && not (match l.Ast.e with Ast.Esuffix _ -> true | _ -> false)
      then begin
        lower_hl st r; d st 0xe5;                  (* PUSH H *)
        lower_hl st l; d st 0xd1                   (* POP D *)
      end else if hl_operand_deref st l
                  && (match r.Ast.e with
                      | Ast.Enumber _ -> true | _ -> false)
      then begin
        (* [E2E-9 R2036 g1] when the LEFT operand is a pointer formal, its
           deref ladder ends in XCHG -- value in HL, DE dead -- and DR then
           skips the PUSH H / LXI H / POP D rotation entirely, loading the
           literal straight into DE:
               LHLD a ; MOV E,M ; INX H ; MOV D,M ; XCHG
               LXI D,0003 ; CALL ?IM22N ; RET
           Legal because ?IM22N multiplies DE x HL, so the operand-to-register
           assignment is free.  The non-deref left case keeps the proven
           PUSH/POP shape [P071B/P080A byte-exact]. *)
        lower_hl st l;
        let rv =
          parse_int_const
            (match r.Ast.e with Ast.Enumber k -> k | _ -> "")
        in
        d st op_lxi_d; d st (rv land 0xff); d st ((rv lsr 8) land 0xff)
      end else begin
      lower_hl st l;
      (match r.Ast.e with
       | Ast.Eident rn ->
           let rvi =
             List.assoc (String.lowercase_ascii rn.Ast.orig) st.vars
           in
           if rvi.vk = Vint && rvi.size = 1 then begin
             d st 0x3a; reloc st Data (rvi.off + st.base);
             d st op_push_h;
             d st op_mov_l_a; d st op_add_a; d st op_sbb_a;
             d st op_mov_h_a;
             d st op_pop_d
           end else begin
             d st op_push_h; lower_hl st r; d st op_pop_d
           end
       | _ -> d st op_push_h; lower_hl st r; d st op_pop_d)
      end;
      call_ext st "?IM22N"
  | Ast.Ebinary (Ast.Div, l, r) ->
      (* DIV by CONSTANT only [P071B/P080A]: zero-extend const into HL via
         MVI A/PUSH/POP idiom, DE=lhs. DIV by variable = no golden -> reject.*)
      (match r.Ast.e with
       | Ast.Enumber c ->
           let n =
             parse_int_const c
           in
           if n = 0 then failwith "codegen: division by zero";
           lower_hl st l;
           d st op_mvi_a; d st (n land 0xff);
           d st op_push_h; d st op_mov_l_a; d st op_add_a; d st op_sbb_a;
           d st op_mov_h_a; d st op_pop_d; call_ext st "?ID22N"
       | _ -> failwith "codegen: DIV by non-constant [TBD]")
  | Ast.Ebinary (Ast.Exp, l, r) ->
      (* EXPONENTIATION has two DISTINCT DR lowerings (probes e2eexp):
         - VARIABLE base:  a ** n => LHLD a; MVI A,n; CALL ?IEXOP [G102]
         - LITERAL base:   k ** n => decimal POOL path
           (LXI H,*S; MVI A,p; DLDOP; MVI A,n; DEXOP; QDI15), base k stored
           as BCD pool ceil((p+1)/2) bytes, auto vars shifted up by pool
           size [P071D/G101/G103/G104/G105].  Both implemented. *)
      (match (l.Ast.e, r.Ast.e) with
       | (Ast.Eident _, Ast.Enumber c) ->
           let n =
             parse_int_const c
           in
           lower_hl st l; d st op_mvi_a; d st (n land 0xff);
           call_ext st "?IEXOP"
       | (Ast.Eident _, _) -> failwith "codegen: ** non-constant exponent [TBD]"
       | (Ast.Enumber bs, Ast.Enumber cs) ->
           let k =
             parse_int_const bs
           in
           let e =
             parse_int_const cs
           in
           let p = String.length (string_of_int k) in
           let addr = pool_alloc st (bcd_pack k p) in
           d st op_lxi_h; reloc st Data addr;
           d st op_mvi_a; d st p; call_ext st "?DLDOP";
           d st op_mvi_a; d st (e land 0xff); call_ext st "?DEXOP";
           call_ext st "?QDI15"
       | _ -> failwith "codegen: ** non-constant exponent [TBD]")
  | Ast.Ebinary (Ast.Sub, { Ast.e = Ast.Enumber ls; _ },
                 { Ast.e = Ast.Enumber rs; _ }) ->
      (* [N301/N306] const-minus-const: DEC pool chain (operands
         allocated SOURCE order; A = decimal digit count each),
         result 16-bit in HL via ?QDI15. The store tail (SHLD or
         MOV A,L;STA) is added by the assignment path. *)
      let l = parse_int_const ls in
      let r = parse_int_const rs in
      let dl = dec_digits l and dr = dec_digits r in
      let al = pool_alloc st (bcd_pack l dl) in
      let ar = pool_alloc st (bcd_pack r dr) in
      d st op_lxi_h; reloc st Data al;
      d st op_mvi_a; d st dl; call_ext st "?DLDOP";
      d st op_lxi_h; reloc st Data ar;
      d st op_mvi_a; d st dr; call_ext st "?DLDOP";
      call_ext st "?DSUOP"; call_ext st "?QDI15";
      st.last_imm <- None
  | Ast.Ebinary (Ast.Sub, x, Ast.{ e = Ast.Enumber c; _ }) ->
      lower_hl st x; const_sub st (int_of_string c)
  | Ast.Ebuilt ("MOD", [l; r]) ->
      (* mod(a,b) -> DE=dividend, HL=divisor, CALL ?IMDOP; the REMAINDER comes
         back in HL [P071B L4, and re-verified by R909 for a VARIABLE divisor].
         [E2E-7A slice 4] a CONSTANT divisor takes a different form: DR loads
         it into A and runs the sign-extend ladder (MOV L,A; ADD A; SBB A;
         MOV H,A), with PUSH H slotted between the MVI and the ladder, NOT the
         LXI H,imm form used for stores [R908/R910/R911/R912, LOAN1
         `if mod(m,12) = 0`: 000F MVI A,0C / 0011 PUSH H / 0012-0015 ladder /
         0016 POP D].  P071B only exercises the variable form, so this
         distinction was invisible until now. *)
      (match r.Ast.e with
       | Ast.Econd { Ast.e = Ast.Enumber k; _ } | Ast.Enumber k ->
           let kk = parse_int_const k in
           if kk < 0 || kk > 255 then
             failwith
              "codegen: MOD with a constant divisor outside 0..255 [TBD] \
               (only the MVI A,k form is sampled)";
           lower_hl st l;
           d st op_mvi_a; d st kk;
           d st op_push_h;
           d st 0x6f; (* MOV L,A *)
           d st 0x87; (* ADD A *)
           d st 0x9f; (* SBB A *)
           d st 0x67; (* MOV H,A *)
           d st op_pop_d
       | _ -> lower_hl st l; d st op_push_h; lower_hl st r; d st op_pop_d);
      call_ext st "?IMDOP";
      st.last_imm <- None
  | Ast.Eprefix (Ast.Minus, x) ->
      (* [N304] -x: evaluate to HL, then ?IN20N (16-bit negate) *)
      lower_hl st x; call_ext st "?IN20N"; st.last_imm <- None
    | Ast.Ebinary (Ast.Sub, l, r) ->
      (* [E2E-8 T1/T3] var - var (neither side a literal, which the arm above
         handles): DR loads the left value, XCHGs, loads the right value and
         calls ?IS22N, which computes DE - HL into HL -- the Add pair-ladder
         with the add replaced by the subtract-call
         [`s = s - i': LHLD S / XCHG / LHLD I / CALL ?IS22N / SHLD S;
           `s = i - i' identical].  POINTER-DEREF operands have no DR sample in
         this route and stay refused. *)
      if hl_operand_deref st l || hl_operand_deref st r then
        failwith "codegen: fixed-bin subtraction with a pointer formal \
                  operand unproven [TBD]";
      (* [E2E-13/C141] SUB with a CALL on the right takes the PUSH route even when the
         left operand is a simple variable -- P6 `return (t - g(3))':
             LHLD T A(0007) ; PUSH H ; LXI H,* A(0009) ; CALL G ; POP D ; CALL ?IS22N
         because ?IS22N computes DE - HL, so the MINUEND has to be in DE when the call
         finishes; there is no later load to defer the value INTO, unlike ADD [P1-P3].
         My general XCHG route parks DE across the call -- the same C139 defect the ADD
         arm just fixed.  Call on the LEFT keeps the XCHG route, byte-exact [P7]. *)
      (match r.Ast.e with
       | Ast.Esuffix _ ->
           failwith
             ("codegen: [TBD] SUB whose right operand is a procedure call.  The route is now known -- DR parks the MINUEND on the runtime stack, because ?IS22N computes DE - HL and the call has destroyed DE by then: `LHLD T / PUSH H / LXI H,* / CALL G / POP D / CALL ?IS22N' [P6, golden/e2e174/P6/P6.PRN].  I emit that sequence and my code bytes are IDENTICAL to DR's and the result is right (P6 prints 91 = DR, golden/e2e180r/P6), but DR emits the call's anonymous-cell allocation records before the left operand's code records while I emit them at point of use, so the .REL streams differ.  NOTE: my previous XCHG route was worse than a byte difference -- it parks the minuend in DE across the call, which any callee that touches DE (every shadowed/recursive one) silently corrupts.  Call on the LEFT is byte-exact and unchanged [P7].")
       | _ ->
           (if add_left_needs_push r then
              (lower_hl st l; d st op_push_h; lower_hl st r; d st op_pop_d
               ; call_ext st "?IS22N")
            else
              (lower_hl st l; d st op_xchg; lower_hl st r; call_ext st "?IS22N")));
      st.last_imm <- None
  | Ast.Ebinary _ -> failwith "codegen: operator not in int subset [TBD]"
  | _ -> failwith "codegen: expression form not in int subset [TBD]"

(* subtract an integer constant: DR folds 1 -> DCX H, small n -> repeated
   DCX H (<=4 observed); anything larger is out of this subset. *)
and const_sub st n =
  (* [E2E-13] extended past 4: DR uses `LXI B,two's-complement(-n) / DAD B' --
     n-5 -> FFFB [N5], n-6 -> FFFA [M6], n-16 -> FFF0 [M16].  Previously this
     refused, which was honest; refusing a shape DR compiles is a gap, so it is
     now covered by the measured route. *)
  if n <= 4 && n >= 1 then
    for _ = 1 to n do d st op_dcx_h done
  else if n > 4 then
    let w = (-n) land 0xffff in
    d st op_lxi_b; d st (w land 0xff); d st ((w lsr 8) land 0xff); d st op_dad_b
  else failwith "codegen: constant sub magnitude [TBD]"

(* store a char literal into a char/varying variable [V101-V105] *)
let store_char st name (k : vkind) (v : string) =
  if List.mem (String.lowercase_ascii name) st.deref then
    failwith "codegen: store to pointer formal unproven [TBD]";
  let len = String.length v in
  if len > 255 then failwith "codegen: literal len > 255 [TBD]";
  d st op_lxi_h; reloc st Data (addr_of st name);
  match k with
  | Vvar cap ->
      (* V104/V108 evidence: the literal registers a pool BLOCK even
         when empty; only non-empty stores emit LXI D/?SMCVM. *)
      let bytes =
        Array.init len (fun i -> Char.code (String.get v i))
      in
      (* [E2E-16/C152] dedup'd like the PUT path: PL11 (`c = 'W'; c = 'W';') pools ONE byte. *)
      let addr = pool_str st bytes in
      if len = 0 then (d st op_mvi_m; d st 0)     (* [V104] *)
      else begin
        d st op_lxi_d; reloc st Data addr;         (* LXI D,*S [V101] *)
        d st op_mvi_a; d st (cap land 0xff);       (* A = capacity *)
        if len = cap then d st op_mov_b_a          (* [V102/V103] *)
        else begin d st op_mvi_b; d st len end;    (* B = length; len>cap
            ALLOWED as-is [V105 B=07,cap=3; RTL semantics not assumed] *)
        call_ext st "?SMCVM"
      end
  | Vfix cap ->
      (* only the V106 shape (0 < len < cap) is proven for fixed *)
      if len = 0 || len > cap then
        failwith "codegen: fixed-char store form unproven [TBD]"
      else if len = cap then
        failwith "codegen: fixed store len==cap MOV B/A unproven [TBD]"
      else begin
        let bytes =
          Array.init len (fun i -> Char.code (String.get v i))
        in
        let addr = pool_str st bytes in   (* [E2E-16/C152] content dedup [PL10/PL11] *)
        d st op_lxi_d; reloc st Data addr;
        d st op_mvi_a; d st cap;
        d st op_mvi_b; d st len;
        call_ext st "?SMCCM"
      end
  | Vint -> failwith "codegen: char store to numeric var [TBD]"

let is_small_int st (n : Ast.name) =
  let li = String.lowercase_ascii n.Ast.orig in
  match List.assoc_opt li st.vars with
  | Some vi -> vi.vk = Vint && vi.size = 1
  | None -> false

(* ================= [E2E-6] FIXED DECIMAL evaluation ================== *
   DR's decimal machine, read straight off the $C traces of R501-R512
   (golden/e2e6) and DFACT (golden/first8080u/DFACT + its re-probe):

     ?DLDOP  PUSH a DEC value:  HL = cell address, A = digits
     ?QI15D  PUSH: INT(15) value already in HL -> DEC
     <call>  a DEC function call leaves its result on the DEC stack --
             the callee exits with JMP ?DCRET instead of RET
             [DFACT @003E/@0093, R509 @0009]
     ?DADOP ?DSUOP ?DMUOP  pop two, push one.  Operands are pushed LEFT
             first [R505 a+b, c-a, a*b; R511 a*1234]; the one observed
             case where the RIGHT operand is a DEC call pushes it first,
             because the call has to run before the left operand is
             reloaded [DFACT: call, then LHLD i + ?QI15D, then ?DMUOP]
     ?QDDSR  rescale the top to the scale in A -- observed ONLY after
             ?DMUOP and ONLY when the store target has scale > 0
             [R505 dec(9,2) -> MVI A,02; R510 dec(9,0) -> none;
             DFACT dec(15,0) -> none].  ADD/SUB carry no rescale [R505].
             DIVISION (?QDDSL before / ?DDVOP / TWO ?QDDSR after)
             is NOT implemented -- unpinned, stays [TBD] [R512].
     ?DSTOP  POP into a DEC cell: HL = address, A = target digits
             [R501/R502/R503/R505/R508/R510/R511]
     ?QDCOP  POP and edit into the print buffer: A = width = p+3,
             B = scale [R501 18/0, R502 12/2, R503 8/0, R508 10/2,
             R510 12/0, R511 12/0, DFACT 18/0 -- p+3 on every sample]
     ?DCRET  DEC function exit: hand the top DEC value back to the
             caller [DFACT @0086/@00A2, R509 @0056]

   DEC LITERAL cells (pool, little-endian packed BCD, sign nibble in the
   top nibble of the last byte -- byte-for-byte verified against DR:
   3@p15 -> 01? no: 03 00 00 00 00 00 00 00 [R501]; 123.45@p7s2 ->
   45 23 01 00 [R508]; 1@p9s2 -> 00 01 00 00 00 [R505]; 1234@p4 ->
   34 12 [R511]; 1@p15s0 -> 01 00 .. [DFACT]):
     bare literal in assignment/RETURN position -> the TARGET's digits
     and scale [R501 d=3 p15; R505 a=1 p9 s2; DFACT return(1) p15]
     literal as an ARITHMETIC OPERAND -> its OWN digit count, scale 0
     [R509 *2 -> 1 byte/MVI A,01; R511 *1234 -> 2 bytes/MVI A,04]
   Negative literals, fractional literals in operand position, DEC
   comparisons and DEC arrays/structs are outside this evidence and are
   refused loudly. *)

(* little-endian packed BCD of the ALREADY-SCALED magnitude v *)
let bcd_pack_scaled (v : int) (p : int) =
  let nbytes = dec_pool_bytes p in
  let ds = string_of_int v in
  if String.length ds > p then
    failwith "codegen: DEC literal does not fit its precision [TBD]";
  let digs =
    Array.init p (fun i ->
      let j = i - (p - String.length ds) in
      if j >= 0 then Char.code (String.get ds j) - 48 else 0)
  in
  let lsf = Array.to_list digs |> List.rev in
  let nib i = try List.nth lsf i with _ -> 0 in
  Array.init nbytes (fun b -> ((nib (2 * b + 1)) lsl 4) lor (nib (2 * b)))

let dec_pool st ~prec ~scale ~text =
  let (mag, _own, ls) = dec_lit_value text in
  if mag < 0 || ls > scale then
    failwith
      (Printf.sprintf
         "codegen: DEC literal %s into scale %d [TBD] (only same-or-less \
          fractional digits are pinned; negative DEC literals are unpinned)"
         text scale);
  let rec mul10 v n = if n = 0 then v else mul10 (v * 10) (n - 1) in
  let bytes = bcd_pack_scaled (mul10 mag (scale - ls)) prec in
  let key = Array.to_list bytes in
  match List.assoc_opt key st.dec_cells with
  | Some addr -> addr                       (* [R614] reuse the live cell *)
  | None ->
      let addr = pool_alloc st bytes in
      st.dec_cells <- (key, addr) :: st.dec_cells;
      addr

let vk_dec vk = match vk with Vdec (p, s) -> Some (p, s) | _ -> None

let vk_dec_opt st (n : Ast.name) =
  match List.assoc_opt (String.lowercase_ascii n.Ast.orig) st.vars with
  | Some vi -> vk_dec vi.vk
  | None -> None

(* is this expression DEC-typed on the proven routes? *)
let rec is_dec_expr st (e : Ast.expr) : bool =
  match e.Ast.e with
  | Ast.Econd x -> is_dec_expr st x
  | Ast.Eident n -> vk_dec_opt st n <> None
  | Ast.Ebuilt ("DECIMAL", _) -> true
  | Ast.Esuffix (b, _) ->
      (match b.Ast.e with
       | Ast.Eident n ->
           (match List.assoc_opt (String.lowercase_ascii n.Ast.orig) st.procs
            with
            | Some pl ->
                (match pl.Bind.pl_ret with
                 | Some (Bind.RTdec _) -> true
                 | _ -> false)
            | None -> false)
       | _ -> false)
  | Ast.Ebinary (_, l, r) -> is_dec_expr st l || is_dec_expr st r
  | Ast.Eprefix (_, x) -> is_dec_expr st x
  | _ -> false

(* true iff every leaf of this DEC-typed expression is itself decimal:
   mixed DEC/INT arithmetic has NO golden evidence at all, so the DEC
   paths accept only pure decimal trees and refuse the mix loudly.
   (decimal(x,p) is the sanctioned INT->DEC doorway [R506/R509/DFACT];
   a DEC->INT conversion is proven only for a DIRECT decimal operand.) *)
let rec dec_pure st (e : Ast.expr) : bool =
  match e.Ast.e with
  | Ast.Econd x -> dec_pure st x
  | Ast.Eident n -> vk_dec_opt st n <> None
  | Ast.Ebuilt ("DECIMAL", _) -> true
  | Ast.Esuffix _ -> true                 (* DEC function result [DFACT] *)
  | Ast.Enumber _ -> true                 (* decimal literal cell *)
  | Ast.Ebinary (_, l, r) -> dec_pure st l && dec_pure st r
  | Ast.Eprefix (_, x) -> dec_pure st x
  | _ -> false

(* (precision, scale) to use when EDITING a DEC expression on output.
   Only the two directly observed shapes are allowed: a DEC variable
   [R501-R511] and a DEC function call [DFACT].  Printing the result of
   decimal() or of a DEC arithmetic expression directly is unpinned. *)
let dec_edit_pt st (e : Ast.expr) : int * int =
  match e.Ast.e with
  | Ast.Eident n ->
      (match vk_dec_opt st n with
       | Some ps -> ps
       | None ->
           failwith (Printf.sprintf
                       "codegen: PUT LIST decimal item on non-decimal \
                        variable %s [TBD]" n.Ast.orig))
  | Ast.Esuffix (b, _) ->
      (match b.Ast.e with
       | Ast.Eident n ->
           (match List.assoc_opt (String.lowercase_ascii n.Ast.orig) st.procs
            with
            | Some pl ->
                (match pl.Bind.pl_ret with
                 | Some (Bind.RTdec (p, s)) -> (p, s)
                 | _ ->
                     failwith
                       "codegen: PUT LIST item is not a decimal function \
                        [TBD]")
            | None ->
                failwith "codegen: PUT LIST decimal item call unresolved [TBD]")
       | _ -> failwith "codegen: PUT LIST decimal item shape [TBD]")
  | _ ->
      failwith "codegen: PUT LIST decimal editing of this expression is \
                unproven [TBD]"

(* ---- [E2E-7A slice 2] DECIMAL value model ---------------------------
   A value on DR's decimal stack carries (p = digits, s = scale).  dv_of
   computes that descriptor WITHOUT emitting anything; dpush emits the
   instruction sequence the descriptor implies, so the LAWS live in exactly
   one place and the emitter cannot drift from them.

   * QDDSL / QDDSR shift the CURRENT TOP OF STACK, and their POSITION in
     the sequence identifies which value is being shifted: between the two
     operand pushes it is the first-pushed operand, after both pushes it is
     the second-pushed one.  That is what makes the pair readable:
        a(9,2)+b(6,4): push a, QDDSL 2, push b, DADOP, QDDSR 2   [R705]
        a(9,4)+b(6,2): push a, push b, QDDSL 2, DADOP            [R707]
        e(9,2)-f(6,4): push e, QDDSL 2, push f, DSUOP, QDDSR 2   [R715]
        a(9,2)>e(6,4): push e, push a, QDDSL 2, DCMOP            [R723]
   * +/- and compare ALIGN to max(s_l,s_r) by shifting the SHORTER operand
     up; equal scales emit nothing [R505, LOAN1 `p = p - pmt`].  R715 pins
     both directions for subtraction, so the law is evidenced for - and not
     merely inherited from +.
   * * needs NO alignment: result scale = s_l + s_r [R711 `d = a*b` into
     dec(9,4) emits no shift whatsoever; R719/R720 product scale 4 into a
     dec(9,2) target gets QDDSR 2].
   * / pre-shifts the DIVIDEND up by N = 15 - p_dividend (omitted when the
     dividend already has 15 digits) so the quotient is computed at 15
     working digits; quotient scale = s_l + N - s_r, or s_l - s_r when
     N = 0.  Evidence: R512/R701/R703/R708 (p=9 -> 6), R710 (p=11 -> 4, so
     N is not a constant), R702 (dividend dec(9,2) with a dec(13,2) TARGET
     still gets 6, so N tracks the DIVIDEND, not the target), R714 (N=5 ->
     add-result precision 10), R717 (N=8 -> 7), R718 (N=4 -> mul 11; N=9 ->
     sub 6), LOAN1/R704 (dividend is a 15-digit product -> N=0 -> no pair).
     Division TRUNCATES: R706 ran 2/3 -> 0.66 and 9/2 into dec(9,0) -> 4.
   * the CONSUMER fixes a value's scale: DOWN with QDDSR, UP with QDDSL.
     store/return target [R701 down 4, R713 down 2, R716 UP 2 to dec(13,8),
     R711 UP 2 for an add into dec(9,4), R505 down 2 after a multiply]; an
     enclosing +/- aligns instead and adds no fix, so a quotient carries its
     scale straight in [R721, R722].
   * result precision is observable ONLY through the next division's N:
        add/sub: min(p_l,p_r)+1     [R714, R717, R718]
        mul:     min(15,p_l+p_r+1)  [R718, LOAN1/R704 via N=0]
        div:     UNPINNED -- no sample exposes a quotient's precision, so a
                 quotient used where p is required refuses [TBD].
   * push order: the RIGHT operand is pushed first iff it is compound and
     the left is simple [DFACT `decimal(i,15) * factorial(i-1)`, R704,
     R719, R722]; otherwise LEFT first -- both compound [R720, R724] and
     both simple [R505, R705, R707] included.  Division always pushes the
     dividend first, even against a compound divisor [R712], because the N
     pre-shift has to act on the dividend while it is still the top.
   * integer literals: additive/compare positions align to the DEC partner
     [R608, R507/R607]; multiplicative positions take their own digit count
     with scale 0 [R509 *2 A=01, R511 *1234 A=04, R512/R703/R710 /2 /8 A=01,
     LOAN1 /1200 A=04]; store/return positions take the target (p,s) [C084].
*)
type dv = { pv : int option; sc : int }

type dctx =
  { c_tgt : (int * int) option   (* store/RETURN target: fixes the scale *)
  ; c_lit : (int * int) option   (* DEC partner of an additive/compare literal *)
  ; c_mult : bool                (* multiplicative operand position *)
  ; c_round : bool }             (* [slice 3] argument of a ROUND [R811] *)

let dsl st n = d st op_mvi_a; d st n; call_ext st "?QDDSL"
let dsr st n = d st op_mvi_a; d st n; call_ext st "?QDDSR"

(* an operand that costs more than one decimal-stack emission.  [E2E-7A
   slice 3] ROUND joins it: LOAN1 and R807 both push `X + round(a/b,n)` with
   the round SUBTREE FIRST even though it sits on the right, which is exactly
   the right-compound/left-simple rule L7 -- so a round node with a compound
   argument behaves like a compound operand.  A round node whose argument is
   SIMPLE is NOT claimed to be compound: no sample shows which side DR pushes
   first for `p + round(a,2)`, and that shape refuses in dpush. *)
let dcompound _st (e : Ast.expr) =
  match (unwrap_e e).Ast.e with
  | Ast.Ebinary _ | Ast.Esuffix _ -> true
  | Ast.Ebuilt ("ROUND", [ a; _ ]) ->
      (match (unwrap_e a).Ast.e with Ast.Ebinary _ -> true | _ -> false)
  | _ -> false

(* the (p,s) an additive/compare integer literal aligns to: only a DEC
   variable or a DEC function call is evidenced [R608, R507/R607] *)
let dpartner st (e : Ast.expr) : (int * int) option =
  match (unwrap_e e).Ast.e with
  | Ast.Eident n -> vk_dec_opt st n
  | Ast.Esuffix _ -> Some (dec_edit_pt st e)
  | _ -> None

let nop_cx = { c_tgt = None; c_lit = None; c_mult = false; c_round = false }
let round_arg_cx = { c_tgt = None; c_lit = None; c_mult = false; c_round = true }

(* ------------------------------------------------------------------ *
 * ROUND(expr, n)  ->  MVI A, k ; CALL ?DROUN        [E2E-7A slice 3]  *
 *                                                                    *
 * DR's convention, from R801-R812 + LOAN1:                           *
 *   the rounded value stays ON TOP of the decimal stack; ?DROUN takes *
 *   ONE byte argument, k = (scale of the entry) - n, i.e. the number  *
 *   of fractional digits to drop, NOT the target scale n.  Observed   *
 *   bytes: dec(9,3) round 2 -> A=01 [R801/R802/R803]; 2/3 at scale 6  *
 *   round 2 -> A=04 [R804/R807]; LOAN1 product+divide at scale 4      *
 *   round 2 -> A=02; dec(9,3) round 0 -> A=03 [R806]; nested          *
 *   round(round(a,3),2) -> A=00 then A=01 [R811] (k=0 IS emitted, it   *
 *   is not elided the way the divide pre-shift is at N=0).            *
 *   The entry KEEPS its scale: after DROUN the consumer fix and the   *
 *   enclosing +/- alignment are computed from the ORIGINAL scale,      *
 *   which is what makes R801's `MVI A,02; CALL ?QDDSR`, R807's         *
 *   `QDDSL 4` before DADOP and LOAN1's `QDDSL 2`/`QDDSR 2` all follow  *
 *   laws L1/L5 already banked in C086 -- ROUND adds no shift of its    *
 *   own.  Rounding is HALF-UP and away from zero (DR runtime: 2.125 -> *
 *   2.13, 2.135 -> 2.14, 2.145 -> 2.15, 2.155 -> 2.16, -2.125 ->       *
 *   -2.13, 2.5 -> 3), and it sees the PRE-STORE stack value, not a     *
 *   truncated copy (R804 prints 0.67 next to x = 2/3's stored 0.66).   *
 *   My compiler emits bytes only -- the arithmetic is DR's ?DROUN --   *
 *   so the mode is evidence for the model, not a rule I implement.     *
 * ------------------------------------------------------------------ *)
let round_split args =
  match args with
  | [ x; nn ] -> (unwrap_e x, nn)
  | [ _ ] ->
      failwith
        "codegen: one-argument ROUND is unproven [TBD] (DR rejects `y = round(a);` \
         itself, with pass-2 `SYNTAX ?` and no .REL [R808])"
  | _ -> failwith "codegen: ROUND arity [TBD]"

let round_n nn =
  match (unwrap_e nn).Ast.e with
  | Ast.Enumber k ->
      let (v, _own, lsc) = dec_lit_value k in
      if lsc <> 0 then
        failwith "codegen: ROUND with a fractional digit count [TBD]";
      if v < 0 then failwith "codegen: ROUND with a negative digit count [TBD]";
      v
  | _ ->
      failwith
        "codegen: ROUND whose digit count is not an integer literal is unproven \
         [TBD] (DR computes it at RUNTIME as LHLD/MOV A,L/SUI 04/CMA [R812]; \
         the static form is the only one LOAN1 needs)"

(* validate the ROUND shape and return (n, argument descriptor) *)
(* everything about a ROUND node that needs no value descriptor: arity, the
   digit-count literal, and the argument shape.  The scale-vs-n check lives
   in dv_of, which is the only place that can see the entry scale. *)
let round_shape st args =
  let (x, nn) = round_split args in
  let n = round_n nn in
  begin
    match (unwrap_e x).Ast.e with
    | Ast.Eident n ->
        (match vk_dec_opt st n with
         | Some _ -> ()
         | None ->
             failwith
               "codegen: ROUND of a non-DECIMAL (integer) argument is unproven \
                [TBD] (DR rounds the INTEGER with a separate route, ?IROUN, \
                then converts via ?QI15D and emits NO ?DROUN at all [R810]; \
                LOAN1 never rounds an integer expression)")
    | Ast.Ebinary _ | Ast.Esuffix _ | Ast.Ebuilt ("ROUND", _) -> ()
    | Ast.Enumber _ ->
        failwith
          "codegen: ROUND of a bare literal is unproven [TBD] (R809 shows DR \
           pushing the literal with its OWN digit count AND own scale, \
           A=04 for 2.125 -- a third literal role with one sample only)"
    | _ ->
        failwith
          "codegen: ROUND of a non-decimal argument is unproven [TBD] (an \
           INTEGER argument takes DR's separate ?IROUN route, then ?QI15D \
           with no ?DROUN at all [R810])"
  end;
  (x, n)

(* context for a BINARY operand: a direct integer literal takes its
   partner's precision in an additive/compare position and its own digit
   count in a multiplicative one; anything else inherits nothing *)
let dchild_cx _st op partner x =
  match op with
  | Ast.Mul | Ast.Div ->
      { c_tgt = None; c_lit = None; c_mult = true; c_round = false }
  | _ ->
      (match (unwrap_e x).Ast.e with
       | Ast.Enumber _ ->
           { c_tgt = None; c_lit = partner; c_mult = false; c_round = false }
       | _ -> nop_cx)

let rec dv_of st (cx : dctx) (e : Ast.expr) : dv =
  match (unwrap_e e).Ast.e with
  | Ast.Eident n ->
      (match vk_dec_opt st n with
       | Some (p, s) -> { pv = Some p; sc = s }
       | None ->
           failwith
             (Printf.sprintf
                "codegen: decimal operation on non-decimal operand %s [TBD]"
                n.Ast.orig))
  | Ast.Ebuilt ("DECIMAL", _) ->
      (* decimal(x,p): the precision ARGUMENT is ignored [R506], so the
         result descriptor comes from context, exactly as in C084 *)
      (match cx.c_tgt with
       | Some (p, s) -> { pv = Some p; sc = s }
       | None -> { pv = Some 15; sc = 0 })
  | Ast.Ebuilt ("ROUND", args) ->
      let (x, n) = round_shape st args in
      let da = dv_of st round_arg_cx x in
      if da.sc < n then
        failwith
          "codegen: ROUND with a digit count ABOVE the operand scale is \
           unproven [TBD] (R805: dec(9,3) round 5 makes DR emit the WRAPPED \
           byte 3-5 = 0xFE; the value came back unchanged, but one sample \
           does not pin the rule and LOAN1 never asks for it)";
      (* SCALE AND PRECISION ARE RETAINED: R801/R804/R807 show the consumer
         fix and the enclosing +/- alignment still computed from the operand's
         original scale after DROUN.  pv is inherited; nothing exposes a
         rounded value's precision, so a ROUND result used where p matters
         refuses below (same family as the quotient-precision gap). *)
      { pv = da.pv; sc = da.sc }
  | Ast.Esuffix _ ->
      let (p, s) = dec_edit_pt st e in
      { pv = Some p; sc = s }
  | Ast.Enumber k ->
      let (_v, own, lsc) = dec_lit_value k in
      (match cx.c_tgt, cx.c_lit with
       | Some (tp, ts), _ -> { pv = Some tp; sc = ts }
       | None, Some (pp, ps) ->
           if lsc > 0 then
             failwith
               "codegen: fractional DEC literal aligned to a decimal partner \
                [TBD] (only an integral literal is pinned in additive or \
                compare position [R608/R507])";
           { pv = Some pp; sc = ps }
       | None, None ->
           if lsc > 0 then
             failwith
               "codegen: fractional DEC literal in multiplicative operand \
                position [TBD]";
           { pv = Some own; sc = 0 })
  | Ast.Ebinary (op, l, r) ->
      let cl = dchild_cx st op (dpartner st r) l in
      let cr = dchild_cx st op (dpartner st l) r in
      let dl = dv_of st cl l and dr = dv_of st cr r in
      begin
        match op with
        | Ast.Add | Ast.Sub ->
          { pv =
              (match (dl.pv, dr.pv) with
               | Some a, Some b -> Some (min 15 (1 + min a b))
               | _ -> None);
            sc = max dl.sc dr.sc }
        | Ast.Mul ->
            { pv =
                (match (dl.pv, dr.pv) with
                 | Some a, Some b -> Some (min 15 (a + b + 1))
                 | _ -> None);
              sc = dl.sc + dr.sc }
        | Ast.Div ->
          (match (unwrap_e l).Ast.e with
           | Ast.Ebuilt ("ROUND", _) ->
               failwith
                 "codegen: ROUND result as a DECIMAL divide dividend is unproven \
                  [TBD] (the pre-shift wants 15 - p of the ROUNDED entry; no \
                  sample shows what p a rounded value carries)"
           | _ -> ());
          let n =
            match dl.pv with
            | Some p -> 15 - p
            | None ->
                failwith
                  "codegen: DECIMAL divide with an unpinned dividend \
                   precision [TBD] (a quotient's precision is not \
                   observable in any sample)"
          in
          let sc = if n > 0 then dl.sc + n - dr.sc else dl.sc - dr.sc in
          if sc < 0 then
            failwith
              "codegen: DECIMAL divide yielding a negative scale [TBD] \
               (no sample puts more fractional digits in the divisor than \
               in the dividend)";
          { pv = None; sc }
        | _ ->
            failwith
              "codegen: decimal operator not in the DEC subset [TBD] \
               (mod/exp/shift on the decimal stack are unpinned)"
      end
  | _ ->
      failwith
        (Printf.sprintf "codegen: decimal expression shape %s not in the DEC \
                         subset [TBD]" (expr_kind_name (unwrap_e e).Ast.e))

(* push one DEC value; emits exactly what dv_of says the descriptor needs *)
let rec dpush st (cx : dctx) (e : Ast.expr) : dv =
  let vd = dv_of st cx e in
  match (unwrap_e e).Ast.e with
  (* [E2E-7A slice 3] ROUND must NOT be swallowed by the simple-operand arm:
     it pushes its argument, then ?DROUN, then takes the ordinary consumer
     fix.  Unknown builtins never reach here anyway -- dv_of, which runs
     first, refuses them. *)
  | Ast.Eident _ | Ast.Ebuilt ("DECIMAL", _) | Ast.Esuffix _ | Ast.Enumber _ ->
      dpush_simple st cx e vd;
      (match cx.c_tgt with
       (* A simple operand whose own scale differs from the store target is
          UNPROVEN: every sample that needed a scale fix had a computed
          value [R711, R713, R716], and LOAN1's `PMT = P` crosses
          PRECISIONS but not scales, which ?DSTOP's A argument already
          covers.  Refuse rather than assume DSTOP rescales. *)
       | Some (_, ts) when ts <> vd.sc ->
           failwith
             "codegen: DECIMAL assignment between differing scales is \
              unproven [TBD] (only computed results are pinned as needing a \
              QDDSL/QDDSR fix; a direct DEC operand store always had equal \
              scales in the samples)"
       | _ -> ());
      vd
  | Ast.Ebinary (op, l, r) ->
      let cl = dchild_cx st op (dpartner st r) l in
      let cr = dchild_cx st op (dpartner st l) r in
      begin
        match op with
        | Ast.Div ->
            (match (unwrap_e l).Ast.e with
             | Ast.Enumber _ ->
                 failwith
                   "codegen: DECIMAL divide with a literal dividend is \
                    unproven [TBD] (every sample divides a variable, a call \
                    result or a computed value)"
             | _ -> ());
            (match (unwrap_e r).Ast.e with
             | Ast.Ebuilt ("ROUND", _) ->
                 failwith
                   "codegen: ROUND result as a DECIMAL divide divisor is unproven \
                    [TBD] (only `a / b` operands are sampled)"
             | _ -> ());
            ignore (dpush st cl l);
            let n =
              match (dv_of st cl l).pv with
              | Some p -> 15 - p
              | None ->
                  failwith
                    "codegen: DECIMAL divide with an unpinned dividend \
                     precision [TBD]"
            in
            if n > 0 then dsl st n;
            ignore (dpush st cr r);
            call_ext st "?DDVOP"
        | (Ast.Add | Ast.Sub | Ast.Mul) as opn ->
            let align =
              match opn with Ast.Mul -> false | _ -> true
            in
            let rf = dcompound st r && not (dcompound st l) in
            let (ef, ex, cxf, cxo, df, dx) =
              if rf
              then (r, l, cr, cl, dv_of st cr r, dv_of st cl l)
              else (l, r, cl, cr, dv_of st cl l, dv_of st cr r)
            in
            ignore (dpush st cxf ef);
            if align && df.sc < dx.sc then dsl st (dx.sc - df.sc);
            ignore (dpush st cxo ex);
            if align && dx.sc < df.sc then dsl st (df.sc - dx.sc);
            call_ext st
              (match opn with
               | Ast.Add -> "?DADOP"
               | Ast.Sub -> "?DSUOP"
               | _ -> "?DMUOP")
        | _ ->
            failwith
              "codegen: decimal operator not in the DEC subset [TBD] \
               (mod/exp/shift on the decimal stack are unpinned)"
      end;
      (* the consumer fixes the scale of a COMPUTED value [R701, R711,
         R713, R716, R721, R722]; an enclosing +/- aligns its operands
         instead, so an operand-context value gets no fix here *)
      (match cx.c_tgt with
       | Some (_, ts) when ts > vd.sc -> dsl st (ts - vd.sc)
       | Some (_, ts) when ts < vd.sc -> dsr st (vd.sc - ts)
       | _ -> ());
      vd
  | Ast.Ebuilt ("ROUND", args) ->
      let (x, n) = round_shape st args in
      (* position legality, from the samples that exist: whole-RHS / return
         [R801-R806, R811] and an additive operand whose argument is COMPOUND
         [R807, LOAN1].  A simple-argument round on either side of +/- has no
         push-order sample, and one in a multiplicative position has none
         either. *)
      begin
        match cx with
        | { c_tgt = Some _; _ } -> ()
        | { c_round = true; _ } -> ()   (* nested round [R811] *)
        | { c_mult = true; _ } ->
            failwith
              "codegen: ROUND in a multiplicative DECIMAL position is unproven \
               [TBD] (no sample multiplies or divides by a rounded value)"
        | _ ->
            if not (dcompound st e) then
              failwith
                "codegen: ROUND with a SIMPLE argument inside +/- is unproven \
                 [TBD] (R807/LOAN1 pin the order only when the rounded \
                 subtree is compound, so which side DR pushes first here is \
                 unknown)"
      end;
      ignore (dpush st round_arg_cx x);
      d st op_mvi_a;
      d st (vd.sc - n);
      call_ext st "?DROUN";
      (* the rounded entry keeps its scale, so the SAME consumer rule as any
         other computed value decides the shift afterwards [R801, R804, R806] *)
      (match cx.c_tgt with
       | Some (_, ts) when ts > vd.sc -> dsl st (ts - vd.sc)
       | Some (_, ts) when ts < vd.sc -> dsr st (vd.sc - ts)
       | _ -> ());
      vd
  | _ ->
      failwith
        (Printf.sprintf "codegen: decimal push of expression shape %s is not \
                         in the DEC subset [TBD]"
           (expr_kind_name (unwrap_e e).Ast.e))
and dpush_simple st (_cx : dctx) (e : Ast.expr) (vd : dv) =
  match (unwrap_e e).Ast.e with
  | Ast.Eident n ->
      let p = Option.get vd.pv in
      (* a DEC FORMAL is a by-reference pointer cell, so the address must be
         LOADED, not used inline [DECPOLY @10D-112, R709/R725] *)
      if List.mem (String.lowercase_ascii n.Ast.orig) st.deref then
        d st op_lhld
      else
        d st op_lxi_h;
      reloc st Data (addr_of st n.Ast.orig);
      d st op_mvi_a; d st p; call_ext st "?DLDOP"
  | Ast.Ebuilt ("DECIMAL", args) ->
      (match args with
       | [ x ] | [ x; _ ] -> lower_hl st x; call_ext st "?QI15D"
       | _ -> failwith "codegen: DECIMAL builtin arity [TBD]")
  | Ast.Esuffix _ -> lower_hl st e
  | Ast.Enumber k ->
      let (p, sc) = (Option.get vd.pv, vd.sc) in
      let addr = dec_pool st ~prec:p ~scale:sc ~text:k in
      d st op_lxi_h; reloc st Data addr;
      d st op_mvi_a; d st p; call_ext st "?DLDOP"
  | _ ->
      failwith
        (Printf.sprintf "codegen: decimal push of this operand shape is not \
                         in the DEC subset [TBD] (%s)"
           (expr_kind_name (unwrap_e e).Ast.e))

(* compatibility wrapper used by the store/PUT/compare paths *)
let dec_push st (tgt : (int * int) option) (e : Ast.expr) : int * int =
  let d =
    dpush st { c_tgt = tgt; c_lit = None; c_mult = false; c_round = false } e
  in
  (match d.pv with Some p -> (p, d.sc) | None -> (0, d.sc))

(* ---- [E2E-7A slice 1] helpers for DECIMAL comparison -------------- *)
(* unwrap_e is defined with the DECIMAL value model above *)
(* a comparison operand is DEC-typed if it is a DEC variable or a DEC
   function call [R601-R606 var/var, LOAN1 P<PMT]; decimal(x,p) in a
   relation is NOT pinned, so it stays refused *)
let is_dec_operand st (e : Ast.expr) =
  match (unwrap_e e).Ast.e with
  | Ast.Eident n -> vk_dec_opt st n <> None
  | Ast.Esuffix (b, _) ->
      (match b.Ast.e with
       | Ast.Eident n ->
           (match List.assoc_opt (String.lowercase_ascii n.Ast.orig) st.procs
            with
            | Some pl ->
                (match pl.Bind.pl_ret with Some (Bind.RTdec (_, _)) -> true
                 | _ -> false)
            | None -> false)
       | _ -> false)
  | _ -> false

let dec_pt_of st (e : Ast.expr) =
  match (unwrap_e e).Ast.e with
  | Ast.Eident n -> vk_dec_opt st n
  | Ast.Esuffix (b, _) ->
      (match b.Ast.e with
       | Ast.Eident n ->
           (match List.assoc_opt (String.lowercase_ascii n.Ast.orig) st.procs
            with
            | Some pl ->
                (match pl.Bind.pl_ret with
                 | Some (Bind.RTdec (p, q)) -> Some (p, q)
                 | _ -> None)
            | None -> None)
       | _ -> None)
  | _ -> None

(* precision/scale each side is pushed with.  A plain integer literal on
   one side becomes a DEC pool cell taking the OTHER operand's precision
   [R507/R607: `0` pushed as MVI A,09 against a dec(9,2) variable], and
   LOAN1 needs exactly `P > 0` with p = dec(11,2) [6-byte cell S(001E)].
   Where BOTH operands are decimal, a literal has no "other side" to take
   precision from, and `p > 3` against a dec(9,2) variable is refused:
   the two candidate encodings (0 vs 300, i.e. scale 0 vs 2) are not
   distinguished by any existing sample. *)
let dec_cmp_pt st (a : Ast.expr) (b : Ast.expr) =
  let la = match (unwrap_e a).Ast.e with Ast.Enumber k -> Some k | _ -> None in
  let lb = match (unwrap_e b).Ast.e with Ast.Enumber k -> Some k | _ -> None in
  let da = dec_pt_of st a and db = dec_pt_of st b in
  match da, db, la, lb with
  | Some (pa, sa), Some (pb, sb), None, None ->
      ((pa, sa, None), (pb, sb, None))
  | Some (pa, sa), None, None, Some kb ->
      ((pa, sa, None), (pa, sa, Some kb))
  | None, Some (pb, sb), Some ka, None ->
      ((pb, sb, Some ka), (pb, sb, None))
  | _ ->
      failwith
        "codegen: decimal comparison operands not in the proven DEC subset \
         [TBD] (DEC variable / DEC-function call / integer-0 literal only; \
         decimal(x,p) in a relation is unpinned, and a scale-carrying \
         literal against a scaled variable is unproven)"

(* push one comparison operand: decimal operands go through dec_push; a
   literal is pre-scaled to the other side's precision, with the scale
   restriction above. *)
let dec_cmp_push st (e : Ast.expr) ((p, s, lit) : int * int * string option) =
  match lit with
  | Some k ->
      let (v, _own, lsc) = dec_lit_value k in
      if not (lsc = 0 && (s = 0 || v = 0)) then
        failwith
          "codegen: decimal comparison literal scale unproven [TBD] (only an \
           integral literal, or any literal equal to 0, is pinned against a \
           scaled decimal operand [R507/R607 use 0])";
      ignore (dec_push st (Some (p, s)) (unwrap_e e))
  | None -> ignore (dec_push st None e)

(* emit a FIXED DECIMAL relation: the push pair (order fixed by the
   relation [C085]), any scale alignment [R723], then ?DCMOP.  Returns the
   SKIP-jump opcode that encodes the relation, so both the single-condition
   arm (backpatch a jump) and the conjunction arm (materialize a boolean
   byte) share ONE lowering of the relation. *)
let dec_cmp_rel st (rop : Ast.relop) (a : Ast.expr) (b : Ast.expr) =
  let (pa, pb) = dec_cmp_pt st a b in
  let (right_first, opc) =
    match rop with
    | Ast.Gt -> (true, op_jp)   | Ast.Lt -> (false, op_jp)
    | Ast.Ge -> (false, op_jm)  | Ast.Le -> (true, op_jm)
    | Ast.Eq -> (false, op_jnz) | Ast.Ne -> (false, 0xca)
  in
  if right_first
  then (dec_cmp_push st b pb; dec_cmp_push st a pa)
  else (dec_cmp_push st a pa; dec_cmp_push st b pb);
  (* [R723] the SAME alignment law +/- use applies to a relation: when
     the two operands have different scales DR shifts the SHORTER one
     up to the longer before ?DCMOP.  Because the relation fixes the
     push order [C085], only the case where the TOP (second-pushed)
     operand is the short one is reachable with a proven mechanism --
     QDDSL acts on the top of the stack, and shifting the DEEPER value
     would need a pop-and-restore sequence no sample shows, so that
     shape refuses rather than guessing. *)
  let sc_of (_, x, _) = x in
  let (s_top, s_deep) =
    if right_first then (sc_of pa, sc_of pb) else (sc_of pb, sc_of pa)
  in
  if s_top < s_deep then dsl st (s_deep - s_top)
  else if s_deep < s_top then
    failwith
      ("codegen: decimal comparison alignment on the deeper operand is " ^
       "unproven [TBD] (DR aligns by shifting the TOP of the decimal stack " ^
       "up [R723]; the relation fixes the push order, so this pair would " ^
       "need the lower value shifted)");
  call_ext st "?DCMOP";
  opc

type fmode =
  | Fmem of int     (* address of a 4-byte float cell *)
  | Fderef of int   (* address of a pointer cell holding that address *)
  | Fstack          (* the value sits on DR's float stack *)
  | Fbin of string  (* accumulator holds the result of a binary FLOAT op; the
                       string is the op letter (A/S/M/D), kept only to name the
                       evidence in refusals *)
  | Fconv           (* accumulator holds a ?QI15F conversion result *)
  | Fneg            (* accumulator holds a ?FN40M / ?FN40S negation result *)

(* ---------- [&] AND-conjunction [E2E-9 slice 6] ----------
   Inside a conjunction DR does NOT emit a per-operand skip jump.  Each
   operand is materialized as a boolean BYTE in A through the flag trick
   `SUI 01 / SBB A` (A := 0FF iff the relation holds, 00 otherwise), the
   operands are combined with `PUSH PSW ... POP B / ANA B` (0FF AND 0FF is
   0FF, so AND-ing on those values IS logical AND), and the WHOLE
   conjunction gets one skip jump, opcode JP (F2): A=0FF -> S=1 -> fall into
   the THEN; A=00 -> S=0 -> skip it.  Left-associative `&` nesting maps onto
   nested PUSH/POP pairs, so `a & b & c` lowers as
     a; PUSH PSW; b; POP B; ANA B; PUSH PSW; c; POP B; ANA B; JP skip
   [DECPOLY `if x=0 & y=0 & z=0`, R2021 fixed-bin `x=0 & y=0`].

   Only the two operand shapes those goldens pin are implemented: a FIXED
   DECIMAL equality (?DLDOP push pair + ?DCMOP) and a 2-byte FIXED BINARY
   compare against 0 (cell-OR test).  Other relations in a conjunction
   refuse [TBD]: DR's boolean-materialization ladder for >, <, >=, <=, ^=
   is unsampled. *)
let vk_name (vk : vkind) : string =
  match vk with
  | Vint -> "fixed-binary" | Vfix n -> "char(" ^ string_of_int n ^ ")"
  | Vvar n -> "varying(" ^ string_of_int n ^ ")"
  | Vdec (p, s) -> "dec(" ^ string_of_int p ^ "," ^ string_of_int s ^ ")"
  | Vflt -> "float" | Vbit1 -> "bit(1)"

(* ==================================================================
   [E2E-10 step 2] FLOAT BINARY(24): value model + operand-mode lowering.

   Representation (C100, every byte observed in golden/e2e13): 4 bytes,
       b0 = fraction bits 7..0,  b1 = 15..8,  b2 = sign<<7 | bits 22..16,
       b3 = characteristic (bias 129), value = (-1)^s (1+frac/2^23) 2^(b3-129)
   with an IMPLIED leading one (24 significant bits, which is what
   `float binary(24)` names), zero = all four bytes 0 (no negative zero
   [R3007]), literal rounding nearest with TIES AWAY FROM ZERO [R3020],
   magnitude range 2^-129 .. 2^127 exclusive of the top [R3019/R3024 vs
   R3015-R3017/R3025], and pool cells deduplicated by identical bytes,
   allocated in first-use order ahead of the variables (C101 -- the same
   rules the DEC pool follows).  tools/floatmodel.py is the INDEPENDENT
   oracle for this encoder: it reproduces 60/60 DR literal cells
   byte-exactly, and the e2e gate checks this OCaml path against the
   same cells.

   Operand modes (C102).  The suffix tells the runtime where the operands
   live; it comes from DR traces, not from the DEC analogue:
     mem,mem      LXI H,l / PUSH H / LXI H,r / POP D / CALL ?FX44M   [R3030]
     deref,deref  LHLD c1 / PUSH H / LHLD c2 / POP D / CALL ?FX44M   [R3038]
     stack,mem    LXI H,r / CALL ?FX44L                              [R3030]
     stack,deref  LHLD r  / CALL ?FX44L                              [R3038]
     mem,stack    LXI H,l / CALL ?FX44R                              [R3036/42]
     stack,stack  CALL ?FX44S                                        [R3034]
   where F is followed by A(plus), S(sub), M(mul) or D(iv) and X44 is the
   fixed 44 in those names.  ?FX44R exists because DR preserves operand
   ORDER when the left side is a plain cell and the right side is computed:
   `d1 = a - b * c` is FM44M over b,c then `LXI H,A / FS44R`, i.e. a minus
   the product, so L means (accumulator op cell) and R means (cell op
   accumulator).  DR is semantically CORRECT there, which is precisely why
   I probed instead of assuming from the DEC path [R3042].
   Every form leaves its result on DR's float stack; a store pops it with
   ?FX44S (a stack/cell transfer with HL = the cell), plain cell-to-cell
   copies use ?FX44M [R3001, R3037].  Unary minus is ?FN40M for a memory
   operand and ?FN40S for a stack operand [R3035, R3046].  A FIXED operand
   inside a float expression is evaluated to HL then converted with
   ?QI15F [R3036].  A float function exits through JMP ?FPRET, plus ?RSBLK
   when the activation is recursive [R3038 non-recursive vs FFACT
   recursive].  PUT of a float variable is MVI A,0E / ?QFCMS and of a stack
   value MVI A,0E / ?QFCSS -- the width byte is the CONSTANT 14, not a
   precision [R3030, R3037, FFACT].

   REFUSED on purpose, because no DR sample decides them: float comparison
   (the JP/JM/JZ pairing of `>` in R3037/R3045 implies `>=`, the same
   C083-style irregularity that needed a RUNTIME probe to settle for DEC),
   GET of a float (observed in R3004, unimplemented), float-to-fixed store
   (?FL40M / ?QFI15 appear only inside FFACT's prologue), storing to or
   bare-returning a float FORMAL, mixed cell/deref operand pairs, float
   binary(p) with p different from 24, whole-literal float expressions (DR
   evaluates those in the DEC runtime and converts with ?QX8F4 [R3044]),
   and literals outside the characterized range -- including the exact
   2^-129 magnitude, whose encoding collides with DR's zero cell.
   ================================================================== *)


(* --- expression lowering --------------------------------------------- *)

(* [E2E-10 step 3] an expression with no identifier anywhere in it.  DR does
   NOT evaluate a whole-literal FLOAT expression with the float runtime: R3044's
   `d1 = 1.5 + 2.5` compiles to the DEC runtime (?DLDOP of each literal's DEC
   pool cell, ?DADOP, then ?QDCOP/?QCXOP/?QX8F4 to convert the DEC result, then
   ?FX44S), and `d2 = 1.5 * 2` likewise uses ?DMUOP.  Emitting ?FA44M instead is
   not merely different bytes -- it computes through the 24-bit float runtime
   rather than DR's decimal one, so the value can differ too.  Until that path
   is implemented this refuses loudly instead of silently diverging. *)
let rec fl_all_literals (e : Ast.expr) =
  match (unwrap_e e).Ast.e with
  | Ast.Eident _ -> false
  | Ast.Ebinary (_, l, r) -> fl_all_literals l && fl_all_literals r
  | Ast.Eprefix (_, x) -> fl_all_literals x
  | Ast.Esuffix (hd, args) ->
      fl_all_literals hd && List.for_all fl_all_literals args
  | _ -> true

let fl_addr st (m : fmode) =
  match m with
  | Fmem a -> d st op_lxi_h; reloc st Data a
  | Fderef a -> d st op_lhld; reloc st Data a
  | (Fstack | Fconv | Fbin _ | Fneg) ->
      failwith "codegen: internal: computed float operand has no address"

let fl_proc_ret st (nm : string) =
  (* [E2E-11 step 4, FDTEST] an EXTERNAL ENTRY with RETURNS is a callable value
     source too: FDTEST's `put skip list(...,fdiv2(i,100))' is a float-valued
     PUT item whose type can only be resolved through bind's pl_exts, since an
     entry has no proc_layout.  Without this, is_float_expr said "not a float
     expression" and the item fell through to the generic refusal.  Only the
     FLOAT case is sampled by FDTEST; a DECIMAL-returning external entry keeps
     resolving to None and refuses, because DR has no such sample here. *)
  let li = String.lowercase_ascii nm in
  match List.assoc_opt li st.exts with
  | Some (_p, _e, ret, _pt) -> ret
  | None ->
      (match List.assoc_opt li st.procs with
       | Some pl -> pl.Bind.pl_ret
       | None -> None)

let rec is_float_expr st (e : Ast.expr) : bool =
  let e = unwrap_e e in
  match e.Ast.e with
  | Ast.Eident n -> vk_of st n.Ast.orig = Vflt
  | Ast.Ebinary (_, l, r) -> is_float_expr st l || is_float_expr st r
  | Ast.Eprefix (_, x) -> is_float_expr st x
  | Ast.Econd inner -> is_float_expr st inner
  | Ast.Esuffix (hd, args) when args <> [] ->
      (match hd.Ast.e with
       | Ast.Eident n ->
           (match fl_proc_ret st n.Ast.orig with
            | Some (Bind.RTfloat _) -> true
            | _ -> false)
       | _ -> false)
  | _ -> false

and fl_push st (e0 : Ast.expr) : fmode =
  let e = unwrap_e e0 in
  match e.Ast.e with
  | Ast.Ebinary (op, l, r) -> fl_bin st op l r
  | Ast.Enumber k ->
      (* an integer or decimal literal in a FLOAT context becomes a float
         pool cell: `d7 = a * 2` [R3036] and FFACT's `return (1)` *)
      let b =
        try mbf_encode k with Fl_range msg ->
          failwith ("codegen: float literal " ^ k ^ " " ^ msg)
      in
      Fmem (fl_pool st b)
  | Ast.Eident n ->
      let nm = String.lowercase_ascii n.Ast.orig in
      begin match vk_of st n.Ast.orig with
      | Vflt ->
          if List.mem nm st.deref then Fderef (addr_of st n.Ast.orig)
          else Fmem (addr_of st n.Ast.orig)
      | Vint ->
          (* fixed operand inside a float expression: evaluate to HL, then
             ?QI15F converts it into the accumulator [R3036].  The result is
             Fconv, NOT Fstack: DR's suffix choice separates a conversion from
             a binary-op result (`a + i` -> ?FA44R vs `a + (b+c)` -> ?FA44L
             [R3036, R3052]), and a negation may only be applied to a binary
             result [R3035, R3038, R3046], never to a conversion. *)
          lower_hl st e;
          call_ext st "?QI15F";
          Fconv
      | vk ->
          failwith
            (Printf.sprintf
               "codegen: mixing %s into a FLOAT expression is unsampled [TBD] (no DR sample mixes decimal or character values into one float expression; line %d)"
               (vk_name vk) e.Ast.epos.Source.line)
      end
  | Ast.Eprefix (Ast.Minus, x) -> (
      (* NEGATIVE LITERALS ARE FOLDED, not negated at run time: R3007/R3018/
         R3020 show DR's pool holding `00 00 c0 81` for -1.5 and `01 00 80 99`
         for -16777217, with NO ?FN40M anywhere in those statements.  A minus
         over a COMPUTED value is different and does use ?FN40M / ?FN40S
         [R3035, R3046].  A minus over a parenthesised literal has no sample,
         so it is refused rather than assumed to fold the same way. *)
      match (unwrap_e x).Ast.e with
      | Ast.Enumber k when (match x.Ast.e with Ast.Econd _ -> false
                                   | _ -> true) ->
          let b =
            try mbf_encode ("-" ^ k) with Fl_range msg ->
              failwith ("codegen: float literal -" ^ k ^ " " ^ msg)
          in
          Fmem (fl_pool st b)
      | Ast.Enumber _ ->
          failwith
            "codegen: FLOAT minus over a PARENTHESISED literal is unsampled [TBD] (R3007-R3020 fold a bare literal; `-(1.5)` has no sample)"
      | _ ->
          (match fl_push st x with
           | Fmem a ->
               (* ?FN40M negates the value ADDRESSED BY HL into the accumulator;
                  it does not write the cell.  R3046 reads `a` and `-a` in
                  consecutive statements, so an in-place negate would corrupt
                  the variable -- the DR evidence itself rules that reading out. *)
               d st op_lxi_h; reloc st Data a; call_ext st "?FN40M"; Fneg
           | Fderef a ->
               d st op_lhld; reloc st Data a; call_ext st "?FN40M"; Fneg
           | (Fstack | Fbin _) ->
               (* ?FN40S negates the accumulator in place [R3035 `d4 = -(a+b)`,
                  R3038 `(p+q) * -1`].  The result occupies the same slot as any
                  other negation, so it is Fneg, not Fstack: R3046 shows a
                  negation on either side of `*` taking L/R and two of them
                  taking S. *)
               call_ext st "?FN40S"; Fneg
           | Fconv ->
               failwith
                 "codegen: negating a ?QI15F conversion result inside a FLOAT operand is unsampled [TBD] (R3035/R3038 sample ?FN40S only on an arithmetic result; R3046 samples ?FN40S only after a second ?FN40M)"
           | Fneg ->
               failwith
                 "codegen: DOUBLE negation of a FLOAT value is unsampled [TBD] (no DR sample applies ?FN40S to a ?FN40M/?FN40S result; `-(-a)` and `--a` have no evidence, and a partial match here is how the R3046 operand-mode bug hid)"))
  | Ast.Eprefix (Ast.Plus, x) -> fl_push st x
  | Ast.Econd inner -> fl_push st inner
  | Ast.Eprefix (op, _) ->
      failwith
        (Printf.sprintf "codegen: FLOAT prefix operator %s is unsampled [TBD] (line %d)"
           (if op = Ast.NegL then "^" else "+/-") e.Ast.epos.Source.line)
  | Ast.Esuffix (hd, args) when args <> [] ->
      (* a float function leaves its result on the float stack; the call
         itself is the ordinary descriptor route [R3005, FFACT] *)
      (match hd.Ast.e with
       | Ast.Eident n ->
           (match fl_proc_ret st n.Ast.orig with
            | Some (Bind.RTfloat 24) -> ignore (args); lower_hl st e; Fstack
            | Some (Bind.RTfloat p) ->
                failwith
                  (Printf.sprintf
                     "codegen: FLOAT BINARY(%d) return precision is unsupported [TBD] (only BINARY(24) is characterized; R3013 proves the CELL is 4 bytes but not the computed precision)"
                     p)
            | _ ->
                failwith
                  (Printf.sprintf
                     "codegen: non-float call %s used as a FLOAT operand [TBD] (line %d)"
                     n.Ast.orig e.Ast.epos.Source.line))
       | _ -> failwith "codegen: indirect call target [TBD]")
  | _ ->
      failwith
        (Printf.sprintf
           "codegen: FLOAT expression shape %s is unsampled [TBD] (line %d)"
           (expr_kind_name e.Ast.e) e.Ast.epos.Source.line)

and fl_bin st (op : Ast.binop) (l : Ast.expr) (r : Ast.expr) : fmode =
  (* NOTE (a real byte-level bug I hit here): an UNPARENTHESISED `match` in a
     preceding arm body swallows every following `|` arm, because OCaml has no
     terminator for it.  fl_push's Eprefix arm is parenthesized for that
     reason.  Same family of trap as the DECPOLY `if`/then-branch absorption. *)  (if fl_all_literals l && fl_all_literals r then
     failwith
       "codegen: a FLOAT arithmetic expression made only of literals is unsampled [TBD] (DR evaluates it in the DEC runtime -- ?DLDOP per literal pool cell, ?DADOP/?DMUOP/?DSUOP, then ?QDCOP/?QCXOP/?QX8F4 to convert the decimal result and ?FX44S to store it [R3044]; emitting the float runtime instead would change both the bytes and the arithmetic)");
  let nm =
    match op with
    | Ast.Add -> "A"
    | Ast.Sub -> "S"
    | Ast.Mul -> "M"
    | Ast.Div -> "D"
    | _ ->
        failwith
          "codegen: FLOAT operand of an operator other than + - * / is unsampled [TBD] (no DR sample exponentiates, concatenates, or does bit/logical arithmetic on floats)"
  in
  (* EVALUATION ORDER: when the RIGHT operand is a CALL, DR runs the whole
     right side FIRST and only then materialises the left -- FFACT's
     `i * factorial(i - 1)` is descriptor, CALL, LHLD i, ?QI15F, ?FM44S.
     This is the same rule the FIXED path learned from RFACT/NFACT, and it is
     forced by the stack discipline: the value pushed first ends up deeper, so
     a left operand that needs code would otherwise sit BELOW the call result.
     When the right is not a call, left goes first [R3034 `a * b + c * a`]. *)
  let right_is_call =
    match (unwrap_e r).Ast.e with
    | Ast.Esuffix (hd, args) -> args <> [] &&
        (match hd.Ast.e with Ast.Eident _ -> true | _ -> false)
    | _ -> false
  in
  let (lk, rk) =
    if right_is_call then begin
      let rr = fl_push st r in
      let ll = fl_push st l in
      (ll, rr)
    end
    else begin
      let ll = fl_push st l in
      let rr = fl_push st r in
      (ll, rr)
    end
  in
  (* only these six combinations have a DR sample; the mixed cell/deref
     pairs and a deref left of a stack value do not, so they stay refused
     instead of borrowing the DEC pattern. *)
  (* classify once, then dispatch on the pair -- `as` bindings over
     or-patterns bind to the enclosing tuple, which would misname the
     operands, so no `as` is used here *)
  let cell m = match m with Fmem _ | Fderef _ -> true | _ -> false in
  (* Fneg belongs in this list: R3046 `d1 = -a * b` takes ?FM44L and `d2 = a * -b` takes ?FM44R, so a negation result is a computed accumulator operand, not a cell.  Leaving it out routed both to ?FM44S silently. *)
  let comp m = match m with Fstack | Fconv | Fbin _ | Fneg -> true | _ -> false in
  if cell lk && cell rk then begin
    (* WRITTEN order, M-form.  R3082 `2 * y`, R3083 `y * 2`, R3084 `y + 2`,
       R3086 `x * y` and R3012 `a / b` pin that a literal pool cell, a plain
       cell and a pointer-formal deref are all just address pushes: DR does NOT
       commute a `+`/`*` here (there is nothing to materialize), and mixing a
       cell with a formal is an ordinary M-form, which is exactly what
       FLTPOLY's `return (x * x + 2 * y + z)` needs.  The earlier assessment
       that R3005's mixed pair was an unknown exotic shape was wrong -- it was
       never a mixed pair. *)
    fl_addr st lk; d st op_push_h; fl_addr st rk; d st op_pop_d;
    call_ext st ("?F" ^ nm ^ "44M");
    Fbin nm
  end else if comp lk && cell rk then begin
    (* accumulator/pushed value LEFT, ADDRESS-MODE right.  A plain cell and a
       pointer formal are interchangeable here: R3087 `(x*x + 2*y) + z` and
       R3089 `z + x*y` take ?FA44L exactly as the cell forms R3034/R3051 do, and
       R3090 `z / (x + y)` takes ?FD44R exactly as R3042/R3043 do.  Only the load
       instruction differs (LXI H vs LHLD), which is fl_addr's job [C103]. *)
    (* accumulator/pushed value LEFT, named cell right [R3034 `a*b + c`,
       R3035 `-a + b`, R3036 `i + a` / `i * a` / `i / a`, R3042 `a/b * c`,
       R3043 `(a-b)/c`] *)
    fl_addr st rk; call_ext st ("?F" ^ nm ^ "44L"); Fbin nm
  end else if cell lk && comp rk then begin
    (* L is available only when the operator commutes AND the right value is an
       arithmetic result, i.e. when DR may read the expression with the operands
       exchanged at no cost [R3034, R3051, R3052].  A ?QI15F conversion result
       is NOT that: DR takes R there [R3036 `a + i`, `a * i`, `a / i`], as it
       must for the non-commutative `-` and `/` [R3042, R3043, R3053]. *)
    (* R3046 pins the three computed kinds apart: `-a * b` -> ?FM44L,
       `a * -b` -> ?FM44R, `-(a) * -(b)` -> ?FM44S.  So DR exchanges the
       operands of a commutative op ONLY when the right side is itself a
       binary-op result [R3034 `a + b*c` -> ?FA44L, R3051 `a*(b+c)` -> ?FM44L,
       R3052 `a + (b+c)` -> ?FA44L]; around a negation [R3035 `a + -b` ->
       ?FA44R, R3046 `a * -b` -> ?FM44R] or a conversion [R3036 `a + i` ->
       ?FA44R, `a * i` -> ?FM44R] it keeps the written order, and for the
       non-commutative `-` and `/` it must [R3042, R3043, R3053]. *)
    let use_l =
      match op with
      | Ast.Add | Ast.Mul -> (match rk with Fbin _ -> true | _ -> false)
      | _ -> false
    in
    fl_addr st lk;
    call_ext st ("?F" ^ nm ^ (if use_l then "44L" else "44R"));
    Fbin nm
  end else
    (* both operands computed [R3034 `(a+b)*(a-b)`, R3044 `i + j`] *)
    (call_ext st ("?F" ^ nm ^ "44S"); Fbin nm)

(* store a float value into a variable's cell *)
let fl_store_var st ?(dst_ptr = false) (addr : int) (m : fmode) =
  match m with
  | Fmem a ->
      (* [E2E-11 step 3d, E26K] when the DESTINATION is a pointer formal, DR
         loads the formal cell instead of taking its address -- the destination
         opcode is the ONLY change, `LXI H,*S(0008) / PUSH H / LHLD Q A(001A) /
         POP D / CALL ?FX44M`: ?FX44M copies 4 bytes from (HL) to (DE), and DE
         already holds the callee-visible address. *)
      d st op_lxi_h; reloc st Data a; d st op_push_h;
      d st (if dst_ptr then op_lhld else op_lxi_h); reloc st Data addr;
      d st op_pop_d;
      call_ext st "?FX44M"
  | (Fstack | Fconv | Fbin _ | Fneg) ->
      (* every computed float kind is popped off the accumulator into the cell
         with ?FX44S [R3030-R3034, and R3035's `d1 = -a` which negates into the
         accumulator with ?FN40M and then stores with ?FX44S] *)
      if dst_ptr then
        failwith
          "codegen: [TBD] FLOAT pointer-formal destination with a COMPUTED source \
           is unsampled (E26K pins only the cell-to-cell ?FX44M route; the ?FX44S \
           pop-into-cell route has no pointer sample)";
      d st op_lxi_h; reloc st Data addr; call_ext st "?FX44S"
  | Fderef a ->
      (* [R3079] `w = x` where x is a float FORMAL: dereference the formal's
         pointer cell to get its address, then the ordinary cell-to-cell copy.
         Same ladder the arithmetic uses; DR keeps ?FX44M either way. *)
      d st op_lhld; reloc st Data a; d st op_push_h;
      (* [E26K gf2] `u = v' where BOTH are pointer formals: DR derefs the source
         AND loads the destination through its cell --
             LXI D,U A(001C) ; MVI C,04 ; ... ; LHLD V A(001E) ; PUSH H
             LHLD U A(001C)  ; POP D    ; CALL ?FX44M
         so dst_ptr must be honoured here too; the earlier version kept the
         LXI H and differed from DR in exactly one opcode byte. *)
      d st (if dst_ptr then op_lhld else op_lxi_h); reloc st Data addr;
      d st op_pop_d;
      call_ext st "?FX44M"

(* prepare a float value for RETURN: it must end on the float stack.
   A cell is LOADED with ?FL40M -- FFACT's `return (1)` is exactly
   `LXI H,*S(000C); CALL ?FL40M; CALL ?RSBLK; JMP ?FPRET`.  ?FX44S is the
   STORE direction and must not be used here. *)
let fl_return_push st (m : fmode) =
  match m with
  | Fmem a -> d st op_lxi_h; reloc st Data a; call_ext st "?FL40M"
  | (Fstack | Fbin _) -> ()
  | (Fconv | Fneg) ->
      failwith
        "codegen: RETURN of a converted or negated FLOAT value is unsampled [TBD] (FFACT returns a literal via ?FL40M and a product via the stack; R3038 returns a product -- none of them returns a bare ?QI15F or ?FN40 result)"
  | Fderef _ ->
      failwith
        "codegen: RETURN of a bare FLOAT formal is unsampled [TBD] (R3038 returns an expression, FFACT a literal and a product)"

(* [E2E-10 step 3] FLOAT relation lowering.  DR compares two float cells by
   pushing their ADDRESSES (right-first or left-first per relation, exactly the
   polarity the DEC table uses), calling ?FC44M, and then testing a flag.  ?FC44M
   leaves A as a SIGNED COMPARISON CODE of (pushed operand) - (named operand):
   A < 0 when pushed < named, A = 0 when equal, A > 0 when pushed > named.  That
   reading is what makes the observed opcode table coherent:

   | relation | pushed first | skip jump | sample |
   |---|---|---|---|
   | `a > b`  | b | JP | R3070, R3077, R3004 |
   | `a < b`  | a | JP | R3071 |
   | `a >= b` | a | JM | R3072 |
   | `a <= b` | b | JM | R3073 |
   | `a = b`  | a | JNZ | R3074, R3076, R3004, FLTPOLY |
   | `a <> b` | -- | -- | R3075: DR ITSELF rejects this, `1 ERROR(S) IN PASS 2` |

   Same table as `dec_cmp_rel`, which is why one opcode pair covers both numeric
   models -- but `<>` is accepted for DEC and REJECTED by the compiler for FLOAT
   [R3075], so the float table has a hole that is DR's, not mine.  A literal
   operand is addressed as its float POOL cell [R3076 `= 0` uses *S(0000),
   deduplicated with other zero cells per C101]. *)
(* save_psw=true reproduces DR's CONJUNCTION form, where the first address
   load is hoisted above `PUSH PSW` so the previous operand's boolean byte
   survives [FLTPOLY, and the identical DECPOLY/R2026 DEC hoist].  It is only
   legal for plain cells: a pointer-formal deref in that position has no
   sample, so the mixed/refused cases stay loud. *)
let fl_cmp_rel ?(save_psw = false) st (rop : Ast.relop)
               (a : Ast.expr) (b : Ast.expr) =
  let (right_first, opc) =
    match rop with
    | Ast.Gt -> (true, op_jp)
    | Ast.Lt -> (false, op_jp)
    | Ast.Ge -> (false, op_jm)
    | Ast.Le -> (true, op_jm)
    | Ast.Eq -> (false, op_jnz)
    | Ast.Ne ->
        failwith
          "codegen: FLOAT `<>` is not accepted by DR itself [TBD] (R3075: `if a <> b` on two float variables compiles clean in PASS 1 and fails `1 ERROR(S) IN PASS 2`, so no `.REL` exists to reproduce; DEC `<>` works via JZ [C085] but the float reader does not offer it)"
    (* Ast.relop has exactly these six constructors, so no catch-all is needed
       -- adding one draws Warning 11 and the baseline warning count is a
       regression gate of its own. *)
  in
  (* operands must be ADDRESSABLE: only cells (variable or pool literal) and
     pointer-formal derefs have a DR sample [R3070-R3077, R3079, FLTPOLY].  A
     computed value on the float stack has none, so refuse BEFORE emitting,
     not after half a statement is out. *)
  let addr_mode (e : Ast.expr) : fmode =
    let e = unwrap_e e in
    match e.Ast.e with
    | Ast.Enumber k ->
        (match mbf_encode k with
         | b -> Fmem (fl_pool st b)
         | exception Fl_range msg ->
             failwith ("codegen: float literal " ^ k ^ " in a comparison " ^ msg))
    | Ast.Eident n ->
        let nm = String.lowercase_ascii n.Ast.orig in
        (match vk_of st n.Ast.orig with
         | Vflt ->
             if List.mem nm st.deref then Fderef (addr_of st n.Ast.orig)
             else Fmem (addr_of st n.Ast.orig)
         | _ ->
             failwith
               "codegen: mixing a non-FLOAT operand into a FLOAT comparison is unsampled [TBD] (no DR sample compares a float against a fixed or decimal value without going through the float pool cell form [R3076 pins the INTEGER LITERAL case, which becomes a float cell])")
    | _ ->
        fl_push st e |> function
        | Fmem _ | Fderef _ as m -> m
        | _ ->
            failwith
              "codegen: computed FLOAT operand in a comparison is unsampled [TBD] (every DR float compare sample addresses two cells or two formal derefs [R3070-R3077, R3079, FLTPOLY]; a comparison against an accumulator value has none -- so nothing is emitted before this refusal)"
  in
  let ma = addr_mode a in
  let mb = addr_mode b in
  if (match ma with Fderef _ -> true | _ -> false)
     <> (match mb with Fderef _ -> true | _ -> false) then
    failwith
      "codegen: FLOAT comparison mixing a plain cell with a pointer formal is unsampled [TBD] (R3070-R3077/R3076 pin cell+cell and cell+pool-cell, R3079 pins formal+formal; the mixed pair has no DR sample -- same boundary the arithmetic lowering keeps)";
  (if right_first then (mb, ma) else (ma, mb))
  |> fun (first, second) ->
  if save_psw then begin
    (match first, second with
     | (Fmem _ | Fconv), (Fmem _ | Fconv) -> ()
     | _ ->
         failwith
           "codegen: FLOAT pointer formal or computed operand in a conjunction is unsampled [TBD] (FLTPOLY pins only the plain-cell `=` form with the PUSH PSW hoist)");
    (* the hoist loads the FIRST operand's address, then saves the previous
       boolean byte, then continues the normal push pair *)
    (if right_first then fl_addr st mb else fl_addr st ma);
    d st op_push_psw; d st op_push_h;
    (if right_first then fl_addr st ma else fl_addr st mb);
    d st op_pop_d
  end
  else begin
    fl_addr st first; d st op_push_h; fl_addr st second; d st op_pop_d
  end;
  call_ext st "?FC44M";
  opc

let op_sui = 0xd6
let op_pop_b = 0xc1
let op_ana_b = 0xa0

(* a 2-byte fixed-bin `var = 0` operand, or None *)
let conj_bin_zero st (e : Ast.expr) =
  match (unwrap_e e).Ast.e with
  | Ast.Ebinary (Ast.EqR Ast.Eq, a, { Ast.e = Ast.Enumber "0"; _ })
    when (match (unwrap_e a).Ast.e with
          | Ast.Eident _ -> not (is_dec_operand st a)
          | _ -> false) ->
      (match (unwrap_e a).Ast.e with Ast.Eident v -> Some v | _ -> None)
  | _ -> None

let bin_zero_tail st =
  d st op_mov_a_m; d st op_inx_h; d st op_ora_m;
  d st op_sui; d st 0x01; d st op_sbb_a

(* FIXED DECIMAL equality lowered as a boolean operand, SPLIT into the two
   pieces a conjunction needs.  [R2026/DECPOLY] DR hoists the leading
   `LXI H,<cell>` above the PUSH PSW exactly as it does for a fixed-bin
   operand (PUSH/POP leave HL alone), then emits `MVI A,p / ?DLDOP`, the
   right-hand push, `?DCMOP` and the flag trick.  Only a DEC VARIABLE on the
   left, both sides at the same scale, is pinned; anything else refuses
   rather than guessing an unsampled split. *)
let dec_eq_bool_parts st (a : Ast.expr) (b : Ast.expr) =
  let (pa, pb) = dec_cmp_pt st a b in
  let (ple, sle, lita) = pa in
  let (_plb, slb, _) = pb in
  if sle <> slb then
    failwith
      ("codegen: DEC conjunction scale alignment unproven [TBD] (only " ^
       "equal-scale operand pairs are pinned as boolean operands)");
  match (unwrap_e a).Ast.e, lita with
  | Ast.Eident v, None ->
      if List.mem (String.lowercase_ascii v.Ast.orig) st.deref then
        failwith
          ("codegen: FIXED DECIMAL formal as a conjunction operand is " ^
           "unproven [TBD] (the LXI-H hoist above PUSH PSW is pinned only " ^
           "for automatic decimal cells [DECPOLY, R2026]; a formal's LHLD " ^
           "hoist has no DR sample)");
      let addr = addr_of st v.Ast.orig in
      let pre () = d st op_lxi_h; reloc st Data addr in
      let post () =
        d st op_mvi_a; d st ple; call_ext st "?DLDOP";
        dec_cmp_push st b pb;
        call_ext st "?DCMOP";
        d st op_sui; d st 0x01; d st op_sbb_a
      in
      Some (pre, post)
  | _ -> None

let rec lower_bool st (c : Ast.expr) =
  let c = unwrap_e c in
  match c.Ast.e with
  | Ast.Ebinary (Ast.And, l, r) ->
      lower_bool st l;
      (* [E2E-10 step 3] FLOAT `=` on the RIGHT of a conjunction has to be
         tested BEFORE conj_bin_zero: that helper claims any `ident = 0` whose
         operand is not DEC, which floats are, and would silently emit the
         2-byte fixed-bin boolean form (this is what made FLTPOLY's second and
         third conjunction operands differ from DR).  FLTPOLY pins the float
         form: the first address load is HOISTED above PUSH PSW exactly as
         DECPOLY's DEC form does, then PUSH H / LXI H,*S(zero) / POP D /
         ?FC44M / SUI 01 / SBB A materializes the boolean byte (?FC44M leaves
         A = 0 when EQUAL, which is the `=` case).  R3078 pins `>` only as the
         FIRST operand, where DR uses ?FC44M's raw signed-comparison byte as the
         boolean and emits nothing more; a `>` on the right has no sample, so it
         refuses. *)
      let saved =
        match (unwrap_e r).Ast.e with
        | Ast.Ebinary (Ast.EqR rop, a, b)
          when (match rop with Ast.Eq | Ast.Gt -> true | _ -> false)
               && (is_float_expr st a || is_float_expr st b) ->
            (match rop with
             | Ast.Eq ->
                 ignore (fl_cmp_rel ~save_psw:true st Ast.Eq a b);
                 d st op_sui; d st 0x01; d st op_sbb_a
             | _ ->
                 failwith
                   "codegen: FLOAT relation other than `=` as the RIGHT operand of a conjunction is unsampled [TBD]")
        | _ ->
        match conj_bin_zero st r with
        | Some v ->
            (* [R2025] fixed-bin operand: address load hoisted above PUSH *)
            d st op_lxi_h; reloc st Data (addr_of st v.Ast.orig);
            d st op_push_psw; bin_zero_tail st
        | None ->
            (match (unwrap_e r).Ast.e with
             | Ast.Ebinary (Ast.EqR Ast.Eq, a, b)
               when is_dec_operand st a || is_dec_operand st b ->
                 (match dec_eq_bool_parts st a b with
                  | Some (pre, post) ->
                      (* [DECPOLY/R2026] DEC operand: same hoist *)
                      pre (); d st op_push_psw; post ()
                  | None ->
                      d st op_push_psw; lower_bool st r)
             | _ -> d st op_push_psw; lower_bool st r)
      in
      ignore saved;
      d st op_pop_b; d st op_ana_b; st.last_imm <- None
  | Ast.Ebinary (Ast.EqR rop, a, b)
    when (match rop with Ast.Eq | Ast.Gt -> true | _ -> false)
         && (is_float_expr st a || is_float_expr st b) ->
      (* first operand of a FLOAT conjunction operand [FLTPOLY `=`, R3078 `>`] *)
      (match rop with
       | Ast.Eq ->
           ignore (fl_cmp_rel st Ast.Eq a b);
           d st op_sui; d st 0x01; d st op_sbb_a
       | _ -> ignore (fl_cmp_rel st rop a b))
  | Ast.Ebinary (Ast.EqR Ast.Eq, a, b) when is_dec_operand st a
                                            || is_dec_operand st b ->
      (* first operand of a conjunction: pre and post run consecutively,
         which is exactly DR's single-condition push pair + flag trick *)
      (match dec_eq_bool_parts st a b with
       | Some (pre, post) -> pre (); post ()
       | None ->
           ignore (dec_cmp_rel st Ast.Eq a b);
           d st op_sui; d st 0x01; d st op_sbb_a)  | Ast.Ebinary (Ast.EqR Ast.Eq, { Ast.e = Ast.Eident v; _ },
                 { Ast.e = Ast.Enumber "0"; _ }) ->
      d st op_lxi_h; reloc st Data (addr_of st v.Ast.orig); bin_zero_tail st
  | _ ->
      failwith
        ("codegen: conjunction operand not in the proven subset [TBD] (only " ^
         "a FIXED DECIMAL `= 0` and a 2-byte FIXED BINARY `= 0` are pinned " ^
         "as boolean-materializing operands [DECPOLY, R2025]; other " ^
         "relations have no DR sample)")

(* [E2E-11 step 1a] DR's 8080 CONSTANT-BIAS LADDER, measured over three
   separate contexts rather than guessed from one.  To add a signed value B to
   HL, DR repeats the 1-byte pointer instruction while it is cheap and switches
   to `LXI B,two's-complement(B) / DAD B' (4 bytes) from |B| = 4 up, with no
   upper bound observed:
        v = v + 1/2/3   -> LHLD v ; (INX H)*k           ; SHLD v   [E22A02,A03]
        v = v + 4..200  -> LHLD v ; LXI B,k ; DAD B     ; SHLD v   [E22A04..A16,A200]
        v = v - 1/2/3   -> LHLD v ; (DCX H)*k           ; SHLD v   [E22B01..B03]
        v = v - 4/5/8   -> LHLD v ; LXI B,FFFC/FFFB/FFF8 ; DAD B   [E22B04..B08]
        if v > k        bias k+1:  DCX repeat of (k+1) for k<=2, LXI B otherwise  [E23G1..G8,G200]
        if v < k        bias k  :  DCX repeat of k    for k<=3, LXI B otherwise  [E23L1..L8,L200]
        if v ^= k       bias k  :  DCX repeat of k    for k<=3, LXI B otherwise  [E23N1..N8,N200]
   One cost model explains all of them, which is why it replaces the three
   hand-capped arms below (they refused or mis-lowered at k >= 4).  |B| = 4 is a
   TIE by byte count and DR takes the LXI B side, so the threshold is inclusive
   on the repeat side at 3 only. *)
let hl_bias st (b : int) =
  let ab = abs b in
  if ab = 0 then ()
  else if ab <= 3 then
    for _ = 1 to ab do d st (if b > 0 then op_inx_h else op_dcx_h) done
  else begin
    let w = b land 0xffff in
    d st op_lxi_b; d st (w land 0xff); d st ((w lsr 8) land 0xff); d st op_dad_b
  end

(* [E2E-11 step 3b, C128] a POINTER formal on the left of a constant compare:
   DR loads the pointer, derefs it into HL, and then runs the ORDINARY bias
   ladder -- E26G `if x > 4`:
       LHLD X ; MOV E,M ; INX H ; MOV D,M ; XCHG
       LXI B,FFFB ; DAD B ; MOV A,H ; ORA A ; JM skip
   so only the 4-byte deref is added; the ladder itself is unchanged. *)
let cmp_load_deref st (nm : string) =
  d st op_lhld; reloc st Data (addr_of st nm);
  if List.mem (String.lowercase_ascii nm) st.deref then
    (d st 0x5e; d st 0x23; d st 0x56; d st op_xchg)

(* [E2E-11 step 3b, C128] the two-operand fixed compare, with POINTER-formal
   support.  Without a deref it is DR's ordinary pair-up:
       LHLD first ; XCHG ; LHLD second ; CALL ?IS22N ; <skip byte>
   When the SECOND operand is a pointer formal the deref ladder ends in its own
   XCHG, which would clobber the pushed value in DE, so DR is forced onto the
   stack form -- E26F `if i < x' and E26G `if x > i' both emit
       LHLD I ; PUSH H ; LHLD X ; MOV E,M ; INX H ; MOV D,M ; XCHG
       POP D ; CALL ?IS22N ; JP skip
   and note DR orders PLAIN-first / POINTER-second in BOTH relations, which my
   arms already do (Lt/Ge take l first, Gt/Le take rr first).  A deref on the
   FIRST side, or on both sides, has no DR sample and refuses: emitting the
   XCHG form there would be a guess, and the addresses would still line up. *)
let cmp_pair st first second skip =
  let fd = List.mem (String.lowercase_ascii first) st.deref in
  let sd = List.mem (String.lowercase_ascii second) st.deref in
  if fd then
    failwith
      ("codegen: [TBD] pointer formal as the FIRST operand of a two-variable \
        compare is unsampled (DR always loads the plain operand first [E26F, \
        E26G]; both-deref has no sample at all)")
  else if sd then begin
    d st op_lhld; reloc st Data (addr_of st first);
    d st op_push_h;
    cmp_load_deref st second;
    d st op_pop_d;
    call_ext st "?IS22N";
    d st skip
  end else begin
    d st op_lhld; reloc st Data (addr_of st first);
    d st op_xchg;
    d st op_lhld; reloc st Data (addr_of st second);
    call_ext st "?IS22N";
    d st skip
  end

let lower_test_skip0 st (c : Ast.expr) =
  (* [E2E-10] every shape handled below is FIXED or DECIMAL.  A FLOAT
     operand must refuse here: reading `2.5` as an integer constant crashed
     (R3045), and a float variable pair silently took the FIXED compare
     ladder and produced wrong bytes (R3037).  DR's float compare is
     ?FC44M plus JP/JM/JZ [R3037, R3045], and its `>` pairing implies `>=`,
     so it needs a runtime discriminator before it can be implemented. *)
  (* [E2E-10 step 3] FLOAT relations ARE handled now, but only through the
     arm below, which is placed FIRST on purpose: `if a > b` on floats would
     otherwise be captured by the FIXED `EqR Gt, Eident, Enumber` ladder below
     and produce wrong bytes (that is exactly what R3037 did), and `if a > 2.5`
     would make parse_int_const read "2.5" and crash (R3045).  Any other FLOAT
     condition falls through to the catch-all refusal, so nothing is emitted
     for a shape DR has not shown. *)
  match c.Ast.e with
  (* [E2E-11 step 2, T4 + FLTPOLY2] a BARE bit variable as a condition is NOT the
     zero test: DR loads the cell and doubles it into itself, then takes the
     jump-if-POSITIVE branch, i.e. it tests bit 7 through the sign flag.
        if f then ..     LDA f ; ORA A ; JP skip
     Placed first so a bit condition can never be captured by the fixed/decimal
     ident-zero ladder further down.  `JP' (0xF2), not `JNZ': after ORA A the
     zero flag says nothing about bit 7 of an arbitrary byte, and DR's own bytes
     at code 0x79 in FLTPOLY2 are f2. *)
  | Ast.Eident v when vk_of st v.Ast.orig = Vbit1 ->
      d st 0x3a (* LDA dir *); reloc st Data (addr_of st v.Ast.orig);
      d st op_ora_a;
      d st op_jp;
      let slot = st.lc in d st 0; d st 0; slot
  (* [E2E-11 step 1a] BIT(1) equality against a bit literal, matched BEFORE the
     fixed/decimal ladders on purpose: a bit cell is 1 byte, and the generic
     1-byte-zero test below would read it with LHLD (two bytes) -- a cell-length
     error that could produce self-consistent but wrong bytes.  DR, from E11D /
     E20B / E20D / E20E:
        if f = '0'b ..   LDA f ; ANI 80 ; JNZ skip
        if f = '1'b ..   LDA f ; ANI 80 ; SUI 80 ; JNZ skip
     The extra SUI 80 appears ONLY on the '1'b side, the same normalizing trick
     as the fixed-bin zero test: after ANI 80 the cell is 0x80 or 0x00, so
     SUI 80 leaves zero exactly when it matched '1'b.  Other relations, the
     reversed operand order, and bit-vs-bit comparison are unsampled: they fall
     through to the catch-all refusal. *)
  | Ast.Ebinary (Ast.EqR Ast.Eq, { Ast.e = Ast.Eident v; _ },
                 { Ast.e = Ast.Ebit b; _ })
    when vk_of st v.Ast.orig = Vbit1 ->
      let want1 =
        match b with
        | "1" -> true | "0" -> false
        | _ -> failwith "codegen: BIT(1) compared against a wide bit literal [TBD]"
      in
      d st 0x3a (* LDA dir *); reloc st Data (addr_of st v.Ast.orig);
      d st 0xe6 (* ANI *); d st 0x80;
      if want1 then (d st 0xd6 (* SUI *); d st 0x80);
      d st op_jnz; let slot = st.lc in d st 0; d st 0; slot
  (* [E2E-10 step 3] FLOAT relations, restored here after an edit that
     accidentally REPLACED this arm instead of inserting above it -- which is
     why R3045/R3077/R3098 began dying in int_of_string on "2.5": with this arm
     gone, `if a > 2.5' on floats fell through to the FIXED `> const' ladder
     below.  Placed first on purpose: a float relation must never be captured by
     the FIXED EqR Gt/Eident/Enumber ladder (R3037) or by parse_int_const
     (R3045), and any other FLOAT condition falls through to the catch-all. *)
  | Ast.Ebinary (Ast.EqR rop, a, b)
    when is_float_expr st a || is_float_expr st b ->
      let opc = fl_cmp_rel st rop a b in
      d st opc;
      let slot = st.lc in d st 0; d st 0; slot
  (* a conjunction lowers as ONE boolean expression + ONE skip jump *)
  | Ast.Ebinary (Ast.And, _, _) ->
      lower_bool st c;
      d st op_jp;
      let slot = st.lc in d st 0; d st 0; slot

  (* ---- [E2E-7A slice 1] FIXED DECIMAL comparison --------------------
     ?DCMOP takes NO relation argument: it pops two decimals and leaves a
     three-way result in the 8080 flags, so DR encodes the relation in the
     PUSH ORDER and the choice of skip jump.  Derived from 9 byte-level
     samples [R601-R607, R507, LOAN1 x2] and confirmed by running all of
     them under DR [golden/e2e7run], where every branch outcome matched:

        flags after ?DCMOP:  CY = (top <= bottom)   Z = (top = bottom)
                             S  = (top >  bottom)   (top = 2nd operand PUSHED)
        A >  B  push B,A  JP(F2)      A <  B  push A,B  JP(F2)
        A >= B  push A,B  JM(FA)      A <= B  push B,A  JM(FA)
        A =  B  push A,B  JNZ(C2)     A ^= B  push A,B  "JZ"(CA)

     "JZ" is DR's mnemonic for opcode CA = JPE -- the same skew already
     banked for integer ^= [C072], so one opcode table covers both
     families.  The jump is a SKIP jump (taken iff the condition is
     FALSE) whose operand is backpatched by the ordinary continuation
     triple, exactly like the integer arms: [R507] JP -> 004F = the
     CALL ?STOPX, [R608] JP -> 0057 = the first address after the loop,
     [LOAN1] JP -> 01E4 (inner-while exit) and JP -> 01A8 (past the
     then-assignment). *)
  | Ast.Ebinary (Ast.EqR rop, a, b) when is_dec_operand st a
                                          || is_dec_operand st b ->
      let opc = dec_cmp_rel st rop a b in
      d st opc;
      let slot = st.lc in d st 0; d st 0; slot
  | Ast.Ebinary (Ast.EqR Ast.Eq, { Ast.e = Ast.Eident v; _ },
                 { Ast.e = Ast.Enumber "0"; _ }) ->
      d st op_lxi_h; reloc st Data (addr_of st v.Ast.orig);
      d st op_mov_a_m; d st op_inx_h; d st op_ora_m;
      d st op_jnz; let slot = st.lc in d st 0; d st 0; slot
  | Ast.Ebinary (Ast.EqR Ast.Gt, { Ast.e = Ast.Eident v; _ },
                 { Ast.e = Ast.Enumber k; _ }) ->
      (* [E23G1..G8, G200] DR biases by k+1 and tests the high byte: the
         bias goes through the shared ladder, so `> 1'/`> 2' use DCX repeats
         and `> 3' upward use LXI B/DAD B.  `> 0' is unprobed (it would be a
         bare DCX), so it still refuses. *)
      let kk = parse_int_const k in
      if kk = 0 && List.mem (String.lowercase_ascii v.Ast.orig) st.deref then
        (* [E25B, C128] `x > 0' through a POINTER formal does not use the bias
           ladder at all (there is nothing to bias by): DR subtracts the
           pointed-to 2-byte value from A=0 in memory and jumps on the sign --
               LHLD X ; XRA A ; CMP M ; INX H ; SBB M ; JP skip
           which is why the plain-variable `> 0' case stays refused: the memory
           form only exists because HL already holds an address. *)
        begin
          d st op_lhld; reloc st Data (addr_of st v.Ast.orig);
          d st 0xaf; d st 0xbe; d st 0x23; d st 0x9e;
          d st op_jp; let slot = st.lc in d st 0; d st 0; slot
        end
      else if kk < 1 then failwith "codegen: compare > k<=0 form unproven [TBD]"
      else begin
        cmp_load_deref st v.Ast.orig;
        hl_bias st (-(kk + 1));
        d st op_mov_a_h; d st op_ora_a;
        d st op_jm; let slot = st.lc in d st 0; d st 0; slot
      end
  | Ast.Ebinary (Ast.EqR Ast.Ne, { Ast.e = Ast.Eident v; _ },
                 { Ast.e = Ast.Enumber k; _ }) ->
      (* [Y303/Y306 + E23N1..N8, N200] i ^= kk -> LHLD; <bias ladder for -kk>;
         MOV A,H; ORA L; skip-when-equal = CA (the ^= skip byte quirk [C072]).
         The old hand-written DCX-repeat form with a cap of 8 was WRONG from
         kk=4 up -- DR switches to LXI B/DAD B there -- and the cap turned a
         correct refusal into a silently wrong byte stream at 4..8 is not a
         concern (it refused), but 1..3 now share the ladder and >=4 is exact. *)
      let kk = parse_int_const k in
      if kk < 1 then failwith "codegen: ^= 0 / negative const form unproven [TBD]";
      cmp_load_deref st v.Ast.orig;
      hl_bias st (-kk);
      d st op_mov_a_h; d st 0xb5;      (* ORA L *)
      d st 0xca;
      let slot = st.lc in d st 0; d st 0; slot
  | Ast.Ebinary (Ast.EqR Ast.Lt, { Ast.e = Ast.Eident v; _ },
                 { Ast.e = Ast.Enumber k; _ }) ->
      (* [Z401/Z405 + E23L1..L8, L200] i < kk: LHLD; <bias ladder for -kk>;
         MOV A,H; ORA A; JP(F2) -> skip.  NOTE ORA A here vs ORA L in the ^=
         form.  The cap of 8 was a hedge at the same switch point the ladder
         now explains: kk <= 3 repeats DCX H, kk >= 4 takes LXI B/DAD B. *)
      let kk = parse_int_const k in
      if kk < 1 then failwith "codegen: < 0 / negative const form unproven [TBD]";
      cmp_load_deref st v.Ast.orig;
      hl_bias st (-kk);
      d st op_mov_a_h; d st op_ora_a;
      d st op_jp;
      let slot = st.lc in d st 0; d st 0; slot
  | Ast.Ebinary (Ast.EqR r, l, rr) when is_ident l && is_ident rr ->
      let ident = fun x ->
        match x.Ast.e with Ast.Eident n -> n.Ast.orig | _ -> assert false
      in
      (match r with
       | Ast.Lt | Ast.Ge ->
           cmp_pair st (ident l) (ident rr) (if r = Ast.Lt then op_jp else op_jm)
       | Ast.Gt | Ast.Le ->
           cmp_pair st (ident rr) (ident l) (if r = Ast.Gt then op_jp else op_jm)
       | Ast.Eq | Ast.Ne ->
           d st op_lhld; reloc st Data (addr_of st (ident l));
           d st op_push_h;
           d st op_lhld; reloc st Data (addr_of st (ident rr));
           d st op_pop_d;
           call_ext st "?IS22N";
           d st op_mov_a_h; d st 0xb5;  (* ORA L *)
           d st (if r = Ast.Eq then op_jnz else 0xca));  (* DR: ^= skip = JPE, not JZ: parity-defect [C072] *)
      let slot = st.lc in d st 0; d st 0; slot
  (* [E2E-7A slice 4] `if mod(x,y) = 0' and `^= 0' -- LOAN1's year-boundary
     test.  Zero new routines: the remainder already lands in HL from the
     existing ?IMDOP lowering, and DR's test is the plain HL-zero form
     (MOV A,H; ORA L) followed by JNZ for `= 0' [R908/R911/R912, LOAN1 00DC]
     and, for `^= 0', DR's usual `^=' skip byte CA -- $C PRINTS it as `JZ' at
     001C but the .REL byte is 0xca [R910], which extends the C072 parity-defect
     family (integer var-literal ^=, DEC ^=) to a third context.  Other
     relations against a mod (`> k', `mod = mod', non-zero right side) are
     unsampled: the relation is narrowed to Eq/Ne below so they keep refusing
     (a bare HL-zero test CANNOT express `> 0', it would silently mis-lower). *)
  | Ast.Ebinary
      ( Ast.EqR ((Ast.Eq | Ast.Ne) as r),
        ({ Ast.e = Ast.Ebuilt ("MOD", [ _; _ ]); _ } as xmod),
        { Ast.e = Ast.Enumber "0"; _ } ) ->
      lower_hl st xmod;
      d st op_mov_a_h; d st 0xb5; (* ORA L *)
      d st (if r = Ast.Eq then 0xc2 else 0xca);  (* DR's ^= skip byte is CA everywhere [C072, R910] *)
      st.last_imm <- None;
      let slot = st.lc in d st 0; d st 0; slot
  | _ -> failwith (Format.asprintf "codegen: condition form not in E2E-3b subset [TBD]: %a" Parser.pp_e c)

(* [R723] DR's HL-CONSTANT REUSE is a straight-line peephole: after a
   conditional skip jump the loaded constant belongs to a DIFFERENT basic
   block, so the tracking state must die with the jump.  R723 proves it --
   `if a > e then m = 1; else m = 0;` reloads `LXI H,0000` in the else
   branch instead of reusing HL=1 through the MOV L,H trick [G116], which
   the unqualified rule would have fired. *)
let lower_test_skip st (c : Ast.expr) =
  let slot = lower_test_skip0 st c in
  st.last_imm <- None;
  slot

(* [E2E-11 step 3b, C127] storing through a POINTER formal.  In a
   non-recursive procedure the formal cell holds the ADDRESS of the caller's
   variable, so a store must go through it -- and DR uses three different
   byte orders depending on whether the pointer survives the right-hand side:
     constant  : LHLD X / (XRA A / MOV M,A / INX H / MOV M,A | MVI M,lo /
                 INX H / MVI M,hi)      [E26A x=0, x=255; E25B x=3;
                 E26E x=9; E26H x=300 -- the same two-byte form past 255]
     x +- lit  : LHLD X / deref / bias / XCHG / MOV M,D / DCX H / MOV M,E
                 [E25F x=x+1; E26B x=x+256 (LXI B/DAD B), z=z-1;
                 E26I x=x-3 = three DCX H] -- HIGH byte first, because DE
                 still holds ptr+1 from the deref read
     anything  : <eval rhs> / PUSH H / LHLD X / POP D / MOV M,E / INX H /
                 MOV M,D                [E26C x=y; E26D x=x and x=x*y;
                 E26H x=q and x=x+p; E26I x=0-x] -- LOW byte first, with the
                 pointer reloaded.  DR takes this route whenever the pointer
                 is not live in DE at store time, which is why "the bias" is
                 keyed on the RHS SHAPE and not on the value.
   Only FIXED BINARY formals are covered: a DECIMAL or FLOAT formal passed by
   reference has no sample here. *)
let lower_store_ptr st (lhs_orig : string) (rhs : Ast.expr) =
  let pa = addr_of st lhs_orig in
  let lhld_ptr () = d st op_lhld; reloc st Data pa in
  let deref_read () = (d st 0x5e; d st 0x23; d st 0x56; d st op_xchg) in
  (* store HL through the pointer held in DE as ptr+1 *)
  let store_via_de () =
    (d st op_xchg; d st 0x72; d st op_dcx_h; d st 0x73)
  in
  (* store HL through the pointer, reloading it from the formal cell *)
  let store_reload () =
    (d st op_push_h; lhld_ptr (); d st op_pop_d;
     d st 0x73; d st 0x23; d st 0x72)
  in
  st.last_imm <- None;
  match (unwrap_e rhs).Ast.e with
  | Ast.Enumber k ->
      let v = parse_int_const k in
      lhld_ptr ();
      if v = 0 then (d st 0xaf; d st 0x77; d st 0x23; d st 0x77)
      else if v > 0 && v <= 0xffff then
        (d st op_mvi_m; d st (v land 0xff); d st 0x23;
         d st op_mvi_m; d st ((v lsr 8) land 0xff))
      else
        failwith "codegen: pointer store of a constant > 65535 unproven [TBD]"
  | Ast.Ebinary ((Add | Sub) as op, l, r) ->
      begin match (unwrap_e l).Ast.e, (unwrap_e r).Ast.e with
      | Ast.Eident n, Ast.Enumber k
        when String.lowercase_ascii n.Ast.orig
             = String.lowercase_ascii lhs_orig ->
          let v = parse_int_const k in
          if v = 0 then
            failwith
              ("codegen: [TBD] `x = x + 0` through a pointer formal is not                 sampled -- C119's zero-elision was established for ordinary                 cells (LHLD/SHLD only), and dropping the bias would also drop                 the store, so the shape has no evidence. Line "
              ^ string_of_int rhs.Ast.epos.Source.line)
          else begin
            lhld_ptr (); deref_read ();
            hl_bias st (if op = Add then v else -v);
            store_via_de ()
          end
      | _ -> lower_hl st rhs; store_reload ()
      end
  | _ -> lower_hl st rhs; store_reload ()

let lower_assign st (lhs : Ast.expr) (rhs : Ast.expr) =
  match lhs.Ast.e with
  | Ast.Eident n when List.mem (String.lowercase_ascii n.Ast.orig) st.deref ->
      (* [E2E-11 step 3b, C127] a first ARM, not a pre-pass: an earlier version
         called lower_store_ptr from a side-effecting guard above and then fell
         through to the ordinary store, emitting the assignment TWICE (E26E came
         out with both a store-through-pointer and an SHLD of the same value).
         Only FIXED BINARY is proven: DEC travels the decimal stack and FLOAT the
         float stack, and neither has a store-through-pointer sample [E26A-E26I]. *)
      (match vk_of st n.Ast.orig with
       | Vint -> lower_store_ptr st n.Ast.orig rhs
       | Vdec _ ->
           (* [E2E-11 step 3d, E26J] DECIMAL store through a pointer formal:
               LXI H,R A(000F) ; MVI A,09 ; CALL ?DLDOP     <- source, as usual
               LHLD Q A(0016)  ; MVI A,09 ; CALL ?DSTOP     <- dest LOADS the cell
           i.e. DR's ordinary decimal store with the destination's `LXI H'
           replaced by `LHLD'.  Nothing else changes -- same precision byte, same
           ?DSTOP -- which is why this is a 1-opcode route, not a new mechanism. *)
           let (p, sc) = Option.get (vk_dec_opt st n) in
           st.last_imm <- None;
           ignore (dec_push st (Some (p, sc)) rhs);
           d st op_lhld; reloc st Data (addr_of st n.Ast.orig);
           d st op_mvi_a; d st p; call_ext st "?DSTOP"
       | Vflt ->
           (* [E26K] FLOAT: cell-to-cell move whose destination is loaded through
              the pointer; see fl_store_var's dst_ptr branch. *)
           st.last_imm <- None;
           fl_store_var st ~dst_ptr:true (addr_of st n.Ast.orig)
             (fl_push st rhs)
       | k ->
           failwith
             ("codegen: [TBD] store through a pointer formal of type "
              ^ vk_name k
              ^ " is unsampled (FIXED BINARY [E26A-E26I], FIXED DECIMAL [E26J] "
              ^ "and FLOAT [E26K] are pinned; BIT(1)/CHAR through a pointer has "
              ^ "no DR sample; line "
              ^ string_of_int lhs.Ast.epos.Source.line ^ ")"))
  | Ast.Eident n when vk_dec_opt st n <> None ->
      (* [E2E-6] FIXED DECIMAL store: push the DEC value (with the target's
         precision as the literal context), then ?DSTOP pops it into the
         cell [R501/R502/R503/R505/R508/R510/R511] *)
      st.last_imm <- None;
      let (p, _s) = Option.get (vk_dec_opt st n) in
      ignore (dec_push st (Some (p, _s)) rhs);
      d st op_lxi_h; reloc st Data (addr_of st n.Ast.orig);
      d st op_mvi_a; d st p; call_ext st "?DSTOP"
  | Ast.Eident n
    when is_small_int st n && is_float_expr st rhs ->
      (* [E2E-11 step 4, E29B/E29E] `i = ff(i, 101.5);' where ff RETURNS FLOAT
         and i is FIXED: DR converts the float result with `CALL ?QFI15' before
         storing (E29B: CALL FF / CALL ?QFI15 / STA I).  Without that step the
         ordinary integer path takes MOV A,L of whatever HL holds -- i.e. one
         mantissa byte of a float -- and the program still compiles, links and
         RUNS with a plausible-looking number.  Refusing is the only acceptable
         behavior: my dump was 13 bytes SHORTER than DR's, which is how I found
         it, but a short file is not a safety net for the general case. *)
      failwith
        ("codegen: [TBD] assignment of a FLOAT-valued expression into a FIXED "
         ^ "variable is unimplemented (DR converts with ?QFI15 first [E29B, "
         ^ "E29E]; lowering it without the conversion silently truncates a "
         ^ "mantissa byte into the integer cell; line "
         ^ string_of_int rhs.Ast.epos.Source.line ^ ")")
  | Ast.Eident n when is_small_int st n ->
      (* [N306/N308] 1-byte FIXED BIN store: value in A then
         STA dir (3C + RELOC). Consts: MVI A,lo. Expressions:
         evaluate to HL, MOV A,L (6A). The const-reuse ladders are
         2-byte-only in DR evidence; not attempted here. *)
      st.last_imm <- None;
      (match rhs.Ast.e with
       | Ast.Enumber s ->
           let k = parse_int_const s in
           if k < 0 || k > 255 then
             failwith "codegen: 1-byte const store range [TBD]";
           (* [E2E-11 step 4, E29B/E29D/E29E + DTEST] zero is stored by CLEARING
              the accumulator, not by loading an immediate: DR emits `XRA A'
              (1 byte) where the general constant path uses `MVI A,00' (2).  Same
              economy as C119's zero elision and the DO-init form, and E29D's
              `i = 0;' pinned it independently of DTEST's loop initialization.
              Non-zero constants keep MVI A,lo, which N306/N308 pin. *)
           if k = 0 then d st 0xaf else begin
             d st op_mvi_a; d st k
           end
       | _ -> lower_hl st rhs; d st 0x7d (* MOV A,L *)) ;
      (* 1-byte store: DR emits opcode 0x32 with the inline-reloc
         16-bit address ($C prints 'STA'; byte replicated literally
         [N303/N306/N308], same family of byte-vs-mnemonic quirks
         as CA/F2 — runtime identity comes from byte-identical COM) *)
      d st 0x32; reloc st Data (addr_of st n.Ast.orig)
  | Ast.Eident n when vk_of st n.Ast.orig = Vflt ->
      (* [E2E-10] store into a FLOAT variable: a literal or plain-cell source
         copies cell-to-cell with ?FX44M [R3001, R3037]; a computed value is
         popped off the float stack with ?FX44S [R3030-R3034] *)
      st.last_imm <- None;
      fl_store_var st (addr_of st n.Ast.orig) (fl_push st rhs)
  | Ast.Eident n when vk_of st n.Ast.orig = Vbit1 ->
      (* [E2E-11 step 1a] DR's whole BIT(1) store, from E20A:
            LXI  H,F A(0002) ; MVI  M,80      ('1'b)
            LXI  H,F A(0002) ; MVI  M,00      ('0'b)
         A 4-byte address form plus a 2-byte memory immediate -- no accumulator,
         no runtime call.  Only a 1-character bit LITERAL is accepted: copying
         bit to bit, assigning from an expression, or storing a character/number
         into a bit cell are all unsampled, so they keep refusing. *)
      st.last_imm <- None;
      let byte =
        match rhs.Ast.e with
        | Ast.Ebit "1" -> 0x80
        | Ast.Ebit "0" -> 0x00
        | _ ->
            failwith
              (Printf.sprintf
                 "codegen: store into BIT(1) from %s is unsampled [TBD]                   (only the '1'b/'0'b literals are pinned by E20A)"
                 (expr_kind_name rhs.Ast.e))
      in
      d st op_lxi_h; reloc st Data (addr_of st n.Ast.orig);
      d st 0x36 (* MVI M,d *) (* ; DR: MVI M,80 / MVI M,00 [E20A] *); d st byte
  | Ast.Eident _n when is_float_expr st rhs ->
      failwith
        (Printf.sprintf
           "codegen: storing a FLOAT value into a non-float variable is unsampled [TBD] (line %d; ?FL40M/?QFI15 has no standalone sample)"
           rhs.Ast.epos.Source.line)
  | Ast.Eident n when is_dec_expr st rhs ->
      (* [E2E-6/R506] DEC -> INT: push the decimal value, convert with
         ?QDI15 (16-bit result in HL), then the ordinary integer store.
         R506 line 6 exactly: LXI H,D A(0002) ; MVI A,0F ; CALL ?DLDOP ;
         CALL ?QDI15 ; SHLD I A(0000).  The DLDOP precision is the
         SOURCE decimal's, not the target's. *)
      let vi =
        match
          List.assoc_opt (String.lowercase_ascii n.Ast.orig) st.vars
        with
        (* an undeclared name reaches here as PL/I's implicit FLOAT, which
           this compiler does not model; fail loud instead of raising
           Not_found out of List.assoc [E2E-9 hygiene] *)
        | Some v -> v
        | None ->
            failwith
              ("codegen: assignment target " ^ n.Ast.orig
               ^ " has no declaration in scope [TBD] (implicit FLOAT is"
               ^ " NOT IMP)")
      in
      if not (dec_pure st rhs) then
        failwith
          "codegen: mixed decimal/integer arithmetic unproven [TBD]            (the DEC->INT conversion is pinned only for a direct decimal             operand: i = d [R506])";
      if vi.size <> 2 then
        failwith
          "codegen: DEC->INT store into a 1-byte FIXED target [TBD] \
           (only the FIXED BIN(15) conversion is pinned by R506)";
      st.last_imm <- None;
      ignore (dec_push st None rhs);
      call_ext st "?QDI15";
      d st op_shld; reloc st Data (addr_of st n.Ast.orig)
  | Ast.Eident n when vk_of st n.Ast.orig <> Vint ->
      (* char/varying store path [V101-V106]; HL clobbered *)
      st.last_imm <- None;
      (match rhs.Ast.e with
       | Ast.Estring v -> store_char st n.Ast.orig (vk_of st n.Ast.orig) v
       | _ -> failwith "codegen: char store from non-literal [TBD]")
  | Ast.Eident n ->
      (* [E2E-11 step 1a] DR's zero-elision pass, before any shape matching:
         this is what turns `a = a + 0' into a 6-byte self-copy instead of an
         ADD, and `b = a + 0 + 0' into one copy of `a' [T5, T8, T9, T13]. *)
      let rhs = elide_fixed_zero st rhs in
      (* HL-REUSE PEEPHOLE [G114 $C]: `a = 5; b = 3;` lowers the second
         constant as 2x DCX H on the HL=5 still live after SHLD A, not a
         fresh LXI H. Only the delta 1..4 (DCX repeat) form is proven;
         larger deltas and INX directions stay [TBD]-free by falling
         back to the ordinary fresh-load path. *)
      (match rhs.Ast.e with
       | Ast.Enumber s ->
           let k = parse_int_const s in
           (match st.last_imm with
            (* [R610/R611/LOAN1] same constant stored again: DR emits NO
               reload at all -- HL still holds it, SHLD does not disturb it.
               LOAN1 needs this for `m = 0; y = 0;` (LXI H,0000; SHLD M;
               SHLD Y) and R611 proves it is value-equality, not zero:
               `x = 5; y = 5;` also shares one LXI H,0005. *)
            | Some pv when pv = k -> st.last_imm <- Some k
            (* [G116] k=0 with previous H byte = 0: MOV L,H zeroes HL *)
            | Some p when k = 0 && p land 0xff00 = 0 ->
                st.last_imm <- Some k; d st 0x6c (* MOV L,H *)
            (* [G114] small positive delta: DCX H repeats *)
            | Some p when p - k >= 1 && p - k <= 2 ->
                st.last_imm <- Some k;
                const_sub st (p - k)
            (* [G114B] small negative delta: INX H repeats *)
            | Some p when k - p >= 1 && k - p <= 2 ->
                st.last_imm <- Some k;
                for _ = 1 to k - p do d st op_inx_h done
            (* [Z401 delta 3, Z406 delta 4] same high byte, |delta|>=3:
               MVI L,lo (2 bytes beats any ladder). G114C (delta 771,
               differing high) stays on the fresh-LXI fallback. *)
            | Some p when p land 0xff00 = k land 0xff00
                          && (p - k >= 3 || k - p >= 3) ->
                st.last_imm <- Some k;
                d st 0x2e (* MVI L *) ; d st (k land 0xff)
            | _ ->
                st.last_imm <- Some k;
                d st op_lxi_h; d st (k land 0xff); d st ((k lsr 8) land 0xff))
       | Ast.Ebinary ((Ast.Add | Ast.Sub as op), { Ast.e = Ast.Eident m; _ },
                      { Ast.e = Ast.Enumber ks; _ })
         when String.lowercase_ascii m.Ast.orig
              = String.lowercase_ascii n.Ast.orig
              (* the arm is for INTEGER literals only: a float literal written
                 against a fixed variable (`x = x + 2.5') must fall through to
                 the generic path, which refuses it.  Without this guard
                 parse_int_const calls int_of_string on "2.5" and the failure is
                 an uncaught exception instead of a [TBD] -- exactly the R3045
                 crash class, re-introduced by widening the pattern. *)
              && is_int_literal ks ->
           (* [E2E-11 step 1a] DR's SELF-ADD / SELF-SUB LADDER, now measured
              across the whole small-k range instead of inferred from one point.
              A program per k (golden/e2e11n, E22A02..E22A16, E22B01..E22B08),
              each preceded by `n = 100;' so the preceding HL cannot be blamed
              for the choice:
                 k = 1,2,3        LHLD v ; (INX H)*k          ; SHLD v
                 k = 4..16        LHLD v ; LXI B,k ; DAD B     ; SHLD v
                 k = -1,-2,-3     LHLD v ; (DCX H)*|k|         ; SHLD v
                 k = -4,-5,-8     LHLD v ; LXI B,FFFC/FFFB/FFF8 ; DAD B ; SHLD v
              so the break-even point is |k| = 4 in BOTH directions, with the
              negative side carrying the two's-complement value in LXI B.  This
              extends the Z401/Z403/Z404 `x = x + 1' rule that used to live here
              alone (its comment said -1 and the INX repeats were unproven --
              they are now).  My generic path lowered `n = n + 2' as
              LHLD/XCHG/LXI H,2/DAD D, which computes the right VALUE and the
              wrong BYTES; that is the class of divergence byte-parity exists to
              catch, and E21A found it by accident.
                 k = 0          LHLD v ;                       SHLD v
              is now sampled too: DR reduces `a = a + 0' and `a = a - 0' to the
              bare self-copy, and its .REL for the two is BYTE-IDENTICAL to the
              one for `a = a' [golden/e2e11v/T5, T6, e2e11w/T7 -- 21 bytes of
              code each].  hl_bias already emits nothing for a zero bias, so
              allowing k = 0 through the same arm reproduces DR with no extra
              code; the previous `ks <> "0" guard sent it to the generic path,
              which produced LXI H/SHLD/LHLD/XCHG/LXI H,0/DAD D -- right value,
              wrong bytes.  A 1-byte target still has no sample (it would need
              the STA form), so that keeps refusing. *)
           let k0 = parse_int_const ks in
           let k = if op = Ast.Sub then -k0 else k0 in
           let vi =
             match List.assoc_opt (String.lowercase_ascii n.Ast.orig) st.vars
             with Some v -> v
             | None -> failwith "codegen: undeclared self-add target [TBD]"
           in
           if vi.size <> 2 then
             failwith
               "codegen: self add/sub on a 1-byte FIXED target is unsampled [TBD] (E22 ladder is the 2-byte LHLD/SHLD form only)";
           st.last_imm <- None;
           d st op_lhld; reloc st Data (addr_of st n.Ast.orig);
           hl_bias st k;
           (* final SHLD comes from the common tail *)
       | _ ->
           st.last_imm <- None;
           lower_hl st rhs);
      d st op_shld; reloc st Data (addr_of st n.Ast.orig)
  | Ast.Esuffix (hd, args)
    when hd_is_element st.arrays hd ->
      (* [E2E-20/Priority 4] ELEMENT STORE -- DR's four measured forms.  Again a GUARDED
         case, so it cannot fall through into any other assignment route.
           1. offset 0, any value            ... ; SHLD A(base)      [AB1 AB16 AC5 AB12]
           2. offset <> 0, LITERAL value     LXI H,A+off ; MVI M,lo ; INX H ; MVI M,hi
                                                                      [AB3 AB9 AB14 AC3]
           3. offset <> 0, COMPUTED value    PUSH H ; LXI H,A+off ; POP D ;
                                             MOV M,E ; INX H ; MOV M,D [AC1 AC2 AC3]
           4. SAME element on both sides     LHLD A+off ; <bias> ; SHLD A+off
                                                                 [AB12 off 0, AC4 off 2]
         The ORDER matters and is what C165 established: "literal vs computed" is NOT DR's
         discriminator -- AC1 (`a(3) = b') parks on the stack because LXI H must destroy HL,
         while AC4 (`a(2) = a(2) + 5') needs no parking because the element address is an
         immediate operand of BOTH the load and the store.  Form 4 is therefore tested
         BEFORE form 3.  Anything outside the four refuses. *)
      let (addr, off) =
        match resolve_suffix st hd args with
        | Suf_element a ->
            let (lb, _ub, ez) =
              match
                List.find_opt
                  (fun (n, _l, _u, _e) ->
                    String.equal n
                      (match hd.Ast.e with
                       | Ast.Eident h -> String.lowercase_ascii h.Ast.orig
                       | _ -> "?"))
                  st.arrays
              with
              | Some (_n, l, u, e) -> (l, u, e)
              | None -> assert false
            in
            let sub =
              match (unwrap_e (List.hd args)).Ast.e with
              | Ast.Enumber t -> int_of_string (String.concat "" (String.split_on_char '_' t))
              | _ -> assert false
            in
            (a, (sub - lb) * ez)
        | Suf_element_dyn _ ->
            (* placeholder: the dynamic branch below takes over before addr/off are used *)
            (0, 0)
        | Suf_call _ -> assert false
      in
      let dyn_r =
        match resolve_suffix st hd args with
        | Suf_element_dyn r -> Some r
        | _ -> None
      in
      (* form 4: self-update on the very same element with a literal bias *)
      let self_k =
        match (unwrap_e rhs).Ast.e with
        | Ast.Ebinary ((Ast.Add | Ast.Sub) as op, l, r) ->
            (match (unwrap_e l).Ast.e, (unwrap_e r).Ast.e with
             | Ast.Esuffix (lh, largs), Ast.Enumber ks ->
                 (match (try Some (resolve_suffix st lh largs) with _ -> None) with
                  | Some (Suf_element laddr) ->
                      if laddr = addr then
                        let k0 = int_of_string
                          (String.concat "" (String.split_on_char '_' ks)) in
                        Some (if op = Ast.Sub then -k0 else k0)
                      else None
                  | _ -> None)
             | _ -> None)
        | _ -> None
      in
      match self_k with
      | Some k ->
          st.last_imm <- None;
          d st op_lhld; reloc st Data addr;
          hl_bias st k;
          d st op_shld; reloc st Data addr
      | None ->
          let litv =
            match (unwrap_e rhs).Ast.e with
            | Ast.Enumber t ->
                Some (int_of_string
                        (String.concat "" (String.split_on_char '_' t)))
            | _ -> None
          in
          if dyn_r <> None then begin
            (* [E2E-22/P2] variable-index STORE.  Two DR-measured shapes, and the discriminator is
               the SAME one as for the ladder's own parking [C141]:
                 literal value   (AB2 `a(i)=9', VB1, VB2) : <ladder> ; MVI M,lo ; INX H ; MVI M,hi
                 computed value  (AB8 `a(i+1)=i*2', AB10 `a(i)=i'):
                     lower_hl(rhs) ; PUSH H ; <ladder> ; POP D ; MOV M,E ; INX H ; MOV M,D
               The computed form parks the VALUE before the ladder runs, so the ladder's own
               PUSH H/POP D pair (needed when bias<>0) nests inside it -- two live stack slots, and
               the value is recovered into DE by the outer POP D immediately before storing.  Byte
               order is E2E-20's corrected one: 0x73 MOV M,E (low) then 0x72 MOV M,D (high).
               NOT measured, so refused: a computed store whose bias is 0 (whether DR would still
               nest a parking pair when the ladder itself has none), and self-update like
               `a(i) = a(i) + 5' -- AC4's form-4 rule is constant-index only. *)
            let r =
              match dyn_r with Some r -> r | None -> assert false
            in
            match litv with
            | Some v ->
                dyn_addr st r;
                d st op_mvi_m; d st (v land 0xff);
                d st op_inx_h; d st op_mvi_m; d st ((v lsr 8) land 0xff)
            | None ->
                if r.dyn_bias = 0 then
                  failwith
                    "codegen: [TBD] variable-index store of a computed value with lower bound 0 \
                     [E2E-22]: both DR-measured computed stores carry a nonzero bias (AB8 lb=1, \
                     AB10 lb=1) and park the value with PUSH H before a ladder that itself parks \
                     the base.  With bias=0 the ladder needs no parking, so whether DR still \
                     nests a pair is UNMEASURED -- refused rather than guessed [C159]"
                else begin
                  st.last_imm <- None;
                  lower_hl st rhs;
                  d st op_push_h;
                  dyn_addr st r;
                  d st op_pop_d;
                  d st 0x73; d st op_inx_h; d st 0x72
                end
          end
          else if off = 0 then begin
            (* form 1: DR's ordinary scalar store -- value in HL, one SHLD.
               AB16 `q(1) = 2' gives `LXI H,0002 / SHLD Q A(0000)' and AC5
               `a(1) = b * 2' gives `LHLD B / DAD H / SHLD A A(0000)', so the
               value route is whatever lower_hl already does. *)
            st.last_imm <- None;
            lower_hl st rhs;
            d st op_shld; reloc st Data addr
          end
          else
            match litv with
            | Some v ->
                (* form 2 *)
                let w = v land 0xffff in
                st.last_imm <- None;
                d st op_lxi_h; reloc st Data addr;
                d st op_mvi_m; d st (w land 0xff);
                d st op_inx_h;
                d st op_mvi_m; d st ((w lsr 8) land 0xff)
            | None -> begin
                (* form 3: park the value on the stack, then byte-store from DE.
                   Only the LITERAL-bias self-update (form 4) and these four are
                   measured; a 1-byte element never reaches here (bind refuses). *)
                st.last_imm <- None;
                lower_hl st rhs;
                d st op_push_h;
                d st op_lxi_h; reloc st Data addr;
                d st op_pop_d;
                (* NB: 0x73 = MOV M,E and 0x72 = MOV M,D -- E (low byte) goes to the LOW
                   address first, then D (high) after INX H, exactly as DR's AC1 shows
                   (`MOV M,E / INX H / MOV M,D').  An earlier draft had these swapped
                   because the opcode comments were wrong; AC1/AC2 caught it [E2E-20]. *)
                d st 0x73; (* MOV M,E *)
                d st op_inx_h;
                d st 0x72  (* MOV M,D *)
              end
  | _ -> failwith "codegen: non-simple assignment lhs [TBD]"

(* ---- E2E-3b: comparisons ----  ALL forms transcribed from $C traces
   golden/e2e3b (G114/G115/G116) — see spec/notes/codegen.md:
   var OP var: relational = load pair XCHG-form + ?IS22N + sign-test
     conditional skip (Gt/Le evaluate RIGHT-left with JP/JM; Lt/Ge
     evaluate LEFT-right); equality = PUSH/POP form + MOV A,H; ORA L
     zero test + JNZ/JZ. var = 0: memory zero test (LXI H; MOV A,M;
     INX H; ORA M; JNZ). var > k (k>=1): LHLD; LXI B,-(k+1); DAD B;
     MOV A,H; ORA A; JM. Each returns the forward conditional-jump
     operand SLOT (fixed later by emit_triple at the skip target). *)

(* GET LIST(n1, n2, ...).  The statement SKELETON is shared by every target
   kind [X201/X202 char-varying, R901-R907 numeric]: LXI D,0290 input
   descriptor (vs 0252 for print, never relocated); LXI B,0000 whose operand
   is triple-patched to the NEXT statement; ?SYSIN; then ONE `?GNVOP ; JP`
   PAIR PER ITEM in source order.  Item k's JP operand is patched to whatever
   follows that item's store -- the NEXT item's GNVOP [R904: 0013 ==== 001B]
   or the closing ?QIOOP for the last item [X202] -- so a skip (EOF / no
   value) abandons the remaining items, not the statement.  One ?QIOOP closes
   the whole statement.

   PER-ITEM CONVERSION, by destination kind [R901-R907]:
     FIXED DEC(p,s) : MVI B,s ; ?QCDOP ; LXI H,var ; MVI A,p ; ?DSTOP
        B is the TARGET SCALE -- 02 for dec(11,2)/dec(9,2), 04 for dec(6,4),
        03 for dec(15,3) -- and is EMITTED even at s=0 [R905 `MVI B,00`]; A is
        the TARGET DIGITS [LOAN1 P=0B, R906 x=0F].  So ?QCDOP converts the
        scanned field straight to scale s and ?DSTOP stores it like any other
        DEC store -- which is why no QDDSL/QDDSR appears here at all.
     FIXED BIN(2b)  : ?QCIOP ; SHLD var                [R903, R904: no MVI]
     CHAR VAR(cap)  : LXI H,var ; MVI B,cap ; ?SSVFS   [X201/X202]
*)
let lower_get st (items : Ast.name list) =
  if
    List.exists
      (fun n -> List.mem (String.lowercase_ascii n.Ast.orig) st.deref)
      items
  then failwith "codegen: GET into pointer formal unproven [TBD]";
  d st op_lxi_d; d st 0x90; d st 0x02;   (* LXI D,0290 input desc *)
  d st op_lxi_b;
  let bslot = st.lc in
  d st 0; d st 0;
  call_ext st "?SYSIN";
  List.iter
    (fun n ->
      call_ext st "?GNVOP";
      d st op_jp;
      let jpslot = st.lc in
      d st 0; d st 0;
      (match List.assoc_opt (String.lowercase_ascii n.Ast.orig) st.vars with
       | Some vi -> (
           match vi.vk with
           | Vdec (p, s) ->
               d st op_mvi_b;
               d st s; (* B = TARGET SCALE, emitted even at 0 [R905] *)
               call_ext st "?QCDOP";
               d st op_lxi_h;
               reloc st Data (addr_of st n.Ast.orig);
               d st op_mvi_a;
               d st p; (* A = TARGET DIGITS [LOAN1 0B, R906 0F] *)
               call_ext st "?DSTOP"
           | Vflt ->
               (* [E2E-10 step 3] DR reads the token as DECIMAL and then
                  converts: ?QCXOP (clean the decimal), ?QX8F4 (decimal ->
                  4-byte float into the accumulator), then the ordinary
                  float store ?FX44S into the variable's cell [R3004, two
                  items; R3065/R3066 pin one item and a mixed float+fixed
                  list].  Note what this means for the value model: an
                  input float goes through the DECIMAL reader, so C101's
                  literal-conversion rounding law is NOT the path a runtime
                  read takes -- it reuses ?GNVOP's decimal scan, which is
                  why the width/scale MVIs the DEC branch emits are absent
                  here.  Nothing in this tail is invented: no MVI A/B
                  operands appear in any DR sample. *)
               call_ext st "?QCXOP";
               call_ext st "?QX8F4";
               d st op_lxi_h;
               reloc st Data (addr_of st n.Ast.orig);
               call_ext st "?FX44S"
           | Vint when vi.size = 2 ->
               call_ext st "?QCIOP";
               d st op_shld; reloc st Data (addr_of st n.Ast.orig)
           | Vint ->
               (* a 1-byte FIXED BIN store is the 0x32/`STA` form [C079] and
                  no numeric-GET sample has one: refuse rather than guess. *)
               failwith
                 "codegen: numeric GET into a 1-byte FIXED BINARY target is unproven [TBD] (R903/R904 sample only the 2-byte ?QCIOP/SHLD form)"
           | Vvar c ->
               if c > 255 then failwith "codegen: cap > 255 [TBD]";
               d st op_lxi_h;
               reloc st Data (addr_of st n.Ast.orig);
               d st op_mvi_b;
               d st c;
               call_ext st "?SSVFS"
           | _ ->
               failwith
                 "codegen: GET LIST of this target kind is unproven [TBD] (based, pointer, float and bit targets are unsampled)")
       | None ->
           failwith
             (Printf.sprintf "codegen: GET LIST of unknown variable %s [TBD]"
                n.Ast.orig));
      (* the skip lands on whatever comes next [R904, X202] *)
      emit_triple st jpslot st.lc)
    items;
  call_ext st "?QIOOP";
  emit_triple st bslot st.lc           (* continuation = next stmt *)

(* PUT LIST with || chain: DR evaluates RIGHT-to-LEFT while the
   pool is allocated LEFT-to-RIGHT in source order [W102 hex:
   HELLO@5, BYE@0x0B]. C2: SLVTS(right var; empty stack -> no PUSH
   PSW) then SJSCM(lit in B). C3: SLCTS(right lit in A); PUSH PSW;
   SLVTS(var); SJSCM(left lit in B); SJSTS. Tail = the standard
   PNCOP/QIOOP + continuation triple [W101/W102]. *)
let lower_cat st (skipn : put_skip) (ch : chain) =
  let maxlit = match ch with C2 (l, _, _) -> String.length l
               | C3 (l, _, r) -> max (String.length l) (String.length r) in
  if maxlit > 255 then failwith "codegen: lit > 255 [TBD]";
  d st op_lxi_d; d st 0x52; d st 0x02;
  d st op_lxi_b;
  let bslot = st.lc in
  d st 0; d st 0;
  call_ext st "?SYSPR";
  (match skipn with
   | Sk_lit c ->
       let n = parse_int_const c in
       if n <= 0 || n > 255 then
         failwith "codegen: skip count out of MVI range [TBD]";
       d st op_mvi_a; d st n; call_ext st "?SKPOP"
   | Sk_expr e -> emit_skip_count st e   (* [SK3 SK4] LHLD / MOV A,L / CALL ?SKPOP *)
   | Sk_none -> ());
  let vk_guard nm =
    match vk_of st nm with
    | Vvar _ -> ()
    | _ -> failwith "codegen: concat operand not char varying [TBD]"
  in
  (match ch with
  | C2 (l, v, _) ->
      let al = pool_alloc st (pool_bytes l) in
      vk_guard v;
      d st op_lxi_h; reloc st Data (addr_of st v);   (* rightmost first *)
      call_ext st "?SLVTS";
      d st op_lxi_h; reloc st Data al;
      d st op_mvi_b; d st (String.length l);
      call_ext st "?SJSCM"
  | C3 (l, v, r) ->
      (* [W102] pool allocation = SOURCE order (HELLO@5, BYE@0x0B) *)
      let al = pool_alloc st (pool_bytes l) in
      let ar = pool_alloc st (pool_bytes r) in
      vk_guard v;
      d st op_lxi_h; reloc st Data ar;
      d st op_mvi_a; d st (String.length r);
      call_ext st "?SLCTS";                          (* rightmost *)
      d st op_lxi_h; reloc st Data (addr_of st v);
      d st op_push_psw;        (* [W102] AFTER LXI H, before SLVTS *)
      call_ext st "?SLVTS";
      d st op_lxi_h; reloc st Data al;
      d st op_mvi_b; d st (String.length l);
      call_ext st "?SJSCM";
      call_ext st "?SJSTS");
  call_ext st "?PNCOP"; call_ext st "?QIOOP";
  emit_triple st bslot st.lc

(* DO ind = from TO bound [BY 1];) E2E-4 slice, [Y301-Y305] bytes:
   init reuses HL when last_imm = from-1 (INX H [Y302]) else LXI H.
   STATIC bound b: head = LHLD i; LXI B,-(b+1); DAD B; MOV A,H;
   ORA A; JP(F2) -> exit (deferred triple AFTER the loop's JMP on the
   record stream [Y301 dump]). DYNAMIC simple-int bound: LHLD bound;
   SHLD temp(base+auto_end+2k); head = LHLD temp; XCHG; LHLD i;
   CALL ?IS22N; JM(FA) -> exit. Increment shared: LHLD i; INX H;
   SHLD i; JMP head (inline backward RELOC). Body continuation
   triples land on the increment start automatically [Y301: put
   cont -> 0x2F]. BY must be absent or literal 1 [Y304]; WHILE/
   REPEAT/no-TO/complex bounds/steps/index types all [TBD]. *)
(* [E2E-22/P4] a POINTER formal read in a DO bound position must be DEREFERENCED, exactly as it
   is when it appears in an expression [C130/E2E-11]: the cell holds the ADDRESS of the caller's
   variable, not a value.  DR's measured tail in both bound slots:
     TO   (DO1 `do j = 1 to x'):   LHLD <x> ; MOV E,M ; INX H ; MOV D,M ; XCHG ; SHLD <temp>
     FROM (DO2 `do j = x to 5'):   LHLD <x> ; MOV E,M ; INX H ; MOV D,M ; XCHG ; SHLD <index>
   Without it the ADDRESS becomes the bound -- a wrong-VALUE miscompile, not a cosmetic byte
   difference: PASSARAY's `do J = 1 to val' printed 69900 lines where DR prints 75, and ARRAY
   139580 against 75 (measured by linking both .RELs with LINK 1.31 and running under cpmsim).
   This exists so the same rule is applied once at each of the two sites instead of being
   re-derived, and it is conditional on st.deref so every non-formal bound (NFACT, RFACT, IFACT,
   R10xx -- all byte-exact) is untouched. *)
let do_bound_deref st d nm =
  if List.mem (String.lowercase_ascii nm) st.deref then begin
    d st 0x5e; d st op_inx_h; d st 0x56; d st op_xchg
  end

let lower_doto st (ls : lblstate) (lo : st -> lblstate -> Ast.stmt -> unit)
    (ind : Ast.name) (from : Ast.expr)
    (by : Ast.expr option) (to_ : Ast.expr option)
    (while_ : Ast.expr option) (rep : Ast.expr option)
    (body : Ast.stmt) =
  (* proven REPEAT form [Z402/DFACT]: DO ind = c REPEAT(ind+1), no
     TO/WHILE/BY. Everything else about REPEAT/WHILE combos is
     unevidenced and stays [TBD]. *)
  let proven_repeat =
    match rep, to_, while_ with
    | Some { Ast.e = Ast.Ebinary (Ast.Add,
             { Ast.e = Ast.Eident ri; _ },
             { Ast.e = Ast.Enumber "1"; _ }); _ }, None, None
      when String.lowercase_ascii ri.Ast.orig =
           String.lowercase_ascii ind.Ast.orig -> true
    | _ -> false
  in
  let forever_repeat =
    match (to_, while_, rep) with
    | (None, None, Some _) -> true
    (* [E2E-8] `do i = 0 by 1;' indexes the loop but gives no bound and no
       REPEAT expression: DR emits NO exit test at all (the increment is the
       whole continuation) [IFACT, R1014, R1030-R1033] *)
    | (None, None, None) -> true
    | _ -> false
  in
  if while_ <> None
     || (to_ <> None && rep <> None)
     || (rep <> None && not proven_repeat && not forever_repeat) then
    failwith "codegen: DO WHILE/REPEAT combo/UNTIL deferred [TBD]";
  (* [E2E-8] DO ... BY step.  A step is an INTEGER LITERAL: DR's increment is
     |step| rung instructions, so an expression step cannot be lowered that
     way at all [N36 stays refused; DR also rejects a non-integer step at
     compile time].  Magnitudes above 2 are unprobed. *)
  let step =
    match by with
    | None -> 1
    | Some { Ast.e = Ast.Enumber c; _ } -> parse_int_const c
    (* a negative literal step arrives as Eprefix(Minus, Enumber) *)
    | Some { Ast.e = Ast.Eprefix (Ast.Minus,
             { Ast.e = Ast.Enumber c; _ }); _ } ->
        -(parse_int_const c)
    | Some _ -> failwith "codegen: DO BY expression step unproven [TBD]"
  in
  if step = 0 then failwith "codegen: DO BY 0 [TBD]";
  let ak = abs step in
  if ak > 2 then failwith "codegen: DO BY magnitude > 2 unproven [TBD]";
  (* [E2E-8] FROM may be a constant (LXI H,imm) or a fixed-bin VARIABLE
     (LHLD v / SHLD index -- IFACT's `do n = i to 1 by -1') *)
  let fromc, fromvar =
    match from with
    | { Ast.e = Ast.Enumber c; _ } -> (Some (parse_int_const c), None)
    | { Ast.e = Ast.Eident nm; _ } ->
        (None,
         match vk_of st nm.Ast.orig with
         | Vint -> Some (addr_of st nm.Ast.orig)
         | _ -> failwith "codegen: DO FROM of non fixed-bin type unproven [TBD]")
    | _ -> failwith "codegen: DO FROM form unproven [TBD]"
  in
  if List.mem (String.lowercase_ascii ind.Ast.orig) st.deref then
    failwith "codegen: DO control is a pointer formal [TBD]";
  let iaddr =
    match vk_of st ind.Ast.orig with
    | Vint -> addr_of st ind.Ast.orig
    | _ -> failwith "codegen: DO index not fixed-bin [TBD]"
  in
  (* [E2E-8] init: DR loads the FROM constant with the CHEAPEST instruction
     that achieves it given the value already in HL (st.last_imm tracks that
     exact value; LXI H/imm and INX H set it, LHLD / branches / loop-body
     entry clear it):
       HL already = from       -> SHLD only          (0 load bytes) [R1015,R1022,R1032]
       HL already = from - 1   -> INX H ; SHLD       (1 byte)       [R1011, Y302]
       H known 0, from <= 255  -> MVI L,from ; SHLD  (2 bytes)      [R1012,R1013,R1030]
       otherwise               -> LXI H,from ; SHLD  (3 bytes)      [Y302, IFACT outer]
     MVI L is only safe when H is known 0, which is exactly the
     last_imm < 256 case. *)
  (match fromc with
   | Some fromv ->
       if is_small_int st ind then
         (* [E2E-11 step 4, DTEST] a 1-byte index cell (fixed(7) needs one byte)
            cannot be initialized through the HL ladder at all: DR clears the
            ACCUMULATOR and stores it directly --
                0006  XRA  A
                0007  STA  I A(000F)
            `XRA A' rather than `MVI A,00' because clearing A is 1 byte and MVI
            is 2, which is the same cheap-zero economy as C119's zero elision.
            Only from = 0 is sampled: for from = 5 there is no DR evidence
            whether it is `MVI A,05 / STA', a reload through LXI H + MOV A,L, or
            something else, and inventing it would change DTEST-shaped programs
            silently.  HL-constant reuse is NOT claimed here: this store never
            puts the value in HL, so last_imm is cleared instead of set. *)
         begin
         if fromv <> 0 then
            failwith
              ("codegen: [TBD] DO index = " ^ string_of_int fromv
                 ^ " into a 1-byte index cell is unsampled (DTEST pins only 0, "
                 ^ "lowered as XRA A / STA <index>; line "
                 ^ string_of_int from.Ast.epos.Source.line ^ ")");
         st.last_imm <- None;
         d st 0xaf; d st 0x32; reloc st Data iaddr
       end
       else begin
       (match st.last_imm with
        | Some v when v = fromv -> ()
        | Some v when v + 1 = fromv -> d st op_inx_h
        | Some v when v >= 0 && v < 256 && fromv >= 0 && fromv < 256 ->
            d st 0x2e; d st fromv        (* MVI L,from *)
        | _ ->
            d st op_lxi_h; d st (fromv land 0xff);
            d st ((fromv lsr 8) land 0xff));
       st.last_imm <- Some (fromv land 0xffff);
       d st op_shld; reloc st Data iaddr
       end
   | None ->
       (* variable FROM: load the source cell, store the index cell
          [IFACT 000C-000F: LHLD I / SHLD N] *)
       (match fromvar with
        | Some a -> d st op_lhld; reloc st Data a
        | None -> failwith "codegen: DO FROM [TBD]");
       (match (unwrap_e from).Ast.e with
        | Ast.Eident h -> do_bound_deref st d h.Ast.orig  (* [DO2] formal FROM [E2E-22/P4] *)
        | _ -> ());
       d st op_shld; reloc st Data iaddr;
       st.last_imm <- None);
  if to_ = None && while_ = None && rep = None && by = None then begin
    (* [E2E-8 R1032] an indexed DO that specifies NOTHING (no TO, no WHILE,
       no REPEAT, no BY) degenerates: DR stores the FROM value, runs the body
       ONCE and falls through -- no increment, no exit test, no back-edge JMP.
       It is therefore not a no-exit loop and does not open the epilogue
       suppression window (DR's PUT after it lowers normally). *)
    lo st ls body;
    st.last_imm <- None
  end else if proven_repeat || forever_repeat then begin
    (* [Z402] body-head is the FIRST BODY instruction (not the
       init); tail increment LHLD/INX/SHLD; JMP back; no test.
       [R414/R426] at the window address the increment is
       LHLD; LXI H,const; DAD D; SHLD; JMP instead. *)
    (* [E2E-8] with no REPEAT expression the increment is the BY step:
       LHLD / (INX H)x|step| (or (DCX H)x|step| when step < 0) / SHLD / JMP
       [IFACT outer loop, R1014 k=1, R1018 k=2, R1033 k=-1]. *)
    let head = st.lc in
    st.last_imm <- None;   (* [E2E-8] body head is a branch target: HL unknown *)
    lo st ls body;
    if is_small_int st ind && rep = None && step = 1 then begin
      (* [E2E-11 step 4, DTEST] a 1-byte index cell is incremented IN PLACE
         through a pointer, not loaded/bumped/stored:
             005C  LXI  H,I A(000F)
             005F  INR  M
             0060  JMP  000A
         DR's 2-byte ladder (LHLD / INX H / SHLD) needs 7 bytes; this is 4, and
         the difference is 3 bytes of code -- which is why DTEST's whole tail
         shifted before this branch existed.  `by -1' and `by 2' on a 1-byte
         cell have no DR sample (DTEST is step 1), so they fall through to the
         refusal below rather than reusing DCR M on a guess. *)
      d st op_lxi_h; reloc st Data iaddr;
      d st 0x34;                          (* INR M *)
      d st op_jmp;
      st.last_imm <- None (* [R723] branch boundary *);
      reloc st Code head;
      st.last_imm <- None
    end
    else if is_small_int st ind then
      failwith
        ("codegen: [TBD] 1-byte index cell with step " ^ string_of_int step
           ^ " / REPEAT is unsampled (DTEST pins only `by 1', lowered as "
           ^ "LXI H,<index> / INR M)")
    else begin
    d st op_lhld; reloc st Data iaddr;
    (* [Z402 k=1; R427 k=2] REPEAT(ind+k) = k INX H rungs;
       k>2 / other shapes unproven -> [TBD] *)
    (match rep with
     | Some { Ast.e = Ast.Ebinary (Ast.Add,
              { Ast.e = Ast.Eident ri; _ },
              { Ast.e = Ast.Enumber ck; _ }); _ }
       when String.lowercase_ascii ri.Ast.orig =
            String.lowercase_ascii ind.Ast.orig ->
         let k = parse_int_const ck in
         if k < 1 || k > 2 then
           failwith "codegen: REPEAT increment const [TBD]";
         for _ = 1 to k do d st op_inx_h done
     | None ->
         for _ = 1 to ak do
           d st (if step > 0 then op_inx_h else op_dcx_h)
         done
     | _ -> failwith "codegen: REPEAT increment form [TBD]");
    d st op_shld; reloc st Data iaddr;
    (d st op_jmp; st.last_imm <- None (* [R723] branch boundary *)); reloc st Code head;
    st.last_imm <- None
    end
  end else begin
  let head, jpslot =
    match to_ with
    | Some { Ast.e = Ast.Enumber c; _ } ->
        let b = parse_int_const c in
        if b < 1 then
          failwith
            ("codegen: DO TO bound below 1 unproven [TBD] (DR switches to a \
             general XRA A/CMP M/INX H/SBB M signed compare for `to 0' \
             [R1029], which is not in the banked subset)");
        let head = st.lc in
        d st op_lhld; reloc st Data iaddr;
        st.last_imm <- None;   (* LHLD clobbers HL *)
        (* [E2E-8] the body is re-entered by the back-edge, so HL knowledge from
     the init/test is dead at body entry: DR's constant-store reuse is
     control-flow sensitive [IFACT line 11 `F = 1' gets LXI H,0001 even though
     the loop init executed LXI H,0000 just before] *)
  st.last_imm <- None;
  (* [E2E-8] the exit test compares the index against a constant:
           rising  -> c = bound + 1, skip when index >= bound+1  (JP)
           falling -> c = bound,     skip when index <  bound    (JM)
           [R1011 to 5 by 2 -> LXI B,FFFA; R1012/R1013 by -1/-2 -> DCX rungs;
            R1023/R1024 rising bound 1/2 -> 2/3 DCX rungs; R1025/R1026 rising
            bound 3/4 -> LXI B,-(b+1); R1027 to 20 by -1 -> LXI B,-20 + JM]
           The subtraction is peeled by size: c rung instructions when the
           ladder is strictly cheaper than LXI B + DAD B (4 bytes), i.e. c<=3. *)
        let cc = if step > 0 then b + 1 else b in
        if cc <= 3 then
          for _ = 1 to cc do d st op_dcx_h done
        else begin
          let neg = -cc in
          d st op_lxi_b; d st (neg land 0xff);
          d st ((neg lsr 8) land 0xff);
          d st op_dad_b
        end;
        d st op_mov_a_h; d st op_ora_a;
        d st (if step > 0 then op_jp else op_jm);
        let slot = st.lc in          (* OPERAND pos [Y301: 0x16] *)
        d st 0; d st 0;
        (head, slot)
    | Some { Ast.e = Ast.Eident bn; _ } ->
        (match vk_of st bn.Ast.orig with
         | Vint -> ()
         | _ -> failwith "codegen: DO bound not fixed-bin [TBD]");
        let auto_end =
          List.fold_left
            (fun a (_, (vi : var_info)) -> max a (vi.off + vi.size))
            0 st.vars
        in
        let temp =
          st.base + max auto_end st.floor + 2 * st.temps
        in
        st.temps <- st.temps + 1;
        d st op_lhld; reloc st Data (addr_of st bn.Ast.orig);
        do_bound_deref st d bn.Ast.orig;   (* [DO1] formal bound [E2E-22/P4] *)
        d st op_shld; reloc st Data temp;
        let head = st.lc in
        d st op_lhld; reloc st Data temp;
        d st op_xchg;
        d st op_lhld; reloc st Data iaddr;
        call_ext st "?IS22N";
        d st op_jm;
        let slot = st.lc in          (* OPERAND pos [Y302] *)
        d st 0; d st 0;
        (head, slot)
    | Some _ -> failwith "codegen: DO complex bound unproven [TBD]"
    | None -> failwith "codegen: DO without TO deferred [TBD]"
  in
  lo st ls body;
  d st op_lhld; reloc st Data iaddr;
  (* [E2E-8] |step| rungs in the step's direction [R1011 by 2 -> 2 INX H;
     R1013 by -2 -> 2 DCX H; R1012/R1033 by -1 -> 1 DCX H] *)
  for _ = 1 to ak do d st (if step > 0 then op_inx_h else op_dcx_h) done;
  d st op_shld; reloc st Data iaddr;
  (d st op_jmp; st.last_imm <- None (* [R723] branch boundary *));
  reloc st Code head;   (* helper advances LC [Y301] *)
  emit_triple st jpslot st.lc;
  st.last_imm <- None
  end

(* numeric item print width: max of IDENT-leaf widths [N301-N305];
   constant-only expressions have no DR evidence -> [TBD] *)
let num_width st (x : Ast.expr) =
  let rec w e =
    match e.Ast.e with
    | Ast.Eident n ->
        (match vk_of st n.Ast.orig with
         | Vint ->
             (List.assoc (String.lowercase_ascii n.Ast.orig) st.vars).w
         | _ -> failwith "codegen: char var in numeric PUT item [TBD]")
    | Ast.Ebinary (_, l, r) -> max (w l) (w r)
    | Ast.Eprefix (_, x) -> w x
    (* [E2E-20] an ARRAY ELEMENT in a PUT item: DR's form is the ordinary scalar one with
       the element address, RD1 `put skip list(a(3))' -> `LHLD A A(0000)+0004 / MVI A,09 /
       ?QICOP / ?PNVOP / ?QIOOP' [golden/e2e225/RD1] -- identical to a scalar PUT except for
       the operand, which my guarded read case already produces.  The WIDTH is the array
       row's own declared width (2-byte FIXED => 9), taken from the binder row rather than
       assumed.  Resolution still goes through resolve_suffix, so there is one authority. *)
    | Ast.Esuffix (hd, [ _ ]) ->
        let hn =
          match hd.Ast.e with
          | Ast.Eident h -> String.lowercase_ascii h.Ast.orig
          | _ -> ""
        in
        (match hd.Ast.e with
         | Ast.Eident h
           when List.exists
                  (fun (n, _lb, _ub, _ez) ->
                    String.equal n (String.lowercase_ascii h.Ast.orig))
                  st.arrays ->
             (try (List.assoc (String.lowercase_ascii h.Ast.orig) st.vars).w
                  with Not_found ->
                    failwith
                      "codegen: [TBD] array element PUT item: array row missing [C164]")
         | _ ->
             if List.mem_assoc hn st.procs then
          (* result of a RETURNS FIXED procedure: default bin(15)
             width [HYPOTHESIS for returns BIN(p): no evidence yet] *)
             9
             else failwith "codegen: PUT numeric item form unproven [TBD]")
    | Ast.Enumber _ -> 0
    | _ -> failwith "codegen: PUT numeric item form unproven [TBD]"
  in
  let r = w x in
  if r = 0 then
    failwith "codegen: constant-only PUT numeric item unproven [TBD]"
  else r

(* General PUT LIST item chain [N301-N306]: preamble; optional skip
   (bare = 1, skip(n)); per item: literal = LXI H,*S; MVI A,len;
   SLCTS; PNCOP; numeric (var/expr) = <HL>; MVI A,width; QICOP;
   PNVOP; single char/varying var = the V101/V106 chain (multi-item
   char vars UNPROVEN -> [TBD]); then ONE QIOOP + continuation. *)
let lower_put_items_gen st (edit_tbl : int option)
    (skipn : put_skip) (items : pitem list) =
  (* [E2E-8] `~edit_tbl' turns the same per-item value preparation into PUT
     EDIT: the table is loaded and ?EDITF called right after ?SYSPR, and every
     item's output tail becomes ?EDTOV instead of ?PNCOP/?PNVOP [IFACT,
     R1001-R1020].  PUT LIST keeps the byte-frozen path (edit_tbl = None). *)
  let is_edit = edit_tbl <> None in
  (* `tail keep_going ()': keep_going = true selects ?PNCOP (character item,
     cursor continues), false selects ?PNVOP (numeric); for PUT EDIT every
     tail is ?EDTOV regardless [R1001-R1020]. *)
  let tail keep_going () =
    call_ext st (if is_edit then "?EDTOV"
                 else if keep_going then "?PNCOP" else "?PNVOP")
  in
  (* [G112/N18-era perimeter] a char-varying item in a MULTI-item PUT LIST is
     unsampled and stays refused.  [E2E-8] PUT EDIT DOES sample it --
     R1020 `put edit(c, i)(a(3), f(2,1), skip)' puts varying+barying ... i.e.
     char varying next to a binary variable -- so the guard applies to the LIST
     path only. *)
  let char_var_ok =
    is_edit || List.length items = 1 ||
    not (List.exists (function PIvar n ->
                        (match vk_of st n.Ast.orig with
                         | Vint -> false | Vdec _ -> false | Vflt -> false
                         | _ -> true)
                      | _ -> false) items)
  in
  if not char_var_ok then
    failwith "codegen: char var in multi-item PUT unproven [TBD]";
  d st op_lxi_d; d st 0x52; d st 0x02;
  d st op_lxi_b;
  let bslot = st.lc in
  d st 0; d st 0;
  call_ext st "?SYSPR";
  (match skipn with
   | Sk_lit c ->
       let n = parse_int_const c in
       if n <= 0 || n > 255 then
         failwith "codegen: skip count out of MVI range [TBD]";
       d st op_mvi_a; d st n; call_ext st "?SKPOP"
   | Sk_expr e -> emit_skip_count st e   (* [SK3 SK4] LHLD / MOV A,L / CALL ?SKPOP *)
   | Sk_none -> ());
  (match edit_tbl with
   | Some addr ->
       (* the table was allocated by prealloc_fmt_tables, ahead of every
          non-table pool item [R1003/R1021/R1022] *)
       d st op_lxi_h; reloc st Data addr; call_ext st "?EDITF"
   | None -> ());
  List.iter
    (fun it ->
      match it with
      | PIlit v ->
          let len = String.length v in
          if len > 255 then failwith "codegen: literal > 255 [TBD]";
          (* [E2E-15/C152] the PUT-LIST literal path -- the one MB40 actually exercises. *)
          let addr = pool_str st (pool_bytes v) in
          d st op_lxi_h; reloc st Data addr;
          d st op_mvi_a; d st len;
          call_ext st "?SLCTS"; tail true ()
      | PIvar n ->
          (match vk_of st n.Ast.orig with
           | Vflt ->
               (* [E2E-10] float variable item: LXI H,var; MVI A,0E; ?QFCMS.
                  0E = 14 is a CONSTANT width in every sample, not a
                  precision [R3030, R3037, R3045: three float vars in one
                  PUT LIST, each with MVI A,0E] *)
               if is_edit then
                 failwith
                   "codegen: PUT EDIT of a FLOAT item is unsampled [TBD] (no DR sample puts a float through an edit list)";
               if List.mem (String.lowercase_ascii n.Ast.orig) st.deref then
                 failwith
                   "codegen: PUT LIST of a FLOAT formal is unsampled [TBD] (R3038 reads a float formal inside an expression, never prints it through its pointer cell)";
               d st op_lxi_h; reloc st Data (addr_of st n.Ast.orig);
               d st op_mvi_a; d st 14; call_ext st "?QFCMS"; tail false ()
           | Vdec (p, s) ->
               if List.mem (String.lowercase_ascii n.Ast.orig) st.deref then
                 failwith
                   ("codegen: PUT LIST of a FIXED DECIMAL formal is unsampled "
                    ^ "[TBD] (no DR sample outputs a decimal through its "
                    ^ "pointer cell)");
               (* [R501/R502/R503/R508/R510/R511] DEC variable item = DLDOP
                  then QDCOP(width=p+3, scale=s); R506 proves a DEC var in a
                  MULTI-item list next to an INT var *)
               d st op_lxi_h; reloc st Data (addr_of st n.Ast.orig);
               d st op_mvi_a; d st p; call_ext st "?DLDOP";
               if is_edit then
                 failwith "codegen: PUT EDIT of a FIXED DECIMAL item is \
                           unsampled [TBD] (no DR sample passes a DEC item \
                           through an edit list)";
               d st op_mvi_a; d st (p + 3); d st op_mvi_b; d st s;
               call_ext st "?QDCOP"; tail false ()
           | Vint ->
               let vi =
                 List.assoc (String.lowercase_ascii n.Ast.orig) st.vars
               in
               lower_hl st { Ast.e = Ast.Eident n;
                             Ast.epos = n.Ast.pos };
               d st op_mvi_a; d st vi.w;
               call_ext st "?QICOP"; tail false ()
           | vk ->
               (* single-item char var = the banked V101/V106 chain *)
               (match vk with
                | Vvar _ ->
                    d st op_lxi_h; reloc st Data (addr_of st n.Ast.orig);
                    call_ext st "?SLVTS"
                | Vfix cap ->
                    if cap > 255 then failwith "codegen: cap > 255 [TBD]";
                    d st op_lxi_h; reloc st Data (addr_of st n.Ast.orig);
                    d st op_mvi_a; d st cap; call_ext st "?SLCTS"
                | Vint -> assert false
                (* [E2E-11 step 1a] a BIT(1) variable in a PUT list: DR has no
                   sample here (E20A/E20B/E20D/E20E never print a bit cell), and
                   falling into the inner match would raise Match_failure
                   instead of a readable refusal.  Refuse explicitly. *)
                | Vbit1 ->
                    failwith
                      "codegen: PUT of a BIT(1) variable is unsampled [TBD]                        (no DR sample puts a bit string; the bit-list output                         edit form is E2E-11 step 3 territory)");
               tail true ())
      | PInum x ->
          if is_float_expr st x then begin
            (* [E2E-10/FFACT] a float call item leaves its result on the
               float stack and the edit pair MVI A,0E / ?QFCSS follows the
               CALL directly.  Other float shapes have no PUT sample. *)
            (match (unwrap_e x).Ast.e with
             | Ast.Esuffix _ -> ()
             | _ ->
                 failwith
                   "codegen: PUT LIST of a computed FLOAT expression is unsampled [TBD] (FFACT pins only a float CALL result: descriptor, CALL, MVI A,0E, ?QFCSS)");
            ignore (fl_push st x);
            d st op_mvi_a; d st 14; call_ext st "?QFCSS"; tail false ()
          end else if is_dec_expr st x then begin
            (* [DFACT] a DEC function-call item leaves its result on the
               decimal stack; the edit pair follows directly *)
            let (p, s) = dec_edit_pt st x in
            ignore (dec_push st None x);
            if is_edit then
              failwith "codegen: PUT EDIT of a FIXED DECIMAL item is unsampled \
                        [TBD] (no DR sample passes a DEC item through an edit \
                        list)";
            d st op_mvi_a; d st (p + 3); d st op_mvi_b; d st s;
            call_ext st "?QDCOP"; tail false ()
          end else begin
            lower_hl st x;
            d st op_mvi_a; d st (num_width st x);
            call_ext st "?QICOP"; tail false ()
          end)
    items;
  call_ext st "?QIOOP";
  emit_triple st bslot st.lc

(* the byte-frozen PUT LIST entry point: no format table, so every item's
   output tail is ?PNCOP/?PNVOP as before [G107/G108, N301-N306, R506]. *)
let lower_put_items st (skipn : put_skip) (items : pitem list) =
  lower_put_items_gen st None skipn items

(* pop the next pre-allocated format-table address [E2E-8] *)
let take_fmt_addr st =
  match st.fmtq with
  | a :: rest -> st.fmtq <- rest; a
  | [] -> failwith "codegen: PUT EDIT format table not pre-allocated [TBD]" 

(* statement lowering with label/goto resolution *)
(* [E2E-5c P401] internal procedure block: forward-call resolution,
   deref prologue, scoped body lowering. Recursive procedures and
   bare-BEGIN blocks stay [TBD]. *)
let rec lower_proc st (ls : lblstate) (bs : Ast.block_stmt) =
  let pb = bs.Ast.blk in
  let nm =
    match pb.Ast.bname with
    | Some n -> String.lowercase_ascii n.Ast.orig
    | None -> failwith "codegen: procedure without name [TBD]"
  in
  let pl =
    match List.assoc_opt nm st.procs with
    | Some p -> p
    | None ->
        failwith "codegen: BEGIN-block/procedure lowering deferred [TBD]"
  in
  (* [R404/R405/R406/R423/R429/R432/P404] TAIL GUARD: emitted at the
     append address BEFORE the entry label / forward-call chain /
     prologue; see the guard_slots field comment for the full rule.
     Evaluated once per program (the first appended proc). *)
  if (not st.in_proc) && not st.top_proc && not st.stop_seen
       && not st.after_forever
  then begin
    if st.guards = 0 then begin
      st.guards <- st.guards + 1;
      (d st op_jmp; st.last_imm <- None (* [R723] branch boundary *));
      st.guard_slots <- st.lc :: st.guard_slots;
      d st 0; d st 0
    end
    else
      (* A SECOND appended proc in a guarded shape is unproven: no
         golden has two top-level procedures. Refuse rather than
         extrapolate DR's behavior. *)
      failwith
        "codegen: second appended procedure after a tail guard \
         [TBD] unproven, no multi-procedure golden]"
  end;
  if not st.in_proc && not st.top_proc then st.appended <- true;
  (* entry label [P401 'dbl:' — blabel from parse_proc_block] *)
  (match pl.Bind.pl_lbl with
   | Some l ->
       ls.labs <- (l, st.lc) :: ls.labs;
       let slots =
         List.filter (fun (k, _) -> k = l) ls.fwd |> List.map snd
       in
       ls.fwd <- List.filter (fun (k, _) -> k <> l) ls.fwd;
       (match slots with
        | [] -> ()
        | [ one ] -> link st t_chain_addr (Some (Code, one)) None
        | _ ->
            failwith
              "codegen: multiple forward GOTO per label chain \
               unproven [TBD]")
   | None -> ());
  (* resolve pending forward CALLs at the entry byte [P401 @1285] *)
  let hits = List.filter (fun (k, _) -> k = nm) st.fcalls in
  st.fcalls <- List.filter (fun (k, _) -> k <> nm) st.fcalls;
  (* [E2E-11/CALL, C123] ONE chain record per procedure regardless of how many
     forward sites it has, targeting the LAST site's operand word [E27A: three
     sites at 0018/001E/0024 -> chain on 0024; E25F: two -> chain on 001A; and
     with a single site the last IS that site, which is the shape every accepted
     specimen before this used].  The earlier sites reach the entry through the
     RELOC chain emitted at each call site. *)
  (match hits with
   | [] -> ()
   | _ ->
       let last = List.fold_left (fun m (_, a) -> max m a) 0 hits in
       link st t_chain_addr (Some (Code, last)) None);
  st.entries <- (nm, st.lc) :: st.entries;
  (match pl.Bind.pl_ptrs with
   | [ (_f, ptr) ] ->
       if pl.Bind.pl_rec then begin
         (* recursive activation [RFACT @56-6D: LXI B,8; LXI D,10;
            CALL ?SVBLK; deref; SHLD ptr@10; LHLD ptr; deref;
            SHLD shadow@12. P402 @2C-40 identical shape with
            B=8,D=6. Sizes from the layout section (4 cells x 2B
            incl. the self-call slot+temp) [R427 re-check] *)
         let (bb, bsz) =
           match
             List.filter_map
               (fun (n, b, sz) -> if n = nm then Some (b, sz) else None)
               st.secs
           with
           | [ x ] -> x
           | _ -> failwith "codegen: proc section missing [TBD]"
         in
         d st op_lxi_b; d st (bsz land 0xff);
         d st ((bsz lsr 8) land 0xff);
         d st op_lxi_d;
         reloc st Data (bb + st.base);
         call_ext st "?SVBLK";
         d st 0x5e; d st 0x23; d st 0x56; d st 0xeb;
         d st op_shld; reloc st Data (ptr + st.base);
         d st op_lhld; reloc st Data (ptr + st.base);
         d st 0x5e; d st 0x23; d st 0x56; d st 0xeb;
         let shad_off =
           match
             List.find_opt
               (fun (k, _rt, _o) ->
                 k = String.lowercase_ascii (fst (List.hd pl.Bind.pl_ptrs)))
               pl.Bind.pl_rows
           with
           | Some (_k, _rt, o) -> o
           | None ->
               failwith "codegen: recursive formal without dcl [TBD]"
         in
         d st op_shld; reloc st Data (shad_off + st.base)
       end else begin
         (* callee prologue [P401 dbl @29]: arg address arrives in HL *)
         d st 0x5e; d st 0x23; d st 0x56; d st 0xeb;
         d st op_shld; reloc st Data (ptr + st.base)
       end
   | [] when pl.Bind.pl_rec ->
       failwith "codegen: recursive procedure without formals [TBD]"
   | [] -> ()
   | ((f0, ptr0) :: rest) ->
       (* [E2E-9] MULTI-argument callee.  DR copies the whole descriptor
          block into the callee's contiguous pointer cells with a counted
          byte loop, HL = the descriptor address the caller left there:
              LXI D,<first ptr cell>     (destination, 2N bytes wide)
              MVI C,2N
          loop: MOV A,M / INX H / STAX D / INX D / DCR C / JNZ loop
          The back edge is an INLINE RELOC(code,loop) [R2001 @1606 -> 003E,
          R2012 JNZ 0063].  Sampled byte-exactly with 2, 3 and 4 formals
          [R2001/R2002/R2005/R2008/R2012/R2013] and with FIXED DECIMAL
          formals [DECPOLY, MVI C,06].

          NO ?SVBLK appears here even for a RECURSIVE multi-formal procedure
          [R2008 rec(a,b) self-calls with a plain block copy], so the
          SVBLK trigger stays the written RECURSIVE ATTRIBUTE plus arity 1;
          attributed multi-formal recursion has no golden and refuses. *)
       let n = 1 + List.length rest in
       ignore f0;
       if pl.Bind.pl_attr_rec then
         failwith
           ("codegen: attributed RECURSIVE multi-formal activation unproven " ^
            "[TBD] (only unattributed recursion is sampled at arity >1 " ^
            "[R2008]; DR's SVBLK shape there has no golden)");
       d st op_lxi_d;
       reloc st Data (ptr0 + st.base);
       d st 0x0e; d st (2 * n);          (* MVI C,2N *)
       let loop = st.lc in
       d st 0x7e;                          (* MOV A,M *)
       d st 0x23;                          (* INX H   *)
       d st 0x12;                          (* STAX D  *)
       d st 0x13;                          (* INX D   *)
       d st 0x0d;                          (* DCR C   (0x05 would be DCR B) *)
       d st op_jnz; reloc st Code loop);
  let saved = st.vars and savedd = st.deref in
  (* [E2E-20] the callee's OWN array metadata must replace the caller's for the duration of
     this scope, exactly as st.vars does.  Without it a subscripted name inside a procedure is
     resolved against the CALLER's block: the name may be absent (so an element falls into the
     call route or a [TBD] refusal) or, worse, PRESENT with a different lb/ub/element size, in
     which case the relocated operand would be a silent wrong address -- the C139/C162/C167
     class.  The list comes from the same proc_layout record that supplies pl_rows, so there is
     still one sizing authority (Bind). *)
  let saveda = st.arrays in
  st.vars <-
    List.map
      (fun (n, rt, o) ->
        (n,
         match rt with
         | Bind.RTbin p ->
             if p > 15 then
               failwith "codegen: FIXED BIN(>15) NOT IMP [TBD]"
             else
               { off = o; size = Bind.bytes_of rt; vk = Vint;
                 w = binw (if p <= 0 then 15 else p) }
         | Bind.RTdec (p, s) ->
             if p > 15 || p < 1 || s < 0 || s > p then
               failwith
                 (Printf.sprintf
                    "codegen: procedure-local FIXED DEC(%d,%d) outside the \
                     probed DEC band [TBD]" p s)
             else if
               List.mem_assoc (String.lowercase_ascii n) pl.Bind.pl_ptrs
             then
               (* [R709/R725, DECPOLY, R2037/R2038] DR passes a FIXED
                  DECIMAL formal BY REFERENCE: the formal owns a 2-BYTE
                  pointer cell (not the ceil((p+1)/2) BCD cell), and every
                  READ is `LHLD <ptr> ; MVI A,digits ; CALL ?DLDOP`, i.e. HL
                  arrives at ?DLDOP as the ADDRESS of the caller's decimal
                  [DECPOLY @10D: LHLD X A(004E) / MVI A,0F / CALL ?DLDOP].
                  Writes to a decimal formal have no golden and refuse in
                  lower_assign / the GET / PUT-EDIT paths. *)
               { off = o; size = 2; vk = Vdec (p, s); w = p + 3 }
             else
               { off = o; size = Bind.bytes_of rt; vk = Vdec (p, s);
                 w = p + 3 }
         | Bind.RTfloat p ->
             if p <> 24 then
               failwith
                 (Printf.sprintf
                    "codegen: procedure-local FLOAT BINARY(%d) precision unsupported [TBD] (only BINARY(24) is characterized)" p)
             else if
               List.mem_assoc (String.lowercase_ascii n) pl.Bind.pl_ptrs
             then
               (* [E2E-10/R3038] a FLOAT formal is passed BY REFERENCE exactly
                  like a decimal one: a 2-byte pointer cell, and every read is
                  `LHLD <cell>` used directly as the operand address
                  [R3038: LHLD Q A(0032) / PUSH H / LHLD Q A(0032) / POP D /
                  CALL ?FM44M].  Writes have no sample. *)
               { off = o; size = 2; vk = Vflt; w = 0 }
             else
               { off = o; size = Bind.bytes_of rt; vk = Vflt; w = 0 }
         | _ ->
             failwith "codegen: non fixed-bin procedure local [TBD]"))
      pl.Bind.pl_rows @ saved;
  st.arrays <- pl.Bind.pl_arrays @ saveda;
  (if pl.Bind.pl_rec
     && List.exists
          (fun (n, rt, _) ->
            match rt with
            | Bind.RTfloat _ ->
                List.mem_assoc (String.lowercase_ascii n) pl.Bind.pl_ptrs
            | _ -> false)
          pl.Bind.pl_rows
   then
     failwith
       "codegen: a FLOAT formal of a RECURSIVE procedure is unsampled [TBD] (R3103 shows DR copying the caller's 4-byte float into the callee's DECLARED formal cell at body entry -- `LXI H,X A(0010) / PUSH H / LHLD X A(000E) / XCHG / POP H / LXI B,0004 / CALL <copy>` -- the recursive shadow-value path the FIXED formals already use [P402, and R3104 is byte-exact for the fixed case].  My recursive lowering has no sample of that float copy, and emitting the non-recursive LHLD deref instead would be silently wrong: R3103's addresses all match and only this prologue is missing, which is exactly the kind of near-miss that must refuse)");
  st.deref <-
    (* recursive bodies read the SHADOW value cell with plain ladders
       [RFACT @80: LHLD I(12); DCX H — no deref] *)
    (if pl.Bind.pl_rec then [] else List.map fst pl.Bind.pl_ptrs);
  let savedp = st.in_proc and savedr = st.in_rec
      and saveddr = st.dec_ret and savedfr = st.float_ret in
  st.dec_ret <-
    (match pl.Bind.pl_ret with
     | Some (Bind.RTdec (p, s)) -> Some (p, s)
     | _ -> None);
  (* [E2E-10] RETURNS FLOAT selects the ?FPRET exit [R3038, FFACT] *)
  st.float_ret <-
    (match pl.Bind.pl_ret with Some (Bind.RTfloat _) -> true | _ -> false);
  st.in_proc <- true;
  st.in_rec <- pl.Bind.pl_rec;
  List.iter (fun x -> lower_stmt st ls x) pl.Bind.pl_body;
  (* [E2E-11/CALL] a procedure with NO RETURNS gets an implicit `RET` after its
     body.  Eight probes pin this and none of them contradict it: E25A (empty
     body -> RET is the body's ONLY instruction), E24A/E24F/E25H (assignment or
     call last), E25G (label then assignment), E25B/E25E (body ends inside an
     IF / a DO WHILE, RET follows the branch), E25D (the subroutine s1 gets it
     while the value-returning f, which already exited through RETURN's own
     RET, gets no second one).  So the trigger is the absence of RETURNS, not
     the shape of the last statement.  Value-returning procedures are NOT given
     one: their exits are RETURN's RET / JMP ?FPRET / JMP ?DCRET. *)
  if pl.Bind.pl_ret = None && not (st.top_proc && st.stop_seen) then begin
    d st 0xc9; (* RET *)
    st.last_imm <- None
  end else
    (* [E2E-11 step 5 / Q6, golden/e2e148] a procedure-only MODULE whose body
       ends in STOP gets NO trailing RET: DR's Q6 is
         ... INX H / XCHG / MOV M,D / DCX H / MOV M,E / CALL ?STOPX
       and DEF-CODE-SIZE 0016 lands right on the CALL operand's second byte --
       one byte less than my unconditional implicit RET produced.  The eight
       no-RETURNS probes above (E25A/E24A/E25D ...) contain no STOP, so this is
       a NEW condition, and it is deliberately scoped to the module shape that
       Q6 pins: whether a NESTED procedure ending in STOP also loses its RET is
       unprobed, so nested lowering keeps the byte it has always emitted. *)
    ()
  ;
  st.dec_ret <- saveddr;
  st.float_ret <- savedfr;
  st.in_rec <- savedr;
  st.in_proc <- savedp;
  st.vars <- saved;
  st.deref <- savedd;
  st.arrays <- saveda
and lower_stmt st (ls : lblstate) (s : Ast.stmt) =
  (* label prefixes resolve at the STATEMENT's LC [G115 loop:/done:] *)
  List.iter
    (fun (l : Ast.name) ->
      let nm = String.lowercase_ascii l.Ast.orig in
      ls.labs <- (nm, st.lc) :: ls.labs;
      let slots = List.filter (fun (k, _) -> k = nm) ls.fwd |> List.map snd in
      ls.fwd <- List.filter (fun (k, _) -> k <> nm) ls.fwd;
      match slots with
      | [] -> ()
      | [ one ] ->
          (* forward GOTO resolution: CHAIN-ADDR at label position [G115] *)
          link st t_chain_addr (Some (Code, one)) None
      | _ -> failwith "codegen: multiple forward GOTO per label chain                        unproven [TBD]")
    s.Ast.slabels;
  (* [E2E-11/CALL, E25G] a LABEL definition also ends HL-CONSTANT REUSE.  In
     E25G `t = 1; jmp: t = 2;` stores 1 with LXI H,0001/SHLD T, and AFTER the
     label DR reloads `LXI H,0002` rather than reusing HL with one INX H --
     mine reused and came out 3 bytes short of DR's SHLD.  This is the same
     boundary rule as [R723] (a branch kills the loaded constant), and a label
     is exactly where a GOTO can land, so HL is not known there.

     Gated on `slabels <> []`: this reset used to be unconditional, which
     silently disabled HL-constant reuse for EVERY statement and broke E24J
     (byte-identical DATA, one relocation record shifted). *)
  if s.Ast.slabels <> [] then st.last_imm <- None;
  match s.Ast.st with
  | Ast.Sassign { lhs; rhs } ->
      st.lowered <- st.lowered + 1; lower_assign st lhs rhs
  | Ast.Sput _ ->
      st.lowered <- st.lowered + 1; st.last_imm <- None;
      (match match_put_edit s with
       | Some (its, specs) ->
           (* [E2E-8] PUT EDIT: the PUT LIST machinery plus the compiled format
              table (?EDITF) and ?EDTOV after every item [IFACT, R1001-R1020]. *)
           ignore specs;
           lower_put_items_gen st (Some (take_fmt_addr st)) Sk_none its
       | None ->
      (match match_put_list_lit s with
       | Plit (skipn, v) -> lower_put_lit st skipn v
       | Pcat (skipn, ch) -> lower_cat st skipn ch
       | Pitems (sk, its) -> lower_put_items st sk its
       | Pnone -> failwith
             (Printf.sprintf
                "codegen: PUT form not in E2E-3a subset [TBD] \
                 (line %d)" s.Ast.spos.Source.line)))
  | Ast.Sget _ ->
      st.lowered <- st.lowered + 1; st.last_imm <- None;
      (match match_get_list_var s with
       | Some nm -> lower_get st nm
       | None -> failwith
             (Printf.sprintf
                "codegen: GET form not in E2E-3e subset [TBD] \
                 (line %d)" s.Ast.spos.Source.line))
  | Ast.Sdowhile { cond; body } ->
      st.lowered <- st.lowered + 1; st.last_imm <- None;
      (* while(...) conditions arrive Econd-wrapped (IF conds don't) *)
      let cond = match cond.Ast.e with
                 | Ast.Econd x -> x
                 | _ -> cond
      in
      let head = st.lc in
      st.last_imm <- None;   (* [E2E-8] branch target => HL unknown *)
      if cond.Ast.e = Ast.Ebit "1" then begin
        (* constant-true bit condition = pure forever, NO test
           [Z404: COPY's DO WHILE('1'B)] *)
        lower_stmt st ls body;
        (d st op_jmp; st.last_imm <- None (* [R723] branch boundary *)); reloc st Code head;
        if not st.in_proc then begin
          (* WHILE('1'B): no test insn; tail address = the JMP
             operand address [head+4] [R408] *)
          st.after_forever <- true;
          st.last_loop_edge <- head + 4
        end
      end else begin
        let slot = lower_test_skip st cond in
        st.last_imm <- None;   (* [E2E-8] branch target => HL unknown *)
        lower_stmt st ls body;
        (d st op_jmp; st.last_imm <- None (* [R723] branch boundary *)); reloc st Code head;
        emit_triple st slot st.lc            (* [Z401: after JMP] *)
      end
  | Ast.Sdoforever body ->
      (* bare DO; .. END; [Z403] body then unconditional JMP back *)
      st.lowered <- st.lowered + 1; st.last_imm <- None;
      let head = st.lc in
      lower_stmt st ls body;
      (d st op_jmp; st.last_imm <- None (* [R723] branch boundary *)); reloc st Code head
  | Ast.Sdoto { ind; from; by; to_; while_; rep; body } ->
      st.lowered <- st.lowered + 1;
      (* open the suppression window at the TAIL ADDRESS before the
         loop lowers, so the increment's own evaluation position is
         visible [R414/R426: const-ident tail rungs] *)
      let window_open =
        st.after_forever && not st.in_proc
        && st.lc = st.last_loop_edge
      in
      let forever =
        match (to_, while_, rep, by) with
        | (None, None, Some _, _) -> true
        (* [E2E-8] DO index = c BY k; -- forever WITH a step [IFACT].  WITHOUT
           a step there is no loop at all [R1032], so no window. *)
        | (None, None, None, Some _) -> true
        | _ -> false
      in
      if forever && not st.in_proc then begin
        (* suppression window: tail address = where the loop's
           back-edge will end — the loop emits its 3-byte
           (LHLD + operand | LXI + imm) increment first, so the
           edge = lc after the increment [RFACT 0x4C, R414/R426
           0x1C, R401 0x1C, R427 0x1D] *)
        if not window_open then st.after_forever <- true;
        let inc_sz =
          match (by, to_) with
          | (None, None) -> 2 + 2 + 2   (* static bound triple *)
          | _ -> 19 / 8 land 0xff * 0 + 5
        in
        let inc_sz =
          match to_ with
          | Some { Ast.e = Ast.Enumber _; _ } -> 2 + 2 + 2
          | Some _ -> 5 + 2               (* dynamic: LHLD+SHLD temp *)
          | None -> 3 + 2                 (* increment LHLD + INX H
                                             (+INX for k=2: +1) *)
        in
        let k =
          match rep with
          | Some { Ast.e = Ast.Ebinary (Ast.Add, _,
                     { Ast.e = Ast.Enumber ck; _ }); _ } ->
              (try int_of_string (String.concat ""
                    (String.split_on_char '_' ck))
               with _ -> 1)
          | _ -> 1
        in
        st.last_loop_edge <- st.lc + 9 + 2 * k
      end;
      lower_doto st ls (fun st ls s -> lower_stmt st ls s)
        ind from by to_ while_ rep body
  | Ast.Sif { cond; then_; els } ->
      st.lowered <- st.lowered + 1; st.last_imm <- None;
      let skip = lower_test_skip st cond in
      lower_stmt st ls then_;
      (match els with
       | None -> emit_triple st skip st.lc
       | Some e ->
           (d st op_jmp; st.last_imm <- None (* [R723] branch boundary *));
           let exit_slot = st.lc in
           d st 0; d st 0;
           emit_triple st skip st.lc;      (* skip -> else start [G114] *)
           lower_stmt st ls e;
           emit_triple st exit_slot st.lc) (* fall-around else -> exit *)
  | Ast.Sgoto { tgt; subscript = [] } ->
      st.lowered <- st.lowered + 1; st.last_imm <- None;
      let nm = String.lowercase_ascii tgt.Ast.orig in
      (match List.assoc_opt nm ls.labs with
       | Some a -> (d st op_jmp; st.last_imm <- None (* [R723] branch boundary *)); reloc st Code a        (* backward [G115] *)
       | None ->
           (d st op_jmp; st.last_imm <- None (* [R723] branch boundary *));
           let slot = st.lc in
           d st 0; d st 0;
           ls.fwd <- (nm, slot) :: ls.fwd)              (* forward [G115] *)
  | Ast.Sgoto _ ->
      failwith "codegen: computed GOTO deferred [TBD]"
  | Ast.Sdobegin ss ->
      st.lowered <- st.lowered + 1;
      List.iter (fun x -> lower_stmt st ls x) ss
  | Ast.Sproc bs ->
      st.lowered <- st.lowered + 1; st.last_imm <- None;
      lower_proc st ls bs
  | Ast.Sreturn eo ->
      st.lowered <- st.lowered + 1; st.last_imm <- None;
      if st.float_ret then begin
        (* [E2E-10] a FLOAT function's exit.  A literal or cell result is
           pushed onto the float stack with ?FX44S; a computed one is already
           there.  Then ?RSBLK when the activation is recursive, then
           JMP ?FPRET.  Both halves are sampled: R3038 (nested, NOT
           recursive: no RSBLK) and FFACT (recursive: RSBLK on both exits). *)
        (match eo with
         | Some e -> fl_return_push st (fl_push st e)
         | None -> failwith "codegen: RETURN without value [TBD]");
        if st.in_rec then call_ext st "?RSBLK";
        d st op_jmp;
        st.last_imm <- None;
        let slot = st.lc in
        d st 0; d st 0;
        link st t_chain_ext (Some (Code, slot)) (Some "?FPRET")
      end else
      (match st.dec_ret with
       | Some ((_p, _s) as ps) ->
           (* [E2E-6/DFACT, R509] a DEC function returns the top of the
              decimal stack via JMP ?DCRET (not RET).  Base case of DFACT:
              LXI H,*S(000C); MVI A,0F; CALL ?DLDOP; CALL ?RSBLK;
              JMP ?DCRET -- the target-precision literal is exactly the
              dec_push rule used for assignments *)
           (match eo with
            | Some e -> ignore (dec_push st (Some ps) e)
            | None -> failwith "codegen: RETURN without value [TBD]");
           if st.in_rec then call_ext st "?RSBLK";
           (d st op_jmp; st.last_imm <- None (* [R723] branch boundary *));
           let slot = st.lc in
           d st 0; d st 0;
           link st t_chain_ext (Some (Code, slot)) (Some "?DCRET")
       | None ->
           (match eo with
            | Some e -> lower_hl st e
            | None -> failwith "codegen: RETURN without value [TBD]");
           (* every exit of a RECURSIVE activation restores its saved
              block first [RFACT: RSBLK @7C base-case AND @95 recursive] *)
           if st.in_rec then call_ext st "?RSBLK";
           d st 0xc9 (* RET [P401 code@41] *) )
  | Ast.Sstop eo ->
      st.lowered <- st.lowered + 1; st.last_imm <- None;
      (match eo with
       | Some _ -> failwith "codegen: STOP(code) deferred [TBD]"
       | None -> ());
      (* stop; sitting at the epilogue/proc append address (immediately
         after a no-exit loop, RFACT @0056) is NOT emitted when
         procedure code follows: the CALL ?STOPX cannot fit below
         appended procs [RFACT/R407/R408/R411/R415?? R415 HAS no
         procs -> emitted ✓; R401/R414/R419/R420/R423 anchored by
         intervening live stmts -> emitted ✓; R410/R421/R422/R424/
         R425 any proc (rec or not, call or not) -> suppressed ✓] *)
      (* [R415/R418/R414/R426 vs R401/R419/R423/R412] the suppression
         window is opened by a no-exit loop (REPEAT-without-WHILE,
         WHILE('1'B)) and closed by any other executable statement
         (put/assign/...); stop; lowering INSIDE the window emits
         NOTHING (its CALL cannot survive at the epilogue/proc
         append address); explicit stop; emitted in place also
         suppresses the epilogue CALL (stop_seen) [P401/R401]. *)
      (* stop; at an open window emits NOTHING: RFACT prints the
         statement at the append address (0056) with no code;
         R415/R418/R414/R426 confirm across proc/no-proc *)
      let at_tail = st.after_forever in
      if at_tail then ()
      else begin
        call_ext st "?STOPX";
        st.stop_seen <- true;
        if not st.in_proc then st.after_forever <- false
      end
      (* suppressed stop: window stays OPEN — trailing procedure
         code then displaces the epilogue entirely [RFACT] *)
  | Ast.Son { cond; cargs; handler } ->
      (* [E2E-11 step 2] ON <conditional-name>(<file>) <unit>.  Shape is from
         four DR specimens (E11A / E11C / E17A / FLTPOLY2, claim C109) and the
         control-block addressing from C120:

             LXI  H,<FILE>        <- SEL-COMMON re-selects the named group, then
                                     a COMMON relocation at offset 0
             MVI  A,05            <- the conditional-name code; ENDFILE = 5
             CALL ?ONCOP
             JMP  over
             <handler unit, inline>
             RET

         The handler is emitted INLINE, immediately after the JMP, and the next
         statement follows the RET -- which is what DR's runtime contract needs
         (C110): on EOF the unit runs ONCE, the interrupted GET then COMPLETES
         with its items unassigned, and control reaches the statement after the
         ON.  My GET already satisfies that: each item's ?GNVOP is followed by a
         JP that skips the conversion and lands on the next item, so an EOF
         mid-list leaves every remaining target untouched and falls through to
         ?QIOOP and the continuation -- no re-entry, no skip of the following
         statement.  FLTPOLY2 is the program that has to prove that.
         Only ENDFILE-on-a-declared-FILE is accepted; ON ERROR, SIGNAL and any
         other conditional name refuse, as do handlers whose own shape is
         unproven (they lower through the ordinary statement dispatcher, which
         refuses what it cannot do).

         Both the ON and its handler are counted (see count_required): the ON is
         the emitted registration/RET sequence, the handler lowers separately. *)
      st.lowered <- st.lowered + 1;
      st.last_imm <- None;
      (match String.lowercase_ascii cond, cargs with
       | "endfile", [ { Ast.e = Ast.Eident f; _ } ] ->
           let fu = String.uppercase_ascii f.Ast.orig in
           if not (List.mem fu st.files) then
             failwith
               (Printf.sprintf
                  "codegen: ON ENDFILE(%s) names something that is not a declared FILE [TBD] (line %d)"
                  f.Ast.orig s.Ast.spos.Source.line);
           (* [E2E-11 step 2] A GOTO out of an ON handler is a DIFFERENT mechanism.
              DR emits, at the TARGET LABEL:  LHLD * A(<2 hidden bytes>) / SPHL /
              CALL ?RECOV  [golden/e2e11g/E11F, code 0x1B] -- a stack unwind, because
              the handler runs inside the runtime's call context and jumping past it
              must discard that frame.  A plain GOTO emits no such thing [G115's
              labels have zero ?RECOV, and it is byte-exact], so this is specific to
              the handler crossing.  My label lowering has no RECOV path at all, and
              guessing the hidden cell would change both the AUTO area and the code.
              Refuse rather than emit E11F's 335 divergent bytes. *)
           (let rec has_goto (x : Ast.stmt) =
             match x.Ast.st with
             | Ast.Sgoto _ -> true
             | Ast.Sdobegin ss -> List.exists has_goto ss
             | Ast.Sif { then_; els; _ } ->
                 has_goto then_
                 || (match els with Some e -> has_goto e | None -> false)
             | Ast.Sdowhile { body; _ } | Ast.Sdoto { body; _ }
             | Ast.Sdoforever body -> has_goto body
             | Ast.Sproc b -> List.exists has_goto b.Ast.blk.Ast.bstmts
             | Ast.Son { handler; _ } -> has_goto handler
             | _ -> false
           in
           if has_goto handler then
             failwith
               (Printf.sprintf
                  "codegen: an ON handler containing GOTO needs DR's ?RECOV label \
                   prologue (LHLD */SPHL/CALL ?RECOV + a 2-byte hidden cell) [TBD] \
                   (line %d; E11F shows the shape, G115 proves plain GOTO has none)"
                  s.Ast.spos.Source.line));
           d st op_lxi_h;
           link st t_sel_common None (Some fu);
           reloc st Common 0;
           d st op_mvi_a; d st 0x05;
           call_ext st "?ONCOP";
           d st 0xc3 (* JMP *);
           let jmp_slot = st.lc in
           d st 0; d st 0;
           lower_stmt st ls handler;
           d st 0xc9 (* RET: terminates the inline handler unit [C109] *);
           emit_triple st jmp_slot st.lc
       | ("endfile", _) ->
           failwith
             (Printf.sprintf
                "codegen: ON ENDFILE with %d argument(s) or a non-identifier argument is unsampled [TBD] (line %d)"
                (List.length cargs) s.Ast.spos.Source.line)
       | _ ->
           failwith
             (Printf.sprintf
                "codegen: ON %s is not implemented [TBD] (only ENDFILE(<file>) has a DR lowering; line %d)"
                cond s.Ast.spos.Source.line))
  | Ast.Sprocedure_stmt { target; args } ->
      (* [E2E-11/CALL] a CALL statement is the SAME lowering as an expression
         call -- `LXI H,*A(desc)` (omitted when there are no arguments) then
         `CALL <entry>` -- and differs only in that the returned value, if any,
         is dropped [E24A: `call q;` = CALL; `n = f();` = CALL + SHLD N].  So
         this handler does not reimplement the descriptor: it marks the callee,
         funnels through the identical Esuffix path, and fails loudly if the
         mark was never consumed (which would mean the target did not resolve
         to an internal procedure and something else got lowered). *)
      st.lowered <- st.lowered + 1; st.last_imm <- None;
      (* Esuffix's head is an `expr`, not an `expr_kind` [ast.ml:35], so a bare
         name in statement position is wrapped, and a parenthesised call is
         already in the form lower_hl consumes. *)
      let call_e =
        match args, target.Ast.e with
        | [], (Ast.Eident _) -> { target with Ast.e = Ast.Esuffix(target, []) }
        | [], (Ast.Esuffix _) -> target
        | _ -> { target with Ast.e = Ast.Esuffix(target, args) }
      in
      let callee =
        match call_e.Ast.e with
        | Ast.Esuffix ({ Ast.e = Ast.Eident h; _ }, _) ->
            String.lowercase_ascii h.Ast.orig
        | _ ->
            failwith
              ("codegen: CALL target is not a simple procedure name [TBD] "
                 ^ "(only `CALL id` / `CALL id(args)` / bare `id;` have a DR "
                 ^ "lowering sampled; line "
                 ^ string_of_int s.Ast.spos.Source.line ^ ")")
      in
      st.call_stmt <- Some callee;
      lower_hl st call_e;
      if st.call_stmt <> None then
        failwith
          (Printf.sprintf
             "codegen: CALL %s did not reach the internal-call lowering [TBD]"
             callee)
  | Ast.Sdcl _ -> ()
  | Ast.Snull _ -> ()
  | _ -> failwith
         (Printf.sprintf "codegen: statement kind not in supported subset \
                          [TBD] (line %d)" s.Ast.spos.Source.line)


type statics =
  { sy_total : int                 (* bytes occupied below the pool *)
  ; sy_addrs : (string * int) list  (* lowercase name -> absolute data addr *)
  ; sy_cells : (int * int list) list (* (addr, init bytes) for the DATA segment *)
  ; sy_files : string list          (* [E2E-11 step 2] uppercased FILE names:
                                       each becomes its own NAMED COMMON group of
                                       34 + len bytes [C120], occupying NO DATA *) }

let empty_statics =
  { sy_total = 0; sy_addrs = []; sy_cells = []; sy_files = [] }

(* DR's FILE control block, measured on two different names [C120]:
   33 zero bytes | 1 byte = name length | the name.  SYSIN 39, INF 37. *)
let file_cb_bytes (name : string) =
  List.init 33 (fun _ -> 0) @ [String.length name]
  @ List.init (String.length name) (fun i -> Char.code name.[i])

let bit1_init (e : Ast.expr) =
  match e.Ast.e with
  | Ast.Ebit "1" -> Some 0x80
  | Ast.Ebit "0" -> Some 0x00
  | _ -> None

(* The parser puts every declaration into bstmts as an Sdcl item and leaves
   blk.bdecls = [] unconditionally [parser.ml:760, parser.ml:1089], so
   "declarations of a block" means "the Sdcl statements in order".  Reading
   bdecls instead silently yields an empty list -- which is exactly how E20C
   (INITIAL without STATIC, DR's own pass-2 NOT STATIC) compiled here instead of
   refusing: the attribute was simply never seen. *)
let block_dcls (blk : Ast.block) : Ast.dcl list =
  List.concat_map
    (fun (st : Ast.stmt) ->
      match st.Ast.st with Ast.Sdcl ds -> ds | _ -> [])
    blk.Ast.bstmts

(* STATIC / INITIAL attributes on one declaration (keys arrive in source case) *)
let dcl_static (d : Ast.dcl) =
  List.exists (fun (a : Ast.attr) -> String.lowercase_ascii a.Ast.akey = "static")
    d.Ast.dattrs
let dcl_initial (d : Ast.dcl) =
  match
    List.find_opt (fun (a : Ast.attr) ->
      String.lowercase_ascii a.Ast.akey = "initial") d.Ast.dattrs
  with
  | Some a -> (match a.Ast.aargs with [e] -> Some e | _ -> None)
  | None -> None

let emit_program (progname : string) (auto_bytes : int)
    (rows : (string * var_info) list) (statics : statics)
    (stmts : Ast.stmt list) (blk : Ast.block) =
  (* ---- Step-0 semantic-safety gate (corpus audit REV 2, D3 + D4) ----
     Two FAIL-SILENT holes were found by the 44-program sweep: block
     options other than OPTIONS(MAIN) (ACK: OPTIONS(MAIN,STACK(2000)))
     were parsed, stored and then dropped, and RETURNS(<non-FIXED type>)
     was mapped by Bind.rt_of_basic and then ignored by lowering (FFACT:
     RETURNS(FLOAT) emitted FIXED-shaped code, diverging at byte 48).
     Both are refused here, before a single byte is emitted.
     Whitelist is evidence-bounded, not convenience-bounded: all 83
     registered byte-exact specimens use exactly OPTIONS(MAIN) and
     RETURNS(FIXED) (verified over tools/e2e_gate.py's source list), so
     nothing already proven is affected.  *)
  let rt_is_implemented (r : Bind.rt) =
    match r with
    (* FIXED: 26 byte-exact specimens. FIXED DECIMAL(p,s) with p<=15:
       E2E-6 DEC core -- DEC(15,0) is pinned by DFACT's own $C trace and
       p=5/7/9/15 storage by R501-R512; DR itself says NOT IMP at p=31
       [R504], so anything wider stays refused. *)
    | Bind.RTbin _ -> true
    | Bind.RTdec (p, s) -> p >= 1 && p <= 15 && s >= 0 && s <= p
    (* [E2E-10] FLOAT BINARY(24) returns are implemented: the value is left on
       DR's float stack and the exit is JMP ?FPRET (+ ?RSBLK when recursive),
       proven by R3038 and FFACT.  Other precisions stay refused. *)
    | Bind.RTfloat 24 -> true
    | _ -> false
  in
  let check_returns (what : string) (line : int) (attrs : Ast.attr list) =
    match
      List.find_opt (fun (a : Ast.attr) -> String.equal a.akey "RETURNS")
        attrs
    with
    | Some a when a.Ast.atypes <> [] ->
        let r = Bind.rt_of_basic (List.hd a.Ast.atypes) in
        if not (rt_is_implemented r) then
          failwith
            ("codegen: " ^ what ^ " returns(" ^ Bind.rty_str r
             ^ ") deferred [TBD] (line " ^ string_of_int line
             ^ "; return types emitted today are FIXED [26 specimens], "
             ^ "FIXED DECIMAL(p<=15) [E2E-6] and FLOAT BINARY(24) [E2E-10]; "
             ^ "CHAR/BIT/POINTER/ENTRY each need their own ABI evidence)")
    | _ -> ()
  in
  let check_bopts (line : int) (opts : (string * Ast.expr list) list) =
    List.iter
      (fun (k, args) ->
        (* [E2E-12] STACK(n) is modelled now (see stack_operand below), so it is
           not refused here; its ARGUMENT is validated there, which is where the
           evidence lives.  Everything else still refuses. *)
        let kl = String.lowercase_ascii k in
        if not ((String.equal kl "main" && args = [])
                || String.equal kl "stack") then
          failwith (Printf.sprintf
                      "codegen: block option %s%s deferred [TBD] (line %d; \
                       only OPTIONS(MAIN) is modelled; STACK/SEGMENTS and \
                       friends move code or data and no golden pins them)"
                      k (if args = [] then "" else "(...)") line))
      opts
  in
  let line_of_block (b : Ast.block) fb =
    match b.Ast.blabel with
    | Some n -> n.Ast.pos.Source.line
    | None -> (match b.Ast.bstmts with
               | s :: _ -> s.Ast.spos.Source.line
               | [] -> fb)
  in
  let rec check_block (b : Ast.block) (fb : int) =
    let ln = line_of_block b fb in
    check_bopts ln b.Ast.bopts;
    check_returns
      (match b.Ast.bname with
       | Some n -> "procedure " ^ n.Ast.orig
       | None -> "block") ln b.Ast.bsuffix;
    List.iter
      (fun (d : Ast.dcl) ->
        check_returns ("declaration " ^ d.Ast.dname.Ast.orig)
          d.Ast.dname.Ast.pos.Source.line d.Ast.dattrs)
      b.Ast.bdecls;
    List.iter (check_stmt ln) b.Ast.bstmts
  and check_stmt fb s =
    match s.Ast.st with
    | Ast.Sdcl ds ->
        List.iter
          (fun (d : Ast.dcl) ->
            check_returns ("declaration " ^ d.Ast.dname.Ast.orig)
              d.Ast.dname.Ast.pos.Source.line d.Ast.dattrs)
          ds
    | Ast.Sif { then_; els; _ } ->
        check_stmt fb then_;
        (match els with Some e -> check_stmt fb e | None -> ())
    | Ast.Sdobegin ss -> List.iter (check_stmt fb) ss
    | Ast.Sdoto { body; _ } -> check_stmt fb body
    | Ast.Sdowhile { body; _ } -> check_stmt fb body
    | Ast.Sdoforever b -> check_stmt fb b
    | Ast.Son { handler; _ } -> check_stmt fb handler
    | Ast.Selse b -> check_stmt fb b
    | Ast.Sproc bs -> check_block bs.Ast.blk bs.Ast.bpos.Source.line
    | _ -> ()
  in
  check_block blk 0;
  List.iter (check_stmt 0) stmts;
  (* ---- [E2E-12] OPTIONS(STACK(n)) ---------------------------------------
     The whole rule, from eleven DR objects (batches golden/e2e160, e2e161):
       T1  no STACK                      -> LXI B,0200        (default 512)
       T2  stack(2000)                   -> LXI B,07D0        (the value itself)
       T3  stack(100)                    -> LXI B,0064        (little-endian,
                                                 leading zero byte is real)
       T12 stack(1)                      -> LXI B,0001        (lower end)
       T4  stack(65535)                  -> LXI B,FFFF        (upper end, ACCEPTED)
       T5  stack(65536)                  -> DR pass-1 ERROR, NO .REL  -> refuse
       T10 stack(2*1000)                 -> DR pass-1 ERROR, NO .REL  -> refuse
       T6  stack(0)                      -> LXI B,0200  !!  ZERO MEANS DEFAULT,
                                           not zero.  This is the one probe that
                                           would have been guessed wrong: the
                                           obvious reading of "stack(0)" is a
                                           0x0000 operand.
       T9  options(stack(2000),main)      -> same as T2  (order-independent)
       T8  + a nested RECURSIVE procedure -> same operand; the SVBLK/ shadow
                                           machinery is untouched by STACK
       T7  procedure-only MODULE + stack(2000) -> BYTE-IDENTICAL to T11 (the same
                                           module with NO STACK at all).  A
                                           module has no main prologue and DR
                                           drops the option entirely -- it is NOT
                                           an error, and there is no other place
                                           in the record stream where the value
                                           appears (DATA/CODE sizes identical).
     So STACK is exactly ONE bit-packed 16-bit operand in the main prologue.  In
     the raw file it straddles a byte boundary, which is why T1 vs T2 differ in
     THREE file bytes while only TWO code bytes change -- a reminder that raw
     `cmp' and a decoded view count different things, and both were needed here. *)
  let stack_operand =
    let def = 0x0200 in
    let acc = ref def in
    List.iter
      (fun (k, args) ->
        if String.equal (String.lowercase_ascii k) "stack" then
          match args with
          | [ { Ast.e = Ast.Enumber t; _ } ] when is_int_literal t ->
              let v = parse_int_const t in
              if v > 0xffff then
                failwith
                  (Printf.sprintf
                     "codegen: [TBD] OPTIONS(STACK(%d)) exceeds 65535 and is                       rejected by DR in pass 1 with NO .REL emitted (T5,                       golden/e2e160/T5/T5.PRN: `1 ERROR(S) IN PASS 1');                       mirroring DR's perimeter rather than truncating to 16 bits"
                     v)
              else if v > 0 then acc := v
              (* v = 0: DR emits the DEFAULT operand, measured by T6 *)
          | _ ->
              failwith
                "codegen: [TBD] OPTIONS(STACK(...)) with a non-integer-literal                  argument is rejected by DR in pass 1 with NO .REL emitted                  (T10 `stack(2*1000)' golden/e2e160/T10/T10.PRN); the operand                  is a compile-time 16-bit value, not an expression")
      blk.Ast.bopts;
    !acc
  in
  let layout = Bind.bind_program blk in
  (* [E2E-11 step 5] a procedure-only module (C136): DR gives it the ordinary
     procedure entry -- copy-in ladder, no ?START prologue, no append/tail-guard
     bookkeeping, and the RETURNS-driven exit -- while the header still carries
     EXTDEF + DEF-PUBLIC code 0000 with the SIX-CHARACTER-truncated module name
     [golden/first/A].  Perimeter: the shapes DR has shown me are no-RETURNS
     (Q2), RETURNS(FIXED) (Q3) and RETURNS(FLOAT) (Q1/A).  A DEC-returning
     module would take lower_proc's DEC exit, whose top-level shape has no DR
     sample, so it refuses here rather than assuming nested-proc bytes carry over. *)
  let top_pl = layout.Bind.pl_top in
  let is_top_proc = top_pl <> None in
  (* RETURNS(DECIMAL) on a module is ACCEPTED.  DR's Q8 (golden/e2e148) shows the
     module DEC exit is the same family the nested DEC path already emits --
     CALL ?QI15D / MVI A,<scale> / CALL ?QDDSL / JMP ?DCRET -- and Q8 comes out byte
     identical here, which is the evidence that mattered.  My earlier refusal assumed
     the nested DEC exit might not carry to a top-level module; it does, unchanged. *)
  (* constant call arguments allocate 2B little-endian pool cells
     [P401: '2' at data@0]; included in the pool prescan total so
     pool-relative layout matches the lowering-time allocation run *)
  (* does callee `pn` have a FLOAT BINARY(24) formal at position i?  Used to
     size a numeric call argument's cell: a fixed formal takes the 2-byte
     integer pool cell, a FLOAT formal takes the 4-byte float pool cell that
     prescan_pool already demands through pdec_fl_expr [R3062].  Counting 2
     bytes for a float formal double-charged the literal and shifted every
     variable address in the program by 2. *)
  (* [E2E-11 step 4] this used to resolve the callee only through pl_procs, so
     for an EXTERNAL ENTRY it answered "not a float formal" and const_cells added
     its 2-byte FIXED cell on top of the 4-byte float cell the prescan had just
     demanded -- FDTEST's data area came out 0x1A against DR's 0x18.  Now it
     delegates to the same accessor the lowering and the prescan use, so there is
     ONE answer to "is argument i FLOAT". *)
  let formal_float_at pn i =
    match callee_formal_rt_l layout pn i with
    | Some (Bind.RTfloat 24) -> true
    | _ -> false
  in
  let const_cells =
    List.fold_left
      (fun a (c : Bind.call_site) ->
        match c.cs_args with
        | [] -> a
        | args ->
            List.fold_left
              (fun acc (i, arg) ->
                match arg.Ast.e with
                | Ast.Enumber _ when not (formal_float_at c.cs_proc i) -> acc + 2
                | _ -> acc)
              a (List.mapi (fun i x -> (i, x)) args)
                  (* ACCUMULATE from the outer total: starting at 0 silently
                     dropped every call site but the last [R406/R421 parity] *)
      ) 0 layout.pl_calls
  in
  (* [E2E-6] prescan context for decimal literal cells: every block's
     variable kinds plus each procedure's decimal return type.  A name
     declared with two different types anywhere in the program would make
     a single global map ambiguous (and could mis-size the pool), so it is
     refused rather than guessed. *)
  let rt_to_vk (rt : Bind.rt) =
    match rt with
    | Bind.RTdec (p, s) -> Vdec (p, s)
    | Bind.RTchar (n, false) -> Vfix n
    | Bind.RTchar (n, true) -> Vvar n
    | Bind.RTfloat 24 -> Vflt
    | _ -> Vint
  in
  let proc_vk_rows =
    List.concat_map
      (fun (p : Bind.proc_layout) ->
        List.map (fun (n, rt, _o) -> (n, rt_to_vk rt)) p.Bind.pl_rows)
      layout.pl_procs
  in
  let pd_vars =
    let acc = ref ([] : (string * vkind) list) in
    List.iter
      (fun (n, vk) ->
        match List.assoc_opt n !acc with
        | Some v when v <> vk ->
            failwith
              (Printf.sprintf
                 "codegen: variable %s declared with conflicting kinds; \
                  decimal pool prescan needs one unambiguous type map [TBD]"
                 n)
        | _ -> acc := (n, vk) :: !acc)
      (proc_vk_rows @ List.map (fun (n, vi) -> (n, vi.vk)) rows);
    !acc
  in
  let pd_procs =
    List.map
      (fun (p : Bind.proc_layout) ->
        (p.Bind.pl_name,
         match p.Bind.pl_ret with
         | Some (Bind.RTdec (pp, ps)) -> Some (pp, ps)
         | _ -> None))
      layout.pl_procs
  in
  let pd_fl_procs =
    List.filter_map
      (fun (p : Bind.proc_layout) ->
        match p.Bind.pl_ret with
        | Some (Bind.RTfloat 24) -> Some p.Bind.pl_name
        | _ -> None)
      layout.pl_procs
  in

  (* [E2E-11 step 5] for a FLOAT-returning module the top-level statements ARE
     the procedure body, so the prescan must see the same return type the
     lowering will: FFACT's `return (1)' allocates its 4-byte float cell through
     pdec_fl_expr only when pd_fl_ret is set (see the Sreturn arm of prescan).
     Left false, A's `return (x/2)' would prescan as a bare integer return and
     its MBF cell (data 0000-0003, `00 00 00 82' in DR's golden) would be charged
     under a different rule than the one that lowers it -- the pool/offset half of
     the C134 "one question, two owners" failure. *)
  let top_fl_ret =
    match top_pl with
    | Some (tp : Bind.proc_layout) ->
        (match tp.Bind.pl_ret with Some (Bind.RTfloat 24) -> true | _ -> false)
    | None -> false
  in
  (* [E2E-11 step 5] the DEC half of the same one-owner argument: a DEC-returning
     module's `return (1)' takes a target-precision pool cell [DFACT], and prescan
     charges that only through cx.pd_ret.  For a MAIN block this stays None exactly
     as before (a main block has no return type); for a module it must be the
     module's own RETURNS, or the pool would be sized under one model and lowered
     under another -- the C134 failure class, not a style preference. *)
  let top_dec_ret =
    match top_pl with
    | Some (tp : Bind.proc_layout) ->
        (match tp.Bind.pl_ret with Some (Bind.RTdec (pp, ps)) -> Some (pp, ps)
                                 | _ -> None)
    | None -> None
  in
  let pool_total =
    prescan_pool { pd_vars; pd_procs; pd_ret = top_dec_ret
                    ; pd_dec = ref []; pd_str = ref []; pd_fl = ref []; pd_fl_ret = top_fl_ret
                    ; pd_fl_procs
                    ; pd_callee_rt =
                        (fun nm i -> callee_formal_rt_l layout nm i) }
                    stmts + const_cells
  in
  let st =
    (* [E2E-11 step 1a-ii] the pool base sits ABOVE the static cells, and the
       pool allocator starts there too, so DATA is one block laid out
       [statics][pool][automatics] exactly as DR does it [C114].  Static
       initialiser bytes are pre-seeded as pool blocks at their absolute
       addresses, which reuses the existing per-block SET-LC(data,addr)
       emission [G113] -- DR emits a SET-LC per data block, not one flat run,
       and E20B's .REL shows exactly that for a static cell followed by a
       string literal. *)
    { base = statics.sy_total + pool_total; items = []; pool = statics.sy_cells
    ; pool_next = statics.sy_total; fmtq = []; dec_cells = []; lc = 0
    ; last_imm = None; lowered = 0; temps = 0
    ; stat_addrs = statics.sy_addrs; stat_total = statics.sy_total
    ; files = statics.sy_files
    ; stop_seen = false; calls = layout.pl_calls
    ; procs =
        List.map
          (fun (p : Bind.proc_layout) -> (p.pl_name, p))
          layout.pl_procs
    ; exts = layout.Bind.pl_exts
    ; entries = []; fcalls = []; deref = []
    ; floor = layout.pl_total; vars = rows
    ; arrays = Bind.bind_arrays blk
    ; dec_ret = None
  ; float_ret = false
  ; fl_cells = []
  ; str_cells = []
    ; in_proc = false; in_rec = false; top_proc = false; call_stmt = None
    ; after_forever = false; guards = 0; guard_slots = []
    ; appended = false; secs = layout.Bind.pl_secs
    ; last_loop_edge = 0 }
  in
  (* [E2E-8] DR allocates every PUT EDIT format table ahead of all other pool
     items [R1003/R1021/R1022], so the tables are reserved BEFORE any
     statement lowers. *)
  prealloc_fmt_tables st stmts;
  (* lower prologue + body + epilogue into st.items (code segment) *)
  let ls = { labs = []; fwd = [] } in
  if is_top_proc then begin
    (* [E2E-11 step 5 / C136] NO `LXI B,0200 / CALL ?START': DR's procedure-only
       module begins with the formal copy-in ladder itself.  The body is lowered
       by lower_proc, the SAME routine used for nested procedures, which supplies
       the copy-in ladder, the deref/pointer-formal ABI, the RETURNS-driven exit
       (?FPRET for FLOAT, implicit RET for no-RETURNS) and forward-CALL resolution
       at the entry byte.  Reusing it rather than writing a second entry sequence
       is the point: the two shapes are byte-identical in DR -- A's code
       0000-0006 is E27C p1's code 001F-0023. *)
    st.top_proc <- true;
    let bpos =
      match blk.Ast.blabel with
      | Some n -> n.Ast.pos
      | None ->
          (match blk.Ast.bstmts with
           | s :: _ -> s.Ast.spos
           | [] -> { Source.line = 0; col = 0 })
    in
    lower_proc st ls { Ast.blk = blk; bpos }
  end else begin
  d st op_lxi_b;
  d st (stack_operand land 0xff);
  d st ((stack_operand lsr 8) land 0xff);
  d st op_call;
  let start_slot = st.lc in
  d st 0; d st 0;
  link st t_chain_ext (Some (Code, start_slot)) (Some "?START");
  List.iter
    (fun (s : Ast.stmt) ->
      (* [R423/ALL goldens] every procedure body is appended AFTER
         every main-block statement; DR layout with a live statement
         following an appended proc is unobserved -> fail loud *)
      if st.appended && not st.in_proc then
        (match s.Ast.st with
         | Ast.Sproc _ | Ast.Sdcl _ | Ast.Snull _ -> ()
         | _ -> failwith
                "codegen: main-block statement after an appended \
                 procedure [TBD] (unproven DR append layout)");
      (* [R401/R414/R419/R420/R423] any main-block statement other
         than a no-exit loop or the trailing stop anchors the
         epilogue region and closes the suppression window; the
         append address advances past it *)
      if st.after_forever && not st.in_proc then begin
        (* append address advances while window open; ANCHORS
           (any stmt except loops/stop;/proc blocks) CLOSE it;
           Sproc does NOT [RFACT/R410/R425] *)
        (match s.Ast.st with
         | Ast.Sdoto _ | Ast.Sdowhile _ | Ast.Sdoforever _
         | Ast.Sstop _ | Ast.Sproc _ | Ast.Snull _ | Ast.Sdcl _ -> ()
         | _ -> st.after_forever <- false);
        st.last_loop_edge <- st.lc
      end;
      lower_stmt st ls s)
    stmts;
  end;
  (match ls.fwd with
   | [] -> ()
   | (nm, _) :: _ ->
       failwith (Printf.sprintf
                   "codegen: GOTO to undefined/unresolvable label %s \
                    [TBD] DR pass-2 UNDEF diag" nm));
  (match st.fcalls with
   | [] -> ()
   | (nm, _) :: _ ->
       failwith (Printf.sprintf
                   "codegen: unresolved forward CALL to %s [TBD]" nm));
  if st.calls <> [] then
    failwith "codegen: unconsumed call-site cells [TBD]";
  (* DISCARD INVARIANT: every non-decl/non-null statement (at any
     nesting depth) must be accounted for by a lowering step. *)
  let req = List.fold_left (fun a s -> a + count_required s) 0 stmts in
  if req <> st.lowered then
    failwith
      (Printf.sprintf "codegen: DISCARD INVARIANT violated (%d required, \
                       %d lowered)" req st.lowered);
  (* explicit stop; inside the body REPLACES the epilogue CALL
     [P401: STOPX @26 emitted at the statement; no trailing call;
     programs without stop; keep the epilogue — 42 prior goldens] *)
  (* epilogue suppressed when the main block ends at a no-exit loop
     (RFACT/R410/R418: edge == final LC; procs or none [R418 proves
     the displacement alone suffices]) and whenever an explicit
     stop; was emitted in place (P401/R401) *)
  (* [RFACT/R407/R410/R411/R418/R425/R426/R427 vs R401/R412/R419/
     R423/R428/P404] the epilogue CALL is dropped exactly when the
     suppression window is still open at main-block end (trailing
     no-exit loop, no anchor after it) — procedure code BELOW does
     not change the window state, it just sits between the window
     address and the epilogue slot *)
  (* [R423] a guarded tail keeps the epilogue CALL (the guard JMP
     targets the CALL itself); plain open windows drop it *)
  let tail_displaced = st.after_forever in
  (* [E2E-11 step 5 / C136] a procedure-only module has NO epilogue: DR's A ends
     at the `JMP ?FPRET' of the RETURN and DEF-CODE-SIZE 0015 follows immediately
     -- no CALL ?STOPX anywhere in the file, because the module is not the program
     entry point and does not terminate it.  What a module CONTAINING `stop;'
     does is unprobed (Q6 is that probe), so the statement refuses instead of
     quietly dropping the epilogue it would have needed. *)
  (* STOP inside a module IS allowed: Q6 (golden/e2e148) shows DR lowering the
     statement to an in-place `CALL ?STOPX' (CD 00 00 + CHAIN-EXT at code 0014)
     and STILL emitting no epilogue CALL -- DEF-CODE-SIZE 0016 follows the
     statement's own bytes.  That is exactly the existing Sstop lowering plus the
     is_top_proc gate below, so no new rule is needed here; the earlier refusal
     was a capability gap that DR's own golden has now closed. *)
  if not is_top_proc && not st.stop_seen && not tail_displaced then begin
    (* backpatch the tail-guard JMP operand(s) to THIS epilogue
       address [R404: @29 -> 0x44; P404: @10 -> 0x2B], immediately
       before the CALL bytes, then emit CALL ?STOPX *)
    List.iter (fun gs -> emit_triple st gs st.lc)
      (List.rev st.guard_slots);
    st.guard_slots <- [];
    d st op_call;
    let stop_slot = st.lc in
    d st 0; d st 0;
    link st t_chain_ext (Some (Code, stop_slot)) (Some "?STOPX")
  end;
  (* a guard whose JMP operand never got an epilogue to point at is
     an unobserved shape: fail loud rather than emit 3 dangling bytes *)
  if st.guard_slots <> [] then
    failwith
      "codegen: tail guard emitted without an epilogue CALL to chain \
       to [TBD] unproven DR shape (no-exit main tail AFTER an \
       appended procedure)]";
  let code_items = st.items in
  (* now build the ordered full item list *)
  (* [E2E-16] DEMAND/LAYOUT INVARIANT.  st.base is the pool size the prescan demanded and
     st.pool_next is what lowering actually allocated.  They MUST agree: if lowering used more
     than was demanded, automatic variables land ON TOP of pool bytes -- the FDTEST failure,
     where the index `i' aliased a float constant and every address in the dump still looked
     plausible -- and if it used less, the data area is oversized and every automatic shifts
     (that is exactly what C152 was).  Before this check the mismatch produced WRONG BYTES with
     no diagnostic at all, so the whole regression panel doubles as a demand/layout test. *)
  if st.pool_next <> st.base then
    failwith
      ("codegen: [TBD] pool demand/layout mismatch: prescan demanded " ^ string_of_int st.base
       ^ " pool bytes, lowering allocated " ^ string_of_int st.pool_next
       ^ " -- the data area size or the automatic offsets would be wrong (C152)");
  let data_size =
    statics.sy_total + pool_total + max auto_bytes layout.pl_total
    + 2 * st.temps
  in
  (* [E2E-9, DECPOLY / LONGNAME] DR emits the program's external name in
     PROG-NAME / EXTDEF / DEF-PUBLIC TRUNCATED TO SIX CHARACTERS: the 7-char
     corpus program DECPOLY carries the symbol "DECPOL", and the 8-char
     probe label LONGNAME carries "LONGNA".  Internal procedure names never
     become symbols [NTEST1: `computeval` appears nowhere in the .REL], so
     two internals colliding on their first six characters is NOT an error
     [NTEST2: factor1/factor2 compile clean]. *)
  let extname =
    let u = String.uppercase_ascii progname in
    if String.length u > 6 then String.sub u 0 6 else u
  in
  let header =
    [ Link (t_progname, None, Some extname)
    ; Link (t_req_library, None, Some "PLILIB")
    ; Link (t_extdef, None, Some extname)
    ; Link (t_def_public, Some (Code, 0), Some extname) ]
  in
  (* [E2E-11 step 2] one NAMED COMMON group per FILE variable, emitted AFTER the
     header links and BEFORE the DATA segment -- DR's own item order [FLTPOLY2:
     PROG-NAME / REQ-LIBRARY / EXTDEF / DEF-PUBLIC / DEF-COMMON-SIZE SYSIN /
     SEL-COMMON SYSIN / SET-LC(common,0) / 39 bytes / SET-LC(data,0) / ...].
     The size is 34 + len(name) and the contents are 33 zeros, the name length,
     then the name [C120]. *)
  let common_seg =
    List.concat_map
      (fun (nm : string) ->
        [ Link (t_def_common_size, Some (Abs, 34 + String.length nm), Some nm)
        ; Link (t_sel_common, None, Some nm)
        ; Link (t_set_lc, Some (Common, 0), None) ]
        @ List.map (fun v -> Data v) (file_cb_bytes nm))
      statics.sy_files
  in
  let data_seg =
    if st.pool <> [] || statics.sy_files <> [] then
      Link (t_set_lc, Some (Data, 0), None)
      ::
      (let sorted =
         List.sort (fun (a, _) (b, _) -> compare a b) st.pool in
       (* each pool block: SET-LC(data,addr) for addr>0 then its bytes;
          block 0 rides the header SET-LC(data,0) [G113] *)
       List.concat_map
         (fun (i, (addr, bs)) ->
           (* [E2E-16/C152] only the FIRST block rides the header's SET-LC(data,0).  A later
              block at address 0 -- which happens exactly when an empty literal is stored twice
              [PL16/PL17: two SET-LC(data,0000), zero DATA bytes] -- gets its own record. *)
           (if addr > 0 || i > 0 then [Link (t_set_lc, Some (Data, addr), None)]
            else [])
           @ List.map (fun v -> Data (v land 0xff)) bs)
         (List.mapi (fun i x -> (i, x)) sorted))
    else []
  in
  let bridge =
    [ Link (t_def_data_size, Some (Abs, data_size), None)
    ; Link (t_set_lc, Some (Code, 0), None) ]
  in
  (* [E2E-11 step 5 / C136] END-PROGRAM's operand SEGMENT distinguishes the two
     file kinds in DR's own output: every MAIN specimen ends with
     `LINK-END-PROGRAM code 0000' (390 byte-exact specimens), while A -- a
     procedure-only module -- ends with `LINK-END-PROGRAM abs 0000'.  That is the
     only place in the record stream where the module shape differs in a header
     field, and it is exactly what a code-path guess would have missed: the value
     is 0 either way, so only the segment type byte tells them apart. *)
  let end_prog_op = if is_top_proc then (Abs, 0) else (Code, 0) in
  let tail =
    [ Link (t_def_code_size, Some (Code, st.lc), None)
    ; Link (t_end_program, Some end_prog_op, None)
    ; Link (t_end_file, None, None) ]
  in
  (header @ common_seg @ data_seg @ bridge @ code_items @ tail, st.lc)

(* build var_info rows from binder rows, keeping only fixed-bin scalars.
   NOTE: storage byte-size comes ONLY from Bind.bytes_of (the binder is the
   single authority on layout) — codegen does not re-derive it.  Returns
   (progname, AUTO_BYTES excluding pool, vars, statics).

   [E2E-11 step 1a-ii] STATIC / INITIAL.  What DR allows here is deliberately
   narrow, and every widening is a measured probe, not an inference:
     * placement: one DATA area, [statics][pool][automatics] (C114).  Bind
       packs statics INTO the auto offsets, so each automatic is corrected by
       subtracting the bytes of every static declared BEFORE it -- the same
       `drops` subtraction style proven for float formals in E2E-10 step 3b.
     * initialiser VALUES: pinned only for bit(1) ('0'b -> 0x00, '1'b -> 0x80)
       by E20A/E20B/E20D/E20E.  `initial' on any other kind is refused rather
       than guessed, because an ignored initialiser is a silent VALUE divergence,
       the worst class in this project.
     * DR REQUIRES STATIC for an INITIALised bit string: E20C
       (`dcl f bit(1) initial('1'b);`) passes pass 1, then fails pass 2 with
       DR's own diagnostic `NOT STATIC' and emits no .REL.  That is a language
       rule, so it refuses here instead of degrading.
     * statics inside a NESTED procedure are unmeasured (the interaction with
       bind's per-proc layout and with re-entry is unknown), so they refuse. *)
let rows_of (b : Ast.block) =
  (* [E2E-11 step 5 / C136] Two layout authorities exist in bind, and which one
     describes the OUTERMOST block depends on the file kind: bind_rows lays out a
     MAIN block (no formal pointer cells at all), while bind_program's section2
     pass lays out a CALLEE (2-byte pointer cell per formal, the declared formal
     dcl DEDUPED onto it, locals shifted after the pointer cells).  A
     procedure-only module is the second kind -- DR's A has DATA AREA 0006 =
     4-byte MBF pool cell + x's 2-byte pointer cell, NOT 4+4 -- so taking the
     auto area from bind_rows over-charges the formal by its declared size and
     would place a second local two bytes too high.  Using the section layout
     here keeps ONE authority per file kind, and any declaration bind_rows sees
     that section2 did not place (STATIC / FILE / FORMAT in a module) is a
     mixture with no DR sample, so it refuses instead of silently keeping the
     wrong offsets. *)
  let bind_all = Bind.bind_program b in
  let rows =
    match bind_all.Bind.pl_top with
    | Some tp ->
        let br = Bind.bind_rows b in
        let missing =
          List.filter
            (fun (n, _rt, _o, _a) ->
              not
                (List.exists
                   (fun (x, _rt, _o) ->
                     String.equal x (String.lowercase_ascii n))
                   tp.Bind.pl_rows))
            br
        in
        if missing <> [] then
          failwith
            (Printf.sprintf
               "codegen: [TBD] declaration %s in a procedure-only module is \
                outside the section layout DR has sampled [C136 covers formals \
                and ordinary locals only]"
               (match List.hd missing with n2, _rt, _o, _a -> n2));
        List.map (fun (n, rt, o) -> (n, rt, o, true)) tp.Bind.pl_rows
    | None -> Bind.bind_rows b
  in
  (* [E2E-11 step 1a-ii] Which declared names carry an EXPLICIT STATIC, and what
     their INITIAL value is.  bind already keeps a separate static offset
     counter (`soff'), giving static cells 0,1,2... and automatics their own
     packing [bind.ml:329-340], which is exactly DR's [statics][pool][autos]
     single DATA area once codegen adds the static total to the pool base
     [C114].  So codegen re-derives NOTHING about placement -- it reads bind's
     offset and only has to decide what it is allowed to lower.
     Scope, deliberately narrow:
       * explicit STATIC is accepted on BIT(1) only.  Static FIXED/DEC/CHAR/
         FLOAT cells are a placement DR has not shown me here, and guessing the
         initialiser encoding is a silent-value divergence -- the worst kind.
       * a static-class row that is NOT an explicit static (FORMAT, FILE, ENTRY
         -- bind's `stc' is broader than the attribute) would have consumed
         `soff' bytes before my bit cell, shifting it.  DR's listing for that
         mixture is unprobed, so it refuses instead of silently reordering.
       * INITIAL without STATIC is DR's own pass-2 error `NOT STATIC' [E20C].
       * statics are collected from the MAIN block's Sdcl statements; a name
         declared static in a nested procedure is not in that map and refuses. *)
  let static_dcls =
    let one (d : Ast.dcl) =
      ( String.lowercase_ascii d.dname.Ast.orig
      , (dcl_static d, dcl_initial d, d.dname.Ast.pos.Source.line) )
    in
    List.map one (block_dcls b)
  in
  let has_static_class rt =
    match rt with
    | Bind.RTfile _ | Bind.RTformat | Bind.RTentry _ -> true
    | _ -> false
  in
  let conflicting =
    List.filter
      (fun (nm, rt, _o, auto) ->
        not (List.mem_assoc nm static_dcls)
        && (match rt with
            | Bind.RTbit 1 -> false
            | _ -> auto = false && has_static_class rt))
      rows
  in
  let sy_addrs = ref [] and sy_cells = ref [] and sy_total = ref 0
  and sy_files = ref [] in
  List.iter
    (fun (nm, rt, off, auto) ->
      let li = String.lowercase_ascii nm in
      let flags = List.assoc_opt li static_dcls in
      let explicit = match flags with Some (st, _i, _l) -> st | None -> false in
      let init_opt = match flags with Some (_s, i, _l) -> i | None -> None in
      let line = match flags with Some (_s, _i, l) -> l | None -> 0 in
      if explicit then begin
        if conflicting <> [] then
          failwith
            (Printf.sprintf
               "codegen: STATIC mixed with a %s declaration is unsampled [TBD] (bind's static offset would place the bit cell after it; DR has not shown that combination)"
               (match List.hd conflicting with
                | (_, Bind.RTformat, _, _) -> "FORMAT"
                | (n2, Bind.RTfile _, _, _) -> "FILE " ^ n2
                | _ -> "static-class"));
        match rt with
        | Bind.RTbit 1 ->
            sy_addrs := !sy_addrs @ [(li, off)];
            sy_total := max !sy_total (off + 1);
            (match init_opt with
             | None -> ()
             | Some e ->
                 (match bit1_init e with
                  | Some v -> sy_cells := !sy_cells @ [(off, [v])]
                  | None ->
                      failwith
                        (Printf.sprintf
                           "codegen: STATIC INITIAL value %s on BIT(1) is unsampled [TBD] (only the '0'b and '1'b literals have DR bytes [E20B/E20D]; anything else would be a silently wrong initialiser)"
                           (Format.asprintf "%a" Parser.pp_e e))))
        | _ ->
            failwith
              (Printf.sprintf
                 "codegen: STATIC on %s is unsampled [TBD] (C114 places static cells below the pool, but only BIT(1) initialiser BYTES are measured; line %d)"
                 (Bind.rty_str rt) line)
      end
      else
        match init_opt with
        | Some _e ->
            (* DR pass 2: `NOT STATIC', and no .REL is emitted [E20C] *)
            failwith
              (Printf.sprintf
                 "codegen: INITIAL on %s without STATIC is rejected by DR \
                  (pass 2 says NOT STATIC, no .REL) [TBD] (line %d)"
                 (Bind.rty_str rt) line)
        | None -> ())
    rows;
  (* INITIAL without STATIC on a name bind did not even place as a storage row
     (e.g. an implicit-FLOAT name) is caught above only when the row exists; the
     attribute check is repeated here so a declaration whose type refuses
     elsewhere cannot quietly skip it. *)
  let row_names = List.map (fun (n, _rt, _o, _a) -> (n, 0)) rows in
  List.iter
    (fun (li, (st, io, line)) ->
      if not st && io <> None
         && not (List.mem_assoc li row_names) then
        failwith
          (Printf.sprintf
             "codegen: INITIAL without STATIC is rejected by DR (NOT STATIC) \
              [TBD] (line %d)"
             line))
    static_dcls;
  let sy_total = !sy_total in
  let stat_set = !sy_addrs in
  let vars =
    List.filter_map
      (fun (nm, rt, off, _auto) ->
        (* a static cell's address comes from st.stat_addrs via addr_of, so its
           var_info offset is irrelevant here; automatics keep bind's packing
           untouched, which is what leaves the 336 existing specimens
           bit-for-bit unaffected. *)
        let _ = stat_set in
        match rt with
        | Bind.RTbin p ->
            if p > 15 then
              (* DR pass-1 rejects these outright ('NOT IMP',
                 N24/N305/N307: no .REL emitted) -- mirror the
                 perimeter boundary rather than compile what DR
                 cannot [C079] *)
              failwith
                (Printf.sprintf
                   "codegen: FIXED BIN(%d) NOT IMP on DR [TBD]" p);
            Some (nm, { off; size = Bind.bytes_of rt; vk = Vint;
                        w = binw (if p <= 0 then 15 else p) })
        | Bind.RTdec (p, s) ->
            (* DR accepts FIXED DECIMAL up to p=15 [R501-R512, DFACT];
               p=31 is DR's own pass-1 'NOT IMP' [R504: no .REL].  The
               band 16..30 is unpinned, so it stays a loud refusal
               rather than an extrapolated cell size. *)
            if p > 15 || p < 1 || s < 0 || s > p then
              failwith
                (Printf.sprintf
                   "codegen: FIXED DEC(%d,%d) outside the probed DEC band \
                    [TBD] (DR: NOT IMP at p=31 [R504]; exact 16..30 unknown)"
                   p s);
            Some (nm, { off; size = Bind.bytes_of rt; vk = Vdec (p, s)
                      ; w = p + 3 })
        | Bind.RTfile _ ->
            (* [E2E-11 step 2] a FILE variable takes NO DATA cell: DR gives it a
               named COMMON group instead [C120, verified for SYSIN and INF].  bind
               classifies it static-class, so it never reaches the static-bit path
               above; here it is recorded for the COMMON emission and contributes
               nothing to the DATA area.  The `internal' flag turned out NOT to
               distinguish SYSIN from a user stream (FLTPOLY2's `dcl sysin file'
               binds as FILE EXTERNAL STATIC), and both get the same block shape --
               so this arm does not branch on it.  A name longer than 6 chars is
               refused: DR's 6-character truncation law is measured for program
               and entry names [DECPOLY, LONGNAME], never for a COMMON symbol. *)
            let up = String.uppercase_ascii nm in
            if String.length up > 6 then
              failwith
                (Printf.sprintf
                   "codegen: FILE name %s (%d chars) exceeds 6 [TBD] (COMMON-symbol truncation for FILE control blocks is unmeasured; SYSIN/INF are 5/3)"
                   up (String.length up));
            sy_files := !sy_files @ [up];
            None
        | Bind.RTchar (n, false) ->
            Some (nm, { off; size = Bind.bytes_of rt; vk = Vfix n; w = 0 })
        | Bind.RTchar (n, true) ->
            Some (nm, { off; size = Bind.bytes_of rt; vk = Vvar n; w = 0 })
        | Bind.RTfloat p ->
            (* [E2E-10] the CELL is 4 bytes for every precision DR stores
               (R3001/R3013), but only binary(24) has a characterized value
               model, and plain `float` IS float binary(24) [R3001].  Other
               precisions stay refused so a binary(14) program can never
               silently get 24-bit arithmetic. *)
            if p <> 24 then
              failwith
                (Printf.sprintf
                   "codegen: FLOAT BINARY(%d) precision unsupported [TBD] (only BINARY(24) is characterized; R3013 proves the CELL is 4 bytes but not the computed precision)"
                   p);
            Some (nm, { off; size = Bind.bytes_of rt; vk = Vflt; w = 0 })
        | Bind.RTbit 1 ->
            (* [E2E-11 step 1a] BIT(1) = one byte, high-bit justified
               [E20A/E20B/E20D/E20E: `dcl s1 bit(1) static initial('1'b)` lands
               at S(0000), `f = '1'b' emits MVI M,80 and `f = '0'b' MVI M,00].
               Bind already sizes bit(n) as (n+7)/8, which gives 1 here; the
               VALUE encoding (bit 7, not bit 0) is what the probes add. *)
            Some (nm, { off; size = 1; vk = Vbit1; w = 0 })
        | Bind.RTbit n ->
            failwith
              (Printf.sprintf
                 "codegen: BIT(%d) has no byte-level DR sample [TBD] (only                   BIT(1) is characterized: 1 byte, value in bit 7)" n)
        (* Symbolic/non-storage kinds legitimately carry no lowering yet.
           Storage kinds outside the int subset must FAIL LOUD (C067
           policy: never silently drop constructs). *)
        | Bind.RTentry _ | Bind.RTlabel | Bind.RTformat
        | Bind.RTbuiltin | Bind.RTstruct _ -> None
        | _ -> failwith
                 (Printf.sprintf
                    "codegen: declared variable kind not in supported \
                     subset [TBD]: %s" (Bind.rty_str rt)))
      rows
  in
  (* NOTE: built after `vars' -- the FILE names are collected as a side effect of
     that fold, so reading sy_files before it produced an empty list and ON
     ENDFILE then refused a perfectly well-declared FILE. *)
  let statics =
    { sy_total; sy_addrs = !sy_addrs; sy_cells = !sy_cells
    ; sy_files = !sy_files }   (* sy_total is the plain int bound just above; the
                                   ref of the same name is shadowed by then *)
  in
  let auto_bytes =
    let from_rows =
      List.fold_left
        (fun acc (nm, vi) ->
          if List.mem_assoc (String.lowercase_ascii nm) stat_set then acc
          else max acc (vi.off + vi.size))
        0 vars
    in
    (* A deduped formal's DECLARED size is not its COST, so for a module the
       section total -- not max(off+size) over rows -- is the authority [C136]. *)
    match bind_all.Bind.pl_top with Some _ -> bind_all.Bind.pl_total
                                  | None -> from_rows
  in
  let prog =
    match b.Ast.bname with Some n -> String.uppercase_ascii n.Ast.orig
                         | None -> failwith "codegen: main has no name"
  in
  (prog, auto_bytes, vars, statics)
