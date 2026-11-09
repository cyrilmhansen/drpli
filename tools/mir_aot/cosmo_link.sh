#!/bin/sh
# cosmo_link.sh — reproducible Cosmopolitan static-link recipe (E2E-54/P1-mC,
# PLAN §P1-mC.5 steps 2 and 4).  A slice tool; NOT part of the historical gate.
#
# WHAT IT DOES
#   Links objects and/or C sources into a PLAIN STATIC LINUX x86-64 ELF with the
#   PINNED Cosmopolitan toolchain, driving the RAW architecture compiler
#   bin/x86_64-linux-cosmo-gcc with the exact flag set that the official wrapper
#   bin/x86_64-unknown-cosmo-cc records in its own BUILDLOG (captured VERBATIM on
#   2026-11-09; see LEARNINGS § "E2E-54/P1-mC hop 2").  There is NO APE step: no
#   fixupobj, no objcopy/zipcopy, no .com/.exe conversion, no launcher.  The output
#   begins with 0x7f 'ELF' and has no PT_INTERP and no dynamic section — the runner
#   tools/mir_aot_cosmo_test.py verifies that on every passing executable.
#
# WHY THE LOADER
#   Every program in the distribution (gcc, cc1, collect2, as, ld.bfd) is an APE
#   file ('MZ' at offset 0).  This host registers binfmt_misc DOSWin, which claims
#   MZ files with wine; the wrapper path additionally execs .ape helper tools and
#   measured over 90 s per link (PLAN §P1-mC.1).  Launching the raw compiler
#   through the distribution's OWN native ELF loader bin/ape-x86_64.elf needs no
#   system change and measured ~1 s, producing a BYTE-IDENTICAL artifact (measured
#   both ways).  COSMO_LOADER=0 reproduces the direct (host-binfmt) route.
#
# USAGE
#   sh tools/mir_aot/cosmo_link.sh --toolchain
#   sh tools/mir_aot/cosmo_link.sh <mode> <out-exe> -- <inputs...> [-DENTRY=.. -DEXPECTED=..]
#     mode          optlinux | tiny | dbg   (lib/<mode> plus that mode's own flags)
#     COSMO_ROOT    toolchain root, default <repo>/build/p1mc-deps (git-ignored)
#     COSMO_LOADER  1 (default) | 0         via bin/ape-x86_64.elf, or exec direct
#     COSMO_TIMEOUT seconds, default 120    (operator time constraint)
#
# It NEVER downloads anything and NEVER substitutes another compiler: a missing or
# incomplete toolchain is a LOUD blocker naming the pinned acquisition.
set -u

root=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd) || exit 1
COSMO=${COSMO_ROOT:-$root/build/p1mc-deps}
LOADER_MODE=${COSMO_LOADER:-1}
TMO=${COSMO_TIMEOUT:-120}
ZIP_NAME=cosmocc-4.0.2.zip
ZIP_SHA256=85b8c37a406d862e656ad4ec14be9f6ce474c1b436b9615e91a55208aced3f44

blocker() {
  echo "cosmo_link: BLOCKER: $1" >&2
  echo "  pinned acquisition: $ZIP_NAME (official release 4.0.2, GCC 14.1.0)" >&2
  echo "  sha256 $ZIP_SHA256" >&2
  echo "  -> extract into $COSMO (git-ignored dependency directory)" >&2
  exit 1
}

case "$COSMO" in
  *" "*) blocker "toolchain root must not contain spaces (the recipe splits flag words)" ;;
esac
[ -d "$COSMO" ] || blocker "Cosmopolitan toolchain root ABSENT at $COSMO"

CC="$COSMO/bin/x86_64-linux-cosmo-gcc"
LOADER="$COSMO/bin/ape-x86_64.elf"
[ -f "$CC" ] || blocker "raw compiler $CC missing"
[ -f "$LOADER" ] || blocker "native APE loader $LOADER missing"

if [ "${1:-}" = "--toolchain" ]; then
  echo "cosmo_root=$COSMO"
  echo "loader=$LOADER"
  echo "raw_compiler=$CC"
  if [ -f "$COSMO/$ZIP_NAME" ]; then
    have=$(sha256sum "$COSMO/$ZIP_NAME" | cut -d' ' -f1)
    echo "archive=$ZIP_NAME size=$(wc -c < "$COSMO/$ZIP_NAME") sha256=$have"
    [ "$have" = "$ZIP_SHA256" ] || blocker "archive $ZIP_NAME hash does NOT match the pin"
  else
    echo "archive=absent (extracted tree only; the pin lives in PLAN §P1-mC.1)"
  fi
  "$LOADER" "$CC" --version 2>/dev/null | head -1
  exit $?
fi

[ $# -ge 3 ] || {
  echo "usage: cosmo_link.sh <mode> <out-exe> -- <inputs...> [-DENTRY=.. -DEXPECTED=..]" >&2
  exit 2
}
MODE=$1
OUT=$2
shift 2
[ "${1:-}" = "--" ] && shift
case "$MODE" in
  optlinux|tiny|dbg) LIB="$COSMO/x86_64-linux-cosmo/lib/$MODE" ;;
  *) blocker "unknown mode '$MODE' (optlinux|tiny|dbg; -mtinylinux does NOT exist in 4.0.2)" ;;
esac
for f in crt.o ape-no-modify-self.o libcosmo.a ape.lds; do
  [ -f "$LIB/$f" ] || blocker "mode library $LIB/$f missing"
done
[ -f "$COSMO/include/stdio.h" ] || blocker "Cosmopolitan headers missing ($COSMO/include)"
[ -f "$COSMO/include/libc/integral/normalize.inc" ] || blocker "normalize.inc missing"

# ---- the recipe, mode by mode (unquoted expansion is intentional; no spaces) ----
BASE="-D__COSMOPOLITAN__ -D__COSMOCC__ -include libc/integral/normalize.inc"
BASE="$BASE -fportcosmo -fno-semantic-interposition -Wno-implicit-int -mno-tls-direct-seg-refs"
CPP="-fno-pie -nostdinc -isystem $COSMO/include"
case "$MODE" in
  optlinux) CPP="$CPP -mred-zone" ;;
  *)        CPP="$CPP -mno-red-zone" ;;
esac
case "$MODE" in
  optlinux) ;;
  tiny|dbg) BASE="$BASE -fno-optimize-sibling-calls -mno-omit-leaf-frame-pointer -fno-schedule-insns2" ;;
esac
LD="-static -no-pie -nostdlib -fuse-ld=bfd -Wl,-z,noexecstack"
LD="$LD -L$LIB -L$COSMO/x86_64-linux-cosmo/lib -Wl,-T,$LIB/ape.lds"
LD="$LD -Wl,-z,common-page-size=4096 -Wl,-z,max-page-size=16384 -lcosmo"
PRECIOUS="-fno-omit-frame-pointer"
CRT="$LIB/ape-no-modify-self.o $LIB/crt.o"

run() {
  if command -v timeout >/dev/null 2>&1; then
    timeout "$TMO" "$@"
  else
    "$@"
  fi
}

if [ "$LOADER_MODE" = 1 ]; then
  # shellcheck disable=SC2086
  run "$LOADER" "$CC" $BASE $CPP $CRT "$@" -o "$OUT" $LD $PRECIOUS
else
  # shellcheck disable=SC2086
  run "$CC" $BASE $CPP $CRT "$@" -o "$OUT" $LD $PRECIOUS
fi
