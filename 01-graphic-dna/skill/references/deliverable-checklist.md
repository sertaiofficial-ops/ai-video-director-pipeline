# Deliverable Checklist

## Source and analysis

- [ ] The user's uploaded file or an accessible URL has been identified.
- [ ] Direct access to the URL has been tried; embed/public alternatives checked if needed.
- [ ] Video technical properties measured with `ffprobe`.
- [ ] Audio extracted and BPM/energy/brightness analyzed; missing dependencies installed safely.
- [ ] Contact sheet or enough visual samples reviewed.
- [ ] Principles observed in the source separated from original SERTAI equivalents.

## Production brief

- [ ] Purpose, length, aspect ratio, audience or demo assumptions written down.
- [ ] Global style, character appearance, environment, camera language and BGM source locked.
- [ ] The `style` field does not exceed 100 characters.
- [ ] Each clip contains one scene / one main movement.
- [ ] Each clip has a detailed transition description of 2–4 sentences.
- [ ] If there is separate music, a per-second Emotional Arc List exists.

## Image and audio production

- [ ] The primary character reference was generated first.
- [ ] A 9:16 first frame was generated from the reference character.
- [ ] The video prompt covers appearance, motion trajectory, state change and environment continuity.
- [ ] The separate BGM prompt covers length, BPM, key, genre, mood, instrumentation, structure, sound space and negative phrases.
- [ ] The music prompt does not imitate a recognizable existing melody.
- [ ] The generated video was checked with `ffprobe` for file integrity only.

## Edit and delivery

- [ ] Video and BGM brought to the same target length.
- [ ] Existing video audio, if any, kept in the mix or its handling explained per the user's preference.
- [ ] Output is 9:16 vertical and H.264/yuv420p; audio is AAC or the format the user requested.
- [ ] `SERTAI LAB`, if needed, is small, low-opacity and in a safe corner.
- [ ] The final report was rewritten from the interim notes.
- [ ] Final MP4, BGM, raw video, references, analyses, prompts and plan are in a single ZIP archive.
- [ ] ZIP verified with `unzip -t`.

## Known limitations

Generative models may not follow length or BPM requests exactly. Post-processing can be applied in that case, but do not present the corrected result as an exact technical match to the source. If the user wants to reproduce people, logos or copyrighted scenes from the source video as is, clarify the permission/license situation first and return to original aesthetic principles.
