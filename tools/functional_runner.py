#!/usr/bin/env python3
"""functional_runner.py -- E2E-50/P2 step 5: the functional test harness.

THE LAW IS `spec/functional/tests/README.md` (schema `pli80-functional/1`).  This file is its
mechanical reading; where the two disagree the README wins and this file is the defect.  Every
rule below cites the section it implements.  Nothing here invents a DR behaviour: verdicts come
from executed, lane-labelled evidence only (PROTOCOL #4).

What it does, per spec and per lane (README section 8 stage chain):

    SOURCE -> DERIVATION -> COMPILE -> LINK -> RUN -> ASSERT

  * SOURCE (section 3, 5.1): the spec's own integrity -- schema validation FAIL-CLOSED (an
    unknown field at ANY level is an error, `null` is never legal for a required field), the
    source sha256 verified BEFORE any execution, the declared encoding form verified, and for
    Lane A the pinned artifact hash.  Hash mismatch is a SOURCE FAIL with attribution `source`;
    a missing file is BLOCKED with attribution `host` (section 8/9).
  * DERIVATION (L3, section 4): the reference script is run in its OWN process and must
    reproduce `expected`; spec/reference drift is a FAIL with attribution `source`, and no lane
    executes after it -- a stale spec can never pass.
  * COMPILE (Lane B only): the local `pli80c.exe` on the spec's source.  Success evidence is
    rc=0 AND a non-empty .REL; a refusal is attributed from its OWN message text (measured
    shapes: `Failure("codegen: ... [TBD]")` = `compiler`; `Pli80.Parser.Parse_error` = `source`).
  * LINK (Lane B only, L2): the historical LINK-80 + PLILIB.IRL under cpmsim through the
    `oracle/cpmwork.py` Workspace safety machinery.  "A .COM appeared" is NEVER success: the
    FULL transcript segment is parsed with `oracle/linkrun.py:parse_undefined` (never a [:120]
    display slice -- section 2 L2) and a non-empty undefined list is a FAIL.
  * RUN: lane-labelled.  Lane B uses the measured `oracle/linkrun.py` session law (prompt-sync
    `##WAIT`, default console input one ^Z) and records WHICH termination witness class it saw
    (`oracle/run.py` exit-code law, [C308]: timeout / sim-died / done are DIFFERENT facts and
    are never collapsed).  Lane A uses the audited `pli80-run` with --trace and --max-steps;
    README section 9 rule 1: its stdout is evidence ONLY at exit 0 because the runner discards
    the buffered program output on every error path (docs/emulator-audit.md 2.18).
  * ASSERT (section 4): the COMPLETE normalized console stream -- `collapse-spaces-v1` is the
    gate's own law verbatim (tools/e2e_gate.py:5632), the line sequence must match with no extra
    and no missing line, a single trailing empty element is ignored (the measured E32B1
    final-\\n), and `!text` entries assert absence.  `exact` mode compares raw bytes.

Verdict law (section 8): PASS only when EVERY APPLICABLE stage ran and produced typed success
evidence and ASSERT matched.  A skipped, unrun, blocked or unclassified stage is NEVER a PASS --
UNKNOWN and BLOCKED are first-class and are never laundered (section 11).  Attribution
(section 9) is admissible only from a typed signal and is NEVER narrowed by reasoning: this
harness has no discriminating run in v1, so an assertion mismatch carries `undefined` even
though `runtime-lib` is the plausible story (docs/functional-testing.md section 7: the runtime
BDOS census of a LINK-80'd image is UNMEASURED).

Redistribution (docs/emulator-audit.md sections 6-7): this file is Package-A material (project
original).  It never copies, bundles or commits a DR binary, a CP/M system image or any lab
code; every restricted path is supplied at invocation and recorded by hash.

usage:
  python3 tools/functional_runner.py                       # all specs, all lanes
  python3 tools/functional_runner.py --tests TABLE-00      # one test
  python3 tools/functional_runner.py --stages SOURCE,DERIVATION,COMPILE   # bounded smoke
  python3 tools/functional_runner.py --double-run          # determinism proof (audit 2.20)

exit code: 0 iff every attempted lane verdict is PASS; 1 otherwise; 2 = harness usage error.
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SCHEMA_TAG = "pli80-functional/1"
RESULT_SCHEMA = "pli80-functional-result/1"
STAGES = ("SOURCE", "DERIVATION", "COMPILE", "LINK", "RUN", "ASSERT")
VERDICTS = ("PASS", "FAIL", "BLOCKED", "UNKNOWN")
ATTRIBUTIONS = ("source", "compiler", "runtime-lib", "emulator", "host", "undefined")

SPEC_DIR_DEFAULT = os.path.join(ROOT, "spec", "functional", "tests")
COVERAGE_TSV = os.path.join(ROOT, "spec", "COVERAGE.tsv")
CC_DEFAULT = os.path.join(ROOT, "ocaml", "_build", "default", "bin", "pli80c.exe")
ARTEFACTS_DEFAULT = os.path.join(ROOT, "artefacts")
SEEDS_DEFAULT = os.path.join(ROOT, "oracle", "disks")
EVIDENCE_ROOT_DEFAULT = os.path.join(ROOT, "build", "functional")

# [E2E-50/P2 step 7] The Lane A emulator fallback, MEASURED paths only (docs/emulator-audit.md,
# step 6 RESULTS section 0: the hop-5 fallback named a dune PUBLIC name that `dune build' does
# not produce -- FALSIFIED; the built executable is bin/main.exe, and the install-directory name
# carries no extension).  Pinned by tools/test_functional_runner.py C14a.
LANE_A_CANDIDATES = ("/home/john/pli/lab/_build/default/bin/main.exe",
                     "/home/john/pli/lab/_build/install/default/bin/pli80-run")

# README section 7 -- forbidden by name in v1.
FORBIDDEN_CAPS = ("AGG.MULTIDIM", "EXPR.K_PLUS_X", "LOOP.TRAVERSAL_RELOAD")
# README section 7 -- the same perimeter expressed as COVERAGE status: a row my compiler
# REFUSED/DIVERGENT, or whose DR status is UNTESTED, cannot carry a v1 functional assertion.
DISALLOWED_MINE = ("REFUSED", "DIVERGENT")
DISALLOWED_DR = ("UNTESTED",)

ID_RE = re.compile(r"^[A-Z][A-Z0-9-]*$")
HEX64_RE = re.compile(r"^[0-9a-f]{64}$")
NAME83_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]{0,7}$")
MODULE_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

DERIVATION_TIMEOUT_S = 30          # pure stdlib computation; not a limits field (section 3)
WALLCLOCK_GRACE_S = 30             # subprocess guard beyond the harness-level timeout

# oracle/run.py documents its exit codes at the top of itself (0 = last ##WAIT matched,
# 1 = timeout, 2 = sim died); oracle/linkrun.py:run_status names them and [C308] forbids
# collapsing them.  `wall-clock-timeout' is this harness's own witness: the pty driver itself
# failed to terminate within limits.*_timeout_s + grace.
TERMINATION_WITNESS = {0: "done", 1: "timeout", 2: "sim-died"}
WALLCLOCK_RC = -1

# README section 3/4 field tables -- the fail-closed universe of legal keys.
TOP_REQUIRED = ("spec", "id", "family", "title", "provenance", "source",
                "capabilities", "limits", "lanes", "expected")
TOP_ALLOWED = TOP_REQUIRED + ("console_input", "notes")
PROV_REQUIRED = ("origin", "author", "date", "note")
PROV_ALLOWED = PROV_REQUIRED
ORIGINS = ("original", "historical-dr", "third-party")
SRC_REQUIRED = ("file", "sha256", "encoding")
SRC_ALLOWED = SRC_REQUIRED
LIMITS_REQUIRED = ("compile_timeout_s", "link_timeout_s", "run_timeout_s", "run_max_steps")
LIMITS_ALLOWED = LIMITS_REQUIRED
EXP_REQUIRED = ("derivation", "normalization")
EXP_ALLOWED = EXP_REQUIRED + ("console", "raw", "file_expectations")
NORMALIZATIONS = ("collapse-spaces-v1", "exact")
LANE_KEYS = ("lane", "substrate", "toolchain", "artifact", "artifact_sha256", "link_targets")
LANES = ("A", "B")
# README section 8: Lane A fixtures declare COMPILE/LINK not-applicable IN ADVANCE -- here that
# declaration is the lane-entry shape itself (a pinned artifact, no compiler, no link_targets).
LANE_A_REQUIRED = ("lane", "substrate", "toolchain", "artifact", "artifact_sha256")
LANE_B_REQUIRED = ("lane", "substrate", "toolchain", "link_targets")
DEFAULT_CONSOLE_INPUT = "^Z"       # oracle/linkrun.py DEFAULT_INPUT convention (section 3)


# --------------------------------------------------------------------------- small utilities
def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def read_coverage_ids(path=COVERAGE_TSV):
    """{id: (dr_status, mine_status)} from the canonical ledger (read-only)."""
    out = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            fields = line.rstrip("\n").split("\t")
            if fields[0] == "id":
                continue
            if len(fields) > 7:
                out[fields[0]] = (fields[6], fields[7])
    return out


def normalize_v1(raw):
    """collapse-spaces-v1 (README section 4, gate law quoted verbatim at tools/e2e_gate.py:5632)."""
    return re.sub(rb" +", b" ", raw.replace(b"\r\n", b"\n"))


def split_stream(norm_text):
    """Complete-stream line sequence; ONE trailing empty element is ignored (the measured
    E32B1 unconditional final \\n -- README section 4)."""
    lines = norm_text.split("\n")
    if lines and lines[-1] == "":
        lines = lines[:-1]
    return lines


def _is_str(v):
    return isinstance(v, str) and v != ""


def _is_pos_int(v):
    return isinstance(v, int) and not isinstance(v, bool) and v > 0


# --------------------------------------------------------------------------- schema validation
def validate_spec(obj, *, basename, coverage):
    """Fail-closed schema check (README section 3).  Returns a list of problem strings; empty
    means the spec is valid.  An unknown field at ANY level is a problem: a silently ignored
    typo must never downgrade or upgrade a verdict."""
    P = []
    if not isinstance(obj, dict):
        return ["spec JSON is not an object"]
    for k in sorted(set(obj) - set(TOP_ALLOWED)):
        P.append("unknown top-level field %r (fail-closed: README section 3)" % k)
    for f in TOP_REQUIRED:
        if f not in obj:
            P.append("missing required field %r" % f)
        elif obj[f] is None:
            P.append("null is not legal for required field %r" % f)
    if obj.get("spec") not in (None, SCHEMA_TAG):
        P.append("schema tag %r is not %r" % (obj.get("spec"), SCHEMA_TAG))
    tid = obj.get("id")
    if _is_str(tid):
        if not ID_RE.match(tid):
            P.append("id %r does not match ^[A-Z][A-Z0-9-]*$" % tid)
        if tid != basename:
            P.append("id %r must equal the spec basename %r" % (tid, basename))
    for f in ("family", "title"):
        if f in obj and not _is_str(obj[f]):
            P.append("%s must be a non-empty string" % f)

    # provenance (section 5.1)
    prov = obj.get("provenance")
    if isinstance(prov, dict):
        for k in sorted(set(prov) - set(PROV_ALLOWED)):
            P.append("unknown provenance field %r" % k)
        for f in PROV_REQUIRED:
            if f not in prov or prov[f] is None:
                P.append("provenance.%s is required" % f)
        if _is_str(prov.get("origin")) and prov["origin"] not in ORIGINS:
            P.append("provenance.origin %r not in %s" % (prov["origin"], list(ORIGINS)))
    elif prov is not None:
        P.append("provenance must be an object")

    # source (section 3)
    src = obj.get("source")
    if isinstance(src, dict):
        for k in sorted(set(src) - set(SRC_ALLOWED)):
            P.append("unknown source field %r" % k)
        for f in SRC_REQUIRED:
            if f not in src or src[f] is None:
                P.append("source.%s is required" % f)
        if _is_str(src.get("sha256")) and not HEX64_RE.match(src["sha256"]):
            P.append("source.sha256 is not 64 lowercase hex")
        if _is_str(src.get("file")) and _bad_relpath(src["file"]):
            P.append("source.file %r must be a relative path inside the spec dir" % src["file"])
    elif src is not None:
        P.append("source must be an object")

    # capabilities (sections 3 + 7)
    caps = obj.get("capabilities")
    # [E2E-50/P2 step 6 AMENDMENT] A Lane-A-ONLY substrate fixture is hand-encoded assembly:
    # it exercises NO PL/I construct, so the capability perimeter (section 7) has nothing to
    # validate and the empty array is legal THERE.  The law is unchanged for every spec with a
    # lane B (or both lanes) -- fail closed.  (Old text: `if not caps: P.append("capabilities
    # must be a non-empty array")', kept as written per PROTOCOL #2.)
    lane_labels = [l.get("lane") for l in (obj.get("lanes") or []) if isinstance(l, dict)]
    lane_a_only = bool(lane_labels) and all(l == "A" for l in lane_labels)
    if isinstance(caps, list):
        if not caps and not lane_a_only:
            P.append("capabilities must be a non-empty array (empty is legal ONLY for a "
                     "Lane-A-only substrate fixture -- README section 3 amendment)")
        for c in caps:
            if not _is_str(c):
                P.append("capabilities entries must be strings")
            elif c not in coverage:
                P.append("capability %r does not exist in spec/COVERAGE.tsv" % c)
            elif c in FORBIDDEN_CAPS:
                P.append("capability %r is forbidden in v1 (README section 7)" % c)
            else:
                dr, mine = coverage[c]
                if mine in DISALLOWED_MINE:
                    P.append("capability %r has mine_status %s -- a refused/divergent row "
                             "carries no v1 assertion (README section 7)" % (c, mine))
                if dr in DISALLOWED_DR:
                    P.append("capability %r has dr_status %s -- UNTESTED rows carry no v1 "
                             "assertion (README section 7)" % (c, dr))
    elif caps is not None:
        P.append("capabilities must be an array")

    # limits (section 3)
    lim = obj.get("limits")
    if isinstance(lim, dict):
        for k in sorted(set(lim) - set(LIMITS_ALLOWED)):
            P.append("unknown limits field %r" % k)
        for f in LIMITS_REQUIRED:
            if f not in lim or lim[f] is None:
                P.append("limits.%s is required" % f)
            elif not _is_pos_int(lim[f]):
                P.append("limits.%s must be a positive integer" % f)
    elif lim is not None:
        P.append("limits must be an object")

    # console_input (section 3)
    ci = obj.get("console_input", DEFAULT_CONSOLE_INPUT)
    if not _is_str(ci):
        P.append("console_input must be a non-empty string when present")

    # lanes (section 5.2)
    lanes = obj.get("lanes")
    seen_lanes = set()
    if isinstance(lanes, list):
        if not lanes:
            P.append("lanes must be a non-empty array")
        for ln in lanes:
            if not isinstance(ln, dict):
                P.append("each lane entry must be an object")
                continue
            for k in sorted(set(ln) - set(LANE_KEYS)):
                P.append("unknown lane field %r" % k)
            lab = ln.get("lane")
            if lab not in LANES:
                P.append("lane %r is not A or B" % (lab,))
                continue
            if lab in seen_lanes:
                P.append("duplicate lane %r in one spec" % lab)
            seen_lanes.add(lab)
            for f in (LANE_A_REQUIRED if lab == "A" else LANE_B_REQUIRED):
                if f not in ln or ln[f] is None:
                    P.append("lane %s: %s is required" % (lab, f))
            for f in ("substrate", "toolchain"):
                if f in ln and not _is_str(ln[f]):
                    P.append("lane %s: %s must be a non-empty string" % (lab, f))
            if lab == "A":
                if "link_targets" in ln:
                    P.append("lane A: link_targets is illegal -- COMPILE/LINK are declared "
                             "not-applicable by the lane shape (README section 8)")
                if _is_str(ln.get("artifact")) and _bad_relpath(ln["artifact"]):
                    P.append("lane A: artifact %r must be a repo-relative path" % ln["artifact"])
                if _is_str(ln.get("artifact_sha256")) and not HEX64_RE.match(ln["artifact_sha256"]):
                    P.append("lane A: artifact_sha256 is not 64 lowercase hex")
                if ci != DEFAULT_CONSOLE_INPUT:
                    P.append("lane A: console_input %r is a substrate claim the audit refutes "
                             "(docs/emulator-audit.md 2.12: no console input exists)" % (ci,))
            else:
                if "artifact" in ln or "artifact_sha256" in ln:
                    P.append("lane B: artifact fields are illegal -- the .COM is produced, "
                             "not pinned (README section 5.2)")
                tgt = ln.get("link_targets")
                if isinstance(tgt, list):
                    if len(tgt) != 1:
                        # Schema-level corollary: `source` pins ONE hashed file, so v1 cannot
                        # derive expectations for a multi-module link.
                        P.append("lane B: v1 supports exactly one link_target (a single hashed "
                                 "source); got %r" % (tgt,))
                    for t in tgt:
                        if not _is_str(t) or not NAME83_RE.match(t):
                            P.append("lane B: link_target %r is not a CP/M 8.3 name" % (t,))
                elif tgt is not None:
                    P.append("lane B: link_targets must be an array")
    elif lanes is not None:
        P.append("lanes must be an array")

    # expected (section 4)
    exp = obj.get("expected")
    if isinstance(exp, dict):
        for k in sorted(set(exp) - set(EXP_ALLOWED)):
            P.append("unknown expected field %r" % k)
        for f in EXP_REQUIRED:
            if f not in exp or exp[f] is None:
                P.append("expected.%s is required" % f)
        norm = exp.get("normalization")
        if _is_str(norm) and norm not in NORMALIZATIONS:
            P.append("expected.normalization %r not in %s" % (norm, list(NORMALIZATIONS)))
        d = exp.get("derivation")
        if _is_str(d):
            script, sep, func = d.partition(":")
            if not sep or not script or not func:
                P.append("expected.derivation %r must be '<script>:<function>'" % d)
            else:
                if _bad_relpath(script):
                    P.append("expected.derivation script %r must live in the spec dir" % script)
                elif not script.endswith(".py"):
                    P.append("expected.derivation script %r is not a .py file" % script)
                elif not MODULE_RE.match(os.path.basename(script)[:-3]):
                    P.append("expected.derivation script %r is not an importable module" % script)
                if not MODULE_RE.match(func):
                    P.append("expected.derivation function %r is not an identifier" % func)
        console = exp.get("console")
        raw = exp.get("raw")
        if norm == "exact":
            if console is not None:
                P.append("expected.console is illegal under 'exact' (raw replaces it -- "
                         "README section 4)")
            if not isinstance(raw, str) or raw == "":
                P.append("normalization 'exact' requires a non-empty expected.raw byte string")
        else:
            if raw is not None:
                P.append("expected.raw is legal only under normalization 'exact'")
            if not isinstance(console, list) or not console:
                # README section 4: an empty expected list is NOT an assertion; the gate's
                # empty-expected-matches-everything trap (tools/e2e_gate.py:5628-5636).
                P.append("expected.console must be a non-empty array (an empty expected list "
                         "matches every transcript and is never an assertion)")
            else:
                for e in console:
                    if not _is_str(e):
                        P.append("expected.console entries must be non-empty strings")
        fe = exp.get("file_expectations")
        if fe not in (None, [], {}):
            P.append("expected.file_expectations is declared in README section 3 but is NOT "
                     "implemented by the v1 harness; it must be absent or empty (never "
                     "silently ignored)")
    elif exp is not None:
        P.append("expected must be an object")
    return P


def _bad_relpath(p):
    return os.path.isabs(p) or ".." in p.split("/") or p == ""


# --------------------------------------------------------------------------- stage records
@dataclass
class Stage:
    name: str
    status: str                       # pass|fail|blocked|unknown|not-applicable|unrun
    attribution: str = ""             # ATTRIBUTIONS, only on fail/blocked/unknown
    witness: str = ""                 # the typed signal that produced this status
    detail: str = ""
    evidence: list = field(default_factory=list)

    def as_dict(self):
        d = {"stage": self.name, "status": self.status, "witness": self.witness,
             "detail": self.detail, "evidence": self.evidence}
        if self.attribution:
            d["attribution"] = self.attribution
        return d


def verdict_of(stages):
    """README section 8.  PASS only when every APPLICABLE stage is `pass`; a not-applicable
    stage (declared by the spec, in advance) neither helps nor hurts.  The first stage that is
    not a typed success decides the verdict; a stage that never ran is missing evidence and is
    therefore UNKNOWN -- never a PASS, in any direction (PROTOCOL #4 by analogy)."""
    for st in stages:
        if st.status == "pass" or st.status == "not-applicable":
            continue
        if st.status == "fail":
            return "FAIL", st
        if st.status == "blocked":
            return "BLOCKED", st
        return "UNKNOWN", st          # unknown | unrun
    return "PASS", None


def render_line(test_id, lane, verdict, attribution, stop_stage):
    """The ONE rendering law.  There is no formatting path by which anything but PASS prints
    'PASS'; BLOCKED/UNKNOWN survive verbatim (README section 11)."""
    extra = ""
    if stop_stage is not None:
        extra = "  [%s: %s%s]" % (stop_stage.name, stop_stage.witness or stop_stage.status,
                                  " -- " + stop_stage.detail if stop_stage.detail else "")
    return "  %-10s lane %s  %-7s%s%s" % (test_id, lane, verdict,
                                          ("  attr=" + attribution) if attribution else "",
                                          extra)


# --------------------------------------------------------------------------- the host substrate
class Host:
    """Everything external, in one place, so the hostile tests can inject their own world.

    No restricted asset is ever copied or bundled: DR tools, cpmsim and `pli80-run' are resolved
    from paths supplied at invocation and recorded by hash."""

    def __init__(self, *, compiler=CC_DEFAULT, pli80_run=None, cpmsim=None,
                 artefacts=ARTEFACTS_DEFAULT, seeds=SEEDS_DEFAULT,
                 subprocess_run=subprocess.run, sim_session=None, git_head=None,
                 link_deps=None, workspace_factory=None, run_factory=None):
        self.compiler = compiler
        self._pli80_run = pli80_run
        self._cpmsim = cpmsim
        self.artefacts = artefacts
        self.seeds = seeds
        self.subprocess_run = subprocess_run
        self.sim_session = sim_session or self.default_sim_session
        self._git_head = git_head
        self._link_deps = link_deps
        self.workspace_factory = workspace_factory or _default_workspace_factory
        self.run_factory = run_factory or _default_run_factory

    # -- dependency resolution (section 8: BLOCKED names what is missing) ------------------
    def missing(self, path):
        return (not path) or (not os.path.isfile(path)) or os.path.islink(path)

    def pli80_run_path(self):
        if self._pli80_run:
            return self._pli80_run
        env = os.environ.get("PLI80_RUN")
        if env:
            return env
        # The audited lab build output (READ-ONLY external tree; never built by this harness).
        # Both measured locations are offered, freshest first (see LANE_A_CANDIDATES).
        for cand in LANE_A_CANDIDATES:
            if os.path.isfile(cand):
                return cand
        return ""

    def cpmsim_path(self):
        if self._cpmsim:
            return self._cpmsim
        env = os.environ.get("CPMSIM")
        if env:
            return env
        cand = os.path.join(ROOT, "thirdparty", "z80pack", "cpmsim", "cpmsim")
        if os.path.exists(cand):
            return cand
        return os.path.expanduser("~/pli/cpm/z80pack/cpmsim/cpmsim")

    def dr_tools(self):
        """oracle/linkrun.py TOOLS -- user-supplied, never packaged, never committed."""
        return [os.path.join(self.artefacts, t) for t in
                ("LINK.COM", "LIB.COM", "RMAC.COM", "PLILIB.IRL")]

    def boot_seeds(self):
        return [os.path.join(self.seeds, s) for s in ("drivea.dsk", "driveb.dsk")]

    def link_deps(self):
        """README section 8: BLOCKED must NAME what is missing."""
        return self._link_deps if self._link_deps is not None else _default_link_deps(self)

    def make_workspace(self, root, seeds):
        return self.workspace_factory(root, seeds)

    def make_run(self, ws, tag):
        return self.run_factory(ws, tag)

    def identities(self, used):
        """README section 11: host substrate identities recorded with the verdict."""
        ids = {"python": sys.version.split()[0], "harness": "tools/functional_runner.py",
               "harness_schema": RESULT_SCHEMA}
        for label, path in used.items():
            if path and os.path.isfile(path):
                ids[label] = {"path": os.path.relpath(path, ROOT), "sha256": sha256_file(path)}
            else:
                ids[label] = {"path": path or "", "sha256": None}
        return ids

    def git_head(self):
        if self._git_head is not None:
            return self._git_head
        try:
            r = self.subprocess_run(["git", "-C", ROOT, "rev-parse", "HEAD"],
                                    capture_output=True, text=True, timeout=20)
            return r.stdout.strip() if r.returncode == 0 else ""
        except Exception:
            return ""

    # -- the external calls ---------------------------------------------------------------
    def run_argv(self, argv, *, timeout, cwd=None, env=None):
        """Returns (rc, stdout_bytes, stderr_bytes, witness).  witness is a [C308] class name:
        `exited' / `timeout' (wall clock) / `launch-failed' (no such tool)."""
        try:
            r = self.subprocess_run(argv, shell=False, capture_output=True, cwd=cwd, env=env,
                                    timeout=timeout + WALLCLOCK_GRACE_S)
            return r.returncode, r.stdout, r.stderr, "exited"
        except subprocess.TimeoutExpired:
            return WALLCLOCK_RC, b"", b"", "wall-clock-timeout"
        except FileNotFoundError:
            return WALLCLOCK_RC, b"", ("no such executable: %s" % argv[0]).encode(), "launch-failed"
        except OSError as e:
            return WALLCLOCK_RC, b"", str(e).encode(), "launch-failed"

    def default_sim_session(self, run, script_lines, timeout, name, evidence):
        """The measured oracle/linkrun.py:session law (prompt-sync, ANSI strip, CPMSIM_EXTRA=-u)
        writing its transcript to the harness evidence dir instead of a golden dir, plus a
        wall-clock guard that run.py itself does not provide."""
        script = os.path.join(run.dir, "%s.session.txt" % name)
        with open(script, "w") as f:
            f.write("\n".join(script_lines) + "\n")
        env = dict(os.environ)
        env["CPMSIM"] = self.cpmsim_path()
        env["CPMSIM_EXTRA"] = "-u"
        argv = [sys.executable, os.path.join(ROOT, "oracle", "run.py"),
                "--disks", run.disks, "--timeout", str(timeout), script]
        rc, out, err, witness = self.run_argv(argv, timeout=timeout, cwd=os.path.join(ROOT, "oracle"),
                                              env=env)
        if witness != "exited":
            self.write_evidence(evidence, "%s.raw-transcript.txt" % name, out or b"",
                                binary=False)
            self.write_evidence(evidence, "%s.stderr.txt" % name, err or b"", binary=False)
            return rc, ""
        tr = re.sub(r"\x1b\[[0-9;]*[a-zA-Z]", "", out.decode("latin-1", "replace"))
        p = self.write_evidence(evidence, "%s.raw-transcript.txt" % name, tr, binary=False)
        return rc, tr

    @staticmethod
    def write_evidence(evidence, name, data, binary=True):
        path = os.path.join(evidence, name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        mode = "wb" if isinstance(data, (bytes, bytearray)) else "w"
        with open(path, mode) as f:
            f.write(data)
        return os.path.relpath(path, ROOT)


# --------------------------------------------------------------------------- lane context
@dataclass
class LaneCtx:
    test_id: str
    lane_entry: dict
    spec: dict
    spec_dir: str
    evidence: str                    # per-(test,lane) evidence dir (absolute)
    host: Host
    stage_ceiling: set
    console_input: str
    rel_path: str = ""               # compiled object (absolute)
    com_path: str = ""               # linked .COM in the evidence dir (absolute)
    console_raw: bytes = None        # the captured console stream (RUN)
    run_witness: str = ""
    run_seq: int = 1     # 2 during the determinism double-run

    @property
    def lane(self):
        return self.lane_entry["lane"]

    def applicable(self, stage):
        if stage in ("SOURCE", "DERIVATION", "ASSERT"):
            return True
        if self.lane == "A":
            return False             # declared not-applicable by the lane shape, in advance
        return True

    def attempted(self, stage):
        return (not self.stage_ceiling) or (stage in self.stage_ceiling)

    def src_path(self):
        return os.path.join(self.spec_dir, self.spec["source"]["file"])


# --------------------------------------------------------------------------- stages
def stage_source(ctx):
    """README section 3/5: integrity of the spec's own inputs, verified BEFORE any execution."""
    ev = []
    src = ctx.src_path()
    decl = ctx.spec["source"]
    if _bad_relpath(decl["file"]) or not os.path.isfile(src):
        return Stage("SOURCE", "blocked", "host", "source-file-missing",
                     "source file not found: %s" % os.path.relpath(src, ROOT), ev)
    got = sha256_file(src)
    if got != decl["sha256"]:
        return Stage("SOURCE", "fail", "source", "sha256-mismatch",
                     "source %s: sha256 %s != spec %s" % (decl["file"], got, decl["sha256"]), ev)
    raw = open(src, "rb").read()
    ev.append(ctx.host.write_evidence(ctx.evidence, "SOURCE.sha256.txt",
                                      "%s  %s\n" % (got, decl["file"]), binary=False))
    bad = check_encoding(raw, decl["encoding"])
    if bad:
        return Stage("SOURCE", "fail", "source", "encoding-mismatch", bad, ev)
    if ctx.lane == "A":
        art = os.path.join(ROOT, ctx.lane_entry["artifact"])
        if not os.path.isfile(art):
            return Stage("SOURCE", "blocked", "host", "artifact-missing",
                         "lane A artifact not found: %s" % ctx.lane_entry["artifact"], ev)
        agot = sha256_file(art)
        if agot != ctx.lane_entry["artifact_sha256"]:
            return Stage("SOURCE", "fail", "source", "artifact-sha256-mismatch",
                         "artifact %s: sha256 %s != spec %s"
                         % (ctx.lane_entry["artifact"], agot, ctx.lane_entry["artifact_sha256"]),
                         ev)
        ev.append(ctx.host.write_evidence(ctx.evidence, "SOURCE.artifact-sha256.txt",
                                          "%s  %s\n" % (agot, ctx.lane_entry["artifact"]),
                                          binary=False))
    return Stage("SOURCE", "pass", "", "sha256+encoding verified",
                 "%s (%d bytes)" % (decl["file"], len(raw)), ev)


def check_encoding(raw, decl):
    """Verify every recognizable token of the declared encoding form (README section 2
    convention).  A declaration with no checkable token is an error -- fail closed."""
    body = raw[:-1] if raw.endswith(b"\x1a") else raw
    checks = 0
    if "CRLF" in decl:
        checks += 1
        for i, byte in enumerate(body):
            if byte == 0x0A and (i == 0 or body[i - 1] != 0x0D):
                return "declared CRLF but found a bare LF at byte %d" % i
    if "LF" in decl and "CRLF" not in decl:
        checks += 1
        if b"\r" in body:
            return "declared LF but found CR bytes"
    if "^Z" in decl:
        checks += 1
        if not raw.endswith(b"\x1a"):
            return "declared ^Z-terminated but the last byte is 0x%02X" % (raw[-1] if raw else 0)
    m = re.search(r"<=\s*(\d+)\s*col", decl)
    if m:
        checks += 1
        limit = int(m.group(1))
        lines = body.replace(b"\r\n", b"\n").split(b"\n")
        widest = max((len(l) for l in lines), default=0)
        if widest > limit:
            return "declared <=%d columns but the widest line is %d" % (limit, widest)
    if "ASCII" in decl:
        checks += 1
        if any(b >= 0x80 for b in body):
            return "declared ASCII but the file carries high bytes"
    if not checks:
        return ("encoding form %r declares no checkable convention (CRLF/LF/^Z/<=N columns/ASCII)"
                % decl)
    return ""


def stage_derivation(ctx):
    """L3 / README section 4 (a): the reference is run in its OWN process and must reproduce the
    spec.  Drift is a spec FAIL with attribution `source`; no lane stage may run after it."""
    exp = ctx.spec["expected"]
    script, _, func = exp["derivation"].partition(":")
    script_path = os.path.normpath(os.path.join(ctx.spec_dir, script))
    if not os.path.isfile(script_path):
        return Stage("DERIVATION", "blocked", "host", "reference-missing",
                     "reference script not found: %s" % os.path.relpath(script_path, ROOT))
    module = os.path.basename(script_path)[:-3]
    code = ("import json,sys; sys.path.insert(0, sys.argv[1]); import %s as m; "
            "sys.stdout.write(json.dumps(m.derive(sys.argv[2])))" % module)
    rc, out, err, witness = ctx.host.run_argv(
        [sys.executable, "-c", code, ctx.spec_dir, func], timeout=DERIVATION_TIMEOUT_S)
    if witness == "launch-failed":
        return Stage("DERIVATION", "blocked", "host", "python-launch-failed", err.decode()[:200])
    if witness == "wall-clock-timeout":
        return Stage("DERIVATION", "fail", "undefined", "timeout",
                     "derivation exceeded %ds (wall clock)" % DERIVATION_TIMEOUT_S)
    if rc != 0:
        p = ctx.host.write_evidence(ctx.evidence, "DERIVATION.traceback.txt", err, binary=False)
        return Stage("DERIVATION", "fail", "source", "derivation-error",
                     "reference.py raised (rc=%d): %s" % (rc, err.decode("utf-8", "replace")[-200:]),
                     [p])
    try:
        derived = json.loads(out.decode("utf-8"))
        assert isinstance(derived, list) and all(isinstance(x, str) for x in derived)
    except Exception as e:
        return Stage("DERIVATION", "fail", "source", "malformed-derivation",
                     "derivation returned non-conforming data: %r (%s)" % (out[:120], e))
    ctx.host.write_evidence(ctx.evidence, "DERIVATION.lines.txt",
                            "\n".join(derived) + "\n", binary=False)
    if exp.get("normalization") == "exact":
        want = "\n".join(derived) + "\n"
        if want != exp["raw"]:
            return Stage("DERIVATION", "fail", "source", "spec/reference drift (exact)",
                         "derived bytes differ from expected.raw",
                         [ctx.host.write_evidence(ctx.evidence, "DERIVATION.drift.txt",
                                                  "derived:\n%s\n--- spec:\n%s\n" % (want, exp["raw"]),
                                                  binary=False)])
        return Stage("DERIVATION", "pass", "", "derivation == expected.raw")
    if derived != exp["console"]:
        return Stage("DERIVATION", "fail", "source", "spec/reference drift",
                     "derive(%r) != expected.console" % func,
                     [ctx.host.write_evidence(ctx.evidence, "DERIVATION.drift.txt",
                                              "derived:\n%s\n--- spec:\n%s\n"
                                              % ("\n".join(derived), "\n".join(exp["console"])),
                                              binary=False)])
    return Stage("DERIVATION", "pass", "", "derivation == spec",
                 [os.path.join(ctx.evidence, "DERIVATION.lines.txt")])


def stage_compile(ctx):
    if not ctx.applicable("COMPILE"):
        return Stage("COMPILE", "not-applicable", "", "declared by the spec (lane A fixture)")
    if not ctx.attempted("COMPILE"):
        return Stage("COMPILE", "unrun", "", "stage ceiling")
    cc = ctx.host.compiler
    if ctx.host.missing(cc):
        return Stage("COMPILE", "blocked", "host", "compiler-missing",
                     "compiler not found (user-supplied): %s" % cc)
    out_rel = os.path.join(ctx.evidence, "%s.REL" % ctx.lane_entry["link_targets"][0])
    argv = [cc, "-d", ctx.src_path(), out_rel]
    timeout = ctx.spec["limits"]["compile_timeout_s"]
    rc, out, err, witness = ctx.host.run_argv(argv, timeout=timeout)
    errtxt = err.decode("utf-8", "replace")
    p_err = ctx.host.write_evidence(ctx.evidence, "COMPILE.stderr.txt", errtxt, binary=False)
    if witness == "wall-clock-timeout":
        # README section 8: a timeout is a FAIL and the WITNESS CLASS is recorded ([C308]).
        return Stage("COMPILE", "fail", "undefined", "timeout",
                     "compile exceeded compile_timeout_s=%d" % timeout, [p_err])
    if witness == "launch-failed":
        return Stage("COMPILE", "blocked", "host", "compiler-launch-failed", errtxt[:200], [p_err])
    if rc == 0:
        if not os.path.isfile(out_rel):
            return Stage("COMPILE", "unknown", "undefined", "rc=0 with no object",
                         "compiler exited 0 but wrote no .REL", [p_err])
        size = os.path.getsize(out_rel)
        if size == 0:
            return Stage("COMPILE", "unknown", "undefined", "empty object",
                         "compiler wrote a zero-byte .REL", [p_err])
        ctx.rel_path = out_rel
        sha = sha256_file(out_rel)
        p = ctx.host.write_evidence(ctx.evidence, "COMPILE.object.sha256.txt",
                                    "%s  %s  (%d bytes)\n" % (sha, os.path.basename(out_rel), size),
                                    binary=False)
        m = re.search(r"CODE=(\d+) DATA=(\d+) ITEMS=(\d+) -> (\d+) bytes", errtxt)
        dims = "code=%s data=%s items=%s bytes=%s" % m.groups() if m else "sizes unreported"
        return Stage("COMPILE", "pass", "", "rc=0, non-empty .REL", dims, [out_rel, p])
    # A compile-stage failure: attribute from the message's OWN typed shape (README section 9).
    attr = classify_compile_message(errtxt)
    if attr == "host":
        return Stage("COMPILE", "blocked", "host", "unreadable file", errtxt.strip()[:200], [p_err])
    return Stage("COMPILE", "fail", attr, "refusal rc=%d" % rc,
                 "compiler message recorded verbatim: %s" % errtxt.strip()[:200], [p_err])


def classify_compile_message(msg):
    """Typed-signal classifier (README section 9).  The shapes are MEASURED against the local
    binary (2026-11-02):
      `Fatal error: exception Failure("codegen: ...")'  -> my compiler's own named-stage refusal
      `Fatal error: exception Pli80.Parser.Parse_error' -> a diagnostic naming the source construct
      `Fatal error: exception Sys_error(...)'           -> the host, not the program
    Anything else has no typed origin and stays `undefined'."""
    if "Sys_error" in msg:
        return "host"
    if "Pli80.Parser" in msg or "Pli80.Lexer" in msg or "Pli80.Bind" in msg:
        return "source"
    if re.search(r'exception Failure\("(lexer|parser|bind|codegen|rel80)[: ]', msg):
        return "compiler"
    return "undefined"


def _oracle():
    sys.path.insert(0, os.path.join(ROOT, "oracle"))
    import cpmwork, linkrun
    return cpmwork, linkrun


def _default_link_deps(host):
    """The real Lane B census: DR tools + cpmsim + boot seeds + cpmtools + harness import."""
    missing = []
    for p in host.dr_tools():
        if host.missing(p):
            missing.append("DR tool %s (user-supplied, never packaged)" % p)
    if host.missing(host.cpmsim_path()):
        missing.append("cpmsim binary %s" % host.cpmsim_path())
    for p in host.boot_seeds():
        if host.missing(p):
            missing.append("boot seed %s" % p)
    try:
        cpmwork, _lr = _oracle()
    except Exception as e:
        missing.append("oracle harness import failed: %s" % e)
        return missing
    for name in ("mkfs.cpm", "cpmcp"):
        p2 = cpmwork.TOOLS.get(name)
        if not p2 or not os.path.isfile(p2) or not os.access(p2, os.X_OK):
            missing.append("cpmtools %s (%s)" % (name, p2))
    return missing


def _default_workspace_factory(root, seeds):
    cpmwork, _ = _oracle()
    return cpmwork.Workspace(root, seeds)


def _default_run_factory(ws, tag):
    _, linkrun = _oracle()
    return linkrun.new_run(ws, tag)


def stage_link(ctx):
    """README L2 (section 1/2): LINK-80 + PLILIB.IRL under cpmsim through the oracle Workspace
    machinery.  Success is the FULL transcript parsed and EMPTY of undefined symbols plus a
    real, non-empty exported .COM.  A .COM appearing is never success."""
    if not ctx.applicable("LINK"):
        return Stage("LINK", "not-applicable", "", "declared by the spec (lane A fixture)")
    if not ctx.attempted("LINK"):
        return Stage("LINK", "unrun", "", "stage ceiling")
    missing = ctx.host.link_deps()
    if missing:
        return Stage("LINK", "blocked", "host", "dependencies-absent", "; ".join(missing))
    cpmwork, linkrun = _oracle()
    target = ctx.lane_entry["link_targets"][0]
    try:
        ws = ctx.host.make_workspace(os.path.join(ctx.evidence, "workspace"), ctx.host.seeds)
        run = ctx.host.make_run(ws, "funclink-%s" % ctx.test_id)
    except cpmwork.SafetyError as e:
        return Stage("LINK", "blocked", "host", "workspace-refused", str(e))
    try:
        run.mkfs("c")
        run.mkfs("d")
        for t in linkrun.TOOLS:
            p = os.path.join(ctx.host.artefacts, t)
            if os.path.exists(p):
                run.import_local("c", p, t)
        run.import_local("d", ctx.rel_path, "%s.REL" % target)
        lines = ["C:", "LINK D:%s" % target, "##HALT"]
        timeout = ctx.spec["limits"]["link_timeout_s"]
        rc, tr = ctx.host.sim_session(run, lines, timeout, "link", ctx.evidence)
        ev = [os.path.join(ctx.evidence, "link.raw-transcript.txt")]
        if rc == WALLCLOCK_RC:
            return Stage("LINK", "fail", "undefined", "wall-clock-timeout",
                         "the pty driver itself did not terminate (link_timeout_s=%d)" % timeout, ev)
        witness = TERMINATION_WITNESS.get(rc, "unknown-rc-%d" % rc)
        seg = re.search(r">>> LINK D:%s(.*?)(?=>>> |\Z)" % re.escape(target), tr, re.S)
        if not seg:
            # L2 corollary: never TRUNCATE the transcript -- the parse input is the FULL
            # segment, and an absent segment is unclassifiable evidence, not a clean link.
            return Stage("LINK", "unknown", "undefined", "no-link-segment",
                         "transcript carries no '>>> LINK D:%s' segment (rc=%d, witness=%s)"
                         % (target, rc, witness), ev)
        full = re.sub(r"\r+\n", "\n", seg.group(1))          # FULL segment, never [:120]
        ev.append(ctx.host.write_evidence(ctx.evidence, "link.segment.txt", full, binary=False))
        undef = linkrun.parse_undefined(full)
        if undef:
            # The [C137] trap: LINK still writes a .COM.  Typed evidence names the symbols.
            return Stage("LINK", "fail", "undefined", "undefined-symbols:%s" % ",".join(undef),
                         "a .COM appearing is not the test [C137]", ev)
        if witness != "done":
            # [C308]: timeout and sim-death are DIFFERENT facts; both are failures of this stage.
            attr = "emulator" if witness == "sim-died" else "undefined"
            return Stage("LINK", "fail", attr, witness,
                         "link session ended on witness %s (rc=%d)" % (witness, rc), ev)
        com = os.path.join(ctx.evidence, "%s.COM" % target)
        got = run.export("d", "%s.COM" % target, ctx.evidence)
        if not got or not os.path.isfile(com) or os.path.getsize(com) == 0:
            return Stage("LINK", "unknown", "undefined", "no-com",
                         "no undefined symbols but no usable .COM either (export=%s)" % got, ev)
        ctx.com_path = com
        sha = sha256_file(com)
        ev.append(ctx.host.write_evidence(ctx.evidence, "link.com.sha256.txt",
                                          "%s  %s.COM  (%d bytes)\n" % (sha, target,
                                                                        os.path.getsize(com)),
                                          binary=False))
        return Stage("LINK", "pass", "", "done, parse_undefined=[]",
                     "%s.COM %d bytes sha256=%s" % (target, os.path.getsize(com), sha[:16]), ev)
    except cpmwork.SafetyError as e:
        return Stage("LINK", "blocked", "host", "safety-refused", str(e))
    except Exception as e:                                  # never launder: unknown
        return Stage("LINK", "unknown", "undefined", "harness-exception",
                     "%s: %s" % (type(e).__name__, e))
    finally:
        try:
            run.cleanup()
        except Exception:
            pass


def _send_input(console_input):
    """Spec console_input -> one ##SEND payload.  run.py unicode_escape-decodes what follows
    ##SEND, so ^Z becomes the \x1a spelling the oracle DEFAULT_INPUT table uses, newlines
    become \r, and literal backslashes are escaped (README section 3)."""
    txt = console_input.replace("^Z", "\x1a")
    out = []
    for c in txt:
        if c == "\\":
            out.append("\\\\")
        elif c in ("\n", "\r"):
            out.append("\\r")
        elif c == "\x1a":
            out.append("\\x1a")
        else:
            out.append(c)
    return "".join(out)


def stage_run(ctx):
    """RUN records WHICH termination witness it saw ([C308]); exit 0 is NEVER correctness (L2)."""
    if not ctx.attempted("RUN"):
        return Stage("RUN", "unrun", "", "stage ceiling")
    if ctx.lane == "A":
        return _run_lane_a(ctx)
    return _run_lane_b(ctx)


# Typed runner-error classes of the audited emulator (docs/emulator-audit.md 2.7-2.19,
# lib/runner + lib/cpm error names).  `emulator' attribution is admissible ONLY from one of
# these strings appearing on the runner's own stderr (README section 9).
LANE_A_TYPED_ERRORS = (
    ("unsupported BDOS function", "unsupported-bdos-function"),
    ("program too large", "program-too-large"),
    ("file error", "file-error"),
    ("invalid command tail", "invalid-command-tail"),
    ("unterminated string", "unterminated-string"),
    ("step limit", "step-limit"),
    ("max steps", "step-limit"),
    ("halted", "cpu-halted"),
    ("load error", "load-error"),
)


def _rname(ctx, base):
    """Evidence basename within the per-lane dir: `run' on the first execution, `run2' on the
    determinism double-run (ctx.run_seq = 2).  The second capture must never overwrite the
    first -- rerun_lane compares the two console captures byte-for-byte, so BOTH have to
    survive on disk.  [Defect fixed at hop 4: the name was referenced 7 times by step-5 part 1
    but never defined -- every attempted Lane A RUN raised NameError (lane B caught it and
    reported harness-exception/UNKNOWN; lane A crashed the runner).  Measured by
    tools/test_functional_runner.py, which exercises both lanes.]"""
    return base if ctx.run_seq <= 1 else "%s%d" % (base, ctx.run_seq)


def _run_lane_a(ctx):
    exe = ctx.host.pli80_run_path()
    if ctx.host.missing(exe):
        return Stage("RUN", "blocked", "host", "emulator-absent",
                     "pli80-run not supplied (user-supplied binary; set --pli80-run or PLI80_RUN); "
                     "the audited lab is READ-ONLY and is never built by this harness")
    art = os.path.join(ROOT, ctx.lane_entry["artifact"])
    trace = os.path.join(ctx.evidence, _rname(ctx, "run") + ".trace.txt")
    argv = [exe, "--trace", trace, "--max-steps", str(ctx.spec["limits"]["run_max_steps"]), art]
    timeout = ctx.spec["limits"]["run_timeout_s"]
    rc, out, err, witness = ctx.host.run_argv(argv, timeout=timeout)
    ev = []
    p_err = ctx.host.write_evidence(ctx.evidence, _rname(ctx, "run") + ".stderr.txt", err,
                                    binary=False)
    ev.append(p_err)
    if os.path.isfile(trace):
        ev.append(os.path.relpath(trace, ROOT))
    if witness == "wall-clock-timeout":
        return Stage("RUN", "fail", "undefined", "timeout",
                     "run exceeded run_timeout_s=%d (wall clock)" % timeout, ev)
    if witness == "launch-failed":
        return Stage("RUN", "blocked", "host", "emulator-launch-failed", err.decode()[:200], ev)
    # README section 9 rule 1: stdout is evidence ONLY at exit 0 -- the runner DISCARDS the
    # buffered program output on every error path (audit 2.18).  Failure-side evidence is the
    # trace file plus stderr, never partial stdout.
    if rc != 0:
        cls = next((c for pat, c in LANE_A_TYPED_ERRORS if pat in err.decode("latin-1", "lower")),
                   "")
        ctx.host.write_evidence(ctx.evidence, _rname(ctx, "run") + ".discarded-stdout.bin",
                                out or b"")
        detail = ("runner exit %d; buffered program output DISCARDED by the emulator "
                  "(audit 2.18) -- stdout is not evidence on this path" % rc)
        if rc == 1 and cls:
            return Stage("RUN", "fail", "emulator", cls, detail,
                         ev + [ctx.host.write_evidence(ctx.evidence, "run.stderr.txt",
                                                       err, binary=False)])
        return Stage("RUN", "unknown", "undefined", "unclassified runner exit %d" % rc, detail, ev)
    ctx.console_raw = out
    ctx.run_witness = "exit-0"
    p = ctx.host.write_evidence(ctx.evidence, _rname(ctx, "run") + ".console.bin", out or b"")
    return Stage("RUN", "pass", "", "exit-0 (termination witness)",
                 "%d stdout bytes (valid: exit 0 only)" % len(out or b""), [p])


def _run_lane_b(ctx):
    missing = ctx.host.link_deps()
    if missing:
        return Stage("RUN", "blocked", "host", "dependencies-absent", "; ".join(missing))
    cpmwork, linkrun = _oracle()
    target = ctx.lane_entry["link_targets"][0]
    try:
        ws = ctx.host.make_workspace(os.path.join(ctx.evidence, "workspace"), ctx.host.seeds)
        run = ctx.host.make_run(ws, "funcrun-%s" % ctx.test_id)
    except cpmwork.SafetyError as e:
        return Stage("RUN", "blocked", "host", "workspace-refused", str(e))
    try:
        run.mkfs("c")
        run.mkfs("d")
        run.import_local("d", ctx.com_path, "%s.COM" % target)
        # The measured prompt-sync law (oracle/linkrun.py:468 -- a stale 'D>' echo can satisfy a
        # later ##WAIT and abort the program before it printed anything): send CR, wait for the
        # FRESH prompt, then invoke.
        lines = ["C:", "D:", "##SEND \\r", "##WAIT \\nD>", "##SEND %s\\r" % target,
                 "##SEND %s" % _send_input(ctx.console_input),
                 "##WAIT \\nD>", "##HALT"]
        timeout = ctx.spec["limits"]["run_timeout_s"]
        rc, tr = ctx.host.sim_session(run, lines, timeout, _rname(ctx, "run"), ctx.evidence)
        ev = [os.path.join(ctx.evidence, _rname(ctx, "run") + ".raw-transcript.txt")]
        if rc == WALLCLOCK_RC:
            return Stage("RUN", "fail", "undefined", "wall-clock-timeout",
                         "the pty driver itself did not terminate (run_timeout_s=%d)" % timeout, ev)
        witness = TERMINATION_WITNESS.get(rc, "unknown-rc-%d" % rc)
        clean = re.sub(r">>> [^\n]*\n", "", tr)
        # FS-01 anchor law (the F1 fix).  The E2E-50/P2 cut `(?=\nD>|...)' consumed the LF of
        # the program's FINAL CRLF into the prompt anchor and stranded a lone CR in the capture
        # (step6/RESULTS.md section 2, F1; od-verified in the FS-01 baseline: the real
        # transcript carries ONE guest-written `\r\n' between program end and prompt,
        # `...LAST= 5\r\nD>').  The region now runs to the first terminator (prompt / `I/O ran'
        # / end of transcript) WITHOUT eating a preceding newline: the program's final newline
        # is retained and the prompt is still never captured.  Fail-closed counterpart: a
        # region whose terminator is NOT preceded by a newline is an ambiguous cut (program end
        # and transcript end are no longer separable) -> UNKNOWN, never PASS; the suspect
        # capture is still written as evidence.  The normalization/split/complete-stream laws
        # are untouched -- extra, missing or wrapped lines still FAIL the assertion.
        seg = re.search(r"%s[^\n]*\r\r\n(.*?)(?=D>|I/O ran|\Z)" % re.escape(target), clean, re.S)
        if seg is None:
            return Stage("RUN", "unknown", "undefined", "no-console-anchor",
                         "transcript carries no console region for %s (rc=%d witness=%s)"
                         % (target, rc, witness), ev)
        cap = seg.group(1)
        if not cap.endswith("\n"):
            p_bad = ctx.host.write_evidence(
                ctx.evidence, _rname(ctx, "run") + ".console.ambiguous.bin",
                cap.encode("latin-1", "replace"))
            return Stage("RUN", "unknown", "undefined", "console-terminator-ambiguous",
                         "console region (%d bytes) ends WITHOUT a newline before its terminator "
                         "(transcript tail %r): the program's final newline was never witnessed "
                         "-- refusing to guess (FS-01 anchor law)"
                         % (len(cap), clean[seg.end():seg.end() + 12]), ev + [p_bad])
        ctx.console_raw = cap.encode("latin-1", "replace")
        ctx.run_witness = witness
        p = ctx.host.write_evidence(ctx.evidence, _rname(ctx, "run") + ".console.bin", ctx.console_raw)
        if witness == "timeout":
            # [C308]: a program that ran on and on; NOT an emulator death, and NOT a result.
            return Stage("RUN", "fail", "undefined", "timeout",
                         "run ended on the timeout witness (rc=1); execution was never observed "
                         "to end [C205]", [p])
        if witness == "sim-died":
            return Stage("RUN", "fail", "emulator", "sim-died",
                         "cpmsim EXITED before the session finished (rc=2) -- an emulator/boot "
                         "failure, not a program that ran on forever [C308]", [p])
        if witness != "done":
            return Stage("RUN", "unknown", "undefined", witness, "unclassified witness rc=%d" % rc,
                         [p])
        # L2: the prompt came back.  That is a TERMINATION WITNESS, never correctness --
        # correctness is decided by ASSERT alone.
        return Stage("RUN", "pass", "", "done (prompt returned; L2: not correctness)",
                     "%d console bytes" % len(ctx.console_raw), [p])
    except cpmwork.SafetyError as e:
        return Stage("RUN", "blocked", "host", "safety-refused", str(e))
    except Exception as e:
        return Stage("RUN", "unknown", "undefined", "harness-exception",
                     "%s: %s" % (type(e).__name__, e))
    finally:
        try:
            run.cleanup()
        except Exception:
            pass


def assert_stream(ctx):
    """README section 4: the COMPLETE normalized stream.  Positive entries must equal the line
    sequence exactly (no extra, no missing line); `!text' entries assert absence from the stream."""
    exp = ctx.spec["expected"]
    if ctx.console_raw is None:
        return Stage("ASSERT", "unknown", "undefined", "no captured stream",
                     "RUN produced no console capture; an assertion cannot be evaluated on "
                     "missing evidence (never a verdict in either direction)")
    if exp.get("normalization") == "exact":
        p = ctx.host.write_evidence(ctx.evidence, "ASSERT.console.raw.bin", ctx.console_raw)
        if ctx.console_raw == exp["raw"].encode():
            return Stage("ASSERT", "pass", "", "exact bytes match",
                         "%d bytes" % len(ctx.console_raw), [p])
        return Stage("ASSERT", "fail", "undefined", "assert-mismatch (exact)",
                     "raw bytes differ from expected.raw (mine %d bytes, spec %d)"
                     % (len(ctx.console_raw), len(exp["raw"].encode())), [p])
    norm = normalize_v1(ctx.console_raw)
    text = norm.decode("ascii", "replace")
    got = split_stream(text)
    want = [e for e in exp["console"] if not e.startswith("!")]
    neg = [e[1:] for e in exp["console"] if e.startswith("!")]
    p_norm = ctx.host.write_evidence(ctx.evidence, "ASSERT.console.norm.txt", text, binary=False)
    missing = [n for n in neg if n in text]
    if got != want or missing:
        extra = got[len(want):]
        absent = want[len(got):]
        first_diff = next((i for i, (a, b) in enumerate(zip(got, want)) if a != b), None)
        # [hop-4 defect fix] the OLD code formatted `line %d differs (got[first_diff]...)' with
        # first_diff=None whenever the streams differed ONLY in length (a missing/extra line)
        # -- TypeError: list indices must be integers. Measured by
        # tools/test_functional_runner.py case C5 (ASSERT-SHORT / ASSERT-EXTRA).
        if missing:
            why = "forbidden-present:%s" % ",".join(missing)
        elif absent or extra:
            why = ("missing lines %r / extra lines %r" % (absent, extra))
        else:
            why = "line %d differs (got %r, want %r)" % (first_diff, got[first_diff], want[first_diff])
        # README section 9 rule 2: narrowing `undefined' -> `runtime-lib' needs a DISCRIMINATING
        # RUN; the v1 harness has none (the linked-program BDOS census is UNMEASURED,
        # docs/emulator-audit.md 4), so no reasoning may assign an origin here.
        return Stage("ASSERT", "fail", "undefined", "assert-mismatch",
                     "%s (got %r want %r) -- attribution stays undefined until a discriminating "
                     "run narrows it (README 9.2)" % (why, text, want), [p_norm])
    return Stage("ASSERT", "pass", "", "complete-stream match",
                 "%d line(s)%s" % (len(got), (" +%d negative(s)" % len(neg)) if neg else ""),
                 [p_norm])


# --------------------------------------------------------------------------- the runner
def run_lane(ctx):
    stages = []
    for fn in (stage_source, stage_derivation, stage_compile, stage_link, stage_run):
        st = fn(ctx)
        stages.append(st)
        if st.status not in ("pass", "not-applicable"):
            for rest in STAGES[STAGES.index(st.name) + 1:]:
                if ctx.applicable(rest):
                    stages.append(Stage(rest, "unrun", "", "chain stopped by %s" % st.name))
            verdict, stop = verdict_of(stages)
            return stages, verdict, stop
    st = assert_stream(ctx)
    stages.append(st)
    verdict, stop = verdict_of(stages)
    return stages, verdict, stop


def rerun_lane(ctx):
    """Determinism double-run (docs/emulator-audit.md 2.20): the chain has ALREADY executed
    RUN once -- that capture is the first run.  Re-execute RUN + ASSERT and compare the
    CONSOLE CAPTURE byte-for-byte.  The cpmsim transcript carries wall-clock text and is
    deliberately NOT the compared object (the repo gitignores those transcripts for exactly
    that reason).  Two runs of one input with different bytes = unclassifiable evidence:
    UNKNOWN, never PASS (README section 8)."""
    first = ctx.console_raw
    ctx.run_seq = 2
    ctx.console_raw = None
    st_run2 = stage_run(ctx)
    st_assert = (assert_stream(ctx) if st_run2.status == "pass" else
                 Stage("ASSERT", "unrun", "", "double-run: second RUN did not complete"))
    second = ctx.console_raw
    if st_run2.status != "pass":
        return [st_run2, st_assert], "second run failed: %s" % st_run2.witness
    if st_assert.status != "pass":
        return [st_run2, st_assert], "second run assert failed: %s" % st_assert.witness
    if first is None or second is None or first != second:
        return ([st_run2, st_assert], "double-run console capture differs: %d vs %d bytes"
                % (len(first or b""), len(second or b"")))
    return [st_run2, st_assert], ""


def run_test(spec_path, host, *, evidence_root, lanes=None, stage_ceiling=None,
             double_run=False, coverage=None):
    """Execute one spec (all lanes, or the named subset).  Returns a list of result records."""
    coverage = coverage if coverage is not None else read_coverage_ids()
    basename = os.path.splitext(os.path.basename(spec_path))[0]
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    test_id = basename
    tdir = os.path.join(evidence_root, "%s-%s" % (basename, stamp))
    try:
        with open(spec_path, encoding="utf-8") as f:
            obj = json.load(f)
    except (OSError, ValueError) as e:
        os.makedirs(tdir, exist_ok=True)
        return [_blocked_record(basename, None, "spec-unreadable", str(e), host, tdir)]
    problems = validate_spec(obj, basename=basename, coverage=coverage)
    test_id = obj.get("id") or basename
    tdir = os.path.join(evidence_root, "%s-%s" % (test_id, stamp))
    if problems:
        # Fail closed: a malformed spec is a SOURCE-stage FAIL with attribution `source'.
        # No lane executes, so no lane can be laundered into PASS.
        os.makedirs(tdir, exist_ok=True)
        p = host.write_evidence(tdir, "SPECERRORS.txt", "\n".join(problems) + "\n", binary=False)
        return [_record(
            test_id, None, "FAIL", "source", "SOURCE",
            [Stage("SOURCE", "fail", "source", "spec-validation",
                   "; ".join(problems), [p])], host, tdir, double_run=None)]
    os.makedirs(tdir, exist_ok=True)
    records = []
    for lane_entry in obj["lanes"]:
        if lanes and lane_entry["lane"] not in lanes:
            continue
        edir = os.path.join(tdir, "lane-%s" % lane_entry["lane"])
        os.makedirs(edir, exist_ok=True)
        ctx = LaneCtx(test_id=test_id, lane_entry=lane_entry, spec=obj,
                      spec_dir=os.path.dirname(spec_path), evidence=edir, host=host,
                      stage_ceiling=set(stage_ceiling or ()),
                      console_input=obj.get("console_input", DEFAULT_CONSOLE_INPUT))
        stages, verdict, stop = run_lane(ctx)
        dr = None
        if double_run and verdict == "PASS":
            dr_stages, dr_fail = rerun_lane(ctx)
            stages += dr_stages
            if dr_fail:
                # Two runs of one input disagree: the evidence cannot be classified (README 8).
                stages.append(Stage("RUN", "unknown", "undefined", "double-run-mismatch", dr_fail))
                verdict, stop = verdict_of(stages)
            dr = {"equal": not dr_fail, "compared": "console capture bytes (not transcript)"}
        records.append(_record(test_id, lane_entry, verdict,
                               stop.attribution if stop else "", stop.name if stop else "",
                               stages, host, edir, double_run=dr))
    return records


def _record(test_id, lane_entry, verdict, attribution, stop_stage, stages, host, edir,
            double_run=None):
    assert verdict in VERDICTS, "internal: verdict vocabulary is closed"
    rec = {
        "schema": RESULT_SCHEMA,
        "test_id": test_id,
        "verdict": verdict,
        "attribution": attribution or None,
        "stopped_at": stop_stage or None,
        "stages": [s.as_dict() for s in stages],
        "git_head": host.git_head(),
        "evidence_dir": os.path.relpath(edir, ROOT),
        "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "substrate_identity": host.identities({}),
    }
    if lane_entry is not None:
        rec["lane"] = lane_entry["lane"]
        rec["substrate"] = lane_entry["substrate"]
        rec["toolchain"] = lane_entry["toolchain"]
        rec["spec_schema"] = SCHEMA_TAG
        used = {}
        if lane_entry["lane"] == "A":
            used["pli80_run"] = host.pli80_run_path()
            used["artifact"] = os.path.join(ROOT, lane_entry.get("artifact", ""))
        else:
            used["compiler"] = host.compiler
            used["cpmsim"] = host.cpmsim_path()
            for t in host.dr_tools():
                used["dr:" + os.path.basename(t)] = t
            for s in host.boot_seeds():
                used["seed:" + os.path.basename(s)] = s
        rec["substrate_identity"] = host.identities(used)
        if lane_entry["lane"] == "B":
            rec["run_max_steps"] = {"declared": None,
                                    "note": "no step budget exists on cpmsim; wall-clock "
                                            "run_timeout_s governs (recorded honestly per README 3)"}
        if double_run is not None:
            rec["double_run"] = double_run
    assert rec["verdict"] != "PASS" or all(
        s["status"] in ("pass", "not-applicable") for s in rec["stages"]), \
        "internal: PASS requires every applicable stage to have run with typed success"
    return rec


def _blocked_record(basename, lane_entry, why, detail, host, tdir):
    return _record(basename, lane_entry, "BLOCKED", "host", "SOURCE",
                   [Stage("SOURCE", "blocked", "host", why, detail)], host, tdir)


# --------------------------------------------------------------------------- substrate probe
def parse_bdos_census(trace_text):
    """BDOS census from a Runes structured trace (`docs/emulator-audit.md` 2.17):
    `BDOS\t<step>\t<fn>\t<DE>` call events plus the `TERM\t<step>\tbdos:<n>` witness.
    Returns (ordered_call_list, counted_set, term_witness).  A trace with no BDOS events
    yields an EMPTY census -- absence of a witness is evidence of nothing (README 8)."""
    calls, term = [], None
    for line in trace_text.splitlines():
        f = line.split("\t")
        if len(f) >= 3 and f[0] == "BDOS":
            calls.append(int(f[2]))
        elif len(f) >= 3 and f[0] == "TERM" and f[2].startswith("bdos:"):
            term = int(f[2][5:])
    return calls, sorted(set(calls)), term


def bdos_census(host, com_path, evidence, max_steps, timeout=60):
    """MEASUREMENT of open question 1 (`docs/emulator-audit.md` 4 + 7.3): which BDOS
    functions a program actually calls on the audited emulator.  This is a SUBSTRATE PROBE,
    not a functional verdict: it never produces PASS/FAIL and never touches a spec lane.
    Artifacts produced by the historical toolchain (Lane B `.COM`) may be probed here, but the
    record must say so -- the image embeds PLILIB and is never distributable."""
    exe = host.pli80_run_path()
    rec = {"probe": "bdos-census", "emulator": exe, "artifact": com_path,
           "note": "substrate probe, NOT a lane verdict (README 11)"}
    if host.missing(exe):
        rec["status"] = "blocked"
        rec["why"] = "pli80-run absent (user-supplied; --pli80-run or PLI80_RUN)"
        return rec
    if host.missing(com_path):
        rec["status"] = "blocked"
        rec["why"] = "artifact absent: %s" % com_path
        return rec
    trace = os.path.join(evidence, "census.trace.txt")
    argv = [exe, "--trace", trace, "--max-steps", str(max_steps), com_path]
    rc, out, err, witness = host.run_argv(argv, timeout=timeout)
    rec.update(rc=rc, witness=witness, sha256=sha256_file(com_path),
               stdout_bytes=len(out or b""),
               stderr=(err or b"").decode("latin-1", "replace").strip()[:400])
    if witness != "exited":
        rec["status"] = "unknown"
        rec["why"] = "emulator process did not terminate normally (%s)" % witness
        return rec
    if not os.path.isfile(trace):
        rec["status"] = "unknown"
        rec["why"] = "no trace file: the census cannot be read from missing evidence"
        return rec
    calls, census, term = parse_bdos_census(open(trace, encoding="latin-1").read())
    rec.update(status="measured", calls=calls, census=census, term_witness=term,
               trace=os.path.relpath(trace, ROOT),
               stdout_valid_at_exit0=bool(rc == 0))
    return rec


def render_census(rec):
    if rec["status"] != "measured":
        return "census %-7s %s: %s" % (rec["status"], os.path.basename(rec["artifact"]),
                                       rec.get("why", ""))
    return ("census %s: functions %s (calls=%d, term=bdos:%s, rc=%d, stdout %d bytes %s)"
            % (os.path.basename(rec["artifact"]),
               ",".join(str(c) for c in rec["census"]) or "NONE",
               len(rec["calls"]), rec["term_witness"], rec["rc"], rec["stdout_bytes"],
               "VALID" if rec["stdout_valid_at_exit0"] else "DISCARDED (audit 2.18)"))


# --------------------------------------------------------------------------- CLI
def parse_stage_ceiling(text):
    if not text:
        return None
    out = []
    for s in text.split(","):
        s = s.strip().upper()
        if s not in STAGES:
            raise SystemExit("unknown stage %r (want any of %s)" % (s, ",".join(STAGES)))
        out.append(s)
    return out


def main(argv=None, *, host=None):
    """`host=' is a TEST SEAM (step 7): the hostile suite injects its stub world here to pin the
    CLI-level stdout grammar without spawning anything.  The CLI never uses it."""
    ap = argparse.ArgumentParser(description="E2E-50/P2 functional test harness (schema "
                                             "pli80-functional/1)")
    ap.add_argument("--spec-dir", default=SPEC_DIR_DEFAULT)
    ap.add_argument("--tests", nargs="*", default=None, help="test ids (default: every *.json)")
    ap.add_argument("--lane", nargs="*", choices=list(LANES), default=None)
    ap.add_argument("--stages", default=None, help="comma list of stages the harness MAY run; "
                    "later stages are recorded UNRUN and the verdict is therefore never PASS")
    ap.add_argument("--evidence", default=None, help="evidence root (default build/functional/)")
    ap.add_argument("--compiler", default=CC_DEFAULT)
    ap.add_argument("--pli80-run", default=None, help="Lane A emulator binary (user-supplied)")
    ap.add_argument("--cpmsim", default=None, help="Lane B cpmsim binary (user-supplied)")
    ap.add_argument("--artefacts", default=ARTEFACTS_DEFAULT,
                    help="directory holding LINK.COM/LIB.COM/RMAC.COM/PLILIB.IRL (user-supplied, "
                         "NEVER packaged)")
    ap.add_argument("--seeds", default=SEEDS_DEFAULT, help="CP/M boot seeds (copy-never-move)")
    ap.add_argument("--double-run", action="store_true",
                    help="run + assert twice and require byte-equal console capture "
                         "(docs/emulator-audit.md 2.20 determinism proof)")
    ap.add_argument("--json-out", default=None, help="also write the records as JSON here")
    ap.add_argument("--census", nargs="+", default=None, metavar="PROGRAM.COM",
                    help="BDOS census SUBSTRATE PROBE (not a verdict): run each program under "
                         "pli80-run --trace and record the observed BDOS call sequence "
                         "(docs/emulator-audit.md 4, open question 1)")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args(argv)

    ceiling = parse_stage_ceiling(a.stages)
    spec_dir = os.path.abspath(a.spec_dir)
    if not os.path.isdir(spec_dir):
        print("spec dir absent: %s" % spec_dir, file=sys.stderr)
        return 2
    names = a.tests if a.tests else sorted(
        f[:-5] for f in os.listdir(spec_dir) if f.endswith(".json"))
    if not names:
        print("no specs found in %s" % spec_dir, file=sys.stderr)
        return 2
    evidence_root = a.evidence or os.path.join(EVIDENCE_ROOT_DEFAULT,
                                               time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()))
    os.makedirs(evidence_root, exist_ok=True)
    if host is None:
        host = Host(compiler=a.compiler, pli80_run=a.pli80_run, cpmsim=a.cpmsim,
                    artefacts=a.artefacts, seeds=a.seeds)
    if a.census:
        # A probe measures the substrate; it produces no spec verdict and no exit-code claim.
        recs = []
        for i, com in enumerate(a.census):
            cdir = os.path.join(evidence_root, "census-%d" % i)
            os.makedirs(cdir, exist_ok=True)
            rec = bdos_census(host, com, cdir, max_steps=4000000)
            recs.append(rec)
            print(render_census(rec))
            host.write_evidence(cdir, "census.json", json.dumps(rec, indent=1) + "\n",
                                binary=False)
        print("evidence: %s" % os.path.relpath(evidence_root, ROOT))
        return 0 if all(r["status"] == "measured" for r in recs) else 1
    coverage = read_coverage_ids()
    all_records = []
    counts = {v: 0 for v in VERDICTS}
    for nid in names:
        path = os.path.join(spec_dir, nid + ".json")
        recs = run_test(path, host, evidence_root=evidence_root, lanes=a.lane,
                        stage_ceiling=ceiling, double_run=a.double_run, coverage=coverage)
        for r in recs:
            counts[r["verdict"]] += 1
            all_records.append(r)
            if not a.quiet:
                stop = next((s for s in r["stages"] if s["status"] not in
                             ("pass", "not-applicable")), None)
                st = Stage(stop["stage"], stop["status"], stop.get("attribution", ""),
                           stop.get("witness", ""), stop.get("detail", "")) if stop else None
                print(render_line(r["test_id"], r.get("lane", "-"), r["verdict"],
                                  r.get("attribution") or "", st))
    print("evidence: %s" % os.path.relpath(evidence_root, ROOT))
    print("verdicts: " + "  ".join("%s=%d" % (v, counts[v]) for v in VERDICTS))
    if a.json_out:
        with open(a.json_out, "w") as f:
            json.dump(all_records, f, indent=1, sort_keys=True)
    return 0 if all_records and counts["PASS"] == len(all_records) else 1


if __name__ == "__main__":
    sys.exit(main())
