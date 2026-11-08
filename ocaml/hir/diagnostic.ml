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
