# Climate Explorer demo storyboard

The [official submission guide](https://www.spaceappschallenge.org/resources/project-submission-guide/) permits either a video of at most 30 seconds or a deck of at most seven slides, including title slides. The recommended format is a seven-slide English deck. It allows the evidence to be read without rushing technical claims into a short video.

This is content for a deck, not a finished demo artifact. Create the actual deck from the final release. Use actual application screenshots and charts. Keep the early-work and AI disclosure visible. Do not include a minor's photo, voice, likeness, or identifying name while age and applicable restrictions are unresolved. The guide's suggested team/member identification must be reconciled with its minor protections before final delivery.

## Seven slides

| Slide | Title and visible text | Visual and source |
|---|---|---|
| 1 | **Climate Explorer**. Historical climate trends with visible assumptions. Prototype begun 11 November 2026. Eligibility unresolved. | Actual project screen. Team label only after confirmed; no invented member names. |
| 2 | **A student climate investigation**. A fitted line gives a rate. Its uncertainty depends on assumptions. Can the student see when a conclusion changes? | Actual annual chart with rate, units, period, and source. State proposed audience; do not claim measured learning. |
| 3 | **The investigation workflow**. Select a variable and location. Inspect the annual series. Compare methods and date windows. | Actual controls beside the resulting method comparison. POWER data and native grid scale visible. |
| 4 | **A failed assumption in the experiment**. No true trend; 45 annual values; AR(1) correlation 0.7. Ordinary interval excludes zero: 42%. Newey-West auto lag: 26.2%. Neither reaches the nominal 5%. | Simple labelled chart from evaluation/results.json. Caption: 2,000 synthetic records in this scenario; not observed city error rates. Link complete protocol. |
| 5 | **A source disagreement worth investigating**. Same years can give different rates in POWER and GISTEMP. The grids and processing differ. | Actual five-location comparison or Toronto rows. Use current release values and current audit finding. Do not assert an unsupported cause. |
| 6 | **A result another person can repeat**. Source data and settings travel with the export. Offline replay recalculates the result. | Actual JSON export and successful replay output from the release. Brief claim about tests only if count remains current. |
| 7 | **Evidence and next validation**. Working prototype. Student usability study pending. No causal or forecasting claim. Code, sources and AI assistance are documented. Early work and AI ideation require organizer review. | Public release and evidence links. Visible “AI-assisted code and content” disclosure. |

Most slides should contain a single main visual and no more than a few short sentences. References can be linked from each slide to the release documents. Do not shrink a long methods section onto a slide.

## Optional video alternative

Use screen capture and readable captions. No generated voice or imagery is necessary. Keep the complete video under 30 seconds; verify its duration after export.

| Time | Caption | Screen |
|---|---|---|
| 0–4 s | Climate Explorer investigates historical climate trends with NASA data. | Name and actual chart |
| 4–10 s | Compare the estimated rate under different assumptions and date windows. | Method comparison and period check |
| 10–17 s | Our synthetic tests show why a narrow interval can mislead. | One labelled simulation failure |
| 17–23 s | Export source data and settings. Repeat the calculation offline. | Export and replay |
| 23–29 s | AI-assisted prototype. Built from 11 November. Eligibility unresolved. User testing pending. | Public evidence links and disclosure |

This alternative gives less space for scientific detail than the deck. Do not speed up illegible text or add unsupported impact claims to make it sound stronger.

## Rehearsal before sharing

The student should explain a per-decade rate, a confidence interval's assumptions, why Newey-West leaves the OLS rate unchanged, and why source agreement is not proof. If he cannot explain one of these, use EXPLANATION.md and practice before presenting. Do not replace learning with memorizing a claim about personal work.
