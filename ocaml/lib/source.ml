(** Source positions. PL/I-80 source uses CR or CRLF line endings; we accept
    LF, CR, CRLF. Lines are 1-based as displayed by the compiler listing. *)
type pos = { line : int; col : int }

let pos line col = { line; col }

let pp_pos fmt p = Format.fprintf fmt "line %d, col %d" p.line p.col

let zero = { line = 0; col = 0 }
