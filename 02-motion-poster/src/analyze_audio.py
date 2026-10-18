#!/usr/bin/env python3
"""Best-effort audio measurements for SERTAI cue planning.

All values are labelled measured or approximate. The script uses ffprobe for
portable technical metadata and optional Python DSP libraries when available.
"""
from __future__ import annotations

import json
import math
import shutil
import subprocess
import sys
from pathlib import Path


def run_probe(path: Path) -> dict:
    if not shutil.which("ffprobe"):
        raise RuntimeError("ffprobe is required")
    cmd = [
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration,format_name:stream=codec_type,codec_name,sample_rate,channels",
        "-of", "json", str(path),
    ]
    result = subprocess.run(cmd, check=True, text=True, capture_output=True)
    return json.loads(result.stdout or "{}")


def read_mono(path: Path):
    try:
        import numpy as np  # type: ignore
        import soundfile as sf  # type: ignore
    except ImportError:
        return None, None
    try:
        data, sample_rate = sf.read(str(path), always_2d=True)
    except Exception:  # format not supported by libsndfile (e.g. AAC/M4A)
        return None, None
    mono = np.mean(data, axis=1).astype(np.float32)
    return mono, int(sample_rate)


def estimate(mono, sample_rate: int) -> dict:
    if mono is None or len(mono) == 0:
        return {"status": "unavailable", "bpm_approx": None,
                "note": "DSP estimates skipped: install numpy and soundfile, and use a format libsndfile can read (WAV, FLAC, OGG; MP3 with libsndfile >= 1.1). Convert other formats to WAV first."}
    import numpy as np  # type: ignore
    rms = float(np.sqrt(np.mean(np.square(mono))))
    peak = float(np.max(np.abs(mono)))
    window = max(1, int(sample_rate * 0.05))
    frames = len(mono) // window
    if frames:
        shaped = mono[: frames * window].reshape(frames, window)
        rms_values = np.sqrt(np.mean(np.square(shaped), axis=1))
        dynamic_range_db = float(20 * math.log10(max(float(np.max(rms_values)), 1e-9) / max(float(np.min(rms_values[rms_values > 0])) if np.any(rms_values > 0) else 1e-9, 1e-9)))
    else:
        dynamic_range_db = None
    spectrum = np.abs(np.fft.rfft(mono[: min(len(mono), sample_rate * 30)]))
    frequencies = np.fft.rfftfreq(len(mono[: min(len(mono), sample_rate * 30)]), 1 / sample_rate)
    brightness_hz = float(np.sum(frequencies * spectrum) / max(np.sum(spectrum), 1e-9))
    return {
        "status": "approximate",
        "rms_linear": rms,
        "peak_linear": peak,
        "dynamic_range_db_approx": dynamic_range_db,
        "spectral_centroid_hz_approx": brightness_hz,
        "bpm_approx": None,
        "note": "BPM requires a beat-tracking dependency; spectral and level values are DSP estimates.",
    }


def main() -> int:
    if len(sys.argv) != 2:
        print(f"Usage: {Path(sys.argv[0]).name} AUDIO", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    if not path.is_file():
        print(f"Audio not found: {path}", file=sys.stderr)
        return 2
    probe = run_probe(path)
    stream = next((s for s in probe.get("streams", []) if s.get("codec_type") == "audio"), None)
    if stream is None:
        print(f"No audio stream found: {path}", file=sys.stderr)
        return 2
    fmt = probe.get("format", {})
    mono, sample_rate = read_mono(path)
    result = {
        "file": str(path),
        "duration_seconds": {"value": float(fmt.get("duration", 0) or 0), "status": "measured"},
        "format": {"value": fmt.get("format_name"), "status": "measured"},
        "sample_rate_hz": {"value": int(stream.get("sample_rate", 0) or 0), "status": "measured"},
        "channels": {"value": int(stream.get("channels", 0) or 0), "status": "measured"},
        "codec": {"value": stream.get("codec_name"), "status": "measured"},
        "analysis": estimate(mono, sample_rate or int(stream.get("sample_rate", 44100) or 44100)),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
