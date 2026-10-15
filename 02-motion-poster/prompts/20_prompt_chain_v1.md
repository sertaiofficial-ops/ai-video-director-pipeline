# SERTAI Motion Poster and AI Video — 20-Prompt Chain

This chain uses the values from the Destiny Poison test as an example; replace the bracketed fields with another song, character or reference set. Keep image/video prompts in English. Each prompt takes the file name of the previous output as the input for the next stage.

## Prompt 01 — Project brief and creative goal

```text
Act as a creative director for a vertical SERTAI music-video teaser. Project: [TRACK NAME]. Goal: turn a short supplied song excerpt and reference images into an original 8-second 9:16 visual proof-of-concept. Do not copy the source characters, typography, logos, or exact scene layout. Extract only transferable principles: color, line/render, surface, lighting, camera rhythm, symbolic objects, and emotional temperature. Produce a concise brief with audience, narrative arc, one location, one subject, one primary action, and one final visual accent.
```

## Prompt 02 — Audio technical analysis

```text
Analyze the supplied audio file as production data. Return duration, sample rate, channel count, codec/format, estimated BPM, RMS energy, spectral brightness, loudness, and dynamic range. Mark each value as measured or approximate. Convert the findings into usable video cue points; do not invent lyrics, genre, or a melody that is not audible or supplied. Recommend a short test window of 8 seconds unless the source excerpt is shorter.
```

## Prompt 03 — Graphic DNA extraction

```text
Analyze the supplied reference images and describe the transferable graphic DNA in these categories: character identity anchors, rendering and line, palette, lighting, surface/material, composition, camera movement, typography, symbols, and emotional tone. Separate observed facts from creative interpretation. Then write a two-column table: source principle / original SERTAI adaptation. Do not reproduce readable poster text, logos, technical labels, or exact layout.
```

## Prompt 04 — Character identity lock

```text
Create a locked character bible for an original recurring SERTAI character based on the supplied identity references. Define age impression, face shape, skin tone, hair, eyes, facial marks, wardrobe, accessories, body scale, posture, expression range, signature light, and forbidden changes. Preserve identity anchors across all future frames. Explicitly state which details are fixed, which details may vary, and which source-specific graphic elements must not be copied.
```

## Prompt 05 — Visual negative library

```text
Write a negative prompt for a dark vertical music-video character. Exclude: readable text, poster typography, logos, watermarks, technical labels, duplicate characters, extra limbs, face drift, changed hairstyle, changed wardrobe, plastic skin, oversaturated neon, random armor, cartoon motion, cheerful expression, bright daylight, flat lighting, noisy background, and unmotivated camera shake. Keep the negative prompt specific to this character and environment; do not add irrelevant objects.
```

## Prompt 06 — Color and lighting map

```text
Create a color-and-lighting map for a 9:16 cyberpunk poison portrait. Use black and deep crimson as the structural base, acid green only for biological signal cracks, chrome silver only for reflective transformation accents, and a restrained neutral skin tone. Define key light, rim light, bounce light, background practicals, shadow density, and the exact moment when the red signal intensifies. Keep the palette limited and avoid a generic rainbow cyberpunk look.
```

## Prompt 07 — Environment and single-scene setup

```text
Design one continuous environment for an 8-second vertical teaser. The same dark industrial interior must remain present from start to finish: [ENVIRONMENT]. Include one wet reflective surface, one background light structure, and one depth cue. Specify what stays visible throughout so the model cannot invent a new location. Use one subject and one main action only. End with a single visual resolution rather than multiple scene changes.
```

## Prompt 08 — Primary character reference

```text
Create a primary character reference image for an original SERTAI visual music-video universe. Use the supplied identity references for continuity, but create a clean original portrait with [CHARACTER ANCHORS]. Visual style: cinematic dark cyberpunk portrait, red-black chrome atmosphere, acid-green bioluminescent fissures, wet hair and leather, controlled specular highlights, deep blacks, subtle film grain. Neutral upright pose, clean silhouette, white background, no text, no watermarks, no logos, no labels, no annotations.
```

## Prompt 09 — Neutral 9:16 first frame

```text
Create the first keyframe for an original 9:16 vertical teaser using the primary character reference. Preserve [HAIR], [FACE], [SKIN], [CRACK PATTERN], [WARDROBE], and [ACCESSORIES]. Place the subject in [ENVIRONMENT] with [KEY LIGHT], [RIM LIGHT], and [BACKGROUND LIGHT]. Frame as a medium close-up at eye level, slightly right of center, with [NEGATIVE SPACE]. Keep the expression neutral and watchful. No readable text, no logos, no watermark, no annotations.
```

## Prompt 10 — Final pulse frame

```text
Edit the supplied first keyframe into the end-state of the same shot. Preserve the exact face proportions, wet hair, jacket silhouette, accessories, environment, camera angle, and composition. Change only these elements: both eyes emit one restrained blood-red pulse, the acid-green fissures brighten slightly, and a small liquid-chrome ripple catches light on the right cheek. No new characters, no outfit change, no new location, no poster typography, no readable text, no logos, no watermark, no labels, no annotations.
```

## Prompt 11 — Real image-to-video motion prompt

```text
An original 8-second vertical SERTAI teaser in cinematic cyberpunk poison portrait style. Preserve the exact subject identity from the input frame: [CHARACTER ANCHORS]. Keep [ENVIRONMENT ANCHORS] visible throughout. From 0–[A] seconds, the subject remains almost still while only [MICRO-MOTION] moves and the camera performs a slow controlled push-in. From [A]–[B] seconds, [SINGLE ACTION] occurs along this trajectory: [TRAJECTORY]. From [B]–[C] seconds, [FINAL STATE CHANGE] happens once and resolves into near-black. Maintain face, hair, wardrobe, body scale, light direction, and location continuity. No new characters, no scene change, no readable text, no logos, no watermark, no captions, no dialogue, no singing. No background music.
```

## Prompt 12 — Character continuity correction

```text
Review the generated clip against the primary reference and list only continuity risks. Check face identity, eye position, hair silhouette, crack placement, jacket seams, accessories, body scale, camera direction, environment geometry, red/green light direction, and timing of the final transformation. For each risk, write one targeted correction prompt that changes only the failing element and preserves all successful elements. Do not redesign the scene.
```

## Prompt 13 — Beat-sync map

```text
Create an 8-second visual beat-sync map for an audio excerpt at approximately [BPM] BPM. Calculate the approximate beat interval, then choose a small number of meaningful visual cue points rather than cutting on every beat. Map: opening stillness, first signal shimmer, second tension cue, final red pulse, material ripple, and blackout. Mark every time as approximate if the tempo measurement is not exact. Avoid over-editing.
```

## Prompt 14 — Motion poster fallback

```text
Design a motion-poster fallback for the same 8-second teaser using only a neutral first keyframe and a final pulse keyframe. Use a slow digital push-in on the neutral frame, low-opacity cyan atmosphere flashes at [CUE 1] and [CUE 2], a short fade-black transition beginning at [TRANSITION START], and a restrained red overlay around [RED CUE]. End on the final keyframe and resolve toward black. Keep the image readable, the effects sparse, and the character identity stable.
```

## Prompt 15 — V1 FFmpeg motion poster command

```text
Write an FFmpeg command that loops one 9:16 PNG for [DURATION] seconds at 24 fps, applies a slow zoompan with a maximum zoom of 1.06x, adds two low-opacity cyan full-frame flashes and one restrained red full-frame flash at specified timestamps, overlays small white `SERTAI LAB` text in the bottom-right safe area, trims the supplied audio to the same duration, and exports H.264/yuv420p video with AAC audio and faststart metadata. Do not crop the subject’s face.
```

## Prompt 16 — V2 two-frame FFmpeg command

```text
Write an FFmpeg filter graph for two 9:16 PNG inputs: hold the neutral keyframe for [NEUTRAL DURATION], hold the final pulse keyframe for [FINAL DURATION], apply separate slow zoompan movements, combine them with a 0.3-second fadeblack transition starting at [OFFSET], add a low-opacity red overlay around the pulse moment, add small `SERTAI LAB` text, and mux the first [DURATION] seconds of the supplied source audio. Output 720x1280, 24 fps, H.264 CRF 18, yuv420p, AAC 192 kbps, and faststart.
```

## Prompt 17 — Audio and video mix check

```text
Audit the final video/audio assembly. Confirm that the source song is the only soundtrack, that no accidental generated audio remains, that audio duration matches video duration, that the source start point is unchanged, and that the export is stereo AAC at the requested bitrate. Report any clipping, silence, offset, or unintended fade. Do not change the audio unless a specific issue is found.
```

## Prompt 18 — Technical quality control

```text
Run a technical QC checklist for the final MP4. Verify duration, width, height, aspect ratio, frame rate, pixel format, video codec, audio codec, sample rate, channels, and file integrity. Check that the video has no unintended black frames except the planned final resolve, no readable generated text, and no missing audio. Return pass/fail per item and a short corrective command only for failed items.
```

## Prompt 19 — Reusable skill improvement

```text
Review this completed production and identify which decisions are reusable for the next project: source intake, audio measurements, graphic DNA categories, character locks, prompt clauses, cue timing, fallback motion-poster filters, export settings, and packaging. Separate stable workflow rules from project-specific values. Rewrite the stable rules as concise imperative instructions for a reusable creative-production skill.
```

## Prompt 20 — Final archive and handoff

```text
Prepare a final handoff package for a vertical music-video proof-of-concept. Include the final MP4, fallback or raw video, source audio, neutral and final keyframes, all supplied reference images, technical audio/video reports, graphic DNA analysis, clip plan, video prompt, prompt chain, and a user guide. Write a concise final report that clearly distinguishes AI-generated motion video from motion-poster fallback. Put all files in one ZIP archive, test it with unzip -t, and report the archive path and the most important preview file.
```

## Usage note

In a first project, use Prompts 01–07 for analysis and planning, 08–10 for image references, 11 for real video generation, 13–18 for rhythm/edit/quality, and 19–20 for improving the skill and delivery. If there is no video generation quota or tool access, run the 14–16 chain; once real image-to-video is possible, use the same first frame with Prompt 11 and archive the fallback as a comparison reference.
