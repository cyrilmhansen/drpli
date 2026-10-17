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

type vkind = Vint | Vfix of int | Vvar of int
   (* fixed/varying char capacity. Varying representation PROVEN
      [V101-V104]: length byte at offset 0, data at +1..+n, total
      n+1 bytes (binder authority Bind.bytes_of). *)
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
  { vars : (string * var_info) list   (* lowername -> info *)
  ; base : int                        (* pool base = total pool bytes *)
  ; mutable items : rel_item list
  ; mutable pool : (int * int list) list  (* (data-addr, bytes) literal blocks *)
  ; mutable pool_next : int           (* next free pool offset *)
  ; mutable lc : int                  (* code location counter *)
  ; mutable last_imm : int option     (* HL still holds this constant?
                                         [G114 b=3 folded from a=5] *)
  ; mutable temps : int               (* dynamic-DO bound temp slots
                                         (2 bytes each, AFTER declared
                                         area [Y302: temp@6 = pool2+4;
                                         Y305: temp@5 = pool1+4]) *)
  ; mutable lowered : int }           (* statements actually lowered
                                         (discard-invariant witness) *)
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
let rec prescan_expr (e : Ast.expr) =
  match e.Ast.e with
  | Ast.Ebinary (Ast.Exp, l, r) ->
      let extra =
        match (l.Ast.e, r.Ast.e) with
        | Ast.Enumber bs, Ast.Enumber _ ->
            let k = String.concat "" (String.split_on_char '_' bs) in
            dec_pool_bytes (String.length k)
        | _ -> 0
      in
      prescan_expr l + prescan_expr r + extra
  | Ast.Ebinary (Ast.Sub, { Ast.e = Ast.Enumber a; _ },
                 { Ast.e = Ast.Enumber b; _ }) ->
      (* [N301/N306] const-minus-const DLDOP operands each take a
         dec pool entry *)
      let pint s =
        int_of_string (String.concat "" (String.split_on_char '_' s))
      in
      dec_pool_bytes (dec_digits (pint a))
      + dec_pool_bytes (dec_digits (pint b))
  | Ast.Ebinary (_, l, r) -> prescan_expr l + prescan_expr r
  | Ast.Eprefix (_, x) -> prescan_expr x
  | Ast.Ebuilt (_, es) -> List.fold_left (fun a x -> a + prescan_expr x) 0 es
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

let match_put_list_lit (s : Ast.stmt) =
  match s.Ast.st with
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
let rec prescan_stmt (s : Ast.stmt) =
  match s.Ast.st with
  | Ast.Sassign { rhs; _ } ->
      (match rhs.Ast.e with
       | Ast.Estring v -> String.length v
           (* char-store pool demand [V101-V103/V105]; '' reserves 0
              [V104]; type-mismatched uses RAISE at lowering *)
       | _ -> prescan_expr rhs)
  | Ast.Sput _ ->
      (match match_put_list_lit s with
       | Plit (_, v) -> String.length v
       | Pcat (_, C2 (l, _, _)) -> String.length l
       | Pcat (_, C3 (l, _, r)) -> String.length l + String.length r
       | Pitems (_, its) ->
           List.fold_left
             (fun a it -> match it with
              | PIlit v -> a + String.length v
              | PInum x -> a + prescan_expr x
              | PIvar _ -> a) 0 its
       | _ -> 0)             (* var-puts consume no pool [V101] *)
  | Ast.Sif { then_; els; _ } ->
      prescan_stmt then_
        + (match els with Some e -> prescan_stmt e | None -> 0)
  | Ast.Sdobegin ss -> List.fold_left (fun a x -> a + prescan_stmt x) 0 ss
  | Ast.Sdowhile { body; _ } -> prescan_stmt body
  | Ast.Sdoto { body; _ } -> prescan_stmt body
  | Ast.Sdoforever body -> prescan_stmt body
  | Ast.Sproc b ->
      List.fold_left (fun a x -> a + prescan_stmt x) 0 b.Ast.blk.Ast.bstmts
  | _ -> 0

let prescan_pool (stmts : Ast.stmt list) =
  List.fold_left (fun acc s -> acc + prescan_stmt s) 0 stmts

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

let lower_test_skip st (c : Ast.expr) =
  match c.Ast.e with
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


(* evaluate an integer expression, leaving the 16-bit value in HL *)
let rec lower_hl st (e : Ast.expr) =
  match e.Ast.e with
  | Ast.Enumber s ->
      let v = int_of_string (String.concat "" (String.split_on_char '_' s)) in
      d st op_lxi_h; d st (v land 0xff); d st ((v lsr 8) land 0xff)
  | Ast.Eident n ->
      (match vk_of st n.Ast.orig with
       | Vint -> ()
       | _ -> failwith "codegen: arithmetic on char variable [TBD]");
      let vi = List.assoc (String.lowercase_ascii n.Ast.orig) st.vars in
      if vi.size = 1 then begin
        (* [N306/N303] 1-byte FIXED BIN: LD A,dir (3A+RELOC) then
           sign-extend into HL: MOV L,A; ADD A; SBB A; MOV H,A *)
        st.last_imm <- None;
        d st 0x3a; reloc st Data (addr_of st n.Ast.orig);
        d st op_mov_l_a; d st op_add_a; d st op_sbb_a; d st op_mov_h_a
      end
      else begin
        d st op_lhld; reloc st Data (addr_of st n.Ast.orig);
        st.last_imm <- None   (* runtime value; not a const *)
      end

  | Ast.Ebinary (Ast.Add, l, { Ast.e = Ast.Enumber "1"; _ }) ->
      (* [(a+1) N304] +1 lowers to INX H on the 2-byte path; other
         additions keep the general ladder *)
      lower_hl st l; d st op_inx_h; st.last_imm <- None
  | Ast.Ebinary (Ast.Add, l, r) ->
      (* DR: HL=left ; XCHG ; HL=right ; DAD D  (=> HL = right+left) [P071A] *)
      lower_hl st l; d st op_xchg; lower_hl st r; d st op_dad_d
  | Ast.Ebinary (Ast.Mul, l, r) ->
      (* var/expr OP var: DE=left HL=right, CALL ?IM22N [P071B/P080A].
         [N303] when the RHS is a 1-byte var DR interleaves: raw
         LDA, PUSH H (save left), THEN sign-extend in HL, POP D. *)
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
       | _ -> d st op_push_h; lower_hl st r; d st op_pop_d);
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

let lower_assign st (lhs : Ast.expr) (rhs : Ast.expr) =
  match lhs.Ast.e with
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
  if while_ <> None || (rep <> None && not proven_repeat) then
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
  if proven_repeat then begin
    (* [Z402] body-head is the FIRST BODY instruction (not the
       init); tail increment LHLD/INX/SHLD; JMP back; no test. *)
    let head = st.lc in
    lo st ls body;
    d st op_lhld; reloc st Data iaddr;
    d st op_inx_h;
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
        let temp = st.base + auto_end + 2 * st.temps in
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
                         | Vint -> false | _ -> true)
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
          lower_hl st x;
          d st op_mvi_a; d st (num_width st x);
          call_ext st "?QICOP"; call_ext st "?PNVOP")
    items;
  call_ext st "?QIOOP";
  emit_triple st bslot st.lc

(* statement lowering with label/goto resolution *)
let rec lower_stmt st (ls : lblstate) (s : Ast.stmt) =
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
        d st op_jmp; reloc st Code head
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
  | Ast.Sdcl _ -> ()
  | Ast.Snull _ -> ()
  | _ -> failwith
         (Printf.sprintf "codegen: statement kind not in supported subset \
                          [TBD] (line %d)" s.Ast.spos.Source.line)


let emit_program (progname : string) (auto_bytes : int)
    (rows : (string * var_info) list) (stmts : Ast.stmt list) =
  let pool_total = prescan_pool stmts in
  let st =
    { vars = rows; base = pool_total; items = []; pool = []
    ; pool_next = 0; lc = 0; last_imm = None; lowered = 0; temps = 0 }
  in
  (* lower prologue + body + epilogue into st.items (code segment) *)
  d st op_lxi_b; d st 0x00; d st 0x02;
  d st op_call;
  let start_slot = st.lc in
  d st 0; d st 0;
  link st t_chain_ext (Some (Code, start_slot)) (Some "?START");
  let ls = { labs = []; fwd = [] } in
  List.iter (fun (s : Ast.stmt) -> lower_stmt st ls s) stmts;
  (match ls.fwd with
   | [] -> ()
   | (nm, _) :: _ ->
       failwith (Printf.sprintf
                   "codegen: GOTO to undefined/unresolvable label %s \
                    [TBD: DR pass-2 UNDEF diag]" nm));
  (* DISCARD INVARIANT: every non-decl/non-null statement (at any
     nesting depth) must be accounted for by a lowering step. *)
  let req = List.fold_left (fun a s -> a + count_required s) 0 stmts in
  if req <> st.lowered then
    failwith
      (Printf.sprintf "codegen: DISCARD INVARIANT violated (%d required, \
                       %d lowered)" req st.lowered);
  d st op_call;
  let stop_slot = st.lc in
  d st 0; d st 0;
  link st t_chain_ext (Some (Code, stop_slot)) (Some "?STOPX");
  let code_items = st.items in
  (* now build the ordered full item list *)
  let data_size = pool_total + auto_bytes + 2 * st.temps in
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
