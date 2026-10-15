# One-Click Motion Poster Automation

## Purpose

`run_motion_poster.py` runs the deterministic post-production pipeline in one command without starting any credit-based or authenticated image/video generation on its own. It validates the source audio or video, extracts the audio stream, runs the audio analysis script, renders a V1/V2 motion poster, muxes the source audio, runs QC with `ffprobe`, writes a manifest and tests the ZIP archive.

This boundary is deliberate: no passwords, tokens or API behavior are guessed for Midjourney, Stable Diffusion, a video model or any paid external service. Image model outputs (`first_keyframe`, `final_keyframe`) or a real image-to-video MP4 are passed in as explicit file inputs.

## Modes

| Mode | Required inputs | Behavior |
|---|---|---|
| `auto` | Audio + first frame; final frame added if present | Real mux if a raw generated video exists; otherwise V2 if a final frame exists, else V1 |
| `fallback` | Audio + first frame; final frame optional | Renders a V2 or V1 motion poster |
| `real` | Audio + `--raw-video` | Applies the source audio and label to a previously generated video |

## Running the Destiny Poison test

```bash
python3 src/run_motion_poster.py \
  --source-audio "./assets/your_track.wav" \
  --first-keyframe "./assets/first_keyframe.png" \
  --final-keyframe "./assets/final_keyframe.png" \
  --mode fallback \
  --output-dir "./assets/automation_output"
```

To see the commands without running them on a first try:

```bash
python3 src/run_motion_poster.py \
  --source-audio "/path/to/source.wav" \
  --first-keyframe "/path/to/first_keyframe.png" \
  --final-keyframe "/path/to/final_keyframe.png" \
  --dry-run \
  --output-dir ./automation_output
```

If a real image-to-video MP4 has already been generated:

```bash
python3 src/run_motion_poster.py \
  --source-audio "/path/to/source.wav" \
  --raw-video "/path/to/generated_video.mp4" \
  --mode real \
  --duration 8 \
  --output-dir ./automation_output
```

## Output contract

| Output | Contents |
|---|---|
| `motion_poster_final.mp4` | Final video |
| `*_technical.json` | `ffprobe` media measurements |
| `source_audio_analysis.txt` | Output of the analysis script |
| `qc_report.json` | Duration, size, audio and status checks |
| `run_config.json` | Parameters used and the resolved mode |
| `automation_commands.log` | Executed or dry-run commands |
| `DELIVERY_MANIFEST.md` | ZIP contents manifest |
| `motion_poster_package.zip` | Verified package |

## Automation logic

1. `ffmpeg` and `ffprobe` are looked up on PATH.
2. The given file paths and mode requirements are checked.
3. The source video or audio is probed in JSON format.
4. If a video is given, its audio is extracted to 48 kHz stereo WAV.
5. The audio analysis script runs; if it fails, an error report is saved.
6. `auto` mode resolves as raw video → real; final frame → V2; first frame only → V1.
7. Video is written as 720×1280, 24 fps, H.264 CRF 18, yuv420p; audio as AAC 192 kbps.
8. The final file is probed again; the run fails if the duration differs by more than 50 ms or if size/audio is missing.
9. Outputs and inputs are collected into one ZIP; archive integrity is checked with `ZipFile.testzip()`.

## Safe-use boundaries

The script performs only local, deterministic operations. It makes no paid generation calls, does not log into user accounts, does not upload files to external services and does not start any irreversible publishing or payment action. A real model generation layer requires a separate platform-specific adapter; if one is built, token handling, retry policy, quota checks and user approval must be designed separately.
