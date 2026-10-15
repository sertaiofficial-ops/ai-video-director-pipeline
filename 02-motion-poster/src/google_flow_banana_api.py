#!/usr/bin/env python3
"""Single-command Banana Pro + Gemini Omni/Veo API integration.

Supported routes
----------------
1. Banana Pro image generation through the Gemini Interactions API.
2. Gemini Omni Flash image-to-video through the Gemini Interactions API.
3. Veo 3.1 Fast image-to-video through the Vertex AI REST endpoint.

The public Google Flow Lab UI is not scraped or automated here. Flow is a
creative application, while this module calls the documented developer APIs.
Set --execute explicitly before any paid/credentialed request.

Examples
--------
Dry-run (safe, no network):
    python google_flow_banana_api.py --visual-prompt-file prompts/visual/M01.txt \
        --video-prompt-file prompts/video/M01.txt --dry-run

Gemini API route:
    GEMINI_API_KEY=... python google_flow_banana_api.py \
        --visual-prompt-file prompts/visual/M01.txt \
        --video-prompt-file prompts/video/M01.txt \
        --reference-image character.png --video-provider omni --execute

Vertex AI route:
    gcloud auth application-default login
    GOOGLE_CLOUD_PROJECT=my-project python google_flow_banana_api.py \
        --visual-prompt-file prompts/visual/M01.txt \
        --video-prompt-file prompts/video/M01.txt \
        --reference-image character.png --video-provider veo \
        --location us-central1 --execute
"""
from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import requests


GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
VERTEX_API_BASE = "https://{location}-aiplatform.googleapis.com/v1"


class ApiIntegrationError(RuntimeError):
    """Raised for configuration, HTTP, or response-shape failures."""


@dataclass
class Config:
    visual_prompt_file: Path | None
    video_prompt_file: Path | None
    visual_prompt: str | None
    video_prompt: str | None
    reference_images: list[Path]
    output_dir: Path
    image_model: str
    video_provider: str
    video_model: str | None
    aspect_ratio: str
    image_size: str
    duration_seconds: int
    location: str
    project: str | None
    poll_seconds: float
    timeout_seconds: float
    execute: bool
    dry_run: bool
    store: bool
    skip_image: bool


def parse_args() -> Config:
    parser = argparse.ArgumentParser(description="Banana Pro + Omni/Veo single-command API integration")
    parser.add_argument("--visual-prompt-file", type=Path)
    parser.add_argument("--video-prompt-file", type=Path)
    parser.add_argument("--visual-prompt")
    parser.add_argument("--video-prompt")
    parser.add_argument("--reference-image", type=Path, action="append", default=[])
    parser.add_argument("--output-dir", type=Path, default=Path("./google_flow_banana_output"))
    parser.add_argument("--image-model", default=os.getenv("GEMINI_IMAGE_MODEL", "gemini-3-pro-image"))
    parser.add_argument("--video-provider", choices=("omni", "veo"), default=os.getenv("VIDEO_PROVIDER", "omni"))
    parser.add_argument("--video-model")
    parser.add_argument("--aspect-ratio", default="9:16", choices=("9:16", "16:9"))
    parser.add_argument("--image-size", default="2K", choices=("1K", "2K", "4K"))
    parser.add_argument("--duration-seconds", type=int, default=8, choices=(4, 6, 8, 10))
    parser.add_argument("--location", default=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"))
    parser.add_argument("--project", default=os.getenv("GOOGLE_CLOUD_PROJECT"))
    parser.add_argument("--poll-seconds", type=float, default=5.0)
    parser.add_argument("--timeout-seconds", type=float, default=900.0)
    parser.add_argument("--execute", action="store_true", help="Explicitly enable the real (paid/authenticated) API call")
    parser.add_argument("--dry-run", action="store_true", help="Write the plan and payload summary without any network call")
    parser.add_argument("--store", action="store_true", help="Enable server-side storage of the Gemini interaction")
    parser.add_argument("--skip-image", action="store_true", help="Skip Banana Pro image generation; use an existing first frame")
    args = parser.parse_args()
    if not (args.visual_prompt or args.visual_prompt_file) and not args.skip_image:
        parser.error("Image generation requires --visual-prompt or --visual-prompt-file; use --skip-image to skip it.")
    if not (args.video_prompt or args.video_prompt_file):
        parser.error("Video generation requires --video-prompt or --video-prompt-file.")
    return Config(
        visual_prompt_file=args.visual_prompt_file,
        video_prompt_file=args.video_prompt_file,
        visual_prompt=args.visual_prompt,
        video_prompt=args.video_prompt,
        reference_images=[path.resolve() for path in args.reference_image],
        output_dir=args.output_dir.resolve(),
        image_model=args.image_model,
        video_provider=args.video_provider,
        video_model=args.video_model,
        aspect_ratio=args.aspect_ratio,
        image_size=args.image_size,
        duration_seconds=args.duration_seconds,
        location=args.location,
        project=args.project,
        poll_seconds=args.poll_seconds,
        timeout_seconds=args.timeout_seconds,
        execute=args.execute,
        dry_run=args.dry_run,
        store=args.store,
        skip_image=args.skip_image,
    )


def read_prompt(value: str | None, path: Path | None, label: str) -> str:
    if value:
        return value.strip()
    if path is None:
        raise ApiIntegrationError(f"{label} not provided.")
    if not path.exists():
        raise ApiIntegrationError(f"{label} not found: {path}")
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        raise ApiIntegrationError(f"{label} is empty: {path}")
    return text


def require_files(paths: Iterable[Path]) -> None:
    for path in paths:
        if not path.exists() or not path.is_file():
            raise ApiIntegrationError(f"Reference image not found: {path}")


def mime_type(path: Path) -> str:
    return mimetypes.guess_type(path.name)[0] or "application/octet-stream"


def image_part(path: Path) -> dict[str, str]:
    return {
        "type": "image",
        "mime_type": mime_type(path),
        "data": base64.b64encode(path.read_bytes()).decode("ascii"),
    }


def request_json(method: str, url: str, *, headers: dict[str, str], payload: dict[str, Any] | None = None, timeout: float = 120.0) -> dict[str, Any]:
    response = requests.request(method, url, headers=headers, json=payload, timeout=timeout)
    if response.status_code >= 400:
        detail = response.text[:4000]
        raise ApiIntegrationError(f"HTTP {response.status_code} — {url}\n{detail}")
    try:
        return response.json()
    except ValueError as exc:
        raise ApiIntegrationError(f"Could not parse JSON response — {url}: {response.text[:1000]}") from exc


def download_url(url: str, *, headers: dict[str, str], output: Path, timeout: float = 300.0) -> None:
    response = requests.get(url, headers=headers, timeout=timeout)
    if response.status_code >= 400:
        raise ApiIntegrationError(f"Media download failed: HTTP {response.status_code} — {url}\n{response.text[:1000]}")
    output.write_bytes(response.content)


def decode_inline_media(data: str, output: Path) -> None:
    try:
        output.write_bytes(base64.b64decode(data))
    except Exception as exc:  # pragma: no cover - defensive response handling
        raise ApiIntegrationError(f"Could not decode base64 media output: {output}") from exc


def walk_dicts(value: Any) -> Iterable[dict[str, Any]]:
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk_dicts(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_dicts(child)


def find_media(response: dict[str, Any], media_type: str) -> tuple[str, str] | None:
    """Return ('data'|'uri', value) from SDK-like or REST-like responses."""
    for item in walk_dicts(response):
        item_type = str(item.get("type", "")).lower()
        if item_type != media_type:
            continue
        for key in ("data", "uri", "url"):
            value = item.get(key)
            if isinstance(value, str) and value:
                return ("data" if key == "data" else "uri", value)
    convenience_key = "output_image" if media_type == "image" else "output_video"
    convenience = response.get(convenience_key)
    if isinstance(convenience, dict):
        if convenience.get("data"):
            return ("data", convenience["data"])
        if convenience.get("uri"):
            return ("uri", convenience["uri"])
    return None


def load_gemini_key() -> str:
    key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not key:
        raise ApiIntegrationError("GEMINI_API_KEY or GOOGLE_API_KEY environment variable not found.")
    return key


class GeminiInteractionsClient:
    def __init__(self, api_key: str, *, timeout: float, store: bool) -> None:
        self.api_key = api_key
        self.timeout = timeout
        self.store = store
        self.headers = {"x-goog-api-key": api_key, "Content-Type": "application/json"}

    def create(self, payload: dict[str, Any]) -> dict[str, Any]:
        payload = {**payload, "store": self.store}
        return request_json("POST", f"{GEMINI_BASE_URL}/interactions", headers=self.headers, payload=payload, timeout=self.timeout)

    def get_interaction(self, interaction_id: str) -> dict[str, Any]:
        return request_json("GET", f"{GEMINI_BASE_URL}/interactions/{interaction_id}", headers=self.headers, timeout=self.timeout)

    def get_file_state(self, file_name: str) -> dict[str, Any]:
        clean = file_name.rsplit("/", 1)[-1]
        return request_json("GET", f"{GEMINI_BASE_URL}/files/{clean}", headers=self.headers, timeout=self.timeout)

    def download_file(self, file_name: str, output: Path) -> None:
        clean = file_name.rsplit("/", 1)[-1]
        download_url(f"{GEMINI_BASE_URL}/files/{clean}:download?alt=media", headers=self.headers, output=output, timeout=self.timeout)


def save_gemini_media(client: GeminiInteractionsClient, response: dict[str, Any], media_type: str, output: Path, *, poll_seconds: float, timeout_seconds: float) -> dict[str, Any]:
    found = find_media(response, media_type)
    if found:
        kind, value = found
        if kind == "data":
            decode_inline_media(value, output)
            return {"delivery": "inline", "output": str(output)}
        if value.startswith("http://") or value.startswith("https://"):
            download_url(value, headers=client.headers, output=output, timeout=client.timeout)
            return {"delivery": "url", "output": str(output), "uri": value}
        started = time.monotonic()
        while time.monotonic() - started <= timeout_seconds:
            state = client.get_file_state(value)
            state_name = str(state.get("state", "")).upper()
            if state_name in ("ACTIVE", "SUCCEEDED", "COMPLETED"):
                client.download_file(value, output)
                return {"delivery": "file_uri", "output": str(output), "uri": value, "state": state_name}
            if state_name in ("FAILED", "ERROR"):
                raise ApiIntegrationError(f"Google file processing failed: {json.dumps(state, ensure_ascii=False)[:2000]}")
            time.sleep(poll_seconds)
        raise ApiIntegrationError(f"Google file URI polling timeout: {value}")

    status = str(response.get("status", "")).lower()
    interaction_id = response.get("id")
    if interaction_id and status not in ("completed", "failed"):
        started = time.monotonic()
        while time.monotonic() - started <= timeout_seconds:
            time.sleep(poll_seconds)
            response = client.get_interaction(str(interaction_id))
            found = find_media(response, media_type)
            if found:
                return save_gemini_media(client, response, media_type, output, poll_seconds=poll_seconds, timeout_seconds=timeout_seconds)
            if str(response.get("status", "")).lower() == "failed":
                break
    raise ApiIntegrationError(f"No {media_type} output found in response: {json.dumps(response, ensure_ascii=False)[:3000]}")


class BananaProAdapter:
    def __init__(self, client: GeminiInteractionsClient, model: str, *, aspect_ratio: str, image_size: str) -> None:
        self.client = client
        self.model = model
        self.aspect_ratio = aspect_ratio
        self.image_size = image_size

    def generate(self, prompt: str, references: list[Path], output: Path, *, poll_seconds: float, timeout_seconds: float) -> dict[str, Any]:
        inputs: list[dict[str, str]] = [{"type": "text", "text": prompt}]
        inputs.extend(image_part(path) for path in references)
        payload = {
            "model": self.model,
            "input": inputs,
            "response_format": {"type": "image", "mime_type": "image/png", "aspect_ratio": self.aspect_ratio, "image_size": self.image_size},
        }
        response = self.client.create(payload)
        result = save_gemini_media(self.client, response, "image", output, poll_seconds=poll_seconds, timeout_seconds=timeout_seconds)
        return {"model": self.model, "request": {"reference_count": len(references), "aspect_ratio": self.aspect_ratio, "image_size": self.image_size}, **result}


class GeminiOmniAdapter:
    def __init__(self, client: GeminiInteractionsClient, model: str, *, aspect_ratio: str, duration_seconds: int) -> None:
        self.client = client
        self.model = model
        self.aspect_ratio = aspect_ratio
        self.duration_seconds = duration_seconds

    def generate(self, prompt: str, image: Path, output: Path, *, poll_seconds: float, timeout_seconds: float) -> dict[str, Any]:
        if self.duration_seconds > 10:
            raise ApiIntegrationError("Gemini Omni Flash duration must be between 3 and 10 seconds.")
        inputs = [image_part(image), {"type": "text", "text": prompt}]
        payload = {
            "model": self.model,
            "input": inputs,
            "response_format": {"type": "video", "delivery": "uri", "aspect_ratio": self.aspect_ratio},
            "generation_config": {"video_config": {"task": "image_to_video"}},
        }
        response = self.client.create(payload)
        result = save_gemini_media(self.client, response, "video", output, poll_seconds=poll_seconds, timeout_seconds=timeout_seconds)
        return {"provider": "gemini_interactions", "model": self.model, "duration_seconds": self.duration_seconds, **result}


class VertexVeoAdapter:
    """Minimal Vertex AI REST adapter for Veo 3.1 Fast.

    Vertex credentials come from Application Default Credentials. Response
    parsing accepts the common `generatedVideos`/`videos` shapes and both
    inline base64 and GCS URI deliveries. If the project returns a different
    response shape, the error includes the response for a focused adapter fix.
    """

    def __init__(self, project: str | None, location: str, model: str, *, timeout: float, duration_seconds: int, aspect_ratio: str) -> None:
        if not project:
            raise ApiIntegrationError("Veo requires GOOGLE_CLOUD_PROJECT or --project.")
        self.project = project
        self.location = location
        self.model = model
        self.timeout = timeout
        self.duration_seconds = duration_seconds
        self.aspect_ratio = aspect_ratio
        try:
            import google.auth  # type: ignore
            from google.auth.transport.requests import AuthorizedSession  # type: ignore
            credentials, detected_project = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
            self.project = project or detected_project
            self.session = AuthorizedSession(credentials)
        except ImportError as exc:
            raise ApiIntegrationError("The Veo adapter requires google-auth: pip install google-auth") from exc
        except Exception as exc:
            raise ApiIntegrationError("Application Default Credentials not found; run gcloud auth application-default login.") from exc
        self.base = VERTEX_API_BASE.format(location=location)

    def generate(self, prompt: str, image: Path, output: Path, *, poll_seconds: float, timeout_seconds: float) -> dict[str, Any]:
        if self.duration_seconds not in (4, 6, 8):
            raise ApiIntegrationError("Veo 3.1 Fast duration must be 4, 6 or 8.")
        model_path = f"projects/{self.project}/locations/{self.location}/publishers/google/models/{self.model}"
        url = f"{self.base}/{model_path}:predictLongRunning"
        payload = {
            "instances": [{
                "prompt": prompt,
                "image": {"bytesBase64Encoded": base64.b64encode(image.read_bytes()).decode("ascii"), "mimeType": mime_type(image)},
            }],
            "parameters": {
                "aspectRatio": self.aspect_ratio,
                "durationSeconds": self.duration_seconds,
                "sampleCount": 1,
                "resolution": "720p",
            },
        }
        response = self.session.post(url, json=payload, timeout=self.timeout)
        if response.status_code >= 400:
            raise ApiIntegrationError(f"Vertex HTTP {response.status_code}: {response.text[:4000]}")
        operation = response.json()
        operation_name = operation.get("name")
        if not operation_name:
            raise ApiIntegrationError(f"Vertex operation name not found: {json.dumps(operation, ensure_ascii=False)[:3000]}")
        started = time.monotonic()
        while time.monotonic() - started <= timeout_seconds:
            time.sleep(poll_seconds)
            poll_url = f"{self.base}/{operation_name}" if not operation_name.startswith("projects/") else f"{self.base}/{operation_name}"
            poll = self.session.get(poll_url, timeout=self.timeout)
            if poll.status_code >= 400:
                raise ApiIntegrationError(f"Vertex operation polling HTTP {poll.status_code}: {poll.text[:3000]}")
            body = poll.json()
            if not body.get("done"):
                continue
            error = body.get("error")
            if error:
                raise ApiIntegrationError(f"Veo operation failed: {json.dumps(error, ensure_ascii=False)}")
            return self._save_result(body, output)
        raise ApiIntegrationError(f"Veo operation polling timeout: {operation_name}")

    def _save_result(self, body: dict[str, Any], output: Path) -> dict[str, Any]:
        response = body.get("response", body)
        candidates: list[dict[str, Any]] = []
        for key in ("generatedVideos", "generated_videos", "videos"):
            value = response.get(key, []) if isinstance(response, dict) else []
            if isinstance(value, list):
                candidates.extend(item for item in value if isinstance(item, dict))
        for item in candidates:
            video = item.get("video", item)
            if video.get("bytesBase64Encoded"):
                decode_inline_media(video["bytesBase64Encoded"], output)
                return {"provider": "vertex_ai", "model": self.model, "delivery": "inline", "output": str(output)}
            uri = video.get("gcsUri") or video.get("uri")
            if uri and str(uri).startswith("gs://"):
                try:
                    from google.cloud import storage  # type: ignore
                except ImportError as exc:
                    raise ApiIntegrationError("GCS video output requires google-cloud-storage.") from exc
                bucket_name, blob_name = str(uri)[5:].split("/", 1)
                storage.Client(project=self.project).bucket(bucket_name).blob(blob_name).download_to_filename(str(output))
                return {"provider": "vertex_ai", "model": self.model, "delivery": "gcs_uri", "uri": uri, "output": str(output)}
        raise ApiIntegrationError(f"Veo finished but no recognized video field was found: {json.dumps(body, ensure_ascii=False)[:5000]}")


def safe_summary(cfg: Config, visual_prompt: str | None, video_prompt: str) -> dict[str, Any]:
    return {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "execute": cfg.execute,
        "dry_run": cfg.dry_run,
        "image_model": cfg.image_model,
        "video_provider": cfg.video_provider,
        "video_model": cfg.video_model,
        "aspect_ratio": cfg.aspect_ratio,
        "duration_seconds": cfg.duration_seconds,
        "reference_images": [str(path) for path in cfg.reference_images],
        "visual_prompt_chars": len(visual_prompt or ""),
        "video_prompt_chars": len(video_prompt),
        "external_calls": "disabled" if not cfg.execute or cfg.dry_run else "enabled",
    }


def main() -> int:
    cfg = parse_args()
    require_files(cfg.reference_images)
    visual_prompt = None if cfg.skip_image else read_prompt(cfg.visual_prompt, cfg.visual_prompt_file, "Visual prompt")
    video_prompt = read_prompt(cfg.video_prompt, cfg.video_prompt_file, "Video prompt")
    cfg.output_dir.mkdir(parents=True, exist_ok=True)
    run_record: dict[str, Any] = {"config": safe_summary(cfg, visual_prompt, video_prompt), "status": "DRY_RUN" if cfg.dry_run or not cfg.execute else "PLANNED"}
    if cfg.dry_run or not cfg.execute:
        run_record["plan"] = {
            "image": None if cfg.skip_image else {"adapter": "Gemini Interactions / Nano Banana Pro", "output": str(cfg.output_dir / "banana_pro_image.png")},
            "video": {"adapter": "Gemini Interactions / Omni Flash" if cfg.video_provider == "omni" else "Vertex AI / Veo Fast", "output": str(cfg.output_dir / "video.mp4")},
            "next_step": "Add --execute for a real call and provide the required key/ADC credentials.",
        }
        (cfg.output_dir / "run.json").write_text(json.dumps(run_record, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(run_record, ensure_ascii=False, indent=2))
        return 0

    if not cfg.execute:
        raise ApiIntegrationError("For safety, a real network call requires --execute.")
    api_key = load_gemini_key() if (not cfg.skip_image or cfg.video_provider == "omni") else None
    gemini_client = GeminiInteractionsClient(api_key, timeout=120.0, store=cfg.store) if api_key else None
    image_output = cfg.output_dir / "banana_pro_image.png"
    if cfg.skip_image:
        if not cfg.reference_images:
            raise ApiIntegrationError("--skip-image requires at least one --reference-image as the existing starting frame.")
        starting_frame = cfg.reference_images[0]
        run_record["image"] = {"skipped": True, "starting_frame": str(starting_frame)}
    else:
        assert gemini_client is not None
        image_result = BananaProAdapter(gemini_client, cfg.image_model, aspect_ratio=cfg.aspect_ratio, image_size=cfg.image_size).generate(
            visual_prompt or "", cfg.reference_images, image_output, poll_seconds=cfg.poll_seconds, timeout_seconds=cfg.timeout_seconds
        )
        starting_frame = image_output
        run_record["image"] = image_result

    video_output = cfg.output_dir / "video.mp4"
    if cfg.video_provider == "omni":
        assert gemini_client is not None
        video_model = cfg.video_model or os.getenv("GEMINI_VIDEO_MODEL", "gemini-omni-flash-preview")
        video_result = GeminiOmniAdapter(gemini_client, video_model, aspect_ratio=cfg.aspect_ratio, duration_seconds=cfg.duration_seconds).generate(
            video_prompt, starting_frame, video_output, poll_seconds=cfg.poll_seconds, timeout_seconds=cfg.timeout_seconds
        )
    else:
        video_model = cfg.video_model or os.getenv("VEO_VIDEO_MODEL", "veo-3.1-fast-generate-001")
        video_result = VertexVeoAdapter(cfg.project, cfg.location, video_model, timeout=120.0, duration_seconds=cfg.duration_seconds, aspect_ratio=cfg.aspect_ratio).generate(
            video_prompt, starting_frame, video_output, poll_seconds=cfg.poll_seconds, timeout_seconds=cfg.timeout_seconds
        )
    run_record["video"] = video_result
    run_record["status"] = "PASS"
    (cfg.output_dir / "run.json").write_text(json.dumps(run_record, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(run_record, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ApiIntegrationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
