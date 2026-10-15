# SERTAI — Clip Plan

## Global definitions

| Field | Decision |
|---|---|
| Goal | Character continuity and graphic DNA test demo on the Destiny Poison excerpt |
| Source audio | User-supplied `destiny_poison_after_hours_echoes_excerpt.wav` (Echoes — from the Destiny Poison (After Hours) EP) |
| Video length | 8.0 s for the first test; the 13.077 s source excerpt is archived separately |
| Framing | 9:16 vertical, 720×1280 output |
| Visual style | `Cyberpunk poison portrait; red/black chrome, acid-green cracks, wet grain.` |
| BGM source | Not `separate`; the supplied audio is kept as the main soundtrack |
| Audio | No dialogue, narration or added music |
| Brand label | Small `SERTAI LAB` in a safe lower corner of the final edit |

## Character lock: Poison Signal

Poison Signal is a SERTAI figure that stays true to the character identity in the reference set, with a newly designed scene and movement: androgynous/male read in their 20s, pale greenish skin, wet messy black hair, slim face, tired and controlled gaze, black leather jacket, black trousers, small metal earrings, and neon-green crack/corrosive vein patterns across the face and neck. In the final move the eyes give a short red pulse; chrome mechanical face and jacket reflections appear only as a transformation accent. Hair, face proportions, jacket silhouette, the general placement of the green cracks and body scale stay constant throughout the clip.

## Clip 01 — The poison looks back

| Field | Value |
|---|---|
| narrative_purpose | establish → develop → climax → resolve |
| pacing | slow to moderate, final beat sharp |
| scene | Night; a dark interior somewhere between an industrial lab and a parking garage; very faint green reflection on wet concrete; red vertical light leaks and black glass/metal panels behind. The location stays the same throughout. |
| content_action | Poison Signal first stands neutral and still; as the camera moves in slightly, the neck and face cracks glow faintly like a green electric current. In the final section the character turns the head toward camera by a few millimetres, both eyes give a single red pulse, and the chrome texture on the right cheek ripples once like a liquid reflection. |
| transition_description | The same Poison Signal character remains in frame throughout: pale greenish skin, wet messy black hair, black leather jacket, small metal earrings, and a stable network of neon-green cracks across the face and neck. From 0–5.8 seconds, the camera performs a slow controlled push-in with a slight left-to-right arc while the character holds a neutral, tired gaze; the wet industrial room, red vertical light leaks, black glass panels, and low green floor reflection remain visible for the entire shot. From 5.8–8 seconds, the character turns the head only a few degrees toward camera, the green cracks briefly brighten, both eyes emit one restrained red pulse, and the chrome texture on the right cheek ripples once before the image cuts to near-black; no new character, outfit, or location appears. |
| target_duration | 8.0 s |
| camera_movement | Slow push-in + subtle arc, final micro-zoom |
| first_keyframe_framing | Medium close-up, eye-level, slightly off-center right, 35mm lens feel, face in upper-middle third, red negative space on left |
| first_keyframe_visible_content | Full head and upper torso, black leather jacket, wet black hair, green facial/neck fissures, one small metal earring, dark industrial interior, red vertical light leaks, low green floor reflection; no readable text |
| inter_clip_boundary | scene_cut |
| first_keyframe_reuse | no |
| on_screen_dialogue | None |
| sound_effects | None; preserve source song only |
| bgm_source | none / source-song replacement |
| bgm_cue | Source song is the only audio. Align visual pulses to approximately 107.67 BPM; do not generate replacement music. |
| narration_budget | 0 |
| narration_cue | None |

## Beat-sync map

The source tempo is approximately 107.67 BPM, so one beat is approximately 0.557 seconds. The 8-second proof-of-concept will use visual accents at the following approximate positions without forcing hard cuts on every beat: `[00.00]` still gaze; `[02.23]` first green fissure shimmer; `[04.46]` second shimmer and slightly stronger push-in; `[05.58]` tension lift; `[06.69]` red eye pulse; `[07.25]` chrome ripple; `[07.80–08.00]` near-black resolve. These are visual cue points, not a claim that every generated frame will land on a mathematically exact beat.

## Emotional Arc List

| Time segment | Mood/emotion | Visual density/brightness | Audio relation |
|---|---|---|---|
| `[00:00–02.23]` | Cold, dormant, watchful | Very low motion; black/green shadows | Source intro/first pulse |
| `[02:23–05.58]` | Poison awakening, controlled tension | Green fissures become more legible; red background remains restrained | Source groove/body |
| `[05.58–06.69]` | Threat approaching | Slightly tighter framing; red begins to dominate | Source lift |
| `[06.69–08.00]` | Flash of power, unresolved blackout | Red eye pulse, chrome ripple, hard dark resolve | Source accent/outro |

## Reference images required

| Element | Clips using it | Required image |
|---|---|---|
| Poison Signal identity | Clip 01 | Use provided `destiny_poison_character_premium.png`, `banana2.jpg`, and `bananapro.jpg` as identity/style references |
| Clip 01 environment | Clip 01 | Generate one 9:16 first keyframe with the character references and the new industrial red/green environment |

## Acceptance checks

Character face, hair, jacket, crack pattern and body scale must remain stable; the title typography and technical poster labels from the hero reference must not appear in the generated frame; the scene must remain one location; green cracks must brighten before the red eyes pulse; the chrome ripple must happen only at the end; output must stay 9:16; source audio must remain the only soundtrack.
