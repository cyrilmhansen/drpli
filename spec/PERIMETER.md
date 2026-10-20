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
| `DECLARE x POINTER;` with no BASED referencing it | NOT IMP (p1) | §3.4 verbatim example `DECLARE X POINTER;`, §4.2 `(P,Q) POINTER` | **[M]** | Works when some `BASED(p)` exists (P063B/P067B) ⇒ dead-code check bug. We support pointer dcl unconditionally. |
| `ALLOCATE v SET(p)` | accepted (p1 clean) | §6.5 documented | **[S]** | |
| `FREE p;` (pointer operand) | **BASED REQ** (p2) | DR §6.8 wording says pointer operand; **Subset G §5.7.2: FREE takes the BASED variable** | **[S + standard]** — DR CODE is standard; DR MANUAL text is wrong (erratum) | `FREE x;` works (P067C) = standard ✓ |
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
| POINTER arithmetic (`+=`) | ? | §3.4 says only = and -= defined | probe later | |

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
| procedure with **no RETURNS** | implicit `RET` appended after the body (7 body endings sampled); RETURNS procs get none | **byte-exact** | E25A/B/C/E/G/H, E24A/F/H, C125 |
| store through a **pointer formal**: const | `LHLD X` + `XRA A/MOV M,A/INX H/MOV M,A` for 0, else `MVI M,lo/INX H/MVI M,hi` | **byte-exact** | E26A(0,255), E25B(3), E26E(9), E26H(300), C127 |
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
