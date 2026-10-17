(* bin/pli80c.ml — PL/I-80 front end → minimal 8080 codegen → .REL writer.

   usage: pli80c [-d] INPUT.PLI OUTPUT.REL

   Pipeline: parse → bind (storage layout) → codegen (fixed-bin int
   assignment subset) → Rel80 encode. Prints a compact disassembly trace
   to stderr with -d. *)

let segn sg = match sg with
  | Pli80.Rel80.Code -> "code" | Pli80.Rel80.Data -> "data"
  | Pli80.Rel80.Common -> "common" | Pli80.Rel80.Abs -> "abs"

let () =
  let args = Array.to_list Sys.argv in
  let dbg = List.mem "-d" args in
  let pos = List.filter (fun a -> a <> "-d") (List.tl args) in
  match pos with
  | [ src; dst ] ->
      let text = In_channel.with_open_bin src In_channel.input_all in
      (* CP/M EOF convention: everything from the first ^Z (0x1A) on is
         file padding, not source. Same convention as pli80parse.exe. *)
      let text =
        match String.index_opt text '\026' with
        | Some i -> String.sub text 0 i
        | None -> text
      in
      let blk = Pli80.Parser.parse_source text in
      let prog, data_size, vars = Pli80.Codegen.rows_of blk in
      let (items, code_len) =
        Pli80.Codegen.emit_program prog data_size vars blk.Pli80.Ast.bstmts
      in
      let rel = Pli80.Rel80.encode items in
      (* pad to 128-byte sector like DR *)
      let n = Bytes.length rel in
      let sectors = ((n + 127) / 128) * 128 in
      let buf = Bytes.make sectors '\000' in
      Bytes.blit_string (Bytes.unsafe_to_string rel) 0 buf 0 n;
      let oc = open_out_bin dst in
      output_string oc (Bytes.to_string buf);
      close_out oc;
      if dbg then begin
        Printf.eprintf "PROGRAM %s  CODE=%d DATA=%d ITEMS=%d -> %d bytes\n"
          prog code_len data_size (List.length items) sectors;
        let cn = ref 0 in
        List.iter
          (fun it ->
            let s =
              match it with
              | Pli80.Rel80.Data v -> Printf.sprintf "DATA     %02X" v
              | Pli80.Rel80.Reloc (sg, v) ->
                  Printf.sprintf "RELOC    %s %04X" (segn sg) v
              | Pli80.Rel80.Link (t, u, nm) ->
                  let vs = match u with
                    | None -> "-"
                    | Some (sg, v) -> Printf.sprintf "%s:%04X" (segn sg) v
                  in
                  Printf.sprintf "LINK     type=%d val=%s name=%s" t vs
                    (match nm with None -> "-" | Some x -> x)
            in
            Printf.eprintf "  %2d %s\n" !cn s;
            incr cn)
          items
      end;
      Printf.eprintf "wrote %s (%d bytes, code=%d data=%d)\n"
        dst sectors code_len data_size
  | _ ->
      prerr_endline "usage: pli80c [-d] INPUT.PLI OUTPUT.REL";
      exit 2
