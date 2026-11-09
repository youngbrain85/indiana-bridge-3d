# Review — <bridge name> (<folder>)

Reviewer: <agent / person>, <date>, model: <e.g. GPT-5 via Codex>

## 1. Dimensional checks (`tools/verify_model.py`)

Summary line from `verification/dimension_report.md`: `PASS n · FAIL n · WARN n · INFO n`

| Failed check | Expected | Model | Cause | Fix |
|---|---|---|---|---|
| | | | | |

## 2. bridge.json vs report_text.txt

| Field | bridge.json | Report | Where in the report | Verdict |
|---|---|---|---|---|
| structure type (43) | | | | |
| spans (45/46, span table) | | | | |
| structure length (49) | | | | |
| deck width (52) / roadway (51) | | | | |
| skew (34) | | | | |
| clearances (10/54) | | | | |
| substructure units / piles / columns | | | | |
| girders / bearings / joints / railing | | | | |
| channel profile (water below deck) | | | | |

Values not found in the report: …

## 3. Render vs photo pairs (`verification/compare_*.jpg`)

| View | Photo | Verdict (PASS / MINOR / MAJOR) | Reasoning |
|---|---|---|---|
| elevation | | | |
| … | | | |

## 4. Fix suggestions

- `blender/bridge_gen.py` → `<function>`: …
- `bridges/<folder>/bridge.json` → `<field>`: …

## 5. Overall verdict

ACCEPT / ACCEPT WITH MINOR FIXES / REWORK — one paragraph.
