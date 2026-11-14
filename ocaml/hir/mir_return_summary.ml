(* ocaml/hir/mir_return_summary.ml — sound interprocedural return-value interval
   summaries for the MIR backend (E2E-54/P2-DIFF-3 §P2-DIFF-3, Stage B).

   WHAT THIS IS.  The backend's lower_call_e (§P1-m3.2-7, I3) gives every value
   call the callee's FULL declared result window W(q).  For a reached
   NONRECURSIVE value procedure whose body is side-effect free and whose
   statements are all inside the backend's own proven grammar, the HIR body
   plus the declared formal windows prove a (possibly) STRICTLY SMALLER
   interval for the returned value.  This module computes that summary.  It is
   ANALYSIS ONLY: it never emits, never diagnoses, never refuses — EVERY
   violation of the subset returns Unknown, and the caller then falls back to
   the existing full-window behaviour byte-for-byte.  Nothing in the accepted
   language changes: the summary can only ADD proofs, never remove them, and an
   Unknown summary is exactly what the backend does today.

   THE SUBSET (the §P2-DIFF-3 pre-registration, verbatim):
     - pid <> 0, a value procedure with ret = Some (Fixed_bin(q,0)), 1 <= q <=
       maxp;
     - every formal is Fixed_bin(p,0), 1 <= p <= maxp, and the env is seeded
       with EXACTLY W(p) (the backend's env0 law, verbatim);
     - the LAST statement of the body is the top-level Return (Some e);
     - no other Return, While, Call_s, Call_e, Get, Put or Stop anywhere in the
       body;
     - Assign targets are D_var of symbols declared in the procedure's OWN
       scope (the declare law: no re-declaration, scope equality, storage
       Auto/Formal, the bin_p precision law — the backend's declare mirrors
       this);
     - the expression grammar mirrors the backend's lower law with the SAME
       window proof via Mir_numeric: Const (a canonical decimal literal inside
       the node's own declared window), Var (declared AND definitely
       initialized), Bin Add/Sub/Mul with operands typed EQUAL to the result
       type, Neg; relational Bin only as an If condition (no interval is
       recorded for it); Convert/Call_e/Elem_read/Elem_ref and any Unknown_ef
       node are outside the grammar;
     - If arms join with the backend's drop-not-inherit law verbatim
       (Mir_numeric.iv_hull on Some/Some; any None side drops the entry; a
       missing ELSE is the identity path);
     - the proven return interval escaping W(q) yields Unknown.

   SOUNDNESS (the §P2-DIFF-3 argument, restated for the implementer): the
   callee is a CLOSED function of its formals and own locals — the backend
   refuses foreign-scope declarations in declare, value calls pass only
   A_value cells, and by-ref actuals are refused at a value call (E18), so no
   caller storage can be written.  The walk is an induction over the statement
   sequence: every env entry is a sound over-approximation of the value on
   every reachable path, the join is the smallest hull covering both sides, and
   every node is window-proved with the SAME endpoint algebra the backend uses
   (the single Mir_numeric implementation).  The returned interval therefore
   satisfies actual_return_values <= inferred <= declared_window for EVERY
   input in the declared formal windows; the caller's defensive re-check
   (in_window (W(q))) is the second half of that inequality.

   DEPENDENCY LAW (§P2-DIFF-3): this module imports ONLY Hir and Mir_numeric.
   No Target, no Diagnostic, no Backend, no emission or mutable instruction
   state, no REF-80/byte-layout vocabulary, no Unix, no open, no exception
   raising, no mutable state.  The precision ceiling maxp is a PARAMETER (the
   backend passes the profile's own ceiling); the type itself is never named
   here, exactly as in Mir_numeric.  The pid -> summary map is an association
   list sorted by pid: a second Map.Make (Int) would be a DISTINCT type from
   the backend's generative Int_map (the MEASURED P2-DIFF-2 constraint), so the
   pure, dependency-free answer is the list.

   This file is in ocaml/hir/ and is covered by the F8 purity glob of
   tools/hir_test.py (the check is code-only, after the nested-comment strip). *)

type summary = Known of (int * int) | Unknown

(* The one accepted integer type, as a PURE function: the backend's bin_p law
   (FIXED BINARY(p,0) with 1 <= p <= maxp) without the diagnostic. *)
let bin_p_of maxp (t : Hir.ty) : int option =
  match t with
  | Hir.Fixed_bin (p, 0) when p >= 1 && p <= maxp -> Some p
  | _ -> None

let find_sym (prog : Hir.program) (sid : int) : Hir.sym option =
  List.find_opt (fun (s : Hir.sym) -> s.Hir.sid = sid) prog.Hir.syms

let find_proc (prog : Hir.program) (pid : int) : Hir.proc option =
  List.find_opt (fun (p : Hir.proc) -> p.Hir.pid = pid) prog.Hir.procs

(* Overwrite-add for the association-list env: the same sid keeps ONE entry
   (the backend's Int_map.add law). *)
let add_env (env : (int * (int * int)) list) (sid : int) (iv : int * int) =
  (sid, iv) :: List.filter (fun (k, _) -> k <> sid) env

(* The backend's join_env law, verbatim (drop-not-inherit): the hull of the
   entries definite on BOTH sides; everything else is dropped. *)
let join (a : (int * (int * int)) list) (b : (int * (int * int)) list) :
    (int * (int * int)) list =
  List.filter_map
    (fun (sid, iv) ->
      match List.assoc_opt sid b with
      | Some iv' -> Some (sid, Mir_numeric.iv_hull iv iv')
      | None -> None)
    a

(* The value-expression grammar of the backend's lower, mirrored: Some iv is
   the proven interval, None is "outside the subset" (NEVER a refusal).
   declared is the sid -> declared-precision list; env is the definite-value
   environment. *)
let rec lower_e maxp (declared : (int * int) list)
    (env : (int * (int * int)) list) (e : Hir.expr) : (int * int) option =
  if e.Hir.ex_ef = Hir.Unknown_ef then None
  else
    match bin_p_of maxp e.Hir.ex_ty with
    | None -> None
    | Some wp ->
        let w = Mir_numeric.window wp in
        match e.Hir.ex with
        | Hir.Const { text } -> (
            match Mir_numeric.decimal_int text with
            | Some v when Mir_numeric.in_window w (v, v) -> Some (v, v)
            | _ -> None)
        | Hir.Var { sid; _ } ->
            if not (List.mem_assoc sid declared) then None
            else
              (match List.assoc_opt sid env with
               | Some iv when Mir_numeric.in_window w iv -> Some iv
               | _ -> None)
        | Hir.Bin { op; left; right; _ } -> (
            match op with
            | Hir.Add | Hir.Sub | Hir.Mul ->
                if left.Hir.ex_ty <> e.Hir.ex_ty
                   || right.Hir.ex_ty <> e.Hir.ex_ty then
                  None
                else
                  (match lower_e maxp declared env left with
                   | Some il -> (
                       match lower_e maxp declared env right with
                       | Some ir ->
                           let iv =
                             match op with
                             | Hir.Add -> Mir_numeric.iv_add il ir
                             | Hir.Sub -> Mir_numeric.iv_sub il ir
                             | Hir.Mul -> Mir_numeric.iv_mul il ir
                             | _ -> assert false
                           in
                           if Mir_numeric.in_window w iv then Some iv else None
                       | None -> None)
                   | None -> None)
            | _ -> None)
        | Hir.Neg { e = inner } -> (
            match lower_e maxp declared env inner with
            | Some iv ->
                let niv = Mir_numeric.iv_neg iv in
                if Mir_numeric.in_window w niv then Some niv else None
            | None -> None)
        | Hir.Convert _ | Hir.Call_e _ | Hir.Elem_read _ | Hir.Elem_ref _ ->
            None

(* The condition law of the backend's lower_cond, mirrored: a relational Bin
   with Condty whose two operands the value grammar proves. No interval is
   recorded — a condition is not a value. *)
let cond_ok maxp declared env (e : Hir.expr) : bool =
  match e.Hir.ex with
  | Hir.Bin { op; left; right; _ } when e.Hir.ex_ty = Hir.Condty -> (
      match op with
      | Hir.Eq | Hir.Ne | Hir.Lt | Hir.Le | Hir.Gt | Hir.Ge ->
          lower_e maxp declared env left <> None
          && lower_e maxp declared env right <> None
      | _ -> false)
  | _ -> false

(* The statement walk, mirroring the backend's lower_stmts: Declare, Assign
   (own-scope D_var, the value proved by the value grammar AND against the
   target's declared window), and If (both arms independent, the join is the
   drop-not-inherit law, a missing ELSE is the identity path). EVERYTHING
   else — While, Call_s, Get, Put, Stop, any Return, an array designation, a
   foreign or undeclared or repeated symbol, a non-integer or non-formal
   storage — is outside the subset. *)
let rec stmts maxp (prog : Hir.program) (pp : Hir.proc)
    (declared : (int * int) list) (env : (int * (int * int)) list)
    (ss : Hir.stmt list) : ((int * int) list * (int * (int * int)) list) option =
  match ss with
  | [] -> Some (declared, env)
  | s :: rest ->
      (match s.Hir.st with
       | Hir.Declare sid ->
           if List.mem_assoc sid declared then None
           else
             (match find_sym prog sid with
              | Some sm ->
                  if sm.Hir.scope <> pp.Hir.scope then None
                  else
                    (match sm.Hir.sstorage with
                     | Hir.Auto ->
                         (match bin_p_of maxp sm.Hir.sty with
                          | Some p ->
                              stmts maxp prog pp ((sid, p) :: declared) env rest
                          | None -> None)
                     | Hir.Formal ->
                         if List.mem sid pp.Hir.params then
                           (match bin_p_of maxp sm.Hir.sty with
                            | Some p ->
                                stmts maxp prog pp ((sid, p) :: declared) env rest
                            | None -> None)
                         else None
                     | _ -> None)
              | None -> None)
       | Hir.Assign { target; value } ->
           (match target with
            | Hir.D_elem _ -> None
            | Hir.D_var { sid } ->
                if not (List.mem_assoc sid declared) then None
                else
                  (match lower_e maxp declared env value with
                   | None -> None
                   | Some iv ->
                       if
                         Mir_numeric.in_window
                           (Mir_numeric.window (List.assoc sid declared))
                           iv
                       then
                         stmts maxp prog pp declared (add_env env sid iv) rest
                       else None))
       | Hir.If { cond; then_; else_ } ->
           if not (cond_ok maxp declared env cond) then None
           else if else_ = [] then
             (* the missing ELSE is the identity path (backend law) *)
             (match stmts maxp prog pp declared env then_ with
              | None -> None
              | Some (d, et) -> stmts maxp prog pp d (join et env) rest)
           else
             (match stmts maxp prog pp declared env then_ with
              | None -> None
              | Some (d, et) ->
                  (match stmts maxp prog pp declared env else_ with
                   | None -> None
                   | Some (_, ee) -> stmts maxp prog pp d (join et ee) rest))
       | _ -> None)

(* The summary of ONE procedure. The backend's env0 law seeds every formal
   with EXACTLY W(p); the last statement must be the top-level Return (Some
   e); the proven interval must sit inside W(q). *)
let summary_of maxp (prog : Hir.program) (pid : int) : summary =
  if pid = 0 then Unknown
  else
    match find_proc prog pid with
    | None -> Unknown
    | Some pp -> (
        match pp.Hir.ret with
        | Some (Hir.Fixed_bin (q, 0)) when q >= 1 && q <= maxp ->
            let rec seed_formals acc = function
              | [] -> Some acc
              | sid :: rest ->
                  (match find_sym prog sid with
                   | Some s ->
                       (match bin_p_of maxp s.Hir.sty with
                        | Some p ->
                            seed_formals
                              ((sid, Mir_numeric.window p) :: acc)
                              rest
                        | None -> None)
                   | None -> None)
            in
            (match seed_formals [] pp.Hir.params with
             | None -> Unknown
             | Some env0 ->
                 (match List.rev pp.Hir.body with
                  | [] -> Unknown
                  | last :: front ->
                      (* the body WITHOUT its final statement, in ORDER — the
                         walk is a left-to-right induction over the statements. *)
                      (match last.Hir.st with
                       | Hir.Return (Some e) ->
                           (match stmts maxp prog pp [] env0 (List.rev front) with
                            | None -> Unknown
                            | Some (declared, env) ->
                                (match lower_e maxp declared env e with
                                 | Some iv ->
                                     if
                                       Mir_numeric.in_window
                                         (Mir_numeric.window q)
                                         iv
                                     then
                                       Known iv
                                     else Unknown
                                 | None -> Unknown))
                       | _ -> Unknown)))
        | _ -> Unknown)

(* The summary list over the queried pids, sorted ascending by pid and
   deduplicated (the deterministic pid -> summary map). *)
let summaries ~maxp (prog : Hir.program) (pids : int list) :
    (int * summary) list =
  List.map
    (fun pid -> (pid, summary_of maxp prog pid))
    (List.sort_uniq Int.compare pids)