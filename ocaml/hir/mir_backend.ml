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
(* E2E-54/P1-m3 §P1-m3.2: the drained lowered image of ONE procedure, built by
   the per-proc engine and consumed by the generalized assembly. *)
type func_data = {
  fd_pid : int;
  fd_sym : string;
  fd_ret : Hir.ty option;
  fd_params : int list;
  fd_insns : (string * int) list;
  fd_v : (int * string) list;
  fd_cu : bool * bool * bool;
  fd_hv : string list;
  fd_homes : string list;
  fd_tmps : string list;
  fd_pc : int list;
  fd_fail : string;
}

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
    (* ---- procedure selection (E2E-54/P1-m3 §P1-m3.2-1) ---------------------- *)
    (* The entry is the head procedure (pid 0); the export law below is unchanged.
       The P1-m0 blanket multi-procedure refusal (PLAN §P1-m3.9 item 1) is hereby
       REPLACED by the reached-set selection and validation scans: a REACHED set
       of procedures lowers to one module (callee-first emission, HOME-PASS ABI,
       §P1-m3.2); UNREACHED procedures are DROPPED. The no-procedure message
       stays VERBATIM. *)
    (match prog.Hir.procs with
     | [] ->
         refuse Diagnostic.e_mir_export
           "MIR backend: the program contains no procedure to export"
     | _ -> ());
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
    (* ---- reached-set validation (§P1-m3.2-2): EVERY scan is a pure structural
       pass that runs BEFORE any instruction is emitted; a refusal means NO
       artifact. Order: (a) nesting, (b) call-graph DFS with the cycle refusal,
       (c) the DROP of unreached procedures (implicit — only reached pids lower),
       (d) per-reached name and final-statement laws, then the -g law (9). ---- *)
    let child_scope par =
      List.exists
        (fun (sc : Hir.scope) -> sc.Hir.parent = Some par)
        prog.Hir.scopes
    in
    List.iter
      (fun (pp : Hir.proc) ->
        if not pp.Hir.is_main && child_scope pp.Hir.scope then
          refuse Diagnostic.e_mir_node
            ("MIR backend: procedure "
            ^ quote (Option.value ~default:"(anonymous)" pp.Hir.name)
            ^ " contains a nested procedure; a nested procedure inside a subsidiary \
               procedure is outside the native subset (§P1-m3.2-2a)"))
      prog.Hir.procs;
    let procs_by_pid =
      List.fold_left
        (fun acc (pp : Hir.proc) -> Int_map.add pp.Hir.pid pp acc)
        Int_map.empty prog.Hir.procs
    in
    let pid_key pid =
      match Int_map.find_opt pid procs_by_pid with
      | Some pp ->
          Option.value ~default:(string_of_int pid)
            (Option.map lower_name pp.Hir.name)
      | None -> string_of_int pid
    in
    let rec expr_call_pids (e : Hir.expr) (f : int -> unit) : unit =
      match e.Hir.ex with
      | Hir.Bin { left; right; _ } ->
          expr_call_pids left f;
          expr_call_pids right f
      | Hir.Neg { e = inner }
      | Hir.Convert { e = inner; _ } ->
          expr_call_pids inner f
      | Hir.Elem_read { subs; _ } ->
          List.iter (fun s -> expr_call_pids s f) subs
      | Hir.Call_e { pid; args } ->
          f pid;
          List.iter
            (fun (a : Hir.actual) ->
              match a.Hir.af with
              | Hir.A_value x -> expr_call_pids x f
              | Hir.A_reference _ -> ())
            args
      | _ -> ()
    in
    let designator_call_pids (d : Hir.designator) (f : int -> unit) : unit =
      match d with
      | Hir.D_var _ -> ()
      | Hir.D_elem { subs; _ } ->
          List.iter (fun s -> expr_call_pids s f) subs
    in
    let rec stmt_call_pids (s : Hir.stmt) (f : int -> unit) : unit =
      (match s.Hir.st with
       | Hir.Assign { target; value } ->
           designator_call_pids target f;
           expr_call_pids value f
       | Hir.If { cond; then_; else_ } ->
           expr_call_pids cond f;
           List.iter (fun x -> stmt_call_pids x f) then_;
           List.iter (fun x -> stmt_call_pids x f) else_
       | Hir.While { cond; body } ->
           expr_call_pids cond f;
           List.iter (fun x -> stmt_call_pids x f) body
       | Hir.Call_s { pid; args } ->
           f pid;
           List.iter
             (fun (a : Hir.actual) ->
               match a.Hir.af with
               | Hir.A_value x -> expr_call_pids x f
               | Hir.A_reference d -> designator_call_pids d f)
             args
       | Hir.Return (Some x) -> expr_call_pids x f
       | Hir.Put (Hir.P_value x) -> expr_call_pids x f
       | Hir.Get d -> designator_call_pids d f
       | Hir.Declare _ | Hir.Return None | Hir.Stop | Hir.Put (Hir.P_text _) -> ());
      ()
    in
    (* DFS from the entry over Call_s/Call_e pids (statements in source order,
       arguments left-to-right); a revisit ON THE CURRENT PATH refuses E18 NAMING
       the cycle path (§P1-m3.2-2b). Direct self-recursion is caught HIR-side
       first and never reaches here (§P1-m3.1-1). *)
    let reached : Hir.proc Int_map.t ref = ref Int_map.empty in
    let rec dfs path pid =
      if List.mem pid path then
        refuse Diagnostic.e_mir_node
          ("MIR backend: cyclic procedure calls are outside the native subset: "
          ^ String.concat " -> " (List.rev_map pid_key (pid :: path)))
      else if not (Int_map.mem pid !reached) then begin
        let pp =
          match Int_map.find_opt pid procs_by_pid with
          | Some pp -> pp
          | None ->
              refuse Diagnostic.e_mir_node
                ("MIR backend: a call designates procedure id "
                ^ string_of_int pid
                ^ " which is no procedure of this program (bind resolves every \
                   call name; defensive)")
        in
        reached := Int_map.add pid pp !reached;
        List.iter
          (fun s -> stmt_call_pids s (fun c -> dfs (pid :: path) c))
          pp.Hir.body
      end
    in
    dfs [] 0;
    (* (d) per reached procedure: a portable folded symbol; a VALUE procedure is
       reachable only through value position (§P1-m3c) and must end RETURN(expr)
       exactly as the entry law. The ENTRY's own body-shape checks below stay
       byte-verbatim (§P1-m2 pins). *)
    let folded_of =
      List.fold_left
        (fun acc (pid, pp) ->
          let folded =
            match pp.Hir.name with
            | None ->
                refuse Diagnostic.e_mir_export
                  ("MIR backend: procedure " ^ string_of_int pid
                  ^ " has no source name")
            | Some nm ->
                let folded = lower_name nm in
                if not (portable_name folded) then
                  refuse Diagnostic.e_mir_export
                    ("MIR backend: procedure name " ^ quote nm
                    ^ " cannot become a portable MIR symbol (letters, digits and \
                       '_' only, starting with a letter or '_')")
                else folded
          in
          if pid <> 0 then
            (match pp.Hir.ret with
             | Some _ ->
                 (match List.rev pp.Hir.body with
                  | { Hir.st = Hir.Return (Some _); _ } :: _ -> ()
                  | [] ->
                      refuse Diagnostic.e_mir_node
                        ("MIR backend: procedure " ^ quote folded
                        ^ " has an empty body (no return to lower)")
                  | { Hir.st; st_line } :: _ ->
                      refuse ~line:st_line Diagnostic.e_mir_node
                        ("MIR backend: a value procedure must end with RETURN(expr); \
                           fall-through semantics are unmeasured [TBD] (found "
                        ^ quote (stmt_kind_name st) ^ ")"))
             | None -> ());
          Int_map.add pid folded acc)
        Int_map.empty (Int_map.bindings !reached)
    in
    (* §P1-m3.2-9: the §P1-mD.3 sidecar format is HARD single-function (one
       [func 0] row, one instruction table). A REACHED multi-function set with a
       debug request refuses E18 BY NAME; the single-function -g bytes stay
       byte-frozen. *)
    if debug_source <> None && Int_map.cardinal !reached > 1 then
      refuse Diagnostic.e_mir_node
        "MIR backend: a multi-procedure program with the debug sidecar (-g) is \
           outside the native subset (the §P1-mD.3 map format is single-function; \
           multi-procedure debugging is a later milestone)";
    (* the reached set drives EVERYTHING below: lowering runs in DFS DISCOVERY
       order (entry first; hop-6 LOCKED decision, recorded with the pins), the
       func items assemble in DFS POST-ORDER (callees first, entry LAST and the
       only export), and the single-function case (reached = {entry}) re-emits
       the P1-m0/m1/m2 bytes EXACTLY (I6): no pc protos, no entry hoists, the
       shared Lfail tail. *)
    let post_order : int list ref = ref [] in
    let rec collect pid =
      if List.mem pid !post_order then ()
      else begin
        let pp = Int_map.find pid !reached in
        let subs = ref [] in
        List.iter
          (fun s -> stmt_call_pids s (fun c -> subs := c :: !subs))
          pp.Hir.body;
        List.iter collect (List.rev !subs);
        (* post-order: the pid is APPENDED after its callees complete — the
           emission list ends with the entry (callee first, §P1-m3.1-2/§P1-m3.2-3;
           a caller emitted before a callee is mir2o rc 1 undeclared name). *)
        post_order := !post_order @ [pid]
      end
    in
    collect 0;
    let multi = Int_map.cardinal !reached > 1 in
    (* ---- emission state (a pure function of the program: deterministic) ---- *)
    (* E2E-54/P1-mD: each emitted instruction carries the PL/I source line it
       came from (already available as [st_line]/[ex_line] at every call site).
       The .mir assembly DROPS the line, so the bytes are FROZEN (§P1-mD.2); the
       line rides only into the sidecar. Default [line] is 0 (unlocated).
       E2E-54/P1-m3 §P1-m3.2: the whole engine below runs ONCE PER REACHED
       PROCEDURE (discovery order). Module-wide (NEVER reset): [fresh] temp
       numbering, [cf_n] labels, [string_items], [hv_n] value cells. Per-proc
       (reset at the top of each pass): the [insns] buffer, [declared], the
       failure-tail label, the [hv] cell list, the HOME set (§P1-m3b), the
       callee-proto list and the control-flow state. ---- *)
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
       are collision-free by construction. §P1-m3.2-10 keeps the counter
       module-wide; each label is DEFINED in exactly one func (I5). *)
    let cf_n = ref 0 in
    (* E2E-54/P1-m3 §P1-m3.2-6 (HOME-PASS): one value cell hv<k> per (call site,
       argument position), numbered module-wide; the alloca rides the caller's
       ENTRY hoists (§P1-m3.2-4), the mov into the cell rides right before the
       call row. *)
    let hv_n = ref 0 in
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
    (* ---- per-procedure state (§P1-m3.2): reset at the top of every pass ---- *)
    (* declared local registers of the CURRENT procedure: sid -> declared
       precision (§P1-m0.4); formals enter through [declare] exactly like Autos
       (their dcl row lowers Declare sid — CAND06 proven) but ride the HOME-PASS
       indirection [i64:(v<sid>)] instead of the register itself. *)
    let declared = ref Int_map.empty in
    (* the failure tail of the CURRENT procedure: the shared Lfail of a
       single-function module stays byte-frozen (§P1-m3.2-5); a multi-function
       module names it Lfail_0 (entry) / Lfail_<pid> (subsidiary). *)
    let cur_fail = ref "Lfail" in
    (* the value cells this procedure hoists at entry, and the callee pids whose
       pc protos the module needs (deduplicated at assembly). *)
    let hv_cells : string list ref = ref [] in
    (* E2E-54/P1-m3b §P1-m3.2-6 + §P1-m3.16 R3: the by-reference homes of the
       CURRENT procedure — every caller sid designated by ANY by-reference
       actual in the body (at ANY statement depth), discovered by the pre-body
       scan and sorted ascending. A designated sid has NO register: every read
       and write rides its entry-hoisted home cell i64:(h<sid>) (§P1-m3.2-6),
       the locals line omits v<sid>, and ONE alloca covers the whole func. *)
    let home_sids : int list ref = ref [] in
    let pc_uses : int list ref = ref [] in
    (* the lowered image of each procedure, drained after its pass. *)
    let func_datas : func_data list ref = ref [] in
    let find_sym sid =
      match List.find_opt (fun (s : Hir.sym) -> s.Hir.sid = sid) prog.Hir.syms with
      | Some s -> s
      | None ->
          refuse Diagnostic.e_mir_node
            ("MIR backend: sym(" ^ string_of_int sid
            ^ ") is used but carries no symbol row in the program")
    in
    (* the procedure being lowered (declare routes Formal through it) *)
    let cur_pp : Hir.proc ref = ref p in
    let is_formal sid = (find_sym sid).Hir.sstorage = Hir.Formal in
    (* HOME-PASS access forms (§P1-m3.2-6): a formal sid is reached ONLY through
       the pointer its caller passed — READ [mov k, i64:(v<sid>)], WRITE
       [mov i64:(v<sid>), rv]. An Auto keeps the P1-m0 register bytes verbatim. *)
    let formal_read ?(line = 0) k sid =
      emit ~line "mov %s, i64:(v%d)" k sid
    and formal_write ?(line = 0) sid rv =
      emit ~line "mov i64:(v%d), %s" sid rv
    in
    (* HOME-PASS access forms of a DESIGNATED caller variable (§P1-m3.2-6, the
       m3b half): READ [mov k, i64:(h<sid>)], WRITE [mov i64:(h<sid>), rv]. The
       home register h<sid> holds the ADDRESS of the variable's own stack cell;
       passing the variable twice passes the SAME home, so the callee sees ONE
       shared mutable location (§P1-m3.16 B1 derivation). *)
    let is_homed sid = List.mem sid !home_sids in
    let home_read ?(line = 0) k sid =
      emit ~line "mov %s, i64:(h%d)" k sid
    and home_write ?(line = 0) sid rv =
      emit ~line "mov i64:(h%d), %s" sid rv
    in
    let declare ?(line = 0) sid =
      if Int_map.mem sid !declared then
        refuse ~line Diagnostic.e_mir_node
          ("MIR backend: sym(" ^ string_of_int sid
          ^ ") is declared twice in this body (re-declaration is not modelled)")
      else begin
        let s = find_sym sid in
        if s.Hir.scope <> !cur_pp.Hir.scope then
          refuse ~line Diagnostic.e_mir_node
            ("MIR backend: sym(" ^ string_of_int sid
            ^ ") belongs to a different scope than the procedure being lowered \
               (nested block scoping is outside the native subset)");
        (match s.Hir.sstorage with
         | Hir.Auto -> ()
         (* §P1-m3.2-2d: a formal dcl lowers Declare sid (CAND06 PROVEN); the
            formal must be one of THIS procedure's parameters (bind already
            guarantees it — defensive witness), and its declared type keeps the
            bin_p law through the same precision check as Autos. *)
         | Hir.Formal ->
             if not (List.mem sid !cur_pp.Hir.params) then
               refuse ~line Diagnostic.e_mir_node
                 ("MIR backend: sym(" ^ string_of_int sid
                 ^ ") has storage formal but is not a parameter of the procedure \
                    being lowered (defensive)")
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
               if is_formal sid then begin
                 formal_read ~line k sid;
                 (k, v)
               end
               else if is_homed sid then begin
                 (* §P1-m3.2-6: a designated variable has NO register — the
                    read rides its home cell (no stale register can exist). *)
                 home_read ~line k sid;
                 (k, v)
               end
               else begin
                 emit ~line "mov %s, v%d" k sid;
                 (k, v)
               end
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
    (* the console-use summary of ONE procedure body (§P1-m1.5; §P1-m3.2-3 makes
       it PER-FUNC for the locals and the tail, and the OR across the reached
       funcs for the module items). For a single-proc body this is the EXISTING
       fold — recursive walk, top-level statements in order (P1-m2 fact 3). *)
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
    (* ---- the per-procedure engine (E2E-54/P1-m3 §P1-m3.2) ------------------- *)
    (* ONE lowering pass per REACHED procedure in DFS discovery order. The refs
       above carry the current procedure; the drained func_data below feeds the
       generalized assembly. *)
    List.iter
      (fun (pid, pp) ->
        cur_pp := pp;
        declared := Int_map.empty;
        hv_cells := [];
        (* §P1-m3.16 R3: the HOME set is discovered BEFORE lowering touches the
           body, so the first emitted instruction can already ride the home and
           v<sid> can be excluded from the locals line deterministically. The
           scan is pure structural (refuses nothing; admission is per-site at
           the call, where the env and symbol facts are known). *)
        home_sids := [];
        walk_stmts pp.Hir.body (fun s ->
          match s.Hir.st with
          | Hir.Call_s { args; _ } ->
              List.iter
                (fun (a : Hir.actual) ->
                  match a.Hir.af with
                  | Hir.A_reference (Hir.D_var { sid }) ->
                      if not (List.mem sid !home_sids) then
                        home_sids := sid :: !home_sids
                  | _ -> ())
                args
          | _ -> ());
        home_sids := List.sort Int.compare !home_sids;
        pc_uses := [];
        insns := [];
        (* §P1-m3.2-5 tail law: the single-function module keeps the shared
           Lfail byte-EXACTLY (I6); a multi-function module names the tails
           Lfail_0 (entry) / Lfail_<pid> (subsidiary). *)
        cur_fail :=
          (if not multi then "Lfail"
           else if pid = 0 then "Lfail_0"
           else "Lfail_" ^ string_of_int pid);
        let ck = Option.value ~default:proc_name (Int_map.find_opt pid folded_of) in
        (* §P1-m3.2-2d: a formal dcl lowers Declare sid and registers through the
           SAME precision law as an Auto; the callee env SEEDS every formal with
           W(formal precision) (§P1-m3.2-6, hop-6 LOCKED) so every later read is
           window-proved against its declared type and the uninitialized law
           never lies about a parameter. *)
        let env0 =
          List.fold_left
            (fun acc sid ->
              let sp = bin_p (find_sym sid).Hir.sty in
              Int_map.add sid (window sp) acc)
            Int_map.empty pp.Hir.params
        in
        let f_body = pp.Hir.body in
        (* the body-shape pre-check: the ENTRY keeps its two pinned messages
           VERBATIM (they name the entry); a non-entry value procedure was
           already checked by validation scan (d), and a VOID procedure carries
           NO final-statement requirement (the bare RETURN; / fall-through law,
           §P1-m3.2-2d). *)
        if pid = 0 then begin
          if f_body = [] then
            refuse Diagnostic.e_mir_node
              "MIR backend: the entry procedure has an empty body (no return to lower)";
          (match List.rev f_body with
           | { Hir.st = Hir.Return (Some _); _ } :: _ -> ()
           | { Hir.st = Hir.Return None; st_line } :: _ ->
               refuse ~line:st_line Diagnostic.e_mir_node
                 "MIR backend: the body must end with RETURN(expr); a bare return leaves \
                    the result undefined (implicit results are unmeasured [TBD])"
           | { Hir.st; st_line } :: _ ->
               refuse ~line:st_line Diagnostic.e_mir_node
                 ("MIR backend: the body must end with RETURN(expr); fall-through \
                    semantics are unmeasured [TBD] (found "
                 ^ quote (stmt_kind_name st) ^ ")")
           | [] -> assert false)
        end;
        let f_cu = List.fold_left cu_scan (false, false, false) f_body in
        let tmp_base = !tmp_n in
        (* the result window of the CURRENT procedure: the entry law (ret_p) is
           byte-frozen; a subsidiary value procedure (m3c) proves against its own
           declared RETURNS precision (§P1-m3.2-2d). *)
        let pp_ret_p =
          match pp.Hir.ret with
          | Some _ when pid = 0 -> ret_p (* the frozen entry law *)
          | None -> 0
          | Some t -> (
              match t with
              | Hir.Fixed_bin (q, 0) -> q
              | _ ->
                  refuse Diagnostic.e_mir_node
                    ("MIR backend: procedure " ^ quote ck
                    ^ " has a result type outside the native subset (a zero-argument \
                       FIXED BINARY(p,0) result is required)"))
        in
        let rec lower_stmts env = function
          | [] -> env
          | s :: rest ->
              let line = s.Hir.st_line in
              match s.Hir.st with
              | Hir.Declare sid ->
                  declare ~line sid;
                  lower_stmts env rest
              | Hir.Assign { target; value } ->
                  (match target with
                   | Hir.D_elem _ ->
                       refuse ~line Diagnostic.e_mir_node
                         "MIR backend: assignment to an array element is outside the \
                            native subset (brief §3)"
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
                       if is_formal sid then formal_write ~line sid rv
                       else if is_homed sid then home_write ~line sid rv
                       else emit ~line "mov v%d, %s" sid rv;
                       lower_stmts (Int_map.add sid iv env) rest)
              | Hir.Return (Some e) ->
                  (* Reachable only as the FINAL statement (checked above), so [rest] is
                     empty and the recursion below simply returns the environment. *)
                  let rv, ev = lower env e in
                  let rw = window pp_ret_p in
                  if not (in_window rw ev) then
                    refuse ~line Diagnostic.e_mir_numeric
                      ("MIR backend: the returned value can reach " ^ show_iv ev
                      ^ ", leaving the window " ^ show_iv rw
                      ^ " of the declared result type " ^ Hir.pp_ty (Hir.Fixed_bin (pp_ret_p, 0))
                      ^ " (§P1-m0.3-3, brief §4)");
                  emit ~line "ret %s" rv;
                  lower_stmts env rest
              | Hir.Return None ->
                  (* §P1-m3.2-2d + the hop-5 MEASURED law (y2): a VOID procedure's bare
                     RETURN; lowers to a BARE ret (a no-result func REJECTS [ret op]).
                     A bare return in a VALUE procedure is refused by the final-
                     statement check above. *)
                  if pp.Hir.ret = None then begin
                    emit ~line "ret";
                    lower_stmts env rest
                  end
                  else
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
                      (* §P1-m3.16 R1/R2: a body call that passes a variable by
                         reference lets the CALLEE write it — the counted-loop env
                         must treat that sid as a body writer (R1: drop-not-inherit
                         at the loop exit; the callee's value is never assumed).
                         A by-ref designation of the INDUCTION VARIABLE itself
                         invalidates the step proof outright (R2: refuse the
                         shape BY NAME, never emit unsound code). *)
                      walk_stmts body (fun s ->
                        match s.Hir.st with
                        | Hir.Call_s { args; _ } ->
                            List.iter
                              (fun (a : Hir.actual) ->
                                match a.Hir.af with
                                | Hir.A_reference (Hir.D_var { sid }) ->
                                    if sid = iv then
                                      refuse ~line:s.Hir.st_line
                                        Diagnostic.e_mir_node
                                        ("MIR backend: DO WHILE loop outside the proven \
                                           counted-loop subset: the loop body passes the \
                                           induction variable sym(" ^ string_of_int iv
                                        ^ ") by reference — the step proof cannot hold \
                                           against a callee write (§P1-m3.16 R2)")
                                    else add_writer sid
                                | _ -> ())
                              args
                        | _ -> ());
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
                      let tmp_base_w = !tmp_n in
                      let cf_base = !cf_n in
                      (* §P1-m3.16 addendum (loop hoists): the DISCARDED
                         verification pass must also rewind the value-cell
                         allocator and the cell list, or a Call_s inside a
                         verified body would DOUBLE-ALLOCATE dead cells — a
                         per-iteration stack growth §P1-m3.2-4/§P1-m3.14 forbid
                         (latent m3a defect, no m3a fixture reached it; fixed
                         here and recorded, never fitted). *)
                      let hv_n_w = !hv_n in
                      let hv_cells_w = !hv_cells in
                      insns := [];
                      let (_ : (int * int) Int_map.t) = lower_stmts body_env body in
                      insns := outer;
                      tmp_n := tmp_base_w;
                      cf_n := cf_base;
                      hv_n := hv_n_w;
                      hv_cells := hv_cells_w;
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
                        "MIR backend: a DO WHILE guard that is not a relational \
                           comparison of proved integer operands is outside the counted-loop \
                           subset (a condition literal is not admitted; §P1-m2.3)")
              | Hir.Call_s { pid = cpid; args } ->
                  (* E2E-54/P1-m3 (§P1-m3.2-6) + m3b (the A_reference half): the
                     HOME-PASS call. Every actual lowers LEFT-TO-RIGHT in the
                     CALLER env through the existing window proofs; a BY-VALUE
                     result is written into its OWN value cell hv<k> (entry-hoisted
                     alloca, §P1-m3.2-4) right before the call row, and the cell
                     ADDRESS is passed; a BY-REFERENCE actual passes the variable's
                     entry-hoisted HOME h<sid> — no copy, no second representation
                     (§P1-m3.16 R3). The callee writes ONLY the cells it is given,
                     so by-value isolation is structural (x8 PROVEN) while a shared
                     home gives genuine shared storage (two actuals, ONE cell).
                     After the call (§P1-m3.2-8): every by-ref-designated caller
                     sid WIDENS to its full declared window W(p) — the caller never
                     assumes what the callee wrote (I2/I4) — while by-value actuals
                     change NOTHING and every caller vreg lives across the call
                     untouched (x7 PROVEN). A VOID callee takes NO result operand
                     (probe_void/y2 EXECUTED); result regs (m3c) come later. *)
                  let callee =
                    match Int_map.find_opt cpid !reached with
                    | Some cp -> cp
                    | None ->
                        refuse ~line Diagnostic.e_mir_node
                          ("MIR backend: a call designates procedure id "
                          ^ string_of_int cpid
                          ^ " which is not a reached procedure (defensive)")
                  in
                  let ckey =
                    match Int_map.find_opt cpid folded_of with
                    | Some ck -> ck
                    | None -> assert false
                  in
                  (* defensive: a statement call to a VALUE procedure dies HIR-side
                     (HIR-E07, §P1-m3.1-1); the backend never sees one. *)
                  (match callee.Hir.ret with
                   | None -> ()
                   | Some _ ->
                       refuse ~line Diagnostic.e_mir_node
                         ("MIR backend: statement-level call to function " ^ quote ckey
                         ^ " discards a value; unlowered (HIR-E07 admits no \
                            statement-call to a value procedure)"));
                  (* §P1-m3.2-6 (m3b admission, replacing the m3a transitional
                     refusal — the arm §P1-m3.9-2/§P1-m3.16 B3 retire): a
                     by-reference actual must designate an AUTO SCALAR OF THIS
                     CALLER procedure (else E18 BY NAME); an array-element
                     designation refuses E18 (arrays are outside the subset);
                     and the caller env must prove the variable DEFINITELY
                     INITIALIZED at this site (else E19 — the callee could read
                     garbage, §P1-m3.11 I2). The argument position rides the
                     SAME 0-based index hir_build uses for its own argument
                     messages (hop-8 STEP-0, measured first-hand). EVERY check
                     runs BEFORE any lowering, so a refusal emits nothing. *)
                  List.iteri
                    (fun pos (a : Hir.actual) ->
                      match a.Hir.af with
                      | Hir.A_value _ -> ()
                      | Hir.A_reference d ->
                          (match d with
                           | Hir.D_elem _ ->
                               refuse ~line:a.Hir.ac_line Diagnostic.e_mir_node
                                 ("MIR backend: by-reference actual argument "
                                 ^ string_of_int pos ^ " of call to " ^ quote ckey
                                 ^ " designates an array element; arrays are outside \
                                    the native subset (§P1-m3.2-6)")
                           | Hir.D_var { sid } ->
                               let s = find_sym sid in
                               if
                                 s.Hir.sstorage <> Hir.Auto
                                 || s.Hir.scope <> (!cur_pp).Hir.scope
                               then
                                 refuse ~line:a.Hir.ac_line Diagnostic.e_mir_node
                                   ("MIR backend: by-reference actual argument "
                                   ^ string_of_int pos ^ " of call to " ^ quote ckey
                                   ^ " does not designate an automatic scalar of the \
                                      calling procedure (storage "
                                   ^ Hir.pp_storage s.Hir.sstorage ^ "; §P1-m3.2-6)")
                               else if List.mem sid !home_sids then begin
                                 (* the pre-scan admitted the designation; the
                                    declaration law still has to hold *)
                                 if not (Int_map.mem sid !declared) then
                                   refuse ~line:a.Hir.ac_line Diagnostic.e_mir_node
                                     ("MIR backend: by-reference actual argument "
                                     ^ string_of_int pos ^ " of call to " ^ quote ckey
                                     ^ " designates sym(" ^ string_of_int sid
                                     ^ ") which was never declared in this body")
                                 else if Int_map.find_opt sid env = None then
                                   refuse ~line:a.Hir.ac_line
                                     Diagnostic.e_mir_numeric
                                     ("MIR backend: by-reference actual argument "
                                     ^ string_of_int pos ^ " of call to " ^ quote ckey
                                     ^ " designates sym(" ^ string_of_int sid
                                     ^ ") which is not definitely initialized on every \
                                        reachable path; the callee could read garbage \
                                        (uninitialized by-reference actual, §P1-m3.2-6)")
                               end
                               else
                                 refuse ~line:a.Hir.ac_line Diagnostic.e_mir_node
                                   ("MIR backend: by-reference actual argument "
                                   ^ string_of_int pos ^ " of call to " ^ quote ckey
                                   ^ " designates sym(" ^ string_of_int sid
                                   ^ ") which the home pre-scan did not admit \
                                      (defensive)")))
                    args;
                  (* §P1-m3.2-2d: bind has already matched each actual to its formal
                     row (E17); the backend RE-PROVES the declared types match before
                     trusting the formal window as the operand window. *)
                  let nargs = List.length args in
                  if nargs <> List.length callee.Hir.params then
                    refuse ~line Diagnostic.e_mir_node
                      ("MIR backend: the call to " ^ quote ckey ^ " passes "
                      ^ string_of_int nargs ^ " actuals to a procedure with "
                      ^ string_of_int (List.length callee.Hir.params)
                      ^ " formals (defensive: bind admits the call arity first)");
                  (* HOME-PASS operands (§P1-m3.2-6): every actual contributes an
                     ADDRESS register to the call row — a fresh value cell hv<k>
                     rewritten at THIS site for A_value, or the variable's single
                     home h<sid> for A_reference. The declared-type equality law
                     runs for BOTH kinds before any lowering. *)
                  let operand_regs =
                    List.map2
                      (fun (a : Hir.actual) (psid : int) ->
                        let ap = bin_p ~line:a.Hir.ac_line a.Hir.ac_ty in
                        let fp = bin_p ~line:a.Hir.ac_line (find_sym psid).Hir.sty in
                        if ap <> fp then
                          refuse ~line:a.Hir.ac_line Diagnostic.e_mir_numeric
                            ("MIR backend: the actual's declared type "
                            ^ Hir.pp_ty a.Hir.ac_ty ^ " does not equal the formal's \
                               declared type of sym(" ^ string_of_int psid
                            ^ ") — the window law cannot be trusted here")
                        else
                          match a.Hir.af with
                          | Hir.A_value x ->
                              let rv, _iv = lower env x in
                              incr hv_n;
                              let cell = "hv" ^ string_of_int !hv_n in
                              hv_cells := cell :: !hv_cells;
                              emit ~line "mov i64:(%s), %s" cell rv;
                              cell
                          | Hir.A_reference (Hir.D_var { sid }) ->
                              "h" ^ string_of_int sid
                          | Hir.A_reference (Hir.D_elem _) ->
                              (* admitted only by the sweep above, which refuses
                                 every element designation first (defensive) *)
                              assert false)
                      args callee.Hir.params
                  in
                  if not (List.mem cpid !pc_uses) then pc_uses := cpid :: !pc_uses;
                  if operand_regs = [] then
                    emit ~line "call pc%d, pli80_%s" cpid ckey
                  else
                    emit ~line "call pc%d, pli80_%s, %s" cpid ckey
                      (String.concat ", " operand_regs);
                  (* §P1-m3.2-8 (m3b half, brief §4): the caller knows NOTHING the
                     callee may have written — every by-ref-designated sid widens
                     to the FULL declared window W(p) (I2/I4: monotone widening,
                     never a call-site constant); by-value actuals and unpassed
                     locals keep their env exactly (I3). *)
                  let env_after =
                    List.fold_left
                      (fun acc (a : Hir.actual) ->
                        match a.Hir.af with
                        | Hir.A_reference (Hir.D_var { sid }) ->
                            Int_map.add sid (window (Int_map.find sid !declared)) acc
                        | _ -> acc)
                      env args
                  in
                  lower_stmts env_after rest
              | Hir.Stop ->
                  refuse ~line Diagnostic.e_mir_node
                    "MIR backend: stop is outside the native subset (startup and end \
                       semantics are out of scope, brief §3)"
              | Hir.Put src ->
                  (* §P1-m1.5 (m1a): the lowered value goes through the raw runtime put
                     (the runtime never adds a newline); the BACKEND closes every PUT
                     statement with a statement-level newline call. EVERY console call
                     is followed by its OWN status branch to THIS function's failure
                     tail (§P1-m3.2-5, I5: same-func and module-unique). *)
                  (match src with
                   | Hir.P_value e ->
                       let rv, _iv = lower env e in
                       emit ~line "call p_put, pli_console_put_i64, st, %s" rv;
                       emit ~line "bne %s, st, 0" !cur_fail;
                       emit ~line "call p_nl, pli_console_put_nl, st";
                       emit ~line "bne %s, st, 0" !cur_fail;
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
                       emit ~line "bne %s, st, 0" !cur_fail;
                       emit ~line "call p_nl, pli_console_put_nl, st";
                       emit ~line "bne %s, st, 0" !cur_fail;
                       lower_stmts env rest)
              | Hir.Get d ->
                  (* §P1-m1.5: the single get slot a1 is stack-allocated (measured
                     probe2 pattern; §P1-m3.2-4 hoists it once at entry for a
                     multi-function func); the runtime call carries the status
                     register, the slot and the target's declared window, and only a
                     zero status stores the value into the target. *)
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
                       if not multi then emit ~line "alloca a1, 8";
                       emit ~line "call p_get, pli_console_get_i64, st, a1, %d, %d" lo hi;
                       emit ~line "bne %s, st, 0" !cur_fail;
                       if is_formal sid then formal_write ~line sid "i64:(a1)"
                       else if is_homed sid then home_write ~line sid "i64:(a1)"
                       else emit ~line "mov v%d, i64:(a1)" sid;
                       (* WINDOW LAW (§P1-m1.1-8): the runtime proved the read value
                          inside [lo,hi] = W(p) of the target's declared precision; the
                          environment records EXACTLY that interval — never wider. *)
                       lower_stmts (Int_map.add sid (lo, hi) env) rest)
        in
        let (_ : (int * int) Int_map.t) = lower_stmts env0 f_body in
        (* §P1-m3.2-2d: a VOID procedure with no trailing RETURN statement still
           needs its bare final ret (fall-through appends it; a RETURN; already
           emitted one). A VALUE procedure ended by its final RETURN(expr) check. *)
        (match pp.Hir.ret with
         | None ->
             (match !insns with
              | ("ret", _) :: _ -> ()
              | _ -> emit "ret");
         | Some _ -> ());
        (* drain the pass: source order; own Autos; own temps (module-wide
           numbers continue); own value cells ascending. *)
        let f_insns = List.rev !insns in
        let f_v_regs =
          List.filter_map
            (fun (s : Hir.sym) ->
              (* §P1-m3.2-6/§P1-m3.16 R3: a DESIGNATED variable has NO register —
                 its storage is the home cell alone, so v<sid> is excluded from
                 the locals line and can never be a stale authority. *)
              if
                s.Hir.scope = pp.Hir.scope && s.Hir.sstorage = Hir.Auto
                && not (List.mem s.Hir.sid !home_sids)
              then Some (s.Hir.sid, s.Hir.sorig)
              else None)
            prog.Hir.syms
        in
        let f_t_regs =
          List.init (!tmp_n - tmp_base) (fun i -> "t" ^ string_of_int (tmp_base + 1 + i))
        in
        func_datas :=
          {
            fd_pid = pid;
            fd_sym = "pli80_" ^ ck;
            fd_ret = pp.Hir.ret;
            fd_params = pp.Hir.params;
            fd_insns = f_insns;
            fd_v = f_v_regs;
            fd_cu = f_cu;
            fd_hv = List.rev !hv_cells;
            fd_homes = List.map (fun sid -> "h" ^ string_of_int sid) !home_sids;
            fd_tmps = f_t_regs;
            fd_pc = !pc_uses;
            fd_fail = !cur_fail;
          }
          :: !func_datas)
      (Int_map.bindings !reached);
    (* the ENTRY's lowered image stays reachable under the P1-m0/m1/m2 names the
       sidecar postlude reads below (!insns, v_regs, entry_sym, cu_any) — the
       single-function bytes are byte-frozen (§P1-mD.2, I6). func_datas carries
       the procs in lowering (discovery) order; the entry was lowered FIRST. *)
    let entry_fd = List.find (fun fd -> fd.fd_pid = 0) !func_datas in
    (* the postlude below reads !insns (reversed accumulation) and must see the
       ENTRY's insns exactly as the frozen single-function path left them. *)
    insns := List.rev entry_fd.fd_insns;
    let v_regs = entry_fd.fd_v in
    let entry_sym = entry_fd.fd_sym in
    (* ---- text assembly (§P1-m0.4 + §P1-m1.5; generalized per §P1-m3.2-3) ---- *)
    (* Console-use summary (§P1-m1.5 law, §P1-m3.2-3 scope): PER FUNC it decides
       that func's st/a1 locals and the existence of ITS failure tail; the OR
       across the reached funcs decides which MODULE items appear. The statement
       arms above emit the matching instructions, so the two can never disagree —
       and a refusal means no artifact at all. For a single-procedure program
       every fold coincides with the existing entry fold: the bytes stay
       identical (I6). *)
    let module_cu =
      List.fold_left
        (fun (pu, ge, tx) fd ->
          let fpu, fge, ftx = fd.fd_cu in
          (pu || fpu, ge || fge, tx || ftx))
        (false, false, false) !func_datas
    in
    let cu_put, cu_get, cu_text = module_cu in
    let cu_any = cu_put || cu_get || cu_text in
    let cu_nl = cu_put || cu_text in
    (* §P1-m3.2-3: the callee protos pc<pid> are USED-ONLY (deduplicated across
       the reached funcs, ascending pid — deterministic); the leading bare i64
       appears iff the callee RETURNS a value; a void callee with no formals
       carries the EMPTY proto (probe_void EXECUTED). *)
    let pc_proto_line cpid =
      let cp = Int_map.find cpid !reached in
      let parts =
        (match cp.Hir.ret with Some _ -> [ "i64" ] | None -> [])
        @ List.map (fun sid -> "i64:v" ^ string_of_int sid) cp.Hir.params
      in
      "pc" ^ string_of_int cpid ^ ":\tproto"
      ^ (if parts = [] then "" else "\t" ^ String.concat ", " parts)
      ^ "\n"
    in
    let used_pc =
      let set = ref [] in
      List.iter
        (fun fd ->
          List.iter
            (fun cpid -> if not (List.mem cpid !set) then set := cpid :: !set)
            fd.fd_pc)
        !func_datas;
      List.sort Int.compare !set
    in
    (* one func item (§P1-m3.2-4/5): title (result type iff value; formals as
       regs, EXCLUDED from the locals line); the locals line ascending within
       each class (own Autos, st iff THIS func has console, a1 iff THIS func has
       GET, homes h<sid> come with m3b, value cells hv<k>, own temps t<k>); the
       entry hoists of a multi-function func (a1, then hv<k>) as the FIRST
       instructions; the body insns; then THIS func's failure tail iff THIS func
       has console insns — BARE ret on a void tail (hop-5 measured law), ret st
       on a value tail. A single-function module re-emits the EXISTING bytes. *)
    let locals_of fd =
      let f_any, f_get, _ = fd.fd_cu in
      (if f_any then [ "st" ] else [])
      @ (if f_get then [ "a1" ] else [])
      @ fd.fd_homes
      @ fd.fd_hv
      @ fd.fd_tmps
    in
    let hoists_of fd =
      let _, f_get, _ = fd.fd_cu in
      (* §P1-m3.2-4 entry-hoist order: a1 (existing GET law), then EACH home
         h<sid> (ascending sid), then each value cell hv<k> — ALL hoisted at
         ENTRY, never at the call site (no per-iteration stack growth). *)
      (if multi && f_get then [ "a1" ] else [])
      @ (if multi then fd.fd_homes else [])
      @ (if multi then fd.fd_hv else [])
    in
    let add_func_item buf fd =
      let parts =
        (match fd.fd_ret with Some _ -> [ "i64" ] | None -> [])
        @ List.map (fun sid -> "i64:v" ^ string_of_int sid) fd.fd_params
      in
      Printf.bprintf buf "%s:\tfunc%s\n" fd.fd_sym
        (if parts = [] then "" else "\t" ^ String.concat ", " parts);
      let regs =
        List.map (fun (sid, _) -> "v" ^ string_of_int sid) fd.fd_v @ locals_of fd
      in
      if regs <> [] then
        Printf.bprintf buf "\tlocal\t%s\n"
          (String.concat ", " (List.map (fun r -> "i64:" ^ r) regs));
      List.iter (fun r -> Printf.bprintf buf "\talloca %s, 8\n" r) (hoists_of fd);
      List.iter (fun (s, _ln) -> Printf.bprintf buf "\t%s\n" s) fd.fd_insns;
      let f_any, _, _ = fd.fd_cu in
      if f_any then begin
        (* the tail label is UNINDENTED (existing byte law; y2 PROVEN per-func);
           the exit call is shared, the ending follows the hop-5 law. *)
        Printf.bprintf buf "%s:\n" fd.fd_fail;
        Buffer.add_string buf "\tcall p_exit, exit, st\n";
        (match fd.fd_ret with
         | None -> Buffer.add_string buf "\tret\n"
         | Some _ -> Buffer.add_string buf "\tret st\n")
      end;
      Buffer.add_string buf "\tendfunc\n"
    in
    let buf = Buffer.create 1024 in
    Buffer.add_string buf "M0:\tmodule\n";
    (* §P1-m3.2-3 module order: M0 / callee protos (multi only) / console protos
       (existing fixed relative order, used-only ACROSS ALL FUNCS) / the ONE
       import line (existing canonical order + exit) / s<k> items (existing
       first-use order) / func items in DFS POST-ORDER (callees first, entry
       LAST) / the ONE export / endmodule. *)
    List.iter (fun cpid -> Buffer.add_string buf (pc_proto_line cpid)) used_pc;
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
           the func items, in first-use order of their distinct text. *)
        [ "\timport\t" ^ String.concat ", " names ^ "\n" ]
        @ List.map
            (fun (text, lbl) ->
              lbl ^ ":\tstring\t\"" ^ escape_text text ^ "\"\n")
            (List.rev !string_items)
      else []
    in
    List.iter (Buffer.add_string buf) console_items;
    let post_order_datas =
      List.filter_map
        (fun opid -> List.find_opt (fun fd -> fd.fd_pid = opid) !func_datas)
        !post_order
    in
    List.iter (add_func_item buf) post_order_datas;
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
