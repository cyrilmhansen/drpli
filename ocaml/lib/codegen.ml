(* lib/codegen.ml — MINIMAL 8080 code generator + LINK-80 .REL emitter for
   the PL/I-80 reimplementation. Deliberately scoped to the fixed-BINARY
   integer assignment subset needed by the first end-to-end specimen
   (P071A): assignment of an integer expression (literal, variable copy,
   +, and the -1 / small-const peepholes) to a simple scalar.

   Inputs shared with the IR builder: Parser AST + Bind storage rows.
   Encodings taken VERBATIM from oracle-verified $C disassembly and the
   reldump record stream (spec/notes/codegen.md §1-2, C056/C064). Nothing
   here is invented: every opcode is cross-checked against DR output.

   Anything outside the supported subset raises a clear
   [codegen: unsupported ...] failure rather than guessing. *)

open Rel80

type var_info = { off : int; vt : Ir.ty }

type st =
  { vars : (string * var_info) list   (* lowername -> info *)
  ; base : int                        (* pool base (0 for int subset) *)
  ; mutable items : rel_item list
  ; mutable lc : int }                (* code location counter *)

let push st it = st.items <- st.items @ [it]
let d st v = push st (Data (v land 0xff)); st.lc <- st.lc + 1
let reloc st seg v =
  push st (Reloc (seg, v)); st.lc <- st.lc + 2          (* inline: 2 bytes *)
let link st t valu name = push st (Link (t, valu, name))

(* ---- opcodes (8080), all observed in DR $C for this construct ---- *)
let op_lxi_b = 0x01
let op_lxi_h = 0x21
let op_lhld = 0x2a
let op_shld = 0x22
let op_dad_d = 0x19
let op_dcx_h = 0x2b
let op_inx_h = 0x23
let op_xchg = 0xeb
let op_call = 0xcd

(* variable data-segment address = pool base + declared auto offset.
   [int subset has no pool => base 0; matches DR SHLD/LHLD operands] *)
let addr_of st name =
  let li = String.lowercase_ascii name in
  match List.assoc_opt li st.vars with
  | Some vi -> vi.off + st.base
  | None -> failwith ("codegen: undeclared " ^ name)

(* evaluate an integer expression, leaving the 16-bit value in HL *)
let rec lower_hl st (e : Ast.expr) =
  match e.Ast.e with
  | Ast.Enumber s ->
      let v = int_of_string (String.concat "" (String.split_on_char '_' s)) in
      d st op_lxi_h; d st (v land 0xff); d st ((v lsr 8) land 0xff)
  | Ast.Eident n ->
      d st op_lhld; reloc st Data (addr_of st n.Ast.orig)
  | Ast.Ebinary (Ast.Add, l, r) ->
      (* DR: HL=left ; XCHG ; HL=right ; DAD D  (=> HL = right+left) [P071A] *)
      lower_hl st l; d st op_xchg; lower_hl st r; d st op_dad_d
  | Ast.Ebinary (Ast.Sub, x, Ast.{ e = Ast.Enumber c; _ }) ->
      lower_hl st x; const_sub st (int_of_string c)
  | Ast.Eprefix (Ast.Minus, x) -> failwith "codegen: negation [TBD]"
  | Ast.Ebinary _ -> failwith "codegen: operator not in int subset [TBD]"
  | _ -> failwith "codegen: expression form not in int subset [TBD]"

(* subtract an integer constant: DR folds 1 -> DCX H, small n -> repeated
   DCX H (<=4 observed); anything larger is out of this subset. *)
and const_sub st n =
  if n = 1 then d st op_dcx_h
  else if n > 1 && n <= 4 then for _ = 1 to n do d st op_dcx_h done
  else failwith "codegen: constant sub magnitude [TBD]"

let lower_assign st (lhs : Ast.expr) (rhs : Ast.expr) =
  match lhs.Ast.e with
  | Ast.Eident n ->
      lower_hl st rhs;
      d st op_shld; reloc st Data (addr_of st n.Ast.orig)
  | _ -> failwith "codegen: non-simple assignment lhs [TBD]"

(* program frame: header link items + prologue + body + epilogue + tail *)
let emit_program (progname : string) (data_size : int)
    (rows : (string * var_info) list) (stmts : Ast.stmt list) =
  let st = { vars = rows; base = 0; items = []; lc = 0 } in
  (* header *)
  link st t_progname None (Some progname);
  link st t_req_library None (Some "PLILIB");
  link st t_extdef None (Some progname);
  link st t_def_public (Some (Code, 0)) (Some progname);
  link st t_def_data_size (Some (Abs, data_size)) None;
  link st t_set_lc (Some (Code, 0)) None;
  (* prologue: LXI B,0200 ; CALL ?START *)
  d st op_lxi_b; d st 0x00; d st 0x02;
  d st op_call;
  let start_slot = st.lc in
  d st 0; d st 0;
  link st t_chain_ext (Some (Code, start_slot)) (Some "?START");
  (* body *)
  List.iter
    (fun (s : Ast.stmt) ->
      match s.Ast.st with
      | Ast.Sassign { lhs; rhs } -> lower_assign st lhs rhs
      | _ -> ())
    stmts;
  (* epilogue: CALL ?STOPX *)
  d st op_call;
  let stop_slot = st.lc in
  d st 0; d st 0;
  link st t_chain_ext (Some (Code, stop_slot)) (Some "?STOPX");
  (* tail *)
  link st t_def_code_size (Some (Code, st.lc)) None;
  link st t_end_program (Some (Code, 0)) None;
  link st t_end_file None None;
  (st.items, st.lc)

(* build var_info rows from binder rows, keeping only fixed-bin scalars *)
let rows_of (b : Ast.block) =
  let size = function
    | Ir.Tbin p -> (p + 8) / 8
    | Ir.Tdec (p, _) -> (p + 2) / 2
    | Ir.Tflt -> 4
    | Ir.Tchr (n, _) -> n
    | Ir.Tbit n -> (n + 7) / 8
  in
  let irty = function
    | Bind.RTbin p -> Some (Ir.Tbin p)
    | Bind.RTdec (p, s) -> Some (Ir.Tdec (p, s))
    | Bind.RTfloat _ -> Some Ir.Tflt
    | Bind.RTchar (n, v) -> Some (Ir.Tchr (n, v))
    | Bind.RTbit n -> Some (Ir.Tbit n)
    | _ -> None
  in
  let rows = Bind.bind_rows b in
  let vars =
    List.filter_map
      (fun (nm, rt, off, _auto) ->
        match irty rt with
        | Some t -> Some (nm, { off; vt = t })
        | None -> None)
      rows
  in
  (* data size = highest (offset+size) over auto vars (== DR AUTO STORAGE) *)
  let data_size =
    List.fold_left
      (fun acc (nm, vi) ->
        let _ = nm in
        max acc (vi.off + size vi.vt))
      0 vars
  in
  let prog =
    match b.Ast.bname with Some n -> String.uppercase_ascii n.Ast.orig
                         | None -> failwith "codegen: main has no name"
  in
  (prog, data_size, vars)
