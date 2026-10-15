#!/usr/bin/env bash
# Digital Research PL/I-80 research manuals. Downloads from their public archives.
# Run from any directory. Requires curl and python3 for content checks.
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
out="${1:-${here}/manuals}"
mkdir -p "$out"

fetch_pdf() {
  local dest="$1" subdir="$2" filename="$3" url tmp
  if [[ -s "$out/$dest" ]] && head -c 5 "$out/$dest" | grep -q '%PDF-'; then
    echo "EXISTS: $dest"
    return 0
  fi
  tmp="$out/.${dest}.part"
  rm -f "$tmp"
  for host in "https://www.bitsavers.org" "https://bitsavers.org" "https://bitsavers.trailing-edge.com"; do
    url="${host}/pdf/digitalResearch/${subdir}/${filename}"
    printf 'GET: %s\n' "$url"
    if curl -fL --connect-timeout 12 --max-time 150 --retry 2 --retry-delay 2 \
        -A 'Mozilla/5.0 (historical research)' -o "$tmp" "$url" &&
        [[ "$(head -c 5 "$tmp")" == '%PDF-'* ]]; then
      mv "$tmp" "$out/$dest"
      printf 'OK:  %s (%s bytes)\n' "$dest" "$(wc -c < "$out/$dest")"
      return 0
    fi
    rm -f "$tmp"
  done
  printf 'FAILED: %s (try links from SOURCES.md manually)\n' "$dest" >&2
  return 1
}

failed=0
fetch_pdf PL1-80_Language_Manual_Dec80.pdf pl1 PL1-80_Language_Manual_Dec80.pdf || failed=1
fetch_pdf PL1-80_Applications_Guide_Dec80.pdf pl1 PL1-80_Applications_Guide_Dec80.pdf || failed=1
fetch_pdf LINK-80_Operators_Guide_Dec80.pdf cpm LINK-80_Operators_Guide_Dec80.pdf || failed=1

(
  cd "$out"
  sha256sum ./*.pdf > SHA256SUMS 2>/dev/null || true
)

# Expected language manual checksum from Runes pass114 historical evidence.
if [[ -f "$out/PL1-80_Language_Manual_Dec80.pdf" ]]; then
  actual=$(sha256sum "$out/PL1-80_Language_Manual_Dec80.pdf" | awk '{print $1}')
  expected='85e09fc830a3520d2e5e24d051cdf74593b393b1851ee982196555e6435b848a'
  if [[ "$actual" == "$expected" ]]; then
    echo 'VERIFIED: Language Manual matches Runes pass114 PDF hash'
  else
    echo "NOTICE: Language Manual checksum differs from Runes pass114 copy: $actual"
    echo 'This may be a different revision, mirror or reprocessed PDF; verify content.'
  fi
fi
exit "$failed"
