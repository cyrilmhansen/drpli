(* lib/hir_build.ml — read-only adapter: (Ast.block x Bind layout rows) -> Hir.program.

   E2E-54/P0 semantic-reuse rule (spec/lab-evidence/e2e54/PLAN.md §P0.4, operator
   brief §5): this module performs NO independent name resolution, NO independent
   type interpretation and NO declaration discovery of its own. Every identifier
   that reaches HIR resolves through a bind-produced row table
   ([Bind.bind_rows] / [Bind.prog_layout]); every type is a bind [Bind.rt]
   projected into [Hir.ty]. The precedent for consuming bind facts this way is
   codegen.ml [callee_formal_rt_l], which reads the same structures.

   What is deliberately NOT carried across the boundary (falsifier F8): frame
   offsets, DATA-area placement, pool cells, saved-SP cells, section sizes. The
   offset component is dropped in [rows_of_block], the first thing that touches
   a bind row.

   Everything outside the P0 subset (FIXED BINARY scalars, +-*/, assignment,
   IF/ELSE, DO WHILE, internal procedure call/return, STOP) is refused with a
   typed Diagnostic. There is no generic statement/expression constructor in
   [Hir] to misuse: the type is closed over the subset.

   Determinism: scopes/sids/pids are assigned by a pre-order walk (main block
   rows in bind declaration order, then nested procedures in source order,
   parents before children). No Hashtbl iteration, no physical identities. *)

(* Cross-library aliases: this unit lives in the separate [pli80hir] library
   (E2E-54/P0 PLAN §P0.8 F1 remedy — the HIR units must never enter the
   [pli80] library that links pli80c.exe). The historical front-end modules
   are reached through the wrapped [Pli80] module. *)
module Source = Pli80.Source
module Ast = Pli80.Ast
module Bind = Pli80.Bind

open Source

module D = Diagnostic
module H = Hir

(* ---------- context ---------- *)

type ctx = {
  profile : Target.profile;
  plan : Bind.prog_layout;
  mutable next_sid : int;
  mutable next_scope : int;
  mutable next_pid : int; (* pid 0 is reserved for the outermost block *)
  mutable blocks : block_info list; (* all registered blocks, pre-order *)
  (* name -> pid for every procedure (bind-registered and AST-seen alike) *)
  mutable procs_by_name : (string * int) list;
}

and block_info = {
  bi_ast : Ast.block; (** the syntax this block came from *)
  bi_scope : int;
  bi_pid : int;
  bi_parent : int option;
  bi_syms : (string * H.sym) list; (** bind rows, re-keyed; NO new lookup rules *)
  bi_proc : Bind.proc_layout option; (** bind's own record, when this block is a procedure *)
}

exception Hir_error of D.t list

let raise_err ?line code msg = raise (Hir_error [ D.make ?line code msg ])

(* Deterministic header line for a block: [Ast.block] carries no pos of its own
   (hop-2 measurement); the name/spelling fields do. Used for block-level
   diagnostics and fallbacks only — symbol lines come from the dcl rows. *)
let block_line (blk : Ast.block) : int =
  match blk.Ast.blabel with
  | Some n -> n.Ast.pos.line
  | None -> (
      match blk.Ast.bname with
      | Some n -> n.Ast.pos.line
      | None -> (
          match blk.Ast.bendpos with
          | Some p -> p.line
          | None -> 0))

(* ---------- bind row projection (offset dropped immediately) ---------- *)

let rows_of_block (blk : Ast.block) : (string * Bind.rt * bool) list =
  List.map
    (fun (nm, rt, _off, auto) -> (nm, rt, auto))
    (Bind.bind_rows blk)

(* ---------- type mapping: Bind.rt -> Hir.ty, P0 subset ONLY ---------- *)

let ty_of_rt (rt : Bind.rt) : (H.ty, string) result =
  match rt with
  | Bind.RTbin p -> Ok (H.Fixed_bin (p, 0))
  | _ -> Error (Bind.rty_str rt)

(* ---------- diagnostics ---------- *)

let refuse_name (s : Ast.stmt_kind) : string =
  match s with
  | Ast.Sdcl _ -> "DCL"
  | Ast.Sassign _ -> "assignment"
  | Ast.Sgoto _ -> "GOTO"
  | Ast.Sif _ -> "IF"
  | Ast.Sdobegin _ -> "DO; group"
  | Ast.Sdoto _ -> "DO WITH-LOOP (P0 admits exactly ONE loop form, DO WHILE — PLAN §P0.3)"
  | Ast.Sdowhile _ -> "DO WHILE"
  | Ast.Sdoforever _ -> "DO FOREVER"
  | Ast.Sproc _ -> "nested PROC/BEGIN block"
  | Ast.Sput _ -> "PUT"
  | Ast.Sget _ -> "GET"
  | Ast.Sfilestmt _ -> "file statement (OPEN/CLOSE/...)"
  | Ast.Sedit _ -> "EDIT"
  | Ast.Sreadwv _ -> "READ VARYING"
  | Ast.Sreturn _ -> "RETURN"
  | Ast.Sstop _ -> "STOP"
  | Ast.Sexit _ -> "EXIT"
  | Ast.Son _ -> "ON unit"
  | Ast.Srevert _ -> "REVERT"
  | Ast.Ssignal _ -> "SIGNAL"
  | Ast.Selse _ -> "orphan ELSE"
  | Ast.Sdeclare_fail _ -> "DECLARED/NOT>RESERVED fail"
  | Ast.Sprocedure_stmt _ -> "procedure-statement call"
  | Ast.Salloc _ -> "ALLOCATE"
  | Ast.Sfree _ -> "FREE"
  | Ast.Sassign_label _ -> "label assignment"
  | Ast.Sformat _ -> "FORMAT"
  | Ast.Spicturestmt _ -> "PICTURE statement"
  | Ast.Spreproc _ -> "preprocessor directive"
  | Ast.Snull _ -> "null statement"

(* ---------- scope + symbol registration ---------- *)

(* Bind's OWN declaration flattener: the parser keeps dcls as Sdcl statements in
   bstmts (blk.bdecls is [] for corpus-shaped programs — codegen.ml:15729 records
   the same trap), so consulting bdecls alone silently yields "no declaration"
   and every symbol falls back to the block line. Using [Bind.frame_decls] keeps
   the semantic-reuse rule (§P0.4): the name->dcl channel is bind's, not ours. *)
let find_dcl (blk : Ast.block) (key : string) : (Ast.dcl * int) option =
  List.find_opt (fun (d, _l) -> String.equal (Bind.pl_l d.Ast.dname) key)
    (Bind.frame_decls blk)

let register_block acc parent_scope pid (blk : Ast.block)
    (binfo_formals : string list) (bi_proc : Bind.proc_layout option) : block_info =
  let scope_id = acc.next_scope in
  acc.next_scope <- scope_id + 1;
  let rows = rows_of_block blk in
  (* bind keeps one alias row per name; ASSERT the identity precondition. *)
  let rec dup_free = function
    | (a, _, _) :: rest
      when List.exists (fun (b, _, _) -> String.equal a b) rest ->
        raise_err ~line:(block_line blk) D.e_decl
          ("bind produced duplicate rows for " ^ a)
    | _ :: rest -> dup_free rest
    | [] -> ()
  in
  dup_free rows;
  let formals = List.map String.lowercase_ascii binfo_formals in
  let syms =
    List.map
      (fun (key, rt, auto) ->
        let d = find_dcl blk key in
        let sorig =
          match d with
          | Some (dd, _) -> dd.Ast.dname.Ast.orig
          | None -> key (* formal without explicit dcl has no row; guards below catch it *)
        in
        let sline = match d with Some (_, l) -> l | None -> block_line blk in
        match ty_of_rt rt with
        | Ok ty ->
            let storage =
              if List.mem key formals then H.Formal
              else if auto then H.Auto
              else H.Static
            in
            let sid = acc.next_sid in
            acc.next_sid <- sid + 1;
            ( key,
              { H.sid; skey = key; sorig; scope = scope_id; sty = ty; sstorage = storage;
                sline } )
        | Error rt_s ->
            raise_err ~line:sline D.e_type
              ("declared type " ^ rt_s ^ " for " ^ key
              ^ " is outside the P0 HIR subset (FIXED BINARY scalars only)"))
      rows
  in
  let bi =
    { bi_ast = blk; bi_scope = scope_id; bi_pid = pid;
      bi_parent = (if pid = 0 then None else Some parent_scope);
      bi_syms = syms; bi_proc }
  in
  acc.blocks <- bi :: acc.blocks;
  bi

(* Resolve a name through bind rows, walking the lexical chain the block nesting
   creates. Existence and meaning come from bind tables only. *)
let rec resolve acc (bi : block_info) (name : string) : H.sym option =
  match List.assoc_opt name bi.bi_syms with
  | Some s -> Some s
  | None -> (
      match bi.bi_parent with
      | Some p ->
          resolve acc (List.find (fun b -> b.bi_scope = p) acc.blocks) name
      | None -> None)

(* ---------- expressions ---------- *)

let ef_union a b = match (a, b) with H.Pure, H.Pure -> H.Pure | _ -> H.Unknown_ef

let wrap ty ef line k = { H.ex = k; ex_ty = ty; ex_line = line; ex_ef = ef }

let lit_int (text : string) : int option =
  int_of_string_opt (String.concat "" (String.split_on_char '_' text))

let lower_lit acc (e : Ast.expr) (text : string) : H.expr =
  let line = e.Ast.epos.line in
  match acc.profile.Target.default_integer_precision.value with
  | None ->
      raise_err ~line D.e_profile
        "target profile leaves default integer precision UNKNOWN: literals \
         cannot be typed (Target dr-pli80-v1.4 carries the P0 subset rule; \
         generic32 is deliberately all-unknown)"
  | Some p ->
      let v =
        match lit_int text with
        | Some v -> v
        | None ->
            raise_err ~line D.e_lit ("numeric literal " ^ text ^ " is not a plain integer in the P0 domain")
      in
      let bound = if p >= 31 then max_int else (1 lsl p) - 1 in
      if v < -bound || v > bound then
        raise_err ~line D.e_lit
          ("numeric literal " ^ text ^ " is outside the P0 bin(" ^ string_of_int p
          ^ ") literal domain; DR's literal typing beyond the measured window is unmeasured [TBD]");
      wrap (H.Fixed_bin (p, 0)) H.Pure line (H.Const { text })

let rec lower_expr acc (bi : block_info) (e : Ast.expr) : H.expr =
  let line = e.Ast.epos.line in
  match e.Ast.e with
  | Ast.Enumber text -> lower_lit acc e text
  | Ast.Eident n -> (
      let key = Bind.pl_l n in
      match resolve acc bi key with
      | Some s ->
          (* procedures are not values in the P0 subset *)
          if List.mem_assoc key acc.procs_by_name then
            raise_err ~line D.e_call
              ("procedure " ^ key ^ " used as a value: P0 admits calls only")
          else wrap s.H.sty H.Pure line (H.Var { sid = s.sid; addressable = true })
      | None ->
          if List.mem_assoc key acc.procs_by_name then
            raise_err ~line D.e_call
              ("procedure " ^ key ^ " used as a value: P0 admits calls only")
          else
            (* undeclared: bind registered no row anywhere visible — the ONE
               authority says it does not exist; do not invent a meaning. *)
            raise_err ~line D.e_unresolved
              ("identifier " ^ n.Ast.orig
              ^ " resolved by NO bind row in this or any enclosing block"))
  | Ast.Econd inner -> lower_expr acc bi inner (* parentheses carry no semantics here *)
  | Ast.Eprefix (pfx, inner) -> (
      match pfx with
      | Ast.Minus ->
          let x = lower_arith acc bi inner in
          wrap x.H.ex_ty x.H.ex_ef x.H.ex_line (H.Neg { e = x })
      | _ ->
          raise_err ~line D.e_expr
            "prefix form outside the P0 subset (only unary minus of a fixed value)")
  | Ast.Ebinary (op, l, r) -> (
      match op with
      | Ast.Add | Ast.Sub | Ast.Mul -> lower_arith_node acc bi op l r e
      | Ast.EqR rop ->
          (* a comparison reaching the arithmetic path (e.g. inside an argument)
             is a CONDITION value: permitted only under IF/WHILE heads, which
             come through [lower_cond]; here it is out of subset. *)
          raise_err ~line D.e_expr
            ("relational operand (" ^ relop_name rop
            ^ ") used outside a condition position in the P0 subset")
      | _ ->
          raise_err ~line D.e_expr
            "binary operator outside the P0 subset (lowered: + - * arithmetic and \
             = ^= < <= > >= only under IF/DO WHILE heads)")
  | Ast.Esuffix ({ e = Ast.Eident f; _ }, args) ->
      lower_call acc bi line (Bind.pl_l f) args
  | _ ->
      raise_err ~line D.e_expr
        "expression form outside the P0 HIR subset (lowered: integer literals, \
         names, parenthesised expressions, unary minus, + - *, direct procedure \
         calls; string/bit/picture literals, built-ins and qualified references \
         are not)"

and lower_arith acc bi (e : Ast.expr) : H.expr =
  let x = lower_expr acc bi e in
  match x.H.ex_ty with
  | H.Fixed_bin _ -> x
  | H.Condty ->
      raise_err ~line:x.H.ex_line D.e_type
        "a CONDITION value cannot be an arithmetic operand in the P0 subset"
  | t ->
      raise_err ~line:x.H.ex_line D.e_type
        ("arithmetic operand has type " ^ H.pp_ty t ^ "; P0 admits FIXED BINARY only")

and lower_arith_node acc bi op l r e =
  let line = e.Ast.epos.line in
  let x = lower_arith acc bi l in
  let y = lower_arith acc bi r in
  let p1, p2 =
    match (x.H.ex_ty, y.H.ex_ty) with
    | H.Fixed_bin (p1, 0), H.Fixed_bin (p2, 0) -> (p1, p2)
    | _ -> raise_err ~line D.e_type "mixed fixed types in P0 arithmetic (scale/decimal rules unextracted; see backend-boundary.md §1.3)"
  in
  let rp, rule =
    match op with
    | Ast.Add -> (max p1 p2 + 1, "language-rule:max+1")
    | Ast.Sub -> (max p1 p2 + 1, "language-rule:max+1")
    | Ast.Mul -> (p1 + p2, "language-rule:prec-sum")
    | _ -> raise_err ~line D.e_expr "operator outside P0 arithmetic (+, -, *)"
  in
  (* hop-2 design amendment (recorded in RESULTS): the profile ceiling is
     Oracle-backed for DECLARATIONS only (bin(16) refused: E1415..E1432);
     DR's intermediate expression precision is UNMEASURED. REFUSING every
     language-rule result beyond the ceiling would make PLAN §P0.6's own
     fixture arithmetic (`i = i + 1', precision 16) unlowerable, so the
     result is CLAMPED and the clamp is named in the node's typing string —
     a representation choice, not a DR law. *)
  let rp, rule =
    match acc.profile.Target.max_fixed_precision.value with
    | Some m when rp > m ->
        ( m,
          rule ^ "; clamped to profile ceiling " ^ string_of_int m
          ^ " (language-rule result precision " ^ string_of_int rp
          ^ "; DR intermediate typing unmeasured [TBD])" )
    | _ -> (rp, rule)
  in
  wrap (H.Fixed_bin (rp, 0)) (ef_union x.ex_ef y.ex_ef) line
    (H.Bin { op = hir_binop op; left = x; right = y; typing = rule })

and profile_src (f : int Target.field) : string =
  match f.source with
  | Target.Oracle_backed s -> "oracle-backed: " ^ s
  | Target.Language_rule s -> "language-rule: " ^ s
  | Target.Unknown -> "UNKNOWN"

and hir_binop = function
  | Ast.Add -> H.Add
  | Ast.Sub -> H.Sub
  | Ast.Mul -> H.Mul
  | _ -> raise_err D.e_expr "internal: non-arith binop"

and relop_name = function
  | Ast.Eq -> "=" | Ast.Ne -> "^=" | Ast.Lt -> "<" | Ast.Le -> "<="
  | Ast.Gt -> ">" | Ast.Ge -> ">="

(* conditions: P0 admits exactly relational comparisons of fixed values. *)
and lower_cond acc bi (e : Ast.expr) : H.expr =
  let line = e.Ast.epos.line in
  match e.Ast.e with
  | Ast.Ebinary (Ast.EqR rop, l, r) ->
      let x = lower_arith acc bi l in
      let y = lower_arith acc bi r in
      let op =
        match rop with
        | Ast.Eq -> H.Eq | Ast.Ne -> H.Ne | Ast.Lt -> H.Lt | Ast.Le -> H.Le
        | Ast.Gt -> H.Gt | Ast.Ge -> H.Ge
      in
      wrap H.Condty (ef_union x.ex_ef y.ex_ef) line
        (H.Bin { op; left = x; right = y; typing = "language-rule:relational" })
  | Ast.Econd inner -> lower_cond acc bi inner
  | _ ->
      raise_err ~line D.e_expr
        "condition shape outside the P0 subset (only relational comparisons of \
         FIXED BINARY expressions; AND/OR chains, ^, built-in conditions require \
         evaluation-order evidence, see backend-boundary.md §1.6)"

(* calls: the callee identity is bind's procedure registry (pl_procs entries
   collected into acc.procs_by_name); argument COUNT is checked against bind's
   own formal cells (pl_ptrs), never against a re-derived signature. *)
and lower_call acc bi line (key : string) (args : Ast.expr list) : H.expr =
  let pid =
    match List.assoc_opt key acc.procs_by_name with
    | Some pid -> pid
    | None ->
        (* maybe an array/built-in suffix call — all out of P0, name them distinctly *)
        (match resolve acc bi key with
        | Some _ ->
            raise_err ~line D.e_expr
              ("indexed/bounded reference " ^ key ^ " is outside the P0 subset (arrays unlowered)")
        | None ->
            raise_err ~line D.e_unresolved
              ("call target " ^ key ^ " is no bind-registered procedure"))
  in
  let callee = proc_info acc pid in
  let nformal =
    match callee.bi_proc with
    | Some pl -> List.length pl.Bind.pl_ptrs
    | None -> List.length callee.bi_ast.Ast.bparams
  in
  if List.length args <> nformal then
    raise_err ~line D.e_call
      ("call to " ^ key ^ " passes " ^ string_of_int (List.length args) ^ " arguments to "
      ^ string_of_int nformal ^ " bind-registered formals");
  let hargs = List.map (fun a -> lower_arith acc bi a) args in
  let () =
    match callee.bi_proc with
    | Some { Bind.pl_rec = true; _ } | Some { Bind.pl_attr_rec = true; _ } ->
        raise_err ~line D.e_call
          ("recursive procedure " ^ key ^ " is outside the P0 subset")
    | _ -> ()
  in
  let rty =
    match callee.bi_proc with
    | Some { Bind.pl_ret = Some rt; _ } -> (
        match ty_of_rt rt with
        | Ok t -> t
        | Error s -> raise_err ~line D.e_type ("procedure result type " ^ s ^ " outside P0 subset"))
    | _ -> raise_err ~line D.e_call
                ("procedure " ^ key ^ " has no bind RETURNS fact: value use unlowered")
  in
  let ef = List.fold_left (fun accx a -> ef_union accx a.H.ex_ef) H.Pure hargs in
  wrap rty ef line (H.Call_e { pid; args = hargs })

and proc_info acc pid = List.find (fun b -> b.bi_pid = pid) acc.blocks

(* ---------- statements ---------- *)

let rec lower_stmts acc bi (ss : Ast.stmt list) : H.stmt list =
  List.concat_map (lower_stmt acc bi) ss

(* a grouped target (DO; ... END;) becomes a list; anything else a singleton. *)
and flatten_group _acc (_bi : block_info) (s : Ast.stmt) : Ast.stmt list =
  match s.Ast.st with
  | Ast.Sdobegin l -> l
  | Ast.Sproc bs ->
      let b = bs.Ast.blk in
      if b.Ast.bkind = Ast.Bproc then
        raise_err ~line:s.Ast.spos.line D.e_stmt
          "a procedure definition may not appear as a grouped statement body in the P0 subset"
      else if b.Ast.bdecls <> [] then
        raise_err ~line:s.Ast.spos.line D.e_scope
          "declarations inside a nested BEGIN are not separately scoped by bind \
           (they merge into the enclosing block); P0 refuses instead of guessing \
           shadowing semantics — migration task, see backend-boundary.md §2.1"
      else [ s ]
  | _ -> [ s ]

and lower_stmt acc bi (s : Ast.stmt) : H.stmt list =
  let line = s.Ast.spos.line in
  let node k = [ { H.st = k; st_line = line } ] in
  match s.Ast.st with
  | Ast.Snull _ -> []
  | Ast.Sdcl ds ->
      List.concat_map
        (fun (d : Ast.dcl) ->
          if d.dlevel <> None then
            raise_err ~line D.e_decl "level-numbered structure declaration is outside the P0 subset"
          ;
          if d.ddims <> [] then
            raise_err ~line D.e_decl ("array declaration for " ^ d.dname.orig ^ " is outside the P0 subset")
          ;
          if d.dinit <> None then
            raise_err ~line D.e_decl "INITIAL values are outside the P0 subset (storage-init evidence is DR-layout)"
          ;
          if d.dattrs <> [] then
            raise_err ~line D.e_decl "declaration attributes (STATIC/EXTERNAL/BASED/...) are outside the P0 subset"
          ;
          if d.dpre <> None then
            raise_err ~line D.e_decl "preprocessor-spliced declaration is outside the P0 subset"
          ;
          let key = Bind.pl_l d.dname in
          match List.assoc_opt key bi.bi_syms with
          | Some sy -> node (H.Declare sy.sid)
          | None ->
              raise_err ~line D.e_decl
                ("declaration " ^ d.dname.orig ^ " produced no bind row in this block"))
        ds
  | Ast.Sassign { lhs; rhs } -> (
      match lhs.Ast.e with
      | Ast.Eident n -> (
          let key = Bind.pl_l n in
          match resolve acc bi key with
          | Some sy ->
              if List.mem_assoc key acc.procs_by_name then
                raise_err ~line D.e_call ("assignment target " ^ key ^ " names a procedure")
              ;
              let t = wrap sy.H.sty H.Pure lhs.Ast.epos.line (H.Var { sid = sy.sid; addressable = true }) in
              let v = lower_expr acc bi rhs in
              let v =
                if v.H.ex_ty <> sy.sty then
                  match (v.H.ex_ty, sy.sty) with
                  | H.Fixed_bin (p1, s1), H.Fixed_bin (p2, s2) ->
                      wrap sy.sty v.ex_ef v.ex_line
                        (H.Convert
                           { from = v.ex_ty; to_ty = sy.sty; e = v;
                             reason =
                               Printf.sprintf
                                 "language-rule:fixed-assignment %d,%d->%d,%d (rounding/overflow profile-UNKNOWN)"
                                 p1 s1 p2 s2 })
                  | _ ->
                      raise_err ~line D.e_conv
                        ("assignment of " ^ H.pp_ty v.H.ex_ty ^ " to " ^ H.pp_ty sy.sty
                        ^ " is not representable in the P0 subset")
                else v
              in
              node (H.Assign { target = t; value = v })
          | None ->
              raise_err ~line D.e_unresolved
                ("assignment target " ^ n.Ast.orig ^ " resolved by NO bind row"))
      | _ ->
          raise_err ~line D.e_expr
            "only simple variable assignment targets are lowered in the P0 subset")
  | Ast.Sif { cond; then_; els } ->
      let cond' = lower_cond acc bi cond in
      let then' = lower_stmts acc bi (flatten_group acc bi then_) in
      let else' =
        match els with
        | Some e -> lower_stmts acc bi (flatten_group acc bi e)
        | None -> []
      in
      node (H.If { cond = cond'; then_ = then'; else_ = else' })
  | Ast.Sdowhile { cond; body } ->
      let cond' = lower_cond acc bi cond in
      let body' = lower_stmts acc bi (flatten_group acc bi body) in
      node (H.While { cond = cond'; body = body' })
  | Ast.Sstop None -> node H.Stop
  | Ast.Sstop (Some _) ->
      raise_err ~line D.e_stmt "STOP with a code argument is outside the P0 subset"
  | Ast.Sreturn eo -> (
      let proc = proc_info acc bi.bi_pid in
      let ret_rt = match proc.bi_proc with Some { Bind.pl_ret = r; _ } -> r | None -> None in
      match (eo, ret_rt) with
      | None, _ -> node (H.Return None)
      | Some _, None ->
          raise_err ~line D.e_conv
            "RETURN with a value in a procedure bind gave no RETURNS fact"
      | Some e, Some rt -> (
          let want =
            match ty_of_rt rt with
            | Ok t -> t
            | Error s -> raise_err ~line D.e_type ("result type " ^ s ^ " outside P0 subset")
          in
          let v = lower_expr acc bi e in
          let v =
            if v.H.ex_ty <> want then
              match (v.H.ex_ty, want) with
              | H.Fixed_bin _, H.Fixed_bin _ ->
                  wrap want v.ex_ef v.ex_line
                    (H.Convert
                       { from = v.ex_ty; to_ty = want; e = v;
                         reason = "language-rule:fixed-result-assignment (profile rounding UNKNOWN)" })
              | _ ->
                  raise_err ~line D.e_conv
                    ("RETURN value " ^ H.pp_ty v.H.ex_ty ^ " vs result " ^ H.pp_ty want)
              else v
          in
          node (H.Return (Some v))))
  | Ast.Sprocedure_stmt { target; args } -> (
      match target.Ast.e with
      | Ast.Eident n ->
          let key = Bind.pl_l n in
          (match List.assoc_opt key acc.procs_by_name with
          | Some pid ->
              let callee = proc_info acc pid in
              (match callee.bi_proc with
              | Some { Bind.pl_ret = Some _; _ } ->
                  raise_err ~line D.e_call
                    ("statement-level call to function " ^ key ^ " discards a value; unlowered in P0")
              | _ -> ());
              let nformal =
                match callee.bi_proc with
                | Some pl -> List.length pl.Bind.pl_ptrs
                | None -> List.length callee.bi_ast.Ast.bparams
              in
              if List.length args <> nformal then
                raise_err ~line D.e_call
                  ("call to " ^ key ^ " passes " ^ string_of_int (List.length args)
                  ^ " arguments to " ^ string_of_int nformal ^ " bind-registered formals");
              let hargs = List.map (fun a -> lower_arith acc bi a) args in
              (match callee.bi_proc with
              | Some { Bind.pl_rec = true; _ } | Some { Bind.pl_attr_rec = true; _ } ->
                  raise_err ~line D.e_call ("recursive procedure " ^ key ^ " is outside the P0 subset")
              | _ -> ());
              node (H.Call_s { pid; args = hargs })
          | None ->
              raise_err ~line D.e_unresolved
                ("call target " ^ key ^ " is no bind-registered procedure"))
      | _ -> raise_err ~line D.e_expr "only direct procedure calls are lowered in P0")
  | Ast.Sproc bs ->
      let ib = bs.Ast.blk in
      if ib.Ast.bkind = Ast.Bproc then
        [] (* procedure DEFINITION: lowered separately as its own pid entry *)
      else if ib.Ast.bdecls <> [] then
        raise_err ~line D.e_scope
          "declarations inside a nested BEGIN are not separately scoped by bind \
           (they merge into the enclosing block); P0 refuses instead of guessing \
           shadowing semantics — migration task, see backend-boundary.md §2.1"
      else
        (* statement-only BEGIN/DO block: bind merged its scope into this one, so
           its statements execute inline here. Dropping them would be exactly the
           silent lowering F9 forbids. *)
        lower_stmts acc bi ib.Ast.bstmts
  | k ->
      raise_err ~line D.e_stmt
        ("statement " ^ refuse_name k ^ " is outside the P0 HIR subset")

(* ---------- top level ---------- *)

(* Mirror of codegen rows_of's two-authority guard: when the outermost block is
   a procedure-only module (bind's pl_top), every bind_rows name must appear in
   the section layout, else refuse (same rule, same reason; a structural
   consistency check over two bind views, not an independent resolution). *)
let check_top_authority (blk : Ast.block) (plan : Bind.prog_layout) : unit =
  match plan.Bind.pl_top with
  | None -> ()
  | Some tp ->
      let missing =
        List.filter
          (fun (n, _rt, _o, _a) ->
            not
              (List.exists
                 (fun (x, _rt, _o) -> String.equal x n)
                 tp.Bind.pl_rows))
          (Bind.bind_rows blk)
      in
      if missing <> [] then
        raise_err ~line:(block_line blk) D.e_decl
          ("declaration "
             ^ (match List.hd missing with n, _, _, _ -> n)
             ^ " is outside bind's section layout for a procedure-only module \
                [C136 shape]")

(* Pre-order registration walk over the Sproc block tree. bind's proc_layout
   registry is flat and carries NO parent pointer (hop-1 measurement), so the
   nesting SHAPE must be re-read from the AST — a structural traversal that
   allocates ids and mirrors bind's own block discovery (bind_program's
   collect descends through every Sproc child likewise); every NAME/TYPE/
   signature fact below comes from bind (falsifier F6): a Bproc child with no
   pl_procs entry is a hard refusal, never a silently invented block. *)
let rec register_children acc (plan : Bind.prog_layout) (parent : block_info) :
    unit =
  List.iter
    (fun (s : Ast.stmt) ->
      match s.Ast.st with
      | Ast.Sproc bs ->
          let ib = bs.Ast.blk in
          if ib.Ast.bkind = Ast.Bproc then begin
            let key =
              match ib.Ast.bname with
              | Some n -> Bind.pl_l n
              | None ->
                  raise_err ~line:bs.Ast.bpos.line D.e_scope
                    "anonymous procedure block: bind registers no procedure \
                     without a name"
            in
            let pl =
              match
                List.find_opt
                  (fun (p : Bind.proc_layout) -> String.equal p.Bind.pl_name key)
                  plan.Bind.pl_procs
              with
              | Some p -> p
              | None ->
                  raise_err ~line:bs.Ast.bpos.line D.e_scope
                    ("procedure " ^ key
                    ^ " is not in bind's proc_layout registry \
                       (second-authority guard)")
            in
            (match List.assoc_opt key acc.procs_by_name with
            | Some _ ->
                raise_err ~line:bs.Ast.bpos.line D.e_scope
                  ("duplicate internal procedure name " ^ key
                  ^ " (bind-legal? P0 refuses rather than guess)")
            | None -> ());
            let pid = acc.next_pid in
            acc.next_pid <- pid + 1;
            (* names complete BEFORE any body lowers: forward calls to later-
               declared internal procedures are bind-legal. *)
            acc.procs_by_name <- (key, pid) :: acc.procs_by_name;
            let bi =
              register_block acc parent.bi_scope pid ib
                (List.map Bind.pl_l ib.Ast.bparams)
                (Some pl)
            in
            register_children acc plan bi
          end
          else
            (* BEGIN/DO blocks share the parent's scope (bind has no per-BEGIN
               scoping — hop-1); descend for PROCEDURE DISCOVERY only. *)
            register_children acc plan parent
      | _ -> ())
    parent.bi_ast.Ast.bstmts

let build (blk : Ast.block) (profile : Target.profile) :
    (H.program, D.t list) result =
  try
    let plan = Bind.bind_program blk in
    let acc =
      { profile;
        plan;
        next_sid = 0;
        next_scope = 0;
        next_pid = 1; (* pid 0 is the outermost block *)
        blocks = [];
        procs_by_name = []
      }
    in
    check_top_authority blk plan;
    (* 1. outermost block: pid 0, scope 0. A procedure-only module (bind's
          pl_top) is the program entry AND a named call target; a MAIN program
          has no bind proc record for its outer block and no module name. *)
    let main_pl = if Bind.top_is_proc blk then plan.Bind.pl_top else None in
    (match main_pl with
    | Some tp ->
        acc.procs_by_name <- (tp.Bind.pl_name, 0) :: acc.procs_by_name
    | None -> ());
    let main_bi = register_block acc 0 0 blk [] main_pl in
    (* 2. pre-order registration of nested procedures; pids/scopes/sids follow
          source order (bind rows are declaration-ordered — hop-1 measurement). *)
    register_children acc plan main_bi;
    (* 3. HIR construction: pid 0 first, then procs in allocation order. *)
    let blocks =
      List.sort (fun a b -> compare a.bi_pid b.bi_pid) acc.blocks
    in
    let params_of (bi : block_info) : int list =
      List.map
        (fun (n : Ast.name) ->
          match List.assoc_opt (Bind.pl_l n) bi.bi_syms with
          | Some s -> s.H.sid
          | None ->
              (* bind gives an undeclared formal no row (hop-1 proposal, tested
                 on H04): P0 requires the explicit formal dcl. *)
              raise_err ~line:n.Ast.pos.line D.e_decl
                ("explicit formal dcl required in P0: parameter " ^ n.Ast.orig
                ^ " produced no bind row"))
        bi.bi_ast.Ast.bparams
    in
    let ret_of (bi : block_info) : H.ty option =
      match bi.bi_proc with
      | Some { Bind.pl_ret = Some rt; _ } -> (
          match ty_of_rt rt with
          | Ok t -> Some t
          | Error s ->
              raise_err ~line:(block_line bi.bi_ast) D.e_type
                ("procedure result type " ^ s ^ " outside the P0 HIR subset"))
      | _ -> None
    in
    let procs =
      List.map
        (fun bi ->
          { H.pid = bi.bi_pid;
            name = (match bi.bi_ast.Ast.bname with
                   | Some n -> Some n.Ast.orig
                   | None -> None);
            is_main = bi.bi_pid = 0;
            scope = bi.bi_scope;
            params = params_of bi;
            ret = ret_of bi;
            (* body = the block's statements; nested Sproc Bproc definitions
               drop out here and lower as their own pid entries (§lower_stmt). *)
            body = lower_stmts acc bi bi.bi_ast.Ast.bstmts
          })
        blocks
    in
    let syms =
      List.sort (fun a b -> compare a.H.sid b.H.sid)
        (List.concat_map (fun bi -> List.map snd bi.bi_syms) blocks)
    in
    let scopes =
      List.sort (fun a b -> compare a.H.scope_id b.H.scope_id)
        (List.map
           (fun bi ->
             { H.scope_id = bi.bi_scope;
               parent = bi.bi_parent;
               skind =
                 (if bi.bi_pid = 0 then H.Program_scope
                 else H.Proc_scope bi.bi_pid)
             })
           blocks)
    in
    Ok
      { H.profile_name = profile.Target.name;
        scopes;
        syms;
        procs
      }
  with Hir_error ds -> Error ds
