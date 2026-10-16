(** PL/I-80 tokens. PL/I keywords are SOFT: the shipped corpus uses
    [default], [print], [label] etc. as identifiers (ENTER.PLI:
    "1 default static"), so the lexer only distinguishes lexical classes and
    the parser decides keyword-ness by position. Identifiers carry both the
    original case (for display) and an uppercase key (for comparison):
    PL/I-80 identifiers are case-insensitive. *)

type punct =
  | LParen | RParen
  | Comma | Semi | Colon
  | Star | Slash | Plus | Minus
  | StarStar            (** **  exponentiation *)
  | CharCat             (** || and // (both in corpus) *)
  | BitCat              (** !! bit concatenation [corpus] *)
  | Amp | Or            (** & ; Or is | or ! *)
  | AndThen | OrElse    (** &: and |: standard short-circuit forms; DR
                           SYNTAX on both [P068M probe37 => [M] gap] *)
  | Not                 (** ^  [corpus: if ^ (a = 'Y' ! ...)] *)
  | Eq | Ne             (** = and <> or >< (both in corpus) *)
  | Lt | Le | Gt | Ge
  | Arrow               (** -> pointer qualification [EX P022] *)
  | Dot                 (** . structure qualification [EX P022] *)
  | Xor                 (** ^= seen in DIOCOPY condition [needs probe] *)
  | Dollar              (** $ end-of-source sign *)
  | Percent             (** preprocessor directive sigil [M §11] *)

type num =
  { text : string       (** literal exactly as written *)
  ; exp_sign : [`Plus | `Minus | `None] }

type tok =
  | EOF
  | Ident of { orig : string; key : string }
  | Num of num
  | Str of { orig : string; value : string }  (** '...' with '' resolved *)
  | Bit of { value : string }                 (** '...'b *)
  | Punct of punct

let id key orig = Ident { key; orig }

(* Longest-match first. *)
let punct_list : (punct * string) list =
  [ (StarStar, "**"); (CharCat, "||"); (CharCat, "//"); (BitCat, "!!")
  ; (Arrow, "->"); (Xor, "^="); (Ne, "<>"); (Ne, "><"); (Ne, "~=")
  ; (Le, "<="); (Ge, ">=")
  ; (LParen, "("); (RParen, ")"); (Comma, ","); (Semi, ";"); (Colon, ":")
  ; (Dot, "."); (Dollar, "$")
  ; (Star, "*"); (Slash, "/"); (Plus, "+"); (Minus, "-")
  ; (AndThen, "&:"); (OrElse, "|:"); (Or, "|"); (Or, "!"); (Amp, "&"); (Not, "^"); (Not, "~")
  (* ~ seen in MPMCALLA/DIORAND; both ~ and ^ for NOT [corpus] *)
  ; (Eq, "="); (Lt, "<"); (Gt, ">"); (Percent, "%") ]

let show_punct = function
  | LParen -> "(" | RParen -> ")" | Comma -> "," | Semi -> ";" | Colon -> ":"
  | Star -> "*" | Slash -> "/" | Plus -> "+" | Minus -> "-"
  | StarStar -> "**" | CharCat -> "||" | BitCat -> "!!"
  | Amp -> "&" | Or -> "|" | Not -> "^" | AndThen -> "&:" | OrElse -> "|:"
  | AndThen -> "&:" | OrElse -> "|:"
  | Eq -> "=" | Ne -> "<>" | Lt -> "<" | Le -> "<=" | Gt -> ">" | Ge -> ">="
  | Arrow -> "->" | Dot -> "." | Xor -> "^=" | Dollar -> "$"
  | Percent -> "%"

let pp_tok fmt = function
  | EOF -> Format.fprintf fmt "end of source"
  | Ident { orig; _ } -> Format.fprintf fmt "identifier %s" orig
  | Num { text; _ } -> Format.fprintf fmt "literal %s" text
  | Str { orig; _ } -> Format.fprintf fmt "string %s" orig
  | Bit { value } -> Format.fprintf fmt "bit literal %s" value
  | Punct p -> Format.fprintf fmt "%s" (show_punct p)
