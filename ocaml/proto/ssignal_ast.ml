(* ocaml/proto/ssignal_ast.ml — [E2E-52/P3-10] brief step 2: AST-preservation
   test for the SIGNAL frontend repair.

   The defect (PLAN §P3-10 §7; repaired in d84665c): parser.ml parsed the
   conditional-name argument list of `SIGNAL con(args) [FROM expr]` and bound
   it to `_sargs', DISCARDING it, so `signal error(1)' was indistinguishable
   from a bare `signal error;' at every later stage.  The repair gives
   Ast.Ssignal a `cargs : expr list' field (mirroring Son/Srevert) and keeps
   the FROM target as `target : expr option' — kept as parsed, NEVER lowered.

   This prototype asserts, at PARSE level ONLY (no bind, no codegen, no
   oracle), that cargs and target are PRESERVED for every SIGNAL shape the
   e52p10 campaign measured — INCLUDING the shapes codegen still REFUSES BY
   NAME (WF/WG single witnesses, multi-arg, FROM, and the WL bare-file form
   which DR itself refuses with PASS 2 SYNTAX).  Preservation is the property
   under test; the accept/refuse verdict of each shape belongs ONLY to
   spec/CLAIMS.md [C368] and the registered goldens.  Isolated like arch1:
   nothing in ../lib or ../bin depends on this target. *)

module A = Pli80.Ast
module P = Pli80.Parser

(* Canonical rendering of the AST shapes we assert against — readable output
   on failure, no positional/structural assumptions beyond what we check. *)
let pp_binop = function
  | A.Add -> "Add"
  | A.Sub -> "Sub"
  | A.Mul -> "Mul"
  | A.Div -> "Div"
  | _ -> "OP"

let rec pp_e (x : A.expr) : string =
  match x.A.e with
  | A.Eident n -> "Eident:" ^ n.A.orig
  | A.Enumber t -> "Enumber:" ^ t
  | A.Estring s -> "Estring:" ^ s
  | A.Ebinary (op, l, r) ->
      "Ebinary(" ^ pp_binop op ^ "," ^ pp_e l ^ "," ^ pp_e r ^ ")"
  | _ -> "?"

let show_opt = function
  | None -> "None"
  | Some s -> "Some(" ^ s ^ ")"

(* One SIGNAL statement per program; declarations mirror the probes so the
   text is representative.  parse-level only, so undeclared names are fine. *)
let prog body =
  "T1: procedure options(main);\n\
  \   dcl x fixed bin;\n\
  \   dcl n fixed bin;\n\
  \   " ^ body ^ "\n\
   end T1;"

let find_signals src =
  let blk = P.parse_source src in
  List.filter_map
    (fun (s : A.stmt) ->
      match s.A.st with
      | A.Ssignal { cond; cargs; target } ->
          Some (cond, List.map pp_e cargs, Option.map pp_e target)
      | _ -> None)
    blk.A.bstmts

let fail = ref 0

let check label body (wcond, wcargs, wtarget) =
  let src = prog body in
  let got =
    try `Signals (find_signals src)
    with e -> `Raised (Printexc.to_string e)
  in
  match got with
  | `Raised msg ->
      Printf.printf "%-24s FAIL raised: %s\n" label msg;
      incr fail
  | `Signals [ (c, a, t) ] ->
      if c = wcond && a = wcargs && t = wtarget then
        Printf.printf "%-24s PASS  cond=%s cargs=[%s] target=%s\n" label c
          (String.concat "; " a) (show_opt t)
      else begin
        Printf.printf
          "%-24s FAIL\n  want cond=%s cargs=[%s] target=%s\n\
          \  got  cond=%s cargs=[%s] target=%s\n"
          label wcond (String.concat "; " wcargs) (show_opt wtarget)
          c (String.concat "; " a) (show_opt t);
        incr fail
      end
  | `Signals xs ->
      Printf.printf "%-24s FAIL found %d signal stmts (want 1)\n" label
        (List.length xs);
      incr fail

(* Panel: shapes MEASURED by campaign e52p10 (WA..WK accepted goldens; WL
   dr-refuses) plus the still-REFUSED shapes whose AST preservation the brief
   names — multi-arg, FROM, and the WF/WG expression/variable args.  cond is
   the lexer's uppercase key; Enumber keeps the literal text as written. *)
let cases =
  [
    (* armed + byte-exact (registered probes) *)
    ("WA-bare", "signal error;", ("ERROR", [], None));
    ("WC-error1", "signal error(1);", ("ERROR", [ "Enumber:1" ], None));
    ("WD-error255", "signal error(255);", ("ERROR", [ "Enumber:255" ], None));
    (* WE falsifier: NO 0..255 check exists — operand is full 16-bit *)
    ("WE-error256", "signal error(256);", ("ERROR", [ "Enumber:256" ], None));
    ("WH-endpage", "signal endpage(printfile);",
     ("ENDPAGE", [ "Eident:printfile" ], None));
    ("WI-endfile", "signal endfile(f);", ("ENDFILE", [ "Eident:f" ], None));
    (* single DR witnesses, armed NEITHER (H-D2 no-generalise) — the parser
       must still preserve their arguments for the eventual fix *)
    ("WG-var-arg", "signal error(n);", ("ERROR", [ "Eident:n" ], None));
    ("WF-expr-arg", "signal error(1+1);",
     ("ERROR", [ "Ebinary(Add,Enumber:1,Enumber:1)" ], None));
    (* multi-arg: UNMEASURED on the SIGNAL route; refused BY NAME in codegen *)
    ("multi-arg", "signal error(1,2);",
     ("ERROR", [ "Enumber:1"; "Enumber:2" ], None));
    (* FROM: kept as parsed, NEVER lowered; no DR object witnesses it here *)
    ("from-bare", "signal error from x;", ("ERROR", [], Some "Eident:x"));
    ("from-args", "signal error(1) from y;",
     ("ERROR", [ "Enumber:1" ], Some "Eident:y"));
    (* WL: DR dr-refuses `signal endfile;' (PASS 2 SYNTAX, NO .REL); my
       frontend parses and preserves it — the refusal is codegen's, BY NAME. *)
    ("WL-drrefuse", "signal endfile;", ("ENDFILE", [], None));
  ]

let () =
  Printf.printf
    "ssignal_ast: [E2E-52/P3-10] parse-level preservation of Ssignal.cargs \
     and FROM target\n\
     (asserts the frontend repair d84665c; verdicts of each shape live in \
     spec/CLAIMS.md [C368])\n\n";
  List.iter (fun (l, b, w) -> check l b w) cases;
  Printf.printf "\nSSIGNAL_AST FAILS: %d\n" !fail;
  if !fail > 0 then exit 1 else exit 0
