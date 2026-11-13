# Contributing

Use Python 3.14 and Node.js 24. Create a virtual environment and install `requirements-lock.txt`. The application has no JavaScript dependency installation step.

```sh
python3.14 -m venv .venv
.venv/bin/python -m pip install --only-binary=:all: -r requirements-lock.txt
.venv/bin/python -m pip check
.venv/bin/python -m unittest discover -s tests -v
for script in static/*.js; do node --check "$script" || exit; done
```

The HTTP tests start an isolated server on an operating-system-assigned local port. They use the retained NASA snapshot and mocks. They do not need a live NASA connection. Node.js is required to run the browser JSON round-trip regression check; without it, that test explicitly skips. CI installs Node so it does not skip.

Before changing a calculation, describe the question and assumptions it estimates. Add an independent numerical reference or a known failure case. A test that repeats the production formula does not establish that the formula is scientifically suitable.

Keep NASA source responses unchanged. Preserve request URLs, retrieval dates, units, missing-value rules, and source hashes. Record method changes in the research notes. Do not replace a saved result because a new method gives a more appealing answer. A changed period answers a different question.

Restart the local server after changing application source. Its export fingerprint is computed at startup. Download and replay a fresh JSON result after changes to calculations or serialization:

```sh
.venv/bin/python evaluation/replay.py /path/to/climate-explorer-analysis.json
```

Check the interface in a browser at desktop and narrow mobile sizes when presentation changes. Verify labels, units, keyboard controls, error messages, and exported results. Passing Python tests does not verify browser behavior.

Keep code comments for assumptions or decisions that the code cannot make clear. Prefer small functions and descriptive names over comments that repeat the next line.

Document AI assistance and the work a human actually reviewed. Do not claim that an AI-assisted implementation was independently written by the student. Preserve the real build start date of 11 November 2026. Eligibility, registration, and final submission must be resolved separately from code quality.

The Python server is intended for local use and binds to `127.0.0.1`. Do not expose it as a production web service. The public demonstration is a separately built, frozen-data site. It does not provide unrestricted live coordinate queries.
