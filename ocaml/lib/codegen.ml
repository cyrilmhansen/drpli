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
type var_info = { off : int; size : int; vk : vkind }

type st =
  { vars : (string * var_info) list   (* lowername -> info *)
  ; base : int                        (* pool base = total pool bytes *)
  ; mutable items : rel_item list
  ; mutable pool : (int * int list) list  (* (data-addr, bytes) literal blocks *)
  ; mutable pool_next : int           (* next free pool offset *)
  ; mutable lc : int                  (* code location counter *)
  ; mutable last_imm : int option     (* HL still holds this constant?
                                         [G114 b=3 folded from a=5] *)
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
  | Ast.Ebinary (_, l, r) -> prescan_expr l + prescan_expr r
  | Ast.Eprefix (_, x) -> prescan_expr x
  | Ast.Ebuilt (_, es) -> List.fold_left (fun a x -> a + prescan_expr x) 0 es
  | _ -> 0

(* accepted shapes: literal [G107/G108/G113] or a SINGLE char/varying
   variable [V101/V106]; optional SKIP(const). Pnone -> [TBD]. *)
type put_shape = Pnone | Plit of string option * string
               | Pvar of string option * Ast.expr
let match_put_list_lit (s : Ast.stmt) =
  match s.Ast.st with
  | Ast.Sput { stream = None; on_opts = []; kind = Ast.List_; items } ->
      (match items with
       | [ Ast.Pi_data { Ast.e = Ast.Estring v; _ } ] -> Plit (None, v)
       | [ Ast.Pi_ctl ("SKIP", Some { Ast.e = Ast.Enumber c; _ });
           Ast.Pi_data { Ast.e = Ast.Estring v; _ } ] -> Plit (Some c, v)
       | [ Ast.Pi_data ({ Ast.e = Ast.Eident _; _ } as x) ] ->
           Pvar (None, x)
       | [ Ast.Pi_ctl ("SKIP", Some { Ast.e = Ast.Enumber c; _ });
           Ast.Pi_data ({ Ast.e = Ast.Eident _; _ } as x) ] ->
           Pvar (Some c, x)
       | _ -> Pnone)
  | _ -> Pnone

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
  | _ -> failwith "codegen: condition form not in E2E-3b subset [TBD]"


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
      d st op_lhld; reloc st Data (addr_of st n.Ast.orig)
  | Ast.Ebinary (Ast.Add, l, r) ->
      (* DR: HL=left ; XCHG ; HL=right ; DAD D  (=> HL = right+left) [P071A] *)
      lower_hl st l; d st op_xchg; lower_hl st r; d st op_dad_d
  | Ast.Ebinary (Ast.Mul, l, r) ->
      (* var/expr OP var: DE=left HL=right, CALL ?IM22N [P071B/P080A] *)
      lower_hl st l; d st op_push_h; lower_hl st r; d st op_pop_d;
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
  | Ast.Ebinary (Ast.Sub, x, Ast.{ e = Ast.Enumber c; _ }) ->
      lower_hl st x; const_sub st (int_of_string c)
  | Ast.Ebuilt ("MOD", [l; r]) ->
      (* mod(a,b) -> DE=a, HL=b, CALL ?IMDOP [P071B L4] *)
      lower_hl st l; d st op_push_h; lower_hl st r; d st op_pop_d;
      call_ext st "?IMDOP"
  | Ast.Eprefix (Ast.Minus, _) -> failwith "codegen: negation [TBD]"
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

let lower_assign st (lhs : Ast.expr) (rhs : Ast.expr) =
  match lhs.Ast.e with
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
            | Some p when p - k >= 1 && p - k <= 4 ->
                st.last_imm <- Some k;
                const_sub st (p - k)
            (* [G114B] small negative delta: INX H repeats *)
            | Some p when k - p >= 1 && k - p <= 4 ->
                st.last_imm <- Some k;
                for _ = 1 to k - p do d st op_inx_h done
            | _ ->
                st.last_imm <- Some k;
                d st op_lxi_h; d st (k land 0xff); d st ((k lsr 8) land 0xff))
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

(* PUT LIST (c);) c = varying [V101: ?SLVTS] / fixed [V106: MVI A,cap
   + ?SLCTS]; identical ?SYSPR preamble + skip + continuation triple. *)
let lower_put_var st (skipn : string option) (x : Ast.expr) =
  let nm = match x.Ast.e with
           | Ast.Eident n -> n.Ast.orig
           | _ -> assert false
  in
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
  (match vk_of st nm with
   | Vvar _cap ->
       d st op_lxi_h; reloc st Data (addr_of st nm);
       call_ext st "?SLVTS"
   | Vfix cap ->
       if cap > 255 then failwith "codegen: char cap > 255 [TBD]";
       d st op_lxi_h; reloc st Data (addr_of st nm);
       d st op_mvi_a; d st cap; call_ext st "?SLCTS"
   | Vint ->
       failwith "codegen: PUT LIST of numeric variable unproven [TBD]");
  call_ext st "?PNCOP"; call_ext st "?QIOOP";
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
       | Pvar (skipn, x) -> lower_put_var st skipn x
       | Pnone -> failwith
             (Printf.sprintf
                "codegen: PUT form not in E2E-3a subset [TBD] \
                 (line %d)" s.Ast.spos.Source.line))
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
    ; pool_next = 0; lc = 0; last_imm = None; lowered = 0 }
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
  let data_size = pool_total + auto_bytes in
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
        | Bind.RTbin _ ->
            Some (nm, { off; size = Bind.bytes_of rt; vk = Vint })
        | Bind.RTchar (n, false) ->
            Some (nm, { off; size = Bind.bytes_of rt; vk = Vfix n })
        | Bind.RTchar (n, true) ->
            Some (nm, { off; size = Bind.bytes_of rt; vk = Vvar n })
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
