(* lib/hir_build.ml — read-only consumer: Semantic_env projection -> Hir.program.

   E2E-54/P0 semantic-reuse rule (spec/lab-evidence/e2e54/PLAN.md §P0.4, operator
   brief §5): this module performs NO independent name resolution, NO independent
   type interpretation and NO declaration discovery of its own. Every identifier
   that reaches HIR resolves through a bind-produced row table; every type is a
   bind type projected into [Hir.ty].

   E2E-54/P1-b seam (PLAN §P1-b.3): ALL table construction, lexical lookup, the
   proc registry, the declaration-line channel and the signature reads now live
   behind [Semantic_env] — the ONE typed projection of the binder. This file is
   the consumer: the HIR SUBSET GATE (stype -> Hir.ty, refusal unchanged,
   quoting the env-carried bind rendering VERBATIM), the eager sid-ordered
   projection of env symbols into [Hir.sym] (which preserves the historic
   refusal ORDER within registration), the lowering and typing rules, and the
   diagnostic plumbing. The ONLY remaining Bind reference here is the single
   [Bind.bind_program] authority call (falsifier S5); every other bind read
   crosses through [Semantic_env].

   What is deliberately NOT carried across the boundary (falsifiers F8/S8):
   frame placements, DATA-area placement, pool cells, saved-stack cells,
   section extents. Semantic_env drops them at its projection boundary.

   Everything outside the P0 subset (FIXED BINARY scalars, +-*/, assignment,
   IF/ELSE, DO WHILE, internal procedure call/return, STOP) is refused with a
   typed Diagnostic. There is no generic statement/expression constructor in
   [Hir] to misuse: the type is closed over the subset.

   Determinism: scopes/sids/pids are assigned by the env's pre-order walk (main
   block rows in bind declaration order, then nested procedures in source
   order, parents before children) — EXACTLY the scheme this file used at
   aaf295f0, so every dump byte is preserved (falsifier S2). No Hashtbl
   iteration, no physical identities. *)

(* Cross-library aliases: this unit lives in the separate [pli80_hir] library
   (E2E-54/P0 PLAN §P0.8 F1 remedy — the HIR units must never enter the
   [pli80] library that links pli80c.exe). The historical front-end modules
   are reached through the wrapped [Pli80] module. *)
module Source = Pli80.Source
module Ast = Pli80.Ast
module Bind = Pli80.Bind

open Source

module D = Diagnostic
module H = Hir
module SE = Semantic_env

(* ---------- context ---------- *)

(* P1-b: the mutable registration tables (next_sid/next_scope/next_pid/
   blocks/procs_by_name) are GONE — Semantic_env owns identity assignment.
   [syms] is the eager, sid-ordered Hir.sym projection of the env symbols;
   lowering reads HIR types through it, never re-deriving them. *)
type ctx = {
  profile : Target.profile;
  env : SE.t;
  mutable syms : (int * H.sym) list; (** sid -> projected Hir.sym (all blocks) *)
}

exception Hir_error of D.t list

let raise_err ?line code msg = raise (Hir_error [ D.make ?line code msg ])

(* ---------- type mapping: Semantic_env.stype -> Hir.ty, P0 subset ONLY ---------- *)

(* THE HIR subset gate (§P1-b.3). [pr] is the bind rendering the caller carries
   (symbol [epr] / signature [sret_pr]), so every type-naming message quotes
   bind's own words byte-identically across the seam (falsifier S10); the gate
   never fabricates a rendering from the projection. *)
let ty_of_rt (s : SE.stype) ~(pr : string) : (H.ty, string) result =
  match s with
  | SE.SFixed_bin p -> Ok (H.Fixed_bin (p, 0))
  | _ -> Error pr

(* Eager sid-ordered projection (blocks pid-ascending, rows in bind order —
   the same sequence register_block consumed at aaf295f0, so the FIRST
   out-of-subset refusal is the same symbol on the same line with the same
   message; the P0 per-block interleaving of registration guards with this
   gate is the §P1-b.3 predicted drift, recorded, never silent). *)
let project_syms ctx =
  List.iter
    (fun (be : SE.block_env) ->
      List.iter
        (fun (_key, (s : SE.symbol)) ->
          match ty_of_rt s.SE.ety ~pr:s.epr with
          | Ok ty ->
              let storage =
                match s.SE.estorage with
                | SE.S_formal -> H.Formal
                | SE.S_auto -> H.Auto
                | SE.S_static -> H.Static
              in
              ctx.syms <-
                ( s.SE.esid,
                  { H.sid = s.SE.esid; skey = s.ekey; sorig = s.eorig;
                    scope = s.escope; sty = ty; sstorage = storage;
                    sline = s.eline } )
                :: ctx.syms
          | Error rt_s ->
              raise_err ~line:s.SE.eline D.e_type
                ("declared type " ^ rt_s ^ " for " ^ s.SE.ekey
                ^ " is outside the P0 HIR subset (FIXED BINARY scalars only)"))
        be.SE.esyms)
    (SE.blocks ctx.env)

(* Resolve a name through the env (bind rows over the AST-nesting chain). *)
let resolve ctx (bi : SE.block_env) (name : string) : H.sym option =
  match SE.resolve ctx.env bi.SE.escope name with
  | Some s -> Some (List.assoc s.SE.esid ctx.syms)
  | None -> None

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
  | Ast.Sformat _ -> "FORMAT statement"
  | Ast.Spicturestmt _ -> "PICTURE statement"
  | Ast.Spreproc _ -> "preprocessor directive"
  | Ast.Snull _ -> "null statement"

(* ---------- expressions ---------- *)

let ef_union a b = match (a, b) with H.Pure, H.Pure -> H.Pure | _ -> H.Unknown_ef

let wrap ty ef line k = { H.ex = k; ex_ty = ty; ex_line = line; ex_ef = ef }

let lit_int (text : string) : int option =
  int_of_string_opt (String.concat "" (String.split_on_char '_' text))

let lower_lit ctx (e : Ast.expr) (text : string) : H.expr =
  let line = e.Ast.epos.line in
  match ctx.profile.Target.default_integer_precision.value with
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

let rec lower_expr ctx (bi : SE.block_env) (e : Ast.expr) : H.expr =
  let line = e.Ast.epos.line in
  match e.Ast.e with
  | Ast.Enumber text -> lower_lit ctx e text
  | Ast.Eident n -> (
      let key = SE.key_of n in
      match resolve ctx bi key with
      | Some s ->
          (* procedures are not values in the P0 subset *)
          if SE.procedure ctx.env key <> None then
            raise_err ~line D.e_call
              ("procedure " ^ key ^ " used as a value: P0 admits calls only")
          else wrap s.H.sty H.Pure line (H.Var { sid = s.sid; addressable = true })
      | None ->
          if SE.procedure ctx.env key <> None then
            raise_err ~line D.e_call
              ("procedure " ^ key ^ " used as a value: P0 admits calls only")
          else
            (* undeclared: bind registered no row anywhere visible — the ONE
               authority says it does not exist; do not invent a meaning. *)
            raise_err ~line D.e_unresolved
              ("identifier " ^ n.Ast.orig
              ^ " resolved by NO bind row in this or any enclosing block"))
  | Ast.Econd inner -> lower_expr ctx bi inner (* parentheses carry no semantics here *)
  | Ast.Eprefix (pfx, inner) -> (
      match pfx with
      | Ast.Minus ->
          let x = lower_arith ctx bi inner in
          wrap x.H.ex_ty x.H.ex_ef x.H.ex_line (H.Neg { e = x })
      | _ ->
          raise_err ~line D.e_expr
            "prefix form outside the P0 subset (only unary minus of a fixed value)")
  | Ast.Ebinary (op, l, r) -> (
      match op with
      | Ast.Add | Ast.Sub | Ast.Mul -> lower_arith_node ctx bi op l r e
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
      lower_call ctx bi line (SE.key_of f) args
  | _ ->
      raise_err ~line D.e_expr
        "expression form outside the P0 HIR subset (lowered: integer literals, \
         names, parenthesised expressions, unary minus, + - *, direct procedure \
         calls; string/bit/picture literals, built-ins and qualified references \
         are not)"

and lower_arith ctx bi (e : Ast.expr) : H.expr =
  let x = lower_expr ctx bi e in
  match x.H.ex_ty with
  | H.Fixed_bin _ -> x
  | H.Condty ->
      raise_err ~line:x.H.ex_line D.e_type
        "a CONDITION value cannot be an arithmetic operand in the P0 subset"
  | t ->
      raise_err ~line:x.H.ex_line D.e_type
        ("arithmetic operand has type " ^ H.pp_ty t ^ "; P0 admits FIXED BINARY only")

and lower_arith_node ctx bi op l r e =
  let line = e.Ast.epos.line in
  let x = lower_arith ctx bi l in
  let y = lower_arith ctx bi r in
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
    match ctx.profile.Target.max_fixed_precision.value with
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
and lower_cond ctx bi (e : Ast.expr) : H.expr =
  let line = e.Ast.epos.line in
  match e.Ast.e with
  | Ast.Ebinary (Ast.EqR rop, l, r) ->
      let x = lower_arith ctx bi l in
      let y = lower_arith ctx bi r in
      let op =
        match rop with
        | Ast.Eq -> H.Eq | Ast.Ne -> H.Ne | Ast.Lt -> H.Lt | Ast.Le -> H.Le
        | Ast.Gt -> H.Gt | Ast.Ge -> H.Ge
      in
      wrap H.Condty (ef_union x.ex_ef y.ex_ef) line
        (H.Bin { op; left = x; right = y; typing = "language-rule:relational" })
  | Ast.Econd inner -> lower_cond ctx bi inner
  | _ ->
      raise_err ~line D.e_expr
        "condition shape outside the P0 subset (only relational comparisons of \
         FIXED BINARY expressions; AND/OR chains, ^, built-in conditions require \
         evaluation-order evidence, see backend-boundary.md §1.6)"

(* calls: the callee identity is the env's procedure registry; argument COUNT
   is bind's own formal-cell count (sptr_count), never a re-derived signature. *)
and lower_call ctx bi line (key : string) (args : Ast.expr list) : H.expr =
  let pid =
    match SE.procedure ctx.env key with
    | Some pid -> pid
    | None ->
        (* maybe an array/built-in suffix call — all out of P0, name them distinctly *)
        (match resolve ctx bi key with
        | Some _ ->
            raise_err ~line D.e_expr
              ("indexed/bounded reference " ^ key ^ " is outside the P0 subset (arrays unlowered)")
        | None ->
            raise_err ~line D.e_unresolved
              ("call target " ^ key ^ " is no bind-registered procedure"))
  in
  let callee = SE.block_of_pid ctx.env pid in
  let nformal =
    match callee.SE.esig with
    | Some s -> s.SE.sptr_count
    | None -> List.length callee.SE.east.Ast.bparams
  in
  if List.length args <> nformal then
    raise_err ~line D.e_call
      ("call to " ^ key ^ " passes " ^ string_of_int (List.length args) ^ " arguments to "
      ^ string_of_int nformal ^ " bind-registered formals");
  let hargs = List.map (fun a -> lower_arith ctx bi a) args in
  let () =
    match callee.SE.esig with
    | Some { SE.srec = true; _ } | Some { SE.sattr_rec = true; _ } ->
        raise_err ~line D.e_call
          ("recursive procedure " ^ key ^ " is outside the P0 subset")
    | _ -> ()
  in
  let rty =
    match callee.SE.esig with
    | Some { SE.sret = Some st; sret_pr = Some pr; _ } -> (
        match ty_of_rt st ~pr with
        | Ok t -> t
        | Error s -> raise_err ~line D.e_type ("procedure result type " ^ s ^ " outside P0 subset"))
    | _ -> raise_err ~line D.e_call
                ("procedure " ^ key ^ " has no bind RETURNS fact: value use unlowered")
  in
  let ef = List.fold_left (fun accx a -> ef_union accx a.H.ex_ef) H.Pure hargs in
  wrap rty ef line (H.Call_e { pid; args = hargs })

(* ---------- statements ---------- *)

let rec lower_stmts ctx bi (ss : Ast.stmt list) : H.stmt list =
  List.concat_map (lower_stmt ctx bi) ss

(* a grouped target (DO; ... END;) becomes a list; anything else a singleton. *)
and flatten_group _ctx (_bi : SE.block_env) (s : Ast.stmt) : Ast.stmt list =
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

and lower_stmt ctx bi (s : Ast.stmt) : H.stmt list =
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
          let key = SE.key_of d.dname in
          match List.assoc_opt key bi.SE.esyms with
          | Some sy -> node (H.Declare sy.SE.esid)
          | None ->
              raise_err ~line D.e_decl
                ("declaration " ^ d.dname.orig ^ " produced no bind row in this block"))
        ds
  | Ast.Sassign { lhs; rhs } -> (
      match lhs.Ast.e with
      | Ast.Eident n -> (
          let key = SE.key_of n in
          match resolve ctx bi key with
          | Some sy ->
              if SE.procedure ctx.env key <> None then
                raise_err ~line D.e_call ("assignment target " ^ key ^ " names a procedure")
              ;
              let t = wrap sy.H.sty H.Pure lhs.Ast.epos.line (H.Var { sid = sy.sid; addressable = true }) in
              let v = lower_expr ctx bi rhs in
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
      let cond' = lower_cond ctx bi cond in
      let then' = lower_stmts ctx bi (flatten_group ctx bi then_) in
      let else' =
        match els with
        | Some e -> lower_stmts ctx bi (flatten_group ctx bi e)
        | None -> []
      in
      node (H.If { cond = cond'; then_ = then'; else_ = else' })
  | Ast.Sdowhile { cond; body } ->
      let cond' = lower_cond ctx bi cond in
      let body' = lower_stmts ctx bi (flatten_group ctx bi body) in
      node (H.While { cond = cond'; body = body' })
  | Ast.Sstop None -> node H.Stop
  | Ast.Sstop (Some _) ->
      raise_err ~line D.e_stmt "STOP with a code argument is outside the P0 subset"
  | Ast.Sreturn eo -> (
      (* bind's RETURNS fact for THIS block, as a typed signature (§P1-b.3):
         sret/sret_pr are mapped together by the env — the Some/None split is
         an env invariant, so one arm covers both. *)
      let ret_spec =
        match SE.signature ctx.env bi.SE.epid with
        | Some { SE.sret = Some st; sret_pr = Some pr; _ } -> Some (st, pr)
        | _ -> None
      in
      match (eo, ret_spec) with
      | None, _ -> node (H.Return None)
      | Some _, None ->
          raise_err ~line D.e_conv
            "RETURN with a value in a procedure bind gave no RETURNS fact"
      | Some e, Some (st, pr) -> (
          let want =
            match ty_of_rt st ~pr with
            | Ok t -> t
            | Error s -> raise_err ~line D.e_type ("result type " ^ s ^ " outside P0 subset")
          in
          let v = lower_expr ctx bi e in
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
          let key = SE.key_of n in
          (match SE.procedure ctx.env key with
          | Some pid ->
              let callee = SE.block_of_pid ctx.env pid in
              (match callee.SE.esig with
              | Some { SE.sret = Some _; _ } ->
                  raise_err ~line D.e_call
                    ("statement-level call to function " ^ key ^ " discards a value; unlowered in P0")
              | _ -> ());
              let nformal =
                match callee.SE.esig with
                | Some s -> s.SE.sptr_count
                | None -> List.length callee.SE.east.Ast.bparams
              in
              if List.length args <> nformal then
                raise_err ~line D.e_call
                  ("call to " ^ key ^ " passes " ^ string_of_int (List.length args)
                  ^ " arguments to " ^ string_of_int nformal ^ " bind-registered formals");
              let hargs = List.map (fun a -> lower_arith ctx bi a) args in
              (match callee.SE.esig with
              | Some { SE.srec = true; _ } | Some { SE.sattr_rec = true; _ } ->
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
        lower_stmts ctx bi ib.Ast.bstmts
  | k ->
      raise_err ~line D.e_stmt
        ("statement " ^ refuse_name k ^ " is outside the P0 HIR subset")

(* ---------- top level ---------- *)

let build (blk : Ast.block) (profile : Target.profile) :
    (H.program, D.t list) result =
  try
    (* THE one semantic-authority call in this file (§P1-b.3, falsifier S5):
       everything the rest of the path reads crosses via Semantic_env. *)
    let plan = Bind.bind_program blk in
    match SE.create blk plan with
    | Error ds -> Error ds (* env registration guards, verbatim diagnostics *)
    | Ok env ->
        let ctx = { profile; env; syms = [] } in
        project_syms ctx;
        (* HIR construction: pid 0 first, then procs in allocation order. *)
        let blocks = SE.blocks env in (* already pid-ascending = pre-order *)
        let params_of (bi : SE.block_env) : int list =
          List.map
            (fun (n : Ast.name) ->
              match List.assoc_opt (SE.key_of n) bi.SE.esyms with
              | Some s -> s.SE.esid
              | None ->
                  (* bind gives an undeclared formal no row (hop-1 proposal, tested
                     on H04): P0 requires the explicit formal dcl. *)
                  raise_err ~line:n.Ast.pos.line D.e_decl
                    ("explicit formal dcl required in P0: parameter " ^ n.Ast.orig
                    ^ " produced no bind row"))
            bi.SE.east.Ast.bparams
        in
        let ret_of (bi : SE.block_env) : H.ty option =
          match bi.SE.esig with
          | Some { SE.sret = Some st; sret_pr = Some pr; _ } -> (
              match ty_of_rt st ~pr with
              | Ok t -> Some t
              | Error s ->
                  raise_err ~line:(SE.block_line bi.SE.east) D.e_type
                    ("procedure result type " ^ s ^ " outside the P0 HIR subset"))
          | _ -> None
        in
        let procs =
          List.map
            (fun bi ->
              { H.pid = bi.SE.epid;
                name = bi.SE.ename;
                is_main = bi.SE.epid = 0;
                scope = bi.SE.escope;
                params = params_of bi;
                ret = ret_of bi;
                (* body = the block's statements; nested Sproc Bproc definitions
                   drop out here and lower as their own pid entries (§lower_stmt). *)
                body = lower_stmts ctx bi bi.SE.east.Ast.bstmts
              })
            blocks
        in
        let syms =
          List.sort (fun a b -> compare a.H.sid b.H.sid)
            (List.map snd ctx.syms)
        in
        let scopes =
          List.sort (fun a b -> compare a.H.scope_id b.H.scope_id)
            (List.map
               (fun bi ->
                 { H.scope_id = bi.SE.escope;
                   parent = bi.SE.eparent;
                   skind =
                     (if bi.SE.epid = 0 then H.Program_scope
                     else H.Proc_scope bi.SE.epid)
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
