(* ocaml/hir/mir_numeric.ml — the pure numeric-domain algebra of the MIR backend
   (E2E-54/P2-DIFF-2 §P2-DIFF-2.4, Stage C).

   WHAT THIS IS.  mir_backend.ml proved every value of a program against a
   closed integer interval before emitting one MIR instruction.  The ALGEBRA of
   those intervals — the declared-precision window, containment, display, the
   exact endpoint arithmetic of + - * and negation, and the control-flow join
   hull — is a pure function of integers.  This module MOVES that algebra out of
   the emission module; it adds, widens or narrows NO rule (invariant 3 of
   §P2-DIFF-2.4): every function below is the byte-for-byte expression that
   `mir_backend` used to hold inline, and the backend's diagnostics, refusal
   order and emission context stay where they were.

   DEPENDENCY LAW (§P2-DIFF-2.4-2): this module imports NOTHING — no `Hir`, no
   `Target`, no `Diagnostic`, no `Backend`, no emission or mutable instruction
   state, no REL-80/byte layout, no compiler-global state.  The precision
   parameter `p` of [window] is the caller's already-extracted `FIXED BINARY(p,0)`
   precision; the type itself is never named here.

   MEASURED CONSTRAINT (why [join_env] did NOT move).  The pre-registration
   listed `join_env` as a candidate; it cannot move as written: the environment
   is `(int * int) Int_map.t` and `Int_map` is a GENERATIVE `Map.Make` instance
   in mir_backend.ml — a second `Map.Make (Int)` in this module would be a
   DISTINCT type (verified first-hand with `ocamlopt`: `int M1.M.t` is not
   `int M2.M.t`).  Only the pure `Some`/`Some` HULL EXPRESSION moves, as
   [iv_hull]; the `Map.merge` stays in the backend.  That is a documented
   deviation from the candidate list, not a failure of separability.

   This file is in ocaml/hir/ and is therefore covered by the F8 purity glob of
   tools/hir_test.py (the check is code-only, after the nested-comment strip);
   it carries no byte-layout vocabulary and no hex literal in its code. *)

(* The closed integer interval [a, b] of a value.  Same representation as the
   backend's `string * (int * int)` payload; the pair IS the interval. *)
type iv = int * int

(* §P1-m0.3: the declared-precision value window W(p) of FIXED BINARY(p,0) — the
   same ±(2^(p-1)-1) domain in which the byte-exact bin(15) goldens live. p is
   bounded by the profile ceiling (15), so OCaml int arithmetic on endpoints and
   on the four products below is exact (|v| <= 32767, products <= 2^30). *)
let window p =
  let lim = (1 lsl (p - 1)) - 1 in
  (- lim, lim)

let in_window (lo, hi) (a, b) = lo <= a && b <= hi

let show_iv (a, b) = "[" ^ string_of_int a ^ "," ^ string_of_int b ^ "]"

(* Literal text as written in the source; only a plain non-negative decimal
   integer (no sign, no leading zero, no suffix, at most 9 digits) is accepted
   (§P1-m0.3-1: a non-canonical literal refuses, it is never reinterpreted). *)
let decimal_int (s : string) : int option =
  let digits = String.length s > 0 && String.for_all (fun c -> c >= '0' && c <= '9') s in
  let canonical =
    String.length s <= 9 && (String.length s = 1 || s.[0] <> '0')
  in
  if digits && canonical then Some (int_of_string s) else None

(* The exact endpoint algebra of the three admitted binops and of negation.
   These are the ONLY arithmetic steps on interval endpoints in the backend
   (§P2-DIFF-2.4); the operator dispatch, the window proof and the emission
   remain in mir_backend.  [iv_sub] is the interval-difference law (the left
   endpoint minus the RIGHT endpoint of the subtrahend, and vice versa);
   [iv_mul] is the four-corner hull — exact, not an approximation, because the
   product of two monotone maps over a rectangle attains its extremes at the
   corners. *)
let iv_add (a, b) (c, d) = (a + c, b + d)

let iv_sub (a, b) (c, d) = (a - d, b - c)

let iv_mul (a, b) (c, d) =
  let c1 = a * c
  and c2 = a * d
  and c3 = b * c
  and c4 = b * d in
  (min (min c1 c2) (min c3 c4), max (max c1 c2) (max c3 c4))

let iv_neg (a, b) = (-b, -a)

(* §P1-m2.2 join law, the SOUND hull arm: a value is definite only when it is
   definite on BOTH incoming paths, and the interval that survives is the smallest
   one containing both — the `Some`/`Some` case of the backend's join. *)
let iv_hull (a, b) (c, d) = (min a c, max b d)
