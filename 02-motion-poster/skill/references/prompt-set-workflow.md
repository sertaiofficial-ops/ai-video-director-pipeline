# Prompt Set and API Production Workflow

## Identity and file contract

The image prompt and video prompt for the same production piece must carry the same ID. Example: the `M01` Banana Pro image prompt in `prompts/visual/M01.txt` matches the Flow/Omni/Veo video prompt in `prompts/video/M01.txt`. Treat the ID as the file identity, not the creative title in the prompt text.

| Asset | Required information | Initial output |
|---|---|---|
| Character | Face, hair, fixed marks, clothing, accessories, body scale | identity anchor image |
| Object | Form, material, surface, attachment points, light behavior | clean product/poster image |
| Environment | Geometry, vanishing point, floor, repeating light lines | environment plate |
| Video | Camera, single action, context, duration, end state, audio | MP4 |

## Sequential flow

1. Validate the ID, image prompt, video prompt and reference files.
2. Send the image prompt to Banana Pro; add identity or style references where possible.
3. Save the PNG output as the starting frame; if generation fails, do not proceed to the video call.
4. Select the video prompt with the same ID; pass the starting frame to Omni or Veo.
5. Check model limits: `image_to_video`, 9:16 and URI delivery in Omni; 4/6/8 seconds, 24 FPS, 9:16 or 16:9 in Veo.
6. Track the interaction/file or long-running operation state with bounded polling.
7. Normalize inline base64, URL, file URI or `gs://` output into a local media file.
8. Write model, adapter, aspect ratio, duration, reference count, output path and status to `run.json`; never write keys or the full private prompt.

## Prompt design standard

Image prompts follow this order: task/quality, subject or asset, fixed identity anchor, composition, lighting, material, environment, color, camera/lens, negative exclusions. Video prompts follow this order: role of the reference, duration and aspect ratio, shot/camera, the subject's single action, keeping the environment constant from start to finish, a 0–2s/2–6s/6–8s timeline, ambience/SFX and limits.

## Retries

For identity drift, first reduce the action and camera movement; do not start by switching models or adding random adjectives to the prompt. HTTP 401/403 is a credential problem; HTTP 400 is a payload/model/image problem; a timeout is an operation/polling problem. Never retry the same failed paid call indefinitely.
