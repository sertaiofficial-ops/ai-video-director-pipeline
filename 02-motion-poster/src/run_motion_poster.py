#!/usr/bin/env python3
"""One-click SERTAI motion-poster automation.

This script intentionally automates deterministic work only:
media probing, audio extraction, audio-analysis invocation,
V1/V2 motion-poster rendering, final muxing, QC, and packaging.
External image/video model calls remain explicit inputs so that
credentials and platform-specific APIs are never guessed or hard-coded.
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import shutil
import subprocess
import sys
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable


SCRIPT_DIR = Path(__file__).resolve().parent
# Optional external audio analyzer. Set SERTAI_AUDIO_ANALYZER to the path of an
# analyze_audio.py script; if it is not set or missing, an ffprobe report is used instead.
DEFAULT_ANALYZER = Path(os.environ.get("SERTAI_AUDIO_ANALYZER", str(SCRIPT_DIR / "analyze_audio.py"))).expanduser()


@dataclass
class Config:
    source_video: Path | None
    source_audio: Path | None
    first_keyframe: Path | None
    final_keyframe: Path | None
    raw_video: Path | None
    output_dir: Path
    mode: str
    duration: float
    fps: int
    width: int
    height: int
    crf: int
    audio_bitrate: str
    label: str
    label_opacity: float
    final_hold: float
    transition: float
    seed: int | None
    dry_run: bool
    package: bool


class AutomationError(RuntimeError):
    pass


def log_command(cmd: Iterable[str]) -> str:
    return subprocess.list2cmdline([str(x) for x in cmd])


def run_command(cmd: list[str], *, dry_run: bool, log_file: Path, capture: bool = False) -> subprocess.CompletedProcess[str]:
    rendered = log_command(cmd)
    logging.info("%s", rendered)
    with log_file.open("a", encoding="utf-8") as handle:
        handle.write(rendered + "\n")
    if dry_run:
        return subprocess.CompletedProcess(cmd, 0, "", "")
    try:
        return subprocess.run(cmd, check=True, text=True, capture_output=capture)
    except FileNotFoundError as exc:
        raise AutomationError(f"Missing system command: {cmd[0]}") from exc
    except subprocess.CalledProcessError as exc:
        details = (exc.stderr or exc.stdout or "").strip()
        raise AutomationError(f"Command failed: {cmd[0]}\n{details}") from exc


def require_binary(name: str) -> None:
    if shutil.which(name) is None:
        raise AutomationError(f"'{name}' not found on PATH. Check your FFmpeg installation and PATH.")


def require_file(path: Path | None, label: str) -> None:
    if path is not None and not path.exists():
        raise AutomationError(f"{label} not found: {path}")


def probe(path: Path, log_file: Path, *, dry_run: bool) -> dict[str, Any]:
    output = log_file.parent / f"{path.stem}_technical.json"
    cmd = [
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration,format_name,size:stream=index,codec_name,codec_type,sample_rate,channels,width,height,r_frame_rate,pix_fmt",
        "-of", "json", str(path),
    ]
    result = run_command(cmd, dry_run=dry_run, log_file=log_file, capture=True)
    if dry_run:
        data: dict[str, Any] = {"dry_run": True, "path": str(path)}
    else:
        try:
            data = json.loads(result.stdout or "{}")
        except json.JSONDecodeError as exc:
            raise AutomationError(f"Could not parse ffprobe JSON output: {path}") from exc
    output.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return data


def media_duration(path: Path, log_file: Path, *, dry_run: bool, fallback: float) -> float:
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(path)]
    result = run_command(cmd, dry_run=dry_run, log_file=log_file, capture=True)
    if dry_run:
        return fallback
    try:
        return float((result.stdout or "").strip())
    except ValueError as exc:
        raise AutomationError(f"Could not read media duration: {path}") from exc


def extract_audio(source_video: Path, out_audio: Path, log_file: Path, *, dry_run: bool) -> None:
    cmd = [
        "ffmpeg", "-y", "-i", str(source_video), "-vn", "-ac", "2", "-ar", "48000", str(out_audio)
    ]
    run_command(cmd, dry_run=dry_run, log_file=log_file)
    if not dry_run and not out_audio.exists():
        raise AutomationError(f"Audio extraction failed: {out_audio}")


def analyze_audio(audio: Path, out_report: Path, log_file: Path, *, dry_run: bool) -> None:
    if not DEFAULT_ANALYZER.exists():
        out_report.write_text("Audio analyzer not found; using the ffprobe technical report.\n", encoding="utf-8")
        return
    cmd = [sys.executable, str(DEFAULT_ANALYZER), str(audio)]
    if dry_run:
        run_command(cmd, dry_run=True, log_file=log_file)
        out_report.write_text("DRY RUN: analyze_audio.py was not run.\n", encoding="utf-8")
        return
    result = run_command(cmd, dry_run=False, log_file=log_file, capture=True)
    out_report.write_text(result.stdout or "", encoding="utf-8")


def audio_trim_filter(duration: float, input_index: int) -> str:
    return f"[{input_index}:a]atrim=duration={duration:.3f},asetpts=N/SR/TB[a]"


def drawtext_label(label: str, opacity: float) -> str:
    safe = label.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")
    return (
        f"drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:"
        f"text='{safe}':fontcolor=white@{opacity:.2f}:fontsize=20:x=w-tw-22:y=h-th-26"
    )


def render_v1(cfg: Config, audio: Path, output: Path, log_file: Path) -> None:
    if cfg.first_keyframe is None:
        raise AutomationError("V1 requires --first-keyframe.")
    visual = (
        f"[0:v]scale=820:1458:force_original_aspect_ratio=increase,crop=820:1458,"
        f"zoompan=z='min(zoom+0.00075,1.06)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
        f"d=1:s={cfg.width}x{cfg.height}:fps={cfg.fps},"
        f"drawbox=x=0:y=0:w=iw:h=ih:color=cyan@0.035:t=fill:enable='between(t,2.20,2.50)',"
        f"drawbox=x=0:y=0:w=iw:h=ih:color=cyan@0.025:t=fill:enable='between(t,4.40,4.70)',"
        f"drawbox=x=0:y=0:w=iw:h=ih:color=red@0.10:t=fill:enable='between(t,6.65,7.05)',"
        f"{drawtext_label(cfg.label, cfg.label_opacity)}[v]"
    )
    filter_graph = f"{visual};{audio_trim_filter(cfg.duration, 1)}"
    cmd = [
        "ffmpeg", "-y", "-loop", "1", "-framerate", str(cfg.fps), "-i", str(cfg.first_keyframe),
        "-i", str(audio), "-filter_complex", filter_graph, "-map", "[v]", "-map", "[a]",
        "-t", f"{cfg.duration:.3f}", "-c:v", "libx264", "-preset", "medium", "-crf", str(cfg.crf),
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", cfg.audio_bitrate, "-movflags", "+faststart", str(output)
    ]
    run_command(cmd, dry_run=cfg.dry_run, log_file=log_file)


def render_v2(cfg: Config, audio: Path, output: Path, log_file: Path) -> None:
    if cfg.first_keyframe is None or cfg.final_keyframe is None:
        raise AutomationError("V2 requires both --first-keyframe and --final-keyframe.")
    if cfg.final_hold <= cfg.transition:
        raise AutomationError("--final-hold must be greater than --transition.")
    neutral_input = cfg.duration - cfg.final_hold + cfg.transition
    offset = neutral_input - cfg.transition
    visual = (
        f"[0:v]scale=820:1458:force_original_aspect_ratio=increase,crop=820:1458,"
        f"zoompan=z='min(zoom+0.0008,1.05)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
        f"d=1:s={cfg.width}x{cfg.height}:fps={cfg.fps},setpts=PTS-STARTPTS[v0];"
        f"[1:v]scale=820:1458:force_original_aspect_ratio=increase,crop=820:1458,"
        f"zoompan=z='min(zoom+0.0012,1.03)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
        f"d=1:s={cfg.width}x{cfg.height}:fps={cfg.fps},setpts=PTS-STARTPTS[v1];"
        f"[v0][v1]xfade=transition=fadeblack:duration={cfg.transition:.3f}:offset={offset:.3f},"
        f"drawbox=x=0:y=0:w=iw:h=ih:color=red@0.07:t=fill:enable='between(t,6.65,7.10)',"
        f"{drawtext_label(cfg.label, cfg.label_opacity)}[v]"
    )
    filter_graph = f"{visual};{audio_trim_filter(cfg.duration, 2)}"
    cmd = [
        "ffmpeg", "-y", "-loop", "1", "-framerate", str(cfg.fps), "-t", f"{neutral_input:.3f}",
        "-i", str(cfg.first_keyframe), "-loop", "1", "-framerate", str(cfg.fps), "-t", f"{cfg.final_hold:.3f}",
        "-i", str(cfg.final_keyframe), "-i", str(audio), "-filter_complex", filter_graph,
        "-map", "[v]", "-map", "[a]", "-t", f"{cfg.duration:.3f}", "-c:v", "libx264", "-preset", "medium",
        "-crf", str(cfg.crf), "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", cfg.audio_bitrate,
        "-movflags", "+faststart", str(output)
    ]
    run_command(cmd, dry_run=cfg.dry_run, log_file=log_file)


def mux_real_video(cfg: Config, audio: Path, output: Path, log_file: Path) -> None:
    if cfg.raw_video is None:
        raise AutomationError("Real mode requires --raw-video.")
    cmd = [
        "ffmpeg", "-y", "-i", str(cfg.raw_video), "-i", str(audio), "-map", "0:v:0", "-map", "1:a:0",
        "-t", f"{cfg.duration:.3f}", "-vf", drawtext_label(cfg.label, cfg.label_opacity),
        "-c:v", "libx264", "-preset", "medium", "-crf", str(cfg.crf), "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", cfg.audio_bitrate, "-movflags", "+faststart", str(output)
    ]
    run_command(cmd, dry_run=cfg.dry_run, log_file=log_file)


def qc(output: Path, cfg: Config, log_file: Path) -> dict[str, Any]:
    data = probe(output, log_file, dry_run=cfg.dry_run)
    expected = {"duration": cfg.duration, "width": cfg.width, "height": cfg.height, "fps": cfg.fps}
    checks: dict[str, Any] = {"expected": expected, "probe": data, "status": "DRY_RUN" if cfg.dry_run else "PASS"}
    if not cfg.dry_run:
        duration = media_duration(output, log_file, dry_run=False, fallback=cfg.duration)
        streams = data.get("streams", [])
        video = next((s for s in streams if s.get("codec_type") == "video"), {})
        audio = next((s for s in streams if s.get("codec_type") == "audio"), {})
        checks["duration_delta"] = abs(duration - cfg.duration)
        checks["duration_pass"] = checks["duration_delta"] <= 0.05
        checks["video_pass"] = video.get("width") == cfg.width and video.get("height") == cfg.height
        checks["audio_present"] = audio.get("codec_type") == "audio"
        checks["status"] = "PASS" if all(checks[k] for k in ("duration_pass", "video_pass", "audio_present")) else "FAIL"
        if checks["status"] == "FAIL":
            raise AutomationError(f"QC failed: {checks}")
    return checks


def package_outputs(cfg: Config, files: list[Path], manifest: Path, archive: Path) -> None:
    entries = [p for p in files if p.exists()]
    lines = ["# Motion-Poster Automation Manifest", "", f"Mode: {cfg.mode}", f"Duration: {cfg.duration:.3f}", "", "## Files"]
    lines.extend(f"- {p.name}" for p in entries)
    manifest.write_text("\n".join(lines) + "\n", encoding="utf-8")
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in entries + [manifest]:
            zf.write(path, arcname=path.name)
    with zipfile.ZipFile(archive) as zf:
        broken = zf.testzip()
        if broken:
            raise AutomationError(f"ZIP contains a corrupt file: {broken}")


def parse_args() -> Config:
    parser = argparse.ArgumentParser(description="SERTAI one-click motion poster automation")
    parser.add_argument("--source-video", type=Path)
    parser.add_argument("--source-audio", type=Path)
    parser.add_argument("--first-keyframe", type=Path)
    parser.add_argument("--final-keyframe", type=Path)
    parser.add_argument("--raw-video", type=Path, help="Previously generated real image-to-video MP4")
    parser.add_argument("--output-dir", type=Path, default=Path("./motion_poster_output"))
    parser.add_argument("--mode", choices=("auto", "fallback", "real"), default="auto")
    parser.add_argument("--duration", type=float, default=8.0)
    parser.add_argument("--fps", type=int, default=24)
    parser.add_argument("--width", type=int, default=720)
    parser.add_argument("--height", type=int, default=1280)
    parser.add_argument("--crf", type=int, default=18)
    parser.add_argument("--audio-bitrate", default="192k")
    parser.add_argument("--label", default="SERTAI LAB")
    parser.add_argument("--label-opacity", type=float, default=0.48)
    parser.add_argument("--final-hold", type=float, default=1.6)
    parser.add_argument("--transition", type=float, default=0.3)
    parser.add_argument("--seed", type=int)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-package", action="store_true")
    args = parser.parse_args()
    return Config(
        source_video=args.source_video, source_audio=args.source_audio, first_keyframe=args.first_keyframe,
        final_keyframe=args.final_keyframe, raw_video=args.raw_video, output_dir=args.output_dir,
        mode=args.mode, duration=args.duration, fps=args.fps, width=args.width, height=args.height,
        crf=args.crf, audio_bitrate=args.audio_bitrate, label=args.label, label_opacity=args.label_opacity,
        final_hold=args.final_hold, transition=args.transition, seed=args.seed, dry_run=args.dry_run,
        package=not args.no_package,
    )


def main() -> int:
    cfg = parse_args()
    cfg.output_dir.mkdir(parents=True, exist_ok=True)
    log_file = cfg.output_dir / "automation_commands.log"
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    logging.info("SERTAI motion poster automation starting: %s", cfg.output_dir)

    require_binary("ffmpeg")
    require_binary("ffprobe")
    require_file(cfg.source_video, "Source video")
    require_file(cfg.source_audio, "Source audio")
    require_file(cfg.first_keyframe, "First keyframe")
    require_file(cfg.final_keyframe, "Final keyframe")
    require_file(cfg.raw_video, "Raw generated video")
    if cfg.source_video is None and cfg.source_audio is None:
        raise AutomationError("Either --source-video or --source-audio must be given.")

    metadata_files: list[Path] = []
    if cfg.source_video:
        probe(cfg.source_video, log_file, dry_run=cfg.dry_run)
        metadata_files.append(cfg.output_dir / f"{cfg.source_video.stem}_technical.json")
    if cfg.source_audio:
        probe(cfg.source_audio, log_file, dry_run=cfg.dry_run)
        metadata_files.append(cfg.output_dir / f"{cfg.source_audio.stem}_technical.json")

    audio = cfg.source_audio
    if audio is None and cfg.source_video is not None:
        audio = cfg.output_dir / f"{cfg.source_video.stem}_extracted.wav"
        extract_audio(cfg.source_video, audio, log_file, dry_run=cfg.dry_run)
    assert audio is not None
    audio_report = cfg.output_dir / "source_audio_analysis.txt"
    analyze_audio(audio, audio_report, log_file, dry_run=cfg.dry_run)

    mode = cfg.mode
    if mode == "auto":
        mode = "real" if cfg.raw_video is not None else "fallback"
    if mode == "real" and cfg.raw_video is None:
        raise AutomationError("--mode real was selected but --raw-video was not given.")
    if mode == "fallback" and cfg.first_keyframe is None:
        raise AutomationError("Fallback requires --first-keyframe.")

    output = cfg.output_dir / "motion_poster_final.mp4"
    if mode == "real":
        mux_real_video(cfg, audio, output, log_file)
    elif cfg.final_keyframe is not None:
        render_v2(cfg, audio, output, log_file)
    else:
        render_v1(cfg, audio, output, log_file)

    qc_report = cfg.output_dir / "qc_report.json"
    checks = qc(output, cfg, log_file)
    qc_report.write_text(json.dumps(checks, ensure_ascii=False, indent=2), encoding="utf-8")

    config_path = cfg.output_dir / "run_config.json"
    config_path.write_text(json.dumps({**asdict(cfg), "source_video": str(cfg.source_video) if cfg.source_video else None,
                                       "source_audio": str(cfg.source_audio) if cfg.source_audio else None,
                                       "first_keyframe": str(cfg.first_keyframe) if cfg.first_keyframe else None,
                                       "final_keyframe": str(cfg.final_keyframe) if cfg.final_keyframe else None,
                                       "raw_video": str(cfg.raw_video) if cfg.raw_video else None,
                                       "output_dir": str(cfg.output_dir), "resolved_mode": mode}, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

    files = [output, audio_report, qc_report, config_path, log_file] + metadata_files
    for candidate in (cfg.first_keyframe, cfg.final_keyframe, cfg.source_audio, cfg.source_video, cfg.raw_video):
        if candidate is not None and candidate.exists():
            files.append(candidate)
    if cfg.package:
        archive = cfg.output_dir / "motion_poster_package.zip"
        manifest = cfg.output_dir / "DELIVERY_MANIFEST.md"
        package_outputs(cfg, files, manifest, archive)
        logging.info("Package verified: %s", archive)
    logging.info("Done: %s", output)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AutomationError as exc:
        logging.error("%s", exc)
        raise SystemExit(2)
