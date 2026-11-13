# Climate Explorer 1.0 silent video

This is the preserved 1.0 artifact. The current public film uses [the narrated story](STORY_PRODUCTION.md).

[The MP4 demonstration](climate-explorer-demo.mp4) lasts **29.00 seconds**. It is silent, with English captions on screen and an additional [WebVTT caption file](climate-explorer-demo.vtt). The video uses actual retained analysis values to show the project's investigation workflow. It is a sequence of data figures, not a screen recording or a fictional application interface.

Every frame visibly identifies the video as an AI-assisted demonstration. The persistent footer records the 11 November start and unresolved eligibility. There is no person's name, likeness, face, voice or personal recording. No NASA branding or generated decorative imagery is included.

## Scenes

| Time | Content | Evidence |
|---|---|---|
| 0-3 seconds | Project and challenge | Student's chosen title and official challenge |
| 3-9 seconds | Tehran temperature and fitted rate | Retained 1981-2025 annual values, about +0.504 °C per decade |
| 9-15 seconds | Conditional intervals and date sensitivity | Retained method checks; 1981-2025 and 1986-2020 rates |
| 15-20 seconds | Toronto source and location diagnostic | All five displayed rates come from the frozen science audit and GISTEMP comparison |
| 20-25 seconds | Evidence export and offline replay | Raw source, settings, hashes and successful replay of the retained Tehran example |
| 25-29 seconds | Public examples and accurate status | Repository and demonstration access; AI and early-work concerns remain visible |

The clip does not claim that methods are universally calibrated, source differences have a demonstrated cause, or educational impact has been measured. The longer PDF and repository provide the scientific detail.

## Rebuild and verify

Install the separate optional PDF tools as described in DEMO_ARTIFACT.md. FFmpeg and FFprobe must be installed too. They are media tools, not application dependencies.

```sh
.demo-venv/bin/python submission/build_demo_video.py
ffprobe -v error -show_format -show_streams submission/climate-explorer-demo.mp4
```

The builder renders six data figures from ReportLab through MuPDF and encodes them with FFmpeg. No new NASA request is made. It checks the duration, resolution and absence of audio. `video-verification.json` records the MP4 hash, source hashes, codec, 696 frames, source tools, and review results. All six scenes were inspected after encoding, and the full file decoded without errors. Captions and watermarks remain readable and unclipped.

## Sources and public delivery

NASA POWER provides the actual temperature series. NASA GISTEMP provides the comparison field. Their provenance and acknowledgement remain in the repository's data and evaluation files. Codex wrote the original figure and video scripts and captions. This is AI assistance to code and content, not AI generation of the NASA observations.

The original public video URL now serves the narrated replacement. The 1.0 silent video remains in the v1.0.0 Git tag and release assets. The original silent artifact is checked against video-verification.json. Current public release checks instead use climate-explorer-story-judge.json for the narrated replacement; do not compare those different artifacts as if they were identical. The player uses the embedded captions by default; optional WebVTT captions can be enabled without changing the source video. The video and PDF are alternative demonstration artifacts; use the chosen artifact's exact public URL in the official form. Publishing a file does not submit the competition project.
