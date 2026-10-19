(* lib/rel80.ml — LINK-80 .REL bitstream ENCODER.

   Faithful OCaml port of the machine-validated Python reference encoder in
   tools/rel_roundtrip.py (268/268 golden .REL files reproduce byte-exact).
   Bit layout per spec/notes/rel-format.md:
     absolute data byte   : 0  + <8-bit value>
     inline relocatable   : 10/110/111? -> 1 + <2-bit seg> + <16-bit LE value>
     link item            : 1 + 00 + <4-bit type> [+ value][+ name]
   Bits are emitted MSB-first; each byte packs bit7..bit0 MSB-first. *)

type seg = Abs | Code | Data | Common

let segn = function
  | Code -> 1 | Data -> 2 | Common -> 3 | Abs -> 0

type rel_item =
  | Data of int                         (* absolute byte at current LC *)
  | Reloc of seg * int                  (* inline relocatable 16-bit *)
  | Link of int * (seg * int) option * string option

(* bit writer: accumulate MSB-first bits, pack into bytes *)
type bw = { mutable bits : int list }   (* most-recent first via rev *)
let bw () = { bits = [] }
let put w n v =
  for i = n - 1 downto 0 do
    w.bits <- ((v lsr i) land 1) :: w.bits
  done
let put_str w s = String.iter (fun c -> put w 8 (Char.code c)) s
let pad_byte w = while List.length w.bits mod 8 <> 0 do w.bits <- 0 :: w.bits done

let bits_to_bytes bits =
  (* `put` prepends, so `bits` is in REVERSE emission order: head is the
     LAST bit written. Reverse to get true MSB-first order (head = first). *)
  let bs = Array.of_list (List.rev bits) in
  let n = Array.length bs in
  let out = Bytes.make ((n + 7) / 8) '\000' in
  for i = 0 to Bytes.length out - 1 do
    let v = ref 0 in
    for j = 0 to 7 do
      let k = i * 8 + j in
      let b = if k < n then bs.(k) else 0 in
      v := (!v lsl 1) lor b
    done;
    Bytes.set out i (Char.chr !v)
  done;
  out

let encode items =
  let w = bw () in
  List.iter
    (fun it ->
      match it with
      | Data v -> put w 1 0; put w 8 v
      | Reloc (seg, v) ->
          put w 1 1; put w 2 (segn seg);
          put w 8 (v land 0xff); put w 8 ((v lsr 8) land 0xff)
      | Link (t, valu, name) ->
          put w 1 1; put w 2 0; put w 4 t;
          (match valu with
           | Some (seg, v) when t >= 5 && t <= 14 ->
               put w 2 (segn seg);
               put w 8 (v land 0xff); put w 8 ((v lsr 8) land 0xff)
           | _ -> ());
          (match name with
           | Some nm when t <= 7 -> put w 3 (String.length nm); put_str w nm
           | _ -> ());
          if t = 14 then pad_byte w)
    items;
  bits_to_bytes w.bits

(* LINK item type codes (LINK-80 guide / reldump TYPES) *)
let t_extdef = 0
(* [E2E-11 step 2] FILE control blocks.  DR puts a `dcl f file;' variable in a
   NAMED COMMON group, not in DATA:  DEF-COMMON-SIZE(f, 34 + len f) establishes
   the group and its size, SEL-COMMON(f) makes it the active group for the
   relocations that follow (DR re-selects it before EVERY reloc into it, e.g.
   before the `LXI H,SYSIN' operand of an ON registration).  Both ride the
   generic LINK encoding -- type 1 carries no value, type 5 carries an ABS 16-bit
   size -- so no bit-layout work was needed, only the codes.
   Verified: SYSIN -> 39 bytes [FLTPOLY2, E11A, E11C, E11E, E11F],
             INF    -> 37 bytes [E17A].  Contents are 33 zero bytes, then the
             name LENGTH as a byte, then the name. *)
let t_sel_common = 1
let t_def_common_size = 5
let t_progname = 2
let t_req_library = 3
let t_chain_ext = 6
let t_def_public = 7
let t_def_data_size = 10
let t_set_lc = 11
let t_def_code_size = 13
let t_end_program = 14
let t_end_file = 15
let t_chain_addr = 12
