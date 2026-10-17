(* lib/ir.ml — typed IR lowering + $V opcode-stream emitter.

   Model: spec/notes/ir-opcodes.md + CLAIMS C051/C052/C058; validated by
   tools/ir_gate.py against DR $V goldens (expression subsets).

   Streams emit one line per IR node in DR order:
     <OP>  <stack> <flagletter> <k> <p> <s?> <f6> <f7> [ <desc> ]
   Field values marked [TBD] are defaults (00) refined gate-driven. *)

type ty =
  | Tbin of int                       (* FIXED BINARY(p,0) *)
  | Tdec of int * int                 (* FIXED DECIMAL(p,s) *)
  | Tflt                              (* FLOAT BINARY(24,0) *)
  | Tchr of int * bool                (* CHARACTER(n) [VARYING] *)
  | Tbit of int

let pp_ty = function
  | Tbin p -> Printf.sprintf "FIXED BINARY(%d,0)" p
  | Tdec (p, s) -> Printf.sprintf "FIXED DECIMAL(%d,%d)" p s
  | Tflt -> "FLOAT BINARY(24,0)"
  | Tchr (n, true) -> Printf.sprintf "CHAR(%d) VARYING" n
  | Tchr (n, false) -> Printf.sprintf "CHAR(%d)" n
  | Tbit n -> Printf.sprintf "BIT(%d)" n

type env =
  { vars : (string * (int * ty)) list
  ; base : int                        (* pool total: [A(off)] in $V/$C =
       pool size + soffset: constants/formats live BELOW variables in
       the data frame [EX P071C z@0x10 = pool(8)+soff(8); P071D z@1] *)
  ; pool : int ref                    (* next *S byte offset *)
  ; mutable out : string list
  ; mutable assigned : string list    (* vars assigned in EARLIER stmts:
       their RHS reads print f6=28 [P071A a@L4 vs P071B a@L3; targets
       and never-assigned vars print 00; pool constants print 28] *)
  }
  (* NOTE: the 'stack' numeric field on every record = NODE ARITY in
     DR's tree representation: address nodes IID/C2 = 0, loads ILD.. = 1
     (they consume their address node), binary ops = 2, conversion ops
     Q-something = 1, stores TAS = 2. Verified across P071A-P072E. *)

let emit env s = env.out <- env.out @ [s]
let upper s = String.uppercase_ascii s

let ty_prefix = function
  | Tbin _ -> 'I' | Tdec _ -> 'D' | Tflt -> 'F'
  | Tchr (_, true) -> 'V' | Tchr (_, false) -> 'C' | Tbit _ -> 'B'

let addr_op t = Printf.sprintf "%cID" (ty_prefix t)
let load_op t = Printf.sprintf "%cLD" (ty_prefix t)
let store_op t = Printf.sprintf "%cAS" (ty_prefix t)

(* p/s pair rendered for a node of this type (fields f4 f5) *)
let tp_fields = function
  | Tbin p -> (p, 0)
  | Tdec (p, s) -> (p, s)
  | Tflt -> (24, 0)
  | Tchr (n, _) -> (n, 0)
  | Tbit n -> (n, 0)

let lookup (env : env) (name : string) =
  List.assoc_opt (String.lowercase_ascii name) env.vars

(* variable leaf: address node + load node.
   f6=28 appears on reads of previously-ASSIGNED vars [P071A a@L4 vs
   P071B a@L3; rule generalization OPEN — v1 emits 00 everywhere]. *)
let lower_var (env : env) (name : string) =
  match lookup env name with
  | Some (off, t) ->
      let off = off + env.base in
      let f6 =
        if List.mem (String.lowercase_ascii name) env.assigned then 28
        else 0
      in
      emit env (Printf.sprintf "%s 0 N 1 00 00 %02d 00 %s A(%04X)"
                  (addr_op t) f6 (upper name) off);
      let (p, s) = tp_fields t in
      emit env (Printf.sprintf "%s 1 N 0 %02d %02d 00 00" (load_op t) p s);
      t
  | None -> failwith ("ir: undeclared " ^ name)

let bit_width n =
  let rec go w v = if v <= 0 then (if w = 0 then 1 else w) else go (w + 1) (v / 2) in
  go 0 n

(* numeric literal.
   integer: C2 #<value> (decimal, %04d) + ILD minimal precision.
   decimal/float literals: pool record DID/FID * S(k) + LOAD —
   [TBD: DR dec-literal p/s (P071C '1.5' loaded as 15 4?!?) and
   pool stride; float pool = 4B reserved ✓]. *)
let lower_num (env : env) (txt : string) =
  let digits = String.concat "" (String.split_on_char '_' txt) in
  if String.contains digits '.' then begin
    let epos =
      let best = ref max_int in
      String.iteri (fun i c -> if c = 'e' || c = 'E' then best := min !best i)
        digits;
      if !best = max_int then None else Some !best
    in
    let is_float = epos <> None in
    let before_e = match epos with None -> digits | Some i -> String.sub digits 0 i in
    let (ipd, fps) =
      match String.index_opt before_e '.' with
      | Some i -> (String.length (String.sub before_e 0 i),
                   String.length before_e - i - 1)
      | None -> (String.length digits, 0)
    in
    (* DR decimal literals [P071C '1.5' -> DLD 15 4 pool 8B; P060A
       '123'->*S(0006) DLD 05 02?!?]: integer part p15/s=fps-ish; v1
       model: p = 15 when fractional digits exist?? else pool BCD of
       the number. SIZE = ceil((p+1)/2) BCD. [rule partially TBD —
       gate-driven] *)
    let (p, s) = if fps > 0 then (15, 4) else (ipd, 0) in
    let off = !(env.pool) in
    env.pool := off + (if is_float then 4 else (p + 2) / 2 + (if s > 0 then 1 else 0));
    if is_float then begin
      emit env (Printf.sprintf "FID 0 N 1 00 00 28 00 * S(%04X)" off);
      emit env "FLD 1 N 0 24 00 00 00";
      Tflt
    end else begin
      emit env (Printf.sprintf "DID 0 N 1 00 00 28 00 * S(%04X)" off);
      emit env (Printf.sprintf "DLD 1 N 0 %02d %02d 00 00" p s);
      Tdec (p, s)
    end
  end else begin
    let v = int_of_string digits in
    emit env (Printf.sprintf "C2  0 N 0 00 00 00 00 #%04d" v);
    emit env (Printf.sprintf "ILD 1 N 0 %02d 00 00 00" (bit_width v));
    Tbin 15
  end

(* result type algebra (proven subset) *)
let arith_result op lt rt =
  match (lt, rt, op) with
  | Tbin _, Tbin _, _ -> Tbin 15
  | Tdec (p1, s1), Tdec (p2, s2), Ast.Mul -> Tdec (p1 + p2 + 1, s1 + s2)
  | Tdec (p1, s1), Tdec (p2, s2), (Ast.Add | Ast.Sub) ->
      Tdec (max p1 p2 + 1, max s1 s2)
  | Tdec (p1, s1), Tdec (_, s2), Ast.Div -> Tdec (p1 + s2 + 1, p1 + s2)
      (* [HYPOTHESIS from P087H rescale chain; needs gate confirm] *)
  | (Tflt, Tflt, _) -> Tflt
  | _ -> failwith "ir: mixed-type arithmetic [TBD conversions]"

let op_name fam op =
  match (fam, op) with
  | 'I', Ast.Add -> "IAD" | 'I', Ast.Sub -> "ISU" | 'I', Ast.Mul -> "IMU"
  | 'I', Ast.Div -> "IDV" | 'I', Ast.Exp -> "IEX"
  | 'D', Ast.Add -> "DAD" | 'D', Ast.Sub -> "DSU" | 'D', Ast.Mul -> "DMU"
  | 'D', Ast.Div -> "DDV" | 'D', Ast.Exp -> "DEX"
  | 'F', Ast.Add -> "FAD" | 'F', Ast.Sub -> "FSU" | 'F', Ast.Mul -> "FMU"
  | 'F', Ast.Div -> "FDV" | 'F', Ast.Exp -> "FEX"
  | _ -> failwith "ir: op/type unsupported"

(* pure type inference (no emission) *)
let rec infer (env : env) (e : Ast.expr) : ty =
  match e.Ast.e with
  | Ast.Eident n ->
      (match lookup env n.Ast.orig with Some (_, t) -> t | None -> Tbin 15)
  | Ast.Enumber t -> num_ty t
  | Ast.Eprefix (m, x) ->
      let t = infer env x in
      (match m with Ast.Minus | Ast.Plus -> t | _ -> Tbin 15)
  | Ast.Ebinary (op, l, r) -> arith_result op (infer env l) (infer env r)
  | _ -> Tbin 15

and num_ty (t : string) : ty =
  let digits = String.concat "" (String.split_on_char '_' t) in
  if not (String.contains digits '.') then Tbin 15
  else
    let best = ref max_int in
    String.iteri (fun i c -> if c = 'e' || c = 'E' then best := min !best i)
      digits;
    if !best <> max_int then Tflt
    else
      let dot = Option.get (String.index_opt digits '.') in
      let ipd = ref 0 and fps = ref 0 in
      String.iter (fun c -> if c >= '0' && c <= '9' then incr ipd)
        (String.sub digits 0 dot);
      for i = dot + 1 to String.length digits - 1 do
        if digits.[i] >= '0' && digits.[i] <= '9' then incr fps
      done;
      if !fps = 0 then Tbin 15
      else if !ipd + !fps <= 15 then Tdec (!ipd + !fps, !fps)
      else if !ipd <= 15 then Tdec (15, !fps)
      else Tdec (!ipd, 0)

(* decimal literal emitted under an alignment-requiring op (+,-) gets
   PRE-RESCALED at compile time into a pool BCD entry of the target
   (p,s) [EX P071C '1.5' under (p*q)- : DID *S(0000) DLD 15 04, pool
   8B]. '*'/'/' keep the literal's natural type [P072D '10.0' (3,1)]. *)
let emit_pool_dec env (txt : string) (p : int) (s : int) =
  let off = !(env.pool) in
  env.pool := off + (p + 2) / 2;
  emit env (Printf.sprintf "DID 0 N 1 00 00 28 00 * S(%04X)" off);
  emit env (Printf.sprintf "DLD 1 N 0 %02d %02d 00 00" p s);
  Tdec (p, s)

let rec lower ?(root = false) ?(dctx : (int * int) option) (env : env)
    (e : Ast.expr) =
  match e.Ast.e with
  | Ast.Eident n -> lower_var env n.Ast.orig
  | Ast.Enumber t ->
      let digits = String.concat "" (String.split_on_char '_' t) in
      let is_plain_dec =
        String.contains digits '.'
        &&
        let best = ref max_int in
        String.iteri (fun i c -> if c = 'e' || c = 'E' then best := min !best i)
          digits;
        !best = max_int
      in
      (match dctx with
       | Some (p, s) when is_plain_dec -> emit_pool_dec env digits p s
       | _ -> lower_num env t)
  | Ast.Ebinary (op, l, r) ->
      (* operand/result types inferred WITHOUT emission first so that
         alignment-requiring ops can constant-fold dec literals *)
      let lt = infer env l in
      let rt = infer env r in
      let res = arith_result op lt rt in
      let (p, s) = tp_fields res in
      let dctx =
        match op with
        | Ast.Add | Ast.Sub when (match res with Tdec _ -> true | _ -> false) ->
            Some (p, s)
        | _ -> None
      in
      let letter =
        match op with
        | Ast.Add | Ast.Mul -> "B"
        | Ast.Sub | Ast.Div | Ast.Exp -> "N"
        | _ -> "B"
      in
      let _ = lower ?dctx env l in
      let _ = lower ?dctx env r in
      emit env (Printf.sprintf "%s 2 %s 0 %02d %02d 00 00"
                  (op_name (ty_prefix res) op) letter p s);
      res
  | Ast.Eprefix (Ast.Minus, x) ->
      (* -x over literal: DR folds sign into the C2/ISU chain [P071A
         'a+b-1' uses ISU, not negation node] — handled at bin level;
         standalone prefix [TBD] *)
      lower env x
  | _ -> failwith "ir: expression form not yet lowered"

(* statements v1: only plain assignment to a simple variable.
   LIO #<source line> [P071x: #NNNN = source line number]. TARGET addr
   prints f6=00 even if previously assigned; AFTER the statement the
   target enters env.assigned (reads then carry 28). *)
let lower_assign (env : env) (tgt : string) (rhs : Ast.expr) (line : int) =
  emit env (Printf.sprintf "LIO 0 N 1 00 00 00 00 #%04d" line);
  let tt =
    match lookup env tgt with
    | Some (off0, t) ->
        let off = off0 + env.base in
        emit env (Printf.sprintf "%s 0 N 1 00 00 00 00 %s A(%04X)"
                    (addr_op t) (upper tgt) off);
        t
    | None -> failwith ("ir: assign to undeclared " ^ tgt)
  in
  ignore (lower ~root:true env rhs);
  let (p, s) = tp_fields tt in
  (* DEC stores print f6=28 [P071C both stmts; float/int stores 00 —
     rule [HYPOTHESIS], refine on P071F/P072D/P060A] *)
  let f6 = match tt with Tdec _ -> 28 | _ -> 0 in
  emit env (Printf.sprintf "%s 2 X 0 %02d %02d %02d 00" (store_op tt) p s f6);
  let k = String.lowercase_ascii tgt in
  if not (List.mem k env.assigned) then
    env.assigned <- k :: env.assigned

(* entry point: lower the main block's assignment statements *)
let lower_block (env : env) (b : Ast.block) =
  let rec st (s : Ast.stmt) =
    match s.Ast.st with
    | Ast.Sassign { lhs; rhs } ->
        (match lhs.Ast.e with
         | Ast.Eident n ->
             lower_assign env n.Ast.orig rhs s.Ast.spos.Source.line
         | _ -> ())
    | _ -> ()
  in
  List.iter st b.Ast.bstmts
