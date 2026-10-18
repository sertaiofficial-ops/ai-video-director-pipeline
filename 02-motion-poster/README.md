# Part 2 · Motion Poster Production

Second step: with the DNA locked, generate 20 sequenced poster prompts and 20 matching motion prompts, render the posters, then animate them (Veo 3.1 Fast / Gemini Omni) or build an ffmpeg motion poster from first and final keyframes.

<p align="center">
  <img src="keyframes/first_keyframe.png" width="260" alt="First keyframe">
  <img src="keyframes/final_keyframe.png" width="260" alt="Final keyframe">
</p>

| Folder | What it holds |
|---|---|
| [`prompts/`](prompts/) | Song-to-clip master prompt, 20 visual + 20 video prompts, prompt chain v1/v2, matrix, guidelines; `split/` = one file per ID |
| [`src/`](src/) | Prompt pack runner, image → video API tool, motion poster renderer |
| [`skill/`](skill/) | Google API (Gemini / Vertex AI) integration skill |
| [`docs/`](docs/) | Clip plan, motion poster recipe, API research, integration and production-reliability guides |
| [`keyframes/`](keyframes/) | First / final keyframes for the fallback motion poster |

```bash
pip install -r ../requirements.txt
bash src/run_banana_flow_prompt_pack.sh --dry-run
python3 src/google_flow_banana_api.py --dry-run \
  --visual-prompt-file prompts/split/visual/M01.txt \
  --video-prompt-file  prompts/split/video/M01.txt --video-provider omni --output-dir output/M01
python3 src/run_motion_poster.py --source-audio assets/your_track.wav \
  --first-keyframe keyframes/first_keyframe.png --final-keyframe keyframes/final_keyframe.png \
  --mode fallback --output-dir output/motion_poster --dry-run
```
Every tool is dry-run first; real (paid) calls only with `--execute`. Keys go in `.env` (see `../.env.example`), never in the repo.

## Production reliability

Copy `config/project_config.example.json` to a project config and run the prompt pack validator with it:

```bash
bash src/run_banana_flow_prompt_pack.sh \
  --project-config config/project_config.example.json \
  --dry-run
```

For generated assets, add `--assets-dir assets`. The runner writes `asset_manifest.json`, validates ID-matched poster/video files with `ffprobe`, and records brand and rights metadata. See [`docs/production_reliability.md`](docs/production_reliability.md).
