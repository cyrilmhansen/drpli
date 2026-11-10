(* ocaml/hir/sha256.ml — pure OCaml SHA-256 (E2E-54/P1-mD, PLAN §P1-mD.10 step 1).

   Self-contained, dependency-free implementation of the FIPS 180-4 SHA-256
   digest, used by the MIR backend to fingerprint the EXACT .mir bytes inside
   the sidecar debug map (§P1-mD.3). Nothing else in the HIR library depends on
   it; the historical pipeline never links this unit (F1 remedy: it lives in
   library pli80_hir, never in ocaml/bin).

   F8 vocabulary law (tools/hir_test.py, every ocaml/hir/*.ml after comment
   strip): the round constants and initial hash values are carried as a single
   SPACE-SEPARATED DECIMAL string parsed once at module init — there are NO
   hexadecimal literals in this file. The lowercase hex renderer uses only the
   two-digit Printf field widths below, never a raw 0-prefixed literal. *)

(* 32-bit truncation constants, written in decimal (never hexadecimal). *)
let mask32 = 4294967295
let two_pow32 = 4294967296

(* The 64 round constants — the first 32 bits of the cube roots of the first 64
   primes — carried as a space-separated decimal table parsed at init. *)
let round_rows =
  [ "1116352408 1899447441 3049323471 3921009573 961987163 1508970993 2453635748 2870763221"
  ; "3624381080 310598401 607225278 1426881987 1925078388 2162078206 2614888103 3248222580"
  ; "3835390401 4022224774 264347078 604807628 770255983 1249150122 1555081692 1996064986"
  ; "2554220882 2821834349 2952996808 3210313671 3336571891 3584528711 113926993 338241895"
  ; "666307205 773529912 1294757372 1396182291 1695183700 1986661051 2177026350 2456956037"
  ; "2730485921 2820302411 3259730800 3345764771 3516065817 3600352804 4094571909 275423344"
  ; "430227734 506948616 659060556 883997877 958139571 1322822218 1537002063 1747873779"
  ; "1955562222 2024104815 2227730452 2361852424 2428436474 2756734187 3204031479 3329325298"
  ]

(* The 8 initial hash values — the first 32 bits of the square roots of the
   first 8 primes — as the same decimal-table style. *)
let init_rows =
  [ "1779033703 3144134277 1013904242 2773480762 1359893119 2600822924 528734635 1541459225" ]

(* Parse a space-separated decimal table into an int array. *)
let parse_dec (rows : string list) : int array =
  rows
  |> String.concat " "
  |> String.split_on_char ' '
  |> List.filter (fun s -> String.length s > 0)
  |> List.map int_of_string
  |> Array.of_list

let k_table = parse_dec round_rows
let h_init = parse_dec init_rows

(* Bitwise helpers; every result is truncated to 32 bits. *)
let add32 x y = (x + y) land mask32
let sum32 (xs : int list) : int = List.fold_left add32 0 xs
let rot_r x n = ((x lsr n) lor ((x lsl (32 - n)) land mask32)) land mask32
let shr_r x n = (x lsr n) land mask32
let not32 x = (lnot x) land mask32

(* The six logical functions of the SHA-256 compression step (lowercase names). *)
let choice x y z = ((x land y) lxor (not32 x land z)) land mask32
let majority x y z = ((x land y) lxor (x land z) lxor (y land z)) land mask32
let big_sig0 x = (rot_r x 2) lxor (rot_r x 13) lxor (rot_r x 22)
let big_sig1 x = (rot_r x 6) lxor (rot_r x 11) lxor (rot_r x 25)
let small_sig0 x = (rot_r x 7) lxor (rot_r x 18) lxor (shr_r x 3)
let small_sig1 x = (rot_r x 17) lxor (rot_r x 19) lxor (shr_r x 10)

(* Big-endian word at byte index base of a byte-as-int array. *)
let word_at (data : int array) (base : int) : int =
  (data.(base) lsl 24)
  lor (data.(base + 1) lsl 16)
  lor (data.(base + 2) lsl 8)
  lor data.(base + 3)

(* Compress one 64-byte block into the running hash state (8 words, in place). *)
let compress (st : int array) (data : int array) (base : int) : unit =
  let w = Array.make 64 0 in
  for t = 0 to 15 do
    w.(t) <- word_at data (base + (4 * t))
  done;
  for t = 16 to 63 do
    w.(t)
      <- sum32
           [ small_sig1 w.(t - 2); w.(t - 7); small_sig0 w.(t - 15); w.(t - 16) ]
  done;
  let a = ref st.(0) in
  let b = ref st.(1) in
  let c = ref st.(2) in
  let d = ref st.(3) in
  let e = ref st.(4) in
  let f = ref st.(5) in
  let g = ref st.(6) in
  let h = ref st.(7) in
  for t = 0 to 63 do
    let t1 = sum32 [ !h; big_sig1 !e; choice !e !f !g; k_table.(t); w.(t) ] in
    let t2 = sum32 [ big_sig0 !a; majority !a !b !c ] in
    h := !g;
    g := !f;
    f := !e;
    e := add32 !d t1;
    d := !c;
    c := !b;
    b := !a;
    a := add32 t1 t2
  done;
  st.(0) <- add32 st.(0) !a;
  st.(1) <- add32 st.(1) !b;
  st.(2) <- add32 st.(2) !c;
  st.(3) <- add32 st.(3) !d;
  st.(4) <- add32 st.(4) !e;
  st.(5) <- add32 st.(5) !f;
  st.(6) <- add32 st.(6) !g;
  st.(7) <- add32 st.(7) !h

(* Pad the message: a 1 bit, then zeros, then the 64-bit big-endian bit width,
  so the byte length is a multiple of 64. Returns the padded byte-as-int array. *)
let pad (input : string) : int array =
  let msg_len = String.length input in
  let bit_len = msg_len * 8 in
  let zeros = ((56 - ((msg_len + 1) mod 64)) + 64) mod 64 in
  let total = msg_len + 1 + zeros + 8 in
  let data = Array.make total 0 in
  String.iteri (fun i c -> data.(i) <- Char.code c) input;
  data.(msg_len) <- 128;
  let hi = bit_len / two_pow32 in
  let lo = bit_len land mask32 in
  let tail = total - 8 in
  data.(tail) <- (hi lsr 24) land 255;
  data.(tail + 1) <- (hi lsr 16) land 255;
  data.(tail + 2) <- (hi lsr 8) land 255;
  data.(tail + 3) <- hi land 255;
  data.(tail + 4) <- (lo lsr 24) land 255;
  data.(tail + 5) <- (lo lsr 16) land 255;
  data.(tail + 6) <- (lo lsr 8) land 255;
  data.(tail + 7) <- lo land 255;
  data

(* The 32-byte digest as a lowercase hexadecimal string (64 characters). *)
let hex_digest (input : string) : string =
  let data = pad input in
  let st = Array.copy h_init in
  let blocks = Array.length data / 64 in
  for i = 0 to blocks - 1 do
    compress st data (i * 64)
  done;
  let out = Buffer.create 64 in
  for i = 0 to 7 do
    let w = st.(i) in
    Buffer.add_string out (Printf.sprintf "%02x%02x%02x%02x"
      ((w lsr 24) land 255) ((w lsr 16) land 255) ((w lsr 8) land 255) (w land 255))
  done;
  Buffer.contents out
