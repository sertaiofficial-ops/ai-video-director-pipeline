# Release Notes

## Improved: Production Reliability Update

We've improved the pipeline. Our R&D work continues behind the scenes, and based on feedback the necessary patches and updates have been shipped. Creative prompts are unchanged; this update makes every production package easier to check before delivery.

### What's new

- **Project config manifest.** `02-motion-poster/config/project_config.example.json` keeps workflow mode, scene count, duration, aspect ratio, audio mode, video route, character and style references, cue map, brand, rights and asset policy in one file. Pass it with `--project-config`.
- **Per-ID asset QC.** With `--assets-dir`, the prompt-pack runner looks for a poster and a video for every prompt ID, reads each file with `ffprobe` and checks the 9:16 ratio. The result is `PASS`, `PARTIAL` (draft package with missing files listed) or `FAIL` (unreadable or wrong-ratio files, or missing files when `require_complete_set` is `true`), written to `asset_manifest.json`, `validation.json` and the delivery manifest.
- **Extended validator.** Continuity language, single-location exclusion and audio strategy are now checked and reported as warnings, alongside the existing structural checks. Video duration that differs from the target is flagged too.
- **Audio analysis tool.** New `02-motion-poster/src/analyze_audio.py` reports measured duration, format, codec, sample rate and channels, plus approximate level and spectral estimates when `numpy` and `soundfile` are installed. BPM is never invented: it stays empty unless you supply it.
- **Brand and rights fields.** Brand text, position and opacity, and rights status, source, creator and permission note, are validated and recorded in the run config. An `unknown` rights status triggers a draft-only warning.
- **Fixed documentation paths.** Skill documents now point to the real `02-motion-poster/src/` scripts.
- **Research-file fallback.** The runner now also finds `01-graphic-dna/docs/character_consistency_research.md`, and warns instead of failing silently when the file is missing.
- **Documentation.** New `ARCHITECTURE.md` and `02-motion-poster/docs/production_reliability.md`.

The no-API manual route is still the default, and every script runs as a dry-run unless `--execute` is given.

### Next steps

- Read duration, aspect ratio and asset folder directly from the project config instead of the command line.
- Optional beat tracking for BPM in the audio analysis tool.
- Automated tests and CI.

— SERTAI LAB
