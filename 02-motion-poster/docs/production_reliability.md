# Production Reliability — Motion Poster

This layer checks that a production package is complete without changing any creative prompt.

## Project config

Copy `config/project_config.example.json` to `project_config.json` for your project. Fill in at least `workflow_mode`, `audio_mode`, `video_provider`, `brand` and `rights`. Before publishing, set `rights.status` to `cleared` or `user-approved`; `unknown` is for draft work only and the runner prints a warning for it.

Fields that are validated by the runner:

- `brand.text`: 80 characters or fewer.
- `brand.opacity`: a number between 0 and 1.
- `rights.status`: `unknown`, `cleared`, `user-approved` or `restricted`.
- `assets.require_complete_set`: `true` or `false` (see Asset QC).
- `assets.poster_pattern` / `assets.video_pattern`: preferred file names, with `{id}` replaced by the prompt ID.

The other fields (`workflow_mode`, `scene_count`, `audio_mode`, `video_provider`, `character_id`, references, `cue_map`, `assets.directory`) are recorded in `run_config.json` as project metadata. Duration, aspect ratio and the assets folder are still set on the command line (`--duration`, `--aspect-ratio`, `--assets-dir`).

## Validate the prompt pack

Run from `02-motion-poster/`:

```bash
bash src/run_banana_flow_prompt_pack.sh \
  --project-config config/project_config.example.json \
  --dry-run
```

This checks the 20 visual and 20 video prompts, ID matching, the M/F/O/E category split and the shared 9:16 / 8-second rules, and reads the project config. Continuity checks (same-reference language, single-location exclusion, audio strategy) are reported as `warnings`, not errors, so existing creative prompts are not rejected. If the character research file is not found, a warning is printed and the package is built without it. Runs without `--dry-run` also write `asset_manifest.json`.

## Asset QC

Put generated files in `assets/`, named with the prompt ID first. Example:

```text
assets/
├── M01_poster_9x16.png
├── M01_video_8s.mp4
├── F01_nyx_poster_9x16.png
└── F01_nyx_video_8s.mp4
```

A file matches an ID when its name equals the configured pattern, or when it is named `<ID>`, `<ID>_…` or `<ID>-…`. With `--assets-dir assets` the runner looks for one poster (`.png`, `.jpg`, `.jpeg`, `.webp`) and one video (`.mp4`, `.mov`, `.webm`) per ID and uses `ffprobe` to check that each file is readable and 9:16. Video duration is compared with the target and reported as a warning if it differs by more than 0.5 seconds.

Statuses:

- `SKIPPED`: no `--assets-dir` given.
- `PARTIAL`: some posters or videos are missing and `require_complete_set` is `false`; the draft package is still built and the missing IDs are listed.
- `PASS`: every ID has a readable 9:16 poster and video.
- `FAIL`: a file is unreadable or not 9:16, or files are missing while `require_complete_set` is `true`. The run stops.

The status is written to `validation.json` (`asset_qc_status`), `asset_manifest.json` and `DELIVERY_MANIFEST.md`.

## Audio analysis

`src/analyze_audio.py` uses `ffprobe` for technical metadata (duration, format, codec, sample rate, channels), all labelled `measured`. If `numpy` and `soundfile` are installed and the format is readable by libsndfile (WAV, FLAC, OGG), it also estimates RMS, peak, spectral centroid and approximate dynamic range, labelled `approximate`. Otherwise the analysis block is marked `unavailable`.

BPM is never invented: `bpm_approx` is always `null`. If a BPM is needed for the cue map, it has to come from the artist or from a separate beat-tracking tool.

```bash
python3 src/analyze_audio.py path/to/track.wav
```

## Brand and rights

The brand text is not added to generation prompts; it is applied in the final edit layer. `brand.enabled`, `brand.text`, `brand.position` and `brand.opacity` are stored in the run config. For reference images, record `rights.source_url`, `rights.creator`, `rights.permission_note` and `rights.status`.
