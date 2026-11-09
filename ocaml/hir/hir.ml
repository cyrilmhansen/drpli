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
   [Call_s], so an argument is never at the same depth as its label.

   E2E-54/P1-a1 (PLAN §P1-a1.3) — one-dimensional arrays and addressable targets.
   Three representation decisions, all internal (the H01-H04/H06/H07 dump bytes
   stay frozen, falsifier T2):
     - [Array1] carries the ELEMENT type and the two DECLARED INDEX BOUNDS. No
       stride, no element width, no placement: those are layout and stop at the
       Semantic_env boundary (§P1-a1.4, T6).
     - Reading an element ([Elem_read]) and designating an element as the target
       of an assignment ([Elem_ref]) are DIFFERENT constructors, so the two
       programs [x = a(i);] and [a(i) = x;] cannot collapse into one node (brief
       Phase 3). Designation is expressed by the [target] type, not by a flag.
     - [Assign.target] becomes [target] ([T_var]/[T_elem]) instead of an [expr].
       A target is not a value expression, so it no longer carries its own line:
       a designated target prints at the line of the assignment statement — the
       same bytes every existing fixture produces today (measured T2 review of
       H01-H04, where each lhs sits on its statement's line) and one less piece
       of duplicated state. Bounds are recovered for printing through [program]
       (rendering, not representation): the dump helpers take the symbol table.
   DR's historical evaluation order for subscripts is UNMEASURED [TBD]; what is
   recorded here is an HIR representation choice, never a language law (§P1-a1.3).

   E2E-54/P1-a2 (PLAN §P1-a2.2, §P1-a2.4) — arguments and designation.

   Evaluation-order adjudication (§P1-a2.2, DECIDED not deferred): the dump wording
   [args left-to-right] is NOT an unsupported claim — it is DR-ABI-backed for the
   measured shapes by [C093] (interleaved per-argument materialisation, source
   order). It is an EMISSION-order fact about DR's ABI, not a portable PL/I
   execution-order guarantee, and the language-level order of evaluation of actuals
   remains [unmeasured]/[TBD]. The ordered [arg N] list is therefore a REPRESENTATION
   ordering (source/positional order = bind's own [cs_args] order); the only backed
   execution-order evidence is [C093] for internal fixed-type calls, with DEC/array/
   external shapes unmeasured. Argument POSITIONS are kept ([arg N] = bind formal
   position); no node here claims an evaluation order beyond that cited evidence.

   Representation (§P1-a2.4): designation is ONE notion — a [designator] — used both
   for assignment targets ([target], the P1-a1 [T_var]/[T_elem] RENAMED, bytes
   unchanged) and for reference-passed actuals. An actual is [A_value] or
   [A_reference], never a flag: the two passing requirements are different
   constructors, so it is impossible for a backend to treat an unresolved
   reference-passing requirement as ordinary by-value passing. An [A_value] is never
   built from a bare name or an element designation (the classifier routes every such
   actual to [A_reference]), and an unclassified case is not representable at all —
   the lowering refuses (HIR-E15/E16/E17) instead of inventing a node. No
   unrestricted pointer type and no dereference node is added. *)

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
  | Array1 of { elem : ty; lo : int; hi : int }
      (** one-dimensional array: element type + DECLARED lower/upper index bounds
          (facts A-2/A-6: the bounds are bind's own literal record). Semantic
          quantities only — no stride, no element width, no placement (§P1-a1.3). *)

let rec pp_ty = function
  | Fixed_bin (p, s) -> Printf.sprintf "FIXED BINARY(%d,%d)" p s
  | Fixed_dec (p, s) -> Printf.sprintf "FIXED DECIMAL(%d,%d)" p s
  | Char (n, true) -> Printf.sprintf "CHARACTER(%d) VARYING" n
  | Char (n, false) -> Printf.sprintf "CHARACTER(%d)" n
  | Bit n -> Printf.sprintf "BIT(%d)" n
  | Ptrty -> "POINTER"
  | Labelty -> "LABEL"
  | Condty -> "CONDITION"
  | Voidty -> "VOID"
  | Array1 { elem; lo; hi } ->
      Printf.sprintf "%s ARRAY[%d:%d]" (pp_ty elem) lo hi

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
  | Call_e of { pid : int; args : actual list }
      (** function call used as a value; P1-a2 §P1-a2.4: every argument carries its OWN
          passing requirement — an [actual], never a bare expression. **)
  | Elem_read of { base : int; subs : expr list }
      (** LOAD of element [base(subs)] (§P1-a1.3). [ex_ty] is the ELEMENT type; [subs]
          holds EXACTLY ONE expression (the subset gate refuses any other count) and its
          effect is the union of the subscript effects — an element read is not [Pure]
          merely because its subscript is. The base sid names a symbol whose projected
          type is [Array1]; the declared bounds are NOT duplicated here, they live on the
          type (§P1-a1.3). A whole-array load is unrepresentable: no node exists for it
          and the lowering refuses it (HIR-E13). *)
  | Elem_ref of { base : int; subs : expr list }
      (** LVALUE designator of element [base(subs)]; [ex_ty] is the ELEMENT type.
          DEAD since P1-a1: designation lives ONLY in the [designator] type below
          (assignment targets and reference actuals), the value-lowering path never
          constructs it, and semtest invariant I8 rejects it if anything ever does. *)
(* Designation, not value (§P1-a2.4): the location a program talks about — used for
   assignment targets ([target]) AND for reference-passed actuals, so the two roles
   cannot drift apart. [D_elem] carries EXACTLY ONE subscript (the subset gate refuses
   any other count) and its base sid names a symbol whose projected type is [Array1];
   the declared bounds ride the type, never the node. *)
and designator =
  | D_var of { sid : int }
  | D_elem of { base : int; subs : expr list }
(* The passing requirement of ONE actual argument (§P1-a2.4), constructed ONLY by the
   classifier from bind's own passing evidence (§P1-a2.3) — see [lower_actual]: the two
   requirements are different constructors, no bool, no default. *)
and actual_form =
  | A_value of expr
      (** by-value requirement: the callee receives a value; the caller's storage is NOT
          addressable through it. The expression is never itself a bare-name read on
          this path (the classifier routes every bare name/element to [A_reference]). **)
  | A_reference of designator
      (** reference requirement: the callee can read AND write the designated caller
          cell [C093 R2011; C130 E28C; C175 EA2]. Built ONLY from a bare name or an
          element designation — never from an expression. **)
and actual = {
  af : actual_form;
  ac_ty : ty;  (** the callee's DECLARED formal type (§P1-a2.5 type discipline) **)
  ac_ef : ef_kind;  (** the effect of evaluating/designating this argument **)
  ac_line : int;  (** the call's line: designators carry no line of their own **)
}

(* ---------- assignment targets (P1-a1 §P1-a1.3; P1-a2 §P1-a2.4) ---------- *)

(* A target IS a designator: the same node type the reference actuals use. P1-a1's
   [T_var]/[T_elem] are RENAMED [D_var]/[D_elem] and every dump byte is unchanged
   (falsifier T2). [Elem_read] cannot appear here by typing, so reading and
   designating can never collapse into the same node (brief Phase 3). *)
type target = designator

(* ---------- console I/O (E2E-54/P1-m1, PLAN §P1-m1.4) ---------- *)

(* The two console output roles are DIFFERENT constructors, so a backend can never
   treat an output EXPRESSION (m1a: an integer value) as an output TEXT (m1b: a
   validated literal) or vice versa. Nothing below names a stream, a buffer or a
   byte: the MIR shapes live in the backend alone (§P1-m1.5). *)
type put_source =
  | P_value of expr                          (** m1a: an integer expression  *)
  | P_text  of { text : string }             (** m1b: a validated literal    *)

(* ---------- statements ---------- *)

type stmt = { st : stmt_kind; st_line : int }
and stmt_kind =
  | Declare of int                        (** the sid introduced by a dcl statement *)
  | Assign of { target : target; value : expr }
      (** target is a designator: a scalar variable or an array element (P1-a1/P1-a2) *)
  | If of { cond : expr; then_ : stmt list; else_ : stmt list }
  | While of { cond : expr; body : stmt list }  (** the single P0 loop form: DO WHILE *)
  | Call_s of { pid : int; args : actual list }
      (** call as a statement; result discarded; arguments carry passing requirements *)
  | Return of expr option
  | Stop                                  (** program end (no code: the backend decides how) *)
  | Put of put_source
      (** E2E-54/P1-m1 §P1-m1.4: console PUT of the ONE accepted data item on the
          default stream; the statement line rides [st_line], the expression (if any)
          carries its own. *)
  | Get of designator
      (** console GET into a scalar designation (only [D_var] is ever produced — the
          lowering refuses every other target shape at HIR-E21; designation REUSES
          [Hir.designator] resolved through the EXISTING resolve channel). *)

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

(* Rendering recovers the declared bounds through [program] (representation stays
   minimal, §P1-a1.3). A base sid with no projected symbol, or a non-array symbol
   used as an element base, would violate a [Hir.program] invariant that semtest I8
   judges against the live environment; the markers are loud and decimal-free so they
   could never be mistaken for data, and are unreachable by proof. *)
let find_sym (syms : sym list) (sid : int) : sym option =
  List.find_opt (fun (s : sym) -> s.sid = sid) syms

let pp_elem_base syms sid =
  match find_sym syms sid with
  | Some { sty = Array1 { lo; hi; _ }; _ } -> Printf.sprintf "sym(%d)[%d:%d]" sid lo hi
  | Some _ -> Printf.sprintf "sym(%d)[not-an-array]" sid
  | None -> Printf.sprintf "sym(%d)[no-such-sym]" sid

let pp_sym_ty syms sid =
  match find_sym syms sid with
  | Some { sty; _ } -> pp_ty sty
  | None -> "no-such-sym"

(* P1-a2 §P1-a2.4: ONE designator renderer for BOTH roles — an assignment target and a
   reference actual. The bytes are the old [dump_target] bytes exactly (T2): a variable
   designation prints the line the old [T_var] printed, an element designation the line
   the old [T_elem] printed. The element type is ALWAYS recovered through [find_sym]
   (rendering, not representation); [dvar_ty] supplies the type text of the variable
   line — the target role passes the symbol projection, an actual passes its recorded
   formal type, which the E17 discipline makes equal to it. No reference line ever
   carries a readonly marker: a designator IS a location. *)
let rec dump_designator syms buf indent (ef : ef_kind) (dvar_ty : int -> string)
    (line : int) (d : designator) =
  let pad = String.make (2 * indent) ' ' in
  let eff = match ef with Pure -> "pure" | Unknown_ef -> "unknown-effect" in
  match d with
  | D_var { sid } ->
      Printf.bprintf buf "%svar sym(%d) : %s  [%s, line %d]\n" pad sid (dvar_ty sid) eff
        line
  | D_elem { base; subs } ->
      let elem_ty =
        match find_sym syms base with
        | Some { sty = Array1 { elem; _ }; _ } -> pp_ty elem
        | _ -> pp_elem_base syms base
      in
      Printf.bprintf buf "%selem_ref %s : %s  [%s, line %d]\n"
        pad (pp_elem_base syms base) elem_ty eff line;
      List.iter (dump_expr syms buf (indent + 1)) subs

(* [A_value] renders exactly the expression line it renders today (byte-identical,
   T2); [A_reference] renders the designator at the SAME indent (§P1-a2.4). *)
and dump_actual syms buf indent (a : actual) =
  match a.af with
  | A_value e -> dump_expr syms buf indent e
  | A_reference d ->
      dump_designator syms buf indent a.ac_ef
        (fun _ -> pp_ty a.ac_ty) a.ac_line d

and dump_expr syms buf indent e =
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
      dump_expr syms buf (indent + 1) left;
      dump_expr syms buf (indent + 1) right
  | Neg { e = inner } ->
      Printf.bprintf buf "%snegate : %s  [%s, line %d]\n"
        pad (pp_ty e.ex_ty) eff e.ex_line;
      dump_expr syms buf (indent + 1) inner
  | Convert { from; to_ty; e = inner; reason } ->
      Printf.bprintf buf "%sconvert %s -> %s  [%s, line %d; reason=%s]\n"
        pad (pp_ty from) (pp_ty to_ty) eff e.ex_line reason;
      dump_expr syms buf (indent + 1) inner
  | Call_e { pid; args } ->
      Printf.bprintf buf "%scall proc(%d) : %s  [%s, line %d; args left-to-right]\n"
        pad pid (pp_ty e.ex_ty) eff e.ex_line;
      List.iteri
        (fun i a ->
          Printf.bprintf buf "%s  arg %d\n" pad i;
          dump_actual syms buf (indent + 2) a)
        args
  | Elem_read { base; subs } ->
      Printf.bprintf buf "%selem_read %s : %s  [%s, line %d]\n"
        pad (pp_elem_base syms base) (pp_ty e.ex_ty) eff e.ex_line;
      List.iter (dump_expr syms buf (indent + 1)) subs
  | Elem_ref { base; subs } ->
      Printf.bprintf buf "%selem_ref %s : %s  [%s, line %d]\n"
        pad (pp_elem_base syms base) (pp_ty e.ex_ty) eff e.ex_line;
      List.iter (dump_expr syms buf (indent + 1)) subs

(* A designated target prints at its assignment statement's line, effect [pure]
   (§P1-a1.3); the bytes are the pre-P1-a2 [dump_target] bytes verbatim. *)
let rec dump_stmt syms buf indent s =
  let pad = String.make (2 * indent) ' ' in
  match s.st with
  | Declare sid ->
      Printf.bprintf buf "%sdeclare sym(%d)  [line %d]\n" pad sid s.st_line
  | Assign { target; value } ->
      Printf.bprintf buf "%sassign  [line %d]\n" pad s.st_line;
      Printf.bprintf buf "%s  order: target address then value\n" pad;
      dump_designator syms buf (indent + 1) Pure (pp_sym_ty syms) s.st_line target;
      dump_expr syms buf (indent + 1) value
  | If { cond; then_; else_ } ->
      Printf.bprintf buf "%sif  [line %d]\n" pad s.st_line;
      dump_expr syms buf (indent + 1) cond;
      Printf.bprintf buf "%s  then:\n" pad;
      List.iter (dump_stmt syms buf (indent + 1)) then_;
      if else_ <> [] then begin
        Printf.bprintf buf "%s  else:\n" pad;
        List.iter (dump_stmt syms buf (indent + 1)) else_
      end
  | While { cond; body } ->
      Printf.bprintf buf "%swhile  [line %d]\n" pad s.st_line;
      dump_expr syms buf (indent + 1) cond;
      Printf.bprintf buf "%s  body:\n" pad;
      List.iter (dump_stmt syms buf (indent + 1)) body
  | Call_s { pid; args } ->
      Printf.bprintf buf "%scall proc(%d)  [line %d; args left-to-right]\n" pad pid s.st_line;
      List.iteri
        (fun i a ->
          Printf.bprintf buf "%s  arg %d\n" pad i;
          dump_actual syms buf (indent + 2) a)
        args
  | Return None -> Printf.bprintf buf "%sreturn  [line %d]\n" pad s.st_line
  | Return Some e ->
      Printf.bprintf buf "%sreturn value  [line %d]\n" pad s.st_line;
      dump_expr syms buf (indent + 1) e
  | Stop -> Printf.bprintf buf "%sstop  [line %d]\n" pad s.st_line
  (* E2E-54/P1-m1 §P1-m1.4: bytes modeled on [return value]/[assign] (two spaces
     before the [line] bracket; children one level deeper). The GET designator is
     rendered through the SHARED [dump_designator] with the assignment-target
     rendering (symbol-projection type, pure effect). No H fixture contains
     PUT/GET, so every committed H dump byte is unchanged (T2). *)
  | Put (P_value e) ->
      Printf.bprintf buf "%sput value  [line %d]\n" pad s.st_line;
      dump_expr syms buf (indent + 1) e
  | Put (P_text { text }) ->
      Printf.bprintf buf "%sput literal  [line %d]\n" pad s.st_line;
      Printf.bprintf buf "%s  literal '%s'  [line %d]\n" pad text s.st_line
  | Get d ->
      Printf.bprintf buf "%sget  [line %d]\n" pad s.st_line;
      dump_designator syms buf (indent + 1) Pure (pp_sym_ty syms) s.st_line d

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
      List.iter (dump_stmt p.syms buf 1) pr.body;
      Printf.bprintf buf "END proc(%d)\n" pr.pid)
    p.procs;
  Buffer.contents buf
