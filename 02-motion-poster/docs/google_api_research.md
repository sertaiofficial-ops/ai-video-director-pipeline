# Google API Research — Banana Pro / Veo / Omni / Flow

## Verified findings

Google's developer documentation lists Nano Banana Pro under the model code `gemini-3-pro-image` as a professional image generation and editing model. The official image generation docs show the `interactions` endpoint in the Python and REST examples for the Gemini API, with the model name, text and base64 image inputs. Nano Banana Pro supports image generation; audio generation is not supported. Sources: [1] [2].

Google's Gemini API video documentation separates two main video generation surfaces: Gemini Omni Flash and Veo. The same page positions Omni Flash for multi-input generation, character consistency and multi-turn editing, and Veo 3.1 for features such as frame-specific generation, scene extension and image-based direction. Source: [3].

Google Cloud documentation gives the model code for Veo 3.1 Fast as `veo-3.1-fast-generate-001`. It supports image-to-video, first-and-last frame and reference images, with technical options of 4/6/8 seconds, 9:16 or 16:9, 720p/1080p and 24 FPS. The documentation describes the Google Cloud/Agent Platform surface for API access. Source: [4].

Google Flow is described by Google Labs as a creative video and storytelling studio. No general public API for Flow itself was found in the official developer docs. The module should therefore use the official Gemini API / Google Cloud video adapter instead of a fragile browser/scraping integration that logs into the Flow Lab UI or imitates its internal API; if output files are downloaded from Flow manually, add them to the package with `--assets-dir`. Google's Flow product page: [5].

## Integration decision

The module should provide three adapters: `GeminiImageAdapter` (Nano Banana Pro), `GeminiOmniVideoAdapter` (Gemini Omni Flash, if access and the model name are enabled on the account) and `VertexVeoAdapter` (Veo 3.1 Fast / Veo 3.1). The default safe behavior is dry-run. A real call is made only with an explicit `--execute` flag and when the required environment variables are present. Model names and the API surface should stay configurable; do not blindly trust hardcoded model names.

## Sources

[1]: https://ai.google.dev/gemini-api/docs/models/gemini-3-pro-image "Google AI for Developers — Gemini 3 Pro image"
[2]: https://ai.google.dev/gemini-api/docs/image-generation "Google AI for Developers — Nano Banana image generation"
[3]: https://ai.google.dev/gemini-api/docs/video "Google AI for Developers — Video generation in the Gemini API"
[4]: https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/veo/3-1-generate "Google Cloud — Veo 3.1 Generate"
[5]: https://labs.google/fx/tools/flow "Google Labs — Google Flow"

## Python SDK example

Google Cloud's official sample passes an image reference, a prompt and a `GenerateVideosConfig` through `genai.NewClient` / the Gen AI SDK; after the `GenerateVideos` call it polls with `GetVideosOperation` until the operation completes and returns `GeneratedVideos[0].Video.URI` from the result. Although the sample shows an older/preview model name, the adapter should accept `veo-3.1-fast-generate-001` from the current model docs or any model name supplied through configuration. Source: [6].

[6]: https://docs.cloud.google.com/vertex-ai/generative-ai/docs/samples/googlegenaisdk-videogen-with-img "Google Cloud — Generate Videos from Images using Veo"

## Gemini Omni Flash API

Gemini Omni Flash is listed on the official model page as a preview model with the code `gemini-omni-flash-preview`; it accepts text/image/video input, produces video output, and returns 720p/24 FPS video of 3–10 seconds. The official Omni docs show the `client.interactions.create(...)` call in the Python SDK, text + base64 image input for image-to-video, and the `generation_config.video_config.task = "image_to_video"` field. For portrait video, `response_format = {"type": "video", "aspect_ratio": "9:16"}` can be used. For large outputs `delivery="uri"` is recommended; poll the video file through the Files API until it is ACTIVE, then download it. Sources: [7] [8].

[7]: https://ai.google.dev/gemini-api/docs/models/gemini-omni-flash "Google AI for Developers — Gemini Omni Flash"
[8]: https://ai.google.dev/gemini-api/docs/omni "Google AI for Developers — Generate and edit videos with Gemini Omni Flash"
