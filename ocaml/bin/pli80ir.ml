(* pli80ir FILE — parse, bind, lower expressions, print the $V-format
   opcode stream (for diffing against DR $V goldens via ir_gate). *)

let () =
  if Array.length Sys.argv < 2 then begin
    prerr_endline "usage: pli80ir FILE"; exit 2
  end;
  let file = Sys.argv.(1) in
  let src =
    let ic = open_in_bin file in
    let n = in_channel_length ic in
    let s = really_input_string ic n in
    close_in ic; s
  in
  let blk = Pli80.Parser.parse_source src in
  let rows = Pli80.Bind.bind_rows blk in
  let vars =
    List.filter_map
      (fun (n, rt, off, _auto) ->
        let ty : Pli80.Ir.ty option =
          match rt with
          | Pli80.Bind.RTbin p -> Some (Pli80.Ir.Tbin p)
          | Pli80.Bind.RTdec (p, s) -> Some (Pli80.Ir.Tdec (p, s))
          | Pli80.Bind.RTfloat _ -> Some Pli80.Ir.Tflt
          | Pli80.Bind.RTchar (n, v) -> Some (Pli80.Ir.Tchr (n, v))
          | Pli80.Bind.RTbit n -> Some (Pli80.Ir.Tbit n)
          | _ -> None
        in
        match ty with Some t -> Some (n, (off, t)) | None -> None)
      rows
  in
  (* pool pre-scan: float/dec literal sizes in source order; base =
     total pool bytes (pool sits BELOW auto vars in the data frame) *)
  let rec lit_pool (e : Pli80.Ast.expr) (acc : (int * bool) list) =
    match e.Pli80.Ast.e with
    | Pli80.Ast.Enumber t ->
        let d = String.concat "" (String.split_on_char '_' t) in
        if not (String.contains d '.') then acc
        else begin
          let isf =
            let best = ref max_int in
            String.iteri (fun i c -> if c = 'e' || c = 'E' then best := min !best i) d;
            !best <> max_int
          in
          if isf then (4, true) :: acc
          else
            let fps =
              match String.index_opt d '.' with
              | Some i -> String.length d - i - 1
              | None -> 0
            in
            if fps > 0 then (8, false) :: acc else acc
        end
    | Pli80.Ast.Ebinary (_, l, r) ->
        let a1 = lit_pool l acc in lit_pool r a1
    | Pli80.Ast.Eprefix (_, x) -> lit_pool x acc
    | _ -> acc
  in
  let stmts_pool ss acc =
    List.fold_left
      (fun a s ->
        match s.Pli80.Ast.st with
        | Pli80.Ast.Sassign { rhs; _ } -> lit_pool rhs a
        | _ -> a)
      acc ss
  in
  let pool_items = stmts_pool blk.Pli80.Ast.bstmts [] in
  let base = List.fold_left (fun a (sz, _) -> a + sz) 0 pool_items in
  if Sys.getenv_opt "IR_DEBUG" <> None then
    Printf.eprintf "DBG base=%d items=%d stmts=%d\n" base
      (List.length pool_items) (List.length blk.Pli80.Ast.bstmts);
  let env =
    { Pli80.Ir.vars; base; pool = ref 0; out = []; assigned = [] }
  in
  Pli80.Ir.lower_block env blk;
  List.iter print_endline env.out
