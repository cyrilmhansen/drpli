(* Binder v1 — resolution pass + $S-compatible symbol-table dump.
   Ground truth: golden/bind*/S/*.s.txt (original compiler). Rules with
   evidence in spec/notes/parser-phase.md + CLAIMS C021-C024/C036-C038:

   - FIXED w/o spec => FIXED BINARY(15,0)
   - bytes: BIN<=15b -> 2 else 4; DEC p -> ceil((p+1)/2) BCD; FLOAT -> 4;
     CHAR n -> n; VARYING -> 1+n; BIT n -> ceil(n/8); FILE/static -> 0 auto
   - ONE automatic frame per PROCEDURE; DECLAREs nested in DO/BEGIN blocks
     share it and keep source order (P046: X Y W)
   - dump blocks exist only for procs (+ compile-unit block at line 1)
   - unit block storage = sum of OUTER static bytes (KEYFILE 31, CREATE 1);
     nested-proc statics are counted nowhere visible (P046 z)
   - symbols: flag 'a' unit entries/builtins; 'c' outer-block decls;
     'e' nested-proc block symbols
   - nested procedure statement => parent gets
     `c 0000 NAME ENTRY PARAMETERS(k) CONSTANT` after its dcl lines;
     own block follows depth-first
   - group levels: first numbered item opens STRUCTURE header (printed at
     its slot), higher-level items are `.NAME ... MEMBER` at running
     offsets; members inherit header STATIC
   - FILE => disp FILE, tail EXTERNAL STATIC (or INTERNAL STATIC)
   - external entry dcl => FUNCTION PARAMETERS(k) EXTERNAL CONSTANT *)

open Ast

(* parser's builtin table re-declared here for bare-ident detection
   [EX CREATE: `get list(addr)` registers ADDR BUILTIN] *)
let is_builtin_name k =
  List.mem k [ "LOG"; "LOG10"; "CHAR"; "DEC"; "ABS"; "ACOS"; "ADD"; "ADDR"; "ASIN"; "ATAN"; "ATAN2"; "BOOL"
             ; "CEIL"; "COPY"; "COS"; "DIVIDE"; "EXP"; "FIXED"; "FLOAT"
             ; "HBOUND"; "INDEX"; "LBOUND"; "LENGTH"; "LINENO"; "MAXIMUM"
             ; "MINIMUM"; "MOD"; "NULL"; "PAGENO"; "PRESENT"; "RANK"
             ; "ASCII"; "RELATE"; "SIGN"; "SIN"; "SQRT"; "SUMMARY"
             ; "TRANSLATE"; "TRUNC"; "VSIZE"; "ROUND"
             ; "LOG"; "LOG10"; "CHAR"; "DEC" ]

type rt =
  | RTbin of int | RTdec of int * int | RTfloat of int
  | RTchar of int * bool | RTbit of int | RTptr
  | RTfile of { internal : bool }
  | RTentry of { params : int; external_ : bool
               ; ret : rt option; ptypes : rt list }
  | RTlabel | RTformat | RTbuiltin
  | RTstruct of { level : int; members : int }

let rty_str = function
  | RTbin p -> Printf.sprintf "FIXED BINARY(%d,0)" p
  | RTdec (p, s) -> Printf.sprintf "FIXED DECIMAL(%d,%d)" p s
  | RTfloat p -> Printf.sprintf "FLOAT BINARY(%d,0)" p
  | RTchar (n, false) -> Printf.sprintf "CHAR(%d)" n
  | RTchar (n, true) -> Printf.sprintf "CHAR(%d) VARYING" n
  | RTbit n -> Printf.sprintf "BIT(%d)" n
  | RTptr -> "POINTER"
  | RTfile { internal } -> if internal then "FILE INTERNAL" else "FILE"
  | RTentry { params; external_; ret } ->
      Printf.sprintf "%s PARAMETERS(%d)"
        (if external_ || ret <> None then "FUNCTION" else "ENTRY") params
  | RTlabel -> "LABEL"
  | RTformat -> "FORMAT"
  | RTbuiltin -> "BUILTIN"
  | RTstruct { level; members } ->
      Printf.sprintf "STRUCTURE LEVEL %d, MEMBERS %d" level members

let num_arg0 = function
  | Some { e = Enumber t; _ } -> (try Some (int_of_string t) with _ -> None)
  | _ -> None

(* basic_type → rt for RETURNS/entry-param lists *)
let rec rt_of_basic (t : Ast.basic_type) : rt =
  match t with
  | Ast.Tfixed { dec; prec; scale } ->
      let q = match num_arg0 prec with Some x -> x | None -> 15 in
      if dec then RTdec (q, match num_arg0 scale with Some x -> x | None -> 0)
      else RTbin q
  | Ast.Tfloat { prec } ->
      RTfloat (match num_arg0 prec with Some x -> x | None -> 24)
  | Ast.Tchar { varying; len } ->
      RTchar ((match num_arg0 len with Some x -> x | None -> 1), varying)
  | Ast.Tbit { len } -> RTbit (match num_arg0 len with Some x -> x | None -> 1)
  | Ast.Tptr -> RTptr
  | Ast.Tfile -> RTfile { internal = false }
  | Ast.Tentry { opts } ->
      RTentry { params = List.length opts; external_ = false
              ; ret = None; ptypes = List.map rt_of_basic opts }
  | _ -> RTbin 15

and bytes_of = function
  | RTbin p -> (p + 8) / 8
      (* PROVEN [P063A $S ladder]: bytes = ceil((p+1)/8) incl. sign bit:
         1/7->1  8/9/15->2  16/17->3  24->4  32->5 *)
  | RTdec (p, _) -> (p + 2) / 2
  | RTfloat _ -> 4
  | RTchar (n, false) -> n
  | RTchar (n, true) -> 1 + n
  | RTbit n -> (n + 7) / 8
  | RTptr -> 2                                    (* [HYPOTHESIS] PROBE 57 *)
  | RTentry _ -> 0   (* entry/FUNCTION symbols show at 0000, no visible bytes *)
  | _ -> 0

let upper = String.uppercase_ascii

let has_attr (ds : attr list) k = List.exists (fun a -> String.equal a.akey k) ds

let num_arg = function
  | Some { e = Enumber t; _ } -> (try Some (int_of_string t) with _ -> None)
  | _ -> None

let resolve_type (d : dcl) : rt =
  match d.dtype with
  | Some (Tfixed { dec; prec; scale }) ->
      let p = match num_arg prec with Some p -> p | None -> 15 in
      if dec then RTdec (p, match num_arg scale with Some s -> s | None -> 0)
      else RTbin p
  | Some (Tfloat { prec }) ->
      RTfloat (match num_arg prec with Some p -> p | None -> 24)
  | Some (Tchar { varying; len }) ->
      RTchar ((match num_arg len with Some n -> n | None -> 1), varying)
  | Some (Tbit { len }) -> RTbit (match num_arg len with Some n -> n | None -> 1)
  | Some Tptr -> RTptr
  | Some Tfile -> RTfile { internal = has_attr d.dattrs "INTERNAL" }
  | Some (Tentry { opts }) ->
      let ret =
        match
          List.find_opt (fun (a : attr) -> String.equal a.akey "RETURNS")
            d.dattrs
        with
        | Some a when a.atypes <> [] -> Some (rt_of_basic (List.hd a.atypes))
        | _ -> None
      in
      RTentry { params = List.length opts
              ; external_ = has_attr d.dattrs "EXTERNAL"
              ; ret; ptypes = List.map rt_of_basic opts }
  | None ->
      if has_attr d.dattrs "LABEL" then RTlabel
      else if has_attr d.dattrs "FORMAT" then RTformat
      else RTbin 15

type sym = { flag : string; sname : string; disp : string; off : int }

let is_init_attr (d : dcl) =
  List.exists (fun (a : attr) ->
      List.mem a.akey [ "INIT"; "INITIALIZED"; "INITIAL" ]) d.dattrs

(* flatten the declaration items that contribute to a frame: bdecls is
   usually []; corpus keeps dcls as Sdcl statements, including inside
   DO/BEGIN groups (but NOT inside nested procedures) *)
let frame_decls (b : block) : (dcl * int) list =
  (* (item, source line of the DECLARE keyword) *)
  let out = ref [] in
  let rec st s =
    match s.st with
    | Sdcl items ->
        out := !out @ List.map (fun d -> (d, s.spos.Source.line)) items
    | Sdobegin ss -> List.iter st ss
    | Sdowhile { body } | Sdoto { body } ->
        (* body may be a group stmt or a single stmt *)
        (match body.st with Sdobegin ss -> List.iter st ss | _ -> st body)
    | Sif { then_; els; _ } ->
        st then_; Option.iter st els
    | Sproc _ -> ()          (* nested proc: its own block *)
    | _ -> ()
  in
  List.iter st b.bstmts;
  List.map (fun d -> (d, d.dname.pos.Source.line)) b.bdecls @ !out

(* layout one procedure block: returns (auto_bytes, syms, static_bytes) *)
let returns_attr (b : block) : rt option =
  match
    List.find_opt (fun (a : attr) -> String.equal a.akey "RETURNS") b.bsuffix
  with
  | Some a when a.atypes <> [] -> Some (rt_of_basic (List.hd a.atypes))
  | _ -> None

(* FUNCTION blocks pass params by reference: each declared parameter
   occupies a 2B slot dumped as `<type> PARAMETER` [EX FLTPOLY p:
   X/Y/Z @0,2,4 FLOAT PARAMETER, frame 6B] whereas procedures copy
   params as AUTOMATIC [EX P060B] *)
let layout ?(soff_start = 0) ?(isfn = false) (b : block) =
  let items = List.map fst (frame_decls b) in
  let off = ref 0 in
  (* STATIC area: separate running base; members/fields of static groups
     carry REAL offsets relative to it [EX P022 .B@0002, GRP2@0006].
     FORMAT descriptors occupy this area FIRST [EX P075A: S@0006 after
     6-byte format]. *)
  let soff = ref soff_start in
  let syms = ref [] in
  let statics = ref 0 in
  (* structured rows for the IR builder: (lower name, rt, offset, auto) *)
  let rows = ref [] in
  let push s = syms := s :: !syms in
  let head = ref None in   (* Some (level, offset) *)
  let members = ref [] in
  let mcnt = ref 0 in
  let hname = ref "" in
  let hlevel = ref 0 in
  let hstatic = ref false in
  let hoff = ref 0 in
  let flush () =
    match !head with
    | None -> ()
    | Some (hl, ho) ->
        push { flag = "c"; sname = !hname
             ; disp = Printf.sprintf "STRUCTURE LEVEL %d, MEMBERS %d %s"
                    hl !mcnt (if !hstatic then "STATIC" else "AUTOMATIC")
             ; off = ho };
        List.iter push (List.rev !members);
        head := None; members := []; mcnt := 0
  in
  List.iter
    (fun (item : dcl) ->
      match item.dpre with
      | Some _ -> ()
      | None ->
        let lvl =
          match item.dlevel with
          | Some { e = Enumber t; _ } -> (try int_of_string t with _ -> 0)
          | _ -> 0
        in
        let rt = resolve_type item in
        let explicit_static = has_attr item.dattrs "STATIC" in
        let filey = match rt with RTfile _ -> true | _ -> false in
        if lvl > 0 then begin
          (* group head (level <= open head) vs member (level > head) *)
          let starts_head =
            match !head with
            | None -> true
            | Some (hl, _) -> lvl <= hl
          in
          if starts_head then begin
            flush ();
            let ho = if explicit_static then !soff else !off in
            hstatic := explicit_static;
            hname := upper item.dname.orig;
            members := []; mcnt := 0;
            (* TYPELESS group heads occupy nothing [EX employee, record,
               grp]; heads with an explicit type reserve their size *)
            if item.dtype <> None && bytes_of rt > 0 then begin
              if explicit_static then begin
                head := Some (lvl, !soff); soff := !soff + bytes_of rt
              end else begin
                head := Some (lvl, !off); off := !off + bytes_of rt
              end
            end else head := Some (lvl, ho)
          end;
          (* head itself reserves nothing unless it has storage *)
          let is_head =
            match !head with Some (hl, _) -> lvl <= hl && !mcnt = 0 | None -> false
          in
          if is_head then begin
            (* head line materialized at flush; do not emit member *)
            ()
          end else begin
            incr mcnt;
            let sz = bytes_of rt in
            (* member offsets are BASE-RELATIVE [EX P022: GRP2@0006 but
               .C@0000]; the STRUCTURE line carries the absolute base *)
            let base =
              match !head with Some (_, ho) -> ho | None -> 0
            in
            let o = if !hstatic then begin
                      statics := !statics + sz;
                      let b0 = !soff in soff := !soff + sz; b0 - base
                    end else begin
                      off := !off + sz; !off - sz - base
                    end in
            members :=
              { flag = "c"; sname = "." ^ upper item.dname.orig
              ; disp = rty_str rt ^ " MEMBER"; off = o } :: !members
          end
        end
        else if
             isfn
             && List.exists
                  (fun (n : Ast.name) ->
                    String.equal
                      (String.lowercase_ascii n.orig)
                      (String.lowercase_ascii item.dname.orig))
                  b.bparams
             && not explicit_static
        then begin
          flush ();
          let o = !off in
          off := !off + 2;
          rows := (String.lowercase_ascii item.dname.orig, rt, o, true)
                  :: !rows;
          push { flag = "c"; sname = upper item.dname.orig
               ; disp = rty_str rt ^ " PARAMETER"; off = o }
        end
        else begin
          flush ();
          let entryy = match rt with RTentry _ -> true | _ -> false in
          let stc = explicit_static || filey || entryy
                    || (is_init_attr item && has_attr item.dattrs "STATIC") in
          let sz = bytes_of rt in
          let o =
            if stc then begin
              if sz > 0 && not filey && not entryy then begin
                let b0 = !soff in soff := !soff + sz; b0
              end else 0
            end
            else begin off := !off + sz; !off - sz end
          in
          if stc && sz > 0 && not filey && not entryy then statics := !statics + sz;
          let tail =
            match rt with
            | RTfile { internal } -> if internal then "FILE INTERNAL STATIC" else "FILE EXTERNAL STATIC"
            | RTentry { params; external_; ret } ->
                (* FUNCTION word requires RETURNS [EX ftc]; EXTERNAL from
                   attr OR returns-bearing free dcl [EX P079A: external,
                   no returns => ENTRY EXTERNAL; P079B: internal =>
                   ENTRY CONSTANT] *)
                Printf.sprintf "%s PARAMETERS(%d) %sCONSTANT"
                  (if ret <> None then "FUNCTION" else "ENTRY") params
                  (if external_ || ret <> None then "EXTERNAL " else "")
            | RTlabel -> "LABEL CONSTANT"
            | RTformat -> "FORMAT STATIC"
            | _ ->
                rty_str rt ^ " "
                ^ (if is_init_attr item then
                     (if stc then "INITIAL STATIC" else "INITIAL AUTOMATIC")
                   else if stc then "STATIC" else "AUTOMATIC")
          in
          rows := (String.lowercase_ascii item.dname.orig, rt, o,
                   not stc) :: !rows;
          push { flag = "c"; sname = upper item.dname.orig; disp = tail; off = o }
        end;
        (* entry dcl WITH returns ⇒ this is an external FUNCTION: DR emits
           a `.* <type> RETURNED` descriptor followed by one
           `.* <type> PARAMETER` per entry-arg, offsets sequential from 0
           in a private per-entry area [EX ANNUITY FTC: CHAR(17) VARYING
           RETURNED@0000 (18B), FLOAT PARAMETER@0012] *)
        (match rt with
         | RTentry { ret; ptypes; _ } ->
             let cur = ref 0 in
             Option.iter
               (fun (rr : rt) ->
                 push { flag = "c"; sname = ".*"
                      ; disp = rty_str rr ^ " RETURNED"; off = !cur };
                 cur := !cur + bytes_of rr)
               ret;
             List.iter
               (fun (pt : rt) ->
                 push { flag = "c"; sname = ".*"
                      ; disp = rty_str pt ^ " PARAMETER"; off = !cur };
                 cur := !cur + bytes_of pt)
               ptypes
         | _ -> ())
      )
    items;
  flush ();
  (!off, List.rev !syms, !statics, List.rev !rows)

(* ---------- format descriptors & labels (binder v2) [C052] ---------- *)
(* sizes: F/E items 6B, A 2B, controls(SKIP/PAGE/LINE) 2B, count prefix +3B,
   PICTURE = len(picspec)+7; data parentheses contribute NOTHING (only the
   format parens compile to a descriptor). Evidence: P065A/P074A-G grids,
   ANNUITY offsets 0000/0018/002F. *)
let rec fmt_sz items = List.fold_left (fun acc i -> acc + item_sz i) 0 items
and item_sz it =
  match it with
  | Pi_fmt { fkey; fargs = _; fcount } ->
      let base = match fkey with
        | "F" | "E" -> 6
        | "A" -> 2
        | "B" -> 2            (* [EX P076A: e+b+column=10] *)
        | "X" -> 2             (* [HYPOTHESIS] *)
        | _ -> 2               (* V I N M C COLUMN WIDTH: [HYPOTHESIS] *)
      in base + (match fcount with Some _ -> 3 | None -> 0)
  | Pi_pic s -> String.length s + 7
  | Pi_ctl (_, n) -> 2 + (match n with Some _ -> 0 | None -> 0)
  | Pi_remote _ -> 2          (* [HYPOTHESIS: r(lab) inline reference rec] *)
  | Pi_group is -> 2 + fmt_sz is
  | Pi_rep (_, _) -> 0 (* rep of data item: no format bytes [verify] *)
  | Pi_repgrp (c, is) -> 3 + fmt_sz is + (match c with { e = Eprefix _; _ } -> 0 | _ -> 0)
  | Pi_data _ -> 0

(* symbol lines for a block in statement order [(name, disp, size, _)].
   RULES [C052]:
   - labeled FORMAT stmt → symbol carries the label name [EX P073A
     `MONEY FORMAT STATIC`]; inline PUT/GET EDIT → `* FORMAT STATIC`;
   - `r(lab)` inside EDIT items → `* FORMAT BASED(LAB)`, 0 bytes [EX
     P073A/P075A: both at offset 0000, unit total counts format once];
   - plain statement labels → LABEL CONSTANT, offset 0000, no bytes;
     labels that ARE a proc/FORMAT name fold into their lines [EX P046
     golden has no `INNER LABEL`]. *)
let fmt_and_labels (b : block) =
  let out = ref [] in
  let push n t sz = out := (n, t, sz, 0) :: !out in
  let rec st (s : stmt) =
    (match s.st with
     | Sformat _ -> ()
     (* PROCEDURE labels fold into the ENTRY/FUNCTION line; BEGIN-block
        labels are ordinary statement labels [EX P077A LBL LABEL CONSTANT] *)
     | Sproc { blk = { bkind = Ast.Bproc; _ }; _ } -> ()
     | _ ->
       List.iter
         (fun (l : name) -> push l.orig "LABEL CONSTANT" 0)
         s.slabels);
    (match s.st with
     | Sformat items ->
         let nm =
           match s.slabels with
           | l :: _ -> String.uppercase_ascii l.orig
           | _ -> "*"
         in
         push nm "FORMAT STATIC" (fmt_sz items)
     | Sput { kind = Edit; items; _ } | Sget { kind = Edit; items; _ } ->
         let fsz =
           List.fold_left
             (fun acc i -> match i with Pi_data _ -> acc | _ -> acc + item_sz i)
             0 items
         in
         (* `r(lab)` refs compile to a BASED descriptor alone; any other
            items in the same format paren still emit STATIC [P073A/P075A:
            put edit(x)(r(money)) emits ONLY the BASED line, 0 bytes] *)
         if fsz > 0
            && not (List.exists (fun i -> match i with
                      | Pi_remote _ -> true | _ -> false) items)
         then push "*" "FORMAT STATIC" fsz;
         List.iter
           (fun i ->
             match i with
             | Pi_remote n ->
                 push "*"
                   ("FORMAT BASED(" ^ String.uppercase_ascii n.orig ^ ")")
                   0
             | _ -> ())
           items
     | Sdobegin ss -> List.iter st ss
     | Sdowhile { body; _ } | Sdoto { body; _ } ->
         (match body.st with Sdobegin ss -> List.iter st ss | _ -> st body)
     | Sif { then_; els; _ } -> st then_; Option.iter st els
     | Ast.Son { handler; _ } ->
         (match handler.st with
          | Sproc _ -> () (* begin-handler owns its descriptors in its own frame *)
          | _ -> st handler)
     | _ -> ())
  in
  List.iter st b.bstmts;
  List.rev !out

(* two-pass binder [v2]: discover FORMAT area program-wide FIRST
   (DFS pre-order of blocks, statement order inside each), then lay out
   each block with statics starting after the format area. *)
let rec bind_and_dump (blk : block) =
  let fmt_base = ref 0 in
  let total_static = ref 0 in
  let children (b : block) =
    let out = ref [] in
    let rec st s =
      match s.st with
      | Sproc { blk = inner; bpos } ->
          out := (inner, bpos.Source.line) :: !out
      | Sdobegin ss -> List.iter st ss
      | Sdowhile { body; _ } | Sdoto { body; _ } ->
          (match body.st with Sdobegin ss -> List.iter st ss | _ -> st body)
      | Sif { then_; els; _ } -> st then_; Option.iter st els
      | _ -> ()
    in
    List.iter st b.bstmts;
    List.rev !out
  in
  (* ordered dump nodes: real blocks + empty ON-handler frames.
     Anchors: procedures = their keyword line (refined to first dcl line
     in phase 2); BEGIN blocks = FIRST INNER STATEMENT line, END line when
     empty [EX P078A-D, P077B]; ON stmts = handler's first line [EX
     ANNUITY 29(on->begin)/30(inner put), P078B 6] *)
  let empty_blk =
    { blabel = None; bname = None; bparams = []; bopts = []
    ; bsuffix = []; bdecls = []; bstmts = []; bkind = Ast.Bdo
    ; bendpos = None }
  in
  let flat =
    let out = ref [] in
    let rec go (b : block) (anchor : int) =
      out := (b, anchor) :: !out;
      let rec st (s : stmt) =
        match s.st with
        | Sproc { blk = inner; bpos } ->
            let dflt = bpos.Source.line in
            let a =
              if inner.bkind = Ast.Bbegin then
                match inner.bstmts with
                | first :: _ -> first.spos.Source.line
                | [] ->
                    (match inner.bendpos with
                     | Some pp -> pp.Source.line
                     | None -> dflt + 1)
              else dflt
            in
            go inner a
        | Ast.Son { handler; _ } ->
            out := (empty_blk, handler.spos.Source.line) :: !out;
            (match handler.st with
             | Sproc _ -> st handler
             | _ -> st handler)
        | Sdobegin ss -> List.iter st ss
        | Sdowhile { body; _ } | Sdoto { body; _ } -> st body
        | Sif { then_; els; _ } -> st then_; Option.iter st els
        | _ -> ()
      in
      List.iter st b.bstmts
    in
    go blk 1;
    if Sys.getenv_opt "BIND_DEBUG" <> None then
      List.iteri
        (fun i (b, l) ->
          let d1 =
            match b.bstmts with
            | s :: _ ->
                Printf.sprintf " first=%d/%s" s.spos.Source.line
                  (match s.st with
                   | Ast.Sdcl _ -> "dcl"
                   | Ast.Sproc _ -> "proc/begin"
                   | Ast.Son _ -> "on"
                   | Ast.Sif _ -> "if"
                   | Ast.Sassign _ -> "assign"
                   | Ast.Sput _ -> "put"
                   | _ -> "?")
            | [] -> ""
          in
          prerr_endline
            (Printf.sprintf "DBG %d line=%d kind=%s n=%d%s" i l
               (match b.bkind with
                | Ast.Bproc -> "proc"
                | Ast.Bbegin -> "begin"
                | Ast.Bdo -> "do")
               (List.length b.bstmts) d1))
        (List.rev !out);
    List.rev !out
  in
  let plans = List.map (fun (b, ln) -> (b, ln, fmt_and_labels b)) flat in
  let fmt_total =
    List.fold_left
      (fun acc (_, _, fl) ->
        acc
        + List.fold_left
            (fun a (_n, t, sz, _l) -> if t = "FORMAT STATIC" then a + sz else a)
            0 fl)
      0 plans
  in
  let params_str (b : block) =
    match b.bparams with
    | [] -> ""
    | ps ->
        ", PARAMETERS "
        ^ String.concat ", " (List.map (fun n -> upper n.orig) ps)
  in
  let blocks : (int * int * string * sym list) list ref = ref [] in
  List.iter
    (fun (b, ln, fl) ->
      let auto, syms, statics, _rows =
        layout ~soff_start:fmt_total ~isfn:(returns_attr b <> None) b
      in
      (* unit-block storage totals ALL statics program-wide, incl. nested
         procs' [EX P046: z (2B) inside inner shows on BLOCK AT LINE 1] *)
      total_static := !total_static + statics;
      let anchor =
        match frame_decls b with (_, l) :: _ -> l | [] -> ln
      in
      let kids =
        List.filter (fun (inner, _) -> inner.bkind = Ast.Bproc) (children b)
      in
      let entry_lines =
        List.concat_map
          (fun (inner, _) ->
            let inm =
              match inner.bname with Some n -> upper n.orig | None -> "*"
            in
            let hd =
              { flag = "c"; sname = inm
              ; disp =
                  Printf.sprintf
                    "%s PARAMETERS(%d) CONSTANT"
                    (if returns_attr inner <> None then "FUNCTION" else "ENTRY")
                    (List.length inner.bparams)
              ; off = 0 }
            in
            match returns_attr inner with
            | Some rr ->
                let pt_rts =
                  List.map
                    (fun (n : Ast.name) ->
                      match
                        List.find_opt
                          (fun (d, _) ->
                            String.equal
                              (String.lowercase_ascii d.dname.orig)
                              (String.lowercase_ascii n.orig))
                          (frame_decls inner)
                      with
                      | Some (d, _) -> resolve_type d
                      | None -> RTbin 15)
                    inner.bparams
                in
                let cur = ref (bytes_of rr) in
                let descs =
                  { flag = "c"; sname = ".*"
                  ; disp = rty_str rr ^ " RETURNED"; off = 0 }
                  :: List.map
                       (fun (pt : rt) ->
                         let o = !cur in
                         cur := !cur + bytes_of pt;
                         { flag = "c"; sname = ".*"
                         ; disp = rty_str pt ^ " PARAMETER"; off = o })
                       pt_rts
                in
                hd :: descs
            | None -> [ hd ])
          kids
      in
      let flag = if b == blk then "c" else "e" in
      let syms = List.map (fun s -> { s with flag }) syms in
      let lsyms, fsyms =
        List.partition (fun (_ : sym) -> false) []
      in
      ignore (lsyms, fsyms);
      let mk =
        List.filter_map
          (fun (n, t, sz, _l) ->
            if t = "FORMAT STATIC" then begin
              let o = !fmt_base in
              fmt_base := !fmt_base + sz;
              Some { flag; sname = n; disp = t; off = o }
            end
            else if t = "LABEL CONSTANT" then
              Some { flag; sname = String.uppercase_ascii n; disp = t; off = 0 }
            else
              Some { flag; sname = n; disp = t; off = 0 })
          fl
      in
      blocks :=
        (anchor, auto, params_str b, syms @ entry_lines @ mk) :: !blocks)
    plans;
  (* builtins (sorted) + unit entry line *)
  let builtins = collect_builtins blk in
  let nm = match blk.bname with Some n -> upper n.orig | None -> "*" in
  let unit_syms =
    List.map
      (fun k -> { flag = "a"; sname = k; disp = "BUILTIN CONSTANT"; off = 0 })
      builtins
    @ [ { flag = "a"; sname = nm
        ; disp =
            Printf.sprintf "ENTRY PARAMETERS(%d) EXTERNAL CONSTANT"
              (List.length blk.bparams)
        ; off = 0 } ]
  in
  let buf = Buffer.create 1024 in
  let line s = Buffer.add_string buf (s ^ "\n") in
  let emit oline storage oparams syms =
    line
      (Printf.sprintf "BLOCK AT LINE %d, AUTO STORAGE %d BYTES%s" oline storage
         oparams);
    List.iter
      (fun (s : sym) ->
        line (Printf.sprintf "%s %04X %s %s" s.flag s.off s.sname s.disp))
      syms
  in
  emit 1 (!total_static + !fmt_base) "" unit_syms;
  List.iter
    (fun (oline, storage, oparams, syms) -> emit oline storage oparams syms)
    (List.rev !blocks);
  Buffer.contents buf

and collect_builtins (blk : block) =
  let acc = ref [] in
  let add k = acc := k :: !acc in
  let rec e (x : expr) =
    match x.e with
    | Ebuilt (k, args) when k <> "COMMA" && k <> "REPSPEC" -> add k; List.iter e args
    | Ebuilt (_, args) -> List.iter e args
    | Esuffix (f, args) -> e f; List.iter e args
    | Ebinary (_, a, b) -> e a; e b
    | Eprefix (_, a) -> e a
    | Econd a -> e a
    | Eqstruct (a, _) | Eqptr (a, _) -> e a
    | Eident { key; _ } when is_builtin_name key -> add key
    | _ -> ()
  in
  let rec opts os = List.iter (fun (o : io_opt) -> Option.iter e o.io_val) os in
  let rec fmtitems is =
    List.iter
      (fun (i : put_item) ->
        match i with
        | Pi_data x -> e x
        | Pi_fmt { fargs; _ } -> List.iter e fargs
        | Pi_rep (a, b) -> e a; e b
        | Pi_repgrp (_, is) -> fmtitems is
        | Pi_group is -> fmtitems is
        | Pi_ctl (_, Some x) -> e x
        | _ -> ())
      is
  in
  let rec st (s : stmt) =
    match s.st with
    | Sdcl items ->
        List.iter
          (fun (i : dcl) ->
            List.iter (fun (a : attr) -> List.iter e a.aargs) i.dattrs;
            Option.iter
              (fun x -> match x with Init_expr y -> e y | Init_rep (_, _) -> ())
              i.dinit;
            List.iter
              (fun (dd : dim) ->
                match dd with
                | Dim_bound (a, bo) -> e a; Option.iter e bo
                | Dim_star -> ())
              i.ddims)
          items
    | Sassign { lhs; rhs } -> e lhs; e rhs
    | Sif { cond; then_; els } -> e cond; st then_; Option.iter st els
    | Sdoto { from; by; while_; to_; rep; body; _ } ->
        e from; Option.iter e by; Option.iter e while_; Option.iter e to_;
        Option.iter e rep; st body
    | Sdowhile { cond; body } -> e cond; st body
    | Sdobegin ss -> List.iter st ss
    | Sproc { blk = inner } -> walk inner
    | Sput { on_opts; items; _ } -> opts on_opts; fmtitems items
    | Sget { on_opts; items; _ } -> opts on_opts; fmtitems items
    | Sfilestmt { opts = os; _ } -> opts os
    | Sedit { target; opts = os } -> e target; opts os
    | Sreadwv { to_ = x; _ } -> e x
    | Sreturn (Some x) | Sstop (Some x) -> e x
    | Son { handler; _ } -> st handler
    | Ssignal { target; _ } -> Option.iter e target
    | Sprocedure_stmt { target; args } -> e target; List.iter e args
    | Salloc { ptr; based } -> e ptr; Option.iter e based
    | Sfree es -> List.iter e es
    | Sgoto { subscript; _ } -> List.iter e subscript
    | Sassign_label { to_ = x; _ } -> e x
    | Sformat items -> fmtitems items
    | _ -> ()
  and walk b =
    List.iter (fun (a : attr) -> List.iter e a.aargs) b.bsuffix;
    List.iter st b.bstmts
  in
  walk blk;
  let seen = Hashtbl.create 8 in
  List.sort String.compare
    (List.filter
       (fun k -> if Hashtbl.mem seen k then false else (Hashtbl.add seen k (); true))
       !acc)

let dump_s = bind_and_dump

(* structured view for the IR builder: first (frame) block's rows *)
let bind_rows (blk : block) =
  let (_auto, _syms, _statics, rows) = layout blk in
  rows

(* ---------- [E2E-5c] whole-program call layout (additive view) ----------
   Rules extracted from DR bytes, P401/P402/RFACT ($S + $C + .REL
   deferred-pair records) [C080]:
     - caller block: named autos, then per call site in flow order one
     2B PARAM cell; an expression argument adds a 2B value temp right
     after its cell [P402: slot@A temp@C].
     - callee blocks follow their caller's cells (DFS, declaration
       order): first one 2B pointer cell per formal, then the block's
       named dcl rows (offsets keep bind_rows packing, shifted after
       the ptrs). A RECURSIVE callee's formal dcl cell IS the value
       'shadow' [P402: n@6 ptr, n@8 value]; a NON-recursive callee
       DEDUPS its formal dcl onto the ptr cell [P401 dbl: i@6 only].
     - nested-procedure RETURNED cells occupy no storage (result in
       HL) [P401 DATA=8; P402 DATA=0x0E].
   Additive view for codegen; the $S byte path is untouched. *)
type call_site =
  { cs_proc : string; cs_slot : int; cs_arg : Ast.expr
  ; cs_temp : int option }        (* Some addr iff arg is an expression *)

type proc_layout =
  { pl_name : string; pl_lbl : string option; pl_rec : bool
  ; pl_ptrs : (string * int) list             (* formal -> ptr cell *)
  ; pl_rows : (string * rt * int) list        (* body-visible rows *)
  ; pl_body : Ast.stmt list }

type prog_layout =
  { pl_calls : call_site list     (* DFS order, POOL-EXCLUSIVE offsets *)
  ; pl_procs : proc_layout list   (* DFS: parents before children *)
  ; pl_total : int }              (* non-pool data bytes *)

let pl_l (n : Ast.name) = String.lowercase_ascii n.Ast.orig

(* direct subexpressions, source order *)
let rec pl_kids (e : Ast.expr) : Ast.expr list =
  match e.Ast.e with
  | Ast.Esuffix (h, es) -> h :: es
  | Ast.Ebinary (_, a, b) -> [ a; b ]
  | Ast.Econd a | Ast.Eprefix (_, a) -> [ a ]
  | Ast.Eqstruct (a, _) | Ast.Eqptr (a, _) -> [ a ]
  | Ast.Ebuilt (_, es) -> es
  | _ -> []

(* calls to procs matching nm_of inside one expression (flow order).
   NOTE: the callee-operand position of Esuffix is a name, not a call,
   so `dbl(dbl(1))` would register only the inner [HYPOTHESIS corner;
   nested calls fail loud later at codegen pop-name assert]. *)
let pl_expr_calls nm_of (e : Ast.expr) =
  let out = ref ([] : (string * Ast.expr * Source.pos) list) in
  let rec go x =
    match x.Ast.e with
    | Ast.Esuffix (hd, args) -> begin
        match hd.Ast.e with
        | Ast.Eident h when nm_of (pl_l h) -> begin
            match args with
            | [ arg ] ->
                out := !out @ [(pl_l h, arg, x.Ast.epos)]; go arg
            | _ ->
                failwith
                  (Printf.sprintf
                     "bind: multi-arg call at line %d deferred [TBD]"
                     x.Ast.epos.Source.line)
          end
        | _ -> List.iter go (pl_kids x)
      end
    | _ -> List.iter go (pl_kids x)
  in
  go e; !out

let rec pl_stmt_calls (nm_of : string -> bool) (s : Ast.stmt) =
  let w e = pl_expr_calls nm_of e in
  let own =
    match s.Ast.st with
    | Ast.Sassign { lhs; rhs } -> w lhs @ w rhs
    | Ast.Sif { cond; _ } -> w cond
    | Ast.Sdowhile { cond; _ } -> w cond
    | Ast.Sdoto { from; by; to_; while_; rep; _ } ->
        w from @ (match by with Some b -> w b | None -> [])
        @ (match to_ with Some b -> w b | None -> [])
        @ (match while_ with Some b -> w b | None -> [])
        @ (match rep with Some b -> w b | None -> [])
    | Ast.Sreturn (Some e) | Ast.Sstop (Some e) -> w e
    | Ast.Sgoto { subscript; _ } -> List.concat_map w subscript
    | Ast.Sput { items; _ } | Ast.Sget { items; _ } ->
        List.concat_map
          (fun it ->
            match it with
            | Ast.Pi_fmt { fargs; fcount; _ } ->
                List.concat_map w fargs
                @ (match fcount with Some c -> w c | None -> [])
            | Ast.Pi_rep (a, b) -> w a @ w b
            | Ast.Pi_repgrp (a, _) -> w a
            | Ast.Pi_data e -> w e
            | Ast.Pi_ctl (_, Some e) -> w e
            | _ -> [])
          items
    | _ -> []
  in
  let kids =
    match s.Ast.st with
    | Ast.Sproc _ -> []      (* child blocks: separate DFS phase *)
    | Ast.Sif { then_; els; _ } ->
        pl_stmt_calls nm_of then_
        @ (match els with Some e -> pl_stmt_calls nm_of e | None -> [])
    | Ast.Sdobegin ss -> List.concat_map (pl_stmt_calls nm_of) ss
    | Ast.Sdowhile { body; _ } -> pl_stmt_calls nm_of body
    | Ast.Sdoforever body -> pl_stmt_calls nm_of body
    | Ast.Sdoto { body; _ } -> pl_stmt_calls nm_of body
    | _ -> []
  in
  own @ kids

let bind_program (blk : Ast.block) : prog_layout =
  let named_of (b : Ast.block) =
    List.map (fun (nm, rt, off, _a) -> (nm, rt, off)) (bind_rows b)
  in
  let rt_bytes rt = match rt with RTentry _ -> 0 | _ -> bytes_of rt in
  (* recursion: any call to `nm` anywhere inside block b's subtree *)
  let rec is_rec (nm : string) (b : Ast.block) =
    List.exists (fun s -> pl_stmt_calls (fun x -> x = nm) s <> [])
      b.bstmts
    || List.exists
         (fun s ->
           match s.Ast.st with
           | Ast.Sproc bs -> is_rec nm bs.Ast.blk
           | _ -> false)
         b.bstmts
  in
  let calls = ref ([] : call_site list) in
  let pls = ref ([] : proc_layout list) in
  (* two-phase: registry first so call matching sees real procedures;
     the first pass above is superseded by section2. *)
  let reg = ref ([] : (string * Ast.block * bool * string list) list) in
  let rec collect b =
    List.iter
      (fun (s : Ast.stmt) ->
        match s.Ast.st with
        | Ast.Sproc bs ->
            let pb = bs.Ast.blk in
            if pb.bkind = Ast.Bproc then begin
              let nm = pl_l (Option.get pb.bname) in
              let fm = List.map pl_l pb.bparams in
              if fm = [] then
                failwith (Printf.sprintf
                            "bind: procedure %s without formals [TBD]" nm);
              reg := !reg @ [(nm, pb, is_rec nm pb, fm)];
              collect pb
            end else collect pb
        | _ -> ())
      b.bstmts
  in
  collect blk;
  calls := []; pls := [];
  let names = List.map (fun (n, _, _, _) -> n) !reg in
  let is_proc nm = List.mem nm names in
  let rec section2 b base formals recf nm =
    let nf = List.length formals in
    if nm <> None && nf > 1 then
      failwith "bind: multi-formal procedures deferred [TBD]";
    let nr = named_of b in
    let dedup x =
      nf > 0 && List.mem x formals && nm <> None && not recf
    in
    let span =
      List.fold_left
        (fun m (x, rt, o) -> if dedup x then m else max m (o + rt_bytes rt))
        0 nr
    in
    let named_base = base + (if nm <> None then 2 * nf else 0) in
    let rows =
      List.map
        (fun (x, rt, o) ->
          if dedup x then
            let gi =
              match List.find_index (fun f -> f = x) formals with
              | Some i -> i | None -> 0
            in
            (x, rt, base + 2 * gi)
          else (x, rt, named_base + o))
        nr
    in
    let cur = ref (named_base + span) in
    let sites =
      List.map
        (fun (p, arg, _pos) ->
          let slot = !cur in
          cur := !cur + 2;
          let temp =
            match arg.Ast.e with
            | Ast.Enumber _ | Ast.Eident _ -> None
            | _ -> let t = !cur in cur := !cur + 2; Some t
          in
          { cs_proc = p; cs_slot = slot; cs_arg = arg; cs_temp = temp })
        (List.concat_map (fun s -> pl_stmt_calls is_proc s) b.bstmts)
    in
    calls := !calls @ sites;
    let after = !cur in
    (match nm with
     | Some pn ->
         pls := !pls
                @ [ { pl_name = pn
                    ; pl_lbl = (match b.blabel with
                                | Some l -> Some (pl_l l) | None -> None)
                    ; pl_rec = recf
                    ; pl_ptrs =
                        List.mapi (fun i f -> (f, base + 2 * i)) formals
                    ; pl_rows = rows
                    ; pl_body = b.bstmts } ]
     | None -> ());
    List.fold_left
      (fun acc (s : Ast.stmt) ->
        match s.Ast.st with
        | Ast.Sproc bs ->
            let pb = bs.Ast.blk in
            if pb.bkind = Ast.Bproc then begin
              let cn = pl_l (Option.get pb.bname) in
              match List.find_opt (fun (n, _, _, _) -> n = cn) !reg with
              | Some (_, _, r, fm) -> section2 pb acc fm r (Some cn)
              | None -> acc
            end else section2 pb acc [] false None
        | _ -> acc)
      after b.bstmts
  in
  let total = section2 blk 0 [] false None in
  { pl_calls = !calls; pl_procs = !pls; pl_total = total }
