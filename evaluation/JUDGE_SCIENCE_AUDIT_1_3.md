# Critical science and challenge audit of version 1.3

Reviewed 13 November 2026 by a separate Codex specialist at the student's request. This is an AI-assisted internal review, not NASA judging, external peer review, human user testing, or an award prediction. The review distinguishes a demonstrated software defect from missing scientific or product evidence. Subsequent fixes must be verified separately from the original finding.

## Demonstrated defect

**High priority for Validity: ordinary offline replay did not bind the calculated numbers to their scientific labels.** In the released 1.3 implementation, `evaluation/replay.py:verify` checked the source hash, settings and numerical arrays/results, but did not check location against the recorded request, metadata against the selected variable, or the provenance URL. A direct adversarial probe made four independent copies of a valid Tehran rainfall analysis, then changed its location to Toronto, its annual unit to degrees Celsius, its request URL to an unrelated host, or its code fingerprint to an arbitrary 64-character hex value. Each still returned 45 verified annual observations. This does not show an incorrect original calculation. It shows that a mathematically correct but mislabeled investigation could pass that verifier.

The first three probes demonstrate the semantic binding defect. Acceptance of a different, correctly shaped code fingerprint is a verification-scope observation, not by itself a numerical replay defect: compatible earlier exports must remain replayable. The engineering reviewer owns the coordinated runtime fix and regression tests in `tests/test_replay_context.py`. Bind selected-variable units, numeric coordinates, request coverage and provenance to the retained source; validate calendar bounds before iteration. Treat a code fingerprint as recorded consistency metadata, not NASA authentication. Compatibility with older exports does not require their fingerprint to equal the current checkout. The independent atlas validator already checked its stronger basis contract. A selected investigation and its complete parent atlas remain different verification scopes.

## Evidence gaps that can lower scores

| Priority and criterion | Concrete evidence | What follows, and what does not |
|---|---|---|
| High, eligibility and truthful relevance | `README.md`, Competition status; `submission/REQUIREMENTS.md`, Two material eligibility concerns; `AI_ASSISTANCE.md` | Development began 11 November and AI helped choose the approach. Organizer interpretation is unresolved. More code, a new name, a new host or a later release cannot change that history. Do not submit a contrary authorship or event-only declaration. |
| High, impact and creativity | `evaluation/USER_TEST.md` has no observations; `RESEARCH.md` identifies educational benefit as a hypothesis | There is no evidence that learners understand uncertainty better with this workflow, or that 666 choices help more than four. Observe an actual task and retain errors before claiming benefit. A small convenience pilot can find confusion but cannot establish a general educational effect. |
| Medium, scientific validity | `evaluation/DATASET_CHECK.md`; `evaluation/SCIENCE_AUDIT.md`; `evaluation/STORY_SCIENCE_REVIEW.md` | Toronto's POWER/GISTEMP temperature difference remains unresolved. Rainfall has conversion checks but no independent product or station evaluation. Replay verifies computation from retained inputs; it does not validate climate truth. Do not use the temperature diagnostic to validate the Tehran rainfall story. |
| Medium, creativity | `INNOVATION_REVIEW.md`, Shortlist; prior art below | The methods, climate plotting, and start/end trend matrices are established. The defensible contribution is their specific learner-oriented evidence workflow. Its comparative value and broad originality are unproven. The 100-candidate review is a documented design search, not 100 implemented innovations or empirical evidence. |
| Medium, relevance and scope | `submission/verified-sources/challenge-requirements.json`; `climate.py:VARIABLES`; `README.md`, Data and method | Two NASA model variables, selected grid locations, historical rates and conditional significance assessment fit the stated core task. The public site is a frozen five-location demonstration; it does not itself offer live arbitrary-region acquisition. A point model-grid record is not a district survey, regional area mean, station measurement, forecast or causal attribution. State this scope when showing the public product. |

## Statistical claims that remain defensible with their limits

The annual transformations match the declared units: monthly temperature means are calendar-day weighted, and monthly precipitation rates in mm/day are multiplied by month length and summed. Complete-year filtering avoids silently annualizing partial years. The synthetic study exposes failures of ordinary and adjusted intervals instead of selecting a method by its desired real-data result.

An exhaustive atlas exposes a declared collection of date choices. It does not remove selection bias or supply simultaneous inference. Ten years is an exploration threshold, not a universal minimum for reliable climate detection. Each overlapping period estimates its own period-specific rate. Neither sign counts nor the fraction of intervals excluding zero measures a probability that a city is changing. The ordinary and HAC intervals do not include source/model uncertainty. The wide recent Tehran rainfall interval remains essential context; a negative point estimate does not establish permanent reversal.

No new aggregation or trend-calculation defect was demonstrated in this review. This is a bounded result, not a claim that all science is validated or all bugs have been excluded.

## Primary-source comparison

The current official challenge summary accepts Earth-science mission or model variables and asks for change over time, location, rate and significance. A fresh official-page search recovered that summary; direct full-page retrieval returned 502 during this audit. The earlier production-page requirement extraction remains in the repository. No staging page or another competitor's claims were used as authority. [Official challenge](https://www.spaceappschallenge.org/2026/challenges/earth-system-trend-detective/).

KNMI's own service description documents existing multi-source climate time series, trend significance, visualization and downloads. NASA's Giovanni guide documents variable/date/region selection, time series and accessible provenance. Therefore these basic capabilities are not novel to this application. [KNMI Climate Explorer](https://climexp.knmi.nl/start.cgi), [NASA Giovanni User Guide](https://giovanni.gsfc.nasa.gov/giovanni/doc/UsersManualworkingdocument.docx.html).

Yosef, Aguilar and Alpert's primary study explicitly calculates trend matrices to examine sensitivity to period length (section 3 and Figure 6). This confirms a specific precedent for the start/end display, without implying that the present implementation copied its code or uses its different climate indices and methods. [Author-hosted paper](https://www.tau.ac.il/~pinhas/papers/2020/Yosef_et_al_IJC_2020.pdf), [doi:10.1002/joc.6740](https://doi.org/10.1002/joc.6740). The atlas protocol now cites this precedent directly.

## Verification actually performed

- Read the folder instructions, root overview, competition preparation and source records, current project README/research, official requirements, innovation review, science studies, statistical implementation, replay and atlas interpretation.
- Ran the four adversarial ordinary-replay probes described above against the initially reviewed implementation. All four were accepted. No NASA observations were changed.
- Reran the 12-test atlas suite: all passed in 11.538 seconds. It includes full offline reconstruction/replay of all 666 Tehran rainfall windows, independent numerical references, malformed/cross-case records, missing-year behavior and exact enumeration.
- Consulted the primary sources linked above. No user results, station comparisons, organizer decision, human listening or official scores were invented.

No runtime, release tag, public media or source observations were changed by this reviewer. Documentation changes are the specific matrix citation and this audit record. Engineering fixes and their final test outcomes belong in the release verification record.
