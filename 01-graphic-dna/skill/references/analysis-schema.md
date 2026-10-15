# Source Analysis Template

## Technical media table

| Field | Value | Source/command |
|---|---:|---|
| Duration |  | `ffprobe` |
| Video resolution |  | `ffprobe` |
| Framing/aspect ratio |  | `ffprobe` + visual check |
| Frame rate |  | `ffprobe` |
| Video codec |  | `ffprobe` |
| Audio codec |  | `ffprobe` |
| Audio sample rate |  | `ffprobe` |
| Channel count |  | `ffprobe` |
| BPM |  | `analyze_audio.py` |
| RMS energy |  | `analyze_audio.py` |
| Spectral brightness |  | `analyze_audio.py` |

## Timecoded scene analysis

| Time | Scene/subject | Framing/lens | Camera or motion | Color/light | Texture/optical processing | Edit/transition | Audio |
|---|---|---|---|---|---|---|---|
| 00:00– |  |  |  |  |  |  |  |
| 00:00– |  |  |  |  |  |  |  |

## Graphic DNA table

| Dimension | Principle observed in the source | Original SERTAI equivalent |
|---|---|---|
| Line and render |  |  |
| Color hierarchy |  |  |
| Light and contrast |  |  |
| Texture and optical processing |  |  |
| Composition and lens |  |  |
| Motion and editing |  |  |
| Symbolic objects |  |  |
| Typography |  |  |
| Sound and music |  |  |

## Analysis summary paragraph

Summarize the distinctive essence of the source video in one paragraph. Separate character, scene or brand elements that could be copied one-to-one; relate the reproducible abstract principles to the SERTAI adaptation. Do not state unmeasured properties of the source as fact; use "observed", "approximate" or "could not be verified".

## Acceptance checks

Compare frame samples with the automatic report. Take technical values from `ffprobe` output. Produce BPM/energy values with `analyze_audio.py`. Verify any text visible in the video separately by visual inspection. If audio cannot be listened to, say so explicitly and report only measured/detected information.
