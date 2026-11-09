(* hir/semantic_env.ml — the ONE typed, read-only projection of bind facts
   (E2E-54/P1-b, spec/lab-evidence/e2e54/PLAN.md §P1-b.2).

   Contract (operator brief Step 2): this module is a PROJECTION over
   (Ast.block x Bind.prog_layout), never a competing binder. [create] performs
   NO name resolution of uses, NO type interpretation of declarations (that is
   bind's own job) and NO storage computation. Where bind exposes no fact the
   interface returns a typed absence ([None], or the typed [Not_found] for an
   out-of-scope id) and never infers silently (§P1-b.6 lists every capability
   bind does NOT expose; each stays a documented gap).

   Authority law (P0 falsifier F6, inherited and extended by P1-b S5): every
   fact below traces to a bind-exported function or field —
     rows (existence/name/type/auto flag) ......... [Bind.bind_rows]
     declaration spelling + declare line ......... [Bind.frame_decls]
     the ONE alias/key policy .................... [Bind.pl_l] (via [key_of])
     procedure identity/formals/returns/recursive  [Bind.proc_layout]
     external entries ............................ [Bind.pl_exts]
   What bind does NOT provide, and what this module therefore ORGANISES from
   AST shape (audit class [O], §P1-b.1 anti-overclaim list — never a Bind fact):
     - the block-tree nesting (parent/child edges): pl_procs is FLAT;
     - sid/scope/pid numbering: a deterministic pre-order contract, assigned
       EXACTLY as hir_build did at aaf295f0 (main pid 0 scope 0, then AST-nested
       Bproc children in source order; rows in bind declaration order) so every
       existing HIR dump byte is preserved (falsifier S2);
     - the Formal storage flag: AST bparams-list membership (the row itself,
       its type and its existence remain bind facts).

   Excluded by contract (brief Step 2; falsifier S8): frame/DATA placement,
   cell placement, section extents, total extents, saved-stack cells,
   relocation records, data-pool placements, 8080 vocabulary. The placement
   component of every bind tuple is DROPPED at the first touch; [pp_stype]
   re-renders only the semantic surface. Bind's own full wording crosses ONLY
   as the verbatim [epr]/[sret_pr] diagnostic strings so type-naming messages
   stay byte-identical across the seam (§P1-b.2, falsifier S10) — no numeric
   storage value is carried in any typed field.

   The public interface references NO [Hir] type: this env is backend-
   independent; Hir_build remains the only module mapping stype -> Hir.ty
   (the HIR subset gate).

   E2E-54/P1-a1 amendment (PLAN §P1-a1.4): one-dimensional arrayness is projected
   from bind's SECOND view of the same layout walk, [Bind.bind_arrays] — the only
   array authority (facts A-1..A-8). Arrayness is a separate symbol field
   ([e_array]), merged by lowered key onto the bind row; the row keeps the ELEMENT
   type and bind's verbatim element rendering (fact A-1), bounds are carried as the
   declared index limits only, and the record's physical element width is dropped at
   the first touch like every other layout component. [resolve]/[symbol]/
   [scope_syms] are unchanged: an array fact rides the eparent chain exactly as an
   enclosing scalar does (fact A-8).

   E2E-54/P1-a2 amendment (PLAN §P1-a2.3): parameter PASSING EVIDENCE and FORMAL
   descriptions are projected from bind's OWN records — [Bind.pl_calls] (the DFS
   call-site list) and [Bind.pl_ptrs] (the formal-cell order). Like every other
   physical quantity, the integer payload of the site records (descriptor slot,
   value-cell and copy-in cell addresses) is DROPPED AT THE FIRST TOUCH: the
   projection keeps the callee key, the PHYSICAL node identities of the argument
   expressions (used for MATCHING, never interpreted), three parallel BOOLEAN
   lists and bind's [cs_dec] flags as-is. Passing modes are symbolic
   ([passing_mode] below) and a disagreement between bind's record and the
   argument syntax is [PM_unknown] — a typed unknown the lowering must refuse
   loudly (HIR-E16), never guess through. bind's descriptor-slot field is not
   read at all (falsifier T5: the raw grep pins it out of this directory
   entirely — hop-8 reword). *)

(* Cross-library aliases (P0 F1 law: these units live in the separate
   [pli80_hir] library; the historical front end is reached through [Pli80]). *)
module Ast = Pli80.Ast
module Bind = Pli80.Bind

module D = Diagnostic

(* ---------- projected type surface (faithful, total, non-interpretive) ---------- *)

type stype =
  | SFixed_bin of int
  | SFixed_dec of int * int
  | SFloat of int
  | SChar of int * bool
  | SBit of int
  | SPointer
  | SLabel
  | SFormat (* AMENDMENT to the pre-registered surface (§P1-b.2 "additions only
               by amendment"): Bind.RTformat has no constructor in the list and
               type_of_rt must be TOTAL; this records the fact as-is. *)
  | SFile of { internal : bool }
  | SBased of string * stype (** view through a named pointer cell *)
  | SMember of { owner : string; based : bool; ty : stype }
      (** record-relative position dropped (§P1-b.2) *)
  | SStruct of { level : int; members : int }
  | SStructrec of { ptr : string } (** record extent dropped (§P1-b.2) *)
  | SBuiltin
  | SEntry of { params : int; external_ : bool; ret : stype option
              ; ptypes : stype list }
  | SArray1 of { elem : stype; lo : int; hi : int }
      (** AMENDMENT to the pre-registered surface (§P1-a1.4): one-dimensional array
          shape as a SEMANTIC pair of declared index bounds. [type_of_rt] NEVER
              produces it — bind array rows carry the ELEMENT type (fact A-1) — so
              arrayness arrives through the separate [bind_arrays] channel and is
              merged onto the symbol below. This constructor exists so a merged
              array symbol renders as an array (§P1-a1.4); it carries no stride,
              no element width, no placement (those are layout, dropped at the
              projection boundary exactly like the row offset). *)

let rec type_of_rt (rt : Bind.rt) : stype =
  match rt with
  | Bind.RTbin p -> SFixed_bin p
  | Bind.RTdec (p, s) -> SFixed_dec (p, s)
  | Bind.RTfloat p -> SFloat p
  | Bind.RTchar (n, v) -> SChar (n, v)
  | Bind.RTbit n -> SBit n
  | Bind.RTptr -> SPointer
  | Bind.RTlabel -> SLabel
  | Bind.RTformat -> SFormat
  | Bind.RTfile { internal } -> SFile { internal }
  | Bind.RTbased (p, t) -> SBased (p, type_of_rt t)
  | Bind.RTbmem (p, _rel, t) -> SMember { owner = p; based = true; ty = type_of_rt t }
  | Bind.RTimem (owner, _rel, inner) ->
      SMember { owner; based = false; ty = type_of_rt inner }
  | Bind.RTstruct { level; members } -> SStruct { level; members }
  | Bind.RTstructrec (p, _extent) -> SStructrec { ptr = p }
  | Bind.RTbuiltin -> SBuiltin
  | Bind.RTentry { params; external_; ret; ptypes } ->
      SEntry
        { params; external_; ret = Option.map type_of_rt ret
        ; ptypes = List.map type_of_rt ptypes }

(* Deterministic semantic rendering of a projection. NOT bind's full wording —
   diagnostics that must quote bind VERBATIM use the carried [epr]/[sret_pr]. *)
let rec pp_stype (s : stype) : string =
  match s with
  | SFixed_bin p -> Printf.sprintf "FIXED BINARY(%d,0)" p
  | SFixed_dec (p, q) -> Printf.sprintf "FIXED DECIMAL(%d,%d)" p q
  | SFloat p -> Printf.sprintf "FLOAT BINARY(%d,0)" p
  | SChar (n, false) -> Printf.sprintf "CHAR(%d)" n
  | SChar (n, true) -> Printf.sprintf "CHAR(%d) VARYING" n
  | SBit n -> Printf.sprintf "BIT(%d)" n
  | SPointer -> "POINTER"
  | SLabel -> "LABEL"
  | SFormat -> "FORMAT"
  | SFile { internal } -> if internal then "FILE INTERNAL" else "FILE"
  | SBased (p, t) -> pp_stype t ^ " BASED(" ^ String.uppercase_ascii p ^ ")"
  | SMember { owner; based = true; ty } ->
      pp_stype ty ^ " MEMBER OF BASED"
      ^ (if String.equal owner "" then ""
        else "(" ^ String.uppercase_ascii owner ^ ")")
  | SMember { owner; based = false; ty } ->
      pp_stype ty ^ " MEMBER OF " ^ String.uppercase_ascii owner
  | SStruct { level; members } ->
      Printf.sprintf "STRUCTURE LEVEL %d, MEMBERS %d" level members
  | SStructrec { ptr } ->
      "STRUCTURE BASED"
      ^ (if String.equal ptr "" then "" else "(" ^ String.uppercase_ascii ptr ^ ")")
  | SBuiltin -> "BUILTIN"
  | SEntry { params; external_; ret; _ } ->
      Printf.sprintf "%s PARAMETERS(%d)"
        (if external_ || ret <> None then "FUNCTION" else "ENTRY")
        params
  | SArray1 { elem; lo; hi } ->
      Printf.sprintf "%s ARRAY[%d:%d]" (pp_stype elem) lo hi

(* ---------- symbols ---------- *)

type storage = S_auto | S_static | S_formal

(* The merged array description (§P1-a1.4). Declared index bounds are SEMANTIC
   quantities (what the program says the array indexes are), never extents:
   bind's fourth record component is the physical element width and is dropped
   at the FIRST touch, in the [arrays_of] read below — it crosses nothing here
   and nothing downstream (falsifier T6). *)
type array1 = { a_elem : stype; a_lo : int; a_hi : int }

type symbol = {
  esid : int;
  ekey : string;   (** lowered resolution key, exactly as bind rows carry it *)
  eorig : string;  (** source spelling, from the bind-flattened dcl row *)
  escope : int;
  ety : stype;
  epr : string;    (** bind's own rendering VERBATIM (Bind.rty_str of the row) *)
  estorage : storage;
  eline : int;     (** declaration line, from bind's frame_decls channel *)
  e_array : array1 option;
      (** AMENDMENT (P1-a1): [Some] = bind's array channel recorded this very name
          in THIS block (facts A-1/A-8: arrayness is per-block and lives only in
          [bind_arrays], so the merge is by lowered key). [None] = no array record —
          which includes a written-but-unvalidated dimension such as [a(1)] (fact
          A-5) and structure members (fact A-14, which never reach the channel). *)
}

(* Formal identity, position, declared type and OWNERSHIP scope (§P1-a2.3 item
   3). [f_sid]/[f_stype] are [None] exactly together — bind laid no row for
   this formal (P0 refuses such a procedure; the [None] stays typed, never an
   invented symbol). Resolution is the callee block's OWN [esyms] association,
   never [resolve] up the chain: a formal shadowing an outer name is the
   [C358] shape and the callee's own row must win. *)
type formal_desc = {
  f_pos : int;            (** 0-based, bind pl_ptrs order (the semantic position) **)
  f_key : string;         (** lowered formal name (bind fact) **)
  f_sid : int option;     (** env symbol in the CALLEE's own scope **)
  f_stype : stype option; (** declared row type; None exactly when f_sid is None **)
  f_scope : int;          (** owning (callee) scope — ownership and lexical scope **)
}

(* ---------- procedure signatures (bind's own facts, projected) ---------- *)

type proc_sig = {
  sptrs : string list;      (** formal names in bind's own order (pl_ptrs keys) *)
  sret : stype option;
  sret_pr : string option;  (** bind's rendering of RETURNS, VERBATIM *)
  sptr_count : int;         (** arity = number of bind formal cells *)
  srec : bool;              (** bind's derived recursion fact *)
  sattr_rec : bool;         (** RECURSIVE attribute written in the source *)
  sformals : formal_desc list;
      (** AMENDMENT (§P1-a2.3): the formal list projected WITH identity, type and
          ownership, positions exactly in [pl_ptrs] order (matrix row 1: the
          order is bind's semantic formal order; the cell addresses never
          cross). **)
}

let sig_of_pl (pl : Bind.proc_layout) ~(syms : (string * symbol) list)
    ~(scope : int) : proc_sig =
  let keys = List.map fst pl.Bind.pl_ptrs in
  { sptrs = keys
  ; sret = Option.map type_of_rt pl.Bind.pl_ret
  ; sret_pr = Option.map Bind.rty_str pl.Bind.pl_ret
  ; sptr_count = List.length keys
  ; srec = pl.Bind.pl_rec
  ; sattr_rec = pl.Bind.pl_attr_rec
  ; sformals =
      List.mapi
        (fun i key ->
          match List.assoc_opt key syms with
          | Some s ->
              { f_pos = i; f_key = key; f_sid = Some s.esid
              ; f_stype = Some s.ety; f_scope = scope }
          | None ->
              { f_pos = i; f_key = key; f_sid = None
              ; f_stype = None; f_scope = scope })
        keys }

(* ---------- block environments ---------- *)

type block_env = {
  epid : int;
  escope : int;
  eparent : int option;    (** enclosing block's SCOPE (AST-nesting fact, [O]) *)
  ename : string option;   (** source spelling *)
  ekey : string option;    (** lowered proc key, as bind names the layout *)
  esyms : (string * symbol) list; (** bind row order; NO new lookup rules *)
  eformals : string list;  (** lowered AST bparams (the [O] formal set) *)
  esig : proc_sig option;  (** None = bind laid no procedure record *)
  east : Ast.block;        (** the syntax this block came from *)
}

(* ---------- parameter passing evidence (§P1-a2.3) ---------- *)

(* The SYMBOLIC classification of what bind recorded at one argument position.
   Evidence classes (matrix rows, §P1-a2.1): [PM_value_cell] is the anonymous
   expression cell ([C145], cs_temps Some); [PM_own_cell] is a bare name or an
   array-ELEMENT actual designating its own storage (no cell in bind's record,
   [C093]/[C175]); [PM_immediate] is an [Enumber] actual (no cell; DR
   materialises a descriptor constant); [PM_copy_in] is the DEC widening temp
   ([C358], cs_copies Some) — OUTSIDE the lowering subset, refused by rule; and
   [PM_unknown] is a typed disagreement between bind's record and the argument
   syntax. This is evidence about DR's ABI materialisation, NOT a portable
   language law (brief §2 warning). *)
type passing_mode =
  | PM_value_cell
  | PM_own_cell
  | PM_immediate
  | PM_copy_in
  | PM_unknown

(* One projected call site: bind's callee key, the physical argument NODES (for
   identity matching only — never inspected beyond their constructors by the
   classifier below), and the positional flags. Every Some address in bind's
   record became [true]; no integer entered this type (falsifier T6). *)
type call_site = {
  cs_proc : string;
  cs_args : Ast.expr list;
  cs_temps : bool list;
  cs_copies : bool list;
  cs_dec : bool list; (** carried as-is per §P1-a2.3; no lowering consumes it yet **)
}

(* The answer of [call_evidence]: the callee key and one passing mode per
   recorded argument position, plus bind's scalar-DEC-formal flags carried
   as-is. No position count or mode here is re-derived from the AST. The mode
   FUNCTIONS live with the lookups below (they consume [t]); only the types
   are declared here. *)
type call_evidence = {
  ce_proc : string;
  ce_args : passing_mode list;
  ce_dec : bool list;
}

(* ---------- external entries (pl_exts channel) ---------- *)

type entry_sig = {
  en_params : int;
  en_external : bool;
  en_ret : stype option;
  en_ptypes : stype list;
}

(* ---------- the environment ---------- *)

type t = {
  main_bd : block_env;
  all_blocks : block_env list; (** pid-ascending = pre-order registration *)
  by_scope : (int * block_env) list;
  procs_by_name : (string * int) list; (** lowered key -> pid *)
  entries : (string * entry_sig) list;
  sites : call_site list;
      (** AMENDMENT (§P1-a2.3): bind's [pl_calls] projected ONCE at [create] —
          DFS order preserved, every Some address replaced by [true], the slot
          integer DROPPED unread (T5 raw grep: this descriptor-slot field is
          named NOWHERE in this directory — hop-8 reword). The physical node
          identities enable [call_evidence]
          matching; nothing here interprets an expression. **)
}

(* Typed unsupported (brief Step 2): a lookup against an out-of-range scope id
   is a caller error and raises — never a silent None. *)
exception Not_found of { scope : int }

(* Internal refusal channel: registration guards refuse with Diagnostics, the
   same typed refusals Hir_build has always raised (§P1-b.3: no message, code
   or refusal changes; hir_build re-raises the list). *)
exception Refuse of Diagnostic.t list

let refuse ?line code msg = raise (Refuse [ D.make ?line code msg ])

(* ---------- bind-fact channels ---------- *)

(* the ONE alias policy, delegated verbatim *)
let key_of (n : Ast.name) : string = Bind.pl_l n

(* Bind's OWN declaration flattener (the [Bind.frame_decls] channel — the
   parser keeps dcls as Sdcl statements; blk.bdecls is [] for corpus-shaped
   programs; consulting bdecls alone silently loses every declaration). *)
let find_dcl_blk (blk : Ast.block) (key : string) : (Ast.dcl * int) option =
  List.find_opt
    (fun (d, _l) -> String.equal (Bind.pl_l d.Ast.dname) key)
    (Bind.frame_decls blk)

let find_dcl (_t : t) (be : block_env) (key : string) : (Ast.dcl * int) option =
  find_dcl_blk be.east key

(* Deterministic header line for a block: [Ast.block] carries no pos of its own
   (hop-2 measurement); the name/spelling fields do. Used for block-level
   diagnostics and fallbacks only — symbol lines come from the dcl rows. *)
let block_line (blk : Ast.block) : int =
  match blk.Ast.blabel with
  | Some n -> n.Ast.pos.line
  | None -> (
      match blk.Ast.bname with
      | Some n -> n.Ast.pos.line
      | None -> (
          match blk.Ast.bendpos with
          | Some p -> p.line
          | None -> 0))

(* ---------- array channel (bind's second view of the SAME layout walk) ---------- *)

(* [Bind.bind_arrays] is the ONE array authority (fact A-1); the projection reads
   it per block (fact A-8/A-13: a nested procedure owns its own records) and keeps
   ONLY the name and the two declared bounds. The record list is already in
   declaration order and its names are already lowered by bind itself. *)
let arrays_of (blk : Ast.block) : (string * int * int) list =
  List.map
    (fun (nm, lb, ub, _physical) -> (nm, lb, ub))
    (Bind.bind_arrays blk)

(* Split-channel guards (§P1-a1.4 guard law). bind produces rows and array
   records from ONE layout walk, so a record with no row — or two records for one
   name — is an internal inconsistency; the env refuses loudly rather than
   guessing which view wins. No probe produced either shape (recorded honestly as
   unexercised, like the P0 dup_free witness); the refusal rides the diagnostic
   channel so the CLI reports it as a typed HIR-E14, never a crash. *)
let guard_arrays (blk : Ast.block) (rows : (string * 'a * 'b) list)
    (arrs : (string * int * int) list) : unit =
  let rec dup_free = function
    | (a, _, _) :: rest
      when List.exists (fun (b, _, _) -> String.equal a b) rest ->
        refuse ~line:(block_line blk) D.e_dims
          ("duplicate bind array records for " ^ a
             ^ " (split-channel inconsistency)")
    | _ :: rest -> dup_free rest
    | [] -> ()
  in
  dup_free arrs;
  List.iter
    (fun (nm, _lb, _ub) ->
      if not (List.exists (fun (k, _, _) -> String.equal k nm) rows) then
        refuse ~line:(block_line blk) D.e_dims
          ("bind array record for " ^ nm
             ^ " has no matching row (split-channel inconsistency)"))
    arrs

(* ---------- registration (pre-order id assignment, EXACTLY as at aaf295f0) ---------- *)

type acc = {
  mutable next_sid : int;
  mutable next_scope : int;
  mutable next_pid : int; (* pid 0 is reserved for the outermost block *)
  mutable blocks : block_env list; (* registration order; sorted to pid order below *)
  mutable procs_by_name : (string * int) list;
}

let register_block st parent_scope pid (blk : Ast.block) (formals : string list)
    (pl : Bind.proc_layout option) : block_env =
  let scope_id = st.next_scope in
  st.next_scope <- scope_id + 1;
  (* The FIRST touch of a bind row drops its placement component (§P1-b.1
     audit site 4, falsifier S8/F8): only (name, type, auto-flag) cross. *)
  let rows =
    List.map
      (fun (nm, rt, _placement, auto) -> (nm, rt, auto))
      (Bind.bind_rows blk)
  in
  (* bind keeps one alias row per name; ASSERT the identity precondition. *)
  let rec dup_free = function
    | (a, _, _) :: rest
      when List.exists (fun (b, _, _) -> String.equal a b) rest ->
        refuse ~line:(block_line blk) D.e_decl
          ("bind produced duplicate rows for " ^ a)
    | _ :: rest -> dup_free rest
    | [] -> ()
  in
  dup_free rows;
  (* P1-a1: the block's array records, read once, guards run, then merged by key. *)
  let arrs = arrays_of blk in
  guard_arrays blk rows arrs;
  let syms =
    List.map
      (fun (key, rt, auto) ->
        let d = find_dcl_blk blk key in
        let eorig =
          match d with
          | Some (dd, _) -> dd.Ast.dname.Ast.orig
          | None -> key (* formal without explicit dcl has no row; consumers guard it *)
        in
        let eline = match d with Some (_, l) -> l | None -> block_line blk in
        let estorage =
          if List.mem key formals then S_formal
          else if auto then S_auto
          else S_static
        in
        let ety = type_of_rt rt in
        (* The merge (§P1-a1.4): a row whose lowered key carries an array record
           gains the description; its [ety]/[epr] stay the ELEMENT type and bind's
           verbatim element rendering (fact A-1 — an array row is shape-identical
           to a scalar row). Bounds come from bind's record, never from the AST
           dimension text. *)
        let e_array =
          match List.find_opt (fun (k, _, _) -> String.equal k key) arrs with
          | Some (_, lb, ub) -> Some { a_elem = ety; a_lo = lb; a_hi = ub }
          | None -> None
        in
        let esid = st.next_sid in
        st.next_sid <- esid + 1;
        ( key,
          { esid; ekey = key; eorig; escope = scope_id; ety;
            epr = Bind.rty_str rt; estorage; eline; e_array } ) )
      rows
  in
  let be =
    { epid = pid; escope = scope_id;
      eparent = (if pid = 0 then None else Some parent_scope);
      ename = (match blk.Ast.bname with Some n -> Some n.Ast.orig | None -> None);
      ekey = (match pl with Some p -> Some p.Bind.pl_name | None -> None);
      esyms = syms; eformals = formals;
      esig = Option.map (fun p -> sig_of_pl p ~syms ~scope:scope_id) pl;
      east = blk }
  in
  st.blocks <- be :: st.blocks;
  be

(* Mirror of codegen rows_of's two-authority guard: when the outermost block is
   a procedure-only module (bind's pl_top), every bind_rows name must appear in
   the section layout, else refuse (same rule, same reason; a structural
   consistency check over two bind views, not an independent resolution). *)
let check_top_authority (blk : Ast.block) (plan : Bind.prog_layout) : unit =
  match plan.Bind.pl_top with
  | None -> ()
  | Some tp ->
      let missing =
        List.filter
          (fun (n, _rt, _o, _a) ->
            not
              (List.exists
                 (fun (x, _rt, _o) -> String.equal x n)
                 tp.Bind.pl_rows))
          (Bind.bind_rows blk)
      in
      if missing <> [] then
        refuse ~line:(block_line blk) D.e_decl
          ("declaration "
             ^ (match List.hd missing with n, _, _, _ -> n)
             ^ " is outside bind's section layout for a procedure-only module \
                [C136 shape]")

(* Pre-order registration walk over the Sproc block tree. bind's proc_layout
   registry is flat and carries NO parent pointer (hop-1 measurement), so the
   nesting SHAPE must be re-read from the AST — a structural traversal that
   allocates ids and mirrors bind's own block discovery (bind_program's
   collect descends through every Sproc child likewise); every NAME/TYPE/
   signature fact below comes from bind (falsifier F6): a Bproc child with no
   pl_procs entry is a hard refusal, never a silently invented block.

   §P1-h hygiene: the visitor SEPARATES the statement subtree under traversal
   ([ss]) from the enclosing procedure's env ([parent], the semantic OWNER).
   The pre-repair non-Bproc branch re-entered the OWNER's own statement list
   (re-reading the same Sproc forever — the measured hang, RESULTS §P1-b.5
   note 3, and a bogus duplicate-name refusal when a Bproc sibling came
   first). Termination now follows structurally: the parser AST is a finite
   tree and the recursion strictly DESCENDS into the nested block's own
   statements, visiting each nested block exactly once along its path; the
   descent mirrors bind's collect (bind.ml:2204-2231) exactly — through every
   Sproc child, registering only Bprocs. *)
let rec discover_stmts st (plan : Bind.prog_layout) (parent : block_env)
    (ss : Ast.stmt list) : unit =
  List.iter
    (fun (s : Ast.stmt) ->
      match s.Ast.st with
      | Ast.Sproc bs ->
          let ib = bs.Ast.blk in
          if ib.Ast.bkind = Ast.Bproc then begin
            let key =
              match ib.Ast.bname with
              | Some n -> Bind.pl_l n
              | None ->
                  refuse ~line:bs.Ast.bpos.line D.e_scope
                    "anonymous procedure block: bind registers no procedure \
                     without a name"
            in
            let pl =
              match
                List.find_opt
                  (fun (p : Bind.proc_layout) -> String.equal p.Bind.pl_name key)
                  plan.Bind.pl_procs
              with
              | Some p -> p
              | None ->
                  refuse ~line:bs.Ast.bpos.line D.e_scope
                    ("procedure " ^ key
                    ^ " is not in bind's proc_layout registry \
                       (second-authority guard)")
            in
            (match List.assoc_opt key st.procs_by_name with
            | Some _ ->
                refuse ~line:bs.Ast.bpos.line D.e_scope
                  ("duplicate internal procedure name " ^ key
                  ^ " (bind-legal? P0 refuses rather than guess)")
            | None -> ());
            let pid = st.next_pid in
            st.next_pid <- pid + 1;
            (* names complete BEFORE any body lowers: forward calls to later-
               declared internal procedures are bind-legal. *)
            st.procs_by_name <- (key, pid) :: st.procs_by_name;
            let be =
              register_block st parent.escope pid ib
                (List.map Bind.pl_l ib.Ast.bparams)
                (Some pl)
            in
            discover_stmts st plan be ib.Ast.bstmts
          end
          else
            (* BEGIN/DO blocks share the parent's scope (bind has no per-BEGIN
               scoping — hop-1); descend the NESTED block's OWN statements for
               PROCEDURE DISCOVERY, keeping the enclosing procedure as the
               semantic context. No scope/pid/ownership is invented. *)
            discover_stmts st plan parent ib.Ast.bstmts
      | _ -> ())
    ss

(* Discovery entry for one registered block: its own statement list, itself
   as the enclosing-procedure context (§P1-h.2; identical registration
   sequence to the pre-repair code for every tree without nested non-Bproc
   blocks — the zero-drift preservation law). *)
let register_children st plan (parent : block_env) : unit =
  discover_stmts st plan parent parent.east.Ast.bstmts

let create (blk : Ast.block) (plan : Bind.prog_layout) :
    (t, Diagnostic.t list) result =
  try
    check_top_authority blk plan;
    let st =
      { next_sid = 0; next_scope = 0; next_pid = 1 (* pid 0 is the outermost block *);
        blocks = []; procs_by_name = [] }
    in
    (* 1. outermost block: pid 0, scope 0. A procedure-only module (bind's
          pl_top) is the program entry AND a named call target; a MAIN program
          has no bind proc record for its outer block and no module name.
          The AST formal set of the outer block is empty at aaf295f0 (preserved
          identity contract, falsifier S2). *)
    let main_pl = if Bind.top_is_proc blk then plan.Bind.pl_top else None in
    (match main_pl with
    | Some tp -> st.procs_by_name <- (tp.Bind.pl_name, 0) :: st.procs_by_name
    | None -> ());
    let main_bd = register_block st 0 0 blk [] main_pl in
    (* 2. pre-order registration of nested procedures; pids/scopes/sids follow
          source order (bind rows are declaration-ordered — hop-1 measurement). *)
    register_children st plan main_bd;
    let all_blocks =
      List.sort (fun a b -> compare a.epid b.epid) st.blocks
    in
    let entries =
      List.map
        (fun (nm, (params, external_, ret, ptypes)) ->
          ( nm,
            { en_params = params; en_external = external_
            ; en_ret = Option.map type_of_rt ret
            ; en_ptypes = List.map type_of_rt ptypes } ))
        plan.Bind.pl_exts
    in
    (* §P1-a2.3: the call-site projection. The option payloads of bind's site
       records are converted to booleans HERE, at the first and only touch; the
       slot field is never read. *)
    let sites =
      List.map
        (fun (cs : Bind.call_site) ->
          { cs_proc = cs.Bind.cs_proc
          ; cs_args = cs.Bind.cs_args
          ; cs_temps = List.map Option.is_some cs.Bind.cs_temps
          ; cs_copies = List.map Option.is_some cs.Bind.cs_copies
          ; cs_dec = cs.Bind.cs_dec })
        plan.Bind.pl_calls
    in
    Ok
      { main_bd; all_blocks;
        by_scope = List.map (fun b -> (b.escope, b)) all_blocks;
        procs_by_name = st.procs_by_name; entries; sites }
  with Refuse ds -> Error ds

(* ---------- lookups ---------- *)

let blocks (t : t) : block_env list = t.all_blocks

let main_block (t : t) : block_env = t.main_bd

let block_of_scope (t : t) (scope : int) : block_env =
  match List.assoc_opt scope t.by_scope with
  | Some b -> b
  | None -> raise (Not_found { scope })

let block_of_pid (t : t) (pid : int) : block_env =
  match
    List.find_opt (fun (b : block_env) -> b.epid = pid) t.all_blocks
  with
  | Some b -> b
  (* Typed unknown: an out-of-range pid is a caller bug, never a silent None.
     Same channel as scopes (§P1-b.2); the field carries the offending id. *)
  | None -> raise (Not_found { scope = pid })

let scope_syms (t : t) (scope : int) : (string * symbol) list =
  (block_of_scope t scope).esyms

let symbol (t : t) (sid : int) : symbol option =
  List.find_map
    (fun (_k, (s : symbol)) -> if s.esid = sid then Some s else None)
    (List.concat_map (fun (b : block_env) -> b.esyms) t.all_blocks)

(* Resolve a name through bind rows, walking the lexical chain the AST block
   nesting creates (class [O] over [P] data). Existence and meaning come from
   bind tables only: a name absent from the whole visible chain returns None
   because bind — the ONE authority — registered no row. *)
let rec resolve (t : t) (scope : int) (name : string) : symbol option =
  let be = block_of_scope t scope in
  match List.assoc_opt name be.esyms with
  | Some s -> Some s
  | None -> (
      match be.eparent with
      | Some p -> resolve t p name
      | None -> None)

let procedure (t : t) (key : string) : int option =
  List.assoc_opt key t.procs_by_name

let signature (t : t) (pid : int) : proc_sig option =
  (block_of_pid t pid).esig

(* §P1-a2.3 mode computation — functions over [t], defined with the lookups.

An [O]-class organization over bind rows (same class as the Formal flag):
   an array-ELEMENT actual is a 1-subscript [Esuffix] on a plain name whose env
   symbol carries [e_array = Some], resolved from the CALLER's scope chain.
   bind's own discriminator (section2) consults only the calling block's
   records; where the two views disagree the classifier yields [PM_unknown]
   rather than guessing (see [passing_mode_of]). *)
let element_actual (t : t) (caller_scope : int) (e : Ast.expr) : bool =
  match e.Ast.e with
  | Ast.Esuffix (hd, [ _ ]) -> (
      match hd.Ast.e with
      | Ast.Eident h -> (
          match resolve t caller_scope (key_of h) with
          | Some s -> s.e_array <> None
          | None -> false)
      | _ -> false)
  | _ -> false

(* Per-position mode from bind's OWN discriminators, never re-derived (§P1-a2.3):
   the copy-in flag wins, then the recorded cell flag, then the argument syntax.
   The arms where bind recorded a value cell for a bare name, an immediate or an
   element are internal inconsistencies (bind's own rule gives those no cell) and
   classify [PM_unknown]; so does a genuine expression bind recorded no cell for. *)
let passing_mode_of (t : t) (caller_scope : int) (temp : bool) (copy : bool)
    (e : Ast.expr) : passing_mode =
  if copy then PM_copy_in
  else
    match e.Ast.e with
    | Ast.Eident _ -> if temp then PM_unknown else PM_own_cell
    | Ast.Enumber _ -> if temp then PM_unknown else PM_immediate
    | Ast.Esuffix ({ e = Ast.Eident _; _ }, [ _ ])
      when element_actual t caller_scope e ->
        if temp then PM_unknown else PM_own_cell
    | _ -> if temp then PM_value_cell else PM_unknown

(* §P1-a2.3: formal descriptions of a registered block. [None] = bind laid no
   procedure record; typed [Not_found] for an out-of-range pid (same channel as
   [signature]/[block_of_pid], §P1-b.2). *)
let formals_of (t : t) (pid : int) : formal_desc list option =
  match (block_of_pid t pid).esig with
  | Some s -> Some s.sformals
  | None -> None

(* §P1-a2.3 matching law: the FIRST recorded site (bind DFS order) whose callee
   key equals [callee_key] and whose [cs_args] are PHYSICALLY ([==]) the very
   [Ast.expr] nodes being lowered. Determinism: these nodes are the nodes of the
   parsed tree [bind_program] walked, and [Hir_build] re-runs bind on the SAME
   tree, so identity is stable within a process; two zero-arity sites to one
   callee are indistinguishable but both carry EMPTY evidence lists, making
   first-match provably harmless. A typed [None] (no recorded site, or a site
   whose positional lists disagree in length — impossible by bind construction,
   loud if ever seen) makes the lowering refuse with HIR-E16 and never assume a
   mode. §P1-a2.10 pins the falsification path: if this identity law ever fails
   to match a real call, that failure IS the E16 refusal — re-audit, never a
   positional guess. *)
let call_evidence (t : t) ~(caller_scope : int) ~(callee_key : string)
    (args : Ast.expr list) : call_evidence option =
  let rec same_nodes l1 l2 =
    match (l1, l2) with
    | [], [] -> true
    | a :: r1, b :: r2 -> a == b && same_nodes r1 r2
    | _ -> false
  in
  List.find_map
    (fun (cs : call_site) ->
      if not (String.equal cs.cs_proc callee_key) then None
      else if not (same_nodes cs.cs_args args) then None
      else if
        List.length cs.cs_temps <> List.length cs.cs_args
        || List.length cs.cs_copies <> List.length cs.cs_args
      then None
        (* defensive: bind builds the three lists per argument by List.mapi, so
           equal length is a construction; a mismatch would be an internal
           inconsistency and is reported as NO evidence, never guessed past *)
      else
        Some
          { ce_proc = cs.cs_proc
          ; ce_args =
              List.map2
                (fun (temp, copy) e ->
                  passing_mode_of t caller_scope temp copy e)
                (List.combine cs.cs_temps cs.cs_copies) cs.cs_args
          ; ce_dec = cs.cs_dec })
    t.sites

(* pid -> pid of the enclosing procedure (main, pid 0, has none). *)
let enclosing (t : t) (pid : int) : int option =
  match (block_of_pid t pid).eparent with
  | Some scope -> Some (block_of_scope t scope).epid
  | None -> None

let entry_decls (t : t) : (string * entry_sig) list = t.entries
