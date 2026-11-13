# Demo artifact status

The finished [seven-page PDF demonstration](climate-explorer-demo.pdf) uses actual retained project data. It is a PDF fallback, not a native Spaces presentation or editable PPTX. The public link must be checked after publication.

The Spaces presentation service created an empty Page on 13 November, then rejected the first cover edit with `artifact_preparation_failed`. It reported that no edit was saved and the failure was not retryable. A read-only inspection failed for the same reason. The empty Page is not a finished demo and must not be used as the submission link.

The local Artifact Tool fallback was also unavailable: the dependency-loader tool was not exposed and the required package was not installed in the available runtime. No substitute package was installed. No finished slide count, render review, or export is claimed for that attempt.

The PDF has seven 16:9 pages at 1280 by 720 points. Every page was rendered with MuPDF and visually inspected. It contains the actual Tehran annual series and intervals, synthetic-study false-positive rates, the Toronto spatial diagnostic, replay information, public project links and visible AI disclosures. The cover and conclusion retain the early-work and AI-ideation eligibility concerns. It contains no person's photograph, voice or name, and no invented application screenshot.

## Rebuild

Use a separate tools environment so PDF dependencies do not change the application lock:

```sh
python3 -m venv .demo-venv
.demo-venv/bin/python -m pip install -r submission/requirements-demo.txt
.demo-venv/bin/python submission/build_demo_pdf.py
```

The source reads retained analysis and evaluation JSON. It does not retrieve new NASA data. The PDF is not a screenshot of the latest live application. Its Tehran source is the retained example named in the captions. The replay claim was checked with `evaluation/replay.py` against that exact file.

PDF authoring used the PDF skill because both permitted presentation runtimes failed. A service failure does not establish public access to the empty Spaces Page. Do not publish or cite that Page as the demo.

Record the release commit and verify the final public PDF URL after publishing. The prepared URL is `https://armandamirchilou.github.io/climate-explorer/climate-explorer-demo.pdf`; it becomes valid only after the site build includes the file.
