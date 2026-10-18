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

type vkind = Vint | Vfix of int | Vvar of int | Vdec of int * int
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
  ; mutable entries : (string * int) list (* lowered proc -> entry lc *)
  ; mutable fcalls : (string * int) list  (* pending forward CALL slots *)
  ; mutable deref : string list           (* ptr-formal names, cur scope *)
  ; mutable floor : int                   (* layout total (cells+procs) *)
  ; mutable vars : (string * var_info) list
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

let pool_bytes (s : string) =
  Array.init (String.length s) (fun i -> Char.code (String.get s i))

(* ---- opcodes (8080) : all cross-checked against DR .REL bytes ---- *)
let op_lxi_b = 0x01
let op_lxi_d = 0x11
let op_lxi_h = 0x21
let op_lhld = 0x2a
let op_shld = 0x22
let op_dad_d = 0x19
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

(* variable data-segment address = pool base + declared auto offset.
   [int subset has no pool => base 0; matches DR SHLD/LHLD operands] *)
let addr_of st name =
  let li = String.lowercase_ascii name in
  match List.assoc_opt li st.vars with
  | Some vi -> vi.off + st.base
  | None -> failwith ("codegen: undeclared " ^ name)

let vk_of st name =
  let li = String.lowercase_ascii name in
  match List.assoc_opt li st.vars with
  | Some vi -> vi.vk
  | None -> failwith ("codegen: undeclared " ^ name)

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
let op_jz   = 0xc4
let op_jp   = 0xf2
let op_jm   = 0xfa
let op_mov_a_m = 0x7e
let op_ora_m   = 0xb6
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
type pdec_ctx =
  { pd_vars : (string * vkind) list
  ; pd_procs : (string * (int * int) option) list
  ; pd_ret : (int * int) option
  ; pd_dec : (int * int * int) list ref
      (* [R614] distinct DEC literal cells already counted.  DR REUSES a
         decimal pool cell whose byte image is identical -- `d = 3; e = 3;`
         (both dec(9,2)) emits LXI H,* S(0000) twice against ONE 5-byte cell
         -- so pool DEMAND must count each distinct cell once.  Key is the
         packed image (precision, scale, scaled magnitude), i.e. exactly the
         byte content the lowering run compares in dec_pool. This replaces
         the E2E-6 assumption that DEC cells are never deduplicated, which
         was inferred from R505 (two literals, DIFFERENT values). *) }

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
        int_of_string (String.concat "" (String.split_on_char '_' s))
      in
      dec_pool_bytes (dec_digits (pint a))
      + dec_pool_bytes (dec_digits (pint b))
  | Ast.Ebinary (_, l, r) -> prescan_expr cx l + prescan_expr cx r
  | Ast.Eprefix (_, x) -> prescan_expr cx x
  | Ast.Ebuilt (_, es) ->
      List.fold_left (fun a x -> a + prescan_expr cx x) 0 es
  | _ -> 0

type chain = C2 of string * string * string   (* lit || var [W101] *)
           | C3 of string * string * string   (* lit || var || lit [W102] *)
type pitem = PIlit of string | PIvar of Ast.name | PInum of Ast.expr
type put_shape = Pnone | Plit of string option * string
               | Pvar of string option * Ast.expr
               | Pcat of string option * chain
               | Pitems of string option * pitem list

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
  | Ast.Esuffix (hd, [ _ ]) ->
      (* [RFACT @3B-46] function-call item: pair + LXI H,*A(slot) +
         CALL; the result already sits in HL when the numeric chain
         reads it (MVI A,9; QICOP follows the CALL directly) *)
      (match hd.Ast.e with
       | Ast.Eident _ -> Some (PInum x)
       | _ -> None)
  | _ -> None

let match_skip_ctl (items : Ast.put_item list) =
  match items with
  | Ast.Pi_ctl ("SKIP", Some { Ast.e = Ast.Enumber c; _ }) :: tl ->
      Some (Some c, tl)
  | Ast.Pi_ctl ("SKIP", None) :: tl ->
      Some (Some "1", tl)   (* bare SKIP = 1 [N302: MVI A,01] *)
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
  | Ast.Sput { stream = None; on_opts = []; kind = Ast.List_; items } ->
      let (sk, rest) =
        match match_skip_ctl items with
        | Some x -> x
        | None -> (None, items)
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

(* GET LIST (varying);) — single varying data item, default stream,
   no ON opts, no edit. Shapes beyond this raise [TBD] at lowering
   [X201/X202]. *)
let match_get_list_var (s : Ast.stmt) =
  match s.Ast.st with
  | Ast.Sget { stream = None; on_opts = []; kind = Ast.List_;
              items = [ Ast.Pi_data { Ast.e = Ast.Eident n; _ } ] } ->
      Some n.Ast.orig
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
  match (unwrap c).Ast.e with
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
      dec_store_bytes
      + (match rhs.Ast.e with
         | Ast.Estring v -> String.length v
             (* char-store pool demand [V101-V103/V105]; '' reserves 0
                [V104]; type-mismatched uses RAISE at lowering *)
         | _ -> prescan_expr cx rhs)
  | Ast.Sreturn (Some e0) ->
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
      (match match_put_list_lit s with
       | Plit (_, v) -> String.length v
       | Pcat (_, C2 (l, _, _)) -> String.length l
       | Pcat (_, C3 (l, _, r)) -> String.length l + String.length r
       | Pitems (_, its) ->
           List.fold_left
             (fun a it -> match it with
              | PIlit v -> a + String.length v
              | PInum x -> a + prescan_expr cx x
              | PIvar _ -> a) 0 its
       | _ -> 0)             (* var-puts consume no pool [V101] *)
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
        (fun a x -> a + prescan_stmt { cx with pd_ret = ret } x) 0
        b.Ast.blk.Ast.bstmts
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
let lower_put_lit st (skipn : string option) (v : string) =
  d st op_lxi_d; d st 0x52; d st 0x02;
  d st op_lxi_b;
  let bslot = st.lc in
  d st 0; d st 0;
  call_ext st "?SYSPR";
  (match skipn with
   | Some c ->
       let n = int_of_string (String.concat "" (String.split_on_char '_' c)) in
       if n <= 0 || n > 255 then
         failwith "codegen: skip count out of MVI range [TBD]";
       d st op_mvi_a; d st n; call_ext st "?SKPOP"
   | None -> ());
  let bytes =
    Array.init (String.length v) (fun i -> Char.code (String.get v i))
  in
  let addr = pool_alloc st bytes in
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
  | _ -> 1


(* assemble: header ; [SET-LC data + pool bytes] ; DEF-DATA-SIZE ;
   SET-LC code ; prologue ; body ; epilogue ; tail.  Body is lowered
   into a scratch state (collecting code items + pool bytes), then
   re-emitted in segment order. *)

let parse_int_const (s : string) =
  int_of_string (String.concat "" (String.split_on_char '_' s))

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
let rec lower_hl st (e : Ast.expr) =
  match e.Ast.e with
  | Ast.Enumber s ->
      let v = int_of_string (String.concat "" (String.split_on_char '_' s)) in
      d st op_lxi_h; d st (v land 0xff); d st ((v lsr 8) land 0xff)
  | Ast.Esuffix (hd, args) ->
      (* [E2E-5c P401] single-argument internal procedure call.
         Deferred pointer pair + LXI H,*A(cell) + CALL; forward entry
         via CHAIN-ADDR resolved at the procedure's first byte, known
         entry via inline RELOC(code,entry) [P402 backward pattern] *)
      begin match hd.Ast.e, args with
      | Ast.Eident h, [ arg ] ->
          let nm = String.lowercase_ascii h.Ast.orig in
          if not (List.mem_assoc nm st.procs) then
            failwith
              (Printf.sprintf "codegen: call to unknown %s [TBD]" nm);
          (match st.calls with
           | (cs :: rest) when cs.Bind.cs_proc = nm ->
               st.calls <- rest;
               let target =
                 match cs.Bind.cs_temp with
                 | Some t ->
                     (* expression argument [RFACT @80-84, P402
                        @4D-51]: evaluate to HL, runtime SHLD into the
                        prescan-paired temp cell; the deferred pair
                        then links slot -> temp *)
                     lower_hl st cs.Bind.cs_arg;
                     d st op_shld;
                     reloc st Data (t + st.base);
                     t + st.base
                 | None -> begin
                     match cs.Bind.cs_arg.Ast.e with
                     | Ast.Enumber k ->
                         let kv =
                           int_of_string
                             (String.concat ""
                                (String.split_on_char '_' k))
                         in
                         pool_alloc st
                           [| kv land 0xff; (kv lsr 8) land 0xff |]
                     | Ast.Eident v ->
                         let vn = String.lowercase_ascii v.Ast.orig in
                         if List.mem vn st.deref then
                           failwith
                             "codegen: pointer-formal call argument \
                              unproven [TBD]";
                         addr_of st v.Ast.orig
                     | _ ->
                         failwith
                           "codegen: expression call argument \
                            deferred [TBD]"
                   end
               in
               let slot = cs.Bind.cs_slot + st.base in
               link st t_set_lc (Some (Data, slot)) None;
               push st (Reloc (Data, target));
               link st t_set_lc (Some (Code, st.lc)) None;
               d st op_lxi_h; reloc st Data slot;
               d st op_call;
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
                    d st 0; d st 0;
                    st.fcalls <- (nm, oslot) :: st.fcalls);
               st.last_imm <- None
           | _ -> failwith "codegen: call-site queue mismatch [TBD]")
      | _ -> failwith "codegen: multi-arg call deferred [TBD]"
      end
  | Ast.Eident n ->
      (match vk_of st n.Ast.orig with
       | Vint -> ()
       | Vdec _ ->
           failwith
             "codegen: decimal operand inside an integer expression [TBD] \
              (mixed-mode routes are unpinned)"
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
  | Ast.Ebinary (Ast.Add, l, { Ast.e = Ast.Enumber "1"; _ }) ->
      (* [(a+1) N304] +1 lowers to INX H on the 2-byte path; other
         additions keep the general ladder *)
      lower_hl st l; d st op_inx_h; st.last_imm <- None
    | Ast.Ebinary (Ast.Add, l, r) ->
      (* DR: HL=left ; XCHG ; HL=right ; DAD D  (=> HL = right+left)
         [P071A]. WITH POINTER-DEREF OPERANDS the ladder is
         left ; PUSH H ; right ; POP D ; DAD D [P401 dbl (i+i):
         E5 @37, D1 @3F] — forced by mechanics: the deref ladder's own
         XCHG (EB) clobbers DE, so the XCHG form cannot preserve the
         left value across a second deref. *)
      if hl_operand_deref st l || hl_operand_deref st r then begin
        lower_hl st l; d st 0xe5;                    (* PUSH H *)
        lower_hl st r; d st 0xd1; d st op_dad_d      (* POP D; DAD D *)
      end else begin
        lower_hl st l; d st op_xchg; lower_hl st r; d st op_dad_d
      end
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
             int_of_string (String.concat "" (String.split_on_char '_' c))
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
             int_of_string (String.concat "" (String.split_on_char '_' c))
           in
           lower_hl st l; d st op_mvi_a; d st (n land 0xff);
           call_ext st "?IEXOP"
       | (Ast.Eident _, _) -> failwith "codegen: ** non-constant exponent [TBD]"
       | (Ast.Enumber bs, Ast.Enumber cs) ->
           let k =
             int_of_string (String.concat "" (String.split_on_char '_' bs))
           in
           let e =
             int_of_string (String.concat "" (String.split_on_char '_' cs))
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
      (* mod(a,b) -> DE=a, HL=b, CALL ?IMDOP [P071B L4] *)
      lower_hl st l; d st op_push_h; lower_hl st r; d st op_pop_d;
      call_ext st "?IMDOP"
  | Ast.Eprefix (Ast.Minus, x) ->
      (* [N304] -x: evaluate to HL, then ?IN20N (16-bit negate) *)
      lower_hl st x; call_ext st "?IN20N"; st.last_imm <- None
  | Ast.Ebinary _ -> failwith "codegen: operator not in int subset [TBD]"
  | _ -> failwith "codegen: expression form not in int subset [TBD]"

(* subtract an integer constant: DR folds 1 -> DCX H, small n -> repeated
   DCX H (<=4 observed); anything larger is out of this subset. *)
and const_sub st n =
  if n = 1 then d st op_dcx_h
  else if n > 1 && n <= 4 then for _ = 1 to n do d st op_dcx_h done
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
      let addr = pool_alloc st bytes in
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
        let addr = pool_alloc st bytes in
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

(* push a DEC value on the decimal stack; tgt = Some(p,s) when the value
   is being produced for a DEC assignment/return (bare literals then take
   the TARGET's digits+scale), None in operand position (literals keep
   their own digit count).  Returns the pushed value's (p,s). *)
let rec dec_push st (tgt : (int * int) option) (e : Ast.expr) : int * int =
  (* parenthesised expressions arrive Econd-wrapped [N304 precedent: PUT
     items and RETURN (..) do this]; the parens carry no codegen meaning *)
  match (match e.Ast.e with Ast.Econd x -> x.Ast.e | k -> k) with
  | Ast.Eident n ->
      (match vk_dec_opt st n with
       | Some (p, s) ->
           d st op_lxi_h; reloc st Data (addr_of st n.Ast.orig);
           d st op_mvi_a; d st p; call_ext st "?DLDOP"; (p, s)
       | None ->
           failwith (Printf.sprintf
                       "codegen: decimal operation on non-decimal operand %s \
                        [TBD]" n.Ast.orig))
  | Ast.Ebuilt ("DECIMAL", args) ->
      (* decimal(x,p): DR IGNORES p [R506: decimal(i,15) and decimal(i,7)
         compile to the identical LHLD/?QI15D pair]; x stays an integer
         expression and ?QI15D converts the HL value *)
      (match args with
       | [ x ] | [ x; _ ] -> lower_hl st x; call_ext st "?QI15D"
       | _ -> failwith "codegen: DECIMAL builtin arity [TBD]") ;
      (match tgt with Some ps -> ps | None -> (15, 0))
  | Ast.Esuffix _ ->
      (* DEC function call: identical call-site bytes to the FIXED ABI
         [DFACT @003B-LX I H,*A(001C); CALL], but ?DCRET leaves the result
         on the decimal stack instead of HL *)
      lower_hl st e;
      dec_edit_pt st e
  | Ast.Ebinary (op, l, r) ->
      let opn =
        match op with
        | Ast.Mul -> "?DMUOP"
        | Ast.Add -> "?DADOP"
        | Ast.Sub -> "?DSUOP"
        | _ ->
            failwith
              "codegen: decimal operator not in the DEC subset [TBD] \
               (divide/compare/mod/exp not pinned)"
      in
      (* operand push order: right-first only in the observed case where
         the right operand is itself a DEC call [DFACT] *)
      let right_first =
        match r.Ast.e with Ast.Esuffix _ -> true | _ -> false
      in
      (* [R608] ADD/SUB ALIGN SCALES: `p = p - 1` against a dec(9,2)
         variable pushes the literal as a 9-DIGIT cell holding 1.00
         (pool S(000A) = 00 01 00 00 00, MVI A,09) -- NOT the own-digit,
         scale-0 form that MULTIPLY/DIVIDE use [R509 `*2` A=01, R511
         `*1234` A=04, LOAN1 `/1200` A=04 (2-byte cell S(0028) = 00 12)].
         So an additive literal is pre-scaled to its DEC PARTNER's
         (p,s).  Only that partner-driven case is pinned: when the partner
         precision is unknown, or the store target disagrees with the
         partner, no sample says which wins, so it refuses. *)
      let additive = match op with Ast.Add | Ast.Sub -> true | _ -> false in
      let static_ps x =
        match (match x.Ast.e with Ast.Econd y -> (y : Ast.expr) | _ -> x).Ast.e with
        | Ast.Eident n -> vk_dec_opt st n
        | Ast.Esuffix (b, _) ->
            (match b.Ast.e with
             | Ast.Eident n ->
                 (match List.assoc_opt (String.lowercase_ascii n.Ast.orig)
                          st.procs with
                  | Some pl ->
                      (match pl.Bind.pl_ret with
                       | Some (Bind.RTdec (a1, a2)) -> Some (a1, a2)
                       | _ -> None)
                  | None -> None)
             | _ -> None)
        | _ -> None
      in
      let push_operand partner x =
        let ux = match x.Ast.e with Ast.Econd y -> y | _ -> x in
        if additive && match ux.Ast.e with Ast.Enumber _ -> true | _ -> false
        then
          match partner with
          | None ->
              failwith
                "codegen: decimal +/- literal precision source unproven                  [TBD] (partner is not a DEC variable or DEC function                  call; only the partner-aligned form is pinned [R608])"
          | Some ps ->
              (match tgt with
               | None -> ()
               | Some t when t <> ps ->
                   failwith
                     "codegen: decimal +/- literal: partner and store target                       precisions differ [TBD] (no sample says which one DR                       aligns the literal to)"
               | Some _ -> ());
              ignore (dec_push st (Some ps) ux)
        else ignore (dec_push st None ux)
      in
      let push_pair () =
        if right_first then begin
          let rp = static_ps r in
          push_operand (static_ps l) r; push_operand rp l
        end else begin
          let lp = static_ps l in
          push_operand (static_ps r) l; push_operand lp r
        end
      in
      push_pair ();
      call_ext st opn;
      (* multiply rescales to the TARGET scale, and only when that scale
         is non-zero [R505 vs R510/DFACT] *)
      (match op, tgt with
       | Ast.Mul, Some (_, s) when s > 0 ->
           d st op_mvi_a; d st s; call_ext st "?QDDSR"
       | _ -> ());
      (match tgt with Some ps -> ps | None -> (15, 0))
  | Ast.Enumber s ->
      let (v, own_digits, lscale) = dec_lit_value s in
      let (p, sc) =
        match tgt with
        | Some (tp, ts) -> (tp, ts)
        (* operand position: the literal's own digit count, scale 0
           [R509 *2 -> MVI A,01; R511 *1234 -> MVI A,04] *)
        | None -> (own_digits, 0)
      in
      ignore (v, lscale);
      (* literal scale <= target scale is scaled up by dec_pool: `a = 1`
         into dec(9,2) becomes the cell 100 [R505 bytes 00 01 00 00 00],
         and d = 123.45 into dec(7,2) stays 12345 [R508].  ls > sc would
         lose digits -- refused inside dec_pool. *)
      if lscale > 0 && tgt = None then
        failwith "codegen: fractional DEC literal in operand position [TBD]";
      let addr = dec_pool st ~prec:p ~scale:sc ~text:s in
      d st op_lxi_h; reloc st Data addr;
      d st op_mvi_a; d st p; call_ext st "?DLDOP"; (p, sc)
  | _ ->
      failwith (Printf.sprintf
                  "codegen: decimal expression shape %s not in the DEC \
                   subset [TBD]"
                  (expr_kind_name e.Ast.e))

(* ---- [E2E-7A slice 1] helpers for DECIMAL comparison -------------- *)
let unwrap_e (e : Ast.expr) =
  match e.Ast.e with Ast.Econd x -> x | _ -> e

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

let lower_test_skip st (c : Ast.expr) =
  match c.Ast.e with
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
      call_ext st "?DCMOP";
      d st opc;
      let slot = st.lc in d st 0; d st 0; slot
  | Ast.Ebinary (Ast.EqR Ast.Eq, { Ast.e = Ast.Eident v; _ },
                 { Ast.e = Ast.Enumber "0"; _ }) ->
      d st op_lxi_h; reloc st Data (addr_of st v.Ast.orig);
      d st op_mov_a_m; d st op_inx_h; d st op_ora_m;
      d st op_jnz; let slot = st.lc in d st 0; d st 0; slot
  | Ast.Ebinary (Ast.EqR Ast.Gt, { Ast.e = Ast.Eident v; _ },
                 { Ast.e = Ast.Enumber k; _ }) ->
      let kk = parse_int_const k in
      if kk < 1 then failwith "codegen: compare > k<=0 form unproven [TBD]";
      d st op_lhld; reloc st Data (addr_of st v.Ast.orig);
      let m = (-(kk + 1)) land 0xffff in
      d st op_lxi_b; d st (m land 0xff); d st ((m lsr 8) land 0xff);
      d st op_dad_b; d st op_mov_a_h; d st op_ora_a;
      d st op_jm; let slot = st.lc in d st 0; d st 0; slot
  | Ast.Ebinary (Ast.EqR Ast.Ne, { Ast.e = Ast.Eident v; _ },
                 { Ast.e = Ast.Enumber k; _ }) ->
      (* [Y303/Y306] i ^= kk -> LHLD; (DCX H)*kk; MOV A,H; ORA L;
         skip-when-equal = CA (the ^= skip byte quirk [C072]).
         DR's switch to a cheaper ladder for large kk unproven:
         cap 8, above -> [TBD] *)
      let kk = parse_int_const k in
      if kk < 1 || kk > 8 then
        failwith "codegen: ^= const range unproven [TBD]";
      d st op_lhld; reloc st Data (addr_of st v.Ast.orig);
      for _ = 1 to kk do d st op_dcx_h done;
      d st op_mov_a_h; d st 0xb5;      (* ORA L *)
      d st 0xca;
      let slot = st.lc in d st 0; d st 0; slot
  | Ast.Ebinary (Ast.EqR Ast.Lt, { Ast.e = Ast.Eident v; _ },
                 { Ast.e = Ast.Enumber k; _ }) ->
      (* [Z401/Z405] i < kk: LHLD; (DCX H)*kk; MOV A,H; ORA A;
         JP(F2) -> skip. NOTE ORA A here vs ORA L in the ^= form.
         DR's switch point to a cheaper ladder for large kk
         unproven: cap 8, above -> [TBD] *)
      let kk = parse_int_const k in
      if kk < 1 || kk > 8 then
        failwith "codegen: < const range unproven [TBD]";
      d st op_lhld; reloc st Data (addr_of st v.Ast.orig);
      for _ = 1 to kk do d st op_dcx_h done;
      d st op_mov_a_h; d st op_ora_a;
      d st op_jp;
      let slot = st.lc in d st 0; d st 0; slot
  | Ast.Ebinary (Ast.EqR r, l, rr) when is_ident l && is_ident rr ->
      let ident = fun x ->
        match x.Ast.e with Ast.Eident n -> n.Ast.orig | _ -> assert false
      in
      (match r with
       | Ast.Lt | Ast.Ge ->
           d st op_lhld; reloc st Data (addr_of st (ident l));
           d st op_xchg;
           d st op_lhld; reloc st Data (addr_of st (ident rr));
           call_ext st "?IS22N";
           d st (if r = Ast.Lt then op_jp else op_jm)
       | Ast.Gt | Ast.Le ->
           d st op_lhld; reloc st Data (addr_of st (ident rr));
           d st op_xchg;
           d st op_lhld; reloc st Data (addr_of st (ident l));
           call_ext st "?IS22N";
           d st (if r = Ast.Gt then op_jp else op_jm)
       | Ast.Eq | Ast.Ne ->
           d st op_lhld; reloc st Data (addr_of st (ident l));
           d st op_push_h;
           d st op_lhld; reloc st Data (addr_of st (ident rr));
           d st op_pop_d;
           call_ext st "?IS22N";
           d st op_mov_a_h; d st 0xb5;  (* ORA L *)
           d st (if r = Ast.Eq then op_jnz else 0xca));  (* DR: ^= skip = JPE, not JZ: parity-defect [C072] *)
      let slot = st.lc in d st 0; d st 0; slot
  | _ -> failwith (Format.asprintf "codegen: condition form not in E2E-3b subset [TBD]: %a" Parser.pp_e c)

let lower_assign st (lhs : Ast.expr) (rhs : Ast.expr) =
  (match lhs.Ast.e with
   | Ast.Eident n ->
       if List.mem (String.lowercase_ascii n.Ast.orig) st.deref then
         failwith
           "codegen: store to pointer formal unproven [TBD]"
   | _ -> ());
  match lhs.Ast.e with
  | Ast.Eident n when vk_dec_opt st n <> None ->
      (* [E2E-6] FIXED DECIMAL store: push the DEC value (with the target's
         precision as the literal context), then ?DSTOP pops it into the
         cell [R501/R502/R503/R505/R508/R510/R511] *)
      st.last_imm <- None;
      let (p, _s) = Option.get (vk_dec_opt st n) in
      ignore (dec_push st (Some (p, _s)) rhs);
      d st op_lxi_h; reloc st Data (addr_of st n.Ast.orig);
      d st op_mvi_a; d st p; call_ext st "?DSTOP"
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
           d st op_mvi_a; d st k
       | _ -> lower_hl st rhs; d st 0x7d (* MOV A,L *)) ;
      (* 1-byte store: DR emits opcode 0x32 with the inline-reloc
         16-bit address ($C prints 'STA'; byte replicated literally
         [N303/N306/N308], same family of byte-vs-mnemonic quirks
         as CA/F2 — runtime identity comes from byte-identical COM) *)
      d st 0x32; reloc st Data (addr_of st n.Ast.orig)
  | Ast.Eident n when is_dec_expr st rhs ->
      (* [E2E-6/R506] DEC -> INT: push the decimal value, convert with
         ?QDI15 (16-bit result in HL), then the ordinary integer store.
         R506 line 6 exactly: LXI H,D A(0002) ; MVI A,0F ; CALL ?DLDOP ;
         CALL ?QDI15 ; SHLD I A(0000).  The DLDOP precision is the
         SOURCE decimal's, not the target's. *)
      let vi = List.assoc (String.lowercase_ascii n.Ast.orig) st.vars in
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
       | Ast.Ebinary (Ast.Add, { Ast.e = Ast.Eident m; _ },
                      { Ast.e = Ast.Enumber "1"; _ })
         when String.lowercase_ascii m.Ast.orig
              = String.lowercase_ascii n.Ast.orig ->
           (* [Z401/Z403/Z404] x = x + 1 -> LHLD; INX H; SHLD.
              HL holds a RUNTIME value afterwards: last_imm is
              constant-tracking only -> None. -1/INX-variant forms
              unproven, stay on the generic path. *)
           st.last_imm <- None;
           d st op_lhld; reloc st Data (addr_of st n.Ast.orig);
           d st op_inx_h
           (* final SHLD comes from the common tail *)
       | _ ->
           st.last_imm <- None;
           lower_hl st rhs);
      d st op_shld; reloc st Data (addr_of st n.Ast.orig)
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

(* GET LIST(n);) n char-varying [X201/X202]: input descriptor 0290
   (vs 0252 for print); SYSIN attaches, GNVOP reads item(s) onto the
   RTL stack; JP(F2) operand triple-patched to the QIOOP call start
   (EOF/error skips the store, NOT the QIOOP); SSVFS stores stack->var
   with B = capacity; QIOOP completes I/O; LXI B continuation triple ->
   next stmt. Record-stream order (X202 dump): after the SSVFS chain
   comes the JP triple, then QIOOP data, then the continuation triple. *)
let lower_get st (nm : string) =
  if List.mem (String.lowercase_ascii nm) st.deref then
    failwith "codegen: GET into pointer formal unproven [TBD]";
  let cap = match vk_of st nm with
            | Vvar c -> if c > 255 then failwith "codegen: cap > 255 [TBD]"
                        else c
            | _ -> failwith
                "codegen: GET LIST of non-varying var unproven [TBD]"
  in
  d st op_lxi_d; d st 0x90; d st 0x02;   (* LXI D,0290 input desc *)
  d st op_lxi_b;
  let bslot = st.lc in
  d st 0; d st 0;
  call_ext st "?SYSIN";
  call_ext st "?GNVOP";
  d st op_jp;
  let jpslot = st.lc in
  d st 0; d st 0;
  d st op_lxi_h; reloc st Data (addr_of st nm);
  d st op_mvi_b; d st cap;
  call_ext st "?SSVFS";
  emit_triple st jpslot st.lc;          (* JP -> QIOOP call start *)
  call_ext st "?QIOOP";
  emit_triple st bslot st.lc            (* continuation = next stmt *)

(* PUT LIST with || chain: DR evaluates RIGHT-to-LEFT while the
   pool is allocated LEFT-to-RIGHT in source order [W102 hex:
   HELLO@5, BYE@0x0B]. C2: SLVTS(right var; empty stack -> no PUSH
   PSW) then SJSCM(lit in B). C3: SLCTS(right lit in A); PUSH PSW;
   SLVTS(var); SJSCM(left lit in B); SJSTS. Tail = the standard
   PNCOP/QIOOP + continuation triple [W101/W102]. *)
let lower_cat st (skipn : string option) (ch : chain) =
  let maxlit = match ch with C2 (l, _, _) -> String.length l
               | C3 (l, _, r) -> max (String.length l) (String.length r) in
  if maxlit > 255 then failwith "codegen: lit > 255 [TBD]";
  d st op_lxi_d; d st 0x52; d st 0x02;
  d st op_lxi_b;
  let bslot = st.lc in
  d st 0; d st 0;
  call_ext st "?SYSPR";
  (match skipn with
   | Some c ->
       let n = parse_int_const c in
       if n <= 0 || n > 255 then
         failwith "codegen: skip count out of MVI range [TBD]";
       d st op_mvi_a; d st n; call_ext st "?SKPOP"
   | None -> ());
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
    | _ -> false
  in
  if while_ <> None
     || (to_ <> None && rep <> None)
     || (rep <> None && not proven_repeat && not forever_repeat) then
    failwith "codegen: DO WHILE/REPEAT combo/UNTIL deferred [TBD]";
  (match by with
   | None -> ()
   | Some { Ast.e = Ast.Enumber "1"; _ } -> ()
   | _ -> failwith "codegen: DO step unproven [TBD]");
  let fromv =
    match from with
    | { Ast.e = Ast.Enumber c; _ } -> parse_int_const c
    | _ -> failwith "codegen: DO non-constant FROM unproven [TBD]"
  in
  if List.mem (String.lowercase_ascii ind.Ast.orig) st.deref then
    failwith "codegen: DO control is a pointer formal [TBD]";
  let iaddr =
    match vk_of st ind.Ast.orig with
    | Vint -> addr_of st ind.Ast.orig
    | _ -> failwith "codegen: DO index not fixed-bin [TBD]"
  in
  (* init [Y302: INX H reuse when last_imm = from-1] *)
  (if st.last_imm = Some (fromv - 1) then
     (d st op_inx_h; st.last_imm <- Some fromv)
   else
     (d st op_lxi_h; d st (fromv land 0xff);
      d st ((fromv lsr 8) land 0xff);
      st.last_imm <- Some fromv));
  d st op_shld; reloc st Data iaddr;
  if proven_repeat || forever_repeat then begin
    (* [Z402] body-head is the FIRST BODY instruction (not the
       init); tail increment LHLD/INX/SHLD; JMP back; no test.
       [R414/R426] at the window address the increment is
       LHLD; LXI H,const; DAD D; SHLD; JMP instead. *)
    let head = st.lc in
    lo st ls body;
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
     | _ -> failwith "codegen: REPEAT increment form [TBD]");
    d st op_shld; reloc st Data iaddr;
    d st op_jmp; reloc st Code head;
    st.last_imm <- None
  end else begin
  let head, jpslot =
    match to_ with
    | Some { Ast.e = Ast.Enumber c; _ } ->
        let b = parse_int_const c in
        let head = st.lc in
        d st op_lhld; reloc st Data iaddr;
        let neg = -(b + 1) in
        d st op_lxi_b; d st (neg land 0xff);
        d st ((neg lsr 8) land 0xff);
        d st op_dad_b; d st op_mov_a_h; d st op_ora_a;
        d st op_jp;
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
  d st op_inx_h;
  d st op_shld; reloc st Data iaddr;
  d st op_jmp;
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
    | Ast.Esuffix (hd, [ _ ]) ->
        let hn =
          match hd.Ast.e with
          | Ast.Eident h -> String.lowercase_ascii h.Ast.orig
          | _ -> ""
        in
        if List.mem_assoc hn st.procs then
          (* result of a RETURNS FIXED procedure: default bin(15)
             width [HYPOTHESIS for returns BIN(p): no evidence yet] *)
          9
        else failwith "codegen: PUT numeric item form unproven [TBD]"
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
let lower_put_items st (skipn : string option) (items : pitem list) =
  let char_var_ok =
    List.length items = 1 ||
    not (List.exists (function PIvar n ->
                        (match vk_of st n.Ast.orig with
                         | Vint -> false | Vdec _ -> false | _ -> true)
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
   | Some c ->
       let n = parse_int_const c in
       if n <= 0 || n > 255 then
         failwith "codegen: skip count out of MVI range [TBD]";
       d st op_mvi_a; d st n; call_ext st "?SKPOP"
   | None -> ());
  List.iter
    (fun it ->
      match it with
      | PIlit v ->
          let len = String.length v in
          if len > 255 then failwith "codegen: literal > 255 [TBD]";
          let addr = pool_alloc st (pool_bytes v) in
          d st op_lxi_h; reloc st Data addr;
          d st op_mvi_a; d st len;
          call_ext st "?SLCTS"; call_ext st "?PNCOP"
      | PIvar n ->
          (match vk_of st n.Ast.orig with
           | Vdec (p, s) ->
               (* [R501/R502/R503/R508/R510/R511] DEC variable item = DLDOP
                  then QDCOP(width=p+3, scale=s); R506 proves a DEC var in a
                  MULTI-item list next to an INT var *)
               d st op_lxi_h; reloc st Data (addr_of st n.Ast.orig);
               d st op_mvi_a; d st p; call_ext st "?DLDOP";
               d st op_mvi_a; d st (p + 3); d st op_mvi_b; d st s;
               call_ext st "?QDCOP"; call_ext st "?PNVOP"
           | Vint ->
               let vi =
                 List.assoc (String.lowercase_ascii n.Ast.orig) st.vars
               in
               lower_hl st { Ast.e = Ast.Eident n;
                             Ast.epos = n.Ast.pos };
               d st op_mvi_a; d st vi.w;
               call_ext st "?QICOP"; call_ext st "?PNVOP"
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
                | Vint -> assert false);
               call_ext st "?PNCOP")
      | PInum x ->
          if is_dec_expr st x then begin
            (* [DFACT] a DEC function-call item leaves its result on the
               decimal stack; the edit pair follows directly *)
            let (p, s) = dec_edit_pt st x in
            ignore (dec_push st None x);
            d st op_mvi_a; d st (p + 3); d st op_mvi_b; d st s;
            call_ext st "?QDCOP"; call_ext st "?PNVOP"
          end else begin
            lower_hl st x;
            d st op_mvi_a; d st (num_width st x);
            call_ext st "?QICOP"; call_ext st "?PNVOP"
          end)
    items;
  call_ext st "?QIOOP";
  emit_triple st bslot st.lc

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
  if (not st.in_proc) && not st.stop_seen && not st.after_forever
  then begin
    if st.guards = 0 then begin
      st.guards <- st.guards + 1;
      d st op_jmp;
      st.guard_slots <- st.lc :: st.guard_slots;
      d st 0; d st 0
    end
    else
      (* A SECOND appended proc in a guarded shape is unproven: no
         golden has two top-level procedures. Refuse rather than
         extrapolate DR's behavior. *)
      failwith
        "codegen: second appended procedure after a tail guard \
         [TBD: unproven, no multi-procedure golden]"
  end;
  if not st.in_proc then st.appended <- true;
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
  (match hits with
   | [] -> ()
   | [ (_, one) ] -> link st t_chain_addr (Some (Code, one)) None
   | _ ->
       failwith "codegen: multiple forward CALL chain unproven [TBD]");
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
   | _ -> failwith "codegen: multi-formal prologue deferred [TBD]");
  let saved = st.vars and savedd = st.deref in
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
             else
               { off = o; size = Bind.bytes_of rt; vk = Vdec (p, s);
                 w = p + 3 }
         | _ ->
             failwith "codegen: non fixed-bin procedure local [TBD]"))
      pl.Bind.pl_rows @ saved;
  st.deref <-
    (* recursive bodies read the SHADOW value cell with plain ladders
       [RFACT @80: LHLD I(12); DCX H — no deref] *)
    (if pl.Bind.pl_rec then [] else List.map fst pl.Bind.pl_ptrs);
  let savedp = st.in_proc and savedr = st.in_rec
      and saveddr = st.dec_ret in
  st.dec_ret <-
    (match pl.Bind.pl_ret with
     | Some (Bind.RTdec (p, s)) -> Some (p, s)
     | _ -> None);
  st.in_proc <- true;
  st.in_rec <- pl.Bind.pl_rec;
  List.iter (fun x -> lower_stmt st ls x) pl.Bind.pl_body;
  st.dec_ret <- saveddr;
  st.in_rec <- savedr;
  st.in_proc <- savedp;
  st.vars <- saved;
  st.deref <- savedd
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
  match s.Ast.st with
  | Ast.Sassign { lhs; rhs } ->
      st.lowered <- st.lowered + 1; lower_assign st lhs rhs
  | Ast.Sput _ ->
      st.lowered <- st.lowered + 1; st.last_imm <- None;
      (match match_put_list_lit s with
       | Plit (skipn, v) -> lower_put_lit st skipn v
       | Pcat (skipn, ch) -> lower_cat st skipn ch
       | Pitems (sk, its) -> lower_put_items st sk its
       | Pnone -> failwith
             (Printf.sprintf
                "codegen: PUT form not in E2E-3a subset [TBD] \
                 (line %d)" s.Ast.spos.Source.line))
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
      if cond.Ast.e = Ast.Ebit "1" then begin
        (* constant-true bit condition = pure forever, NO test
           [Z404: COPY's DO WHILE('1'B)] *)
        lower_stmt st ls body;
        d st op_jmp; reloc st Code head;
        if not st.in_proc then begin
          (* WHILE('1'B): no test insn; tail address = the JMP
             operand address [head+4] [R408] *)
          st.after_forever <- true;
          st.last_loop_edge <- head + 4
        end
      end else begin
        let slot = lower_test_skip st cond in
        lower_stmt st ls body;
        d st op_jmp; reloc st Code head;
        emit_triple st slot st.lc            (* [Z401: after JMP] *)
      end
  | Ast.Sdoforever body ->
      (* bare DO; .. END; [Z403] body then unconditional JMP back *)
      st.lowered <- st.lowered + 1; st.last_imm <- None;
      let head = st.lc in
      lower_stmt st ls body;
      d st op_jmp; reloc st Code head
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
        match (to_, while_, rep) with
        | (None, None, Some _) -> true
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
           d st op_jmp;
           let exit_slot = st.lc in
           d st 0; d st 0;
           emit_triple st skip st.lc;      (* skip -> else start [G114] *)
           lower_stmt st ls e;
           emit_triple st exit_slot st.lc) (* fall-around else -> exit *)
  | Ast.Sgoto { tgt; subscript = [] } ->
      st.lowered <- st.lowered + 1; st.last_imm <- None;
      let nm = String.lowercase_ascii tgt.Ast.orig in
      (match List.assoc_opt nm ls.labs with
       | Some a -> d st op_jmp; reloc st Code a        (* backward [G115] *)
       | None ->
           d st op_jmp;
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
           d st op_jmp;
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
  | Ast.Sprocedure_stmt _ ->
      failwith "codegen: CALL statement deferred [TBD]"
  | Ast.Sdcl _ -> ()
  | Ast.Snull _ -> ()
  | _ -> failwith
         (Printf.sprintf "codegen: statement kind not in supported subset \
                          [TBD] (line %d)" s.Ast.spos.Source.line)


let emit_program (progname : string) (auto_bytes : int)
    (rows : (string * var_info) list) (stmts : Ast.stmt list)
    (blk : Ast.block) =
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
             ^ "; return types emitted today are FIXED [26 specimens] and "
             ^ "FIXED DECIMAL(p<=15) [E2E-6]; FLOAT/CHAR/BIT/POINTER/ENTRY "
             ^ "each need their own ABI evidence)")
    | _ -> ()
  in
  let check_bopts (line : int) (opts : (string * Ast.expr list) list) =
    List.iter
      (fun (k, args) ->
        if not (String.equal (String.lowercase_ascii k) "main"
                && args = []) then
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
  let layout = Bind.bind_program blk in
  (* constant call arguments allocate 2B little-endian pool cells
     [P401: '2' at data@0]; included in the pool prescan total so
     pool-relative layout matches the lowering-time allocation run *)
  let const_cells =
    List.fold_left
      (fun a (c : Bind.call_site) ->
        match c.cs_arg.Ast.e with
        | Ast.Enumber _ -> a + 2
        | _ -> a)
      0 layout.pl_calls
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
  let pool_total =
    prescan_pool { pd_vars; pd_procs; pd_ret = None
                    ; pd_dec = ref [] } stmts + const_cells
  in
  let st =
    { base = pool_total; items = []; pool = []
    ; pool_next = 0; dec_cells = []; lc = 0; last_imm = None; lowered = 0; temps = 0
    ; stop_seen = false; calls = layout.pl_calls
    ; procs =
        List.map
          (fun (p : Bind.proc_layout) -> (p.pl_name, p))
          layout.pl_procs
    ; entries = []; fcalls = []; deref = []
    ; floor = layout.pl_total; vars = rows
    ; dec_ret = None
    ; in_proc = false; in_rec = false
    ; after_forever = false; guards = 0; guard_slots = []
    ; appended = false; secs = layout.Bind.pl_secs
    ; last_loop_edge = 0 }
  in
  (* lower prologue + body + epilogue into st.items (code segment) *)
  d st op_lxi_b; d st 0x00; d st 0x02;
  d st op_call;
  let start_slot = st.lc in
  d st 0; d st 0;
  link st t_chain_ext (Some (Code, start_slot)) (Some "?START");
  let ls = { labs = []; fwd = [] } in
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
                 procedure [TBD: unproven DR append layout]");
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
  (match ls.fwd with
   | [] -> ()
   | (nm, _) :: _ ->
       failwith (Printf.sprintf
                   "codegen: GOTO to undefined/unresolvable label %s \
                    [TBD: DR pass-2 UNDEF diag]" nm));
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
  if not st.stop_seen && not tail_displaced then begin
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
       to [TBD: unproven DR shape (no-exit main tail AFTER an \
       appended procedure)]";
  let code_items = st.items in
  (* now build the ordered full item list *)
  let data_size =
    pool_total + max auto_bytes layout.pl_total + 2 * st.temps
  in
  let header =
    [ Link (t_progname, None, Some progname)
    ; Link (t_req_library, None, Some "PLILIB")
    ; Link (t_extdef, None, Some progname)
    ; Link (t_def_public, Some (Code, 0), Some progname) ]
  in
  let data_seg =
    if st.pool <> [] then
      Link (t_set_lc, Some (Data, 0), None)
      ::
      (let sorted =
         List.sort (fun (a, _) (b, _) -> compare a b) st.pool in
       (* each pool block: SET-LC(data,addr) for addr>0 then its bytes;
          block 0 rides the header SET-LC(data,0) [G113] *)
       List.concat_map
         (fun (addr, bs) ->
           (if addr > 0 then [Link (t_set_lc, Some (Data, addr), None)]
            else [])
           @ List.map (fun v -> Data (v land 0xff)) bs) sorted)
    else []
  in
  let bridge =
    [ Link (t_def_data_size, Some (Abs, data_size), None)
    ; Link (t_set_lc, Some (Code, 0), None) ]
  in
  let tail =
    [ Link (t_def_code_size, Some (Code, st.lc), None)
    ; Link (t_end_program, Some (Code, 0), None)
    ; Link (t_end_file, None, None) ]
  in
  (header @ data_seg @ bridge @ code_items @ tail, st.lc)

(* build var_info rows from binder rows, keeping only fixed-bin scalars.
   NOTE: storage byte-size comes ONLY from Bind.bytes_of (the binder is the
   single authority on layout) — codegen does not re-derive it.  Returns
   (progname, AUTO_BYTES excluding pool, vars). *)
let rows_of (b : Ast.block) =
  let rows = Bind.bind_rows b in
  let vars =
    List.filter_map
      (fun (nm, rt, off, _auto) ->
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
        | Bind.RTchar (n, false) ->
            Some (nm, { off; size = Bind.bytes_of rt; vk = Vfix n; w = 0 })
        | Bind.RTchar (n, true) ->
            Some (nm, { off; size = Bind.bytes_of rt; vk = Vvar n; w = 0 })
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
  let auto_bytes =
    List.fold_left (fun acc (_, vi) -> max acc (vi.off + vi.size)) 0 vars
  in
  let prog =
    match b.Ast.bname with Some n -> String.uppercase_ascii n.Ast.orig
                         | None -> failwith "codegen: main has no name"
  in
  (prog, auto_bytes, vars)
