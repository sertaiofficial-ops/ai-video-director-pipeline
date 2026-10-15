# Prompt Blueprints

This file standardizes prompt production in the SERTAI graphic DNA skill. Pick an adapter per platform; load the detailed rules in `references/character-consistency.md` when needed. Fill the bracketed fields with project findings; do not blindly carry example physical traits over to other characters.

## 1. Identity anchor block

Repeat the same physical description at the start of the prompt for every series:

```text
[CHARACTER_ID] is an original recurring character. Preserve exact face geometry, eye shape and spacing, nose bridge, cheekbones, jaw and chin, skin undertone, hair cut and silhouette, hair texture, fixed facial marks and their approximate locations, wardrobe silhouette and seams, accessories, body scale, and apparent age impression. These identity anchors are fixed across every image. Change only [ONE_VARIABLE].
```

## 2. Negative drift block

```text
No face drift, no age drift, no hairstyle drift, no wardrobe drift, no changed facial marks, no changed crack pattern, no body-scale drift, no duplicate person, no extra limbs, no extra fingers, no random armor, no plastic skin, no cheerful expression, no readable text, no logo, no watermark, no label, no annotation, no new location.
```

## 3. Midjourney V7 / Omni Reference

```text
[IDENTITY_ANCHOR_BLOCK] Original cinematic 9:16 portrait of [CHARACTER_ID] in [SCENE], [SHOT], [POSE], [GAZE], [LIGHTING], [SINGLE_ACTION]. Preserve all fixed identity anchors; change only [ONE_VARIABLE]. [STYLE_SPEC]. [NEGATIVE_DRIFT_BLOCK] --v 7 --ar 9:16 --oref [IDENTITY_REF_URL] --ow 250 --sref [STYLE_REF_URL] --sw 50 --stylize 100 --chaos 0 --seed [SEED] --no text,logo,watermark,labels,annotations,duplicate person,extra limbs,face drift,age drift,hairstyle drift,wardrobe drift
```

Start with `--ow 250`, `--chaos 0` and low/medium `--stylize`. In V7, `--oref` works with a single main character/object reference. Keep the style reference separate from the character reference.

## 4. Midjourney V6 / Niji 6

```text
[IDENTITY_ANCHOR_BLOCK] Original cinematic 9:16 portrait of [CHARACTER_ID] in [SCENE], [SHOT], [POSE], [GAZE], [LIGHTING], [SINGLE_ACTION]. Preserve all fixed identity anchors; change only [ONE_VARIABLE]. [STYLE_SPEC]. [NEGATIVE_DRIFT_BLOCK] --v 6.1 --ar 9:16 --cref [IDENTITY_REF_URL] --cw 100 --sref [STYLE_REF_URL] --sw 50 --stylize 100 --chaos 0 --seed [SEED] --no text,logo,watermark,labels,annotations,duplicate person,extra limbs,face drift,age drift,hairstyle drift,wardrobe drift
```

When controlled variation in outfit or hair is needed, lower `--cw`; do not remove the physical anchor block from the prompt.

## 5. Stable Diffusion XL / IP-Adapter

```text
[IDENTITY_ANCHOR_BLOCK] Original 9:16 portrait of [CHARACTER_ID] in [SCENE], [SHOT], [POSE], [GAZE]. Preserve face geometry, eye spacing, hair silhouette, skin undertone, fixed facial marks, wardrobe silhouette, accessories, and body scale. Change only [ONE_VARIABLE]. [STYLE_SPEC].

Negative prompt: [NEGATIVE_DRIFT_BLOCK]
Controls: same SDXL checkpoint, same VAE, same sampler, same scheduler, same resolution, same seed; IP-Adapter FaceID scale 0.60; optional IP-Adapter Plus scale 0.35–0.55; optional single ControlNet pose/depth condition; img2img denoise 0.30–0.45.
```

FaceID should be used for facial identity, Plus for material/style, and ControlNet for pose/structure, each as a separate job. Do not try to solve identity and pose problems with a single control signal.

## 6. Neutral 9:16 first frame

```text
Create the first keyframe for an original 9:16 vertical SERTAI teaser using [CHARACTER_ID] and [IDENTITY_REF]. Repeat the exact identity anchor block first. Place the character in [SCENE]. Preserve [FACE_GEOMETRY], [EYE_SPACING], [HAIR_SILHOUETTE], [SKIN_UNDERTONE], [FIXED_MARKS], [WARDROBE], [ACCESSORIES], and [BODY_SCALE]. Camera: [SHOT_SIZE], eye-level, [LENS_FEEL], [FOCAL_PLACEMENT], [NEGATIVE_SPACE]. Vary only [POSE] and [GAZE]. No readable text, no logo, no watermark, no label, no annotation.
```

## 7. Final-state frame

```text
Edit [FIRST_KEYFRAME] into the controlled final state of the same shot. Preserve the exact face geometry, eye spacing, hair silhouette, skin undertone, facial marks, crack pattern, jacket seams, accessories, body scale, crop, camera angle, environment geometry, and light direction. Change only [FINAL_SINGLE_CHANGE]. Make it look like the same frame a moment later, not a redesign. No new character, no new location, no new outfit, no text, no logo, no watermark, no annotation.
```

## 8. Image-to-video

```text
An original [DURATION]-second vertical SERTAI teaser using the exact input frame as identity and composition reference. Preserve [IDENTITY_ANCHOR_BLOCK] in every frame. The same [ENVIRONMENT_ANCHORS] remain visible from start to finish.

0.0–[A] seconds: [START_STATE] with only [MICRO_MOTION]; camera [CAMERA_MOVE]. [A]–[B] seconds: one and only one action, [SINGLE_ACTION], along [TRAJECTORY]. [B]–[C] seconds: [CONTROLLED_TENSION_CHANGE] happens once. [C]–END: [FINAL_STATE] resolves toward near-black. Maintain face, hair, wardrobe, body scale, light direction, camera crop, and location continuity. No new characters, no scene change, no readable text, no logos, no watermark, no captions, no dialogue, no singing. No background music.
```

## 9. Motion-poster fallback

```text
Design an 8-second motion-poster fallback using [FIRST_KEYFRAME] and [FINAL_KEYFRAME]. Apply one slow center-anchored push-in, two low-opacity cyan atmosphere flashes at [CUE_1] and [CUE_2], a 0.3-second fade-black transition at [OFFSET], and one restrained red overlay around [RED_CUE]. End on [FINAL_KEYFRAME] and resolve toward black. Keep face readability and identity unchanged. This is a proof-of-concept fallback, not physically generated motion.
```

## 10. QC prompt

```text
Compare [OUTPUT] against [IDENTITY_REF] and [FIRST_KEYFRAME]. Score face geometry, eye spacing, hair silhouette, skin undertone, fixed marks, crack pattern, wardrobe, accessories, body scale, pose, crop, environment geometry, light direction, palette, and final-state timing. Report only deviations, assign severity 1–3, and write one minimal corrective prompt per failure. Do not redesign successful attributes.
```

## Platform notes

- In Midjourney, keep parameters at the end of the prompt; use `--oref` for V7 and `--cref` for V6/Niji 6.
- In Stable Diffusion, keep checkpoint, VAE, sampler, scheduler, resolution, prompt order and seed fixed throughout the series.
- A seed alone is not a character lock; the reference/adapter and the fixed anchor block are the main carriers.
- Change only one main variable per frame; if drift occurs, reduce the variables instead of lengthening the prompt.

## Sources

[1]: https://docs.midjourney.com/hc/en-us/articles/32162917505293-Character-Reference "Midjourney — Character Reference"
[2]: https://docs.midjourney.com/hc/en-us/articles/36285124473997-Omni-Reference "Midjourney — Omni Reference"
[3]: https://docs.midjourney.com/hc/en-us/articles/32859204029709-Parameter-List "Midjourney — Parameter List"
[4]: https://docs.midjourney.com/hc/en-us/articles/32604356340877-Seeds "Midjourney — Seeds"
[5]: https://huggingface.co/docs/diffusers/en/using-diffusers/ip_adapter "Hugging Face Diffusers — IP-Adapter"
