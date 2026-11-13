# Climate Explorer improvement plan

Started 11 November 2026; first iteration verified 12 November; release work continued on 13 November. Owner of research and implementation: Codex, working for the student. The student owns personal explanations, user feedback, and any final submission. This is an early prototype with unresolved competition eligibility.

The aim is a useful, scientifically honest investigation tool that a student can explain and another person can reproduce. Winning is an outcome we cannot control. We can control the quality of the question, evidence, implementation, and explanation.

## Working product question

Can a student tell whether an apparent local climate trend survives reasonable changes in statistical assumptions and the selected period?

The proposed audience is secondary-school students and their teachers. This is a hypothesis until tested with real users. The tool supports an evidence-based school investigation. It does not advise farmers, predict drought, measure street-level heat, or prove why climate changed.

## Stages and completion checks

| Stage | Work | Completion check | Status |
|---|---|---|---|
| 1. Establish the requirements | Read the full challenge and current judging guide. Map every requirement to a feature or piece of evidence. Separate local and global requirements. | Exact official requirements have source links and no invented weights. Unavailable requirements remain open. | Core challenge, submission guide, judging guide, and Ankara schedule recovered and mapped on 13 November in submission/REQUIREMENTS.md. Eligibility, personal account details, and online delivery process remain open. |
| 2. Audit the prototype and alternatives | Review data suitability, existing NASA tools, statistical assumptions, architecture, and exports. Compare plausible approaches before selecting one. | Research and decisions explain benefits, costs, and limitations. Critical weaknesses are ranked. | First review complete in RESEARCH.md; revise when full requirements arrive |
| 3. Evaluate methods | Use fixed synthetic experiments with known trends, independent and correlated errors, outliers, and changing variability. Compare uncertainty coverage, false positives, slope error, and cost. | Save the generator, seed, protocol, results, and failures. Never choose a method because it gives a more impressive Tehran result. | Fixed study complete: 20,000 records, eight configurations; no deployable universal interval passed |
| 4. Improve one complete investigation | Add the checks justified by the evaluation. Keep a simple default and show disagreement. Include provenance and correct spatial scale. | Real NASA data, exports, and UI tell the same story. Method changes do not silently change the question. | Professional release includes network-free build, HTTP tests, frozen public demonstration, source checks and worksheet export. Current evidence is in evaluation/RELEASE_VERIFICATION.md; historical verification remains in evaluation/VERIFICATION.md. |
| 5. Validate with people and independent data | Run a brief task with three students or teachers. Compare selected results with a suitable independent dataset over matched periods and scales. | Record actual feedback, task completion, and mismatches. No simulated participants or invented endorsements. | Five-location GISTEMP consistency check complete at different spatial scales. A fixed Toronto diagnostic checks all 45 annual values and nearby locations; spatial sensitivity is substantial and its cause remains unresolved. User study pending. |
| 6. Prepare an honest demonstration | Explain the problem, alternatives, selected method, evidence, limitations, and next improvement. Practice answering questions about the calculations. | The student can explain the core calculation and one failure case without reading a script. Required submission media follow the actual guide. | Learning guide, form drafts, judge questions and seven-slide content prepared. Official media limits verified. Public PDF demo prepared separately; student explanation and organizer decisions remain open. |

Stages can be revised when evidence changes. A stage is not complete because its code runs. Requirements that cannot be checked must not be presented as confirmed.

## Priorities

1. Prevent misleading certainty. The current independent-error interval can be too narrow for correlated years.
2. Make results reproducible. Freeze data and record method versions and all parameters.
3. Explain method and period sensitivity in plain language.
4. Validate the intended benefit with students before making impact claims.
5. Improve presentation around the demonstrated benefit.

Keep the existing public POWER endpoint and small local architecture unless a requirement shows they are insufficient. Defer a chatbot, neural forecasting, a global map, accounts, and extra dashboards. Each adds work without yet answering the product question.

## Release checks

- Calculations agree with a separate reference implementation on fixed fixtures.
- Synthetic evaluation reports both successes and failures, including uncertainty that misses its advertised coverage.
- Incomplete years are not imputed or treated as adjacent calendar years.
- Raw data, units, source dates, code version, and analysis settings travel with the result.
- Mobile and desktop layouts are inspected after changes. Controls work with a keyboard.
- No claim that agreement between two methods establishes truth or removes dataset bias.
- Early-work and AI-ideation eligibility, guardian requirements, and online local delivery instructions are resolved before treating this as an eligible entry. The user handles registration and submission.

## Current deliverables

Research decisions: `RESEARCH.md`. Evaluation protocol and results: `evaluation/`. Current implementation and run instructions: `README.md`.

Ankara published schedule rechecked on 13 November: local start Saturday 14 November at 09:45 Tehran; local delivery Sunday 15 November at 17:30 Tehran. Our target is 16:30. See submission/REQUIREMENTS.md for the current source record and unresolved online delivery process. The first code was written on 11 November and must never be described as work first created during the event.

## Release completion and remaining human decisions

The software milestone is a reproducible, publicly inspectable prototype with evidence and submission preparation. It is complete when the release checks and public deployment pass. A winning competition result is not a software acceptance test.

The three specialist AI reviews are documented in AI_ASSISTANCE.md. Their science, engineering and submission findings informed the current release. They are not human peer reviewers or NASA judges.

The project began before the event, and AI helped supply the approach. Those historical facts cannot be fixed by more code. An organizer must decide how the rules apply. The student must complete any required guardian/team checks, practice the explanation, and provide real usability observations before those claims can be made. No AI-generated testimony or user feedback can close those checks.
