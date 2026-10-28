#!/usr/bin/env python3
"""E2E-42/P2b: DR's answers vs the predictions registered in HYPOTHESES.md.

Prints, per probe: the verdict, CODE and DATA against the prediction, the number of ?SIOOP /
?SYSPR / ?QIOOP, and DR's diagnostic where it refused.  Nothing here interprets -- it lines the
prediction up against the measurement.
"""
import pathlib, sys
HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))
from chaindump import instrs                       # noqa: E402

# (predicted CODE, predicted DATA or None, predicted ?SIOOP, predicted ?QIOOP)
PRED = {
 "E46M1": (115, 11, 1, 2), "E46M2": (96, 11, 2, 2), "E46M3": (137, 15, 1, 2),
 "E46M4": (103, 11, 1, 1), "E46M5": (132, None, 2, 2), "E46M6": (92, 10, 1, 1),
 "E46M7": (107, 51, 1, 2), "E46M8": (115, 33, 1, 2), "E46M9": (178, 44, 2, 4),
 "E46M10": (178, 32, 2, 4), "E46M11": (128, 34, 2, 2), "E46M12": (87, 25, 0, 2),
 "E46M13": (214, 15, 2, 4), "E46M14": (121, 32, 2, 2), "E46M15": (117, 50, 1, 1),
 "E46M16": (146, 26, 2, 3), "E46M17": (105, 32, 2, 2), "E46M18": (123, 50, 2, 2),
 "E46M19": (122, 121, 1, 1), "E46M20": (122, 121, 1, 1),
 "E46M21": (79, 34, 1, 1), "E46M22": (79, 36, 1, 1), "E46M23": (80, 32, 1, 1),
 "E46M24": (None, None, 1, 1), "E46M25": (None, None, 1, 1),
 "E46M26": (73, 34, 1, 1),
 "E46M27": (207, 63, 4, 5), "E46M28": (115, 20, 1, 2), "E46M29": (190, None, 2, 3),
 "E46M30": (130, 30, 1, 2), "E46M31": (226, None, 1, 2), "E46M32": (149, 71, 1, 2),
}
TAGS = ("e42p2b", "e42p2b2", "e42p2b3")


def find(n):
    for t in TAGS:
        d = pathlib.Path("golden") / t / n
        if (d / (n + ".PRN")).exists() or (d / (n + ".REL")).exists():
            return d
    return None


def diag(path):
    t = path.read_bytes().split(b"\x1a")[0].decode("latin1")
    for i in range(len(t)):
        if t[i:i + 4] in ("IKY0", "IKY1", "IFB ", "IFB.", "IFO "):
            return t[i:i + 76].replace("\r", " | ")
    return "(no 4-byte diagnostic block; last line:) " + \
           [l.rstrip() for l in t.split("\n") if l.strip(" \r\n\x0c")][-1][:60]


def eq(pred, got):
    if pred is None:
        return "  ?  "
    return " OK  " if pred == got else "FAIL "


for i in range(1, 33):
    n = f"E46M{i}"
    d = find(n)
    pc, pd, ps, pq = PRED[n]
    rel = d / (n + ".REL")
    if not rel.exists():
        print(f"{n}: DR REFUSED   pred CODE {pc}  ::  {diag(d / (n + '.PRN'))}")
        continue
    got, sizes = instrs(rel)
    sz = lambda k: (sizes.get(k)[1] if isinstance(sizes.get(k), tuple) else None)
    cs, ds = sz("DEF-CODE-SIZE"), sz("DEF-DATA-SIZE")
    cnt = lambda m: sum(1 for _, mn, op in got if mn == "call" and op == "?" + m)
    si, pr, qi = cnt("SIOOP"), cnt("SYSPR"), cnt("QIOOP")
    print(f"{n}: DR ACCEPTED  CODE {eq(pc, cs)}{cs:>4} (pred {pc})   "
          f"DATA {eq(pd, ds)}{ds:>4} (pred {pd})   "
          f"SIOOP {eq(ps, si)}{si}  SYSPR {pr}  QIOOP {eq(pq, qi)}{qi}")
