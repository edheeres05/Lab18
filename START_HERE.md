# Lab 18 — Ethan D. Heeres

## Open the app on Windows

1. Extract the entire downloaded project first. Do not run it from inside the ZIP viewer.
2. Open the extracted `Lab18_EthanHeeres` folder.
3. Double-click `RUN_APP.bat`. Keep its terminal window open. The first run installs the required packages and needs internet.
4. The browser should open the app. If it does not, open http://localhost:8501.

Use standard 64-bit Python 3.10–3.14. This package uses pandas 2.3.3, including support for Python 3.14. The app opens COST using the included SEC download and recomputes the figures. Change the ticker to JPM for the missing-data probe. Use **Live SEC download → Load / refresh data** for fresh data or another ticker.

For the usual Downloads extraction with a folder inside a folder, paste this into the VS Code PowerShell terminal:

```powershell
cd "$env:USERPROFILE\Downloads\Lab18_EthanHeeres\Lab18_EthanHeeres"
.\RUN_APP.bat
```

Expected result: a local Streamlit page with the COST chart, five-year table, three passing checks, memo, and personal-decision field. Running `python app.py` directly is not the Streamlit launch command.

If you already have the working environment, launch directly:

```powershell
cd "$env:USERPROFILE\Downloads\Lab18_EthanHeeres\Lab18_EthanHeeres"
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Expected result: the same app opens using the installed packages.

To update your existing project, stop the app with Ctrl+C and copy the contents of the downloaded `Lab18_EthanHeeres` folder into your existing inner project folder, replacing matching files. Keep your existing `.venv` folder; it is not part of the download. Restart the app to load your confirmed decision. If you downloaded to another folder or Windows added a suffix to its name, adjust the `cd` path accordingly.

## Run the skill in Codex in VS Code

Open this entire folder in VS Code. The skill lives at `.agents/skills/buffett-business/SKILL.md`, with its script bundled in `scripts/`. In Codex, enter:

> Use $buffett-business on COST. Run the SEC script, review its printed facts, write the business-only memo, and audit every numeric literal. Then run the JPM missing-data probe. Do not use prices or paid data.

The normal script command downloads live SEC data:

```powershell
py .agents/skills/buffett-business/scripts/sec_facts.py COST
```

Expected result: COST's latest five annual periods and XBRL tags printed in the terminal; three checks printed; facts and a memo-writing prompt saved in `reports`. The AI writes the memo after reading this output. The Python script does not manufacture a verdict.

To recompute the included snapshots without network access:

```powershell
py .agents/skills/buffett-business/scripts/sec_facts.py COST --offline
py .agents/skills/buffett-business/scripts/sec_facts.py JPM --offline
```

Expected result: COST passes all three checks; JPM has `not found` capital spending/owner earnings and `not known` owner-earnings checks. JPM's ROE check fails.

The SEC User-Agent is `Ethan D. Heeres edheeres@gmail.com`. Change it in the app sidebar or set `SEC_USER_AGENT` if you prefer another contact email. No API key is required. Cached raw SEC files have source URLs, download timestamps and SHA-256 checksums; they are not the course answer key.

## Files to review / submit

| File | Purpose |
| --- | --- |
| `.agents/skills/buffett-business/SKILL.md` | AI instructions and trigger metadata |
| `.agents/skills/buffett-business/scripts/sec_facts.py` | SEC download, annual fact selection, arithmetic, checks and memo audit |
| `app.py` and `requirements.txt` | Streamlit app and dependencies |
| `reports/COST_memo.md` | AI-written Buffett-inspired COST memo |
| `reports/JPM_memo.md` | AI-written memo explaining the missing owner earnings |
| `reports/COST_facts.md` and `reports/JPM_facts.md` | Computed tables, checks, tags and filing provenance |
| `reports/COST_decision.md` | Your confirmed personal decision |
| `reports/fresh_chat_response.md` | The fresh-chat response you supplied, with its cited sources |
| `Lab18_checkout.md` | Question, proposed build request, your decision, Aidan's discussion points, ROE comparison and learning/reflection notes |
| `VALIDATION.md` | Actual verification results |
| `tests/test_lab18.py` | Answer-key comparison and calculation/audit edge cases |

Keep `data/` and `reports/` with the app so the saved-snapshot option works. The facts JSON, table CSV and memo prompt files are generated outputs. The `.provenance.json` memo companions detect stale memos after data changes.

## Recorded and remaining

Your Costco trust decision, partner Aidan Murrin's comments, and the fresh-chat response/comparison are now recorded. You reported a successful local run after the dependency fix. Your screenshot confirms COST's matching table and three passes; the automated tests also cover JPM and the hand-entered-number probe.

- Explain `year_row` to your partner without AI if you have not already done so. Preparation notes are in `Lab18_checkout.md`; completion has not been confirmed here.
- Complete the Brightspace quiz yourself if you have not already done so.
- The assignment ultimately asks for GitHub file links. Nothing was uploaded to GitHub, as requested. Upload the files yourself when ready for checkout; include the hidden `.agents` folder. VS Code can show that folder even if your file picker hides it.

## Test the hand-entered number

In the COST memo editor, append `ROE was 40.0%.` The app should immediately flag `40.0%` with the line and context. Remove that sentence afterward. You do not need to save the deliberately wrong version.

## Run the regression tests

```powershell
py -m unittest discover -s tests -v
```

Expected result: all tests pass. Tests use saved SEC snapshots and never feed their answer-key constants into the app.

## Sources

- [Course prework](https://github.com/CinderZhang/FIN43900-Fall2026/blob/main/lessons/week-11/student-prework.md)
- [FAskills README — read only](https://github.com/CinderZhang/FAskills/blob/main/README.md)
- [Buffett philosophy — read only](https://github.com/CinderZhang/FAskills/blob/main/financial-researcher/experts/warren_buffett.md)
- [Codex skills and `.agents/skills` location](https://developers.openai.com/codex/skills)
- [SEC API documentation](https://www.sec.gov/search-filings/edgar-application-programming-interfaces)
- [SEC ticker mapping](https://www.sec.gov/files/company_tickers.json)
- [COST company facts](https://data.sec.gov/api/xbrl/companyfacts/CIK0000909832.json)
- [JPM company facts](https://data.sec.gov/api/xbrl/companyfacts/CIK0000019617.json)
- [Streamlit chart documentation](https://docs.streamlit.io/develop/api-reference/charts/st.line_chart)
- [pandas 2.3.3 and Python 3.14 support](https://pandas.pydata.org/pandas-docs/stable/whatsnew/v2.3.3.html)
