#!/bin/sh
# build_native.sh — reproducible P1-m0 native-emitter build (PLAN §P1-m0.5).
#
# 1. Verify the pinned laboratory checkout EXACTLY (lab ccc92c5c650b4385b4f42c9493725ae1415ab2e5,
#    submodule madc f541a7a54624869e29b01f2f30b174bc0329eea5).  Absent or moved checkout:
#    FAIL LOUD naming the exact blocker (brief §11).  NO re-pin, NO network, NO C-only
#    substitution, and the lab tree is never modified or advanced.
# 2. Build libmir.a strictly OUT-OF-TREE into build/p1m0-deps/mir-obj (measured law D-2:
#    BUILD_DIR must pre-exist for the libmir.a goal when invoked from another cwd).
# 3. Compile the emitter: gcc -O2 -Wall -Wextra -Werror against the pinned headers/archive.
#
# All outputs live under the ignored build/ tree; the lab stays git-clean (verified here
# after every mutating step; falsifier T7 re-checks at close).
set -u

LAB=thirdparty/mir-madc-aot-lab
LAB_PIN=ccc92c5c650b4385b4f42c9493725ae1415ab2e5
MADC_PIN=f541a7a54624869e29b01f2f30b174bc0329eea5

root=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd) || exit 1
cd "$root" || exit 1

if [ ! -d "$LAB" ]; then
  echo "build_native: BLOCKER: pinned laboratory checkout ABSENT at $LAB" >&2
  echo "  (expected lab commit $LAB_PIN with submodule madc at $MADC_PIN;" >&2
  echo "   acquisition is a separate pre-registered step — no network here)." >&2
  exit 1
fi

head=$(git -C "$LAB" rev-parse HEAD) || { echo "build_native: BLOCKER: $LAB is not a git checkout" >&2; exit 1; }
if [ "$head" != "$LAB_PIN" ]; then
  echo "build_native: BLOCKER: laboratory pin MOVED: $LAB HEAD=$head, expected $LAB_PIN" >&2
  exit 1
fi
madc_head=$(git -C "$LAB/madc" rev-parse HEAD 2>/dev/null) || {
  echo "build_native: BLOCKER: submodule $LAB/madc absent or not a git checkout" >&2; exit 1; }
if [ "$madc_head" != "$MADC_PIN" ]; then
  echo "build_native: BLOCKER: madc submodule pin MOVED: $LAB/madc HEAD=$madc_head, expected $MADC_PIN" >&2
  exit 1
fi
if [ -n "$(git -C "$LAB" status --porcelain)" ]; then
  echo "build_native: BLOCKER: laboratory tree DIRTY (must stay clean, falsifier T7)" >&2
  exit 1
fi

MIRSRC="$LAB/madc/third_party/mir"
[ -f "$MIRSRC/GNUmakefile" ] || { echo "build_native: BLOCKER: $MIRSRC/GNUmakefile missing (submodule content absent)" >&2; exit 1; }
[ -f "$MIRSRC/mir.h" ] || { echo "build_native: BLOCKER: $MIRSRC/mir.h missing" >&2; exit 1; }
[ -f "$MIRSRC/mir-gen.h" ] || { echo "build_native: BLOCKER: $MIRSRC/mir-gen.h missing" >&2; exit 1; }

OBJ=$root/build/p1m0-deps/mir-obj
mkdir -p "$OBJ" || { echo "build_native: BLOCKER: cannot create $OBJ (D-2: BUILD_DIR must pre-exist)" >&2; exit 1; }

( cd "$MIRSRC" && make -f GNUmakefile BUILD_DIR="$OBJ" "$OBJ/libmir.a" -j"$(nproc)" ) \
  || { echo "build_native: BLOCKER: libmir.a out-of-tree build failed" >&2; exit 1; }
[ -f "$OBJ/libmir.a" ] || { echo "build_native: BLOCKER: $OBJ/libmir.a not produced" >&2; exit 1; }

[ -n "$(git -C "$LAB" status --porcelain)" ] && {
  echo "build_native: BLOCKER: laboratory tree became DIRTY during the build" >&2; exit 1; }

gcc -O2 -Wall -Wextra -Werror -I"$MIRSRC" tools/mir_aot/mir2o.c "$OBJ/libmir.a" \
    -ldl -lm -o "$root/build/p1m0-deps/mir2o" \
  || { echo "build_native: BLOCKER: mir2o.c compilation/link failed" >&2; exit 1; }

[ -n "$(git -C "$LAB" status --porcelain)" ] && {
  echo "build_native: BLOCKER: laboratory tree became DIRTY during the emitter build" >&2; exit 1; }

echo "build_native: OK — emitter at build/p1m0-deps/mir2o (lab $LAB_PIN, madc $MADC_PIN, lib out-of-tree)"
