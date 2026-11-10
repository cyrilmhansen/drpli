(* hir/pli80mir.ml — opt-in MIR-text CLI (E2E-54/P1-m0, PLAN §P1-m0.5).

   Experimental NATIVE backend front door; it is NOT the historical compiler and
   is NOT linked into pli80c.exe (F1 remedy: every unit of this path lives in the
   separate pli80_hir library, ocaml/bin/ is untouched).

   Pipeline (brief §5, no second parse, no dump reading, no Semantic_env bypass):
     read file -> strip at the first ^Z (the CP/M end-of-file convention, copied
     honestly from pli80hir.ml) -> Pli80.Parser.parse_source
     -> Pli80_hir.Hir_build.build (the typed HIR + bind as the single semantic
     authority) -> Backend.Driver (Mir_backend.For (E)) with the runtime --export
     name closed over by [E].

   Contract (PLAN §P1-m0.5, falsifier T10):
     success        -> the deterministic MIR text on stdout, plus the -o file
                       (written only AFTER an [Ok] artifact), exit 0
     any refusal    -> diagnostics on stderr, exit 2, ZERO stdout bytes and NO
                       output file — a failed compile leaves no misleading artifact
     usage/profile  -> exit 2 (a missing --export is a usage error)

   E2E-54/P1-mD additions (PLAN §P1-mD.2, ADDITIVE flags; default behaviour
   FROZEN): with -g the backend is asked for the sidecar debug map (§P1-mD.3)
   and the .mir bytes are STILL byte-identical — the map is a separate file.
   --debug-map MAP names the map file; without it the map path is
   OUT.mir ^ ".p1md" (so -g without -o requires an explicit MAP). Usage errors,
   each exit 2 with a named reason: --debug-map WITHOUT -g; -g WITHOUT -o AND
   without an explicit MAP; -g given twice; --debug-map given twice; unknown
   option. The map file is written only AFTER the .mir write, on the [Ok] path
   only, and a map-write failure exits 2 with a named reason. The source path
   recorded inside the map is ABSOLUTE (§P1-mD.3 validation law): a relative
   argument is resolved against Unix.getcwd — the unix library is linked by
   THIS executable stanza only, never by the pli80_hir library.

   Nothing here runs an assembler, a C compiler or a linker: the OCaml side emits
   MIR TEXT and stops (brief §2). The host-side emitter lives in tools/mir_aot/.

   usage: pli80mir [-g] [--debug-map MAP] [--profile NAME] --export NAME
                   [-o OUT.mir] INPUT.PLI *)

module D = Pli80_hir.Diagnostic
module Mir = Pli80_hir.Mir_backend

let usage =
  "usage: pli80mir [-g] [--debug-map MAP] [--profile NAME] --export NAME \
   [-o OUT.mir] INPUT.PLI"

let die ds =
  (* print on stderr then exit: stdout is NEVER touched on this path. *)
  prerr_endline (D.pp_all ds);
  exit 2

let usage_die reason =
  prerr_endline usage;
  prerr_endline ("pli80mir: " ^ reason);
  exit 2

(* Compile-time witnesses (PLAN §P1-m0.5): [Mir.For] is a [Backend.BACKEND] and
   [Backend.Driver] accepts it. This is a type-checking test only — no code here
   runs at program start, and the witness export name is never used. *)
module _ = Pli80_hir.Backend.Driver (Mir.For (struct
                                                let export = "witness"
                                              end))

let absolute_path (p : string) : string =
  if String.length p > 0 && p.[0] = '/' then p
  else Filename.concat (Unix.getcwd ()) p

let run (profile_name : string) (export : string) (out_path : string option)
    (debug : bool) (map_path : string option) (src : string) : unit =
  let profile =
    match Pli80_hir.Target.lookup profile_name with
    | Some p -> p
    | None ->
        prerr_endline
          (Printf.sprintf "%s: unknown profile %S (known: %s, %s)" usage profile_name
             Pli80_hir.Target.dr_pli80_v1_4.Pli80_hir.Target.name
             Pli80_hir.Target.generic32_unspecified.Pli80_hir.Target.name);
        exit 2
  in
  let text =
    try In_channel.with_open_bin src In_channel.input_all
    with Sys_error msg -> die [ D.make D.e_parse msg ]
  in
  (* CP/M EOF convention, copied from pli80hir.ml: everything from the first ^Z
     (0x1A) on is file padding, not source. *)
  let text =
    match String.index_opt text '\026' with
    | Some i -> String.sub text 0 i
    | None -> text
  in
  let blk =
    try Pli80.Parser.parse_source text
    with Failure msg -> die [ D.make D.e_parse ("front end (lexer/parser) failed: " ^ msg) ]
  in
  (* bind failures arrive as plain Failure messages from the ONE semantic
     authority; they are reported, never reinterpreted (HIR-E01). *)
  match
    (try Pli80_hir.Hir_build.build blk profile with
     | Failure msg ->
         Error [ D.make D.e_bind ("bind (semantic authority) refused: " ^ msg) ])
  with
  | Error ds -> die ds
  | Ok prog ->
      (* The export name is a runtime value; the BACKEND instance closes over it
         (see the DEVIATION note in mir_backend.ml). The instance is NOT named a
         single uppercase letter: that trips the F8 mnemonic grep (measured).
         P1-mD: the DEFAULT path keeps the Driver plumbing byte-for-byte; the
         -g path calls Mir.compile directly with the absolute source path so the
         backend builds the sidecar (§P1-mD.3). *)
      let compiled =
        if debug then
          Mir.compile ~profile ~export ~debug_source:(Some (absolute_path src)) prog
        else
          let module Entry = Mir.For (struct
                                        let export = export
                                      end) in
          let module Driver = Pli80_hir.Backend.Driver (Entry) in
          Driver.run ~profile prog
      in
      (match compiled with
       | Error ds -> die ds
       | Ok art ->
           (* The artifact exists: the -o file is written FIRST so that a failing
              write still leaves stdout empty and rc non-zero. The debug map is
              written only AFTER the .mir file, still before any stdout (§ law:
              a refusal writes NO output files; a map lives after the frozen
              .mir bytes). *)
           (match out_path with
            | None -> ()
            | Some o ->
                (try
                   Out_channel.with_open_bin o
                     (fun ch -> Out_channel.output_string ch art.Mir.mir_text)
                 with Sys_error msg ->
                   prerr_endline ("pli80mir: cannot write " ^ o ^ ": " ^ msg);
                   exit 2));
           (if debug then
              let map_file =
                match map_path with
                | Some m -> m
                | None ->
                    (* parse_args guarantees -g WITHOUT -o carries an explicit
                       MAP, so this arm is reached only with out_path = Some. *)
                    match out_path with
                    | Some o -> o ^ ".p1md"
                    | None ->
                        usage_die
                          "-g without -o requires an explicit --debug-map MAP"
              in
              match art.Mir.debug_map with
              | None ->
                  prerr_endline
                    ("pli80mir: the debug compile produced no map for " ^ map_file);
                  exit 2
              | Some m ->
                  (try
                     Out_channel.with_open_bin map_file
                       (fun ch -> Out_channel.output_string ch m)
                   with Sys_error msg ->
                     prerr_endline
                       ("pli80mir: cannot write " ^ map_file ^ ": " ^ msg);
                     exit 2));
           print_string art.Mir.mir_text;
           exit 0)

(* Argument parsing is explicit and loud: every unexplained shape is a usage
   error (rc 2), a repeated option is a usage error, and --export is REQUIRED. *)
let parse_args (argv : string list) :
    string * string * string option * bool * string option * string =
  let rec go profile export out debug map files = function
    | [] -> (profile, export, out, debug, map, files)
    | "--profile" :: v :: tl ->
        if profile <> "" then usage_die "--profile given twice" else ();
        if String.length v > 0 && v.[0] = '-' then usage_die "--profile needs a name"
        else go v export out debug map files tl
    | "--export" :: v :: tl ->
        if export <> "" then usage_die "--export given twice" else ();
        if String.length v > 0 && v.[0] = '-' then usage_die "--export needs a name"
        else go profile v out debug map files tl
    | "-o" :: v :: tl ->
        if out <> None then usage_die "-o given twice" else ();
        if String.length v > 0 && v.[0] = '-' then usage_die "-o needs a file name"
        else go profile export (Some v) debug map files tl
    | "-g" :: tl ->
        if debug then usage_die "-g given twice" else ();
        go profile export out true map files tl
    | "--debug-map" :: v :: tl ->
        if map <> None then usage_die "--debug-map given twice" else ();
        if String.length v > 0 && v.[0] = '-' then
          usage_die "--debug-map needs a file name"
        else go profile export out debug (Some v) files tl
    | f :: tl ->
        if String.length f > 0 && f.[0] = '-' then usage_die ("unknown option " ^ f)
        else go profile export out debug map (f :: files) tl
  in
  let profile, export, out, debug, map, files = go "" "" None false None [] argv in
  if export = "" then usage_die "--export NAME is required (the single MIR entry name)";
  (* P1-mD usage arms (§P1-mD.2): checked AFTER the loop so the flag order in
     the command line does not matter. *)
  if map <> None && not debug then
    usage_die "--debug-map MAP is accepted only together with -g";
  if debug && out = None && map = None then
    usage_die
      "-g without -o requires an explicit --debug-map MAP (the default map path \
       is OUT.mir ^ .p1md)";
  match files with
  | [ f ] -> (profile, export, out, debug, map, f)
  | [] -> usage_die "one input .pli file is required"
  | _ -> usage_die "exactly one input file is required"

let () =
  let argv = List.tl (Array.to_list Sys.argv) in
  let profile, export, out, debug, map, src = parse_args argv in
  let profile_name =
    if profile = "" then Pli80_hir.Target.dr_pli80_v1_4.Pli80_hir.Target.name else profile
  in
  run profile_name export out debug map src
