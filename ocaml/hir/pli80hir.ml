(* bin/pli80hir.ml — deterministic HIR dump CLI (E2E-54/P0, PLAN §P0.5).

   Opt-in OBSERVATIONAL path only: lexer/parser + bind (the single semantic
   authority) + the read-only HIR adapter. It NEVER touches the historical
   codegen/Rel80 pipeline; the standard compiler invocation (pli80c) is
   byte-untouched (zero-edit set).

   Contract (PLAN §P0.5, falsifier F9):
     success          -> Hir.dump on stdout, exit 0
     any refusal      -> diagnostics on stderr, exit 2, ZERO stdout bytes
     usage/profile    -> exit 2

   usage: pli80hir [--profile NAME] INPUT.PLI *)

module D = Pli80_hir.Diagnostic

let usage = "usage: pli80hir [--profile NAME] INPUT.PLI"

let die ds =
  (* print_string on stderr then exit: stdout is NEVER touched on this path. *)
  prerr_endline (D.pp_all ds);
  exit 2

let run (profile_name : string) (src : string) : unit =
  let profile =
    match Pli80_hir.Target.lookup profile_name with
    | Some p -> p
    | None ->
        prerr_endline
          (Printf.sprintf "%s: unknown profile %S (known: %s, %s)" usage
             profile_name Pli80_hir.Target.dr_pli80_v1_4.Pli80_hir.Target.name
             Pli80_hir.Target.generic32_unspecified.Pli80_hir.Target.name);
        exit 2
  in
  let text =
    try In_channel.with_open_bin src In_channel.input_all
    with Sys_error msg -> die [ D.make D.e_parse msg ]
  in
  (* CP/M EOF convention, copied from pli80c.ml: everything from the first ^Z
     (0x1A) on is file padding, not source. *)
  let text =
    match String.index_opt text '\026' with
    | Some i -> String.sub text 0 i
    | None -> text
  in
  let blk =
    try Pli80.Parser.parse_source text
    with
    | Failure msg ->
        die [ D.make D.e_parse ("front end (lexer/parser) failed: " ^ msg) ]
  in
  (* bind failures arrive as plain Failure messages from the ONE semantic
     authority; they are reported, never reinterpreted (HIR-E01). *)
  match
    (try Pli80_hir.Hir_build.build blk profile with
     | Failure msg ->
         Error [ D.make D.e_bind ("bind (semantic authority) refused: " ^ msg) ])
  with
  | Ok p ->
      print_string (Pli80_hir.Hir.dump p);
      exit 0
  | Error ds -> die ds

let () =
  match List.tl (Array.to_list Sys.argv) with
  | ["--profile"; nm; src] -> run nm src
  | [src] -> run Pli80_hir.Target.dr_pli80_v1_4.Pli80_hir.Target.name src
  | _ ->
      prerr_endline usage;
      exit 2
