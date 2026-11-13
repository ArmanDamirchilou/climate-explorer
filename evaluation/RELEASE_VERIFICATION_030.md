# Climate Explorer 0.3.0 release verification

Verified 13 November 2026, around 10:45 Tehran time (UTC+3:30). This release completes the shareable software prototype and its preparation materials. It does not establish competition eligibility, an award, station-level validity, or measured educational impact.

Runtime source was checked at commit `4a8ebd11f76b99e7d52efa09ab33d084e61db155`. The `v0.3.0` release includes this record and documentation updates. The exported source fingerprint is `f089606669534a1bf723627c0db2ade602c2b9a5c5a48ce3c22915b46d379f03`; its input file list is included in each analysis. Documentation-only additions do not change this fingerprint.

## Observed checks

| Check | Result |
|---|---|
| Numerical, HTTP, replay and build tests | 54 tests passed locally, with no skips |
| Linux execution | GitHub Actions installed the locked binary dependencies, ran the 54 tests, checked JavaScript, built and deployed successfully |
| Clean environment | Engineering reviewer independently installed the exact lock and passed the then-current 53-test suite in a fresh macOS environment; a later worksheet regression brings the release suite to 54 |
| Dependencies | `pip check` passed; Python 3.14 is the supported runtime |
| Frozen public build | Ten complete analyses generated from retained NASA responses; source endpoints, coordinates, periods and recorded hashes checked before analysis |
| Build isolation | Tests block network connections and confirm all ten analyses replay without fetching NASA data |
| Public integrity | 21 public files match the deployed manifest; hidden build metadata is intentionally excluded because GitHub Pages does not serve it |
| Public numerical replay | All ten deployed analyses replay, 45 annual values each; deployed code fingerprints match the local release source |
| Local HTTP analysis | Current Tehran temperature response replays, retains actual source metadata, and matches the release fingerprint |
| Actual browser worksheet | Chrome downloaded `artifacts/climate-explorer-investigation-v030-browser.json`; nested analysis replays and source comparison and entered QA notes are preserved. It records the earlier 0.3.0 build used during that browser check |
| Browser access | Incognito Chrome opened the public app, precipitation case, evaluation page, spatial audit, and seven-page PDF without login |
| Layout | Narrow native Chrome window and maximized desktop inspected. The first-cycle 400-pixel inspection remains in the historical verification record |
| PDF | Seven 16:9 pages; all rendered and visually reviewed; actual data, metric checks, text bounds and source hashes recorded in `submission/demo-verification.json` |
| Privacy and repository scope | Only the project is published. Environment files, caches, render scratch files and unrelated competition-planning documents are excluded. Original local baseline archive remains unchanged and unpublished because it contains a local account path |
| Authorship and rules | Actual 11 November start date and substantial Codex ideation/code/documentation contribution preserved; no personal contribution or organizer approval invented |

Successful Linux build and deployment: [GitHub Actions run](https://github.com/ArmanDamirchilou/climate-explorer/actions/runs/43383883631). Machine-readable anonymous public checks: [public-verification-030.json](public-verification-030.json). The earlier implementation cycle remains in [VERIFICATION.md](VERIFICATION.md).

## Findings fixed during this release

CSV previously fetched a new result instead of saving the displayed one. It now uses the displayed immutable analysis. Damaged saved evaluation reports now return structured errors. The launcher selects Python 3.14. Public asset and report links work beneath the repository subpath. The frozen builder refuses unexpected source hashes, queries and output directories.

The first workflow did not parse because its binary-wheel command contained a colon followed by a space in an unquoted YAML scalar. It was changed to a block scalar, parsed locally and successfully executed on GitHub. The first public-integrity check also attempted to fetch two hidden build metadata files that Pages does not serve. They were removed from the public asset manifest, and the complete anonymous check then passed. These failures were not recorded as successful runs.

## Scientific and product limits

The synthetic study retains all eight configurations and ten scenarios. No deployable uncertainty candidate passed every screening case. The app shows conditional comparisons and does not promise calibrated real-world significance. Source checks have different spatial supports. The Toronto diagnostic checks aggregation and nearby points, without selecting a physical cause or a source as truth. Precipitation has no second-source validation.

The proposed educational benefit still requires actual student or teacher observations. No usability participant, testimonial or feedback result has been simulated. The student must learn the calculations and describe their actual contributions.

## Competition entry remains separate

The full official challenge, submission guide, judging guide and Ankara schedule were recovered and mapped in [requirements](../submission/REQUIREMENTS.md). The recorded early work and AI role create two unresolved eligibility concerns. Team/challenge selection, age/guardian requirements and local virtual delivery still need personal or organizer checks. No competition submission, registration, account creation, payment or organizer communication was performed in this release.

## Repeat verification

```sh
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m pip check
node --check static/app.js
node --check static/validation.js
.venv/bin/python build_demo.py --output dist
.venv/bin/python evaluation/replay.py artifacts/tehran-temperature-v030-http.json
.venv/bin/python evaluation/verify_public.py
```

The public check uses anonymous HTTP. It verifies deployed bytes and recalculates the frozen analyses locally; it does not replace browser checks or organizer decisions.
