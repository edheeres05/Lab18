"""Run: python -m streamlit run app.py"""
import hashlib
import json
import os
from pathlib import Path
import sys

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / ".agents/skills/buffett-business/scripts"))
from sec_facts import (DEFAULT_AGENT, LABELS, analyze, audit_memo, clean_ticker,
                       load_company, memo_prompt, render_report, result_fingerprint,
                       save_outputs, table_records)

st.set_page_config(page_title="Lab 18 | Buffett Business", page_icon="📊", layout="wide")
st.title("Legend Investor — Buffett's Business Test")
st.caption("Data from SEC EDGAR; built with AI help, a learning demonstration, not investment advice.")

with st.sidebar:
    st.header("Company")
    entered_ticker = st.text_input("Ticker", value="COST")
    mode = st.radio("Data source", ["Saved SEC snapshot", "Live SEC download"])
    user_agent = st.text_input("SEC User-Agent (name and email)",
                               value=os.environ.get("SEC_USER_AGENT", DEFAULT_AGENT))
    run = st.button("Load / refresh data", type="primary")
    st.caption("Saved COST and JPM snapshots contain downloaded SEC facts. Every metric is recomputed; the answer key is never used as data.")

try:
    ticker = clean_ticker(entered_ticker)
except ValueError as exc:
    st.error(str(exc))
    st.stop()

load_key = (ticker, mode, user_agent)
if run or "result" not in st.session_state or st.session_state.get("load_key") != load_key:
    try:
        with st.spinner("Reading SEC facts and computing annual results..."):
            facts, source = load_company(ticker, offline=(mode == "Saved SEC snapshot"), user_agent=user_agent)
            result = analyze(facts, ticker, source)
            save_outputs(result, ROOT / "reports")
            st.session_state.result = result
            st.session_state.load_key = load_key
    except (OSError, ValueError, RuntimeError, KeyError) as exc:
        st.error(str(exc))
        st.info("For a new ticker, select Live SEC download. A failed request never becomes estimated data.")
        st.stop()

result = st.session_state.result
st.subheader(f'{ticker} · {result["company"]}')
st.caption(f'{result["source"]["mode"]} · downloaded {result["source"]["downloaded_at"]}')
st.markdown(f'[SEC company facts]({result["source"]["source_url"]})')
if len(result["rows"]) != 5:
    st.warning("Fewer than five annual periods are available; full-window checks are not known.")

chart = pd.DataFrame([{
    "Fiscal year end": pd.to_datetime(r["fiscal_year_end"]),
    "Owner earnings": None if r["owner_earnings"]["value"] is None else r["owner_earnings"]["value"] / 1_000_000,
    "Net income": None if r["net_income"]["value"] is None else r["net_income"]["value"] / 1_000_000,
} for r in result["rows"]]).set_index("Fiscal year end")
st.line_chart(chart, y_label="USD millions")
if chart["Owner earnings"].isna().any():
    st.info("Missing owner earnings are not plotted as zero; the table shows not found.")
st.caption("Financial amounts below are USD millions; ROE uses year-end equity.")
st.dataframe(pd.DataFrame(table_records(result)), hide_index=True, width="stretch")

for column, (name, status) in zip(st.columns(3), result["checks"].items()):
    with column:
        st.markdown(f"**{name}**")
        {"pass": st.success, "fail": st.error, "not known": st.warning}[status](status)

with st.expander("XBRL tags and filing provenance"):
    st.markdown(render_report(result).split("## Tags and filing provenance", 1)[1])

st.subheader("Buffett-inspired memo")
st.caption("The AI judges the business. Python computes all figures. This is a simulation, not a statement by Warren Buffett.")
memo_path = ROOT / "reports" / f"{ticker}_memo.md"
original = memo_path.read_text(encoding="utf-8") if memo_path.exists() else ""
provenance_path = memo_path.with_suffix(".provenance.json")
fingerprint = result_fingerprint(result)
if original:
    provenance = json.loads(provenance_path.read_text()) if provenance_path.exists() else {}
    if provenance.get("facts_sha256") != fingerprint:
        st.warning("This memo is not bound to these computed facts. Ask Codex to regenerate and audit it before relying on it.")
else:
    st.info("No AI memo exists for this ticker yet. Use the prompt below in Codex; the app does not invent a verdict.")

editor_key = f"memo_{ticker}_{fingerprint}_{hashlib.sha256(original.encode()).hexdigest()}"
memo = st.text_area("Edit memo (try adding ROE of 40.0%)", value=original, height=250, key=editor_key)
flags = audit_memo(memo, result)
if memo.strip():
    if flags:
        st.error("Unprinted numbers found in memo:")
        st.dataframe(pd.DataFrame(flags), hide_index=True, width="stretch")
    else:
        st.success("No unprinted numeric literals found.")
    st.markdown(memo)
    st.caption("The audit checks numeric literals, including percentages and dates. It does not prove that a number is attached to the correct year or metric; review the wording too.")
    left, right = st.columns(2)
    with left:
        if st.button("Save memo edits"):
            memo_path.write_text(memo, encoding="utf-8")
            st.success("Memo saved. Any flagged numbers still need correction.")
    with right:
        st.download_button("Download memo .md", memo, file_name=f"{ticker}_memo.md")

decision_path = ROOT / "reports" / f"{ticker}_decision.md"
decision = decision_path.read_text(encoding="utf-8") if decision_path.exists() else ""
st.markdown("**Your decision — do you trust the verdict, and why?**")
personal = st.text_area("Your own decision", value=decision, key=f"decision_{ticker}")
if st.button("Save my decision"):
    decision_path.write_text(personal.strip() + "\n", encoding="utf-8")
    st.success("Decision saved separately from the AI memo.")

with st.expander("Prompt for Codex to write / update the memo"):
    st.code(memo_prompt(result), language=None)
st.download_button("Download computed facts .md", render_report(result), file_name=f"{ticker}_facts.md")
