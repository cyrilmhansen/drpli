(* ocaml/proto/arch1.ml — ARCH-1 prototype driver.

   Encodes each hand-written plan into a .REL and compares the RAW BYTES against
   DR's golden.  Raw byte equality is the criterion (as everywhere else in this
   project); a decoded dump is only used to explain a difference, never to claim
   its absence.  It also reports the representation's bookkeeping: how many
   chain items were DERIVED from an operand class versus placed by hand, which is
   the measurement that decides whether the abstraction is carrying weight or
   just relabelling. *)

(* Rel80 lives inside the wrapped production library `pli80`; aliasing
   it keeps these prototype sources readable without a prefix on every line. *)
module Rel80 = Pli80.Rel80

(* Find the repo root by walking up until `golden/' exists, so the prototype
   runs from anywhere instead of depending on the caller's cwd. *)
let rec find_root dir =
  if Sys.file_exists (Filename.concat dir "golden") then dir
  else
    let parent = Filename.dirname dir in
    if parent = dir then dir else find_root parent

let root = find_root (Sys.getcwd ())

let read_file p =
  let ic = open_in_bin p in
  let n = in_channel_length ic in
  let s = Bytes.create n in
  really_input ic s 0 n;
  close_in ic;
  s

(* None == byte-identical (same length, no differing byte).  An early version
   returned Some n when the common prefix matched, which reported a *successful*
   comparison as "DIFFERS at byte 128 (mine=eof dr=eof)" -- a confusing way to
   lose an acceptance signal, and worth noting because a tool that reports success
   as failure trains you to distrust it. *)
let first_diff a b =
  if Bytes.length a <> Bytes.length b then
    Some (min (Bytes.length a) (Bytes.length b), true)
  else
    let n = Bytes.length a in
    let rec go i =
      if i >= n then None
      else if Bytes.get a i <> Bytes.get b i then Some (i, false)
      else go (i + 1)
    in
    go 0

let classify (path : string) (want : Bytes.t) (got : Bytes.t) =
  (* where does the first difference fall: header, code bytes, or link records *)
  Printf.sprintf "%s: mine=%dB dr=%dB" (Filename.basename path)
    (Bytes.length got) (Bytes.length want)

(* --emit DIR writes the prototype's .REL next to nothing but a scratch dir, so
   the decoded streams can be diffed against DR with tools/reldump.py.  Raw byte
   equality against the golden is still the criterion; the dump only explains a
   difference. *)
let emit_dir =
  let a = Array.to_list Sys.argv in
  let rec go i =
    if i + 1 >= List.length a then None
    else if List.nth a i = "--emit" then Some (List.nth a (i + 1))
    else go (i + 1)
  in
  go 0

let run (nm : string) (p : Inst80.program) (golden : string) =
  let items = Inst80.encode p in
  let raw = Rel80.encode items in
  (* pad to a 128-byte sector, exactly as bin/pli80c.ml does: DR writes .REL in
     CP/M sectors and pads with ZERO bytes (verified against E29A.REL, whose
     bytes past the last record are all 00).  This lives in the driver, not in
     inst80.ml, because it is a property of the file writer and not of the
     instruction representation -- one of the separations the prototype is
     checking for. *)
  let n = Bytes.length raw in
  let sectors = ((n + 127) / 128) * 128 in
  let got =
    if sectors = n then raw
    else begin
      let b = Bytes.make sectors '\000' in
      Bytes.blit raw 0 b 0 n;
      b
    end
  in
  let () =
    match emit_dir with
    | Some d ->
        let f = Filename.concat d (nm ^ ".REL") in
        let oc = open_out_bin f in
        output_string oc (Bytes.to_string got);
        close_out oc
    | None -> ()
  in
  let derived, placed =
    List.fold_left
      (fun (d, pl) ev ->
        match ev with
        | Inst80.Ins i ->
            (match i.Inst80.arg with
             | Some (Inst80.CallSym _) -> (d + 1, pl)
             | _ -> (d, pl))
        | Inst80.ChainItem _ -> (d, pl + 1)
        | _ -> (d, pl))
      (0, 0) p.events
  in
  if not (Sys.file_exists golden) then
    Printf.printf "%-6s NO GOLDEN at %s\n" nm golden
  else
    let want = read_file golden in
    match first_diff want got with
    | None ->
        Printf.printf
          "%-6s BYTE-IDENTICAL (%d bytes)  [chain items derived from operand \
           class: %d ; placed by hand: %d]%s\n"
          nm (Bytes.length want) derived placed
          (if placed > 0 then
             "   <-- the plan needed an escape hatch; see report below"
           else "")
    | Some (i, len_only) ->
        Printf.printf "%-6s %s at byte %d (mine=%s dr=%s)  %s\n" nm
          (if len_only then "LENGTH DIFFERS" else "DIFFERS") i
          (if i < Bytes.length got then
             Printf.sprintf "%02X" (Char.code (Bytes.get got i))
           else "eof")
          (if i < Bytes.length want then
             Printf.sprintf "%02X" (Char.code (Bytes.get want i))
           else "eof")
          (classify golden want got)

let () =
  Printf.printf "ARCH-1 prototype: symbolic 8080 + explicit relocation classes, \
                 threaded location counter, plan-owned ordering\n\n";
  Printf.printf "production comparison (unchanged, for reference):\n";
  Printf.printf "  codegen.ml emits bytes at 484 `d st' sites and calls \
                 `reloc st' at 94;\n";
  Printf.printf "  cstate carries 33 mutable fields, of which lc/items/pool are \
                 the\n";
  Printf.printf "  ones this prototype replaces with a fold over a plan.\n\n";
  List.iter
    (fun (nm, p, gold) -> run nm p gold)
    [
      ("E29A", Specimens.e29a,
       Filename.concat root "golden/e2e143/E29A/E29A.REL");
      ("E25F", Specimens.e25f,
       Filename.concat root "golden/e2e123/E25F/E25F.REL");
    ];
  Printf.printf "\nNothing here writes a file; the goldens are read-only \
                 inputs.\n"
