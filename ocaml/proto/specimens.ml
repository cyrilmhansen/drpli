(* ocaml/proto/specimens.ml — two DR programs, hand-transcribed from DR's own
   listings (the .PRN beside each golden), used as the prototype's acceptance
   set.  Nothing here is lowered or parsed: the instruction sequences are exactly
   what DR's listing shows, which is what makes this an isolated test of the
   REPRESENTATION rather than a second compiler.

   Chosen deliberately:
     E29A  minimal -- header block, a CALL-by-external-symbol chain fixup, and
                 DR's 0x32/STA opcode quirk.  Tests whether the derived chain
                 placement rule is right where it plausibly should be.
     E25F  the relocation-sensitive case -- forward CALL sites with a CHAIN-ADDR
                 header, descriptor cells in the DATA segment, mid-stream
                 segment switches, and an integer constant relocated against
                 DATA.  This is the specimen whose chain-target bytes made me
                 publish (and retract) a false byte-parity claim, see C123. *)

(* Rel80 lives inside the wrapped production library `pli80`; aliasing
   it keeps these prototype sources readable without a prefix on every line. *)
module Rel80 = Pli80.Rel80

open Inst80
open Rel80

let cd = 0xcd (* CALL a16 *)
let lxi_b = 0x01
let lxi_h = 0x21
let mvi_a = 0x3e
let sta_dir = 0x32 (* DR's STA-direct opcode -- NOT 0x3c.  C079. *)
let shld = 0x22
let inx_h = 0x23
let lhld = 0x2a
let dcx_h = 0x2b
let mov_a_l = 0x7d
let mov_m_l = 0x72 (* MOV M,L -- DR uses it here as MOV M,D's neighbor; the
                      mnemonic label in the listing is DR's, the byte is what
                      matters [CMP M/SBB M lesson, step 3b] *)
let mov_l_a = 0x6f
let mov_m_h = 0x74
let xchg = 0xeb
let ret = 0xc9

(* header block shared by every DR program *)
let hdr nm =
  [
    link_sym t_progname None nm;
    link_sym t_req_library None "PLILIB";
    link_sym t_extdef None nm;
    link_sym t_def_public (Some (Code, 0)) nm;
  ]

(* ---------------------------------------------------------------- E29A ---- *)
(* e29a: procedure options(main);
     declare i fixed(7), f float;
     i = 1;
     stop;
   end e29a;
 *)
let e29a : program =
  {
    name = "E29A";
    code_size = 0x0e;
    pub = true;
    events =
      hdr "E29A"
      @ [
          (* DR's data area for this program is 5 bytes; it never writes a data
             byte, so there is no DATA-segment block at all *)
          link_at t_def_data_size (Some (Abs, 5));
          set_lc Code 0;
          (* LXI B,0200 -- the stack-pointer prologue, two ABSOLUTE bytes *)
          ins2 "lxi b" lxi_b (I16 0x0200);
          (* CALL ?START -- external symbol: opcode, absolute zero slot, and a
             CHAIN-EXT derived by the encoder *)
          ins2 "call ?START" cd (CallSym "?START");
          ins2 "mvi a,1" mvi_a (I8 1);
          (* STA I -- opcode byte plus ONE relocatable DATA word (C079) *)
          ins2 "sta i" sta_dir (Rel (Data, 0x0000));
          ins2 "call ?STOPX" cd (CallSym "?STOPX");
        ];
  }

(* ---------------------------------------------------------------- E25F ---- *)
(* e25f: procedure options(main);
     declare (a, b) fixed;
     a = 1;            LXI H,*D(0001) ; SHLD A
     b = 2;            INX H ; SHLD B          (HL constant reuse!  C126)
     call s(a);        <data cell @0004 = 0000>; LXI H,*A(0004) ; CALL 0000
     call s(b);        <data cell @0006 = 0002>; LXI H,*A(0006) ; CALL *CODE(0014)
     stop;             CALL ?STOPX
     s: procedure (x); declare x fixed;
        x = x + 1;
     end s;
   end e25f;
 *)
let e25f : program =
  let open Inst80 in
  {
    name = "E25F";
    code_size = 0x33;
    pub = true;
    events =
      hdr "E25F"
      @ [
          link_at t_def_data_size (Some (Abs, 0x0a));
          set_lc Code 0;
          ins2 "lxi b,200" lxi_b (I16 0x0200);
          ins2 "call ?START" cd (CallSym "?START");
          (* `a = 1': DR writes the constant as two ABSOLUTE bytes (LXI H,0001).
             The `*' in its listing -- `LXI H,* A(0004)' -- marks a relocatable
             operand, and only those become RELOC records; a bare operand stays
             plain bytes.  I read the listing too fast and used Rel here, which
             produced 2 items where DR emits 3 bytes: byte 48 of the file, one
             bit out of place.  The distinction is exactly what the operand-class
             enumeration is for, and it is worth recording that I got it wrong
             even after naming the classes -- the class list only helps if the
             reading of the listing behind it is careful. *)
          ins2 "lxi h,1" lxi_h (I16 1);
          ins2 "shld a" shld (Rel (Data, 0));
          ins1 "inx h" inx_h;
          ins2 "shld b" shld (Rel (Data, 2));
          (* descriptor cell for call s(a): DATA word at 0004 holding 0000 *)
          DataWord (4, Rel (Data, 0));
          set_lc Code 0x10;
          ins2 "lxi h,*a(0004)" lxi_h (Rel (Data, 4));
          (* forward call, first site: zeros, and NO chain item of its own *)
          ins2 "call s (site 1)" cd (CallFwd "s");
          DataWord (6, Rel (Data, 2));
          set_lc Code 0x16;
          ins2 "lxi h,*a(0006)" lxi_h (Rel (Data, 6));
          (* second site: its target word IS the chain link -- a relocatable
             CODE value pointing at the immediately preceding site (C123) *)
          (* second site: DR's own bytes are `cd' + RELOC code 0014 -- the call
             word IS the chain link.  The prototype derives that from CallFwd
             rather than being told, and derives the header from Resolves. *)
          ins2 "call s (site 2)" cd (CallFwd "s");
          ins2 "call ?STOPX" cd (CallSym "?STOPX");
          (* `s:' -- the definition resolves the chain, and the header belongs
             HERE, not next to the reference *)
          Resolves "s";
          (* ---- s body, byte for byte from DR's listing ----
                001F: 5E 23 56 EB            MOV E,M / INX H / MOV L,M / XCHG
                0023: 22 <reloc D 0008>      SHLD X   (descriptor copy-in)
                0026: 2A <reloc D 0008>      LHLD X
                0029: 5E 23 56 EB 23 EB      re-load, INX, ...
                002F: 72 2B 73 C9            MOV M,D / DCX H / MOV M,A / RET *)
          ins1 "mov e,m" 0x5e;
          ins1 "inx h" inx_h;
          ins1 "mov l,m" 0x56;
          ins1 "xchg" xchg;
          ins2 "shld x" shld (Rel (Data, 8));
          ins2 "lhld x" lhld (Rel (Data, 8));
          ins1 "mov e,m" 0x5e;
          ins1 "inx h" inx_h;
          ins1 "mov l,m" 0x56;
          ins1 "xchg" xchg;
          ins1 "inx h" inx_h;
          ins1 "xchg" xchg;
          ins1 "mov m,d" mov_m_l;
          ins1 "dcx h" dcx_h;
          ins1 "mov m,a" 0x73;
          ins1 "ret" ret;
        ];
  }


(* ---------------------------------------------------------------- E27C ----
   TWO concurrent forward chains -- the case that decides whether the
   resolution-point rule (C135) is per-chain or per-site.  DR emits:
     code 0013: cd 00 00     call p1(a)   <- first (only) site of chain p1
     code 0019: cd 00 00     call p2(b)   <- first (only) site of chain p2
     ... CALL ?STOPX + CHAIN-EXT 001D ...
     LINK-CHAIN-ADDR code 0014   <- p1's header, immediately before p1's body
     <p1 body 001F-0032>
     LINK-CHAIN-ADDR code 001A   <- p2's header, immediately before p2's body
     <p2 body 0033-0047>
   So: one header per CHAIN (each chain here has a single site), placed at each
   chain's own resolution point, and the two are NOT emitted together at the end.
   This is also why E25F (two sites, one target) produced one header whose second
   site carried a RELOC CODE word instead of zeros -- the newest site is the head.
 *)
let e27c : program =
  {
    name = "E27C";
    code_size = 0x48;
    pub = true;
    events =
      hdr "E27C"
      @ [
          link_at t_def_data_size (Some (Abs, 0x0c));
          set_lc Code 0;
          ins2 "lxi b,200" lxi_b (I16 0x0200);
          ins2 "call ?START" cd (CallSym "?START");
          ins2 "lxi h,1" lxi_h (I16 1);
          ins2 "shld a" shld (Rel (Data, 0));
          ins1 "inx h" inx_h;
          ins2 "shld b" shld (Rel (Data, 2));
          DataWord (4, Rel (Data, 0));
          set_lc Code 0x10;
          ins2 "lxi h,*a(0004)" lxi_h (Rel (Data, 4));
          ins2 "call p1" cd (CallFwd "p1");
          DataWord (6, Rel (Data, 2));
          set_lc Code 0x16;
          ins2 "lxi h,*a(0006)" lxi_h (Rel (Data, 6));
          ins2 "call p2" cd (CallFwd "p2");
          ins2 "call ?STOPX" cd (CallSym "?STOPX");
          Resolves "p1";
          (* p1 body: x = x + 1 *)
          ins1 "mov e,m" 0x5e;
          ins1 "inx h" inx_h;
          ins1 "mov l,m" 0x56;
          ins1 "xchg" xchg;
          ins2 "shld x" shld (Rel (Data, 8));
          ins2 "lhld x" lhld (Rel (Data, 8));
          ins1 "mov e,m" 0x5e;
          ins1 "inx h" inx_h;
          ins1 "mov l,m" 0x56;
          ins1 "xchg" xchg;
          ins1 "inx h" inx_h;
          ins1 "xchg" xchg;
          ins1 "mov m,d" mov_m_l;
          ins1 "dcx h" dcx_h;
          ins1 "mov m,e" 0x73;
          ins1 "ret" ret;
          Resolves "p2";
          (* p2 body: y = y + 2 -- note 23 23, two INX H, not a runtime add *)
          ins1 "mov e,m" 0x5e;
          ins1 "inx h" inx_h;
          ins1 "mov d,m" 0x56;
          ins1 "xchg" xchg;
          ins2 "shld y" shld (Rel (Data, 0x0a));
          ins2 "lhld y" lhld (Rel (Data, 0x0a));
          ins1 "mov e,m" 0x5e;
          ins1 "inx h" inx_h;
          ins1 "mov d,m" 0x56;
          ins1 "xchg" xchg;
          ins1 "inx h" inx_h;
          ins1 "inx h" inx_h;
          ins1 "xchg" xchg;
          ins1 "mov m,d" mov_m_l;
          ins1 "dcx h" dcx_h;
          ins1 "mov m,e" 0x73;
          ins1 "ret" ret;
        ];
  }
