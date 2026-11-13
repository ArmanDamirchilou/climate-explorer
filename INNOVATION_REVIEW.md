# Climate Explorer innovation review

Prepared 13 November 2026 by the Codex submission specialist. These are design judgments and proposed experiments, not NASA scores, tested educational outcomes, or a claim that the student independently developed these ideas. The public 1.2 release is the baseline. The next selected enhancement is a complete date-window sensitivity atlas, subject to science and engineering verification.

## The decision

Develop one deeper investigation: make the effect of selecting dates visible across a declared universe of windows, then let a reader reproduce a chosen result. Keep the historical-rate question, existing source, simple line and explicit limitations. This follows the strongest existing demonstration: one Tehran rainfall record gives a positive full-period slope and a negative recent-period point estimate whose ordinary interval includes zero.

The request to think through thousands of possibilities is a request for breadth and judgment. It should not produce a thousand untested features or a claim that a thousand methods were evaluated. This review records **100 distinct candidates**, including competing approaches, validation work, teaching activities and release tasks. Scores prioritize investigation; they do not establish merit empirically. A finite, documented search with reasons for rejection is more reviewable than an inflated idea count.

## Research and reasoning

NASA's systems-engineering decision process asks for a defined decision, criteria, alternatives, evaluation, limitations and a documented recommendation. Its effort should fit the decision's consequences. We apply this as a small trade study, not as a claim that this prototype meets NASA engineering certification. [NASA, Decision Analysis](https://www.nasa.gov/reference/6-8-decision-analysis/), read 13 November.

Design Council describes exploring a problem and possible answers before narrowing and testing small solutions. That argues for investigating a student's actual difficulty before adding a platform. Its people-centered requirement is not yet satisfied by real student observations here. [Framework for Innovation](https://www.designcouncil.org.uk/resources/framework-for-innovation/), read 13 November.

Stanford d.school separates broad idea generation from selection and uses inexpensive prototypes to learn from users. We therefore list competing concepts before choosing, and preserve ideas that need human feedback rather than inventing that feedback. [Design Thinking Bootleg](https://dschool.stanford.edu/tools/design-thinking-bootleg), ideation and prototype cards in its linked 2018 PDF, read 13 November.

The Space Apps guide's five criteria are Impact, Creativity, Validity, Relevance and Presentation, each scored 1–5. Our internal scores below are a different planning tool. The official guide supplies no probability of winning. Public media have a 30-second video or seven-slide limit; the proposed 135-second technical film is a separate portfolio explanation. [Judging guide](https://www.spaceappschallenge.org/resources/judging-awards-guide/), [submission guide](https://www.spaceappschallenge.org/resources/project-submission-guide/). The retained full-page retrieval and root agent's Chrome review on 13 November support these facts. This review's new web requests returned 502/403, so they are not represented as another successful full read. See [requirements and source record](submission/REQUIREMENTS.md).

## Mandatory gates before scoring

An idea cannot ship if it fabricates observations or impact, hides selection, implies unsupported causal attribution or disaster consequences, misstates ownership, exposes a minor's likeness in the submission, or silently changes the source. Do not promise first place, invent approval, imply NASA endorsement through uniforms or branding, or count cosmetic names and redundant tests as evaluated innovation. Paid services require an actual quote and bounded generation plan. A polished film cannot close competition eligibility: work began 11 November, and AI helped develop the solution approach. Real student explanation, user feedback, guardian/team checks and an organizer's decision remain human tasks.

## Shortlist and trade study

| Approach | Benefit for the current question | Main cost or failure | Decision |
|---|---|---|---|
| Preserve four fixed end-2025 periods only | Simple, comprehensible baseline | Does not show all other start/end choices | Keep baseline alongside atlas |
| Free date slider alone | Direct exploration | Can hide selective reporting and omit unchosen dates | Do not make this the main evidence |
| Search for the largest slope or smallest p-value | Visually dramatic | Rewards selection and produces an unjustified winner | Reject |
| Complete contiguous-window atlas | Reveals dependence on both endpoints and retains the universe | Overlapping windows are dependent; color can invite cherry-picking | Select with explicit safeguards |
| Neural forecasting | Could address a different future-prediction task | Requires new targets, holdouts, baselines and claims | Defer |
| Chatbot answering climate claims | Flexible interface | Grounding, explanation and privacy burden without validated need | Defer |
| Independent precipitation comparison | Could reveal dataset disagreement | Matched grids/versions and access need separate work | Next scientific study, not a rushed merge |
| Student task comparison | Direct evidence about educational benefit | Requires real people, consent and honest observations | Highest human validation priority |

The selected atlas can be useful without claiming to invent trend matrices. Its proposed distinction is the joined workflow: full window universe, visible selection caveat, same source, exact selected-period opening, and replayable evidence for a learner. Originality across all tools is unproven. The official challenge links the existing KNMI Climate Explorer; this project is independent.

## Atlas contract and acceptance

Use the same retained monthly source. Enumerate contiguous requested calendar windows. A window is eligible when it contains at least the declared minimum of complete annual observations. Incomplete years remain excluded inside the window; requested endpoints and observed coverage must be distinguished. Withhold HAC checks when gaps violate the implementation's calendar-spacing requirement. This contract does not restrict the universe to uninterrupted complete-year runs. A complete 45-year record has `(45 - 10 + 1) × (45 - 10 + 2) / 2 = 666` candidate windows. Actual counts must be derived from the supplied record, not hard-coded as universal.

The heatmap uses start year and end year, a fixed diverging slope scale and explicit units. Invalid cells remain uncolored. Retain an accessible chronological table and complete export. Display-only length/direction filters must show both visible and full-universe counts. No significance filter, ranking, best-window button or percentage interpreted as a probability. Overlap makes the windows dependent. A ten-year minimum is a product exploration boundary, not a guarantee of sufficient climate evidence.

Opening one cell must use the exact retained source and dates, preserve notes, and show its ordinary/Newey-West assumptions, point comparisons and source metadata in the full analysis. The atlas is descriptive sensitivity, not a corrected hypothesis-testing procedure. A negative window does not establish reversal; an interval excluding zero after browsing is not a selection-adjusted discovery. Export the declared minimum, enumeration rule, source hash, method/version and all windows, even when a filter is active. Distinguish browser checks from full Python replay.

Before release: independent enumeration and point calculations; missing-year fixtures; exact first/last dates; same-hash verification; invalid-cell keyboard handling; filters not changing the underlying universe; complete export and replay tests; mobile/keyboard review; and a plain-language selection warning beside the plot. Report actual test results in the release record. This document does not predeclare them passed.

## How the 100 candidates are scored

Each row has **V/E/F/C** on a 1–5 ordinal scale: value for the investigation, ability to verify with evidence, feasibility in this iteration, and clarity for the intended learner. Five is favorable. The sum is out of 20. Scores are specialist estimates, with no measurement or invented precision. Equal totals are not a ranking. A lower score can still be valuable later.

Triage: **Now** = selected next work or release gate; **Keep** = preserve and improve an existing capability; **Human** = depends on an actual person; **Study** = prototype or evaluate before commitment; **Later** = plausible but outside this release; **Reject** = violates the present question or a mandatory gate. These labels are recommendations, not implementation status. Validate each proposed outcome before promotion.

### Date selection and scientific reasoning

| ID | Specific candidate and the evidence that would justify it | V/E/F/C | Total | Triage |
|---|---|---|---|---|
| 01 | Enumerate every contiguous ≥10-year period from the frozen record; independent enumeration must match the exact universe. | 5/5/4/4 | 18 | Now |
| 02 | Plot start against end year with one slope color scale; readers must identify the full and recent periods correctly. | 5/4/4/4 | 17 | Now |
| 03 | Put a persistent overlap/selection warning next to the atlas; task review must show it is noticed before a claim is written. | 5/4/5/5 | 19 | Now |
| 04 | Offer a chronological table with the same cells for keyboard and screen-reader use; values must equal the heatmap payload. | 5/5/4/4 | 18 | Now |
| 05 | Open a selected window in the existing investigation while retaining the raw hash and notes; round trip must preserve both. | 5/5/4/5 | 19 | Now |
| 06 | Keep a full-universe count beside display-only filters; filtering must never replace the saved universe. | 5/5/5/4 | 19 | Now |
| 07 | Let a learner record a date-choice reason before seeing its result; evaluate whether this reduces result-led explanations. | 5/3/3/4 | 15 | Study |
| 08 | Compare windows of equal duration in a separate view; verify that only endpoints, not length, differ. | 4/5/3/4 | 16 | Later |
| 09 | Mark the four existing fixed periods on the atlas; selected cells must match previously released results. | 4/5/4/5 | 18 | Now |
| 10 | Freeze a dated analysis plan before revealing each result, then retain later deviations; evaluate whether readers distinguish planned and exploratory claims. | 5/4/3/4 | 16 | Study |

### Estimation and uncertainty

| ID | Specific candidate and the evidence that would justify it | V/E/F/C | Total | Triage |
|---|---|---|---|---|
| 11 | Show OLS rate with units and dates before uncertainty; a learner must explain what one decade changes in the fitted line. | 5/5/5/5 | 20 | Keep |
| 12 | Keep Newey-West alongside OLS with its lag disclosed; calculations must match the reference implementation. | 5/5/5/3 | 18 | Keep |
| 13 | Keep Theil-Sen as an outlier-sensitive slope comparison, without claiming dependence correction; verify point fixtures. | 4/5/5/4 | 18 | Keep |
| 14 | Show leave-one-year-out spread beside the original slope; verify all omitted-year values, including an extreme endpoint. | 4/5/5/4 | 18 | Keep |
| 15 | Prototype moving-block bootstrap intervals at several fixed block lengths; predeclare coverage scenarios before viewing real results. | 4/5/2/2 | 13 | Study |
| 16 | Compare GLSAR only after convergence and misspecification checks; refuse an automatic best-model label. | 3/4/2/2 | 11 | Study |
| 17 | Add a centered quadratic description with held-out comparison; establish whether curvature adds useful explanation rather than visual fit. | 3/4/2/2 | 11 | Later |
| 18 | Use a spline as the default trend; extra flexibility would blur the current single-rate question without demonstrated benefit. | 2/3/2/2 | 9 | Later |
| 19 | Show an uncertainty explainer using repeated synthetic intervals; learners must distinguish coverage from probability of a claim. | 5/4/3/5 | 17 | Study |
| 20 | Calibrate an atlas-wide null procedure for a future detection claim; jointly simulate the entire overlapping search, not independent cells. | 5/5/1/2 | 13 | Study |

### Source and spatial validity

| ID | Specific candidate and the evidence that would justify it | V/E/F/C | Total | Triage |
|---|---|---|---|---|
| 21 | Put native grid size beside each city label; readers must identify it as a grid estimate rather than a station. | 5/5/5/5 | 20 | Keep |
| 22 | Preserve a small coarse-grid diagram without claiming a precise footprint boundary; validate coordinates against source metadata. | 4/4/3/5 | 16 | Study |
| 23 | Compare neighboring POWER locations over identical dates; retain all requests and resist selecting the preferred neighbor. | 5/5/3/4 | 17 | Study |
| 24 | Extend the fixed Toronto spatial diagnostic to a predeclared second city; report disagreement before explaining its cause. | 5/5/2/3 | 15 | Study |
| 25 | Compare precipitation with CHIRPS over a matched period and footprint; verify product version, units and missing-data rules first. | 5/4/2/3 | 14 | Study |
| 26 | Compare temperature with GISTEMP over matched years while showing different smoothing; preserve existing disagreement evidence. | 5/5/5/4 | 19 | Keep |
| 27 | Add an in-situ Tehran station comparison if a legitimate complete series is available; document siting and quality flags. | 5/4/1/4 | 14 | Later |
| 28 | Show source retrieval time separately from analysis time; regenerated analysis must not imply newly fetched observations. | 4/5/5/5 | 19 | Keep |
| 29 | Add an explicit source-version comparison fixture when upstream data change; keep both payload hashes and quantify actual differences. | 4/5/3/3 | 15 | Later |
| 30 | Add seasonal rainfall summaries with separately declared seasons and units; check missing months and explain that this changes the estimand. | 4/5/2/3 | 14 | Study |

### Evidence and reproducibility

| ID | Specific candidate and the evidence that would justify it | V/E/F/C | Total | Triage |
|---|---|---|---|---|
| 31 | Export all atlas windows and enumeration settings with the source hash; filtered exports must retain the declared full universe. | 5/5/4/4 | 18 | Now |
| 32 | Extend strict Python replay to the atlas; intentionally edited dates, counts and slopes must be rejected. | 5/5/4/4 | 18 | Now |
| 33 | Distinguish browser point checks from Python uncertainty replay in every import result; deliberately changed intervals must not be called verified. | 5/5/5/5 | 20 | Keep |
| 34 | Include a short claim, rationale and limitation in saved investigation notes; reload must retain the exact text locally. | 4/5/5/5 | 19 | Keep |
| 35 | Provide a tiny command-line replay example with an expected fixture hash; an isolated environment must reproduce it. | 5/5/4/4 | 18 | Now |
| 36 | Bundle selected analysis, full atlas and a plain-language README into a downloadable evidence package; verify every internal link/hash. | 4/5/2/4 | 15 | Later |
| 37 | Document the export schema and backward-compatibility policy; fixture imports must survive a new app version or explain rejection. | 4/5/5/3 | 17 | Keep |
| 38 | Add a citation snippet containing source, dates, method and limitations; check it against the actual selected record. | 4/5/3/5 | 17 | Study |
| 39 | Export an atlas image with dates, units, source and selection warning inside the figure; shared screenshots must retain context. | 5/4/3/5 | 17 | Study |
| 40 | Provide a local archive-verification CLI that checks every evidence-package hash and schema without recomputing statistics; test deliberate corruption. | 4/5/3/4 | 16 | Later |

### Learning and real evaluation

| ID | Specific candidate and the evidence that would justify it | V/E/F/C | Total | Triage |
|---|---|---|---|---|
| 41 | Observe three real students comparing the two Tehran periods; record task errors and exact observations without invented quotes. | 5/5/2/5 | 17 | Human |
| 42 | Ask a teacher to review the explanation of mm/year per decade; revise only from recorded actual feedback. | 5/5/2/5 | 17 | Human |
| 43 | Test a before/after claim-writing task with a declared rubric; report sample size and convenience-sample limits. | 5/5/1/4 | 15 | Human |
| 44 | Compare the four-period view with the atlas on one fixed task; observe whether extra choice creates confusion. | 5/5/2/4 | 16 | Human |
| 45 | Add a teacher worksheet asking for claim, evidence and caveat; review whether a student can finish without assistance. | 4/4/4/5 | 17 | Study |
| 46 | Add a worked leap-year rain conversion exercise; numeric answer must agree with calendar-aware aggregation. | 4/5/4/5 | 18 | Study |
| 47 | Ask learners to predict slope direction before revealing the recent window; use actual answers rather than a fake success rate. | 4/4/3/5 | 16 | Human |
| 48 | Offer Persian definitions reviewed by a fluent science teacher; preserve exact English variable names and units. | 5/3/2/5 | 15 | Human |
| 49 | Let students compare a careful and an overstated headline about the same data; assess reasoning rather than completion clicks. | 5/4/3/5 | 17 | Study |
| 50 | Run a focused uncertainty-comprehension task comparing the interval explanation with the default chart; score misconceptions using a predeclared rubric. | 5/5/2/5 | 17 | Human |

### Interface and accessibility

| ID | Specific candidate and the evidence that would justify it | V/E/F/C | Total | Triage |
|---|---|---|---|---|
| 51 | Use a color-blind-safe diverging atlas palette with printed sign values in the table; inspect grayscale and common deficiency simulations. | 5/4/4/5 | 18 | Now |
| 52 | Make focused cells announce start, end, length, slope and source scope; test with an actual screen reader. | 5/5/3/5 | 18 | Human |
| 53 | Keep heatmap axes visible on narrow screens and offer table-first mode; inspect at 360 and 400 pixels. | 5/5/4/5 | 19 | Now |
| 54 | Show a selected-window outline and textual summary without relying on hover; keyboard selection must open the same result. | 5/5/4/5 | 19 | Now |
| 55 | Respect reduced-motion preferences in chart reveals; story content and values must remain accessible when animation stops. | 4/5/4/5 | 18 | Now |
| 56 | Make direct links include chosen preset, variable and view; signed-out reload must restore those exact settings. | 4/5/5/5 | 19 | Keep |
| 57 | Put analysis caveats in the printed worksheet, not only a tooltip; print preview must retain dates, source and full notes. | 5/5/5/5 | 20 | Keep |
| 58 | Add keyboard shortcuts only after a task shows repeated navigation burden; avoid overriding browser or assistive shortcuts. | 2/4/3/3 | 12 | Later |
| 59 | Add a globe as the main navigation; a coarse point investigation does not yet justify the interaction or bandwidth. | 2/4/2/2 | 10 | Later |
| 60 | Let teachers annotate a saved claim and export feedback separately from original evidence; verify that annotations cannot overwrite the source record. | 4/5/2/4 | 15 | Study |

### Engineering and delivery

| ID | Specific candidate and the evidence that would justify it | V/E/F/C | Total | Triage |
|---|---|---|---|---|
| 61 | Compute atlas data once from frozen source and store the result; network-free builds must fail any accidental fetch. | 5/5/4/4 | 18 | Now |
| 62 | Bound atlas size and input years before allocation; malformed or huge imports must fail clearly without blocking the page. | 5/5/4/3 | 17 | Now |
| 63 | Verify public atlas hashes after deployment; signed-out HTTP retrieval must match the built release. | 5/5/4/4 | 18 | Now |
| 64 | Add payload schema/version fields and deliberate migration errors; a future field change must not silently misinterpret old evidence. | 5/5/4/3 | 17 | Now |
| 65 | Benchmark atlas build and browser interaction on the actual small dataset; publish measured timings only after running the benchmark. | 4/5/4/3 | 16 | Study |
| 66 | Use a worker only if measured atlas interaction blocks the main thread; compare complexity against the observed gain. | 3/5/2/2 | 12 | Later |
| 67 | Preserve release tags, input hashes and a one-command build; another environment must produce equivalent analysis values. | 5/5/5/4 | 19 | Keep |
| 68 | Stage media atomically and verify source hashes before/after copy; an in-progress render must not replace a valid website. | 5/5/5/3 | 18 | Keep |
| 69 | Add server accounts and a cloud database for worksheets; local evidence currently meets the need without personal-data collection. | 2/4/1/2 | 9 | Later |
| 70 | Build a source-change ledger comparing upstream payload versions field by field; distinguish changed observations from code-only recalculation. | 4/5/2/3 | 14 | Later |

### Film and explanation

| ID | Specific candidate and the evidence that would justify it | V/E/F/C | Total | Triage |
|---|---|---|---|---|
| 71 | Produce a 135-second technical studio film answering why this approach was selected; retain the ≤30-second official candidate separately. | 5/4/3/5 | 17 | Now |
| 72 | Use a fictional adult presenter as a narrator, with visible disclosure; never portray them as the student or an independent reviewer. | 4/5/3/5 | 17 | Now |
| 73 | Establish one studio reference, wardrobe and lighting plan before multiple presenter shots; inspect identity and room continuity at every edit. | 4/4/3/5 | 16 | Now |
| 74 | Animate exact data figures outside the video model; verify every displayed value against retained JSON. | 5/5/4/5 | 19 | Now |
| 75 | Capture the working atlas and selected-window opening as real interface footage; inspect absence of private browser content. | 5/5/3/5 | 18 | Now |
| 76 | Make subtitles follow actual speech with semantic line breaks and units in explanatory graphics; inspect every caption boundary. | 5/5/4/5 | 19 | Now |
| 77 | Show an honest failure case from the synthetic evaluation instead of a generic success montage; trace the value to the results file. | 5/5/4/4 | 18 | Now |
| 78 | Add a searchable transcript and chapter index with links into the long film and evidence; verify caption times and every deep link. | 4/5/4/5 | 18 | Study |
| 79 | Show a real export and strict replay outcome, captured from the verified release; a narrated claim alone is insufficient. | 5/5/3/5 | 18 | Now |
| 80 | Publish an audio-described alternate explanation of plots using exact signs, dates and units; evaluate clarity with a visually impaired reviewer. | 5/4/2/5 | 16 | Human |

### Competition and professional review

| ID | Specific candidate and the evidence that would justify it | V/E/F/C | Total | Triage |
|---|---|---|---|---|
| 81 | Ask the organizer about the true early-work and AI-ideation history using the drafted message; retain the actual reply. | 5/5/2/5 | 17 | Human |
| 82 | Resolve age, guardian, acceptance and team route in the student's account; the student/guardian performs any required registration action. | 5/5/2/5 | 17 | Human |
| 83 | Check the final public short-demo duration and no-login access; never place the long film in the official demo field. | 5/5/5/5 | 20 | Keep |
| 84 | Send Farhad a bounded review request only when the user explicitly instructs sending; record findings rather than endorsement language. | 4/5/2/5 | 16 | Human |
| 85 | Map one inspectable artifact to each official judging criterion; keep unmeasured impact visible as a gap. | 5/5/5/4 | 19 | Keep |
| 86 | Prepare an offline folder containing source, PDF and evidence for a failed connection; verify local opening and licenses. | 4/5/3/5 | 17 | Study |
| 87 | Rehearse answers about units, dependence and why no forecast was selected; the student must explain in their own words. | 5/5/2/5 | 17 | Human |
| 88 | Run a timed independent review in which a reader reconstructs one claim from the export alone; record missing information and revise the package. | 5/5/2/5 | 17 | Human |
| 89 | Keep a public decision log of discarded concepts and actual contributions; a reader must distinguish research from student-authored work. | 5/5/5/4 | 19 | Now |
| 90 | Compare the name and workflow with KNMI Climate Explorer; identify this as independent and avoid claiming generic trend analysis as new. | 5/5/5/4 | 19 | Keep |

### Longer-term research and portfolio routes

| ID | Specific candidate and the evidence that would justify it | V/E/F/C | Total | Triage |
|---|---|---|---|---|
| 91 | Create a short reproducible notebook teaching one selected window from raw monthly data; a fresh environment must match the saved rate. | 4/5/3/5 | 17 | Later |
| 92 | Study whether spatial and date sensitivity interact using a predeclared location grid; export the full joint search before interpretation. | 5/5/1/2 | 13 | Study |
| 93 | Add a second variable only after a written question connects it to an educational task; assess benefit against extra terminology. | 3/4/2/3 | 12 | Later |
| 94 | Build a forecasting benchmark with naive baselines and blocked holdouts as a separate project; do not relabel historical fit as prediction. | 3/5/1/2 | 11 | Later |
| 95 | Build causal attribution only with a defensible study design and suitable covariates; this single-series prototype cannot establish causes. | 2/3/1/1 | 7 | Later |
| 96 | Produce a small methods note describing the atlas and failure cases; independently reproduce figures before any publication claim. | 5/5/2/4 | 16 | Later |
| 97 | Let a university mentor audit one evidence package; obtain actual comments and permission before quoting or naming them. | 5/5/1/4 | 15 | Human |
| 98 | Document one student-authored extension after the student actually implements it; retain the diff, reasoning and observed test outcome. | 5/5/2/5 | 17 | Human |
| 99 | Prepare a portfolio case study showing decisions, failures and contribution boundaries, independent of award eligibility. | 5/5/4/5 | 19 | Now |
| 100 | Build a student learning log connecting each actual code change to a calculation, test and explanation; assess progress with a mentor rather than an award. | 5/4/3/5 | 17 | Human |

## The next concrete evidence

Science owns enumeration/statistical scope and independent references. Engineering owns safe payloads, UI, export/replay and integration. Submission owns truthful story, source attribution, captions and a separate long-film identity. None is a human judge or peer reviewer. The selected software acceptance evidence belongs in the release verification record once it exists.

After the atlas and media are checked, pause feature expansion and run the real student task and explanation rehearsal. If the atlas increases confusion, retain the simpler four-period view as the default. If organizer rules exclude this work, preserve the complete dated portfolio and learning value without calling it an eligible NASA submission.
