#!/usr/bin/env python3
"""Deterministic builder for the Lane A functional SUBSTRATE fixtures.

E2E-50/P2 step 6 (2026-11-02).  Original DRPLi work: hand-encoded Intel 8080 CP/M `.COM`
images that exercise the audited free-core emulator (`docs/emulator-audit.md` 2.7 COM loading,
2.9 BDOS {0,2,9,11,12}, 2.11 typed failure on an unimplemented function, 2.12 no console input,
2.18 stdout valid only at exit 0) WITHOUT any compiler and WITHOUT any Digital Research
content.  They are the Lane A artifacts pinned by `spec/functional/tests/FX-*.json`.

Why a generator instead of a committed blob: the image AND its annotated `.asm` listing are
rendered from ONE op table, so listing, bytes and hash cannot drift apart, and `--check` proves
the committed artifacts still agree with it (a listing that drifts from its binary is worthless
evidence).  The encodings were cross-checked against the audited decoder
(`/home/john/pli/lab/lib/i8080/decode.ml` `lower_opcode`: `opcode land 7` = 4 INR, 5 DCR,
6 MVI with the register in bits 3-5; `opcode land 0x0f = 0x01` LXI) and against the lab's own
`examples/HELLO.COM.asm` byte listing (`0E 09 11 0D 01 CD 05 00` = MVI C,9 / LXI D / CALL 5).

Law (`spec/functional/tests/README.md` L3): the EXPECTED output of a fixture comes from
`reference.py`, i.e. from what the source DECLARES it prints -- never from a capture of the run.
A fixture PASS is evidence about the harness and the substrate, never about PL/I.

usage:
    python3 tools/mk_functional_fixture.py --write        # write .COM images + listings
    python3 tools/mk_functional_fixture.py --check        # verify them against this table
"""

import argparse
import hashlib
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORG = 0x0100                    # CP/M transient entry point (audit 2.7)
BDOS = 0x0005                   # BDOS entry address of the Cpm22 personality (audit 2.7)

FIXTURE_DIR = os.path.join(ROOT, "spec", "functional", "fixtures")
SPEC_DIR = os.path.join(ROOT, "spec", "functional", "tests")

# Intel 8080 register codes, as the audited decoder reads them (bits 3-5 of MVI/INR/DCR).
REG = {"B": 0, "C": 1, "D": 2, "E": 3, "H": 4, "L": 5, "M": 6, "A": 7}
LXI_RP = {"B": 0, "D": 1, "H": 2, "SP": 3}


def mvi(reg, imm):
    """MVI r,d -> 0x06 | (r << 3), d   (verified: 0x0E 0x09 = MVI C,9)."""
    return bytes([0x06 | (REG[reg] << 3), imm & 0xFF])


def lxi(rp, addr):
    """LXI rp,nn -> 0x01 | (rp << 4), lo, hi   (verified: 0x11 0x0D 0x01 = LXI D,010DH)."""
    return bytes([0x01 | (LXI_RP[rp] << 4), addr & 0xFF, (addr >> 8) & 0xFF])


def call(addr):
    """CALL nn -> 0xCD, lo, hi   (verified: 0xCD 0x05 0x00 = CALL 0005H)."""
    return bytes([0xCD, addr & 0xFF, (addr >> 8) & 0xFF])


def _ascii(b):
    return "'%s'" % chr(b) if 0x20 <= b < 0x7F else "0%oH" % b


FN_NAME = {0: "TERMINATE", 1: "CONSOLE INPUT (MISSING)", 2: "CONSOLE WRITE",
           9: "PRINT $-STRING", 11: "CONSOLE STATUS", 12: "VERSION"}


def program(banner, chars, extra_funcs=(), input_func=None):
    """Return (ops, banner) where each op is (mnemonic, comment, bytes).

    Sizes are fixed per instruction, so the message address is known before the image is
    emitted (one pass, no patching, no drift between listing and bytes)."""
    size = 8 + 7 * len(chars) + 5 * len(extra_funcs) + (5 if input_func is not None else 0) + 5
    msg = ORG + size
    ops = [("MVI C,09H", "BDOS FN 9", mvi("C", 9)),
           ("LXI D,MSG", "DE -> STRING AT %04XH" % msg, lxi("D", msg)),
           ("CALL 0005H", "BDOS ENTRY", call(BDOS))]
    for b in chars:
        ops.append(("MVI E,%s" % _ascii(b), "CHARACTER", mvi("E", b)))
        ops.append(("MVI C,02H", "BDOS FN 2", mvi("C", 2)))
        ops.append(("CALL 0005H", "BDOS ENTRY", call(BDOS)))
    for fn in extra_funcs:
        ops.append(("MVI C,%02XH" % fn, "BDOS FN %d: %s" % (fn, FN_NAME[fn]), mvi("C", fn)))
        ops.append(("CALL 0005H", "RESULT DISCARDED", call(BDOS)))
    if input_func is not None:
        ops.append(("MVI C,%02XH" % input_func, "BDOS FN %d: %s"
                    % (input_func, FN_NAME[input_func]), mvi("C", input_func)))
        ops.append(("CALL 0005H", "DIES WITH TYPED ERROR", call(BDOS)))
    ops.append(("MVI C,00H", "BDOS FN 0", mvi("C", 0)))
    ops.append(("CALL 0005H", "WITNESS bdos:0", call(BDOS)))
    return ops, banner


FIXTURES = {
    "FX-00": dict(
        banner=b"FX-00 CORE OK\r\n$",
        chars=b"BDOS2-OK\r\n",
        extra_funcs=[11, 12],
        header="""; FX-00.asm -- ORIGINAL DRPLi SUBSTRATE FIXTURE (E2E-50/P2 step 6,
; 2026-11-02).
; Author: DRPLi E2E-50/P2 step 6. Origin: original work; no compiler
; involved,
; no Digital Research content, no third-party code.
; Spec: FX-00.json; expected output: reference.py:fx00 (DECLARED here,
; never
; captured from a run -- README law L3).
;
; PURPOSE. Exercise the Lane A path of tools/functional_runner.py end
; to end on
; the audited free-core emulator (docs/emulator-audit.md 2.7 COM
; loading at
; 0100H, 2.9 BDOS 9/2/11/12, 2.18 stdout valid only at exit 0): BDOS 9
; banner,
; ten BDOS 2 characters, BDOS 11 and 12, BDOS 0 termination. A PASS is
; evidence
; about harness + substrate, never about PL/I semantics.
;
; Generated by tools/mk_functional_fixture.py (the same table emits the
; .COM);
; do not hand-edit the byte listing. Address column = load address."""),
    "FX-01": dict(
        banner=b"FX-01 BEFORE-TYPED-ERROR\r\n$",
        chars=b"",
        input_func=1,
        header="""; FX-01.asm -- ORIGINAL DRPLi NEGATIVE SUBSTRATE FIXTURE (E2E-50/P2
; step 6).
; Author: DRPLi E2E-50/P2 step 6. Origin: original work; no compiler,
; no DR
; content. Spec: FX-01.json; expected (declared, not captured):
; reference.py:fx01.
;
; PURPOSE. The audited emulator implements NO console input (audit
; 2.12: BDOS 1
; and 10 are absent from the dispatch) and fails TYPED, never silently
; (audit
; 2.11). This fixture prints its banner, then calls BDOS function 1 and
; therefore
; dies with `pli80-run: unsupported BDOS function 1' and exit 1. The
; INTENDED
; harness verdict is FAIL with attribution `emulator': this fixture
; measures the
; typed-error classification and the stdout-discard law (audit 2.18)
; against the
; REAL substrate, not a stub.
;
; Generated by tools/mk_functional_fixture.py; do not hand-edit the
; byte listing."""),
}


def build(name):
    ops, banner = _prog(name)
    return b"".join(b for _m, _c, b in ops) + banner


def _prog(name):
    kw = {k: v for k, v in FIXTURES[name].items() if k != "header"}
    return program(**kw)


def listing(image):
    return " ".join("%02X" % b for b in image)


def render_asm(name):
    ops, banner = _prog(name)
    image = b"".join(b for _m, _c, b in ops) + banner
    out = [FIXTURES[name]["header"].rstrip("\n"), "", "; --- CODE (ORG 0100H) ---"]
    addr = ORG
    for mnem, comment, data in ops:
        line = "%04X  %-11s %-14s; %s" % (addr, listing(data), mnem, comment)
        assert len(line) <= 71, "listing line wider than 71 columns: %r" % line
        out.append(line)
        addr += len(data)
    for i in range(0, len(banner), 8):
        chunk = banner[i:i + 8]
        line = "%04X  %-23s %s" % (addr + i, listing(chunk),
                                   "DB " + ",".join("%02XH" % b for b in chunk))
        assert len(line) <= 71, "listing data line too wide: %r" % line
        out.append(line)
    out.append("; THE STRING IS $-TERMINATED; BDOS 9 STOPS AT THE '$'")
    out.append("")
    out.append("; --- COMPLETE IMAGE (%d BYTES), 16 PER LINE ---" % len(image))
    for i in range(0, len(image), 16):
        out.append("; BYTES(%03X): %s" % (i, listing(image[i:i + 16])))
    dig = hashlib.sha256(image).hexdigest()
    out.append("; SHA256: %s" % dig[:32])
    out.append(";         %s" % dig[32:])
    return "\n".join(out) + "\n"


BYTES_RE = re.compile(r"^; BYTES\([0-9A-F]{3}\): ((?:[0-9A-F]{2} ?)+)$", re.M)


def check_one(name):
    com = os.path.join(FIXTURE_DIR, "%s.COM" % name)
    asm = os.path.join(SPEC_DIR, "%s.asm" % name)
    image = build(name)
    problems = []
    if not os.path.isfile(asm):
        return ["missing listing %s" % os.path.relpath(asm, ROOT)]
    text = open(asm, encoding="ascii", errors="replace").read()
    got = " ".join(m.group(1).strip() for m in BYTES_RE.finditer(text))
    if got != listing(image):
        problems.append("listing BYTES lines differ from the emitted image")
    dig = hashlib.sha256(image).hexdigest()
    if (("; SHA256: %s" % dig[:32]) not in text) or ((";         %s" % dig[32:]) not in text):
        problems.append("listing SHA256 line differs from the emitted image")
    if not os.path.isfile(com):
        problems.append("missing artifact %s" % os.path.relpath(com, ROOT))
    elif open(com, "rb").read() != image:
        problems.append("artifact bytes differ from the emitted image")
    wide = max((len(l) for l in text.split("\n")), default=0)
    if wide > 71:
        problems.append("listing exceeds 71 columns (widest line %d)" % wide)
    if "\r" in text:
        problems.append("listing carries CR bytes (declared LF)")
    return problems


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--write", action="store_true", help="write .COM images and .asm listings")
    ap.add_argument("--check", action="store_true", help="verify artifacts and listings")
    ap.add_argument("--print-hashes", action="store_true")
    a = ap.parse_args(argv)
    rc = 0
    for name in sorted(FIXTURES):
        image = build(name)
        if a.write:
            os.makedirs(FIXTURE_DIR, exist_ok=True)
            with open(os.path.join(FIXTURE_DIR, "%s.COM" % name), "wb") as f:
                f.write(image)
            with open(os.path.join(SPEC_DIR, "%s.asm" % name), "w", newline="\n") as f:
                f.write(render_asm(name))
            print("%s: wrote .COM (%d bytes) and .asm listing" % (name, len(image)))
        if a.check:
            problems = check_one(name)
            print("%s: %s" % (name, "OK (listing+artifact+width match)" if not problems
                              else "MISMATCH: " + "; ".join(problems)))
            rc = 1 if problems else rc
        if a.print_hashes or a.write:
            print("%s  sha256=%s  (%d bytes)" % (name, hashlib.sha256(image).hexdigest(),
                                                 len(image)))
    return rc


if __name__ == "__main__":
    sys.exit(main())
