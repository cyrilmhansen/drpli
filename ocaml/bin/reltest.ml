(* bin/reltest.ml — validate the REL80 encoder against a known golden by
   replaying the exact decoded record list and comparing byte-for-byte. *)

open Pli80

let d v = Rel80.Data v
let r seg v = Rel80.Reloc (seg, v)
let lk t v nm = Rel80.Link (t, v, nm)

let p071a =
  [ lk Rel80.t_progname None (Some "PP071A")
  ; lk Rel80.t_req_library None (Some "PLILIB")
  ; lk Rel80.t_extdef None (Some "PP071A")
  ; lk Rel80.t_def_public (Some (Rel80.Code, 0)) (Some "PP071A")
  ; lk Rel80.t_def_data_size (Some (Rel80.Abs, 6)) None
  ; lk Rel80.t_set_lc (Some (Rel80.Code, 0)) None
  ; d 1; d 0; d 2; d 205; d 0; d 0
  ; lk Rel80.t_chain_ext (Some (Rel80.Code, 4)) (Some "?START")
  ; d 33; d 5; d 0; d 34
  ; r Rel80.Data 0
  ; d 42
  ; r Rel80.Data 0
  ; d 235; d 42
  ; r Rel80.Data 2
  ; d 25; d 43; d 34
  ; r Rel80.Data 4
  ; d 205; d 0; d 0
  ; lk Rel80.t_chain_ext (Some (Rel80.Code, 25)) (Some "?STOPX")
  ; lk Rel80.t_def_code_size (Some (Rel80.Code, 27)) None
  ; lk Rel80.t_end_program (Some (Rel80.Code, 0)) None
  ; lk Rel80.t_end_file None None
  ]

let () =
  let got = Rel80.encode p071a in
  let gl = Bytes.length got in
  let path = Sys.argv.(1) in
  let ic = open_in_bin path in
  let n = in_channel_length ic in
  let orig = really_input_string ic n in
  close_in ic;
  let cmp_len = min gl (String.length orig) in
  let rec first_diff k =
    if k >= cmp_len then -1
    else if Char.code (Bytes.get got k) <> Char.code (String.get orig k) then k
    else first_diff (k + 1)
  in
  let dd = first_diff 0 in
  let tail_ok =
    if gl > String.length orig then false
    else
      let allz = ref true in
      for k = gl to String.length orig - 1 do
        if String.get orig k <> '\000' then allz := false
      done;
      !allz
  in
  Printf.printf "encoded %d bytes; golden %d bytes\n" gl (String.length orig);
  Printf.printf "content match: %b (first_diff=%d tail_zero=%b)\n"
    (dd = (-1) && tail_ok) dd tail_ok;
  if dd <> (-1) || not tail_ok then exit 1
