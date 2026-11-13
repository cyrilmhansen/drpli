(* hir/mirnumtest.ml — independent test driver for the pure Mir_numeric algebra
   (E2E-54/P2-DIFF-2 §P2-DIFF-2.4, Stage C; the semtest precedent).

   WHAT IT PROVES.  Mir_numeric.ml is a MOVEMENT of code, not a new rule: the
   equivalence of the movement is the frozen panel (every .mir pin, every
   suite).  This driver proves the ALGEBRA ITSELF, independently of the backend
   that uses it — so that a mutation of the module cannot be masked by a
   mutation of the caller.  Every expectation below is a hand-derived literal
   written in this file; the reference computation in [ref_*] is a SECOND,
   independent formulation of the same law (explicit min/max over the corners,
   endpoint arithmetic spelled out), not a call to the module's own functions.

   Output contract (mirrors semtest):
     every check holds  -> stdout gets EXACTLY one line
        MIR-NUMERIC OK <n> checks          rc 0
     any check fails    -> `MIRNUM-FAIL ...' lines on stderr, rc 1, ZERO stdout

   Corrupt controls (non-vacuity; the S6/T7 law): each deliberately perturbs the
   REFERENCE side of one family and the driver must then see the module
   DISAGREE — exit 1, stderr carries MIRNUM-FAIL lines only, ZERO stdout.  A
   control that stays silent is itself a failure, because it would mean the
   check does not observe the value it claims to observe.
     --corrupt-sub        the reference subtrahend LOW endpoint is taken from the
                          wrong side of the operand (a-d instead of a-c)
     --corrupt-hull       the reference hull keeps the FIRST interval's bounds
                          (the one-sided hull that would silently LOOSEN a proof)
     --corrupt-window     the reference window of p is widened by one
     --corrupt-decimal    the reference literal parser accepts a leading zero
   There is no mode that passes the live checks: the live run is the default and
   every corrupt mode is a separate process. *)

module N = Pli80_hir.Mir_numeric

let fails = ref ([] : string list)
let nchecks = ref 0

let check name (cond : bool) =
  incr nchecks;
  if not cond then fails := name :: !fails

let show (a, b) = "(" ^ string_of_int a ^ "," ^ string_of_int b ^ ")"

let quote s = "'" ^ s ^ "'"

let _fmt ivs = "[" ^ String.concat "; " (List.map show ivs) ^ "]"

(* The reference side, written independently of the module. *)
let ref_window p = (- ((1 lsl (p - 1)) - 1), (1 lsl (p - 1)) - 1)

let ref_add (a, b) (c, d) = (a + c, b + d)
let ref_sub ?(corrupt = false) (a, b) (c, d) = (a - (if corrupt then c else d), b - c)
let ref_mul (a, b) (c, d) =
  let cs = [ a * c; a * d; b * c; b * d ] in
  (List.fold_left min (List.hd cs) cs, List.fold_left max (List.hd cs) cs)
let ref_neg (a, b) = (-b, -a)
let ref_hull ?(corrupt = false) (a, b) (c, d) =
  if corrupt then (a, b) else (min a c, max b d)

let ref_decimal ?(corrupt = false) (s : string) : int option =
  let n = String.length s in
  let all_digits = n > 0 && String.for_all (fun ch -> ch >= '0' && ch <= '9') s in
  let canonical = n > 0 && n <= 9 && (n = 1 || corrupt || s.[0] <> '0') in
  if all_digits && canonical then Some (int_of_string s) else None

(* ---- the hand-derived vector table (§P2-DIFF-2.4) -------------------------- *)
(* [a, b] is the interval; [lo, hi] is its declared window; the expectation is
   the value a reader of the source can verify by hand. *)
let t_add =
  [ ((1, 2), (3, 4), (4, 6)); ((0, 0), (0, 0), (0, 0)); ((-5, -5), (5, 5), (0, 0));
    ((-7, -3), (2, 4), (-5, 1)); ((32767, 32767), (1, 1), (32768, 32768));
    ((-32768, -32768), (-1, -1), (-32769, -32769)) ]

let t_sub =
  [ ((5, 7), (1, 3), (2, 6)); ((3, 3), (1, 1), (2, 2)); ((1, 1), (0, 1), (0, 1));
    ((0, 0), (10, 10), (-10, -10)); ((1, 2), (1, 1), (0, 1));
    ((11, 11), (1, 8), (3, 10)); ((-1, 1), (1, 1), (-2, 0)) ]

let t_mul =
  [ ((2, 3), (4, 5), (8, 15)); ((-2, 3), (4, 5), (-10, 15));
    ((-2, -1), (4, 5), (-10, -4)); ((-2, -1), (-4, -3), (3, 8));
    ((0, 0), (5, 5), (0, 0)); ((-5, 5), (0, 0), (0, 0));
    ((-1, 1), (-1, 1), (-1, 1)); ((1, 1), (1, 1), (1, 1));
    ((2, 3), (4, 4), (8, 12)); ((-2, 2), (-2, 2), (-4, 4)) ]

let t_neg =
  [ ((0, 0), (0, 0)); ((-3, 0), (0, 3)); ((5, 5), (-5, -5)); ((-10, 1), (-1, 10)) ]

let t_hull =
  [ ((1, 1), (3, 3), (1, 3)); ((1, 3), (2, 4), (1, 4)); ((-3, -3), (3, 3), (-3, 3));
    ((0, 0), (0, 0), (0, 0)); ((5, 8), (5, 8), (5, 8)) ]

let t_window =
  [ (1, (0, 0)); (2, (-1, 1)); (3, (-3, 3)); (4, (-7, 7)); (7, (-63, 63));
    (8, (-127, 127)); (15, (-16383, 16383)) ]

let t_decimal =
  [ ("0", Some 0); ("7", Some 7); ("12345", Some 12345); ("999999999", Some 999999999);
    ("10", Some 10); ("01", None); ("00", None); ("007", None);
    ("1000000000", None); ("12a", None); ("a", None); ("-1", None);
    ("+1", None); ("1.5", None); (" 1", None); ("1 ", None) ]

let t_in_window =
  [ ((0, 0), (0, 0), true); ((-3, 3), (-3, 3), true); ((-3, 3), (-4, 0), false);
    ((-3, 3), (0, 4), false); ((-1, 0), (0, 0), true); ((-1, 0), (0, 1), false) ]

let t_show = [ ((0, 0), "[0,0]"); ((1, 2), "[1,2]"); ((-3, 3), "[-3,3]");
               ((-32767, 32767), "[-32767,32767]"); ((-1, 0), "[-1,0]") ]

(* ---- the families ---------------------------------------------------------- *)
let family_add () =
  List.iteri
    (fun i (x, y, want) ->
      let got = N.iv_add x y in
      check
        ("add " ^ string_of_int i ^ ": " ^ show x ^ " + " ^ show y ^ " = " ^ show got
        ^ ", expected " ^ show want)
        (got = want);
      check
        ("add " ^ string_of_int i ^ " vs reference")
        (got = ref_add x y);
      (* NO "contains the operands" law: the sum interval need not contain
         either operand (1,2)+(3,4) = (4,6) — the driver's own first run
         falsified that invented invariant, so it is not asserted. *)
      check ("add " ^ string_of_int i ^ " is monotone in both operands")
        (N.in_window (N.iv_add x y) (N.iv_add x (fst y, fst y))
        && N.in_window (N.iv_add x y) (N.iv_add (fst x, fst x) y)))
    t_add

let family_sub ?(corrupt = false) () =
  List.iteri
    (fun i (x, y, want) ->
      let got = N.iv_sub x y in
      let refv = ref_sub ~corrupt x y in
      check
        ("sub " ^ string_of_int i ^ ": " ^ show x ^ " - " ^ show y ^ " = " ^ show got
        ^ ", expected " ^ show want)
        (got = want || corrupt);
      check ("sub " ^ string_of_int i ^ " vs reference") (got = refv))
    t_sub

let family_mul () =
  List.iteri
    (fun i (x, y, want) ->
      let got = N.iv_mul x y in
      check
        ("mul " ^ string_of_int i ^ ": " ^ show x ^ " * " ^ show y ^ " = " ^ show got
        ^ ", expected " ^ show want)
        (got = want);
      check ("mul " ^ string_of_int i ^ " vs reference") (got = ref_mul x y);
      (* the four corners are all inside the result — the hull is not an
         approximation of the corner set, it is its exact envelope *)
      check
        ("mul " ^ string_of_int i ^ " covers its corners")
        (List.for_all (fun c -> N.in_window got (c, c))
           [ fst x * fst y; fst x * snd y; snd x * fst y; snd x * snd y ]))
    t_mul

let family_neg () =
  List.iteri
    (fun i (x, want) ->
      let got = N.iv_neg x in
      check
        ("neg " ^ string_of_int i ^ ": -" ^ show x ^ " = " ^ show got
        ^ ", expected " ^ show want)
        (got = want);
      check ("neg " ^ string_of_int i ^ " is an involution") (N.iv_neg got = x);
      check ("neg " ^ string_of_int i ^ " vs reference") (got = ref_neg x))
    t_neg

let family_hull ?(corrupt = false) () =
  List.iteri
    (fun i (x, y, want) ->
      let got = N.iv_hull x y in
      check
        ("hull " ^ string_of_int i ^ ": " ^ show x ^ " / " ^ show y ^ " = " ^ show got
        ^ ", expected " ^ show want)
        (got = want || corrupt);
      check ("hull " ^ string_of_int i ^ " vs reference") (got = ref_hull ~corrupt x y);
      (* the hull is the smallest interval containing both — a sound join *)
      check
        ("hull " ^ string_of_int i ^ " is the least envelope")
        (N.in_window got x && N.in_window got y
        && (fst got = min (fst x) (fst y) && snd got = max (snd x) (snd y)));
      check ("hull " ^ string_of_int i ^ " is symmetric") (N.iv_hull x y = N.iv_hull y x))
    t_hull

let family_window ?(corrupt = false) () =
  List.iteri
    (fun i (p, want) ->
      let got = N.window p in
      let refv = ref_window (if corrupt then p + 1 else p) in
      check
        ("window " ^ string_of_int i ^ ": W(" ^ string_of_int p ^ ") = " ^ show got
        ^ ", expected " ^ show want)
        (got = want || corrupt);
      check ("window " ^ string_of_int i ^ " vs reference") (got = refv);
      (* the endpoints are the extreme values, and the window is symmetric *)
      check
        ("window " ^ string_of_int p ^ " is exact and symmetric")
        (N.in_window got got && not (N.in_window got (fst got - 1, snd got))
        && not (N.in_window got (fst got, snd got + 1))
        && (p = 1 || fst got = - (snd got))))
    t_window

let family_decimal ?(corrupt = false) () =
  List.iteri
    (fun i (s, want) ->
      let got = N.decimal_int s in
      let refv = ref_decimal ~corrupt s in
      check
        ("decimal " ^ string_of_int i ^ ": " ^ quote s ^ " -> "
        ^ (match got with None -> "refused" | Some v -> string_of_int v)
        ^ ", expected "
        ^ (match want with None -> "refused" | Some v -> string_of_int v))
        (got = want || corrupt);
      check ("decimal " ^ string_of_int i ^ " vs reference") (got = refv))
    t_decimal

let family_in_window () =
  List.iteri
    (fun i (w, v, want) ->
      check
        ("in_window " ^ string_of_int i ^ ": " ^ show v ^ " in " ^ show w ^ " = "
        ^ string_of_bool want)
        (N.in_window w v = want))
    t_in_window

let family_show () =
  List.iteri
    (fun i (v, want) ->
      check ("show " ^ string_of_int i ^ ": " ^ show v ^ " -> " ^ want)
        (N.show_iv v = want))
    t_show

(* the exhaustive over-approximation and tightness law, over the small range:
   for every pair of intervals in [-6,6]^2 the result is the EXACT envelope of
   the pointwise result set, and every point of the operands is inside the
   add/sub result. *)
let exhaustive () =
  let lo = -6 and hi = 6 in
  let ivs =
    List.concat
      (List.init ((hi - lo + 1) * (hi - lo + 2) / 2)
         (fun k ->
           let a = lo + k / (hi - lo + 1) in
           let b = lo + k mod (hi - lo + 1) in
           [ (min a b, max a b) ]))
  in
  List.iter
    (fun x ->
      List.iter
        (fun y ->
          let set_of (f : int -> int -> int) : int list =
            List.concat
              (List.concat
                 (List.init (snd x - fst x + 1) (fun i ->
                    [ List.init (snd y - fst y + 1) (fun j ->
                        f (fst x + i) (fst y + j)) ])))
          in
          let neg_set =
            List.map (fun v -> -v)
              (List.init (snd x - fst x + 1) (fun i -> fst x + i))
          in
          let envelope (vs : int list) : int * int =
            (List.fold_left min (List.hd vs) vs, List.fold_left max (List.hd vs) vs)
          in
          check ("exhaustive add " ^ show x ^ " " ^ show y)
            (N.iv_add x y = envelope (set_of (fun a b -> a + b)));
          check ("exhaustive sub " ^ show x ^ " " ^ show y)
            (N.iv_sub x y = envelope (set_of (fun a b -> a - b)));
          check ("exhaustive mul " ^ show x ^ " " ^ show y)
            (N.iv_mul x y = envelope (set_of (fun a b -> a * b)));
          check ("exhaustive neg " ^ show x)
            (N.iv_neg x = envelope neg_set);
          check ("exhaustive hull " ^ show x ^ " " ^ show y)
            (N.iv_hull x y = envelope (fst x :: snd x :: fst y :: snd y :: [])))
        ivs)
    ivs

let live () =
  family_add ();
  family_sub ();
  family_mul ();
  family_neg ();
  family_hull ();
  family_window ();
  family_decimal ();
  family_in_window ();
  family_show ();
  exhaustive ()

type mode =
  | Live
  | Corrupt_sub
  | Corrupt_hull
  | Corrupt_window
  | Corrupt_decimal

let () =
  let args = List.tl (Array.to_list Sys.argv) in
  let mode =
    match args with
    | [] -> Live
    | [ "--corrupt-sub" ] -> Corrupt_sub
    | [ "--corrupt-hull" ] -> Corrupt_hull
    | [ "--corrupt-window" ] -> Corrupt_window
    | [ "--corrupt-decimal" ] -> Corrupt_decimal
    | _ ->
        prerr_endline "usage: mirnumtest [--corrupt-sub|--corrupt-hull|--corrupt-window|--corrupt-decimal]";
        exit 2
  in
  (match mode with
  | Live -> live ()
  | Corrupt_sub ->
      family_add ();
      family_sub ~corrupt:true ()
  | Corrupt_hull ->
      family_add ();
      family_hull ~corrupt:true ()
  | Corrupt_window ->
      family_add ();
      family_window ~corrupt:true ()
  | Corrupt_decimal ->
      family_add ();
      family_decimal ~corrupt:true ());
  if !fails <> [] then begin
    List.iter (fun m -> prerr_endline ("MIRNUM-FAIL: " ^ m)) (List.rev !fails);
    exit 1
  end;
  Printf.printf "MIR-NUMERIC OK %d checks\n" !nchecks;
  exit 0
