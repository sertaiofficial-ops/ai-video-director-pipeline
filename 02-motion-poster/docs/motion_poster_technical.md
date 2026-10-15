# Motion Poster v2 — Technical Breakdown and Reproduction Guide

## 1. What did this demo do?

A motion poster is a fallback method that combines two controlled reference frames with the rhythm of the audio instead of running real image-to-video generation. The first frame shows the character in a neutral, cold, waiting state. The final frame is the resolution moment of the same character, with a short red pulse in both eyes and a liquid-chrome ripple on the right cheek. The motion in between is not a synthetic 3D transformation; it is micro-motion simulated with a controlled `zoompan`, timecoded color flashes and a `fadeblack` transition.

Use this method when the video model quota is exhausted, when only one or two strong image references exist, when the rhythm of a music excerpt needs a quick test, or when preparing an art-direction proof of concept for social media. The output must not be presented as a real image-to-video clip.

## 2. Input and output parameters

| Parameter | Value |
|---|---|
| Start image | `first_keyframe.png`, 1440×2560, 9:16 |
| Final image | `final_keyframe.png`, 1440×2560, 9:16 |
| Audio | `destiny_poison_after_hours_echoes_excerpt.wav` (Echoes — from the Destiny Poison (After Hours) EP) |
| Audio length | 13.077 s; the first 8.0 s were used in the edit |
| Audio format | 48 kHz, stereo, PCM signed 16-bit |
| Measured tempo | Approx. 107.67 BPM |
| One beat interval | Approx. 0.557 s |
| Video length | 8.0 s |
| Output resolution | 720×1280 |
| Output aspect ratio | 9:16 vertical |
| Frame rate | 24 fps |
| Video codec | H.264, `yuv420p`, CRF 18, `medium` preset |
| Audio codec | AAC, 192 kbps, 48 kHz, stereo |
| Web optimization | `-movflags +faststart` |
| Brand label | `SERTAI LAB`, white at 48% opacity, 20 px, lower-right safe area |

## 3. V1 motion poster chain

V1 uses only `first_keyframe.png`. The image slowly zooms in over 8 seconds. A low-level cyan flash is applied at roughly 2.20–2.50 s and 4.40–4.70 s, and a red flash at 6.65–7.05 s. This version is for fast, low-cost testing.

```bash
ffmpeg -y \
  -loop 1 -framerate 24 \
  -i first_keyframe.png \
  -i destiny_poison_after_hours_echoes_excerpt.wav \
  -filter_complex "[0:v]scale=820:1458:force_original_aspect_ratio=increase,crop=820:1458,zoompan=z='min(zoom+0.00075,1.06)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=720x1280:fps=24,drawbox=x=0:y=0:w=iw:h=ih:color=cyan@0.035:t=fill:enable='between(t,2.20,2.50)',drawbox=x=0:y=0:w=iw:h=ih:color=cyan@0.025:t=fill:enable='between(t,4.40,4.70)',drawbox=x=0:y=0:w=iw:h=ih:color=red@0.10:t=fill:enable='between(t,6.65,7.05)',drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:text='SERTAI LAB':fontcolor=white@0.48:fontsize=20:x=w-tw-22:y=h-th-26[v];[1:a]atrim=duration=8,asetpts=N/SR/TB[a]" \
  -map "[v]" -map "[a]" -t 8 \
  -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p \
  -c:a aac -b:a 192k -movflags +faststart \
  motion_poster_v1.mp4
```

### What the V1 parameters do

| Parameter | Function |
|---|---|
| `-loop 1` | Loops the single image as the frame source for the length of the video |
| `-framerate 24` | Locks input frame generation to 24 fps |
| `scale=820:1458` | Brings the 9:16 image to an intermediate processing size |
| `crop=820:1458` | Crops from the center without distorting the ratio |
| `zoompan` | Simulates a slow digital camera push-in |
| `z='min(zoom+0.00075,1.06)'` | Small zoom per frame; upper limit 1.06x |
| `x/y=iw/2-(iw/zoom/2)` | Keeps the zoom centered on the image |
| `d=1` | Processes each input frame as one output frame |
| `s=720x1280:fps=24` | Final vertical frame size and fps |
| `drawbox cyan@0.035` | Very subtle cyan atmosphere flash |
| `drawbox red@0.10` | Red color wash at the final tension point |
| `drawtext` | Low-opacity `SERTAI LAB` label |
| `atrim=duration=8` | Takes the first 8 seconds of the source audio |
| `-t 8` | Limits the final video to exactly 8 seconds |
| `-crf 18` | Image quality/compression balance |
| `-pix_fmt yuv420p` | Social-media-compatible pixel format |
| `-movflags +faststart` | Moves MP4 metadata to the front for fast web playback |

## 4. V2 motion poster chain

V2 uses the first frame and the final pulse frame. The first frame slowly zooms in for 6.7 seconds. The final frame is prepared for a short 1.6-second entrance. The two streams are joined with a 0.3-second `fadeblack` transition starting at 6.4 seconds. This gives the red eye pulse around 6.69 seconds and the chrome ripple around 7.25 seconds a visual final accent.

```bash
ffmpeg -y \
  -loop 1 -framerate 24 -t 6.7 -i first_keyframe.png \
  -loop 1 -framerate 24 -t 1.6 -i final_keyframe.png \
  -i destiny_poison_after_hours_echoes_excerpt.wav \
  -filter_complex "[0:v]scale=820:1458,zoompan=z='min(zoom+0.0008,1.05)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=720x1280:fps=24,setpts=PTS-STARTPTS[v0];[1:v]scale=820:1458,zoompan=z='min(zoom+0.0012,1.03)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=720x1280:fps=24,setpts=PTS-STARTPTS[v1];[v0][v1]xfade=transition=fadeblack:duration=0.3:offset=6.4,drawbox=x=0:y=0:w=iw:h=ih:color=red@0.07:t=fill:enable='between(t,6.65,7.10)',drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:text='SERTAI LAB':fontcolor=white@0.48:fontsize=20:x=w-tw-22:y=h-th-26[v];[2:a]atrim=duration=8,asetpts=N/SR/TB[a]" \
  -map "[v]" -map "[a]" -t 8 \
  -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p \
  -c:a aac -b:a 192k -movflags +faststart \
  destiny_poison_motion_poster_v2.mp4
```

### V2 timeline

| Time | Visual operation | Reason |
|---|---|---|
| 0.00–2.20 | Neutral character + slow zoom | Waiting, cold opening |
| 2.20–2.50 | Cyan flash | First biological/poison signal |
| 2.50–4.40 | Controlled zoom in the same framing | Preserve character continuity |
| 4.40–4.70 | Weaker cyan flash | The cracks wake up again |
| 4.70–5.58 | Push-in continues | Build tension |
| 5.58–6.40 | Red atmosphere builds | Lead into the final accent |
| 6.40–6.70 | `fadeblack` transition to the final frame | Sharp but soft resolve |
| 6.65–7.10 | Red color wash | Eye pulse and threat peak |
| 7.10–7.80 | Short hold/zoom on the final frame | Let the chrome ripple read |
| 7.80–8.00 | Near-black feel | Unresolved ending |

## 5. Doing it yourself, step by step

First prepare a 9:16 character reference and generate two states: a neutral start and a final pulse. In the image prompts, lock the face, hair, clothing, crack pattern and location constants explicitly. Keep the first 8 seconds of the source song as a separate file; convert it to WAV if needed and measure the BPM.

Then run the V1 chain to test the rhythm with a single image. If the rhythm works, move to V2: add the final pulse frame, adjust the `xfade` offset to the audio cue point and keep the opacity of the color flashes low. Finally, match audio and video length, add the `SERTAI LAB` label and export the file in a social-media-compatible format.

At every stage run these four technical checks: verify duration/resolution/fps with `ffprobe`; make sure the full source audio did not end up in the video by mistake; confirm the aspect ratio is still 9:16; test the ZIP archive with `unzip -t`. Do not stack effects to make the motion poster look strong; one camera move, one color signal and one final transformation are enough.

## 6. Moving to a real image-to-video version

Once quota or tool access is available, use `first_keyframe.png` as the first frame. Run the detailed prompt in `video_prompt.txt`; for real model motion, keep breathing, wet hair, a small head turn, the eye pulse and the chrome ripple in the same time windows. It does not matter if the model generates no audio; the Destiny Poison excerpt is added as the only audio in the final edit. Once a real image-to-video MP4 exists, keep the motion poster fallback in the archive as a technical reference and rhythm storyboard.
