(* CLI: pli80parse [files...]  — parse each, report first error like
   pass-1 SYNTAX (line-based). Exit 0 iff all parse. *)

let () =
  let args = Array.sub Sys.argv 1 (Array.length Sys.argv - 1) in
  let fails = ref 0 in
  Array.iter
    (fun f ->
      let src = In_channel.with_open_bin f In_channel.input_all in
      (* strip CP/M ^Z (0x1A) tail and '$' terminator handling in parser *)
      try
        let stop =
          try Some (String.index src '\026') with Not_found -> None
        in
        let src = match stop with Some i -> String.sub src 0 i | None -> src in
        let _blk = Pli80.Parser.parse_source src in
        Printf.printf "%-24s OK\n" f
      with
      | Pli80.Lexer.Lex_error (pos, msg) ->
          incr fails;
          Printf.printf "%-24s LEX  %s: %s\n" f
            (string_of_int pos.Pli80.Source.line) msg
      | Pli80.Parser.Parse_error (pos, msg) ->
          incr fails;
          Printf.printf "%-24s SYN  line %d: %s\n" f pos.Pli80.Source.line msg
      | e ->
          incr fails;
          Printf.printf "%-24s ??? %s\n" f (Printexc.to_string e))
    args;
  exit (if !fails = 0 then 0 else 1)
