# PL/I-80 — historical reimplementation project

Reverse-engineering of the Digital Research **PL/I-80 Compiler v1.4**
(CP/M-80, 1983) with the long-term goal of an OCaml reimplementation.

Method: scientific — no claim about compiler behavior is accepted without
an experiment against the original binaries. Live truth source:
[`spec/CLAIMS.md`](spec/CLAIMS.md). Grammar work:
[`grammar/pli80.ebnf`](grammar/pli80.ebnf).

## Layout

- `artefacts/` — original distribution (treat as READ-ONLY ground truth)
- `manuals/`   — DR manuals (scans + SHA256), `extracted/` = OCR text
- `oracle/`    — neutral oracle: z80pack `cpmsim -8` (pure Intel 8080)
  - `run.py`     tiny pty console driver (no external deps)
  - `batch.py`   golden-corpus runner (1 sim session per disk batch —
                 cpmsim cannot see host-side disk image changes while running)
  - `disks/`     generated drive images (gitignored)
- `golden/`    — captured compilations (transcripts, .PRN, .REL)
- `probes/`    — black-box micro-test programs + their results
- `spec/`      — claims ledger + derived notes; the project's memory
- `grammar/`   — hand-built grammar of the accepted subset
- `ocaml/`     — (later) the reimplementation, dune project

## Oracle quickstart

    cd oracle && python3 batch.py DEMO --switches '$L$D'
    # manual session:
    python3 run.py --disks disks /tmp/script.txt
    # script lines: plain CP/M commands; ##WAIT <regex>; ##SEND <txt>; ##HALT

Prior related research (kept deliberately separate — see spec/CLAIMS.md
for how it is used): `~/pli/lab` ("Runes") and `~/pli/cpm/pli80` (QX-10
traces). This project is a pragmatic restart: small experiments, bounded
data, revisited priorities every ~10 turns.

## Current status (rolling)
* Front end (OCaml): lexer → parser (218-file accept/reject parity gate)
  → binder ($S dump **43/43 byte-exact** gate) — DONE through binding.
* $V IR opcode dictionary: ~90 ops role-decoded (spec/notes/ir-opcodes.md).
* $C codegen oracle phase: OPENED — 20-specimen battery, pseudo-register
  model, inline-vs-RTL decisions, PLILIB index + ABI table extracted
  (spec/notes/codegen.md, tools/ctrace.py, spec/notes/plilib-*.txt).
* Next: branch/loop/call encodings, array addressing, $C-parity gate
  wiring, own back-end (IR builder → RTL-call codegen → .REL writer).

