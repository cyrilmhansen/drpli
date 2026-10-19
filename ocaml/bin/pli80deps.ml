(* bin/pli80deps.ml — E2E-11 step 0: per-program FEATURE/BLOCKER SET extractor.

   usage: pli80deps FILE.PLI [FILE.PLI ...]

   Motivation (user correction #1): ranking candidates by the FIRST refusal my
   compiler reports is useless, because most programs need several kinds at once.
   This tool walks the parsed AST (and the bound storage rows when binding
   succeeds) and emits the COMPLETE set of feature tags a program touches, each
   with a count and the first source line that uses it, so the audit can separate
   independent language features from coupled implementation requirements.

   It deliberately does NOT decide what is hard.  It reports what is used.

   Output (one line per tag, stable for diffing):
     PROG <path>
     PARSE ok | PARSE FAIL <msg>
     BIND  ok | BIND FAIL <msg> | BIND skipped
     TAG <tag> count=<n> first_line=<l> <detail>
*)

open Pli80

let tbl : (string, int * int * string) Hashtbl.t = Hashtbl.create 64

let tag ?(detail = "") (k : string) (line : int) =
  let (n, first, d) =
    match Hashtbl.find_opt tbl k with Some x -> x | None -> (0, line, detail)
  in
  Hashtbl.replace tbl k (n + 1, first, if d = "" && detail <> "" then detail else d)

let lower = String.lowercase_ascii
let nline (n : Ast.name) = n.Ast.pos.Source.line

(* ---------- expressions ---------- *)

let rec walk_expr (e : Ast.expr) =
  let line = e.Ast.epos.Source.line in
  match e.Ast.e with
  | Ast.Eident _ -> ()
  | Ast.Eqstruct (_, _) -> tag ~detail:"qualified reference a.b" "QUALIFIED_REF" line
  | Ast.Eqptr (_, _) -> tag ~detail:"pointer dereference a->b" "POINTER_DEREF" line
  | Ast.Enumber _ -> ()
  | Ast.Estring _ -> ()
  | Ast.Ebit _ -> tag ~detail:"bit literal '1'b / '1010'b" "BIT_LITERAL" line
  | Ast.Eprefix (p, x) ->
      (match p with
       | Ast.NegL -> tag ~detail:"prefix ^ (logical not on bit strings)" "BIT_NOT_PREFIX" line
       | _ -> ());
      walk_expr x
  | Ast.Ebinary (op, l, r) ->
      (match op with
       | Ast.BitCat ->
           tag ~detail:"!! bit-string concatenation" "BIT_CONCAT" line
       | Ast.Cat -> tag ~detail:"|| // character concatenation" "CHAR_CONCAT" line
       | Ast.And | Ast.Or | Ast.XorNe ->
           tag ~detail:"& | ^ (numeric or bit: needs operand kinds)"
             "LOGICAL_OR_BIT_OPS" line
       | Ast.AndThen | Ast.OrElse ->
           tag ~detail:"&& || short-circuit" "SHORT_CIRCUIT_OPS" line
       | Ast.Exp -> tag ~detail:"** exponentiation" "EXPONENTIATION" line
       | _ -> ());
      walk_expr l; walk_expr r
  | Ast.Econd x -> walk_expr x
  | Ast.Esuffix (hd, args) ->
      (match hd.Ast.e with
       | Ast.Eident n when args <> [] ->
           tag ~detail:("call/index " ^ n.Ast.orig) "SUFFIX_APPLY" line
       | _ -> ());
      walk_expr hd; List.iter walk_expr args
  | Ast.Ebuilt (k, args) ->
      tag ~detail:("builtin " ^ k) ("BUILTIN:" ^ lower k) line;
      List.iter walk_expr args
  | Ast.Eformat_ref n ->
      tag ~detail:("R(" ^ n.Ast.orig ^ ") format reference") "FORMAT_REF" line
  | Ast.Epicture s -> tag ~detail:("P'" ^ s ^ "'") "PICTURE_LITERAL" line

(* ---------- declarations ---------- *)

let walk_type (t : Ast.basic_type) (line : int) =
  match t with
  | Ast.Tfixed { dec; prec; scale } ->
      (match prec with
       | Some p ->
           let txt = match p.Ast.e with Ast.Enumber k -> k | _ -> "<expr>" in
           tag ~detail:((if dec then "dec(" else "bin(") ^ txt ^ ")")
             (if dec then "DEC_PRECISION" else "BIN_PRECISION") line
       | None -> ());
      (match scale with Some _ -> tag "FIXED_SCALE" line | None -> ())
  | Ast.Tfloat { prec } ->
      let d =
        match prec with
        | Some p ->
            "float binary" ^
            (match p.Ast.e with Ast.Enumber k -> "(" ^ k ^ ")" | _ -> "(expr)")
        | None -> "float (default precision)"
      in
      tag ~detail:d "FLOAT_DECL" line
  | Ast.Tchar { varying; len } ->
      if varying then
        tag ~detail:("character(" ^
                     (match len with
                      | Some e -> (match e.Ast.e with Ast.Enumber k -> k | _ -> "expr")
                      | None -> "?") ^ ") varying") "VARYING_DECL" line
      else (match len with Some _ -> () | None -> tag "CHAR_UNBOUNDED" line)
  | Ast.Tbit { len } ->
      tag ~detail:("bit(" ^
                   (match len with
                    | Some e -> (match e.Ast.e with Ast.Enumber k -> k | _ -> "expr")
                    | None -> "1 default") ^ ")") "BIT_DECL" line
  | Ast.Tptr -> tag ~detail:"POINTER" "POINTER_DECL" line
  | Ast.Tfile -> tag ~detail:"FILE variable" "FILE_DECL" line
  | Ast.Tentry { opts } ->
      tag ~detail:("ENTRY with " ^ string_of_int (List.length opts) ^ " param types")
        "ENTRY_DECL" line

let walk_attr (a : Ast.attr) =
  let line = a.Ast.apos.Source.line in
  let k = lower a.Ast.akey in
  match k with
  | "static" -> tag ~detail:"STATIC" "STATIC_ATTR" line
  | "initial" ->
      tag ~detail:("INITIAL(" ^
                   String.concat "," (List.map (fun e ->
                       match e.Ast.e with
                       | Ast.Enumber x -> x
                       | Ast.Estring x -> "'" ^ x ^ "'"
                       | Ast.Ebit x -> "'" ^ x ^ "'b"
                       | _ -> "...") a.Ast.aargs) ^ ")") "INITIAL_ATTR" line;
      List.iter walk_expr a.Ast.aargs
  | "based" -> tag ~detail:"BASED(ptr)" "BASED_ATTR" line; List.iter walk_expr a.Ast.aargs
  | "external" -> tag ~detail:"EXTERNAL" "EXTERNAL_ATTR" line
  | "recursive" -> tag ~detail:"RECURSIVE" "RECURSIVE_ATTR" line
  | "reenter" -> tag ~detail:"REENTER" "REENTER_ATTR" line
  | "returns" ->
      tag ~detail:"RETURNS" "RETURNS_ATTR" line;
      List.iter (fun t -> walk_type t line) a.Ast.atypes
  | "label" -> tag ~detail:"LABEL type" "LABEL_AS_DATA" line
  | "def" | "defined" -> tag ~detail:"DEF" "DEF_ATTR" line
  | "aligned" -> tag ~detail:"ALIGNED" "ALIGNED_ATTR" line
  | _ -> tag ~detail:("attribute " ^ k) ("OTHER_ATTR:" ^ k) line

let walk_dcl (d : Ast.dcl) =
  let line = nline d.Ast.dname in
  (match d.Ast.dlevel with
   | Some _ -> tag ~detail:"leading level number (structure/group)" "STRUCTURE_LEVEL" line
   | None -> ());
  List.iter
    (fun dim ->
      match dim with
      | Ast.Dim_bound _ -> tag ~detail:"array dimension" "ARRAY_DIM" line
      | Ast.Dim_star -> tag ~detail:"assumed size (*)" "ASSUMED_DIM" line)
    d.Ast.ddims;
  (match d.Ast.dtype with Some t -> walk_type t line | None -> ());
  List.iter walk_attr d.Ast.dattrs;
  (match d.Ast.dinit with
   | Some i ->
       tag ~detail:"declaration initializer (= / initial)" "DCL_INIT" line;
       let rec rep x =
         match x with
         | Ast.Init_rep (n, xs) ->
             tag ~detail:("replication " ^ string_of_int n) "INIT_REPLICATION" line;
             List.iter rep xs
         | Ast.Init_expr e -> walk_expr e
       in
       rep i
   | None -> ());
  (match d.Ast.dpre with
   | Some (k, _) -> tag ~detail:("preprocessor splice in dcl list: " ^ k)
       "PREPROC_IN_DCL" line
   | None -> ())

(* ---------- items ---------- *)

let rec walk_item (it : Ast.put_item) =
  let line = 0 in
  match it with
  | Ast.Pi_fmt { fkey; fargs; fcount } ->
      tag ~detail:("format spec " ^ fkey) ("FORMAT_SPEC:" ^ lower fkey) line;
      List.iter walk_expr fargs; Option.iter walk_expr fcount
  | Ast.Pi_rep (_, _) ->
      tag ~detail:"(x do n=..) generated item" "PUT_GENERATED_ITEM" line
  | Ast.Pi_repgrp (e, its) ->
      tag ~detail:"counted group 2(..)" "PUT_COUNTED_GROUP" line;
      walk_expr e; List.iter walk_item its
  | Ast.Pi_data e -> walk_expr e
  | Ast.Pi_ctl (k, eo) ->
      tag ~detail:("control item " ^ k) ("IO_CONTROL:" ^ lower k) line;
      Option.iter walk_expr eo
  | Ast.Pi_pic s -> tag ~detail:("P'" ^ s ^ "'") "PICTURE_LITERAL" line
  | Ast.Pi_remote n -> tag ~detail:("R(" ^ n.Ast.orig ^ ")") "FORMAT_REF" line
  | Ast.Pi_group its -> List.iter walk_item its
  | Ast.Pi_fmtlist its -> List.iter walk_item its

(* ---------- statements ---------- *)

let rec walk_stmt (s : Ast.stmt) =
  let line = s.Ast.spos.Source.line in
  (match s.Ast.st with
   | Ast.Sdcl ds -> List.iter walk_dcl ds
   | Ast.Snull _ -> ()
   | Ast.Sassign { lhs; rhs } -> walk_expr lhs; walk_expr rhs
   | Ast.Sgoto { tgt; subscript } ->
       if subscript <> [] then
         tag ~detail:("goto " ^ tgt.Ast.orig ^ "(i) -- label parameter")
           "GOTO_LABEL_PARAM" line
       else tag "GOTO" line
   | Ast.Sif { cond; then_; els } ->
       walk_expr cond; walk_stmt then_; Option.iter walk_stmt els
   | Ast.Sdobegin ss -> List.iter walk_stmt ss
   | Ast.Sdoto { ind; from; by; while_; to_; body; _ } ->
       ignore ind;
       walk_expr from; Option.iter walk_expr by;
       Option.iter walk_expr while_; Option.iter walk_expr to_;
       walk_stmt body
   | Ast.Sdowhile { cond; body } -> walk_expr cond; walk_stmt body
   | Ast.Sdoforever b -> walk_stmt b
   | Ast.Sproc b -> walk_block b
   | Ast.Sput { stream; on_opts; kind; items } ->
       tag ("PUT_"
            ^ match kind with
              | Ast.List_ -> "LIST" | Ast.Edit -> "EDIT"
              | Ast.Item -> "ITEM" | Ast.Editsk _ -> "EDIT_SKIP") line;
       (match stream with
        | Some e ->
            walk_expr e;
            (match e.Ast.e with
             | Ast.Eident n ->
                 tag ~detail:("PUT FILE(" ^ n.Ast.orig ^ ")-style stream operand")
                   "PUT_STREAM" line
             | _ -> ())
        | None -> ());
       List.iter walk_io_opt on_opts;
       List.iter walk_item items
   | Ast.Sget { stream; on_opts; kind; items } ->
       tag ("GET_"
            ^ match kind with
              | Ast.List_ -> "LIST" | Ast.Edit -> "EDIT" | Ast.Const_ -> "CONST") line;
       (match stream with
        | Some e ->
            walk_expr e;
            (match e.Ast.e with
             | Ast.Eident n ->
                 tag ~detail:("GET stream operand " ^ n.Ast.orig) "GET_STREAM" line
             | _ -> ())
        | None -> ());
       List.iter walk_io_opt on_opts;
       List.iter walk_item items
   | Ast.Sfilestmt { key; file; opts } ->
       tag ~detail:("file statement " ^ key) ("FILE_STMT:" ^ lower key) line;
       Option.iter walk_expr file; List.iter walk_io_opt opts
   | Ast.Sedit { target; opts } ->
       tag "EDIT_STMT" line; walk_expr target; List.iter walk_io_opt opts
   | Ast.Sreadwv { dir; file; to_ } ->
       tag ~detail:("READ/WRITE " ^ dir) "READ_WRITE_FILE" line;
       walk_expr file; walk_expr to_
   | Ast.Sreturn eo -> Option.iter walk_expr eo
   | Ast.Sstop eo -> Option.iter walk_expr eo
   | Ast.Sexit _ -> tag "EXIT" line
   | Ast.Son { cond; cargs = _; handler } ->
       tag ~detail:("ON " ^ cond) ("ON_COND:" ^ lower cond) line;
       walk_stmt handler
   | Ast.Ssignal { cond; target } ->
       tag ~detail:("SIGNAL " ^ cond) ("SIGNAL_COND:" ^ lower cond) line;
       Option.iter walk_expr target
   | Ast.Selse b -> walk_stmt b
   | Ast.Sdeclare_fail _ -> tag "DECLARED_STMT" line
   | Ast.Sprocedure_stmt { target; args } ->
       tag "CALL_STMT" line; walk_expr target; List.iter walk_expr args
   | Ast.Salloc { ptr; based } ->
       tag "ALLOCATE" line; walk_expr ptr; Option.iter walk_expr based
   | Ast.Sfree es -> tag "FREE" line; List.iter walk_expr es
   | Ast.Sassign_label { labels; to_ } ->
       tag ~detail:("assign label(s) " ^
                    String.concat "," (List.map (fun n -> n.Ast.orig) labels))
         "LABEL_ASSIGN" line;
       walk_expr to_
   | Ast.Sformat items ->
       tag "FORMAT_DECL" line; List.iter walk_item items
   | Ast.Spicturestmt _ -> tag "PICTURE_STMT" line
   | Ast.Spreproc { directive; args } ->
       tag ~detail:("%" ^ directive ^ " " ^ String.concat " " args)
         ("PREPROC:" ^ lower directive) line);
  if s.Ast.slabels <> [] then
    tag ~detail:(String.concat "," (List.map (fun n -> n.Ast.orig) s.Ast.slabels))
      "STMT_LABEL" line

and walk_io_opt (o : Ast.io_opt) =
  let k = lower o.Ast.io_key in
  tag ~detail:("io option " ^ k) ("IO_OPT:" ^ k) 0;
  Option.iter walk_expr o.Ast.io_val

and walk_block (b : Ast.block_stmt) =
  let blk = b.Ast.blk in
  let line = b.Ast.bpos.Source.line in
  (match blk.Ast.bname with
   | Some n -> tag ~detail:n.Ast.orig "PROCEDURE_BLOCK" line
   | None -> ());
  (match blk.Ast.bparams with
   | [] -> ()
   | ps ->
       tag ~detail:(string_of_int (List.length ps) ^ " formals ("
                    ^ String.concat "," (List.map (fun n -> n.Ast.orig) ps) ^ ")")
         "PROC_FORMALS" line);
  List.iter
    (fun (k, args) ->
      tag ~detail:("OPTIONS(" ^ k ^ ")") ("BLOCK_OPT:" ^ lower k) line;
      List.iter walk_expr args)
    blk.Ast.bopts;
  List.iter walk_attr blk.Ast.bsuffix;
  List.iter walk_dcl blk.Ast.bdecls;
  List.iter walk_stmt blk.Ast.bstmts

(* ---------- driver ---------- *)

let strip_eof raw =
  match String.index_opt raw '\026' with
  | Some i -> String.sub raw 0 i
  | None -> raw

let analyse path =
  Hashtbl.clear tbl;
  Printf.printf "PROG %s\n" path;
  let raw = In_channel.with_open_bin path In_channel.input_all in
  let text = strip_eof raw in
  let blk_opt =
    try
      let blk = Pli80.Parser.parse_source text in
      Printf.printf "PARSE ok\n";
      Some blk
    with
    | Pli80.Lexer.Lex_error (pos, msg) ->
        Printf.printf "PARSE FAIL LEX line %d: %s\n" pos.Source.line msg; None
    | Pli80.Parser.Parse_error (pos, msg) ->
        Printf.printf "PARSE FAIL SYN line %d: %s\n" pos.Source.line msg; None
    | e ->
        Printf.printf "PARSE FAIL %s\n" (Printexc.to_string e); None
  in
  match blk_opt with
  | None -> ()
  | Some blk ->
      (* declaration KINDS come from the binder when it succeeds, because the
         AST alone cannot say whether a name is a FILE/POINTER/LABEL object *)
      (try
         let rows = Bind.bind_rows blk in
         Printf.printf "BIND ok (%d rows)\n" (List.length rows);
         List.iter
           (fun (nm, rt, _off, _auto) ->
             let line = 0 in
             (match rt with
             | Bind.RTfile { internal } ->
                  tag ~detail:("bound FILE object " ^ nm ^
                               (if internal then " (internal)" else ""))
                      "FILE_DECL" line
              | Bind.RTptr -> tag ~detail:("bound POINTER object " ^ nm) "POINTER_DECL" line
              | Bind.RTlabel ->
                  tag ~detail:("bound LABEL-as-data object " ^ nm) "LABEL_AS_DATA" line
              | Bind.RTbit n -> tag ~detail:("bound BIT(" ^ string_of_int n ^ ") " ^ nm)
                  "BIT_DECL" line
              | Bind.RTchar (_, true) ->
                  tag ~detail:("bound CHARACTER VARYING " ^ nm) "VARYING_DECL" line
              | Bind.RTfloat n ->
                  tag ~detail:("bound FLOAT BINARY(" ^ string_of_int n ^ ") " ^ nm)
                      "FLOAT_DECL" line
              | Bind.RTformat -> tag ~detail:("bound FORMAT " ^ nm) "FORMAT_DECL" line
              | Bind.RTbuiltin -> tag ~detail:("bound builtin ref " ^ nm) "BUILTIN_REF" line
              | Bind.RTstruct { level; members } ->
                  tag ~detail:("structure level " ^ string_of_int level ^ ", "
                               ^ string_of_int members ^ " members")
                      "STRUCTURE_LEVEL" line
              | Bind.RTentry { params; external_; _ } ->
                  tag ~detail:("ENTRY, " ^ string_of_int params ^ " params"
                               ^ (if external_ then ", external" else ""))
                      "ENTRY_DECL" line
             | _ -> ()))
           rows
       with
       | e -> Printf.printf "BIND FAIL %s\n" (Printexc.to_string e));
      (* top-level block itself *)
      let fake : Ast.block_stmt =
        { Ast.blk = blk; Ast.bpos = Source.zero } in
      walk_block fake;
      let keys =
        Hashtbl.fold (fun k _ acc -> k :: acc) tbl [] |> List.sort String.compare
      in
      List.iter
        (fun k ->
          let (n, first, d) = Hashtbl.find tbl k in
          Printf.printf "TAG %-28s count=%-3d first_line=%-4d %s\n" k n first d)
        keys

let () =
  Array.iter (fun a -> analyse a)
    (Array.sub Sys.argv 1 (Array.length Sys.argv - 1))
