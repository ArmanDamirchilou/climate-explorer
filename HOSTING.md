# Independent deployment

Canonical application: https://climate-explorer-evidence.techtrendmedia-ai.chatgpt.site/

Source and development history: https://github.com/ArmanDamirchilou/climate-explorer

Climate Explorer has its own public GitHub repository. The earlier address under `armandamirchilou.github.io/climate-explorer/` was that repository's GitHub Pages deployment, not a modification of the personal-site repository. GitHub's API showed the separate `ArmanDamirchilou/armandamirchilou.github.io` repository was last pushed on 9 October 2026. The producer did not modify that repository during this project.

At the student's request, the public application now uses a separate Sites host and origin. The GitHub workflow checks the source and packages a frozen build; it no longer publishes to GitHub Pages. Personal-site hosting, source and settings are outside this deployment.

## Publication contract

1. Run the appropriate tests and `build_demo.py --output dist` from this repository. The build verifies retained NASA records and reviewed media; no NASA network request is required.
2. Copy the exact verified `dist/` into the dedicated hosting checkout. Verify every file against `build-manifest.json` before copying. The deployment checkout contains only public build files, its hosting manifest, and `UPSTREAM.json` identifying this repository's exact release, source commit and code fingerprint.
3. Use the Sites source helper to commit, push and package that checkout. Deploy the matching saved version. Its hosting commit is a mirror commit, not a replacement for the GitHub development history.
4. Run `evaluation/verify_public.py` against the returned public URL. This checks anonymous access, the complete published manifest, reviewed media, forty fixed analyses, two guided records and all 6,660 atlas cells.

The Sites project identity is retained in the hosting checkout's `.openai/hosting.json`. Tokens are passed through process input and are not stored in either source repository. No application login, NASA credential, user account database or private student notes are deployed. Optional browser notes are local to an origin; changing hosts does not migrate those notes automatically. Download an investigation from an open old tab before closing it if you need to retain notes.

## Entry links

- Final project overview: `/review.html`
- Application: `/`
- Short demonstration candidate only: `/demo-short.html`, or `/climate-explorer-demo.mp4`
- Separate technical portfolio film: `/demo.html#technical-film`

The short and long films retain the same narration, scientific figures and caption timing. Release 1.3.1 corrects visible distribution-link panels to the stable dedicated repository. The seven-page PDF updates its app link and atlas explanation. Previous bytes remain in earlier tags; a new host does not change authorship or eligibility. No competition form is submitted by deployment. Historical release documents retain their original addresses as historical records; use this page and the current project description for final outward links.

The static host injects its own Cloudflare detection script into navigation HTML. Its static delivery path did not apply the tested `_headers` no-transform request, so that unused configuration was removed. The verifier requests the anonymous XHR asset representation with `X-Requested-With: XMLHttpRequest` and `Accept: application/octet-stream`; this returns the original HTML asset. It checks every returned byte against the same manifest, without stripping scripts or normalizing hashes. NASA JSON, app scripts, media and captions retain strict hash checks. Actual browser navigation is inspected separately and may include the provider's extra script. This is a hosting transformation, not a generated application script or an authenticity guarantee. Cloudflare describes its [HTML-versus-AJAX injection behavior](https://developers.cloudflare.com/cloudflare-challenges/challenge-types/javascript-detections/).
