# Lab 18 — Legend Investor as Skill

Ethan D. Heeres

Partner: Aidan Murrin

## D — question

Can an investor's philosophy become a skill your AI runs the same way every time — every number computed by code from the 10-K, the judgment the model's?

Yes, the data selection and financial tests can follow a fixed process. The AI's interpretation remains judgment and can differ even when the inputs are identical. The reproducible part is the computation, not a guarantee that every generated sentence will be identical.

## Proposed build request

Build a Codex skill called buffett-business in .agents/skills and bundle a Python script that downloads SEC EDGAR company facts using my name and email. Use the lab's exact tags, annual periods, latest-filing rule and missing-data rules. Compute the last five fiscal years, ROE, owner earnings and all three checks in Python. Have the AI write a short Buffett-inspired business-only memo from the printed results, with no prices or invented numbers. Build a Streamlit app showing the chart, table, checks, tags and memo, and flag unprinted numeric literals. Verify COST against the course table, preserve JPM's missing capital spending, and test a hand-added 40.0%. Keep the expected-answer table confined to tests. Save the code, memos and results as local files.

## Code versus judgment

Code can calculate owner earnings by subtracting capital spending from operating cash flow. It can check whether ROE met the threshold in every year. Judgment is deciding whether the historical earning record is convincing enough to want to own the business and what evidence is still missing about the moat or management.

## COST memo and decision

*AI-written educational simulation, not a statement by Warren Buffett. Amounts are USD millions.*

**Verdict: own the business — a business-quality judgment, with further qualitative review needed.**

I want a business that turns its earnings into cash for its owners. From fiscal year-end 2022-08-28 to 2026-08-30, net income rose from 5,844 to 9,226 and owner earnings rose from 3,501 to 9,382. Owner earnings stayed positive throughout the period. They did not rise in every year: they slipped from 6,745 in 2023 to 6,629 in 2024 before recovering.

The annual returns on year-end equity were 28.3%, 25.1%, 31.2%, 27.8%, and 25.8%, respectively. Each cleared the 15% test. Together with positive owner earnings and higher owner earnings from first year to last, that gives me evidence of an attractive earning record.

I would still need to understand whether Costco can defend those economics and whether management will allocate future cash well. These figures alone do not establish a durable moat, prove management quality, or measure balance-sheet risk. The lab's cash-flow-minus-capital-spending measure is a simplified owner-earnings proxy. My favorable judgment concerns the business record; without price data, I cannot say whether the shares are a bargain.

**My decision:** I trust the favorable verdict on Costco because I believe its leadership in bulk buying and strong membership policies will help its competitive advantages last.

## Partner discussion — Aidan Murrin

We discussed whether strong historical financial results prove that Costco's advantages will last. I believe its leadership in bulk buying and strong membership policies support the favorable verdict. Aidan said those advantages could weaken if younger consumers increasingly rely on e-commerce and online grocery ordering, given Costco's emphasis on physical stores. He also identified new competitors as a threat.

The distinction is that code can calculate ROE, owner earnings and the three checks from reported facts. Deciding whether changing customer preferences and competition could weaken Costco's position requires judgment. A strong historical record does not settle that future question.

## Explain the code — preparation, not a completed partner exercise

Open `year_row` in `.agents/skills/buffett-business/scripts/sec_facts.py`.

| Statement | Plain-English explanation |
| --- | --- |
| `row = {"fiscal_year_end": end}` | Start a row labelled with the actual year-end date. |
| `for metric, tags in TAGS.items()` | Go through the required financial fields and their allowed tags. |
| `row[metric] = select_fact(...)` | Find that period's value using tag priority and the latest eligible filing. Flows must cover a year; equity must be an instant. |
| Assign `income`, `equity`, `cash`, `capex` | Pull the selected inputs out of their provenance records. |
| Set `roe` | Divide income by year-end equity only if both inputs exist and equity is positive. Otherwise store `None`. |
| Set `owner` | Subtract capital spending from operating cash flow only if both exist. Otherwise store `None`. |
| Add `roe` and `owner_earnings` to the row | Store the code-computed result with the underlying tag formula. |
| `return row` | Return the completed year's data. |

Where does **not found** come from? `select_fact` exhausts both allowed tags and returns `value=None`. `year_row` preserves that absence rather than replacing it with zero. `display_value` turns a missing financial value into `not found`, and a missing or invalid ROE into `not known`. `three_checks` returns `not known` when a required input is absent.

Why not use `fy` directly? A later filing repeats earlier years' numbers. The filing's `fy` describes the filing, while each fact's `start` and `end` describe the period actually measured.

Why check duration? A 10-K can contain quarterly data as well as annual data. Form alone does not prove a flow covers a full year.

## Probes

- **COST:** the computed table matches the supplied answer key and all checks pass. See `VALIDATION.md` for executed checks.
- **JPM:** permitted capital spending is missing; owner earnings is missing; both owner-earnings checks are unknown. The memo explicitly states it cannot judge owner earnings.
- **Hand-entered number:** adding `40.0%` to COST's memo is flagged; the delivered memo does not retain the intentionally incorrect sentence.
- **Fresh chat without the skill:** I asked, “Is Costco a Buffett business? Give its ROE for the last five years.” The response cited Costco's SEC annual reports but explicitly calculated ROE using average shareholders' equity. My skill follows the lab's year-end-equity rule instead. The response I supplied is preserved in `reports/fresh_chat_response.md`.

| Fiscal year | Fresh chat: average equity | Skill: year-end equity |
| --- | --- | --- |
| 2022 | 30.59% | 28.3% |
| 2023 | 27.54% | 25.1% |
| 2024 | 30.27% | 31.2% |
| 2025 | 30.69% | 27.8% |
| 2026 | 28.40% | 25.8% |

The net-income figures matched the skill's table. The ROE figures differed because the fresh chat used a different denominator, not simply because it lacked sources. Its cited sources were the [2026 Form 10-K](https://www.sec.gov/Archives/edgar/data/909832/000090983226000093/cost-20260830.htm) and [2024 Form 10-K](https://www.sec.gov/Archives/edgar/data/909832/000090983224000049/cost-20240901.htm). These are the sources the response named; the comparison does not independently verify every additional claim in that response.

This shows why the skill needs an explicit formula: a general AI response can use a different definition even when it cites the same type of source. The fresh chat also introduced membership figures, renewal rates and a special dividend, which are outside the script's printed metrics and are not used as inputs to its memo.

## Local run

After the pandas dependency was updated, I reported that the app ran successfully. I subsequently reported that everything appeared to work. My screenshot shows COST's matching table and all three passing checks. The screenshot does not show JPM or the edited-memo probe; those also passed the separate automated application tests documented in `VALIDATION.md`.

## Learn

**What is a skill?** A folder containing a SKILL.md file with a name, a description and instructions. It can include scripts and supporting resources.

**How does it work?** The AI first sees the name and description to decide whether the skill fits the request. It loads the detailed instructions only when needed, keeping unrelated instructions out of the active context. The skill then directs the AI to run the same calculation script and use its output.

**Why should numbers belong in code?** The calculations are inspectable, testable and repeatable. The model interprets the computed facts rather than recalling financial figures or doing unchecked arithmetic.

## Reflect

**What stays the same?** For identical SEC inputs, the tag rules, annual-period selection, formulas, missing-data treatment and check results stay the same. The model still decides how convincing the evidence is and writes the explanation. A new SEC filing can legitimately change the input and result.

**Why is “not found” better than an estimate?** It tells the reader the data does not support the calculation. An estimate could make JPM appear to pass a cash-earnings test that could not actually be evaluated under the lab's rules.

## Remaining checkout actions

- Complete the no-AI, line-by-line `year_row` explanation with your partner if not already done; its completion has not been confirmed here.
- Complete Brightspace's Lab 18 quiz if not already done.
- Upload the files to your chosen GitHub repository and submit the real links. No GitHub upload has been made.
