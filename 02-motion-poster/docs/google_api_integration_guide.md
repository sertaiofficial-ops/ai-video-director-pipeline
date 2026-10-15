# Banana Pro + Omni/Veo One-Command API Integration

## Scope

`google_flow_banana_api.py` generates an image from a visual prompt with Nano Banana Pro and, in the same command, turns that image into a short video with Gemini Omni Flash or Vertex AI Veo 3.1 Fast, using it as the starting frame. The module prepares the prompt and reference images before generation and makes API calls only when `--execute` is given explicitly.

Google Flow Lab is a creative web app. This module does not log into the Flow Lab interface, does not use cookies/sessions and does not imitate its internal API. For programmatic integration it uses Google's documented developer API surfaces. To add videos produced manually in Flow Lab to the archive later, use the `--assets-dir` flow of the prompt packaging script.

## Adapters

| Adapter | Official model/endpoint | Authentication | Use |
|---|---|---|---|
| `BananaProAdapter` | Gemini Interactions API, `gemini-3-pro-image` | `GEMINI_API_KEY` or `GOOGLE_API_KEY` | Generates a PNG from a prompt + 0–N reference images |
| `GeminiOmniAdapter` | Gemini Interactions API, `gemini-omni-flash-preview` | `GEMINI_API_KEY` or `GOOGLE_API_KEY` | Generates a 3–10 s video from an image + prompt |
| `VertexVeoAdapter` | Vertex AI REST, `veo-3.1-fast-generate-001` | Application Default Credentials | Generates a 4/6/8 s MP4 from an image + prompt |

The official developer docs list Nano Banana Pro under the model code `gemini-3-pro-image` and Gemini Omni Flash under `gemini-omni-flash-preview`.[1] [2] The official model code for Veo 3.1 Fast is `veo-3.1-fast-generate-001`; 4/6/8-second video generation is documented with 9:16, 720p/1080p and 24 FPS options.[3]

## Installation

Python packages required for the Gemini API and Veo adapters:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-google-flow-banana.txt
```

Gemini Omni and Banana Pro need only `requests`. The Veo adapter uses Google Cloud Application Default Credentials and requires `google-auth`. If the output is returned as a Cloud Storage URI, `google-cloud-storage` is also required.

## Safe test: dry-run

See the plan without making network calls:

```bash
python3 google_flow_banana_api.py \
  --visual-prompt-file prompts/visual/M01.txt \
  --video-prompt-file prompts/video/M01.txt \
  --reference-image character_anchor.png \
  --video-provider omni \
  --output-dir ./google_flow_banana_dry_run \
  --dry-run
```

Dry-run writes the model, aspect ratio, duration, reference count, output path and external call status to `run.json`. It does not read credentials and does not touch the network.

## Real generation with the Gemini API

First put your key from Google AI Studio or your Gemini API account into an environment variable:

```bash
export GEMINI_API_KEY='your-key-in-shell-environment'
```

Then, for the Banana Pro image and the Omni video:

```bash
python3 google_flow_banana_api.py \
  --visual-prompt-file prompts/visual/M01.txt \
  --video-prompt-file prompts/video/M01.txt \
  --reference-image character_anchor.png \
  --video-provider omni \
  --output-dir ./google_flow_banana_output \
  --execute
```

The module first saves the Banana Pro image as `banana_pro_image.png`, then uses it as the Omni Flash image-to-video input and produces `video.mp4`. For large video outputs it uses URI delivery and polls until the file state becomes ACTIVE.[2]

Use `--skip-image` to start from an existing frame:

```bash
python3 google_flow_banana_api.py \
  --skip-image \
  --reference-image starting_frame.png \
  --video-prompt-file prompts/video/M01.txt \
  --video-provider omni \
  --execute
```

## Real generation with Vertex AI Veo 3.1 Fast

The Veo route needs a Google Cloud project and ADC:

```bash
gcloud auth application-default login
export GOOGLE_CLOUD_PROJECT='your-project-id'
```

Then:

```bash
python3 google_flow_banana_api.py \
  --skip-image \
  --reference-image starting_frame.png \
  --video-prompt-file prompts/video/M01.txt \
  --video-provider veo \
  --video-model veo-3.1-fast-generate-001 \
  --location us-central1 \
  --duration-seconds 8 \
  --output-dir ./veo_output \
  --execute
```

This adapter starts the image-to-video request, polls the long-running operation until it completes, and saves the returned inline base64 or `gs://` URI output as an MP4. Google Cloud's samples also show video generation as a long-running operation with status polling.[4]

## Settings and security

Without `--execute`, the default behavior is to write a dry-run plan. `--execute` explicitly enables a real, potentially paid generation call. API keys must never be written into source files, prompts, URLs or visible command-line arguments; use only the `GEMINI_API_KEY`/`GOOGLE_API_KEY` environment variables. Unless `--store` is given, Gemini Interactions requests are sent statelessly with `store=false`. Enable `--store` deliberately if you need server-side interaction history.

Make sure you hold the rights to any personal or licensed images before uploading them. The module does not try to bypass content policy; it reports any 4xx/5xx response from the API as is. Do not add cookies, CAPTCHA handling or account credentials to automate the Flow Lab UI session or its internal endpoints.

## Output contract

Every successful run produces the following files:

```text
google_flow_banana_output/
├── banana_pro_image.png   # if Banana Pro was used
├── video.mp4              # Omni or Veo output
└── run.json               # model, adapter, output and status record
```

`run.json` does not store the full prompt text or any secret key; it records only the prompt character count, the model and an operation summary.

## Sources

[1]: https://ai.google.dev/gemini-api/docs/models/gemini-3-pro-image "Google AI for Developers — Gemini 3 Pro image"
[2]: https://ai.google.dev/gemini-api/docs/omni "Google AI for Developers — Generate and edit videos with Gemini Omni Flash"
[3]: https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/veo/3-1-generate "Google Cloud — Veo 3.1 Generate"
[4]: https://docs.cloud.google.com/vertex-ai/generative-ai/docs/samples/googlegenaisdk-videogen-with-img "Google Cloud — Generate Videos from Images using Veo"
