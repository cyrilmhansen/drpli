(* lib/diagnostic.ml — typed, deterministic diagnostics for the E2E-54 HIR layer.

   A diagnostic is the ONLY legitimate way for the HIR path to refuse: there is no
   silent-generic-node escape hatch in Hir (E2E-54/P0 brief §3). Rendering is pure
   and stable: code + optional source line + message; no timestamps, pids or
   addresses. *)

type severity = Error

type t = { code : string; sev : severity; line : int option; msg : string }

let make ?(sev = Error) ?line code msg = { code; sev; line; msg }

let pp d =
  let l = match d.line with Some n -> Printf.sprintf "line %d: " n | None -> "" in
  Printf.sprintf "%s: %s%s" d.code l d.msg

let pp_all ds = String.concat "\n" (List.map pp ds)

(* Stable codes (P0 set). Codes NEVER change meaning; new refusals get new codes. *)
let e_parse = "HIR-E00" (* front end died before HIR could see the program *)
let e_bind = "HIR-E01" (* the semantic authority (bind) refused the program *)
let e_type = "HIR-E02" (* declared type outside the P0 HIR lowering subset *)
let e_decl = "HIR-E03" (* declaration form outside the subset (arrays, INITIAL, ...) *)
let e_expr = "HIR-E04" (* expression form outside the subset *)
let e_stmt = "HIR-E05" (* statement form outside the subset *)
let e_unresolved = "HIR-E06" (* identifier resolved by NO bind row in any visible scope *)
let e_call = "HIR-E07" (* call/signature outside the P0 subset (external, recursive, arity) *)
let e_lit = "HIR-E08" (* literal outside the P0 domain (bin(15) range) *)
let e_conv = "HIR-E09" (* a conversion the HIR cannot represent faithfully *)
let e_profile = "HIR-E10" (* the target profile leaves a required field UNKNOWN *)
let e_scope = "HIR-E11" (* lexical form whose scoping bind does not expose per-block *)

(* E2E-54/P1-a1 additions (PLAN §P1-a1.5). Codes are APPENDED to the stable list;
   no existing code changes meaning (falsifier T10). Landed with the Semantic_env
   step because the env's split-channel guard already needs [e_dims]. *)
let e_index = "HIR-E12" (* subscript use that is not a 1-D array reference: scalar name,
                            or a constant subscript outside the declared bounds — the
                            bounds test is an HIR subset rule, DR's out-of-range
                            behaviour is unmeasured [TBD] (§P1-a1.2) *)
let e_whole_array = "HIR-E13" (* array name used whole, in value or target position;
                                 P1-a1 admits element references only (§P1-a1.2) *)
let e_dims = "HIR-E14" (* subscript count /= 1, or a bind split-channel inconsistency
                          (an array record with no row, or duplicate records) *)

(* E2E-54/P1-a2 additions (PLAN §P1-a2.5). Appended to the stable list; no existing
   code changes meaning (falsifier T10). *)
let e_arg_whole_array = "HIR-E15"
  (* whole-array ACTUAL at an argument position (a name projecting Array1): P1-a2
     admits element designators only — DR has no array calling convention [C175] and
     whole-array actuals are unmeasured [TBD] (§P1-a2.5). Handover recorded: the same
     input died on E13 (a value/target-position code) before this slice. *)
let e_arg_evidence = "HIR-E16"
  (* missing or contradictory bind PASSING evidence at an argument position: no
     recorded call site matches the call node, a position classifies PM_unknown /
     PM_copy_in, or an admitted shape is contradicted by bind's record. UNEXERCISED
     defensive witness, exactly like the P0 dup_free and the P1-a1 §P1-a1.5(e) guards
     — never fitted, never silently accepted. *)
let e_arg_type = "HIR-E17"
  (* actual/formal declared-TYPE mismatch at an argument position, naming both sides;
     DR's conversion behaviour at argument positions is unmeasured [TBD], so no
     conversion node is invented (§P1-a2.5). *)

(* E2E-54/P1-m0 additions (PLAN §P1-m0.5). APPENDED only; no existing code changes
   meaning (falsifier T10). These codes are raised by the MIR backend alone — the
   historical pipeline and the HIR lowering never emit them. *)
let e_mir_node = "HIR-E18"
  (* a HIR construct outside the P1-m0 native subset (§P1-m0.2): control flow, calls,
     arrays, non-automatic storage, an unmodelled target, or a body that does not end
     in RETURN(expr). Fall-through/implicit-return semantics are unmeasured [TBD], so
     no MIR is invented for them. *)
let e_mir_numeric = "HIR-E19"
  (* numeric semantics outside the proven-safe domain (§P1-m0.3): an uninitialized read
     on the only path, a literal this backend cannot prove, a conversion whose rounding
     or overflow behaviour the profile leaves UNKNOWN, or an interval that can leave the
     declared-precision window W(p). Refusing honours the profile; nothing wraps,
     saturates or traps by assumption. *)
let e_mir_export = "HIR-E20"
  (* export selection or entry signature outside the native subset (§P1-m0.2): no
     procedure, more than one procedure, no source name, a name that cannot become a
     portable symbol, a --export option that matches no procedure, parameters, or a
     result type that is not FIXED BINARY(p,0). *)

(* E2E-54/P1-m1 additions (PLAN §P1-m1.3). APPENDED only; no existing code changes
   meaning (falsifier T10). These codes are raised by the CONSOLE LOWERING in
   hir_build.ml; the historical pipeline and every other HIR refusal never emit them. *)
let e_io_construct = "HIR-E21"
  (* console PUT/GET construct outside the accepted subset (§P1-m1.2), arms BY NAME:
     statement options (the io_opt key, e.g. FILE); kind (PUT EDIT/ITEM, GET EDIT/CONST);
     a leading control item (SKIP/PAGE/LINE); an item count other than 1; an item class
     that is not a single data item; a GET target that is not a scalar-name designation.
     Trailing control items never reach this code — they die in the parser (§P1-m1.1-3). *)
let e_io_domain = "HIR-E22"
  (* console DOMAIN outside the subset (§P1-m1.3): a PUT literal outside the printable
     range 32..126; an empty PUT literal; a defensive non-FIXED-BINARY(p,0) I/O operand
     type, expected UNEXERCISED because the declaration channels (E01/E02) precede it —
     same honest status as the P1-a2 E16 arm. *)
