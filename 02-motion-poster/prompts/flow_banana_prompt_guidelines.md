# Banana Pro + Google Flow Prompt Guidelines

## Image prompts

In image prompts, describe poster quality together with the generation task: one main subject, controlled composition, clear lens/lighting, material behavior, a limited palette, a clean silhouette, text-safe negative space, and exclusions such as `no readable text, no logo, no watermark`. In character sets, repeat the same identity anchor at the start of every prompt; limit variation to pose, gaze, lens or a single action.

## Google Flow / Veo prompt formula

The official Google Cloud guide structures effective Veo prompts in this order: **cinematography + subject + action + context + style & ambiance**. For camera language, explicit terms such as medium shot, close-up, wide shot, dolly, tracking, pan, tilt, arc shot, rack focus and shallow depth of field can be used. If audio is needed, request SFX, ambient noise, dialogue or music in separate sentences. Source: [1].

For Veo 3.1, the official guide lists 720p or 1080p, 16:9 or 9:16 and 4/6/8-second clip options; this pack assumes 9:16 and a short 8 seconds for vertical poster motion. The same guide explains transitions between two images with first-and-last-frame and the use of character, object, scene or style references with ingredients-to-video. Source: [1].

Google DeepMind's Veo page highlights the use of image references in Flow for scene/character/object consistency and style references, as well as Veo 3.1's synchronized audio generation and first/last frame transitions. Source: [2].

The official Gemini Omni prompt guide recommends stating the desired framing and camera movement in natural language, steering camera behavior with phrases such as `one continuous shot`, `oner`, `static`, `locked off`, `push in`, `punch in` and `dolly zoom`, and combining reference images with video, audio and style. In Omni, a short, intent-focused prompt can be expanded through iterative conversational corrections when needed. Source: [3].

## Omni + Veo Fast compatibility strategy

This pack uses no invalid platform-specific flags. Every video prompt follows this order in natural language: **shot/camera → subject identity → one action → environment → lighting/style → temporal beats → audio → exclusions**. For Omni, the creative intent and the single continuous shot are stated explicitly. For Veo Fast, the number of actions is reduced, time windows are kept short, and physical motion is defined by the camera and one action. Every prompt ends with `No dialogue, no readable text, no logos, no watermark, no captions. Vertical 9:16.`

## Reference usage protocol

Keep the following file roles when generating each image:

| Role | Use |
|---|---|
| Identity reference | Locks face, hair, skin, clothing, accessories and body scale |
| Style reference | Carries color, surface, lighting, poster finishing and atmosphere |
| Starting frame | Locks the clip's initial composition and character pose |
| Ending frame | Defines only the controlled final transformation |
| Audio reference | Carries tempo, energy and cue points |

Do not add more than one new character or location to any video prompt. Keep the same scene and main subject; describe only one action. Use the reference image as a continuity anchor for original generation, not as something to copy directly.

## Sources

[1]: https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-veo-3-1 "Google Cloud — The ultimate prompting guide for Veo 3.1"
[2]: https://deepmind.google/models/veo/ "Google DeepMind — Veo"
[3]: https://deepmind.google/models/gemini-omni/prompt-guide/ "Google DeepMind — How to create effective prompts with Gemini Omni"
