# Character Consistency Research Notes

## Midjourney

According to Midjourney's official Character Reference documentation, `--cref` carries a character image into new scenes. `--cw 100` preserves more detail, including face, hair and clothing, while `--cw 0` puts the weight mostly on the face. The documentation also recommends pairing the reference with a clear text prompt, treating the character reference as inspiration and guidance rather than an exact copy of the source image, and notes that small details may not match exactly. Source: [1].

According to Midjourney's official Omni Reference documentation, V7 uses `--oref` for character/object references and `--ow` to adjust the reference strength. V7 Omni Reference accepts a single reference image; the default is `--ow 100`, and the official recommendation is to keep the weight below 400 unless very high stylize values are used. In V7, `--oref` should be preferred over the older `--cref`. Source: [2].

According to the official Parameter List, parameters belong at the end of the prompt; controls such as `--ar`, `--sref`, `--oref`, `--ow`, `--seed`, `--no` and `--raw` should be written in that final section. Source: [3].

Midjourney's official Seeds documentation states clearly that a seed makes comparisons easier during testing but does not lock character or style identity on its own; references, style references and personalization are the real continuity tools. In optimized prompts, a seed should therefore support controlled A/B testing, not replace the character lock. Source: [4].

## Stable Diffusion / Diffusers

According to the Hugging Face Diffusers documentation, IP-Adapter combines image-based guidance with text-based diffusion generation. `set_ip_adapter_scale()` adjusts the influence of the image reference; the examples show `0.5` as a balanced starting point between text and image. The FaceID variant works with face embeddings; the Plus variant carries more general visual features. Source: [5].

The same documentation shows that IP-Adapter can be combined with ControlNet to control structural signals such as depth, edges and pose. IP-Adapter image embeddings can also be saved to disk and reused across generations, which improves consistency and efficiency when producing a series of frames. Source: [5].

## Practical takeaway

Do not rely on a long text prompt alone for character consistency. Use a fixed character bible, a fixed reference image, a fixed model/version, a fixed aspect ratio, low-to-medium creativity and a recorded seed. In Midjourney, use `--oref`/`--ow` for V7 and `--cref`/`--cw` for V6/Niji 6; on the Stable Diffusion side, add FaceID or IP-Adapter and, if needed, ControlNet pose/depth. In each new frame, change only pose, location, lens or a controlled expression; restate hair, face proportions, skin tone, crack pattern, clothing and accessories explicitly.

## References

[1]: https://docs.midjourney.com/hc/en-us/articles/32162917505293-Character-Reference "Midjourney — Character Reference"
[2]: https://docs.midjourney.com/hc/en-us/articles/36285124473997-Omni-Reference "Midjourney — Omni Reference"
[3]: https://docs.midjourney.com/hc/en-us/articles/32859204029709-Parameter-List "Midjourney — Parameter List"
[4]: https://docs.midjourney.com/hc/en-us/articles/32604356340877-Seeds "Midjourney — Seeds"
[5]: https://huggingface.co/docs/diffusers/en/using-diffusers/ip_adapter "Hugging Face Diffusers — IP-Adapter"
