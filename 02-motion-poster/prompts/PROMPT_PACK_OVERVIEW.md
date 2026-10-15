# Banana Pro × Google Flow Lab Prompt Pack

## Pack purpose

This pack contains 20 visual assets that belong to the same original SERTAI poster universe and 20 matched video prompts for animating them in Google Flow Lab. The split is **5 male characters, 5 female characters, 5 objects and 5 fictional/atmospheric environments**.

The image prompts are written in natural language for Banana Pro, aimed at poster quality and 9:16 vertical use. Each video prompt treats the matching image as its single reference and describes an 8-second, single continuous shot with one main action, controlled camera movement and a final state.

## Order of use

First pick an ID and asset role from `prompt_set_matrix.md`. Then give the prompt with the same ID in `20_banana_pro_visual_prompts.md` to Banana Pro and generate the image as a 9:16 poster frame. Save the result with the ID in the file name. Next, upload the same image to Flow Lab as a reference and use the video prompt with the same ID in `20_flow_omni_veo_fast_video_prompts.md`.

In Flow, add the image as a starting frame or ingredient where possible. In Omni, state the single continuous shot and reference preservation in natural language; in Veo Fast, keep one action, short time windows and a clear camera move. Do not use invalid model-specific flags on either platform. If you do not want generated audio, keep the ambient sound line in the prompt and replace the video's audio with your own music afterwards.

## Character continuity

When generating a character a second time, use the same ID, the same physical identity anchor and the same image reference. Change only one of pose, gaze, lens, single action or background density. Restate face, hair, skin, fixed marks, clothing, accessories and body scale in every prompt. Do not delete the "preserve the reference identity and composition" sentence from the video prompt.

## Poster quality

For a polished look, keep a single focal point, separate the face or object silhouette from the background, use red/green/chrome only as limited accents, describe material behavior physically, and do not ask the model to draw readable text in the image. If a title, artist name or logo is needed, add it in a separate typography layer.

## File manifest

| File | Contents |
|---|---|
| `20_banana_pro_visual_prompts.md` | 5 male + 5 female + 5 object + 5 environment image prompts |
| `20_flow_omni_veo_fast_video_prompts.md` | 20 video prompts matched to the images by ID |
| `prompt_set_matrix.md` | Asset, identity and video action matrix |
| `flow_banana_prompt_guidelines.md` | Cross-platform common ground, camera language, reference and audio rules |
| `character_consistency_research.md` | Midjourney/Diffusers notes on character continuity from official sources |
| `SKILL.md` | Updated SERTAI graphic DNA skill |

## Sources

[1]: https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-veo-3-1 "Google Cloud — The ultimate prompting guide for Veo 3.1"
[2]: https://deepmind.google/models/veo/ "Google DeepMind — Veo"
[3]: https://deepmind.google/models/gemini-omni/prompt-guide/ "Google DeepMind — How to create effective prompts with Gemini Omni"
[4]: https://docs.midjourney.com/hc/en-us/articles/36285124473997-Omni-Reference "Midjourney — Omni Reference"
[5]: https://huggingface.co/docs/diffusers/en/using-diffusers/ip_adapter "Hugging Face Diffusers — IP-Adapter"
