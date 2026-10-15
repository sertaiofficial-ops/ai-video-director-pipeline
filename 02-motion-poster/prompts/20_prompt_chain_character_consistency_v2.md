# SERTAI — 20-Prompt Chain v2
## Character consistency optimization for Midjourney / Stable Diffusion

This version hardens the image generation steps of the previous chain for character continuity. In every project, fill in `CHARACTER_ID`, `IDENTITY_REF`, `STYLE_REF`, `SEED`, `MODEL_VERSION`, `FIXED_ANCHORS`, `VARIABLES` and `NEGATIVE_BLOCK` first. In every new image of the same character, repeat the fixed identity block as the unchanging first part of the prompt; change only pose, lens, location or a single controlled action.

## 0. Consistency lock

**Fixed identity anchors:** face proportions, eye spacing, nose/chin profile, hair silhouette, hair color and wetness, skin tone, general placement of face and neck cracks, jacket silhouette, accessories, body scale and the character's basic apparent age.

**Allowed variables:** pose, gaze direction, camera distance, a single facial expression, ambient light, hand/head position and background density of the scene.

**Must never change:** new person, new haircut, outfit change, different crack map, different facial age, different body proportions, random armor, two locations merged, readable text, logos and watermarks.

**Practical starting settings:** In Midjourney use the same model/version, `--ar 9:16`, `--chaos 0`, a fixed seed and low/medium stylize. Use `--oref`/`--ow` in V7 and `--cref`/`--cw` in V6 or Niji 6. In Stable Diffusion keep the same checkpoint, VAE, sampler, scheduler, resolution, seed and prompt order; use IP-Adapter FaceID for face identity, IP-Adapter Plus for overall look, and ControlNet for pose/structure if needed.

---

## Prompt 01 — Project brief and creative goal

```text
Act as a continuity-first creative director for an original vertical SERTAI music-video teaser. Project: [TRACK NAME]. Goal: turn a short supplied song excerpt and reference images into an original 8-second 9:16 proof-of-concept. Extract only transferable principles: palette, rendering, surface, lighting, camera rhythm, symbolic objects, and emotional temperature. Do not copy the source person, exact costume, poster typography, logo, or scene layout. Produce a locked brief with: one character, one location, one primary action, one final visual accent, fixed identity anchors, permitted variations, and a continuity risk list.
```

## Prompt 02 — Audio technical analysis

```text
Analyze the supplied audio file as production data. Return duration, sample rate, channel count, codec/format, estimated BPM, RMS energy, spectral brightness, loudness, and dynamic range. Mark every value as measured or approximate. Convert the findings into a small set of visual cue points for an 8-second test. Do not invent lyrics, melody, or genre. Recommend a test window that does not exceed the supplied excerpt.
```

## Prompt 03 — Graphic DNA extraction

```text
Analyze the supplied reference images and describe only transferable graphic DNA in these categories: character identity anchors, rendering and line, palette, lighting, surface/material, composition, lens/camera, motion language, typography, symbols, and emotional tone. Separate observed facts from creative interpretation. Return a two-column table: source principle / original SERTAI adaptation. Explicitly list source-specific details that must not be copied.
```

## Prompt 04 — Identity card / Character Bible

```text
Create a continuity-first character identity card for an original recurring SERTAI character named [CHARACTER_ID], using [IDENTITY_REF] as the identity reference. Write one exact, reusable anchor paragraph and do not use synonyms in later prompts. Define: apparent age range, face geometry, eye shape and spacing, nose bridge, cheekbones, jaw and chin, skin undertone, hair cut and silhouette, hair texture, facial marks and their approximate locations, wardrobe silhouette, material, accessories, body proportions, posture, default expression, signature signal color, and forbidden changes. Split the result into FIXED ANCHORS, VARIABLE CONTROLS, and NEGATIVE DRIFT RULES. Never identify the character as a real person.
```

## Prompt 05 — Identity anchor block + negative block

```text
Using the character identity card, produce three copy-ready blocks for every future image prompt.

BLOCK A — FIXED IDENTITY ANCHORS: repeat the exact physical description of [CHARACTER_ID] in 45–70 words; prioritize face geometry, hair silhouette, skin undertone, fixed facial marks, wardrobe silhouette, accessories, and body scale.

BLOCK B — CONTROLLED VARIATION: list only [POSE], [GAZE], [LENS], [LOCATION], [LIGHT CHANGE], and [SINGLE ACTION]. Each variable must be independently changeable without rewriting Block A.

BLOCK C — NEGATIVE DRIFT: exclude face drift, age drift, hairstyle drift, wardrobe drift, crack-pattern drift, body-scale drift, duplicate person, extra limbs, extra fingers, random armor, plastic skin, cheerful expression, text, logo, watermark, label, and new location.

Return the three blocks without adding new traits.
```

## Prompt 06 — Reference preparation / face and body sheet

```text
Create a clean character reference sheet for [CHARACTER_ID] from [IDENTITY_REF]. Generate exactly four panels on a neutral dark-gray background: full-body front, full-body back, neutral portrait close-up, and three-quarter profile. Keep the same face geometry, eye spacing, hair silhouette, skin undertone, facial mark/crack placement, jacket seams, accessories, and body scale in all four panels. Use neutral expression except where specified. No props, no environment, no poster design, no typography, no logos, no watermark, no labels, no annotations. This sheet is an identity control asset, not a finished poster.
```

## Prompt 07 — Environment and single-scene setup

```text
Design one continuous environment for an 8-second vertical teaser around [CHARACTER_ID]. Keep the exact same room geometry from start to finish: [ENVIRONMENT]. Include one wet reflective surface, one background light structure, one depth cue, and one controlled negative-space area. State what remains visible in every frame. Do not introduce a second location, a second character, a different time of day, or an unmotivated prop. The environment must support the fixed identity anchors rather than compete with the face.
```

## Prompt 08 — Midjourney V7 primary image

```text
[FIXED_IDENTITY_ANCHORS] Original cinematic portrait of [CHARACTER_ID] in [SCENE], [SHOT_SIZE], [CAMERA_ANGLE], [LENS_FEEL], [POSE], [GAZE]. Preserve the exact face geometry, eye spacing, hair silhouette, skin undertone, fixed facial marks, wardrobe silhouette, accessories, and body scale from the reference. Style: [STYLE_SPEC]. Lighting: [KEY_LIGHT], [RIM_LIGHT], [BACKGROUND_LIGHT]. Keep one character and one location. No poster layout and no readable text. --v 7 --ar 9:16 --oref [IDENTITY_REF_URL] --ow 250 --sref [STYLE_REF_URL] --sw 50 --stylize 100 --chaos 0 --seed [SEED] --no text,logo,watermark,labels,annotations,duplicate person,extra limbs,random armor,face drift
```

**V7 note:** Use `--oref` with a single Omni Reference image. `--ow 250` is a safe starting value here; raise it if the character drifts too much, lower it if style or pose gets locked too hard. Do not mistake the seed for an identity lock; use it to compare identical test conditions.

## Prompt 09 — Midjourney V6 / Niji 6 alternative primary image

```text
[FIXED_IDENTITY_ANCHORS] Original cinematic portrait of [CHARACTER_ID] in [SCENE], [SHOT_SIZE], [CAMERA_ANGLE], [LENS_FEEL], [POSE], [GAZE]. Preserve the exact face geometry, eye spacing, hair silhouette, skin undertone, fixed facial marks, wardrobe silhouette, accessories, and body scale from the reference. Style: [STYLE_SPEC]. Lighting: [KEY_LIGHT], [RIM_LIGHT], [BACKGROUND_LIGHT]. One character, one location, clean readable silhouette, no poster layout, no readable text. --v 6.1 --ar 9:16 --cref [IDENTITY_REF_URL] --cw 100 --sref [STYLE_REF_URL] --sw 50 --stylize 100 --chaos 0 --seed [SEED] --no text,logo,watermark,labels,annotations,duplicate person,extra limbs,random armor,face drift
```

**V6 note:** `--cw 100` is the starting point for preserving more reference detail such as face, hair and clothing. Lower `--cw` for controlled variations where you want to change the outfit; keep the physical anchor block in the prompt to preserve facial identity.

## Prompt 10 — Stable Diffusion XL + IP-Adapter FaceID

```text
Generate one original 9:16 vertical portrait of [CHARACTER_ID] using the supplied face identity reference [IDENTITY_REF]. Preserve the fixed identity anchors exactly: [FIXED_IDENTITY_ANCHORS]. Scene: [SCENE]. Shot: [SHOT_SIZE], [CAMERA_ANGLE], [LENS_FEEL]. Pose and gaze: [POSE], [GAZE]. Lighting: [KEY_LIGHT], [RIM_LIGHT], [BACKGROUND_LIGHT]. Rendering: [STYLE_SPEC]. Change only [CONTROLLED_VARIABLE].

Use the same SDXL checkpoint, VAE, sampler, scheduler, resolution, prompt order, and seed for the series. Use IP-Adapter FaceID for face identity, starting at scale 0.60; use IP-Adapter Plus at scale 0.35–0.55 only when material/style transfer is required. If pose must be locked, add a single ControlNet OpenPose or depth condition rather than a second identity reference. Keep denoise strength around 0.30–0.45 for img2img variations. No readable text, no logo, no watermark, no label, no annotation, no duplicate person, no face drift, no age drift, no hairstyle drift, no wardrobe drift, no extra limbs.
```

## Prompt 11 — Stable Diffusion img2img final-state frame

```text
Edit [FIRST_KEYFRAME] into the controlled final state of the same shot. Preserve the exact face geometry, eye spacing, hair silhouette, skin undertone, facial marks, crack pattern, jacket seams, accessories, body scale, camera angle, crop, environment geometry, and light direction. Change only: [FINAL_SINGLE_CHANGE]. Use low-to-moderate img2img denoise, protect the face with a mask if available, and keep the same seed and checkpoint. The result must look like the same frame a moment later, not a redesign. No new character, no new location, no new outfit, no text, no logos, no watermark, no annotations, no extra limbs, no face drift.
```

## Prompt 12 — 9:16 first frame / platform-agnostic

```text
Create the first keyframe for an original 9:16 vertical teaser using [CHARACTER_ID] and [IDENTITY_REF]. Repeat the exact FIXED_IDENTITY_ANCHORS at the beginning of the prompt. Place the character in [SCENE]. Preserve [HAIR], [FACE GEOMETRY], [SKIN], [FACIAL MARKS], [WARDROBE], [ACCESSORIES], and [BODY SCALE]. Camera: [SHOT_SIZE], eye-level, [LENS_FEEL], character placed [FOCAL_PLACEMENT], with [NEGATIVE_SPACE]. Expression: neutral and watchful. Vary only [POSE] and [GAZE]. No readable text, no logos, no watermark, no labels, no annotations.
```

## Prompt 13 — Real image-to-video motion prompt

```text
An original 8-second vertical SERTAI teaser using the exact input frame as the visual identity and composition reference. Preserve [FIXED_IDENTITY_ANCHORS] in every frame: face geometry, eye spacing, hair silhouette, skin undertone, fixed facial marks, crack pattern, wardrobe silhouette, accessories, and body scale. The same [ENVIRONMENT_ANCHORS] remain visible from start to finish.

0.0–2.2 seconds: [CHARACTER] stays almost still; only [MICRO_MOTION] moves while the camera performs a slow controlled push-in. 2.2–5.6 seconds: one and only one action, [SINGLE_ACTION], occurs along [TRAJECTORY]; do not change identity or location. 5.6–6.7 seconds: [CONTROLLED_TENSION_CHANGE] happens once. 6.7–7.4 seconds: [FINAL_SIGNAL] appears exactly once. 7.4–8.0 seconds: the final material highlight holds and the image resolves toward near-black. Maintain physically consistent camera movement, light direction, environment geometry, and subject scale. No new characters, no scene change, no readable text, no logos, no watermark, no captions, no dialogue, no singing. No background music.
```

## Prompt 14 — Continuity comparison and drift diagnosis

```text
Compare [GENERATED_FRAME_OR_CLIP] against [IDENTITY_REF] and [FIRST_KEYFRAME]. Report only continuity deviations in this order: face geometry, eye spacing, hair silhouette, skin undertone, facial marks/cracks, wardrobe seams, accessories, body scale, pose, camera crop, environment geometry, light direction, palette, and final-state timing. For each deviation, assign severity 1–3 and write one minimal correction prompt that changes only the failing attribute. Do not redesign the scene or add new style directions.
```

## Prompt 15 — Beat-sync map

```text
Create an 8-second visual beat-sync map for an audio excerpt at approximately [BPM] BPM. Calculate the approximate beat interval. Use only a small number of cue points: opening stillness, first signal shimmer, second tension cue, final red pulse, material ripple, and blackout. Keep the character and environment continuous; never use a beat as an excuse for a new character or scene. Mark every timing as approximate when the BPM measurement is approximate.
```

## Prompt 16 — Motion poster fallback

```text
Design a motion-poster fallback for the same 8-second teaser using [FIRST_KEYFRAME] and [FINAL_KEYFRAME]. Use one slow digital push-in on the neutral frame, two low-opacity cyan atmosphere flashes at [CUE 1] and [CUE 2], a short fade-black transition beginning at [TRANSITION START], and one restrained red overlay around [RED CUE]. End on the final keyframe and resolve toward black. Keep the face readable, effects sparse, and the character identity unchanged. This is a proof-of-concept fallback, not a claim of physically generated motion.
```

## Prompt 17 — V1 FFmpeg command

```text
Write an FFmpeg command that loops one 9:16 PNG for [DURATION] seconds at 24 fps, preserves the face crop, applies a slow center-anchored zoompan with a maximum zoom of 1.06x, adds two low-opacity cyan full-frame flashes and one restrained red full-frame flash at specified timestamps, overlays small white `SERTAI LAB` text in the bottom-right safe area, trims the supplied audio to the same duration, and exports H.264/yuv420p video with AAC audio and faststart metadata. Return both the command and a parameter table.
```

## Prompt 18 — V2 two-frame FFmpeg command

```text
Write an FFmpeg filter graph for [FIRST_KEYFRAME] and [FINAL_KEYFRAME]. Hold the neutral keyframe for [NEUTRAL DURATION], hold the final keyframe for [FINAL DURATION], apply separate slow center-anchored zoompan movements, combine them with a 0.3-second fadeblack transition starting at [OFFSET], add a low-opacity red overlay around [RED CUE], add small `SERTAI LAB` text, and mux the first [DURATION] seconds of [SOURCE_AUDIO]. Output 720x1280, 24 fps, H.264 CRF 18, yuv420p, AAC 192 kbps, and faststart. Do not introduce any new visual element.
```

## Prompt 19 — Audio/video and character QC

```text
Audit the final assembly against the identity card and first keyframe. Confirm that the source song is the only soundtrack, audio and video durations match, the original audio start point is unchanged, and the export is stereo AAC at the requested bitrate. Separately score character consistency: face geometry, eyes, hair, skin, facial marks, wardrobe, accessories, body scale, scene, camera crop, and final-state timing. Return pass/fail plus one corrective action per failure. Do not change successful attributes.
```

## Prompt 20 — Skill improvement and final handoff

```text
Review this completed production and convert the stable decisions into reusable automation fields: source intake, audio analysis, identity card, fixed anchor block, platform adapter, reference image paths, seed, model version, cue timings, motion-poster fallback, export settings, QC, and packaging. Separate project-specific values from stable rules. Prepare a final handoff package containing the final MP4, source audio, reference images, identity sheet, first/final keyframes, prompt chain, technical report, QC report, and manifest. Clearly label whether the video is model-generated motion or motion-poster fallback.
```

## Quick platform recipe

| Platform | Identity control | Style/structure control | Starting strategy |
|---|---|---|---|
| Midjourney V7 | `--oref` + `--ow` | `--sref` + `--sw` | Same model, `--ar 9:16`, `--chaos 0`, low/medium `--stylize`, fixed seed |
| Midjourney V6/Niji 6 | `--cref` + `--cw` | `--sref` + `--sw` | Full identity with `--cw 100`; lower the weight for outfit variations |
| Stable Diffusion XL | IP-Adapter FaceID | IP-Adapter Plus + ControlNet if needed | Same checkpoint/scheduler/seed; FaceID ~0.60, low/medium denoise |
| ComfyUI | FaceID/IP-Adapter node | ControlNet pose/depth | Keep the identity reference fixed in a single node chain; put pose control in a separate node |

## Final decision rule

If the face, hair, jacket, crack pattern or body scale drifts in a frame, reduce the number of variables instead of lengthening the prompt. Fix the identity reference and anchor block first; then add the pose/lens/location variables back one at a time. The seed is only for controlled comparison; it is not the main carrier of character consistency.

## Sources

[1]: https://docs.midjourney.com/hc/en-us/articles/32162917505293-Character-Reference "Midjourney — Character Reference"
[2]: https://docs.midjourney.com/hc/en-us/articles/36285124473997-Omni-Reference "Midjourney — Omni Reference"
[3]: https://docs.midjourney.com/hc/en-us/articles/32859204029709-Parameter-List "Midjourney — Parameter List"
[4]: https://docs.midjourney.com/hc/en-us/articles/32604356340877-Seeds "Midjourney — Seeds"
[5]: https://huggingface.co/docs/diffusers/en/using-diffusers/ip_adapter "Hugging Face Diffusers — IP-Adapter"
