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
Full evidence in `spec/notes/e2e11-step0-step1-endfile.md`, claims C109-C113.

| construct | DR behaviour (observed) | my build | evidence |
|---|---|---|---|
| `dcl f file;` (SYSIN) | no data storage; PLILIB control block at TPA `0x0290` | refuses | E11E, C109 |
| `dcl f file;` (user file) | own control block in the program's data area | refuses | E17A, C109 |
| `ON ENDFILE(f) <unit>;` | `LXI H,<cb>` / `MVI A,05` / `CALL ?ONCOP` / `JMP` over / inline unit / `RET`; 6 bytes data | refuses | E11A, E11C, E17A, C109 |
| ENDFILE, **handled** | unit runs once; interrupted GET **completes unassigned**; next statement runs; no re-entry, no termination | n/a | E18B, E17A, E11A, E11C, C110 |
| ENDFILE, **unhandled** | TERMINAL: `END OF FILE (1), File: <var>=<name>` + traceback | n/a | E18A, C110 |
| `get file(f) list(x)` | `LXI H,<cb>` / `LXI D,0690` / `LXI B,0` / `CALL ?SIOOP` then the shared DEC reader | refuses | E17A, C111 |
| `get list(x)` (SYSIN) | `LXI D,0290` / `LXI B,0` / `CALL ?SYSIN` then the same DEC reader | refuses | E11E, C111 |
| `open file(f) stream title(t)` | `?SLCTS`(t) + 6-word push block + `LXI H,<cb>` + `CALL ?OIOOP` | refuses | E17A, C111 |
| `bit(1)` storage | **1 byte, high-bit justified**: `'1'b`→`0x80`; store `LXI H,c`/`MVI M,80`; test `LDA c`/`ANI 80`/`JNZ` | refuses | E11C, E11D, E17A, C112 |
| `STATIC INITIAL` on `bit(1)` | initialises at entry, independent of any FILE use (E11D has no FILE at all and runs) | refuses | E11D, C112 |
| `CALL p(args);` as a **statement** | (not yet probed for lowering shape) | refuses | **23 corpus programs** — #1 payoff, E2E-11 step 4 |
| `bit(16)` and wide bit strings | unknown | refuses | unprobed |

## Grammar/reimpl policy
1. Grammar accepts [S] exactly as the compiler does (byte-parity track
   uses this).
2. [M] items: grammar accepts the MANUAL form; binder may emit a
   "compiler-divergence" diagnostic when mimicking v1.4 for the
   byte-identical track, but the portable track implements the manual.
3. [C] items: not parsed by default (future `--std` mode may accept).

## Corrections this session found to earlier notes
- PICTURE is NOT a dcl attribute (no `picture(...)` dcl form in working
  samples; P066B confirms SYNTAX) — grammar updated.
- ROUND/CEIL/LOG are ordinary builtin calls (earlier "auto-injection"
  hypothesis refuted by LOAN1 source + P066A).
