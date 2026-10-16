(** Syntax-faithful AST. Names keep source case + uppercase key; positions
    on every node (the compiler's own diagnostics are line/offset based,
    so we mirror that granularity). Attributes are kept as raw
    [key * args] until a binding pass resolves them — this mirrors the
    compiler's own dcl grammar where attribute order/interleaving is free
    [M App C]. *)

open Source

type name = { orig : string; key : string; pos : pos }

type relop = Eq | Ne | Lt | Le | Gt | Ge

type binop =
  | Add | Sub | Mul | Div | Exp          (** + - * / ** *)
  | Cat                                   (** || // (character) *)
  | BitCat                                (** !! bit *)
  | And | Or | NotB | XorNe | AndThen | OrElse                (** & |(!) ^ ; XorNe = ^= : PROVEN
      numeric NE (5^=3->1, 5^=5->0, 3^=1->1, left-assoc) [P052B];
      bit-string ^= ambiguous AND/XOR/NE [PROBE 64] *)
  | EqR of relop                          (** relational inside condition *)

type expr =
  { e : expr_kind; epos : pos }
and expr_kind =
  | Eident of name                        (** bare name; resolution later *)
  | Eqstruct of expr * name               (** a.b qualified [EX P022] *)
  | Eqptr of expr * name                  (** a->b [EX P022] *)
  | Enumber of string                     (** literal text as written *)
  | Estring of string                     (** resolved value ('' folded) *)
  | Ebit of string
  | Eprefix of pfx * expr
  | Ebinary of binop * expr * expr
  | Econd of expr                         (** (c) — condition paren *)
  | Esuffix of expr * expr list           (** call/index f(a, b) *)
  | Ebuilt of string * expr list          (** built-in by key [M §12] *)
  | Eformat_ref of name                    (** R(label) [EX P020] *)
  | Epicture of string                    (** P'picspec' [EX P045] *)

and pfx = Plus | Minus | NegL              (** ^ logical not *)

(* ---------- declarations ---------- *)

type dim =
  | Dim_bound of expr * expr option       (** (lo:)hi  or  hi *)
  | Dim_star                              (** *   assumed size *)

and init =
  | Init_expr of expr
  | Init_rep of int * init list           (** N(n) replication form, coarse *)

(* attrs: raw (KEY, args); binding pass interprets. e.g. (STATIC, []),
   (FIXED, [(DEC?)...]) captured inside type_spec instead, see below. *)
and attr = { akey : string; aargs : expr list; atypes : basic_type list; apos : pos }
(* RETURNS(bit(1)) carries atypes; EXTERNAL('NAME') carries aargs. *)

and basic_type =
  | Tfixed of { dec : bool; prec : expr option; scale : expr option }
  | Tfloat of { prec : expr option }      (** FLOAT DECIMAL: rejected by
                                              compiler — kept parseable *)
  | Tchar of { varying : bool; len : expr option }
  | Tbit of { len : expr option }
  | Tptr
  | Tfile                       (* declare (f,g) file [EX COPY] *)
  | Tentry of { opts : basic_type list }

(* one declaration item, e.g.  x(10) fixed bin(15) static external('X') *)
and dcl =
  { dlevel : expr option                  (** leading 1/2/... level int *)
  ; dname : name
  ; ddims : dim list
  ; dtype : basic_type option
  ; dinit : init option
  ; dattrs : attr list
  ; dpre : (string * expr list) option    (** %include/%replace spliced
                                              inside a dcl list [EX DIOCOPY,
                                              CREATE %replace true by '1'b] *) }

(* ---------- statements ---------- *)

type io_opt = { io_key : string; io_val : expr option }   (** FILE(f) ... *)

type stmt =
  { st : stmt_kind; spos : pos; slabels : name list }
and stmt_kind =
  | Snull of pos                                   (* ; [EX P008] *)
  | Sdcl of dcl list
  | Sassign of { lhs : expr; rhs : expr }          (* simple x = e; *)
  | Sgoto of { tgt : name; subscript : expr list } (** goto z(i) computed [EX LABELS] *)
  | Sif of { cond : expr; then_ : stmt; els : stmt option }
  | Sdobegin of stmt list
  | Sdoto of { ind : name; from : expr; by : expr option;
               while_ : expr option; to_ : expr option;
               rep : expr option;              (* DO name=x REPEAT(e) [EX DFACT,
                                                  DIOCOPY `repeat(i+1) while(i^=..)`] *)
               body : stmt }
  | Sdowhile of { cond : expr; body : stmt }
  | Sdoforever of stmt
  | Sproc of block_stmt                            (* nested BEGIN/PROC *)
  | Sput of { stream : expr option; on_opts : io_opt list;
              kind : put_kind; items : put_item list }
  | Sget of { stream : expr option; on_opts : io_opt list;
              kind : get_kind; items : put_item list }
  | Sfilestmt of { key : string; file : expr option; opts : io_opt list }
      (* OPEN/CLOSE/... file statements [M §10]; file may be absent until bound *)
  | Sedit of { target : expr; opts : io_opt list }  (* EDIT FILE(f) ... *)
  | Sreadwv of { dir : string; file : expr; to_ : expr }  (* READ VARYING *)
  | Sreturn of expr option
  | Sstop of expr option
  | Sexit of name option
  | Son of { cond : string; handler : stmt }       (* ON con stmt; *)
  | Ssignal of { cond : string; target : expr option }
  | Selse of stmt                                  (* orphan ELSE *)
  | Sdeclare_fail of pos                           (* DECLARED/NOT>RESERVED *)
  | Sprocedure_stmt of { target : expr; args : expr list }
      (* name(args) or CALL name(args) [PROBE 28] *)
  | Salloc of { ptr : expr; based : expr option }
  | Sfree of expr list
  | Sassign_label of { labels : name list; to_ : expr }
  | Sformat of put_item list            (* FORMAT items; p'..' not an expr [EX P020] *)
  | Spicturestmt of pos                            (* reserved *)
  | Spreproc of { directive : string; args : string list }

and put_kind = List_ | Edit | Item | Editsk of int option

and put_item =
  | Pi_fmt of { fkey : string; fargs : expr list;
                fcount : expr option }             (** 4a counted item [EX DIOCALLS] *)
  | Pi_rep of expr * expr                          (** (x do n=0 to 3) [EX ACK] *)
  | Pi_repgrp of expr * put_item list              (** 2(skip,column(i),a) counted group [EX DEPREC, LOAN2] *)
  | Pi_data of expr                                  (** data-paren item *)
  | Pi_ctl of string * expr option                   (** SKIP/PAGE/LINE(n) *)
  | Pi_pic of string                                 (** P'picspec' [EX] *)
  | Pi_remote of name                                (** R(label) [EX P020] *)
  | Pi_group of put_item list                        (** nested (..) *)

and get_kind = List_ | Edit | Const_

(* ---------- procedures / compilation unit ---------- *)

and block_stmt =
  { blk : block; bpos : pos }

and block =
  { blabel : name option              (** stmt label: money: FORMAT(...) *)
  ; bname : name option               (** proc name or BEGIN[..] *)
  ; bparams : name list
  ; bopts : (string * expr list) list (** options(main), file, ... raw *)
  ; bsuffix : attr list               (** after ')' reentering static ext etc *)
  ; bdecls : dcl list
  ; bstmts : stmt list
  ; bkind : block_kind
  ; bendpos : Source.pos option   (** END-keyword line; BEGIN frames anchor
      at first inner stmt, else END line [EX P077B/P078A-D] *) }

and block_kind = Bproc | Bbegin | Bdo
