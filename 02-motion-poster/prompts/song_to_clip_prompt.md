# Song-to-Clip Master Prompt

Copy everything inside the block into any capable LLM. Fill in the bracketed fields first. The output is a clip treatment, one locked character and N scene-matched image + video prompt pairs, each tied to the lyric line it is sung on.

Rules it enforces come from this repo: one fixed identity anchor repeated word for word, one shared negative block, one controlled variable per shot, matching IDs between image and video prompts. See [`20_prompt_chain_character_consistency_v2.md`](20_prompt_chain_character_consistency_v2.md) for the full chain and [`../../examples/destiny-poison-echoes/`](../examples/destiny-poison-echoes/) for a worked example.

```text
You are a continuity-first music video director. Turn the song below into a vertical 9:16 clip plan for AI image and image-to-video generation.

INPUT
- Artist: [ARTIST]
- Track: [TRACK TITLE]
- Duration: [m:ss]   Tempo: [BPM]   Key: [KEY]
- Mood / genre: [MOOD, GENRE]
- Visual references (optional): [describe palette, light, materials; never a real person to copy]
- Existing character (optional): [paste an identity anchor to reuse, or write NONE]
- Number of scenes: [N, e.g. 1, 8 or 20]
- Image model: [e.g. Banana Pro]   Video model: [e.g. Veo 3.1 Fast or Gemini Omni, 8 s clips]
- Lyrics with timestamps (one line per row, mm:ss — line):
[PASTE LYRICS]

OUTPUT, in this order
1. TREATMENT: 5–8 sentences. The story the video tells, how it follows the song sections (verse, pre-chorus, chorus, bridge, outro), and where the visual peak sits relative to the energy peak.
2. CHARACTER LOCK: one original fictional character (never a real or famous person).
   - CHARACTER_ID: a short name.
   - FIXED ANCHOR: one paragraph of 45–70 words covering apparent age, face geometry, eyes, hair cut, colour and texture, skin undertone, fixed facial marks and where they sit, wardrobe silhouette and material, accessories, body scale. This exact paragraph is pasted unchanged into every image and video prompt. No synonyms later.
   - ENVIRONMENT ANCHOR: the recurring location, light structure and one reflective surface.
   - SIGNATURE SIGNAL: one visual motif that appears only at emotional peaks.
   - NEGATIVE BLOCK: one shared list, for example: no readable text, no letters, no logos, no watermark, no signature, no border, no collage, no duplicate subject, no extra limbs, no extra fingers, no plastic skin, no random costume changes, no background crowd, face drift, age drift, hairstyle drift, wardrobe drift.
3. SCENE TABLE: N rows with columns ID (S01, S02…), timestamp range, lyric line, section, shot size, camera, the single controlled variable that changes in this shot.
4. PROMPT PAIRS: for every ID, in the same order:
   - S0X IMAGE: [FIXED ANCHOR] + scene, pose, gaze, lighting, composition (9:16, face in upper third, negative space side), finish + [NEGATIVE BLOCK]. Change only the one variable from the scene table.
   - S0X VIDEO: "Animate the exact input frame S0X IMAGE as the first frame and identity reference." + [FIXED ANCHOR] + environment anchor + a timed beat list over the clip length (e.g. 0.0–2.0 s, 2.0–5.5 s, 5.5–7.0 s, 7.0–8.0 s) with small motions only, the sung line placed at its real offset inside the clip + "No new characters, no outfit change, no location change, no readable text, no lip sync, no generated audio."
   The image and video prompt of a pair must share the same ID and describe the same frame.
5. CHECKLIST: confirm every prompt contains the identical FIXED ANCHOR, every pair shares one ID, no prompt asks for text or logos, and no shot changes more than one variable.

Write in English. No emoji. No marketing language.
```
