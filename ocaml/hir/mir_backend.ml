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
   import line with the used host names in canonical order, the st (and a1)
   locals, and the shared Lfail failure tail after the body return. A procedure
   WITHOUT console statements emits the §P1-m0 bytes EXACTLY — the M01/M02/M03
   pins and the CT2 object-byte law (§P1-m1.6).

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

type artifact = { entry_sym : string; mir_text : string }

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

let compile ~(profile : Target.profile) ~(export : string) (prog : Hir.program)
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
    let insns : string list ref = ref [] in
    let emit fmt = Printf.ksprintf (fun s -> insns := s :: !insns) fmt in
    let tmp_n = ref 0 in
    let fresh () =
      incr tmp_n;
      "t" ^ string_of_int !tmp_n
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
               emit "mov %s, %d" k v;
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
               emit "mov %s, v%d" k sid;
               (k, v)
           | None ->
               refuse ~line Diagnostic.e_mir_numeric
                 ("MIR backend: uninitialized read of sym(" ^ string_of_int sid
                 ^ ") on the only path of this straight-line body; reading an undefined \
                    value is outside the proven-safe domain (brief §4)"))
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
          emit "%s %s, %s, %s" nm k rl rr;
          (k, v)
      | Hir.Neg { e = inner } ->
          let w = win () in
          let ri, iiv = lower env inner in
          let niv = (- (snd iiv), - (fst iiv)) in
          let v = prove w niv ("the negation of " ^ show_iv iiv) in
          let k = fresh () in
          emit "neg %s, %s" k ri;
          (k, v)
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
                   emit "mov v%d, %s" sid rv;
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
              emit "ret %s" rv;
              lower_stmts env rest
          | Hir.Return None ->
              refuse ~line Diagnostic.e_mir_node
                "MIR backend: return with no value (see the final-statement check)"
          | Hir.If _ ->
              refuse ~line Diagnostic.e_mir_node
                "MIR backend: if is outside the P1-m0 native subset (straight-line only; \
                   brief §3 admits conditional control only for a LATER preregistered \
                   milestone)"
          | Hir.While _ ->
              refuse ~line Diagnostic.e_mir_node
                "MIR backend: a while loop is outside the P1-m0 native subset (brief §3: \
                   loops are explicitly excluded)"
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
                   emit "call p_put, pli_console_put_i64, st, %s" rv;
                   emit "bne Lfail, st, 0";
                   emit "call p_nl, pli_console_put_nl, st";
                   emit "bne Lfail, st, 0";
                   lower_stmts env rest
               | Hir.P_text _ ->
                   (* Defensive until milestone m1b: the HIR lowering refuses literal
                      PUT items at HIR-E21 in m1a, so this arm is UNEXERCISED; the
                      p_text/s<k> emission lands with §P1-m1.11 step 4. *)
                   refuse ~line Diagnostic.e_mir_node
                     "MIR backend: a console PUT of a literal is outside the native \
                        subset until the §P1-m1 milestone m1b emission lands")
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
                   emit "alloca a1, 8";
                   emit "call p_get, pli_console_get_i64, st, a1, %d, %d" lo hi;
                   emit "bne Lfail, st, 0";
                   emit "mov v%d, i64:(a1)" sid;
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
       means no artifact at all. P_text is deliberately not counted: literal
       items are refused at lowering until milestone m1b lands. *)
    let cu_put, cu_get =
      List.fold_left
        (fun (pu, ge) (s : Hir.stmt) ->
          match s.Hir.st with
          | Hir.Put (Hir.P_value _) -> (true, ge)
          | Hir.Get _ -> (pu, true)
          | _ -> (pu, ge))
        (false, false)
        body
    in
    let cu_any = cu_put || cu_get in
    let entry_sym = "pli80_" ^ proc_name in
    (* one i64 register per automatic symbol of the export procedure, ascending
       sid from the program's symbol table (§P1-m0.4); then one temp per fresh
       register, numbered in evaluation order by the counter above. *)
    let v_regs =
      List.filter_map
        (fun (s : Hir.sym) ->
          if s.Hir.scope = p.Hir.scope && s.Hir.sstorage = Hir.Auto then Some s.Hir.sid
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
      List.map (fun sid -> "v" ^ string_of_int sid) v_regs @ extra_regs @ t_regs
    in
    (* §P1-m1.5: protos (only the used ones, fixed relative order p_put, p_get,
       p_text, p_nl, p_exit) then EXACTLY ONE import line listing only the used
       host names in canonical order — all before the func item; exit is always
       among them because the shared failure tail uses it. *)
    let console_items =
      (if cu_put then [ "p_put:\tproto\ti64, i64:v\n" ] else [])
      @ (if cu_get then [ "p_get:\tproto\ti64, i64:out, i64:lo, i64:hi\n" ] else [])
      @ (if cu_put then [ "p_nl:\tproto\ti64\n" ] else [])
      @ (if cu_any then [ "p_exit:\tproto\ti64:c\n" ] else [])
      @
      if cu_any then
        let names =
          (if cu_put then [ "pli_console_put_i64" ] else [])
          @ (if cu_get then [ "pli_console_get_i64" ] else [])
          @ (if cu_put then [ "pli_console_put_nl" ] else [])
          @ [ "exit" ]
        in
        [ "\timport\t" ^ String.concat ", " names ^ "\n" ]
      else []
    in
    let buf = Buffer.create 1024 in
    Buffer.add_string buf "M0:\tmodule\n";
    List.iter (Buffer.add_string buf) console_items;
    Printf.bprintf buf "%s:\tfunc\ti64\n" entry_sym;
    if all_regs <> [] then
      Printf.bprintf buf "\tlocal\t%s\n"
        (String.concat ", " (List.map (fun r -> "i64:" ^ r) all_regs));
    List.iter (fun s -> Printf.bprintf buf "\t%s\n" s) (List.rev !insns);
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
    Ok { entry_sym; mir_text = Buffer.contents buf }
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
