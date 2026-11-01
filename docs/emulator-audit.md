# Emulator Audit — the Runes lab at `/home/john/pli/lab`

**E2E-50/P2, steps 1–2 deliverable.** Written 2026-11-02 by the P2 renewal-hop-1 session.
Sources: the accepted reconnaissance entries in `LEARNINGS.md` §
"2026-11-02 — E2E-50/P2 bootstrap + emulator audit reconnaissance", re-verified this session
file-by-file against the live lab, plus two lab evidence documents read in full
(`docs/pli80-cpm-surface.md`, `docs/i8080-exercisers.md`).

**Method and discipline.** The lab is READ-ONLY for this round (external tree; nothing was
created, modified or deleted there; tracked-file status unchanged: the same three pre-existing
untracked entries). Capability ratings are assigned ONLY from code read plus executed evidence;
the presence of code is never treated as proof of correctness (`PROTOCOL.md` #4). Verdict
vocabulary for the capability matrix: **IMPLEMENTED / PARTIAL / MISSING / UNTESTED /
KNOWN DEFECT**. "UNTESTED" means the behaviour exists in code but no executed evidence
distinguishes it from a defect; UNKNOWN is never rendered as PASS.

**Verified coordinates at write time.**
- Lab: dune project `pli80_lab` ("Runes"), git HEAD `43e38bac088ea30903da86fb31d1e6cf802ed6ac`,
  197 commits, single author (Cyril M. Hansen — the DRPLi operator), `README.md` opens
  "Runes — Executable software archaeology", initial target DR PL/I-80 v1.4.
- **No LICENSE/COPYING/NOTICE file anywhere in the tracked tree** (find over the whole lab,
  `_build` excluded; the only license files present are inside
  `tools/provenance-explorer/node_modules/`, i.e. third-party npm dependencies — see § 6).
- Layers relevant to execution: `lib/i8080` (alu, bus, cpu, decode, flags, instr, instr_format,
  memory, state, step, timing + interfaces), `lib/cpm` (bdos, fcb, filesystem, loader,
  personality), `lib/runner`, `lib/trace`. (`lib/analysis`, `lib/pli80`, `lib/pli80_host`,
  `bin/` proofs and `research/` belong to the reverse-engineering mission, not to the emulator
  core; see § 5–6.)

## 1. What the emulator is — and is not

Measured identity (code read, accepted):

- An **Intel 8080 concrete CPU core** (`lib/i8080`) executing a flat **64 KiB address space**
  (`memory.ml:3 size = 0x10000`), with typed out-of-range access errors and **no wrapping
  `load`**.
- Plus a **minimal, deterministic CP/M 2.2 *transient-process userspace runner***
  (`lib/cpm` + `lib/runner`): one selectable personality, `Cpm22` (`personality.ml:1 type t =
  Cpm22`). It is explicitly **NOT a complete CP/M emulator**:
  **no CCP, no BIOS, no disk images, no physical allocation geometry**. The lab's own
  architecture law (`docs/pli80-cpm-surface.md` header, `docs/cpm-personality-boundary.md`):
  "CP/M 2.2 userspace minimal" is the contract; QX-10/CP/M-Plus observations are a
  differential *observation environment*, never the target runtime; a run forced only by
  faking BDOS 12 "does not constitute a real CP/M 2.2 run".
- **Process model:** COM image loaded at `0100h` (`loader.ml:1`), size-bounded
  (`Program_too_large` typed error), entry point `0100h`; BDOS invoked at guest PC `0005h`
  (`bdos_entry_address Cpm22 = 0x0005`), termination observed at PC `0000h` (warm boot) or
  BDOS function 0; personality installs page zero, overlapping default FCBs, a command tail
  limited to 127 characters (`Invalid_command_tail`), stack `0fffeh`, DMA convention `0080h`.
  CP/M's A→L / B→H return aliasing is applied on every Continue (`bdos.ml:261-265`, commented
  as the compatibility convention).
- **CLI:** `pli80-run [--trace FILE] [--max-steps N] PROGRAM.COM` (`bin/main.ml:2`); default
  budget `default_max_steps = 100_000` (`runner.ml:141`); positive integer enforced.
- **Determinism:** the filesystem is memory-backed, keyed `{drive; user; name}` with
  128-byte logical records, max 65,536 records/file, drives 0–15, users 0–31, typed model
  limits (`filesystem.ml`); BDOS console status returns "no character pending" (0)
  deterministically; console input is not provided at all (see § 2). A structured trace
  format (`lib/trace`, `--trace`) records steps, BDOS calls and effects.

## 2. Capability matrix

| # | Capability | Rating | Evidence (all re-read or re-run this session) |
|---|---|---|---|
| 2.1 | 8080 opcode decode | **IMPLEMENTED** (decoding + execution exist for all 256 codes) | `test/cpu_core.exe` prints "Opcode coverage: 256 supported, none intentionally unsupported" (suite re-run rc=0) |
| 2.2 | Undocumented alias opcodes 08h,10h,18h,20h,28h,30h,38h,0CBh,0D9h,0DDh,0EDh,0FDh (NOP/JMP/RET/CALL spellings) | **UNTESTED** (semantics) | `decode.ml:24-29` verbatim: "historically reported 8080 behaviors, supplied as a work list for later confirmation. They have not been experimentally verified by this project" |
| 2.3 | ALU + flag semantics | **IMPLEMENTED, exhaustively tested** | `test/alu_flags.exe` re-run rc=0: 976,272 exhaustive cases checked against an independent bit-ripple reference |
| 2.4 | Memory model (flat 64 KiB, typed OOR, no-wrap load) | **IMPLEMENTED** | `memory.ml` (`size = 0x10000`); loader bounds; `cpm_runner.exe` loader-bounds tests rc=0 |
| 2.5 | Interrupts (RST 7 vectoring, acknowledge protocol) | **IMPLEMENTED, lab-tested** | `test/cpu_interrupts.exe` re-run rc=0; typed "interrupt acknowledge … requires N bytes" errors in `runner.ml:70-72` |
| 2.6 | Timing model | **IMPLEMENTED, lab-tested** | `lib/i8080/timing.ml`, `test/timing.exe` rc=0 (state model, not wall-clock fidelity — no claim of cycle accuracy) |
| 2.7 | COM loading | **IMPLEMENTED** | `loader.ml`: `0100h`, `Program_too_large`, `File_error` typed; integration test HELLO.COM rc=0 |
| 2.8 | Page zero / FCB / command tail | **IMPLEMENTED** | `personality.ml:55 install_page_zero`, tail limit 127, `Invalid_command_tail` |
| 2.9 | BDOS implemented set {0,2,9,11,12,15,16,19,20,21,22,26} | **IMPLEMENTED, integration-tested** | `bdos.ml:124-249` re-read: 0 terminate; 2 conout; 9 print `$`-string (`Unterminated_string` typed error); 11 console status → 0; 12 version → A=22h,HL=0022h + the documented CP/M 2.2 convention; 15 open; 16 close; 19 delete; 20 read sequential (extent transitions at records 127→128 modelled, `bdos.ml:89-91`); 21 write sequential; 22 list file names; 26 set DMA |
| 2.10 | BDOS functions >40 | **IMPLEMENTED (per stated model)** | `bdos.ml:119 bdos_function_limit = 40`; `250-254`: out-of-range zero-return fallback (A=B=HL=0), matching the CP/M 2.2 convention measured by the lab's z80pack cpmsim 1.39 probe (`pli80-cpm-surface.md` § Authentic CP/M 2.2 validation) |
| 2.11 | Every other BDOS number | **typed failure, never silent success** | `bdos.ml:255 → Error (Unsupported_function number)`; surfaced as `pli80-run: unsupported BDOS function N` + exit 1 |
| 2.12 | Console INPUT (BDOS 1, 10; also 12-as-getchar is *version*, not input) | **MISSING** | functions 1 and 10 are absent from the dispatch → typed `Unsupported_function`. Consequence: interactive PL/I `GET`/`ASK` paths and the documented interactive OPTIMIST example cannot run here |
| 2.13 | List/punch device output (BDOS 5 etc.) | **MISSING** | not in dispatch; `PLI.COM …$L` listing paths call fn 5 per the lab census (observed statically), so listing-option runs would abort with a typed error |
| 2.14 | Search first/next (17,18), rename (23), random I/O, login vector (24) | **MISSING** | absent from dispatch; the lab's own plan is to add them only on evidence (`pli80-cpm-surface.md` § Étapes 3–4: "Ne pas ajouter Search/Random par anticipation") |
| 2.15 | CP/M Plus / BIOS / CCP / disk images | **MISSING by design** | architecture law § 1; CP/M Plus fn 108 is deliberately NOT implemented with Plus semantics — the zero fallback covers the observed `PLI.COM` exit call (verified both by code and by the authentic-2.2 probe) |
| 2.16 | Filesystem | **IMPLEMENTED (logical model)** | memory-backed, drive/user/name keys, 128-byte records, deterministic listing order, extent snapshots; **KNOWN LIMIT:** no physical geometry, no host-backed passthrough |
| 2.17 | Trace | **IMPLEMENTED** | `lib/trace` + `--trace`; `test/trace_format.exe` rc=0; step indices, BDOS call events, register-effect diffing (`bdos.ml:287-305`) |
| 2.18 | Exit-code discipline | **IMPLEMENTED, with one harness caveat** | `bin/main.ml:104-141`: normal termination → program output flushed to stdout, exit 0; any runner error (unsupported BDOS, step limit, CPU halt, load error, bad tail) → message on stderr, exit 1. **Caveat (measured this session, accepted):** on the error path the buffered program output is DISCARDED — a harness must not read partial stdout as evidence of partial progress |
| 2.19 | Step budget | **IMPLEMENTED** | default 100,000 (`runner.ml:141`); CLI `--max-steps`; step counting includes host transitions (`runner.ml:196`); exercisers needed up to 4,000,000,000 via CLI |
| 2.20 | Determinism of the whole pipeline | **PARTIAL** | same-input reruns are deterministic by construction (memory-backed FS, no wall-clock in state); no executed double-run equality proof exists yet in the lab suite → the P2 harness (step 5) will measure it |

## 3. Executed evidence behind the ratings (this chain)

- **Lab suite re-run (accepted, previous session of this chain, method re-confirmed this
  session):** building writes only the lab's gitignored `_build/`; the seven emulator-relevant
  test executables — `alu_flags`, `primitives`, `cpu_core`, `cpu_interrupts`, `timing`,
  `cpm_runner`, `trace_format` — ALL rc=0 on opam switch 5.4.0 / dune. `cpm_runner.exe`
  covers loader bounds, typed BDOS errors (incl. `Unsupported_function 7`), sequential files,
  extent snapshots, a HELLO integration run, warm-boot termination, step-limit and halted-CPU
  paths. (The lab `test/` tree contains ~40 further executables belonging to the RE mission;
  they were not run — out of audit scope.)
- **Independent corroboration (pre-existing record, NOT re-run here; corroboration, not
  proof):** `docs/i8080-exercisers.md` — TST8080, 8080PRE, CPUTEST and 8080EXM (all 25 CRC
  groups) PASS under the runner, cross-checked against the pinned MIT `superzazu/8080` at
  commit `274ffd700b81baabea99b0963bc1260b67132185` with identical success and CRCs; step
  counts differ by shim design only. Source URLs and SHA-256 of each .COM are recorded in
  that table; the four binaries are deliberately NOT committed (re-verified: nothing named
  `*.COM` except the labelled `examples/HELLO.COM.asm` source).
- Optional C harness `test/reference/daa_superzazu.c` exists (re-verified path); the
  superzazu library is NOT vendored.

## 4. Relevance to the PL/I-80 workflow (Lane B feasibility)

Measured census (`pli80-cpm-surface.md`, dynamic runs — compiler `PLI OPTIMIST`):

- Under QX-10/CP/M Plus + MAME, the transient census (1,936 BDOS entries to the warm-boot
  witness) used functions **2, 11, 12, 15, 16, 19, 20, 21, 22, 26** and one CP/M-Plus-only
  **108** at exit; under **authentic CP/M 2.2 (z80pack cpmsim 1.39)** `PLI OPTIMIST` completed
  and produced `OPTIMIST.REL` **byte-identical** (1,408 bytes, SHA-256 `5fca1ffe…`) to the
  QX-10 reference; fn 12 answered `HL=0022h`, fn 108 fell back to zero.
- **Every dynamically observed compile-time function is in the Runes implemented set** (§ 2.9)
  → the audited emulator is plausibly sufficient to *run the historical compiler* itself.
  Static-only call sites (1, 5, 9, 25) sit outside the observed compile path; no
  Search/Rename/Random calls were captured pre-warm-boot.
- **NOT yet measured:** the BDOS census of a *LINK-80'd user program* (e.g. our compiled
  TABLE programs → `.REL` → `LINK` + `PLILIB.IRL` → `.COM`). The predecessor's hypothesis
  ("pure PUT LIST needs only fn 2 + terminate; stdin needs 1/10") stays **PROPOSED**; step 6
  must MEASURE it by running the linked .COM under `pli80-run` and recording the observed
  call sequence (typed `unsupported BDOS function N` on failure). Until measured, any TABLE
  run on this emulator is at best UNKNOWN, never assumed.
- LINK-80 itself has never been run under Runes (the lab table marks it "documented; not
  executed in that study"). P2 step 6 uses the project's existing oracle-harness route for
  LINK; that is a bounded, lane-labelled run per the mission brief.

## 5. Provenance and license audit (evidence)

| Component | Evidence (re-verified at write time) | Classification |
|---|---|---|
| **Runes lab** (`/home/john/pli/lab` code) | No LICENSE anywhere in tracked tree (find, § 0); 197-commit single-author history, no vendored third-party sources in `lib/` | **UNLICENSED — operator-original work; redistribution rights UNRESOLVED.** Licensing it is an OPERATOR decision; this round must not and did not add one |
| **z80pack** (`thirdparty/z80pack/LICENSE`) | MIT, "Copyright (c) 1987-2025 Udo Munk and others" (relicensed from the old non-profit clause) | **CONFIRMED REDISTRIBUTABLE** (MIT attribution) |
| **superzazu/8080** | Primary source checked (GitHub LICENSE, © 2018 Nicolas Allemand); pinned commit `274ffd7…` recorded in lab doc; NOT vendored | **MIT — usable as a labelled comparison emulator** if ever vendored with attribution |
| **TST8080.COM** | Microcosm Associates diagnostic, © notice in source, no explicit grant; SHA-256 + URL recorded | **RESTRICTED / UNRESOLVED** — user-supplied only |
| **CPUTEST.COM** | SuperSoft Diagnostics II, © 1981 (binary's own output); no license found | **RESTRICTED / UNRESOLVED** — user-supplied only |
| **8080PRE / 8080EXM** | `.MAC`/`.ASM` sources carry GPL-2.0-or-later terms; the doc itself states binary status was NOT separately assessed | **MIXED — binary redistribution status UNRESOLVED**; GPL source does not settle the .COM |
| **CP/M 2.2 system binaries** (z80pack disk images; mirrored `oracle/disks/*.dsk`) | Caldera 1997/98 conditional release (not OSI; informal 2022 relaxation noted on cpm.z80.de) | **REDISTRIBUTABLE SUBJECT TO CONDITIONS — needs legal care before any package** |
| **DR PL/I-80 v1.4, LINK-80, PLILIB.IRL** (`artefacts/`; `PLI.COM` banner re-read: "Copyright (c) 1980-1982 Digital Research, Inc.") | Not covered by the Caldera CP/M release | **RESTRICTED** — Lane B, user-supplied, NEVER in a release artifact |
| **lab `research/annotated-assembly`** (14M) | README re-read: reconstructs the four DR v1.4 images with byte-exact verification; verification requires originals supplied separately | **DERIVATIVE OF PROPRIETARY DR BINARIES — EXCLUDED from any free-core package** |
| **lab `research/minimal-baseline`** (17M) | README re-read: byte-level coverage analysis of the historical images ("94,720 historical bytes remain exact"; RAW/DECODED/STRUCTURED/UNDERSTOOD census over image bytes) | **DR-image derivative evidence — EXCLUDED from free core** (same basis as annotated-assembly) |
| **lab `research/host-compiler`** (25M) | Pass READMEs re-read: "Faithful host compiler boundary reconnaissance" — native shadow reconstruction packets derived from the historical compiler images | **DR-image derivative evidence — EXCLUDED from free core** |
| lab `research/{discriminator,fizzbuz-delta,plm80-oracle}` (small) | directory shape read; plm80-oracle concerns PLM-80 (another DR product) experiments | **RE evidence, NOT emulator core; classification for distribution UNTESTED** — irrelevant to both packages unless ever quoted |
| lab `tools/{annotated-assembly,provenance-explorer}` | node frontends; `provenance-explorer/node_modules/` present with many third-party licenses — dependency tree NOT audited | **UNRESOLVED; out of emulator-core scope** |
| `/home/john/pli/cpm/QX10CPMPlus` | README.TXT re-read: "QX-10 CP/M Plus … Supplied by MML Systems Ltd. Version 3.1A (01:Jun:84)", TD0 images assembled by Fred Jan Kraan 2004 from Don Maslin's collection; no license grant | **PROPRIETARY-LINEAGE (CP/M Plus + QX10), status UNRESOLVED — excluded from both packages** |
| `examples/HELLO.COM.asm` + `test` fixtures in lab | lab-authored | follows the lab's own UNRESOLVED status |

## 6. Two-package redistribution matrix

Package A = *free redistributable core* (everything a functional Lane A run needs, shippable
today-or-after-one-decision); Package B = *historical-compat lane* (Lane B: never shipped,
always user-supplied, provenance-labelled).

| Item | Package A (free core) | Package B (historical-compat) |
|---|---|---|
| DRPLi OCaml compiler sources | ALLOWED (project-original; DRPLi repo governs) | same code, no DR bytes |
| Functional harness `tools/functional_runner.py` + specs | ALLOWED | same harness, extra lanes |
| TABLE corpus sources (originals written this round, provenance headers) | ALLOWED as original works | also fed to historical tools |
| **Runes emulator** (`pli80-run`, `lib/i8080`, `lib/cpm`, `lib/runner`, `lib/trace`) | **BLOCKED on the operator's license decision** (§ 5 row 1) — the code itself contains no third-party content | may RUN locally once licensed or user-supplied; shipping blocked independently of B's restrictions |
| z80pack / cpmsim | ALLOWED under MIT with attribution (include `LICENSE`) | permitted as a tool, not shipped with DR disks |
| superzazu/8080 | ALLOWED under MIT if vendored with attribution; today only a labelled external reference | n/a |
| Exerciser .COMs (TST8080, CPUTEST, 8080PRE, 8080EXM) | **EXCLUDED** (binaries unresolved; GPL-source-of-two does not clear the binaries). Option: user-supplied acceptance script by hash+URL (§ 7) | user-supplied only |
| CP/M 2.2 system (BDOS/CCP/BIOS binaries, `.dsk`) | **CONDITIONAL** — Caldera-terms review required before inclusion; recommend the Runes minimal runner instead (no system binaries at all) | user-supplied disk images, never packaged |
| DR `PLI.COM`, overlays, `LINK.COM`, `PLILIB.IRL` | **FORBIDDEN** | **user-supplied only; never in any release artifact** (existing repo rule) |
| lab `research/*` DR-image derivatives | **FORBIDDEN** | reference material only, not packaged |
| node tools + `node_modules` | EXCLUDED until dependency-tree audit | n/a |
| QX10CPMPlus | FORBIDDEN (unresolved proprietary) | not needed (observation environment only) |

**No operator-level license is decided by this document** — it records evidence and options.

## 7. Blockers and release-readiness path

1. **Blocker (license, operator-owned):** the Runes lab is unlicensed → Package A cannot ship
   the emulator today. Options recorded for the operator: (a) add an OSI license to the lab;
   (b) vendor only the 4 emulator libs into DRPLi under a project license; (c) keep Lane A
   fixtures running under z80pack cpmsim (MIT) or user-supplied `pli80-run`. This round
   decides none of these.
2. **Blocker (legal):** CP/M 2.2 system binaries are Caldera-conditional; any Package A that
   ships them needs a conditions review. The Runes minimal-runner design sidesteps this
   entirely (no system binaries) — recommended Lane A substrate once 1 is resolved.
3. **Open measurement (step 6):** runtime BDOS census of LINK-80'd PL/I programs on Runes is
   UNMEASURED (§ 4); classify each TABLE verdict BLOCKED/UNKNOWN honestly until observed.
4. **Open question (accepted as owed work, PROPOSED):** adopt the four public exercisers as
   an OPTIONAL user-supplied Lane A acceptance script (hashes + URLs already recorded in the
   lab doc; binaries never committed).
5. **Known harness defect to design around:** `pli80-run` discards buffered program output on
   any error path (§ 2.18) — the P2 harness must treat stdout as valid only at exit 0 and use
   `--trace` when failure-side evidence is needed.
6. **Untested areas listed for honesty:** alias-opcode semantics (§ 2.2), whole-pipeline
   determinism proof (§ 2.20), `$L`-listing and interactive paths (§ 2.12–2.13), RE research
   directories' distribution status (§ 5).

## 8. Verdict

The audited emulator is a **credible, tested, deterministic 8080 + minimal CP/M 2.2 transient
runner** — its implemented BDOS set exactly covers the dynamically observed historical
compile scenario, and its deliberate typed-failure discipline (never a silent success on
unsupported calls) is precisely what the P2 harness needs for honest verdicts. Its limits are
documented and structural: no console input, no search/random I/O, no system binaries, and —
for redistribution — an unresolved license on the single-author lab code. None of these are
defects disguised as capabilities: this audit classifies what is measured and marks the rest
UNTESTED/MISSING/BLOCKED, per protocol.
