# GitHub Pages deployment

Canonical application: https://armandamirchilou.github.io/climate-explorer/

Dedicated source repository and development history: https://github.com/ArmanDamirchilou/climate-explorer

Climate Explorer is published only through the dedicated project's GitHub Pages site. The `/climate-explorer/` path belongs to that repository's Pages deployment. It does not require changing the separate personal-site repository, `ArmanDamirchilou/armandamirchilou.github.io`, which this project has not modified.

## Publication contract

1. Push reviewed source to this dedicated repository. The pinned GitHub Actions workflow installs locked dependencies, runs tests and JavaScript syntax checks, and builds the frozen demonstration.
2. The build uses retained NASA records and reviewed media. It makes no live NASA request. Main-branch checks upload the generated `dist/` as a Pages artifact; the dependent deployment job publishes that artifact. Pull requests run checks without publishing.
3. Run `evaluation/verify_public.py` against the canonical GitHub Pages URL after deployment. It checks ordinary anonymous HTTP responses against the build manifest and replays forty fixed analyses, two guided records and all 6,660 atlas cells. No special XHR representation, script stripping or hash normalization is used.
4. Retain the release, verification record and checksummed handoff archive. A hosted page can change later; downloaded investigations preserve their recorded evidence.

No NASA credential, student account database or private notes are deployed. Optional saved browser notes belong to the browser origin. Download an investigation from an old open tab if you need to preserve notes before changing hosts.

## Entry links

- Project overview: https://armandamirchilou.github.io/climate-explorer/review.html
- Application: https://armandamirchilou.github.io/climate-explorer/
- Short demonstration candidate: https://armandamirchilou.github.io/climate-explorer/demo-short.html
- Separate technical portfolio film: https://armandamirchilou.github.io/climate-explorer/demo.html#technical-film

An alternative Sites deployment was briefly prepared during the hosting review. The student explicitly selected GitHub-only publication. Current entry links and deployment instructions therefore use GitHub Pages. Historical audit and assistance records preserve actions that actually occurred; this document does not claim that an external copy has been deleted or made private.

The current anonymous GitHub verification checks79 public files, forty fixed analyses, two guided records and all6,660 atlas cells. See evaluation/RELEASE_VERIFICATION.md for the tested commit, source fingerprint, completed Pages run and verification scope.
