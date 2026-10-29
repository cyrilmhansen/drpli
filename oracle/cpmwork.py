#!/usr/bin/env python3
"""cpmwork.py — filesystem-safety layer for the PL/I-80 oracle harness.

Pi runs WITHOUT a sandbox, so every destructive/overwriting filesystem
operation the oracle performs is funnelled through explicit, validated
guards here. Design rules (fail closed):

  * Two zones, both realpath-validated and symlink-free:
      - WORKSPACE: dedicated dir for *generated* disk images + scratch.
        All cpmsim/mkfs/cpmcp writes happen here, inside a per-run subdir.
      - OUTPUT: the golden/<tag> archive dir. Only NEW files are created;
        pre-existing files are never deleted and only overwritten when the
        caller passes an explicit allow_clobber flag.
  * The irreplaceable boot seeds (oracle/disks/drivea|driveb.dsk) are
        treated as READ-ONLY. Every run COPIES them into its own subdir, so
        cpmsim's read-write mount can never touch the originals.
  * No shell. Every external tool call is subprocess.run([...], shell=False)
        with an argv list; no string interpolation reaches a shell.
  * Names are validated against CP/M 8.3-safe charset (^[A-Za-z0-9_]{1,8}$)
        so a malicious/probe name cannot traverse or inject.
  * Symlinks are rejected for every path we read-from-write-to-create.

Deleting is only ever performed inside the workspace run dir this process
created, using os.remove on individual validated regular files -- never an
external `rm`, never outside the run dir.
"""
import os
import re
import shutil
import subprocess
import sys

FMT = "ibm-3740"
NAME_RE = re.compile(r"^[A-Za-z0-9_]{1,8}$")
# [E2E-41/P3b] This was `^([A-Za-z0-9_]{1,8})(?:\.([A-Za-z0-9_]{1,3})?)$' -- the `?' written
# INSIDE the group instead of after it, which makes the DOT mandatory and the extension optional,
# so an EXTENSIONLESS name never matched:
#   re.match(old, "OUT")     -> None      (measured, Python 3.14.8)
#   re.match(old, "OUT.DAT") -> match
# A defect in this guard, not a regex-engine quirk -- the same shape rejects `OUT' on every
# version.  It cost real evidence rather than only a message: E16D's own `title('E16OUT DAT')'
# creates the CP/M file `E16OUT' with NO extension (spec/lab-evidence/e2e41-p3/E16D-RUN.txt), and
# the export guard refused to copy it out of the run disk, so a program that had demonstrably
# written a file was reported as having written nothing.  CP/M's F8.3 grammar makes the whole
# `.EXT' optional, so the optional group now wraps both the dot and the extension; group 2 is
# still the extension when there is one, which is what check_f83() below reads.
# Reproduction: spec/lab-evidence/e2e41-p3/F83-REGEX.txt
F83_RE = re.compile(r"^([A-Za-z0-9_]{1,8})(?:\.([A-Za-z0-9_]{1,3}))?$")
# Explicit absolute tool paths; verified present & non-symlink on import.
TOOLS = {
    "mkfs.cpm": "/usr/bin/mkfs.cpm",
    "cpmcp": "/usr/bin/cpmcp",
    "cpmls": "/usr/bin/cpmls",
}


class SafetyError(Exception):
    """Raised whenever a guard refuses an operation. Never auto-recovered."""


def _tool(name):
    p = TOOLS[name]
    if os.path.islink(p):
        raise SafetyError(f"{name}: refusing symlinked tool {p}")
    if not os.path.isfile(p) or not os.access(p, os.X_OK):
        raise SafetyError(f"{name}: required tool {p} missing/not executable")
    return p


def _is_under(base, target):
    """True if realpath(target) is base or strictly inside realpath(base)."""
    base = os.path.realpath(base)
    target = os.path.realpath(target)
    return target == base or target.startswith(base + os.sep)


def _reject_symlink(path, label):
    """Reject if path OR any existing ancestor component is a symlink."""
    cur = os.path.abspath(path)
    while True:
        if os.path.islink(cur):
            raise SafetyError(f"{label}: symlink component refused: {cur}")
        parent = os.path.dirname(cur)
        if parent == cur:
            break
        cur = parent


def _require_dir_not_symlink(path, label):
    _reject_symlink(path, label)
    if os.path.exists(path) and not os.path.isdir(path):
        raise SafetyError(f"{label}: path exists but is not a dir: {path}")


def check_name(name):
    if not NAME_RE.match(name):
        raise SafetyError(
            f"illegal CP/M name {name!r} (want {NAME_RE.pattern})")
    return name.upper()


def check_f83(name):
    """Validate a CP/M F8.3 'BASE[.EXT]' token; return normalised form."""
    m = F83_RE.match(name)
    if not m:
        raise SafetyError(
            f"illegal CP/M F8.3 name {name!r} (want {F83_RE.pattern})")
    base, ext = m.group(1), m.group(2)
    return base.upper() + ("." + ext.upper() if ext else "")


class Workspace:
    """Validated root under which all generated disks/scratch live."""

    def __init__(self, root, seeds_dir):
        _reject_symlink(root, "workspace")
        _reject_symlink(seeds_dir, "seeds")
        rs = os.path.realpath(seeds_dir)
        if not os.path.isdir(rs):
            raise SafetyError(f"seeds dir missing: {rs}")
        self.seeds = rs
        os.makedirs(root, exist_ok=True)
        _reject_symlink(root, "workspace")
        self.root = os.path.realpath(root)
        # workspace must not be able to escape into the seeds dir
        if _is_under(self.root, self.seeds):
            raise SafetyError("seeds dir must not be inside workspace root")


class Run:
    """A single, uniquely-named subdirectory of the workspace.

    Owns drivea/b (copied seeds), drivec/d (fresh mkfs), and all cpmsim
    activity. Cleanup is scoped strictly to this dir.
    """

    def __init__(self, ws, tag):
        self.ws = ws
        tag = re.sub(r"[^A-Za-z0-9_.-]", "_", tag)
        # unique-per-run: take the first FREE run-<tag>-<seq>; never clobber/reuse.
        # [E2E-42/P2c] This used to be `if not os.path.exists(base): break' followed by
        # os.makedirs, which is a check-then-create window: two gate arms claiming the same tag
        # concurrently both saw the slot free and one then died in FileExistsError.  The gate's
        # slow arms are now run in parallel, so the CLAIM has to be the atomic operation --
        # makedirs(exist_ok=False) either creates the dir or loses the race, and losing means
        # taking the next slot.  Nothing about the guards changed: the symlink check still runs
        # before the claim, and a slot held by anyone else is still never reused or removed.
        seq = 0
        while True:
            base = os.path.join(self.ws.root, f"run-{tag}-{seq:03d}")
            if os.path.islink(base):
                raise SafetyError(f"run dir is a symlink, refusing: {base}")
            try:
                os.makedirs(base)
                break
            except FileExistsError:
                seq += 1
                if seq > 999:
                    raise SafetyError(f"too many run dirs for tag {tag!r}")
            except NotADirectoryError:
                raise SafetyError(f"run path is not a directory, refusing: {base}")
        self.dir = os.path.realpath(base)
        if not _is_under(self.ws.root, self.dir):
            raise SafetyError("run dir escaped workspace root")
        self.disks = self.dir  # cpmsim -d target

    # -- disk lifecycle --------------------------------------------------
    def _disk_path(self, drive):
        if len(drive) != 1 or not ("a" <= drive.lower() <= "z"):
            raise SafetyError(f"bad drive letter: {drive!r}")
        d = drive.lower()
        _reject_symlink(os.path.join(self.dir, f"drive{d}.dsk"), "disk")
        return os.path.join(self.dir, f"drive{d}.dsk")

    def seed(self, drive, seed_name):
        """Copy a read-only boot seed into the run dir (never touches seed)."""
        src = os.path.join(self.ws.seeds, seed_name)
        _reject_symlink(src, "seed")
        if not os.path.isfile(src):
            raise SafetyError(f"seed not found: {src}")
        dst = self._disk_path(drive)
        if os.path.exists(dst):
            raise SafetyError(f"seed dst already exists: {dst}")
        shutil.copyfile(src, dst)          # copy, never move/delete source
        return dst

    def mkfs(self, drive):
        """Create a FRESH empty disk. Refuses if target exists (no clobber)."""
        path = self._disk_path(drive)
        if os.path.exists(path):
            raise SafetyError(f"mkfs target exists (would clobber): {path}")
        subprocess.run([_tool("mkfs.cpm"), "-f", FMT, path],
                       shell=False, check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        if os.path.islink(path):
            raise SafetyError(f"mkfs produced a symlink?!: {path}")
        return path

    def import_local(self, disk_drive, local_path, on_disk):
        """Copy a host file onto a CP/M disk. Validates BOTH endpoints."""
        _reject_symlink(local_path, "import-src")
        if not os.path.isfile(local_path):
            raise SafetyError(f"import source not a regular file: {local_path}")
        rp = os.path.realpath(local_path)
        if not (_is_under(self.ws.seeds, rp) or _is_under(self.ws.root, rp)
                or _is_under(_proj_root(), rp)):
            raise SafetyError(f"import source outside allowed roots: {rp}")
        disk = self._disk_path(disk_drive)
        on_disk = check_f83(on_disk)
        # cpmcp uses 0:<name> target; pass the full 8.3 name via argv list
        subprocess.run([_tool("cpmcp"), "-f", FMT, disk,
                        rp, f"0:{on_disk}"],
                       shell=False, check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

    def export(self, disk_drive, on_disk, dst_dir, allow_clobber=False):
        """Copy a file off a CP/M disk into OUTPUT dst_dir (a new file)."""
        disk = self._disk_path(disk_drive)
        on_disk = check_f83(on_disk)
        _require_dir_not_symlink(dst_dir, "export-dir")
        base = os.path.basename(on_disk)
        dst = os.path.join(dst_dir, base)
        _reject_symlink(dst, "export-dst")
        if os.path.exists(dst) and not allow_clobber:
            raise SafetyError(
                f"export would overwrite pre-existing file: {dst}")
        subprocess.run([_tool("cpmcp"), "-f", FMT, disk,
                        f"0:{on_disk}", dst],
                       shell=False, check=False)
        ok = os.path.isfile(dst) and os.path.getsize(dst) > 0
        if not ok and os.path.exists(dst) and not allow_clobber:
            # we created an empty stub this run; remove only OUR new file
            if _is_under(dst_dir, os.path.realpath(dst)):
                os.remove(dst)
        return ok

    def ls(self, disk_drive):
        disk = self._disk_path(disk_drive)
        r = subprocess.run([_tool("cpmls"), "-l", "-f", FMT, disk],
                           shell=False, check=False,
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return r.stdout.decode("latin-1", "replace")

    def run_sim(self, sim, script, timeout, extra_env=None):
        # run.py is the pty wrapper; it finds the cpmsim binary via the
        # CPMSIM env var (its --sim default). We pass sim through env.
        run_py = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              "run.py")
        env = dict(os.environ)
        env["CPMSIM"] = sim
        if extra_env:
            env.update(extra_env)
        r = subprocess.run([sys.executable, run_py, "--disks", self.disks,
                            "--timeout", str(timeout), script],
                           shell=False, capture_output=True, env=env)
        return r.returncode, r.stdout.decode("latin-1")

    def cleanup(self):
        """Remove this run dir ONLY. Strictly scoped + symlink-guarded."""
        if not _is_under(self.ws.root, self.dir) or self.dir == self.ws.root:
            raise SafetyError("refusing to cleanup dir outside workspace")
        shutil.rmtree(self.dir)


def _proj_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Output:
    """A curated golden/<tag> archive directory.

    Golden dirs hold the acceptance baseline read by the parity gates, so
    they are protected independently from the scratch workspace:
      * dir must sit under the golden root, never a symlink;
      * creating into a PRE-EXISTING dir is refused unless allow_reuse;
      * individual file writes refuse to clobber an existing file unless
        allow_clobber (so `--tag probe38` cannot silently overwrite goldens).
    """

    def __init__(self, golden_root, tag, allow_reuse=False):
        _reject_symlink(golden_root, "golden-root")
        self.root = os.path.realpath(golden_root)
        os.makedirs(self.root, exist_ok=True)
        _reject_symlink(self.root, "golden-root")
        if not re.match(r"^[A-Za-z0-9_][A-Za-z0-9_.-]*$", tag):
            raise SafetyError(f"illegal golden tag {tag!r}")
        target = os.path.join(self.root, tag)
        _reject_symlink(target, "golden-tag")
        if not _is_under(self.root, os.path.realpath(target) if os.path.exists(target) else target):
            raise SafetyError("golden tag path escapes golden root")
        if os.path.exists(target) and not allow_reuse:
            raise SafetyError(
                f"golden dir exists; pass allow_reuse to add into it: {target}")
        os.makedirs(target, exist_ok=True)
        self.allow_clobber = allow_reuse
        self.dir = os.path.realpath(target)
        if not _is_under(self.root, self.dir):
            raise SafetyError("golden dir resolved outside root")

    def subdir(self, name):
        name = check_name(name)
        p = os.path.join(self.dir, name)
        _reject_symlink(p, "golden-sub")
        os.makedirs(p, exist_ok=True)
        return os.path.realpath(p)

    def path(self, subdir, fname):
        """Resolve an output file path with symlink + clobber guards.

        subdir is relative to this Output dir ('.' = the tag dir itself).
        """
        if subdir in (".", "", None):
            subdir = self.dir
        else:
            subdir = os.path.join(self.dir, subdir)
        _reject_symlink(subdir, "golden-sub")
        if not _is_under(self.dir, os.path.realpath(subdir)):
            raise SafetyError("output subdir outside golden dir")
        if os.sep in fname or ".." in fname:
            raise SafetyError(f"unsafe output filename {fname!r}")
        p = os.path.join(subdir, fname)
        _reject_symlink(p, "output-file")
        if os.path.exists(p) and not self.allow_clobber:
            raise SafetyError(f"refusing to overwrite existing output: {p}")
        return p

    def write(self, subdir, fname, data):
        p = self.path(subdir, fname)
        with open(p, "w") as f:
            f.write(data)
        return p
