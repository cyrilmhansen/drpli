(* lib/codegen.ml — MINIMAL 8080 code generator + LINK-80 .REL emitter for
   the PL/I-80 reimplementation. Deliberately scoped to the fixed-BINARY
   integer assignment subset needed by the first end-to-end specimen
   (P071A): assignment of an integer expression (literal, variable copy,
   +, and the -1 / small-const peepholes) to a simple scalar.

   Inputs shared with the IR builder: Parser AST + Bind storage rows.
   Encodings taken VERBATIM from oracle-verified $C disassembly and the
   reldump record stream (spec/notes/codegen.md §1-2, C056/C064). Nothing
   here is invented: every opcode is cross-checked against DR output.

   Anything outside the supported subset raises a clear
   [codegen: unsupported ...] failure rather than guessing. *)

open Rel80

type vkind = Vint | Vfix of int | Vvar of int | Vdec of int * int | Vflt
   (* fixed/varying char capacity. Varying representation PROVEN
      [V101-V104]: length byte at offset 0, data at +1..+n, total
      n+1 bytes (binder authority Bind.bytes_of).
      [E2E-6] Vdec(p,s) = FIXED DECIMAL(p,s); storage bytes =
      ceil((p+1)/2) little-endian packed BCD with the sign nibble in
      the top nibble of the last byte -- confirmed on FOUR independent
      precisions: p=5 -> 3, p=7 -> 4, p=9 -> 5, p=15 -> 8
      [R503/R508/R502/R501 + DFACT], which is exactly Bind.bytes_of
      RTdec; codegen never re-derives sizes. *)
type var_info = { off : int; size : int; vk : vkind; w : int }
(* print width for FIXED BIN: min(9, digits(2^p-1)+4) -- banded rule
   matching ALL 16 probed points p=1..15,16,24 + default15 [N301-N308;
   C079]. NOT a linear formula. *)
let bin_digits10 n =
  let rec go x acc = if x < 10 then acc + 1 else go (x / 10) (acc + 1) in
  go n 0
let binw p = min 9 (bin_digits10 ((1 lsl p) - 1) + 4)
let dec_digits k =
  let k = abs k in
  if k = 0 then 1 else bin_digits10 k

type st =
  { base : int                        (* pool base = total pool bytes *)
  ; mutable items : rel_item list
  ; mutable pool : (int * int list) list  (* (data-addr, bytes) literal blocks *)
  ; mutable pool_next : int           (* next free pool offset *)
  ; mutable fmtq : int list
      (* [E2E-8] FIFO of pre-allocated PUT EDIT format-table addresses.  DR
         allocates EVERY format table in a block BEFORE any other pool item --
         proven by R1003 (table at *S(0000) while the 'AB' literal used by the
         EARLIER statement `c = 'AB'` sits at *S(0005)), R1021 (two tables,
         then both literals) and R1022 (a table inside a DO body still comes
         before the top-level literal).  Tables keep source/depth-first order
         among themselves, literals among themselves. *)
  ; mutable float_ret : bool
      (* [E2E-10] the current procedure RETURNS FLOAT: `return (e)` has to
         leave the value on DR's float stack and exit through JMP ?FPRET,
         plus ?RSBLK when the activation is recursive [R3038, FFACT] *)
  ; mutable fl_cells : (int * int list) list
      (* [E2E-10] float literal cells already allocated, for DEDUPLICATION by
         identical bytes [C101: R3007/R3010/R3012/R3013 share cells] *)
  ; mutable dec_cells : (int list * int) list
                                        (* [R614] DEC literal cells are
                                           DEDUPLICATED by byte content:
                                           `d = 3; e = 3;` (both dec(9,2))
                                           emits LXI H,* S(0000) twice from
                                           the SAME 5-byte cell, so DR
                                           reuses rather than re-allocating.
                                           This CORRECTS the E2E-6 note that
                                           DEC cells are never deduplicated,
                                           which was inferred only from R505
                                           (two literals, DIFFERENT values).
                                           Keyed on the packed bytes, so a
                                           differing precision or scale (a
                                           different byte image) still gets
                                           its own cell. *)
  ; mutable lc : int                  (* code location counter *)
  ; mutable last_imm : int option     (* HL still holds this constant?
                                         [G114 b=3 folded from a=5] *)
  ; mutable temps : int               (* dynamic-DO bound temp slots
                                         (2 bytes each, AFTER declared
                                         area [Y302: temp@6 = pool2+4;
                                         Y305: temp@5 = pool1+4]) *)
  ; mutable lowered : int             (* statements actually lowered
                                         (discard-invariant witness) *)
  (* ---- E2E-5c call state [P401/P402/RFACT bytes] ---- *)
  ; mutable stop_seen : bool          (* explicit stop; suppresses the
                                         epilogue CALL ?STOPX [P401: no
                                         second STOPX after dbl code] *)
  ; mutable calls : Bind.call_site list   (* prescan FIFO, DFS order *)
  ; mutable procs : (string * Bind.proc_layout) list
  ; mutable entries : (string * int) list (* lowered proc -> entry lc *)
  ; mutable fcalls : (string * int) list  (* pending forward CALL slots *)
  ; mutable deref : string list           (* ptr-formal names, cur scope *)
  ; mutable floor : int                   (* layout total (cells+procs) *)
  ; mutable vars : (string * var_info) list
      (* scope chain head (lowername -> info); swapped per procedure
         body [PL/I nesting: inner declarations shadow outer] *)
  ; mutable dec_ret : (int * int) option
      (* [E2E-6] Some(p,s) while lowering the body of a procedure whose
         RETURNS type is FIXED DECIMAL(p,s): selects the ?DLDOP/
         ?DSTOP/JMP ?DCRET path for RETURN [DFACT @007B, R509 @0041] *)
  ; mutable guards : int      (* tail-guard JMPs emitted (max one) *)
  ; mutable appended : bool   (* a TOP-LEVEL procedure body has been
                                 appended at the tail address. Every
                                 golden lowers ALL procedures AFTER
                                 every main-block statement; a live
                                 main statement following an appended
                                 proc is an unobserved DR layout, so
                                 it fails loud instead of guessing. *)
  ; mutable guard_slots : int list
      (* [R404/R405/R406/R423/R429/R432/P404] tail-guard operand slots.
         TAIL GUARD (bytes, 37-specimen matrix): when a top-level
         PROCEDURE body is appended at the address control reaches from
         the MAIN tail (fall-through OR a forward reference such as a
         DO-loop exit jump) AND the epilogue CALL ?STOPX is emitted
         AFTER that appended code, DR emits 3 bytes at the append
         address, BEFORE the entry label / forward-call CHAIN-ADDR /
         prologue:
             C3 00 00            JMP <epilogue CALL address>
         resolved by the usual deferred triple (SET-LC(code,slot),
         RELOC(code,epi), SET-LC(code,epi)) emitted immediately BEFORE
         the epilogue CALL bytes themselves [R404: JMP operand @29 ->
         44 = the CD of the epilogue CALL ?STOPX; R405 @29 -> 6E;
         P404 @10 -> 2B; R423 @34 -> 57; R432 @0D -> 28]. NOTE the
         target is the epilogue CALL INSTRUCTION, not its operand slot
         -- the same continuation mechanism as the PUT/LXI-B triples
         [G113/P401]. CORRECTION to the earlier note in this file: the
         discriminator is NOT "can the main tail loop exit" but
         "is the epilogue displaced past appended proc code", i.e.
         (no explicit stop printed in place) AND (suppression window
         CLOSED at the proc entry). Open-window tails emit an
         unconditional back edge and LOSE the epilogue => no guard
         [RFACT/R407/R408/R410/R411/R414/R421/R422/R424/R425/R426/
         R427/R431]; stop-in-place tails need no jump either [P401/
         R409/R416/R417/R430/R433]. *)
  ; mutable in_proc : bool    (* lowering a procedure body *)
  ; mutable in_rec : bool     (* lowering a RECURSIVE proc body *)
  ; mutable after_forever : bool  (* last MAIN stmt = no-exit loop/stop *)
  ; mutable secs : (string * int * int) list (* proc -> base,size excl pool *)
  ; mutable last_loop_edge : int }
(* label bookkeeping for GOTO resolution [G115/G116]:
   emitted-labels assoc (lowername -> lc); pending forward refs
   (lowername -> operand slot). *)
type lblstate = { mutable labs : (string * int) list
                ; mutable fwd : (string * int) list }

let push st it = st.items <- st.items @ [it]
let d st v = push st (Data (v land 0xff)); st.lc <- st.lc + 1
let reloc st seg v =
  push st (Reloc (seg, v)); st.lc <- st.lc + 2          (* inline: 2 bytes *)
let link st t valu name = push st (Link (t, valu, name))

(* allocate a constant-pool entry (ONE block per literal), returning its
   data-segment address. G113 evidence: DR emits a SET-LC(data,addr) per
   POOL BLOCK (string/dec literal allocation), not one flat byte run —
   single-block programs like G107/G106/P071D cannot distinguish, two
   strings prove it. *)
let pool_alloc st (bytes : int array) =
  let addr = st.pool_next in
  st.pool <- st.pool @ [(addr, Array.to_list bytes)];
  st.pool_next <- addr + Array.length bytes;
  addr

let pool_bytes (s : string) =
  Array.init (String.length s) (fun i -> Char.code (String.get s i))

(* ---- opcodes (8080) : all cross-checked against DR .REL bytes ---- *)
let op_lxi_b = 0x01
let op_lxi_d = 0x11
let op_lxi_h = 0x21
let op_lhld = 0x2a
let op_shld = 0x22
let op_dad_d = 0x19
let op_dad_b = 0x09
let op_dcx_h = 0x2b
let op_inx_h = 0x23
let op_xchg = 0xeb
let op_call = 0xcd
let op_push_h = 0xe5
let op_pop_d = 0xd1
let op_mvi_a = 0x3e
let op_mvi_b = 0x06
let op_mov_b_a = 0x47   (* [V102/V103] len==cap store peephole *)
let op_mvi_m = 0x36     (* [V104] MVI M,00: empty-varying store *)
let op_push_psw = 0xf5  (* [W102] PSW guard before nested SLVTS *)
let op_jp = 0xf2      (* [X201/X202] GET skip byte; $C prints "JP";
                          REL byte is F2 = JPE (same family as the ^=
                          CA/"JZ" quirk [C072]); operand patched by a
                          deferred triple to the QIOOP call [X202] *)
let op_mov_l_a = 0x6f
let op_mov_h_a = 0x67
let op_add_a = 0x87
let op_sbb_a = 0x9f

(* variable data-segment address = pool base + declared auto offset.
   [int subset has no pool => base 0; matches DR SHLD/LHLD operands] *)
let addr_of st name =
  let li = String.lowercase_ascii name in
  match List.assoc_opt li st.vars with
  | Some vi -> vi.off + st.base
  | None -> failwith ("codegen: undeclared " ^ name)

let vk_of st name =
  let li = String.lowercase_ascii name in
  match List.assoc_opt li st.vars with
  | Some vi -> vi.vk
  | None -> failwith ("codegen: undeclared " ^ name)

let call_ext st name =
  (* CALL <external RTL>: operand slot = cd 00 00, immediately followed by
     LINK-CHAIN-EXT at the operand address [DR emits CHAIN-EXT per call site]
     — matches ?START/?STOPX/?IM22N/?ID22N/?IMDOP record streams *)
  d st op_call;
  let slot = st.lc in
  d st 0; d st 0;
  link st t_chain_ext (Some (Code, slot)) (Some name)

let op_jmp  = 0xc3
let op_jnz  = 0xc2
let op_jz   = 0xc4
let op_jp   = 0xf2
let op_jm   = 0xfa
let op_mov_a_m = 0x7e
let op_ora_m   = 0xb6
let op_dcr_c = 0x0d      (* DCR C (counted-copy loop) [R2031]; 0x05 = DCR B *)
let op_mov_a_h = 0x7c
let op_ora_a   = 0xb7

(* deferred forward-fixup triple [C062/G107/G113/G114]: placeholder
   already emitted at SLOT; now that target VALUE is known write
   SET-LC(code,slot) / RELOC(code,value) / SET-LC(code,value). *)
let emit_triple st slot value =
  link st t_set_lc (Some (Code, slot)) None;
  push st (Reloc (Code, value));
  link st t_set_lc (Some (Code, value)) None

(* ---- decimal constant POOL (DATA segment) ----
   PL/I-80 stores a literal-base `k ** n` base as a DECIMAL pool entry
   (proven across 6 samples 2/7/12/25/100 + P071D):
     p        = number of decimal digits of k
     bytes    = ceil((p+1)/2)            (PL/I dec storage: +1 sign nibble)
     packing  = little-endian, 2 BCD digits/byte as (hi<<4 | lo), most-
                significant nibble zero-padded [100 -> 00 01 ; 25 -> 25 00 ;
                12 -> 12 00 ; 7 -> 07 ; 2 -> 02]
   Pool sits at data offset 0; auto vars are placed ABOVE it, so every
   variable address = pool_total + declared_soffset (matches DR SHLD
   operands P071D z@1, G106 q@3=pool1+q2). DLDOP precision = p [MVI A,p].
   DATA-seg REL emission order [P071D reldump]:
     SET-LC(data,0) ; pool DATA bytes ; DEF-DATA-SIZE(abs, pool+auto) ;
     SET-LC(code,0) ; code ...   (no pool -> just DEF-DATA-SIZE ; SET-LC(code))
*)
let dec_pool_bytes p = (p + 1 + 1) / 2   (* ceil((p+1)/2) *)

let dec_digits_of k =
  let k = abs k in
  let rec go x acc = if x < 10 then acc + 1 else go (x / 10) (acc + 1) in
  if k = 0 then 1 else go k 0

(* literal text -> (magnitude of ALL digits, own digit count, number of
   fractional digits): "123.45" -> (12345,5,2), "1234" -> (1234,4,0) *)
let dec_lit_value (s : string) : int * int * int =
  let t = String.concat "" (String.split_on_char '_' s) in
  match String.split_on_char '.' t with
  | [ ip ] ->
      if ip = "" then failwith "codegen: malformed numeric literal [TBD]";
      (int_of_string ip, String.length ip, 0)
  | [ ip; fp ] ->
      let all = ip ^ fp in
      let mag = if all = "" then 0 else int_of_string all in
      (mag, dec_digits_of mag, String.length fp)
  | _ -> failwith "codegen: malformed decimal literal [TBD]"

let expr_kind_name (k : Ast.expr_kind) =
  match k with
  | Ast.Eident _ -> "ident"        | Ast.Eqstruct _ -> "qualified name"
  | Ast.Eqptr _ -> "pointer designator" | Ast.Enumber _ -> "numeric literal"
  | Ast.Estring _ -> "character literal" | Ast.Ebit _ -> "bit string"
  | Ast.Eprefix _ -> "prefix operator"  | Ast.Ebinary _ -> "binary operator"
  | Ast.Econd _ -> "condition"          | Ast.Esuffix _ -> "call/index"
  | Ast.Ebuilt _ -> "builtin"           | Ast.Eformat_ref _ -> "format ref"
  | Ast.Epicture _ -> "picture"


let bcd_pack (k : int) (p : int) =
  let nbytes = dec_pool_bytes p in
  let digs =
    let ds = string_of_int k in
    Array.init p (fun i -> Char.code (String.get ds i) - 48)   (* MSB-first *)
  in
  (* digits reversed to least-significant-first nibble order *)
  let lsf = Array.to_list digs |> List.rev in
  let nib = fun i -> try List.nth lsf i with _ -> 0 in
  Array.init nbytes (fun b -> ((nib (2 * b + 1)) lsl 4) lor (nib (2 * b)))


(* sum of decimal-pool bytes required by literal-base ** over all stmts
   (pure pre-scan, no side effects; mirrors pool_alloc ordering). *)

(* [E2E-6] prescan needs the same DEC-literal byte counts the lowering
   run will allocate.  Literal cells are TARGET-precision in bare
   assignment/RETURN position [R501/R505/DFACT] and OWN-digit-count as
   arithmetic operands [R509/R511].  cx carries every block's variable
   kinds and the current procedure's DEC return type; the map is built
   over the whole program, so a name declared with two DIFFERENT types
   is refused instead of silently mis-sizing the pool. *)
exception Fl_range of string

(* --- exact decimal-string helpers: no int64 magnitude limits ---------- *)
let ds_trim (s : string) : string =
  let t = String.trim s in
  let i = ref 0 in
  while !i < String.length t - 1 && t.[!i] = '0' do incr i done;
  if !i > 0 then String.sub t !i (String.length t - !i) else t

let ds_cmp (a : string) (b : string) : int =
  let a = ds_trim a and b = ds_trim b in
  if String.length a <> String.length b then
    compare (String.length a) (String.length b)
  else compare a b

let ds_double (s : string) : string =
  let carry = ref 0 in
  let out = Bytes.make (String.length s + 1) '0' in
  for i = String.length s - 1 downto 0 do
    let v = (Char.code s.[i] - 48) * 2 + !carry in
    Bytes.set out (i + 1) (Char.unsafe_chr (48 + v mod 10));
    carry := v / 10
  done;
  Bytes.set out 0 (Char.unsafe_chr (48 + !carry));
  ds_trim (Bytes.to_string out)

let ds_pow10 (n : int) : string = "1" ^ String.make n '0'

let ds_two_pow24 = "16777216"               (* 2^24: hidden bit plus 23 stored *)
let ds_two_pow23 = "8388608"

(* literal text -> (negative, magnitude digits, decimal scale), where
   value = digits * 10^(-scale).  Handles "1.5", "3E7", "-0.1", "1E-20",
   "1.4691E-39".  More than 18 significant digits is refused: DR garbles
   long tiny literals (R3029/R3041 compile to cells unrelated to their
   value), so that band cannot be reproduced byte-exactly by anything. *)
let fl_lit_split (text : string) : bool * string * int =
  let t0 = String.concat "" (String.split_on_char '_' text) in
  let t = String.map (fun c ->
      if c = 'd' || c = 'D' || c = 'e' then 'E' else c) t0 in
  let (neg, t) =
    if String.length t > 0 && t.[0] = '-' then
      (true, String.sub t 1 (String.length t - 1))
    else if String.length t > 0 && t.[0] = '+' then
      (false, String.sub t 1 (String.length t - 1))
    else (false, t)
  in
  let (mant, expo) =
    match String.index_opt t 'E' with
    | Some i ->
        let ex = String.sub t (i + 1) (String.length t - i - 1) in
        if ex = "" then failwith "codegen: malformed float literal [TBD]";
        (String.sub t 0 i, int_of_string ex)
    | None -> (t, 0)
  in
  let (ip, fp) =
    match String.split_on_char '.' mant with
    | [ a ] -> (a, "")
    | [ a; b ] -> (a, b)
    | _ -> failwith "codegen: malformed float literal [TBD]"
  in
  if String.length ip + String.length fp > 400 then
    failwith "codegen: absurdly long numeric literal [TBD]";
  let raw = ds_trim (ip ^ fp) in
  let rec go d sc =
    let l = String.length d in
    if l > 0 && d.[l - 1] = '0' then
      go (String.sub d 0 (l - 1)) (sc - 1)
    else (d, sc)
  in
  let (digits, scale) = go raw (String.length fp - expo) in
  let digits = if digits = "" then "0" else digits in
  if digits = "0" then (neg, "0", 0)
  else begin
    if String.length digits > 18 then
      failwith
        (Printf.sprintf
           "codegen: float literal %s has %d significant digits, beyond the band DR converts exactly [TBD] (R3029/R3041: long tiny literals compile to unrelated bytes)"
           text (String.length digits));
    (neg, digits, scale)
  end

(* single decimal digit division: divide string `a` by the single digit `dv`,
   returning (quotient, remainder) *)
let ds_div1 (a : string) (dv : int) : string * int =
  let q = Bytes.make (String.length a) '0' in
  let rem = ref 0 in
  for i = 0 to String.length a - 1 do
    let cur = !rem * 10 + (Char.code a.[i] - 48) in
    Bytes.set q i (Char.unsafe_chr (48 + cur / dv));
    rem := cur mod dv
  done;
  (ds_trim (Bytes.to_string q), !rem)

(* subtract non-negative decimal strings, a >= b *)
and ds_sub_small (a : string) (b : string) : string =
  let la = String.length a and lb = String.length b in
  let out = Bytes.make la '0' in
  let borrow = ref 0 in
  for i = la - 1 downto 0 do
    let x = Char.code a.[i] - 48 - !borrow
            - (if i - (la - lb) >= 0 then Char.code b.[i - (la - lb)] - 48 else 0) in
    if x < 0 then begin Bytes.set out i (Char.unsafe_chr (x + 58)); borrow := 1 end
    else begin Bytes.set out i (Char.unsafe_chr (x + 48)); borrow := 0 end
  done;
  if !borrow <> 0 then failwith "codegen: internal: negative remainder in float model";
  ds_trim (Bytes.to_string out)

(* long division of two non-negative decimal strings: (quotient, remainder).
   Schoolbook, one dividend digit at a time, with the running remainder kept
   as a STRING -- DR's float range reaches 2**127, i.e. ~39 decimal digits,
   which no machine integer holds. *)
let ds_divmod (a : string) (dv : string) : string * string =
  let dv = ds_trim dv in
  if dv = "0" then failwith "codegen: internal: zero divisor in float model";
  if ds_cmp a dv < 0 then ("0", ds_trim a)
  else if dv = "1" then (ds_trim a, "0")
  else begin
    (* dv's digit count is implied by the long-division walk *)
    let qbuf = Buffer.create (String.length a) in
    let remb = ref "" in
    for i = 0 to String.length a - 1 do
      remb := ds_trim (!remb ^ String.make 1 a.[i]);
      let c = ref 0 in
      while ds_cmp !remb dv >= 0 do
        remb := ds_sub_small !remb dv;
        incr c
      done;
      Buffer.add_char qbuf (Char.unsafe_chr (48 + !c))
    done;
    (ds_trim (Buffer.contents qbuf), ds_trim !remb)
  end

(* floor(digits * 10^(-scale) * 2^p) as a decimal string, plus the exact
   discarded remainder and its denominator, so the caller can decide a tie
   WITHOUT any floating-point.  p may be negative (values >= 2^24 need a
   right shift), which is why the denominator is a string, not a "how many
   digits were dropped" count. *)
let fl_shift (digits : string) (scale : int) (p : int)
    : string * string * string =
  (* numerator = digits * 10^(max(-scale,0)) * 2^(max(p,0)) *)
  let num = ref (digits ^ String.make (max (-scale) 0) '0') in
  for _ = 1 to max p 0 do num := ds_double !num done;
  (* denominator = 10^(max(scale,0)) * 2^(max(-p,0)) *)
  let den = ref (ds_pow10 (max scale 0)) in
  for _ = 1 to max (-p) 0 do den := ds_double !den done;
  let (q, r) = ds_divmod !num !den in
  (q, r, !den)

(* the binary exponent k with 2^k <= value < 2^(k+1).  A double estimate
   starts the search; every step is DECIDED BY EXACT COMPARISON, so float
   round-off cannot choose the exponent.  t(k) = floor(value * 2^24 / 2^k)
   is >= 2^24 exactly when value >= 2^k. *)
let fl_k (digits : string) (scale : int) : int =
  let dv =
    try float_of_string digits with _ ->
      failwith "codegen: cannot read float literal magnitude [TBD]"
  in
  (* this OCaml has no Float.log2: derive it, and note the estimate is only a
     STARTING POINT -- fl_k's loop decides every step by exact comparison *)
  let ln2 = Float.log 2.0 in
  let flog2 x = Float.log x /. ln2 in
  let est =
    try
      if scale >= 0 then
        int_of_float (Float.floor (flog2 dv -. float_of_int scale *. flog2 10.))
      else
        int_of_float
          (Float.floor (flog2 (dv *. (10. ** float_of_int (-scale)))))
    with _ -> 0
  in
  let est = if est <> est then 0 else est in
  let rec go k tries =
    if tries > 4000 then
      failwith
        "codegen: float literal exponent search did not converge [TBD]";
    (* t(k) = floor(value * 2^(23-k)) is >= 2^24 exactly when value >= 2^(k+1),
       and < 2^23 exactly when value < 2^k, so these two comparisons pin k *)
    let (tq, _, _) = fl_shift digits scale (23 - k) in
    if ds_cmp tq ds_two_pow24 >= 0 then go (k + 1) (tries + 1)
    else if tq = "0" || ds_cmp tq ds_two_pow23 < 0 then go (k - 1) (tries + 1)
    else k
  in
  go est 0

(* literal text -> DR's 4 bytes. *)
let mbf_encode (text : string) : bytes =
  let (neg, digits, scale) = fl_lit_split text in
  if digits = "0" then Bytes.of_string "\000\000\000\000"
  (* DR has NO negative zero: `-0.0` shares the all-zero cell [R3007] *)
  else begin
    let k = fl_k digits scale in
    let (tq, rem, den) = fl_shift digits scale (23 - k) in
    let t = int_of_string tq in   (* tq is in [2^23,2^24), so this is safe *)
    (* t is in [2^23, 2^24): the hidden bit sits at 2^23 and the 23 stored
       fraction bits below it.  Nearest, ties away from zero [R3020], the same
       tie direction the DECIMAL ROUND law C087 reached independently. *)
    (* nearest, ties away from zero: the discarded fraction is rem/den, so it
       rounds up exactly when 2*rem >= den [R3020] *)
    let up =
      if rem = "0" || rem = "" then false
      else ds_cmp (ds_double rem) den >= 0
    in
    let (t, k) =
      if up then
        let t = t + 1 in
        if t >= 1 lsl 24 then (1 lsl 23, k + 1) else (t, k)
      else (t, k)
    in
    let e = k + 129 in
    if e > 255 then
      raise
        (Fl_range
           (Printf.sprintf
              "magnitude 2**%d exceeds DR's float upper bound 2**127 [TBD] (DR pass-2 CONVERT rejects it: R3016/R3025)"
              k));
    if e < 0 then
      raise
        (Fl_range
           (Printf.sprintf
              "magnitude 2**%d is below DR's float lower bound 2**-129 [TBD] (DR rejects the deep cases with pass-2 CONVERT [R3015-R3017, R3026, R3028, R3047] but its SHALLOW-underflow band compiles to unrelated bytes [R3029/R3048]; I reproduce neither)"
              k));
    if e = 0 && t = 1 lsl 23 then
      raise
        (Fl_range
           "magnitude exactly 2**-129 collides with DR's zero encoding (bytes 00 00 00 00) [TBD]; the only exponent-byte-0 value ever observed is 2E-39, which has a NONZERO fraction [R3023]");
    let frac = t - (1 lsl 23) in
    Bytes.of_string
      (String.make 1 (Char.unsafe_chr (frac land 0xff))
      ^ String.make 1 (Char.unsafe_chr ((frac lsr 8) land 0xff))
      ^ String.make 1
          (Char.unsafe_chr (((frac lsr 16) land 0x7f)
                            lor (if neg then 0x80 else 0)))
      ^ String.make 1 (Char.unsafe_chr e))
  end

type pdec_ctx =
  { pd_vars : (string * vkind) list
  ; pd_procs : (string * (int * int) option) list
  ; pd_ret : (int * int) option
  ; pd_dec : (int * int * int) list ref
  ; pd_fl : int list list ref
      (* [E2E-10] float literal cell byte-images already counted, so pool
         DEMAND counts each distinct 4-byte cell once (DR deduplicates them
         [C101, R3007/R3010/R3012/R3013]) *)
  ; pd_fl_ret : bool
      (* [E2E-10] the block being prescanned RETURNS FLOAT, so its literal
         operands become float cells rather than DEC/FIXED values *)
  ; pd_fl_procs : string list
      (* [E2E-10] names (lower-cased) of procedures whose RETURNS type is
         FLOAT BINARY(24).  pd_procs carries DEC precisions only and
         pd_vars holds VARIABLES, so float-returning callees need their own
         list -- without it the pool demand missed FFACT's return literal and
         every data address after the pool shifted down 4 bytes. *)
      (* [R614] distinct DEC literal cells already counted.  DR REUSES a
         decimal pool cell whose byte image is identical -- `d = 3; e = 3;`
         (both dec(9,2)) emits LXI H,* S(0000) twice against ONE 5-byte cell
         -- so pool DEMAND must count each distinct cell once.  Key is the
         packed image (precision, scale, scaled magnitude), i.e. exactly the
         byte content the lowering run compares in dec_pool. This replaces
         the E2E-6 assumption that DEC cells are never deduplicated, which
         was inferred from R505 (two literals, DIFFERENT values). *) }

let pdec_pow10 n =
  let rec go v k = if k = 0 then v else go (v * 10) (k - 1) in go 1 n

(* count the pool bytes for one DEC literal occurrence, 0 if an
   identical cell was already counted [R614] *)
let pdec_dec_cell cx (p : int) (sc : int) (text : string) : int =
  let (mag, _own, ls) = dec_lit_value text in
  if ls > sc then 0          (* the lowering refuses this case *)
  else begin
    let key = (p, sc, mag * pdec_pow10 (sc - ls)) in
    if List.mem key !(cx.pd_dec) then 0
    else (cx.pd_dec := key :: !(cx.pd_dec); dec_pool_bytes p)
  end

(* parenthesised expressions arrive Econd-wrapped [N304]; prescan must
   see through them exactly like lowering does *)
(* [E2E-10] count the pool bytes for one FLOAT literal occurrence: 4 if the
   byte image is new, 0 if that identical cell was already counted.  The
   bytes come from the SAME encoder the lowering uses, so demand and layout
   cannot drift apart.  A literal the encoder refuses (out of range, the
   2**-129 collision, >18 digits) still counts 4 bytes: such a program is
   refused by the lowering and never emits a .REL, so the total is moot. *)
let pdec_fl_cell (cx : pdec_ctx) (text : string) : int =
  let key =
    try
      let b = mbf_encode text in
      List.init (Bytes.length b) (fun i -> Char.code (Bytes.get b i))
    with _ -> [ 0; 0; 0; 4 ]
  in
  if List.mem key !(cx.pd_fl) then 0
  else begin
    cx.pd_fl := key :: !(cx.pd_fl);
    4
  end

(* [E2E-10] float literals inside a float expression, in evaluation order.
   Fixed operands contribute nothing (they are converted at run time by
   ?QI15F) and a float call's arguments are frame temporaries, not pool. *)
let rec pdec_fl_expr (cx : pdec_ctx) (e : Ast.expr) : int =
  (* inlined: pdec_unwrap/unwrap_e are both defined below this point *)
  let e = match e.Ast.e with Ast.Econd x -> x | _ -> e in
  match e.Ast.e with
  | Ast.Enumber t -> pdec_fl_cell cx t
  | Ast.Ebinary (_, l, r) -> pdec_fl_expr cx l + pdec_fl_expr cx r
  | Ast.Eprefix (p, x) ->
      (match (match x.Ast.e with Ast.Econd y -> y | _ -> x).Ast.e with
       | Ast.Enumber k when p = Ast.Minus -> pdec_fl_cell cx ("-" ^ k)
       | _ -> pdec_fl_expr cx x)
  | Ast.Econd inner -> pdec_fl_expr cx inner
  | Ast.Esuffix (_hd, args) ->
      (* A FLOAT call argument that is a LITERAL needs its pool cell demanded
         here: DR passes it by address through the descriptor [R3062:
         `LXI H,*A(0010)`, the slot pointing at the 4-byte literal cell], so
         the cell exists before the variable area is based.  Without this the
         prescan sized the pool 2 bytes short, the variables overlapped the
         literal cell, and every downstream address shifted.  A VARIABLE
         argument needs no demand (its cell is a declared variable); a general
         expression argument has no DR sample and the lowering refuses it. *)
      List.fold_left
        (fun acc a ->
          match (match a.Ast.e with Ast.Econd x -> x | _ -> a).Ast.e with
          | Ast.Enumber t -> acc + pdec_fl_cell cx t
          | _ -> acc)
        0 args
  | _ -> 0

let pdec_unwrap (e : Ast.expr) =
  match e.Ast.e with Ast.Econd x -> x | _ -> e

let pdec_own_digits s =
  (* the literal's OWN digit count -- same rule the lowering run uses
     for operand-position DEC literals [R509 *2 -> 1 digit; R511 *1234
     -> 4 digits -> 3-byte cell] *)
  let (_mag, own, _ls) = dec_lit_value s in
  own

let rec pdec_operand_bytes (cx : pdec_ctx) (e : Ast.expr) =
  match e.Ast.e with
  | Ast.Econd x -> pdec_operand_bytes cx x
  | Ast.Enumber s ->
      pdec_dec_cell cx (pdec_own_digits s) 0 s
  (* [R608] ADD/SUB ALIGN the integer literal to its DEC partner: `p = p - 1`
     against dec(9,2) pushes MVI A,09 from a 5-byte cell holding 1.00, NOT
     the own-digit cell that * and / use [R509/R511/LOAN1]. Sizing the cell
     from the partner here is what keeps the pool aligned; if the partner's
     precision is unknown the lowering refuses, so nothing is under-sized
     silently. *)
  | Ast.Ebinary ((Ast.Add | Ast.Sub) as op, l, r) ->
      let unw x = match x.Ast.e with Ast.Econd y -> y | _ -> x in
      let islit x = match (unw x).Ast.e with Ast.Enumber _ -> true | _ -> false in
      let prec x =
        match (unw x).Ast.e with
        | Ast.Eident n ->
            (match List.assoc_opt (String.lowercase_ascii n.Ast.orig) cx.pd_vars
             with Some (Vdec (p, sc)) -> Some (p, sc) | _ -> None)
        | Ast.Esuffix (b, _) ->
            (match b.Ast.e with
             | Ast.Eident n ->
                 (match List.assoc_opt (String.lowercase_ascii n.Ast.orig)
                          cx.pd_procs with
                  | Some (Some (p, sc)) -> Some (p, sc)
                  | _ -> None)
             | _ -> None)
        | _ -> None
      in
      let side lit other =
        match (islit lit, prec other) with
        | true, Some (po, sc) ->
            let k = match (unw lit).Ast.e with
                    | Ast.Enumber t -> t
                    | _ -> assert false
            in
            pdec_dec_cell cx po sc k
        | _ -> pdec_operand_bytes cx lit
      in
      ignore op; side l r + side r l
  | Ast.Ebinary (_, l, r) -> pdec_operand_bytes cx l + pdec_operand_bytes cx r
  | Ast.Eprefix (_, x) -> pdec_operand_bytes cx x
  (* [E2E-7A slice 3] ROUND(a,n): the ARGUMENT's literals need pool cells like
     any other DEC operand -- LOAN1's `round(i*P/1200, 2)` puts the 1200 cell
     inside the call, and under-counting it moves the AUTO base (R813 caught
     that: my first build sized the pool 3 bytes short).  The digit count n is
     an IMMEDIATE byte (it becomes MVI A, s-n), never a pool cell. *)
  | Ast.Ebuilt ("ROUND", [ a; _ ]) -> pdec_operand_bytes cx a
  | Ast.Ebuilt ("DECIMAL", _) -> 0   (* integer argument: no DEC cell *)
  | _ -> 0

(* is this expression DEC-typed at prescan time? (mirrors codegen's
   is_dec_expr but reads the prescan context instead of st) *)
let rec pdec_is_dec (cx : pdec_ctx) (e : Ast.expr) =
  match e.Ast.e with
  | Ast.Econd x -> pdec_is_dec cx x
  | Ast.Eident n ->
      (match List.assoc_opt (String.lowercase_ascii n.Ast.orig) cx.pd_vars
       with Some (Vdec _) -> true | _ -> false)
  | Ast.Ebuilt ("DECIMAL", _) -> true
  | Ast.Esuffix (b, _) ->
      (match b.Ast.e with
       | Ast.Eident n ->
           (match List.assoc_opt (String.lowercase_ascii n.Ast.orig)
                    cx.pd_procs with
            | Some (Some _) -> true
            | _ -> false)
       | _ -> false)
  | Ast.Ebinary (_, l, r) -> pdec_is_dec cx l || pdec_is_dec cx r
  | Ast.Eprefix (_, x) -> pdec_is_dec cx x
  | _ -> false

let rec prescan_expr (cx : pdec_ctx) (e : Ast.expr) =
  match e.Ast.e with
  | Ast.Ebinary (Ast.Exp, l, r) ->
      let extra =
        match (l.Ast.e, r.Ast.e) with
        | Ast.Enumber bs, Ast.Enumber _ ->
            let k = String.concat "" (String.split_on_char '_' bs) in
            dec_pool_bytes (String.length k)
        | _ -> 0
      in
      prescan_expr cx l + prescan_expr cx r + extra
  | Ast.Ebinary (Ast.Sub, { Ast.e = Ast.Enumber a; _ },
                 { Ast.e = Ast.Enumber b; _ }) ->
      (* [N301/N306] const-minus-const DLDOP operands each take a
         dec pool entry *)
      let pint s =
        int_of_string (String.concat "" (String.split_on_char '_' s))
      in
      dec_pool_bytes (dec_digits (pint a))
      + dec_pool_bytes (dec_digits (pint b))
  | Ast.Ebinary (_, l, r) -> prescan_expr cx l + prescan_expr cx r
  | Ast.Eprefix (_, x) -> prescan_expr cx x
  | Ast.Ebuilt (_, es) ->
      List.fold_left (fun a x -> a + prescan_expr cx x) 0 es
  | _ -> 0

type chain = C2 of string * string * string   (* lit || var [W101] *)
           | C3 of string * string * string   (* lit || var || lit [W102] *)
type pitem = PIlit of string | PIvar of Ast.name | PInum of Ast.expr
type put_shape = Pnone | Plit of string option * string
               | Pvar of string option * Ast.expr
               | Pcat of string option * chain
               | Pitems of string option * pitem list

(* flatten a (left-assoc per our parser) || chain to operands
   left-to-right; only the proven shapes C2 [lit;varying] and
   C3 [lit;varying;lit] survive; anything else -> None -> [TBD]
   at lowering [W101/W102] *)
let flatten_cat (e : Ast.expr) =
  let rec leaves2 x acc =
    match x.Ast.e with
    | Ast.Ebinary (Ast.Cat, l, r) ->
        (* prepend accumulator => recurse RIGHT first to end up with
           SOURCE order left-to-right *)
        (match leaves2 r acc with
         | Some a -> leaves2 l a
         | None -> None)
    | Ast.Estring s -> Some (("STR", s) :: acc)
    | Ast.Eident n -> Some (("VAR", n.Ast.orig) :: acc)
    | _ -> None
  in
  match leaves2 e [] with
  | Some ls ->
      (match ls with
       | [ ("STR", l); ("VAR", v) ] -> Some (C2 (l, v, ""))
       | [ ("STR", l); ("VAR", v); ("STR", r2) ] ->
           Some (C3 (l, v, r2))
       | _ -> None)
  | None -> None

(* item classification (syntax-only; char-vs-numeric resolved at
   lowering where the binder's vk is known). Numeric CONSTANTS alone
   have no DR evidence -> reject. [N301-N306] *)
let classify_item (x : Ast.expr) =
  match x.Ast.e with
  | Ast.Estring v -> Some (PIlit v)
  | Ast.Eident n -> Some (PIvar n)
  | Ast.Ebinary _ | Ast.Eprefix _ -> Some (PInum x)
  | Ast.Econd inner -> Some (PInum inner)  (* parens grouping [N304] *)
  | Ast.Esuffix (hd, args) when args <> [] ->
      (* [RFACT @3B-46] function-call item: pair + LXI H,*A(slot) +
         CALL; the result already sits in HL when the numeric chain
         reads it (MVI A,9; QICOP follows the CALL directly).
         [E2E-9/DECPOLY] the arity restriction is gone -- DR treats a
         3-argument decimal call item exactly like a 1-argument integer
         one (`LXI H,*A(0048) / CALL P / MVI A,12 / MVI B,04 / ?QDCOP`). *)
      (match hd.Ast.e with
       | Ast.Eident _ -> Some (PInum x)
       | _ -> None)
  | _ -> None

let match_skip_ctl (items : Ast.put_item list) =
  match items with
  | Ast.Pi_ctl ("SKIP", Some { Ast.e = Ast.Enumber c; _ }) :: tl ->
      Some (Some c, tl)
  | Ast.Pi_ctl ("SKIP", None) :: tl ->
      Some (Some "1", tl)   (* bare SKIP = 1 [N302: MVI A,01] *)
  | _ -> None

(* accepted shapes: literal [G107/G108/G113] or a SINGLE char/varying
   variable [V101/V106]; optional SKIP(const). Pnone -> [TBD]. *)
let all_data (items : Ast.put_item list) =
  let rec go acc = function
    | [] -> Some (List.rev acc)
    | Ast.Pi_data x :: tl -> go (x :: acc) tl
    | _ -> None
  in
  go [] items

(* PUT forms other than PUT LIST are NOT implemented.  Corpus audit REV
   2 defect D1: PUT EDIT / PUT ITEM / bare PUT SKIP used to escape as an
   uncaught Match_failure from this function during the pool prescan
   (IFACT, OPTIMIST, SAMPLE).  They are refused by name now, which is
   the project's fail-loud contract; the implemented subset is PUT LIST
   with optional leading SKIP control item [G107/G108/N301-N306]. *)
let put_kind_str (k : Ast.put_kind) =
  match k with
  | Ast.List_ -> "LIST"
  | Ast.Edit -> "EDIT"
  | Ast.Item -> "ITEM (also the parse form of bare PUT SKIP;/PAGE;)"
  | Ast.Editsk _ -> "SKIP(n) without LIST"

let match_put_list_lit (s : Ast.stmt) =
  match s.Ast.st with
  | Ast.Sput { kind = (Ast.Edit | Ast.Item | Ast.Editsk _) as k; _ } ->
      failwith (Printf.sprintf
                  "codegen: PUT %s deferred [TBD] (line %d; only PUT LIST \
                   is implemented; format/picture editing needs the \
                   ?EDITF/?EDTOV/?QDDSL route family)"
                  (put_kind_str k) s.Ast.spos.Source.line)
  | Ast.Sput { stream = None; on_opts = []; kind = Ast.List_; items } ->
      let (sk, rest) =
        match match_skip_ctl items with
        | Some x -> x
        | None -> (None, items)
      in
      let one x = match classify_item x with
                   | Some i -> [i] | None -> []
      in
      match rest with
      | [ Ast.Pi_data ({ Ast.e = Ast.Estring v; _ } as x) ] ->
          ignore x; Plit (sk, v)          (* byte-frozen 3a path *)
      | [ Ast.Pi_data x ] ->
          (match flatten_cat x with
           | Some ch -> Pcat (sk, ch)     (* proven concat shapes *)
           | None ->
               (match one x with
                | [ it ] -> Pitems (sk, [it])
                | _ -> Pnone))
      | _ when List.length rest >= 2 ->
          (match all_data rest with
           | Some xs ->
               let its = List.map classify_item xs in
               if List.for_all (fun o -> o <> None) its then
                 Pitems (sk, List.map
                   (function Some i -> i | None -> assert false) its)
               else Pnone
           | None -> Pnone)
      | _ -> Pnone
  | _ -> Pnone

let parse_int_const (s : string) =
  int_of_string (String.concat "" (String.split_on_char '_' s))

(* ---- [E2E-8] PUT EDIT: the compiled format list --------------------
   Decoded byte-wise from 11 DR tables (golden/e2e11/ R1001-R1010,
   R1018-R1020, IFACT).  A format table is a DATA pool item:

       80 00 | record record ... record | 81

   and record length is FIXED PER OPCODE (that is what R1018 vs R1019 vs
   R1020 pin down):
       f(w)    -> 00 w FF   [R1001 f(3), R1002 f(12), R1019 f(1), IFACT f(2)/f(7)]
       f(w,d)  -> 00 w d    [R1018 f(6,2) -> 00 06 02]
       a       -> 03 FF     [R1003, R1010, IFACT]
       a(w)    -> 03 w      [R1008 a(5), R1020 a(3)]
       skip    -> 0C FF     [R1004, R1005, R1010, IFACT]
       page    -> 0F FF     [R1007]
   UNPINNED and therefore not modelled: the header's second byte (0x00 in all
   11 samples), counted skip/page (skip(n) is unsampled), and every other edit
   operator (x/b/e/v/i/n/m/c/p/picture/remote/rep-group).  Those refuse.
*)
let fmt_w (e : Ast.expr) =
  match e.Ast.e with
  | Ast.Enumber t ->
      let v = parse_int_const t in
      if v < 0 || v > 255 then
        failwith "codegen: PUT EDIT width outside 0..255 [TBD]";
      v
  | _ -> failwith "codegen: PUT EDIT non-constant width [TBD] \
                   (only literal widths are sampled)"

let fmt_spec (it : Ast.put_item) : int list =
  match it with
  | Ast.Pi_ctl (k, None) when k = "SKIP" -> [ 0x0c; 0xff ]
  | Ast.Pi_ctl (k, None) when k = "PAGE" -> [ 0x0f; 0xff ]
  | Ast.Pi_ctl (_, Some _) ->
      failwith "codegen: PUT EDIT counted SKIP/PAGE is unsampled [TBD] \
                (only the bare form's second byte 0xFF has been observed)"
  | Ast.Pi_fmt { fkey = "F"; fargs = [ w ]; fcount = None } ->
      [ 0x00; fmt_w w; 0xff ]
  | Ast.Pi_fmt { fkey = "F"; fargs = [ w; d ]; fcount = None } ->
      [ 0x00; fmt_w w; fmt_w d ]
  | Ast.Pi_fmt { fkey = "A"; fargs = []; fcount = None } -> [ 0x03; 0xff ]
  | Ast.Pi_fmt { fkey = "A"; fargs = [ w ]; fcount = None } -> [ 0x03; fmt_w w ]
  | Ast.Pi_fmt { fkey = k; _ } ->
      failwith (Printf.sprintf
                  "codegen: PUT EDIT operator %s is unsampled [TBD] \
                   (only F and A formats are decoded from DR tables)" k)
  | _ ->
      failwith "codegen: PUT EDIT format item form unsampled [TBD] \
                (counted, grouped, picture, remote and rep-group formats \
                 are not decoded)"

let fmt_table_bytes (specs : Ast.put_item list) =
  if specs = [] then failwith "codegen: PUT EDIT with an empty format list [TBD]";
  Array.of_list (([ 0x80; 0x00 ] @ List.concat_map fmt_spec specs) @ [ 0x81 ])

(* `put edit(items)(specs);' -- default stream, no ON options, no leading
   SKIP/PAGE control item (that combination is unsampled: in every EDIT probe
   the skip lives INSIDE the format list).  Items accept exactly what PUT LIST
   prepares -- char literal, fixed-bin variable/expression, char varying --
   because [R1001/R1003/R1010/IFACT] show DR reusing the same value preparation
   with ?EDTOV in place of ?PNCOP/?PNVOP.  FIXED DECIMAL items are refused at
   lowering: no DR sample puts a DEC item through an edit list. *)
let match_put_edit (s : Ast.stmt) =
  match s.Ast.st with
  | Ast.Sput { stream = None; on_opts = []; kind = Ast.Edit; items } ->
      let rec data acc = function
        | [] -> None                     (* no format list: not an EDIT shape *)
        | Ast.Pi_fmtlist specs :: tl ->
            if tl <> [] || acc = [] then None
            else Some (List.rev acc, specs)
        | Ast.Pi_data x :: tl -> data (x :: acc) tl
        (* a control/rep/picture/remote item in the DATA half of an EDIT list
           is unsampled: refuse rather than guess where it belongs *)
        | _ -> None
      in
      (match data [] items with
       | Some (ds, specs) ->
           let its = List.map classify_item ds in
           if List.for_all (fun o -> o <> None) its then
             Some (List.map (function Some i -> i | None -> assert false) its,
                   specs)
           else None
       | None -> None)
  | _ -> None

(* [E2E-8] depth-first source-order walk: every accepted PUT EDIT statement
   in the order lowering will reach it.  Used to pre-allocate the format
   tables at the front of the pool, which is where DR puts them. *)
let rec edit_stmts (ss : Ast.stmt list) : Ast.stmt list =
  List.concat_map
    (fun s ->
      match s.Ast.st with
      | Ast.Sput _ ->
          if match_put_edit s <> None then [ s ] else []
      | Ast.Sdobegin body -> edit_stmts body
      | Ast.Sif { then_; els; _ } ->
          then_ :: (match els with Some e -> [ e ] | None -> [])
          |> edit_stmts
      | Ast.Sdowhile { body; _ } | Ast.Sdoforever body | Ast.Sdoto { body; _ } ->
          edit_stmts [ body ]
      | Ast.Sproc b -> edit_stmts b.Ast.blk.Ast.bstmts
      | _ -> [])
    ss

let prealloc_fmt_tables st (ss : Ast.stmt list) =
  st.fmtq
    <- List.map
         (fun s ->
           match match_put_edit s with
           | Some (_, specs) -> pool_alloc st (fmt_table_bytes specs)
           | None -> assert false)
         (edit_stmts ss)

(* GET LIST (varying);) — single varying data item, default stream,
   no ON opts, no edit. Shapes beyond this raise [TBD] at lowering
   [X201/X202]. *)
let match_get_list_var (s : Ast.stmt) =
  match s.Ast.st with
  (* [E2E-7A slice 4] GET LIST accepts ANY number of simple name items
     [R904 pins the multi-item lowering order].  Every other item shape
     (subscripted, expression, EDIT/STRING form, file options, stream) still
     falls through to the [TBD] refusal at the call site. *)
  | Ast.Sget { stream = None; on_opts = []; kind = Ast.List_; items } ->
      let rec names acc = function
        | [] -> if acc = [] then None else Some (List.rev acc)
        | Ast.Pi_data { Ast.e = Ast.Eident n; _ } :: tl -> names (n :: acc) tl
        | _ -> None
      in
      names [] items
  | _ -> None

(* pool demand: RECURSIVE over container bodies (G114: puts live inside
   IF arms; a flat scan under-counts the pool and shifts DATA) *)
(* [E2E-7A slice 1] a DECIMAL comparison literal takes a pool cell sized
   by the OTHER (decimal) operand's precision -- DR pushes `0` as
   MVI A,09 against a dec(9,2) variable [R507/R607] and as A=0B against
   LOAN1's dec(11,2) P (6-byte cell at S(001E)).  prescan_stmt did not
   visit conditions at all, so without this the pool is under-sized and
   every variable address after it is short by the missing cell. *)
let rec prescan_cond (cx : pdec_ctx) (c : Ast.expr) =
  let unwrap x = match x.Ast.e with Ast.Econd y -> y | _ -> x in
  let prec_of e =
    match (unwrap e).Ast.e with
    | Ast.Eident n ->
        (match List.assoc_opt (String.lowercase_ascii n.Ast.orig) cx.pd_vars
         with Some (Vdec (p, sc)) -> Some (p, sc) | _ -> None)
    | Ast.Esuffix (b, _) ->
        (match b.Ast.e with
         | Ast.Eident n ->
             (match List.assoc_opt (String.lowercase_ascii n.Ast.orig)
                      cx.pd_procs with
              | Some (Some (p, sc)) -> Some (p, sc)
              | _ -> None)
         | _ -> None)
    | _ -> None
  in
  let litof e = match (unwrap e).Ast.e with Ast.Enumber k -> Some k | _ -> None in
  match (unwrap c).Ast.e with
  | Ast.Ebinary (Ast.EqR _, a, b) ->
      let one side other =
        match litof side, prec_of other with
        | Some k, Some (p, sc) -> pdec_dec_cell cx p sc k
        | _ -> 0
      in
      one a b + one b a
  | Ast.Ebinary (_, l, r) -> prescan_cond cx l + prescan_cond cx r
  | Ast.Eprefix (_, x) -> prescan_cond cx x
  | _ -> 0

let rec prescan_stmt (cx : pdec_ctx) (s : Ast.stmt) =
  match s.Ast.st with
  | Ast.Sassign { lhs; rhs } ->
      (* [E2E-6] a DEC store of a bare literal allocates one TARGET-
         precision cell; a DEC arithmetic expression allocates one cell
         per literal at the literal's own digit count [R501/R505/R511] *)
      let dec_store_bytes =
        match lhs.Ast.e with
        | Ast.Eident n ->
            (match List.assoc_opt (String.lowercase_ascii n.Ast.orig)
                     cx.pd_vars with
             | Some (Vdec (p, sc)) ->
                 let rhs = pdec_unwrap rhs in
                 (match rhs.Ast.e with
                  | Ast.Enumber t -> pdec_dec_cell cx p sc t
                  | _ -> if pdec_is_dec cx rhs
                         then pdec_operand_bytes cx rhs else 0)
             | _ -> 0)
        | _ -> 0
      in
      (* [E2E-10] a FLOAT target store takes FLOAT cells for its literals
         (R3036 `d7 = a * 2` makes `2` a 4-byte float cell, not a DEC one),
         so the DEC demand path must be skipped entirely for that statement *)
      let fl_target =
        match lhs.Ast.e with
        | Ast.Eident n ->
            (match List.assoc_opt (String.lowercase_ascii n.Ast.orig)
                     cx.pd_vars with
             | Some Vflt -> true
             | _ -> false)
        | _ -> false
      in
      if fl_target then pdec_fl_expr cx rhs
      else
      dec_store_bytes
      + (match rhs.Ast.e with
         | Ast.Estring v -> String.length v
             (* char-store pool demand [V101-V103/V105]; '' reserves 0
                [V104]; type-mismatched uses RAISE at lowering *)
         | _ -> prescan_expr cx rhs)
  | Ast.Sreturn (Some e0) ->
      (* [E2E-10] a FLOAT function's literal becomes a float cell: FFACT's
         `return (1)` is the 4-byte cell at *S(000C), which sits AFTER the
         main block's two character cells, matching first-use order *)
      if cx.pd_fl_ret then pdec_fl_expr cx e0 else
      (* [E2E-6] a bare literal RETURNed from a DEC function takes a
         TARGET-precision pool cell [DFACT return(1) = 8 bytes at
         S(000C)]; DEC arithmetic literals take their own digit cells *)
      (match cx.pd_ret with
       | Some (p, sc) ->
           let e = pdec_unwrap e0 in
           (match e.Ast.e with
            | Ast.Enumber t -> pdec_dec_cell cx p sc t
            | _ -> if pdec_is_dec cx e then pdec_operand_bytes cx e else 0)
       | None -> 0)
  | Ast.Sput _ ->
      (* [E2E-8] a PUT EDIT statement consumes pool space for the compiled
         FORMAT TABLE plus its item literals, and the table is allocated
         BEFORE the literals [*S(0000) in all 11 samples].  Missing it would
         shift every later data address silently -- the exact failure mode of
         the slice-3 ROUND prescan bug. *)
      (match match_put_edit s with
       | Some (its, specs) ->
           Array.length (fmt_table_bytes specs)
           + List.fold_left
               (fun a it -> match it with
                | PIlit v -> a + String.length v
                | PInum x -> a + prescan_expr cx x
                | PIvar _ -> a) 0 its
       | None ->
      (match match_put_list_lit s with
       | Plit (_, v) -> String.length v
       | Pcat (_, C2 (l, _, _)) -> String.length l
       | Pcat (_, C3 (l, _, r)) -> String.length l + String.length r
       | Pitems (_, its) ->
           List.fold_left
             (fun a it -> match it with
              | PIlit v -> a + String.length v
              | PInum x -> a + prescan_expr cx x
              | PIvar _ -> a) 0 its
       | _ -> 0)             (* var-puts consume no pool [V101] *))
  | Ast.Sif { cond; then_; els; _ } ->
      prescan_cond cx cond
        + prescan_stmt cx then_
        + (match els with Some e -> prescan_stmt cx e | None -> 0)
  | Ast.Sdobegin ss -> List.fold_left (fun a x -> a + prescan_stmt cx x) 0 ss
  | Ast.Sdowhile { cond; body; _ } ->
      prescan_cond cx cond + prescan_stmt cx body
  | Ast.Sdoto { while_; body; _ } ->
      (* the DO ... WHILE guard can hold a DEC comparison literal; sizing
         it here keeps the pool aligned instead of shifting every later
         data address silently (a compare DR's lowering refuses anyway is
         still a refusal, never a short pool) *)
      (match while_ with Some e -> prescan_cond cx e | None -> 0)
        + prescan_stmt cx body
  | Ast.Sdoforever body -> prescan_stmt cx body
  | Ast.Sproc b ->
      (* descending into a procedure: RETURN literals take THAT
         procedure's decimal return precision [DFACT] *)
      let pn =
        match b.Ast.blk.Ast.bname with
        | Some n -> String.lowercase_ascii n.Ast.orig
        | None -> ""
      in
      let ret =
        match List.assoc_opt pn cx.pd_procs with Some r -> r | None -> None
      in
      List.fold_left
        (* pd_procs carries DEC return types only, so floatness comes from
           the kind map (a float-returning procedure appears there as Vflt) *)
        (fun a x ->
          a + prescan_stmt { cx with pd_ret = ret
                                   ; pd_fl_ret =
                                       (List.mem pn cx.pd_fl_procs) } x) 0
        b.Ast.blk.Ast.bstmts
  | _ -> 0

let prescan_pool (cx : pdec_ctx) (stmts : Ast.stmt list) =
  List.fold_left (fun acc s -> acc + prescan_stmt cx s) 0 stmts

(* ---- E2E-3a: PUT LIST '<char literal>' [G107/G108 $C-verified] ------
   Supported shape ONLY (match_put_list_lit); anything else fails loud.
   DR sequence (e2eput2 goldens, reldump + $C):
     LXI D,0252 ; LXI B,0000 ; CALL ?SYSPR
     [skip: MVI A,n ; CALL ?SKPOP]        (G108; SKPOP BEFORE data emit)
     LXI H,*S(pool) ; MVI A,len ; CALL ?SLCTS ; CALL ?PNCOP ; CALL ?QIOOP
   then a deferred backpatch triple per statement —
     SET-LC(code,bslot) ; RELOC(code,epi_addr) ; SET-LC(code,epi_addr) —
   emitted after the LAST statement, before the ?STOPX epilogue CALL:
   the LXI B operand receives the epilogue (continuation) address. *)
let lower_put_lit st (skipn : string option) (v : string) =
  d st op_lxi_d; d st 0x52; d st 0x02;
  d st op_lxi_b;
  let bslot = st.lc in
  d st 0; d st 0;
  call_ext st "?SYSPR";
  (match skipn with
   | Some c ->
       let n = int_of_string (String.concat "" (String.split_on_char '_' c)) in
       if n <= 0 || n > 255 then
         failwith "codegen: skip count out of MVI range [TBD]";
       d st op_mvi_a; d st n; call_ext st "?SKPOP"
   | None -> ());
  let bytes =
    Array.init (String.length v) (fun i -> Char.code (String.get v i))
  in
  let addr = pool_alloc st bytes in
  d st op_lxi_h; reloc st Data addr;
  d st op_mvi_a; d st (String.length v land 0xff);
  call_ext st "?SLCTS"; call_ext st "?PNCOP"; call_ext st "?QIOOP";
  (* G113: the backpatch triple is emitted INLINE after each put; the
     LXI B operand receives the CONTINUATION address (LC right after
     this statement), not an epilogue. [G107/G108: continuation == the
     ?STOPX call, so both models coincided.] *)
  emit_triple st bslot st.lc

(* count statements that MUST be accounted for by lowering (everything
   except declarations and empty statements). The counter + per-stmt
   `lowered` increments make silent discarding — including from future
   container statements — a hard failure. *)
let rec count_required (s : Ast.stmt) =
  match s.Ast.st with
  | Ast.Sdcl _ | Ast.Snull _ -> 0
  | Ast.Sdobegin ss ->
      1 + List.fold_left (fun a x -> a + count_required x) 0 ss
  | Ast.Sif { then_; els; _ } ->
      1 + count_required then_
        + (match els with Some e -> count_required e | None -> 0)
  | Ast.Sdowhile { body; _ } -> 1 + count_required body
  | Ast.Sdoto { body; _ } -> 1 + count_required body
  | Ast.Sdoforever body -> 1 + count_required body
  | Ast.Sproc b ->
      1 + List.fold_left (fun a x -> a + count_required x) 0
          b.Ast.blk.Ast.bstmts
  | _ -> 1


(* assemble: header ; [SET-LC data + pool bytes] ; DEF-DATA-SIZE ;
   SET-LC code ; prologue ; body ; epilogue ; tail.  Body is lowered
   into a scratch state (collecting code items + pool bytes), then
   re-emitted in segment order. *)

(* is this name an AUTOMATIC-or-formal FIXED DECIMAL variable?  Defined up
   here (not via vk_dec_opt, which lives in the DEC block below) so the CALL
   lowering can mode-check decimal arguments. *)
(* moved above the call lowering: a FLOAT call argument passes the address
   of its pool cell [R3062], so the descriptor path needs fl_pool too *)
(* float literal cells live in the SHARED pool (byte-packed, first-use
   order, deduplicated by identical bytes [C101]) but are tracked apart from
   DEC and character cells, so a coincidental byte match can never alias a
   string literal onto a float operand or the other way round. *)
let fl_pool st (b : bytes) =
  let l = List.init (Bytes.length b) (fun i -> Char.code (Bytes.get b i)) in
  match List.find_opt (fun (_addr, bs) -> bs = l) st.fl_cells with
  | Some (addr, _) -> addr
  | None ->
      let addr = pool_alloc st (Array.of_list l) in
      st.fl_cells <- st.fl_cells @ [ (addr, l) ];
      addr

let vk_is_dec st (n : Ast.name) =
  match List.assoc_opt (String.lowercase_ascii n.Ast.orig) st.vars with
  | Some vi -> (match vi.vk with Vdec _ -> true | _ -> false)
  | None -> false

(* strip a parenthesised-condition wrapper: DR lowers (c) exactly like c
   [P401 dbl body: (i+i)], and Econd also wraps while-conditions.  Moved up
   from the DEC model block so the CALL lowering can mode-check arguments. *)
let unwrap_e (e : Ast.expr) =
  match e.Ast.e with Ast.Econd x -> x | _ -> e

let is_ident (e : Ast.expr) =
  match e.Ast.e with Ast.Eident _ -> true | _ -> false



(* evaluate an integer expression, leaving the 16-bit value in HL *)
(* does evaluating e touch a pointer formal (deref ladder)? *)
let rec hl_operand_deref st (e : Ast.expr) =
  match e.Ast.e with
  | Ast.Eident n -> List.mem (String.lowercase_ascii n.Ast.orig) st.deref
  | Ast.Ebinary (_, a, b) -> hl_operand_deref st a || hl_operand_deref st b
  | Ast.Econd a | Ast.Eprefix (_, a) -> hl_operand_deref st a
  | _ -> false

(* [E2E-5c slice 2] tail = the continuation address that follows the
   MAIN block (tail_addr in emit_program). DR routes an ADD through
   PUSH H/POP D when the instruction at the evaluation position IS
   the tail position itself (RFACT's main increment at 0x4C:
   LHLD;INX H;SHLD) and uses the plain XCHG form elsewhere (dbl body
   at 0x30: MOV A,M / ORA M) [P401/P402/RFACT byte differentials]. *)
(* [E2E-9 slice 6] DR's FIXED BINARY peephole set, newly sampled by R2045,
   R2046 and P044.  All four shapes below are ones MY lowering gets WRONG --
   it emits a plausible instruction sequence instead of DR's -- so they fail
   loud here until the peepholes are implemented.  Every message carries the
   DR evidence that proves the divergence. *)
let lit_int (e : Ast.expr) =
  match e.Ast.e with
  | Ast.Enumber t -> (try Some (parse_int_const t) with _ -> None)
  | _ -> None

let fp_add_guard (l : Ast.expr) (r : Ast.expr) =
  match lit_int r with
  | Some 0 ->
      failwith
        ("codegen: fixed-bin ADD whose RIGHT operand is the literal 0 is "
         ^ "elided by DR to a bare `LHLD X ; SHLD X` pair [P044 line 5 "
         ^ "`x = x + 0`]; my general ladder is not that shape [TBD]")
  | _ ->
      (match lit_int l, lit_int r with
       | Some _, Some _ ->
           failwith
             ("codegen: fixed-bin ADD between TWO INTEGER LITERALS is not "
              ^ "constant-folded by DR: it emits the DECIMAL pool path "
              ^ "`LXI H,*S / MVI A,01 / CALL ?DLDOP / LXI H,*S / MVI A,01 / "
              ^ "CALL ?DLDOP / CALL ?DADOP / CALL ?QDI15` with one-byte "
              ^ "1-digit cells [R2045 `r = 3 + 2`, P044 line 3 `x = 2 + 4`]; "
              ^ "my immediate folding is not byte-equal [TBD].  Note this is "
              ^ "ADD-specific: `j = 0 - 7` [N301] and `e = 0 - 2` [N306] DO "
              ^ "fold to an immediate in DR, both byte-exact here.")
       | _ -> false)

let fp_mul_guard (l : Ast.expr) (r : Ast.expr) =
  match lit_int l, lit_int r with
  | _, (Some 1 | Some 2 as k) ->
      failwith
        ("codegen: fixed-bin MULTIPLY by literal "
         ^ string_of_int (match k with Some x -> x | None -> 0)
         ^ " is strength-reduced by DR, not sent to ?IM22N: `x * 1` ELIDES "
         ^ "to `LHLD X ; SHLD X` [P044 line 4] and `n * 2` becomes `LHLD n ; "
         ^ "DAD H ; SHLD n` [R2046 line 11]; my build emits the ?IM22N "
         ^ "rotation instead [TBD]")
  | Some _, Some _ ->
      failwith
        ("codegen: fixed-bin MULTIPLY between two integer literals is "
         ^ "unsampled -- no accepted DR object contains one [TBD]")
  | _ ->
      (match lit_int l, r.Ast.e with
       | Some _, (Ast.Eident _ | Ast.Ebinary (_, _, _) | Ast.Esuffix _) ->
           failwith
             ("codegen: fixed-bin multiply with the LITERAL on the LEFT is commuted "
         ^ "by DR into `LHLD <right> ; LXI D,<left> ; CALL ?IM22N` with no "
           ^ "stack rotation [P044 line 6 `x = 3 * x`]; my PUSH H / LXI H / "
           ^ "POP D ladder is not byte-equal [TBD]")
       | _ -> false)

let rec lower_hl st (e : Ast.expr) =
  match e.Ast.e with
  | Ast.Enumber s ->
      let v = int_of_string (String.concat "" (String.split_on_char '_' s)) in
      d st op_lxi_h; d st (v land 0xff); d st ((v lsr 8) land 0xff)
  | Ast.Esuffix (hd, args) ->
      (* [E2E-5c P401] single-argument internal procedure call.
         Deferred pointer pair + LXI H,*A(cell) + CALL; forward entry
         via CHAIN-ADDR resolved at the procedure's first byte, known
         entry via inline RELOC(code,entry) [P402 backward pattern] *)
      begin match hd.Ast.e, args with
      | Ast.Eident h, args when args <> [] ->
          let nm = String.lowercase_ascii h.Ast.orig in
          if not (List.mem_assoc nm st.procs) then
            failwith
              (Printf.sprintf "codegen: call to unknown %s [TBD]" nm);
          (match st.calls with
           | (cs :: rest) when cs.Bind.cs_proc = nm ->
               st.calls <- rest;
               if List.length cs.Bind.cs_args <> List.length args then
                 failwith "codegen: call-site arity mismatch [TBD]";
               (* [E2E-9] multi-argument internal call.  PER ARGUMENT, in
                  source order, DR does: (1) if the argument is an
                  EXPRESSION, evaluate it and SHLD the value into that
                  argument's value cell; (2) emit the descriptor address
                  constant for that argument's cell.  The two steps are
                  INTERLEAVED, not batched [R2032: RELOC(&i) lands BEFORE
                  the `j + 1` temp store, RELOC(&temp) AFTER it].  Then ONE
                  `LXI H,*A(slot)` + CALL for the whole block -- DR does NOT
                  emit one push per argument [R2001 two, R2034 three, R2035
                  four, DECPOLY three decimals]. *)
               let slot = cs.Bind.cs_slot + st.base in
               let pairs =
                 List.combine cs.Bind.cs_args cs.Bind.cs_temps
               in
               (* the callee's formal type at each position, so an argument
                  can be MODE-CHECKED [E2E-9]: DR's only pinned decimal
                  argument route is by-reference from an AUTOMATIC decimal
                  variable [DECPOLY, R2037/R2038, R725]. *)
               let pl = List.assoc nm st.procs in
               (* the callee's formal type at a position, used for MODE
                  checking; None = some other type or no re-declaration *)
               let formal_rt i =
                 match List.nth_opt pl.Bind.pl_ptrs i with
                 | Some (fn, _) ->
                     List.find_opt (fun (k, _rt, _o) -> k = fn)
                       pl.Bind.pl_rows
                 | None -> None
               in
               let formal_is_float i =
                 match formal_rt i with
                 | Some (_, Bind.RTfloat 24, _) -> true
                 | Some (_, Bind.RTfloat p, _) ->
                     failwith
                       ("codegen: FLOAT BINARY(" ^ string_of_int p
                        ^ ") formal is unsupported [TBD] (only BINARY(24) is "
                        ^ "characterized; C100/C101)")
                 | _ -> false
               in
               let formal_is_dec i =
                 match List.nth_opt pl.Bind.pl_ptrs i with
                 | Some (fn, _) ->
                     let frt =
                       List.find_opt (fun (k, _rt, _o) -> k = fn)
                         pl.Bind.pl_rows
                     in
                     begin match frt with
                     | Some (_, Bind.RTdec _, _) -> true
                     | Some _ -> false
                     | None ->
                         failwith
                           ("codegen: call argument against a formal with no "
                            ^ "declaration [TBD] (DR requires the callee to "
                            ^ "redeclare its formals [R2007])")
                     end
                 | None -> false
               in
               List.iteri
                 (fun i (arg, tmp) ->
                   (* [E2E-9] mode check.  Bound as `let () = ... in` on
                      purpose: an `if` whose THEN branch is a MATCH swallows
                      every following expression into the match's last arm
                      (a real DECPOLY byte failure -- the descriptor
                      constants vanished), so the guard must be sealed. *)
                   let () =
                     if formal_is_float i then
                       begin match (unwrap_e arg).Ast.e with
                       | Ast.Eident v when vk_of st v.Ast.orig = Vflt -> ()
                       | Ast.Eident v when List.mem
                             (String.lowercase_ascii v.Ast.orig) st.deref -> ()
                       | Ast.Enumber _ -> ()
                       | _ ->
                         failwith
                           ("codegen: non-float-variable argument against a "
                            ^ "FLOAT formal is unsampled [TBD] (DR's pinned "
                            ^ "float argument routes are a plain float "
                            ^ "variable or a float literal, both passed by "
                            ^ "address through the descriptor [R3061, R3062]; "
                            ^ "a FIXED argument takes a convert-into-temp-cell "
                            ^ "route [R3064: ?QI15F then ?FX44S into an "
                            ^ "anonymous float cell] which is understood but "
                            ^ "not yet implemented, and a general expression "
                            ^ "has no sample at all. Line "
                            ^ string_of_int arg.Ast.epos.Source.line ^ ")")
                       end
                   in
                   let () =
                     if formal_is_dec i then
                       begin match (unwrap_e arg).Ast.e with
                       | Ast.Eident v when vk_is_dec st v -> ()
                       | _ ->
                         failwith
                           ("codegen: non-variable argument against a FIXED "
                            ^ "DECIMAL formal is unproven [TBD] (DR passes an "
                            ^ "automatic decimal BY REFERENCE -- the "
                            ^ "descriptor holds LXI H,*A(cell); a literal or "
                            ^ "expression decimal argument has no sample "
                            ^ "[DECPOLY, R2037/R2038/R725]. Line "
                            ^ string_of_int arg.Ast.epos.Source.line ^ ")")
                     end
                   in
                   (match tmp with
                    | Some t ->
                        lower_hl st arg;
                        d st op_shld; reloc st Data (t + st.base)
                    | None -> ());
                   let target =
                     match tmp with
                     | Some t -> t + st.base
                     | None -> begin
                         match arg.Ast.e with
                         | Ast.Enumber k ->
                             if formal_is_float i then
                               (* a FLOAT literal argument is passed by address
                                  of its POOL cell [R3062: LXI H,*A(0010) with
                                  the descriptor pointing at the 4-byte cell],
                                  so the target is the float cell, not the
                                  2-byte integer cell the fixed route builds. *)
                               (match mbf_encode k with
                                | b -> fl_pool st b
                                | exception Fl_range msg ->
                                    failwith
                                      ("codegen: float literal argument "
                                       ^ k ^ " " ^ msg))
                             else begin
                               let kv = parse_int_const k in
                               pool_alloc st
                                 [| kv land 0xff; (kv lsr 8) land 0xff |]
                             end
                         | Ast.Eident v ->
                             let vn =
                               String.lowercase_ascii v.Ast.orig
                             in
                             if List.mem vn st.deref then
                               failwith
                                 ("codegen: pointer-formal call argument " ^
                                  "unproven [TBD]");
                             addr_of st v.Ast.orig
                         | _ ->
                             failwith
                               ("codegen: expression call argument " ^
                                "deferred [TBD]")
                       end
                   in
                   link st t_set_lc (Some (Data, slot + 2 * i)) None;
                   push st (Reloc (Data, target));
                   link st t_set_lc (Some (Code, st.lc)) None)
                 pairs;
               d st op_lxi_h; reloc st Data slot;
               d st op_call;
               (match List.assoc_opt nm st.entries with
                | Some a ->
                    (* known entry (backward/self): the CALL operand is
                       a single INLINE relocatable reference
                       [RFACT @8A cd+RELOC code 56; NFACT @99] *)
                    reloc st Code a
                | None ->
                    (* forward: two placeholder DATA bytes; resolved by
                       CHAIN-ADDR at the callee's entry byte
                       [P401 @9-000B + chain @1285] *)
                    let oslot = st.lc in
                    d st 0; d st 0;
                    st.fcalls <- (nm, oslot) :: st.fcalls);
               st.last_imm <- None
           | _ -> failwith "codegen: call-site queue mismatch [TBD]")
      | _ -> failwith "codegen: zero-arg / non-identifier call deferred [TBD]"
      end
  | Ast.Eident n ->
      (match vk_of st n.Ast.orig with
       | Vint -> ()
       | Vdec _ ->
           failwith
             "codegen: decimal operand inside an integer expression [TBD] \
              (mixed-mode routes are unpinned)"
       | Vflt ->
           failwith
             "codegen: FLOAT value used where a FIXED value is expected [TBD] (the float-to-fixed route ?FL40M/?QFI15 appears only inside FFACT's prologue, so no standalone conversion or mixed-mode arithmetic is sampled)"
      | _ -> failwith "codegen: arithmetic on char variable [TBD]");
      let vi = List.assoc (String.lowercase_ascii n.Ast.orig) st.vars in
      if vi.size = 1
         && List.mem (String.lowercase_ascii n.Ast.orig) st.deref then
        failwith "codegen: 1-byte pointer formal unproven [TBD]";
      if vi.size = 1 then begin
        (* [N306/N303] 1-byte FIXED BIN: LD A,dir (3A+RELOC) then
           sign-extend into HL: MOV L,A; ADD A; SBB A; MOV H,A *)
        st.last_imm <- None;
        d st 0x3a; reloc st Data (addr_of st n.Ast.orig);
        d st op_mov_l_a; d st op_add_a; d st op_sbb_a; d st op_mov_h_a
      end
      else begin
        d st op_lhld; reloc st Data (addr_of st n.Ast.orig);
        if List.mem (String.lowercase_ascii n.Ast.orig) st.deref then
          (* pointer formal: dereference the passed address [P401 dbl:
             LHLD i; MOV E,M; INX H; MOV D,M; XCHG -> HL = value] *)
          (d st 0x5e; d st 0x23; d st 0x56; d st 0xeb);
        st.last_imm <- None   (* runtime value; not a const *)
      end

  | Ast.Econd x ->
      (* parentheses around an arithmetic expression arrive Econd-wrapped
         (RETURN(expr), item positions). DR lowers them EXACTLY like the
         unwrapped expression [P401 dbl body: (i+i) -> standard Add
         ladder], so unwrap transparently. *)
      lower_hl st x
  | Ast.Ebinary (Ast.Add, l, r) when fp_add_guard l r ->
      failwith "codegen: internal: fp_add_guard raised no message"
  | Ast.Ebinary (Ast.Add, l, { Ast.e = Ast.Enumber "1"; _ }) ->
      (* [(a+1) N304] +1 lowers to INX H on the 2-byte path; other
         additions keep the general ladder *)
      lower_hl st l; d st op_inx_h; st.last_imm <- None
    | Ast.Ebinary (Ast.Add, l, r) ->
      (* DR: HL=left ; XCHG ; HL=right ; DAD D  (=> HL = right+left)
         [P071A]. WITH POINTER-DEREF OPERANDS the ladder is
         left ; PUSH H ; right ; POP D ; DAD D [P401 dbl (i+i):
         E5 @37, D1 @3F] — forced by mechanics: the deref ladder's own
         XCHG (EB) clobbers DE, so the XCHG form cannot preserve the
         left value across a second deref. *)
      if hl_operand_deref st l || hl_operand_deref st r then begin
        lower_hl st l; d st 0xe5;                    (* PUSH H *)
        lower_hl st r; d st 0xd1; d st op_dad_d      (* POP D; DAD D *)
      end else begin
        lower_hl st l; d st op_xchg; lower_hl st r; d st op_dad_d
      end
  | Ast.Ebinary (Ast.Mul, l, r) when fp_mul_guard l r ->
      failwith "codegen: internal: fp_mul_guard raised no message"
  | Ast.Ebinary (Ast.Mul, l, r) ->
      (* var/expr OP var: DE=left HL=right, CALL ?IM22N [P071B/P080A].
         [N303] when the RHS is a 1-byte var DR interleaves: raw
         LDA, PUSH H (save left), THEN sign-extend in HL, POP D.
         [RFACT/NFACT @8D/@9C] when the RIGHT operand is a CALL the
         whole right side runs FIRST (arg eval, pair, LXI, CALL,
         PUSH H, LHLD left, POP D) — left-first ordering is only
         evidenced for plain operands [P080A]. *)
      if (match r.Ast.e with Ast.Esuffix _ -> true | _ -> false)
         && not (match l.Ast.e with Ast.Esuffix _ -> true | _ -> false)
      then begin
        lower_hl st r; d st 0xe5;                  (* PUSH H *)
        lower_hl st l; d st 0xd1                   (* POP D *)
      end else if hl_operand_deref st l
                  && (match r.Ast.e with
                      | Ast.Enumber _ -> true | _ -> false)
      then begin
        (* [E2E-9 R2036 g1] when the LEFT operand is a pointer formal, its
           deref ladder ends in XCHG -- value in HL, DE dead -- and DR then
           skips the PUSH H / LXI H / POP D rotation entirely, loading the
           literal straight into DE:
               LHLD a ; MOV E,M ; INX H ; MOV D,M ; XCHG
               LXI D,0003 ; CALL ?IM22N ; RET
           Legal because ?IM22N multiplies DE x HL, so the operand-to-register
           assignment is free.  The non-deref left case keeps the proven
           PUSH/POP shape [P071B/P080A byte-exact]. *)
        lower_hl st l;
        let rv =
          parse_int_const
            (match r.Ast.e with Ast.Enumber k -> k | _ -> "")
        in
        d st op_lxi_d; d st (rv land 0xff); d st ((rv lsr 8) land 0xff)
      end else begin
      lower_hl st l;
      (match r.Ast.e with
       | Ast.Eident rn ->
           let rvi =
             List.assoc (String.lowercase_ascii rn.Ast.orig) st.vars
           in
           if rvi.vk = Vint && rvi.size = 1 then begin
             d st 0x3a; reloc st Data (rvi.off + st.base);
             d st op_push_h;
             d st op_mov_l_a; d st op_add_a; d st op_sbb_a;
             d st op_mov_h_a;
             d st op_pop_d
           end else begin
             d st op_push_h; lower_hl st r; d st op_pop_d
           end
       | _ -> d st op_push_h; lower_hl st r; d st op_pop_d)
      end;
      call_ext st "?IM22N"
  | Ast.Ebinary (Ast.Div, l, r) ->
      (* DIV by CONSTANT only [P071B/P080A]: zero-extend const into HL via
         MVI A/PUSH/POP idiom, DE=lhs. DIV by variable = no golden -> reject.*)
      (match r.Ast.e with
       | Ast.Enumber c ->
           let n =
             int_of_string (String.concat "" (String.split_on_char '_' c))
           in
           if n = 0 then failwith "codegen: division by zero";
           lower_hl st l;
           d st op_mvi_a; d st (n land 0xff);
           d st op_push_h; d st op_mov_l_a; d st op_add_a; d st op_sbb_a;
           d st op_mov_h_a; d st op_pop_d; call_ext st "?ID22N"
       | _ -> failwith "codegen: DIV by non-constant [TBD]")
  | Ast.Ebinary (Ast.Exp, l, r) ->
      (* EXPONENTIATION has two DISTINCT DR lowerings (probes e2eexp):
         - VARIABLE base:  a ** n => LHLD a; MVI A,n; CALL ?IEXOP [G102]
         - LITERAL base:   k ** n => decimal POOL path
           (LXI H,*S; MVI A,p; DLDOP; MVI A,n; DEXOP; QDI15), base k stored
           as BCD pool ceil((p+1)/2) bytes, auto vars shifted up by pool
           size [P071D/G101/G103/G104/G105].  Both implemented. *)
      (match (l.Ast.e, r.Ast.e) with
       | (Ast.Eident _, Ast.Enumber c) ->
           let n =
             int_of_string (String.concat "" (String.split_on_char '_' c))
           in
           lower_hl st l; d st op_mvi_a; d st (n land 0xff);
           call_ext st "?IEXOP"
       | (Ast.Eident _, _) -> failwith "codegen: ** non-constant exponent [TBD]"
       | (Ast.Enumber bs, Ast.Enumber cs) ->
           let k =
             int_of_string (String.concat "" (String.split_on_char '_' bs))
           in
           let e =
             int_of_string (String.concat "" (String.split_on_char '_' cs))
           in
           let p = String.length (string_of_int k) in
           let addr = pool_alloc st (bcd_pack k p) in
           d st op_lxi_h; reloc st Data addr;
           d st op_mvi_a; d st p; call_ext st "?DLDOP";
           d st op_mvi_a; d st (e land 0xff); call_ext st "?DEXOP";
           call_ext st "?QDI15"
       | _ -> failwith "codegen: ** non-constant exponent [TBD]")
  | Ast.Ebinary (Ast.Sub, { Ast.e = Ast.Enumber ls; _ },
                 { Ast.e = Ast.Enumber rs; _ }) ->
      (* [N301/N306] const-minus-const: DEC pool chain (operands
         allocated SOURCE order; A = decimal digit count each),
         result 16-bit in HL via ?QDI15. The store tail (SHLD or
         MOV A,L;STA) is added by the assignment path. *)
      let l = parse_int_const ls in
      let r = parse_int_const rs in
      let dl = dec_digits l and dr = dec_digits r in
      let al = pool_alloc st (bcd_pack l dl) in
      let ar = pool_alloc st (bcd_pack r dr) in
      d st op_lxi_h; reloc st Data al;
      d st op_mvi_a; d st dl; call_ext st "?DLDOP";
      d st op_lxi_h; reloc st Data ar;
      d st op_mvi_a; d st dr; call_ext st "?DLDOP";
      call_ext st "?DSUOP"; call_ext st "?QDI15";
      st.last_imm <- None
  | Ast.Ebinary (Ast.Sub, x, Ast.{ e = Ast.Enumber c; _ }) ->
      lower_hl st x; const_sub st (int_of_string c)
  | Ast.Ebuilt ("MOD", [l; r]) ->
      (* mod(a,b) -> DE=dividend, HL=divisor, CALL ?IMDOP; the REMAINDER comes
         back in HL [P071B L4, and re-verified by R909 for a VARIABLE divisor].
         [E2E-7A slice 4] a CONSTANT divisor takes a different form: DR loads
         it into A and runs the sign-extend ladder (MOV L,A; ADD A; SBB A;
         MOV H,A), with PUSH H slotted between the MVI and the ladder, NOT the
         LXI H,imm form used for stores [R908/R910/R911/R912, LOAN1
         `if mod(m,12) = 0`: 000F MVI A,0C / 0011 PUSH H / 0012-0015 ladder /
         0016 POP D].  P071B only exercises the variable form, so this
         distinction was invisible until now. *)
      (match r.Ast.e with
       | Ast.Econd { Ast.e = Ast.Enumber k; _ } | Ast.Enumber k ->
           let kk = parse_int_const k in
           if kk < 0 || kk > 255 then
             failwith
              "codegen: MOD with a constant divisor outside 0..255 [TBD] \
               (only the MVI A,k form is sampled)";
           lower_hl st l;
           d st op_mvi_a; d st kk;
           d st op_push_h;
           d st 0x6f; (* MOV L,A *)
           d st 0x87; (* ADD A *)
           d st 0x9f; (* SBB A *)
           d st 0x67; (* MOV H,A *)
           d st op_pop_d
       | _ -> lower_hl st l; d st op_push_h; lower_hl st r; d st op_pop_d);
      call_ext st "?IMDOP";
      st.last_imm <- None
  | Ast.Eprefix (Ast.Minus, x) ->
      (* [N304] -x: evaluate to HL, then ?IN20N (16-bit negate) *)
      lower_hl st x; call_ext st "?IN20N"; st.last_imm <- None
    | Ast.Ebinary (Ast.Sub, l, r) ->
      (* [E2E-8 T1/T3] var - var (neither side a literal, which the arm above
         handles): DR loads the left value, XCHGs, loads the right value and
         calls ?IS22N, which computes DE - HL into HL -- the Add pair-ladder
         with the add replaced by the subtract-call
         [`s = s - i': LHLD S / XCHG / LHLD I / CALL ?IS22N / SHLD S;
           `s = i - i' identical].  POINTER-DEREF operands have no DR sample in
         this route and stay refused. *)
      if hl_operand_deref st l || hl_operand_deref st r then
        failwith "codegen: fixed-bin subtraction with a pointer formal \
                  operand unproven [TBD]";
      lower_hl st l; d st op_xchg; lower_hl st r;
      call_ext st "?IS22N";
      st.last_imm <- None
  | Ast.Ebinary _ -> failwith "codegen: operator not in int subset [TBD]"
  | _ -> failwith "codegen: expression form not in int subset [TBD]"

(* subtract an integer constant: DR folds 1 -> DCX H, small n -> repeated
   DCX H (<=4 observed); anything larger is out of this subset. *)
and const_sub st n =
  if n = 1 then d st op_dcx_h
  else if n > 1 && n <= 4 then for _ = 1 to n do d st op_dcx_h done
  else failwith "codegen: constant sub magnitude [TBD]"

(* store a char literal into a char/varying variable [V101-V105] *)
let store_char st name (k : vkind) (v : string) =
  if List.mem (String.lowercase_ascii name) st.deref then
    failwith "codegen: store to pointer formal unproven [TBD]";
  let len = String.length v in
  if len > 255 then failwith "codegen: literal len > 255 [TBD]";
  d st op_lxi_h; reloc st Data (addr_of st name);
  match k with
  | Vvar cap ->
      (* V104/V108 evidence: the literal registers a pool BLOCK even
         when empty; only non-empty stores emit LXI D/?SMCVM. *)
      let bytes =
        Array.init len (fun i -> Char.code (String.get v i))
      in
      let addr = pool_alloc st bytes in
      if len = 0 then (d st op_mvi_m; d st 0)     (* [V104] *)
      else begin
        d st op_lxi_d; reloc st Data addr;         (* LXI D,*S [V101] *)
        d st op_mvi_a; d st (cap land 0xff);       (* A = capacity *)
        if len = cap then d st op_mov_b_a          (* [V102/V103] *)
        else begin d st op_mvi_b; d st len end;    (* B = length; len>cap
            ALLOWED as-is [V105 B=07,cap=3; RTL semantics not assumed] *)
        call_ext st "?SMCVM"
      end
  | Vfix cap ->
      (* only the V106 shape (0 < len < cap) is proven for fixed *)
      if len = 0 || len > cap then
        failwith "codegen: fixed-char store form unproven [TBD]"
      else if len = cap then
        failwith "codegen: fixed store len==cap MOV B/A unproven [TBD]"
      else begin
        let bytes =
          Array.init len (fun i -> Char.code (String.get v i))
        in
        let addr = pool_alloc st bytes in
        d st op_lxi_d; reloc st Data addr;
        d st op_mvi_a; d st cap;
        d st op_mvi_b; d st len;
        call_ext st "?SMCCM"
      end
  | Vint -> failwith "codegen: char store to numeric var [TBD]"

let is_small_int st (n : Ast.name) =
  let li = String.lowercase_ascii n.Ast.orig in
  match List.assoc_opt li st.vars with
  | Some vi -> vi.vk = Vint && vi.size = 1
  | None -> false

(* ================= [E2E-6] FIXED DECIMAL evaluation ================== *
   DR's decimal machine, read straight off the $C traces of R501-R512
   (golden/e2e6) and DFACT (golden/first8080u/DFACT + its re-probe):

     ?DLDOP  PUSH a DEC value:  HL = cell address, A = digits
     ?QI15D  PUSH: INT(15) value already in HL -> DEC
     <call>  a DEC function call leaves its result on the DEC stack --
             the callee exits with JMP ?DCRET instead of RET
             [DFACT @003E/@0093, R509 @0009]
     ?DADOP ?DSUOP ?DMUOP  pop two, push one.  Operands are pushed LEFT
             first [R505 a+b, c-a, a*b; R511 a*1234]; the one observed
             case where the RIGHT operand is a DEC call pushes it first,
             because the call has to run before the left operand is
             reloaded [DFACT: call, then LHLD i + ?QI15D, then ?DMUOP]
     ?QDDSR  rescale the top to the scale in A -- observed ONLY after
             ?DMUOP and ONLY when the store target has scale > 0
             [R505 dec(9,2) -> MVI A,02; R510 dec(9,0) -> none;
             DFACT dec(15,0) -> none].  ADD/SUB carry no rescale [R505].
             DIVISION (?QDDSL before / ?DDVOP / TWO ?QDDSR after)
             is NOT implemented -- unpinned, stays [TBD] [R512].
     ?DSTOP  POP into a DEC cell: HL = address, A = target digits
             [R501/R502/R503/R505/R508/R510/R511]
     ?QDCOP  POP and edit into the print buffer: A = width = p+3,
             B = scale [R501 18/0, R502 12/2, R503 8/0, R508 10/2,
             R510 12/0, R511 12/0, DFACT 18/0 -- p+3 on every sample]
     ?DCRET  DEC function exit: hand the top DEC value back to the
             caller [DFACT @0086/@00A2, R509 @0056]

   DEC LITERAL cells (pool, little-endian packed BCD, sign nibble in the
   top nibble of the last byte -- byte-for-byte verified against DR:
   3@p15 -> 01? no: 03 00 00 00 00 00 00 00 [R501]; 123.45@p7s2 ->
   45 23 01 00 [R508]; 1@p9s2 -> 00 01 00 00 00 [R505]; 1234@p4 ->
   34 12 [R511]; 1@p15s0 -> 01 00 .. [DFACT]):
     bare literal in assignment/RETURN position -> the TARGET's digits
     and scale [R501 d=3 p15; R505 a=1 p9 s2; DFACT return(1) p15]
     literal as an ARITHMETIC OPERAND -> its OWN digit count, scale 0
     [R509 *2 -> 1 byte/MVI A,01; R511 *1234 -> 2 bytes/MVI A,04]
   Negative literals, fractional literals in operand position, DEC
   comparisons and DEC arrays/structs are outside this evidence and are
   refused loudly. *)

(* little-endian packed BCD of the ALREADY-SCALED magnitude v *)
let bcd_pack_scaled (v : int) (p : int) =
  let nbytes = dec_pool_bytes p in
  let ds = string_of_int v in
  if String.length ds > p then
    failwith "codegen: DEC literal does not fit its precision [TBD]";
  let digs =
    Array.init p (fun i ->
      let j = i - (p - String.length ds) in
      if j >= 0 then Char.code (String.get ds j) - 48 else 0)
  in
  let lsf = Array.to_list digs |> List.rev in
  let nib i = try List.nth lsf i with _ -> 0 in
  Array.init nbytes (fun b -> ((nib (2 * b + 1)) lsl 4) lor (nib (2 * b)))

let dec_pool st ~prec ~scale ~text =
  let (mag, _own, ls) = dec_lit_value text in
  if mag < 0 || ls > scale then
    failwith
      (Printf.sprintf
         "codegen: DEC literal %s into scale %d [TBD] (only same-or-less \
          fractional digits are pinned; negative DEC literals are unpinned)"
         text scale);
  let rec mul10 v n = if n = 0 then v else mul10 (v * 10) (n - 1) in
  let bytes = bcd_pack_scaled (mul10 mag (scale - ls)) prec in
  let key = Array.to_list bytes in
  match List.assoc_opt key st.dec_cells with
  | Some addr -> addr                       (* [R614] reuse the live cell *)
  | None ->
      let addr = pool_alloc st bytes in
      st.dec_cells <- (key, addr) :: st.dec_cells;
      addr

let vk_dec vk = match vk with Vdec (p, s) -> Some (p, s) | _ -> None

let vk_dec_opt st (n : Ast.name) =
  match List.assoc_opt (String.lowercase_ascii n.Ast.orig) st.vars with
  | Some vi -> vk_dec vi.vk
  | None -> None

(* is this expression DEC-typed on the proven routes? *)
let rec is_dec_expr st (e : Ast.expr) : bool =
  match e.Ast.e with
  | Ast.Econd x -> is_dec_expr st x
  | Ast.Eident n -> vk_dec_opt st n <> None
  | Ast.Ebuilt ("DECIMAL", _) -> true
  | Ast.Esuffix (b, _) ->
      (match b.Ast.e with
       | Ast.Eident n ->
           (match List.assoc_opt (String.lowercase_ascii n.Ast.orig) st.procs
            with
            | Some pl ->
                (match pl.Bind.pl_ret with
                 | Some (Bind.RTdec _) -> true
                 | _ -> false)
            | None -> false)
       | _ -> false)
  | Ast.Ebinary (_, l, r) -> is_dec_expr st l || is_dec_expr st r
  | Ast.Eprefix (_, x) -> is_dec_expr st x
  | _ -> false

(* true iff every leaf of this DEC-typed expression is itself decimal:
   mixed DEC/INT arithmetic has NO golden evidence at all, so the DEC
   paths accept only pure decimal trees and refuse the mix loudly.
   (decimal(x,p) is the sanctioned INT->DEC doorway [R506/R509/DFACT];
   a DEC->INT conversion is proven only for a DIRECT decimal operand.) *)
let rec dec_pure st (e : Ast.expr) : bool =
  match e.Ast.e with
  | Ast.Econd x -> dec_pure st x
  | Ast.Eident n -> vk_dec_opt st n <> None
  | Ast.Ebuilt ("DECIMAL", _) -> true
  | Ast.Esuffix _ -> true                 (* DEC function result [DFACT] *)
  | Ast.Enumber _ -> true                 (* decimal literal cell *)
  | Ast.Ebinary (_, l, r) -> dec_pure st l && dec_pure st r
  | Ast.Eprefix (_, x) -> dec_pure st x
  | _ -> false

(* (precision, scale) to use when EDITING a DEC expression on output.
   Only the two directly observed shapes are allowed: a DEC variable
   [R501-R511] and a DEC function call [DFACT].  Printing the result of
   decimal() or of a DEC arithmetic expression directly is unpinned. *)
let dec_edit_pt st (e : Ast.expr) : int * int =
  match e.Ast.e with
  | Ast.Eident n ->
      (match vk_dec_opt st n with
       | Some ps -> ps
       | None ->
           failwith (Printf.sprintf
                       "codegen: PUT LIST decimal item on non-decimal \
                        variable %s [TBD]" n.Ast.orig))
  | Ast.Esuffix (b, _) ->
      (match b.Ast.e with
       | Ast.Eident n ->
           (match List.assoc_opt (String.lowercase_ascii n.Ast.orig) st.procs
            with
            | Some pl ->
                (match pl.Bind.pl_ret with
                 | Some (Bind.RTdec (p, s)) -> (p, s)
                 | _ ->
                     failwith
                       "codegen: PUT LIST item is not a decimal function \
                        [TBD]")
            | None ->
                failwith "codegen: PUT LIST decimal item call unresolved [TBD]")
       | _ -> failwith "codegen: PUT LIST decimal item shape [TBD]")
  | _ ->
      failwith "codegen: PUT LIST decimal editing of this expression is \
                unproven [TBD]"

(* ---- [E2E-7A slice 2] DECIMAL value model ---------------------------
   A value on DR's decimal stack carries (p = digits, s = scale).  dv_of
   computes that descriptor WITHOUT emitting anything; dpush emits the
   instruction sequence the descriptor implies, so the LAWS live in exactly
   one place and the emitter cannot drift from them.

   * QDDSL / QDDSR shift the CURRENT TOP OF STACK, and their POSITION in
     the sequence identifies which value is being shifted: between the two
     operand pushes it is the first-pushed operand, after both pushes it is
     the second-pushed one.  That is what makes the pair readable:
        a(9,2)+b(6,4): push a, QDDSL 2, push b, DADOP, QDDSR 2   [R705]
        a(9,4)+b(6,2): push a, push b, QDDSL 2, DADOP            [R707]
        e(9,2)-f(6,4): push e, QDDSL 2, push f, DSUOP, QDDSR 2   [R715]
        a(9,2)>e(6,4): push e, push a, QDDSL 2, DCMOP            [R723]
   * +/- and compare ALIGN to max(s_l,s_r) by shifting the SHORTER operand
     up; equal scales emit nothing [R505, LOAN1 `p = p - pmt`].  R715 pins
     both directions for subtraction, so the law is evidenced for - and not
     merely inherited from +.
   * * needs NO alignment: result scale = s_l + s_r [R711 `d = a*b` into
     dec(9,4) emits no shift whatsoever; R719/R720 product scale 4 into a
     dec(9,2) target gets QDDSR 2].
   * / pre-shifts the DIVIDEND up by N = 15 - p_dividend (omitted when the
     dividend already has 15 digits) so the quotient is computed at 15
     working digits; quotient scale = s_l + N - s_r, or s_l - s_r when
     N = 0.  Evidence: R512/R701/R703/R708 (p=9 -> 6), R710 (p=11 -> 4, so
     N is not a constant), R702 (dividend dec(9,2) with a dec(13,2) TARGET
     still gets 6, so N tracks the DIVIDEND, not the target), R714 (N=5 ->
     add-result precision 10), R717 (N=8 -> 7), R718 (N=4 -> mul 11; N=9 ->
     sub 6), LOAN1/R704 (dividend is a 15-digit product -> N=0 -> no pair).
     Division TRUNCATES: R706 ran 2/3 -> 0.66 and 9/2 into dec(9,0) -> 4.
   * the CONSUMER fixes a value's scale: DOWN with QDDSR, UP with QDDSL.
     store/return target [R701 down 4, R713 down 2, R716 UP 2 to dec(13,8),
     R711 UP 2 for an add into dec(9,4), R505 down 2 after a multiply]; an
     enclosing +/- aligns instead and adds no fix, so a quotient carries its
     scale straight in [R721, R722].
   * result precision is observable ONLY through the next division's N:
        add/sub: min(p_l,p_r)+1     [R714, R717, R718]
        mul:     min(15,p_l+p_r+1)  [R718, LOAN1/R704 via N=0]
        div:     UNPINNED -- no sample exposes a quotient's precision, so a
                 quotient used where p is required refuses [TBD].
   * push order: the RIGHT operand is pushed first iff it is compound and
     the left is simple [DFACT `decimal(i,15) * factorial(i-1)`, R704,
     R719, R722]; otherwise LEFT first -- both compound [R720, R724] and
     both simple [R505, R705, R707] included.  Division always pushes the
     dividend first, even against a compound divisor [R712], because the N
     pre-shift has to act on the dividend while it is still the top.
   * integer literals: additive/compare positions align to the DEC partner
     [R608, R507/R607]; multiplicative positions take their own digit count
     with scale 0 [R509 *2 A=01, R511 *1234 A=04, R512/R703/R710 /2 /8 A=01,
     LOAN1 /1200 A=04]; store/return positions take the target (p,s) [C084].
*)
type dv = { pv : int option; sc : int }

type dctx =
  { c_tgt : (int * int) option   (* store/RETURN target: fixes the scale *)
  ; c_lit : (int * int) option   (* DEC partner of an additive/compare literal *)
  ; c_mult : bool                (* multiplicative operand position *)
  ; c_round : bool }             (* [slice 3] argument of a ROUND [R811] *)

let dsl st n = d st op_mvi_a; d st n; call_ext st "?QDDSL"
let dsr st n = d st op_mvi_a; d st n; call_ext st "?QDDSR"

(* an operand that costs more than one decimal-stack emission.  [E2E-7A
   slice 3] ROUND joins it: LOAN1 and R807 both push `X + round(a/b,n)` with
   the round SUBTREE FIRST even though it sits on the right, which is exactly
   the right-compound/left-simple rule L7 -- so a round node with a compound
   argument behaves like a compound operand.  A round node whose argument is
   SIMPLE is NOT claimed to be compound: no sample shows which side DR pushes
   first for `p + round(a,2)`, and that shape refuses in dpush. *)
let dcompound _st (e : Ast.expr) =
  match (unwrap_e e).Ast.e with
  | Ast.Ebinary _ | Ast.Esuffix _ -> true
  | Ast.Ebuilt ("ROUND", [ a; _ ]) ->
      (match (unwrap_e a).Ast.e with Ast.Ebinary _ -> true | _ -> false)
  | _ -> false

(* the (p,s) an additive/compare integer literal aligns to: only a DEC
   variable or a DEC function call is evidenced [R608, R507/R607] *)
let dpartner st (e : Ast.expr) : (int * int) option =
  match (unwrap_e e).Ast.e with
  | Ast.Eident n -> vk_dec_opt st n
  | Ast.Esuffix _ -> Some (dec_edit_pt st e)
  | _ -> None

let nop_cx = { c_tgt = None; c_lit = None; c_mult = false; c_round = false }
let round_arg_cx = { c_tgt = None; c_lit = None; c_mult = false; c_round = true }

(* ------------------------------------------------------------------ *
 * ROUND(expr, n)  ->  MVI A, k ; CALL ?DROUN        [E2E-7A slice 3]  *
 *                                                                    *
 * DR's convention, from R801-R812 + LOAN1:                           *
 *   the rounded value stays ON TOP of the decimal stack; ?DROUN takes *
 *   ONE byte argument, k = (scale of the entry) - n, i.e. the number  *
 *   of fractional digits to drop, NOT the target scale n.  Observed   *
 *   bytes: dec(9,3) round 2 -> A=01 [R801/R802/R803]; 2/3 at scale 6  *
 *   round 2 -> A=04 [R804/R807]; LOAN1 product+divide at scale 4      *
 *   round 2 -> A=02; dec(9,3) round 0 -> A=03 [R806]; nested          *
 *   round(round(a,3),2) -> A=00 then A=01 [R811] (k=0 IS emitted, it   *
 *   is not elided the way the divide pre-shift is at N=0).            *
 *   The entry KEEPS its scale: after DROUN the consumer fix and the   *
 *   enclosing +/- alignment are computed from the ORIGINAL scale,      *
 *   which is what makes R801's `MVI A,02; CALL ?QDDSR`, R807's         *
 *   `QDDSL 4` before DADOP and LOAN1's `QDDSL 2`/`QDDSR 2` all follow  *
 *   laws L1/L5 already banked in C086 -- ROUND adds no shift of its    *
 *   own.  Rounding is HALF-UP and away from zero (DR runtime: 2.125 -> *
 *   2.13, 2.135 -> 2.14, 2.145 -> 2.15, 2.155 -> 2.16, -2.125 ->       *
 *   -2.13, 2.5 -> 3), and it sees the PRE-STORE stack value, not a     *
 *   truncated copy (R804 prints 0.67 next to x = 2/3's stored 0.66).   *
 *   My compiler emits bytes only -- the arithmetic is DR's ?DROUN --   *
 *   so the mode is evidence for the model, not a rule I implement.     *
 * ------------------------------------------------------------------ *)
let round_split args =
  match args with
  | [ x; nn ] -> (unwrap_e x, nn)
  | [ _ ] ->
      failwith
        "codegen: one-argument ROUND is unproven [TBD] (DR rejects `y = round(a);` \
         itself, with pass-2 `SYNTAX ?` and no .REL [R808])"
  | _ -> failwith "codegen: ROUND arity [TBD]"

let round_n nn =
  match (unwrap_e nn).Ast.e with
  | Ast.Enumber k ->
      let (v, _own, lsc) = dec_lit_value k in
      if lsc <> 0 then
        failwith "codegen: ROUND with a fractional digit count [TBD]";
      if v < 0 then failwith "codegen: ROUND with a negative digit count [TBD]";
      v
  | _ ->
      failwith
        "codegen: ROUND whose digit count is not an integer literal is unproven \
         [TBD] (DR computes it at RUNTIME as LHLD/MOV A,L/SUI 04/CMA [R812]; \
         the static form is the only one LOAN1 needs)"

(* validate the ROUND shape and return (n, argument descriptor) *)
(* everything about a ROUND node that needs no value descriptor: arity, the
   digit-count literal, and the argument shape.  The scale-vs-n check lives
   in dv_of, which is the only place that can see the entry scale. *)
let round_shape st args =
  let (x, nn) = round_split args in
  let n = round_n nn in
  begin
    match (unwrap_e x).Ast.e with
    | Ast.Eident n ->
        (match vk_dec_opt st n with
         | Some _ -> ()
         | None ->
             failwith
               "codegen: ROUND of a non-DECIMAL (integer) argument is unproven \
                [TBD] (DR rounds the INTEGER with a separate route, ?IROUN, \
                then converts via ?QI15D and emits NO ?DROUN at all [R810]; \
                LOAN1 never rounds an integer expression)")
    | Ast.Ebinary _ | Ast.Esuffix _ | Ast.Ebuilt ("ROUND", _) -> ()
    | Ast.Enumber _ ->
        failwith
          "codegen: ROUND of a bare literal is unproven [TBD] (R809 shows DR \
           pushing the literal with its OWN digit count AND own scale, \
           A=04 for 2.125 -- a third literal role with one sample only)"
    | _ ->
        failwith
          "codegen: ROUND of a non-decimal argument is unproven [TBD] (an \
           INTEGER argument takes DR's separate ?IROUN route, then ?QI15D \
           with no ?DROUN at all [R810])"
  end;
  (x, n)

(* context for a BINARY operand: a direct integer literal takes its
   partner's precision in an additive/compare position and its own digit
   count in a multiplicative one; anything else inherits nothing *)
let dchild_cx _st op partner x =
  match op with
  | Ast.Mul | Ast.Div ->
      { c_tgt = None; c_lit = None; c_mult = true; c_round = false }
  | _ ->
      (match (unwrap_e x).Ast.e with
       | Ast.Enumber _ ->
           { c_tgt = None; c_lit = partner; c_mult = false; c_round = false }
       | _ -> nop_cx)

let rec dv_of st (cx : dctx) (e : Ast.expr) : dv =
  match (unwrap_e e).Ast.e with
  | Ast.Eident n ->
      (match vk_dec_opt st n with
       | Some (p, s) -> { pv = Some p; sc = s }
       | None ->
           failwith
             (Printf.sprintf
                "codegen: decimal operation on non-decimal operand %s [TBD]"
                n.Ast.orig))
  | Ast.Ebuilt ("DECIMAL", _) ->
      (* decimal(x,p): the precision ARGUMENT is ignored [R506], so the
         result descriptor comes from context, exactly as in C084 *)
      (match cx.c_tgt with
       | Some (p, s) -> { pv = Some p; sc = s }
       | None -> { pv = Some 15; sc = 0 })
  | Ast.Ebuilt ("ROUND", args) ->
      let (x, n) = round_shape st args in
      let da = dv_of st round_arg_cx x in
      if da.sc < n then
        failwith
          "codegen: ROUND with a digit count ABOVE the operand scale is \
           unproven [TBD] (R805: dec(9,3) round 5 makes DR emit the WRAPPED \
           byte 3-5 = 0xFE; the value came back unchanged, but one sample \
           does not pin the rule and LOAN1 never asks for it)";
      (* SCALE AND PRECISION ARE RETAINED: R801/R804/R807 show the consumer
         fix and the enclosing +/- alignment still computed from the operand's
         original scale after DROUN.  pv is inherited; nothing exposes a
         rounded value's precision, so a ROUND result used where p matters
         refuses below (same family as the quotient-precision gap). *)
      { pv = da.pv; sc = da.sc }
  | Ast.Esuffix _ ->
      let (p, s) = dec_edit_pt st e in
      { pv = Some p; sc = s }
  | Ast.Enumber k ->
      let (_v, own, lsc) = dec_lit_value k in
      (match cx.c_tgt, cx.c_lit with
       | Some (tp, ts), _ -> { pv = Some tp; sc = ts }
       | None, Some (pp, ps) ->
           if lsc > 0 then
             failwith
               "codegen: fractional DEC literal aligned to a decimal partner \
                [TBD] (only an integral literal is pinned in additive or \
                compare position [R608/R507])";
           { pv = Some pp; sc = ps }
       | None, None ->
           if lsc > 0 then
             failwith
               "codegen: fractional DEC literal in multiplicative operand \
                position [TBD]";
           { pv = Some own; sc = 0 })
  | Ast.Ebinary (op, l, r) ->
      let cl = dchild_cx st op (dpartner st r) l in
      let cr = dchild_cx st op (dpartner st l) r in
      let dl = dv_of st cl l and dr = dv_of st cr r in
      begin
        match op with
        | Ast.Add | Ast.Sub ->
          { pv =
              (match (dl.pv, dr.pv) with
               | Some a, Some b -> Some (min 15 (1 + min a b))
               | _ -> None);
            sc = max dl.sc dr.sc }
        | Ast.Mul ->
            { pv =
                (match (dl.pv, dr.pv) with
                 | Some a, Some b -> Some (min 15 (a + b + 1))
                 | _ -> None);
              sc = dl.sc + dr.sc }
        | Ast.Div ->
          (match (unwrap_e l).Ast.e with
           | Ast.Ebuilt ("ROUND", _) ->
               failwith
                 "codegen: ROUND result as a DECIMAL divide dividend is unproven \
                  [TBD] (the pre-shift wants 15 - p of the ROUNDED entry; no \
                  sample shows what p a rounded value carries)"
           | _ -> ());
          let n =
            match dl.pv with
            | Some p -> 15 - p
            | None ->
                failwith
                  "codegen: DECIMAL divide with an unpinned dividend \
                   precision [TBD] (a quotient's precision is not \
                   observable in any sample)"
          in
          let sc = if n > 0 then dl.sc + n - dr.sc else dl.sc - dr.sc in
          if sc < 0 then
            failwith
              "codegen: DECIMAL divide yielding a negative scale [TBD] \
               (no sample puts more fractional digits in the divisor than \
               in the dividend)";
          { pv = None; sc }
        | _ ->
            failwith
              "codegen: decimal operator not in the DEC subset [TBD] \
               (mod/exp/shift on the decimal stack are unpinned)"
      end
  | _ ->
      failwith
        (Printf.sprintf "codegen: decimal expression shape %s not in the DEC \
                         subset [TBD]" (expr_kind_name (unwrap_e e).Ast.e))

(* push one DEC value; emits exactly what dv_of says the descriptor needs *)
let rec dpush st (cx : dctx) (e : Ast.expr) : dv =
  let vd = dv_of st cx e in
  match (unwrap_e e).Ast.e with
  (* [E2E-7A slice 3] ROUND must NOT be swallowed by the simple-operand arm:
     it pushes its argument, then ?DROUN, then takes the ordinary consumer
     fix.  Unknown builtins never reach here anyway -- dv_of, which runs
     first, refuses them. *)
  | Ast.Eident _ | Ast.Ebuilt ("DECIMAL", _) | Ast.Esuffix _ | Ast.Enumber _ ->
      dpush_simple st cx e vd;
      (match cx.c_tgt with
       (* A simple operand whose own scale differs from the store target is
          UNPROVEN: every sample that needed a scale fix had a computed
          value [R711, R713, R716], and LOAN1's `PMT = P` crosses
          PRECISIONS but not scales, which ?DSTOP's A argument already
          covers.  Refuse rather than assume DSTOP rescales. *)
       | Some (_, ts) when ts <> vd.sc ->
           failwith
             "codegen: DECIMAL assignment between differing scales is \
              unproven [TBD] (only computed results are pinned as needing a \
              QDDSL/QDDSR fix; a direct DEC operand store always had equal \
              scales in the samples)"
       | _ -> ());
      vd
  | Ast.Ebinary (op, l, r) ->
      let cl = dchild_cx st op (dpartner st r) l in
      let cr = dchild_cx st op (dpartner st l) r in
      begin
        match op with
        | Ast.Div ->
            (match (unwrap_e l).Ast.e with
             | Ast.Enumber _ ->
                 failwith
                   "codegen: DECIMAL divide with a literal dividend is \
                    unproven [TBD] (every sample divides a variable, a call \
                    result or a computed value)"
             | _ -> ());
            (match (unwrap_e r).Ast.e with
             | Ast.Ebuilt ("ROUND", _) ->
                 failwith
                   "codegen: ROUND result as a DECIMAL divide divisor is unproven \
                    [TBD] (only `a / b` operands are sampled)"
             | _ -> ());
            ignore (dpush st cl l);
            let n =
              match (dv_of st cl l).pv with
              | Some p -> 15 - p
              | None ->
                  failwith
                    "codegen: DECIMAL divide with an unpinned dividend \
                     precision [TBD]"
            in
            if n > 0 then dsl st n;
            ignore (dpush st cr r);
            call_ext st "?DDVOP"
        | (Ast.Add | Ast.Sub | Ast.Mul) as opn ->
            let align =
              match opn with Ast.Mul -> false | _ -> true
            in
            let rf = dcompound st r && not (dcompound st l) in
            let (ef, ex, cxf, cxo, df, dx) =
              if rf
              then (r, l, cr, cl, dv_of st cr r, dv_of st cl l)
              else (l, r, cl, cr, dv_of st cl l, dv_of st cr r)
            in
            ignore (dpush st cxf ef);
            if align && df.sc < dx.sc then dsl st (dx.sc - df.sc);
            ignore (dpush st cxo ex);
            if align && dx.sc < df.sc then dsl st (df.sc - dx.sc);
            call_ext st
              (match opn with
               | Ast.Add -> "?DADOP"
               | Ast.Sub -> "?DSUOP"
               | _ -> "?DMUOP")
        | _ ->
            failwith
              "codegen: decimal operator not in the DEC subset [TBD] \
               (mod/exp/shift on the decimal stack are unpinned)"
      end;
      (* the consumer fixes the scale of a COMPUTED value [R701, R711,
         R713, R716, R721, R722]; an enclosing +/- aligns its operands
         instead, so an operand-context value gets no fix here *)
      (match cx.c_tgt with
       | Some (_, ts) when ts > vd.sc -> dsl st (ts - vd.sc)
       | Some (_, ts) when ts < vd.sc -> dsr st (vd.sc - ts)
       | _ -> ());
      vd
  | Ast.Ebuilt ("ROUND", args) ->
      let (x, n) = round_shape st args in
      (* position legality, from the samples that exist: whole-RHS / return
         [R801-R806, R811] and an additive operand whose argument is COMPOUND
         [R807, LOAN1].  A simple-argument round on either side of +/- has no
         push-order sample, and one in a multiplicative position has none
         either. *)
      begin
        match cx with
        | { c_tgt = Some _; _ } -> ()
        | { c_round = true; _ } -> ()   (* nested round [R811] *)
        | { c_mult = true; _ } ->
            failwith
              "codegen: ROUND in a multiplicative DECIMAL position is unproven \
               [TBD] (no sample multiplies or divides by a rounded value)"
        | _ ->
            if not (dcompound st e) then
              failwith
                "codegen: ROUND with a SIMPLE argument inside +/- is unproven \
                 [TBD] (R807/LOAN1 pin the order only when the rounded \
                 subtree is compound, so which side DR pushes first here is \
                 unknown)"
      end;
      ignore (dpush st round_arg_cx x);
      d st op_mvi_a;
      d st (vd.sc - n);
      call_ext st "?DROUN";
      (* the rounded entry keeps its scale, so the SAME consumer rule as any
         other computed value decides the shift afterwards [R801, R804, R806] *)
      (match cx.c_tgt with
       | Some (_, ts) when ts > vd.sc -> dsl st (ts - vd.sc)
       | Some (_, ts) when ts < vd.sc -> dsr st (vd.sc - ts)
       | _ -> ());
      vd
  | _ ->
      failwith
        (Printf.sprintf "codegen: decimal push of expression shape %s is not \
                         in the DEC subset [TBD]"
           (expr_kind_name (unwrap_e e).Ast.e))
and dpush_simple st (_cx : dctx) (e : Ast.expr) (vd : dv) =
  match (unwrap_e e).Ast.e with
  | Ast.Eident n ->
      let p = Option.get vd.pv in
      (* a DEC FORMAL is a by-reference pointer cell, so the address must be
         LOADED, not used inline [DECPOLY @10D-112, R709/R725] *)
      if List.mem (String.lowercase_ascii n.Ast.orig) st.deref then
        d st op_lhld
      else
        d st op_lxi_h;
      reloc st Data (addr_of st n.Ast.orig);
      d st op_mvi_a; d st p; call_ext st "?DLDOP"
  | Ast.Ebuilt ("DECIMAL", args) ->
      (match args with
       | [ x ] | [ x; _ ] -> lower_hl st x; call_ext st "?QI15D"
       | _ -> failwith "codegen: DECIMAL builtin arity [TBD]")
  | Ast.Esuffix _ -> lower_hl st e
  | Ast.Enumber k ->
      let (p, sc) = (Option.get vd.pv, vd.sc) in
      let addr = dec_pool st ~prec:p ~scale:sc ~text:k in
      d st op_lxi_h; reloc st Data addr;
      d st op_mvi_a; d st p; call_ext st "?DLDOP"
  | _ ->
      failwith
        (Printf.sprintf "codegen: decimal push of this operand shape is not \
                         in the DEC subset [TBD] (%s)"
           (expr_kind_name (unwrap_e e).Ast.e))

(* compatibility wrapper used by the store/PUT/compare paths *)
let dec_push st (tgt : (int * int) option) (e : Ast.expr) : int * int =
  let d =
    dpush st { c_tgt = tgt; c_lit = None; c_mult = false; c_round = false } e
  in
  (match d.pv with Some p -> (p, d.sc) | None -> (0, d.sc))

(* ---- [E2E-7A slice 1] helpers for DECIMAL comparison -------------- *)
(* unwrap_e is defined with the DECIMAL value model above *)
(* a comparison operand is DEC-typed if it is a DEC variable or a DEC
   function call [R601-R606 var/var, LOAN1 P<PMT]; decimal(x,p) in a
   relation is NOT pinned, so it stays refused *)
let is_dec_operand st (e : Ast.expr) =
  match (unwrap_e e).Ast.e with
  | Ast.Eident n -> vk_dec_opt st n <> None
  | Ast.Esuffix (b, _) ->
      (match b.Ast.e with
       | Ast.Eident n ->
           (match List.assoc_opt (String.lowercase_ascii n.Ast.orig) st.procs
            with
            | Some pl ->
                (match pl.Bind.pl_ret with Some (Bind.RTdec (_, _)) -> true
                 | _ -> false)
            | None -> false)
       | _ -> false)
  | _ -> false

let dec_pt_of st (e : Ast.expr) =
  match (unwrap_e e).Ast.e with
  | Ast.Eident n -> vk_dec_opt st n
  | Ast.Esuffix (b, _) ->
      (match b.Ast.e with
       | Ast.Eident n ->
           (match List.assoc_opt (String.lowercase_ascii n.Ast.orig) st.procs
            with
            | Some pl ->
                (match pl.Bind.pl_ret with
                 | Some (Bind.RTdec (p, q)) -> Some (p, q)
                 | _ -> None)
            | None -> None)
       | _ -> None)
  | _ -> None

(* precision/scale each side is pushed with.  A plain integer literal on
   one side becomes a DEC pool cell taking the OTHER operand's precision
   [R507/R607: `0` pushed as MVI A,09 against a dec(9,2) variable], and
   LOAN1 needs exactly `P > 0` with p = dec(11,2) [6-byte cell S(001E)].
   Where BOTH operands are decimal, a literal has no "other side" to take
   precision from, and `p > 3` against a dec(9,2) variable is refused:
   the two candidate encodings (0 vs 300, i.e. scale 0 vs 2) are not
   distinguished by any existing sample. *)
let dec_cmp_pt st (a : Ast.expr) (b : Ast.expr) =
  let la = match (unwrap_e a).Ast.e with Ast.Enumber k -> Some k | _ -> None in
  let lb = match (unwrap_e b).Ast.e with Ast.Enumber k -> Some k | _ -> None in
  let da = dec_pt_of st a and db = dec_pt_of st b in
  match da, db, la, lb with
  | Some (pa, sa), Some (pb, sb), None, None ->
      ((pa, sa, None), (pb, sb, None))
  | Some (pa, sa), None, None, Some kb ->
      ((pa, sa, None), (pa, sa, Some kb))
  | None, Some (pb, sb), Some ka, None ->
      ((pb, sb, Some ka), (pb, sb, None))
  | _ ->
      failwith
        "codegen: decimal comparison operands not in the proven DEC subset \
         [TBD] (DEC variable / DEC-function call / integer-0 literal only; \
         decimal(x,p) in a relation is unpinned, and a scale-carrying \
         literal against a scaled variable is unproven)"

(* push one comparison operand: decimal operands go through dec_push; a
   literal is pre-scaled to the other side's precision, with the scale
   restriction above. *)
let dec_cmp_push st (e : Ast.expr) ((p, s, lit) : int * int * string option) =
  match lit with
  | Some k ->
      let (v, _own, lsc) = dec_lit_value k in
      if not (lsc = 0 && (s = 0 || v = 0)) then
        failwith
          "codegen: decimal comparison literal scale unproven [TBD] (only an \
           integral literal, or any literal equal to 0, is pinned against a \
           scaled decimal operand [R507/R607 use 0])";
      ignore (dec_push st (Some (p, s)) (unwrap_e e))
  | None -> ignore (dec_push st None e)

(* emit a FIXED DECIMAL relation: the push pair (order fixed by the
   relation [C085]), any scale alignment [R723], then ?DCMOP.  Returns the
   SKIP-jump opcode that encodes the relation, so both the single-condition
   arm (backpatch a jump) and the conjunction arm (materialize a boolean
   byte) share ONE lowering of the relation. *)
let dec_cmp_rel st (rop : Ast.relop) (a : Ast.expr) (b : Ast.expr) =
  let (pa, pb) = dec_cmp_pt st a b in
  let (right_first, opc) =
    match rop with
    | Ast.Gt -> (true, op_jp)   | Ast.Lt -> (false, op_jp)
    | Ast.Ge -> (false, op_jm)  | Ast.Le -> (true, op_jm)
    | Ast.Eq -> (false, op_jnz) | Ast.Ne -> (false, 0xca)
  in
  if right_first
  then (dec_cmp_push st b pb; dec_cmp_push st a pa)
  else (dec_cmp_push st a pa; dec_cmp_push st b pb);
  (* [R723] the SAME alignment law +/- use applies to a relation: when
     the two operands have different scales DR shifts the SHORTER one
     up to the longer before ?DCMOP.  Because the relation fixes the
     push order [C085], only the case where the TOP (second-pushed)
     operand is the short one is reachable with a proven mechanism --
     QDDSL acts on the top of the stack, and shifting the DEEPER value
     would need a pop-and-restore sequence no sample shows, so that
     shape refuses rather than guessing. *)
  let sc_of (_, x, _) = x in
  let (s_top, s_deep) =
    if right_first then (sc_of pa, sc_of pb) else (sc_of pb, sc_of pa)
  in
  if s_top < s_deep then dsl st (s_deep - s_top)
  else if s_deep < s_top then
    failwith
      ("codegen: decimal comparison alignment on the deeper operand is " ^
       "unproven [TBD] (DR aligns by shifting the TOP of the decimal stack " ^
       "up [R723]; the relation fixes the push order, so this pair would " ^
       "need the lower value shifted)");
  call_ext st "?DCMOP";
  opc

(* ---------- [&] AND-conjunction [E2E-9 slice 6] ----------
   Inside a conjunction DR does NOT emit a per-operand skip jump.  Each
   operand is materialized as a boolean BYTE in A through the flag trick
   `SUI 01 / SBB A` (A := 0FF iff the relation holds, 00 otherwise), the
   operands are combined with `PUSH PSW ... POP B / ANA B` (0FF AND 0FF is
   0FF, so AND-ing on those values IS logical AND), and the WHOLE
   conjunction gets one skip jump, opcode JP (F2): A=0FF -> S=1 -> fall into
   the THEN; A=00 -> S=0 -> skip it.  Left-associative `&` nesting maps onto
   nested PUSH/POP pairs, so `a & b & c` lowers as
     a; PUSH PSW; b; POP B; ANA B; PUSH PSW; c; POP B; ANA B; JP skip
   [DECPOLY `if x=0 & y=0 & z=0`, R2021 fixed-bin `x=0 & y=0`].

   Only the two operand shapes those goldens pin are implemented: a FIXED
   DECIMAL equality (?DLDOP push pair + ?DCMOP) and a 2-byte FIXED BINARY
   compare against 0 (cell-OR test).  Other relations in a conjunction
   refuse [TBD]: DR's boolean-materialization ladder for >, <, >=, <=, ^=
   is unsampled. *)
let vk_name (vk : vkind) : string =
  match vk with
  | Vint -> "fixed-binary" | Vfix n -> "char(" ^ string_of_int n ^ ")"
  | Vvar n -> "varying(" ^ string_of_int n ^ ")"
  | Vdec (p, s) -> "dec(" ^ string_of_int p ^ "," ^ string_of_int s ^ ")"
  | Vflt -> "float"

(* ==================================================================
   [E2E-10 step 2] FLOAT BINARY(24): value model + operand-mode lowering.

   Representation (C100, every byte observed in golden/e2e13): 4 bytes,
       b0 = fraction bits 7..0,  b1 = 15..8,  b2 = sign<<7 | bits 22..16,
       b3 = characteristic (bias 129), value = (-1)^s (1+frac/2^23) 2^(b3-129)
   with an IMPLIED leading one (24 significant bits, which is what
   `float binary(24)` names), zero = all four bytes 0 (no negative zero
   [R3007]), literal rounding nearest with TIES AWAY FROM ZERO [R3020],
   magnitude range 2^-129 .. 2^127 exclusive of the top [R3019/R3024 vs
   R3015-R3017/R3025], and pool cells deduplicated by identical bytes,
   allocated in first-use order ahead of the variables (C101 -- the same
   rules the DEC pool follows).  tools/floatmodel.py is the INDEPENDENT
   oracle for this encoder: it reproduces 60/60 DR literal cells
   byte-exactly, and the e2e gate checks this OCaml path against the
   same cells.

   Operand modes (C102).  The suffix tells the runtime where the operands
   live; it comes from DR traces, not from the DEC analogue:
     mem,mem      LXI H,l / PUSH H / LXI H,r / POP D / CALL ?FX44M   [R3030]
     deref,deref  LHLD c1 / PUSH H / LHLD c2 / POP D / CALL ?FX44M   [R3038]
     stack,mem    LXI H,r / CALL ?FX44L                              [R3030]
     stack,deref  LHLD r  / CALL ?FX44L                              [R3038]
     mem,stack    LXI H,l / CALL ?FX44R                              [R3036/42]
     stack,stack  CALL ?FX44S                                        [R3034]
   where F is followed by A(plus), S(sub), M(mul) or D(iv) and X44 is the
   fixed 44 in those names.  ?FX44R exists because DR preserves operand
   ORDER when the left side is a plain cell and the right side is computed:
   `d1 = a - b * c` is FM44M over b,c then `LXI H,A / FS44R`, i.e. a minus
   the product, so L means (accumulator op cell) and R means (cell op
   accumulator).  DR is semantically CORRECT there, which is precisely why
   I probed instead of assuming from the DEC path [R3042].
   Every form leaves its result on DR's float stack; a store pops it with
   ?FX44S (a stack/cell transfer with HL = the cell), plain cell-to-cell
   copies use ?FX44M [R3001, R3037].  Unary minus is ?FN40M for a memory
   operand and ?FN40S for a stack operand [R3035, R3046].  A FIXED operand
   inside a float expression is evaluated to HL then converted with
   ?QI15F [R3036].  A float function exits through JMP ?FPRET, plus ?RSBLK
   when the activation is recursive [R3038 non-recursive vs FFACT
   recursive].  PUT of a float variable is MVI A,0E / ?QFCMS and of a stack
   value MVI A,0E / ?QFCSS -- the width byte is the CONSTANT 14, not a
   precision [R3030, R3037, FFACT].

   REFUSED on purpose, because no DR sample decides them: float comparison
   (the JP/JM/JZ pairing of `>` in R3037/R3045 implies `>=`, the same
   C083-style irregularity that needed a RUNTIME probe to settle for DEC),
   GET of a float (observed in R3004, unimplemented), float-to-fixed store
   (?FL40M / ?QFI15 appear only inside FFACT's prologue), storing to or
   bare-returning a float FORMAL, mixed cell/deref operand pairs, float
   binary(p) with p different from 24, whole-literal float expressions (DR
   evaluates those in the DEC runtime and converts with ?QX8F4 [R3044]),
   and literals outside the characterized range -- including the exact
   2^-129 magnitude, whose encoding collides with DR's zero cell.
   ================================================================== *)


(* --- expression lowering --------------------------------------------- *)
type fmode =
  | Fmem of int     (* address of a 4-byte float cell *)
  | Fderef of int   (* address of a pointer cell holding that address *)
  | Fstack          (* the value sits on DR's float stack *)
  | Fbin of string  (* accumulator holds the result of a binary FLOAT op; the
                       string is the op letter (A/S/M/D), kept only to name the
                       evidence in refusals *)
  | Fconv           (* accumulator holds a ?QI15F conversion result *)
  | Fneg            (* accumulator holds a ?FN40M / ?FN40S negation result *)

let fl_addr st (m : fmode) =
  match m with
  | Fmem a -> d st op_lxi_h; reloc st Data a
  | Fderef a -> d st op_lhld; reloc st Data a
  | (Fstack | Fconv | Fbin _ | Fneg) ->
      failwith "codegen: internal: computed float operand has no address"

let fl_proc_ret st (nm : string) =
  match List.assoc_opt (String.lowercase_ascii nm) st.procs with
  | Some pl -> pl.Bind.pl_ret
  | None -> None

let rec is_float_expr st (e : Ast.expr) : bool =
  let e = unwrap_e e in
  match e.Ast.e with
  | Ast.Eident n -> vk_of st n.Ast.orig = Vflt
  | Ast.Ebinary (_, l, r) -> is_float_expr st l || is_float_expr st r
  | Ast.Eprefix (_, x) -> is_float_expr st x
  | Ast.Econd inner -> is_float_expr st inner
  | Ast.Esuffix (hd, args) when args <> [] ->
      (match hd.Ast.e with
       | Ast.Eident n ->
           (match fl_proc_ret st n.Ast.orig with
            | Some (Bind.RTfloat _) -> true
            | _ -> false)
       | _ -> false)
  | _ -> false

and fl_push st (e0 : Ast.expr) : fmode =
  let e = unwrap_e e0 in
  match e.Ast.e with
  | Ast.Ebinary (op, l, r) -> fl_bin st op l r
  | Ast.Enumber k ->
      (* an integer or decimal literal in a FLOAT context becomes a float
         pool cell: `d7 = a * 2` [R3036] and FFACT's `return (1)` *)
      let b =
        try mbf_encode k with Fl_range msg ->
          failwith ("codegen: float literal " ^ k ^ " " ^ msg)
      in
      Fmem (fl_pool st b)
  | Ast.Eident n ->
      let nm = String.lowercase_ascii n.Ast.orig in
      begin match vk_of st n.Ast.orig with
      | Vflt ->
          if List.mem nm st.deref then Fderef (addr_of st n.Ast.orig)
          else Fmem (addr_of st n.Ast.orig)
      | Vint ->
          (* fixed operand inside a float expression: evaluate to HL, then
             ?QI15F converts it into the accumulator [R3036].  The result is
             Fconv, NOT Fstack: DR's suffix choice separates a conversion from
             a binary-op result (`a + i` -> ?FA44R vs `a + (b+c)` -> ?FA44L
             [R3036, R3052]), and a negation may only be applied to a binary
             result [R3035, R3038, R3046], never to a conversion. *)
          lower_hl st e;
          call_ext st "?QI15F";
          Fconv
      | vk ->
          failwith
            (Printf.sprintf
               "codegen: mixing %s into a FLOAT expression is unsampled [TBD] (no DR sample mixes decimal or character values into one float expression; line %d)"
               (vk_name vk) e.Ast.epos.Source.line)
      end
  | Ast.Eprefix (Ast.Minus, x) -> (
      (* NEGATIVE LITERALS ARE FOLDED, not negated at run time: R3007/R3018/
         R3020 show DR's pool holding `00 00 c0 81` for -1.5 and `01 00 80 99`
         for -16777217, with NO ?FN40M anywhere in those statements.  A minus
         over a COMPUTED value is different and does use ?FN40M / ?FN40S
         [R3035, R3046].  A minus over a parenthesised literal has no sample,
         so it is refused rather than assumed to fold the same way. *)
      match (unwrap_e x).Ast.e with
      | Ast.Enumber k when (match x.Ast.e with Ast.Econd _ -> false
                                   | _ -> true) ->
          let b =
            try mbf_encode ("-" ^ k) with Fl_range msg ->
              failwith ("codegen: float literal -" ^ k ^ " " ^ msg)
          in
          Fmem (fl_pool st b)
      | Ast.Enumber _ ->
          failwith
            "codegen: FLOAT minus over a PARENTHESISED literal is unsampled [TBD] (R3007-R3020 fold a bare literal; `-(1.5)` has no sample)"
      | _ ->
          (match fl_push st x with
           | Fmem a ->
               (* ?FN40M negates the value ADDRESSED BY HL into the accumulator;
                  it does not write the cell.  R3046 reads `a` and `-a` in
                  consecutive statements, so an in-place negate would corrupt
                  the variable -- the DR evidence itself rules that reading out. *)
               d st op_lxi_h; reloc st Data a; call_ext st "?FN40M"; Fneg
           | Fderef a ->
               d st op_lhld; reloc st Data a; call_ext st "?FN40M"; Fneg
           | (Fstack | Fbin _) ->
               (* ?FN40S negates the accumulator in place [R3035 `d4 = -(a+b)`,
                  R3038 `(p+q) * -1`].  The result occupies the same slot as any
                  other negation, so it is Fneg, not Fstack: R3046 shows a
                  negation on either side of `*` taking L/R and two of them
                  taking S. *)
               call_ext st "?FN40S"; Fneg
           | Fconv ->
               failwith
                 "codegen: negating a ?QI15F conversion result inside a FLOAT operand is unsampled [TBD] (R3035/R3038 sample ?FN40S only on an arithmetic result; R3046 samples ?FN40S only after a second ?FN40M)"
           | Fneg ->
               failwith
                 "codegen: DOUBLE negation of a FLOAT value is unsampled [TBD] (no DR sample applies ?FN40S to a ?FN40M/?FN40S result; `-(-a)` and `--a` have no evidence, and a partial match here is how the R3046 operand-mode bug hid)"))
  | Ast.Eprefix (Ast.Plus, x) -> fl_push st x
  | Ast.Econd inner -> fl_push st inner
  | Ast.Eprefix (op, _) ->
      failwith
        (Printf.sprintf "codegen: FLOAT prefix operator %s is unsampled [TBD] (line %d)"
           (if op = Ast.NegL then "^" else "+/-") e.Ast.epos.Source.line)
  | Ast.Esuffix (hd, args) when args <> [] ->
      (* a float function leaves its result on the float stack; the call
         itself is the ordinary descriptor route [R3005, FFACT] *)
      (match hd.Ast.e with
       | Ast.Eident n ->
           (match fl_proc_ret st n.Ast.orig with
            | Some (Bind.RTfloat 24) -> ignore (args); lower_hl st e; Fstack
            | Some (Bind.RTfloat p) ->
                failwith
                  (Printf.sprintf
                     "codegen: FLOAT BINARY(%d) return precision is unsupported [TBD] (only BINARY(24) is characterized; R3013 proves the CELL is 4 bytes but not the computed precision)"
                     p)
            | _ ->
                failwith
                  (Printf.sprintf
                     "codegen: non-float call %s used as a FLOAT operand [TBD] (line %d)"
                     n.Ast.orig e.Ast.epos.Source.line))
       | _ -> failwith "codegen: indirect call target [TBD]")
  | _ ->
      failwith
        (Printf.sprintf
           "codegen: FLOAT expression shape %s is unsampled [TBD] (line %d)"
           (expr_kind_name e.Ast.e) e.Ast.epos.Source.line)

and fl_bin st (op : Ast.binop) (l : Ast.expr) (r : Ast.expr) : fmode =
  (* NOTE (a real byte-level bug I hit here): an UNPARENTHESISED `match` in a
     preceding arm body swallows every following `|` arm, because OCaml has no
     terminator for it.  fl_push's Eprefix arm is parenthesized for that
     reason.  Same family of trap as the DECPOLY `if`/then-branch absorption. *)  let nm =
    match op with
    | Ast.Add -> "A"
    | Ast.Sub -> "S"
    | Ast.Mul -> "M"
    | Ast.Div -> "D"
    | _ ->
        failwith
          "codegen: FLOAT operand of an operator other than + - * / is unsampled [TBD] (no DR sample exponentiates, concatenates, or does bit/logical arithmetic on floats)"
  in
  (* EVALUATION ORDER: when the RIGHT operand is a CALL, DR runs the whole
     right side FIRST and only then materialises the left -- FFACT's
     `i * factorial(i - 1)` is descriptor, CALL, LHLD i, ?QI15F, ?FM44S.
     This is the same rule the FIXED path learned from RFACT/NFACT, and it is
     forced by the stack discipline: the value pushed first ends up deeper, so
     a left operand that needs code would otherwise sit BELOW the call result.
     When the right is not a call, left goes first [R3034 `a * b + c * a`]. *)
  let right_is_call =
    match (unwrap_e r).Ast.e with
    | Ast.Esuffix (hd, args) -> args <> [] &&
        (match hd.Ast.e with Ast.Eident _ -> true | _ -> false)
    | _ -> false
  in
  let (lk, rk) =
    if right_is_call then begin
      let rr = fl_push st r in
      let ll = fl_push st l in
      (ll, rr)
    end
    else begin
      let ll = fl_push st l in
      let rr = fl_push st r in
      (ll, rr)
    end
  in
  (* only these six combinations have a DR sample; the mixed cell/deref
     pairs and a deref left of a stack value do not, so they stay refused
     instead of borrowing the DEC pattern. *)
  (* classify once, then dispatch on the pair -- `as` bindings over
     or-patterns bind to the enclosing tuple, which would misname the
     operands, so no `as` is used here *)
  let cell m = match m with Fmem _ | Fderef _ -> true | _ -> false in
  (* Fneg belongs in this list: R3046 `d1 = -a * b` takes ?FM44L and `d2 = a * -b` takes ?FM44R, so a negation result is a computed accumulator operand, not a cell.  Leaving it out routed both to ?FM44S silently. *)
  let comp m = match m with Fstack | Fconv | Fbin _ | Fneg -> true | _ -> false in
  let deref m = match m with Fderef _ -> true | _ -> false in
  if cell lk && cell rk then begin
    if deref lk <> deref rk then
      failwith
        "codegen: FLOAT operand mixing a plain cell with a pointer formal is unsampled [TBD] (R3030-R3033 pin cell+cell, R3038 pins formal+formal; `q * 1.5` has no sample)";
    fl_addr st lk; d st op_push_h; fl_addr st rk; d st op_pop_d;
    call_ext st ("?F" ^ nm ^ "44M");
    Fbin nm
  end else if comp lk && cell rk then begin
    (* accumulator/pushed value LEFT, named cell right [R3034 `a*b + c`,
       R3035 `-a + b`, R3036 `i + a` / `i * a` / `i / a`, R3042 `a/b * c`,
       R3043 `(a-b)/c`] *)
    fl_addr st rk; call_ext st ("?F" ^ nm ^ "44L"); Fbin nm
  end else if cell lk && comp rk then begin
    if deref lk then
      failwith
        "codegen: FLOAT pointer-formal operand followed by a computed operand is unsampled [TBD] (R3036/R3042/R3051-R3053 sample only the plain-cell left side of the R and L forms)";
    (* L is available only when the operator commutes AND the right value is an
       arithmetic result, i.e. when DR may read the expression with the operands
       exchanged at no cost [R3034, R3051, R3052].  A ?QI15F conversion result
       is NOT that: DR takes R there [R3036 `a + i`, `a * i`, `a / i`], as it
       must for the non-commutative `-` and `/` [R3042, R3043, R3053]. *)
    (* R3046 pins the three computed kinds apart: `-a * b` -> ?FM44L,
       `a * -b` -> ?FM44R, `-(a) * -(b)` -> ?FM44S.  So DR exchanges the
       operands of a commutative op ONLY when the right side is itself a
       binary-op result [R3034 `a + b*c` -> ?FA44L, R3051 `a*(b+c)` -> ?FM44L,
       R3052 `a + (b+c)` -> ?FA44L]; around a negation [R3035 `a + -b` ->
       ?FA44R, R3046 `a * -b` -> ?FM44R] or a conversion [R3036 `a + i` ->
       ?FA44R, `a * i` -> ?FM44R] it keeps the written order, and for the
       non-commutative `-` and `/` it must [R3042, R3043, R3053]. *)
    let use_l =
      match op with
      | Ast.Add | Ast.Mul -> (match rk with Fbin _ -> true | _ -> false)
      | _ -> false
    in
    fl_addr st lk;
    call_ext st ("?F" ^ nm ^ (if use_l then "44L" else "44R"));
    Fbin nm
  end else
    (* both operands computed [R3034 `(a+b)*(a-b)`, R3044 `i + j`] *)
    (call_ext st ("?F" ^ nm ^ "44S"); Fbin nm)

(* store a float value into a variable's cell *)
let fl_store_var st (addr : int) (m : fmode) =
  match m with
  | Fmem a ->
      d st op_lxi_h; reloc st Data a; d st op_push_h;
      d st op_lxi_h; reloc st Data addr; d st op_pop_d;
      call_ext st "?FX44M"
  | (Fstack | Fconv | Fbin _ | Fneg) ->
      (* every computed float kind is popped off the accumulator into the cell
         with ?FX44S [R3030-R3034, and R3035's `d1 = -a` which negates into the
         accumulator with ?FN40M and then stores with ?FX44S] *)
      d st op_lxi_h; reloc st Data addr; call_ext st "?FX44S"
  | Fderef _ ->
      failwith
        "codegen: assigning a FLOAT formal to a variable is unsampled [TBD] (R3037 samples cell-to-cell ?FX44M and stack-to-cell ?FX44S only; reading a float formal inside an expression IS sampled [R3038])"

(* prepare a float value for RETURN: it must end on the float stack.
   A cell is LOADED with ?FL40M -- FFACT's `return (1)` is exactly
   `LXI H,*S(000C); CALL ?FL40M; CALL ?RSBLK; JMP ?FPRET`.  ?FX44S is the
   STORE direction and must not be used here. *)
let fl_return_push st (m : fmode) =
  match m with
  | Fmem a -> d st op_lxi_h; reloc st Data a; call_ext st "?FL40M"
  | (Fstack | Fbin _) -> ()
  | (Fconv | Fneg) ->
      failwith
        "codegen: RETURN of a converted or negated FLOAT value is unsampled [TBD] (FFACT returns a literal via ?FL40M and a product via the stack; R3038 returns a product -- none of them returns a bare ?QI15F or ?FN40 result)"
  | Fderef _ ->
      failwith
        "codegen: RETURN of a bare FLOAT formal is unsampled [TBD] (R3038 returns an expression, FFACT a literal and a product)"

let op_sui = 0xd6
let op_pop_b = 0xc1
let op_ana_b = 0xa0

(* a 2-byte fixed-bin `var = 0` operand, or None *)
let conj_bin_zero st (e : Ast.expr) =
  match (unwrap_e e).Ast.e with
  | Ast.Ebinary (Ast.EqR Ast.Eq, a, { Ast.e = Ast.Enumber "0"; _ })
    when (match (unwrap_e a).Ast.e with
          | Ast.Eident _ -> not (is_dec_operand st a)
          | _ -> false) ->
      (match (unwrap_e a).Ast.e with Ast.Eident v -> Some v | _ -> None)
  | _ -> None

let bin_zero_tail st =
  d st op_mov_a_m; d st op_inx_h; d st op_ora_m;
  d st op_sui; d st 0x01; d st op_sbb_a

(* FIXED DECIMAL equality lowered as a boolean operand, SPLIT into the two
   pieces a conjunction needs.  [R2026/DECPOLY] DR hoists the leading
   `LXI H,<cell>` above the PUSH PSW exactly as it does for a fixed-bin
   operand (PUSH/POP leave HL alone), then emits `MVI A,p / ?DLDOP`, the
   right-hand push, `?DCMOP` and the flag trick.  Only a DEC VARIABLE on the
   left, both sides at the same scale, is pinned; anything else refuses
   rather than guessing an unsampled split. *)
let dec_eq_bool_parts st (a : Ast.expr) (b : Ast.expr) =
  let (pa, pb) = dec_cmp_pt st a b in
  let (ple, sle, lita) = pa in
  let (_plb, slb, _) = pb in
  if sle <> slb then
    failwith
      ("codegen: DEC conjunction scale alignment unproven [TBD] (only " ^
       "equal-scale operand pairs are pinned as boolean operands)");
  match (unwrap_e a).Ast.e, lita with
  | Ast.Eident v, None ->
      if List.mem (String.lowercase_ascii v.Ast.orig) st.deref then
        failwith
          ("codegen: FIXED DECIMAL formal as a conjunction operand is " ^
           "unproven [TBD] (the LXI-H hoist above PUSH PSW is pinned only " ^
           "for automatic decimal cells [DECPOLY, R2026]; a formal's LHLD " ^
           "hoist has no DR sample)");
      let addr = addr_of st v.Ast.orig in
      let pre () = d st op_lxi_h; reloc st Data addr in
      let post () =
        d st op_mvi_a; d st ple; call_ext st "?DLDOP";
        dec_cmp_push st b pb;
        call_ext st "?DCMOP";
        d st op_sui; d st 0x01; d st op_sbb_a
      in
      Some (pre, post)
  | _ -> None

let rec lower_bool st (c : Ast.expr) =
  let c = unwrap_e c in
  match c.Ast.e with
  | Ast.Ebinary (Ast.And, l, r) ->
      lower_bool st l;
      let saved =
        match conj_bin_zero st r with
        | Some v ->
            (* [R2025] fixed-bin operand: address load hoisted above PUSH *)
            d st op_lxi_h; reloc st Data (addr_of st v.Ast.orig);
            d st op_push_psw; bin_zero_tail st
        | None ->
            (match (unwrap_e r).Ast.e with
             | Ast.Ebinary (Ast.EqR Ast.Eq, a, b)
               when is_dec_operand st a || is_dec_operand st b ->
                 (match dec_eq_bool_parts st a b with
                  | Some (pre, post) ->
                      (* [DECPOLY/R2026] DEC operand: same hoist *)
                      pre (); d st op_push_psw; post ()
                  | None ->
                      d st op_push_psw; lower_bool st r)
             | _ -> d st op_push_psw; lower_bool st r)
      in
      ignore saved;
      d st op_pop_b; d st op_ana_b; st.last_imm <- None
  | Ast.Ebinary (Ast.EqR Ast.Eq, a, b) when is_dec_operand st a
                                            || is_dec_operand st b ->
      (* first operand of a conjunction: pre and post run consecutively,
         which is exactly DR's single-condition push pair + flag trick *)
      (match dec_eq_bool_parts st a b with
       | Some (pre, post) -> pre (); post ()
       | None ->
           ignore (dec_cmp_rel st Ast.Eq a b);
           d st op_sui; d st 0x01; d st op_sbb_a)  | Ast.Ebinary (Ast.EqR Ast.Eq, { Ast.e = Ast.Eident v; _ },
                 { Ast.e = Ast.Enumber "0"; _ }) ->
      d st op_lxi_h; reloc st Data (addr_of st v.Ast.orig); bin_zero_tail st
  | _ ->
      failwith
        ("codegen: conjunction operand not in the proven subset [TBD] (only " ^
         "a FIXED DECIMAL `= 0` and a 2-byte FIXED BINARY `= 0` are pinned " ^
         "as boolean-materializing operands [DECPOLY, R2025]; other " ^
         "relations have no DR sample)")

let lower_test_skip0 st (c : Ast.expr) =
  (* [E2E-10] every shape handled below is FIXED or DECIMAL.  A FLOAT
     operand must refuse here: reading `2.5` as an integer constant crashed
     (R3045), and a float variable pair silently took the FIXED compare
     ladder and produced wrong bytes (R3037).  DR's float compare is
     ?FC44M plus JP/JM/JZ [R3037, R3045], and its `>` pairing implies `>=`,
     so it needs a runtime discriminator before it can be implemented. *)
  (if is_float_expr st c then
     failwith
       "codegen: FLOAT comparison in a condition is unsampled [TBD] (DR uses ?FC44M with JP/JM/JZ; R3037/R3045 show `>` guarding the ELSE branch, which implies `>=`, so the flag convention needs a runtime probe -- same shape of problem the DEC path settled at runtime for C083)");
  match c.Ast.e with
  (* a conjunction lowers as ONE boolean expression + ONE skip jump *)
  | Ast.Ebinary (Ast.And, _, _) ->
      lower_bool st c;
      d st op_jp;
      let slot = st.lc in d st 0; d st 0; slot

  (* ---- [E2E-7A slice 1] FIXED DECIMAL comparison --------------------
     ?DCMOP takes NO relation argument: it pops two decimals and leaves a
     three-way result in the 8080 flags, so DR encodes the relation in the
     PUSH ORDER and the choice of skip jump.  Derived from 9 byte-level
     samples [R601-R607, R507, LOAN1 x2] and confirmed by running all of
     them under DR [golden/e2e7run], where every branch outcome matched:

        flags after ?DCMOP:  CY = (top <= bottom)   Z = (top = bottom)
                             S  = (top >  bottom)   (top = 2nd operand PUSHED)
        A >  B  push B,A  JP(F2)      A <  B  push A,B  JP(F2)
        A >= B  push A,B  JM(FA)      A <= B  push B,A  JM(FA)
        A =  B  push A,B  JNZ(C2)     A ^= B  push A,B  "JZ"(CA)

     "JZ" is DR's mnemonic for opcode CA = JPE -- the same skew already
     banked for integer ^= [C072], so one opcode table covers both
     families.  The jump is a SKIP jump (taken iff the condition is
     FALSE) whose operand is backpatched by the ordinary continuation
     triple, exactly like the integer arms: [R507] JP -> 004F = the
     CALL ?STOPX, [R608] JP -> 0057 = the first address after the loop,
     [LOAN1] JP -> 01E4 (inner-while exit) and JP -> 01A8 (past the
     then-assignment). *)
  | Ast.Ebinary (Ast.EqR rop, a, b) when is_dec_operand st a
                                          || is_dec_operand st b ->
      let opc = dec_cmp_rel st rop a b in
      d st opc;
      let slot = st.lc in d st 0; d st 0; slot
  | Ast.Ebinary (Ast.EqR Ast.Eq, { Ast.e = Ast.Eident v; _ },
                 { Ast.e = Ast.Enumber "0"; _ }) ->
      d st op_lxi_h; reloc st Data (addr_of st v.Ast.orig);
      d st op_mov_a_m; d st op_inx_h; d st op_ora_m;
      d st op_jnz; let slot = st.lc in d st 0; d st 0; slot
  | Ast.Ebinary (Ast.EqR Ast.Gt, { Ast.e = Ast.Eident v; _ },
                 { Ast.e = Ast.Enumber k; _ }) ->
      let kk = parse_int_const k in
      if kk < 1 then failwith "codegen: compare > k<=0 form unproven [TBD]";
      d st op_lhld; reloc st Data (addr_of st v.Ast.orig);
      let m = (-(kk + 1)) land 0xffff in
      d st op_lxi_b; d st (m land 0xff); d st ((m lsr 8) land 0xff);
      d st op_dad_b; d st op_mov_a_h; d st op_ora_a;
      d st op_jm; let slot = st.lc in d st 0; d st 0; slot
  | Ast.Ebinary (Ast.EqR Ast.Ne, { Ast.e = Ast.Eident v; _ },
                 { Ast.e = Ast.Enumber k; _ }) ->
      (* [Y303/Y306] i ^= kk -> LHLD; (DCX H)*kk; MOV A,H; ORA L;
         skip-when-equal = CA (the ^= skip byte quirk [C072]).
         DR's switch to a cheaper ladder for large kk unproven:
         cap 8, above -> [TBD] *)
      let kk = parse_int_const k in
      if kk < 1 || kk > 8 then
        failwith "codegen: ^= const range unproven [TBD]";
      d st op_lhld; reloc st Data (addr_of st v.Ast.orig);
      for _ = 1 to kk do d st op_dcx_h done;
      d st op_mov_a_h; d st 0xb5;      (* ORA L *)
      d st 0xca;
      let slot = st.lc in d st 0; d st 0; slot
  | Ast.Ebinary (Ast.EqR Ast.Lt, { Ast.e = Ast.Eident v; _ },
                 { Ast.e = Ast.Enumber k; _ }) ->
      (* [Z401/Z405] i < kk: LHLD; (DCX H)*kk; MOV A,H; ORA A;
         JP(F2) -> skip. NOTE ORA A here vs ORA L in the ^= form.
         DR's switch point to a cheaper ladder for large kk
         unproven: cap 8, above -> [TBD] *)
      let kk = parse_int_const k in
      if kk < 1 || kk > 8 then
        failwith "codegen: < const range unproven [TBD]";
      d st op_lhld; reloc st Data (addr_of st v.Ast.orig);
      for _ = 1 to kk do d st op_dcx_h done;
      d st op_mov_a_h; d st op_ora_a;
      d st op_jp;
      let slot = st.lc in d st 0; d st 0; slot
  | Ast.Ebinary (Ast.EqR r, l, rr) when is_ident l && is_ident rr ->
      let ident = fun x ->
        match x.Ast.e with Ast.Eident n -> n.Ast.orig | _ -> assert false
      in
      (match r with
       | Ast.Lt | Ast.Ge ->
           d st op_lhld; reloc st Data (addr_of st (ident l));
           d st op_xchg;
           d st op_lhld; reloc st Data (addr_of st (ident rr));
           call_ext st "?IS22N";
           d st (if r = Ast.Lt then op_jp else op_jm)
       | Ast.Gt | Ast.Le ->
           d st op_lhld; reloc st Data (addr_of st (ident rr));
           d st op_xchg;
           d st op_lhld; reloc st Data (addr_of st (ident l));
           call_ext st "?IS22N";
           d st (if r = Ast.Gt then op_jp else op_jm)
       | Ast.Eq | Ast.Ne ->
           d st op_lhld; reloc st Data (addr_of st (ident l));
           d st op_push_h;
           d st op_lhld; reloc st Data (addr_of st (ident rr));
           d st op_pop_d;
           call_ext st "?IS22N";
           d st op_mov_a_h; d st 0xb5;  (* ORA L *)
           d st (if r = Ast.Eq then op_jnz else 0xca));  (* DR: ^= skip = JPE, not JZ: parity-defect [C072] *)
      let slot = st.lc in d st 0; d st 0; slot
  (* [E2E-7A slice 4] `if mod(x,y) = 0' and `^= 0' -- LOAN1's year-boundary
     test.  Zero new routines: the remainder already lands in HL from the
     existing ?IMDOP lowering, and DR's test is the plain HL-zero form
     (MOV A,H; ORA L) followed by JNZ for `= 0' [R908/R911/R912, LOAN1 00DC]
     and, for `^= 0', DR's usual `^=' skip byte CA -- $C PRINTS it as `JZ' at
     001C but the .REL byte is 0xca [R910], which extends the C072 parity-defect
     family (integer var-literal ^=, DEC ^=) to a third context.  Other
     relations against a mod (`> k', `mod = mod', non-zero right side) are
     unsampled: the relation is narrowed to Eq/Ne below so they keep refusing
     (a bare HL-zero test CANNOT express `> 0', it would silently mis-lower). *)
  | Ast.Ebinary
      ( Ast.EqR ((Ast.Eq | Ast.Ne) as r),
        ({ Ast.e = Ast.Ebuilt ("MOD", [ _; _ ]); _ } as xmod),
        { Ast.e = Ast.Enumber "0"; _ } ) ->
      lower_hl st xmod;
      d st op_mov_a_h; d st 0xb5; (* ORA L *)
      d st (if r = Ast.Eq then 0xc2 else 0xca);  (* DR's ^= skip byte is CA everywhere [C072, R910] *)
      st.last_imm <- None;
      let slot = st.lc in d st 0; d st 0; slot
  | _ -> failwith (Format.asprintf "codegen: condition form not in E2E-3b subset [TBD]: %a" Parser.pp_e c)

(* [R723] DR's HL-CONSTANT REUSE is a straight-line peephole: after a
   conditional skip jump the loaded constant belongs to a DIFFERENT basic
   block, so the tracking state must die with the jump.  R723 proves it --
   `if a > e then m = 1; else m = 0;` reloads `LXI H,0000` in the else
   branch instead of reusing HL=1 through the MOV L,H trick [G116], which
   the unqualified rule would have fired. *)
let lower_test_skip st (c : Ast.expr) =
  let slot = lower_test_skip0 st c in
  st.last_imm <- None;
  slot

let lower_assign st (lhs : Ast.expr) (rhs : Ast.expr) =
  (match lhs.Ast.e with
   | Ast.Eident n ->
       if List.mem (String.lowercase_ascii n.Ast.orig) st.deref then
         failwith
           "codegen: store to pointer formal unproven [TBD]"
   | _ -> ());
  match lhs.Ast.e with
  | Ast.Eident n when vk_dec_opt st n <> None ->
      (* [E2E-6] FIXED DECIMAL store: push the DEC value (with the target's
         precision as the literal context), then ?DSTOP pops it into the
         cell [R501/R502/R503/R505/R508/R510/R511] *)
      st.last_imm <- None;
      let (p, _s) = Option.get (vk_dec_opt st n) in
      ignore (dec_push st (Some (p, _s)) rhs);
      d st op_lxi_h; reloc st Data (addr_of st n.Ast.orig);
      d st op_mvi_a; d st p; call_ext st "?DSTOP"
  | Ast.Eident n when is_small_int st n ->
      (* [N306/N308] 1-byte FIXED BIN store: value in A then
         STA dir (3C + RELOC). Consts: MVI A,lo. Expressions:
         evaluate to HL, MOV A,L (6A). The const-reuse ladders are
         2-byte-only in DR evidence; not attempted here. *)
      st.last_imm <- None;
      (match rhs.Ast.e with
       | Ast.Enumber s ->
           let k = parse_int_const s in
           if k < 0 || k > 255 then
             failwith "codegen: 1-byte const store range [TBD]";
           d st op_mvi_a; d st k
       | _ -> lower_hl st rhs; d st 0x7d (* MOV A,L *)) ;
      (* 1-byte store: DR emits opcode 0x32 with the inline-reloc
         16-bit address ($C prints 'STA'; byte replicated literally
         [N303/N306/N308], same family of byte-vs-mnemonic quirks
         as CA/F2 — runtime identity comes from byte-identical COM) *)
      d st 0x32; reloc st Data (addr_of st n.Ast.orig)
  | Ast.Eident n when vk_of st n.Ast.orig = Vflt ->
      (* [E2E-10] store into a FLOAT variable: a literal or plain-cell source
         copies cell-to-cell with ?FX44M [R3001, R3037]; a computed value is
         popped off the float stack with ?FX44S [R3030-R3034] *)
      st.last_imm <- None;
      fl_store_var st (addr_of st n.Ast.orig) (fl_push st rhs)
  | Ast.Eident _n when is_float_expr st rhs ->
      failwith
        (Printf.sprintf
           "codegen: storing a FLOAT value into a non-float variable is unsampled [TBD] (line %d; ?FL40M/?QFI15 has no standalone sample)"
           rhs.Ast.epos.Source.line)
  | Ast.Eident n when is_dec_expr st rhs ->
      (* [E2E-6/R506] DEC -> INT: push the decimal value, convert with
         ?QDI15 (16-bit result in HL), then the ordinary integer store.
         R506 line 6 exactly: LXI H,D A(0002) ; MVI A,0F ; CALL ?DLDOP ;
         CALL ?QDI15 ; SHLD I A(0000).  The DLDOP precision is the
         SOURCE decimal's, not the target's. *)
      let vi =
        match
          List.assoc_opt (String.lowercase_ascii n.Ast.orig) st.vars
        with
        (* an undeclared name reaches here as PL/I's implicit FLOAT, which
           this compiler does not model; fail loud instead of raising
           Not_found out of List.assoc [E2E-9 hygiene] *)
        | Some v -> v
        | None ->
            failwith
              ("codegen: assignment target " ^ n.Ast.orig
               ^ " has no declaration in scope [TBD] (implicit FLOAT is"
               ^ " NOT IMP)")
      in
      if not (dec_pure st rhs) then
        failwith
          "codegen: mixed decimal/integer arithmetic unproven [TBD]            (the DEC->INT conversion is pinned only for a direct decimal             operand: i = d [R506])";
      if vi.size <> 2 then
        failwith
          "codegen: DEC->INT store into a 1-byte FIXED target [TBD] \
           (only the FIXED BIN(15) conversion is pinned by R506)";
      st.last_imm <- None;
      ignore (dec_push st None rhs);
      call_ext st "?QDI15";
      d st op_shld; reloc st Data (addr_of st n.Ast.orig)
  | Ast.Eident n when vk_of st n.Ast.orig <> Vint ->
      (* char/varying store path [V101-V106]; HL clobbered *)
      st.last_imm <- None;
      (match rhs.Ast.e with
       | Ast.Estring v -> store_char st n.Ast.orig (vk_of st n.Ast.orig) v
       | _ -> failwith "codegen: char store from non-literal [TBD]")
  | Ast.Eident n ->
      (* HL-REUSE PEEPHOLE [G114 $C]: `a = 5; b = 3;` lowers the second
         constant as 2x DCX H on the HL=5 still live after SHLD A, not a
         fresh LXI H. Only the delta 1..4 (DCX repeat) form is proven;
         larger deltas and INX directions stay [TBD]-free by falling
         back to the ordinary fresh-load path. *)
      (match rhs.Ast.e with
       | Ast.Enumber s ->
           let k = parse_int_const s in
           (match st.last_imm with
            (* [R610/R611/LOAN1] same constant stored again: DR emits NO
               reload at all -- HL still holds it, SHLD does not disturb it.
               LOAN1 needs this for `m = 0; y = 0;` (LXI H,0000; SHLD M;
               SHLD Y) and R611 proves it is value-equality, not zero:
               `x = 5; y = 5;` also shares one LXI H,0005. *)
            | Some pv when pv = k -> st.last_imm <- Some k
            (* [G116] k=0 with previous H byte = 0: MOV L,H zeroes HL *)
            | Some p when k = 0 && p land 0xff00 = 0 ->
                st.last_imm <- Some k; d st 0x6c (* MOV L,H *)
            (* [G114] small positive delta: DCX H repeats *)
            | Some p when p - k >= 1 && p - k <= 2 ->
                st.last_imm <- Some k;
                const_sub st (p - k)
            (* [G114B] small negative delta: INX H repeats *)
            | Some p when k - p >= 1 && k - p <= 2 ->
                st.last_imm <- Some k;
                for _ = 1 to k - p do d st op_inx_h done
            (* [Z401 delta 3, Z406 delta 4] same high byte, |delta|>=3:
               MVI L,lo (2 bytes beats any ladder). G114C (delta 771,
               differing high) stays on the fresh-LXI fallback. *)
            | Some p when p land 0xff00 = k land 0xff00
                          && (p - k >= 3 || k - p >= 3) ->
                st.last_imm <- Some k;
                d st 0x2e (* MVI L *) ; d st (k land 0xff)
            | _ ->
                st.last_imm <- Some k;
                d st op_lxi_h; d st (k land 0xff); d st ((k lsr 8) land 0xff))
       | Ast.Ebinary (Ast.Add, { Ast.e = Ast.Eident m; _ },
                      { Ast.e = Ast.Enumber "1"; _ })
         when String.lowercase_ascii m.Ast.orig
              = String.lowercase_ascii n.Ast.orig ->
           (* [Z401/Z403/Z404] x = x + 1 -> LHLD; INX H; SHLD.
              HL holds a RUNTIME value afterwards: last_imm is
              constant-tracking only -> None. -1/INX-variant forms
              unproven, stay on the generic path. *)
           st.last_imm <- None;
           d st op_lhld; reloc st Data (addr_of st n.Ast.orig);
           d st op_inx_h
           (* final SHLD comes from the common tail *)
       | _ ->
           st.last_imm <- None;
           lower_hl st rhs);
      d st op_shld; reloc st Data (addr_of st n.Ast.orig)
  | _ -> failwith "codegen: non-simple assignment lhs [TBD]"

(* ---- E2E-3b: comparisons ----  ALL forms transcribed from $C traces
   golden/e2e3b (G114/G115/G116) — see spec/notes/codegen.md:
   var OP var: relational = load pair XCHG-form + ?IS22N + sign-test
     conditional skip (Gt/Le evaluate RIGHT-left with JP/JM; Lt/Ge
     evaluate LEFT-right); equality = PUSH/POP form + MOV A,H; ORA L
     zero test + JNZ/JZ. var = 0: memory zero test (LXI H; MOV A,M;
     INX H; ORA M; JNZ). var > k (k>=1): LHLD; LXI B,-(k+1); DAD B;
     MOV A,H; ORA A; JM. Each returns the forward conditional-jump
     operand SLOT (fixed later by emit_triple at the skip target). *)

(* GET LIST(n1, n2, ...).  The statement SKELETON is shared by every target
   kind [X201/X202 char-varying, R901-R907 numeric]: LXI D,0290 input
   descriptor (vs 0252 for print, never relocated); LXI B,0000 whose operand
   is triple-patched to the NEXT statement; ?SYSIN; then ONE `?GNVOP ; JP`
   PAIR PER ITEM in source order.  Item k's JP operand is patched to whatever
   follows that item's store -- the NEXT item's GNVOP [R904: 0013 ==== 001B]
   or the closing ?QIOOP for the last item [X202] -- so a skip (EOF / no
   value) abandons the remaining items, not the statement.  One ?QIOOP closes
   the whole statement.

   PER-ITEM CONVERSION, by destination kind [R901-R907]:
     FIXED DEC(p,s) : MVI B,s ; ?QCDOP ; LXI H,var ; MVI A,p ; ?DSTOP
        B is the TARGET SCALE -- 02 for dec(11,2)/dec(9,2), 04 for dec(6,4),
        03 for dec(15,3) -- and is EMITTED even at s=0 [R905 `MVI B,00`]; A is
        the TARGET DIGITS [LOAN1 P=0B, R906 x=0F].  So ?QCDOP converts the
        scanned field straight to scale s and ?DSTOP stores it like any other
        DEC store -- which is why no QDDSL/QDDSR appears here at all.
     FIXED BIN(2b)  : ?QCIOP ; SHLD var                [R903, R904: no MVI]
     CHAR VAR(cap)  : LXI H,var ; MVI B,cap ; ?SSVFS   [X201/X202]
*)
let lower_get st (items : Ast.name list) =
  if
    List.exists
      (fun n -> List.mem (String.lowercase_ascii n.Ast.orig) st.deref)
      items
  then failwith "codegen: GET into pointer formal unproven [TBD]";
  d st op_lxi_d; d st 0x90; d st 0x02;   (* LXI D,0290 input desc *)
  d st op_lxi_b;
  let bslot = st.lc in
  d st 0; d st 0;
  call_ext st "?SYSIN";
  List.iter
    (fun n ->
      call_ext st "?GNVOP";
      d st op_jp;
      let jpslot = st.lc in
      d st 0; d st 0;
      (match List.assoc_opt (String.lowercase_ascii n.Ast.orig) st.vars with
       | Some vi -> (
           match vi.vk with
           | Vdec (p, s) ->
               d st op_mvi_b;
               d st s; (* B = TARGET SCALE, emitted even at 0 [R905] *)
               call_ext st "?QCDOP";
               d st op_lxi_h;
               reloc st Data (addr_of st n.Ast.orig);
               d st op_mvi_a;
               d st p; (* A = TARGET DIGITS [LOAN1 0B, R906 0F] *)
               call_ext st "?DSTOP"
           | Vflt ->
               (* R3004 OBSERVES DR's float GET route (?QFADS, ?FNCVS, ...)
                  but it is not implemented here, so refuse instead of
                  guessing: no target program of this milestone reads a
                  float (FLTPOLY's GET feeds DECIMAL variables). *)
               failwith
                 "codegen: GET LIST into a FLOAT variable is observed on DR [R3004] but unimplemented [TBD]"
           | Vint when vi.size = 2 ->
               call_ext st "?QCIOP";
               d st op_shld; reloc st Data (addr_of st n.Ast.orig)
           | Vint ->
               (* a 1-byte FIXED BIN store is the 0x32/`STA` form [C079] and
                  no numeric-GET sample has one: refuse rather than guess. *)
               failwith
                 "codegen: numeric GET into a 1-byte FIXED BINARY target is unproven [TBD] (R903/R904 sample only the 2-byte ?QCIOP/SHLD form)"
           | Vvar c ->
               if c > 255 then failwith "codegen: cap > 255 [TBD]";
               d st op_lxi_h;
               reloc st Data (addr_of st n.Ast.orig);
               d st op_mvi_b;
               d st c;
               call_ext st "?SSVFS"
           | _ ->
               failwith
                 "codegen: GET LIST of this target kind is unproven [TBD] (based, pointer, float and bit targets are unsampled)")
       | None ->
           failwith
             (Printf.sprintf "codegen: GET LIST of unknown variable %s [TBD]"
                n.Ast.orig));
      (* the skip lands on whatever comes next [R904, X202] *)
      emit_triple st jpslot st.lc)
    items;
  call_ext st "?QIOOP";
  emit_triple st bslot st.lc           (* continuation = next stmt *)

(* PUT LIST with || chain: DR evaluates RIGHT-to-LEFT while the
   pool is allocated LEFT-to-RIGHT in source order [W102 hex:
   HELLO@5, BYE@0x0B]. C2: SLVTS(right var; empty stack -> no PUSH
   PSW) then SJSCM(lit in B). C3: SLCTS(right lit in A); PUSH PSW;
   SLVTS(var); SJSCM(left lit in B); SJSTS. Tail = the standard
   PNCOP/QIOOP + continuation triple [W101/W102]. *)
let lower_cat st (skipn : string option) (ch : chain) =
  let maxlit = match ch with C2 (l, _, _) -> String.length l
               | C3 (l, _, r) -> max (String.length l) (String.length r) in
  if maxlit > 255 then failwith "codegen: lit > 255 [TBD]";
  d st op_lxi_d; d st 0x52; d st 0x02;
  d st op_lxi_b;
  let bslot = st.lc in
  d st 0; d st 0;
  call_ext st "?SYSPR";
  (match skipn with
   | Some c ->
       let n = parse_int_const c in
       if n <= 0 || n > 255 then
         failwith "codegen: skip count out of MVI range [TBD]";
       d st op_mvi_a; d st n; call_ext st "?SKPOP"
   | None -> ());
  let vk_guard nm =
    match vk_of st nm with
    | Vvar _ -> ()
    | _ -> failwith "codegen: concat operand not char varying [TBD]"
  in
  (match ch with
  | C2 (l, v, _) ->
      let al = pool_alloc st (pool_bytes l) in
      vk_guard v;
      d st op_lxi_h; reloc st Data (addr_of st v);   (* rightmost first *)
      call_ext st "?SLVTS";
      d st op_lxi_h; reloc st Data al;
      d st op_mvi_b; d st (String.length l);
      call_ext st "?SJSCM"
  | C3 (l, v, r) ->
      (* [W102] pool allocation = SOURCE order (HELLO@5, BYE@0x0B) *)
      let al = pool_alloc st (pool_bytes l) in
      let ar = pool_alloc st (pool_bytes r) in
      vk_guard v;
      d st op_lxi_h; reloc st Data ar;
      d st op_mvi_a; d st (String.length r);
      call_ext st "?SLCTS";                          (* rightmost *)
      d st op_lxi_h; reloc st Data (addr_of st v);
      d st op_push_psw;        (* [W102] AFTER LXI H, before SLVTS *)
      call_ext st "?SLVTS";
      d st op_lxi_h; reloc st Data al;
      d st op_mvi_b; d st (String.length l);
      call_ext st "?SJSCM";
      call_ext st "?SJSTS");
  call_ext st "?PNCOP"; call_ext st "?QIOOP";
  emit_triple st bslot st.lc

(* DO ind = from TO bound [BY 1];) E2E-4 slice, [Y301-Y305] bytes:
   init reuses HL when last_imm = from-1 (INX H [Y302]) else LXI H.
   STATIC bound b: head = LHLD i; LXI B,-(b+1); DAD B; MOV A,H;
   ORA A; JP(F2) -> exit (deferred triple AFTER the loop's JMP on the
   record stream [Y301 dump]). DYNAMIC simple-int bound: LHLD bound;
   SHLD temp(base+auto_end+2k); head = LHLD temp; XCHG; LHLD i;
   CALL ?IS22N; JM(FA) -> exit. Increment shared: LHLD i; INX H;
   SHLD i; JMP head (inline backward RELOC). Body continuation
   triples land on the increment start automatically [Y301: put
   cont -> 0x2F]. BY must be absent or literal 1 [Y304]; WHILE/
   REPEAT/no-TO/complex bounds/steps/index types all [TBD]. *)
let lower_doto st (ls : lblstate) (lo : st -> lblstate -> Ast.stmt -> unit)
    (ind : Ast.name) (from : Ast.expr)
    (by : Ast.expr option) (to_ : Ast.expr option)
    (while_ : Ast.expr option) (rep : Ast.expr option)
    (body : Ast.stmt) =
  (* proven REPEAT form [Z402/DFACT]: DO ind = c REPEAT(ind+1), no
     TO/WHILE/BY. Everything else about REPEAT/WHILE combos is
     unevidenced and stays [TBD]. *)
  let proven_repeat =
    match rep, to_, while_ with
    | Some { Ast.e = Ast.Ebinary (Ast.Add,
             { Ast.e = Ast.Eident ri; _ },
             { Ast.e = Ast.Enumber "1"; _ }); _ }, None, None
      when String.lowercase_ascii ri.Ast.orig =
           String.lowercase_ascii ind.Ast.orig -> true
    | _ -> false
  in
  let forever_repeat =
    match (to_, while_, rep) with
    | (None, None, Some _) -> true
    (* [E2E-8] `do i = 0 by 1;' indexes the loop but gives no bound and no
       REPEAT expression: DR emits NO exit test at all (the increment is the
       whole continuation) [IFACT, R1014, R1030-R1033] *)
    | (None, None, None) -> true
    | _ -> false
  in
  if while_ <> None
     || (to_ <> None && rep <> None)
     || (rep <> None && not proven_repeat && not forever_repeat) then
    failwith "codegen: DO WHILE/REPEAT combo/UNTIL deferred [TBD]";
  (* [E2E-8] DO ... BY step.  A step is an INTEGER LITERAL: DR's increment is
     |step| rung instructions, so an expression step cannot be lowered that
     way at all [N36 stays refused; DR also rejects a non-integer step at
     compile time].  Magnitudes above 2 are unprobed. *)
  let step =
    match by with
    | None -> 1
    | Some { Ast.e = Ast.Enumber c; _ } -> parse_int_const c
    (* a negative literal step arrives as Eprefix(Minus, Enumber) *)
    | Some { Ast.e = Ast.Eprefix (Ast.Minus,
             { Ast.e = Ast.Enumber c; _ }); _ } ->
        -(parse_int_const c)
    | Some _ -> failwith "codegen: DO BY expression step unproven [TBD]"
  in
  if step = 0 then failwith "codegen: DO BY 0 [TBD]";
  let ak = abs step in
  if ak > 2 then failwith "codegen: DO BY magnitude > 2 unproven [TBD]";
  (* [E2E-8] FROM may be a constant (LXI H,imm) or a fixed-bin VARIABLE
     (LHLD v / SHLD index -- IFACT's `do n = i to 1 by -1') *)
  let fromc, fromvar =
    match from with
    | { Ast.e = Ast.Enumber c; _ } -> (Some (parse_int_const c), None)
    | { Ast.e = Ast.Eident nm; _ } ->
        (None,
         match vk_of st nm.Ast.orig with
         | Vint -> Some (addr_of st nm.Ast.orig)
         | _ -> failwith "codegen: DO FROM of non fixed-bin type unproven [TBD]")
    | _ -> failwith "codegen: DO FROM form unproven [TBD]"
  in
  if List.mem (String.lowercase_ascii ind.Ast.orig) st.deref then
    failwith "codegen: DO control is a pointer formal [TBD]";
  let iaddr =
    match vk_of st ind.Ast.orig with
    | Vint -> addr_of st ind.Ast.orig
    | _ -> failwith "codegen: DO index not fixed-bin [TBD]"
  in
  (* [E2E-8] init: DR loads the FROM constant with the CHEAPEST instruction
     that achieves it given the value already in HL (st.last_imm tracks that
     exact value; LXI H/imm and INX H set it, LHLD / branches / loop-body
     entry clear it):
       HL already = from       -> SHLD only          (0 load bytes) [R1015,R1022,R1032]
       HL already = from - 1   -> INX H ; SHLD       (1 byte)       [R1011, Y302]
       H known 0, from <= 255  -> MVI L,from ; SHLD  (2 bytes)      [R1012,R1013,R1030]
       otherwise               -> LXI H,from ; SHLD  (3 bytes)      [Y302, IFACT outer]
     MVI L is only safe when H is known 0, which is exactly the
     last_imm < 256 case. *)
  (match fromc with
   | Some fromv ->
       (match st.last_imm with
        | Some v when v = fromv -> ()
        | Some v when v + 1 = fromv -> d st op_inx_h
        | Some v when v >= 0 && v < 256 && fromv >= 0 && fromv < 256 ->
            d st 0x2e; d st fromv        (* MVI L,from *)
        | _ ->
            d st op_lxi_h; d st (fromv land 0xff);
            d st ((fromv lsr 8) land 0xff));
       st.last_imm <- Some (fromv land 0xffff);
       d st op_shld; reloc st Data iaddr
   | None ->
       (* variable FROM: load the source cell, store the index cell
          [IFACT 000C-000F: LHLD I / SHLD N] *)
       (match fromvar with
        | Some a -> d st op_lhld; reloc st Data a
        | None -> failwith "codegen: DO FROM [TBD]");
       d st op_shld; reloc st Data iaddr;
       st.last_imm <- None);
  if to_ = None && while_ = None && rep = None && by = None then begin
    (* [E2E-8 R1032] an indexed DO that specifies NOTHING (no TO, no WHILE,
       no REPEAT, no BY) degenerates: DR stores the FROM value, runs the body
       ONCE and falls through -- no increment, no exit test, no back-edge JMP.
       It is therefore not a no-exit loop and does not open the epilogue
       suppression window (DR's PUT after it lowers normally). *)
    lo st ls body;
    st.last_imm <- None
  end else if proven_repeat || forever_repeat then begin
    (* [Z402] body-head is the FIRST BODY instruction (not the
       init); tail increment LHLD/INX/SHLD; JMP back; no test.
       [R414/R426] at the window address the increment is
       LHLD; LXI H,const; DAD D; SHLD; JMP instead. *)
    (* [E2E-8] with no REPEAT expression the increment is the BY step:
       LHLD / (INX H)x|step| (or (DCX H)x|step| when step < 0) / SHLD / JMP
       [IFACT outer loop, R1014 k=1, R1018 k=2, R1033 k=-1]. *)
    let head = st.lc in
    st.last_imm <- None;   (* [E2E-8] body head is a branch target: HL unknown *)
    lo st ls body;
    d st op_lhld; reloc st Data iaddr;
    (* [Z402 k=1; R427 k=2] REPEAT(ind+k) = k INX H rungs;
       k>2 / other shapes unproven -> [TBD] *)
    (match rep with
     | Some { Ast.e = Ast.Ebinary (Ast.Add,
              { Ast.e = Ast.Eident ri; _ },
              { Ast.e = Ast.Enumber ck; _ }); _ }
       when String.lowercase_ascii ri.Ast.orig =
            String.lowercase_ascii ind.Ast.orig ->
         let k = parse_int_const ck in
         if k < 1 || k > 2 then
           failwith "codegen: REPEAT increment const [TBD]";
         for _ = 1 to k do d st op_inx_h done
     | None ->
         for _ = 1 to ak do
           d st (if step > 0 then op_inx_h else op_dcx_h)
         done
     | _ -> failwith "codegen: REPEAT increment form [TBD]");
    d st op_shld; reloc st Data iaddr;
    (d st op_jmp; st.last_imm <- None (* [R723] branch boundary *)); reloc st Code head;
    st.last_imm <- None
  end else begin
  let head, jpslot =
    match to_ with
    | Some { Ast.e = Ast.Enumber c; _ } ->
        let b = parse_int_const c in
        if b < 1 then
          failwith
            ("codegen: DO TO bound below 1 unproven [TBD] (DR switches to a \
             general XRA A/CMP M/INX H/SBB M signed compare for `to 0' \
             [R1029], which is not in the banked subset)");
        let head = st.lc in
        d st op_lhld; reloc st Data iaddr;
        st.last_imm <- None;   (* LHLD clobbers HL *)
        (* [E2E-8] the body is re-entered by the back-edge, so HL knowledge from
     the init/test is dead at body entry: DR's constant-store reuse is
     control-flow sensitive [IFACT line 11 `F = 1' gets LXI H,0001 even though
     the loop init executed LXI H,0000 just before] *)
  st.last_imm <- None;
  (* [E2E-8] the exit test compares the index against a constant:
           rising  -> c = bound + 1, skip when index >= bound+1  (JP)
           falling -> c = bound,     skip when index <  bound    (JM)
           [R1011 to 5 by 2 -> LXI B,FFFA; R1012/R1013 by -1/-2 -> DCX rungs;
            R1023/R1024 rising bound 1/2 -> 2/3 DCX rungs; R1025/R1026 rising
            bound 3/4 -> LXI B,-(b+1); R1027 to 20 by -1 -> LXI B,-20 + JM]
           The subtraction is peeled by size: c rung instructions when the
           ladder is strictly cheaper than LXI B + DAD B (4 bytes), i.e. c<=3. *)
        let cc = if step > 0 then b + 1 else b in
        if cc <= 3 then
          for _ = 1 to cc do d st op_dcx_h done
        else begin
          let neg = -cc in
          d st op_lxi_b; d st (neg land 0xff);
          d st ((neg lsr 8) land 0xff);
          d st op_dad_b
        end;
        d st op_mov_a_h; d st op_ora_a;
        d st (if step > 0 then op_jp else op_jm);
        let slot = st.lc in          (* OPERAND pos [Y301: 0x16] *)
        d st 0; d st 0;
        (head, slot)
    | Some { Ast.e = Ast.Eident bn; _ } ->
        (match vk_of st bn.Ast.orig with
         | Vint -> ()
         | _ -> failwith "codegen: DO bound not fixed-bin [TBD]");
        let auto_end =
          List.fold_left
            (fun a (_, (vi : var_info)) -> max a (vi.off + vi.size))
            0 st.vars
        in
        let temp =
          st.base + max auto_end st.floor + 2 * st.temps
        in
        st.temps <- st.temps + 1;
        d st op_lhld; reloc st Data (addr_of st bn.Ast.orig);
        d st op_shld; reloc st Data temp;
        let head = st.lc in
        d st op_lhld; reloc st Data temp;
        d st op_xchg;
        d st op_lhld; reloc st Data iaddr;
        call_ext st "?IS22N";
        d st op_jm;
        let slot = st.lc in          (* OPERAND pos [Y302] *)
        d st 0; d st 0;
        (head, slot)
    | Some _ -> failwith "codegen: DO complex bound unproven [TBD]"
    | None -> failwith "codegen: DO without TO deferred [TBD]"
  in
  lo st ls body;
  d st op_lhld; reloc st Data iaddr;
  (* [E2E-8] |step| rungs in the step's direction [R1011 by 2 -> 2 INX H;
     R1013 by -2 -> 2 DCX H; R1012/R1033 by -1 -> 1 DCX H] *)
  for _ = 1 to ak do d st (if step > 0 then op_inx_h else op_dcx_h) done;
  d st op_shld; reloc st Data iaddr;
  (d st op_jmp; st.last_imm <- None (* [R723] branch boundary *));
  reloc st Code head;   (* helper advances LC [Y301] *)
  emit_triple st jpslot st.lc;
  st.last_imm <- None
  end

(* numeric item print width: max of IDENT-leaf widths [N301-N305];
   constant-only expressions have no DR evidence -> [TBD] *)
let num_width st (x : Ast.expr) =
  let rec w e =
    match e.Ast.e with
    | Ast.Eident n ->
        (match vk_of st n.Ast.orig with
         | Vint ->
             (List.assoc (String.lowercase_ascii n.Ast.orig) st.vars).w
         | _ -> failwith "codegen: char var in numeric PUT item [TBD]")
    | Ast.Ebinary (_, l, r) -> max (w l) (w r)
    | Ast.Eprefix (_, x) -> w x
    | Ast.Esuffix (hd, [ _ ]) ->
        let hn =
          match hd.Ast.e with
          | Ast.Eident h -> String.lowercase_ascii h.Ast.orig
          | _ -> ""
        in
        if List.mem_assoc hn st.procs then
          (* result of a RETURNS FIXED procedure: default bin(15)
             width [HYPOTHESIS for returns BIN(p): no evidence yet] *)
          9
        else failwith "codegen: PUT numeric item form unproven [TBD]"
    | Ast.Enumber _ -> 0
    | _ -> failwith "codegen: PUT numeric item form unproven [TBD]"
  in
  let r = w x in
  if r = 0 then
    failwith "codegen: constant-only PUT numeric item unproven [TBD]"
  else r

(* General PUT LIST item chain [N301-N306]: preamble; optional skip
   (bare = 1, skip(n)); per item: literal = LXI H,*S; MVI A,len;
   SLCTS; PNCOP; numeric (var/expr) = <HL>; MVI A,width; QICOP;
   PNVOP; single char/varying var = the V101/V106 chain (multi-item
   char vars UNPROVEN -> [TBD]); then ONE QIOOP + continuation. *)
let lower_put_items_gen st (edit_tbl : int option)
    (skipn : string option) (items : pitem list) =
  (* [E2E-8] `~edit_tbl' turns the same per-item value preparation into PUT
     EDIT: the table is loaded and ?EDITF called right after ?SYSPR, and every
     item's output tail becomes ?EDTOV instead of ?PNCOP/?PNVOP [IFACT,
     R1001-R1020].  PUT LIST keeps the byte-frozen path (edit_tbl = None). *)
  let is_edit = edit_tbl <> None in
  (* `tail keep_going ()': keep_going = true selects ?PNCOP (character item,
     cursor continues), false selects ?PNVOP (numeric); for PUT EDIT every
     tail is ?EDTOV regardless [R1001-R1020]. *)
  let tail keep_going () =
    call_ext st (if is_edit then "?EDTOV"
                 else if keep_going then "?PNCOP" else "?PNVOP")
  in
  (* [G112/N18-era perimeter] a char-varying item in a MULTI-item PUT LIST is
     unsampled and stays refused.  [E2E-8] PUT EDIT DOES sample it --
     R1020 `put edit(c, i)(a(3), f(2,1), skip)' puts varying+barying ... i.e.
     char varying next to a binary variable -- so the guard applies to the LIST
     path only. *)
  let char_var_ok =
    is_edit || List.length items = 1 ||
    not (List.exists (function PIvar n ->
                        (match vk_of st n.Ast.orig with
                         | Vint -> false | Vdec _ -> false | Vflt -> false
                         | _ -> true)
                      | _ -> false) items)
  in
  if not char_var_ok then
    failwith "codegen: char var in multi-item PUT unproven [TBD]";
  d st op_lxi_d; d st 0x52; d st 0x02;
  d st op_lxi_b;
  let bslot = st.lc in
  d st 0; d st 0;
  call_ext st "?SYSPR";
  (match skipn with
   | Some c ->
       let n = parse_int_const c in
       if n <= 0 || n > 255 then
         failwith "codegen: skip count out of MVI range [TBD]";
       d st op_mvi_a; d st n; call_ext st "?SKPOP"
   | None -> ());
  (match edit_tbl with
   | Some addr ->
       (* the table was allocated by prealloc_fmt_tables, ahead of every
          non-table pool item [R1003/R1021/R1022] *)
       d st op_lxi_h; reloc st Data addr; call_ext st "?EDITF"
   | None -> ());
  List.iter
    (fun it ->
      match it with
      | PIlit v ->
          let len = String.length v in
          if len > 255 then failwith "codegen: literal > 255 [TBD]";
          let addr = pool_alloc st (pool_bytes v) in
          d st op_lxi_h; reloc st Data addr;
          d st op_mvi_a; d st len;
          call_ext st "?SLCTS"; tail true ()
      | PIvar n ->
          (match vk_of st n.Ast.orig with
           | Vflt ->
               (* [E2E-10] float variable item: LXI H,var; MVI A,0E; ?QFCMS.
                  0E = 14 is a CONSTANT width in every sample, not a
                  precision [R3030, R3037, R3045: three float vars in one
                  PUT LIST, each with MVI A,0E] *)
               if is_edit then
                 failwith
                   "codegen: PUT EDIT of a FLOAT item is unsampled [TBD] (no DR sample puts a float through an edit list)";
               if List.mem (String.lowercase_ascii n.Ast.orig) st.deref then
                 failwith
                   "codegen: PUT LIST of a FLOAT formal is unsampled [TBD] (R3038 reads a float formal inside an expression, never prints it through its pointer cell)";
               d st op_lxi_h; reloc st Data (addr_of st n.Ast.orig);
               d st op_mvi_a; d st 14; call_ext st "?QFCMS"; tail false ()
           | Vdec (p, s) ->
               if List.mem (String.lowercase_ascii n.Ast.orig) st.deref then
                 failwith
                   ("codegen: PUT LIST of a FIXED DECIMAL formal is unsampled "
                    ^ "[TBD] (no DR sample outputs a decimal through its "
                    ^ "pointer cell)");
               (* [R501/R502/R503/R508/R510/R511] DEC variable item = DLDOP
                  then QDCOP(width=p+3, scale=s); R506 proves a DEC var in a
                  MULTI-item list next to an INT var *)
               d st op_lxi_h; reloc st Data (addr_of st n.Ast.orig);
               d st op_mvi_a; d st p; call_ext st "?DLDOP";
               if is_edit then
                 failwith "codegen: PUT EDIT of a FIXED DECIMAL item is \
                           unsampled [TBD] (no DR sample passes a DEC item \
                           through an edit list)";
               d st op_mvi_a; d st (p + 3); d st op_mvi_b; d st s;
               call_ext st "?QDCOP"; tail false ()
           | Vint ->
               let vi =
                 List.assoc (String.lowercase_ascii n.Ast.orig) st.vars
               in
               lower_hl st { Ast.e = Ast.Eident n;
                             Ast.epos = n.Ast.pos };
               d st op_mvi_a; d st vi.w;
               call_ext st "?QICOP"; tail false ()
           | vk ->
               (* single-item char var = the banked V101/V106 chain *)
               (match vk with
                | Vvar _ ->
                    d st op_lxi_h; reloc st Data (addr_of st n.Ast.orig);
                    call_ext st "?SLVTS"
                | Vfix cap ->
                    if cap > 255 then failwith "codegen: cap > 255 [TBD]";
                    d st op_lxi_h; reloc st Data (addr_of st n.Ast.orig);
                    d st op_mvi_a; d st cap; call_ext st "?SLCTS"
                | Vint -> assert false);
               tail true ())
      | PInum x ->
          if is_float_expr st x then begin
            (* [E2E-10/FFACT] a float call item leaves its result on the
               float stack and the edit pair MVI A,0E / ?QFCSS follows the
               CALL directly.  Other float shapes have no PUT sample. *)
            (match (unwrap_e x).Ast.e with
             | Ast.Esuffix _ -> ()
             | _ ->
                 failwith
                   "codegen: PUT LIST of a computed FLOAT expression is unsampled [TBD] (FFACT pins only a float CALL result: descriptor, CALL, MVI A,0E, ?QFCSS)");
            ignore (fl_push st x);
            d st op_mvi_a; d st 14; call_ext st "?QFCSS"; tail false ()
          end else if is_dec_expr st x then begin
            (* [DFACT] a DEC function-call item leaves its result on the
               decimal stack; the edit pair follows directly *)
            let (p, s) = dec_edit_pt st x in
            ignore (dec_push st None x);
            if is_edit then
              failwith "codegen: PUT EDIT of a FIXED DECIMAL item is unsampled \
                        [TBD] (no DR sample passes a DEC item through an edit \
                        list)";
            d st op_mvi_a; d st (p + 3); d st op_mvi_b; d st s;
            call_ext st "?QDCOP"; tail false ()
          end else begin
            lower_hl st x;
            d st op_mvi_a; d st (num_width st x);
            call_ext st "?QICOP"; tail false ()
          end)
    items;
  call_ext st "?QIOOP";
  emit_triple st bslot st.lc

(* the byte-frozen PUT LIST entry point: no format table, so every item's
   output tail is ?PNCOP/?PNVOP as before [G107/G108, N301-N306, R506]. *)
let lower_put_items st (skipn : string option) (items : pitem list) =
  lower_put_items_gen st None skipn items

(* pop the next pre-allocated format-table address [E2E-8] *)
let take_fmt_addr st =
  match st.fmtq with
  | a :: rest -> st.fmtq <- rest; a
  | [] -> failwith "codegen: PUT EDIT format table not pre-allocated [TBD]" 

(* statement lowering with label/goto resolution *)
(* [E2E-5c P401] internal procedure block: forward-call resolution,
   deref prologue, scoped body lowering. Recursive procedures and
   bare-BEGIN blocks stay [TBD]. *)
let rec lower_proc st (ls : lblstate) (bs : Ast.block_stmt) =
  let pb = bs.Ast.blk in
  let nm =
    match pb.Ast.bname with
    | Some n -> String.lowercase_ascii n.Ast.orig
    | None -> failwith "codegen: procedure without name [TBD]"
  in
  let pl =
    match List.assoc_opt nm st.procs with
    | Some p -> p
    | None ->
        failwith "codegen: BEGIN-block/procedure lowering deferred [TBD]"
  in
  (* [R404/R405/R406/R423/R429/R432/P404] TAIL GUARD: emitted at the
     append address BEFORE the entry label / forward-call chain /
     prologue; see the guard_slots field comment for the full rule.
     Evaluated once per program (the first appended proc). *)
  if (not st.in_proc) && not st.stop_seen && not st.after_forever
  then begin
    if st.guards = 0 then begin
      st.guards <- st.guards + 1;
      (d st op_jmp; st.last_imm <- None (* [R723] branch boundary *));
      st.guard_slots <- st.lc :: st.guard_slots;
      d st 0; d st 0
    end
    else
      (* A SECOND appended proc in a guarded shape is unproven: no
         golden has two top-level procedures. Refuse rather than
         extrapolate DR's behavior. *)
      failwith
        "codegen: second appended procedure after a tail guard \
         [TBD: unproven, no multi-procedure golden]"
  end;
  if not st.in_proc then st.appended <- true;
  (* entry label [P401 'dbl:' — blabel from parse_proc_block] *)
  (match pl.Bind.pl_lbl with
   | Some l ->
       ls.labs <- (l, st.lc) :: ls.labs;
       let slots =
         List.filter (fun (k, _) -> k = l) ls.fwd |> List.map snd
       in
       ls.fwd <- List.filter (fun (k, _) -> k <> l) ls.fwd;
       (match slots with
        | [] -> ()
        | [ one ] -> link st t_chain_addr (Some (Code, one)) None
        | _ ->
            failwith
              "codegen: multiple forward GOTO per label chain \
               unproven [TBD]")
   | None -> ());
  (* resolve pending forward CALLs at the entry byte [P401 @1285] *)
  let hits = List.filter (fun (k, _) -> k = nm) st.fcalls in
  st.fcalls <- List.filter (fun (k, _) -> k <> nm) st.fcalls;
  (match hits with
   | [] -> ()
   | [ (_, one) ] -> link st t_chain_addr (Some (Code, one)) None
   | _ ->
       failwith "codegen: multiple forward CALL chain unproven [TBD]");
  st.entries <- (nm, st.lc) :: st.entries;
  (match pl.Bind.pl_ptrs with
   | [ (_f, ptr) ] ->
       if pl.Bind.pl_rec then begin
         (* recursive activation [RFACT @56-6D: LXI B,8; LXI D,10;
            CALL ?SVBLK; deref; SHLD ptr@10; LHLD ptr; deref;
            SHLD shadow@12. P402 @2C-40 identical shape with
            B=8,D=6. Sizes from the layout section (4 cells x 2B
            incl. the self-call slot+temp) [R427 re-check] *)
         let (bb, bsz) =
           match
             List.filter_map
               (fun (n, b, sz) -> if n = nm then Some (b, sz) else None)
               st.secs
           with
           | [ x ] -> x
           | _ -> failwith "codegen: proc section missing [TBD]"
         in
         d st op_lxi_b; d st (bsz land 0xff);
         d st ((bsz lsr 8) land 0xff);
         d st op_lxi_d;
         reloc st Data (bb + st.base);
         call_ext st "?SVBLK";
         d st 0x5e; d st 0x23; d st 0x56; d st 0xeb;
         d st op_shld; reloc st Data (ptr + st.base);
         d st op_lhld; reloc st Data (ptr + st.base);
         d st 0x5e; d st 0x23; d st 0x56; d st 0xeb;
         let shad_off =
           match
             List.find_opt
               (fun (k, _rt, _o) ->
                 k = String.lowercase_ascii (fst (List.hd pl.Bind.pl_ptrs)))
               pl.Bind.pl_rows
           with
           | Some (_k, _rt, o) -> o
           | None ->
               failwith "codegen: recursive formal without dcl [TBD]"
         in
         d st op_shld; reloc st Data (shad_off + st.base)
       end else begin
         (* callee prologue [P401 dbl @29]: arg address arrives in HL *)
         d st 0x5e; d st 0x23; d st 0x56; d st 0xeb;
         d st op_shld; reloc st Data (ptr + st.base)
       end
   | [] when pl.Bind.pl_rec ->
       failwith "codegen: recursive procedure without formals [TBD]"
   | [] -> ()
   | ((f0, ptr0) :: rest) ->
       (* [E2E-9] MULTI-argument callee.  DR copies the whole descriptor
          block into the callee's contiguous pointer cells with a counted
          byte loop, HL = the descriptor address the caller left there:
              LXI D,<first ptr cell>     (destination, 2N bytes wide)
              MVI C,2N
          loop: MOV A,M / INX H / STAX D / INX D / DCR C / JNZ loop
          The back edge is an INLINE RELOC(code,loop) [R2001 @1606 -> 003E,
          R2012 JNZ 0063].  Sampled byte-exactly with 2, 3 and 4 formals
          [R2001/R2002/R2005/R2008/R2012/R2013] and with FIXED DECIMAL
          formals [DECPOLY, MVI C,06].

          NO ?SVBLK appears here even for a RECURSIVE multi-formal procedure
          [R2008 rec(a,b) self-calls with a plain block copy], so the
          SVBLK trigger stays the written RECURSIVE ATTRIBUTE plus arity 1;
          attributed multi-formal recursion has no golden and refuses. *)
       let n = 1 + List.length rest in
       ignore f0;
       if pl.Bind.pl_attr_rec then
         failwith
           ("codegen: attributed RECURSIVE multi-formal activation unproven " ^
            "[TBD] (only unattributed recursion is sampled at arity >1 " ^
            "[R2008]; DR's SVBLK shape there has no golden)");
       d st op_lxi_d;
       reloc st Data (ptr0 + st.base);
       d st 0x0e; d st (2 * n);          (* MVI C,2N *)
       let loop = st.lc in
       d st 0x7e;                          (* MOV A,M *)
       d st 0x23;                          (* INX H   *)
       d st 0x12;                          (* STAX D  *)
       d st 0x13;                          (* INX D   *)
       d st 0x0d;                          (* DCR C   (0x05 would be DCR B) *)
       d st op_jnz; reloc st Code loop);
  let saved = st.vars and savedd = st.deref in
  st.vars <-
    List.map
      (fun (n, rt, o) ->
        (n,
         match rt with
         | Bind.RTbin p ->
             if p > 15 then
               failwith "codegen: FIXED BIN(>15) NOT IMP [TBD]"
             else
               { off = o; size = Bind.bytes_of rt; vk = Vint;
                 w = binw (if p <= 0 then 15 else p) }
         | Bind.RTdec (p, s) ->
             if p > 15 || p < 1 || s < 0 || s > p then
               failwith
                 (Printf.sprintf
                    "codegen: procedure-local FIXED DEC(%d,%d) outside the \
                     probed DEC band [TBD]" p s)
             else if
               List.mem_assoc (String.lowercase_ascii n) pl.Bind.pl_ptrs
             then
               (* [R709/R725, DECPOLY, R2037/R2038] DR passes a FIXED
                  DECIMAL formal BY REFERENCE: the formal owns a 2-BYTE
                  pointer cell (not the ceil((p+1)/2) BCD cell), and every
                  READ is `LHLD <ptr> ; MVI A,digits ; CALL ?DLDOP`, i.e. HL
                  arrives at ?DLDOP as the ADDRESS of the caller's decimal
                  [DECPOLY @10D: LHLD X A(004E) / MVI A,0F / CALL ?DLDOP].
                  Writes to a decimal formal have no golden and refuse in
                  lower_assign / the GET / PUT-EDIT paths. *)
               { off = o; size = 2; vk = Vdec (p, s); w = p + 3 }
             else
               { off = o; size = Bind.bytes_of rt; vk = Vdec (p, s);
                 w = p + 3 }
         | Bind.RTfloat p ->
             if p <> 24 then
               failwith
                 (Printf.sprintf
                    "codegen: procedure-local FLOAT BINARY(%d) precision unsupported [TBD] (only BINARY(24) is characterized)" p)
             else if
               List.mem_assoc (String.lowercase_ascii n) pl.Bind.pl_ptrs
             then
               (* [E2E-10/R3038] a FLOAT formal is passed BY REFERENCE exactly
                  like a decimal one: a 2-byte pointer cell, and every read is
                  `LHLD <cell>` used directly as the operand address
                  [R3038: LHLD Q A(0032) / PUSH H / LHLD Q A(0032) / POP D /
                  CALL ?FM44M].  Writes have no sample. *)
               { off = o; size = 2; vk = Vflt; w = 0 }
             else
               { off = o; size = Bind.bytes_of rt; vk = Vflt; w = 0 }
         | _ ->
             failwith "codegen: non fixed-bin procedure local [TBD]"))
      pl.Bind.pl_rows @ saved;
  st.deref <-
    (* recursive bodies read the SHADOW value cell with plain ladders
       [RFACT @80: LHLD I(12); DCX H — no deref] *)
    (if pl.Bind.pl_rec then [] else List.map fst pl.Bind.pl_ptrs);
  let savedp = st.in_proc and savedr = st.in_rec
      and saveddr = st.dec_ret and savedfr = st.float_ret in
  st.dec_ret <-
    (match pl.Bind.pl_ret with
     | Some (Bind.RTdec (p, s)) -> Some (p, s)
     | _ -> None);
  (* [E2E-10] RETURNS FLOAT selects the ?FPRET exit [R3038, FFACT] *)
  st.float_ret <-
    (match pl.Bind.pl_ret with Some (Bind.RTfloat _) -> true | _ -> false);
  st.in_proc <- true;
  st.in_rec <- pl.Bind.pl_rec;
  List.iter (fun x -> lower_stmt st ls x) pl.Bind.pl_body;
  st.dec_ret <- saveddr;
  st.float_ret <- savedfr;
  st.in_rec <- savedr;
  st.in_proc <- savedp;
  st.vars <- saved;
  st.deref <- savedd
and lower_stmt st (ls : lblstate) (s : Ast.stmt) =
  (* label prefixes resolve at the STATEMENT's LC [G115 loop:/done:] *)
  List.iter
    (fun (l : Ast.name) ->
      let nm = String.lowercase_ascii l.Ast.orig in
      ls.labs <- (nm, st.lc) :: ls.labs;
      let slots = List.filter (fun (k, _) -> k = nm) ls.fwd |> List.map snd in
      ls.fwd <- List.filter (fun (k, _) -> k <> nm) ls.fwd;
      match slots with
      | [] -> ()
      | [ one ] ->
          (* forward GOTO resolution: CHAIN-ADDR at label position [G115] *)
          link st t_chain_addr (Some (Code, one)) None
      | _ -> failwith "codegen: multiple forward GOTO per label chain                        unproven [TBD]")
    s.Ast.slabels;
  match s.Ast.st with
  | Ast.Sassign { lhs; rhs } ->
      st.lowered <- st.lowered + 1; lower_assign st lhs rhs
  | Ast.Sput _ ->
      st.lowered <- st.lowered + 1; st.last_imm <- None;
      (match match_put_edit s with
       | Some (its, specs) ->
           (* [E2E-8] PUT EDIT: the PUT LIST machinery plus the compiled format
              table (?EDITF) and ?EDTOV after every item [IFACT, R1001-R1020]. *)
           ignore specs;
           lower_put_items_gen st (Some (take_fmt_addr st)) None its
       | None ->
      (match match_put_list_lit s with
       | Plit (skipn, v) -> lower_put_lit st skipn v
       | Pcat (skipn, ch) -> lower_cat st skipn ch
       | Pitems (sk, its) -> lower_put_items st sk its
       | Pnone -> failwith
             (Printf.sprintf
                "codegen: PUT form not in E2E-3a subset [TBD] \
                 (line %d)" s.Ast.spos.Source.line)))
  | Ast.Sget _ ->
      st.lowered <- st.lowered + 1; st.last_imm <- None;
      (match match_get_list_var s with
       | Some nm -> lower_get st nm
       | None -> failwith
             (Printf.sprintf
                "codegen: GET form not in E2E-3e subset [TBD] \
                 (line %d)" s.Ast.spos.Source.line))
  | Ast.Sdowhile { cond; body } ->
      st.lowered <- st.lowered + 1; st.last_imm <- None;
      (* while(...) conditions arrive Econd-wrapped (IF conds don't) *)
      let cond = match cond.Ast.e with
                 | Ast.Econd x -> x
                 | _ -> cond
      in
      let head = st.lc in
      st.last_imm <- None;   (* [E2E-8] branch target => HL unknown *)
      if cond.Ast.e = Ast.Ebit "1" then begin
        (* constant-true bit condition = pure forever, NO test
           [Z404: COPY's DO WHILE('1'B)] *)
        lower_stmt st ls body;
        (d st op_jmp; st.last_imm <- None (* [R723] branch boundary *)); reloc st Code head;
        if not st.in_proc then begin
          (* WHILE('1'B): no test insn; tail address = the JMP
             operand address [head+4] [R408] *)
          st.after_forever <- true;
          st.last_loop_edge <- head + 4
        end
      end else begin
        let slot = lower_test_skip st cond in
        st.last_imm <- None;   (* [E2E-8] branch target => HL unknown *)
        lower_stmt st ls body;
        (d st op_jmp; st.last_imm <- None (* [R723] branch boundary *)); reloc st Code head;
        emit_triple st slot st.lc            (* [Z401: after JMP] *)
      end
  | Ast.Sdoforever body ->
      (* bare DO; .. END; [Z403] body then unconditional JMP back *)
      st.lowered <- st.lowered + 1; st.last_imm <- None;
      let head = st.lc in
      lower_stmt st ls body;
      (d st op_jmp; st.last_imm <- None (* [R723] branch boundary *)); reloc st Code head
  | Ast.Sdoto { ind; from; by; to_; while_; rep; body } ->
      st.lowered <- st.lowered + 1;
      (* open the suppression window at the TAIL ADDRESS before the
         loop lowers, so the increment's own evaluation position is
         visible [R414/R426: const-ident tail rungs] *)
      let window_open =
        st.after_forever && not st.in_proc
        && st.lc = st.last_loop_edge
      in
      let forever =
        match (to_, while_, rep, by) with
        | (None, None, Some _, _) -> true
        (* [E2E-8] DO index = c BY k; -- forever WITH a step [IFACT].  WITHOUT
           a step there is no loop at all [R1032], so no window. *)
        | (None, None, None, Some _) -> true
        | _ -> false
      in
      if forever && not st.in_proc then begin
        (* suppression window: tail address = where the loop's
           back-edge will end — the loop emits its 3-byte
           (LHLD + operand | LXI + imm) increment first, so the
           edge = lc after the increment [RFACT 0x4C, R414/R426
           0x1C, R401 0x1C, R427 0x1D] *)
        if not window_open then st.after_forever <- true;
        let inc_sz =
          match (by, to_) with
          | (None, None) -> 2 + 2 + 2   (* static bound triple *)
          | _ -> 19 / 8 land 0xff * 0 + 5
        in
        let inc_sz =
          match to_ with
          | Some { Ast.e = Ast.Enumber _; _ } -> 2 + 2 + 2
          | Some _ -> 5 + 2               (* dynamic: LHLD+SHLD temp *)
          | None -> 3 + 2                 (* increment LHLD + INX H
                                             (+INX for k=2: +1) *)
        in
        let k =
          match rep with
          | Some { Ast.e = Ast.Ebinary (Ast.Add, _,
                     { Ast.e = Ast.Enumber ck; _ }); _ } ->
              (try int_of_string (String.concat ""
                    (String.split_on_char '_' ck))
               with _ -> 1)
          | _ -> 1
        in
        st.last_loop_edge <- st.lc + 9 + 2 * k
      end;
      lower_doto st ls (fun st ls s -> lower_stmt st ls s)
        ind from by to_ while_ rep body
  | Ast.Sif { cond; then_; els } ->
      st.lowered <- st.lowered + 1; st.last_imm <- None;
      let skip = lower_test_skip st cond in
      lower_stmt st ls then_;
      (match els with
       | None -> emit_triple st skip st.lc
       | Some e ->
           (d st op_jmp; st.last_imm <- None (* [R723] branch boundary *));
           let exit_slot = st.lc in
           d st 0; d st 0;
           emit_triple st skip st.lc;      (* skip -> else start [G114] *)
           lower_stmt st ls e;
           emit_triple st exit_slot st.lc) (* fall-around else -> exit *)
  | Ast.Sgoto { tgt; subscript = [] } ->
      st.lowered <- st.lowered + 1; st.last_imm <- None;
      let nm = String.lowercase_ascii tgt.Ast.orig in
      (match List.assoc_opt nm ls.labs with
       | Some a -> (d st op_jmp; st.last_imm <- None (* [R723] branch boundary *)); reloc st Code a        (* backward [G115] *)
       | None ->
           (d st op_jmp; st.last_imm <- None (* [R723] branch boundary *));
           let slot = st.lc in
           d st 0; d st 0;
           ls.fwd <- (nm, slot) :: ls.fwd)              (* forward [G115] *)
  | Ast.Sgoto _ ->
      failwith "codegen: computed GOTO deferred [TBD]"
  | Ast.Sdobegin ss ->
      st.lowered <- st.lowered + 1;
      List.iter (fun x -> lower_stmt st ls x) ss
  | Ast.Sproc bs ->
      st.lowered <- st.lowered + 1; st.last_imm <- None;
      lower_proc st ls bs
  | Ast.Sreturn eo ->
      st.lowered <- st.lowered + 1; st.last_imm <- None;
      if st.float_ret then begin
        (* [E2E-10] a FLOAT function's exit.  A literal or cell result is
           pushed onto the float stack with ?FX44S; a computed one is already
           there.  Then ?RSBLK when the activation is recursive, then
           JMP ?FPRET.  Both halves are sampled: R3038 (nested, NOT
           recursive: no RSBLK) and FFACT (recursive: RSBLK on both exits). *)
        (match eo with
         | Some e -> fl_return_push st (fl_push st e)
         | None -> failwith "codegen: RETURN without value [TBD]");
        if st.in_rec then call_ext st "?RSBLK";
        d st op_jmp;
        st.last_imm <- None;
        let slot = st.lc in
        d st 0; d st 0;
        link st t_chain_ext (Some (Code, slot)) (Some "?FPRET")
      end else
      (match st.dec_ret with
       | Some ((_p, _s) as ps) ->
           (* [E2E-6/DFACT, R509] a DEC function returns the top of the
              decimal stack via JMP ?DCRET (not RET).  Base case of DFACT:
              LXI H,*S(000C); MVI A,0F; CALL ?DLDOP; CALL ?RSBLK;
              JMP ?DCRET -- the target-precision literal is exactly the
              dec_push rule used for assignments *)
           (match eo with
            | Some e -> ignore (dec_push st (Some ps) e)
            | None -> failwith "codegen: RETURN without value [TBD]");
           if st.in_rec then call_ext st "?RSBLK";
           (d st op_jmp; st.last_imm <- None (* [R723] branch boundary *));
           let slot = st.lc in
           d st 0; d st 0;
           link st t_chain_ext (Some (Code, slot)) (Some "?DCRET")
       | None ->
           (match eo with
            | Some e -> lower_hl st e
            | None -> failwith "codegen: RETURN without value [TBD]");
           (* every exit of a RECURSIVE activation restores its saved
              block first [RFACT: RSBLK @7C base-case AND @95 recursive] *)
           if st.in_rec then call_ext st "?RSBLK";
           d st 0xc9 (* RET [P401 code@41] *) )
  | Ast.Sstop eo ->
      st.lowered <- st.lowered + 1; st.last_imm <- None;
      (match eo with
       | Some _ -> failwith "codegen: STOP(code) deferred [TBD]"
       | None -> ());
      (* stop; sitting at the epilogue/proc append address (immediately
         after a no-exit loop, RFACT @0056) is NOT emitted when
         procedure code follows: the CALL ?STOPX cannot fit below
         appended procs [RFACT/R407/R408/R411/R415?? R415 HAS no
         procs -> emitted ✓; R401/R414/R419/R420/R423 anchored by
         intervening live stmts -> emitted ✓; R410/R421/R422/R424/
         R425 any proc (rec or not, call or not) -> suppressed ✓] *)
      (* [R415/R418/R414/R426 vs R401/R419/R423/R412] the suppression
         window is opened by a no-exit loop (REPEAT-without-WHILE,
         WHILE('1'B)) and closed by any other executable statement
         (put/assign/...); stop; lowering INSIDE the window emits
         NOTHING (its CALL cannot survive at the epilogue/proc
         append address); explicit stop; emitted in place also
         suppresses the epilogue CALL (stop_seen) [P401/R401]. *)
      (* stop; at an open window emits NOTHING: RFACT prints the
         statement at the append address (0056) with no code;
         R415/R418/R414/R426 confirm across proc/no-proc *)
      let at_tail = st.after_forever in
      if at_tail then ()
      else begin
        call_ext st "?STOPX";
        st.stop_seen <- true;
        if not st.in_proc then st.after_forever <- false
      end
      (* suppressed stop: window stays OPEN — trailing procedure
         code then displaces the epilogue entirely [RFACT] *)
  | Ast.Sprocedure_stmt _ ->
      failwith "codegen: CALL statement deferred [TBD]"
  | Ast.Sdcl _ -> ()
  | Ast.Snull _ -> ()
  | _ -> failwith
         (Printf.sprintf "codegen: statement kind not in supported subset \
                          [TBD] (line %d)" s.Ast.spos.Source.line)


let emit_program (progname : string) (auto_bytes : int)
    (rows : (string * var_info) list) (stmts : Ast.stmt list)
    (blk : Ast.block) =
  (* ---- Step-0 semantic-safety gate (corpus audit REV 2, D3 + D4) ----
     Two FAIL-SILENT holes were found by the 44-program sweep: block
     options other than OPTIONS(MAIN) (ACK: OPTIONS(MAIN,STACK(2000)))
     were parsed, stored and then dropped, and RETURNS(<non-FIXED type>)
     was mapped by Bind.rt_of_basic and then ignored by lowering (FFACT:
     RETURNS(FLOAT) emitted FIXED-shaped code, diverging at byte 48).
     Both are refused here, before a single byte is emitted.
     Whitelist is evidence-bounded, not convenience-bounded: all 83
     registered byte-exact specimens use exactly OPTIONS(MAIN) and
     RETURNS(FIXED) (verified over tools/e2e_gate.py's source list), so
     nothing already proven is affected.  *)
  let rt_is_implemented (r : Bind.rt) =
    match r with
    (* FIXED: 26 byte-exact specimens. FIXED DECIMAL(p,s) with p<=15:
       E2E-6 DEC core -- DEC(15,0) is pinned by DFACT's own $C trace and
       p=5/7/9/15 storage by R501-R512; DR itself says NOT IMP at p=31
       [R504], so anything wider stays refused. *)
    | Bind.RTbin _ -> true
    | Bind.RTdec (p, s) -> p >= 1 && p <= 15 && s >= 0 && s <= p
    (* [E2E-10] FLOAT BINARY(24) returns are implemented: the value is left on
       DR's float stack and the exit is JMP ?FPRET (+ ?RSBLK when recursive),
       proven by R3038 and FFACT.  Other precisions stay refused. *)
    | Bind.RTfloat 24 -> true
    | _ -> false
  in
  let check_returns (what : string) (line : int) (attrs : Ast.attr list) =
    match
      List.find_opt (fun (a : Ast.attr) -> String.equal a.akey "RETURNS")
        attrs
    with
    | Some a when a.Ast.atypes <> [] ->
        let r = Bind.rt_of_basic (List.hd a.Ast.atypes) in
        if not (rt_is_implemented r) then
          failwith
            ("codegen: " ^ what ^ " returns(" ^ Bind.rty_str r
             ^ ") deferred [TBD] (line " ^ string_of_int line
             ^ "; return types emitted today are FIXED [26 specimens], "
             ^ "FIXED DECIMAL(p<=15) [E2E-6] and FLOAT BINARY(24) [E2E-10]; "
             ^ "CHAR/BIT/POINTER/ENTRY each need their own ABI evidence)")
    | _ -> ()
  in
  let check_bopts (line : int) (opts : (string * Ast.expr list) list) =
    List.iter
      (fun (k, args) ->
        if not (String.equal (String.lowercase_ascii k) "main"
                && args = []) then
          failwith (Printf.sprintf
                      "codegen: block option %s%s deferred [TBD] (line %d; \
                       only OPTIONS(MAIN) is modelled; STACK/SEGMENTS and \
                       friends move code or data and no golden pins them)"
                      k (if args = [] then "" else "(...)") line))
      opts
  in
  let line_of_block (b : Ast.block) fb =
    match b.Ast.blabel with
    | Some n -> n.Ast.pos.Source.line
    | None -> (match b.Ast.bstmts with
               | s :: _ -> s.Ast.spos.Source.line
               | [] -> fb)
  in
  let rec check_block (b : Ast.block) (fb : int) =
    let ln = line_of_block b fb in
    check_bopts ln b.Ast.bopts;
    check_returns
      (match b.Ast.bname with
       | Some n -> "procedure " ^ n.Ast.orig
       | None -> "block") ln b.Ast.bsuffix;
    List.iter
      (fun (d : Ast.dcl) ->
        check_returns ("declaration " ^ d.Ast.dname.Ast.orig)
          d.Ast.dname.Ast.pos.Source.line d.Ast.dattrs)
      b.Ast.bdecls;
    List.iter (check_stmt ln) b.Ast.bstmts
  and check_stmt fb s =
    match s.Ast.st with
    | Ast.Sdcl ds ->
        List.iter
          (fun (d : Ast.dcl) ->
            check_returns ("declaration " ^ d.Ast.dname.Ast.orig)
              d.Ast.dname.Ast.pos.Source.line d.Ast.dattrs)
          ds
    | Ast.Sif { then_; els; _ } ->
        check_stmt fb then_;
        (match els with Some e -> check_stmt fb e | None -> ())
    | Ast.Sdobegin ss -> List.iter (check_stmt fb) ss
    | Ast.Sdoto { body; _ } -> check_stmt fb body
    | Ast.Sdowhile { body; _ } -> check_stmt fb body
    | Ast.Sdoforever b -> check_stmt fb b
    | Ast.Son { handler; _ } -> check_stmt fb handler
    | Ast.Selse b -> check_stmt fb b
    | Ast.Sproc bs -> check_block bs.Ast.blk bs.Ast.bpos.Source.line
    | _ -> ()
  in
  check_block blk 0;
  List.iter (check_stmt 0) stmts;
  let layout = Bind.bind_program blk in
  (* constant call arguments allocate 2B little-endian pool cells
     [P401: '2' at data@0]; included in the pool prescan total so
     pool-relative layout matches the lowering-time allocation run *)
  (* does callee `pn` have a FLOAT BINARY(24) formal at position i?  Used to
     size a numeric call argument's cell: a fixed formal takes the 2-byte
     integer pool cell, a FLOAT formal takes the 4-byte float pool cell that
     prescan_pool already demands through pdec_fl_expr [R3062].  Counting 2
     bytes for a float formal double-charged the literal and shifted every
     variable address in the program by 2. *)
  let formal_float_at pn i =
    match List.find_opt (fun (p : Bind.proc_layout) -> p.Bind.pl_name = pn)
            layout.pl_procs with
    | None -> false
    | Some pl ->
        (match List.nth_opt pl.Bind.pl_ptrs i with
         | Some (fn, _) ->
             (match List.find_opt (fun (k, _rt, _o) -> k = fn) pl.Bind.pl_rows
              with
              | Some (_, Bind.RTfloat 24, _) -> true
              | _ -> false)
         | None -> false)
  in
  let const_cells =
    List.fold_left
      (fun a (c : Bind.call_site) ->
        match c.cs_args with
        | [] -> a
        | args ->
            List.fold_left
              (fun acc (i, arg) ->
                match arg.Ast.e with
                | Ast.Enumber _ when not (formal_float_at c.cs_proc i) -> acc + 2
                | _ -> acc)
              a (List.mapi (fun i x -> (i, x)) args)
                  (* ACCUMULATE from the outer total: starting at 0 silently
                     dropped every call site but the last [regression caught by
                     R406/R421 byte parity] *)
      ) 0 layout.pl_calls
  in
  (* [E2E-6] prescan context for decimal literal cells: every block's
     variable kinds plus each procedure's decimal return type.  A name
     declared with two different types anywhere in the program would make
     a single global map ambiguous (and could mis-size the pool), so it is
     refused rather than guessed. *)
  let rt_to_vk (rt : Bind.rt) =
    match rt with
    | Bind.RTdec (p, s) -> Vdec (p, s)
    | Bind.RTchar (n, false) -> Vfix n
    | Bind.RTchar (n, true) -> Vvar n
    | Bind.RTfloat 24 -> Vflt
    | _ -> Vint
  in
  let proc_vk_rows =
    List.concat_map
      (fun (p : Bind.proc_layout) ->
        List.map (fun (n, rt, _o) -> (n, rt_to_vk rt)) p.Bind.pl_rows)
      layout.pl_procs
  in
  let pd_vars =
    let acc = ref ([] : (string * vkind) list) in
    List.iter
      (fun (n, vk) ->
        match List.assoc_opt n !acc with
        | Some v when v <> vk ->
            failwith
              (Printf.sprintf
                 "codegen: variable %s declared with conflicting kinds; \
                  decimal pool prescan needs one unambiguous type map [TBD]"
                 n)
        | _ -> acc := (n, vk) :: !acc)
      (proc_vk_rows @ List.map (fun (n, vi) -> (n, vi.vk)) rows);
    !acc
  in
  let pd_procs =
    List.map
      (fun (p : Bind.proc_layout) ->
        (p.Bind.pl_name,
         match p.Bind.pl_ret with
         | Some (Bind.RTdec (pp, ps)) -> Some (pp, ps)
         | _ -> None))
      layout.pl_procs
  in
  let pd_fl_procs =
    List.filter_map
      (fun (p : Bind.proc_layout) ->
        match p.Bind.pl_ret with
        | Some (Bind.RTfloat 24) -> Some p.Bind.pl_name
        | _ -> None)
      layout.pl_procs
  in
  let pool_total =
    prescan_pool { pd_vars; pd_procs; pd_ret = None
                    ; pd_dec = ref []; pd_fl = ref []; pd_fl_ret = false
                    ; pd_fl_procs }
                    stmts + const_cells
  in
  let st =
    { base = pool_total; items = []; pool = []
    ; pool_next = 0; fmtq = []; dec_cells = []; lc = 0; last_imm = None; lowered = 0; temps = 0
    ; stop_seen = false; calls = layout.pl_calls
    ; procs =
        List.map
          (fun (p : Bind.proc_layout) -> (p.pl_name, p))
          layout.pl_procs
    ; entries = []; fcalls = []; deref = []
    ; floor = layout.pl_total; vars = rows
    ; dec_ret = None
  ; float_ret = false
  ; fl_cells = []
    ; in_proc = false; in_rec = false
    ; after_forever = false; guards = 0; guard_slots = []
    ; appended = false; secs = layout.Bind.pl_secs
    ; last_loop_edge = 0 }
  in
  (* [E2E-8] DR allocates every PUT EDIT format table ahead of all other pool
     items [R1003/R1021/R1022], so the tables are reserved BEFORE any
     statement lowers. *)
  prealloc_fmt_tables st stmts;
  (* lower prologue + body + epilogue into st.items (code segment) *)
  d st op_lxi_b; d st 0x00; d st 0x02;
  d st op_call;
  let start_slot = st.lc in
  d st 0; d st 0;
  link st t_chain_ext (Some (Code, start_slot)) (Some "?START");
  let ls = { labs = []; fwd = [] } in
  List.iter
    (fun (s : Ast.stmt) ->
      (* [R423/ALL goldens] every procedure body is appended AFTER
         every main-block statement; DR layout with a live statement
         following an appended proc is unobserved -> fail loud *)
      if st.appended && not st.in_proc then
        (match s.Ast.st with
         | Ast.Sproc _ | Ast.Sdcl _ | Ast.Snull _ -> ()
         | _ -> failwith
                "codegen: main-block statement after an appended \
                 procedure [TBD: unproven DR append layout]");
      (* [R401/R414/R419/R420/R423] any main-block statement other
         than a no-exit loop or the trailing stop anchors the
         epilogue region and closes the suppression window; the
         append address advances past it *)
      if st.after_forever && not st.in_proc then begin
        (* append address advances while window open; ANCHORS
           (any stmt except loops/stop;/proc blocks) CLOSE it;
           Sproc does NOT [RFACT/R410/R425] *)
        (match s.Ast.st with
         | Ast.Sdoto _ | Ast.Sdowhile _ | Ast.Sdoforever _
         | Ast.Sstop _ | Ast.Sproc _ | Ast.Snull _ | Ast.Sdcl _ -> ()
         | _ -> st.after_forever <- false);
        st.last_loop_edge <- st.lc
      end;
      lower_stmt st ls s)
    stmts;
  (match ls.fwd with
   | [] -> ()
   | (nm, _) :: _ ->
       failwith (Printf.sprintf
                   "codegen: GOTO to undefined/unresolvable label %s \
                    [TBD: DR pass-2 UNDEF diag]" nm));
  (match st.fcalls with
   | [] -> ()
   | (nm, _) :: _ ->
       failwith (Printf.sprintf
                   "codegen: unresolved forward CALL to %s [TBD]" nm));
  if st.calls <> [] then
    failwith "codegen: unconsumed call-site cells [TBD]";
  (* DISCARD INVARIANT: every non-decl/non-null statement (at any
     nesting depth) must be accounted for by a lowering step. *)
  let req = List.fold_left (fun a s -> a + count_required s) 0 stmts in
  if req <> st.lowered then
    failwith
      (Printf.sprintf "codegen: DISCARD INVARIANT violated (%d required, \
                       %d lowered)" req st.lowered);
  (* explicit stop; inside the body REPLACES the epilogue CALL
     [P401: STOPX @26 emitted at the statement; no trailing call;
     programs without stop; keep the epilogue — 42 prior goldens] *)
  (* epilogue suppressed when the main block ends at a no-exit loop
     (RFACT/R410/R418: edge == final LC; procs or none [R418 proves
     the displacement alone suffices]) and whenever an explicit
     stop; was emitted in place (P401/R401) *)
  (* [RFACT/R407/R410/R411/R418/R425/R426/R427 vs R401/R412/R419/
     R423/R428/P404] the epilogue CALL is dropped exactly when the
     suppression window is still open at main-block end (trailing
     no-exit loop, no anchor after it) — procedure code BELOW does
     not change the window state, it just sits between the window
     address and the epilogue slot *)
  (* [R423] a guarded tail keeps the epilogue CALL (the guard JMP
     targets the CALL itself); plain open windows drop it *)
  let tail_displaced = st.after_forever in
  if not st.stop_seen && not tail_displaced then begin
    (* backpatch the tail-guard JMP operand(s) to THIS epilogue
       address [R404: @29 -> 0x44; P404: @10 -> 0x2B], immediately
       before the CALL bytes, then emit CALL ?STOPX *)
    List.iter (fun gs -> emit_triple st gs st.lc)
      (List.rev st.guard_slots);
    st.guard_slots <- [];
    d st op_call;
    let stop_slot = st.lc in
    d st 0; d st 0;
    link st t_chain_ext (Some (Code, stop_slot)) (Some "?STOPX")
  end;
  (* a guard whose JMP operand never got an epilogue to point at is
     an unobserved shape: fail loud rather than emit 3 dangling bytes *)
  if st.guard_slots <> [] then
    failwith
      "codegen: tail guard emitted without an epilogue CALL to chain \
       to [TBD: unproven DR shape (no-exit main tail AFTER an \
       appended procedure)]";
  let code_items = st.items in
  (* now build the ordered full item list *)
  let data_size =
    pool_total + max auto_bytes layout.pl_total + 2 * st.temps
  in
  (* [E2E-9, DECPOLY / LONGNAME] DR emits the program's external name in
     PROG-NAME / EXTDEF / DEF-PUBLIC TRUNCATED TO SIX CHARACTERS: the 7-char
     corpus program DECPOLY carries the symbol "DECPOL", and the 8-char
     probe label LONGNAME carries "LONGNA".  Internal procedure names never
     become symbols [NTEST1: `computeval` appears nowhere in the .REL], so
     two internals colliding on their first six characters is NOT an error
     [NTEST2: factor1/factor2 compile clean]. *)
  let extname =
    let u = String.uppercase_ascii progname in
    if String.length u > 6 then String.sub u 0 6 else u
  in
  let header =
    [ Link (t_progname, None, Some extname)
    ; Link (t_req_library, None, Some "PLILIB")
    ; Link (t_extdef, None, Some extname)
    ; Link (t_def_public, Some (Code, 0), Some extname) ]
  in
  let data_seg =
    if st.pool <> [] then
      Link (t_set_lc, Some (Data, 0), None)
      ::
      (let sorted =
         List.sort (fun (a, _) (b, _) -> compare a b) st.pool in
       (* each pool block: SET-LC(data,addr) for addr>0 then its bytes;
          block 0 rides the header SET-LC(data,0) [G113] *)
       List.concat_map
         (fun (addr, bs) ->
           (if addr > 0 then [Link (t_set_lc, Some (Data, addr), None)]
            else [])
           @ List.map (fun v -> Data (v land 0xff)) bs) sorted)
    else []
  in
  let bridge =
    [ Link (t_def_data_size, Some (Abs, data_size), None)
    ; Link (t_set_lc, Some (Code, 0), None) ]
  in
  let tail =
    [ Link (t_def_code_size, Some (Code, st.lc), None)
    ; Link (t_end_program, Some (Code, 0), None)
    ; Link (t_end_file, None, None) ]
  in
  (header @ data_seg @ bridge @ code_items @ tail, st.lc)

(* build var_info rows from binder rows, keeping only fixed-bin scalars.
   NOTE: storage byte-size comes ONLY from Bind.bytes_of (the binder is the
   single authority on layout) — codegen does not re-derive it.  Returns
   (progname, AUTO_BYTES excluding pool, vars). *)
let rows_of (b : Ast.block) =
  let rows = Bind.bind_rows b in
  let vars =
    List.filter_map
      (fun (nm, rt, off, _auto) ->
        match rt with
        | Bind.RTbin p ->
            if p > 15 then
              (* DR pass-1 rejects these outright ('NOT IMP',
                 N24/N305/N307: no .REL emitted) -- mirror the
                 perimeter boundary rather than compile what DR
                 cannot [C079] *)
              failwith
                (Printf.sprintf
                   "codegen: FIXED BIN(%d) NOT IMP on DR [TBD]" p);
            Some (nm, { off; size = Bind.bytes_of rt; vk = Vint;
                        w = binw (if p <= 0 then 15 else p) })
        | Bind.RTdec (p, s) ->
            (* DR accepts FIXED DECIMAL up to p=15 [R501-R512, DFACT];
               p=31 is DR's own pass-1 'NOT IMP' [R504: no .REL].  The
               band 16..30 is unpinned, so it stays a loud refusal
               rather than an extrapolated cell size. *)
            if p > 15 || p < 1 || s < 0 || s > p then
              failwith
                (Printf.sprintf
                   "codegen: FIXED DEC(%d,%d) outside the probed DEC band \
                    [TBD] (DR: NOT IMP at p=31 [R504]; exact 16..30 unknown)"
                   p s);
            Some (nm, { off; size = Bind.bytes_of rt; vk = Vdec (p, s)
                      ; w = p + 3 })
        | Bind.RTchar (n, false) ->
            Some (nm, { off; size = Bind.bytes_of rt; vk = Vfix n; w = 0 })
        | Bind.RTchar (n, true) ->
            Some (nm, { off; size = Bind.bytes_of rt; vk = Vvar n; w = 0 })
        | Bind.RTfloat p ->
            (* [E2E-10] the CELL is 4 bytes for every precision DR stores
               (R3001/R3013), but only binary(24) has a characterized value
               model, and plain `float` IS float binary(24) [R3001].  Other
               precisions stay refused so a binary(14) program can never
               silently get 24-bit arithmetic. *)
            if p <> 24 then
              failwith
                (Printf.sprintf
                   "codegen: FLOAT BINARY(%d) precision unsupported [TBD] (only BINARY(24) is characterized; R3013 proves the CELL is 4 bytes but not the computed precision)"
                   p);
            Some (nm, { off; size = Bind.bytes_of rt; vk = Vflt; w = 0 })
        (* Symbolic/non-storage kinds legitimately carry no lowering yet.
           Storage kinds outside the int subset must FAIL LOUD (C067
           policy: never silently drop constructs). *)
        | Bind.RTentry _ | Bind.RTlabel | Bind.RTformat
        | Bind.RTbuiltin | Bind.RTstruct _ -> None
        | _ -> failwith
                 (Printf.sprintf
                    "codegen: declared variable kind not in supported \
                     subset [TBD]: %s" (Bind.rty_str rt)))
      rows
  in
  let auto_bytes =
    List.fold_left (fun acc (_, vi) -> max acc (vi.off + vi.size)) 0 vars
  in
  let prog =
    match b.Ast.bname with Some n -> String.uppercase_ascii n.Ast.orig
                         | None -> failwith "codegen: main has no name"
  in
  (prog, auto_bytes, vars)
