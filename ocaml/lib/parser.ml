(* PL/I-80 recursive-descent parser — implements grammar/pli80.ebnf.
   Keywords are SOFT: the lexer emits Ident for every word; this parser
   decides keyword-ness by position (proven necessary by ENTER.PLI
   [default] group, DIOCOPY [space] field). *)

(* module open below *)

open Ast

exception Parse_error of Source.pos * string

type ps = { toks : (Token.tok * Source.pos) array; mutable i : int }

let make toks = { toks = Array.of_list toks; i = 0 }
let peek p = fst p.toks.(p.i)
let curpos p = snd p.toks.(p.i)
let next_tok p =
  if p.i + 1 < Array.length p.toks then Some (fst p.toks.(p.i + 1)) else None

let advance p = if p.i < Array.length p.toks - 1 then p.i <- p.i + 1
let at_eof p = match peek p with Token.EOF -> true | _ -> false

let at_punct p x = match peek p with Token.Punct y -> y = x | _ -> false
let at_key p k =
  match peek p with Token.Ident { key; _ } -> String.equal key k | _ -> false
let at_any_ident p = match peek p with Token.Ident _ -> true | _ -> false
let at_num p = match peek p with Token.Num _ -> true | _ -> false

let eat_punct p x = if at_punct p x then (advance p; true) else false
let eat_key p k = if at_key p k then (advance p; true) else false

let err_at p pos fmt =
  Format.kasprintf
    (fun s ->
      if Sys.getenv_opt "PLI80_BT" <> None then begin
        let toks =
          let rec go i acc =
            if i > p.i + 3 then List.rev acc
            else
              go (i + 1)
                 (Format.asprintf "%a" Token.pp_tok (fst p.toks.(i)) :: acc)
          in go (max 0 (p.i - 2)) []
        in
        Printf.eprintf "raise at line %d idx %d: %s | near: %s\n%!"
          (String.length (string_of_int pos.Source.line) + pos.Source.line - String.length (string_of_int pos.Source.line))
          p.i s (String.concat ", " toks)
      end;
      raise (Parse_error (pos, s)))
    fmt
let err p fmt = err_at p (curpos p) fmt

let expect_punct p x =
  if eat_punct p x then () else err p "expected %s" (Token.show_punct x)
let expect_key p k = if eat_key p k then () else err p "expected %s" k

let name_any p =
  match peek p with
  | Token.Ident { orig; key } ->
      let q = curpos p in advance p; { orig; key; pos = q }
  | _ -> err p "expected identifier"

let ident_str p =
  match peek p with
  | Token.Str { value; _ } -> advance p; value
  | _ -> err p "expected character constant"

let num_text p =
  match peek p with
  | Token.Num { text; _ } -> advance p; text
  | _ -> err p "expected number"

let number p = let t = num_text p in { e = Enumber t; epos = curpos p }
let mk_num t = { e = Enumber t; epos = Source.zero }

(* ---------- builtins [M §12] ---------- *)
let builtins =
  [ "ABS"; "ACOS"; "ADD"; "ADDR"; "ASIN"; "ATAN"; "ATAN2"; "BOOL"; "CEIL"
  ; "COPY"; "COS"; "DIVIDE"; "EXP"; "FIXED"; "FLOAT"; "HBOUND"; "INDEX"
  ; "LBOUND"; "LENGTH"; "LINENO"; "MAXIMUM"; "MINIMUM"; "MOD"; "NULL"
  ; "PAGENO"; "PRESENT"; "RANK"; "ASCII"; "RELATE"; "SIGN"; "SIN"; "SQRT"
  ; "SUMMARY"; "TRANSLATE"; "TRUNC"; "VSIZE"; "UNSUIT"; "LOG"; "LOG10"; "CHAR"
  ; "DEC"; "ROUND"; "DECIMAL" ]

let is_builtin k = List.mem k builtins

(* ---------- lexical key classes ---------- *)
let type_keys = [ "FIXED"; "FLOAT"; "CHARACTER"; "CHAR"; "BIT"; "POINTER"
                ; "PTR"; "ENTRY"; "FILE"; "DECIMAL"; "DEC"; "BINARY"; "BIN" ]

let attr_keys =
  [ "STATIC"; "AUTOMATIC"; "BASED"; "INIT"; "INITIALIZED"; "EXTERNAL"
  ; "INTERNAL"; "RETURNS"; "FILE"; "FORMAT"; "PICTURE"; "OPTIONS"
  ; "TITLE"; "ENVIRONMENT"; "REENTER"; "VARYING"; "INPUT"; "OUTPUT"
  ; "UPDATE"; "APPEND"; "KEYED"; "SEQUENTIAL"; "RANDOM"; "STREAM"
  ; "PRINT"; "SET"; "LABEL"; "INITIAL"; "RECURSIVE"; "VARIABLE"; "VAR" ]

let ioopt_keys =
  [ "FILE"; "STREAM"; "SOURCE"; "SINK"; "TITLE"; "ENVIRONMENT"; "RECORD"
  ; "PREAMBLE"; "KEYFROM"; "KEYINTO"; "KEY"; "SET"; "SETUPDATE"; "INPUT"
  ; "OUTPUT"; "UPDATE"; "APPEND"; "VARYING"; "ENV" ]

let ctl_keys = [ "SKIP"; "PAGE"; "LINE" ]

(* ---------- expressions ---------- *)

(* precedence ladder; ^= placement unprobed [PROBE 50]; relational vs
   additive order to be validated against $V traces [PROBE 51]. *)
let prec_of_punct = function
  | Token.Or -> Some 10
  | Token.AndThen | Token.OrElse -> Some 12
  | Token.Amp -> Some 20
  | Token.(Eq | Ne | Lt | Le | Gt | Ge | Xor) -> Some 30
  | Token.(CharCat | BitCat) -> Some 40
  | Token.(Plus | Minus) -> Some 50
  | Token.(Star | Slash) -> Some 60
  | Token.StarStar -> Some 70
  | _ -> None

let relop_of = function
  | Token.Eq -> Eq | Token.Ne -> Ne | Token.Lt -> Lt
  | Token.Le -> Le | Token.Gt -> Gt | Token.Ge -> Ge | _ -> assert false

let bin_of = function
  | Token.Plus -> Add | Token.Minus -> Sub | Token.Star -> Mul
  | Token.Slash -> Div | Token.StarStar -> Exp | Token.CharCat -> Cat
  | Token.BitCat -> BitCat | Token.Amp -> And | Token.Or -> Or
  | Token.Xor -> NotB
  | Token.AndThen -> AndThen | Token.OrElse -> OrElse
  | _ -> assert false

let rec opt_paren_exprs p = if at_punct p Token.LParen then arglist p else []

and arglist p =
  expect_punct p Token.LParen;
  if at_punct p Token.RParen then (advance p; [])
  else begin
    let rec go acc =
      let a = expr p 0 in
      if eat_punct p Token.Comma then go (a :: acc)
      else (expect_punct p Token.RParen; List.rev (a :: acc))
    in go []
  end

and expr p minp =
  let lhs = unary p in
  loop p lhs minp

and loop p lhs minp =
  match peek p with
  | Token.Punct op -> begin
      match prec_of_punct op with
      | Some prec when prec >= minp ->
          let q = curpos p in
          advance p;
          let rhs = if op = Token.StarStar then expr p prec else expr p (prec + 1) in
          let node =
            { e =
                (match op with
                 | Token.(Eq | Ne | Lt | Le | Gt | Ge | Xor) ->
                 (* ^= is the Subset-G ASCII spelling of NOT-EQUAL
                    [subsetg-cowan 1.1.2 table; confirmed semantically:
                    numeric P052B, bit(1)-padded P052E] *)
                     let op' = if op = Token.Xor then Token.Ne else op in
                     Ebinary (EqR (relop_of op'), lhs, rhs)
                 | _ -> Ebinary (bin_of op, lhs, rhs));
              epos = q }
          in
          loop p node minp
      | _ -> lhs
    end
  | _ -> lhs

and unary p =
  let q = curpos p in
  match peek p with
  | Token.Punct (Token.Minus as x) | Token.Punct (Token.Plus as x) ->
      advance p;
      let e = unary p in
      { e = Eprefix ((if x = Token.Minus then Minus else Plus), e); epos = q }
  | Token.Punct Token.Not ->
      advance p;
      let e = unary p in
      { e = Eprefix (NegL, e); epos = q }
  | _ -> primary p

and primary p =
  let q = curpos p in
  match peek p with
  | Token.Ident { orig; key } ->
      advance p;
      if is_builtin key && at_punct p Token.LParen then begin
        let args = arglist p in
        suffix_chain p { e = Ebuilt (key, args); epos = q }
      end
      else suffix_chain p { e = Eident { orig; key; pos = q }; epos = q }
  | Token.Num { text; _ } ->
      advance p; suffix_chain p { e = Enumber text; epos = q }
  | Token.Str { value; _ } ->
      advance p; suffix_chain p { e = Estring value; epos = q }
  | Token.Bit { value } ->
      advance p; suffix_chain p { e = Ebit value; epos = q }
  | Token.Punct Token.LParen ->
      advance p;
      let e = expr p 0 in
      expect_punct p Token.RParen;
      suffix_chain p { e = Econd e; epos = q }
  | _ -> err p "expected expression"

and suffix_chain p base =
  let cur = ref base in
  let stop = ref false in
  while not !stop do
    match peek p with
    | Token.Punct Token.LParen ->
        let q = curpos p in
        let args = arglist p in
        cur := { e = Esuffix (!cur, args); epos = q }
    | Token.Punct Token.Dot ->
        advance p;
        let q = curpos p in
        let n = name_any p in
        cur := { e = Eqstruct (!cur, n); epos = q }
    | Token.Punct Token.Arrow ->
        advance p;
        let q = curpos p in
        let n = name_any p in
        cur := { e = Eqptr (!cur, n); epos = q }
    | _ -> stop := true
  done;
  !cur

let expr0 p = expr p 0

(* END is a block terminator UNLESS followed by an operator-ish token,
   in which case it is an identifier used as a name [EX LOAN2:
   `end bit(1)`, `end = '1'b`] *)
let is_end_term p =
  at_key p "END"
  &&
  match next_tok p with
  | Some (Token.Punct Token.(Eq | LParen | Dot | Arrow)) -> false
  | _ -> true

(* wrap a stmt_kind into a bare stmt node at position q *)
let stq q k = { st = k; spos = q; slabels = [] }

(* ---------- types / attributes / declarations ---------- *)

let rec parse_type p =
  match peek p with
  | Token.Ident { key = "FIXED"; _ } ->
      advance p;
      let dec =
        if eat_key p "DECIMAL" || eat_key p "DEC" then Some true
        else if eat_key p "BINARY" || eat_key p "BIN" then Some false
        else None
      in
      let es = opt_paren_exprs p in
      let prec, scale =
        match es with [] -> (None, None) | [ a ] -> (Some a, None)
        | [ a; b ] -> (Some a, Some b) | _ -> err p "FIXED: too many arguments"
      in
      ignore dec;
      Tfixed { dec = dec = Some true; prec; scale }
  | Token.Ident { key = "FLOAT"; _ } ->
      advance p;
      let _dec =
        if eat_key p "DECIMAL" || eat_key p "DEC" then true
        else (ignore (eat_key p "BINARY" || eat_key p "BIN"); false)
      in
      let es = opt_paren_exprs p in
      Tfloat { prec = (match es with [ a ] -> Some a | _ -> None) }
  | Token.Ident { key = ("CHARACTER" | "CHAR"); _ } ->
      advance p;
      let len =
        match opt_paren_exprs p with
        | [] -> None | [ a ] -> Some a | _ -> err p "CHARACTER: args"
      in
      let varying = eat_key p "VARYING" in
      Tchar { varying; len }
  | Token.Ident { key = "BIT"; _ } ->
      advance p;
      Tbit { len = (match opt_paren_exprs p with
                    | [] -> None | [ a ] -> Some a | _ -> err p "BIT: args") }
  | Token.Ident { key = ("POINTER" | "PTR"); _ } -> advance p; Tptr
  | Token.Ident { key = "FILE"; _ } -> advance p; Tfile
  (* bare DECIMAL/BINARY without FIXED prefix [EX ACKTST `ncalls decimal(6)`] *)
  | Token.Ident { key = ("DECIMAL" | "DEC"); _ } ->
      advance p;
      let es = opt_paren_exprs p in
      let prec, scale = match es with
        | [] -> (None, None) | [ a ] -> (Some a, None)
        | [ a; b ] -> (Some a, Some b) | _ -> err p "DECIMAL: args"
      in
      Tfixed { dec = true; prec; scale }
  | Token.Ident { key = ("BINARY" | "BIN"); _ } ->
      advance p;
      let es = opt_paren_exprs p in
      let prec, scale = match es with
        | [] -> (None, None) | [ a ] -> (Some a, None)
        | [ a; b ] -> (Some a, Some b) | _ -> err p "BINARY: args"
      in
      Tfixed { dec = false; prec; scale }
  | Token.Ident { key = "ENTRY"; _ } ->
      advance p;
      let ptypes =
        if at_punct p Token.LParen then begin
          advance p;
          if at_punct p Token.RParen then (advance p; [])
          else begin
            let rec elem () =
              (* `(maxrow,maxcol) float(24)` shared-attr param group
                 [EX MAININVT] *)
              if looks_like_group p then begin
                advance p;
                while not (at_punct p Token.RParen) && not (at_eof p) do
                  advance p
                done;
                expect_punct p Token.RParen;
                parse_type p
              end else parse_type p
            in
            let rec go acc =
              let t = elem () in
              if eat_punct p Token.Comma then go (t :: acc)
              else (expect_punct p Token.RParen; t :: acc)
            in List.rev (go [])
          end
        end else []
      in
      Tentry { opts = ptypes }
  | _ -> err p "expected type"

and at_type_start p =
  match peek p with Token.Ident { key; _ } -> List.mem key type_keys | _ -> false

and parse_attrs p =
  let rec go acc =
    let q = curpos p in
    match peek p with
    | Token.Ident { key; _ } when List.mem key attr_keys ->
        advance p;
        let args, types =
          match key with
          | "RETURNS" ->
              if at_punct p Token.LParen then begin
                advance p;
                let rec g2 acc2 =
                  let t = parse_type p in
                  if eat_punct p Token.Comma then g2 (t :: acc2)
                  else (expect_punct p Token.RParen; t :: acc2)
                in ([], List.rev (g2 []))
              end else ([], [])
          | "PICTURE" ->
              let s =
                if at_punct p Token.LParen then begin
                  advance p; let v = ident_str p in expect_punct p Token.RParen; v
                end else ident_str p
              in
              ([ { e = Estring s; epos = q } ], [])
          | _ -> (opt_paren_exprs p, [])
        in
        go ({ akey = key; aargs = args; atypes = types; apos = q } :: acc)
    | _ -> List.rev acc
  in go []

and parse_dims p =
  expect_punct p Token.LParen;
  if at_punct p Token.RParen then (advance p; [])
  else begin
    let rec go acc =
      let lo = expr p 0 in
      let d = if eat_punct p Token.Colon then Dim_bound (lo, Some (expr p 0))
              else Dim_bound (lo, None) in
      if eat_punct p Token.Comma then go (d :: acc)
      else (expect_punct p Token.RParen; List.rev (d :: acc))
    in go []
  end

(* '(a, b)' / '(1, p)' before attrs = shared declaration group;
   'x(3)' after a name = dims. Decided by element shapes. *)
and looks_like_group p =
  (* true iff '(' opens a declaration group:
     ( name [dims] [type words...] )  , ...   with optional leading level.
     Backtracks; used only to disambiguate from array-dim '(' of a plain
     item that has already started with a name. *)
  let save = p.i in
  let res =
    try
      if not (at_punct p Token.LParen) then raise Exit;
      advance p;
      if at_num p then ignore (num_text p);
      let rec skip_balanced () =
        if at_punct p Token.LParen then begin
          advance p;
          let d = ref 1 in
          while !d > 0 do
            if at_eof p then raise Exit
            else begin
              if at_punct p Token.LParen then incr d
              else if at_punct p Token.RParen then decr d;
              advance p
            end
          done
        end
      in
      let rec member () =
        if not (at_any_ident p) then raise Exit;
        advance p;
        skip_balanced ();
        while (match peek p with
               | Token.Ident { key; _ } ->
                   List.mem key type_keys || String.equal key "VARYING"
               | _ -> false) do
          advance p; skip_balanced ()
        done
      in
      member ();
      while eat_punct p Token.Comma do member () done;
      at_punct p Token.RParen
    with Exit -> false
  in
  p.i <- save; res

and parse_dcl_item p =
  let level = if at_num p then Some (number p) else None in
  if at_punct p Token.LParen && looks_like_group p then begin
    expect_punct p Token.LParen;
    if at_num p then ignore (num_text p);
    let rec names acc =
      let n = name_any p in
      let dims = if at_punct p Token.LParen then parse_dims p else [] in
      (* per-member type: (line character(14), buff character(254)) varying
         [EX COPYLPT, EXPR2] *)
      let mt = if at_type_start p then Some (parse_type p) else None in
      let acc = (n, dims, mt) :: acc in
      if eat_punct p Token.Comma then names acc
      else (expect_punct p Token.RParen; List.rev acc)
    in
    let ns = names [] in
    let rec cont t attrs =
      if at_type_start p then cont (Some (parse_type p)) attrs
      else
        match parse_attrs p with
        | [] -> (t, attrs)
        | more -> cont t (attrs @ more)
    in
    let t, attrs = cont None [] in
    let initv = if eat_punct p Token.Eq then Some (Init_expr (expr0 p)) else None in
    List.map (fun (n, dims, mt) ->
      { dlevel = None; dname = n; ddims = dims; dtype = (match mt, t with
          | Some x, _ -> Some x | None, x -> x)
      ; dinit = initv; dattrs = attrs; dpre = None }) ns
  end
  else begin
    let n = name_any p in
    let dims = if at_punct p Token.LParen then parse_dims p else [] in
    (* type and attributes may interleave in ANY order:
       `q based(p) fixed` [EX P041], `x char(30) varying` etc. *)
    let rec cont t attrs =
      if at_type_start p then cont (Some (parse_type p)) attrs
      else
        match parse_attrs p with
        | [] -> (t, attrs)
        | more -> cont t (attrs @ more)
    in
    let t, attrs = cont None [] in
    let initv = if eat_punct p Token.Eq then Some (Init_expr (expr0 p)) else None in
    [ { dlevel = level; dname = n; ddims = dims; dtype = t; dinit = initv
      ; dattrs = attrs; dpre = None } ]
  end

and parse_directive p =
  (* '%' at point; directive word + raw tokens until ';' (not consumed) *)
  expect_punct p Token.Percent;
  let d = name_any p in
  let rec go acc =
    match peek p with
    | Token.EOF | Token.Punct Token.Semi -> List.rev acc
    | Token.Punct Token.Comma -> advance p; go (mk_comma :: acc)
    | Token.Ident { orig; key } ->
        let q = curpos p in advance p;
        go ({ e = Eident { orig; key; pos = q }; epos = q } :: acc)
    | Token.Num { text; _ } ->
        let q = curpos p in advance p; go ({ e = Enumber text; epos = q } :: acc)
    | Token.Str { value; _ } ->
        let q = curpos p in advance p; go ({ e = Estring value; epos = q } :: acc)
    | Token.Bit { value } ->
        let q = curpos p in advance p; go ({ e = Ebit value; epos = q } :: acc)
    | _ -> advance p; go acc
  in
  let args = go [] in
  (d.key, args)

and mk_comma =
  { e = Eident { orig = ","; key = ","; pos = Source.zero }; epos = Source.zero }

and parse_declare p =
  let rec items acc =
    let q = curpos p in
    if at_punct p Token.Percent then begin
      let d, args = parse_directive p in
      let hd = { dlevel = None; dname = { orig = "%"; key = d; pos = q }
               ; ddims = []; dtype = None; dinit = None; dattrs = []
               ; dpre = Some (d, args) } in
      let acc = hd :: acc in
      if eat_punct p Token.Comma then items acc else List.rev acc
    end
    else if at_eof p then List.rev acc
    else begin
      let ns = parse_dcl_item p in
      let acc = List.rev_append ns acc in
      if eat_punct p Token.Comma then items acc else List.rev acc
    end
  in
  items []

(* ---------- statements ---------- *)

and parse_stmt p =
  let q = curpos p in
  let labels = collect_labels p in
  if Sys.getenv_opt "PLI80_TR" <> None then
    Format.eprintf "parse_stmt q=%d labels=%d@." q.Source.line (List.length labels);
  let st = parse_stmt_body p q labels in
  { st; spos = q; slabels = labels }

and label_ahead p =
  (* pure scan: Ident ['(' balanced ')'] ':' ? (no side effects — must not
     consume the parens of `format(...)` when it is NOT a label [EX P020
     regression found by corpus sweep]) *)
  let n = Array.length p.toks in
  match peek p with
  | Token.Ident _ ->
      let j = ref (p.i + 1) in
      if !j < n && fst p.toks.(!j) = Token.Punct Token.LParen then begin
        incr j;
        let depth = ref 1 in
        while !depth > 0 && !j < n do
          (match fst p.toks.(!j) with
           | Token.Punct Token.LParen -> incr depth
           | Token.Punct Token.RParen -> decr depth
           | _ -> ());
          incr j
        done
      end;
      !j < n && fst p.toks.(!j) = Token.Punct Token.Colon
  | _ -> false

and collect_labels p =
  (* NAME:  or  NAME(args):  (subscripted label ref [EX LABELS `c(1):;`]) *)
  let rec go acc =
    if not (label_ahead p) then List.rev acc
    else begin
      let q = curpos p in
      let Token.Ident { orig; key } = peek p in
      advance p;
      let subscript = opt_paren_exprs p in
      expect_punct p Token.Colon;
      if subscript = [] then go ({ orig; key; pos = q } :: acc)
      else go ({ orig = orig ^ "("; key = key ^ "SUB"; pos = q } :: acc)
      (* subscripted label kept coarse; binding pass will refine *)
    end
  in go []

and parse_stmt_body p q labels =
  if labels <> [] && is_end_term p then
    (* LABEL: before END — label on the terminating point [EX REVERT
       `exit:` before `end;`] modeled as labeled null statement *)
    Snull q
  else if labels <> [] && at_key p "PROCEDURE" then
    Sproc { blk = parse_proc_block p labels; bpos = q }
  else if labels <> [] && at_key p "FORMAT" then begin
    if Sys.getenv_opt "PLI80_TR" <> None then Format.eprintf "labeled FORMAT hit@.";
    advance p;
    (* FORMAT (item-list): items are FORMAT items, not expressions —
       P'..' pictures allowed [EX P020 `format(p'$++,+++.++')`] *)
    if at_punct p Token.LParen then Sformat (parse_fmt_items p)
    else Sformat []
  end
  else match peek p with
  | Token.Punct Token.Semi -> advance p; Snull q
  | Token.Punct Token.Percent ->
      let d, args = parse_directive p in
      Sdcl [ { dlevel = None; dname = { orig = "%"; key = d; pos = q }
             ; ddims = []; dtype = None; dinit = None; dattrs = []
             ; dpre = Some (d, args) } ]
  | Token.Ident { key = ("DECLARE" | "DCL"); _ } ->
      advance p; Sdcl (parse_declare p)
  | Token.Ident { key = "IF"; _ } -> advance p; parse_if p
  | Token.Ident { key = "DO"; _ } -> advance p; parse_do p
  | Token.Ident { key = "BEGIN"; _ } -> parse_begin_block p q
  | Token.Ident { key = "PUT"; _ } -> advance p; parse_put p
  | Token.Ident { key = "GET"; _ } -> advance p; parse_get p
  | Token.Ident { key = "ON"; _ } ->
      advance p;
      let cond = if at_num p then num_text p else (name_any p).key in
      (* conditional-name arguments: ON ENDFILE(sysin) [EX EXPR1] *)
      let cargs = opt_paren_exprs p in
      Son { cond; cargs; handler = parse_stmt p }
  | Token.Ident { key = "SIGNAL"; _ } ->
      advance p;
      let cond = if at_num p then num_text p else (name_any p).key in
      (* SIGNAL cond(args) [EX EXPR1 `signal error(1)`, COPYLPT] *)
      let _sargs = opt_paren_exprs p in
      let target = if eat_key p "FROM" then Some (expr0 p) else None in
      Ssignal { cond; target }
  | Token.Ident { key = "RETURN"; _ } ->
      advance p;
      Sreturn (if at_punct p Token.Semi || is_end_term p then None else Some (expr0 p))
  | Token.Ident { key = "STOP"; _ } ->
      advance p;
      Sstop (if at_punct p Token.Semi || is_end_term p then None else Some (expr0 p))
  | Token.Ident { key = "EXIT"; _ } ->
      advance p;
      Sexit (if at_any_ident p && not (at_punct p Token.Semi) && not (is_end_term p)
             then Some (name_any p) else None)
  | Token.Ident { key = "GOTO"; _ } ->
      advance p;
      let n = name_any p in
      Sgoto { tgt = n; subscript = opt_paren_exprs p }
  | Token.Ident { key = "GO"; _ } ->
      advance p; expect_key p "TO";
      let n = name_any p in
      Sgoto { tgt = n; subscript = opt_paren_exprs p }
  | Token.Ident { key = "CALL"; _ } ->
      advance p;
      let e = expr0 p in
      Sprocedure_stmt { target = e; args = [] }
  | Token.Ident { key = "ALLOCATE"; _ } ->
      advance p;
      let e = expr0 p in
      let based = if eat_key p "SET" then Some (expr0 p) else None in
      Salloc { ptr = e; based }
  | Token.Ident { key = "FREE"; _ } ->
      advance p;
      let rec go acc =
        let e = expr0 p in
        if eat_punct p Token.Comma then go (e :: acc) else List.rev (e :: acc)
      in Sfree (go [])
  | Token.Ident { key = ("READ" | "WRITE" | "REWRITE" | "UPDATE" | "OPEN"
                       | "CLOSE" | "CREATE" | "REWIND" | "DELETE" as k); _ } ->
      advance p;
      let opts = parse_io_opts p in
      let file =
        match List.find_opt (fun o -> o.io_key = "FILE") opts with
        | Some o -> o.io_val | None -> None
      in
      Sfilestmt { key = k; file; opts }
  | Token.Ident { key = "EDIT"; _ } ->
      advance p;
      let opts = parse_io_opts p in
      let target = match eat_key p "FROM", (if at_punct p Token.LParen then Some (expr0 p) else None) with
        | true, Some e -> e | _, Some e -> e | _ -> mk_num "0"
      in
      Sedit { target; opts }
  | Token.Ident _ ->
      (* LHS is a REFERENCE chain only (primary + suffixes): '=' must not
         be eaten as the equality operator here (found via $V alignment on
         P068E5: `z = 2+3*4` was mis-parsed as a comparison) *)
      let e = expr p 100 in
      if eat_punct p Token.Eq then Sassign { lhs = e; rhs = expr0 p }
      else Sprocedure_stmt { target = e; args = [] }
  | _ -> err p "expected statement"

and opt_semi p = ignore (eat_punct p Token.Semi)

(* `END name ;` — consume the closing name ONLY if the token after it
   terminates the statement (a plain `END put edit(...)` must not eat
   the next statement's head [EX IFACT imbalance]. *)
and eat_end_name p =
  ignore
    (match peek p, next_tok p with
     | Token.Ident _, Some (Token.Punct Token.Semi) -> advance p; advance p; true
     | _ -> false)

and parse_if p =
  let cond = expr0 p in
  expect_key p "THEN";
  let then_ = parse_stmt p in
  let els =
    opt_semi p;
    if eat_key p "ELSE" then Some (parse_stmt p) else None
  in
  Sif { cond; then_; els }

and parse_do p =
  if eat_punct p Token.Semi then
    (* bare `DO;` = COMPOUND BLOCK (like BEGIN..END), NOT forever —
       proven by DR codegen [Z403: no back edge emitted]. Forever
       loops are written DO WHILE('1'b) [COPY] / DO WHILE(TRUE). *)
    Sdobegin (parse_group_until_end p)
  else if eat_key p "WHILE" then begin
    let cond = expr0 p in
    let body =
      if at_punct p Token.Semi then begin
        let q = curpos p in
        advance p; stq q (Sdobegin (parse_group_until_end p))
      end else begin
        let s = parse_stmt p in
        if is_end_term p then begin advance p; if at_any_ident p then ignore (name_any p); end;
        s
      end
    in
    Sdowhile { cond; body }
  end
  else begin
    let ind = name_any p in
    expect_punct p Token.Eq;
    let from_ = expr0 p in
    (* TO / BY / WHILE / REPEAT in any order [EX IFACT `to 1 by -1`,
       DIOCOPY `repeat(e) while(c)`] *)
    let rec tail by_ w t r =
      if eat_key p "TO" then tail by_ w (Some (expr0 p)) r
      else if eat_key p "BY" then tail (Some (expr0 p)) w t r
      else if eat_key p "WHILE" then tail by_ (Some (expr0 p)) t r
      else if eat_key p "REPEAT" then
        match opt_paren_exprs p with
        | [ e ] -> tail by_ w t (Some e)
        | _ -> err p "REPEAT: one argument expected"
      else if eat_key p "UNTIL" then err p "DO UNTIL [not in corpus]"
      else (by_, w, t, r)
    in
    let by_, while_, to_, rep = tail None None None None in
    let body =
      if at_punct p Token.Semi then begin
        let q = curpos p in
        advance p; stq q (Sdobegin (parse_group_until_end p))
      end else begin
        let s = parse_stmt p in
        if at_key p "END" then begin advance p; if at_any_ident p then ignore (name_any p); end;
        s
      end
    in
    match to_, rep with
    | Some bound, _ -> Sdoto { ind; from = from_; by = by_; while_
                             ; to_ = Some bound; rep = None; body }
    | None, Some r -> Sdoto { ind; from = from_; by = by_; while_
                              ; to_ = None; rep = Some r; body }
    | None, None ->
        (* indexed with no bound: `do i = 0 by 1;` forever [EX DTEST] *)
        Sdoto { ind; from = from_; by = by_; while_; to_ = None; rep = None; body }
  end

and parse_begin_block p q =
  expect_key p "BEGIN";
  let nm =
    if at_any_ident p && not (at_punct p Token.Semi) then Some (name_any p) else None
  in
  let _attrs = parse_attrs p in
  (* the `;` in `begin;` is the BEGIN's own terminator, not a null stmt
     [EX P078A: golden frames anchor at first INNER stmt, our phantom
     Snull was stealing the anchor] *)
  expect_punct p Token.Semi;
  let body = parse_body p in
  let qe = curpos p in
  expect_key p "END";
  eat_end_name p;
  Sproc { blk = { blabel = None; bname = nm; bparams = []; bopts = []
                ; bsuffix = []; bdecls = []; bstmts = body; bkind = Bbegin
                ; bendpos = Some qe }
        ; bpos = q }

and parse_io_opts p =
  let rec go acc =
    match peek p with
    | Token.Ident { key; _ } when List.mem key ioopt_keys ->
        advance p;
        let vals = opt_paren_exprs p in
        let v = match vals with
          | [] -> None | [ e ] -> Some e
          | es -> Some { e = Ebuilt ("COMMA", es); epos = curpos p }
        in
        go ({ io_key = key; io_val = v } :: acc)
    | _ -> List.rev acc
  in go []

and parse_ctl_items p =
  let rec go acc =
    match peek p with
    | Token.Ident { key; _ } when List.mem key ctl_keys ->
        advance p;
        let vals = opt_paren_exprs p in
        let n = match vals with [ e ] -> Some e | _ -> None in
        go ({ io_key = key; io_val = n } :: acc)
    | _ -> List.rev acc
  in go []

and parse_fmt_items p =
  expect_punct p Token.LParen;
  let r = fmt_seq p in
  expect_punct p Token.RParen;
  r

and fmt_seq p =
  let rec go acc =
    if at_punct p Token.RParen || at_eof p then List.rev acc
    else begin
      if Sys.getenv_opt "PLI80_TR" <> None then
        Format.eprintf "fmt_seq item, idx %d tok %a@." p.i Token.pp_tok (peek p);
      let item = fmt_item p in
      let acc = item :: acc in
      if eat_punct p Token.Comma then go acc else List.rev acc
    end
  in go []

and fmt_item p =
  let q = curpos p in
  let fmt_word_keys = [ "F"; "E"; "B"; "A"; "V"; "I"; "N"; "M"; "C"; "X" ] in
  (* leading repeat count: `4a` or `2(skip,column(i),a)`
     [EX DIOCALLS, DEPREC, LOAN2] *)
  let count =
    if at_num p &&
       (match next_tok p with
        | Some (Token.Ident { key; _ }) -> List.mem key fmt_word_keys
        | Some (Token.Punct Token.LParen) -> true
        | _ -> false)
    then Some (mk_num (num_text p)) else None
  in
  if count <> None && at_punct p Token.LParen then begin
    let c = Option.get count in
    advance p;
    let grp = fmt_seq p in
    expect_punct p Token.RParen;
    ignore q; Pi_repgrp (c, grp)
  end
  else
  match peek p with
  | Token.Ident { key = (("F" | "E" | "B" | "A" | "V" | "I" | "N" | "M" | "C" | "X"
                         | "COLUMN" | "COL" | "WIDTH") as k); _ }
      when next_fmt_word p ->
          advance p;
          Pi_fmt { fkey = k; fargs = opt_paren_exprs p; fcount = count }
  | Token.Ident { key = ("P" | "PICTURE"); _ } ->
      if Sys.getenv_opt "PLI80_TR" <> None then Printf.eprintf "fmt_item P-branch hit\n%!";
      advance p;
      let s =
        if at_punct p Token.LParen then begin
          advance p; let v = ident_str p in expect_punct p Token.RParen; v
        end else ident_str p
      in
      ignore q; ignore count; Pi_pic s
  | Token.Ident { key = "R"; _ } when next_tok p = Some (Token.Punct Token.LParen) ->
      advance p; advance p;
      let n = name_any p in
      expect_punct p Token.RParen;
      ignore q; ignore count; Pi_remote n
  | Token.Ident { key; _ } when List.mem key ctl_keys ->
      advance p;
      let vals = opt_paren_exprs p in
      let n = match vals with [ e ] -> Some e | _ -> None in
      ignore q; ignore count; Pi_ctl (key, n)
  | Token.Punct Token.LParen ->
      advance p;
      let grp = fmt_seq p in
      expect_punct p Token.RParen;
      ignore q; ignore count; Pi_group grp
  | _ -> ignore q; ignore count; Pi_data (expr0 p)

and next_fmt_word p =
  (* single-letter format keys are words when followed by '(' , ',' , ')'
     or another format word; never when they are ordinary names in parens.
     Conservative: treat as format key only if next token is LParen/Comma/
     RParen/Ident — refined by corpus iteration. *)
  match next_tok p with
  | Some (Token.Punct (Token.LParen | Token.Comma | Token.RParen)) -> true
  | Some (Token.Ident _) -> true
  | _ -> false

and parse_rep_spec p =
  (* DO <ind> = <from> [TO <b>] [BY <s>] -> REPSPEC expr [PROBE: order] *)
  if Sys.getenv_opt "PLI80_TR" <> None then
    Format.eprintf "rep_spec at idx %d tok %a@." p.i Token.pp_tok (peek p);
  let ind = name_any p in
  if Sys.getenv_opt "PLI80_TR" <> None then
    Format.eprintf "rep_spec after ind: idx %d tok %a@." p.i Token.pp_tok (peek p);
  expect_punct p Token.Eq;
  let from_ = expr0 p in
  let to_ = if eat_key p "TO" then Some (expr0 p) else None in
  let by_ = if eat_key p "BY" then Some (expr0 p) else None in
  ignore ind; ignore by_;
  { e = Ebuilt ("REPSPEC",
                [ from_ ] @ (match to_ with Some x -> [ x ] | None -> []))
  ; epos = curpos p }

and data_items p =
  expect_punct p Token.LParen;
  (* leading-paren rep item: (expr do n=...) [EX ACK] vs nested parens *)
  let item0 p =
    if at_punct p Token.LParen then begin
      let save = p.i in
      try
        advance p;
        let e = expr0 p in
        if eat_key p "DO" then begin
          let spec = parse_rep_spec p in
          expect_punct p Token.RParen;
          Pi_rep (e, spec)
        end else raise Exit
      with Exit -> p.i <- save; Pi_data (expr0 p)
    end
    else begin
      let e = expr0 p in
      if eat_key p "DO" then Pi_rep (e, parse_rep_spec p) else Pi_data e
    end
  in
  let rec go acc =
    if at_punct p Token.RParen then (advance p; List.rev acc)
    else begin
      let item = item0 p in
      let acc = item :: acc in
      if eat_punct p Token.Comma then go acc
      else (expect_punct p Token.RParen; List.rev acc)
    end
  in go []

and parse_put p =
  (* FILE/SOURCE options and SKIP/PAGE controls may interleave
     [EX LOAN2 `put skip file(output) edit`] *)
  let opts = ref [] and ctl = ref [] in
  let rec consume () =
    let o = parse_io_opts p and c = parse_ctl_items p in
    if o = [] && c = [] then begin
      (* bare file reference: `get f list(x)` / `put f edit(...) ...`
         — DR accepts the name directly, not only FILE(f) [EX P080Q] *)
      match peek p with
      | Token.Ident { key; _ }
        when not
               (List.mem key
                  (ioopt_keys @ ctl_keys
                  @ [ "LIST"; "EDIT"; "CONST"; "ITEM"; "FROM"; "USING" ])) ->
          let nm = name_any p in
          opts := !opts
                  @ [ { io_key = "FILE"
                      ; io_val = Some { e = Eident nm; epos = nm.pos } } ];
          consume ()
      | _ -> ()
    end
    else begin
      opts := !opts @ o; ctl := !ctl @ c; consume ()
    end
  in consume ();
  let opts = !opts and ctl = !ctl in
  let ctl_items = List.map (fun o -> Pi_ctl (o.io_key, o.io_val)) ctl in
  let trail lead it =
    (* PL/I allows a trailing control item (`put list(x) skip;`).  Our
       parser would leave SKIP/PAGE/LINE to be read as a SEPARATE
       statement, which reaches codegen as a phantom CALL (corpus audit
       REV 2, defect D5) - a wrong AST that would become silently wrong
       the day CALL is implemented.  Refuse it loudly here instead; the
       leading form `put skip list(...)` [N301-N306, G107/G108] is the
       shape this compiler is byte-exact on. *)
    (match peek p with
     | Token.Ident { key; _ } when List.mem key ctl_keys ->
         err p "%s"
           (Printf.sprintf
              "trailing %s control item before ';' is not supported [TBD] \
               (write it first: %s)" key lead);
     | _ -> ());
    it
  in
  if eat_key p "LIST" then
    Sput { stream = None; on_opts = opts; kind = List_;
           items = ctl_items @ trail "put skip list(...)" (data_items p) }
  else if eat_key p "EDIT" then begin
    let d = data_items p in
    let f = parse_fmt_items p in
    Sput { stream = None; on_opts = opts; kind = Edit;
           items = ctl_items @ d @ [Pi_fmtlist f] }
  end
  else if eat_key p "ITEM" then
    Sput { stream = None; on_opts = opts; kind = Item;
           items = ctl_items @ trail "put skip item(...)" (data_items p) }
  else if eat_key p "FROM" then
    Sput { stream = None; on_opts = opts; kind = List_;
           items = ctl_items @ trail "put skip from(...)" (data_items p) }
  else if ctl_items <> [] && at_punct p Token.Semi then
    (* PUT SKIP; / PUT PAGE; newline-only controls [EX CREATE] *)
    Sput { stream = None; on_opts = opts; kind = Item; items = ctl_items }
  else err p "PUT: expected LIST/EDIT/ITEM/FROM"

and parse_get p =
  (* FILE/SOURCE options and SKIP/PAGE controls may interleave
     [EX LOAN2 `put skip file(output) edit`] *)
  let opts = ref [] and ctl = ref [] in
  let rec consume () =
    let o = parse_io_opts p and c = parse_ctl_items p in
    if o = [] && c = [] then begin
      (* bare file reference: `get f list(x)` / `put f edit(...) ...`
         — DR accepts the name directly, not only FILE(f) [EX P080Q] *)
      match peek p with
      | Token.Ident { key; _ }
        when not
               (List.mem key
                  (ioopt_keys @ ctl_keys
                  @ [ "LIST"; "EDIT"; "CONST"; "ITEM"; "FROM"; "USING" ])) ->
          let nm = name_any p in
          opts := !opts
                  @ [ { io_key = "FILE"
                      ; io_val = Some { e = Eident nm; epos = nm.pos } } ];
          consume ()
      | _ -> ()
    end
    else begin
      opts := !opts @ o; ctl := !ctl @ c; consume ()
    end
  in consume ();
  let opts = !opts and ctl = !ctl in
  let ctl_items = List.map (fun o -> Pi_ctl (o.io_key, o.io_val)) ctl in
  let trail lead it =
    (* same D5 guard as PUT: a trailing control item would otherwise be
       read as a separate statement (phantom CALL) instead of a refusal *)
    (match peek p with
     | Token.Ident { key; _ } when List.mem key ctl_keys ->
         err p "%s"
           (Printf.sprintf
              "trailing %s control item before ';' is not supported [TBD] \
               (write it first: %s)" key lead);
     | _ -> ());
    it
  in
  if eat_key p "LIST" then
    Sget { stream = None; on_opts = opts; kind = List_;
           items = ctl_items @ trail "get skip list(...)" (data_items p) }
  else if eat_key p "EDIT" then begin
    let d = data_items p in
    let f = parse_fmt_items p in
    Sget { stream = None; on_opts = opts; kind = Edit;
           items = ctl_items @ d @ f }
  end
  else if eat_key p "CONST" then
    Sget { stream = None; on_opts = opts; kind = Const_;
           items = ctl_items @ parse_fmt_items p }
  else if ctl_items <> [] && at_punct p Token.Semi then
    (* GET SKIP; newline sync [EX EXPR1, REPORT] *)
    Sget { stream = None; on_opts = opts; kind = List_; items = ctl_items }
  else err p "GET: expected LIST/EDIT/CONST"

and parse_body p =
  let rec go acc =
    if is_end_term p || at_eof p then List.rev acc
    else begin
      let s = parse_stmt p in
      opt_semi p;
      go (s :: acc)
    end
  in go []

and parse_group_until_end p =
  let body = parse_body p in
  expect_key p "END";
  eat_end_name p;
  body

and parse_proc_block p labels =
  let nm = List.hd labels in
  expect_key p "PROCEDURE";
  let params =
    if at_punct p Token.LParen then begin
      advance p;
      if at_punct p Token.RParen then (advance p; [])
      else begin
        let rec go acc =
          let n = name_any p in
          if eat_punct p Token.Comma then go (n :: acc)
          else (expect_punct p Token.RParen; n :: acc)
        in List.rev (go [])
      end
    end else []
  in
  let opts =
    if eat_key p "OPTIONS" then begin
      expect_punct p Token.LParen;
      let rec go acc =
        let k = name_any p in
        let args = opt_paren_exprs p in
        if eat_punct p Token.Comma then go ((k.key, args) :: acc)
        else (expect_punct p Token.RParen; (k.key, args) :: acc)
      in List.rev (go [])
    end else []
  in
  let suffix = parse_attrs p in
  expect_punct p Token.Semi;
  let body = parse_body p in
  let qe = curpos p in
  expect_key p "END";
  eat_end_name p;
  { blabel = None; bname = Some nm; bparams = params; bopts = opts
  ; bsuffix = suffix; bdecls = []; bstmts = body; bkind = Bproc
  ; bendpos = Some qe }

(* ---------- program ---------- *)

let rec preproc_stmt p q =
  let d, args = parse_directive p in
  Sdcl [ { dlevel = None; dname = { orig = "%"; key = d; pos = q }
         ; ddims = []; dtype = None; dinit = None; dattrs = []
         ; dpre = Some (d, args) } ]

and parse_program p =
  let labels = collect_labels p in
  if labels = [] then err p "expected outer procedure label:"
  else begin
    let blk =
      if at_key p "PROCEDURE" then parse_proc_block p labels
      else if at_key p "BEGIN" then begin
        let Sproc b = parse_begin_block p (curpos p) in b.blk
      end
      else err p "expected PROCEDURE after label"
    in
    let rec trail () =
      if at_eof p then ()
      else if at_punct p Token.Dollar then (advance p; trail ())
      else if at_punct p Token.Semi then (advance p; trail ())
      else if at_punct p Token.Percent then begin
        ignore (parse_directive p); opt_semi p; trail ()
      end
      else err p "trailing garbage after final END"
    in
    trail ();
    blk
  end

let parse_source src =
  let toks = Lexer.tokenize src in
  let p = make toks in
  parse_program p

(* ---------- debug: parenthesized expression trees ---------- *)

let rec pp_e fmt = function
  | { e = Eident n; _ } -> Format.fprintf fmt "%s" n.orig
  | { e = Enumber t; _ } -> Format.fprintf fmt "%s" t
  | { e = Estring s; _ } -> Format.fprintf fmt "'%s'" s
  | { e = Ebit b; _ } -> Format.fprintf fmt "%sb" b
  | { e = Eprefix (op, x); _ } ->
      let s = match op with Plus -> "+" | Minus -> "-" | NegL -> "^" in
      Format.fprintf fmt "(%s %a)" s pp_e x
  | { e = Ebinary (op, a, b); _ } ->
      let s = match op with
        | Add -> "+" | Sub -> "-" | Mul -> "*" | Div -> "/" | Exp -> "**"
        | Cat -> "||" | BitCat -> "!!" | And -> "&" | Or -> "|" | NotB -> "^"
        | AndThen -> "&:" | OrElse -> "|:" | XorNe -> "^=" | EqR r ->
            (match r with Eq -> "=" | Ne -> "<>" | Lt -> "<" | Le -> "<="
                        | Gt -> ">" | Ge -> ">=")
      in
      Format.fprintf fmt "(%s %a %a)" s pp_e a pp_e b
  | { e = Econd x; _ } -> Format.fprintf fmt "(cond %a)" pp_e x
  | { e = Esuffix (f, args); _ } ->
      Format.fprintf fmt "(call %a[%a])" pp_e f
        (Format.pp_print_list ~pp_sep:(fun f () -> Format.fprintf f ", ") pp_e) args
  | { e = Ebuilt (k, args); _ } ->
      Format.fprintf fmt "(%s[%a])" (String.lowercase_ascii k)
        (Format.pp_print_list ~pp_sep:(fun f () -> Format.fprintf f ", ") pp_e) args
  | { e = Eqstruct (a, n); _ } -> Format.fprintf fmt "(qual %a .%s)" pp_e a n.orig
  | { e = Eqptr (a, n); _ } -> Format.fprintf fmt "(ptr %a ->%s)" pp_e a n.orig
  | { e = Eformat_ref n; _ } -> Format.fprintf fmt "(r %s)" n.orig
  | { e = Epicture s; _ } -> Format.fprintf fmt "(p '%s')" s

let dump_trees src =
  let toks = Lexer.tokenize src in
  let p = make toks in
  let blk = parse_program p in
  let rec pp_st s =
    match s.st with
    | Sdcl items ->
        List.iter (fun (d : dcl) ->
            Format.printf "DCL line %d: %s\n" d.dname.pos.Source.line d.dname.orig)
          items
    | Sassign { lhs; rhs } ->
        Format.printf "L%d: ASSIGN %a <- %a\n"
          s.spos.Source.line pp_e lhs pp_e rhs
    | Sif { cond; then_; els } ->
        Format.printf "L%d: IF %a\n" s.spos.Source.line pp_e cond;
        pp_st then_; Option.iter pp_st els
    | Sdowhile { cond; body } ->
        Format.printf "L%d: DO-WHILE %a\n" s.spos.Source.line pp_e cond;
        pp_st body
    | Sdoto { from; by; while_; to_; rep; body; _ } ->
        Format.printf "L%d: DO %a%a%a%a\n" s.spos.Source.line
          pp_e from
          (fun f o -> match o with Some x -> Format.fprintf f " BY %a" pp_e x | None -> ()) by
          (fun f o -> match o with Some x -> Format.fprintf f " WHILE %a" pp_e x | None -> ()) while_
          (fun f o -> match o with Some x -> Format.fprintf f " TO %a" pp_e x | None -> ()) to_;
        (match rep with Some r -> Format.printf " REPEAT %a" pp_e r | None -> ());
        Format.printf "\n%!";
        pp_st body
    | Sdobegin ss -> List.iter pp_st ss
    | Sproc { blk; _ } -> List.iter pp_st blk.bstmts
    | Sput { kind = k; items; on_opts; stream; _ } ->
        Format.printf "L%d: PUT kind=%s items=%d opts=%d%s\n%!"
          s.spos.Source.line
          (match k with
           | List_ -> "LIST" | Edit -> "EDIT" | Item -> "ITEM"
           | Editsk n -> "EDITSK(" ^
               (match n with Some x -> string_of_int x | None -> "-") ^ ")")
          (List.length items) (List.length on_opts)
          (if stream = None then "" else " FILEREF")
    | Sget { kind = k; items; on_opts; stream; _ } ->
        Format.printf "L%d: GET kind=%s items=%d opts=%d%s\n%!"
          s.spos.Source.line
          (match k with List_ -> "LIST" | Edit -> "EDIT" | Const_ -> "CONST")
          (List.length items) (List.length on_opts)
          (if stream = None then "" else " FILEREF")
    | _ ->
        (* fail-loud observability: never silently elide a statement kind *)
        Format.printf "L%d: [STMT-KIND-NOT-PRINTED]\n%!" s.spos.Source.line
  in
  List.iter pp_st blk.bstmts
