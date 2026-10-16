(* pli80bind [--inc DIR] FILE — parse, bind, print $S-format dump.
   %include is expanded TEXTUALLY like the compiler's preprocessor
   (artefact .DCL files are raw fragments spliced mid-declaration). *)

let find_sub ?(start = 0) sub s =
  let n = String.length s and m = String.length sub in
  let rec go i =
    if i + m > n then None
    else if String.sub s i m = sub then Some i
    else go (i + 1)
  in
  go start

let rec expand_includes src dirs =
  let key = "%include '" in
  let hay = String.lowercase_ascii src in
  match find_sub key hay with
  | None -> src
  | Some at ->
      let q_start = at + String.length key in
      match find_sub ~start:q_start "'" hay with
      | None -> src
      | Some qe ->
          if qe < q_start then src
          else begin
            let fname = String.sub src q_start (qe - q_start) in
            (* replacement spans `%include 'name' only; the ORIGINAL
               statement semicolon stays, exactly like the compiler's
               text splicing (fragments like FCB.DCL depend on it) *)
            let candidates =
              [ fname; String.uppercase_ascii fname;
                String.capitalize_ascii fname ]
            in
            let candidates =
              [ fname; String.uppercase_ascii fname;
                String.capitalize_ascii fname ]
            in
            let found =
              let rec search = function
                | [], _ -> None
                | d :: drest, names ->
                    let rec try_names = function
                      | [] -> search (drest, candidates)
                      | b :: bre ->
                          let p = Filename.concat d b in
                          if Sys.file_exists p then Some p else try_names bre
                    in
                    try_names names
              in search (dirs, candidates)
            in
            match found with
            | None ->
                Printf.eprintf "pli80bind: include %s not found; skipping directive@." fname;
                let before = String.sub src 0 at in
                let after = String.sub src (qe + 1) (String.length src - qe - 1) in
                expand_includes (before ^ after) dirs
            | Some path ->
                let content =
                  In_channel.with_open_bin path In_channel.input_all
                in
                let content =
                  String.map (fun c ->
                      if c = '\r' || c = '\026' then ' ' else c) content
                in
                let before = String.sub src 0 at in
                let after = String.sub src (qe + 1) (String.length src - qe - 1) in
                expand_includes (before ^ content ^ after) dirs
          end

let () =
  let rec split acc = function
    | "--inc" :: d :: tl -> split (d :: acc) tl
    | [ f ] -> (List.rev acc, f)
    | f :: tl when tl = [] -> (List.rev acc, f)
    | _ :: tl -> split acc tl
    | [] -> Printf.eprintf "usage: pli80bind [--inc DIR] FILE\n"; exit 2
  in
  let (dirs, file) = split [] (List.tl (Array.to_list Sys.argv)) in
  let dirs = dirs @ [ "artefacts"; "probes"; Filename.dirname file ] in
  let src = In_channel.with_open_bin file In_channel.input_all in
  let src =
    try String.sub src 0 (String.index src '\026') with Not_found -> src
  in
  let src = expand_includes src dirs in
  let blk = Pli80.Parser.parse_source src in
  print_string (Pli80.Bind.dump_s blk)
