# Ready-to-paste prompt for OpenAI Codex (or any GPT-based coding agent)

Open the repository in Codex and paste the text below. It assumes the agent can run shell commands and look at images
(the comparison sheets are JPEGs). `AGENTS.md` in the repository root is picked up automatically by Codex and carries
the detailed instructions, so the prompt only needs to state the job.

```
Read AGENTS.md first.

Task: independently verify the three bridge models in this repository against the INDOT inspection reports they
were built from, then write one REVIEW.md per bridge in bridges/<folder>/verification/.

1. Run `bash tools/run_checks.sh`. It must end with "exit 0". Paste the summary line of every
   dimension_report.md in your review. If anything FAILs, locate the cause in blender/bridge_gen.py or
   bridges/<folder>/bridge.json, fix it, rebuild (`cd blender && python3 bridge_gen.py --build <id>`), re-run
   `python3 tools/verify_model.py <id> --blend`, and explain the fix. If bpy cannot be installed in your
   sandbox, say so and verify the committed GLBs only.

2. Cross-check bridges/<folder>/bridge.json against bridges/<folder>/report_text.txt: structure type (NBI 43/44),
   number and length of spans (45/46 and the span table), structure length (49), deck and roadway widths (51/52),
   skew (34), clearances (10/54), element quantities (piles, columns, girders, bearings, joints, railings) and the
   channel profile. List every value you could not find in the report, and every value that disagrees.

3. Open bridges/<folder>/verification/compare_sheet.jpg (or each compare_<view>.jpg). For every render/photo pair
   decide PASS / MINOR / MAJOR against the "CHECK" line printed on the sheet and give one sentence of reasoning:
   structure type, member counts and proportions, parapet shape, pier type, what is under the bridge, materials
   and colours, vegetation and season.

4. Write bridges/<folder>/verification/REVIEW.md with: the dimension-check summary, the per-pair verdicts, the
   data discrepancies from step 2, and concrete fix suggestions (file + function + what to change). Use English.
   Do not commit anything under blender/out/.

Finish with a short overall verdict per bridge: ACCEPT, ACCEPT WITH MINOR FIXES, or REWORK.
```

## What the agent gets

- `tools/verify_model.py` — pure-Python glTF reader; checks span stations, widths, skew, parapet height, support
  count, piles/columns/girders, water level and clearance against `bridge.json`. Exit 1 on any FAIL.
- `tools/compare_photos.py` — writes the render/photo sheets with the check text printed on them.
- `bridges/<folder>/report_text.txt` — the inspection report as text, so no PDF tooling is needed.
- `VERIFY.md` — the human checklist, keyed to photo numbers.

## Running locally on Windows (PowerShell)

```powershell
py -3.13 -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python tools\verify_model.py --all
python tools\compare_photos.py --all
cd blender; python bridge_gen.py --build 07620; python bridge_gen.py --render 07620 preview elevation
```
