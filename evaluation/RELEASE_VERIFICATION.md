# Climate Explorer 1.0 release verification

Release work dated 13 November 2026, Tehran time (UTC+3:30). Version 0.4.0 is preserved at commit `e21bde3903eba8d44ec1e501103485fd1fc99627`. Its Linux CI succeeded in runs 43388445880 and 43388446054. The 1.0 runtime and media checks are recorded below, with public deployment evidence added after deployment.

## Observed local checks

- All 83 numerical, HTTP, build, browser-module and public-verification tests pass with zero skips. The engineering agent also passed the preceding 81-test suite in a clean macOS environment installed from the exact lock. Its dated report remains in engineering-checks.json.
- All static JavaScript passes Node syntax checks. Dependency checks pass. Python 3.14 is the supported application runtime.
- Forty frozen analyses cover five locations, two variables and four fixed periods. Every analysis replays without a NASA request. Retained hashes, endpoints, coordinates and periods are checked before building.
- Twenty browser-module/integration tests cover aggregation, source hash serialization, point estimates, untrusted input, storage failure, clear-during-save, delayed files and pending configuration responses. Browser checks explicitly do not recalculate uncertainty intervals, p-values, residual correlation or bands.
- Anonymous local HTTP verification checks all 55 built files against the manifest and replays all forty analyses. Two regression tests exercise this real HTTP path, including rejection of altered video bytes even if the asset manifest is also changed.
- Actual Chrome tested the 2011–2025 precipitation period, all-four-period table, note entry, opt-in save, reload, explicit restore, JSON download and file import. The actual download replays fifteen annual values. These are release-QA notes, not invented student work.
- Chrome printed a five-page investigation. The resulting private PDF retains every entered note and the AI/method-limit disclosure. Extracted text and the rendered final page were checked. The private scratch PDF is not a submission artifact.
- The seven-page PDF and all six encoded video scenes were rendered and visually reviewed. The MP4 is 29.00 seconds, 1280×720, H.264, yuv420p, 696 frames, with no audio. Full decoding passed. English captions, visible AI assistance and the recorded start date remain present. Media hashes are in submission/demo-verification.json and video-verification.json.

## Fixes found during verification

A baseline test assumed the public demo would always contain ten records. Its original-ten check now names those fixtures explicitly, and a new integration check verifies all forty periods. Slow file loads and configuration responses could overwrite newer actions; asynchronous saves could complete after clearing. These races were corrected and regression-tested. A missing import in the new media verification path was found by running the real command, fixed, and covered by the new HTTP verification tests. No failed check is recorded as successful.

## Hosted and package checks

The 1.0 runtime commit is `ea820c5fda5672b039ae421ec2b9ebc555f60d7e`, with source fingerprint `7f90ec174eaff5ad27b1185fadd0c89409b8b94c50127a0a31c76123368abc3b`. [Linux run 43389104282](https://github.com/ArmanDamirchilou/climate-explorer/actions/runs/43389104282) passed all 83 tests and deployed the site.

Anonymous HTTP checks verified 55 public files, all forty analyses and both media hashes. Chrome played the packaged video. This revealed duplicate captions from enabling the optional WebVTT track by default on top of the embedded captions. The default track setting was removed; embedded English captions remain visible, and optional captions remain available. The corrected player was rechecked.

A clean tracked-source package was built and all 170 included source/demo files were verified against its internal manifest. Archive structure excludes environments, private baseline archive and unrelated root documents. The final release archive is rebuilt from the final clean commit and carries that exact commit and a checksum in its accompanying verification JSON. Current public checks are in public-verification.json.

## Limits and honest history

The method settings remain version 0.2.1. No new statistical calibration, cause for Toronto's mismatch, rainfall source validation, station validation, user outcome or award has been established. The 1.0 label documents a complete software workflow and compatibility contract.

Development began on 11 November. AI contributed the approach, implementation, research and media. Eligibility, actual team/guardian details and Ankara online delivery remain separate personal or organizer checks. Nothing has been submitted or sent to Farhad by the assistant.

Historical 0.3 evidence: [release record](RELEASE_VERIFICATION_030.md). The full history is in [CHANGELOG.md](../CHANGELOG.md).
