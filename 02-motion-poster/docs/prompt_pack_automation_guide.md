# Banana Pro × Google Flow Lab One-Click Automation

## What it does

`run_banana_flow_prompt_pack.py` prepares the Banana Pro image prompts and the Google Flow Lab video prompts without calling any model. The script reads the two prompt files, validates the 20+20 count, checks the M/F/O/E distribution, tests image-video ID matching, scans the shared duration/aspect-ratio rules, exports each prompt as a standalone copy-ready `.txt` file, collects the guidelines and any optional generated assets, writes a manifest and a validation report, and finally builds a ZIP.

This is a deliberate safety boundary: the script does not log into Banana Pro or Google Flow Lab, does not run browser automation, does not start paid or quota-limited generation calls and does not store API keys. You generate the images in Banana Pro and the videos in Flow Lab; the script organizes the prompt pack before generation and the asset delivery after it.

## One command

Run the script in the folder that holds the prompts:

```bash
python3 run_banana_flow_prompt_pack.py \
  --source-dir . \
  --output-dir ./banana_flow_automation
```

When this command completes successfully, you get:

```text
banana_flow_automation/
├── prompts/
│   ├── visual/M01.txt ... E05.txt
│   └── video/M01.txt ... E05.txt
├── references/
│   ├── prompt_set_matrix.md
│   ├── flow_banana_prompt_guidelines.md
│   └── character_consistency_research.md
├── assets/                 # if --assets-dir is given
├── validation.json
├── run_config.json
├── DELIVERY_MANIFEST.md
└── prompt_pack.zip
```

## Check first

On first use, run only the checks without writing files:

```bash
python3 run_banana_flow_prompt_pack.py \
  --source-dir . \
  --output-dir ./banana_flow_dry_run \
  --dry-run
```

Dry-run checks for 20 headings in both files, the 5 male/5 female/5 object/5 environment split, a matching ID set, 9:16, poster purpose, identity anchor, one continuous shot, reference preservation, timeline, and text/watermark exclusions.

## Adding generated assets to the package

Put images generated in Banana Pro and videos downloaded from Flow Lab in a separate folder and pass it to the command:

```bash
python3 run_banana_flow_prompt_pack.py \
  --source-dir . \
  --assets-dir ./generated_assets \
  --output-dir ./banana_flow_automation
```

Using the ID in asset file names is recommended: `M01_KaelVoss_banana.png`, `M01_KaelVoss_flow.mp4`. The script does not judge file contents; it only copies the assets under `assets/` and lists them in the manifest.

## Prompt production loop

First pick an ID from `prompt_set_matrix.md`. Run the Banana Pro image prompt for that ID and keep the result as the starting frame. Then use the Flow prompt with the same ID together with that image. For characters, do not change the single identity anchor; for objects and environments, do not change the geometry. If a video fails, reduce the action to a single movement and slow the camera down instead of making the prompt longer.

## Key assumptions

The default target is `8 seconds`, `9:16 vertical` and one continuous shot. Google's Veo prompting guide recommends directing with camera/shot, subject, action, context, style/ambience and separate audio sentences; the video prompts in the pack follow this shared structure. Sources: [1] [2] [3].

## Troubleshooting

If you get `Prompt validation failed`, open the ID in the error list and fix the missing phrase. Headings must use the format `## M01 — ...`, `## F01 — ...`, `## O01 — ...`, `## E01 — ...`. Every prompt must sit inside a ` ```text ` block. If you rename files or headings, keep the IDs; the automation matches on ID.

## Sources

[1]: https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-veo-3-1 "Google Cloud — The ultimate prompting guide for Veo 3.1"
[2]: https://deepmind.google/models/veo/ "Google DeepMind — Veo"
[3]: https://deepmind.google/models/gemini-omni/prompt-guide/ "Google DeepMind — How to create effective prompts with Gemini Omni"
