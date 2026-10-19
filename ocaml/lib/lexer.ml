exception Lex_error of Source.pos * string

let is_letter c = (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z')
(* standard identifier chars: '$','_' interior + '$'/'_' start allowed
   [Subset G 1.1.3]; DR rejects them ([M] gap) — we parse anyway *)
let is_ident_char c = is_letter c || (c >= '0' && c <= '9') || c = '_' || c = '$'
let is_ident_start c = is_letter c || c = '_' || c = '$'
let is_digit c = c >= '0' && c <= '9'

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
    (* Subset-G 'character-string'Bn [subsetg-cowan 3.4.1.1]: n = BITS
       PER DIGIT (base 4/8/16 for n=2/3/4; default 1; n>4 rejected by
       the compiler in pass 2). Each digit becomes its n-bit binary. *)
    let rep = ref 1 in
    while is_digit (peek t) do
      rep := !rep * 10 + (Char.code (peek t) - 48); advance t
    done;
    let digit_val c =
      match c with
      | '0' .. '9' -> Some (Char.code c - 48)
      | 'a' .. 'f' -> Some (Char.code c - 87)
      | 'A' .. 'F' -> Some (Char.code c - 55)
      | _ -> None
    in
    let v =
      if !rep <= 1 then value
      else if !rep > 4 then value       (* keep raw; binding flags it *)
      else begin
        let b2 = Buffer.create (String.length value * !rep) in
        String.iter
          (fun c ->
            match digit_val c with
            | Some d ->
                for k = !rep - 1 downto 0 do
                  Buffer.add_char b2 (if (d lsr k) land 1 = 1 then '1' else '0')
                done
            | None -> Buffer.add_char b2 c)
          value;
        Buffer.contents b2
      end
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
    if is_ident_start c then scan_ident t, start
    else if is_digit c || (c = '.' && is_digit (peek ~k:1 t)) then scan_number t, start
    else if c = '\'' then scan_string t start, start
    else scan_punct t start, start
  end

(* ---------- [%REPLACE] preprocessor ----------
   [DECPOLY: %replace true by '1'b;]  DR PL/I-80 1.4 treats %replace as a
   pass-1 textual macro: the directive itself vanishes from the listing's
   CODE stream (it prints, but generates nothing) and every later use of the
   macro name expands to the replacement text.

   Scope pinned by the golden: whole-identifier replacement in CODE context.
   An occurrence inside a character literal or a comment is refused [TBD] --
   no golden pins DR's behaviour there, and silently guessing would risk a
   wrong byte stream. *)

let quote = '\''
let is_ws c = c = ' ' || c = '\r' || c = '\n' || c = '\t' || c = '\014'

(* (lowercase name, replacement text, byte offset just past the directive) *)
type macro = { mname : string; mtext : string; mfrom : int }

let collect_macros (src : string) (out : Bytes.t) =
  let n = String.length src in
  let reps = ref [] in
  let blank a b =
    for k = a to b - 1 do
      let c = Bytes.get out k in
      if c <> '\r' && c <> '\n' then Bytes.set out k ' '
    done
  in
  (* true if src.[i] starts a /* */ comment *)
  let is_cmt i = i + 1 < n && src.[i] = '/' && src.[i + 1] = '*' in
  let i = ref 0 in
  while !i < n do
    let c = src.[!i] in
    if is_cmt !i then begin
      let j = ref (!i + 2) in
      while !j + 1 < n && not (src.[!j] = '*' && src.[!j + 1] = '/') do
        incr j
      done;
      i := (!j + 2) (* unterminated -> n+1 -> loop ends *)
    end
    else if c = '\'' then begin
      (* character literal: run to the closing quote (doubled '' folds) *)
      let j = ref (!i + 1) in
      let stop = ref false in
      while !j < n && not !stop do
        if src.[!j] = '\'' then begin
          if !j + 1 < n && src.[!j + 1] = '\'' then (j := !j + 2)
          else (stop := true; incr j)
        end
        else incr j
      done;
      i := !j
    end
    else if c = '%' then begin
      let j = ref (!i + 1) in
      while !j < n && is_letter src.[!j] do incr j done;
      let word =
        String.lowercase_ascii (String.sub src (!i + 1) (!j - !i - 1))
      in
      if word = "replace" then begin
        let k = ref !j in
        (* Whitespace AND comments between clauses: DIOCOPY writes
             %replace
                bufwds by 64,   /* words per buffer */
                quest  by 63,
                true   by '1'b,
                false  by '0'b;
           so a clause separator may be followed by a block comment before the
           next NAME BY VALUE [E2E-9 slice 6, R2043]. *)
        let rec sp () =
          while !k < n && is_ws src.[!k] do incr k done;
          if is_cmt !k then begin
            let j2 = ref (!k + 2) in
            while !j2 + 1 < n && not (src.[!j2] = '*' && src.[!j2 + 1] = '/') do
              incr j2
            done;
            k := (if !j2 + 1 < n then !j2 + 2 else n);
            sp ()
          end
        in
        let word_at () =
          let a = !k in
          while !k < n && is_ident_char src.[!k] do incr k done;
          String.sub src a (!k - a)
        in
        let stop = ref false in
        while not !stop do
          sp ();
          if !k >= n then stop := true
          else if src.[!k] = ';' then (stop := true; incr k)
          else if src.[!k] = ',' then incr k
          else if is_ident_start src.[!k] then begin
            let name = String.lowercase_ascii (word_at ()) in
            sp ();
            let kw = word_at () in
            if String.lowercase_ascii kw <> "by" then
              failwith
                (Printf.sprintf
                   "lexer: %%replace operand %s is not BY [TBD]" kw);
            sp ();
            let rs = !k in
            let lvl = ref 0 in
            let done' = ref false in
            while !k < n && not !done' do
              let d = src.[!k] in
              if d = ';' && !lvl = 0 then done' := true
              else if d = ',' && !lvl = 0 then done' := true
              else if d = '(' then (incr lvl; incr k)
              else if d = ')' then (decr lvl; incr k)
              else if d = '\'' || is_cmt !k then begin
                (* quoted / comment run inside the replacement text *)
                let close = if d = quote then quote else '*' in
                let q = ref (!k + 1) in
                if d <> '\'' then q := !k + 2;
                while !q < n && src.[!q] <> close do incr q done;
                q := !q + 1;
                if d = '*' && !q < n && src.[!q] = '/' then incr q;
                k := (if !q < n then !q else n)
              end
              else incr k
            done;
            let rtext = String.trim (String.sub src rs (!k - rs)) in
            if rtext = "" then
              failwith "lexer: empty %replace body [TBD]";
            reps := { mname = name; mtext = rtext; mfrom = !k } :: !reps
          end
          else
            failwith
              (Printf.sprintf "lexer: %%replace clause at offset %d [TBD]"
                 !k)
        done;
        blank !i !k;
        i := !k
      end else
        i := !j (* other directive (%eof/%echo/...): parser's business *)
    end
    else incr i
  done;
  List.rev !reps

let rec macro_for ms name =
  match ms with
  | [] -> None
  | m :: rest -> if m.mname = name then Some m else macro_for rest name

(* refuse a macro name used as a whole word inside literal/comment text *)
let check_scope ms txt =
  let ln = String.length txt in
  let p = ref 0 in
  while !p < ln do
    if is_ident_start txt.[!p] then begin
      let a = !p in
      while !p < ln && is_ident_char txt.[!p] do incr p done;
      let w = String.lowercase_ascii (String.sub txt a (!p - a)) in
      match macro_for ms w with
      | Some m ->
          failwith
            ("lexer: %replace macro " ^ m.mname
             ^ " used inside a literal or comment [TBD]"
             ^ " (DR substitution scope there is unpinned)")
      | None -> ()
    end
    else incr p
  done

let apply_macros (src : string) (ms : macro list) =
  if ms = [] then src
  else begin
    let n = String.length src in
    let buf = Buffer.create n in
    let i = ref 0 in
    while !i < n do
      let c = src.[!i] in
      let is_cmt () =
        !i + 1 < n && c = '/' && src.[!i + 1] = '*'
      in
      if is_cmt () then begin
        let j = ref (!i + 2) in
        while !j + 1 < n && not (src.[!j] = '*' && src.[!j + 1] = '/') do
          incr j
        done;
        j := !j + 2;
        let txt = String.sub src !i (min n !j - !i) in
        check_scope ms txt; Buffer.add_string buf txt; i := !j
      end
      else if c = '\'' then begin
        let j = ref (!i + 1) in
        let stop = ref false in
        while !j < n && not !stop do
          if src.[!j] = '\'' then begin
            if !j + 1 < n && src.[!j + 1] = '\'' then (j := !j + 2)
            else (stop := true; incr j)
          end
          else incr j
        done;
        let txt = String.sub src !i (!j - !i) in
        check_scope ms txt; Buffer.add_string buf txt; i := !j
      end
      else if is_ident_start c then begin
        let a = !i in
        while !i < n && is_ident_char src.[!i] do incr i done;
        let w = String.sub src a (!i - a) in
        (match macro_for (List.filter (fun m -> m.mfrom <= a) ms)
                 (String.lowercase_ascii w) with
         | Some m -> Buffer.add_string buf m.mtext
         | None -> Buffer.add_string buf w)
      end
      else begin Buffer.add_char buf c; incr i end
    done;
    Buffer.contents buf
  end

let preprocess src =
  let out = Bytes.of_string src in
  let ms = collect_macros src out in
  apply_macros (Bytes.to_string out) ms

(* whole file -> list of (tok, pos); caller prepends nothing *)
let tokenize src =
  let src = preprocess src in
  let t = create src in
  let out = ref [] in
  let rec loop () =
    let tok, p = scan t in
    out := (tok, p) :: !out;
    if tok <> Token.EOF then loop ()
  in
  loop ();
  List.rev !out
