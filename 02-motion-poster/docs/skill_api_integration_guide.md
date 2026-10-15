# Permanent Google API Integration into the SERTAI Skill — Step-by-Step Guide

This guide explains how to add the `google_flow_banana_api.py` module permanently to the existing `sertai-graphic-dna-music-video` skill so the same API flow is reused whenever the skill is triggered. "Permanent" here means the module lives in the skill's `scripts/` folder and the API behavior lives in its `references/` files. No API key or user session is embedded in the skill.

## 1. Confirm the skill's actual folder

For skill-creator skills, `SKILL.md` is the required entry point; reusable code goes under `scripts/` and context-loaded documentation under `references/`. So first check that the folder exists:

```bash
export SKILL_DIR="$(pwd)/01-graphic-dna/skill"
ls "$SKILL_DIR/SKILL.md" "$SKILL_DIR/scripts" "$SKILL_DIR/references"
```

If you are on another computer, set `SKILL_DIR` to the skill path on that machine. No new skill is being created; since this iterates on an existing skill, do not run `init_skill.py` again. The skill-creator guidance also recommends updating and validating the resources of an existing skill instead of scaffolding a new one.

## 2. Copy the module into `scripts/`

Add the module to the skill and make it executable:

```bash
cp google_flow_banana_api.py "$SKILL_DIR/scripts/google_flow_banana_api.py"
chmod +x "$SKILL_DIR/scripts/google_flow_banana_api.py"
```

The module contains three adapters. `BananaProAdapter` uses the `gemini-3-pro-image` model in the Gemini Interactions API; `GeminiOmniAdapter` uses `gemini-omni-flash-preview`; and `VertexVeoAdapter` uses `veo-3.1-fast-generate-001` in Vertex AI. Model codes and capabilities come from the official Google documentation.[1] [2] [3]

## 3. Put the API notes under `references/`

Do not bloat the skill body with unnecessary detail. Put variant information such as setup, endpoints, polling, security and the Flow Lab UI boundary into reference files:

```bash
cp google_flow_banana_api_guide.md "$SKILL_DIR/references/google-api-integration.md"
cp google_api_research.md "$SKILL_DIR/references/google-api-research.md"
cp requirements-google-flow-banana.txt "$SKILL_DIR/references/google-api-requirements.txt"
```

This split follows the progressive disclosure principle: when the skill is triggered, the short workflow is read first, and the API reference is loaded only when API integration is needed.

## 4. Update the `SKILL.md` frontmatter and routing

The frontmatter description decides when the skill is triggered. Mention source graphic DNA, Banana Pro poster prompts, Flow/Omni/Veo video prompts and API automation together:

```yaml
---
name: sertai-graphic-dna-music-video
description: Extract graphic DNA from a source video or social media link; adapt it into an original visual-music language for the SERTAI universe; produce Banana Pro poster prompts, Google Flow Lab Omni/Veo Fast video prompts and official Gemini/Vertex API automation. Use when MP4/MOV files, Instagram Reels/TikTok/YouTube links, style breakdowns, AI music prompts, image-to-video or packaged deliverables are requested.
---
```

Add only routing to the body. Keep API details in `references/google-api-integration.md`:

```markdown
### Official API integration

`google_flow_banana_api.py` does not scrape the Flow Lab UI. It uses the Gemini Interactions API for Nano Banana Pro and Gemini Omni, and a Vertex AI REST/ADC adapter for Veo. Real network calls happen only with an explicit `--execute`; the default is dry-run. Detailed setup and security notes are in `references/google-api-integration.md`; package dependencies are in `references/google-api-requirements.txt`.
```

Do not keep long REST examples, full model responses or secrets such as keys in the skill body. They increase context cost and can lead to secrets being shared by accident.

## 5. Install dependencies

The Gemini Interactions route needs `requests`; the Vertex route needs `google-auth`; if Veo returns a `gs://` URI, `google-cloud-storage` is also required:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-google-flow-banana.txt
```

Although Google's official samples use the Gen AI SDK, this module handles Gemini Interactions and Vertex calls directly with HTTP/ADC adapters. This keeps the single-file CLI and limits the impact of SDK version changes.

## 6. Re-validate the skill

Run two checks after every change:

```bash
python3 -m py_compile "$SKILL_DIR/scripts/google_flow_banana_api.py"
python3 "$SKILL_CREATOR_DIR/scripts/quick_validate.py" \
  sertai-graphic-dna-music-video
```

The `Skill is valid!` output means the frontmatter and skill directory structure follow the rules. It does not mean the API key is valid; it is only a structural validation of the skill package.

## 7. Check with a dry-run before real generation

First test the Omni plan without touching the network:

```bash
python3 "$SKILL_DIR/scripts/google_flow_banana_api.py" \
  --visual-prompt-file ./prompts/visual/M01.txt \
  --video-prompt-file ./prompts/video/M01.txt \
  --reference-image ./character_anchor.png \
  --video-provider omni \
  --output-dir ./google_flow_banana_dry_run \
  --dry-run
```

For the Veo route you can use an existing starting frame without regenerating the image:

```bash
python3 "$SKILL_DIR/scripts/google_flow_banana_api.py" \
  --skip-image \
  --reference-image ./starting_frame.png \
  --video-prompt-file ./prompts/video/M01.txt \
  --video-provider veo \
  --video-model veo-3.1-fast-generate-001 \
  --project "$GOOGLE_CLOUD_PROJECT" \
  --location us-central1 \
  --output-dir ./veo_dry_run \
  --dry-run
```

Dry-run writes only the config and output plan; it does not call a model, upload files or start a paid job.

## 8. Provide credentials at generation time

Do not write the Gemini API key into a skill file. Keep it in an environment variable:

```bash
export GEMINI_API_KEY='your-key-in-shell-environment'
```

Start real Omni generation only with an explicit `--execute`:

```bash
python3 "$SKILL_DIR/scripts/google_flow_banana_api.py" \
  --visual-prompt-file ./prompts/visual/M01.txt \
  --video-prompt-file ./prompts/video/M01.txt \
  --reference-image ./character_anchor.png \
  --video-provider omni \
  --output-dir ./google_flow_banana_output \
  --execute
```

For Veo, set up Application Default Credentials:

```bash
gcloud auth application-default login
export GOOGLE_CLOUD_PROJECT='your-project-id'
```

Then:

```bash
python3 "$SKILL_DIR/scripts/google_flow_banana_api.py" \
  --skip-image \
  --reference-image ./starting_frame.png \
  --video-prompt-file ./prompts/video/M01.txt \
  --video-provider veo \
  --video-model veo-3.1-fast-generate-001 \
  --location us-central1 \
  --duration-seconds 8 \
  --output-dir ./veo_output \
  --execute
```

## 9. Keep the boundary between Flow Lab and the API

Google Flow Lab is Google Labs' creative web app. This module does not connect to a Flow Lab account with cookies, does not scrape internal endpoints, and does not fake CAPTCHAs or user sessions. The official developer surfaces are the Gemini Interactions API and Vertex AI. To add MP4s produced manually in the Flow Lab UI to the same project's prompt pack, use `run_banana_flow_prompt_pack.py --assets-dir ./generated_assets`.

This boundary matters for a permanent integration: the skill does not break when the web app's internal API changes; if the API contract changes, only the relevant adapter needs updating.

## 10. Versioning and maintenance

On every API model change, update three things together: the short adapter routing in `SKILL.md`, the model/endpoint note in `references/google-api-integration.md`, and the default model in `google_flow_banana_api.py`. After the change, run dry-run, `py_compile` and `quick_validate`. Run a real generation test only when it has been explicitly authorized with the user's account and budget.

Inspect `run.json` to see which adapter was selected and which output was planned. The module does not store keys or the full prompt text. Use `--store` only if you really want Interactions history kept server-side; the default stateless flow sends `store=false`.[2]

## 11. How the skill will be used automatically in the future

When a new task invokes the skill with an explicit request such as "generate the Banana Pro image, turn it into a video with Omni/Veo, use the real API", the skill first reads `references/google-api-integration.md`, checks that credentials are present and proposes a dry-run by default. If the required key or ADC is missing, it does not make up values; it asks the user for a secure setup. Even when credentials are present, it does not start a paid call unless `--execute` is given explicitly.

This structure separates the skill's creative decisions from deterministic API operations: the agent designs the prompt and references; the Python adapter sends them to the right endpoint, polls the operation/file and saves the output; the final edit and asset packaging are separate local steps.

## Sources

[1]: https://ai.google.dev/gemini-api/docs/models/gemini-3-pro-image "Google AI for Developers — Gemini 3 Pro image"
[2]: https://ai.google.dev/gemini-api/docs/omni "Google AI for Developers — Generate and edit videos with Gemini Omni Flash"
[3]: https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/veo/3-1-generate "Google Cloud — Veo 3.1 Generate"
[4]: https://docs.cloud.google.com/vertex-ai/generative-ai/docs/samples/googlegenaisdk-videogen-with-img "Google Cloud — Generate Videos from Images using Veo"
