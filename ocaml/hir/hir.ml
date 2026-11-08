(* lib/hir.ml — backend-neutral typed High-level IR (E2E-54/P0).

   This module defines a TARGET-INDEPENDENT semantic representation only. The
   invariant is contractual, not aspirational: NOTHING below may mention a byte
   size, a frame or DATA offset, an 8080 register/opcode, a LINK-80/REL record,
   a DR builtin name or a memory address. Those live in the historical backend
   (Codegen/Rel80) which never references this module (E2E-54 falsifiers F7/F8,
   spec/lab-evidence/e2e54/PLAN.md).

   This is deliberately NOT Digital Research's historical `$V` intermediate
   representation — that instrument lives in ir.ml and stays untouched.

   Identities: every symbol gets a stable [sid], every procedure a stable [pid],
   every scope a stable [scope_id], assigned by deterministic pre-order traversal
   of bind-produced layout rows. No hash iteration, no addresses, no timestamps.

   No SSA: statements mutate named storage through sids (assignment-oriented,
   matching the source language), per the P0 "avoid premature SSA" constraint.

   Provenance: every derived type carries the RULE that produced it as a plain
   string; the rules are language-level and documented (backend-boundary.md §4);
   none of them is a claim about DR.

   Dump indentation (adjudicated E2E-54/P0 hop 4, PLAN §P0.3 review): a call's
   argument EXPRESSION nests one level below its [arg N] label — the call node's
   children print at [indent + 2] (label at [indent + 1]) in BOTH [Call_e] and
   [Call_s], so an argument is never at the same depth as its label. *)

(* ---------- semantic types ---------- *)

type ty =
  | Fixed_bin of int * int   (** FIXED BINARY(precision, scale) *)
  | Fixed_dec of int * int   (** FIXED DECIMAL(p,s) — type expressible; P0 lowering refuses *)
  | Char of int * bool       (** CHARACTER(n) [VARYING] — semantic length, NOT the DR length-byte cell *)
  | Bit of int
  | Ptrty                    (** POINTER: names a designation relation, not a 2-byte cell *)
  | Labelty                  (** LABEL value (an address per the LANGUAGE; representation is backend choice) *)
  | Condty                   (** the value type of a condition expression (language-level notion) *)
  | Voidty                   (** the absence of a value (procedures called as statements, STOP) *)

let pp_ty = function
  | Fixed_bin (p, s) -> Printf.sprintf "FIXED BINARY(%d,%d)" p s
  | Fixed_dec (p, s) -> Printf.sprintf "FIXED DECIMAL(%d,%d)" p s
  | Char (n, true) -> Printf.sprintf "CHARACTER(%d) VARYING" n
  | Char (n, false) -> Printf.sprintf "CHARACTER(%d)" n
  | Bit n -> Printf.sprintf "BIT(%d)" n
  | Ptrty -> "POINTER"
  | Labelty -> "LABEL"
  | Condty -> "CONDITION"
  | Voidty -> "VOID"

(* ---------- symbols and scopes ---------- *)

type storage =
  | Auto        (** ordinary automatic duration (NO frame offset: that is layout) *)
  | Static      (** declared STATIC: duration semantics only *)
  | Formal      (** procedure parameter *)
  | External_sym (** EXTERNAL/ENTRY-declared name (identity only in P0) *)

let pp_storage = function
  | Auto -> "auto" | Static -> "static" | Formal -> "formal" | External_sym -> "external"

type sym = {
  sid : int;
  skey : string;      (** lowercase resolution key exactly as bind rows carry it *)
  sorig : string;     (** source spelling, for dumps *)
  scope : int;
  sty : ty;
  sstorage : storage;
  sline : int;        (** declaration line *)
}

type scope_kind = Program_scope | Proc_scope of int (** owning pid *)

type scope = { scope_id : int; parent : int option; skind : scope_kind }

(* ---------- expressions ---------- *)

type binop = Add | Sub | Mul | Eq | Ne | Lt | Le | Gt | Ge

let pp_binop = function
  | Add -> "+" | Sub -> "-" | Mul -> "*"
  | Eq -> "=" | Ne -> "^=" | Lt -> "<" | Le -> "<=" | Gt -> ">" | Ge -> ">="

type ef_kind =
  | Pure          (** constants and variable reads *)
  | Unknown_ef    (** contains a call: a PL/I procedure may write anything reachable *)

(** Expression nodes are ORDERED: [left] evaluates before [right]; call [args]
    evaluate left-to-right. That ordering IS the evaluation-order contract. *)
type expr =
  { ex : expr_kind; ex_ty : ty; ex_line : int; ex_ef : ef_kind }
and expr_kind =
  | Const of { text : string }            (** literal as written; [ex_ty] from the profile *)
  | Var of { sid : int; addressable : bool }
  | Bin of { op : binop; left : expr; right : expr; typing : string }
  | Neg of { e : expr }
  | Convert of { from : ty; to_ty : ty; e : expr; reason : string }
  | Call_e of { pid : int; args : expr list }  (** function call used as a value *)

(* ---------- statements ---------- *)

type stmt = { st : stmt_kind; st_line : int }
and stmt_kind =
  | Declare of int                        (** the sid introduced by a dcl statement *)
  | Assign of { target : expr; value : expr }  (** target is a Var in the P0 subset *)
  | If of { cond : expr; then_ : stmt list; else_ : stmt list }
  | While of { cond : expr; body : stmt list }  (** the single P0 loop form: DO WHILE *)
  | Call_s of { pid : int; args : expr list }   (** call as a statement; result discarded *)
  | Return of expr option
  | Stop                                  (** program end (no code: the backend decides how) *)

(* ---------- program ---------- *)

type proc = {
  pid : int;
  name : string option;           (** source name (None for an anonymous nesting) *)
  is_main : bool;
  scope : int;
  params : int list;              (** sids, declaring order = the calling-order contract *)
  ret : ty option;                (** RETURNS(...) type, or None for a PROCEDURE *)
  body : stmt list;
}

type program = {
  profile_name : string;          (** the profile whose rules typed the literals *)
  scopes : scope list;            (** ascending scope_id *)
  syms : sym list;                (** ascending sid *)
  procs : proc list;              (** ascending pid; pid 0 is the entry/main block *)
}

(* ---------- deterministic textual dump ---------- *)

let rec dump_expr buf indent e =
  let pad = String.make (2 * indent) ' ' in
  let eff = match e.ex_ef with Pure -> "pure" | Unknown_ef -> "unknown-effect" in
  match e.ex with
  | Const { text } ->
      Printf.bprintf buf "%sconst %s : %s  [%s, line %d]\n"
        pad text (pp_ty e.ex_ty) eff e.ex_line
  | Var { sid; addressable } ->
      Printf.bprintf buf "%svar sym(%d)%s : %s  [%s, line %d]\n"
        pad sid (if addressable then "" else " readonly") (pp_ty e.ex_ty) eff e.ex_line
  | Bin { op; left; right; typing } ->
      Printf.bprintf buf "%sbinop %s : %s  [%s, line %d; typing=%s]\n"
        pad (pp_binop op) (pp_ty e.ex_ty) eff e.ex_line typing;
      Printf.bprintf buf "%s  order: left then right\n" pad;
      dump_expr buf (indent + 1) left;
      dump_expr buf (indent + 1) right
  | Neg { e = inner } ->
      Printf.bprintf buf "%snegate : %s  [%s, line %d]\n"
        pad (pp_ty e.ex_ty) eff e.ex_line;
      dump_expr buf (indent + 1) inner
  | Convert { from; to_ty; e = inner; reason } ->
      Printf.bprintf buf "%sconvert %s -> %s  [%s, line %d; reason=%s]\n"
        pad (pp_ty from) (pp_ty to_ty) eff e.ex_line reason;
      dump_expr buf (indent + 1) inner
  | Call_e { pid; args } ->
      Printf.bprintf buf "%scall proc(%d) : %s  [%s, line %d; args left-to-right]\n"
        pad pid (pp_ty e.ex_ty) eff e.ex_line;
      List.iteri
        (fun i a ->
          Printf.bprintf buf "%s  arg %d\n" pad i;
          dump_expr buf (indent + 2) a)
        args

let rec dump_stmt buf indent s =
  let pad = String.make (2 * indent) ' ' in
  match s.st with
  | Declare sid ->
      Printf.bprintf buf "%sdeclare sym(%d)  [line %d]\n" pad sid s.st_line
  | Assign { target; value } ->
      Printf.bprintf buf "%sassign  [line %d]\n" pad s.st_line;
      Printf.bprintf buf "%s  order: target address then value\n" pad;
      dump_expr buf (indent + 1) target;
      dump_expr buf (indent + 1) value
  | If { cond; then_; else_ } ->
      Printf.bprintf buf "%sif  [line %d]\n" pad s.st_line;
      dump_expr buf (indent + 1) cond;
      Printf.bprintf buf "%s  then:\n" pad;
      List.iter (dump_stmt buf (indent + 1)) then_;
      if else_ <> [] then begin
        Printf.bprintf buf "%s  else:\n" pad;
        List.iter (dump_stmt buf (indent + 1)) else_
      end
  | While { cond; body } ->
      Printf.bprintf buf "%swhile  [line %d]\n" pad s.st_line;
      dump_expr buf (indent + 1) cond;
      Printf.bprintf buf "%s  body:\n" pad;
      List.iter (dump_stmt buf (indent + 1)) body
  | Call_s { pid; args } ->
      Printf.bprintf buf "%scall proc(%d)  [line %d; args left-to-right]\n" pad pid s.st_line;
      List.iteri
        (fun i a ->
          Printf.bprintf buf "%s  arg %d\n" pad i;
          dump_expr buf (indent + 2) a)
        args
  | Return None -> Printf.bprintf buf "%sreturn  [line %d]\n" pad s.st_line
  | Return Some e ->
      Printf.bprintf buf "%sreturn value  [line %d]\n" pad s.st_line;
      dump_expr buf (indent + 1) e
  | Stop -> Printf.bprintf buf "%sstop  [line %d]\n" pad s.st_line

let dump (p : program) : string =
  let buf = Buffer.create 4096 in
  Printf.bprintf buf "HIR-DUMP schema=v0 profile=%s\n" p.profile_name;
  List.iter
    (fun sc ->
      let kind =
        match sc.skind with
        | Program_scope -> "program"
        | Proc_scope pid -> Printf.sprintf "proc(%d)" pid
      in
      let par = match sc.parent with Some x -> string_of_int x | None -> "-" in
      Printf.bprintf buf "SCOPE %d parent=%s kind=%s\n" sc.scope_id par kind)
    p.scopes;
  List.iter
    (fun sy ->
      Printf.bprintf buf "SYM %d name=%s key=%s scope=%d type=%s storage=%s line=%d\n"
        sy.sid sy.sorig sy.skey sy.scope (pp_ty sy.sty) (pp_storage sy.sstorage) sy.sline)
    p.syms;
  List.iter
    (fun pr ->
      let nm = match pr.name with Some n -> n | None -> "(anonymous)" in
      let ret = match pr.ret with Some t -> pp_ty t | None -> "none" in
      let ps = String.concat "," (List.map string_of_int pr.params) in
      Printf.bprintf buf "PROC %d name=%s main=%b scope=%d params=[%s] returns=%s\n"
        pr.pid nm pr.is_main pr.scope ps ret;
      Printf.bprintf buf "BODY proc(%d)\n" pr.pid;
      List.iter (dump_stmt buf 1) pr.body;
      Printf.bprintf buf "END proc(%d)\n" pr.pid)
    p.procs;
  Buffer.contents buf
