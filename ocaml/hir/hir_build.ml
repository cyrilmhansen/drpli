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

(* P1-a1 §P1-a1.5: the ARRAY ELEMENT gate. The admitted band is FIXED BINARY 7..15
   — the MEASURED bind-recordable window (facts A-7/A-10/A-11/A-12: bind itself
   refuses 1-byte elements with [C159], bit(8) sizes to 1, char(1) refuses; the
   manual prose never decides this — HIR keys on the projected runtime type).
   Out-of-band elements refuse on the EXISTING HIR-E02 channel with the
   pre-registered array wording; the scalar gate above stays byte-identical. *)
let ty_of_array_elem (s : SE.stype) : (H.ty, unit) result =
  match s with
  | SE.SFixed_bin p when 7 <= p && p <= 15 -> Ok (H.Fixed_bin (p, 0))
  | _ -> Error ()

(* Eager sid-ordered projection (blocks pid-ascending, rows in bind order —
   the same sequence register_block consumed at aaf295f0, so the FIRST
   out-of-subset refusal is the same symbol on the same line with the same
   message; the P0 per-block interleaving of registration guards with this
   gate is the §P1-b.3 predicted drift, recorded, never silent). *)
let project_syms ctx =
  (* ONE emitter for both channels, so the sid order never moves (§P1-a1.5). *)
  let add (s : SE.symbol) (ty : H.ty) =
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
  in
  List.iter
    (fun (be : SE.block_env) ->
      List.iter
        (fun (_key, (s : SE.symbol)) ->
          match s.SE.e_array with
          | None ->
              (* scalar gate and message BYTE-IDENTICAL (T10 — the H06 pin) *)
              (match ty_of_rt s.SE.ety ~pr:s.epr with
               | Ok ty -> add s ty
               | Error rt_s ->
                   raise_err ~line:s.SE.eline D.e_type
                     ("declared type " ^ rt_s ^ " for " ^ s.SE.ekey
                     ^ " is outside the P0 HIR subset (FIXED BINARY scalars only)"))
          | Some a ->
              (* array row: gate the ELEMENT type (the row's ety is the element
                 type too — fact A-1); the declared bounds ride the Hir type. *)
              (match ty_of_array_elem a.SE.a_elem with
               | Ok elem -> add s (H.Array1 { elem; lo = a.a_lo; hi = a.a_hi })
               | Error () ->
                   raise_err ~line:s.SE.eline D.e_type
                     ("array element type " ^ s.epr ^ " for " ^ s.SE.ekey
                     ^ " is outside the P1-a1 array subset (1-D FIXED BINARY(7..15) "
                     ^ "elements only)") ))
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

(* E2E-54/P1-m1 §P1-m1.3: BY-NAME renderings for the HIR-E21 item-class and
   GET-target-shape arms (falsifier T10: every message NAMES its construct). *)
let put_item_class_name (it : Ast.put_item) : string =
  match it with
  | Ast.Pi_fmt _ -> "format item"
  | Ast.Pi_rep _ -> "repetition"
  | Ast.Pi_repgrp _ -> "counted group"
  | Ast.Pi_data _ -> "data item"
  | Ast.Pi_ctl (k, _) -> "control item " ^ k
  | Ast.Pi_pic _ -> "picture literal"
  | Ast.Pi_remote _ -> "remote label"
  | Ast.Pi_group _ -> "group"
  | Ast.Pi_fmtlist _ -> "format list"

let get_target_shape (e : Ast.expr) : string =
  match e.Ast.e with
  | Ast.Esuffix _ -> "an array element or call designation"
  | Ast.Estring _ -> "a string literal"
  | Ast.Enumber _ -> "a numeric literal"
  | Ast.Ebinary _ -> "a binary expression"
  | Ast.Eprefix _ -> "a prefixed expression"
  | Ast.Econd _ -> "a parenthesised expression"
  | _ -> "a non-name expression"

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
          else if
            match s.H.sty with H.Array1 _ -> true | _ -> false
          then
            (* §P1-a1.5: an ARRAY name is not a value either — no whole-array
               load node exists in the HIR; the use refuses loudly (A-16: bind
               recorded nothing about this use, the HIR decides). *)
            raise_err ~line D.e_whole_array
              ("whole-array use of " ^ n.Ast.orig
              ^ " is outside the P1-a1 subset (element references only)")
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
      (* §P1-a1.5(c): a suffix on a plain name is a CALL or an ELEMENT READ, decided
         by the env — procedure ⇒ existing lower_call UNCHANGED; resolved
         non-procedure ⇒ lower_array_ref (array ⇒ Elem_read, scalar ⇒ E12, wrong
         count ⇒ E14); unresolved ⇒ existing lower_call (keeps its E06 wording). *)
      let key = SE.key_of f in
      (match (SE.procedure ctx.env key, resolve ctx bi key) with
       | Some _, _ -> lower_call ctx bi line key args
       | None, Some s -> lower_array_ref ctx bi line f.Ast.orig s args
       | None, None -> lower_call ctx bi line key args)
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
        (* DEFENSIVE GUARD (P1-a1 §P1-a1.5(e)): since the Esuffix dispatch above routes
           every resolved non-procedure name to lower_array_ref, a name that resolves
           but is not a procedure can no longer reach this function — the old
           "arrays unlowered" text became FALSE with P1-a1 and is replaced. UNEXERCISED
           by any probe/fixture (recorded, like the dup_free/E14 witnesses). *)
        (match resolve ctx bi key with
        | Some _ ->
            raise_err ~line D.e_expr
              ("internal: non-procedure name " ^ key
              ^ " reached call lowering (defensive guard; unreachable in P1-a1)")
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
  (* P1-a2 §P1-a2.5: arguments lower through bind's OWN passing evidence; the refusal
     ORDER of this function stays frozen (callee -> arity -> args -> recursion ->
     RETURNS) so every existing diagnostic byte is preserved (T10). *)
  let hargs =
    lower_args ctx bi ~caller_scope:bi.SE.escope ~callee_key:key ~callee_pid:pid line args
  in
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
  let ef = List.fold_left (fun accx a -> ef_union accx a.H.ac_ef) H.Pure hargs in
  wrap rty ef line (H.Call_e { pid; args = hargs })

(* §P1-a1.5(d): a subscript EXPRESSION. A plain integer literal is range-checked
   against the declared bounds — a compile-time HIR subset rule, NOT a DR law: bind
   performs NO out-of-range check (fact A-9) and DR's runtime behaviour is unmeasured.
   Everything else lowers through the existing arithmetic gate (variable subscripts
   are FIXED BINARY by the P0 arithmetic rules). *)
and lower_index ctx bi (line : int) (orig : string) (lo : int) (hi : int)
      (ix : Ast.expr) : H.expr =
  (match ix.Ast.e with
   | Ast.Enumber text ->
       (match lit_int text with
        | Some v when v < lo || v > hi ->
            raise_err ~line D.e_index
              ("constant subscript " ^ string_of_int v ^ " for array " ^ orig
              ^ " is outside the declared bounds [" ^ string_of_int lo ^ ":"
              ^ string_of_int hi
              ^ "] (compile-time HIR subset rule; DR out-of-range behaviour "
              ^ "unmeasured [TBD])")
        | _ -> ())
   | _ -> ());
  lower_arith ctx bi ix

(* §P1-a1.5(d): the VALUE-position element read. One subscript on an Array1 ⇒
   Elem_read; any other count ⇒ E14; a resolved NON-array name ⇒ E12 (A-15: bind
   is blind to subscripts, the HIR decides). The element type rides the node. *)
and lower_array_ref ctx bi (line : int) (orig : string) (sy : H.sym)
      (args : Ast.expr list) : H.expr =
  match sy.H.sty with
  | H.Array1 { elem; lo; hi } ->
      (match args with
       | [ ix ] ->
           let ixe = lower_index ctx bi line orig lo hi ix in
           wrap elem ixe.H.ex_ef line (H.Elem_read { base = sy.sid; subs = [ ixe ] })
       | l ->
           raise_err ~line D.e_dims
             ("subscript form for " ^ orig
             ^ " is outside the 1-D P1-a1 subset ("
             ^ string_of_int (List.length l) ^ " subscript(s))"))
  | _ ->
      raise_err ~line D.e_index
        ("subscript on " ^ orig
        ^ " is not a 1-D array reference in the P1-a1 subset (bind recorded "
        ^ "no array for this name)")

(* ---------- P1-a2 actual arguments (PLAN §P1-a2.4/.5) ---------- *)

(* The callee's declared type at formal position [pos] — the §P1-a2.5 TYPE DISCIPLINE,
   judged against bind's OWN formal description (§P1-a2.3 item 3), never against a
   re-derived signature. Raises:
   - E16 when there is no record to judge against (no signature, no description at the
     position, or bind laid no row for that formal — P0's [params_of] E03 refuses such a
     procedure before any caller lowers, so this stays a defensive witness);
   - E17 when the formal's declared type is outside the FIXED BINARY subset — matrix
     row 3 says NO evidence licenses a silent conversion, so none is invented. *)
and formal_ty ctx line (callee_key : string) (callee_pid : int) (pos : int) : H.ty =
  match SE.formals_of ctx.env callee_pid with
  | None ->
      raise_err ~line D.e_arg_evidence
        ("call to " ^ callee_key ^ " has no bind formal record, so argument "
        ^ string_of_int pos ^ " cannot be type-checked (defensive witness; the HIR "
        ^ "never assumes a formal type)")
  | Some fs ->
      match List.find_opt (fun (fd : SE.formal_desc) -> fd.SE.f_pos = pos) fs with
      | None ->
          raise_err ~line D.e_arg_evidence
            ("bind records no formal at position " ^ string_of_int pos ^ " of "
            ^ callee_key ^ " (defensive witness)")
      | Some fd ->
          match fd.SE.f_stype with
          | None ->
              (* MEASURED (this step): blocks lower pid-ascending, so the CALLER's body
                 is lowered before the callee's [params_of] runs — pinning H07 showed the
                 undeclared-formal refusal MUST be re-emitted here to keep its pinned
                 bytes. The refusal stays on the EXISTING E03 channel with the EXISTING
                 wording and the formal's own declaration line (§P1-b [C358] law: bind
                 lays no row for an undeclared formal). *)
              let bparams = (SE.block_of_pid ctx.env callee_pid).SE.east.Ast.bparams in
              (match List.nth_opt bparams pos with
               | Some n ->
                   raise_err ~line:n.Ast.pos.line D.e_decl
                     ("explicit formal dcl required in P0: parameter " ^ n.Ast.orig
                     ^ " produced no bind row")
               | None ->
                   raise_err ~line D.e_arg_evidence
                     ("formal " ^ fd.SE.f_key ^ " of " ^ callee_key ^ " has no bind "
                     ^ "declaration row to type argument " ^ string_of_int pos
                     ^ " against (defensive witness)"))
          | Some st ->
              (match ty_of_rt st ~pr:(SE.pp_stype st) with
               | Ok t -> t
               | Error s ->
                   raise_err ~line D.e_arg_type
                     ("argument " ^ string_of_int pos ^ " of call to " ^ callee_key
                     ^ " has formal type " ^ s
                     ^ "; P1-a2 lowers FIXED BINARY actual/formal pairs only (DR "
                     ^ "conversion unmeasured [TBD])"))

(* E17 naming BOTH sides (§P1-a2.5): the actual's declared type and the formal's. *)
and refuse_arg_type line (callee_key : string) (pos : int) (have : H.ty)
    (want : H.ty) =
  raise_err ~line D.e_arg_type
    ("argument " ^ string_of_int pos ^ " of call to " ^ callee_key ^ " is "
    ^ H.pp_ty have ^ " but the formal is " ^ H.pp_ty want
    ^ "; DR's conversion at an argument position is unmeasured [TBD]")

(* §P1-a2.5 decision list — MODE FIRST. Every admitted actual traces to a row of the
   evidence matrix through bind's OWN classification (§P1-a2.3); nothing is inferred
   from argument syntax alone and no disagreement is lowered silently. The formal type
   is consulted only AFTER the structural refusals, so E15/E12/E14 keep priority. *)
and lower_actual ctx bi ~caller_scope:_ ~callee_key ~callee_pid line (pos : int)
    (pm : SE.passing_mode) (e : Ast.expr) : H.actual =
  match pm with
  | SE.PM_copy_in ->
      raise_err ~line D.e_arg_evidence
        ("argument " ^ string_of_int pos ^ " of call to " ^ callee_key ^ " needs a "
        ^ "DEC copy-in temp (widening): fixed-decimal actuals are outside the P1-a2 "
        ^ "subset and no conversion is invented [C358] [TBD]")
  | SE.PM_unknown ->
      raise_err ~line D.e_arg_evidence
        ("passing evidence for argument " ^ string_of_int pos ^ " of call to "
        ^ callee_key ^ " is unknown or contradicts the argument syntax; the HIR "
        ^ "never guesses a passing mode (defensive witness)")
  | SE.PM_immediate ->
      (match e.Ast.e with
       | Ast.Enumber _ ->
           let x = lower_arith ctx bi e in
           let want = formal_ty ctx line callee_key callee_pid pos in
           if x.H.ex_ty <> want then refuse_arg_type line callee_key pos x.H.ex_ty want;
           { H.af = H.A_value x; ac_ty = want; ac_ef = x.H.ex_ef; ac_line = line }
       | _ ->
           raise_err ~line D.e_arg_evidence
             ("argument " ^ string_of_int pos ^ " of call to " ^ callee_key ^ ": bind "
             ^ "recorded an immediate but the syntax is no numeric literal "
             ^ "(contradiction; defensive witness)"))
  | SE.PM_value_cell ->
      (match e.Ast.e with
       | Ast.Eident _ | Ast.Enumber _ ->
           (* defensive: the classifier gives those own-cell/immediate evidence, and a
              recorded value cell on either is an internal inconsistency (PM_unknown). *)
           raise_err ~line D.e_arg_evidence
             ("argument " ^ string_of_int pos ^ " of call to " ^ callee_key ^ ": bind "
             ^ "recorded a value cell for a name or a literal (contradiction; "
             ^ "defensive witness)")
       | _ ->
           let x = lower_arith ctx bi e in
           let want = formal_ty ctx line callee_key callee_pid pos in
           if x.H.ex_ty <> want then refuse_arg_type line callee_key pos x.H.ex_ty want;
           { H.af = H.A_value x; ac_ty = want; ac_ef = x.H.ex_ef; ac_line = line })
  | SE.PM_own_cell ->
      match e.Ast.e with
      | Ast.Eident n ->
          let key = SE.key_of n in
          if SE.procedure ctx.env key <> None then
            (* procedures are not values — the EXISTING wording (T10) *)
            raise_err ~line D.e_call
              ("procedure " ^ key ^ " used as a value: P0 admits calls only")
          else
            (match resolve ctx bi key with
             | None ->
                 raise_err ~line D.e_arg_evidence
                   ("argument " ^ string_of_int pos ^ " of call to " ^ callee_key
                   ^ ": bind's own-cell evidence names " ^ n.Ast.orig
                   ^ ", which resolves by NO bind row (contradiction; defensive witness)")
             | Some sy ->
                 (match sy.H.sty with
                  | H.Array1 _ ->
                      (* §P1-a2.5: E15 fires BEFORE the formal gate (BY NAME, [C175]) *)
                      raise_err ~line D.e_arg_whole_array
                        ("whole-array actual " ^ n.Ast.orig ^ " at argument "
                        ^ string_of_int pos ^ " of call to " ^ callee_key
                        ^ " is outside the P1-a2 subset (element designators only; "
                        ^ "DR has no array calling convention [C175] and whole-array "
                        ^ "actuals are unmeasured [TBD])")
                  | have ->
                      let want = formal_ty ctx line callee_key callee_pid pos in
                      if have <> want then refuse_arg_type line callee_key pos have want;
                      { H.af = H.A_reference (H.D_var { sid = sy.sid });
                        ac_ty = want;
                        ac_ef = H.Pure;
                        ac_line = line }))
      | Ast.Esuffix ({ e = Ast.Eident n; _ }, subs) ->
          (* the array-ELEMENT actual [C175]: designates the element's OWN cell *)
          let key = SE.key_of n in
          (match resolve ctx bi key with
           | None ->
               (* defensive (the classifier resolved the head to an array row): the
                  EXISTING no-bind-row wording, unchanged (T10) *)
               raise_err ~line D.e_unresolved
                 ("identifier " ^ n.Ast.orig
                 ^ " resolved by NO bind row in this or any enclosing block")
           | Some sy ->
               match sy.H.sty with
               | H.Array1 { elem; lo; hi } ->
                   (match subs with
                    | [ ix ] ->
                        (* the EXISTING subscript gate and its E12 wording, verbatim *)
                        let ixe = lower_index ctx bi line n.Ast.orig lo hi ix in
                        let want = formal_ty ctx line callee_key callee_pid pos in
                        if elem <> want then
                          refuse_arg_type line callee_key pos elem want;
                        { H.af =
                            H.A_reference (H.D_elem { base = sy.sid; subs = [ ixe ] });
                          ac_ty = want;
                          ac_ef = ixe.H.ex_ef;
                          ac_line = line }
                    | l ->
                        (* defensive: the classifier admits one subscript only *)
                        raise_err ~line D.e_dims
                          ("subscript form for " ^ n.Ast.orig
                          ^ " is outside the 1-D P1-a1 subset ("
                          ^ string_of_int (List.length l) ^ " subscript(s))"))
               | _ ->
                   (* defensive: the EXISTING E12 wording, unchanged (T10) *)
                   raise_err ~line D.e_index
                     ("subscript on " ^ n.Ast.orig
                     ^ " is not a 1-D array reference in the P1-a1 subset (bind "
                     ^ "recorded no array for this name)"))
      | _ ->
          raise_err ~line D.e_arg_evidence
            ("argument " ^ string_of_int pos ^ " of call to " ^ callee_key
            ^ ": bind's own-cell evidence designates a form the HIR cannot represent "
            ^ "(defensive witness)")

(* Per-call evidence lookup (§P1-a2.3 matching law): bind's recorded site for THIS
   callee key whose argument NODES are the very nodes being lowered. No match, or a
   positional-list length disagreement, is a typed absence and refuses loudly —
   NEVER a positional guess (§P1-a2.10). *)
and lower_args ctx bi ~caller_scope ~callee_key ~callee_pid line
    (args : Ast.expr list) : H.actual list =
  match SE.call_evidence ctx.env ~caller_scope ~callee_key args with
  | None ->
      raise_err ~line D.e_arg_evidence
        ("no bind call-site record matches the call to " ^ callee_key
        ^ " (its argument nodes are not the nodes bind walked); passing modes are "
        ^ "never assumed (defensive witness)")
  | Some ce ->
      if List.length ce.SE.ce_args <> List.length args then
        raise_err ~line D.e_arg_evidence
          ("bind call-site evidence for " ^ callee_key ^ " carries "
          ^ string_of_int (List.length ce.SE.ce_args) ^ " argument positions for "
          ^ string_of_int (List.length args) ^ " arguments (defensive witness)")
      else
        List.mapi
          (fun pos (pm, a) ->
            lower_actual ctx bi ~caller_scope ~callee_key ~callee_pid line pos pm a)
          (List.combine ce.SE.ce_args args)

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

(* §P1-a1.5(g): the assignment RHS machinery, shared by the scalar (D_var) and the
   element (D_elem) targets. The Convert node, its language-rule reason and the E09
   refusal text are the EXISTING bytes moved verbatim (T10). [~tv] is the target
   type (the scalar type, or the ELEMENT type for an array element); [~line] is the
   statement line, as before. *)
and assign_value ctx (bi : SE.block_env) (rhs : Ast.expr) ~(tv : H.ty)
      ~(line : int) : H.expr =
  let v = lower_expr ctx bi rhs in
  if v.H.ex_ty <> tv then
    match (v.H.ex_ty, tv) with
    | H.Fixed_bin (p1, s1), H.Fixed_bin (p2, s2) ->
        wrap tv v.H.ex_ef v.H.ex_line
          (H.Convert
             { from = v.ex_ty; to_ty = tv; e = v;
               reason =
                 Printf.sprintf
                   "language-rule:fixed-assignment %d,%d->%d,%d (rounding/overflow profile-UNKNOWN)"
                   p1 s1 p2 s2 })
    | _ ->
        raise_err ~line D.e_conv
          ("assignment of " ^ H.pp_ty v.H.ex_ty ^ " to " ^ H.pp_ty tv
          ^ " is not representable in the P0 subset")
  else v

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
          (* §P1-a1.5(f): the ddims guard NARROWED to DIMS-WITHOUT-RECORD (A-5/A-14:
             bind silently drops a(1) and never records member arrays — those must
             keep refusing with the UNCHANGED text, H10 pins it). An admitted
             declaration (row present AND e_array = Some) lowers to Declare. *)
          let key = SE.key_of d.dname in
          let row = List.assoc_opt key bi.SE.esyms in
          if d.ddims <> []
             && (match row with
                 | Some (s : SE.symbol) -> s.SE.e_array = None
                 | None -> true)
          then
            raise_err ~line D.e_decl
              ("array declaration for " ^ d.dname.orig ^ " is outside the P0 subset")
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
          match row with
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
              (match sy.H.sty with
               | H.Array1 _ ->
                   (* §P1-a1.5(g): whole-array assignment — the HIR has no
                      whole-array node; refuse loudly (A-16: bind recorded
                      nothing about this use, the HIR decides). *)
                   raise_err ~line D.e_whole_array
                     ("whole-array use of " ^ n.Ast.orig
                     ^ " is outside the P1-a1 subset (element references only)")
               | tv ->
                   let v = assign_value ctx bi rhs ~tv ~line in
                   node (H.Assign { target = H.D_var { sid = sy.sid }; value = v }))
          | None ->
              raise_err ~line D.e_unresolved
                ("assignment target " ^ n.Ast.orig ^ " resolved by NO bind row"))
      | Ast.Esuffix ({ e = Ast.Eident n; _ }, subs) ->
          (* §P1-a1.5(g): element DESIGNATION target. Array + exactly one
             subscript ⇒ D_elem, the RHS typed against the ELEMENT type; wrong
             count ⇒ E14; non-array ⇒ E12; unresolved ⇒ the existing
             NO-bind-row channel (defensive: no fixture reaches it). *)
          let key = SE.key_of n in
          (match (SE.procedure ctx.env key, resolve ctx bi key) with
           | Some _, _ ->
               raise_err ~line D.e_call
                 ("assignment target " ^ key ^ " names a procedure")
           | None, Some sy -> (
               match (sy.H.sty, subs) with
               | H.Array1 { elem; lo; hi }, [ ix ] ->
                   let ixe = lower_index ctx bi line n.Ast.orig lo hi ix in
                   let v = assign_value ctx bi rhs ~tv:elem ~line in
                   node
                     (H.Assign
                        { target = H.D_elem { base = sy.sid; subs = [ ixe ] };
                          value = v })
               | H.Array1 _, l ->
                   raise_err ~line D.e_dims
                     ("subscript form for " ^ n.Ast.orig
                     ^ " is outside the 1-D P1-a1 subset ("
                     ^ string_of_int (List.length l) ^ " subscript(s))")
               | _ ->
                   raise_err ~line D.e_index
                     ("subscript on " ^ n.Ast.orig
                     ^ " is not a 1-D array reference in the P1-a1 subset (bind "
                     ^ "recorded no array for this name)"))
           | None, None ->
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
              (* Parser law (read first-hand, hop 5): an [Eident] statement target never
                 carries an argument list — [Sprocedure_stmt.args] is always []. The guard
                 keeps that law loud if the parser ever changes. This route deliberately
                 consults NO call evidence: bind's raw call-site records (the
                 [Semantic_env] site channel, §P1-a2.3) hold no site for a plain
                 identifier statement call, so there is nothing to align with (§P1-a2.5). *)
              if args <> [] then
                raise_err ~line D.e_expr
                  ("internal: statement call to " ^ key
                  ^ " carries arguments on an identifier target (parser law)");
              let hargs : H.actual list = [] in
              (match callee.SE.esig with
              | Some { SE.srec = true; _ } | Some { SE.sattr_rec = true; _ } ->
                  raise_err ~line D.e_call ("recursive procedure " ^ key ^ " is outside the P0 subset")
              | _ -> ());
              node (H.Call_s { pid; args = hargs })
          | None ->
              raise_err ~line D.e_unresolved
                ("call target " ^ key ^ " is no bind-registered procedure"))
      | Ast.Esuffix ({ e = Ast.Eident n; _ }, sargs) ->
          (* P1-a2 §P1-a2.5 — the INTENDED new coverage of this slice: a statement-position
             call whose SUFFIX TARGET carries an argument list now lowers to [Call_s] with
             per-position passing requirements. Parser law (read first-hand, hop 5): every
             Sprocedure_stmt has [args = []] — the list lives in the target — so the guard
             below refuses loudly if that ever changes. The zero-argument [Eident] route
             above is untouched (it records NO bind call site, so it never consults
             evidence); the refusal ORDER here mirrors lower_call (T10). *)
          if args <> [] then
            raise_err ~line D.e_expr
              ("internal: statement call to " ^ SE.key_of n
              ^ " carries arguments outside its target (parser law)")
          ;
          let key = SE.key_of n in
          (match SE.procedure ctx.env key with
           (* A non-procedure head keeps the EXISTING E04 wording: bind's raw
              call-site records prove a non-procedure suffix head records NO call
              site, so E04 — not a resolution failure — is the honest refusal
              (T10). *)
           | None ->
               raise_err ~line D.e_expr
                 "only direct procedure calls are lowered in P0"
           | Some pid ->
               let callee = SE.block_of_pid ctx.env pid in
               (match callee.SE.esig with
                | Some { SE.sret = Some _; _ } ->
                    raise_err ~line D.e_call
                      ("statement-level call to function " ^ key
                      ^ " discards a value; unlowered in P0")
                | _ -> ());
               let nformal =
                 match callee.SE.esig with
                 | Some s -> s.SE.sptr_count
                 | None -> List.length callee.SE.east.Ast.bparams
               in
               if List.length sargs <> nformal then
                 raise_err ~line D.e_call
                   ("call to " ^ key ^ " passes " ^ string_of_int (List.length sargs)
                   ^ " arguments to " ^ string_of_int nformal
                   ^ " bind-registered formals");
               let hargs =
                 lower_args ctx bi ~caller_scope:bi.SE.escope ~callee_key:key
                   ~callee_pid:pid line sargs
               in
               (match callee.SE.esig with
                | Some { SE.srec = true; _ } | Some { SE.sattr_rec = true; _ } ->
                    raise_err ~line D.e_call
                      ("recursive procedure " ^ key ^ " is outside the P0 subset")
                | _ -> ());
               node (H.Call_s { pid; args = hargs }))
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
  | Ast.Sput { stream; on_opts; kind; items } ->
      (* E2E-54/P1-m1 §P1-m1.2/.3: the accepted console PUT is ONE data item on the
         DEFAULT stream via the LIST route (deviation §P1-m1.10-1: FROM parses to
         List_ and is accepted as such). Arms fire in the PRE-REGISTERED ORDER:
         options -> kind -> item scan (ctl -> count -> class) -> data-expression
         lowering through the EXISTING channels, which are never bypassed. *)
      (match stream with
       | None -> ()
       | Some _ ->
           raise_err ~line D.e_io_construct
             "console PUT carries a stream expression; the accepted subset is the \
              default console stream only (defensive: this parser never builds one)")
      ;
      (match on_opts with
       | [] -> ()
       | o :: _ ->
           raise_err ~line D.e_io_construct
             ("console PUT option " ^ o.Ast.io_key
             ^ " is outside the accepted subset (default console stream only)"));
      (match kind with
       | Ast.List_ -> ()
       | Ast.Edit ->
           raise_err ~line D.e_io_construct
             "PUT EDIT is outside the accepted console subset (LIST route only)"
       | Ast.Editsk _ ->
           raise_err ~line D.e_io_construct
             "PUT EDIT SKIP is outside the accepted console subset (LIST route only)"
       | Ast.Item ->
           (* Parser law (read first-hand, hop 1): the bare-control forms
              PUT SKIP;/PUT PAGE; arrive with kind = Item and an ALL-control-item
              list — the honest arm for THAT shape is the control item itself
              (N8/N9). A data-carrying ITEM route refuses at the kind arm (N12). *)
           if
             items <> []
             && List.for_all
                  (function Ast.Pi_ctl _ -> true | _ -> false)
                  items
           then ()
           else
             raise_err ~line D.e_io_construct
               "PUT ITEM is outside the accepted console subset (LIST route only)")
      ;
      List.iter
        (function
         | Ast.Pi_ctl (key, _) ->
             raise_err ~line D.e_io_construct
               ("console PUT control item " ^ key
               ^ " is outside the accepted subset (no control items)")
         | _ -> ())
        items;
      if List.length items <> 1 then
        raise_err ~line D.e_io_construct
          ("console PUT carries " ^ string_of_int (List.length items)
          ^ " items; the accepted subset is exactly ONE data item")
      ;
      (match items with
       | [ Ast.Pi_data e ] ->
           (match e.Ast.e with
            | Ast.Estring s ->
                (* m1b (PLAN §P1-m1.2/.3): a literal data item is accepted when it is
                   NON-EMPTY and EVERY character lies inside the printable console
                   range 32..126; both refusals go to HIR-E22 and name their
                   construct, the charset one giving the 1-based character position
                   and the DECIMAL code point (never hex — the F8 vocabulary law).
                   (RECORDED, not hidden: the m1a transient wording of this arm was
                   replaced here; no pin ever carried those bytes, §P1-m1.3.) *)
                if String.length s = 0 then
                  raise_err ~line D.e_io_domain
                    "console PUT of an empty literal string; the accepted subset is a \
                     non-empty literal whose characters all lie in the printable \
                     console range 32..126"
                else begin
                  String.iteri
                    (fun i c ->
                      let code = Char.code c in
                      if code < 32 || code > 126 then
                        raise_err ~line D.e_io_domain
                          ("console PUT literal carries character "
                           ^ string_of_int (i + 1) ^ " (code point "
                           ^ string_of_int code
                           ^ ") outside the printable console range 32..126"))
                    s;
                  node (H.Put (H.P_text { text = s }))
                end
            | _ ->
                (* the EXISTING expression channels, never bypassed: an unresolved
                   name keeps E06, an out-of-window literal keeps E08, a whole-array
                   name keeps E13; a CONDITION value keeps E04. *)
                let v = lower_expr ctx bi e in
                node (H.Put (H.P_value v)))
       | [ it ] ->
           raise_err ~line D.e_io_construct
             ("console PUT item class " ^ put_item_class_name it
             ^ " is outside the accepted subset (a single data item only)")
       | _ -> assert false (* length checked to be 1 above *))
  | Ast.Sget { stream; on_opts; kind; items } ->
      (* §P1-m1.2/.3: the accepted console GET is ONE data item, a scalar-name
         designation, on the default stream via the LIST route; same arm ORDER. *)
      (match stream with
       | None -> ()
       | Some _ ->
           raise_err ~line D.e_io_construct
             "console GET carries a stream expression; the accepted subset is the \
              default console stream only (defensive: this parser never builds one)")
      ;
      (match on_opts with
       | [] -> ()
       | o :: _ ->
           raise_err ~line D.e_io_construct
             ("console GET option " ^ o.Ast.io_key
             ^ " is outside the accepted subset (default console stream only)"));
      (match kind with
       | Ast.List_ -> ()
       | Ast.Edit ->
           raise_err ~line D.e_io_construct
             "GET EDIT is outside the accepted console subset (LIST route only)"
       | Ast.Const_ ->
           raise_err ~line D.e_io_construct
             "GET CONST is outside the accepted console subset (LIST route only)")
      ;
      List.iter
        (function
         | Ast.Pi_ctl (key, _) ->
             raise_err ~line D.e_io_construct
               ("console GET control item " ^ key
               ^ " is outside the accepted subset (no control items)")
         | _ -> ())
        items;
      if List.length items <> 1 then
        raise_err ~line D.e_io_construct
          ("console GET carries " ^ string_of_int (List.length items)
          ^ " items; the accepted subset is exactly ONE data item")
      ;
      (match items with
       | [ Ast.Pi_data e ] ->
           (* target shape AFTER the EXISTING resolve channel, before anything else
              touches the symbol (§P1-m1.3); an unresolved name keeps E06. *)
           (match e.Ast.e with
            | Ast.Eident n ->
                let key = SE.key_of n in
                (match resolve ctx bi key with
                 | None ->
                     (* the EXISTING unresolved wording, unchanged (T10) *)
                     raise_err ~line D.e_unresolved
                       ("identifier " ^ n.Ast.orig
                       ^ " resolved by NO bind row in this or any enclosing block")
                 | Some sy ->
                     (match sy.H.sty with
                      | H.Array1 _ ->
                          raise_err ~line D.e_io_construct
                            ("GET target " ^ n.Ast.orig
                            ^ " designates an array; the accepted subset is a scalar \
                               name designation")
                      | H.Fixed_bin _ -> node (H.Get (H.D_var { sid = sy.sid }))
                      | t ->
                          (* defensive: project_syms admits FIXED BINARY scalars and
                             array rows only, so no other type can reach this arm —
                             same honest status as the P1-a2 E16 arm (§P1-m1.3). *)
                          raise_err ~line D.e_io_domain
                            ("GET target " ^ n.Ast.orig ^ " has type " ^ H.pp_ty t
                            ^ ", not FIXED BINARY(p,0) (defensive witness)")))
            | _ ->
                raise_err ~line D.e_io_construct
                  ("GET target " ^ get_target_shape e
                  ^ " is outside the accepted subset (a scalar name designation \
                     only)"))
       | [ it ] ->
           raise_err ~line D.e_io_construct
             ("console GET item class " ^ put_item_class_name it
             ^ " is outside the accepted subset (a single data item only)")
       | _ -> assert false (* length checked to be 1 above *))
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
