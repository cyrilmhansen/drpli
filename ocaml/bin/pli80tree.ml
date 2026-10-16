let () =
  let f = Sys.argv.(1) in
  let src = In_channel.with_open_bin f In_channel.input_all in
  let src = try String.sub src 0 (String.index src '\026') with Not_found -> src in
  Pli80.Parser.dump_trees src
