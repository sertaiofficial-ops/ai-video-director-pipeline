# Architecture

**Scope:** the `01-graphic-dna` and `02-motion-poster` modules.
**Goal:** a reliable production line from graphic DNA analysis, through character-consistent poster and video prompts, to a verifiable motion-poster delivery package.

## 1. Purpose

The pipeline turns a song, a reference video or a reference image into a cinematic visual production in the SERTAI universe. It has two layers:

1. **Graphic DNA analysis:** extracts the colour, light, lens, texture, atmosphere, typography and motion of the source.
2. **Motion-poster production:** combines that visual language with character continuity to produce poster prompts, image-to-video prompts and, when needed, an FFmpeg motion poster.

The aim is not only to write prompts but to make every creative decision reusable, filed, verifiable and reproducible with one command.

The no-API manual route stays the default: the skill files can be pasted into any chat assistant, and every script runs as a dry-run unless `--execute` is given.

## 2. Layers

```text
Source song / reference video / image
                  │
                  ▼
┌─────────────────────────────────────┐
│ 01 · GRAPHIC DNA                    │
│ palette · light · lens · texture    │
│ motion · typography · mood          │
│ character identity anchors          │
└─────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│ 02 · MOTION POSTER                  │
│ 20 visual prompts                   │
│ 20 video prompts                    │
│ prompt matrix                       │
│ character consistency               │
│ audio / cue relationship            │
└─────────────────────────────────────┘
                  │
       ┌──────────┴──────────┐
       ▼                     ▼
┌───────────────┐   ┌──────────────────┐
│ Optional API  │   │ FFmpeg fallback  │
│ image API     │   │ first keyframe   │
│ video API     │   │ final keyframe   │
│               │   │ source audio     │
└───────────────┘   └──────────────────┘
       │                     │
       └──────────┬──────────┘
                  ▼
┌─────────────────────────────────────┐
│ QC + DELIVERY                       │
│ prompt validation                   │
│ asset manifest + ffprobe checks     │
│ run config · delivery manifest      │
│ ZIP package                         │
└─────────────────────────────────────┘
```

## 3. Modules

### `01-graphic-dna/`

The skill and reference layer for graphic DNA analysis. It makes no model calls; it produces the creative and identity decisions first.

- `skill/SKILL.md`: main instructions for DNA extraction, character locking and the production flow.
- `docs/`: analysis findings and character consistency research (`character_consistency_research.md`).
- `skill/references/`: prompt blueprints, character consistency and delivery checklists.

### `02-motion-poster/`

Turns the graphic DNA output into a production package.

- `prompts/`: 20 visual and 20 video prompts, prompt chains, matrix and guidelines.
- `src/run_banana_flow_prompt_pack.py`: prompt validation, asset QC and packaging runner (`.sh` wrapper alongside).
- `src/run_motion_poster.py`: FFmpeg fallback motion-poster renderer.
- `src/analyze_audio.py`: technical and optional DSP audio analysis.
- `src/google_flow_banana_api.py`: optional adapter for the official Google image and video APIs (dry-run by default).
- `src/probe_media.sh`, `src/package_demo.sh`: media probe and demo packaging.
- `config/`: project config example.
- `docs/`: clip plan, API integration and production reliability guides.
- `keyframes/`: first and final keyframes for the fallback.
- `skill/`: API integration skill.

## 4. Prompt set

```text
M01–M05  male characters
F01–F05  female characters
O01–O05  objects
E01–E05  atmospheric environments
```

Every ID has a visual poster prompt and a video motion prompt with the same ID, so the poster generated for an ID is passed to the image-to-video prompt of that same ID.

Shared rules: 9:16 vertical frame, 8-second default video, one main movement, one main location, start / middle / end time segments, physical identity anchors, explicit exclusions, matching IDs across visual and video prompts.

## 5. Production routes

### 5.1 Optional API route

```text
Visual prompt → image API → poster / starting frame → video API → image-to-video clip → ffprobe + asset QC + manifest
```

The adapter uses documented developer APIs only. It does not automate any web interface and does not carry cookies or user sessions. Model IDs are set through `.env` / command-line flags (see `.env.example`).

### 5.2 FFmpeg fallback route

```text
first_keyframe.png + final_keyframe.png + source audio
  → zoompan + crop + xfade + brand overlay
  → H.264 720×1280 + AAC MP4
```

This route produces a testable demo without any API access or budget.

## 6. Production reliability layer

### 6.1 Project config

`02-motion-poster/config/project_config.example.json` collects `workflow_mode`, `scene_count`, `duration_seconds`, `aspect_ratio`, `audio_mode`, `video_provider`, `character_id`, `identity_reference`, `style_reference`, `cue_map`, `brand`, `rights` and `assets` in one file. The runner validates brand, rights and asset policy and records the rest in `run_config.json`.

### 6.2 Per-ID asset QC

For every prompt ID the runner looks for a poster and a video, reads them with `ffprobe` (codec, resolution, duration) and checks the 9:16 ratio. Results are written to `asset_manifest.json`:

- `SKIPPED`: no `--assets-dir` given.
- `PARTIAL`: some assets missing, draft package allowed.
- `PASS`: complete, readable 9:16 set.
- `FAIL`: unreadable or wrong-ratio files, or missing files when `require_complete_set` is `true`.

### 6.3 Extended validator

Besides counts and ID matching, the validator checks the M/F/O/E split, the 9:16 phrase, the 8-second target and the time segments. Continuity language, single-location exclusion and audio strategy are reported as `warnings` so existing creative prompts are not rejected; structural problems stay `errors`.

### 6.4 Audio analysis

`src/analyze_audio.py` reports measured `ffprobe` metadata and, when `numpy` and `soundfile` are installed, approximate RMS, peak, spectral centroid and dynamic range. BPM is never invented; `bpm_approx` stays `null`.

### 6.5 Brand and rights

`brand` (enabled, text, position, opacity) and `rights` (status, source URL, creator, permission note) live in the config. Brand text is applied in the final edit layer, never inside generation prompts.

### 6.6 Paths

Skill documents now point to the real `02-motion-poster/src/` paths. The runner looks for the character research file in this order:

1. `<source-dir>/character_consistency_research.md` (default `02-motion-poster/prompts/`)
2. `02-motion-poster/docs/character_consistency_research.md`
3. `01-graphic-dna/docs/character_consistency_research.md`

If none exists, it prints a warning and builds the package without it.

## 7. Commands (run from `02-motion-poster/`)

```bash
# Prompt dry-run
bash src/run_banana_flow_prompt_pack.sh --project-config config/project_config.example.json --dry-run

# Build the prompt package
bash src/run_banana_flow_prompt_pack.sh --project-config config/project_config.example.json \
  --output-dir output/banana_flow_automation

# Package with asset QC
bash src/run_banana_flow_prompt_pack.sh --project-config config/project_config.json \
  --assets-dir assets --output-dir output/banana_flow_automation

# Audio analysis
python3 src/analyze_audio.py assets/source.wav

# FFmpeg motion-poster fallback
python3 src/run_motion_poster.py --source-audio assets/source.wav \
  --first-keyframe keyframes/first_keyframe.png --final-keyframe keyframes/final_keyframe.png \
  --mode fallback --output-dir output/motion_poster
```

## 8. Outputs

```text
output/banana_flow_automation/
├── prompts/visual/M01.txt …
├── prompts/video/M01.txt …
├── references/
├── assets/            (when --assets-dir is given)
├── validation.json
├── asset_manifest.json
├── run_config.json
├── DELIVERY_MANIFEST.md
└── prompt_pack.zip
```

## 9. Out of scope

Automatic push, paid API calls, web-interface automation, rewriting creative prompts, automatic visual quality scoring, CI/CD and parallel API orchestration for 20 scenes.

— SERTAI LAB
