exception Lex_error of Source.pos * string

let is_letter c = (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z')
let is_digit c = c >= '0' && c <= '9'
let is_ident_char c = is_letter c || is_digit c || c = '_' (* underscore [EX input_file] *)

type t = { src : string; mutable i : int; mutable line : int; mutable col : int }

let create src = { src; i = 0; line = 1; col = 1 }
let pos t = Source.pos t.line t.col
let eof t = t.i >= String.length t.src

let advance t =
  let c = Char.code t.src.[t.i] in
  t.i <- t.i + 1;
  if c = 13 then (t.line <- t.line + 1; t.col <- 1)
  else if c = 10 then
    (* treat bare LF as newline unless it just followed a CR (col=1 already) *)
    if t.col > 1 then (t.line <- t.line + 1; t.col <- 1)
  else t.col <- t.col + 1

let peek ?(k = 0) t = if t.i + k < String.length t.src then t.src.[t.i + k] else '\000'
let up = String.uppercase_ascii

(* skip whitespace and non-nesting /* */ comments *)
let skip t =
  let stop = ref false in
  while not !stop do
    let c = peek t in
    if c = ' ' || c = '\t' || c = '\r' || c = '\n' then advance t
    else if c = '/' && peek ~k:1 t = '*' then begin
      advance t; advance t;
      let closed = ref false in
      while not !closed do
        if eof t then raise (Lex_error (pos t, "unterminated comment"));
        if peek t = '*' && peek ~k:1 t = '/' then begin advance t; advance t; closed := true end
        else advance t
      done
    end
    else stop := true
  done

let scan_ident t =
  let b = Buffer.create 16 in
  while is_ident_char (peek t) do Buffer.add_char b (peek t); advance t done;
  let orig = Buffer.contents b in
  Token.Ident { orig; key = up orig }

(* quoted literal; '' escapes a quote; optional b/x suffix.
   NOTE [PROBE 3]: caret ^x sequences inside strings are runtime
   conventions — preserved verbatim here. *)
let scan_string t start =
  let buf = Buffer.create 16 in
  advance t (* opening quote *);
  let closed = ref false in
  while not !closed do
    if eof t then
      raise (Lex_error (start, "unterminated string (compiler halts: MISSING QUOTE)"));
    let c = peek t in
    if c = '\'' then begin
      advance t;
      if peek t = '\'' then begin Buffer.add_char buf '\''; advance t end
      else closed := true
    end else begin Buffer.add_char buf c; advance t end
  done;
  let value = Buffer.contents buf in
  if peek t = 'b' || peek t = 'B' then begin
    advance t;
    (* optional repeat count: '20'b4 = (20)x4 [EX DIORAND] *)
    let rep = ref 1 in
    while is_digit (peek t) do
      rep := !rep * 10 + (Char.code (peek t) - 48); advance t
    done;
    let v =
      if !rep <= 1 then value
      else
        let b2 = Buffer.create (String.length value * !rep) in
        for _ = 1 to !rep do Buffer.add_string b2 value done;
        Buffer.contents b2
    in
    Token.Bit { value = v }
  end
  else if peek t = 'x' || peek t = 'X' then begin advance t; Token.Str { orig = value; value } end
  else Token.Str { orig = value; value }

let scan_number t =
  let b = Buffer.create 16 in
  while is_digit (peek t) do Buffer.add_char b (peek t); advance t done;
  if peek t = '.' && is_digit (peek ~k:1 t) then begin
    Buffer.add_char b '.'; advance t;
    while is_digit (peek t) do Buffer.add_char b (peek t); advance t done
  end;
  (* optional exponent E/D [sign] digits; roll back if no digits follow *)
  let c = peek t in
  if c = 'E' || c = 'e' || c = 'D' || c = 'd' then begin
    let save_i, save_l, save_c = t.i, t.line, t.col in
    Buffer.add_char b c; advance t;
    let s = peek t in
    if s = '+' || s = '-' then begin Buffer.add_char b s; advance t end;
    if is_digit (peek t) then begin
      while is_digit (peek t) do Buffer.add_char b (peek t); advance t done
    end else begin t.i <- save_i; t.line <- save_l; t.col <- save_c end
  end;
  Token.Num { text = Buffer.contents b; exp_sign = `None }

let scan_punct t start =
  let rec go = function
    | [] -> raise (Lex_error (start, "unexpected character"))
    | (p, s) :: rest ->
      let n = String.length s in
      let avail = String.length t.src - t.i in
      if n <= avail && String.sub t.src t.i n = s then begin
        for _ = 1 to n do advance t done;
        Token.Punct p
      end else go rest
  in
  go Token.punct_list

(* one token *)
let scan t =
  skip t;
  let start = pos t in
  if eof t then Token.EOF, start
  else begin
    let c = peek t in
    if is_letter c then scan_ident t, start
    else if is_digit c || (c = '.' && is_digit (peek ~k:1 t)) then scan_number t, start
    else if c = '\'' then scan_string t start, start
    else scan_punct t start, start
  end

(* whole file -> list of (tok, pos); caller prepends nothing *)
let tokenize src =
  let t = create src in
  let out = ref [] in
  let rec loop () =
    let tok, p = scan t in
    out := (tok, p) :: !out;
    if tok <> Token.EOF then loop ()
  in
  loop ();
  List.rev !out
