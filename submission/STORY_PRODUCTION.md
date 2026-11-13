# Climate Explorer story video production

Prepared 13 November 2026. This records the narrated films published with release 1.2. The short film replaces the public silent clip; that earlier source remains preserved in release 1.0.

## Story and first three seconds

Open with the adult narrator asking, “Can one city tell two climate stories?” Show the person immediately. Reveal **one city** and **two stories** as spoken words, with Tehran rainfall identified. Do not open with a title slide, feature list or space footage.

The story uses one frozen NASA POWER response. The fitted annual-rainfall rate over 1981-2025 is **+36.901 mm/year per decade**. Over 2011-2025 it is **-52.832 mm/year per decade**. Both records carry the same raw-source hash. The recent ordinary 95% interval is **-172.276 to +66.612**, so it includes zero. A downward point estimate does not establish a significant decline or prove a climate reversal. The dates define different questions.

The conclusion is a practical habit: check the period, assumptions and evidence before sharing a climate claim. Educational impact has not been measured.

## Approved 65 word narration

Can one city tell two climate stories? Look at Tehran's rainfall. Over forty-five years, the fitted trend points up. Over fifteen, it points down. The dates changed. That doesn't prove the climate reversed. Climate Explorer lets you test that difference with NASA data. Compare periods, inspect uncertainty, and save the evidence so someone else can check your result. Before sharing a claim, check what changed.

This is 65 whitespace-separated words. Record or generate a natural read first, then cut to its actual timing. Keep the uncertain recent estimate visible when its negative slope appears. The judge cut must remain at most 30 seconds. The current production target is 29.8 seconds, including all opening and closing frames.

## Actual source performance and shot plan

The current generated source is a 30.041667-second portrait clip with native speech. Its automatic transcript matches the intended script through the final word around 28.72 seconds. A low-confidence extra transcription after that point needs human listening; do not add it to captions unless it is actually spoken. Caption timings come from the source performance, not guessed fixed reading speeds.

| Source time before speed adjustment | Picture and edit | Text and sound |
|---|---|---|
| 0-3 seconds | Fictional adult narrator, natural medium close-up. Small push-in. The question appears as emphasis beside the person. | Native speech starts immediately. No title jingle. Visible AI disclosure. |
| 3.5-5.2 seconds | Introduce Tehran annual rainfall, then match-cut from the narrator to actual data. | One quiet authored accent marks the chart reveal. |
| 5.2-8.7 seconds | Animate the actual annual values and full-period fitted line. Keep dates and units fixed and readable. | 1981-2025, +36.9. Label NASA POWER model grid. |
| 8.7-13.2 seconds | Highlight 2011-2025 within the same record. Draw its fitted line only over those years. | -52.8. The period label changes with the line. Never silently rescale the data to exaggerate a reversal. |
| 13.2-19.9 seconds | Show the recent interval crossing zero. Introduce the application name after the problem is clear. | “Recent estimate uncertain.” Explain that different dates ask different questions. |
| 19.9-22.5 seconds | Keep uncertainty visible while the narration says to inspect it. Actual app footage may replace a figure only if captured from the working release. | No simulated interface or fabricated interaction. |
| 22.5-26.1 seconds | Return to the narrator with a short evidence summary beside them. | Preserve the native voice. Mention saved source and settings without claiming the browser performs complete Python replay. |
| 26.1-end | Narrator finishes the practical takeaway. Project link remains readable. | A restrained closing accent. Do not cut off the last consonant to meet the duration limit. |

Use short matched cuts and restrained chart movement. The scientific values supply the visual drama. Avoid disaster imagery, an invented satellite view, a fake NASA control room, or an invented testimonial.

## Deliverables

The **landscape judge candidate** is 1920 by 1080, H.264 with AAC audio, at most 30 seconds. The **portrait portfolio reel** is 1080 by 1920 and about 45 seconds. Its final fifteen seconds expand the real investigation and evidence workflow. Mark the longer version **Portfolio reel, not the NASA submission demo** throughout. Do not put the longer reel in the official demo field.

Use new candidate filenames. Keep the earlier PDF, video and verification records until the replacement is checked and deliberately integrated. Publishing a new video does not submit the project or resolve eligibility.

## Sources for the charts and app

- [Full-period rainfall analysis](https://armandamirchilou.github.io/climate-explorer/demo/tehran-rainfall.json), retained video input `submission/story-inputs/tehran-rainfall.json`.
- [Recent fifteen-year analysis](https://armandamirchilou.github.io/climate-explorer/demo/tehran-recent15-rainfall.json), retained video input `submission/story-inputs/tehran-recent15-rainfall.json`.
- [Public application](https://armandamirchilou.github.io/climate-explorer/).
- [Source and methods](https://github.com/ArmanDamirchilou/climate-explorer).
- [NASA POWER methodology](https://power.larc.nasa.gov/docs/methodology/data/sources_meteorology/).

The record is coarse model-grid meteorology, not a station or street measurement. Annual rain totals come from monthly mean daily rates and calendar-day conversion. No AI-generated observations enter the charts.

The tracked video inputs preserve the exact release 1.1 rendered analyses. The actual application capture is `submission/story-app-capture.png`, captured from the working release 1.1 guided story. It appears at about 15.7-19.9 seconds, with a gentle camera move in the landscape cut, and again in the reel's extended investigation. Cropping frames real content for readability; it does not simulate a click, change the values or invent an interface.

## Reproduce the edit

The original generated presenter source is retained locally at `tmp/story-production/presenter.mp4`. Its hash and generation job identify the exact source. Do not spend credits regenerating a different performance to reproduce an existing edit. Obtain the original source file if it is absent. The retained `submission/story-inputs/presenter-transcript.json` contains the reviewed automatic timing draft from the larger speech-recognition model.

Use the optional media tools environment. Run from the repository root:

```sh
.demo-venv/bin/python submission/build_story_video.py \
  --presenter tmp/story-production/presenter.mp4 \
  --transcript submission/story-inputs/presenter-transcript.json \
  --app-frame submission/story-app-capture.png \
  --mode judge \
  --output submission/climate-explorer-story-judge.mp4

.demo-venv/bin/python submission/build_story_video.py \
  --presenter tmp/story-production/presenter.mp4 \
  --transcript submission/story-inputs/presenter-transcript.json \
  --app-frame submission/story-app-capture.png \
  --mode reel \
  --output submission/climate-explorer-story-reel.mp4
```

FFmpeg and FFprobe must be available. The builder also uses Pillow and NumPy, with installed Arial fonts on this Mac. Pass `--font` and `--bold-font` for another installed TrueType family. It writes new MP4 candidates, English WebVTT captions, actual encoded-frame posters, and per-cut JSON records. Intermediate image sequences stay under ignored `tmp/`.

The judge cut uses a synchronized 1.015 tempo adjustment for video and original speech. The 45-second reel preserves the source speech timing and adds fifteen seconds of evidence with authored instrumental tones. The generation and editing code do not establish human listening or audience feedback. Those checks must be recorded separately.

## Higgsfield workflow research

Higgsfield's [avatar guide](https://higgsfield.ai/blog/how-to-make-ai-avatar-2026), published 21 October 2026, describes an invented character reference, a voice track, and a talking video that reuses the references. Its [talking-character guide](https://higgsfield.ai/blog/still-image-to-talking-video), published 8 October, recommends checking audio duration before animating, using a clear unobstructed face, and reviewing identity and lip sync throughout the result. These support generating one continuous adult performance and editing it against deterministic data figures.

The [audio and lip-sync help page](https://higgsfield.ai/creator-hub/help-center/ai-models/how-do-i-use-lipsync-voiceover-and-aspect-ratios) distinguishes voice creation from talking-character animation and lists portrait and landscape formats. Available models and settings still need confirmation in the connected tool. The [cinematic tutorial](https://higgsfield.ai/blog/cinema-studio-3.5-full-tutorial), published 5 November, argues for choosing framing and movement to serve a scene's purpose. We apply that as restrained presenter framing and purposeful data reveals, not decorative camera tricks.

These are platform instructions, not evidence that a presenter improves scientific understanding or judging scores. Current costs and availability come from the actual generation receipt. No extra paid generation is part of this plan.

## Presenter and audio direction

The presenter is a fictional adult, clearly over 25, in a simple study. They are a narrator, not the student, a NASA employee, a scientist endorsing the project, or a real user giving feedback. Keep the delivery curious at the hook, precise at the data comparison, and calm at the uncertainty. Natural blinks and small gestures are enough.

Retain the generated clip's original speech and synchronize any slight whole-clip speed adjustment in both video and audio. Do not replace its voice after lip synchronization. Mix original synthesized ambient tones and short accents below the speech. Keep speech intelligible on laptop speakers. Avoid a dramatic score that turns uncertainty into a crisis claim.

Every frame needs a visible AI-generated presenter/voice or AI-assisted demonstration indicator. Descriptive text and MP4 metadata must identify the generated speech. Preserve the 11 November build date and unresolved early-work/AI-ideation concerns. No NASA logo or agency costume appears.

## Adult self recording alternative

If a real adult narrates instead, use their own face and voice with permission. Record at eye level in a quiet room, facing soft window light. Use a simple background, keep the mouth visible, and leave a little silence before and after the script. Record three natural takes without changing the factual wording. A plain recording with good sound is preferable to a rushed performance.

The student may practice privately. If he is under 18, do not use his face, voice, image or likeness in the NASA submission. Do not clone a minor's voice or use a face swap to imply that an adult narrator is the student. The fictional adult route avoids a personal recording.

## Release checks

Listen to the actual source and final mix. Correct automatic captions against what is spoken. Inspect the first three seconds, the two period labels, the interval crossing zero, the final sentence and both aspect ratios. Check every cut for mouth-sync discontinuity or clipped words. Decode the full video, inspect codec and duration with FFprobe, and verify the final public file hash. Keep generated-source and data-source hashes in the new production manifest. Only then replace the published candidate.


## Observed release results

Both final encodes passed a full decode and encoded-scene visual review. The short film is 29.800 seconds; the portrait reel is 45.000 seconds. The final mixed short-film audio automatically transcribes to the complete intended narration, including the closing sentence. Exact file hashes, source hashes, audio loudness and peak measurements are recorded in each cut's JSON. Chrome played both local files, and the public short film played with audio in Incognito without login. Human listening and audience feedback have not been recorded. The raw source stays private; edited, disclosed cuts are public.

The public builder now verifies media hashes before and after staging. A render that is still being written cannot replace an existing valid demonstration. The root release verification record records CI and anonymous HTTP checks.


## 1.3.1 distribution correction

The final host migration retired the old project-site address. The correction pass in correct_media_distribution_links.py replaces only the visible distribution rectangles with the stable dedicated repository address. Each media record preserves the original tagged video/record hashes, correction helper, rectangles and times. Full decodes pass; compressed AAC and decoded float-PCM hashes match before and after. The short poster is refreshed. Scientific figures, caption timing and narration remain. The original builder hash identifies the pre-correction composition. Earlier cuts remain in their own tags. The later final-reel automatic check produced extra words in its instrumental tail and is not a strict full-mix pass; human listening remains unperformed.
