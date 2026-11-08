(* lib/target.ml — minimal target semantic profile (E2E-54/P0, brief §4).

   A profile describes LANGUAGE semantics a backend must honour. Physical ABI
   choices (cell sizes, calling conventions, relocation models) deliberately do
   NOT appear here — they belong to backends.

   Every field carries its PROVENANCE. The rule is strict (brief §4): never
   invent a historical rule to populate a field. A field is
   - [Oracle_backed ptr] only when pre-existing oracle evidence in THIS
     repository (claim id or golden path) supports it, and the pointer must be
     verifiable;
   - [Language_rule txt] for language-level rules (specification/established
     semantics) that are NOT claims about DR's internals;
   - [Unknown] when nothing supports any value — consumers must refuse or ask,
     never default silently.
   The P0 prototype adds ZERO new oracle measurements, so the only
   Oracle_backed fields are pointers to E2E-era evidence that predates P0. *)

type provenance =
  | Oracle_backed of string (* pointer to EXISTING evidence (claim/golden path) *)
  | Language_rule of string (* language-level justification, NOT a DR claim *)
  | Unknown (* requires a decision or an oracle experiment (preregistered, separate) *)

type 'a field = { value : 'a option; source : provenance }

type profile = {
  name : string;
  (* precision applied to an unsuffixed integer literal (the ONLY way Hir's
     literal typing can be fixed); None => literals cannot be typed => refuse. *)
  default_integer_precision : int field;
  (* ceiling on FIXED precision the profile will accept, when the target has one. *)
  max_fixed_precision : int field;
  (* how result types of fixed arithmetic are computed. Unmeasured for DR's $V —
     see docs/architecture/backend-boundary.md §4: expression typing is entangled
     with instruction selection in codegen.ml and was NOT extracted. *)
  fixed_arithmetic_typing : unit field;
  (* overflow behaviour of fixed arithmetic (saturation/wrap/trap/condition). *)
  overflow_behavior : unit field;
  (* rounding rules for fixed-point conversions. *)
  rounding_rules : unit field;
  (* floating-point semantics (representation, range, traps). *)
  float_semantics : unit field;
  (* assumed character set/encoding for CHARACTER data. *)
  character_encoding : unit field;
  (* named constructs the profile forbids outright (target-specific restrictions). *)
  semantic_restrictions : string list;
}

let unknown_field () = { value = None; source = Unknown }
let unit_unknown () = { value = None; source = Unknown }

(* The historical target: semantics that EXISTING oracle evidence already pins.
   Fields not backed by an existing claim/golden pointer stay Unknown. *)
let dr_pli80_v1_4 = {
  name = "dr-pli80-v1.4";
  default_integer_precision =
    { value = Some 15;
      (* SUBSET CHOICE, not a measured DR semantic: every byte-exact DR witness for
         fixed arithmetic in this repository is within the bin(15)/±32767 domain the
         compiler's own literal checks admit (bind.ml dr_max_fixed_prec, bin15_fits;
         E1415..E1432/E15D09..E15D31, golden/e2e11f). DR's internal literal precision
         is UNMEASURED [TBD]; if a future preregistered experiment contradicts this,
         the field — and only the field — changes. *)
      source = Language_rule "P0 domain restriction to the measured bin(15) literal window; not a claim about DR internals" };
  max_fixed_precision =
    { value = Some 15;
      (* DR refuses bin(16)/dec(16) outright: measured pre-E2E-54 evidence. *)
      source = Oracle_backed "E1415..E1432 / E15D09..E15D31 (golden/e2e11f); enforced at bind.ml:dr_max_fixed_prec" };
  fixed_arithmetic_typing =
    { value = None; (* DR's internal result-precision rules are unmeasured. *)
      source = Language_rule "max(p1,p2)+1 for +,- and p1+p2 for * applied by Hir_build as an explicitly labelled LANGUAGE rule (docs/architecture/backend-boundary.md §4)" };
  overflow_behavior = unit_unknown ();
  rounding_rules = unit_unknown ();
  float_semantics = unit_unknown ();
  character_encoding =
    { value = None;
      (* DR's characters are measured as literal bytes in goldens, but a profile-level
         encoding law (full character set) is not independently characterized. *)
      source = Unknown };
  semantic_restrictions = [ "FIXED precision ceiling 15 (Oracle_backed above)" ];
}

(* A deliberately EMPTY sketch: what a modern 32-bit target must DECIDE before
   any lowering can start. Nothing is populated except the name — an honest
   all-unknown profile, the P0 point being that Unknown is representable. *)
let generic32_unspecified = {
  name = "generic32-unspecified";
  default_integer_precision = unknown_field ();
  max_fixed_precision = unknown_field ();
  fixed_arithmetic_typing = unit_unknown ();
  overflow_behavior = unit_unknown ();
  rounding_rules = unit_unknown ();
  float_semantics = unit_unknown ();
  character_encoding = unit_unknown ();
  semantic_restrictions = [];
}

let lookup n =
  if String.equal n dr_pli80_v1_4.name then Some dr_pli80_v1_4
  else if String.equal n generic32_unspecified.name then Some generic32_unspecified
  else None
