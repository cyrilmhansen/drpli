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
| FLOAT formal of a RECURSIVE procedure | works; DR copies the value into the declared cell at body entry [R3103] | §6.3 | **[S] not implemented** | refuses (N71) — data addresses match, the copy prologue is missing. |
| `FLOAT BINARY(p)` with p != 24 | cell is 4 bytes for every p probed [R3001/R3013] | Subset G lists BINARY(p) | **[S] storage only** | only binary(24) has a characterized value model; other precisions refuse so a `float binary(14)` program can never silently get 24-bit arithmetic. |
| dedup'd callee formal's declared cell | occupies NO storage; a written-RECURSIVE callee's cell does | not addressable in the manual | **[S]** | C106, six probes (R3093-R3102) + P401/NFACT/FFACT/R3104. |
| FILE attribute cluster (KEYED/ENVIRONMENT/TITLE...) | works | §10 | **[S]** | |
| level numbers, groups, qualified refs, group assign | bind parses them; group assign and level-2+ members REFUSED | §4.2-4.3 | **[X]** | **[E2E-39/P3] corrects this row**: a second level number on a non-first item, a group-level name and a whole-group assignment each get a bind refusal quoting [C226][C227][C228], and DR compiles two of those three shapes. The row was copied from the manual's capability table and described bind's ability to PARSE a declaration, not to compile a reference. Qualified internal member access itself IS supported since E2E-40/P2 [C258] -- established by byte comparison against E40Q1/E40Q2, not read off a table. Structured declaration entries do emit one symbol per member, which is genuine and is what makes a member offset resolvable at all.
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
| builtins | **52 documented** (§12, TOC pp.75-88) [C243] | §12 | **[S] surface unmeasured** | All 52 parse (spec/coverage-builtin-sweep.tsv); **no byte-exact corpus program calls one**, so DR-verified lowering exists only per-probe. | no auto-injection for plain conversions (P066A); ANNUITY CHAR/DEC mystery still open [PROBE 66: picture-in-format + entry(returns char varying) bisect] |
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
| `BASED` pointer-ref: declaring-scope resolution, per-reference re-evaluation | documented §6.4 p.32 ("taken from the scope of the BASED declaration" / "re-evaluated at each occurrence") | resolves in the *use* scope, materialises the base once per statement | **[M] [C241]**; competing hypothesis for the four one-byte E30 traversal divergences — pinned, not fitted; no probe shadows a base |
| `STATIC` / `STATIC INITIAL` on `bit(1)` | one DATA area `[statics][pool][autos]`; `'0'b`→00, `'1'b`→80 | **byte-exact** | E20B, E20D, E20E, E11D, C114, C115 |
| `INITIAL` without `STATIC` | pass 1 clean, pass 2 `NOT STATIC`, **no .REL** | refuses (agrees) | E20C, N78, C114 |
| `1 t static, 2 m … INITIAL(…)` — member `INITIAL` under a STATIC top | **compiles** (DIOCALLS, ENTER have authenticated .RELs) | refuses, blaming DR | **my defect [C242]**; manual §6.2 p.31 documents the form with exactly this example. Two corpus programs unlock with zero oracle work. |
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
section is now DR's exact size and its residual was described in [C225] as "a LINKAGE record, not
an instruction" -- that diagnosis was WRONG and is corrected in [C237]; the residual is a real
instruction-sequence difference in the `LHLD / LXI B / DAD B' region of a pointer walk (DR does
`LXI B,FFFE / DAD B' where I do `LXI H,#target / PUSH H / LXI D / POP H / DAD D': +3 bytes, and the
DATA difference is the BASED-pointer own pad, which is pinned separately).  E27S2 and NETWORK are
Family-B/C rows and neither has moved.  The divergence panel was 12 rows as of E2E-38 (9 + the three
PB4-shape probes E37B1/B2/B3, registered then as proof that PB4 itself is a WRONG-VALUE defect
[C246]).  E2E-39/P1 retired all four rows including PB4's: the missing deref ladder was real, the
`q > 3' agreement at z = 1, 3, 4, 40 was coincidence, and the wrong value lived in `q = k'
[C251][C252].  The panel is 8 rows.

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
  distances even after it compiles.  PB4 used to be cited in that sentence as the same-family case
that works; it is byte-exact now, so NETWORK/E32C8's residual stands on [C237]'s instruction
difference alone and no longer has a counter-example next to it.
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

- **E32B3 is a shape divergence with a correct value.**  PB4's row was retired in E2E-39/P1 [C251]:
  the missing deref ladder was real, the branch masking it was a coincidence, and the object is
  byte-exact now.  PB4's row had been rewritten because its
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
  referencing block.  **REMOVED BY E2E-36/P2** [C233] -- the rule that made it necessary was
  "does a statement in this block name L?", and the probes showed the target block's ownership is
  what matters; see the E2E-36 section below.  Kept verbatim because it is the record of what was
  known at the time, and because its measured corpus cost (15 exact / 26 refusals / 0 divergent)
  is still the baseline the E2E-36 sweep has to beat.  **Re-swept after E2E-36/P6, denominator
  corrected by E2E-37/P1 (`tools/corpus_census.py', snapshot in `spec/census/'): of 44 historical
  programs, 41 carry sha256-authenticated DR `.REL' goldens and 3 (CALL, INVERT, MAININVT) are
  DR-rejected with no oracle -- 15 byte-exact (the same 15), 0 divergent, 26 controlled refusals, 0
  unexpected.**  The cross-block refusal fired on no corpus program and removing it moved nothing,
  which is the result a change to shared label-survey and HL-kill code should produce.  E35Y3 shows DR making the TARGET block pad-bearing and giving it the saved-SP
  cell with no ON-unit in the program, so [C208]'s pad demand is a special case of entering a block's
  stack frame; I have no rule for the demand, and emitting another block's address is a wrong value.
  E35X5 shows an already-padded target still differing by 2, so reusing the pad is not the answer
  either.  Measured cost: of the 41 corpus sources available, 15 are byte-exact, 26 refuse, 0 diverge,
  and this refusal fires on none of them.  Registered as negatives E35Y3, E35X5, E35Y4.
- **Still open**: the two-formal DATA anomaly (E32C6 26 vs 22, E33MC 16 vs 14), E34G3 (qualified
  varying member source, one sample), `k + x` and expr-vs-expr comparisons (no sample), procedure-local
  FILE, and DR's out-of-range-literal route (E28N7/PB4-class rows).

## [E2E-36] Perimeter state -- cross-block GOTO is IN; DR's HL constant model is closed

Gate at this commit: **933 byte-exact / 0 fail, 124/124 negatives, 9/9 divergences as recorded,
16/16 runtime, exit 0.**  Evidence: `spec/notes/e2e36-cross-block-goto-and-hl-constants.md',
[C233]-[C238], `golden/e36t' (17 transfer probes), `golden/e36h' (32 HL-ladder probes),
`golden/e36r' (the executed nonlocal transfer).

- **Cross-block `GOTO' is inside the perimeter** [C233].  Pad and saved-SP cell belong to the block
  that OWNS the label; a plain `GOTO' from another block charges that pad exactly as `ON ... GOTO'
  does, and a `GOTO' inside the owning block charges nothing (E36T11/T12 stay byte-exact with no
  cell).  Bind surveys the whole block tree once and codegen resolves through a scope chain
  [C235].  E35X5 / E35Y3 / E35Y4 moved from refusals to byte-exact specimens.
- **`GOTO <procedure entry name>' is refused, and so is DR's** [C234]: `NOT LABEL', five
  orientations, DR's diagnosis in `golden/e36t/*/`.  This is the only label-shaped refusal left.
- **DR's HL constant model is closed for the fixed-width binary store path** [C237].  It is the
  same model as DE's [C219] and it dies at branch TARGETS (label definition, IF join, conditional
  landing pad, GOTO join) and at anything that writes HL; it survives an unconditional `JMP',
  including into the dead code after a `GOTO'.  Reuse is destination-independent.  Six previously
  divergent or exact-but-fragile goldens depended on this (E35Y3, E35X5, E36T3/T4/T5/T8) and two
  pinned divergences closed with it (E29X3, E30L1).
- **A nested procedure's branch-over is per declaration in ANY block** [C238].  Mine emitted it only
  in the outermost block, so a procedure nested inside a procedure could be fallen into; E36T4 and
  E36T14 measured 3 bytes short with the enclosing body's data agreeing.  Wrong value, not shape.
- **A DR defect is now reproduced deliberately** [C236]: the `nx = addr(z)' route stores a pointer
  member with its HIGH half at the LOWER byte.  E27S2/ST2 is byte-exact on that basis.  It has no
  runtime witness because ST2 never dereferences the member; if a future program does, DR's answer
  is wrong and mine will be wrong the same way, which is what the contract asks for.
- **Still open, unchanged in shape**: the E30 traversal family (E30L2/L3/L4, E30G1) is one HL reload
  over each and the `null()`-publish fix did not reach it, so that reload is a different rule and is
  pinned rather than fitted [C179]; E28N7 is 2 bytes of code at equal data; E32B3 is the
  shape-only pointer rows; the two-formal/no-local DATA anomaly (E32C6 26 vs 22, E33MC 16 vs 14) is
  still undocumented; E34G3 (qualified varying member source), `k + x' and expr-vs-expr comparisons
  still have no sample.  DECIMAL and NUMERIC are untouched.
- **`E36H13' is not registered anywhere**: it does not parse here (the [E34A9] `begin ... end;'
  statement shape) and DR's answer for that source has not been established, so it is neither a
  specimen nor a negative.

## [E2E-39/P2] Unqualified internal-structure member references: subset implemented

| Shape | DR | Mine | Evidence |
|---|---|---|---|
| `declare 1 g, 2 a fixed` + `a = 7; put list(a)` (unqualified read/write, top-level head, FIXED BIN(15)/POINTER) | compiles, member lands in the owning structure's cells | **compiles**; DATA area equals DR exactly (E39S2 0004, E39S3 0006, E27S12/ST12 0006) | golden/e39a, golden/e2e324d/ST12 [C253][C256] |
| Qualified spelling of the same member (`g.a = 7`) | compiles, `.REL` **byte-identical** to the unqualified spelling | **SUPPORTED since E2E-40/P2 [C258]** -- resolved in the parser into one dotted identifier; my qualified/unqualified pair differs at exactly the same three byte offsets DR's pair does |
| Member nested two levels deep (`1 g, 2 h, 3 a fixed, 2 b fixed`) | DATA 4, same object as the flat form | compiles but **DATA 6** -- bind re-dispatches a head for a level-2 sibling after a level-3 member; row entry is gated to a level-1 owning head so the extra members stay unresolved | E39S5 vs DR [C255] |
| Character / bit / decimal / varying internal member | resolves the name | **refuses**: no DR sample of the cell size, and a wrong size overlaps the next variable [C162 class] | -- |
| Member name colliding with an ordinary variable | `DUPLIC ?` pass 1, no `.REL` | **refuses**, same outcome | E39X2 [C255] |
| Ambiguous unqualified member, two INTERNAL structures | `QUALIFY ?` at each unqualified use, `2 ERROR(S) IN PASS 2`, no `.REL` | **refuses, same outcome** — raised at the USE, in the frame that sees the candidates. E39X1 was a wrong-acceptance through E2E-39 (first-binding selection compiled it); closed in E2E-40/P1 [C257] | E39X1 `golden/e39b/E39X1/E39X1.PRN` |
| Ambiguous unqualified member, INTERNAL structure + BASED view | same: `QUALIFY ?` pass 2, no `.REL` | **refuses, same outcome** — a BASED view's member name joins the candidate set exactly like an internal one, so the set is over member NAMES, not over members that own storage | E40X3 `golden/e40a/E40X3/E40X3.PRN` [C257] |
| Ambiguous member declared in an ENCLOSING frame, used unqualified inside a nested procedure | (unprobed — E39S4, the intended probe, was written malformed and says nothing) | **not caught**: `layout` checks only its own frame's candidates, and no caller threads ancestors yet. E40N1 shows DR DOES resolve an enclosing structure's member from inside a nested procedure, so the same visibility must carry the ambiguity with it; the miss needs two structures sharing a name in the outer block plus an unqualified use in the inner one | E40N1 (accepted by both) narrows it; the ambiguous case is unmeasured [C257] |
| Ambiguous name used only inside a DECLARATION (INITIAL/DIMS/ATTRS) | (unprobed) | **not caught**: the use-walker skips `Sdcl`. Including it could only add refusals DR has not been asked about | statements are the shape E39X1/E40X3 use [C257] |

**Why none of the resolved shapes is byte-exact yet [C254]:** for one program differing only in
whether the operands are structure members or ordinary variables, DR emits `PUSH H/POP D` around the
second load (CODE 0036) where it uses `XCHG` for plain variables (CODE 0030) -- same addresses, same
register state on exit, 3 bytes per member-operand ADD. My compiler uses the ordinary-variable form
for both, so my member build is byte-identical to my ordinary build and 6 bytes short of DR's. This
is a code-shape rule, value-preserving; recorded as divergences, not promotions.

## [E2E-40/P2] Qualified internal member access SUPPORTED -- resolved in the parser, verified byte-for-byte

| shape | verdict | evidence | note |
|---|---|---|---|
| `g.a = 7; put list(g.a + g.b)` on `declare 1 g, 2 a fixed, 2 b fixed` (read AND write of a qualified top-level FIXED member, inside an expression, inside a PUT item) | **SUPPORTED** | golden/e39a/E39S1.REL (code 48 vs DR 54, data 4 = 4), golden/e40a/E40Q1.REL, artefacts/E39S7.PLI | One place does the work: the parser's `.' step turns `head.member' with a plain identifier on the left into a single dotted identifier, and bind keys a member row under that name as well as under the bare member name. Why that is the right level: DR's E40Q1 (every reference qualified) and E40Q2 (disjoint names, every reference bare) differ at exactly offsets 5/16/23 -- their procedure name -- and my pair differs at those same three offsets; my E39S1 vs E39S2 are byte-identical, as DR's are [C258]. |
| `cpb.nameadr = addr(t)` and `cpb.paramadr = cpb.nameadr` (POINTER members of an internal structure -- MPMCALLB's own shape) | **SUPPORTED** | golden/e40a/E40Q4.REL (code 50 vs DR 62, data 8 = 8) | The second statement is why the rewrite had to happen earlier than lowering: the predicates that decide whether a pointer assignment is a measured form inspect the RAW node, so an unresolved `Eqstruct' reads to them as an unknown expression kind. The 12-byte code shortfall here against DR's 4-byte shortfall on the single-FIXED case is further [C254] evidence. |
| E39X1 with its uses qualified | **COMPILES** | artefacts/E39X1.PLI, DR's own named remedy | The ambiguity's fix is available here, so E39X1 stays a genuine wrong-acceptance rather than a matched gap. |
| `a(1).b`, `p->q.b` (left side not a plain identifier) | REFUSED, loudly | none -- no DR sample of either | The structured node is kept so these reach refusals that describe them instead of an undeclared-name message. |
| `g.a` where `g` has no member `a` | REFUSED: "not a member of that owner" | none -- **DR's behaviour here is UNMEASURED** | Needs its own probe. This is a wrong-acceptance risk pointing the OTHER way from the rest of the episode: bind already ignores the head name when it collects member declarations, so DR may resolve `g.a' from all visible members regardless of the stated owner. Neither behaviour should be trusted until an oracle sample exists. |

- **Not attempted here**: [C254] (member operand preservation, the PUSH H/POP D shape). Every newly
  compiling program in this family is short by exactly that amount -- 9 specimens now, none exact --
  and all are registered in DIVERGENT.txt rather than being called matches.
- **Not extended**: level-2+ members, and member types other than FIXED BIN(15)/POINTER [C228].
- **Runtime**: none of these programs has been executed under cpmsim, so the VALUES remain unverified
  by execution. What is verified is the layout invariant, at byte-offset granularity.
