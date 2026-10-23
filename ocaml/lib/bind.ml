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
  (* [E2E-26/P1] `dcl q based(p) fixed':  DR's own storage maps show the BASED name with NO
     storage of its own -- it prints at its POINTER's offset and the block's AUTO STORAGE excludes
     it (P063B: auto=4 = p+z; PB4: auto=4; P067C: auto=2 = p alone).  So a based declaration is a
     VIEW through a pointer cell, carrying the pointer's name and the value type, and it must
     contribute 0 bytes to the layout: giving it a cell would silently shift every later automatic
     and disagree with DR's DATA area (PB1 places the pointer BETWEEN two ordinary automatics, so a
     spurious cell would move `b'). *)
  | RTbased of string * rt
  | RTfile of { internal : bool }
  | RTentry of { params : int; external_ : bool
               ; ret : rt option; ptypes : rt list }
  | RTlabel | RTformat | RTbuiltin
  | RTstruct of { level : int; members : int }
  | RTbmem of string * int * rt
      (* [E2E-27/P2] a MEMBER of a level-numbered BASED structure: the associated pointer's name
         ("" for DR's BARE `based', where every access must be qualified), the record-relative
         offset, and the member's own type.  DR's map prints these as `.A FIXED BINARY(15,0)
         MEMBER' at the record offset [S1-S12], and the member has NO cell of its own: S1's
         AUTO STORAGE is 2 bytes -- just `declare p pointer' -- with the whole structure adding
         nothing. *)
  | RTstructrec of string * int
      (* the structure NAME itself -- what `allocate s set(p)', `free s' and `free p->s' name.
         Carries the associated pointer ("" = bare based) and the total record size, which is
         DR's measured ALLOCATE operand: S1 2, S2 4, S3 4, S6 5, S7 6, and REVERSE's
         wordnode = char(30) varying + pointer = 0x21 = 33 [golden/e2e319d 0065 LXI H,0021]. *)

let rec rty_str = function
  | RTbin p -> Printf.sprintf "FIXED BINARY(%d,0)" p
  | RTdec (p, s) -> Printf.sprintf "FIXED DECIMAL(%d,%d)" p s
  | RTfloat p -> Printf.sprintf "FLOAT BINARY(%d,0)" p
  | RTchar (n, false) -> Printf.sprintf "CHAR(%d)" n
  | RTchar (n, true) -> Printf.sprintf "CHAR(%d) VARYING" n
  | RTbit n -> Printf.sprintf "BIT(%d)" n
  | RTptr -> "POINTER"
  | RTbased (p, t) -> rty_str t ^ " BASED(" ^ String.uppercase_ascii p ^ ")"
      (* DR prints exactly this shape: `c 0000 Q FIXED BINARY(15,0) BASED(P)' [P063B, PB1-PB4, PB9] *)
  | RTfile { internal } -> if internal then "FILE INTERNAL" else "FILE"
  | RTentry { params; external_; ret } ->
      Printf.sprintf "%s PARAMETERS(%d)"
        (if external_ || ret <> None then "FUNCTION" else "ENTRY") params
  | RTlabel -> "LABEL"
  | RTformat -> "FORMAT"
  | RTbuiltin -> "BUILTIN"
  | RTbmem (p, k, t) ->
      rty_str t ^ " MEMBER OF BASED"
      ^ (if String.equal p "" then "" else "(" ^ String.uppercase_ascii p ^ ")@" ^ string_of_int k)
  | RTstructrec (p, sz) ->
      "STRUCTURE BASED"
      ^ (if String.equal p "" then "" else "(" ^ String.uppercase_ascii p ^ ")")
      ^ " SIZE " ^ string_of_int sz
  | RTstruct { level; members } ->
      Printf.sprintf "STRUCTURE LEVEL %d, MEMBERS %d" level members

let num_arg0 = function
  | Some { e = Enumber t; _ } -> (try Some (int_of_string t) with _ -> None)
  | _ -> None

(* [E2E-11 step 0] DR's own ceiling on FIXED precision, established by direct
   observation (E1415..E1432 / E15D09..E15D31, golden/e2e11f): PL/I-80 V1.4
   reports "NOT IMP" and emits NO .REL for any FIXED BINARY(p) or FIXED
   DECIMAL(p) with p > 15.  bin(15) and dec(15) compile; bin(16) does not.
   Before this check my compiler happily accepted bin(31) -- a false capability
   on the permissive side, which is the dangerous direction: it would have
   emitted bytes for a program DR refuses outright, and nothing in the corpus
   would ever have compared them.  Refuse loudly instead. *)
let dr_max_fixed_prec = 15

let check_fixed_prec (dec : bool) (p : int) =
  if p > dr_max_fixed_prec then
    failwith
      (Printf.sprintf
         "bind: FIXED %s(%d) exceeds DR's FIXED precision limit 15 \
          (PL/I-80 V1.4 says NOT IMP) [TBD]"
         (if dec then "DECIMAL" else "BINARY") p)
  else p

(* basic_type → rt for RETURNS/entry-param lists *)
let rec rt_of_basic (t : Ast.basic_type) : rt =
  match t with
  | Ast.Tfixed { dec; prec; scale } ->
      let q = check_fixed_prec dec
                  (match num_arg0 prec with Some x -> x | None -> 15) in
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
      (* RE-DERIVED LIVE [E19A, golden/e2e11k].  The previous citation was to
         "P063A", whose golden directory holds a .PLI entry but NO .REL, and
         whose source is gone -- an unverifiable claim, and its p>15 rows
         (16/17->3, 24->4, 32->5) were extrapolation, not measurement: DR
         refuses to compile those precisions at all.
         E19A declares fixed bin(1)..bin(15) in order and stores to each; the
         listing offsets give the exact ladder:
            b01..b07 -> 0x24,25,26,27,28,29,2A   (1 byte each, stored with STA)
            b08      -> 0x2B, b09 -> 0x2D        (2 bytes, stored with SHLD)
         so p<=7 -> 1 byte, 8<=p<=15 -> 2 bytes, which is (p+8)/8 for p<=15.
         Cross-checked on the decimal side by the same specimen:
            dec(1)->1  2,3->2  4,5->3  6,7->4  8,9->5  10,11->6  12,13->7
            14,15->8   = (p+2)/2 exactly, confirmed independently.
         Beyond p=15 nothing is claimable because nothing is compilable. *)
  | RTdec (p, _) -> (p + 2) / 2
  | RTfloat _ -> 4
  | RTchar (n, false) -> n
  | RTchar (n, true) -> 1 + n
  | RTbit n -> (n + 7) / 8
  | RTptr -> 2
      (* MEASURED, no longer a hypothesis [E2E-26/P1]: DR's maps put each POINTER automatic in a
         2-byte cell in DECLARATION ORDER -- P063B p@0000 z@0002; P086M p@0000 q@0002 z@0004;
         PB1 a@0000 p@0002 b@0004 (pointer cells are NOT hoisted to the front for locals; the
         pointer-cells-first rule belongs to FORMAL argument descriptors only [C130/C175]).  The
         cell holds a 16-bit data address, which is what `p = addr(z)' stores [LXI H,<DATA+off z>
         / SHLD <p>] and `LHLD <p>' reads.  The old citation was `[HYPOTHESIS] PROBE 57', whose
         probe has no .REL. *)
  | RTbmem (_, _, _) -> 0   (* a view into an allocated record, not a variable *)
  | RTstructrec (_, _) -> 0 (* the record type itself allocates nothing statically *)
  | RTbased (_, t) -> 0                     (* a view, not a variable -- see the type note above *)
  | RTentry _ -> 0   (* entry/FUNCTION symbols show at 0000, no visible bytes *)
  | _ -> 0

let upper = String.uppercase_ascii

(* attribute keys arrive in SOURCE case (R406 writes `recursive`, RFACT too),
   so the comparison must be case-insensitive -- [E2E-9] this is what made
   the RECURSIVE-attribute law silently depend on the call-graph fallback. *)
let has_attr (ds : attr list) k =
  List.exists (fun a -> String.uppercase_ascii a.akey = k) ds

let num_arg = function
  | Some { e = Enumber t; _ } -> (try Some (int_of_string t) with _ -> None)
  | _ -> None

let resolve_type_raw (d : dcl) : rt =
  match d.dtype with
  | Some (Tfixed { dec; prec; scale }) ->
      let p = check_fixed_prec dec
                  (match num_arg prec with Some p -> p | None -> 15) in
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

(* [E2E-26/P2] ONE place applies the BASED attribute, so sizing, printing and lowering can never
   disagree about it [C179].  `dcl q based(p) fixed' resolves to the value type wrapped with the
   pointer's name; DR's map line for it is `Q FIXED BINARY(15,0) BASED(P)' at p's offset with no
   storage [P063B, PB1-PB4, PB9, PB13-PB15].  Shapes that are not measured are refused here rather
   than given a plausible layout:
     - a BASED whose operand is not a bare identifier  (e.g. based(expr) -- no DR sample);
     - a based-on name that is not a declared POINTER in scope (PB16/ST11: `declare nb based(pn)
       nd' -- DR gives SYNTAX + BASED REQ, so naming a structure type through a based declaration
       is not a form in this dialect.  This is NOT a limit on based structures themselves, which
       DR accepts: see [E2E-27] below.)
     - a typeless based declaration (DR's own `BASED REQ' family, PB10/PB17).
   Note the pointer is resolved BY NAME, not by offset: DR reads the cell at every access, so a
   based view must follow whatever the pointer holds at that moment [PB3, PB22]. *)
let resolve_type (d : dcl) : rt =
  let rt = resolve_type_raw d in
  match List.find_opt (fun (a : attr) -> String.uppercase_ascii a.akey = "BASED") d.dattrs with
  | None -> rt
  | Some a ->
      let ptr =
        match a.aargs with
        | [ { e = Ast.Eident h; _ } ] -> String.lowercase_ascii h.Ast.orig
        | [] when d.dtype = None ->
            "" (* [E2E-27/P2] BARE `based' on a typeless structure head -- NETWORK's
                  `declare 1 city_node based' and S3/S4, all accepted by DR with a .REL.
                  The record has no associated pointer, so only qualified `p->member' access
                  is possible; the empty name is what marks that downstream. A bare BASED on a
                  declaration WITH a type (a scalar `q based fixed') has no DR sample, so it
                  falls through to the refusal below rather than getting a silent layout. *)
        | _ ->
            failwith
              ("codegen: BASED whose operand is not a bare pointer name [TBD] "
               ^ "(no DR sample: every accepted probe is based(<name>) -- P063B, P067C, PB1-PB4, "
               ^ "PB13-PB15)")
      in
      match rt with
      | RTlabel | RTformat | RTbuiltin | RTentry _ | RTfile _ ->
          failwith
            ("codegen: BASED(" ^ ptr ^ ") on a " ^ rty_str rt
             ^ " declaration has no DR sample [TBD].  [E2E-27 correction] an earlier draft of "
             ^ "this message claimed based STRUCTURES were refused by DR itself, on the strength "
             ^ "of PB10/PB16/PB17; that was wrong -- those were bad declaration spellings.  "
             ^ "REVERSE and NETWORK both compile, and ST1-ST10 reproduce level-numbered based "
             ^ "structures byte for byte.  What has no sample is a BASED on a label, format, "
             ^ "entry or file head.")
      | rt' ->
          (* the based-on pointer must be a declared POINTER somewhere DR will resolve; if it is not
             in this frame's symbols the view would silently read an unrelated cell, so refuse. *)
          RTbased (ptr, rt')

(* [E2E-27/P2] ONE place reads the BASED attribute of a STRUCTURE HEAD, so the layout walk, the
   member bindings and the record size all agree on which pointer a record belongs to [C179].
   Some "" is DR's bare `based' (NETWORK's city_node/route_node; S3, S4 accepted): the record has
   no associated pointer, so an unqualified member reference has no address to use and refuses at
   codegen -- DR's accepted spelling there is `p->member'.  Some p is `based(p)'. *)
let head_based (d : dcl) : string option =
  match
    List.find_opt (fun (a : attr) -> String.uppercase_ascii a.akey = "BASED") d.dattrs
  with
  | None -> None
  | Some a ->
      (match a.aargs with
       | [] -> Some ""
       | [ { e = Ast.Eident h; _ } ] -> Some (String.lowercase_ascii h.Ast.orig)
       | _ ->
           failwith
             "bind: BASED(...) on a structure head with a non-identifier operand has no DR sample [TBD] (S1-S12 and REVERSE/NETWORK use based(<pointer name>) or bare based)")

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
  (* [E2E-19] 1-D array metadata: (lower name, lower bound, upper bound,
     element bytes).  Filled by the SAME walk that computes offsets, so
     layout stays the single authority on storage: the only thing this adds
     is the element count, and the offset advance below uses it.  It is a
     separate list rather than a wider `rows' tuple because pl_rows is read
     at 7 sites in codegen.ml, none of which needs array info. *)
  let arrays = ref [] in
  let push s = syms := s :: !syms in
  let head = ref None in   (* Some (level, offset) *)
  let members = ref [] in
  let mcnt = ref 0 in
  let hname = ref "" in
  let hlevel = ref 0 in
  let hstatic = ref false in
  (* [E2E-27/P2] state for a level-numbered BASED structure head.  hbase is None for an ordinary
     (storage-bearing) structure and Some ptr for `1 s based(ptr)' / bare `1 s based'.  hmo runs the
     record-relative member offset and hsz accumulates the total record size, which is exactly the
     operand DR puts in `LXI H,<size>' before CALL ?ALLOP -- S1 2, S2 4, S3 4, S6 5 (fixed+bit+fixed,
     NO alignment padding), S7 6, REVERSE 33.  Accumulating the size here keeps ONE layout authority: nothing
     downstream re-derives offsets or the record size. *)
  let hbase = ref (None : string option) in
  let horig = ref "" in
  let hmo = ref 0 in
  let hsz = ref 0 in
  let hoff = ref 0 in
  let flush () =
    match !head with
    | None -> ()
    | Some (hl, ho) ->
        push { flag = "c"; sname = !hname
             ; disp =
                 (match !hbase with
                  (* DR prints a based head as `WORDNODE STRUCTURE LEVEL 1, MEMBERS 2
                     BASED(SENTENCE)' [REVERSE] and a BARE-based one as `NODE STRUCTURE LEVEL 1,
                     MEMBERS 2 BASED()' [S3] -- the empty parentheses are DR's own, not a
                     placeholder I invented. *)
                  | Some p ->
                      Printf.sprintf "STRUCTURE LEVEL %d, MEMBERS %d BASED(%s)" hl !mcnt
                        (String.uppercase_ascii p)
                  | None ->
                      Printf.sprintf "STRUCTURE LEVEL %d, MEMBERS %d %s" hl !mcnt
                        (if !hstatic then "STATIC" else "AUTOMATIC"))
             ; off = ho };
        List.iter push (List.rev !members);
        (* the structure NAME becomes addressable for ALLOCATE/FREE only once its size is known *)
        (match !hbase with
         | Some p when !mcnt > 0 && String.length !horig > 0 ->
             rows := (!horig, RTstructrec (p, !hsz), 0, false) :: !rows
         | _ -> ());
        head := None; members := []; mcnt := 0; hbase := None; hmo := 0; hsz := 0
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
            hbase := head_based item;
            horig := String.lowercase_ascii item.dname.orig;
            hmo := 0; hsz := 0;
            members := []; mcnt := 0;
            (* TYPELESS group heads occupy nothing [EX employee, record,
               grp]; heads with an explicit type reserve their size.  A BASED head
               reserves NOTHING even when it has a type: the whole record lives at the
               pointer's target, which S1 proves with AUTO STORAGE 2 for `declare p
               pointer' plus a 2-byte structure. *)
            if !hbase = None && item.dtype <> None && bytes_of rt > 0 then begin
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
          end else if !hbase <> None then begin
            (* [E2E-27/P2] a member of a BASED structure: offset accumulates in the RECORD, not in
               the frame.  DR lays members out CONTIGUOUSLY with no alignment padding -- S6 is
               fixed(0..1), bit(2), fixed(3..4) with a 2-byte member at the ODD offset 3, and
               allocation size 5 -- so `mo + bytes_of' is the whole rule and anything that inserted
               padding would change both the offsets and the ALLOCATE operand. *)
            incr mcnt;
            let sz = bytes_of rt in
            let mo = !hmo in
            hmo := mo + sz;
            hsz := !hsz + sz;
            (match !hbase with
             | Some pp ->
                 rows :=
                   (String.lowercase_ascii item.dname.orig,
                    RTbmem (pp, mo, rt), 0, false)
                   :: !rows
             | None -> ());
            members :=
              { flag = "c"; sname = "." ^ upper item.dname.orig
              ; disp = rty_str rt ^ " MEMBER"; off = mo } :: !members
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
          (* [E2E-19/Priority 1] ONE-DIMENSIONAL ARRAY SIZING.
             DR's measured rule (AB1: `dcl a(5) fixed' occupies data 0000-0009
             and the NEXT scalar lands at 000A):
                 storage = element_bytes * (ub - lb + 1),  default lb = 1
             Everything outside the characterized subset refuses loudly instead
             of sizing on a guess -- an under-sized array silently overlaps the
             next variable, which is exactly the C162 failure class. *)
          let elem_sz = bytes_of rt in
          let nelem, lb, ub =
            match item.ddims with
            | [] -> (1, 1, 1)
            | [Ast.Dim_bound (lo_e, hi_opt)] ->
                (* `a(5)' is ONE bound meaning upper, with lb defaulting to 1;
                   `a(0:3)' is LOWER:UPPER.  The parser stores the first
                   expression as the bound-before-the-colon, so a single
                   dimension is (ub, None) and an explicit pair is (lb, Some ub)
                   -- AR3 `a(1:5)' vs AR4 `a(0:3)' pin this against DR. *)
                let cint x =
                  match x.Ast.e with
                  | Ast.Enumber t ->
                      (match int_of_string_opt
                             (String.concat "" (String.split_on_char '_' t)) with
                       | Some v -> v
                       | None ->
                           failwith
                             ("codegen: [TBD] array bound '" ^ t
                              ^ "' is not a decimal literal [C159]"))
                  | _ ->
                      failwith
                        "codegen: [TBD] non-constant array dimension [C159] \
                         (only literal bounds are sizeable at bind time)"
                in
                let ubv = match hi_opt with
                          | Some x -> cint x
                          | None -> cint lo_e
                in
                let lbv = match hi_opt with
                          | Some _ -> cint lo_e
                          | None -> 1
                in
                if ubv < lbv then
                  failwith "codegen: [TBD] array upper bound below lower bound";
                (ubv - lbv + 1, lbv, ubv)
            | _ ->
                failwith
                  "codegen: [TBD] multi-dimensional or assumed-size array \
                   [C159] (DR's 2-D is row-major, last subscript fastest -- \
                   characterized, not implemented)"
          in
          if nelem > 1 then begin
            if elem_sz <> 2 then
              failwith
                ("codegen: [TBD] array of " ^ string_of_int elem_sz
                 ^ "-byte elements [C159] (only FIXED BINARY(15) / typeless \
                    FIXED, i.e. 2-byte elements, are measured; DECIMAL, FLOAT, \
                    BIT and CHARACTER arrays refuse)");
            if stc then
              failwith
                "codegen: [TBD] STATIC array is not independently characterized \
                 [C159/AB5] (AB5 shows DR places it below the pool, but that probe \
                 also carries the pre-existing STATIC-on-fixed-bin refusal)";
            arrays := (String.lowercase_ascii item.dname.orig, lb, ub, elem_sz)
                      :: !arrays
          end;
          let sz = elem_sz * nelem in
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
  (!off, List.rev !syms, !statics, List.rev !rows, List.rev !arrays)

(* ---------- format descriptors & labels (binder v2) [C052] ---------- *)
(* sizes: F/E items 6B, A 2B, controls(SKIP/PAGE/LINE) 2B, count prefix +3B,
   PICTURE = len(picspec)+7; data parentheses contribute NOTHING (only the
   format parens compile to a descriptor). Evidence: P065A/P074A-G grids,
   ANNUITY offsets 0000/0018/002F. *)
(* [E2E-8] the parser now keeps a PUT/GET EDIT statement's FORMAT half in its
   own node (Ast.Pi_fmtlist) so codegen can tell the DATA list from the FORMAT
   list.  The binder's descriptor model predates that boundary and counted the
   two halves as one flat item list [P062A/P065A/P074A-G FORMAT grids, $S byte
   parity], so every binder-side consumer of a statement's items flattens it
   back first -- otherwise FORMAT sizes would silently change. *)
let rec flatten_items is =
  List.concat_map
    (function
      | Ast.Pi_fmtlist inner -> flatten_items inner
      | i -> [ i ])
    is

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
  (* [E2E-8] Ast.Pi_fmtlist is the PUT-statement wrapper that keeps the DATA
     half separate from the FORMAT half.  It never appears inside a FORMAT
     STATIC descriptor, and there is no DR sample of what its descriptor size
     would be, so refuse rather than invent a size. *)
  | Pi_fmtlist _ ->
      failwith "bind: nested FORMAT LIST inside a FORMAT STATIC descriptor \
                unproven [TBD]" 

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
         let items = flatten_items items in
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
      let auto, syms, statics, _rows, _arrays =
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
        (* [E2E-8] the PUT EDIT format half: walk it like a group so no
           replication/skip expression inside it goes uncollected *)
        | Pi_fmtlist is -> fmtitems is
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
    | Sput { on_opts; items; _ } -> opts on_opts; fmtitems (flatten_items items)
    | Sget { on_opts; items; _ } -> opts on_opts; fmtitems (flatten_items items)
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
  let (_auto, _syms, _statics, rows, _arrays) = layout blk in
  rows

(* [E2E-19] array metadata for a block, from the SAME `layout' walk that
   computes every offset.  Re-running layout is not a second allocator: it is
   one function, called twice, producing two views of one model. *)
let bind_arrays (blk : block) =
  let (_auto, _syms, _statics, _rows, arrays) = layout blk in
  arrays

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
(* [E2E-11 step 5] Does the OUTERMOST block name a procedure that is NOT the
   program entry point?  DR compiles such a file as a plain callable module:
   corpus program `A' (a: procedure(x) returns (float)) has no `LXI B,0200 /
   CALL ?START' prologue at all, still carries LINK-DEF-PUBLIC code 0000 A, and
   its entry sequence is the ordinary procedure copy-in (`5E 23 56 EB' + SHLD of
   the incoming pointer) followed by `JMP' + CHAIN-EXT ?FPRET for the FLOAT
   return [C136, golden/first/A].  The distinguishing feature is the ABSENCE of
   OPTIONS(MAIN), not the absence of a name: every accepted specimen's outermost
   block is a named procedure too, it just says options(main).

   This is exported as ONE predicate because both layout passes have to agree
   about it -- codegen's rows_of (auto-area size + variable offsets) and
   bind_program (per-section pointer cells).  Two copies of the question is
   exactly the C134 failure mode: if one said "procedure" and the other said
   "main", the DATA size and the offsets would come from different models and
   the addresses would disagree quietly. *)
let top_is_proc (b : Ast.block) : bool =
  b.Ast.bkind = Ast.Bproc
  && b.Ast.bname <> None
  && not
       (List.exists
          (fun (k, args) ->
            String.equal (String.lowercase_ascii k) "main" && args = [])
          b.Ast.bopts)

type call_site =
  { cs_proc : string; cs_slot : int; cs_args : Ast.expr list
  ; cs_temps : int option list }  (* Some addr iff that arg is an expression *)

(* ---------- [E2E-34/P1, E2E-36/P2] label ownership, references and recovery-pad demand ----------
   ONE scan, exported, used by bind (which allocates the hidden saved-SP cell) and by
   codegen (which decides which labels carry a recovery pad, which labels are visible from
   where, and which names are procedure entries and therefore NOT GOTO-able).  Layout demand
   and instruction emission must agree or the DATA area shifts under the code [C179], and a
   property written out twice drifts [C202].

   [E2E-36] rewrote the DEMAND rule.  The pre-E36 version asked "does an ON ... GOTO written
   in this block name label L" and gave THIS block the cell and the pad.  That was true of
   every one of the 884 specimens because every ON-unit in them named a label of its own
   block -- and it is false [C167].  E35Y3, E36T2-T8, E36T13 and E36T14 (13 DR goldens) say
   the pad and the cell follow the block that OWNS the label, whoever points at it:

     * a label is pad-bearing if an ON-unit's GOTO handler names it, from any block that can
       see it (E36T13: a nested procedure's `on endfile(sysin) goto sk;' gives MAIN the cell
       and pads MAIN's `sk:', with no ON-unit anywhere in main -- DATA 6, pad at 0013);
     * or a plain GOTO names it from a DIFFERENT block (E35Y3: nested `goto sk;' to main's
       label, no ON-unit in the program at all -- DATA 6, main gets the cell, pad at 0013);
     * a plain GOTO from the owning block does NOT pad (E36T11/T12, byte-exact with no cell
       and no pad: DATA 4) -- so the same-block orientation is what makes the rule need the
       "who references it" input at all.

   E36T15/T16/T17 add a second boundary: `GOTO <procedure entry label>' is rejected by DR
   itself with `NOT LABEL' (1 ERROR IN PASS 2, no .REL), in the same-block orientation too
   (T17 is main jumping to its own `sub:'), so a procedure name is not a transfer target and
   the plan exports the entry-label set to make codegen say so. *)
type ref_kind = Rk_on | Rk_plain

type on_facts =
{ of_labels : string list (* labels OWNED by this block that carry a recovery pad [E2E-36] *)
; of_goto : bool          (* = of_labels <> []: this block saves SP at entry *)
; of_any : bool           (* an ON-unit is WRITTEN here -> ?OFCOP on a procedure tail [C209] *)
; of_own : string list    (* statement labels defined at this block level, incl. nested BEGINs
                             of the SAME block [C228] *)
; of_procs : string list  (* nested procedure entry labels: visible, but NOT GOTO-able [E36T17] *) }

(* The block that owns a label is the block whose statements define it.  A nested DO/IF/BEGIN
   group does NOT own labels separately -- E36T5 puts the referencing GOTO inside `do; ... end;'
   and the pad still belongs to main, exactly as NETWORK:145's ON inside two DO WHILEs belongs
   to print_paths.  Descent stops at Ast.Sproc, because a nested procedure DOES own its labels
   (E35X1/E35X4: the nested `hd:' shadows main's, [C228]). *)
let lbl (x : Ast.name) = String.lowercase_ascii x.Ast.orig

let rec own_labels_stmts (ss : Ast.stmt list) =
  List.concat_map own_labels_stmt ss
and own_labels_stmt (s : Ast.stmt) =
  let here = List.map lbl s.Ast.slabels in
  let deeper =
    match s.Ast.st with
    | Ast.Sdobegin ss -> own_labels_stmts ss
    | Ast.Sif { then_; els; _ } ->
        own_labels_stmt then_
        @ (match els with Some e -> own_labels_stmt e | None -> [])
    | Ast.Selse e -> own_labels_stmt e
    | Ast.Sdowhile { body; _ } -> own_labels_stmt body
    | Ast.Sdoto { body; _ } -> own_labels_stmt body
    | Ast.Sdoforever body -> own_labels_stmt body
    | Ast.Son { handler; _ } -> own_labels_stmt handler
    | Ast.Sproc _ -> []
    | _ -> []
  in
  here @ deeper

(* nested procedure ENTRY labels: this block owns the names, but they are not transfer targets *)
let proc_entries (ss : Ast.stmt list) =
  List.concat_map
    (fun (s : Ast.stmt) ->
      match s.Ast.st with
      | Ast.Sproc bs ->
          (match bs.Ast.blk.Ast.bname with Some x -> [lbl x] | None -> [])
      | _ -> [])
    ss

(* label REFERENCES written at this block level.  A GOTO in a handler that is itself a plain
   GOTO is the ON-unit demand; anything deeper inside a handler is a plain reference, which
   matches [E2E-34/P5]'s finding that a statement-form handler in a nested procedure demands
   nothing for the block it is written in. *)
let rec refs_stmts (ss : Ast.stmt list) = List.concat_map refs_stmt ss
and refs_stmt (s : Ast.stmt) =
  match s.Ast.st with
  | Ast.Son { handler; _ } ->
      (match handler.Ast.st with
       | Ast.Sgoto { tgt = t; subscript = [] } -> [(lbl t, Rk_on)]
       | Ast.Sgoto _ -> []
       | _ -> refs_stmt handler)
  | Ast.Sgoto { tgt = t; subscript = [] } -> [(lbl t, Rk_plain)]
  | Ast.Sgoto _ -> []
  | Ast.Sproc _ -> []
  | Ast.Sdobegin ss -> refs_stmts ss
  | Ast.Sif { then_; els; _ } ->
      refs_stmt then_ @ (match els with Some e -> refs_stmt e | None -> [])
  | Ast.Selse e -> refs_stmt e
  | Ast.Sdowhile { body; _ } -> refs_stmt body
  | Ast.Sdoto { body; _ } -> refs_stmt body
  | Ast.Sdoforever body -> refs_stmt body
  | _ -> []

(* the ON-unit presence test, unchanged in meaning from [E2E-34]: any ON-unit written at this
   block level, of any condition, with any handler shape, turns on ?OFCOP for a procedure tail *)
let rec on_any_stmt (s : Ast.stmt) =
  match s.Ast.st with
  | Ast.Son _ -> true
  | Ast.Sproc _ -> false
  | Ast.Sdobegin ss -> List.exists on_any_stmt ss
  | Ast.Sif { then_; els; _ } ->
      on_any_stmt then_ || (match els with Some e -> on_any_stmt e | None -> false)
  | Ast.Selse e -> on_any_stmt e
  | Ast.Sdowhile { body; _ } -> on_any_stmt body
  | Ast.Sdoto { body; _ } -> on_any_stmt body
  | Ast.Sdoforever body -> on_any_stmt body
  | _ -> false

(* One pass over the block tree.  Each block returns its own facts plus the references it
   could NOT resolve, which its ancestors must try; a reference reaches the root unresolved
   when no enclosing block owns the label, and codegen refuses that (DR calls it NOT LABEL).
   Blocks are keyed by PHYSICAL identity, not by name: anonymous nested BEGINs have no name to
   key on, and silently merging two blocks that happen to share one would merge their labels. *)
let rec survey (b : Ast.block)
  : (Ast.block * on_facts) list * (string * ref_kind) list =
  let procs = proc_entries b.Ast.bstmts in
  (* [E2E-36/P2] a nested procedure's ENTRY label is carried in the Sproc statement's label
     list by the parser, but it is NOT a transfer target: DR calls `GOTO sub;' NOT LABEL in
     both orientations (E36T16 sibling-to-sibling entry, E36T17 parent-to-own-child entry).
     Keeping those names out of `own' makes the survey hand them to `procs', which is what
     codegen refuses on, and stops a reference to an entry label from charging a saved-SP
     cell to a block DR never even gets to lay out. *)
  let own =
    List.filter (fun x -> not (List.mem x procs)) (own_labels_stmts b.Ast.bstmts) in
  let direct = List.map (fun (n, k) -> (n, k, true)) (refs_stmts b.Ast.bstmts) in
  let kids =
    List.filter_map
      (fun (s : Ast.stmt) -> match s.Ast.st with Ast.Sproc bs -> Some bs.Ast.blk | _ -> None)
      b.Ast.bstmts
  in
  let kid_plans, kid_unresolved =
    List.split (List.map survey kids)
  in
  let propagated =
    List.map (fun (x, k) -> (x, k, false)) (List.concat kid_unresolved)
  in
  let (demanded, upward) =
    List.fold_left
      (fun (dem, up) (nm, kind, local) ->
        if List.mem nm own then
          (* resolved HERE.  Demanded if the ON-unit points at it, or if the reference came
             from another block; a plain same-block GOTO does not demand a pad [E36T11]. *)
          (if kind = Rk_on || not local then (nm :: dem, up) else (dem, up))
        else
          (* not ours: an ancestor's, or nothing's -- either way it goes up unchanged *)
          (dem, (nm, kind) :: up))
      ([], []) (direct @ propagated)
  in
  let facts =
    { of_labels = demanded
    ; of_goto = demanded <> []
    ; of_any = List.exists on_any_stmt b.Ast.bstmts
    ; of_own = own
    ; of_procs = procs }
  in
  (if Sys.getenv_opt "PLI80_PADDEBUG" <> None then
     prerr_endline
       (Printf.sprintf "[pad] block@%d own=%s procs=%s direct=%s kidrefs=%s demanded=%s up=%s"
          (match b.Ast.bstmts with x :: _ -> x.Ast.spos.Source.line | [] -> -1)
          (String.concat "," own) (String.concat "," procs)
          (String.concat "," (List.map (fun (n2, k, _) -> n2 ^ if k = Rk_on then ":on" else ":plain") direct))
          (String.concat "," (List.map (fun (n2, k) -> n2 ^ if k = Rk_on then ":on" else ":plain")
                              (List.concat kid_unresolved)))
          (String.concat "," demanded)
          (String.concat "," (List.map fst upward))));
  ( (b, facts) :: List.concat kid_plans
  , upward )

let survey_all (b : Ast.block) = fst (survey b)

(* the facts of ONE block out of a program-wide survey.  Absence is a bug, not a default: a
   block that was not surveyed would silently lose its cell and its pads, which shifts DATA
   and lands a jump in the wrong place [C179]. *)
let facts_of (plan : (Ast.block * on_facts) list) (b : Ast.block) : on_facts =
  match List.find_opt (fun (x, _) -> x == b) plan with
  | Some (_, f) -> f
  | None ->
      failwith
        "bind: block missing from the pad survey plan (internal inconsistency, [C179])"

let no_facts =
  { of_labels = []; of_goto = false; of_any = false; of_own = []; of_procs = [] }

type proc_layout =
  { pl_name : string; pl_lbl : string option; pl_rec : bool
  ; pl_attr_rec : bool      (* RECURSIVE literally written in the source *)
  ; pl_ret : rt option                      (* RETURNS(<type>), [E2E-6] *)
  ; pl_ptrs : (string * int) list             (* formal -> ptr cell *)
  ; pl_rows : (string * rt * int) list        (* body-visible rows *)
  ; pl_arrays : (string * int * int * int) list
    (* [E2E-19] (lower name, lower bound, upper bound, element bytes) for the
       1-D arrays declared in THIS block.  Explicit addition rather than a
       wider pl_rows tuple, so the 7 codegen consumers of pl_rows -- and every
       scalar offset they produce -- are untouched. *)
  ; pl_body : Ast.stmt list
; pl_on : on_facts         (* [E2E-34] this block's ON-unit facts *)
; pl_sp_cell : int option  (* [E2E-34] bind-relative DATA addr of its saved-SP cell *) }

type prog_layout =
  { pl_top_cell : int option (* [E2E-34] saved-SP cell of the OUTERMOST block *)
  ; pl_top_on : on_facts     (* [E2E-36] the OUTERMOST block's surveyed facts, so codegen
                                reads the SAME plan bind allocated from and never rescans *)
; pl_calls : call_site list     (* DFS order, POOL-EXCLUSIVE offsets *)
  ; pl_procs : proc_layout list   (* DFS: parents before children *)
  ; pl_secs : (string * int * int) list
      (* proc name -> (block base, section size) POOL-EXCLUSIVE.
         RECURSIVE prologue SVBLK operands [RFACT: LXI B,8 ; LXI D,10
         = block base..end-of-section incl. its own call cells;
         P402: LXI B,8 ; LXI D,6 — two specimens; ACK/EXPR/DFACT
         corpus RELs carry more] *)
  ; pl_total : int                (* non-pool data bytes *)
  ; (* [E2E-11 step 5] the OUTERMOST block, when it is a procedure-only module
       (see top_is_proc / C136), laid out by the SAME section2 pass that handles
       nested callees -- pointer cell per formal, declared formal dcl deduped
       onto it, locals shifted after the pointer cells.  Some for such a module,
       None for a MAIN program, so every existing consumer that treats the
       outermost block as the main block is untouched.  It is ALSO a member of
       pl_procs (so procedure lowering, prescan contexts and callee formal
       lookup find it through the channels that already exist), and this field
       exists so codegen's rows_of can ask "which layout authority applies to
       my automatic area" without re-deriving the predicate. *)
     pl_top : proc_layout option
  ; (* [E2E-11 step 4] EXTERNAL/ENTRY declarations, name -> (params, external_,
       returns, formal types).  bind already classifies these as RTentry, which
       is the classification DR's own $V symbol table prints (bind.ml:22 records
       that correspondence: "external entry dcl => FUNCTION PARAMETERS(k)
       EXTERNAL CONSTANT").  Codegen used to DROP those rows (its outer-scope map
       returns None for RTentry), so an external entry was literally invisible
       and a CALL to it failed the `call to unknown' check -- an information
       loss, not a language limit.  ptypes is carried here precisely so argument
       MODE decisions survive: FIXED/DECIMAL/FLOAT formals take different
       descriptor routes, and without ptypes codegen could only guess. *)
    pl_exts : (string * (int * bool * rt option * rt list)) list }
(* NOTE: an earlier iteration added a pl_tail_exit field ("can the last
   MAIN tail loop exit?") as the guard gate. The 37-specimen matrix
   REFUTES it: P404/R432/R406 guard straight-line tails with no loop at
   all, and the real discriminator is whether the epilogue CALL ?STOPX
   is displaced behind appended procedure code (window CLOSED and no
   stop printed in place). The field is therefore gone; see the
   guard_slots comment in codegen.ml. *)

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
  let out = ref ([] : (string * Ast.expr list * Source.pos) list) in
  let rec go x =
    match x.Ast.e with
    | Ast.Esuffix (hd, args) -> begin
        match hd.Ast.e with
        | Ast.Eident h when nm_of (pl_l h) -> begin
            match args with
            | [] ->
                (* [E2E-11/CALL, E24A/E24J] a zero-argument call IS a call site:
                   DR registers it (the queue must stay aligned with codegen's
                   pop order) but allocates NO descriptor cell -- `cur` advances
                   by 2*0, and codegen emits a bare `CALL <entry>` with no
                   `LXI H`.  Three such sites in E24J left main's a/b/c at
                   0/2/4, which is the check that the slot really is zero-sized.
                   The old refusal here was a capability gap: it existed only
                   because no probe had pinned the zero-arg layout before. *)
                out := !out @ [(pl_l h, [], x.Ast.epos)]
            | _ ->
                (* [E2E-9] multi-arg calls register ONE site carrying the
                   whole argument list; DR allocates one 2-byte pointer cell
                   per argument in a single contiguous block [R2001-R2005, 
                   R2012, DECPOLY] *)
                out := !out @ [(pl_l h, args, x.Ast.epos)];
                List.iter go args
          end
        | _ -> List.iter go (pl_kids x)
      end
    | _ -> List.iter go (pl_kids x)
  in
  go e; !out

let rec pl_stmt_calls (nm_of : string -> bool) (s : Ast.stmt) =
  let w e = pl_expr_calls nm_of e in
  (* an I/O option's value is optional: FILE(f) carries an expression, SKIP
     carries none *)
  let wo o = match o.Ast.io_val with Some e -> w e | None -> [] in
  (* [E2E-8] hoisted out of the PUT/GET arm so FORMAT statements can reuse it: 
     a call inside a replication or a skip count must still reach the collector *)
  let rec wi it =
    match it with
    | Ast.Pi_fmt { fargs; fcount; _ } ->
        List.concat_map w fargs @ (match fcount with Some c -> w c | None -> [])
    | Ast.Pi_rep (a, b) -> w a @ w b
    | Ast.Pi_repgrp (a, _) -> w a
    | Ast.Pi_data e -> w e
    | Ast.Pi_ctl (_, Some e) -> w e
    | Ast.Pi_fmtlist is -> List.concat_map wi is
    | _ -> []
  in
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
    | Ast.Sreturn eo | Ast.Sstop eo ->
        (match eo with Some e -> w e | None -> [])
    (* [E2E-11/CALL] a CALL STATEMENT's arguments are call sites exactly like
       expression calls and get descriptor cells in the same source order:
       E24B allocates A(0004) for `call g(a);` then A(0006) for `n = h(a);`.
       The parser puts the arguments inside `target` as an Esuffix, so w alone
       would find them -- but walking `args` too keeps the collector correct if
       that ever changes, and costs nothing while args is []. *)
    | Ast.Sprocedure_stmt { target; args } ->
        (* a bare `call q;` / `q;` has NO Esuffix around its target -- the
           parser hands back a plain Eident -- so the expression walker would
           register no site and codegen's pop would land one short.  A
           zero-argument call still has to be IN the queue, because DR keeps the
           sites in source order (E24A: `call q` then `n = f();`). *)
        (match target.Ast.e with
         | Ast.Eident h when args = [] && nm_of (pl_l h) ->
             [ (pl_l h, [], target.Ast.epos) ]
         | _ -> [])
        @ w target @ List.concat_map w args
    | Ast.Sgoto { subscript; _ } -> List.concat_map w subscript
    | Ast.Sput { items; stream; on_opts; _ } | Ast.Sget { items; stream; on_opts; _ } ->
        let items = flatten_items items in
      (match stream with Some e -> w e | None -> [])
      @ List.concat_map wo on_opts
      @ List.concat_map wi items
    (* [E2E-11/CALL] full statement coverage.  This collector omitted ON
       handlers, EDIT, FORMAT, file-statement and READ/WRITE-VARYING subjects,
       plus PUT/GET stream and option expressions -- exactly the omission that
       made E11A relocate wrongly in step 2.  A missed call site is not a
       diagnostic, it is a silently shifted descriptor queue, so every arm of
       Ast.stmt_kind is now accounted for.  Sproc's child block is handled by
       the separate DFS phase; Snull/Sdcl/Sexit/Spicturestmt/Spreproc/
       Sdeclare_fail carry no expressions. *)
    | Ast.Son { cargs; _ } -> List.concat_map w cargs
    (* [E2E-34/P2] REVERT registers nothing and allocates nothing, but its conditional-
       name argument list is still EXPRESSIONS in this statement: this walker has no
       catch-all by design (see the ALLOCATE/FREE note below), so leaving the arm out
       would kill E32E2 in a bare Match_failure inside bind -- the exact contract
       violation that note records, reproduced from the other side. *)
    | Ast.Srevert { cargs; _ } -> List.concat_map w cargs
    | Ast.Sedit { target; opts } -> w target @ List.concat_map wo opts
    | Ast.Sfilestmt { file; opts } ->
        (match file with Some e -> w e | None -> [])
        @ List.concat_map wo opts
    | Ast.Sreadwv { file; to_ } -> w file @ w to_
    | Ast.Sformat items -> List.concat_map wi (flatten_items items)
    | Ast.Sassign_label { to_; _ } -> w to_
    | Ast.Snull _ | Ast.Sdcl _ | Ast.Sexit _ | Ast.Spicturestmt _
    | Ast.Spreproc _ | Ast.Sdeclare_fail _ | Ast.Ssignal _ -> []
    (* [E20-21/P0] ALLOCATE/FREE carry REAL expressions (the pointer, the
       based-on operand, the freed names).  This walker has no catch-all on
       purpose -- "exhaustive by construction" -- so omitting these two arms made
       every program containing ALLOCATE or FREE die in a bare Match_failure
       inside bind BEFORE codegen could refuse it (corpus NETWORK and REVERSE,
       both rc!=0 but with NO [TBD], which is exactly what the negative panel
       exists to catch).  Traversing the operands is not implementing the
       statement: codegen still refuses ALLOCATE/FREE with [TBD], and this only
       restores the contract that a refusal is REASONED. *)
    | Ast.Salloc { ptr; based } ->
        w ptr @ (match based with Some x -> w x | None -> [])
    | Ast.Sfree xs -> List.concat (List.map w xs)
    (* statements whose ONLY expressions live in sub-blocks: `own` is a separate
       pass from `kids` over the same statement, so these must still be matched
       here or the exhaustive-by-construction intent collapses into a
       Match_failure at runtime (E24B: `do while` had no `own` arm). *)
    | Ast.Sproc _ | Ast.Sdobegin _ | Ast.Sdoforever _ | Ast.Selse _ -> []
  in
  (* Sub-blocks.  Enumerated rather than catch-all on purpose: a catch-all here
     is what let step 2's walkers silently drop ON handlers, and a missed call
     site shifts the whole descriptor queue without ever failing a check. *)
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
    | Ast.Son { handler; _ } | Ast.Selse handler -> pl_stmt_calls nm_of handler
    (* [E2E-34/P2] REVERT has no sub-block (no handler), so it contributes no calls; it
       must still be named here because this list is enumerated on purpose. *)
    | Ast.Srevert _ -> []
    | Ast.Snull _ | Ast.Sdcl _ | Ast.Sassign _ | Ast.Sgoto _
    | Ast.Sput _ | Ast.Sget _ | Ast.Sfilestmt _ | Ast.Sedit _
    | Ast.Sreadwv _ | Ast.Sreturn _ | Ast.Sstop _ | Ast.Sexit _
    | Ast.Ssignal _ | Ast.Sdeclare_fail _ | Ast.Sprocedure_stmt _
    | Ast.Salloc _ | Ast.Sfree _ | Ast.Sassign_label _ | Ast.Sformat _
    | Ast.Spicturestmt _ | Ast.Spreproc _ -> []
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
  (* [E2E-36/P2] the program-wide pad plan, built ONCE per program, BEFORE section2 numbers
     any block: a block's cell demand can come from a reference written in a descendant, and
     section2 lays out a parent before it recurses into children [C179]. *)
  let pad_plan = survey_all blk in
  let calls = ref ([] : call_site list) in
  let pls = ref ([] : proc_layout list) in
  let secs = ref ([] : (string * int * int) list) in
  (* [E2E-34] the OUTERMOST block's saved-SP cell, written by section2 when top=true.
     Declared beside the other layout refs and filled in the SAME pass that lays out
     every procedure's cell, so main and a procedure-only module cannot drift [C202]. *)
  let top_cell = ref (None : int option) in
  (* two-phase: registry first so call matching sees real procedures;
     the first pass above is superseded by section2. *)
  let reg =
    ref ([] : (string * Ast.block * bool * bool * string list) list) in
  let rec collect b =
    List.iter
      (fun (s : Ast.stmt) ->
        match s.Ast.st with
        | Ast.Sproc bs ->
            let pb = bs.Ast.blk in
            if pb.bkind = Ast.Bproc then begin
              let nm = pl_l (Option.get pb.bname) in
              let fm = List.map pl_l pb.bparams in
              (* [E2E-11/CALL, E24A] a procedure with NO formals is ordinary
                 DR: `call q;` lowers to a bare `CALL <q>` with no descriptor
                 cell at all, and the body starts directly (`q`'s own `k fixed`
                 follows main's `n` in the auto area, no shadow, no SVBLK).
                 The old refusal here was a capability gap, not a language
                 limit -- the zero-formal case needed no new layout rule, just
                 nf = 0 (which the existing formulas already carry). *)
              (* [R411] the RECURSIVE attribute IS the trigger for
                 SVBLK + the shadow value cell (no self-call yet the
                 full machinery); call-derivation OR-ed as fallback
                 [HYPOTHESIS from attributed P402/RFACT/NFACT] *)
              reg := !reg @ [(nm, pb,
                  has_attr pb.Ast.bsuffix "RECURSIVE"
                  || is_rec nm pb,
                  has_attr pb.Ast.bsuffix "RECURSIVE", fm)];
              collect pb
            end else collect pb
        | _ -> ())
      b.bstmts
  in
  collect blk;
  calls := []; pls := [];
  let names = List.map (fun (n, _, _, _, _) -> n) !reg in
  let exts =
    List.filter_map
      (fun (nm, rt, _o, _a) ->
        match rt with
        | RTentry { params; external_; ret; ptypes } ->
            Some (nm, (params, external_, ret, ptypes))
        | _ -> None)
      (bind_rows blk)
  in
  (* an EXTERNAL ENTRY is a callable target: without this its call sites never
     reach `calls', so no descriptor cells get allocated for them and the pool
     layout of every LATER call site shifts -- the silent-shift failure class of
     C116/C129, not a diagnostic. *)
  let is_proc nm = List.mem nm names || List.mem_assoc nm exts in
  let rec section2 top b base formals recf attrf nm =
    let nf = List.length formals in
    if nf > 8 then
      failwith (Printf.sprintf "bind: %d-formal procedure unproven [TBD]" nf);
    let nr = named_of b in
    (* [E2E-9] the SHADOW-cell trigger is the written RECURSIVE attribute,
       not derived self-recursion: R2008's unattributed recursive rec(a,b)
       reads its POINTER cells directly (LHLD A A(000C)) with no shadow. *)
    let dedup x =
      nf > 0 && List.mem x formals && nm <> None && not attrf
    in
    (* [E2E-10 step 3 / 3b, C106] a formal dcl that DEDUPS onto its 2-byte
       pointer cell consumes NO storage -- for FLOAT and FIXED alike.  Six
       probes bracket the law by formal count: with 1/2/3 FLOAT formals DR's
       later local sits at A(0014)/A(0018)/A(001C) [R3095/R3096/R3093] and with
       1/2/3 FIXED formals at A(000C)/A(0010)/A(0014) [R3094/R3101/R3102], in
       every case immediately after the pointer cells, while a model that charges
       the declared cell is +4/+8/+12 (float) and +2/+4/+6 (fixed) too high.
       The exception is the written RECURSIVE attribute, where dedup does not
       apply at all: there the declared cell IS the shadow value cell and is
       really allocated, which is what keeps P401/NFACT/FFACT/R3104 byte-exact.
       So the subtraction is keyed on `dedup`, exactly like the row's address. *)
    let drops =
      (* cumulative dedup'd-formal bytes to subtract, in declaration order *)
      let rec go rest acc =
        match rest with
        | [] -> []
        | (x, rt, _) :: t ->
            let d = if dedup x then rt_bytes rt else 0 in
            (x, acc) :: go t (acc + d)
      in
      go nr 0
    in
    let drop_of x = match List.assoc_opt x drops with Some d -> d | None -> 0 in
    (* [E2E-20/C167] the span must use a row's REAL storage extent, not `rt_bytes'.
       bind_rows already ADVANCES offsets by the array's full extent (so with
       `dcl q(3) fixed, s fixed' the scalar correctly lands at 000A -- AR1 pins it),
       but rt_bytes knows only the element size: an array row contributes 2 here.
       That is harmless while some later row's offset pushes the max past the array
       (accidental correctness -- which is why AR1-AR5, all array-FIRST, are exact),
       and wrong as soon as the array is last or middle:
         `dcl s fixed, q(3) fixed'  -> mine span 4, DR DATA AREA = 0008 [AB18]
         `dcl x fixed, q(2) fixed, y fixed' -> DR 0008 [AB19]
       An under-sized span silently truncates the module's DATA area (LINK-DEF-DATA-SIZE
       0002 vs DR 0006 in AB16), which is the C162 overlap class again, arrived at from
       the third direction: not over-demand, not under-demand, but under-extent.
       The extent comes from Bind.bind_arrays -- the SAME walk, so there is exactly one
       sizing rule; codegen never recomputes it.  Re-running the walk here follows the
       existing `named_of' precedent immediately above rather than adding a new
       recursion class. *)
    let arrs = bind_arrays b in
    let row_sz (x, rt, _o) =
      match List.find_opt (fun (n, _lb, _ub, _ez) -> String.equal n x) arrs with
      | Some (_n, lb, ub, ez) -> (ub - lb + 1) * ez
      | None -> rt_bytes rt
    in
    let span =
      List.fold_left
        (fun m (x, rt, o) ->
          if dedup x then m else max m (o - drop_of x + row_sz (x, rt, o)))
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
          else (x, rt, named_base + (o - drop_of x)))
        nr
    in
    let cur = ref (named_base + span) in
    let () = () in
    (* one contiguous 2-byte pointer cell per argument [R2001: desc
       block A(0008)+A(000A), R2012: two 4-byte blocks back to back],
       then the expression-argument value cells [R2003: temp A(000C)
       after both desc cells] *)
    (* [E2E-14/C142 prototype, model A] TWO PHASES, not one per site:
             phase 1 numbers every site's DESCRIPTOR slots (2 bytes per argument,
             pre-order over call sites), phase 2 numbers the EXPRESSION-argument value
             cells.  DR's D3 `t + g(h(k(2)))' numbers descriptors 0013(g),0015(h),
             0017(k) and only then the value cells 0019, 001B; P9 `t + g(h(2))' numbers
             g.slot 000B, h.slot 000D, then g's arg cell 000F -- whereas the single-pass
             version interleaves (slot,temps) per site and puts g's arg cell at 000D
             ahead of h's descriptor.  This is the only difference between the two
             orderings, so it is decided by byte parity over the whole call corpus. *)
  (* [E2E-34/P1] the hidden saved-SP cell: demanded here, emitted by codegen at the
     block entry as `LXI H,0000 / DAD SP / SHLD * A(<cell>)'. It sits at the end of the
     NAMED autos and BEFORE the anonymous call cells -- DR's NETWORK numbers setup's
     cell 0088 while its first call temp is 008A, and E32E2's cell is 0019 = main's
     base 2 + AUTO STORAGE 23 -- so charging it here makes every later temp, child
     block and the DATA total shift by 2 automatically, with no second copy of the
     arithmetic. Only the ON ... GOTO form demands it: E32E1 has one statement-handler
     ON-unit, no `DAD SP', no `*' cell, DATA AREA 0019 against E32E2's 001B. *)
  let of_ = facts_of pad_plan b in
  let sp_cell =
    if of_.of_goto then begin
      let c = !cur in
      cur := !cur + 2;
      Some c
    end
    else None
  in
  if top then top_cell := sp_cell;
  let sites0 =
            List.map
              (fun (p, args, _pos) ->
                let slot = !cur in
                cur := !cur + 2 * List.length args;
                (p, args, slot))
              (List.concat_map (fun s -> pl_stmt_calls is_proc s) b.bstmts)
          in
          let sites =
            List.map
              (fun (p, args, slot) ->
                let arrs = try bind_arrays b with _ -> [] in
                let is_arr_hd aarg =
                  match aarg.Ast.e with
                  | Ast.Esuffix (hd, [ _ ]) ->
                      (match hd.Ast.e with
                       | Ast.Eident h ->
                           List.exists
                             (fun (n, _l, _u, _e) ->
                               String.equal n
                                 (String.lowercase_ascii h.Ast.orig))
                             arrs
                       | _ -> false)
                  | _ -> false
                in
                let temps =
                  List.map
                    (fun arg ->
                      (* [E2E-22/P3] an array ELEMENT actual is passed by reference to the
                         element's own cell -- AB7 `call p(a(4))' emits `LXI H,A+0006 / SHLD
                         <desc>' and PASSARAY's `call inner(argument(I))' emits the variable-index
                         ladder then `SHLD <desc>'.  Neither allocates a value cell, unlike a call
                         actual (`g(3)'), which DR evaluates into an anonymous temp [C145].  So the
                         element joins the simple-actual list here; getting this wrong would add a
                         DATA byte AND shift every later anonymous-cell number. *)
                      match arg.Ast.e with
                      | Ast.Enumber _ | Ast.Eident _ -> None
                      | _ when is_arr_hd arg -> None
                      | _ -> let t = !cur in cur := !cur + 2; Some t)
                    args
                in
                { cs_proc = p; cs_slot = slot; cs_args = args; cs_temps = temps })
              sites0
    in
    calls := !calls @ sites;
    let after = !cur in
    (match nm with
     | Some pn ->
         secs := !secs @ [(pn, base, after - base)];
         pls := !pls
                @ [ { pl_name = pn
                    ; pl_lbl = (match b.blabel with
                                | Some l -> Some (pl_l l) | None -> None)
                    ; pl_rec = recf
                    ; pl_attr_rec = attrf
                    ; pl_ret = returns_attr b
                    ; pl_ptrs =
                        List.mapi (fun i f -> (f, base + 2 * i)) formals
                    ; pl_rows = rows
                    ; pl_arrays = bind_arrays b
                    ; pl_body = b.bstmts
                    ; pl_on = of_
                    ; pl_sp_cell = sp_cell } ]
     | None -> ());
    List.fold_left
      (fun acc (s : Ast.stmt) ->
        match s.Ast.st with
        | Ast.Sproc bs ->
            let pb = bs.Ast.blk in
            if pb.bkind = Ast.Bproc then begin
              let cn = pl_l (Option.get pb.bname) in
              match List.find_opt (fun (n, _, _, _, _) -> n = cn) !reg with
              | Some (_, _, r, ar, fm) ->
                  section2 false pb acc fm r ar (Some cn)
              | None -> acc
            end else section2 false pb acc [] false false None
        | _ -> acc)
      after b.bstmts
  in
  (* [E2E-11 step 5] for a procedure-only module the outermost block is laid out
     exactly as a callee is: formals from bparams, nm = Some name (which is what
     turns on the formal-pointer cells AND the dedup of the declared formal dcl
     onto them -- section2's `dedup' tests `nm <> None', so passing None would
     silently charge A 4 bytes for `declare x float' where DR charges 2 for the
     pointer cell, and its DATA area would come out 8 against DR's 6).
     Deliberately refused here rather than guessed: a RECURSIVE or
     RECURSIVE-attributed procedure-only module, because the shadow-cell +
     SVBLK shape for a top-level module has no DR sample; and a module with more
     than one entry-visible name whose dedup status would change the span, which
     is not something the section formulas have been checked against. *)
  let top_pl = ref None in
  let total =
    if top_is_proc blk then begin
      let tn = pl_l (Option.get blk.Ast.bname) in
      if has_attr blk.Ast.bsuffix "RECURSIVE" || is_rec tn blk then
        failwith
          (Printf.sprintf
             "bind: procedure-only module %s is RECURSIVE [TBD: DR has no sample               of a shadow-cell/SVBLK prologue for a top-level module               (C136 covers non-recursive A only)]" tn);
      let t = section2 true blk 0 (List.map pl_l blk.bparams) false false (Some tn) in
      top_pl := List.find_opt (fun (p : proc_layout) -> p.pl_name = tn) !pls;
      t
    end else section2 true blk 0 [] false false None
  in
  { pl_calls = !calls; pl_procs = !pls; pl_secs = !secs;
    pl_total = total
  ; pl_exts = exts; pl_top = !top_pl
  ; pl_top_on = facts_of pad_plan blk;
    pl_top_cell = !top_cell (* [E2E-34] the outermost block's cell, from the SAME
                               allocation site as every procedure's *) }
