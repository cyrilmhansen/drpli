# Claims ledger — PL/I-80 reverse engineering

Every statement about the system lives here with a status and evidence
pointer. Statuses:

- `confirmed`   — reproduced in this project on a neutral oracle (cpmsim -8)
- `probed`      — black-box experiment run here, result recorded
- `inherited-unverified` — prior knowledge from ~/pli (2025-09 session),
  useful but NOT trusted; must re-derive before any `confirmed`
- `hypothesis`  — ours, awaiting experiment
- `false`       — falsified by experiment

Prior work is referenced as [PLI-LAB] = ~/pli/lab (Runes OCaml engine),
[PLI-QX] = ~/pli/cpm/pli80 (QX-10/MAME trace corpus). Binaries verified
byte-identical between [PLI-QX]/DISK1-2 and ./artefacts (except
OPTIMIST.PLI edited variant), so inherited claims apply to the same code.

| # | Claim | Status | Evidence / next experiment |
|---|-------|--------|----------------------------|
| C001 | Product is DR PL/I-80 v1.4 (serial 3032-0000-001130), compiler = PLI.COM + PLI0/1/2.OVL | confirmed | banners in artefacts; golden/run transcripts |
| C002 | Compiler runs correctly on pure Intel 8080 (no Z80 instructions) | **confirmed** | full 44-sample sweep under cpmsim `-8` with `-u` (undocumented-instruction trap active; none ever executed): golden/first8080u. Caveat: coverage = instructions executed during these compiles. |
| C003 | Pipeline: passes 1-2 in PLI.COM+PLI0+PLI1 emit a mnemonic IR tree file (".INT") on disk; PLI2.OVL is pass 3 (IR -> REL) | **confirmed** | Kill-catch experiment: SIGKILL after "IN PASS 2" leaves `demo.int` + opened PRN/REL entries on the work disk (golden/first8080u/evidence-kill-after-pass2.txt); `$V` "Verify Intermediate File" dumps the IR (C004). INT deleted by normal completion. Files are PREOPENED (0-byte entries appear for .PRN/.REL at compile start). |
| C004 | IR opcodes are 3-4 char mnemonics (BEG NID ENT LIO IID ILD C2 IAD IAS STP ...) with CTL control rows | **confirmed** | Captured on cpmsim via `PLI D:DEMO $V$L`: interleaved source/IR listing (BEG NID ENT LIO C2 ILD SIO SKP CID CLD PNC QIO STP + CTL 0251/0254 words) — same format as [PLI-QX] traces. Golden: golden/first8080u/evidence-DEMO-$V-trace.txt, golden/probes4/evidence-P008-SV-dump.txt, golden/probes5 (P011/P012). IR is per-statement-ordered; string operands printed as `* S(hex)`, addresses `#hex`. |
| C005 | Internal expression optimizer rewrites the IR (V trace vs E trace differ) | inherited-unverified | [PLI-QX]; v1.4 switches V,E,T |
| C006 | Compiler switches v1.0 era: B D I L N P S (+ later V E T M A C K per v1.4 harness) — max 7 after one `$` | hypothesis/probed | Applications Guide §2; [PLI-QX] default `'$V$E$T$I$D$K'`; verify each on v1.4 and find full table incl. undocumented ones |
| C007 | `PLI name $L$D` -> name.PRN listing on disk, name.REL object | confirmed | golden/run first session: DEMO.PRN 1024 B, DEMO.REL 512 B |
| C008 | Language perimeter = ANSI Subset G + DR deltas (cuts: DEFINED/LIKE/FLOAT DEC/...; adds: %REPLACE, READ/WRITE varying, ASCII/RANK, PICTURE v1.3+) | hypothesis (doc-based) | Language Manual intro; verify each delta by probe |
| C009 | PLILIB.IRL = Indexed Relocatable LIBRARY (LINK/LIB format), NOT a compiler IR | **confirmed** | LINK 1.31 (`C:LINK.COM`, PLILIB on same drive) + `LINK D:NAME` produces runnable .COM for 41/41 RELs (incl. externals with UNDEFINED SYMBOLS warnings kept as diagnostics); runs on CP/M 2.2 console: golden/link1, golden/run1. Linker map format captured (CODE/DATA/COMMON SIZE, USE FACTOR, /FCB/ placement, 8-char module name truncation). |
| C010 | Hard limits exist: SYMBOL TABLE OVERFLOW, BLOCK OVERFLOW, EXPRESSION OVERFLOW, AUTOMATIC STORAGE OVERFLOW, NESTED REPLACE, etc. | hypothesis | strings in PLI0/1/2.OVL; probe each to find numeric limit |
| C011 | v1.4 fixes 18 listed v1.3 bugs (MOD negative, LENGTH varying concat, BOOL, BIT(1)->BIT(8) copy, READ Varying overwrite, ...) | hypothesis | RELNOTES.PRN; build one probe per bug, expect post-fix semantics |
| C013 | 3 shipped samples are REJECTED by the shipped v1.4 compiler: CALL (1+4 errors), INVERT (2+10), MAININVT (3+5) | probed; root cause **confirmed for INVERT/MAININVT** | Probe P005 (`declare (d,a(maxrow,maxcol)) float binary(24)` with those names never defined) reproduces `SYNTAX ?` on the dcl line: golden/probes3. Shipped MATSIZE.LIB defines only TRUE/FALSE — a distribution defect (probably v1.3-era drift). CALL (different errors, source-edited `*/ entry constant */` cruft) still to be root-caused. |
| C014 | `%INCLUDE 'f'` without drive resolves to the SOURCE drive, not current drive | confirmed | `NO FILE D:RECORD.DCL` when context only on C:; golden/first8080u batch2 |
| C015 | PL/I-80 sources must have CR-terminated lines; LF-only input SILENTLY aborts compilation (header-only PRN, no REL, zero diagnostics) | confirmed | golden/probes (LF, 4/4 silent) vs golden/probes2 (CRLF, 4/4 ok) — probe id P000-LFEOL |
| C016 | With `$D`, listing+object are written to the drive of the SOURCE file | confirmed | outputs appeared on D: during first8080u sweep |
| C017 | `PLI` CLI takes up to 7 `$X` switches on the CP/M command line; `$L$D` = numbered source listing into .PRN on disk | confirmed | golden/first8080u; switch set B D I L N P S from Applications Guide §2; V E T M A C K present in v1.4 (old harness) — each still to be probed |
| C012 | QX-10 memory-map constants from prior INT parser (PLI2 base 0x2200, DESC_ADDR 0x1B4B, MNEM_ADDR 0x2353) | inherited-unverified | reload under cpmsim snapshot; addresses may differ under CP/M 2.2 vs CP/M+ QX layout |
| C018 | Full toolchain compile -> LINK -> execute works under cpmsim -8; linker output DETERMINISTIC across independent sessions | **confirmed** | DEMO.COM from two separate link sessions byte-identical (cmp). Goldens: golden/link1 (41 .COM + maps), golden/run1+run2. |
| C019 | Manual worked-example dialogs reproduce exactly: DECPOLY '12.2300' (Fig 5-2), FLTPOLY '1.2230000E+01' (Fig 5-1), LOAN1 27-month schedule '52.45/30.96/9.33' (Fig 12.1), ANNUITY 'Payment is $251.74' (Fig 12.2), LOAN2 full table last row '11/82 $0.25 ... $3,000.00 $456.97' (Fig 12.3) | **confirmed** | golden/run2/*.output.txt with scripted console input (typeahead ##SEND). See spec/notes/phase1-runtime.md. |
| C020 | RTL runtime diagnostics: `END OF FILE (1), File: SYSIN=CON`, `ZERO DIVIDE (2)`, `FIXED OVERFLOW (1)`, `ERROR (1), Conversion`; unhandled -> `Traceback: xxxx ...` hex return-address dump + `PL/I STOPPED.`/`STOP PL/I (Y/N)?`; ON ERROR units in samples can swallow EOF and re-loop | **confirmed** | golden/run1 (^Z sweep), golden/run2, golden/probes8run (P016). Numeric suffix meaning TBD (condition-code enumeration probe pending). |
| C021 | Default `FIXED` = FIXED BINARY(15,0) | **confirmed** | Manual l.1563/1568 + `$S` symbol-list dump (`D FIXED BINARY(15,0) AUTOMATIC`) + silent 16-bit wrap behavior (C024). |
| C022 | Max implemented FIXED precision = 15 (bin bits AND dec digits): FIXED BINARY(16/17/31), FIXED DECIMAL(18,0) -> `NOT IMP` on the declare + NO object file (compiler still prints CODE SIZE / END COMPILATION); bin(6) declare+assign+put is legal | **confirmed** | golden/probes7 P14A-E REL-presence matrix; manual l.3493 "precision 15 (the maximum precision)"; $S storage offsets: bin<=8 -> 1 byte, 9..15 -> 2, dec digits ~1B/2digits. |
| C023 | NOT IMP marker in a multi-line DECLARE is attributed to the statement's LAST line, not the offending element (P008/P012 flagged `t ...);` while the cause was `c fixed binary(31)`); single-line dcls flag accurately | confirmed (2 obs + controls) | golden/probes4, probes5, probes6 transcripts. |
| C024 | Fixed arithmetic: bin<=15 ops wrap SILENTLY to two's-complement 16-bit (300*300 -> 24464; RFACT n! mod 2**16 -> 0 from 18!); FIXED DECIMAL arithmetic exact BCD with CHECKED overflow -> FIXED OVERFLOW (1) stop (P016); constant->variable out of range -> ERROR (1), Conversion (P007) | **confirmed** | golden/probes3run, probes8run, run2/RFACT.evidence.txt, run1. |
| C025 | Our harness bug (fixed): batch.py classify() accepted pass-2-clean/pass-1-error compiles as "ok"; audit of first8080u: only the 3 known rejections affected — the 41-sample clean sweep stands | confirmed (meta) | oracle/batch.py requires BOTH passes clean now. |

## Cost policy (user constraint, revisit ~every 10 turns)
Prefer small targeted probes over bulk trace collection. Prior project
learned: unbounded concolic tracing produced more data than value.
Every probe must state beforehand: question, expected observations, max
output size. Traces live in `probes/`, extracted findings go here and to
`spec/notes/`; raw binaries stay in `golden/` only when they ARE the
evidence.
