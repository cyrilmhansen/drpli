(* hir/mirsumtest.ml — independent test driver for the pure Mir_return_summary
   analysis (E2E-54/P2-DIFF-3 §P2-DIFF-3, Stage B; the mirnumtest precedent).

   WHAT IT PROVES.  Mir_return_summary is ANALYSIS-ONLY: it may add a smaller
   return interval, never a refusal.  The driver judges the module against
   (1) hand-derived expectation literals for the whole §P2-DIFF-3 subset —
   every expected summary is a literal in this file, written from the subset
   law BEFORE any run of the module on it; (2) an INDEPENDENT concrete
   reference: a hand-written interpreter over the same HIR that evaluates the
   real fixture programs (the committed DIF03/DIF04 classifiers) on EVERY
   point of the declared formal window [-16383,16383] and returns the exact
   envelope of the observed values — the summary must contain that envelope
   (soundness) and the hand-derived expectation must equal it (the
   pre-registered tightness); (3) the corruption controls (the §P2-DIFF-3
   falsifiers): the inferred interval is perturbed while the reference and
   the hand-written expectations stay untouched, and the check must fail
   LOUDLY.

   Output contract (mirrors mirnumtest/semtest):
     every check holds  -> stdout gets EXACTLY one line
        MIR-SUM OK <n> checks                rc 0
     any check fails    -> `MIRSUM-FAIL ...' lines on stderr, rc 1, ZERO stdout

   Corruption controls (non-vacuity; the perturbation hits the INFERRED value
   only — never the reference, never the guard, per the Stage-C method law):
     --corrupt-widen   the classifier's Known (1,3) is widened to (1,4)
     --corrupt-narrow  the classifier's Known (1,3) is narrowed to (1,2)
     --corrupt-unknown every pid-1 Unknown is forced to Known (1,2)
                       (every Unknown case fails LOUDLY)
   The three call-site modes (E2E-54/P2-DIFF-4 Stage C) perturb the
   INFERRED (specialized) result of the call-site entry point only:
     --corrupt-spec-widen  the call-site Known is widened by one
     --corrupt-spec-narrow the call-site Known is narrowed by one
     --corrupt-spec-unknown every call-site Unknown is forced to Known (1,2)
   There is no mode that passes the live checks; every corrupt mode is a
   separate process. *)

module R = Pli80_hir.Mir_return_summary

open Pli80_hir

let fails = ref ([] : string list)
let nchecks = ref 0

let check name (cond : bool) =
  incr nchecks;
  if not cond then fails := name :: !fails

let show (a, b) = "[" ^ string_of_int a ^ "," ^ string_of_int b ^ "]"

let show_sum = function
  | R.Known iv -> "Known " ^ show iv
  | R.Unknown -> "Unknown"

let quote s = "'" ^ s ^ "'"

(* --------------------------------------------------------------------------- *)
(* HIR constructors (the synthetic programs)                                    *)
(* --------------------------------------------------------------------------- *)

let bin15 = Hir.Fixed_bin (15, 0)

let binq q = Hir.Fixed_bin (q, 0)

let e_const ?(ty = bin15) ?(ef = Hir.Pure) ?(line = 0) text =
  {
    Hir.ex = Hir.Const { text };
    ex_ty = ty;
    ex_line = line;
    ex_ef = ef;
  }

let e_var ?(ty = bin15) ?(ef = Hir.Pure) ?(line = 0) sid =
  {
    Hir.ex = Hir.Var { sid; addressable = false };
    ex_ty = ty;
    ex_line = line;
    ex_ef = ef;
  }

let e_bin ?(ty = bin15) ?(ef = Hir.Pure) ?(line = 0) op left right =
  {
    Hir.ex = Hir.Bin { op; left; right; typing = "test" };
    ex_ty = ty;
    ex_line = line;
    ex_ef = ef;
  }

let e_rel ?(ef = Hir.Pure) ?(line = 0) op left right =
  {
    Hir.ex = Hir.Bin { op; left; right; typing = "test" };
    ex_ty = Hir.Condty;
    ex_line = line;
    ex_ef = ef;
  }

let e_convert ?(line = 0) from to_ty e =
  {
    Hir.ex = Hir.Convert { from; to_ty; e; reason = "test" };
    ex_ty = to_ty;
    ex_line = line;
    ex_ef = Hir.Pure;
  }

let e_call ?(line = 0) ?(ef = Hir.Pure) pid args =
  {
    Hir.ex = Hir.Call_e { pid; args };
    ex_ty = bin15;
    ex_line = line;
    ex_ef = ef;
  }

let e_elem ?(line = 0) base subs =
  {
    Hir.ex = Hir.Elem_read { base; subs };
    ex_ty = bin15;
    ex_line = line;
    ex_ef = Hir.Pure;
  }

let st ?(line = 0) k = { Hir.st = k; st_line = line }

let s_declare ?(line = 0) sid = st ~line (Hir.Declare sid)

let s_assign ?(line = 0) sid value =
  st ~line (Hir.Assign { target = Hir.D_var { sid }; value })

let s_assign_elem ?(line = 0) base subs value =
  st ~line (Hir.Assign { target = Hir.D_elem { base; subs }; value })

let s_if ?(line = 0) cond then_ else_ =
  st ~line (Hir.If { cond; then_; else_ })

let s_while ?(line = 0) cond body = st ~line (Hir.While { cond; body })

let s_call_s ?(line = 0) pid args = st ~line (Hir.Call_s { pid; args })

let s_ret ?(line = 0) e = st ~line (Hir.Return e)

let s_put ?(line = 0) e = st ~line (Hir.Put (Hir.P_value e))

let s_get ?(line = 0) sid = st ~line (Hir.Get (Hir.D_var { sid }))

let s_stop ?(line = 0) () = st ~line Hir.Stop

let a_value e =
  { Hir.af = Hir.A_value e; ac_ty = bin15; ac_ef = Hir.Pure; ac_line = 0 }

let sym sid name scope sty sstorage =
  {
    Hir.sid;
    skey = name;
    sorig = name;
    scope;
    sty;
    sstorage;
    sline = 0;
  }

let proc ?(name = "p") ?(is_main = false) ?(ret = Some bin15) ?(params = [])
    pid scope body =
  {
    Hir.pid;
    name = Some name;
    is_main;
    scope;
    params;
    ret;
    body;
  }

let prog procs syms =
  { Hir.profile_name = "test"; scopes = []; syms; procs }

(* the classic classifier body: if x > 5 then (if x > 50 then c = 3 else c = 2)
   else c = 1; return c — with the REAL sid layout of the DIF03 dump. *)
let classify_body xsym csym =
  let open Hir in
  [
    s_declare xsym;
    s_declare csym;
    s_if
      
      (e_rel Gt (e_var xsym) (e_const "5"))
      [
        s_if
          
          (e_rel Gt (e_var xsym) (e_const "50"))
          [ s_assign csym (e_const "3") ]
          [ s_assign csym (e_const "2") ];
      ]
      [ s_assign csym (e_const "1") ];
    s_ret (Some (e_var csym));
  ]

(* --------------------------------------------------------------------------- *)
(* the INDEPENDENT reference: a concrete interpreter over the same HIR           *)
(* (hand-written here, NOT the module; the module does not evaluate programs)   *)
(* --------------------------------------------------------------------------- *)

type ev =
  | Done of (int * int) list
      (** the statements ran to their end; the carried environment is the result *)
  | Ret of int
  | Stuck

let rec ev_e env (e : Hir.expr) : int option =
  match e.Hir.ex with
  | Hir.Const { text } -> int_of_string_opt text
  | Hir.Var { sid; _ } -> List.assoc_opt sid env
  | Hir.Bin { op; left; right; _ } -> (
      match (ev_e env left, ev_e env right) with
      | Some x, Some y ->
          Some
            (match op with
             | Hir.Add -> x + y
             | Hir.Sub -> x - y
             | Hir.Mul -> x * y
             | Hir.Eq -> if x = y then 1 else 0
             | Hir.Ne -> if x <> y then 1 else 0
             | Hir.Lt -> if x < y then 1 else 0
             | Hir.Le -> if x <= y then 1 else 0
             | Hir.Gt -> if x > y then 1 else 0
             | Hir.Ge -> if x >= y then 1 else 0)
      | _ -> None)
  | Hir.Neg { e = inner } -> (
      match ev_e env inner with Some x -> Some (-x) | None -> None)
  | Hir.Convert { e = inner; _ } -> ev_e env inner
  | _ -> None

let rec ev_stmts env (ss : Hir.stmt list) : ev =
  match ss with
  | [] -> Done env
  | s :: rest ->
      (match s.Hir.st with
       | Hir.Declare _ -> ev_stmts env rest
       | Hir.Assign { target = Hir.D_var { sid }; value } ->
           (match ev_e env value with
            | Some v ->
                let env' =
                  (sid, v) :: List.filter (fun (k, _) -> k <> sid) env
                in
                ev_stmts env' rest
            | None -> Stuck)
       | Hir.Assign { target = Hir.D_elem _; _ } -> Stuck
       | Hir.If { cond; then_; else_ } ->
           (match ev_e env cond with
            | Some c ->
                let arm = if c <> 0 then then_ else else_ in
                (match ev_stmts env arm with
                 | Done env' -> ev_stmts env' rest
                 | Ret v -> Ret v
                 | Stuck -> Stuck)
            | None -> Stuck)
       | Hir.Return (Some e) ->
           (match ev_e env e with Some v -> Ret v | None -> Stuck)
       | _ -> Stuck)

let run_proc (pp : Hir.proc) (x : int) : int option =
  match pp.Hir.params with
  | [sid] ->
      (match ev_stmts [ (sid, x) ] pp.Hir.body with
       | Ret v -> Some v
       | _ -> None)
  | _ -> None

(* the exact envelope of the observed values over the FULL declared window;
   the -16383/16383 literals are hand-derived (W(15)) — no module call. *)
let ref_range_pp (pp : Hir.proc) : (int * int) option =
  let lo = -16383 in
  let hi = 16383 in
  let rec scan x acc =
    if x > hi then acc
    else
      match run_proc pp x with
      | Some v ->
          scan (x + 1)
            (match acc with None -> Some (v, v) | Some (a, b) -> Some (min a v, max b v))
      | None -> scan (x + 1) acc
  in
  scan lo None

(* --------------------------------------------------------------------------- *)
(* the live families — every expectation a hand-written literal                 *)
(* --------------------------------------------------------------------------- *)

(* --------------------------------------------------------------------------- *)
(* HIR-only helpers for the E2E-54/P2-DIFF-4 call-site family (Stage C).        *)
(* NOTHING here calls Mir_return_summary: the driver's concrete reference       *)
(* evaluator and the expected values are derived INDEPENDENTLY of the module;   *)
(* the module is consulted only at the check points.                            *)
(* --------------------------------------------------------------------------- *)

(* The declared window W(p) = [-(2^(p-1)-1), 2^(p-1)-1], RE-DERIVED here by the
   driver's own arithmetic (the W(15) = 16383 and W(12) = 2047 constants are
   hand-computed, not taken from the module). *)
let wlim p = (1 lsl (p - 1)) - 1
let wiv p = (-wlim p, wlim p)

(* A call site in the HIR: the entry point of the call is the callee pid; the
   actuals are the expression nodes (the sids are resolved by the caller). *)
type cs = { cs_line : int; cs_callee : int; cs_actuals : Hir.expr list }

(* The value of a pure, non-call expression in the driver's point environment.
   A Call_e is NOT a value here (it is a call site); anything else is a
   genuine read (the driver's own walk never reaches an unsupported node). *)
let rec eval_pt env (e : Hir.expr) : int option =
  let open Hir in
  match e.ex with
  | Const { text } -> int_of_string_opt text
  | Var { sid; _ } -> List.assoc_opt sid env
  | Bin { op; left; right; _ } -> (
      match (eval_pt env left, eval_pt env right) with
      | Some x, Some y ->
          Some
            (match op with
             | Add -> x + y
             | Sub -> x - y
             | Mul -> x * y
             | Eq -> if x = y then 1 else 0
             | Ne -> if x <> y then 1 else 0
             | Lt -> if x < y then 1 else 0
             | Le -> if x <= y then 1 else 0
             | Gt -> if x > y then 1 else 0
             | Ge -> if x >= y then 1 else 0)
      | _ -> None)
  | Neg { e = inner } -> (
      match eval_pt env inner with Some x -> Some (-x) | None -> None)
  | Convert { e = inner; _ } -> eval_pt env inner
  | _ -> None

(* The point interpreter for a CALLEE body (subset: the whole §P2-DIFF-3
   grammar, the same shape the module analyses; no call sites expected inside).
   A final Return (Some e) yields the value; anything else is a genuine bug
   (the walk is only used on known-good bodies). *)
let run_callee env (ss : Hir.stmt list) : int =
  let rec go env = function
    | [] -> failwith "run_callee: body ended without a return"
    | s :: rest ->
        (match s.Hir.st with
         | Hir.Declare _ -> go env rest
         | Hir.Assign { target = Hir.D_var { sid }; value } ->
             (match eval_pt env value with
              | Some v -> go ((sid, v) :: List.filter (fun (k, _) -> k <> sid) env) rest
              | None -> failwith "run_callee: unsupported value")
         | Hir.If { cond; then_; else_ } ->
             (* MEASURED on the real fixtures (the DIF03/DIF04/DIF05/DIF06
                callee layout): the Return is a TOP-LEVEL statement AFTER the
                If, not inside the arm — the chosen arm runs, then the walk
                CONTINUES with the statements after the If. *)
             (match eval_pt env cond with
              | Some c -> go env ((if c <> 0 then then_ else else_) @ rest)
              | None -> failwith "run_callee: unsupported condition")
         | Hir.Return (Some e) ->
             (match eval_pt env e with
              | Some v -> v
              | None -> failwith "run_callee: unsupported return")
         | _ -> failwith "run_callee: unsupported statement")
  in
  go env ss

(* The driver's OWN point interpreter for a CALLER body (the DIF05/DIF06
   entries): straight-line Assign/Declare/If/While, the Call_e assignments
   recorded in acc, the final Return (Some e) yields the value. The loop has a
   hard iteration cap; the callers' exact trip counts are checked separately.
   The driver never trusts the module's env here: the recorded actuals are
   concrete values from the driver's own walk. The WALKED ENVIRONMENT is
   returned with the value (the loop threads it: without it the increments
   inside the body would be lost and the walk would never terminate). *)
let exec ~cap (procs : Hir.proc list) (env0 : (int * int) list)
    (ss : Hir.stmt list) (acc : (int * int * (int * int) list) list) :
    (int * (int * int) list
     * (int * int * (int * int) list) list) option =
  let find_proc pid =
    List.find_opt (fun (p : Hir.proc) -> p.Hir.pid = pid) procs
  in
  let rec go env ss acc =
    match ss with
    | [] -> Some (0, env, acc)
    | s :: rest ->
        (match s.Hir.st with
         | Hir.Declare _ -> go env rest acc
         | Hir.Assign { target = Hir.D_var { sid }; value } ->
             (match value.Hir.ex with
              | Hir.Call_e { pid; args } ->
                  let (x, acc) =
                    match (find_proc pid, args) with
                    | Some pp, args ->
                        let avals =
                          List.map
                            (fun (a : Hir.actual) ->
                              match a.Hir.af with
                              | Hir.A_value e -> eval_pt env e
                              | _ -> None)
                            args
                        in
                        (if List.for_all (fun o -> o <> None) avals then
                           let avl =
                             List.filter_map (fun o -> o) avals
                           in
                           let env' =
                             List.map2
                               (fun (psid : int) (v : int) -> (psid, v))
                               pp.Hir.params avl
                           in
                           let r = run_callee env' pp.Hir.body in
                           (Some r, (pid, s.Hir.st_line,
                                     List.map (fun v -> (v, v)) avl)
                                     :: acc)
                         else
                           (None, acc))
                    | _ -> (None, acc)
                  in
                  (match x with
                   | Some v ->
                       go ((sid, v) :: List.filter (fun (k, _) -> k <> sid) env)
                         rest acc
                   | None -> None)
              | _ ->
                  (match eval_pt env value with
                   | Some v ->
                       go ((sid, v) :: List.filter (fun (k, _) -> k <> sid) env)
                         rest acc
                   | None -> None))
         | Hir.If { cond; then_; else_ } ->
             (match eval_pt env cond with
              | Some c ->
                  (match go env (if c <> 0 then then_ else else_) acc with
                   | Some (rv, env', acc') ->
                       (* the arm's writes are visible after the If *)
                       ignore rv;
                       go env' rest acc'
                   | None -> None)
              | None -> None)
         | Hir.While { cond; body } ->
             let rec it n env acc =
               if n >= cap then None
               else
                 match eval_pt env cond with
                 | Some 0 -> go env rest acc
                 | Some _ ->
                     (match go env body acc with
                      | Some (_, env', acc') -> it (n + 1) env' acc'
                      | None -> None)
                 | None -> None
             in
             it 0 env acc
         | Hir.Put _ ->
             (* the real fixtures' put list(...) statements: the walk never
                inspects the output — the recorded call sites and the final
                value are the only evidence. *)
             go env rest acc
         | Hir.Return (Some e) ->
             (match eval_pt env e with
              | Some v -> Some (v, env, acc)
              | None -> None)
         | _ ->
             (* Get / Call_s / Stop: the drivers never use them. *)
             None)
  in
  go env0 ss acc

(* All call sites of the WHOLE program, in source order (entry first), each
   with its statement line: the independent discovery of the real call sites. *)
let find_calls (procs : Hir.proc list) : cs list =
  let out = ref [] in
  let rec stmts (ss : Hir.stmt list) : unit =
    List.iter
      (fun (s : Hir.stmt) ->
        (match s.Hir.st with
         | Hir.Assign { target = _; value } ->
             (match value.Hir.ex with
              | Hir.Call_e { pid; args } ->
                  out :=
                    { cs_line = s.Hir.st_line; cs_callee = pid;
                      cs_actuals =
                        List.map (fun (a : Hir.actual) ->
                                    match a.Hir.af with
                                    | Hir.A_value e -> e
                                    | _ -> assert false)
                          args }
                    :: !out
              | _ -> ())
         | Hir.If { cond; then_; else_ } ->
             expr cond; stmts then_; stmts else_
         | Hir.While { cond; body } -> expr cond; stmts body
         | _ -> ());
        expr_of_stmt s)
      ss
  and expr (e : Hir.expr) : unit =
    match e.Hir.ex with
    | Hir.Bin { left; right; _ } -> expr left; expr right
    | Hir.Neg { e = inner } -> expr inner
    | Hir.Convert { e = inner; _ } -> expr inner
    | _ -> ()
  and expr_of_stmt (s : Hir.stmt) : unit =
    match s.Hir.st with
    | Hir.Assign { value; _ } -> expr value
    | _ -> ()
  in
  List.iter (fun (p : Hir.proc) -> stmts p.Hir.body) procs;
  List.rev !out

(* --------------------------------------------------------------------------- *)
(* The call-site family (Stage C) — every expectation a hand-written literal    *)
(* --------------------------------------------------------------------------- *)

(* The new corruption modes perturb the INFERRED (specialized) result of the
   call-site entry point only — never the driver's reference, never the
   supplied actuals, never a comparison guard (the Stage-C method law). The
   old three modes are keyed to the context-independent entry point and do
   NOT touch this family; the new three are keyed to the call-site entry
   point and do NOT touch the old family. *)
let corrupt_spec = ref None

let corrupt_spec_apply s =
  match (!corrupt_spec, s) with
  | Some `Spec_widen, R.Known (a, b) -> R.Known (a, b + 1)
  | Some `Spec_narrow, R.Known (a, b) -> R.Known (a, b - 1)
  | Some `Spec_unknown, R.Unknown -> R.Known (1, 2)
  | _ -> s

(* E2E-54/P2-DIFF-5 §P2-DIFF-5.8 NON-VACUITY: the refinement family has its OWN
   control. `--corrupt-refine-arm' perturbs the INFERRED REFINED-ARM result only
   — a Known interval is widened at BOTH endpoints (the arm exclusion is what a
   one-sided perturbation cannot see: an EXCLUDED arm makes the summary the
   surviving arm's own interval, so both endpoints are load-bearing), and an
   Unknown is forced to a Known so the §5.8 hostiles fail loudly too. It NEVER
   touches the driver's concrete reference (exec/run_callee), never the supplied
   actuals and never a comparison guard (the Stage-C method law). *)
let corrupt_refine = ref None

let corrupt_refine_apply s =
  match (!corrupt_refine, s) with
  | Some `Refine_arm, R.Known (a, b) -> R.Known (a - 1, b + 1)
  | Some `Refine_arm, R.Unknown -> R.Known (0, 0)
  | _ -> s

(* The call-site entry point under test (the §P2-DIFF-4.6-1 API). *)
let summary_of_actuals prog pid params actuals =
  corrupt_spec_apply (R.summary_of_actuals ~maxp:15 prog pid ~params ~actuals)

(* The SAME entry point on the refinement family's own corrupt path. *)
let refine_actuals name prog pid params actuals want =
  let got =
    corrupt_refine_apply (R.summary_of_actuals ~maxp:15 prog pid ~params ~actuals)
  in
  check (name ^ ": got " ^ show_sum got ^ ", expected " ^ show_sum want)
    (got = want)

let expect_actuals name prog pid params actuals want =
  let got = summary_of_actuals prog pid params actuals in
  check (name ^ ": got " ^ show_sum got ^ ", expected " ^ show_sum want)
    (got = want)

(* The min-shaped body: if x > cap then c = cap else c = x; return (c) —
   the exact shape of the DIF05/DIF06 subsidiaries (a cap is NOT a literal
   comparison; the whole body is the §P2-DIFF-3 grammar). *)
let min_body cap =
  let open Hir in
  [
    s_declare 10;
    s_declare 11;
    s_if (e_rel Gt (e_var 10) (e_const (string_of_int cap)))
      [ s_assign 11 (e_const (string_of_int cap)) ]
      [ s_assign 11 (e_var 10) ];
    s_ret (Some (e_var 11));
  ]

(* The §5.8 orientation-law body: `if x <op> <v> then <then_> else <else_>;
   return (c)` — the min shape with a CHOSEN relational operator (the
   Stage-C refinement family). *)
let cmp_body op v then_ else_ =
  [
    s_declare 10;
    s_declare 11;
    s_if (e_rel op (e_var 10) (e_const v)) then_ else_;
    s_ret (Some (e_var 11));
  ]

let p_min cap =
  prog
    [
      proc ~name:"entry" ~is_main:true 0 0 [ s_ret (Some (e_const "0")) ];
      proc ~params:[ 10 ] 1 1 (min_body cap);
    ]
    [ sym 10 "x" 1 bin15 Hir.Formal; sym 11 "c" 1 bin15 Hir.Auto ]

(* the p_simple shape (the one-formal program) — defined locally here because
   the Stage-B helpers below are in the same file; it mirrors the original
   p_simple builder exactly (same syms, same proc). *)
let p_simple1 body =
  prog
    [
      proc ~name:"entry" ~is_main:true 0 0 [ s_ret (Some (e_const "0")) ];
      proc ~params:[ 10 ] 1 1 body;
    ]
    [
      sym 10 "x" 1 bin15 Hir.Formal;
      sym 11 "c" 1 bin15 Hir.Auto;
      sym 12 "q" 1 (Hir.Char (1, false)) Hir.Auto;
      sym 13 "s" 1 bin15 Hir.Static;
    ]

let identity_body =
  [ s_declare 10; s_ret (Some (e_var 10)) ]

let p_identity () = p_simple1 identity_body

(* The two-formal body: c = x - y; return (c) — the order-sensitive shape. *)
let p_diff () =
  prog
    [
      proc ~name:"entry" ~is_main:true 0 0 [ s_ret (Some (e_const "0")) ];
      proc ~params:[ 10; 12 ] 1 1
        [
          s_declare 10;
          s_declare 12;
          s_declare 11;
          s_assign 11 (e_bin Hir.Sub (e_var 10) (e_var 12));
          s_ret (Some (e_var 11));
        ];
    ]
    [
      sym 10 "x" 1 bin15 Hir.Formal;
      sym 12 "y" 1 bin15 Hir.Formal;
      sym 11 "c" 1 bin15 Hir.Auto;
    ]

(* The formal-modified body: x = 7; return (x) — the seed must be
   OVERWRITTEN (add_env), not merged with the actual. *)
let p_formal_written () =
  p_simple1
    [
      s_declare 10;
      s_assign 10 (e_const "7");
      s_ret (Some (e_var 10));
    ]

(* A narrow-declared formal (bin 12): the containment obligation is measured
   against the FORMAL's own declared window. *)
let p_min12 () =
  prog
    [
      proc ~name:"entry" ~is_main:true 0 0 [ s_ret (Some (e_const "0")) ];
      proc ~params:[ 10 ] 1 1 (min_body 20);
    ]
    [ sym 10 "x" 1 (Hir.Fixed_bin (12, 0)) Hir.Formal;
      sym 11 "c" 1 bin15 Hir.Auto ]

(* The pivots (H3): a body that is unsafe over the FULL declared window. *)
let p_esc () =
  p_simple1
    [
      s_declare 10;
      s_declare 11;
      s_assign 11 (e_bin Hir.Mul (e_var 10) (e_const "100"));
      s_ret (Some (e_var 11));
    ]

let p_esc2 () =
  p_simple1
    [
      s_declare 10;
      s_declare 11;
      s_assign 11 (e_bin Hir.Add (e_var 10) (e_const "1"));
      s_ret (Some (e_var 11));
    ]

let f_actuals () =
  (* the POSITIVES (the §P2-DIFF-4.7 list) *)
  expect_actuals "spec-identity-point" (p_identity ()) 1 [ 10 ] [ (5, 5) ]
    (R.Known (5, 5));
  expect_actuals "spec-identity-range" (p_identity ()) 1 [ 10 ] [ (5, 9) ]
    (R.Known (5, 9));
  expect_actuals "spec-min-cap-point" (p_min 20) 1 [ 10 ] [ (20, 20) ]
    (R.Known (20, 20));
  expect_actuals "spec-min-above-cap" (p_min 20) 1 [ 10 ] [ (25, 25) ]
    (R.Known (20, 20));
  expect_actuals "spec-min-across-cap" (p_min 20) 1 [ 10 ] [ (3, 30) ]
    (R.Known (3, 20));
  expect_actuals "spec-min-nonpoint" (p_min 20) 1 [ 10 ] [ (10, 15) ]
    (R.Known (10, 15));
  expect_actuals "spec-distinct-1" (p_min 20) 1 [ 10 ] [ (3, 3) ]
    (R.Known (3, 3));
  expect_actuals "spec-distinct-2" (p_min 20) 1 [ 10 ] [ (12, 12) ]
    (R.Known (12, 12));
  expect_actuals "spec-distinct-3" (p_min 20) 1 [ 10 ] [ (30, 30) ]
    (R.Known (20, 20));
  expect_actuals "spec-full-window-identity" (p_identity ()) 1 [ 10 ]
    [ wiv 15 ] (R.Known (-16383, 16383));
  expect_actuals "spec-full-window-min" (p_min 20) 1 [ 10 ] [ wiv 15 ]
    (R.Known (-16383, 20));
  expect_actuals "spec-loop-iv" (p_min 12) 1 [ 10 ] [ (1, 4) ]
    (R.Known (1, 4));
  expect_actuals "spec-two-formals-1" (p_diff ()) 1 [ 10; 12 ] [ (10, 10); (1, 1) ]
    (R.Known (9, 9));
  expect_actuals "spec-two-formals-2" (p_diff ()) 1 [ 10; 12 ] [ (1, 1); (10, 10) ]
    (R.Known (-9, -9));
  expect_actuals "spec-two-formals-ranges" (p_diff ()) 1 [ 10; 12 ]
    [ (1, 5); (2, 7) ] (R.Known (-6, 3));
  expect_actuals "spec-boundary-16383" (p_identity ()) 1 [ 10 ] [ (16383, 16383) ]
    (R.Known (16383, 16383));
  expect_actuals "spec-boundary-neg16383" (p_identity ()) 1 [ 10 ]
    [ (-16383, -16383) ] (R.Known (-16383, -16383));
  expect_actuals "spec-boundary-min-12" (p_min 12) 1 [ 10 ] [ (12, 12) ]
    (R.Known (12, 12));
  expect_actuals "spec-boundary-min-20" (p_min 20) 1 [ 10 ] [ (20, 20) ]
    (R.Known (20, 20));
  expect_actuals "spec-boundary-12" (p_min 12) 1 [ 10 ] [ (12, 12) ]
    (R.Known (12, 12));
  expect_actuals "spec-boundary-min-13" (p_min 12) 1 [ 10 ] [ (13, 13) ]
    (R.Known (12, 12));
  expect_actuals "spec-formal-written" (p_formal_written ()) 1 [ 10 ] [ (3, 3) ]
    (R.Known (7, 7));
  (* the H3 (i) legal asymmetry: the specialized interval may be Known while
     the context-independent one is Unknown — a point actual inside the
     operand's window is admissible even though the callee's full window is
     NOT. *)
  expect_actuals "spec-esc-point" (p_esc ()) 1 [ 10 ] [ (3, 3) ]
    (R.Known (300, 300));
  expect_actuals "spec-esc-point-163" (p_esc ()) 1 [ 10 ] [ (163, 163) ]
    (R.Known (16300, 16300));
  expect_actuals "spec-esc2-point" (p_esc2 ()) 1 [ 10 ] [ (0, 0) ]
    (R.Known (1, 1));
  (* the context-independent summaries of the SAME programs (the §P2-DIFF-3
     entry point) — the comparison the two-level law needs. *)
  let ctx name p want =
    let s =
      match R.summaries ~maxp:15 p [ 1 ] with
      | [ (_, s) ] -> s
      | _ -> R.Unknown
    in
    check (name ^ ": got " ^ show_sum s ^ ", expected " ^ show_sum want)
      (s = want)
  in
  ctx "spec-ctx-esc" (p_esc ()) R.Unknown;
  ctx "spec-ctx-esc2" (p_esc2 ()) R.Unknown;
  ctx "spec-ctx-min" (p_min 20) (R.Known (-16383, 20));
  (* the HOSTILES (each Unknown, never a refusal) *)
  expect_actuals "spec-outside-window" (p_min12 ()) 1 [ 10 ] [ (3000, 3000) ]
    R.Unknown;
  expect_actuals "spec-outside-window-16" (p_min12 ()) 1 [ 10 ] [ (2048, 2048) ]
    R.Unknown;
  expect_actuals "spec-empty-interval" (p_min 20) 1 [ 10 ] [ (10, 9) ]
    R.Unknown;
  expect_actuals "spec-missing-actual" (p_min 20) 1 [ 10 ] [] R.Unknown;
  expect_actuals "spec-extra-actual" (p_min 20) 1 [ 10 ] [ (3, 3); (4, 4) ]
    R.Unknown;
  expect_actuals "spec-arity-mismatch" (p_diff ()) 1 [ 10; 12 ] [ (3, 3) ]
    R.Unknown;
  expect_actuals "spec-permuted-order" (p_diff ()) 1 [ 12; 10 ] [ (3, 3); (4, 4) ]
    R.Unknown;
  expect_actuals "spec-unknown-formal" (p_diff ()) 1 [ 10; 99 ] [ (3, 3); (4, 4) ]
    R.Unknown;
  expect_actuals "spec-nonformal-storage" (p_diff ()) 1 [ 10; 11 ] [ (3, 3); (4, 4) ]
    R.Unknown;
  expect_actuals "spec-unsupported-body" (p_simple1 [ s_declare 10; s_declare 11;
    s_assign 11 (e_convert bin15 (Hir.Fixed_bin (12, 0)) (e_const "4"));
    s_ret (Some (e_var 11)) ]) 1 [ 10 ] [ (3, 3) ] R.Unknown;
  expect_actuals "spec-effect-body" (p_simple1 [ s_declare 10; s_declare 11;
    s_assign 11 (e_const "2"); s_put (e_const "1"); s_ret (Some (e_var 11)) ])
    1 [ 10 ] [ (3, 3) ] R.Unknown;
  expect_actuals "spec-entry-pid" (p_min 20) 0 [ 10 ] [ (3, 3) ] R.Unknown;
  expect_actuals "spec-missing-pid" (p_min 20) 7 [ 10 ] [ (3, 3) ] R.Unknown;
  expect_actuals "spec-void-proc" (prog [ proc ~name:"entry" ~is_main:true 0 0
    [ s_ret (Some (e_const "0")) ]; proc ~params:[ 10 ] ~ret:None 1 1 [ s_declare 10 ] ]
    [ sym 10 "x" 1 bin15 Hir.Formal ]) 1 [ 10 ] [ (3, 3) ] R.Unknown

(* --------------------------------------------------------------------------- *)
(* The E2E-54/P2-DIFF-5 §P2-DIFF-5.8 BRANCH-REFINEMENT family (Stage C).        *)
(* EVERY expectation below is a hand-derived literal, written from the §5.2      *)
(* subset law BEFORE any Stage-C run; the arm-by-arm derivation and the          *)
(* CONCRETE value (the driver's own point evaluation, never the module) are in   *)
(* the comment above each check. The positives go through the CORRUPT-WRAPPED    *)
(* call-site entry point, so every refined-arm value is on the non-vacuity path  *)
(* (§5.8: "a control that passes is not a control"); the context-independent     *)
(* pivots use the direct, uncorrupted `R.summaries` call, exactly as the         *)
(* existing `spec-ctx-*` law does.                                              *)
(* --------------------------------------------------------------------------- *)

(* The orientation-law body: `if x <op> 20 then c = 20 else c = x; return (c)` —
   the min shape with a CHOSEN relational operator (the §5.8 orientation law). *)
let cmp_min op =
  cmp_body op "20" [ s_assign 11 (e_const "20") ] [ s_assign 11 (e_var 10) ]

(* `if x = 20 then c = <c> else c = x; return (c)` — the Eq then-side is the
   POINT, the Eq ELSE side is UNREFINED (§5.2-5: the complement of a point is
   not an interval, so the existing env is kept). *)
let cmp_eq c = cmp_body Hir.Eq "20" [ s_assign 11 (e_const c) ] [ s_assign 11 (e_var 10) ]

(* `if x <> 20 then c = 1 else c = x; return (c)` — Ne refines NOTHING on
   either side (§5.2); the conservative hull is kept VERBATIM. *)
let cmp_ne =
  cmp_body Hir.Ne "20" [ s_assign 11 (e_const "1") ] [ s_assign 11 (e_var 10) ]

(* `if x > 20 then c = 20 else c = 5; return (c + x)` — the EXCLUDED arm and the
   variable RE-READ after the join (§5.8): the surviving arm's env, including the
   REFINED condition variable, is what the return expression sees. *)
let p_reread () =
  p_simple1
    [
      s_declare 10;
      s_declare 11;
      s_if
        (e_rel Hir.Gt (e_var 10) (e_const "20"))
        [ s_assign 11 (e_const "20") ]
        [ s_assign 11 (e_const "5") ];
      s_ret (Some (e_bin Hir.Add (e_var 11) (e_var 10)));
    ]

(* `c = 2; if x > 20 then c = 9` (NO else) — the missing-ELSE law (§5.2): the
   THEN arm is refined, the false path is the CURRENT env, and the two are
   joined by the existing drop-not-inherit join. *)
let p_noelse () =
  p_simple1
    [
      s_declare 10;
      s_declare 11;
      s_assign 11 (e_const "2");
      s_if
        (e_rel Hir.Gt (e_var 10) (e_const "20"))
        [ s_assign 11 (e_const "9") ]
        [];
      s_ret (Some (e_var 11));
    ]

(* `Var op Var` with TWO definite formals: outside the §5.2 subset (the right
   operand is not a Const), so the conservative hull is kept VERBATIM. *)
let p_varopvar () =
  prog
    [
      proc ~name:"entry" ~is_main:true 0 0 [ s_ret (Some (e_const "0")) ];
      proc ~params:[ 10; 12 ] 1 1
        [
          s_declare 10;
          s_declare 12;
          s_declare 11;
          s_if
            (e_rel Hir.Gt (e_var 10) (e_var 12))
            [ s_assign 11 (e_const "1") ]
            [ s_assign 11 (e_const "2") ];
          s_ret (Some (e_var 11));
        ];
    ]
    [
      sym 10 "x" 1 bin15 Hir.Formal;
      sym 12 "y" 1 bin15 Hir.Formal;
      sym 11 "c" 1 bin15 Hir.Auto;
    ]

(* HOSTILE: the condition's Var is NOT DEFINITE in the env (§5.2-1). sid 14 is
   declared in the procedure's own scope — so the Declare itself is accepted and
   the sid joins `declared` — but it is never assigned, so it has no env entry.
   The refinement does not apply, and because the value grammar cannot prove the
   operand either, the whole If is outside the subset: the SAME Unknown the
   pre-change code produced. *)
let p_nondefinite () =
  prog
    [
      proc ~name:"entry" ~is_main:true 0 0 [ s_ret (Some (e_const "0")) ];
      proc ~params:[ 10 ] 1 1
        [
          s_declare 10;
          s_declare 11;
          s_declare 14;
          s_assign 11 (e_const "5");
          s_if
            (e_rel Hir.Gt (e_var 14) (e_const "20"))
            [ s_assign 11 (e_const "6") ]
            [ s_assign 11 (e_const "7") ];
          s_ret (Some (e_var 11));
        ];
    ]
    [
      sym 10 "x" 1 bin15 Hir.Formal;
      sym 11 "c" 1 bin15 Hir.Auto;
      sym 14 "u" 1 bin15 Hir.Auto;
    ]

(* The H3 pivot body: `if x > 20 then c = 16383 else c = x * 1000; return (c)`.
   Over the FULL declared window the ELSE arm is unsafe (x * 1000 reaches
   [-16383000,20000], outside W(15)), so the callee's own proof FAILS — the
   refinement must never weaken that (H3). A small actual, however, excludes the
   THEN arm and a big one excludes the ELSE arm, so the SPECIALIZED summary is
   Known while the context-independent one stays Unknown (the legal §P2-DIFF-4
   asymmetry, now reached through a refined arm). *)
let p_h3 () =
  p_simple1
    [
      s_declare 10;
      s_declare 11;
      s_if
        (e_rel Hir.Gt (e_var 10) (e_const "20"))
        [ s_assign 11 (e_const "16383") ]
        [ s_assign 11 (e_bin Hir.Mul (e_var 10) (e_const "1000")) ];
      s_ret (Some (e_var 11));
    ]

let f_refine () =
  (* ---- POSITIVES: the §5.2 orientation law on the min shape. ---- *)
  (* Lt (x < 20): then [lo,min(hi,19)]; else [max(lo,20),hi].
     (3,3): then [3,3] feasible, else [20,3] EMPTY -> the else arm is excluded;
     the surviving arm assigns c = 20 -> [20,20]. Concrete: 3 < 20 -> c = 20. *)
  refine_actuals "refine-lt-below" (p_simple1 (cmp_min Hir.Lt)) 1 [ 10 ]
    [ (3, 3) ] (R.Known (20, 20));
  (* (30,30): then [30,19] EMPTY -> the THEN arm is excluded; else [30,30] ->
     c = x -> [30,30]. Concrete: 30 < 20 is false -> c = 30. *)
  refine_actuals "refine-lt-above" (p_simple1 (cmp_min Hir.Lt)) 1 [ 10 ]
    [ (30, 30) ] (R.Known (30, 30));
  (* (19,20): BOTH arms feasible — then [19,19] (c = 20), else [20,20] (c = x)
     -> the hull is the POINT [20,20]. Concrete: 19 -> 20, 20 -> 20. *)
  refine_actuals "refine-lt-across" (p_simple1 (cmp_min Hir.Lt)) 1 [ 10 ]
    [ (19, 20) ] (R.Known (20, 20));
  (* Le (x <= 20): then [lo,min(hi,20)]; else [max(lo,21),hi].
     (20,20): then [20,20]; else [21,20] EMPTY -> c = 20 -> [20,20]. *)
  refine_actuals "refine-le-at-cap" (p_simple1 (cmp_min Hir.Le)) 1 [ 10 ]
    [ (20, 20) ] (R.Known (20, 20));
  (* (21,21): then [21,20] EMPTY -> excluded; else [21,21] -> c = x -> [21,21].
     Concrete: 21 <= 20 is false -> c = 21. *)
  refine_actuals "refine-le-above" (p_simple1 (cmp_min Hir.Le)) 1 [ 10 ]
    [ (21, 21) ] (R.Known (21, 21));
  (* Ge (x >= 20): then [max(lo,20),hi]; else [lo,min(hi,19)].
     (19,19): then [20,19] EMPTY -> excluded; else [19,19] -> c = x -> [19,19]. *)
  refine_actuals "refine-ge-below" (p_simple1 (cmp_min Hir.Ge)) 1 [ 10 ]
    [ (19, 19) ] (R.Known (19, 19));
  (* (19,25): then [20,25] (c = 20 -> [20,20]); else [19,19] (c = x -> [19,19]);
     the join is [19,20]. Concrete over the points: 19 -> 19, 20..25 -> 20. *)
  refine_actuals "refine-ge-across" (p_simple1 (cmp_min Hir.Ge)) 1 [ 10 ]
    [ (19, 25) ] (R.Known (19, 20));
  (* Gt (x > 20) at the NON-POINT actual [3,30]: then [21,30] -> c = 20;
     else [3,20] -> c = x; the hull is [3,20] — the §5.6-5 computation with the
     orientation flipped. Concrete: 3 -> 3, 20 -> 20, 21 -> 20, 30 -> 20. *)
  refine_actuals "refine-gt-across" (p_simple1 (cmp_min Hir.Gt)) 1 [ 10 ]
    [ (3, 30) ] (R.Known (3, 20));
  (* ---- Eq: the then-side is the POINT, the ELSE side stays UNREFINED. ---- *)
  (* (20,20): then [20,20] -> c = 1; else UNREFINED x = [20,20] -> c = x;
     the join is [1,20]. Concrete: the point 20 takes the THEN arm -> 1, and the
     summary is deliberately WIDER than the concrete value (the else keeps the
     whole entry): the unrefined-else law is visible in the literal. *)
  refine_actuals "refine-eq-point" (p_simple1 (cmp_eq "1")) 1 [ 10 ]
    [ (20, 20) ] (R.Known (1, 20));
  (* (19,25): then [20,20] -> c = 1; else unrefined [19,25] -> c = x -> [19,25];
     the join is [1,25]. Concrete envelope over the points: 19 -> 19, 20 -> 1,
     25 -> 25, i.e. EXACTLY [1,25] (tight). *)
  refine_actuals "refine-eq-across" (p_simple1 (cmp_eq "1")) 1 [ 10 ]
    [ (19, 25) ] (R.Known (1, 25));
  (* (19,19): then [max(19,20),min(19,20)] = [20,19] EMPTY -> the THEN arm is
     EXCLUDED; the unrefined else keeps x = [19,19] -> c = x -> [19,19]. WITHOUT
     the Eq then-side refinement the join would be the hull [1,19], so this
     literal is the discriminating witness of the then-side law. Concrete: 19. *)
  refine_actuals "refine-eq-then-excluded" (p_simple1 (cmp_eq "1")) 1 [ 10 ]
    [ (19, 19) ] (R.Known (19, 19));
  (* (21,21): then [21,20] EMPTY -> excluded; else x = [21,21] -> c = 21. *)
  refine_actuals "refine-eq-else-only" (p_simple1 (cmp_eq "1")) 1 [ 10 ]
    [ (21, 21) ] (R.Known (21, 21));
  (* ---- Ne and Var op Var: the conservative hull is kept VERBATIM. ---- *)
  (* Ne refines NOTHING (§5.2): at (20,20) the arms are walked with the whole
     entry -> hull(c=1, c=x=20) = [1,20]. Had the THEN arm been refined to the
     EMPTY complement, the answer would be [20,20]. Concrete: 20<>20 false -> 20. *)
  refine_actuals "refine-ne-point" (p_simple1 cmp_ne) 1 [ 10 ] [ (20, 20) ]
    (R.Known (1, 20));
  refine_actuals "refine-ne-range" (p_simple1 cmp_ne) 1 [ 10 ] [ (19, 25) ]
    (R.Known (1, 25));
  (* Var op Var (two definite formals): refine does not apply -> the two-arm
     hull [1,2] VERBATIM at (5,5),(3,3) (concrete: 5>3 -> c = 1). *)
  refine_actuals "refine-varopvar-conservative" (p_varopvar ()) 1 [ 10; 12 ]
    [ (5, 5); (3, 3) ] (R.Known (1, 2));
  (* ---- the EXCLUDED arm with the variable RE-READ after the join. ---- *)
  (* (3,3): the THEN arm is EMPTY ([21,3]) -> excluded; the ELSE arm is
     c = 5 with x REFINED to [3,3] -> c + x = [8,8]. Concrete: 5 + 3 = 8. *)
  refine_actuals "refine-reread-else" (p_reread ()) 1 [ 10 ] [ (3, 3) ]
    (R.Known (8, 8));
  (* (30,30): the ELSE arm is EMPTY ([30,20]) -> excluded; the THEN arm is
     c = 20 with x = [30,30] -> [50,50]. Concrete: 20 + 30 = 50. *)
  refine_actuals "refine-reread-then" (p_reread ()) 1 [ 10 ] [ (30, 30) ]
    (R.Known (50, 50));
  (* (19,25): BOTH arms feasible — then c = [20,20], x = [21,25]; else c = [5,5],
     x = [19,20] -> the join is c = [5,20], x = [19,25] -> c + x = [24,45].
     Concrete envelope: 19 -> 24, 20 -> 25, 21 -> 41, 25 -> 45. *)
  refine_actuals "refine-reread-across" (p_reread ()) 1 [ 10 ] [ (19, 25) ]
    (R.Known (24, 45));
  (* ---- the MISSING ELSE: the then arm refined, the false path the identity. *)
  (* (25,25): then [21,25] feasible -> c = 9; the false path is the CURRENT env
     (c = [2,2]); the drop-not-inherit join is [2,9]. Concrete: 25 -> 9. *)
  refine_actuals "refine-noelse-feasible" (p_noelse ()) 1 [ 10 ] [ (25, 25) ]
    (R.Known (2, 9));
  (* (19,19): the THEN arm is EMPTY ([21,19]) and there is no ELSE -> the whole
     If is a NO-OP (§5.2/§5.3-b): the env is the current one, c = [2,2].
     Concrete: 19 > 20 is false, c keeps 2. Pre-refinement this was [2,9]. *)
  refine_actuals "refine-noelse-then-infeasible" (p_noelse ()) 1 [ 10 ]
    [ (19, 19) ] (R.Known (2, 2));
  (* (19,25): the then arm is feasible, so the identity false path still joins:
     [2,9] — the missing-ELSE law is unchanged by the refinement. *)
  refine_actuals "refine-noelse-across" (p_noelse ()) 1 [ 10 ] [ (19, 25) ]
    (R.Known (2, 9));
  (* ---- the FULL-WINDOW seed: the §5.6-7 no-change law at the full window. ----
     Lt at W(15): then [-16383,19] -> c = 20; else [20,16383] -> c = x ->
     the hull is [20,16383]; the concrete envelope over the window is the SAME
     (x < 20 -> 20, x >= 20 -> x, max 16383, min 20). *)
  refine_actuals "refine-fullwindow-lt" (p_simple1 (cmp_min Hir.Lt)) 1 [ 10 ]
    [ wiv 15 ] (R.Known (20, 16383));
  (* Eq at W(15): then [20,20] -> c = 1; the else is UNREFINED over the whole
     window -> c = x = [-16383,16383]; the hull is the whole window — the
     refinement changes NOTHING at the full seed (the §5.3-d no-weakening law). *)
  refine_actuals "refine-fullwindow-eq" (p_simple1 (cmp_eq "1")) 1 [ 10 ]
    [ wiv 15 ] (R.Known (-16383, 16383));
  (* ---- the monotonicity invariant (§5.1 H1): a narrower actual NEVER yields a
     wider summary than the full-window seed, and the refined min summaries form
     the chain [3,3] subset [3,20] subset [-16383,20]. *)
  let sub (a, b) (c, d) = c <= a && b <= d in
  let known = function R.Known iv -> Some iv | R.Unknown -> None in
  let rsum pp pa =
    corrupt_refine_apply (R.summary_of_actuals ~maxp:15 pp 1 ~params:[ 10 ] ~actuals:pa)
  in
  check "refine-monotone-chain"
    (match
       ( known (rsum (p_min 20) [ (3, 3) ]),
         known (rsum (p_min 20) [ (3, 30) ]),
         known (rsum (p_min 20) [ wiv 15 ]) )
     with
     | Some a, Some b, Some c -> sub a b && sub b c
     | _ -> false);
  (* and the same chain for the Gt-oriented reread body: [3,3] -> [8,8];
     [3,30] -> the join c = [5,20] and x = [3,30] -> [8,50]; [-100,100] ->
     c = [5,20] and x = [-100,100] -> [-95,120]. (The FULL window is NOT in
     this chain: there c + x reaches [-16378,16403], outside W(15), so the
     summary is Unknown — the window obligation is applied to the JOINED, i.e.
     already-refined, envs, never to a hull the refinement would widen.) *)
  check "refine-monotone-reread"
    (match
       ( known (rsum (p_reread ()) [ (3, 3) ]),
         known (rsum (p_reread ()) [ (3, 30) ]),
         known (rsum (p_reread ()) [ (-100, 100) ]) )
     with
     | Some a, Some b, Some c -> sub a b && sub b c
     | _ -> false);
  (* ---- HOSTILES (§5.8: each yields the SAME result as the current code). ----
     A non-definite Var in the condition: no refinement, no admission. *)
  refine_actuals "refine-hostile-nondefinite-var" (p_nondefinite ()) 1 [ 10 ]
    [ (3, 3) ] R.Unknown;
  (* A Const that is not a canonical decimal literal ("007" — the decimal_int
     domain): the condition is not provable at all -> the pre-change Unknown. *)
  refine_actuals "refine-hostile-nondecimal-const"
    (p_simple1
       (cmp_body Hir.Gt "007" [ s_assign 11 (e_const "1") ]
          [ s_assign 11 (e_const "2") ]))
    1 [ 10 ] [ (3, 3) ] R.Unknown;
  (* A Const LEFT operand (`20 > x`): outside the §5.2 subset, so the hull is
     kept VERBATIM — [1,2] at the point (3,3), where a (forbidden) refinement of
     the reversed comparison would have produced [1,1]. Concrete: 20>3 -> 1. *)
  refine_actuals "refine-hostile-const-left"
    (p_simple1
       [
         s_declare 10;
         s_declare 11;
         s_if
           (e_rel Hir.Gt (e_const "20") (e_var 10))
           [ s_assign 11 (e_const "1") ]
           [ s_assign 11 (e_const "2") ];
         s_ret (Some (e_var 11));
       ])
    1 [ 10 ] [ (3, 3) ] (R.Known (1, 2));
  (* `Var op Var` where BOTH sides are the same definite Var (`x > x`): the right
     operand is not a Const -> no refinement -> the conservative [1,2] (concrete:
     3>3 is false -> 2). *)
  refine_actuals "refine-hostile-var-op-var"
    (p_simple1
       [
         s_declare 10;
         s_declare 11;
         s_if
           (e_rel Hir.Gt (e_var 10) (e_var 10))
           [ s_assign 11 (e_const "1") ]
           [ s_assign 11 (e_const "2") ];
         s_ret (Some (e_var 11));
       ])
    1 [ 10 ] [ (3, 3) ] (R.Known (1, 2));
  (* A COMPOSITE condition ((x > 20) + (x < 30) carried as a Condty value): not a
     relational Bin, so cond_ok refuses it exactly as before -> Unknown. *)
  refine_actuals "refine-hostile-composite-cond"
    (p_simple1
       [
         s_declare 10;
         s_declare 11;
         s_if
           (e_bin ~ty:Hir.Condty Hir.Add
              (e_rel Hir.Gt (e_var 10) (e_const "20"))
              (e_rel Hir.Lt (e_var 10) (e_const "30")))
           [ s_assign 11 (e_const "1") ]
           [ s_assign 11 (e_const "2") ];
         s_ret (Some (e_var 11));
       ])
    1 [ 10 ] [ (3, 3) ] R.Unknown;
  (* An EMPTY ACTUAL interval is the §P2-DIFF-4 SEED obligation, never an arm
     exclusion: Unknown (the arm-exclusion law must not be reached). *)
  refine_actuals "refine-hostile-empty-actual" (p_min 20) 1 [ 10 ] [ (20, 19) ]
    R.Unknown;
  (* ---- the H3 pivot. ---- *)
  (* Over the FULL declared window the callee is UNSAFE (the else arm's
     x * 1000 escapes W(15)) — the refinement changes NOTHING: Unknown. *)
  let h3ctx =
    match R.summaries ~maxp:15 (p_h3 ()) [ 1 ] with
    | [ (_, s) ] -> s
    | _ -> R.Unknown
  in
  check ("refine-h3-fullwindow: got " ^ show_sum h3ctx ^ ", expected Unknown")
    (h3ctx = R.Unknown);
  (* A small actual EXCLUDES the unsafe THEN... (3,3): the then arm [21,3] is
     EMPTY -> excluded; the surviving else arm is x = [3,3] -> c = 3000,
     inside W(15) -> Known (3000,3000). Concrete: 3000. This is the legal
     asymmetry (the specialized proof is not the callee's own proof); the
     BACKEND still lowers the callee over W(p) and still refuses it — the
     DIF07/DIF08 native lanes and the 190/190 negative panel are the witnesses. *)
  refine_actuals "refine-h3-small-actual" (p_h3 ()) 1 [ 10 ] [ (3, 3) ]
    (R.Known (3000, 3000));
  (* (25,25): the ELSE arm [25,20] is EMPTY -> excluded; the then arm is the
     window-proved POINT 16383 -> Known (16383,16383). Concrete: 16383. *)
  refine_actuals "refine-h3-large-actual" (p_h3 ()) 1 [ 10 ] [ (25, 25) ]
    (R.Known (16383, 16383));
  (* (19,25): BOTH arms feasible -> the hull of the point 16383 (then) and of
     [19,20] * 1000 = [19000,20000] — which ESCAPES W(15) -> Unknown (the window
     obligation is applied to the REFINED interval, not to the old hull). *)
  refine_actuals "refine-h3-across-unknown" (p_h3 ()) 1 [ 10 ] [ (19, 25) ]
    R.Unknown

(* the corruption modes apply to the INFERRED value only, never to the
   reference or the expectation (the Stage-C method law). *)
let corrupt = ref None

let corrupt_apply pid s =
  match (!corrupt, s) with
  | Some `Widen, R.Known (a, b) when pid = 1 -> R.Known (a, b + 1)
  | Some `Narrow, R.Known (a, b) when pid = 1 -> R.Known (a, b - 1)
  | Some `Unknown, R.Unknown when pid = 1 -> R.Known (1, 2)
  | _ -> s

let summary_of prog pid =
  corrupt_apply pid
    (match R.summaries ~maxp:15 prog [ pid ] with
     | [ (_, s) ] -> s
     | _ -> R.Unknown)

let expect name prog pid want =
  let got = summary_of prog pid in
  check (name ^ ": got " ^ show_sum got ^ ", expected " ^ show_sum want)
    (got = want)

let syms_x_c ?(xty = bin15) ?(cty = bin15) xsym csym =
  [
    sym xsym "x" 1 xty Hir.Formal;
    sym csym "c" 1 cty Hir.Auto;
  ]

let p_classify ?(xsym = 10) ?(csym = 11) ?(ret = Some bin15) ?(params = [ xsym ])
    ?(xty = bin15) () =
  prog
    [
      proc ~name:"entry" ~is_main:true 0 0 [ s_ret (Some (e_const "0")) ];
      proc ~params ~ret 1 1 (classify_body xsym csym);
    ]
    (syms_x_c ~xty xsym csym)

let p_simple body =
  prog
    [
      proc ~name:"entry" ~is_main:true 0 0 [ s_ret (Some (e_const "0")) ];
      proc ~params:[ 10 ] 1 1 body;
    ]
    [
      sym 10 "x" 1 bin15 Hir.Formal;
      sym 11 "c" 1 bin15 Hir.Auto;
      sym 12 "q" 1 (Hir.Char (1, false)) Hir.Auto;
      sym 13 "s" 1 bin15 Hir.Static;
    ]

let p_classify_with_callers () =
  prog
    [
      proc ~name:"entry" ~is_main:true 0 0
        [
          s_assign 20 (e_call 1 [ a_value (e_const "1") ]);
          s_assign 21 (e_call 1 [ a_value (e_const "2") ]);
          s_ret (Some (e_var 20));
        ];
      proc ~params:[ 10 ] 1 1 (classify_body 10 11);
    ]
    (sym 20 "n" 0 bin15 Hir.Auto
    :: sym 21 "m" 0 bin15 Hir.Auto
    :: syms_x_c 10 11)

let f_constant () =
  expect "const-direct" (p_simple [ s_declare 10; s_ret (Some (e_const "7")) ]) 1
    (R.Known (7, 7));
  expect "const-local"
    (p_simple [ s_declare 10; s_declare 11; s_assign 11 (e_const "5"); s_ret (Some (e_var 11)) ]) 1
    (R.Known (5, 5));
  expect "classifier" (p_classify ()) 1 (R.Known (1, 3))

let f_join () =
  expect "two-arm-hull"
    (p_simple
       [
         s_declare 10;
         s_declare 11;
         s_if (e_rel Hir.Gt (e_var 10) (e_const "5"))
           [ s_assign 11 (e_const "1") ]
           [ s_assign 11 (e_const "2") ];
         s_ret (Some (e_var 11));
       ])
    1 (R.Known (1, 2));
  expect "missing-else-identity"
    (p_simple
       [
         s_declare 10;
         s_declare 11;
         s_assign 11 (e_const "2");
         s_if (e_rel Hir.Gt (e_var 10) (e_const "5"))
           [ s_assign 11 (e_const "1") ] [];
         s_ret (Some (e_var 11));
       ])
    1 (R.Known (1, 2));
  expect "overwrite-after-join"
    (p_simple
       [
         s_declare 10;
         s_declare 11;
         s_if (e_rel Hir.Gt (e_var 10) (e_const "5"))
           [ s_assign 11 (e_const "1") ]
           [ s_assign 11 (e_const "2") ];
         s_assign 11 (e_const "4");
         s_ret (Some (e_var 11));
       ])
    1 (R.Known (4, 4))

let f_nonexhaustive () =
  (* the c = 1 arm only: c is not definite on the ELSE path — the join drops
     it (the backend's own drop-not-inherit law), so the read of c is a
     definite-initialization violation. *)
  expect "non-exhaustive-assign"
    (p_simple
       [
         s_declare 10;
         s_declare 11;
         s_if (e_rel Hir.Gt (e_var 10) (e_const "5"))
           [ s_assign 11 (e_const "1") ] [];
         s_ret (Some (e_var 11));
       ])
    1 R.Unknown

let f_effectful () =
  expect "effect-put"
    (p_simple [ s_declare 10; s_declare 11; s_assign 11 (e_const "2"); s_put (e_const "1"); s_ret (Some (e_var 11)) ])
    1 R.Unknown;
  expect "effect-call-s"
    (p_simple [ s_declare 10; s_declare 11; s_assign 11 (e_const "2"); s_call_s 0 [ a_value (e_const "1") ]; s_ret (Some (e_var 11)) ])
    1 R.Unknown;
  expect "effect-get"
    (p_simple [ s_declare 10; s_declare 11; s_assign 11 (e_const "2"); s_get 10; s_ret (Some (e_var 11)) ])
    1 R.Unknown;
  expect "effect-stop"
    (p_simple [ s_declare 10; s_declare 11; s_assign 11 (e_const "2"); s_stop (); s_ret (Some (e_var 11)) ])
    1 R.Unknown;
  expect "effect-while"
    (p_simple [ s_declare 10; s_declare 11; s_assign 11 (e_const "2"); s_while (e_rel Hir.Lt (e_var 11) (e_const "1")) [ s_assign 11 (e_const "1") ]; s_ret (Some (e_var 11)) ])
    1 R.Unknown;
  expect "early-return"
    (p_simple [ s_declare 10; s_declare 11; s_assign 11 (e_const "2"); s_ret (Some (e_var 11)); s_ret (Some (e_const "1")) ])
    1 R.Unknown;
  expect "return-not-last"
    (p_simple [ s_declare 10; s_ret (Some (e_const "1")); s_assign 11 (e_const "2") ]) 1
    R.Unknown;
  expect "bare-return"
    (p_simple [ s_declare 10; s_assign 11 (e_const "2"); s_ret None ]) 1 R.Unknown

let f_unsupported () =
  expect "unsupported-convert"
    (p_simple [ s_declare 10; s_declare 11; s_assign 11 (e_convert bin15 (Hir.Fixed_bin (12, 0)) (e_const "4")); s_ret (Some (e_var 11)) ])
    1 R.Unknown;
  expect "unsupported-relational-value"
    (p_simple [ s_declare 10; s_declare 11; s_assign 11 (e_rel Hir.Gt (e_var 10) (e_const "5")); s_ret (Some (e_var 11)) ])
    1 R.Unknown;
  expect "unsupported-call-e"
    (p_simple [ s_declare 10; s_declare 11; s_assign 11 (e_call 1 [ a_value (e_const "1") ]); s_ret (Some (e_var 11)) ])
    1 R.Unknown;
  expect "unsupported-return-call"
    (p_simple [ s_declare 10; s_ret (Some (e_call 1 [ a_value (e_const "1") ])) ]) 1
    R.Unknown;
  expect "unsupported-elem-read"
    (p_simple [ s_declare 10; s_declare 11; s_assign 11 (e_elem 11 [ e_const "0" ]); s_ret (Some (e_var 11)) ])
    1 R.Unknown;
  expect "unsupported-elem-assign"
    (p_simple [ s_declare 10; s_declare 11; s_assign_elem 11 [ e_const "0" ] (e_const "2"); s_ret (Some (e_var 11)) ])
    1 R.Unknown;
  expect "unsupported-unknown-ef"
    (p_simple [ s_declare 10; s_declare 11; s_assign 11 (e_const ~ef:Hir.Unknown_ef "4"); s_ret (Some (e_var 11)) ])
    1 R.Unknown;
  expect "unsupported-condition-call"
    (p_simple
       [
         s_declare 10;
         s_declare 11;
         s_assign 11 (e_const "1");
         s_if (e_rel Hir.Gt (e_call 1 [ a_value (e_const "1") ]) (e_const "0"))
           [ s_assign 11 (e_const "2") ]
           [ s_assign 11 (e_const "3") ];
         s_ret (Some (e_var 11));
       ])
    1 R.Unknown

let f_escape () =
  expect "escape-full-window"
    (p_simple [ s_declare 10; s_declare 11; s_assign 11 (e_bin Hir.Mul (e_var 10) (e_const "100")); s_ret (Some (e_var 11)) ])
    1 R.Unknown;
  expect "escape-add-1"
    (p_simple [ s_declare 10; s_declare 11; s_assign 11 (e_bin Hir.Add (e_var 10) (e_const "1")); s_ret (Some (e_var 11)) ])
    1 R.Unknown;
  expect "literal-16383"
    (p_simple [ s_declare 10; s_ret (Some (e_const "16383")) ]) 1 (R.Known (16383, 16383));
  expect "literal-16384"
    (p_simple [ s_declare 10; s_ret (Some (e_const "16384")) ]) 1 R.Unknown;
  expect "identity-full-window"
    (p_simple [ s_declare 10; s_ret (Some (e_var 10)) ]) 1 (R.Known (-16383, 16383))

let f_declarations () =
  expect "undeclared-formal-read"
    (p_simple [ s_declare 11; s_assign 11 (e_const "2"); s_ret (Some (e_var 10)) ])
    1 R.Unknown;
  expect "undeclared-read"
    (p_simple [ s_declare 10; s_ret (Some (e_var 11)) ]) 1 R.Unknown;
  expect "double-declare"
    (p_simple [ s_declare 10; s_declare 10; s_assign 11 (e_const "2"); s_ret (Some (e_var 11)) ])
    1 R.Unknown;
  expect "foreign-scope-declare"
    (prog
       [
         proc ~name:"entry" ~is_main:true 0 0 [ s_ret (Some (e_const "0")) ];
         proc ~params:[ 10 ] 1 1
           [ s_declare 10; s_declare 99; s_declare 11; s_assign 11 (e_const "2"); s_ret (Some (e_var 11)) ];
       ]
       [ sym 99 "z" 0 bin15 Hir.Auto; sym 10 "x" 1 bin15 Hir.Formal; sym 11 "c" 1 bin15 Hir.Auto ])
    1 R.Unknown;
  expect "non-integer-declare"
    (p_simple [ s_declare 10; s_declare 12; s_declare 11; s_assign 11 (e_const "2"); s_ret (Some (e_var 11)) ])
    1 R.Unknown;
  expect "static-declare"
    (p_simple [ s_declare 10; s_declare 13; s_declare 11; s_assign 11 (e_const "2"); s_ret (Some (e_var 11)) ])
    1 R.Unknown

let f_shapes () =
  expect "entry-unknown" (p_simple [ s_declare 10; s_ret (Some (e_const "1")) ]) 0
    R.Unknown;
  expect "missing-pid" (p_simple [ s_declare 10; s_ret (Some (e_const "1")) ]) 7
    R.Unknown;
  expect "void-proc"
    (prog
       [
         proc ~name:"entry" ~is_main:true 0 0 [ s_ret (Some (e_const "0")) ];
         proc ~params:[ 10 ] ~ret:None 1 1 [ s_declare 10 ];
       ]
       [ sym 10 "x" 1 bin15 Hir.Formal ])
    1 R.Unknown;
  expect "non-bin-result"
    (prog
       [
         proc ~name:"entry" ~is_main:true 0 0 [ s_ret (Some (e_const "0")) ];
         proc ~ret:(Some (Hir.Char (1, false))) 1 1 [ s_ret (Some (e_const "1")) ];
       ]
       [])
    1 R.Unknown;
  expect "empty-body"
    (prog
       [
         proc ~name:"entry" ~is_main:true 0 0 [ s_ret (Some (e_const "0")) ];
         proc 1 1 [];
       ]
       [])
    1 R.Unknown

let f_precision () =
  expect "ret-p0" (p_classify ~ret:(Some (binq 0)) ()) 1 R.Unknown;
  expect "ret-p16" (p_classify ~ret:(Some (binq 16)) ()) 1 R.Unknown;
  expect "formal-p0" (p_classify ~xty:(binq 0) ()) 1 R.Unknown;
  expect "formal-p16" (p_classify ~xty:(binq 16) ()) 1 R.Unknown;
  expect "formal-non-bin"
    (p_classify ~xty:(Hir.Char (1, false)) ()) 1 R.Unknown;
  (* a classifier with a smaller declared window: the summary still holds
     inside the window. *)
  expect "classifier-narrow-precision"
    (p_classify ~xty:(Hir.Fixed_bin (2, 0)) ())
    1 (R.Known (1, 1))

let f_purity () =
  let p = p_classify () in
  let s = R.summaries ~maxp:15 p [ 1; 1 ] in
  check "two-callers-single-entry" (s = [ (1, R.Known (1, 3)) ]);
  let s = R.summaries ~maxp:15 (p_classify_with_callers ()) [ 1; 1; 0 ] in
  check "two-callers-one-summary" (s = [ (0, R.Unknown); (1, R.Known (1, 3)) ]);
  check "deterministic"
    (R.summaries ~maxp:15 p [ 3; 1; 2 ] = [ (1, R.Known (1, 3)); (2, R.Unknown); (3, R.Unknown) ])

let f_boundary () =
  expect "boundary-neg-16383"
    (p_simple [ s_declare 10; s_declare 11; s_assign 11 (e_bin Hir.Sub (e_var 10) (e_const "0")); s_ret (Some (e_var 11)) ])
    1 (R.Known (-16383, 16383));
  expect "boundary-neg-op"
    (p_simple [ s_declare 10; s_declare 11; s_assign 11 (Hir.({ ex = Hir.Neg { e = e_const "16383" }; ex_ty = bin15; ex_line = 0; ex_ef = Hir.Pure })); s_ret (Some (e_var 11)) ])
    1 (R.Known (-16383, -16383));
  expect "boundary-tight"
    (p_simple
       [
         s_declare 10;
         s_declare 11;
         s_if (e_rel Hir.Gt (e_var 10) (e_const "0"))
           [ s_assign 11 (e_const "16383") ]
           [ s_assign 11 (e_bin Hir.Sub (e_const "0") (e_const "16383")) ];
         s_ret (Some (e_var 11));
       ])
    1 (R.Known (-16383, 16383))

(* --------------------------------------------------------------------------- *)
(* The real fixtures (the committed DIF03–DIF06) through the REAL Hir_build     *)
(* path: the builders are shared by the context-independent family (f_real)     *)
(* and the call-site family (f_real_spec). The expectations are the same        *)
(* hand-derived literals; the module is consulted only at the check points.     *)
(* --------------------------------------------------------------------------- *)

let read_src f =
  let text = In_channel.with_open_bin f In_channel.input_all in
  match String.index_opt text '\026' with
  | Some i -> String.sub text 0 i
  | None -> text

let find_pid name procs =
  match
    List.find_opt (fun (p : Hir.proc) -> p.Hir.name = Some name) procs
  with
  | Some p -> Some p.Hir.pid
  | None -> None

let find_proc_by_name name procs =
  List.find_opt (fun (p : Hir.proc) -> p.Hir.name = Some name) procs

let build_hir f =
  let text =
    try Some (read_src f) with _ -> None
  in
  match text with
  | None ->
      check ("real-source exists: " ^ quote f) false;
      None
  | Some text ->
      (try
         let blk = Pli80.Parser.parse_source text in
         let profile = Pli80_hir.Target.dr_pli80_v1_4 in
         (match Pli80_hir.Hir_build.build blk profile with
          | Ok p -> Some p
          | Error _ ->
              check ("real-source builds: " ^ quote f) false;
              None)
       with
       | _ ->
           check ("real-source parses: " ^ quote f) false;
           None)

let f_real () =
  let check_real f name want =
    match build_hir f with
    | None -> ()
    | Some p ->
        (match find_pid name p.Hir.procs with
         | None ->
             check ("real-proc exists: " ^ quote name) false
         | Some pid ->
             let s = R.summaries ~maxp:15 p [ pid ] in
             check ("real: " ^ quote name ^ " got " ^ show_sum (snd (List.hd s)) ^ " expected " ^ show_sum want)
               (s = [ (pid, want) ]);
             (match (want, List.find (fun (x : Hir.proc) -> x.Hir.pid = pid) p.Hir.procs) with
              | R.Known (lo, hi), pp ->
                  (match ref_range_pp pp with
                   | Some (a, b) ->
                       check ("real-ref: " ^ quote name ^ " envelope " ^ show (a, b))
                         (a = lo && b = hi)
                   | None ->
                       check ("real-ref: " ^ quote name ^ " ran to a value") false)
              | _ -> ())
        )
  in
  check_real "hir/dif-fixtures/DIF03.pli" "classify" (R.Known (1, 3));
  check_real "hir/dif-fixtures/DIF04.pli" "stepclass" (R.Known (1, 3));
  (* the §P2-DIFF-5 REAL fixtures: the min-shaped callees. Their CONTEXT-
     independent summaries are the §5.6-7 no-change law at the full seed
     (the always-feasible arm clips the hull), and the concrete envelope over
     the whole window is the independent witness (ref_range_pp). *)
  check_real "hir/dif-fixtures/DIF07.pli" "capped" (R.Known (-16383, 20));
  check_real "hir/dif-fixtures/DIF08.pli" "limited" (R.Known (-16383, 12))

(* --------------------------------------------------------------------------- *)
(* The REAL-FIXTURE call-site measurement (E2E-54/P2-DIFF-4 §P2-DIFF-4.7, the   *)
(* numbers the 2d78f47b commit OWES). The entry is executed by the driver's     *)
(* OWN concrete walk (exec — the INDEPENDENT reference, never the module); the  *)
(* call sites are the driver's own structural find_calls; the module is         *)
(* consulted ONLY at the summary calls (the corrupt-controlled path). EVERY     *)
(* expectation below is a hand-derived literal: the §P2-DIFF-4.4 campaign       *)
(* vectors (DIF05 puts [1500,6000,10000] — the last cell is 10000; DIF06 puts   *)
(* [700,1400,2100,2800] — the last cell is 2800, the loop exits at i = 5) and   *)
(* the specialized summaries from the §P2-DIFF-5.2 REFINEMENT law BY HAND: an   *)
(* arm whose condition is provably FALSE over the actual is EXCLUDED —          *)
(* [3,3] |-> the c = 20 arm is infeasible (3 > 20 is false) -> [3,3];           *)
(* [12,12] |-> [12,12]; [30,30] |-> the c = x arm is infeasible -> [20,20];     *)
(* [1,4] |-> the c = 12 arm is infeasible -> [1,4]; the context-independent     *)
(* summary of both min-shaped callees is the FULL hull clipped by the ALWAYS-   *)
(* feasible arm: [-16383,20] (the new spec-ctx-min law). *)
(* --------------------------------------------------------------------------- *)

let f_real_spec () =
  (* the driver's OWN re-derivation of W(15) (wiv/wlim above) — the
     cross-check's containment, never a module call. *)
  let w15 = wiv 15 in
  let in_w15 (a, b) =
    let (lo, hi) = w15 in
    a >= lo && b <= hi
  in
  let ctx_sum p pid =
    match R.summaries ~maxp:15 p [ pid ] with
    | [ (_, s) ] -> s
    | _ -> R.Unknown
  in
  let real_spec f entry_name callee_name =
    match build_hir f with
    | None -> None
    | Some p ->
        (match
           (find_proc_by_name entry_name p.Hir.procs,
            find_proc_by_name callee_name p.Hir.procs)
         with
         | Some entry, Some callee -> Some (p, entry, callee)
         | _ ->
             check ("spec-real-procs: " ^ quote f) false;
             None)
  in
  (* DIF05: entry billing, callee capped_units (the min(x,20) shape). *)
  (match real_spec "hir/dif-fixtures/DIF05.pli" "billing" "capped_units" with
   | None -> ()
   | Some (p, entry, callee) ->
       let cp = callee.Hir.pid in
       let calls = find_calls p.Hir.procs in
       check "spec-real-dif05-struct"
         (List.length calls = 3
          && List.for_all (fun (c : cs) -> c.cs_callee = cp &&
                                           List.length c.cs_actuals = 1) calls
          && List.map (fun (c : cs) -> c.cs_line) calls = [ 6; 10; 14 ]);
       (match exec ~cap:50 p.Hir.procs [] entry.Hir.body [] with
        | None -> check "spec-real-dif05-exec" false
        | Some (v, env, recd) ->
            let ivs = List.map (fun (_, _, a) -> a) (List.rev recd) in
            check "spec-real-dif05-actuals"
              (ivs = [ [(3, 3)]; [(12, 12)]; [(30, 30)] ]);
            (* the CONCRETE call results: the driver's walk returns the
               ACTUAL values (the module's hull would be wider — the
               condition is never decided). *)
            check "spec-real-dif05-cats" (List.assoc_opt 1 env = Some 20);
            check "spec-real-dif05-bill" (List.assoc_opt 2 env = Some 10000);
            check "spec-real-dif05-entry" (v = 10000);
            expect_actuals "spec-real-dif05-sum1" p cp callee.Hir.params
              [ (3, 3) ] (R.Known (3, 3));
            expect_actuals "spec-real-dif05-sum2" p cp callee.Hir.params
              [ (12, 12) ] (R.Known (12, 12));
            expect_actuals "spec-real-dif05-sum3" p cp callee.Hir.params
              [ (30, 30) ] (R.Known (20, 20));
            let ctx = ctx_sum p cp in
            check "spec-real-dif05-ctx" (ctx = R.Known (-16383, 20));
            (* the cross-checks (the invariant actual ⊆ specialized ⊆
               declared): every recorded actual is a non-empty point inside
               the driver's own W(15), and the specialized summary is a
               subset of the context-independent (full-window) one. *)
            check "spec-real-dif05-subset"
              (List.for_all
                 (fun ivs ->
                   List.for_all (fun (a, b) -> a <= b && in_w15 (a, b)) ivs)
                 ivs
               && List.for_all
                    (fun (a, b) ->
                      match ctx with
                      | R.Known (c, d) -> a >= c && b <= d
                      | R.Unknown -> false)
                    [ (3, 3); (12, 12); (20, 20) ])
       ));
  (* DIF06: entry batch, callee limited_step (the min(x,12) shape); the
     loop-IV actual [1,4] is the HULL of the four recorded trips. *)
  (match real_spec "hir/dif-fixtures/DIF06.pli" "batch" "limited_step" with
   | None -> ()
   | Some (p, entry, callee) ->
       let cp = callee.Hir.pid in
       let calls = find_calls p.Hir.procs in
       check "spec-real-dif06-struct"
         (List.length calls = 1
          && List.for_all (fun (c : cs) -> c.cs_callee = cp &&
                                           List.length c.cs_actuals = 1) calls
          && List.map (fun (c : cs) -> c.cs_line) calls = [ 7 ]);
       (match exec ~cap:50 p.Hir.procs [] entry.Hir.body [] with
        | None -> check "spec-real-dif06-exec" false
        | Some (v, env, recd) ->
            let recd = List.rev recd in
            let ivs = List.map (fun (_, _, a) -> a) recd in
            check "spec-real-dif06-trips"
              (ivs = [ [(1, 1)]; [(2, 2)]; [(3, 3)]; [(4, 4)] ]);
            let hull =
              List.fold_left
                (fun (a, b) ivs ->
                  List.fold_left
                    (fun (x, y) (u, w) -> (min x u, max y w))
                    (a, b) ivs)
                (1, 1) ivs
            in
            check "spec-real-dif06-hull" (hull = (1, 4));
            check "spec-real-dif06-cl" (List.assoc_opt 1 env = Some 4);
            check "spec-real-dif06-v" (List.assoc_opt 2 env = Some 2800);
            check "spec-real-dif06-entry" (v = 5);
            expect_actuals "spec-real-dif06-sum" p cp callee.Hir.params
              [ hull ] (R.Known (1, 4));
            let ctx = ctx_sum p cp in
            check "spec-real-dif06-ctx" (ctx = R.Known (-16383, 12));
            check "spec-real-dif06-subset"
              (in_w15 hull
               && match ctx with
                  | R.Known (c, d) ->
                      let (a, b) = (1, 4) in
                      a >= c && b <= d && c = -16383 && d = 12
                  | R.Unknown -> false)
       ));
  (* ---- E2E-54/P2-DIFF-5 §P2-DIFF-5.8: the two REAL refinement fixtures. ----
     DIF07 (entry `scaling`, callee `capped` = min(x,20)) has THREE call sites
     with the POINT actuals 3, 7, 12 — every one of them BELOW the cap, so the
     `c = 20` arm is provably infeasible, is EXCLUDED, and the summary is the
     actual POINT itself (the branch-insensitive hull would have been [a,20]).
     The hand-derived campaign vector is [3000,7000,12000] (each min(q,20) * 1000)
     and the entry returns the LAST bill, 12000. *)
  (match real_spec "hir/dif-fixtures/DIF07.pli" "scaling" "capped" with
   | None -> ()
   | Some (p, entry, callee) ->
       let cp = callee.Hir.pid in
       let calls = find_calls p.Hir.procs in
       check "spec-real-dif07-struct"
         (List.length calls = 3
          && List.for_all (fun (c : cs) -> c.cs_callee = cp &&
                                           List.length c.cs_actuals = 1) calls
          && List.map (fun (c : cs) -> c.cs_line) calls = [ 6; 10; 14 ]);
       (match exec ~cap:50 p.Hir.procs [] entry.Hir.body [] with
        | None -> check "spec-real-dif07-exec" false
        | Some (v, _env, recd) ->
            let ivs = List.map (fun (_, _, a) -> a) (List.rev recd) in
            check "spec-real-dif07-actuals"
              (ivs = [ [(3, 3)]; [(7, 7)]; [(12, 12)] ]);
            check "spec-real-dif07-entry" (v = 12000);
            expect_actuals "spec-real-dif07-sum1" p cp callee.Hir.params
              [ (3, 3) ] (R.Known (3, 3));
            expect_actuals "spec-real-dif07-sum2" p cp callee.Hir.params
              [ (7, 7) ] (R.Known (7, 7));
            expect_actuals "spec-real-dif07-sum3" p cp callee.Hir.params
              [ (12, 12) ] (R.Known (12, 12));
            let ctx = ctx_sum p cp in
            check "spec-real-dif07-ctx" (ctx = R.Known (-16383, 20));
            (* the core invariant on the REAL fixture: actual ⊆ specialized ⊆
               context-independent ⊆ W(15), plus the refinement witness that
               every below-cap POINT actual specializes to ITSELF. *)
            check "spec-real-dif07-subset"
              (List.for_all
                 (fun ivs ->
                   List.for_all (fun (a, b) -> a <= b && in_w15 (a, b)) ivs)
                 ivs
               && List.for_all
                    (fun (a, b) ->
                      match ctx with
                      | R.Known (c, d) -> a >= c && b <= d
                      | R.Unknown -> false)
                    [ (3, 3); (7, 7); (12, 12) ]
               && List.for_all
                    (fun (a, b) ->
                      match
                        summary_of_actuals p cp callee.Hir.params [ (a, b) ]
                      with
                      | R.Known (x, y) -> x = a && y = b
                      | R.Unknown -> false)
                    [ (3, 3); (7, 7); (12, 12) ])
       ));
  (* DIF08 (entry `batched`, callee `limited` = min(x,12)) has ONE call site
     inside the loop; the four trips carry the actuals 1..4, so the hull is the
     NON-POINT [1,4] — still below the cap, so the `c = 12` arm is EXCLUDED and
     the summary is [1,4] (the hull would have been [1,12]). The campaign vector
     is [1500,3000,4500,6000] and the entry returns the loop IV, 5. *)
  (match real_spec "hir/dif-fixtures/DIF08.pli" "batched" "limited" with
   | None -> ()
   | Some (p, entry, callee) ->
       let cp = callee.Hir.pid in
       let calls = find_calls p.Hir.procs in
       check "spec-real-dif08-struct"
         (List.length calls = 1
          && List.for_all (fun (c : cs) -> c.cs_callee = cp &&
                                           List.length c.cs_actuals = 1) calls
          && List.map (fun (c : cs) -> c.cs_line) calls = [ 7 ]);
       (match exec ~cap:50 p.Hir.procs [] entry.Hir.body [] with
        | None -> check "spec-real-dif08-exec" false
        | Some (v, _env, recd) ->
            let recd = List.rev recd in
            let ivs = List.map (fun (_, _, a) -> a) recd in
            check "spec-real-dif08-trips"
              (ivs = [ [(1, 1)]; [(2, 2)]; [(3, 3)]; [(4, 4)] ]);
            let hull =
              List.fold_left
                (fun (a, b) ivs ->
                  List.fold_left
                    (fun (x, y) (u, w) -> (min x u, max y w))
                    (a, b) ivs)
                (1, 1) ivs
            in
            check "spec-real-dif08-hull" (hull = (1, 4));
            check "spec-real-dif08-entry" (v = 5);
            expect_actuals "spec-real-dif08-sum" p cp callee.Hir.params
              [ hull ] (R.Known (1, 4));
            (* the boundary of the REAL fixture: at the actual [1,12] the THEN arm
               needs x > 12, which is EMPTY, so the ELSE arm (c = x) is the only
               feasible one and the summary is the whole [1,12]. *)
            expect_actuals "spec-real-dif08-sum-atcap" p cp callee.Hir.params
              [ (1, 12) ] (R.Known (1, 12));
            (* the first actual ABOVE the cap: the ELSE arm is EMPTY, so the
               `c = 12' arm alone survives and the summary collapses to the cap. *)
            expect_actuals "spec-real-dif08-sum-above" p cp callee.Hir.params
              [ (13, 13) ] (R.Known (12, 12));
            let ctx = ctx_sum p cp in
            check "spec-real-dif08-ctx" (ctx = R.Known (-16383, 12));
            check "spec-real-dif08-subset"
              (in_w15 hull
               && match ctx with
                  | R.Known (c, d) ->
                      let (a, b) = (1, 4) in
                      a >= c && b <= d && c = -16383 && d = 12
                  | R.Unknown -> false)
       ))

let live () =
  f_constant ();
  f_join ();
  f_nonexhaustive ();
  f_effectful ();
  f_unsupported ();
  f_escape ();
  f_declarations ();
  f_shapes ();
  f_precision ();
  f_purity ();
  f_boundary ();
  f_real ();
  (* the Stage-C call-site family LAST: its corrupt modes (the §P2-DIFF-4.7
     non-vacuity controls) must keep the OLD corrupt tables' failure lines
     byte-identical — the old modes are keyed to the old path only, and the
     new family's failures are appended at the END of the failure list. *)
  f_actuals ();
  (* the Stage-C §5.8 refinement family (E2E-54/P2-DIFF-5): the orientation law,
     the Eq-else-UNREFINED law, the Ne/Var-op-Var conservative law, the missing-
     ELSE law, the excluded-arm + re-read law, the full-window no-change law, the
     §5.8 hostiles and the H3 pivot — all on the CORRUPT-WRAPPED call-site path. *)
  f_refine ();
  f_real_spec ()

type mode =
  | Live
  | Corrupt_widen
  | Corrupt_narrow
  | Corrupt_unknown
  | Corrupt_spec_widen
  | Corrupt_spec_narrow
  | Corrupt_spec_unknown
  | Corrupt_refine_arm
  | Usage_error

let () =
  let args = List.tl (Array.to_list Sys.argv) in
  let mode =
    match args with
    | [] -> Live
    | [ "--corrupt-widen" ] ->
        corrupt := Some `Widen;
        Corrupt_widen
    | [ "--corrupt-narrow" ] ->
        corrupt := Some `Narrow;
        Corrupt_narrow
    | [ "--corrupt-unknown" ] ->
        corrupt := Some `Unknown;
        Corrupt_unknown
    | [ "--corrupt-spec-widen" ] ->
        corrupt_spec := Some `Spec_widen;
        Corrupt_spec_widen
    | [ "--corrupt-spec-narrow" ] ->
        corrupt_spec := Some `Spec_narrow;
        Corrupt_spec_narrow
    | [ "--corrupt-spec-unknown" ] ->
        corrupt_spec := Some `Spec_unknown;
        Corrupt_spec_unknown
    | [ "--corrupt-refine-arm" ] ->
        corrupt_refine := Some `Refine_arm;
        Corrupt_refine_arm
    | _ -> Usage_error
  in
  if mode = Usage_error then begin
    prerr_endline
      ("usage: mirsumtest [--corrupt-widen|--corrupt-narrow|--corrupt-unknown"
       ^ "|--corrupt-spec-widen|--corrupt-spec-narrow|--corrupt-spec-unknown"
       ^ "|--corrupt-refine-arm]");
    exit 2
  end;
  live ();
  if !fails <> [] then begin
    List.iter (fun m -> prerr_endline ("MIRSUM-FAIL: " ^ m)) (List.rev !fails);
    exit 1
  end;
  Printf.printf "MIR-SUM OK %d checks\n" !nchecks;
  exit 0