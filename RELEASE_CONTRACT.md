# Version 1.0 software contract

Version 1.0 marks a complete reviewable investigation workflow and its first documented compatibility contract. It does not claim production certification, calibrated inference for every climate record, measured educational impact or competition eligibility.

## Supported workflow

Select temperature or precipitation and a preset or custom coordinate. Choose at least ten complete calendar years in the full Python app. The public demo offers five frozen presets and four fixed periods ending in 2025. Inspect annual values, conditional uncertainty, date sensitivity, source provenance and the monthly view. Add notes, then download the exact displayed evidence. Reopen the file in the browser or run the complete Python replay.

Optional browser storage keeps the latest investigation on this device. It is off on page load, requires explicit activation and can be cleared. There is no user account, note upload or cloud synchronization. The public demo still needs a server to load local files. The handoff archive includes a static-server command.

## Compatibility

The worksheet envelope is `Climate Explorer investigation 1`. Its `analysis` property retains the existing analysis JSON. New optional fields may be added within 1.x. Breaking required-field or meaning changes require a new envelope identifier. Unknown worksheet notes are not interpreted as commands. Untrusted imports are limited to 2 MiB and validated before rendering.

The browser accepts the supported NASA POWER export layout from application 0.2.1 onward. It checks the recorded hash, calendar aggregation and point estimates. It does not recompute uncertainty intervals, p-values, residual correlation or bands. `evaluation/replay.py` checks the recorded supported settings, raw response, annual/monthly values, trend and sensitivity output. Future unsupported method versions must be handled explicitly rather than silently relabelled.

App release and method settings have separate versions. App 1.0.0 retains method settings 0.2.1 because this release improves the workflow rather than silently replacing the statistical method. Exported source fingerprints identify a source snapshot, not a cryptographic signature, NASA authentication or peer review.

## Release gates

The scientific fixtures, HTTP behavior, frozen build and browser-import regression suite must pass. All forty public analyses must replay from retained source responses. Public files must match their manifest. JavaScript syntax and locked dependency checks must pass. Media must remain within the current published limits and accurately disclose assistance. New UI behavior must be inspected in a real browser. Package and release notes must preserve known limits and actual work dates.

The GitHub history, changelog and release tags preserve how each published version changed. Earlier local milestones are described as local milestones. AI commit co-author trailers are omitted at the student's request, while the assistance record remains public.

## Remaining evidence

The existing source comparison uses different spatial supports. Toronto's cause remains unresolved. Precipitation has no second-source validation. A suitable station comparison and real student/teacher observations are follow-up work. Technical checks cannot settle the organizer's early-work and AI-ideation rules or confirm personal registration requirements.
