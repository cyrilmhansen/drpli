(* hir/semtest.ml — semantic-authority test binary (E2E-54/P1-b, PLAN §P1-b.4).

   This tool judges the HIR build path against the LIVE environment: it parses a
   positive fixture, builds the [Semantic_env] projection over bind's own plan,
   lowers the same program through [Hir_build.build], and asserts the seven
   pre-registered invariants (I1-I7 below) that every semantic-carrying [Hir]
   field equals the bind-fact projection it claims to project. Dump text is
   never consulted — a check must fail even if the CLI printer is broken
   (falsifier S6).

   Output contract (§P1-b.4):
     every invariant holds  -> stdout gets EXACTLY one line
        SEMANTIC-AUTHORITY OK <n> refs / <m> syms        rc 0
     any invariant violated -> `SEM-FAIL ...' lines on stderr, rc 1, ZERO stdout
   refs counts the Var references (I2) plus call sites (I7) checked across all
   procedure bodies; syms is the number of projected Hir symbols (I1).

   [--corrupt] control: the FIRST projected symbol is run through the very same
   field-comparison used by I1 with a deliberately wrong sid. The comparison
   must reject it — a control that cannot reject is itself a SEM-FAIL (the tool
   proves non-vacuity, S6). This mode NEVER prints the OK line.

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

type mode = Live | Corrupt

let fails : string list ref = ref []
let bad fmt = Printf.ksprintf (fun s -> fails := s :: !fails) fmt

let die_early msg =
  (* parse/env/build blowups: SEM-FAIL, rc 1, zero stdout — the tool itself
     refuses loudly rather than silently claiming authority. *)
  prerr_endline ("SEM-FAIL: " ^ msg);
  exit 1

let show ds = String.concat " / " (List.map D.pp ds)

(* ---------- shared traversal ---------- *)

type ref_item =
  | R_var of int
  | R_call of { pid : int; nargs : int }

let rec walk_expr acc (e : H.expr) : ref_item list =
  match e.H.ex with
  | H.Const _ -> acc
  | H.Var { sid; _ } -> R_var sid :: acc
  | H.Bin { left; right; _ } -> walk_expr (walk_expr acc right) left
  | H.Neg { e = inner } -> walk_expr acc inner
  | H.Convert { e = inner; _ } -> walk_expr acc inner
  | H.Call_e { pid; args } ->
      List.fold_left walk_expr (R_call { pid; nargs = List.length args } :: acc) args

let rec walk_stmt acc (s : H.stmt) : ref_item list =
  match s.H.st with
  | H.Declare _ | H.Stop -> acc
  | H.Assign { target; value } -> walk_expr (walk_expr acc target) value
  | H.If { cond; then_; else_ } ->
      List.fold_left walk_stmt
        (List.fold_left walk_stmt (walk_expr acc cond) then_)
        else_
  | H.While { cond; body } -> List.fold_left walk_stmt (walk_expr acc cond) body
  | H.Call_s { pid; args } ->
      List.fold_left walk_expr (R_call { pid; nargs = List.length args } :: acc) args
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
          match s.SE.ety with
          | SE.SFixed_bin p when hs.H.sty = H.Fixed_bin (p, 0) -> None
          | SE.SFixed_bin p ->
              Some ("type differs for " ^ s.SE.ekey ^ " (env bin(" ^ f p ^ "))")
          | _ ->
              Some ("env symbol " ^ s.SE.ekey
                ^ " is outside the subset gate; no sym may project it")
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
          | R_call _ -> ()
          | R_var sid -> (
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
          | R_var _ -> ()
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

(* ---------- corrupt control ---------- *)

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

(* ---------- driver ---------- *)

let () =
  let args = List.tl (Array.to_list Sys.argv) in
  let mode, src =
    match args with
    | [ "--corrupt"; s ] -> (Corrupt, s)
    | [ s ] -> (Live, s)
    | _ ->
        prerr_endline "usage: semtest [--corrupt] FIXTURE.PLI";
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
  if !fails <> [] then begin
    List.iter (fun m -> prerr_endline ("SEM-FAIL: " ^ m)) (List.rev !fails);
    exit 1
  end;
  if mode = Corrupt then corrupt_probe env prog;
  let nrefs =
    List.fold_left
      (fun n (p : H.proc) -> n + List.length (List.fold_left walk_stmt [] p.H.body))
      0 prog.H.procs
  in
  Printf.printf "SEMANTIC-AUTHORITY OK %d refs / %d syms\n" nrefs
    (List.length prog.H.syms);
  exit 0
