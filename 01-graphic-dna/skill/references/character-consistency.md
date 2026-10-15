# Character Consistency Reference

## Purpose

Keep the same original character as stable as possible across different poses, lenses, locations and final states. Instead of relying on a long, shifting text prompt, use a fixed **identity anchor block**, a single main reference image, a fixed model/version, a fixed aspect ratio and a controlled seed.

## Fixed and variable fields

**Fixed fields:** face geometry, eye shape and spacing, nose/chin profile, haircut and silhouette, skin undertone, fixed facial/crack marks, jacket or outfit silhouette, accessories, body scale and basic apparent age.

**Variable fields:** pose, gaze direction, lens and camera distance, a single facial expression, background density of the location, one light level and one main movement.

Do not change more than one variable in a single generation. First produce a single pose or lens variation while preserving identity; then change the environment.

## Midjourney V7

In V7, use `--oref [IMAGE_URL]` for a character/object reference and `--ow [1–1000]` to adjust its influence. Start with `--ow 250`; raise it if the face or outfit drifts, lower it if the reference composition locks the scene too much. Use the same model/version and `--ar 9:16`. For controlled A/B testing, use `--chaos 0`, low/medium `--stylize`, a fixed `--seed` and `--raw` if needed.

Style Reference is a separate job from appearance: control appearance with `--oref` and color/rendering language with `--sref`. Repeat the physical identity description of the prompt in every frame. A seed is not a character identity lock; it only makes it easier to compare test conditions.

```text
[IDENTITY ANCHOR BLOCK] [SCENE] [SHOT] [POSE] [GAZE] [LIGHTING] [SINGLE ACTION] --v 7 --ar 9:16 --oref [IDENTITY_REF_URL] --ow 250 --sref [STYLE_REF_URL] --sw 50 --stylize 100 --chaos 0 --seed [SEED] --no text,logo,watermark,labels,annotations,duplicate person,extra limbs,face drift,age drift,hairstyle drift,wardrobe drift
```

## Midjourney V6 / Niji 6

In V6 or Niji 6, use `--cref [IMAGE_URL]` and `--cw [0–100]`. Start with `--cw 100` for full face-hair-outfit transfer; lower the weight for controlled outfit or hair variations, but keep the physical anchor block in the prompt. Do not mix V7 and V6 parameters in the same prompt.

```text
[IDENTITY ANCHOR BLOCK] [SCENE] [SHOT] [POSE] [GAZE] [LIGHTING] [SINGLE ACTION] --v 6.1 --ar 9:16 --cref [IDENTITY_REF_URL] --cw 100 --sref [STYLE_REF_URL] --sw 50 --stylize 100 --chaos 0 --seed [SEED] --no text,logo,watermark,labels,annotations,duplicate person,extra limbs,face drift,age drift,hairstyle drift,wardrobe drift
```

## Stable Diffusion / SDXL

Keep the same checkpoint, VAE, sampler, scheduler, resolution, prompt order and seed throughout the series. Use IP-Adapter FaceID for facial identity, IP-Adapter Plus for overall look or material, and a single ControlNet condition for pose/structure. As starting values, use FaceID scale `0.60`, Plus scale `0.35–0.55` and img2img denoise `0.30–0.45`; these are controlled starting ranges, not mandatory universal values.

If the face changes, lower the denoise, simplify the reference crop so it shows the face and shoulders clearly, and keep the physical anchor at the very start of the prompt. If the pose changes, add ControlNet pose; do not try to solve identity and pose problems with a single mechanism. In series production, saving and reusing IP-Adapter image embeddings is efficient.

```text
[FIXED_IDENTITY_ANCHORS]. Original 9:16 portrait of [CHARACTER_ID] in [SCENE], [SHOT], [POSE], [GAZE]. Preserve exact face geometry, eye spacing, hair silhouette, skin undertone, facial marks, wardrobe silhouette, accessories, and body scale. Change only [ONE_VARIABLE].
Negative: face drift, age drift, hairstyle drift, wardrobe drift, changed crack pattern, duplicate person, extra limbs, plastic skin, text, logo, watermark, label, annotation.
Controls: same SDXL checkpoint, same VAE, same sampler, same scheduler, same resolution, same seed; IP-Adapter FaceID 0.60; optional IP-Adapter Plus 0.35–0.55; optional ControlNet pose/depth; img2img denoise 0.30–0.45.
```

## Series production protocol

1. First lock the character identity card and the single main reference image.
2. Generate a neutral portrait and a full-body sheet; write fixed anchors for face, hair, jacket and crack pattern.
3. Generate the first scene frame; make only pose, lens and location variable.
4. In the final-state frame, add only one controlled transformation.
5. Save every variation with the same naming scheme: `charid_scene_state_seed_model.png`.
6. When drift is detected, do not lengthen the prompt; reduce the number of variables and adjust the reference weight or denoise in a controlled way.
7. Do not move on to video generation before selecting the best two frames.

## Sources

[1]: https://docs.midjourney.com/hc/en-us/articles/32162917505293-Character-Reference "Midjourney — Character Reference"
[2]: https://docs.midjourney.com/hc/en-us/articles/36285124473997-Omni-Reference "Midjourney — Omni Reference"
[3]: https://docs.midjourney.com/hc/en-us/articles/32859204029709-Parameter-List "Midjourney — Parameter List"
[4]: https://docs.midjourney.com/hc/en-us/articles/32604356340877-Seeds "Midjourney — Seeds"
[5]: https://huggingface.co/docs/diffusers/en/using-diffusers/ip_adapter "Hugging Face Diffusers — IP-Adapter"
