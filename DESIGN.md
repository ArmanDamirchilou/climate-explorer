# Climate Explorer design

Build started 11 November 2026, before the Space Apps hackathon. This date must remain visible in the project record. Competition eligibility is not established.

The audience is a curious student who wants to investigate a place, not a professional climate analyst. The main job is to make one defensible comparison over time, using real NASA data and an explanation that a student can follow.

Palette: glacier #edf3f7, snow #fbfdfe, deep sea #183d47, water #147c89, temperature #cc6545, slate #617982. Use temperature orange only for temperature data and teal for rainfall and actions. Body type uses the local system sans serif. Large headings use Trebuchet MS for its open, human shapes. No font downloads.

Layout: a compact navigation bar, a short invitation to explore, then an investigation workspace. A narrow left column holds location and time controls. The large right column holds the chart, interpretation, and a seasonal heatmap. Sources and methodology sit below the results. Everything is left aligned except chart axis labels.

```
Climate Explorer                         Method / Data
See how a place changes.
[location / variable / dates]  [annual chart and trend]
[coordinates / explore]       [result / uncertainty]
                              [monthly heatmap]
[method and data source / downloads]
```

Review: a large chart and quiet controls suit the science task. Avoid a generic stack of metric cards, a globe stock image, decorative gradients, and oversized numbers without context. Make the graph the visual identity. All charts carry units, dates, and text alternatives. The location control is a coordinate selector, not a claim that the data describe one precise street.

## Review and improvement on 11 November

Keep the existing palette, typography, and chart. Add a section between the annual chart and monthly heatmap titled "Does the result depend on the method?" Its main device is an interval plot with a visible zero line. Ordinary and dependence-adjusted intervals share the same axis. This directly shows disagreement without using a score or an unexplained confidence badge.

Below it, show a small table of fixed period checks and the robust slope estimate. Explain that the checks use the same observations and do not independently validate each other. Always show the source grid size. Place the synthetic validation link beside the method explanation, where it helps assess the claim.

```
[Annual observations and fitted line]
[Estimated rate and conditional interpretation]
[Method intervals       | zero |             ]
[Robust slope / one-year influence / date checks]
[Monthly detail]
```

Review against the user's request: this change makes the choice of method visible. It adds no decorative dashboard cards and no unsupported claim of reliability. On a phone, comparison rows and the table retain readable labels; long tables scroll within their own section.

## Public demonstration and evidence review, 13 November

Preserve the palette and large investigation chart. Add a compact source comparison after the method checks, with two rows on the same units and period. Keep the spatial mismatch beside those values. In particular, retain Toronto's disagreement instead of selecting only favorable examples. Link to the frozen scientific review. Do not imply either dataset is ground truth.

The public demonstration uses five frozen locations for 1981–2025. A plain notice above the workspace explains this scope before someone uses the controls. Disable unsupported dates and remove the custom-location option in that mode. The full local application keeps these controls. Relative links must work inside a GitHub Pages project path.

Add an optional investigation worksheet below the source section. Ask for the user's question, interpretation, and remaining uncertainty. A download combines those notes with the actual result, assumptions, source URLs, and reproducible analysis. Keep notes in the current browser tab only. This supports a defensible explanation without generating a conclusion for the user.

```
[Frozen demonstration notice, when applicable]
[Controls] [Annual chart / methods / fixed dates]
           [POWER rate / GISTEMP rate / spatial limitation]
           [Monthly detail / source and downloads]
           [My question / interpretation / uncertainty / save]
```

Review: the new comparison tests the claim across sources. The worksheet serves the proposed educational task. Neither requires a new dashboard, accounts, or decorative animation. Real comprehension testing remains necessary before claiming educational impact.

## Saved investigation workflow, 13 November

The upgrade keeps the existing climate chart as the main visual. The palette remains ice white #fbfdfe, blue ground #edf3f7, ink #183d47, muted blue #526c76, teal #147c89 and temperature orange #cc6545. System sans serif handles controls and evidence; Trebuchet retains the existing display role. The four-period table is a comparison of estimates, so rows replace extra metric cards. Saved-file controls sit under a disclosure in the investigation sidebar. Opt-in storage remains beside the notes, with device privacy explained at the point of choice.

The four fixed periods use the same frozen response and retain the longest default. Import shows its verification scope before the result. The form remains a separate way to begin another analysis rather than silently changing its controls to arbitrary imported data. Printed notes become plain paragraphs so textarea scrolling cannot hide their content. Media live on a separate demonstration page, keeping the main data workflow focused.


## 1.1 guided investigation

Retain the glacier, snow, deep-sea, slate and teal colors and system/Trebuchet type. A compact full-width story precedes the investigation workspace. Three genuine steps reveal the long period, the recent period and their uncertainty. The comparison uses actual values on one scale, with dates and rate units. Semantic buttons and an explicit action open matching evidence in the existing chart. There is no autoplay; scrolling follows a deliberate action. Mobile uses one column. The selection disclosure, source hash and conditional-interval caveat stay available.
