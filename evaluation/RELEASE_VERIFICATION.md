# Version 1.3 release verification

Checked 13 November 2026. Earlier verification is preserved in RELEASE_VERIFICATION_100.md, RELEASE_VERIFICATION_110.md and RELEASE_VERIFICATION_120.md, with their separate public reports.

## Local software checks

All **151 tests pass with zero skips**, in 162.944 seconds on the current Mac with the CI thread controls. The suite includes independent enumeration and statsmodels interval references, all-cell reconstruction/replay, missing-year and unavailable-window behavior, cross-case and edited-source rejection, actual browser-module/app harness checks, HTTP recovery, exact deployed-path validation, media tamper rejection and build copy/rename rollback. An earlier complete 151-test run passed in 189.535 seconds; the final run includes the later verification-resource adjustments.

The public-check test serves a real temporary static build over HTTP without authentication and fully replays all **6,660** atlas cells, forty fixed-period analyses and two guided records. It checks reviewed hashes for all three films, caption tracks and posters. Matching a manifest alone is insufficient: tests alter media or omit atlas rows while updating the manifest and require rejection.

The final frozen build has **77 manifest-covered public files**. Static JavaScript syntax checks and the locked application's pip check pass. App release is 1.3.0; statistical settings remain 0.2.1. Runtime source fingerprint:

`6541292e4d39e3ad93f78602d83639b74fae4e5cef5bb22ef7d908a0bec9f2b7`

The guided record and retained film atlas use this fingerprint. The local full Python application was restarted at port 8766; its frozen Tehran rainfall atlas reports 1.3.0, the current fingerprint and 666 windows. Static film HTTP access returns 200, video/mp4 and the expected byte count.

Chrome loaded the complete Tehran rainfall atlas, announced the same raw-source hash and rendered the triangular map. Node harness checks exercise cell selection, keyboard movement, filters, chronological pagination, cancellation, source warnings, note preservation and late-request errors. This is not a new human usability, mobile-device or screen-reader certification. The prior 1.1 actual app capture remains identified as that release.

## Final technical film

- Exact video/audio duration: **135.000 seconds**; 4,050 video frames at 30 fps.
- 1920×1080 H.264/yuv420p; AAC stereo, 48,000 Hz; **12,492,700 bytes**.
- SHA-256: `aeb40d39bdf2750f6b86e86af48c5e009ddb1119c47409821a81078f23f60e58`.
- Post-AAC measured loudness **−19.22 LUFS**, true peak **−4.66 dBTP**, range **3.8 LU**. These are actual values, not an assertion that the initial −16 target was met.
- Full decode and 16 kHz PCM decode pass with **zero warnings**. Each chapter is decoded separately to uniform stereo PCM and joined at exactly 27 seconds; compressed streams with different channel layouts are not concatenated.
- Thirty-one encoded-sample review observations cover the five chapters, transitions, same-source figures, synthetic failure example, atlas plate, correction masks, subtitles and opaque closing card. Some ending times were checked twice.
- Forty-two valid, nonoverlapping WebVTT cues. Maximum reading speed 20.0 characters/second; no 22+ flags.
- The final mixed MP4's automatic medium.en transcription agrees with the revised **307-word** script after case, punctuation and equivalent number spelling are normalized. All five edited source checks agree independently with their paragraphs.
- Presenter footage is **480p origin**. Graphics, subtitles and composition are 1080p. The fictional adult presenter and voice are visibly disclosed throughout. The data-derived atlas plate is labeled as a rendering, not an interface capture; the genuine app image is identified as release 1.1.
- A native-voice correction take and full-clause omissions are explicit in the receipts. No incorrect name is silently inserted into captions. No student likeness, voice clone, invented observation or human testimonial is used.

The generation record retains five 27-second jobs and one 13-second correction job, all completed. Quotes total **444 credits** within the observed existing 444.73-credit balance. The initial 1080p attempt was rejected before a job started. No top-up, subscription or account was created. No human listening is claimed.

The 29.8-second demo candidate, 45-second portrait reel and reviewed seven-page PDF retain their previous hashes and identities. The long film is a technical portfolio explanation and exceeds the official demo limit.

## Deployment and package

Linux CI, anonymous public verification and the release archive are checked after the source commit. Their observed results will be recorded here before the final release tag. No pending run is counted as passed.

The initial Linux run [43454215563](https://github.com/ArmanDamirchilou/climate-explorer/actions/runs/43454215563), on runtime commit 661fe268d0cf649b4279a8af160ef81527510eac, exceeded the original ten-minute job allowance and was canceled. Its cold-atlas HTTP test also reached the test client's five-second timeout. It is not counted as a passing run. The client now allows thirty seconds for that cold request, while other HTTP tests retain their earlier bound. CI fixes numerical-library thread counts, allows twenty minutes and rejects malformed atlases before expensive replay; complete accepted-atlas replay is retained. Documentation/evidence-only changes and release tags reuse the verified runtime instead of starting duplicate numerical jobs.

## Open human and eligibility work

Numerical tests do not establish source truth, universal interval calibration or educational benefit. Matched station checks and real student/teacher tasks remain open. Development began 11 November, and AI contributed to the solution approach. Organizer eligibility, age/guardian/team details and local delivery procedure remain separate. No competition entry, Farhad message, award, human peer review or NASA endorsement is claimed.
