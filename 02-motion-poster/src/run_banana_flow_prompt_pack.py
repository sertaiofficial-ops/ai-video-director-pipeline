#!/usr/bin/env python3
"""One-click Banana Pro + Google Flow Lab prompt-pack automation.

The script automates deterministic preparation only:
- validates 20 visual and 20 video prompt entries;
- checks the M/F/O/E 5+5+5+5 category distribution;
- verifies visual/video ID matching and common 9:16/8-second rules;
- exports one copy-ready .txt file per prompt;
- copies the matrix, guidelines, research and optional generated assets;
- optionally reads a project config (brand, rights, asset policy) and runs
  per-ID asset QC with ffprobe (PASS / PARTIAL / FAIL / SKIPPED);
- writes validation/config/manifest files and creates a verified ZIP.

It intentionally does not log in to, scrape, or call Banana Pro or Google Flow
Lab. Creative model calls remain explicit user actions so credentials, quotas,
and paid generation are never guessed or triggered by the script.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
# Prompt files live in <repo>/prompts by default; override with SERTAI_PROMPTS_DIR or --source-dir.
DEFAULT_SOURCE_DIR = Path(os.environ.get("SERTAI_PROMPTS_DIR", str(REPO_ROOT / "prompts"))).expanduser()
DEFAULT_OUTPUT_DIR = Path(os.environ.get("SERTAI_OUTPUT_DIR", str(REPO_ROOT / "output" / "banana_flow_automation"))).expanduser()
DOCS_DIR = REPO_ROOT / "docs"
VISUAL_NAME = "20_banana_pro_visual_prompts.md"
VIDEO_NAME = "20_flow_omni_veo_fast_video_prompts.md"
MATRIX_NAME = "prompt_set_matrix.md"
GUIDELINES_NAME = "flow_banana_prompt_guidelines.md"
RESEARCH_NAME = "character_consistency_research.md"
GUIDE_NAME = "banana_flow_automation_guide.md"
HEADER_RE = re.compile(r"^##\s+([MFOE]\d{2})\s+—\s+(.+?)\s*$", re.MULTILINE)
TEXT_BLOCK_RE = re.compile(r"```text\s*(.*?)```", re.IGNORECASE | re.DOTALL)
EXPECTED_CATEGORIES = {"M": 5, "F": 5, "O": 5, "E": 5}


class AutomationError(RuntimeError):
    """Raised when input validation or packaging fails."""


@dataclass
class Config:
    source_dir: Path
    output_dir: Path
    assets_dir: Path | None
    project_config: Path | None
    visual_prompts: Path
    video_prompts: Path
    matrix: Path
    guidelines: Path
    research: Path | None
    guide: Path | None
    project_name: str
    duration: float
    aspect_ratio: str
    dry_run: bool
    package: bool


def parse_args() -> Config:
    parser = argparse.ArgumentParser(
        description="Banana Pro + Google Flow Lab 20+20 prompt packaging automation"
    )
    parser.add_argument("--source-dir", type=Path, default=DEFAULT_SOURCE_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--assets-dir", type=Path, help="Optional folder of Banana Pro/Flow outputs")
    parser.add_argument("--project-config", type=Path, help="Optional project_config.json with brand, rights and asset policy")
    parser.add_argument("--visual-prompts", type=Path)
    parser.add_argument("--video-prompts", type=Path)
    parser.add_argument("--matrix", type=Path)
    parser.add_argument("--guidelines", type=Path)
    parser.add_argument("--research", type=Path)
    parser.add_argument("--guide", type=Path)
    parser.add_argument("--project-name", default="BananaPro_Flow_20_Prompt_Pack")
    parser.add_argument("--duration", type=float, default=8.0)
    parser.add_argument("--aspect-ratio", default="9:16")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-package", action="store_true")
    args = parser.parse_args()

    source_dir = args.source_dir.resolve()
    research = args.research or source_dir / RESEARCH_NAME
    if not research.exists():
        research = DOCS_DIR / RESEARCH_NAME
    if not research.exists():
        research = REPO_ROOT.parent / "01-graphic-dna" / "docs" / RESEARCH_NAME
    guide = args.guide or source_dir / GUIDE_NAME
    if not guide.exists():
        guide = DOCS_DIR / "prompt_pack_automation_guide.md"
    return Config(
        source_dir=source_dir,
        output_dir=args.output_dir.resolve(),
        assets_dir=args.assets_dir.resolve() if args.assets_dir else None,
        project_config=args.project_config.resolve() if args.project_config else None,
        visual_prompts=(args.visual_prompts or source_dir / VISUAL_NAME).resolve(),
        video_prompts=(args.video_prompts or source_dir / VIDEO_NAME).resolve(),
        matrix=(args.matrix or source_dir / MATRIX_NAME).resolve(),
        guidelines=(args.guidelines or source_dir / GUIDELINES_NAME).resolve(),
        research=research.resolve() if research.exists() else None,
        guide=guide.resolve() if guide.exists() else None,
        project_name=args.project_name,
        duration=args.duration,
        aspect_ratio=args.aspect_ratio,
        dry_run=args.dry_run,
        package=not args.no_package,
    )


def load_project_config(path: Path | None) -> dict[str, object]:
    if path is None:
        return {}
    require_file(path, "Project config")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise AutomationError(f"Project config is not valid JSON: {path}") from exc
    if not isinstance(data, dict):
        raise AutomationError("Project config root must be an object.")
    return data


def require_file(path: Path, label: str) -> None:
    if not path.exists():
        raise AutomationError(f"{label} not found: {path}")
    if not path.is_file():
        raise AutomationError(f"{label} is not a file: {path}")


def parse_prompt_file(path: Path) -> dict[str, dict[str, str]]:
    text = path.read_text(encoding="utf-8")
    headers = list(HEADER_RE.finditer(text))
    if not headers:
        raise AutomationError(f"No prompt headings found: {path}")
    entries: dict[str, dict[str, str]] = {}
    for index, header in enumerate(headers):
        item_id, title = header.group(1), header.group(2)
        section_end = headers[index + 1].start() if index + 1 < len(headers) else len(text)
        section = text[header.end():section_end]
        block = TEXT_BLOCK_RE.search(section)
        if not block:
            raise AutomationError(f"{path.name}: no text prompt block found for {item_id}.")
        if item_id in entries:
            raise AutomationError(f"{path.name}: duplicate ID {item_id}.")
        entries[item_id] = {"id": item_id, "title": title, "prompt": block.group(1).strip()}
    return entries


def validate_common(entries: dict[str, dict[str, str]], label: str, duration: float, aspect_ratio: str) -> list[str]:
    errors: list[str] = []
    if len(entries) != 20:
        errors.append(f"{label}: expected 20 prompts, found {len(entries)}.")
    category_counts = {category: 0 for category in EXPECTED_CATEGORIES}
    for item_id in entries:
        category_counts[item_id[0]] = category_counts.get(item_id[0], 0) + 1
    for category, expected in EXPECTED_CATEGORIES.items():
        actual = category_counts.get(category, 0)
        if actual != expected:
            errors.append(f"{label}: category {category} should have {expected}, found {actual}.")

    for item_id, entry in entries.items():
        lower = entry["prompt"].lower()
        if aspect_ratio not in entry["prompt"] and "vertical 9:16" not in lower:
            errors.append(f"{label} {item_id}: missing 9:16 phrase.")
        if "no readable text" not in lower:
            errors.append(f"{label} {item_id}: missing 'no readable text' exclusion.")
        if "no watermark" not in lower:
            errors.append(f"{label} {item_id}: missing 'no watermark' exclusion.")
    return errors


def validate_visuals(entries: dict[str, dict[str, str]]) -> list[str]:
    errors: list[str] = []
    for item_id, entry in entries.items():
        lower = entry["prompt"].lower()
        if "poster" not in lower:
            errors.append(f"Visual {item_id}: poster purpose not stated.")
        if not any(token in lower for token in ("identity anchor", "object identity anchor", "location identity anchor")):
            errors.append(f"Visual {item_id}: identity anchor not stated.")
    return errors


def validate_videos(entries: dict[str, dict[str, str]], visual_ids: set[str], duration: float) -> list[str]:
    errors: list[str] = []
    if set(entries) != visual_ids:
        errors.append(f"Visual/video ID sets do not match: visual={sorted(visual_ids)}, video={sorted(entries)}")
    for item_id, entry in entries.items():
        lower = entry["prompt"].lower()
        required_phrases = (
            ("one continuous", "one continuous shot"),
            ("preserve the reference", "reference preservation"),
            ("no dialogue", "no dialogue"),
            ("no singing", "no singing"),
        )
        for needle, description in required_phrases:
            if needle not in lower:
                errors.append(f"Video {item_id}: missing {description} phrase.")
        if f"{duration:g}-second" not in lower and f"{duration:.1f}-second" not in lower:
            errors.append(f"Video {item_id}: missing target {duration:g}-second phrase.")
        if "0–2s" not in entry["prompt"] or "6–8s" not in entry["prompt"]:
            errors.append(f"Video {item_id}: missing 0–2s / 6–8s timeline.")
    return errors


def continuity_warnings(entries: dict[str, dict[str, str]]) -> list[str]:
    warnings: list[str] = []
    for item_id, entry in entries.items():
        lower = entry["prompt"].lower()
        if "preserve" not in lower or "same" not in lower:
            warnings.append(f"Video {item_id}: add explicit same-reference continuity language.")
        if "no new" not in lower and "no scene change" not in lower and "no location change" not in lower:
            warnings.append(f"Video {item_id}: add an explicit single-location exclusion.")
        if "audio:" not in lower and "ambient sound" not in lower:
            warnings.append(f"Video {item_id}: add an explicit audio strategy.")
    return warnings


def write_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def export_prompt_files(entries: dict[str, dict[str, str]], output_dir: Path, kind: str) -> list[Path]:
    target = output_dir / "prompts" / kind
    target.mkdir(parents=True, exist_ok=True)
    outputs: list[Path] = []
    for item_id in sorted(entries):
        path = target / f"{item_id}.txt"
        path.write_text(entries[item_id]["prompt"] + "\n", encoding="utf-8")
        outputs.append(path)
    return outputs


def copy_reference(path: Path | None, output_dir: Path) -> Path | None:
    if path is None:
        return None
    target = output_dir / "references" / path.name
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, target)
    return target


def copy_assets(assets_dir: Path | None, output_dir: Path) -> list[Path]:
    if assets_dir is None:
        return []
    if not assets_dir.exists() or not assets_dir.is_dir():
        raise AutomationError(f"Assets folder not found or not a directory: {assets_dir}")
    copied: list[Path] = []
    for source in sorted(path for path in assets_dir.rglob("*") if path.is_file()):
        target = output_dir / "assets" / source.relative_to(assets_dir)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        copied.append(target)
    return copied


def probe_asset(path: Path) -> dict[str, object]:
    if shutil.which("ffprobe") is None:
        return {"path": str(path), "status": "UNVERIFIED", "reason": "ffprobe not found"}
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_type,width,height,codec_name",
           "-of", "json", str(path)]
    try:
        result = subprocess.run(cmd, check=True, text=True, capture_output=True)
        data = json.loads(result.stdout or "{}")
        stream = next((item for item in data.get("streams", []) if item.get("codec_type") == "video"), None)
        if stream is None:
            return {"path": str(path), "status": "FAIL", "reason": "no image/video stream found"}
        width, height = int(stream.get("width", 0) or 0), int(stream.get("height", 0) or 0)
        ratio_ok = width > 0 and height > 0 and abs((width / height) - (9 / 16)) < 0.02
        return {"path": str(path), "status": "PASS", "width": width, "height": height,
                "codec": stream.get("codec_name"), "duration": data.get("format", {}).get("duration"),
                "ratio_9x16": ratio_ok}
    except (OSError, subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        return {"path": str(path), "status": "FAIL", "reason": str(exc)}


IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}
VIDEO_SUFFIXES = {".mp4", ".mov", ".webm"}
DURATION_TOLERANCE = 0.5


def find_asset(assets: list[Path], item_id: str, suffixes: set[str], pattern: object) -> Path | None:
    """Prefer the exact config pattern name, then any file named <ID>, <ID>_* or <ID>-*."""
    if isinstance(pattern, str) and "{id}" in pattern:
        expected = pattern.replace("{id}", item_id)
        exact = next((p for p in assets if p.name == expected), None)
        if exact is not None:
            return exact
    return next((p for p in assets
                 if p.suffix.lower() in suffixes
                 and (p.stem == item_id or p.stem.startswith(item_id + "_") or p.stem.startswith(item_id + "-"))), None)


def validate_assets(assets_dir: Path | None, visual_ids: set[str], project_config: dict[str, object],
                    target_duration: float | None = None) -> dict[str, object]:
    result: dict[str, object] = {"status": "SKIPPED", "directory": str(assets_dir) if assets_dir else None, "items": {}}
    if assets_dir is None:
        return result
    if not assets_dir.exists() or not assets_dir.is_dir():
        raise AutomationError(f"Assets folder not found or not a directory: {assets_dir}")
    assets = sorted(path for path in assets_dir.rglob("*") if path.is_file())
    asset_policy = project_config.get("assets") if isinstance(project_config.get("assets"), dict) else {}
    require_complete = bool(asset_policy.get("require_complete_set", False))
    items: dict[str, object] = {}
    failures: list[str] = []
    missing: list[str] = []
    for item_id in sorted(visual_ids):
        image = find_asset(assets, item_id, IMAGE_SUFFIXES, asset_policy.get("poster_pattern"))
        video = find_asset(assets, item_id, VIDEO_SUFFIXES, asset_policy.get("video_pattern"))
        entry = {"poster": probe_asset(image) if image else {"status": "MISSING"},
                 "video": probe_asset(video) if video else {"status": "MISSING"}}
        video_duration = entry["video"].get("duration")
        if video_duration is not None and target_duration:
            try:
                if abs(float(video_duration) - target_duration) > DURATION_TOLERANCE:
                    entry["video"]["duration_warning"] = f"duration {float(video_duration):g}s differs from target {target_duration:g}s"
            except (TypeError, ValueError):
                pass
        items[item_id] = entry
        if require_complete and (image is None or video is None):
            failures.append(f"{item_id}: missing poster or video")
        elif image is None or video is None:
            missing.append(f"{item_id}: missing poster or video")
        for role in ("poster", "video"):
            if entry[role].get("status") == "FAIL":
                failures.append(f"{item_id}: unreadable {role}")
            if entry[role].get("ratio_9x16") is False:
                failures.append(f"{item_id}: {role} is not 9:16")
    result["items"] = items
    result["status"] = "FAIL" if failures else ("PARTIAL" if missing else "PASS")
    result["errors"] = failures
    result["missing"] = missing
    return result


def config_payload(cfg: Config, project_config: dict[str, object], asset_qc: dict[str, object]) -> dict[str, object]:
    return {
        "source_dir": str(cfg.source_dir),
        "output_dir": str(cfg.output_dir),
        "assets_dir": str(cfg.assets_dir) if cfg.assets_dir else None,
        "visual_prompts": str(cfg.visual_prompts),
        "video_prompts": str(cfg.video_prompts),
        "matrix": str(cfg.matrix),
        "guidelines": str(cfg.guidelines),
        "research": str(cfg.research) if cfg.research else None,
        "guide": str(cfg.guide) if cfg.guide else None,
        "project_name": cfg.project_name,
        "duration": cfg.duration,
        "aspect_ratio": cfg.aspect_ratio,
        "dry_run": cfg.dry_run,
        "package": cfg.package,
        "project_config": project_config,
        "asset_qc": asset_qc,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
    }


def write_manifest(output_dir: Path, cfg: Config, validation: dict[str, object], files: list[Path]) -> Path:
    manifest = output_dir / "DELIVERY_MANIFEST.md"
    relative = sorted(str(path.relative_to(output_dir)) for path in files if path.exists())
    lines = [
        f"# {cfg.project_name}",
        "",
        "Validated delivery package of Banana Pro image prompts and Google Flow Lab Omni/Veo Fast video prompts.",
        "",
        f"- Created at: {datetime.now(timezone.utc).isoformat()}",
        f"- Target duration: {cfg.duration:g} seconds",
        f"- Target aspect ratio: {cfg.aspect_ratio}",
        f"- Validation: {validation['status']}",
        f"- Asset QC: {validation.get('asset_qc_status', 'SKIPPED')}",
        "",
        "## Files",
        "",
    ]
    lines.extend(f"- `{name}`" for name in relative)
    manifest.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return manifest


def package_output(output_dir: Path, archive: Path) -> None:
    if archive.exists():
        archive.unlink()
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(output_dir.rglob("*")):
            if path.is_file() and path != archive:
                zf.write(path, arcname=path.relative_to(output_dir))
    with zipfile.ZipFile(archive) as zf:
        bad = zf.testzip()
        if bad:
            raise AutomationError(f"ZIP contains a corrupt file: {bad}")


def main() -> int:
    cfg = parse_args()
    project_config = load_project_config(cfg.project_config)
    if isinstance(project_config.get("brand"), dict):
        brand = project_config["brand"]
        if brand.get("text") and len(str(brand["text"])) > 80:
            raise AutomationError("brand.text must be 80 characters or fewer.")
        opacity = brand.get("opacity")
        if opacity is not None and (isinstance(opacity, bool) or not isinstance(opacity, (int, float)) or not 0 <= opacity <= 1):
            raise AutomationError("brand.opacity must be a number between 0 and 1.")
    rights = project_config.get("rights")
    if isinstance(rights, dict) and rights.get("status") not in {None, "unknown", "cleared", "user-approved", "restricted"}:
        raise AutomationError("rights.status must be unknown, cleared, user-approved or restricted.")
    config_warnings: list[str] = []
    if cfg.research is None:
        config_warnings.append(f"Character research file ({RESEARCH_NAME}) not found in the source dir, docs/ or 01-graphic-dna/docs/; package will not include it.")
    if isinstance(rights, dict) and rights.get("status") in {None, "unknown"}:
        config_warnings.append("rights.status is unknown: draft use only; set cleared or user-approved before publishing.")
    if isinstance(rights, dict) and rights.get("status") == "restricted":
        config_warnings.append("rights.status is restricted: do not publish without a new permission check.")
    for message in config_warnings:
        print(f"WARNING: {message}", file=sys.stderr)
    for path, label in (
        (cfg.visual_prompts, "Visual prompt file"),
        (cfg.video_prompts, "Video prompt file"),
        (cfg.matrix, "Prompt matrix"),
        (cfg.guidelines, "Flow/Banana guidelines"),
    ):
        require_file(path, label)
    for path, label in ((cfg.research, "Character research"), (cfg.guide, "Automation guide")):
        if path is not None:
            require_file(path, label)
    if cfg.duration <= 0:
        raise AutomationError("--duration must be positive.")
    if cfg.aspect_ratio != "9:16":
        raise AutomationError("For this prompt set, --aspect-ratio must be 9:16.")

    visuals = parse_prompt_file(cfg.visual_prompts)
    videos = parse_prompt_file(cfg.video_prompts)
    errors = validate_common(visuals, "Visual", cfg.duration, cfg.aspect_ratio)
    errors.extend(validate_common(videos, "Video", cfg.duration, cfg.aspect_ratio))
    errors.extend(validate_visuals(visuals))
    errors.extend(validate_videos(videos, set(visuals), cfg.duration))
    warnings = config_warnings + continuity_warnings(videos)
    asset_qc = validate_assets(cfg.assets_dir, set(visuals), project_config, cfg.duration)
    if asset_qc["status"] == "FAIL":
        errors.extend(asset_qc.get("errors", []))
    for item_id, entry in (asset_qc.get("items") or {}).items():
        note = entry["video"].get("duration_warning")
        if note:
            warnings.append(f"Asset {item_id}: video {note}.")
    if asset_qc["status"] == "PARTIAL":
        warnings.append(f"Asset QC PARTIAL: {len(asset_qc.get('missing', []))} ID(s) missing a poster or video.")
    validation = {
        "status": "PASS" if not errors else "FAIL",
        "visual_count": len(visuals),
        "video_count": len(videos),
        "category_counts": {category: sum(item_id.startswith(category) for item_id in visuals) for category in EXPECTED_CATEGORIES},
        "matched_ids": set(visuals) == set(videos),
        "asset_qc_status": asset_qc["status"],
        "errors": errors,
        "warnings": warnings,
    }
    cfg.output_dir.mkdir(parents=True, exist_ok=True)
    write_json(cfg.output_dir / "validation.json", validation)
    if errors:
        raise AutomationError("Prompt validation failed: " + " | ".join(errors))

    if cfg.dry_run:
        write_json(cfg.output_dir / "run_config.json", {**config_payload(cfg, project_config, asset_qc), "planned_outputs": ["validation.json", "run_config.json", "asset_manifest.json", "DELIVERY_MANIFEST.md", "prompt_pack.zip"]})
        print(json.dumps(validation, ensure_ascii=False, indent=2))
        print(f"DRY RUN PASS — {cfg.output_dir}")
        return 0

    output_files: list[Path] = []
    output_files.extend(export_prompt_files(visuals, cfg.output_dir, "visual"))
    output_files.extend(export_prompt_files(videos, cfg.output_dir, "video"))
    for reference in (cfg.matrix, cfg.guidelines, cfg.research, cfg.guide):
        copied = copy_reference(reference, cfg.output_dir)
        if copied:
            output_files.append(copied)
    output_files.extend(copy_assets(cfg.assets_dir, cfg.output_dir))
    config_path = cfg.output_dir / "run_config.json"
    write_json(config_path, config_payload(cfg, project_config, asset_qc))
    asset_manifest = cfg.output_dir / "asset_manifest.json"
    write_json(asset_manifest, asset_qc)
    output_files.extend([cfg.output_dir / "validation.json", config_path, asset_manifest])
    manifest = write_manifest(cfg.output_dir, cfg, validation, output_files)
    output_files.append(manifest)

    if cfg.package:
        archive = cfg.output_dir / "prompt_pack.zip"
        package_output(cfg.output_dir, archive)
        print(f"ZIP PASS — {archive}")
    print(f"PASS — {len(visuals)} visual + {len(videos)} video prompts prepared: {cfg.output_dir}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AutomationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
