# Independent deployment

Canonical application: https://climate-explorer-evidence.techtrendmedia-ai.chatgpt.site/

Source and development history: https://github.com/ArmanDamirchilou/climate-explorer

Climate Explorer has its own public GitHub repository. The earlier address under `armandamirchilou.github.io/climate-explorer/` was that repository's GitHub Pages deployment, not a modification of the personal-site repository. GitHub's API showed the separate `ArmanDamirchilou/armandamirchilou.github.io` repository was last pushed on 9 October 2026. The producer did not modify that repository during this project.

At the student's request, the public application now uses a separate Sites host and origin. The GitHub workflow checks the source and packages a frozen build; it no longer publishes to GitHub Pages. Personal-site hosting, source and settings are outside this deployment.

## Publication contract

1. Run the appropriate tests and `build_demo.py --output dist` from this repository. The build verifies retained NASA records and reviewed media; no NASA network request is required.
2. Copy the exact verified `dist/` into the dedicated hosting checkout. Verify every file against `build-manifest.json` before copying. Copy `hosting-headers.txt` to the mirror as `dist/_headers`; this host configuration is not a public asset. The deployment checkout contains only public build files, its hosting manifest, and `UPSTREAM.json` identifying this repository's exact release, source commit and code fingerprint.
3. Use the Sites source helper to commit, push and package that checkout. Deploy the matching saved version. Its hosting commit is a mirror commit, not a replacement for the GitHub development history.
4. Run `evaluation/verify_public.py` against the returned public URL. This checks anonymous access, the complete published manifest, reviewed media, forty fixed analyses, two guided records and all 6,660 atlas cells.

The Sites project identity is retained in the hosting checkout's `.openai/hosting.json`. Tokens are passed through process input and are not stored in either source repository. No application login, NASA credential, user account database or private student notes are deployed. Optional browser notes are local to an origin; changing hosts does not migrate those notes automatically. Download an investigation from an open old tab before closing it if you need to retain notes.

## Entry links

- Final project overview: `/review.html`
- Application: `/`
- Short demonstration candidate only: `/demo-short.html`, or `/climate-explorer-demo.mp4`
- Separate technical portfolio film: `/demo.html#technical-film`

The short and long films are unchanged reviewed artifacts. A new host does not alter their production version, authorship or eligibility. No competition form is submitted by deployment. Historical release documents retain their original addresses as historical records; use this page and the current project description for final outward links.

The host configuration requests `Cache-Control: no-transform` so scientific pages retain the build's exact HTML bytes for integrity verification. Cloudflare documents [custom static headers](https://developers.cloudflare.com/workers/static-assets/headers/) and [JavaScript injection behavior](https://developers.cloudflare.com/cloudflare-challenges/challenge-types/javascript-detections/). The verifier does not strip scripts or relax scientific/media checks to accommodate a transformed page.
