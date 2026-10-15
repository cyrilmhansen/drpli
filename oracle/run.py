#!/usr/bin/env python3
"""Minimal pty driver for z80pack cpmsim (no pexpect dependency).

Usage:
  run.py --disks DIR [--cpu -8] [--timeout 60] SCRIPT
SCRIPT is a file of lines; special directives:
  ##WAIT <regex>   wait for regex in stream (default also matches prompts)
  ##SEND <text>    send text without newline
  <text>           send text + \r
Every line typed is echoed to transcript as ">>> <line>".
Transcript (raw, ANSI stripped) goes to stdout.
Exit codes: 0 = last ##WAIT matched, 1 = timeout, 2 = sim died.
"""
import argparse, os, pty, re, select, signal, subprocess, sys, time

PROMPT = re.compile(rb"[A-P]>")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--disks", required=True)
    ap.add_argument("--cpu", default="-8")
    ap.add_argument("--sim", default=os.environ.get("CPMSIM",
        os.path.expanduser("~/pli/cpm/z80pack/cpmsim/cpmsim")))
    ap.add_argument("--timeout", type=float, default=60.0)
    ap.add_argument("--prompt-wait", type=float, default=2.0)
    ap.add_argument("script")
    a = ap.parse_args()

    master, slave = pty.openpty()
    import fcntl
    def pre():
        os.setsid()
        fcntl.ioctl(slave, 0x540E, 0)  # TIOCSCTTY: pty becomes ctty
    proc = subprocess.Popen([a.sim, a.cpu, "-d", a.disks]
                            + os.environ.get("CPMSIM_EXTRA", "").split(),
                            stdin=slave, stdout=slave, stderr=sys.stderr,
                            preexec_fn=pre)
    os.close(slave)
    buf = b""
    deadline = time.time() + a.timeout
    ok = True
    halting = False
    def read_until(pred):
        nonlocal buf, deadline
        while True:
            m = pred(buf)
            if m:
                return m
            if not proc.poll() is None:
                sys.exit(2)
            r, _, _ = select.select([master], [], [], 0.25)
            if r:
                try:
                    data = os.read(master, 65536)
                except OSError:
                    sys.exit(2)
                if not data:
                    sys.exit(2)
                buf += data
            if time.time() > deadline:
                return None

    shown = 0
    def show(n=None):
        nonlocal shown
        data = buf[shown:n] if n else buf[shown:]
        shown = len(buf) if n is None else max(shown, n)
        sys.stdout.write(data.decode("latin-1", "replace"))
        sys.stdout.flush()

    # wait for first prompt after boot
    buf = b""
    m = read_until(lambda b: PROMPT.search(b))
    if m is None:
        show(); print("\n!! boot timeout", file=sys.stderr); sys.exit(1)

    with open(a.script) as f:
        lines = [l.rstrip("\n") for l in f if l.strip()]
    for line in lines:
        if line == "##HALT":
            halting = True
            os.write(master, b"A:BYE\r")
            print("\n>>> A:BYE (halt)")
            # drain until sim exits
            halt_deadline = time.time() + 30
            while True:
                if proc.poll() is not None:
                    break
                if time.time() > halt_deadline:
                    print("!! halt timeout", file=sys.stderr)
                    break
                r, _, _ = select.select([master], [], [], 0.5)
                if r:
                    try:
                        d = os.read(master, 65536)
                    except OSError:
                        break
                    if not d:
                        break
                    buf += d
            show()
            break
        if line.startswith("##WAIT "):
            pat = re.compile(line[7:].encode("latin-1"))
            mark = len(buf)
            deadline = time.time() + a.timeout
            m = read_until(lambda b, p=pat, k=mark: p.search(b, k))
            show()
            if m is None:
                print(f"\n!! wait timeout: {pat}", file=sys.stderr)
                ok = False
                break
        elif line.startswith("##SEND "):
            os.write(master, line[7:].encode("latin-1"))
        else:
            # clear prompt tail so next read starts fresh
            os.write(master, (line + "\r").encode("latin-1"))
            print(f"\n>>> {line}")
            deadline = time.time() + a.timeout
            mark = len(buf)
            m = read_until(lambda b, k=mark: PROMPT.search(b, k)
                           or re.search(rb"STOP PL/I \(Y/N\)", b[k:]))
            # small extra window to catch late output
            r, _, _ = select.select([master], [], [], a.prompt_wait)
            if r:
                try: buf += os.read(master, 65536)
                except OSError: pass
            # answer compiler's STOP PL/I (Y/N)? prompt, if any
            for _ in range(3):
                if re.search(rb"STOP PL/I \(Y/N\)\?", buf[mark:]):
                    os.write(master, b"Y\r")
                    print("\n>>> [auto Y]")
                    deadline = time.time() + a.timeout
                    mark = len(buf)
                    m = read_until(lambda b, k=mark: PROMPT.search(b, k))
                    if m is None:
                        break
                else:
                    break
            show()
    proc.send_signal(signal.SIGTERM)
    try:
        proc.wait(5)
    except subprocess.TimeoutExpired:
        proc.kill()
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
