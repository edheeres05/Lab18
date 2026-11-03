# Lab 18 validation

Executed November 3, 2026. The SEC company facts were downloaded from the SEC endpoints, not transcribed from the assignment. Raw responses, source URLs, timestamps and checksums are included in `data/`.

| Check | Actual result |
| --- | --- |
| SEC ticker-to-CIK lookup | COST → 0000909832; JPM → 0000019617 |
| COST annual period ends | 2022-08-28 through 2026-08-30 |
| Every COST table cell | Matched the supplied answer key, including all five ROE percentages |
| COST three checks | pass / pass / pass |
| JPM annual period ends | 2021-12-31 through 2025-12-31 |
| JPM capital spending and owner earnings | not found in every row |
| JPM three checks | fail / not known / not known |
| Original COST and JPM memos | No unprinted numeric literals found |
| Deliberately add `40.0%` in COST's Streamlit memo editor | Flagged `40.0%` with line and context; original delivered memo kept clean |
| Streamlit COST screen | No application exceptions; three pass indicators; memo audit passes |
| Streamlit JPM screen | No application exceptions; two unknown indicators; memo says it cannot judge owner earnings |
| Invalid ticker input | Displayed a clear input error |
| Streamlit server | Started successfully; page and health endpoint returned HTTP 200 |
| Skill frontmatter | Passed the skill validator |
| Regression suite | 16 tests passed |

The regression suite also covers latest-filing selection, comparative fiscal periods, tag fallback and priority, 53-week years, rejection of quarterly and multiyear flows, rejection of other filing forms, nonpositive equity, unrounded threshold comparisons, missing inputs, missing history, endpoint growth versus every-year growth, repeated numeric flags, percentage/amount distinction, and detection of changed saved JSON.

The application was exercised using Streamlit's AppTest API. Ethan's initial Windows installation failed while generating pandas metadata. The dependency was updated from pandas 2.2.3 to pandas 2.3.3, and installation now requests prebuilt packages. Ethan then reported that the app ran successfully and that everything appeared to work. His screenshot confirms the COST table and all three passing checks; it does not show JPM or the edited-memo probe. Those two probes passed the automated application tests separately.

The revised package was tested with pandas 2.3.3 and Streamlit 1.66.1. The Windows batch file itself was not executed in this Linux environment. Initial setup requires internet and standard 64-bit Python 3.10–3.14; the included SEC snapshots support subsequent offline calculation. The exact cause of the original Windows error was not confirmed because the screenshot omitted the earlier diagnostic lines and Python version.

The memo audit verifies whether a numeric literal is among the allowed printed financial values, dates, years and check parameters. It does not verify the meaning of a sentence, numbers written as words, the metric/year attached to a value, or unprinted unit conversions. The skill prohibits conversions and additional model arithmetic. Review the memo's wording alongside the table.

Ethan supplied his personal trust decision, named Aidan Murrin as his partner, reported Aidan's concerns about e-commerce preferences and new competition, and pasted his fresh-chat response. These are included in the revised checkout document. Completion of the separate no-AI line-by-line explanation and Brightspace quiz has not been confirmed. No GitHub files were created or changed.
