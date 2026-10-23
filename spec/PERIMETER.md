# Language perimeter: compiler-supported vs manual vs Subset G

Per project direction (2026-10): the FIRST target is the language actually
accepted by the PL/I-80 v1.4 compiler; the MANUAL-defined language is a
close second; NO bug-for-bug compatibility; long-term north star is the
ANSI X3J1 **Subset G** standard with DR deltas. Every original-compiler
rejection is therefore classified into one of three buckets before it
becomes a rule in our grammar/binder:

  [S] SUPPORTED      — compiler accepts; corpus-proven; reimplementation
                        follows compiler behaviour (primary target).
  [M] MANUAL-GAP     — manual documents the feature, compiler
                        rejects/misbehaves ⇒ DR INCOMPLETE implementation,
                        NOT perimeter. Reimplementation follows the
                        MANUAL; the divergence is a compiler bug we
                        deliberately do not clone.
  [C] CUT            — absent from both manual and compiler (full-ANSI
                        territory, or Subset-G cut). Not supported by
                        reimplementation at v1; parseable syntax may be
                        accepted-with-diagnostic for future extension.

## Classification table (evidence in spec/CLAIMS.md + spec/notes/)

| Feature | Compiler v1.4 | Manual | Class | Notes |
|---|---|---|---|---|
| `DECLARE x POINTER;` with no BASED referencing it | NOT IMP (p1) | §3.4 verbatim example `DECLARE X POINTER;`, §4.2 `(P,Q) POINTER` | **[M]** | Works when some `BASED(p)` exists (P063B/P067B) ⇒ dead-code check bug. We support pointer dcl unconditionally. **[E2E-26/P1] NOT REPRODUCED on DR v1.4 as of golden/e2e312d/e2e313d: PD2 (`declare p pointer;` never used), PD3 (unused pointer beside another variable), PD4 (uppercase `DECLARE X POINTER;`) and PD5 (lowercase `declare x pointer;`) all compile NO ERROR(S) in both passes and emit .REL. The trigger of the original observation is therefore narrower than this row implies and is unpinned; POINTER-without-BASED must NOT be treated as a language rule or as a required refusal. See spec/notes/e2e26-p1-pointer-based-address-model.md.** | **[E2E-26/P1 NOT REPRODUCED]: PD2 (`declare p pointer;' alone), PD3, PD4 (uppercase verbatim manual shape) and PD5 all compile clean in DR with a .REL and 0 errors, and all four are byte-exact in mine (golden/e2e312d, e2e313d). The old NOT IMP note came from a probe that also lacked the BASED it claims to reference; a lone POINTER declaration is accepted.** |
| `ALLOCATE v SET(p)` | accepted (p1 clean) | §6.5 documented | **[S]** | | **[E2E-26/P3 IMPLEMENTED for based FIXED BINARY(15)]: DR lowers `allocate <based-name> set(<ptr>)' to `LXI H,<bytes> / CALL ?ALLOP / SHLD <ptr>' (PB7, PB8 -- and PB6/PB13/PB14/PB15 give 5/3/1/3 for char(5)/dec(5)/bit(8)/char(3)). Mine reproduces PB7/PB8 byte-exactly and PB7 was LINKed and executed (`x=       100  y=       200 done'). `allocate <type-name> to p' is NOT a form DR accepts: PD6/PD8 get BASED REQ + SYNTAX and no .REL.** |
| `FREE p;` (pointer operand) | **BASED REQ** (p2) | DR §6.8 wording says pointer operand; **Subset G §5.7.2: FREE takes the BASED variable** | **[S + standard]** — DR CODE is standard; DR MANUAL text is wrong (erratum) | `FREE x;` works (P067C) = standard ✓ | **[E2E-26/P3]: confirmed from AV1 (`free p;' -> BASED REQ, no .REL, golden/e26av2). DR's accepted operand is a BASED NAME: `free q;' lowers to `LHLD <ptr> / CALL ?FREOP' (PD9 000C-000F, PB7 006B) and mine reproduces both byte-exactly. `free <pointer>' therefore refuses, citing DR's own diagnostic.** |
| `STRUCTURE` keyword on dcl head | dcl derails (NO DCL cascade) | never shown in dcl syntax (level numbers ARE the structure mechanism) | **[C]** for compiler-era; parse-accept as head synonym for future | P023 |
| `DEFAULT(ref)` attribute | SYNTAX (p1) | **no DEFAULT anywhere in Subset G reference (0 hits)** | **[C]** confirmed ✓ P025 |
| FLOAT DECIMAL(p) | CONFLICT | NOT in manual (0 occurrences) | **[C]** ✓ consistent with Subset-G cut | C024 |
| FLOAT BINARY(24) assign/arithmetic/calls/GET/conditions | **works, byte-exact** | §7 float ops | **[S]** | E2E-10 closed: FFACT, FLTPOLY, TEST accepted (9/41).  Value model C100/C101, suffix law C103/C103a (address-mode vs computed), relations C104, conjunction booleans C105, formal storage C106, GET path C107. |
| float `<>` in a condition | **1 ERROR IN PASS 2**, no .REL (R3075) | Subset G lists `<>` generally | **[M]** | compiler refuses; DEC `<>` works via JZ [C085], the float reader offers no equivalent. |
| whole-literal float arithmetic (`1.5 + 2.5`) | works via the DEC runtime (`?DLDOP/?DADOP/?QDCOP/?QCXOP/?QX8F4`) | §7 | **[S] not implemented** | compiler refuses loudly: emitting the float runtime instead would change the arithmetic, not just the bytes [R3044]. |
| FLOAT formal of a RECURSIVE procedure | works; DR copies the value into the declared cell at body entry [R3103] | §6.4 | **[S] not implemented** | refuses (N71) — data addresses match, the copy prologue is missing. |
| `FLOAT BINARY(p)` with p != 24 | cell is 4 bytes for every p probed [R3001/R3013] | Subset G lists BINARY(p) | **[S] storage only** | only binary(24) has a characterized value model; other precisions refuse so a `float binary(14)` program can never silently get 24-bit arithmetic. |
| dedup'd callee formal's declared cell | occupies NO storage; a written-RECURSIVE callee's cell does | not addressable in the manual | **[S]** | C106, six probes (R3093-R3102) + P401/NFACT/FFACT/R3104. |
| FILE attribute cluster (KEYED/ENVIRONMENT/TITLE...) | works | §10 | **[S]** | |
| level numbers, groups, qualified refs, group assign | works (COPY-level) | §4.2-4.3 | **[S]** | incl. per-member dims/types in group parens (parser round) |
| bare `PUT SKIP;` / `GET SKIP;` | works | §10 (control PUT) | **[S]** | |
| `REPEAT(e)` in DO | works: i := e per pass (P055B) | §6.5 general forms ("replaces the control variable") | **[S]** | no implicit termination |
| `^=` operator | works | **Subset G §1.1.2: `^=` = NOT EQUAL (standard ASCII substitution)**; `~=≡^=`?? (table: ~ ≡ ^, ! ≡ \|) | **[S + standard]** RESOLVED: NE → bit(1) result; P052E '1000' = bit(1) '1' widened into bit(4) (left-align pad) — DR consistent, our earlier "contradiction" was an artifact |
| `~`, `~=`, `><`, `//`, `||`, `!!` | work | `~`/`~=` not in manual tables; others ANSI | **[S-extension]** | |
| bit literal `'…'bN` | accepts N=1..4 (b5/b8 ⇒ p2 SYNTAX) | **Subset G §3.4.1.1: N = BITS PER DIGIT — base-4/8/16 digit encoding** (Kednos/Cowan ref), NOT plain repeat | **[S + standard]** | RESOLVED (probe25/26 + subsetg §3.4.1.1): all observations match: '1'b2→'01'(01000000) '11'b3→'001001' '111'b2→'010101' 'ffff'b4 = 16-bit all-ones; DR manual §init wording misleading. Display anomalies were left-align padding of correctly converted values. |
| binary `^` (XOR operator) | **pass-2 SYNTAX** (P052C/D) | Subset G §6.2.2.4 defines `^` binary EXCLUSIVE OR | **[M]** standard XOR missing from DR | reimpl may add; byte-parity track omits |
| bit-string display/ops generally | runs | documented types | **OPEN** — internal representation unknown (slot/reversal hypotheses in flight) | highest-value runtime unknown |
| FORMAT items `A,B,E,F,P,R,SKIP,LINE,PAGE,COLUMN,WIDTH`; counts `4a`, `2(...)`; `(x do n=..)` replication | work | §10.6-10.8 (A/B/E/F/P/R/SKIP/LINE/PAGE documented; counts documented for EDIT; `column/width` partially) | **[S]** | |
| PICTURE `p'...'` in format parens | works (v1.3+) | App D | **[S]** | '+'-picture scale anomaly [PROBE 40 round 4] |
| `x picture('...')` dcl form (PICTURE as declared type) | **SYNTAX (p1)** (P066B plain, P066C standard §1.2.3 spelling) | **Subset G HAS Pictured Data (§3.2.5, §1.2.3 example)** | **[M]** | DR implemented PICTURE only as the PUT/GET EDIT format item (App D) — declared pictured type missing. Long-term std-conformance list; byte-parity track follows DR. |
| subscripted label `c(1):`, label arrays (LABELS) | works+runs | §8 labels | **[S]** | |
| `end` as identifier | works (LOAN2) | identifier rules §1 | **[S]** — keywords are context-soft | |
| `%INCLUDE` textual splice, `%REPLACE name by lit` | works | §11 | **[S]** | directive-only span, ';' survives |
| `DCL` synonym | works | shown in shipped .DCL files | **[S]** | |
| ON/SIGNAL numeric condition designators (filtering) | works | §8.5 | **[S]** | |
| builtins | MOD ROUND CEIL LOG etc. via explicit calls | §12 | **[S]** | no auto-injection for plain conversions (P066A); ANNUITY CHAR/DEC mystery still open [PROBE 66: picture-in-format + entry(returns char varying) bisect] |
| shipped-sample defects (INVERT/MAININVT maxrow/maxcol undefined; CALL.PLI broken comment) | rejected/failed | n/a | **not language** — distribution artifacts | C013 |
| `PUT ... FROM (…)`/`TO` in FILE stmts, keyed ISAM suite | works | §10, App E | **[S]** | |
| POINTER arithmetic (`+=`) | ? | §3.4 says only = and -= defined | probe later | | **[E2E-26/P2]: still no DR sample. Assignment INTO a pointer cell is implemented only for the three measured right-hand shapes (addr(local), null(), copy from another pointer -- P063B/P041/PB3/P086M); anything else, including `p = p + 2' and `p = <integer>', refuses by name rather than storing an address-shaped guess.** |
| BASED of char / bit(8) / fixed dec(5) (store & read) | accepted by DR, ALLOCATE included | PB6/PB13/PB14/PB15 all compile with .REL | **[my gap]** | E2E-26/P2 admits only based FIXED BINARY(15); the others refuse at the layout switch and are pinned as negatives. PB6 measures the char route (`LHLD <p> / LXI D,<text> / MVI A,len / MOV B,A / CALL ?SMCCM'), which is store_char's existing SMCCM with LHLD in place of LXI H. |
| BASED STRUCTURE with FIXED / POINTER members (`declare 1 s based(p), 2 m fixed, 2 nx pointer`) | accepted by DR; record layout, `allocate s set(q)` through any q, qualified and unqualified access, `free s` == `free p->s`, link following | ST1/ST3/ST8/ST9/ST10/LN1 byte-exact; LN1 linked from my .REL and from DR's and run identically | **ACCEPTED [C185]** | E2E-27. Corrects E2E-26's "blocked on DR itself". Members are contiguous with NO padding (ST6). Based char/bit/dec/DECIMAL members still refused after correct layout binding (ST5/ST6/ST7) |

| FIXED BINARY(p) / FIXED DECIMAL(p) with p>15 | **NOT IMP** at dcl; **no `.REL` emitted** (E1415/E1416..E1432, E15D09/E15D16/E15D31 — golden/e2e11f) | Subset G §3.2.2 permits (max 31) | **[M]** | DR 16-bit-RTL cut. **Evidence refresh:** this row previously cited a "P068 L-series sweep" whose artefacts no longer exist (every `golden/probe2*/P068*/` holds only `dir.txt`). Re-established live. Enforcement moved from a partial codegen arm to `bind.check_fixed_prec` (unconditional, earliest point known); storage ladder re-derived from E19A, and the old `P063A` citation — which described 16/24/32-bit storage for types DR cannot compile — removed. N24/N27/N72/N73 pin it. |
| identifiers starting $ or _ | **SYNTAX** (P067D) | Subset G §1.1.3 ALLOWS $ and _ start chars | **[M]** minor | lexer keeps alnum; revisit in std mode |

## E2E-11 frontier — measured from DR, NOT yet implemented by my build

These rows record what the oracle says about constructs I currently refuse.  All
are **[S]** (the compiler accepts them, so the byte-parity track must eventually
reproduce them); none is supported by my build yet, and each refusal is loud.
Full evidence in `spec/notes/e2e11-step0-step1-endfile.md`, claims C109-C113;
step 2 (FILE/ON/FLTPOLY2 acceptance) in `spec/notes/e2e11-step2-file-endfile.md`,
claims C119-C121.

| construct | DR behaviour (observed) | my build | evidence |
|---|---|---|---|
| `dcl f file;` (SYSIN **or** user file) | named COMMON group, 34 + len(name) bytes: 33 zeros, the length, the name; **no DATA cell** | **byte-exact** | E11E, FLTPOLY2, C120 |
| `ON ENDFILE(f) <unit>;` | `LXI H,<cb>` (SEL-COMMON + COMMON reloc) / `MVI A,05` / `CALL ?ONCOP` / `JMP` over / inline unit / `RET`; **zero DATA bytes** | **byte-exact** | E11A, E11B, FLTPOLY2, C109 (6-byte claim retracted) |
| bare `if <bit1> then` | `LDA c` / `ORA A` / `JP skip` (sign flag, opcode F2) | **byte-exact** | T4, FLTPOLY2, C119 |
| `ON ENDFILE(f) goto label;` | target label grows `LHLD */SPHL/CALL ?RECOV` (2 hidden auto bytes) | refuses (perimeter) | E11F, N79, C121 |
| ENDFILE, **handled** | unit runs once; interrupted GET **completes unassigned**; next statement runs; no re-entry, no termination | n/a | E18B, E17A, E11A, E11C, C110 |
| ENDFILE, **unhandled** | TERMINAL: `END OF FILE (1), File: <var>=<name>` + traceback | n/a | E18A, C110 |
| `get file(f) list(x)` | `LXI H,<cb>` / `LXI D,0690` / `LXI B,0` / `CALL ?SIOOP` then the shared DEC reader | refuses (step 3) | E17A, C111 |
| `get list(x)` (SYSIN) | `LXI D,0290` / `LXI B,0` / `CALL ?SYSIN` then the same DEC reader | **byte-exact** | E11E, FLTPOLY2, R901-R917, C111 |
| `open file(f) stream title(t)` | `?SLCTS`(t) + 6-word push block + `LXI H,<cb>` + `CALL ?OIOOP` | refuses | E17A, C111 |
| `bit(1)` storage | **1 byte, high-bit justified**: `'1'b`→`0x80`; store `LXI H,c`/`MVI M,80`; test `LDA c`/`ANI 80`/`JNZ` | **byte-exact** | E20A, E21A, E21B, E11D, C112, C115 |
| `STATIC` / `STATIC INITIAL` on `bit(1)` | one DATA area `[statics][pool][autos]`; `'0'b`→00, `'1'b`→80 | **byte-exact** | E20B, E20D, E20E, E11D, C114, C115 |
| `INITIAL` without `STATIC` | pass 1 clean, pass 2 `NOT STATIC`, **no .REL** | refuses (agrees) | E20C, N78, C114 |
| `CALL p(args);` as a **statement** (internal proc) | **same lowering as an expression call** (`LXI H,*A(desc)` / `CALL`); only the result store is skipped | **byte-exact** | E24A-E24F, E27C, C122 |
| `CALL p;` / `f()` with **zero arguments** | bare 3-byte `CALL`; **no descriptor, no storage** | **byte-exact** | E24J, E25A, E25D, C124 |
| `CALL p(args);` where p **`RETURNS`** | DR `NOT PROC`, no `.REL` | refuses (agrees) | E24D fixed, E24H float, N81, N82, C122 |
| no-`RETURNS` proc in **expression** position | DR `TYPES NOT=`, no `.REL` | refuses (agrees) | E24I, N83, C122 |
| `CALL ext(args);` where ext is an external **`ENTRY`** | `LXI H,*A(desc)` / `CALL EX` + `LINK-CHAIN-EXT EX`, **no EXTDEF** | refuses (perimeter — linkage is its own milestone) | E24G, N84 |
| forward call (callee emitted after the call) | `CALL 0000` + 2 literal-zero DATA bytes + one `LINK-CHAIN-ADDR`; **N sites → N-1 inline RELOCs, each against the PREVIOUS site, chain targets the LAST** | **byte-exact + .COM-identical + runs** | E25F (2 sites), E27A (3 sites), C123 |
| procedure with **no RETURNS** | `RET` after the body **only when control can fall through it** (9 body endings sampled); RETURNS procs get none; a body whose tail is an unconditional jump emits no RET at all | **byte-exact** | E25A/B/C/E/G/H, E24A/F/H, C125; [E2E-28] REVERSE read_it @008E `JMP 003C' tail -> no RET, write_it @010F -> RET, N7/N8/N10 |
| nested-procedure placement in a main block | one 3-byte branch-over `C3 00 00' PER DECLARATION, operand = where main's emission resumes after that body; no branch when there is no resumption point; no prologue for the nested body; enclosing variables by absolute address; bare `RETURN;' = `RET' and emission continues; no dead-code suppression after a straight-line `STOP' | **byte-exact** | [C187] E2E-28: E28N1-N6/E28N8/E28N10 + ST13, plus six older refusals (ST8/ST13/ST14/AB7/AB14/EA1) that became byte-identical; N1/N4 executed from my .REL and from DR's with identical output | 
| BASED-member address stepping by record offset | `INX H' repeated for offsets <= 3, `LXI D,<off> / DAD D' for offsets >= 4; ONE encoder (member_step) shared by store, qualified read, unqualified read | **byte-exact** | [C189] E2E-28: O3(2), O5(4 store), O6(6 read), O8(2 pointer) + ST3/LN1/ST6/ST1; DR's DE-reuse of the offset (O1/O2/O4, +3 bytes each) is a pinned divergence, not fitted | | store through a **pointer formal**: const | `LHLD X` + `XRA A/MOV M,A/INX H/MOV M,A` for 0, else `MVI M,lo/INX H/MVI M,hi` | **byte-exact** | E26A(0,255), E25B(3), E26E(9), E26H(300), C127 |
| store through a pointer formal: `x ± lit` | deref, bias, `XCHG`, **`MOV M,D`/`DCX H`/`MOV M,E`** (high byte first) | **byte-exact** | E25F, E26B(+256,-1,+1000), E26I(-3), C127 |
| store through a pointer formal: general | `<rhs> / PUSH H / LHLD X / POP D / MOV M,E / INX H / MOV M,D` (low first) | **byte-exact** | E26C, E26D, E26H, C127 |
| compare vs a **pointer formal** | deref prefixed to the bias ladder; `>0` uses memory `XRA A/CMP M/INX H/SBB M/JP`; two-variable pairs plain-first with `PUSH H`/`POP D` | **byte-exact** | E25B, E25E, E26F, E26G, C128 |
| DEC store through a pointer formal (`q = r;`) | ordinary decimal route with destination **`LHLD` instead of `LXI H`** before `MVI A,p / CALL ?DSTOP` | **byte-exact + .COM-identical + mutation witness** | E26J, E28D, E28E, C131 |
| FLOAT store through a pointer formal | `?FX44M` cell-to-cell; destination `LHLD`; works with **both** operands pointers (`u = v`) | **byte-exact + .COM-identical** | E26K, C131 |
| FLOAT pointer destination, **computed** source (`?FX44S` route) | no DR sample | refuses (perimeter) | C131 scope note |
| BIT(1)/CHAR store through a pointer formal | no DR sample | refuses (perimeter) | C131 |
| label definition | **ends HL-constant reuse** (next constant reloads with LXI H) | **byte-exact** | E25G, C126 |
| **forwarding a pointer formal** as an actual (`call s(y)` in `t(y)`) | descriptor word written at RUNTIME: `LHLD Y / SHLD desc / LXI H,desc / CALL`, **no SET-LC pair**, no static operand | **byte-exact + .COM-identical + semantically checked** | E27B, E28A, E28B (order), E28C (mutation), C130 |
| bit-to-bit copy `g = f;` | DR compiles | refuses (perimeter) | T1, N74, golden/e2e11u/T1 |
| `bit(5)` cell + copy `b = c;` | DR compiles | refuses (perimeter) | T2, N75, .../T2 |
| bare `if f then` on a bit | DR compiles | refuses (perimeter) | T4, N77, .../T4 |
| `STATIC INITIAL` on FIXED | DR compiles | refuses (perimeter — initialiser encoding unpinned) | T3, N76, .../T3 |
| multi-bit literal `'10101'b` | **DR SYNTAX error, no .REL** | refuses | C117 |
| `x = x + 0` / `b = a + 0` / `b = 0 + a` / `b = a - 0` | literal 0 against a **variable** elides to a plain copy (`LHLD/SHLD`) | **byte-exact** | T5-T10, T12, T13, C119 |
| `b = 5 + 0` (zero against a **literal**) | decimal pool path `?DLDOP/?DADOP/?QDI15`, NOT elided | refuses (agrees with the no-fold rule) | T11, C119 |

## Grammar/reimpl policy
1. Grammar accepts [S] exactly as the compiler does (byte-parity track
   uses this).
2. [M] items: grammar accepts the MANUAL form; binder may emit a
   "compiler-divergence" diagnostic when mimicking v1.4 for the
   byte-identical track, but the portable track implements the manual.
3. [C] items: not parsed by default (future `--std` mode may accept).

## Corrections this session found to earlier notes
- **DR compiles `x = x + 0` and `x = x`** — a refusal message and negative N56 both
  asserted DR rejected them. It elides the zero to a copy [C119]; N56 retired, eight
  positives added.
- **`Ast.block.bdecls` is always empty** [C116] — declarations live in `bstmts` as
  `Sdcl`. A rule wired to `bdecls` does nothing silently, which is how E20C compiled
  instead of refusing.
- PICTURE is NOT a dcl attribute (no `picture(...)` dcl form in working
  samples; P066B confirms SYNTAX) — grammar updated.
- ROUND/CEIL/LOG are ordinary builtin calls (earlier "auto-injection"
  hypothesis refuted by LOAN1 source + P066A).

## [E2E-29] Perimeter widened — REVERSE is inside it now

Everything REVERSE needs is [S] SUPPORTED and byte-exact here, and the program itself is a registered
specimen (748-row inventory). Newly inside the perimeter, each with goldens and (where it can be
observed) executed evidence:

- **CHARACTER VARYING based members** — store from literal / varying / member, read for PUT, the
  `len==cap` and `len==0` folds, capacity truncation by the runtime, offsets past the C189 step
  boundary (`.next`@001F). [C190]
- **Character comparison** in IF and DO WHILE conditions: `?SCVCM` / `?SCCVM` / `?SCVVM`, literal on
  either side, member on either side, `=` and `^=`. [C191]
- **Pointer comparison**: null tests in both orientations for `null` and `null()` (tested through the
  cell's own bits), and pointer-vs-pointer through `?NC22N`. [C191]
- **Procedure-local** CHARACTER VARYING and POINTER cells, the nested-body tail-RET rule (no RET after
  a no-exit loop, RET otherwise), and bare `put skip;`. [C192]

Still [S]-known-but-open, unchanged by this milestone: DR's register-reuse peephole family
(PB4/PB20/E28N7/O1/O2/O4/**E29X3** — 8 rows in spec/DIVERGENT.txt, E29X3 being the only new one), the
numeric-condition gaps E28N1/E28N9, and the decimal backlog. REVERSE's `free p->wordnode` compiles
because that structure is BASED(p) [C185]; E2E-27's bare-based refusal is untouched for the shapes
that remain unsampled (E27S3/E27S4 still refuse).  **E27S6 was since proved byte-exact and promoted
to a specimen in E2E-30** [C195][C154] -- what E2E-27 refused was the *absence of a sample* for a
`BIT(1)` member's store/test bytes, not a perimeter limit.

## [E2E-30] Perimeter widened — NETWORK's graph structures are inside it

NETWORK.PLI's data-structure and control-flow language is now [S] SUPPORTED and mostly byte-exact;
the program itself is still refused, at `find(..) returns(POINTER)`. **(refusal superseded: NETWORK
has compiled end-to-end since E2E-34/P6, is BYTE-EXACT against DR's golden as of E2E-35/P3, and has
been EXECUTED (gate runtime row 15, E2E-35/P4) -- see the [E2E-35] section at the end of this file.)**
Newly inside the perimeter:

- **`BIT(1)` based structure members** — one byte at the member's record offset, `MVI M,80`/`MVI M,00`
  to store, `MOV A,M / ORA A / JP` to test, reached through the shared `member_step` encoder. Byte-exact
  at offsets 0, 2 and 23 (E30B1/B5/B7, E27S6 promoted). [C195]
- **The pre-test pointer traversal** `do p = <init> repeat(p-><link>) while(p ^= null)` — DR's exact
  init / top-test / body / repeat-update / back-JMP order, lowered through the existing pointer-store and
  test encoders rather than as an equivalent-but-reordered post-test `while`. [C196]
- **Chained qualification into a VARYING member** `q->next_city->city_name` — two dereferences through
  one encoder, byte-exact (E30C1). [C197]
- **`GET LIST` with several items** (E30H1) and the **capacity-vs-source-length store asymmetry**
  (`MVI A,dest-cap / MVI B,src-len / ?SMCVM`, E30T1). [C190]

Still [S]-known-but-open (as of E2E-29) -- superseded by the [E2E-31] section below.**named-SYSIN `ON ENDFILE`/`REVERT`** (`?ONCOP` at 0027/025A/02A4,
`?REVOP` at 02F8, all `LXI H,SYSIN` + `MVI A,05`; E30E2/E30E3), member-vs-member and chained **relational conditions**
(E30C3/E30B4), and `GO TO <label>`. The **register-reuse peephole** grew to 14 divergence rows
(PB4/PB20/E27S2/E28N7/O1/O2/O4/E29X3 + **E30L1-L4, E30B2, E30G1**): every pointer-walking loop we emit
carries one or two reloads DR elides, so the traversal is behaviourally right (E30G1's linked output is
byte-identical to DR's) but not yet byte-exact. That family is now the largest single obstacle to
NETWORK. [C196][C197]

**(Corrected by E2E-35/P2 [C223].)  Of those rows, PB20 had already died as a defect; E30B2, O1, O2
and O4 turned out not to be HL reuse at all but missing DE tracking [C219], and went byte-exact in one
pass (they are specimens now).  E30L1-L4 and E30G1 shrank (E30L2 154->153, E30L3 309->306, E30G1
560->554 of DR's 152/305/553) and PB4, E27S2 and E28N7 did not move, so the rows whose cause really is
HL-side liveness are the ones still open.  NETWORK is no longer blocked by this family: its code
section is now DR's exact size and its residual is a single linkage record [C225].  The divergence
panel is 13 rows.

## [E2E-31] Perimeter widened — RETURNS(POINTER) is in; two wrong-value defects are now on the record

`find(..) returns(POINTER)` -- NETWORK's first blocker through three milestones -- is inside the
perimeter and byte-exact (E31F1, E31F3).  The convention is shared with RETURNS(FIXED): the callee
leaves the pointer in HL and `RET's, the caller stores it with one SHLD [C199].  Bare `null' as an
assignment value to a POINTER cell was already inside it (E31F6), so E2E-30's matrix row 9 is
withdrawn.  NETWORK then stopped at `ON ENDFILE(sysin) GOTO eof' (line 50) [C201] -- withdrawn, that
ON unit compiles byte-exact and NETWORK has not stopped anywhere since E2E-34/P6.

Two things moved from "benign divergence" to "defect", and they are perimeter-relevant because they
affect programs that already compile:

- **Family B -- based/pointer member reads accumulated in arithmetic produce wrong values** (PB20,
  E31F4, E31F7C).  E31F7C is NETWORK's own loop body, so NETWORK would compute wrong shortest
  distances even after it compiles.  PB4 in the same family is correct, so the boundary is undrawn.
- **Family C -- a FIXED formal parameter compared in a condition is not dereferenced, so the test is
  made against the caller's address** (E31F8 prints `r=2' where DR prints the correct `r=1', at
  identical code size with one differing byte).  E31F2 has the defect with a lucky-correct value.

Neither is fitted [C179][C167]: both fixes need a probe in the opposite direction first, and Family C
has to be checked against the 756 accepted specimens before the condition lowering is touched.

`ON ENDFILE/REVERT` with label transfer is [S] SUPPORTED by DR and [M]-open in ours; its layout is now
fully measured [C201] but unimplemented, and ENDFILE *firing* is still unobserved because a linked
object driven to EOF under cpmsim hangs rather than transferring.

## [E2E-32] Both wrong-value families are INSIDE the perimeter now; ON/GOTO is the open blocker

`RETURNS(POINTER)`-era divergences turned out to be two defects, and both are fixed with one shared
mechanism each: **a by-reference formal must be read through its cell** (`val_addr`, plus routing
ident-vs-ident `=/^=` through `cmp_load_deref`) [C202], and **the left operand of ADD/SUB is parked in
DE unless the right operand's lowering writes DE** (`writes_de`) [C204].  Byte-exactness went 759 ->
776 with **no previously exact specimen moving**, and the six probes that printed wrong numbers
(E31F8, E31F2, E31F5, PB20, E31F4, E31F7C) are now byte-identical to DR *and* print independently
derived correct values.  E31F7C is NETWORK's own accumulation, so its shortest-distance computation is
now believed correct rather than merely compilable.

Two things are on the record as still open, both attributed rather than lumped:

- **E32B3 / PB4 are shape divergences with correct values.**  PB4's row was rewritten because its
  `q > 3` branch is taken for the wrong reason -- mine biases the **address**, and any `0x1Bxx`
  address is > 3 -- so it must not be cited as evidence that based comparisons work.
- **C203: with two or more by-reference formals my DATA segment is 4 bytes too large.**  E32C6's code
  is byte-identical after the Family-C fix; only the allocation differs.  This is a real NETWORK
  blocker (`connect` has three formals) and is left unfitted pending 2- and 3-formal DR samples.

`ON ENDFILE` is now split accurately [C206]: a **statement** handler is byte-exact (E32E1); the hidden
saved-SP cell is **per block**, not per ON-unit (E32E2), correcting C201; only `... GOTO label` --
stub, `?RECOV` prologue, label transfer -- remains [M]-open, and **EOF firing under cpmsim is still
unobserved**, so compile-side parity and runtime handler execution stay separate claims.

Evidence-kind rule adopted [C205]: byte parity, independent arithmetic, and running a byte-identical
image are three different claims.  `tools/e2e_gate.py --runtime` now labels each runtime row with the
authority that did the work, because after these fixes ten of twelve rows became circular.


**[E2E-34] registration:** `e34a/E34A2..E34A9` (ON ... GOTO pads, hidden saved-SP cell,
REVERT, OFCOP), `e34b/E34B1` (the FILE-with-empty-pool control for the SET-LC fix),
`e34c/E34C1..E34C10` (CHARACTER VARYING x VARYING comparison: the four load/immediate
shapes, both orientations), `e34d/E34D1..E34D4` (tail `RET' for value-returning procedures,
trigger = shape of the last top-level statement), `e34e/E34E1..E34E11` (a based FIXED BINARY
member as a comparison operand, six relations, both orientations), `e34f/E34F1..E34F14`
(`= k' through the shared bias ladder up to 32767, and `= <arithmetic expression>' in both
evaluation orders), `e34g/E34G1, G2, G4..G10` (the CHARACTER VARYING assignment family, four
cells, and the deref ladder `bmem_addr' was missing for a formal base) -- 48 specimens this
episode, plus `N7MFWD` and `N79GOTO` promoted from negatives against their own DR goldens and
`E28N9` / `E32C10` promoted once the `= k' gap they recorded closed.  `e34g/E34G3` and
`e34a/E34A9` are registered as refusals (qualified varying member source, and the unnamed
nested block).  Panel after E2E-34: 840 byte-exact, 119 refused, 17 pinned divergences.


## [E2E-35] Perimeter state -- DE tracking in, NETWORK byte-exact AND executed

E2E-35 changed no language boundary: what it changed is how existing constructs are ENCODED, and one
measurement convention.

- **DR's DE knowledge is now modelled** [C219][C220][C221].  Every based-member offset load and every
  zero load can now take the short form DR takes, which is a per-statement instruction-selection rule,
  not a feature.  37 new DR goldens pin it (e35r/e35t/e35v/e35w), all byte-exact, all registered.
- **Five former divergences are specimens**: E30B2, O1, O2, O4 [C223] and NETWORK [C227].  The panel
  is 12 rows.
- **Labels are block-scoped** [C228].  A label defined in a nested procedure shadows an identically
  named label in an enclosing block; my flat emission-ordered table used to resolve a nested forward
  reference to the OUTER pad, which is a live wrong address.  That was NETWORK's last remaining .REL
  difference [C227] -- not the `LINK-CHAIN-ADDR' encoding I had written up at the end of P2.
- **The tail RET is one question, asked once** [C229]: a subroutine whose last top-level statement
  cannot fall through (`goto`, `return;`, `stop;`) gets no trailing RET, exactly as a value-returning
  procedure already did.  E35X2/X3/Y1/Y2 are the positives, E35Y3/Y4 the controls.
- **NETWORK is byte-exact AND executed** [C231]: code 1456 = DR's `CODE SIZE = 05B0', data 235 = DR's
  `00EB', whole file identical to `golden/first8080u/NETWORK/NETWORK.REL'; linked with LINK 1.31 +
  PLILIB and run to completion, printing `30 miles remain,        30 miles to Paris' for a Boston to
  Paris query on a 3-node graph whose alternatives cost 150.  The run executes two recovery pads,
  `?RECOV', and `?REVOP' from a `revert endfile(sysin)'.  Its expectation is hand-derived from the
  source, so the row is `kind=independent': the image is DR's own compilation of a byte-identical
  .REL, and comparing its output to DR's would be circular [C137].
- **`ON ... GOTO` has been EXECUTED** (E35N1, E35N2, normal flow, `n=         7`, pad SPHL + ?RECOV in
  the path [C218]); the ENDFILE condition has still never FIRED in anything executed, and no EOF event
  is simulated here.
- **New refusal, deliberately narrower than DR** [C230]: a GOTO to a label NOT defined in the
  referencing block.  E35Y3 shows DR making the TARGET block pad-bearing and giving it the saved-SP
  cell with no ON-unit in the program, so [C208]'s pad demand is a special case of entering a block's
  stack frame; I have no rule for the demand, and emitting another block's address is a wrong value.
  E35X5 shows an already-padded target still differing by 2, so reusing the pad is not the answer
  either.  Measured cost: of the 41 corpus sources available, 15 are byte-exact, 26 refuse, 0 diverge,
  and this refusal fires on none of them.  Registered as negatives E35Y3, E35X5, E35Y4.
- **Still open**: the two-formal DATA anomaly (E32C6 26 vs 22, E33MC 16 vs 14), E34G3 (qualified
  varying member source, one sample), `k + x` and expr-vs-expr comparisons (no sample), procedure-local
  FILE, and DR's out-of-range-literal route (E28N7/PB4-class rows).
