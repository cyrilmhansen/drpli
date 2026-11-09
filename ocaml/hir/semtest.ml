(* hir/semtest.ml — semantic-authority test binary (E2E-54/P1-b, PLAN §P1-b.4).

   This tool judges the HIR build path against the LIVE environment: it parses a
   positive fixture, builds the [Semantic_env] projection over bind's own plan,
   lowers the same program through [Hir_build.build], and asserts the ten
   pre-registered invariants (I1-I7 from §P1-b.4, I8-I10 from §P1-a1.7) that
   every semantic-carrying [Hir] field equals the bind-fact projection it claims
   to project. Dump text is never consulted — a check must fail even if the CLI
   printer is broken (falsifier S6).

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

   This is an executable in ocaml/hir/ (never ocaml/bin/ — the P0 F1 exe-dir
   law: a stanza in the hir directory does not move pli80c.exe; S1 re-checked
   after adding it). It links [pli80] + [pli80_hir] only. Reading bind's raw
   layout here (bind_rows, proc_layout) is intentional: a TEST must judge the
   env against its authority, not against itself; the S5 one-reader law binds
   the compiler path (hir_build/semantic_env), not this binary. *)

module Ast = Pli80.Ast
module Bind = Pli80.Bind
module D = Pli80_hir.Diagnostic
module H = Pli80_hir.Hir
module HB = Pli80_hir.Hir_build
module SE = Pli80_hir.Semantic_env

(* ---------- failure accumulation ---------- *)

type mode = Live | Corrupt | Corrupt_hi | Corrupt_base

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
              match SE.symbol env sid with
              | None ->
                  bad "invariant 2: proc(%d) reads sym(%d) the env does not know"
                    p.H.pid sid
              | Some s -> (
                  match
                    (try SE.resolve env p.H.scope s.SE.ekey
                     with SE.Not_found _ -> None)
                  with
                  | Some found when found.SE.esid = sid -> ()
                  | Some found ->
                      bad "invariant 2: name %s resolves from scope %d to sym(%d), \
                           not the sym(%d) this reference was lowered to"
                        s.SE.ekey p.H.scope found.SE.esid sid
                  | None ->
                      bad "invariant 2: name %s resolves from scope %d to nothing"
                        s.SE.ekey p.H.scope))
          )
        (List.fold_left walk_stmt [] p.H.body))
    prog.H.procs

(* 8. reference soundness (§P1-a1.7 I8): every element read/designation has a
   base that resolves (from the REFERRING procedure's scope, shadowing included)
   to an env symbol WITH an array record, and the node's type equals the env
   element projection (mapped exactly as I1 maps it). No Var node ever carries
   an [Array1] type — a whole-array value reference is unrepresentable and any
   one that appeared would be the silent-collapse defect this guards. The
   per-reference comparison is a shared function so --corrupt-array-base runs
   THE SAME CODE as the invariant, never a copy. *)
let elem_ref_mismatch env (p : H.proc) (r : elem_ref) : string option =
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
            (try SE.resolve env p.H.scope s.SE.ekey with SE.Not_found _ -> None)
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
                ^ f p.H.scope ^ " resolves for " ^ s.SE.ekey ^ " (shadowing?)")
          | None ->
              Some ("element base name " ^ s.SE.ekey ^ " resolves from scope "
                ^ f p.H.scope ^ " to nothing")))

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
              match elem_ref_mismatch env p e with
              | None -> ()
              | Some w ->
                  bad "invariant 8: proc(%d) %s: %s" p.H.pid
                    (if e.write then "designates" else "reads") w))
        (List.fold_left walk_stmt [] p.H.body))
    prog.H.procs

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
      match elem_ref_mismatch env p { r with base = sid } with
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

(* ---------- driver ---------- *)

let () =
  let args = List.tl (Array.to_list Sys.argv) in
  let mode, src =
    match args with
    | [ "--corrupt"; s ] -> (Corrupt, s)
    | [ "--corrupt-array-hi"; s ] -> (Corrupt_hi, s)
    | [ "--corrupt-array-base"; s ] -> (Corrupt_base, s)
    | [ s ] -> (Live, s)
    | _ ->
        prerr_endline
          "usage: semtest [--corrupt|--corrupt-array-hi|--corrupt-array-base] \
            FIXTURE.PLI";
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
  if !fails <> [] then begin
    List.iter (fun m -> prerr_endline ("SEM-FAIL: " ^ m)) (List.rev !fails);
    exit 1
  end;
  (match mode with
  | Live -> ()
  | Corrupt -> corrupt_probe env prog
  | Corrupt_hi -> corrupt_hi env
  | Corrupt_base -> corrupt_base env prog);
  let nrefs =
    List.fold_left
      (fun n (p : H.proc) -> n + List.length (List.fold_left walk_stmt [] p.H.body))
      0 prog.H.procs
  in
  Printf.printf "SEMANTIC-AUTHORITY OK %d refs / %d syms\n" nrefs
    (List.length prog.H.syms);
  exit 0
