(* ocaml/hir/mir_backend.ml — PL/I HIR -> MIR text (E2E-54/P1-m0 native backend).

   Contract (PLAN §P1-m0.2/.3/.4, brief §5): consume the typed [Hir.program]
   produced by the EXISTING Parser + Bind + Semantic_env + Hir_build pipeline
   (never re-parse PL/I, never read a dump, never bypass Semantic_env) and emit
   a DETERMINISTIC MIR textual artifact for the pinned external object emitter,
   or a typed list of loud refusals. The compile-time witness (module
   constraint + [Backend.Driver] application) lives in pli80mir.ml; the
   [Backend.BACKEND] instance the CLI instantiates is [For (E)] at the bottom.

   Scope is deliberately minimal (brief §3): ONE zero-argument procedure whose
   result is FIXED BINARY(p,0); straight-line assignments, console PUT/GET
   statements (E2E-54/P1-m1 §P1-m1.5) and exactly one final RETURN; constants,
   variable reads, + - * and unary negation. Every other HIR
   node refuses (HIR-E18); every numeric step that can leave the proven-safe
   domain refuses (HIR-E19); every export-shape problem refuses (HIR-E20).
   Nothing is silently dropped: a refusal means NO artifact.

   E2E-54/P1-m1 (§P1-m1.5): a body that carries console statements additionally
   emits the runtime protos (used-only, fixed relative order), exactly ONE
   import line with the used host names in canonical order, the m1b string items
   s<k> (after the import line, before the func item), the st (and a1) locals,
   and the shared Lfail failure tail after the body return. A procedure WITHOUT
   console statements emits the §P1-m0 bytes EXACTLY — the M01/M02/M03 pins and
   the CT2 object-byte law (§P1-m1.6).

   The native carrier is MIR [i64] — a REPRESENTATION CHOICE, not a claim about
   DR integer widths (§P1-m0.3). The profile's UNKNOWN overflow/rounding/float
   fields are honoured by REFUSING outside the statically proved value window
   W(p) = ±(2^(p-1)-1); no wrapping, saturation or trapping is assumed.

   MIR specifics — text syntax, mnemonics, register naming, export symbol shape
   — live HERE and nowhere else (brief §5): Hir.ml and semantic_env.ml never
   mention MIR. This unit is never linked into pli80c.exe (F1 remedy).

   DEVIATION (recorded; PLAN §P1-m0.5 wording): the [Backend.BACKEND] signature
   fixes [compile] to a [~profile] labelled argument plus the program, while
   §P1-m0.2 makes the export NAME part of the subset decision (a mismatch is
   HIR-E20). A runtime string cannot be a module parameter, so [compile] takes
   the export as a third labelled argument and [For] supplies the
   [Backend.BACKEND] instance by closing over a parameter module. The contract
   semantics are unchanged: the backend alone decides, and every MIR-specific
   name still lives only in this unit.

   F8 law (tools/hir_test.py, every ocaml/hir/*.ml after comment strip): no
   byte-layout words, no hex literals, no uppercase 8080 mnemonics; the MIR
   mnemonics used below are lowercase text-format names and never match. *)

module Int_map = Map.Make (struct type t = int let compare = compare end)

(* E2E-54/P1-mD §P1-mD.3: an OPT-IN sidecar debug map, built only when the CLI
   passes ~debug_source:(Some abs_path). [None] on the default path — the .mir
   bytes are then produced exactly as before (§P1-mD.2: default behaviour FROZEN). *)
type artifact = {
  entry_sym : string;
  mir_text : string;
  debug_map : string option;
}

exception Refusal of Diagnostic.t

let refuse ?line code msg = raise (Refusal (Diagnostic.make ?line code msg))

let quote s = "'" ^ s ^ "'"

(* F8 law (measured, this slice): a single uppercase letter in CODE trips the
   8080-mnemonic grep -- both the char literals of an 'A'..'Z' range and a
   one-letter module name. The fold is therefore written on character codes. *)
let lower_name =
  String.map
    (fun c ->
      let n = Char.code c in
      if n >= 65 && n <= 90 then Char.chr (n + 32) else c)

(* §P1-m0.2: the folded procedure name must be usable as a portable MIR symbol
   verbatim; anything else refuses loudly (no invented symbol mangling). *)
let portable_name nm =
  String.length nm > 0
  &&
  let c0 = nm.[0] in
  ((c0 >= 'a' && c0 <= 'z') || c0 = '_')
  && String.for_all (fun c -> (c >= 'a' && c <= 'z') || (c >= '0' && c <= '9') || c = '_') nm

(* Statement kind by NAME (§P1-m0.2 refuses BY NAME; falsifier T10 requires the
   diagnostic to name the construct). Spelled in the HIR dump's own wording. *)
let stmt_kind_name = function
  | Hir.Declare _ -> "declare"
  | Hir.Assign _ -> "assign"
  | Hir.If _ -> "if"
  | Hir.While _ -> "while"
  | Hir.Call_s _ -> "call statement"
  | Hir.Return _ -> "return"
  | Hir.Stop -> "stop"
  (* E2E-54/P1-m1 §P1-m1.4: the two new names for the body-end diagnostic. *)
  | Hir.Put _ -> "put"
  | Hir.Get _ -> "get"

(* §P1-m0.3: the declared-precision value window W(p) of FIXED BINARY(p,0) — the
   same ±(2^(p-1)-1) domain in which the byte-exact bin(15) goldens live. p is
   bounded by the profile ceiling (15), so OCaml int arithmetic on endpoints and
   on the four products below is exact (|v| <= 32767, products <= 2^30). *)
let window p =
  let lim = (1 lsl (p - 1)) - 1 in
  (- lim, lim)

let in_window (lo, hi) (a, b) = lo <= a && b <= hi

let show_iv (a, b) = "[" ^ string_of_int a ^ "," ^ string_of_int b ^ "]"

(* Literal text as written in the source; only a plain non-negative decimal
   integer (no sign, no leading zero, no suffix, at most 9 digits) is accepted
   (§P1-m0.3-1: a non-canonical literal refuses, it is never reinterpreted). *)
let decimal_int (s : string) : int option =
  let digits = String.length s > 0 && String.for_all (fun c -> c >= '0' && c <= '9') s in
  let canonical =
    String.length s <= 9 && (String.length s = 1 || s.[0] <> '0')
  in
  if digits && canonical then Some (int_of_string s) else None

let compile ~(profile : Target.profile) ~(export : string)
    ?(debug_source : string option = None) (prog : Hir.program)
  : (artifact, Diagnostic.t list) result =
  try
    (* ---- export selection (§P1-m0.2): exactly one procedure ---------------- *)
    (match prog.Hir.procs with
     | [] ->
         refuse Diagnostic.e_mir_export
           "MIR backend: the program contains no procedure to export"
     | [ _ ] -> ()
     | _ ->
         refuse Diagnostic.e_mir_export
           "MIR backend: P1-m0 exports exactly one procedure; this program contains \
            more than one (nested procedures and calls are outside the native subset)");
    let p = List.hd prog.Hir.procs in
    let proc_name =
      match p.Hir.name with
      | None ->
          refuse Diagnostic.e_mir_export
            "MIR backend: the entry procedure has no source name"
      | Some nm ->
          let folded = lower_name nm in
          if not (portable_name folded) then
            refuse Diagnostic.e_mir_export
              ("MIR backend: procedure name " ^ quote nm
              ^ " cannot become a portable MIR symbol (letters, digits and '_' only, \
                 starting with a letter or '_')")
          else folded
    in
    (* PL/I name folding: the --export option matches the procedure name without
       regard to case (§P1-m0.2). *)
    if lower_name export <> proc_name then
      refuse Diagnostic.e_mir_export
        ("MIR backend: --export " ^ quote export ^ " selects no procedure of this \
           program; the single entry is named "
        ^ quote (Option.value ~default:"(anonymous)" p.Hir.name));
    if p.Hir.params <> [] then
      refuse Diagnostic.e_mir_export
        ("MIR backend: procedure " ^ quote proc_name ^ " takes parameters; P1-m0 is \
           restricted to zero-argument entries (brief §3)");
    let maxp =
      match profile.Target.max_fixed_precision.value with
      | Some m -> m
      | None ->
          refuse Diagnostic.e_profile
            "MIR backend: the profile leaves the FIXED precision ceiling UNKNOWN; \
             it is never defaulted (target.ml provenance contract)"
    in
    (* the one accepted integer type: FIXED BINARY(p,0) with 1 <= p <= ceiling *)
    let bin_p ?line (t : Hir.ty) : int =
      match t with
      | Hir.Fixed_bin (p_, 0) when p_ >= 1 && p_ <= maxp -> p_
      | _ ->
          refuse ?line Diagnostic.e_mir_node
            ("MIR backend: type " ^ Hir.pp_ty t ^ " is outside the native integer subset \
               (FIXED BINARY(p,0) with 1 <= p <= " ^ string_of_int maxp ^ " only)")
    in
    let ret_p =
      match p.Hir.ret with
      | Some (Hir.Fixed_bin (pr, 0)) when pr >= 1 && pr <= maxp -> pr
      | Some t ->
          refuse Diagnostic.e_mir_export
            ("MIR backend: result type " ^ Hir.pp_ty t ^ " is outside the native subset \
               (a zero-argument FIXED BINARY(p,0) result is required)")
      | None ->
          refuse Diagnostic.e_mir_export
            ("MIR backend: procedure " ^ quote proc_name
            ^ " is a PROCEDURE without a result type; P1-m0 entries must RETURN a \
               FIXED BINARY value (brief §3)")
    in
    (* ---- emission state (a pure function of the program: deterministic) ---- *)
    (* E2E-54/P1-mD: each emitted instruction carries the PL/I source line it
       came from (already available as [st_line]/[ex_line] at every call site).
       The .mir assembly DROPS the line, so the bytes are FROZEN (§P1-mD.2); the
       line rides only into the sidecar. Default [line] is 0 (unlocated). *)
    let insns : (string * int) list ref = ref [] in
    let emit ?(line = 0) fmt =
      Printf.ksprintf (fun s -> insns := (s, line) :: !insns) fmt
    in
    let tmp_n = ref 0 in
    let fresh () =
      incr tmp_n;
      "t" ^ string_of_int !tmp_n
    in
    (* E2E-54/P1-m2 §P1-m2.2: control-flow label names Lthen<n>/Lelse<n>/Ljoin<n>/
       Lh<n>/Lx<n> come from their OWN counter (statement order, from 1), NEVER
       from the temp counter; MIR label scope is the whole module, so the names
       are collision-free by construction. The shared console failure tail keeps
       its single `Lfail`: control flow never emits, reuses or shadows it. *)
    let cf_n = ref 0 in
    (* §P1-m1.5 item 3 (m1b): the module's string data items s<k>, numbered by FIRST
       USE of each DISTINCT literal text in BODY order — a pure function of the typed
       body, so the artifact is deterministic. Only '"' and backslash are escaped; that
       is exactly what the pinned emitter decodes (measured in probe2). *)
    let string_items = ref [] in
    let string_label (text : string) : string =
      match List.assoc_opt text !string_items with
      | Some lbl -> lbl
      | None ->
          let lbl = "s" ^ string_of_int (List.length !string_items + 1) in
          string_items := (text, lbl) :: !string_items;
          lbl
    in
    let escape_text (text : string) : string =
      let b = Buffer.create (String.length text + 2) in
      String.iter
        (fun c ->
          if c = '"' then Buffer.add_string b "\\\""
          else if c = '\\' then Buffer.add_string b "\\\\"
          else Buffer.add_char b c)
        text;
      Buffer.contents b
    in
    (* declared local registers: sid -> declared precision (§P1-m0.4) *)
    let declared = ref Int_map.empty in
    let find_sym sid =
      match List.find_opt (fun (s : Hir.sym) -> s.Hir.sid = sid) prog.Hir.syms with
      | Some s -> s
      | None ->
          refuse Diagnostic.e_mir_node
            ("MIR backend: sym(" ^ string_of_int sid
            ^ ") is used but carries no symbol row in the program")
    in
    let declare sid line =
      if Int_map.mem sid !declared then
        refuse ~line Diagnostic.e_mir_node
          ("MIR backend: sym(" ^ string_of_int sid
          ^ ") is declared twice in this body (re-declaration is not modelled)")
      else begin
        let s = find_sym sid in
        if s.Hir.scope <> p.Hir.scope then
          refuse ~line Diagnostic.e_mir_node
            ("MIR backend: sym(" ^ string_of_int sid
            ^ ") belongs to a different scope than the entry procedure (nested block \
               scoping is outside the native subset)");
        (match s.Hir.sstorage with
         | Hir.Auto -> ()
         | st ->
             refuse ~line Diagnostic.e_mir_node
               ("MIR backend: sym(" ^ string_of_int sid ^ ") has storage "
               ^ Hir.pp_storage st
               ^ "; P1-m0 lowers automatic locals only (STATIC initial values are \
                  unmeasured [TBD])"));
        let sp = bin_p ~line s.Hir.sty in
        declared := Int_map.add sid sp !declared
      end
    in
    (* ---- expression lowering: one register plus the exact interval ---------- *)
    (* Every value ends in a freshly named temp (§P1-m0.4); the interval is the
       EXACT closed integer interval of §P1-m0.3, computed on a straight-line
       walk so it is a proof and not an approximation. A node's own declared
       type fixes the window it must stay inside (§P1-m0.3-2). *)
    let rec lower env (e : Hir.expr) : string * (int * int) =
      let line = e.Hir.ex_line in
      let win () = window (bin_p ~line e.Hir.ex_ty) in
      let prove w iv what =
        if in_window w iv then iv
        else
          refuse ~line Diagnostic.e_mir_numeric
            (what ^ " can reach " ^ show_iv iv ^ ", leaving the declared-precision \
               window " ^ show_iv w ^ " of " ^ Hir.pp_ty e.Hir.ex_ty
            ^ "; overflow behaviour is profile-UNKNOWN and is never assumed (brief §4)")
      in
      if e.Hir.ex_ef = Hir.Unknown_ef then
        refuse ~line Diagnostic.e_mir_node
          "MIR backend: an expression with unknown effects (a call) is outside the \
             native subset";
      match e.Hir.ex with
      (* The NODE class is judged before the type, so a refused construct always
         names itself (§P1-m0.2: the chosen code names the PRIMARY reason). *)
      | Hir.Convert { from; to_ty; _ } ->
          refuse ~line Diagnostic.e_mir_numeric
            ("MIR backend: conversion " ^ Hir.pp_ty from ^ " -> " ^ Hir.pp_ty to_ty
            ^ " is outside the proven-safe domain (fixed-point conversion rounding and \
               overflow are profile-UNKNOWN; §P1-m0.3 refuses, never guesses)")
      | Hir.Call_e _ ->
          refuse ~line Diagnostic.e_mir_node
            "MIR backend: a value-position call is outside the native subset (brief §3)"
      | Hir.Elem_read _ ->
          refuse ~line Diagnostic.e_mir_node
            "MIR backend: an array element read is outside the native subset (brief §3)"
      | Hir.Elem_ref _ ->
          refuse ~line Diagnostic.e_mir_node
            "MIR backend: a dead element-designation node reached value lowering \
               (semtest I8 law)"
      | Hir.Const { text } ->
          let w = win () in
          (match decimal_int text with
           | Some v ->
               let civ = prove w (v, v) ("the literal " ^ quote text) in
               let k = fresh () in
               emit ~line "mov %s, %d" k v;
               (k, civ)
           | None ->
               refuse ~line Diagnostic.e_mir_numeric
                 ("MIR backend: literal text " ^ quote text
                 ^ " is not a plain non-negative decimal integer; the native subset \
                    refuses any literal it cannot prove (brief §4)"))
      | Hir.Var { sid; _ } ->
          let w = win () in
          if not (Int_map.mem sid !declared) then
            refuse ~line Diagnostic.e_mir_node
              ("MIR backend: sym(" ^ string_of_int sid
              ^ ") is read but was never declared in this body");
          (match Int_map.find_opt sid env with
           | Some civ ->
               let v = prove w civ ("the value of sym(" ^ string_of_int sid ^ ")") in
               let k = fresh () in
               emit ~line "mov %s, v%d" k sid;
               (k, v)
           | None ->
               (* §P1-m2.8 item 0: the reason is PATH truth — with joins a symbol can
                  lose its definite value even though the body is walked once; the
                  message names the join law, never a straight-line fiction. *)
               refuse ~line Diagnostic.e_mir_numeric
                 ("MIR backend: uninitialized read of sym(" ^ string_of_int sid
                 ^ "); the symbol is not definitely initialized on every reachable \
                   path (straight-line law §P1-m0.2, join law §P1-m2.2); reading an \
                   undefined value is outside the proven-safe domain (brief §4)"))
      | Hir.Bin { op; left; right; _ } ->
          let w = win () in
          let nm =
            match op with
            | Hir.Add -> "add"
            | Hir.Sub -> "sub"
            | Hir.Mul -> "mul"
            | _ ->
                refuse ~line Diagnostic.e_mir_node
                  ("MIR backend: operator " ^ quote (Hir.pp_binop op)
                  ^ " is outside the native subset (integer + - * only; a relational \
                     result is a condition value, brief §3)")
          in
          if left.Hir.ex_ty <> e.Hir.ex_ty || right.Hir.ex_ty <> e.Hir.ex_ty then
            refuse ~line Diagnostic.e_mir_numeric
              ("MIR backend: operands typed " ^ Hir.pp_ty left.Hir.ex_ty ^ " / "
              ^ Hir.pp_ty right.Hir.ex_ty ^ " against result " ^ Hir.pp_ty e.Hir.ex_ty
              ^ " would require an uncharacterized conversion (profile rounding and \
                 overflow UNKNOWN, brief §4)");
          (* evaluation order = HIR order: left before right (§P1-m0.4) *)
          let rl, il = lower env left in
          let rr, ir = lower env right in
          let iv =
            match op with
            | Hir.Add -> (fst il + fst ir, snd il + snd ir)
            | Hir.Sub -> (fst il - snd ir, snd il - fst ir)
            | Hir.Mul ->
                let c1 = fst il * fst ir
                and c2 = fst il * snd ir
                and c3 = snd il * fst ir
                and c4 = snd il * snd ir in
                (min (min c1 c2) (min c3 c4), max (max c1 c2) (max c3 c4))
            | _ -> assert false
          in
          let v =
            prove w iv
              ("binop " ^ quote (Hir.pp_binop op) ^ " on operands proved within "
              ^ show_iv il ^ " and " ^ show_iv ir)
          in
          let k = fresh () in
          emit ~line "%s %s, %s, %s" nm k rl rr;
          (k, v)
      | Hir.Neg { e = inner } ->
          let w = win () in
          let ri, iiv = lower env inner in
          let niv = (- (snd iiv), - (fst iiv)) in
          let v = prove w niv ("the negation of " ^ show_iv iiv) in
          let k = fresh () in
          emit ~line "neg %s, %s" k ri;
          (k, v)
    in
    (* ---- E2E-54/P1-m2: conditions, joins, arms (§P1-m2.2) ------------------- *)
    (* The join law (brief §3): a variable is definitely initialized only when
       initialized on EVERY incoming path (Some + Some -> sound hull; any None
       side DROPS the entry — assignments made only in one arm are never
       inherited). Int_map is immutable, so passing [env] into an arm IS the
       copy: the arms never share mutable state. *)
    let join_env (a : (int * int) Int_map.t) (b : (int * int) Int_map.t) =
      Int_map.merge
        (fun _k x y ->
          match (x, y) with
          | Some (a1, a2), Some (b1, b2) -> Some (min a1 b1, max a2 b2)
          | _ -> None)
        a b
    in
    (* Branch mnemonics and the label-first operand order are the hop-1 PROVEN
       pinned-parser forms (`blt L, x, y` / `bge L, x, y` executed; the table is
       documented in MIR.md; the unproven rows are MEASURED-FIRST at fixtures).
       The relational node comes from hir_build's condition lowering ONLY
       (typing "language-rule:relational", ex_ty Condty); its Condty never
       reaches bin_p — each operand keeps its OWN declared-window proof inside
       the existing `lower`. *)
    let relop_cc (op : Hir.binop) : string option =
      match op with
      | Hir.Eq -> Some "eq"
      | Hir.Ne -> Some "ne"
      | Hir.Lt -> Some "lt"
      | Hir.Le -> Some "le"
      | Hir.Gt -> Some "gt"
      | Hir.Ge -> Some "ge"
      | _ -> None
    in
    let invert_cc cc =
      match cc with
      | "lt" -> "ge"
      | "le" -> "gt"
      | "gt" -> "le"
      | "ge" -> "lt"
      | "eq" -> "ne"
      | "ne" -> "eq"
      | _ -> assert false
    in
    let lower_cond ?(inverted = false) env (e : Hir.expr) (target : string) : unit =
      let line = e.Hir.ex_line in
      match e.Hir.ex with
      | Hir.Bin { op; left; right; _ } when e.Hir.ex_ty = Hir.Condty ->
          (match relop_cc op with
           | None ->
               refuse ~line Diagnostic.e_mir_node
                 ("MIR backend: a condition with operator " ^ quote (Hir.pp_binop op)
                 ^ " is outside the P1-m2 subset (only the six relational comparisons, \
                    brief §2)")
           | Some cc ->
               let cc = if inverted then invert_cc cc else cc in
               (* evaluation order = HIR order: left before right (§P1-m0.4) *)
               let rl, _il = lower env left in
               let rr, _ir = lower env right in
               emit ~line "b%s %s, %s, %s" cc target rl rr)
      | _ ->
          refuse ~line Diagnostic.e_mir_node
            "MIR backend: a condition that is not a relational comparison of proved \
               integer operands is outside the P1-m2 subset (a condition literal is \
               NOT admitted in this slice; brief §2)"
    in
    (* Early/nested RETURN stays outside the subset (§P1-m2.2): the ONE final
       top-level RETURN(expr) law is unchanged. A structural scan refuses it BY
       NAME before any arm instruction is emitted. *)
    let rec no_return_in (arm : Hir.stmt list) : unit =
      List.iter
        (fun (s : Hir.stmt) ->
          match s.Hir.st with
          | Hir.Return _ ->
              refuse ~line:s.Hir.st_line Diagnostic.e_mir_node
                "MIR backend: a RETURN nested inside a conditional or loop arm is \
                   outside the P1-m2 subset (only the one final top-level RETURN(expr) \
                   is admitted; brief §3)"
          | Hir.If { cond = _; then_; else_ } ->
              no_return_in then_;
              no_return_in else_
          | Hir.While { cond = _; body = b } -> no_return_in b
          | _ -> ())
        arm
    in
    (* ---- E2E-54/P1-m2 §P1-m2.3: the counted DO WHILE machinery -------------- *)
    (* Every recognition step is a pure structural scan (NO emission) and runs
       BEFORE any instruction is committed; a refused loop therefore emits
       nothing at all. The exact exit value comes from the §P1-m2.3-5 formula
       (exact integer arithmetic; the ceiling p <= 15 keeps every product
       inside OCaml int). The guard is lowered INSIDE the header — never
       peeled — so it re-evaluates EVERY iteration; the backedge jmp is
       mandatory; header/post env carry the IV at its exact exit value and
       DROP every other body-written symbol (drop-not-inherit, §P1-m2.2 law
       reused). CFN6 ordering law (hop-3 PROPOSED, binding): the step Assign
       window check inside the body lowering must be the FIRST refusal a
       window-escaping loop hits, before the explicit orbit check and before
       any guard check — the guard operand proofs are pre-computed in a
       DISCARDED pass (no emission, temp counter rewound) so lowering the
       guard in the header env can never refuse first. *)
    let rec walk_expr (e : Hir.expr) (f : Hir.expr -> unit) : unit =
      f e;
      match e.Hir.ex with
      | Hir.Bin { left; right; _ } ->
          walk_expr left f;
          walk_expr right f
      | Hir.Neg { e = inner }
      | Hir.Convert { e = inner; _ }
      | Hir.Elem_read { subs = inner :: _; _ } ->
          walk_expr inner f
      | _ -> ()
    in
    let rec walk_stmts (ss : Hir.stmt list) (f : Hir.stmt -> unit) : unit =
      List.iter
        (fun (s : Hir.stmt) ->
          f s;
          match s.Hir.st with
          | Hir.If { then_; else_; _ } ->
              walk_stmts then_ f;
              walk_stmts else_ f
          | Hir.While { body; _ } -> walk_stmts body f
          | _ -> ())
        ss
    in
    (* statement-level WRITE of a scalar sid (assignment and GET target) *)
    let stmt_write ?line (s : Hir.stmt) : int option =
      let target =
        match s.Hir.st with
        | Hir.Assign { target; _ } -> Some target
        | Hir.Get d -> Some d
        | _ -> None
      in
      match target with
      | Some (Hir.D_var { sid }) -> Some sid
      | Some (Hir.D_elem { base = _; _ }) ->
          refuse ?line Diagnostic.e_mir_node
            "MIR backend: an array designation inside a loop body is outside the \
               native subset (brief §3)"
      | _ -> None
    in
    (* guard comparison mnemonic for the FOUR provable monotonic relations ONLY
       (Eq/Ne cannot prove a monotonic exit, §P1-m2.3-1; inversion table §P1-m2.2) *)
    let guard_cc (op : Hir.binop) : string option =
      match op with
      | Hir.Lt -> Some "lt"
      | Hir.Le -> Some "le"
      | Hir.Gt -> Some "gt"
      | Hir.Ge -> Some "ge"
      | _ -> None
    in
    (* §P1-m2.3-5 exact exit value; ZERO iterations iff iv0 already fails the guard *)
    let zero_iterations (c : int) (t0 : int) (iv0 : int) : bool =
      if c > 0 then iv0 >= t0 else iv0 <= t0
    in
    let exit_value (c : int) (t0 : int) (iv0 : int) : int =
      if zero_iterations c t0 iv0 then iv0
      else if c > 0 then
        (* iv0 < t0: ceil((t0 - iv0) / c), exact on ints *)
        let d = t0 - iv0 in
        iv0 + (c * ((d + c - 1) / c))
      else
        (* c < 0, iv0 > t0: ceil((iv0 - t0) / -c), exact on ints *)
        let d = iv0 - t0 in
        let m = -c in
        iv0 - (m * ((d + m - 1) / m))
    in
    (* ---- statements (§P1-m0.2: declare / assign / exactly one final return) -- *)
    let body = p.Hir.body in
    if body = [] then
      refuse Diagnostic.e_mir_node
        "MIR backend: the entry procedure has an empty body (no return to lower)";
    (match List.rev body with
     | { Hir.st = Hir.Return (Some _); _ } :: _ -> ()
     | { Hir.st = Hir.Return None; st_line } :: _ ->
         refuse ~line:st_line Diagnostic.e_mir_node
           "MIR backend: the body must end with RETURN(expr); a bare return leaves the \
              result undefined (implicit results are unmeasured [TBD])"
     | { Hir.st; st_line } :: _ ->
         refuse ~line:st_line Diagnostic.e_mir_node
           ("MIR backend: the body must end with RETURN(expr); fall-through semantics \
              are unmeasured [TBD] (found " ^ quote (stmt_kind_name st) ^ ")")
     | [] -> assert false);
    let rec lower_stmts env = function
      | [] -> env
      | s :: rest ->
          let line = s.Hir.st_line in
          match s.Hir.st with
          | Hir.Declare sid ->
              declare sid line;
              lower_stmts env rest
          | Hir.Assign { target; value } ->
              (match target with
               | Hir.D_elem _ ->
                   refuse ~line Diagnostic.e_mir_node
                     "MIR backend: assignment to an array element is outside the native \
                        subset (brief §3)"
               | Hir.D_var { sid } ->
                   if not (Int_map.mem sid !declared) then
                     refuse ~line Diagnostic.e_mir_node
                       ("MIR backend: assignment to sym(" ^ string_of_int sid
                       ^ ") which was never declared in this body");
                   let rv, iv = lower env value in
                   let sp = Int_map.find sid !declared in
                   if not (in_window (window sp) iv) then
                     refuse ~line Diagnostic.e_mir_numeric
                       ("MIR backend: the value stored into sym(" ^ string_of_int sid
                       ^ ") can reach " ^ show_iv iv ^ ", leaving the window "
                       ^ show_iv (window sp) ^ " of its declared type "
                       ^ Hir.pp_ty (Hir.Fixed_bin (sp, 0)) ^ " (brief §4)");
                   emit ~line "mov v%d, %s" sid rv;
                   lower_stmts (Int_map.add sid iv env) rest)
          | Hir.Return (Some e) ->
              (* Reachable only as the FINAL statement (checked above), so [rest] is
                 empty and the recursion below simply returns the environment. *)
              let rv, ev = lower env e in
              let rw = window ret_p in
              if not (in_window rw ev) then
                refuse ~line Diagnostic.e_mir_numeric
                  ("MIR backend: the returned value can reach " ^ show_iv ev
                  ^ ", leaving the window " ^ show_iv rw
                  ^ " of the declared result type " ^ Hir.pp_ty (Hir.Fixed_bin (ret_p, 0))
                  ^ " (§P1-m0.3-3, brief §4)");
              emit ~line "ret %s" rv;
              lower_stmts env rest
          | Hir.Return None ->
              refuse ~line Diagnostic.e_mir_node
                "MIR backend: return with no value (see the final-statement check)"
          | Hir.If { cond; then_; else_ } ->
              (* §P1-m2.2: the PROVEN branch forms; both arms lower in independent
                 copies of the pre-if env and the join drops everything the arms
                 disagree about (drop-not-inherit). A missing ELSE is the identity
                 path. Statement order is preserved; every emitted instruction —
                 branches, jumps and labels included — carries the IF statement's
                 source line (§P1-m2.9, sidecar law). *)
              no_return_in then_;
              no_return_in else_;
              incr cf_n;
              let sfx = string_of_int !cf_n in
              if else_ = [] then begin
                lower_cond ~inverted:true env cond ("Ljoin" ^ sfx);
                let env_then = lower_stmts env then_ in
                emit ~line "Ljoin%s:" sfx;
                lower_stmts (join_env env_then env) rest
              end
              else begin
                let lthen = "Lthen" ^ sfx in
                let lelse = "Lelse" ^ sfx in
                let ljoin = "Ljoin" ^ sfx in
                lower_cond env cond lthen;
                emit ~line "jmp %s" lelse;
                emit ~line "%s:" lthen;
                let env_t = lower_stmts env then_ in
                emit ~line "jmp %s" ljoin;
                emit ~line "%s:" lelse;
                let env_e = lower_stmts env else_ in
                emit ~line "%s:" ljoin;
                lower_stmts (join_env env_t env_e) rest
              end
          | Hir.While { cond; body } ->
              (* §P1-m2.3: the recognized counted loop; every refusal names itself
                 BEFORE any instruction is committed. Label counter shared with m2a:
                 loop k gets Lh<k>/Lx<k> (hop-1 fact 1.2: MIR label scope is the whole
                 module, so names are collision-free by construction). *)
              let line_guard = cond.Hir.ex_line in
              let refuse_shape msg =
                refuse ~line:line_guard Diagnostic.e_mir_node
                  ("MIR backend: DO WHILE loop outside the proven counted-loop subset: "
                  ^ msg ^ " (§P1-m2.3)")
              in
              let refuse_numeric msg =
                refuse ~line:line_guard Diagnostic.e_mir_numeric
                  ("MIR backend: DO WHILE loop refused: " ^ msg ^ " (§P1-m2.3)")
              in
              (match cond.Hir.ex with
              | Hir.Bin { op; left; right; _ } when cond.Hir.ex_ty = Hir.Condty ->
                  (* (1) guard shape: Var sid OP expr_B, OP in {Lt,Le,Gt,Ge}
                     (Eq/Ne cannot prove a monotonic exit, §P1-m2.3-1) *)
                  let iv =
                    match left.Hir.ex with
                    | Hir.Var { sid; addressable = _ } -> sid
                    | _ ->
                        refuse_shape
                          "the left guard operand is not a simple variable read (the \
                             induction variable must be a scalar symbol)"
                  in
                  let cc =
                    match guard_cc op with
                    | Some cc -> cc
                    | None ->
                        refuse_shape
                          ("the guard comparison " ^ quote (Hir.pp_binop op)
                          ^ " cannot prove a monotonic exit (only < <= > >= guards are \
                             admitted)")
                  in
                  (* (2) IV definitely initialized to ONE proven constant before the
                     loop (§P1-m2.3-2; the pre-loop env entry is the proof — the
                     constant and Neg forms all arrive as point intervals) *)
                  let iv0 =
                    match Int_map.find_opt iv env with
                    | None ->
                        refuse_numeric
                          ("the induction variable sym(" ^ string_of_int iv
                          ^ ") is not definitely initialized on every reachable path \
                             before the loop (uninitialized induction variable — the \
                             counted-loop proof needs its exact start value)")
                    | Some (lo0, hi0) when lo0 <> hi0 ->
                        refuse_shape
                          ("the induction variable sym(" ^ string_of_int iv
                          ^ ") starts from the interval " ^ show_iv (lo0, hi0)
                          ^ ", not a single proven constant")
                    | Some (v0, _) -> v0
                  in
                  (* (3) body scans BEFORE any emission (§P1-m2.3-3): early/nested
                     RETURN, nested loops, every bodyWriter, and the EXACTLY-ONE
                     recognized monotonic step write *)
                  no_return_in body;
                  let nested = ref None in
                  walk_stmts body (fun s ->
                    match s.Hir.st with
                    | Hir.While _ ->
                        if !nested = None then nested := Some s.Hir.st_line
                    | _ -> ());
                  (match !nested with
                   | None -> ()
                   | Some nl ->
                       refuse ~line:nl Diagnostic.e_mir_node
                         "MIR backend: a loop nested inside a DO WHILE body is outside \
                            the proven counted-loop subset (nested loops are not \
                            admitted; §P1-m2.3)");
                  let writers = ref [] in
                  let add_writer sid =
                    if sid <> iv && not (List.mem sid !writers) then
                      writers := sid :: !writers
                  in
                  let bad_step = ref None in
                  let step_c = ref None in
                  let nsteps = ref 0 in
                  walk_stmts body (fun s ->
                    match stmt_write ~line:s.Hir.st_line s with
                    | Some sid when sid = iv ->
                        incr nsteps;
                        let recognized =
                          match s.Hir.st with
                          | Hir.Assign { target = Hir.D_var _; value = ve } -> (
                              match ve.Hir.ex with
                              | Hir.Bin { op = bop; left = le; right = re; _ }
                                when bop = Hir.Add || bop = Hir.Sub -> (
                                  match (le.Hir.ex, re.Hir.ex) with
                                  | (Hir.Var { sid = ls; _ }, Hir.Const { text }) -> (
                                      match decimal_int text with
                                      | Some cv when cv > 0 && ls = iv ->
                                          Some (if bop = Hir.Add then cv else (0 - cv))
                                      | _ -> None)
                                  | _ -> None)
                              | _ -> None)
                          | _ -> None
                        in
                        (match recognized with
                         | Some cv -> if !step_c = None then step_c := Some cv
                         | None ->
                             if !bad_step = None then bad_step := Some s.Hir.st_line)
                    | Some sid -> add_writer sid
                    | None -> ());
                  if !nsteps <> 1 then
                    refuse ~line Diagnostic.e_mir_node
                      ("MIR backend: the loop body must write the induction variable \
                         sym(" ^ string_of_int iv ^ ") EXACTLY ONCE in the recognized \
                         step form; found " ^ string_of_int !nsteps
                      ^ " write(s) (§P1-m2.3-3: the counted-loop proof refuses every \
                         other body write to the induction variable by name)");
                  (match !bad_step with
                   | None -> ()
                   | Some sl ->
                       refuse ~line:sl Diagnostic.e_mir_node
                         "MIR backend: the loop body writes the induction variable \
                            outside the recognized monotonic step form (i = i + n or \
                            i = i - n with a positive literal step n, §P1-m2.3-3)");
                  let c =
                    match !step_c with
                    | Some cv -> cv
                    | None -> assert false
                    (* nsteps = 1 with no bad write: the recognized form was seen *)
                  in
                  (* (4) direction match (§P1-m2.3-4) *)
                  let dir_ok =
                    (c > 0 && (cc = "lt" || cc = "le"))
                    || (c < 0 && (cc = "gt" || cc = "ge"))
                  in
                  if not dir_ok then
                    refuse_shape
                      ("the guard direction " ^ quote (Hir.pp_binop op)
                      ^ " does not match the step sign (a non-terminating form the \
                         proof cannot discharge)");
                  (* (5) the bound reads NOTHING the body moves — every other
                     bodyWriter AND the induction variable itself (a bound that
                     reads the IV is not constant across iterations: the shape is
                     refused, hop-3 PROPOSED point-bound restriction) — and lowers
                     to a CONSTANT POINT interval in the pre-loop env. The guard
                     operands' own window proofs are pre-computed in a DISCARDED
                     pass (buffer and temp counter rewound; the identical pass runs
                     again inside the header below) so the real guard lowering can
                     never refuse BEFORE the body's step check — CFN6 ordering law
                     (§P1-m2.3-6, hop-3 PROPOSED, binding). *)
                  let bound_reads_moved = ref None in
                  walk_expr right (fun en ->
                    match en.Hir.ex with
                    | Hir.Var { sid; _ } when sid = iv || List.mem sid !writers ->
                        if !bound_reads_moved = None then
                          bound_reads_moved := Some sid
                    | _ -> ());
                  (match !bound_reads_moved with
                   | None -> ()
                   | Some bs ->
                       refuse_shape
                         ("the guard bound reads sym(" ^ string_of_int bs
                         ^ "), which the loop itself writes — the bound must be a \
                            proven constant the body cannot move (§P1-m2.3-1)"));
                  let insns_save = !insns in
                  let tmp_save = !tmp_n in
                  insns := [];
                  let (_ : string * (int * int)) = lower env left in
                  let (_, (blo, bhi)) = lower env right in
                  insns := insns_save;
                  tmp_n := tmp_save;
                  if blo <> bhi then
                    refuse_shape
                      ("the guard bound is proved only within the interval "
                      ^ show_iv (blo, bhi)
                      ^ ", not a single proven constant (point-bound restriction, \
                         hop-3 decision)");
                  let b = blo in
                  (* (6) first failing guard value T and the EXACT exit (§P1-m2.3-5,
                     exact integer arithmetic; p <= 15 keeps every product in int) *)
                  let t0 =
                    if c > 0 then if cc = "lt" then b else b + 1
                    else if cc = "gt" then b
                    else b - 1
                  in
                  let exit_v = exit_value c t0 iv0 in
                  (* loop-state discipline (§P1-m2.3): the header env carries the IV
                     at its exact exit value and DROPS every other body-written sid
                     (drop-not-inherit); inside the body the IV is refined to the
                     guard-admitted interval — sound over-approximation by the
                     monotonic direction (Lt [iv0,T-1], Le [iv0,T], Gt [T+1,iv0],
                     Ge [T,iv0] as pre-registered); when that interval is EMPTY the
                     loop takes ZERO iterations, the body is unreachable, and the
                     body env carries the exit point instead — values are still
                     checked (hop-3 PROPOSED) *)
                  let raw_refine =
                    match cc with
                    | "lt" -> (iv0, t0 - 1)
                    | "le" -> (iv0, t0)
                    | "gt" -> (t0 + 1, iv0)
                    | _ (* "ge" *) -> (t0, iv0)
                  in
                  let body_iv =
                    if fst raw_refine > snd raw_refine then (exit_v, exit_v)
                    else raw_refine
                  in
                  let header_env =
                    List.fold_left
                      (fun acc w -> Int_map.remove w acc)
                      env !writers
                  in
                  let header_env = Int_map.add iv (exit_v, exit_v) header_env in
                  let body_env = Int_map.add iv body_iv header_env in
                  (* (7) VERIFICATION body pass (CFN6 ordering law): the step
                     Assign's own window check is the FIRST refusal a window-escaping
                     loop hits — before the orbit check and before any guard check.
                     This pass is DISCARDED (buffer, temp counter AND label counter
                     rewound — an If inside a verified body must not consume a cf_n
                     number invisibly: §P1-m2.2 counts IF statements in source order
                     densely); the emission below re-lowers the identical code so
                     t<k stay in EVALUATION ORDER (guard before body, §P1-m0.4 law) *)
                  incr cf_n;
                  let sfx = string_of_int !cf_n in
                  let outer = !insns in
                  let tmp_base = !tmp_n in
                  let cf_base = !cf_n in
                  insns := [];
                  let (_ : (int * int) Int_map.t) = lower_stmts body_env body in
                  insns := outer;
                  tmp_n := tmp_base;
                  cf_n := cf_base;
                  (* (8) explicit orbit check (belt-and-suspenders AFTER the body
                     lowering, §P1-m2.3-6): every value the induction variable
                     takes — start, every body value, every step result and the
                     exact exit — lies inside W(p) of its declared precision *)
                  let sp = Int_map.find iv !declared in
                  let w_iv = window sp in
                  let orbit =
                    if exit_v = iv0 then (iv0, iv0)
                    else if c > 0 then (iv0, max exit_v (snd body_iv + c))
                    else (min exit_v (snd body_iv + c), iv0)
                  in
                  if not (in_window w_iv orbit) then
                    refuse_numeric
                      ("the induction variable sym(" ^ string_of_int iv
                      ^ ") is proved to reach " ^ show_iv orbit
                      ^ " across the loop orbit (start, body, step and exit values), \
                         leaving the window " ^ show_iv w_iv
                      ^ " of its declared type "
                      ^ Hir.pp_ty (Hir.Fixed_bin (sp, 0)) ^ " (brief §4)");
                  (* (9) EMISSION passes, in evaluation order: guard first in the
                     header env (the IV read carries [exit,exit], ⊆ W by the orbit
                     check, so this lowering CANNOT refuse — the discarded proofs
                     above are the same computations), then the body *)
                  insns := [];
                  lower_cond ~inverted:true header_env cond ("Lx" ^ sfx);
                  let guard_insns = !insns in
                  insns := [];
                  let (_ : (int * int) Int_map.t) = lower_stmts body_env body in
                  let body_insns = !insns in
                  (* (10) splice in the PROVEN emission order (hop-1 probe_loop.mir,
                     executed value 3): Lh, guard (re-evaluated EVERY iteration),
                     body, mandatory backedge jmp, Lx; every instruction rides the
                     loop statement's source line (§P1-m2.9 sidecar law) *)
                  insns := outer;
                  emit ~line "Lh%s:" sfx;
                  List.iter
                    (fun (txt, l) -> emit ~line:l "%s" txt)
                    (List.rev guard_insns);
                  List.iter
                    (fun (txt, l) -> emit ~line:l "%s" txt)
                    (List.rev body_insns);
                  emit ~line "jmp Lh%s" sfx;
                  emit ~line "Lx%s:" sfx;
                  (* the header env IS the post-loop env: IV = [exit,exit]; every
                     other body-written sid stays DROPPED (zero-iteration path) *)
                  lower_stmts header_env rest
              | _ ->
                  refuse ~line:line_guard Diagnostic.e_mir_node
                    "MIR backend: a DO WHILE guard that is not a relational comparison \
                       of proved integer operands is outside the counted-loop subset \
                       (a condition literal is not admitted; §P1-m2.3)")
          | Hir.Call_s _ ->
              refuse ~line Diagnostic.e_mir_node
                "MIR backend: a call statement is outside the native subset (brief §3)"
          | Hir.Stop ->
              refuse ~line Diagnostic.e_mir_node
                "MIR backend: stop is outside the native subset (startup and end \
                   semantics are out of scope, brief §3)"
          | Hir.Put src ->
              (* §P1-m1.5 (m1a): the lowered value goes through the raw runtime put
                 (the runtime never adds a newline); the BACKEND closes every PUT
                 statement with a statement-level newline call. EVERY console call
                 is followed by its OWN status branch to the shared failure tail. *)
              (match src with
               | Hir.P_value e ->
                   let rv, _iv = lower env e in
                   emit ~line "call p_put, pli_console_put_i64, st, %s" rv;
                   emit ~line "bne Lfail, st, 0";
                   emit ~line "call p_nl, pli_console_put_nl, st";
                   emit ~line "bne Lfail, st, 0";
                   lower_stmts env rest
               | Hir.P_text { text } ->
                   (* §P1-m1.5 item 5 (m1b, PROVEN probe2 shape): the literal's
                      CHARACTER COUNT rides an immediate into a fresh temp; the text
                      itself is a module string item s<k>. The runtime put_text emits
                      NO newline, so the statement closes with p_nl exactly like a
                      value put; the status branch is this call's own. *)
                   let char_count = String.length text in
                   let len_reg = fresh () in
                   let s_lbl = string_label text in
                   emit ~line "mov %s, %d" len_reg char_count;
                   emit ~line "call p_text, pli_console_put_text, st, %s, %s" s_lbl len_reg;
                   emit ~line "bne Lfail, st, 0";
                   emit ~line "call p_nl, pli_console_put_nl, st";
                   emit ~line "bne Lfail, st, 0";
                   lower_stmts env rest)
          | Hir.Get d ->
              (* §P1-m1.5: the single get slot a1 is stack-allocated per GET
                 statement (measured probe2 pattern); the runtime call carries the
                 status register, the slot and the target's declared window, and
                 only a zero status stores the value into v<sid>. *)
              (match d with
               | Hir.D_elem _ ->
                   refuse ~line Diagnostic.e_mir_node
                     "MIR backend: a console GET of an array designation is outside \
                        the native subset (HIR lowering refuses every such target at \
                        HIR-E21; defensive witness)"
               | Hir.D_var { sid } ->
                   if not (Int_map.mem sid !declared) then
                     refuse ~line Diagnostic.e_mir_node
                       ("MIR backend: assignment to sym(" ^ string_of_int sid
                       ^ ") which was never declared in this body");
                   let sp = Int_map.find sid !declared in
                   let lo, hi = window sp in
                   emit ~line "alloca a1, 8";
                   emit ~line "call p_get, pli_console_get_i64, st, a1, %d, %d" lo hi;
                   emit ~line "bne Lfail, st, 0";
                   emit ~line "mov v%d, i64:(a1)" sid;
                   (* WINDOW LAW (§P1-m1.1-8): the runtime proved the read value
                      inside [lo,hi] = W(p) of the target's declared precision; the
                      environment records EXACTLY that interval — never wider. *)
                   lower_stmts (Int_map.add sid (lo, hi) env) rest)
    in
    let (_ : (int * int) Int_map.t) = lower_stmts Int_map.empty body in
    (* ---- text assembly (§P1-m0.4 + §P1-m1.5) -------------------------------- *)
    (* Console-use summary (§P1-m1.5): a pure function of the typed body. It
       decides WHICH module items appear; the statement arms above emit the
       matching instructions, so the two can never disagree — and a refusal
       means no artifact at all. Every PUT (value or literal) closes with the
       newline call, so p_nl / pli_console_put_nl key on put-of-either-kind.
       E2E-54/P1-m2 §P1-m2.1 fact 3: the fold is a RECURSIVE walk (a top-level
       scan cannot see a PUT/GET inside an arm); for a straight-line body it
       visits EXACTLY the same statements in EXACTLY the same order, so every
       pre-P1-m2 artifact byte stays identical (I6). *)
    let rec cu_scan (pu, ge, tx) (s : Hir.stmt) =
      match s.Hir.st with
      | Hir.Put (Hir.P_value _) -> (true, ge, tx)
      | Hir.Put (Hir.P_text _) -> (pu, ge, true)
      | Hir.Get _ -> (pu, true, tx)
      | Hir.If { cond = _; then_; else_ } ->
          let acc = List.fold_left cu_scan (pu, ge, tx) then_ in
          List.fold_left cu_scan acc else_
      | Hir.While { cond = _; body = b } -> List.fold_left cu_scan (pu, ge, tx) b
      | _ -> (pu, ge, tx)
    in
    let cu_put, cu_get, cu_text =
      List.fold_left cu_scan (false, false, false) body
    in
    let cu_any = cu_put || cu_get || cu_text in
    let cu_nl = cu_put || cu_text in
    let entry_sym = "pli80_" ^ proc_name in
    (* one i64 register per automatic symbol of the export procedure, ascending
       sid from the program's symbol table (§P1-m0.4); then one temp per fresh
       register, numbered in evaluation order by the counter above. *)
    (* E2E-54/P1-mD §P1-mD.3: the automatic symbols of the entry, carrying the
       SOURCE SPELLING (sorig) alongside sid so the sidecar can name the MIR local
       v<sid> by its PL/I source name. The .mir local ORDER is unchanged (still
       ascending sid); the byte output is FROZEN — only sorig is now also kept. *)
    let v_regs =
      List.filter_map
        (fun (s : Hir.sym) ->
          if s.Hir.scope = p.Hir.scope && s.Hir.sstorage = Hir.Auto
          then Some (s.Hir.sid, s.Hir.sorig)
          else None)
        prog.Hir.syms
    in
    let t_regs = List.init !tmp_n (fun i -> "t" ^ string_of_int (i + 1)) in
    (* §P1-m1.5: the status register st once when any console call exists, the
       single get slot a1 once when any GET exists — between the ascending
       v<sid> registers and the ascending t<k> temps. *)
    let extra_regs =
      (if cu_any then [ "st" ] else []) @ (if cu_get then [ "a1" ] else [])
    in
    let all_regs =
      List.map (fun (sid, _) -> "v" ^ string_of_int sid) v_regs @ extra_regs @ t_regs
    in
    (* §P1-m1.5: protos (only the used ones, fixed relative order p_put, p_get,
       p_text, p_nl, p_exit) then EXACTLY ONE import line listing only the used
       host names in canonical order — all before the func item; exit is always
       among them because the shared failure tail uses it. *)
    let console_items =
      (if cu_put then [ "p_put:\tproto\ti64, i64:v\n" ] else [])
      @ (if cu_get then [ "p_get:\tproto\ti64, i64:out, i64:lo, i64:hi\n" ] else [])
      @ (if cu_text then [ "p_text:\tproto\ti64, i64:s, i64:n\n" ] else [])
      @ (if cu_nl then [ "p_nl:\tproto\ti64\n" ] else [])
      @ (if cu_any then [ "p_exit:\tproto\ti64:c\n" ] else [])
      @
      if cu_any then
        let names =
          (if cu_put then [ "pli_console_put_i64" ] else [])
          @ (if cu_get then [ "pli_console_get_i64" ] else [])
          @ (if cu_text then [ "pli_console_put_text" ] else [])
          @ (if cu_nl then [ "pli_console_put_nl" ] else [])
          @ [ "exit" ]
        in
        (* §P1-m1.5 item 3: the s<k> items come AFTER the ONE import line and BEFORE
           the func item, in first-use order of their distinct text. *)
        [ "\timport\t" ^ String.concat ", " names ^ "\n" ]
        @ List.map
            (fun (text, lbl) ->
              lbl ^ ":\tstring\t\"" ^ escape_text text ^ "\"\n")
            (List.rev !string_items)
      else []
    in
    let buf = Buffer.create 1024 in
    Buffer.add_string buf "M0:\tmodule\n";
    List.iter (Buffer.add_string buf) console_items;
    Printf.bprintf buf "%s:\tfunc\ti64\n" entry_sym;
    if all_regs <> [] then
      Printf.bprintf buf "\tlocal\t%s\n"
        (String.concat ", " (List.map (fun r -> "i64:" ^ r) all_regs));
    List.iter (fun (s, _ln) -> Printf.bprintf buf "\t%s\n" s) (List.rev !insns);
    (* §P1-m1.5: the SHARED failure tail lives AFTER the body's final ret and
       before endfunc — Lfail is its own UNINDENTED line; every nonzero runtime
       status fail-fasts through exit(status), observable as the process code. *)
    if cu_any then begin
      Buffer.add_string buf "Lfail:\n";
      Buffer.add_string buf "\tcall p_exit, exit, st\n";
      Buffer.add_string buf "\tret st\n";
    end;
    Buffer.add_string buf "\tendfunc\n";
    Printf.bprintf buf "\texport %s\n" entry_sym;
    Buffer.add_string buf "\tendmodule\n";
    let mir_text = Buffer.contents buf in
    (* ---- E2E-54/P1-mD sidecar debug map (§P1-mD.3) — ONLY when requested ---- *)
    (* The default path (debug_source = None) builds NOTHING: the .mir bytes and
       the whole artifact are exactly as before (§P1-mD.2, default FROZEN). When a
       source path is supplied, the sidecar lists the instruction sequence the MIR
       parser WILL see: the body insns in emit order (line from the HIR), then the
       shared failure tail the assembly writes directly (label/call/ret, line 0),
       with the MIR opcode = the first token of each instruction. *)
    let first_token (text : string) : string =
      let n = String.length text in
      let stop = ref 0 in
      while
        !stop < n && text.[!stop] <> ' ' && text.[!stop] <> ','
      do
        incr stop
      done;
      String.sub text 0 !stop
    in
    let opcodes =
      List.map
        (fun (text, ln) ->
          (* A MIR label directive parses as an insn named "label" (mir2o
             validates every row against MIR_insn_name).  The backend writes
             labels as "NAME:" alone on the line — including the m2a/m2b
             control-flow labels — so the sidecar opcode for such a row is
             "label", never the label name (§P1-mD.3 opcode law). *)
          let n = String.length text in
          let op =
            if n > 0 && text.[n - 1] = ':' then "label" else first_token text
          in
          (op, ln))
        (List.rev !insns)
      @
      if cu_any then [ ("label", 0); ("call", 0); ("ret", 0) ] else []
    in
    let debug_map =
      match debug_source with
      | None -> None
      | Some abs_path ->
          let sb = Buffer.create 256 in
          Buffer.add_string sb "p1md 1\n";
          Buffer.add_string sb ("mir " ^ Sha256.hex_digest mir_text ^ "\n");
          Buffer.add_string sb ("file " ^ abs_path ^ "\n");
          Printf.bprintf sb "func 0 %s\n" entry_sym;
          List.iteri
            (fun i (op, ln) ->
              Printf.bprintf sb "insn %s %d %s %d\n" entry_sym i op ln)
            opcodes;
          List.iter
            (fun (sid, sorig) -> Printf.bprintf sb "var v%d %s\n" sid sorig)
            v_regs;
          Some (Buffer.contents sb)
    in
    Ok { entry_sym; mir_text; debug_map }
  with Refusal d -> Error [ d ]

(* The [Backend.BACKEND] instance for a GIVEN export name (see the DEVIATION note
   in the header): the export arrives as a compile-time module parameter, the CLI
   closes over the runtime value. *)
module type EXPORT = sig
  val export : string
end

module For (E : EXPORT) : Backend.BACKEND with type artifact = artifact = struct
  type nonrec artifact = artifact

  let compile ~(profile : Target.profile) (prog : Hir.program) =
    compile ~profile ~export:E.export prog
end
