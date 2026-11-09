#!/usr/bin/env bash
# Runs every verification that does not need Blender. Exit code: 0 all PASS, 1 a dimension check FAILED or sheets missing.
set -u
cd "$(dirname "$0")/.."
status=0
echo "== dimensional checks (GLB vs bridge.json)"
python3 tools/verify_model.py --all --md verification_report.md || status=$?
echo "== render vs photo comparison sheets"
python3 tools/compare_photos.py --all || status=1
echo "== deliverables"
for d in bridges/*/; do
  id=$(basename "$d" | cut -c1-5)
  for f in "model/bridge_${id}.glb" "renders" "verification/dimension_report.md" "verification/compare_sheet.jpg"; do
    [ -e "$d$f" ] && echo "ok      $d$f" || { echo "MISSING $d$f"; status=1; }
  done
done
echo "exit $status"
exit $status
