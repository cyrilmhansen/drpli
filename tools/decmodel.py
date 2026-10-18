#!/usr/bin/env python3
"""decmodel.py -- INDEPENDENT simulator of DR PL/I-80's FIXED DECIMAL stack.

Written from the laws measured on the R512 / R701-R725 $C traces and used in
two directions, neither of which reads compiler output:

  * SCHEDULE  the token sequence predicted here is compared against the
              tokens DR emitted in its own $C listing;
  * NUMBERS   the value predicted here is compared against DR's console
              output, and is also recomputable from exact Python Decimal
              arithmetic (the quotient is `trunc(m_l * 10**N / m_r)`).

Value model: a stack entry is (p, s, m) meaning value m / 10**s, m integer.
  QDDSL n : m *= 10**n, s += n    -- shifts the CURRENT TOP left, value kept
  QDDSR n : m //= 10**n, s -= n   -- shifts the TOP right, TRUNCATES low
                                    digits (proven by R706: 2/3 -> 0.66 and
                                    R703: 9/2 into dec(9,0) -> 4)
  DADOP/DSUOP/DMUOP/DDVOP : pop two, push one    DSTOP : pop into a cell

Laws (each cited in spec/notes/e2e7a-slice2-divide.md):
  + -      align the SHORTER operand UP to max(s_l,s_r); the shift is emitted
           BETWEEN the pushes when the first-pushed operand is the short one
           and AFTER both pushes when the second-pushed one is [R705, R707,
           R715 both directions, R723 compare]; p = min(15, min(p_l,p_r)+1)
           [R714 (9,9)->10, R717 (9,6)->7, R718 sub (5,5)->6]
  *        NO alignment; s = s_l + s_r [R711 `d = a*b` into dec(9,4) emits no
         shift at all]; p = min(15, p_l + p_r + 1) [R718 (5,5)->11; and via
         N=0 in LOAN1/R704 where 4+11+1 -> 15]
  /        pre-shift the DIVIDEND by N = 15 - p_dividend, and omit the whole
         pair when N = 0 [13 samples: R512, R701, R702, R703, R708, R709,
         R710 (p=11 -> N=4, so N is not a constant), R712, R713, R714, R716,
         R717, R718, LOAN1/R704 (product with p=15 -> N=0 -> no pair)];
         quotient s = s_l + N - s_r when N > 0, else s_l - s_r; the quotient's
         PRECISION is unpinned (no sample exposes it), so a quotient is never
         consumed where p is required.
  consumer  a store/return fixes the scale (UP = QDDSL, DOWN = QDDSR)
         [R701/R711/R713/R716]; an enclosing +/- aligns its own operands
         instead and adds no fix, so a quotient carries its scale straight in
         [R721, R722].
  literal   store/return role -> the TARGET (p,s) [C084]; additive or compare
         role -> the DEC PARTNER (p,s) [R608, R507]; multiplicative role ->
         own digit count, scale 0 [R509, R511, R512, R703, R710, LOAN1 1200].
  order     the RIGHT operand is pushed first iff it is compound and the left
         is simple [DFACT, R704, R719, R722]; left first otherwise, including
         both-compound [R720, R724] and both-simple [R505, R705, R707].
         DIVISION always pushes the dividend first [R712], because its N
         pre-shift has to act on the dividend while it is still the top.
"""
import os
import re
import sys
from decimal import Decimal, getcontext

getcontext().prec = 60


class V:
    __slots__ = ("p", "s", "m")

    def __init__(self, p, s, m):
        self.p, self.s, self.m = p, s, m

    @property
    def val(self):
        return Decimal(self.m) / Decimal(10) ** self.s

    def copy(self):
        return V(self.p, self.s, self.m)


def shift_l(v, n):
    return V(v.p, v.s + n, v.m * 10 ** n)


def shift_r(v, n):
    sign = -1 if v.m < 0 else 1
    return V(v.p, v.s - n, sign * (abs(v.m) // 10 ** n))


def div_trunc(a, b):
    sign = -1 if (a < 0) != (b < 0) else 1
    return sign * (abs(a) // abs(b))


def strip_paren(t):
    t = t.strip()
    while t.startswith("(") and t.endswith(")"):
        d, ok = 0, True
        for i, c in enumerate(t):
            if c == "(":
                d += 1
            elif c == ")":
                d -= 1
                if d == 0 and i != len(t) - 1:
                    ok = False
                    break
        if ok:
            t = t[1:-1].strip()
        else:
            break
    return t


def split_level(t, ops):
    """split at the RIGHTMOST top-level operator of a PRECEDENCE LEVEL
    (left-associative): `*` and `/` are one level, so `i * p / 1200` splits
    at the `/` -> (`i * p`, `1200`), NOT at the `*`."""
    depth = 0
    hits = []
    for i, c in enumerate(t):
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
        elif depth == 0 and c in ops and i > 0 and t[i - 1] not in "*/+-":
            hits.append((i, c))
    if not hits:
        return None
    i, c = hits[-1]
    return c, t[:i], t[i + 1:]


def split_top(t, op):
    r = split_level(t, op)
    return (r[1], r[2]) if r and r[0] == op else None


def parse_num(t):
    t = t.strip()
    if "." in t:
        w, f = t.split(".")
        return int((w + f) or "0"), len(f)
    return int(t), 0


def own_digits(t):
    return len(t.replace(".", "").lstrip("0") or "0")


def split_round(t):
    """`round(a, 2)' -> ('a', 2), else None.  [E2E-7A slice 3]"""
    t = strip_paren(t)
    if not re.match(r"round\s*\(", t, re.I):
        return None
    inner = t[t.index("(") + 1:t.rindex(")")]
    depth = 0
    for i, c in enumerate(inner):
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
        elif c == "," and depth == 0:
            a, b = inner[:i], inner[i + 1:]
            b = b.strip()
            if not re.fullmatch(r"\d+", b):
                raise AssertionError(
                    "decmodel: ROUND whose digit count is not a literal")
            return a.strip(), int(b)
    raise AssertionError("decmodel: one-argument ROUND (DR rejects it [R808])")


def is_compound(t):
    t = strip_paren(t)
    r = split_round(t)
    if r:
        # LOAN1/R807: a round whose ARGUMENT is compound behaves compound;
        # a simple-argument round in an operand position has no sample at all.
        return is_compound(r[0])
    return any(split_top(t, o) for o in "+-*/")


class Model:
    def __init__(self, src):
        self.decl, self.stmts, self.puts = {}, [], None
        self.puts_cond = False   # put reached only inside an IF arm
        src = src.replace("\r", "")
        cur = None
        for line in src.splitlines():
            s = line.strip()
            if re.match(r"\w+:\s*$", s):
                cur = "pre"
                continue
            if re.match(r"procedure options\(main\)", s):
                cur = "main"
                continue
            if re.match(r"\w+:\s*procedure options\(main\)", s):
                cur = "main"
                continue
            if re.match(r"procedure\s*\(", s) or re.match(r"\w+:\s*procedure", s):
                cur = "proc"
                continue
            if cur != "main":
                continue
            m = re.match(r"dcl\s+(\w+)\s+fixed\s+dec\((\d+)\s*,\s*(\d+)\)", s)
            if m:
                self.decl[m.group(1)] = (int(m.group(2)), int(m.group(3)))
                continue
            m = re.match(r"dcl\s+(\w+)\s+fixed\b", s)
            if m:
                self.decl[m.group(1)] = None
                continue
            # several statements can share one source line (`p = 5; q = 3;`)
            for piece in s.split(";"):
                piece = piece.strip()
                if not piece:
                    continue
                m = re.match(r"(\w+)\s*=\s*(.+)$", piece)
                if m and m.group(1) in self.decl and "__cmp__" not in piece:
                    self.stmts.append((m.group(1), m.group(2)))
            if re.search(r"\b(if|while)\b", s):
                # condition text: between parens for WHILE, after IF ... THEN
                m = re.search(r"while\s*\(([^)]*)\)", s)
                if not m:
                    m = re.search(r"if\s*(.+?)\s+then", s)
                if m:
                    c = re.match(r"\s*(\S+)\s*(>=|<=|\^=|>|<|=)\s*(\S+)",
                                 m.group(1).strip())
                    if c:
                        self.stmts.append(("__cmp__",
                                           (c.group(2), c.group(1), c.group(3))))
                        # NO `continue` here: [R507] puts an IF arm on the
                        # same source line as its condition, and that arm's
                        # `put ... list(dec_var)` still pushes a ?DLDOP.
            m = re.match(r"put\s+(skip\s+)?list\((.*)\);", s)
            cond = False
            if not m:
                # [R507] `if d > 0 then put skip list(d);` -- a PUT inside an
                # IF arm still pushes its DEC items for printing, so the
                # schedule needs it; the printed VALUE does not, because a
                # false branch never prints.  Track the difference instead of
                # pretending the item is unconditional.
                m = re.search(r"then\s+put\s+(skip\s+)?list\((.*)\);", s)
                cond = bool(m)
            if m:
                self.puts = m.group(2)
                self.puts_cond = self.puts_cond or cond
        self.var = {k: V(ps[0], ps[1], 0)
                    for k, ps in self.decl.items() if ps}

    # -- operand descriptor without emitting, for the alignment/precision laws
    def probe(self, txt, role):
        t = strip_paren(txt)
        if t in self.var and self.decl.get(t):
            return self.decl[t]
        if re.fullmatch(r"[\d.]+", t):
            return None
        r_ = split_round(t) if re.match(r"round\s*\(", t, re.I) else None
        if r_:
            return self.probe(r_[0], role)
        if is_compound(t):
            return None
        return None

    def role_for(self, op, other, side):
        if op in "*/" or (op == "+" or op == "-") is False:
            return ("mul",)
        return ("add", self.probe(other, None))

    def ev(self, txt, role, log):
        t = strip_paren(txt)
        if t in self.var and self.decl.get(t):
            p, s = self.decl[t]
            log.append(("DLDOP", p))
            return V(p, s, self.var[t].m)
        if re.fullmatch(r"[\d.]+", t):
            m, ls = parse_num(t)
            if role[0] == "store":
                p, s = role[1]
            elif role[0] == "add":
                if role[1] is None:
                    raise AssertionError(
                        "additive/compare literal with an unknown DEC partner")
                if ls:
                    raise AssertionError("fractional additive literal unpinned")
                p, s = role[1]
            else:
                if ls:
                    raise AssertionError("fractional multiplicative literal")
                p, s = own_digits(t), 0
            if s < ls:
                raise AssertionError("literal scale exceeds the role scale")
            log.append(("DLDOP", p))
            return V(p, s, m * 10 ** (s - ls))
        r_ = split_round(t)
        if r_:
            inner, n = r_
            if role[0] == "mul":
                raise AssertionError(
                    "decmodel: ROUND in a multiplicative position (unpinned)")
            v = self.ev(inner, ("nop",), log)   # arg pushes with NO fix
            k = v.s - n
            assert k >= 0, "decmodel: ROUND n above entry scale"
            log.append(("DROUN", k))
            return self.consumer_fix(self.round_val(v, n), role, log)
        for level in ("+-", "*/"):             # lowest precedence first
            r = split_level(t, level)
            if r:
                op, lt, rt = r
                return self.ev_bin(op, lt, rt, role, log)
        raise AssertionError(f"decmodel: cannot evaluate {txt!r}")

    def consumer_fix(self, res, role, log):
        """L5: the CONSUMER decides the final scale of a computed value."""
        if role[0] == "store":
            tp, ts = role[1]
            if res.s < ts:
                log.append(("QDDSL", ts - res.s))
                res = shift_l(res, ts - res.s)
            elif res.s > ts:
                log.append(("QDDSR", res.s - ts))
                res = shift_r(res, res.s - ts)
        return res

    def round_val(self, v, n):
        """?DROUN: HALF-UP and AWAY FROM ZERO at n places, scale RETAINED.
        DR's runtime evidence [R802/R803/R806]: 2.125->2.13, 2.135->2.14,
        2.145->2.15, 2.155->2.16, -2.125->-2.13, 2.5->3.  Nothing here is
        assumed: HALF-EVEN would have given 2.12 / 2.14 / 2.14 / 2.16."""
        k = v.s - n
        assert k >= 0, "decmodel: ROUND n above the entry scale [R805 wrapped]"
        f = 10 ** k
        q, rem = divmod(abs(v.m), f)
        if 2 * rem >= f:
            q += 1
        return V(v.p, v.s, q * f * (1 if v.m >= 0 else -1))

    def ev_bin(self, op, l, r, role, log):
        rl = self.role_for(op, r, l)
        rr = self.role_for(op, l, r)
        dl = self.ev(l, rl, [])                  # descriptor: no emission
        dr = self.ev(r, rr, [])
        right_first = is_compound(r) and not is_compound(l) and op != "/"
        if op == "/":
            if dl.p is None:
                raise AssertionError("divide: dividend precision unpinned")
            n = 15 - dl.p
        if right_first:
            first_txt, first_role, first_v = r, rr, dr
            second_txt, second_role, second_v = l, rl, dl
        else:
            first_txt, first_role, first_v = l, rl, dl
            second_txt, second_role, second_v = r, rr, dr
        fv = self.ev(first_txt, first_role, log)
        # the pre-shift / alignment shift acting on the FIRST-pushed operand
        if op == "/":
            if n > 0:
                log.append(("QDDSL", n))
                fv = shift_l(fv, n)
        elif fv.s < second_v.s:
            log.append(("QDDSL", second_v.s - fv.s))
            fv = shift_l(fv, second_v.s - fv.s)
        sv = self.ev(second_txt, second_role, log)
        if op != "/" and sv.s < fv.s:
            log.append(("QDDSL", fv.s - sv.s))
            sv = shift_l(sv, fv.s - sv.s)
        if op == "+":
            log.append(("DADOP", None))
            res = V(min(15, min(fv.p, sv.p) + 1) if None not in (fv.p, sv.p)
                    else None, max(fv.s, sv.s), fv.m + sv.m)
        elif op == "-":
            log.append(("DSUOP", None))
            lo, hi = (fv, sv) if not right_first else (sv, fv)
            res = V(min(15, min(fv.p, sv.p) + 1) if None not in (fv.p, sv.p)
                    else None, max(fv.s, sv.s), lo.m - hi.m)
        elif op == "*":
            log.append(("DMUOP", None))
            res = V(min(15, fv.p + sv.p + 1) if None not in (fv.p, sv.p)
                    else None, fv.s + sv.s, fv.m * sv.m)
        else:
            log.append(("DDVOP", None))
            if n > 0:
                s = fv.s - sv.s          # fv is already pre-shifted
                m = div_trunc(fv.m, sv.m)
            else:
                s = dl.s - dr.s
                m = div_trunc(dl.m, dr.m)
            if s < 0:
                raise AssertionError("divide: negative quotient scale")
            res = V(None, s, m)
        return self.consumer_fix(res, role, log)

    def run(self):
        log = []
        for name, rhs in self.stmts:
            if name == "__cmp__":
                # C085 relation push order (RIGHT first for > and <=) plus the
                # R723 alignment: DR shifts the SHORTER operand up, and the
                # only reachable shape is the one where the top is shorter.
                rop, l, r = rhs
                right_first = rop in (">", "<=")
                def side(t, other):
                    if t in self.var and self.decl.get(t):
                        return self.decl[t]
                    if re.fullmatch(r"[\d.]+", t):
                        # C085/R507: a compare literal is a DEC cell taking the
                        # DEC PARTNER's (p,s); only 0 or an integral literal is
                        # pinned, which is all these probes use.
                        ps = self.decl.get(other)
                        if ps is None:
                            raise AssertionError("compare literal without DEC partner")
                        return ps
                    raise AssertionError(f"compare operand {t!r} unpinned")
                dl, dr = side(l, r), side(r, l)
                order = [(r, dr), (l, dl)] if right_first else [(l, dl), (r, dr)]
                for nm, (p, sc) in order:
                    log.append(("DLDOP", p))
                # order[0] is pushed FIRST (the deeper value), order[1] LAST
                # (the top of the stack, which is what QDDSL can reach)
                deep, top = order[0][1][1], order[1][1][1]
                if top < deep:
                    log.append(("QDDSL", deep - top))
                elif deep < top:
                    raise AssertionError("compare: deeper operand is the short one")
                log.append(("DCMOP", None))
                continue
            ps = self.decl.get(name)
            if not ps:
                continue
            v = self.ev(rhs, ("store", ps), log)
            self.var[name] = V(ps[0], ps[1], v.m)
            log.append(("DSTOP", ps[0]))
        return log


def dr_tokens(prn_path):
    out, pend = [], None
    for line in open(prn_path, errors="replace").read().replace("\r", "").splitlines():
        m = re.match(r"\s+[0-9A-F]{4}\s+MVI\s+A,([0-9A-F]{2})\s*$", line)
        if m:
            pend = int(m.group(1), 16)
            continue
        m = re.match(
            r"\s+[0-9A-F]{4}\s+CALL \?(DLDOP|DSTOP|DADOP|DSUOP|DMUOP|DDVOP|QDDSL|QDDSR|DCMOP|DROUN|IROUN)\b",
            line)
        if m:
            out.append((m.group(1), pend))
            pend = None
            continue
        pend = None
    return out


def fmt(tokens):
    return " ".join(f"{a}{'' if b is None else ':' + str(b)}" for a, b in tokens)


def expected_put_line(mdl):
    """Returns None for a conditional PUT (an IF arm may not execute)."""
    if getattr(mdl, "puts_cond", False):
        return None
    """DR's PUT LIST edit: each item is right-justified in width p+3 with s
    fractional digits, and ONE BLANK separates items (evidenced byte-exactly
    by R706/R711/R715/R718/R724 console transcripts)."""
    if not mdl.puts:
        return None
    out = []
    for it in mdl.puts.split(","):
        t = strip_paren(it)
        if t in mdl.var and mdl.decl.get(t):
            p, s_ = mdl.decl[t]
            v = Decimal(mdl.var[t].m) / Decimal(10) ** s_
            out.append(f"{v:{p + 3}.{s_}f}")
        else:
            return None          # binary / string item: not modelled
    return " ".join(out)


def main():
    paths = sys.argv[1:]
    bad = 0
    for path in paths:
        src = open(path, errors="replace").read()
        try:
            mdl = Model(src)
            log = mdl.run()
        except AssertionError as ex:
            print(f"{os.path.basename(path):8s} MODEL-REFUSED: {ex}")
            continue
        name = os.path.basename(path).split(".")[0]
        prn = None
        for tag in ("e2e9", "e2e8", "e2e7", "e2e6"):
            cand = f"golden/{tag}/{name}/{name}.PRN"
            if os.path.exists(cand):
                prn = cand
                break
        # the PUT LIST items that are DEC variables push themselves
        if mdl.puts:
            for item in mdl.puts.split(","):
                t = strip_paren(item)
                if t in mdl.var and mdl.decl.get(t):
                    log.append(("DLDOP", mdl.decl[t][0]))
        mine = [(a, b) for a, b in log]
        vals = " ".join(f"{k}={Decimal(v.m)/Decimal(10)**v.s:.{v.s}f}"
                        for k, v in mdl.var.items() if mdl.decl.get(k))
        sched = "no-PRN"
        if prn:
            dr = dr_tokens(prn)
            sched = "MATCH" if dr == mine else "DIFFER"
            if sched == "DIFFER":
                bad += 1
                print("   mine:", fmt(mine))
                print("   DR  :", fmt(dr))
        # numeric cross-check against a captured console transcript
        num = "no-transcript"
        exp = expected_put_line(mdl)
        for tagdir in ("e2e9run", "e2e8run", "e2erundr", "e2e7run", "e2e6run"):
            c = f"golden/{tagdir}/{name}.output.txt"
            if exp is not None and os.path.exists(c) and os.path.getsize(c):
                raw = open(c, errors="replace").read().replace("\r\n", "\n")
                lines = [l for l in raw.split("\n") if l.strip()]
                num = "VALUE-MATCH" if lines and lines[-1] == exp else "VALUE-DIFF"
                if num == "VALUE-DIFF":
                    bad += 1
                    print(f"   model : {exp!r}\n   DR    : {lines[-1]!r}")
                break
        print(f"{name}: SCHED {sched}  NUM {num}  {vals}")
    return bad


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
