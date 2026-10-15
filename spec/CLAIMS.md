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
| C003 | Pipeline: passes 1-2 in PLI.COM+PLI0+PLI1 emit a mnemonic IR tree file (".INT") on disk; PLI2.OVL is pass 3 (IR -> REL) | inherited-unverified | [PLI-QX] qx10-compile-v13 INT writer/reader traces; corroborated by strings "EOF ON INT FILE"/"BAD INT FILE" + ext table REL/INT/PLI. Verify: does an INT temp file appear on disk during compile (kept or deleted?) |
| C004 | IR opcodes are 3-4 char mnemonics (BEG NID ENT LIO IID ILD C2 IAD IAS STP ...) with CTL control rows | inherited-unverified | [PLI-QX] ADD1 V/E traces; opcode table visible in PLI2.OVL strings |
| C005 | Internal expression optimizer rewrites the IR (V trace vs E trace differ) | inherited-unverified | [PLI-QX]; v1.4 switches V,E,T |
| C006 | Compiler switches v1.0 era: B D I L N P S (+ later V E T M A C K per v1.4 harness) — max 7 after one `$` | hypothesis/probed | Applications Guide §2; [PLI-QX] default `'$V$E$T$I$D$K'`; verify each on v1.4 and find full table incl. undocumented ones |
| C007 | `PLI name $L$D` -> name.PRN listing on disk, name.REL object | confirmed | golden/run first session: DEMO.PRN 1024 B, DEMO.REL 512 B |
| C008 | Language perimeter = ANSI Subset G + DR deltas (cuts: DEFINED/LIKE/FLOAT DEC/...; adds: %REPLACE, READ/WRITE varying, ASCII/RANK, PICTURE v1.3+) | hypothesis (doc-based) | Language Manual intro; verify each delta by probe |
| C009 | PLILIB.IRL = Indexed Relocatable LIBRARY (LINK/LIB format), NOT a compiler IR | confirmed | SOURCES.md/LINK-80 §1.7 + LIB.COM strings REL/IRL; links DEMO via LINK command [pending full-chain test] |
| C010 | Hard limits exist: SYMBOL TABLE OVERFLOW, BLOCK OVERFLOW, EXPRESSION OVERFLOW, AUTOMATIC STORAGE OVERFLOW, NESTED REPLACE, etc. | hypothesis | strings in PLI0/1/2.OVL; probe each to find numeric limit |
| C011 | v1.4 fixes 18 listed v1.3 bugs (MOD negative, LENGTH varying concat, BOOL, BIT(1)->BIT(8) copy, READ Varying overwrite, ...) | hypothesis | RELNOTES.PRN; build one probe per bug, expect post-fix semantics |
| C013 | 3 shipped samples are REJECTED by the shipped v1.4 compiler: CALL (1+4 errors), INVERT (2+10), MAININVT (3+5) | probed | golden/first8080u PRNs. Root-cause hypothesis: INVERT/MAININVT `SYNTAX ?` at `(d,a(maxrow,maxcol)) float binary(24)` because shipped MATSIZE.LIB defines TRUE/FALSE (belongs to OPTIMIST), not maxrow/maxcol — array subscripts must be constants; CALL file appears source-edited (`*/ entry constant */` cruft). Probe P005 (undefined name as subscript) pending. |
| C014 | `%INCLUDE 'f'` without drive resolves to the SOURCE drive, not current drive | confirmed | `NO FILE D:RECORD.DCL` when context only on C:; golden/first8080u batch2 |
| C015 | PL/I-80 sources must have CR-terminated lines; LF-only input SILENTLY aborts compilation (header-only PRN, no REL, zero diagnostics) | confirmed | golden/probes (LF, 4/4 silent) vs golden/probes2 (CRLF, 4/4 ok) — probe id P000-LFEOL |
| C016 | With `$D`, listing+object are written to the drive of the SOURCE file | confirmed | outputs appeared on D: during first8080u sweep |
| C017 | `PLI` CLI takes up to 7 `$X` switches on the CP/M command line; `$L$D` = numbered source listing into .PRN on disk | confirmed | golden/first8080u; switch set B D I L N P S from Applications Guide §2; V E T M A C K present in v1.4 (old harness) — each still to be probed |
| C012 | QX-10 memory-map constants from prior INT parser (PLI2 base 0x2200, DESC_ADDR 0x1B4B, MNEM_ADDR 0x2353) | inherited-unverified | reload under cpmsim snapshot; addresses may differ under CP/M 2.2 vs CP/M+ QX layout |

## Cost policy (user constraint, revisit ~every 10 turns)
Prefer small targeted probes over bulk trace collection. Prior project
learned: unbounded concolic tracing produced more data than value.
Every probe must state beforehand: question, expected observations, max
output size. Traces live in `probes/`, extracted findings go here and to
`spec/notes/`; raw binaries stay in `golden/` only when they ARE the
evidence.
