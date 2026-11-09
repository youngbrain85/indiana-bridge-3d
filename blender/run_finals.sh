#!/usr/bin/env bash
# Build, render (final quality), export and verify every bridge. Resumable: existing renders are skipped.
#   bash blender/run_finals.sh [ids...]            default: 07620 41750 19027
# Needs: python3 with bpy; optional gltfpack on PATH or in $GLTFPACK for the compressed viewer model.
set -u
cd "$(dirname "$0")"
ROOT=$(cd .. && pwd)
IDS=${*:-"07620 41750 19027"}
GLTFPACK=${GLTFPACK:-$(command -v gltfpack || true)}
export RENDER_SKIP_EXISTING=1
for id in $IDS; do
  folder=$(python3 -c "import bridge_gen as b; print(b.BRIDGES['$id']['folder'])" 2>/dev/null | tail -1)
  echo "=== $id ($folder)"
  python3 bridge_gen.py --build "$id" 2>&1 | grep -v CUEW | tail -2
  python3 bridge_gen.py --render "$id" final 2>&1 | grep -E "^[a-z]+: [0-9]+s|skip|Error|Traceback"
  mkdir -p "$ROOT/bridges/$folder/renders" "$ROOT/bridges/$folder/model"
  cp out/"$id"/renders_final/*.png "$ROOT/bridges/$folder/renders/"
  python3 bridge_gen.py --export "$id" 2>&1 | grep -E "exported|Error|Traceback"
  python3 bridge_gen.py --export "$id" --lite 2>&1 | grep -E "exported|Error|Traceback"
  lite="$ROOT/bridges/$folder/model/bridge_${id}_lite.glb"
  if [ -n "$GLTFPACK" ] && [ -f "$lite" ]; then
    "$GLTFPACK" -i "$lite" -o "${lite%.glb}_packed.glb" -cc -kn -km -vp 14 -vt 12 -noq && mv "${lite%.glb}_packed.glb" "$lite" && echo "packed $(du -h "$lite" | cut -f1)"
  fi
done
cd "$ROOT" && python3 tools/make_viewer_config.py 2>&1 | grep -v CUEW
bash tools/run_checks.sh
