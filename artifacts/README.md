# Climate Explorer saved artifacts

Historical browser export from 12 November: `climate-explorer-analysis-v021-browser.json`. It passed offline replay and contains the frozen raw NASA response, settings, source hash, and code fingerprint. Current release verification is recorded in evaluation/RELEASE_VERIFICATION.md.

The Tehran temperature, Tehran rainfall, Toronto temperature, and ten-year rainfall JSON files named `v02` were regenerated with version 0.2.1 and also passed replay. Their internal version is authoritative.

`baseline-2026-11-11.zip` is retained unchanged locally. It is excluded from the public repository because its original README includes a local account path. `baseline-manifest.json` retains its original hash. This omission does not change the original build date. `climate-explorer-analysis.json` and `climate-explorer-chart.svg` are original Berlin examples from that prototype.

`climate-explorer-analysis-v020-browser-known-hash-bug.json` preserves the export that exposed the JavaScript numeric-formatting hash bug. It is a regression record, not a current reusable result. Use the version 0.2.1 export instead.

None of these files is an event submission or evidence of competition eligibility.
