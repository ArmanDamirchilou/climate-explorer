# Climate Explorer judge questions

These answers describe the current evidence. They are not a script claiming student authorship. Revise them if the release changes.

**Why does this need to exist when NASA already has climate charts?**

Giovanni, GISTEMP and KNMI Climate Explorer already offer climate analysis tools. The KNMI product has the same name and is separate from this student prototype. Our proposed contribution is a student workflow that compares reasonable analysis choices and carries enough evidence to repeat the result. We have not established that no other product does this. The next test is whether students interpret conclusions more accurately with these checks.

**What exactly is a student supposed to learn?**

The intended task is to distinguish the estimated rate from the uncertainty model, notice when changing the dates changes the question, and recognize a disagreement between sources. This is a proposed benefit. The prepared three-person pilot has not yet produced observations.

**Why not use a neural network or add a chatbot?**

The question concerns historical rates in a few decades of annual data. A straight-line summary is inspectable and easy to test. A forecasting model answers a different question. A chatbot would add another interpretation layer before we have shown that the existing explanations work.

**Does a confidence interval excluding zero prove warming or its cause?**

It reports evidence under a particular statistical model for that chosen dataset and period. It does not prove a cause. Serial dependence, dataset error, repeated exploration, and model misspecification can affect inference.

**Why show Newey-West if your experiment shows failures?**

It shows how estimated uncertainty changes with dependence assumptions and lag choice. We do not label it universally corrected. The experiment prevented us from silently replacing one interval with another and claiming the problem was solved.

**Why not present only the best-performing method?**

The simulation control with known dependence performed well because it had information unavailable in real data. Selecting a method by its p-value or a favorable city result would be misleading. All fixed experiment results remain available.

**Are POWER and GISTEMP independent ground truth?**

No. They have different grids and processing, and may share information. The comparison tests consistency over matching years, not station-level truth. A source discrepancy needs investigation rather than an invented physical explanation.

**What does a point on the map represent?**

The selected coordinate requests a value from a model grid. The POWER meteorology grid is much larger than a street. A city label helps select a location; it does not establish a precise city measurement.

**What happens when data are missing or NASA is unavailable?**

An incomplete year is excluded. Missing calendar years prevent the dependence interval calculation from treating distant years as neighbors. Cached data and the labelled real Tehran snapshot support a fallback. An exported result can be replayed without contacting NASA. Check the final release's specific offline demonstration behavior.

**What have you validated?**

The repository records numerical tests, a fixed synthetic study, browser/export checks, and a five-location source comparison. These do not establish educational impact, universal statistical calibration, or production readiness for public decisions. Cite the final release verification record rather than memorizing an outdated test count.

**Who designed and wrote this?**

The student selected the Climate Explorer name and climate direction. Codex developed research, detailed solution choices, implementation, tests and documentation, with specialist agents reviewing separate areas. The student's later review or contributions must be described separately. The project began before the event, and organizer guidance is required on early work and AI ideation.

**What would you improve next?**

First resolve entry eligibility and the student's account details. Then observe students doing the investigation, improve the explanations that cause mistakes, and follow the source discrepancy with matched spatial data and a suitable station comparison. Broader features should follow evidence from those tasks.
