(* hir/semtest.ml — semantic-authority test binary (E2E-54/P1-b, PLAN §P1-b.4).

   This tool judges the HIR build path against the LIVE environment: it parses a
   positive fixture, builds the [Semantic_env] projection over bind's own plan,
   lowers the same program through [Hir_build.build], and asserts the thirteen
   pre-registered invariants (I1-I7 from §P1-b.4, I8-I10 from §P1-a1.7, I11-I13
   from §P1-a2.6) that every semantic-carrying [Hir] field equals the bind-fact
   projection it claims to project. Dump text is never consulted — a check must
   fail even if the CLI printer is broken (falsifier S6).

   Output contract (§P1-b.4):
     every invariant holds  -> stdout gets EXACTLY one line
        SEMANTIC-AUTHORITY OK <n> refs / <m> syms        rc 0
     any invariant violated -> `SEM-FAIL ...' lines on stderr, rc 1, ZERO stdout
   refs counts every walked reference — Var reads and assign targets (I2), call
   sites (I7), element reads and designations (I8) — across all procedure
   bodies; syms is the number of projected Hir symbols (I1).

   Corrupt controls (non-vacuity, S6/T7) — each runs the SAME comparison the
   live invariant uses, on deliberately perturbed data, and must see it reject;
   a control that ACCEPTS the corruption is itself a SEM-FAIL, and a fixture
   with nothing to perturb says so loudly (`nothing was proven'). Every control
   exits 1 with SEM-FAIL-only stderr and ZERO stdout, never the OK line:
     --corrupt              first projected sym re-checked with a wrong sid (I1)
     --corrupt-array-hi     one bounds triple gets hi+1 before the I9 comparison
     --corrupt-array-base   one element reference is repointed at a non-array
                            sid before the I8 comparison
     --corrupt-formal       one formal's sid shifted by +1000 before the I13
                            comparison (wrong formal identity, §P1-a2.6)
     --corrupt-actual-base  one argument designator repointed at a symbol the
                            caller scope cannot resolve before the I11
                            comparison (wrong actual base, §P1-a2.6)
     --corrupt-arg-position the recorded passing-mode list of one call loses its
                            first position before the I12 comparison (the
                            arity-disagreement branch, §P1-a2.6)
     --corrupt-mode         one own/value-cell passing mode flipped before the
                            I12 comparison (wrong passing requirement)

   This is an executable in ocaml/hir/ (never ocaml/bin/ — the P0 F1 exe-dir
   law: a stanza in the hir directory does not move pli80c.exe; S1 re-checked
   after adding it). It links [pli80] + [pli80_hir] only. Reading bind's raw
   layout here (bind_rows, bind_arrays, proc_layout, and — §P1-a2.6 — the call
   records pl_calls with their positional cs_temps/cs_copies/cs_dec flags) is
   intentional: a TEST must judge the env against its authority, not against
   itself; the S5/T5 one-reader law binds the COMPILER path (hir_build reads
   none of these; semantic_env is the projection, this binary the intentional
   authority reader). *)

module Ast = Pli80.Ast
module Bind = Pli80.Bind
module D = Pli80_hir.Diagnostic
module H = Pli80_hir.Hir
module HB = Pli80_hir.Hir_build
module SE = Pli80_hir.Semantic_env

(* ---------- failure accumulation ---------- *)

type mode =
  | Live
  | Corrupt
  | Corrupt_hi
  | Corrupt_base
  | Corrupt_formal
  | Corrupt_actual
  | Corrupt_argpos
  | Corrupt_mode

let fails : string list ref = ref []
let bad fmt = Printf.ksprintf (fun s -> fails := s :: !fails) fmt

let die_early msg =
  (* parse/env/build blowups: SEM-FAIL, rc 1, zero stdout — the tool itself
     refuses loudly rather than silently claiming authority. *)
  prerr_endline ("SEM-FAIL: " ^ msg);
  exit 1

let show ds = String.concat " / " (List.map D.pp ds)

(* ---------- shared traversal ---------- *)

(* One element reference collected by the walk (§P1-a1.7 I8). [ety] is the
   NODE's type where a node has one (Elem_read / expression Elem_ref); the
   D_elem TARGET carries no type field, so [ety = None] there and the
   comparison checks base soundness only (a P1-a2 reference ACTUAL does carry
   its recorded formal type, so [ety = Some] there — §P1-a2.6). *)
type elem_ref = { base : int; write : bool; ety : H.ty option }

type ref_item =
  | R_var of { sid : int; ty : H.ty option }
      (** [ty] = the expression node's type where there is one; D_var targets
          have none (the type lives on the symbol, §P1-a1.3). *)
  | R_call of { pid : int; nargs : int }
  | R_elem of elem_ref (* P1-a1 I8: element read / designation *)

let rec walk_expr acc (e : H.expr) : ref_item list =
  match e.H.ex with
  | H.Const _ -> acc
  | H.Var { sid; _ } -> R_var { sid; ty = Some e.H.ex_ty } :: acc
  | H.Bin { left; right; _ } -> walk_expr (walk_expr acc right) left
  | H.Neg { e = inner } -> walk_expr acc inner
  | H.Convert { e = inner; _ } -> walk_expr acc inner
  | H.Call_e { pid; args } ->
      List.fold_left walk_actual
        (R_call { pid; nargs = List.length args } :: acc)
        args
  | H.Elem_read { base; subs } ->
      List.fold_left walk_expr
        (R_elem { base; write = false; ety = Some e.H.ex_ty } :: acc)
        subs
  | H.Elem_ref { base; subs } ->
      List.fold_left walk_expr
        (R_elem { base; write = true; ety = Some e.H.ex_ty } :: acc)
        subs

and walk_actual acc (a : H.actual) : ref_item list =
  (* P1-a2 §P1-a2.6 walk law (MINIMAL compile-adaptation): an actual contributes
     EXACTLY the item its old expression node contributed, so every measured
     SEMANTIC-AUTHORITY count is preserved. A reference actual is a READ at an
     argument position ([write] stays false; the callee's writes are its own
     references), and its recorded type is the callee's declared formal type — equal
     to the designated type by construction (the E17 discipline refuses otherwise). *)
  match a.H.af with
  | H.A_value e -> walk_expr acc e
  | H.A_reference (H.D_var { sid }) -> R_var { sid; ty = Some a.H.ac_ty } :: acc
  | H.A_reference (H.D_elem { base; subs }) ->
      List.fold_left walk_expr
        (R_elem { base; write = false; ety = Some a.H.ac_ty } :: acc)
        subs

and walk_target acc (t : H.target) : ref_item list =
  match t with
  | H.D_var { sid } -> R_var { sid; ty = None } :: acc
  | H.D_elem { base; subs } ->
      List.fold_left walk_expr (R_elem { base; write = true; ety = None } :: acc)
        subs

let rec walk_stmt acc (s : H.stmt) : ref_item list =
  match s.H.st with
  | H.Declare _ | H.Stop -> acc
  | H.Assign { target; value } -> walk_target (walk_expr acc value) target
  | H.If { cond; then_; else_ } ->
      List.fold_left walk_stmt
        (List.fold_left walk_stmt (walk_expr acc cond) then_)
        else_
  | H.While { cond; body } -> List.fold_left walk_stmt (walk_expr acc cond) body
  | H.Call_s { pid; args } ->
      List.fold_left walk_actual
        (R_call { pid; nargs = List.length args } :: acc)
        args
  | H.Return eo -> (match eo with Some x -> walk_expr acc x | None -> acc)

(* ---------- P1-a2 §P1-a2.6: the call-collection walk (AST <-> HIR, 1:1) ----------

   [SE.call_evidence] answers for a call by PHYSICAL identity of the argument
   nodes (the §P1-a2.3 matching law), but HIR [actual] nodes carry NO AST node.
   The evidence is therefore re-found by walking the fixture's own AST block in
   EXACT 1:1 lockstep with the lowered statements, mirroring [Hir_build]'s
   lowering shape: [Semantic_env.block_of_pid pid .east.bstmts] vs [proc.body].
   ANY structural disagreement is a LOUD SEM-FAIL — the walker never silently
   skips a call and never positional-guesses. This pass adds NO reference item:
   the walked [R_var]/[R_call]/[R_elem] counts and every measured
   SEMANTIC-AUTHORITY OK line are untouched (§P1-a2.6). *)

type call_item = {
  ci_owner_pid : int;
  ci_owner_scope : int;
  ci_callee : int; (** HIR proc pid of the callee, from the Call node *)
  ci_key : string; (** callee's lowered key — the key bind's site record carries *)
  ci_ast_args : Ast.expr list option;
      (** [None] exactly on the zero-argument identifier statement route (§P1-a2.5:
          bind records NO site there — the exclusion arm, UNEXERCISED by every
          positive fixture, recorded honestly); [Some] carries the very [Ast.expr]
          nodes the CLI parsed, for the identity lookup. *)
  ci_args : H.actual list; (** the lowered HIR actuals, positional order *)
}

exception Pair_fail of string

let bad_pair msg = raise (Pair_fail msg)

let is_eident (e : Ast.expr) =
  match e.Ast.e with Ast.Eident _ -> true | _ -> false

let eident_key (e : Ast.expr) =
  match e.Ast.e with Ast.Eident n -> SE.key_of n | _ -> bad_pair "not an identifier"

(* flatten mirror of [Hir_build.flatten_group]: a grouped DO/branch body splices
   its statements; a statement-only nested BEGIN stays a statement here and is
   spliced by [pair_stmts] with the SAME owner scope; a procedure definition in
   a group body was refused by the build and fails loudly. *)
let flatten_mirror (s : Ast.stmt) : Ast.stmt list =
  match s.Ast.st with
  | Ast.Sdobegin l -> l
  | Ast.Sproc bs ->
      let b = bs.Ast.blk in
      if b.Ast.bkind = Ast.Bproc then
        bad_pair "a procedure definition appears as a grouped body statement"
      else [ s ]
  | _ -> [ s ]

let take_hir n hs =
  let rec go k acc rest =
    if k = 0 then (List.rev acc, rest)
    else
      match rest with
      | [] -> bad_pair "fewer lowered statements than the AST expects"
      | x :: tl -> go (k - 1) (x :: acc) tl
  in
  go n [] hs

let rec pair_stmts env owner acc (ss : Ast.stmt list) (hs : H.stmt list) =
  match ss with
  | [] -> (acc, hs)
  | s :: rest -> (
      match s.Ast.st with
      | Ast.Snull _ -> pair_stmts env owner acc rest hs
      | Ast.Sproc bs ->
          let b = bs.Ast.blk in
          if b.Ast.bkind = Ast.Bproc then
            (* definition: lowers as its OWN pid entry, consumes nothing here *)
            pair_stmts env owner acc rest hs
          else if b.Ast.bdecls <> [] then
            bad_pair "a nested BEGIN carries declarations the build refuses"
          else
            (* statement-only BEGIN: hir_build splices inline into the SAME
               owner — the mirror follows with the same owner scope *)
            let acc, hs = pair_stmts env owner acc b.Ast.bstmts hs in
            pair_stmts env owner acc rest hs
      | Ast.Sdcl ds ->
          let taken, hs = take_hir (List.length ds) hs in
          List.iter
            (fun (h : H.stmt) ->
              match h.H.st with
              | H.Declare _ -> ()
              | _ -> bad_pair "a dcl item lowered to a non-declaration node")
            taken;
          pair_stmts env owner acc rest hs
      | Ast.Sassign { lhs; rhs } -> (
          match hs with
          | hd :: tl -> (
              match hd.H.st with
              | H.Assign { target; value } ->
                  let acc = pair_expr env owner acc rhs value in
                  let acc = pair_designator env owner acc lhs target in
                  pair_stmts env owner acc rest tl
              | _ -> bad_pair "an assignment is not paired with an assign node")
          | [] -> bad_pair "fewer lowered statements than the AST expects")
      | Ast.Sif { cond; then_; els } -> (
          match hs with
          | hd :: tl -> (
              match hd.H.st with
              | H.If { cond = c; then_ = th; else_ = e } ->
                  let acc = pair_expr env owner acc cond c in
                  let acc = pair_group env owner acc then_ th in
                  let acc =
                    match els with
                    | None ->
                        if e <> [] then
                          bad_pair "an if without ELSE carries else statements"
                        else acc
                    | Some x -> pair_group env owner acc x e
                  in
                  pair_stmts env owner acc rest tl
              | _ -> bad_pair "an if is not paired with an if node")
          | [] -> bad_pair "fewer lowered statements than the AST expects")
      | Ast.Sdowhile { cond; body } -> (
          match hs with
          | hd :: tl -> (
              match hd.H.st with
              | H.While { cond = c; body = b } ->
                  let acc = pair_expr env owner acc cond c in
                  let acc = pair_group env owner acc body b in
                  pair_stmts env owner acc rest tl
              | _ -> bad_pair "a DO WHILE is not paired with a while node")
          | [] -> bad_pair "fewer lowered statements than the AST expects")
      | Ast.Sstop None -> (
          match hs with
          | hd :: tl -> (
              match hd.H.st with
              | H.Stop -> pair_stmts env owner acc rest tl
              | _ -> bad_pair "a STOP is not paired with a stop node")
          | [] -> bad_pair "fewer lowered statements than the AST expects")
      | Ast.Sreturn eo -> (
          match hs with
          | hd :: tl -> (
              match (eo, hd.H.st) with
              | None, H.Return None -> pair_stmts env owner acc rest tl
              | Some ae, H.Return (Some hv) ->
                  let acc = pair_expr env owner acc ae hv in
                  pair_stmts env owner acc rest tl
              | _ -> bad_pair "a RETURN does not pair with its value shape")
          | [] -> bad_pair "fewer lowered statements than the AST expects")
      | Ast.Sprocedure_stmt { target; args } -> (
          (* parser law (read first-hand, hop 5): the statement's own [args]
             field is ALWAYS [] — any list lives in the suffix target *)
          if args <> [] then
            bad_pair "a statement call carries arguments outside its target";
          match hs with
          | hd :: tl -> (
              match hd.H.st with
              | H.Call_s { pid; args = hargs } ->
                  let mk ast_args key =
                    { ci_owner_pid = owner.SE.epid;
                      ci_owner_scope = owner.SE.escope;
                      ci_callee = pid;
                      ci_key = key;
                      ci_ast_args = ast_args;
                      ci_args = hargs }
                  in
                  let shape_ok, acc =
                    match target.Ast.e with
                    | Ast.Eident _ ->
                        (* zero-argument identifier route: bind records NO site
                           (§P1-a2.5) — excluded from the Some-requirement *)
                        if hargs <> [] then
                          bad_pair "an identifier-route call carries actuals";
                        (true, acc @ [ mk None (eident_key target) ])
                    | Ast.Esuffix (hd2, sargs) when is_eident hd2 ->
                        let acc = acc @ [ mk (Some sargs) (eident_key hd2) ] in
                        (true, pair_actuals env owner acc sargs hargs)
                    | _ -> (false, acc)
                  in
                  if not shape_ok then
                    bad_pair "a statement call has no identifier-shaped target";
                  pair_stmts env owner acc rest tl
              | _ -> bad_pair "a procedure statement is not paired with a call node")
          | [] -> bad_pair "fewer lowered statements than the AST expects")
      | _ -> bad_pair "a statement form outside the mirrored subset reached the walk")

(* branch/group body: [flatten] then lower — the mirror consumes exactly the
   node's statement list and rejects a leftover. *)
and pair_group env owner acc (s : Ast.stmt) (body : H.stmt list) =
  match pair_stmts env owner acc (flatten_mirror s) body with
  | acc, [] -> acc
  | _ -> bad_pair "statements remain after a grouped body ran out"

and pair_expr env owner acc (a : Ast.expr) (h : H.expr) =
  (* transparency laws (read first-hand in hir_build): parentheses carry no
     semantics (both lowering paths strip [Econd]); [Convert] is a wrapper the
     assignment/return paths add, never the expression path itself. *)
  match a.Ast.e with
  | Ast.Econd inner -> pair_expr env owner acc inner h
  | _ -> (
      match h.H.ex with
      | H.Convert { e = inner; _ } -> pair_expr env owner acc a inner
      | H.Const { text } ->
          (match a.Ast.e with
           | Ast.Enumber s when String.equal s text -> acc
           | _ -> bad_pair "a constant node is not paired with its literal syntax")
      | H.Var _ ->
          (match a.Ast.e with
           | Ast.Eident _ -> acc
           | _ -> bad_pair "a variable read is paired with compound syntax")
      | H.Bin { left; right; _ } ->
          (match a.Ast.e with
           | Ast.Ebinary (Ast.Add, l, r)
           | Ast.Ebinary (Ast.Sub, l, r)
           | Ast.Ebinary (Ast.Mul, l, r)
           | Ast.Ebinary (Ast.EqR _, l, r) ->
               pair_expr env owner (pair_expr env owner acc l left) r right
           | _ -> bad_pair "a binary node is paired with a different syntax")
      | H.Neg { e = inner } ->
          (match a.Ast.e with
           | Ast.Eprefix (Ast.Minus, x) -> pair_expr env owner acc x inner
           | _ -> bad_pair "a negate node is paired with a different prefix")
      | H.Call_e { pid; args } ->
          (match a.Ast.e with
           | Ast.Esuffix (hd, sargs) when is_eident hd ->
               let acc =
                 acc
                 @ [ { ci_owner_pid = owner.SE.epid;
                       ci_owner_scope = owner.SE.escope;
                       ci_callee = pid;
                       ci_key = eident_key hd;
                       ci_ast_args = Some sargs;
                       ci_args = args } ]
               in
               pair_actuals env owner acc sargs args
           | _ -> bad_pair "a value call node is paired with non-suffix syntax")
      | H.Elem_read { subs; _ } | H.Elem_ref { subs; _ } ->
          (match a.Ast.e with
           | Ast.Esuffix (_, sargs) when List.length sargs = List.length subs ->
               List.fold_left2 (pair_expr env owner) acc sargs subs
           | _ -> bad_pair "an element node is paired with a different subscript shape"))

and pair_designator _env _owner acc (a : Ast.expr) (d : H.designator) =
  (* SHAPE pairing only: sid soundness is the invariants' job (I2/I11); the
     mirroring proves the target/actual roles sit where the lowering put them
     (assignment targets §P1-a1.5(g), reference actuals §P1-a2.5). *)
  match d with
  | H.D_var _ ->
      (match a.Ast.e with
       | Ast.Eident _ -> acc
       | _ -> bad_pair "a variable designator is paired with compound syntax")
  | H.D_elem { subs; _ } ->
      (match a.Ast.e with
       | Ast.Esuffix (_, sargs) when List.length sargs = List.length subs ->
           List.fold_left2 (pair_expr _env _owner) acc sargs subs
       | _ -> bad_pair "an element designator is paired with a non-suffix form")

and pair_actuals env owner acc (as_ : Ast.expr list) (hs : H.actual list) =
  match (as_, hs) with
  | [], [] -> acc
  | a :: ar, h :: hr ->
      let acc =
        match h.H.af with
        | H.A_value e -> pair_expr env owner acc a e
        | H.A_reference d -> pair_designator env owner acc a d
      in
      pair_actuals env owner acc ar hr
  | _ -> bad_pair "an argument list and its lowering have different lengths"

(* [collect_calls] runs the walk over EVERY procedure body (pid-ascending,
   statements in AST order, nested value calls emitted at their Call_e node —
   DFS entry order). A pairing failure exits SEM-FAIL rc 1 loudly. *)
let collect_calls env prog =
  try
    let go acc (p : H.proc) =
      let owner = SE.block_of_pid env p.H.pid in
      let acc, left =
        pair_stmts env owner acc owner.SE.east.Ast.bstmts p.H.body
      in
      if left <> [] then
        bad_pair "lowered statements remain after the AST block ran out";
      acc
    in
    List.fold_left go [] prog.H.procs
  with Pair_fail msg ->
    prerr_endline ("SEM-FAIL: call walker — " ^ msg);
    exit 1

(* ---------- the shared passing-evidence comparison (I12, §P1-a2.6) ----------

   Judges one collected call against the evidence bind's OWN site record
   yielded through [call_evidence]. [ce] is passed IN (not looked up inside)
   so --corrupt-arg-position and --corrupt-mode can perturb the evidence and
   re-run THIS code — the non-vacuity law, never a copy. The mode naming
   renders the SYMBOLIC classes only; no address, no size, nothing physical. *)
let mode_name = function
  | SE.PM_value_cell -> "a value cell"
  | SE.PM_own_cell -> "its own cell"
  | SE.PM_immediate -> "an immediate"
  | SE.PM_copy_in -> "a copy-in temp"
  | SE.PM_unknown -> "unknown evidence"

let arg_evidence_mismatch (env : SE.t) (ci : call_item)
    (ce : SE.call_evidence) : string option =
  let f = string_of_int in
  let nargs = List.length ci.ci_args in
  match
    (try Some (SE.signature env ci.ci_callee) with SE.Not_found _ -> None)
  with
  | Some (Some sg) -> (
      let position i a pm =
        match (a.H.af, pm) with
        | H.A_reference _, SE.PM_own_cell -> None
        | H.A_value { H.ex = H.Const _; _ }, SE.PM_immediate -> None
        | H.A_value _, SE.PM_value_cell -> None
        | _, SE.PM_copy_in ->
            Some ("copy-in evidence backs an admitted node at argument " ^ f i
              ^ " — outside the subset")
        | _, SE.PM_unknown ->
            Some ("unknown passing evidence backs an admitted node at argument "
              ^ f i ^ " — the env never guesses")
        | H.A_reference _, other ->
            Some ("argument " ^ f i ^ " needs its own cell (bind recorded "
              ^ mode_name other ^ ")")
        | H.A_value { H.ex = H.Const _; _ }, other ->
            Some ("argument " ^ f i ^ " is an immediate (bind recorded "
              ^ mode_name other ^ ")")
        | H.A_value _, other ->
            Some ("argument " ^ f i ^ " needs a value cell (bind recorded "
              ^ mode_name other ^ ")")
      in
      if not (String.equal ce.SE.ce_proc ci.ci_key) then
        Some ("recorded site names " ^ ce.SE.ce_proc ^ ", the walked call names "
          ^ ci.ci_key)
      else if List.length ci.ci_args <> List.length ce.SE.ce_args then
        Some ("positional evidence list disagrees in length — impossible by bind \
               construction")
      else if sg.SE.sptr_count <> nargs then
        Some ("call to " ^ ci.ci_key ^ " passes " ^ f nargs
          ^ " arguments to " ^ f sg.SE.sptr_count ^ " bind formal cells")
      else if List.length ce.SE.ce_dec <> nargs then
        Some ("DEC-formal flags disagree in length — impossible by bind \
               construction")
      else
        List.find_map Fun.id
          (List.mapi
             (fun i (pm, a) -> position i a pm)
             (List.combine ce.SE.ce_args ci.ci_args))
      )
  | _ ->
      Some ("callee pid " ^ f ci.ci_callee ^ " has no bind signature")

(* ---------- the shared formal-API comparison (I13, §P1-a2.6) ----------

   [f_key] is checked against the LOWERED AST parameter names of the owning
   block (recorded deviation from the pre-registration wording "f_key = the
   sptrs entry": [sptrs] and [f_key] share one bind origin, so the comparison
   here is against the SYNTAX — bind's own alias policy is
   [String.lowercase_ascii] of the source spelling; [String.equal] on the
   lowered name keeps it exact). [f_sid]/[f_stype] are the env identity and
   type behind the Hir param row. --corrupt-formal perturbs an [f_sid] and
   re-runs THIS code. *)
let formals_mismatch (env : SE.t) (p : H.proc) (fs : SE.formal_desc list) :
    string option =
  let f = string_of_int in
  match (try Some (SE.block_of_pid env p.H.pid) with SE.Not_found _ -> None) with
  | None -> Some ("proc(" ^ f p.H.pid ^ ") has no env block behind it")
  | Some b ->
      let names = b.SE.eformals in
      if
        List.length fs <> List.length p.H.params
        || List.length names <> List.length fs
      then
        Some ("formal record lengths disagree for proc(" ^ f p.H.pid ^ ")")
      else
        let rec go i fs params names =
          match (fs, params, names) with
          | [], [], [] -> None
          | fd :: fr, sid :: pr, nm :: nr -> (
              if fd.SE.f_pos <> i then
                Some ("formal slot " ^ f i ^ " reports position "
                  ^ f fd.SE.f_pos)
              else if not (String.equal fd.SE.f_key (String.lowercase_ascii nm))
              then
                Some ("formal " ^ nm ^ " of proc(" ^ f p.H.pid
                  ^ ") carries key " ^ fd.SE.f_key ^ ", not its lowered name")
              else if fd.SE.f_sid <> Some sid then
                Some ("formal " ^ fd.SE.f_key ^ " of proc(" ^ f p.H.pid
                  ^ ") projects sid "
                  ^ (match fd.SE.f_sid with None -> "None" | Some s -> f s)
                  ^ ", bind's row says " ^ f sid)
              else
                match (fd.SE.f_stype, SE.symbol env sid) with
                | Some ty, Some s when ty = s.SE.ety -> go (i + 1) fr pr nr
                | _ ->
                    Some ("env symbol/type differs for formal " ^ fd.SE.f_key
                      ^ " of proc(" ^ f p.H.pid ^ ")"))
          | _ ->
              Some ("formal record lengths disagree for proc(" ^ f p.H.pid
                ^ ")")
        in
        go 0 fs p.H.params names

let env_rows (env : SE.t) : SE.symbol list =
  List.concat_map
    (fun (b : SE.block_env) -> List.map snd b.SE.esyms)
    (SE.blocks env)

(* ---------- I1 comparison, used verbatim by the --corrupt control ---------- *)

(* One [Hir.sym] against the env symbol it projects; [None] means agreement,
   [Some w] names the disagreement. Field set and mapping mirror §P1-b.4
   exactly: sid/key/orig/scope/storage/line/type. *)
let sym_mismatch (env : SE.t) (hs : H.sym) : string option =
  let f = string_of_int in
  match SE.symbol env hs.H.sid with
  | None -> Some ("sym " ^ f hs.H.sid ^ " has no env symbol behind it")
  | Some s ->
      let st =
        match s.SE.estorage with
        | SE.S_formal -> H.Formal
        | SE.S_auto -> H.Auto
        | SE.S_static -> H.Static
      in
      let w =
        if not (String.equal hs.H.skey s.SE.ekey) then
          Some "skey differs from the env ekey"
        else if not (String.equal hs.H.sorig s.SE.eorig) then
          Some ("sorig differs from the env spelling for " ^ s.SE.ekey)
        else if hs.H.scope <> s.SE.escope then
          Some ("scope " ^ f hs.H.scope ^ " vs env scope " ^ f s.SE.escope)
        else if hs.H.sline <> s.SE.eline then
          Some ("line " ^ f hs.H.sline ^ " vs env dcl line " ^ f s.SE.eline)
        else if hs.H.sstorage <> st then
          Some ("storage differs for " ^ s.SE.ekey)
        else
          (* P1-a1 §P1-a1.7(a): the comparison is ARRAY-AWARE. With no array
             record the scalar branch below is EXACTLY the P1-b bytes; with one,
             the projection must be Array1 carrying the env's bounds and the
             element image of the env element fact. *)
          match s.SE.e_array with
          | None -> (
              match s.SE.ety with
              | SE.SFixed_bin p when hs.H.sty = H.Fixed_bin (p, 0) -> None
              | SE.SFixed_bin p ->
                  Some ("type differs for " ^ s.SE.ekey ^ " (env bin(" ^ f p ^ "))")
              | _ ->
                  Some ("env symbol " ^ s.SE.ekey
                    ^ " is outside the subset gate; no sym may project it"))
          | Some a -> (
              match a.SE.a_elem with
              | SE.SFixed_bin p -> (
                  match hs.H.sty with
                  | H.Array1 { elem; lo; hi } ->
                      if elem = H.Fixed_bin (p, 0) && lo = a.SE.a_lo
                         && hi = a.SE.a_hi then None
                      else
                        Some
                          ("array projection differs for " ^ s.SE.ekey
                          ^ " (env element bin(" ^ f p ^ ") bounds ["
                          ^ f a.SE.a_lo ^ ":" ^ f a.SE.a_hi ^ "])")
                  | _ ->
                      Some ("env symbol " ^ s.SE.ekey
                        ^ " carries an array record but its sym is not projected \
                            as Array1"))
              | _ ->
                  Some ("array element of " ^ s.SE.ekey
                    ^ " is outside the HIR element gate"))
      in
      (match w with
      | None -> None
      | Some m -> Some (m ^ " (sym " ^ f hs.H.sid ^ ")"))

(* ---------- the seven invariants (§P1-b.4, numbered as pre-registered) ---------- *)

(* 1. every Hir.sym field equals the env symbol projection. *)
let i1 env prog =
  let rows = env_rows env in
  let syms = prog.H.syms in
  if List.length syms <> List.length rows then
    bad "invariant 1: %d Hir syms vs %d env symbols"
      (List.length syms) (List.length rows);
  let rec asc prev = function
    | [] -> ()
    | hd :: tl ->
        if hd.H.sid <= prev then
          bad "invariant 1: sids not strictly ascending at sym %d" hd.H.sid;
        asc hd.H.sid tl
  in
  asc (-1) syms;
  let m = List.length syms in
  if m > 0 then begin
    if (List.nth syms 0).H.sid <> 0 then
      bad "invariant 1: sid sequence does not start at 0";
    if (List.nth syms (m - 1)).H.sid <> m - 1 then
      bad "invariant 1: sid sequence does not end at m-1 (%d)" (m - 1)
  end;
  List.iter
    (fun hs ->
      match sym_mismatch env hs with
      | None -> ()
      | Some w -> bad "invariant 1: %s" w)
    syms

(* ---------- the shared reference-designator comparison (the I2 law) ----------

   Extracted VERBATIM from invariant 2 by the §P1-a2.6 shared-comparison law:
   I2, I11 (via [designator_mismatch]) and --corrupt-actual-base all run THIS
   code, never a copy. [scope] is the REFERRING scope; the owning proc number
   in the first message is re-read from the env block for that scope, so the
   message bytes are exactly the pre-extraction i2 messages. *)
let var_mismatch (env : SE.t) (scope : int) (sid : int) : string option =
  let f = string_of_int in
  match SE.symbol env sid with
  | None ->
      let pid =
        try (SE.block_of_scope env scope).SE.epid with SE.Not_found _ -> scope
      in
      Some ("proc(" ^ f pid ^ ") reads sym(" ^ f sid
        ^ ") the env does not know")
  | Some s -> (
      match
        (try SE.resolve env scope s.SE.ekey with SE.Not_found _ -> None)
      with
      | Some found when found.SE.esid = sid -> None
      | Some found ->
          Some ("name " ^ s.SE.ekey ^ " resolves from scope " ^ f scope
            ^ " to sym(" ^ f found.SE.esid ^ "), not the sym(" ^ f sid
            ^ ") this reference was lowered to")
      | None ->
          Some ("name " ^ s.SE.ekey ^ " resolves from scope " ^ f scope
            ^ " to nothing"))

(* 2. every Var in a body resolves, from the REFERRING procedure's scope,
   through Semantic_env.resolve to exactly that symbol — shadowing is judged
   against bind rows, not dump strings (H03: sym(0) is the OUTER x; the inner
   x sym(3) must not answer that reference). *)
let i2 env prog =
  List.iter
    (fun (p : H.proc) ->
      List.iter
        (fun r ->
          match r with
          | R_call _ | R_elem _ -> ()
          | R_var { sid; _ } -> (
              match var_mismatch env p.H.scope sid with
              | None -> ()
              | Some w -> bad "invariant 2: %s" w))
        (List.fold_left walk_stmt [] p.H.body))
    prog.H.procs

(* 8. reference soundness (§P1-a1.7 I8): every element read/designation has a
   base that resolves (from the REFERRING procedure's scope, shadowing included)
   to an env symbol WITH an array record, and the node's type equals the env
   element projection (mapped exactly as I1 maps it). No Var node ever carries
   an [Array1] type — a whole-array value reference is unrepresentable and any
   one that appeared would be the silent-collapse defect this guards. The
   per-reference comparison is a shared function so --corrupt-array-base runs
   THE SAME CODE as the invariant, never a copy.

   §P1-a2.6 GENERALISATION (recorded deviation): the taking of the scope moved
   from [p.H.scope] to an explicit [scope] parameter so I11 can run the SAME
   comparison from a CALLER scope; the comparison logic is bit-identical and
   the messages print the very scope passed in. *)
let elem_ref_mismatch (env : SE.t) (scope : int) (r : elem_ref) : string option =
  let f = string_of_int in
  match SE.symbol env r.base with
  | None -> Some ("sym(" ^ f r.base ^ ") has no env symbol behind it")
  | Some s -> (
      match s.SE.e_array with
      | None ->
          Some ("element base sym(" ^ f r.base ^ ") (" ^ s.SE.ekey
            ^ ") carries no array record")
      | Some a -> (
          match
            (try SE.resolve env scope s.SE.ekey with SE.Not_found _ -> None)
          with
          | Some found when found.SE.esid = r.base -> (
              match (r.ety, a.SE.a_elem) with
              | None, _ -> None (* D_elem target: no node type to judge (§P1-a1.3) *)
              | Some t, SE.SFixed_bin p ->
                  if t = H.Fixed_bin (p, 0) then None
                  else
                    Some ("element reference type differs from the env element \
                          projection for " ^ s.SE.ekey)
              | Some _, _ ->
                  Some ("element of " ^ s.SE.ekey
                    ^ " is outside the env element projection; no node type \
                       may claim it"))
          | Some _ ->
              Some ("element base sym(" ^ f r.base ^ ") is not what scope "
                ^ f scope ^ " resolves for " ^ s.SE.ekey ^ " (shadowing?)")
          | None ->
              Some ("element base name " ^ s.SE.ekey ^ " resolves from scope "
                ^ f scope ^ " to nothing")))

let i8 env prog =
  List.iter
    (fun (p : H.proc) ->
      List.iter
        (fun r ->
          match r with
          | R_call _ -> ()
          | R_var { sid; ty = Some (H.Array1 _) } ->
              bad "invariant 8: var sym(%d) in proc(%d) carries an Array1 type \
                   (whole-array silence is impossible)"
                sid p.H.pid
          | R_var _ -> ()
          | R_elem e -> (
              match elem_ref_mismatch env p.H.scope e with
              | None -> ()
              | Some w ->
                  bad "invariant 8: proc(%d) %s: %s" p.H.pid
                    (if e.write then "designates" else "reads") w))
        (List.fold_left walk_stmt [] p.H.body))
    prog.H.procs

(* ---------- the shared argument-designator comparison (I11, §P1-a2.6) ----------

   A REFERENCE actual must pass the same soundness law as an in-body variable
   reference: the base resolves from the CALLER's scope back to its own sid
   ([var_mismatch], the I2 comparison verbatim) and its env symbol carries NO
   array record — a whole array can never be a designator (the E15 refusal of
   hir_build makes that impossible; this pins the impossibility). An element
   designator runs the I8 comparison ([elem_ref_mismatch]) with the actual's
   recorded formal type as the node type. A VALUE actual carries no
   designator. --corrupt-actual-base runs THIS code. *)
let designator_mismatch (env : SE.t) (scope : int) (a : H.actual) :
    string option =
  let f = string_of_int in
  match a.H.af with
  | H.A_value _ -> None
  | H.A_reference (H.D_var { sid }) -> (
      match var_mismatch env scope sid with
      | Some w -> Some w
      | None -> (
          match SE.symbol env sid with
          | Some s when s.SE.e_array <> None ->
              Some ("whole-array designator sym(" ^ f sid ^ ") (" ^ s.SE.ekey
                ^ ") is impossible (E15 refuses it)")
          | _ -> None))
  | H.A_reference (H.D_elem { base; _ }) ->
      (* write = false: a reference actual is a READ at the argument position
         (the callee's writes are its own references — the walk law). The
         actual's recorded formal type is the node type the I8 comparison
         judges against the env element projection (§P1-a2.4: E17 makes them
         equal by construction; this pins it). *)
      elem_ref_mismatch env scope
        { base; write = false; ety = Some a.H.ac_ty }

(* 9. bound preservation (§P1-a1.7 I9): every block's projected array bounds
   equal the live Bind.bind_arrays records for that block with the physical
   element width DROPPED at the read — a 3-tuple comparison, so an esz leak
   into the env would move the comparison itself (T5/T6 law). The comparison is
   a shared function so --corrupt-array-hi runs THE SAME CODE. *)
let block_arrays_bind (b : SE.block_env) : (string * int * int) list =
  List.sort compare
    (List.map
       (fun (nm, lb, ub, _physical) -> (nm, lb, ub))
       (Bind.bind_arrays b.SE.east))

let block_arrays_env (b : SE.block_env) : (string * int * int) list =
  List.sort compare
    (List.filter_map
       (fun (_k, (s : SE.symbol)) ->
         match s.SE.e_array with
         | Some a -> Some (s.SE.ekey, a.SE.a_lo, a.SE.a_hi)
         | None -> None)
       b.SE.esyms)

let bounds_mismatch (want : (string * int * int) list)
    (got : (string * int * int) list) : string option =
  let show l =
    String.concat "; "
      (List.map
         (fun (n, lo, hi) -> Printf.sprintf "%s[%d:%d]" n lo hi)
         l)
  in
  if want = got then None
  else Some ("bind records [" ^ show want ^ "], env projects [" ^ show got ^ "]")

let i9 env =
  List.iter
    (fun (b : SE.block_env) ->
      match bounds_mismatch (block_arrays_bind b) (block_arrays_env b) with
      | None -> ()
      | Some w -> bad "invariant 9: proc(%d): %s" b.SE.epid w)
    (SE.blocks env)

(* 10. projection completeness (§P1-a1.7 I10): every bind array record of every
   block lands as [Some e_array] on the env symbol with the matching key (never
   a silent drop), its bounds equal the record's, and the env symbol HAS a
   Hir.sym projection whose type is Array1. *)
let i10 env prog =
  List.iter
    (fun (b : SE.block_env) ->
      List.iter
        (fun (nm, lb, ub, _physical) ->
          match
            List.find_opt
              (fun (_k, (s : SE.symbol)) -> String.equal s.SE.ekey nm)
              b.SE.esyms
          with
          | None ->
              bad "invariant 10: bind array record %s of proc(%d) has no env \
                   symbol with that key"
                nm b.SE.epid
          | Some (_k, s) ->
              (match s.SE.e_array with
               | None ->
                   bad "invariant 10: env symbol %s (proc %d) dropped its array \
                        record"
                     nm b.SE.epid
               | Some a ->
                   if a.SE.a_lo <> lb || a.SE.a_hi <> ub then
                     bad "invariant 10: env symbol %s bounds [%d:%d] differ from \
                          the bind record [%d:%d]"
                       nm a.SE.a_lo a.SE.a_hi lb ub);
              (match List.find_opt (fun (hs : H.sym) -> hs.H.sid = s.SE.esid) prog.H.syms with
               | Some hs -> (
                   match hs.H.sty with
                   | H.Array1 _ -> ()
                   | _ ->
                       bad "invariant 10: array sym(%d) (%s) is not projected as \
                            Array1"
                         s.SE.esid nm)
               | None ->
                   bad "invariant 10: array sym(%d) (%s) has no Hir projection"
                     s.SE.esid nm))
        (Bind.bind_arrays b.SE.east))
    (SE.blocks env)

(* 11. argument-designator soundness (§P1-a2.6 I11): every REFERENCE actual of
   every COLLECTED call passes the shared designator comparison judged from the
   OWNER's scope. Value actuals carry no designator; their internal soundness is
   the expression walk's job (I2/I8 through the existing item counts). *)
let i11 env prog calls =
  List.iter
    (fun (ci : call_item) ->
      match
        List.find_opt
          (fun (q : H.proc) -> q.H.pid = ci.ci_owner_pid)
          prog.H.procs
      with
      | None ->
          bad "invariant 11: collected call owner pid %d is not a Hir proc"
            ci.ci_owner_pid
      | Some _ ->
          List.iteri
            (fun i a ->
              match a.H.af with
              | H.A_value _ -> ()
              | H.A_reference _ -> (
                  match designator_mismatch env ci.ci_owner_scope a with
                  | None -> ()
                  | Some w ->
                      bad "invariant 11: proc(%d) call to %s argument %d: %s"
                        ci.ci_owner_pid ci.ci_key i w))
            ci.ci_args)
    calls

(* 12. passing-evidence alignment (§P1-a2.6 I12): every walked call that has
   AST argument nodes answers [SE.call_evidence] with [Some] — the physical
   identity matching law — and the shared comparison judges the recorded modes.
   [ci_ast_args = None] is the recorded EXCLUSION arm: the zero-argument
   identifier statement route lays NO bind site (§P1-a2.5) and no positive
   fixture takes that route (recorded honestly, never silently trusted). *)
let i12 env calls =
  List.iter
    (fun (ci : call_item) ->
      match ci.ci_ast_args with
      | None -> () (* Eident zero-arg exclusion: no recorded site to demand *)
      | Some ast -> (
          match
            SE.call_evidence env ~caller_scope:ci.ci_owner_scope
              ~callee_key:ci.ci_key ast
          with
          | None ->
              bad "invariant 12: no bind call-site evidence matches the call to \
                   %s from proc(%d) (identity matching law)"
                ci.ci_key ci.ci_owner_pid
          | Some ce -> (
              match arg_evidence_mismatch env ci ce with
              | None -> ()
              | Some w -> bad "invariant 12: %s" w)))
    calls

(* 13. formal-API alignment (§P1-a2.6 I13): every Hir proc's projected formal
   sids agree position by position with the env's OWN formal descriptions —
   identity, position, key and type judged against bind/env, never dump text.
   DEVIATION recorded (§P1-a2.6 wording "every HIR proc"): the outer block of a
   MAIN program carries NO bind proc_layout record by env law (i4/i5 tolerate
   [None] exactly when the proc projects zero params — the same law applies
   here); a [None] answer WITH params, or for any registered procedure, is
   still the loud violation the plan named. *)
let i13 env prog =
  List.iter
    (fun (p : H.proc) ->
      match SE.formals_of env p.H.pid with
      | None ->
          if p.H.params <> [] then
            bad "invariant 13: formals_of answered None for proc(%d) with %d \
                 projected params — bind laid no record"
              p.H.pid (List.length p.H.params)
      | Some fs -> (
          match formals_mismatch env p fs with
          | None -> ()
          | Some w -> bad "invariant 13: %s" w))
    prog.H.procs

(* 3. declaration order: every block's esyms are in bind row order; sids
   ascend in the documented pre-order (blocks pid-ascending, rows per block in
   bind order). *)
let i3 env =
  List.iter
    (fun (b : SE.block_env) ->
      let raw =
        List.map (fun (nm, _rt, _placement, _auto) -> nm) (Bind.bind_rows b.SE.east)
      in
      let got = List.map fst b.SE.esyms in
      if raw <> got then
        bad "invariant 3: block pid(%d) env rows are not in bind row order"
          b.SE.epid)
    (SE.blocks env);
  let rec go next = function
    | [] -> ()
    | s :: tl ->
        if s.SE.esid <> next then
          bad "invariant 3: pre-order expects sid %d, env gives %d" next s.SE.esid;
        go (next + 1) tl
  in
  go 0 (env_rows env)

(* 4. procedure/formal relationship: Hir.proc.params equals the sids of the
   block's formal set resolved in the proc's OWN scope, in bind pl_ptrs order;
   every such symbol carries the formal storage flag. *)
let i4 env prog =
  List.iter
    (fun (b : SE.block_env) ->
      match List.find_opt (fun (q : H.proc) -> q.H.pid = b.SE.epid) prog.H.procs with
      | None -> bad "invariant 4: env block pid(%d) has no Hir proc" b.SE.epid
      | Some q -> (
          match b.SE.esig with
          | Some sg ->
              let expect =
                List.map
                  (fun nm ->
                    match SE.resolve env b.SE.escope nm with
                    | Some s -> Some s.SE.esid
                    | None -> None)
                  sg.SE.sptrs
              in
              let got = List.map (fun sid -> Some sid) q.H.params in
              if expect <> got then
                bad "invariant 4: proc(%d) params are not the bind formal-cell sids \
                     in pl_ptrs order" b.SE.epid;
              List.iter
                (fun sid ->
                  match SE.symbol env sid with
                  | Some s when s.SE.estorage = SE.S_formal -> ()
                  | Some s ->
                      bad "invariant 4: formal sid %d (%s) lacks the formal storage flag"
                        sid s.SE.ekey
                  | None -> bad "invariant 4: param sid %d is unknown to the env" sid)
                q.H.params
          | None ->
              if q.H.params <> [] then
                bad "invariant 4: proc(%d) has params but bind laid no signature"
                  b.SE.epid))
    (SE.blocks env)

(* 5. return type: the env signature's sret equals type_of_rt of bind's own
   pl_ret, the rendering agreement (sret_pr = Bind.rty_str) is checked against
   raw bind, and the Hir proc ret is the gate image of that same fact. *)
let i5 env plan prog =
  List.iter
    (fun (b : SE.block_env) ->
      let raw =
        match b.SE.ekey with
        | Some k ->
            List.find_opt
              (fun (pl : Bind.proc_layout) -> String.equal pl.Bind.pl_name k)
              plan.Bind.pl_procs
        | None -> None
      in
      match (b.SE.esig, raw) with
      | Some sg, Some pl ->
          if sg.SE.sret <> Option.map SE.type_of_rt pl.Bind.pl_ret then
            bad "invariant 5: proc(%d) signature ret is not type_of_rt of bind's \
                 pl_ret" b.SE.epid;
          if sg.SE.sret_pr <> Option.map Bind.rty_str pl.Bind.pl_ret then
            bad "invariant 5: proc(%d) ret rendering is not bind's own wording"
              b.SE.epid;
          (match List.find_opt (fun (q : H.proc) -> q.H.pid = b.SE.epid) prog.H.procs with
          | Some q ->
              let want =
                match sg.SE.sret with
                | Some (SE.SFixed_bin p) -> Some (H.Fixed_bin (p, 0))
                | Some _ -> None (* outside the gate: build refuses first *)
                | None -> None
              in
              if q.H.ret <> want then
                bad "invariant 5: proc(%d) Hir ret is not the gate image of the \
                     bind returns fact" b.SE.epid
          | None -> ())
      | Some _, None ->
          bad "invariant 5: env sig for proc(%d) has no bind layout behind it"
            b.SE.epid
      | None, Some _ ->
          bad "invariant 5: bind lays out proc(%d) but the env projected no signature"
            b.SE.epid
      | None, None -> ())
    (SE.blocks env)

(* 6. parent/child: every env block's eparent/enclosing matches the AST nesting
   of the fixture, re-read from the parsed syntax itself (physical block
   identity), never from a string. *)
let rec ast_nesting parent acc (stmts : Ast.stmt list) =
  List.fold_left
    (fun a (s : Ast.stmt) ->
      match s.Ast.st with
      | Ast.Sproc bs ->
          let b = bs.Ast.blk in
          if b.Ast.bkind = Ast.Bproc then
            ast_nesting b ((b, parent) :: a) b.Ast.bstmts
          else
            (* BEGIN/DO carry no separate scope: procedures discovered inside
               them belong to the SAME parent block. (Measured note, RESULTS
               §P1-b: the live env hangs on this shape — a defect PRE-EXISTING
               at aaf295f0; no positive fixture contains a bare BEGIN/DO block,
               so this arm never runs for them.) *)
            ast_nesting parent a b.Ast.bstmts
      | _ -> a)
    acc stmts

let i6 env blk =
  let pairs = List.rev (ast_nesting blk [] blk.Ast.bstmts) in
  let blocks = SE.blocks env in
  if List.length blocks <> List.length pairs + 1 then
    bad "invariant 6: %d env blocks for %d AST-nested procedures (main is the extra)"
      (List.length blocks) (List.length pairs);
  let main = SE.main_block env in
  if main.SE.epid <> 0 || main.SE.eparent <> None then
    bad "invariant 6: main block is not pid 0 with no parent scope";
  if not (main.SE.east == blk) then
    bad "invariant 6: env main block is not the parsed AST root";
  (match SE.enclosing env 0 with
  | None -> ()
  | Some _ -> bad "invariant 6: main pid claims an enclosing procedure");
  List.iter
    (fun (child, parent) ->
      let cb = List.find_opt (fun (b : SE.block_env) -> b.SE.east == child) blocks in
      let pb = List.find_opt (fun (b : SE.block_env) -> b.SE.east == parent) blocks in
      match (cb, pb) with
      | Some cb, Some pb ->
          if cb.SE.eparent <> Some pb.SE.escope then
            bad "invariant 6: proc(%d) eparent is not the enclosing block's scope"
              cb.SE.epid;
          if cb.SE.epid <= pb.SE.epid then
            bad "invariant 6: pre-order broken — proc(%d) numbered at or below its \
                 parent" cb.SE.epid;
          (match SE.enclosing env cb.SE.epid with
          | Some e ->
              if e <> pb.SE.epid then
                bad "invariant 6: enclosing(%d) answers %d, the AST says %d"
                  cb.SE.epid e pb.SE.epid
          | None -> bad "invariant 6: proc(%d) claims no enclosing pid" cb.SE.epid)
      | _ -> bad "invariant 6: an AST-nested procedure has no env block for it")
    pairs

(* 7. every Call_e/Call_s pid has a bind signature whose arity (pl_ptrs cell
   count) equals the argument count — never a re-derived signature. *)
let i7 env prog =
  List.iter
    (fun (p : H.proc) ->
      List.iter
        (fun r ->
          match r with
          | R_var _ | R_elem _ -> ()
          | R_call { pid; nargs } ->
              match (try Some (SE.signature env pid) with SE.Not_found _ -> None) with
              | Some (Some sg) ->
                  if sg.SE.sptr_count <> nargs then
                    bad "invariant 7: call to proc(%d) passes %d arguments to %d \
                         bind cells" pid nargs sg.SE.sptr_count
              | Some None ->
                  bad "invariant 7: call target proc(%d) carries no bind signature"
                    pid
              | None ->
                  bad "invariant 7: call target pid %d is not a registered block"
                    pid)
        (List.fold_left walk_stmt [] p.H.body))
    prog.H.procs

(* ---------- corrupt controls ---------- *)

let nothing_proven what =
  prerr_endline
    ("SEM-FAIL: corrupt control had " ^ what ^ " to perturb \
      (nothing was proven)");
  exit 1

let corrupt_probe env prog =
  match prog.H.syms with
  | [] ->
      prerr_endline
        "SEM-FAIL: corrupt control had no symbols to query (nothing was proven)";
      exit 1
  | hd :: _ ->
      let wrong = { hd with H.sid = hd.H.sid + 1000 } in
      match sym_mismatch env wrong with
      | Some why ->
          prerr_endline
            ("SEM-FAIL: [corrupt control] deliberately wrong sid rejected as it \
              must: " ^ why);
          exit 1
      | None ->
          prerr_endline
            "SEM-FAIL: corrupt control ACCEPTED a wrong sid — the check is vacuous";
          exit 1

(* Perturb one projected a_hi by +1 and re-run the I9 comparison; it must
   reject (§P1-a1.7: THE SAME comparison, never a copy). A fixture with no array
   symbol prints nothing-was-proven rather than passing vacuously. *)
let corrupt_hi env =
  match
    List.find_map
      (fun (b : SE.block_env) ->
        match block_arrays_env b with
        | [] -> None
        | (n, lo, hi) :: rest ->
            Some (b.SE.epid, block_arrays_bind b, (n, lo, hi + 1) :: rest))
      (SE.blocks env)
  with
  | None ->
      nothing_proven "no array bounds"
  | Some (pid, bind_side, perturbed) -> (
      match bounds_mismatch bind_side perturbed with
      | Some why ->
          prerr_endline
            ("SEM-FAIL: [corrupt control] perturbed a_hi on proc(" ^ string_of_int pid
            ^ ") rejected as it must: " ^ why);
          exit 1
      | None ->
          prerr_endline
            "SEM-FAIL: corrupt control ACCEPTED a perturbed a_hi — the check is \
              vacuous";
          exit 1)

(* Repoint one element reference's base at a NON-array sid and re-run the I8
   per-reference comparison; it must reject. H05 (one array sym, no scalar) and
   array-free fixtures print nothing-was-proven. *)
let corrupt_base env prog =
  let refs =
    List.concat_map
      (fun (p : H.proc) ->
        List.filter_map
          (fun r -> match r with R_elem e -> Some (p, e) | _ -> None)
          (List.fold_left walk_stmt [] p.H.body))
      prog.H.procs
  in
  let non_arrays =
    List.filter_map
      (fun (s : H.sym) ->
        match s.H.sty with H.Array1 _ -> None | _ -> Some s.H.sid)
      prog.H.syms
  in
  match (refs, non_arrays) with
  | ([], _) | (_, []) ->
      nothing_proven
        (if refs = [] then "no element reference" else "no non-array symbol")
  | ((p, r) :: _, sid :: _) -> (
      match elem_ref_mismatch env p.H.scope { r with base = sid } with
      | Some why ->
          prerr_endline
            ("SEM-FAIL: [corrupt control] element base sym(" ^ string_of_int r.base
            ^ ") repointed at sym(" ^ string_of_int sid ^ ") in proc(" ^ string_of_int p.H.pid
            ^ ") rejected as it must: " ^ why);
          exit 1
      | None ->
          prerr_endline
            "SEM-FAIL: corrupt control ACCEPTED a non-array element base — the \
              check is vacuous";
          exit 1)

(* Perturb one recorded formal's identity — shift the FIRST [f_sid] by +1000 —
   and re-run THE SAME I13 comparison (§P1-a2.6: wrong formal IDENTITY). A
   fixture with no formal carrying an identity prints nothing-was-proven. *)
let corrupt_formal env prog =
  let f = string_of_int in
  match
    List.find_map
      (fun (p : H.proc) ->
        match SE.formals_of env p.H.pid with
        | Some (fd :: _ as fs) -> (
            match fd.SE.f_sid with
            | Some sid0 -> Some (p, fs, sid0)
            | None -> None)
        | _ -> None)
      prog.H.procs
  with
  | None -> nothing_proven "no recorded formal identity"
  | Some (p, fs, sid0) -> (
      let perturbed =
        List.mapi
          (fun i fd ->
            if i = 0 then { fd with SE.f_sid = Some (sid0 + 1000) } else fd)
          fs
      in
      match formals_mismatch env p perturbed with
      | Some why ->
          prerr_endline
            ("SEM-FAIL: [corrupt control] formal sid shifted by +1000 on proc("
            ^ f p.H.pid ^ ") rejected as it must: " ^ why);
          exit 1
      | None ->
          prerr_endline
            "SEM-FAIL: corrupt control ACCEPTED a shifted formal sid — the check \
              is vacuous";
          exit 1)

(* Repoint one argument designator's sid and re-run THE SAME I11 comparison
   (§P1-a2.6: wrong ACTUAL base). KEY LAW (hop 9, measured): repointing among
   symbols the CALLER scope CAN resolve is an I2-legal alias, never a bug —
   the candidate is the first projected sym whose key the caller scope does NOT
   resolve back to it (foreign or shadowed spelling). *)
let corrupt_actual env prog calls =
  let f = string_of_int in
  let hit =
    List.find_map
      (fun (ci : call_item) ->
        match ci.ci_ast_args with
        | None -> None
        | Some _ ->
            List.find_map
              (fun (a : H.actual) ->
                match a.H.af with
                | H.A_reference (H.D_var { sid }) -> Some (ci, a, sid)
                | H.A_reference (H.D_elem { base; _ }) -> Some (ci, a, base)
                | H.A_value _ -> None)
              ci.ci_args)
      calls
  in
  match hit with
  | None -> nothing_proven "no reference actual"
  | Some (ci, a, orig) ->
      (* the first projected sym the CALLER scope cannot resolve back to it —
         a VISIBLE alias would pass I2 and prove nothing (hop-9 key law) *)
      let candidate =
        List.find_opt
          (fun (hs : H.sym) ->
            match SE.resolve env ci.ci_owner_scope hs.H.skey with
            | Some s -> s.SE.esid <> hs.H.sid
            | None -> true)
          prog.H.syms
      in
      match candidate with
      | None -> nothing_proven "no caller-invisible symbol"
      | Some (cand : H.sym) -> (
          let perturbed =
            match a.H.af with
            | H.A_reference (H.D_var _) ->
                { a with
                  H.af = H.A_reference (H.D_var { sid = cand.H.sid }) }
            | H.A_reference (H.D_elem { subs; _ }) ->
                { a with
                  H.af =
                    H.A_reference (H.D_elem { base = cand.H.sid; subs }) }
            | H.A_value _ -> a
          in
          match designator_mismatch env ci.ci_owner_scope perturbed with
          | Some why ->
              prerr_endline
                ("SEM-FAIL: [corrupt control] argument designator of call to "
                ^ ci.ci_key ^ " repointed sym(" ^ f orig ^ ")->sym("
                ^ f cand.H.sid ^ ") rejected as it must: " ^ why);
              exit 1
          | None ->
              prerr_endline
                "SEM-FAIL: corrupt control ACCEPTED a repointed argument \
                  designator — the check is vacuous";
              exit 1)

(* Drop the FIRST recorded position of one call's evidence and re-run THE SAME
   I12 comparison (§P1-a2.6, "drop one ce_args position"). ADJUDICATED
   DEVIATION: the pre-registration offered an OR (drop, or swap two positions);
   only the DROP arm is implemented — the swap would exercise the identical
   positional comparison one step further and the drop already moves the whole
   list out of alignment; recorded honestly, never quietly narrowed. *)
let corrupt_argpos env calls =
  let hit =
    List.find_map
      (fun (ci : call_item) ->
        match ci.ci_ast_args with
        | None -> None
        | Some ast -> (
            match
              SE.call_evidence env ~caller_scope:ci.ci_owner_scope
                ~callee_key:ci.ci_key ast
            with
            | Some ({ SE.ce_args = _ :: _; _ } as ce) -> Some (ci, ce)
            | _ -> None))
      calls
  in
  match hit with
  | None -> nothing_proven "no multi-position evidence list"
  | Some (ci, ce) -> (
      match
        arg_evidence_mismatch env ci { ce with SE.ce_args = List.tl ce.SE.ce_args }
      with
      | Some why ->
          prerr_endline
            ("SEM-FAIL: [corrupt control] first evidence position dropped on the \
              call to " ^ ci.ci_key ^ " rejected as it must: " ^ why);
          exit 1
      | None ->
          prerr_endline
            "SEM-FAIL: corrupt control ACCEPTED a dropped evidence position — \
              the check is vacuous";
          exit 1)

(* Flip one own/value-cell passing mode of one call and re-run THE SAME I12
   comparison (§P1-a2.6: wrong PASSING REQUIREMENT). *)
let corrupt_mode_flip env calls =
  let rec find_at i = function
    | [] -> None
    | pm :: rest ->
        (match pm with
        | SE.PM_own_cell -> Some (i, SE.PM_value_cell)
        | SE.PM_value_cell -> Some (i, SE.PM_own_cell)
        | _ -> find_at (i + 1) rest)
  in
  let hit =
    List.find_map
      (fun (ci : call_item) ->
        match ci.ci_ast_args with
        | None -> None
        | Some ast -> (
            match
              SE.call_evidence env ~caller_scope:ci.ci_owner_scope
                ~callee_key:ci.ci_key ast
            with
            | Some ce -> (
                match find_at 0 ce.SE.ce_args with
                | None -> None
                | Some (i, flipped) ->
                    Some
                      ( ci,
                        { ce with
                          SE.ce_args =
                            List.mapi
                              (fun j pm -> if j = i then flipped else pm)
                              ce.SE.ce_args } ) )
            | None -> None))
      calls
  in
  match hit with
  | None -> nothing_proven "no own/value-cell passing mode"
  | Some (ci, ce) -> (
      match arg_evidence_mismatch env ci ce with
      | Some why ->
          prerr_endline
            ("SEM-FAIL: [corrupt control] passing mode flipped on the call to "
            ^ ci.ci_key ^ " rejected as it must: " ^ why);
          exit 1
      | None ->
          prerr_endline
            "SEM-FAIL: corrupt control ACCEPTED a flipped passing mode — the \
              check is vacuous";
          exit 1)

(* ---------- driver ---------- *)

let () =
  let args = List.tl (Array.to_list Sys.argv) in
  let mode, src =
    match args with
    | [ "--corrupt"; s ] -> (Corrupt, s)
    | [ "--corrupt-array-hi"; s ] -> (Corrupt_hi, s)
    | [ "--corrupt-array-base"; s ] -> (Corrupt_base, s)
    | [ "--corrupt-formal"; s ] -> (Corrupt_formal, s)
    | [ "--corrupt-actual-base"; s ] -> (Corrupt_actual, s)
    | [ "--corrupt-arg-position"; s ] -> (Corrupt_argpos, s)
    | [ "--corrupt-mode"; s ] -> (Corrupt_mode, s)
    | [ s ] -> (Live, s)
    | _ ->
        prerr_endline
          "usage: semtest [--corrupt|--corrupt-array-hi|--corrupt-array-base \
            |--corrupt-formal|--corrupt-actual-base|--corrupt-arg-position \
            |--corrupt-mode] FIXTURE.PLI";
        exit 2
  in
  let text =
    try In_channel.with_open_bin src In_channel.input_all
    with Sys_error msg -> die_early ("cannot read input: " ^ msg)
  in
  (* same CP/M EOF convention as the CLI: everything from the first ^Z is padding. *)
  let text =
    match String.index_opt text '\026' with
    | Some i -> String.sub text 0 i
    | None -> text
  in
  let blk =
    try Pli80.Parser.parse_source text
    with Failure msg -> die_early ("front end (lexer/parser) failed: " ^ msg)
  in
  let plan =
    try Bind.bind_program blk
    with Failure msg -> die_early ("bind (semantic authority) refused: " ^ msg)
  in
  let env =
    match SE.create blk plan with
    | Ok e -> e
    | Error ds -> die_early ("Semantic_env.create refused: " ^ show ds)
  in
  let profile = Pli80_hir.Target.dr_pli80_v1_4 in
  let prog =
    match HB.build blk profile with
    | Ok p -> p
    | Error ds -> die_early ("Hir_build.build refused: " ^ show ds)
  in
  (* the §P1-a2.6 collection walk FIRST: any AST<->HIR pairing disagreement is
     LOUD before any invariant (or OK line) can be claimed. *)
  let calls = collect_calls env prog in
  i1 env prog;
  i2 env prog;
  i3 env;
  i4 env prog;
  i5 env plan prog;
  i6 env blk;
  i7 env prog;
  i8 env prog;
  i9 env;
  i10 env prog;
  i11 env prog calls;
  i12 env calls;
  i13 env prog;
  if !fails <> [] then begin
    List.iter (fun m -> prerr_endline ("SEM-FAIL: " ^ m)) (List.rev !fails);
    exit 1
  end;
  (match mode with
  | Live -> ()
  | Corrupt -> corrupt_probe env prog
  | Corrupt_hi -> corrupt_hi env
  | Corrupt_base -> corrupt_base env prog
  | Corrupt_formal -> corrupt_formal env prog
  | Corrupt_actual -> corrupt_actual env prog calls
  | Corrupt_argpos -> corrupt_argpos env calls
  | Corrupt_mode -> corrupt_mode_flip env calls);
  let nrefs =
    List.fold_left
      (fun n (p : H.proc) -> n + List.length (List.fold_left walk_stmt [] p.H.body))
      0 prog.H.procs
  in
  Printf.printf "SEMANTIC-AUTHORITY OK %d refs / %d syms\n" nrefs
    (List.length prog.H.syms);
  exit 0
