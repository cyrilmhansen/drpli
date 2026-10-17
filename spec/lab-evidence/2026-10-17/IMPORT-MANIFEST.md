# Lab evidence snapshot — 2026-10-17

Immutable import per workspace policy (mainline = this repo; labs stay
independent; no bidirectional sync; mainline validation must not require
these paths to exist).

| File | Original location | Origin provenance | SHA-256 |
|---|---|---|---|
| `pli80-ir-opcodes-v01.json` | `~/pli/cpm/pli80/pli80-ir-opcodes-v01.json` (historical QX-10/MAME experiment tree, not a git repo) | user-supplied path; recorded as-is | `455c34390766b8adb8bb9f09e1701c5e3b8f61352250d1df745336f4309f0531` |
| `annotated-assembly-progress.md` | `~/pli/lab/research/annotated-assembly/progress.md` | Runes lab git HEAD `43e38bac088ea30903da86fb31d1e6cf802ed6ac` | `75cb0aba017fa8b0f3873844896a80f9d175f21d5eb9acf315c44bf21af8c98a` |
| `annotated-assembly-README.md` | `~/pli/lab/research/annotated-assembly/README.md` | same lab HEAD | `c02dcf042b03d5438153abc88e1fe8f361e91dd8c141976985c5a1b2f7e111e9` |

Purpose: these are referenced by `grammar/pli80.ebnf` (IR opcode
metadata) and by reconstruction status discussions. They are
**context evidence**, not build or gate inputs: no tool in `tools/`,
`oracle/`, or `ocaml/` reads this directory.

Re-import rule: copy anew, update this manifest (date, origin commit,
checksums), never edit files in place.
