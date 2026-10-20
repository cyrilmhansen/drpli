(* ocaml/proto/inst80.ml — ARCH-1 PROTOTYPE.  A symbolic 8080 instruction
   representation whose operands carry an EXPLICIT RELOCATION CLASS, plus a
   location counter that is threaded through the encoder instead of living in
   mutable program state.

   ISOLATED ON PURPOSE: nothing in ocaml/lib or ocaml/bin depends on this file,
   it is not linked into pli80c, and it does not parse or lower PL/I.  The
   programs in specimens.ml are hand-transcribed from DR's own listings.  The
   question being tested is narrow (ARCH-0 §9 step 2 / §11): can the bytes of a
   DR .REL -- including record ORDER and the quirks -- be produced from an
   instruction-level representation, without the author ever naming a bit offset
   or relying on the order in which side effects happened to happen?

   Deliberate design choices, each one a departure from production codegen.ml:

   1. Operand classes are named after what they CONTRIBUTE to the bitstream, not
      after mnemonics.  DR's own output needs all four:
        I8   -- one absolute byte            (MVI A,n / opcode bytes)
        I16  -- two absolute bytes, no reloc (LXI B,0200 / the zero slot of a CALL)
        Rel  -- ONE relocatable 16-bit item  (LXI H,*A(addr), SHLD, STA, and --
                bizarrely but verifiably -- DR's encoding of an INTEGER CONSTANT:
                E25F's `a = 1' emits 0x21 + RELOC(Data,0001), a data-relative
                relocatable value for the literal 1.  That is exactly the kind of
                fact a mnemonic-driven layer gets wrong and a class-driven one
                cannot.)
        CallSym  -- a CALL whose target is an unresolved external symbol: opcode,
                    two absolute zero bytes, and a CHAIN-EXT item whose value is
                    the ADDRESS OF THE SLOT.  The class carries the fixup, so the
                    caller cannot forget it -- in production this pairing is a
                    convention (89 call_ext sites) rather than a type.
   2. The location counter is a VALUE passed to the encoder, not mutable state.
      ARCH-0 §11 named this as the prototype's kill criterion -- "if Inst ->
      rel_item cannot be written without a location counter threaded through the
      emitter, the abstraction is wrong".  It CAN be written that way, and this
      file is the demonstration: threading is not the failure mode, and the
      threaded form keeps emission pure (see encode's signature: a fold).
   3. Order constraints are DATA.  Segment switches (SET-LC) and chain items are
      explicit events in the plan, so the encoder's output order is a property of
      the plan, not of the sequence in which something was mutated.  Where a rule
      CAN be derived mechanically (CallSym's CHAIN-EXT), it is derived here;
      where DR's placement is not derivable from the instruction it nominally
      belongs to, the plan says so out loud -- and that boundary is the actual
      result of this experiment, reported by arch1.ml. *)

(* Rel80 lives inside the wrapped production library `pli80`; aliasing
   it keeps these prototype sources readable without a prefix on every line. *)
module Rel80 = Pli80.Rel80

type operand =
  | I8 of int
  | I16 of int
  | Rel of Rel80.seg * int
  | CallSym of string
  | CallFwd of string
      (* a CALL to a target that is not defined yet.  The class carries the
         chain: the FIRST site writes two absolute zero bytes and becomes the
         chain head; every LATER site writes one relocatable CODE word holding
         the current head, and becomes the new head.  That is DR's own shape --
         E25F's `call s(a)' at 0013 is zeros, its `call s(b)' at 0019 carries
         RELOC code 0014 -- and it is why production prepends `fcalls' (head =
         most recent).  Here it is a rule over data instead of a list direction. *)

type ins = { mnem : string; opcode : int list; arg : operand option }

(* How many BYTES an instruction occupies.  This is a property of the
   instruction, derived from its operand class -- not a count of REL items, which
   is what I did first: `STA dir' is 3 bytes but only 2 items (opcode Data +
   operand Reloc), so counting items made the location counter drift and E29A's
   second chain fixup pointed at 000B instead of 000C (the opcode byte).  A
   Reloc item is 2 bytes; a Data item is 1. *)
let ins_bytes (i : ins) : int =
  List.length i.opcode
  +
  match i.arg with
  | None -> 0
  | Some (I8 _) -> 1
  | Some _ -> 2

(* one instruction -> the items it occupies, and the address of its 16-bit slot
   if it has one (needed for chain fixups) *)
let emit_ins (lc : int) (i : ins) :
    Rel80.rel_item list * int * (int * string) option =
  let n = List.length i.opcode in
  let items =
    List.map (fun b -> Rel80.Data b) i.opcode
    @
    match i.arg with
    | None -> []
    | Some (I8 v) -> [ Rel80.Data v ]
    | Some (I16 v) ->
        [ Rel80.Data (v land 0xff); Rel80.Data ((v lsr 8) land 0xff) ]
    | Some (Rel (seg, v)) -> [ Rel80.Reloc (seg, v) ]
    | Some (CallSym _ | CallFwd _) ->
        (* placeholder: the fold below decides, because a forward site after the
           first one is a RELOC word rather than two absolute zeros *)
        [ Rel80.Data 0; Rel80.Data 0 ]
  in
  let slot_addr = lc + n in
  let chain =
    match i.arg with
    | Some (CallSym sym) -> Some (slot_addr, sym)
    | _ -> None
  in
  (items, slot_addr, chain)

(* a program is a PLAN: declared events in emission order.  No event knows about
   bit positions; the encoder maintains the counters. *)
type event =
  | LinkAt of Rel80.rel_item
      (* a LINK item placed exactly here in the plan.  Used for the header block
         (PROG-NAME, REQ-LIBRARY, EXTDEF, DEF-PUBLIC) AND for DEF-DATA-SIZE,
         whose position is NOT constant across programs: E29A puts it before the
         code SET-LC, while N306 puts it after its static-data block.  Making it
         a plan event rather than a generated field is what lets the prototype be
         honest about that -- production codegen encodes the position by
         construction, which is fine until you need to know it is variable. *)
  | SetLc of Rel80.seg * int
  | Ins of ins
  | DataWord of int * operand
      (* a DATA-segment word written at a declared address, e.g. a descriptor cell
         holding the address of an argument.  Needs its own SET-LC because DR
         re-selects the location counter before every such write. *)
  | ChainItem of Rel80.rel_item
  | Resolves of string
      (* an explicitly placed chain LINK item, for the cases where DR's placement
         is NOT a function of the instruction it refers to -- see arch1.ml's
         report, which counts how often this escape hatch is needed. *)
  | Trailer of Rel80.rel_item

type program = {
  name : string;
  code_size : int;   (* DR's DEF-CODE-SIZE: always the last code byte + 1 *)
  pub : bool;          (* DEF-PUBLIC the program name (main entry) *)
  events : event list;
}

(* encode: fold over the plan, threading (segment, location counter).  Pure --
   there is no mutable state anywhere in this module. *)
let encode (p : program) : Rel80.rel_item list =
  let open Rel80 in
  let seg0, lc0 = (Code, 0) in
  (* `acc` is the REVERSE of the emitted stream (head = most recently emitted),
     so pushing a list xs in order is `List.rev_append xs acc` (= rev xs @ acc),
     and anything that must come AFTER xs in the output has to be pushed after
     that -- i.e. closer to the head.
     Two order mistakes here cost two iterations, and both are the same failure
     mode as production's fcalls-prepend-vs-calls-FIFO hazard (ARCH-0 §5.3):
       * first version pushed the chain item and then the instruction bytes, so
         every CHAIN-EXT landed BEFORE its CALL slot;
       * "fixing" it by pushing `List.rev xs` reversed the bytes of every
         instruction instead (STA emitted its Reloc before its 0x32 opcode byte),
         which reldump reports as DATA-vs-RELOC at bit 400 and `cmp` saw as a
         one-bit shift at byte 32.
     The lesson is the one already recorded twice in this project: a list
     direction cannot be reasoned about from the code that reads most naturally.
     Print the bytes. *)
  let push_items acc xs = List.rev_append xs acc in
  (* pending forward chains: (target name, address of the current head slot).
     Threaded through the fold, never mutated -- the prototype's answer to
     production's `fcalls' prepend-order hazard (ARCH-0 §5.3). *)
  let items, _, _, _ =
    List.fold_left
      (fun (acc, seg, lc, chains) ev ->
        match ev with
        | LinkAt it -> (it :: acc, seg, lc, chains)
        | SetLc (s, a) ->
            (Link (t_set_lc, Some (s, a), None) :: acc, s, a, chains)
        | DataWord (addr, op) ->
            let switch = Link (t_set_lc, Some (Data, addr), None) in
            let items, _, _ =
              emit_ins addr { mnem = ""; opcode = []; arg = Some op }
            in
            (* DR selects the location counter BEFORE writing the word, and
               "before" in a reversed accumulator means pushed FIRST (deeper),
               then the word items go on top of it.  I had this inverted and the
               dump came out SET-LC, SET-LC with the word stranded before the
               first switch -- the third order mistake in 200 lines, all three of
               them list-direction errors.  A cleaner long-term answer is to make
               the accumulator a real queue with an append operation, which is
               what the prototype's report recommends. *)
            (push_items (switch :: acc) items, Data, addr + 2, chains)
        | Ins i ->
            let _items, _slot, chain = emit_ins lc i in
            let acc =
              match i.arg with
              | Some (CallFwd nm) ->
                  (* first site of a chain: absolute zeros, becomes the head.
                     later sites: a relocatable CODE word pointing at the
                     current head (DR's E25F: `RELOC code 0014'), and the new
                     slot becomes the head. *)
                  (match List.assoc_opt nm chains with
                   | None ->
                       push_items acc (Data (List.hd i.opcode) ::
                                       [ Data 0; Data 0 ])
                  | Some head ->
                       push_items acc
                         (Data (List.hd i.opcode) :: Reloc (Code, head) :: []))
              | _ ->
                  let items, _, _ = emit_ins lc i in
                  push_items acc items
            in
            let acc =
              (* the derived placement rule for EXTERNAL symbols: a CallSym's
                 chain item goes immediately AFTER the bytes that carry the slot
                 -- pushed last, because the accumulator is reversed *)
              match chain with
              | Some (addr, sym) ->
                  Link (t_chain_ext, Some (Code, addr), Some sym) :: acc
              | None -> acc
            in
            let chains =
              match i.arg with
              | Some (CallFwd nm) ->
                  let slot = lc + List.length i.opcode in
                  (nm, slot)
                  :: List.filter (fun (n, _) -> n <> nm) chains
              | _ -> chains
            in
            (acc, seg, lc + ins_bytes i, chains)
        | ChainItem it -> (it :: acc, seg, lc, chains)
        (* a definition RESOLVES the pending chain(s) for that name, and DR emits
           the CHAIN-ADDR header at that moment -- immediately before the first
           byte of the resolving body -- regardless of how many sites referenced
           it.  Two independent goldens pin the placement (E25F header at bit 826
           directly precedes `s' body at code 001F; E27C has one header per
           procedure, each immediately preceding its body), and the count is
           pinned across the whole chain-bearing set: E25C has 7 CHAIN-EXT and 8
           CALLs but ONE header, E26J has 8/9 and one, E27C has two targets and
           two headers.  So: one header per chain, at the resolution point.
           This event replaces the hand-placed ChainItem I needed in the first
           two drafts -- the escape hatch turned out to be an unfinished rule. *)
        | Resolves nm ->
            (match List.assoc_opt nm chains with
             | Some head ->
                 (Link (t_chain_addr, Some (Code, head), None) :: acc, seg, lc,
                  List.filter (fun (n, _) -> n <> nm) chains)
             | None -> (acc, seg, lc, chains))
        | Trailer it -> (it :: acc, seg, lc, chains))
      ([], seg0, lc0, []) p.events
  in
  let rev = items in
  (* the header is declared explicitly in the plan, so ordering is authored, not
     implied; the tail records are generated from the declared sizes *)
  List.rev rev
  @ [
      Link (t_def_code_size, Some (Code, p.code_size), None);
      Link (t_end_program, Some (Code, 0), None);
      Link (t_end_file, None, None);
    ]

(* convenience constructors, so a specimen reads like an instruction list.  They
   yield EVENTS, not bare instructions: the plan is the only place ordering is
   decided, and construction must not be able to bypass it. *)
let ins1 mnem op = Ins { mnem; opcode = [ op ]; arg = None }
let ins2 mnem op arg = Ins { mnem; opcode = [ op ]; arg = Some arg }
let set_lc s a = SetLc (s, a)
let link_at nm v = LinkAt (Rel80.Link (nm, v, None))
let link_sym nm v s = LinkAt (Rel80.Link (nm, v, Some s))
