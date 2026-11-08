(* ocaml/hir/backend.ml — minimal backend contract (E2E-54/P0, brief §7).

   The interface is deliberately format-agnostic: it assumes no ELF, no
   REL-80 record layout, no 8080 register set and no MIR-specific IR nodes
   (brief §7). It leaves room for native AOT code generation, library /
   shared-object output, WASM output, and interpreter-style backends; P0
   builds none of them and no plugin registry (brief §7).

   Compile-time tests only, as §P0.2 prescribes: the signature, the [Null]
   instance checked against it, and the [Driver] functor instantiated with
   [Null]. A functor application is verified by the type checker at build
   time; nothing here runs at program start.

   Deviation from PLAN §P0.2 (recorded in RESULTS §P0): this unit lives in
   ocaml/hir/ (library pli80_hir), NOT ocaml/lib/ — E2E-54/P0 hop-3 F1
   evidence: any unit or stanza sharing the historical exe directory moves
   pli80c.exe. The module is referenced by NOTHING in the historical
   pipeline and is not linked into pli80c.exe (falsifiers F1/F7). *)

(* The backend contract of brief §7, adapted to the measured module names. *)
module type BACKEND = sig
  (** A backend turns a typed, target-independent [Hir.program] — interpreted
      under an explicit [Target.profile] — into its own opaque artifact, or
      into a non-empty, positioned list of [Diagnostic.t] refusals. Profile
      fields marked [Unknown] must never be silently defaulted: a backend
      that needs one refuses (target.ml provenance contract). *)
  type artifact

  val compile :
    profile:Target.profile ->
    Hir.program ->
    (artifact, Diagnostic.t list) result
end

module type S = BACKEND

(* Witness 1: [Null] satisfies [BACKEND] — the annotation is itself a
   compile-time test. Null lowers nothing: it accepts the program and
   produces no payload. It exists to exercise the contract and to serve
   tooling that only needs the HIR dump path. *)
module Null : BACKEND = struct
  type artifact = unit

  let compile ~(profile : Target.profile) (_prog : Hir.program)
    : (artifact, Diagnostic.t list) result =
    (* Null receives but deliberately does not consult the profile. *)
    ignore profile;
    Ok ()
end

(* Witness 2: [Driver] is written generically over any [BACKEND]; the
   functor application below type-checks the whole call plumbing for a
   concrete instance without committing to any artifact format. *)
module Driver (B : BACKEND) = struct
  let run ~(profile : Target.profile) (prog : Hir.program)
    : (B.artifact, Diagnostic.t list) result =
    B.compile ~profile prog
end

module _ = Driver (Null)
