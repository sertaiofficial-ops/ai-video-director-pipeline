"""Offline tests for 02-motion-poster/src. No network, API keys or paid calls."""
import json
import subprocess
import sys
from pathlib import Path
from unittest import mock

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "02-motion-poster" / "src"
sys.path.insert(0, str(SRC))

import analyze_audio  # noqa: E402
import google_flow_banana_api as api  # noqa: E402
import run_banana_flow_prompt_pack as pack  # noqa: E402


@pytest.fixture(autouse=True)
def no_credentials(monkeypatch):
    for name in ("GEMINI_API_KEY", "GOOGLE_API_KEY", "GOOGLE_CLOUD_PROJECT"):
        monkeypatch.delenv(name, raising=False)


# ---------- analyze_audio ----------

def test_estimate_sine_levels():
    sr = 8000
    t = np.arange(sr * 2) / sr
    mono = (0.5 * np.sin(2 * np.pi * 440 * t)).astype(np.float32)
    out = analyze_audio.estimate(mono, sr)
    assert out["status"] == "approximate"
    assert out["peak_linear"] == pytest.approx(0.5, abs=1e-3)
    assert out["rms_linear"] == pytest.approx(0.5 / np.sqrt(2), abs=1e-3)
    assert out["spectral_centroid_hz_approx"] == pytest.approx(440, abs=15)


def test_estimate_unavailable():
    assert analyze_audio.estimate(None, 44100)["status"] == "unavailable"


def test_analyze_audio_cli_on_generated_wav(tmp_path):
    sf = pytest.importorskip("soundfile")
    sr = 16000
    t = np.arange(sr) / sr
    wav = tmp_path / "tone.wav"
    sf.write(str(wav), 0.3 * np.sin(2 * np.pi * 1000 * t), sr)
    r = subprocess.run([sys.executable, str(SRC / "analyze_audio.py"), str(wav)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    data = json.loads(r.stdout)
    assert data["sample_rate_hz"]["value"] == sr
    assert data["channels"]["value"] == 1
    assert data["duration_seconds"]["value"] == pytest.approx(1.0, abs=0.01)
    assert data["analysis"]["spectral_centroid_hz_approx"] == pytest.approx(1000, abs=30)


def test_analyze_audio_usage_error():
    r = subprocess.run([sys.executable, str(SRC / "analyze_audio.py")], capture_output=True, text=True)
    assert r.returncode == 2


# ---------- google_flow_banana_api ----------

def test_find_media_nested_and_convenience():
    nested = {"outputs": [{"type": "text"}, {"type": "image", "data": "QUJD"}]}
    assert api.find_media(nested, "image") == ("data", "QUJD")
    assert api.find_media({"output_video": {"uri": "gs://b/v.mp4"}}, "video") == ("uri", "gs://b/v.mp4")
    assert api.find_media({"x": 1}, "image") is None


def test_read_prompt(tmp_path):
    assert api.read_prompt("  hi  ", None, "P") == "hi"
    f = tmp_path / "p.txt"
    f.write_text("from file\n", encoding="utf-8")
    assert api.read_prompt(None, f, "P") == "from file"
    f.write_text("   ", encoding="utf-8")
    with pytest.raises(api.ApiIntegrationError):
        api.read_prompt(None, f, "P")


def test_load_key_missing_raises():
    with pytest.raises(api.ApiIntegrationError):
        api.load_gemini_key()


def test_request_json_is_mocked_and_handles_errors():
    ok = mock.Mock(status_code=200)
    ok.json.return_value = {"id": "abc"}
    bad = mock.Mock(status_code=403, text="denied")
    with mock.patch.object(api.requests, "request", return_value=ok) as req:
        client = api.GeminiInteractionsClient("fake-key", timeout=5, store=False)
        assert client.create({"model": "m"}) == {"id": "abc"}
        _, kwargs = req.call_args
        assert kwargs["json"]["store"] is False
        assert kwargs["headers"]["x-goog-api-key"] == "fake-key"
    with mock.patch.object(api.requests, "request", return_value=bad):
        with pytest.raises(api.ApiIntegrationError, match="HTTP 403"):
            api.request_json("GET", "https://example.invalid", headers={})


def test_dry_run_makes_no_network_call(tmp_path, monkeypatch):
    out = tmp_path / "out"
    monkeypatch.setattr(sys, "argv", ["x", "--dry-run", "--visual-prompt", "poster", "--video-prompt", "motion", "--output-dir", str(out)])
    with mock.patch.object(api.requests, "request", side_effect=AssertionError("network used")), \
         mock.patch.object(api.requests, "get", side_effect=AssertionError("network used")):
        assert api.main() == 0
    record = json.loads((out / "run.json").read_text(encoding="utf-8"))
    assert record["status"] == "DRY_RUN"
    assert record["plan"]["video"]["output"].endswith("video.mp4")


# ---------- run_banana_flow_prompt_pack ----------

def test_parse_prompt_file_and_duplicates(tmp_path):
    good = tmp_path / "p.md"
    good.write_text((SRC.parent / "prompts" / "20_banana_pro_visual_prompts.md").read_text(encoding="utf-8"), encoding="utf-8")
    entries = pack.parse_prompt_file(good)
    assert len(entries) == 20
    assert "M01" in entries and entries["M01"]["prompt"]
    empty = tmp_path / "empty.md"
    empty.write_text("nothing here", encoding="utf-8")
    with pytest.raises(pack.AutomationError):
        pack.parse_prompt_file(empty)


def test_validate_common_flags_missing_phrases():
    entries = {"M01": {"id": "M01", "title": "t", "prompt": "a plain prompt"}}
    errors = pack.validate_common(entries, "Visual", 8.0, "9:16")
    joined = " ".join(errors)
    assert "expected 20 prompts" in joined
    assert "missing 9:16" in joined and "no watermark" in joined


def test_prompt_pack_dry_run_passes(tmp_path):
    out = tmp_path / "pack"
    r = subprocess.run([sys.executable, str(SRC / "run_banana_flow_prompt_pack.py"), "--dry-run", "--output-dir", str(out)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert "DRY RUN PASS" in r.stdout
    validation = json.loads((out / "validation.json").read_text(encoding="utf-8"))
    assert isinstance(validation, dict)
    assert (out / "run_config.json").exists()
