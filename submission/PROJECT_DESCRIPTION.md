# Climate Explorer project description

Draft text for the published form fields. Public source, browser demo and PDF links were verified on 13 November. Keep the eligibility and authorship statements accurate. These drafts do not mean the project is eligible or submitted.

## Project name

Climate Explorer

## High level project summary

Climate Explorer helps students investigate historical temperature and rainfall trends using NASA POWER data. It shows the estimated rate of change and checks whether the conclusion changes with statistical assumptions or the selected dates. A saved analysis includes the source data and settings, so another person can repeat the calculation. The goal is to make climate investigations easier to question and reproduce. Educational benefit has not yet been measured.

## Link to project demo

Verified public PDF link: https://armandamirchilou.github.io/climate-explorer/climate-explorer-demo.pdf

The demo is a seven-page PDF, including the cover. It opened in Incognito Chrome without login; recheck access before the final form.

Alternative short video: https://armandamirchilou.github.io/climate-explorer/climate-explorer-demo.mp4

The silent video lasts 29 seconds and uses English captions. Verify its public link after publication. Choose the PDF or MP4 as the form's demonstration link. Both retain the AI and early-work disclosures.

## Link to final project

Repository: https://github.com/ArmanDamirchilou/climate-explorer

Frozen browser demonstration: https://armandamirchilou.github.io/climate-explorer/

The hosted demonstration uses retained examples. The repository provides the Python application for live NASA queries and instructions for reproducing calculations. Anonymous public access was verified on 13 November; recheck access before the final form.

## Detailed project description

An apparent trend can change when we choose a different time period, uncertainty model, or data source. Climate Explorer makes these choices visible during a student investigation.

The user selects temperature or rainfall, a location, and at least ten complete years. The backend retrieves NASA POWER monthly data. It forms annual temperature means using calendar-day weights. It estimates annual rainfall totals from monthly daily rates. Incomplete years are excluded. The interface shows annual values, a monthly view, a fitted rate per decade, and the original independent-error interval with its assumptions.

The investigation then compares Newey-West intervals at recorded lag settings, a Theil-Sen slope, fixed date windows, and the influence of removing each year. Agreement does not prove that a result is correct. The methods share the same data and can share the same biases. The app reports disagreement instead of selecting the most impressive result.

The project tested eight method configurations on 20,000 generated records with known answers. In one 45-year simulation with strong serial dependence and no true trend, the ordinary interval excluded zero in 42% of records. Automatic-lag Newey-West reduced that rate to 26.2%, which was still far above the nominal 5%. These are experimental scenarios, not estimated error probabilities for a real city. The failure led us to present the intervals as sensitivity checks rather than a universal statistical correction.

A five-location comparison uses NASA GISTEMP temperature data over the same years. Different spatial supports are explicit. A large Toronto disagreement is retained for investigation. Neither source is treated as ground truth.

Analysis exports retain the raw NASA response, request, source date, units, method settings, software versions, and hashes. The replay tool recalculates a downloaded result without contacting NASA. The app uses Python, NumPy, SciPy and statsmodels, with a browser interface written in HTML, CSS, JavaScript and SVG. It has no account system or third-party browser libraries.

The proposed users are students and teachers. The project supports historical exploration. It does not predict weather, establish causes, or provide street-level climate measurements. The next impact check is an observed student task using the prepared usability protocol.

This is an independent student prototype. It is not affiliated with the existing KNMI Climate Explorer, which is also linked from the challenge resources. Plotting and significance testing already exist in established tools. Our proposed contribution is the particular student workflow combining sensitivity checks with repeatable evidence.

Development began on 11 November 2026, before the hackathon. Codex contributed research, solution design, code, tests and documentation. Eligibility under the event's early-work and AI-ideation rules is unresolved. Student contributions must be stated separately and accurately.

## Use of Super Intelligence

OpenAI Codex was used to research methods, compare solution approaches, choose and refine the investigation workflow, implement the application, develop tests, and draft documentation and submission materials. At the student's request, separate Codex agents reviewed the science, engineering, and submission strategy. Their roles and resulting changes are recorded in AI_ASSISTANCE.md.

The student's confirmed choices were the Climate Explorer name and climate-project direction. We do not claim that the student independently designed or wrote the generated implementation. NASA source data were retrieved from the named NASA services. The synthetic experiment generated test records using a documented random process; these are not NASA observations. The project includes no AI-generated portrait, voice, or decorative imagery. See AI_ASSISTANCE.md for the detailed record and the unresolved guide restriction on AI-generated solution ideas.

## NASA data

NASA POWER monthly T2M and PRECTOTCORR provide the main temperature and rainfall records. The actual responses identify their meteorology source, currently MERRA-2 for the retained records. NASA GISTEMP v4 land-only 250 km smoothing data provide a separate temperature consistency comparison at a different spatial scale. Source URLs, retrieval dates, units, and hashes are retained with the analysis and evaluation records.

See [POWER monthly API](https://power.larc.nasa.gov/docs/services/api/temporal/monthly/), [POWER methodology](https://power.larc.nasa.gov/docs/methodology/data/sources_meteorology/), and [GISTEMP](https://data.giss.nasa.gov/gistemp/).

## Space agency partner data and other references

No Space Agency Partner dataset is currently integrated. Do not list one merely because it appeared in research. Include every library, source, and asset actually used in the final release. Start with the references in the repository README, RESEARCH.md, evaluation/DATASET_CHECK.md, the dependency lock, and AI_ASSISTANCE.md. Follow applicable third-party licenses and data acknowledgments.
