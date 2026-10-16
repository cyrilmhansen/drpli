let () =
  let f = Sys.argv.(1) in
  let src = In_channel.with_open_bin f In_channel.input_all in
  let src =
    try String.sub src 0 (String.index src '\026') with Not_found -> src
  in
  List.iteri
    (fun i (t, pos) ->
      Printf.printf "%3d %d:%d %s\n" i pos.Pli80.Source.line pos.Pli80.Source.col
        (match t with
         | Pli80.Token.Ident { orig; _ } -> "ID " ^ orig
         | Num { text; _ } -> "NUM " ^ text
         | Str { value; _ } -> "STR " ^ value
         | Bit { value } -> "BIT " ^ value
         | Punct p -> "P " ^ Pli80.Token.show_punct p
         | EOF -> "EOF"))
    (Pli80.Lexer.tokenize src)
