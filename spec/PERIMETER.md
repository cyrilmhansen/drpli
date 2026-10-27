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
| FILE attribute cluster (KEYED/ENVIRONMENT/TITLE...) | works | §9.5/§9.6/§10 (OPEN attributes listed on printed p.60; CLOSE syntax p.62) | **[S]** | **[E2E-41/P2b] what this compiler lowers today:** titleless `open file(f) input`/`stream` [C273] and the **literal-TITLE** form `open file(f) stream|input title('<literal>')` [C278], plus `get file(f) list(names)` [C274] and `close file(f)` [C275] for a stream file — byte-exact on P081Q/P072H (titleless) and E17B/E16C/E18A (titled).  TITLE (**30** of 34 measured OPEN sites carry the 0x0800 bit, 4 do not — recomputed from OPEN-MATRIX.tsv by [E2E-41/P3a], which also corrects the 29 this row used to state and the "25 of 34" P1 wrote here [C279]; spec/lab-evidence/e2e41-p3/TITLE-CENSUS.txt) — **[E2E-41/P2b]: the LITERAL-title form is now lowered and byte-exact**: `open file(f) stream|input title('<literal>')` emits DR's 29-byte block (`LXI H,<pool>; MVI A,<byte len>; CALL ?SLCTS; MOV B,A; PUSH B; INX SP` + w1 0x0E90 + five zero words + `LXI H,<cb>`/`CALL ?OIOOP`) on E17B/E16C/E18A [C278], alongside P1's titleless P081Q/P072H [C273][C274][C275].  **[E2E-41/P3b]: the titled `stream output' open is lowered too** -- `open file(f) stream output title('<literal>')` measures w1 = 0x0E50, which is the input open's 0x0E90 with the input bit 0x0080 REPLACED by the output bit 0x0040, and E17D's block is otherwise byte-identical to E17B's including w6 = 0x0000 (no record length), so a stream OUTPUT open cannot be blamed for E17D's 128-byte file [C279][C280]; E16D/E17D are byte-exact specimens and both now carry a runtime row that compares the FILE the program created, all 128 bytes [C280].  A single-literal `put file(f) list(<literal>)` is lowered on the same evidence (attach word 0x0652, CALL ?SIOOP; E17D's own console PUT proves the item chain is route-independent) [C280], and `get file(f) list(names)` has been since P1 [C274].  **[E2E-42/P0, P1a, P1b] what is lowered NOW, beyond the above:** a MODE-LESS open (`open file(f)' and `open file(f) stream', both w1 = 0x0690 -- DR defaults to stream input, [C286]); a FILE name LONGER THAN SIX CHARACTERS, whose COMMON GROUP symbol is clipped to six while the control block stores the full name, INCLUDING the collision case DR accepts silently ([C283][C284][C289] -- the long-name my-gap in the sentence below this one is CLOSED); and the VARIABLE TITLE, which is not one route but a DISPATCH ON THE OPERAND'S STORAGE CLASS: a CHARACTER(n) VARYING operand takes `LXI H,<descriptor>; CALL ?SLVTS' in a 27-byte block and a CHARACTER(n) FIXED operand keeps `LXI H,<cell>; MVI A,<declared length>; CALL ?SLCTS' in a 29-byte one -- E46F1 versus E46F2 differ in source by one declaration and in the object by the helper name and two bytes ([C288]; the proof is LINK-CHAIN-EXT records, because in an unlinked .REL both CALLs are `CD 00 00').  E46F4 composes [C288] with [C283] in one statement.  DR diagnoses a REPEATED option keyword, or two members of the mode group, as pass-2 CONFLICT with no .REL, and this compiler now refuses it instead of COLLAPSING it ([C285]).  **Still refusing by name:** PRINT opens, a TITLELESS OUTPUT (its word, 0x0650, is measured only as a record-WRITE attach word and never as an OPEN w1), KEYED, DIRECT, ENVIRONMENT, PAGESIZE, LINESIZE, RECORD, SEQUENTIAL and UPDATE opens -- all OPTION WORDS, and none of them a TITLE problem -- READ of a named file, every file PUT that is not one literal (a variable item, a multi-item list, SKIP on a file, PUT EDIT), and a TITLE operand that is an EXPRESSION, an ARRAY ELEMENT or a QUALIFIED reference, or names a non-CHARACTER variable.  ONE KNOWN DIVERGENCE, recorded rather than hidden: an UNQUALIFIED reference to a VARYING-STRUCTURE MEMBER -- COPYLPT's `title(line)' -- binds as a fixed cell here, so this compiler emits ?SLCTS + MVI A where DR emits ?SLVTS (COPYLPT 014C..016D, 01E8..020A); no probe pins that shape and [C288] does not claim it.  DR ACCEPTS FILE names longer than six characters — the COMMON symbol is the first 6 chars and the CB stores the full name (COPY/RETRIEVE/COPYLPT/REPORT/DEPREC measure it [C277]); the long-name refusal this compiler used to raise was a my-gap, not a DR perimeter limit, and [E2E-42/P1a] CLOSED it: E46D1-D7 are byte-exact, including the two-name collision DR accepts silently [C283][C284][C289].  The cluster itself is DR's, not a standard extension: DR's objects measure it, which is why the refusals are `my-gap`.  Note the vocabulary trap P1a closed: the parser used to DROP five of these words silently and re-read the rest of the statement as new statements [C276(d)].
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

**Episode attribution.**  This table records the **E2E-11-era** state (claims
C109-C113, C119-C121): what the oracle said then, and what *this* build did then.  Its
"my build" column is therefore a historical observation and several of its rows have since
been closed -- several are marked **byte-exact** below, so the sentence "none is supported
by my build yet" was already loose when it was written and is not a current claim.  For the
CURRENT status of any row, read the FILE attribute cluster above and `spec/COVERAGE.tsv`;
`tools/e2e_gate.py` and the corpus census are the authority on what compiles today.  Rows
are not rewritten to say "byte-exact" wholesale, because doing so would destroy the record
of what was unknown at E2E-11; where a row's status has moved it is annotated in place.
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
| `open file(f) stream title(t)` | `?SLCTS`(t) + 6-word push block + `LXI H,<cb>` + `CALL ?OIOOP` | refused at E2E-11; **byte-exact since E2E-41/P2b for a LITERAL t** [C278] (E17A's operand is the literal `'$1.$1'`, so this row measures the literal route only), and **since E2E-42/P1b for a VARIABLE t** -- which is `?SLVTS` for CHARACTER(n) VARYING and `?SLCTS` + `MVI A,<len>` for CHARACTER(n) FIXED, not the single helper this row assumed [C288] | E17A, C111; E17B/E16C/E18A, E46F1-F4 |
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
| Member nested two levels deep (`1 g, 2 h, 3 a fixed, 2 b fixed`) | DATA 4, the SAME object as the flat form | **byte-exact** (E39S5) | [C264]: a level-numbered item WITH CHILDREN is a group and reserves nothing; the frame offset advances only by leaf sizes. Before P6 this compiled to a 6-byte frame with `a' at DATA+0x2 and `b' at 0x4 where DR fixes up 0x0 and 0x2. Probe E40S3 (`3 i, 4 a fixed') shows the rule is "has children", not "level = 3"; E40S1 (group last) and E40S4 (leaf before group) pin the rest. |
| Character / bit / decimal / varying internal member | resolves the name | **refuses**: no DR sample of the cell size, and a wrong size overlaps the next variable [C162 class] | -- |
| Member name colliding with an ordinary variable | `DUPLIC ?` pass 1, no `.REL` | **refuses**, same outcome | E39X2 [C255] |
| Ambiguous unqualified member, two INTERNAL structures | `QUALIFY ?` at each unqualified use, `2 ERROR(S) IN PASS 2`, no `.REL` | **refuses, same outcome** — raised at the USE, in the frame that sees the candidates. E39X1 was a wrong-acceptance through E2E-39 (first-binding selection compiled it); closed in E2E-40/P1 [C257] | E39X1 `golden/e39b/E39X1/E39X1.PRN` |
| Ambiguous unqualified member, INTERNAL structure + BASED view | same: `QUALIFY ?` pass 2, no `.REL` | **refuses, same outcome** — a BASED view's member name joins the candidate set exactly like an internal one, so the set is over member NAMES, not over members that own storage | E40X3 `golden/e40a/E40X3/E40X3.PRN` [C257] |
| Ambiguous member declared in an ENCLOSING frame, used unqualified inside a nested procedure | (unprobed — E39S4, the intended probe, was written malformed and says nothing) | **not caught**: `layout` checks only its own frame's candidates, and no caller threads ancestors yet. E40N1 shows DR DOES resolve an enclosing structure's member from inside a nested procedure, so the same visibility must carry the ambiguity with it; the miss needs two structures sharing a name in the outer block plus an unqualified use in the inner one | E40N1 (accepted by both) narrows it; the ambiguous case is unmeasured [C257] |
| Ambiguous name used only inside a DECLARATION (INITIAL/DIMS/ATTRS) | (unprobed) | **not caught**: the use-walker skips `Sdcl`. Including it could only add refusals DR has not been asked about | statements are the shape E39X1/E40X3 use [C257] |

**The operand-class code-shape rule -- [C254] as measured, [C260] as corrected, [C261] as
implemented.** For one program differing only in whether the operands are structure members or
ordinary variables (E39S2 vs E39P1, same statements, same addresses), DR changes TWO things, and the
condition for both is the operand class. **Both clauses are now implemented ([E2E-40/P4]) and eight
specimens in this family became byte-for-byte DR objects**, so the table is current state, not a gap
list:

| operand | DR store form | DR read-operand form | my form (both cases) |
|---|---|---|---|
| ordinary variable | `LXI H,<value> / SHLD <cell> / INX H x k / SHLD <cell+k>` | `LHLD / XCHG / ... / DAD D` | **same as DR** (E39P1 byte-exact, and one of the 946 exact specimens) |
| FIXED BIN(15) member, literal value | `LXI H,<DATA+offset> / MVI M,<lo> / INX H / MVI M,<hi>` per write -- H holds the ADDRESS, the value never enters a register pair | `LHLD / PUSH H / LHLD / POP D / DAD D` when **BOTH** operands are members | **same as DR** since [E2E-40/P4]: E39S1/S2/S3, E40N1/Q1/Q2/R1 are byte-exact |
| POINTER member | not sampled -- E40Q4 stays 50 vs DR 62 | not sampled | **divergent**, deliberately not guessed [C261(f)] |
| member store of a COMPUTED value | `LHLD / PUSH H / LXI H,<addr> / POP D / MOV M,E / INX H / MOV M,D` (destroys HL, so DR's value reload is mandatory) | -- | **divergent**: E39S7 52 vs DR 57; its tail is byte-identical from 001F on, only the store's 3-byte value load differs [C261(d)] |

The cost table in [C260] scored DR's member write as MORE expensive than mine and concluded a
byte-exact specimen must be paying an offsetting cost elsewhere -- which is why the store route was
abandoned mid-implementation, and why my first correct-looking attempt then overshot (E39S1 went
48 -> 59 against DR's 54, because the value load was emitted AND ignored). Measured per write, DR's
member store is CHEAPER (8 bytes vs my 9) and the gap closes with no offsetting cost [C261(b)].

The old text of this paragraph said "3 bytes per member-operand ADD" and described the store as
`MOV M,A / INX H / MOV M,A`. Both were wrong: the read delta is 1 byte (2 for PUSH+POP against 1 for
XCHG), and `MOV M,A` is ZS1's ARRAY store of a VARIABLE, never used by DR for an immediate member
store -- the paragraph was built from a sequence copied from an unrelated shape. What survives is the
observation: a code-shape rule keyed on operand class, value-preserving, recorded as divergences and
not promotions. Its positional explanation ("the tail is where no instruction follows the CALL'") is
withdrawn -- DR's `PUSH H` sits mid-expression with `MVI A,09` and four calls after it [C260].

## [E2E-40/P2] Qualified internal member access SUPPORTED -- resolved in the parser, verified byte-for-byte

| shape | verdict | evidence | note |
|---|---|---|---|
| `g.a = 7; put list(g.a + g.b)` on `declare 1 g, 2 a fixed, 2 b fixed` (read AND write of a qualified top-level FIXED member, inside an expression, inside a PUT item) | **SUPPORTED** | golden/e39a/E39S1.REL (code 48 vs DR 54, data 4 = 4), golden/e40a/E40Q1.REL, artefacts/E39S7.PLI | One place does the work: the parser's `.' step turns `head.member' with a plain identifier on the left into a single dotted identifier, and bind keys a member row under that name as well as under the bare member name. Why that is the right level: DR's E40Q1 (every reference qualified) and E40Q2 (disjoint names, every reference bare) differ at exactly offsets 5/16/23 -- their procedure name -- and my pair differs at those same three offsets; my E39S1 vs E39S2 are byte-identical, as DR's are [C258]. |
| `cpb.nameadr = addr(t)` and `cpb.paramadr = cpb.nameadr` (POINTER members of an internal structure -- MPMCALLB's own shape) | **SUPPORTED** | golden/e40a/E40Q4.REL (code 50 vs DR 62, data 8 = 8) | The second statement is why the rewrite had to happen earlier than lowering: the predicates that decide whether a pointer assignment is a measured form inspect the RAW node, so an unresolved `Eqstruct' reads to them as an unknown expression kind. The 12-byte code shortfall here against DR's 4-byte shortfall on the single-FIXED case is further [C254] evidence. |
| E39X1 with its uses qualified | **COMPILES** | artefacts/E39X1.PLI, DR's own named remedy | The ambiguity's fix is available here, so E39X1 stays a genuine wrong-acceptance rather than a matched gap. |
| `a(1).b`, `p->q.b` (left side not a plain identifier) | REFUSED, loudly | none -- no DR sample of either | The structured node is kept so these reach refusals that describe them instead of an undeclared-name message. |
| `g.a` where `g` has no member `a` | REFUSED: "not a member of that owner" | none -- **DR's behaviour here is UNMEASURED** | Needs its own probe. This is a wrong-acceptance risk pointing the OTHER way from the rest of the episode: bind already ignores the head name when it collects member declarations, so DR may resolve `g.a' from all visible members regardless of the stated owner. Neither behaviour should be trusted until an oracle sample exists. |

- **DONE in [E2E-40/P4]**: the two [C254]/[C260] clauses -- member stores via `LXI H,<addr> + MVI M`,
  and `PUSH H/POP D` instead of `XCHG` when **both** ADD operands are members. Gated on operand class as
  required: applied globally the member store form would break the specimens that already match DR's
  variable form, and applied to "either operand" it would break E39S3, which is member + ordinary and
  keeps `XCHG`. Result: 8 specimens promoted, byte-exact panel 939 -> 946, corpus census unchanged
  (0 DIFFERS / 0 UNEXPECTED), and E40R1 additionally verified at link and console level [C261(e)].
- **Not extended**: level-2+ members, and member types other than FIXED BIN(15)/POINTER [C228].
- **Runtime**: E40R1 (`g.a = 7; g.b = 9; put list('g=', g.a + g.b)`) is now the strongest runtime
  witness in the project, at three levels: its `.REL` is byte-for-byte DR's, the gate's `--link-run` arm
  reports **`.COM` IDENTICAL vs DR**, and its console output is **BYTE-EQUAL** -- 13 raw bytes,
  `g=        16\r` [golden/e40dr/E40R1.output.txt, C261(e)]. Byte-exactness is what UNLOCKED that arm:
  it links both sides, so it is available only for names in the SPECIMENS panel. The earlier claim here
  ("mine prints the same value even though my image is 6 bytes short of DR's") is superseded, and the
  same false sentence was corrected in place inside spec/RUNTIME.txt. E39S7 and E40Q4 remain
  unexecuted; for them only the layout invariant is verified, at byte-offset granularity. E39S5 WAS linked and run
  in [E2E-40/P6]: `.COM` **IDENTICAL** to DR's (6912 bytes) and console **BYTE-EQUAL** (`      16`,
  10 raw bytes) -- but see [C264]: a run cannot discriminate this class of layout defect, because the
  pre-fix frame was self-consistent and printed 16 as well.

## [E2E-40/P4] The member store and ADD-preservation routes IMPLEMENTED -- 8 specimens promoted to byte-exact

| shape | before (HEAD `acf1cc7`) | now | note |
|---|---|---|---|
| FIXED BIN(15) internal member, literal store (`g.a = 7`) | 48 vs DR 54 | **byte-exact** (E39S1, E39S2, E40Q1, E40Q2, E27S12) | `LXI H,<addr> / MVI M,lo / INX H / MVI M,hi`, and -- the part that cost me an iteration -- **no value load at all**. Route is my array form 2 (AB3/AB9/AB14/AC3) reused, not a third encoder. |
| member + member ADD (`g.a + g.b`) | inside the 48 above | **byte-exact** | `LHLD / PUSH H / LHLD / POP D / DAD D` replaces `XCHG`. Value-equivalent; 2 bytes. |
| member + ordinary ADD (`a + h`) | 53 vs DR 59 | **byte-exact** (E39S3) | keeps `XCHG`. This is the control that forbids widening preservation to "either operand is a member" -- its LEFT operand is a member and DR still uses `XCHG`. |
| enclosing-frame member read from a nested procedure | 73 vs DR 76 | **byte-exact** (E40N1) | [C257]'s visibility rule now also matches in bytes. |
| qualified member access, executed | runtime row only (mine vs a transcribed value) | **byte-exact + `.COM` IDENTICAL + console BYTE-EQUAL** (E40R1) | [C261(e)] |
| nested level-3 structure | CODE 48, DATA 6 vs DR 4 | 54, DATA 6 vs DR 4 (E39S5) | **[E2E-40/P6 WITHDRAWS THE "CODE BYTE-IDENTICAL" CLAIM WRITTEN HERE]**: the code payload was identical because it never contains a member address; DR and mine disagreed in the RELOC fixups (DR DATA+0x0/0x2, mine 0x2/0x4), and two of the five "record-length" bytes were exactly those offsets. Closed by the subgroup rule [C264] -- E39S5 is 256/256 identical and its .COM is DR's. |
| member store of a COMPUTED value (`a = a + g.b`) | 49 vs DR 57 | **byte-exact** (E39S7, 57 = DR 57) | **This row was DELETED from the table by [E2E-40/P6]'s edit and is restored from `git show 6df2bd9:spec/PERIMETER.md`, with P4's wording where it still stands.** P4 recorded 52 vs 57 and called the difference "a deliberate choice on an unmeasured shape" -- keeping my cheaper reuse because DR's parked form destroys HL. The shape was not unmeasured: E39S7 IS the DR sample, read in the wrong place. [C266]: a store whose destination cell has a fixed DATA address parks the value (`PUSH H / LXI H,<cell> / POP D / MOV M,E / INX H / MOV M,D`) whenever the value came from the general expression path; the subsequent `put list(a)` is a full `LHLD` reload on both sides, so the reuse kill was right and the store shape was not. E40S2/E40S4, which P6 pointed at from here, are a different question -- operand preservation, not the store. |
| POINTER members (`cpb.nameadr = addr(t)`) | 50 vs DR 62 | 50 vs DR 62 (E40Q4) | **untouched**: out of scope, no oracle for the pointer store shape. Its gap is 3x the FIXED case, which is itself evidence the two routes are not the same route. |

- **Why the gate did not move on 939 -> 946 by accident**: the class predicate is bind's own
  `RTimem (owner, k, RTbin p)` with `p <= 15`, carried into codegen as `var_info.imem` and stamped by
  one function (`Vinfo.attach`) at both frame builders -- so it cannot be set in one scope and
  forgotten in the other. Ordinary scalars, array elements, BASED/POINTER views, formals, heads and
  statics all resolve to `None` and keep the `SHLD` route. AB3/ZK6 (array byte stores) and E39P1
  (flat scalars) are the two controls, and both are byte-exact.
- **Process**: my first implementation of the store route emitted the value load *and* the address
  load (48 -> 59 against 54). The array code had already documented that exact defect and I walked
  into it from the other direction. The reason I abandoned the correct rule mid-course was a cost
  model in [C260] that had DR's member write MORE expensive than mine; the per-write table in
  [C261(b]) shows it is cheaper. Both errors are recorded rather than quietly fixed.

## [E2E-40/P6] Nested internal structures: the subgroup rule, and what a code-byte match cannot prove

**The rule (C264).** A level-numbered item is a GROUP when the items after it, up to the next one at
its own level or higher, nest under it. A group reserves NOTHING: it takes the running offset as its
own offset, its children start there, and the running offset advances only by LEAF sizes. The level-1
head path already had this ("typeless group heads occupy nothing"); level >= 2 subgroups did not, and
were charged `bytes_of` of the default type -- a typeless item resolves to FIXED BINARY(15), 2 bytes --
so the group took a cell nobody declared and every later member sat 2 high.

| | before | after | DR |
|---|---|---|---|
| E39S5 `1 g, 2 h, 3 a fixed, 2 b fixed` | frame 6, fixups 0x2/0x4 | **256/256 identical**, fixups 0x0/0x2 | DATA 4, 0x0/0x2 |
| E40S1 `1 g, 2 h, 3 a fixed` (group last) | 4 | **identical** | DATA 2 |
| E40S3 `1 g, 2 h, 3 i, 4 a fixed, 2 b fixed` | 8 | **identical** | DATA 4 |
| E40S2 `2 h, 3 a, 3 c, 2 b` | DATA 8 | DATA **6 = DR**, members 0/2/4 | DATA 6 |
| E40S4 `2 a, 2 h, 3 c, 2 b` (leaf first) | DATA 8 | DATA **6 = DR**, members 0/2/4 | DATA 6 |
| ENTER `2 address, 3 street/city/state/zip, 2 age...` | age 91, wage 93, hours 96 | age 89, wage 91, hours 94, next structure 97 | **89 / 91 / 94 / 97** |

**Why the previous slice's note was wrong, and how it was capable of being wrong.** [C261] recorded
E39S5 as "CODE byte-identical to DR, only the DATA extent differs". Both halves looked like
measurements and the first is literally true of the code PAYLOAD -- which is exactly why it proves
nothing: `LXI H,<DATA+off>` records the segment and leaves the offset to the LINK-CHAIN-DATA/RELOC
item. Of the 5 differing file bytes, two (`0x2F`, `0x38`) WERE the member addresses, so even the
"all of them record-length fields" description misread its own evidence. The panel legend in
`spec/DIVERGENT.txt` now says this out loud, because a CODE/DATA column pair that agrees is not
parity.

**The gate's own census could not have caught any of it (C265).** `--verify` compares
`dr_verdict, sha_ok, mine, mine_bytes, differing_bytes` -- not `msg` -- and only `--check` writes the
snapshot. So [C263]'s blocker transition was found by hand, and [C264]'s reverse transition was
initially "measured" as 0 changes because the comparison read a stale snapshot against a file nothing
had rewritten. `msg` is now compared (41 of 44 messages already agreed; the 3 that drifted are this
change), and the snapshots were refreshed with the sanctioned writer, which simultaneously proved the
counts identical (15 EXACT / 0 DIFFERS / 0 UNEXPECTED).

**Blocker state after P6 (per program, not aggregate).** ENTER and UPDATE are held by a statement
they contain -- `open file(emp) keyed output environment(f(128),b(8000))` at ENTER line 37 -- and
REPORT by `STATIC on CHAR(15)`. That is where they stood at P1/P2/P3: [C263]'s claim that P4 had made
`get list` / `write file from` non-blocking is WITHDRAWN, because the `EMPLOYEE@31` refusal that
appeared to unblock them was this slice's phantom cell. MPMCALLB (CHAR(27)), FSCAN (CHAR(80)
VARYING) and LOAN2 (CHAR(14) VARYING) are unchanged: they never moved.

**What is NOT claimed.** Nested structures are not "supported" in general. Unsampled or still
unsupported: the `$S` dump SPELLING of a subgroup (`STRUCTURE LEVEL n, MEMBERS k` at level >= 2 is my
analogue of the head line -- golden/bind1 holds six DR dumps and every structure in them is LEVEL 1
with leaf members, so nothing here is transcription); `MEMBERS k` counting for nested heads;
references to a bare GROUP name (`address = default`) -- they now resolve to nothing and refuse,
whereas before they resolved to the phantom cell, i.e. a wrong-width copy instead of a refusal, and
DR's correct behaviour for that shape has no sample; arrays inside level-numbered structures;
subgroups inside BASED views (the head path, untouched); CHAR/BIT/DEC/VARYING members [C228];
STATIC INITIAL on any member.  ~~E40S2/E40S4 remain divergent on 1 instruction, which shows
[C261]'s "both operands are members" preservation predicate is too narrow -- the three-term sum
is E39S7's class and is deliberately outside this slice.~~  **[CLOSED in P9: the discriminator
was neither the layout nor the store route.  It is the class of the operand DR loads next
([C271], golden/e45), and both programs are now 256/256 whole-file identical and registered
byte-exact; the predicate was not only too narrow, it could not express the shape -- it took
`Eident' names and a compound left operand is not one.]**

## [E2E-40/P7] Computed member store: the DESTINATION's addressing mode selects DR's route [C266]

One question per store: **can the cell be written without moving HL?** The RHS never picks between
the two answers; it only decides whether the value is a literal DR can write in place.

| destination | value | DR's write | witnesses |
|---|---|---|---|
| plain cell (ordinary scalar) | literal / variable / computed / call | `SHLD <cell>` | RT4 `c = a(2)+a(4)`, AC3 `i = a(0)+a(3)`, 34 `var = var` copies in LABELS/R613/R3094/R3101/LOAN2 |
| " | hl_const literal | `LXI H,<value> / SHLD` | RT4 `b = 17` |
| fixed DATA-address cell (array element, **internal member**) | hl_const literal | `LXI H,<cell> / MVI M,lo / INX H / MVI M,hi` | AC3 `a(0) = 1`, E39S1/S2 [C260] |
| " | **anything else, including a plain variable** | `PUSH H / LXI H,<cell> / POP D / MOV M,E / INX H / MOV M,D` | AC1 `a(3) = b`, AC2, RT4, **E39S7**, **E41P1/P4** |
| " | self-update ladder | `LHLD / <bias> / SHLD` -- form 4 tested BEFORE form 3 | AC4, RT4 `a(2) = a(2)+5` [C165]; **on a MEMBER: E42P1 [P8]** |
| pointer-displaced cell | non-literal | reload the pointer into HL (`LHLD <ptr>`), park | C127's three shapes, MPMCALLB, DIORAND |

**Four new DR probes close the matrix (`golden/e41p`, byte-exact against mine on all four: code
60/46/65/59, DATA 4/6/4/4; predictions recorded in `golden/e41p/PREDICTIONS.txt` before DR ran):**

| probe | statement | destination | DR body | settles |
|---|---|---|---|---|
| E41P1 | `a = b + 1` | member, DATA+0 | `LHLD b / INX H / PUSH H / LXI H,*(0) / POP D / MOV M,E / INX H / MOV M,D` | the bias belongs to the VALUE; destination relocates to the cell's own offset (M3 refuted); `LHLD;INX H;SHLD` does not appear |
| E41P2 | `h = g.a` | **ordinary scalar** | `LHLD a / SHLD *(h)` | a member *source* does not force parking (M1 refuted) |
| E41P4 | `a = b` | member | parked, 11 bytes | **a bare copy parks -- the RHS class is irrelevant** |
| E41P3 | `g.a=7; g.b=5; a = a + g.b` | member | E39S7's shape, DR console `12` | the arithmetic oracle E39S7 is not |

Corpus-wide: 12 parked sites against 3740 `SHLD` occurrences in 1185 authentic objects, and the
triple `2a .. 23 22` (`LHLD;INX H;SHLD`) occurs **zero times in all 1963 goldens** -- which is what
[C260]'s corrected citation claimed for E39S2. It is the ordinary-variable ladder (`LHLD v / INX H /
SHLD v`, load and store naming the SAME cell) misread as a member store.

**Consequences for register state.** The parked store leaves HL at `cell+1`, so `last_imm` dies at
the store -- not at the preceding `DAD D` (HL legitimately holds the sum). DR's E41P1 reloads
`put list(a)` with a full `LHLD a` and **no `XRA A`**, so the zero-store machinery (E36H11/E36H12/
ZS3-ZS6) does not fire here and my `kill` is right.

**Two rows of this perimeter moved.** E39S7 (`a = a + g.b`, 52 vs DR 57) is byte-exact and promoted;
its [C261(d)] note "DR's form destroys HL, so its value reload is mandatory; keeping my cheaper
reuse is a deliberate choice on an unmeasured shape" was wrong because the shape WAS measured -- by
E39S7 itself, read in the wrong place. **The P6 edit also destroyed a table row: the
"member store of a COMPUTED value" row of the P4 table above was consumed by a string replacement
and is now restored from `git show 6df2bd9:spec/PERIMETER.md` with its wording preserved.** That is
also where the P6 claim about ENTER/UPDATE's blockers was recorded, corrected in two COVERAGE rows
here (`EMPLOYEE@31` was the phantom subgroup cell, never a DR-shaped fact).

**Still refused / still unmeasured (as of P7 -- [P8] below moves two of these five items).** POINTER
members (E40Q4 stays divergent at 50 vs 62); CHAR/VARYING/DEC/BIT members [C228]; STATIC INITIAL on
any member; ~~member stores of out-of-range literals (keep `SHLD` + DR's decimal-conversion calls,
LR7 parks only for array elements)~~ **[P8] MEASURED, AND WRONG: E42P2 parks**; ~~the self-add ladder
on a member (E40L1 was MY build only, no DR oracle, so it is not evidence -- no `MVI M`, no
parking)~~ **[P8] MEASURED, AND RIGHT: E42P1 keeps the ladder and `SHLD`**; `unspec(x) = <computed>`
into a plain
scalar in MPMCALLB parks, which does not fit the table above -- three of its four `unspec` sites
have a based/pointer destination and the fourth is a genuine anomaly I did not build on. **E40S2 /
E40S4 are a different question, not a leftover of this one**: their stores are all literals and
their residual is operand preservation inside `a + b + c`; they remain pinned at 67 vs DR 68 with
LAYOUT agreeing (DATA 6/6, members 0/2/4), and [C261]'s both-operands-are-members predicate is still
too narrow with the real discriminator unmeasured. **[P9: closed. The predicate was too narrow AND could not express the shape --
it took `Eident` names, and a compound left operand is not a name; the discriminator is the right
operand's addressing mode, [C271]. E40S2/E40S4 are byte-exact.]**

## [E2E-40/P8] The two shapes P7 called unmeasured were being emitted; one of them was wrong [C267]

P7's `rhs_landed_in_hl` flag routed the computed member stores and *excluded* two shapes on the
grounds that DR had no sample of them.  Because the exclusion was implemented by not setting the
flag, both fell through the tail match to `SHLD` -- so a build whose prose said "unpinned rather
than guessed" was emitting a specific pinned store shape for them, and `E40L1` (P4's ladder probe)
had never been shown to DR at all.  The defect is the general one: **declining to decide a shape is
a decision, written into the fall-through arm.**

Two probes (`golden/e42p`, predictions in its `PREDICTIONS.txt` first, verdicts read off DR's linked
`.COM` with `tools/dis80.py --com` rather than off a `.REL` listing, per [C264]):

| probe | statement | DR's store | mine at HEAD | now |
|---|---|---|---|---|
| E42P1 | `g.a=5; g.b=100; a = a + 5` | `LHLD 19F6 / LXI B,0005 / DAD B / SHLD 19F6`, console `10` | ladder + `SHLD` | **unchanged -- 256/256 identical** (code 0x3A = 58, DATA 4).  Right shape, wrong label: [C165]'s form-4-before-form-3 owns this, not [C266]'s destination rule (AC4 says the same for an array cell) |
| E42P2 | `a = 65535` (member) | decimal-conversion calls, then **`PUSH H / LXI H,<cell> / POP D / MOV M,E / INX H / MOV M,D`** | conversion + `SHLD`, 168 differing bytes | **parked -- 384/384 identical** (code 0x5A, DATA 0x7: the extra DATA is DR's literal-pool cell for the 5-digit value).  A silent mis-shape, closed |

`[C266]`'s destination-first framing is untouched; its *second* half needed the qualification.  In
a member store the RHS chooses among THREE shapes and the dividing line is whether HL holds the
**value** at the tail, not whether the source text was a literal: an in-range literal is written in
place, a literal DR must convert arrives in HL and parks.  32768..65535 is admitted on E42P2 plus
LR7 (same conversion result parked into an array cell at 32768); above that, nothing.

**E42P2 then produced the slice's sharpest result.** DR compiles it, links it -- and its own object
aborts at run time: `ERROR (1), Conversion`, traceback `0612 10B0 3620 3535 3533`, because a
`FIXED BIN(15)` cell cannot hold 65535.  The range check is in DR's runtime library, so MY object,
linked from a byte-identical `.REL` against that same library, aborts with byte-identical console
text (`golden/e42p/E42P2.MINE.COM`).  E42P2 is therefore a RUNTIME row whose expected output is an
error message: byte parity of a `.REL` still says nothing about behaviour unless something executes
it, and this time executing it changes what the specimen is *for*.

**The code now refuses instead of falling through.** `member_store_class` runs immediately after
`elide_fixed_zero`, before the value-producing match, and the tail reads its verdict:

| class | destination | route | licensed by |
|---|---|---|---|
| `Ms_literal` | member | `MVI M` at the cell | E39S1/S2, E40S1..S4, E43L* |
| `Ms_ladder` | member, same cell +/- k where the **source literal** fits BIN(15) (measured 25 biases, -32767..+32767) | ladder then `SHLD` | E42P1, then **E43L*/E43B*** [P8a]; `-32768` does NOT qualify -- E44A1 vs E44B1 [C270] |
| `Ms_general` | member, anything else | parked store | E39S7, E41P1/P4, E42P2, E43M1 |
| `Ms_unsampled` | member | **refusal before any byte** | nothing -- that is the point |

Four `my-gap` negatives pin the refusals (`E42N1..E42N4`: `a = -5`, `a = -65535`, `a = a + 100`,
`a = 100000`); none is registered as `dr-refuses`, because DR has never been shown any of these
shapes at a member store [C256].  Ordinary scalar destinations are not classified at all -- `mstore`
is `None` for them, `SHLD` stays their measured route for every RHS class in the corpus, and a
blanket rule would break 900+ byte-exact specimens.  `rhs_landed_in_hl` is deleted: mutable state
that every value arm must remember to set, replaced by a syntactic classification the tail can check
against the same AST the value arm consumed.

**Still open after P8.**  ~~The ladder on a member at biases other than +5, and under `-`~~
(**measured in P8a**, see below); negated literals at a member; FLOAT/DEC literals into a FIXED
member [C228]; POINTER/BASED members entirely (E40Q4) -- this table is for cells with a fixed DATA
address; ~~the cross-spelling ladder equivalence (`a = g.a + 5`), inferred from E40Q1/E40Q2's
byte-identity and never probed~~ (**probed in P8a: E43L6/E43L7**); and whether *my* runtime should
abort on the E42P2 shape when the linked library is mine rather than DR's, which is an ARCH-level
question, not a codegen one.  ~~E40S2/E40S4 remain where P7 left them~~ **(closed in P9: [C271], `golden/e45', both 256/256 identical).**

## [E2E-40/P8a] The classifier and the producer were two predicates; and the -8..16 range was mine, not DR's

Two defects, one measurement campaign.  `golden/e43l` (10 programs) + `golden/e43b` (**19**
programs -- the "20" first written here counted one probe twice), whole `.REL` compared each time,
`PREDICTIONS.txt` written first.  29 new P8a programs in total (30 ladder rows counting E42P1 and
E44A1; 35 programs counting golden/e42p and golden/e44): 28 ladder/cross-spelling plus the
converted-literal probe E43M1.  **The "-32768 endpoint" claimed below is withdrawn by P8b: the
ladder's measured span is -32767..+32767 at **26 distinct sampled biases** (1 from P8, 24 more from
P8a, 1 more from P8b's E44A1), and `a = a - 32768` converts.**  Also withdrawn from the section below:
"CODE is 0x3A across every one of them" -- 0x3A holds for the E43-template probes whose bias is spelled
`LXI B,k / DAD B`, while E43L3 (-1, `DCX H`) is 0x37 and E43L8 (+3, `INX H` x3) is 0x39.**

**(1) The alleged classifier/producer agreement did not exist.**  `member_store_class` decided
`Ms_ladder` by comparing resolved DATA addresses; the value-producing ladder arm inside
`lower_assign` decided by comparing the two operands' `Ast.orig` **spellings textually**.  Those
open onto different things, and they disagreed: instrumenting the arm shows `a = a + 5` firing it
and `a = g.a + 5` (R3/R4/X2/X4) **never** firing it -- the value came from the general ADD route
while the tail stored with `SHLD` because the verdict said ladder.  Their bytes still equalled DR's
for one reason only: `lower_hl` and the ladder both reach for `hl_bias`, whose `|k| <= 3` INX/DCX-vs-
`LXI B / DAD B` selection happens to reproduce the ladder's.  Two independently written predicates
agreeing by coincidence is exactly the [C260] failure mode.  P8a closes it by making the verdict
carry its operands (`Ms_ladder of Ast.binop * int`, `Ms_literal of string`) and by opening the ladder
arm **on the verdict** for a member destination (`None` -> the textual test, which is what the
ordinary-variable specimens measured and what 900+ byte-exact files depend on).  Consequences now
enforced rather than lucky: an `Ms_ladder` member cannot fall through to general value production,
an `Ms_general` member cannot emit a ladder, and a member carrying `Ms_unsampled` fails loudly in the
store `match` instead of reaching the `SHLD` default arm.

**(2) The range was an artifact of my own probe set.**  P8 refused a member self-update outside
-8..16, citing E22A02..E22A16/E22B01..E22B08 -- but those probes never asked for `|k| > 16`.  DR
was shown, at a member, **-32767, -16, -10, -9, -8, -1, +3, +4, +5, +14..+20, +30, +60, +100, +127,
+200, +1000, +5000, +10000, +30000, +32767** -- **26 distinct biases**: the 25 values covered by the 28
P8a ladder/cross-spelling rows (24 new to P8a; +5, +16 and +17 are each sampled twice, and +5 itself was
first established by P8's E42P1) plus E44A1's -32767.  Per-program audit in
`golden/e44/PROVENANCE.tsv`.  (The list first written here also had -30, -5, -2, +1, +2: no artifact
supports those.  -30 was a sign slip for E43B30 = +30; **+1, +2 and -2** have never been probed at a
member, while -1 has -- E43L3's `DCX H` x1.  The earlier "+/-1 and +/-2" phrasing contradicted the very
sentence next to it and is corrected.)  **Every sampled one takes the ladder with `SHLD`, the
operand carrying k exactly** (`+100` -> `LXI B,0064`, `+5000` -> `1388`, `+30000` -> `7530`,
`+32767` -> `7FFF`, `-9` -> `FFF7`) and whole-program CODE stays `0x3A` across all of them.  The
gate is therefore not a window.  It was then written as "whether the constant fits the 16-bit `DAD`
addend", and **that too was wrong: [C270] shows the boundary is the SOURCE LITERAL's magnitude.**
`a = a - 32767` (literal in BIN(15)) ladders with `LXI B,8001`; `a = a - 32768` (literal 32768,
addend -32768 = `8000h`, representable) converts, subtracts generally, parks, and DR's own run
ABORTS -- all of it byte-identical to this compiler without a codegen change.  The same
sentence tested at an *ordinary* variable (`artefacts/E22A17`, `100 = 100 + 100`) also ladders, so
this is not a member-specific relaxation.  **E42N3 (`a = a + 100`) is retired from the negative
panel and returns as byte-exact specimen E43B1C** -- a refusal removed only with a replacement
specimen.  What still divides the routes: a literal too large for the addend (32768..65535) goes
through DR's decimal conversion and then **parks**, and E43M1 measures that at a member at the
interval's lower end, so `32768..65535` is no longer a composition of LR7 + E42P2.  Above 65535
(E42N4) and for any negated literal (E42N1/E42N2) there is still no sample and the store refuses.

**(3) Cross-spelling is now measured, not inferred.**  `a = g.a + 5` (E43L6) and `g.a = a + 5`
(E43L7) are each 256/256 identical to DR and to each other and to E42P1's body, and their linked
objects print 105 [C268].  E40Q1/E40Q2's byte-identity was the only prior warrant for treating the
two spellings as one cell inside a self-update; there is now direct evidence in both directions.

**(4) DR's abort traceback is a literal dump.**  E43M1 (`a = 32768`) aborts the way E42P2 (`65535`)
does, with traceback `0612 1099 3320 3732 3836`: dropping the first word and reading the surviving
ASCII digit pairs left-to-right gives `3 32 327 3276 32768` -- DR's incremental decimal conversion.
My object aborts with byte-equal text.  The check is therefore magnitude-independent, and the
traceback is a *decoding key*, which is worth knowing before one mistakes it for an address [C267].

Gate after P8a: **969 byte-exact / 0 fail** (+13 specimens, 0 regressions), **128 refusals** (129
-1, E42N3 retired), **11 divergences** (unchanged -- no divergent row moved toward or away from
parity), **34 runtime rows** (+6), coverage 85 rows / 0 errors (DECL.MEMBER_SCOPE now `MIXED:34/37, recomputed from the row's own probe column in P8b`),
census 44 programs / 15 EXACT / 0 DIFFERS / 0 UNEXPECTED (no corpus verdict or blocker text moved),
exit 0.

## [E2E-40/P8b] The `-32768' endpoint: the boundary is the SOURCE LITERAL, and no codegen change was licensed

P8a wrote that the member ladder "runs over the whole 16-bit addend".  That sentence conflated two
facts and one unknown: `DAD B` can represent `8000h`; my ladder arm is gated by `fits t` on the
**positive source literal**, so the only spelling that yields k = -32768 (`a = a - 32768`) never
reaches `ladder_bias_fits` and its lower endpoint is dead code; and DR's choice was unmeasured.
Three probes (golden/e44, predictions committed first at 6ba2dc6) settled it; a fourth, E44D1, was
added after that commit as a control on a traceback reading of mine, and it is also 256/256 identical.

| probe | statement | literal in BIN(15) | DR's body | code | DATA | run |
|---|---|---|---|---|---|---|
| E44A1 | `a = a - 32767` | yes | `LHLD / LXI B,8001 / DAD B / SHLD` | 0x3A | 0004 | `-32667` |
| E44B1 | `a = a - 32768` | **no** | conversion of 32768, general subtract, **parked** store | 0x4B | 0007 | **abort** |
| E44C1 | `h = h - 32768` (ordinary) | **no** | same conversion + general subtract, then `SHLD` | 0x4C | 0009 | **abort** |

All three `.REL` are 256/256 identical to this compiler **as it already stood** -- so no codegen
change was made, and none should have been: the shape P8a's comment called "the addend's range" is
reached only by literals that `fits t` already admits.  The measured span is therefore **-32767 to
+32767 at 26 distinct sampled biases** (1 from P8, 24 more from P8a, 1 more from P8b), not "the whole
addend"; +1, +2 and -2 have no member sample (-1 does), and the intervals between sampled points are
interpolation.

**The abort is not [C267]'s store-range check.** `100 - 32768 = -32668` fits BIN(15) and is never
computed: DR dies inside the decimal conversion of the operand, before the subtraction.  E44C1 aborts
identically with an ordinary destination and the variable plainly in scope, so the check belongs to
the literal's route, not to the member store -- and [C266]'s destination rule still shows through
inside it (E44B1 parks, E44C1 uses `SHLD`).

**Provenance audit, because P8a's numbers were wrong.** golden/e43l = 10 programs, golden/e43b =
**19** (the "20" in [C268], the P8a note, K_TABLE.txt and the section above counted one probe twice):
29 new P8a programs, 28 ladder/cross-spelling plus the converted literal E43M1; E42P1/E42P2 belong to
P8.  [C268]'s bias list carried five entries with no artifact -- `-30` was a sign slip for E43B30
(+30), and `-5`, `-2`, `+1`, `+2` were never probed at a member (only `-1`, as `DCX H` x1 in E43L3).
E43L6 is **not** whole-file identical to E42P1: 4 bytes differ (0x31, 0x32, 0x3A, 0x3B -- the two
initialization immediates `MVI M,05`/`MVI M,64` vs `MVI M,64`/`MVI M,01`, plus the record-length bytes
after them); what is identical is the self-update sequence at code 0x16-0x20 and every DATA fixup,
including both member-address fixups.  **The traceback's last word is the VALUE the subtraction targets, not an address:
E44C1 `0064' (= h's 100) and E44D1 `0007' (= h's 7, with g.a = 1 and the layout moved) are the two
measurements; the address reading was tried and is withdrawn, and why the word sits there is unresolved
because the .REL carries no EXTERNAL records for the library calls. Digit prefixes: safe to decode.
Tail words: not evidence about addresses. See spec/lab-evidence/e2e40-p8b/TAILWORD.txt.** E43L6 and E43L7
*are* whole-file identical, so the
qualification symmetry survives with a narrower statement.  Per-program table:
`golden/e44/PROVENANCE.tsv` (+ `PROVENANCE-NOTES.txt`).  COVERAGE's DECL.MEMBER_SCOPE row also
contradicted itself: the 13 E43 panel specimens cited in P8a's commit message had been lost from its
probe column when the row was restored from HEAD after a column-index error, and the `46/49` figure
was not the probe list's count -- it is now `MIXED:34/37`, recomputed from the row itself.

**Harness lesson.** The first oracle run returned PRNs reading `UNEXPECTED EOF` and no `.REL` for all
three programs, which looks exactly like "DR rejects this source".  It was my own LF line endings in
a CRLF corpus.  The order to distinguish, before believing any verdict: DR I/O error on my file -> DR
language diagnostic -> LINK failure -> PLILIB runtime abort -> code-generation difference.

Gate after P8b: **973 byte-exact / 0 fail** (+4, 0 regressions), **128/128** refusals (unchanged --
this shape was never a refusal), **11/11** divergences (E40S2/E40S4/E40Q4 untouched), **38/38**
runtime (+4: -32667 and three aborts), coverage **85 rows / 0 errors / 0 warnings** (DECL.MEMBER_SCOPE
`MIXED:36/39'), census 44 programs / 15 EXACT / 0 DIFFERS / 0 UNEXPECTED and `--verify' clean,
INVENTORY **973** (+4/-0), exit 0 (and the runtime run exits 0 too, checked without a pipe so the code
is the gate's, not grep's).  All four new specimens additionally have DR's `.COM` identical to mine and
byte-equal consoles (10/64/64/64 raw bytes).

**And a claim of my own that did not survive its own control.**  Between the commit and this
paragraph I read E44C1's traceback tail `0064' as "100 = g.a's value at the abort"; the follow-up
note here repeats that; the version I then wrote instead ("it is the literal pool cell's address")
is also wrong.  `golden/e44/E44D1` -- same statement, `g.a = 1`, `h = 7`, an extra variable so the
pool cell moves (DATA 000B vs 0009) -- aborts with tail `0007'.  The tail equals the value of the
variable the subtraction *targets* in all three measurements; it is not an address and not g.a.
E44C1 was the trap: there the target's value, g.a's value and the target's DATA address are 0064h
all at once, which is precisely why its traceback appeared to say something it never said.  Why the
word is where the printer finds it is *unresolved* -- these .REL files carry no EXTERNAL records, so
`10A1'/'109F' cannot be named without PLILIB's load map, and the mechanism sentence was invented
rather than read.  What survives: the ASCII digit pairs are the literal being converted (safe to
decode, reproduces across E42P2/E43M1/E44B1/C1/D1), and traceback agreement between the two
compilers is byte-identity of a shared failure path, nothing more.  E44D1 is 256/256 identical, so
this whole correction cost no code.  Evidence: `spec/lab-evidence/e2e40-p8b/TAILWORD.txt`.

## [E2E-40/P9] What selects DR's operand-preservation route at an ADD: the RIGHT operand's addressing mode [C271]

**The change.** One predicate at the generic ADD route selector in `ocaml/lib/codegen.ml`:
`rhs_is_imem st r` (the operand about to be loaded into HL is a `FIXED BIN(<=15)` member of an
**internal** structure) replaces `vinfo_both_members st l r` (both operands are members).  Four
lines of executable code; the rest of the diff is the comment that used to state the old rule.

**Why the old rule could not be patched into shape.** `vinfo_both_members` takes `Eident` names, so
`(compound, member)` -- the exact shape E40S2/E40S4 fail on -- was not merely mis-classified, it was
inexpressible.  Prose described the residual as "unmeasured"; the implementation could not have
reached the question.

**The rule DR actually uses**, over seven initial probes (plus an eighth, E45S8, written after the
first seven had decided the compound-left case) whose operands are named from DR's own linked
`.COM` (`golden/e45/ADD_REGIONS.txt`), plus the two goldens that pinned the defect: park with
`PUSH H / LHLD <right> / POP D / DAD D` when the right operand is an internal member cell or is
itself compound; use `XCHG / LHLD <right> / DAD D` for an ordinary cell; emit no swap at all for a
literal (immediate pair + `DAD B`); and let the self-add ladder win first (`a = a + 5` has no `LHLD`
to park behind, E42P1).  Corpus-wide: **44 park sites, all 44 preceded by a load of a DATA cell**
(`golden/e45/scan_tails.py`, `golden/e45/CORPUS_SCAN.txt` -- which also states that the scan reads
DR's goldens only and therefore measures nothing about my build).

**E45S8 closes the last hole in the reading.**  `put list(h + a)` -- ordinary value in HL, member on
the right, **nothing stored afterwards**, so DE survives the load and my `writes_de` disjunct cannot
be DR's reason either.  DR parks; `golden/e45/E45S8/E45S8.REL` is 256/256 identical to this
compiler's; DR's own console is 24, predicted in `golden/e45/PREDICTIONS.txt`'s addendum before the
oracle ran.  Without that probe, E45S1's agreement would have been an artefact of the wrong
mechanism, and I would have written "the class rule is sufficient" on evidence that only showed the
two rules coinciding.

**Four errors of mine, recorded rather than deleted.**
(i) I diffed *instruction listings* instead of whole files, read DR's `LHLD <cell>` reloc operands
(printed `None/None` in my own output because they are RELOC records) as missing instructions, and
concluded the fix had missed its target.  [C264]'s mistake repeated one level up, by the tool that
had told me the truth in P6.
(ii) I then registered E45S1 as a shape divergence on the theory that my `XCHG` there was hidden by
identical bytes.  My E45S1 output already contains DR's `PUSH H` at 003A; the theory had silently
assumed the node went through the arm I changed.  The row was added and deleted within the slice.
(iii) I wrote a post-fix tail count (56) into `golden/e45/CORPUS_SCAN.txt` without re-running the
scan.  Struck, with a sentence about what that instrument can and cannot measure -- it reads DR's
goldens, so re-running it after a codegen change measures nothing about my build.
(iv) Commit `f4d894d` says "No codegen change in this commit" and contains 61 changed lines of
`codegen.ml`, including the new predicate.  A bare `git add -A` earlier in the same turn staged the
edit and `git commit` takes the index.  Pushed, so annotated rather than rewritten
(`spec/notes/e2e40-p9-add-operand-preservation-route.md` section 9, with the `--numstat` check that
finds this class of mismatch).  The pre-oracle chronology is unaffected: `b618332` has zero codegen
lines and E45S8's predictions state this compiler's post-change behaviour out loud.

**Gate after P9 (measured, `tools/e2e_gate.py --runtime` on the shipped build): 982 byte-exact / 0
fail** (973 + E40S2, E40S4 and the eight E45 specimens that compile), **129/129** refusals (+1:
E45S6, a *my-gap* negative -- DR compiles it, I refuse in the PUT-item matcher), **9/9** pinned
divergences (was 11: E40S2 and E40S4 left the panel, nothing new joined it), **45/45** runtime (+7:
E45S1-S5, S7, S8 at DR's own console values), coverage **86 rows / 0 errors / 0 warnings** (new row
`EXPR.ADD_PRESERVE_ROUTE'), census 44 programs / 15 EXACT / 0 DIFFERS / 0 UNEXPECTED with
`--verify' clean, INVENTORY 982, exit 0.

**Still open in this area.**  POINTER/BASED-view members as right operands (E40Q4, untouched:
`vinfo_imem` is `None` for them by construction).  ~~Array elements park in DR (E45S5's inner node,
LR4, RT4, AB6) but reach that by `writes_de`, not by the class test~~ **[P9a: two errors folded
together.  LR4/RT4/AB6 are member/array STORES, which park by [C266]'s destination rule and have
nothing to do with an ADD operand; and `writes_de` returns false for a plain array element, so no
disjunct of mine has ever been traced firing for one.  E45S5's inner node parks via `rhs_is_imem`.]**
Whether an array element as an ADD *right operand* parks at all has no sample; generalizing the class
test to it is one obvious probe, unmeasured.  SUB/MUL/DIV untouched.  `a + (-32768)` at a member and the
other unsampled store shapes from P8 stay refused.  And E45S6: DR accepts a parenthesized sum in a
`put list` item, which is a PUT-item-classifier gap, not a codegen one.

### [E2E-40/P9a] Documentation closure on P9: the route attribution was wrong, and I nearly
### concluded the fix was dead code

P9's prose said E45S1's inner `h + a' parks because of `writes_de'.  It does not: `writes_de` tests
`Eqptr' and `Vbased/Vbfix/Vbptr' rows, and an internal FIXED member is none of them.  Traced directly
(temporary `prerr_endline' per branch, run over the eight probes, then removed -- nothing ships):
`rhs_is_imem' fires twice for E45S1, once for E45S8, twice for E40S2/E40S4 and once for E45S5's inner
node; `writes_de' fires at none of those.  The counterfactual settles it -- building `b618332'
(HEAD minus the predicate) leaves `a + b + 5' byte-identical but puts E45S1 11 bytes from DR with an
`XCHG' at 003A.  Artifacts in `spec/lab-evidence/e2e40-p9a/'.

So E45S1 was already an independent falsification of [C260]'s class-pair reading, and E45S8
independently replicates the class result in a minimal two-operand PUT.  P9's E45S8 section claimed
the separating probe "has not been written" -- it had, by me, one commit earlier.

**The instrumentation error is the more transferable finding.**  Two of my five trace insertions
landed in a different `Ast.Ebinary (Ast.Add, ...)` arm, because the call-on-right arm at 3884 ends
with the same source text as the generic arm at 3936 and my anchor matched there first.  The first
run printed nothing at exactly the four programs the fix was supposed to explain, and "the shipped
predicate is dead code" looked like the only reading of that.  A trace answers *which instrumented
arm ran*; an absent line is weaker evidence than a present one, and it says nothing about placement.

Also corrected here: "both nodes flip" for S3/S7 and S1/S4 (only one node flips in each pair -- the
sentence contradicted the table four lines above it), the [C271] note that E45S6's array-element
parking was `writes_de', and the prediction record.  **P9's summary claimed all eight console values
had been predicted; `golden/e45/PREDICTIONS.txt' line 73 predicts 49 for E45S7 where DR printed 43**
(17+19+7 -- the prediction used `c' where the program names `a').  Seven of eight.  The pre-oracle
entry is left exactly as written; 43 is the authenticated runtime value in `spec/RUNTIME.txt'.

`DECL.MEMBER_SCOPE`'s parity is recomputed rather than incremented: **36 exact + 1 divergence
(E40Q4) of 37 registered probes = `MIXED:36/37'**, with `artefacts/ST12.PLI' kept in the probe list
but not counted, because it is a file reference and not a panel key.  `tools/panel_keys.py` is new
and does this by resolving cited names against `spec/INVENTORY.txt` (kind=specimen/refusal) and
`spec/DIVERGENT.txt`; reading the generated table is required because only 466 of the 982 specimens
are literal `SPECIMENS` dict keys -- the rest arrive through `SPECIMENS[x] = ...` in loops, which a
source-scanning count silently misses.  Coverage 86 rows / 0 errors / 0 warnings.

## [E2E-40/P10] A parenthesized ADD on the right of an ADD is evaluated FIRST by DR [C272]

**The change.**  Two additions to `ocaml/lib/codegen.ml`, one per problem: `num_width`'s recursive
width function gains `| Ast.Econd x -> w x` (parens are transparent for width, joining `unwrap_e`,
`add_left_needs_push`, `writes_de` and `rhs_is_imem`), and the generic FIXED ADD arm gains a
right-first route, placed before the existing route tests, gated as P10 shipped it by
`paren_add_right r && (add_left_needs_push r || writes_de st r || rhs_is_imem st r)` -- a suffix P10a
proved tautological and removed, so the shipped test is `paren_add_right r` alone.  `paren_add_right`
is
`Econd { e = Ebinary (Add, _, _) }` and nothing wider.

**Two gaps where P9 saw one.**  P9 registered E45S6 as a PUT-item-classifier refusal and noted,
correctly, that DR's three expression fixups read `DATA+2, +4, +0` -- `b, c, a` -- i.e. that DR
evaluates the parenthesized group first.  It then concluded the shape was "NOT about operand
preservation" and stopped.  Measured here: fixing the classifier alone makes the program compile and
leave **11 bytes** from DR's, because this compiler loads `a` first.  A fact in a comment is not a
fact applied.

**The order lives in the relocations, not the code.**  Both sides emit 17 bytes for the expression;
the difference is which cells the fixups name and in what order.  Cell identity comes from DR's own
DATA initializers (7/11/13 distinct) and the DATA layout is identical, so the comparison is not
circular and not about spelling.  Execution discriminated nothing at any point: both orders print 31
[C264, again].

**The bound, measured before and after.**  MB34 `n + (n*3)` and MB35 `(n+1) + (n*3)` are parenthesized
right operands whose inner operator is MUL; they reach this arm, DR evaluates them LEFT-first (MB34's
DATA fixups run 0x1, 0x1, 0x3 = n, n, m), and this compiler keeps them byte-identical -- which is why
the gate names the inner operator instead of testing for parentheses.  P10 also cited R722
`a + (b/d)` and LR19 `x + (-32768)` here; **[E2E-40/P10a] a branch trace shows neither reaches this
arm** (decimal operands; out-of-range literal), so DIV, SUB, EXP and a parenthesized literal are
UNSAMPLED at this arm, though both programs remain byte-exact specimens of the route they do take.  Unparenthesized compound rights keep [C271]'s route.  No
reassociation: the AST order is untouched, and no normalization to `(a + b) + c` anywhere.

**Gate (measured on the shipped build, `--runtime', exit read without a pipe):** 983 byte-exact / 0
fail, 128/128 refusals, 9/9 divergences, 46/46 runtime rows, coverage 86 rows / 0 errors / 0
warnings, census 44 programs / 15 EXACT / 0 DIFFERS / 0 UNEXPECTED with `--verify' clean, INVENTORY
983.  E45S6 promoted from negative panel to specimen and runtime row; the retirement text stays in
`tools/e2e_gate.py` where the entry was, because a `my-gap' row that vanishes silently is
indistinguishable from a gap that never existed [C256].

**Open after P10** *(three of these four statements are wrong; the P10a section below corrects them --
kept as the record of what P10 believed it had left open)*.  Parenthesized group on the LEFT of an
ADD; a parenthesized group inside a store RHS or a condition; inner SUB/EXP in a parenthesized right
operand -- all four have no sample, and each is one probe.  Unchanged from P9: POINTER/BASED-view members as right operands (E40Q4's 12-byte
gap), array elements as right operands (never traced through any disjunct), SUB/MUL/DIV ADD routes.

## [E2E-40/P10a] A tautological guard removed; two of P10's four witnesses were never at this arm

**The change.**  `if paren_add_right r && (add_left_needs_push r || writes_de st r || rhs_is_imem st r)`
becomes `if paren_add_right r`.  The suffix was not merely unnecessary, it was **provable from the
definitions**: `paren_add_right` matches only `Econd { e = Ebinary (Add, _, _) }` and
`add_left_needs_push` recurses through `Econd` to `Ebinary _ -> true`, so the first disjunct is true
whenever the guard is considered, for every AST value.  And `writes_de st r` in that position is dead
the other way: the match lives inside the `else` of `if writes_de st r`.  Body, arm order and every
surrounding branch are untouched -- verified by stripping all comments from HEAD's and this revision's
`codegen.ml` and diffing, which yields exactly one changed executable line -- plus one blank line that
moved with a relocated comment block (`spec/lab-evidence/e2e40-p10a/CODE-DIFF.txt`).  A
**semantics-preserving simplification, not a DR finding.**

**The write-up corrections, which are the substance of this slice.**  (1) P10 restored, over P9a's
corrected text, the comment claiming E45S1's inner park came from `writes_de` and that
`put list(h + a)` "has not been written" -- both disproved in P9a by branch trace, and re-disproved
here by the same instrument (`rhs_is_imem` fires at E45S1 inner and outer, at E45S8, at E40S2/E40S4's
outer; `writes_de` at none).  P9a's block is restored verbatim; P10's helper and its comment are kept.
(2) The conjunction was described as "load-bearing" and as the reason MB34/R722 stayed left-first; the
pattern is what excludes them, and the conjunction excluded nothing.  (3) R722 and LR19 were listed as
guards of this route; a trace shows neither reaches the generic FIXED ADD arm, so the sampled operator
set at this arm is **ADD (right-first, E45S6) and MUL (left-first, MB34/MB35) only**, and DIV, SUB,
EXP and a parenthesized literal are unsampled.  (4) The comment's relocation sequence had been written
as `0x2, 0x4, 0x0` twice; the recorded evidence is `0, 2, 4, 6, 8, A | 2, 4, 0 | 51`.  (5) The P10 note
carried a duplicated paragraph whose second copy said "the first five fixups agree" where six
initializers agree.  (6) `EXPR.ADD_PRESERVE_ROUTE`'s boundary column still asserted, in the present
tense, that E45S6 is a my-gap refusal and that E45S1's agreement came from `writes_de`; both removed,
one labelled historical clause kept in their place, and the row now says why `runtime=NONE` on it is
deliberate (both routes and both orders compute the same sum, so no linked-image run bears on this
contract).

**Gate (measured on this build).**  983 byte-exact / 0 fail, 128/128 refusals, 9/9 divergences,
46/46 runtime rows, coverage 86 rows / 0 errors / 0 warnings, census 44 programs / 15 EXACT /
0 DIFFERS / 0 UNEXPECTED with `--verify` clean, INVENTORY unchanged at 983 + 128.  E45S6 stays
256/256 identical to DR.  Clean-build warning count unchanged at 116 (pre-existing sites; this slice
adds none -- and note `dune` hashes content, so `touch` alone does not force a recompile and a cached
build prints no warnings, which briefly made the tree look warning-free).

**Open after P10a.**  Parenthesized DIV/SUB/EXP/literal as the right operand of a FIXED ADD at this
arm -- one probe each, and R722/LR19 do not answer them.  A parenthesized inner ADD inside a store's
RHS (MB34/MB35 show a parenthesized MUL there is left-first; the ADD case is unsampled).  A
parenthesized group inside a condition, and parenthesized groups on both sides -- no sample of either.
**Correction to P10's list above:** it says a parenthesized group on the LEFT has no sample.  It does --
MB35 `(n+1) + (n*3)' reaches this arm and DR computes the left group first and parks it (`LHLD n /
INX H / PUSH H / LHLD n / LXI D,3 / CALL ?IM22N / POP D / DAD D / SHLD m`, expression fixups
`0x1, 0x1, 0x3`).  What stays open there is `(a+b) + c`, a parenthesized left group with a SIMPLE
right operand: MB35's right is compound, so its order comes from [C271]'s park and says nothing about
a left-group rule.  Unchanged from P10: E40Q4's 12-byte POINTER-member gap, array elements as
right operands, SUB/MUL/DIV operand preservation.
