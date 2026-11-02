#!/usr/bin/env python3
"""[E2E-50/P2 step 5 part 2] Hostile test suite for tools/functional_runner.py.

THE LAW IS `spec/functional/tests/README.md` (schema `pli80-functional/1`); the 13 required
cases are enumerated in `HANDOFF.md` -> Unfinished operations.  This suite proves the harness
cannot be mistaken for success: absent dependencies, timeouts, malformed output and mismatched
assertions are shown to produce their typed verdict (BLOCKED / FAIL / UNKNOWN) and NEVER a
PASS.  It is `check()`-style like tools/test_functional_dashboard.py: plain python3, exit 0
iff every check passes.

NO compiler, LINK-80, cpmsim, emulator or oracle process is EVER launched: every external
layer is injected through `Host(subprocess_run=, sim_session=, link_deps=, workspace_factory=,
run_factory=)` plus a class-level git_head stub.  The only real code executed is the harness
module itself and the oracle's PURE parser (`oracle/linkrun.py:parse_undefined` -- an import,
not a process): the [C137] classifier this suite must exercise verbatim.

The suite also PINs a landed defect: step-5 part 1 referenced `_rname` (the double-run evidence
name) seven times but never defined it -- every attempted Lane A RUN raised NameError and every
attempted Lane B RUN laundered it as `harness-exception/UNKNOWN`.  Case C12 (positive control:
a stubbed PASS reachable end-to-end) is what forces the fix; without it every "never PASS"
check below would be vacuously true.

  usage: python3 tools/test_functional_runner.py
"""
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import contextlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import functional_runner as fr  # noqa: E402

REPO = fr.ROOT                       # the real repository, kept for the oracle import path
sys.path.insert(0, os.path.join(REPO, "oracle"))
import cpmwork                        # noqa: E402  -- PURE: SafetyError class
import linkrun                        # noqa: E402  -- PURE: parse_undefined, TOOLS

# Every repo-relative join inside the harness (Lane A artifacts, evidence relpaths, identity
# paths) is re-rooted into the scratch world, so the suite writes NOTHING into the repository.
TMP = tempfile.mkdtemp(prefix="fr-hostile-")
fr.ROOT = TMP

# No git, ever: the record's git_head is stubbed at class level.
fr.Host.git_head = lambda self: "0" * 40
# Ambient overrides must not leak into dependency resolution.
os.environ.pop("PLI80_RUN", None)
os.environ.pop("CPMSIM", None)

FAILED = []
TOTAL = 0


def check(label, cond):
    """Self-counting: the summary prints TOTAL, so a document can quote a MEASURED number
    instead of a copy of the previous document's (the step-7 lesson: prose said "148 checks"
    while the artifact printed 171)."""
    global TOTAL
    TOTAL += 1
    print(("PASS  " if cond else "FAIL  ") + label)
    if not cond:
        FAILED.append(label)


# --------------------------------------------------------------------------- fixture constants
SRC = b"procedure options(main);\r\n  put list('x');\r\nend;\x1a"
ENCODING = "CRLF, ^Z-terminated, <=71 columns, ASCII"

# Synthetic coverage map (injected via run_test/validate_spec -- the real ledger is only read
# by the CLI cases, through main()).
COV = {
    "TABLE.TRAVERSE": ("ACCEPTS", "SUPPORTED"),
    "TABLE.SORT": ("ACCEPTS", "SUPPORTED"),
    "AGG.MULTIDIM": ("ACCEPTS", "SUPPORTED"),          # forbidden BY NAME, not by status
    "EXPR.K_PLUS_X": ("ACCEPTS", "SUPPORTED"),
    "LOOP.TRAVERSAL_RELOAD": ("ACCEPTS", "SUPPORTED"),
    "X.REFUSED": ("ACCEPTS", "REFUSED"),
    "X.DIVERGENT": ("ACCEPTS", "DIVERGENT"),
    "X.UNTESTED": ("UNTESTED", "SUPPORTED"),
}

DERIVE_LINES = ["SUM=6", "N=2"]

# LINK transcript shapes: the segment regex is `>>> LINK D:<T>(.*?)(?=>>> |\Z)'.
LINK_OK_TR = ">>> LINK D:TABLE00\nLINK-80 V1.3\nNO ERRORS\n>>> HALT\n"
# The [C137] trap: padding pushes `UNDEFINED SYMBOLS:' past character 120 -- a [:120] display
# slice reads CLEAN, the FULL segment names the symbol, and LINK wrote the .COM anyway.
LINK_UNDEF_TR = (">>> LINK D:TABLE00\n" + "-" * 130 +
                 "\nUNDEFINED SYMBOLS:\nPLIINP\nABSOLUTE LINK END\n>>> HALT\n")
# RUN transcripts: FS-01 anchor law `NAME[^\n]*\r\r\n(.*?)(?=D>|I/O ran|\Z)' + a fail-closed
# newline guard on the cut (functional_runner _run_lane_b).  The historical shape
# (oracle/linkrun.py:488 / FS-01 baseline od) is ONE guest `\r\n' between program end and prompt.
RUN_OK_TR = ">>> CP/M-80 2.2\nD>TABLE00\r\r\nSUM=6\r\nN=2\r\n"
RUN_BAD_TR = ">>> CP/M-80 2.2\nD>TABLE00\r\r\nSUM=5\r\nN=2\r\n"      # wrong value -> ASSERT
RUN_NOANCHOR_TR = ">>> CP/M-80 2.2\nD>TABLE00\n(no console region here)\n"
LANE_A_OUT = b"SUM=6\r\nN=2\r\n"          # Lane A stdout IS the capture (valid at exit 0 only)

LANE_B = {"lane": "B", "substrate": "cpmsim:z80pack (historical)",
          "toolchain": "pli80c -> .REL -> LINK-80 + PLILIB.IRL (user-supplied)",
          "link_targets": ["TABLE00"]}


def lane_a(artifact, sha):
    return {"lane": "A", "substrate": "pli80-run (free core)",
            "toolchain": "hand-assembled .COM fixture",
            "artifact": artifact, "artifact_sha256": sha}


REF_PY = ("import sys\ndef derive(func):\n"
          "    if func in ('derive', 'table00'):\n"
          "        return ['SUM=6', 'N=2']\n"
          "    raise KeyError(func)\n")


# --------------------------------------------------------------------------- the stub world
class FakeRun:
    """Stands in for oracle/cpmwork.py `Run' -- pure filesystem; no mkfs, no cpmcp, no cpmsim."""

    def __init__(self, world, tag):
        self.world = world
        self.tag = tag
        self.dir = os.path.join(world.root, "ws-" + tag)
        os.makedirs(self.dir, exist_ok=True)
        self.disks = os.path.join(self.dir, "disks.txt")
        self.calls = []
        self.cleaned = False
        world.runs.append(self)

    def mkfs(self, drive):
        self.calls.append(("mkfs", drive))

    def import_local(self, drive, path, name):
        assert os.path.isfile(path), "harness handed me a missing import: %s" % path
        self.calls.append(("import", drive, name))

    def export(self, drive, name, dest):
        self.calls.append(("export", drive, name))
        p = os.path.join(dest, name)
        with open(p, "wb") as f:
            f.write(b"\xc3\x00stub-COM")
        return p

    def cleanup(self):
        self.cleaned = True


class World:
    """One isolated universe: spec dir + source + reference, stub toolchain files, and the
    injectable Host with programmable subprocess/sim/link behaviours."""

    def __init__(self, name):
        self.root = os.path.join(TMP, name)
        self.spec_dir = os.path.join(self.root, "specs")
        os.makedirs(self.spec_dir)
        self.artefacts = os.path.join(self.root, "artefacts")     # FAKE DR files, never real
        os.makedirs(self.artefacts)
        self.seeds = os.path.join(self.root, "seeds")
        os.makedirs(self.seeds)
        for t in linkrun.TOOLS:
            with open(os.path.join(self.artefacts, t), "wb") as f:
                f.write(b"fake-" + t.encode())
        for s in ("drivea.dsk", "driveb.dsk"):
            with open(os.path.join(self.seeds, s), "wb") as f:
                f.write(b"fake-seed")
        self.cc = os.path.join(self.root, "pli80c.exe")           # stub COMPILER FILE
        with open(self.cc, "w") as f:
            f.write("stub compiler; never executed\n")
        self.pli80_run = os.path.join(self.root, "pli80-run.exe")  # stub EMULATOR FILE
        with open(self.pli80_run, "w") as f:
            f.write("stub runner; never executed\n")
        with open(os.path.join(self.spec_dir, "reference.py"), "w") as f:
            f.write(REF_PY)
        os.makedirs(os.path.join(TMP, "artifacts"), exist_ok=True)
        self.artifact = os.path.join(TMP, "artifacts", "HELLO.COM")
        with open(self.artifact, "wb") as f:
            f.write(b"stub artifact")
        self.src_sha = self.write_source()
        # programmable results
        self.compile_result = (0, b"CODE=358 DATA=30 ITEMS=12 -> 896 bytes\n")
        self.derive_result = (0, json.dumps(DERIVE_LINES).encode())
        self.lane_a_result = (0, LANE_A_OUT, b"")
        self.sessions_map = {}                     # name -> (rc, transcript)
        self.calls = []                            # every subprocess argv
        self.sessions = []                         # (name, script_lines) seen
        self.runs = []
        self._n = 0

    # -- spec authoring --------------------------------------------------------------
    def write_source(self, name="SRC.PLI", body=SRC):
        p = os.path.join(self.spec_dir, name)
        with open(p, "wb") as f:
            f.write(body)
        self.src_sha = fr.sha256_file(p)
        return self.src_sha

    def make_obj(self, tid, *, lanes=None, caps=None, expected=None, source=None,
                 limits=None, console_input=None, spec_tag=fr.SCHEMA_TAG):
        obj = {
            "spec": spec_tag, "id": tid, "family": "HOSTILE",
            "title": "hostile-suite fixture",
            "provenance": {"origin": "original", "author": "step-5 part 2 suite",
                           "date": "2026-11-02",
                           "note": "synthetic fixture; claims no DR behaviour"},
            "source": source or {"file": "SRC.PLI", "sha256": self.src_sha,
                                 "encoding": ENCODING},
            "capabilities": caps or ["TABLE.TRAVERSE"],
            "limits": limits or {"compile_timeout_s": 10, "link_timeout_s": 10,
                                 "run_timeout_s": 10, "run_max_steps": 100000},
            "lanes": lanes if lanes is not None else [dict(LANE_B)],
            "expected": expected or {"derivation": "reference.py:derive",
                                     "normalization": "collapse-spaces-v1",
                                     "console": list(DERIVE_LINES)},
        }
        if console_input is not None:
            obj["console_input"] = console_input
        return obj

    def write_spec(self, obj, name=None):
        p = os.path.join(self.spec_dir, (name or obj["id"]) + ".json")
        with open(p, "w") as f:
            json.dump(obj, f, indent=1)
        return p

    # -- external world ---------------------------------------------------------------
    def subprocess_run(self, argv, **kw):
        argv = list(argv)
        self.calls.append(argv)
        if argv[0] == self.pli80_run:                      # Lane A runner
            rc, out, err = self.lane_a_result
            if isinstance(rc, BaseException):
                raise rc
            return subprocess.CompletedProcess(argv, rc, out, err)
        if argv[0] == self.cc:                             # compiler stub
            rc, err = self.compile_result
            if isinstance(rc, BaseException):
                raise rc
            if rc == 0:
                with open(argv[-1], "wb") as f:
                    f.write(b"\xe9" * 128)                 # a real non-empty .REL FILE
            return subprocess.CompletedProcess(argv, rc, b"", err)
        if len(argv) > 1 and argv[1] == "-c":              # derivation (its own process)
            rc, payload = self.derive_result
            if isinstance(rc, BaseException):
                raise rc
            err = b"" if rc == 0 else b"Traceback (most recent call last): boom"
            return subprocess.CompletedProcess(argv, rc, payload, err)
        raise AssertionError("the suite must never launch this: %r" % argv)

    def sim_session(self, run, lines, timeout, name, evidence):
        self.sessions.append((name, list(lines)))
        rc, tr = self.sessions_map.get(
            name, (0, RUN_OK_TR if name.startswith("run") else LINK_OK_TR))
        if isinstance(rc, BaseException):
            raise rc
        with open(os.path.join(evidence, "%s.raw-transcript.txt" % name), "w") as f:
            f.write(tr)
        return rc, tr

    def boom(self, *a, **k):
        raise AssertionError("no external layer may be touched by this case")

    def host(self, *, compiler=None, pli80_run="unset", **over):
        kw = dict(compiler=compiler or self.cc, subprocess_run=self.subprocess_run,
                  sim_session=self.sim_session, link_deps=[],
                  artefacts=self.artefacts, seeds=self.seeds,
                  workspace_factory=lambda root, seeds: object(),
                  run_factory=lambda ws, tag: FakeRun(self, tag))
        if pli80_run != "unset":
            kw["pli80_run"] = pli80_run
        kw.update(over)
        return fr.Host(**kw)

    def lane_a_obj(self, tid, **over):
        return self.make_obj(tid, lanes=[lane_a("artifacts/HELLO.COM",
                                                fr.sha256_file(self.artifact))], **over)

    def run(self, path=None, obj=None, tid="HOST-01", *, host=None, lanes=None,
            stage_ceiling=None, double_run=False, coverage=COV):
        if path is None:
            path = self.write_spec(obj or self.make_obj(tid, lanes=lanes))
        host = host or self.host()
        self._n += 1
        ev = os.path.join(self.root, "ev%02d" % self._n)
        return fr.run_test(path, host, evidence_root=ev, lanes=lanes,
                           stage_ceiling=stage_ceiling, double_run=double_run,
                           coverage=coverage)

    def edir(self, rec):
        return os.path.join(TMP, rec["evidence_dir"])


# --------------------------------------------------------------------------- record helpers
def stage_of(rec, name):
    return next((s for s in rec["stages"] if s["stage"] == name), None)


def statuses(rec):
    return {s["stage"]: s["status"] for s in rec["stages"]}


def lane_recs(recs, lane):
    return [r for r in recs if r.get("lane") == lane]


# =========================================================================== C12 first: the
# positive control.  A stubbed PASS reachable end-to-end, both lanes.  If this fails, every
# "never PASS" check below is vacuous and the suite proves nothing.
print("== C12: positive control -- a stubbed PASS is reachable end-to-end (both lanes)")
w = World("c12")
rec = w.run(obj=w.make_obj("POS-B"))[0]
check("C12a lane B stub chain verdict PASS", rec["verdict"] == "PASS" and rec["stopped_at"] is None)
check("C12a lane B every applicable stage ran+passed",
      statuses(rec) == {"SOURCE": "pass", "DERIVATION": "pass", "COMPILE": "pass",
                        "LINK": "pass", "RUN": "pass", "ASSERT": "pass"})
check("C12a COMPILE -d banner parsed when present", "code=358" in stage_of(rec, "COMPILE")["detail"])
check("C12a LINK success = done witness + parse_undefined=[] on the FULL segment",
      stage_of(rec, "LINK")["witness"] == "done, parse_undefined=[]")
check("C12a RUN lane-B witness is TERMINATION, never correctness (L2)",
      "not correctness" in stage_of(rec, "RUN")["witness"])
sess = dict(w.sessions)
check("C12a the RUN session obeys the measured prompt-sync law",
      "##SEND \\r" in sess["run"] and "##WAIT \\nD>" in sess["run"]
      and "##SEND TABLE00\\r" in sess["run"] and "##SEND \\x1a" in sess["run"])
check("C12a the LINK session is C:/LINK D:NAME/##HALT",
      sess["link"] == ["C:", "LINK D:TABLE00", "##HALT"])
check("C12a the console capture is exactly the anchored region",
      open(os.path.join(w.edir(rec), "run.console.bin"), "rb").read() == b"SUM=6\r\nN=2\r\n")
check("C12a ASSERT passed on the normalized complete stream",
      stage_of(rec, "ASSERT")["witness"] == "complete-stream match")
check("C12a evidence files landed (segment, COM sha, COM sha, norm stream)",
      all(os.path.isfile(os.path.join(w.edir(rec), f))
          for f in ("link.segment.txt", "link.com.sha256.txt", "TABLE00.COM",
                    "COMPILE.object.sha256.txt", "run.console.bin", "ASSERT.console.norm.txt")))
check("C12a every FakeRun was cleaned up (finally-path)", w.runs and all(r.cleaned for r in w.runs))
check("C12a the record hashes the DR tool identities it declares",
      rec["substrate_identity"]["dr:LINK.COM"]["sha256"] ==
      fr.sha256_file(os.path.join(w.artefacts, "LINK.COM")))

w2 = World("c12b")
w2.compile_result = (0, b"")                       # NO CODE=/DATA= banner on stderr
rec_nb = w2.run(obj=w2.make_obj("POS-B2"))[0]
check("C12b the -d banner is OPTIONAL: PASS with 'sizes unreported'",
      rec_nb["verdict"] == "PASS" and
      stage_of(rec_nb, "COMPILE")["detail"] == "sizes unreported")

w = World("c12c")
rec = w.run(obj=w.lane_a_obj("POS-A"), host=w.host(pli80_run=w.pli80_run))[0]
check("C12c lane A stub chain verdict PASS", rec["verdict"] == "PASS")
check("C12c lane A COMPILE/LINK not-applicable IN ADVANCE (README 5.2/8)",
      statuses(rec)["COMPILE"] == "not-applicable" and statuses(rec)["LINK"] == "not-applicable")
check("C12c lane A artifact hash pinned at SOURCE",
      stage_of(rec, "SOURCE")["witness"] == "sha256+encoding verified")
check("C12c lane A substrate records the artifact AND runner hashes (README 11)",
      rec["substrate_identity"]["artifact"]["sha256"] == fr.sha256_file(w.artifact) and
      rec["substrate_identity"]["pli80_run"]["sha256"] == fr.sha256_file(w.pli80_run))
check("C12c render_line shows PASS with no attr field",
      "PASS" in fr.render_line(rec["test_id"], "A", rec["verdict"], rec["attribution"] or "", None))
# the defect the positive control exposed (measured before the fix): `_rname' was referenced
# by both lane RUN paths but never defined -> Lane A crashed, Lane B laundered harness-exception.
check("C12d the harness defines every name its RUN paths reference (hop-4 `_rname' fix landed)",
      hasattr(fr, "_rname"))

# =========================================================================== C1: absent deps
print("== C1: absent dependencies -> BLOCKED, NAMED, never PASS (README 8)")
w = World("c1")
rec = w.run(obj=w.make_obj("DEP-CC"), host=w.host(compiler=os.path.join(w.root, "no-cc")))[0]
check("C1a missing compiler -> COMPILE blocked, verdict BLOCKED, never PASS",
      rec["verdict"] == "BLOCKED" and rec["attribution"] == "host" and
      statuses(rec)["COMPILE"] == "blocked" and
      stage_of(rec, "COMPILE")["witness"] == "compiler-missing")
check("C1a BLOCKED names the missing compiler path",
      "no-cc" in stage_of(rec, "COMPILE")["detail"])
check("C1a later stages unrun after a blocked stage",
      statuses(rec)["LINK"] == "unrun" and statuses(rec)["ASSERT"] == "unrun")
missing = ["DR tool /user/supplied/LINK.COM (user-supplied, never packaged)",
           "cpmsim binary /user/supplied/cpmsim"]
rec = w.run(obj=w.make_obj("DEP-LINK"), host=w.host(link_deps=missing))[0]
check("C1b absent link deps -> LINK blocked, verdict BLOCKED",
      rec["verdict"] == "BLOCKED" and statuses(rec)["LINK"] == "blocked" and
      stage_of(rec, "LINK")["witness"] == "dependencies-absent")
check("C1b the BLOCKED detail NAMES every missing dep",
      all(s in stage_of(rec, "LINK")["detail"] for s in ("LINK.COM", "cpmsim")))
check("C1b no link session was started for a dependency-blocked LINK",
      "link" not in [n for n, _ in w.sessions])


def safety_boom(root, seeds):
    raise cpmwork.SafetyError("refusing to touch anything outside the workspace")


rec = w.run(obj=w.make_obj("DEP-WS"), host=w.host(workspace_factory=safety_boom))[0]
check("C1c workspace SafetyError -> LINK blocked workspace-refused with the message",
      rec["verdict"] == "BLOCKED" and stage_of(rec, "LINK")["witness"] == "workspace-refused"
      and "outside the workspace" in stage_of(rec, "LINK")["detail"])
rec = w.run(obj=w.lane_a_obj("DEP-EMU"),
            host=w.host(pli80_run=os.path.join(w.root, "no-run.exe")))[0]
check("C1d missing pli80-run -> RUN blocked, verdict BLOCKED, never PASS",
      rec["verdict"] == "BLOCKED" and statuses(rec)["RUN"] == "blocked" and
      stage_of(rec, "RUN")["witness"] == "emulator-absent")
check("C1d the RUN detail names the supplying mechanism (--pli80-run / PLI80_RUN)",
      "--pli80-run" in stage_of(rec, "RUN")["detail"] and
      "PLI80_RUN" in stage_of(rec, "RUN")["detail"])
rec = w.run(obj=w.make_obj("DEP-SRC", source={"file": "GONE.PLI", "sha256": "0" * 64,
                                              "encoding": ENCODING}))[0]
check("C1e missing source -> SOURCE blocked source-file-missing, verdict BLOCKED",
      rec["verdict"] == "BLOCKED" and
      stage_of(rec, "SOURCE")["witness"] == "source-file-missing" and
      "GONE.PLI" in stage_of(rec, "SOURCE")["detail"])
rec = w.run(obj=w.make_obj(
    "DEP-REF", expected={"derivation": "gone_ref.py:derive",
                         "normalization": "collapse-spaces-v1",
                         "console": list(DERIVE_LINES)}))[0]
check("C1f missing reference -> DERIVATION blocked reference-missing, verdict BLOCKED",
      rec["verdict"] == "BLOCKED" and
      stage_of(rec, "DERIVATION")["witness"] == "reference-missing" and
      "gone_ref.py" in stage_of(rec, "DERIVATION")["detail"])
w3 = World("c1g")
w3.compile_result = (FileNotFoundError(2, "No such file or directory"), b"")
rec = w3.run(obj=w3.make_obj("DEP-EXEC"))[0]
check("C1g compiler launch-failed -> COMPILE blocked, verdict BLOCKED",
      rec["verdict"] == "BLOCKED" and
      stage_of(rec, "COMPILE")["witness"] == "compiler-launch-failed")
w4 = World("c1h")
w4.lane_a_result = (FileNotFoundError(2, "No such file or directory"), b"", b"")
rec = w4.run(obj=w4.lane_a_obj("DEP-AEXEC"), host=w4.host(pli80_run=w4.pli80_run))[0]
check("C1h Lane A launch-failed -> RUN blocked, verdict BLOCKED",
      rec["verdict"] == "BLOCKED" and stage_of(rec, "RUN")["witness"] == "emulator-launch-failed")

# ============================================== C2: three distinct termination witnesses
print("== C2: wall-clock vs timeout(rc=1) vs sim-died(rc=2) -- distinct witnesses, none PASS [C308]")
wit = {}
for rc, key, attr, status in ((-1, "wall-clock-timeout", "undefined", "fail"),
                              (1, "timeout", "undefined", "fail"),
                              (2, "sim-died", "emulator", "fail"),
                              (3, "unknown-rc-3", "undefined", "unknown")):
    w = World("c2-%s" % key)
    w.sessions_map = {"run": (rc, RUN_OK_TR)}
    rec = w.run(obj=w.make_obj("WIT-B"))[0]
    st = stage_of(rec, "RUN")
    wit[key] = st["witness"]
    check("C2 lane B RUN rc=%d -> witness %r, status %r, attribution %r" % (rc, key, status, attr),
          st["witness"] == key and st["status"] == status and st.get("attribution") == attr)
    check("C2 lane B rc=%d verdict never PASS; ASSERT never evaluates" % rc,
          rec["verdict"] != "PASS" and statuses(rec)["ASSERT"] == "unrun")
check("C2 the four witnesses are DISTINCT facts (never collapsed)", len(set(wit.values())) == 4)
check("C2 timeout is NOT sim-died and the harness wall-clock guard is its own class",
      wit["timeout"] != wit["sim-died"] and wit["wall-clock-timeout"] not in
      ("timeout", "sim-died"))
for rc, key in ((-1, "wall-clock-timeout"), (1, "timeout"), (2, "sim-died")):
    w = World("c2l-%s" % key)
    w.sessions_map = {"link": (rc, LINK_OK_TR)}
    rec = w.run(obj=w.make_obj("WIT-L"))[0]
    check("C2 lane B LINK rc=%d -> %s recorded, verdict FAIL, RUN unrun" % (rc, key),
          stage_of(rec, "LINK")["witness"] == key and statuses(rec)["LINK"] == "fail" and
          rec["verdict"] == "FAIL" and statuses(rec)["RUN"] == "unrun")
w = World("c2simattr")
w.sessions_map = {"link": (2, LINK_OK_TR)}
rec = w.run(obj=w.make_obj("WIT-LS"))[0]
check("C2 sim-died at LINK attributes to the EMULATOR (the typed witness licenses it)",
      stage_of(rec, "LINK")["attribution"] == "emulator")
w = World("c2a")
w.lane_a_result = (subprocess.TimeoutExpired(cmd="x", timeout=1), b"", b"")
rec = w.run(obj=w.lane_a_obj("WIT-A"), host=w.host(pli80_run=w.pli80_run))[0]
check("C2 Lane A wall-clock -> RUN fail attribution undefined, verdict FAIL, never PASS",
      rec["verdict"] == "FAIL" and statuses(rec)["RUN"] == "fail" and
      stage_of(rec, "RUN")["attribution"] == "undefined")

# ==================================================== C3: malformed transcript -> UNKNOWN
print("== C3: malformed output (no link segment / no console anchor) -> UNKNOWN, never PASS")
w = World("c3")
w.sessions_map = {"link": (0, ">>> CP/M boot banner\nD> nothing linked here\n")}
rec = w.run(obj=w.make_obj("MAL-LINK"))[0]
check("C3 LINK transcript with no '>>> LINK D:' segment -> UNKNOWN no-link-segment",
      rec["verdict"] == "UNKNOWN" and statuses(rec)["LINK"] == "unknown" and
      stage_of(rec, "LINK")["witness"] == "no-link-segment" and
      rec["attribution"] == "undefined")
check("C3 rc=0 with unparseable evidence is NOT read as a clean link (L2)",
      statuses(rec)["RUN"] == "unrun")
w = World("c3b")
w.sessions_map = {"link": (0, LINK_OK_TR), "run": (0, RUN_NOANCHOR_TR)}
rec = w.run(obj=w.make_obj("MAL-RUN"))[0]
check("C3 RUN transcript with no console anchor -> UNKNOWN no-console-anchor",
      rec["verdict"] == "UNKNOWN" and stage_of(rec, "RUN")["witness"] == "no-console-anchor")
check("C3 the chain stops: ASSERT never evaluates missing evidence",
      statuses(rec)["ASSERT"] == "unrun")
w = World("c3c")
w.derive_result = (0, b"[1, 2, 3]")                  # not a list of strings
rec = w.run(obj=w.make_obj("MAL-DERIVE"))[0]
check("C3 malformed derivation payload -> FAIL malformed-derivation (source), lane never run",
      rec["verdict"] == "FAIL" and
      stage_of(rec, "DERIVATION")["witness"] == "malformed-derivation" and
      statuses(rec)["COMPILE"] == "unrun")

# ============================ C4: UNDEFINED SYMBOLS past char 120 + a .COM present -> FAIL
print("== C4: [C137] UNDEFINED SYMBOLS beyond char 120 with a .COM present -> FAIL")
seg_full = re.sub(r"\r+\n", "\n", LINK_UNDEF_TR.split(">>> LINK D:TABLE00", 1)[1]
                  .split(">>> HALT", 1)[0])
check("C4 the [:120] display slice reads CLEAN -- this is the documented trap",
      linkrun.parse_undefined(seg_full[:120]) == [])
check("C4 the FULL segment names the symbol (parse finds PLIINP)",
      linkrun.parse_undefined(seg_full) == ["PLIINP"])
w = World("c4")
w.sessions_map = {"link": (0, LINK_UNDEF_TR)}
rec = w.run(obj=w.make_obj("C137-LINK"))[0]
check("C4 harness LINK verdict FAIL on the deep UNDEFINED SYMBOLS",
      rec["verdict"] == "FAIL" and statuses(rec)["LINK"] == "fail" and
      "undefined-symbols:PLIINP" in stage_of(rec, "LINK")["witness"])
check("C4 the [C137] lesson is recorded in the detail", "C137" in stage_of(rec, "LINK")["detail"])
check("C4 attribution stays typed `undefined' (README 9: no evidence names an origin yet)",
      stage_of(rec, "LINK")["attribution"] == "undefined")
check("C4 a .COM would not have saved it: export never ran on the undef path",
      not any(c[0] == "export" for r in w.runs for c in r.calls))
check("C4 RUN/ASSERT never execute after the FAILed LINK",
      statuses(rec)["RUN"] == "unrun" and statuses(rec)["ASSERT"] == "unrun")
check("C4 the FULL segment is preserved as evidence (never a slice)",
      "UNDEFINED SYMBOLS" in open(os.path.join(w.edir(rec), "link.segment.txt")).read())

# ============================================ C5: assertion mismatch -> FAIL, attr undefined
print("== C5: assertion mismatch -> FAIL with attribution `undefined', never narrowed")
w = World("c5")
w.sessions_map = {"run": (0, RUN_BAD_TR)}
rec = w.run(obj=w.make_obj("ASSERT-NE"))[0]
check("C5 mismatched stream -> FAIL assert-mismatch, verdict FAIL",
      rec["verdict"] == "FAIL" and statuses(rec)["ASSERT"] == "fail" and
      stage_of(rec, "ASSERT")["witness"] == "assert-mismatch")
check("C5 attribution is `undefined' and is NEVER narrowed (README 9.2: no runtime-lib)",
      rec["attribution"] == "undefined" and
      all(s.get("attribution") != "runtime-lib" for s in rec["stages"]) and
      "undefined" in stage_of(rec, "ASSERT")["detail"])
check("C5 RUN passed but earns nothing: capture then judged by ASSERT (L3)",
      statuses(rec)["RUN"] == "pass")
w = World("c5b")
w.sessions_map = {"run": (0, "D>TABLE00\r\r\nSUM=6\r\nN=2\r\nEXTRA\r\n")}
rec = w.run(obj=w.make_obj("ASSERT-EXTRA"))[0]
check("C5 an extra line breaks the COMPLETE-stream law",
      rec["verdict"] == "FAIL" and "extra lines" in stage_of(rec, "ASSERT")["detail"])
w = World("c5c")
w.sessions_map = {"run": (0, "D>TABLE00\r\r\nSUM=6\r\n")}
rec = w.run(obj=w.make_obj("ASSERT-SHORT"))[0]
check("C5 a missing line breaks the COMPLETE-stream law",
      rec["verdict"] == "FAIL" and "missing lines" in stage_of(rec, "ASSERT")["detail"])
NEG_EXP = {"derivation": "reference.py:derive", "normalization": "collapse-spaces-v1",
           "console": DERIVE_LINES + ["!NUL"]}
w = World("c5d")
w.derive_result = (0, json.dumps(DERIVE_LINES + ["!NUL"]).encode())
w.sessions_map = {"run": (0, "D>TABLE00\r\r\nSUM=6\r\nN=2\r\nNUL: error\r\n")}
rec = w.run(obj=w.make_obj("ASSERT-NEG", expected=dict(NEG_EXP)))[0]
check("C5 a present `!text' negative -> FAIL forbidden-present in the detail",
      rec["verdict"] == "FAIL" and
      "forbidden-present:NUL" in stage_of(rec, "ASSERT")["detail"])
w = World("c5e")
w.derive_result = (0, json.dumps(DERIVE_LINES + ["!NUL"]).encode())
w.sessions_map = {"run": (0, "D>TABLE00\r\r\nSUM=6\r\nN=2\r\n")}
rec = w.run(obj=w.make_obj("ASSERT-NEGOK", expected=dict(NEG_EXP)))[0]
check("C5 an absent `!text' negative contributes to a real PASS",
      rec["verdict"] == "PASS" and "negative" in stage_of(rec, "ASSERT")["detail"])
RAW_EXP = {"derivation": "reference.py:derive", "normalization": "exact", "raw": "SUM=6\nN=2\n"}
w = World("c5f")
w.sessions_map = {"run": (0, "D>TABLE00\r\r\nSUM=6\r\nN=3\r\n")}
rec = w.run(obj=w.make_obj("ASSERT-EXACT", expected=dict(RAW_EXP)))[0]
check("C5 exact-mode byte mismatch -> FAIL assert-mismatch (exact)",
      rec["verdict"] == "FAIL" and
      stage_of(rec, "ASSERT")["witness"] == "assert-mismatch (exact)")
check("C5 verdict_of never grants PASS with a failed ASSERT",
      fr.verdict_of([fr.Stage("RUN", "pass"), fr.Stage("ASSERT", "fail", "undefined")])[0] == "FAIL")

# ================================ C6: fail-closed schema validation, no lane may execute
print("== C6: fail-closed validation (unknown/null/empty/forbidden/illegal-shape) -> spec FAIL `source'")
MUT = []


def mut(label, fixer, want):
    MUT.append((label, fixer, want))


mut("unknown top-level field", lambda o: o.update(colour="red"), "unknown top-level field")
mut("unknown lane field", lambda o: o["lanes"][0].update(extra=1), "unknown lane field")
mut("unknown provenance field", lambda o: o["provenance"].update(why=1), "unknown provenance field")
mut("unknown source field", lambda o: o["source"].update(encoding2="x"), "unknown source field")
mut("unknown limits field", lambda o: o["limits"].update(max_ram=1), "unknown limits field")
mut("unknown expected field", lambda o: o["expected"].update(stream=1), "unknown expected field")
mut("null required field", lambda o: o.update(title=None), "null is not legal")
mut("missing required field", lambda o: o.pop("provenance"), "missing required field")
mut("wrong schema tag", lambda o: o.update(spec="pli80-functional/2"), "pli80-functional/1")
mut("id != basename", lambda o: o.update(id="OTHER"), "must equal the spec basename")
mut("empty expected.console", lambda o: o["expected"].update(console=[]), "non-empty array")
mut("non-string console entry [FC-01 hop 3: '' is now LEGAL, non-strings still refused]",
    lambda o: o["expected"].update(console=["SUM=6", 7]), "must be strings")
mut("bare '!' console entry (negative needs text)",
    lambda o: o["expected"].update(console=["SUM=6", "!"]), 'bare "!"')
mut("forbidden cap AGG.MULTIDIM (in coverage!)",
    lambda o: o.update(capabilities=["AGG.MULTIDIM"]), "forbidden in v1")
mut("forbidden cap EXPR.K_PLUS_X", lambda o: o.update(capabilities=["EXPR.K_PLUS_X"]), "forbidden in v1")
mut("forbidden cap LOOP.TRAVERSAL_RELOAD",
    lambda o: o.update(capabilities=["LOOP.TRAVERSAL_RELOAD"]), "forbidden in v1")
mut("unknown cap", lambda o: o.update(capabilities=["NO.SUCH"]), "does not exist in spec/COVERAGE.tsv")
mut("REFUSED cap", lambda o: o.update(capabilities=["X.REFUSED"]), "mine_status REFUSED")
mut("DIVERGENT cap", lambda o: o.update(capabilities=["X.DIVERGENT"]), "mine_status DIVERGENT")
mut("UNTESTED-DR cap", lambda o: o.update(capabilities=["X.UNTESTED"]), "dr_status UNTESTED")
mut("lane A link_targets illegal",
    lambda o: o.update(lanes=[{"lane": "A", "substrate": "s", "toolchain": "t",
                               "artifact": "artifacts/HELLO.COM",
                               "artifact_sha256": "0" * 64, "link_targets": ["X"]}]),
    "link_targets is illegal")
mut("lane B artifact illegal",
    lambda o: o.update(lanes=[{"lane": "B", "substrate": "s", "toolchain": "t",
                               "link_targets": ["TABLE00"], "artifact": "x.COM"}]),
    "artifact fields are illegal")
mut("multi link_targets",
    lambda o: o.update(lanes=[{"lane": "B", "substrate": "s", "toolchain": "t",
                               "link_targets": ["AAA", "BBB"]}]), "exactly one link_target")
mut("non-8.3 link_target", lambda o: o["lanes"][0].update(link_targets=["1BAD-NAME!"]),
    "not a CP/M 8.3 name")
mut("file_expectations refused (unimplemented)",
    lambda o: o["expected"].update(file_expectations={"OUT.DAT": "golden/x"}), "NOT implemented")
mut("duplicate lane B", lambda o: o.update(lanes=[dict(LANE_B), dict(LANE_B)]), "duplicate lane")
mut("lane A console_input (audit 2.12: no console input exists)",
    lambda o: o.update(lanes=[lane_a("artifacts/HELLO.COM", "0" * 64)], console_input="hello\n"),
    "console_input")
mut("derivation without colon", lambda o: o["expected"].update(derivation="reference.py"),
    "<script>:<function>")
mut("bad normalization", lambda o: o["expected"].update(normalization="collapse-v2"), "not in")
mut("exact with console",
    lambda o: o["expected"].update(normalization="exact", raw="x\n"), "illegal under 'exact'")
mut("exact without raw",
    lambda o: o["expected"].update(normalization="exact", console=list(DERIVE_LINES)),
    "requires a non-empty expected.raw")
mut("raw without exact", lambda o: o["expected"].update(raw="x\n"), "legal only under")
mut("limits zero", lambda o: o["limits"].update(run_timeout_s=0), "positive integer")
mut("limits missing", lambda o: o["limits"].pop("compile_timeout_s"),
    "limits.compile_timeout_s is required")
mut("source.sha256 not hex64", lambda o: o["source"].update(sha256="deadbeef"), "64 lowercase hex")
mut("source.file traversal", lambda o: o["source"].update(file="../escape.PLI"), "relative path")

w = World("c6")
for label, fixer, want in MUT:
    obj = w.make_obj("VAL-01")
    fixer(obj)
    probs = fr.validate_spec(obj, basename="VAL-01", coverage=COV)
    hit = any(want in p for p in probs)
    if not hit:
        print("    problems for %r: %s" % (label, probs))
    check("C6 fail-closed: %s" % label, bool(probs) and hit)
# a VALID spec must produce NO problems (else the fail-closed loop proves nothing)
check("C6 the unmutated fixture spec is VALID (suite is not vacuous)",
      fr.validate_spec(w.make_obj("VAL-OK"), basename="VAL-OK", coverage=COV) == [])
# run_test on a broken spec: FAIL/source, ONE stage, no external layer touched
w = World("c6r")
obj = w.make_obj("VAL-RUN")
obj["expected"]["console"] = []
host = w.host(subprocess_run=w.boom, sim_session=w.boom, link_deps=w.boom,
              workspace_factory=w.boom, run_factory=w.boom)
rec = w.run(path=w.write_spec(obj), host=host)[0]
check("C6 invalid spec -> FAIL attribution source",
      rec["verdict"] == "FAIL" and rec["attribution"] == "source")
check("C6 invalid spec -> exactly ONE SOURCE stage record (spec-validation), NO lane ran",
      len(rec["stages"]) == 1 and rec["stages"][0]["witness"] == "spec-validation")
check("C6 invalid spec -> SPECERRORS.txt evidence written",
      os.path.isfile(os.path.join(TMP, rec["evidence_dir"], "SPECERRORS.txt")))
check("C6 invalid spec -> no lane evidence dir exists",
      not os.path.isdir(os.path.join(TMP, rec["evidence_dir"], "lane-B")))
check("C6 nothing external ran on the validation path", w.calls == [])
rec = w.run(path=os.path.join(w.root, "nope.json"), host=host)[0]
check("C6 an unreadable spec file -> BLOCKED spec-unreadable, never FAIL-laundered",
      rec["verdict"] == "BLOCKED" and rec["stages"][0]["witness"] == "spec-unreadable")

# =============================================== C7: sha256 / encoding mismatch -> SOURCE FAIL
print("== C7: source or artifact sha mismatch -> SOURCE FAIL `source' (BEFORE any execution)")
w = World("c7")
obj = w.make_obj("SHA-SRC")
obj["source"]["sha256"] = "f" * 64                     # spec pins the WRONG hash
rec = w.run(path=w.write_spec(obj))[0]
check("C7 source sha256 mismatch -> SOURCE fail sha256-mismatch, verdict FAIL `source'",
      rec["verdict"] == "FAIL" and rec["attribution"] == "source" and
      stage_of(rec, "SOURCE")["witness"] == "sha256-mismatch")
check("C7 the hash check runs BEFORE any execution (no compiler/derivation call)",
      w.calls == [])
w = World("c7b")
w.write_source(body=b"LF only\nno crlf\n")             # sha updated by write_source
rec = w.run()[0]                                       # spec pins the NEW sha
rec = rec                                              # SOURCE must fail on the DECLARED form
check("C7 bare LF under a declared-CRLF spec -> SOURCE fail encoding-mismatch",
      rec["verdict"] == "FAIL" and stage_of(rec, "SOURCE")["witness"] == "encoding-mismatch" and
      "bare LF" in stage_of(rec, "SOURCE")["detail"])
w = World("c7c")
w.write_source(body=b"/* " + b"x" * 80 + b" */\r\nend;\x1a")
rec = w.run()[0]
check("C7 a line wider than declared -> SOURCE fail (<=71 col law)",
      stage_of(rec, "SOURCE")["witness"] == "encoding-mismatch" and
      "widest line" in stage_of(rec, "SOURCE")["detail"])
w = World("c7d")
w.write_source(body=b"caf\xc3\xa9\r\n\x1a")
rec = w.run()[0]
check("C7 high bytes under the ASCII declaration -> SOURCE fail",
      stage_of(rec, "SOURCE")["witness"] == "encoding-mismatch" and
      "high bytes" in stage_of(rec, "SOURCE")["detail"])
w = World("c7e")
obj = w.make_obj("SHA-NOCONV")
obj["source"]["encoding"] = "whatever"                 # no checkable token AT ALL
rec = w.run(path=w.write_spec(obj))[0]
check("C7 an encoding form with NO checkable token fails CLOSED",
      stage_of(rec, "SOURCE")["witness"] == "encoding-mismatch" and
      "no checkable" in stage_of(rec, "SOURCE")["detail"])
w = World("c7f")
declared = fr.sha256_file(w.artifact)            # the sha the spec pins
with open(w.artifact, "wb") as f:
    f.write(b"tampered artifact bytes")          # the file DISAGREES with the pin
rec = w.run(obj=w.make_obj("SHA-ART", lanes=[lane_a("artifacts/HELLO.COM", declared)]),
            host=w.host(pli80_run=w.pli80_run))[0]
check("C7 Lane A artifact sha mismatch -> SOURCE fail artifact-sha256-mismatch",
      rec["verdict"] == "FAIL" and
      stage_of(rec, "SOURCE")["witness"] == "artifact-sha256-mismatch" and
      rec["attribution"] == "source")
w = World("c7g")
obj = w.make_obj("SHA-ARTMISS",
                 lanes=[lane_a("artifacts/ABSENT.COM", "a" * 64)])
rec = w.run(path=w.write_spec(obj), host=w.host(pli80_run=w.pli80_run))[0]
check("C7 Lane A artifact missing -> SOURCE blocked artifact-missing -> BLOCKED",
      rec["verdict"] == "BLOCKED" and stage_of(rec, "SOURCE")["witness"] == "artifact-missing")

# ================================================ C8: derivation drift/raise -> FAIL `source'
print("== C8: reference/spec drift -> FAIL `source', NO lane stage may run afterwards")
w = World("c8")
w.derive_result = (0, json.dumps(["SUM=7", "N=2"]).encode())    # the reference DISAGREES
rec = w.run(obj=w.make_obj("DRIFT"))[0]
check("C8 drift -> FAIL spec/reference drift attribution source",
      rec["verdict"] == "FAIL" and rec["attribution"] == "source" and
      stage_of(rec, "DERIVATION")["witness"] == "spec/reference drift")
check("C8 drift stops the chain: COMPILE/LINK/RUN/ASSERT unrun, no compiler call",
      statuses(rec)["COMPILE"] == "unrun" and statuses(rec)["ASSERT"] == "unrun" and
      not any(a[0] == w.cc for a in w.calls))
check("C8 the drift evidence file exists (derived vs spec)",
      os.path.isfile(os.path.join(w.edir(rec), "DERIVATION.drift.txt")))
w = World("c8b")
w.derive_result = (1, b"")                                      # reference.py RAISES
rec = w.run(obj=w.make_obj("RAISE"))[0]
check("C8 reference raised -> FAIL derivation-error (source), traceback evidence kept",
      rec["verdict"] == "FAIL" and stage_of(rec, "DERIVATION")["witness"] == "derivation-error" and
      os.path.isfile(os.path.join(w.edir(rec), "DERIVATION.traceback.txt")))
w = World("c8c")
w.derive_result = (subprocess.TimeoutExpired(cmd="x", timeout=1), b"")
rec = w.run(obj=w.make_obj("DERIV-TO"))[0]
check("C8 derivation wall-clock -> FAIL timeout witness, attribution undefined, never PASS",
      rec["verdict"] == "FAIL" and stage_of(rec, "DERIVATION")["witness"] == "timeout" and
      stage_of(rec, "DERIVATION")["attribution"] == "undefined")

# ============================================ C9: --stages ceiling -> unrun stage = UNKNOWN
print("== C9: the stage ceiling records UNRUN stages and the verdict is never PASS")
w = World("c9")
recs = w.run(obj=w.make_obj("CEIL-2", lanes=[dict(LANE_B),
                                             lane_a("artifacts/HELLO.COM",
                                                    fr.sha256_file(w.artifact))]),
             host=w.host(pli80_run=w.pli80_run), stage_ceiling=["SOURCE", "DERIVATION"])
recB, recA = lane_recs(recs, "B")[0], lane_recs(recs, "A")[0]
check("C9 all-never-PASS under a ceiling", all(r["verdict"] != "PASS" for r in recs))
check("C9 lane B: COMPILE/LINK/RUN/ASSERT unrun -> UNKNOWN",
      recB["verdict"] == "UNKNOWN" and statuses(recB)["COMPILE"] == "unrun" and
      statuses(recB)["LINK"] == "unrun" and statuses(recB)["RUN"] == "unrun" and
      statuses(recB)["ASSERT"] == "unrun")
check("C9 lane A: not-applicable does NOT launder -- the unrun RUN keeps UNKNOWN",
      recA["verdict"] == "UNKNOWN" and statuses(recA)["COMPILE"] == "not-applicable" and
      statuses(recA)["LINK"] == "not-applicable" and statuses(recA)["RUN"] == "unrun")
w = World("c9b")
rec = w.run(obj=w.make_obj("CEIL-B"), stage_ceiling=["SOURCE", "DERIVATION", "COMPILE"])[0]
check("C9 ceiling ends at COMPILE: LINK unrun (stage ceiling) -> UNKNOWN, never PASS",
      rec["verdict"] == "UNKNOWN" and statuses(rec)["LINK"] == "unrun" and
      stage_of(rec, "LINK")["witness"] == "stage ceiling")
# DOCUMENTED nuance (measured hop 4, recorded in LEARNINGS): the ceiling gates COMPILE/LINK/RUN;
# DERIVATION and ASSERT are evaluation stages the harness always runs -- a ceiling of
# SOURCE..RUN therefore yields an EVIDENCE-BACKED PASS because ASSERT DID execute. README 8 keys
# the law on stages that DID NOT run, so this is not laundering; the CLI help wording overpromises.
w = World("c9c")
rec = w.run(obj=w.make_obj("CEIL-RUN"), stage_ceiling=list(fr.STAGES[:-1]))[0]
check("C9 ceiling SOURCE..RUN: ASSERT actually RAN, so PASS is earned not laundered (README 8)",
      rec["verdict"] == "PASS" and statuses(rec)["ASSERT"] == "pass")

# ======================= C10: Lane A rc!=0 -> stdout DISCARDED; typed class; else UNKNOWN
print("== C10: Lane A failure paths -- audit 2.18 stdout law, typed classes, no laundering")
w = World("c10")
w.lane_a_result = (1, b"partial garbage that is NOT evidence", b"Fatal: unsupported BDOS function 21")
rec = w.run(obj=w.lane_a_obj("LA-FAIL"), host=w.host(pli80_run=w.pli80_run))[0]
check("C10 Lane A rc=1 + typed stderr -> RUN FAIL attribution emulator",
      rec["verdict"] == "FAIL" and statuses(rec)["RUN"] == "fail" and
      stage_of(rec, "RUN")["attribution"] == "emulator" and
      stage_of(rec, "RUN")["witness"] == "unsupported-bdos-function")
check("C10 the DISCARD is recorded: stdout saved AS discarded, NEVER as console.bin",
      open(os.path.join(w.edir(rec), "run.discarded-stdout.bin"), "rb").read() ==
      b"partial garbage that is NOT evidence" and
      not os.path.exists(os.path.join(w.edir(rec), "run.console.bin")))
check("C10 the detail names the audit law (2.18) and the stdout-not-evidence rule",
      "2.18" in stage_of(rec, "RUN")["detail"] and "DISCARDED" in stage_of(rec, "RUN")["detail"])
w = World("c10b")
w.lane_a_result = (1, b"x", b"some totally unknown message")
rec = w.run(obj=w.lane_a_obj("LA-UNCL"), host=w.host(pli80_run=w.pli80_run))[0]
check("C10 Lane A rc=1 UNCLASSIFIED -> UNKNOWN (attribution only from typed evidence)",
      rec["verdict"] == "UNKNOWN" and statuses(rec)["RUN"] == "unknown" and
      stage_of(rec, "RUN")["attribution"] == "undefined")
w = World("c10c")
w.lane_a_result = (2, b"x", b"program too large")           # typed text, but rc != 1: no class
rec = w.run(obj=w.lane_a_obj("LA-RC2"), host=w.host(pli80_run=w.pli80_run))[0]
check("C10 a typed message at rc!=1 is STILL unclassified -> UNKNOWN (README 9: evidence only)",
      rec["verdict"] == "UNKNOWN")

# ======================================= C11: --double-run determinism proof (audit 2.20)
print("== C11: --double-run compares the CONSOLE CAPTURE, not the transcript")
w = World("c11")
# transcripts DIFFER (wall-clock-style noise OUTSIDE the capture); captures are byte-EQUAL.
w.sessions_map = {"run": (0, RUN_OK_TR),
                  "run2": (0, ">>> boot 12:34:56\nD>TABLE00\r\r\nSUM=6\r\nN=2\r\n")}
rec = w.run(obj=w.make_obj("DR-EQ"), double_run=True)[0]
check("C11 equal captures keep PASS possible (double_run.equal)",
      rec["verdict"] == "PASS" and rec["double_run"]["equal"] is True)
check("C11 the compared object is the console capture (audit 2.20 law)",
      "console capture" in rec["double_run"]["compared"])
check("C11 the second run wrote run2.* evidence WITHOUT overwriting run.* (the _rname fix)",
      os.path.isfile(os.path.join(w.edir(rec), "run2.console.bin")) and
      os.path.isfile(os.path.join(w.edir(rec), "run.console.bin")) and
      open(os.path.join(w.edir(rec), "run.console.bin"), "rb").read() ==
      open(os.path.join(w.edir(rec), "run2.console.bin"), "rb").read())
w = World("c11b")
# raw bytes DIFFER (two spaces vs one INSIDE the line) while normalization COLLAPSES both to
# the SAME expected line -- the comparison is raw bytes, not the verdict:
w.sessions_map = {"run": (0, "D>TABLE00\r\r\nSUM=  6\r\nN=2\r\n"),
                  "run2": (0, "D>TABLE00\r\r\nSUM= 6\r\nN=2\r\n")}
exp = {"derivation": "reference.py:derive", "normalization": "collapse-spaces-v1",
       "console": ["SUM= 6", "N=2"]}
w.derive_result = (0, json.dumps(["SUM= 6", "N=2"]).encode())
rec = w.run(obj=w.make_obj("DR-DIFF", expected=exp), double_run=True)[0]
check("C11 differing raw captures (equal after normalization) -> UNKNOWN, NEVER PASS",
      rec["verdict"] == "UNKNOWN" and
      any(s["witness"] == "double-run-mismatch" for s in rec["stages"]) and
      rec["double_run"]["equal"] is False)
check("C11 the mismatch is a typed RUN record, attribution undefined",
      any(s["stage"] == "RUN" and s["status"] == "unknown" and
          s.get("attribution") == "undefined" and s["witness"] == "double-run-mismatch"
          for s in rec["stages"]))
w = World("c11c")
w.sessions_map = {"run": (0, RUN_OK_TR), "run2": (1, RUN_OK_TR)}   # second attempt TIMES OUT
rec = w.run(obj=w.make_obj("DR-R2FAIL"), double_run=True)[0]
check("C11 a second run that fails its witness -> verdict FAIL/UNKNOWN, never PASS",
      rec["verdict"] in ("UNKNOWN", "FAIL"))

# ============================== C13: the ONE rendering law -- BLOCKED/UNKNOWN are never PASS
print("== C13: rendering never launders BLOCKED/UNKNOWN into PASS (README 11)")
st = fr.Stage("LINK", "blocked", "host", "dependencies-absent", "no LINK.COM here")
line = fr.render_line("T-1", "B", "BLOCKED", "host", st)
check("C13 BLOCKED prints BLOCKED verbatim", "BLOCKED" in line and "PASS" not in line)
line = fr.render_line("T-1", "B", "UNKNOWN", "undefined",
                      fr.Stage("RUN", "unknown", "undefined", "no-console-anchor", ""))
check("C13 UNKNOWN prints UNKNOWN verbatim", "UNKNOWN" in line and "PASS" not in line)
line = fr.render_line("T-1", "B", "FAIL", "source",
                      fr.Stage("SOURCE", "fail", "source", "sha256-mismatch", "would-PASS trick"))
check("C13 the verdict FIELD is exactly the verdict (no padding/format path to PASS)",
      line.split()[3] == "FAIL")
check("C13 the PASS verdict field prints PASS",
      fr.render_line("T", "A", "PASS", "", None).split()[3] == "PASS")
check("C13 verdict_of: an unrun applicable stage anywhere => UNKNOWN (never PASS)",
      fr.verdict_of([fr.Stage("RUN", "pass"), fr.Stage("ASSERT", "unrun")])[0] == "UNKNOWN")
check("C13 verdict_of: not-applicable is neutral; all pass => PASS",
      fr.verdict_of([fr.Stage("COMPILE", "not-applicable"), fr.Stage("RUN", "pass"),
                     fr.Stage("ASSERT", "pass")])[0] == "PASS")
check("C13 verdict_of: the FIRST non-success decides (blocked before fail)",
      fr.verdict_of([fr.Stage("LINK", "blocked", "host"), fr.Stage("RUN", "fail")])[0] == "BLOCKED")
w = World("c13")
rec = w.run(obj=w.make_obj("REND-B"), host=w.host(compiler=os.path.join(w.root, "no-cc")))[0]
_st = stage_of(rec, "COMPILE")
line = fr.render_line(rec["test_id"], rec["lane"], rec["verdict"], rec["attribution"],
                      fr.Stage(_st["stage"], _st["status"], _st.get("attribution", ""),
                               _st.get("witness", ""), _st.get("detail", "")))
check("C13 a real BLOCKED record renders BLOCKED (stopped_at survives into the record)",
      "BLOCKED" in line and "PASS" not in line and rec["stopped_at"] == "COMPILE")

# =============================== compile-message attribution: the hop-3 measured shapes
print("== C-extra: COMPILE refusal attribution from the message's OWN shape (README 9)")
w = World("cc1")
w.compile_result = (2, b'Fatal error: exception Failure("codegen: X [TBD] unproven")\n')
rec = w.run(obj=w.make_obj("CC-CODEGEN"))[0]
check("codegen Failure -> FAIL attribution compiler",
      statuses(rec)["COMPILE"] == "fail" and
      stage_of(rec, "COMPILE")["attribution"] == "compiler" and rec["verdict"] == "FAIL")
w = World("cc2")
w.compile_result = (2, b"Fatal error: exception Pli80.Parser.Parse_error(_, \"expected ;\")\n")
rec = w.run(obj=w.make_obj("CC-PARSE"))[0]
check("Parser exception -> FAIL attribution source",
      stage_of(rec, "COMPILE")["attribution"] == "source" and rec["verdict"] == "FAIL")
w = World("cc3")
w.compile_result = (2, b"Fatal error: exception Sys_error(\"no perm\")\n")
rec = w.run(obj=w.make_obj("CC-SYS"))[0]
check("Sys_error -> BLOCKED attribution host (the host failed, not the program)",
      statuses(rec)["COMPILE"] == "blocked" and rec["verdict"] == "BLOCKED")
w = World("cc4")
w.compile_result = (2, b"some gibberish nobody recognizes\n")
rec = w.run(obj=w.make_obj("CC-GIB"))[0]
check("an untyped refusal keeps attribution `undefined' (never narrowed)",
      stage_of(rec, "COMPILE")["attribution"] == "undefined" and rec["verdict"] == "FAIL")
w = World("cc5")
w.compile_result = (subprocess.TimeoutExpired(cmd="x", timeout=1), b"")
rec = w.run(obj=w.make_obj("CC-TO"))[0]
check("compile wall-clock -> FAIL witness timeout, attribution undefined ([C308] class)",
      stage_of(rec, "COMPILE")["witness"] == "timeout" and rec["verdict"] == "FAIL")


class _NoRel(World):
    def subprocess_run(self, argv, **kw):
        argv = list(argv)
        self.calls.append(argv)
        if argv[0] == self.cc:                      # rc=0 but NO .REL written
            return subprocess.CompletedProcess(argv, 0, b"", b"")
        return super().subprocess_run(argv, **kw)


w = _NoRel("cc7")
rec = w.run(obj=w.make_obj("CC-NOREL"))[0]
check("rc=0 with NO .REL written -> UNKNOWN (typed success evidence required; not PASS)",
      statuses(rec)["COMPILE"] == "unknown" and rec["verdict"] == "UNKNOWN")


class _EmptyRel(World):
    def subprocess_run(self, argv, **kw):
        argv = list(argv)
        self.calls.append(argv)
        if argv[0] == self.cc:                      # rc=0 but the .REL is ZERO bytes
            with open(argv[-1], "wb") as f:
                pass
            return subprocess.CompletedProcess(argv, 0, b"", b"")
        return super().subprocess_run(argv, **kw)


w = _EmptyRel("cc8")
rec = w.run(obj=w.make_obj("CC-EMPTYREL"))[0]
check("rc=0 with a ZERO-byte .REL -> UNKNOWN empty object, never PASS",
      stage_of(rec, "COMPILE")["witness"] == "empty object" and rec["verdict"] == "UNKNOWN")

# ==================================================== pure-law unit checks (the small gears)
print("== units: normalization / stream-split / witness tables / typed classifier")
check("normalize_v1 is the gate law verbatim: CRLF->LF, runs of SPACES collapse",
      fr.normalize_v1(b"A  B\r\nC\r\n") == b"A B\nC\n")
check("split_stream ignores ONE trailing empty element (the measured final \\n)",
      fr.split_stream("a\nb\n") == ["a", "b"])
check("split_stream does NOT ignore interior empties", fr.split_stream("a\n\nb") == ["a", "", "b"])
check("TERMINATION_WITNESS is the oracle/run.py exit-code law",
      fr.TERMINATION_WITNESS == {0: "done", 1: "timeout", 2: "sim-died"})
check("classify: codegen Failure -> compiler", fr.classify_compile_message(
    'Fatal error: exception Failure("codegen: [TBD]")') == "compiler")
check("classify: Bind -> source", fr.classify_compile_message(
    "Fatal error: exception Pli80.Bind.Bad(x)") == "source")
check("classify: Sys_error -> host", fr.classify_compile_message("Sys_error(oops)") == "host")
check("classify: anything else -> undefined", fr.classify_compile_message("boom") == "undefined")
check("_send_input encodes ^Z as \\x1a, newlines as \\r, backslashes escaped",
      fr._send_input("ab\\c\n^Z") == "ab\\\\c\\r\\x1a")
check("parse_stage_ceiling uppercases and rejects unknown stages",
      fr.parse_stage_ceiling("source,compile") == ["SOURCE", "COMPILE"])
try:
    fr.parse_stage_ceiling("SOURCE,NOPE")
    check("parse_stage_ceiling rejects an unknown stage", False)
except SystemExit:
    check("parse_stage_ceiling rejects an unknown stage (SystemExit)", True)

# ============================================================ CLI wiring (main, bounded)
print("== CLI: main() bounded smoke returns honest codes and renders honest verdicts")
w = World("cli")
obj = w.make_obj("CLI-B", caps=["AGG.ARRAY_1D_FIXED"])   # REAL ledger id (main reads real COVERAGE)
w.write_spec(obj)
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    rc = fr.main(["--spec-dir", w.spec_dir, "--tests", "CLI-B", "--stages", "SOURCE",
                  "--evidence", os.path.join(w.root, "cli-ev"), "--compiler", w.cc])
out = buf.getvalue()
check("CLI bounded (--stages SOURCE) rc=1: nothing PASSED", rc == 1)
check("CLI prints lane B UNKNOWN (unrun COMPILE), never a PASS verdict line",
      "  UNKNOWN" in out and not re.search(r"lane B  +PASS", out))
check("CLI prints the verdict census with PASS=0", re.search(r"verdicts: PASS=0", out) is not None)
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    rc = fr.main(["--spec-dir", os.path.join(w.root, "absent-dir"),
                  "--evidence", os.path.join(w.root, "cli-ev2")])
check("CLI missing spec dir -> rc=2 usage error", rc == 2)
# Lane A through the CLI with no runner supplied (env override points at an absent file):
w = World("cli2")
obj = w.lane_a_obj("CLI-A")
obj["capabilities"] = ["AGG.ARRAY_1D_FIXED"]
w.write_spec(obj)
env_save = os.environ.get("PLI80_RUN")
os.environ["PLI80_RUN"] = os.path.join(w.root, "definitely-absent")
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    rc = fr.main(["--spec-dir", w.spec_dir, "--tests", "CLI-A", "--stages", "SOURCE",
                  "--evidence", os.path.join(w.root, "cli-ev"), "--compiler", w.cc])
del os.environ["PLI80_RUN"]
if env_save:
    os.environ["PLI80_RUN"] = env_save
out = buf.getvalue()
check("CLI lane A bounded run renders UNKNOWN (RUN unrun), never PASS",
      "  UNKNOWN" in out and "lane A" in out and rc == 1 and
      not re.search(r"lane A  +PASS", out))

# ===================== C14 (step 7): the runner's stdout carries ONLY rendered records
# The measured leak (step 6 RESULTS section 3): `oracle/cpmwork.py Run.export()' ran cpmcp with
# check=False and NO capture, so an external cpmtools debug print ("len 128") inherited the
# harness's stdout and appeared AHEAD of the rendered record.  Two sides are pinned here:
# (a) the ROOT fix -- export()'s child stdio is redirected, verified on the source of the REAL
#     oracle module (no child is spawned by this suite, so this is a source-level pin, stated
#     honestly at its scope);
# (b) the DETECTOR -- the CLI's stdout grammar is CLOSED: every non-empty line is a record, an
#     `evidence:' line or the `verdicts:' census.  A simulated chatty child (a stub export that
#     prints) proves the detector is NOT vacuous: foreign chatter is caught.
print("== C14: runner stdout grammar is closed; cpmcp stdio redirection pinned")
import inspect  # noqa: E402
_ex = inspect.getsource(cpmwork.Run.export)
check("C14a cpmwork.Run.export redirects the cpmcp child's stdout (step-7 leak fix)",
      "stdout=subprocess.DEVNULL" in _ex and "stderr=subprocess.STDOUT" in _ex)
check("C14a the failure contract is UNCHANGED: export still returns the file+size bool",
      "ok = os.path.isfile(dst) and os.path.getsize(dst) > 0" in _ex and "return ok" in _ex)
check("C14a the Lane A fallback list is exactly the two MEASURED paths",
      fr.LANE_A_CANDIDATES == ("/home/john/pli/lab/_build/default/bin/main.exe",
                               "/home/john/pli/lab/_build/install/default/bin/pli80-run"))
check("C14a the FALSIFIED hop-5 name (dune public name + .exe) is nowhere in the list",
      not any(os.path.basename(c) == "pli80-run.exe" for c in fr.LANE_A_CANDIDATES))
_isf = fr.os.path.isfile
try:
    fr.os.path.isfile = lambda p: p == fr.LANE_A_CANDIDATES[1]
    check("C14a the resolver falls back to the install name when the fresh build is absent",
          fr.Host().pli80_run_path() == fr.LANE_A_CANDIDATES[1])
    fr.os.path.isfile = lambda p: False
    check("C14a with NEITHER candidate present the resolver returns '' (BLOCKED names it)",
          fr.Host().pli80_run_path() == "")
finally:
    fr.os.path.isfile = _isf

REC_RE = re.compile(r"^  \S+\s+lane [AB]\s+(PASS|FAIL|BLOCKED|UNKNOWN)\b")
EV_RE = re.compile(r"^evidence: ")
VD_RE = re.compile(r"^verdicts: PASS=\d+ +FAIL=\d+ +BLOCKED=\d+ +UNKNOWN=\d+$")


def stdout_violations(text):
    return [ln for ln in text.splitlines() if ln.strip()
            and not (REC_RE.match(ln) or EV_RE.match(ln) or VD_RE.match(ln))]


def cli_pass_run(evdir):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = fr.main(["--spec-dir", w.spec_dir, "--tests", "CLI-G",
                      "--stages", "SOURCE,DERIVATION,COMPILE,LINK,RUN,ASSERT",
                      "--evidence", os.path.join(w.root, evdir), "--compiler", w.cc],
                     host=w.host())
    return rc, buf.getvalue()


w = World("cli3")
g = w.make_obj("CLI-G", caps=["AGG.ARRAY_1D_FIXED"])
w.write_spec(g)
rc, out = cli_pass_run("cli3-ev")
check("C14b positive control at CLI level: the stubbed lane-B chain PASSes via main(host=)",
      rc == 0 and re.search(r"lane B  +PASS", out) is not None)
check("C14b the WHOLE stdout is rendered records only -- no foreign line",
      stdout_violations(out) == [])
_lines = out.splitlines()
check("C14b record/evidence/verdicts all present (the grammar is not vacuously empty)",
      any(REC_RE.match(l) for l in _lines) and any(EV_RE.match(l) for l in _lines)
      and any(VD_RE.match(l) for l in _lines))
# non-vacuity: make the stub child chatter on INHERITED stdout, exactly like the real cpmcp did.
_orig_export = FakeRun.export


def _chatty_export(self, drive, name, dest):
    print("len 128")                      # the step-6 measured leak string
    return _orig_export(self, drive, name, dest)


FakeRun.export = _chatty_export
try:
    rc2, out2 = cli_pass_run("cli3-ev-chatty")
finally:
    FakeRun.export = _orig_export
viol = stdout_violations(out2)
check("C14c the detector CATCHES inherited-child chatter (not vacuous)", viol == ["len 128"])
check("C14c a chatty child does not change the verdict or rc (it is noise, not evidence)",
      rc2 == 0 and re.search(r"lane B  +PASS", out2) is not None)

# ================= C15 (FS-01): the console-anchoring law -- final newline kept, prompt
# never captured, ambiguous cuts fail closed.  F1 (step6/RESULTS.md section 2): the old cut
# `(?=\nD>)' ate the LF of the program's last CRLF and left a lone CR in the capture.  The two
# directions are pinned here: VALID transcripts keep the program's final newline and stay PASS
# end-to-end; MALFORMED/AMBIGUOUS ones never launder into PASS.
print("== C15: FS-01 console extraction -- newline retained, prompt excluded, ambiguity closes")
# C15a positive: the measured real shape -- program ends CRLF, prompt follows immediately.
w = World("c15a")
w.sessions_map = {"run": (0, "D>TABLE00\r\r\nSUM=6\r\nN=2\r\nD>")}
rec = w.run(obj=w.make_obj("F1-PROMPT"))[0]
check("C15a valid prompt-terminated stream PASSes end-to-end (no F1 residue)",
      rec["verdict"] == "PASS" and statuses(rec)["RUN"] == "pass" and
      stage_of(rec, "ASSERT")["witness"] == "complete-stream match")
check("C15a the capture retains the program's FINAL newline",
      open(os.path.join(w.edir(rec), "run.console.bin"), "rb").read() == b"SUM=6\r\nN=2\r\n")
check("C15a no terminal lone \r survives into the normalized stream",
      not open(os.path.join(w.edir(rec), "ASSERT.console.norm.txt")).read().endswith("\r"))
# C15b: everything AFTER the prompt (stale echoes, cpmsim stats) is never captured and never
# hides output -- the cut sits exactly at the first prompt byte.
w = World("c15b")
w.sessions_map = {"run": (0, "D>TABLE00\r\r\nSUM=6\r\nN=2\r\nD>\r\r\nD>A:BYE\r\r\n"
                          "I/O ran for 4020 ms\r\n")}
rec = w.run(obj=w.make_obj("F1-TAIL"))[0]
check("C15b prompt and post-prompt transcript tail stay OUT of the capture",
      rec["verdict"] == "PASS" and
      open(os.path.join(w.edir(rec), "run.console.bin"), "rb").read() == b"SUM=6\r\nN=2\r\n")
# C15c ambiguous: the prompt arrives with NO newline separating it from the program's last
# bytes -- program end and prompt start are inseparable; the harness must refuse to guess.
w = World("c15c")
w.sessions_map = {"run": (0, "D>TABLE00\r\r\nSUM=6\r\nN=2D>")}
rec = w.run(obj=w.make_obj("F1-AMBIG"))[0]
check("C15c prompt glued to the last line -> RUN UNKNOWN console-terminator-ambiguous",
      rec["verdict"] == "UNKNOWN" and statuses(rec)["RUN"] == "unknown" and
      stage_of(rec, "RUN")["witness"] == "console-terminator-ambiguous" and
      rec["attribution"] == "undefined")
check("C15c ASSERT never evaluates an ambiguous capture (chain stops at RUN)",
      statuses(rec)["ASSERT"] == "unrun")
check("C15c the suspect capture is kept as evidence, unmodified",
      open(os.path.join(w.edir(rec), "run.console.ambiguous.bin"), "rb").read()
      == b"SUM=6\r\nN=2")
# C15d truncated transcript (no prompt): the old F1 residue (lone CR at end) is NOT silently
# completed into a newline -- UNKNOWN, never PASS, never fabricated.
w = World("c15d")
w.sessions_map = {"run": (0, "D>TABLE00\r\r\nSUM=6\r\nN=2\r")}
rec = w.run(obj=w.make_obj("F1-TRUNC"))[0]
check("C15d truncated transcript ending in a lone CR -> UNKNOWN (no newline invented)",
      rec["verdict"] == "UNKNOWN" and
      stage_of(rec, "RUN")["witness"] == "console-terminator-ambiguous")
# C15e the complete-stream law is NOT weakened by the fix: an extra line before the prompt
# still FAILs, and it is still captured (nothing hidden by the new cut).
w = World("c15e")
w.sessions_map = {"run": (0, "D>TABLE00\r\r\nSUM=6\r\nN=2\r\nEXTRA\r\nD>")}
rec = w.run(obj=w.make_obj("F1-EXTRA"))[0]
check("C15e extra output line before the prompt still FAILs the complete-stream law",
      rec["verdict"] == "FAIL" and statuses(rec)["ASSERT"] == "fail" and
      "extra lines" in stage_of(rec, "ASSERT")["detail"])
check("C15e the extra line survives INTO the capture (the fix hides nothing)",
      open(os.path.join(w.edir(rec), "run.console.bin"), "rb").read()
      == b"SUM=6\r\nN=2\r\nEXTRA\r\n")
# C15f doubled-CRLF terminator (echo-doubling shape): classified, but the residue still FAILs
# the stream law -- fail closed, never laundered to PASS.
w = World("c15f")
w.sessions_map = {"run": (0, "D>TABLE00\r\r\nSUM=6\r\nN=2\r\r\nD>")}
rec = w.run(obj=w.make_obj("F1-DOUBLE"))[0]
check("C15f doubled-CRLF terminator -> ASSERT FAIL (lone \r residue survives normalization)",
      rec["verdict"] == "FAIL" and statuses(rec)["ASSERT"] == "fail")
# C15g the `I/O ran' alternative terminator (cpmsim tail without a prompt) still works and
# keeps the program's final newline.
w = World("c15g")
w.sessions_map = {"run": (0, "D>TABLE00\r\r\nSUM=6\r\nN=2\r\nI/O ran for 4020 ms\r\n")}
rec = w.run(obj=w.make_obj("F1-IORAN"))[0]
check("C15g I/O-ran terminator: region cut before the tail, final newline kept",
      rec["verdict"] == "PASS" and
      open(os.path.join(w.edir(rec), "run.console.bin"), "rb").read() == b"SUM=6\r\nN=2\r\n")

# ================= C16 (FC-01 hop 3): the "" blank-line entry -- schema acceptance AND the
# ASSERT semantics it earns.  The framing law [C352] puts real blank lines at stream start
# (first-statement PUT SKIP) and, after a final bare PUT SKIP, at stream end (unconditional
# exit CRLF).  Complete-stream law is NOT weakened: an extra or missing blank still FAILs.
print("== C16: blank-line entries -- schema \"\" accepted; ASSERT exact-blank semantics; "
      "complete-stream law NOT weakened ([C352])")
wsch = World("c16sch")
for pos, con in (("leading", ["", "SUM=6", "N=2"]),
                 ("interior", ["SUM=6", "", "N=2"]),
                 ("trailing", ["SUM=6", "N=2", ""])):
    obj = wsch.make_obj("BLK-%s" % pos[:4].upper())
    obj["expected"]["console"] = list(con)
    probs = fr.validate_spec(obj, basename=obj["id"], coverage=COV)
    check("C16a schema accepts a %s \"\" blank-line entry" % pos, probs == [])
for label, con, want in (("non-string entry", ["SUM=6", 7], "must be strings"),
                         ("bare '!' entry", ["!"], 'bare "!"'),
                         ("null entry", [None], "must be strings")):
    obj = wsch.make_obj("BLK-BAD")
    obj["expected"]["console"] = list(con)
    probs = fr.validate_spec(obj, basename=obj["id"], coverage=COV)
    check("C16b schema still rejects %s" % label, any(want in p for p in probs))
obj = wsch.make_obj("BLK-EMPTY")
obj["expected"]["console"] = []
check("C16b the empty-LIST rule is UNCHANGED (\"\" entries do not relax it)",
      any("non-empty array" in p for p in fr.validate_spec(obj, basename=obj["id"],
                                                            coverage=COV)))


def blank_case(tag, want, tr, expect_pass, label):
    w = World(tag)
    w.derive_result = (0, json.dumps(want).encode())
    w.sessions_map = {"run": (0, tr)}
    exp = {"derivation": "reference.py:derive", "normalization": "collapse-spaces-v1",
           "console": list(want)}
    rec = w.run(obj=w.make_obj(tag.upper(), expected=exp))[0]
    st = stage_of(rec, "ASSERT")
    check("C16c %s -> verdict %s (witness %r)" % (label, "PASS" if expect_pass else "FAIL", 
                                                  st["witness"] if st else "-"),
          rec["verdict"] == ("PASS" if expect_pass else "FAIL") and
          statuses(rec)["ASSERT"] == ("pass" if expect_pass else "fail"))
    return w, rec


# Measured shapes (FCPS3 at start, FCPS1 at end): the blank lines are REAL stream content.
w, rec = blank_case("c16lead", ["", "SUM=6", "N=2"],
                    "D>TABLE00\r\r\n\r\nSUM=6\r\nN=2\r\nD>", True,
                    "leading blank expected and present ([C352] FCPS3 shape)")
check("C16c the leading CRLF survives into the capture, prompt never",
      open(os.path.join(w.edir(rec), "run.console.bin"), "rb").read()
      == b"\r\nSUM=6\r\nN=2\r\n")
w, rec = blank_case("c16trail", ["SUM=6", "N=2", ""],
                    "D>TABLE00\r\r\nSUM=6\r\nN=2\r\n\r\nD>", True,
                    "trailing blank expected and present ([C352] FCPS1 shape)")
check("C16c the exit-chain double CRLF is captured verbatim (no laundering)",
      open(os.path.join(w.edir(rec), "run.console.bin"), "rb").read()
      == b"SUM=6\r\nN=2\r\n\r\n")
# The complete-stream law is NOT weakened by the new representation: blanks are lines too.
blank_case("c16extra", ["SUM=6", "N=2"],
           "D>TABLE00\r\r\nSUM=6\r\n\r\nN=2\r\nD>", False,
           "UNEXPECTED interior blank still FAILs (extra line)")
blank_case("c16missing", ["", "SUM=6", "N=2"],
           "D>TABLE00\r\r\nSUM=6\r\nN=2\r\nD>", False,
           "expected leading blank MISSING from the stream still FAILs")
blank_case("c16ws", ["SUM=6", "", "N=2"],
           "D>TABLE00\r\r\nSUM=6\r\n \r\nN=2\r\nD>", False,
           "a whitespace-only line is NOT an exact blank line (collapse-spaces-v1 keeps ' ')")
# "" and '!text' coexist: the negative entry still asserts absence.
w = World("c16neg")
want = ["", "SUM=6", "N=2", "!BOOM"]
w.derive_result = (0, json.dumps(want).encode())
w.sessions_map = {"run": (0, "D>TABLE00\r\r\n\r\nSUM=6\r\nN=2\r\nD>")}
rec = w.run(obj=w.make_obj("C16NEG", expected={"derivation": "reference.py:derive",
                                               "normalization": "collapse-spaces-v1",
                                               "console": list(want)}))[0]
check("C16d blank-line + negative entries compose (PASS, negative witnessed)",
      rec["verdict"] == "PASS" and
      "+1 negative(s)" in stage_of(rec, "ASSERT")["detail"])
w = World("c16neg2")
want = ["SUM=6", "N=2", "!\r"]  # '!text' with text after the bang; absence holds
w.derive_result = (0, json.dumps(want).encode())
w.sessions_map = {"run": (0, "D>TABLE00\r\r\nSUM=6\r\nN=2\r\nD>")}
rec = w.run(obj=w.make_obj("C16NEG2", expected={"derivation": "reference.py:derive",
                                                "normalization": "collapse-spaces-v1",
                                                "console": list(want)}))[0]
check("C16e bare-! rejection at schema level does not disturb '!text' handling",
      rec["verdict"] == "PASS")

# --------------------------------------------------------------------------- summary
print()
if FAILED:
    print("%d CHECK(S) FAILED out of %d:" % (len(FAILED), TOTAL))
    for f in FAILED:
        print("  - " + f)
    sys.exit(1)
print("all %d functional_runner hostile checks passed (evidence kept under %s)"
      % (TOTAL, TMP))
sys.exit(0)
